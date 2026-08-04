"""Tests for daemon_v2's pre-spawn backend state durability wait.

Regression: the backend commits claim transactions AFTER its response is
sent (FastAPI dependency teardown), so a get_run immediately after a claim
can return the pre-claim state. _fetch_and_write_backend_state must poll
until the claimed step run is visible, or the child's outcome POST would
404 with "Step run not found" and the run would stall forever.
"""
from __future__ import annotations

import json
from pathlib import Path

from agent_runner_v2 import daemon_v2


class _FakeLogger:
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    def log(self, level: str, event: str, *, message: str = "", details: dict | None = None) -> None:
        self.events.append((event, message))


def _make_client(sequence: list[dict]) -> tuple[type, dict]:
    """Fake V2BackendClient returning run states from a fixed sequence."""
    calls = {"count": 0}

    class FakeClient:
        def __init__(self, base_url: str = "http://backend:8200"):
            self.base_url = base_url

        def get_run(self, *, run_id: str) -> dict:
            idx = min(calls["count"], len(sequence) - 1)
            calls["count"] += 1
            return sequence[idx]

    return FakeClient, calls


def _run_state(current_step_run_id: str | None, run_status: str = "RUNNING") -> dict:
    return {
        "run_id": "run-1",
        "run_code": "JOB-1",
        "workflow_name": "agnes_media_gen_v1",
        "run_status": run_status,
        "current_step": "archive_step_02",
        "current_step_run_id": current_step_run_id,
    }


def test_waits_until_claimed_step_run_is_durable(tmp_path) -> None:
    """Stale pre-claim state followed by durable state → writes the durable one."""
    client_cls, calls = _make_client([
        _run_state(None, run_status="PENDING"),  # pre-claim (stale)
        _run_state("sr-1"),                       # durable
    ])
    logger = _FakeLogger()

    path = daemon_v2._fetch_and_write_backend_state(
        client=client_cls(),
        run_id="run-1",
        step_run_id="sr-1",
        child_dir=tmp_path,
        logger=logger,
        timeout_seconds=5.0,
    )

    assert path is not None
    assert calls["count"] == 2
    written = json.loads(Path(path).read_text(encoding="utf-8"))
    assert written["current_step_run_id"] == "sr-1"
    assert written["run_status"] == "RUNNING"


def test_returns_none_when_step_run_never_becomes_durable(tmp_path, monkeypatch) -> None:
    """Claim never becomes visible → None, no state file, loud log event."""
    client_cls, _ = _make_client([_run_state(None, run_status="PENDING")])

    class _AdvancingTime:
        def __init__(self) -> None:
            self._now = 0.0

        def monotonic(self) -> float:
            self._now += 1.0
            return self._now

        def sleep(self, _seconds: float) -> None:
            return None

    monkeypatch.setattr(daemon_v2, "time", _AdvancingTime())
    logger = _FakeLogger()

    path = daemon_v2._fetch_and_write_backend_state(
        client=client_cls(),
        run_id="run-1",
        step_run_id="sr-1",
        child_dir=tmp_path,
        logger=logger,
        timeout_seconds=0.5,
    )

    assert path is None
    assert not (tmp_path / "backend_state.json").exists()
    assert any(event == "daemon_v2_claim_not_durable" for event, _ in logger.events)


def test_writes_immediately_when_claim_already_durable(tmp_path) -> None:
    """First get_run already shows the claimed step run → single fetch."""
    client_cls, calls = _make_client([_run_state("sr-1")])
    logger = _FakeLogger()

    path = daemon_v2._fetch_and_write_backend_state(
        client=client_cls(),
        run_id="run-1",
        step_run_id="sr-1",
        child_dir=tmp_path,
        logger=logger,
    )

    assert path is not None
    assert calls["count"] == 1
    written = json.loads(Path(path).read_text(encoding="utf-8"))
    assert written["current_step_run_id"] == "sr-1"
