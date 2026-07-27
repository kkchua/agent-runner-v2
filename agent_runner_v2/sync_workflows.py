"""Sync workflow definitions to the backend registry.

Discovers workflows from packaged ``workflow.toml`` workflow directories.

Each definition is validated locally first, then POSTed to the backend API at
``/api/admin/workflows/sync`` only if local validation passes.

The backend sync endpoint is treated as persistence-oriented transport. Bundle
semantics and workflow-definition validation are owned by ``agent-runner-v2``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from urllib import error, request

from .config_loader import load_runner_config
from .workflow_packages.loader import (
    bundle_to_template_group_dict,
    load_workflow_package,
)
from .workflow_bundle_validator import validate_workflow_bundle_dir

def _workflows_dir() -> Path:
    return Path.cwd().resolve() / "workflows"


def _discover_plugin_workflows(workflows_dir: Path) -> dict[str, dict]:
    """Scan the current repo workflow root for ``workflow.toml`` packages."""
    plugin_workflows: dict[str, dict] = {}

    for candidate in sorted(workflows_dir.iterdir()):
        if not candidate.is_dir():
            continue
        manifest = candidate / "workflow.toml"
        if not manifest.is_file():
            continue

        bundle = load_workflow_package(candidate)
        group_dict = bundle_to_template_group_dict(bundle)
        
        # Debug: show what we loaded from TOML
        print(f"  [plugin] Loaded {bundle.name!r}: default_max_rejects={bundle.default_max_rejects}", file=sys.stderr)
        
        plugin_workflows[bundle.name] = group_dict

    return plugin_workflows

def _load_all_workflows(workflows_dir: Path) -> dict[str, dict]:
    """Load workflow definitions from the current repo workflow packages."""
    plugin = _discover_plugin_workflows(workflows_dir)
    print(f"[sync] Discovered {len(plugin)} workflow packages from {workflows_dir}", file=sys.stderr)
    return plugin


def _strip_bundle_refs(definition: dict) -> dict:
    """Remove runtime-only ``_workflow_bundle`` references before serialization.

    ``bundle_to_template_group_dict()`` stamps a non-serializable
    ``WorkflowBundle`` object on each step config for runtime use
    (context hook injection in ``step_runner``). The backend sync
    API only needs the plain dict shape.
    """
    step_configs = definition.get("step_configs", {})
    for cfg in step_configs.values():
        cfg.pop("_workflow_bundle", None)
    return definition


def _post_sync(
    backend_url: str,
    workflow_name: str,
    definition: dict,
    preserve_history: bool,
    changed_by: str = "sync_script",
    change_reason: str = "",
) -> dict:
    """POST a single workflow definition to the backend sync endpoint."""
    payload = json.dumps(
        {
            "workflow_name": workflow_name,
            "definition": definition,
            "preserve_history": preserve_history,
            "changed_by": changed_by,
            "change_reason": change_reason,
        }
    ).encode("utf-8")
    req = request.Request(
        f"{backend_url.rstrip('/')}/api/admin/workflows/sync",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _print_validation_failure(workflow_name: str, validation) -> None:
    print(f"\n[{workflow_name}] local validation failed:", file=sys.stderr)
    for finding in validation.findings:
        print(
            f"  - [{finding.code}] step={finding.step or '-'} path={finding.path or '-'} {finding.message}",
            file=sys.stderr,
        )


def _print_sync_summary(*, synced: list[str], validation_failed: list[str], transport_failed: list[str]) -> None:
    print("\nSync summary:", file=sys.stderr)
    print(f"  synced: {len(synced)}", file=sys.stderr)
    print(f"  local_validation_failed: {len(validation_failed)}", file=sys.stderr)
    print(f"  backend_transport_failed: {len(transport_failed)}", file=sys.stderr)
    if validation_failed:
        print(f"  validation_failed_workflows: {', '.join(validation_failed)}", file=sys.stderr)
    if transport_failed:
        print(f"  backend_failed_workflows: {', '.join(transport_failed)}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    cfg = load_runner_config()
    parser = argparse.ArgumentParser(
        description=(
            "Validate workflow bundles locally, then sync validated workflow "
            "definitions into the backend registry."
        )
    )
    parser.add_argument(
        "workflow_names",
        nargs="*",
        help=(
            "Workflow names to sync. If omitted, syncs every workflow.toml package "
            "under the current repository workflows/ folder."
        ),
    )
    parser.add_argument(
        "--backend-url",
        default=os.environ.get("AGENT_RUNNER_BACKEND_URL")
        or str(cfg.get("backend_url") or "")
        or "http://127.0.0.1:8100",
        help="Backend base URL (default: ~/.ukbe-runner/config.json backend_url, else http://127.0.0.1:8100)",
    )
    parser.add_argument(
        "--preserve-history",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep existing execution history when definitions change.",
    )
    parser.add_argument(
        "--changed-by",
        default="sync_script",
        help="Who is making this change (default: sync_script).",
    )
    parser.add_argument(
        "--change-reason",
        default="",
        help="Reason for the change (optional audit trail note).",
    )
    args = parser.parse_args(argv)
    workflows_dir = _workflows_dir()
    if not workflows_dir.is_dir():
        print(
            f"ERROR: Required workflow source folder is missing: {workflows_dir}",
            file=sys.stderr,
        )
        return 2

    workflows = _load_all_workflows(workflows_dir)
    workflow_names = args.workflow_names or sorted(workflows.keys())

    missing = [name for name in workflow_names if name not in workflows]
    if missing:
        print(
            f"Unknown workflow name(s): {', '.join(missing)}",
            file=sys.stderr,
        )
        return 2

    print(f"Backend URL: {args.backend_url}")
    print(f"Workflows: {', '.join(workflow_names)}")
    print("Validation owner: agent-runner-v2 (local preflight)")
    print("Backend role: persistence-oriented workflow registry")

    failed = False
    synced: list[str] = []
    validation_failed: list[str] = []
    transport_failed: list[str] = []
    for workflow_name in workflow_names:
        bundle_dir = workflows_dir / workflow_name
        validation = validate_workflow_bundle_dir(bundle_dir)
        if not validation.valid:
            _print_validation_failure(workflow_name, validation)
            failed = True
            validation_failed.append(workflow_name)
            continue

        definition = _strip_bundle_refs(workflows[workflow_name])
        
        # Debug: calculate hash locally to match backend calculation
        source_hash = hashlib.sha256(
            json.dumps(definition, sort_keys=True).encode("utf-8")
        ).hexdigest()
        
        print(f"\n[{workflow_name}] Preparing sync:", file=sys.stderr)
        print(f"  default_max_rejects: {definition.get('default_max_rejects')}", file=sys.stderr)
        print(f"  steps count: {len(definition.get('steps', []))}", file=sys.stderr)
        print(f"  step_configs count: {len(definition.get('step_configs', {}))}", file=sys.stderr)
        print(f"  source_hash (first 16): {source_hash[:16]}...", file=sys.stderr)
        
        try:
            response = _post_sync(
                args.backend_url,
                workflow_name,
                definition,
                args.preserve_history,
                args.changed_by,
                args.change_reason,
            )
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            print(
                f"[{workflow_name}] sync failed: HTTP {exc.code} {body}",
                file=sys.stderr,
            )
            failed = True
            transport_failed.append(workflow_name)
            continue
        except Exception as exc:
            print(
                f"[{workflow_name}] sync failed: {exc}",
                file=sys.stderr,
            )
            failed = True
            transport_failed.append(workflow_name)
            continue

        status = response.get("status", "unknown")
        workflow = response.get("workflow", {})
        revision = response.get("revision", {})
        prev_rev = response.get("previous_revision")
        rev_info = f"rev={revision.get('revision_number')}" if revision else ""
        prev_info = f" (was {prev_rev})" if prev_rev else ""
        print(
            f"[{workflow_name}] {status} -> "
            f"id={workflow.get('id')} name={workflow.get('name')} "
            f"{rev_info}{prev_info}"
        )
        synced.append(workflow_name)

    _print_sync_summary(
        synced=synced,
        validation_failed=validation_failed,
        transport_failed=transport_failed,
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
