#!/usr/bin/env python3
from __future__ import annotations

"""
Terminal step that finalizes a completed workflow.

Marks the job as COMPLETED in state. Workflow completion notification is sent
by the normal advancement path so it fires exactly once.
"""

from pathlib import Path

from ..action_result import ActionResult
from ..job_state import set_job_status


def step_completion(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    set_job_status(state, "COMPLETED")

    return ActionResult(
        status="APPROVED",
        remark="Workflow completed successfully.",
        artifacts={},
    )
