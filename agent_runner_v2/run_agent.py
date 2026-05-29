#!/usr/bin/env python3
"""
run_agent.py — Main CLI entry point for agent_runner_v2.

Orchestration only: load config → resolve job → preflight → prompt → run_step → route.

Related: IMPL-20260422-04

Key v2 differences from v1:
- No disk recovery functions anywhere
- No pre-invocation sidecar writes
- No markdown write-backs (no sync_review_metadata, stamp_created_metadata, etc.)
- run_step() and route_after_step() are the single execution path
- Hard failures (MetaJsonMissingError, etc.) go to route_after_failure() immediately
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from .bundle_loader import (
    init_workspace,
    load_project_config,
    load_workflow_module,
    workflow_root as workflow_root_for,
)
from .coder_adapters import CoderInvocationError, dataclass_dict
from .exceptions import ArtifactMissingError, MetaJsonInvalidError, MetaJsonMissingError, PreflightBlockedError
from .job_state import (
    REVIEW_DECISIONS,
    HUMAN_DECISIONS,
    FINAL_DECISION_SOURCES,
    advance_step,
    append_failure_history,
    apply_task_execution_binding,
    build_failure_envelope,
    build_task_execution_binding_from_ids,
    check_preflight_artifact_status,
    classify_pre_run_failure,
    clear_last_failure,
    create_job,
    default_review_state,
    default_usage_summary,
    ensure_backward_compatible_state,
    ensure_execution_task_binding_integrity,
    ensure_planning_task_queue_integrity,
    enforce_retry_limit_before_run,
    find_matching_active_job,
    find_matching_completed_job,
    get_job_status,
    infer_seed_identity,
    load_job,
    make_step_dir,
    migrate_job_state,
    prepare_state_for_retry,
    recover_exhausted_planning_job,
    reconcile_job_state,
    save_job,
    set_job_status,
    set_last_failure,
    task_execution_binding_current_item,
)
from .model_config import resolve_coder
from .runner_logger import log_resolver
from .runtime_context import (
    PROJECT_ROOT, RUNNER_ROOT, JOBS_ROOT, ARTIFACT_ROOT,
    get_delivery_root, get_workflow_module,
    set_context, set_workflow_module, set_delivery_root,
)
from .step_runner import (
    StepResult,
    build_context,
    prompt_checksum,
    render_prompt,
    resolve_prompt_path,
    run_action,
    run_step,
)
from .workflow_router import route_after_failure, route_after_step


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw = list(argv if argv is not None else sys.argv[1:])
    if not raw or raw[0].startswith("-"):
        raw = ["run", *raw]

    command = raw[0]
    if command == "init":
        p = argparse.ArgumentParser(description="Initialize a project-local runner workspace.")
        p.add_argument("--project-root", default=".", help="Workspace directory to initialize.")
        p.add_argument("--workflow", default="default", help="Workflow name to seed.")
        ns = p.parse_args(raw[1:])
        ns.command = "init"
        return ns

    p = argparse.ArgumentParser(description="Run a job-based LLM workflow (v2).")
    p.add_argument("--project-root", default="", help="Workspace root. Defaults to the current directory.")
    p.add_argument("--workflow", default="", help="Workflow name to run. Defaults to the workspace default.")
    p.add_argument("--target-project-root", default="",
                   help="Target project root for delivery scaffold artifacts (docs/delivery/). "
                        "Defaults to --project-root if not specified.")
    p.add_argument("--template-group", required=True, help="Workflow template group name.")
    p.add_argument("--coder", default="", help="Optional coder override for the current step.")
    p.add_argument("--job-id", default="", help="Existing job id to continue.")
    p.add_argument("--job", default="", help="Explicit step to run. If omitted, auto-resolve.")
    p.add_argument("--set", action="append", default=[], help="Seed artifact for new job: KEY=PATH")
    p.add_argument("--task-graph-id", default="", help="Approved task graph id for execution binding startup.")
    p.add_argument("--task-node-id", default="", help="Selected task node id within the approved task graph.")
    p.add_argument("--show-job", action="store_true", help="Print current job.json and exit.")
    p.add_argument("--approve-step", default="", help="Record human approval for a pending step and exit.")
    p.add_argument("--force-approve-step", default="",
                   help="Force-approve a step regardless of review decision.")
    p.add_argument("--dry-run", action="store_true", help="Render prompt and save prompt.txt without invoking coder.")
    p.add_argument("--new-job", action="store_true", help="Force creation of a new job instead of auto-resuming.")
    p.add_argument("--max-rejects", type=int, default=-1, help="Override max rejects for this run.")
    p.add_argument("--reapply-routing", action="store_true",
                   help="Re-apply routing logic to a job stuck in WAITING_FOR_HUMAN_INTERVENTION.")
    p.add_argument("--override-step", default="",
                   help="Force current_step to a specific step and reset loop context.")
    p.add_argument("--check-job-status", action="store_true",
                   help="Print a formatted summary of job status.")
    p.add_argument("--workflow-key", default="",
                   help="Override ComfyUI workflow key for submit_prompts step.")
    ns = p.parse_args(raw[1:] if command == "run" else raw)
    ns.command = "run"
    return ns


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    workspace_root = Path(args.project_root or ".").resolve()
    if args.command == "init":
        result = init_workspace(workspace_root, workflow_name=args.workflow or "default")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    config = load_project_config(workspace_root)
    workflow_name = args.workflow or str(config.get("default_workflow") or "default")
    workflow_cfg = ((config.get("workflows") or {}).get(workflow_name) or {})
    workflow_path = workflow_cfg.get("path") or str(workflow_root_for(workspace_root, workflow_name).relative_to(workspace_root))
    workflow_bundle_root = (workspace_root / workflow_path).resolve()
    workflow_module = load_workflow_module(workspace_root, workflow_name, config=config)

    # Set delivery root for cross-project scaffold workflows
    delivery_root = None
    if args.target_project_root:
        delivery_root = Path(args.target_project_root).resolve()
        if args.template_group.startswith("delivery_scaffold"):
            # Create the delivery folder structure in the target project
            _ensure_delivery_folders(delivery_root)

    set_context(
        workspace_root=workspace_root,
        workflow_name=workflow_name,
        workflow_root=workflow_bundle_root,
        workflow_module=workflow_module,
        delivery_root=delivery_root,
    )
    set_workflow_module(workflow_module)

    # Effective root for artifact operations: delivery_root for scaffold, workspace_root otherwise
    effective_root = delivery_root if delivery_root is not None else workspace_root

    state: dict | None = None
    group_cfg: dict | None = None
    step: str | None = None
    coder_used = ""
    coder_config: dict | None = None
    max_rejects = 0
    original_current_step: str | None = None
    execution_binding: dict | None = None

    try:
        group_cfg = _load_group(args.template_group)
        _validate_static_reference_files(workspace_root, group_cfg, template_group=args.template_group)

        if (args.task_graph_id or args.task_node_id) and args.template_group != "task_execution_v1":
            raise ValueError("--task-graph-id/--task-node-id are supported only for template group 'task_execution_v1'.")
        if bool(args.task_graph_id) != bool(args.task_node_id):
            raise ValueError("--task-graph-id and --task-node-id must be provided together.")

        # --- Admin commands ---
        if args.show_job:
            if not args.job_id:
                raise ValueError("--show-job requires --job-id")
            state = ensure_backward_compatible_state(load_job(args.template_group, args.job_id))
            state = migrate_job_state(state)
            state = reconcile_job_state(state, group_cfg)
            print(json.dumps(state, indent=2))
            return 0

        if args.check_job_status:
            if not args.job_id:
                raise ValueError("--check-job-status requires --job-id")
            state = ensure_backward_compatible_state(load_job(args.template_group, args.job_id))
            state = migrate_job_state(state)
            state = reconcile_job_state(state, group_cfg)
            print(_format_job_status_summary(state, group_cfg))
            return 0

        if args.approve_step:
            if not args.job_id:
                raise ValueError("--approve-step requires --job-id")
            from .job_state import approve_step
            state = ensure_backward_compatible_state(load_job(args.template_group, args.job_id))
            state = migrate_job_state(state)
            state = reconcile_job_state(state, group_cfg)
            state = approve_step(
                group_name=args.template_group,
                group_cfg=group_cfg,
                state=state,
                step=args.approve_step.strip(),
            )
            print(json.dumps({
                "status": "APPROVED",
                "remark": f"Human approval recorded for step {args.approve_step.strip()!r}.",
                "job_status": get_job_status(state),
                "job_id": state["job_id"],
                "current_step": state["current_step"],
            }, indent=2))
            return 0

        if args.force_approve_step:
            if not args.job_id:
                raise ValueError("--force-approve-step requires --job-id")
            from .job_state import force_approve_step
            state = ensure_backward_compatible_state(load_job(args.template_group, args.job_id))
            state = migrate_job_state(state)
            state = reconcile_job_state(state, group_cfg)
            state = force_approve_step(
                group_name=args.template_group,
                group_cfg=group_cfg,
                state=state,
                step=args.force_approve_step.strip(),
            )
            print(json.dumps({
                "status": "APPROVED",
                "remark": f"Force human approval recorded for step {args.force_approve_step.strip()!r}.",
                "job_status": get_job_status(state),
                "job_id": state["job_id"],
                "current_step": state["current_step"],
            }, indent=2))
            return 0

        if args.reapply_routing:
            if not args.job_id:
                raise ValueError("--reapply-routing requires --job-id")
            from .job_state import reapply_routing
            state = ensure_backward_compatible_state(load_job(args.template_group, args.job_id))
            state = migrate_job_state(state)
            state = reapply_routing(state, group_cfg)
            save_job(args.template_group, state["job_id"], state)
            print(json.dumps({
                "status": "APPROVED",
                "remark": f"Routing reapplied. current_step={state['current_step']!r}, job_status={get_job_status(state)!r}",
                "job_id": state["job_id"],
                "current_step": state["current_step"],
                "job_status": get_job_status(state),
                "loop_context": state.get("loop_context"),
            }, indent=2))
            return 0

        if args.override_step:
            if not args.job_id:
                raise ValueError("--override-step requires --job-id")
            state = ensure_backward_compatible_state(load_job(args.template_group, args.job_id))
            state = migrate_job_state(state)
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
            set_job_status(state, "IN_PROGRESS")
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
            clear_last_failure(state)
            save_job(args.template_group, state["job_id"], state)
            print(json.dumps({
                "status": "APPROVED",
                "remark": f"Step overridden to {target_step!r}. Retry state and loop context reset.",
                "job_id": state["job_id"],
                "current_step": state["current_step"],
                "job_status": get_job_status(state),
            }, indent=2))
            return 0

        # --- Job resolution ---
        if not args.job_id:
            seed_artifacts = _parse_key_value_pairs(args.set)
            if args.template_group == "task_execution_v1":
                if args.task_graph_id and args.task_node_id:
                    execution_binding = build_task_execution_binding_from_ids(
                        task_graph_id=args.task_graph_id.strip(),
                        task_node_id=args.task_node_id.strip(),
                    )
                elif seed_artifacts.get("TASK_FILE"):
                    execution_binding = _build_task_execution_binding_from_task_file(seed_artifacts["TASK_FILE"])
                else:
                    raise ValueError(
                        "task_execution_v1 requires either --task-graph-id with --task-node-id or --set TASK_FILE=PATH."
                    )
            resume_job_id = ""
            completed_job_id = ""
            if not args.new_job:
                if execution_binding is not None:
                    seed_artifact_type, seed_artifact_path = _task_execution_binding_identity(execution_binding)
                else:
                    seed_artifact_type, seed_artifact_path = infer_seed_identity(args.template_group, seed_artifacts)
                if seed_artifact_type and seed_artifact_path:
                    resume_job_id = find_matching_active_job(
                        group_name=args.template_group,
                        seed_artifact_type=seed_artifact_type,
                        seed_artifact_path=seed_artifact_path,
                    ) or ""
                    if not resume_job_id:
                        completed_job_id = find_matching_completed_job(
                            group_name=args.template_group,
                            seed_artifact_type=seed_artifact_type,
                            seed_artifact_path=seed_artifact_path,
                        ) or ""
            if resume_job_id:
                state = ensure_backward_compatible_state(load_job(args.template_group, resume_job_id))
                state = migrate_job_state(state)
                state = recover_exhausted_planning_job(state, group_cfg)
                state = reconcile_job_state(state, group_cfg)
                original_current_step = state.get("current_step")
                if state.get("pending_human_approval_for"):
                    raise ValueError(
                        f"Job {state['job_id']} is waiting for human approval of "
                        f"step {state['pending_human_approval_for']!r}."
                    )
                step = args.job.strip() or state.get("current_step")
                if not step:
                    print(json.dumps({
                        "status": "APPROVED",
                        "remark": f"Job {state['job_id']} is already completed.",
                        "job_status": get_job_status(state),
                        "job_id": state["job_id"],
                    }, indent=2))
                    return 0
                state = prepare_state_for_retry(group_name=args.template_group, state=state, step=step)
            elif completed_job_id:
                state = ensure_backward_compatible_state(load_job(args.template_group, completed_job_id))
                state = migrate_job_state(state)
                print(json.dumps({
                    "status": "REJECTED",
                    "remark": (
                        f"Job {state['job_id']} for this seed is already completed. "
                        "Use --new-job only if you intentionally want a duplicate execution cycle."
                    ),
                    "job_status": get_job_status(state),
                    "job_id": state["job_id"],
                    "last_failure_class": "HUMAN_RETRY_REQUIRED",
                    "last_failure_code": "JOB_ALREADY_COMPLETED_FOR_SEED",
                    "last_failure_source": "runner",
                    "return_code": 1,
                }, indent=2))
                return 1
            else:
                state = create_job(args.template_group, group_cfg, seed_artifacts)
                if execution_binding is not None:
                    apply_task_execution_binding(state, execution_binding)
                    if not seed_artifacts.get("TASK_FILE"):
                        state["artifacts"]["TASK_FILE"] = None
                save_job(args.template_group, state["job_id"], state)
                original_current_step = state.get("current_step")
                default_init_step = group_cfg["job_init_step"]
                step = args.job.strip() or default_init_step
                if step != default_init_step:
                    raise ValueError(
                        f"New job may only start with init step {default_init_step!r} "
                        f"for template group {args.template_group!r}"
                    )
                missing_init = _missing_artifacts(group_cfg.get("job_init_inputs", []), state)
                if missing_init:
                    raise FileNotFoundError("Missing required job init input(s): " + ", ".join(missing_init))
        else:
            state = ensure_backward_compatible_state(load_job(args.template_group, args.job_id))
            state = migrate_job_state(state)
            state = recover_exhausted_planning_job(state, group_cfg)
            state = reconcile_job_state(state, group_cfg)
            original_current_step = state.get("current_step")
            if state.get("pending_human_approval_for"):
                raise ValueError(
                    f"Job {state['job_id']} is waiting for human approval of "
                    f"step {state['pending_human_approval_for']!r}."
                )
            step = args.job.strip() or state.get("current_step")
            if not step:
                print(json.dumps({
                    "status": "APPROVED",
                    "remark": f"Job {state['job_id']} is already completed.",
                    "job_status": get_job_status(state),
                    "job_id": state["job_id"],
                }, indent=2))
                return 0
            state = prepare_state_for_retry(group_name=args.template_group, state=state, step=step)

        step_cfg = group_cfg["step_configs"].get(step)
        if not step_cfg:
            raise ValueError(f"Step {step!r} is not defined for template group {args.template_group!r}")

        # Reset loop context if user forced a different step
        explicit_job = args.job.strip()
        if explicit_job and explicit_job != original_current_step:
            ctx = state.get("loop_context", {})
            if ctx.get("active"):
                state["loop_context"] = {
                    "active": False, "loop_step": None, "refine_step": None,
                    "loop_target_artifact": None, "loop_source_review": None,
                    "loop_iteration": 0, "pre_refine_checksum": None,
                }
                save_job(args.template_group, state["job_id"], state)

        # --- Action step path (non-coder) ---
        action_name = step_cfg.get("action")
        if action_name:
            max_rejects = (
                args.max_rejects if args.max_rejects >= 0
                else int(step_cfg.get("max_rejects", group_cfg["default_max_rejects"]))
            )
            enforce_retry_limit_before_run(state=state, step=step, max_rejects=max_rejects)

            missing_required = _missing_artifacts(step_cfg.get("required_inputs", []), state)
            if missing_required:
                raise FileNotFoundError(
                    f"Cannot run step {step!r}. Missing required input artifact(s): {', '.join(missing_required)}"
                )

            check_preflight_artifact_status(step_cfg=step_cfg, state=state)
            ensure_planning_task_queue_integrity(state, step=step)
            ensure_execution_task_binding_integrity(state, step=step)

            # Build context so action can reference path variables
            context = build_context(state, step=step, step_cfg=step_cfg)
            if args.workflow_key:
                context["WORKFLOW_KEY_OVERRIDE"] = args.workflow_key
            else:
                context["WORKFLOW_KEY_OVERRIDE"] = ""

            step_dir = make_step_dir(group_cfg, state, step)

            print(f"[{_now_iso()}] action={action_name} step={step} status=STARTING", flush=True)

            _mark_review_started(state, step=step, step_cfg=step_cfg, coder_used="action")
            save_job(args.template_group, state["job_id"], state)

            try:
                step_result = run_action(
                    action_name=action_name,
                    state=state,
                    step=step,
                    step_cfg=step_cfg,
                    project_root=effective_root,
                    context=context,
                )
            except Exception as exc:
                print(f"[{_now_iso()}] action={action_name} step={step} status=FAILED error={type(exc).__name__}", flush=True)
                state, exit_code = route_after_failure(
                    group_name=args.template_group,
                    state=state,
                    step=step,
                    coder_used="action",
                    exc=exc,
                    max_rejects=max_rejects,
                    usage_data=default_usage_summary(),
                )
                print(json.dumps({
                    "status": "REJECTED",
                    "remark": str(exc),
                    "job_status": get_job_status(state),
                    "job_id": state["job_id"],
                    "template_group": state["template_group"],
                    "step": step,
                    "coder_used": "action",
                    "last_failure_class": state.get("last_failure_class"),
                    "last_failure_code": state.get("last_failure_code"),
                    "last_failure_source": state.get("last_failure_source"),
                    "reject_count": state.get("reject_counts", {}).get(step, 0),
                    "max_rejects": max_rejects,
                    "step_dir": str(step_dir.relative_to(JOBS_ROOT)),
                }, indent=2))
                return exit_code

            state, exit_code = route_after_step(
                group_name=args.template_group,
                group_cfg=group_cfg,
                state=state,
                step=step,
                step_cfg=step_cfg,
                step_result=step_result,
                coder_used="action",
                max_rejects=max_rejects,
            )
            print(json.dumps({
                "status": step_result.status,
                "remark": step_result.remark,
                "job_status": get_job_status(state),
                "job_id": state["job_id"],
                "template_group": state["template_group"],
                "step": step,
                "coder_used": "action",
                "artifacts": step_result.artifacts,
            }, indent=2))
            return exit_code

        # --- Coder step path ---
        coder_used, coder_config = _resolve_step_coder(
            group_cfg=group_cfg, state=state, step=step, step_cfg=step_cfg,
            cli_coder=args.coder or None,
        )
        max_rejects = (
            args.max_rejects if args.max_rejects >= 0
            else int(step_cfg.get("max_rejects", group_cfg["default_max_rejects"]))
        )
        enforce_retry_limit_before_run(state=state, step=step, max_rejects=max_rejects)

        missing_required = _missing_artifacts(step_cfg.get("required_inputs", []), state)
        if missing_required:
            raise FileNotFoundError(
                f"Cannot run step {step!r}. Missing required input artifact(s): {', '.join(missing_required)}"
            )

        check_preflight_artifact_status(step_cfg=step_cfg, state=state)
        ensure_planning_task_queue_integrity(state, step=step)
        ensure_execution_task_binding_integrity(state, step=step)

        model_id = (coder_config or {}).get("model") or None
        prompt_path = resolve_prompt_path(step_cfg=step_cfg, coder=coder_used, model_id=model_id)
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    except PreflightBlockedError as exc:
        if state is not None and step:
            set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
            state["pending_intervention_for"] = step
            set_last_failure(
                state=state,
                failure_class="HUMAN_RETRY_REQUIRED",
                failure_code="PREFLIGHT_STATUS_NOT_APPROVED",
                failure_reason=str(exc),
                failure_source="runner",
                step=step,
            )
            append_failure_history(
                state=state, step=step,
                failure_class="HUMAN_RETRY_REQUIRED",
                failure_code="PREFLIGHT_STATUS_NOT_APPROVED",
                failure_source="runner",
            )
            save_job(args.template_group, state["job_id"], state)
        _print_failure(
            remark=str(exc),
            state=state,
            template_group=args.template_group,
            step=step,
            coder_used=coder_used or None,
            failure_class="HUMAN_RETRY_REQUIRED",
            failure_code="PREFLIGHT_STATUS_NOT_APPROVED",
            failure_source="runner",
        )
        return 1
    except Exception as exc:
        envelope = classify_pre_run_failure(exc)
        if state is not None and step and max_rejects > 0:
            state, exit_code = route_after_failure(
                group_name=args.template_group,
                state=state,
                step=step,
                coder_used=coder_used,
                exc=exc,
                max_rejects=max_rejects,
                usage_data=default_usage_summary(),
            )
        else:
            exit_code = 1
        _print_failure(
            remark=envelope["failure_reason"],
            state=state,
            template_group=args.template_group,
            step=step,
            coder_used=coder_used or None,
            failure_class=envelope["failure_class"],
            failure_code=envelope["failure_code"],
            failure_source=envelope["failure_source"],
        )
        return exit_code

    # --- Prompt rendering ---
    template_text = prompt_path.read_text(encoding="utf-8")
    context = build_context(state, step=step, step_cfg=step_cfg)

    # Inject CLI-level overrides into context
    if args.workflow_key:
        context["WORKFLOW_KEY_OVERRIDE"] = args.workflow_key
    else:
        context["WORKFLOW_KEY_OVERRIDE"] = ""

    # For refine steps: override REVIEW_FILE from loop_context to prevent stale review
    loop_ctx = state.get("loop_context", {})
    if step_cfg.get("loop_returns_to") and loop_ctx.get("active") and loop_ctx.get("loop_source_review"):
        context["REVIEW_FILE"] = loop_ctx["loop_source_review"]

    prompt_text = render_prompt(template_text, context)
    checksum = prompt_checksum(prompt_text)

    step_dir = make_step_dir(group_cfg, state, step)
    _save_text(step_dir / "prompt.txt", prompt_text)

    for line in context.get("ARTIFACT_FINGERPRINTS", "").splitlines():
        print(f"[run_agent] {line[2:]}", flush=True)

    if args.dry_run:
        print(json.dumps({
            "status": "APPROVED",
            "remark": f"Dry run complete for step {step!r} using coder {coder_used!r}.",
            "template_group": args.template_group,
            "job_id": state["job_id"],
            "step": step,
            "coder_used": coder_used,
            "step_dir": str(step_dir.relative_to(JOBS_ROOT)),
        }, indent=2))
        return 0

    print(f"[{_now_iso()}] coder={coder_used} step={step} status=STARTING", flush=True)

    # Mark review state started (job.json only — no markdown writes in v2)
    _mark_review_started(state, step=step, step_cfg=step_cfg, coder_used=coder_used)
    save_job(args.template_group, state["job_id"], state)

    # --- Core execution ---
    try:
        step_result = run_step(
            group_name=args.template_group,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            coder=coder_used,
            coder_config=coder_config,
            prompt_text=prompt_text,
            checksum=checksum,
            step_dir=step_dir,
            project_root=effective_root,
            context=context,
        )
    except (CoderInvocationError, MetaJsonMissingError, MetaJsonInvalidError, ArtifactMissingError) as exc:
        print(f"[{_now_iso()}] coder={coder_used} step={step} status=FAILED error={type(exc).__name__}", flush=True)
        state, exit_code = route_after_failure(
            group_name=args.template_group,
            state=state,
            step=step,
            coder_used=coder_used,
            exc=exc,
            max_rejects=max_rejects,
            usage_data=default_usage_summary(),
        )
        print(json.dumps({
            "status": "REJECTED",
            "remark": str(exc),
            "job_status": get_job_status(state),
            "job_id": state["job_id"],
            "template_group": state["template_group"],
            "step": step,
            "coder_used": coder_used,
            "last_failure_class": state.get("last_failure_class"),
            "last_failure_code": state.get("last_failure_code"),
            "last_failure_source": state.get("last_failure_source"),
            "reject_count": state.get("reject_counts", {}).get(step, 0),
            "max_rejects": max_rejects,
            "step_dir": str(step_dir.relative_to(JOBS_ROOT)),
        }, indent=2))
        return exit_code

    # --- Route result ---
    state, exit_code = route_after_step(
        group_name=args.template_group,
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        step_result=step_result,
        coder_used=coder_used,
        max_rejects=max_rejects,
    )

    # Save result.json for diagnostics
    _save_json(step_dir / "result.json", {
        "status": step_result.status,
        "remark": step_result.remark,
        "artifacts": step_result.artifacts,
        "reject_code": step_result.reject_code,
        "meta_json_path": step_result.meta_json_path,
    })

    print(json.dumps({
        "status": step_result.status,
        "remark": step_result.remark,
        "job_status": get_job_status(state),
        "job_id": state["job_id"],
        "template_group": state["template_group"],
        "step": step,
        "coder_used": coder_used,
        "reject_count": state.get("reject_counts", {}).get(step, 0),
        "max_rejects": max_rejects,
        "last_failure_class": state.get("last_failure_class"),
        "last_failure_code": state.get("last_failure_code"),
        "last_failure_source": state.get("last_failure_source"),
        "artifacts": step_result.artifacts,
        "meta_json_path": step_result.meta_json_path,
        "step_dir": str(step_dir.relative_to(JOBS_ROOT)),
    }, indent=2))
    return exit_code


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_delivery_folders(target_root: Path) -> None:
    """Create the standard docs/delivery/ folder structure in a target project."""
    folders = [
        "docs/delivery/00_templates",
        "docs/delivery/01_initiatives",
        "docs/delivery/02_plans",
        "docs/delivery/02_plans/artifacts",
        "docs/delivery/03_tasks",
        "docs/delivery/04_implementation_plans",
        "docs/delivery/05_reviews",
        "docs/delivery/06_memory",
        "docs/delivery/07_master_prompts",
        "docs/delivery/08_agents",
    ]
    for folder in folders:
        (target_root / folder).mkdir(parents=True, exist_ok=True)


def _load_group(group_name: str) -> dict:
    bundle = get_workflow_module() or __import__(__package__ + ".template_groups", fromlist=["TEMPLATE_GROUPS"])
    template_groups = bundle.TEMPLATE_GROUPS
    if group_name not in template_groups:
        valid = ", ".join(sorted(template_groups))
        raise ValueError(f"Unknown template group {group_name!r}. Valid groups: {valid}")
    return template_groups[group_name]


def _validate_static_reference_files(workspace_root: Path, group_cfg: dict | None = None, template_group: str = "") -> None:
    # Scaffold workflows generate the delivery docs — they don't need pre-existing reference files
    if template_group.startswith("delivery_scaffold"):
        return
    bundle = get_workflow_module() or __import__(__package__ + ".template_groups", fromlist=["REFERENCE_FILES"])
    reference_files = bundle.REFERENCE_FILES
    if group_cfg is not None and "reference_files" in group_cfg:
        reference_files = group_cfg.get("reference_files") or {}
    missing = [f"{k}: {workspace_root / v}" for k, v in reference_files.items()
               if not (workspace_root / v).exists()]
    if missing:
        raise FileNotFoundError("Missing static reference file(s):\n" + "\n".join(missing))


def _missing_artifacts(keys: list[str], state: dict) -> list[str]:
    missing = []
    artifacts = state.get("artifacts") or {}
    for key in keys:
        value = artifacts.get(key)
        if not value or not (ARTIFACT_ROOT / value).exists():
            missing.append(key)
    return missing


def _parse_key_value_pairs(values: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"Invalid --set value {item!r}. Expected KEY=PATH.")
        key, value = item.split("=", 1)
        key, value = key.strip(), value.strip()
        if not key or not value:
            raise ValueError(f"Invalid --set value {item!r}. Expected KEY=PATH.")
        out[key] = value
    return out


def _resolve_step_coder(
    *, group_cfg: dict, state: dict, step: str, step_cfg: dict, cli_coder: str | None
) -> tuple[str, dict | None]:
    coder_cfg = step_cfg.get("coder", {})
    default_coder = coder_cfg.get("default")
    allowed_coders = coder_cfg.get("allowed", [])
    chosen = cli_coder.strip() if cli_coder else default_coder
    if not chosen:
        raise ValueError(f"No coder specified and no default coder configured for step {step!r}")

    resolved_config = resolve_coder(chosen)
    if resolved_config is not None:
        actual_coder = resolved_config.get("coder", chosen)
        log_resolver(chosen, f"{actual_coder} (model={resolved_config.get('model', '')})", is_alias=True)
        if shutil.which(actual_coder) is None:
            raise FileNotFoundError(f"Coder executable not found: {actual_coder!r} (alias {chosen!r})")
        chosen = actual_coder
    else:
        log_resolver(chosen, chosen, is_alias=False)
        if shutil.which(chosen) is None:
            raise FileNotFoundError(f"Coder executable not found in PATH: {chosen!r}")

    if allowed_coders and chosen not in allowed_coders:
        raise ValueError(f"Coder {chosen!r} is not allowed for step {step!r}. Allowed: {allowed_coders}")
    if coder_cfg.get("must_differ_from_previous_step"):
        idx = group_cfg["steps"].index(step)
        if idx > 0:
            prev_step = group_cfg["steps"][idx - 1]
            prev_coder = state.get("step_coders", {}).get(prev_step)
            if prev_coder and chosen == prev_coder:
                raise ValueError(
                    f"Coder {chosen!r} is not allowed for step {step!r} because it matches previous step {prev_step!r}"
                )
    return chosen, resolved_config


def _task_execution_binding_identity(binding: dict | None) -> tuple[str | None, str | None]:
    if not isinstance(binding, dict):
        return None, None
    task_graph_file = str(binding.get("task_graph_file") or "").strip()
    task_node_id = str(binding.get("task_node_id") or "").strip()
    if not task_graph_file or not task_node_id:
        return None, None
    rel = str((PROJECT_ROOT / task_graph_file).resolve().relative_to(PROJECT_ROOT.resolve()))
    return "TASK_EXECUTION_BINDING", f"{rel}::{task_node_id}"


def _build_task_execution_binding_from_task_file(task_file: str) -> dict:
    """Build task execution binding from a legacy TASK_FILE seed."""
    from .job_state import build_task_execution_binding
    import json as _json

    task_path = PROJECT_ROOT / task_file
    if not task_path.exists():
        raise FileNotFoundError(f"Task file does not exist: {task_path}")

    def _extract_value(content: str, key: str) -> str | None:
        pattern = re.compile(
            rf"^\s*[-*]\s*(?:\*\*)?{re.escape(key)}(?::(?:\*\*)?|\*\*:\s*|:)\s*(.+?)\s*$",
            re.IGNORECASE,
        )
        for line in content.splitlines():
            m = pattern.match(line.strip())
            if m:
                return m.group(1).strip()
        return None

    content = task_path.read_text(encoding="utf-8")
    task_node_id = (_extract_value(content, "Task ID") or "").strip()
    plan_id = (_extract_value(content, "Plan ID") or "").strip()
    if not task_node_id or not plan_id:
        raise ValueError(f"Task file {task_file!r} is missing Task ID or Plan ID metadata.")

    artifact_dir = PROJECT_ROOT / "docs" / "delivery" / "02_plans" / "artifacts"
    matches: list[str] = []
    for candidate in sorted(artifact_dir.glob("*.md")):
        graph_content = candidate.read_text(encoding="utf-8")
        metadata_plan_id = (_extract_value(graph_content, "Plan ID") or "").strip()
        raw_status = ""
        for line in graph_content.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("status:"):
                raw_status = re.sub(r"\s+", "_", stripped.split(":", 1)[1].strip().lower())
                break
        if metadata_plan_id != plan_id or raw_status != "approved":
            continue
        task_graph_file = str(candidate.relative_to(PROJECT_ROOT))
        try:
            b = build_task_execution_binding(task_graph_file=task_graph_file, task_node_id=task_node_id)
            matches.append(_json.dumps(b, sort_keys=True))
        except ValueError:
            continue
    if not matches:
        raise ValueError(
            f"Could not resolve an approved task graph for TASK_FILE {task_file!r} with task_node_id {task_node_id!r}."
        )
    if len(matches) > 1:
        raise ValueError(
            f"Multiple approved task graphs match TASK_FILE {task_file!r} with task_node_id {task_node_id!r}."
        )
    return _json.loads(matches[0])


def _mark_review_started(state: dict, *, step: str, step_cfg: dict, coder_used: str) -> None:
    """Update review tracking in job state (no markdown writes in v2)."""
    on_reject_refine = step_cfg.get("on_reject_refine") or {}
    artifact_key = on_reject_refine.get("artifact")
    if not artifact_key:
        produces = step_cfg.get("produces", [])
        if step_cfg.get("requires_human_approval_after") and produces:
            artifact_key = str(produces[0])
    if not artifact_key:
        return
    review_state = state.setdefault("review_state", default_review_state())
    review_state["reviewer_step"] = step
    review_state["coder_used"] = coder_used
    review_state["review_decision"] = "PENDING"
    review_state["review_decided_at"] = None
    review_state["human_decision"] = "PENDING"
    review_state["human_decided_at"] = None
    review_state["final_decision"] = None
    review_state["final_decision_source"] = None
    # Increment review iteration counter
    prior = sum(
        1 for e in state.get("retry_history", [])
        if e.get("step") == step
    )
    review_state["review_iteration"] = prior + 1


def _print_failure(
    *,
    remark: str,
    state: dict | None,
    template_group: str,
    step: str | None,
    coder_used: str | None,
    failure_class: str,
    failure_code: str,
    failure_source: str,
) -> None:
    print(json.dumps({
        "status": "REJECTED",
        "remark": remark,
        "job_status": get_job_status(state) if state else "RUNNER_ERROR",
        "job_id": state["job_id"] if state else None,
        "template_group": template_group,
        "step": step,
        "coder_used": coder_used,
        "last_failure_class": failure_class,
        "last_failure_code": failure_code,
        "last_failure_source": failure_source,
    }, indent=2))


def _format_job_status_summary(state: dict, group_cfg: dict) -> str:
    lines = [
        f"Job ID:        {state.get('job_id')}",
        f"Template:      {state.get('template_group')}",
        f"Status:        {get_job_status(state)}",
        f"Current Step:  {state.get('current_step')}",
        "",
        "Completed Steps:",
    ]
    for s in state.get("completed_steps", []):
        lines.append(f"  {s}")
    lines.append("")
    lines.append("Reject Counts:")
    for step_name, count in (state.get("reject_counts") or {}).items():
        if count > 0:
            lines.append(f"  {step_name}: {count}")
    return "\n".join(lines)


def _save_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
