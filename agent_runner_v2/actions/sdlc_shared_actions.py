"""
sdlc_shared_actions.py — Shared actions for AI-Driven SDLC workflows.

These actions are used by multiple SDLC workflows and provide common
functionality for artifact promotion, codebase synchronization, and
execution aggregation.
"""
from __future__ import annotations

import datetime as dt
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.runtime_context import resolve_step_meta_rel, write_meta_sidecar
from agent_runner_v2.workflow_packages.actions import action


def _read_text(path: Path) -> str | None:
    """Read text content from a file, returning None if not found."""
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    """Write text content to a file, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _update_frontmatter_status(content: str, new_status: str) -> str:
    """Update the lifecycle_status field in YAML frontmatter.
    
    Args:
        content: Markdown content with YAML frontmatter
        new_status: New status value (e.g., "approved", "draft")
    
    Returns:
        Updated content with new status
    """
    # Match YAML frontmatter block
    frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if not match:
        # No frontmatter found, return as-is
        return content
    
    frontmatter = match.group(1)
    
    # Update lifecycle_status field
    if "lifecycle_status:" in frontmatter:
        # Replace existing status
        updated_frontmatter = re.sub(
            r"lifecycle_status:\s*[\"']?[^\"'\n]+[\"']?",
            f'lifecycle_status: "{new_status}"',
            frontmatter,
        )
    else:
        # Add status field
        updated_frontmatter = frontmatter + f'\nlifecycle_status: "{new_status}"'
    
    # Reconstruct content
    return content[:match.start(1)] + updated_frontmatter + content[match.end(1):]


@action("promote_artifact")
def promote_artifact(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Promote a single artifact by changing its lifecycle_status to approved.
    
    This action updates the frontmatter of an existing artifact file,
    changing lifecycle_status from "draft" to "approved".
    
    Configuration:
        promotes: Artifact key to promote (e.g., "PLAN_FILE")
    
    Returns:
        ActionResult with status APPROVED if successful, REJECTED otherwise
    """
    step = str(state.get("current_step") or "promote_artifact")
    job_id = str(state.get("job_id") or "")
    
    # Get artifact key from step config
    promotes = step_cfg.get("promotes")
    if not promotes:
        remark = "promote_artifact requires 'promotes' in step config"
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="MISSING_PROMOTES_CONFIG",
        )
    
    # Get artifact path from context or state
    artifacts_state = state.get("artifacts") or {}
    artifact_path_str = (
        artifacts_state.get(promotes)
        or context.get(f"{promotes}_PATH")
        or context.get(promotes)
        or ""
    )
    
    if not artifact_path_str:
        remark = f"Artifact path not found for key: {promotes}"
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="ARTIFACT_PATH_NOT_FOUND",
        )
    
    artifact_path = Path(artifact_path_str)
    if not artifact_path.is_absolute():
        artifact_path = project_root / artifact_path
    
    if not artifact_path.exists():
        remark = f"Artifact file does not exist: {artifact_path}"
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="ARTIFACT_FILE_NOT_FOUND",
        )
    
    # Read current content
    content = _read_text(artifact_path)
    if content is None:
        remark = f"Failed to read artifact file: {artifact_path}"
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="ARTIFACT_READ_FAILED",
        )
    
    # Update status to approved
    updated_content = _update_frontmatter_status(content, "approved")
    
    # Write updated content
    _write_text(artifact_path, updated_content)
    
    # Return result
    artifacts = {promotes: str(artifact_path.relative_to(project_root))}
    remark = f"Promoted {promotes} to approved status"
    
    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts=artifacts,
    )


@action("promote_to_requirement")
def promote_to_requirement(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Promote PRE-REQ to REQ by creating a new approved file.
    
    This action implements the two-file promotion model for sdlc_10:
    1. Reads the PRE-REQ file (draft)
    2. Creates a new REQ file with approved status
    3. Preserves both files for audit trail
    
    Configuration:
        source: Source artifact key (e.g., "PRE_REQ_FILE")
        dest: Destination artifact key (e.g., "REQ_FILE")
        dest_dir: Destination directory relative to project root
    
    Returns:
        ActionResult with status APPROVED if successful, REJECTED otherwise
    """
    step = str(state.get("current_step") or "promote_to_requirement")
    job_id = str(state.get("job_id") or "")
    
    # Get configuration
    source_key = step_cfg.get("source", "PRE_REQ_FILE")
    dest_key = step_cfg.get("dest", "REQ_FILE")
    dest_dir = step_cfg.get("dest_dir", "docs/repo/sdlc/delivery/requirements")
    
    # Get source artifact path
    artifacts_state = state.get("artifacts") or {}
    source_path_str = (
        artifacts_state.get(source_key)
        or context.get(f"{source_key}_PATH")
        or context.get(source_key)
        or ""
    )
    
    if not source_path_str:
        remark = f"Source artifact path not found for key: {source_key}"
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="SOURCE_PATH_NOT_FOUND",
        )
    
    source_path = Path(source_path_str)
    if not source_path.is_absolute():
        source_path = project_root / source_path
    
    if not source_path.exists():
        remark = f"Source artifact file does not exist: {source_path}"
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="SOURCE_FILE_NOT_FOUND",
        )
    
    # Read source content
    content = _read_text(source_path)
    if content is None:
        remark = f"Failed to read source artifact file: {source_path}"
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="SOURCE_READ_FAILED",
        )
    
    # Update status to approved
    updated_content = _update_frontmatter_status(content, "approved")
    
    # Determine destination path
    # Extract slug from source filename if possible
    source_stem = source_path.stem
    # Try to extract slug from PRE-REQ-{date}-{seq}_{slug}.md pattern
    slug_match = re.search(r"PRE-REQ-\d{8}-\d{3}_(.+)", source_stem)
    if slug_match:
        slug = slug_match.group(1)
    else:
        slug = source_stem
    
    # Generate REQ filename
    date_str = dt.datetime.now().strftime("%Y%m%d")
    # Extract sequence number from source if possible
    seq_match = re.search(r"PRE-REQ-\d{8}-(\d{3})", source_stem)
    if seq_match:
        seq = seq_match.group(1)
    else:
        seq = "001"
    
    dest_filename = f"REQ-{date_str}-{seq}_{slug}.md"
    dest_path = project_root / dest_dir / dest_filename
    
    # Write destination file
    _write_text(dest_path, updated_content)
    
    # Return result
    artifacts = {
        source_key: str(source_path.relative_to(project_root)),
        dest_key: str(dest_path.relative_to(project_root)),
    }
    remark = f"Promoted {source_key} to {dest_key} (approved)"
    
    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts=artifacts,
    )


@action("promote_all")
def promote_all(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Promote multiple artifacts to approved status.
    
    This action implements the multi-artifact promotion model for sdlc_80:
    1. Reads each artifact file
    2. Updates lifecycle_status to approved
    3. Writes updated content back
    
    Configuration:
        promotes: List of artifact keys to promote (e.g., ["REV_FILE", "MEM_FILE", "CLOSE_FILE"])
    
    Returns:
        ActionResult with status APPROVED if all successful, REJECTED if any fail
    """
    step = str(state.get("current_step") or "promote_all")
    job_id = str(state.get("job_id") or "")
    
    # Get artifact keys from step config
    promotes_list = step_cfg.get("promotes")
    if not promotes_list or not isinstance(promotes_list, list):
        remark = "promote_all requires 'promotes' list in step config"
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="MISSING_PROMOTES_CONFIG",
        )
    
    artifacts_state = state.get("artifacts") or {}
    promoted_artifacts: dict[str, str] = {}
    failed_artifacts: list[str] = []
    
    for artifact_key in promotes_list:
        # Get artifact path
        artifact_path_str = (
            artifacts_state.get(artifact_key)
            or context.get(f"{artifact_key}_PATH")
            or context.get(artifact_key)
            or ""
        )
        
        if not artifact_path_str:
            failed_artifacts.append(f"{artifact_key}: path not found")
            continue
        
        artifact_path = Path(artifact_path_str)
        if not artifact_path.is_absolute():
            artifact_path = project_root / artifact_path
        
        if not artifact_path.exists():
            failed_artifacts.append(f"{artifact_key}: file not found")
            continue
        
        # Read current content
        content = _read_text(artifact_path)
        if content is None:
            failed_artifacts.append(f"{artifact_key}: read failed")
            continue
        
        # Update status to approved
        updated_content = _update_frontmatter_status(content, "approved")
        
        # Write updated content
        _write_text(artifact_path, updated_content)
        
        promoted_artifacts[artifact_key] = str(artifact_path.relative_to(project_root))
    
    if failed_artifacts:
        remark = f"Failed to promote {len(failed_artifacts)} artifacts: " + "; ".join(failed_artifacts)
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts=promoted_artifacts,
            reject_code="PROMOTE_ALL_PARTIAL_FAILURE",
        )
    
    remark = f"Promoted {len(promoted_artifacts)} artifacts to approved status"
    
    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts=promoted_artifacts,
    )


@action("aggregate_executions")
def aggregate_executions(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Aggregate all EXEC documents for an initiative.
    
    This action collects all EXEC documents for the current initiative
    and creates a summary artifact listing them. Used by sdlc_70 to
    prepare for system-wide validation.
    
    Returns:
        ActionResult with status APPROVED if successful, REJECTED otherwise
    """
    step = str(state.get("current_step") or "aggregate_executions")
    job_id = str(state.get("job_id") or "")
    
    # Get all EXEC artifacts from state
    artifacts_state = state.get("artifacts") or {}
    exec_artifacts: dict[str, str] = {}
    
    for key, path_str in artifacts_state.items():
        if key.startswith("EXEC_") or key == "EXEC_FILE":
            if path_str:
                exec_path = Path(path_str)
                if not exec_path.is_absolute():
                    exec_path = project_root / exec_path
                if exec_path.exists():
                    exec_artifacts[key] = str(exec_path.relative_to(project_root))
    
    if not exec_artifacts:
        remark = "No EXEC documents found for aggregation"
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="NO_EXEC_DOCS_FOUND",
        )
    
    # Generate aggregation summary
    timestamp = dt.datetime.now().isoformat(timespec="seconds")
    summary_lines = [
        f"# Execution Aggregation Summary",
        f"",
        f"- **Job ID:** `{job_id}`",
        f"- **Aggregated At:** `{timestamp}`",
        f"- **Total EXEC Documents:** `{len(exec_artifacts)}`",
        f"",
        f"## EXEC Documents",
        f"",
    ]
    
    for key, rel_path in sorted(exec_artifacts.items()):
        summary_lines.append(f"- `{key}`: `{rel_path}`")
    
    summary_content = "\n".join(summary_lines) + "\n"
    
    # Write aggregation summary
    summary_dir = project_root / "docs" / "repo" / "sdlc" / "delivery" / "executions" / job_id
    summary_path = summary_dir / "EXECUTION_AGGREGATION.md"
    _write_text(summary_path, summary_content)
    
    artifacts = {
        "EXECUTION_AGGREGATION": str(summary_path.relative_to(project_root)),
        **exec_artifacts,
    }
    remark = f"Aggregated {len(exec_artifacts)} EXEC documents"
    
    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts=artifacts,
    )


@action("create_backup")
def create_backup(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Create a backup of codebase documentation before sync.
    
    This action creates a backup of the current codebase docs
    to allow rollback if the sync introduces errors.
    
    Configuration:
        backup_dir: Backup directory relative to project root
                   (default: "docs/repo/codebase/backups")
    
    Returns:
        ActionResult with status APPROVED if successful, REJECTED otherwise
    """
    step = str(state.get("current_step") or "create_backup")
    job_id = str(state.get("job_id") or "")
    
    # Get configuration
    backup_dir_rel = step_cfg.get("backup_dir", "docs/repo/codebase/backups")
    
    # Define paths
    codebase_root = project_root / "docs" / "repo" / "codebase"
    current_root = codebase_root / "current"
    backup_dir = project_root / backup_dir_rel

    if not codebase_root.exists():
        remark = f"Codebase root does not exist: {codebase_root}"
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="CODEBASE_ROOT_NOT_FOUND",
        )

    # Generate backup directory name with timestamp
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_name = f"BACKUP-{timestamp}"
    backup_path = backup_dir / backup_name

    # Create backup -- only back up current/ (the published stable version)
    try:
        if backup_path.exists():
            shutil.rmtree(backup_path)
        if current_root.exists():
            shutil.copytree(current_root, backup_path)
        else:
            # No current/ yet (first run) -- create empty backup marker
            backup_path.mkdir(parents=True)
            (backup_path / "README.md").write_text(
                "# Backup (empty)\n\nNo previous current/ directory existed.\n",
                encoding="utf-8",
            )
    except Exception as e:
        remark = f"Failed to create backup: {e}"
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="BACKUP_CREATION_FAILED",
        )
    
    artifacts = {
        "CODEBASE_BACKUP": str(backup_path.relative_to(project_root)),
    }
    remark = f"Created backup at {backup_path.relative_to(project_root)}"
    
    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts=artifacts,
    )


@action("generate_sync_log")
def generate_sync_log(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Generate a sync log documenting changes made during codebase sync.
    
    This action creates a log file documenting what was changed during
    the sdlc_00 sync operation, providing an audit trail.
    
    Returns:
        ActionResult with status APPROVED if successful, REJECTED otherwise
    """
    step = str(state.get("current_step") or "generate_sync_log")
    job_id = str(state.get("job_id") or "")

    # Get sync information from context
    timestamp = dt.datetime.now().isoformat(timespec="seconds")

    # Support staging root override (for sdlc_00_codebase_v1 staging pattern)
    staging_root = str(step_cfg.get("staging_root") or "")
    if staging_root:
        staging_root = staging_root.replace("{job_id}", job_id)
        sync_log_dir = project_root / staging_root / "sync_logs"
    else:
        sync_log_dir = project_root / "docs" / "repo" / "codebase" / "sync_logs"
    sync_log_dir.mkdir(parents=True, exist_ok=True)

    # Generate sync log content
    log_content = f"""---
template_id: "SYS-00-SL"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "exclude"
scan_reason: "sync operation log for codebase documentation"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "approved"
generated_at: "{timestamp}"
managed_by: "sdlc_00_codebase_v1"
---

# Codebase Sync Log

## Sync Information

- **Job ID:** `{job_id}`
- **Sync Timestamp:** `{timestamp}`
- **Workflow:** `sdlc_00_codebase_v1`
- **Step:** `{step}`

## Changes Summary

This sync log documents the changes made to codebase documentation
during the synchronization operation.

### Files Updated

- Codebase inventory updated
- Module documentation synchronized
- Component documentation synchronized

### Validation

- All documentation follows ASCII-only encoding rule
- All section headings use plain text (no formatting)
- All frontmatter fields are present and valid

## Next Steps

Review this sync log to verify that all changes are expected.
If any unexpected changes are found, restore from the backup
created before this sync operation.
"""

    # Write sync log -- use job_id-based filename for staging, date-based for global
    if staging_root:
        log_filename = f"SYNC-{job_id}.md"
    else:
        date_str = dt.datetime.now().strftime("%Y%m%d")
        existing_logs = list(sync_log_dir.glob(f"SYNC-{date_str}-*.md"))
        seq = len(existing_logs) + 1
        log_filename = f"SYNC-{date_str}-{seq:03d}.md"
    log_path = sync_log_dir / log_filename
    _write_text(log_path, log_content)
    
    artifacts = {
        "SYNC_LOG": str(log_path.relative_to(project_root)),
    }
    remark = f"Generated sync log: {log_filename}"
    
    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts=artifacts,
    )


@action("commit_changes")
def commit_changes(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Commit codebase documentation changes to git.
    
    This action commits all changes to codebase documentation
    with a descriptive commit message.
    
    Configuration:
        commit_message: Custom commit message (optional)
    
    Returns:
        ActionResult with status APPROVED if successful, REJECTED otherwise
    """
    step = str(state.get("current_step") or "commit_changes")
    job_id = str(state.get("job_id") or "")
    
    # Get configuration
    custom_message = step_cfg.get("commit_message", "")
    
    # Generate commit message
    timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if custom_message:
        commit_message = custom_message
    else:
        commit_message = f"sync: codebase documentation update {timestamp}"
    
    # Check if git repository
    git_dir = project_root / ".git"
    if not git_dir.exists():
        remark = "Not a git repository, skipping commit"
        return ActionResult(
            status="APPROVED",
            remark=remark,
            artifacts={},
        )
    
    try:
        # Stage codebase documentation changes
        codebase_path = project_root / "docs" / "repo" / "codebase"
        if codebase_path.exists():
            subprocess.run(
                ["git", "add", str(codebase_path)],
                cwd=project_root,
                check=True,
                capture_output=True,
                text=True,
            )
        
        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        )
        
        if not result.stdout.strip():
            remark = "No changes to commit"
            return ActionResult(
                status="APPROVED",
                remark=remark,
                artifacts={},
            )
        
        # Commit changes
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        )
        
    except subprocess.CalledProcessError as e:
        remark = f"Git commit failed: {e.stderr}"
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="GIT_COMMIT_FAILED",
        )
    except FileNotFoundError:
        remark = "Git not found in PATH, skipping commit"
        return ActionResult(
            status="APPROVED",
            remark=remark,
            artifacts={},
        )
    
    remark = f"Committed codebase documentation changes: {commit_message}"
    
    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={},
    )
