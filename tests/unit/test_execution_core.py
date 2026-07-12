from __future__ import annotations

from pathlib import Path

from agent_runner_v2.execution_core import execute_routed_step
from agent_runner_v2.step_runner import StepResult


def test_execute_routed_step_uses_injected_step_router():
    captured: dict[str, object] = {}

    def executor(**kwargs):
        return StepResult(
            status="APPROVED",
            remark="ok",
            artifacts={},
            reject_code=None,
            meta_json_path="tmp/meta.json",
            usage_data={},
        )

    def step_router(**kwargs):
        captured["group_name"] = kwargs["group_name"]
        captured["step"] = kwargs["step"]
        captured["coder_used"] = kwargs["coder_used"]
        captured["step_result"] = kwargs["step_result"]
        return {"job_id": "JOB-1"}, 0

    def failure_router(**kwargs):
        raise AssertionError("failure router should not be used on success")

    routed = execute_routed_step(
        executor=executor,
        failure_router=failure_router,
        step_router=step_router,
        prepared=object(),
        group_name="group-a",
        group_cfg={},
        state={},
        step="step-a",
        step_cfg={},
        coder_used="qwen",
        max_rejects=2,
        effective_root=Path("."),
    )

    assert routed.succeeded is True
    assert routed.exit_code == 0
    assert captured["group_name"] == "group-a"
    assert captured["step"] == "step-a"
    assert captured["coder_used"] == "qwen"
    assert isinstance(captured["step_result"], StepResult)


def test_execute_routed_step_uses_injected_failure_router():
    captured: dict[str, object] = {}

    def executor(**kwargs):
        raise FileNotFoundError("missing required input artifact")

    def step_router(**kwargs):
        raise AssertionError("step router should not be used on failure")

    def failure_router(**kwargs):
        captured["group_name"] = kwargs["group_name"]
        captured["step"] = kwargs["step"]
        captured["coder_used"] = kwargs["coder_used"]
        captured["max_rejects"] = kwargs["max_rejects"]
        captured["exc"] = kwargs["exc"]
        return {"job_id": "JOB-2"}, 1

    routed = execute_routed_step(
        executor=executor,
        failure_router=failure_router,
        step_router=step_router,
        prepared=object(),
        group_name="group-b",
        group_cfg={},
        state={},
        step="step-b",
        step_cfg={},
        coder_used="claude",
        max_rejects=3,
        effective_root=Path("."),
    )

    assert routed.succeeded is False
    assert routed.exit_code == 1
    assert captured["group_name"] == "group-b"
    assert captured["step"] == "step-b"
    assert captured["coder_used"] == "claude"
    assert captured["max_rejects"] == 3
    assert isinstance(captured["exc"], FileNotFoundError)
