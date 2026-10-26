"""No-op action for skipping steps without failing.

This action immediately returns APPROVED without performing any work.
Used by Generator implementation to skip AGB infrastructure steps.
"""
from __future__ import annotations

from pathlib import Path

from ..action_result import ActionResult


def noop(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    """No-op action that approves immediately.

    Returns APPROVED status with an empty artifacts dict.
    Used to skip infrastructure steps in Generator workflows.
    """
    step_name = step_cfg.get("name", "unknown")
    return ActionResult(
        status="APPROVED",
        remark=f"Step '{step_name}' skipped via noop action",
        artifacts={},
    )
