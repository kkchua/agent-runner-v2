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
# Default Stubs
# ============================================================================

@action("generate_images_default")
def generate_images_default(*, context, state, step_cfg, project_root) -> ActionResult:
    """Default action for generate_images.

    This is a placeholder action. Please select a provider
    (e.g., 'agnes_v1') configured in config.json.
    """
    return ActionResult(
        status="REJECTED",
        remark=(
            "No image generation provider selected. "
            "Please configure a provider in config.json (e.g., agnes_v1)."
        ),
        artifacts={},
        reject_code="MISSING_PROVIDER",
    )


@action("generate_videos_default")
def generate_videos_default(*, context, state, step_cfg, project_root) -> ActionResult:
    """Default action for generate_videos.

    This is a placeholder action. Please select a provider
    (e.g., 'happyhorse_v1_1') configured in config.json.
    """
    return ActionResult(
        status="REJECTED",
        remark=(
            "No video generation provider selected. "
            "Please configure a provider in config.json (e.g., happyhorse_v1_1)."
        ),
        artifacts={},
        reject_code="MISSING_PROVIDER",
    )
