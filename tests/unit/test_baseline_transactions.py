"""Tests for baseline transaction management (plan_first_review_v1).

Covers:
- validate_immutable_operation (phase-aware, ownership, ledger)
- complete_baseline_transaction (atomic, idempotent, durable)
- get_planning_folder helper
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

import agent_runner_v2.job_state as job_state
from agent_runner_v2.exceptions import TransactionConflictError


TEST_REQUEST_BYTES = b"test request"
TEST_REQUEST_HASH = hashlib.sha256(TEST_REQUEST_BYTES).hexdigest()
TEST_SNAPSHOT_BYTES = b"{}"
TEST_SNAPSHOT_HASH = hashlib.sha256(TEST_SNAPSHOT_BYTES).hexdigest()


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
    operation = {
        "operation_id": "op_abc123",
        "request_id": "req_xyz789",
        "group_name": "plan_first_review_v1",
        "job_id": "test-job-123",
        "ending_baseline": 1,
        "new_baseline": 2,
        "request_hash": TEST_REQUEST_HASH,
        "ending_snapshot_hash": TEST_SNAPSHOT_HASH,
        "ending_state_identity": job_state._semantic_ending_identity(
            json.loads(TEST_SNAPSHOT_BYTES)
        ),
        "canonical_paths": {
            "request": "Planning/test-project/baseline_02/request.md",
            "operation": "Planning/test-project/baseline_02/operation.json",
            "ending_snapshot": "Planning/test-project/baseline_02/ending_snapshot.json",
            "receipt": "Planning/test-project/baseline_02/receipt.json",
        },
    }
    digest = hashlib.sha256(
        json.dumps(
            {k: v for k, v in operation.items() if k != "manifest_hash"},
            sort_keys=True,
        ).encode()
    ).hexdigest()
    operation["manifest_hash"] = digest
    return operation


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
    (staging_dir / "request.md").write_bytes(TEST_REQUEST_BYTES)
    (staging_dir / "ending_snapshot.json").write_bytes(TEST_SNAPSHOT_BYTES)

    result = job_state.validate_immutable_operation(
        existing_op=base_operation,
        operation_id="op_abc123",
        request_id="req_xyz789",
        request_bytes=TEST_REQUEST_BYTES,
        incoming_request_hash=TEST_REQUEST_HASH,
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
    (final_dir / "request.md").write_bytes(TEST_REQUEST_BYTES)
    (final_dir / "ending_snapshot.json").write_bytes(TEST_SNAPSHOT_BYTES)

    result = job_state.validate_immutable_operation(
        existing_op=base_operation,
        operation_id="op_abc123",
        request_id="req_xyz789",
        request_bytes=TEST_REQUEST_BYTES,
        incoming_request_hash=TEST_REQUEST_HASH,
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
            "ending_snapshot": "Planning/test-project/baseline_02/ending_snapshot.json",
            "receipt": "Planning/test-project/baseline_02/receipt.json",
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
    (final_dir / "request.md").write_bytes(TEST_REQUEST_BYTES)
    (final_dir / "ending_snapshot.json").write_bytes(TEST_SNAPSHOT_BYTES)

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
        request_bytes=TEST_REQUEST_BYTES,
        incoming_request_hash=TEST_REQUEST_HASH,
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
        _use_in_memory_state=True,
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
        _use_in_memory_state=True,
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
        _use_in_memory_state=True,
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
            _use_in_memory_state=True,
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
            _use_in_memory_state=True,
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


# ---------------------------------------------------------------------------
# R8: Canonical path validation tests
# ---------------------------------------------------------------------------

def test_validate_operation_rejects_missing_canonical_key(base_state, tmp_path):
    """validate_immutable_operation rejects operation missing required canonical key."""
    project_root = tmp_path
    final_dir = project_root / "Planning/test-project/baseline_02"
    final_dir.mkdir(parents=True)

    # Operation missing ending_snapshot and receipt keys
    op = {
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
            # Missing ending_snapshot and receipt
        },
    }

    with pytest.raises(TransactionConflictError, match="Missing required canonical field"):
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


def test_validate_operation_rejects_non_string_canonical_value(base_state, tmp_path):
    """validate_immutable_operation rejects non-string canonical path value."""
    project_root = tmp_path
    final_dir = project_root / "Planning/test-project/baseline_02"
    final_dir.mkdir(parents=True)

    op = {
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
            "ending_snapshot": 123,  # Non-string
            "receipt": "Planning/test-project/baseline_02/receipt.json",
        },
    }

    with pytest.raises(TransactionConflictError, match="Canonical ending_snapshot is not a string"):
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


# ---------------------------------------------------------------------------
# R8: Timestamp validation tests
# ---------------------------------------------------------------------------

def test_complete_transaction_includes_timestamps_in_result(base_state, mock_save_job, mock_now_iso, tmp_path):
    """complete_baseline_transaction includes committed_at in result."""
    project_root = tmp_path
    planning_folder = "Planning/test-project"

    result = job_state.complete_baseline_transaction(
        _use_in_memory_state=True,
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

    # Result must have committed_at timestamp
    assert "committed_at" in result
    assert result["committed_at"] == "2026-11-19T00:00:00"


def test_complete_transaction_timestamps_match_in_result_and_envelope(base_state, mock_save_job, mock_now_iso, tmp_path):
    """complete_baseline_transaction uses same timestamp in result and envelope."""
    project_root = tmp_path
    planning_folder = "Planning/test-project"

    result = job_state.complete_baseline_transaction(
        _use_in_memory_state=True,
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

    # Get envelope from ledger
    envelope = base_state["baseline_commits"]["req_xyz789"]

    # Timestamps must match
    assert result["committed_at"] == envelope["committed_at"]


# ---------------------------------------------------------------------------
# R8: Receipt tests
# ---------------------------------------------------------------------------

def test_complete_transaction_writes_receipt(base_state, mock_save_job, mock_now_iso, tmp_path):
    """complete_baseline_transaction writes receipt.json after state commit."""
    project_root = tmp_path
    planning_folder = "Planning/test-project"

    job_state.complete_baseline_transaction(
        _use_in_memory_state=True,
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

    # Verify receipt was written
    final_dir = project_root / planning_folder / "baseline_02"
    receipt_path = final_dir / "receipt.json"
    assert receipt_path.exists()

    # Verify receipt content
    receipt = json.loads(receipt_path.read_text())
    assert receipt["request_id"] == "req_xyz789"
    assert receipt["operation_id"] == "op_abc123"
    assert receipt["baseline"] == 2
    assert receipt["committed_at"] == "2026-11-19T00:00:00"


def test_repair_derived_receipt_repairs_missing(base_state, mock_now_iso, tmp_path):
    """repair_derived_receipt creates missing receipt."""
    project_root = tmp_path
    planning_folder = "Planning/test-project"
    final_dir = project_root / planning_folder / "baseline_02"
    final_dir.mkdir(parents=True)
    receipt_path = final_dir / "receipt.json"

    operation = {
        "operation_id": "op_abc123",
        "request_id": "req_xyz789",
        "new_baseline": 2,
        "manifest_hash": "abc123",
    }
    commit_record = {
        "committed_at": "2026-11-19T00:00:00",
    }

    # Receipt doesn't exist
    assert not receipt_path.exists()

    # Repair should create it
    repaired = job_state.repair_derived_receipt(operation, commit_record, receipt_path)

    assert repaired is True
    assert receipt_path.exists()

    receipt = json.loads(receipt_path.read_text())
    assert receipt["request_id"] == "req_xyz789"


def test_repair_derived_receipt_repairs_truncated(base_state, mock_now_iso, tmp_path):
    """repair_derived_receipt replaces truncated/malformed receipt."""
    project_root = tmp_path
    planning_folder = "Planning/test-project"
    final_dir = project_root / planning_folder / "baseline_02"
    final_dir.mkdir(parents=True)
    receipt_path = final_dir / "receipt.json"

    # Write truncated receipt
    receipt_path.write_text('{"request_id": "req_xyz789", "truncated')

    operation = {
        "operation_id": "op_abc123",
        "request_id": "req_xyz789",
        "new_baseline": 2,
        "manifest_hash": "abc123",
    }
    commit_record = {
        "committed_at": "2026-11-19T00:00:00",
    }

    # Repair should replace it
    repaired = job_state.repair_derived_receipt(operation, commit_record, receipt_path)

    assert repaired is True

    receipt = json.loads(receipt_path.read_text())
    assert receipt["request_id"] == "req_xyz789"
    assert receipt["operation_id"] == "op_abc123"


def test_repair_derived_receipt_no_change_when_valid(base_state, mock_now_iso, tmp_path):
    """repair_derived_receipt returns False when receipt is already valid."""
    project_root = tmp_path
    planning_folder = "Planning/test-project"
    final_dir = project_root / planning_folder / "baseline_02"
    final_dir.mkdir(parents=True)
    receipt_path = final_dir / "receipt.json"

    operation = {
        "operation_id": "op_abc123",
        "request_id": "req_xyz789",
        "new_baseline": 2,
        "manifest_hash": "abc123",
    }
    commit_record = {
        "committed_at": "2026-11-19T00:00:00",
    }

    # Write valid receipt first
    expected_receipt = job_state._derive_receipt(operation, commit_record)
    receipt_path.write_text(json.dumps(expected_receipt))

    # Repair should not change it
    repaired = job_state.repair_derived_receipt(operation, commit_record, receipt_path)

    assert repaired is False


# ---------------------------------------------------------------------------
# R8: Snapshot tests
# ---------------------------------------------------------------------------

def test_complete_transaction_writes_snapshot(base_state, mock_save_job, mock_now_iso, tmp_path):
    """complete_baseline_transaction writes ending_snapshot.json."""
    project_root = tmp_path
    planning_folder = "Planning/test-project"

    job_state.complete_baseline_transaction(
        _use_in_memory_state=True,
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

    # Verify snapshot was written
    final_dir = project_root / planning_folder / "baseline_02"
    snapshot_path = final_dir / "ending_snapshot.json"
    assert snapshot_path.exists()

    # Verify snapshot content is a deep copy of the ENDING state (before the
    # transition), so the frozen snapshot still records baseline 1.
    snapshot = json.loads(snapshot_path.read_text())
    assert snapshot["job_id"] == "test-job-123"
    assert snapshot["requirements_baseline"] == 1  # Ending baseline, not new baseline


# ---------------------------------------------------------------------------
# Real-persistence convergence regressions (Phase B R3)
# ---------------------------------------------------------------------------

def test_resumed_staging_with_changed_bytes_conflicts(base_state, tmp_path):
    """A same-owner staging holding another request's bytes must not publish."""
    planning = tmp_path / "Planning/test-project"
    staging = planning / ".staging_op_conflict"
    staging.mkdir(parents=True)

    persisted_bytes = b"original request bytes"
    staging_op = {
        "operation_id": "op_conflict",
        "request_id": "req_conflict",
        "group_name": "plan_first_review_v1",
        "job_id": "test-job-123",
        "request_hash": hashlib.sha256(persisted_bytes).hexdigest(),
    }
    (staging / "request.md").write_bytes(persisted_bytes)
    (staging / "operation.json").write_text(json.dumps(staging_op), encoding="utf-8")

    with pytest.raises(TransactionConflictError, match="Staging request bytes differ"):
        job_state.execute_baseline_transaction(
            group_name="plan_first_review_v1",
            job_id="test-job-123",
            request_bytes=b"changed request bytes",
            request_id="req_conflict",
            project_root=tmp_path,
            _authoritative_state=base_state,
        )


def test_adoption_conflicts_on_changed_ending_state(base_state, tmp_path):
    """After publication/pre-save failure, a changed ending state must conflict."""
    state = copy.deepcopy(base_state)
    real_save = job_state.save_job

    def flaky_save(*args, **kwargs):
        raise RuntimeError("injected pre-save failure")

    with patch.object(job_state, "save_job", flaky_save):
        with pytest.raises(RuntimeError):
            job_state.execute_baseline_transaction(
                group_name="plan_first_review_v1",
                job_id="test-job-123",
                request_bytes=b"request body",
                request_id="req_adopt",
                project_root=tmp_path,
                _authoritative_state=state,
            )

    # Publication completed before the injected failure; the final exists.
    assert (tmp_path / "Planning/test-project/baseline_02").exists()

    changed = copy.deepcopy(base_state)
    changed["pending_intervention_for"] = "changed-after-publication"

    with patch.object(job_state, "save_job", lambda *a, **k: None):
        with pytest.raises(TransactionConflictError, match="Current ending state differs"):
            job_state.execute_baseline_transaction(
                group_name="plan_first_review_v1",
                job_id="test-job-123",
                request_bytes=b"request body",
                request_id="req_adopt",
                project_root=tmp_path,
                _authoritative_state=changed,
            )


def test_complete_transaction_rejects_changed_bytes_on_replay(
    base_state, mock_save_job, mock_now_iso, tmp_path
):
    """Retrying a committed request with changed bytes must conflict."""
    kwargs = dict(
        state=base_state,
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        request_id="req_fixed",
        operation_id="op_fixed",
        ending_baseline=1,
        new_baseline=2,
        planning_folder="Planning/test-project",
        project_root=tmp_path,
    )
    job_state.complete_baseline_transaction(
        _use_in_memory_state=True,
        request_bytes=b"first bytes",
        request_hash="ignored",
        commit_ledger=base_state["baseline_commits"],
        **kwargs,
    )
    with pytest.raises(TransactionConflictError, match="Incoming request.*hash"):
        job_state.complete_baseline_transaction(
            _use_in_memory_state=True,
            request_bytes=b"changed bytes",
            request_hash="ignored",
            commit_ledger=base_state["baseline_commits"],
            **kwargs,
        )


def test_complete_transaction_does_not_mutate_caller_on_save_failure(base_state, tmp_path):
    """A save failure must not mutate the caller's state dict."""
    original = copy.deepcopy(base_state)

    def boom(*args, **kwargs):
        raise RuntimeError("save failed")

    with patch.object(job_state, "save_job", boom):
        with pytest.raises(RuntimeError):
            job_state.complete_baseline_transaction(
                _use_in_memory_state=True,
                state=base_state,
                group_name="plan_first_review_v1",
                job_id="test-job-123",
                request_id="req_fail",
                operation_id="op_fail",
                request_bytes=b"bytes",
                request_hash="ignored",
                ending_baseline=1,
                new_baseline=2,
                planning_folder="Planning/test-project",
                project_root=tmp_path,
                commit_ledger=base_state["baseline_commits"],
            )

    assert base_state == original


def test_replay_rejects_missing_canonical_snapshot_with_consistent_manifest(
    base_state, tmp_path
):
    """Missing canonical ending_snapshot/receipt must reject even if digests agree."""
    planning = tmp_path / "Planning/test-project"
    final_dir = planning / "baseline_02"
    final_dir.mkdir(parents=True)

    req_bytes = b"request bytes"
    snapshot_bytes = b"{}"
    (final_dir / "request.md").write_bytes(req_bytes)
    (final_dir / "ending_snapshot.json").write_bytes(snapshot_bytes)
    (final_dir / "receipt.json").write_text("{}", encoding="utf-8")

    baseline_dir_rel = "Planning/test-project/baseline_02"
    op = {
        "operation_id": "op_x",
        "request_id": "req_x",
        "group_name": "plan_first_review_v1",
        "job_id": "test-job-123",
        "ending_baseline": 1,
        "new_baseline": 2,
        "request_hash": hashlib.sha256(req_bytes).hexdigest(),
        "ending_snapshot_hash": hashlib.sha256(snapshot_bytes).hexdigest(),
        "canonical_paths": {
            "request": f"{baseline_dir_rel}/request.md",
            "operation": f"{baseline_dir_rel}/operation.json",
            # Deliberately omit "ending_snapshot" and "receipt"
        },
    }
    op["manifest_hash"] = hashlib.sha256(
        json.dumps(op, sort_keys=True).encode()
    ).hexdigest()
    (final_dir / "operation.json").write_text(json.dumps(op), encoding="utf-8")

    commit = {
        "request_id": "req_x",
        "operation_id": "op_x",
        "manifest_hash": op["manifest_hash"],
        "operation": op,
        "result": {
            "status": "committed",
            "baseline": 2,
            "operation_id": "op_x",
            "request_id": "req_x",
            "committed_at": "2026-11-19T00:00:00",
        },
        "committed_at": "2026-11-19T00:00:00",
    }

    with pytest.raises(TransactionConflictError, match="Missing required canonical field"):
        job_state._handle_committed_replay(
            request_id="req_x",
            request_bytes=req_bytes,
            request_hash=op["request_hash"],
            existing_commit=commit,
            authoritative_state=base_state,
            group_name="plan_first_review_v1",
            job_id="test-job-123",
            project_root=tmp_path,
        )


# ---------------------------------------------------------------------------
# R4 residual regressions: shared validator, authority, reset, archive, errors
# ---------------------------------------------------------------------------

def _build_complete_staging(request_bytes, request_id, op_id, planning_folder):
    """Return (staging_dir, operation, snapshot) with complete immutable evidence."""
    staging = Path(planning_folder) / f".staging_{op_id}"
    staging.mkdir(parents=True, exist_ok=True)
    (staging / "request.md").write_bytes(request_bytes)
    snapshot = {"job_id": "test-job-123", "requirements_baseline": 1}
    (staging / "ending_snapshot.json").write_text(json.dumps(snapshot), encoding="utf-8")
    snapshot_hash = hashlib.sha256((staging / "ending_snapshot.json").read_bytes()).hexdigest()
    baseline_dir_rel = "Planning/test-project/baseline_02"
    operation = {
        "operation_id": op_id,
        "request_id": request_id,
        "group_name": "plan_first_review_v1",
        "job_id": "test-job-123",
        "ending_baseline": 1,
        "new_baseline": 2,
        "request_hash": hashlib.sha256(request_bytes).hexdigest(),
        "ending_snapshot_hash": snapshot_hash,
        "ending_state_identity": job_state._semantic_ending_identity(snapshot),
        "canonical_paths": {
            "request": f"{baseline_dir_rel}/request.md",
            "operation": f"{baseline_dir_rel}/operation.json",
            "ending_snapshot": f"{baseline_dir_rel}/ending_snapshot.json",
            "receipt": f"{baseline_dir_rel}/receipt.json",
        },
    }
    operation["manifest_hash"] = hashlib.sha256(
        json.dumps(operation, sort_keys=True).encode()
    ).hexdigest()
    (staging / "operation.json").write_text(json.dumps(operation), encoding="utf-8")
    return staging, operation, snapshot


def test_validate_rejects_changed_actual_bytes_with_agreeing_hash(base_state, base_operation, tmp_path):
    """Hashing the declared arg is insufficient: actual persisted bytes must match."""
    staging = tmp_path / "Planning/test-project/.staging_op_abc123"
    staging.mkdir(parents=True)
    (staging / "request.md").write_bytes(b"DIFFERENT actual bytes")
    (staging / "ending_snapshot.json").write_bytes(TEST_SNAPSHOT_BYTES)

    with pytest.raises(TransactionConflictError, match="Persisted request bytes"):
        job_state.validate_immutable_operation(
            existing_op=base_operation,
            operation_id="op_abc123",
            request_id="req_xyz789",
            request_bytes=TEST_REQUEST_BYTES,
            incoming_request_hash=TEST_REQUEST_HASH,  # agrees with stored digest
            ending_baseline=1,
            actual_dir=staging,
            state=base_state,
            group_name="plan_first_review_v1",
            job_id="test-job-123",
            project_root=tmp_path,
            phase="staging",
        )


def test_validate_rejects_modified_on_disk_snapshot(base_state, base_operation, tmp_path):
    """A modified on-disk snapshot must be rejected even with declared digests."""
    final_dir = tmp_path / "Planning/test-project/baseline_02"
    final_dir.mkdir(parents=True)
    (final_dir / "request.md").write_bytes(TEST_REQUEST_BYTES)
    (final_dir / "ending_snapshot.json").write_bytes(b'{"tampered": true}')

    with pytest.raises(TransactionConflictError, match="Persisted snapshot hash"):
        job_state.validate_immutable_operation(
            existing_op=base_operation,
            operation_id="op_abc123",
            request_id="req_xyz789",
            request_bytes=TEST_REQUEST_BYTES,
            incoming_request_hash=TEST_REQUEST_HASH,
            ending_baseline=1,
            actual_dir=final_dir,
            state=base_state,
            group_name="plan_first_review_v1",
            job_id="test-job-123",
            project_root=tmp_path,
            phase="final",
        )


def test_resume_rejects_corrupt_manifest(base_state, tmp_path):
    """Resume must reject corrupt immutable evidence, not rewrite it."""
    staging, operation, _ = _build_complete_staging(
        TEST_REQUEST_BYTES, "req_resume", "op_resume", tmp_path / "Planning/test-project"
    )
    operation["manifest_hash"] = "0" * 64
    (staging / "operation.json").write_text(json.dumps(operation), encoding="utf-8")

    with pytest.raises(TransactionConflictError, match="Computed manifest != stored manifest_hash"):
        job_state.execute_baseline_transaction(
            group_name="plan_first_review_v1",
            job_id="test-job-123",
            request_bytes=TEST_REQUEST_BYTES,
            request_id="req_resume",
            project_root=tmp_path,
            _authoritative_state=base_state,
        )


def test_adoption_rejects_changed_canonical_location(base_state, tmp_path):
    """Adoption must reject canonical authority that replay would reject."""
    state = copy.deepcopy(base_state)

    def flaky_save(*args, **kwargs):
        raise RuntimeError("injected pre-save failure")

    with patch.object(job_state, "save_job", flaky_save):
        with pytest.raises(RuntimeError):
            job_state.execute_baseline_transaction(
                group_name="plan_first_review_v1",
                job_id="test-job-123",
                request_bytes=b"canonical request",
                request_id="req_canon",
                project_root=tmp_path,
                _authoritative_state=state,
            )

    final_dir = tmp_path / "Planning/test-project/baseline_02"
    op = json.loads((final_dir / "operation.json").read_text())
    op["canonical_paths"]["request"] = "Planning/elsewhere/request.md"
    op["manifest_hash"] = hashlib.sha256(
        json.dumps({k: v for k, v in op.items() if k != "manifest_hash"}, sort_keys=True).encode()
    ).hexdigest()
    (final_dir / "operation.json").write_text(json.dumps(op), encoding="utf-8")

    with patch.object(job_state, "save_job", lambda *a, **k: None):
        with pytest.raises(TransactionConflictError, match="Canonical request path mismatch"):
            job_state.execute_baseline_transaction(
                group_name="plan_first_review_v1",
                job_id="test-job-123",
                request_bytes=b"canonical request",
                request_id="req_canon",
                project_root=tmp_path,
                _authoritative_state=state,
            )


def test_production_compatibility_rejects_stale_caller(base_state, tmp_path, monkeypatch):
    """Production compatibility reloads disk; a stale caller cannot roll it back."""
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "plan_first_review_v1" / "test-job-123"
    job_dir.mkdir(parents=True)
    disk_state = {
        "job_id": "test-job-123",
        "template_group": "plan_first_review_v1",
        "requirements_baseline": 5,
        "artifacts": {"PLANNING_FOLDER": "Planning/test-project"},
        "baseline_commits": {},
    }
    (job_dir / "job.json").write_text(json.dumps(disk_state), encoding="utf-8")
    before = (job_dir / "job.json").read_bytes()

    monkeypatch.setattr(job_state, "JOBS_ROOT", jobs_root)

    stale_caller_state = copy.deepcopy(base_state)  # requirements_baseline == 1

    with pytest.raises(TransactionConflictError, match="stale"):
        job_state.complete_baseline_transaction(
            state=stale_caller_state,
            group_name="plan_first_review_v1",
            job_id="test-job-123",
            request_id="req_stale",
            operation_id="op_stale",
            request_bytes=b"bytes",
            request_hash="ignored",
            ending_baseline=1,
            new_baseline=2,
            planning_folder="Planning/test-project",
            project_root=tmp_path,
            commit_ledger={},
        )

    assert (job_dir / "job.json").read_bytes() == before
    assert json.loads(before)["requirements_baseline"] == 5


def test_apply_baseline_reset_clears_usage_without_losing_history():
    """The reset matrix clears usage/coder/revision state but retains history."""
    state = {
        "completed_steps": ["prepare_request", "generate_plan"],
        "step_usage": {"generate_plan": {"total_tokens": 10}},
        "usage_summary": {"total_tokens": 10},
        "step_coders": {"generate_plan": "qwen"},
        "revision_completions": {"b1_r1": {"attempt_id": "att_1"}},
        "change_history": [{"baseline": 1, "reason": "prior"}],
        "baseline_commits": {"req_old": {"request_id": "req_old"}},
    }
    job_state._apply_baseline_reset(state)

    assert state["step_usage"] == {}
    assert state["step_coders"] == {}
    assert state["revision_completions"] == {}
    assert state["usage_summary"] == job_state.default_usage_summary()
    assert state["change_history"] == [{"baseline": 1, "reason": "prior"}]
    assert state["baseline_commits"] == {"req_old": {"request_id": "req_old"}}


def test_execute_failure_exposes_generated_identity(base_state, tmp_path):
    """Auto-generated identity and phase are exposed on failure."""
    state = copy.deepcopy(base_state)
    state["job_status"] = "STOPPED_ARCHIVED"
    state["status"] = "STOPPED_ARCHIVED"

    with pytest.raises(TransactionConflictError) as excinfo:
        job_state.execute_baseline_transaction(
            group_name="plan_first_review_v1",
            job_id="test-job-123",
            request_bytes=b"bytes",
            project_root=tmp_path,
            _authoritative_state=state,
        )

    err = excinfo.value
    assert getattr(err, "request_id", None)
    assert err.request_id.startswith("req_")
    assert getattr(err, "phase", None) == "reloaded"


def test_archived_historical_replay_returns_result(base_state, tmp_path):
    """An identical historical retry on an archived job returns the saved result."""
    request_bytes = b"archived request"
    request_id = "req_archived"
    op_id = "op_archived"
    base = "Planning/test-project/baseline_02"
    final_dir = tmp_path / base
    final_dir.mkdir(parents=True)
    (final_dir / "request.md").write_bytes(request_bytes)
    snapshot = {"job_id": "test-job-123"}
    (final_dir / "ending_snapshot.json").write_text(json.dumps(snapshot), encoding="utf-8")
    snapshot_hash = hashlib.sha256((final_dir / "ending_snapshot.json").read_bytes()).hexdigest()
    operation = {
        "operation_id": op_id,
        "request_id": request_id,
        "group_name": "plan_first_review_v1",
        "job_id": "test-job-123",
        "ending_baseline": 1,
        "new_baseline": 2,
        "request_hash": hashlib.sha256(request_bytes).hexdigest(),
        "ending_snapshot_hash": snapshot_hash,
        "ending_state_identity": job_state._semantic_ending_identity(snapshot),
        "canonical_paths": {
            "request": f"{base}/request.md",
            "operation": f"{base}/operation.json",
            "ending_snapshot": f"{base}/ending_snapshot.json",
            "receipt": f"{base}/receipt.json",
        },
    }
    operation["manifest_hash"] = hashlib.sha256(
        json.dumps(operation, sort_keys=True).encode()
    ).hexdigest()
    (final_dir / "operation.json").write_text(json.dumps(operation), encoding="utf-8")
    result = {
        "status": "committed",
        "baseline": 2,
        "operation_id": op_id,
        "request_id": request_id,
        "committed_at": "2026-11-19T00:00:00",
    }
    commit = {
        "request_id": request_id,
        "operation_id": op_id,
        "manifest_hash": operation["manifest_hash"],
        "operation": operation,
        "result": result,
        "committed_at": "2026-11-19T00:00:00",
    }

    state = copy.deepcopy(base_state)
    state["job_status"] = "STOPPED_ARCHIVED"
    state["status"] = "STOPPED_ARCHIVED"
    state["baseline_commits"] = {request_id: commit}

    returned = job_state.execute_baseline_transaction(
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        request_bytes=request_bytes,
        request_id=request_id,
        project_root=tmp_path,
        _authoritative_state=state,
    )
    assert returned == result


# ---------------------------------------------------------------------------
# R5 residual regressions: replay schema, ledger membership, discovery order
# ---------------------------------------------------------------------------

def _build_published_final_and_commit(
    tmp_path, request_bytes, request_id, op_id, committed_at="2026-11-19T00:00:00"
):
    """Create valid published final evidence plus a matching ledger envelope."""
    base = "Planning/test-project/baseline_02"
    final_dir = tmp_path / base
    final_dir.mkdir(parents=True)
    (final_dir / "request.md").write_bytes(request_bytes)
    snapshot = {"job_id": "test-job-123"}
    (final_dir / "ending_snapshot.json").write_text(json.dumps(snapshot), encoding="utf-8")
    snapshot_hash = hashlib.sha256((final_dir / "ending_snapshot.json").read_bytes()).hexdigest()
    operation = {
        "operation_id": op_id,
        "request_id": request_id,
        "group_name": "plan_first_review_v1",
        "job_id": "test-job-123",
        "ending_baseline": 1,
        "new_baseline": 2,
        "request_hash": hashlib.sha256(request_bytes).hexdigest(),
        "ending_snapshot_hash": snapshot_hash,
        "ending_state_identity": job_state._semantic_ending_identity(snapshot),
        "canonical_paths": {
            "request": f"{base}/request.md",
            "operation": f"{base}/operation.json",
            "ending_snapshot": f"{base}/ending_snapshot.json",
            "receipt": f"{base}/receipt.json",
        },
    }
    operation["manifest_hash"] = hashlib.sha256(
        json.dumps(operation, sort_keys=True).encode()
    ).hexdigest()
    (final_dir / "operation.json").write_text(json.dumps(operation), encoding="utf-8")
    result = {
        "status": "committed",
        "baseline": 2,
        "operation_id": op_id,
        "request_id": request_id,
        "committed_at": committed_at,
    }
    commit = {
        "request_id": request_id,
        "operation_id": op_id,
        "manifest_hash": operation["manifest_hash"],
        "operation": operation,
        "result": result,
        "committed_at": committed_at,
    }
    return final_dir, operation, commit


def _replay(state, request_bytes, request_id, commit, tmp_path):
    return job_state._handle_committed_replay(
        request_id=request_id,
        request_bytes=request_bytes,
        request_hash=hashlib.sha256(request_bytes).hexdigest(),
        existing_commit=commit,
        authoritative_state=state,
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        project_root=tmp_path,
    )


def test_replay_rejects_missing_ending_identity(base_state, tmp_path):
    """Missing recorded semantic identity must reject even with agreeing digests."""
    req = b"replay bytes"
    final_dir, op, commit = _build_published_final_and_commit(
        tmp_path, req, "req_r", "op_r"
    )
    op.pop("ending_state_identity")
    op["manifest_hash"] = hashlib.sha256(
        json.dumps({k: v for k, v in op.items() if k != "manifest_hash"}, sort_keys=True).encode()
    ).hexdigest()
    commit["manifest_hash"] = op["manifest_hash"]
    (final_dir / "operation.json").write_text(json.dumps(op), encoding="utf-8")

    with pytest.raises(TransactionConflictError, match="Missing ending_state_identity"):
        _replay(base_state, req, "req_r", commit, tmp_path)


def test_replay_rejects_unbound_envelope(base_state, tmp_path):
    """Envelope operation_id/manifest must bind to the embedded operation."""
    req = b"replay bytes"
    _, op, commit = _build_published_final_and_commit(tmp_path, req, "req_r", "op_r")
    commit["operation_id"] = "op_other"

    with pytest.raises(TransactionConflictError, match="Envelope operation_id"):
        _replay(base_state, req, "req_r", commit, tmp_path)


def test_replay_rejects_invalid_equal_timestamps(base_state, tmp_path):
    """Equal but non-ISO timestamps must reject on schema, not just equality."""
    req = b"replay bytes"
    _, op, commit = _build_published_final_and_commit(tmp_path, req, "req_r", "op_r")
    commit["committed_at"] = "not-a-timestamp"
    commit["result"]["committed_at"] = "not-a-timestamp"

    with pytest.raises(TransactionConflictError, match="Invalid envelope committed_at"):
        _replay(base_state, req, "req_r", commit, tmp_path)


def test_malformed_ledger_entry_rejects_without_new_operation(base_state, tmp_path):
    """A present empty ledger value is corruption, not an absent request."""
    state = copy.deepcopy(base_state)
    state["baseline_commits"] = {"req_bad": {}}
    before = copy.deepcopy(state)

    with pytest.raises(TransactionConflictError, match="Malformed commit ledger entry"):
        job_state.execute_baseline_transaction(
            group_name="plan_first_review_v1",
            job_id="test-job-123",
            request_bytes=b"bytes",
            request_id="req_bad",
            project_root=tmp_path,
            _authoritative_state=state,
        )

    assert state == before
    assert not (tmp_path / "Planning/test-project/baseline_02").exists()
    assert not list((tmp_path / "Planning/test-project").glob(".staging_*"))


def test_final_adoption_rejects_conflicting_staging(base_state, tmp_path):
    """Simultaneous final + unidentifiable staging is ambiguous before mutation."""
    state = copy.deepcopy(base_state)

    def flaky_save(*args, **kwargs):
        raise RuntimeError("injected pre-save failure")

    with patch.object(job_state, "save_job", flaky_save):
        with pytest.raises(RuntimeError):
            job_state.execute_baseline_transaction(
                group_name="plan_first_review_v1",
                job_id="test-job-123",
                request_bytes=b"published request",
                request_id="req_amb",
                project_root=tmp_path,
                _authoritative_state=state,
            )

    planning = tmp_path / "Planning/test-project"
    staging = planning / ".staging_conflicting"
    staging.mkdir()
    (staging / "request.md").write_bytes(b"other")
    (staging / "operation.json").write_text(
        json.dumps(
            {
                "operation_id": "op_conflicting",
                "request_id": "req_other",
                "group_name": "plan_first_review_v1",
                "job_id": "test-job-123",
                "request_hash": hashlib.sha256(b"other").hexdigest(),
            }
        ),
        encoding="utf-8",
    )
    before = copy.deepcopy(state)

    with patch.object(job_state, "save_job", lambda *a, **k: None):
        with pytest.raises(TransactionConflictError, match="Ambiguous evidence"):
            job_state.execute_baseline_transaction(
                group_name="plan_first_review_v1",
                job_id="test-job-123",
                request_bytes=b"published request",
                request_id="req_amb",
                project_root=tmp_path,
                _authoritative_state=state,
            )

    assert state == before
    assert (planning / ".staging_conflicting").exists()


# ---------------------------------------------------------------------------
# R6 residual regressions: types, receipt encoding, raw snapshot, lock errors
# ---------------------------------------------------------------------------

def test_replay_rejects_coherent_integer_operation_id(base_state, tmp_path):
    """A coherent integer operation_id must still reject on schema."""
    req = b"replay bytes"
    final_dir, op, commit = _build_published_final_and_commit(
        tmp_path, req, "req_r", "op_r"
    )
    op["operation_id"] = 123
    commit["operation_id"] = 123
    commit["result"]["operation_id"] = 123
    op["manifest_hash"] = hashlib.sha256(
        json.dumps({k: v for k, v in op.items() if k != "manifest_hash"}, sort_keys=True).encode()
    ).hexdigest()
    commit["manifest_hash"] = op["manifest_hash"]
    (final_dir / "operation.json").write_text(json.dumps(op), encoding="utf-8")

    with pytest.raises(TransactionConflictError, match="nonempty string"):
        _replay(base_state, req, "req_r", commit, tmp_path)


def test_replay_rejects_float_result_baseline(base_state, tmp_path):
    """result.baseline must be an exact integer, not a float equal by value."""
    req = b"replay bytes"
    _, op, commit = _build_published_final_and_commit(tmp_path, req, "req_r", "op_r")
    commit["result"]["baseline"] = 2.0

    with pytest.raises(TransactionConflictError, match="exact integer"):
        _replay(base_state, req, "req_r", commit, tmp_path)


def test_replay_repairs_invalid_encoding_receipt(base_state, tmp_path):
    """Invalid-encoding derived receipt must be replaced after verification."""
    req = b"replay bytes"
    final_dir, op, commit = _build_published_final_and_commit(
        tmp_path, req, "req_r", "op_r", committed_at="2026-11-19T00:00:00"
    )
    (final_dir / "receipt.json").write_bytes(b"\xff\xfe\xff")

    returned = _replay(base_state, req, "req_r", commit, tmp_path)
    assert returned == commit["result"]

    repaired = json.loads((final_dir / "receipt.json").read_text(encoding="utf-8"))
    assert repaired == job_state._derive_receipt(op, commit)


def test_frozen_snapshot_excludes_default_baseline_commits(
    base_state, mock_save_job, mock_now_iso, tmp_path
):
    """Raw job without baseline_commits must not gain it in the frozen snapshot."""
    state = copy.deepcopy(base_state)
    state.pop("baseline_commits", None)
    assert "baseline_commits" not in state

    job_state.execute_baseline_transaction(
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        request_bytes=b"raw request",
        request_id="req_raw",
        project_root=tmp_path,
        _authoritative_state=state,
    )

    snapshot_path = tmp_path / "Planning/test-project/baseline_02/ending_snapshot.json"
    snapshot = json.loads(snapshot_path.read_text())
    assert "baseline_commits" not in snapshot

    # The committed working state still initializes the ledger.
    committed = mock_save_job[-1][2]
    assert "baseline_commits" in committed


def test_lock_acquisition_failure_exposes_identity(base_state, tmp_path):
    """Lock-acquisition failure exposes retry id/phase and releases nothing."""
    released = []

    def boom(_path):
        raise OSError("lock unavailable")

    with patch.object(job_state, "_acquire_lock", boom), patch.object(
        job_state, "_release_lock", lambda p: released.append(p)
    ):
        with pytest.raises(OSError) as excinfo:
            job_state.execute_baseline_transaction(
                group_name="plan_first_review_v1",
                job_id="test-job-123",
                request_bytes=b"bytes",
                project_root=tmp_path,
                _authoritative_state=base_state,
            )

    err = excinfo.value
    assert getattr(err, "request_id", None)
    assert err.request_id.startswith("req_")
    assert getattr(err, "phase", None) == "init"
    assert released == []
