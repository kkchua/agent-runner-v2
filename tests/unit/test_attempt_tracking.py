"""Tests for attempt tracking and recovery (plan_first_review_v1).

Covers:
- _create_recovery_snapshot_for_preparation (actual field validation, no synthesis)
- prepare_plan_attempt (input/output rules, canonical paths, atomic save)
- _validate_owned_recovery_context (identity match, same contract)
- One-field-at-a-time invalid cases (active, loop_step, refine_step, target_artifact)

This is the core v33 validation: actual loop fields are validated before snapshot
construction, and validated actual values are copied into the snapshot (no synthesis).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

import agent_runner_v2.job_state as job_state
from agent_runner_v2.constants import ARTIFACT_PATH_CODEX_REVIEW, ARTIFACT_PATH_QWEN_PLAN


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
def valid_refinement_state():
    """Valid state for refinement with all actual loop fields set correctly."""
    planning_folder = "Planning/test-project"
    baseline = 1
    current_revision = 2
    canonical_review = ARTIFACT_PATH_CODEX_REVIEW(planning_folder, current_revision, baseline)

    return {
        "job_id": "test-job-123",
        "template_group": "plan_first_review_v1",
        "requirements_baseline": baseline,
        "plan_revision": current_revision,
        "artifacts": {
            "PLANNING_FOLDER": planning_folder,
        },
        "attempt_records": {},
        "loop_context": {
            "active": True,
            "loop_step": "codex_review",
            "refine_step": "refine_plan",
            "loop_target_artifact": "QWEN_PLAN_FILE",
            "loop_source_review": canonical_review,
            "loop_iteration": 1,
            "pre_refine_checksum": "abc123def456",
        },
    }


@pytest.fixture
def valid_group_cfg():
    """Valid group config with codex_review.on_reject_refine."""
    return {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                },
            },
        },
    }


@pytest.fixture
def valid_generation_state():
    """Valid state for generation (first plan)."""
    return {
        "job_id": "test-job-123",
        "template_group": "plan_first_review_v1",
        "requirements_baseline": 1,
        "plan_revision": 1,
        "artifacts": {
            "PLANNING_FOLDER": "Planning/test-project",
        },
        "attempt_records": {},
        "loop_context": {},
    }


# ---------------------------------------------------------------------------
# _create_recovery_snapshot_for_preparation tests
# ---------------------------------------------------------------------------

def test_valid_refinement_snapshot_preserves_actual_values(valid_refinement_state, valid_group_cfg):
    """Valid refinement snapshot preserves validated actual values."""
    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    snapshot = job_state._create_recovery_snapshot_for_preparation(
        attempt_record=attempt_record,
        state=valid_refinement_state,
        group_cfg=valid_group_cfg,
        group_name="plan_first_review_v1",
        planning_folder="Planning/test-project",
    )

    # Verify identity
    assert snapshot["job_id"] == "test-job-123"
    assert snapshot["group_name"] == "plan_first_review_v1"
    assert snapshot["baseline"] == 1
    assert snapshot["step"] == "refine_plan"
    assert snapshot["input_revision"] == 2
    assert snapshot["target_revision"] == 3

    # Verify loop context — all values are from actual state (validated, not synthesized)
    assert snapshot["active"] is True
    assert snapshot["loop_step"] == "codex_review"
    assert snapshot["refine_step"] == "refine_plan"
    assert snapshot["loop_target_artifact"] == "QWEN_PLAN_FILE"
    assert snapshot["loop_source_review"] == ARTIFACT_PATH_CODEX_REVIEW("Planning/test-project", 2, 1)
    assert snapshot["loop_iteration"] == 1
    assert snapshot["pre_refine_checksum"] == "abc123def456"
    assert snapshot["planning_folder"] == "Planning/test-project"


def test_valid_generation_snapshot(valid_generation_state, valid_group_cfg):
    """Valid generation snapshot has minimal inactive context."""
    attempt_record = {
        "step": "generate_plan",
        "baseline": 1,
        "input_revision": None,
        "target_revision": 1,
    }

    snapshot = job_state._create_recovery_snapshot_for_preparation(
        attempt_record=attempt_record,
        state=valid_generation_state,
        group_cfg=valid_group_cfg,
        group_name="plan_first_review_v1",
        planning_folder="Planning/test-project",
    )

    assert snapshot["active"] is False
    assert snapshot["step"] == "generate_plan"
    assert snapshot["input_revision"] is None
    assert snapshot["target_revision"] == 1


# ---------------------------------------------------------------------------
# One-field-at-a-time invalid cases (v33 core validation)
# ---------------------------------------------------------------------------

def test_active_false_rejected(valid_refinement_state, valid_group_cfg):
    """Change only active to False: preparation fails before save/coder invocation."""
    valid_refinement_state["loop_context"]["active"] = False

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    with pytest.raises(ValueError, match="Actual loop_context.active is not exactly True"):
        job_state._create_recovery_snapshot_for_preparation(
            attempt_record=attempt_record,
            state=valid_refinement_state,
            group_cfg=valid_group_cfg,
            group_name="plan_first_review_v1",
            planning_folder="Planning/test-project",
        )


def test_active_none_rejected(valid_refinement_state, valid_group_cfg):
    """Change only active to None: preparation fails."""
    valid_refinement_state["loop_context"]["active"] = None

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    with pytest.raises(ValueError, match="Actual loop_context.active is not exactly True"):
        job_state._create_recovery_snapshot_for_preparation(
            attempt_record=attempt_record,
            state=valid_refinement_state,
            group_cfg=valid_group_cfg,
            group_name="plan_first_review_v1",
            planning_folder="Planning/test-project",
        )


def test_active_non_bool_rejected(valid_refinement_state, valid_group_cfg):
    """Change only active to truthy non-bool: preparation fails."""
    valid_refinement_state["loop_context"]["active"] = 1  # Truthy but not bool

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    with pytest.raises(ValueError, match="Actual loop_context.active is not exactly True"):
        job_state._create_recovery_snapshot_for_preparation(
            attempt_record=attempt_record,
            state=valid_refinement_state,
            group_cfg=valid_group_cfg,
            group_name="plan_first_review_v1",
            planning_folder="Planning/test-project",
        )


def test_loop_step_wrong_rejected(valid_refinement_state, valid_group_cfg):
    """Change only loop_step to wrong value: preparation fails."""
    valid_refinement_state["loop_context"]["loop_step"] = "generate_plan"

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    with pytest.raises(ValueError, match="Actual loop_step.*!= codex_review"):
        job_state._create_recovery_snapshot_for_preparation(
            attempt_record=attempt_record,
            state=valid_refinement_state,
            group_cfg=valid_group_cfg,
            group_name="plan_first_review_v1",
            planning_folder="Planning/test-project",
        )


def test_loop_step_missing_rejected(valid_refinement_state, valid_group_cfg):
    """Change only loop_step to missing: preparation fails."""
    del valid_refinement_state["loop_context"]["loop_step"]

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    with pytest.raises(ValueError, match="Actual loop_step.*!= codex_review"):
        job_state._create_recovery_snapshot_for_preparation(
            attempt_record=attempt_record,
            state=valid_refinement_state,
            group_cfg=valid_group_cfg,
            group_name="plan_first_review_v1",
            planning_folder="Planning/test-project",
        )


def test_refine_step_wrong_rejected(valid_refinement_state, valid_group_cfg):
    """Change only refine_step to wrong value: preparation fails."""
    valid_refinement_state["loop_context"]["refine_step"] = "generate_plan"

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    with pytest.raises(ValueError, match="Actual refine_step.*!= attempt step"):
        job_state._create_recovery_snapshot_for_preparation(
            attempt_record=attempt_record,
            state=valid_refinement_state,
            group_cfg=valid_group_cfg,
            group_name="plan_first_review_v1",
            planning_folder="Planning/test-project",
        )


def test_refine_step_missing_rejected(valid_refinement_state, valid_group_cfg):
    """Change only refine_step to missing: preparation fails."""
    del valid_refinement_state["loop_context"]["refine_step"]

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    with pytest.raises(ValueError, match="Actual refine_step.*!= attempt step"):
        job_state._create_recovery_snapshot_for_preparation(
            attempt_record=attempt_record,
            state=valid_refinement_state,
            group_cfg=valid_group_cfg,
            group_name="plan_first_review_v1",
            planning_folder="Planning/test-project",
        )


def test_target_artifact_wrong_rejected(valid_refinement_state, valid_group_cfg):
    """Change only loop_target_artifact to wrong value: preparation fails."""
    valid_refinement_state["loop_context"]["loop_target_artifact"] = "WRONG_ARTIFACT"

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    with pytest.raises(ValueError, match="Actual loop_target_artifact.*!= configured"):
        job_state._create_recovery_snapshot_for_preparation(
            attempt_record=attempt_record,
            state=valid_refinement_state,
            group_cfg=valid_group_cfg,
            group_name="plan_first_review_v1",
            planning_folder="Planning/test-project",
        )


def test_target_artifact_missing_rejected(valid_refinement_state, valid_group_cfg):
    """Change only loop_target_artifact to missing: preparation fails."""
    del valid_refinement_state["loop_context"]["loop_target_artifact"]

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    with pytest.raises(ValueError, match="Actual loop_target_artifact.*!= configured"):
        job_state._create_recovery_snapshot_for_preparation(
            attempt_record=attempt_record,
            state=valid_refinement_state,
            group_cfg=valid_group_cfg,
            group_name="plan_first_review_v1",
            planning_folder="Planning/test-project",
        )


# ---------------------------------------------------------------------------
# Source/checksum/iteration validation (v32 checks retained in v33)
# ---------------------------------------------------------------------------

def test_source_path_wrong_rejected(valid_refinement_state, valid_group_cfg):
    """Wrong loop_source_review is rejected."""
    valid_refinement_state["loop_context"]["loop_source_review"] = "Planning/other-project/baseline_01/Codex_Review_v02.md"

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    with pytest.raises(ValueError, match="Actual loop_source_review.*!= canonical"):
        job_state._create_recovery_snapshot_for_preparation(
            attempt_record=attempt_record,
            state=valid_refinement_state,
            group_cfg=valid_group_cfg,
            group_name="plan_first_review_v1",
            planning_folder="Planning/test-project",
        )


def test_bool_iteration_rejected(valid_refinement_state, valid_group_cfg):
    """Bool iteration is rejected (not coerced)."""
    valid_refinement_state["loop_context"]["loop_iteration"] = True

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    with pytest.raises(ValueError, match="loop_iteration is not int"):
        job_state._create_recovery_snapshot_for_preparation(
            attempt_record=attempt_record,
            state=valid_refinement_state,
            group_cfg=valid_group_cfg,
            group_name="plan_first_review_v1",
            planning_folder="Planning/test-project",
        )


def test_negative_iteration_rejected(valid_refinement_state, valid_group_cfg):
    """Negative iteration is rejected."""
    valid_refinement_state["loop_context"]["loop_iteration"] = -1

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    with pytest.raises(ValueError, match="loop_iteration is negative"):
        job_state._create_recovery_snapshot_for_preparation(
            attempt_record=attempt_record,
            state=valid_refinement_state,
            group_cfg=valid_group_cfg,
            group_name="plan_first_review_v1",
            planning_folder="Planning/test-project",
        )


def test_missing_checksum_rejected(valid_refinement_state, valid_group_cfg):
    """Missing pre_refine_checksum is rejected."""
    del valid_refinement_state["loop_context"]["pre_refine_checksum"]

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    with pytest.raises(ValueError, match="Missing or invalid pre_refine_checksum"):
        job_state._create_recovery_snapshot_for_preparation(
            attempt_record=attempt_record,
            state=valid_refinement_state,
            group_cfg=valid_group_cfg,
            group_name="plan_first_review_v1",
            planning_folder="Planning/test-project",
        )


# ---------------------------------------------------------------------------
# prepare_plan_attempt tests
# ---------------------------------------------------------------------------

def test_prepare_attempt_refinement(valid_refinement_state, valid_group_cfg, mock_save_job, mock_now_iso):
    """prepare_plan_attempt creates attempt record for refinement."""
    attempt = job_state.prepare_plan_attempt(
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        state=valid_refinement_state,
        step="refine_plan",
        step_cfg={},
        group_cfg=valid_group_cfg,
        prepared_context={},
        project_root=Path("/tmp"),
    )

    # Verify attempt record structure
    assert attempt["attempt_id"].startswith("att_")
    assert attempt["workflow"] == "plan_first_review_v1"
    assert attempt["job_id"] == "test-job-123"
    assert attempt["baseline"] == 1
    assert attempt["step"] == "refine_plan"
    assert attempt["input_revision"] == 2  # current_revision
    assert attempt["target_revision"] == 3  # current_revision + 1
    assert attempt["status"] == "prepared"
    assert attempt["recovered_context"] is not None

    # Verify attempt was saved to state
    assert attempt["attempt_id"] in valid_refinement_state["attempt_records"]
    assert valid_refinement_state["loop_context"]["active_attempt_id"] == attempt["attempt_id"]


def test_prepare_attempt_generation(valid_generation_state, valid_group_cfg, mock_save_job, mock_now_iso):
    """prepare_plan_attempt creates attempt record for generation."""
    attempt = job_state.prepare_plan_attempt(
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        state=valid_generation_state,
        step="generate_plan",
        step_cfg={},
        group_cfg=valid_group_cfg,
        prepared_context={},
        project_root=Path("/tmp"),
    )

    assert attempt["input_revision"] is None
    assert attempt["target_revision"] == 1


def test_prepare_attempt_invalid_context_rejected(valid_refinement_state, valid_group_cfg, mock_save_job, mock_now_iso):
    """prepare_plan_attempt rejects invalid context before saving."""
    # Invalidate the context
    valid_refinement_state["loop_context"]["active"] = False

    with pytest.raises(ValueError, match="Actual loop_context.active is not exactly True"):
        job_state.prepare_plan_attempt(
            group_name="plan_first_review_v1",
            job_id="test-job-123",
            state=valid_refinement_state,
            step="refine_plan",
            step_cfg={},
            group_cfg=valid_group_cfg,
            prepared_context={},
            project_root=Path("/tmp"),
        )

    # Verify no attempt was saved
    assert len(valid_refinement_state["attempt_records"]) == 0


# ---------------------------------------------------------------------------
# _validate_owned_recovery_context tests (from workflow_router)
# ---------------------------------------------------------------------------

def test_validate_recovery_context_valid(valid_refinement_state, valid_group_cfg):
    """_validate_owned_recovery_context returns context for valid recovery."""
    from agent_runner_v2.v2.workflow_router import _validate_owned_recovery_context

    # First create a valid snapshot
    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
    }

    snapshot = job_state._create_recovery_snapshot_for_preparation(
        attempt_record=attempt_record,
        state=valid_refinement_state,
        group_cfg=valid_group_cfg,
        group_name="plan_first_review_v1",
        planning_folder="Planning/test-project",
    )

    # Now create an attempt record with that snapshot as recovered_context
    attempt_record_with_recovery = {
        **attempt_record,
        "recovered_context": snapshot,
    }

    # Validate it
    result = _validate_owned_recovery_context(
        attempt_record=attempt_record_with_recovery,
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        baseline=1,
        step="refine_plan",
        input_revision=2,
        target_revision=3,
        group_cfg=valid_group_cfg,
        planning_folder="Planning/test-project",
    )

    assert result is not None
    assert result["active"] is True
    assert result["loop_step"] == "codex_review"


def test_validate_recovery_context_rejects_invalid():
    """_validate_owned_recovery_context returns None for invalid context."""
    from agent_runner_v2.v2.workflow_router import _validate_owned_recovery_context

    attempt_record = {
        "step": "refine_plan",
        "baseline": 1,
        "input_revision": 2,
        "target_revision": 3,
        "recovered_context": {
            "job_id": "test-job-123",
            "group_name": "plan_first_review_v1",
            "baseline": 1,
            "step": "refine_plan",
            "input_revision": 2,
            "target_revision": 3,
            "active": False,  # Invalid for refinement
            "loop_step": "codex_review",
            "refine_step": "refine_plan",
            "loop_target_artifact": "QWEN_PLAN_FILE",
            "loop_source_review": "Planning/test-project/baseline_01/Codex_Review_v02.md",
            "loop_iteration": 1,
            "pre_refine_checksum": "abc123",
        },
    }

    group_cfg = {
        "step_configs": {
            "codex_review": {
                "on_reject_refine": {
                    "step": "refine_plan",
                    "artifact": "QWEN_PLAN_FILE",
                },
            },
        },
    }

    result = _validate_owned_recovery_context(
        attempt_record=attempt_record,
        group_name="plan_first_review_v1",
        job_id="test-job-123",
        baseline=1,
        step="refine_plan",
        input_revision=2,
        target_revision=3,
        group_cfg=group_cfg,
        planning_folder="Planning/test-project",
    )

    assert result is None  # Invalid context rejected
