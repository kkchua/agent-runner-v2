"""Custom actions for agnes_media_gen_v1 workflow.

This module provides the action functions for the Agnes Media Generation v1
workflow. Two custom actions are defined:

- generate_images: Calls the Agnes Image 2.1 Flash API to produce images
  from prompt variants, downloads them to step_03/, and updates JSON files
  with image_url fields.
- generate_videos: Calls the Agnes Video V2.0 API to produce image-to-video
  animations, polls for completion, and downloads videos to step_04/.

Both actions implement retry logic for HTTP 503 responses with exponential
backoff, configurable timeouts, process delays between API calls, and
graceful partial failure handling.
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

import requests

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.api_key_pool import ApiKeyPool, load_env_from_project, mask_api_key
from agent_runner_v2.workflow_packages.actions import action

logger = logging.getLogger(__name__)


def _load_config(config_path):
    """Load and parse the media configuration JSON file.

    Args:
        config_path: Absolute path to config.json.

    Returns:
        Dictionary of configuration values.

    Raises:
        FileNotFoundError: If the config file does not exist.
        json.JSONDecodeError: If the config file is not valid JSON.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Media config not found: {config_path}"
        )
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


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
                resp = requests.get(
                    url, headers=headers, timeout=timeout
                )
            else:
                resp = requests.post(
                    url,
                    headers=headers,
                    json=json_payload,
                    timeout=timeout,
                )

            if resp.status_code in (503, 429):
                wait_seconds = min(retry_base_wait * (2 ** attempt), 120)
                last_error = (
                    f"HTTP {resp.status_code} on attempt {attempt + 1}/"
                    f"{max_retries + 1}"
                )
                logger.warning(
                    "HTTP %d from %s — attempt %d/%d, "
                    "retrying in %ds",
                    resp.status_code, url, attempt + 1, max_retries + 1,
                    wait_seconds,
                )
                time.sleep(wait_seconds)
                continue

            resp.raise_for_status()
            logger.debug(
                "HTTP %s %s → %d", method, url, resp.status_code,
            )
            return resp

        except requests.exceptions.Timeout:
            last_error = (
                f"Timeout on attempt {attempt + 1}/"
                f"{max_retries + 1}"
            )
            if attempt < max_retries:
                wait_seconds = min(retry_base_wait * (2 ** attempt), 120)
                logger.warning(
                    "Timeout on %s — attempt %d/%d, "
                    "retrying in %ds",
                    url, attempt + 1, max_retries + 1,
                    wait_seconds,
                )
                time.sleep(wait_seconds)
                continue
            raise RuntimeError(
                f"Request timed out after {max_retries + 1} attempts"
            ) from None

    raise RuntimeError(
        f"Max retries ({max_retries}) exhausted. Last error: {last_error}"
    )


def _write_index(index_path, step_name, file_mappings):
    """Write an index.json file listing input-to-output file mappings.

    Args:
        index_path: Absolute path for the index.json output file.
        step_name: Name of the step producing the index.
        file_mappings: List of dictionaries with 'input' and 'output' keys.
    """
    index_data = {
        "step": step_name,
        "files": file_mappings,
    }
    index_path = Path(index_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)


@action("generate_images")
def generate_images(*, context, state, step_cfg, project_root) -> ActionResult:
    """Generate images from prompt variants using Agnes Image 2.1 Flash API.

    Scans step_02/ for variant JSON files, calls the image generation API
    for each variant, downloads generated images to step_03/, updates the
    JSON files with image_url fields, archives processed inputs, and
    produces an index.json manifest.

    Configuration is read from config.json (MEDIA_CONFIG context variable).
    API credentials are loaded from .env (AGNES_API_KEY, AGNES_BASE_URL).

    On partial failure (some images succeed, some fail), successfully
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
    base_url = os.environ.get(
        "AGNES_BASE_URL", "https://apihub.agnes-ai.com"
    )
    logger.info(
        "generate_images: starting (base_url=%s, keys=%d)",
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
    step_02_dir = Path(context.get("STEP_02_DIR", ""))
    step_03_dir = Path(context.get("STEP_03_DIR", ""))
    config_path = Path(context.get("MEDIA_CONFIG", ""))
    logger.info(
        "generate_images1: MEDIA_CONFIG=%r, config_path=%r",
        context.get("MEDIA_CONFIG", "<MISSING>"),
        config_path,
    )
    logger.debug(
        "generate_images: paths — step_02=%s, step_03=%s, config=%s",
        step_02_dir, step_03_dir, config_path,
    )

    # Validate paths
    if not step_02_dir.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"Step 02 directory not found: {step_02_dir}",
            artifacts={},
            reject_code="MISSING_INPUT_DIR",
        )

    # Load configuration
    try:
        config = _load_config(config_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to load config: {exc}",
            artifacts={},
            reject_code="CONFIG_LOAD_FAILED",
        )

    img_config = config.get("image", {})
    img_model = img_config.get("model", "agnes-image-2.1-flash")
    img_size = img_config.get("size", "1024x1024")
    process_delay = config.get("process_delay", 15)
    api_timeout = config.get("api_timeout", 500)
    api_max_retries = config.get("api_max_retries", 5)
    retry_base_wait = config.get("retry_base_wait", 5)
    logger.info(
        "generate_images: config — model=%s, size=%s, "
        "delay=%ds, timeout=%ds, max_retries=%d, retry_base_wait=%ds",
        img_model, img_size, process_delay,
        api_timeout, api_max_retries, retry_base_wait,
    )

    # Prepare output directory
    step_03_dir.mkdir(parents=True, exist_ok=True)

    # Scan for variant JSON files in step_02 (skip index.json)
    variant_jsons = sorted(
        p for p in step_02_dir.glob("*.json")
        if p.name != "index.json"
    )
    logger.info(
        "generate_images: found %d variant JSON(s) in %s",
        len(variant_jsons), step_02_dir,
    )
    if not variant_jsons:
        return ActionResult(
            status="REJECTED",
            remark="No variant JSON files found in step_02.",
            artifacts={},
            reject_code="NO_INPUTS",
        )

    # API endpoint
    image_endpoint = f"{base_url.rstrip('/')}/v1/images/generations"

    successes = []
    failures = []
    file_mappings = []

    for variant_json_path in variant_jsons:
        logger.info(
            "generate_images: processing %s", variant_json_path.name,
        )
        try:
            with open(variant_json_path, "r", encoding="utf-8") as f:
                variant_data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error(
                "generate_images: failed to read %s: %s",
                variant_json_path.name, exc,
            )
            failures.append(
                f"{variant_json_path.name}: read error - {exc}"
            )
            continue

        variations = variant_data.get("variations", [])
        logger.info(
            "generate_images: %s has %d variation(s)",
            variant_json_path.name, len(variations),
        )
        if not variations:
            failures.append(
                f"{variant_json_path.name}: no variations found"
            )
            continue

        updated_variations = []
        variant_success = True

        for var_idx, variation in enumerate(variations):
            # Process delay before each API call
            if var_idx > 0 or variant_jsons.index(variant_json_path) > 0:
                logger.debug(
                    "generate_images: process delay %ds before API call",
                    process_delay,
                )
                time.sleep(process_delay)

            t2i_prompt = variation.get("t2i_prompt1", "")
            image_filename = variation.get("image_filename", "")

            if not t2i_prompt:
                logger.warning(
                    "generate_images: %s[%d] empty t2i_prompt1",
                    variant_json_path.name, var_idx,
                )
                failures.append(
                    f"{variant_json_path.name}[{var_idx}]: "
                    f"empty t2i_prompt1"
                )
                variant_success = False
                continue

            payload = {
                "model": img_model,
                "prompt": t2i_prompt,
                "size": img_size,
            }
            logger.info(
                "generate_images: %s[%d] requesting image "
                "(model=%s, size=%s, prompt=%.80s...)",
                variant_json_path.name, var_idx,
                img_model, img_size, t2i_prompt,
            )

            try:
                # Get next API key from rotation pool
                api_key = key_pool.next_key()
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                logger.info(
                    "generate_images: %s[%d] using key %s (index %d)",
                    variant_json_path.name, var_idx,
                    mask_api_key(api_key),
                    key_pool.current_index(),
                )

                resp = _api_request_with_retry(
                    "POST",
                    image_endpoint,
                    headers=headers,
                    json_payload=payload,
                    timeout=api_timeout,
                    max_retries=api_max_retries,
                    retry_base_wait=retry_base_wait,
                )
                resp_data = resp.json()

                # Extract image URL from response
                image_url = ""
                data_array = resp_data.get("data", [])
                if data_array:
                    image_url = data_array[0].get("url", "")

                if not image_url:
                    logger.warning(
                        "generate_images: %s[%d] no image URL "
                        "in API response",
                        variant_json_path.name, var_idx,
                    )
                    failures.append(
                        f"{variant_json_path.name}[{var_idx}]: "
                        f"no image URL in API response"
                    )
                    variant_success = False
                    continue

                # Download the generated image
                img_resp = requests.get(
                    image_url, timeout=api_timeout
                )
                img_resp.raise_for_status()

                # Determine output filename
                if not image_filename:
                    stem = variant_json_path.stem
                    image_filename = f"{stem}_{var_idx + 1:02d}.png"

                img_output_path = step_03_dir / image_filename
                with open(img_output_path, "wb") as img_f:
                    img_f.write(img_resp.content)
                logger.info(
                    "generate_images: %s[%d] saved %s (%d bytes)",
                    variant_json_path.name, var_idx,
                    image_filename, len(img_resp.content),
                )

                # Update variation with image_url
                updated_var = dict(variation)
                updated_var["image_url"] = image_url
                updated_variations.append(updated_var)

                file_mappings.append({
                    "input": f"step_02/{variant_json_path.name}",
                    "output": f"step_03/{image_filename}",
                    "updated_json": f"step_03/{variant_json_path.name}",
                })

                # Write updated JSON immediately after each image
                updated_data = dict(variant_data)
                updated_data["variations"] = updated_variations
                updated_json_path = step_03_dir / variant_json_path.name
                with open(updated_json_path, "w", encoding="utf-8") as f:
                    json.dump(
                        updated_data, f, indent=2, ensure_ascii=False
                    )
                logger.info(
                    "generate_images: %s[%d] updated JSON %s "
                    "(%d variation(s) so far)",
                    variant_json_path.name, var_idx,
                    updated_json_path.name, len(updated_variations),
                )

            except Exception as exc:
                logger.error(
                    "generate_images: %s[%d] API error: %s",
                    variant_json_path.name, var_idx, exc,
                )
                failures.append(
                    f"{variant_json_path.name}[{var_idx}]: "
                    f"API error - {exc}"
                )
                variant_success = False

        if variant_success:
            successes.append(variant_json_path.name)

    # Write index.json to step_03
    index_path = step_03_dir / "index.json"
    _write_index(index_path, "generate_images", file_mappings)

    # Build result
    total = len(variant_jsons)
    success_count = len(successes)
    fail_count = len(failures)
    logger.info(
        "generate_images: complete — %d/%d succeeded, %d error(s)",
        success_count, total, fail_count,
    )

    if fail_count == 0:
        return ActionResult(
            status="APPROVED",
            remark=(
                f"Generated images for {success_count}/{total} "
                f"variant files. Index written to step_03/index.json."
            ),
            artifacts={
                "IMAGE_INDEX": str(index_path),
            },
        )
    else:
        failure_detail = "; ".join(failures[:10])
        if len(failures) > 10:
            failure_detail += f" ... and {len(failures) - 10} more"
        return ActionResult(
            status="REJECTED",
            remark=(
                f"Partial failure: {success_count}/{total} variant "
                f"files succeeded, {fail_count} errors. "
                f"Details: {failure_detail}. "
                f"Partial results saved to step_03/."
            ),
            artifacts={
                "IMAGE_INDEX": str(index_path),
            },
            reject_code="IMAGE_GEN_PARTIAL_FAILURE",
        )


@action("generate_videos")
def generate_videos(*, context, state, step_cfg, project_root):
    """Generate videos from images using Agnes Video V2.0 API.

    Scans step_03/ for updated JSON files containing image_url and
    t2i_prompt1 fields. For each variant, submits a video generation
    request, polls the status endpoint until completion, downloads
    the video to step_04/, archives processed inputs, and produces
    an index.json manifest.

    Configuration is read from config.json (MEDIA_CONFIG context variable).
    API credentials are loaded from .env (AGNES_API_KEY, AGNES_BASE_URL).

    On partial failure, successfully processed files are saved and the
    action returns REJECTED with a detailed error remark.

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
    base_url = os.environ.get(
        "AGNES_BASE_URL", "https://apihub.agnes-ai.com"
    )
    logger.info(
        "generate_videos: starting (base_url=%s, keys=%d)",
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
        "generate_videos: paths — step_03=%s, step_04=%s, config=%s",
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
        config = _load_config(config_path)
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
    vid_prompt_field = vid_config.get("video_prompt", "t2v_prompt1")
    vid_prompt_prefix = vid_config.get("video_prompt_prefix", "")
    vid_prompt_postfix = vid_config.get("video_prompt_postfix", "")
    process_delay = config.get("process_delay", 15)
    api_timeout = config.get("api_timeout", 500)
    api_max_retries = config.get("api_max_retries", 5)
    retry_base_wait = config.get("retry_base_wait", 5)
    logger.info(
        "generate_videos: config — model=%s, %dx%d, "
        "frames=%d, fps=%d, delay=%ds, timeout=%ds, "
        "max_retries=%d, retry_base_wait=%ds, video_prompt_field=%s",
        vid_model, vid_width, vid_height, vid_num_frames,
        vid_frame_rate, process_delay, api_timeout,
        api_max_retries, retry_base_wait, vid_prompt_field,
    )

    # Prepare output directory
    step_04_dir.mkdir(parents=True, exist_ok=True)

    # Scan for JSON files in step_03 (skip index.json)
    variant_jsons = sorted(
        p for p in step_03_dir.glob("*.json")
        if p.name != "index.json"
    )
    logger.info(
        "generate_videos: found %d variant JSON(s) in %s",
        len(variant_jsons), step_03_dir,
    )
    if not variant_jsons:
        return ActionResult(
            status="REJECTED",
            remark="No variant JSON files found in step_03.",
            artifacts={},
            reject_code="NO_INPUTS",
        )

    # API endpoints
    video_submit_endpoint = f"{base_url.rstrip('/')}/v1/videos"
    video_status_endpoint = f"{base_url.rstrip('/')}/agnesapi"

    successes = []
    failures = []
    file_mappings = []

    for variant_json_path in variant_jsons:
        logger.info(
            "generate_videos: processing %s",
            variant_json_path.name,
        )
        try:
            with open(variant_json_path, "r", encoding="utf-8") as f:
                variant_data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error(
                "generate_videos: failed to read %s: %s",
                variant_json_path.name, exc,
            )
            failures.append(
                f"{variant_json_path.name}: read error - {exc}"
            )
            continue

        variations = variant_data.get("variations", [])
        logger.info(
            "generate_videos: %s has %d variation(s)",
            variant_json_path.name, len(variations),
        )
        if not variations:
            failures.append(
                f"{variant_json_path.name}: no variations found"
            )
            continue

        file_success = True

        for var_idx, variation in enumerate(variations):
            # Process delay before each API call
            if var_idx > 0 or variant_jsons.index(variant_json_path) > 0:
                logger.debug(
                    "generate_videos: process delay %ds before API call",
                    process_delay,
                )
                time.sleep(process_delay)

            # Resolve video prompt: use configured field, fallback to t2i_prompt1
            video_prompt = variation.get(vid_prompt_field, "")
            if not video_prompt:
                video_prompt = variation.get("t2i_prompt1", "")
            image_url = variation.get("image_url", "")

            if not video_prompt or not image_url:
                logger.warning(
                    "generate_videos: %s[%d] missing "
                    "%s/image_url",
                    variant_json_path.name, var_idx,
                    vid_prompt_field,
                )
                failures.append(
                    f"{variant_json_path.name}[{var_idx}]: "
                    f"missing {vid_prompt_field}/image_url"
                )
                file_success = False
                continue

            # Construct final video prompt with prefix/postfix
            final_video_prompt = vid_prompt_prefix + video_prompt + vid_prompt_postfix

            # Submit video generation request
            payload = {
                "model": vid_model,
                "prompt": final_video_prompt,
                "image": image_url,
                "width": vid_width,
                "height": vid_height,
                "num_frames": vid_num_frames,
                "frame_rate": vid_frame_rate,
            }
            logger.info(
                "generate_videos: %s[%d] submitting video "
                "(model=%s, %dx%d, frames=%d, fps=%d)",
                variant_json_path.name, var_idx,
                vid_model, vid_width, vid_height,
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
                    "generate_videos: %s[%d] using key %s (index %d)",
                    variant_json_path.name, var_idx,
                    mask_api_key(api_key),
                    key_pool.current_index(),
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
                        "generate_videos: %s[%d] no video_id "
                        "in submit response",
                        variant_json_path.name, var_idx,
                    )
                    failures.append(
                        f"{variant_json_path.name}[{var_idx}]: "
                        f"no video_id in submit response"
                    )
                    file_success = False
                    continue

                logger.info(
                    "generate_videos: %s[%d] submitted — "
                    "video_id=%s",
                    variant_json_path.name, var_idx, video_id,
                )

                # Poll for video completion
                status_url = (
                    f"{video_status_endpoint}?video_id={video_id}"
                )
                video_download_url = ""
                max_poll_attempts = 120
                poll_interval = 10
                logger.info(
                    "generate_videos: %s[%d] polling %s "
                    "(interval=%ds, max=%d)",
                    variant_json_path.name, var_idx,
                    video_id, poll_interval, max_poll_attempts,
                )

                for poll_attempt in range(max_poll_attempts):
                    time.sleep(poll_interval)

                    try:
                        status_resp = requests.get(
                            status_url,
                            headers=headers,
                            timeout=api_timeout,
                        )
                        status_resp.raise_for_status()
                        status_data = status_resp.json()

                        vid_status = status_data.get(
                            "status", ""
                        )
                        logger.debug(
                            "generate_videos: poll %d/%d — "
                            "video_id=%s status=%s",
                            poll_attempt + 1,
                            max_poll_attempts,
                            video_id, vid_status,
                        )

                        if vid_status == "completed":
                            video_download_url = status_data.get(
                                "url", ""
                            )
                            if not video_download_url:
                                video_download_url = (
                                    status_data.get(
                                        "video_url", ""
                                    )
                                )
                            logger.info(
                                "generate_videos: video_id=%s "
                                "completed after %d poll(s)",
                                video_id, poll_attempt + 1,
                            )
                            break
                        elif vid_status in (
                            "failed", "error", "cancelled"
                        ):
                            raise RuntimeError(
                                f"Video generation failed with "
                                f"status: {vid_status}"
                            )
                    except requests.exceptions.RequestException:
                        if poll_attempt >= max_poll_attempts - 1:
                            raise RuntimeError(
                                "Polling timed out after "
                                f"{max_poll_attempts} attempts"
                            )
                        continue

                if not video_download_url:
                    logger.warning(
                        "generate_videos: %s[%d] no download "
                        "URL after completion",
                        variant_json_path.name, var_idx,
                    )
                    failures.append(
                        f"{variant_json_path.name}[{var_idx}]: "
                        f"no download URL after completion"
                    )
                    file_success = False
                    continue

                # Download the completed video
                vid_resp = requests.get(
                    video_download_url, timeout=api_timeout
                )
                vid_resp.raise_for_status()

                # Determine output filename
                image_filename = variation.get(
                    "image_filename", ""
                )
                if image_filename:
                    video_filename = (
                        Path(image_filename).stem + ".mp4"
                    )
                else:
                    stem = variant_json_path.stem
                    video_filename = (
                        f"{stem}_{var_idx + 1:02d}.mp4"
                    )

                vid_output_path = step_04_dir / video_filename
                with open(vid_output_path, "wb") as vid_f:
                    vid_f.write(vid_resp.content)
                logger.info(
                    "generate_videos: %s[%d] saved %s "
                    "(%d bytes)",
                    variant_json_path.name, var_idx,
                    video_filename, len(vid_resp.content),
                )

                file_mappings.append({
                    "input": (
                        f"step_03/{image_filename}"
                        if image_filename
                        else f"step_03/{variant_json_path.name}"
                    ),
                    "output": f"step_04/{video_filename}",
                })

            except Exception as exc:
                logger.error(
                    "generate_videos: %s[%d] API error: %s",
                    variant_json_path.name, var_idx, exc,
                )
                failures.append(
                    f"{variant_json_path.name}[{var_idx}]: "
                    f"API error - {exc}"
                )
                file_success = False

        if file_success:
            successes.append(variant_json_path.name)

    # Write index.json to step_04
    index_path = step_04_dir / "index.json"
    _write_index(index_path, "generate_videos", file_mappings)

    # Build result
    total = len(variant_jsons)
    success_count = len(successes)
    fail_count = len(failures)
    logger.info(
        "generate_videos: complete — %d/%d succeeded, "
        "%d error(s)",
        success_count, total, fail_count,
    )

    if fail_count == 0:
        return ActionResult(
            status="APPROVED",
            remark=(
                f"Generated videos for {success_count}/{total} "
                f"variant files. Index written to "
                f"step_04/index.json."
            ),
            artifacts={
                "VIDEO_INDEX": str(index_path),
            },
        )
    else:
        failure_detail = "; ".join(failures[:10])
        if len(failures) > 10:
            failure_detail += (
                f" ... and {len(failures) - 10} more"
            )
        return ActionResult(
            status="REJECTED",
            remark=(
                f"Partial failure: {success_count}/{total} "
                f"variant files succeeded, {fail_count} errors. "
                f"Details: {failure_detail}. "
                f"Partial results saved to step_04/."
            ),
            artifacts={
                "VIDEO_INDEX": str(index_path),
            },
            reject_code="VIDEO_GEN_PARTIAL_FAILURE",
        )
