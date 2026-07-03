#!/usr/bin/env python3
"""
actions/submit_comfyui.py - Submit prompt entries to ComfyUI remote API.

Reads JSON files from {IMAGE_CSV_RUN_DIR}, authenticates to the ComfyUI API,
submits each entry, and writes summary + meta.json sidecar.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from ..action_result import ActionResult
from ..runtime_context import write_meta_sidecar

# Package root — comfyui_config.json lives alongside the .py modules
_PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def _fail(
    project_root: Path,
    run_dir: Path,
    run_dir_str: str,
    remark: str,
    code: str,
) -> ActionResult:
    """Helper: write meta.json for rejection and return ActionResult."""
    write_meta_sidecar(run_dir / "submission_results.meta.json", status="REJECTED", remark=remark, artifacts={})
    return ActionResult(
        status="REJECTED",
        remark=remark,
        artifacts={},
        reject_code=code,
    )


def submit_comfyui(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Submit all prompt entries from IMAGE_CSV_RUN_DIR to ComfyUI API."""

    # Load .env from project root if present (action runs in-process, no shell)
    env_file = project_root / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

    run_dir_str = context.get("IMAGE_CSV_RUN_DIR", "")
    if not run_dir_str:
        return ActionResult(
            status="REJECTED",
            remark="IMAGE_CSV_RUN_DIR context variable is empty -- cannot locate JSON files",
            artifacts={},
            reject_code="MISSING_RUN_DIR",
        )

    run_dir = project_root / run_dir_str
    if not run_dir.exists() or not run_dir.is_dir():
        return _fail(project_root, run_dir, run_dir_str,
                     "Run directory does not exist: " + run_dir_str,
                     "RUN_DIR_MISSING")

    # Load ComfyUI config
    config_path = _PACKAGE_ROOT / "comfyui_config.json"
    if not config_path.exists():
        return _fail(project_root, run_dir, run_dir_str,
                     "ComfyUI config not found: comfyui_config.json",
                     "CONFIG_MISSING")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    base_url = config["base_url"].rstrip("/")
    email_key = config["email_env"]
    password_key = config["password_env"]
    delay = config.get("delay_seconds", 5)
    test_mode = config.get("test_mode", False)

    email = os.environ.get(email_key)
    password = os.environ.get(password_key)

    if not email or not password:
        return _fail(project_root, run_dir, run_dir_str,
                     "Missing credentials: " + email_key + "=" + str(bool(email))
                     + ", " + password_key + "=" + str(bool(password)),
                     "CREDENTIALS_MISSING")

    # Workflow key override from CLI
    workflow_override = context.get("WORKFLOW_KEY_OVERRIDE", "")

    # Default workflow key from config (fallback when entries lack workflowKey)
    default_workflow_key = config.get("default_workflow_key", "")

    login_url = base_url + "/api/v1/auth/login"
    execute_url = base_url + "/api/v1/agent-studio/execute"

    # Authenticate
    try:
        status_code, login_body = _post_json(
            login_url,
            {"email": email, "password": password},
        )
        login_resp = json.loads(login_body)
        token = login_resp["token"]
    except Exception as exc:
        return _fail(project_root, run_dir, run_dir_str,
                     "Authentication failed: " + str(exc),
                     "AUTH_FAILED")

    # Collect JSON files (exclude sidecars and our own output files)
    json_files = sorted(run_dir.glob("*.json"))
    json_files = [
        p for p in json_files
        if p.name not in ("meta.json", "submission_results.json", "submission_results.meta.json")
    ]

    results = []
    submitted = 0
    succeeded = 0
    failed = 0

    for json_file in json_files:
        try:
            entries = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception as e:
            results.append({
                "source_file": json_file.name,
                "error": "failed_to_parse_json: " + str(e),
            })
            continue

        if not isinstance(entries, list):
            results.append({
                "source_file": json_file.name,
                "error": "json_root_is_not_an_array",
            })
            continue

        for idx, entry in enumerate(entries):
            submitted += 1
            workflow_key = (
                workflow_override
                or entry.get("workflowKey")
                or default_workflow_key
            )

            if not workflow_key:
                failed += 1
                results.append({
                    "source_file": json_file.name,
                    "entry_index": idx,
                    "image_filename": entry.get("image_filename"),
                    "status": "failed",
                    "error": "missing_workflowKey",
                })
                time.sleep(delay)
                continue

            try:
                status_code, body = _post_json(
                    execute_url,
                    {
                        "workflow_key": workflow_key,
                        "inputs": entry,
                        "test_mode": test_mode,
                    },
                    headers={"Authorization": "Bearer " + token},
                )
                resp = json.loads(body)
                job_id = (
                    resp.get("job_id")
                    or resp.get("data", {}).get("job_id")
                    or resp.get("id")
                )

                if job_id:
                    succeeded += 1
                    results.append({
                        "source_file": json_file.name,
                        "entry_index": idx,
                        "image_filename": entry.get("image_filename"),
                        "status": "succeeded",
                        "workflow_key": workflow_key,
                        "job_id": job_id,
                        "response_status": status_code,
                    })
                else:
                    failed += 1
                    results.append({
                        "source_file": json_file.name,
                        "entry_index": idx,
                        "image_filename": entry.get("image_filename"),
                        "status": "failed",
                        "workflow_key": workflow_key,
                        "error": "missing_job_id_in_response",
                        "response": resp,
                        "response_status": status_code,
                    })
            except urllib.error.HTTPError as e:
                failed += 1
                err_body = e.read().decode("utf-8", errors="replace")
                results.append({
                    "source_file": json_file.name,
                    "entry_index": idx,
                    "image_filename": entry.get("image_filename"),
                    "status": "failed",
                    "workflow_key": workflow_key,
                    "error": "http_error_" + str(e.code),
                    "response": err_body,
                })
            except Exception as e:
                failed += 1
                results.append({
                    "source_file": json_file.name,
                    "entry_index": idx,
                    "image_filename": entry.get("image_filename"),
                    "status": "failed",
                    "workflow_key": workflow_key,
                    "error": "exception: " + str(e),
                })

            time.sleep(delay)

    # Write summary
    summary_path = run_dir / "submission_results.json"
    summary = {
        "schema_version": "v2",
        "source_directory": run_dir_str,
        "submitted_count": submitted,
        "succeeded_count": succeeded,
        "failed_count": failed,
        "results": results,
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Determine status
    overall_status = "APPROVED" if submitted > 0 and failed == 0 else "REJECTED"
    remark = "Submitted " + str(submitted) + " entries: " + str(succeeded) + " succeeded, " + str(failed) + " failed"
    if submitted == 0:
        remark = "No JSON entries found to submit"
        overall_status = "REJECTED"

    artifacts = {}
    if overall_status == "APPROVED":
        artifacts["IMAGE_CSV_SUBMIT_RESULT"] = str(
            (run_dir / "submission_results.json").relative_to(project_root)
        )

    # Write meta.json sidecar
    write_meta_sidecar(
        run_dir / "submission_results.meta.json",
        status=overall_status,
        remark=remark,
        artifacts=artifacts,
    )

    return ActionResult(
        status=overall_status,
        remark=remark,
        artifacts=artifacts,
    )


def _post_json(
    url: str,
    payload: dict,
    headers: dict | None = None,
    timeout: int = 120,
) -> tuple[int, str]:
    """POST JSON to a URL, return (status_code, response_body)."""
    data = json.dumps(payload).encode("utf-8")
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, body
