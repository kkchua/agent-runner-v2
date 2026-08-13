"""Domain actions for agnes_gen_video_v1.

Provides generic/shared actions and helpers for video generation workflows.
Specific providers (e.g., Agnes, Sora) should be implemented in the `impls/` folder.
"""
from __future__ import annotations

import json
import logging
import struct
from pathlib import Path
from typing import Any

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action

logger = logging.getLogger(__name__)


def _extract_prompts_from_png(png_path: Path) -> dict[str, str]:
    """Extract t2i_prompt1 and t2i_prompt2 from PNG metadata (ComfyUI).

    This is a shared utility as input format is consistent across the workflow.
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

                        break  # Found the prompt chunk

            pos += 12 + length

    except (OSError, json.JSONDecodeError, struct.error) as exc:
        logger.warning("Failed to extract prompts from %s: %s", png_path.name, exc)

    return prompts


@action("generate_videos_default")
def generate_videos_default(
    *, context, state, step_cfg, project_root
) -> ActionResult:
    """Default action for generate_videos.

    This is a placeholder action. Please select an implementation
    (e.g., 'agnes_v2') or implement a specific provider action.
    """
    return ActionResult(
        status="REJECTED",
        remark="No video generation provider selected. Please configure an implementation (e.g., agnes_v2).",
        artifacts={},
        reject_code="MISSING_IMPLEMENTATION",
    )
