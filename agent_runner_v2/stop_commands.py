"""Request a graceful stop for a backend run."""
from __future__ import annotations

import argparse
import json
import os
import sys

from .backend_client import BackendClient
from .config_loader import load_runner_config


def _load_config() -> dict:
    return load_runner_config()


def main(argv: list[str] | None = None) -> int:
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
        result = client.stop_run(
            run_id=args.run_id,
            reason=args.reason or None,
            mode="after_current_step",
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 1
