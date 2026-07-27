"""Tests for daemon race condition fixes.

Tests the pre-execution backend sync and post-execution conflict check
that prevent console cancel/update operations from being overwritten.
"""
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_daemon_fetches_backend_state_before_spawn(tmp_path):
    """Test that daemon fetches full backend state before spawning CLI."""
    from agent_runner_v2.daemon import _spawn_child
    
    # Mock claim data
    claim = {
        "run": {"id": "run-123", "run_code": "JOB-001", "workflow_name": "test_workflow"},
        "step_run": {"id": "step-run-456", "step_name": "generate", "sequence_no": 1},
        "step_execution_spec": {"step_sequence_no": 1, "step_order": 1},
    }
    
    # Mock backend response
    backend_state = {
        "run": {
            "id": "run-123",
            "run_code": "JOB-001",
            "workflow_name": "test_workflow",
            "current_step_run_id": "step-run-456",
            "output_payload": {"ARTIFACT_1": "/path/to/artifact1.md"},
            "context_payload": {"__run_control": {"stop_requested": False}},
        }
    }
    
    # Mock dependencies
    mock_logger = MagicMock()
    mock_client = MagicMock()
    mock_client.get_run.return_value = backend_state
    
    with patch("agent_runner_v2.backend_client.BackendClient", return_value=mock_client):
        with patch("agent_runner_v2.run_agent._build_worker_request_payload") as mock_build:
            mock_build.return_value = {
                "project_root": str(tmp_path),
                "workspace_root": str(tmp_path),
                "job_id": "JOB-001",
                "template_group": "test_workflow",
            }
            with patch("agent_runner_v2.job_state.job_dir", return_value=tmp_path):
                with patch("subprocess.Popen") as mock_popen:
                    mock_process = MagicMock()
                    mock_process.pid = 12345
                    mock_popen.return_value = mock_process
                    
                    child = _spawn_child(
                        claim=claim,
                        runtime_root=tmp_path,
                        cli_pythonpath=None,
                        logger=mock_logger,
                        backend_url="http://localhost:8100",
                        step_spec_source="backend",
                    )
                    
                    # Verify backend state was fetched
                    mock_client.get_run.assert_called_once_with(run_id="run-123")
                    
                    # Verify backend_state.json was written
                    backend_state_path = tmp_path / "step-run-456" / "backend_state.json"
                    assert backend_state_path.exists()
                    written_state = json.loads(backend_state_path.read_text(encoding="utf-8"))
                    assert written_state == backend_state


def test_cli_initializes_from_backend_state(tmp_path):
    """Test that CLI initializes job.json from backend state when available."""
    from agent_runner_v2.manual_runtime import _load_backend_state_file, _initialize_state_from_backend
    
    # Create backend state file
    backend_state = {
        "run": {
            "id": "run-123",
            "run_code": "JOB-001",
            "workflow_name": "test_workflow",
            "current_step_run_id": "step-run-456",
            "output_payload": {"ARTIFACT_1": "/path/to/artifact1.md"},
            "context_payload": {"__run_control": {"stop_requested": False}},
        }
    }
    
    backend_state_path = tmp_path / "backend_state.json"
    backend_state_path.write_text(json.dumps(backend_state), encoding="utf-8")
    
    # Set env var
    with patch.dict(os.environ, {"AGENT_RUNNER_BACKEND_STATE_FILE": str(backend_state_path)}):
        loaded = _load_backend_state_file()
        assert loaded is not None
        assert loaded["run"]["id"] == "run-123"
        assert loaded["run"]["current_step_run_id"] == "step-run-456"
    
    # Test initialization
    mock_hooks = MagicMock()
    mock_hooks.create_job.return_value = {
        "job_id": "JOB-001",
        "template_group": "test_workflow",
        "artifacts": {},
        "job_status": "IN_PROGRESS",
    }
    
    group_cfg = {"workflow_name": "test_workflow", "job_init_step": "generate"}
    
    state = _initialize_state_from_backend(
        backend_state=backend_state,
        group_cfg=group_cfg,
        seed_artifacts={},
        mode="daemon",
        job_no="JOB-001",
        hooks=mock_hooks,
    )
    
    # Verify backend state was merged
    assert state["workflow_run_id"] == "run-123"
    assert state["workflow_step_run_id"] == "step-run-456"
    assert state["artifacts"]["ARTIFACT_1"] == "/path/to/artifact1.md"


def test_cli_skips_sync_when_backend_cancelled():
    """Test that CLI skips sync when backend state is cancelled/stopped."""
    from agent_runner_v2.run_agent import _sync_results_to_backend
    
    state = {
        "workflow_run_id": "run-123",
        "workflow_step_run_id": "step-run-456",
        "job_status": "IN_PROGRESS",
        "artifacts": {"ARTIFACT_1": "/path/to/artifact1.md"},
    }
    
    step_result = MagicMock()
    step_result.status = "completed"
    step_result.remark = "Step completed successfully"
    
    # Mock backend response showing cancelled state
    backend_response = {
        "run": {
            "id": "run-123",
            "run_status": "stopped",
            "context_payload": {"__run_control": {"stop_requested": True}},
        }
    }
    
    mock_client = MagicMock()
    mock_client.get_run.return_value = backend_response
    
    with patch("agent_runner_v2.backend_client.BackendClient", return_value=mock_client):
        _sync_results_to_backend(
            state=state,
            step_result=step_result,
            coder_used="test_coder",
            backend_url="http://localhost:8100",
        )
        
        # Verify get_run was called to check status
        mock_client.get_run.assert_called_once_with(run_id="run-123")
        
        # Verify sync_job_state was NOT called (skipped due to cancelled state)
        mock_client.sync_job_state.assert_not_called()


def test_cli_syncs_when_backend_active():
    """Test that CLI syncs normally when backend state is active."""
    from agent_runner_v2.run_agent import _sync_results_to_backend
    
    state = {
        "workflow_run_id": "run-123",
        "workflow_step_run_id": "step-run-456",
        "job_status": "IN_PROGRESS",
        "artifacts": {"ARTIFACT_1": "/path/to/artifact1.md"},
        "current_step": "generate",
    }
    
    step_result = MagicMock()
    step_result.status = "completed"
    step_result.remark = "Step completed successfully"
    
    # Mock backend response showing active state
    backend_response = {
        "run": {
            "id": "run-123",
            "run_status": "pending",
            "context_payload": {"__run_control": {"stop_requested": False}},
        }
    }
    
    mock_client = MagicMock()
    mock_client.get_run.return_value = backend_response
    
    with patch("agent_runner_v2.backend_client.BackendClient", return_value=mock_client):
        with patch("agent_runner_v2.daemon_runtime.build_job_sync_payload") as mock_build:
            mock_build.return_value = {"step_status": "completed"}
            
            _sync_results_to_backend(
                state=state,
                step_result=step_result,
                coder_used="test_coder",
                backend_url="http://localhost:8100",
            )
            
            # Verify get_run was called to check status
            mock_client.get_run.assert_called_once_with(run_id="run-123")
            
            # Verify sync_job_state WAS called (backend is active)
            mock_client.sync_job_state.assert_called_once()


def test_cli_syncs_when_backend_check_fails():
    """Test that CLI proceeds with sync if backend status check fails (non-fatal)."""
    from agent_runner_v2.run_agent import _sync_results_to_backend
    
    state = {
        "workflow_run_id": "run-123",
        "workflow_step_run_id": "step-run-456",
        "job_status": "IN_PROGRESS",
        "artifacts": {},
    }
    
    step_result = MagicMock()
    step_result.status = "completed"
    step_result.remark = "Step completed"
    
    mock_client = MagicMock()
    mock_client.get_run.side_effect = RuntimeError("Backend unavailable")
    
    with patch("agent_runner_v2.backend_client.BackendClient", return_value=mock_client):
        with patch("agent_runner_v2.daemon_runtime.build_job_sync_payload") as mock_build:
            mock_build.return_value = {"step_status": "completed"}
            
            _sync_results_to_backend(
                state=state,
                step_result=step_result,
                coder_used="test_coder",
                backend_url="http://localhost:8100",
            )
            
            # Verify sync_job_state was still called despite check failure
            mock_client.sync_job_state.assert_called_once()
