"""Sync workflow definitions to the backend registry.

Discovers workflows from two sources:
1. ``TEMPLATE_GROUPS`` in the bootstrap module (legacy Python dict format)
2. ``workflows/<name>/workflow.toml`` directories (plugin package format)

Plugin packages override legacy entries on name collision.
Each definition is POSTed to the backend API at ``/api/admin/workflows/sync``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from urllib import error, request

from .bootstrap.workflows.default.template_groups import TEMPLATE_GROUPS
from .runtime_context import PACKAGE_ROOT
from .workflow_packages.loader import (
    bundle_to_template_group_dict,
    load_workflow_package,
)

# Root of the ``workflows/`` directory containing plugin packages IN BOOTSTRAP.
# Plugin workflows are first developed in repo root workflows/, then published
# to bootstrap/workflows/default/ via run-bootstrap-publish.bat. The sync script
# loads from the bootstrap location (source of truth), not the dev location.
_WORKFLOWS_DIR = PACKAGE_ROOT / "bootstrap" / "workflows" / "default"


def _discover_plugin_workflows() -> dict[str, dict]:
    """Scan ``workflows/`` for ``workflow.toml`` packages.

    Returns a ``name -> definition dict`` map, where each definition has
    the same shape as a ``TEMPLATE_GROUPS`` entry.
    """
    plugin_workflows: dict[str, dict] = {}
    if not _WORKFLOWS_DIR.is_dir():
        return plugin_workflows

    for candidate in sorted(_WORKFLOWS_DIR.iterdir()):
        if not candidate.is_dir():
            continue
        manifest = candidate / "workflow.toml"
        if not manifest.is_file():
            continue

        bundle = load_workflow_package(candidate)
        group_dict = bundle_to_template_group_dict(bundle)
        plugin_workflows[bundle.name] = group_dict

    return plugin_workflows


def _load_all_workflows() -> dict[str, dict]:
    """Combine legacy ``TEMPLATE_GROUPS`` and plugin packages.

    Plugin packages take priority when a name exists in both sources.
    Plugin packages are loaded from bootstrap/workflows/default/ (source of truth),
    not from repo root workflows/ (development location).
    """
    workflows = dict(TEMPLATE_GROUPS)
    plugin = _discover_plugin_workflows()
    
    # Debug: show what we're loading
    print(f"[sync] Loaded {len(TEMPLATE_GROUPS)} workflows from TEMPLATE_GROUPS", file=sys.stderr)
    print(f"[sync] Discovered {len(plugin)} plugin workflows from bootstrap", file=sys.stderr)
    
    for name, definition in plugin.items():
        if name in workflows:
            print(
                f"[sync] Bootstrap plugin {name!r} overrides legacy TEMPLATE_GROUPS entry.",
                file=sys.stderr,
            )
        workflows[name] = definition

    return workflows


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
) -> dict:
    """POST a single workflow definition to the backend sync endpoint."""
    payload = json.dumps(
        {
            "workflow_name": workflow_name,
            "definition": definition,
            "preserve_history": preserve_history,
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync workflow definitions into the backend registry."
    )
    parser.add_argument(
        "workflow_names",
        nargs="*",
        help=(
            "Workflow names to sync. If omitted, syncs every workflow "
            "from both TEMPLATE_GROUPS and plugin workflow.toml packages."
        ),
    )
    parser.add_argument(
        "--backend-url",
        default=os.environ.get(
            "AGENT_RUNNER_BACKEND_URL", "http://127.0.0.1:8100"
        ),
        help="Backend base URL (default: http://127.0.0.1:8100)",
    )
    parser.add_argument(
        "--preserve-history",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep existing execution history when definitions change.",
    )
    args = parser.parse_args()

    workflows = _load_all_workflows()
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

    failed = False
    for workflow_name in workflow_names:
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
            )
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            print(
                f"[{workflow_name}] sync failed: HTTP {exc.code} {body}",
                file=sys.stderr,
            )
            failed = True
            continue
        except Exception as exc:
            print(
                f"[{workflow_name}] sync failed: {exc}",
                file=sys.stderr,
            )
            failed = True
            continue

        status = response.get("status", "unknown")
        workflow = response.get("workflow", {})
        print(
            f"[{workflow_name}] {status} -> "
            f"id={workflow.get('id')} name={workflow.get('name')}"
        )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
