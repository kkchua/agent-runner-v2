#!/usr/bin/env python3
"""
run_agent.py â€” Main CLI entry point for agent_runner_v2.

Orchestration only: load config â†’ resolve job â†’ preflight â†’ prompt â†’ run_step â†’ route.

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
import sys
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
from .failure_runtime import append_failure_history, clear_last_failure, set_last_failure
from .job_state import (
    REVIEW_DECISIONS,
    HUMAN_DECISIONS,
    FINAL_DECISION_SOURCES,
    advance_step,
    apply_task_execution_binding,
    approve_step,
    build_failure_envelope,
    check_preflight_artifact_status,
    classify_pre_run_failure,
    create_job,
    create_step_dir,
    CURRENT_SCHEMA_VERSION,
    default_task_execution_binding,
    default_review_state,
    default_usage_summary,
    ensure_backward_compatible_state,
    enforce_retry_limit_before_run,
    find_matching_active_job,
    find_matching_completed_job,
    force_approve_step,
    get_job_status,
    infer_seed_identity,
    load_job,
    migrate_job_state,
    prepare_state_for_retry,
    recover_exhausted_planning_job,
    reconcile_job_state,
    reapply_routing,
    save_job,
    set_job_status,
    _update_document_status,
)
from .coder_registry import resolve_coder_role, resolve_role_policy
from .runner_logger import log_resolver
from .runtime_context import (
    PROJECT_ROOT, RUNNER_ROOT, JOBS_ROOT, ARTIFACT_ROOT, PACKAGE_ROOT,
    format_report_artifacts, format_report_path,
    get_workflow_module,
    set_context, set_workflow_module, set_delivery_root,
)
from .constants import RUN_AGENT_REQUIRED_DOC_DIRS, delivery_doc_rel
from .doc_paths import repo_doc_rel
from .path_catalog import get_master_docs_output_paths, known_artifact_paths, legacy_artifact_paths
from .task_runtime import (
    build_task_execution_binding,
    build_task_execution_binding_from_ids,
    ensure_execution_task_binding_integrity,
    ensure_planning_task_queue_integrity,
    task_execution_binding_current_item,
)
from .routing_runtime import predict_next_step_after_approved
from .step_runner import (
    StepResult,
    build_context,
    prompt_checksum,
    render_prompt,
    resolve_prompt_path,
    run_action,
    run_step,
)
from .documentation_guardrails import EXECUTION_SCAFFOLD_WORKFLOWS, MASTER_BOOTSTRAP_WORKFLOWS
from .workflow_packages.loader import bundle_to_template_group_dict, load_workflow_package

__version__ = "0.3.0"
from .execution_request import ExecutionRequest
from .execution_result import ExecutionFailure, ExecutionResult
from . import daemon_runtime as _daemon_runtime
from . import cli_runtime as _cli_runtime
from . import manual_runtime as _manual_runtime
from . import manual_runtime_deps as _manual_runtime_deps
from . import runtime_utils as _runtime_utils
from . import shared_runtime_deps as _shared_runtime_deps
from . import step_execution_runtime as _step_execution_runtime
from . import transition_runtime as _transition_runtime
from . import workflow_runtime as _workflow_runtime
from .execution_core import execute_routed_step, invoke_prepared_step
from .workflow_router import route_after_failure, route_after_step
from .workflow_specs import reconcile_step_execution_spec
from .workflow_specs import build_step_execution_spec, get_template_group_cfg

make_step_dir = create_step_dir


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_relative_to(path: Path, base: Path) -> str:
    return _runtime_utils.safe_relative_to(path, base)


def _save_text(path: Path, content: str) -> None:
    _runtime_utils.save_text(path, content)


def _save_json(path: Path, data: Any) -> None:
    _runtime_utils.save_json(path, data)


def _now_iso() -> str:
    return _runtime_utils.now_iso()


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
        _cli_runtime.print_failure(
        remark=remark,
        state=state,
        template_group=template_group,
        step=step,
        coder_used=coder_used,
        failure_class=failure_class,
        failure_code=failure_code,
        failure_source=failure_source,
        hooks=_manual_runtime_deps,
    )


def _step_progress_parts(group_cfg: dict[str, Any], step: str | None) -> tuple[int | None, int]:
    return _cli_runtime.step_progress_parts(group_cfg, step)


def _step_progress_label(group_cfg: dict[str, Any], step: str | None) -> str:
    return _cli_runtime.step_progress_label(group_cfg, step)


def _format_job_status_summary(state: dict[str, Any], group_cfg: dict) -> str:
    return _cli_runtime.format_job_status_summary(state, group_cfg, get_job_status=get_job_status)


def _mark_review_started(state: dict[str, Any], *, step: str, step_cfg: dict, coder_used: str) -> None:
    _transition_runtime.mark_review_started(
        state=state,
        step=step,
        step_cfg=step_cfg,
        coder_used=coder_used,
        default_review_state=default_review_state,
    )


def _worker_command(
    *,
    backend_url: str,
    worker_id: str,
    host_name: str | None,
    poll_seconds: int,
    once: bool,
    engine_root: str | None = None,
    worker_label: str = "live",
) -> int:
    from .daemon import main as _daemon_main

    daemon_argv = [worker_id]
    if worker_label:
        daemon_argv.extend(["--worker-label", worker_label])
    if backend_url:
        daemon_argv.extend(["--backend-url", backend_url])
    if poll_seconds:
        daemon_argv.extend(["--poll-seconds", str(poll_seconds)])
    if once:
        daemon_argv.append("--once")
    if engine_root:
        daemon_argv.extend(["--engine-root", engine_root])
    return _daemon_main(daemon_argv)


def _execute_step_command(request_path: Path, result_path: Path | None = None) -> int:
    payload = {
        "status": "failed",
        "outcome": "failed",
        "remark": (
            "The legacy 'execute-step' command is no longer supported. "
            "Use 'ukbe-run-agent daemon' so claimed backend work executes through "
            "the standard 'ukbe-run-agent run' path."
        ),
        "failure": {
            "failure_class": "FATAL",
            "failure_code": "LEGACY_EXECUTE_STEP_UNSUPPORTED",
            "failure_reason": "execute-step command has been retired in favor of daemon -> run delegation",
            "failure_source": "runner",
        },
        "diagnostics": {
            "request_file": str(request_path),
            "result_file": str(result_path) if result_path else None,
        },
    }
    if result_path is not None:
        result_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 2


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _resolve_workflow_bundle_root(workspace_root: Path, workflow_name: str, config: dict) -> Path:
    """Resolve the active workflow bundle root from the global runner home."""
    return resolve_workflow_root(workspace_root, workflow_name, config=config)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw = list(argv if argv is not None else sys.argv[1:])
    if not raw or raw[0].startswith("-"):
        raw = ["run", *raw]

    command = raw[0]
    if command == "init":
        p = argparse.ArgumentParser(description="Initialize the runner home from the current repository bootstrap snapshot.")
        p.add_argument("--workflow", default="default", help="Workflow name to seed.")
        p.add_argument("--bundle-domain", default="general", help="Domain bundle to record for this workspace (e.g. frontend, backend, content).")
        p.add_argument("--bundle-profile", default="core+workflow", help="Bundle profile to record for this workspace.")
        ns = p.parse_args(raw[1:])
        ns.command = "init"
        return ns

    if command == "bootstrap-publish":
        p = argparse.ArgumentParser(description="Publish the current repository bootstrap snapshot from the current working directory.")
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
        from .config_loader import load_runner_config as _load_runner_config
        _cfg = _load_runner_config()
        p = argparse.ArgumentParser(description="Single-shot backend poll (claim one step and exit).")
        p.add_argument("--backend-url", default=_os.environ.get("AGENT_RUNNER_BACKEND_URL") or str(_cfg.get("backend_url") or "") or "http://127.0.0.1:8100")
        p.add_argument("--worker-id", default=_os.environ.get("AGENT_RUNNER_WORKER_ID", ""))
        p.add_argument("--host-name", default="")
        p.add_argument("--engine-root", default=str(_cfg.get("engine_root") or ""))
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

    if command == "stop":
        ns = argparse.Namespace()
        ns.command = "stop"
        ns.stop_argv = raw[1:]
        return ns

    if command == "console":
        ns = argparse.Namespace()
        ns.command = "console"
        ns.console_argv = raw[1:]
        return ns

    if command == "codebase-init":
        ns = argparse.Namespace()
        ns.command = "codebase-init"
        ns.codebase_init_argv = raw[1:]
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
    p.add_argument("--job-no", default="", help="Backend job number/run_code (used as job_id in daemon mode)")
    p.add_argument("--mode", choices=["manual", "daemon"], default="manual",
                   help="Execution mode: manual (auto-generate job ID) or daemon (use provided --job-no)")
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
    cwd_root = Path.cwd().resolve()
    if args.command == "init":
        workspace_root = cwd_root
        result = init_workspace(
            workspace_root,
            workflow_name=args.workflow or "default",
            domain=args.bundle_domain or "general",
            bundle_profile=args.bundle_profile or "core+workflow",
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "bootstrap-publish":
        workspace_root = cwd_root
        result = publish_bootstrap_bundle(
            workspace_root,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "daemon":
        from .daemon import main as _daemon_main
        return _daemon_main(args.daemon_argv)

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
        return _worker_command(
            backend_url=args.backend_url,
            worker_id=args.worker_id,
            host_name=args.host_name or None,
            poll_seconds=1,
            once=True,
            engine_root=args.engine_root or None,
            worker_label=args.worker_label,
        )

    if args.command == "execute-step":
        result_path = Path(args.result_file).resolve() if args.result_file else None
        return _execute_step_command(Path(args.request_file).resolve(), result_path)

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

    if args.command == "stop":
        from .stop_commands import main as _stop_main
        return _stop_main(args.stop_argv)

    if args.command == "console":
        from .console_commands import main as _console_main
        return _console_main(args.console_argv)

    if args.command == "codebase-init":
        from .codebase_init_commands import main as _codebase_init_main
        return _codebase_init_main(args.codebase_init_argv)

    if args.project_root and Path(args.project_root).resolve() != cwd_root:
        raise ValueError(
            f"--project-root is fixed to the current repository root under the single-repo contract: {cwd_root}"
        )
    if args.target_project_root and Path(args.target_project_root).resolve() != cwd_root:
        raise ValueError(
            f"--target-project-root is not supported under the single-repo contract: {cwd_root}"
        )

    workspace_root = cwd_root
    config = load_project_config(workspace_root)
    workflow_name = args.workflow or str(config.get("default_workflow") or "default")
    workflow_bundle_root = _resolve_workflow_bundle_root(workspace_root, workflow_name, config)
    workflow_module = load_workflow_module(workspace_root, workflow_name, config=config)

    delivery_root = workspace_root
    if (
        args.template_group.startswith("delivery_scaffold")
        or args.template_group.startswith("codebase_")
        or args.template_group.startswith("system_docs_")
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

    effective_root = workspace_root

    state: dict | None = None
    group_cfg: dict | None = None
    step: str | None = None
    coder_used = ""
    coder_config: dict | None = None
    max_rejects = 0
    original_current_step: str | None = None

    try:
        group_cfg = _load_group(args.template_group, workspace_root=workspace_root, workflow_root=workflow_bundle_root)
        _validate_static_reference_files(workspace_root, group_cfg, template_group=args.template_group)

        if (args.task_graph_id or args.task_node_id) and args.template_group != "task_execution_v1":
            raise ValueError("--task-graph-id/--task-node-id are supported only for template group 'task_execution_v1'.")
        if bool(args.task_graph_id) != bool(args.task_node_id):
            raise ValueError("--task-graph-id and --task-node-id must be provided together.")

        # --- Admin commands ---
        admin_resolution = _cli_runtime.handle_admin_command(
            args=args,
            group_cfg=group_cfg,
            hooks=_manual_runtime_deps,
        )
        if admin_resolution.handled and not admin_resolution.continue_execution:
            return admin_resolution.exit_code
        if admin_resolution.continue_execution:
            state = admin_resolution.state
            step = admin_resolution.step
            args.single_step = False

        if state is None or step is None:
            resolution = _manual_runtime.resolve_manual_run(
                args=args,
                group_cfg=group_cfg,
                hooks=_manual_runtime_deps,
                mode=args.mode,
            )
            state = resolution.state
            step = resolution.step
            original_current_step = resolution.original_current_step
            if resolution.terminal_payload is not None:
                print(json.dumps(resolution.terminal_payload, indent=2))
                return 0

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
            project_root=effective_root,
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

    # Mark review state started (job.json only â€” no markdown writes in v2)
    _mark_review_started(state, step=step, step_cfg=step_cfg, coder_used=coder_used)
    save_job(args.template_group, state["job_id"], state)

    routed = execute_routed_step(
        executor=_execute_prepared_step,
        failure_router=route_after_failure,
        step_router=route_after_step,
        prepared=prepared,
        group_name=args.template_group,
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        coder_used=coder_used,
        max_rejects=max_rejects,
        effective_root=effective_root,
    )
    if routed.failure is not None:
        actor = f"action={prepared.action_name}" if prepared.action_name else f"coder={coder_used}"
        print(f"[{_now_iso()}] {actor} step={step} status=FAILED error={type(routed.failure.exception).__name__}", flush=True)
        state = routed.state
        print(json.dumps({
            "status": "REJECTED",
            "remark": routed.failure.failure_reason,
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
        return routed.exit_code

    assert routed.step_result is not None
    step_result = routed.step_result
    state = routed.state
    exit_code = routed.exit_code
    report_artifacts = format_report_artifacts(
        step_result.artifacts,
        project_root=effective_root,
        runtime_root=JOBS_ROOT,
    )
    report_meta_json_path = format_report_path(
        step_result.meta_json_path,
        project_root=effective_root,
        runtime_root=JOBS_ROOT,
    )

    # Save result.json for diagnostics
    _save_json(step_dir / "result.json", {
        "status": step_result.status,
        "remark": step_result.remark,
        "artifacts": report_artifacts,
        "reject_code": step_result.reject_code,
        "meta_json_path": report_meta_json_path,
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
        "artifacts": report_artifacts,
        "meta_json_path": report_meta_json_path,
        "step_dir": _safe_relative_to(step_dir, JOBS_ROOT),
    }, indent=2))
    return exit_code


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
        hooks=_shared_runtime_deps,
    )


PreparedStepExecution = _step_execution_runtime.PreparedStepExecution


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
) -> PreparedStepExecution:
    return _step_execution_runtime.prepare_step_execution(
        template_group=template_group,
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        project_root=project_root,
        workflow_key_override=workflow_key_override,
        cli_coder=cli_coder,
        hooks=_shared_runtime_deps,
    )


def _augment_generated_doc_prompt(
    template_text: str,
    *,
    template_group: str,
    step: str,
    step_cfg: dict[str, Any],
    state: dict[str, Any],
) -> str:
    return _step_execution_runtime.augment_generated_doc_prompt(
        template_text,
        template_group=template_group,
        step=step,
        step_cfg=step_cfg,
        state=state,
    )


def _generated_doc_frontmatter_contract(
    *,
    template_group: str,
    step: str,
    step_cfg: dict[str, Any],
    state: dict[str, Any],
) -> str:
    return _step_execution_runtime.generated_doc_frontmatter_contract(
        template_group=template_group,
        step=step,
        step_cfg=step_cfg,
        state=state,
    )


def _master_bootstrap_frontmatter_rows(
    *,
    template_group: str,
    step_cfg: dict[str, Any],
    state: dict[str, Any],
) -> list[tuple[str, str, str]]:
    return _step_execution_runtime.master_bootstrap_frontmatter_rows(
        template_group=template_group,
        step_cfg=step_cfg,
        state=state,
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
    return _step_execution_runtime.execute_prepared_step(
        prepared=prepared,
        template_group=template_group,
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        effective_root=effective_root,
        hooks=_shared_runtime_deps,
    )


def _resolve_step_coder(
    *,
    group_cfg: dict,
    state: dict,
    step: str,
    step_cfg: dict,
    cli_coder: str | None,
) -> tuple[str, str | None, str | None, dict | None]:
    return _step_execution_runtime.resolve_step_coder(
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        cli_coder=cli_coder,
    )


def _ensure_delivery_folders(target_root: Path) -> None:
    _workflow_runtime.ensure_delivery_folders(target_root)


def _load_group(
    group_name: str,
    workspace_root: Path | None = None,
    workflow_root: Path | None = None,
) -> dict:
    return _workflow_runtime.load_group(
        group_name,
        workspace_root=workspace_root,
        workflow_root=workflow_root,
    )


def _validate_static_reference_files(workspace_root: Path, group_cfg: dict | None = None, template_group: str = "") -> None:
    _workflow_runtime.validate_static_reference_files(
        workspace_root,
        group_cfg=group_cfg,
        template_group=template_group,
    )


def _missing_artifacts(keys: list[str], state: dict) -> list[str]:
    return _workflow_runtime.missing_artifacts(keys, state)


def _parse_key_value_pairs(values: list[str]) -> dict[str, str]:
    return _workflow_runtime.parse_key_value_pairs(values)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        try:
            from .coder_adapters import abort_active_coder_processes
            abort_active_coder_processes(reason="KeyboardInterrupt")
        except Exception:
            pass
        sys.exit(130)
