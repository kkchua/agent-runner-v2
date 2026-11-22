#!/usr/bin/env python3
"""workflow_router.py — Post-step routing for agent_runner_v2."""
from __future__ import annotations

import copy
import datetime as dt
import re
from pathlib import Path
from typing import Any

from ..coder_adapters import CoderInvocationError
from ..constants import ARTIFACT_KEY_REVIEW
from ..exceptions import ArtifactMissingError, MetaJsonInvalidError, MetaJsonMissingError, UnauthorizedWriteError
from ..failure_runtime import append_failure_history, clear_last_failure, set_last_failure
from ..recovery_runtime import (
    activate_refine_loop,
    handle_recovery_budget_exceeded,
)
from ..job_state import (
    CONTROL_CLASSES,
    REVIEW_DECISIONS,
    HUMAN_DECISIONS,
    FINAL_DECISION_SOURCES,
    REVIEW_ARTIFACT_TYPES,
    _get_effective_limit,
    advance_step,
    default_review_state,
    record_step_usage,
    save_job,
    set_job_status,
)
from ..notifications import send_notification
from ..notification_manager import send_workflow_notification, send_step_notification
from ..runtime_context import PROJECT_ROOT
from ..step_runner import StepResult


# ---------------------------------------------------------------------------
# Path helpers (R20: A16-02)
# ---------------------------------------------------------------------------

def _resolve_path_against_root(path_str: str) -> Path:
    """Resolve a path against PROJECT_ROOT.

    R20: Handles both relative and absolute paths consistently.
    """
    from .. import runtime_context
    project_root = Path(str(runtime_context.PROJECT_ROOT)).resolve()
    path = Path(str(path_str))
    if path.is_absolute():
        return path.resolve()
    return (project_root / path).resolve()


def _normalize_optional_path(path_str: str | None) -> str | None:
    """Normalize optional path to canonical representation.

    R20: Returns None for absent, resolved string for present.
    Used for unconditional comparison.
    """
    if path_str is None:
        return None
    return str(_resolve_path_against_root(path_str))


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
    # R10-I3: For plan-first, run gate BEFORE any defaults/mutations
    if group_name == "plan_first_review_v1" and step in ("generate_plan", "refine_plan"):
        gate_result = _plan_first_result_gate(
            group_name=group_name,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            step_result=step_result,
        )

        # Terminal two-tuple: return immediately (no mutations, no copies)
        if isinstance(gate_result, tuple) and len(gate_result) == 2 and isinstance(gate_result[0], dict):
            return gate_result

        # Validation tuple: first outcome validated - copy BEFORE any setdefault
        if isinstance(gate_result, tuple) and len(gate_result) == 5:
            # Create baseline and transition BEFORE touching original state
            baseline = copy.deepcopy(state)
            transition = copy.deepcopy(baseline)

            # Initialize ALL dictionaries on transition (not original)
            transition.setdefault("reject_counts", {})
            transition.setdefault("artifacts", {})
            transition.setdefault("failed_steps", [])
            transition.setdefault("completed_steps", [])
            transition.setdefault("model_approved_steps", [])
            transition.setdefault("step_coders", {})
            transition.setdefault("retry_history", [])
            transition.setdefault("auto_retry_count_by_step", {})
            transition.setdefault("human_retry_count_by_step", {})

            # Record bookkeeping on transition
            transition["step_coders"][step] = coder_used
            record_step_usage(transition, step, step_result.usage_data)

            transition["retry_history"].append({
                "step": step,
                "attempted_at": _now_iso(),
                "coder_used": coder_used,
                "return_code": 0,
                "result_status": step_result.status,
                "result_remark": step_result.remark,
                "reject_code": step_result.reject_code,
            })

            transition["last_model_output"] = {
                "step": step,
                "coder_used": coder_used,
                "status": step_result.status,
                "remark": step_result.remark,
                "artifacts": dict(step_result.artifacts),
                "reject_code": step_result.reject_code,
                "recorded_at": _now_iso(),
            }

            # Route on transition and RETURN (do NOT fall through to generic routing)
            if step_result.status == "APPROVED":
                return _route_plan_first_approved(
                    group_name=group_name,
                    group_cfg=group_cfg,
                    original_state=state,  # Original, untouched
                    baseline=baseline,
                    transition=transition,
                    step=step,
                    step_cfg=step_cfg,
                    step_result=step_result,
                    coder_used=coder_used,
                    validation=gate_result,
                )
            else:  # REJECTED
                return _route_plan_first_rejected(
                    group_name=group_name,
                    group_cfg=group_cfg,
                    original_state=state,  # Original, untouched
                    baseline=baseline,
                    transition=transition,
                    step=step,
                    step_cfg=step_cfg,
                    step_result=step_result,
                    coder_used=coder_used,
                    max_rejects=max_rejects,
                    validation=gate_result,
                )

        # Unexpected gate result: internal error, not generic routing
        raise RuntimeError(
            f"Unexpected gate result for plan-first routing: {type(gate_result).__name__}"
        )

    # Non-plan-first: existing behavior (setdefault on original)
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
    step_cfg: dict | None = None,
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

    # Check for step-level failure notification configuration
    if step_cfg:
        send_step_notification("STEP_FAILED", state, step, step_cfg)

    if non_progressing:
        set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
        state["current_step"] = step
        state["pending_intervention_for"] = step
        save_job(group_name, state["job_id"], state)
        # Send notification for human intervention required
        send_workflow_notification("WAITING_FOR_HUMAN_INTERVENTION", dict(state))
        return state, 1

    if failure_class == "FATAL" or current_count >= max_rejects:
        set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
        if step not in failed_steps:
            failed_steps.append(step)
        state["current_step"] = step
        state["pending_intervention_for"] = step
        save_job(group_name, state["job_id"], state)
        send_workflow_notification("WAITING_FOR_HUMAN_INTERVENTION", dict(state))
        return state, 1

    set_job_status(
        state,
        "WAITING_FOR_AUTO_RETRY" if failure_class == "AUTO_RETRYABLE" else "WAITING_FOR_HUMAN_INTERVENTION",
    )
    state["current_step"] = step
    if failure_class != "AUTO_RETRYABLE":
        state["pending_intervention_for"] = step
    save_job(group_name, state["job_id"], state)
    if failure_class != "AUTO_RETRYABLE":
        send_workflow_notification("WAITING_FOR_HUMAN_INTERVENTION", dict(state))
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
    skip_save: bool = False,
    defer_notifications: bool = False,
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
        defer_notifications=defer_notifications,
    )
    if not skip_save:
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
    skip_save: bool = False,
) -> tuple[dict, int]:
    if not skip_save:
        send_step_notification("STEP_REJECTED", state, step, step_cfg)

    on_reject_refine = _resolve_reject_route(step_cfg=step_cfg, reject_code=step_result.reject_code)
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
        set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
        failed_steps = state.setdefault("failed_steps", [])
        if step not in failed_steps:
            failed_steps.append(step)
        state["current_step"] = step
        state["pending_intervention_for"] = step
        save_job(group_name, state["job_id"], state)
        send_workflow_notification("WAITING_FOR_HUMAN_INTERVENTION", dict(state))
        return state, 1

    set_job_status(
        state,
        "WAITING_FOR_AUTO_RETRY" if failure_class == "AUTO_RETRYABLE" else "WAITING_FOR_HUMAN_INTERVENTION",
    )
    state["current_step"] = step
    if failure_class != "AUTO_RETRYABLE":
        state["pending_intervention_for"] = step
    save_job(group_name, state["job_id"], state)
    if failure_class != "AUTO_RETRYABLE":
        send_workflow_notification("WAITING_FOR_HUMAN_INTERVENTION", dict(state))
    return state, 1


def _resolve_reject_route(*, step_cfg: dict, reject_code: str | None) -> dict | None:
    """Return the refine-route config for the current reject code, if any."""
    default_route = step_cfg.get("on_reject_refine")
    routes = step_cfg.get("reject_code_routes") or {}
    if reject_code and isinstance(routes, dict):
        candidate = routes.get(str(reject_code).strip().upper())
        if isinstance(candidate, dict) and candidate.get("step") and candidate.get("artifact"):
            return candidate
    return default_route


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
    # R20: A16-01 - For plan_first_review_v1 codex_review, require declared review
    if group_name == "plan_first_review_v1" and step == "codex_review":
        from ..constants import ARTIFACT_PATH_CODEX_REVIEW

        planning_folder = state.get("artifacts", {}).get("PLANNING_FOLDER")
        current_revision = state.get("plan_revision", 1)
        baseline = state.get("requirements_baseline", 1)

        # R20: REQUIRE nonempty CODEX_REVIEW_FILE in current outcome
        reported_review = step_result.artifacts.get("CODEX_REVIEW_FILE")
        if not reported_review:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="MISSING_REVIEW_ARTIFACT_DECLARATION",
                failure_reason="Current codex_review outcome did not declare CODEX_REVIEW_FILE",
            )

        # R20: Compute canonical declared review path
        canonical_review_path = ARTIFACT_PATH_CODEX_REVIEW(planning_folder, current_revision, baseline)
        canonical_resolved = _resolve_path_against_root(canonical_review_path)

        # R20: Validate reported matches canonical
        reported_resolved = _resolve_path_against_root(reported_review)
        if reported_resolved != canonical_resolved:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="INVALID_REVIEW_ARTIFACT",
                failure_reason=f"Reported review {reported_review} != canonical {canonical_review_path}",
            )

        # R20: Verify canonical file exists and is a readable regular file
        if not canonical_resolved.exists():
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="REVIEW_ARTIFACT_MISSING",
                failure_reason=f"Declared review artifact missing: {canonical_review_path}",
            )
        if not canonical_resolved.is_file():
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="REVIEW_ARTIFACT_NOT_FILE",
                failure_reason=f"Declared review artifact is not a file: {canonical_review_path}",
            )

        # R20: Verify file is readable
        try:
            canonical_resolved.read_bytes()
        except Exception as e:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="REVIEW_ARTIFACT_UNREADABLE",
                failure_reason=f"Cannot read declared review artifact: {e}",
            )

        # R20: Bind declared review (override stale generic alias)
        artifacts["CODEX_REVIEW_FILE"] = canonical_review_path
        artifacts[ARTIFACT_KEY_REVIEW] = canonical_review_path
        review_file = canonical_review_path
    else:
        # Existing logic: merge artifacts and alias
        for key, value in step_result.artifacts.items():
            if value:
                artifacts[key] = value
        # Alias VALIDATION_FILE → REVIEW_FILE_SUGGESTED for validator step
        _sync_review_feedback_artifact(step=step, artifacts=artifacts)
        _cleanup_rejected_feedback_docs(
            group_name=group_name,
            state=state,
            step=step,
            artifacts=artifacts,
        )
        review_file = artifacts.get(ARTIFACT_KEY_REVIEW)
    current_count = int(reject_counts.get(step, 0)) + 1
    reject_counts[step] = current_count
    iteration = current_count
    max_iter = int(on_reject_refine.get("max_iterations", 2))

    # ── Cumulative refinement limit (plan_first_review_v1 only) ──
    if group_name == "plan_first_review_v1":
        effective_limit = _get_effective_limit(state, on_reject_refine)
        current_revision = state.get("plan_revision", 1)
        if effective_limit > 0 and current_revision > effective_limit:
            cumulative_code = str(
                on_reject_refine.get("exhausted_failure_code") or "PLAN_REFINEMENT_EXHAUSTED"
            )
            set_last_failure(
                state=state,
                failure_class=str(on_reject_refine.get("exhausted_failure_class") or "HUMAN_RETRY_REQUIRED"),
                failure_code=cumulative_code,
                failure_reason=f"Cumulative refinements ({current_revision}) exceeded effective limit ({effective_limit}) for step {step!r}.",
                failure_source="runner",
                step=step,
            )
            set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
            state["current_step"] = step
            state["pending_intervention_for"] = step
            save_job(group_name, state["job_id"], state)
            send_workflow_notification("WAITING_FOR_HUMAN_INTERVENTION", dict(state))
            return state, 1

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

    # Loop exhausted
    exhausted_failure_class = str(
        on_reject_refine.get("exhausted_failure_class") or "HUMAN_RETRY_REQUIRED"
    )
    exhausted_failure_code = str(
        on_reject_refine.get("exhausted_failure_code")
        or "REFINEMENT_EXHAUSTED"
    )
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
    set_job_status(state, "WAITING_FOR_HUMAN_MAXRETRIED")
    state["current_step"] = step
    state["pending_intervention_for"] = step
    save_job(group_name, state["job_id"], state)
    send_workflow_notification("WAITING_FOR_HUMAN_MAXRETRIED", dict(state))
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
    # R20: A16-01 - Compute MD5 checksum from target artifact before loop activation
    # (plan_first_review_v1 only, to avoid changing unrelated workflows)
    pre_refine_checksum = None
    if group_name == "plan_first_review_v1":
        target_artifact = on_reject_refine.get("artifact")  # "QWEN_PLAN_FILE"
        target_path_value = state.get("artifacts", {}).get(target_artifact)

        if target_path_value:
            target_resolved = _resolve_path_against_root(target_path_value)

            # R20: Validate target exists and is readable BEFORE loop publication
            if not target_resolved.exists():
                return _gate_failure(
                    group_name=group_name,
                    state=state,
                    step=step,
                    failure_code="REFINE_TARGET_MISSING",
                    failure_reason=f"Refinement target missing: {target_path_value}",
                )
            if not target_resolved.is_file():
                return _gate_failure(
                    group_name=group_name,
                    state=state,
                    step=step,
                    failure_code="REFINE_TARGET_NOT_FILE",
                    failure_reason=f"Refinement target is not a file: {target_path_value}",
                )
            try:
                # R20: MD5 for recovery no-op comparison (not SHA256)
                from ..job_state import _md5_file
                pre_refine_checksum = _md5_file(target_resolved)
            except Exception as e:
                return _gate_failure(
                    group_name=group_name,
                    state=state,
                    step=step,
                    failure_code="REFINE_TARGET_UNREADABLE",
                    failure_reason=f"Cannot read refinement target: {e}",
                )
        else:
            # R20: Missing target artifact - fail before publishing
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="REFINE_TARGET_NOT_FOUND",
                failure_reason="No target artifact found for refinement checksum",
            )

    # Budget check
    allowed, _ = _consume_planning_attempt_budget(state=state, group_cfg=group_cfg)
    if not allowed:
        state, exit_code = handle_recovery_budget_exceeded(
            state=state,
            step=step,
            reject_counts=reject_counts,
            set_last_failure=set_last_failure,
            append_failure_history=append_failure_history,
            set_job_status=set_job_status,
        )
        save_job(group_name, state["job_id"], state)
        return state, exit_code

    state, exit_code = activate_refine_loop(
        state=state,
        step=step,
        refine_step=on_reject_refine["step"],
        target_artifact=on_reject_refine["artifact"],
        review_file=review_file,
        iteration=iteration,
        pre_refine_checksum=pre_refine_checksum,  # R20: MD5 checksum
        now_iso=_now_iso,
        clear_last_failure=clear_last_failure,
        set_job_status=set_job_status,
    )
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
    save_job(group_name, state["job_id"], state)
    return state, exit_code


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
        # All coder invocation failures are auto-retryable — the LLM may
        # have stopped early, hit a transient API issue, or failed to
        # produce output. max_rejects (default 3) prevents infinite loops.
        if _looks_like_transient_error(str(exc)):
            return "AUTO_RETRYABLE", "TRANSIENT_API_ERROR", "adapter"
        return "AUTO_RETRYABLE", "ADAPTER_INVOCATION_FAILED", "adapter"
    if isinstance(exc, MetaJsonMissingError):
        return "AUTO_RETRYABLE", "META_JSON_MISSING", "validator"
    if isinstance(exc, MetaJsonInvalidError):
        return "AUTO_RETRYABLE", "META_JSON_INVALID", "validator"
    if isinstance(exc, ArtifactMissingError):
        message = str(exc)
        if _looks_like_step_contract_mismatch(message):
            return "HUMAN_RETRY_REQUIRED", "STEP_CONTRACT_MISMATCH", "validator"
        return "HUMAN_RETRY_REQUIRED", "ARTIFACT_FILES_MISSING", "validator"
    if isinstance(exc, UnauthorizedWriteError):
        return "HUMAN_RETRY_REQUIRED", "UNAUTHORIZED_WRITE_DETECTED", "validator"
    # Unknown exception — treat as fatal
    return "FATAL", "UNEXPECTED_RUNNER_ERROR", "runner"


def _looks_like_transient_error(message: str) -> bool:
    lowered = message.lower()
    # If retries have been exhausted or this is an aggregate partial result,
    # the action already consumed its internal retry budget — NOT transient.
    exhausted_indicators = (
        "max retries", "retries exhausted", "max attempts", "attempts exhausted",
        "retry limit", "retry quota",
        "partial failure", "partial success",
    )
    if any(indicator in lowered for indicator in exhausted_indicators):
        return False
    hints = (
        "connection error", "fetch failed", "timed out", "timeout", "temporar",
        "rate limit", "429", "service unavailable", "network error",
    )
    return any(hint in lowered for hint in hints)


def _is_non_progressing(*, failure_class: str, failure_code: str, failure_source: str) -> bool:
    return (
        failure_source in {"runner", "validator"}
        and failure_class == "HUMAN_RETRY_REQUIRED"
        and failure_code in {
            "INVALID_RUNNER_CONFIGURATION",
            "UNKNOWN_CODER",
            "STEP_CONTRACT_MISMATCH",
        }
    )


def _looks_like_step_contract_mismatch(message: str) -> bool:
    lowered = str(message or "").lower()
    hints = (
        "reported artifacts not declared in 'produces' list",
        "no resolved output path",
        "step config has neither 'result_meta_key' nor 'result_meta_key_from_context'",
        "write-capable but declares no write contract",
    )
    return any(hint in lowered for hint in hints)


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
    """Alias validator outputs to REVIEW_FILE_SUGGESTED for refine-loop prompts."""
    if artifacts.get(ARTIFACT_KEY_REVIEW):
        return

    candidate_keys = []
    if step == "validator":
        candidate_keys.append("VALIDATION_FILE")
    if step == "07_validate_codebase_baseline":
        candidate_keys.append("VALIDATION_FILE")
    if step == "08_validate_master_system_docs":
        candidate_keys.append("SYSTEM_DOCS_VALIDATION")

    for key in candidate_keys:
        validation_file = str(artifacts.get(key) or "").strip()
        if validation_file:
            artifacts[ARTIFACT_KEY_REVIEW] = validation_file
            return


def _cleanup_rejected_feedback_docs(
    *,
    group_name: str,
    state: dict,
    step: str,
    artifacts: dict,
) -> None:
    """Remove stale downstream feedback docs before a refine reroute."""
    template_group = str(state.get("template_group") or group_name or "").strip()
    if template_group not in {"00_layer1_governance_bootstrap_v1", "01_governance_foundation_v1"}:
        return

    job_id = str(state.get("job_id") or "").strip()
    if not job_id:
        return

    stale_rel_paths = _layer1_rejected_stale_feedback_paths(job_id=job_id, step=step)
    if not stale_rel_paths:
        return

    project_root = Path(str(PROJECT_ROOT)).resolve()
    for rel_path in stale_rel_paths:
        file_path = project_root / rel_path
        try:
            file_path.unlink(missing_ok=True)
        except OSError:
            pass
        try:
            file_path.with_suffix(".meta.json").unlink(missing_ok=True)
        except OSError:
            pass

        normalized_rel = rel_path.replace("\\", "/")
        for artifact_key in list(artifacts.keys()):
            artifact_value = str(artifacts.get(artifact_key) or "").strip().replace("\\", "/")
            if artifact_value == normalized_rel:
                artifacts.pop(artifact_key, None)


def _layer1_rejected_stale_feedback_paths(*, job_id: str, step: str) -> list[str]:
    base = "docs/system/00_governance/bootstrap"
    validation_paths = [
        f"{base}/{job_id}-layer1-governance-validation.md",
        f"{base}/{job_id}-bootstrap-validation.md",
    ]
    audit_path = f"{base}/{job_id}-layer1-governance-audit.md"

    if step == "review_layer1_governance_docs":
        return [*validation_paths, audit_path]
    if step == "validate_layer1_governance_docs":
        return [audit_path]
    return []


# ---------------------------------------------------------------------------
# Time helper
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Phase A: Plan-First Result Gate
# ---------------------------------------------------------------------------

def _gate_failure(
    *,
    group_name: str,
    state: dict,
    step: str,
    failure_code: str,
    failure_reason: str,
) -> tuple[dict, int]:
    """Record a plan-first gate failure and return terminal tuple.

    R20: A16-04 - Creates isolated copy to avoid mutating original caller on save failure.
    Returns the isolated failure state for caller inspection.
    """
    # R20: Create isolated copy BEFORE any mutations
    isolated = copy.deepcopy(state)

    # Apply failure envelope to isolated copy
    set_last_failure(
        state=isolated,
        failure_class="HUMAN_RETRY_REQUIRED",
        failure_code=failure_code,
        failure_reason=failure_reason,
        failure_source="runner",
        step=step,
    )
    set_job_status(isolated, "WAITING_FOR_HUMAN_INTERVENTION")
    isolated["current_step"] = step
    isolated["pending_intervention_for"] = step

    # Save isolated state (may raise on failure)
    save_job(group_name, isolated["job_id"], isolated)
    send_workflow_notification("WAITING_FOR_HUMAN_INTERVENTION", dict(isolated))

    return isolated, 1


def _plan_first_result_gate(
    *,
    group_name: str,
    group_cfg: dict,
    state: dict,
    step: str,
    step_cfg: dict,
    step_result: StepResult,
) -> tuple[dict, int] | tuple[bool, dict | None, dict | None, Path | None, str | None]:
    """Validate plan-first result before routing.

    Returns:
        Terminal tuple (state, exit_code) on failure or terminal replay.
        Validation tuple (True, recovery, output_evidence, canonical_path, digest) on success.
    """
    attempt_id = step_result.attempt_id

    # R10-I2: Missing attempt_id is a failure
    if not attempt_id:
        return _gate_failure(
            group_name=group_name,
            state=state,
            step=step,
            failure_code="MISSING_ATTEMPT_ID",
            failure_reason="StepResult has no attempt_id for plan-first routing.",
        )

    # R10-I2: Validate ownership
    attempt_record = state.get("attempt_records", {}).get(attempt_id)
    if not attempt_record:
        return _gate_failure(
            group_name=group_name,
            state=state,
            step=step,
            failure_code="UNKNOWN_ATTEMPT_ID",
            failure_reason=f"Attempt record not found: {attempt_id}",
        )

    if attempt_record.get("job_id") != state.get("job_id"):
        return _gate_failure(
            group_name=group_name,
            state=state,
            step=step,
            failure_code="ATTEMPT_JOB_MISMATCH",
            failure_reason=f"Attempt job_id {attempt_record.get('job_id')!r} != state job_id {state.get('job_id')!r}",
        )

    if attempt_record.get("workflow") != group_name:
        return _gate_failure(
            group_name=group_name,
            state=state,
            step=step,
            failure_code="ATTEMPT_WORKFLOW_MISMATCH",
            failure_reason=f"Attempt workflow {attempt_record.get('workflow')!r} != group {group_name!r}",
        )

    if attempt_record.get("step") != step:
        return _gate_failure(
            group_name=group_name,
            state=state,
            step=step,
            failure_code="ATTEMPT_STEP_MISMATCH",
            failure_reason=f"Attempt step {attempt_record.get('step')!r} != current step {step!r}",
        )

    # R10-I2: Check terminal duplicate (applied/rejected/failed)
    current_status = attempt_record.get("status")
    if current_status in ("applied", "rejected", "failed"):
        # Terminal replay: validate identity and return stored outcome
        return _handle_terminal_replay(
            group_name=group_name,
            state=state,
            step=step,
            step_result=step_result,
            attempt_record=attempt_record,
            current_status=current_status,
        )

    # R10-I2: Validate eligibility (baseline, revision formula, active conflict)
    loop_context = state.get("loop_context", {})
    active_attempt_id = loop_context.get("active_attempt_id")

    if active_attempt_id and active_attempt_id != attempt_id:
        return _gate_failure(
            group_name=group_name,
            state=state,
            step=step,
            failure_code="ACTIVE_ATTEMPT_CONFLICT",
            failure_reason=f"Attempt {attempt_id} conflicts with active attempt {active_attempt_id}",
        )

    # Use _validate_prepared_eligibility if available (test may mock it)
    baseline = attempt_record.get("baseline")
    input_revision = attempt_record.get("input_revision")
    target_revision = attempt_record.get("target_revision")

    # Call _validate_prepared_eligibility for revision formula validation
    valid, error, recovery_context = _validate_prepared_eligibility(
        state=state,
        group_name=group_name,
        step=step,
        attempt_id=attempt_id,
        baseline=baseline,
        input_revision=input_revision,
        target_revision=target_revision,
    )
    if not valid:
        return _gate_failure(
            group_name=group_name,
            state=state,
            step=step,
            failure_code="ELIGIBILITY_FAILURE",
            failure_reason=error or "Eligibility validation failed",
        )

    # F2: Validate owned recovery context if present
    planning_folder = state.get("artifacts", {}).get("PLANNING_FOLDER")

    # R16-02: Refinement REQUIRES a valid recovery context
    if step == "refine_plan":
        if not attempt_record.get("recovered_context"):
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="MISSING_RECOVERY_CONTEXT",
                failure_reason="Refinement requires a recovery context.",
            )
        validated_context = _validate_owned_recovery_context(
            attempt_record=attempt_record,
            group_name=group_name,
            job_id=state.get("job_id"),
            baseline=baseline,
            step=step,
            input_revision=input_revision,
            target_revision=target_revision,
            group_cfg=group_cfg,
            planning_folder=planning_folder,
        )
        if validated_context is None:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="INVALID_RECOVERY_CONTEXT",
                failure_reason="Recovery context failed ownership validation.",
            )
        # Use validated context
        recovery_context = validated_context
    else:
        # R16-R6: Generation REQUIRES valid inactive recovery context
        # Missing/empty context is NOT valid - must come from preparation producer
        recovered_context = attempt_record.get("recovered_context")
        if not recovered_context:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="MISSING_RECOVERY_CONTEXT",
                failure_reason="Generation requires a recovery context from preparation producer.",
            )
        validated_context = _validate_owned_recovery_context(
            attempt_record=attempt_record,
            group_name=group_name,
            job_id=state.get("job_id"),
            baseline=baseline,
            step=step,
            input_revision=input_revision,
            target_revision=target_revision,
            group_cfg=group_cfg,
            planning_folder=planning_folder,
        )
        if validated_context is None:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="INVALID_RECOVERY_CONTEXT",
                failure_reason="Generation recovery context failed validation (must be inactive with active=False).",
            )
        # Use validated context
        recovery_context = validated_context

    # R10-I2: Completion ownership check
    completions = state.get("revision_completions", {})
    if baseline is not None and target_revision is not None:
        completion_key = f"b{baseline}_r{target_revision}"
        existing = completions.get(completion_key)
        if existing and existing.get("attempt_id") != attempt_id:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="COMPLETION_OWNERSHIP_CONFLICT",
                failure_reason=f"Target b{baseline}_r{target_revision} already completed by {existing.get('attempt_id')}",
            )

    # R10-I1: For APPROVED, validate output with ARTIFACT_PATH_QWEN_PLAN
    if step_result.status == "APPROVED":
        if not planning_folder:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="MISSING_PLANNING_FOLDER",
                failure_reason="PLANNING_FOLDER artifact not found.",
            )

        # Derive expected output path from step config
        step_configs = group_cfg.get("step_configs", {})
        step_config = step_configs.get(step, {})
        on_reject_refine = step_config.get("on_reject_refine", {})
        artifact_key = on_reject_refine.get("artifact", "QWEN_PLAN_FILE")

        output_artifact = step_result.artifacts.get(artifact_key)
        if not output_artifact:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="MISSING_OUTPUT_ARTIFACT",
                failure_reason=f"Output artifact {artifact_key!r} not found in StepResult.",
            )

        # F2: Derive canonical path using ARTIFACT_PATH_QWEN_PLAN
        from ..constants import ARTIFACT_PATH_QWEN_PLAN
        canonical_relative = ARTIFACT_PATH_QWEN_PLAN(
            folder=planning_folder,
            revision=target_revision or 1,
            baseline=baseline or 1,
        )

        # R20: A16-02 - Resolve both paths against PROJECT_ROOT and compare full identity
        output_resolved = _resolve_path_against_root(str(output_artifact))
        canonical_resolved = _resolve_path_against_root(canonical_relative)

        if output_resolved != canonical_resolved:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="NON_CANONICAL_OUTPUT_PATH",
                failure_reason=f"Output path {output_resolved} != canonical {canonical_resolved}",
            )

        # Use resolved path for file operations
        full_output_path = output_resolved

        # Verify file exists and is readable
        if not full_output_path.exists():
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="OUTPUT_FILE_MISSING",
                failure_reason=f"Output file does not exist: {full_output_path}",
            )

        if not full_output_path.is_file():
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="OUTPUT_NOT_FILE",
                failure_reason=f"Output path is not a file: {full_output_path}",
            )

        # Compute SHA256 digest
        from ..job_state import compute_output_digest
        try:
            output_digest = compute_output_digest(full_output_path)
        except Exception as e:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="OUTPUT_DIGEST_ERROR",
                failure_reason=f"Failed to compute output digest: {e}",
            )

        # Build output evidence
        output_evidence = {
            "artifact_key": artifact_key,
            "relative_path": output_artifact,
            "digest": output_digest,
            "collected_at": _now_iso(),
        }

        # R10-I1: Return resolved Path (not string)
        return True, recovery_context, output_evidence, full_output_path, output_digest

    # Non-APPROVED result passes through for normal routing
    return True, recovery_context, None, None, None


def _handle_terminal_replay(
    *,
    group_name: str,
    state: dict,
    step: str,
    step_result: StepResult,
    attempt_record: dict,
    current_status: str,
) -> tuple[dict, int]:
    """Handle terminal replay for applied/rejected/failed results.

    Validates identity and returns the stored outcome unchanged.
    """
    # Get stored result based on status
    if current_status == "applied":
        stored_result = attempt_record.get("applied_result", {})
        # Applied identity: status + remark (no reject_code)
        stored_identity = {
            "status": "APPROVED",
            "remark": stored_result.get("remark"),
        }
        incoming_identity = {
            "status": step_result.status,
            "remark": step_result.remark,
            # Omit reject_code for applied comparison
        }
    elif current_status == "rejected":
        stored_result = attempt_record.get("rejected_result", {})
        # Rejected identity: status + remark + reject_code
        stored_identity = {
            "status": "REJECTED",
            "remark": stored_result.get("remark"),
            "reject_code": stored_result.get("reject_code"),
        }
        incoming_identity = {
            "status": step_result.status,
            "remark": step_result.remark,
            "reject_code": step_result.reject_code,
        }
    else:  # failed
        stored_result = attempt_record.get("failed_result", {})
        # Failed identity: original_status + remark (not "failed")
        stored_identity = {
            "status": stored_result.get("original_status", "APPROVED"),
            "remark": stored_result.get("remark"),
        }
        incoming_identity = {
            "status": step_result.status,  # Original APPROVED
            "remark": step_result.remark,
            # Omit failure_reason - it's metadata, not identity
        }

    # Validate identity match
    if incoming_identity != stored_identity:
        return _gate_failure(
            group_name=group_name,
            state=state,
            step=step,
            failure_code="TERMINAL_RESULT_CONFLICT",
            failure_reason=f"Identity mismatch: incoming {incoming_identity} != stored {stored_identity}",
        )

    # Return stored outcome unchanged
    if current_status == "applied":
        # MANDATORY evidence verification for applied
        stored_path = stored_result.get("output_path")
        stored_digest = stored_result.get("output_digest")

        # Evidence MUST be present
        if not stored_path or not stored_digest:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="TERMINAL_EVIDENCE_MISSING",
                failure_reason="Applied result missing required evidence (path or digest)",
            )

        # R20: A16-02 - Unconditional path identity comparison using resolved paths
        incoming_path = step_result.artifacts.get("QWEN_PLAN_FILE") if step_result.artifacts else None
        # Get relative path from evidence for comparison (output_path may be absolute)
        output_evidence = stored_result.get("output_evidence", {})
        relative_path = output_evidence.get("relative_path") if output_evidence else None
        # Use relative_path for comparison if available, otherwise use output_path
        comparison_path = relative_path or stored_path

        # R20: Normalize both UNCONDITIONALLY - None != path is conflict, None == None is match
        stored_normalized = _normalize_optional_path(comparison_path)
        incoming_normalized = _normalize_optional_path(incoming_path)

        if incoming_normalized != stored_normalized:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="TERMINAL_EVIDENCE_CONFLICT",
                failure_reason=f"Path identity conflict: incoming {incoming_normalized!r} != stored {stored_normalized!r}",
            )

        # Verify file exists and is readable
        from .. import runtime_context
        project_root = Path(str(runtime_context.PROJECT_ROOT)).resolve()
        full_path = project_root / stored_path

        if not full_path.exists():
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="TERMINAL_EVIDENCE_MISSING",
                failure_reason=f"Output file does not exist: {stored_path}",
            )

        if not full_path.is_file():
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="TERMINAL_EVIDENCE_INVALID",
                failure_reason=f"Output path is not a file: {stored_path}",
            )

        # Verify current digest matches stored
        from ..job_state import compute_output_digest
        try:
            current_digest = compute_output_digest(full_path)
        except Exception as e:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="TERMINAL_EVIDENCE_UNREADABLE",
                failure_reason=f"Cannot read output file: {e}",
            )

        if current_digest != stored_digest:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="TERMINAL_EVIDENCE_CONFLICT",
                failure_reason=f"Output file changed: digest mismatch (current {current_digest[:8]}... != stored {stored_digest[:8]}...)",
            )

        # All verification passed - return success unchanged
        return state, 0

    elif current_status == "rejected":
        # Return with saved exit_code (may be 1 for intervention)
        exit_code = stored_result.get("exit_code", 1)
        return state, exit_code

    else:  # failed
        # FAILED replay: Validate evidence for IDENTICAL state
        # R16-R5: Handle missing/unreadable output at failure time as identical state
        stored_path = stored_result.get("output_path")
        stored_digest = stored_result.get("output_digest")
        stored_missing = stored_result.get("output_missing", False)
        stored_unreadable = stored_result.get("output_unreadable", False)

        # R16-R7: REQUIRE incoming path identity unconditionally, including both absent
        incoming_path = step_result.artifacts.get("QWEN_PLAN_FILE") if step_result.artifacts else None
        # Get relative path from evidence for comparison (output_path may be absolute)
        output_evidence = stored_result.get("output_evidence", {})
        relative_path = output_evidence.get("relative_path") if output_evidence else None
        # Use relative_path for comparison if available, otherwise use stored_path
        comparison_path = relative_path or stored_path
        # R24: A16-02 - Use same unconditional path resolution as applied branch
        stored_normalized = _normalize_optional_path(comparison_path)
        incoming_normalized = _normalize_optional_path(incoming_path)
        if incoming_normalized != stored_normalized:
            return _gate_failure(
                group_name=group_name,
                state=state,
                step=step,
                failure_code="TERMINAL_EVIDENCE_CONFLICT",
                failure_reason=f"Failed result incoming path {incoming_normalized!r} != stored path {stored_normalized!r}",
            )

        # R16-R5: If output was recorded, verify current state matches stored state
        if stored_path:
            from .. import runtime_context
            project_root = Path(str(runtime_context.PROJECT_ROOT)).resolve()
            full_path = project_root / stored_path

            # R16-R5: Handle three failure-time states: missing, unreadable, or readable
            if stored_missing:
                # File was missing when failure occurred - must still be missing
                if full_path.exists():
                    return _gate_failure(
                        group_name=group_name,
                        state=state,
                        step=step,
                        failure_code="TERMINAL_EVIDENCE_CONFLICT",
                        failure_reason=f"Failed result output file now exists but was missing at failure time: {stored_path}",
                    )
                # File still missing - identical state, allow replay

            elif stored_unreadable:
                # R16-R5: File was unreadable when failure occurred
                # Check if file still exists and is unreadable (identical state)
                if not full_path.exists():
                    return _gate_failure(
                        group_name=group_name,
                        state=state,
                        step=step,
                        failure_code="TERMINAL_EVIDENCE_CONFLICT",
                        failure_reason=f"Failed result output file now missing but was unreadable at failure time: {stored_path}",
                    )
                # R16-R6: Try to read - detect if now readable
                # Keep digest read in narrow try, conflict decision OUTSIDE
                from ..job_state import compute_output_digest
                now_readable = False
                try:
                    compute_output_digest(full_path)
                    now_readable = True
                except Exception:
                    # Still unreadable - identical state
                    pass
                # R16-R6: Conflict decision OUTSIDE the try to avoid swallowing save errors
                if now_readable:
                    return _gate_failure(
                        group_name=group_name,
                        state=state,
                        step=step,
                        failure_code="TERMINAL_EVIDENCE_CONFLICT",
                        failure_reason=f"Failed result output file now readable but was unreadable at failure time: {stored_path}",
                    )

            else:
                # File existed and was readable at failure time - verify it still exists and matches
                if not stored_digest:
                    return _gate_failure(
                        group_name=group_name,
                        state=state,
                        step=step,
                        failure_code="TERMINAL_EVIDENCE_MISSING",
                        failure_reason="Failed result has readable output but missing output_digest",
                    )

                if not full_path.exists():
                    return _gate_failure(
                        group_name=group_name,
                        state=state,
                        step=step,
                        failure_code="TERMINAL_EVIDENCE_CONFLICT",
                        failure_reason=f"Failed result output file now missing but existed at failure time: {stored_path}",
                    )

                if not full_path.is_file():
                    return _gate_failure(
                        group_name=group_name,
                        state=state,
                        step=step,
                        failure_code="TERMINAL_EVIDENCE_INVALID",
                        failure_reason=f"Failed result output path is not a file: {stored_path}",
                    )

                # Verify current digest matches stored
                from ..job_state import compute_output_digest
                try:
                    current_digest = compute_output_digest(full_path)
                except Exception as e:
                    return _gate_failure(
                        group_name=group_name,
                        state=state,
                        step=step,
                        failure_code="TERMINAL_EVIDENCE_UNREADABLE",
                        failure_reason=f"Failed result output file became unreadable: {e}",
                    )

                if current_digest != stored_digest:
                    return _gate_failure(
                        group_name=group_name,
                        state=state,
                        step=step,
                        failure_code="TERMINAL_EVIDENCE_CONFLICT",
                        failure_reason=f"Failed result output file changed: digest mismatch",
                    )

        # Return with exit code 1
        return state, 1


def _validate_refinement_no_op(
    *,
    step_result: StepResult,
    validated_recovery: dict | None = None,
    canonical_path: Path | None = None,
) -> str | None:
    """Validate that refinement is not a no-op (unchanged content).

    Returns None if valid, or "NO_OP_REFINEMENT" if content unchanged.
    """
    if not validated_recovery or not canonical_path:
        return None

    pre_refine_checksum = validated_recovery.get("pre_refine_checksum")
    if not pre_refine_checksum:
        # No checksum to compare - assume it's a real change
        return None

    # Verify file exists
    if not canonical_path.exists():
        return None

    # Compute current file checksum using MD5
    from ..job_state import _md5_file
    try:
        current_checksum = _md5_file(canonical_path)
    except Exception:
        return None

    if current_checksum == pre_refine_checksum:
        # No-op: content unchanged
        return "NO_OP_REFINEMENT"

    return None


def _commit_application_failure_from_baseline(
    *,
    baseline: dict,
    group_name: str,
    attempt_id: str,
    step_result: StepResult,
    failure_reason: str,
    step: str,
    output_digest: str | None = None,
) -> tuple[dict, int]:
    """Commit application failure from clean baseline state.

    Derives failure state from baseline, not from mutated transition.
    """
    # Copy baseline as starting point
    failure_state = copy.deepcopy(baseline)

    # Record failure
    attempt_record = failure_state.get("attempt_records", {}).get(attempt_id, {})

    # R20: A16-02/A16-05 - Resolve and classify output path FIRST
    output_path_raw = None
    if step_result.artifacts and step_result.artifacts.get("QWEN_PLAN_FILE"):
        output_path_raw = str(step_result.artifacts.get("QWEN_PLAN_FILE"))

    computed_digest = output_digest
    output_missing = False
    output_unreadable = False

    if output_path_raw:
        output_resolved = _resolve_path_against_root(output_path_raw)

        # R20: A16-05 - Check file type BEFORE deciding on digest reuse
        if not output_resolved.exists():
            output_missing = True
        elif not output_resolved.is_file():
            # R20: Explicitly reject non-file observations unconditionally
            raise ValueError(
                f"Output path is not a regular file: {output_path_raw}. "
                f"Only missing, unreadable, or readable regular files are supported observations."
            )
        else:
            # R20: File exists and is regular - compute or reuse digest
            if not computed_digest:
                try:
                    from ..job_state import compute_output_digest
                    computed_digest = compute_output_digest(output_resolved)
                except Exception:
                    output_unreadable = True
            # If computed_digest supplied externally, use it

    # Build failed result with ORIGINAL status for identity matching
    # (not derived "failed" status)
    # R16-01: Include output_digest for evidence validation
    # R16-01 follow-up: Include output_missing/output_unreadable for identical replay
    failed_result = {
        "original_status": step_result.status,  # APPROVED - for identity matching
        "remark": step_result.remark,
        "output_path": output_path_raw,  # R20: Use raw path string
        "output_digest": computed_digest,  # R16-01: For replay evidence validation
        "output_missing": output_missing,  # R16-01 follow-up: For identical missing-state replay
        "output_unreadable": output_unreadable,  # R16-01 follow-up: For identical unreadable-state replay
        "failure_reason": failure_reason,  # Metadata, not identity
        "failed_at": _now_iso(),
    }

    # Update attempt record
    if attempt_record:
        attempt_record["status"] = "failed"
        attempt_record["failed_result"] = failed_result

    # Set failure state
    set_last_failure(
        state=failure_state,
        failure_class="HUMAN_RETRY_REQUIRED",
        failure_code="APPLICATION_FAILURE",
        failure_reason=failure_reason,
        failure_source="runner",
        step=step,
    )
    set_job_status(failure_state, "WAITING_FOR_HUMAN_INTERVENTION")
    failure_state["current_step"] = step
    failure_state["pending_intervention_for"] = step

    # Save once (let exceptions propagate)
    # Import job_state module to allow test patching
    from .. import job_state
    job_state.save_job(group_name, failure_state["job_id"], failure_state)
    send_workflow_notification("WAITING_FOR_HUMAN_INTERVENTION", dict(failure_state))

    return failure_state, 1


def _commit_plan_first_terminal_state(
    *,
    group_name: str,
    state: dict,
    attempt_id: str,
    step: str,
    step_result: StepResult,
    output_evidence: dict | None = None,
    output_path: Path | None = None,
    output_digest: str | None = None,
    exit_code: int = 0,
) -> None:
    """Commit terminal state for plan-first workflow.

    Saves once with terminal receipt and completion ownership.
    """
    attempt_record = state.get("attempt_records", {}).get(attempt_id, {})
    if not attempt_record:
        return

    # Build terminal result based on status
    if step_result.status == "APPROVED":
        applied_result = {
            "status": "APPROVED",
            "remark": step_result.remark,
            "output_path": str(output_path) if output_path else None,
            "output_digest": output_digest,
            "output_evidence": output_evidence,
            "applied_at": _now_iso(),
        }
        attempt_record["status"] = "applied"
        attempt_record["applied_result"] = applied_result

        # R10-I2: Record completion ownership
        baseline = attempt_record.get("baseline")
        target_revision = attempt_record.get("target_revision")
        if baseline is not None and target_revision is not None:
            completions = state.setdefault("revision_completions", {})
            completion_key = f"b{baseline}_r{target_revision}"
            completions[completion_key] = {
                "attempt_id": attempt_id,
                "completed_at": _now_iso(),
            }

    elif step_result.status == "REJECTED":
        rejected_result = {
            "status": "REJECTED",
            "remark": step_result.remark,
            "reject_code": step_result.reject_code,
            "exit_code": exit_code,
            "rejected_at": _now_iso(),
        }
        attempt_record["status"] = "rejected"
        attempt_record["rejected_result"] = rejected_result

    # Clear loop context
    state.setdefault("loop_context", {})
    state["loop_context"]["active_attempt_id"] = None

    # Save once (import module for test patching)
    from .. import job_state
    job_state.save_job(group_name, state["job_id"], state)


def _dispatch_plan_first_notifications(
    *,
    group_name: str,
    state: dict,
    step: str,
    step_cfg: dict,
    step_result: StepResult | None = None,
    status: str | None = None,
) -> None:
    """Dispatch notifications after successful commit.

    Called only after save completes.
    Accepts either step_result or status parameter.
    """
    # Determine status from either parameter
    effective_status = status
    if step_result is not None and effective_status is None:
        effective_status = step_result.status

    if effective_status == "APPROVED":
        send_step_notification("STEP_COMPLETED", state, step, step_cfg)
    elif effective_status == "REJECTED":
        send_step_notification("STEP_REJECTED", state, step, step_cfg)


def _validate_owned_recovery_context(
    *,
    attempt_record: dict,
    group_name: str,
    job_id: str,
    baseline: int,
    step: str,
    input_revision: int | None,
    target_revision: int | None,
    group_cfg: dict,
    planning_folder: str | None,
) -> dict | None:
    """Validate that the recovery context is owned by this attempt and is complete.

    Returns the recovery context if valid, None otherwise.

    R16-02: Validates complete producer contract, not just identity fields.
    """
    recovered_context = attempt_record.get("recovered_context")
    if not recovered_context:
        return None

    # R16-02: Empty dict is not valid
    if not any(recovered_context.values()):
        return None

    # Validate identity match
    if recovered_context.get("job_id") != job_id:
        return None
    if recovered_context.get("group_name") != group_name:
        return None
    if recovered_context.get("baseline") != baseline:
        return None
    if recovered_context.get("step") != step:
        return None
    if recovered_context.get("input_revision") != input_revision:
        return None
    if recovered_context.get("target_revision") != target_revision:
        return None

    # R16-02: For refinement, validate complete producer contract
    if step == "refine_plan":
        # active must be exactly True (boolean, not just truthy)
        active = recovered_context.get("active")
        if not isinstance(active, bool) or active is not True:
            return None

        # loop_step must be "codex_review"
        if recovered_context.get("loop_step") != "codex_review":
            return None

        # refine_step must be "refine_plan"
        if recovered_context.get("refine_step") != "refine_plan":
            return None

        # loop_target_artifact must be present and non-empty
        loop_target_artifact = recovered_context.get("loop_target_artifact")
        if not loop_target_artifact or not isinstance(loop_target_artifact, str):
            return None

        # Validate against config if provided
        step_configs = group_cfg.get("step_configs", {})
        codex_review_cfg = step_configs.get("codex_review", {})
        on_reject_refine = codex_review_cfg.get("on_reject_refine", {})
        configured_target = on_reject_refine.get("artifact")
        if configured_target and loop_target_artifact != configured_target:
            return None

        # loop_source_review must be present and non-empty
        loop_source_review = recovered_context.get("loop_source_review")
        if not loop_source_review or not isinstance(loop_source_review, str):
            return None

        # R16-02 follow-up: Validate loop_source_review against canonical path
        if planning_folder and input_revision is not None:
            from ..constants import ARTIFACT_PATH_CODEX_REVIEW
            canonical_review_path = ARTIFACT_PATH_CODEX_REVIEW(planning_folder, input_revision, baseline)
            if loop_source_review != canonical_review_path:
                return None

        # loop_iteration must be a non-negative int (not bool)
        loop_iteration = recovered_context.get("loop_iteration")
        if not isinstance(loop_iteration, int) or isinstance(loop_iteration, bool):
            return None
        if loop_iteration < 0:
            return None

        # pre_refine_checksum must be present and non-empty
        pre_refine_checksum = recovered_context.get("pre_refine_checksum")
        if not pre_refine_checksum or not isinstance(pre_refine_checksum, str):
            return None

    else:
        # R16-R6: For generation, validate inactive snapshot
        # active MUST be exactly False (not missing, not truthy)
        active = recovered_context.get("active")
        if not isinstance(active, bool) or active is not False:
            return None
        # Other loop context fields should not be present for inactive
        inactive_forbidden = ["loop_step", "refine_step", "loop_target_artifact", 
                              "loop_source_review", "loop_iteration", "pre_refine_checksum"]
        for field in inactive_forbidden:
            if recovered_context.get(field) is not None:
                return None

    return recovered_context


def _validate_prepared_eligibility(
    *,
    state: dict,
    group_name: str,
    step: str,
    attempt_id: str,
    baseline: int | None = None,
    input_revision: int | None = None,
    target_revision: int | None = None,
) -> tuple[bool, str | None, dict | None]:
    """Validate eligibility for prepared attempt.

    Returns (is_valid, error_message, recovery_context).
    """
    attempt_record = state.get("attempt_records", {}).get(attempt_id)
    if not attempt_record:
        return False, f"Attempt not found: {attempt_id}", None

    # R20: A16-03 - Validate current_revision is exact int (not bool/float)
    current_revision = state.get("plan_revision", 1)
    if isinstance(current_revision, bool):
        return False, f"plan_revision must be exact int, got bool True", None
    if not isinstance(current_revision, int):
        return False, f"plan_revision must be exact int, got {type(current_revision).__name__}", None

    # R24: A16-03 - Validate current_revision is positive
    if current_revision <= 0:
        return False, f"plan_revision must be positive int, got {current_revision}", None

    # R20: A16-03 - Validate requirements_baseline is exact int (not bool/float)
    current_baseline = state.get("requirements_baseline", 1)
    if isinstance(current_baseline, bool):
        return False, f"requirements_baseline must be exact int, got bool True", None
    if not isinstance(current_baseline, int):
        return False, f"requirements_baseline must be exact int, got {type(current_baseline).__name__}", None

    # R24: A16-03 - Validate requirements_baseline is positive
    if current_baseline <= 0:
        return False, f"requirements_baseline must be positive int, got {current_baseline}", None

    # R24: A16-03 - Record baseline MUST be exact positive int (unconditional)
    record_baseline = attempt_record.get("baseline")
    if record_baseline is None:
        return False, "record baseline is required", None
    if isinstance(record_baseline, bool):
        return False, f"record baseline must be exact int, got bool True", None
    if not isinstance(record_baseline, int):
        return False, f"record baseline must be exact int, got {type(record_baseline).__name__}", None
    if record_baseline <= 0:
        return False, f"record baseline must be positive int, got {record_baseline}", None
    if record_baseline != current_baseline:
        return False, f"record baseline {record_baseline} != current baseline {current_baseline}", None

    # F2: Validate baseline matches current state (caller argument)
    if baseline is not None and current_baseline is not None and baseline != current_baseline:
        return False, f"Attempt baseline {baseline} != current baseline {current_baseline}", None

    # Validate revision formula
    from ..job_state import validate_revision_formula

    valid, error = validate_revision_formula(
        step=step,
        input_revision=input_revision,
        target_revision=target_revision,
        current_revision=current_revision,
    )

    if not valid:
        return False, error, None

    # Build recovery context
    recovery_context = attempt_record.get("recovered_context")

    return True, None, recovery_context


def _route_plan_first_approved(
    *,
    group_name: str,
    group_cfg: dict,
    original_state: dict,
    baseline: dict,
    transition: dict,
    step: str,
    step_cfg: dict,
    step_result: StepResult,
    coder_used: str,
    validation: tuple,
) -> tuple[dict, int]:
    """Route plan-first APPROVED result with terminal commit.

    Args:
        original_state: The original caller state (untouched, for reference)
        baseline: Deep copy of state before any mutations (for failure recovery)
        transition: Deep copy with dictionaries initialized (for routing)
    """
    # Unpack validation tuple
    _, recovery_context, output_evidence, output_path, output_digest = validation
    attempt_id = step_result.attempt_id

    # Install recovery context into transition
    if recovery_context:
        transition.setdefault("loop_context", {})
        transition["loop_context"].update(recovery_context)

    # Get dictionaries from transition (already initialized by caller)
    transition_reject_counts = transition["reject_counts"]
    transition_artifacts = transition["artifacts"]
    transition_auto_retry_counts = transition["auto_retry_count_by_step"]
    transition_human_retry_counts = transition["human_retry_count_by_step"]

    # Route on transition with skip_save and defer_notifications
    routed_transition, exit_code = _route_approved(
        group_name=group_name,
        group_cfg=group_cfg,
        state=transition,
        step=step,
        step_cfg=step_cfg,
        step_result=step_result,
        coder_used=coder_used,
        reject_counts=transition_reject_counts,
        artifacts=transition_artifacts,
        auto_retry_counts=transition_auto_retry_counts,
        human_retry_counts=transition_human_retry_counts,
        skip_save=True,
        defer_notifications=True,
    )

    # Check application result
    if exit_code != 0:
        # Application failure - derive from baseline (original_state untouched)
        return _commit_application_failure_from_baseline(
            baseline=baseline,
            group_name=group_name,
            attempt_id=attempt_id,
            step_result=step_result,
            failure_reason="Application routing failed",
            step=step,
        )

    # Success - commit terminal state from routed_transition
    _commit_plan_first_terminal_state(
        group_name=group_name,
        state=routed_transition,
        attempt_id=attempt_id,
        step=step,
        step_result=step_result,
        output_evidence=output_evidence,
        output_path=output_path,
        output_digest=output_digest,
        exit_code=exit_code,
    )

    # Dispatch notifications
    _dispatch_plan_first_notifications(
        group_name=group_name,
        state=routed_transition,
        step=step,
        step_cfg=step_cfg,
        status="APPROVED",
    )

    return routed_transition, exit_code


def _route_plan_first_rejected(
    *,
    group_name: str,
    group_cfg: dict,
    original_state: dict,
    baseline: dict,
    transition: dict,
    step: str,
    step_cfg: dict,
    step_result: StepResult,
    coder_used: str,
    max_rejects: int,
    validation: tuple,
) -> tuple[dict, int]:
    """Route plan-first REJECTED result with terminal commit.

    Args:
        original_state: The original caller state (untouched, for reference)
        baseline: Deep copy of state before any mutations (for failure recovery)
        transition: Deep copy with dictionaries initialized (for routing)
    """
    # Unpack validation tuple
    _, recovery_context, _, _, _ = validation
    attempt_id = step_result.attempt_id

    # Install recovery context into transition
    if recovery_context:
        transition.setdefault("loop_context", {})
        transition["loop_context"].update(recovery_context)

    # Handle rejection accounting on transition
    current_count = int(transition.get("reject_counts", {}).get(step, 0)) + 1
    if "reject_counts" not in transition:
        transition["reject_counts"] = {}
    transition["reject_counts"][step] = current_count

    # Set failure state for intervention
    set_last_failure(
        state=transition,
        failure_class="HUMAN_RETRY_REQUIRED",
        failure_code=step_result.reject_code or "MODEL_REJECTED",
        failure_reason=step_result.remark,
        failure_source="model",
        step=step,
    )
    append_failure_history(
        state=transition,
        step=step,
        failure_class="HUMAN_RETRY_REQUIRED",
        failure_code=step_result.reject_code or "MODEL_REJECTED",
        failure_source="model",
    )

    set_job_status(transition, "WAITING_FOR_HUMAN_INTERVENTION")
    transition["current_step"] = step
    transition["pending_intervention_for"] = step

    # Commit terminal state (this saves)
    _commit_plan_first_terminal_state(
        group_name=group_name,
        state=transition,
        attempt_id=attempt_id,
        step=step,
        step_result=step_result,
        exit_code=1,  # Rejection = intervention required
    )

    # Dispatch notifications
    _dispatch_plan_first_notifications(
        group_name=group_name,
        state=transition,
        step=step,
        step_cfg=step_cfg,
        status="REJECTED",
    )

    return transition, 1
