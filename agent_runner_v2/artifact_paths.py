#!/usr/bin/env python3
"""
artifact_paths.py — Single source of truth for all step artifact paths.

Design:
1. One function: `compute_paths(node_id, title, output_dir, ext=".md")`
2. Returns (artifact_path, meta_json_path) — always same base name.
3. No parsing. Node ID IS the base. Title is appended as slug.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

logger = logging.getLogger(__name__)


def compute_paths(
    *,
    node_id: str,
    title: str = "",
    output_dir: str,
    ext: str = ".md",
) -> tuple[str, str]:
    """Return (artifact_path, meta_json_path) — single source of truth.

    The node_id from the task graph is already the canonical identifier.
    We just use it as the base filename. Title is appended as sanitized slug
    only if provided and different from node_id's existing slug.

    Args:
        node_id:    Task node ID from task graph (e.g., "TASK-20260413-07_supersede-workflow").
        title:      Human-readable title (e.g., "Supersede Workflow Implementation").
        output_dir: Relative output directory (e.g., "docs/delivery/03_tasks").
        ext:        Artifact file extension (default ".md").

    Returns:
        (artifact_path, meta_json_path) as repo-relative POSIX paths.
    """
    # The node_id is the canonical prefix: TASK-YYYYMMDD-NN
    # Build the full filename by appending the title as a slug.
    # Example: TASK-20260413-07 + "Supersede Workflow" → TASK-20260413-07_supersede-workflow.md

    if title:
        title_slug = re.sub(r"[^a-z0-9]+", "-", title.lower().strip()).strip("-")
        base_name = f"{node_id}_{title_slug}"
    else:
        base_name = node_id

    artifact_path = str(PurePosixPath(output_dir) / f"{base_name}{ext}")
    meta_json_path = str(PurePosixPath(output_dir) / f"{base_name}.meta.json")

    logger.debug(f"compute_paths: node_id='{node_id}', title='{title}'")
    logger.debug(f"  base_name      = '{base_name}'")
    logger.debug(f"  artifact_path  = '{artifact_path}'")
    logger.debug(f"  meta_json_path = '{meta_json_path}'")

    return artifact_path, meta_json_path


def meta_json_path_for_artifact(artifact_path: str) -> str:
    """Return the meta.json path for any artifact path.

    Simply replaces the extension with .meta.json.
    """
    p = PurePosixPath(artifact_path)
    return str(p.parent / f"{p.stem}.meta.json")


def load_meta_json(artifact_path: str) -> dict | None:
    """Load coder-written meta.json. Returns None if missing."""
    meta_path = meta_json_path_for_artifact(artifact_path)
    full_path = Path(meta_path)
    if not full_path.exists() or not full_path.is_file():
        return None
    try:
        return json.loads(full_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def read_coder_result(artifact_path: str) -> dict | None:
    """Read coder_result from meta.json. Returns None if missing or invalid."""
    meta = load_meta_json(artifact_path)
    if not meta:
        return None
    coder_result = meta.get("coder_result")
    if not isinstance(coder_result, dict):
        return None
    status = coder_result.get("status", "").upper()
    if status not in ("APPROVED", "REJECTED"):
        return None
    return coder_result
