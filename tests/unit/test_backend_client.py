"""Unit tests for backend_client module.

Tests URL construction, payload building, HTTP error handling,
and all 14 API methods. Mocks urllib to avoid real HTTP calls.
"""
from __future__ import annotations

import io
import json
from unittest.mock import MagicMock, patch

import pytest

from agent_runner_v2.backend_client import BackendClient


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


def _make_client(url: str = "http://localhost:8100") -> BackendClient:
    return BackendClient(base_url=url)


# ---------------------------------------------------------------------------
# URL construction
# ---------------------------------------------------------------------------

class TestUrlConstruction:
    def test_basic_path(self):
        c = _make_client("http://localhost:8100")
        assert c._url("/api/runs") == "http://localhost:8100/api/runs"

    def test_strips_trailing_slash(self):
        c = _make_client("http://localhost:8100/")
        assert c._url("/api/runs") == "http://localhost:8100/api/runs"

    def test_with_query_params(self):
        c = _make_client()
        url = c._url("/api/runs", query={"worker_id": "w1", "status_group": "active"})
        assert "worker_id=w1" in url
        assert "status_group=active" in url
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
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.side_effect = HTTPError(
                url="http://localhost:8100/api/runs",
                code=404,
                msg="Not Found",
                hdrs=MagicMock(),
                fp=io.BytesIO(b'{"detail":"not found"}'),
            )
            with pytest.raises(RuntimeError, match="status=404"):
                c._request("GET", "/api/runs")

    def test_url_error_raises_runtime_error(self):
        from urllib.error import URLError
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.side_effect = URLError("Connection refused")
            with pytest.raises(RuntimeError, match="Connection refused"):
                c._request("GET", "/api/runs")

    def test_empty_body_returns_empty_dict(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response("")
            result = c._request("GET", "/api/runs/123")
        assert result == {}

    def test_json_body_parsed(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({"id": "r1", "status": "running"})
            result = c._request("GET", "/api/runs/r1")
        assert result["id"] == "r1"

    def test_payload_serialized_as_json(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c._request("POST", "/api/runs", payload={"workflow_name": "wf1"})
            # Verify the request was constructed with JSON data
            call_args = mock_open.call_args
            req = call_args[0][0]
            assert req.data == json.dumps({"workflow_name": "wf1"}).encode("utf-8")
            assert req.get_header("Content-type") == "application/json"


# ---------------------------------------------------------------------------
# submit_run
# ---------------------------------------------------------------------------

class TestSubmitRun:
    def test_minimal_payload(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({"run": {"id": "r1"}})
            result = c.submit_run(workflow_name="wf1")
            req = mock_open.call_args[0][0]
            body = json.loads(req.data)
        assert body["workflow_name"] == "wf1"
        assert body["worker_label"] == "live"
        assert "target_worker_id" not in body

    def test_target_worker_id_not_worker_id(self):
        """CRITICAL: parameter is target_worker_id, not worker_id."""
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({"run": {"id": "r1"}})
            c.submit_run(workflow_name="wf1", target_worker_id="w1")
            req = mock_open.call_args[0][0]
            body = json.loads(req.data)
        assert body["target_worker_id"] == "w1"
        assert "worker_id" not in body  # Must NOT use worker_id

    def test_all_optional_fields(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({"run": {"id": "r1"}})
            c.submit_run(
                workflow_name="wf1",
                initiative_id="init-1",
                target_worker_id="w1",
                assigned_provider="provider-a",
                coder_override="opencode",
                project_root="/repo",
                target_project_root="/repo",
                workspace_path="/ws",
                repo_url="https://github.com/test",
                repo_ref="main",
                worker_label="dev",
                env_overrides={"KEY": "val"},
                input_payload={"INPUT": "file.md"},
                context_payload={"start_step": "step2"},
            )
            req = mock_open.call_args[0][0]
            body = json.loads(req.data)
        assert body["initiative_id"] == "init-1"
        assert body["target_worker_id"] == "w1"
        assert body["assigned_provider"] == "provider-a"
        assert body["coder_override"] == "opencode"
        assert body["project_root"] == "/repo"
        assert body["env_overrides"] == {"KEY": "val"}
        assert body["input_payload"] == {"INPUT": "file.md"}
        assert body["context_payload"] == {"start_step": "step2"}
        assert body["worker_label"] == "dev"

    def test_posts_to_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.submit_run(workflow_name="wf1")
            req = mock_open.call_args[0][0]
        assert req.full_url == "http://localhost:8100/api/runs"
        assert req.get_method() == "POST"


# ---------------------------------------------------------------------------
# approve_run
# ---------------------------------------------------------------------------

class TestApproveRun:
    def test_default_action_is_approve(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.approve_run(run_id="r1")
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["action"] == "approve"

    def test_reject_action(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.approve_run(run_id="r1", action="reject", feedback="needs work")
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["action"] == "reject"
        assert body["feedback"] == "needs work"

    def test_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.approve_run(run_id="run-uuid-123")
            req = mock_open.call_args[0][0]
        assert "/api/runs/run-uuid-123/approve" in req.full_url


# ---------------------------------------------------------------------------
# get_run
# ---------------------------------------------------------------------------

class TestGetRun:
    def test_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({"run": {"id": "r1"}})
            c.get_run(run_id="r1")
            req = mock_open.call_args[0][0]
        assert req.full_url == "http://localhost:8100/api/runs/r1"
        assert req.get_method() == "GET"


# ---------------------------------------------------------------------------
# list_runs
# ---------------------------------------------------------------------------

class TestListRuns:
    def test_no_filters(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response([])
            c.list_runs()
            req = mock_open.call_args[0][0]
        assert "?" not in req.full_url

    def test_with_worker_id(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response([])
            c.list_runs(worker_id="w1")
            req = mock_open.call_args[0][0]
        assert "worker_id=w1" in req.full_url

    def test_with_status_group(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response([])
            c.list_runs(status_group="non_terminal")
            req = mock_open.call_args[0][0]
        assert "status_group=non_terminal" in req.full_url

    def test_with_workflow_name(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response([])
            c.list_runs(workflow_name="wf1")
            req = mock_open.call_args[0][0]
        assert "workflow_name=wf1" in req.full_url


# ---------------------------------------------------------------------------
# stop_run
# ---------------------------------------------------------------------------

class TestStopRun:
    def test_default_mode(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.stop_run(run_id="r1")
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["mode"] == "after_current_step"

    def test_with_reason(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.stop_run(run_id="r1", reason="Cancelled by operator")
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["reason"] == "Cancelled by operator"

    def test_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.stop_run(run_id="r1")
            req = mock_open.call_args[0][0]
        assert "/api/runs/r1/stop" in req.full_url


# ---------------------------------------------------------------------------
# reset_run_step
# ---------------------------------------------------------------------------

class TestResetRunStep:
    def test_payload(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.reset_run_step(run_id="r1", step_name="generate_docs")
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["step_name"] == "generate_docs"

    def test_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.reset_run_step(run_id="r1", step_name="s1")
            req = mock_open.call_args[0][0]
        assert "/api/runs/r1/reset-step" in req.full_url


# ---------------------------------------------------------------------------
# register_worker
# ---------------------------------------------------------------------------

class TestRegisterWorker:
    def test_payload(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.register_worker(worker_id="w1", host_name="myhost", worker_label="dev")
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["worker_id"] == "w1"
        assert body["host_name"] == "myhost"
        assert body["worker_label"] == "dev"
        assert body["capabilities"] == {}


# ---------------------------------------------------------------------------
# heartbeat
# ---------------------------------------------------------------------------

class TestHeartbeat:
    def test_minimal_payload(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.heartbeat(worker_id="w1")
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["worker_id"] == "w1"
        assert "status" not in body

    def test_all_fields(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.heartbeat(
                worker_id="w1",
                status="running",
                current_step_run_id="sr1",
                workflow_run_id="wr1",
                workflow_step_run_id="wsr1",
                run_code="JOB-001",
                pid=12345,
                state="active",
                log_file="/tmp/log",
                watchdog_reason=None,
                exit_code=0,
            )
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["status"] == "running"
        assert body["pid"] == 12345
        assert body["exit_code"] == 0


# ---------------------------------------------------------------------------
# claim_step
# ---------------------------------------------------------------------------

class TestClaimStep:
    def test_uses_query_param(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.claim_step(worker_id="w1")
            req = mock_open.call_args[0][0]
        assert "worker_id=w1" in req.full_url
        assert "/api/workers/claim" in req.full_url


# ---------------------------------------------------------------------------
# complete_step_run / sync_job_state
# ---------------------------------------------------------------------------

class TestStepRunEndpoints:
    def test_complete_step_run_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.complete_step_run(step_run_id="sr1", payload={"status": "completed"})
            req = mock_open.call_args[0][0]
        assert "/api/step-runs/sr1/complete" in req.full_url

    def test_sync_job_state_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.sync_job_state(step_run_id="sr1", payload={"run_status": "running"})
            req = mock_open.call_args[0][0]
        assert "/api/step-runs/sr1/job-sync" in req.full_url


# ---------------------------------------------------------------------------
# create_artifact / create_event
# ---------------------------------------------------------------------------

class TestRunSubResources:
    def test_create_artifact_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.create_artifact(run_id="r1", payload={"key": "OUTPUT", "path": "/out.md"})
            req = mock_open.call_args[0][0]
        assert "/api/runs/r1/artifacts" in req.full_url

    def test_create_event_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.create_event(run_id="r1", payload={"event_type": "STEP_STARTED"})
            req = mock_open.call_args[0][0]
        assert "/api/runs/r1/events" in req.full_url


# ---------------------------------------------------------------------------
# cleanup_execution
# ---------------------------------------------------------------------------

class TestCleanupExecution:
    def test_payload_structure(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({"deleted": True})
            c.cleanup_execution(workflow_name="wf1", dry_run=False)
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["dry_run"] is False
        assert body["include_workers"] is False
        assert body["scope"]["workflow_name"] == "wf1"

    def test_dry_run_default(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.cleanup_execution(workflow_name="wf1")
            body = json.loads(mock_open.call_args[0][0].data)
        assert body["dry_run"] is False

    def test_correct_endpoint(self):
        c = _make_client()
        with patch("agent_runner_v2.backend_client.request.urlopen") as mock_open:
            mock_open.return_value = _mock_response({})
            c.cleanup_execution(workflow_name="wf1")
            req = mock_open.call_args[0][0]
        assert "/api/admin/execution/cleanup" in req.full_url
