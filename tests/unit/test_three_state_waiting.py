"""Tests for the three-state human waiting status split.

Verifies that WAITING_FOR_HUMAN_APPROVAL, WAITING_FOR_HUMAN_INTERVENTION,
and WAITING_FOR_HUMAN_MAXRETRIED are correctly set and handled.
"""
from __future__ import annotations

import pytest

from agent_runner_v2.job_state import (
    NON_TERMINAL_JOB_STATUSES,
    get_job_status,
    resume_step,
    retry_step,
    set_job_status,
)
from agent_runner_v2.recovery_runtime import handle_recovery_budget_exceeded


# ---------------------------------------------------------------------------
# Status constants
# ---------------------------------------------------------------------------

def test_maxretried_in_non_terminal_statuses() -> None:
    assert "WAITING_FOR_HUMAN_MAXRETRIED" in NON_TERMINAL_JOB_STATUSES
    assert "WAITING_FOR_HUMAN_INTERVENTION" in NON_TERMINAL_JOB_STATUSES
    assert "WAITING_FOR_HUMAN_APPROVAL" in NON_TERMINAL_JOB_STATUSES


# ---------------------------------------------------------------------------
# resume_step
# ---------------------------------------------------------------------------

def _make_group_cfg(steps: list[str] | None = None) -> dict:
    """Build a minimal group_cfg for testing."""
    steps = steps or ["step_a", "step_b", "step_c"]
    return {
        "steps": steps,
        "step_configs": {s: {"produces": []} for s in steps},
    }


def _make_state(status: str, step: str = "step_b") -> dict:
    """Build a minimal job state for testing."""
    return {
        "job_id": "TEST-001",
        "template_group": "test_wf",
        "job_status": status,
        "status": status,
        "current_step": step,
        "completed_steps": ["step_a"],
        "pending_intervention_for": step,
        "pending_human_approval_for": None,
        "reject_counts": {"step_b": 2},
        "loop_context": {"active": True, "loop_step": "step_b"},
        "replan_context": {"active": False},
        "last_failure_class": "HUMAN_RETRY_REQUIRED",
        "last_failure_code": "REFINEMENT_EXHAUSTED",
        "last_failure_reason": "loop exhausted",
        "last_failure_source": "runner",
        "failure_history": [],
        "human_approvals": {},
        "review_state": {
            "review_decision": "REJECTED",
            "human_decision": "NOT_REQUIRED",
            "final_decision": "REJECTED",
            "final_decision_source": "MODEL",
        },
        "artifacts": {},
    }


def test_resume_step_from_intervention_advances_to_next_step() -> None:
    state = _make_state("WAITING_FOR_HUMAN_INTERVENTION")
    group_cfg = _make_group_cfg()

    result = resume_step(
        group_name="test_wf",
        group_cfg=group_cfg,
        state=state,
        step="step_b",
    )

    assert get_job_status(result) == "IN_PROGRESS"
    assert result["current_step"] == "step_c"
    assert "step_b" in result["completed_steps"]
    assert result["pending_intervention_for"] is None
    assert result["loop_context"]["active"] is False
    assert result["last_failure_class"] is None
    assert result["human_approvals"]["step_b"]["resume"] is True


def test_resume_step_from_maxretried_advances_to_next_step() -> None:
    state = _make_state("WAITING_FOR_HUMAN_MAXRETRIED")
    group_cfg = _make_group_cfg()

    result = resume_step(
        group_name="test_wf",
        group_cfg=group_cfg,
        state=state,
        step="step_b",
    )

    assert get_job_status(result) == "IN_PROGRESS"
    assert result["current_step"] == "step_c"
    assert "step_b" in result["completed_steps"]


def test_resume_step_rejects_wrong_status() -> None:
    state = _make_state("IN_PROGRESS")
    group_cfg = _make_group_cfg()

    with pytest.raises(ValueError, match="cannot be resumed"):
        resume_step(
            group_name="test_wf",
            group_cfg=group_cfg,
            state=state,
            step="step_b",
        )


def test_resume_step_completes_job_when_no_next_step() -> None:
    state = _make_state("WAITING_FOR_HUMAN_INTERVENTION", step="step_c")
    state["completed_steps"] = ["step_a", "step_b"]
    group_cfg = _make_group_cfg()

    result = resume_step(
        group_name="test_wf",
        group_cfg=group_cfg,
        state=state,
        step="step_c",
    )

    assert get_job_status(result) == "COMPLETED"
    assert result["current_step"] is None


# ---------------------------------------------------------------------------
# retry_step
# ---------------------------------------------------------------------------

def test_retry_step_from_intervention_resets_counts() -> None:
    state = _make_state("WAITING_FOR_HUMAN_INTERVENTION")
    state["reject_counts"] = {"step_b": 3}
    state["human_retry_count_by_step"] = {"step_b": 2}
    group_cfg = _make_group_cfg()

    result = retry_step(
        group_name="test_wf",
        group_cfg=group_cfg,
        state=state,
        step="step_b",
    )

    assert get_job_status(result) == "IN_PROGRESS"
    assert result["current_step"] == "step_b"
    assert result["reject_counts"]["step_b"] == 0
    assert result["human_retry_count_by_step"]["step_b"] == 0
    assert result["pending_intervention_for"] is None
    assert result["loop_context"]["active"] is False
    assert result["replan_context"]["active"] is False
    assert result["last_failure_class"] is None
    # step_b should NOT be in completed_steps (it's being retried, not completed)
    assert "step_b" not in result["completed_steps"]


def test_retry_step_from_maxretried_resets_counts() -> None:
    state = _make_state("WAITING_FOR_HUMAN_MAXRETRIED")
    state["reject_counts"] = {"step_b": 2}
    group_cfg = _make_group_cfg()

    result = retry_step(
        group_name="test_wf",
        group_cfg=group_cfg,
        state=state,
        step="step_b",
    )

    assert get_job_status(result) == "IN_PROGRESS"
    assert result["current_step"] == "step_b"
    assert result["reject_counts"]["step_b"] == 0


def test_retry_step_rejects_wrong_status() -> None:
    state = _make_state("WAITING_FOR_HUMAN_APPROVAL")
    group_cfg = _make_group_cfg()

    with pytest.raises(ValueError, match="cannot be retried"):
        retry_step(
            group_name="test_wf",
            group_cfg=group_cfg,
            state=state,
            step="step_b",
        )


# ---------------------------------------------------------------------------
# handle_recovery_budget_exceeded → MAXRETRIED
# ---------------------------------------------------------------------------

def test_budget_exceeded_sets_maxretried_status() -> None:
    statuses: list[str] = []
    state: dict = {}
    reject_counts: dict = {}

    updated, exit_code = handle_recovery_budget_exceeded(
        state=state,
        step="review_docs",
        reject_counts=reject_counts,
        set_last_failure=lambda **kwargs: None,
        append_failure_history=lambda **kwargs: None,
        set_job_status=lambda s, v: (statuses.append(v), s.__setitem__("job_status", v), s.__setitem__("status", v)),
    )

    assert exit_code == 1
    assert statuses == ["WAITING_FOR_HUMAN_MAXRETRIED"]
    assert updated["pending_intervention_for"] == "review_docs"
