"""Unit tests for V2 backend_client module.

Tests URL construction, payload building, HTTP error handling,
and all API methods. Mocks urllib to avoid real HTTP calls.
"""
from __future__ import annotations

import io
import json
from unittest.mock import MagicMock, patch

import pytest

from agent_runner_v2.v2.backend_client import V2BackendClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_response(body: dict | list | str = "{}", status: int = 200):
    """Create a mock urllib response."""
    if isinstance(body, (dict, list)):
        data = json.dumps(body).encode("utf-8")
    else:
        data = body.encode("utf-8")
    resp = MagicMock()
    resp.read.return_value = data
    resp.status = status
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def _make_client(url: str = "http://localhost:8200") -> V2BackendClient:
    return V2BackendClient(base_url=url)


# ---------------------------------------------------------------------------
# URL construction
# ---------------------------------------------------------------------------

class TestUrlConstruction:
    def test_basic_path(self):
        c = _make_client("http://localhost:8200")
        assert c._url("/api/workers/w1") == "http://localhost:8200/api/workers/w1"

    def test_strips_trailing_slash(self):
        c = _make_client("http://localhost:8200/")
        assert c._url("/api/workers/w1") == "http://localhost:8200/api/workers/w1"

    def test_with_query_params(self):
        c = _make_client()
        url = c._url("/api/runs", query={"status": "running", "worker_id": "w1"})
        assert "status=running" in url
        assert "worker_id=w1" in url
        assert "?" in url

    def test_empty_query_omitted(self):
        c = _make_client()
        url = c._url("/api/runs", query=None)
        assert "?" not in url


# ---------------------------------------------------------------------------
# _request error handling
# ---------------------------------------------------------------------------

class TestRequestErrorHandling:
    def test_http_error_raises_runtime_error(self):
        from urllib.error import HTTPError
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.side_effect = HTTPError(
                url="http://localhost:8200/api/workers/w1",
                code=404,
                msg="Not Found",
                hdrs=MagicMock(),
                fp=io.BytesIO(b'{"detail":"not found"}'),
            )
            with pytest.raises(RuntimeError, match="status=404"):
                c._request("GET", "/api/workers/w1")

    def test_url_error_raises_runtime_error(self):
        from urllib.error import URLError
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.side_effect = URLError("Connection refused")
            with pytest.raises(RuntimeError, match="Connection refused"):
                c._request("GET", "/api/workers/w1")

    def test_empty_body_returns_empty_dict(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response("")
            result = c._request("GET", "/api/workers/w1")
        assert result == {}

    def test_json_body_parsed(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({"worker_id": "w1", "status": "active"})
            result = c._request("GET", "/api/workers/w1")
        assert result["worker_id"] == "w1"
        assert result["status"] == "active"


# ---------------------------------------------------------------------------
# register_worker
# ---------------------------------------------------------------------------

class TestRegisterWorker:
    def test_payload(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.register_worker(worker_id="w1", worker_label="dev", capabilities={"mode": ["execute"]})
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["worker_id"] == "w1"
        assert body["worker_label"] == "dev"
        assert body["capabilities"] == {"mode": ["execute"]}

    def test_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.register_worker(worker_id="w1")
            req = mock_open.call_args[0][0]
        assert req.full_url == "http://localhost:8200/api/workers/register"
        assert req.get_method() == "POST"


# ---------------------------------------------------------------------------
# get_worker
# ---------------------------------------------------------------------------

class TestGetWorker:
    def test_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({"worker_id": "w1", "status": "active"})
            c.get_worker(worker_id="w1")
            req = mock_open.call_args[0][0]
        assert req.full_url == "http://localhost:8200/api/workers/w1"
        assert req.get_method() == "GET"

    def test_returns_worker_dict(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({
                "worker_id": "w1",
                "status": "active",
                "label": "dev-worker",
                "capabilities": {"mode": ["execute-step-daemon"]},
            })
            result = c.get_worker(worker_id="w1")
        assert result["worker_id"] == "w1"
        assert result["status"] == "active"
        assert result["label"] == "dev-worker"

    def test_raises_on_not_found(self):
        from urllib.error import HTTPError
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.side_effect = HTTPError(
                url="http://localhost:8200/api/workers/unknown",
                code=404,
                msg="Not Found",
                hdrs=MagicMock(),
                fp=io.BytesIO(b'{"detail":"worker not found"}'),
            )
            with pytest.raises(RuntimeError, match="status=404"):
                c.get_worker(worker_id="unknown")


# ---------------------------------------------------------------------------
# heartbeat
# ---------------------------------------------------------------------------

class TestHeartbeat:
    def test_minimal_payload(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.heartbeat(worker_id="w1")
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["status"] == "idle"
        assert "current_run_id" not in body

    def test_busy_with_current_run(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({"commands": []})
            c.heartbeat(worker_id="w1", status="busy", current_run_id="r1", current_step_run_id="sr1")
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["status"] == "busy"
        assert body["current_run_id"] == "r1"
        assert body["current_step_run_id"] == "sr1"

    def test_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.heartbeat(worker_id="w1")
            req = mock_open.call_args[0][0]
        assert req.full_url == "http://localhost:8200/api/workers/w1/heartbeat"
        assert req.get_method() == "POST"


# ---------------------------------------------------------------------------
# claim_work
# ---------------------------------------------------------------------------

class TestClaimWork:
    def test_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({"work_type": "IDLE"})
            c.claim_work(worker_id="w1")
            req = mock_open.call_args[0][0]
        assert req.full_url == "http://localhost:8200/api/workers/w1/claim"
        assert req.get_method() == "POST"

    def test_returns_work_type(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({
                "work_type": "EXECUTE_STEP",
                "run": {"run_id": "r1"},
                "step_run": {"step_run_id": "sr1"},
            })
            result = c.claim_work(worker_id="w1")
        assert result["work_type"] == "EXECUTE_STEP"
        assert result["run"]["run_id"] == "r1"


# ---------------------------------------------------------------------------
# report_outcome
# ---------------------------------------------------------------------------

class TestReportOutcome:
    def test_minimal_payload(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.report_outcome(step_run_id="sr1", outcome="approved")
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["outcome"] == "approved"
        assert "failure_class" not in body
        assert "artifacts" not in body

    def test_all_fields(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.report_outcome(
                step_run_id="sr1",
                outcome="failed",
                failure_class="HUMAN_RETRY_REQUIRED",
                artifacts={"OUTPUT": "/path/to/output.md"},
                review={"decision": "rejected", "reason": "bad quality"},
                error_message="Step failed",
                usage_summary={"tokens": 1000},
                job_dir="/jobs/wf1/job1",
            )
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["outcome"] == "failed"
        assert body["failure_class"] == "HUMAN_RETRY_REQUIRED"
        assert body["artifacts"] == {"OUTPUT": "/path/to/output.md"}
        assert body["review"]["decision"] == "rejected"
        assert body["error_message"] == "Step failed"
        assert body["job_dir"] == "/jobs/wf1/job1"

    def test_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.report_outcome(step_run_id="sr1", outcome="approved")
            req = mock_open.call_args[0][0]
        assert req.full_url == "http://localhost:8200/api/runs/step-runs/sr1/outcome"
        assert req.get_method() == "POST"


# ---------------------------------------------------------------------------
# get_run
# ---------------------------------------------------------------------------

class TestGetRun:
    def test_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({"run": {"id": "r1"}})
            c.get_run(run_id="r1")
            req = mock_open.call_args[0][0]
        assert req.full_url == "http://localhost:8200/api/runs/r1"
        assert req.get_method() == "GET"


# ---------------------------------------------------------------------------
# list_runs
# ---------------------------------------------------------------------------

class TestListRuns:
    def test_no_filters(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response([])
            c.list_runs()
            req = mock_open.call_args[0][0]
        assert "?" not in req.full_url

    def test_with_status(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response([])
            c.list_runs(status="running")
            req = mock_open.call_args[0][0]
        assert "status=running" in req.full_url

    def test_with_worker_id(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response([])
            c.list_runs(worker_id="w1")
            req = mock_open.call_args[0][0]
        assert "worker_id=w1" in req.full_url


# ---------------------------------------------------------------------------
# request_action
# ---------------------------------------------------------------------------

class TestRequestAction:
    def test_minimal_payload(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.request_action(run_id="r1", action="approve")
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["action"] == "approve"
        assert "feedback" not in body
        assert body["force"] is False

    def test_with_feedback_and_force(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.request_action(run_id="r1", action="reject", feedback="needs work", force=True)
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["action"] == "reject"
        assert body["feedback"] == "needs work"
        assert body["force"] is True

    def test_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.request_action(run_id="r1", action="approve")
            req = mock_open.call_args[0][0]
        assert req.full_url == "http://localhost:8200/api/runs/r1/action"


# ---------------------------------------------------------------------------
# sync_workflow
# ---------------------------------------------------------------------------

class TestSyncWorkflow:
    def test_payload(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.sync_workflow(workflow_name="wf1", definition={"steps": []})
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["workflow_name"] == "wf1"
        assert body["definition"] == {"steps": []}

    def test_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.sync_workflow(workflow_name="wf1", definition={})
            req = mock_open.call_args[0][0]
        assert req.full_url == "http://localhost:8200/api/workflows/sync"
