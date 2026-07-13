from __future__ import annotations

import json

from agent_runner_v2 import submit_commands


class _FailingBackendClient:
    def __init__(self, _base_url: str) -> None:
        pass

    def submit_run(self, **_kwargs):
        raise RuntimeError(
            "Backend request failed: POST /api/runs status=404 "
            "body={\"detail\":\"Workflow '00_master_docs_bootstrap_v2' not found\"}"
        )


def test_submit_command_returns_json_error_when_backend_rejects(monkeypatch, capsys):
    monkeypatch.setattr(submit_commands, "BackendClient", _FailingBackendClient)
    monkeypatch.setattr(submit_commands, "_load_config", lambda: {})

    exit_code = submit_commands.main(
        [
            "--workflow-name",
            "00_master_docs_bootstrap_v2",
            "--project-root",
            "D:/MyProjectSpace/01_Workflows/agent-runner-v2",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    payload = json.loads(captured.err.strip())
    assert payload["status"] == "error"
    assert payload["code"] == "workflow_not_found"
    assert "Workflow '00_master_docs_bootstrap_v2' is not registered in the backend" in payload["message"]
