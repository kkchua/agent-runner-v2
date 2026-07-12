from __future__ import annotations

from pathlib import Path
from typing import Any


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


def ensure_delivery_folders(target_root: Path, *, hooks: Any) -> None:
    for folder in hooks.RUN_AGENT_REQUIRED_DOC_DIRS:
        (target_root / folder).mkdir(parents=True, exist_ok=True)


def load_group(
    group_name: str,
    *,
    workspace_root: Path | None = None,
    workflow_root: Path | None = None,
    hooks: Any,
) -> dict[str, Any]:
    if workflow_root is not None:
        pkg_dir = workflow_root / group_name
        manifest = pkg_dir / "workflow.toml"
        if manifest.is_file():
            bundle = hooks.load_workflow_package(pkg_dir)
            group_dict = hooks.bundle_to_template_group_dict(bundle)
            group_dict["_workflow_bundle"] = bundle
            return group_dict
        if pkg_dir.is_dir():
            raise FileNotFoundError(
                f"Plugin workflow directory exists at {pkg_dir} "
                f"but no workflow.toml found."
            )

    bundle = hooks.get_workflow_module()
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
    hooks: Any,
) -> None:
    if template_group in ("00_master_docs_bootstrap_v1", "00_master_docs_bootstrap_v2", "10_execution_scaffold_v1", "10_execution_scaffold_v2", "delivery_scaffold_v1") or template_group.startswith("delivery_scaffold"):
        return

    if group_cfg is None or "reference_files" not in group_cfg:
        return
    reference_files = group_cfg.get("reference_files") or {}
    if not reference_files:
        return

    global_bundle_root = hooks.core_bundles_root() / "current"
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


def missing_artifacts(keys: list[str], state: dict[str, Any], *, hooks: Any) -> list[str]:
    missing: list[str] = []
    if "artifacts" not in state or state["artifacts"] is None:
        state["artifacts"] = {}
    artifacts = state["artifacts"]
    known_paths = hooks.known_artifact_paths()
    legacy_paths = hooks.legacy_artifact_paths()
    for key in keys:
        value = artifacts.get(key)
        if value and (hooks.ARTIFACT_ROOT / value).exists():
            continue
        known_path = known_paths.get(key)
        if known_path and (hooks.ARTIFACT_ROOT / known_path).exists():
            artifacts[key] = known_path
            continue
        for legacy_path in legacy_paths.get(key, []):
            if legacy_path and (hooks.ARTIFACT_ROOT / legacy_path).exists():
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
