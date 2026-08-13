"""Implementation actions for agnes_gen_video_v1.impls.agnes_v2.

Implements the generate_videos_agnes_v2 action using Agnes Video V2.0 API.
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
    negative_prompt: str
    video_submit_endpoint: str
    video_status_endpoint: str
    vid_model: str
    vid_width: int
    vid_height: int
    vid_num_frames: int
    vid_frame_rate: int
    api_timeout: int
    api_max_retries: int
    retry_base_wait: int
    process_delay: int
    step_04_dir: Path
    key_pool: ApiKeyPool


def _process_single_video_from_image(item: _VideoFromImageWorkItem) -> dict:
    """Worker function for concurrent video-from-image generation."""
    video_filename = item.png_path.stem + ".mp4"
    image_b64 = base64.b64encode(item.png_path.read_bytes()).decode("utf-8")

    payload = {
        "model": item.vid_model,
        "prompt": item.t2i_prompt1,
        "image": f"data:image/png;base64,{image_b64}",
        "width": item.vid_width,
        "height": item.vid_height,
        "num_frames": item.vid_num_frames,
        "frame_rate": item.vid_frame_rate,
    }
    if item.negative_prompt:
        payload["negative_prompt"] = item.negative_prompt

    logger.info("generate_videos_agnes_v2: %s submitting video (model=%s, %dx%d, frames=%d, fps=%d)",
                item.png_path.name, item.vid_model, item.vid_width, item.vid_height, item.vid_num_frames, item.vid_frame_rate)

    if item.process_delay > 0:
        time.sleep(item.process_delay)

    api_key = item.key_pool.next_key()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    submit_resp = _api_request_with_retry("POST", item.video_submit_endpoint, headers=headers, json_payload=payload,
                                          timeout=item.api_timeout, max_retries=item.api_max_retries, retry_base_wait=item.retry_base_wait)
    submit_data = submit_resp.json()

    video_id = submit_data.get("video_id", "") or submit_data.get("id", "")
    if not video_id:
        raise ValueError(f"{item.png_path.name}: no video_id in submit response")

    status_url = f"{item.video_status_endpoint}?video_id={video_id}"
    video_download_url = ""
    max_poll_attempts = 120
    poll_interval = 10

    for poll_attempt in range(max_poll_attempts):
        time.sleep(poll_interval)
        try:
            status_resp = requests.get(status_url, headers=headers, timeout=item.api_timeout)
            status_resp.raise_for_status()
            status_data = status_resp.json()
            vid_status = status_data.get("status", "")
            if vid_status == "completed":
                video_download_url = status_data.get("url", "") or status_data.get("video_url", "")
                break
            elif vid_status in ("failed", "error", "cancelled"):
                raise RuntimeError(f"Video generation failed with status: {vid_status}")
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


@action("generate_videos_agnes_v2")
def generate_videos_agnes_v2(*, context, state, step_cfg, project_root) -> ActionResult:
    """Generate videos using Agnes Video V2.0 API."""
    load_env_from_project(project_root)
    key_pool = ApiKeyPool("AGNES_API_KEY", load_env=False)
    base_url = os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com")
    
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
    vid_model = vid_config.get("model", "agnes-video-v2.0")
    vid_width = vid_config.get("width", 1024)
    vid_height = vid_config.get("height", 576)
    vid_num_frames = vid_config.get("num_frames", 72)
    vid_frame_rate = vid_config.get("frame_rate", 24)
    vid_prompt_prefix = vid_config.get("video_prompt_prefix", "")
    vid_prompt_postfix = vid_config.get("video_prompt_postfix", "")
    negative_prompt_video = vid_config.get("negative_prompt_video", "")
    negative_prompt_video_postfix = vid_config.get("negative_prompt_video_postfix", "")
    
    negative_prompt = negative_prompt_video
    if negative_prompt_video_postfix:
        negative_prompt = f"{negative_prompt} {negative_prompt_video_postfix}" if negative_prompt else negative_prompt_video_postfix

    process_delay = config.get("process_delay", 15)
    api_timeout = config.get("api_timeout", 500)
    api_max_retries = config.get("api_max_retries", 5)
    retry_base_wait = config.get("retry_base_wait", 5)
    max_concurrent = config.get("max_concurrent", 2)

    step_04_dir.mkdir(parents=True, exist_ok=True)
    png_files = sorted(step_03_dir.glob("*.png"))

    if not png_files:
        return ActionResult(status="REJECTED", remark="No PNG files found in step_03_generatedimage.", artifacts={}, reject_code="NO_INPUTS")

    video_submit_endpoint = f"{base_url.rstrip('/')}/v1/videos"
    video_status_endpoint = f"{base_url.rstrip('/')}/agnesapi"

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
            png_path=png_path, t2i_prompt1=final_video_prompt, negative_prompt=negative_prompt,
            video_submit_endpoint=video_submit_endpoint, video_status_endpoint=video_status_endpoint,
            vid_model=vid_model, vid_width=vid_width, vid_height=vid_height,
            vid_num_frames=vid_num_frames, vid_frame_rate=vid_frame_rate,
            api_timeout=api_timeout, api_max_retries=api_max_retries, retry_base_wait=retry_base_wait,
            process_delay=process_delay, step_04_dir=step_04_dir, key_pool=key_pool,
        ))

    if not work_items:
        return ActionResult(status="REJECTED", remark="No work items to process. " + "; ".join(pre_failures), artifacts={}, reject_code="NO_INPUTS")

    runner = ConcurrentApiRunner(max_workers=max_concurrent)
    results = runner.run(work_items, _process_single_video_from_image, desc="generate_videos_agnes_v2")

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
    _write_index(index_path, "generate_videos_agnes_v2", file_mappings)

    total = len(png_files)
    success_count = len(successes)
    fail_count = len(failures)

    if fail_count == 0:
        return ActionResult(status="APPROVED", remark=f"Generated videos for {success_count}/{total} PNG files.", artifacts={"VIDEO_INDEX": str(index_path)})
    else:
        failure_detail = "; ".join(failures[:10])
        return ActionResult(status="REJECTED", remark=f"Partial failure: {success_count}/{total} succeeded. Errors: {failure_detail}", artifacts={"VIDEO_INDEX": str(index_path)}, reject_code="VIDEO_GEN_PARTIAL_FAILURE")
