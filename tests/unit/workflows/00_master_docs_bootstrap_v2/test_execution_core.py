from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from agent_runner_v2.execution_core import execute_routed_step
from agent_runner_v2.execution_request import ExecutionRequest
from agent_runner_v2.job_state import get_job_status
from agent_runner_v2.step_runner import StepResult
from agent_runner_v2 import run_agent as run_agent_module
from agent_runner_v2 import runtime_context as runtime_context_module
from agent_runner_v2.workflow_router import route_after_failure, route_after_step
from conftest import load_bootstrap_workflow_module


_BOOTSTRAP_WORKFLOW_MODULE = load_bootstrap_workflow_module()
_WORKFLOW_NAME = "00_repo_master_docs_bootstrap_v1"
_ACTION_STEPS = [
    "00_scan_repo_codebase",
    "01_generate_codebase_baseline",
    "07_validate_codebase_baseline",
    "09_finalize_bootstrap",
    "stepCompletion",
]
_LLM_STEPS = [
    "02_generate_project_analysis",
    "03_generate_system_overview_docs",
    "04_generate_architecture_docs",
]


@pytest.fixture(autouse=True)
def _seed_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    runner_home = tmp_path / ".ukbe-runner"
    monkeypatch.setattr(runtime_context_module, "GLOBAL_RUNNER_HOME", runner_home)
    monkeypatch.setattr(
        runtime_context_module,
        "_CTX",
        runtime_context_module.RuntimeContext(
            workspace_root=tmp_path,
            runner_home=runner_home,
            workflow_name="default",
            workflow_root=tmp_path / "workflows" / "default",
            workflow_module=_BOOTSTRAP_WORKFLOW_MODULE,
            delivery_root=None,
        ),
    )


@pytest.fixture
def bootstrap_group_cfg(project_root: Path) -> dict:
    return run_agent_module._load_group(
        _WORKFLOW_NAME,
        workflow_root=project_root / "workflows",
    )


def _build_state(
    *,
    tmp_path: Path,
    group_cfg: dict,
    step_name: str,
) -> dict:
    request = ExecutionRequest.from_dict(
        {
            "workflow_name": _WORKFLOW_NAME,
            "template_group": _WORKFLOW_NAME,
            "workflow_run_id": f"run-{step_name}",
            "workflow_step_run_id": f"step-{step_name}",
            "job_id": f"JOB-{step_name}",
            "step_name": step_name,
            "project_root": str(tmp_path),
        }
    )
    return run_agent_module._build_execution_state(
        request=request,
        group_cfg=group_cfg,
    )


def _prepared_stub(tmp_path: Path, step_name: str) -> SimpleNamespace:
    return SimpleNamespace(
        action_name="",
        step_dir=tmp_path / ".ukbe-runner" / "jobs" / _WORKFLOW_NAME / "JOB" / step_name,
    )


def _execute_with_workflow_routing(
    *,
    executor,
    prepared,
    group_cfg: dict,
    state: dict,
    step: str,
    step_cfg: dict,
    coder_used: str,
    effective_root: Path,
):
    return execute_routed_step(
        executor=executor,
        failure_router=route_after_failure,
        step_router=route_after_step,
        prepared=prepared,
        group_name=_WORKFLOW_NAME,
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        coder_used=coder_used,
        max_rejects=int(group_cfg["default_max_rejects"]),
        effective_root=effective_root,
    )


def _artifact_payload(step_name: str, step_cfg: dict) -> dict[str, str]:
    produces = list(step_cfg.get("produces") or [])
    if not produces:
        return {}
    artifact_key = produces[0]
    markdown_validation_keys = {"VALIDATION_FILE", "SYSTEM_DOCS_VALIDATION"}
    suffix = ".json" if artifact_key.endswith("SNAPSHOT") else ".md"
    if artifact_key in markdown_validation_keys:
        suffix = ".md"
    return {artifact_key: f"artifacts/{step_name}/{artifact_key.lower()}{suffix}"}


def _success_result(step_name: str, step_cfg: dict) -> StepResult:
    return StepResult(
        status="APPROVED",
        remark=f"{step_name} approved",
        artifacts=_artifact_payload(step_name, step_cfg),
        reject_code=None,
        meta_json_path=f"artifacts/{step_name}/meta.json",
        usage_data={},
    )


def _rejected_result(step_name: str, step_cfg: dict) -> StepResult:
    return StepResult(
        status="REJECTED",
        remark=f"{step_name} rejected",
        artifacts=_artifact_payload(step_name, step_cfg),
        reject_code="TEST_REJECTED",
        meta_json_path=f"artifacts/{step_name}/meta.json",
        usage_data={},
    )


@pytest.mark.parametrize("step_name", _ACTION_STEPS)
def test_master_docs_action_steps_approved_route_to_expected_next_step(
    tmp_path: Path,
    bootstrap_group_cfg: dict,
    step_name: str,
) -> None:
    step_cfg = bootstrap_group_cfg["step_configs"][step_name]
    state = _build_state(tmp_path=tmp_path, group_cfg=bootstrap_group_cfg, step_name=step_name)
    if step_name == "stepCompletion":
        state["completed_steps"] = [
            prior_step
            for prior_step in bootstrap_group_cfg["steps"]
            if prior_step != "stepCompletion"
        ]

    routed = _execute_with_workflow_routing(
        executor=lambda **kwargs: _success_result(step_name, step_cfg),
        prepared=_prepared_stub(tmp_path, step_name),
        group_cfg=bootstrap_group_cfg,
        state=state,
        step=step_name,
        step_cfg=step_cfg,
        coder_used="action",
        effective_root=tmp_path,
    )

    assert routed.succeeded
    assert routed.exit_code == 0
    if step_name == "stepCompletion":
        assert get_job_status(routed.state) == "COMPLETED"
        assert routed.state["current_step"] is None
    else:
        assert get_job_status(routed.state) == "IN_PROGRESS"
        assert routed.state["current_step"] == step_cfg["onsuccess"]


@pytest.mark.parametrize("step_name", _ACTION_STEPS)
def test_master_docs_action_steps_exception_fail_terminally(
    tmp_path: Path,
    bootstrap_group_cfg: dict,
    step_name: str,
) -> None:
    step_cfg = bootstrap_group_cfg["step_configs"][step_name]
    state = _build_state(tmp_path=tmp_path, group_cfg=bootstrap_group_cfg, step_name=step_name)

    routed = _execute_with_workflow_routing(
        executor=lambda **kwargs: (_ for _ in ()).throw(RuntimeError(f"{step_name} boom")),
        prepared=_prepared_stub(tmp_path, step_name),
        group_cfg=bootstrap_group_cfg,
        state=state,
        step=step_name,
        step_cfg=step_cfg,
        coder_used="action",
        effective_root=tmp_path,
    )

    assert not routed.succeeded
    assert routed.failure is not None
    assert routed.failure.failure_code == "PRE_RUN_FAILURE"
    assert routed.exit_code == 2
    assert get_job_status(routed.state) == "FAILED"
    assert routed.state["current_step"] == step_name


@pytest.mark.parametrize("step_name", _LLM_STEPS)
def test_master_docs_llm_steps_approved_route_to_expected_next_step(
    tmp_path: Path,
    bootstrap_group_cfg: dict,
    step_name: str,
) -> None:
    step_cfg = bootstrap_group_cfg["step_configs"][step_name]
    state = _build_state(tmp_path=tmp_path, group_cfg=bootstrap_group_cfg, step_name=step_name)

    routed = _execute_with_workflow_routing(
        executor=lambda **kwargs: _success_result(step_name, step_cfg),
        prepared=_prepared_stub(tmp_path, step_name),
        group_cfg=bootstrap_group_cfg,
        state=state,
        step=step_name,
        step_cfg=step_cfg,
        coder_used="qwen-architect",
        effective_root=tmp_path,
    )

    assert routed.succeeded
    assert routed.exit_code == 0
    assert get_job_status(routed.state) == "IN_PROGRESS"
    assert routed.state["current_step"] == step_cfg["onsuccess"]


@pytest.mark.parametrize("step_name", _LLM_STEPS)
def test_master_docs_llm_steps_rejected_require_human_intervention(
    tmp_path: Path,
    bootstrap_group_cfg: dict,
    step_name: str,
) -> None:
    step_cfg = bootstrap_group_cfg["step_configs"][step_name]
    state = _build_state(tmp_path=tmp_path, group_cfg=bootstrap_group_cfg, step_name=step_name)

    routed = _execute_with_workflow_routing(
        executor=lambda **kwargs: _rejected_result(step_name, step_cfg),
        prepared=_prepared_stub(tmp_path, step_name),
        group_cfg=bootstrap_group_cfg,
        state=state,
        step=step_name,
        step_cfg=step_cfg,
        coder_used="qwen-architect",
        effective_root=tmp_path,
    )

    assert routed.succeeded
    assert routed.step_result is not None
    assert routed.step_result.status == "REJECTED"
    assert routed.exit_code == 1
    assert get_job_status(routed.state) == "WAITING_FOR_HUMAN_INTERVENTION"
    assert routed.state["current_step"] == step_name


@pytest.mark.parametrize("step_name", _LLM_STEPS)
def test_master_docs_llm_steps_exception_fail_terminally(
    tmp_path: Path,
    bootstrap_group_cfg: dict,
    step_name: str,
) -> None:
    step_cfg = bootstrap_group_cfg["step_configs"][step_name]
    state = _build_state(tmp_path=tmp_path, group_cfg=bootstrap_group_cfg, step_name=step_name)

    routed = _execute_with_workflow_routing(
        executor=lambda **kwargs: (_ for _ in ()).throw(RuntimeError(f"{step_name} boom")),
        prepared=_prepared_stub(tmp_path, step_name),
        group_cfg=bootstrap_group_cfg,
        state=state,
        step=step_name,
        step_cfg=step_cfg,
        coder_used="qwen-architect",
        effective_root=tmp_path,
    )

    assert not routed.succeeded
    assert routed.failure is not None
    assert routed.failure.failure_code == "PRE_RUN_FAILURE"
    assert routed.exit_code == 2
    assert get_job_status(routed.state) == "FAILED"
    assert routed.state["current_step"] == step_name


def test_master_docs_review_step_approved_advances_to_validation(
    tmp_path: Path,
    bootstrap_group_cfg: dict,
) -> None:
    step_name = "05_review_master_system_docs"
    step_cfg = bootstrap_group_cfg["step_configs"][step_name]
    state = _build_state(tmp_path=tmp_path, group_cfg=bootstrap_group_cfg, step_name=step_name)

    routed = _execute_with_workflow_routing(
        executor=lambda **kwargs: _success_result(step_name, step_cfg),
        prepared=_prepared_stub(tmp_path, step_name),
        group_cfg=bootstrap_group_cfg,
        state=state,
        step=step_name,
        step_cfg=step_cfg,
        coder_used="qwen-reviewer",
        effective_root=tmp_path,
    )

    assert routed.succeeded
    assert routed.exit_code == 0
    assert routed.state["current_step"] == "07_validate_codebase_baseline"


def test_master_docs_review_step_rejected_enters_refine_loop(
    tmp_path: Path,
    bootstrap_group_cfg: dict,
) -> None:
    step_name = "05_review_master_system_docs"
    step_cfg = bootstrap_group_cfg["step_configs"][step_name]
    state = _build_state(tmp_path=tmp_path, group_cfg=bootstrap_group_cfg, step_name=step_name)

    routed = _execute_with_workflow_routing(
        executor=lambda **kwargs: _rejected_result(step_name, step_cfg),
        prepared=_prepared_stub(tmp_path, step_name),
        group_cfg=bootstrap_group_cfg,
        state=state,
        step=step_name,
        step_cfg=step_cfg,
        coder_used="qwen-reviewer",
        effective_root=tmp_path,
    )

    assert routed.succeeded
    assert routed.exit_code == 0
    assert get_job_status(routed.state) == "IN_PROGRESS"
    assert routed.state["current_step"] == "06_refine_master_system_docs"
    assert routed.state["loop_context"]["active"] is True
    assert routed.state["loop_context"]["loop_step"] == step_name


def test_master_docs_review_step_rejected_after_max_iterations_waits_for_human(
    tmp_path: Path,
    bootstrap_group_cfg: dict,
) -> None:
    step_name = "05_review_master_system_docs"
    step_cfg = bootstrap_group_cfg["step_configs"][step_name]
    state = _build_state(tmp_path=tmp_path, group_cfg=bootstrap_group_cfg, step_name=step_name)
    state["loop_context"] = {
        "active": True,
        "loop_step": step_name,
        "refine_step": "06_refine_master_system_docs",
        "loop_target_artifact": "PROJECT_ANALYSIS",
        "loop_source_review": None,
        "loop_iteration": int(step_cfg["on_reject_refine"]["max_iterations"]),
        "pre_refine_checksum": None,
    }

    routed = _execute_with_workflow_routing(
        executor=lambda **kwargs: _rejected_result(step_name, step_cfg),
        prepared=_prepared_stub(tmp_path, step_name),
        group_cfg=bootstrap_group_cfg,
        state=state,
        step=step_name,
        step_cfg=step_cfg,
        coder_used="qwen-reviewer",
        effective_root=tmp_path,
    )

    assert routed.succeeded
    assert routed.exit_code == 1
    assert get_job_status(routed.state) == "WAITING_FOR_HUMAN_INTERVENTION"
    assert routed.state["current_step"] == step_name
    assert routed.state["last_failure_code"] == "MASTER_SYSTEM_DOC_REFINEMENT_EXHAUSTED"


def test_master_docs_review_step_exception_fail_terminally(
    tmp_path: Path,
    bootstrap_group_cfg: dict,
) -> None:
    step_name = "05_review_master_system_docs"
    step_cfg = bootstrap_group_cfg["step_configs"][step_name]
    state = _build_state(tmp_path=tmp_path, group_cfg=bootstrap_group_cfg, step_name=step_name)

    routed = _execute_with_workflow_routing(
        executor=lambda **kwargs: (_ for _ in ()).throw(RuntimeError("review boom")),
        prepared=_prepared_stub(tmp_path, step_name),
        group_cfg=bootstrap_group_cfg,
        state=state,
        step=step_name,
        step_cfg=step_cfg,
        coder_used="qwen-reviewer",
        effective_root=tmp_path,
    )

    assert not routed.succeeded
    assert routed.exit_code == 2
    assert routed.failure is not None
    assert get_job_status(routed.state) == "FAILED"


def test_master_docs_system_validation_rejected_enters_refine_loop(
    tmp_path: Path,
    bootstrap_group_cfg: dict,
) -> None:
    step_name = "08_validate_master_system_docs"
    step_cfg = bootstrap_group_cfg["step_configs"][step_name]
    state = _build_state(tmp_path=tmp_path, group_cfg=bootstrap_group_cfg, step_name=step_name)

    routed = _execute_with_workflow_routing(
        executor=lambda **kwargs: _rejected_result(step_name, step_cfg),
        prepared=_prepared_stub(tmp_path, step_name),
        group_cfg=bootstrap_group_cfg,
        state=state,
        step=step_name,
        step_cfg=step_cfg,
        coder_used="action",
        effective_root=tmp_path,
    )

    assert routed.succeeded
    assert routed.exit_code == 0
    assert get_job_status(routed.state) == "IN_PROGRESS"
    assert routed.state["current_step"] == "06_refine_master_system_docs"
    assert routed.state["loop_context"]["active"] is True
    assert routed.state["loop_context"]["loop_source_review"] == "artifacts/08_validate_master_system_docs/system_docs_validation.md"


@pytest.mark.parametrize(
    ("status", "expected_exit_code", "expected_job_status", "expected_step"),
    [
        ("APPROVED", 0, "IN_PROGRESS", "05_review_master_system_docs"),
        ("REJECTED", 1, "WAITING_FOR_HUMAN_INTERVENTION", "06_refine_master_system_docs"),
    ],
)
def test_master_docs_refine_step_routes_expected_outcomes(
    tmp_path: Path,
    bootstrap_group_cfg: dict,
    status: str,
    expected_exit_code: int,
    expected_job_status: str,
    expected_step: str,
) -> None:
    step_name = "06_refine_master_system_docs"
    step_cfg = bootstrap_group_cfg["step_configs"][step_name]
    state = _build_state(tmp_path=tmp_path, group_cfg=bootstrap_group_cfg, step_name=step_name)

    result = _success_result(step_name, step_cfg) if status == "APPROVED" else _rejected_result(step_name, step_cfg)
    routed = _execute_with_workflow_routing(
        executor=lambda **kwargs: result,
        prepared=_prepared_stub(tmp_path, step_name),
        group_cfg=bootstrap_group_cfg,
        state=state,
        step=step_name,
        step_cfg=step_cfg,
        coder_used="qwen-architect",
        effective_root=tmp_path,
    )

    assert routed.succeeded
    assert routed.exit_code == expected_exit_code
    assert get_job_status(routed.state) == expected_job_status
    assert routed.state["current_step"] == expected_step


def test_master_docs_refine_step_exception_fail_terminally(
    tmp_path: Path,
    bootstrap_group_cfg: dict,
) -> None:
    step_name = "06_refine_master_system_docs"
    step_cfg = bootstrap_group_cfg["step_configs"][step_name]
    state = _build_state(tmp_path=tmp_path, group_cfg=bootstrap_group_cfg, step_name=step_name)

    routed = _execute_with_workflow_routing(
        executor=lambda **kwargs: (_ for _ in ()).throw(RuntimeError("refine boom")),
        prepared=_prepared_stub(tmp_path, step_name),
        group_cfg=bootstrap_group_cfg,
        state=state,
        step=step_name,
        step_cfg=step_cfg,
        coder_used="qwen-architect",
        effective_root=tmp_path,
    )

    assert not routed.succeeded
    assert routed.failure is not None
    assert routed.exit_code == 2
    assert get_job_status(routed.state) == "FAILED"
