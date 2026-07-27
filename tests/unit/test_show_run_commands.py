"""Unit tests for show_run_commands module."""
from __future__ import annotations

import json

from agent_runner_v2 import show_run_commands


class _FakeBackendClient:
    """Fake BackendClient that returns canned run detail."""

    def __init__(self, _base_url: str) -> None:
        self.base_url = _base_url

    def get_run(self, *, run_id: str):
        """Return a fake run detail with the run_id for verification."""
        return {
            "run": {
                "id": run_id,
                "run_code": "JOB-001",
                "run_status": "pending",
                "workflow_name": "agnes_media_gen_v1",
                "awaiting_human_step": None,
                "active_step_run_id": "step-run-abc",
            },
        }


def test_show_run(monkeypatch, capsys) -> None:
    """show-run returns the run detail for the given run_id."""
    monkeypatch.setattr(show_run_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(
        show_run_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = show_run_commands.main(["run-uuid-123"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["run"]["id"] == "run-uuid-123"
    assert payload["run"]["run_code"] == "JOB-001"
    assert payload["run"]["workflow_name"] == "agnes_media_gen_v1"


def test_show_run_backend_error(monkeypatch, capsys) -> None:
    """show-run prints error JSON to stderr on backend failure."""

    class _ErrorClient:
        def __init__(self, _url):
            pass

        def get_run(self, *, run_id):
            raise RuntimeError("Run not found")

    monkeypatch.setattr(show_run_commands, "BackendClient", _ErrorClient)
    monkeypatch.setattr(
        show_run_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = show_run_commands.main(["nonexistent-id"])

    captured = capsys.readouterr()
    assert exit_code == 1
    payload = json.loads(captured.err)
    assert payload["status"] == "error"
    assert "Run not found" in payload["message"]
