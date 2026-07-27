"""Approve, reject, resume, or retry a run awaiting human action.

Invoked via: ukbe-run-agent approve <run-id> [--reject] [--resume] [--retry] [--feedback "notes"]

Reads backend_url from ~/.ukbe-runner/config.json by default.

Actions:
  - (default)  Approve the current step and advance to the next.
  - --reject   Reject the current step, triggering on_reject_refine routing.
  - --resume   Force-approve a step waiting for intervention/max-retried.
  - --retry    Reset reject/failure counts and re-execute the same step.
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
    """Approve, reject, resume, or retry a run awaiting human action.

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
        description="Approve or reject a run that is awaiting human action.",
    )
    p.add_argument("run_id", help="Run ID (UUID) to approve or reject.")
    p.add_argument("--reject", action="store_true", default=False,
                   help="Reject the run instead of approving it.")
    p.add_argument("--resume", action="store_true", default=False,
                   help="Resume a step waiting for intervention (force-approve + advance).")
    p.add_argument("--retry", action="store_true", default=False,
                   help="Retry a step (reset counts, re-execute).")
    p.add_argument("--feedback", default="", help="Optional feedback or reason.")
    p.add_argument("--outcome", default="", help="Outcome label override (e.g. 'rejected').")
    p.add_argument("--backend-url", default="", help="Backend URL override.")
    args = p.parse_args(argv)

    cfg = _load_config()
    backend_url = (args.backend_url
                   or os.environ.get("AGENT_RUNNER_BACKEND_URL")
                   or str(cfg.get("backend_url") or "")
                   or "http://localhost:8100")

    # Determine action and default feedback
    if args.reject:
        action = "reject"
    else:
        action = "approve"

    feedback = args.feedback
    if not feedback:
        if args.resume:
            feedback = "Resumed by operator"
        elif args.retry:
            feedback = "Retried by operator"

    client = BackendClient(backend_url)
    try:
        result = client.approve_run(
            run_id=args.run_id,
            action=action,
            feedback=feedback or None,
            outcome=args.outcome or None,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as e:
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        return 1
