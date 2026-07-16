from __future__ import annotations

from pathlib import Path

from agent_runner_v2.job_state import get_job_status
from agent_runner_v2.step_runner import StepResult
from agent_runner_v2.workflow_router import route_after_step


def _base_state() -> dict:
    return {
        "job_id": "JOB-1",
        "template_group": "wf",
        "workflow_name": "wf",
        "current_step": "review_docs",
        "artifacts": {},
        "reject_counts": {},
        "retry_history": [],
        "step_coders": {},
        "completed_steps": [],
        "failed_steps": [],
        "model_approved_steps": [],
        "auto_retry_count_by_step": {},
        "human_retry_count_by_step": {},
        "review_state": {},
    }


def _write_file(path: Path, content: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_model_rejected_without_refine_sends_waiting_notification(monkeypatch) -> None:
    workflow_captured: list[tuple[str, dict]] = []
    step_captured: list[tuple[str, dict, str, dict]] = []

    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.save_job",
        lambda group_name, job_id, state: None,
    )
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.send_workflow_notification",
        lambda status, context: workflow_captured.append((status, dict(context))) or True,
    )
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.send_step_notification",
        lambda status, context, step, step_cfg: step_captured.append((status, dict(context), step, dict(step_cfg))) or True,
    )

    state, exit_code = route_after_step(
        group_name="wf",
        group_cfg={},
        state=_base_state(),
        step="review_docs",
        step_cfg={"enable_notifications": True},
        step_result=StepResult(
            status="REJECTED",
            remark="missing input artifact",
            artifacts={},
            reject_code="MISSING_INPUT",
            meta_json_path="meta.json",
            usage_data={},
        ),
        coder_used="qwen",
        max_rejects=2,
    )

    assert exit_code == 1
    assert get_job_status(state) == "WAITING_FOR_HUMAN_INTERVENTION"
    assert len(step_captured) == 1
    assert step_captured[0][0] == "STEP_REJECTED"
    assert step_captured[0][2] == "review_docs"
    assert step_captured[0][3] == {"enable_notifications": True}
    assert len(workflow_captured) == 1
    assert workflow_captured[0][0] == "WAITING_FOR_HUMAN_INTERVENTION"


def test_refine_loop_exhaustion_sends_waiting_notification(monkeypatch) -> None:
    workflow_captured: list[tuple[str, dict]] = []
    step_captured: list[tuple[str, dict, str, dict]] = []

    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.save_job",
        lambda group_name, job_id, state: None,
    )
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.send_workflow_notification",
        lambda status, context: workflow_captured.append((status, dict(context))) or True,
    )
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.send_step_notification",
        lambda status, context, step, step_cfg: step_captured.append((status, dict(context), step, dict(step_cfg))) or True,
    )

    step_cfg = {
        "enable_notifications": True,
        "on_reject_refine": {
            "step": "refine_docs",
            "artifact": "SYSTEM_DOCS_INDEX",
            "max_iterations": 0,
            "exhausted_failure_code": "REFINE_EXHAUSTED",
            "exhausted_failure_class": "HUMAN_RETRY_REQUIRED",
        }
    }
    state, exit_code = route_after_step(
        group_name="wf",
        group_cfg={},
        state=_base_state(),
        step="review_docs",
        step_cfg=step_cfg,
        step_result=StepResult(
            status="REJECTED",
            remark="review still rejected",
            artifacts={},
            reject_code="QUALITY_GAP",
            meta_json_path="meta.json",
            usage_data={},
        ),
        coder_used="qwen",
        max_rejects=2,
    )

    assert exit_code == 1
    assert get_job_status(state) == "WAITING_FOR_HUMAN_INTERVENTION"
    assert len(step_captured) == 1
    assert step_captured[0][0] == "STEP_REJECTED"
    assert step_captured[0][2] == "review_docs"
    assert step_captured[0][3] == step_cfg
    assert len(workflow_captured) == 1
    assert workflow_captured[0][0] == "WAITING_FOR_HUMAN_INTERVENTION"


def test_rejected_with_refine_loop_sends_step_rejected_before_recovery(monkeypatch) -> None:
    workflow_captured: list[tuple[str, dict]] = []
    step_captured: list[tuple[str, dict, str, dict]] = []

    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.save_job",
        lambda group_name, job_id, state: None,
    )
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.send_workflow_notification",
        lambda status, context: workflow_captured.append((status, dict(context))) or True,
    )
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.send_step_notification",
        lambda status, context, step, step_cfg: step_captured.append((status, dict(context), step, dict(step_cfg))) or True,
    )

    step_cfg = {
        "enable_notifications": True,
        "on_reject_refine": {
            "step": "refine_docs",
            "artifact": "SYSTEM_DOCS_INDEX",
            "max_iterations": 2,
        }
    }
    state, exit_code = route_after_step(
        group_name="wf",
        group_cfg={},
        state=_base_state(),
        step="review_docs",
        step_cfg=step_cfg,
        step_result=StepResult(
            status="REJECTED",
            remark="needs refinement",
            artifacts={"REVIEW_FILE": "docs/review.md"},
            reject_code="QUALITY_GAP",
            meta_json_path="meta.json",
            usage_data={},
        ),
        coder_used="qwen",
        max_rejects=2,
    )

    assert exit_code == 0
    assert get_job_status(state) == "IN_PROGRESS"
    assert state["current_step"] == "refine_docs"
    assert len(step_captured) == 1
    assert step_captured[0][0] == "STEP_REJECTED"
    assert step_captured[0][2] == "review_docs"
    assert step_captured[0][3] == step_cfg
    assert workflow_captured == []


def test_layer1_review_reject_cleans_stale_validation_and_audit_docs(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.save_job",
        lambda group_name, job_id, state: None,
    )
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.send_workflow_notification",
        lambda status, context: True,
    )
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.send_step_notification",
        lambda status, context, step, step_cfg: True,
    )
    monkeypatch.setattr("agent_runner_v2.workflow_router.PROJECT_ROOT", tmp_path)

    job_id = "00L1-TEST-001"
    review_path = tmp_path / "docs/system/00_governance/bootstrap" / f"{job_id}-layer1-governance-review.md"
    validation_path = tmp_path / "docs/system/00_governance/bootstrap" / f"{job_id}-layer1-governance-validation.md"
    audit_path = tmp_path / "docs/system/00_governance/bootstrap" / f"{job_id}-layer1-governance-audit.md"
    legacy_validation_path = tmp_path / "docs/system/00_governance/bootstrap" / f"{job_id}-bootstrap-validation.md"
    _write_file(review_path, "review")
    _write_file(validation_path, "validation")
    _write_file(audit_path, "audit")
    _write_file(legacy_validation_path, "legacy-validation")

    state = _base_state()
    state["job_id"] = job_id
    state["template_group"] = "00_layer1_governance_bootstrap_v1"
    step_cfg = {
        "enable_notifications": True,
        "on_reject_refine": {
            "step": "refine_layer1_governance_docs",
            "artifact": "SYSTEM_DOCS_INDEX",
            "max_iterations": 2,
        },
    }
    state, exit_code = route_after_step(
        group_name="00_layer1_governance_bootstrap_v1",
        group_cfg={},
        state=state,
        step="review_layer1_governance_docs",
        step_cfg=step_cfg,
        step_result=StepResult(
            status="REJECTED",
            remark="needs refinement",
            artifacts={"REVIEW_FILE_SUGGESTED": review_path.relative_to(tmp_path).as_posix()},
            reject_code="QUALITY_GAP",
            meta_json_path="meta.json",
            usage_data={},
        ),
        coder_used="qwen",
        max_rejects=2,
    )

    assert exit_code == 0
    assert get_job_status(state) == "IN_PROGRESS"
    assert review_path.exists()
    assert not validation_path.exists()
    assert not legacy_validation_path.exists()
    assert not audit_path.exists()


def test_layer1_validate_reject_preserves_current_validation_but_cleans_stale_audit(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.save_job",
        lambda group_name, job_id, state: None,
    )
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.send_workflow_notification",
        lambda status, context: True,
    )
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.send_step_notification",
        lambda status, context, step, step_cfg: True,
    )
    monkeypatch.setattr("agent_runner_v2.workflow_router.PROJECT_ROOT", tmp_path)

    job_id = "00L1-TEST-002"
    validation_path = tmp_path / "docs/system/00_governance/bootstrap" / f"{job_id}-layer1-governance-validation.md"
    audit_path = tmp_path / "docs/system/00_governance/bootstrap" / f"{job_id}-layer1-governance-audit.md"
    _write_file(validation_path, "validation")
    _write_file(audit_path, "audit")

    state = _base_state()
    state["job_id"] = job_id
    state["template_group"] = "00_layer1_governance_bootstrap_v1"
    step_cfg = {
        "enable_notifications": True,
        "on_reject_refine": {
            "step": "refine_layer1_governance_docs",
            "artifact": "SYSTEM_DOCS_INDEX",
            "max_iterations": 2,
        },
    }
    state, exit_code = route_after_step(
        group_name="00_layer1_governance_bootstrap_v1",
        group_cfg={},
        state=state,
        step="validate_layer1_governance_docs",
        step_cfg=step_cfg,
        step_result=StepResult(
            status="REJECTED",
            remark="validation failed",
            artifacts={"SYSTEM_DOCS_VALIDATION": validation_path.relative_to(tmp_path).as_posix()},
            reject_code="LAYER1_GOVERNANCE_VALIDATION_FAILED",
            meta_json_path="meta.json",
            usage_data={},
        ),
        coder_used="action",
        max_rejects=2,
    )

    assert exit_code == 0
    assert get_job_status(state) == "IN_PROGRESS"
    assert validation_path.exists()
    assert not audit_path.exists()


def test_refine_loop_uses_persistent_reject_count_for_exhaustion(monkeypatch) -> None:
    workflow_captured: list[tuple[str, dict]] = []
    step_captured: list[tuple[str, dict, str, dict]] = []

    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.save_job",
        lambda group_name, job_id, state: None,
    )
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.send_workflow_notification",
        lambda status, context: workflow_captured.append((status, dict(context))) or True,
    )
    monkeypatch.setattr(
        "agent_runner_v2.workflow_router.send_step_notification",
        lambda status, context, step, step_cfg: step_captured.append((status, dict(context), step, dict(step_cfg))) or True,
    )

    step_cfg = {
        "enable_notifications": True,
        "on_reject_refine": {
            "step": "refine_docs",
            "artifact": "SYSTEM_DOCS_INDEX",
            "max_iterations": 2,
            "exhausted_failure_code": "REFINE_EXHAUSTED",
            "exhausted_failure_class": "HUMAN_RETRY_REQUIRED",
        }
    }
    state = _base_state()
    state["reject_counts"]["review_docs"] = 2
    state["loop_context"] = {
        "active": False,
        "loop_step": None,
        "refine_step": None,
        "target_artifact": None,
        "review_file": None,
        "loop_iteration": 0,
        "pre_refine_checksum": None,
    }

    state, exit_code = route_after_step(
        group_name="wf",
        group_cfg={},
        state=state,
        step="review_docs",
        step_cfg=step_cfg,
        step_result=StepResult(
            status="REJECTED",
            remark="still not compliant",
            artifacts={"REVIEW_FILE": "docs/review.md"},
            reject_code="QUALITY_GAP",
            meta_json_path="meta.json",
            usage_data={},
        ),
        coder_used="qwen",
        max_rejects=5,
    )

    assert exit_code == 1
    assert get_job_status(state) == "WAITING_FOR_HUMAN_INTERVENTION"
    assert state["current_step"] == "review_docs"
    assert state["reject_counts"]["review_docs"] == 3
    assert state["last_failure_code"] == "REFINE_EXHAUSTED"
    assert len(step_captured) == 1
    assert step_captured[0][0] == "STEP_REJECTED"
    assert step_captured[0][2] == "review_docs"
    assert step_captured[0][3] == step_cfg
    assert len(workflow_captured) == 1
    assert workflow_captured[0][0] == "WAITING_FOR_HUMAN_INTERVENTION"
