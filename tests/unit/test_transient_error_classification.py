"""Unit tests for transient error classification in workflow_router.

Verifies that _looks_like_transient_error and _classify_model_rejection
correctly distinguish between transient (retryable) and permanent (non-retryable)
errors — especially the HTTP 400 vs 503 distinction and partial-failure remarks
from concurrent action steps.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agent_runner_v2.v2.workflow_router import (
    _classify_model_rejection,
    _looks_like_transient_error,
)


# ---------------------------------------------------------------------------
# _looks_like_transient_error
# ---------------------------------------------------------------------------

class TestLooksLikeTransientError:
    """Pure-logic tests for the transient-error hint matcher."""

    # --- True: genuinely transient signals ---

    @pytest.mark.parametrize("message", [
        "Connection error: refused",
        "fetch failed for https://api.example.com/v1",
        "Request timed out after 30s",
        "timeout waiting for response",
        "Service temporarily unavailable",
        "HTTP 429 Too Many Requests",
        "503 Service Unavailable",
        "network error: DNS resolution failed",
    ])
    def test_transient_signals_return_true(self, message: str) -> None:
        assert _looks_like_transient_error(message) is True

    # --- False: retry exhaustion indicators ---

    @pytest.mark.parametrize("message", [
        "Max retries (5) exhausted. Last error: HTTP 503",
        "retries exhausted after 3 attempts",
        "max attempts reached for video generation",
        "attempts exhausted: could not download after 10 tries",
        "retry limit reached",
        "retry quota exceeded",
    ])
    def test_exhaustion_indicators_return_false(self, message: str) -> None:
        assert _looks_like_transient_error(message) is False

    # --- False: partial-failure aggregate results (the bug fix) ---

    @pytest.mark.parametrize("message", [
        "Partial failure: 25/36 PNG files succeeded, 11 errors.",
        "Partial failure: 34/36 PNG files succeeded, 2 errors. Details: API error - 400 Client Error",
        "Partial success: 30 of 36 items completed",
    ])
    def test_partial_failure_indicators_return_false(self, message: str) -> None:
        assert _looks_like_transient_error(message) is False

    # --- False: "api error" with 400 is no longer matched (was the bug) ---

    def test_api_error_400_not_transient(self) -> None:
        remark = (
            "Partial failure: 25/36 PNG files succeeded, 11 errors. "
            "Details: ugc_c1615683.png: API error - 400 Client Error: "
            "Bad Request for url: https://apihub.agnes-ai.com/v1/videos"
        )
        assert _looks_like_transient_error(remark) is False

    def test_bare_400_error_not_transient(self) -> None:
        assert _looks_like_transient_error("400 Client Error: Bad Request") is False

    # --- False: unrelated messages ---

    @pytest.mark.parametrize("message", [
        "Step completed successfully",
        "Artifact missing: review.md not found",
        "Schema validation failed",
        "",
    ])
    def test_unrelated_messages_return_false(self, message: str) -> None:
        assert _looks_like_transient_error(message) is False


# ---------------------------------------------------------------------------
# _classify_model_rejection
# ---------------------------------------------------------------------------

class TestClassifyModelRejection:
    """Verify routing classification for REJECTED step results."""

    def _make_result(self, *, remark: str, reject_code: str | None = None) -> MagicMock:
        result = MagicMock()
        result.status = "REJECTED"
        result.remark = remark
        result.reject_code = reject_code
        return result

    def test_partial_failure_with_api_error_400_is_human_retry(self) -> None:
        """The exact scenario from the agnes_gen_video_v1 bug."""
        remark = (
            "Partial failure: 25/36 PNG files succeeded, 11 errors. "
            "Details: ugc_c1615683.png: API error - 400 Client Error: Bad Request"
        )
        result = self._make_result(remark=remark, reject_code="VIDEO_GEN_PARTIAL_FAILURE")
        failure_class, failure_code, failure_source = _classify_model_rejection(result)

        assert failure_class == "HUMAN_RETRY_REQUIRED"
        assert failure_code == "VIDEO_GEN_PARTIAL_FAILURE"
        assert failure_source == "model"

    def test_transient_connection_error_is_auto_retryable(self) -> None:
        result = self._make_result(
            remark="Connection error: could not reach https://api.example.com",
            reject_code="API_FAILURE",
        )
        failure_class, _, _ = _classify_model_rejection(result)
        assert failure_class == "AUTO_RETRYABLE"

    def test_service_unavailable_is_auto_retryable(self) -> None:
        result = self._make_result(
            remark="503 Service Unavailable — try again later",
            reject_code="API_FAILURE",
        )
        failure_class, _, _ = _classify_model_rejection(result)
        assert failure_class == "AUTO_RETRYABLE"

    def test_rate_limit_is_auto_retryable(self) -> None:
        result = self._make_result(
            remark="HTTP 429 Too Many Requests — rate limit exceeded",
            reject_code="RATE_LIMITED",
        )
        failure_class, _, _ = _classify_model_rejection(result)
        assert failure_class == "AUTO_RETRYABLE"

    def test_approval_missing_is_human_retry(self) -> None:
        result = self._make_result(
            remark="Step pending human approval",
            reject_code="PENDING_APPROVAL",
        )
        failure_class, _, _ = _classify_model_rejection(result)
        assert failure_class == "HUMAN_RETRY_REQUIRED"

    def test_forbidden_is_fatal(self) -> None:
        result = self._make_result(
            remark="Operation forbidden by policy",
            reject_code="POLICY_BLOCK",
        )
        failure_class, _, _ = _classify_model_rejection(result)
        assert failure_class == "FATAL"

    def test_unknown_rejection_is_human_retry(self) -> None:
        result = self._make_result(
            remark="Something went wrong with the output",
            reject_code="UNKNOWN",
        )
        failure_class, _, _ = _classify_model_rejection(result)
        assert failure_class == "HUMAN_RETRY_REQUIRED"
