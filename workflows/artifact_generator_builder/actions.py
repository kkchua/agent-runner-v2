"""Custom actions for Artifact Generator Builder.

This module provides action implementations for the artifact generator
builder workflow. Actions are deterministic, code-driven steps that
perform specific operations without LLM involvement.
"""

from pathlib import Path
from typing import Any

from agent_runner_v2.action import action


@action
def promote_artifact(
    artifacts: dict[str, Any],
    config: dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    """Promote the generated workflow package to its target location.

    This action copies the generated workflow package from the run output
    directory to the workflows/ directory, creating a backup of any
    existing workflow first.

    Args:
        artifacts: Dictionary of artifact keys to file paths
        config: Step configuration containing artifact_key and backup flag

    Returns:
        Dictionary with promotion status and paths
    """
    artifact_key = config.get("artifact_key", "WORKFLOW_PACKAGE_DIR")
    backup_enabled = config.get("backup", True)

    source_path = Path(artifacts.get(artifact_key, ""))
    if not source_path or not source_path.exists():
        return {
            "status": "ERROR",
            "message": f"Artifact {artifact_key} not found at {source_path}",
        }

    # Extract workflow name from the generated workflow.toml
    manifest_path = Path(artifacts.get("WORKFLOW_MANIFEST_FILE", ""))
    if not manifest_path.exists():
        return {
            "status": "ERROR",
            "message": "WORKFLOW_MANIFEST_FILE not found",
        }

    # Read workflow name from manifest
    import tomli
    with open(manifest_path, "rb") as f:
        manifest = tomli.load(f)

    workflow_name = manifest.get("workflow", {}).get("name", "")
    if not workflow_name:
        return {
            "status": "ERROR",
            "message": "Workflow name not found in manifest",
        }

    # Determine target path
    workspace_root = source_path.parent.parent.parent  # Navigate up from output/run/repo
    target_path = workspace_root / "workflows" / workflow_name

    # Backup existing workflow if enabled
    if backup_enabled and target_path.exists():
        import shutil
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = workspace_root / "workflows" / f"{workflow_name}_bak_{timestamp}"
        shutil.copytree(target_path, backup_path)
        backup_status = f"Backed up existing workflow to {backup_path}"
    else:
        backup_status = "No backup needed"

    # Copy new workflow to target
    import shutil
    if target_path.exists():
        shutil.rmtree(target_path)
    shutil.copytree(source_path, target_path)

    return {
        "status": "SUCCESS",
        "message": f"Promoted workflow to {target_path}",
        "workflow_name": workflow_name,
        "target_path": str(target_path),
        "backup_status": backup_status,
    }
