from __future__ import annotations

from pathlib import Path

from agent_runner_v2.actions.step_completion import step_completion


def test_step_completion_marks_job_complete_without_sending_notification(monkeypatch) -> None:
    notifications: list[tuple[str, dict]] = []

    monkeypatch.setattr(
        "agent_runner_v2.notification_manager.send_workflow_notification",
        lambda status, state: notifications.append((status, state)),
    )

    state = {"job_status": "IN_PROGRESS", "status": "IN_PROGRESS"}

    result = step_completion(
        context={},
        state=state,
        step_cfg={},
        project_root=Path("."),
    )

    assert result.status == "APPROVED"
    assert state["job_status"] == "COMPLETED"
    assert state["status"] == "COMPLETED"
    assert notifications == []
