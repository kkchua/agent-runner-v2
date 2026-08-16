"""Show a single workflow run's details from the backend.

Invoked via: ukbe-run-agent show-run <run_id>

Reads backend_url from ~/.ukbe-runner/config.json by default.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from .v2.backend_client_v1 import BackendClient
from .config_loader import load_runner_config


def _load_config() -> dict:
    """Load runner configuration from ~/.ukbe-runner/config.json."""
    return load_runner_config()


def main(argv: list[str] | None = None) -> int:
    """Show a single workflow run's details from the backend.

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
        prog="ukbe-run-agent show-run",
        description="Show a single workflow run's details from the backend.",
    )
    p.add_argument("run_id", help="Run ID (UUID) to show.")
    args = p.parse_args(argv)

    cfg = _load_config()
    backend_url = (os.environ.get("AGENT_RUNNER_BACKEND_URL")
                   or str(cfg.get("backend_url") or "")
                   or "http://localhost:8100")

    client = BackendClient(backend_url)
    try:
        result = client.get_run(run_id=args.run_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 1
