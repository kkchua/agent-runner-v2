"""Tests for daemon_v2._child_outcome_action race condition fix.

Regression: when a child exits after its outcome was already processed and
archived by _process_queue, the daemon used to write a false failure because
the queue file no longer existed. _child_outcome_action now checks the
archive/ and failed/ directories before deciding to write a failure.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from agent_runner_v2.daemon_v2 import ChildExecution, _child_outcome_action


def _make_child(tmp_path: Path, step_run_id: str = "sr-abc") -> ChildExecution:
    """Create a minimal ChildExecution for testing."""
    queue_dir = tmp_path / "queue"
    queue_dir.mkdir(exist_ok=True)
    return ChildExecution(
        run_id="run-1",
        run_code="JOB-1",
        step_run_id=step_run_id,
        step_name="test_step",
        run_payload={},
        step_run_payload={},
        request_payload={},
        request_path=tmp_path / "req.json",
        result_path=tmp_path / "result.json",
        combined_log_path=tmp_path / "combined.log",
        child_event_log_path=tmp_path / "events.jsonl",
        process=MagicMock(),
        started_at_monotonic=0.0,
        started_at_iso="2026-08-08T00:00:00",
        exit_code=0,
        queue_dir=queue_dir,
    )


class TestChildOutcomeAction:
    def test_queue_file_exists_returns_queue(self, tmp_path):
        child = _make_child(tmp_path)
        (child.queue_dir / f"{child.step_run_id}.json").write_text("{}")

        assert _child_outcome_action(child) == "queue"

    def test_archived_outcome_returns_skip(self, tmp_path):
        """Race condition: outcome was processed and archived while child was still alive."""
        child = _make_child(tmp_path)
        archive_dir = child.queue_dir / "archive"
        archive_dir.mkdir()
        (archive_dir / f"{child.step_run_id}.json").write_text("{}")

        assert _child_outcome_action(child) == "skip"

    def test_failed_outcome_returns_skip(self, tmp_path):
        """Outcome was permanently failed (409) — don't write another failure."""
        child = _make_child(tmp_path)
        failed_dir = child.queue_dir / "failed"
        failed_dir.mkdir()
        (failed_dir / f"{child.step_run_id}.json").write_text("{}")

        assert _child_outcome_action(child) == "skip"

    def test_no_files_returns_failure(self, tmp_path):
        """No outcome anywhere — daemon should write a failure."""
        child = _make_child(tmp_path)

        assert _child_outcome_action(child) == "failure"

    def test_no_queue_dir_returns_failure(self, tmp_path):
        """Child has no queue_dir configured — must write failure."""
        child = _make_child(tmp_path)
        child.queue_dir = None

        assert _child_outcome_action(child) == "failure"

    def test_queue_file_takes_priority_over_archive(self, tmp_path):
        """If both pending and archived exist (shouldn't happen), pending wins."""
        child = _make_child(tmp_path)
        (child.queue_dir / f"{child.step_run_id}.json").write_text("{}")
        archive_dir = child.queue_dir / "archive"
        archive_dir.mkdir()
        (archive_dir / f"{child.step_run_id}.json").write_text("{}")

        assert _child_outcome_action(child) == "queue"
