from __future__ import annotations

from pathlib import Path
from typing import Any

from .bundle_loader import core_bundles_root
from .constants import RUN_AGENT_REQUIRED_DOC_DIRS
from .path_catalog import known_artifact_paths, legacy_artifact_paths
from .runtime_context import ARTIFACT_ROOT
from .workflow_packages.loader import bundle_to_template_group_dict, load_workflow_package


_REPO_BASED_REFERENCE_KEYS = {
    "PROJECT_ANALYSIS",
    "DELIVERY_AGENTS",
    "DELIVERY_AGENT_PLANNER",
    "DELIVERY_AGENT_TASK_DECOMPOSER",
    "DELIVERY_AGENT_IMPL_PLANNER",
    "DELIVERY_AGENT_EXECUTOR",
    "DELIVERY_AGENT_REVIEWER",
    "DELIVERY_AGENT_MEMORY_MANAGER",
    "DELIVERY_STATUS_RULES",
    "WORKFLOW_SOP",
    "DELIVERY_SOP",
    "CODEBASE_DOC_SOP",
    "CODEBASE_DOC_STATUS_RULES",
    "CODEBASE_INVENTORY",
    "EXISTING_REPO_WORKFLOW_SOP",
    "INTEGRATION_MAP",
    "FAILURE_MODES",
    "ARCHITECTURE_FLOW",
}


def ensure_delivery_folders(target_root: Path) -> None:
    for folder in RUN_AGENT_REQUIRED_DOC_DIRS:
        (target_root / folder).mkdir(parents=True, exist_ok=True)


def load_group(
    group_name: str,
    *,
    workspace_root: Path | None = None,
    workflow_root: Path | None = None,
) -> dict[str, Any]:
    if workflow_root is not None:
        pkg_dir = workflow_root / group_name
        manifest = pkg_dir / "workflow.toml"
        if manifest.is_file():
            bundle = load_workflow_package(pkg_dir)
            group_dict = bundle_to_template_group_dict(bundle)
            group_dict["_workflow_bundle"] = bundle
            return group_dict
        if pkg_dir.is_dir():
            raise FileNotFoundError(
                f"Plugin workflow directory exists at {pkg_dir} "
                f"but no workflow.toml found."
            )

    from .runtime_context import get_workflow_module

    bundle = get_workflow_module()
    if bundle is None:
        raise RuntimeError("Workflow module is not loaded. Runtime must use the global workflow bundle.")
    template_groups = bundle.TEMPLATE_GROUPS
    if group_name not in template_groups:
        valid = ", ".join(sorted(template_groups))
        raise ValueError(f"Unknown template group {group_name!r}. Valid groups: {valid}")
    return template_groups[group_name]


def validate_static_reference_files(
    workspace_root: Path,
    *,
    group_cfg: dict[str, Any] | None = None,
    template_group: str = "",
) -> None:
    if template_group == "00_layer1_governance_bootstrap_v1":
        return

    if group_cfg is None or "reference_files" not in group_cfg:
        return
    reference_files = group_cfg.get("reference_files") or {}
    if not reference_files:
        return

    global_bundle_root = core_bundles_root() / "current"
    missing: list[str] = []

    for key, rel_path in reference_files.items():
        if key in _REPO_BASED_REFERENCE_KEYS:
            file_path = workspace_root / rel_path
            if not file_path.exists():
                missing.append(f"{key}: {rel_path} (not found in workspace at {workspace_root})")
            continue

        filename = Path(rel_path).name
        possible_paths = [
            global_bundle_root / filename,
            global_bundle_root / f"{filename}.md",
            global_bundle_root / rel_path,
        ]
        if not any(path.exists() for path in possible_paths):
            missing.append(f"{key}: {rel_path} (not found in global bundle at {global_bundle_root})")

    if missing:
        raise FileNotFoundError("Missing static reference file(s):\n" + "\n".join(missing))


def missing_artifacts(keys: list[str], state: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if "artifacts" not in state or state["artifacts"] is None:
        state["artifacts"] = {}
    artifacts = state["artifacts"]
    known_paths = known_artifact_paths()
    legacy_paths = legacy_artifact_paths()
    for key in keys:
        value = artifacts.get(key)
        if value and (ARTIFACT_ROOT / value).exists():
            continue
        known_path = known_paths.get(key)
        if known_path and (ARTIFACT_ROOT / known_path).exists():
            artifacts[key] = known_path
            continue
        for legacy_path in legacy_paths.get(key, []):
            if legacy_path and (ARTIFACT_ROOT / legacy_path).exists():
                artifacts[key] = legacy_path
                break
        else:
            missing.append(key)
    return missing


def parse_key_value_pairs(values: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"Invalid --set value {item!r}. Expected KEY=PATH.")
        key, value = item.split("=", 1)
        key, value = key.strip(), value.strip()
        if not key or not value:
            raise ValueError(f"Invalid --set value {item!r}. Expected KEY=PATH.")
        out[key] = value
    return out


def build_config_from_request(
    template_group: str,
    step_name: str,
    *,
    workspace_root: Path | None = None,
    workflow_root: Path | None = None,
    step_execution_spec: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build group_cfg and step_cfg from request with fallback to spec.
    
    This is the unified config builder used by both manual and daemon modes.
    It tries workflow package loading first (same as manual mode), then falls
    back to building from step_execution_spec (daemon/backend compatibility).
    
    Args:
        template_group: Template group identifier
        step_name: Step name to configure
        workspace_root: Workspace directory for plugin workflows
        workflow_root: Workflow bundle root directory
        step_execution_spec: Backend execution spec for fallback
        
    Returns:
        Tuple of (group_cfg, step_cfg) dictionaries
        
    Raises:
        ValueError: If neither workflow package nor spec can provide config
    """
    # Try loading from workflow package first (same as manual mode)
    try:
        group_cfg = load_group(
            template_group,
            workspace_root=workspace_root,
            workflow_root=workflow_root,
        )
        step_cfg = group_cfg.get("step_configs", {}).get(step_name)
        if step_cfg:
            return group_cfg, step_cfg
    except Exception:
        pass
    
    # Fallback: build from step_execution_spec (daemon/backend compatibility)
    if not step_execution_spec:
        raise ValueError(
            f"Cannot build config for {template_group}/{step_name}: "
            f"workflow package not found and no step_execution_spec provided"
        )
    
    return _build_group_cfg_from_spec(step_execution_spec, template_group, step_name)


def _build_group_cfg_from_spec(
    spec: dict[str, Any],
    template_group: str,
    step_name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build group and step config from execution spec.
    
    This is a compatibility fallback when workflow package loading fails.
    It reconstructs the config structure from the backend's step_execution_spec.
    
    Args:
        spec: Execution spec from backend claim
        template_group: Template group identifier  
        step_name: Step name to configure
        
    Returns:
        Tuple of (group_cfg, step_cfg) dictionaries
    """
    from .runtime_context import PACKAGE_ROOT
    
    raw_config = dict(spec.get("raw_config") or {})
    required_inputs = [
        item.get("artifact_key")
        for item in spec.get("required_inputs") or []
        if item.get("artifact_key")
    ]
    optional_inputs = [
        item.get("artifact_key")
        for item in spec.get("optional_inputs") or []
        if item.get("artifact_key")
    ]
    immutable_inputs = [
        item.get("artifact_key")
        for item in spec.get("immutable_inputs") or []
        if item.get("artifact_key")
    ]
    produces = [
        item.get("artifact_key")
        for item in spec.get("produces") or []
        if item.get("artifact_key")
    ]
    updates = [
        item.get("artifact_key")
        for item in spec.get("updates") or []
        if item.get("artifact_key")
    ]
    
    step_cfg = dict(raw_config)
    step_cfg["prompt_file"] = spec.get("prompt_file")
    step_cfg["action"] = spec.get("action_name") or raw_config.get("action")
    step_cfg["edit_mode"] = spec.get("edit_mode")
    step_cfg["result_meta_key"] = spec.get("result_meta_key")
    step_cfg["result_meta_key_from_context"] = spec.get("result_meta_key_from_context")
    step_cfg["template_ref"] = spec.get("template_ref")
    step_cfg["required_inputs"] = required_inputs
    if optional_inputs:
        step_cfg["optional_inputs"] = optional_inputs
    if immutable_inputs:
        step_cfg["immutable_inputs"] = immutable_inputs
    step_cfg["produces"] = produces
    if updates:
        step_cfg["updates"] = updates
    
    target_artifact = spec.get("target_artifact")
    if target_artifact:
        step_cfg["target_artifact"] = target_artifact
    
    coder_policy = spec.get("coder_policy")
    if coder_policy:
        step_cfg["coder"] = {
            "default": coder_policy.get("default_coder"),
            "allowed": list(coder_policy.get("allowed_coders") or []),
            "role_policy": coder_policy.get("role_policy"),
            "default_role": coder_policy.get("default_role"),
            "allowed_roles": list(coder_policy.get("allowed_roles") or []),
            "must_differ_from_previous_step": bool(coder_policy.get("must_differ_from_previous_step")),
        }
    
    # Try to resolve workflow bundle from spec
    bundle = _bundle_from_spec_prompt_file(spec, template_group=template_group)
    if bundle is not None:
        step_cfg["_workflow_bundle"] = bundle
    
    group_cfg = {
        "job_prefix": spec.get("job_prefix") or template_group,
        "job_init_step": spec.get("job_init_step") or step_name,
        "job_init_inputs": list(spec.get("job_init_inputs") or []),
        "default_max_rejects": int(spec.get("default_max_rejects") or 0),
        "reference_files": dict(spec.get("reference_files") or {}),
        "steps": [step_name],
        "step_configs": {step_name: step_cfg},
    }
    
    if bundle is not None:
        group_cfg["_workflow_bundle"] = bundle
    
    return group_cfg, step_cfg


def _bundle_from_spec_prompt_file(
    spec: dict[str, Any],
    *,
    template_group: str,
):
    """Resolve workflow bundle from spec's prompt_file field.
    
    This is a compatibility helper for backend execution specs.
    It tries multiple resolution strategies in order of preference.
    Uses global runner home as fallback (not repo-local bootstrap).
    """
    from .runtime_context import GLOBAL_RUNNER_HOME
    
    prompt_file = spec.get("prompt_file")
    if not isinstance(prompt_file, str) or not prompt_file:
        return _bundle_from_template_group(template_group)
    
    prompt_path = Path(prompt_file)
    candidate_roots: list[Path] = []
    
    if prompt_path.is_absolute():
        candidate_roots.append(prompt_path.parent.parent)
    else:
        candidate_roots.extend(_relative_prompt_bundle_candidates(prompt_path, template_group=template_group))
        candidate_roots.append(GLOBAL_RUNNER_HOME / "workflows" / "default" / template_group)
    
    for bundle_root in candidate_roots:
        manifest = bundle_root / "workflow.toml"
        if not manifest.is_file():
            continue
        try:
            return load_workflow_package(bundle_root)
        except Exception:
            continue
    
    return _bundle_from_template_group(template_group)


def _relative_prompt_bundle_candidates(prompt_path: Path, *, template_group: str) -> list[Path]:
    """Generate candidate bundle roots from relative prompt path."""
    from .runtime_context import GLOBAL_RUNNER_HOME
    
    parts = prompt_path.parts
    roots: list[Path] = []
    default_root = GLOBAL_RUNNER_HOME / "workflows" / "default"
    
    if parts and parts[0] == template_group:
        roots.append(default_root / template_group)
    elif "prompts" in parts:
        roots.append(default_root / template_group)
    
    return roots


def _bundle_from_template_group(template_group: str):
    """Load workflow bundle from template group name in global bootstrap.
    
    Uses the global runner home workflows directory (not repo-local bootstrap).
    This ensures both manual and daemon modes resolve from the same installed-global location.
    """
    from .runtime_context import GLOBAL_RUNNER_HOME
    
    bundle_root = GLOBAL_RUNNER_HOME / "workflows" / "default" / template_group
    manifest = bundle_root / "workflow.toml"
    
    if not manifest.is_file():
        return None
    
    try:
        return load_workflow_package(bundle_root)
    except Exception:
        return None
