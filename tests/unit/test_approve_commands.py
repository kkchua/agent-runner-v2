"""Unit tests for approve_commands module."""
from __future__ import annotations

import json

from agent_runner_v2 import approve_commands


class _FakeBackendClient:
    """Fake BackendClient that records sync_job_state calls."""

    def __init__(self, _base_url: str) -> None:
        self.base_url = _base_url
        self.sync_calls = []
        self.run_detail = {
            "run": {
                "id": "run-1",
                "current_step_run_id": "step-run-1",
                "current_step": "review_step",
            }
        }

    def get_run(self, *, run_id: str) -> dict:
        """Return a fake run detail."""
        return self.run_detail

    def sync_job_state(self, *, step_run_id: str, payload: dict) -> dict:
        """Record the sync call and return success."""
        self.sync_calls.append({"step_run_id": step_run_id, "payload": payload})
        return {"status": "ok"}


def test_approve_default(monkeypatch, capsys) -> None:
    """approve with no flags sets approve_requested flag."""
    fake_client = _FakeBackendClient("http://127.0.0.1:8100")
    monkeypatch.setattr(approve_commands, "BackendClient", lambda url: fake_client)
    monkeypatch.setattr(
        approve_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = approve_commands.main(["run-1"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert len(fake_client.sync_calls) == 1
    payload = fake_client.sync_calls[0]["payload"]
    assert payload["context_payload"]["__run_control"]["approve_requested"] is True
    assert payload["context_payload"]["__run_control"]["action_step"] == "review_step"
    output = json.loads(captured.out)
    assert output["action"] == "approve_requested"


def test_approve_reject(monkeypatch, capsys) -> None:
    """approve --reject sets reject_requested flag."""
    fake_client = _FakeBackendClient("http://127.0.0.1:8100")
    monkeypatch.setattr(approve_commands, "BackendClient", lambda url: fake_client)
    monkeypatch.setattr(
        approve_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = approve_commands.main(["run-1", "--reject", "--feedback", "Needs work"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert len(fake_client.sync_calls) == 1
    payload = fake_client.sync_calls[0]["payload"]
    assert payload["context_payload"]["__run_control"]["reject_requested"] is True
    assert payload["context_payload"]["__run_control"]["feedback"] == "Needs work"
    output = json.loads(captured.out)
    assert output["action"] == "reject_requested"


def test_approve_resume(monkeypatch, capsys) -> None:
    """approve --resume sets resume_requested flag with default feedback."""
    fake_client = _FakeBackendClient("http://127.0.0.1:8100")
    monkeypatch.setattr(approve_commands, "BackendClient", lambda url: fake_client)
    monkeypatch.setattr(
        approve_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = approve_commands.main(["run-1", "--resume"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert len(fake_client.sync_calls) == 1
    payload = fake_client.sync_calls[0]["payload"]
    assert payload["context_payload"]["__run_control"]["resume_requested"] is True
    assert payload["context_payload"]["__run_control"]["feedback"] == "Resumed by operator"


def test_approve_retry(monkeypatch, capsys) -> None:
    """approve --retry sets retry_requested flag with default feedback."""
    fake_client = _FakeBackendClient("http://127.0.0.1:8100")
    monkeypatch.setattr(approve_commands, "BackendClient", lambda url: fake_client)
    monkeypatch.setattr(
        approve_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = approve_commands.main(["run-1", "--retry"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert len(fake_client.sync_calls) == 1
    payload = fake_client.sync_calls[0]["payload"]
    assert payload["context_payload"]["__run_control"]["retry_requested"] is True
    assert payload["context_payload"]["__run_control"]["feedback"] == "Retried by operator"


def test_approve_resume_with_custom_feedback(monkeypatch, capsys) -> None:
    """approve --resume --feedback 'custom' uses the custom feedback."""
    fake_client = _FakeBackendClient("http://127.0.0.1:8100")
    monkeypatch.setattr(approve_commands, "BackendClient", lambda url: fake_client)
    monkeypatch.setattr(
        approve_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = approve_commands.main(["run-1", "--resume", "--feedback", "Fixed the issue"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = fake_client.sync_calls[0]["payload"]
    assert payload["context_payload"]["__run_control"]["feedback"] == "Fixed the issue"


def test_approve_backend_error(monkeypatch, capsys) -> None:
    """approve prints error JSON to stderr on backend failure."""

    class _ErrorClient:
        def __init__(self, _url):
            pass

        def get_run(self, *, run_id: str):
            raise RuntimeError("Run not found")

    monkeypatch.setattr(approve_commands, "BackendClient", _ErrorClient)
    monkeypatch.setattr(
        approve_commands, "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = approve_commands.main(["nonexistent-id"])

    captured = capsys.readouterr()
    # Should still succeed because get_run failure is non-fatal
    # but will fail because step_run_id is empty
    assert exit_code == 1
    output = json.loads(captured.err)
    assert output["status"] == "error"
