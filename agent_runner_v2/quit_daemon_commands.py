"""Submit a quit command for the daemon.

Invoked via: ukbe-run-agent daemon-quit [options]

Submits a job with __run_control.quit_daemon flag. The daemon will claim this job,
recognize the flag, and gracefully shut down after completing current work.

Uses the special ``__daemon_control__`` workflow — a lightweight control-plane
workflow registered automatically if missing.  No real workflow steps are
executed; the daemon intercepts the ``quit_daemon`` flag and shuts down.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from .backend_client import BackendClient
from .config_loader import load_runner_config

CONTROL_WORKFLOW = "__daemon_control__"


def _load_config() -> dict:
    return load_runner_config()


def _ensure_control_workflow(client: BackendClient, workflow_name: str) -> None:
    """Register the control workflow in the backend if it doesn't exist.

    Checks the workflow list first. If the workflow is missing, loads the
    workflow package from the global runner home and syncs it properly.
    """
    if workflow_name != CONTROL_WORKFLOW:
        return  # Only auto-register the built-in control workflow

    try:
        existing = client._request("GET", "/api/workflows")
        names = [w.get("name") for w in (existing if isinstance(existing, list) else [])]
        if workflow_name in names:
            return
    except Exception:
        pass  # If we can't check, try to register anyway

    try:
        from pathlib import Path
        from .runtime_context import get_workflow_root
        from .workflow_packages.loader import load_workflow_package, bundle_to_template_group_dict
        from .sync_workflows import _strip_bundle_refs
        from urllib import request as url_request

        pkg_dir = Path(get_workflow_root()) / workflow_name
        if not pkg_dir.exists():
            return  # Can't register without a local package

        bundle = load_workflow_package(pkg_dir)
        definition = _strip_bundle_refs(bundle_to_template_group_dict(bundle))

        payload = json.dumps({
            "workflow_name": workflow_name,
            "definition": definition,
            "preserve_history": True,
            "changed_by": "daemon_quit",
            "change_reason": "Auto-register control workflow for daemon quit",
        }).encode("utf-8")

        backend_url = client.base_url.rstrip("/")
        req = url_request.Request(
            f"{backend_url}/api/admin/workflows/sync",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with url_request.urlopen(req, timeout=30):
            pass
    except Exception as exc:
        print(
            json.dumps({"warning": f"Could not auto-register {workflow_name}: {exc}"}),
            file=sys.stderr,
        )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="ukbe-run-agent daemon-quit",
        description="Submit a quit command for the daemon to gracefully shut down.",
    )
    p.add_argument("--worker-id", default="", help="Target specific worker ID (optional).")
    p.add_argument("--worker-label", default="", help="Target specific worker label (optional).")
    p.add_argument("--reason", default="", help="Reason for quit (logged).")
    p.add_argument("--backend-url", default="", help="Backend URL override.")
    p.add_argument("--workflow", default=CONTROL_WORKFLOW,
                   help=f"Control workflow name (default: {CONTROL_WORKFLOW}).")
    args = p.parse_args(argv)

    cfg = _load_config()

    backend_url = (args.backend_url
                   or os.environ.get("AGENT_RUNNER_BACKEND_URL")
                   or str(cfg.get("backend_url") or "")
                   or "http://localhost:8100")
    worker_id = (args.worker_id
                 or os.environ.get("AGENT_RUNNER_WORKER_ID")
                 or str(cfg.get("worker_id") or "")
                 or "kode-worker-01")
    worker_label = (args.worker_label
                    or os.environ.get("AGENT_RUNNER_WORKER_LABEL")
                    or str(cfg.get("worker_label") or "")
                    or "live")

    client = BackendClient(backend_url)

    try:
        # Ensure the control workflow exists in the backend
        _ensure_control_workflow(client, args.workflow)

        # Submit a job with quit_daemon flag in __run_control
        # The daemon will recognize this and shut down gracefully
        result = client.submit_run(
            workflow_name=args.workflow,
            input_payload={
                "command": "quit_daemon",
                "reason": args.reason or "Quit requested from console",
            },
            context_payload={
                "__run_control": {
                    "quit_daemon": True,
                    "requested_at": datetime.now(timezone.utc).isoformat(),
                    "reason": args.reason or "Quit requested from console",
                }
            },
            target_worker_id=worker_id or None,
            worker_label=worker_label,
        )

        run_obj = result.get("run", result)
        output = {
            "status": "submitted",
            "run_id": run_obj.get("id"),
            "run_code": run_obj.get("run_code"),
            "worker_id": worker_id,
            "message": "Quit command submitted. Daemon will exit after completing current work.",
        }
        print(json.dumps(output, indent=2))
        return 0

    except RuntimeError as exc:
        error_output = {
            "status": "error",
            "message": str(exc),
        }
        print(json.dumps(error_output, indent=2), file=sys.stderr)
        return 1
