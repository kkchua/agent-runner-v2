#!/usr/bin/env python3
from __future__ import annotations

"""
actions/scan_repo_codebase.py - Deterministic repository scan snapshot for master-doc bootstrap.
"""

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from ..action_result import ActionResult
from ..codebase_docs import build_snapshot
from ..constants import FOLDER_KEY_CODEBASE_CHANGES
from ..runtime_context import resolve_step_meta_rel, write_meta_sidecar


def _json_default(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def scan_repo_codebase(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    mode = str(step_cfg.get("mode") or "bootstrap")
    job_id = str(state.get("job_id") or "00DOC")
    step = str(state.get("current_step") or "scan_repo_codebase")
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="CODEBASE_SCAN_SNAPSHOT_METAJSON",
        default_step=step,
    )

    snapshot = build_snapshot(
        project_root,
        mode=mode,
        job_id=job_id,
        step=step,
        workflow_name=str(state.get("template_group") or mode),
    )
    snapshot_path = project_root / FOLDER_KEY_CODEBASE_CHANGES / f"{job_id}-{mode}-snapshot.json"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False, default=_json_default) + "\n",
        encoding="utf-8",
    )

    artifact_rel = snapshot_path.relative_to(project_root).as_posix()
    artifacts = {"CODEBASE_SCAN_SNAPSHOT": artifact_rel}
    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark=f"Repository scan {mode} completed.",
            artifacts=artifacts,
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Repository scan {mode} completed.",
        artifacts=artifacts,
    )
