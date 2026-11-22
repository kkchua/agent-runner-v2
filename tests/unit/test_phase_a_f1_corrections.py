"""F1 Correction Tests — Gate before defaults, copy before setdefault.

These tests verify that plan-first routing never mutates the original caller state.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from agent_runner_v2.step_runner import StepResult
from agent_runner_v2.v2 import workflow_router
from agent_runner_v2 import job_state


class TestF1_CallerIsolation:
    """F1: Original caller state must remain untouched on any failure."""

    def test_original_state_untouched_on_save_failure(self, tmp_path, monkeypatch):
        """After save failure, original state equals pre-call snapshot."""
        # Setup: Create a minimal job state
        original_state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                "att_test123": {
                    "attempt_id": "att_test123",
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                    # R16-R6: Valid inactive context for generation
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
            "loop_context": {"active_attempt_id": "att_test123"},
        }

        # Create output file for APPROVED
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test plan content")

        # Save original snapshot
        original_snapshot = copy.deepcopy(original_state)

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job to raise exception
        def mock_save_fail(group_name, job_id, state_to_save):
            raise RuntimeError("Simulated save failure")
        monkeypatch.setattr(job_state, "save_job", mock_save_fail)

        # Mock notifications
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Create APPROVED result
        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={"QWEN_PLAN_FILE": str(output_file.relative_to(tmp_path))},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id="att_test123",
        )

        group_cfg = {
            "step_configs": {
                "generate_plan": {},
            },
        }

        # Call route_after_step - should propagate exception
        with pytest.raises(RuntimeError, match="Simulated save failure"):
            workflow_router.route_after_step(
                group_name="plan_first_review_v1",
                group_cfg=group_cfg,
                state=original_state,
                step="generate_plan",
                step_cfg={},
                step_result=result,
                coder_used="test-coder",
                max_rejects=3,
            )

        # CRITICAL: Original state must equal pre-call snapshot
        assert original_state == original_snapshot, \
            f"Original state was mutated! Keys changed: {set(original_state.keys()) - set(original_snapshot.keys())}"

    def test_no_setdefault_on_original_for_plan_first(self, tmp_path, monkeypatch):
        """Plan-first routing must not call setdefault on original state."""
        # Setup: Create state WITHOUT reject_counts, retry_history, etc.
        original_state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                "att_test123": {
                    "attempt_id": "att_test123",
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                    # R16-R6: Valid inactive context for generation
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
            "loop_context": {"active_attempt_id": "att_test123"},
        }

        # Create output file
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test plan content")

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Create APPROVED result
        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={"QWEN_PLAN_FILE": str(output_file.relative_to(tmp_path))},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id="att_test123",
        )

        group_cfg = {"step_configs": {"generate_plan": {}}}

        # Call route_after_step
        returned_state, exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=original_state,
            step="generate_plan",
            step_cfg={},
            step_result=result,
            coder_used="test-coder",
            max_rejects=3,
        )

        # CRITICAL: Original state must NOT have reject_counts, retry_history, etc.
        # These should only exist on the returned transition, not the original
        assert "reject_counts" not in original_state, \
            "setdefault was called on original state - reject_counts added"
        assert "retry_history" not in original_state, \
            "setdefault was called on original state - retry_history added"
        assert "last_model_output" not in original_state, \
            "last_model_output was added to original state"

        # Returned state should have these
        assert "reject_counts" in returned_state
        assert "retry_history" in returned_state


class TestF1_TerminalReplayUnchanged:
    """F1: Terminal replay must return state completely unchanged."""

    def test_terminal_replay_no_mutation(self, tmp_path, monkeypatch):
        """Identical terminal replay returns state unchanged (no copy, no mutations)."""
        # Create output file with known content
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_content = "test plan content"
        output_file.write_text(output_content)

        # Compute real SHA256 digest
        import hashlib
        real_digest = hashlib.sha256(output_content.encode()).hexdigest()

        # Setup: Create state with applied attempt
        attempt_id = "att_test123"
        original_state = {
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
                    "status": "applied",  # Already applied
                    "applied_result": {
                        "remark": "Good",
                        "output_path": "Planning/test/Qwen_Plan_v01.md",
                        "output_digest": real_digest,  # Real digest
                        "output_evidence": {
                            "relative_path": "Planning/test/Qwen_Plan_v01.md",
                            "digest": real_digest,
                        },
                    },
                    # R16-R6: Valid inactive context for generation
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

        # Save original object id
        original_id = id(original_state)
        original_snapshot = copy.deepcopy(original_state)

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Create identical APPROVED result
        # R16-R6: Incoming path must match stored path exactly
        result = StepResult(
            status="APPROVED",
            remark="Good",  # Same as stored
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
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
            state=original_state,
            step="generate_plan",
            step_cfg={},
            step_result=result,
            coder_used="test-coder",
            max_rejects=3,
        )

        # CRITICAL: Returned state must be THE SAME object (no copy made)
        assert id(returned_state) == original_id, \
            "Terminal replay created a copy instead of returning original"

        # State must equal snapshot (no mutations)
        assert returned_state == original_snapshot, \
            "Terminal replay mutated the state"


class TestF1_MissingAttemptIdBlocked:
    """F1: Missing attempt_id must be blocked by gate, not fall to generic routing."""

    def test_missing_attempt_id_gate_failure(self, tmp_path, monkeypatch):
        """Missing attempt_id produces gate failure (intervention), not generic routing."""
        # Setup: State with no attempt_records
        original_state = {
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

        original_snapshot = copy.deepcopy(original_state)

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Create result with NO attempt_id
        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=None,  # Missing!
        )

        group_cfg = {"step_configs": {"generate_plan": {}}}

        # Call route_after_step
        returned_state, exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=original_state,
            step="generate_plan",
            step_cfg={},
            step_result=result,
            coder_used="test-coder",
            max_rejects=3,
        )

        # Gate failure: exit_code=1 (intervention required) - not 2 (fatal)
        assert exit_code == 1, f"Expected exit_code=1 for gate failure, got {exit_code}"

        # CRITICAL: Original state should be unchanged (no setdefault)
        # Note: The gate does mutate the state (set_last_failure, set_job_status) because
        # it needs to record the failure. But it should NOT add reject_counts, retry_history, etc.
        # The gate only records the failure, not bookkeeping defaults.
        assert "reject_counts" not in original_state, \
            "Gate failure added reject_counts to original state"
        assert "retry_history" not in original_state, \
            "Gate failure added retry_history to original state"