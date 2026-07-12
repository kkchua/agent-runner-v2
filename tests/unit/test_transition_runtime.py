from __future__ import annotations

from agent_runner_v2.transition_runtime import (
    advance_to_next_step,
    mark_review_started,
    mark_review_waiting_for_human,
    mark_task_exec_success,
)


def test_mark_review_started_sets_pending_review_state() -> None:
    state: dict[str, object] = {
        "retry_history": [
            {"step": "review_docs"},
            {"step": "other_step"},
        ],
    }

    mark_review_started(
        state=state,
        step="review_docs",
        step_cfg={
            "on_reject_refine": {"artifact": "SYSTEM_DOCS_INDEX"},
            "produces": ["SYSTEM_DOCS_INDEX"],
        },
        coder_used="qwen-reviewer",
        default_review_state=lambda: {
            "reviewer_step": None,
            "coder_used": None,
            "review_decision": "APPROVED",
            "review_decided_at": "stale",
            "human_decision": "APPROVED",
            "human_decided_at": "stale",
            "final_decision": "APPROVED",
            "final_decision_source": "MODEL",
            "review_iteration": 0,
        },
    )

    review_state = state["review_state"]
    assert review_state["reviewer_step"] == "review_docs"
    assert review_state["coder_used"] == "qwen-reviewer"
    assert review_state["review_decision"] == "PENDING"
    assert review_state["review_decided_at"] is None
    assert review_state["human_decision"] == "PENDING"
    assert review_state["human_decided_at"] is None
    assert review_state["final_decision"] is None
    assert review_state["final_decision_source"] is None
    assert review_state["review_iteration"] == 2


def test_mark_review_waiting_for_human_sets_review_state() -> None:
    statuses: list[str] = []
    state: dict[str, object] = {}

    updated, exit_code = mark_review_waiting_for_human(
        state=state,
        step="review_docs",
        coder_used="qwen-reviewer",
        default_review_state=lambda: {
            "reviewer_step": None,
            "coder_used": None,
            "review_decision": "PENDING",
            "review_decided_at": None,
            "human_decision": "PENDING",
        },
        now_iso=lambda: "2026-07-12T10:00:00",
        set_job_status=lambda s, v: (statuses.append(v), s.__setitem__("job_status", v), s.__setitem__("status", v)),
    )

    assert exit_code == 0
    assert updated["current_step"] == "review_docs"
    assert updated["pending_human_approval_for"] == "review_docs"
    assert updated["model_approved_steps"] == ["review_docs"]
    assert updated["review_state"]["review_decision"] == "APPROVED"
    assert statuses == ["WAITING_FOR_HUMAN_APPROVAL"]


def test_mark_task_exec_success_routes_to_review_task() -> None:
    statuses: list[str] = []
    state = {"completed_steps": []}

    updated, exit_code = mark_task_exec_success(
        state=state,
        step="task",
        set_job_status=lambda s, v: (statuses.append(v), s.__setitem__("job_status", v), s.__setitem__("status", v)),
    )

    assert exit_code == 0
    assert updated["current_step"] == "review_task"
    assert updated["completed_steps"] == ["task"]
    assert statuses == ["IN_PROGRESS"]


def test_advance_to_next_step_completes_when_no_next_step() -> None:
    statuses: list[str] = []
    completed_notifications: list[str | None] = []
    state = {"completed_steps": []}

    updated, exit_code = advance_to_next_step(
        group_cfg={"steps": ["final"], "step_configs": {"final": {}}},
        state=state,
        step="final",
        step_cfg={},
        set_job_status=lambda s, v: (statuses.append(v), s.__setitem__("job_status", v), s.__setitem__("status", v)),
        get_next_step_skipping_refine_replan=lambda group_cfg, completed_steps: None,
        on_completed=lambda current_state: completed_notifications.append(current_state.get("current_step")),
    )

    assert exit_code == 0
    assert updated["current_step"] is None
    assert updated["completed_steps"] == ["final"]
    assert statuses == ["COMPLETED"]
    assert completed_notifications == [None]
