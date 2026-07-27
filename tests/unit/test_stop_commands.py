"""Unit tests for stop_commands module."""
from __future__ import annotations

import json

from agent_runner_v2 import stop_commands


class _FakeBackendClient:
    """Fake BackendClient that records all calls for verification."""

    def __init__(self, _base_url: str) -> None:
        self.base_url = _base_url
        self.stop_called = False
        self.stop_kwargs = {}
        self.sync_called = False
        self.sync_payload = {}
        self.get_run_called = False

    def get_run(self, *, run_id: str):
        """Return a fake run detail with an active step_run_id."""
        self.get_run_called = True
        return {"run": {"id": run_id, "current_step_run_id": "step-run-abc"}}

    def sync_job_state(self, *, step_run_id: str, payload: dict):
        """Record the sync call."""
        self.sync_called = True
        self.sync_payload = payload
        return {"status": "ok"}

    def stop_run(self, **kwargs):
        """Record the stop call."""
        self.stop_called = True
        self.stop_kwargs = kwargs
        return {"status": "ok", "kwargs": kwargs}


def test_stop_command_comprehensive_cancel(monkeypatch, capsys) -> None:
    """stop performs get_run + sync_job_state + stop_run for comprehensive cancel."""
    fake = _FakeBackendClient(None)
    monkeypatch.setattr(stop_commands, "BackendClient", lambda url: fake)
    monkeypatch.setattr(
        stop_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = stop_commands.main(["run-1", "--reason", "Operator requested stop"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["status"] == "ok"

    # Verify all three steps were called
    assert fake.get_run_called
    assert fake.sync_called
    assert fake.sync_payload["run_status"] == "stopped"
    assert fake.sync_payload["step_status"] == "cancelled"
    assert fake.sync_payload["context_payload"]["__run_control"]["stop_requested"] is True

    assert fake.stop_called
    assert fake.stop_kwargs == {
        "run_id": "run-1",
        "reason": "Operator requested stop",
        "mode": "after_current_step",
    }

    # Verify result includes step_synced flag
    assert payload["step_synced"] is True
    assert payload["step_run_id"] == "step-run-abc"


def test_stop_command_no_active_step(monkeypatch, capsys) -> None:
    """stop falls back to stop_run only when no active step_run_id exists."""

    class _NoStepClient:
        def __init__(self, _url):
            pass

        def get_run(self, *, run_id):
            return {"run": {"id": run_id}}  # No active_step_run_id

        def stop_run(self, **kwargs):
            return {"status": "ok", "kwargs": kwargs}

    fake = _NoStepClient(None)
    monkeypatch.setattr(stop_commands, "BackendClient", lambda url: fake)
    monkeypatch.setattr(
        stop_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = stop_commands.main(["run-1"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["status"] == "ok"
    assert "step_synced" not in payload


def test_stop_command_get_run_fails(monkeypatch, capsys) -> None:
    """stop proceeds with stop_run even if get_run fails."""

    class _GetRunFailsClient:
        def __init__(self, _url):
            pass

        def get_run(self, *, run_id):
            raise RuntimeError("Connection timeout")

        def stop_run(self, **kwargs):
            return {"status": "ok", "kwargs": kwargs}

    monkeypatch.setattr(stop_commands, "BackendClient", lambda url: _GetRunFailsClient(url))
    monkeypatch.setattr(
        stop_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = stop_commands.main(["run-1", "--reason", "test"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["status"] == "ok"
    assert payload["kwargs"]["run_id"] == "run-1"
