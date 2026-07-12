from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def handle_recovery_budget_exceeded(
    *,
    state: dict[str, Any],
    step: str,
    reject_counts: dict[str, Any],
    set_last_failure: Callable[..., None],
    append_failure_history: Callable[..., None],
    set_job_status: Callable[[dict[str, Any], str], None],
) -> tuple[dict[str, Any], int]:
    reject_counts[step] = int(reject_counts.get(step, 0)) + 1
    set_last_failure(
        state=state,
        failure_class="HUMAN_RETRY_REQUIRED",
        failure_code="PLANNING_ATTEMPT_BUDGET_EXCEEDED",
        failure_reason="Planning recovery attempt budget exceeded",
        failure_source="runner",
        step=step,
    )
    append_failure_history(
        state=state,
        step=step,
        failure_class="HUMAN_RETRY_REQUIRED",
        failure_code="PLANNING_ATTEMPT_BUDGET_EXCEEDED",
        failure_source="runner",
    )
    set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
    state["current_step"] = step
    return state, 1


def activate_refine_loop(
    *,
    state: dict[str, Any],
    step: str,
    refine_step: str,
    target_artifact: str,
    review_file: str | None,
    iteration: int,
    now_iso: Callable[[], str],
    clear_last_failure: Callable[[dict[str, Any]], None],
    set_job_status: Callable[[dict[str, Any], str], None],
) -> tuple[dict[str, Any], int]:
    state["loop_context"] = {
        "active": True,
        "loop_step": step,
        "refine_step": refine_step,
        "loop_target_artifact": target_artifact,
        "loop_source_review": review_file,
        "loop_iteration": iteration,
        "pre_refine_checksum": None,
    }
    timestamp = now_iso()
    state.setdefault("loop_history", []).append(
        {
            "iteration": iteration,
            "loop_step": step,
            "refine_step": refine_step,
            "review_result": "REJECTED",
            "review_file": review_file,
            "review_at": timestamp,
            "refine_result": None,
            "refine_at": None,
            "started_at": timestamp,
            "resolved_at": None,
        }
    )
    clear_last_failure(state)
    state["current_step"] = refine_step
    set_job_status(state, "IN_PROGRESS")
    return state, 0


def activate_replan(
    *,
    state: dict[str, Any],
    step: str,
    replan_step: str,
    target_artifact: str,
    review_file: str | None,
    replan_attempt: int,
    trigger_reason: str,
    artifacts: dict[str, Any],
    project_root: Path,
    checksum_file: Callable[[Path], str],
    now_iso: Callable[[], str],
    clear_last_failure: Callable[[dict[str, Any]], None],
    set_job_status: Callable[[dict[str, Any], str], None],
) -> tuple[dict[str, Any], int]:
    state["replan_context"] = {
        "active": True,
        "source_review_step": step,
        "replan_step": replan_step,
        "target_artifact": target_artifact,
        "source_review_file": review_file,
        "replan_attempt": replan_attempt,
        "pre_replan_checksum": None,
        "trigger_reason": trigger_reason,
        "blocking_issues": [],
        "previous_blocking_issue_count": 0,
        "previous_blocking_issue_severity": 0,
    }
    target_path_value = artifacts.get(target_artifact)
    if target_path_value:
        target_path = project_root / str(target_path_value)
        if target_path.exists():
            state["replan_context"]["pre_replan_checksum"] = checksum_file(target_path)
    state.setdefault("replan_history", []).append(
        {
            "source_review_step": step,
            "trigger_reason": trigger_reason,
            "source_review_file": review_file,
            "blocking_issues": [],
            "replan_step": replan_step,
            "replan_attempt": replan_attempt,
            "triggered_at": now_iso(),
            "replan_result": None,
            "review_result": None,
            "resolved_at": None,
        }
    )
    state["loop_context"] = {
        "active": False,
        "loop_step": None,
        "refine_step": None,
        "loop_target_artifact": None,
        "loop_source_review": None,
        "loop_iteration": 0,
        "pre_refine_checksum": None,
    }
    clear_last_failure(state)
    state["current_step"] = replan_step
    set_job_status(state, "IN_PROGRESS")
    return state, 0
