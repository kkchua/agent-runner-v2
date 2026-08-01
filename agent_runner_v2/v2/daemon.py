"""V2 daemon supervisor — thin claim→spawn→report worker loop.

Architecture reference:
    docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260801-002_platform-v2-architecture-redesign.md

The V2 backend handles all routing, action detection, and stop requests.
The daemon only needs to: claim → spawn → report outcome.

No separate approval polling, no __run_control flag parsing,
no terminal_run_ids safety net.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..daemon import (
    ChildExecution,
    SupervisorConfig,
    _DaemonLogger,
    _resolve_subprocess_cwd,
)


def _spawn_child_v2(
    *,
    claim: dict,
    runtime_root: Path,
    cli_pythonpath: str | None,
    logger: "_DaemonLogger",
    v2_backend_url: str,
) -> "ChildExecution":
    """Spawn a child process for V2 daemon mode.

    Builds CLI args directly from V2 claim data. The child process reports
    its own outcome to V2 backend via run_agent.py's V2 sync path.

    For new jobs (no existing job folder), passes --start-step so the CLI
    knows which step to execute regardless of whether it's the init step.
    """
    from ..job_state import job_dir

    run = claim["run"]
    step_run = claim["step_run"]
    step_run_id = str(step_run["id"])
    run_id = str(run["id"])
    run_code = str(run.get("run_code", ""))
    workflow_name = str(run.get("workflow_name", ""))
    step_name = str(step_run.get("step_name", ""))
    project_root = str(run.get("project_root") or ".")

    child_dir = runtime_root / step_run_id
    child_dir.mkdir(parents=True, exist_ok=True)

    # Determine if this is a new job or existing job
    job_id_to_pass = ""  # Default: empty = new job
    if run_code and workflow_name:
        potential_job_dir = job_dir(workflow_name, run_code)
        if potential_job_dir.exists():
            job_id_to_pass = run_code

    # Build CLI args
    cli_args = [
        sys.executable, "-m", "agent_runner_v2.run_agent", "run",
        "--project-root", project_root,
        "--template-group", workflow_name,
        "--mode", "daemon",
        "--job-id", job_id_to_pass,
        "--job-no", run_code,
        "--job", step_name,
    ]

    # For new jobs, pass --start-step so CLI accepts non-init steps.
    # The backend is authoritative — it already validated the step.
    if not job_id_to_pass:
        cli_args.extend(["--start-step", step_name])

    # For PROCESS_ACTION, add the action flag
    action_flag = claim.get("_v2_action_flag")
    if action_flag:
        action_step = claim.get("_v2_action_step", step_name)
        cli_args.extend([action_flag, action_step])
        feedback = claim.get("_v2_feedback", "")
        if feedback:
            cli_args.extend(["--feedback", feedback])

    env = os.environ.copy()
    if cli_pythonpath:
        env["PYTHONPATH"] = cli_pythonpath + os.pathsep + env.get("PYTHONPATH", "")
    env["AGENT_RUNNER_WORKFLOW_RUN_ID"] = run_id
    env["AGENT_RUNNER_WORKFLOW_STEP_RUN_ID"] = step_run_id
    env["AGENT_RUNNER_V2_BACKEND_URL"] = v2_backend_url

    # Set working directory to project_root so subprocess can find .env
    subprocess_cwd = _resolve_subprocess_cwd(
        project_root=project_root, workspace_root=None,
    )

    logger.log("info", "subprocess_cwd", message=f"Setting subprocess cwd to {subprocess_cwd}", details={
        "project_root": project_root, "subprocess_cwd": str(subprocess_cwd),
    })

    combined_log_path = child_dir / "child.log"
    log_handle = combined_log_path.open("ab")

    try:
        proc = subprocess.Popen(
            cli_args,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=subprocess_cwd,
        )
    except Exception:
        log_handle.close()
        raise

    logger.log("info", "daemon_v2_child_spawned", message=f"spawned child pid={proc.pid}", details={
        "step_run_id": step_run_id, "step_name": step_name,
        "run_code": run_code, "cli_args": " ".join(cli_args),
    })

    return ChildExecution(
        run_id=run_id,
        run_code=run_code,
        step_run_id=step_run_id,
        step_name=step_name,
        run_payload=run,
        step_run_payload=step_run,
        request_payload={"cli_args": cli_args, "project_root": project_root},
        request_path=child_dir / "request.json",
        result_path=child_dir / "result.json",
        combined_log_path=combined_log_path,
        child_event_log_path=child_dir / "child-events.jsonl",
        process=proc,
        started_at_monotonic=time.monotonic(),
        started_at_iso=datetime.now(timezone.utc).isoformat(),
    )


def run_supervisor_v2(*, config: SupervisorConfig, v2_url: str) -> int:
    """V2 supervisor — simplified claim loop using state machine backend.

    The V2 backend handles all routing, action detection, and stop requests.
    The daemon only needs to: claim → spawn → report outcome.

    No separate approval polling, no __run_control flag parsing,
    no terminal_run_ids safety net.
    """
    from .backend_client import V2BackendClient

    logger = _DaemonLogger(config.log_file, config.worker_id)
    client = V2BackendClient(v2_url)
    client.register_worker(
        worker_id=config.worker_id,
        worker_label=config.worker_label,
        capabilities={"mode": ["execute-step-daemon"], "max_parallel": config.max_parallel},
    )
    logger.log("info", "daemon_v2_started", message="V2 worker daemon started", details={
        "v2_backend_url": v2_url, "worker_id": config.worker_id,
    })

    children: dict[str, ChildExecution] = {}
    running = True

    def _handle_signal(_sig, _frame):
        nonlocal running
        running = False
        logger.log("info", "daemon_v2_shutdown_signal", message="received shutdown signal")

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    while running or children:
        # Heartbeat — check for shutdown commands
        try:
            hb_resp = client.heartbeat(
                worker_id=config.worker_id,
                status="idle" if not children else "busy",
            )
            commands = hb_resp.get("commands", [])
            if "shutdown" in commands:
                logger.log("info", "daemon_v2_shutdown_command", message="backend requested shutdown")
                running = False
        except RuntimeError as hb_err:
            logger.log("warning", "daemon_v2_heartbeat_failed", message=str(hb_err))

        # Claim work (single endpoint serves both EXECUTE_STEP and PROCESS_ACTION)
        if running and len(children) < config.max_parallel:
            try:
                work = client.claim_work(worker_id=config.worker_id)
            except RuntimeError as claim_err:
                logger.log("warning", "daemon_v2_claim_failed", message=str(claim_err))
                work = {"work_type": "IDLE"}

            work_type = work.get("work_type", "IDLE")

            if work_type == "IDLE":
                logger.log("info", "daemon_v2_no_work", message="no work available")
            elif work_type in ("EXECUTE_STEP", "PROCESS_ACTION"):
                run_data = work.get("run", {})
                step_data = work.get("step_run", {})
                run_id = str(run_data.get("run_id", ""))
                run_code = str(run_data.get("run_code", ""))
                step_run_id = str(step_data.get("step_run_id", ""))
                step_name = str(step_data.get("step_name", ""))
                workflow_name = str(run_data.get("workflow_name", ""))

                logger.log("info", "daemon_v2_claimed", message=f"claimed {work_type}", details={
                    "run_code": run_code, "step": step_name, "work_type": work_type,
                })

                # Build claim dict for _spawn_child_v2
                claim = {
                    "run": {
                        "id": run_id,
                        "run_code": run_code,
                        "workflow_name": workflow_name,
                        "project_root": run_data.get("project_root"),
                    },
                    "step_run": {
                        "id": step_run_id,
                        "step_name": step_name,
                    },
                }

                # For PROCESS_ACTION, add action info to claim
                if work_type == "PROCESS_ACTION":
                    action = work.get("action", "")
                    flag_map = {
                        "APPROVE": "--approve-step",
                        "REJECT": "--reject-step",
                        "RESUME": "--resume-step",
                        "RETRY": "--retry-step",
                    }
                    flag = flag_map.get(action, "--approve-step")
                    claim["_v2_action_flag"] = flag
                    claim["_v2_action_step"] = step_name
                    claim["_v2_feedback"] = work.get("feedback", "")

                try:
                    child = _spawn_child_v2(
                        claim=claim,
                        runtime_root=config.runtime_dir,
                        cli_pythonpath=config.cli_pythonpath,
                        logger=logger,
                        v2_backend_url=v2_url,
                    )
                    children[child.step_run_id] = child
                except Exception as exc:
                    logger.log("error", "daemon_v2_spawn_failed", message=str(exc), details={
                        "run_code": run_code, "step": step_name,
                    })
                    # Report failure to V2 backend
                    try:
                        client.report_outcome(
                            step_run_id=step_run_id,
                            outcome="failed",
                            failure_class="FATAL",
                            error_message=f"Daemon failed to spawn child: {exc}",
                        )
                    except Exception:
                        pass

            if config.once:
                running = False

        # Check completed children
        for step_run_id in list(children.keys()):
            child = children[step_run_id]
            if child.state in ("completed", "failed", "killed", "timed_out"):
                logger.log("info", "daemon_v2_child_done", message=f"child done: {child.state}", details={
                    "step_run_id": step_run_id, "exit_code": child.exit_code,
                })
                # If child crashed without reporting outcome, report failure to V2 backend
                if child.exit_code and child.exit_code != 0:
                    try:
                        client.report_outcome(
                            step_run_id=step_run_id,
                            outcome="failed",
                            failure_class="HUMAN_RETRY_REQUIRED",
                            error_message=f"Child process exited with code {child.exit_code}",
                        )
                    except Exception as sync_err:
                        logger.log("warning", "daemon_v2_outcome_report_failed", message=str(sync_err), details={
                            "step_run_id": step_run_id,
                        })
                del children[step_run_id]

        time.sleep(config.poll_seconds)

    logger.log("info", "daemon_v2_stopped", message="V2 daemon stopped")
    return 0
