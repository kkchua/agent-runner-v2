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
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .backend_client import BackendClient
from .bundle_loader import (
    core_bundles_root,
    init_workspace,
    load_project_config,
    load_workflow_module,
    publish_bootstrap_bundle,
    resolve_workflow_root,
)
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
    CURRENT_SCHEMA_VERSION,
    default_task_execution_binding,
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
    _update_document_status,
)
from .model_config import resolve_coder
from .runner_logger import log_resolver
from .runtime_context import (
    PROJECT_ROOT, RUNNER_ROOT, JOBS_ROOT, ARTIFACT_ROOT, PACKAGE_ROOT,
    get_delivery_root, get_workflow_module,
    set_context, set_workflow_module, set_delivery_root,
)
from .constants import RUN_AGENT_REQUIRED_DOC_DIRS, codebase_doc_rel, delivery_doc_rel, system_doc_rel
from .doc_paths import repo_doc_rel
from .constants import known_artifact_paths
from .step_runner import (
    StepResult,
    build_context,
    prompt_checksum,
    render_prompt,
    resolve_prompt_path,
    run_action,
    run_step,
)
from .documentation_guardrails import (
    EXECUTION_SCAFFOLD_WORKFLOW,
    MASTER_BOOTSTRAP_WORKFLOWS,
    generated_doc_manifest,
    managed_banner,
)
from .workflow_packages.registry import discover_workflow_package
from .workflow_packages.loader import bundle_to_template_group_dict, load_workflow_package

__version__ = "0.1.0"
from .execution_request import ExecutionRequest
from .execution_result import ExecutionFailure, ExecutionResult
from .workflow_router import route_after_failure, route_after_step
from .workflow_specs import reconcile_step_execution_spec
from .workflow_specs import build_step_execution_spec, get_template_group_cfg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_relative_to(path: Path, base: Path) -> str:
    """Safely compute relative path, falling back to os.path.relpath on Windows."""
    try:
        return str(path.relative_to(base))
    except ValueError:
        # Windows pathlib.relative_to() can fail even for valid subpaths
        return os.path.relpath(path, base)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _resolve_workflow_bundle_root(workspace_root: Path, workflow_name: str, config: dict) -> Path:
    """Resolve the active workflow bundle root from configured overrides or runner home."""
    workflow_cfg = ((config.get("workflows") or {}).get(workflow_name) or {})
    workflow_path = workflow_cfg.get("path")
    if workflow_path:
        return (workspace_root / workflow_path).resolve()
    return resolve_workflow_root(workspace_root, workflow_name, config=config)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw = list(argv if argv is not None else sys.argv[1:])
    if not raw or raw[0].startswith("-"):
        raw = ["run", *raw]

    command = raw[0]
    if command == "init":
        p = argparse.ArgumentParser(description="Initialize the runner home and workspace configuration.")
        p.add_argument("--project-root", default=".", help="Workspace directory to initialize.")
        p.add_argument("--workflow", default="default", help="Workflow name to seed.")
        p.add_argument("--bundle-domain", default="general", help="Domain bundle to record for this workspace (e.g. frontend, backend, content).")
        p.add_argument("--bundle-profile", default="core+workflow", help="Bundle profile to record for this workspace.")
        ns = p.parse_args(raw[1:])
        ns.command = "init"
        return ns

    if command == "bootstrap-publish":
        p = argparse.ArgumentParser(description="Publish repo-local bootstrap docs into the packaged core bundle.")
        p.add_argument("--project-root", default=".", help="Workspace directory containing the repo-local bootstrap docs.")
        p.add_argument("--source-root", default="", help="Optional explicit source directory to publish.")
        p.add_argument("--bundle-root", default="", help="Optional explicit package bundle destination.")
        ns = p.parse_args(raw[1:])
        ns.command = "bootstrap-publish"
        return ns

    if command == "execute-step":
        p = argparse.ArgumentParser(description="Execute one backend-provided step request.")
        p.add_argument("--request-file", required=True, help="Path to execution request JSON.")
        p.add_argument("--result-file", default="", help="Optional path to write execution result JSON.")
        ns = p.parse_args(raw[1:])
        ns.command = "execute-step"
        return ns

    if command == "worker":
        p = argparse.ArgumentParser(description="Backend-connected worker mode.")
        p.add_argument("--backend-url", required=True, help="Backend base URL, e.g. http://127.0.0.1:8100")
        p.add_argument("--worker-id", required=True, help="Worker identifier to register and claim work with.")
        p.add_argument("--host-name", default="", help="Optional host name for worker registration.")
        p.add_argument("--poll-seconds", type=int, default=5, help="Polling interval when idle.")
        p.add_argument("--once", action="store_true", help="Claim and process at most one step, then exit.")
        p.add_argument("--engine-root", default="", help="Explicit version directory to prepend to PYTHONPATH for execute-step subprocesses. Overrides config.json lookup.")
        p.add_argument("--worker-label", default="live", help="Worker queue label (e.g. 'live' or 'dev'). Only claims runs with matching worker_label.")
        ns = p.parse_args(raw[1:])
        ns.command = "worker"
        return ns

    if command == "poll":
        # Convenience single-shot variant: reads AGENT_RUNNER_BACKEND_URL and AGENT_RUNNER_WORKER_ID
        # from the environment. Equivalent to: worker --once --backend-url URL --worker-id ID
        import os as _os
        p = argparse.ArgumentParser(description="Single-shot backend poll (claim one step and exit).")
        p.add_argument("--backend-url", default=_os.environ.get("AGENT_RUNNER_BACKEND_URL", "http://127.0.0.1:8100"))
        p.add_argument("--worker-id", default=_os.environ.get("AGENT_RUNNER_WORKER_ID", ""))
        p.add_argument("--host-name", default="")
        p.add_argument("--engine-root", default="")
        p.add_argument("--worker-label", default=_os.environ.get("WORKER_LABEL", "live"))
        ns = p.parse_args(raw[1:])
        ns.command = "poll"
        return ns

    if command == "engine":
        ns = argparse.Namespace()
        ns.command = "engine"
        ns.engine_argv = raw[1:]
        return ns

    if command == "daemon":
        ns = argparse.Namespace()
        ns.command = "daemon"
        ns.daemon_argv = raw[1:]
        return ns

    if command == "submit":
        ns = argparse.Namespace()
        ns.command = "submit"
        ns.submit_argv = raw[1:]
        return ns

    if command == "workflow-spec":
        ns = argparse.Namespace()
        ns.command = "workflow-spec"
        ns.workflow_spec_argv = raw[1:]
        return ns

    if command == "sync-workflow-spec":
        ns = argparse.Namespace()
        ns.command = "sync-workflow-spec"
        ns.workflow_spec_argv = raw[1:]
        return ns

    if command == "approve":
        ns = argparse.Namespace()
        ns.command = "approve"
        ns.approve_argv = raw[1:]
        return ns

    p = argparse.ArgumentParser(description="Run a job-based LLM workflow (v2).")
    p.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument("--project-root", default="", help="Workspace root. Defaults to the current directory.")
    p.add_argument("--workflow", default="", help="Workflow name to run. Defaults to the workspace default.")
    p.add_argument("--target-project-root", default="",
                   help=f"Target project root for delivery scaffold artifacts ({delivery_doc_rel()}/). "
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
    p.add_argument("--single-step", action="store_true",
                   help="Run exactly the step specified by --job, ignoring auto-resolve logic. "
                        "Intended for backend worker integration. Outputs structured JSON for the worker to parse.")
    ns = p.parse_args(raw[1:] if command == "run" else raw)
    ns.command = "run"
    return ns


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "init":
        workspace_root = Path(args.project_root or ".").resolve()
        result = init_workspace(
            workspace_root,
            workflow_name=args.workflow or "default",
            domain=args.bundle_domain or "general",
            bundle_profile=args.bundle_profile or "core+workflow",
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "bootstrap-publish":
        workspace_root = Path(args.project_root or ".").resolve()
        source_root = Path(args.source_root).resolve() if args.source_root else None
        bundle_root = Path(args.bundle_root).resolve() if args.bundle_root else None
        result = publish_bootstrap_bundle(
            workspace_root,
            source_root=source_root,
            package_root=bundle_root,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "execute-step":
        result_path = Path(args.result_file).resolve() if args.result_file else None
        return _execute_step_command(Path(args.request_file).resolve(), result_path)

    if args.command == "worker":
        return _worker_command(
            backend_url=args.backend_url,
            worker_id=args.worker_id,
            host_name=args.host_name or None,
            poll_seconds=args.poll_seconds,
            once=args.once,
            engine_root=args.engine_root or None,
            worker_label=args.worker_label,
        )

    if args.command == "poll":
        import os as _os
        worker_id = args.worker_id or _os.environ.get("AGENT_RUNNER_WORKER_ID", "")
        if not worker_id:
            print("[poll] ERROR: --worker-id or AGENT_RUNNER_WORKER_ID env var required", flush=True)
            return 1
        return _worker_command(
            backend_url=args.backend_url,
            worker_id=worker_id,
            host_name=args.host_name or None,
            poll_seconds=5,
            once=True,
            engine_root=args.engine_root or None,
            worker_label=args.worker_label,
        )

    if args.command == "engine":
        from .engine_commands import main as _engine_main
        return _engine_main(args.engine_argv)

    if args.command == "daemon":
        from .daemon import main as _daemon_main
        return _daemon_main(args.daemon_argv)

    if args.command == "submit":
        from .submit_commands import main as _submit_main
        return _submit_main(args.submit_argv)

    if args.command == "workflow-spec":
        from .workflow_spec_commands import main as _workflow_spec_main
        return _workflow_spec_main(args.workflow_spec_argv)

    if args.command == "sync-workflow-spec":
        from .workflow_spec_commands import main as _workflow_spec_main
        return _workflow_spec_main(args.workflow_spec_argv)

    if args.command == "approve":
        from .approve_commands import main as _approve_main
        return _approve_main(args.approve_argv)

    workspace_root = Path(args.project_root or ".").resolve()
    config = load_project_config(workspace_root)
    workflow_name = args.workflow or str(config.get("default_workflow") or "default")
    workflow_bundle_root = _resolve_workflow_bundle_root(workspace_root, workflow_name, config)
    workflow_module = load_workflow_module(workspace_root, workflow_name, config=config)

    # Set target root for cross-project workflows that write into a repository tree.
    delivery_root = None
    if args.target_project_root:
        delivery_root = Path(args.target_project_root).resolve()
        if (
            args.template_group.startswith("delivery_scaffold")
            or args.template_group.startswith("codebase_")
            or args.template_group.startswith("system_docs_")
        ):
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
        group_cfg = _load_group(args.template_group, workspace_root=workspace_root, workflow_root=workflow_bundle_root)
        _validate_static_reference_files(workspace_root, group_cfg, template_group=args.template_group)

        if (args.task_graph_id or args.task_node_id) and args.template_group != "task_execution_v1":
            raise ValueError("--task-graph-id/--task-node-id are supported only for template group 'task_execution_v1'.")
        if bool(args.task_graph_id) != bool(args.task_node_id):
            raise ValueError("--task-graph-id and --task-node-id must be provided together.")

        # --- Admin commands ---
        if args.single_step:
            if not args.job_id:
                raise ValueError("--single-step requires --job-id")
            if not args.job:
                raise ValueError("--single-step requires --job <step_name>")
            # Single-step mode: load job, force the step, run it, output structured result
            state = ensure_backward_compatible_state(load_job(args.template_group, args.job_id))
            state = migrate_job_state(state)
            state = reconcile_job_state(state, group_cfg)
            step = args.job.strip()
            step_cfg = group_cfg["step_configs"].get(step)
            if not step_cfg:
                raise ValueError(f"Step {step!r} is not defined for template group {args.template_group!r}")
            # Reset loop/replan context for a clean step execution
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
            save_job(args.template_group, state["job_id"], state)
            # Fall through to normal execution — the CLI will run the step and exit
            # The structured JSON output will be parsed by the worker

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
                # Clear artifacts produced by downstream steps so they get
                # regenerated with fresh paths on re-run.
                for ds_step in downstream:
                    ds_cfg = group_cfg["step_configs"].get(ds_step)
                    if ds_cfg:
                        for produced_key in (ds_cfg.get("produces") or []):
                            if produced_key in state.get("artifacts", {}):
                                state["artifacts"][produced_key] = None
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
                        "current_step": state.get("current_step"),
                        "progress": _step_progress_label(group_cfg, state.get("current_step")),
                        "status_summary": _format_job_status_summary(state, group_cfg),
                    }, indent=2))
                    return 0
                state = prepare_state_for_retry(group_name=args.template_group, state=state, step=step)
            elif completed_job_id:
                state = ensure_backward_compatible_state(load_job(args.template_group, completed_job_id))
                state = migrate_job_state(state)
                state = reconcile_job_state(state, group_cfg)
                print(json.dumps({
                    "status": "APPROVED",
                    "remark": (
                        f"Job {state['job_id']} for this seed is already completed. "
                        "Use --new-job only if you intentionally want a duplicate execution cycle."
                    ),
                    "job_status": get_job_status(state),
                    "job_id": state["job_id"],
                    "current_step": state.get("current_step"),
                    "progress": _step_progress_label(group_cfg, state.get("current_step")),
                    "status_summary": _format_job_status_summary(state, group_cfg),
                }, indent=2))
                return 0
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
                    "current_step": state.get("current_step"),
                    "progress": _step_progress_label(group_cfg, state.get("current_step")),
                    "status_summary": _format_job_status_summary(state, group_cfg),
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

        max_rejects = (
            args.max_rejects if args.max_rejects >= 0
            else int(step_cfg.get("max_rejects", group_cfg["default_max_rejects"]))
        )
        enforce_retry_limit_before_run(state=state, step=step, max_rejects=max_rejects)
        prepared = _prepare_step_execution(
            template_group=args.template_group,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            workflow_key_override=args.workflow_key or "",
            cli_coder=args.coder or None,
        )
        coder_used = prepared.coder_used

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
                step_cfg=step_cfg,
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

    step_dir = prepared.step_dir
    if not prepared.action_name:
        for line in prepared.context.get("ARTIFACT_FINGERPRINTS", "").splitlines():
            print(f"[run_agent] {line[2:]}", flush=True)

        if args.dry_run:
            print(json.dumps({
                "status": "APPROVED",
                "remark": f"Dry run complete for step {step!r} using coder {coder_used!r}.",
                "template_group": args.template_group,
                "job_id": state["job_id"],
                "step": step,
                "step_progress": _step_progress_label(group_cfg, step),
                "coder_used": coder_used,
                "step_dir": _safe_relative_to(step_dir, JOBS_ROOT),
            }, indent=2))
            return 0

        coder_label = f"{prepared.coder_alias} ({coder_used})" if prepared.coder_alias else coder_used
        print(
            f"[{_now_iso()}] coder={coder_label} step={step} "
            f"progress=\"{_step_progress_label(group_cfg, step)}\" status=STARTING",
            flush=True,
        )
    else:
        print(
            f"[{_now_iso()}] action={prepared.action_name} step={step} "
            f"progress=\"{_step_progress_label(group_cfg, step)}\" status=STARTING",
            flush=True,
        )

    # Mark review state started (job.json only — no markdown writes in v2)
    _mark_review_started(state, step=step, step_cfg=step_cfg, coder_used=coder_used)
    save_job(args.template_group, state["job_id"], state)

    # --- Core execution ---
    try:
        step_result = _execute_prepared_step(
            prepared=prepared,
            template_group=args.template_group,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            effective_root=effective_root,
        )
    except Exception as exc:
        actor = f"action={prepared.action_name}" if prepared.action_name else f"coder={coder_used}"
        print(f"[{_now_iso()}] {actor} step={step} status=FAILED error={type(exc).__name__}", flush=True)
        state, exit_code = route_after_failure(
            group_name=args.template_group,
            state=state,
            step=step,
            step_cfg=step_cfg,
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
            "step_progress": _step_progress_label(group_cfg, step),
            "coder_used": coder_used,
            "last_failure_class": state.get("last_failure_class"),
            "last_failure_code": state.get("last_failure_code"),
            "last_failure_source": state.get("last_failure_source"),
            "reject_count": state.get("reject_counts", {}).get(step, 0),
            "max_rejects": max_rejects,
            "step_dir": _safe_relative_to(step_dir, JOBS_ROOT),
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
        "step_progress": _step_progress_label(group_cfg, step),
        "coder_used": coder_used,
        "reject_count": state.get("reject_counts", {}).get(step, 0),
        "max_rejects": max_rejects,
        "last_failure_class": state.get("last_failure_class"),
        "last_failure_code": state.get("last_failure_code"),
        "last_failure_source": state.get("last_failure_source"),
        "artifacts": step_result.artifacts,
        "meta_json_path": step_result.meta_json_path,
        "step_dir": _safe_relative_to(step_dir, JOBS_ROOT),
    }, indent=2))
    return exit_code


def _execute_step_command(request_path: Path, result_path: Path | None = None) -> int:
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    request = ExecutionRequest.from_dict(payload)

    try:
        workspace_root = Path(request.workspace_root or request.project_root).resolve()
        config = load_project_config(workspace_root)
        workflow_name = request.workflow_name or str(config.get("default_workflow") or "default")
        workflow_cfg_map = config.get("workflows") or {}
        bundle_workflow_name = workflow_name if workflow_name in workflow_cfg_map else str(config.get("default_workflow") or "default")

        # Prefer a user-customized global default workflow bundle when present.
        # Otherwise use DB-provided step_execution_spec directly.
        # If neither is available, fail fast.
        workflow_module = None
        global_default_root = resolve_workflow_root(workspace_root, "default", config=config)
        global_default_module = global_default_root / "template_groups.py"
        if global_default_module.exists():
            workflow_bundle_root = global_default_root
            workflow_module = load_workflow_module(workspace_root, "default", config=config)
        elif request.step_execution_spec:
            workflow_bundle_root = PACKAGE_ROOT.resolve()
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
            _ensure_delivery_folders(delivery_root)

        set_context(
            workspace_root=workspace_root,
            workflow_name=workflow_name,
            workflow_root=workflow_bundle_root,
            workflow_module=workflow_module,
            delivery_root=delivery_root,
        )
        set_workflow_module(workflow_module)
        effective_root = delivery_root if delivery_root is not None else workspace_root

        spec_source = (request.step_spec_source or "backend").strip().lower()
        if spec_source == "global":
            group_cfg = _load_group(request.template_group, workspace_root=workspace_root, workflow_root=workflow_bundle_root)
            step_cfg = group_cfg["step_configs"].get(request.step_name)
            if not step_cfg:
                raise ValueError(f"Step {request.step_name!r} is not defined for template group {request.template_group!r}")
            request.step_execution_spec = build_step_execution_spec(
                template_group=request.template_group,
                step_name=request.step_name,
                group_cfg=group_cfg,
            )
        elif request.step_execution_spec:
            if spec_source == "hybrid":
                try:
                    request.step_execution_spec = reconcile_step_execution_spec(
                        template_group=request.template_group,
                        step_name=request.step_name,
                        workspace_root=workspace_root,
                        workflow_name=bundle_workflow_name or "default",
                        backend_spec=dict(request.step_execution_spec or {}),
                    )
                except Exception:
                    pass
            group_cfg, step_cfg = _build_group_cfg_from_execution_spec(
                request.step_execution_spec,
                request.template_group,
                request.step_name,
            )
        else:
            group_cfg = _load_group(request.template_group, workspace_root=workspace_root, workflow_root=workflow_bundle_root)
            step_cfg = group_cfg["step_configs"].get(request.step_name)
            if not step_cfg:
                raise ValueError(f"Step {request.step_name!r} is not defined for template group {request.template_group!r}")
        _validate_static_reference_files(workspace_root, group_cfg, template_group=request.template_group)

        state = _build_execution_state(request=request, group_cfg=group_cfg)
        save_job(request.template_group, state["job_id"], state)

        old_env: dict[str, str | None] = {}
        try:
            for key, value in request.env_overrides.items():
                old_env[key] = os.environ.get(key)
                os.environ[key] = value
            result = _execute_backend_step_request(
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
        save_job(request.template_group, state["job_id"], state)
        if result_path is not None:
            result_path.write_text(json.dumps(result_payload, indent=2), encoding="utf-8")
        print(json.dumps(result_payload, indent=2))
        return 0 if result.status == "completed" else 1
    except Exception as exc:
        step_order = 1
        if isinstance(request.step_execution_spec, dict):
            step_order = int(request.step_execution_spec.get("step_order") or request.step_execution_spec.get("step_sequence_no") or 1)
        crash_result = _build_worker_crash_result(
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


def _build_group_cfg_from_execution_spec(spec: dict[str, Any], template_group: str, step_name: str) -> tuple[dict[str, Any], dict[str, Any]]:
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


def _resolve_worker_engine_root(engine_root: str | None) -> tuple[str | None, str | None]:
    """Resolve engine root and version from --engine-root flag or config.json.

    Returns (effective_engine_root, engine_version).
    Both are None if no version is configured (dev/live-source mode).
    """
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


def _worker_command(*, backend_url: str, worker_id: str, host_name: str | None, poll_seconds: int, once: bool, engine_root: str | None = None, worker_label: str = "live") -> int:
    effective_engine_root, engine_version = _resolve_worker_engine_root(engine_root)
    if effective_engine_root:
        print(f"[worker] engine version: {engine_version!r}  root: {effective_engine_root}", flush=True)
    else:
        print("[worker] engine version: live source (no config.json or PYTHONPATH override)", flush=True)

    client = BackendClient(backend_url)
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
        _write_backend_job_json(run=run, step_run=step_run, last_event="STEP_CLAIMED")
        request_payload = _build_worker_request_payload(run=run, step_run=step_run, step_execution_spec=claim.get("step_execution_spec"), backend_url=backend_url)
        try:
            result = _invoke_execute_step_subprocess(request_payload, engine_root=effective_engine_root)
        except Exception as exc:
            result = _build_worker_crash_result(run=run, step_run=step_run, error=exc)
        completion = _submit_worker_result(client=client, run=run, step_run=step_run, result=result)
        _finalize_worker_completion(client=client, run=run, step_run=step_run, completion=completion)
        client.heartbeat(worker_id=worker_id, status="idle", current_step_run_id=None)
        if once:
            return 0


def _build_worker_request_payload(
    *,
    run: dict[str, Any],
    step_run: dict[str, Any],
    step_execution_spec: dict[str, Any] | None = None,
    backend_url: str = "",
    step_spec_source: str = "backend",
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
            group_cfg = get_template_group_cfg(
                template_group=template_group,
                workspace_root=workspace_path,
                workflow_name=workflow_name or "default",
            )
            spec = build_step_execution_spec(
                template_group=template_group,
                step_name=step_name,
                group_cfg=group_cfg,
            )
            coder_override = None
        except Exception:
            spec = dict(step_execution_spec or {})
    elif mode == "hybrid":
        try:
            spec = reconcile_step_execution_spec(
                template_group=template_group,
                step_name=step_name,
                workspace_root=workspace_path,
                workflow_name=workflow_name or "default",
                backend_spec=spec,
            )
        except Exception:
            spec = dict(step_execution_spec or {})
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

    # Compute step sequence number for backend_step_dir_rel
    job_id = str(run.get("run_code") or run.get("id") or "backend-job")

    # ALWAYS compute from current workflow definition to prevent drift from stale backend data
    try:
        from .job_state import get_template_group_cfg
        group_cfg = get_template_group_cfg(
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
        # Fallback to backend-provided value only if we can't load the workflow
        step_sequence_no = spec.get("step_sequence_no") or step_run.get("sequence_no") or 1
    
    # Compute backend_step_dir_rel to ensure actions can write meta.json
    backend_step_dir_rel = str(
        JOBS_ROOT
        / template_group
        / job_id
        / f"{int(step_sequence_no):02d}_{step_name}"
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
        "state_overrides": {
            "backend_step_dir_rel": backend_step_dir_rel,
        },
        "step_execution_spec": spec,
    }


def _invoke_execute_step_subprocess(request_payload: dict[str, Any], engine_root: str | None = None) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="agent-runner-v2-") as temp_dir:
        req_path = Path(temp_dir) / "request.json"
        res_path = Path(temp_dir) / "result.json"
        req_path.write_text(json.dumps(request_payload, indent=2), encoding="utf-8")
        module = "agent_runner_v2.run_agent"
        cmd = [sys.executable, "-m", module, "execute-step", "--request-file", str(req_path), "--result-file", str(res_path)]
        env = os.environ.copy()
        
        # Set working directory to project_root so subprocess can find .env file
        project_root = request_payload.get("project_root") or request_payload.get("workspace_root")
        cwd = Path(project_root).resolve() if project_root else None
        
        if engine_root:
            # Prepend <engine_root>/agent_runner_v2 so Python finds the frozen inner package
            # at <engine_root>/agent_runner_v2/agent_runner_v2/, not the outer worker's copy.
            env["PYTHONPATH"] = str(Path(engine_root) / "agent_runner_v2") + os.pathsep + env.get("PYTHONPATH", "")
        # SNAPSHOT: engine_root is None — outer worker PYTHONPATH already provides agent_runner_v2
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd)
        if not res_path.exists():
            # Print full stderr before raising for debugging
            print(f"[_invoke_execute_step_subprocess] FULL STDERR:\n{proc.stderr}", flush=True)
            raise RuntimeError(f"execute-step did not write result file; rc={proc.returncode}\nFull stderr:\n{proc.stderr[-2000:]}")
        payload = json.loads(res_path.read_text(encoding="utf-8"))
        payload.setdefault("diagnostics", {})["subprocess_return_code"] = proc.returncode
        payload["diagnostics"]["stdout"] = proc.stdout[-2000:]
        payload["diagnostics"]["stderr"] = proc.stderr[-2000:]
        return payload


def _job_json_path(*, workflow_name: str, run_code: str) -> Path:
    return JOBS_ROOT / workflow_name / run_code / "job.json"


def _write_backend_job_json(
    *,
    run: dict[str, Any],
    step_run: dict[str, Any] | None = None,
    next_step_run: dict[str, Any] | None = None,
    last_event: str | None = None,
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
        "updated_at": _now_iso(),
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

    job_json_path = _job_json_path(workflow_name=workflow_name, run_code=run_code)
    job_json_path.parent.mkdir(parents=True, exist_ok=True)
    _save_json(job_json_path, payload)


def _submit_worker_result(*, client: BackendClient, run: dict[str, Any], step_run: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
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
            artifact_errors.append({
                "artifact_key": artifact_key,
                "file_path": file_path,
                "error": str(exc),
            })

    review = result.get("review")
    complete_payload: dict[str, Any] = {
        "status": result.get("status", "failed"),
        "outcome": result.get("outcome"),
        "coder": result.get("coder_used"),
        "output_payload": normalized_artifacts,
        "error_message": (result.get("failure") or {}).get("failure_reason"),
    }
    if review:
        complete_payload["review"] = review
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


def _finalize_worker_completion(
    *,
    client: BackendClient,
    run: dict[str, Any],
    step_run: dict[str, Any],
    completion: dict[str, Any] | None,
) -> dict[str, Any]:
    """Mirror backend completion locally and send workflow notifications.

    This is shared by both `worker` mode and the daemon supervisor so they
    do not drift on terminal run handling.
    """
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

    _write_backend_job_json(
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


def _build_execution_state(*, request: ExecutionRequest, group_cfg: dict[str, Any]) -> dict[str, Any]:
    bundle = get_workflow_module()
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

    # Use definition step_order for workflow metadata, but runtime sequence for contiguous backend working dirs.
    step_order = (request.step_execution_spec or {}).get("step_order", step_index)
    step_sequence = (request.step_execution_spec or {}).get("step_sequence_no", step_index)

    run_id = str(request.job_id or request.workflow_run_id or "backend-run")
    backend_ctx = dict(request.context_payload)
    task_binding = default_task_execution_binding()
    current_item = backend_ctx.get("current_item") if isinstance(backend_ctx.get("current_item"), dict) else {}
    ctx_task_node_id = (current_item.get("task_node_id") or backend_ctx.get("CURRENT_TASK_NODE_ID") or "").strip()
    ctx_task_graph_file = (backend_ctx.get("TASK_GRAPH_FILE") or "").strip()
    if ctx_task_graph_file and ctx_task_node_id and request.template_group == "task_execution_v1":
        try:
            from .job_state import build_task_execution_binding
            task_binding = build_task_execution_binding(
                task_graph_file=ctx_task_graph_file,
                task_node_id=ctx_task_node_id,
            )
            if not task_binding.get("task_graph_id"):
                task_binding["task_graph_id"] = backend_ctx.get("SOURCE_TASK_GRAPH_ID")
        except Exception as _bind_exc:
            raise RuntimeError(f"[_build_execution_state] could not build task execution binding: {_bind_exc}") from _bind_exc
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
        "usage_summary": default_usage_summary(),
        "pending_human_approval_for": None,
        "human_approvals": {},
        "model_approved_steps": [],
        "review_state": default_review_state(),
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
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "artifacts": artifacts,
        "loop_context": {
            "active": False, "loop_step": None, "refine_step": None,
            "loop_target_artifact": None, "loop_source_review": None,
            "loop_iteration": 0, "pre_refine_checksum": None,
        },
        "loop_history": [],
        "replan_context": {
            "active": False, "source_review_step": None, "replan_step": None,
            "target_artifact": None, "source_review_file": None, "replan_attempt": 0,
            "pre_replan_checksum": None, "trigger_reason": None, "blocking_issues": [],
            "previous_blocking_issue_count": 0, "previous_blocking_issue_severity": 0,
        },
        "replan_history": [],
        "planning_attempt_count": 0,
        "recovered_from_invalid_result": False,
        "recovery_code": None,
        "recovery_source": None,
        "task_generation_state_version": 1,
        "task_generation_state": None,
        "task_execution_binding": task_binding,
        "state_schema_version": CURRENT_SCHEMA_VERSION,
        "repair_history": [],
        "reconciled_from_failure": None,
        "workflow_run_id": request.workflow_run_id,
        "workflow_step_run_id": request.workflow_step_run_id,
        "backend_context_payload": dict(request.context_payload),
        "backend_artifact_rules": dict((request.step_execution_spec or {}).get("artifact_rules") or {}),
        "backend_step_order": step_order,
        "backend_step_sequence": step_sequence,
        "backend_step_dir_rel": str(
            JOBS_ROOT
            / request.template_group
            / str(request.job_id or request.workflow_run_id or "backend-job")
            / f"{step_sequence:02d}_{request.step_name}"
        ),
    }
    state.update(request.state_overrides)
    return state


DELIVERY_SCAFFOLD_PUBLISH_PATHS: dict[str, str] = {
    "PROJECT_ANALYSIS": system_doc_rel("PROJECT_ANALYSIS.md"),
    "DELIVERY_SOP": system_doc_rel("WORKFLOW_SOP_v1.md"),
    "DELIVERY_STATUS_RULES": system_doc_rel("DELIVERY_STATUS_RULES_v1.md"),
    "CODEBASE_DOC_SOP": codebase_doc_rel("00_standards/CODEBASE_DOC_SOP_v1.md"),
    "CODEBASE_DOC_STATUS_RULES": codebase_doc_rel("00_standards/CODEBASE_DOC_STATUS_RULES_v1.md"),
    "EXISTING_REPO_WORKFLOW_SOP": system_doc_rel("EXISTING_REPO_WORKFLOW_SOP.md"),
    "DELIVERY_VALIDATION_TEMPLATE": system_doc_rel("templates/delivery/08_delivery_validation_template.md"),
    "DELIVERY_TEMPLATE_REGISTRY": system_doc_rel("templates/delivery/01_delivery_template_registry.md"),
    "DELIVERY_INITIATIVE_TEMPLATE": system_doc_rel("templates/delivery/02_delivery_initiative_template.md"),
    "DELIVERY_PLAN_TEMPLATE": system_doc_rel("templates/delivery/03_delivery_plan_template.md"),
    "DELIVERY_TASK_GRAPH_TEMPLATE": system_doc_rel("templates/delivery/04_delivery_task_graph_template.md"),
    "DELIVERY_TASK_TEMPLATE": system_doc_rel("templates/delivery/05_delivery_task_template.md"),
    "DELIVERY_IMPL_TEMPLATE": system_doc_rel("templates/delivery/06_delivery_impl_template.md"),
    "DELIVERY_REVIEW_TEMPLATE": system_doc_rel("templates/delivery/07_delivery_review_template.md"),
    "DELIVERY_MEMORY_TEMPLATE": system_doc_rel("templates/delivery/09_delivery_memory_template.md"),
    "CODEBASE_TEMPLATE_REGISTRY": system_doc_rel("templates/codebase/01_codebase_template_registry.md"),
    "CODEBASE_INVENTORY_TEMPLATE": system_doc_rel("templates/codebase/02_codebase_inventory_template.md"),
    "CODEBASE_MODULE_TEMPLATE": system_doc_rel("templates/codebase/03_codebase_module_template.md"),
    "CODEBASE_COMPONENT_TEMPLATE": system_doc_rel("templates/codebase/04_codebase_component_template.md"),
    "CODEBASE_CHANGE_TEMPLATE": system_doc_rel("templates/codebase/05_codebase_change_template.md"),
    "CODEBASE_INVENTORY": codebase_doc_rel("01_inventory/codebase_inventory.md"),
}


@dataclass
class PreparedStepExecution:
    step_dir: Path
    action_name: str = ""
    post_action: str = ""  # Action to run after LLM completes (for LLM_Action type)
    coder_used: str = "action"
    coder_alias: str | None = None
    coder_config: dict[str, Any] | None = None
    context: dict[str, str] = field(default_factory=dict)
    prompt_path: Path | None = None
    prompt_text: str = ""
    checksum: str = ""


def _prepare_step_execution(
    *,
    template_group: str,
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
    workflow_key_override: str = "",
    cli_coder: str | None = None,
) -> PreparedStepExecution:
    missing_required = _missing_artifacts(step_cfg.get("required_inputs", []), state)
    if missing_required:
        raise FileNotFoundError(
            f"Cannot run step {step!r}. Missing required input artifact(s): {', '.join(missing_required)}"
        )

    check_preflight_artifact_status(step_cfg=step_cfg, state=state)
    ensure_planning_task_queue_integrity(state, step=step)
    ensure_execution_task_binding_integrity(state, step=step)

    step_dir = make_step_dir(group_cfg, state, step)
    step_dir.mkdir(parents=True, exist_ok=True)
    # Ensure PROGRESS_FILE resolves to the same step directory as make_step_dir
    state["backend_step_dir_rel"] = str(step_dir)

    context = build_context(state, step=step, step_cfg=step_cfg)
    context["WORKFLOW_KEY_OVERRIDE"] = workflow_key_override or ""

    loop_ctx = state.get("loop_context", {})
    if step_cfg.get("loop_returns_to") and loop_ctx.get("active") and loop_ctx.get("loop_source_review"):
        context["REVIEW_FILE"] = loop_ctx["loop_source_review"]

    action_name = str(step_cfg.get("action") or "")
    if action_name:
        return PreparedStepExecution(
            step_dir=step_dir,
            action_name=action_name,
            coder_used="action",
            context=context,
        )

    coder_used, coder_alias, coder_config = _resolve_step_coder(
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        cli_coder=cli_coder,
    )
    model_id = (coder_config or {}).get("model") or None
    prompt_path = resolve_prompt_path(step_cfg=step_cfg, coder=coder_used, model_id=model_id)
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    template_text = prompt_path.read_text(encoding="utf-8")
    template_text = _augment_generated_doc_prompt(
        template_text,
        template_group=template_group,
        step=step,
        step_cfg=step_cfg,
        state=state,
    )
    prompt_text = render_prompt(template_text, context, step_cfg=step_cfg)
    checksum = prompt_checksum(prompt_text)
    _save_text(step_dir / "prompt.txt", prompt_text)

    return PreparedStepExecution(
        step_dir=step_dir,
        coder_used=coder_used,
        coder_alias=coder_alias,
        coder_config=coder_config,
        context=context,
        prompt_path=prompt_path,
        prompt_text=prompt_text,
        checksum=checksum,
        post_action=str(step_cfg.get("post_action") or ""),
    )


def _augment_generated_doc_prompt(
    template_text: str,
    *,
    template_group: str,
    step: str,
    step_cfg: dict[str, Any],
    state: dict[str, Any],
) -> str:
    if template_group not in MASTER_BOOTSTRAP_WORKFLOWS and template_group != EXECUTION_SCAFFOLD_WORKFLOW:
        return template_text

    banner = managed_banner(workflow=template_group, step=step)
    manifest = generated_doc_manifest(template_group=template_group, state=state)
    return (
        template_text
        + "\n\n## Workflow-Generated Document Rule\n\n"
        + "- Every markdown document written by this step is workflow-generated and protected.\n"
        + f"- Add this exact banner immediately after the frontmatter of each generated markdown file:\n\n{banner}"
        + "- If the file uses frontmatter, include `managed_by: workflow-generated` in that frontmatter.\n"
        + "- Do not rename the target files.\n"
        + "- Use the generated-doc inventory below as the authoritative protected set for this workflow.\n\n"
        + manifest
    )


def _execute_prepared_step(
    *,
    prepared: PreparedStepExecution,
    template_group: str,
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
    effective_root: Path,
) -> StepResult:
    if prepared.action_name:
        return run_action(
            action_name=prepared.action_name,
            state=state,
            step=step,
            step_cfg=step_cfg,
            step_dir=prepared.step_dir,
            project_root=effective_root,
            context=prepared.context,
        )

    # LLM step (with optional post_action for LLM_Action type)
    result = run_step(
        group_name=template_group,
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        coder=prepared.coder_used,
        coder_config=prepared.coder_config,
        prompt_text=prepared.prompt_text,
        checksum=prepared.checksum,
        step_dir=prepared.step_dir,
        project_root=effective_root,
        context=prepared.context,
    )

    # Run post_action if configured and LLM step succeeded (for LLM_Action type)
    if prepared.post_action and result.status == "APPROVED":
        print(f"[step_runner] Running post_action={prepared.post_action} after LLM step", flush=True)
        post_result = run_action(
            action_name=prepared.post_action,
            state=state,
            step=step,
            step_cfg=step_cfg,
            step_dir=prepared.step_dir,
            project_root=effective_root,
            context=prepared.context,
        )
        # Merge artifacts from post_action into result
        if post_result.artifacts:
            result.artifacts.update(post_result.artifacts)
        # If post_action failed, update result status
        if post_result.status != "APPROVED":
            result.status = post_result.status
            result.remark = f"{result.remark}; post_action: {post_result.remark}"
            if post_result.reject_code:
                result.reject_code = post_result.reject_code

    return result


def _publish_backend_artifacts(*, state: dict[str, Any], step: str, artifacts: dict[str, str], project_root: Path) -> dict[str, str]:
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
        target_rel = DELIVERY_SCAFFOLD_PUBLISH_PATHS.get(artifact_key)
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


def _execute_backend_step_request(
    *,
    request: ExecutionRequest,
    group_cfg: dict[str, Any],
    step_cfg: dict[str, Any],
    state: dict[str, Any],
    effective_root: Path,
) -> ExecutionResult:
    step = request.step_name
    coder_used = "action"

    try:
        prepared = _prepare_step_execution(
            template_group=request.template_group,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            workflow_key_override=request.workflow_key_override or "",
            cli_coder=request.coder_override or None,
        )
        coder_used = prepared.coder_used
        step_result = _execute_prepared_step(
            prepared=prepared,
            template_group=request.template_group,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            effective_root=effective_root,
        )
        
        # Send step-level notification if configured (for backend/daemon mode)
        if step_result.status == "APPROVED":
            print(f"[backend_mode] Step {step} completed successfully, checking for notifications", flush=True)
            
            # Update timestamp for duration calculation
            from .job_state import now_iso
            state["updated_at"] = now_iso()
            
            # Ensure state has workflow info for notifications
            if "workflow_name" not in state:
                state["workflow_name"] = request.template_group
            if "template_group" not in state:
                state["template_group"] = request.template_group
            
            print(f"[backend_mode] State keys: {list(state.keys())}", flush=True)
            print(f"[backend_mode] workflow_name={state.get('workflow_name')}, template_group={state.get('template_group')}", flush=True)
            print(f"[backend_mode] created_at={state.get('created_at')}, updated_at={state.get('updated_at')}", flush=True)

            from .notification_manager import send_step_notification
            send_step_notification("STEP_COMPLETED", state, step, step_cfg)
    except PreflightBlockedError as exc:
        failure = ExecutionFailure(
            failure_class="HUMAN_RETRY_REQUIRED",
            failure_code="PREFLIGHT_STATUS_NOT_APPROVED",
            failure_reason=str(exc),
            failure_source="runner",
        )
        return ExecutionResult(status="failed", outcome="preflight_blocked", step_name=step, coder_used=coder_used, failure=failure)
    except Exception as exc:
        envelope = classify_pre_run_failure(exc)
        failure = ExecutionFailure(
            failure_class=envelope["failure_class"],
            failure_code=envelope["failure_code"],
            failure_reason=envelope["failure_reason"],
            failure_source=envelope["failure_source"],
        )
        return ExecutionResult(status="failed", outcome="failed", step_name=step, coder_used=coder_used, failure=failure)

    review = None
    if step.startswith("review_") or step.startswith("validator"):
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
                    _update_document_status(file_path=artifact_path, new_status="changes_requested")

    produced_status = step_cfg.get("produced_document_status") or {}
    produced_artifact = str(produced_status.get("artifact") or "").strip()
    produced_required_status = str(produced_status.get("required_status") or "").strip()
    if produced_artifact and produced_required_status:
        artifact_path = (step_result.artifacts or {}).get(produced_artifact) or state.get("artifacts", {}).get(produced_artifact)
        if artifact_path:
            _update_document_status(file_path=artifact_path, new_status=produced_required_status)

    published_artifacts = _publish_backend_artifacts(
        state=state,
        step=step,
        artifacts=step_result.artifacts,
        project_root=effective_root,
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
            "step_dir": _safe_relative_to(prepared.step_dir, JOBS_ROOT),
        },
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_delivery_folders(target_root: Path) -> None:
    """Create the standard delivery and codebase documentation structure."""
    for folder in RUN_AGENT_REQUIRED_DOC_DIRS:
        (target_root / folder).mkdir(parents=True, exist_ok=True)


def _load_group(
    group_name: str,
    workspace_root: Path | None = None,
    workflow_root: Path | None = None,
) -> dict:
    """Load a template group config.

    Resolution order:
    1. ``<workflow_root>/<group_name>/workflow.toml`` — plugin workflow
       package (self-contained; runtime source of truth).  If the
       directory exists but the file is missing, fails fast.
    2. ``TEMPLATE_GROUPS[group_name]`` — fallback for template_groups.py
       entries (no ``workflow.toml`` package).

    There is **no** fallback from the global path to a project-local
    ``workflows/`` directory.  For runtime, the package must be present
    in the global runner home (seeded via ``ukbe-run-agent init``).
    """
    # --- Direct path check (plugin package) ---------------------------
    if workflow_root is not None:
        pkg_dir = workflow_root / group_name
        manifest = pkg_dir / "workflow.toml"
        if manifest.is_file():
            bundle = load_workflow_package(pkg_dir)
            group_dict = bundle_to_template_group_dict(bundle)
            group_dict["_workflow_bundle"] = bundle
            return group_dict
        if pkg_dir.is_dir():
            # Directory exists but no workflow.toml — broken package
            raise FileNotFoundError(
                f"Plugin workflow directory exists at {pkg_dir} "
                f"but no workflow.toml found."
            )

    # --- Fallback: TEMPLATE_GROUPS ------------------------------------
    bundle = get_workflow_module()
    if bundle is None:
        raise RuntimeError("Workflow module is not loaded. Runtime must use the global workflow bundle.")
    template_groups = bundle.TEMPLATE_GROUPS
    if group_name not in template_groups:
        valid = ", ".join(sorted(template_groups))
        raise ValueError(f"Unknown template group {group_name!r}. Valid groups: {valid}")
    return template_groups[group_name]


def _validate_static_reference_files(workspace_root: Path, group_cfg: dict | None = None, template_group: str = "") -> None:
    # Bootstrap and scaffold workflows generate docs — they don't need pre-existing reference files
    if template_group in ("00_master_docs_bootstrap_v1", "00_master_docs_bootstrap_v2", "10_execution_scaffold_v1", "delivery_scaffold_v1") or template_group.startswith("delivery_scaffold"):
        return

    bundle = get_workflow_module()
    if bundle is None:
        raise RuntimeError("Workflow module is not loaded. Runtime must use the global workflow bundle.")

    reference_files = bundle.REFERENCE_FILES
    if group_cfg is not None and "reference_files" in group_cfg:
        reference_files = group_cfg.get("reference_files") or {}

    # Separate reference files into two categories:
    # 1. Global bundle files: System governance docs (WORKFLOW_SOP, DELIVERY_AGENTS_MD, etc.)
    # 2. Repo-based files: Codebase documentation generated by execution scaffold workflows
    
    # These are repo-based artifacts, NOT part of the global bootstrap bundle
    REPO_BASED_KEYS = {
        "CODEBASE_DOC_SOP",
        "CODEBASE_DOC_STATUS_RULES",
        "CODEBASE_INVENTORY",
    }

    global_bundle_root = core_bundles_root() / "current"
    missing = []

    for key, rel_path in reference_files.items():
        if key in REPO_BASED_KEYS:
            # Check repo-based files at workspace root
            file_path = workspace_root / rel_path
            if not file_path.exists():
                missing.append(f"{key}: {rel_path} (not found in workspace at {workspace_root})")
        else:
            # Check global bundle files
            # The rel_path might be like "docs/system/00_governance/bootstrap/DELIVERY_AGENTS.md"
            # but in the global bundle it's just "DELIVERY_AGENTS_MD" (no extension, flat structure)
            
            # Extract just the filename from the path
            filename = Path(rel_path).name
            
            # Try multiple possible locations in the global bundle
            possible_paths = [
                global_bundle_root / filename,  # Direct match (e.g., DELIVERY_AGENTS_MD)
                global_bundle_root / f"{filename}.md",  # With .md extension
                global_bundle_root / rel_path,  # Full relative path (if bundle has subdirs)
            ]
            
            # Check if any of the possible paths exist
            if not any(p.exists() for p in possible_paths):
                missing.append(f"{key}: {rel_path} (not found in global bundle at {global_bundle_root})")

    if missing:
        raise FileNotFoundError("Missing static reference file(s):\n" + "\n".join(missing))


def _missing_artifacts(keys: list[str], state: dict) -> list[str]:
    missing = []
    if "artifacts" not in state or state["artifacts"] is None:
        state["artifacts"] = {}
    artifacts = state["artifacts"]
    known_paths = known_artifact_paths()
    for key in keys:
        value = artifacts.get(key)
        if value and (ARTIFACT_ROOT / value).exists():
            continue
        # Auto-discover: check if artifact exists at known path on disk
        known_path = known_paths.get(key)
        if known_path and (ARTIFACT_ROOT / known_path).exists():
            # Auto-populate the artifact in job state
            artifacts[key] = known_path
            continue
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
) -> tuple[str, str | None, dict | None]:
    """Returns (resolved_coder, original_alias, resolved_config)."""
    coder_cfg = step_cfg.get("coder", {})
    default_coder = coder_cfg.get("default")
    allowed_coders = coder_cfg.get("allowed", [])
    chosen = cli_coder.strip() if cli_coder else default_coder
    if not chosen:
        raise ValueError(f"No coder specified and no default coder configured for step {step!r}")

    original = chosen
    resolved_config = resolve_coder(chosen)
    if resolved_config is not None:
        actual_coder = resolved_config.get("coder", chosen)
        log_resolver(original, f"{actual_coder} (model={resolved_config.get('model', '')})", is_alias=True)
        if shutil.which(actual_coder) is None:
            raise FileNotFoundError(f"Coder executable not found: {actual_coder!r} (alias {original!r})")
        chosen = actual_coder
    else:
        log_resolver(original, original, is_alias=False)
        if shutil.which(chosen) is None:
            raise FileNotFoundError(f"Coder executable not found in PATH: {chosen!r}")

    # Check the original name (alias or direct) against the allowed list.
    # The allowed list contains alias names (e.g. 'qwen-architect') or direct
    # coder names (e.g. 'claude', 'codex'), NOT resolved backend executables.
    check_name = original if original != chosen else chosen
    if allowed_coders and check_name not in allowed_coders:
        raise ValueError(f"Coder {check_name!r} is not allowed for step {step!r}. Allowed: {allowed_coders}")
    if coder_cfg.get("must_differ_from_previous_step"):
        idx = group_cfg["steps"].index(step)
        if idx > 0:
            prev_step = group_cfg["steps"][idx - 1]
            prev_coder = state.get("step_coders", {}).get(prev_step)
            if prev_coder and chosen == prev_coder:
                raise ValueError(
                    f"Coder {chosen!r} is not allowed for step {step!r} because it matches previous step {prev_step!r}"
                )
    return chosen, original if original != chosen else None, resolved_config


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


def _step_progress_parts(group_cfg: dict[str, Any], step: str | None) -> tuple[int | None, int]:
    steps = list(group_cfg.get("steps") or [])
    total = len(steps)
    if not step or step not in steps:
        return None, total
    return steps.index(step) + 1, total


def _step_progress_label(group_cfg: dict[str, Any], step: str | None) -> str:
    index, total = _step_progress_parts(group_cfg, step)
    if index is None or total <= 0:
        return "step ? of ?"
    return f"step {index} of {total}"


def _format_job_status_summary(state: dict, group_cfg: dict) -> str:
    current_step = state.get("current_step")
    current_progress = _step_progress_label(group_cfg, current_step)
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


def _save_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def _worker_step_dir(*, run: dict[str, Any], step_run: dict[str, Any]) -> Path:
    workflow_name = str(run.get("workflow_name") or "")
    run_code = str(run.get("run_code") or run.get("id") or "backend-run")
    sequence_no = int(step_run.get("sequence_no") or 1)
    step_name = str(step_run.get("step_name") or "unknown_step")
    return JOBS_ROOT / workflow_name / run_code / f"{sequence_no:02d}_{step_name}"


def _build_worker_crash_result(*, run: dict[str, Any], step_run: dict[str, Any], error: Exception) -> dict[str, Any]:
    step_name = str(step_run.get("step_name") or "unknown_step")
    step_dir = _worker_step_dir(run=run, step_run=step_run)
    diagnostics = {
        "workflow_run_id": str(run.get("id") or ""),
        "workflow_step_run_id": str(step_run.get("id") or ""),
        "job_id": str(run.get("run_code") or ""),
        "step_dir": _safe_relative_to(step_dir, JOBS_ROOT),
        "worker_error": repr(error),
    }
    step_dir.mkdir(parents=True, exist_ok=True)
    _save_json(
        step_dir / "worker_error.json",
        {
            "step_name": step_name,
            "worker_error": repr(error),
            "diagnostics": diagnostics,
            "failed_at": _now_iso(),
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


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
