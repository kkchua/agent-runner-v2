from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class ManualRunResolution:
    state: dict[str, Any]
    step: str | None
    original_current_step: str | None
    terminal_payload: dict[str, Any] | None = None


def _validate_daemon_claimed_step(*, mode: str, args: Any, state: dict[str, Any], step: str | None) -> None:
    if mode != "daemon":
        return
    claimed_step = str(getattr(args, "job", "") or "").strip()
    if not claimed_step:
        return
    current_step = str(state.get("current_step") or "").strip()
    if not current_step:
        raise ValueError(
            f"Daemon claimed step {claimed_step!r} but job {state['job_id']} has no current_step."
        )
    if claimed_step != current_step:
        raise ValueError(
            f"Daemon claimed step {claimed_step!r} but job {state['job_id']} is currently at {current_step!r}."
        )


def _apply_daemon_backend_linkage(*, mode: str, state: dict[str, Any]) -> bool:
    if mode != "daemon":
        return False

    changed = False
    workflow_run_id = str(os.environ.get("AGENT_RUNNER_WORKFLOW_RUN_ID") or "").strip()
    workflow_step_run_id = str(os.environ.get("AGENT_RUNNER_WORKFLOW_STEP_RUN_ID") or "").strip()
    backend_url = str(os.environ.get("AGENT_RUNNER_BACKEND_URL") or "").strip()

    if workflow_run_id and str(state.get("workflow_run_id") or "").strip() != workflow_run_id:
        state["workflow_run_id"] = workflow_run_id
        changed = True
    if workflow_step_run_id and str(state.get("workflow_step_run_id") or "").strip() != workflow_step_run_id:
        state["workflow_step_run_id"] = workflow_step_run_id
        changed = True
    if backend_url and str(state.get("backend_url") or "").strip() != backend_url:
        state["backend_url"] = backend_url
        changed = True

    return changed


def _load_backend_state_file() -> dict[str, Any] | None:
    """Load backend state from file if available (daemon mode only).
    
    The daemon writes the full backend run state to a file and sets
    AGENT_RUNNER_BACKEND_STATE_FILE env var pointing to it. This allows
    the CLI to initialize job.json from the latest backend state instead
    of creating from scratch.
    
    Returns None if file doesn't exist or can't be read.
    """
    import json
    from pathlib import Path
    
    backend_state_file = os.environ.get("AGENT_RUNNER_BACKEND_STATE_FILE", "").strip()
    if not backend_state_file:
        return None
    
    try:
        path = Path(backend_state_file)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return data
    except Exception:
        return None


def _initialize_state_from_backend(
    backend_state: dict[str, Any],
    group_cfg: dict[str, Any],
    seed_artifacts: dict[str, Any],
    mode: str,
    job_no: str,
    hooks: Any,
) -> dict[str, Any]:
    """Initialize job state from backend run state (daemon mode only).
    
    Extracts relevant fields from the backend run detail and creates
    a job.json state that reflects the current backend state. This ensures
    the CLI operates on the latest data, not stale claim data.
    
    Parameters
    ----------
    backend_state :
        Full backend run detail from get_run() API.
    group_cfg :
        Workflow group configuration.
    seed_artifacts :
        Input artifacts from --set flags.
    mode :
        Execution mode (should be "daemon").
    job_no :
        Backend run_code for folder naming.
    hooks :
        Runtime hooks for job state management.
    
    Returns
    -------
    dict
        Initialized job state.
    """
    run = backend_state.get("run") or {}
    
    # Create base job state
    state = hooks.create_job(
        group_name=run.get("workflow_name") or group_cfg.get("workflow_name", ""),
        group_cfg=group_cfg,
        seed_artifacts=seed_artifacts,
        mode=mode,
        job_no=job_no or run.get("run_code", ""),
    )
    
    # Merge backend state into job state
    if run.get("id"):
        state["workflow_run_id"] = str(run["id"])
    if run.get("current_step_run_id"):
        state["workflow_step_run_id"] = str(run["current_step_run_id"])
    if run.get("backend_url"):
        state["backend_url"] = str(run["backend_url"])
    
    # Merge artifacts from backend (if available)
    backend_artifacts = run.get("output_payload") or {}
    if backend_artifacts:
        for key, value in backend_artifacts.items():
            if value and key not in state.get("artifacts", {}):
                state.setdefault("artifacts", {})[key] = value
    
    # Merge context from backend (if available)
    context = run.get("context_payload") or {}
    if context:
        # Preserve __run_control for stop detection
        if "__run_control" in context:
            state.setdefault("context_payload", {})["__run_control"] = context["__run_control"]
    
    return state


def resolve_manual_run(*, args: Any, group_cfg: dict[str, Any], hooks: Any, mode: str = "manual") -> ManualRunResolution:
    if not args.job_id:
        seed_artifacts = hooks._parse_key_value_pairs(args.set)
        execution_binding = None
        if args.template_group == "task_execution_v1":
            if args.task_graph_id and args.task_node_id:
                execution_binding = hooks.build_task_execution_binding_from_ids(
                    task_graph_id=args.task_graph_id.strip(),
                    task_node_id=args.task_node_id.strip(),
                )
            elif seed_artifacts.get("TASK_FILE"):
                execution_binding = hooks._build_task_execution_binding_from_task_file(seed_artifacts["TASK_FILE"])
            else:
                raise ValueError(
                    "task_execution_v1 requires either --task-graph-id with --task-node-id or --set TASK_FILE=PATH."
                )

        resume_job_id = ""
        completed_job_id = ""
        if not args.new_job:
            if execution_binding is not None:
                seed_artifact_type, seed_artifact_path = hooks._task_execution_binding_identity(execution_binding)
            else:
                seed_artifact_type, seed_artifact_path = hooks.infer_seed_identity(args.template_group, seed_artifacts)
            if seed_artifact_type and seed_artifact_path:
                resume_job_id = hooks.find_matching_active_job(
                    group_name=args.template_group,
                    seed_artifact_type=seed_artifact_type,
                    seed_artifact_path=seed_artifact_path,
                ) or ""
                if not resume_job_id:
                    completed_job_id = hooks.find_matching_completed_job(
                        group_name=args.template_group,
                        seed_artifact_type=seed_artifact_type,
                        seed_artifact_path=seed_artifact_path,
                    ) or ""

        if resume_job_id:
            state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, resume_job_id))
            state = hooks.migrate_job_state(state)
            state = hooks.recover_exhausted_planning_job(state, group_cfg)
            state = hooks.reconcile_job_state(state, group_cfg)
            if _apply_daemon_backend_linkage(mode=mode, state=state):
                hooks.save_job(args.template_group, state["job_id"], state)
            original_current_step = state.get("current_step")
            if state.get("pending_human_approval_for"):
                raise ValueError(
                    f"Job {state['job_id']} is waiting for human approval of "
                    f"step {state['pending_human_approval_for']!r}."
                )
            step = args.job.strip() or state.get("current_step")
            _validate_daemon_claimed_step(mode=mode, args=args, state=state, step=step)
            if not step:
                return ManualRunResolution(
                    state=state,
                    step=None,
                    original_current_step=original_current_step,
                    terminal_payload={
                        "status": "APPROVED",
                        "remark": f"Job {state['job_id']} is already completed.",
                        "job_status": hooks.get_job_status(state),
                        "job_id": state["job_id"],
                        "current_step": state.get("current_step"),
                        "progress": hooks._step_progress_label(group_cfg, state.get("current_step")),
                        "status_summary": hooks._format_job_status_summary(state, group_cfg),
                    },
                )
            state = hooks.prepare_state_for_retry(group_name=args.template_group, state=state, step=step)
            return ManualRunResolution(state=state, step=step, original_current_step=original_current_step)

        if completed_job_id:
            state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, completed_job_id))
            state = hooks.migrate_job_state(state)
            state = hooks.reconcile_job_state(state, group_cfg)
            if _apply_daemon_backend_linkage(mode=mode, state=state):
                hooks.save_job(args.template_group, state["job_id"], state)
            return ManualRunResolution(
                state=state,
                step=None,
                original_current_step=state.get("current_step"),
                terminal_payload={
                    "status": "APPROVED",
                    "remark": (
                        f"Job {state['job_id']} for this seed is already completed. "
                        "Use --new-job only if you intentionally want a duplicate execution cycle."
                    ),
                    "job_status": hooks.get_job_status(state),
                    "job_id": state["job_id"],
                    "current_step": state.get("current_step"),
                    "progress": hooks._step_progress_label(group_cfg, state.get("current_step")),
                    "status_summary": hooks._format_job_status_summary(state, group_cfg),
                },
            )

        # Initialize job state: use backend state if available (daemon mode), otherwise create from scratch
        backend_state = _load_backend_state_file() if mode == "daemon" else None
        if backend_state:
            state = _initialize_state_from_backend(
                backend_state=backend_state,
                group_cfg=group_cfg,
                seed_artifacts=seed_artifacts,
                mode=mode,
                job_no=args.job_no,
                hooks=hooks,
            )
        else:
            state = hooks.create_job(args.template_group, group_cfg, seed_artifacts, mode=mode, job_no=args.job_no)
        
        if execution_binding is not None:
            hooks.apply_task_execution_binding(state, execution_binding)
            if not seed_artifacts.get("TASK_FILE"):
                state["artifacts"]["TASK_FILE"] = None
        _apply_daemon_backend_linkage(mode=mode, state=state)

        default_init_step = group_cfg["job_init_step"]
        start_step = getattr(args, "start_step", "").strip()

        if start_step:
            # Validate the start step exists in the workflow
            step_configs = group_cfg.get("step_configs", {})
            if start_step not in step_configs:
                raise ValueError(
                    f"--start-step {start_step!r} is not a valid step for "
                    f"template group {args.template_group!r}. "
                    f"Available steps: {list(step_configs.keys())}"
                )
            # Set current_step to the start step
            state["current_step"] = start_step
            # Mark all steps before the start step as completed
            step_order = group_cfg.get("steps", [])
            if start_step in step_order:
                start_idx = step_order.index(start_step)
                state["completed_steps"] = list(step_order[:start_idx])
            hooks.save_job(args.template_group, state["job_id"], state)
            original_current_step = start_step
            step = start_step
        else:
            hooks.save_job(args.template_group, state["job_id"], state)
            original_current_step = state.get("current_step")
            step = args.job.strip() or default_init_step
            if step != default_init_step:
                raise ValueError(
                    f"New job may only start with init step {default_init_step!r} "
                    f"for template group {args.template_group!r}"
                )
            missing_init = hooks._missing_artifacts(group_cfg.get("job_init_inputs", []), state)
            if missing_init:
                raise FileNotFoundError("Missing required job init input(s): " + ", ".join(missing_init))

        return ManualRunResolution(state=state, step=step, original_current_step=original_current_step)

    state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, args.job_id))
    state = hooks.migrate_job_state(state)
    state = hooks.recover_exhausted_planning_job(state, group_cfg)
    state = hooks.reconcile_job_state(state, group_cfg)
    if _apply_daemon_backend_linkage(mode=mode, state=state):
        hooks.save_job(args.template_group, state["job_id"], state)
    original_current_step = state.get("current_step")
    if state.get("pending_human_approval_for"):
        raise ValueError(
            f"Job {state['job_id']} is waiting for human approval of "
            f"step {state['pending_human_approval_for']!r}."
        )
    step = args.job.strip() or state.get("current_step")
    _validate_daemon_claimed_step(mode=mode, args=args, state=state, step=step)
    if not step:
        return ManualRunResolution(
            state=state,
            step=None,
            original_current_step=original_current_step,
            terminal_payload={
                "status": "APPROVED",
                "remark": f"Job {state['job_id']} is already completed.",
                "job_status": hooks.get_job_status(state),
                "job_id": state["job_id"],
                "current_step": state.get("current_step"),
                "progress": hooks._step_progress_label(group_cfg, state.get("current_step")),
                "status_summary": hooks._format_job_status_summary(state, group_cfg),
            },
        )
    state = hooks.prepare_state_for_retry(group_name=args.template_group, state=state, step=step)
    return ManualRunResolution(state=state, step=step, original_current_step=original_current_step)
