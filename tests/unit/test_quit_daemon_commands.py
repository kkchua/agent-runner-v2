"""Unit tests for quit_daemon_commands module.

Tests main() argument parsing, payload construction, response handling,
and _ensure_control_workflow() auto-registration logic.
"""
from __future__ import annotations

import io
import json
from unittest.mock import MagicMock, patch

import pytest

from agent_runner_v2 import quit_daemon_commands
from agent_runner_v2.quit_daemon_commands import CONTROL_WORKFLOW, main, _ensure_control_workflow


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def _run_main(argv=None, submit_result=None):
    """Run main() with mocked config and backend client.

    Returns (exit_code, captured_dict, stdout_text).
    """
    if submit_result is None:
        submit_result = {"run": {"id": "run-123", "run_code": "CTRL-001"}}

    captured = {}

    def fake_submit(**kwargs):
        captured["kwargs"] = kwargs
        return submit_result

    def fake_ensure(client, workflow_name):
        captured["ensure_called"] = True
        captured["ensure_workflow"] = workflow_name

    with patch.object(quit_daemon_commands, "_load_config", return_value={
        "backend_url": "http://test:8100",
        "worker_id": "test-worker",
        "worker_label": "live",
    }):
        with patch.object(quit_daemon_commands, "BackendClient") as MockClient:
            mock_client = MagicMock()
            mock_client.submit_run.side_effect = fake_submit
            mock_client.base_url = "http://test:8100"
            MockClient.return_value = mock_client
            with patch.object(quit_daemon_commands, "_ensure_control_workflow", side_effect=fake_ensure):
                stdout = io.StringIO()
                with patch("sys.stdout", stdout):
                    exit_code = main(argv or [])
    return exit_code, captured, stdout.getvalue()


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_control_workflow_name(self):
        assert CONTROL_WORKFLOW == "__daemon_control__"


# ---------------------------------------------------------------------------
# main() — argument parsing and defaults
# ---------------------------------------------------------------------------

class TestMainDefaults:
    def test_default_workflow_is_daemon_control(self):
        """Default --workflow is __daemon_control__, not a real workflow."""
        exit_code, captured, _ = _run_main([])
        assert exit_code == 0
        assert captured["kwargs"]["workflow_name"] == "__daemon_control__"

    def test_default_worker_id_from_config(self):
        """Worker ID falls back to config.json value."""
        exit_code, captured, _ = _run_main([])
        assert captured["kwargs"]["target_worker_id"] == "test-worker"

    def test_explicit_worker_id(self):
        """--worker-id overrides config."""
        exit_code, captured, _ = _run_main(["--worker-id", "custom-worker"])
        assert captured["kwargs"]["target_worker_id"] == "custom-worker"

    def test_reason_in_context_payload(self):
        """--reason is included in context_payload.__run_control."""
        exit_code, captured, _ = _run_main(["--reason", "Maintenance window"])
        ctx = captured["kwargs"]["context_payload"]
        assert ctx["__run_control"]["quit_daemon"] is True
        assert ctx["__run_control"]["reason"] == "Maintenance window"

    def test_default_reason_when_empty(self):
        """Default reason when --reason not provided."""
        exit_code, captured, _ = _run_main([])
        ctx = captured["kwargs"]["context_payload"]
        assert ctx["__run_control"]["quit_daemon"] is True
        assert "Quit requested" in ctx["__run_control"]["reason"]

    def test_uses_target_worker_id_not_worker_id(self):
        """CRITICAL: submit_run called with target_worker_id, not worker_id."""
        exit_code, captured, _ = _run_main([])
        assert "target_worker_id" in captured["kwargs"]
        assert "worker_id" not in captured["kwargs"]

    def test_worker_label_from_config(self):
        """Worker label from config."""
        exit_code, captured, _ = _run_main([])
        assert captured["kwargs"]["worker_label"] == "live"

    def test_explicit_worker_label(self):
        """--worker-label overrides config."""
        exit_code, captured, _ = _run_main(["--worker-label", "dev"])
        assert captured["kwargs"]["worker_label"] == "dev"

    def test_input_payload_has_command(self):
        """input_payload includes command=quit_daemon."""
        exit_code, captured, _ = _run_main([])
        assert captured["kwargs"]["input_payload"]["command"] == "quit_daemon"

    def test_ensure_control_workflow_called(self):
        """_ensure_control_workflow is called before submit."""
        exit_code, captured, _ = _run_main([])
        assert captured.get("ensure_called") is True
        assert captured["ensure_workflow"] == "__daemon_control__"


# ---------------------------------------------------------------------------
# main() — response handling
# ---------------------------------------------------------------------------

class TestMainResponseHandling:
    def test_extracts_run_id_from_nested_response(self):
        """run_id extracted from result['run']['id'], not result['id']."""
        submit_result = {"run": {"id": "nested-id", "run_code": "CTRL-001"}}
        exit_code, _, stdout = _run_main(submit_result=submit_result)
        output = json.loads(stdout)
        assert output["run_id"] == "nested-id"

    def test_extracts_run_code_from_nested_response(self):
        """run_code extracted from result['run']['run_code']."""
        submit_result = {"run": {"id": "r1", "run_code": "CTRL-42"}}
        exit_code, _, stdout = _run_main(submit_result=submit_result)
        output = json.loads(stdout)
        assert output["run_code"] == "CTRL-42"

    def test_fallback_when_no_run_key(self):
        """Falls back to top-level id if 'run' key missing."""
        submit_result = {"id": "flat-id", "run_code": "FLAT-001"}
        exit_code, _, stdout = _run_main(submit_result=submit_result)
        output = json.loads(stdout)
        assert output["run_id"] == "flat-id"

    def test_output_status_submitted(self):
        """Output includes status=submitted on success."""
        exit_code, _, stdout = _run_main()
        output = json.loads(stdout)
        assert output["status"] == "submitted"

    def test_exit_code_zero_on_success(self):
        exit_code, _, _ = _run_main()
        assert exit_code == 0

    def test_output_includes_worker_id(self):
        """Output includes the worker_id used."""
        exit_code, _, stdout = _run_main(["--worker-id", "w42"])
        output = json.loads(stdout)
        assert output["worker_id"] == "w42"


# ---------------------------------------------------------------------------
# main() — error handling
# ---------------------------------------------------------------------------

class TestMainErrorHandling:
    def test_exit_code_one_on_runtime_error(self):
        """RuntimeError from submit_run returns exit code 1."""
        with patch.object(quit_daemon_commands, "_load_config", return_value={
            "backend_url": "http://test:8100",
            "worker_id": "w1",
        }):
            with patch.object(quit_daemon_commands, "BackendClient") as MockClient:
                mock_client = MagicMock()
                mock_client.submit_run.side_effect = RuntimeError("Backend down")
                mock_client.base_url = "http://test:8100"
                MockClient.return_value = mock_client
                with patch.object(quit_daemon_commands, "_ensure_control_workflow"):
                    stderr = io.StringIO()
                    with patch("sys.stderr", stderr):
                        exit_code = main([])
        assert exit_code == 1
        error_output = json.loads(stderr.getvalue())
        assert error_output["status"] == "error"
        assert "Backend down" in error_output["message"]


# ---------------------------------------------------------------------------
# _ensure_control_workflow
# ---------------------------------------------------------------------------

class TestEnsureControlWorkflow:
    def test_skips_non_control_workflow(self):
        """Non-control workflow names are not auto-registered."""
        client = MagicMock()
        _ensure_control_workflow(client, "agnes_media_gen_v1")
        client._request.assert_not_called()

    def test_skips_if_already_registered(self):
        """No sync call if workflow already exists in backend."""
        client = MagicMock()
        client._request.return_value = [{"name": "__daemon_control__"}]
        client.base_url = "http://test:8100"

        _ensure_control_workflow(client, "__daemon_control__")
        # Should only call _request to check, not urlopen to sync
        client._request.assert_called_once_with("GET", "/api/workflows")

    def test_attempts_sync_if_not_registered(self):
        """Tries to sync if workflow not in backend list."""
        client = MagicMock()
        client._request.return_value = [{"name": "other_workflow"}]
        client.base_url = "http://test:8100"

        # Mock the lazy imports inside _ensure_control_workflow
        mock_pkg_dir = MagicMock()
        mock_pkg_dir.exists.return_value = False  # No local package

        with patch("agent_runner_v2.runtime_context.get_workflow_root", return_value="/tmp/workflows"):
            with patch("pathlib.Path") as MockPath:
                MockPath.return_value.__truediv__.return_value = mock_pkg_dir
                # Should not crash even if package doesn't exist
                _ensure_control_workflow(client, "__daemon_control__")

    def test_handles_check_failure_gracefully(self):
        """If checking workflow list fails, still tries to register."""
        client = MagicMock()
        client._request.side_effect = RuntimeError("Connection refused")
        client.base_url = "http://test:8100"

        mock_pkg_dir = MagicMock()
        mock_pkg_dir.exists.return_value = False

        with patch("agent_runner_v2.runtime_context.get_workflow_root", return_value="/tmp/workflows"):
            with patch("pathlib.Path") as MockPath:
                MockPath.return_value.__truediv__.return_value = mock_pkg_dir
                # Should not crash
                _ensure_control_workflow(client, "__daemon_control__")
