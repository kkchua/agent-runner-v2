"""[V1 LEGACY] Worker daemon supervisor.

This module contains V1 (legacy) daemon logic for the old backend protocol.
It is kept for backward compatibility during the V1→V2 migration.

For the current V2 architecture (backend-authoritative state machine):
    - V2 daemon code: agent_runner_v2/v2/daemon.py
    - Architecture spec: docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260801-002_platform-v2-architecture-redesign.md

The entry point (main, _run_supervisor) dispatches to V2 when v2_backend_url
is configured. Shared infrastructure (ChildExecution, _DaemonLogger,
SupervisorConfig) is used by both V1 and V2 code paths.

Invoked via: ukbe-run-agent daemon [worker-id]
"""
from __future__ import annotations

import json
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
from .runtime_context import GLOBAL_RUNNER_HOME


def _utcnow_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _load_config() -> dict:
    """Load runner configuration from config.json."""
    return load_runner_config()


def _setting(cfg: dict, env_key: str, config_key: str, default: str) -> str:
    """Resolve a setting from env var, config, or default.

    Priority: env var > config key > default.

    Args:
        cfg: Configuration dict from config.json.
        env_key: Environment variable name to check first.
        config_key: Key in configuration dict.
        default: Fallback value if not found elsewhere.

    Returns:
        Resolved setting value as string.
    """
    return os.environ.get(env_key) or str(cfg.get(config_key) or default)


def _setting_int(cfg: dict, env_key: str, config_key: str, default: int) -> int:
    """Resolve an integer setting from env var, config, or default.

    Args:
        cfg: Configuration dict from config.json.
        env_key: Environment variable name to check first.
        config_key: Key in configuration dict.
        default: Fallback value if not found elsewhere.

    Returns:
        Resolved setting value as integer.
    """
    return int(_setting(cfg, env_key, config_key, str(default)))


def _step_spec_source(cfg: dict, cli_value: str) -> str:
    """Resolve step spec source from CLI, env, or config.

    Args:
        cfg: Configuration dict from config.json.
        cli_value: CLI argument value (highest priority).

    Returns:
        One of 'global', 'backend', or 'hybrid'. Defaults to 'backend'.
    """
    value = (cli_value or os.environ.get('STEP_SPEC_SOURCE') or str(cfg.get('step_spec_source') or 'backend')).strip().lower()
    if value not in {'global', 'backend', 'hybrid'}:
        return 'backend'
    return value


def _resolve_engine_pythonpath(cfg: dict, log) -> str | None:
    """Resolve the PYTHONPATH for child process execution.

    Priority:
    1. AGENT_RUNNER_V2_SRC env var (live source override)
    2. engine_version from config (versioned engine path)
    3. repo_root from config (for SNAPSHOT mode)
    4. Ambient PYTHONPATH (no override)

    Args:
        cfg: Configuration dict from config.json.
        log: Logger function for diagnostics.

    Returns:
        PYTHONPATH value or None for ambient mode.
    """
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
    """Append a JSON line to a JSONL log file.

    Creates parent directories if needed.

    Args:
        path: Path to the JSONL file.
        payload: Dict to serialize as JSON line.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(payload, ensure_ascii=True, sort_keys=True) + '\n')


def _latest_mtime(paths: list[Path], fallback: float) -> float:
    """Return the latest modification time among paths.

    Args:
        paths: List of paths to check.
        fallback: Fallback timestamp if no paths exist.

    Returns:
        Latest mtime or fallback if no paths exist.
    """
    latest = fallback
    for path in paths:
        if path.exists():
            latest = max(latest, path.stat().st_mtime)
    return latest


def _failure_result(*, step_name: str, code: str, reason: str, diagnostics: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a failure result dict for daemon error cases.

    Args:
        step_name: Name of the failed step.
        code: Failure code for diagnostics.
        reason: Human-readable failure reason.
        diagnostics: Optional additional diagnostic info.

    Returns:
        Dict with failure status and details.
    """
    return {
        'status': 'failed',
        'outcome': 'failed',
        'step_name': step_name,
        'coder_used': None,
        'remark': reason,
        'artifacts': {},
        'meta_json_path': None,
        'review': None,
        'usage': {},
        'failure': {
            'failure_class': 'FATAL',
            'failure_code': code,
            'failure_reason': reason,
            'failure_source': 'daemon',
        },
        'diagnostics': diagnostics or {},
    }


@dataclass
class ChildExecution:
    """Tracks state for a spawned child process executing a workflow step.

    Attributes:
        run_id: Backend workflow run ID.
        run_code: Human-readable run code (e.g., 'SDLC00CB-001').
        step_run_id: Backend step run ID.
        step_name: Step name being executed.
        run_payload: Full run dict from backend claim.
        step_run_payload: Full step_run dict from backend claim.
        request_payload: Request dict passed to child CLI.
        request_path: Path to request.json for child.
        result_path: Path to result.json from child.
        combined_log_path: Path to child.log output.
        child_event_log_path: Path to child-events.jsonl.
        process: The subprocess.Popen instance.
        started_at_monotonic: Monotonic start time for timeout tracking.
        started_at_iso: ISO timestamp of spawn time.
        state: Current state (spawned, running, stalled, timed_out, killed).
        watchdog_reason: Reason for watchdog intervention if any.
        exit_code: Process exit code when available.
        term_sent_at: Monotonic time when SIGTERM was sent.
        last_heartbeat_at: Monotonic time of last heartbeat.
        submission_done: Whether submission result was processed.
        job_step_result_path: Path to job step result.json if available.
    """
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


class _DaemonLogger:
    """JSONL logger for daemon events.

    Writes to both a file and stdout for daemon monitoring.
    Supports log rotation: when file exceeds max_size, rotates to .1, .2, etc.

    Args:
        path: Path to the JSONL log file.
        worker_id: Worker identifier for log correlation.
        max_bytes: Maximum file size before rotation (default 10MB).
        backup_count: Number of backup files to keep (default 5).
    """

    def __init__(self, path: Path, worker_id: str, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
        self.path = path
        self.worker_id = worker_id
        self.max_bytes = max_bytes
        self.backup_count = backup_count

    def _rotate_if_needed(self) -> None:
        """Rotate log file if it exceeds max_bytes."""
        if not self.path.exists():
            return
        try:
            if self.path.stat().st_size < self.max_bytes:
                return
        except OSError:
            return

        # Rotate: delete oldest, shift others up
        for i in range(self.backup_count - 1, 0, -1):
            src = self.path.with_suffix(f".log.{i}" if i > 0 else ".log")
            dst = self.path.with_suffix(f".log.{i + 1}")
            if src.exists():
                try:
                    src.rename(dst)
                except OSError:
                    pass

        # Current log becomes .1
        try:
            self.path.rename(self.path.with_suffix(".log.1"))
        except OSError:
            pass

    def log(self, level: str, event: str, *, message: str = '', child: ChildExecution | None = None, details: dict[str, Any] | None = None) -> None:
        """Log an event to JSONL file and stdout.

        Args:
            level: Log level (info, warning, error).
            event: Event type identifier.
            message: Human-readable message.
            child: Optional child execution context to include.
            details: Optional additional details dict.
        """
        self._rotate_if_needed()
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
        _append_jsonl(self.path, payload)
        sys.stdout.write(json.dumps(payload, ensure_ascii=True) + '\n')
        sys.stdout.flush()
        if child is not None:
            _append_jsonl(child.child_event_log_path, payload)


def _persist_backend_linkage_to_job_state(
    *,
    job_state: dict[str, Any],
    job_json_path: Path,
    child: ChildExecution,
    backend_url: str,
) -> dict[str, Any]:
    """Persist backend IDs to job.json for traceability.

    Updates workflow_run_id, workflow_step_run_id, and backend_url
    in job.json if changed.

    Args:
        job_state: Current job state dict.
        job_json_path: Path to job.json file.
        child: Child execution with backend IDs.
        backend_url: Backend URL for persistence.

    Returns:
        Updated job state dict.
    """
    changed = False
    if str(job_state.get("workflow_run_id") or "").strip() != str(child.run_id or "").strip():
        job_state["workflow_run_id"] = child.run_id
        changed = True
    if str(job_state.get("workflow_step_run_id") or "").strip() != str(child.step_run_id or "").strip():
        job_state["workflow_step_run_id"] = child.step_run_id
        changed = True
    if backend_url and str(job_state.get("backend_url") or "").strip() != str(backend_url).strip():
        job_state["backend_url"] = backend_url
        changed = True
    if changed:
        job_json_path.write_text(json.dumps(job_state, indent=2), encoding="utf-8")
    return job_state


def _send_child_heartbeat(client, worker_id: str, child: ChildExecution, *, status: str) -> None:
    """Send a heartbeat for an active child execution.

    Args:
        client: BackendClient instance.
        worker_id: Worker identifier.
        child: Child execution to report on.
        status: Heartbeat status ('busy' for active children).
    """
    client.heartbeat(
        worker_id=worker_id,
        status=status,
        current_step_run_id=None,
        workflow_run_id=child.run_id,
        workflow_step_run_id=child.step_run_id,
        run_code=child.run_code,
        pid=child.process.pid,
        state=child.state,
        log_file=str(child.combined_log_path),
        watchdog_reason=child.watchdog_reason or None,
        exit_code=child.exit_code,
    )


def _is_stop_requested(run: dict[str, Any]) -> bool:
    """Check if a stop was requested via context_payload flag or run_status."""
    context = run.get("context_payload") or {}
    if isinstance(context, dict):
        control = context.get("__run_control") or {}
        if isinstance(control, dict) and control.get("stop_requested"):
            return True
    return str(run.get("run_status") or "").lower() == "stopped"


def _handle_stop_on_claim(client, claim: dict, logger) -> None:
    """Log and skip when stop_requested is detected on claim.

    The backend should have filtered this run already. If it didn't,
    we just skip spawning — no sync needed since the run is already stopped.
    """
    run = claim["run"]
    run_code = run.get("run_code", "")
    logger.log(
        "info", "stop_requested_on_claim",
        message=f"Stop requested for run {run_code}, skipping (backend should have filtered this)",
        details={"run_id": run.get("id"), "run_code": run_code},
    )


def _is_quit_daemon_requested(run: dict[str, Any]) -> bool:
    """Check if quit_daemon was requested via context_payload flag.

    This is signaled via context_payload.__run_control.quit_daemon = True
    """
    context = run.get("context_payload") or {}
    if isinstance(context, dict):
        control = context.get("__run_control") or {}
        if isinstance(control, dict) and control.get("quit_daemon"):
            return True
    return False


def _get_approval_request(run: dict[str, Any]) -> dict[str, Any] | None:
    """Check if an approval/reject/resume/retry was requested via context_payload flag.

    Only checks context_payload.__run_control flags (approve_requested, etc.).
    Does NOT auto-detect awaiting_human status - that would auto-approve without human action.

    Returns the approval request details if found, None otherwise.
    """
    context = run.get("context_payload") or {}
    if isinstance(context, dict):
        control = context.get("__run_control") or {}
        if isinstance(control, dict):
            for action_type in ("approve_requested", "reject_requested", "resume_requested", "retry_requested"):
                if control.get(action_type):
                    return {
                        "action_type": action_type,
                        "action_step": control.get("action_step", ""),
                        "feedback": control.get("feedback", ""),
                    }
    return None


def _spawn_approval_child(
    *,
    run: dict[str, Any],
    approval_request: dict[str, Any],
    runtime_root: Path,
    cli_pythonpath: str,
    logger: _DaemonLogger,
    backend_url: str,
) -> ChildExecution | None:
    """Spawn CLI with --approve-step to handle the approval request.

    The CLI will load local job.json, record the approval, advance to next step, and sync.
    """
    import subprocess
    import sys

    run_id = str(run.get("id") or "")
    run_code = str(run.get("run_code") or "")
    workflow_name = str(run.get("workflow_name") or "")
    job_id = str(run.get("run_code") or "")  # Local job ID is the run_code
    action_step = approval_request.get("action_step", "")
    action_type = approval_request.get("action_type", "")

    # Map action_type to CLI flag
    flag_map = {
        "approve_requested": "--approve-step",
        "reject_requested": "--reject-step",
        "resume_requested": "--resume-step",
        "retry_requested": "--retry-step",
    }
    cli_flag = flag_map.get(action_type, "--approve-step")

    logger.log(
        "info", "spawning_approval_child",
        message=f"Spawning CLI to handle {action_type} for step {action_step}",
        details={"run_id": run_id, "run_code": run_code, "action_step": action_step, "cli_flag": cli_flag},
    )

    # Create child directory
    child_dir = runtime_root / f"approval-{run_id}"
    child_dir.mkdir(parents=True, exist_ok=True)

    # Build request payload for the CLI
    request_payload = {
        "workflow_run_id": run_id,
        "workflow_name": workflow_name,
        "job_id": job_id,
        "step_name": action_step,
        "cli_flag": cli_flag,
        "backend_url": backend_url,
    }
    request_path = child_dir / "request.json"
    request_path.write_text(json.dumps(request_payload, indent=2), encoding="utf-8")

    result_path = child_dir / "result.json"
    combined_log_path = child_dir / "child.log"
    child_event_log_path = child_dir / "child-events.jsonl"

    # Build CLI command
    python_exe = sys.executable
    cli_args = [
        python_exe, "-m", "agent_runner_v2.run_agent", "run",
        "--template-group", workflow_name,
        "--job-id", job_id,
        cli_flag, action_step,
    ]

    env = os.environ.copy()
    if cli_pythonpath:
        env["PYTHONPATH"] = cli_pythonpath
    env["BACKEND_URL"] = backend_url

    # Set working directory to project_root so subprocess can find .env file
    project_root = str(run.get("project_root") or "")
    subprocess_cwd = _resolve_subprocess_cwd(project_root=project_root, workspace_root=None)

    try:
        with open(combined_log_path, "ab") as log_fh:
            proc = subprocess.Popen(
                cli_args,
                stdout=log_fh,
                stderr=subprocess.STDOUT,
                cwd=str(subprocess_cwd),
                env=env,
            )

        child = ChildExecution(
            run_id=run_id,
            step_run_id=f"approval-{run_id}",
            step_name=action_step,
            run_code=run_code,
            request_payload=request_payload,
            request_path=request_path,
            result_path=result_path,
            combined_log_path=combined_log_path,
            child_event_log_path=child_event_log_path,
            process=proc,
            started_at_iso=_now_iso(),
            started_at_monotonic=time.monotonic(),
        )

        logger.log(
            "info", "approval_child_spawned",
            message=f"Spawned CLI for {action_type}",
            child=child,
            details={"pid": proc.pid, "cli_flag": cli_flag, "action_step": action_step},
        )
        return child

    except Exception as exc:
        logger.log(
            "error", "approval_spawn_failed",
            message=f"Failed to spawn CLI for {action_type}: {exc}",
            details={"run_id": run_id, "run_code": run_code, "error": str(exc)},
        )
        return None


def _handle_quit_daemon(client, claim: dict, logger) -> bool:
    """Handle quit daemon command.

    Acknowledges the quit, stops the run, and signals shutdown.

    Args:
        client: BackendClient instance
        claim: The claimed run/step
        logger: Daemon logger

    Returns:
        True if daemon should shut down, False otherwise
    """
    run = claim["run"]
    step_run = claim["step_run"]
    step_run_id = str(step_run.get("id") or "")
    run_id = str(run.get("id") or "")

    logger.log(
        "info", "daemon_quit_requested",
        message="Received quit command from console, shutting down",
        details={"run_id": run_id, "run_code": run.get("run_code")},
    )

    # Sync the step as completed
    try:
        client.sync_job_state(
            step_run_id=step_run_id,
            payload={
                "run_status": "completed",
                "step_status": "completed",
                "step_outcome": "completed",
                "step_coder": "system",
                "step_duration_seconds": 0,
                "next_step_name": None,
                "output_payload": {},
                "error_message": None,
                "review": None,
                "artifacts": [],
                "events": [{"event_type": "DAEMON_QUIT_ACK", "message": "Daemon acknowledged quit command"}],
            },
        )
    except Exception as exc:
        logger.log("warning", "daemon_quit_sync_failed", message=f"Failed to sync quit acknowledgment: {exc}")

    # Also stop the run to prevent re-claiming on daemon restart
    try:
        client.stop_run(run_id=run_id, reason="Daemon quit acknowledged")
    except Exception as exc:
        logger.log("warning", "daemon_quit_stop_failed", message=f"Failed to stop quit run: {exc}")

    return True


def _spawn_child(*, claim: dict[str, Any], runtime_root: Path, cli_pythonpath: str | None, logger: _DaemonLogger, backend_url: str, step_spec_source: str) -> ChildExecution:
    """Spawn a child process to execute a claimed workflow step.

    Creates a child directory with request.json, sets up environment,
    and launches the CLI subprocess with proper PYTHONPATH and CWD.

    Args:
        claim: Backend claim response with run and step_run dicts.
        runtime_root: Directory for child execution files.
        cli_pythonpath: Optional PYTHONPATH override for engine version.
        logger: Daemon logger instance.
        backend_url: Backend URL for child communication.
        step_spec_source: Step spec source mode.

    Returns:
        ChildExecution dataclass tracking the spawned process.
    """
    from .run_agent import _build_worker_request_payload
    from .job_state import job_dir
    from .backend_client import BackendClient

    run = dict(claim['run'])
    step_run = dict(claim['step_run'])
    step_run_id = str(step_run['id'])
    run_id = str(run['id'])
    child_dir = runtime_root / step_run_id
    child_dir.mkdir(parents=True, exist_ok=True)
    
    # Fetch full backend state before spawning CLI (pre-execution sync)
    backend_state = None
    try:
        client = BackendClient(backend_url)
        run_detail = client.get_run(run_id=run_id)
        backend_state = run_detail
        logger.log('info', 'backend_state_fetched', message=f'Fetched full backend state for run {run_id}', details={'run_id': run_id})
    except Exception as exc:
        logger.log('warning', 'backend_state_fetch_failed', message=f'Failed to fetch backend state: {exc}, proceeding with claim data only', details={'run_id': run_id, 'error': str(exc)})
    
    request_payload = _build_worker_request_payload(
        run=run,
        step_run=step_run,
        step_execution_spec=claim.get('step_execution_spec'),
        backend_url=backend_url,
        step_spec_source=step_spec_source,
    )

    # Include full backend state in request_payload for CLI initialization
    if backend_state:
        request_payload['backend_state'] = backend_state

    request_path = child_dir / 'request.json'
    result_path = child_dir / 'result.json'
    combined_log_path = child_dir / 'child.log'
    child_event_log_path = child_dir / 'child-events.jsonl'
    request_path.write_text(json.dumps(request_payload, indent=2), encoding='utf-8')

    env = os.environ.copy()
    if cli_pythonpath:
        env['PYTHONPATH'] = cli_pythonpath + os.pathsep + env.get('PYTHONPATH', '')
    env['AGENT_RUNNER_WORKFLOW_RUN_ID'] = str(run.get('id') or '')
    env['AGENT_RUNNER_WORKFLOW_STEP_RUN_ID'] = str(step_run.get('id') or '')
    env['AGENT_RUNNER_BACKEND_URL'] = str(backend_url or '')
    
    # Write backend state to a separate file for CLI to read
    if backend_state:
        backend_state_path = child_dir / 'backend_state.json'
        backend_state_path.write_text(json.dumps(backend_state, indent=2), encoding='utf-8')
        env['AGENT_RUNNER_BACKEND_STATE_FILE'] = str(backend_state_path)

    log_handle = combined_log_path.open('ab')
    
    # Set working directory to project_root so subprocess can find .env file
    project_root = request_payload.get("project_root")
    workspace_root = request_payload.get("workspace_root")
    subprocess_cwd = _resolve_subprocess_cwd(project_root=project_root, workspace_root=workspace_root)
    
    logger.log('info', 'subprocess_cwd', message=f'Setting subprocess cwd to {subprocess_cwd}', details={'project_root': project_root, 'subprocess_cwd': str(subprocess_cwd)})

    # Check if job folder already exists (for multi-step workflows)
    backend_run_code = request_payload.get("job_id", "")
    template_group = request_payload.get("template_group", "")
    
    # Validate template_group is present (required for job folder creation)
    if not template_group:
        error_msg = (
            f"template_group is missing from request payload. "
            f"Backend run.workflow_name={run.get('workflow_name')!r}, "
            f"step_execution_spec.template_group={claim.get('step_execution_spec', {}).get('template_group')!r}. "
            f"Cannot create job folder without workflow name."
        )
        logger.log('error', 'missing_template_group', message=error_msg, details={
            'run_id': run_id,
            'workflow_name': run.get('workflow_name'),
            'step_execution_spec': claim.get('step_execution_spec'),
        })
        raise ValueError(error_msg)
    
    # Compute job step directory path (where manual mode writes result.json)
    step_sequence_no = int(claim.get('step_execution_spec', {}).get("step_sequence_no") or 
                          claim.get('step_execution_spec', {}).get("step_order") or 1)
    step_name = str(step_run.get('step_name') or '')
    job_id_to_pass = ""  # Default: empty, will create new job

    if backend_run_code and template_group:
        potential_job_dir = job_dir(template_group, backend_run_code)
        if potential_job_dir.exists():
            job_id_to_pass = backend_run_code
        elif step_sequence_no > 1:
            raise FileNotFoundError(
                f"Local job state missing for backend run {backend_run_code!r} "
                f"before claimed step {step_name!r} (sequence {step_sequence_no})."
            )

    job_step_dir = job_dir(template_group, backend_run_code) / f"{step_sequence_no:02d}_{step_name}"
    job_step_result_path = job_step_dir / "result.json"

    # Build CLI args same as manual mode (like run-*.bat files)
    cli_args = [
        sys.executable, '-m', 'agent_runner_v2.run_agent', 'run',
        '--project-root', request_payload.get("project_root", "."),
        '--template-group', template_group,
        '--mode', 'daemon',
        '--job-id', job_id_to_pass,  # Empty for new job, or run_code to load existing
        '--job-no', backend_run_code,  # Backend's run_code for folder name
        '--job', step_name,
    ]

    if request_payload.get("target_project_root"):
        cli_args.extend(['--target-project-root', request_payload["target_project_root"]])

    # Pass input artifacts as --set flags so they seed into job state
    input_artifacts = request_payload.get("input_artifacts") or {}
    for key, value in input_artifacts.items():
        if value:
            cli_args.extend(['--set', f'{key}={value}'])

    # Pass start_step from context_payload if provided
    context_payload = request_payload.get("context_payload") or {}
    start_step = str(context_payload.get("start_step") or "").strip()
    if start_step:
        cli_args.extend(['--start-step', start_step])

    proc = subprocess.Popen(
        cli_args,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        env=env,
        cwd=str(subprocess_cwd),
    )
    started_monotonic = time.monotonic()
    child = ChildExecution(
        run_id=str(run['id']),
        run_code=str(run.get('run_code') or ''),
        step_run_id=step_run_id,
        step_name=str(step_run.get('step_name') or ''),
        run_payload=run,
        step_run_payload=step_run,
        request_payload=request_payload,
        request_path=request_path,
        result_path=result_path,
        combined_log_path=combined_log_path,
        child_event_log_path=child_event_log_path,
        process=proc,
        started_at_monotonic=started_monotonic,
        started_at_iso=_utcnow_iso(),
        state='running',
        last_heartbeat_at=0.0,
        job_step_result_path=job_step_result_path,
    )
    logger.log('info', 'child_spawned', message='spawned execute-step child', child=child, details={'request_path': str(request_path), 'result_path': str(result_path), 'log_file': str(combined_log_path), 'step_spec_source': step_spec_source, 'engine_pythonpath': env.get('PYTHONPATH', '(default)'), 'coder_override': request_payload.get('coder_override')})
    return child


def _resolve_subprocess_cwd(*, project_root: str | None, workspace_root: str | None) -> Path:
    """Resolve the working directory for child subprocess.

    Prefers project_root, then workspace_root, falls back to cwd.

    Args:
        project_root: Project root from request payload.
        workspace_root: Workspace root from request payload.

    Returns:
        Resolved Path for subprocess CWD.
    """
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


def _child_result(child: ChildExecution) -> dict[str, Any]:
    """Read and return the child execution result.

    Checks job step directory first (manual mode output), then falls
    back to worker runtime directory.

    Args:
        child: ChildExecution to read result from.

    Returns:
        Result dict from result.json, or failure dict if missing.
    """
    diagnostics = {
        'log_file': str(child.combined_log_path), 
        'request_path': str(child.request_path), 
        'result_path': str(child.result_path),
        'job_step_result_path': str(child.job_step_result_path) if child.job_step_result_path else None,
    }
    
    # Check job step directory first (manual mode writes here)
    if child.job_step_result_path and child.job_step_result_path.exists():
        payload = json.loads(child.job_step_result_path.read_text(encoding='utf-8'))
        payload.setdefault('diagnostics', {}).update(diagnostics)
        if child.exit_code is not None:
            payload['diagnostics']['subprocess_return_code'] = child.exit_code
        return payload
    
    # Fall back to worker runtime directory (legacy)
    if child.result_path.exists():
        payload = json.loads(child.result_path.read_text(encoding='utf-8'))
        payload.setdefault('diagnostics', {}).update(diagnostics)
        if child.exit_code is not None:
            payload['diagnostics']['subprocess_return_code'] = child.exit_code
        return payload
        
    reason = f'child process exited without result file for step {child.step_name}'
    return _failure_result(step_name=child.step_name, code='CHILD_RESULT_MISSING', reason=reason, diagnostics=diagnostics | {'subprocess_return_code': child.exit_code})


def _terminate_child(child: ChildExecution, logger: _DaemonLogger, sigkill: bool = False) -> None:
    """Terminate a child process gracefully or forcefully.

    Args:
        child: ChildExecution to terminate.
        logger: Daemon logger instance.
        sigkill: If True, send SIGKILL instead of SIGTERM.
    """
    try:
        if sigkill:
            child.process.kill()
            if os.name == 'nt':
                logger.log('error', 'child_killed', message='force terminated child process', child=child)
            else:
                logger.log('error', 'child_killed', message='sent SIGKILL to child', child=child)
        else:
            child.process.terminate()
            if os.name == 'nt':
                logger.log('error', 'child_terminated', message='terminated child process', child=child)
            else:
                logger.log('error', 'child_terminated', message='sent SIGTERM to child', child=child)
    except ProcessLookupError:
        return


@dataclass
class SupervisorConfig:
    """Configuration for the daemon supervisor.

    Encapsulates all parameters needed to run the supervisor loop,
    replacing the previous 17-parameter function signature.
    """
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


# V2 daemon code moved to agent_runner_v2/v2/daemon.py
# _spawn_child_v2 and _run_supervisor_v2 are now in the v2/ module.


def _run_supervisor(*, config: SupervisorConfig) -> int:
    """Run the main daemon supervisor loop.

    Polls backend for work, spawns children, monitors liveness,
    and handles timeouts and shutdown signals.

    V2 mode: If v2_backend_url is configured, uses a simplified claim loop
    that delegates all routing to the V2 backend's state machine.

    Args:
        config: Supervisor configuration dataclass containing all parameters.

    Returns:
        Exit code (0 for normal shutdown).
    """
    from .backend_client import BackendClient
    from .daemon_runtime import build_job_sync_payload
    from .job_state import job_dir
    from .v2.sync import resolve_v2_backend_url

    v2_url = resolve_v2_backend_url()
    if v2_url:
        from .v2.daemon import run_supervisor_v2
        return run_supervisor_v2(config=config, v2_url=v2_url)

    logger = _DaemonLogger(config.log_file, config.worker_id)
    client = BackendClient(config.backend_url)
    client.register_worker(worker_id=config.worker_id, host_name=None, capabilities={'mode': ['execute-step-daemon'], 'max_parallel': config.max_parallel}, worker_label=config.worker_label)
    logger.log('info', 'daemon_started', message='worker daemon started', details={'backend_url': config.backend_url, 'worker_label': config.worker_label, 'max_parallel': config.max_parallel, 'runtime_dir': str(config.runtime_dir), 'step_spec_source': config.step_spec_source, 'cli_version': config.cli_version, 'engine_version': config.engine_version, 'engine_pythonpath': config.cli_pythonpath or '(ambient)'})

    children: dict[str, ChildExecution] = {}
    terminal_run_ids: set[str] = set()
    seen_approval_requests: dict[str, tuple[str, str]] = {}
    running = True

    def _handle_signal(_sig, _frame):
        nonlocal running
        running = False
        logger.log('info', 'daemon_shutdown_signal', message='received shutdown signal')

    signal.signal(signal.SIGINT, _handle_signal)
    if os.name != 'nt':
        signal.signal(signal.SIGTERM, _handle_signal)

    while running or children:
        now = time.monotonic()
        active = 0
        for step_run_id in list(children):
            child = children[step_run_id]
            proc_rc = child.process.poll()
            last_activity = _latest_mtime([child.combined_log_path, child.result_path], child.started_at_monotonic)
            if proc_rc is None:
                active += 1
                if child.term_sent_at is not None and now - child.term_sent_at >= config.kill_grace_seconds:
                    child.state = 'killed'
                    child.watchdog_reason = 'kill_grace_exceeded'
                    _terminate_child(child, logger, sigkill=True)
                elif config.step_timeout_seconds > 0 and child.term_sent_at is None and now - child.started_at_monotonic >= config.step_timeout_seconds:
                    child.state = 'timed_out'
                    child.watchdog_reason = 'step_timeout_exceeded'
                    child.term_sent_at = now
                    logger.log('error', 'child_timeout', message='child exceeded timeout', child=child, details={'timeout_seconds': config.step_timeout_seconds})
                    _terminate_child(child, logger, sigkill=False)
                elif child.term_sent_at is None and now - last_activity >= config.stalled_seconds and child.state != 'stalled':
                    child.state = 'stalled'
                    child.watchdog_reason = 'log_inactive'
                    logger.log('warning', 'child_stalled', message='child appears stalled', child=child, details={'stalled_seconds': config.stalled_seconds})
                elif child.term_sent_at is None and child.state != 'running':
                    child.state = 'running'
                    child.watchdog_reason = ''
                    logger.log('info', 'child_running', message='child is running', child=child)
                if now - child.last_heartbeat_at >= max(5, config.poll_seconds):
                    try:
                        _send_child_heartbeat(client, config.worker_id, child, status='busy')
                        child.last_heartbeat_at = now
                    except RuntimeError as hb_err:
                        # Backend temporarily unavailable (e.g., during sync)
                        logger.log('warning', 'heartbeat_failed', message=f'child heartbeat failed: {hb_err}', child=child)
                        # Don't update last_heartbeat_at, will retry next cycle
                continue

            child.exit_code = proc_rc
            # CLI subprocess handles result syncing to backend directly (Phase 1+).
            # Daemon only monitors liveness and logs exit.
            logger.log('info', 'child_exited', message='child finished', child=child, details={'exit_code': proc_rc})
            if proc_rc != 0:
                terminal_run_ids.add(child.run_id)
            del children[step_run_id]

        if running:
            # Check backend health before polling
            try:
                client.heartbeat(worker_id=config.worker_id, status='polling', current_step_run_id=None)
            except RuntimeError as hb_err:
                # Backend temporarily unavailable (e.g., during sync)
                logger.log('warning', 'poll_heartbeat_failed', message=f'poll heartbeat failed: {hb_err}', details={'active_children': len(children)})
                time.sleep(config.poll_seconds)
                continue

            while len(children) < config.max_parallel:
                logger.log('info', 'poll_started', message='polling for work', details={'active_children': len(children)})
                try:
                    claim = client.claim_step(worker_id=config.worker_id)
                except RuntimeError as claim_err:
                    # Backend temporarily unavailable
                    logger.log('warning', 'claim_step_failed', message=f'claim_step failed: {claim_err}', details={'active_children': len(children)})
                    break

                if not claim.get('step_run') or not claim.get('run'):
                    logger.log('info', 'poll_no_work', message='no work available', details={'active_children': len(children)})
                    break
                # Check if a stop was requested — agent-runner-v2 owns this decision
                if _is_stop_requested(claim['run']):
                    _handle_stop_on_claim(client, claim, logger)
                    continue
                # Check if quit_daemon was requested via context_payload
                if _is_quit_daemon_requested(claim['run']):
                    should_quit = _handle_quit_daemon(client, claim, logger)
                    if should_quit:
                        running = False
                        break
                    continue
                # Skip runs this daemon already processed as failed (safety net
                # against backend re-serving a run whose sync didn't stick).
                claim_run_id = str(claim['run'].get('id') or '')
                if claim_run_id in terminal_run_ids:
                    run_code = str(claim['run'].get('run_code') or '')
                    logger.log('info', 'skip_terminal_run', message=f'run {run_code} already failed in this daemon session, skipping', details={'run_id': claim_run_id, 'run_code': run_code})
                    continue
                try:
                    child = _spawn_child(claim=claim, runtime_root=config.runtime_dir, cli_pythonpath=config.cli_pythonpath, logger=logger, backend_url=config.backend_url, step_spec_source=config.step_spec_source)
                except Exception as exc:
                    step_run_id = str(claim.get('step_run', {}).get('id') or '')
                    run_code = str(claim.get('run', {}).get('run_code') or '')
                    logger.log('error', 'spawn_child_failed', message=f'failed to spawn child for run {run_code}: {exc}', details={'step_run_id': step_run_id, 'run_code': run_code, 'error': str(exc)})
                    try:
                        client.sync_job_state(
                            step_run_id=step_run_id,
                            payload={
                                "run_status": "failed",
                                "step_status": "failed",
                                "step_outcome": "failed",
                                "step_coder": None,
                                "step_duration_seconds": 0,
                                "next_step_name": None,
                                "output_payload": {},
                                "error_message": f"Daemon failed to spawn child: {exc}",
                                "review": None,
                                "artifacts": [],
                                "events": [{"event_type": "SPAWN_FAILED", "message": f"Failed to spawn child: {exc}"}],
                            },
                        )
                    except Exception:
                        pass
                    continue
                children[child.step_run_id] = child
                _send_child_heartbeat(client, config.worker_id, child, status='busy')
                child.last_heartbeat_at = time.monotonic()
                active = len(children)
                if config.once:
                    running = False
                    break

            # Check for approval requests on runs assigned to this worker
            # This handles the case where a step completed with WAITING_FOR_HUMAN_APPROVAL
            # and the console has recorded an approval request via sync_job_state
            if running and len(children) < config.max_parallel:
                try:
                    # Query for runs assigned to this worker that might have approval requests
                    runs_response = client.list_runs(worker_id=config.worker_id)
                    runs_list = runs_response if isinstance(runs_response, list) else runs_response.get("runs", [])

                    current_approval_requests: dict[str, tuple[str, str]] = {}

                    for run_data in runs_list:
                        if len(children) >= config.max_parallel:
                            break

                        # Check if this run has an approval request
                        approval_request = _get_approval_request(run_data)
                        if approval_request:
                            run_id = str(run_data.get("id") or "")
                            run_code = str(run_data.get("run_code") or "")
                            request_key = (
                                str(approval_request.get("action_type") or ""),
                                str(approval_request.get("action_step") or ""),
                            )
                            current_approval_requests[run_id] = request_key

                            # Skip if we're already handling this run
                            if f"approval-{run_id}" in children:
                                continue
                            if seen_approval_requests.get(run_id) == request_key:
                                continue

                            logger.log(
                                "info", "approval_request_detected",
                                message=f"Detected {approval_request['action_type']} for run {run_code}",
                                details={"run_id": run_id, "run_code": run_code, "action_step": approval_request["action_step"]},
                            )

                            # Spawn CLI to handle the approval
                            approval_child = _spawn_approval_child(
                                run=run_data,
                                approval_request=approval_request,
                                runtime_root=config.runtime_dir,
                                cli_pythonpath=config.cli_pythonpath,
                                logger=logger,
                                backend_url=config.backend_url,
                            )

                            if approval_child:
                                seen_approval_requests[run_id] = request_key
                                children[approval_child.step_run_id] = approval_child
                                _send_child_heartbeat(client, config.worker_id, approval_child, status='busy')
                                approval_child.last_heartbeat_at = time.monotonic()

                    stale_run_ids = [
                        run_id for run_id, request_key in seen_approval_requests.items()
                        if current_approval_requests.get(run_id) != request_key
                    ]
                    for run_id in stale_run_ids:
                        del seen_approval_requests[run_id]

                except RuntimeError as list_err:
                    logger.log('warning', 'approval_poll_failed', message=f'Failed to poll for approval requests: {list_err}')

        if not children:
            try:
                client.heartbeat(worker_id=config.worker_id, status='idle', current_step_run_id=None)
            except RuntimeError as hb_err:
                logger.log('warning', 'idle_heartbeat_failed', message=f'idle heartbeat failed: {hb_err}')
            if config.once and not running:
                break
        time.sleep(max(config.poll_seconds, 1))

    if children:
        for child in children.values():
            _terminate_child(child, logger, sigkill=False)
    client.heartbeat(worker_id=config.worker_id, status='idle', current_step_run_id=None)
    logger.log('info', 'daemon_shutdown', message='worker daemon stopped')
    return 0


def main(argv: list[str] | None = None) -> int:
    """Daemon CLI entry point.

    Parses arguments, resolves configuration, and starts supervisor.

    Args:
        argv: Optional argument list. Defaults to sys.argv.

    Returns:
        Exit code from supervisor.
    """
    import argparse

    cfg = _load_config()
    engine_version = (cfg.get('engine_version') or '').strip() or '(not set)'

    from .run_agent import __version__ as cli_version
    p = argparse.ArgumentParser(prog='ukbe-run-agent daemon', description='Worker daemon supervisor.')
    p.add_argument('-v', '--version', action='version', version=f'%(prog)s {cli_version} (engine: {engine_version})')
    p.add_argument('worker_id', nargs='?', default='', help='Worker ID (overrides config and WORKER_ID env var).')
    p.add_argument('--worker-label', default='', help='Queue label override (live or dev).')
    p.add_argument('--backend-url', default='', help='Backend URL override.')
    p.add_argument('--poll-seconds', type=int, default=0, help='Poll interval override.')
    p.add_argument('--log-file', default='', help='Daemon log file path override.')
    p.add_argument('--max-parallel', type=int, default=0, help='Maximum concurrent child executions.')
    p.add_argument('--runtime-dir', default='', help='Runtime directory for child request/result files.')
    p.add_argument('--stalled-seconds', type=int, default=0, help='Seconds without child log/result activity before marking stalled.')
    p.add_argument('--step-timeout-seconds', type=int, default=0, help='Hard timeout for a child execution.')
    p.add_argument('--kill-grace-seconds', type=int, default=0, help='Grace period between SIGTERM and SIGKILL.')
    p.add_argument('--step-spec-source', default='', help='Workflow step spec source: global, backend, or hybrid.')
    p.add_argument('--engine-root', default='', help='Explicit engine root to prepend to PYTHONPATH for child runs.')
    p.add_argument('--once', action='store_true', help='Claim and process at most one step, then exit.')
    args = p.parse_args(argv)

    # Single instance enforcement - only one daemon can run
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

    bootstrap_logger = _DaemonLogger(log_file, worker_id)
    cli_pythonpath = args.engine_root or _resolve_engine_pythonpath(cfg, bootstrap_logger.log)
    runtime_dir.mkdir(parents=True, exist_ok=True)

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

    return _run_supervisor(config=config)
