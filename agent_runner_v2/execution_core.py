from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .execution_support import classify_pre_run_failure, default_usage_summary
from .step_runner import StepResult


@dataclass
class StepExecutionFailure:
    exception: Exception
    failure_class: str
    failure_code: str
    failure_reason: str
    failure_source: str


@dataclass
class StepExecutionAttempt:
    step_result: StepResult | None = None
    failure: StepExecutionFailure | None = None

    @property
    def succeeded(self) -> bool:
        return self.step_result is not None


@dataclass
class RoutedStepExecution:
    state: dict[str, Any]
    exit_code: int
    step_result: StepResult | None = None
    failure: StepExecutionFailure | None = None

    @property
    def succeeded(self) -> bool:
        return self.step_result is not None


PreparedStepExecutor = Callable[..., StepResult]
FailureRouter = Callable[..., tuple[dict[str, Any], int]]
StepRouter = Callable[..., tuple[dict[str, Any], int]]


def invoke_prepared_step(
    *,
    executor: PreparedStepExecutor,
    prepared: Any,
    template_group: str,
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
    effective_root: Path,
) -> StepExecutionAttempt:
    try:
        step_result = executor(
            prepared=prepared,
            template_group=template_group,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            effective_root=effective_root,
        )
    except Exception as exc:
        envelope = classify_pre_run_failure(exc)
        return StepExecutionAttempt(
            failure=StepExecutionFailure(
                exception=exc,
                failure_class=envelope["failure_class"],
                failure_code=envelope["failure_code"],
                failure_reason=envelope["failure_reason"],
                failure_source=envelope["failure_source"],
            )
        )
    return StepExecutionAttempt(step_result=step_result)


def execute_routed_step(
    *,
    executor: PreparedStepExecutor,
    failure_router: FailureRouter,
    step_router: StepRouter,
    prepared: Any,
    group_name: str,
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
    coder_used: str,
    max_rejects: int,
    effective_root: Path,
) -> RoutedStepExecution:
    attempt = invoke_prepared_step(
        executor=executor,
        prepared=prepared,
        template_group=group_name,
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        effective_root=effective_root,
    )
    if attempt.failure is not None:
        routed_state, exit_code = failure_router(
            group_name=group_name,
            state=state,
            step=step,
            step_cfg=step_cfg,
            coder_used=coder_used,
            exc=attempt.failure.exception,
            max_rejects=max_rejects,
            usage_data=default_usage_summary(),
        )
        return RoutedStepExecution(
            state=routed_state,
            exit_code=exit_code,
            failure=attempt.failure,
        )

    assert attempt.step_result is not None
    routed_state, exit_code = step_router(
        group_name=group_name,
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        step_result=attempt.step_result,
        coder_used=coder_used,
        max_rejects=max_rejects,
    )
    return RoutedStepExecution(
        state=routed_state,
        exit_code=exit_code,
        step_result=attempt.step_result,
    )
