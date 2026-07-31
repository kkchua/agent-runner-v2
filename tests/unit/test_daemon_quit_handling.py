"""Unit tests for daemon quit and stop handling functions.

Tests _is_quit_daemon_requested(), _is_stop_requested(),
_handle_quit_daemon(), and _handle_stop_on_claim().
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agent_runner_v2.daemon import (
    _handle_quit_daemon,
    _handle_stop_on_claim,
    _is_quit_daemon_requested,
    _is_stop_requested,
)


# ---------------------------------------------------------------------------
# _is_quit_daemon_requested
# ---------------------------------------------------------------------------

class TestIsQuitDaemonRequested:
    def test_detects_quit_flag(self):
        """Returns True when __run_control.quit_daemon is True."""
        run = {
            "context_payload": {
                "__run_control": {"quit_daemon": True}
            }
        }
        assert _is_quit_daemon_requested(run) is True

    def test_returns_false_when_no_flag(self):
        """Returns False when quit_daemon flag is absent."""
        run = {"context_payload": {"__run_control": {}}}
        assert _is_quit_daemon_requested(run) is False

    def test_returns_false_when_no_context(self):
        """Returns False when context_payload is missing."""
        run = {}
        assert _is_quit_daemon_requested(run) is False

    def test_returns_false_when_context_is_none(self):
        """Returns False when context_payload is None."""
        run = {"context_payload": None}
        assert _is_quit_daemon_requested(run) is False

    def test_returns_false_when_run_control_is_none(self):
        """Returns False when __run_control is None."""
        run = {"context_payload": {"__run_control": None}}
        assert _is_quit_daemon_requested(run) is False

    def test_returns_false_when_quit_daemon_false(self):
        """Returns False when quit_daemon is explicitly False."""
        run = {"context_payload": {"__run_control": {"quit_daemon": False}}}
        assert _is_quit_daemon_requested(run) is False

    def test_does_not_confuse_with_stop_requested(self):
        """stop_requested flag does NOT trigger quit detection."""
        run = {"context_payload": {"__run_control": {"stop_requested": True}}}
        assert _is_quit_daemon_requested(run) is False


# ---------------------------------------------------------------------------
# _is_stop_requested
# ---------------------------------------------------------------------------

class TestIsStopRequested:
    def test_detects_stop_flag(self):
        """Returns True when __run_control.stop_requested is True."""
        run = {
            "context_payload": {
                "__run_control": {"stop_requested": True}
            }
        }
        assert _is_stop_requested(run) is True

    def test_detects_stopped_status(self):
        """Returns True when run_status is 'stopped'."""
        run = {"run_status": "stopped"}
        assert _is_stop_requested(run) is True

    def test_detects_stopped_status_case_insensitive(self):
        """Returns True for 'Stopped' (case insensitive)."""
        run = {"run_status": "Stopped"}
        assert _is_stop_requested(run) is True

    def test_returns_false_when_no_flag(self):
        """Returns False when stop flag is absent."""
        run = {"context_payload": {"__run_control": {}}}
        assert _is_stop_requested(run) is False

    def test_returns_false_when_running(self):
        """Returns False when run_status is 'running'."""
        run = {"run_status": "running"}
        assert _is_stop_requested(run) is False

    def test_returns_false_when_no_context(self):
        """Returns False when context_payload is missing."""
        run = {}
        assert _is_stop_requested(run) is False

    def test_does_not_confuse_with_quit_daemon(self):
        """quit_daemon flag does NOT trigger stop detection."""
        run = {"context_payload": {"__run_control": {"quit_daemon": True}}}
        assert _is_stop_requested(run) is False


# ---------------------------------------------------------------------------
# _handle_quit_daemon
# ---------------------------------------------------------------------------

class TestHandleQuitDaemon:
    def _make_claim(self, run_id="run-1", step_run_id="sr-1"):
        return {
            "run": {"id": run_id, "run_code": "CTRL-001"},
            "step_run": {"id": step_run_id},
        }

    def _make_logger(self):
        return MagicMock()

    def test_returns_true(self):
        """Always returns True to signal daemon shutdown."""
        client = MagicMock()
        claim = self._make_claim()
        logger = self._make_logger()

        result = _handle_quit_daemon(client, claim, logger)

        assert result is True

    def test_syncs_step_as_completed(self):
        """Calls sync_job_state with completed status."""
        client = MagicMock()
        claim = self._make_claim(run_id="r1", step_run_id="sr1")
        logger = self._make_logger()

        _handle_quit_daemon(client, claim, logger)

        client.sync_job_state.assert_called_once()
        call_kwargs = client.sync_job_state.call_args
        assert call_kwargs[1]["step_run_id"] == "sr1" or call_kwargs[0][0] == "sr1"
        payload = call_kwargs[1].get("payload") or call_kwargs[0][1] if len(call_kwargs[0]) > 1 else call_kwargs[1]["payload"]
        assert payload["run_status"] == "completed"
        assert payload["step_status"] == "completed"
        assert payload["step_outcome"] == "completed"
        assert payload["step_coder"] == "system"

    def test_includes_quit_ack_event(self):
        """Sync payload includes DAEMON_QUIT_ACK event."""
        client = MagicMock()
        claim = self._make_claim()
        logger = self._make_logger()

        _handle_quit_daemon(client, claim, logger)

        payload = client.sync_job_state.call_args[1]["payload"]
        events = payload["events"]
        assert any(e["event_type"] == "DAEMON_QUIT_ACK" for e in events)

    def test_stops_run_after_sync(self):
        """Calls stop_run to prevent re-claiming on daemon restart."""
        client = MagicMock()
        claim = self._make_claim(run_id="run-42")
        logger = self._make_logger()

        _handle_quit_daemon(client, claim, logger)

        client.stop_run.assert_called_once()
        call_kwargs = client.stop_run.call_args
        assert call_kwargs[1]["run_id"] == "run-42" or call_kwargs[0][0] == "run-42"

    def test_still_returns_true_if_sync_fails(self):
        """Returns True even if sync_job_state raises."""
        client = MagicMock()
        client.sync_job_state.side_effect = RuntimeError("Backend down")
        claim = self._make_claim()
        logger = self._make_logger()

        result = _handle_quit_daemon(client, claim, logger)

        assert result is True

    def test_still_returns_true_if_stop_fails(self):
        """Returns True even if stop_run raises."""
        client = MagicMock()
        client.stop_run.side_effect = RuntimeError("Backend down")
        claim = self._make_claim()
        logger = self._make_logger()

        result = _handle_quit_daemon(client, claim, logger)

        assert result is True

    def test_logs_quit_requested(self):
        """Logs daemon_quit_requested event."""
        client = MagicMock()
        claim = self._make_claim()
        logger = self._make_logger()

        _handle_quit_daemon(client, claim, logger)

        logger.log.assert_any_call(
            "info", "daemon_quit_requested",
            message=pytest.approx(logger.log.call_args_list[0][1]["message"], abs=None),
            details=pytest.approx(logger.log.call_args_list[0][1]["details"], abs=None),
        )


# ---------------------------------------------------------------------------
# _handle_stop_on_claim
# ---------------------------------------------------------------------------

class TestHandleStopOnClaim:
    def test_logs_and_returns(self):
        """Logs stop_requested_on_claim and returns None."""
        client = MagicMock()
        claim = {"run": {"id": "r1", "run_code": "JOB-001"}}
        logger = MagicMock()

        result = _handle_stop_on_claim(client, claim, logger)

        assert result is None
        logger.log.assert_called_once()
        call_args = logger.log.call_args
        assert call_args[0][0] == "info"
        assert call_args[0][1] == "stop_requested_on_claim"

    def test_does_not_sync(self):
        """Does not call sync_job_state (run is already stopped)."""
        client = MagicMock()
        claim = {"run": {"id": "r1", "run_code": "JOB-001"}}
        logger = MagicMock()

        _handle_stop_on_claim(client, claim, logger)

        client.sync_job_state.assert_not_called()

    def test_does_not_stop(self):
        """Does not call stop_run (run is already stopped)."""
        client = MagicMock()
        claim = {"run": {"id": "r1", "run_code": "JOB-001"}}
        logger = MagicMock()

        _handle_stop_on_claim(client, claim, logger)

        client.stop_run.assert_not_called()
