"""[V1 DEPRECATED] Backend execution — V1 sync and execution logic.

→ Replaced by: agent_runner_v2/v2/sync.py (outcome-only sync)
→ Architecture: docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260801-002_platform-v2-architecture-redesign.md
"""
from __future__ import annotations
from pathlib import Path
from typing import Any

from .execution_request import ExecutionRequest
from .execution_result import ExecutionFailure, ExecutionResult
from .runtime_context import JOBS_ROOT, format_report_artifacts, format_report_path
from .state_defaults import default_loop_context, default_replan_context


def build_group_cfg_from_execution_spec(spec: dict[str, Any], template_group: str, step_name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build group and step config from execution spec.
    
    This is a compatibility wrapper that delegates to workflow_runtime module.
    The actual bundle resolution logic lives in workflow_runtime to ensure parity
    between manual and daemon execution modes.
    """
    from .workflow_runtime import _build_group_cfg_from_spec
    return _build_group_cfg_from_spec(spec, template_group, step_name)


def execute_step_command(request_path: Path, result_path: Path | None = None, *, hooks: Any) -> int:
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    request = ExecutionRequest.from_dict(payload)

    try:
        workspace_root = Path(request.workspace_root or request.project_root).resolve()
        config = hooks.load_project_config(workspace_root)
        workflow_name = request.workflow_name or str(config.get("default_workflow") or "default")
        workflow_cfg_map = config.get("workflows") or {}
        bundle_workflow_name = workflow_name if workflow_name in workflow_cfg_map else str(config.get("default_workflow") or "default")

        workflow_module = None
        global_default_root = hooks.resolve_workflow_root(workspace_root, "default", config=config)
        try:
            workflow_module = hooks.load_workflow_module(workspace_root, "default", config=config)
            workflow_bundle_root = global_default_root
        except FileNotFoundError:
            if not request.step_execution_spec:
                raise FileNotFoundError(
                    f"Workflow bundle not found under {global_default_root}. "
                    "Provide backend step_execution_spec or create %USERPROFILE%\\.ukbe-runner\\workflows\\default."
                )
            workflow_bundle_root = hooks.PACKAGE_ROOT.resolve()

        delivery_root = Path(request.target_project_root).resolve() if request.target_project_root else None
        if delivery_root is not None and (
            request.template_group.startswith("delivery_scaffold")
            or request.template_group.startswith("codebase_")
            or request.template_group.startswith("system_docs_")
        ):
            hooks._ensure_delivery_folders(delivery_root)

        hooks.set_context(
            workspace_root=workspace_root,
            workflow_name=workflow_name,
            workflow_root=workflow_bundle_root,
            workflow_module=workflow_module,
            delivery_root=delivery_root,
        )
        hooks.set_workflow_module(workflow_module)
        effective_root = delivery_root if delivery_root is not None else workspace_root

        spec_source = (request.step_spec_source or "backend").strip().lower()
        if spec_source == "global":
            group_cfg = hooks._load_group(request.template_group, workspace_root=workspace_root, workflow_root=workflow_bundle_root)
            step_cfg = group_cfg["step_configs"].get(request.step_name)
            if not step_cfg:
                raise ValueError(f"Step {request.step_name!r} is not defined for template group {request.template_group!r}")
            request.step_execution_spec = hooks.build_step_execution_spec(
                template_group=request.template_group,
                step_name=request.step_name,
                group_cfg=group_cfg,
            )
        elif request.step_execution_spec:
            if spec_source == "hybrid":
                try:
                    request.step_execution_spec = hooks.reconcile_step_execution_spec(
                        template_group=request.template_group,
                        step_name=request.step_name,
                        workspace_root=workspace_root,
                        workflow_name=bundle_workflow_name or "default",
                        backend_spec=dict(request.step_execution_spec or {}),
                    )
                except Exception:
                    pass
            group_cfg, step_cfg = hooks._build_group_cfg_from_execution_spec(
                request.step_execution_spec,
                request.template_group,
                request.step_name,
            )
        else:
            group_cfg = hooks._load_group(request.template_group, workspace_root=workspace_root, workflow_root=workflow_bundle_root)
            step_cfg = group_cfg["step_configs"].get(request.step_name)
            if not step_cfg:
                raise ValueError(f"Step {request.step_name!r} is not defined for template group {request.template_group!r}")
        hooks._validate_static_reference_files(workspace_root, group_cfg, template_group=request.template_group)

        state = hooks._build_execution_state(request=request, group_cfg=group_cfg)
        hooks.save_job(request.template_group, state["job_id"], state)

        old_env: dict[str, str | None] = {}
        try:
            for key, value in request.env_overrides.items():
                old_env[key] = os.environ.get(key)
                os.environ[key] = value
            result = hooks._execute_backend_step_request(
                request=request,
                group_cfg=group_cfg,
                step_cfg=step_cfg,
                state=state,
                effective_root=effective_root,
            )
        finally:
            for key, previous in old_env.items():
                if previous is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = previous

        result_payload = result.to_dict()
        state["artifacts"].update(dict(result.artifacts or {}))
        if result.failure is not None:
            state["last_failure_class"] = result.failure.failure_class
            state["last_failure_code"] = result.failure.failure_code
            state["last_failure_reason"] = result.failure.failure_reason
            state["last_failure_source"] = result.failure.failure_source
        else:
            state["last_failure_class"] = None
            state["last_failure_code"] = None
            state["last_failure_reason"] = None
            state["last_failure_source"] = None
        hooks.save_job(request.template_group, state["job_id"], state)
        if result_path is not None:
            result_path.write_text(json.dumps(result_payload, indent=2), encoding="utf-8")
        print(json.dumps(result_payload, indent=2))
        return 0 if result.status == "completed" else 1
    except Exception as exc:
        step_order = 1
        if isinstance(request.step_execution_spec, dict):
            step_order = int(request.step_execution_spec.get("step_order") or request.step_execution_spec.get("step_sequence_no") or 1)
        crash_result = hooks._build_worker_crash_result(
            run={
                "id": request.workflow_run_id or "",
                "run_code": request.job_id or "",
                "workflow_name": request.template_group,
            },
            step_run={
                "id": request.workflow_step_run_id or "",
                "step_name": request.step_name,
                "sequence_no": step_order,
                "coder": request.coder_override or "",
            },
            error=exc,
        )
        if result_path is not None:
            result_path.write_text(json.dumps(crash_result, indent=2), encoding="utf-8")
        print(json.dumps(crash_result, indent=2))
        return 1


def build_execution_state(*, request: ExecutionRequest, group_cfg: dict[str, Any], hooks: Any) -> dict[str, Any]:
    bundle = hooks.get_workflow_module()
    if bundle is None:
        raise RuntimeError("Workflow module is not loaded. Runtime must use the global workflow bundle.")
    artifact_keys = list(bundle.ARTIFACT_KEYS)
    artifacts: dict[str, Any] = {key: None for key in artifact_keys}
    artifacts.update(dict(request.input_artifacts))

    step_index = 1
    try:
        step_index = list(group_cfg.get("steps") or []).index(request.step_name) + 1
    except ValueError:
        step_index = 1

    step_order = (request.step_execution_spec or {}).get("step_order", step_index)
    step_sequence = (request.step_execution_spec or {}).get("step_sequence_no", step_index)

    backend_ctx = dict(request.context_payload)
    task_binding = hooks.default_task_execution_binding()
    current_item = backend_ctx.get("current_item") if isinstance(backend_ctx.get("current_item"), dict) else {}
    ctx_task_node_id = (current_item.get("task_node_id") or backend_ctx.get("CURRENT_TASK_NODE_ID") or "").strip()
    ctx_task_graph_file = (backend_ctx.get("TASK_GRAPH_FILE") or "").strip()
    if ctx_task_graph_file and ctx_task_node_id and request.template_group == "task_execution_v1":
        try:
            from .task_runtime import build_task_execution_binding
            task_binding = build_task_execution_binding(task_graph_file=ctx_task_graph_file, task_node_id=ctx_task_node_id)
            if not task_binding.get("task_graph_id"):
                task_binding["task_graph_id"] = backend_ctx.get("SOURCE_TASK_GRAPH_ID")
        except Exception as bind_exc:
            raise RuntimeError(f"[_build_execution_state] could not build task execution binding: {bind_exc}") from bind_exc
    else:
        task_binding["task_node_id"] = ctx_task_node_id or None
        task_binding["task_title"] = current_item.get("title") or backend_ctx.get("CURRENT_TASK_TITLE")
        task_binding["task_graph_id"] = backend_ctx.get("SOURCE_TASK_GRAPH_ID")
        task_binding["task_graph_file"] = ctx_task_graph_file or None
        task_binding["plan_file"] = backend_ctx.get("PLAN_FILE")
        task_binding["plan_id"] = backend_ctx.get("PLAN_ID")

    state: dict[str, Any] = {
        "job_id": str(request.job_id or request.workflow_run_id or "backend-job"),
        "template_group": request.template_group,
        "project_root": str(request.project_root or ""),
        "workspace_path": str(request.workspace_root or request.project_root or ""),
        "target_project_root": str(request.target_project_root or request.project_root or ""),
        "runner_version": "v2",
        "job_init_step": group_cfg.get("job_init_step"),
        "job_status": "IN_PROGRESS",
        "status": "IN_PROGRESS",
        "current_step": request.step_name,
        "completed_steps": [],
        "failed_steps": [],
        "reject_counts": {},
        "step_coders": {},
        "step_usage": {},
        "usage_summary": hooks.default_usage_summary(),
        "pending_human_approval_for": None,
        "human_approvals": {},
        "model_approved_steps": [],
        "review_state": hooks.default_review_state(),
        "last_model_output": None,
        "retry_history": [],
        "pending_intervention_for": None,
        "last_failure_class": None,
        "last_failure_code": None,
        "last_failure_reason": None,
        "last_failure_source": None,
        "auto_retry_count_by_step": {},
        "human_retry_count_by_step": {},
        "failure_history": [],
        "seed_artifact_type": None,
        "seed_artifact_path": None,
        "created_at": hooks._now_iso(),
        "updated_at": hooks._now_iso(),
        "artifacts": artifacts,
        "loop_context": default_loop_context(),
        "loop_history": [],
        "replan_context": default_replan_context(),
        "replan_history": [],
        "planning_attempt_count": 0,
        "recovered_from_invalid_result": False,
        "recovery_code": None,
        "recovery_source": None,
        "task_generation_state_version": 1,
        "task_generation_state": None,
        "task_execution_binding": task_binding,
        "state_schema_version": hooks.CURRENT_SCHEMA_VERSION,
        "repair_history": [],
        "reconciled_from_failure": None,
        "workflow_run_id": request.workflow_run_id,
        "workflow_step_run_id": request.workflow_step_run_id,
        "backend_context_payload": dict(request.context_payload),
        "backend_artifact_rules": dict((request.step_execution_spec or {}).get("artifact_rules") or {}),
        "backend_step_order": step_order,
        "backend_step_sequence": step_sequence,
        "backend_step_dir_rel": str(
            hooks.JOBS_ROOT
            / request.template_group
            / str(request.job_id or request.workflow_run_id or "backend-job")
            / f"{step_sequence:02d}_{request.step_name}"
        ),
    }
    state.update(request.state_overrides)
    return state


def publish_backend_artifacts(*, state: dict[str, Any], step: str, artifacts: dict[str, str], project_root: Path, hooks: Any) -> dict[str, str]:
    rules = state.get("backend_artifact_rules") or {}
    if isinstance(rules, dict) and rules:
        published = dict(artifacts)
        for artifact_key, source_rel in artifacts.items():
            rule = rules.get(artifact_key)
            if not isinstance(rule, dict):
                continue
            final_rel = rule.get("final_path_template")
            publish_mode = str(rule.get("publish_mode") or "none")
            publish_on_status = str(rule.get("publish_on_status") or "approved")
            if not final_rel or publish_mode == "none" or publish_on_status not in {"approved", "completed", "always"}:
                continue
            source_path = (project_root / source_rel).resolve()
            target_path = (project_root / str(final_rel)).resolve()
            if source_path == target_path:
                published[artifact_key] = str(final_rel)
                continue
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if publish_mode == "move":
                shutil.move(str(source_path), str(target_path))
            else:
                shutil.copy2(source_path, target_path)
            published[artifact_key] = str(final_rel)
        return published

    if step not in {"project_analysis", "generate_sop", "generate_templates"}:
        return dict(artifacts)

    published = dict(artifacts)
    for artifact_key, source_rel in artifacts.items():
        target_rel = hooks.DELIVERY_SCAFFOLD_PUBLISH_PATHS.get(artifact_key)
        if not target_rel:
            continue
        source_path = (project_root / source_rel).resolve()
        target_path = (project_root / target_rel).resolve()
        if source_path == target_path:
            published[artifact_key] = target_rel
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        published[artifact_key] = target_rel
    return published


def execute_backend_step_request(
    *,
    request: ExecutionRequest,
    group_cfg: dict[str, Any],
    step_cfg: dict[str, Any],
    state: dict[str, Any],
    effective_root: Path,
    hooks: Any,
) -> ExecutionResult:
    step = request.step_name
    coder_used = "action"

    try:
        prepared = hooks._prepare_step_execution(
            template_group=request.template_group,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            project_root=effective_root,
            workflow_key_override=request.workflow_key_override or "",
            cli_coder=request.coder_override or None,
        )
        coder_used = prepared.coder_used
    except hooks.PreflightBlockedError as exc:
        failure = ExecutionFailure(
            failure_class="HUMAN_RETRY_REQUIRED",
            failure_code="PREFLIGHT_STATUS_NOT_APPROVED",
            failure_reason=str(exc),
            failure_source="runner",
        )
        return ExecutionResult(status="failed", outcome="preflight_blocked", step_name=step, coder_used=coder_used, failure=failure)
    except Exception as exc:
        envelope = hooks.classify_pre_run_failure(exc)
        failure = ExecutionFailure(
            failure_class=envelope["failure_class"],
            failure_code=envelope["failure_code"],
            failure_reason=envelope["failure_reason"],
            failure_source=envelope["failure_source"],
        )
        return ExecutionResult(status="failed", outcome="failed", step_name=step, coder_used=coder_used, failure=failure)

    attempt = hooks.invoke_prepared_step(
        executor=hooks._execute_prepared_step,
        prepared=prepared,
        template_group=request.template_group,
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        effective_root=effective_root,
    )
    if attempt.failure is not None:
        failure = ExecutionFailure(
            failure_class=attempt.failure.failure_class,
            failure_code=attempt.failure.failure_code,
            failure_reason=attempt.failure.failure_reason,
            failure_source=attempt.failure.failure_source,
        )
        return ExecutionResult(status="failed", outcome="failed", step_name=step, coder_used=coder_used, failure=failure)

    assert attempt.step_result is not None
    step_result = attempt.step_result

    review = None
    if step_cfg and step_cfg.get("on_reject_refine"):
        review = {
            "decision": step_result.status.lower(),
            "remark": step_result.remark,
            "reject_code": step_result.reject_code,
        }
        if review["decision"] == "rejected":
            reject_target = ((step_cfg.get("on_reject_refine") or {}).get("artifact") or "").strip()
            if reject_target:
                artifact_path = state.get("artifacts", {}).get(reject_target)
                if artifact_path:
                    hooks._update_document_status(file_path=artifact_path, new_status="changes_requested")

    produced_status = step_cfg.get("produced_document_status") or {}
    produced_artifact = str(produced_status.get("artifact") or "").strip()
    produced_required_status = str(produced_status.get("required_status") or "").strip()
    if produced_artifact and produced_required_status:
        artifact_path = (step_result.artifacts or {}).get(produced_artifact) or state.get("artifacts", {}).get(produced_artifact)
        if artifact_path:
            hooks._update_document_status(file_path=artifact_path, new_status=produced_required_status)

    published_artifacts = hooks._publish_backend_artifacts(
        state=state,
        step=step,
        artifacts=step_result.artifacts,
        project_root=effective_root,
    )

    next_step = hooks.predict_next_step_after_approved(
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
    )

    return ExecutionResult(
        status="completed",
        outcome=step_result.status.lower(),
        step_name=step,
        coder_used=coder_used,
        remark=step_result.remark,
        artifacts=format_report_artifacts(
            published_artifacts,
            project_root=effective_root,
            runtime_root=JOBS_ROOT,
        ),
        meta_json_path=format_report_path(
            step_result.meta_json_path,
            project_root=effective_root,
            runtime_root=JOBS_ROOT,
        ),
        review=review,
        usage=step_result.usage_data,
        diagnostics={
            "workflow_run_id": request.workflow_run_id,
            "workflow_step_run_id": request.workflow_step_run_id,
            "job_id": state.get("job_id"),
            "step_dir": hooks._safe_relative_to(prepared.step_dir, hooks.JOBS_ROOT),
        },
        next_step=next_step,
    )
