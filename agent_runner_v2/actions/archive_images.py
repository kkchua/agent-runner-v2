#!/usr/bin/env python3
"""
actions/archive_images.py - Move processed source images to an archive folder.

After a successful ComfyUI submission, this action moves the original source
images (and their description files) from source_images/ to
archive/<run_dir>/ at the project root level — outside the source folder
so they won't be picked up on the next run.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path, PurePath

from ..action_result import ActionResult

# Image file extensions to archive
_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff", ".tif"}


def _write_meta(
    project_root: Path,
    archive_dir: Path,
    status: str,
    remark: str,
    artifacts: dict,
) -> None:
    """Write meta.json sidecar."""
    meta_path = archive_dir / "meta.json"
    archive_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "schema_version": "v2",
        "coder_result": {
            "status": status,
            "remark": remark,
            "artifacts": artifacts,
            "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        },
    }
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _fail(
    project_root: Path,
    archive_dir: Path,
    remark: str,
    code: str,
) -> ActionResult:
    """Write meta.json for rejection and return ActionResult."""
    _write_meta(project_root, archive_dir, "REJECTED", remark, {})
    return ActionResult(
        status="REJECTED",
        remark=remark,
        artifacts={},
        reject_code=code,
    )


def archive_images(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Move processed source images to archive/<run_dir>/."""

    # Determine the run directory from context.
    # Try IMAGE_CSV_RUN_DIR first, then fall back to deriving from IMAGE_CSV_JSON artifact.
    run_dir_str = context.get("IMAGE_CSV_RUN_DIR", "")
    if not run_dir_str:
        existing = context.get("IMAGE_CSV_JSON", "")
        if existing:
            run_dir_str = existing.rstrip("/")

    if not run_dir_str:
        archive_dir = project_root / "archive" / "unknown"
        return _fail(project_root, archive_dir,
                     "Cannot determine run directory: IMAGE_CSV_RUN_DIR and IMAGE_CSV_JSON are both empty",
                     "MISSING_RUN_DIR")

    # Extract the run directory name (e.g. "20260531-005") from the full path
    run_dir_name = PurePath(run_dir_str).name

    # Archive location: project_root/archive/<run_dir_name>/
    archive_dir = project_root / "archive" / run_dir_name

    # Source image folder
    image_folder_str = context.get("IMAGE_FOLDER", "")
    if not image_folder_str:
        return _fail(project_root, archive_dir,
                     "IMAGE_FOLDER context variable is empty",
                     "MISSING_IMAGE_FOLDER")

    source_dir = project_root / image_folder_str
    if not source_dir.exists() or not source_dir.is_dir():
        return _fail(project_root, archive_dir,
                     f"Source image directory does not exist: {source_dir}",
                     "SOURCE_DIR_MISSING")

    # Collect files to archive: images + description JSONs
    files_to_move = []
    for f in source_dir.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() in _IMAGE_EXTS:
            files_to_move.append(f)
        elif f.suffix == ".json" and f.name != "meta.json":
            # Description JSON files (not the step sidecar)
            files_to_move.append(f)

    if not files_to_move:
        return _fail(project_root, archive_dir,
                     "No image files found in source folder to archive",
                     "NO_FILES_TO_ARCHIVE")

    # Create archive directory and move files
    archive_dir.mkdir(parents=True, exist_ok=True)
    moved = []
    for src in files_to_move:
        dest = archive_dir / src.name
        shutil.move(str(src), str(dest))
        moved.append(dest.name)

    # Write summary
    summary_path = archive_dir / "archive_summary.json"
    summary = {
        "schema_version": "v2",
        "source_folder": image_folder_str,
        "archive_folder": str(archive_dir.relative_to(project_root)),
        "run_directory": run_dir_name,
        "archived_files": sorted(moved),
        "archived_count": len(moved),
        "archived_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    remark = f"Archived {len(moved)} files to archive/{run_dir_name}/"
    artifacts = {
        "ARCHIVED_IMAGES": str(archive_dir.relative_to(project_root)),
    }

    _write_meta(project_root, archive_dir, "APPROVED", remark, artifacts)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts=artifacts,
    )
