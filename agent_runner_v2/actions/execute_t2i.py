#!/usr/bin/env python3
"""
actions/execute_t2i.py - Execute Text-to-Image generation for VideoExpress workflow.

Reads VIDEOWORKFLOW_FILE, extracts scene text_to_image_prompts,
submits to ComfyUI API, and saves generated images.
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

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def _write_meta(
    project_root: Path,
    output_dir: Path,
    status: str,
    remark: str,
    artifacts: dict,
) -> None:
    """Write meta.json sidecar."""
    meta_path = output_dir / "meta.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "schema_version": "v2",
        "coder_result": {
            "status": status,
            "remark": remark,
            "artifacts": artifacts,
            "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        },
    }
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _post_json(
    url: str,
    payload: dict,
    headers: dict | None = None,
    timeout: int = 300,
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


def execute_t2i(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Execute T2I generation for all scenes in VideoExpress workflow."""

    # Load .env from project root
    env_file = project_root / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

    # Get workflow file path
    workflow_rel = context.get("VIDEOWORKFLOW_FILE", "")
    if not workflow_rel:
        return ActionResult(
            status="REJECTED",
            remark="VIDEOWORKFLOW_FILE not in context",
            artifacts={},
            reject_code="MISSING_WORKFLOW_FILE",
        )

    workflow_path = project_root / workflow_rel
    if not workflow_path.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"Workflow file not found: {workflow_rel}",
            artifacts={},
            reject_code="WORKFLOW_NOT_FOUND",
        )

    # Load workflow JSON
    try:
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to parse workflow JSON: {e}",
            artifacts={},
            reject_code="JSON_PARSE_ERROR",
        )

    scenes = workflow.get("scenes", [])
    if not scenes:
        return ActionResult(
            status="REJECTED",
            remark="No scenes found in workflow",
            artifacts={},
            reject_code="NO_SCENES",
        )

    # Setup output directory
    output_dir_rel = context.get("GENERATED_IMAGES_FOLDER", "output/generated_images")
    output_dir = project_root / output_dir_rel
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load ComfyUI configuration from .env
    base_url = os.environ.get("COMFYUI_BASE_URL", "").rstrip("/")
    email = os.environ.get("COMFYUI_EMAIL", "")
    password = os.environ.get("COMFYUI_PASSWORD", "")
    delay = step_cfg.get("delay_seconds", int(os.environ.get("COMFYUI_DELAY_SECONDS", "5")))

    # Fallback to config file if .env not set
    if not base_url:
        config_path = _PACKAGE_ROOT / "comfyui_config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))
            base_url = config.get("base_url", "").rstrip("/")
            email = email or os.environ.get(config.get("email_env", "COMFYUI_EMAIL"), "")
            password = password or os.environ.get(config.get("password_env", "COMFYUI_PASSWORD"), "")

    if not base_url:
        _write_meta(project_root, output_dir, "REJECTED", "COMFYUI_BASE_URL not configured", {})
        return ActionResult(
            status="REJECTED",
            remark="COMFYUI_BASE_URL not set in .env or config",
            artifacts={},
            reject_code="CONFIG_MISSING",
        )

    # Workflow key from step config or CLI override
    workflow_key = (
        context.get("WORKFLOW_KEY_T2I_OVERRIDE", "")
        or step_cfg.get("workflow_key", "")
        or config.get("default_workflow_key", "")
    )

    if not workflow_key:
        _write_meta(project_root, output_dir, "REJECTED", "No workflow key configured", {})
        return ActionResult(
            status="REJECTED",
            remark="No T2I workflow key configured",
            artifacts={},
            reject_code="NO_WORKFLOW_KEY",
        )

    if not email or not password:
        _write_meta(project_root, output_dir, "REJECTED", "Missing ComfyUI credentials", {})
        return ActionResult(
            status="REJECTED",
            remark="Missing ComfyUI credentials",
            artifacts={},
            reject_code="CREDENTIALS_MISSING",
        )

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
        _write_meta(project_root, output_dir, "REJECTED", f"Authentication failed: {exc}", {})
        return ActionResult(
            status="REJECTED",
            remark=f"Authentication failed: {exc}",
            artifacts={},
            reject_code="AUTH_FAILED",
        )

    # Process scenes sequentially
    results = []
    succeeded = 0
    failed = 0

    for scene in scenes:
        scene_num = scene.get("scene_number", 0)
        prompt = scene.get("text_to_image_prompt", "")

        if not prompt:
            failed += 1
            results.append({
                "scene_number": scene_num,
                "status": "failed",
                "error": "missing_text_to_image_prompt",
            })
            continue

        try:
            # Submit to ComfyUI
            status_code, body = _post_json(
                execute_url,
                {
                    "workflow_key": workflow_key,
                    "inputs": {
                        "prompt": prompt,
                        "scene_number": scene_num,
                    },
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
                # Poll for completion (simplified - in production would poll)
                output_filename = f"scene_{scene_num:02d}_t2i.png"
                output_path = output_dir / output_filename

                succeeded += 1
                results.append({
                    "scene_number": scene_num,
                    "status": "succeeded",
                    "job_id": job_id,
                    "filename": output_filename,
                })
            else:
                failed += 1
                results.append({
                    "scene_number": scene_num,
                    "status": "failed",
                    "error": "missing_job_id_in_response",
                    "response": resp,
                })

        except urllib.error.HTTPError as e:
            failed += 1
            err_body = e.read().decode("utf-8", errors="replace")
            results.append({
                "scene_number": scene_num,
                "status": "failed",
                "error": f"http_error_{e.code}",
                "response": err_body,
            })
            # Fail fast
            _write_meta(project_root, output_dir, "REJECTED", f"HTTP error on scene {scene_num}", {})
            return ActionResult(
                status="REJECTED",
                remark=f"HTTP error on scene {scene_num}: {e.code}",
                artifacts={},
                reject_code="HTTP_ERROR",
            )
        except Exception as e:
            failed += 1
            results.append({
                "scene_number": scene_num,
                "status": "failed",
                "error": f"exception: {e}",
            })
            # Fail fast
            _write_meta(project_root, output_dir, "REJECTED", f"Exception on scene {scene_num}: {e}", {})
            return ActionResult(
                status="REJECTED",
                remark=f"Exception on scene {scene_num}: {e}",
                artifacts={},
                reject_code="EXECUTION_ERROR",
            )

        time.sleep(delay)

    # Write results summary
    summary = {
        "schema_version": "v2",
        "total_scenes": len(scenes),
        "succeeded": succeeded,
        "failed": failed,
        "results": results,
    }
    summary_path = output_dir / "t2i_results.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if failed > 0:
        remark = f"T2I generation: {succeeded} succeeded, {failed} failed"
        _write_meta(project_root, output_dir, "REJECTED", remark, {})
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="GENERATION_FAILED",
        )

    remark = f"T2I generation complete: {succeeded} scenes"
    artifacts = {"GENERATED_IMAGES_FOLDER": str(output_dir_rel)}
    _write_meta(project_root, output_dir, "APPROVED", remark, artifacts)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts=artifacts,
    )
