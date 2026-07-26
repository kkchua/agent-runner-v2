from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from .backend_client import BackendClient
from .config_loader import load_runner_config
from .daemon_runtime import build_job_sync_payload
from .state_defaults import default_loop_context, default_replan_context


@dataclass
class AdminCommandResolution:
    handled: bool
    exit_code: int = 0
    continue_execution: bool = False
    state: dict[str, Any] | None = None
    step: str | None = None


def _sync_backend_after_human_approval(*, state: dict[str, Any]) -> str | None:
    step_run_id = str(state.get("workflow_step_run_id") or "").strip()
    if not step_run_id:
        return None

    cfg = load_runner_config()
    backend_url = (
        str(state.get("backend_url") or "").strip()
        or os.environ.get("AGENT_RUNNER_BACKEND_URL")
        or str(cfg.get("backend_url") or "").strip()
    )
    if not backend_url:
        return "backend sync skipped: backend_url not configured"

    last_model_output = state.get("last_model_output") or {}
    step_result = {
        "status": str(last_model_output.get("status") or "APPROVED"),
        "outcome": "approved",
        "coder_used": last_model_output.get("coder_used"),
        "remark": last_model_output.get("remark"),
        "artifacts": dict(last_model_output.get("artifacts") or {}),
    }
    payload = build_job_sync_payload(
        job=state,
        step_result=step_result,
        step_run_id=step_run_id,
    )
    BackendClient(backend_url).sync_job_state(step_run_id=step_run_id, payload=payload)
    return None


def _sync_backend_after_override_step(*, state: dict[str, Any], step_name: str) -> str | None:
    run_id = str(state.get("workflow_run_id") or "").strip()
    if not run_id:
        return None

    cfg = load_runner_config()
    backend_url = (
        str(state.get("backend_url") or "").strip()
        or os.environ.get("AGENT_RUNNER_BACKEND_URL")
        or str(cfg.get("backend_url") or "").strip()
    )
    if not backend_url:
        return "backend sync skipped: backend_url not configured"

    BackendClient(backend_url).reset_run_step(run_id=run_id, step_name=step_name)
    return None


def _should_resync_completed_job(*, state: dict[str, Any], requested_step: str) -> bool:
    pending = str(state.get("pending_human_approval_for") or "").strip()
    if pending:
        return False
    completed_steps = {str(step).strip() for step in list(state.get("completed_steps") or [])}
    return (
        str(state.get("workflow_step_run_id") or "").strip() != ""
        and requested_step in completed_steps
        and state.get("current_step") is None
        and str(state.get("job_status") or state.get("status") or "").strip().upper() == "COMPLETED"
    )


def handle_admin_command(*, args: Any, group_cfg: dict[str, Any], hooks: Any) -> AdminCommandResolution:
    if args.single_step:
        if not args.job_id:
            raise ValueError("--single-step requires --job-id")
        if not args.job:
            raise ValueError("--single-step requires --job <step_name>")
        state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, args.job_id))
        state = hooks.migrate_job_state(state)
        state = hooks.reconcile_job_state(state, group_cfg)
        step = args.job.strip()
        step_cfg = group_cfg["step_configs"].get(step)
        if not step_cfg:
            raise ValueError(f"Step {step!r} is not defined for template group {args.template_group!r}")
        state["loop_context"] = default_loop_context()
        state["replan_context"] = default_replan_context()
        state["current_step"] = step
        state.setdefault("reject_counts", {})[step] = state.get("reject_counts", {}).get(step, 0)
        hooks.save_job(args.template_group, state["job_id"], state)
        return AdminCommandResolution(handled=True, continue_execution=True, state=state, step=step)

    if args.show_job:
        if not args.job_id:
            raise ValueError("--show-job requires --job-id")
        state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, args.job_id))
        state = hooks.migrate_job_state(state)
        state = hooks.reconcile_job_state(state, group_cfg)
        print(json.dumps(state, indent=2))
        return AdminCommandResolution(handled=True, exit_code=0)

    if args.check_job_status:
        if not args.job_id:
            raise ValueError("--check-job-status requires --job-id")
        state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, args.job_id))
        state = hooks.migrate_job_state(state)
        state = hooks.reconcile_job_state(state, group_cfg)
        print(hooks._format_job_status_summary(state, group_cfg))
        return AdminCommandResolution(handled=True, exit_code=0)

    if args.approve_step:
        if not args.job_id:
            raise ValueError("--approve-step requires --job-id")
        state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, args.job_id))
        state = hooks.migrate_job_state(state)
        state = hooks.reconcile_job_state(state, group_cfg)
        requested_step = args.approve_step.strip()
        current_status = hooks.get_job_status(state)
        # Auto-detect intervention/maxretried and delegate to resume_step
        if current_status in ("WAITING_FOR_HUMAN_INTERVENTION", "WAITING_FOR_HUMAN_MAXRETRIED"):
            state = hooks.resume_step(
                group_name=args.template_group,
                group_cfg=group_cfg,
                state=state,
                step=requested_step,
            )
            sync_warning = _sync_backend_after_human_approval(state=state)
            remark = (
                f"Step {requested_step!r} resumed (was {current_status})."
                if not sync_warning
                else f"Step {requested_step!r} resumed (was {current_status}); {sync_warning}."
            )
            print(json.dumps({
                "status": "APPROVED",
                "remark": remark,
                "job_status": hooks.get_job_status(state),
                "job_id": state["job_id"],
                "current_step": state["current_step"],
            }, indent=2))
            return AdminCommandResolution(handled=True, exit_code=0)
        try:
            state = hooks.approve_step(
                group_name=args.template_group,
                group_cfg=group_cfg,
                state=state,
                step=requested_step,
            )
            sync_warning = _sync_backend_after_human_approval(state=state)
            remark = (
                f"Human approval recorded for step {requested_step!r}."
                if not sync_warning
                else f"Human approval recorded for step {requested_step!r}; {sync_warning}."
            )
        except ValueError:
            if not _should_resync_completed_job(state=state, requested_step=requested_step):
                raise
            sync_warning = _sync_backend_after_human_approval(state=state)
            remark = (
                f"Job was already locally completed after human approval; backend status resynced for step {requested_step!r}."
                if not sync_warning
                else f"Job was already locally completed after human approval for step {requested_step!r}; {sync_warning}."
            )
        print(json.dumps({
            "status": "APPROVED",
            "remark": remark,
            "job_status": hooks.get_job_status(state),
            "job_id": state["job_id"],
            "current_step": state["current_step"],
        }, indent=2))
        return AdminCommandResolution(handled=True, exit_code=0)

    if args.reject_step:
        if not args.job_id:
            raise ValueError("--reject-step requires --job-id")
        state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, args.job_id))
        state = hooks.migrate_job_state(state)
        state = hooks.reconcile_job_state(state, group_cfg)
        requested_step = args.reject_step.strip()
        state = hooks.reject_step(
            group_name=args.template_group,
            group_cfg=group_cfg,
            state=state,
            step=requested_step,
        )
        sync_warning = _sync_backend_after_human_approval(state=state)
        remark = (
            f"Step {requested_step!r} rejected — routed to refine step."
            if not sync_warning
            else f"Step {requested_step!r} rejected — routed to refine step; {sync_warning}."
        )
        print(json.dumps({
            "status": "REJECTED",
            "remark": remark,
            "job_status": hooks.get_job_status(state),
            "job_id": state["job_id"],
            "current_step": state["current_step"],
        }, indent=2))
        return AdminCommandResolution(handled=True, exit_code=0)

    if args.resume_step:
        if not args.job_id:
            raise ValueError("--resume-step requires --job-id")
        state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, args.job_id))
        state = hooks.migrate_job_state(state)
        state = hooks.reconcile_job_state(state, group_cfg)
        requested_step = args.resume_step.strip()
        state = hooks.resume_step(
            group_name=args.template_group,
            group_cfg=group_cfg,
            state=state,
            step=requested_step,
        )
        sync_warning = _sync_backend_after_human_approval(state=state)
        print(json.dumps({
            "status": "APPROVED",
            "remark": (
                f"Step {requested_step!r} resumed — advancing to next step."
                if not sync_warning
                else f"Step {requested_step!r} resumed — advancing to next step; {sync_warning}."
            ),
            "job_status": hooks.get_job_status(state),
            "job_id": state["job_id"],
            "current_step": state["current_step"],
        }, indent=2))
        return AdminCommandResolution(handled=True, exit_code=0)

    if args.retry_step:
        if not args.job_id:
            raise ValueError("--retry-step requires --job-id")
        state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, args.job_id))
        state = hooks.migrate_job_state(state)
        state = hooks.reconcile_job_state(state, group_cfg)
        requested_step = args.retry_step.strip()
        state = hooks.retry_step(
            group_name=args.template_group,
            group_cfg=group_cfg,
            state=state,
            step=requested_step,
        )
        sync_warning = _sync_backend_after_human_approval(state=state)
        print(json.dumps({
            "status": "APPROVED",
            "remark": (
                f"Step {requested_step!r} reset for retry — reject count cleared."
                if not sync_warning
                else f"Step {requested_step!r} reset for retry — reject count cleared; {sync_warning}."
            ),
            "job_status": hooks.get_job_status(state),
            "job_id": state["job_id"],
            "current_step": state["current_step"],
        }, indent=2))
        return AdminCommandResolution(handled=True, exit_code=0)

    if args.force_approve_step:
        if not args.job_id:
            raise ValueError("--force-approve-step requires --job-id")
        state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, args.job_id))
        state = hooks.migrate_job_state(state)
        state = hooks.reconcile_job_state(state, group_cfg)
        state = hooks.force_approve_step(
            group_name=args.template_group,
            group_cfg=group_cfg,
            state=state,
            step=args.force_approve_step.strip(),
        )
        sync_warning = _sync_backend_after_human_approval(state=state)
        print(json.dumps({
            "status": "APPROVED",
            "remark": (
                f"Force human approval recorded for step {args.force_approve_step.strip()!r}."
                if not sync_warning
                else f"Force human approval recorded for step {args.force_approve_step.strip()!r}; {sync_warning}."
            ),
            "job_status": hooks.get_job_status(state),
            "job_id": state["job_id"],
            "current_step": state["current_step"],
        }, indent=2))
        return AdminCommandResolution(handled=True, exit_code=0)

    if args.cancel_run:
        if not args.job_id:
            raise ValueError("--cancel-run requires --job-id")
        state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, args.job_id))
        state = hooks.migrate_job_state(state)
        hooks.set_job_status(state, "STOPPED")
        hooks.save_job(args.template_group, state["job_id"], state)
        # Sync to backend — set run status to stopped
        step_run_id = str(state.get("workflow_step_run_id") or "").strip()
        backend_url = (
            str(state.get("backend_url") or "").strip()
            or os.environ.get("AGENT_RUNNER_BACKEND_URL")
            or str(load_runner_config().get("backend_url") or "").strip()
        )
        if backend_url:
            client = BackendClient(backend_url)
            run_id = str(state.get("workflow_run_id") or "").strip()
            if step_run_id:
                from datetime import datetime, timezone
                client.sync_job_state(
                    step_run_id=step_run_id,
                    payload={
                        "run_status": "stopped",
                        "step_status": "cancelled",
                        "step_outcome": "cancelled",
                        "step_coder": None,
                        "step_duration_seconds": 0,
                        "next_step_name": None,
                        "output_payload": {},
                        "error_message": "Cancelled by operator",
                        "review": None,
                        "artifacts": [],
                        "context_payload": {"__run_control": {"stop_requested": True}},
                        "events": [{"event_type": "RUN_STOPPED", "message": f"Run {state['job_id']} cancelled by operator"}],
                    },
                )
            if run_id:
                client.stop_run(run_id=run_id, reason="Cancelled by operator")
        print(json.dumps({
            "status": "STOPPED",
            "remark": "Run cancelled by operator.",
            "job_status": "STOPPED",
            "job_id": state["job_id"],
        }, indent=2))
        return AdminCommandResolution(handled=True, exit_code=0)

    if args.reapply_routing:
        if not args.job_id:
            raise ValueError("--reapply-routing requires --job-id")
        state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, args.job_id))
        state = hooks.migrate_job_state(state)
        state = hooks.reapply_routing(state, group_cfg)
        hooks.save_job(args.template_group, state["job_id"], state)
        print(json.dumps({
            "status": "APPROVED",
            "remark": f"Routing reapplied. current_step={state['current_step']!r}, job_status={hooks.get_job_status(state)!r}",
            "job_id": state["job_id"],
            "current_step": state["current_step"],
            "job_status": hooks.get_job_status(state),
            "loop_context": state.get("loop_context"),
        }, indent=2))
        return AdminCommandResolution(handled=True, exit_code=0)

    if args.override_step:
        if not args.job_id:
            raise ValueError("--override-step requires --job-id")
        state = hooks.ensure_backward_compatible_state(hooks.load_job(args.template_group, args.job_id))
        state = hooks.migrate_job_state(state)
        target_step = args.override_step.strip()
        if target_step not in group_cfg["step_configs"]:
            raise ValueError(f"Step {target_step!r} is not defined for template group {args.template_group!r}")
        state["loop_context"] = default_loop_context()
        state["replan_context"] = default_replan_context()
        state["current_step"] = target_step
        hooks.set_job_status(state, "IN_PROGRESS")
        state["pending_human_approval_for"] = None
        state["pending_intervention_for"] = None
        state.setdefault("reject_counts", {})[target_step] = 0
        state.setdefault("auto_retry_count_by_step", {})[target_step] = 0
        state.setdefault("human_retry_count_by_step", {})[target_step] = 0
        failed_steps = state.setdefault("failed_steps", [])
        state["failed_steps"] = [s for s in failed_steps if s != target_step]
        steps_order = group_cfg["steps"]
        target_idx = steps_order.index(target_step) if target_step in steps_order else -1
        if target_idx >= 0:
            downstream = set(steps_order[target_idx:])
            state["completed_steps"] = [s for s in state.get("completed_steps", []) if s not in downstream]
            for ds_step in downstream:
                ds_cfg = group_cfg["step_configs"].get(ds_step)
                if ds_cfg:
                    for produced_key in (ds_cfg.get("produces") or []):
                        if produced_key in state.get("artifacts", {}):
                            state["artifacts"][produced_key] = None
        hooks.clear_last_failure(state)
        hooks.save_job(args.template_group, state["job_id"], state)
        sync_warning = _sync_backend_after_override_step(state=state, step_name=target_step)
        print(json.dumps({
            "status": "APPROVED",
            "remark": (
                f"Step overridden to {target_step!r}. Retry state and loop context reset."
                if not sync_warning
                else f"Step overridden to {target_step!r}. Retry state and loop context reset; {sync_warning}."
            ),
            "job_id": state["job_id"],
            "current_step": state["current_step"],
            "job_status": hooks.get_job_status(state),
        }, indent=2))
        return AdminCommandResolution(handled=True, exit_code=0)

    return AdminCommandResolution(handled=False)


def print_failure(
    *,
    remark: str,
    state: dict[str, Any] | None,
    template_group: str,
    step: str | None,
    coder_used: str | None,
    failure_class: str,
    failure_code: str,
    failure_source: str,
    hooks: Any,
) -> None:
    print(json.dumps({
        "status": "REJECTED",
        "remark": remark,
        "job_status": hooks.get_job_status(state) if state else "RUNNER_ERROR",
        "job_id": state["job_id"] if state else None,
        "template_group": template_group,
        "step": step,
        "coder_used": coder_used,
        "last_failure_class": failure_class,
        "last_failure_code": failure_code,
        "last_failure_source": failure_source,
    }, indent=2))


def step_progress_parts(group_cfg: dict[str, Any], step: str | None) -> tuple[int | None, int]:
    steps = list(group_cfg.get("steps") or [])
    total = len(steps)
    if not step or step not in steps:
        return None, total
    return steps.index(step) + 1, total


def step_progress_label(group_cfg: dict[str, Any], step: str | None) -> str:
    index, total = step_progress_parts(group_cfg, step)
    if index is None or total <= 0:
        return "step ? of ?"
    return f"step {index} of {total}"


def format_job_status_summary(
    state: dict[str, Any],
    group_cfg: dict[str, Any],
    *,
    get_job_status: Any,
) -> str:
    current_step = state.get("current_step")
    current_progress = step_progress_label(group_cfg, current_step)
    completed_steps = list(state.get("completed_steps", []))
    total_steps = len(group_cfg.get("steps") or [])
    lines = [
        f"Job ID:        {state.get('job_id')}",
        f"Template:      {state.get('template_group')}",
        f"Status:        {get_job_status(state)}",
        f"Current Step:  {current_step}",
        f"Progress:      {current_progress}",
        f"Completed:     {len(completed_steps)} of {total_steps}",
        "",
        "Completed Steps:",
    ]
    for s in completed_steps:
        lines.append(f"  {s}")
    lines.append("")
    lines.append("Reject Counts:")
    for step_name, count in (state.get("reject_counts") or {}).items():
        if count > 0:
            lines.append(f"  {step_name}: {count}")
    return "\n".join(lines)
