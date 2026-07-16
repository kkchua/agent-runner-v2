from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config_loader import load_runner_config
from .runtime_context import format_report_artifacts


def _resolved_coder_summary(
    *,
    run: dict[str, Any],
    step_run: dict[str, Any],
    spec: dict[str, Any],
    template_group: str,
    step_name: str,
    hooks: Any,
) -> dict[str, Any]:
    try:
        group_cfg, step_cfg = hooks._build_group_cfg_from_execution_spec(spec, template_group, step_name)
        state = {"step_coders": {}}
        resolved = hooks._resolve_step_coder(
            group_cfg=group_cfg,
            state=state,
            step=step_name,
            step_cfg=step_cfg,
            cli_coder=None,
        )
        if not isinstance(resolved, tuple):
            raise TypeError("Resolved coder payload must be a tuple.")
        if len(resolved) == 4:
            coder_used, coder_alias, coder_role, coder_config = resolved
        elif len(resolved) == 2:
            coder_used, coder_config = resolved
            coder_alias = None
            coder_role = None
        else:
            raise ValueError(f"Unexpected resolved coder tuple shape: {len(resolved)}")
        coder_config = coder_config or {}
        model = str(coder_config.get("model") or "").strip() or None
        model_id = str(coder_config.get("model_id") or "").strip() or None
        connection = str(coder_config.get("connection") or "").strip() or None
        provider_key = str(coder_config.get("provider_key") or "").strip() or None
        return {
            "coder_used": str(coder_used),
            "coder_alias": coder_alias,
            "coder_role": coder_role,
            "connection": connection,
            "model_id": model_id,
            "model": model,
            "provider_key": provider_key,
            "source": "resolved",
        }
    except Exception:
        fallback_model = (
            str(((spec.get("coder_policy") or {}).get("model")) or "").strip()
            or str((((spec.get("raw_config") or {}).get("coder") or {}).get("model")) or "").strip()
            or None
        )
        coder_override = str(step_run.get("coder") or "").strip() or None
        return {
            "coder_used": coder_override,
            "coder_alias": coder_override,
            "coder_role": None,
            "connection": None,
            "model_id": fallback_model,
            "model": fallback_model,
            "provider_key": None,
            "source": "fallback",
        }


def resolve_worker_engine_root(engine_root: str | None, *, hooks: Any) -> tuple[str | None, str | None]:
    if engine_root:
        vfile = Path(engine_root) / "version.json"
        version = None
        if vfile.exists():
            try:
                version = json.loads(vfile.read_text(encoding="utf-8")).get("version")
            except Exception:
                pass
        return engine_root, version

    cfg = load_runner_config()

    engine_version = (cfg.get("engine_version") or "").strip()
    if not engine_version:
        return None, None
    if engine_version == "SNAPSHOT":
        return None, engine_version

    global_store = Path.home() / ".ukbe-runner" / "engine" / "versions" / engine_version
    if global_store.exists():
        print(f"[worker] engine {engine_version!r} resolved from global store (~/.ukbe-runner/engine/versions/)", flush=True)
        return str(global_store), engine_version

    raise RuntimeError(
        f"[worker] engine version {engine_version!r} not found in global store ({global_store}). "
        "Run: ukbe-run-agent engine install <version>"
    )


def _local_workflow_step_index(*, hooks: Any, template_group: str, workspace_path: Path, workflow_name: str, step_name: str) -> int | None:
    try:
        group_cfg = hooks.get_template_group_cfg(
            template_group=template_group,
            workspace_root=workspace_path,
            workflow_name=workflow_name or "default",
        )
    except Exception:
        return None

    steps = list(group_cfg.get("steps") or [])
    if step_name not in steps:
        return None
    return steps.index(step_name) + 1


def build_worker_request_payload(
    *,
    run: dict[str, Any],
    step_run: dict[str, Any],
    step_execution_spec: dict[str, Any] | None = None,
    backend_url: str = "",
    step_spec_source: str = "backend",
    hooks: Any,
) -> dict[str, Any]:
    workflow_name = str(run.get("workflow_name") or "")
    project_root = str(run.get("project_root") or run.get("workspace_path") or ".")
    template_group = str((step_execution_spec or {}).get("template_group") or workflow_name)
    step_name = str(step_run.get("step_name") or "")
    mode = (step_spec_source or "backend").strip().lower()
    if mode not in {"global", "backend", "hybrid"}:
        mode = "backend"
    spec = dict(step_execution_spec or {})
    coder_override = step_run.get("coder")
    workspace_path = Path(project_root).resolve()

    if mode == "global":
        try:
            group_cfg = hooks.get_template_group_cfg(
                template_group=template_group,
                workspace_root=workspace_path,
                workflow_name=workflow_name or "default",
            )
            spec = hooks.build_step_execution_spec(
                template_group=template_group,
                step_name=step_name,
                group_cfg=group_cfg,
            )
            coder_override = None
        except Exception:
            spec = dict(step_execution_spec or {})
    elif mode == "hybrid":
        try:
            spec = hooks.reconcile_step_execution_spec(
                template_group=template_group,
                step_name=step_name,
                workspace_root=workspace_path,
                workflow_name=workflow_name or "default",
                backend_spec=spec,
            )
        except Exception:
            spec = dict(step_execution_spec or {})

    if mode == "hybrid":
        try:
            group_cfg = hooks.get_template_group_cfg(
                template_group=template_group,
                workspace_root=workspace_path,
                workflow_name=workflow_name or "default",
            )
            local_spec = hooks.build_step_execution_spec(
                template_group=template_group,
                step_name=step_name,
                group_cfg=group_cfg,
            )
            if "required_inputs" not in spec and "required_inputs" in local_spec:
                spec["required_inputs"] = local_spec["required_inputs"]
            if "optional_inputs" not in spec and "optional_inputs" in local_spec:
                spec["optional_inputs"] = local_spec["optional_inputs"]
            if "produces" not in spec and "produces" in local_spec:
                spec["produces"] = local_spec["produces"]
        except Exception:
            pass

    input_artifacts = dict(run.get("input_payload") or {})
    required_artifact_keys = {
        item.get("artifact_key")
        for item in (spec.get("required_inputs") or [])
        if isinstance(item, dict) and item.get("artifact_key")
    }
    optional_artifact_keys = {
        item.get("artifact_key")
        for item in (spec.get("optional_inputs") or [])
        if isinstance(item, dict) and item.get("artifact_key")
    }
    context_payload = dict(run.get("context_payload") or {})
    for artifact_key in required_artifact_keys | optional_artifact_keys:
        value = context_payload.get(artifact_key)
        if isinstance(value, str) and value:
            input_artifacts[artifact_key] = value

    job_id = str(run.get("run_code") or run.get("id") or "backend-job")
    if mode == "backend":
        step_sequence_no = (
            spec.get("step_sequence_no")
            or step_run.get("sequence_no")
            or spec.get("step_order")
            or _local_workflow_step_index(
                hooks=hooks,
                template_group=template_group,
                workspace_path=workspace_path,
                workflow_name=workflow_name,
                step_name=step_name,
            )
            or 1
        )
    else:
        step_sequence_no = (
            _local_workflow_step_index(
                hooks=hooks,
                template_group=template_group,
                workspace_path=workspace_path,
                workflow_name=workflow_name,
                step_name=step_name,
            )
            or spec.get("step_sequence_no")
            or step_run.get("sequence_no")
            or 1
        )

    backend_step_dir_rel = str(
        hooks.JOBS_ROOT / template_group / job_id / f"{int(step_sequence_no):02d}_{step_name}"
    )
    resolved_coder = _resolved_coder_summary(
        run=run,
        step_run=step_run,
        spec=spec,
        template_group=template_group,
        step_name=step_name,
        hooks=hooks,
    )
    return {
        "workflow_name": workflow_name,
        "template_group": spec.get("template_group") or workflow_name,
        "job_id": job_id,
        "step_name": step_name,
        "step_sequence_no": int(step_sequence_no),
        "workflow_run_id": run.get("id"),
        "workflow_step_run_id": step_run.get("id"),
        "project_root": project_root,
        "target_project_root": run.get("project_root"),
        "input_artifacts": input_artifacts,
        "context_payload": context_payload,
        "env_overrides": {
            **(run.get("env_overrides") or {}),
            "BACKEND_URL": backend_url,
            "WORKFLOW_STEP_RUN_ID": str(step_run.get("id") or ""),
        },
        "coder_override": coder_override,
        "workflow_key_override": "",
        "backend_url": backend_url,
        "state_overrides": {"backend_step_dir_rel": backend_step_dir_rel},
        "step_execution_spec": spec,
        "resolved_coder": resolved_coder,
        "step_spec_source": mode,
    }

def _map_job_status_to_run_status(job_status: str) -> str:
    """Map job.json status to backend DB run_status."""
    mapping = {
        "IN_PROGRESS": "pending",
        "COMPLETED": "completed",
        "FAILED": "failed",
        "WAITING_FOR_HUMAN_INTERVENTION": "awaiting_human",
        "WAITING_FOR_AUTO_RETRY": "pending",
    }
    return mapping.get(job_status.upper(), "pending")


def build_job_sync_payload(*, job: dict[str, Any], step_result: dict[str, Any], step_run_id: str) -> dict[str, Any]:
    """Build the job-sync API payload from job.json state and step result.

    This is the sole mapping layer between the v2 runner's job.json state
    and the backend persistence API. No transition/routing logic here.
    """
    job_status = str(job.get("job_status") or job.get("status") or "IN_PROGRESS")
    current_step = job.get("current_step")
    run_status = _map_job_status_to_run_status(job_status)

    # next_step_name: the step to enqueue next (None = terminal)
    next_step_name: str | None = None
    if run_status == "pending" and current_step:
        next_step_name = str(current_step)

    # Artifacts: from job.json artifacts dict (filter out null values)
    artifacts_raw = job.get("artifacts") or {}
    project_root = Path(str(job.get("project_root") or "")).resolve() if str(job.get("project_root") or "").strip() else None
    output_payload = format_report_artifacts(artifacts_raw, project_root=project_root)
    # Filter out null/empty values to prevent backend FK violations
    output_payload = {k: v for k, v in output_payload.items() if isinstance(v, str) and v.strip()}
    artifacts_list: list[dict[str, Any]] = []
    for artifact_key, file_path in output_payload.items():
        artifacts_list.append({
            "artifact_key": artifact_key,
            "file_path": file_path.replace("\\", "/"),
            "role": "output",
        })

    # Events: build minimal events based on state
    events: list[dict[str, Any]] = []
    completed_steps = job.get("completed_steps") or []
    failed_steps = job.get("failed_steps") or []

    if job_status in ("FAILED",) or run_status == "failed":
        event_type = "RUN_FAILED"
        event_msg = job.get("last_failure_reason") or "Workflow failed"
        events.append({"event_type": event_type, "message": event_msg, "payload": {"failed_steps": failed_steps}})
    elif run_status == "awaiting_human":
        events.append({"event_type": "HUMAN_APPROVAL_REQUIRED", "message": f"Awaiting human approval after step", "payload": {}})
    elif run_status == "completed":
        events.append({"event_type": "RUN_COMPLETED", "message": "Workflow completed", "payload": {"completed_steps": completed_steps}})
    elif next_step_name:
        events.append({"event_type": "STEP_COMPLETED", "message": f"Step completed, next: {next_step_name}", "payload": {"next_step": next_step_name, "completed_steps": completed_steps}})
    else:
        events.append({"event_type": "STEP_COMPLETED", "message": "Step completed", "payload": {"completed_steps": completed_steps}})

    # Review: from review_state in job.json
    review_state = job.get("review_state") or {}
    review: dict[str, Any] | None = None
    review_decision = review_state.get("final_decision") or review_state.get("review_decision")
    if review_decision and str(review_decision).upper() != "PENDING":
        review = {
            "review_type": "step_review",
            "decision": str(review_decision),
            "remark": review_state.get("remark") or step_result.get("remark"),
            "findings": review_state.get("findings"),
            "evidence": review_state.get("evidence"),
            "full_result": review_state.get("full_result"),
        }

    # Error message
    error_message = job.get("last_failure_reason")

    # Duration estimate
    duration_seconds = None

    return {
        "step_status": step_result.get("status", "completed").lower(),
        "step_outcome": step_result.get("outcome"),
        "step_coder": step_result.get("coder_used"),
        "step_duration_seconds": duration_seconds,
        "run_status": run_status,
        "next_step_name": next_step_name,
        "output_payload": output_payload,
        "error_message": error_message,
        "review": review,
        "artifacts": artifacts_list,
        "events": events,
    }


def build_worker_crash_result(*, run: dict[str, Any], step_run: dict[str, Any], error: Exception, hooks: Any) -> dict[str, Any]:
    step_name = str(step_run.get("step_name") or "unknown_step")
    step_dir = hooks.JOBS_ROOT / str(run.get("workflow_name") or "") / str(run.get("run_code") or run.get("id") or "backend-run") / f"{int(step_run.get('sequence_no') or 1):02d}_{step_name}"
    diagnostics = {
        "workflow_run_id": str(run.get("id") or ""),
        "workflow_step_run_id": str(step_run.get("id") or ""),
        "job_id": str(run.get("run_code") or ""),
        "step_dir": hooks._safe_relative_to(step_dir, hooks.JOBS_ROOT),
        "worker_error": repr(error),
    }
    step_dir.mkdir(parents=True, exist_ok=True)
    hooks._save_json(
        step_dir / "worker_error.json",
        {
            "step_name": step_name,
            "worker_error": repr(error),
            "diagnostics": diagnostics,
            "failed_at": hooks._now_iso(),
        },
    )
    return {
        "status": "failed",
        "outcome": "failed",
        "step_name": step_name,
        "coder_used": str(step_run.get("coder") or ""),
        "remark": f"Worker failed before execute-step completed: {error}",
        "artifacts": {},
        "meta_json_path": None,
        "review": None,
        "usage": None,
        "failure": {
            "failure_class": "SYSTEM_ERROR",
            "failure_code": "WORKER_EXECUTE_STEP_FAILED",
            "failure_reason": str(error),
            "failure_source": "worker",
        },
        "diagnostics": diagnostics,
    }
