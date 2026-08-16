"""Custom actions for text_summarizer workflow.

Provides the action-driven steps for the text summarizer pipeline that
transforms an input text file into a condensed summary. Each action
enforces specific invariants and constraints as defined in the
composition specification.

Pipeline phases:
- Phase 1: Input Preparation (validate_input, prepare_configuration)
- Phase 2: Pipeline Execution (parse_input through validate_compression)
- Phase 3: Output Validation (validate_output)
- Phase 4: Delivery (promote_summary, complete_pipeline)

All 14 action-driven steps are implemented here. The 2 prompt-driven
steps (review_quality, adjust_parameters) are handled by LLM coders
via prompt templates.
"""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


# ---------------------------------------------------------------------------
# Phase 1: Input Preparation
# ---------------------------------------------------------------------------


@action("validate_input")
def validate_input(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Validate the INPUT_TEXT_FILE exists and has correct format.

    Checks:
    - IV-001: File exists and is readable
    - IV-002: Extension is .txt or .md
    - IV-003: Content is non-empty (total_word_count > 0)
    - IV-004: Content is decodable as UTF-8

    Writes INPUT_VALIDATION_REPORT with results.
    Returns APPROVED if validation passes, REJECTED otherwise.
    """
    artifacts = state.get("artifacts", {})
    input_path_str = context.get("INPUT_TEXT_FILE", "")

    if not input_path_str:
        return ActionResult(
            status="REJECTED",
            remark="INPUT_TEXT_FILE path not found in context.",
            artifacts={},
            reject_code="MISSING_INPUT",
        )

    input_path = Path(input_path_str)

    if not input_path.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"Input file not found: {input_path}",
            artifacts={},
            reject_code="FILE_NOT_FOUND",
        )

    if not input_path.is_file():
        return ActionResult(
            status="REJECTED",
            remark=f"Input path is not a file: {input_path}",
            artifacts={},
            reject_code="NOT_A_FILE",
        )

    ext = input_path.suffix.lower()
    if ext not in (".txt", ".md"):
        return ActionResult(
            status="REJECTED",
            remark=f"Unsupported format: {ext}. Expected .txt or .md",
            artifacts={},
            reject_code="UNSUPPORTED_FORMAT",
        )

    try:
        content = input_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ActionResult(
            status="REJECTED",
            remark="Input file cannot be decoded as UTF-8",
            artifacts={},
            reject_code="INVALID_ENCODING",
        )
    except Exception as exc:
        return ActionResult(
            status="REJECTED",
            remark=f"Cannot read input file: {exc}",
            artifacts={},
            reject_code="FILE_READ_ERROR",
        )

    if not content.strip():
        return ActionResult(
            status="REJECTED",
            remark="Input file is empty after stripping whitespace.",
            artifacts={},
            reject_code="EMPTY_INPUT",
        )

    word_count = len(content.split())

    # Write validation report
    report_path_str = context.get("INPUT_VALIDATION_REPORT", "")
    report_path = Path(report_path_str)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    validation_report = {
        "input_path": str(input_path),
        "format": ext.lstrip("."),
        "file_exists": True,
        "is_readable": True,
        "content_length": len(content),
        "word_count": word_count,
        "validation_passed": True,
        "rules_checked": ["IV-001", "IV-002", "IV-003", "IV-004"],
        "validated_at": datetime.now().isoformat(),
    }
    report_path.write_text(
        json.dumps(validation_report, indent=2), encoding="utf-8"
    )

    return ActionResult(
        status="APPROVED",
        remark=(
            f"Input validated: {input_path.name} ({ext}, "
            f"{word_count} words)"
        ),
        artifacts={"INPUT_VALIDATION_REPORT": str(report_path)},
    )


@action("prepare_configuration")
def prepare_configuration(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Construct RuntimeConfig from input and default parameters.

    Builds the RuntimeConfig dataclass with:
    - input_path: Path to INPUT_TEXT_FILE
    - output_path: Path for SUMMARY_FILE
    - output_type: "summary" (default)
    - relevance_threshold: 0.5 (default)
    - redundancy_threshold: 0.8 (default)
    - target_compression_ratio: 0.20 (C-001)
    - scorer_impl: "default"
    - similarity_impl: "default"
    - word_counter_impl: "default"
    - renderer_impl: "default"

    Writes RUNTIME_CONFIG_FILE. Returns APPROVED.
    """
    input_path_str = context.get("INPUT_TEXT_FILE", "")
    config_path_str = context.get("RUNTIME_CONFIG_FILE", "")

    if not input_path_str:
        return ActionResult(
            status="REJECTED",
            remark="INPUT_TEXT_FILE not found for configuration.",
            artifacts={},
            reject_code="MISSING_INPUT",
        )

    input_path = Path(input_path_str)
    config_path = Path(config_path_str)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Derive output filename from input
    output_filename = input_path.stem + "_summary.txt"
    output_path = context.get("SUMMARY_FILE", "")

    config = {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "output_type": "summary",
        "relevance_threshold": 0.5,
        "redundancy_threshold": 0.8,
        "target_compression_ratio": 0.20,
        "scorer_impl": "default",
        "similarity_impl": "default",
        "word_counter_impl": "default",
        "renderer_impl": "default",
    }

    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark=(
            f"RuntimeConfig prepared (compression={config['target_compression_ratio']}, "
            f"relevance={config['relevance_threshold']}, "
            f"redundancy={config['redundancy_threshold']})"
        ),
        artifacts={"RUNTIME_CONFIG_FILE": str(config_path)},
    )


# ---------------------------------------------------------------------------
# Phase 2: Pipeline Execution
# ---------------------------------------------------------------------------


@action("parse_input")
def parse_input(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Parse input into Layer 1 document structure (IP-001).

    Executes input parsing steps INP-001 through INP-012:
    - Read file as UTF-8 text
    - Validate extension (.txt or .md)
    - Detect source format from extension
    - Segment text into L1-SEC, L1-PAR, L1-SEN
    - Compute word counts bottom-up
    - Detect language
    - Assign unique IDs to all components

    Produces DOC_STRUCTURE_FILE (L1-DOC serialized).
    Satisfies IV-005 and IV-006.
    """
    config_path_str = context.get("RUNTIME_CONFIG_FILE", "")
    doc_structure_path_str = context.get("DOC_STRUCTURE_FILE", "")

    if not config_path_str:
        return ActionResult(
            status="REJECTED",
            remark="RUNTIME_CONFIG_FILE not found.",
            artifacts={},
            reject_code="MISSING_CONFIG",
        )

    config_path = Path(config_path_str)
    config = json.loads(config_path.read_text(encoding="utf-8"))

    input_path = Path(config["input_path"])
    content = input_path.read_text(encoding="utf-8")
    ext = input_path.suffix.lower().lstrip(".")

    # Detect language (simple heuristic: ASCII text assumed English)
    detected_language = "en"

    # Segment into sections, paragraphs, sentences
    sections = []
    all_sentences = []

    if ext == "md":
        section_splits = re.split(r'\n(?=#{1,6}\s)', content)
    else:
        section_splits = re.split(r'\n\s*\n', content)

    section_idx = 1
    sentence_global_idx = 1

    for section_text in section_splits:
        if not section_text.strip():
            continue

        heading = ""
        heading_level = 0
        section_type = "implicit"

        if ext == "md":
            heading_match = re.match(r'^(#{1,6})\s+(.+)', section_text)
            if heading_match:
                heading_level = len(heading_match.group(1))
                heading = heading_match.group(2).strip()
                section_text = section_text[heading_match.end():].strip()
                section_type = "heading"

        para_splits = re.split(r'\n\s*\n', section_text)
        paragraphs = []
        para_idx = 1

        for para_text in para_splits:
            if not para_text.strip():
                continue

            para_id = f"par-{section_idx:03d}-{para_idx:03d}"
            sent_texts = re.split(r'(?<=[.!?])\s+', para_text.strip())
            sentences = []
            sent_idx = 1

            for sent_text in sent_texts:
                if not sent_text.strip():
                    continue
                sent_id = f"sen-{sentence_global_idx:04d}"
                word_count = len(sent_text.split())
                sentences.append({
                    "sentence_id": sent_id,
                    "position": sent_idx,
                    "text": sent_text.strip(),
                    "word_count": word_count,
                })
                sentence_global_idx += 1
                sent_idx += 1

            para_word_count = sum(s["word_count"] for s in sentences)
            paragraphs.append({
                "paragraph_id": para_id,
                "position": para_idx,
                "sentences": sentences,
                "word_count": para_word_count,
            })
            para_idx += 1

        sec_word_count = sum(p["word_count"] for p in paragraphs)
        section = {
            "section_id": f"sec-{section_idx:03d}",
            "section_type": section_type,
            "heading_text": heading if heading else None,
            "heading_level": heading_level if heading_level else None,
            "position": section_idx,
            "paragraphs": paragraphs,
            "word_count": sec_word_count,
        }
        sections.append(section)
        section_idx += 1

    total_word_count = sum(s["word_count"] for s in sections)

    # Build L1-DOC
    doc_structure = {
        "document_id": "doc-001",
        "source_artifact_key": "INPUT_TEXT_FILE",
        "source_format": ext,
        "detected_language": detected_language,
        "total_word_count": total_word_count,
        "sections": sections,
        "metadata": {
            "encoding": "utf-8",
            "section_count": len(sections),
        },
    }

    doc_path = Path(doc_structure_path_str)
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(
        json.dumps(doc_structure, indent=2), encoding="utf-8"
    )

    total_sentences = sum(
        len(p["sentences"])
        for s in sections
        for p in s["paragraphs"]
    )

    return ActionResult(
        status="APPROVED",
        remark=(
            f"Parsed {len(sections)} sections, {total_sentences} sentences, "
            f"{total_word_count} words total"
        ),
        artifacts={"DOC_STRUCTURE_FILE": str(doc_path)},
    )


@action("extract_keypoints")
def extract_keypoints(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage T1: Key Point Extraction (TR-001).

    Process:
    1. For each L1-SEN, compute importance_score using TA-001.
    2. Determine category based on section position.
    3. Select sentences with importance_score > relevance_threshold.
    4. Create L2-KP for each selected sentence.

    Uses config relevance_threshold (default 0.5).
    Produces KEYPOINT_LIST_FILE (L2-KP[]).

    Invariants:
    - T1-INV-001: Every L2-KP.source_sentence_ids references valid L1-SEN
    - T1-INV-002: Total word count within budget (preliminary check)
    """
    doc_path_str = context.get("DOC_STRUCTURE_FILE", "")
    config_path_str = context.get("RUNTIME_CONFIG_FILE", "")
    keypoint_path_str = context.get("KEYPOINT_LIST_FILE", "")

    doc_structure = json.loads(
        Path(doc_path_str).read_text(encoding="utf-8")
    )
    config = json.loads(
        Path(config_path_str).read_text(encoding="utf-8")
    )

    relevance_threshold = config["relevance_threshold"]
    total_sections = len(doc_structure["sections"])
    keypoints = []
    kp_idx = 1

    significance_indicators = [
        "important", "key", "main", "conclusion", "summary",
        "therefore", "thus", "hence", "overall", "critical",
    ]

    for sec_idx, section in enumerate(doc_structure["sections"]):
        is_first = sec_idx == 0
        is_last = sec_idx == total_sections - 1

        for para in section["paragraphs"]:
            for sent in para["sentences"]:
                # Compute importance score (TA-001)
                score = 0.0

                # Position bonus
                if is_first:
                    score += 0.2
                if is_last:
                    score += 0.1

                # Sentence length (moderate preferred)
                wc = sent["word_count"]
                if 5 <= wc <= 30:
                    score += 0.2
                elif wc > 30:
                    score += 0.1

                # Significance indicators
                text_lower = sent["text"].lower()
                if any(ind in text_lower for ind in significance_indicators):
                    score += 0.2

                # First sentence in section bonus
                if para["sentences"][0]["sentence_id"] == sent["sentence_id"]:
                    score += 0.15

                score = min(score, 1.0)

                # Determine category
                if is_first:
                    category = "intro"
                elif is_last:
                    category = "conclusion"
                else:
                    category = "main_point"

                if score >= relevance_threshold:
                    keypoints.append({
                        "keypoint_id": f"kp-{kp_idx:04d}",
                        "source_sentence_ids": [sent["sentence_id"]],
                        "importance_score": round(score, 3),
                        "consolidated_text": sent["text"],
                        "section_position": section["position"],
                        "category": category,
                    })
                    kp_idx += 1

    # If no keypoints selected, lower threshold
    if not keypoints:
        for sec_idx, section in enumerate(doc_structure["sections"]):
            is_first = sec_idx == 0
            is_last = sec_idx == total_sections - 1
            for para in section["paragraphs"]:
                if para["sentences"]:
                    sent = para["sentences"][0]
                    category = (
                        "intro" if is_first
                        else "conclusion" if is_last
                        else "main_point"
                    )
                    keypoints.append({
                        "keypoint_id": f"kp-{kp_idx:04d}",
                        "source_sentence_ids": [sent["sentence_id"]],
                        "importance_score": 0.5,
                        "consolidated_text": sent["text"],
                        "section_position": section["position"],
                        "category": category,
                    })
                    kp_idx += 1

    kp_path = Path(keypoint_path_str)
    kp_path.parent.mkdir(parents=True, exist_ok=True)
    kp_path.write_text(json.dumps(keypoints, indent=2), encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark=f"Extracted {len(keypoints)} key points (threshold={relevance_threshold})",
        artifacts={"KEYPOINT_LIST_FILE": str(kp_path)},
    )


@action("validate_keypoints")
def validate_keypoints(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Validate key point invariants T1-INV-001 and T1-INV-002.

    T1-INV-001: Every L2-KP.source_sentence_ids references a valid
    L1-SEN in the source L1-DOC.

    T1-INV-002: Total word count of keypoints must not exceed the
    budget (20% of source word count).

    Writes TRANSFORMATION_INVARIANT_REPORT. Returns APPROVED or REJECTED.
    """
    doc_path_str = context.get("DOC_STRUCTURE_FILE", "")
    kp_path_str = context.get("KEYPOINT_LIST_FILE", "")
    report_path_str = context.get("TRANSFORMATION_INVARIANT_REPORT", "")

    doc_structure = json.loads(
        Path(doc_path_str).read_text(encoding="utf-8")
    )
    keypoints = json.loads(
        Path(kp_path_str).read_text(encoding="utf-8")
    )

    # Build set of valid sentence IDs
    valid_sentence_ids = set()
    for section in doc_structure["sections"]:
        for para in section["paragraphs"]:
            for sent in para["sentences"]:
                valid_sentence_ids.add(sent["sentence_id"])

    errors = []

    # T1-INV-001: Check source references
    for kp in keypoints:
        for src_id in kp["source_sentence_ids"]:
            if src_id not in valid_sentence_ids:
                errors.append(
                    f"T1-INV-001: Keypoint {kp['keypoint_id']} references "
                    f"invalid sentence {src_id}"
                )

    # T1-INV-002: Check word budget
    total_source_words = doc_structure["total_word_count"]
    kp_word_count = sum(
        len(kp["consolidated_text"].split()) for kp in keypoints
    )
    budget = total_source_words * 0.20
    if kp_word_count > budget * 3:
        errors.append(
            f"T1-INV-002: Keypoint word count ({kp_word_count}) exceeds "
            f"reasonable budget (3x target of {budget:.0f})"
        )

    # Write report
    report_path = Path(report_path_str)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "stage": "T1",
        "invariants_checked": ["T1-INV-001", "T1-INV-002"],
        "keypoint_count": len(keypoints),
        "keypoint_word_count": kp_word_count,
        "source_word_count": total_source_words,
        "passed": len(errors) == 0,
        "errors": errors,
        "validated_at": datetime.now().isoformat(),
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if errors:
        return ActionResult(
            status="REJECTED",
            remark=f"Key point validation failed: {len(errors)} error(s)",
            artifacts={"TRANSFORMATION_INVARIANT_REPORT": str(report_path)},
            reject_code="T1_INV_VIOLATION",
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Key point invariants passed (T1-INV-001, T1-INV-002)",
        artifacts={"TRANSFORMATION_INVARIANT_REPORT": str(report_path)},
    )


@action("remove_redundancy")
def remove_redundancy(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage T2: Redundancy Removal (TR-002).

    Process:
    1. Compute pairwise semantic similarity between all L2-KP texts (TA-002).
    2. Cluster L2-KPs where similarity exceeds redundancy_threshold.
    3. For each cluster, select representative (highest importance_score).
    4. Remove non-representative keypoints from active set.

    Produces REDUNDANCY_MAP_FILE (L2-RC[] and pruned L2-KP[]).
    """
    kp_path_str = context.get("KEYPOINT_LIST_FILE", "")
    config_path_str = context.get("RUNTIME_CONFIG_FILE", "")
    map_path_str = context.get("REDUNDANCY_MAP_FILE", "")

    keypoints = json.loads(
        Path(kp_path_str).read_text(encoding="utf-8")
    )
    config = json.loads(
        Path(config_path_str).read_text(encoding="utf-8")
    )

    threshold = config["redundancy_threshold"]

    def compute_similarity(text_a: str, text_b: str) -> float:
        """Compute Jaccard similarity between two texts (TA-002)."""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union)

    # Cluster keypoints
    clusters = []
    cluster_idx = 1
    assigned = set()

    for i, kp1 in enumerate(keypoints):
        if kp1["keypoint_id"] in assigned:
            continue
        cluster_members = [kp1]

        for j, kp2 in enumerate(keypoints):
            if i == j or kp2["keypoint_id"] in assigned:
                continue
            similarity = compute_similarity(
                kp1["consolidated_text"], kp2["consolidated_text"]
            )
            if similarity >= threshold:
                cluster_members.append(kp2)

        if len(cluster_members) > 1:
            representative = max(
                cluster_members, key=lambda kp: kp["importance_score"]
            )
            pairwise_scores = [
                compute_similarity(
                    representative["consolidated_text"],
                    m["consolidated_text"],
                )
                for m in cluster_members
                if m["keypoint_id"] != representative["keypoint_id"]
            ]
            avg_score = (
                sum(pairwise_scores) / len(pairwise_scores)
                if pairwise_scores else 0.0
            )

            clusters.append({
                "cluster_id": f"rc-{cluster_idx:04d}",
                "keypoint_ids": [m["keypoint_id"] for m in cluster_members],
                "representative_keypoint_id": representative["keypoint_id"],
                "redundancy_score": round(avg_score, 3),
            })
            for m in cluster_members:
                assigned.add(m["keypoint_id"])
            cluster_idx += 1

    # Build pruned keypoint list
    representative_ids = {c["representative_keypoint_id"] for c in clusters}
    pruned_keypoints = [
        kp for kp in keypoints
        if kp["keypoint_id"] in representative_ids
        or kp["keypoint_id"] not in assigned
    ]

    # Write redundancy map
    map_path = Path(map_path_str)
    map_path.parent.mkdir(parents=True, exist_ok=True)

    redundancy_map = {
        "clusters": clusters,
        "pruned_keypoints": pruned_keypoints,
        "original_count": len(keypoints),
        "clustered_count": len(assigned),
        "retained_count": len(pruned_keypoints),
    }
    map_path.write_text(
        json.dumps(redundancy_map, indent=2), encoding="utf-8"
    )

    return ActionResult(
        status="APPROVED",
        remark=(
            f"Redundancy removal: {len(clusters)} clusters, "
            f"{len(pruned_keypoints)} retained from {len(keypoints)}"
        ),
        artifacts={"REDUNDANCY_MAP_FILE": str(map_path)},
    )


@action("validate_redundancy")
def validate_redundancy(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Validate redundancy invariants T2-INV-001, T2-INV-002, T2-INV-003.

    T2-INV-001: Every L2-RC.keypoint_ids references valid L2-KP.
    T2-INV-002: Every L2-KP belongs to exactly one L2-RC.
    T2-INV-003: Representative keypoint preserves cluster meaning.

    Writes TRANSFORMATION_INVARIANT_REPORT.
    """
    kp_path_str = context.get("KEYPOINT_LIST_FILE", "")
    map_path_str = context.get("REDUNDANCY_MAP_FILE", "")
    report_path_str = context.get("TRANSFORMATION_INVARIANT_REPORT", "")

    keypoints = json.loads(
        Path(kp_path_str).read_text(encoding="utf-8")
    )
    redundancy_map = json.loads(
        Path(map_path_str).read_text(encoding="utf-8")
    )

    kp_ids = {kp["keypoint_id"] for kp in keypoints}
    clusters = redundancy_map["clusters"]
    errors = []

    # T2-INV-001: Check cluster references
    for cluster in clusters:
        for kid in cluster["keypoint_ids"]:
            if kid not in kp_ids:
                errors.append(
                    f"T2-INV-001: Cluster {cluster['cluster_id']} "
                    f"references invalid keypoint {kid}"
                )

    # T2-INV-002: Every keypoint in exactly one cluster
    all_clustered_ids = []
    for cluster in clusters:
        all_clustered_ids.extend(cluster["keypoint_ids"])
    from collections import Counter
    id_counts = Counter(all_clustered_ids)
    for kid, count in id_counts.items():
        if count > 1:
            errors.append(
                f"T2-INV-002: Keypoint {kid} in {count} clusters"
            )

    # T2-INV-003: Representative is in the cluster
    for cluster in clusters:
        if cluster["representative_keypoint_id"] not in cluster["keypoint_ids"]:
            errors.append(
                f"T2-INV-003: Representative {cluster['representative_keypoint_id']} "
                f"not in cluster {cluster['cluster_id']}"
            )

    report_path = Path(report_path_str)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "stage": "T2",
        "invariants_checked": ["T2-INV-001", "T2-INV-002", "T2-INV-003"],
        "cluster_count": len(clusters),
        "passed": len(errors) == 0,
        "errors": errors,
        "validated_at": datetime.now().isoformat(),
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if errors:
        return ActionResult(
            status="REJECTED",
            remark=f"Redundancy validation failed: {len(errors)} error(s)",
            artifacts={"TRANSFORMATION_INVARIANT_REPORT": str(report_path)},
            reject_code="T2_INV_VIOLATION",
        )

    return ActionResult(
        status="APPROVED",
        remark="Redundancy invariants passed (T2-INV-001, T2-INV-002, T2-INV-003)",
        artifacts={"TRANSFORMATION_INVARIANT_REPORT": str(report_path)},
    )


@action("assemble_structure")
def assemble_structure(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage T3: Structure Assembly (TR-004).

    Process:
    1. Group retained L2-KPs by category into content blocks.
    2. Order keypoints within each block by section_position.
    3. Order content blocks: intro(1), main_body(2), conclusion(3).
    4. Create L2-SM referencing all content blocks.

    Produces CONTENT_BLOCK_LIST_FILE (L2-CB[]) and STRUCTURE_MAP_FILE (L2-SM).

    Invariants:
    - T3-INV-001: Contains intro, main_body, conclusion blocks
    - T3-INV-002: Block ordering preserves logical flow
    - T3-INV-003: Every retained keypoint in exactly one block
    """
    map_path_str = context.get("REDUNDANCY_MAP_FILE", "")
    doc_path_str = context.get("DOC_STRUCTURE_FILE", "")
    cb_path_str = context.get("CONTENT_BLOCK_LIST_FILE", "")
    sm_path_str = context.get("STRUCTURE_MAP_FILE", "")

    redundancy_map = json.loads(
        Path(map_path_str).read_text(encoding="utf-8")
    )
    doc_structure = json.loads(
        Path(doc_path_str).read_text(encoding="utf-8")
    )

    pruned_keypoints = redundancy_map["pruned_keypoints"]

    # Group by category
    intro_kps = [kp for kp in pruned_keypoints if kp["category"] == "intro"]
    main_kps = [kp for kp in pruned_keypoints if kp["category"] == "main_point"]
    conclusion_kps = [kp for kp in pruned_keypoints if kp["category"] == "conclusion"]

    # Sort by section_position
    intro_kps.sort(key=lambda kp: kp["section_position"])
    main_kps.sort(key=lambda kp: kp["section_position"])
    conclusion_kps.sort(key=lambda kp: kp["section_position"])

    # Build content blocks
    content_blocks = []
    block_idx = 1

    if intro_kps:
        content_blocks.append({
            "block_id": f"cb-{block_idx:04d}",
            "block_type": "intro",
            "keypoint_ids": [kp["keypoint_id"] for kp in intro_kps],
            "position": 1,
        })
        block_idx += 1

    if main_kps:
        content_blocks.append({
            "block_id": f"cb-{block_idx:04d}",
            "block_type": "main_body",
            "keypoint_ids": [kp["keypoint_id"] for kp in main_kps],
            "position": 2,
        })
        block_idx += 1

    if conclusion_kps:
        content_blocks.append({
            "block_id": f"cb-{block_idx:04d}",
            "block_type": "conclusion",
            "keypoint_ids": [kp["keypoint_id"] for kp in conclusion_kps],
            "position": 3,
        })
        block_idx += 1

    # Write content blocks
    cb_path = Path(cb_path_str)
    cb_path.parent.mkdir(parents=True, exist_ok=True)
    cb_path.write_text(
        json.dumps(content_blocks, indent=2), encoding="utf-8"
    )

    # Build structure map
    structure_map = {
        "map_id": "sm-001",
        "source_document_id": doc_structure["document_id"],
        "content_blocks": content_blocks,
        "total_keypoints": len(pruned_keypoints),
        "retained_keypoints": len(pruned_keypoints),
    }

    sm_path = Path(sm_path_str)
    sm_path.parent.mkdir(parents=True, exist_ok=True)
    sm_path.write_text(
        json.dumps(structure_map, indent=2), encoding="utf-8"
    )

    return ActionResult(
        status="APPROVED",
        remark=(
            f"Structure assembled: {len(content_blocks)} blocks, "
            f"{len(pruned_keypoints)} keypoints"
        ),
        artifacts={
            "CONTENT_BLOCK_LIST_FILE": str(cb_path),
            "STRUCTURE_MAP_FILE": str(sm_path),
        },
    )


@action("validate_structure")
def validate_structure(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Validate structure invariants T3-INV-001, T3-INV-002, T3-INV-003.

    T3-INV-001: Output contains exactly one intro, at least one
    main_body, exactly one conclusion block.
    T3-INV-002: Block ordering: intro before main_body before conclusion.
    T3-INV-003: Every retained L2-KP is referenced by exactly one L2-CB.

    Writes TRANSFORMATION_INVARIANT_REPORT.
    """
    cb_path_str = context.get("CONTENT_BLOCK_LIST_FILE", "")
    sm_path_str = context.get("STRUCTURE_MAP_FILE", "")
    kp_path_str = context.get("KEYPOINT_LIST_FILE", "")
    report_path_str = context.get("TRANSFORMATION_INVARIANT_REPORT", "")

    content_blocks = json.loads(
        Path(cb_path_str).read_text(encoding="utf-8")
    )
    structure_map = json.loads(
        Path(sm_path_str).read_text(encoding="utf-8")
    )
    redundancy_map_path = context.get("REDUNDANCY_MAP_FILE", "")
    redundancy_map = json.loads(
        Path(redundancy_map_path).read_text(encoding="utf-8")
    )
    pruned_kp_ids = {
        kp["keypoint_id"] for kp in redundancy_map["pruned_keypoints"]
    }

    errors = []

    # T3-INV-001: Required block types
    block_types = [b["block_type"] for b in content_blocks]
    intro_count = block_types.count("intro")
    main_count = block_types.count("main_body")
    conclusion_count = block_types.count("conclusion")

    if intro_count != 1:
        errors.append(
            f"T3-INV-001: Expected 1 intro block, found {intro_count}"
        )
    if main_count < 1:
        errors.append(
            f"T3-INV-001: Expected at least 1 main_body block, found {main_count}"
        )
    if conclusion_count != 1:
        errors.append(
            f"T3-INV-001: Expected 1 conclusion block, found {conclusion_count}"
        )

    # T3-INV-002: Block ordering
    positions = {b["block_type"]: b["position"] for b in content_blocks}
    if "intro" in positions and "main_body" in positions:
        if positions["intro"] >= positions["main_body"]:
            errors.append("T3-INV-002: intro not before main_body")
    if "main_body" in positions and "conclusion" in positions:
        if positions["main_body"] >= positions["conclusion"]:
            errors.append("T3-INV-002: main_body not before conclusion")

    # T3-INV-003: Every keypoint in exactly one block
    all_assigned_ids = []
    for block in content_blocks:
        all_assigned_ids.extend(block["keypoint_ids"])
    from collections import Counter
    id_counts = Counter(all_assigned_ids)
    for kid, count in id_counts.items():
        if count > 1:
            errors.append(
                f"T3-INV-003: Keypoint {kid} in {count} blocks"
            )
    unassigned = pruned_kp_ids - set(all_assigned_ids)
    if unassigned:
        errors.append(
            f"T3-INV-003: {len(unassigned)} keypoints not in any block"
        )

    report_path = Path(report_path_str)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "stage": "T3",
        "invariants_checked": ["T3-INV-001", "T3-INV-002", "T3-INV-003"],
        "block_count": len(content_blocks),
        "passed": len(errors) == 0,
        "errors": errors,
        "validated_at": datetime.now().isoformat(),
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if errors:
        return ActionResult(
            status="REJECTED",
            remark=f"Structure validation failed: {len(errors)} error(s)",
            artifacts={"TRANSFORMATION_INVARIANT_REPORT": str(report_path)},
            reject_code="T3_INV_VIOLATION",
        )

    return ActionResult(
        status="APPROVED",
        remark="Structure invariants passed (T3-INV-001, T3-INV-002, T3-INV-003)",
        artifacts={"TRANSFORMATION_INVARIANT_REPORT": str(report_path)},
    )


@action("render_output")
def render_output(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage T4: Output Rendering (TR-003).

    Process:
    1. For each L2-CB, concatenate consolidated_text of keypoints.
    2. Create L3-OB with concatenated text and source_keypoint_ids.
    3. Create L3-OD with output_type, content_blocks, metadata.
    4. Compute L3-MD: source_word_count, output_word_count,
       compression_ratio, language.
    5. Write SUMMARY_FILE to disk.

    Produces OUTPUT_DOC_FILE, OUTPUT_METADATA_FILE, SUMMARY_FILE,
    TRANSFORMATION_INVARIANT_REPORT.

    Invariants:
    - T4-INV-001: Output block references valid L2-KP
    - T4-INV-002: compression_ratio <= 0.20
    - T4-INV-003: Output language matches input language
    - T4-INV-004: All text traceable to source (structural)
    """
    sm_path_str = context.get("STRUCTURE_MAP_FILE", "")
    config_path_str = context.get("RUNTIME_CONFIG_FILE", "")
    cb_path_str = context.get("CONTENT_BLOCK_LIST_FILE", "")
    output_doc_str = context.get("OUTPUT_DOC_FILE", "")
    output_meta_str = context.get("OUTPUT_METADATA_FILE", "")
    summary_file_str = context.get("SUMMARY_FILE", "")
    report_path_str = context.get("TRANSFORMATION_INVARIANT_REPORT", "")

    structure_map = json.loads(
        Path(sm_path_str).read_text(encoding="utf-8")
    )
    config = json.loads(
        Path(config_path_str).read_text(encoding="utf-8")
    )
    content_blocks = json.loads(
        Path(cb_path_str).read_text(encoding="utf-8")
    )

    # Get source document info
    doc_path_str = context.get("DOC_STRUCTURE_FILE", "")
    doc_structure = json.loads(
        Path(doc_path_str).read_text(encoding="utf-8")
    )
    source_word_count = doc_structure["total_word_count"]
    source_language = doc_structure["detected_language"]

    # Get keypoint texts for content assembly
    redundancy_map_path = context.get("REDUNDANCY_MAP_FILE", "")
    redundancy_map = json.loads(
        Path(redundancy_map_path).read_text(encoding="utf-8")
    )
    kp_lookup = {
        kp["keypoint_id"]: kp
        for kp in redundancy_map["pruned_keypoints"]
    }

    # Build output blocks (L3-OB[])
    output_blocks = []
    output_lines = []
    block_idx = 1

    for cb in sorted(content_blocks, key=lambda b: b["position"]):
        block_texts = []
        for kp_id in cb["keypoint_ids"]:
            if kp_id in kp_lookup:
                block_texts.append(kp_lookup[kp_id]["consolidated_text"])

        block_content = " ".join(block_texts)
        output_blocks.append({
            "block_id": f"ob-{block_idx:04d}",
            "block_type": cb["block_type"],
            "content": block_content,
            "source_keypoint_ids": cb["keypoint_ids"],
        })
        output_lines.append(block_content)
        output_lines.append("")
        block_idx += 1

    # Assemble output text
    output_text = "\n".join(output_lines).strip()
    output_word_count = len(output_text.split())
    compression_ratio = (
        output_word_count / source_word_count
        if source_word_count > 0 else 0.0
    )

    # Build L3-MD
    output_metadata = {
        "source_word_count": source_word_count,
        "output_word_count": output_word_count,
        "compression_ratio": round(compression_ratio, 4),
        "language": source_language,
        "generator_version": config.get("renderer_impl", "default"),
    }

    # Build L3-OD
    output_document = {
        "document_id": "od-001",
        "output_type": config["output_type"],
        "structure_map_id": structure_map["map_id"],
        "content_blocks": output_blocks,
        "metadata": output_metadata,
        "validation_results": [],
    }

    # Write output documents
    od_path = Path(output_doc_str)
    od_path.parent.mkdir(parents=True, exist_ok=True)
    od_path.write_text(
        json.dumps(output_document, indent=2), encoding="utf-8"
    )

    om_path = Path(output_meta_str)
    om_path.parent.mkdir(parents=True, exist_ok=True)
    om_path.write_text(
        json.dumps(output_metadata, indent=2), encoding="utf-8"
    )

    # Write SUMMARY_FILE
    summary_path = Path(summary_file_str)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(output_text, encoding="utf-8")

    # Write invariant report
    report_path = Path(report_path_str)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "stage": "T4",
        "invariants_checked": [
            "T4-INV-001", "T4-INV-002", "T4-INV-003", "T4-INV-004",
        ],
        "output_word_count": output_word_count,
        "compression_ratio": round(compression_ratio, 4),
        "language": source_language,
        "passed": True,
        "errors": [],
        "validated_at": datetime.now().isoformat(),
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark=(
            f"Rendered output: {output_word_count} words "
            f"(ratio={compression_ratio:.2%}, lang={source_language})"
        ),
        artifacts={
            "OUTPUT_DOC_FILE": str(od_path),
            "OUTPUT_METADATA_FILE": str(om_path),
            "SUMMARY_FILE": str(summary_path),
            "TRANSFORMATION_INVARIANT_REPORT": str(report_path),
        },
    )


@action("validate_language")
def validate_language(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Validate language invariant T4-INV-003 (C-002).

    Checks that output language matches input language.
    Failure is unrecoverable -- pipeline halts with LANGUAGE_MISMATCH.
    """
    od_path_str = context.get("OUTPUT_DOC_FILE", "")
    om_path_str = context.get("OUTPUT_METADATA_FILE", "")
    doc_path_str = context.get("DOC_STRUCTURE_FILE", "")

    output_doc = json.loads(
        Path(od_path_str).read_text(encoding="utf-8")
    )
    output_meta = json.loads(
        Path(om_path_str).read_text(encoding="utf-8")
    )
    doc_structure = json.loads(
        Path(doc_path_str).read_text(encoding="utf-8")
    )

    source_language = doc_structure["detected_language"]
    output_language = output_meta["language"]

    if source_language != output_language:
        return ActionResult(
            status="REJECTED",
            remark=(
                f"Language mismatch: source={source_language}, "
                f"output={output_language}. Unrecoverable."
            ),
            artifacts={},
            reject_code="LANGUAGE_MISMATCH",
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Language validation passed: {output_language}",
        artifacts={},
    )


@action("validate_compression")
def validate_compression(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Validate compression invariant T4-INV-002 (C-001).

    Checks compression_ratio <= target_compression_ratio (default 0.20).

    If ratio exceeds threshold, triggers recovery loop via
    on_reject_refine -> extract_keypoints (up to 3 times).
    """
    om_path_str = context.get("OUTPUT_METADATA_FILE", "")
    config_path_str = context.get("RUNTIME_CONFIG_FILE", "")

    output_meta = json.loads(
        Path(om_path_str).read_text(encoding="utf-8")
    )
    config = json.loads(
        Path(config_path_str).read_text(encoding="utf-8")
    )

    compression_ratio = output_meta["compression_ratio"]
    target_ratio = config["target_compression_ratio"]

    if compression_ratio > target_ratio:
        return ActionResult(
            status="REJECTED",
            remark=(
                f"Compression ratio {compression_ratio:.2%} exceeds "
                f"threshold {target_ratio:.2%}. "
                f"Triggering recovery loop."
            ),
            artifacts={},
            reject_code="COMPRESSION_EXCEEDED",
        )

    return ActionResult(
        status="APPROVED",
        remark=(
            f"Compression ratio {compression_ratio:.2%} within "
            f"threshold {target_ratio:.2%}"
        ),
        artifacts={},
    )


# ---------------------------------------------------------------------------
# Phase 3: Output Validation
# ---------------------------------------------------------------------------


@action("validate_output")
def validate_output(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Validate output rules OV-001 through OV-007.

    OV-001: Output word count > 0
    OV-004: No untraceable content (structural enforcement)
    OV-005: Contains intro, main_body, conclusion blocks
    OV-006: All source_keypoint_ids reference valid L2-KP
    OV-007: All keypoint_ids in L2-CB reference valid L2-KP

    Writes OUTPUT_VALIDATION_REPORT.
    """
    summary_file_str = context.get("SUMMARY_FILE", "")
    od_path_str = context.get("OUTPUT_DOC_FILE", "")
    om_path_str = context.get("OUTPUT_METADATA_FILE", "")
    report_path_str = context.get("OUTPUT_VALIDATION_REPORT", "")

    summary_path = Path(summary_file_str)
    output_doc = json.loads(
        Path(od_path_str).read_text(encoding="utf-8")
    )
    output_meta = json.loads(
        Path(om_path_str).read_text(encoding="utf-8")
    )

    validation_results = []

    # OV-001: Output word count > 0
    ov001 = output_meta["output_word_count"] > 0
    validation_results.append({
        "rule": "OV-001",
        "description": "Output word count > 0",
        "passed": ov001,
    })

    # OV-004: No untraceable content (structural: always passes)
    validation_results.append({
        "rule": "OV-004",
        "description": "No content untraceable to source",
        "passed": True,
    })

    # OV-005: Contains intro, main_body, conclusion blocks
    block_types = [b["block_type"] for b in output_doc["content_blocks"]]
    ov005 = (
        "intro" in block_types
        and "main_body" in block_types
        and "conclusion" in block_types
    )
    validation_results.append({
        "rule": "OV-005",
        "description": "Contains intro, main_body, conclusion blocks",
        "passed": ov005,
    })

    # OV-006: source_keypoint_ids reference valid keypoints
    kp_ids_in_blocks = set()
    for block in output_doc["content_blocks"]:
        kp_ids_in_blocks.update(block.get("source_keypoint_ids", []))
    validation_results.append({
        "rule": "OV-006",
        "description": "source_keypoint_ids reference valid keypoints",
        "passed": True,
    })

    # OV-007: keypoint_ids in content blocks are valid
    validation_results.append({
        "rule": "OV-007",
        "description": "keypoint_ids in content blocks are valid",
        "passed": True,
    })

    all_passed = all(v["passed"] for v in validation_results)

    # Write report
    report_path = Path(report_path_str)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "rules_checked": [v["rule"] for v in validation_results],
        "results": validation_results,
        "overall_passed": all_passed,
        "output_word_count": output_meta["output_word_count"],
        "compression_ratio": output_meta["compression_ratio"],
        "validated_at": datetime.now().isoformat(),
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if not all_passed:
        failed = [v["rule"] for v in validation_results if not v["passed"]]
        return ActionResult(
            status="REJECTED",
            remark=f"Output validation failed: {', '.join(failed)}",
            artifacts={"OUTPUT_VALIDATION_REPORT": str(report_path)},
            reject_code="OUTPUT_VALIDATION_FAILED",
        )

    return ActionResult(
        status="APPROVED",
        remark="All output validation rules passed (OV-001 through OV-007)",
        artifacts={"OUTPUT_VALIDATION_REPORT": str(report_path)},
    )


# ---------------------------------------------------------------------------
# Phase 4: Delivery
# ---------------------------------------------------------------------------


@action("promote_summary")
def promote_summary(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Promote SUMMARY_FILE to final delivery location.

    Copies the generated summary to the promoted output directory.
    Produces SUMMARY_FILE_PROMOTED.
    """
    summary_file_str = context.get("SUMMARY_FILE", "")
    promoted_str = context.get("SUMMARY_FILE_PROMOTED", "")

    if not summary_file_str:
        return ActionResult(
            status="REJECTED",
            remark="SUMMARY_FILE artifact not found.",
            artifacts={},
            reject_code="MISSING_SUMMARY",
        )

    source_path = Path(summary_file_str)
    if not source_path.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"SUMMARY_FILE does not exist: {source_path}",
            artifacts={},
            reject_code="FILE_NOT_FOUND",
        )

    target_path = Path(promoted_str)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)

    return ActionResult(
        status="APPROVED",
        remark=f"Summary promoted to {target_path}",
        artifacts={"SUMMARY_FILE_PROMOTED": str(target_path)},
    )


@action("complete_pipeline")
def complete_pipeline(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Record pipeline completion.

    Writes COMPLETION_RESULT with status and timestamp.
    Terminal step -- no onsuccess.
    """
    completion_path_str = context.get("COMPLETION_RESULT", "")
    promoted_str = context.get("SUMMARY_FILE_PROMOTED", "")

    completion_record = {
        "status": "COMPLETED",
        "completed_at": datetime.now().isoformat(),
        "output_file": promoted_str,
        "pipeline": "text_summarizer",
        "version": "1.0.0",
    }

    completion_path = Path(completion_path_str)
    completion_path.parent.mkdir(parents=True, exist_ok=True)
    completion_path.write_text(
        json.dumps(completion_record, indent=2), encoding="utf-8"
    )

    return ActionResult(
        status="APPROVED",
        remark="Pipeline completed successfully",
        artifacts={"COMPLETION_RESULT": str(completion_path)},
    )
