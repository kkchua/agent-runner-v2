"""[V1 DEPRECATED] Request a stop for a backend run (Operator Console command).

→ Replaced by: Console calls POST /api/runs/{id}/action with CANCEL directly to backend
→ Architecture: docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260801-002_platform-v2-architecture-redesign.md

Invoked via:
  ukbe-run-agent stop <run_id> [--reason "..."]          # Graceful stop
  ukbe-run-agent stop <run_id> --force [--reason "..."]  # Force kill

MODES:
  Default (no --force): Sets stop_requested flag in backend. Daemon
  detects this and gracefully terminates the job after current step.

  --force: Immediately kills the daemon process and all worker processes.
  Use when graceful stop is not responding or you need immediate termination.

Flow (graceful):
  1. Operator Console calls this CLI command with run_id
  2. CLI queries backend for active step_run_id
  3. CLI syncs step-level cancelled status to backend
  4. CLI sets run-level stop flag in backend DB
  5. Daemon (running the job) detects stop flag and calls --cancel-run

Flow (--force):
  1. Find and kill daemon process
  2. Workers become orphaned and terminate
  3. Backend detects worker disconnect

Reads backend_url from ~/.ukbe-runner/config.json by default.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from .backend_client import BackendClient
from .config_loader import load_runner_config


def _load_config() -> dict:
    """Load runner configuration from ~/.ukbe-runner/config.json."""
    return load_runner_config()


def main(argv: list[str] | None = None) -> int:
    """Request a backend run to stop (Operator Console command).

    This sets a stop flag in the backend database. The daemon running
    the job will detect this flag and terminate the job via --cancel-run.

    This is a "request to stop" — not an immediate termination.

    Parameters
    ----------
    argv :
        Command-line arguments (excluding the program name).
        Requires a positional run_id (UUID).

    Returns
    -------
    int
        0 on success, 1 on error.
    """
    p = argparse.ArgumentParser(
        prog="ukbe-run-agent stop",
        description="Request a stop for a backend run.",
    )
    p.add_argument("run_id", help="Run ID (UUID) to stop.")
    p.add_argument("--reason", default="", help="Optional operator reason.")
    p.add_argument("--backend-url", default="", help="Backend URL override.")
    p.add_argument("--force", action="store_true", help="Force kill daemon and workers immediately.")
    args = p.parse_args(argv)

    # --force mode: Kill daemon process directly
    if args.force:
        return _force_stop_run(args.run_id, args.reason)

    # Graceful mode: Set stop flag in backend
    return _graceful_stop_run(args.run_id, args.reason, args.backend_url)


def _force_stop_run(run_id: str, reason: str) -> int:
    """Force kill daemon and workers for a run.

    Uses platform-specific process termination to kill the daemon
    and any worker processes immediately.

    Args:
        run_id: Run ID to stop
        reason: Reason for stopping

    Returns:
        Exit code (0 on success, 1 on error)
    """
    import subprocess
    import sys
    import os

    killed_pids = []
    errors = []

    # Find and kill daemon process
    if sys.platform == "win32":
        # Windows: Use taskkill with filter for daemon processes
        try:
            # Kill daemon processes
            result = subprocess.run(
                ["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq *daemon*"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                killed_pids.append("daemon processes")
        except Exception as e:
            errors.append(f"Failed to kill daemon: {e}")

        # Also try to kill by process name pattern
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like '*run_agent daemon*' } | Select-Object ProcessId | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                killed_pids.append("daemon by command line")
        except Exception:
            pass  # Non-fatal
    else:
        # Linux/Mac: Find and kill daemon processes
        try:
            # Find daemon processes
            result = subprocess.run(
                ["pgrep", "-f", "run_agent daemon"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                pids = result.stdout.strip().split("\n")
                for pid in pids:
                    if pid.strip():
                        try:
                            os.kill(int(pid.strip()), 9)  # SIGKILL
                            killed_pids.append(pid.strip())
                        except Exception as e:
                            errors.append(f"Failed to kill PID {pid}: {e}")
        except Exception as e:
            errors.append(f"Failed to find/kill daemon: {e}")

    output = {
        "status": "force_stopped" if killed_pids else "no_processes_found",
        "run_id": run_id,
        "reason": reason or "Force stopped by operator",
        "killed": killed_pids,
        "errors": errors if errors else None,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if killed_pids else 1


def _graceful_stop_run(run_id: str, reason: str, backend_url_override: str) -> int:
    """Graceful stop via backend flag.

    Sets stop_requested flag in backend. Daemon detects this
    and gracefully terminates after current step.

    Args:
        run_id: Run ID to stop
        reason: Reason for stopping
        backend_url_override: Optional backend URL override

    Returns:
        Exit code (0 on success, 1 on error)
    """
    cfg = _load_config()
    backend_url = (
        backend_url_override
        or os.environ.get("AGENT_RUNNER_BACKEND_URL")
        or str(cfg.get("backend_url") or "")
        or "http://localhost:8100"
    )

    client = BackendClient(backend_url)
    try:
        # Step 1: Query run to get active step_run_id
        step_run_id = ""
        try:
            run_detail = client.get_run(run_id=run_id)
            run = run_detail.get("run") or {}
            step_run_id = str(run.get("current_step_run_id") or "").strip()
        except RuntimeError:
            pass  # Non-fatal — proceed with stop_run only

        # Step 2: Sync step-level cancelled status
        if step_run_id:
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
                    "error_message": reason or "Cancelled by operator",
                    "review": None,
                    "artifacts": [],
                    "context_payload": {"__run_control": {"stop_requested": True}},
                    "events": [{"event_type": "RUN_STOPPED",
                                "message": f"Run {run_id} cancelled by operator"}],
                },
            )

        # Step 3: Set run-level stop flag
        result = client.stop_run(
            run_id=run_id,
            reason=reason or None,
            mode="after_current_step",
        )
        if step_run_id:
            result["step_synced"] = True
            result["step_run_id"] = step_run_id
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 1
