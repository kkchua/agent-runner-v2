"""Submit a run to the agent-runner-backend API.

Invoked via: ukbe-run-agent submit --workflow-name <name> [options]

Reads backend_url and worker_id from ~/.ukbe-runner/engine/config.json by default.
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
        prog="ukbe-run-agent submit",
        description="Submit a run to the agent-runner-backend API.",
    )
    p.add_argument("--workflow-name", required=True, help="Workflow name, e.g. delivery_scaffold_v1")
    p.add_argument("--project-root", default="", help="Project root path for the run.")
    p.add_argument("--worker-id", default="", help="Pin run to a specific worker ID.")
    p.add_argument("--worker-label", default="", help="Queue label (live or dev). Defaults to config/live.")
    p.add_argument("--backend-url", default="", help="Backend URL override.")
    p.add_argument("--input", action="append", default=[], metavar="KEY=VALUE",
                   help="Input payload key=value pairs (repeatable).")
    args = p.parse_args(argv)

    cfg = _load_config()

    backend_url = (args.backend_url
                   or os.environ.get("AGENT_RUNNER_BACKEND_URL")
                   or str(cfg.get("backend_url") or "")
                   or "http://localhost:8100")
    worker_id = (args.worker_id
                 or os.environ.get("AGENT_RUNNER_WORKER_ID")
                 or str(cfg.get("worker_id") or ""))
    worker_label = (args.worker_label
                    or os.environ.get("WORKER_LABEL")
                    or str(cfg.get("worker_label") or "live"))

    input_payload: dict[str, str] = {}
    for kv in args.input:
        if "=" not in kv:
            print(f"ERROR: --input must be KEY=VALUE, got: {kv!r}", file=sys.stderr)
            return 1
        k, v = kv.split("=", 1)
        input_payload[k] = v

    client = BackendClient(backend_url)
    try:
        result = client.submit_run(
            workflow_name=args.workflow_name,
            project_root=args.project_root or None,
            target_worker_id=worker_id or None,
            worker_label=worker_label,
            input_payload=input_payload or None,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as e:
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        return 1
