"""Implementation actions for agnes_media_gen_v1.impls.agnes_media_v1.

Implements the Agnes-specific image and video generation actions.
"""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.api_key_pool import ApiKeyPool, load_env_from_project, mask_api_key
from agent_runner_v2.concurrent_api import ConcurrentApiRunner
from agent_runner_v2.workflow_packages.actions import action

logger = logging.getLogger(__name__)


# ============================================================================
# Shared Utilities (kept local for implementation isolation)
# ============================================================================

def _load_config(config_path):
    """Load and parse the media configuration JSON file."""
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Media config not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _api_request_with_retry(method, url, *, headers, json_payload=None, timeout=500, max_retries=5, retry_base_wait=5):
    """Execute an HTTP request with retry logic for 503, 429, and 400 responses."""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            if method.upper() == "GET":
                resp = requests.get(url, headers=headers, timeout=timeout)
            else:
                resp = requests.post(url, headers=headers, json=json_payload, timeout=timeout)

            if resp.status_code in (503, 429, 400):
                wait_seconds = min(retry_base_wait * (2 ** attempt), 120)
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
                wait_seconds = min(retry_base_wait * (2 ** attempt), 120)
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


def _get_next_sequence_filename(output_dir: Path, base_name: str, ext: str) -> str:
    """Find the next available filename with auto-incrementing sequence number."""
    ext = ext.lstrip(".")
    base_path = output_dir / f"{base_name}.{ext}"
    if not base_path.exists():
        return f"{base_name}.{ext}"
    seq = 1
    while True:
        candidate = output_dir / f"{base_name}_{seq:03d}.{ext}"
        if not candidate.exists():
            return f"{base_name}_{seq:03d}.{ext}"
        seq += 1
        if seq > 9999:
            return f"{base_name}_{seq:04d}.{ext}"


# ============================================================================
# Image Generation Implementation
# ============================================================================

@dataclass
class _ImageWorkItem:
    """Single image generation work item for concurrent processing."""
    variation: dict
    variant_json_path: Path
    var_idx: int
    image_endpoint: str
    img_model: str
    img_size: str
    img_ratio: str
    api_timeout: int
    api_max_retries: int
    retry_base_wait: int
    process_delay: int
    step_03_dir: Path
    key_pool: ApiKeyPool


def _process_single_image(item: _ImageWorkItem) -> dict:
    """Worker function for concurrent image generation."""
    t2i_prompt = item.variation.get("t2i_prompt1", "")
    image_filename = item.variation.get("image_filename", "")

    if not t2i_prompt:
        raise ValueError(f"{item.variant_json_path.name}[{item.var_idx}]: empty t2i_prompt1")

    payload = {"model": item.img_model, "prompt": t2i_prompt, "size": item.img_size}
    if item.img_ratio:
        payload["ratio"] = item.img_ratio

    if item.process_delay > 0:
        time.sleep(item.process_delay)

    api_key = item.key_pool.next_key()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    resp = _api_request_with_retry("POST", item.image_endpoint, headers=headers, json_payload=payload,
                                   timeout=item.api_timeout, max_retries=item.api_max_retries, retry_base_wait=item.retry_base_wait)
    resp_data = resp.json()

    image_url = ""
    data_array = resp_data.get("data", [])
    if data_array:
        image_url = data_array[0].get("url", "")

    if not image_url:
        raise ValueError(f"{item.variant_json_path.name}[{item.var_idx}]: no image URL in API response")

    img_resp = requests.get(image_url, timeout=item.api_timeout)
    img_resp.raise_for_status()

    if not image_filename:
        stem = item.variant_json_path.stem
        image_filename = f"{stem}_{item.var_idx + 1:02d}.png"

    base_name = Path(image_filename).stem
    image_filename = _get_next_sequence_filename(item.step_03_dir, base_name, "png")
    img_output_path = item.step_03_dir / image_filename

    with open(img_output_path, "wb") as img_f:
        img_f.write(img_resp.content)

    updated_var = dict(item.variation)
    updated_var["image_url"] = image_url

    return {
        "updated_variation": updated_var,
        "image_filename": image_filename,
        "file_mapping": {
            "input": f"step_02_promptvariant/{item.variant_json_path.name}",
            "output": f"step_03_generatedimage/{image_filename}",
            "updated_json": f"step_03_generatedimage/{item.variant_json_path.name}",
        },
    }


@action("generate_images_agnes_media")
def generate_images_agnes_media(*, context, state, step_cfg, project_root) -> ActionResult:
    """Generate images from prompt variants using Agnes Image 2.1 Flash API."""
    load_env_from_project(project_root)
    key_pool = ApiKeyPool("AGNES_API_KEY", load_env=False)
    base_url = os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com")
    
    step_02_dir = Path(context.get("STEP_02_DIR", ""))
    step_03_dir = Path(context.get("STEP_03_DIR", ""))
    config_path = Path(context.get("MEDIA_CONFIG", ""))

    if not step_02_dir.is_dir():
        return ActionResult(status="REJECTED", remark=f"Step 02 directory not found: {step_02_dir}", artifacts={}, reject_code="MISSING_INPUT_DIR")

    try:
        config = _load_config(config_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return ActionResult(status="REJECTED", remark=f"Failed to load config: {exc}", artifacts={}, reject_code="CONFIG_LOAD_FAILED")

    img_config = config.get("image", {})
    img_model = img_config.get("model", "agnes-image-2.1-flash")
    img_size = img_config.get("size", "1024x1024")
    img_ratio = img_config.get("ratio", "")
    process_delay = config.get("process_delay", 15)
    api_timeout = config.get("api_timeout", 500)
    api_max_retries = config.get("api_max_retries", 5)
    retry_base_wait = config.get("retry_base_wait", 5)
    max_concurrent = config.get("max_concurrent", 2)

    step_03_dir.mkdir(parents=True, exist_ok=True)
    variant_jsons = sorted(p for p in step_02_dir.glob("*.json") if p.name != "index.json")

    if not variant_jsons:
        return ActionResult(status="REJECTED", remark="No variant JSON files found in step_02_promptvariant.", artifacts={}, reject_code="NO_INPUTS")

    image_endpoint = f"{base_url.rstrip('/')}/v1/images/generations"
    variant_data_map: dict[str, dict] = {}
    work_items: list[_ImageWorkItem] = []
    read_failures: list[str] = []

    for variant_json_path in variant_jsons:
        try:
            with open(variant_json_path, "r", encoding="utf-8") as f:
                variant_data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            read_failures.append(f"{variant_json_path.name}: read error - {exc}")
            continue

        variations = variant_data.get("variations", [])
        if not variations:
            read_failures.append(f"{variant_json_path.name}: no variations found")
            continue

        variant_data_map[variant_json_path.name] = variant_data

        for var_idx, variation in enumerate(variations):
            work_items.append(_ImageWorkItem(
                variation=variation, variant_json_path=variant_json_path, var_idx=var_idx,
                image_endpoint=image_endpoint, img_model=img_model, img_size=img_size, img_ratio=img_ratio,
                api_timeout=api_timeout, api_max_retries=api_max_retries, retry_base_wait=retry_base_wait,
                process_delay=process_delay, step_03_dir=step_03_dir, key_pool=key_pool,
            ))

    if not work_items:
        return ActionResult(status="REJECTED", remark="No work items to process. " + "; ".join(read_failures), artifacts={}, reject_code="NO_INPUTS")

    runner = ConcurrentApiRunner(max_workers=max_concurrent)
    results = runner.run(work_items, _process_single_image, desc="generate_images_agnes_media")

    successes = []
    failures = list(read_failures)
    file_mappings = []
    results_by_json: dict[str, list] = {}

    for r in results:
        item = r.item
        json_name = item.variant_json_path.name
        if r.success:
            file_mappings.append(r.data["file_mapping"])
            results_by_json.setdefault(json_name, []).append(r.data)
        else:
            failures.append(f"{item.variant_json_path.name}[{item.var_idx}]: {r.error}")

    for variant_json_path in variant_jsons:
        json_name = variant_json_path.name
        if json_name not in variant_data_map:
            continue

        original_data = variant_data_map[json_name]
        json_results = results_by_json.get(json_name, [])
        success_indices = {r.item.var_idx: r.data["updated_variation"] for r in results if r.success and r.item.variant_json_path.name == json_name}

        updated_variations = []
        all_succeeded = True
        for var_idx, variation in enumerate(original_data.get("variations", [])):
            if var_idx in success_indices:
                updated_variations.append(success_indices[var_idx])
            else:
                all_succeeded = False

        if updated_variations:
            updated_data = dict(original_data)
            updated_data["variations"] = updated_variations
            updated_json_path = step_03_dir / json_name
            with open(updated_json_path, "w", encoding="utf-8") as f:
                json.dump(updated_data, f, indent=2, ensure_ascii=False)

        if all_succeeded and json_results:
            successes.append(json_name)

    index_path = step_03_dir / "index.json"
    _write_index(index_path, "generate_images_agnes_media", file_mappings)

    total = len(variant_jsons)
    success_count = len(successes)
    fail_count = len(failures)

    if fail_count == 0:
        return ActionResult(status="APPROVED", remark=f"Generated images for {success_count}/{total} variant files.", artifacts={"IMAGE_INDEX": str(index_path)})
    else:
        return ActionResult(status="REJECTED", remark=f"Partial failure: {success_count}/{total} succeeded. Errors: {'; '.join(failures[:10])}", artifacts={"IMAGE_INDEX": str(index_path)}, reject_code="IMAGE_GEN_PARTIAL_FAILURE")


# ============================================================================
# Video Generation Implementation
# ============================================================================

@dataclass
class _VideoWorkItem:
    """Single video generation work item for concurrent processing."""
    variation: dict
    variant_json_path: Path
    var_idx: int
    video_submit_endpoint: str
    video_status_endpoint: str
    vid_model: str
    vid_width: int
    vid_height: int
    vid_num_frames: int
    vid_frame_rate: int
    final_video_prompt: str
    negative_prompt: str
    api_timeout: int
    api_max_retries: int
    retry_base_wait: int
    process_delay: int
    step_04_dir: Path
    key_pool: ApiKeyPool


def _process_single_video(item: _VideoWorkItem) -> dict:
    """Worker function for concurrent video generation."""
    video_prompt = item.final_video_prompt
    image_url = item.variation.get("image_url", "")

    if not video_prompt or not image_url:
        raise ValueError(f"{item.variant_json_path.name}[{item.var_idx}]: missing video prompt or image_url")

    payload = {
        "model": item.vid_model, "prompt": video_prompt, "image": image_url,
        "width": item.vid_width, "height": item.vid_height,
        "num_frames": item.vid_num_frames, "frame_rate": item.vid_frame_rate,
    }
    if item.negative_prompt:
        payload["negative_prompt"] = item.negative_prompt

    if item.process_delay > 0:
        time.sleep(item.process_delay)

    api_key = item.key_pool.next_key()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    submit_resp = _api_request_with_retry("POST", item.video_submit_endpoint, headers=headers, json_payload=payload,
                                          timeout=item.api_timeout, max_retries=item.api_max_retries, retry_base_wait=item.retry_base_wait)
    submit_data = submit_resp.json()

    video_id = submit_data.get("video_id", "") or submit_data.get("id", "")
    if not video_id:
        raise ValueError(f"{item.variant_json_path.name}[{item.var_idx}]: no video_id in submit response")

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
        raise ValueError(f"{item.variant_json_path.name}[{item.var_idx}]: no download URL after completion")

    vid_resp = requests.get(video_download_url, timeout=item.api_timeout)
    vid_resp.raise_for_status()

    image_filename = item.variation.get("image_filename", "")
    if image_filename:
        video_base = Path(image_filename).stem
    else:
        stem = item.variant_json_path.stem
        video_base = f"{stem}_{item.var_idx + 1:02d}"

    video_filename = _get_next_sequence_filename(item.step_04_dir, video_base, "mp4")
    vid_output_path = item.step_04_dir / video_filename

    with open(vid_output_path, "wb") as vid_f:
        vid_f.write(vid_resp.content)

    return {
        "video_filename": video_filename,
        "file_mapping": {
            "input": f"step_03_generatedimage/{image_filename}" if image_filename else f"step_03_generatedimage/{item.variant_json_path.name}",
            "output": f"step_04_generatedvideo/{video_filename}",
        },
    }


@action("generate_videos_agnes_media")
def generate_videos_agnes_media(*, context, state, step_cfg, project_root) -> ActionResult:
    """Generate videos from images using Agnes Video V2.0 API."""
    load_env_from_project(project_root)
    key_pool = ApiKeyPool("AGNES_API_KEY", load_env=False)
    base_url = os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com")
    
    step_03_dir = Path(context.get("STEP_03_DIR", ""))
    step_04_dir = Path(context.get("STEP_04_DIR", ""))
    config_path = Path(context.get("MEDIA_CONFIG", ""))

    if not step_03_dir.is_dir():
        return ActionResult(status="REJECTED", remark=f"Step 03 directory not found: {step_03_dir}", artifacts={}, reject_code="MISSING_INPUT_DIR")

    try:
        config = _load_config(config_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return ActionResult(status="REJECTED", remark=f"Failed to load config: {exc}", artifacts={}, reject_code="CONFIG_LOAD_FAILED")

    vid_config = config.get("video", {})
    vid_model = vid_config.get("model", "agnes-video-v2.0")
    vid_width = vid_config.get("width", 1024)
    vid_height = vid_config.get("height", 576)
    vid_num_frames = vid_config.get("num_frames", 72)
    vid_frame_rate = vid_config.get("frame_rate", 24)
    vid_prompt_field = vid_config.get("video_prompt", "t2v_prompt1")
    vid_prompt_prefix = vid_config.get("video_prompt_prefix", "")
    vid_prompt_postfix = vid_config.get("video_prompt_postfix", "")
    vid_negative_prompt_postfix = vid_config.get("negative_prompt_video_postfix", "")

    _HARDCODED_NEGATIVE = (
        "birds, seagulls, flying creatures, falling leaves, falling petals, "
        "fish jumping, dolphins, butterflies, insects, debris falling, "
        "objects appearing, objects disappearing, new animals, new people, "
        "duplicate moon, double moon, duplicate sun, double sun, "
        "multiple moons, multiple suns, duplicated objects, "
        "shaky camera, handheld camera, walking camera, footstep motion, "
        "camera bounce, camera jitter, footstep shake, unstable camera"
    )

    process_delay = config.get("process_delay", 15)
    api_timeout = config.get("api_timeout", 500)
    api_max_retries = config.get("api_max_retries", 5)
    retry_base_wait = config.get("retry_base_wait", 5)
    max_concurrent = config.get("max_concurrent", 2)

    step_04_dir.mkdir(parents=True, exist_ok=True)
    variant_jsons = sorted(p for p in step_03_dir.glob("*.json") if p.name != "index.json")

    if not variant_jsons:
        return ActionResult(status="REJECTED", remark="No variant JSON files found in step_03_generatedimage.", artifacts={}, reject_code="NO_INPUTS")

    video_submit_endpoint = f"{base_url.rstrip('/')}/v1/videos"
    video_status_endpoint = f"{base_url.rstrip('/')}/agnesapi"

    work_items: list[_VideoWorkItem] = []
    read_failures: list[str] = []
    variant_json_names: list[str] = []

    for variant_json_path in variant_jsons:
        try:
            with open(variant_json_path, "r", encoding="utf-8") as f:
                variant_data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            read_failures.append(f"{variant_json_path.name}: read error - {exc}")
            continue

        variations = variant_data.get("variations", [])
        if not variations:
            read_failures.append(f"{variant_json_path.name}: no variations found")
            continue

        variant_json_names.append(variant_json_path.name)

        for var_idx, variation in enumerate(variations):
            video_prompt = variation.get(vid_prompt_field, "")
            if not video_prompt:
                video_prompt = variation.get("t2i_prompt1", "")
            image_url = variation.get("image_url", "")

            if not video_prompt or not image_url:
                read_failures.append(f"{variant_json_path.name}[{var_idx}]: missing {vid_prompt_field}/image_url")
                continue

            final_video_prompt = vid_prompt_prefix + video_prompt + vid_prompt_postfix

            neg_prompt_video = variation.get("negative_prompt_video", "")
            negative_prompt = neg_prompt_video
            if vid_negative_prompt_postfix:
                negative_prompt = f"{negative_prompt} {vid_negative_prompt_postfix}" if negative_prompt else vid_negative_prompt_postfix
            if negative_prompt:
                negative_prompt = negative_prompt + " " + _HARDCODED_NEGATIVE
            else:
                negative_prompt = _HARDCODED_NEGATIVE

            work_items.append(_VideoWorkItem(
                variation=variation, variant_json_path=variant_json_path, var_idx=var_idx,
                video_submit_endpoint=video_submit_endpoint, video_status_endpoint=video_status_endpoint,
                vid_model=vid_model, vid_width=vid_width, vid_height=vid_height,
                vid_num_frames=vid_num_frames, vid_frame_rate=vid_frame_rate,
                final_video_prompt=final_video_prompt, negative_prompt=negative_prompt,
                api_timeout=api_timeout, api_max_retries=api_max_retries, retry_base_wait=retry_base_wait,
                process_delay=process_delay, step_04_dir=step_04_dir, key_pool=key_pool,
            ))

    if not work_items:
        return ActionResult(status="REJECTED", remark="No work items to process. " + "; ".join(read_failures), artifacts={}, reject_code="NO_INPUTS")

    runner = ConcurrentApiRunner(max_workers=max_concurrent)
    results = runner.run(work_items, _process_single_video, desc="generate_videos_agnes_media")

    successes = []
    failures = list(read_failures)
    file_mappings = []
    success_json_names: set[str] = set()

    for r in results:
        item = r.item
        if r.success:
            file_mappings.append(r.data["file_mapping"])
            success_json_names.add(item.variant_json_path.name)
        else:
            failures.append(f"{item.variant_json_path.name}[{item.var_idx}]: {r.error}")

    failed_json_names = {f.split("]")[0] + "]" for f in failures if "[" in f}
    for name in variant_json_names:
        if name not in failed_json_names and name in success_json_names:
            successes.append(name)

    index_path = step_04_dir / "index.json"
    _write_index(index_path, "generate_videos_agnes_media", file_mappings)

    total = len(variant_jsons)
    success_count = len(successes)
    fail_count = len(failures)

    if fail_count == 0:
        return ActionResult(status="APPROVED", remark=f"Generated videos for {success_count}/{total} variant files.", artifacts={"VIDEO_INDEX": str(index_path)})
    else:
        return ActionResult(status="REJECTED", remark=f"Partial failure: {success_count}/{total} succeeded. Errors: {'; '.join(failures[:10])}", artifacts={"VIDEO_INDEX": str(index_path)}, reject_code="VIDEO_GEN_PARTIAL_FAILURE")
