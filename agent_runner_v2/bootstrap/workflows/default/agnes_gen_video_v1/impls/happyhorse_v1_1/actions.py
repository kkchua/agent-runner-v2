"""Implementation actions for agnes_gen_video_v1.impls.happyhorse_v1_1.

Implements the generate_videos_happyhorse action using HappyHorse-1.1-i2v API
(DashScope-style async task submission).
"""
from __future__ import annotations

import base64
import json
import logging
import os
import struct
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.api_key_pool import ApiKeyPool, load_env_from_project, mask_api_key
from agent_runner_v2.concurrent_api import ConcurrentApiRunner
from agent_runner_v2.workflow_packages.actions import action

logger = logging.getLogger(__name__)


def _extract_prompts_from_png(png_path: Path) -> dict[str, str]:
    """Extract t2i_prompt1 and t2i_prompt2 from PNG metadata."""
    prompts = {"t2i_prompt1": "", "t2i_prompt2": ""}
    try:
        with open(png_path, "rb") as f:
            data = f.read()
        pos = 8
        while pos < len(data):
            length = struct.unpack(">I", data[pos : pos + 4])[0]
            chunk_type = data[pos + 4 : pos + 8]
            if chunk_type == b"tEXt":
                chunk_data = data[pos + 8 : pos + 8 + length]
                null_pos = chunk_data.find(b"\x00")
                if null_pos != -1:
                    keyword = chunk_data[:null_pos].decode("latin-1")
                    text = chunk_data[null_pos + 1 :].decode("latin-1")
                    if keyword == "prompt":
                        workflow = json.loads(text)
                        for node_id, node_data in workflow.items():
                            if not isinstance(node_data, dict): continue
                            inputs = node_data.get("inputs", {})
                            meta = node_data.get("_meta", {})
                            title = meta.get("title", "")
                            if "t2i_prompt1" in title and "value" in inputs:
                                prompts["t2i_prompt1"] = inputs["value"]
                            if "t2i_prompt2" in title and "value" in inputs:
                                prompts["t2i_prompt2"] = inputs["value"]
                        break
            pos += 12 + length
    except (OSError, json.JSONDecodeError, struct.error) as exc:
        logger.warning("Failed to extract prompts from %s: %s", png_path.name, exc)
    return prompts


def _api_request_with_retry(method, url, *, headers, json_payload=None, timeout=500, max_retries=5, retry_base_wait=5):
    """Execute an HTTP request with retry logic for 503 and 429 responses."""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            if method.upper() == "GET":
                resp = requests.get(url, headers=headers, timeout=timeout)
            else:
                resp = requests.post(url, headers=headers, json=json_payload, timeout=timeout)

            if resp.status_code in (503, 429):
                wait_seconds = min(retry_base_wait * (2**attempt), 120)
                last_error = f"HTTP {resp.status_code} on attempt {attempt + 1}/{max_retries + 1}"
                logger.warning("HTTP %d from %s — attempt %d/%d, retrying in %ds", resp.status_code, url, attempt + 1, max_retries + 1, wait_seconds)
                time.sleep(wait_seconds)
                continue

            resp.raise_for_status()
            logger.debug("HTTP %s %s → %d", method, url, resp.status_code)
            return resp

        except requests.exceptions.Timeout:
            last_error = f"Timeout on attempt {attempt + 1}/{max_retries + 1}"
            if attempt < max_retries:
                wait_seconds = min(retry_base_wait * (2**attempt), 120)
                logger.warning("Timeout on %s — attempt %d/%d, retrying in %ds", url, attempt + 1, max_retries + 1, wait_seconds)
                time.sleep(wait_seconds)
                continue
            raise RuntimeError(f"Request timed out after {max_retries + 1} attempts") from None

    raise RuntimeError(f"Max retries ({max_retries}) exhausted. Last error: {last_error}")


def _write_index(index_path, step_name, file_mappings):
    """Write an index.json file listing input-to-output file mappings."""
    index_data = {"step": step_name, "files": file_mappings}
    index_path = Path(index_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)


@dataclass
class _VideoFromImageWorkItem:
    """Single video-from-image work item for concurrent processing."""
    png_path: Path
    t2i_prompt1: str
    video_submit_endpoint: str
    video_status_endpoint_fmt: str  # format string with task_id placeholder
    vid_model: str
    vid_resolution: str
    vid_ratio: str
    vid_duration: int
    api_timeout: int
    api_max_retries: int
    retry_base_wait: int
    process_delay: int
    step_04_dir: Path
    key_pool: ApiKeyPool


def _process_single_video_from_image(item: _VideoFromImageWorkItem) -> dict:
    """Worker function for concurrent video-from-image generation using HappyHorse (DashScope-style API)."""
    video_filename = item.png_path.stem + ".mp4"
    image_b64 = f"data:image/png;base64,{base64.b64encode(item.png_path.read_bytes()).decode('utf-8')}"

    # DashScope-style payload
    payload = {
        "model": item.vid_model,
        "input": {
            "prompt": item.t2i_prompt1,
            "media": [
                {"type": "first_frame", "url": image_b64}
            ]
        },
        "parameters": {
            "resolution": item.vid_resolution,
            "ratio": item.vid_ratio,
            "duration": item.vid_duration,
        }
    }

    logger.info("generate_videos_happyhorse: %s submitting video (model=%s, res=%s, ratio=%s, duration=%ds)",
                item.png_path.name, item.vid_model, item.vid_resolution, item.vid_ratio, item.vid_duration)

    if item.process_delay > 0:
        time.sleep(item.process_delay)

    api_key = item.key_pool.next_key()
    submit_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }

    submit_resp = _api_request_with_retry(
        "POST", item.video_submit_endpoint, headers=submit_headers, json_payload=payload,
        timeout=item.api_timeout, max_retries=item.api_max_retries, retry_base_wait=item.retry_base_wait,
    )
    submit_data = submit_resp.json()

    # DashScope response: {"output": {"task_id": "..."}}
    task_id = submit_data.get("output", {}).get("task_id", "")
    if not task_id:
        raise ValueError(f"{item.png_path.name}: no task_id in submit response: {submit_data}")

    logger.info("generate_videos_happyhorse: %s task_id=%s, polling for completion...", item.png_path.name, task_id)

    status_headers = {"Authorization": f"Bearer {api_key}"}
    status_url = item.video_status_endpoint_fmt.format(task_id=task_id)
    video_download_url = ""
    max_poll_attempts = 120
    poll_interval = 15

    for poll_attempt in range(max_poll_attempts):
        time.sleep(poll_interval)
        try:
            status_resp = requests.get(status_url, headers=status_headers, timeout=item.api_timeout)
            status_resp.raise_for_status()
            status_data = status_resp.json()
            task_status = status_data.get("output", {}).get("task_status", "")

            if task_status == "SUCCEEDED":
                output = status_data.get("output", {})
                video_download_url = output.get("video_url", "")
                if not video_download_url:
                    results = output.get("results", [{}])
                    if results:
                        video_download_url = results[0].get("url", "")
                if video_download_url:
                    break
                raise ValueError(f"{item.png_path.name}: SUCCEEDED but no video_url in response")
            elif task_status == "FAILED":
                raise RuntimeError(f"Video generation FAILED: {status_data}")
        except requests.exceptions.RequestException:
            if poll_attempt >= max_poll_attempts - 1:
                raise RuntimeError(f"Polling timed out after {max_poll_attempts} attempts")
            continue

    if not video_download_url:
        raise ValueError(f"{item.png_path.name}: no download URL after completion")

    vid_resp = requests.get(video_download_url, timeout=item.api_timeout)
    vid_resp.raise_for_status()

    vid_output_path = item.step_04_dir / video_filename
    with open(vid_output_path, "wb") as vid_f:
        vid_f.write(vid_resp.content)

    return {
        "video_filename": video_filename,
        "file_mapping": {"input": f"step_03_generatedimage/{item.png_path.name}", "output": f"step_04_generatedvideo/{video_filename}"},
    }


@action("generate_videos_happyhorse")
def generate_videos_happyhorse(*, context, state, step_cfg, project_root) -> ActionResult:
    """Generate videos using HappyHorse-1.1-i2v API (DashScope-style async)."""
    load_env_from_project(project_root)

    key_pool = ApiKeyPool("HAPPYHORSE_API_KEY", load_env=False)
    base_url = os.environ.get("HAPPYHORSE_BASE_URL", "https://dashscope.aliyuncs.com")

    step_03_dir = Path(context.get("STEP_03_DIR", ""))
    step_04_dir = Path(context.get("STEP_04_DIR", ""))
    config_path = Path(context.get("MEDIA_CONFIG", ""))

    if not step_03_dir.is_dir():
        return ActionResult(status="REJECTED", remark=f"Step 03 directory not found: {step_03_dir}", artifacts={}, reject_code="MISSING_INPUT_DIR")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return ActionResult(status="REJECTED", remark=f"Failed to load config: {exc}", artifacts={}, reject_code="CONFIG_LOAD_FAILED")

    vid_config = config.get("video", {})
    vid_model = vid_config.get("model", "happyhorse-1.1-i2v")
    vid_resolution = vid_config.get("resolution", "480P")
    vid_ratio = vid_config.get("ratio", "9:16")
    vid_duration = vid_config.get("duration", 15)
    vid_prompt_prefix = vid_config.get("video_prompt_prefix", "")
    vid_prompt_postfix = vid_config.get("video_prompt_postfix", "")

    process_delay = config.get("process_delay", 15)
    api_timeout = config.get("api_timeout", 500)
    api_max_retries = config.get("api_max_retries", 5)
    retry_base_wait = config.get("retry_base_wait", 5)
    max_concurrent = config.get("max_concurrent", 2)

    step_04_dir.mkdir(parents=True, exist_ok=True)
    png_files = sorted(step_03_dir.glob("*.png"))

    if not png_files:
        return ActionResult(status="REJECTED", remark="No PNG files found in step_03_generatedimage.", artifacts={}, reject_code="NO_INPUTS")

    # DashScope-style endpoints
    video_submit_endpoint = f"{base_url.rstrip('/')}/api/v1/services/aigc/video-generation/video-synthesis"
    video_status_endpoint_fmt = f"{base_url.rstrip('/')}/api/v1/tasks/{{task_id}}"

    work_items = []
    pre_failures = []

    for png_path in png_files:
        prompts = _extract_prompts_from_png(png_path)
        t2i_prompt1 = prompts["t2i_prompt1"]
        if not t2i_prompt1:
            pre_failures.append(f"{png_path.name}: no t2i_prompt1 in metadata")
            continue

        final_video_prompt = vid_prompt_prefix + t2i_prompt1 + vid_prompt_postfix

        work_items.append(_VideoFromImageWorkItem(
            png_path=png_path,
            t2i_prompt1=final_video_prompt,
            video_submit_endpoint=video_submit_endpoint,
            video_status_endpoint_fmt=video_status_endpoint_fmt,
            vid_model=vid_model,
            vid_resolution=vid_resolution,
            vid_ratio=vid_ratio,
            vid_duration=vid_duration,
            api_timeout=api_timeout,
            api_max_retries=api_max_retries,
            retry_base_wait=retry_base_wait,
            process_delay=process_delay,
            step_04_dir=step_04_dir,
            key_pool=key_pool,
        ))

    if not work_items:
        return ActionResult(status="REJECTED", remark="No work items to process. " + "; ".join(pre_failures), artifacts={}, reject_code="NO_INPUTS")

    runner = ConcurrentApiRunner(max_workers=max_concurrent)
    results = runner.run(work_items, _process_single_video_from_image, desc="generate_videos_happyhorse")

    successes = []
    failures = list(pre_failures)
    file_mappings = []

    for r in results:
        item = r.item
        if r.success:
            file_mappings.append(r.data["file_mapping"])
            successes.append(item.png_path.name)
        else:
            failures.append(f"{item.png_path.name}: {r.error}")

    index_path = step_04_dir / "index.json"
    _write_index(index_path, "generate_videos_happyhorse", file_mappings)

    total = len(png_files)
    success_count = len(successes)
    fail_count = len(failures)

    if fail_count == 0:
        return ActionResult(status="APPROVED", remark=f"Generated videos for {success_count}/{total} PNG files.", artifacts={"VIDEO_INDEX": str(index_path)})
    else:
        failure_detail = "; ".join(failures[:10])
        return ActionResult(status="REJECTED", remark=f"Partial failure: {success_count}/{total} succeeded. Errors: {failure_detail}", artifacts={"VIDEO_INDEX": str(index_path)}, reject_code="VIDEO_GEN_PARTIAL_FAILURE")
