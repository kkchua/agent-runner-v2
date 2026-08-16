"""List workflow runs from the backend registry.

Invoked via: ukbe-run-agent list-runs [--worker-id X] [--status-group non_terminal|terminal|all]

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
    """List workflow runs from the backend.

    Parameters
    ----------
    argv :
        Command-line arguments (excluding the program name).
        Supports --worker-id, --status-group, --workflow-name.

    Returns
    -------
    int
        0 on success, 1 on error.
    """
    p = argparse.ArgumentParser(
        prog="ukbe-run-agent list-runs",
        description="List workflow runs from the backend.",
    )
    p.add_argument("--worker-id", default="",
                   help="Filter by worker ID.")
    p.add_argument("--status-group", default="non_terminal",
                   choices=["non_terminal", "terminal", "all"],
                   help="Status group filter (default: non_terminal).")
    p.add_argument("--workflow-name", default="",
                   help="Filter by workflow name.")
    args = p.parse_args(argv)

    cfg = _load_config()
    backend_url = (os.environ.get("AGENT_RUNNER_BACKEND_URL")
                   or str(cfg.get("backend_url") or "")
                   or "http://localhost:8100")

    client = BackendClient(backend_url)
    try:
        result = client.list_runs(
            status_group=args.status_group if args.status_group != "all" else None,
            worker_id=args.worker_id or None,
            workflow_name=args.workflow_name or None,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 1
