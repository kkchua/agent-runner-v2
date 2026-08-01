"""V2 sync adapter — outcome-only sync and config resolution.

Provides:
- resolve_v2_backend_url(): Check if v2 mode is enabled
- build_v2_outcome_payload(): Build outcome-only payload for V2 backend
- sync_outcome_v2(): Send outcome to V2 backend and return routing decision
"""
from __future__ import annotations

import os
from typing import Any

from .config_loader import load_runner_config


def resolve_v2_backend_url() -> str | None:
    """Resolve the V2 backend URL from config or environment.

    Returns the V2 backend URL if configured, None otherwise.
    Priority: env var > config.json > None
    """
    env_url = os.environ.get("AGENT_RUNNER_V2_BACKEND_URL", "").strip()
    if env_url:
        return env_url

    config = load_runner_config()
    config_url = str(config.get("v2_backend_url") or "").strip()
    if config_url:
        return config_url

    return None


def is_v2_enabled() -> bool:
    """Return True if V2 backend is configured and should be used."""
    return resolve_v2_backend_url() is not None


def build_v2_outcome_payload(
    *,
    step_result: dict[str, Any],
    state: dict[str, Any],
) -> dict[str, Any]:
    """Build an outcome-only payload for the V2 backend.

    Unlike the old sync payload which includes run_status and next_step_name
    (computed by the CLI), this payload only reports what happened.
    The V2 backend computes the next state via its state machine.
    """
    outcome = str(step_result.get("outcome") or step_result.get("status") or "approved").lower()

    # Map step result status to V2 outcome
    if outcome in ("approved", "completed"):
        v2_outcome = "approved"
    elif outcome in ("rejected",):
        v2_outcome = "rejected"
    else:
        v2_outcome = "failed"

    payload: dict[str, Any] = {"outcome": v2_outcome}

    # Failure classification (CLI owns this — backend trusts it)
    failure_class = step_result.get("failure_class") or step_result.get("control_class")
    if failure_class:
        payload["failure_class"] = str(failure_class).upper()

    # Artifacts from job state
    artifacts_raw = state.get("artifacts") or {}
    artifacts = {}
    for key, path in artifacts_raw.items():
        if path and isinstance(path, str) and path.strip():
            artifacts[key] = path.strip()
    if artifacts:
        payload["artifacts"] = artifacts

    # Review state
    review_state = state.get("review_state") or {}
    review_decision = review_state.get("final_decision") or review_state.get("review_decision")
    if review_decision and str(review_decision).upper() != "PENDING":
        payload["review"] = {
            "decision": str(review_decision),
            "remark": review_state.get("remark") or step_result.get("remark"),
        }

    # Error message
    error_msg = step_result.get("remark") or state.get("last_failure_reason")
    if error_msg:
        payload["error_message"] = str(error_msg)

    # Usage summary
    usage = state.get("usage_summary")
    if usage:
        payload["usage_summary"] = usage

    return payload


def sync_outcome_v2(
    *,
    backend_url: str,
    step_run_id: str,
    step_result: dict[str, Any],
    state: dict[str, Any],
) -> dict[str, Any]:
    """Send outcome to V2 backend and return the routing decision.

    Returns the backend response which includes:
    - run_status: the new status computed by the state machine
    - current_step: the next step to execute
    - action_requested: any pending action
    """
    from .v2_backend_client import V2BackendClient

    client = V2BackendClient(backend_url)
    payload = build_v2_outcome_payload(step_result=step_result, state=state)

    return client.report_outcome(
        step_run_id=step_run_id,
        outcome=payload["outcome"],
        failure_class=payload.get("failure_class"),
        artifacts=payload.get("artifacts"),
        review=payload.get("review"),
        error_message=payload.get("error_message"),
        usage_summary=payload.get("usage_summary"),
    )
