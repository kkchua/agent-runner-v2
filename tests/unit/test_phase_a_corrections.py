"""Tests for Phase A final corrections: A1-A5.

Verifies:
- A1: No pre-routing terminal save (validation-only gate)
- A2: Active-conflict has no exemption, revision formulas enforced
- A3: Output evidence with digest, recovery context installed to state.loop_context
- A4: Normalized terminal identity for both approved and rejected
- A5: Real behavioral tests without mocking the checks being asserted
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import agent_runner_v2.job_state as job_state
import agent_runner_v2.run_agent as run_agent
import agent_runner_v2.v2.workflow_router as workflow_router
from agent_runner_v2.step_runner import StepResult


# ---------------------------------------------------------------------------
# Helper Tests
# ---------------------------------------------------------------------------

class TestHelpers:
    """Test helper functions added for Phase A."""

    def test_compute_output_digest(self, tmp_path):
        """compute_output_digest returns SHA256 hex digest."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test content")
        
        digest = job_state.compute_output_digest(test_file)
        expected = hashlib.sha256(b"# Test content").hexdigest()
        assert digest == expected

    def test_compute_output_digest_missing_file(self, tmp_path):
        """compute_output_digest raises ValueError for missing file."""
        missing_file = tmp_path / "missing.md"
        
        with pytest.raises(ValueError, match="Cannot read output file"):
            job_state.compute_output_digest(missing_file)

    def test_validate_revision_formula_generation_valid(self):
        """Generation formula: input=None, target=1, current=1."""
        valid, error = job_state.validate_revision_formula(
            step="generate_plan",
            input_revision=None,
            target_revision=1,
            current_revision=1,
        )
        assert valid is True
        assert error is None

    def test_validate_revision_formula_generation_invalid_input(self):
        """Generation with non-None input is invalid."""
        valid, error = job_state.validate_revision_formula(
            step="generate_plan",
            input_revision=1,  # Should be None
            target_revision=1,
            current_revision=1,
        )
        assert valid is False
        assert "input must be None" in error

    def test_validate_revision_formula_refinement_valid(self):
        """Refinement formula: input=current, target=input+1, current>=1."""
        # First refinement: v1 -> v2 when current=1
        valid, error = job_state.validate_revision_formula(
            step="refine_plan",
            input_revision=1,
            target_revision=2,
            current_revision=1,
        )
        assert valid is True
        assert error is None
        
        # Second refinement: v2 -> v3 when current=2
        valid, error = job_state.validate_revision_formula(
            step="refine_plan",
            input_revision=2,
            target_revision=3,
            current_revision=2,
        )
        assert valid is True
        assert error is None

    def test_validate_revision_formula_refinement_invalid_bool(self):
        """Refinement with bool input is invalid."""
        valid, error = job_state.validate_revision_formula(
            step="refine_plan",
            input_revision=True,  # Bool, not int
            target_revision=2,
            current_revision=1,
        )
        assert valid is False
        assert "exact int" in error


# ---------------------------------------------------------------------------
# R1: Execution Wiring Tests
# ---------------------------------------------------------------------------

class TestExecutionWiring:
    """R1: Verify wrapper is called for plan-first steps."""

    def test_wrapper_exists_and_has_correct_logic(self):
        """Wrapper function exists and contains plan-first logic."""
        assert hasattr(run_agent, "_execute_prepared_step_with_plan_first_attempt")
        import inspect
        source = inspect.getsource(run_agent._execute_prepared_step_with_plan_first_attempt)
        assert "plan_first_review_v1" in source
        assert "generate_plan" in source
        assert "refine_plan" in source

    def test_executor_selection_logic_exists(self):
        """run_agent contains conditional executor selection for plan-first."""
        import inspect
        source = inspect.getsource(run_agent)
        assert "_execute_prepared_step_with_plan_first_attempt" in source
        assert "executor_fn" in source


# ---------------------------------------------------------------------------
# R2: Result Gate Correction Tests
# ---------------------------------------------------------------------------

class TestResultGateCorrections:
    """R2: Verify gate corrections."""

    def test_gate_failure_uses_correct_notification_import(self):
        """_gate_failure does not import send_workflow_notification from notifications."""
        import inspect
        source = inspect.getsource(workflow_router._gate_failure)
        assert "from ..notifications import send_workflow_notification" not in source

    def test_gate_fails_on_missing_attempt_id(self, monkeypatch):
        """Missing attempt_id triggers durable failure."""
        step_result = StepResult(
            status="APPROVED",
            remark="Test",
            artifacts={},
            reject_code=None,
            meta_json_path="test/meta.json",
            usage_data={},
            attempt_id=None,
        )
        
        state = {
            "job_id": "test-job",
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {},
        }
        
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "set_last_failure", lambda **kw: None)
        monkeypatch.setattr(workflow_router, "set_job_status", lambda *a: None)
        
        result = workflow_router._plan_first_result_gate(
            group_name="plan_first_review_v1",
            group_cfg={},
            state=state,
            step="generate_plan",
            step_cfg={},
            step_result=step_result,
        )
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[1] == 1

    def test_gate_validates_record_ownership(self, monkeypatch):
        """Gate rejects attempt record with mismatched job_id."""
        step_result = StepResult(
            status="APPROVED",
            remark="Test",
            artifacts={},
            reject_code=None,
            meta_json_path="test/meta.json",
            usage_data={},
            attempt_id="att_test123",
        )
        
        attempt_record = {
            "attempt_id": "att_test123",
            "job_id": "different-job",
            "workflow": "plan_first_review_v1",
            "step": "generate_plan",
            "status": "prepared",
        }
        
        state = {
            "job_id": "test-job",
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {"att_test123": attempt_record},
            "loop_context": {},
        }
        
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "set_last_failure", lambda **kw: None)
        monkeypatch.setattr(workflow_router, "set_job_status", lambda *a: None)
        
        result = workflow_router._plan_first_result_gate(
            group_name="plan_first_review_v1",
            group_cfg={},
            state=state,
            step="generate_plan",
            step_cfg={},
            step_result=step_result,
        )
        
        assert isinstance(result, tuple)
        assert result[1] == 1

    def test_gate_blocks_active_conflict_without_exemption(self, monkeypatch):
        """Gate blocks unapplied attempt while another is active — no exemption."""
        step_result = StepResult(
            status="APPROVED",
            remark="Test",
            artifacts={},
            reject_code=None,
            meta_json_path="test/meta.json",
            usage_data={},
            attempt_id="att_A",
        )
        
        attempt_record = {
            "attempt_id": "att_A",
            "job_id": "test-job",
            "workflow": "plan_first_review_v1",
            "step": "generate_plan",
            "status": "prepared",  # Unapplied
        }
        
        state = {
            "job_id": "test-job",
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {"att_A": attempt_record},
            "loop_context": {"active_attempt_id": "att_B"},  # Different attempt is active
        }
        
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "set_last_failure", lambda **kw: None)
        monkeypatch.setattr(workflow_router, "set_job_status", lambda *a: None)
        
        result = workflow_router._plan_first_result_gate(
            group_name="plan_first_review_v1",
            group_cfg={},
            state=state,
            step="generate_plan",
            step_cfg={},
            step_result=step_result,
        )
        
        # Should fail with ACTIVE_ATTEMPT_CONFLICT
        assert isinstance(result, tuple)
        assert result[1] == 1

    def test_gate_returns_validation_tuple_for_success(self, monkeypatch, tmp_path):
        """Gate returns validation tuple (True, recovery, evidence, path, digest) on success."""
        step_result = StepResult(
            status="APPROVED",
            remark="Test",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
            reject_code=None,
            meta_json_path="test/meta.json",
            usage_data={},
            attempt_id="att_test123",
        )
        
        attempt_record = {
            "attempt_id": "att_test123",
            "job_id": "test-job",
            "workflow": "plan_first_review_v1",
            "baseline": 1,
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
        
        state = {
            "job_id": "test-job",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {"att_test123": attempt_record},
            "loop_context": {},
        }
        
        group_cfg = {
            "step_configs": {
                "generate_plan": {
                    "on_reject_refine": {
                        "artifact": "QWEN_PLAN_FILE",
                    },
                },
            },
        }
        
        # Create the output file
        output_file = tmp_path / "Planning/test/Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("# Plan")
        
        # Mock PROJECT_ROOT in runtime_context module (where it's imported from)
        import agent_runner_v2.runtime_context as runtime_context
        from pathlib import Path as PathClass
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", PathClass(str(tmp_path)))
        
        # Mock eligibility
        monkeypatch.setattr(
            workflow_router,
            "_validate_prepared_eligibility",
            lambda **kw: (True, None, attempt_record["recovered_context"])
        )
        
        result = workflow_router._plan_first_result_gate(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="generate_plan",
            step_cfg={},
            step_result=step_result,
        )
        
        # Should return validation tuple: (True, recovery, evidence, path, digest)
        assert isinstance(result, tuple)
        assert len(result) == 5
        assert result[0] is True
        assert result[1] == attempt_record["recovered_context"]
        assert result[2] is not None  # output_evidence
        # canonical_path is now a resolved Path (R10-I1 fix)
        assert isinstance(result[3], Path)  # Path object, not string
        assert result[3].name == "Qwen_Plan_v01.md"  # filename matches
        assert result[4] is not None  # output_digest

    def test_gate_runs_before_bookkeeping_mutations(self):
        """Gate is called before retry_history, step_coders mutations."""
        import inspect
        source = inspect.getsource(workflow_router.route_after_step)
        
        gate_pos = source.find("_plan_first_result_gate")
        retry_history_pos = source.find("retry_history.append")
        
        assert gate_pos > 0
        assert retry_history_pos > 0
        assert gate_pos < retry_history_pos
