from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from agent_runner_v2.artifact_keys import ARTIFACT_KEY_PLANNING_FOLDER, ARTIFACT_KEY_RAW_REQUEST
from agent_runner_v2.constants import ARTIFACT_PATH_RAW_REQUEST, PLANNING_BASE


def prepare_request(*, context, state, step_cfg, step, project_root):
    """Allocate Planning folder and copy request file."""
    from agent_runner_v2.action_result import ActionResult

    raw_request = context.get(ARTIFACT_KEY_RAW_REQUEST, "")
    if not raw_request:
        return ActionResult(status="REJECTED", remark="No RAW_REQUEST_FILE provided")

    src = Path(raw_request)
    if not src.is_absolute():
        src = project_root / src
    if not src.exists():
        return ActionResult(status="REJECTED", remark=f"Request file not found: {src}")

    now = datetime.now()
    date_str = now.strftime("%Y%m%d")

    # Find next sequence number for today — atomic claim
    planning_base = project_root / PLANNING_BASE
    planning_base.mkdir(parents=True, exist_ok=True)
    seq = 1
    while True:
        slug = _derive_slug(src.stem)
        folder_name = f"{date_str}-{seq:02d}_{slug}"
        folder_path = planning_base / folder_name
        try:
            folder_path.mkdir(parents=True, exist_ok=False)
            break
        except FileExistsError:
            seq += 1

    planning_folder_rel = f"{PLANNING_BASE}/{folder_name}"

    # Copy request file — destination built from layered path constant
    dest = project_root / ARTIFACT_PATH_RAW_REQUEST(planning_folder_rel)
    shutil.copy2(str(src), str(dest))

    # Initialize revision counter in job state
    state["plan_revision"] = 1
    state.setdefault("human_reject_counts", {})

    return ActionResult(
        status="APPROVED",
        remark=f"Created Planning folder: {planning_folder_rel}",
        artifacts={
            ARTIFACT_KEY_PLANNING_FOLDER: planning_folder_rel,
            ARTIFACT_KEY_RAW_REQUEST: ARTIFACT_PATH_RAW_REQUEST(planning_folder_rel),
        },
    )


def promote_plan(*, context, state, step_cfg, step, project_root):
    """Promote the approved plan (no-op passthrough)."""
    from agent_runner_v2.action_result import ActionResult

    plan_path = context.get("QWEN_PLAN_FILE", "")
    return ActionResult(
        status="APPROVED",
        remark=f"Plan promoted: {plan_path}",
        artifacts={"QWEN_PLAN_FILE": plan_path},
    )


def step_completion(*, context, state, step_cfg, step, project_root):
    """Final cleanup — reset human rejection counters."""
    from agent_runner_v2.action_result import ActionResult

    state.pop("human_reject_counts", None)
    return ActionResult(status="APPROVED", remark="Workflow complete")


def _derive_slug(stem: str) -> str:
    """Derive a folder slug from the request file stem."""
    slug = stem.strip().replace(" ", "_")
    slug = "".join(c for c in slug if c.isalnum() or c in "_-")
    return slug[:60] or "Plan"
