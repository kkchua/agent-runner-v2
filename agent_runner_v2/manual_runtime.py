from __future__ import annotations

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

        state = hooks.create_job(args.template_group, group_cfg, seed_artifacts, mode=mode, job_no=args.job_no)
        if execution_binding is not None:
            hooks.apply_task_execution_binding(state, execution_binding)
            if not seed_artifacts.get("TASK_FILE"):
                state["artifacts"]["TASK_FILE"] = None
        hooks.save_job(args.template_group, state["job_id"], state)
        original_current_step = state.get("current_step")
        default_init_step = group_cfg["job_init_step"]
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
