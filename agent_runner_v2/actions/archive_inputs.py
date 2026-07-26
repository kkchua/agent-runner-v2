#!/usr/bin/env python3
"""Archive input files from a source directory to an archive directory.

Moves all files (not subdirectories) from source_dir to archive_dir.
Creates the archive directory if it doesn't exist.

Step config (from workflow.toml extra passthrough):
    source_dir: Source directory relative to project_root (e.g. "step_02")
    archive_dir: Archive directory relative to project_root (e.g. "step_02_archive")
"""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

from ..action_result import ActionResult

logger = logging.getLogger(__name__)


def archive_inputs(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Move files from source_dir to archive_dir.

    Reads source_dir and archive_dir from step_cfg (extra passthrough
    from workflow.toml). Both paths are relative to project_root.
    """
    source_dir_rel = str(step_cfg.get("source_dir", "")).strip()
    archive_dir_rel = str(step_cfg.get("archive_dir", "")).strip()

    if not source_dir_rel:
        return ActionResult(
            status="REJECTED",
            remark="source_dir not configured in step config.",
            artifacts={},
            reject_code="MISSING_CONFIG",
        )
    if not archive_dir_rel:
        return ActionResult(
            status="REJECTED",
            remark="archive_dir not configured in step config.",
            artifacts={},
            reject_code="MISSING_CONFIG",
        )

    source_dir = Path(project_root) / source_dir_rel
    archive_dir = Path(project_root) / archive_dir_rel

    if not source_dir.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"Source directory not found: {source_dir}",
            artifacts={},
            reject_code="SOURCE_NOT_FOUND",
        )

    archive_dir.mkdir(parents=True, exist_ok=True)

    files_archived = []
    for item in sorted(source_dir.iterdir()):
        if item.is_file():
            dest = archive_dir / item.name
            shutil.move(str(item), str(dest))
            files_archived.append(item.name)
            logger.info("archive_inputs: moved %s → %s", item.name, archive_dir.name)

    if not files_archived:
        return ActionResult(
            status="APPROVED",
            remark=f"No files to archive in {source_dir_rel}/.",
            artifacts={},
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Archived {len(files_archived)} file(s) from {source_dir_rel}/ to {archive_dir_rel}/.",
        artifacts={},
    )
