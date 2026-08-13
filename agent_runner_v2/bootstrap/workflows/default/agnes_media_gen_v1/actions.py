"""Shared actions and utilities for agnes_media_gen_v1 workflow.

Provides reusable helpers for media generation workflows (config loading,
API retry logic, index writing, filename sequencing). Specific providers
(e.g., Agnes, HappyHorse) should be implemented in the `impls/` folder.
"""
from __future__ import annotations

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
# Default Stubs
# ============================================================================

@action("generate_images_default")
def generate_images_default(*, context, state, step_cfg, project_root) -> ActionResult:
    """Default action for generate_images.

    This is a placeholder action. Please select an implementation
    (e.g., 'agnes_media_v1') or implement a specific provider action.
    """
    return ActionResult(
        status="REJECTED",
        remark="No image generation provider selected. Please configure an implementation (e.g., agnes_media_v1).",
        artifacts={},
        reject_code="MISSING_IMPLEMENTATION",
    )


@action("generate_videos_default")
def generate_videos_default(*, context, state, step_cfg, project_root) -> ActionResult:
    """Default action for generate_videos.

    This is a placeholder action. Please select an implementation
    (e.g., 'agnes_media_v1') or implement a specific provider action.
    """
    return ActionResult(
        status="REJECTED",
        remark="No video generation provider selected. Please configure an implementation (e.g., agnes_media_v1).",
        artifacts={},
        reject_code="MISSING_IMPLEMENTATION",
    )
