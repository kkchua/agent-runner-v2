"""Shared actions and utilities for gen_media_content_v1 workflow.

Provides reusable helpers for media generation workflows (config loading,
API retry logic, index writing, filename sequencing, and dynamic provider
import). Specific providers are implemented in the api_actions/ directory.
"""
from __future__ import annotations

import importlib
import json
import logging
import os
import time
from pathlib import Path

import requests

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.actions.preset_config import merge_preset_into_config
from agent_runner_v2.api_key_pool import ApiKeyPool, load_env_from_project
from agent_runner_v2.workflow_packages.actions import action

logger = logging.getLogger(__name__)


# ============================================================================
# Shared Utilities
# ============================================================================

def _load_config(config_path):
    """Load and parse the media configuration JSON file.

    Parameters
    ----------
    config_path : str or Path
        Path to the JSON configuration file.

    Returns
    -------
    dict
        Parsed configuration dictionary.

    Raises
    ------
    FileNotFoundError
        If the config file does not exist.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Media config not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _api_request_with_retry(method, url, *, headers, json_payload=None,
                            timeout=500, max_retries=5, retry_base_wait=5):
    """Execute an HTTP request with retry logic for 503, 429, and timeout errors.

    Retries on HTTP 503, 429, and timeout exceptions with exponential backoff.
    Raises RuntimeError after max retries are exhausted.

    Parameters
    ----------
    method : str
        HTTP method ("GET" or "POST").
    url : str
        Target URL.
    headers : dict
        HTTP headers to send.
    json_payload : dict, optional
        JSON body for POST requests.
    timeout : int
        Request timeout in seconds (forwarded to requests library).
    max_retries : int
        Maximum number of retry attempts after initial request.
    retry_base_wait : int
        Base wait time in seconds for exponential backoff.

    Returns
    -------
    requests.Response
        The successful HTTP response.

    Raises
    ------
    RuntimeError
        If max retries are exhausted.
    """
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            if method.upper() == "GET":
                resp = requests.get(url, headers=headers, timeout=timeout)
            else:
                resp = requests.post(url, headers=headers, json=json_payload, timeout=timeout)

            if resp.status_code in (503, 429):
                wait_seconds = min(retry_base_wait * (2 ** attempt), 120)
                last_error = f"HTTP {resp.status_code} on attempt {attempt + 1}/{max_retries + 1}"
                logger.warning(
                    "HTTP %d from %s - attempt %d/%d, retrying in %ds",
                    resp.status_code, url, attempt + 1, max_retries + 1, wait_seconds,
                )
                time.sleep(wait_seconds)
                continue

            resp.raise_for_status()
            logger.debug("HTTP %s %s -> %d", method, url, resp.status_code)
            return resp

        except requests.exceptions.Timeout:
            last_error = f"Timeout on attempt {attempt + 1}/{max_retries + 1}"
            if attempt < max_retries:
                wait_seconds = min(retry_base_wait * (2 ** attempt), 120)
                logger.warning(
                    "Timeout on %s - attempt %d/%d, retrying in %ds",
                    url, attempt + 1, max_retries + 1, wait_seconds,
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

    Creates parent directories if they do not exist.

    Parameters
    ----------
    index_path : str or Path
        Path where the index JSON file will be written.
    step_name : str
        Name of the pipeline step (e.g., "render_image").
    file_mappings : list
        List of file mapping dicts (e.g., [{"input": "a.png", "output": "b.png"}]).
    """
    index_data = {"step": step_name, "files": file_mappings}
    index_path = Path(index_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)


def _get_next_sequence_filename(output_dir: Path, base_name: str, ext: str) -> str:
    """Find the next available filename with auto-incrementing sequence number.

    Returns base.ext when no files exist, then base_001.ext, base_002.ext, etc.
    Format changes from 3-digit to 4-digit at seq > 9999.

    Parameters
    ----------
    output_dir : Path
        Directory where files are being created.
    base_name : str
        Base filename without extension.
    ext : str
        File extension (leading dot is stripped if present).

    Returns
    -------
    str
        The next available filename string.
    """
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


def _get_api_actions_dir():
    """Return the path to the api_actions directory for this workflow.

    Separated as a helper to enable test mocking.

    Returns
    -------
    Path
        Absolute path to the api_actions directory.
    """
    return Path(__file__).resolve().parent / "api_actions"


def import_provider(provider_type, provider_name):
    """Dynamically import a provider module from the api_actions directory.

    Imports the module at
    workflows.gen_media_content_v1.api_actions.{provider_type}.{provider_name}
    and validates that it contains a call_api function.

    Parameters
    ----------
    provider_type : str
        Provider type (e.g., "render_image", "render_video").
    provider_name : str
        Provider name (e.g., "agnes_v1", "happyhorse_v1_1").

    Returns
    -------
    module
        The imported provider module (guaranteed to have call_api).

    Raises
    ------
    ImportError
        If the module does not exist or lacks a call_api function.
    """
    module_path = (
        f"workflows.gen_media_content_v1.api_actions.{provider_type}.{provider_name}"
    )
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as exc:
        raise ImportError(
            f"Provider '{provider_type}/{provider_name}' not found: {exc}"
        ) from exc

    if not hasattr(module, "call_api"):
        raise ImportError(
            f"Provider '{provider_type}/{provider_name}' missing call_api function"
        )
    return module


# ============================================================================
# Provider Resolution Helpers
# ============================================================================

_PROVIDER_KEY_PREFIX_MAP = {
    "agnes_v1": "AGNES_API_KEY",
    "agnes_v2": "AGNES_API_KEY",
    "happyhorse_v1_1": "HAPPYHORSE_API_KEY",
}

_PROVIDER_BASE_URL_MAP = {
    "agnes_v1": ("AGNES_BASE_URL", "https://apihub.agnes-ai.com"),
    "agnes_v2": ("AGNES_BASE_URL", "https://apihub.agnes-ai.com"),
    "happyhorse_v1_1": ("HAPPYHORSE_BASE_URL", "https://dashscope.aliyuncs.com"),
}


def _resolve_key_prefix(provider_name: str) -> str:
    """Map provider name to API key environment variable prefix.

    Uses a static mapping for known providers. Falls back to deriving
    the prefix from the provider name by stripping the version suffix.

    Parameters
    ----------
    provider_name : str
        Provider name (e.g., "agnes_v1", "happyhorse_v1_1").

    Returns
    -------
    str
        Environment variable prefix (e.g., "AGNES_API_KEY").
    """
    if provider_name in _PROVIDER_KEY_PREFIX_MAP:
        return _PROVIDER_KEY_PREFIX_MAP[provider_name]
    base = provider_name.split("_v")[0].upper()
    return f"{base}_API_KEY"


def _resolve_base_url(provider_name: str) -> str:
    """Resolve base URL for a provider from environment or default.

    Returns empty string if the provider is unknown and the derived
    environment variable is not set. Callers MUST validate the return
    value is non-empty before making API calls.

    Parameters
    ----------
    provider_name : str
        Provider name (e.g., "agnes_v1", "happyhorse_v1_1").

    Returns
    -------
    str
        Base URL string. May be empty for unknown providers without
        an environment variable set.
    """
    if provider_name in _PROVIDER_BASE_URL_MAP:
        env_var, default = _PROVIDER_BASE_URL_MAP[provider_name]
        return os.environ.get(env_var, default)
    base = provider_name.split("_v")[0].upper()
    env_var = f"{base}_BASE_URL"
    return os.environ.get(env_var, "")


# ============================================================================
# Default Orchestrators
# ============================================================================

@action("generate_images_default")
def generate_images_default(*, context, state, step_cfg, project_root) -> ActionResult:
    """Default orchestrator for image generation.

    Dynamically imports the configured render_image provider, scans STEP_02_DIR
    for variant JSON files, calls the provider API for each variation, downloads
    the resulting images, and writes an index.json to STEP_03_DIR.

    Parameters
    ----------
    context : dict
        Workflow context with MEDIA_CONFIG, STEP_02_DIR, STEP_03_DIR keys.
    state : object
        Workflow state (unused by this action).
    step_cfg : object
        Step configuration (unused by this action).
    project_root : Path or str
        Root directory of the project (used for .env loading).

    Returns
    -------
    ActionResult
        APPROVED if at least one image generated successfully,
        REJECTED with appropriate reject_code on failure.
    """
    logger.info("=== generate_images_default START ===")
    config_path = Path(context.get("MEDIA_CONFIG", ""))
    step_02_dir = Path(context.get("STEP_02_DIR", ""))
    step_03_dir = Path(context.get("STEP_03_DIR", ""))
    logger.info("Config: %s, step_02: %s, step_03: %s", config_path, step_02_dir, step_03_dir)

    load_env_from_project(project_root)

    try:
        config = _load_config(config_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logger.error("Failed to load config: %s", exc)
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to load config: {exc}",
            artifacts={},
            reject_code="CONFIG_LOAD_FAILED",
        )

    config = merge_preset_into_config(config, context)

    # Step slot selection takes precedence over config + preset
    provider_name = context.get("STEP_SLOT_GENERATE_IMAGES", "")
    if not provider_name:
        provider_name = config.get("actions", {}).get("render_image", "")
    logger.info("Image provider selected: %s", provider_name or "(none)")
    if not provider_name or provider_name == "__none__":
        logger.info("Image generation skipped")
        return ActionResult(
            status="APPROVED",
            remark="Image generation skipped (no provider configured).",
            artifacts={},
        )

    try:
        provider = import_provider("render_image", provider_name)
        logger.info("Provider imported: %s", provider.__name__ if hasattr(provider, '__name__') else provider_name)
    except ImportError as exc:
        logger.error("Failed to import provider '%s': %s", provider_name, exc)
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to import provider: {exc}",
            artifacts={},
            reject_code="IMPORT_FAILED",
        )

    api_config = config.get("api", {}).get(provider_name)
    if api_config is None:
        logger.error("Provider '%s' not found in config.api section", provider_name)
        return ActionResult(
            status="REJECTED",
            remark=f"Provider '{provider_name}' not found in config.api section",
            artifacts={},
            reject_code="INVALID_CONFIG",
        )

    key_prefix = _resolve_key_prefix(provider_name)
    key_pool = ApiKeyPool(key_prefix, project_root=project_root, load_env=False)

    base_url = _resolve_base_url(provider_name)
    if not base_url or not base_url.strip():
        logger.error("No base_url configured for provider '%s'", provider_name)
        return ActionResult(
            status="REJECTED",
            remark=f"Base URL could not be resolved for provider '{provider_name}'",
            artifacts={},
            reject_code="INVALID_CONFIG",
        )

    if not step_02_dir.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"Step 02 directory not found: {step_02_dir}",
            artifacts={},
            reject_code="MISSING_INPUT_DIR",
        )

    step_03_dir.mkdir(parents=True, exist_ok=True)

    variant_jsons = sorted(
        p for p in step_02_dir.glob("*_prompts.json")
    )
    if not variant_jsons:
        return ActionResult(
            status="REJECTED",
            remark="No variant JSON files found in step_02 directory",
            artifacts={},
            reject_code="NO_INPUTS",
        )

    successes = 0
    failures = []
    file_mappings = []

    for variant_path in variant_jsons:
        try:
            with open(variant_path, "r", encoding="utf-8") as f:
                variant_data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            failures.append(f"{variant_path.name}: read error - {exc}")
            continue

        variations = variant_data.get("variations", [])
        updated_variations = []

        for var_idx, variation in enumerate(variations):
            t2i_prompt = variation.get("t2i_prompt1", "")
            if not t2i_prompt:
                failures.append(
                    f"{variant_path.name}[{var_idx}]: empty t2i_prompt1"
                )
                continue

            api_key = key_pool.next_key()
            logger.info("Generating image for %s[%d] using provider %s", variant_path.name, var_idx, provider_name)
            try:
                result = provider.call_api(
                    prompt=t2i_prompt,
                    config=api_config,
                    api_key=api_key,
                    base_url=base_url,
                )
                logger.info("API call succeeded for %s[%d], image_url: %s", variant_path.name, var_idx, result.get("image_url", "")[:80] + "..." if result.get("image_url") else "(none)")
            except Exception as exc:
                logger.error("API error for %s[%d]: %s", variant_path.name, var_idx, exc)
                failures.append(
                    f"{variant_path.name}[{var_idx}]: API error - {exc}"
                )
                continue

            image_url = result.get("image_url", "")
            if not image_url:
                logger.error("No image_url in response for %s[%d]", variant_path.name, var_idx)
                failures.append(
                    f"{variant_path.name}[{var_idx}]: no image_url in response"
                )
                continue

            try:
                img_resp = requests.get(image_url, timeout=500)
                img_resp.raise_for_status()
                logger.info("Downloaded image for %s[%d] (%d bytes)", variant_path.name, var_idx, len(img_resp.content))
            except requests.exceptions.RequestException as exc:
                logger.error("Download error for %s[%d]: %s", variant_path.name, var_idx, exc)
                failures.append(
                    f"{variant_path.name}[{var_idx}]: download error - {exc}"
                )
                continue

            image_filename = variation.get("image_filename", "")
            if image_filename:
                base_name = Path(image_filename).stem
            else:
                base_name = f"{variant_path.stem}_{var_idx + 1:02d}"

            output_filename = _get_next_sequence_filename(
                step_03_dir, base_name, "png"
            )
            output_path = step_03_dir / output_filename
            with open(output_path, "wb") as img_f:
                img_f.write(img_resp.content)
            logger.info("Saved image: %s", output_filename)

            updated_var = dict(variation)
            updated_var["image_url"] = image_url
            updated_var["image_filename"] = output_filename  # Actual generated image filename
            updated_variations.append(updated_var)

            file_mappings.append({
                "input": variant_path.name,
                "output": output_filename,
            })
            successes += 1

        if updated_variations:
            updated_data = dict(variant_data)
            updated_data["variations"] = updated_variations
            updated_json_path = step_03_dir / variant_path.name
            with open(updated_json_path, "w", encoding="utf-8") as f:
                json.dump(updated_data, f, indent=2, ensure_ascii=False)

    index_path = step_03_dir / "index.json"
    _write_index(index_path, "generate_images_default", file_mappings)

    if successes == 0:
        logger.error("All image generations failed. Errors: %s", "; ".join(failures[:10]))
        return ActionResult(
            status="REJECTED",
            remark=f"All image generations failed. Errors: {'; '.join(failures[:10])}",
            artifacts={"IMAGE_INDEX": str(index_path)},
            reject_code="ALL_FAILED",
        )

    total = len(variant_jsons)
    if failures:
        logger.warning("Partial success: %d/%d images generated. Errors: %s", successes, total, "; ".join(failures[:5]))
        return ActionResult(
            status="APPROVED",
            remark=f"Partial success: {successes} images generated from {total} variant files. Errors: {'; '.join(failures[:5])}",
            artifacts={"IMAGE_INDEX": str(index_path)},
        )

    logger.info("=== generate_images_default COMPLETE: %d images generated ===", successes)
    return ActionResult(
        status="APPROVED",
        remark=f"Generated {successes} images from {total} variant files.",
        artifacts={"IMAGE_INDEX": str(index_path)},
    )


@action("generate_videos_default")
def generate_videos_default(*, context, state, step_cfg, project_root) -> ActionResult:
    """Default orchestrator for video generation.

    Scans STEP_03_DIR for variant JSONs (with image_url fields populated by
    generate_images), calls the configured render_video provider for each
    variation, downloads resulting videos, and writes an index.json to STEP_04_DIR.

    Parameters
    ----------
    context : dict
        Workflow context with MEDIA_CONFIG, STEP_03_DIR, STEP_04_DIR keys.
    state : object
        Workflow state (unused by this action).
    step_cfg : object
        Step configuration (unused by this action).
    project_root : Path or str
        Root directory of the project (used for .env loading).

    Returns
    -------
    ActionResult
        APPROVED if video generation succeeded or was skipped,
        REJECTED with appropriate reject_code on failure.
    """
    logger.info("=== generate_videos_default START ===")
    config_path = Path(context.get("MEDIA_CONFIG", ""))
    step_03_dir = Path(context.get("STEP_03_DIR", ""))
    step_04_dir = Path(context.get("STEP_04_DIR", ""))
    logger.info("Config: %s, step_03: %s, step_04: %s", config_path, step_03_dir, step_04_dir)

    load_env_from_project(project_root)

    try:
        config = _load_config(config_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logger.error("Failed to load config: %s", exc)
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to load config: {exc}",
            artifacts={},
            reject_code="CONFIG_LOAD_FAILED",
        )

    config = merge_preset_into_config(config, context)

    # Step slot selection takes precedence over config + preset
    provider_name = context.get("STEP_SLOT_GENERATE_VIDEOS", "")
    if not provider_name:
        provider_name = config.get("actions", {}).get("render_video", "")
    logger.info("Video provider selected: %s", provider_name or "(none)")
    if not provider_name or provider_name == "__none__":
        logger.info("Video generation skipped")
        return ActionResult(
            status="APPROVED",
            remark="Video generation skipped (no provider configured).",
            artifacts={},
        )

    try:
        provider = import_provider("render_video", provider_name)
        logger.info("Provider imported: %s", provider.__name__ if hasattr(provider, '__name__') else provider_name)
    except ImportError as exc:
        logger.error("Failed to import provider '%s': %s", provider_name, exc)
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to import provider: {exc}",
            artifacts={},
            reject_code="IMPORT_FAILED",
        )

    api_config = config.get("api", {}).get(provider_name)
    if api_config is None:
        logger.error("Provider '%s' not found in config.api section", provider_name)
        return ActionResult(
            status="REJECTED",
            remark=f"Provider '{provider_name}' not found in config.api section",
            artifacts={},
            reject_code="INVALID_CONFIG",
        )

    logger.info("API config for %s: %s", provider_name, api_config)

    key_prefix = _resolve_key_prefix(provider_name)
    key_pool = ApiKeyPool(key_prefix, project_root=project_root, load_env=False)

    base_url = _resolve_base_url(provider_name)
    if not base_url or not base_url.strip():
        logger.error("No base_url configured for provider '%s'", provider_name)
        return ActionResult(
            status="REJECTED",
            remark=f"Base URL could not be resolved for provider '{provider_name}'",
            artifacts={},
            reject_code="INVALID_CONFIG",
        )

    logger.info("Base URL for %s: %s", provider_name, base_url)

    if not step_03_dir.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"Step 03 directory not found: {step_03_dir}",
            artifacts={},
            reject_code="MISSING_INPUT_DIR",
        )

    step_04_dir.mkdir(parents=True, exist_ok=True)

    successes = 0
    skipped = 0
    failures = []
    file_mappings = []

    # Build a lookup: image_filename → (video_prompt, image_url) from variant JSONs.
    # This allows us to scan actual images and find their prompts/URLs.
    image_to_variation: dict[str, dict] = {}
    variant_jsons = sorted(p for p in step_03_dir.glob("*.json") if p.name != "index.json")
    for variant_json_path in variant_jsons:
        try:
            with open(variant_json_path, "r", encoding="utf-8") as f:
                variant_data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read variant JSON %s: %s", variant_json_path.name, exc)
            continue
        for variation in variant_data.get("variations", []):
            img_filename = variation.get("image_filename", "")
            if img_filename:
                image_to_variation[img_filename] = variation

    # Scan step_03 for actual PNG images — these are the source of truth.
    # User may have deleted some images before proceeding to video generation.
    actual_images = sorted(p.name for p in step_03_dir.glob("*.png"))

    if not actual_images:
        return ActionResult(
            status="REJECTED",
            remark="No PNG images found in step_03 directory",
            artifacts={},
            reject_code="NO_INPUTS",
        )

    logger.info("Found %d images in step_03, %d variant JSONs with %d image mappings",
                len(actual_images), len(variant_jsons), len(image_to_variation))

    for img_name in actual_images:
        variation = image_to_variation.get(img_name)
        if variation is None:
            # No variant data for this image — skip with warning
            logger.warning("No variant data found for image %s — skipping", img_name)
            failures.append(f"{img_name}: no variant data (prompt/image_url)")
            continue

        video_prompt = variation.get("t2v_prompt1", "") or variation.get("t2i_prompt1", "")
        image_url = variation.get("image_url", "")
        if not video_prompt or not image_url:
            failures.append(f"{img_name}: missing prompt or image_url in variant data")
            continue

        video_base = Path(img_name).stem
        api_key = key_pool.next_key()
        logger.info("Generating video for %s using provider %s", img_name, provider_name)
        try:
            result = provider.call_api(
                prompt=video_prompt,
                image=image_url,
                config=api_config,
                api_key=api_key,
                base_url=base_url,
            )
            logger.info("API call succeeded for %s, video_url: %s", img_name, result.get("video_url", "")[:80] + "..." if result.get("video_url") else "(none)")
        except Exception as exc:
            logger.error("API error for %s: %s", img_name, exc)
            failures.append(f"{img_name}: API error - {exc}")
            continue

        if result.get("skipped", False):
            logger.info("Video skipped by provider for %s", img_name)
            skipped += 1
            continue

        video_url = result.get("video_url", "")
        if not video_url:
            logger.error("No video_url in response for %s", img_name)
            failures.append(f"{img_name}: no video_url in response")
            continue

        try:
            vid_resp = requests.get(video_url, timeout=500)
            vid_resp.raise_for_status()
            logger.info("Downloaded video for %s (%d bytes)", img_name, len(vid_resp.content))
        except requests.exceptions.RequestException as exc:
            logger.error("Download error for %s: %s", img_name, exc)
            failures.append(f"{img_name}: download error - {exc}")
            continue

        video_filename = _get_next_sequence_filename(step_04_dir, video_base, "mp4")
        vid_output_path = step_04_dir / video_filename
        with open(vid_output_path, "wb") as vid_f:
            vid_f.write(vid_resp.content)
        logger.info("Saved video: %s", video_filename)

        file_mappings.append({
            "input": img_name,
            "output": video_filename,
        })
        successes += 1

    video_index_path = step_04_dir / "index.json"
    _write_index(video_index_path, "generate_videos_default", file_mappings)

    if successes == 0 and skipped == 0:
        logger.error("All video generations failed. Errors: %s", "; ".join(failures[:10]))
        return ActionResult(
            status="REJECTED",
            remark=f"All video generations failed. Errors: {'; '.join(failures[:10])}",
            artifacts={"VIDEO_INDEX": str(video_index_path)},
            reject_code="ALL_FAILED",
        )

    if skipped > 0 and successes == 0:
        logger.info("All %d video(s) skipped by provider", skipped)
        return ActionResult(
            status="APPROVED",
            remark=f"All {skipped} video(s) skipped by provider.",
            artifacts={"VIDEO_INDEX": str(video_index_path)},
        )

    if failures:
        logger.warning("Partial success: %d videos generated, %d skipped. Errors: %s", successes, skipped, "; ".join(failures[:5]))
        return ActionResult(
            status="APPROVED",
            remark=f"Partial success: {successes} videos generated, {skipped} skipped. Errors: {'; '.join(failures[:5])}",
            artifacts={"VIDEO_INDEX": str(video_index_path)},
        )

    logger.info("=== generate_videos_default COMPLETE: %d videos generated ===", successes)
    return ActionResult(
        status="APPROVED",
        remark=f"Generated {successes} videos.",
        artifacts={"VIDEO_INDEX": str(video_index_path)},
    )
