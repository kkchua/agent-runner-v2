#!/usr/bin/env python3
"""
actions/promote_init.py — Promote a reviewed PRE_INIT_FILE to an official INIT_FILE.

Reads the PRE_INIT_FILE, extracts the Initiative ID and title, derives a
kebab-case filename, and writes the promoted copy to docs/delivery/01_initiatives/
with Status changed from draft → Approved.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path

from ..action_result import ActionResult

logger = logging.getLogger(__name__)

# Matches table row: | Initiative ID | `INIT-20260607-01` | or plain text: Initiative ID: INIT-20260607-01
_INIT_ID_RE = re.compile(r"Initiative\s+ID[^`\n]*`?(INIT-[\w-]+)`?", re.IGNORECASE)
# Matches table row: | Status | `draft` | or plain text: Status: draft
_STATUS_RE = re.compile(r"(\|\s*Status\s*\|\s*)`draft`", re.IGNORECASE)


def _extract_init_id(text: str) -> str | None:
    m = _INIT_ID_RE.search(text)
    return m.group(1).strip() if m else None


def _extract_title(text: str) -> str | None:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            title = line[2:].strip()
            # Strip "Initiative: INIT-YYYYMMDD-NN — " prefix if present
            title = re.sub(r"^Initiative\s*:\s*INIT-[\w-]+\s*[—\-]+\s*", "", title, flags=re.IGNORECASE).strip()
            return title or None
    return None


def _to_slug(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^\w\s-]", "", title)
    title = re.sub(r"[\s_]+", "-", title)
    title = title.strip("-")
    return title


def _write_meta(meta_rel: str, project_root: Path, status: str, remark: str, artifacts: dict) -> None:
    if not meta_rel:
        print("[promote_init] WARNING: INIT_FILE_METAJSON not in context — meta.json not written", flush=True)
        return
    meta_path = project_root / meta_rel
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(
        json.dumps({
            "schema_version": "v2",
            "coder_result": {
                "status": status,
                "remark": remark,
                "artifacts": artifacts,
                "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            },
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[promote_init] wrote meta.json → {meta_rel}", flush=True)


def promote_init(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    meta_rel = context.get("INIT_FILE_METAJSON", "")
    print(f"[promote_init] starting. INIT_FILE_METAJSON={meta_rel!r}", flush=True)
    print(f"[promote_init] PRE_INIT_FILE={context.get('PRE_INIT_FILE','')!r}", flush=True)

    pre_init_rel = context.get("PRE_INIT_FILE", "")
    if not pre_init_rel:
        remark = "PRE_INIT_FILE not found in context"
        _write_meta(meta_rel, project_root, "REJECTED", remark, {})
        return ActionResult(status="REJECTED", remark=remark, artifacts={})

    pre_init_path = project_root / pre_init_rel
    if not pre_init_path.exists():
        remark = f"PRE_INIT_FILE does not exist: {pre_init_rel}"
        _write_meta(meta_rel, project_root, "REJECTED", remark, {})
        return ActionResult(status="REJECTED", remark=remark, artifacts={})

    content = pre_init_path.read_text(encoding="utf-8")
    print(f"[promote_init] read PRE_INIT_FILE ({len(content)} bytes)", flush=True)

    init_id = _extract_init_id(content)
    print(f"[promote_init] extracted init_id={init_id!r}", flush=True)
    if not init_id:
        remark = "Could not extract Initiative ID from PRE_INIT_FILE"
        _write_meta(meta_rel, project_root, "REJECTED", remark, {})
        return ActionResult(status="REJECTED", remark=remark, artifacts={})

    title = _extract_title(content)
    print(f"[promote_init] extracted title={title!r}", flush=True)
    if not title:
        remark = "Could not extract title (# Heading) from PRE_INIT_FILE"
        _write_meta(meta_rel, project_root, "REJECTED", remark, {})
        return ActionResult(status="REJECTED", remark=remark, artifacts={})

    slug = _to_slug(title)
    filename = f"{init_id}_{slug}.md"
    dest_dir = project_root / "docs" / "delivery" / "01_initiatives"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename

    promoted_content = _STATUS_RE.sub(r"\1`Approved`", content, count=1)
    dest_path.write_text(promoted_content, encoding="utf-8")
    init_file_rel = f"docs/delivery/01_initiatives/{filename}"
    print(f"[promote_init] wrote INIT_FILE → {init_file_rel}", flush=True)

    _write_meta(meta_rel, project_root, "APPROVED", f"Promoted to {init_file_rel}", {"INIT_FILE": init_file_rel})

    return ActionResult(
        status="APPROVED",
        remark=f"Promoted to {init_file_rel}",
        artifacts={"INIT_FILE": init_file_rel},
    )
