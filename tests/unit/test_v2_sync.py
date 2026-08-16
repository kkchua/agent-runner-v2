"""Tests for V2 sync adapter — config resolution, outcome payload, V2 client."""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent_runner_v2.v2.sync import (
    build_v2_outcome_payload,
    is_v2_enabled,
    resolve_v2_backend_url,
    sync_outcome_v2,
)


class TestResolveV2BackendUrl:
    def test_returns_none_when_not_configured(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("agent_runner_v2.v2.sync.load_runner_config", return_value={}):
                os.environ.pop("AGENT_RUNNER_V2_BACKEND_URL", None)
                assert resolve_v2_backend_url() is None

    def test_returns_url_from_env_var(self):
        with patch.dict(os.environ, {"AGENT_RUNNER_V2_BACKEND_URL": "http://localhost:8200"}):
            assert resolve_v2_backend_url() == "http://localhost:8200"

    def test_returns_url_from_config(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("AGENT_RUNNER_V2_BACKEND_URL", None)
            with patch("agent_runner_v2.v2.sync.load_runner_config", return_value={
                "v2_backend_url": "http://localhost:8200",
            }):
                assert resolve_v2_backend_url() == "http://localhost:8200"

    def test_env_var_takes_priority_over_config(self):
        with patch.dict(os.environ, {"AGENT_RUNNER_V2_BACKEND_URL": "http://env:8200"}):
            with patch("agent_runner_v2.v2.sync.load_runner_config", return_value={
                "v2_backend_url": "http://config:8200",
            }):
                assert resolve_v2_backend_url() == "http://env:8200"

    def test_empty_string_treated_as_none(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("AGENT_RUNNER_V2_BACKEND_URL", None)
            with patch("agent_runner_v2.v2.sync.load_runner_config", return_value={
                "v2_backend_url": "",
            }):
                assert resolve_v2_backend_url() is None

    def test_is_v2_enabled_false_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("AGENT_RUNNER_V2_BACKEND_URL", None)
            with patch("agent_runner_v2.v2.sync.load_runner_config", return_value={}):
                assert is_v2_enabled() is False

    def test_is_v2_enabled_true_when_configured(self):
        with patch.dict(os.environ, {"AGENT_RUNNER_V2_BACKEND_URL": "http://localhost:8200"}):
            assert is_v2_enabled() is True


class TestBuildV2OutcomePayload:
    def test_approved_outcome(self):
        result = {"status": "APPROVED", "outcome": "approved"}
        state = {"artifacts": {"DOC_A": "/tmp/doc_a.md"}}

        payload = build_v2_outcome_payload(step_result=result, state=state)

        assert payload["outcome"] == "approved"
        assert payload["artifacts"] == {"DOC_A": "/tmp/doc_a.md"}
        assert "failure_class" not in payload

    def test_rejected_outcome_with_failure_class(self):
        result = {
            "status": "REJECTED",
            "outcome": "rejected",
            "failure_class": "AUTO_RETRYABLE",
            "remark": "API rate limit exceeded",
        }
        state = {}

        payload = build_v2_outcome_payload(step_result=result, state=state)

        assert payload["outcome"] == "rejected"
        assert payload["failure_class"] == "AUTO_RETRYABLE"
        assert payload["error_message"] == "API rate limit exceeded"

    def test_failed_outcome(self):
        result = {"status": "FAILED", "outcome": "failed", "remark": "Coder crashed"}
        state = {"last_failure_reason": "Coder crashed"}

        payload = build_v2_outcome_payload(step_result=result, state=state)

        assert payload["outcome"] == "failed"
        assert payload["error_message"] == "Coder crashed"

    def test_artifacts_filter_empty_values(self):
        result = {"status": "APPROVED"}
        state = {
            "artifacts": {
                "DOC_A": "/tmp/doc_a.md",
                "EMPTY": "",
                "NONE": None,
                "WHITESPACE": "   ",
            },
        }

        payload = build_v2_outcome_payload(step_result=result, state=state)

        assert payload["artifacts"] == {"DOC_A": "/tmp/doc_a.md"}

    def test_review_state_included(self):
        result = {"status": "APPROVED"}
        state = {
            "review_state": {
                "final_decision": "APPROVED",
                "remark": "Looks good",
            },
        }

        payload = build_v2_outcome_payload(step_result=result, state=state)

        assert payload["review"]["decision"] == "APPROVED"
        assert payload["review"]["remark"] == "Looks good"

    def test_pending_review_state_excluded(self):
        result = {"status": "APPROVED"}
        state = {
            "review_state": {
                "final_decision": "PENDING",
            },
        }

        payload = build_v2_outcome_payload(step_result=result, state=state)

        assert "review" not in payload

    def test_usage_summary_included(self):
        result = {"status": "APPROVED"}
        state = {
            "usage_summary": {"input_tokens": 5000, "output_tokens": 2000},
        }

        payload = build_v2_outcome_payload(step_result=result, state=state)

        assert payload["usage_summary"] == {"input_tokens": 5000, "output_tokens": 2000}

    def test_control_class_fallback(self):
        result = {"status": "REJECTED", "control_class": "HUMAN_RETRY_REQUIRED"}
        state = {}

        payload = build_v2_outcome_payload(step_result=result, state=state)

        assert payload["failure_class"] == "HUMAN_RETRY_REQUIRED"


class TestV2BackendClient:
    def test_import_succeeds(self):
        from agent_runner_v2.v2.backend_client import V2BackendClient
        client = V2BackendClient("http://localhost:8200")
        assert client.base_url == "http://localhost:8200"
        assert client.timeout_seconds == 30

    def test_url_construction(self):
        from agent_runner_v2.v2.backend_client import V2BackendClient
        client = V2BackendClient("http://localhost:8200")
        assert client._url("/api/runs") == "http://localhost:8200/api/runs"
        assert client._url("/api/runs", {"status": "active"}) == "http://localhost:8200/api/runs?status=active"

    def test_url_trailing_slash_stripped(self):
        from agent_runner_v2.v2.backend_client import V2BackendClient
        client = V2BackendClient("http://localhost:8200/")
        assert client._url("/api/runs") == "http://localhost:8200/api/runs"


class TestSyncOutcomeV2Retry:
    def test_retries_then_succeeds(self):
        """Transient 404 (claim commit still in flight) must be retried."""
        calls = {"count": 0}

        class FakeClient:
            def __init__(self, base_url, **kwargs):
                self.base_url = base_url

            def report_outcome(self, **kwargs):
                calls["count"] += 1
                if calls["count"] < 3:
                    raise RuntimeError(
                        "V2 backend request failed: POST /api/runs/step-runs/sr-1/outcome "
                        'status=404 body={"detail":"Step run sr-1 not found"}'
                    )
                return {"run_status": "PENDING", "current_step": "next_step"}

        with patch("agent_runner_v2.v2.backend_client.V2BackendClient", FakeClient):
            result = sync_outcome_v2(
                backend_url="http://localhost:8200",
                step_run_id="sr-1",
                step_result={"status": "APPROVED"},
                state={},
                max_attempts=3,
                backoff_base=0,
            )

        assert calls["count"] == 3
        assert result["run_status"] == "PENDING"
        assert result["current_step"] == "next_step"

    def test_exhausts_retries_and_raises(self):
        class FakeClient:
            def __init__(self, base_url, **kwargs):
                self.base_url = base_url

            def report_outcome(self, **kwargs):
                raise RuntimeError("always failing")

        with patch("agent_runner_v2.v2.backend_client.V2BackendClient", FakeClient):
            with pytest.raises(RuntimeError, match="always failing"):
                sync_outcome_v2(
                    backend_url="http://localhost:8200",
                    step_run_id="sr-1",
                    step_result={"status": "APPROVED"},
                    state={},
                    max_attempts=2,
                    backoff_base=0,
                )

    def test_succeeds_on_first_attempt(self):
        class FakeClient:
            def __init__(self, base_url, **kwargs):
                self.base_url = base_url

            def report_outcome(self, **kwargs):
                return {"run_status": "COMPLETED"}

        with patch("agent_runner_v2.v2.backend_client.V2BackendClient", FakeClient):
            result = sync_outcome_v2(
                backend_url="http://localhost:8200",
                step_run_id="sr-1",
                step_result={"status": "APPROVED"},
                state={},
            )

        assert result["run_status"] == "COMPLETED"
