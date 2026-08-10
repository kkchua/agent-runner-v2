"""Action functions for key_points implementation variant.

Contains action implementations specific to the key_points output variant.
These functions override the default (summary) implementations for the
render_output and validate_output steps.

Overridden steps:
  Step 5: render_key_points  -- Renders ordered list with importance scores
  Step 6: validate_key_points -- Validates key_points output against OV rules

Steps NOT overridden (inherited from workflow.toml / shared actions.py):
  Step 1: parse_input_document
  Step 2: analyze_structure (prompt)
  Step 3: score_importance (prompt)
  Step 4: identify_core_message (prompt)
  Step 7: step_completion
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# =============================================================================
# Step 5: render_key_points (key_points override)
# Implements EP-003 OutputRenderer Protocol
# =============================================================================

def render_key_points(
    state: dict[str, Any],
    ctx: dict[str, str],
    step_cfg: dict[str, Any],
) -> dict[str, Any]:
    """Render ordered list of key points with importance scores.

    Selects non-redundant segments sorted by importance descending.
    Each key point preserves the original text verbatim (OV-007).
    Satisfies OR-002 rendering rules.

    Returns an OutputDocument as a JSON-serializable dict.
    """
    analysis_result = _load_json_artifact(state, ctx, "ANALYSIS_RESULT")
    parsed_doc = _load_json_artifact(state, ctx, "PARSED_DOCUMENT")

    doc_ctx = parsed_doc["document_context"]
    analyzed_segments = analysis_result["analyzed_segments"]

    # Select non-redundant segments, sorted by importance descending
    candidates = [
        a for a in analyzed_segments
        if not a.get("is_redundant", False)
    ]
    candidates.sort(
        key=lambda a: a.get("importance_score", 0.0), reverse=True
    )

    # Limit to configured maximum (default 10)
    max_points = step_cfg.get("key_points_max_count", 10)
    candidates = candidates[:max_points]

    # Build KeyPointContentBlocks
    content_blocks = []
    for rank, an_seg in enumerate(candidates, start=1):
        content_blocks.append({
            "rank": rank,
            "original_text": an_seg["original_content"],
            "importance_score": an_seg["importance_score"],
            "source_segment_id": an_seg["segment_id"],
        })

    # Compute output word count
    output_word_count = sum(
        len(block["original_text"].split()) for block in content_blocks
    )
    source_word_count = doc_ctx["source_word_count"]
    compression_ratio = (
        output_word_count / source_word_count
        if source_word_count > 0
        else 0.0
    )

    metadata = {
        "source_language": doc_ctx["source_language"],
        "source_word_count": source_word_count,
        "output_word_count": output_word_count,
        "compression_ratio": round(compression_ratio, 4),
        "implementation": "key_points",
        "generation_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    output_document = {
        "output_type": "key_points",
        "metadata": metadata,
        "content_blocks": content_blocks,
        "validation_status": "pass",
    }

    return output_document


# =============================================================================
# Step 6: validate_key_points (key_points override)
# Implements EP-004 ValidationStrategy Protocol
# =============================================================================

def validate_key_points(
    state: dict[str, Any],
    ctx: dict[str, str],
    step_cfg: dict[str, Any],
) -> dict[str, Any]:
    """Validate key_points output against applicable OV rules.

    Checks:
      OV-002: Source language preserved
      OV-003: No new information (segment ID reference check)
      OV-004: Core message retained
      OV-006: Points ordered by importance descending
      OV-007: Original wording preserved (no paraphrase)
      OV-008: All importance scores valid in [0.0, 1.0]
      OV-009: Single coherent document

    Also writes the final OUTPUT_KEY_POINTS file.
    Returns a ValidationResult as a JSON-serializable dict.
    """
    output_doc = _load_json_artifact(state, ctx, "OUTPUT_DOCUMENT")
    parsed_doc = _load_json_artifact(state, ctx, "PARSED_DOCUMENT")
    analysis_result = _load_json_artifact(state, ctx, "ANALYSIS_RESULT")

    violations: list[dict[str, str]] = []

    # OV-002: Source language preserved
    if (
        output_doc["metadata"]["source_language"]
        != parsed_doc["document_context"]["source_language"]
    ):
        violations.append({
            "rule_id": "OV-002",
            "code": "LANGUAGE_MISMATCH",
            "detail": (
                f"Expected {parsed_doc['document_context']['source_language']}, "
                f"got {output_doc['metadata']['source_language']}"
            ),
        })

    # OV-003: No new information
    valid_ids = {s["segment_id"] for s in parsed_doc["text_segments"]}
    for block in output_doc.get("content_blocks", []):
        if block.get("source_segment_id") not in valid_ids:
            violations.append({
                "rule_id": "OV-003",
                "code": "NEW_INFO_DETECTED",
                "detail": (
                    f"Key point references unknown segment: "
                    f"{block.get('source_segment_id')}"
                ),
            })

    # OV-004: Core message retained
    core_seg_ids = {
        a["segment_id"]
        for a in analysis_result.get("analyzed_segments", [])
        if a.get("is_core_message")
    }
    output_seg_ids = {
        b["source_segment_id"]
        for b in output_doc.get("content_blocks", [])
    }
    if not (output_seg_ids & core_seg_ids):
        violations.append({
            "rule_id": "OV-004",
            "code": "CORE_MESSAGE_LOST",
            "detail": "No key point references the core message segment",
        })

    # OV-006: Ranking order (descending importance)
    scores = [
        b["importance_score"]
        for b in output_doc.get("content_blocks", [])
    ]
    for i in range(len(scores) - 1):
        if scores[i] < scores[i + 1]:
            violations.append({
                "rule_id": "OV-006",
                "code": "RANKING_INVALID",
                "detail": (
                    f"Score at rank {i + 1} ({scores[i]}) < "
                    f"rank {i + 2} ({scores[i + 1]})"
                ),
            })
            break

    # OV-007: Original wording preserved
    seg_lookup = {
        s["segment_id"]: s for s in parsed_doc["text_segments"]
    }
    for block in output_doc.get("content_blocks", []):
        source_seg = seg_lookup.get(block.get("source_segment_id"))
        if source_seg and block["original_text"] != source_seg["content"]:
            violations.append({
                "rule_id": "OV-007",
                "code": "PARAPHRASE_DETECTED",
                "detail": (
                    f"Segment {block.get('source_segment_id')}: "
                    f"output text differs from source"
                ),
            })

    # OV-008: Score validity (0.0 to 1.0)
    for block in output_doc.get("content_blocks", []):
        score = block.get("importance_score", 0.0)
        if not (0.0 <= score <= 1.0):
            violations.append({
                "rule_id": "OV-008",
                "code": "SCORE_INVALID",
                "detail": (
                    f"Rank {block.get('rank')}: "
                    f"score {score} out of [0.0, 1.0]"
                ),
            })

    # OV-009: Single coherent document
    if not output_doc.get("content_blocks"):
        violations.append({
            "rule_id": "OV-009",
            "code": "FRAGMENTED_OUTPUT",
            "detail": "Output has no content blocks",
        })

    status = "pass" if not violations else "fail"

    # Write output file
    _write_key_points_file(output_doc, state, ctx)

    validation_result = {
        "status": status,
        "violations": violations,
    }

    return validation_result


# =============================================================================
# Internal Helpers
# =============================================================================

def _load_json_artifact(
    state: dict[str, Any],
    ctx: dict[str, str],
    artifact_key: str,
) -> dict[str, Any]:
    """Load a JSON artifact from disk using the resolved path."""
    artifacts = state.get("artifacts") or {}
    artifact_path = artifacts.get(artifact_key, "")
    if not artifact_path:
        artifact_path = ctx.get(artifact_key, "")
    if not artifact_path:
        raise FileNotFoundError(
            f"Artifact {artifact_key} not found in state or context"
        )
    path = Path(artifact_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Artifact file not found: {artifact_path}"
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_key_points_file(
    output_doc: dict[str, Any],
    state: dict[str, Any],
    ctx: dict[str, str],
) -> None:
    """Write key_points output as numbered list to OUTPUT_KEY_POINTS path."""
    artifacts = state.get("artifacts") or {}
    output_path = artifacts.get("OUTPUT_KEY_POINTS", "")
    if not output_path:
        output_path = ctx.get("OUTPUT_KEY_POINTS", "")
    if not output_path:
        return

    lines: list[str] = []
    blocks = sorted(
        output_doc.get("content_blocks", []),
        key=lambda b: b.get("rank", 0),
    )
    for block in blocks:
        lines.append(
            f"{block['rank']}. {block['original_text']} "
            f"[importance: {block['importance_score']:.2f}]"
        )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
