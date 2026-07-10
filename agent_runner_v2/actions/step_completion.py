#!/usr/bin/env python3
from __future__ import annotations

"""
actions/step_completion.py — Terminal step that finalizes a completed workflow.

Sends Pushover notification and marks the job as COMPLETED in state.
The runner handles meta.json writing automatically via run_action().
"""

from pathlib import Path

from ..action_result import ActionResult
from ..job_state import set_job_status
from ..notification_manager import send_workflow_notification


def step_completion(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    set_job_status(state, "COMPLETED")
    send_workflow_notification("COMPLETED", dict(state))

    return ActionResult(
        status="APPROVED",
        remark="Workflow completed successfully.",
        artifacts={},
    )
