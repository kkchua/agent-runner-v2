"""Unit tests for reset_step_commands module."""
from __future__ import annotations

import json

from agent_runner_v2 import reset_step_commands


class _FakeBackendClient:
    """Fake BackendClient that records reset-step calls."""

    def __init__(self, _base_url: str) -> None:
        self.base_url = _base_url

    def reset_run_step(self, *, run_id: str, step_name: str):
        """Return a fake reset result with the kwargs for verification."""
        return {"status": "ok", "run_id": run_id, "step_name": step_name}


def test_reset_step(monkeypatch, capsys) -> None:
    """reset-step sends the correct run_id and step_name to the backend."""
    monkeypatch.setattr(reset_step_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(
        reset_step_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = reset_step_commands.main(["run-uuid-123", "generate_prompts"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["status"] == "ok"
    assert payload["run_id"] == "run-uuid-123"
    assert payload["step_name"] == "generate_prompts"


def test_reset_step_backend_error(monkeypatch, capsys) -> None:
    """reset-step prints error JSON to stderr on backend failure."""

    class _ErrorClient:
        def __init__(self, _url):
            pass

        def reset_run_step(self, *, run_id, step_name):
            raise RuntimeError("Step not found in workflow")

    monkeypatch.setattr(reset_step_commands, "BackendClient", _ErrorClient)
    monkeypatch.setattr(
        reset_step_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = reset_step_commands.main(["run-uuid-123", "nonexistent_step"])

    captured = capsys.readouterr()
    assert exit_code == 1
    payload = json.loads(captured.err)
    assert payload["status"] == "error"
    assert "Step not found" in payload["message"]
