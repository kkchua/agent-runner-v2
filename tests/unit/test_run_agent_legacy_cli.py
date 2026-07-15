from __future__ import annotations

import json

from agent_runner_v2 import run_agent


def test_main_worker_command_delegates_to_daemon(monkeypatch):
    captured: dict[str, object] = {}

    def fake_daemon_main(argv=None):
        captured["argv"] = list(argv or [])
        return 0

    monkeypatch.setattr("agent_runner_v2.daemon.main", fake_daemon_main)

    rc = run_agent.main(
        [
            "worker",
            "--backend-url", "http://127.0.0.1:8100",
            "--worker-id", "worker-1",
            "--poll-seconds", "7",
            "--engine-root", "C:/engine",
            "--worker-label", "dev",
            "--once",
        ]
    )

    assert rc == 0
    assert captured["argv"] == [
        "worker-1",
        "--worker-label", "dev",
        "--backend-url", "http://127.0.0.1:8100",
        "--poll-seconds", "7",
        "--once",
        "--engine-root", "C:/engine",
    ]


def test_main_execute_step_returns_legacy_error(tmp_path, capsys):
    request_path = tmp_path / "request.json"
    result_path = tmp_path / "result.json"
    request_path.write_text("{}", encoding="utf-8")

    rc = run_agent.main(
        [
            "execute-step",
            "--request-file", str(request_path),
            "--result-file", str(result_path),
        ]
    )

    assert rc == 2
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert payload["failure"]["failure_code"] == "LEGACY_EXECUTE_STEP_UNSUPPORTED"
    assert "no longer supported" in payload["remark"]

    stdout_payload = json.loads(capsys.readouterr().out)
    assert stdout_payload["failure"]["failure_code"] == "LEGACY_EXECUTE_STEP_UNSUPPORTED"
