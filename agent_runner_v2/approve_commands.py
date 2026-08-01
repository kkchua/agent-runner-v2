"""[V1 DEPRECATED] Request approval for a backend run (Operator Console command).

→ Replaced by: Console calls POST /api/runs/{id}/action directly to backend
→ Architecture: docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260801-002_platform-v2-architecture-redesign.md

Invoked via:
  ukbe-run-agent approve <run_id> [--reject] [--resume] [--retry] [--feedback "..."]

MODES:
  Default (no flags): Sets approve_requested flag in backend. Daemon
  detects this and spawns CLI with --approve-step to record approval
  in local job.json and advance to next step.

  --reject: Sets reject_requested flag in backend. Daemon detects this
  and spawns CLI with --reject-step to trigger refine loop.

  --resume: Sets resume_requested flag in backend. Daemon detects this
  and spawns CLI with --resume-step to force-approve and advance.

  --retry: Sets retry_requested flag in backend. Daemon detects this
  and spawns CLI with --retry-step to re-execute the step.

Flow (CLI is the brain, backend is dumb persistence):
  1. Operator Console calls this CLI command with run_id
  2. CLI queries backend for active step_run_id
  3. CLI sets approval request flag via sync_job_state ONLY (dumb persistence)
  4. Daemon detects the flag and spawns CLI with --approve-step
  5. CLI loads local job.json, records approval, advances step, syncs

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
    """Request approval/rejection/resume/retry for a backend run.

    This sets a request flag in the backend database via sync_job_state ONLY.
    No other backend endpoints are called. The daemon running the job will
    detect this flag and spawn CLI to handle the action via local job.json.

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
        prog="ukbe-run-agent approve",
        description="Request approval/rejection/resume/retry for a backend run.",
    )
    p.add_argument("run_id", help="Run ID (UUID) to approve/reject/resume/retry.")
    p.add_argument("--reject", action="store_true", default=False,
                   help="Reject the step (triggers refine loop).")
    p.add_argument("--resume", action="store_true", default=False,
                   help="Resume a step waiting for intervention (force-approve + advance).")
    p.add_argument("--retry", action="store_true", default=False,
                   help="Retry a step (reset counts, re-execute).")
    p.add_argument("--feedback", default="", help="Optional feedback or reason.")
    p.add_argument("--backend-url", default="", help="Backend URL override.")
    args = p.parse_args(argv)

    # Determine action type
    if args.reject:
        action_type = "reject_requested"
        action_label = "reject"
    elif args.resume:
        action_type = "resume_requested"
        action_label = "resume"
    elif args.retry:
        action_type = "retry_requested"
        action_label = "retry"
    else:
        action_type = "approve_requested"
        action_label = "approve"

    cfg = _load_config()
    backend_url = (
        args.backend_url
        or os.environ.get("AGENT_RUNNER_BACKEND_URL")
        or str(cfg.get("backend_url") or "")
        or "http://localhost:8100"
    )

    client = BackendClient(backend_url)
    try:
        # Step 1: Query run to get active step_run_id and current step
        step_run_id = ""
        current_step = ""
        try:
            run_detail = client.get_run(run_id=args.run_id)
            run = run_detail.get("run") or {}
            step_run_id = str(run.get("current_step_run_id") or "").strip()
            current_step = str(run.get("current_step") or "").strip()
        except RuntimeError:
            pass  # Non-fatal — proceed with flag setting only

        if not step_run_id:
            print(json.dumps({
                "status": "error",
                "message": f"Could not find active step_run for run {args.run_id}",
            }), file=sys.stderr)
            return 1

        # Step 2: Set approval request flag via sync_job_state ONLY
        # Backend is just dumb persistence - stores the flag
        # Daemon will detect this flag and spawn CLI with --approve-step
        feedback = args.feedback
        if not feedback:
            if args.resume:
                feedback = "Resumed by operator"
            elif args.retry:
                feedback = "Retried by operator"

        client.sync_job_state(
            step_run_id=step_run_id,
            payload={
                # Keep run_status as awaiting_human - don't change it
                # The daemon will detect the flag and spawn CLI to handle
                "run_status": "awaiting_human",
                "step_status": "completed",
                "step_outcome": action_label,
                "step_coder": None,
                "step_duration_seconds": 0,
                "next_step_name": None,
                "output_payload": {},
                "error_message": None,
                "review": None,
                "artifacts": [],
                "context_payload": {
                    "__run_control": {
                        action_type: True,
                        "action_step": current_step,
                        "feedback": feedback,
                    }
                },
                "events": [{
                    "event_type": f"HUMAN_{action_label.upper()}_REQUESTED",
                    "message": f"Human {action_label} requested for step {current_step}",
                    "payload": {"feedback": feedback} if feedback else {},
                }],
            },
        )

        print(json.dumps({
            "status": "ok",
            "message": f"{action_label.capitalize()} request recorded for step {current_step}",
            "run_id": args.run_id,
            "step_run_id": step_run_id,
            "action": action_type,
            "feedback": feedback or None,
        }, indent=2, ensure_ascii=False))
        return 0

    except RuntimeError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 1
