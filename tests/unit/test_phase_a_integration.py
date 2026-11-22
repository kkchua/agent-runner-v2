"""Integration tests for Phase A acceptance criteria.

These tests use real routing/eligibility with temporary persistence.
Only coder/notifications are mocked.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

import agent_runner_v2.job_state as job_state
import agent_runner_v2.v2.workflow_router as workflow_router
from agent_runner_v2.step_runner import StepResult


class TestRejectionAccounting:
    """Test that rejection is consumed and accounted once."""

    def test_first_rejection_consumed_once(self, tmp_path, monkeypatch):
        """First rejection should be recorded once, not double-counted on replay."""
        # Setup: Create a job state with an attempt record
        job_dir = tmp_path / "jobs" / "test-group"
        job_dir.mkdir(parents=True)
        job_file = job_dir / "test-job.json"
        
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
            "loop_context": {"active_attempt_id": attempt_id},
            "reject_counts": {},
            "retry_history": [],
        }
        
        # Save initial state
        job_file.write_text(json.dumps(state))
        
        # Mock save_job to use temp file
        def mock_save(group_name, job_id, state_to_save):
            job_file.write_text(json.dumps(state_to_save))
        monkeypatch.setattr(job_state, "save_job", mock_save)
        
        # Mock notifications
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)
        
        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        
        # Create first rejection result
        rejection_result = StepResult(
            status="REJECTED",
            remark="Needs improvement",
            artifacts={},
            reject_code="QUALITY",
            meta_json_path="test/meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )
        
        group_cfg = {
            "step_configs": {
                "generate_plan": {},  # No on_reject_refine
            },
        }
        
        # First rejection via route_after_step
        state1, exit_code1 = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="generate_plan",
            step_cfg={},
            step_result=rejection_result,
            coder_used="test-coder",
            max_rejects=3,
        )
        
        # Should return exit_code=1 (intervention required)
        assert exit_code1 == 1
        
        # Reload state from disk
        reloaded_state = json.loads(job_file.read_text())
        
        # Check that attempt is marked as rejected
        assert reloaded_state["attempt_records"][attempt_id]["status"] == "rejected"
        
        # Check that reject_counts has exactly 1
        assert reloaded_state["reject_counts"].get("generate_plan", 0) == 1
        
        # Check that retry_history has exactly 1 entry
        assert len(reloaded_state["retry_history"]) == 1
        
        # Now deliver the same rejection again (replay)
        state2, exit_code2 = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=reloaded_state,
            step="generate_plan",
            step_cfg={},
            step_result=rejection_result,
            coder_used="test-coder",
            max_rejects=3,
        )
        
        # Reload state again
        final_state = json.loads(job_file.read_text())
        
        # CRITICAL: reject_counts should still be 1 (no double-count)
        assert final_state["reject_counts"].get("generate_plan", 0) == 1, \
            "Rejection was double-counted on replay"
        
        # retry_history should still have 1 entry
        assert len(final_state["retry_history"]) == 1, \
            "retry_history grew on replay"
        
        # Attempt status should still be rejected
        assert final_state["attempt_records"][attempt_id]["status"] == "rejected"
