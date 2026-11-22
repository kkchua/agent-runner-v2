"""F3 Correction Tests — Symmetric terminal identities with mandatory evidence verification.

These tests verify that terminal replay validates identity and evidence correctly.
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


class TestF3_AppliedEvidenceVerification:
    """F3: Applied terminal replay must verify evidence (mandatory)."""

    def test_applied_replay_requires_evidence(self, tmp_path, monkeypatch):
        """Applied replay fails if evidence (path/digest) is missing."""
        # Setup: State with applied attempt but missing evidence
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
                    "status": "applied",
                    "applied_result": {
                        "remark": "Good",
                        # Missing output_path and output_digest
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

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Create identical APPROVED result
        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={},
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

        # Should fail with TERMINAL_EVIDENCE_MISSING
        assert exit_code == 1
        assert state.get("last_failure_code") == "TERMINAL_EVIDENCE_MISSING"

    def test_applied_replay_fails_missing_file(self, tmp_path, monkeypatch):
        """Applied replay fails if output file doesn't exist."""
        # Setup: State with applied attempt and evidence pointing to missing file
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
                    "status": "applied",
                    "applied_result": {
                        "remark": "Good",
                        "output_path": "Planning/test/Qwen_Plan_v01.md",
                        "output_digest": "abc123",
                        "output_evidence": {
                            "relative_path": "Planning/test/Qwen_Plan_v01.md",
                            "digest": "abc123",
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

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Create identical APPROVED result
        # R16-R6: Incoming path must match stored path exactly
        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        group_cfg = {"step_configs": {"generate_plan": {}}}

        # Call route_after_step - file doesn't exist
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

        # Should fail with TERMINAL_EVIDENCE_MISSING
        assert exit_code == 1
        assert state.get("last_failure_code") == "TERMINAL_EVIDENCE_MISSING"

    def test_applied_replay_fails_digest_mismatch(self, tmp_path, monkeypatch):
        """Applied replay fails if file digest changed."""
        # Setup: State with applied attempt
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
                    "status": "applied",
                    "applied_result": {
                        "remark": "Good",
                        "output_path": "Planning/test/Qwen_Plan_v01.md",
                        "output_digest": "stored_digest_abc123",  # Different from actual
                        "output_evidence": {
                            "relative_path": "Planning/test/Qwen_Plan_v01.md",
                            "digest": "stored_digest_abc123",
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

        # Create output file with DIFFERENT content
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("changed content - different digest")

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Create identical APPROVED result
        # R16-R6: Incoming path must match stored path exactly
        result = StepResult(
            status="APPROVED",
            remark="Good",
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
            state=state,
            step="generate_plan",
            step_cfg={},
            step_result=result,
            coder_used="test-coder",
            max_rejects=3,
        )

        # Should fail with TERMINAL_EVIDENCE_CONFLICT
        assert exit_code == 1
        assert state.get("last_failure_code") == "TERMINAL_EVIDENCE_CONFLICT"


class TestF3_RejectedTerminalIdentity:
    """F3: Rejected terminal replay uses status + remark + reject_code."""

    def test_rejected_replay_matches_identity(self, tmp_path, monkeypatch):
        """Rejected replay succeeds with matching identity."""
        # Setup: State with rejected attempt
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
                    "status": "rejected",
                    "rejected_result": {
                        "remark": "Needs work",
                        "reject_code": "QUALITY",
                        "exit_code": 1,
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

        original_snapshot = copy.deepcopy(state)

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Create identical REJECTED result
        result = StepResult(
            status="REJECTED",
            remark="Needs work",
            artifacts={},
            reject_code="QUALITY",
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

        # Should return unchanged
        assert exit_code == 1
        assert returned_state == original_snapshot

    def test_rejected_replay_different_remark_conflicts(self, tmp_path, monkeypatch):
        """Rejected replay with different remark conflicts."""
        # Setup: State with rejected attempt
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
                    "status": "rejected",
                    "rejected_result": {
                        "remark": "Needs work",
                        "reject_code": "QUALITY",
                        "exit_code": 1,
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

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Create REJECTED result with DIFFERENT remark
        result = StepResult(
            status="REJECTED",
            remark="Different remark",  # Changed!
            artifacts={},
            reject_code="QUALITY",
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

        # Should conflict
        assert exit_code == 1
        assert state.get("last_failure_code") == "TERMINAL_RESULT_CONFLICT"