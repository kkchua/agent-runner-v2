from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from .execution_request import ExecutionRequest
from .execution_result import ExecutionFailure, ExecutionResult
from .state_defaults import default_loop_context, default_replan_context


def build_group_cfg_from_execution_spec(spec: dict[str, Any], template_group: str, step_name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    raw_config = dict(spec.get("raw_config") or {})
    required_inputs = [item.get("artifact_key") for item in spec.get("required_inputs") or [] if item.get("artifact_key")]
    optional_inputs = [item.get("artifact_key") for item in spec.get("optional_inputs") or [] if item.get("artifact_key")]
    immutable_inputs = [item.get("artifact_key") for item in spec.get("immutable_inputs") or [] if item.get("artifact_key")]
    produces = [item.get("artifact_key") for item in spec.get("produces") or [] if item.get("artifact_key")]
    updates = [item.get("artifact_key") for item in spec.get("updates") or [] if item.get("artifact_key")]
    step_cfg = dict(raw_config)
    step_cfg["prompt_file"] = spec.get("prompt_file")
    step_cfg["action"] = spec.get("action_name") or raw_config.get("action")
    step_cfg["edit_mode"] = spec.get("edit_mode")
    step_cfg["result_meta_key"] = spec.get("result_meta_key")
    step_cfg["result_meta_key_from_context"] = spec.get("result_meta_key_from_context")
    step_cfg["template_ref"] = spec.get("template_ref")
    step_cfg["required_inputs"] = required_inputs
    if optional_inputs:
        step_cfg["optional_inputs"] = optional_inputs
    if immutable_inputs:
        step_cfg["immutable_inputs"] = immutable_inputs
    step_cfg["produces"] = produces
    if updates:
        step_cfg["updates"] = updates
    target_artifact = spec.get("target_artifact")
    if target_artifact:
        step_cfg["target_artifact"] = target_artifact
    coder_policy = spec.get("coder_policy")
    if coder_policy:
        step_cfg["coder"] = {
            "default": coder_policy.get("default_coder"),
            "allowed": list(coder_policy.get("allowed_coders") or []),
            "must_differ_from_previous_step": bool(coder_policy.get("must_differ_from_previous_step")),
        }
    group_cfg = {
        "job_prefix": spec.get("job_prefix") or template_group,
        "job_init_step": spec.get("job_init_step") or step_name,
        "job_init_inputs": list(spec.get("job_init_inputs") or []),
        "default_max_rejects": int(spec.get("default_max_rejects") or 0),
        "reference_files": dict(spec.get("reference_files") or {}),
        "steps": [step_name],
        "step_configs": {step_name: step_cfg},
    }
    return group_cfg, step_cfg


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
        global_default_module = global_default_root / "template_groups.py"
        if global_default_module.exists():
            workflow_bundle_root = global_default_root
            workflow_module = hooks.load_workflow_module(workspace_root, "default", config=config)
        elif request.step_execution_spec:
            workflow_bundle_root = hooks.PACKAGE_ROOT.resolve()
        else:
            raise FileNotFoundError(
                f"Workflow bundle not found at {global_default_module}. "
                "Provide backend step_execution_spec or create %USERPROFILE%\\.ukbe-runner\\workflows\\default."
            )

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

    config_path = Path.home() / ".ukbe-runner" / "engine" / "config.json"
    if not config_path.exists():
        return None, None

    try:
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"[worker] failed to read engine config {config_path}: {exc}") from exc

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


def worker_command(
    *,
    backend_url: str,
    worker_id: str,
    host_name: str | None,
    poll_seconds: int,
    once: bool,
    engine_root: str | None = None,
    worker_label: str = "live",
    hooks: Any,
) -> int:
    effective_engine_root, engine_version = hooks._resolve_worker_engine_root(engine_root)
    if effective_engine_root:
        print(f"[worker] engine version: {engine_version!r}  root: {effective_engine_root}", flush=True)
    else:
        print("[worker] engine version: live source (no config.json or PYTHONPATH override)", flush=True)

    client = hooks.BackendClient(backend_url)
    client.register_worker(worker_id=worker_id, host_name=host_name, capabilities={"mode": ["execute-step"], "engine_version": engine_version}, worker_label=worker_label)

    while True:
        client.heartbeat(worker_id=worker_id, status="idle")
        claim = client.claim_step(worker_id=worker_id)
        step_run = claim.get("step_run")
        run = claim.get("run")
        if not step_run or not run:
            if once:
                return 0
            import time
            time.sleep(max(poll_seconds, 1))
            continue

        client.heartbeat(worker_id=worker_id, status="busy", current_step_run_id=step_run.get("id"))
        hooks._write_backend_job_json(run=run, step_run=step_run, last_event="STEP_CLAIMED")
        request_payload = hooks._build_worker_request_payload(run=run, step_run=step_run, step_execution_spec=claim.get("step_execution_spec"), backend_url=backend_url)
        try:
            result = hooks._invoke_execute_step_subprocess(request_payload, engine_root=effective_engine_root)
        except Exception as exc:
            result = hooks._build_worker_crash_result(run=run, step_run=step_run, error=exc)
        completion = hooks._submit_worker_result(client=client, run=run, step_run=step_run, result=result)
        hooks._finalize_worker_completion(client=client, run=run, step_run=step_run, completion=completion)
        client.heartbeat(worker_id=worker_id, status="idle", current_step_run_id=None)
        if once:
            return 0


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

    if mode in {"backend", "hybrid"}:
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
    try:
        group_cfg = hooks.get_template_group_cfg(
            template_group=template_group,
            workspace_root=workspace_path,
            workflow_name=workflow_name or "default",
        )
        steps = list(group_cfg.get("steps") or [])
        if step_name in steps:
            step_sequence_no = steps.index(step_name) + 1
        else:
            step_sequence_no = 1
    except Exception:
        step_sequence_no = spec.get("step_sequence_no") or step_run.get("sequence_no") or 1

    backend_step_dir_rel = str(
        hooks.JOBS_ROOT / template_group / job_id / f"{int(step_sequence_no):02d}_{step_name}"
    )
    return {
        "workflow_name": workflow_name,
        "template_group": spec.get("template_group") or workflow_name,
        "workflow_run_id": run.get("id"),
        "workflow_step_run_id": step_run.get("id"),
        "job_id": job_id,
        "step_name": step_name,
        "step_spec_source": mode,
        "project_root": project_root,
        "workspace_root": project_root,
        "target_project_root": run.get("project_root"),
        "coder_override": coder_override,
        "workflow_key_override": "",
        "env_overrides": {
            **(run.get("env_overrides") or {}),
            "BACKEND_URL": backend_url,
            "WORKFLOW_STEP_RUN_ID": str(step_run.get("id") or ""),
        },
        "input_artifacts": input_artifacts,
        "context_payload": context_payload,
        "state_overrides": {"backend_step_dir_rel": backend_step_dir_rel},
        "step_execution_spec": spec,
    }


def invoke_execute_step_subprocess(request_payload: dict[str, Any], engine_root: str | None = None, *, hooks: Any) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="agent-runner-v2-") as temp_dir:
        req_path = Path(temp_dir) / "request.json"
        res_path = Path(temp_dir) / "result.json"
        req_path.write_text(json.dumps(request_payload, indent=2), encoding="utf-8")
        module = "agent_runner_v2.run_agent"
        cmd = [sys.executable, "-m", module, "execute-step", "--request-file", str(req_path), "--result-file", str(res_path)]
        env = os.environ.copy()

        project_root = request_payload.get("project_root") or request_payload.get("workspace_root")
        cwd = Path(project_root).resolve() if project_root else None

        if engine_root:
            env["PYTHONPATH"] = str(Path(engine_root) / "agent_runner_v2") + os.pathsep + env.get("PYTHONPATH", "")
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd)
        if not res_path.exists():
            print(f"[invoke_execute_step_subprocess] FULL STDERR:\n{proc.stderr}", flush=True)
            raise RuntimeError(f"execute-step did not write result file; rc={proc.returncode}\nFull stderr:\n{proc.stderr[-2000:]}")
        payload = json.loads(res_path.read_text(encoding="utf-8"))
        payload.setdefault("diagnostics", {})["subprocess_return_code"] = proc.returncode
        payload["diagnostics"]["stdout"] = proc.stdout[-2000:]
        payload["diagnostics"]["stderr"] = proc.stderr[-2000:]
        return payload


def job_json_path(*, workflow_name: str, run_code: str, hooks: Any) -> Path:
    return hooks.JOBS_ROOT / workflow_name / run_code / "job.json"


def write_backend_job_json(
    *,
    run: dict[str, Any],
    step_run: dict[str, Any] | None = None,
    next_step_run: dict[str, Any] | None = None,
    last_event: str | None = None,
    hooks: Any,
) -> None:
    workflow_name = str(run.get("workflow_name") or "")
    run_code = str(run.get("run_code") or "")
    if not workflow_name or not run_code:
        return

    payload: dict[str, Any] = {
        "run_id": run.get("id"),
        "run_code": run_code,
        "workflow_name": workflow_name,
        "status": run.get("status"),
        "current_step_name": run.get("current_step_name"),
        "current_step_run_id": run.get("current_step_run_id"),
        "awaiting_human_step": run.get("awaiting_human_step"),
        "target_worker_id": run.get("target_worker_id"),
        "claimed_by_worker": run.get("claimed_by_worker"),
        "project_root": run.get("project_root"),
        "context_payload": dict(run.get("context_payload") or {}),
        "submitted_at": run.get("submitted_at"),
        "started_at": run.get("started_at"),
        "completed_at": run.get("completed_at"),
        "error_message": run.get("error_message"),
        "updated_at": hooks._now_iso(),
    }
    if step_run:
        payload["current_step_status"] = step_run.get("status")
        payload["current_step_outcome"] = step_run.get("outcome")
        payload["current_step_coder"] = step_run.get("coder")
    if next_step_run:
        payload["next_step_name"] = next_step_run.get("step_name")
        payload["next_step_run_id"] = next_step_run.get("id")
    if last_event:
        payload["last_event"] = last_event

    path = hooks._job_json_path(workflow_name=workflow_name, run_code=run_code)
    path.parent.mkdir(parents=True, exist_ok=True)
    hooks._save_json(path, payload)


def submit_worker_result(*, client: Any, run: dict[str, Any], step_run: dict[str, Any], result: dict[str, Any], hooks: Any) -> dict[str, Any]:
    normalized_artifacts: dict[str, str] = {}
    for artifact_key, file_path in (result.get("artifacts") or {}).items():
        normalized_artifacts[artifact_key] = str(file_path).replace("\\", "/")

    diagnostics = dict(result.get("diagnostics") or {})
    artifact_errors: list[dict[str, str]] = []
    for artifact_key, file_path in normalized_artifacts.items():
        try:
            client.create_artifact(
                run_id=str(run["id"]),
                payload={
                    "artifact_key": artifact_key,
                    "file_path": file_path,
                    "role": "output",
                    "workflow_step_run_id": str(step_run["id"]),
                    "details": {},
                },
            )
        except Exception as exc:
            artifact_errors.append({"artifact_key": artifact_key, "file_path": file_path, "error": str(exc)})

    review = result.get("review")
    next_step = result.get("next_step")
    complete_payload: dict[str, Any] = {
        "status": result.get("status", "failed"),
        "outcome": result.get("outcome"),
        "coder": result.get("coder_used"),
        "output_payload": normalized_artifacts,
        "error_message": (result.get("failure") or {}).get("failure_reason"),
    }
    if review:
        complete_payload["review"] = review
    if next_step:
        complete_payload["next_step"] = next_step
    completion = client.complete_step_run(step_run_id=str(step_run["id"]), payload=complete_payload)

    event_payload = {
        "event_type": "WORKER_RESULT",
        "message": result.get("remark") or result.get("outcome") or result.get("status"),
        "workflow_step_run_id": str(step_run["id"]),
        "payload": {
            "failure": result.get("failure"),
            "diagnostics": diagnostics,
            "meta_json_path": result.get("meta_json_path"),
            "usage": result.get("usage"),
        },
    }
    if artifact_errors:
        event_payload["payload"]["artifact_registration_errors"] = artifact_errors
    client.create_event(run_id=str(run["id"]), payload=event_payload)
    return completion


def finalize_worker_completion(*, client: Any, run: dict[str, Any], step_run: dict[str, Any], completion: dict[str, Any] | None, hooks: Any) -> dict[str, Any]:
    completion_run = dict((completion or {}).get("run") or run)
    completion_step_run = dict((completion or {}).get("step_run") or step_run)
    next_step_run = (completion or {}).get("next_step_run")
    last_event = "STEP_COMPLETED"

    terminal_statuses = {"awaiting_human", "failed", "completed"}
    run_id = str(run.get("id") or "")
    if completion_run.get("status") not in terminal_statuses and next_step_run is None and run_id:
        try:
            refreshed_run = client.get_run(run_id=run_id)
            if isinstance(refreshed_run, dict) and refreshed_run:
                completion_run = refreshed_run
        except Exception as exc:
            print(f"[worker] WARNING: Failed to refresh run state for notification handling: {exc}", flush=True)

    is_last_step = next_step_run is None
    if completion_run.get("status") == "awaiting_human":
        last_event = "HUMAN_APPROVAL_REQUIRED"
        print(f"[worker] Attempting to send WAITING_FOR_HUMAN_INTERVENTION notification for run {completion_run.get('id', 'unknown')}", flush=True)
        from .notification_manager import send_workflow_notification
        notify_result = send_workflow_notification("WAITING_FOR_HUMAN_INTERVENTION", completion_run)
        print(f"[worker] Notification result: {notify_result}", flush=True)
    elif completion_run.get("status") == "failed":
        last_event = "RUN_FAILED"
        print(f"[worker] Attempting to send FAILED notification for run {completion_run.get('id', 'unknown')}", flush=True)
        from .notification_manager import send_workflow_notification
        notify_result = send_workflow_notification("FAILED", completion_run)
        print(f"[worker] Notification result: {notify_result}", flush=True)
    elif completion_run.get("status") == "completed" and is_last_step:
        last_event = "RUN_COMPLETED"
        print(f"[worker] Workflow completed (last step). Sending COMPLETED notification for run {completion_run.get('id', 'unknown')}", flush=True)
        from .notification_manager import send_workflow_notification
        notify_result = send_workflow_notification("COMPLETED", completion_run)
        print(f"[worker] Notification result: {notify_result}", flush=True)
    elif next_step_run:
        last_event = "STEP_ENQUEUED"
        print(f"[worker] Step completed, next step enqueued: {next_step_run.get('step_name', 'unknown')}", flush=True)
    else:
        print(
            f"[worker] WARNING: Run completion state is non-terminal after final step. "
            f"status={completion_run.get('status')!r}, next_step_run={next_step_run!r}",
            flush=True,
        )

    hooks._write_backend_job_json(
        run=completion_run,
        step_run=completion_step_run,
        next_step_run=next_step_run if isinstance(next_step_run, dict) else None,
        last_event=last_event,
    )
    return {
        "run": completion_run,
        "step_run": completion_step_run,
        "next_step_run": next_step_run,
        "last_event": last_event,
    }


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
        artifacts=published_artifacts,
        meta_json_path=step_result.meta_json_path,
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
