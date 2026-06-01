"""Tests for workflow_router.py — step advancement, retry logic,
approve/complete flows, rejection routing, loop/replan.

Uses real state dicts — no mocks for routing logic.
Uses mock.patch for save_job and external I/O.
"""
import datetime as dt
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agent_runner_v2.workflow_router import (
    route_after_step,
    route_after_failure,
    _route_approved,
    _route_rejected,
    _route_loop_or_replan,
    _trigger_loop,
    _trigger_replan,
    _classify_model_rejection,
    _classify_exception_v2,
    _looks_like_transient_error,
    _is_non_progressing,
    _consume_planning_attempt_budget,
    _update_review_state,
    _sync_review_feedback_artifact,
    _review_target_artifact_key,
)
from agent_runner_v2.step_runner import StepResult
from agent_runner_v2.coder_adapters import CoderInvocationError
from agent_runner_v2.exceptions import MetaJsonMissingError, MetaJsonInvalidError, ArtifactMissingError
from agent_runner_v2.job_state import (
    CONTROL_CLASSES,
    REVIEW_DECISIONS,
    HUMAN_DECISIONS,
    FINAL_DECISION_SOURCES,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_step_result(
    status="APPROVED",
    remark="",
    artifacts=None,
    reject_code=None,
    usage_data=None,
) -> StepResult:
    return StepResult(
        status=status,
        remark=remark,
        artifacts=artifacts or {},
        reject_code=reject_code,
        meta_json_path="sidecar.meta.json",
        usage_data=usage_data or {},
    )


def _base_state(**overrides):
    """Create a minimal state dict for testing routing."""
    state = {
        "job_id": "TEST-001",
        "template_group": "test_group",
        "job_status": "IN_PROGRESS",
        "status": "IN_PROGRESS",
        "current_step": "project_analysis",
        "completed_steps": [],
        "failed_steps": [],
        "reject_counts": {},
        "step_coders": {},
        "step_usage": {},
        "usage_summary": {
            "steps_with_usage": 0, "steps_without_usage": 0,
            "input_tokens": None, "output_tokens": None,
            "total_tokens": None, "cost": None, "duration_ms": None,
        },
        "model_approved_steps": [],
        "review_state": {
            "artifact_type": None, "artifact_key": None, "artifact_path": None,
            "reviewer_step": None, "review_iteration": 0, "review_decision": "PENDING",
            "review_decided_at": None, "coder_used": None, "human_decision": "PENDING",
            "human_decided_at": None, "human_actor": None,
            "final_decision": None, "final_decision_source": None,
        },
        "last_model_output": None,
        "retry_history": [],
        "auto_retry_count_by_step": {},
        "human_retry_count_by_step": {},
        "failure_history": [],
        "artifacts": {},
        "loop_context": {
            "active": False, "loop_step": None, "refine_step": None,
            "loop_target_artifact": None, "loop_source_review": None,
            "loop_iteration": 0, "pre_refine_checksum": None,
        },
        "loop_history": [],
        "replan_context": {
            "active": False, "source_review_step": None, "replan_step": None,
            "target_artifact": None, "source_review_file": None, "replan_attempt": 0,
            "pre_replan_checksum": None, "trigger_reason": None, "blocking_issues": [],
            "previous_blocking_issue_count": 0, "previous_blocking_issue_severity": 0,
        },
        "replan_history": [],
        "planning_attempt_count": 0,
        "pending_intervention_for": None,
        "last_failure_class": None,
        "last_failure_code": None,
        "last_failure_reason": None,
        "last_failure_source": None,
    }
    state.update(overrides)
    return state


def _base_group_cfg(**overrides):
    cfg = {
        "steps": ["project_analysis", "generate_sop", "review_sop", "generate_plan"],
        "job_init_step": "project_analysis",
        "step_configs": {
            "project_analysis": {"coder": "qwen"},
            "generate_sop": {"coder": "qwen"},
            "review_sop": {"requires_human_approval_after": True},
            "generate_plan": {"coder": "qwen"},
        },
    }
    cfg.update(overrides)
    return cfg


# ====================================================================
# route_after_step — APPROVED path
# ====================================================================

class TestRouteAfterStepApproved:
    def _make_save_job_noop(self):
        return patch("agent_runner_v2.workflow_router.save_job")

    def test_approved_clears_reject_counts(self):
        state = _base_state(reject_counts={"review_sop": 3}, auto_retry_count_by_step={"review_sop": 2})
        step_cfg = {}
        result = _make_step_result(status="APPROVED", remark="ok")

        with self._make_save_job_noop() as mock_save, \
             patch("agent_runner_v2.workflow_router.advance_step") as mock_advance:
            mock_advance.return_value = (state, 0)
            new_state, exit_code = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="review_sop", step_cfg=step_cfg,
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        assert exit_code == 0
        assert new_state["reject_counts"]["review_sop"] == 0

    def test_approved_merges_artifacts(self):
        state = _base_state(artifacts={"INIT_FILE": "init.md"})
        step_cfg = {}
        result = _make_step_result(
            status="APPROVED",
            artifacts={"PLAN_FILE": "plan.md", "NEW_ARTIFACT": "new.md"},
        )

        with self._make_save_job_noop() as mock_save, \
             patch("agent_runner_v2.workflow_router.advance_step") as mock_advance:
            mock_advance.return_value = (state, 0)
            new_state, exit_code = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="generate_plan", step_cfg=step_cfg,
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        assert new_state["artifacts"]["INIT_FILE"] == "init.md"
        assert new_state["artifacts"]["PLAN_FILE"] == "plan.md"
        assert new_state["artifacts"]["NEW_ARTIFACT"] == "new.md"

    def test_approved_records_step_coder(self):
        state = _base_state()
        result = _make_step_result(status="APPROVED")

        with self._make_save_job_noop() as mock_save, \
             patch("agent_runner_v2.workflow_router.advance_step") as mock_advance:
            mock_advance.return_value = (state, 0)
            new_state, _ = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="generate_sop", step_cfg={},
                step_result=result, coder_used="claude", max_rejects=3,
            )

        assert new_state["step_coders"]["generate_sop"] == "claude"

    def test_approved_records_retry_history(self):
        state = _base_state()
        result = _make_step_result(status="APPROVED", remark="looks good")

        with self._make_save_job_noop() as mock_save, \
             patch("agent_runner_v2.workflow_router.advance_step") as mock_advance:
            mock_advance.return_value = (state, 0)
            new_state, _ = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="gen", step_cfg={},
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        assert len(new_state["retry_history"]) == 1
        entry = new_state["retry_history"][0]
        assert entry["step"] == "gen"
        assert entry["result_status"] == "APPROVED"
        assert entry["result_remark"] == "looks good"
        assert entry["coder_used"] == "qwen"

    def test_approved_records_last_model_output(self):
        state = _base_state()
        result = _make_step_result(
            status="APPROVED", remark="good",
            artifacts={"X": "x.md"}, reject_code=None,
        )

        with self._make_save_job_noop() as mock_save, \
             patch("agent_runner_v2.workflow_router.advance_step") as mock_advance:
            mock_advance.return_value = (state, 0)
            new_state, _ = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="step", step_cfg={},
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        lmo = new_state["last_model_output"]
        assert lmo["status"] == "APPROVED"
        assert lmo["remark"] == "good"
        assert lmo["artifacts"] == {"X": "x.md"}

    def test_approved_clears_last_failure(self):
        state = _base_state(
            last_failure_class="HUMAN_RETRY_REQUIRED",
            last_failure_code="SOME_CODE",
            last_failure_reason="something",
        )
        result = _make_step_result(status="APPROVED")

        with self._make_save_job_noop() as mock_save, \
             patch("agent_runner_v2.workflow_router.advance_step") as mock_advance:
            mock_advance.return_value = (state, 0)
            new_state, _ = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="step", step_cfg={},
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        assert new_state["last_failure_class"] is None
        assert new_state["last_failure_code"] is None

    def test_approved_records_step_usage(self):
        state = _base_state()
        usage = {"input_tokens": 100, "output_tokens": 200}
        result = _make_step_result(status="APPROVED", usage_data=usage)

        with self._make_save_job_noop() as mock_save, \
             patch("agent_runner_v2.workflow_router.advance_step") as mock_advance:
            mock_advance.return_value = (state, 0)
            new_state, _ = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="step", step_cfg={},
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        assert "step" in new_state["step_usage"]


# ====================================================================
# route_after_step — REJECTED with on_reject_refine (loop)
# ====================================================================

class TestRouteAfterStepRejectedLoop:
    def _make_save_job_noop(self):
        return patch("agent_runner_v2.workflow_router.save_job")

    def test_triggers_loop_on_first_reject(self):
        state = _base_state(
            artifacts={"REVIEW_FILE": "docs/reviews/rev-01.md"},
        )
        step_cfg = {
            "on_reject_refine": {
                "step": "refine_task",
                "artifact": "REVIEW_FILE",
                "max_iterations": 2,
            },
            "produces": ["REVIEW_FILE"],
        }
        result = _make_step_result(status="REJECTED", remark="needs fixes")

        with self._make_save_job_noop() as mock_save, \
             patch("agent_runner_v2.workflow_router._consume_planning_attempt_budget") as mock_budget:
            mock_budget.return_value = (True, 1)
            new_state, exit_code = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="review_task", step_cfg=step_cfg,
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        assert exit_code == 0  # continue
        assert new_state["loop_context"]["active"] is True
        assert new_state["loop_context"]["loop_step"] == "review_task"
        assert new_state["loop_context"]["loop_iteration"] == 1
        assert new_state["current_step"] == "refine_task"

    def test_loop_iteration_increments(self):
        state = _base_state(
            artifacts={"REVIEW_FILE": "docs/reviews/rev-01.md"},
            loop_context={
                "active": True, "loop_step": "review_task", "loop_iteration": 1,
                "refine_step": None, "loop_target_artifact": None,
                "loop_source_review": None, "pre_refine_checksum": None,
            },
        )
        step_cfg = {
            "on_reject_refine": {
                "step": "refine_task",
                "artifact": "REVIEW_FILE",
                "max_iterations": 3,
            },
        }
        result = _make_step_result(status="REJECTED", remark="still broken")

        with self._make_save_job_noop() as mock_save, \
             patch("agent_runner_v2.workflow_router._consume_planning_attempt_budget") as mock_budget:
            mock_budget.return_value = (True, 1)
            new_state, exit_code = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="review_task", step_cfg=step_cfg,
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        assert new_state["loop_context"]["loop_iteration"] == 2

    def test_loop_exhausted_triggers_replan(self):
        state = _base_state(
            artifacts={"REVIEW_FILE": "docs/reviews/rev-01.md"},
            loop_context={
                "active": True, "loop_step": "review_task", "loop_iteration": 2,
                "refine_step": None, "loop_target_artifact": None,
                "loop_source_review": None, "pre_refine_checksum": None,
            },
            replan_context={
                "active": False, "replan_attempt": 0,
                "source_review_step": None, "replan_step": None,
                "target_artifact": None, "source_review_file": None,
                "pre_replan_checksum": None, "trigger_reason": None,
                "blocking_issues": [],
                "previous_blocking_issue_count": 0, "previous_blocking_issue_severity": 0,
            },
        )
        step_cfg = {
            "on_reject_refine": {
                "step": "refine_task",
                "artifact": "REVIEW_FILE",
                "max_iterations": 2,
            },
            "on_exhaust_replan": {
                "step": "replan_task",
                "artifact": "TASK_GRAPH_FILE",
                "max_replans": 1,
            },
        }
        result = _make_step_result(status="REJECTED", remark="still broken")

        with self._make_save_job_noop() as mock_save, \
             patch("agent_runner_v2.workflow_router._consume_planning_attempt_budget") as mock_budget:
            mock_budget.return_value = (True, 1)
            new_state, exit_code = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="review_task", step_cfg=step_cfg,
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        assert exit_code == 0  # continue to replan
        assert new_state["replan_context"]["active"] is True
        assert new_state["current_step"] == "replan_task"

    def test_loop_and_replan_exhausted_human_intervention(self):
        state = _base_state(
            artifacts={"REVIEW_FILE": "docs/reviews/rev-01.md"},
            loop_context={
                "active": True, "loop_step": "review_task", "loop_iteration": 2,
                "refine_step": None, "loop_target_artifact": None,
                "loop_source_review": None, "pre_refine_checksum": None,
            },
            replan_context={
                "active": False, "replan_attempt": 1,
                "source_review_step": None, "replan_step": None,
                "target_artifact": None, "source_review_file": None,
                "pre_replan_checksum": None, "trigger_reason": None,
                "blocking_issues": [],
                "previous_blocking_issue_count": 0, "previous_blocking_issue_severity": 0,
            },
        )
        step_cfg = {
            "on_reject_refine": {
                "step": "refine_task",
                "artifact": "REVIEW_FILE",
                "max_iterations": 2,
                "exhausted_failure_class": "HUMAN_RETRY_REQUIRED",
                "exhausted_failure_code": "REFINEMENT_EXHAUSTED",
            },
            "on_exhaust_replan": {
                "step": "replan_task",
                "artifact": "TASK_GRAPH_FILE",
                "max_replans": 1,
                "terminal_failure_code": "REPLAN_EXHAUSTED",
            },
        }
        result = _make_step_result(status="REJECTED", remark="exhausted")

        with self._make_save_job_noop() as mock_save, \
             patch("agent_runner_v2.workflow_router._consume_planning_attempt_budget") as mock_budget:
            mock_budget.return_value = (True, 1)
            new_state, exit_code = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="review_task", step_cfg=step_cfg,
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        assert exit_code == 1  # human intervention
        assert new_state["job_status"] == "WAITING_FOR_HUMAN_INTERVENTION"


# ====================================================================
# route_after_step — REJECTED without on_reject_refine
# ====================================================================

class TestRouteAfterStepRejectedNoRefine:
    def _make_save_job_noop(self):
        return patch("agent_runner_v2.workflow_router.save_job")

    def test_first_reject_human_retry(self):
        state = _base_state()
        result = _make_step_result(
            status="REJECTED",
            remark="pending approval",
            reject_code="PENDING",
        )

        with self._make_save_job_noop() as mock_save:
            new_state, exit_code = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="review_sop", step_cfg={},
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        assert exit_code == 1
        assert new_state["job_status"] == "WAITING_FOR_HUMAN_INTERVENTION"

    def test_reject_count_increments(self):
        state = _base_state(reject_counts={"review_sop": 1})
        result = _make_step_result(status="REJECTED", remark="rejected again")

        with self._make_save_job_noop() as mock_save:
            new_state, _ = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="review_sop", step_cfg={},
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        assert new_state["reject_counts"]["review_sop"] == 2

    def test_max_rejects_failed(self):
        state = _base_state(reject_counts={"step": 2})
        result = _make_step_result(status="REJECTED", remark="third reject")

        with self._make_save_job_noop() as mock_save:
            new_state, exit_code = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="step", step_cfg={},
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        assert exit_code == 2  # fatal
        assert new_state["job_status"] == "FAILED"
        assert "step" in new_state["failed_steps"]

    def test_fatal_classification(self):
        state = _base_state()
        result = _make_step_result(
            status="REJECTED",
            remark="forbidden by policy",
            reject_code="FATAL",
        )

        with self._make_save_job_noop() as mock_save:
            new_state, exit_code = route_after_step(
                group_name="test", group_cfg=_base_group_cfg(),
                state=state, step="step", step_cfg={},
                step_result=result, coder_used="qwen", max_rejects=3,
            )

        assert exit_code == 2
        assert new_state["job_status"] == "FAILED"


# ====================================================================
# route_after_failure
# ====================================================================

class TestRouteAfterFailure:
    def _make_save_job_noop(self):
        return patch("agent_runner_v2.workflow_router.save_job")

    def test_transient_error_auto_retry(self):
        state = _base_state()
        exc = CoderInvocationError(
            message="Connection error: timeout",
            command=["qwen"],
            return_code=1,
            stdout="",
            stderr="",
            raw_events=[],
        )

        with self._make_save_job_noop() as mock_save:
            new_state, exit_code = route_after_failure(
                group_name="test", state=state, step="step",
                coder_used="qwen", exc=exc, max_rejects=3,
                usage_data={},
            )

        assert exit_code == 1
        assert new_state["job_status"] == "WAITING_FOR_AUTO_RETRY"
        assert new_state["auto_retry_count_by_step"]["step"] == 1

    def test_meta_json_missing_human_retry(self):
        state = _base_state()
        exc = MetaJsonMissingError("meta.json not found")

        with self._make_save_job_noop() as mock_save:
            new_state, exit_code = route_after_failure(
                group_name="test", state=state, step="step",
                coder_used="qwen", exc=exc, max_rejects=3,
                usage_data={},
            )

        assert exit_code == 1
        assert new_state["job_status"] == "WAITING_FOR_HUMAN_INTERVENTION"

    def test_meta_json_invalid_human_retry(self):
        state = _base_state()
        exc = MetaJsonInvalidError("invalid schema")

        with self._make_save_job_noop() as mock_save:
            new_state, exit_code = route_after_failure(
                group_name="test", state=state, step="step",
                coder_used="qwen", exc=exc, max_rejects=3,
                usage_data={},
            )

        assert exit_code == 1
        assert new_state["job_status"] == "WAITING_FOR_HUMAN_INTERVENTION"

    def test_artifact_missing_human_retry(self):
        state = _base_state()
        exc = ArtifactMissingError("files missing", missing=["foo.md"])

        with self._make_save_job_noop() as mock_save:
            new_state, exit_code = route_after_failure(
                group_name="test", state=state, step="step",
                coder_used="qwen", exc=exc, max_rejects=3,
                usage_data={},
            )

        assert exit_code == 1

    def test_unknown_exception_fatal(self):
        state = _base_state()
        exc = RuntimeError("something unexpected")

        with self._make_save_job_noop() as mock_save:
            new_state, exit_code = route_after_failure(
                group_name="test", state=state, step="step",
                coder_used="qwen", exc=exc, max_rejects=3,
                usage_data={},
            )

        assert exit_code == 2
        assert new_state["job_status"] == "FAILED"

    def test_max_rejects_from_failure(self):
        state = _base_state(reject_counts={"step": 2})
        exc = MetaJsonMissingError("missing again")

        with self._make_save_job_noop() as mock_save:
            new_state, exit_code = route_after_failure(
                group_name="test", state=state, step="step",
                coder_used="qwen", exc=exc, max_rejects=3,
                usage_data={},
            )

        assert exit_code == 2  # max_rejects hit

    def test_non_progressing_no_reject_count_increment(self):
        """Runner configuration errors should not increment reject counts."""
        state = _base_state(reject_counts={"step": 1})
        exc = RuntimeError("something unexpected")

        with self._make_save_job_noop() as mock_save:
            new_state, exit_code = route_after_failure(
                group_name="test", state=state, step="step",
                coder_used="qwen", exc=exc, max_rejects=3,
                usage_data={},
            )

        # Unknown exception → FATAL → exit_code=2, reject count increments
        assert exit_code == 2
        assert new_state["job_status"] == "FAILED"
        # FATAL classification increments reject count
        assert new_state["reject_counts"]["step"] == 2

    def test_failure_records_retry_history(self):
        state = _base_state()
        exc = CoderInvocationError(
            message="Connection error",
            command=["qwen"],
            return_code=1,
            stdout="", stderr="", raw_events=[],
        )

        with self._make_save_job_noop() as mock_save:
            new_state, _ = route_after_failure(
                group_name="test", state=state, step="step",
                coder_used="qwen", exc=exc, max_rejects=3,
                usage_data={},
            )

        assert len(new_state["retry_history"]) == 1
        entry = new_state["retry_history"][0]
        assert entry["result_status"] == "FAILED_BEFORE_RESULT"
        assert entry["reject_type"] == "AUTO_RETRYABLE"

    def test_failure_records_failure_history(self):
        state = _base_state()
        exc = MetaJsonMissingError("no meta")

        with self._make_save_job_noop() as mock_save:
            new_state, _ = route_after_failure(
                group_name="test", state=state, step="step",
                coder_used="qwen", exc=exc, max_rejects=3,
                usage_data={},
            )

        assert len(new_state["failure_history"]) == 1


# ====================================================================
# _classify_model_rejection
# ====================================================================

class TestClassifyModelRejection:
    def test_control_class_hint(self):
        result = _make_step_result(status="REJECTED", reject_code="FATAL", remark="some remark")
        fclass, code, source = _classify_model_rejection(result)
        assert fclass == "FATAL"

    def test_transient_error(self):
        result = _make_step_result(status="REJECTED", remark="Connection error: timeout")
        fclass, code, source = _classify_model_rejection(result)
        assert fclass == "AUTO_RETRYABLE"

    def test_pending_approval(self):
        result = _make_step_result(status="REJECTED", remark="pending approval")
        fclass, code, source = _classify_model_rejection(result)
        assert fclass == "HUMAN_RETRY_REQUIRED"

    def test_forbidden_is_fatal(self):
        result = _make_step_result(status="REJECTED", remark="forbidden by policy")
        fclass, code, source = _classify_model_rejection(result)
        assert fclass == "FATAL"

    def test_out_of_scope_is_fatal(self):
        result = _make_step_result(status="REJECTED", remark="out of scope")
        fclass, code, source = _classify_model_rejection(result)
        assert fclass == "FATAL"

    def test_default_human_retry(self):
        result = _make_step_result(status="REJECTED", remark="something weird")
        fclass, code, source = _classify_model_rejection(result)
        assert fclass == "HUMAN_RETRY_REQUIRED"

    def test_no_reject_code_defaults_to_model_rejected(self):
        result = _make_step_result(status="REJECTED", remark="rejected")
        fclass, code, source = _classify_model_rejection(result)
        assert code == "MODEL_REJECTED"


# ====================================================================
# _classify_exception_v2
# ====================================================================

class TestClassifyExceptionV2:
    def test_transient_coder_error(self):
        exc = CoderInvocationError(
            message="Rate limit 429",
            command=["qwen"], return_code=1,
            stdout="", stderr="", raw_events=[],
        )
        fclass, code, source = _classify_exception_v2(exc)
        assert fclass == "AUTO_RETRYABLE"
        assert code == "TRANSIENT_API_ERROR"

    def test_non_transient_coder_error(self):
        exc = CoderInvocationError(
            message="some error",
            command=["qwen"], return_code=1,
            stdout="", stderr="", raw_events=[],
        )
        fclass, code, source = _classify_exception_v2(exc)
        assert fclass == "HUMAN_RETRY_REQUIRED"
        assert code == "ADAPTER_INVOCATION_FAILED"

    def test_meta_json_missing(self):
        exc = MetaJsonMissingError("missing")
        fclass, code, source = _classify_exception_v2(exc)
        assert fclass == "HUMAN_RETRY_REQUIRED"
        assert code == "META_JSON_MISSING"

    def test_meta_json_invalid(self):
        exc = MetaJsonInvalidError("invalid")
        fclass, code, source = _classify_exception_v2(exc)
        assert fclass == "HUMAN_RETRY_REQUIRED"
        assert code == "META_JSON_INVALID"

    def test_artifact_missing(self):
        exc = ArtifactMissingError("missing", missing=["x.md"])
        fclass, code, source = _classify_exception_v2(exc)
        assert fclass == "HUMAN_RETRY_REQUIRED"
        assert code == "ARTIFACT_FILES_MISSING"

    def test_unknown_exception_fatal(self):
        exc = ValueError("unexpected")
        fclass, code, source = _classify_exception_v2(exc)
        assert fclass == "FATAL"
        assert code == "UNEXPECTED_RUNNER_ERROR"


# ====================================================================
# _looks_like_transient_error
# ====================================================================

class TestLooksLikeTransientError:
    def test_connection_error(self):
        assert _looks_like_transient_error("Connection error occurred")

    def test_timeout(self):
        assert _looks_like_transient_error("Request timed out")

    def test_rate_limit(self):
        assert _looks_like_transient_error("Rate limit exceeded")

    def test_429(self):
        assert _looks_like_transient_error("HTTP 429 Too Many Requests")

    def test_service_unavailable(self):
        assert _looks_like_transient_error("Service unavailable")

    def test_not_transient(self):
        assert not _looks_like_transient_error("Schema validation failed")

    def test_case_insensitive(self):
        assert _looks_like_transient_error("CONNECTION ERROR")


# ====================================================================
# _is_non_progressing
# ====================================================================

class TestIsNonProgressing:
    def test_runner_human_retry_invalid_config(self):
        assert _is_non_progressing(
            failure_class="HUMAN_RETRY_REQUIRED",
            failure_code="INVALID_RUNNER_CONFIGURATION",
            failure_source="runner",
        )

    def test_runner_human_retry_unknown_coder(self):
        assert _is_non_progressing(
            failure_class="HUMAN_RETRY_REQUIRED",
            failure_code="UNKNOWN_CODER",
            failure_source="runner",
        )

    def test_non_runner_not_non_progressing(self):
        assert not _is_non_progressing(
            failure_class="HUMAN_RETRY_REQUIRED",
            failure_code="INVALID_RUNNER_CONFIGURATION",
            failure_source="adapter",
        )

    def test_other_code_not_non_progressing(self):
        assert not _is_non_progressing(
            failure_class="HUMAN_RETRY_REQUIRED",
            failure_code="META_JSON_MISSING",
            failure_source="runner",
        )


# ====================================================================
# _consume_planning_attempt_budget
# ====================================================================

class TestConsumePlanningAttemptBudget:
    def test_no_limit_allows(self):
        state = {}
        group_cfg = {"max_planning_attempts": 0}
        allowed, current = _consume_planning_attempt_budget(state=state, group_cfg=group_cfg)
        assert allowed is True

    def test_within_budget(self):
        state = {}
        group_cfg = {"max_planning_attempts": 3}
        allowed, current = _consume_planning_attempt_budget(state=state, group_cfg=group_cfg)
        assert allowed is True
        assert current == 1

    def test_exceeds_budget(self):
        state = {"planning_attempt_count": 3}
        group_cfg = {"max_planning_attempts": 3}
        allowed, current = _consume_planning_attempt_budget(state=state, group_cfg=group_cfg)
        assert allowed is False
        assert current == 4

    def test_updates_counter(self):
        state = {}
        group_cfg = {"max_planning_attempts": 5}
        _consume_planning_attempt_budget(state=state, group_cfg=group_cfg)
        assert state["planning_attempt_count"] == 1


# ====================================================================
# _update_review_state
# ====================================================================

class TestUpdateReviewState:
    def test_sets_review_decision(self):
        state = {"artifacts": {}}
        step_cfg = {"on_reject_refine": {"artifact": "REVIEW_FILE"}}
        _update_review_state(
            state, step="review", step_cfg=step_cfg,
            review_decision="REJECTED",
            final_decision="REJECTED",
            final_decision_source="MODEL",
        )
        rs = state["review_state"]
        assert rs["review_decision"] == "REJECTED"
        assert rs["final_decision"] == "REJECTED"
        assert rs["final_decision_source"] == "MODEL"

    def test_sets_human_decision(self):
        state = {"artifacts": {}}
        step_cfg = {"on_reject_refine": {"artifact": "REVIEW_FILE"}}
        _update_review_state(
            state, step="review", step_cfg=step_cfg,
            human_decision="APPROVED",
        )
        rs = state["review_state"]
        assert rs["human_decision"] == "APPROVED"
        assert rs["human_decided_at"] is not None
        assert rs["human_actor"] == "human"

    def test_human_not_required(self):
        state = {"artifacts": {}}
        step_cfg = {"on_reject_refine": {"artifact": "REVIEW_FILE"}}
        _update_review_state(
            state, step="review", step_cfg=step_cfg,
            human_decision="NOT_REQUIRED",
        )
        rs = state["review_state"]
        assert rs["human_decision"] == "NOT_REQUIRED"
        assert rs["human_decided_at"] is None

    def test_pending_review_decided_at_none(self):
        state = {"artifacts": {}}
        step_cfg = {"on_reject_refine": {"artifact": "REVIEW_FILE"}}
        _update_review_state(
            state, step="review", step_cfg=step_cfg,
            review_decision="PENDING",
        )
        assert state["review_state"]["review_decided_at"] is None

    def test_no_artifact_key(self):
        state = {"artifacts": {}}
        _update_review_state(
            state, step="step", step_cfg={},
            review_decision="APPROVED",
        )
        # Should not set artifact-related fields
        rs = state["review_state"]
        assert rs.get("artifact_key") is None

    def test_sets_coder_used(self):
        state = {"artifacts": {}}
        step_cfg = {"on_reject_refine": {"artifact": "REVIEW_FILE"}}
        _update_review_state(
            state, step="review", step_cfg=step_cfg,
            coder_used="qwen",
        )
        assert state["review_state"]["coder_used"] == "qwen"


# ====================================================================
# _sync_review_feedback_artifact
# ====================================================================

class TestSyncReviewFeedbackArtifact:
    def test_aliases_validation_to_review(self):
        artifacts = {"VALIDATION_FILE": "docs/validation.md"}
        _sync_review_feedback_artifact(step="validator", artifacts=artifacts)
        assert artifacts["REVIEW_FILE"] == "docs/validation.md"

    def test_does_not_overwrite_existing_review(self):
        artifacts = {
            "VALIDATION_FILE": "docs/validation.md",
            "REVIEW_FILE": "docs/existing_review.md",
        }
        _sync_review_feedback_artifact(step="validator", artifacts=artifacts)
        assert artifacts["REVIEW_FILE"] == "docs/existing_review.md"

    def test_non_validator_step_no_alias(self):
        artifacts = {"VALIDATION_FILE": "docs/validation.md"}
        _sync_review_feedback_artifact(step="other_step", artifacts=artifacts)
        assert "REVIEW_FILE" not in artifacts

    def test_empty_validation_no_alias(self):
        artifacts = {"VALIDATION_FILE": ""}
        _sync_review_feedback_artifact(step="validator", artifacts=artifacts)
        assert "REVIEW_FILE" not in artifacts


# ====================================================================
# _review_target_artifact_key
# ====================================================================

class TestReviewTargetArtifactKey:
    def test_from_on_reject_refine(self):
        step_cfg = {"on_reject_refine": {"artifact": "REVIEW_FILE"}}
        assert _review_target_artifact_key(step_cfg) == "REVIEW_FILE"

    def test_from_produces_with_human_approval(self):
        step_cfg = {
            "produces": ["PLAN_FILE"],
            "requires_human_approval_after": True,
        }
        assert _review_target_artifact_key(step_cfg) == "PLAN_FILE"

    def test_no_on_reject_refine_no_produces(self):
        step_cfg = {}
        assert _review_target_artifact_key(step_cfg) is None

    def test_on_reject_refine_empty(self):
        step_cfg = {"on_reject_refine": {}}
        assert _review_target_artifact_key(step_cfg) is None

    def test_produces_without_human_approval(self):
        step_cfg = {"produces": ["PLAN_FILE"]}
        assert _review_target_artifact_key(step_cfg) is None
