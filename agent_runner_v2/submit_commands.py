"""Submit a run to the agent-runner-backend API.

Invoked via: ukbe-run-agent submit --workflow-name <name> [options]

Reads backend_url, worker_id, and worker_label from ~/.ukbe-runner/config.json
by default. All options can be overridden via flags or env vars.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from .backend_client import BackendClient
from .config_loader import load_runner_config


def _load_config() -> dict:
    return load_runner_config()


def _parse_kv(pairs: list[str], flag: str) -> dict[str, str] | None:
    result: dict[str, str] = {}
    for kv in pairs:
        if "=" not in kv:
            print(f"ERROR: {flag} must be KEY=VALUE, got: {kv!r}", file=sys.stderr)
            sys.exit(1)
        k, v = kv.split("=", 1)
        result[k] = v
    return result or None


def _build_error_payload(exc: RuntimeError) -> dict[str, str]:
    message = str(exc)
    workflow_not_found = re.search(r"Workflow '([^']+)' not found", message)
    if workflow_not_found:
        workflow_name = workflow_not_found.group(1)
        return {
            "status": "error",
            "code": "workflow_not_found",
            "message": (
                f"Workflow '{workflow_name}' is not registered in the backend. "
                "Sync workflow definitions first or submit a migrated backend-supported workflow."
            ),
        }
    return {"status": "error", "message": message}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="ukbe-run-agent submit",
        description="Submit a run to the agent-runner-backend API.",
    )
    p.add_argument("--workflow-name", required=True, help="Workflow name, e.g. delivery_scaffold_v1")
    p.add_argument("--project-root", default="", help="Reserved for compatibility; must match the current repository root.")
    p.add_argument("--target-project-root", default="", help="Not supported under the single-repo contract; must match the current repository root when provided.")
    p.add_argument("--workspace-path", default="", help="Workspace path override.")
    p.add_argument("--initiative-id", default="", help="Initiative ID to link to this run.")
    p.add_argument("--worker-id", default="", help="Pin run to a specific worker ID.")
    p.add_argument("--worker-label", default="", help="Queue label (live or dev).")
    p.add_argument("--assigned-provider", default="", help="LLM provider override.")
    p.add_argument("--coder", default="", help="Coder override.")
    p.add_argument("--repo-url", default="", help="Repository URL.")
    p.add_argument("--repo-ref", default="", help="Repository ref (branch/tag/commit).")
    p.add_argument("--backend-url", default="", help="Backend URL override.")
    p.add_argument("--input", action="append", default=[], metavar="KEY=VALUE",
                   help="input_payload key=value (repeatable).")
    p.add_argument("--context", action="append", default=[], metavar="KEY=VALUE",
                   help="context_payload key=value (repeatable).")
    p.add_argument("--env", action="append", default=[], metavar="KEY=VALUE",
                   help="env_overrides key=value (repeatable).")
    p.add_argument("--start-step", default="",
                   help="Override the starting step for a new job (skip earlier steps).")
    args = p.parse_args(argv)
    cwd_root = Path.cwd().resolve()

    if args.project_root and Path(args.project_root).resolve() != cwd_root:
        print(
            f"ERROR: --project-root must match the current repository root under the single-repo contract: {cwd_root}",
            file=sys.stderr,
        )
        return 2
    if args.target_project_root and Path(args.target_project_root).resolve() != cwd_root:
        print(
            f"ERROR: --target-project-root is not supported under the single-repo contract: {cwd_root}",
            file=sys.stderr,
        )
        return 2

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

    client = BackendClient(backend_url)
    try:
        # Build context_payload, merging --start-step if provided
        context_payload = _parse_kv(args.context, "--context") or {}
        if args.start_step:
            context_payload["start_step"] = args.start_step

        result = client.submit_run(
            workflow_name=args.workflow_name,
            initiative_id=args.initiative_id or None,
            target_worker_id=worker_id or None,
            assigned_provider=args.assigned_provider or None,
            coder_override=args.coder or None,
            project_root=str(cwd_root),
            workspace_path=args.workspace_path or None,
            repo_url=args.repo_url or None,
            repo_ref=args.repo_ref or None,
            target_project_root=str(cwd_root),
            worker_label=worker_label,
            input_payload=_parse_kv(args.input, "--input"),
            context_payload=context_payload or None,
            env_overrides=_parse_kv(args.env, "--env"),
        )
        # If --start-step specified, reset the run to the correct step
        if args.start_step:
            run_id = str((result.get("run") or {}).get("id") or "").strip()
            if run_id:
                reset_result = client.reset_run_step(run_id=run_id, step_name=args.start_step)
                result["reset_step"] = reset_result
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as e:
        print(json.dumps(_build_error_payload(e), ensure_ascii=False), file=sys.stderr)
        return 1
