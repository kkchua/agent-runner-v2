"""Reset a run's current step to a different step.

Invoked via: ukbe-run-agent reset-step <run_id> <step_name>

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
    """Reset a run's current step to a different step.

    Parameters
    ----------
    argv :
        Command-line arguments (excluding the program name).
        Requires positional run_id (UUID) and step_name.

    Returns
    -------
    int
        0 on success, 1 on error.
    """
    p = argparse.ArgumentParser(
        prog="ukbe-run-agent reset-step",
        description="Reset a run's current step to a different step.",
    )
    p.add_argument("run_id", help="Run ID (UUID) to reset.")
    p.add_argument("step_name", help="Target step name.")
    args = p.parse_args(argv)

    cfg = _load_config()
    backend_url = (os.environ.get("AGENT_RUNNER_BACKEND_URL")
                   or str(cfg.get("backend_url") or "")
                   or "http://localhost:8100")

    client = BackendClient(backend_url)
    try:
        result = client.reset_run_step(run_id=args.run_id, step_name=args.step_name)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 1
