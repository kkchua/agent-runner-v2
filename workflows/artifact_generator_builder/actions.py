"""Custom actions for Artifact Generator Builder.

This module provides action implementations for the artifact generator
builder workflow. Actions are deterministic, code-driven steps that
perform specific operations without LLM involvement.
"""

from pathlib import Path
from typing import Any

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


@action
def promote_artifact(
    artifacts: dict[str, Any],
    config: dict[str, Any],
    **kwargs: Any,
) -> ActionResult:
    """Promote the generated workflow package to its target location.

    This action copies the generated workflow package from the run output
    directory to the workflows/ directory, creating a backup of any
    existing workflow first.

    Args:
        artifacts: Dictionary of artifact keys to file paths
        config: Step configuration containing artifact_key and backup flag

    Returns:
        ActionResult with promotion status and paths
    """
    artifact_key = config.get("artifact_key", "WORKFLOW_PACKAGE_DIR")
    backup_enabled = config.get("backup", True)

    source_path = Path(artifacts.get(artifact_key, ""))
    if not source_path or not source_path.exists():
        return ActionResult(
            success=False,
            artifact_key="PROMOTION_REPORT_FILE",
            artifact_path="",
            message=f"Artifact {artifact_key} not found at {source_path}",
        )

    # Extract workflow name from the generated workflow.toml
    manifest_path = Path(artifacts.get("WORKFLOW_MANIFEST_FILE", ""))
    if not manifest_path.exists():
        return ActionResult(
            success=False,
            artifact_key="PROMOTION_REPORT_FILE",
            artifact_path="",
            message="WORKFLOW_MANIFEST_FILE not found",
        )

    # Read workflow name from manifest
    import tomli
    with open(manifest_path, "rb") as f:
        manifest = tomli.load(f)

    workflow_name = manifest.get("workflow", {}).get("name", "")
    if not workflow_name:
        return ActionResult(
            success=False,
            artifact_key="PROMOTION_REPORT_FILE",
            artifact_path="",
            message="Workflow name not found in manifest",
        )

    # Determine target path
    workspace_root = source_path.parent.parent.parent  # Navigate up from output/run/repo
    target_path = workspace_root / "workflows" / workflow_name

    # Backup existing workflow if enabled
    backup_status = "No backup needed"
    if backup_enabled and target_path.exists():
        import shutil
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = workspace_root / "workflows" / f"{workflow_name}_bak_{timestamp}"
        shutil.copytree(target_path, backup_path)
        backup_status = f"Backed up existing workflow to {backup_path}"

    # Copy new workflow to target
    import shutil
    if target_path.exists():
        shutil.rmtree(target_path)
    shutil.copytree(source_path, target_path)

    # Write promotion report
    report_path = Path(artifacts.get("PROMOTION_REPORT_FILE", ""))
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_content = f"""# Promotion Report

## Status: SUCCESS

## Workflow Name
{workflow_name}

## Target Path
{target_path}

## Backup Status
{backup_status}

## Files Promoted
- workflow.toml
- context_extensions.py
- actions.py
- prompts/
- README.md
"""
        report_path.write_text(report_content, encoding="utf-8")

    return ActionResult(
        success=True,
        artifact_key="PROMOTION_REPORT_FILE",
        artifact_path=str(report_path) if report_path else "",
        message=f"Promoted workflow to {target_path}",
    )
