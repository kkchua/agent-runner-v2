"""Implementation-specific actions for key_points variant.

Provides render_list_output action that formats key points as a numbered list
with importance scores.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


@action("render_list_output")
def render_list_output(*, context, state, step_cfg, project_root):
    """Render TRANSFORMED_CONTENT JSON containing key_points as a formatted numbered list with importance scores."""
    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    # Resolve TRANSFORMED_CONTENT path
    transformed_path_str = context.get("TRANSFORMED_CONTENT")
    if not transformed_path_str:
        return ActionResult(
            status="REJECTED",
            remark="TRANSFORMED_CONTENT not found in context",
            artifacts={},
            reject_code="MISSING_ARTIFACT",
        )

    transformed_path = Path(transformed_path_str)
    if not transformed_path.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"TRANSFORMED_CONTENT file not found: {transformed_path}",
            artifacts={},
            reject_code="MISSING_ARTIFACT",
        )

    # Load JSON content
    try:
        content_text = transformed_path.read_text(encoding="utf-8")
        transformed_data = json.loads(content_text)
    except json.JSONDecodeError as e:
        return ActionResult(
            status="REJECTED",
            remark=f"TRANSFORMED_CONTENT is not valid JSON: {e}",
            artifacts={},
            reject_code="INVALID_STRUCTURE",
        )
    except OSError as e:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to read TRANSFORMED_CONTENT: {e}",
            artifacts={},
            reject_code="MISSING_ARTIFACT",
        )

    # Validate JSON structure
    if not isinstance(transformed_data, dict):
        return ActionResult(
            status="REJECTED",
            remark="TRANSFORMED_CONTENT JSON must be an object",
            artifacts={},
            reject_code="INVALID_STRUCTURE",
        )

    if "key_points" not in transformed_data:
        return ActionResult(
            status="REJECTED",
            remark="TRANSFORMED_CONTENT JSON missing required field: key_points",
            artifacts={},
            reject_code="INVALID_STRUCTURE",
        )

    key_points = transformed_data["key_points"]
    if not isinstance(key_points, list):
        return ActionResult(
            status="REJECTED",
            remark="key_points field must be an array",
            artifacts={},
            reject_code="INVALID_STRUCTURE",
        )

    if len(key_points) == 0:
        return ActionResult(
            status="REJECTED",
            remark="key_points array is empty",
            artifacts={},
            reject_code="EMPTY_CONTENT",
        )

    # Validate each key point has required fields
    for i, point in enumerate(key_points):
        if not isinstance(point, dict):
            return ActionResult(
                status="REJECTED",
                remark=f"key_points[{i}] is not an object",
                artifacts={},
                reject_code="INVALID_STRUCTURE",
            )
        if "text" not in point:
            return ActionResult(
                status="REJECTED",
                remark=f"key_points[{i}] missing required field: text",
                artifacts={},
                reject_code="INVALID_STRUCTURE",
            )
        if "importance_score" not in point:
            return ActionResult(
                status="REJECTED",
                remark=f"key_points[{i}] missing required field: importance_score",
                artifacts={},
                reject_code="INVALID_STRUCTURE",
            )
        if not isinstance(point["text"], str) or not point["text"].strip():
            return ActionResult(
                status="REJECTED",
                remark=f"key_points[{i}].text is empty or not a string",
                artifacts={},
                reject_code="INVALID_STRUCTURE",
            )

    # Sort by importance_score descending
    sorted_points = sorted(key_points, key=lambda p: p.get("importance_score", 0.0), reverse=True)

    # Format each point as: "{rank}. [{score}] {text}"
    lines = []
    for rank, point in enumerate(sorted_points, start=1):
        score = point["importance_score"]
        text = point["text"].strip()
        lines.append(f"{rank}. [{score:.2f}] {text}")

    formatted_output = "\n\n".join(lines)

    # Write to OUTPUT_FILE
    output_path_str = context.get("OUTPUT_FILE")
    if not output_path_str:
        return ActionResult(
            status="REJECTED",
            remark="OUTPUT_FILE output path not found in context",
            artifacts={},
            reject_code="MISSING_OUTPUT_PATH",
        )

    output_path = Path(output_path_str)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(formatted_output, encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark=f"Rendered {len(sorted_points)} key points as numbered list with importance scores. Written to OUTPUT_FILE.",
        artifacts={"OUTPUT_FILE": str(output_path)},
    )
