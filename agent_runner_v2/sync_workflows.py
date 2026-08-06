"""Sync workflow definitions to the V2 backend registry.

Discovers workflows from packaged ``workflow.toml`` workflow directories,
converts from runner format to V2 backend format, validates locally,
then POSTs to the V2 backend API at ``/api/workflows/sync``.

V2 backend format differs from runner's TEMPLATE_GROUPS format:
  Runner:  {"steps": [...], "step_configs": {"name": {...}}}
  V2:      {"steps": {"name": {...}}, "init_step": "...", ...}
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from .config_loader import load_runner_config
from .workflow_packages.loader import (
    bundle_to_template_group_dict,
    load_workflow_package,
)
from .workflow_bundle_validator import validate_workflow_bundle_dir


# ---------------------------------------------------------------------------
# URL resolution
# ---------------------------------------------------------------------------

def _resolve_backend_url(cfg: dict, cli_url: str) -> str:
    """Resolve backend URL — prefer V2 over V1.

    Priority: CLI flag > V2 env > V2 config > V1 env > V1 config > default.
    """
    if cli_url:
        return cli_url
    v2_env = os.environ.get("AGENT_RUNNER_V2_BACKEND_URL", "").strip()
    if v2_env:
        return v2_env
    v2_cfg = str(cfg.get("v2_backend_url") or "").strip()
    if v2_cfg:
        return v2_cfg
    v1_env = os.environ.get("AGENT_RUNNER_BACKEND_URL", "").strip()
    if v1_env:
        return v1_env
    return str(cfg.get("backend_url") or "") or "http://127.0.0.1:8100"


# ---------------------------------------------------------------------------
# Format conversion: runner TEMPLATE_GROUPS → V2 backend definition
# ---------------------------------------------------------------------------

def convert_to_v2_format(group_dict: dict) -> dict:
    """Convert runner's TEMPLATE_GROUPS format to V2 backend definition format.

    Runner format (from bundle_to_template_group_dict):
        {"steps": ["a", "b"], "step_configs": {"a": {"onsuccess": "...", ...}}}

    V2 backend format:
        {"job_prefix": "...", "init_step": "...", "default_max_rejects": N,
         "steps": {"a": {"onsuccess": "...", ...}, "b": {...}}}
    """
    step_configs = group_dict.get("step_configs", {})
    steps_order = group_dict.get("steps", [])

    definition = {
        "job_prefix": group_dict.get("job_prefix", "JOB"),
        "init_step": group_dict.get("job_init_step"),
        "default_max_rejects": group_dict.get("default_max_rejects", 0),
        "steps": {},
    }

    for step_name in steps_order:
        cfg = step_configs.get(step_name, {})
        # Store the full step config as-is to preserve all data
        # (bundle_to_template_group_dict flattens artifacts, so reconstruct)
        step_def = dict(cfg)
        # Reconstruct nested artifacts from flattened fields
        artifacts = {}
        for key in ("required_inputs", "optional_inputs", "immutable_inputs",
                     "produces", "updates", "result_meta_key", "target_artifact", "edit_mode"):
            if key in step_def:
                artifacts[key] = step_def.pop(key)
        if artifacts:
            step_def["artifacts"] = artifacts
        definition["steps"][step_name] = step_def

    return definition


def _extract_init_input_dirs(bundle_dir: Path, group_dict: dict) -> dict[str, str]:
    """Extract artifact path directories for init step required inputs.

    Loads the workflow's context_extensions.py, calls register_artifact_keys(),
    and returns the directory portion of each init input's path template.

    Returns:
        Dict mapping artifact_key → directory (e.g. {"DRAFT_INIT_FILE": "docs/.../00_draft_initiatives"})
    """
    import importlib.util

    context_ext_file = bundle_dir / "context_extensions.py"
    if not context_ext_file.is_file():
        return {}

    # Find init step's required inputs
    init_step_name = group_dict.get("job_init_step")
    if not init_step_name:
        return {}

    step_configs = group_dict.get("step_configs", {})
    init_cfg = step_configs.get(init_step_name, {})
    # Adapter flattens artifacts to top-level; try nested first, then flat
    artifacts_cfg = init_cfg.get("artifacts") or init_cfg
    required_inputs = artifacts_cfg.get("required_inputs", [])
    if not required_inputs:
        return {}

    # Load context_extensions module
    spec = importlib.util.spec_from_file_location("_ctx_ext", context_ext_file)
    if spec is None or spec.loader is None:
        return {}
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        return {}

    # Find WorkflowExtensions subclass
    from agent_runner_v2.workflow_packages.extensions_base import WorkflowExtensions
    ext_cls = None
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name)
        if (isinstance(attr, type) and issubclass(attr, WorkflowExtensions)
                and attr is not WorkflowExtensions):
            ext_cls = attr
            break
    if ext_cls is None:
        return {}

    # Get path templates
    instance = ext_cls()
    try:
        path_templates = instance.register_artifact_keys()
    except Exception:
        return {}

    # Extract directory portion for each required input
    result: dict[str, str] = {}
    for key in required_inputs:
        template = path_templates.get(key)
        if template:
            if "/" in template:
                directory = template.rsplit("/", 1)[0]
            else:
                directory = ""
            result[key] = directory

    return result


# ---------------------------------------------------------------------------
# Workflow discovery
# ---------------------------------------------------------------------------

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

        print(f"  [plugin] Loaded {bundle.name!r}: default_max_rejects={bundle.default_max_rejects}", file=sys.stderr)
        plugin_workflows[bundle.name] = group_dict

    return plugin_workflows


def _load_all_workflows(workflows_dir: Path) -> dict[str, dict]:
    """Load workflow definitions from the current repo workflow packages."""
    plugin = _discover_plugin_workflows(workflows_dir)
    print(f"[sync] Discovered {len(plugin)} workflow packages from {workflows_dir}", file=sys.stderr)
    return plugin


def _strip_bundle_refs(definition: dict) -> dict:
    """Remove runtime-only ``_workflow_bundle`` references before serialization."""
    step_configs = definition.get("step_configs", {})
    for cfg in step_configs.values():
        cfg.pop("_workflow_bundle", None)
    return definition


# ---------------------------------------------------------------------------
# Backend sync
# ---------------------------------------------------------------------------

def _post_sync(
    backend_url: str,
    workflow_name: str,
    definition: dict,
) -> dict:
    """POST a V2-format workflow definition to the backend sync endpoint."""
    from .v2.backend_client import V2BackendClient
    from .v2.sync import resolve_v2_api_key

    api_key = resolve_v2_api_key()
    client = V2BackendClient(backend_url, api_key=api_key)
    return client.sync_workflow(
        workflow_name=workflow_name,
        definition=definition,
    )


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    cfg = load_runner_config()
    parser = argparse.ArgumentParser(
        description=(
            "Validate workflow bundles locally, convert to V2 backend format, "
            "then sync to the V2 backend registry."
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
        default="",
        help="V2 backend URL (default: config.json v2_backend_url, else V1 backend_url)",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip local validation before sync.",
    )
    args = parser.parse_args(argv)

    backend_url = _resolve_backend_url(cfg, args.backend_url)

    workflows_dir = _workflows_dir()
    if not workflows_dir.is_dir():
        print(f"ERROR: Required workflow source folder is missing: {workflows_dir}", file=sys.stderr)
        return 2

    workflows = _load_all_workflows(workflows_dir)
    workflow_names = args.workflow_names or sorted(workflows.keys())

    missing = [name for name in workflow_names if name not in workflows]
    if missing:
        print(f"Unknown workflow name(s): {', '.join(missing)}", file=sys.stderr)
        return 2

    print(f"Backend URL: {backend_url}")
    print(f"Workflows: {', '.join(workflow_names)}")
    print("Format: V2 backend (steps dict, not steps list)")

    failed = False
    synced: list[str] = []
    validation_failed: list[str] = []
    transport_failed: list[str] = []

    for workflow_name in workflow_names:
        bundle_dir = workflows_dir / workflow_name

        if not args.skip_validation:
            validation = validate_workflow_bundle_dir(bundle_dir)
            if not validation.valid:
                _print_validation_failure(workflow_name, validation)
                failed = True
                validation_failed.append(workflow_name)
                continue

        group_dict = _strip_bundle_refs(workflows[workflow_name])
        v2_definition = convert_to_v2_format(group_dict)

        # Extract artifact path directories for init step required inputs
        init_input_dirs = _extract_init_input_dirs(bundle_dir, workflows[workflow_name])
        if init_input_dirs:
            v2_definition["init_input_dirs"] = init_input_dirs

        source_hash = hashlib.sha256(
            json.dumps(v2_definition, sort_keys=True).encode("utf-8")
        ).hexdigest()

        print(f"\n[{workflow_name}] Preparing sync:", file=sys.stderr)
        print(f"  init_step: {v2_definition.get('init_step')}", file=sys.stderr)
        print(f"  steps count: {len(v2_definition.get('steps', {}))}", file=sys.stderr)
        print(f"  default_max_rejects: {v2_definition.get('default_max_rejects')}", file=sys.stderr)
        print(f"  source_hash (first 16): {source_hash[:16]}...", file=sys.stderr)

        try:
            response = _post_sync(backend_url, workflow_name, v2_definition)
        except Exception as exc:
            print(f"[{workflow_name}] sync failed: {exc}", file=sys.stderr)
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
