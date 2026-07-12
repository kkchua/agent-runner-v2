from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def mark_review_started(
    *,
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
    coder_used: str,
    default_review_state: Callable[[], dict[str, Any]],
) -> None:
    on_reject_refine = step_cfg.get("on_reject_refine") or {}
    artifact_key = on_reject_refine.get("artifact")
    if not artifact_key:
        produces = step_cfg.get("produces", [])
        if step_cfg.get("requires_human_approval_after") and produces:
            artifact_key = str(produces[0])
    if not artifact_key:
        return

    review_state = state.setdefault("review_state", default_review_state())
    review_state["reviewer_step"] = step
    review_state["coder_used"] = coder_used
    review_state["review_decision"] = "PENDING"
    review_state["review_decided_at"] = None
    review_state["human_decision"] = "PENDING"
    review_state["human_decided_at"] = None
    review_state["final_decision"] = None
    review_state["final_decision_source"] = None

    prior = sum(1 for entry in state.get("retry_history", []) if entry.get("step") == step)
    review_state["review_iteration"] = prior + 1


def mark_review_waiting_for_human(
    *,
    state: dict[str, Any],
    step: str,
    coder_used: str,
    default_review_state: Callable[[], dict[str, Any]],
    now_iso: Callable[[], str],
    set_job_status: Callable[[dict[str, Any], str], None],
) -> tuple[dict[str, Any], int]:
    state["model_approved_steps"] = list(dict.fromkeys(
        state.setdefault("model_approved_steps", []) + [step]
    ))
    review_state = state.setdefault("review_state", default_review_state())
    review_state["reviewer_step"] = step
    review_state["coder_used"] = coder_used
    review_state["review_decision"] = "APPROVED"
    review_state["review_decided_at"] = now_iso()
    review_state["human_decision"] = "PENDING"
    set_job_status(state, "WAITING_FOR_HUMAN_APPROVAL")
    state["pending_human_approval_for"] = step
    state["current_step"] = step
    return state, 0


def mark_task_exec_success(
    *,
    state: dict[str, Any],
    step: str,
    set_job_status: Callable[[dict[str, Any], str], None],
) -> tuple[dict[str, Any], int]:
    state["completed_steps"] = list(dict.fromkeys(state.setdefault("completed_steps", []) + [step]))
    set_job_status(state, "IN_PROGRESS")
    state["current_step"] = "review_task"
    return state, 0


def advance_to_next_step(
    *,
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any] | None,
    set_job_status: Callable[[dict[str, Any], str], None],
    get_next_step_skipping_refine_replan: Callable[[dict[str, Any], list[str]], str | None],
    on_completed: Callable[[dict[str, Any]], None],
) -> tuple[dict[str, Any], int]:
    state["completed_steps"] = list(dict.fromkeys(state.setdefault("completed_steps", []) + [step]))
    onsuccess = (step_cfg or {}).get("onsuccess") if step_cfg else None
    if onsuccess:
        next_step = onsuccess
    else:
        next_step = get_next_step_skipping_refine_replan(group_cfg, list(state.get("completed_steps", [])))
    if next_step is None:
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
        on_completed(state)
    else:
        set_job_status(state, "IN_PROGRESS")
        state["current_step"] = next_step
    return state, 0


def complete_recovery_step(
    *,
    state: dict[str, Any],
    step: str,
    target_key: str,
    artifacts: dict[str, Any],
    pre_checksum: str | None,
    no_op_failure_code: str,
    no_op_failure_reason: str,
    history_key: str,
    history_result_field: str,
    history_time_field: str,
    next_step: str,
    project_root: Path,
    now_iso: Callable[[], str],
    set_last_failure: Callable[..., None],
    append_failure_history: Callable[..., None],
    set_job_status: Callable[[dict[str, Any], str], None],
    checksum_file: Callable[[Path], str],
    reset_replan_context: bool,
) -> tuple[dict[str, Any], int]:
    if not artifacts.get(target_key):
        set_last_failure(
            state=state,
            failure_class="HUMAN_RETRY_REQUIRED",
            failure_code="MISSING_TARGET_ARTIFACT",
            failure_reason=f"{step} returned APPROVED but produced no {target_key}",
            failure_source="runner",
            step=step,
        )
        append_failure_history(
            state=state,
            step=step,
            failure_class="HUMAN_RETRY_REQUIRED",
            failure_code="MISSING_TARGET_ARTIFACT",
            failure_source="runner",
        )
        state.setdefault("reject_counts", {})[step] = int(state.get("reject_counts", {}).get(step, 0)) + 1
        set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
        state["current_step"] = step
        return state, 1

    if pre_checksum:
        target_path = project_root / str(artifacts[target_key])
        post_checksum = checksum_file(target_path) if target_path.exists() else None
        if post_checksum and post_checksum == pre_checksum:
            set_last_failure(
                state=state,
                failure_class="HUMAN_RETRY_REQUIRED",
                failure_code=no_op_failure_code,
                failure_reason=no_op_failure_reason,
                failure_source="runner",
                step=step,
            )
            append_failure_history(
                state=state,
                step=step,
                failure_class="HUMAN_RETRY_REQUIRED",
                failure_code=no_op_failure_code,
                failure_source="runner",
            )
            state.setdefault("reject_counts", {})[step] = int(state.get("reject_counts", {}).get(step, 0)) + 1
            set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
            state["current_step"] = step
            return state, 1

    history = state.get(history_key, [])
    if history:
        history[-1][history_result_field] = "APPROVED"
        history[-1][history_time_field] = now_iso()

    state["loop_context"] = {
        "active": False,
        "loop_step": None,
        "refine_step": None,
        "loop_target_artifact": None,
        "loop_source_review": None,
        "loop_iteration": 0,
        "pre_refine_checksum": None,
    }
    if reset_replan_context:
        state["replan_context"] = {
            "active": False,
            "source_review_step": None,
            "replan_step": None,
            "target_artifact": None,
            "source_review_file": None,
            "replan_attempt": 0,
            "pre_replan_checksum": None,
            "trigger_reason": None,
            "blocking_issues": [],
            "previous_blocking_issue_count": 0,
            "previous_blocking_issue_severity": 0,
        }

    state["current_step"] = next_step
    set_job_status(state, "IN_PROGRESS")
    return state, 0
