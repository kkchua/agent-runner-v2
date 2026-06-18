"""Approve or reject a run awaiting human action.

Invoked via: ukbe-run-agent approve <run-id> [--reject] [--feedback "notes"]

Reads backend_url from ~/.ukbe-runner/engine/config.json by default.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .backend_client import BackendClient


def _load_config() -> dict:
    local_cfg = Path(".ukbe-runner") / "engine" / "config.json"
    global_cfg = Path.home() / ".ukbe-runner" / "engine" / "config.json"
    path = local_cfg if local_cfg.exists() else global_cfg
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="ukbe-run-agent approve",
        description="Approve or reject a run that is awaiting human action.",
    )
    p.add_argument("run_id", help="Run ID (UUID) to approve or reject.")
    p.add_argument("--reject", action="store_true", default=False,
                   help="Reject the run instead of approving it.")
    p.add_argument("--feedback", default="", help="Optional feedback or reason.")
    p.add_argument("--outcome", default="", help="Outcome label override (e.g. 'rejected').")
    p.add_argument("--backend-url", default="", help="Backend URL override.")
    args = p.parse_args(argv)

    cfg = _load_config()
    backend_url = (args.backend_url
                   or os.environ.get("AGENT_RUNNER_BACKEND_URL")
                   or str(cfg.get("backend_url") or "")
                   or "http://localhost:8100")

    action = "reject" if args.reject else "approve"
    client = BackendClient(backend_url)
    try:
        result = client.approve_run(
            run_id=args.run_id,
            action=action,
            feedback=args.feedback or None,
            outcome=args.outcome or None,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as e:
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        return 1
