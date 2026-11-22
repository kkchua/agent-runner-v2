"""Tests for baseline transaction management (plan_first_review_v1).

Covers:
- validate_immutable_operation (phase-aware, ownership, ledger)
- complete_baseline_transaction (atomic, idempotent, durable)
- get_planning_folder helper
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

import agent_runner_v2.job_state as job_state
from agent_runner_v2.exceptions import TransactionConflictError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_save_job(monkeypatch):
    """Mock save_job to avoid disk writes."""
    saved = []
    monkeypatch.setattr(job_state, "save_job", lambda *a: saved.append(a))
    return saved


@pytest.fixture
def mock_now_iso(monkeypatch):
    """Mock now_iso to return fixed timestamp."""
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-11-19T00:00:00")


@pytest.fixture
def base_state():
    """Base state dict for transaction tests."""
    return {
        "job_id": "test-job-123",
        "template_group": "plan_first_review_v1",
        "requirements_baseline": 1,
        "artifacts": {
            "PLANNING_FOLDER": "Planning/test-project",
        },
        "baseline_commits": {},
    }


@pytest.fixture
def base_operation():
    """Base operation dict for validation tests."""
    return {
        "operation_id": "op_abc123",
        "request_id": "req_xyz789",
        "group_name": "plan_first_review_v1",
        "job_id": "test-job-123",
        "ending_baseline": 1,
        "new_baseline": 2,
        "request_hash": "deadbeef" * 8,
        "canonical_paths": {
            "request": "Planning/test-project/baseline_02/request.md",
            "operation": "Planning/test-project/baseline_02/operation.json",
        },
    }


# ---------------------------------------------------------------------------
# get_planning_folder tests
# ---------------------------------------------------------------------------

def test_get_planning_folder_returns_value(base_state):
    """get_planning_folder returns the PLANNING_FOLDER from artifacts."""
    result = job_state.get_planning_folder(base_state)
    assert result == "Planning/test-project"


def test_get_planning_folder_raises_on_missing():
    """get_planning_folder raises ValueError when PLANNING_FOLDER is missing."""
    state = {"artifacts": {}}
    with pytest.raises(ValueError, match="Missing PLANNING_FOLDER"):
        job_state.get_planning_folder(state)


def test_get_planning_folder_raises_on_empty():
    """get_planning_folder raises ValueError when PLANNING_FOLDER is empty."""
    state = {"artifacts": {"PLANNING_FOLDER": ""}}
    with pytest.raises(ValueError, match="Missing PLANNING_FOLDER"):
        job_state.get_planning_folder(state)


# ---------------------------------------------------------------------------
# validate_immutable_operation tests
# ---------------------------------------------------------------------------

def test_validate_operation_staging_phase(base_state, base_operation, tmp_path):
    """validate_immutable_operation accepts valid staging phase operation."""
    project_root = tmp_path
    planning_folder = "Planning/test-project"
    staging_dir = project_root / planning_folder / ".staging_op_abc123"
    staging_dir.mkdir(parents=True)

    result = job_state.validate_immutable_operation(
        existing_op=base_operation,
        operation_id="op_abc123",
        request_id="req_xyz789",
        request_bytes=b"test request",
        incoming_request_hash="deadbeef" * 8,
        ending_baseline=1,
        actual_dir=staging_dir,
        state=base_state,
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        project_root=project_root,
        phase="staging",
    )

    assert result["operation_id"] == "op_abc123"
    assert "manifest_hash" in result


def test_validate_operation_final_phase(base_state, base_operation, tmp_path):
    """validate_immutable_operation accepts valid final phase operation."""
    project_root = tmp_path
    planning_folder = "Planning/test-project"
    final_dir = project_root / planning_folder / "baseline_02"
    final_dir.mkdir(parents=True)

    result = job_state.validate_immutable_operation(
        existing_op=base_operation,
        operation_id="op_abc123",
        request_id="req_xyz789",
        request_bytes=b"test request",
        incoming_request_hash="deadbeef" * 8,
        ending_baseline=1,
        actual_dir=final_dir,
        state=base_state,
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        project_root=project_root,
        phase="final",
    )

    assert result["operation_id"] == "op_abc123"


def test_validate_operation_rejects_wrong_group(base_state, base_operation, tmp_path):
    """validate_immutable_operation rejects operation with wrong group_name."""
    project_root = tmp_path
    final_dir = project_root / "Planning/test-project/baseline_02"
    final_dir.mkdir(parents=True)

    with pytest.raises(TransactionConflictError, match="Group name mismatch"):
        job_state.validate_immutable_operation(
            existing_op=base_operation,
            operation_id="op_abc123",
            request_id="req_xyz789",
            request_bytes=b"test request",
            incoming_request_hash="deadbeef" * 8,
            ending_baseline=1,
            actual_dir=final_dir,
            state=base_state,
            group_name="wrong_group",  # Wrong group
            job_id="test-job-123",
            project_root=project_root,
            phase="final",
        )


def test_validate_operation_rejects_wrong_job(base_state, base_operation, tmp_path):
    """validate_immutable_operation rejects operation with wrong job_id."""
    project_root = tmp_path
    final_dir = project_root / "Planning/test-project/baseline_02"
    final_dir.mkdir(parents=True)

    with pytest.raises(TransactionConflictError, match="Job ID mismatch"):
        job_state.validate_immutable_operation(
            existing_op=base_operation,
            operation_id="op_abc123",
            request_id="req_xyz789",
            request_bytes=b"test request",
            incoming_request_hash="deadbeef" * 8,
            ending_baseline=1,
            actual_dir=final_dir,
            state=base_state,
            group_name="plan_first_review_v1",
            job_id="wrong-job-id",  # Wrong job
            project_root=project_root,
            phase="final",
        )


def test_validate_operation_rejects_bool_baseline(base_state, tmp_path):
    """validate_immutable_operation rejects bool ending_baseline."""
    project_root = tmp_path
    final_dir = project_root / "Planning/test-project/baseline_02"
    final_dir.mkdir(parents=True)

    op = {
        "operation_id": "op_abc123",
        "request_id": "req_xyz789",
        "group_name": "plan_first_review_v1",
        "job_id": "test-job-123",
        "ending_baseline": True,  # Bool instead of int
        "new_baseline": 2,
        "request_hash": "deadbeef" * 8,
        "canonical_paths": {
            "request": "Planning/test-project/baseline_02/request.md",
            "operation": "Planning/test-project/baseline_02/operation.json",
        },
    }

    with pytest.raises(TransactionConflictError, match="ending_baseline is not an integer"):
        job_state.validate_immutable_operation(
            existing_op=op,
            operation_id="op_abc123",
            request_id="req_xyz789",
            request_bytes=b"test request",
            incoming_request_hash="deadbeef" * 8,
            ending_baseline=1,
            actual_dir=final_dir,
            state=base_state,
            group_name="plan_first_review_v1",
            job_id="test-job-123",
            project_root=project_root,
            phase="final",
        )


def test_validate_operation_committed_replay_with_ledger(base_state, base_operation, tmp_path):
    """validate_immutable_operation validates committed replay against ledger."""
    project_root = tmp_path
    final_dir = project_root / "Planning/test-project/baseline_02"
    final_dir.mkdir(parents=True)

    # Add commit record to ledger
    base_state["baseline_commits"]["req_xyz789"] = {
        "request_id": "req_xyz789",
        "operation_id": "op_abc123",
        "operation": base_operation,
        "result": {"status": "committed", "baseline": 2},
    }

    result = job_state.validate_immutable_operation(
        existing_op=base_operation,
        operation_id="op_abc123",
        request_id="req_xyz789",
        request_bytes=b"test request",
        incoming_request_hash="deadbeef" * 8,
        ending_baseline=1,
        actual_dir=final_dir,
        state=base_state,
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        project_root=project_root,
        phase="committed_replay",
        commit_ledger=base_state["baseline_commits"],
    )

    assert result["operation_id"] == "op_abc123"


def test_validate_operation_committed_replay_rejects_missing_ledger(base_state, base_operation, tmp_path):
    """validate_immutable_operation rejects committed replay without ledger record."""
    project_root = tmp_path
    final_dir = project_root / "Planning/test-project/baseline_02"
    final_dir.mkdir(parents=True)

    with pytest.raises(TransactionConflictError, match="Committed replay requires commit ledger|No commit record"):
        job_state.validate_immutable_operation(
            existing_op=base_operation,
            operation_id="op_abc123",
            request_id="req_xyz789",
            request_bytes=b"test request",
            incoming_request_hash="deadbeef" * 8,
            ending_baseline=1,
            actual_dir=final_dir,
            state=base_state,
            group_name="plan_first_review_v1",
            job_id="test-job-123",
            project_root=project_root,
            phase="committed_replay",
            commit_ledger={},  # Empty ledger
        )


# ---------------------------------------------------------------------------
# complete_baseline_transaction tests
# ---------------------------------------------------------------------------

def test_complete_transaction_writes_files(base_state, mock_save_job, mock_now_iso, tmp_path):
    """complete_baseline_transaction writes request.md and operation.json."""
    project_root = tmp_path
    planning_folder = "Planning/test-project"

    result = job_state.complete_baseline_transaction(
        state=base_state,
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        request_id="req_xyz789",
        operation_id="op_abc123",
        request_bytes=b"test request content",
        request_hash="deadbeef" * 8,
        ending_baseline=1,
        new_baseline=2,
        planning_folder=planning_folder,
        project_root=project_root,
        commit_ledger=base_state["baseline_commits"],
    )

    # Verify result
    assert result["status"] == "committed"
    assert result["baseline"] == 2

    # Verify files were written
    final_dir = project_root / planning_folder / "baseline_02"
    assert (final_dir / "request.md").exists()
    assert (final_dir / "operation.json").exists()

    # Verify state was updated
    assert base_state["requirements_baseline"] == 2

    # Verify commit ledger was updated
    assert "req_xyz789" in base_state["baseline_commits"]


def test_complete_transaction_idempotent(base_state, mock_save_job, mock_now_iso, tmp_path):
    """complete_baseline_transaction is idempotent for same request_id."""
    project_root = tmp_path
    planning_folder = "Planning/test-project"

    # First call
    result1 = job_state.complete_baseline_transaction(
        state=base_state,
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        request_id="req_xyz789",
        operation_id="op_abc123",
        request_bytes=b"test request content",
        request_hash="deadbeef" * 8,
        ending_baseline=1,
        new_baseline=2,
        planning_folder=planning_folder,
        project_root=project_root,
        commit_ledger=base_state["baseline_commits"],
    )

    # Second call with same request_id
    result2 = job_state.complete_baseline_transaction(
        state=base_state,
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        request_id="req_xyz789",
        operation_id="op_abc123",
        request_bytes=b"test request content",
        request_hash="deadbeef" * 8,
        ending_baseline=1,
        new_baseline=2,
        planning_folder=planning_folder,
        project_root=project_root,
        commit_ledger=base_state["baseline_commits"],
    )

    # Should return same result without re-writing
    assert result1 == result2


def test_complete_transaction_rejects_wrong_baseline_transition(base_state, mock_save_job, mock_now_iso, tmp_path):
    """complete_baseline_transaction rejects new_baseline != ending_baseline + 1."""
    project_root = tmp_path
    planning_folder = "Planning/test-project"

    with pytest.raises(TransactionConflictError, match="new_baseline.*!=.*ending_baseline"):
        job_state.complete_baseline_transaction(
            state=base_state,
            group_name="plan_first_review_v1",
            job_id="test-job-123",
            request_id="req_xyz789",
            operation_id="op_abc123",
            request_bytes=b"test request content",
            request_hash="deadbeef" * 8,
            ending_baseline=1,
            new_baseline=3,  # Wrong: should be 2
            planning_folder=planning_folder,
            project_root=project_root,
            commit_ledger=base_state["baseline_commits"],
        )


def test_complete_transaction_rejects_ledger_conflict(base_state, mock_save_job, mock_now_iso, tmp_path):
    """complete_baseline_transaction rejects conflicting operation_id for same request_id."""
    project_root = tmp_path
    planning_folder = "Planning/test-project"

    # Pre-populate ledger with different operation_id
    base_state["baseline_commits"]["req_xyz789"] = {
        "request_id": "req_xyz789",
        "operation_id": "op_different",
        "operation": {},
        "result": {"status": "committed", "baseline": 2},
    }

    with pytest.raises(TransactionConflictError, match="different operation_id"):
        job_state.complete_baseline_transaction(
            state=base_state,
            group_name="plan_first_review_v1",
            job_id="test-job-123",
            request_id="req_xyz789",
            operation_id="op_abc123",  # Different from ledger
            request_bytes=b"test request content",
            request_hash="deadbeef" * 8,
            ending_baseline=1,
            new_baseline=2,
            planning_folder=planning_folder,
            project_root=project_root,
            commit_ledger=base_state["baseline_commits"],
        )
