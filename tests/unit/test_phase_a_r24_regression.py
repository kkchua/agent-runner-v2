"""Phase A baseline and observation regressions.

These tests verify the R22/R24 findings:
- R22-01: Failed replay rejects equivalent relative/absolute paths
- R24-01: Record baseline None/missing bypasses validation
- R22-02: Positive range validation missing
"""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from unittest.mock import patch

import pytest

from agent_runner_v2.step_runner import StepResult
from agent_runner_v2.v2 import workflow_router
from agent_runner_v2 import job_state


@pytest.fixture(autouse=True)
def isolated_job_storage(tmp_path, monkeypatch):
    """Keep even imported save aliases inside this test's temporary storage."""
    monkeypatch.setattr(
        job_state, "job_state_path",
        lambda group, job_id: tmp_path / "jobs" / group / job_id / "job.json",
    )


# ---------------------------------------------------------------------------
# Production persistence fixture (module-level for pytest)
# ---------------------------------------------------------------------------

@pytest.fixture
def production_persistence(tmp_path, monkeypatch):
    """Shared fixture that redirects production job paths and wraps original save/load."""
    # Capture original production functions BEFORE patching
    original_save_job = job_state.save_job
    original_load_job = job_state.load_job

    # Create jobs directory
    jobs_dir = tmp_path / "jobs" / "plan_first_review_v1"
    jobs_dir.mkdir(parents=True, exist_ok=True)

    # Track counts
    save_count = [0]
    load_count = [0]
    notification_count = [0]

    # Redirect job_dir to temp path
    def patched_job_dir(group_name: str, job_id: str) -> Path:
        return jobs_dir / job_id

    # Counting save wrapper that CALLS captured original
    def counting_save_wrapper(group_name: str, job_id: str, state_to_save: dict) -> None:
        save_count[0] += 1
        original_save_job(group_name, job_id, state_to_save)

    # Counting load wrapper that CALLS captured original
    def counting_load_wrapper(group_name: str, job_id: str) -> dict | None:
        load_count[0] += 1
        try:
            return original_load_job(group_name, job_id)
        except FileNotFoundError:
            return None

    # Mock only external effects
    def mock_notification(*args, **kwargs):
        notification_count[0] += 1

    import agent_runner_v2.runtime_context as runtime_context
    monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
    monkeypatch.setattr(job_state, "job_dir", patched_job_dir)
    # Patch both job_state and workflow_router since router imports save_job at module level
    monkeypatch.setattr(job_state, "save_job", counting_save_wrapper)
    monkeypatch.setattr(workflow_router, "save_job", counting_save_wrapper)
    monkeypatch.setattr(job_state, "load_job", counting_load_wrapper)
    monkeypatch.setattr(workflow_router, "send_workflow_notification", mock_notification)
    monkeypatch.setattr(workflow_router, "send_step_notification", mock_notification)

    return {
        "jobs_dir": jobs_dir,
        "save_count": save_count,
        "load_count": load_count,
        "notification_count": notification_count,
        "load_state": lambda job_id: counting_load_wrapper("plan_first_review_v1", job_id),
        "save_state": lambda job_id, state: counting_save_wrapper("plan_first_review_v1", job_id, state),
    }


# ---------------------------------------------------------------------------
# R22-01: Failed replay path resolution (REGRESSION)
# ---------------------------------------------------------------------------

class TestR22_01_FailedReplayPathResolution:
    """R22-01: Failed branch uses slash normalization, not path resolution."""

    def test_failed_replay_relative_to_absolute_preserves_state(self, tmp_path, monkeypatch):
        """Regression: Failed receipt with relative, replay with absolute incorrectly rejects."""
        # Setup: Create a failed attempt with RELATIVE path
        attempt_id = "att_test123"
        relative_path = "Planning/test/Qwen_Plan_v01.md"
        absolute_path = str(tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md")

        # Create the output file FIRST
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test content")

        # Compute correct digest for the file
        from agent_runner_v2.job_state import compute_output_digest
        correct_digest = compute_output_digest(output_file)

        # NOW create state with correct digest
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "failed",
                    "failed_result": {
                        "original_status": "APPROVED",
                        "remark": "Good",
                        "output_path": relative_path,  # RELATIVE
                        "output_digest": correct_digest,  # Correct digest
                        "output_missing": False,
                        "output_unreadable": False,
                    },
                    "recovered_context": {
                        "job_id": "test-job",
                        "group_name": "plan_first_review_v1",
                        "baseline": 1,
                        "step": "generate_plan",
                        "input_revision": None,
                        "target_revision": 1,
                        "active": False,
                    },
                }
            },
            "loop_context": {},
        }

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Create APPROVED result with ABSOLUTE path (equivalent)
        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={"QWEN_PLAN_FILE": absolute_path},  # ABSOLUTE (equivalent)
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        group_cfg = {"step_configs": {"generate_plan": {}}}

        # Call route_after_step
        returned_state, exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="generate_plan",
            step_cfg={},
            step_result=result,
            coder_used="test-coder",
            max_rejects=3,
        )

        # Failed replay returns exit_code=1 (the stored failure exit code)
        # Path resolution should accept equivalent relative/absolute paths
        # If paths are NOT equivalent, returns exit_code=1 with TERMINAL_EVIDENCE_CONFLICT
        # This test verifies the path resolution fix allows equivalent paths
        assert exit_code == 1, f"Failed replay should return exit_code=1"
        assert returned_state.get("last_failure_code") != "TERMINAL_EVIDENCE_CONFLICT", \
            f"Should accept equivalent paths, got TERMINAL_EVIDENCE_CONFLICT"
        assert returned_state == state

    def test_failed_replay_absolute_to_relative_preserves_state(self, tmp_path, monkeypatch):
        """Regression: Failed receipt with absolute, replay with relative incorrectly rejects."""
        # Setup: Create a failed attempt with ABSOLUTE path
        attempt_id = "att_test123"
        relative_path = "Planning/test/Qwen_Plan_v01.md"
        absolute_path = str(tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md")

        # Create the output file FIRST
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test content")

        # Compute correct digest for the file
        from agent_runner_v2.job_state import compute_output_digest
        correct_digest = compute_output_digest(output_file)

        # NOW create state with correct digest
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "failed",
                    "failed_result": {
                        "original_status": "APPROVED",
                        "remark": "Good",
                        "output_path": absolute_path,  # ABSOLUTE
                        "output_digest": correct_digest,  # Correct digest
                        "output_missing": False,
                        "output_unreadable": False,
                    },
                    "recovered_context": {
                        "job_id": "test-job",
                        "group_name": "plan_first_review_v1",
                        "baseline": 1,
                        "step": "generate_plan",
                        "input_revision": None,
                        "target_revision": 1,
                        "active": False,
                    },
                }
            },
            "loop_context": {},
        }

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Create APPROVED result with RELATIVE path (equivalent)
        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={"QWEN_PLAN_FILE": relative_path},  # RELATIVE (equivalent)
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        group_cfg = {"step_configs": {"generate_plan": {}}}

        # Call route_after_step
        returned_state, exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="generate_plan",
            step_cfg={},
            step_result=result,
            coder_used="test-coder",
            max_rejects=3,
        )

        # Failed replay returns exit_code=1 (the stored failure exit code)
        # Path resolution should accept equivalent relative/absolute paths
        # If paths are NOT equivalent, returns exit_code=1 with TERMINAL_EVIDENCE_CONFLICT
        # This test verifies the path resolution fix allows equivalent paths
        assert exit_code == 1, f"Failed replay should return exit_code=1"
        assert returned_state.get("last_failure_code") != "TERMINAL_EVIDENCE_CONFLICT", \
            f"Should accept equivalent paths, got TERMINAL_EVIDENCE_CONFLICT"
        assert returned_state == state


# ---------------------------------------------------------------------------
# R24-01: Record baseline validation (REGRESSION)
# ---------------------------------------------------------------------------

class TestR24_01_RecordBaselineValidation:
    """R24-01: Record baseline None/missing bypasses validation."""

    def test_eligibility_rejects_record_baseline_none(self, tmp_path, monkeypatch):
        """Regression: Eligibility accepts record baseline None (should reject)."""
        attempt_id = "att_test123"

        # Create state with record missing baseline (None)
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": None,  # DEFECT: Should be rejected
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                    "recovered_context": {
                        "job_id": "test-job",
                        "group_name": "plan_first_review_v1",
                        "baseline": 1,
                        "step": "generate_plan",
                        "input_revision": None,
                        "target_revision": 1,
                        "active": False,
                    },
                }
            },
            "loop_context": {},
        }

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Call _validate_prepared_eligibility directly
        is_valid, error, recovery = workflow_router._validate_prepared_eligibility(
            state=state,
            group_name="plan_first_review_v1",
            step="generate_plan",
            attempt_id=attempt_id,
            baseline=1,
            input_revision=None,
            target_revision=1,
        )

        # DEFECT: Should be False (rejected), but currently True
        assert is_valid is False, f"Should reject record baseline None, got valid=True with error: {error}"

    def test_eligibility_rejects_record_baseline_true(self, tmp_path, monkeypatch):
        """Regression: Eligibility accepts record baseline True (should reject bool)."""
        attempt_id = "att_test123"

        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": True,  # DEFECT: bool accepted via equality (True == 1)
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                    "recovered_context": {
                        "job_id": "test-job",
                        "group_name": "plan_first_review_v1",
                        "baseline": 1,
                        "step": "generate_plan",
                        "input_revision": None,
                        "target_revision": 1,
                        "active": False,
                    },
                }
            },
            "loop_context": {},
        }

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Call _validate_prepared_eligibility directly
        is_valid, error, recovery = workflow_router._validate_prepared_eligibility(
            state=state,
            group_name="plan_first_review_v1",
            step="generate_plan",
            attempt_id=attempt_id,
            baseline=1,
            input_revision=None,
            target_revision=1,
        )

        # DEFECT: Should be False (rejected), but currently True (True == 1)
        assert is_valid is False, f"Should reject record baseline True (bool), got valid=True"


# ---------------------------------------------------------------------------
# R22-02: Positive range validation (REGRESSION)
# ---------------------------------------------------------------------------

class TestR22_02_PositiveRangeValidation:
    """R22-02: Missing positive range validation for baselines."""

    def test_prepare_rejects_baseline_zero(self, tmp_path, monkeypatch):
        """Regression: prepare_plan_attempt accepts baseline=0 (should reject)."""
        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Create minimal valid state with baseline=0
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "requirements_baseline": 0,  # DEFECT: Should be rejected
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {},
        }

        # Call prepare_plan_attempt
        try:
            result = job_state.prepare_plan_attempt(
                group_name="plan_first_review_v1",
                job_id="test-job",
                state=state,
                step="generate_plan",
                step_cfg={},
                group_cfg={"step_configs": {"generate_plan": {}}},
                prepared_context={},
                project_root=tmp_path,
            )
            # DEFECT: Should have raised ValueError
            pytest.fail(f"Should reject baseline=0, but got result: {result}")
        except ValueError as e:
            # Expected after fix
            assert "positive" in str(e).lower() or "baseline" in str(e).lower()

    def test_prepare_rejects_baseline_negative(self, tmp_path, monkeypatch):
        """Regression: prepare_plan_attempt accepts baseline=-1 (should reject)."""
        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Create minimal valid state with baseline=-1
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "requirements_baseline": -1,  # DEFECT: Should be rejected
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {},
        }

        # Call prepare_plan_attempt
        try:
            result = job_state.prepare_plan_attempt(
                group_name="plan_first_review_v1",
                job_id="test-job",
                state=state,
                step="generate_plan",
                step_cfg={},
                group_cfg={"step_configs": {"generate_plan": {}}},
                prepared_context={},
                project_root=tmp_path,
            )
            # DEFECT: Should have raised ValueError
            pytest.fail(f"Should reject baseline=-1, but got result: {result}")
        except ValueError as e:
            # Expected after fix
            assert "positive" in str(e).lower() or "baseline" in str(e).lower()

    def test_eligibility_rejects_baseline_zero(self, tmp_path, monkeypatch):
        """Regression: Eligibility accepts current baseline=0 (should reject)."""
        attempt_id = "att_test123"

        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 0,  # DEFECT: Should be rejected
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                    "recovered_context": None,
                }
            },
            "loop_context": {},
        }

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Call _validate_prepared_eligibility directly
        is_valid, error, recovery = workflow_router._validate_prepared_eligibility(
            state=state,
            group_name="plan_first_review_v1",
            step="generate_plan",
            attempt_id=attempt_id,
            baseline=0,  # Matches state
            input_revision=None,
            target_revision=1,
        )

        # DEFECT: Should be False (rejected), but currently True
        assert is_valid is False, f"Should reject baseline=0, got valid=True with error: {error}"


# ---------------------------------------------------------------------------
# R26-01: Actual review producer flow with production persistence
# ---------------------------------------------------------------------------

class TestR26_01_ReviewRefinementFlow:
    """A16-01: Generation → review rejection → preparation → refinement with MD5."""

    def test_review_rejection_requires_declared_codex_review_file(
        self, tmp_path, monkeypatch, production_persistence
    ):
        """A16-01: Review rejection requires declared CODEX_REVIEW_FILE.

        Verifies the A16-01 gate check for review declaration.
        """
        # Create planning folder
        planning_folder = tmp_path / "Planning" / "test"
        planning_folder.mkdir(parents=True, exist_ok=True)

        # Create target plan file
        target_file = planning_folder / "Qwen_Plan_v01.md"
        target_file.write_text("Plan content")

        # State after generation
        attempt_id = "att_gen_123"
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "codex_review",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {
                "PLANNING_FOLDER": "Planning/test",
                "QWEN_PLAN_FILE": str(target_file.relative_to(tmp_path)),
            },
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                    "recovered_context": None,
                }
            },
            "loop_context": {},
        }

        # Create REJECTED result WITHOUT CODEX_REVIEW_FILE
        result = StepResult(
            status="REJECTED",
            remark="Needs revision",
            artifacts={},  # No CODEX_REVIEW_FILE
            reject_code="QUALITY",
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        group_cfg = {
            "step_configs": {
                "generate_plan": {},
                "codex_review": {
                    "on_reject_refine": {
                        "step": "refine_plan",
                        "artifact": "QWEN_PLAN_FILE",
                    }
                },
            }
        }

        # Call route_after_step for codex_review
        returned_state, exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="codex_review",
            step_cfg=group_cfg["step_configs"]["codex_review"],
            step_result=result,
            coder_used="test-coder",
            max_rejects=3,
        )

        # Verify: Gate failure for missing declaration
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "MISSING_REVIEW_ARTIFACT_DECLARATION"

    def test_review_omitted_with_present_canonical_fails(self, tmp_path, monkeypatch):
        """A16-01: Omitted declaration when old canonical file exists (stale)."""
        import agent_runner_v2.runtime_context as runtime_context

        # Set up project root
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Create planning folder with OLD review file
        planning_folder = tmp_path / "Planning" / "test"
        planning_folder.mkdir(parents=True, exist_ok=True)
        old_review = planning_folder / "Codex_Review_v01.md"
        old_review.write_text("Old review content")

        # State after generation
        attempt_id = "att_gen_123"
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "codex_review",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {
                "PLANNING_FOLDER": "Planning/test",
                "QWEN_PLAN_FILE": str(planning_folder / "Qwen_Plan_v01.md"),
            },
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                    "recovered_context": None,
                }
            },
            "loop_context": {},
        }

        # Mock save and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Create REJECTED result WITHOUT CODEX_REVIEW_FILE (but file exists on disk)
        result = StepResult(
            status="REJECTED",
            remark="Needs revision",
            artifacts={},  # No CODEX_REVIEW_FILE - stale situation
            reject_code="QUALITY",
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        group_cfg = {"step_configs": {
            "generate_plan": {},
            "codex_review": {"on_reject_refine": {
                "step": "refine_plan", "artifact": "QWEN_PLAN_FILE",
            }},
        }}

        # Call route_after_step
        returned_state, exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="codex_review",
            step_cfg=group_cfg["step_configs"]["codex_review"],
            step_result=result,
            coder_used="test-coder",
            max_rejects=3,
        )

        # Should fail - omitted current declaration with existing file
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "MISSING_REVIEW_ARTIFACT_DECLARATION"
        assert not returned_state.get("loop_context", {}).get("active")


# ---------------------------------------------------------------------------
# R26-03: Complete state/record validation matrix
# ---------------------------------------------------------------------------

class TestR26_03_StateRecordMatrix:
    """Complete negative/boundary scenarios for state/record validation."""

    def test_record_baseline_missing_key_rejected(self, tmp_path, monkeypatch):
        """R24-01: Record baseline missing from record is rejected."""
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        attempt_id = "att_test123"
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    # baseline key missing entirely
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                    "recovered_context": None,
                }
            },
            "loop_context": {},
        }

        is_valid, error, recovery = workflow_router._validate_prepared_eligibility(
            state=state,
            group_name="plan_first_review_v1",
            step="generate_plan",
            attempt_id=attempt_id,
            baseline=1,
            input_revision=None,
            target_revision=1,
        )

        assert is_valid is False, f"Should reject missing baseline key, got error: {error}"

    def test_record_baseline_float_rejected(self, tmp_path, monkeypatch):
        """R24-01: Record baseline float is rejected."""
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        attempt_id = "att_test123"
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1.0,  # Float
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                    "recovered_context": None,
                }
            },
            "loop_context": {},
        }

        is_valid, error, recovery = workflow_router._validate_prepared_eligibility(
            state=state,
            group_name="plan_first_review_v1",
            step="generate_plan",
            attempt_id=attempt_id,
            baseline=1,
            input_revision=None,
            target_revision=1,
        )

        assert is_valid is False, f"Should reject float baseline, got error: {error}"

    def test_record_baseline_valid_match_accepted(self, tmp_path, monkeypatch):
        """R24-01: Record baseline valid match with current is accepted."""
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        attempt_id = "att_test123"
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,  # Valid, matches current
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                    "recovered_context": None,
                }
            },
            "loop_context": {},
        }

        is_valid, error, recovery = workflow_router._validate_prepared_eligibility(
            state=state,
            group_name="plan_first_review_v1",
            step="generate_plan",
            attempt_id=attempt_id,
            baseline=1,
            input_revision=None,
            target_revision=1,
        )

        assert is_valid is True, f"Should accept valid baseline match, got error: {error}"


# ---------------------------------------------------------------------------
# R26-04: Gate failure isolation and non-file rejection
# ---------------------------------------------------------------------------

class TestR26_04_GateAndNonFile:
    """Gate failure isolation and non-file rejection tests."""

    def test_gate_failure_isolated_copy_preserves_original(self, tmp_path, monkeypatch):
        """A16-04: Gate failure returns isolated copy, original unchanged."""
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Create state
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {},
            "loop_context": {},
        }

        original_snapshot = copy.deepcopy(state)

        # Mock save and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Call _gate_failure
        returned_state, returned_exit_code = workflow_router._gate_failure(
            state=state,
            group_name="plan_first_review_v1",
            step="generate_plan",
            failure_code="TEST_FAILURE",
            failure_reason="Test reason",
        )

        # Verify: Original unchanged
        assert state == original_snapshot, "Original state should be unchanged"

        # Verify: Returned state has failure envelope
        assert returned_state.get("last_failure_code") == "TEST_FAILURE"
        assert returned_state.get("last_failure_reason") == "Test reason"

    def test_directory_rejection_no_save_or_notification(self, tmp_path, monkeypatch):
        """A16-05: Directory rejection raises ValueError with no save/notification."""
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Create a directory (not a file)
        output_dir = tmp_path / "Planning" / "test" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Track saves and notifications
        save_count = [0]
        notify_count = [0]

        monkeypatch.setattr(job_state, "save_job", lambda *a: save_count.__setitem__(0, save_count[0] + 1))
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: notify_count.__setitem__(0, notify_count[0] + 1))
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: notify_count.__setitem__(0, notify_count[0] + 1))

        # Create state
        attempt_id = "att_test123"
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                    "recovered_context": None,
                }
            },
            "loop_context": {},
        }

        # Create StepResult with directory path
        step_result = StepResult(
            status="APPROVED",
            remark="Good plan",
            artifacts={"QWEN_PLAN_FILE": str(output_dir)},  # Directory, not file
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        # Try to commit application failure with directory path
        with pytest.raises(ValueError) as exc_info:
            workflow_router._commit_application_failure_from_baseline(
                baseline=state,
                group_name="plan_first_review_v1",
                step="generate_plan",
                step_result=step_result,
                failure_reason="Test failure",
                attempt_id=attempt_id,
                output_digest="abc123",  # Even with digest
            )

        # Verify no save was called
        assert save_count[0] == 0, f"Should not save, but save_count={save_count[0]}"

        # Verify no notification was called
        assert notify_count[0] == 0, f"Should not notify, but notify_count={notify_count[0]}"

    def test_directory_rejection_with_digest_still_rejects(self, tmp_path, monkeypatch):
        """A16-05: Directory rejection is unconditional even with supplied digest."""
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Create a directory
        output_dir = tmp_path / "Planning" / "test" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        attempt_id = "att_test123"
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                    "recovered_context": None,
                }
            },
            "loop_context": {},
        }

        # Create StepResult with directory path
        step_result = StepResult(
            status="APPROVED",
            remark="Good plan",
            artifacts={"QWEN_PLAN_FILE": str(output_dir)},  # Directory
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        # Even with a digest provided, directory should be rejected
        with pytest.raises(ValueError):
            workflow_router._commit_application_failure_from_baseline(
                baseline=state,
                group_name="plan_first_review_v1",
                step="generate_plan",
                step_result=step_result,
                failure_reason="Test failure",
                output_digest="supplied_digest",  # Digest provided
                attempt_id=attempt_id,
            )


# ---------------------------------------------------------------------------
# R28-01: Positive review→refinement flow with production persistence
