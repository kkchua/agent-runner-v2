from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass
class AdminCommandResolution:
    handled: bool
    exit_code: int = 0
    continue_execution: bool = False
    state: dict[str, Any] | None = None
    step: str | None = None


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
        state["loop_context"] = {
            "active": False, "loop_step": None, "refine_step": None,
            "loop_target_artifact": None, "loop_source_review": None,
            "loop_iteration": 0, "pre_refine_checksum": None,
        }
        state["replan_context"] = {
            "active": False, "source_review_step": None, "replan_step": None,
            "target_artifact": None, "source_review_file": None, "replan_attempt": 0,
            "pre_replan_checksum": None, "trigger_reason": None, "blocking_issues": [],
            "previous_blocking_issue_count": 0, "previous_blocking_issue_severity": 0,
        }
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
        state = hooks.approve_step(
            group_name=args.template_group,
            group_cfg=group_cfg,
            state=state,
            step=args.approve_step.strip(),
        )
        print(json.dumps({
            "status": "APPROVED",
            "remark": f"Human approval recorded for step {args.approve_step.strip()!r}.",
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
        print(json.dumps({
            "status": "APPROVED",
            "remark": f"Force human approval recorded for step {args.force_approve_step.strip()!r}.",
            "job_status": hooks.get_job_status(state),
            "job_id": state["job_id"],
            "current_step": state["current_step"],
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
        state["loop_context"] = {
            "active": False, "loop_step": None, "refine_step": None,
            "loop_target_artifact": None, "loop_source_review": None,
            "loop_iteration": 0, "pre_refine_checksum": None,
        }
        state["replan_context"] = {
            "active": False, "source_review_step": None, "replan_step": None,
            "target_artifact": None, "source_review_file": None, "replan_attempt": 0,
            "pre_replan_checksum": None, "trigger_reason": None, "blocking_issues": [],
            "previous_blocking_issue_count": 0, "previous_blocking_issue_severity": 0,
        }
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
        print(json.dumps({
            "status": "APPROVED",
            "remark": f"Step overridden to {target_step!r}. Retry state and loop context reset.",
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


def format_job_status_summary(state: dict[str, Any], group_cfg: dict[str, Any], *, hooks: Any) -> str:
    current_step = state.get("current_step")
    current_progress = step_progress_label(group_cfg, current_step)
    completed_steps = list(state.get("completed_steps", []))
    total_steps = len(group_cfg.get("steps") or [])
    lines = [
        f"Job ID:        {state.get('job_id')}",
        f"Template:      {state.get('template_group')}",
        f"Status:        {hooks.get_job_status(state)}",
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
