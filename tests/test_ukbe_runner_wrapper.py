from __future__ import annotations

import os
import subprocess
from pathlib import Path


def test_worker_start_reports_early_crash_and_cleans_pid(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    fake_cli = tmp_path / "fake-ukbe-run-agent.sh"
    fake_cli.write_text("#!/usr/bin/env bash\necho daemon crashed >&2\nexit 1\n", encoding="utf-8")
    fake_cli.chmod(0o755)

    script = Path(__file__).resolve().parents[1] / "scripts" / "ukbe-runner.sh"
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["UKBE_CLI"] = str(fake_cli)

    result = subprocess.run(
        ["bash", str(script), "worker", "start", "test-worker"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 1
    assert "failed to stay running" in result.stdout
    assert f"{home}/.ukbe-runner/logs/worker-test-worker.log" in result.stdout
    assert not (home / ".ukbe-runner" / "workers" / "test-worker.pid").exists()

    worker_log = home / ".ukbe-runner" / "logs" / "worker-test-worker.log"
    assert worker_log.exists()
    assert "daemon crashed" in worker_log.read_text(encoding="utf-8")


def test_worker_status_reports_log_path_when_worker_is_not_running(tmp_path):
    home = tmp_path / "home"
    log_dir = home / ".ukbe-runner" / "logs"
    log_dir.mkdir(parents=True)
    worker_log = log_dir / "worker-test-worker.log"
    worker_log.write_text("previous failure\n", encoding="utf-8")

    script = Path(__file__).resolve().parents[1] / "scripts" / "ukbe-runner.sh"
    env = os.environ.copy()
    env["HOME"] = str(home)

    result = subprocess.run(
        ["bash", str(script), "worker", "status", "test-worker"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 1
    assert "is not running" in result.stdout
    assert str(worker_log) in result.stdout
