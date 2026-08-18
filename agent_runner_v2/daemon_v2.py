"""V2 worker daemon supervisor — self-contained, no V1 imports.

Architecture: backend-authoritative state machine with pre-execution sync.

The daemon claims work from the V2 backend, fetches the full run state,
writes it to a backend_state.json file, and passes it to the CLI via
AGENT_RUNNER_BACKEND_STATE_FILE env var. The CLI merges backend state
into local job.json before execution, ensuring it always starts fresh.

Entry point: main() — invoked via `ukbe-run-agent daemon [worker-id]`
when v2_backend_url is configured.

Imports only from core modules (config_loader, runtime_context, job_state)
and V2 infrastructure (v2.backend_client). No V1 daemon imports.
"""
from __future__ import annotations

import json
import logging
import logging.handlers
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config_loader import load_runner_config
from .runtime_context import GLOBAL_RUNNER_HOME, JOBS_ROOT, QUEUE_ROOT
from .v2.backend_client import V2BackendClient
from .v2 import queue as outcome_queue


# ---------------------------------------------------------------------------
# Utility functions (self-contained, no V1 imports)
# ---------------------------------------------------------------------------

def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _setting(cfg: dict, env_key: str, config_key: str, default: str) -> str:
    return os.environ.get(env_key) or str(cfg.get(config_key) or default)


def _setting_int(cfg: dict, env_key: str, config_key: str, default: int) -> int:
    return int(_setting(cfg, env_key, config_key, str(default)))


def _step_spec_source(cfg: dict, cli_value: str) -> str:
    value = (cli_value or os.environ.get('STEP_SPEC_SOURCE') or str(cfg.get('step_spec_source') or 'backend')).strip().lower()
    if value not in {'global', 'backend', 'hybrid'}:
        return 'backend'
    return value


def _resolve_engine_pythonpath(cfg: dict, log) -> str | None:
    src = os.environ.get('AGENT_RUNNER_V2_SRC', '').strip()
    if src:
        log('info', 'engine_override', message=f'engine live source override ({src})')
        return src

    version = (cfg.get('engine_version') or '').strip()
    if not version or version == 'SNAPSHOT':
        repo_root = str(cfg.get('repo_root') or '').strip()
        if repo_root:
            log('info', 'engine_mode', message=f'engine version={version!r} using repo_root from config: {repo_root}')
            return repo_root
        log('info', 'engine_mode', message=f'engine version={version!r} using ambient PYTHONPATH')
        return None

    global_dir = Path.home() / '.ukbe-runner' / 'engine' / 'versions' / version
    if global_dir.exists():
        log('info', 'engine_resolved', message=f'engine {version!r} resolved from global store', details={'path': str(global_dir)})
        return str(global_dir)

    log('error', 'engine_missing', message=f'engine version {version!r} not found', details={'global_path': str(global_dir)})
    return None


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(payload, ensure_ascii=True, sort_keys=True) + '\n')


def _resolve_subprocess_cwd(*, project_root: str | None, workspace_root: str | None) -> Path:
    candidates = [project_root, workspace_root]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            path = Path(candidate).resolve()
        except Exception:
            continue
        if path.exists() and path.is_dir():
            return path
    return Path.cwd()


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ChildExecution:
    """Tracks state for a spawned child process executing a workflow step."""
    run_id: str
    run_code: str
    step_run_id: str
    step_name: str
    run_payload: dict[str, Any]
    step_run_payload: dict[str, Any]
    request_payload: dict[str, Any]
    request_path: Path
    result_path: Path
    combined_log_path: Path
    child_event_log_path: Path
    process: subprocess.Popen[Any]
    started_at_monotonic: float
    started_at_iso: str
    state: str = 'spawned'
    watchdog_reason: str = ''
    exit_code: int | None = None
    term_sent_at: float | None = None
    last_heartbeat_at: float = 0.0
    submission_done: bool = False
    job_step_result_path: Path | None = None
    queue_dir: Path | None = None
    job_path: Path | None = None
    log_handle: Any | None = None  # File handle for child.log, must be closed


@dataclass
class SupervisorConfig:
    """Configuration for the daemon supervisor."""
    worker_id: str
    worker_label: str
    backend_url: str
    poll_seconds: int
    max_parallel: int
    stalled_seconds: int
    step_timeout_seconds: int
    kill_grace_seconds: int
    runtime_dir: Path
    log_file: Path
    cli_pythonpath: str | None
    step_spec_source: str
    cli_version: str = ""
    engine_version: str = ""
    once: bool = False


# ---------------------------------------------------------------------------
# JSONL logger
# ---------------------------------------------------------------------------

class DaemonLogger:
    """JSONL logger for daemon events using standard library rotation."""

    def __init__(self, path: Path, worker_id: str, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
        self.path = path
        self.worker_id = worker_id

        path.parent.mkdir(parents=True, exist_ok=True)
        self._handler = logging.handlers.RotatingFileHandler(
            str(path), maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8',
        )
        self._handler.setFormatter(logging.Formatter('%(message)s'))

        self._stdout_handler = logging.StreamHandler(sys.stdout)
        self._stdout_handler.setFormatter(logging.Formatter('%(message)s'))

        self._logger = logging.getLogger(f'daemon_v2.{worker_id}.{id(self)}')
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False
        self._logger.addHandler(self._handler)
        self._logger.addHandler(self._stdout_handler)

    def log(self, level: str, event: str, *, message: str = '', child: ChildExecution | None = None, details: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {
            'ts': _utcnow_iso(),
            'level': level,
            'event': event,
            'worker_id': self.worker_id,
            'message': message,
            'details': details or {},
        }
        if child is not None:
            payload.update({
                'workflow_run_id': child.run_id,
                'workflow_step_run_id': child.step_run_id,
                'run_code': child.run_code,
                'pid': child.process.pid,
                'state': child.state,
            })
        line = json.dumps(payload, ensure_ascii=True, sort_keys=True)
        self._logger.info(line)
        if child is not None:
            _append_jsonl(child.child_event_log_path, payload)


# ---------------------------------------------------------------------------
# Pre-execution sync: fetch backend state and write to file for CLI
# ---------------------------------------------------------------------------

def _fetch_and_write_backend_state(
    *,
    client: V2BackendClient,
    run_id: str,
    step_run_id: str,
    child_dir: Path,
    logger: DaemonLogger,
    timeout_seconds: float = 15.0,
) -> str | None:
    """Fetch full run state from backend and write to backend_state.json.

    Waits (bounded) until the claimed step run is visible in the backend
    state. The backend commits claim transactions AFTER its response is
    sent (FastAPI dependency teardown), so the claim acknowledgment can
    arrive before the step run INSERT is durable. Polling get_run until
    current_step_run_id matches the claim guarantees the child's outcome
    POST will find its step run, and that backend_state.json is fresh.

    Returns the path to the written file, or None if the step run never
    became visible within the timeout (the supervisor then reports the
    step as failed instead of silently stalling).
    """
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            full_run = client.get_run(run_id=run_id)
        except Exception as exc:
            logger.log("warning", "daemon_v2_backend_state_fetch_failed", message=str(exc), details={"run_id": run_id})
            full_run = None

        if full_run is not None:
            run = full_run.get("run") or full_run
            current_step_run_id = str(run.get("current_step_run_id") or "").strip()
            if current_step_run_id == step_run_id:
                state_path = child_dir / "backend_state.json"
                try:
                    state_path.write_text(json.dumps(full_run, indent=2, default=str), encoding="utf-8")
                except Exception as exc:
                    logger.log("warning", "daemon_v2_backend_state_write_failed", message=str(exc), details={"path": str(state_path)})
                    return None
                logger.log("info", "daemon_v2_backend_state_written", message="wrote backend state for CLI sync", details={
                    "run_id": run_id, "step_run_id": step_run_id, "path": str(state_path),
                })
                return str(state_path)

        if time.monotonic() >= deadline:
            logger.log("error", "daemon_v2_claim_not_durable", message=(
                f"claimed step run {step_run_id} for run {run_id} not visible within {timeout_seconds:g}s; "
                "aborting spawn so the step is reported failed"
            ), details={"run_id": run_id, "step_run_id": step_run_id})
            return None

        time.sleep(0.25)


# ---------------------------------------------------------------------------
# Child process spawning
# ---------------------------------------------------------------------------

def _build_cli_args(
    *,
    run_data: dict,
    step_data: dict,
    project_root: str,
    job_id_to_pass: str,
    python_executable: str = sys.executable,
) -> list[str]:
    """Construct CLI arguments from backend claim data.

    This function is extracted for unit testing to verify data flow.
    """
    run_code = str(run_data.get("run_code", ""))
    workflow_name = str(run_data.get("workflow_name", ""))
    step_name = str(step_data.get("step_name", ""))
    
    args = [
        python_executable, "-m", "agent_runner_v2.run_agent", "run",
        "--project-root", project_root,
        "--template-group", workflow_name,
        "--mode", "daemon",
        "--job-id", job_id_to_pass,
        "--job-no", run_code,
        "--job", step_name,
    ]

    # BCS Section 11.4: Extract implementation_name
    # The Golden Rule: NO aliases (impl_name/IMPL_NAME) allowed.
    impl_name = str(run_data.get("implementation_name") or "").strip()
    
    if impl_name:
        args.extend(["--impl-name", impl_name])
    
    if not job_id_to_pass:
        args.extend(["--start-step", step_name])

    return args


def _spawn_child(
    *,
    run_data: dict,
    step_data: dict,
    runtime_root: Path,
    cli_pythonpath: str | None,
    logger: DaemonLogger,
    v2_backend_url: str,
    client: V2BackendClient,
) -> ChildExecution:
    """Spawn a CLI child process with pre-execution backend state sync.

    Receives raw run/step data from the Backend claim response directly.
    """
    from .job_state import job_dir as compute_job_dir

    run = run_data
    step_run = step_data
    
    # Use native Backend keys (run_id / step_run_id)
    run_id = str(run.get("run_id") or run.get("id", ""))
    step_run_id = str(step_run.get("step_run_id") or step_run.get("id", ""))
    
    run_code = str(run.get("run_code", ""))
    workflow_name = str(run.get("workflow_name", ""))
    step_name = str(step_run.get("step_name", ""))
    project_root = str(run.get("project_root") or ".")

    # Date-based directory structure
    today = datetime.now().strftime("%Y%m%d")

    # Job directory: use backend-provided path if available, else construct
    job_dir_from_backend = run.get("job_dir")
    if job_dir_from_backend:
        job_path = Path(job_dir_from_backend)
    else:
        job_path = Path(str(JOBS_ROOT)) / today / workflow_name / run_code

    # Queue directory for CLI outcome files
    queue_path = Path(str(QUEUE_ROOT)) / today / workflow_name / run_code

    # Runtime directory for child logs and request files
    child_dir = runtime_root / today / workflow_name / run_code / step_run_id
    child_dir.mkdir(parents=True, exist_ok=True)

    # Pre-execution sync: fetch backend state and write to file.
    # Waits until the claimed step run is durable (see _fetch_and_write_backend_state).
    backend_state_path = _fetch_and_write_backend_state(
        client=client, run_id=run_id, step_run_id=step_run_id,
        child_dir=child_dir, logger=logger,
    )
    if backend_state_path is None:
        raise RuntimeError(
            f"Claim for step run {step_run_id} not durable within timeout; refusing to spawn child"
        )

    # Determine if this is a new job or existing job
    job_id_to_pass = ""
    if run_code and workflow_name:
        if job_path.exists():
            job_id_to_pass = run_code
        else:
            # Also check legacy path (pre-date-prefix)
            legacy_job_path = compute_job_dir.__wrapped__(workflow_name, run_code) if hasattr(compute_job_dir, '__wrapped__') else None
            # Fallback: check via the function with env var cleared
            old_env = os.environ.pop("AGENT_RUNNER_JOB_DIR", None)
            try:
                legacy_path = Path(str(JOBS_ROOT)) / workflow_name / run_code
                if legacy_path.exists():
                    job_id_to_pass = run_code
                    job_path = legacy_path
            finally:
                if old_env is not None:
                    os.environ["AGENT_RUNNER_JOB_DIR"] = old_env

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

    # --- BCS Section 11.6: Log received backend payload ---
    logger.log("info", "daemon_backend_payload_received", message="Run payload from backend API", details={
        "run_id": run_id,
        "workflow": workflow_name,
        "run_keys": list(run.keys()),
        # Canonical keys per BCS Section 11.7
        "implementation_name": run.get("implementation_name"),
        "prompt_selections": run.get("prompt_selections"),
    })

    # BCS Section 11.4: Extract implementation_name from flattened run object
    # The Golden Rule: NO aliases (impl_name/IMPL_NAME) allowed.
    impl_name = str(run.get("implementation_name") or "").strip()
    
    # --- BCS Section 11.6: Log CLI args before spawning ---
    if impl_name:
        cli_args.extend(["--impl-name", impl_name])
    
    logger.log("info", "daemon_cli_args", message="Spawning CLI child", details={
        "run_id": run_id,
        "cli_args": cli_args,
        "impl_name_resolved": impl_name,
    })

    if not job_id_to_pass:
        cli_args.extend(["--start-step", step_name])

    env = os.environ.copy()
    if cli_pythonpath:
        env["PYTHONPATH"] = cli_pythonpath + os.pathsep + env.get("PYTHONPATH", "")
    env["AGENT_RUNNER_WORKFLOW_RUN_ID"] = run_id
    env["AGENT_RUNNER_WORKFLOW_STEP_RUN_ID"] = step_run_id
    env["AGENT_RUNNER_JOB_DIR"] = str(job_path)
    env["AGENT_RUNNER_QUEUE_DIR"] = str(queue_path)

    # Pass backend state file path for CLI pre-execution sync
    if backend_state_path:
        env["AGENT_RUNNER_BACKEND_STATE_FILE"] = backend_state_path

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
        "job_dir": str(job_path), "queue_dir": str(queue_path),
        "backend_state_file": backend_state_path or "(none)",
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
        queue_dir=queue_path,
        job_path=job_path,
        log_handle=log_handle,
    )


# ---------------------------------------------------------------------------
# Queue processing
# ---------------------------------------------------------------------------

def _child_outcome_action(child: ChildExecution) -> str:
    """Determine what to do when a child process has exited.

    Returns:
        ``"queue"``    — queue file exists, poller will handle it.
        ``"skip"``     — outcome already processed (archived or failed); no action.
        ``"failure"``  — no outcome found, write a failure to the queue.
    """
    if child.queue_dir is None:
        return "failure"

    step_run_id = child.step_run_id
    queue_file = child.queue_dir / f"{step_run_id}.json"
    if queue_file.exists():
        return "queue"

    archived_file = child.queue_dir / "archive" / f"{step_run_id}.json"
    failed_file = child.queue_dir / "failed" / f"{step_run_id}.json"
    if archived_file.exists() or failed_file.exists():
        return "skip"

    return "failure"


def _write_failure_to_queue(
    child: ChildExecution,
    *,
    outcome: str,
    failure_class: str,
    error_message: str,
    logger: DaemonLogger,
) -> None:
    """Write a failure outcome to the queue on behalf of a crashed CLI child."""
    if child.queue_dir is None:
        logger.log("warning", "daemon_v2_no_queue_dir", message="cannot write failure: no queue_dir", details={
            "step_run_id": child.step_run_id,
        })
        return
    outcome_data = {
        "step_run_id": child.step_run_id,
        "run_id": child.run_id,
        "run_code": child.run_code,
        "workflow_name": child.run_payload.get("workflow_name", ""),
        "step_name": child.step_name,
        "job_dir": str(child.job_path) if child.job_path else None,
        "outcome": outcome,
        "failure_class": failure_class,
        "error_message": error_message,
        "exit_code": child.exit_code,
    }
    try:
        outcome_queue.write_outcome(child.queue_dir, child.step_run_id, outcome_data)
        logger.log("info", "daemon_v2_failure_queued", message="wrote failure to queue", details={
            "step_run_id": child.step_run_id, "outcome": outcome,
        })
    except Exception as exc:
        logger.log("error", "daemon_v2_queue_write_failed", message=str(exc), details={
            "step_run_id": child.step_run_id,
        })


def _process_queue(client: V2BackendClient, logger: DaemonLogger) -> None:
    """Scan the queue for pending outcome files and report them to the backend."""
    queue_root = Path(str(QUEUE_ROOT))
    pending = outcome_queue.list_pending_outcomes(queue_root)
    if not pending:
        return

    logger.log("info", "daemon_v2_queue_scan", message=f"found {len(pending)} pending outcome(s)")

    for file_path in pending:
        data = outcome_queue.read_outcome(file_path)
        if data is None:
            logger.log("warning", "daemon_v2_queue_invalid", message=f"invalid queue file: {file_path}")
            outcome_queue.fail_outcome(file_path)
            continue

        step_run_id = data.get("step_run_id", "")
        outcome = data.get("outcome", "failed")
        failure_class = data.get("failure_class")
        artifacts = data.get("artifacts")
        review = data.get("review")
        error_message = data.get("error_message")
        usage_summary = data.get("usage_summary")
        job_dir = data.get("job_dir")

        try:
            response = client.report_outcome(
                step_run_id=step_run_id,
                outcome=outcome,
                failure_class=failure_class,
                artifacts=artifacts,
                review=review,
                error_message=error_message,
                usage_summary=usage_summary,
                job_dir=job_dir,
            )
            new_status = response.get("run_status", "?")
            next_step = response.get("current_step", "?")
            outcome_queue.archive_outcome(file_path)
            logger.log("info", "daemon_v2_queue_reported", message=f"outcome reported: {outcome}", details={
                "step_run_id": step_run_id, "new_status": new_status,
                "next_step": next_step, "file": str(file_path),
            })
        except Exception as exc:
            error_str = str(exc)
            # Permanent failures: backend will never accept this outcome
            # (step run deleted, run cancelled, etc.)
            is_permanent = "status=404" in error_str or "status=409" in error_str
            if is_permanent:
                outcome_queue.fail_outcome(file_path)
                logger.log("warning", "daemon_v2_queue_permanent_failure", message=f"outcome moved to failed (permanent error)", details={
                    "step_run_id": step_run_id, "file": str(file_path),
                    "error": error_str[:200],
                })
            else:
                logger.log("warning", "daemon_v2_queue_report_failed", message=str(exc), details={
                    "step_run_id": step_run_id, "file": str(file_path),
                })
                # Leave file in queue for retry on next poll cycle (transient error)


# ---------------------------------------------------------------------------
# Supervisor loop
# ---------------------------------------------------------------------------

def run_supervisor(*, config: SupervisorConfig, v2_url: str) -> int:
    """V2 supervisor — claim → sync → spawn → report loop.

    The V2 backend handles all routing, action detection, and stop requests.
    The daemon fetches full backend state before spawning each child, ensuring
    the CLI starts with fresh backend-authoritative local state.

    Workers must be pre-registered in the backend (via operator console or admin API).
    The daemon validates the worker exists and is active on startup, then only
    sends heartbeats and claims work — no auto-registration.
    """
    from .v2.sync import resolve_v2_api_key

    logger = DaemonLogger(config.log_file, config.worker_id)
    api_key = resolve_v2_api_key()
    client = V2BackendClient(v2_url, api_key=api_key)

    # Startup validation: verify worker exists and is enabled in backend
    # Retry indefinitely on connection errors (backend may be temporarily down)
    # Only terminate if worker is explicitly disabled
    retry_delay = 5  # seconds between retries
    worker_validated = False
    
    while not worker_validated:
        try:
            worker_info = client.get_worker(worker_id=config.worker_id)
            is_enabled = worker_info.get("is_enabled", False)
            if not is_enabled:
                logger.log("error", "daemon_v2_worker_disabled", message=(
                    f"Worker '{config.worker_id}' is disabled (is_enabled=false). "
                    "Enable the worker via operator console or admin API before starting the daemon."
                ))
                print(f"ERROR: Worker '{config.worker_id}' is disabled (is_enabled=false).")
                print("Enable the worker via operator console or admin API before starting the daemon.")
                return 1
            # Worker is enabled — proceed
            logger.log("info", "daemon_v2_worker_validated", message=f"Worker '{config.worker_id}' is enabled", details={
                "is_enabled": is_enabled,
                "worker_label": worker_info.get("worker_label", ""),
            })
            worker_validated = True
        except RuntimeError as exc:
            error_msg = str(exc)
            # Connection error — retry indefinitely
            logger.log("warning", "daemon_v2_backend_unreachable", message=(
                f"Backend unreachable: {error_msg}. Retrying in {retry_delay}s..."
            ))
            print(f"WARNING: Backend unreachable. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)
            # Continue loop — retry forever until backend is available

    logger.log("info", "daemon_v2_started", message="V2 worker daemon started", details={
        "v2_backend_url": v2_url, "worker_id": config.worker_id,
    })

    children: dict[str, ChildExecution] = {}
    running = True

    def _handle_signal(_sig, _frame):
        nonlocal running
        running = False
        logger.log("info", "daemon_v2_shutdown_signal", message="received shutdown signal")
        for step_run_id, child in list(children.items()):
            if child.exit_code is None:
                logger.log("info", "daemon_v2_shutdown_terminate", message="terminating child on shutdown", details={
                    "step_run_id": step_run_id, "pid": child.process.pid,
                })
                try:
                    child.process.terminate()
                    child.process.wait(timeout=5)  # Brief wait for graceful termination
                except Exception:
                    pass

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    while running:
        try:
            # Heartbeat — check for shutdown commands and force-cancel signals
            try:
                hb_resp = client.heartbeat(
                    worker_id=config.worker_id,
                    status="idle" if not children else "busy",
                )
                commands = hb_resp.get("commands", [])
                if "shutdown" in commands:
                    logger.log("info", "daemon_v2_shutdown_command", message="backend requested shutdown")
                    running = False

                if "terminate_children" in commands:
                    detail = hb_resp.get("detail") or {}
                    force_run_ids = set(detail.get("force_cancel_run_ids", []))
                    for step_run_id, child in list(children.items()):
                        if child.run_id in force_run_ids and child.exit_code is None:
                            logger.log("info", "daemon_v2_force_cancel", message="force-cancelling child", details={
                                "step_run_id": step_run_id, "run_id": child.run_id, "pid": child.process.pid,
                            })
                            try:
                                child.process.terminate()
                                child.process.wait(timeout=3)  # Brief wait for termination
                            except Exception:
                                pass
            except RuntimeError as hb_err:
                logger.log("warning", "daemon_v2_heartbeat_failed", message=str(hb_err))

            # Claim work
            if running and len(children) < config.max_parallel:
                try:
                    work = client.claim_work(worker_id=config.worker_id)
                except RuntimeError as claim_err:
                    logger.log("warning", "daemon_v2_claim_failed", message=str(claim_err))
                    work = {"work_type": "IDLE"}

                work_type = work.get("work_type", "IDLE")

                if work_type == "IDLE":
                    logger.log("info", "daemon_v2_no_work", message="no work available")

                elif work_type == "PROCESS_ACTION":
                    run_data = work.get("run", {})
                    step_data = work.get("step_run", {})
                    run_code = str(run_data.get("run_code", ""))
                    step_run_id = str(step_data.get("step_run_id", ""))
                    step_name = str(step_data.get("step_name", ""))
                    action = work.get("action", "")

                    logger.log("info", "daemon_v2_action_claimed", message=f"processing {action} directly", details={
                        "run_code": run_code, "step": step_name, "action": action,
                    })

                    _ACTION_OUTCOME = {
                        "APPROVE": ("approved", None),
                        "RESUME":  ("approved", None),
                        "REJECT":  ("rejected", "HUMAN_RETRY_REQUIRED"),
                        "RETRY":   ("failed",   "HUMAN_RETRY_REQUIRED"),
                    }
                    outcome, failure_class = _ACTION_OUTCOME.get(action, ("failed", "FATAL"))

                    try:
                        client.report_outcome(
                            step_run_id=step_run_id,
                            outcome=outcome,
                            failure_class=failure_class,
                        )
                        logger.log("info", "daemon_v2_action_reported", message=f"{action} reported as {outcome}", details={
                            "run_code": run_code, "step": step_name,
                        })
                    except Exception as exc:
                        logger.log("error", "daemon_v2_action_report_failed", message=str(exc), details={
                            "run_code": run_code, "step": step_name, "action": action,
                        })

                elif work_type == "EXECUTE_STEP":
                    run_data = work.get("run", {})
                    step_data = work.get("step_run", {})
                    run_code = str(run_data.get("run_code", ""))
                    step_run_id = str(step_data.get("step_run_id", ""))
                    step_name = str(step_data.get("step_name", ""))
                    workflow_name = str(run_data.get("workflow_name", ""))

                    logger.log("info", "daemon_v2_claimed", message=f"claimed {work_type}", details={
                        "run_code": run_code, "step": step_name, "work_type": work_type,
                    })

                    try:
                        child = _spawn_child(
                            run_data=run_data,
                            step_data=step_data,
                            runtime_root=config.runtime_dir,
                            cli_pythonpath=config.cli_pythonpath,
                            logger=logger,
                            v2_backend_url=v2_url,
                            client=client,
                        )
                        children[child.step_run_id] = child
                    except Exception as exc:
                        logger.log("error", "daemon_v2_spawn_failed", message=str(exc), details={
                            "run_code": run_code, "step": step_name,
                        })
                        # Write failure to queue (no child object available)
                        try:
                            today = datetime.now().strftime("%Y%m%d")
                            spawn_queue_dir = Path(str(QUEUE_ROOT)) / today / workflow_name / run_code
                            outcome_queue.write_outcome(spawn_queue_dir, step_run_id, {
                                "step_run_id": step_run_id,
                                "run_id": run_id,
                                "run_code": run_code,
                                "workflow_name": workflow_name,
                                "step_name": step_name,
                                "outcome": "failed",
                                "failure_class": "FATAL",
                                "error_message": f"Daemon failed to spawn child: {exc}",
                            })
                        except Exception:
                            pass

                if config.once:
                    running = False

            # Check completed children
            for step_run_id in list(children.keys()):
                child = children[step_run_id]

                if child.exit_code is None:
                    proc_rc = child.process.poll()
                    if proc_rc is not None:
                        child.exit_code = proc_rc
                        child.state = "completed"

                if child.exit_code is None and config.step_timeout_seconds > 0:
                    elapsed = time.monotonic() - child.started_at_monotonic
                    if child.term_sent_at is None and elapsed >= config.step_timeout_seconds:
                        child.state = "timed_out"
                        child.term_sent_at = time.monotonic()
                        logger.log("error", "daemon_v2_child_timeout", message="child exceeded timeout", details={
                            "step_run_id": step_run_id, "timeout_seconds": config.step_timeout_seconds,
                        })
                        try:
                            child.process.terminate()
                        except OSError:
                            pass

                if child.exit_code is None and child.term_sent_at is not None:
                    if time.monotonic() - child.term_sent_at >= 30:
                        child.state = "killed"
                        child.exit_code = -1
                        logger.log("warning", "daemon_v2_child_killed", message="force-killed child after grace period", details={
                            "step_run_id": step_run_id,
                        })
                        try:
                            child.process.kill()
                            child.process.wait(timeout=5)  # Reap zombie process
                        except Exception:
                            pass

                if child.state in ("completed", "failed", "killed", "timed_out"):
                    logger.log("info", "daemon_v2_child_done", message=f"child done: {child.state}", details={
                        "step_run_id": step_run_id, "exit_code": child.exit_code,
                    })
                    # Determine what to do with the completed child's outcome
                    action = _child_outcome_action(child)
                    if action == "queue":
                        queue_file = child.queue_dir / f"{step_run_id}.json"
                        logger.log("info", "daemon_v2_result_in_queue", message="result file found in queue", details={
                            "step_run_id": step_run_id, "queue_file": str(queue_file),
                        })
                    elif action == "skip":
                        logger.log("info", "daemon_v2_outcome_already_handled", message="outcome already processed, skipping false failure", details={
                            "step_run_id": step_run_id,
                        })
                    else:
                        # CLI didn't write to queue — write failure on its behalf
                        exit_code = child.exit_code or -1
                        _write_failure_to_queue(
                            child,
                            outcome="failed",
                            failure_class="HUMAN_RETRY_REQUIRED",
                            error_message=f"Child exited with code {exit_code}, no result in queue",
                            logger=logger,
                        )
                    # Close log file handle to prevent file descriptor leak
                    if child.log_handle is not None:
                        try:
                            child.log_handle.close()
                        except Exception:
                            pass
                    del children[step_run_id]

            # Process pending outcome queue files
            _process_queue(client, logger)

        except Exception as exc:
            # Top-level exception handler — daemon keeps running through any error
            logger.log("error", "daemon_v2_loop_error", message=f"Unexpected error in main loop: {exc}")

        time.sleep(config.poll_seconds)

    # Final cleanup: close any remaining log handles
    for step_run_id, child in list(children.items()):
        if child.log_handle is not None:
            try:
                child.log_handle.close()
            except Exception:
                pass
    logger.log("info", "daemon_v2_stopped", message="V2 daemon stopped")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """V2 daemon CLI entry point.

    Parses arguments, resolves configuration, and starts the V2 supervisor.
    """
    import argparse

    from .run_agent import __version__ as cli_version

    cfg = load_runner_config()
    engine_version = (cfg.get('engine_version') or '').strip() or '(not set)'

    p = argparse.ArgumentParser(prog='ukbe-run-agent daemon', description='V2 worker daemon supervisor.')
    p.add_argument('-v', '--version', action='version', version=f'%(prog)s {cli_version} (engine: {engine_version})')
    p.add_argument('worker_id', nargs='?', default='', help='Worker ID (overrides config and WORKER_ID env var).')
    p.add_argument('--worker-label', default='', help='Queue label override.')
    p.add_argument('--backend-url', default='', help='V2 Backend URL override.')
    p.add_argument('--poll-seconds', type=int, default=0, help='Poll interval override.')
    p.add_argument('--log-file', default='', help='Daemon log file path override.')
    p.add_argument('--max-parallel', type=int, default=0, help='Maximum concurrent child executions.')
    p.add_argument('--runtime-dir', default='', help='Runtime directory for child request/result files.')
    p.add_argument('--stalled-seconds', type=int, default=0, help='Seconds without activity before marking stalled.')
    p.add_argument('--step-timeout-seconds', type=int, default=0, help='Hard timeout for child execution.')
    p.add_argument('--kill-grace-seconds', type=int, default=0, help='Grace period between SIGTERM and SIGKILL.')
    p.add_argument('--step-spec-source', default='', help='Workflow step spec source: global, backend, or hybrid.')
    p.add_argument('--engine-root', default='', help='Explicit engine root for PYTHONPATH.')
    p.add_argument('--once', action='store_true', help='Claim and process at most one step, then exit.')
    args = p.parse_args(argv)

    from .single_instance import check_single_instance
    check_single_instance(
        "ukbe-runner-daemon",
        "Daemon is already running. Use 'taskkill /F /IM python.exe' to stop it."
    )

    worker_id = args.worker_id or _setting(cfg, 'WORKER_ID', 'worker_id', 'kode-worker-01')
    worker_label = args.worker_label or _setting(cfg, 'WORKER_LABEL', 'worker_label', 'live')
    backend_url = args.backend_url or _setting(cfg, 'AGENT_RUNNER_BACKEND_URL', 'backend_url', 'http://127.0.0.1:8100')
    poll_seconds = args.poll_seconds or _setting_int(cfg, 'WORKER_POLL_SEC', 'poll_seconds', 5)
    max_parallel = args.max_parallel or _setting_int(cfg, 'WORKER_MAX_PARALLEL', 'max_parallel', 1)
    stalled_seconds = args.stalled_seconds or _setting_int(cfg, 'WORKER_STALLED_SEC', 'stalled_seconds', 300)
    step_timeout_seconds = (
        args.step_timeout_seconds
        if args.step_timeout_seconds is not None and args.step_timeout_seconds > 0
        else int(os.environ['WORKER_STEP_TIMEOUT_SEC']) if os.environ.get('WORKER_STEP_TIMEOUT_SEC') is not None
        else int(cfg['step_timeout_seconds']) if 'step_timeout_seconds' in cfg and cfg['step_timeout_seconds'] is not None
        else 3600
    )
    kill_grace_seconds = args.kill_grace_seconds or _setting_int(cfg, 'WORKER_KILL_GRACE_SEC', 'kill_grace_seconds', 30)
    step_spec_source = _step_spec_source(cfg, args.step_spec_source)
    default_log_file = str(GLOBAL_RUNNER_HOME / 'logs' / 'worker-daemon.jsonl')
    default_runtime_dir = str(GLOBAL_RUNNER_HOME / 'runtime' / 'worker')
    _raw_log = args.log_file or _setting(cfg, 'WORKER_LOG_FILE', 'log_file', default_log_file)
    _log_path = Path(_raw_log)
    log_file = (_log_path if _log_path.is_absolute() else GLOBAL_RUNNER_HOME / _log_path).resolve()
    _raw_runtime = args.runtime_dir or _setting(cfg, 'WORKER_RUNTIME_DIR', 'runtime_dir', default_runtime_dir)
    _runtime_path = Path(_raw_runtime)
    runtime_dir = (_runtime_path if _runtime_path.is_absolute() else GLOBAL_RUNNER_HOME / _runtime_path).resolve()

    bootstrap_logger = DaemonLogger(log_file, worker_id)
    cli_pythonpath = args.engine_root or _resolve_engine_pythonpath(cfg, bootstrap_logger.log)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    # Resolve V2 backend URL
    from .v2.sync import resolve_v2_backend_url
    v2_url = args.backend_url or resolve_v2_backend_url() or backend_url

    config = SupervisorConfig(
        worker_id=worker_id,
        worker_label=worker_label,
        backend_url=backend_url,
        poll_seconds=poll_seconds,
        max_parallel=max_parallel,
        stalled_seconds=stalled_seconds,
        step_timeout_seconds=step_timeout_seconds,
        kill_grace_seconds=kill_grace_seconds,
        runtime_dir=runtime_dir,
        log_file=log_file,
        cli_pythonpath=cli_pythonpath,
        step_spec_source=step_spec_source,
        cli_version=cli_version,
        engine_version=engine_version,
        once=args.once,
    )

    return run_supervisor(config=config, v2_url=v2_url)
