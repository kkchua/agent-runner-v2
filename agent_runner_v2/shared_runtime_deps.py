from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from .backend_client import BackendClient
from .bundle_loader import load_project_config, load_workflow_module, resolve_workflow_root
from .path_catalog import known_artifact_paths as _known_artifact_paths
from .exceptions import PreflightBlockedError
from .execution_core import invoke_prepared_step
from .job_state import (
    CURRENT_SCHEMA_VERSION,
    check_preflight_artifact_status,
    classify_pre_run_failure,
    create_step_dir as make_step_dir,
    default_usage_summary,
    default_review_state,
    default_task_execution_binding,
    get_job_status,
    load_job,
    save_job,
    _update_document_status,
)
from .runtime_context import ARTIFACT_ROOT, JOBS_ROOT, PACKAGE_ROOT, get_workflow_module, set_context, set_workflow_module
from .runtime_utils import now_iso as _now_iso, safe_relative_to as _safe_relative_to, save_json as _save_json, save_text as _save_text
from .step_runner import build_context, prompt_checksum, render_prompt, resolve_prompt_path, run_action, run_step
from .task_runtime import ensure_execution_task_binding_integrity, ensure_planning_task_queue_integrity
from .transition_runtime import mark_review_started
from .workflow_specs import build_step_execution_spec, get_template_group_cfg, reconcile_step_execution_spec
from .routing_runtime import predict_next_step_after_approved

from . import backend_execution as _backend_execution
from . import daemon_runtime as _daemon_runtime
from . import step_execution_runtime as _step_execution_runtime
from . import workflow_runtime as _workflow_runtime


DELIVERY_SCAFFOLD_PUBLISH_PATHS = _known_artifact_paths()


def _ensure_delivery_folders(target_root: Path) -> None:
    _workflow_runtime.ensure_delivery_folders(target_root)


def _load_group(
    group_name: str,
    workspace_root: Path | None = None,
    workflow_root: Path | None = None,
) -> dict[str, Any]:
    return _workflow_runtime.load_group(
        group_name,
        workspace_root=workspace_root,
        workflow_root=workflow_root,
    )


def _validate_static_reference_files(
    workspace_root: Path,
    group_cfg: dict[str, Any] | None = None,
    template_group: str = "",
) -> None:
    _workflow_runtime.validate_static_reference_files(
        workspace_root,
        group_cfg=group_cfg,
        template_group=template_group,
    )


def _missing_artifacts(keys: list[str], state: dict[str, Any]) -> list[str]:
    return _workflow_runtime.missing_artifacts(keys, state)


def _prepare_step_execution(
    *,
    template_group: str,
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
    project_root: Path,
    workflow_key_override: str = "",
    cli_coder: str | None = None,
):
    return _step_execution_runtime.prepare_step_execution(
        template_group=template_group,
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        project_root=project_root,
        workflow_key_override=workflow_key_override,
        cli_coder=cli_coder,
        hooks=sys.modules[__name__],
    )


def _execute_prepared_step(
    *,
    prepared: Any,
    template_group: str,
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
    effective_root: Path,
):
    return _step_execution_runtime.execute_prepared_step(
        prepared=prepared,
        template_group=template_group,
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        effective_root=effective_root,
        hooks=sys.modules[__name__],
    )


def _resolve_step_coder(
    *,
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
    cli_coder: str | None,
):
    return _step_execution_runtime.resolve_step_coder(
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        cli_coder=cli_coder,
    )


def _resolve_worker_engine_root(engine_root: str | None) -> tuple[str | None, str | None]:
    return _daemon_runtime.resolve_worker_engine_root(engine_root, hooks=sys.modules[__name__])


def _build_group_cfg_from_execution_spec(
    spec: dict[str, Any],
    template_group: str,
    step_name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    return _backend_execution.build_group_cfg_from_execution_spec(spec, template_group, step_name)


def _build_worker_crash_result(*, run: dict[str, Any], step_run: dict[str, Any], error: Exception) -> dict[str, Any]:
    return _daemon_runtime.build_worker_crash_result(run=run, step_run=step_run, error=error, hooks=sys.modules[__name__])


def _build_worker_request_payload(
    *,
    run: dict[str, Any],
    step_run: dict[str, Any],
    step_execution_spec: dict[str, Any] | None = None,
    backend_url: str = "",
    step_spec_source: str = "backend",
) -> dict[str, Any]:
    return _daemon_runtime.build_worker_request_payload(
        run=run,
        step_run=step_run,
        step_execution_spec=step_execution_spec,
        backend_url=backend_url,
        step_spec_source=step_spec_source,
        hooks=sys.modules[__name__],
    )
