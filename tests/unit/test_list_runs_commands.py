"""Unit tests for list_runs_commands module."""
from __future__ import annotations

import json

from agent_runner_v2 import list_runs_commands


class _FakeBackendClient:
    """Fake BackendClient that records calls and returns canned data."""

    def __init__(self, _base_url: str) -> None:
        self.base_url = _base_url

    def list_runs(self, **kwargs):
        """Return a fake list of runs with the kwargs for verification."""
        return {
            "runs": [
                {"id": "run-1", "run_code": "JOB-001", "run_status": "pending", "workflow_name": "agnes_media_gen_v1"},
                {"id": "run-2", "run_code": "JOB-002", "run_status": "awaiting_human", "workflow_name": "agnes_media_gen_v1"},
            ],
            "kwargs": kwargs,
        }


def test_list_runs_default(monkeypatch, capsys) -> None:
    """list-runs with no filters returns all non-terminal runs."""
    monkeypatch.setattr(list_runs_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(
        list_runs_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = list_runs_commands.main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert len(payload["runs"]) == 2
    assert payload["runs"][0]["id"] == "run-1"
    assert payload["kwargs"]["status_group"] == "non_terminal"
    assert payload["kwargs"]["worker_id"] is None
    assert payload["kwargs"]["workflow_name"] is None


def test_list_runs_with_worker_filter(monkeypatch, capsys) -> None:
    """list-runs --worker-id passes the filter to the backend."""
    monkeypatch.setattr(list_runs_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(
        list_runs_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = list_runs_commands.main(["--worker-id", "my-worker-01"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["kwargs"]["worker_id"] == "my-worker-01"


def test_list_runs_with_workflow_filter(monkeypatch, capsys) -> None:
    """list-runs --workflow-name passes the filter to the backend."""
    monkeypatch.setattr(list_runs_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(
        list_runs_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = list_runs_commands.main(["--workflow-name", "agnes_media_gen_v1"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["kwargs"]["workflow_name"] == "agnes_media_gen_v1"


def test_list_runs_status_group_all(monkeypatch, capsys) -> None:
    """list-runs --status-group all passes None (no filter) to the backend."""
    monkeypatch.setattr(list_runs_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(
        list_runs_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = list_runs_commands.main(["--status-group", "all"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["kwargs"]["status_group"] is None


def test_list_runs_backend_error(monkeypatch, capsys) -> None:
    """list-runs prints error JSON to stderr on backend failure."""

    class _ErrorClient:
        def __init__(self, _url):
            pass

        def list_runs(self, **kwargs):
            raise RuntimeError("Connection refused")

    monkeypatch.setattr(list_runs_commands, "BackendClient", _ErrorClient)
    monkeypatch.setattr(
        list_runs_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = list_runs_commands.main([])

    captured = capsys.readouterr()
    assert exit_code == 1
    payload = json.loads(captured.err)
    assert payload["status"] == "error"
    assert "Connection refused" in payload["message"]
