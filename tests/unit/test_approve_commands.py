"""Unit tests for approve_commands module."""
from __future__ import annotations

import json

from agent_runner_v2 import approve_commands


class _FakeBackendClient:
    """Fake BackendClient that records approve calls."""

    def __init__(self, _base_url: str) -> None:
        self.base_url = _base_url

    def approve_run(self, **kwargs):
        """Return a fake approve result with the kwargs for verification."""
        return {"status": "ok", "kwargs": kwargs}


def test_approve_default(monkeypatch, capsys) -> None:
    """approve with no flags sends action=approve."""
    monkeypatch.setattr(approve_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(
        approve_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = approve_commands.main(["run-1"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["kwargs"]["action"] == "approve"
    assert payload["kwargs"]["run_id"] == "run-1"
    assert payload["kwargs"]["feedback"] is None


def test_approve_reject(monkeypatch, capsys) -> None:
    """approve --reject sends action=reject."""
    monkeypatch.setattr(approve_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(
        approve_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = approve_commands.main(["run-1", "--reject", "--feedback", "Needs work"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["kwargs"]["action"] == "reject"
    assert payload["kwargs"]["feedback"] == "Needs work"


def test_approve_resume(monkeypatch, capsys) -> None:
    """approve --resume sends action=approve with default resume feedback."""
    monkeypatch.setattr(approve_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(
        approve_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = approve_commands.main(["run-1", "--resume"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["kwargs"]["action"] == "approve"
    assert payload["kwargs"]["feedback"] == "Resumed by operator"


def test_approve_retry(monkeypatch, capsys) -> None:
    """approve --retry sends action=approve with default retry feedback."""
    monkeypatch.setattr(approve_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(
        approve_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = approve_commands.main(["run-1", "--retry"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["kwargs"]["action"] == "approve"
    assert payload["kwargs"]["feedback"] == "Retried by operator"


def test_approve_resume_with_custom_feedback(monkeypatch, capsys) -> None:
    """approve --resume --feedback 'custom' uses the custom feedback."""
    monkeypatch.setattr(approve_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(
        approve_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = approve_commands.main(["run-1", "--resume", "--feedback", "Fixed the issue"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["kwargs"]["feedback"] == "Fixed the issue"


def test_approve_backend_error(monkeypatch, capsys) -> None:
    """approve prints error JSON to stderr on backend failure."""

    class _ErrorClient:
        def __init__(self, _url):
            pass

        def approve_run(self, **kwargs):
            raise RuntimeError("Run not found")

    monkeypatch.setattr(approve_commands, "BackendClient", _ErrorClient)
    monkeypatch.setattr(
        approve_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = approve_commands.main(["nonexistent-id"])

    captured = capsys.readouterr()
    assert exit_code == 1
    payload = json.loads(captured.err)
    assert payload["status"] == "error"
    assert "Run not found" in payload["message"]
