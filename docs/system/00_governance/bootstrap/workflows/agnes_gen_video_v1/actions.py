"""Custom actions for agnes_gen_video_v1 workflow.

This module provides the action function for generating videos from images
using the Agnes Video V2.0 API. The action:

- Scans step_03/ for PNG images
- Extracts t2i_prompt1 and t2i_prompt2 from PNG metadata (ComfyUI tEXt chunks)
- Calls the video generation API with t2i_prompt1 as the prompt
- Polls for completion and downloads videos to step_04/
- Produces an index.json manifest

The action implements retry logic for HTTP 503 responses with exponential
backoff, configurable timeouts, process delays between API calls, and
graceful partial failure handling.
"""
from __future__ import annotations

import base64
import json
import logging
import os
import struct
import time
from pathlib import Path

import requests

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.api_key_pool import ApiKeyPool, load_env_from_project, mask_api_key
from agent_runner_v2.workflow_packages.actions import action

logger = logging.getLogger(__name__)


def _extract_prompts_from_png(png_path: Path) -> dict[str, str]:
    """Extract t2i_prompt1 and t2i_prompt2 from PNG metadata.

    Parses the tEXt chunk with keyword 'prompt' containing ComfyUI
    workflow JSON. Searches node titles for prompt field names.

    Args:
        png_path: Path to the PNG file.

    Returns:
        Dictionary with 't2i_prompt1' and 't2i_prompt2' keys.
        Empty string if a prompt is not found.
    """
    prompts = {"t2i_prompt1": "", "t2i_prompt2": ""}

    try:
        with open(png_path, "rb") as f:
            data = f.read()

        pos = 8  # Skip PNG signature
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
                            if not isinstance(node_data, dict):
                                continue
                            inputs = node_data.get("inputs", {})
                            meta = node_data.get("_meta", {})
                            title = meta.get("title", "")

                            if "t2i_prompt1" in title and "value" in inputs:
                                prompts["t2i_prompt1"] = inputs["value"]
                            if "t2i_prompt2" in title and "value" in inputs:
                                prompts["t2i_prompt2"] = inputs["value"]

                        break  # Found the prompt chunk, stop searching

            pos += 12 + length

    except (OSError, json.JSONDecodeError, struct.error) as exc:
        logger.warning("Failed to extract prompts from %s: %s", png_path.name, exc)

    return prompts


def _api_request_with_retry(
    method,
    url,
    *,
    headers,
    json_payload=None,
    timeout=500,
    max_retries=5,
    retry_base_wait=5,
):
    """Execute an HTTP request with retry logic for 503 and 429 responses.

    Implements exponential backoff for HTTP 503 (Service Unavailable)
    and HTTP 429 (Too Many Requests) responses. Other error statuses
    are raised immediately.

    Args:
        method: HTTP method string ('GET' or 'POST').
        url: Full endpoint URL.
        headers: Dictionary of HTTP headers.
        json_payload: Dictionary payload for POST requests.
        timeout: HTTP request timeout in seconds.
        max_retries: Maximum number of retry attempts for 503/429 errors.

    Returns:
        requests.Response object on success.

    Raises:
        requests.HTTPError: For non-503/429 error responses.
        RuntimeError: If max retries are exhausted on 503/429 errors.
    """
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            if method.upper() == "GET":
                resp = requests.get(url, headers=headers, timeout=timeout)
            else:
                resp = requests.post(
                    url, headers=headers, json=json_payload, timeout=timeout
                )

            if resp.status_code in (503, 429):
                wait_seconds = min(retry_base_wait * (2**attempt), 120)
                last_error = f"HTTP {resp.status_code} on attempt {attempt + 1}/{max_retries + 1}"
                logger.warning(
                    "HTTP %d from %s — attempt %d/%d, retrying in %ds",
                    resp.status_code, url, attempt + 1, max_retries + 1, wait_seconds,
                )
                time.sleep(wait_seconds)
                continue

            resp.raise_for_status()
            logger.debug("HTTP %s %s → %d", method, url, resp.status_code)
            return resp

        except requests.exceptions.Timeout:
            last_error = f"Timeout on attempt {attempt + 1}/{max_retries + 1}"
            if attempt < max_retries:
                wait_seconds = min(retry_base_wait * (2**attempt), 120)
                logger.warning(
                    "Timeout on %s — attempt %d/%d, retrying in %ds",
                    url, attempt + 1, max_retries + 1, wait_seconds,
                )
                time.sleep(wait_seconds)
                continue
            raise RuntimeError(f"Request timed out after {max_retries + 1} attempts") from None

    raise RuntimeError(f"Max retries ({max_retries}) exhausted. Last error: {last_error}")


def _write_index(index_path, step_name, file_mappings):
    """Write an index.json file listing input-to-output file mappings.

    Args:
        index_path: Absolute path for the index.json output file.
        step_name: Name of the step producing the index.
        file_mappings: List of dictionaries with 'input' and 'output' keys.
    """
    index_data = {"step": step_name, "files": file_mappings}
    index_path = Path(index_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)


@action("generate_videos_from_images")
def generate_videos_from_images(
    *, context, state, step_cfg, project_root
) -> ActionResult:
    """Generate videos from images using Agnes Video V2.0 API.

    Scans step_03/ for PNG images, extracts t2i_prompt1 and t2i_prompt2
    from PNG metadata (ComfyUI tEXt chunks), calls the video generation
    API with t2i_prompt1 as the prompt, polls for completion, downloads
    videos to step_04/, and produces an index.json manifest.

    Configuration is read from config.json (MEDIA_CONFIG context variable).
    API credentials are loaded from .env (AGNES_API_KEY, AGNES_BASE_URL).

    On partial failure (some videos succeed, some fail), successfully
    processed files are saved and the action returns REJECTED with a
    detailed error remark listing successes and failures.

    Args:
        context: Prompt context dictionary with resolved paths.
        state: Workflow state dictionary with artifacts and job metadata.
        step_cfg: Step configuration dictionary from workflow.toml.
        project_root: Root path of the target repository.

    Returns:
        ActionResult with APPROVED on full success, REJECTED on any failure.
    """
    # Load .env and create API key pool for round-robin rotation
    load_env_from_project(project_root)
    key_pool = ApiKeyPool("AGNES_API_KEY", load_env=False)
    base_url = os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com")
    logger.info(
        "generate_videos_from_images: starting (base_url=%s, keys=%d)",
        base_url, len(key_pool),
    )
    if not key_pool:
        return ActionResult(
            status="REJECTED",
            remark="AGNES_API_KEY not found in environment.",
            artifacts={},
            reject_code="MISSING_API_KEY",
        )

    # Resolve paths from context
    step_03_dir = Path(context.get("STEP_03_DIR", ""))
    step_04_dir = Path(context.get("STEP_04_DIR", ""))
    config_path = Path(context.get("MEDIA_CONFIG", ""))
    logger.debug(
        "generate_videos_from_images: paths — step_03=%s, step_04=%s, config=%s",
        step_03_dir, step_04_dir, config_path,
    )

    # Validate paths
    if not step_03_dir.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"Step 03 directory not found: {step_03_dir}",
            artifacts={},
            reject_code="MISSING_INPUT_DIR",
        )

    # Load configuration
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to load config: {exc}",
            artifacts={},
            reject_code="CONFIG_LOAD_FAILED",
        )

    vid_config = config.get("video", {})
    vid_model = vid_config.get("model", "agnes-video-v2.0")
    vid_width = vid_config.get("width", 1024)
    vid_height = vid_config.get("height", 576)
    vid_num_frames = vid_config.get("num_frames", 72)
    vid_frame_rate = vid_config.get("frame_rate", 24)
    process_delay = config.get("process_delay", 15)
    api_timeout = config.get("api_timeout", 500)
    api_max_retries = config.get("api_max_retries", 5)
    retry_base_wait = config.get("retry_base_wait", 5)
    logger.info(
        "generate_videos_from_images: config — model=%s, %dx%d, "
        "frames=%d, fps=%d, delay=%ds, timeout=%ds, "
        "max_retries=%d, retry_base_wait=%ds",
        vid_model, vid_width, vid_height, vid_num_frames,
        vid_frame_rate, process_delay, api_timeout,
        api_max_retries, retry_base_wait,
    )

    # Prepare output directory
    step_04_dir.mkdir(parents=True, exist_ok=True)

    # Scan for PNG files in step_03 (skip non-image files)
    png_files = sorted(step_03_dir.glob("*.png"))
    logger.info(
        "generate_videos_from_images: found %d PNG file(s) in %s",
        len(png_files), step_03_dir,
    )
    if not png_files:
        return ActionResult(
            status="REJECTED",
            remark="No PNG files found in step_03.",
            artifacts={},
            reject_code="NO_INPUTS",
        )

    # API endpoints
    video_submit_endpoint = f"{base_url.rstrip('/')}/v1/videos"
    video_status_endpoint = f"{base_url.rstrip('/')}/agnesapi"

    successes = []
    failures = []
    file_mappings = []

    for png_path in png_files:
        logger.info(
            "generate_videos_from_images: processing %s", png_path.name
        )

        # Extract prompts from PNG metadata
        prompts = _extract_prompts_from_png(png_path)
        t2i_prompt1 = prompts["t2i_prompt1"]
        t2i_prompt2 = prompts["t2i_prompt2"]

        if not t2i_prompt1:
            logger.warning(
                "generate_videos_from_images: %s has no t2i_prompt1 in metadata",
                png_path.name,
            )
            failures.append(f"{png_path.name}: no t2i_prompt1 in metadata")
            continue

        logger.info(
            "generate_videos_from_images: %s extracted prompts "
            "(t2i_prompt1=%d chars, t2i_prompt2=%d chars)",
            png_path.name, len(t2i_prompt1), len(t2i_prompt2),
        )

        # Determine output filename
        video_filename = png_path.stem + ".mp4"
        vid_output_path = step_04_dir / video_filename

        # Base64-encode image for API (expects data URI, not local path)
        image_b64 = base64.b64encode(png_path.read_bytes()).decode("utf-8")

        # Submit video generation request
        payload = {
            "model": vid_model,
            "prompt": t2i_prompt1,
            "image": f"data:image/png;base64,{image_b64}",
            "width": vid_width,
            "height": vid_height,
            "num_frames": vid_num_frames,
            "frame_rate": vid_frame_rate,
        }
        logger.info(
            "generate_videos_from_images: %s submitting video "
            "(model=%s, %dx%d, frames=%d, fps=%d)",
            png_path.name, vid_model, vid_width, vid_height,
            vid_num_frames, vid_frame_rate,
        )

        try:
            # Get next API key from rotation pool
            api_key = key_pool.next_key()
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            logger.info(
                "generate_videos_from_images: %s using key %s (index %d)",
                png_path.name, mask_api_key(api_key), key_pool.current_index(),
            )

            submit_resp = _api_request_with_retry(
                "POST",
                video_submit_endpoint,
                headers=headers,
                json_payload=payload,
                timeout=api_timeout,
                max_retries=api_max_retries,
                retry_base_wait=retry_base_wait,
            )
            submit_data = submit_resp.json()

            # Extract video ID from response
            video_id = submit_data.get("video_id", "")
            if not video_id:
                video_id = submit_data.get("id", "")
            if not video_id:
                logger.warning(
                    "generate_videos_from_images: %s no video_id in submit response",
                    png_path.name,
                )
                failures.append(f"{png_path.name}: no video_id in submit response")
                continue

            logger.info(
                "generate_videos_from_images: %s submitted — video_id=%s",
                png_path.name, video_id,
            )

            # Poll for video completion
            status_url = f"{video_status_endpoint}?video_id={video_id}"
            video_download_url = ""
            max_poll_attempts = 120
            poll_interval = 10
            logger.info(
                "generate_videos_from_images: %s polling %s "
                "(interval=%ds, max=%d)",
                png_path.name, video_id, poll_interval, max_poll_attempts,
            )

            for poll_attempt in range(max_poll_attempts):
                time.sleep(poll_interval)

                try:
                    status_resp = requests.get(
                        status_url, headers=headers, timeout=api_timeout
                    )
                    status_resp.raise_for_status()
                    status_data = status_resp.json()

                    vid_status = status_data.get("status", "")
                    logger.debug(
                        "generate_videos_from_images: poll %d/%d — "
                        "video_id=%s status=%s",
                        poll_attempt + 1, max_poll_attempts, video_id, vid_status,
                    )

                    if vid_status == "completed":
                        video_download_url = status_data.get("url", "")
                        if not video_download_url:
                            video_download_url = status_data.get("video_url", "")
                        logger.info(
                            "generate_videos_from_images: video_id=%s "
                            "completed after %d poll(s)",
                            video_id, poll_attempt + 1,
                        )
                        break
                    elif vid_status in ("failed", "error", "cancelled"):
                        raise RuntimeError(
                            f"Video generation failed with status: {vid_status}"
                        )
                except requests.exceptions.RequestException:
                    if poll_attempt >= max_poll_attempts - 1:
                        raise RuntimeError(
                            f"Polling timed out after {max_poll_attempts} attempts"
                        )
                    continue

            if not video_download_url:
                logger.warning(
                    "generate_videos_from_images: %s no download URL after completion",
                    png_path.name,
                )
                failures.append(f"{png_path.name}: no download URL after completion")
                continue

            # Download the completed video
            vid_resp = requests.get(video_download_url, timeout=api_timeout)
            vid_resp.raise_for_status()

            with open(vid_output_path, "wb") as vid_f:
                vid_f.write(vid_resp.content)
            logger.info(
                "generate_videos_from_images: %s saved %s (%d bytes)",
                png_path.name, video_filename, len(vid_resp.content),
            )

            file_mappings.append({
                "input": f"step_03/{png_path.name}",
                "output": f"step_04/{video_filename}",
            })
            successes.append(png_path.name)

            # Process delay before next API call
            if png_files.index(png_path) < len(png_files) - 1:
                logger.debug(
                    "generate_videos_from_images: process delay %ds before next API call",
                    process_delay,
                )
                time.sleep(process_delay)

        except Exception as exc:
            logger.error(
                "generate_videos_from_images: %s API error: %s",
                png_path.name, exc,
            )
            failures.append(f"{png_path.name}: API error - {exc}")

    # Write index.json to step_04
    index_path = step_04_dir / "index.json"
    _write_index(index_path, "generate_videos_from_images", file_mappings)

    # Build result
    total = len(png_files)
    success_count = len(successes)
    fail_count = len(failures)
    logger.info(
        "generate_videos_from_images: complete — %d/%d succeeded, %d error(s)",
        success_count, total, fail_count,
    )

    if fail_count == 0:
        return ActionResult(
            status="APPROVED",
            remark=(
                f"Generated videos for {success_count}/{total} "
                f"PNG files. Index written to step_04/index.json."
            ),
            artifacts={
                "VIDEO_INDEX": str(index_path),
            },
        )
    else:
        failure_detail = "; ".join(failures[:10])
        if len(failures) > 10:
            failure_detail += f" ... and {len(failures) - 10} more"
        return ActionResult(
            status="REJECTED",
            remark=(
                f"Partial failure: {success_count}/{total} PNG "
                f"files succeeded, {fail_count} errors. "
                f"Details: {failure_detail}. "
                f"Partial results saved to step_04/."
            ),
            artifacts={
                "VIDEO_INDEX": str(index_path),
            },
            reject_code="VIDEO_GEN_PARTIAL_FAILURE",
        )
