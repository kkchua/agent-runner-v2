#!/usr/bin/env python3
"""
workflow_router.py — Post-step routing for agent_runner_v2.

Replaces the monolithic update_job_state_after_result() from v1.

Key v2 differences from v1:
- No extract_blocking_issues() — blocking_issues is always [] (coder owns content analysis)
- No review_converges() check — coder decides if replan was adequate
- No review_file_has_actionable_findings() check — trust coder's REJECTED
- No duplicate review file check — coder owns path uniqueness
- No sync_review_metadata() — runner does NOT write to markdown files
- No stamp_created_metadata() — runner does NOT own markdown fields
- update_review_state() still used to track review state in job.json only
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any

from .coder_adapters import CoderInvocationError
from .exceptions import ArtifactMissingError, MetaJsonInvalidError, MetaJsonMissingError
from .job_state import (
    CONTROL_CLASSES,
    REVIEW_DECISIONS,
    HUMAN_DECISIONS,
    FINAL_DECISION_SOURCES,
    REVIEW_ARTIFACT_TYPES,
    advance_step,
    append_failure_history,
    clear_last_failure,
    default_review_state,
    record_step_usage,
    save_job,
    set_job_status,
    set_last_failure,
)
from .runtime_context import PROJECT_ROOT
from .step_runner import StepResult


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def route_after_step(
    *,
    group_name: str,
    group_cfg: dict,
    state: dict,
    step: str,
    step_cfg: dict,
    step_result: StepResult,
    coder_used: str,
    max_rejects: int,
) -> tuple[dict, int]:
    """Route job state after a successful step invocation.

    Returns (state, exit_code):
        exit_code=0 → continue (IN_PROGRESS or WAITING_FOR_HUMAN_APPROVAL)
        exit_code=1 → intervention required
        exit_code=2 → fatal failure
    """
    reject_counts = state.setdefault("reject_counts", {})
    artifacts = state.setdefault("artifacts", {})
    state.setdefault("failed_steps", [])
    state.setdefault("completed_steps", [])
    state.setdefault("model_approved_steps", [])
    step_coders = state.setdefault("step_coders", {})
    retry_history = state.setdefault("retry_history", [])
    auto_retry_counts = state.setdefault("auto_retry_count_by_step", {})
    human_retry_counts = state.setdefault("human_retry_count_by_step", {})

    step_coders[step] = coder_used
    record_step_usage(state, step, step_result.usage_data)

    retry_history.append({
        "step": step,
        "attempted_at": _now_iso(),
        "coder_used": coder_used,
        "return_code": 0,
        "result_status": step_result.status,
        "result_remark": step_result.remark,
        "reject_code": step_result.reject_code,
    })

    state["last_model_output"] = {
        "step": step,
        "coder_used": coder_used,
        "status": step_result.status,
        "remark": step_result.remark,
        "artifacts": dict(step_result.artifacts),
        "reject_code": step_result.reject_code,
        "recorded_at": _now_iso(),
    }

    if step_result.status == "APPROVED":
        return _route_approved(
            group_name=group_name,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            step_result=step_result,
            coder_used=coder_used,
            reject_counts=reject_counts,
            artifacts=artifacts,
            auto_retry_counts=auto_retry_counts,
            human_retry_counts=human_retry_counts,
        )

    # REJECTED path
    return _route_rejected(
        group_name=group_name,
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        step_result=step_result,
        coder_used=coder_used,
        max_rejects=max_rejects,
        reject_counts=reject_counts,
        artifacts=artifacts,
        auto_retry_counts=auto_retry_counts,
        human_retry_counts=human_retry_counts,
    )


def route_after_failure(
    *,
    group_name: str,
    state: dict,
    step: str,
    coder_used: str,
    exc: Exception,
    max_rejects: int,
    usage_data: dict,
) -> tuple[dict, int]:
    """Route job state after a hard failure (exception from run_step).

    Handles: CoderInvocationError, MetaJsonMissingError, MetaJsonInvalidError,
             ArtifactMissingError.
    """
    reject_counts = state.setdefault("reject_counts", {})
    failed_steps = state.setdefault("failed_steps", [])
    step_coders = state.setdefault("step_coders", {})
    retry_history = state.setdefault("retry_history", [])
    auto_retry_counts = state.setdefault("auto_retry_count_by_step", {})
    human_retry_counts = state.setdefault("human_retry_count_by_step", {})

    failure_class, failure_code, failure_source = _classify_exception_v2(exc)
    failure_reason = str(exc)

    non_progressing = _is_non_progressing(
        failure_class=failure_class,
        failure_code=failure_code,
        failure_source=failure_source,
    )
    if not non_progressing:
        step_coders[step] = coder_used

    record_step_usage(state, step, usage_data)

    return_code = exc.return_code if isinstance(exc, CoderInvocationError) else None
    retry_history.append({
        "step": step,
        "attempted_at": _now_iso(),
        "coder_used": coder_used,
        "return_code": return_code,
        "result_status": "FAILED_BEFORE_RESULT",
        "result_remark": failure_reason,
        "reject_type": failure_class,
        "reject_code": failure_code,
        "failure_source": failure_source,
    })

    current_count = int(reject_counts.get(step, 0))
    if not non_progressing:
        current_count += 1
        reject_counts[step] = current_count
        if failure_class == "AUTO_RETRYABLE":
            auto_retry_counts[step] = int(auto_retry_counts.get(step, 0)) + 1
        elif failure_class == "HUMAN_RETRY_REQUIRED":
            human_retry_counts[step] = int(human_retry_counts.get(step, 0)) + 1

    set_last_failure(
        state=state,
        failure_class=failure_class,
        failure_code=failure_code,
        failure_reason=failure_reason,
        failure_source=failure_source,
        step=step,
    )
    append_failure_history(
        state=state,
        step=step,
        failure_class=failure_class,
        failure_code=failure_code,
        failure_source=failure_source,
    )

    if non_progressing:
        set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
        state["current_step"] = step
        state["pending_intervention_for"] = step
        save_job(group_name, state["job_id"], state)
        return state, 1

    if failure_class == "FATAL" or current_count >= max_rejects:
        set_job_status(state, "FAILED")
        if step not in failed_steps:
            failed_steps.append(step)
        state["current_step"] = step
        save_job(group_name, state["job_id"], state)
        return state, 2

    set_job_status(
        state,
        "WAITING_FOR_AUTO_RETRY" if failure_class == "AUTO_RETRYABLE" else "WAITING_FOR_HUMAN_INTERVENTION",
    )
    state["current_step"] = step
    save_job(group_name, state["job_id"], state)
    return state, 1


# ---------------------------------------------------------------------------
# Internal routing
# ---------------------------------------------------------------------------

def _route_approved(
    *,
    group_name: str,
    group_cfg: dict,
    state: dict,
    step: str,
    step_cfg: dict,
    step_result: StepResult,
    coder_used: str,
    reject_counts: dict,
    artifacts: dict,
    auto_retry_counts: dict,
    human_retry_counts: dict,
) -> tuple[dict, int]:
    reject_counts[step] = 0
    auto_retry_counts[step] = 0
    human_retry_counts[step] = 0
    clear_last_failure(state)

    for key, value in step_result.artifacts.items():
        if value:
            artifacts[key] = value

    state, exit_code = advance_step(
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        result_status="APPROVED",
        coder_used=coder_used,
    )
    save_job(group_name, state["job_id"], state)
    return state, exit_code


def _route_rejected(
    *,
    group_name: str,
    group_cfg: dict,
    state: dict,
    step: str,
    step_cfg: dict,
    step_result: StepResult,
    coder_used: str,
    max_rejects: int,
    reject_counts: dict,
    artifacts: dict,
    auto_retry_counts: dict,
    human_retry_counts: dict,
) -> tuple[dict, int]:
    on_reject_refine = step_cfg.get("on_reject_refine")
    if on_reject_refine:
        return _route_loop_or_replan(
            group_name=group_name,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            step_result=step_result,
            coder_used=coder_used,
            on_reject_refine=on_reject_refine,
            reject_counts=reject_counts,
            artifacts=artifacts,
        )

    # No on_reject_refine — classify and route as model rejection
    failure_class, failure_code, failure_source = _classify_model_rejection(step_result)
    current_count = int(reject_counts.get(step, 0)) + 1
    reject_counts[step] = current_count

    set_last_failure(
        state=state,
        failure_class=failure_class,
        failure_code=failure_code,
        failure_reason=step_result.remark,
        failure_source=failure_source,
        step=step,
    )
    append_failure_history(
        state=state,
        step=step,
        failure_class=failure_class,
        failure_code=failure_code,
        failure_source=failure_source,
    )
    if failure_class == "AUTO_RETRYABLE":
        state.setdefault("auto_retry_count_by_step", {})[step] = (
            int(state.get("auto_retry_count_by_step", {}).get(step, 0)) + 1
        )
    elif failure_class == "HUMAN_RETRY_REQUIRED":
        state.setdefault("human_retry_count_by_step", {})[step] = (
            int(state.get("human_retry_count_by_step", {}).get(step, 0)) + 1
        )

    if failure_class == "FATAL" or current_count >= max_rejects:
        set_job_status(state, "FAILED")
        failed_steps = state.setdefault("failed_steps", [])
        if step not in failed_steps:
            failed_steps.append(step)
        state["current_step"] = step
        save_job(group_name, state["job_id"], state)
        return state, 2

    set_job_status(
        state,
        "WAITING_FOR_AUTO_RETRY" if failure_class == "AUTO_RETRYABLE" else "WAITING_FOR_HUMAN_INTERVENTION",
    )
    state["current_step"] = step
    save_job(group_name, state["job_id"], state)
    return state, 1


def _route_loop_or_replan(
    *,
    group_name: str,
    group_cfg: dict,
    state: dict,
    step: str,
    step_cfg: dict,
    step_result: StepResult,
    coder_used: str,
    on_reject_refine: dict,
    reject_counts: dict,
    artifacts: dict,
) -> tuple[dict, int]:
    """Handle REJECTED for steps that have on_reject_refine config."""
    # Merge artifacts from result first
    for key, value in step_result.artifacts.items():
        if value:
            artifacts[key] = value
    # Alias VALIDATION_FILE → REVIEW_FILE for validator step
    _sync_review_feedback_artifact(step=step, artifacts=artifacts)

    review_file = artifacts.get("REVIEW_FILE")
    ctx = state.setdefault("loop_context", {})
    iteration = int(ctx.get("loop_iteration", 0)) + 1
    max_iter = int(on_reject_refine.get("max_iterations", 2))

    if iteration <= max_iter:
        return _trigger_loop(
            group_name=group_name,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            coder_used=coder_used,
            on_reject_refine=on_reject_refine,
            review_file=review_file,
            iteration=iteration,
            reject_counts=reject_counts,
        )

    # Loop exhausted — try replan
    replan_cfg = step_cfg.get("on_exhaust_replan") or {}
    max_replans = int(replan_cfg.get("max_replans", 0))
    current_replan_attempt = int(state.get("replan_context", {}).get("replan_attempt", 0))

    if replan_cfg and current_replan_attempt < max_replans:
        return _trigger_replan(
            group_name=group_name,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            step_result=step_result,
            coder_used=coder_used,
            on_reject_refine=on_reject_refine,
            replan_cfg=replan_cfg,
            review_file=review_file,
            current_replan_attempt=current_replan_attempt,
            reject_counts=reject_counts,
            artifacts=artifacts,
        )

    # Both loop and replan exhausted
    exhausted_failure_class = str(
        on_reject_refine.get("exhausted_failure_class") or "HUMAN_RETRY_REQUIRED"
    )
    exhausted_failure_code = str(
        replan_cfg.get("terminal_failure_code")
        or on_reject_refine.get("exhausted_failure_code")
        or "REFINEMENT_EXHAUSTED"
    )
    reject_counts[step] = int(reject_counts.get(step, 0)) + 1
    state.setdefault("human_retry_count_by_step", {})[step] = (
        int(state.get("human_retry_count_by_step", {}).get(step, 0)) + 1
    )
    set_last_failure(
        state=state,
        failure_class=exhausted_failure_class,
        failure_code=exhausted_failure_code,
        failure_reason=step_result.remark,
        failure_source="runner",
        step=step,
    )
    append_failure_history(
        state=state,
        step=step,
        failure_class=exhausted_failure_class,
        failure_code=exhausted_failure_code,
        failure_source="runner",
    )
    set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
    state["current_step"] = step
    save_job(group_name, state["job_id"], state)
    return state, 1


def _trigger_loop(
    *,
    group_name: str,
    group_cfg: dict,
    state: dict,
    step: str,
    step_cfg: dict,
    coder_used: str,
    on_reject_refine: dict,
    review_file: str | None,
    iteration: int,
    reject_counts: dict,
) -> tuple[dict, int]:
    """Activate the refine loop for this iteration."""
    # Budget check
    allowed, _ = _consume_planning_attempt_budget(state=state, group_cfg=group_cfg)
    if not allowed:
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
        save_job(group_name, state["job_id"], state)
        return state, 1

    state["loop_context"] = {
        "active": True,
        "loop_step": step,
        "refine_step": on_reject_refine["step"],
        "loop_target_artifact": on_reject_refine["artifact"],
        "loop_source_review": review_file,
        "loop_iteration": iteration,
        "pre_refine_checksum": None,
    }
    state.setdefault("loop_history", []).append({
        "iteration": iteration,
        "loop_step": step,
        "refine_step": on_reject_refine["step"],
        "review_result": "REJECTED",
        "review_file": review_file,
        "review_at": _now_iso(),
        "refine_result": None,
        "refine_at": None,
        "started_at": _now_iso(),
        "resolved_at": None,
    })
    clear_last_failure(state)
    state["current_step"] = on_reject_refine["step"]
    _update_review_state(
        state,
        step=step,
        step_cfg=step_cfg,
        coder_used=coder_used,
        review_decision="REJECTED",
        human_decision="NOT_REQUIRED",
        final_decision="REJECTED",
        final_decision_source="MODEL",
    )
    # v2: no sync_review_metadata — runner does NOT write to markdown
    set_job_status(state, "IN_PROGRESS")
    save_job(group_name, state["job_id"], state)
    return state, 0


def _trigger_replan(
    *,
    group_name: str,
    group_cfg: dict,
    state: dict,
    step: str,
    step_cfg: dict,
    step_result: StepResult,
    coder_used: str,
    on_reject_refine: dict,
    replan_cfg: dict,
    review_file: str | None,
    current_replan_attempt: int,
    reject_counts: dict,
    artifacts: dict,
) -> tuple[dict, int]:
    """Trigger a replan after loop exhaustion."""
    # Budget check
    allowed, _ = _consume_planning_attempt_budget(state=state, group_cfg=group_cfg)
    if not allowed:
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
        save_job(group_name, state["job_id"], state)
        return state, 1

    trigger_reason = str(
        on_reject_refine.get("exhausted_failure_code") or "REFINEMENT_EXHAUSTED"
    )

    # v2: blocking_issues is always [] — content analysis is coder's job
    state["replan_context"] = {
        "active": True,
        "source_review_step": step,
        "replan_step": replan_cfg["step"],
        "target_artifact": replan_cfg["artifact"],
        "source_review_file": review_file,
        "replan_attempt": current_replan_attempt + 1,
        "pre_replan_checksum": None,
        "trigger_reason": trigger_reason,
        "blocking_issues": [],         # v2: always empty — coder owns analysis
        "previous_blocking_issue_count": 0,
        "previous_blocking_issue_severity": 0,
    }

    # Capture pre-replan checksum of target artifact
    target_path_value = artifacts.get(replan_cfg["artifact"])
    if target_path_value:
        target_path = PROJECT_ROOT / target_path_value
        if target_path.exists():
            import hashlib
            state["replan_context"]["pre_replan_checksum"] = hashlib.md5(
                target_path.read_bytes()
            ).hexdigest()

    state.setdefault("replan_history", []).append({
        "source_review_step": step,
        "trigger_reason": trigger_reason,
        "source_review_file": review_file,
        "blocking_issues": [],
        "replan_step": replan_cfg["step"],
        "replan_attempt": state["replan_context"]["replan_attempt"],
        "triggered_at": _now_iso(),
        "replan_result": None,
        "review_result": None,
        "resolved_at": None,
    })
    # Reset loop context for the new replan cycle
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
    state["current_step"] = replan_cfg["step"]
    _update_review_state(
        state,
        step=step,
        step_cfg=step_cfg,
        coder_used=coder_used,
        review_decision="REJECTED",
        human_decision="NOT_REQUIRED",
        final_decision="REJECTED",
        final_decision_source="MODEL",
    )
    # v2: no sync_review_metadata
    set_job_status(state, "IN_PROGRESS")
    save_job(group_name, state["job_id"], state)
    return state, 0


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

def _classify_model_rejection(step_result: StepResult) -> tuple[str, str, str]:
    hint = str(step_result.reject_code or "").strip().upper()
    code = hint or "MODEL_REJECTED"
    remark = step_result.remark
    lowered = remark.lower()

    if hint in CONTROL_CLASSES:
        return hint, code, "model"
    if _looks_like_transient_error(remark):
        return "AUTO_RETRYABLE", code, "model"
    if any(tok in lowered for tok in ("pending", "not approved", "approval", "preflight",
                                       "missing input", "missing artifact", "schema", "invalid")):
        return "HUMAN_RETRY_REQUIRED", code, "model"
    if any(tok in lowered for tok in ("forbidden", "not allowed", "out of scope", "scope", "policy")):
        return "FATAL", code, "model"
    return "HUMAN_RETRY_REQUIRED", code, "model"


def _classify_exception_v2(exc: Exception) -> tuple[str, str, str]:
    """Map v2 exception types to (failure_class, failure_code, failure_source)."""
    if isinstance(exc, CoderInvocationError):
        if _looks_like_transient_error(str(exc)):
            return "AUTO_RETRYABLE", "TRANSIENT_API_ERROR", "adapter"
        return "HUMAN_RETRY_REQUIRED", "ADAPTER_INVOCATION_FAILED", "adapter"
    if isinstance(exc, MetaJsonMissingError):
        return "HUMAN_RETRY_REQUIRED", "META_JSON_MISSING", "validator"
    if isinstance(exc, MetaJsonInvalidError):
        return "HUMAN_RETRY_REQUIRED", "META_JSON_INVALID", "validator"
    if isinstance(exc, ArtifactMissingError):
        return "HUMAN_RETRY_REQUIRED", "ARTIFACT_FILES_MISSING", "validator"
    # Unknown exception — treat as fatal
    return "FATAL", "UNEXPECTED_RUNNER_ERROR", "runner"


def _looks_like_transient_error(message: str) -> bool:
    lowered = message.lower()
    hints = (
        "connection error", "fetch failed", "timed out", "timeout", "temporar",
        "rate limit", "429", "service unavailable", "api error", "network error",
    )
    return any(hint in lowered for hint in hints)


def _is_non_progressing(*, failure_class: str, failure_code: str, failure_source: str) -> bool:
    return (
        failure_source == "runner"
        and failure_class == "HUMAN_RETRY_REQUIRED"
        and failure_code in {"INVALID_RUNNER_CONFIGURATION", "UNKNOWN_CODER"}
    )


# ---------------------------------------------------------------------------
# Planning budget
# ---------------------------------------------------------------------------

def _consume_planning_attempt_budget(*, state: dict, group_cfg: dict) -> tuple[bool, int]:
    limit = int(group_cfg.get("max_planning_attempts", 0) or 0)
    if limit <= 0:
        return True, 0
    current = int(state.get("planning_attempt_count", 0)) + 1
    state["planning_attempt_count"] = current
    return current <= limit, current


# ---------------------------------------------------------------------------
# Review state (job.json only — no markdown writes)
# ---------------------------------------------------------------------------

def _review_target_artifact_key(step_cfg: dict) -> str | None:
    on_reject_refine = step_cfg.get("on_reject_refine") or {}
    if on_reject_refine.get("artifact"):
        return str(on_reject_refine["artifact"])
    produces = step_cfg.get("produces", [])
    if step_cfg.get("requires_human_approval_after") and produces:
        return str(produces[0])
    return None


def _update_review_state(
    state: dict,
    *,
    step: str,
    step_cfg: dict,
    coder_used: str | None = None,
    review_decision: str | None = None,
    human_decision: str | None = None,
    final_decision: str | None = None,
    final_decision_source: str | None = None,
) -> None:
    review_state = state.setdefault("review_state", default_review_state())
    artifact_key = _review_target_artifact_key(step_cfg)
    artifact_path = state.get("artifacts", {}).get(artifact_key) if artifact_key else None
    if artifact_key:
        review_state["artifact_key"] = artifact_key
        review_state["artifact_type"] = REVIEW_ARTIFACT_TYPES.get(
            artifact_key, artifact_key.removesuffix("_FILE")
        )
        review_state["artifact_path"] = artifact_path
    review_state["reviewer_step"] = step
    if coder_used:
        review_state["coder_used"] = coder_used
    if review_decision and review_decision in REVIEW_DECISIONS:
        review_state["review_decision"] = review_decision
        review_state["review_decided_at"] = None if review_decision == "PENDING" else _now_iso()
    if human_decision and human_decision in HUMAN_DECISIONS:
        review_state["human_decision"] = human_decision
        if human_decision in {"APPROVED", "REJECTED"}:
            review_state["human_decided_at"] = _now_iso()
            review_state["human_actor"] = "human"
        else:
            review_state["human_decided_at"] = None
            review_state["human_actor"] = None
    if final_decision is not None:
        review_state["final_decision"] = final_decision
    if final_decision_source and final_decision_source in FINAL_DECISION_SOURCES:
        review_state["final_decision_source"] = final_decision_source


def _sync_review_feedback_artifact(*, step: str, artifacts: dict) -> None:
    """Alias VALIDATION_FILE → REVIEW_FILE for validator step."""
    if step == "validator":
        validation_file = str(artifacts.get("VALIDATION_FILE") or "").strip()
        if validation_file and not artifacts.get("REVIEW_FILE"):
            artifacts["REVIEW_FILE"] = validation_file


# ---------------------------------------------------------------------------
# Time helper
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")
