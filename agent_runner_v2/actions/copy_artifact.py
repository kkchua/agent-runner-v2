#!/usr/bin/env python3
"""
actions/copy_artifact.py — Copy an artifact to a new canonical destination path.

Step config:
    "source": "PRE_INIT_FILE"       # artifact key to read from context
    "dest_artifact": "INIT_FILE"    # artifact key for the output file
    "dest_dir": "docs/delivery/01_initiatives"
    "filename_strategy": "init_id_slug"   # derive filename from content metadata
    "result_meta_key": "INIT_FILE"

filename_strategy options:
  "init_id_slug" — extract Initiative ID + H1 title from content, build
                   "<INIT-ID>_<kebab-title>.md"
  (default)      — reuse the source filename as-is
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path

from ..action_result import ActionResult
from ..runtime_context import write_meta_sidecar

logger = logging.getLogger(__name__)

_INIT_ID_RE = re.compile(r"Initiative\s+ID[^`\n]*`?(INIT-[\w-]+)`?", re.IGNORECASE)


def _extract_init_id(text: str) -> str | None:
    m = _INIT_ID_RE.search(text)
    return m.group(1).strip() if m else None


def _extract_title(text: str) -> str | None:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            title = line[2:].strip()
            title = re.sub(r"^Initiative\s*:\s*INIT-[\w-]+\s*[—\-]+\s*", "", title, flags=re.IGNORECASE).strip()
            return title or None
    return None


def _to_slug(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^\w\s-]", "", title)
    title = re.sub(r"[\s_]+", "-", title)
    return title.strip("-")


def _upsert_metadata_field(content: str, field: str, value: str) -> str:
    row_re = re.compile(rf"^\|\s*{re.escape(field)}\s*\|.*$", re.MULTILINE)
    new_row = f"| {field} | `{value}` |"
    if row_re.search(content):
        return row_re.sub(new_row, content, count=1)
    metadata_anchor = "## Metadata\n\n| Field | Value |\n|---|---|\n"
    if metadata_anchor in content:
        return content.replace(metadata_anchor, metadata_anchor + new_row + "\n", 1)
    return content


def copy_artifact(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    source_key = step_cfg.get("source", "")
    dest_artifact_key = step_cfg.get("dest_artifact", "")
    dest_dir_rel = step_cfg.get("dest_dir", "")
    filename_strategy = step_cfg.get("filename_strategy", "")
    result_key = step_cfg.get("result_meta_key", dest_artifact_key)
    meta_rel = context.get(f"{result_key}_METAJSON", "")

    print(f"[copy_artifact] source={source_key!r} dest_artifact={dest_artifact_key!r}", flush=True)

    if not source_key or not dest_artifact_key or not dest_dir_rel:
        remark = "Step config missing required keys: source, dest_artifact, dest_dir"
        if meta_rel:
            write_meta_sidecar(meta_rel, project_root=project_root, status="REJECTED", remark=remark, artifacts={})
        return ActionResult(status="REJECTED", remark=remark, artifacts={})

    source_rel = context.get(source_key, "")
    if not source_rel:
        remark = f"{source_key} not found in context"
        if meta_rel:
            write_meta_sidecar(meta_rel, project_root=project_root, status="REJECTED", remark=remark, artifacts={})
        return ActionResult(status="REJECTED", remark=remark, artifacts={})

    source_path = project_root / source_rel
    if not source_path.exists():
        remark = f"{source_key} file not found: {source_rel}"
        if meta_rel:
            write_meta_sidecar(meta_rel, project_root=project_root, status="REJECTED", remark=remark, artifacts={})
        return ActionResult(status="REJECTED", remark=remark, artifacts={})

    content = source_path.read_text(encoding="utf-8")

    # Derive destination filename
    if filename_strategy == "init_id_slug":
        init_id = _extract_init_id(content)
        if not init_id:
            remark = "Could not extract Initiative ID from source file"
            if meta_rel:
                write_meta_sidecar(meta_rel, project_root=project_root, status="REJECTED", remark=remark, artifacts={})
            return ActionResult(status="REJECTED", remark=remark, artifacts={})
        title = _extract_title(content)
        if not title:
            remark = "Could not extract title (# Heading) from source file"
            if meta_rel:
                write_meta_sidecar(meta_rel, project_root=project_root, status="REJECTED", remark=remark, artifacts={})
            return ActionResult(status="REJECTED", remark=remark, artifacts={})
        filename = f"{init_id}_{_to_slug(title)}.md"
    else:
        filename = source_path.name

    dest_dir = project_root / dest_dir_rel
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename

    dest_rel = f"{dest_dir_rel}/{filename}"
    if filename_strategy == "init_id_slug":
        content = _upsert_metadata_field(content, "Document File", dest_rel)
        content = _upsert_metadata_field(content, "Source Pre-Init File", source_rel)
    dest_path.write_text(content, encoding="utf-8")

    print(f"[copy_artifact] copied {source_rel} → {dest_rel}", flush=True)

    if meta_rel:
        write_meta_sidecar(meta_rel, project_root=project_root, status="APPROVED", remark=f"Copied to {dest_rel}", artifacts={dest_artifact_key: dest_rel})
    return ActionResult(status="APPROVED", remark=f"Copied to {dest_rel}", artifacts={dest_artifact_key: dest_rel})
