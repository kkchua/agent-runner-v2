#!/usr/bin/env python3
from __future__ import annotations

"""
actions/archive_previous_version.py - Archive previous version of a file before regeneration.

This action moves an existing file to a versioned archive directory before
a new version is generated. It maintains a configurable number of historical versions.

Configuration in sites.config:
{
  "41_stakeholder_doc_v1": {
    "versioning": {
      "enabled": true,
      "max_versions": 10
    }
  }
}
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from ..action_result import ActionResult
from ..constants import AUDIENCE_MARKDOWN_ARCHIVE_WORKFLOWS, AUDIENCE_SITE_WORKFLOWS
from ..runtime_context import write_meta_sidecar, resolve_step_meta_rel


AUDIENCE_FILES = {
    **AUDIENCE_MARKDOWN_ARCHIVE_WORKFLOWS,
    **{
        workflow: {
            "target_rel": config["html_rel"],
            "archive_dir_rel": config["archive_dir_rel"],
        }
        for workflow, config in AUDIENCE_SITE_WORKFLOWS.items()
    },
}


def _load_versioning_config(*, project_root: Path, template_group: str) -> dict:
    """Load versioning configuration from sites.config.

    Versioning config is global (under _global.versioning) and applies to all workflows.
    """
    config_path = project_root / "docs" / "sites.config"
    if not config_path.exists():
        return {"enabled": True, "max_versions": 10}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception:
        return {"enabled": True, "max_versions": 10}

    # Versioning is global, under _global.versioning
    global_config = config.get("_global", {})
    versioning = global_config.get("versioning", {})

    return {
        "enabled": versioning.get("enabled", True),
        "max_versions": versioning.get("max_versions", 10),
    }


def _cleanup_old_versions(*, archive_dir: Path, max_versions: int) -> list[str]:
    """Remove old versions beyond the max_versions limit."""
    if not archive_dir.exists():
        return []

    # Get all version files, sorted by modification time (newest first)
    version_files = sorted(
        archive_dir.glob("content_*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    removed = []
    if len(version_files) > max_versions:
        for old_file in version_files[max_versions:]:
            old_file.unlink()
            removed.append(old_file.name)

    return removed


def archive_previous_version(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    """Archive previous version of a file before regeneration.

    This action:
    1. Checks if versioning is enabled in sites.config
    2. If the target file exists, moves it to an archive directory with timestamp
    3. Cleans up old versions beyond the max_versions limit
    """
    template_group = str(state.get("template_group") or "")
    step = str(state.get("current_step") or "archive_previous_version")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="ARCHIVE_METAJSON",
        default_step=step,
    )

    # Get audience-specific file paths
    file_config = AUDIENCE_FILES.get(template_group)
    if not file_config:
        result = ActionResult(
            status="APPROVED",
            remark=f"No file configuration for workflow: {template_group}",
            artifacts={},
        )
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="APPROVED",
                remark=result.remark,
                artifacts={},
            )
        return result

    target_rel = file_config["target_rel"]
    archive_dir_rel = file_config["archive_dir_rel"]

    target_path = project_root / target_rel
    archive_dir = project_root / archive_dir_rel

    # Load versioning configuration
    versioning_config = _load_versioning_config(
        project_root=project_root,
        template_group=template_group,
    )

    if not versioning_config["enabled"]:
        result = ActionResult(
            status="APPROVED",
            remark="Versioning disabled in sites.config",
            artifacts={},
        )
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="APPROVED",
                remark=result.remark,
                artifacts={},
            )
        return result

    max_versions = versioning_config["max_versions"]

    # Check if target file exists
    if not target_path.exists():
        result = ActionResult(
            status="APPROVED",
            remark=f"No previous version to archive: {target_rel}",
            artifacts={},
        )
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="APPROVED",
                remark=result.remark,
                artifacts={},
            )
        return result

    # Create archive directory
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp for archive filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_filename = f"content_{timestamp}.md"
    archive_path = archive_dir / archive_filename

    # Move existing file to archive
    try:
        shutil.copy2(target_path, archive_path)
        target_path.unlink()
    except Exception as exc:
        result = ActionResult(
            status="REJECTED",
            remark=f"Failed to archive previous version: {exc}",
            artifacts={},
            reject_code="ARCHIVE_FAILED",
        )
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="REJECTED",
                remark=result.remark,
                artifacts={},
            )
        return result

    # Clean up old versions
    removed = _cleanup_old_versions(archive_dir=archive_dir, max_versions=max_versions)

    remark = f"Archived previous version to {archive_path.relative_to(project_root)}"
    if removed:
        remark += f"; removed {len(removed)} old version(s)"

    artifacts = {
        "ARCHIVED_VERSION": str(archive_path.relative_to(project_root)),
    }

    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark=remark,
            artifacts=artifacts,
        )

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts=artifacts,
    )
