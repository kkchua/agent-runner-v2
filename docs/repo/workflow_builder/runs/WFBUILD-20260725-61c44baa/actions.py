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
import os
import shutil
import time
from pathlib import Path

import requests

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


def _load_env():
    """Load environment variables from .env file.

    Searches for .env in the current working directory and parent
    directories. Sets AGNES_API_KEY and AGNES_BASE_URL into the
    process environment if found.
    """
    from dotenv import load_dotenv

    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()


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
):
    """Execute an HTTP request with retry logic for 503 responses.

    Implements exponential backoff for HTTP 503 (Service Unavailable)
    responses. Other error statuses are raised immediately.

    Args:
        method: HTTP method string ('GET' or 'POST').
        url: Full endpoint URL.
        headers: Dictionary of HTTP headers.
        json_payload: Dictionary payload for POST requests.
        timeout: HTTP request timeout in seconds.
        max_retries: Maximum number of retry attempts for 503 errors.

    Returns:
        requests.Response object on success.

    Raises:
        requests.HTTPError: For non-503 error responses.
        RuntimeError: If max retries are exhausted on 503 errors.
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

            if resp.status_code == 503:
                wait_seconds = min(2 ** attempt * 5, 120)
                last_error = (
                    f"HTTP 503 on attempt {attempt + 1}/"
                    f"{max_retries + 1}"
                )
                time.sleep(wait_seconds)
                continue

            resp.raise_for_status()
            return resp

        except requests.exceptions.Timeout:
            last_error = (
                f"Timeout on attempt {attempt + 1}/"
                f"{max_retries + 1}"
            )
            if attempt < max_retries:
                wait_seconds = min(2 ** attempt * 5, 120)
                time.sleep(wait_seconds)
                continue
            raise RuntimeError(
                f"Request timed out after {max_retries + 1} attempts"
            ) from None

    raise RuntimeError(
        f"Max retries ({max_retries}) exhausted. Last error: {last_error}"
    )


def _archive_files(source_dir, archive_dir, filenames):
    """Copy files from source to archive directory, then remove from source.

    Args:
        source_dir: Path to the source directory.
        archive_dir: Path to the archive directory.
        filenames: List of filenames to archive.
    """
    source_dir = Path(source_dir)
    archive_dir = Path(archive_dir)
    archive_dir.mkdir(parents=True, exist_ok=True)

    for fname in filenames:
        src = source_dir / fname
        dst = archive_dir / fname
        if src.exists():
            shutil.copy2(str(src), str(dst))
            src.unlink()


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
def generate_images(*, context, state, step_cfg, project_root):
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
    _load_env()

    api_key = os.environ.get("AGNES_API_KEY", "")
    base_url = os.environ.get(
        "AGNES_BASE_URL", "https://apihub.agnes-ai.com"
    )
    if not api_key:
        return ActionResult(
            status="REJECTED",
            remark="AGNES_API_KEY not found in environment.",
            artifacts={},
            reject_code="MISSING_API_KEY",
        )

    # Resolve paths from context
    step_02_dir = Path(context.get("STEP_02_DIR", ""))
    step_03_dir = Path(context.get("STEP_03_DIR", ""))
    step_02_archive = Path(context.get("STEP_02_ARCHIVE", ""))
    config_path = Path(context.get("MEDIA_CONFIG", ""))

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

    # Prepare output directory
    step_03_dir.mkdir(parents=True, exist_ok=True)

    # Scan for variant JSON files in step_02
    variant_jsons = sorted(step_02_dir.glob("*.json"))
    if not variant_jsons:
        return ActionResult(
            status="REJECTED",
            remark="No variant JSON files found in step_02.",
            artifacts={},
            reject_code="NO_INPUTS",
        )

    # API endpoint
    image_endpoint = f"{base_url.rstrip('/')}/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    successes = []
    failures = []
    file_mappings = []
    archived_filenames = []

    for variant_json_path in variant_jsons:
        try:
            with open(variant_json_path, "r", encoding="utf-8") as f:
                variant_data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            failures.append(
                f"{variant_json_path.name}: read error - {exc}"
            )
            continue

        variations = variant_data.get("variations", [])
        if not variations:
            failures.append(
                f"{variant_json_path.name}: no variations found"
            )
            continue

        updated_variations = []
        variant_success = True

        for var_idx, variation in enumerate(variations):
            t2i_prompt = variation.get("t2i_prompt1", "")
            image_filename = variation.get("image_filename", "")

            if not t2i_prompt:
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

            try:
                resp = _api_request_with_retry(
                    "POST",
                    image_endpoint,
                    headers=headers,
                    json_payload=payload,
                    timeout=api_timeout,
                    max_retries=api_max_retries,
                )
                resp_data = resp.json()

                # Extract image URL from response
                image_url = ""
                data_array = resp_data.get("data", [])
                if data_array:
                    image_url = data_array[0].get("url", "")

                if not image_url:
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

                # Update variation with image_url
                updated_var = dict(variation)
                updated_var["image_url"] = image_url
                updated_variations.append(updated_var)

                file_mappings.append({
                    "input": f"step_02/{variant_json_path.name}",
                    "output": f"step_03/{image_filename}",
                    "updated_json": f"step_03/{variant_json_path.name}",
                })

                # Process delay between API calls
                if var_idx < len(variations) - 1:
                    time.sleep(process_delay)

            except Exception as exc:
                failures.append(
                    f"{variant_json_path.name}[{var_idx}]: "
                    f"API error - {exc}"
                )
                variant_success = False

        # Write updated JSON to step_03 (with image_url populated)
        if updated_variations:
            updated_data = dict(variant_data)
            updated_data["variations"] = updated_variations
            updated_json_path = step_03_dir / variant_json_path.name
            with open(updated_json_path, "w", encoding="utf-8") as f:
                json.dump(
                    updated_data, f, indent=2, ensure_ascii=False
                )

        if variant_success:
            successes.append(variant_json_path.name)
        archived_filenames.append(variant_json_path.name)

    # Archive processed JSONs from step_02 to step_02_archive
    if archived_filenames:
        _archive_files(
            step_02_dir, step_02_archive, archived_filenames
        )

    # Write index.json to step_03
    index_path = step_03_dir / "index.json"
    _write_index(index_path, "generate_images", file_mappings)

    # Build result
    total = len(variant_jsons)
    success_count = len(successes)
    fail_count = len(failures)

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
    _load_env()

    api_key = os.environ.get("AGNES_API_KEY", "")
    base_url = os.environ.get(
        "AGNES_BASE_URL", "https://apihub.agnes-ai.com"
    )
    if not api_key:
        return ActionResult(
            status="REJECTED",
            remark="AGNES_API_KEY not found in environment.",
            artifacts={},
            reject_code="MISSING_API_KEY",
        )

    # Resolve paths from context
    step_03_dir = Path(context.get("STEP_03_DIR", ""))
    step_04_dir = Path(context.get("STEP_04_DIR", ""))
    step_03_archive = Path(context.get("STEP_03_ARCHIVE", ""))
    config_path = Path(context.get("MEDIA_CONFIG", ""))

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
    process_delay = config.get("process_delay", 15)
    api_timeout = config.get("api_timeout", 500)
    api_max_retries = config.get("api_max_retries", 5)

    # Prepare output directory
    step_04_dir.mkdir(parents=True, exist_ok=True)

    # Scan for JSON files in step_03 (skip index.json)
    variant_jsons = sorted(
        p for p in step_03_dir.glob("*.json")
        if p.name != "index.json"
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
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    successes = []
    failures = []
    file_mappings = []
    archived_filenames = []

    for variant_json_path in variant_jsons:
        try:
            with open(variant_json_path, "r", encoding="utf-8") as f:
                variant_data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            failures.append(
                f"{variant_json_path.name}: read error - {exc}"
            )
            continue

        variations = variant_data.get("variations", [])
        if not variations:
            failures.append(
                f"{variant_json_path.name}: no variations found"
            )
            continue

        file_success = True

        for var_idx, variation in enumerate(variations):
            t2i_prompt = variation.get("t2i_prompt1", "")
            image_url = variation.get("image_url", "")

            if not t2i_prompt or not image_url:
                failures.append(
                    f"{variant_json_path.name}[{var_idx}]: "
                    f"missing t2i_prompt1 or image_url"
                )
                file_success = False
                continue

            # Submit video generation request
            payload = {
                "model": vid_model,
                "prompt": t2i_prompt,
                "image": image_url,
                "width": vid_width,
                "height": vid_height,
                "num_frames": vid_num_frames,
                "frame_rate": vid_frame_rate,
            }

            try:
                submit_resp = _api_request_with_retry(
                    "POST",
                    video_submit_endpoint,
                    headers=headers,
                    json_payload=payload,
                    timeout=api_timeout,
                    max_retries=api_max_retries,
                )
                submit_data = submit_resp.json()

                # Extract video ID from response
                video_id = submit_data.get("video_id", "")
                if not video_id:
                    video_id = submit_data.get("id", "")
                if not video_id:
                    failures.append(
                        f"{variant_json_path.name}[{var_idx}]: "
                        f"no video_id in submit response"
                    )
                    file_success = False
                    continue

                # Poll for video completion
                status_url = (
                    f"{video_status_endpoint}?video_id={video_id}"
                )
                video_download_url = ""
                max_poll_attempts = 120
                poll_interval = 10

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

                file_mappings.append({
                    "input": (
                        f"step_03/{image_filename}"
                        if image_filename
                        else f"step_03/{variant_json_path.name}"
                    ),
                    "output": f"step_04/{video_filename}",
                })

                # Process delay between API calls
                if var_idx < len(variations) - 1:
                    time.sleep(process_delay)

            except Exception as exc:
                failures.append(
                    f"{variant_json_path.name}[{var_idx}]: "
                    f"API error - {exc}"
                )
                file_success = False

        if file_success:
            successes.append(variant_json_path.name)
        archived_filenames.append(variant_json_path.name)

    # Archive processed files from step_03 to step_03_archive
    if archived_filenames:
        _archive_files(
            step_03_dir, step_03_archive, archived_filenames
        )

    # Write index.json to step_04
    index_path = step_04_dir / "index.json"
    _write_index(index_path, "generate_videos", file_mappings)

    # Build result
    total = len(variant_jsons)
    success_count = len(successes)
    fail_count = len(failures)

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
