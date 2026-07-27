"""Request a graceful stop for a backend run (Operator Console command).

Invoked via: ukbe-run-agent stop <run_id> [--reason "..."]

This is the OPERATOR CONSOLE command for requesting a run to stop.
It does NOT immediately terminate the running job — it sets a stop flag
in the backend database. The daemon will pick up this flag and handle
the actual termination.

Flow:
  1. Operator Console calls this CLI command with run_id
  2. CLI queries backend for active step_run_id
  3. CLI syncs step-level cancelled status to backend
  4. CLI sets run-level stop flag in backend DB
  5. Daemon (running the job) detects stop flag and calls --cancel-run

This is a "request to stop" — the actual job termination happens when
the daemon processes the stop request via --cancel-run.

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
        description="Request a graceful stop for a backend run after the current step.",
    )
    p.add_argument("run_id", help="Run ID (UUID) to stop.")
    p.add_argument("--reason", default="", help="Optional operator reason.")
    p.add_argument("--backend-url", default="", help="Backend URL override.")
    args = p.parse_args(argv)

    cfg = _load_config()
    backend_url = (
        args.backend_url
        or os.environ.get("AGENT_RUNNER_BACKEND_URL")
        or str(cfg.get("backend_url") or "")
        or "http://localhost:8100"
    )

    client = BackendClient(backend_url)
    try:
        # Step 1: Query run to get active step_run_id
        step_run_id = ""
        try:
            run_detail = client.get_run(run_id=args.run_id)
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
                    "error_message": args.reason or "Cancelled by operator",
                    "review": None,
                    "artifacts": [],
                    "context_payload": {"__run_control": {"stop_requested": True}},
                    "events": [{"event_type": "RUN_STOPPED",
                                "message": f"Run {args.run_id} cancelled by operator"}],
                },
            )

        # Step 3: Set run-level stop flag
        result = client.stop_run(
            run_id=args.run_id,
            reason=args.reason or None,
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
