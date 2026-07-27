"""Unit tests for daemon-mode result sync in run_agent."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from agent_runner_v2 import run_agent


class _FakeStepResult:
    """Minimal StepResult stand-in for testing."""

    def __init__(self, status: str = "APPROVED", remark: str = "Step completed") -> None:
        self.status = status
        self.remark = remark
        self.artifacts = {}
        self.reject_code = None
        self.usage_data = None
        self.meta_json_path = None


def test_sync_results_skips_when_no_backend_url() -> None:
    """_sync_results_to_backend does nothing when backend_url is empty."""
    state = {"workflow_step_run_id": "step-run-abc", "job_status": "IN_PROGRESS"}
    result = _FakeStepResult()

    with patch("agent_runner_v2.run_agent.BackendClient") as mock_client_cls:
        run_agent._sync_results_to_backend(
            state=state, step_result=result, coder_used="test-coder", backend_url="",
        )
        mock_client_cls.assert_not_called()


def test_sync_results_skips_when_no_step_run_id() -> None:
    """_sync_results_to_backend does nothing when workflow_step_run_id is missing."""
    state = {"workflow_step_run_id": "", "job_status": "IN_PROGRESS"}
    result = _FakeStepResult()

    with patch("agent_runner_v2.run_agent.BackendClient") as mock_client_cls:
        run_agent._sync_results_to_backend(
            state=state, step_result=result, coder_used="test-coder",
            backend_url="http://localhost:8100",
        )
        mock_client_cls.assert_not_called()


def test_sync_results_calls_backend() -> None:
    """_sync_results_to_backend calls sync_job_state with correct payload."""
    state = {
        "workflow_step_run_id": "step-run-abc",
        "workflow_run_id": "run-123",
        "job_status": "IN_PROGRESS",
        "status": "IN_PROGRESS",
        "current_step": "generate_prompts",
        "artifacts": {},
        "completed_steps": [],
        "failed_steps": [],
        "review_state": {},
        "usage_summary": None,
        "last_failure_reason": None,
        "target_project_root": "",
        "project_root": "/tmp/test",
        "workspace_path": "/tmp/test",
    }
    result = _FakeStepResult(status="APPROVED", remark="Generated 5 prompts")

    mock_client = MagicMock()
    mock_client.sync_job_state.return_value = {"status": "ok"}

    with patch("agent_runner_v2.backend_client.BackendClient", return_value=mock_client):
        run_agent._sync_results_to_backend(
            state=state, step_result=result, coder_used="test-coder",
            backend_url="http://localhost:8100",
        )

    mock_client.sync_job_state.assert_called_once()
    call_kwargs = mock_client.sync_job_state.call_args
    assert call_kwargs.kwargs["step_run_id"] == "step-run-abc"
    payload = call_kwargs.kwargs["payload"]
    assert payload["run_status"] == "pending"
    assert payload["next_step_name"] == "generate_prompts"


def test_sync_results_handles_backend_error(capsys) -> None:
    """_sync_results_to_backend prints error to stderr but does not raise."""
    state = {"workflow_step_run_id": "step-run-abc", "job_status": "IN_PROGRESS"}
    result = _FakeStepResult()

    with patch("agent_runner_v2.backend_client.BackendClient", side_effect=RuntimeError("Connection refused")):
        run_agent._sync_results_to_backend(
            state=state, step_result=result, coder_used="test-coder",
            backend_url="http://localhost:8100",
        )

    captured = capsys.readouterr()
    assert "[daemon-sync] result sync failed" in captured.err
