from __future__ import annotations

from .cli_runtime import format_job_status_summary, step_progress_label
from .failure_runtime import clear_last_failure
from .job_state import (
    approve_step,
    apply_task_execution_binding,
    create_job,
    ensure_backward_compatible_state,
    find_matching_active_job,
    find_matching_completed_job,
    force_approve_step,
    get_job_status,
    infer_seed_identity,
    load_job,
    migrate_job_state,
    prepare_state_for_retry,
    recover_exhausted_planning_job,
    reconcile_job_state,
    reapply_routing,
    save_job,
    set_job_status,
)
from .state_defaults import default_loop_context, default_replan_context
from .task_runtime import build_task_execution_binding_from_ids
from .runtime_context import ARTIFACT_ROOT

from . import workflow_runtime as _workflow_runtime


def _missing_artifacts(keys: list[str], state: dict) -> list[str]:
    return _workflow_runtime.missing_artifacts(keys, state)


def _parse_key_value_pairs(values: list[str]) -> dict[str, str]:
    return _workflow_runtime.parse_key_value_pairs(values)


def _step_progress_label(group_cfg: dict, step: str | None) -> str:
    return step_progress_label(group_cfg, step)


def _format_job_status_summary(state: dict, group_cfg: dict) -> str:
    return format_job_status_summary(state, group_cfg, get_job_status=get_job_status)


def _build_task_execution_binding_from_task_file(task_file: str) -> dict:
    from .job_state import build_task_execution_binding_from_task_file

    return build_task_execution_binding_from_task_file(task_file)


def _task_execution_binding_identity(execution_binding: dict) -> tuple[str | None, str | None]:
    from .job_state import task_execution_binding_identity

    return task_execution_binding_identity(execution_binding)


def _reset_loop_context() -> dict:
    return default_loop_context()


def _reset_replan_context() -> dict:
    return default_replan_context()
