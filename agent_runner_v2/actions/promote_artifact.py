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

import logging
import re
from pathlib import Path

from ..action_result import ActionResult
from ..runtime_context import artifact_rel_to_meta_rel, write_meta_sidecar

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
        if meta_rel:
            write_meta_sidecar(meta_rel, project_root=project_root, status="REJECTED", remark=remark, artifacts={})
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
        if meta_rel:
            write_meta_sidecar(meta_rel, project_root=project_root, status="REJECTED", remark=remark, artifacts={})
        return ActionResult(status="REJECTED", remark=remark, artifacts={})

    remark = f"Status set to {target_status}: {', '.join(promoted.keys())}"
    if meta_rel:
        write_meta_sidecar(meta_rel, project_root=project_root, status="APPROVED", remark=remark, artifacts=promoted)
    for artifact_key, artifact_rel in promoted.items():
        artifact_meta_rel = artifact_rel_to_meta_rel(artifact_rel)
        if artifact_meta_rel != meta_rel:
            write_meta_sidecar(artifact_meta_rel, project_root=project_root, status="APPROVED", remark=remark, artifacts={artifact_key: artifact_rel})
    return ActionResult(status="APPROVED", remark=remark, artifacts=promoted)
