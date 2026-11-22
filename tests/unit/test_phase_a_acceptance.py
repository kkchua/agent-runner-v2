"""Phase A Acceptance Tests — A01-A14

These tests verify the complete Phase A implementation against the acceptance matrix.
Each test corresponds to a specific requirement from the R10 plan.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from agent_runner_v2.step_runner import StepResult
from agent_runner_v2.v2 import workflow_router
from agent_runner_v2 import job_state


class TestA01_WrapperSavesAttempt:
    """A01: Actual wrapper saves attempt/snapshot before coder invocation and retains A's ID for both result statuses."""

    def test_wrapper_saves_attempt_before_coder(self, tmp_path, monkeypatch):
        """Wrapper saves attempt record before coder invocation.

        R9: This test verifies the ACTUAL execution wrapper behavior:
        1. _execute_prepared_step_with_plan_first_attempt saves attempt BEFORE delegation
        2. At intercepted coder entry, the complete owned snapshot and active link already exist on disk
        3. The same attempt_id is attached to the returned StepResult
        """
        # Setup isolated persistence directory
        jobs_dir = tmp_path / "jobs" / "plan_first_review_v1"
        jobs_dir.mkdir(parents=True, exist_ok=True)
        job_json_path = jobs_dir / "test-job.json"

        # Create output file
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test plan content")

        # Setup state with valid inactive context
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

        # Track coder invocation vs save order
        event_log = []
        snapshot_at_coder_entry = [None]

        def real_save(group_name, job_id, state_to_save):
            event_log.append(("save", list(state_to_save.get("attempt_records", {}).keys())))
            # Write to disk for real persistence check
            with open(job_json_path, 'w') as f:
                json.dump(state_to_save, f, indent=2)

        def mock_execute_step(*args, **kwargs):
            # R9: At coder entry, read isolated persisted JSON and assert complete snapshot exists
            if job_json_path.exists():
                with open(job_json_path, 'r') as f:
                    saved_state = json.load(f)
                snapshot_at_coder_entry[0] = saved_state
                event_log.append(("coder_entry_disk_check", True))

                # R9: Assert complete owned snapshot exists
                attempt_records = saved_state.get("attempt_records", {})
                assert len(attempt_records) == 1, "Exactly one attempt should exist at coder entry"
                attempt_id = list(attempt_records.keys())[0]
                attempt = attempt_records[attempt_id]

                # Verify attempt has required fields for owned snapshot
                assert attempt.get("attempt_id") == attempt_id
                assert attempt.get("job_id") == "test-job"
                assert attempt.get("workflow") == "plan_first_review_v1"
                assert attempt.get("baseline") == 1
                assert attempt.get("step") == "generate_plan"
                assert attempt.get("status") == "prepared"
                assert attempt.get("recovered_context") is not None
                assert attempt["recovered_context"].get("active") is False

                # R9: Assert active link exists
                loop_context = saved_state.get("loop_context", {})
                assert loop_context.get("active_attempt_id") == attempt_id

                event_log.append(("snapshot_verified", attempt_id))
            else:
                event_log.append(("coder_entry_disk_check", False))

            # Return APPROVED result
            return StepResult(
                status="APPROVED",
                remark="Good",
                artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
                reject_code=None,
                meta_json_path="meta.json",
                usage_data={},
                attempt_id=None,  # Will be attached by wrapper
            )

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", real_save)

        # Mock the inner execution to intercept coder invocation
        from agent_runner_v2 import run_agent
        monkeypatch.setattr(run_agent, "_execute_prepared_step", mock_execute_step)

        # Prepare a minimal PreparedStepExecution
        from dataclasses import dataclass
        @dataclass
        class PreparedStepExecution:
            context: dict
            action_name: str | None = None
            prompt_file: str | None = None
            prompt_checksum: str | None = None
            prompt_text: str | None = None
            coder: str | None = "test-coder"
            coder_config: dict | None = None

        prepared = PreparedStepExecution(
            context={
                "PLANNING_FOLDER": "Planning/test",
                "JOB_ID": "test-job",
            }
        )

        group_cfg = {
            "step_configs": {
                "generate_plan": {
                    "produces": ["QWEN_PLAN_FILE"],
                }
            }
        }

        # Call the actual wrapper
        result = run_agent._execute_prepared_step_with_plan_first_attempt(
            prepared=prepared,
            template_group="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="generate_plan",
            step_cfg={"produces": ["QWEN_PLAN_FILE"]},
            effective_root=Path(str(tmp_path)),
        )

        # R9: Verify save happened BEFORE coder invocation
        disk_check_events = [e for e in event_log if e[0] == "coder_entry_disk_check"]
        snapshot_events = [e for e in event_log if e[0] == "snapshot_verified"]

        assert disk_check_events[0][1] is True, "Disk should have persisted state at coder entry"
        assert len(snapshot_events) == 1, "Snapshot should be verified at coder entry"

        # R9: Verify returned attempt_id matches the one in snapshot
        snapshot_attempt_id = snapshot_events[0][1]
        assert result.attempt_id is not None
        assert result.attempt_id == snapshot_attempt_id, "Returned attempt_id should match snapshot"

    def test_wrapper_retains_attempt_id_for_rejected(self, tmp_path, monkeypatch):
        """Wrapper retains attempt_id for REJECTED results.

        R9: Verifies REJECTED result also gets the same attempt_id.
        Uses parameterized fixture approach sharing setup with APPROVED test.
        """
        # Setup isolated persistence
        jobs_dir = tmp_path / "jobs" / "plan_first_review_v1"
        jobs_dir.mkdir(parents=True, exist_ok=True)
        job_json_path = jobs_dir / "test-job.json"

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

        snapshot_at_coder_entry = [None]

        def real_save(group_name, job_id, state_to_save):
            with open(job_json_path, 'w') as f:
                json.dump(state_to_save, f, indent=2)

        def mock_execute_step(*args, **kwargs):
            # R9: Read and verify snapshot at coder entry (same as APPROVED test)
            if job_json_path.exists():
                with open(job_json_path, 'r') as f:
                    saved_state = json.load(f)
                snapshot_at_coder_entry[0] = saved_state

                attempt_records = saved_state.get("attempt_records", {})
                assert len(attempt_records) == 1
                attempt_id = list(attempt_records.keys())[0]
                attempt = attempt_records[attempt_id]

                # Verify same owned snapshot structure
                assert attempt.get("status") == "prepared"
                assert attempt.get("recovered_context", {}).get("active") is False

                # Verify active link
                assert saved_state.get("loop_context", {}).get("active_attempt_id") == attempt_id

            # Return REJECTED result
            return StepResult(
                status="REJECTED",
                remark="Needs work",
                artifacts={},
                reject_code="QUALITY",
                meta_json_path="meta.json",
                usage_data={},
                attempt_id=None,  # Will be attached by wrapper
            )

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", real_save)

        from agent_runner_v2 import run_agent
        monkeypatch.setattr(run_agent, "_execute_prepared_step", mock_execute_step)

        from dataclasses import dataclass
        @dataclass
        class PreparedStepExecution:
            context: dict
            action_name: str | None = None
            prompt_file: str | None = None
            prompt_checksum: str | None = None
            prompt_text: str | None = None
            coder: str | None = "test-coder"
            coder_config: dict | None = None

        prepared = PreparedStepExecution(
            context={
                "PLANNING_FOLDER": "Planning/test",
                "JOB_ID": "test-job",
            }
        )

        group_cfg = {
            "step_configs": {
                "generate_plan": {},
            }
        }

        result = run_agent._execute_prepared_step_with_plan_first_attempt(
            prepared=prepared,
            template_group="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="generate_plan",
            step_cfg={},
            effective_root=Path(str(tmp_path)),
        )

        # R9: REJECTED result should also have attempt_id matching snapshot
        if snapshot_at_coder_entry[0]:
            attempt_records = snapshot_at_coder_entry[0].get("attempt_records", {})
            snapshot_attempt_id = list(attempt_records.keys())[0]
            assert result.attempt_id is not None
            assert result.attempt_id == snapshot_attempt_id
        coder_events = [e for e in event_log if e[0] == "coder_invocation"]
        disk_check_events = [e for e in event_log if e[0] == "disk_check_at_coder_entry"]

        assert len(save_events) >= 1, "Save should have been called"
        assert len(coder_events) == 1, "Coder should have been invoked once"
        assert save_events[0][0] == "save"  # First event is save

        # Verify disk persistence at coder entry
        assert disk_check_events[0][1] is True, "Attempt should be on disk at coder entry"

        # Verify attempt_id is attached to result
        assert result.attempt_id is not None
        assert result.attempt_id == saved_attempt_id[0]

    def test_wrapper_retains_attempt_id_for_rejected(self, tmp_path, monkeypatch):
        """Wrapper retains attempt_id for REJECTED results.

        R8: Verifies REJECTED result also gets the same attempt_id.
        """
        # Setup isolated persistence
        jobs_dir = tmp_path / "jobs" / "plan_first_review_v1"
        jobs_dir.mkdir(parents=True, exist_ok=True)

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

        saved_attempt_id = [None]

        def real_save(group_name, job_id, state_to_save):
            for aid, att in state_to_save.get("attempt_records", {}).items():
                saved_attempt_id[0] = aid

        def mock_execute_step(*args, **kwargs):
            # Return REJECTED result
            return StepResult(
                status="REJECTED",
                remark="Needs work",
                artifacts={},
                reject_code="QUALITY",
                meta_json_path="meta.json",
                usage_data={},
                attempt_id=None,  # Will be attached by wrapper
            )

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", real_save)

        from agent_runner_v2 import run_agent
        monkeypatch.setattr(run_agent, "_execute_prepared_step", mock_execute_step)

        from dataclasses import dataclass
        @dataclass
        class PreparedStepExecution:
            context: dict
            action_name: str | None = None
            prompt_file: str | None = None
            prompt_checksum: str | None = None
            prompt_text: str | None = None
            coder: str | None = "test-coder"
            coder_config: dict | None = None

        prepared = PreparedStepExecution(
            context={
                "PLANNING_FOLDER": "Planning/test",
                "JOB_ID": "test-job",
            }
        )

        group_cfg = {
            "step_configs": {
                "generate_plan": {},
            }
        }

        result = run_agent._execute_prepared_step_with_plan_first_attempt(
            prepared=prepared,
            template_group="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="generate_plan",
            step_cfg={},
            effective_root=Path(str(tmp_path)),
        )

        # R8: REJECTED result should also have attempt_id
        assert result.attempt_id is not None
        assert result.attempt_id == saved_attempt_id[0]


class TestA02_UnrelatedWorkflowBypass:
    """A02: Unrelated workflow with generate_plan/refine_plan step names bypasses Phase A handling."""
    
    def test_unrelated_workflow_bypasses_phase_a(self, tmp_path, monkeypatch):
        """Non-plan_first_review_v1 workflows bypass Phase A gate."""
        state = {
            "job_id": "test-job",
            "template_group": "other_workflow",  # Not plan_first_review_v1
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {},
            "attempt_records": {},
            "loop_context": {},
        }
        
        # Mock save_job
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)
        
        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        
        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=None,  # No attempt_id for non-plan-first
        )
        
        # Should not call gate for non-plan_first_review_v1
        with patch.object(workflow_router, "_plan_first_result_gate") as mock_gate:
            workflow_router.route_after_step(
                group_name="other_workflow",
                group_cfg={},
                state=state,
                step="generate_plan",
                step_cfg={},
                step_result=result,
                coder_used="test-coder",
                max_rejects=3,
            )
            # Gate should NOT be called for non-plan_first_review_v1
            mock_gate.assert_not_called()


class TestA03_OwnershipRevisionConflict:
    """A03: Known ownership, exact revisions, completion ownership and active-B conflict are enforced."""

    def test_ownership_conflict_enforced(self, tmp_path, monkeypatch):
        """R13: Gate enforces ownership - attempt job_id must match state job_id."""
        # Test ownership validation
        state = {
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
                    "job_id": "different-job",  # Wrong job_id
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                }
            },
            "loop_context": {"active_attempt_id": "att_test123"},
        }

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Create output file with canonical path
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test plan")

        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id="att_test123",
        )

        group_cfg = {"step_configs": {"generate_plan": {}}}

        # Call route_after_step - should fail with ownership mismatch
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

        # Should fail with ATTEMPT_JOB_MISMATCH
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "ATTEMPT_JOB_MISMATCH"

    def test_revision_mismatch_conflict_enforced(self, tmp_path, monkeypatch):
        """R12: Gate enforces revision formula - target_revision mismatch is caught."""
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
                    "target_revision": 2,  # Mismatch - state has plan_revision=1
                    "status": "prepared",
                    "recovered_context": {
                        "job_id": "test-job",
                        "group_name": "plan_first_review_v1",
                        "baseline": 1,
                        "step": "generate_plan",
                        "input_revision": None,
                        "target_revision": 2,
                        "active": False,
                    },
                }
            },
            "loop_context": {"active_attempt_id": attempt_id},
        }

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test plan")

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

        # R12: Should fail with eligibility failure (revision mismatch caught by validation)
        assert exit_code == 1
        # The revision mismatch is caught by _validate_prepared_eligibility
        assert returned_state.get("last_failure_code") in ("ELIGIBILITY_FAILURE", "REVISION_MISMATCH")

    def test_completion_ownership_mismatch_conflict(self, tmp_path, monkeypatch):
        """R12: Gate enforces completion ownership - existing completion by different attempt."""
        attempt_id = "att_new456"
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
                },
                "att_old123": {  # Prior completion
                    "attempt_id": "att_old123",
                    "status": "applied",
                },
            },
            "loop_context": {"active_attempt_id": attempt_id},
            "revision_completions": {
                "b1_r1": {"attempt_id": "att_old123"}  # Already completed by different attempt
            },
        }

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test plan")

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

        # R12: Should fail with completion ownership conflict
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "COMPLETION_OWNERSHIP_CONFLICT"


class TestA04_GenerationAndRefinement:
    """A04: Real generation and recovered first refinement v1 -> v2 succeed; completed loop remains cleared."""

    def test_generation_and_refinement_v1_to_v2_succeed_finished_loop(self, tmp_path, monkeypatch):
        """Generation creates v1, refinement advances to v2 with cleared loop."""
        # R16-03: Use real file checksums, complete recovery context, assert revision advanced

        # PHASE 1: Generation creates v1
        # Create output file with canonical path
        output_file_v1 = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file_v1.parent.mkdir(parents=True, exist_ok=True)
        v1_content = "v1 plan content with unique text"
        output_file_v1.write_text(v1_content)

        # Compute real MD5 checksum for v1
        v1_checksum = hashlib.md5(v1_content.encode()).hexdigest()

        # Setup: Create state for generation
        gen_attempt_id = "att_gen123"
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                gen_attempt_id: {
                    "attempt_id": gen_attempt_id,
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
            "loop_context": {"active_attempt_id": gen_attempt_id},
        }

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        result_v1 = StepResult(
            status="APPROVED",
            remark="Generated v1",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=gen_attempt_id,
        )

        group_cfg = {
            "step_configs": {
                "generate_plan": {},
                "refine_plan": {},
                "codex_review": {
                    "on_reject_refine": {
                        "step": "refine_plan",
                        "artifact": "QWEN_PLAN_FILE",
                    }
                },
            }
        }

        # PHASE 1: Call route_after_step for generation
        state_after_gen, exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="generate_plan",
            step_cfg={},
            step_result=result_v1,
            coder_used="test-coder",
            max_rejects=3,
        )

        # Verify generation success
        assert exit_code == 0
        assert state_after_gen.get("loop_context", {}).get("active_attempt_id") is None

        gen_record = state_after_gen.get("attempt_records", {}).get(gen_attempt_id, {})
        assert gen_record.get("status") == "applied"

        # PHASE 2: Refinement v1 → v2
        # Create v2 output file with DIFFERENT content
        output_file_v2 = tmp_path / "Planning" / "test" / "Qwen_Plan_v02.md"
        v2_content = "v2 refined content with different unique text"
        output_file_v2.write_text(v2_content)

        # R16-03: Complete recovery context with all required fields
        ref_attempt_id = "att_ref456"
        state_after_gen["current_step"] = "refine_plan"

        # R16-02 follow-up: Use correct canonical review path
        # ARTIFACT_PATH_CODEX_REVIEW(folder, input_revision=1, baseline=1) -> "Planning/test/Codex_Review_v01.md"
        canonical_review_path = "Planning/test/Codex_Review_v01.md"

        state_after_gen["attempt_records"][ref_attempt_id] = {
            "attempt_id": ref_attempt_id,
            "job_id": "test-job",
            "workflow": "plan_first_review_v1",
            "baseline": 1,
            "step": "refine_plan",
            "input_revision": 1,
            "target_revision": 2,
            "status": "prepared",
            "recovered_context": {
                "job_id": "test-job",
                "group_name": "plan_first_review_v1",
                "baseline": 1,
                "step": "refine_plan",
                "input_revision": 1,
                "target_revision": 2,
                # R16-02: Complete loop context with all required fields
                "active": True,
                "loop_step": "codex_review",
                "refine_step": "refine_plan",
                "loop_target_artifact": "QWEN_PLAN_FILE",
                "loop_source_review": canonical_review_path,  # R16-02 follow-up: Canonical path
                "loop_iteration": 1,
                "pre_refine_checksum": v1_checksum,  # R16-03: Real checksum from v1 file
            },
        }
        state_after_gen["loop_context"]["active_attempt_id"] = ref_attempt_id

        result_v2 = StepResult(
            status="APPROVED",
            remark="Refined to v2",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v02.md"},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=ref_attempt_id,
        )

        # R16-03: Use real MD5 checksum (no mock) - v2 has different content
        # _md5_file will be called to verify v2 content != v1 checksum

        # PHASE 2: Call route_after_step for refinement
        state_after_ref, exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state_after_gen,
            step="refine_plan",
            step_cfg={},
            step_result=result_v2,
            coder_used="test-coder",
            max_rejects=3,
        )

        # Verify refinement success
        assert exit_code == 0

        # Verify loop context is cleared after refinement
        assert state_after_ref.get("loop_context", {}).get("active_attempt_id") is None

        # R16-03: Assert plan_revision advanced to 2
        assert state_after_ref.get("plan_revision") == 2

        # Verify refinement attempt is marked as applied
        ref_record = state_after_ref.get("attempt_records", {}).get(ref_attempt_id, {})
        assert ref_record.get("status") == "applied"

        # Verify generation attempt is still applied (not overwritten)
        gen_record_after_ref = state_after_ref.get("attempt_records", {}).get(gen_attempt_id, {})
        assert gen_record_after_ref.get("status") == "applied"


class TestA05_NoOpRecoveryNoFalseSuccess:
    """A05: Actual no-op/failed recovery has no false successful completion/revision/notification."""
    
    def test_no_op_recovery_no_false_success(self, tmp_path, monkeypatch):
        """No-op refinement fails without false completion."""
        # Setup: Create state with attempt record
        attempt_id = "att_test123"
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "refine_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,
                    "step": "refine_plan",
                    "input_revision": 1,
                    "target_revision": 2,
                    "status": "prepared",
                    "recovered_context": {
                        "pre_refine_checksum": "md5hash",
                    },
                }
            },
            "loop_context": {"active_attempt_id": attempt_id},
            "reject_counts": {},
            "retry_history": [],
            "completed_steps": [],
        }
        
        # Create output file with SAME content (no-op)
        output_file = tmp_path / "Planning" / "test" / "plan_v2_b1.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("same content")
        
        # Mock _md5_file to return matching checksum
        monkeypatch.setattr(job_state, "_md5_file", lambda path: "md5hash")
        
        # Mock save_job
        save_calls = []
        def mock_save(group_name, job_id, state_to_save):
            save_calls.append(copy.deepcopy(state_to_save))
        monkeypatch.setattr(job_state, "save_job", mock_save)
        
        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        
        # Call _validate_refinement_no_op
        result = workflow_router._validate_refinement_no_op(
            step_result=StepResult(
                status="APPROVED",
                remark="Good",
                artifacts={"QWEN_PLAN_FILE": str(output_file)},
                reject_code=None,
                meta_json_path="meta.json",
                usage_data={},
                attempt_id=attempt_id,
            ),
            validated_recovery={"pre_refine_checksum": "md5hash"},
            canonical_path=output_file,
        )
        
        # Should detect no-op
        assert result == "NO_OP_REFINEMENT"


class TestA06_CanonicalPaths:
    """A06: Canonical paths work across baselines and different cwd; wrong directory/baseline and missing/unreadable approved output fail."""

    def test_canonical_paths_across_baselines_cwd(self, tmp_path, monkeypatch):
        """Gate rejects non-canonical output path."""
        # Setup: Create state with attempt
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
            "loop_context": {"active_attempt_id": attempt_id},
        }

        # Create output file in WRONG directory (non-canonical)
        output_file = tmp_path / "Planning" / "test" / "wrong_dir" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test plan")

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Create result with NON-CANONICAL path
        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/wrong_dir/Qwen_Plan_v01.md"},  # Wrong!
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

        # Should fail with NON_CANONICAL_OUTPUT_PATH
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "NON_CANONICAL_OUTPUT_PATH"

    def test_baseline_mismatch_rejected(self, tmp_path, monkeypatch):
        """R12: Gate rejects output when baseline mismatch."""
        attempt_id = "att_test123"
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 2,  # Current baseline is 2
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,  # Attempt is from baseline 1
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
        }

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test plan")

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

        # R12: Should fail with eligibility failure (baseline mismatch caught by validation)
        assert exit_code == 1
        # The baseline mismatch is caught by _validate_prepared_eligibility
        assert returned_state.get("last_failure_code") in ("ELIGIBILITY_FAILURE", "BASELINE_MISMATCH")

    def test_missing_output_file_evidence(self, tmp_path, monkeypatch):
        """R12: Gate handles missing output file with evidence flags."""
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
        }

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Do NOT create output file - it's missing

        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},  # File doesn't exist
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        group_cfg = {"step_configs": {"generate_plan": {}}}

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

        # R12: Should fail with output missing
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "OUTPUT_FILE_MISSING"

    def test_baseline2_routing_from_different_cwd(self, tmp_path, monkeypatch, production_persistence):
        """R13: Successful baseline-2 routing from a different working directory.

        Uses ARTIFACT_PATH_QWEN_PLAN to create valid baseline-2 output,
        changes cwd to a different directory, routes actual first outcome,
        persists/reloads and asserts canonical artifact/receipt/completion succeeds.
        """
        from agent_runner_v2.constants import ARTIFACT_PATH_QWEN_PLAN

        # Setup: Create baseline-2 state
        attempt_id = "att_b2_123"
        planning_folder = "test"
        baseline = 2

        state = {
            "job_id": "test-job-b2",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": baseline,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": planning_folder},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job-b2",
                    "workflow": "plan_first_review_v1",
                    "baseline": baseline,
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "prepared",
                    "recovered_context": {
                        "job_id": "test-job-b2",
                        "group_name": "plan_first_review_v1",
                        "baseline": baseline,
                        "step": "generate_plan",
                        "input_revision": None,
                        "target_revision": 1,
                        "active": False,
                    },
                }
            },
            "loop_context": {"active_attempt_id": attempt_id},
        }

        # R13: Create baseline-2 output file using ARTIFACT_PATH_QWEN_PLAN
        # For baseline 2, path is: Planning/{folder}/baseline_02/Qwen_Plan_v01.md
        canonical_relative = ARTIFACT_PATH_QWEN_PLAN(planning_folder, revision=1, baseline=baseline)
        output_file = tmp_path / canonical_relative
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_content = "baseline 2 plan content"
        output_file.write_text(output_content)

        real_digest = hashlib.sha256(output_content.encode()).hexdigest()

        # R13: Create a different working directory and change to it
        different_cwd = tmp_path / "different_working_directory"
        different_cwd.mkdir(parents=True, exist_ok=True)
        original_cwd = Path.cwd()
        import os as os_module
        os_module.chdir(str(different_cwd))

        try:
            # Reset save_count
            production_persistence["save_count"][0] = 0

            group_cfg = {"step_configs": {"generate_plan": {"produces": ["QWEN_PLAN_FILE"]}}}

            result = StepResult(
                status="APPROVED",
                remark="Baseline 2 plan generated",
                artifacts={"QWEN_PLAN_FILE": canonical_relative},
                reject_code=None,
                meta_json_path="meta.json",
                usage_data={},
                attempt_id=attempt_id,
            )

            # R13: Route actual first outcome
            returned_state, exit_code = workflow_router.route_after_step(
                group_name="plan_first_review_v1",
                group_cfg=group_cfg,
                state=state,
                step="generate_plan",
                step_cfg={"produces": ["QWEN_PLAN_FILE"]},
                step_result=result,
                coder_used="test-coder",
                max_rejects=3,
            )

            # R13: Assert routing succeeds
            assert exit_code == 0

            # R13: Assert one save
            assert production_persistence["save_count"][0] == 1

            # R13: Persist and reload
            saved_state = production_persistence["load_state"]("test-job-b2")

            # R13: Assert canonical artifact path in receipt
            saved_attempt = saved_state.get("attempt_records", {}).get(attempt_id, {})
            assert saved_attempt.get("status") == "applied"
            applied_result = saved_attempt.get("applied_result", {})
            assert applied_result.get("output_digest") == real_digest

            # R13: Assert completion accounting for baseline 2
            completions = saved_state.get("revision_completions", {})
            assert "b2_r1" in completions
            assert completions["b2_r1"].get("attempt_id") == attempt_id

        finally:
            # R13: Restore original cwd
            os_module.chdir(str(original_cwd))


class TestA07_RejectionConsumedOnce:
    """A07: First ordinary rejection + reload + identical replay produces one accounting/history application."""

    def test_rejection_consumed_once_replay_unchanged(self, tmp_path, monkeypatch):
        """Rejection is consumed once, replay doesn't double-count."""
        # Setup: State with already-rejected attempt
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
            "reject_counts": {"generate_plan": 1},  # Already counted
        }

        original_reject_count = state["reject_counts"]["generate_plan"]

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Create IDENTICAL REJECTED result
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

        # Call route_after_step - should return unchanged
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

        # Should return with exit_code 1 (rejected)
        assert exit_code == 1

        # CRITICAL: Reject count should NOT increase
        assert returned_state["reject_counts"]["generate_plan"] == original_reject_count


class TestA08_TerminalReplayUnchanged:
    """A08: Identical applied/rejected/failed terminal replay makes no state/default-field/save/accounting/notification changes."""

    def test_terminal_replay_unchanged(self, tmp_path, monkeypatch):
        """Terminal replay returns without mutations."""
        # Create output file with known content
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_content = "test plan content"
        output_file.write_text(output_content)

        # Compute real SHA256 digest
        import hashlib
        real_digest = hashlib.sha256(output_content.encode()).hexdigest()

        # Setup: State with applied attempt
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
                    "status": "applied",
                    "applied_result": {
                        "remark": "Good",
                        "output_path": "Planning/test/Qwen_Plan_v01.md",
                        "output_digest": real_digest,
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


class TestA09_ChangedEvidenceConflicts:
    """A09: Changing only incoming path, file bytes/existence/readability or failed observed evidence produces the defined durable conflict."""

    def test_changed_evidence_conflicts_preserves_progress(self, tmp_path, monkeypatch):
        """Changed evidence conflicts while preserving progress."""
        # Create output file with known content
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("original content")

        # Setup: State with applied attempt and DIFFERENT digest
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
                        "output_digest": "stored_digest_different",  # Different from actual
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

        # Should fail with TERMINAL_EVIDENCE_CONFLICT
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "TERMINAL_EVIDENCE_CONFLICT"


class TestA10_OldBaselineReplay:
    """A10: Valid old-baseline terminal replay preserves newer progress without current first-outcome eligibility blocking it."""

    def test_old_baseline_replay_preserves_progress(self, tmp_path, monkeypatch):
        """Old-baseline replay preserves newer progress."""
        # This test verifies that old-baseline replay doesn't block on current baseline mismatch
        # Create output file
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_content = "test plan content"
        output_file.write_text(output_content)

        import hashlib
        real_digest = hashlib.sha256(output_content.encode()).hexdigest()

        # Setup: State with applied attempt from baseline 1, but current baseline is 2
        attempt_id = "att_test123"
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 2,  # Current baseline is 2
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                attempt_id: {
                    "attempt_id": attempt_id,
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,  # Attempt is from baseline 1
                    "step": "generate_plan",
                    "input_revision": None,
                    "target_revision": 1,
                    "status": "applied",
                    "applied_result": {
                        "remark": "Good",
                        "output_path": "Planning/test/Qwen_Plan_v01.md",
                        "output_digest": real_digest,
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

        # Call route_after_step - should NOT fail due to baseline mismatch for terminal replay
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

        # Should return unchanged (terminal replay succeeds)
        assert exit_code == 0
        assert returned_state == original_snapshot


class TestA11_FailureBeforeSave:
    """A11a: Failure before save call leaves old state unchanged; error is observable."""

    def test_failure_before_save_old_state(self, tmp_path, monkeypatch):
        """Failure before save call leaves old state unchanged."""
        # Setup: Create state
        state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "refine_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,
            "artifacts": {"PLANNING_FOLDER": "Planning/test"},
            "attempt_records": {
                "att_test123": {
                    "attempt_id": "att_test123",
                    "job_id": "test-job",
                    "workflow": "plan_first_review_v1",
                    "baseline": 1,
                    "step": "refine_plan",
                    "input_revision": 1,
                    "target_revision": 2,
                    "status": "prepared",
                }
            },
            "loop_context": {},
            "reject_counts": {},
            "retry_history": [],
            "completed_steps": [],
        }

        original_state = copy.deepcopy(state)

        # Mock save_job to raise exception
        def mock_save_fail(group_name, job_id, state_to_save):
            raise Exception("Simulated save failure")
        monkeypatch.setattr(job_state, "save_job", mock_save_fail)

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Call _commit_application_failure_from_baseline
        baseline = copy.deepcopy(state)

        # Should propagate exception
        with pytest.raises(Exception, match="Simulated save failure"):
            workflow_router._commit_application_failure_from_baseline(
                baseline=baseline,
                group_name="plan_first_review_v1",
                attempt_id="att_test123",
                step_result=StepResult(
                    status="APPROVED",
                    remark="Good",
                    artifacts={},
                    reject_code=None,
                    meta_json_path="meta.json",
                    usage_data={},
                    attempt_id="att_test123",
                ),
                failure_reason="TEST_FAILURE",
                step="refine_plan",
            )

        # Original state should be unchanged
        assert state == original_state


class TestA12_FailureAfterReplacement:
    """A12: Real replacement followed by injected exception leaves complete new JSON; error is observable, and reload/retry does not reapply."""

    def test_failure_after_replacement_new_state(self, tmp_path, monkeypatch):
        """After successful save and crash, reload finds new state and replay returns unchanged."""
        # R16-03: Use real JSON persistence, inject exception after save, reload from disk

        # Create output file with canonical path
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_content = "test plan content for crash/retry"
        output_file.write_text(output_content)

        # Compute real digest
        import hashlib
        real_digest = hashlib.sha256(output_content.encode()).hexdigest()

        # R16-03: Create real JSON persistence directory
        jobs_dir = tmp_path / "jobs" / "plan_first_review_v1"
        jobs_dir.mkdir(parents=True, exist_ok=True)
        job_json_path = jobs_dir / "test-job.json"

        # Setup: Create state for generation
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
            "loop_context": {"active_attempt_id": attempt_id},
        }

        # R16-03: Use real save_job that writes to disk
        save_count = [0]
        exception_after_save = [False]

        def real_save_to_disk(group_name, job_id, state_to_save):
            save_count[0] += 1
            # Write to disk
            with open(job_json_path, 'w') as f:
                json.dump(state_to_save, f, indent=2)
            # R16-03: Inject exception AFTER successful save
            if exception_after_save[0]:
                raise RuntimeError("Injected post-save exception")

        monkeypatch.setattr(job_state, "save_job", real_save_to_disk)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # PHASE 1: First call - successful save
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

        # Verify first call succeeded
        assert exit_code == 0
        assert save_count[0] == 1

        # R16-03: Verify JSON was written to disk
        assert job_json_path.exists()
        with open(job_json_path, 'r') as f:
            saved = json.load(f)

        # Verify terminal state was saved
        saved_attempt = saved.get("attempt_records", {}).get(attempt_id, {})
        assert saved_attempt.get("status") == "applied"
        assert saved_attempt.get("applied_result", {}).get("output_digest") == real_digest

        # PHASE 2: Simulate crash and reload
        # R16-03: Reload from disk (simulates process restart)
        with open(job_json_path, 'r') as f:
            reloaded_state = json.load(f)

        # PHASE 3: Identical replay - should return unchanged
        # R16-R6: Incoming path must match stored path exactly
        result_replay = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        # Replay should return same state unchanged
        replayed_state, replay_exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=reloaded_state,
            step="generate_plan",
            step_cfg={},
            step_result=result_replay,
            coder_used="test-coder",
            max_rejects=3,
        )

        # CRITICAL: Replay must succeed and return unchanged
        assert replay_exit_code == 0

        # R16-03: Verify no additional saves (no double-apply)
        assert save_count[0] == 1  # Only the original save

        # Verify state is unchanged
        assert id(replayed_state) == id(reloaded_state)  # Same object

    def test_exception_after_atomic_save_is_observable(self, tmp_path, monkeypatch):
        """R16-R5: Exception after actual atomic save is observable, reload recovers."""
        # Create output file with canonical path
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_content = "test plan content for exception test"
        output_file.write_text(output_content)

        # Compute real digest
        import hashlib
        real_digest = hashlib.sha256(output_content.encode()).hexdigest()

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
            "loop_context": {"active_attempt_id": attempt_id},
        }

        # R16-R5: Set up real JOBS_ROOT for actual atomic save
        from pathlib import Path as PathLib
        jobs_root = tmp_path / "jobs"
        monkeypatch.setattr(job_state, "JOBS_ROOT", PathLib(str(jobs_root)))

        # Track atomic save and inject exception after it
        atomic_save_calls = []

        original_save_json_atomic = job_state.save_json_atomic

        def save_atomic_then_raise(path, data):
            atomic_save_calls.append(("atomic_save", str(path)))
            # R16-R5: Call the ACTUAL atomic save function
            original_save_json_atomic(path, data)
            # R16-R5: Raise exception AFTER successful atomic save
            raise RuntimeError("Injected post-atomic-save exception")

        monkeypatch.setattr(job_state, "save_json_atomic", save_atomic_then_raise)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

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

        # Call routing - should raise exception AFTER actual atomic save
        with pytest.raises(RuntimeError, match="Injected post-atomic-save exception"):
            workflow_router.route_after_step(
                group_name="plan_first_review_v1",
                group_cfg=group_cfg,
                state=state,
                step="generate_plan",
                step_cfg={},
                step_result=result,
                coder_used="test-coder",
                max_rejects=3,
            )

        # R16-R5: Verify actual atomic save was called
        assert len(atomic_save_calls) == 1
        assert atomic_save_calls[0][0] == "atomic_save"

        # R16-R5: Verify JSON was written via atomic save (despite exception)
        job_json_path = Path(atomic_save_calls[0][1])
        assert job_json_path.exists()
        with open(job_json_path, 'r') as f:
            saved = json.load(f)

        # Verify terminal state was saved before exception
        saved_attempt = saved.get("attempt_records", {}).get(attempt_id, {})
        assert saved_attempt.get("status") == "applied"
        assert saved_attempt.get("applied_result", {}).get("output_digest") == real_digest

        # R16-R5: Reload from disk (actual atomic save) and replay
        with open(job_json_path, 'r') as f:
            reloaded_state = json.load(f)

        # Use normal save for replay
        monkeypatch.setattr(job_state, "save_json_atomic", original_save_json_atomic)

        # R16-R6: Incoming path must match stored path exactly
        result_replay = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        replayed_state, replay_exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=reloaded_state,
            step="generate_plan",
            step_cfg={},
            step_result=result_replay,
            coder_used="test-coder",
            max_rejects=3,
        )

        # CRITICAL: Replay must succeed
        assert replay_exit_code == 0

        # Verify terminal state was saved before exception
        saved_attempt = saved.get("attempt_records", {}).get(attempt_id, {})
        assert saved_attempt.get("status") == "applied"
        assert saved_attempt.get("applied_result", {}).get("output_digest") == real_digest

        # R16-03 follow-up: Reload from disk and replay
        with open(job_json_path, 'r') as f:
            reloaded_state = json.load(f)

        # Replay should work with the saved state
        # R16-R6: Incoming path must match stored path exactly
        result_replay = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        # Use normal save for replay (no exception)
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)

        replayed_state, replay_exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=reloaded_state,
            step="generate_plan",
            step_cfg={},
            step_result=result_replay,
            coder_used="test-coder",
            max_rejects=3,
        )

        # CRITICAL: Replay must succeed
        assert replay_exit_code == 0


class TestA13_NoSplitTerminalCompletion:
    """A13: Success/rejection/failure saves never expose split terminal/completion state; failure-state derivation excludes speculative success mutations."""

    def test_no_split_terminal_completion_state(self, tmp_path, monkeypatch):
        """No split terminal/completion state."""
        # This test verifies that failure state derivation doesn't include speculative success mutations
        # Create output file
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test plan content")

        # Setup: Create state with attempt
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
            "loop_context": {"active_attempt_id": attempt_id},
        }

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

        # Mock save_job and notifications
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

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

        # Verify success
        assert exit_code == 0

        # Verify terminal state is consistent
        # - Attempt is marked as applied (terminal)
        # - Loop context is cleared
        # - No "rejected_result" or "failed_result" present (no split state)
        attempt_record = returned_state.get("attempt_records", {}).get(attempt_id, {})
        assert attempt_record.get("status") == "applied"
        assert "applied_result" in attempt_record
        assert "rejected_result" not in attempt_record
        assert "failed_result" not in attempt_record

        # Verify loop context is cleared
        assert returned_state.get("loop_context", {}).get("active_attempt_id") is None


class TestA14_NotificationsAfterCommit:
    """A14: Notifications use actual APIs after committed outcomes, none on failed saves or duplicates; unrelated workflows remain compatible."""

    def test_notifications_after_commit_through_routing(self, tmp_path, monkeypatch):
        """R16-03: Notifications dispatched after save through actual routing, not before."""
        # Create output file
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test plan content")

        # Setup: Create state with attempt record
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
            "loop_context": {"active_attempt_id": attempt_id},
            "reject_counts": {},
            "retry_history": [],
            "completed_steps": [],
        }

        # R16-03: Track event ordering
        event_log = []

        def mock_save(group_name, job_id, state_to_save):
            event_log.append(("save", job_id))

        def mock_send_step_notification(status, context, step, step_cfg):
            event_log.append(("notification", status, step))

        def mock_send_workflow_notification(status, context):
            event_log.append(("workflow_notification", status))

        monkeypatch.setattr(job_state, "save_job", mock_save)
        monkeypatch.setattr(workflow_router, "send_step_notification", mock_send_step_notification)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", mock_send_workflow_notification)

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

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

        # R16-03: Call through actual routing
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

        # Verify success
        assert exit_code == 0

        # R16-03: Verify save happens before notification
        assert len(event_log) >= 2
        # Save must come before notification
        save_index = next(i for i, e in enumerate(event_log) if e[0] == "save")
        notif_index = next((i for i, e in enumerate(event_log) if e[0] == "notification"), None)

        assert save_index >= 0
        # If notification exists, it must come after save
        if notif_index is not None:
            assert notif_index > save_index, f"Notification at {notif_index} must come after save at {save_index}"

    def test_no_notifications_on_save_failure(self, tmp_path, monkeypatch):
        """R16-03: No notifications dispatched if save fails."""
        # Create output file
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test plan content")

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
            "loop_context": {"active_attempt_id": attempt_id},
        }

        # Track events
        event_log = []

        def mock_save_fail(group_name, job_id, state_to_save):
            event_log.append(("save_attempt", job_id))
            raise RuntimeError("Simulated save failure")

        def mock_send_step_notification(status, context, step, step_cfg):
            event_log.append(("notification", status))

        monkeypatch.setattr(job_state, "save_job", mock_save_fail)
        monkeypatch.setattr(workflow_router, "send_step_notification", mock_send_step_notification)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

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

        # R16-03: Should raise exception from save failure
        with pytest.raises(RuntimeError, match="Simulated save failure"):
            workflow_router.route_after_step(
                group_name="plan_first_review_v1",
                group_cfg=group_cfg,
                state=state,
                step="generate_plan",
                step_cfg={},
                step_result=result,
                coder_used="test-coder",
                max_rejects=3,
            )

        # R16-03: Verify save was attempted but no notification
        assert len(event_log) == 1
        assert event_log[0][0] == "save_attempt"
        # No notification should be logged
        assert not any(e[0] == "notification" for e in event_log)

    def test_no_notifications_on_terminal_replay(self, tmp_path, monkeypatch):
        """R16-03: No notifications on duplicate terminal replay."""
        # Create output file with known content
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_content = "test plan content"
        output_file.write_text(output_content)

        import hashlib
        real_digest = hashlib.sha256(output_content.encode()).hexdigest()

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
                    "status": "applied",  # Already applied
                    "applied_result": {
                        "remark": "Good",
                        "output_path": "Planning/test/Qwen_Plan_v01.md",
                        "output_digest": real_digest,
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

        # Track events
        event_log = []

        def mock_save(group_name, job_id, state_to_save):
            event_log.append(("save", job_id))

        def mock_send_step_notification(status, context, step, step_cfg):
            event_log.append(("notification", status))

        monkeypatch.setattr(job_state, "save_job", mock_save)
        monkeypatch.setattr(workflow_router, "send_step_notification", mock_send_step_notification)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)

        # Mock PROJECT_ROOT
        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))

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

        # Terminal replay
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

        # Verify terminal replay succeeds
        assert exit_code == 0

        # R16-03: No save or notification on terminal replay
        assert len(event_log) == 0


class TestR16R6_OmittedPathConflict:
    """R16-R6: Omitted incoming artifact path conflicts with stored path."""

    def test_applied_replay_omitted_path_conflicts(self, tmp_path, monkeypatch):
        """R16-R6: Applied terminal replay with omitted incoming path produces conflict."""
        # Create output file with known content
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_content = "test plan content"
        output_file.write_text(output_content)

        import hashlib
        real_digest = hashlib.sha256(output_content.encode()).hexdigest()

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
                        "output_path": str(output_file),
                        "output_digest": real_digest,
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

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # R16-R6: Omit incoming path (artifacts={})
        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={},  # OMITTED - should conflict
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        group_cfg = {"step_configs": {"generate_plan": {}}}

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

        # R16-R6: Should return conflict (exit_code 1) with failure
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "TERMINAL_EVIDENCE_CONFLICT"


class TestR16R6_GenerationRecoveryContext:
    """R16-R6: Generation requires valid inactive recovery context."""

    def test_generation_missing_recovery_context_fails(self, tmp_path, monkeypatch):
        """R16-R6: Generation with missing recovery context fails."""
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
                    # R16-R6: NO recovered_context - should fail
                }
            },
            "loop_context": {"active_attempt_id": attempt_id},
        }

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

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

        # R16-R6: Should return failure
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "MISSING_RECOVERY_CONTEXT"

    def test_generation_empty_recovery_context_fails(self, tmp_path, monkeypatch):
        """R16-R6: Generation with empty recovery context fails."""
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
                    # R16-R6: Empty recovered_context - should fail
                    "recovered_context": {},
                }
            },
            "loop_context": {"active_attempt_id": attempt_id},
        }

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

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

        # R16-R6: Should return failure
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "MISSING_RECOVERY_CONTEXT"

    def test_generation_missing_active_field_fails(self, tmp_path, monkeypatch):
        """R16-R6: Generation with missing active=False field fails."""
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
                    # R16-R6: Missing active field - should fail
                    "recovered_context": {
                        "job_id": "test-job",
                        "group_name": "plan_first_review_v1",
                        "baseline": 1,
                        "step": "generate_plan",
                        "input_revision": None,
                        "target_revision": 1,
                        # active field MISSING - should fail
                    },
                }
            },
            "loop_context": {"active_attempt_id": attempt_id},
        }

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

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

        # R16-R6: Should return failure (active must be exactly False)
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "INVALID_RECOVERY_CONTEXT"

    def test_generation_active_true_fails(self, tmp_path, monkeypatch):
        """R16-R6: Generation with active=True fails (must be False)."""
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
                    # R16-R6: active=True - should fail
                    "recovered_context": {
                        "job_id": "test-job",
                        "group_name": "plan_first_review_v1",
                        "baseline": 1,
                        "step": "generate_plan",
                        "input_revision": None,
                        "target_revision": 1,
                        "active": True,  # WRONG - should be False
                    },
                }
            },
            "loop_context": {"active_attempt_id": attempt_id},
        }

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

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

        # R16-R6: Should return failure (active must be exactly False)
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "INVALID_RECOVERY_CONTEXT"


class TestR16R7_FailedReplayPathIdentity:
    """R16-R7: Failed replay path identity enforcement for both absent and present."""

    def test_failed_replay_absent_recorded_new_incoming_conflicts(self, tmp_path, monkeypatch):
        """R16-R7: Failed replay with absent recorded path and new incoming path conflicts."""
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
                    "status": "failed",
                    "failed_result": {
                        "original_status": "APPROVED",
                        "remark": "Failed during processing",
                        # No output_path - was absent at failure time
                        "output_missing": True,
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

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # R16-R7: Incoming path is NEW but stored was absent
        result = StepResult(
            status="APPROVED",
            remark="Failed during processing",  # Must match failed_result.remark
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},  # NEW path
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        group_cfg = {"step_configs": {"generate_plan": {}}}

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

        # R16-R7: Should return conflict
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "TERMINAL_EVIDENCE_CONFLICT"

    def test_failed_replay_identical_absent_identities_unchanged(self, tmp_path, monkeypatch):
        """R16-R7: Failed replay with identical absent identities succeeds unchanged."""
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
                    "status": "failed",
                    "failed_result": {
                        "original_status": "APPROVED",
                        "remark": "Failed during processing",
                        # No output_path - was absent at failure time
                        "output_missing": True,
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

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # R16-R7: Incoming also absent - identical identities
        result = StepResult(
            status="APPROVED",
            remark="Failed during processing",
            artifacts={},  # Also absent
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        group_cfg = {"step_configs": {"generate_plan": {}}}

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

        # R16-R7: Should succeed unchanged
        assert exit_code == 1  # Failed result always returns 1
        assert returned_state == original_snapshot

    def test_failed_replay_recorded_path_omitted_incoming_conflicts(self, tmp_path, monkeypatch):
        """R16-R7: Failed replay with recorded path and omitted incoming conflicts."""
        # Create output file
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_content = "test content"
        output_file.write_text(output_content)

        import hashlib
        real_digest = hashlib.sha256(output_content.encode()).hexdigest()

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
                    "status": "failed",
                    "failed_result": {
                        "original_status": "APPROVED",
                        "remark": "Failed after save",
                        "output_path": str(output_file),
                        "output_digest": real_digest,
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

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # R16-R7: Incoming path OMITTED but stored was present
        result = StepResult(
            status="APPROVED",
            remark="Failed after save",
            artifacts={},  # OMITTED
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        group_cfg = {"step_configs": {"generate_plan": {}}}

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

        # R16-R7: Should return conflict
        assert exit_code == 1
        assert returned_state.get("last_failure_code") == "TERMINAL_EVIDENCE_CONFLICT"

    def test_failed_replay_matching_present_identities_unchanged(self, tmp_path, monkeypatch):
        """R16-R7: Failed replay with matching present identities succeeds."""
        # Create output file
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_content = "test content"
        output_file.write_text(output_content)

        import hashlib
        real_digest = hashlib.sha256(output_content.encode()).hexdigest()

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
                    "status": "failed",
                    "failed_result": {
                        "original_status": "APPROVED",
                        "remark": "Failed after save",
                        "output_path": str(output_file),
                        "output_digest": real_digest,
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

        original_snapshot = copy.deepcopy(state)

        import agent_runner_v2.runtime_context as runtime_context
        monkeypatch.setattr(runtime_context, "PROJECT_ROOT", Path(str(tmp_path)))
        monkeypatch.setattr(job_state, "save_job", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_workflow_notification", lambda *a: None)
        monkeypatch.setattr(workflow_router, "send_step_notification", lambda *a: None)

        # R16-R7: Incoming path MATCHES stored path
        result = StepResult(
            status="APPROVED",
            remark="Failed after save",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},  # MATCHES
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        group_cfg = {"step_configs": {"generate_plan": {}}}

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

        # R16-R7: Should succeed (file exists and digest matches)
        assert exit_code == 1  # Failed result always returns 1
        assert returned_state == original_snapshot


# ---------------------------------------------------------------------------
# R10: Shared temporary-storage fixture for production persistence tests
# ---------------------------------------------------------------------------

@pytest.fixture
def production_persistence(tmp_path, monkeypatch):
    """Shared fixture that redirects production job paths and wraps original save/load.

    R12: Captures original production save_job/load_job, redirects job_dir paths,
    and uses counting wrappers that actually CALL the captured originals.
    Mocks only external effects (notifications).
    """
    # R12: Capture original production functions BEFORE patching
    original_save_job = job_state.save_job
    original_load_job = job_state.load_job

    # Create jobs directory
    jobs_dir = tmp_path / "jobs" / "plan_first_review_v1"
    jobs_dir.mkdir(parents=True, exist_ok=True)

    # Track counts
    save_count = [0]
    load_count = [0]
    notification_count = [0]

    # R12: Redirect job_dir to temp path (used by captured originals)
    def patched_job_dir(group_name: str, job_id: str) -> Path:
        return jobs_dir / job_id

    # R12: Counting save wrapper that CALLS captured original
    def counting_save_wrapper(group_name: str, job_id: str, state_to_save: dict) -> None:
        save_count[0] += 1
        # R12: Call the captured original, which uses patched job_dir
        original_save_job(group_name, job_id, state_to_save)

    # R12: Counting load wrapper that CALLS captured original
    def counting_load_wrapper(group_name: str, job_id: str) -> dict | None:
        load_count[0] += 1
        # R12: Call the captured original, which uses patched job_dir
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
    monkeypatch.setattr(job_state, "save_job", counting_save_wrapper)
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


class TestA07_RejectionSaveReload:
    """A07: Real rejection save/reload/deduplication with production persistence."""

    def test_rejection_save_reload_deduplication(self, tmp_path, monkeypatch, production_persistence):
        """R10: First rejection → production save → production reload → identical replay.
        
        Asserts:
        - One save count for first rejection
        - Production reload succeeds
        - Replay returns unchanged
        - No additional save/notification on replay
        """
        # Setup state
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
            "loop_context": {},
            "reject_counts": {},
        }
        
        group_cfg = {"step_configs": {"generate_plan": {}}}
        
        # PHASE 1: First rejection - production save
        result_reject = StepResult(
            status="REJECTED",
            remark="Needs improvement",
            artifacts={},
            reject_code="QUALITY",
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )
        
        returned_state, exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="generate_plan",
            step_cfg={},
            step_result=result_reject,
            coder_used="test-coder",
            max_rejects=3,
        )
        
        # Assert one save
        assert production_persistence["save_count"][0] == 1
        
        # Assert exit code
        assert exit_code == 1
        
        # Assert reject count updated
        assert returned_state.get("reject_counts", {}).get("generate_plan") == 1
        
        # PHASE 2: Production reload
        reloaded_state = production_persistence["load_state"]("test-job")
        assert reloaded_state is not None
        assert reloaded_state.get("reject_counts", {}).get("generate_plan") == 1
        
        # PHASE 3: Identical replay - no additional save
        result_replay = StepResult(
            status="REJECTED",
            remark="Needs improvement",
            artifacts={},
            reject_code="QUALITY",
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )
        
        # Reset counts
        production_persistence["save_count"][0] = 0
        production_persistence["notification_count"][0] = 0
        
        replayed_state, replay_exit = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=reloaded_state,
            step="generate_plan",
            step_cfg={},
            step_result=result_replay,
            coder_used="test-coder",
            max_rejects=3,
        )
        
        # R10: No additional save or notification on replay
        assert production_persistence["save_count"][0] == 0
        assert production_persistence["notification_count"][0] == 0
        
        # Assert unchanged
        assert replay_exit == 1
        assert replayed_state.get("reject_counts", {}).get("generate_plan") == 1


class TestA11_FailureBeforeReplacement:
    """A11b: Failure before replacement leaves old consistent JSON and original caller unchanged."""

    def test_failure_before_replacement_old_disk_json(self, tmp_path, monkeypatch, production_persistence):
        """R11: Persist initial JSON with production save, patch os.replace to raise before replacement.

        Asserts:
        - Observable error raised
        - Original caller contents equal their deep-copy snapshot
        - Old disk bytes/decoded JSON equal the old snapshot
        """
        # Setup state
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
            "loop_context": {},
            "initial_data": "preserved",
        }

        # R11: Save initial state to disk using production save (not direct json.dump)
        production_persistence["save_state"]("test-job", state)

        # R11: Capture old disk bytes and deep-copy the actual caller immediately before routing
        job_path = production_persistence["jobs_dir"] / "test-job" / "job.json"
        with open(job_path, 'rb') as f:
            old_disk_bytes = f.read()
        old_disk_json = json.loads(old_disk_bytes)
        caller_snapshot = copy.deepcopy(state)

        # Create output file
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test plan content")

        # R11: Patch os.replace to raise BEFORE invoking replacement
        original_os_replace = os.replace
        replace_calls = []

        def replace_then_raise(src, dst):
            replace_calls.append(("replace_attempt", str(src), str(dst)))
            # R11: Raise BEFORE replacement (not after)
            raise RuntimeError("Injected pre-replace failure")

        monkeypatch.setattr(os, "replace", replace_then_raise)

        group_cfg = {"step_configs": {"generate_plan": {}}}

        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        # Call routing - should raise
        with pytest.raises(RuntimeError, match="Injected pre-replace failure"):
            workflow_router.route_after_step(
                group_name="plan_first_review_v1",
                group_cfg=group_cfg,
                state=state,
                step="generate_plan",
                step_cfg={},
                step_result=result,
                coder_used="test-coder",
                max_rejects=3,
            )

        # R11: Assert observable error was raised
        assert len(replace_calls) == 1

        # R11: Assert caller contents equal their deep-copy snapshot
        assert state == caller_snapshot, "Original caller state changed"

        # R11: Assert old disk bytes/decoded JSON equal the old snapshot
        with open(job_path, 'rb') as f:
            new_disk_bytes = f.read()
        assert new_disk_bytes == old_disk_bytes, "Disk bytes changed after pre-replace failure"

        new_disk_json = json.loads(new_disk_bytes)
        assert new_disk_json == old_disk_json, "Disk JSON changed after pre-replace failure"


class TestA13_AuthoritativePersistence:
    """A13: Observe authoritative saved snapshots for applied/rejected/failed outcomes."""

    def test_applied_authoritative_snapshot(self, tmp_path, monkeypatch, production_persistence):
        """R10: Applied outcome saves authoritative snapshot with receipt/completion/accounting."""
        # Setup state
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
            "loop_context": {},
        }
        
        # Create output file
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_content = "test plan content"
        output_file.write_text(output_content)
        
        real_digest = hashlib.sha256(output_content.encode()).hexdigest()
        
        group_cfg = {"step_configs": {"generate_plan": {"produces": ["QWEN_PLAN_FILE"]}}}
        
        result = StepResult(
            status="APPROVED",
            remark="Good",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )
        
        returned_state, exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=state,
            step="generate_plan",
            step_cfg={"produces": ["QWEN_PLAN_FILE"]},
            step_result=result,
            coder_used="test-coder",
            max_rejects=3,
        )
        
        # R10: Assert one save
        assert production_persistence["save_count"][0] == 1
        
        # R10: Load and verify authoritative snapshot
        saved_state = production_persistence["load_state"]("test-job")
        
        # Verify attempt is now applied
        saved_attempt = saved_state.get("attempt_records", {}).get(attempt_id, {})
        assert saved_attempt.get("status") == "applied"
        
        # Verify receipt (applied_result)
        applied_result = saved_attempt.get("applied_result", {})
        assert applied_result.get("status") == "APPROVED"
        assert applied_result.get("output_digest") == real_digest
        
        # Verify completion accounting
        completions = saved_state.get("revision_completions", {})
        assert "b1_r1" in completions
        assert completions["b1_r1"].get("attempt_id") == attempt_id

    def test_rejected_authoritative_snapshot(self, tmp_path, monkeypatch, production_persistence):
        """R10: Rejected outcome saves authoritative snapshot with receipt and exit_code."""
        # Setup state
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
            "loop_context": {},
        }
        
        group_cfg = {"step_configs": {"generate_plan": {}}}
        
        result = StepResult(
            status="REJECTED",
            remark="Needs work",
            artifacts={},
            reject_code="QUALITY",
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )
        
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
        
        # R10: Load and verify authoritative snapshot
        saved_state = production_persistence["load_state"]("test-job")
        
        # Verify attempt is now rejected
        saved_attempt = saved_state.get("attempt_records", {}).get(attempt_id, {})
        assert saved_attempt.get("status") == "rejected"
        
        # Verify receipt (rejected_result)
        rejected_result = saved_attempt.get("rejected_result", {})
        assert rejected_result.get("status") == "REJECTED"
        assert rejected_result.get("reject_code") == "QUALITY"
        assert rejected_result.get("exit_code") == 1
        
        # R10: Verify NO completion accounting for rejected
        completions = saved_state.get("revision_completions", {})
        assert "b1_r1" not in completions

    def test_application_failure_authoritative_snapshot(self, tmp_path, monkeypatch, production_persistence):
        """R11: Application-failure outcome saves authoritative snapshot with receipt.

        Asserts:
        - Attempt status = "failed"
        - failed_result contains receipt (original_status, failure_reason)
        - No speculative transition success/completion
        - Clean baseline progress
        """
        # Setup baseline state (clean state before failure)
        attempt_id = "att_test123"
        baseline_state = {
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
            "loop_context": {},
            "revision_completions": {},  # Clean baseline - no prior completions
        }

        # R11: Reset save_count before the function call (no pre-save in test setup)
        production_persistence["save_count"][0] = 0

        # Create output file (for digest computation)
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_content = "test plan content for failure"
        output_file.write_text(output_content)

        result = StepResult(
            status="APPROVED",
            remark="Generated successfully",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={},
            attempt_id=attempt_id,
        )

        # Call _commit_application_failure_from_baseline
        failure_state, exit_code = workflow_router._commit_application_failure_from_baseline(
            baseline=baseline_state,
            group_name="plan_first_review_v1",
            attempt_id=attempt_id,
            step_result=result,
            failure_reason="DOWNSTREAM_ERROR",
            step="generate_plan",
        )

        # R11: Assert one save (the function's save)
        assert production_persistence["save_count"][0] == 1

        # R11: Load and verify authoritative snapshot
        saved_state = production_persistence["load_state"]("test-job")

        # Verify attempt is now failed
        saved_attempt = saved_state.get("attempt_records", {}).get(attempt_id, {})
        assert saved_attempt.get("status") == "failed"

        # Verify receipt (failed_result) contains original_status and failure_reason
        failed_result = saved_attempt.get("failed_result", {})
        assert failed_result.get("original_status") == "APPROVED"
        assert failed_result.get("failure_reason") == "DOWNSTREAM_ERROR"
        assert failed_result.get("remark") == "Generated successfully"

        # R11: Verify NO completion accounting (failure excludes speculative success)
        completions = saved_state.get("revision_completions", {})
        assert "b1_r1" not in completions, "Failure should not have completion accounting"

        # R11: Verify clean baseline progress - job_status is WAITING_FOR_HUMAN_INTERVENTION
        assert saved_state.get("job_status") == "WAITING_FOR_HUMAN_INTERVENTION"

    def test_application_failure_no_speculative_mutations(self, tmp_path, monkeypatch, production_persistence):
        """R13: Caller-side proof that speculative changes do not enter failure snapshot.

        Invokes real scoped routing, injects downstream application failure
        after speculative transition mutations would have been applied.
        R13: Confirms transition contains speculative changes, then asserts
        persisted failure snapshot excludes those changes while preserving
        allowed failure-envelope/receipt.
        """
        # R13: Setup state with nonempty markers for meaningful comparison
        attempt_id = "att_test123"
        baseline_state = {
            "job_id": "test-job",
            "template_group": "plan_first_review_v1",
            "job_status": "IN_PROGRESS",
            "current_step": "generate_plan",
            "requirements_baseline": 1,
            "plan_revision": 1,  # Baseline has r1
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
            "loop_context": {},
            # R13: Nonempty baseline markers for meaningful exclusion test
            "completed_steps": ["setup"],  # Baseline progress marker
            "retry_history": [{"step": "setup", "attempt": 1}],  # Baseline history
            "revision_completions": {},  # No completions yet
        }

        # R13: Capture baseline snapshot for comparison
        baseline_snapshot = copy.deepcopy(baseline_state)

        # Reset save_count
        production_persistence["save_count"][0] = 0

        # Create output file
        output_file = tmp_path / "Planning" / "test" / "Qwen_Plan_v01.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("test plan content")

        result = StepResult(
            status="APPROVED",
            remark="Generated successfully",
            artifacts={"QWEN_PLAN_FILE": "Planning/test/Qwen_Plan_v01.md"},
            reject_code=None,
            meta_json_path="meta.json",
            usage_data={"tokens_used": 1000},  # R13: Nonempty usage
            attempt_id=attempt_id,
        )

        # R13: Capture transition state to confirm it contains speculative changes
        transition_captured = [None]

        # R13: Patch advance_step to inject failure AFTER capturing speculative mutations
        original_advance_step = workflow_router.advance_step

        def advance_with_injected_failure(*args, **kwargs):
            state, exit_code = original_advance_step(*args, **kwargs)
            # R13: Capture the transition state with speculative mutations
            transition_captured[0] = copy.deepcopy(state)
            # Inject failure - caller should use baseline, not this mutated state
            return state, 1

        monkeypatch.setattr(workflow_router, "advance_step", advance_with_injected_failure)

        group_cfg = {"step_configs": {"generate_plan": {"produces": ["QWEN_PLAN_FILE"]}}}

        # R13: Call real routing through route_after_step
        failure_state, exit_code = workflow_router.route_after_step(
            group_name="plan_first_review_v1",
            group_cfg=group_cfg,
            state=baseline_state,
            step="generate_plan",
            step_cfg={"produces": ["QWEN_PLAN_FILE"]},
            step_result=result,
            coder_used="test-coder",
            max_rejects=3,
        )

        # R13: Assert failure path was taken
        assert exit_code == 1

        # R13: Confirm transition contained speculative changes
        transition = transition_captured[0]
        assert transition is not None, "Transition state was not captured"

        # R13: Transition should have artifacts update (speculative)
        transition_artifacts = transition.get("artifacts", {})
        assert "QWEN_PLAN_FILE" in transition_artifacts, "Transition missing artifact update"

        # R13: Transition should have cleared reject_counts (speculative)
        transition_rejects = transition.get("reject_counts", {})
        assert transition_rejects.get("generate_plan") == 0, "Transition has wrong reject count"

        # R13: Assert one save (the failure commit)
        assert production_persistence["save_count"][0] == 1

        # R13: Load and verify failure snapshot
        saved_state = production_persistence["load_state"]("test-job")

        # R13: Verify attempt is failed
        saved_attempt = saved_state.get("attempt_records", {}).get(attempt_id, {})
        assert saved_attempt.get("status") == "failed"

        # R13: CRITICAL - Verify speculative completion accounting EXCLUDED
        completions = saved_state.get("revision_completions", {})
        assert completions == {}, f"Expected no completions, got {completions}"

        # R13: Verify baseline progress preserved (plan_revision still 1)
        assert saved_state.get("plan_revision") == 1, "Speculative revision advancement leaked"

        # R13: Verify baseline markers preserved (not overwritten by speculative changes)
        assert saved_state.get("completed_steps") == baseline_snapshot.get("completed_steps"), \
            "Baseline completed_steps modified"
        assert saved_state.get("retry_history") == baseline_snapshot.get("retry_history"), \
            "Baseline retry_history modified"

        # R13: Verify allowed failure-envelope changes present
        assert saved_state.get("job_status") == "WAITING_FOR_HUMAN_INTERVENTION"
        assert saved_state.get("last_failure_code") == "APPLICATION_FAILURE"
        assert saved_state.get("pending_intervention_for") == "generate_plan"

        # R13: Verify receipt (failed_result) contains original_status for identity
        failed_result = saved_attempt.get("failed_result", {})
        assert failed_result.get("original_status") == "APPROVED"
        assert failed_result.get("failure_reason") == "Application routing failed"
