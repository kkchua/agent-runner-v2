"""Guardrail validators for agnes_media_gen_v1 workflow.

Validates image inputs before LLM vision processing to prevent
unnecessary API calls on oversized images.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def pre_check(
    *,
    step: str,
    step_cfg: dict[str, Any],
    state: dict[str, Any],
    prepared: Any,
) -> tuple[bool, str | None, str | None]:
    """Validate inputs before step execution.

    For extract_descriptions step: validates that input images
    do not exceed the configured size limit.

    Returns:
        Tuple of (is_valid, reject_reason_or_none, reject_code_or_none)
    """
    if step != "extract_descriptions":
        return True, None, None

    # Get max image size from step config or use default (2MB)
    max_size_mb = step_cfg.get("extra", {}).get("max_image_size_mb", 2)
    max_bytes = max_size_mb * 1024 * 1024

    # Get image folder from prepared context
    image_folder = prepared.context.get("STEP_00_DIR", "")
    if not image_folder:
        # No image folder configured, skip validation
        return True, None, None

    image_path = Path(image_folder)
    if not image_path.exists():
        return False, f"Image folder not found: {image_folder}", "IMAGE_FOLDER_MISSING"

    # Check all images in the folder
    oversized_images = []
    image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}

    for img_file in image_path.iterdir():
        if not img_file.is_file():
            continue
        if img_file.suffix.lower() not in image_extensions:
            continue
        try:
            file_size = img_file.stat().st_size
            if file_size > max_bytes:
                size_mb = file_size / (1024 * 1024)
                oversized_images.append(f"{img_file.name} ({size_mb:.2f}MB)")
        except OSError:
            continue

    if oversized_images:
        images_str = ", ".join(oversized_images)
        return (
            False,
            f"Images exceed {max_size_mb}MB size limit: {images_str}. "
            f"Please resize images before processing.",
            "IMAGE_TOO_LARGE",
        )

    return True, None, None


def post_check(
    *,
    step: str,
    step_cfg: dict[str, Any],
    state: dict[str, Any],
    step_result: Any,
) -> tuple[bool, str | None, str | None]:
    """Validate outputs after step execution.

    For generate_images/generate_videos steps: could validate
    that output files exist and have expected sizes.

    Returns:
        Tuple of (is_valid, reject_reason_or_none, reject_code_or_none)
    """
    # Currently no post-execution validation required
    # Future: validate output files exist and have content
    return True, None, None
