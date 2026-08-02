#!/usr/bin/env python3
"""Archive input files from a source directory to an archive directory.

Moves files from source_dir to archive_dir. Creates the archive directory
if it doesn't exist.

By default, moves ALL files in source_dir. If index_file is configured,
only moves files listed in the index (from a previous generation step).

Index files (index.json) in source_dir are deleted, not archived.

Step config (from workflow.toml extra passthrough):
    source_dir: Source directory relative to project_root (e.g. "step_02")
    archive_dir: Archive directory relative to project_root (e.g. "step_02_archive")
    index_file: Optional index.json path relative to project_root (e.g. "step_03/index.json")
                If provided, only files listed in the index are archived.
"""
from __future__ import annotations

import json
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

    Reads source_dir, archive_dir, and optional index_file from step_cfg
    (extra passthrough from workflow.toml). All paths are relative to
    project_root.

    If index_file is provided, only archives files listed in the index's
    'input' or 'updated_json' fields. Otherwise archives all files.

    Index files (index.json) in source_dir are deleted, not archived.
    """
    source_dir_rel = str(step_cfg.get("source_dir", "")).strip()
    archive_dir_rel = str(step_cfg.get("archive_dir", "")).strip()
    index_file_rel = str(step_cfg.get("index_file", "")).strip()

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
            status="APPROVED",
            remark=f"Source directory not found: {source_dir_rel}/ — nothing to archive (may have been archived in a previous run).",
            artifacts={},
        )

    archive_dir.mkdir(parents=True, exist_ok=True)

    # Build set of files to archive from index (if provided)
    files_to_archive = None
    if index_file_rel:
        index_path = Path(project_root) / index_file_rel
        if index_path.is_file():
            try:
                with open(index_path, "r", encoding="utf-8") as f:
                    index_data = json.load(f)
                files_to_archive = set()
                for mapping in index_data.get("files", []):
                    # Extract filename from input path (e.g., "step_02/1a.json" → "1a.json")
                    input_path = mapping.get("input", "")
                    if input_path:
                        files_to_archive.add(Path(input_path).name)
                    # Also include updated_json if present
                    updated_json = mapping.get("updated_json", "")
                    if updated_json:
                        files_to_archive.add(Path(updated_json).name)
                logger.info(
                    "archive_inputs: index_file=%s specifies %d file(s) to archive",
                    index_file_rel, len(files_to_archive),
                )
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning(
                    "archive_inputs: failed to read index_file=%s: %s — archiving all files",
                    index_file_rel, exc,
                )
        else:
            logger.warning(
                "archive_inputs: index_file=%s not found — archiving all files",
                index_file_rel,
            )

    files_archived = []
    files_deleted = []
    for item in sorted(source_dir.iterdir()):
        if not item.is_file():
            continue

        # Delete index.json files, don't archive them
        if item.name == "index.json":
            item.unlink()
            files_deleted.append(item.name)
            logger.info("archive_inputs: deleted %s", item.name)
            continue

        # If index_file provided, only archive files in the index
        if files_to_archive is not None and item.name not in files_to_archive:
            logger.debug(
                "archive_inputs: skipping %s (not in index)", item.name,
            )
            continue

        dest = archive_dir / item.name
        # Handle filename conflicts — add sequence suffix if dest exists
        if dest.exists():
            stem = item.stem
            suffix = item.suffix
            seq = 1
            while dest.exists():
                dest = archive_dir / f"{stem}_{seq:03d}{suffix}"
                seq += 1
            logger.info(
                "archive_inputs: conflict — %s already exists, renaming to %s",
                item.name, dest.name,
            )
        shutil.move(str(item), str(dest))
        files_archived.append(item.name)
        logger.info("archive_inputs: moved %s → %s", item.name, archive_dir.name)

    if not files_archived and not files_deleted:
        return ActionResult(
            status="APPROVED",
            remark=f"No files to archive in {source_dir_rel}/.",
            artifacts={},
        )

    remark_parts = []
    if files_archived:
        remark_parts.append(
            f"Archived {len(files_archived)} file(s) from {source_dir_rel}/ to {archive_dir_rel}/"
        )
    if files_deleted:
        remark_parts.append(f"Deleted {len(files_deleted)} index file(s)")

    return ActionResult(
        status="APPROVED",
        remark=". ".join(remark_parts) + ".",
        artifacts={},
    )
