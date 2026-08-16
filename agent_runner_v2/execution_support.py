from __future__ import annotations

import json

from .exceptions import ArtifactMissingError, MetaJsonInvalidError, MetaJsonMissingError


def build_failure_envelope(
    *, failure_class: str, failure_code: str, failure_reason: str, failure_source: str,
) -> dict[str, str]:
    return {
        "failure_class": failure_class,
        "failure_code": failure_code,
        "failure_reason": failure_reason,
        "failure_source": failure_source,
    }


def default_usage_summary() -> dict[str, int | float | None]:
    return {
        "steps_with_usage": 0,
        "steps_without_usage": 0,
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "cost": None,
        "duration_ms": None,
    }


def looks_like_transient_error(message: str) -> bool:
    hints = (
        "connection error",
        "fetch failed",
        "timed out",
        "timeout",
        "temporar",
        "rate limit",
        "429",
        "service unavailable",
        "api error",
        "network error",
    )
    return any(hint in message.lower() for hint in hints)


def classify_pre_run_failure(exc: Exception) -> dict[str, str]:
    message = str(exc).strip()
    lowered = message.lower()
    if looks_like_transient_error(message):
        return build_failure_envelope(
            failure_class="AUTO_RETRYABLE",
            failure_code="TRANSIENT_PRE_RUN_FAILURE",
            failure_reason=message,
            failure_source="runner",
        )
    if isinstance(exc, FileNotFoundError):
        code = "MISSING_REQUIRED_FILE"
        if "prompt file not found" in lowered or "missing static reference file" in lowered:
            code = "MISSING_TEMPLATE_OR_REFERENCE"
        elif "missing required job init input" in lowered or "missing required input artifact" in lowered:
            code = "MISSING_INPUT_ARTIFACT"
        elif "job state not found" in lowered:
            code = "MISSING_JOB_STATE"
        return build_failure_envelope(
            failure_class="HUMAN_RETRY_REQUIRED",
            failure_code=code,
            failure_reason=message,
            failure_source="runner",
        )
    if isinstance(exc, MetaJsonMissingError):
        return build_failure_envelope(
            failure_class="AUTO_RETRYABLE",
            failure_code="META_JSON_MISSING",
            failure_reason=message,
            failure_source="runner",
        )
    if isinstance(exc, MetaJsonInvalidError):
        return build_failure_envelope(
            failure_class="AUTO_RETRYABLE",
            failure_code="META_JSON_INVALID",
            failure_reason=message,
            failure_source="runner",
        )
    if isinstance(exc, ArtifactMissingError):
        return build_failure_envelope(
            failure_class="HUMAN_RETRY_REQUIRED",
            failure_code="ARTIFACT_MISSING",
            failure_reason=message,
            failure_source="validator",
        )
    if isinstance(exc, json.JSONDecodeError):
        return build_failure_envelope(
            failure_class="FATAL",
            failure_code="CORRUPTED_JOB_STATE",
            failure_reason=message,
            failure_source="runner",
        )
    if isinstance(exc, ValueError):
        if any(token in lowered for token in ("coder executable not found", "is not allowed for step", "no coder specified")):
            code = "UNKNOWN_CODER" if "coder executable not found" in lowered else "INVALID_RUNNER_CONFIGURATION"
            return build_failure_envelope(
                failure_class="HUMAN_RETRY_REQUIRED",
                failure_code=code,
                failure_reason=message,
                failure_source="runner",
            )
        if any(
            token in lowered
            for token in (
                "waiting for human approval",
                "waiting for human intervention",
                "multiple active jobs match",
                "has reached max rejects",
                "is not defined for template group",
            )
        ):
            if "waiting for human approval" in lowered:
                code = "WAITING_FOR_HUMAN_APPROVAL"
            elif "multiple active jobs match" in lowered:
                code = "MULTIPLE_ACTIVE_JOBS"
            elif "has reached max rejects" in lowered:
                code = "MAX_REJECTS_REACHED"
            else:
                code = "PRE_RUN_INTERVENTION_REQUIRED"
            return build_failure_envelope(
                failure_class="HUMAN_RETRY_REQUIRED",
                failure_code=code,
                failure_reason=message,
                failure_source="runner",
            )
    return build_failure_envelope(
        failure_class="FATAL",
        failure_code="PRE_RUN_FAILURE",
        failure_reason=message,
        failure_source="runner",
    )
