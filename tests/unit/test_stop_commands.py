from __future__ import annotations

import json

from agent_runner_v2 import stop_commands


class _FakeBackendClient:
    def __init__(self, _base_url: str) -> None:
        self.base_url = _base_url

    def stop_run(self, **kwargs):
        return {"status": "ok", "kwargs": kwargs}


def test_stop_command_uses_backend_config(monkeypatch, capsys) -> None:
    monkeypatch.setattr(stop_commands, "BackendClient", _FakeBackendClient)
    monkeypatch.setattr(
        stop_commands,
        "_load_config",
        lambda: {"backend_url": "http://127.0.0.1:8100"},
    )

    exit_code = stop_commands.main(["run-1", "--reason", "Operator requested stop"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["status"] == "ok"
    assert payload["kwargs"] == {
        "run_id": "run-1",
        "reason": "Operator requested stop",
        "mode": "after_current_step",
    }
