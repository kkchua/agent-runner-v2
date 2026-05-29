#!/usr/bin/env python3
"""
submitter.py — ComfyUI API client for agent-runner-v2.

Re-implementation of comfyui-submitter logic in Python.
Handles authentication, workflow execution, and batch submission.

Usage (standalone):
    python -m agent_runner_v2.submitter --input-dir source_csv/20260425-001/
    python -m agent_runner_v2.submitter --input-dir source_csv/20260425-001/ --workflow-key "QWEN/Test"

Usage (from runner):
    submit_files(run_dir, workflow_key_override=None)
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Package root for config loading
PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = PACKAGE_ROOT / "comfyui_config.json"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SubmissionResult:
    """Result of a single entry submission."""
    image_filename: str
    ok: bool
    job_id: str | None = None
    error: str | None = None


@dataclass
class SubmissionSummary:
    """Summary of a batch submission."""
    total_entries: int = 0
    submitted: int = 0
    succeeded: int = 0
    failed: int = 0
    failures: list[dict[str, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load ComfyUI config from JSON file, resolving env var placeholders."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"ComfyUI config not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    cfg: dict[str, Any] = {}
    for key, val in raw.items():
        if isinstance(val, str):
            # Resolve ${ENV_VAR} placeholders
            cfg[key] = val.replace("${", "$").replace("$ENV_VAR", "")  # placeholder
            import re
            def _resolve_env(m: re.Match) -> str:
                return os.environ.get(m.group(1), "")
            cfg[key] = re.sub(r"\$\{(\w+)\}", _resolve_env, val)
        else:
            cfg[key] = val
    return cfg


# ---------------------------------------------------------------------------
# API client
# ---------------------------------------------------------------------------

def _post_json(url: str, body: dict, headers: dict | None = None) -> tuple[int, str]:
    """Make a POST request with JSON body. Returns (status_code, response_text)."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            **(headers or {}),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 0, str(exc.reason)


def login(base_url: str, email: str, password: str) -> str:
    """Authenticate and return JWT token."""
    url = f"{base_url}/api/v1/auth/login"
    status, text = _post_json(url, {"email": email, "password": password})
    if status != 200:
        raise RuntimeError(f"Login failed ({status}): {text}")
    data = json.loads(text)
    token = data.get("token", "")
    if not token:
        raise RuntimeError(f"Login succeeded but no token returned: {text}")
    return token


def execute_workflow(
    base_url: str,
    token: str,
    workflow_key: str,
    entry: dict[str, Any],
    test_mode: bool = False,
) -> tuple[bool, str | None]:
    """Submit a single entry to the ComfyUI workflow.

    Returns:
        (ok, job_id_or_error)
    """
    url = f"{base_url}/api/v1/agent-studio/execute"
    body = {
        "workflow_key": workflow_key,
        "inputs": entry,
        "test_mode": test_mode,
    }
    headers = {"Authorization": f"Bearer {token}"}
    status, text = _post_json(url, body, headers)

    # Re-login on 401 and retry once
    if status == 401:
        print("  Token expired, re-authenticating...", flush=True)
        # Caller needs to re-auth — we signal by raising
        raise RuntimeError(f"Token expired (401): {text}")

    if not text.strip():
        return False, f"Empty response (status={status})"

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return False, f"Invalid JSON response (status={status}): {text[:200]}"

    if status != 200:
        error = data.get("error") or data.get("detail") or text[:200]
        return False, str(error)

    job_id = data.get("job_id") or data.get("id") or "ok"
    return True, job_id


# ---------------------------------------------------------------------------
# Batch submission
# ---------------------------------------------------------------------------

def submit_files(
    run_dir: str | Path,
    *,
    workflow_key_override: str | None = None,
    test_mode: bool = False,
    config: dict | None = None,
) -> SubmissionSummary:
    """Submit all JSON files in run_dir to ComfyUI.

    Args:
        run_dir: Directory containing *.json prompt files (from gen_prompts step).
        workflow_key_override: If set, overrides workflowKey in all entries.
        test_mode: If True, sends test_mode=true in the request body.
        config: Pre-loaded config dict. If None, loads from default config file.

    Returns:
        SubmissionSummary with total counts and per-entry failures.
    """
    cfg = config or load_config()

    # Resolve base_url: env var takes priority, then config file
    base_url = os.environ.get("COMFYUI_BASE_URL", "") or cfg.get("base_url", "")

    # Resolve credentials: read env var names from config, then look up their values
    email_env_name = cfg.get("email_env", "COMFYUI_EMAIL")
    password_env_name = cfg.get("password_env", "COMFYUI_PASSWORD")
    email_val = os.environ.get(email_env_name, "")
    password_val = os.environ.get(password_env_name, "")

    if not base_url:
        raise ValueError("base_url not configured")
    if not email_val or not password_val:
        raise ValueError(f"Credentials not configured: email_env={email_val!r}, password_env={password_val!r}")

    delay_seconds = int(cfg.get("delay_seconds", 5))

    # Authenticate
    print(f"[submitter] Authenticating to {base_url}...", flush=True)
    token = login(base_url, email_val, password_val)
    print("[submitter] Authenticated.", flush=True)

    # Find all JSON files in run_dir
    run_path = Path(run_dir)
    json_files = sorted(run_path.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {run_dir}")

    print(f"[submitter] Found {len(json_files)} file(s) in {run_dir}", flush=True)

    summary = SubmissionSummary()

    for json_file in json_files:
        print(f"\n[submitter] Processing: {json_file.name}", flush=True)

        try:
            entries = json.loads(json_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"  ✗ JSON parse error: {exc}", flush=True)
            summary.failed += 1
            summary.failures.append({
                "file": json_file.name,
                "error": f"JSON parse error: {exc}",
            })
            continue

        if not isinstance(entries, list):
            entries = [entries]

        print(f"  Found {len(entries)} entries", flush=True)

        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue

            summary.total_entries += 1
            summary.submitted += 1

            # Determine workflow key: CLI override > JSON entry
            wkey = workflow_key_override or entry.get("workflowKey", "")
            if not wkey:
                print(f"  ✗ [{i+1}/{len(entries)}] skipped: no workflowKey", flush=True)
                summary.failed += 1
                summary.failures.append({
                    "image_filename": entry.get("image_filename", "unknown"),
                    "error": "No workflowKey in entry and no --workflow-key override",
                })
                continue

            try:
                ok, result = execute_workflow(base_url, token, wkey, entry, test_mode)
            except RuntimeError as exc:
                ok, result = False, str(exc)

            if ok:
                summary.succeeded += 1
                print(f"  ✓ [{i+1}/{len(entries)}] submitted → {result}", flush=True)
            else:
                summary.failed += 1
                summary.failures.append({
                    "image_filename": entry.get("image_filename", "unknown"),
                    "error": str(result),
                })
                print(f"  ✗ [{i+1}/{len(entries)}] failed: {result}", flush=True)

            # Delay between entries
            if i < len(entries) - 1 and delay_seconds > 0:
                time.sleep(delay_seconds)

    print(f"\n[submitter] Summary: {summary.succeeded} succeeded, {summary.failed} failed", flush=True)
    return summary


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="ComfyUI prompt submitter for agent-runner-v2")
    p.add_argument("--input-dir", required=True, help="Directory containing JSON prompt files")
    p.add_argument("--workflow-key", default="", help="Override workflow key for all entries")
    p.add_argument("--test-mode", action="store_true", help="Submit with test_mode=true")
    p.add_argument("--config", default="", help="Path to comfyui_config.json")
    args = p.parse_args()

    try:
        cfg = load_config(args.config) if args.config else None
        summary = submit_files(
            args.input_dir,
            workflow_key_override=args.workflow_key or None,
            test_mode=args.test_mode,
            config=cfg,
        )
        print(json.dumps({
            "status": "APPROVED" if summary.failed == 0 else "REJECTED",
            "summary": {
                "total_entries": summary.total_entries,
                "submitted": summary.submitted,
                "succeeded": summary.succeeded,
                "failed": summary.failed,
                "failures": summary.failures,
            },
        }, indent=2))
        return 0 if summary.failed == 0 else 1
    except Exception as exc:
        print(json.dumps({"status": "FAILED", "error": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
