"""Tests for V2 outcome queue — file-based CLI→daemon handoff."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from agent_runner_v2.v2.queue import (
    archive_outcome,
    ensure_queue_dir,
    fail_outcome,
    get_queue_dir,
    list_pending_outcomes,
    read_outcome,
    write_outcome,
)


@pytest.fixture
def queue_root(tmp_path: Path) -> Path:
    return tmp_path / "queue"


class TestGetQueueDir:
    def test_default_date_is_today(self, queue_root: Path):
        from datetime import datetime
        today = datetime.now().strftime("%Y%m%d")
        result = get_queue_dir(queue_root, "my_workflow", "JOB-001")
        expected = queue_root / today / "my_workflow" / "JOB-001"
        assert result == expected

    def test_explicit_date(self, queue_root: Path):
        result = get_queue_dir(queue_root, "my_workflow", "JOB-001", date="20260804")
        expected = queue_root / "20260804" / "my_workflow" / "JOB-001"
        assert result == expected


class TestWriteOutcome:
    def test_writes_json_file(self, queue_root: Path):
        qdir = queue_root / "20260804" / "wf" / "job1"
        result = write_outcome(qdir, "step-uuid-1", {
            "step_run_id": "step-uuid-1",
            "outcome": "approved",
        })
        assert result.exists()
        assert result.name == "step-uuid-1.json"
        data = json.loads(result.read_text(encoding="utf-8"))
        assert data["outcome"] == "approved"
        assert data["step_run_id"] == "step-uuid-1"
        assert "timestamp" in data

    def test_creates_subfolders(self, queue_root: Path):
        qdir = queue_root / "20260804" / "wf" / "job1"
        write_outcome(qdir, "s1", {"step_run_id": "s1", "outcome": "approved"})
        assert (qdir / "archive").is_dir()
        assert (qdir / "failed").is_dir()

    def test_atomic_write_no_partial(self, queue_root: Path):
        qdir = queue_root / "20260804" / "wf" / "job1"
        write_outcome(qdir, "s1", {"step_run_id": "s1", "outcome": "failed"})
        # No temp files should remain
        temp_files = list(qdir.glob(".tmp_*"))
        assert len(temp_files) == 0


class TestReadOutcome:
    def test_reads_valid_file(self, queue_root: Path):
        qdir = queue_root / "20260804" / "wf" / "job1"
        write_outcome(qdir, "s1", {"step_run_id": "s1", "outcome": "approved"})
        data = read_outcome(qdir / "s1.json")
        assert data is not None
        assert data["outcome"] == "approved"

    def test_returns_none_for_missing_file(self, queue_root: Path):
        assert read_outcome(queue_root / "nonexistent.json") is None

    def test_returns_none_for_invalid_json(self, queue_root: Path):
        qdir = queue_root / "20260804" / "wf" / "job1"
        qdir.mkdir(parents=True)
        bad = qdir / "bad.json"
        bad.write_text("not json", encoding="utf-8")
        assert read_outcome(bad) is None

    def test_returns_none_for_missing_required_fields(self, queue_root: Path):
        qdir = queue_root / "20260804" / "wf" / "job1"
        qdir.mkdir(parents=True)
        incomplete = qdir / "incomplete.json"
        incomplete.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")
        assert read_outcome(incomplete) is None


class TestArchiveOutcome:
    def test_moves_to_archive(self, queue_root: Path):
        qdir = queue_root / "20260804" / "wf" / "job1"
        write_outcome(qdir, "s1", {"step_run_id": "s1", "outcome": "approved"})
        file_path = qdir / "s1.json"
        assert file_path.exists()
        assert archive_outcome(file_path) is True
        assert not file_path.exists()
        assert (qdir / "archive" / "s1.json").exists()


class TestFailOutcome:
    def test_moves_to_failed(self, queue_root: Path):
        qdir = queue_root / "20260804" / "wf" / "job1"
        write_outcome(qdir, "s1", {"step_run_id": "s1", "outcome": "failed"})
        file_path = qdir / "s1.json"
        assert fail_outcome(file_path) is True
        assert not file_path.exists()
        assert (qdir / "failed" / "s1.json").exists()


class TestListPendingOutcomes:
    def test_finds_pending_files(self, queue_root: Path):
        qdir1 = queue_root / "20260804" / "wf1" / "job1"
        qdir2 = queue_root / "20260804" / "wf2" / "job2"
        write_outcome(qdir1, "s1", {"step_run_id": "s1", "outcome": "approved"})
        write_outcome(qdir2, "s2", {"step_run_id": "s2", "outcome": "failed"})
        pending = list_pending_outcomes(queue_root)
        assert len(pending) == 2
        names = {p.name for p in pending}
        assert names == {"s1.json", "s2.json"}

    def test_excludes_archived(self, queue_root: Path):
        qdir = queue_root / "20260804" / "wf" / "job1"
        write_outcome(qdir, "s1", {"step_run_id": "s1", "outcome": "approved"})
        archive_outcome(qdir / "s1.json")
        pending = list_pending_outcomes(queue_root)
        assert len(pending) == 0

    def test_excludes_failed(self, queue_root: Path):
        qdir = queue_root / "20260804" / "wf" / "job1"
        write_outcome(qdir, "s1", {"step_run_id": "s1", "outcome": "failed"})
        fail_outcome(qdir / "s1.json")
        pending = list_pending_outcomes(queue_root)
        assert len(pending) == 0

    def test_excludes_temp_files(self, queue_root: Path):
        qdir = queue_root / "20260804" / "wf" / "job1"
        qdir.mkdir(parents=True)
        (qdir / ".tmp_xxx.json").write_text("{}", encoding="utf-8")
        pending = list_pending_outcomes(queue_root)
        assert len(pending) == 0

    def test_empty_queue_root(self, queue_root: Path):
        assert list_pending_outcomes(queue_root) == []

    def test_nonexistent_queue_root(self, tmp_path: Path):
        assert list_pending_outcomes(tmp_path / "nonexistent") == []
