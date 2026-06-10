#!/usr/bin/env python3
"""
actions/promote_artifact.py — Update artifact Status field in-place.

Step config:
    "promotes": "PLAN_FILE"                          # single artifact key
    "promotes": ["TASK_GRAPH_FILE", "PLAN_FILE"]     # multiple artifact keys
    "target_status": "Approved"                      # default; use "Completed" for task completion
    "result_meta_key": "PLAN_FILE"                   # which artifact's metajson path to use
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path

from ..action_result import ActionResult

logger = logging.getLogger(__name__)

# Matches any current status value (table or KV format)
_TABLE_STATUS_RE = re.compile(r"(\|\s*Status\s*\|\s*)`?[^`|\n]+`?(\s*\|)", re.IGNORECASE)
_KV_STATUS_RE = re.compile(
    r"^(\s*(?:[-*]\s*)?(?:\*\*)?Status(?:\*\*)?(?::\s*|\*\*:\s*))\S[^\n]*$",
    re.IGNORECASE | re.MULTILINE,
)


def _set_status(content: str, target_status: str) -> str:
    content = _TABLE_STATUS_RE.sub(rf"\1`{target_status}`\2", content)
    content = _KV_STATUS_RE.sub(rf"\g<1>{target_status}", content)
    return content


def _write_meta(meta_rel: str, project_root: Path, status: str, remark: str, artifacts: dict) -> None:
    if not meta_rel:
        print("[promote_artifact] WARNING: meta.json path not in context — skipping", flush=True)
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
    print(f"[promote_artifact] wrote meta.json → {meta_rel}", flush=True)


def promote_artifact(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    promotes = step_cfg.get("promotes", [])
    if isinstance(promotes, str):
        promotes = [promotes]

    target_status = step_cfg.get("target_status", "Approved")
    result_key = step_cfg.get("result_meta_key", promotes[0] if promotes else "")
    meta_rel = context.get(f"{result_key}_METAJSON", "")

    if not promotes:
        remark = "No 'promotes' key in step config"
        _write_meta(meta_rel, project_root, "REJECTED", remark, {})
        return ActionResult(status="REJECTED", remark=remark, artifacts={})

    promoted: dict[str, str] = {}
    for artifact_key in promotes:
        rel = context.get(artifact_key, "")
        if not rel:
            print(f"[promote_artifact] {artifact_key} not in context — skipping", flush=True)
            continue
        path = project_root / rel
        if not path.exists():
            print(f"[promote_artifact] {artifact_key} file not found: {rel} — skipping", flush=True)
            continue
        content = path.read_text(encoding="utf-8")
        updated = _set_status(content, target_status)
        path.write_text(updated, encoding="utf-8")
        promoted[artifact_key] = rel
        print(f"[promote_artifact] {artifact_key} Status → {target_status}: {rel}", flush=True)

    if not promoted:
        remark = f"No artifacts promoted (keys: {promotes})"
        _write_meta(meta_rel, project_root, "REJECTED", remark, {})
        return ActionResult(status="REJECTED", remark=remark, artifacts={})

    remark = f"Status set to {target_status}: {', '.join(promoted.keys())}"
    _write_meta(meta_rel, project_root, "APPROVED", remark, promoted)
    return ActionResult(status="APPROVED", remark=remark, artifacts=promoted)
