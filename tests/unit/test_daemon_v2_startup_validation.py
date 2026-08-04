"""Tests for daemon_v2 startup worker validation and resilience.

The daemon must NOT auto-register itself. Instead, it validates that the
worker exists and is enabled in the backend before entering the main loop.

Resilience behavior:
- If backend is unreachable (connection error) → retry indefinitely
- If worker is disabled (is_enabled=false) → terminate with error
- If backend returns any error → retry indefinitely (daemon never crashes)
- Main loop has top-level exception handler → daemon survives any error
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent_runner_v2 import daemon_v2


class _FakeLogger:
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    def log(self, level: str, event: str, *, message: str = "", details: dict | None = None, child=None) -> None:
        self.events.append((level, event, message))


def _make_config(tmp_path: Path, worker_id: str = "worker-1") -> daemon_v2.SupervisorConfig:
    return daemon_v2.SupervisorConfig(
        worker_id=worker_id,
        worker_label="test-worker",
        backend_url="http://localhost:8200",
        poll_seconds=5,
        max_parallel=1,
        stalled_seconds=60,
        step_timeout_seconds=300,
        kill_grace_seconds=10,
        runtime_dir=tmp_path / "runtime",
        log_file=tmp_path / "daemon.log",
        cli_pythonpath=None,
        step_spec_source="backend",
    )


class _FakeClientEnabled:
    """Fake client where worker is enabled."""
    def __init__(self, base_url: str = "http://localhost:8200"):
        self.base_url = base_url

    def get_worker(self, *, worker_id: str) -> dict:
        return {"worker_id": worker_id, "is_enabled": True, "worker_label": "test-worker"}

    def heartbeat(self, **kwargs):
        return {"commands": ["shutdown"]}


class _FakeClientDisabled:
    """Fake client where worker exists but is disabled."""
    def __init__(self, base_url: str = "http://localhost:8200"):
        self.base_url = base_url

    def get_worker(self, *, worker_id: str) -> dict:
        return {"worker_id": worker_id, "is_enabled": False, "worker_label": "test-worker"}


class _FakeClientBackendDown:
    """Fake client where backend is unreachable (connection error)."""
    def __init__(self, base_url: str = "http://localhost:8200"):
        self.base_url = base_url
        self.call_count = 0

    def get_worker(self, *, worker_id: str) -> dict:
        self.call_count += 1
        raise RuntimeError("V2 backend request failed: GET /api/workers/w1 error=Connection refused")


class _FakeClientRecoversAfterRetries:
    """Fake client that fails N times then succeeds (simulates backend recovery)."""
    def __init__(self, base_url: str = "http://localhost:8200"):
        self.base_url = base_url
        self.call_count = 0
        self.fail_until = 3  # Fail first 3 calls, then succeed

    def get_worker(self, *, worker_id: str) -> dict:
        self.call_count += 1
        if self.call_count < self.fail_until:
            raise RuntimeError("V2 backend request failed: GET /api/workers/w1 error=Connection refused")
        return {"worker_id": worker_id, "is_enabled": True, "worker_label": "test-worker"}

    def heartbeat(self, **kwargs):
        return {"commands": ["shutdown"]}


def test_startup_succeeds_when_worker_enabled(tmp_path, monkeypatch) -> None:
    """Worker exists and is_enabled is True → daemon proceeds past startup validation."""
    config = _make_config(tmp_path)

    monkeypatch.setattr(daemon_v2, "DaemonLogger", lambda *args, **kwargs: _FakeLogger())
    monkeypatch.setattr(daemon_v2, "V2BackendClient", _FakeClientEnabled)
    monkeypatch.setattr(daemon_v2.signal, "signal", lambda *args: None)

    result = daemon_v2.run_supervisor(config=config, v2_url="http://localhost:8200")

    assert result == 0


def test_startup_fails_when_worker_disabled(tmp_path, monkeypatch, capsys) -> None:
    """Worker exists but is_enabled is False → daemon exits with code 1."""
    config = _make_config(tmp_path)

    monkeypatch.setattr(daemon_v2, "DaemonLogger", lambda *args, **kwargs: _FakeLogger())
    monkeypatch.setattr(daemon_v2, "V2BackendClient", _FakeClientDisabled)

    result = daemon_v2.run_supervisor(config=config, v2_url="http://localhost:8200")

    assert result == 1
    captured = capsys.readouterr()
    assert "disabled" in captured.out
    assert "is_enabled=false" in captured.out


def test_startup_retries_when_backend_down(tmp_path, monkeypatch) -> None:
    """Backend unreachable → daemon retries indefinitely, does NOT terminate."""
    config = _make_config(tmp_path)
    
    # Track how many times get_worker is called
    call_count = {"value": 0}
    max_calls = 5  # Stop after this many calls to avoid infinite loop
    
    class AlwaysFailClient:
        def __init__(self, base_url: str = "http://localhost:8200"):
            self.base_url = base_url
        
        def get_worker(self, *, worker_id: str) -> dict:
            call_count["value"] += 1
            if call_count["value"] >= max_calls:
                # After N retries, succeed to exit the loop
                return {"worker_id": worker_id, "is_enabled": True, "worker_label": "test-worker"}
            raise RuntimeError("V2 backend request failed: GET /api/workers/w1 error=Connection refused")
        
        def heartbeat(self, **kwargs):
            return {"commands": ["shutdown"]}
    
    fake_logger = _FakeLogger()
    
    monkeypatch.setattr(daemon_v2, "DaemonLogger", lambda *args, **kwargs: fake_logger)
    monkeypatch.setattr(daemon_v2, "V2BackendClient", AlwaysFailClient)
    monkeypatch.setattr(daemon_v2.signal, "signal", lambda *args: None)
    # Make sleep a no-op to avoid test hanging
    monkeypatch.setattr(daemon_v2.time, "sleep", lambda *args: None)
    
    result = daemon_v2.run_supervisor(config=config, v2_url="http://localhost:8200")
    
    # Should succeed after retries
    assert result == 0
    assert call_count["value"] == max_calls, f"Expected {max_calls} retries, got {call_count['value']}"
    
    # Check that retry warnings were logged
    events = [e[1] for e in fake_logger.events]
    assert "daemon_v2_backend_unreachable" in events


def test_startup_succeeds_after_backend_recovers(tmp_path, monkeypatch) -> None:
    """Backend fails N times then recovers → daemon eventually starts."""
    config = _make_config(tmp_path)
    fake_client = _FakeClientRecoversAfterRetries()

    monkeypatch.setattr(daemon_v2, "DaemonLogger", lambda *args, **kwargs: _FakeLogger())
    monkeypatch.setattr(daemon_v2, "V2BackendClient", lambda *args, **kwargs: fake_client)
    monkeypatch.setattr(daemon_v2.signal, "signal", lambda *args: None)
    # Make sleep a no-op
    monkeypatch.setattr(daemon_v2.time, "sleep", lambda *args: None)

    result = daemon_v2.run_supervisor(config=config, v2_url="http://localhost:8200")

    # Should succeed after retries
    assert result == 0
    assert fake_client.call_count == 3, f"Expected 3 calls (2 failures + 1 success), got {fake_client.call_count}"


def test_startup_logs_validation_success(tmp_path, monkeypatch) -> None:
    """Worker enabled → logs daemon_v2_worker_validated event."""
    config = _make_config(tmp_path)
    fake_logger = _FakeLogger()

    monkeypatch.setattr(daemon_v2, "DaemonLogger", lambda *args, **kwargs: fake_logger)
    monkeypatch.setattr(daemon_v2, "V2BackendClient", _FakeClientEnabled)
    monkeypatch.setattr(daemon_v2.signal, "signal", lambda *args: None)

    daemon_v2.run_supervisor(config=config, v2_url="http://localhost:8200")

    events = [e[1] for e in fake_logger.events]
    assert "daemon_v2_worker_validated" in events
    assert "daemon_v2_started" in events


def test_startup_logs_error_when_disabled(tmp_path, monkeypatch) -> None:
    """Worker disabled → logs daemon_v2_worker_disabled event."""
    config = _make_config(tmp_path)
    fake_logger = _FakeLogger()

    monkeypatch.setattr(daemon_v2, "DaemonLogger", lambda *args, **kwargs: fake_logger)
    monkeypatch.setattr(daemon_v2, "V2BackendClient", _FakeClientDisabled)

    daemon_v2.run_supervisor(config=config, v2_url="http://localhost:8200")

    events = [e[1] for e in fake_logger.events]
    assert "daemon_v2_worker_disabled" in events


def test_no_register_worker_call_on_startup(tmp_path, monkeypatch) -> None:
    """Verify that register_worker is NOT called during startup."""
    config = _make_config(tmp_path)

    register_called = {"value": False}

    class TrackingClient:
        def __init__(self, base_url: str = "http://localhost:8200"):
            self.base_url = base_url

        def get_worker(self, *, worker_id: str) -> dict:
            return {"worker_id": worker_id, "is_enabled": True}

        def register_worker(self, **kwargs):
            register_called["value"] = True
            return {}

        def heartbeat(self, **kwargs):
            return {"commands": ["shutdown"]}

    monkeypatch.setattr(daemon_v2, "DaemonLogger", lambda *args, **kwargs: _FakeLogger())
    monkeypatch.setattr(daemon_v2, "V2BackendClient", TrackingClient)
    monkeypatch.setattr(daemon_v2.signal, "signal", lambda *args: None)

    daemon_v2.run_supervisor(config=config, v2_url="http://localhost:8200")

    assert register_called["value"] is False


def test_main_loop_survives_unexpected_errors(tmp_path, monkeypatch) -> None:
    """Main loop has top-level exception handler — daemon survives any error."""
    config = _make_config(tmp_path)
    fake_logger = _FakeLogger()

    call_count = {"value": 0}

    class FlakyClient:
        def __init__(self, base_url: str = "http://localhost:8200"):
            self.base_url = base_url

        def get_worker(self, *, worker_id: str) -> dict:
            return {"worker_id": worker_id, "is_enabled": True}

        def heartbeat(self, **kwargs):
            call_count["value"] += 1
            if call_count["value"] == 1:
                # First heartbeat succeeds with shutdown command
                return {"commands": ["shutdown"]}
            return {"commands": []}

    monkeypatch.setattr(daemon_v2, "DaemonLogger", lambda *args, **kwargs: fake_logger)
    monkeypatch.setattr(daemon_v2, "V2BackendClient", FlakyClient)
    monkeypatch.setattr(daemon_v2.signal, "signal", lambda *args: None)

    result = daemon_v2.run_supervisor(config=config, v2_url="http://localhost:8200")

    # Daemon should exit cleanly via shutdown command
    assert result == 0
