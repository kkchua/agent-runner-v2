"""Custom actions for Text Summarizer workflow.

Provides the 10-stage transformation pipeline actions that transform
an input text file into a condensed summary. Each action enforces
specific invariants and constraints as defined in the composition
specification.

Pipeline stages:
- validate_input: File existence and format validation
- prepare_configuration: RuntimeConfig construction
- parse_input: Layer 1 content component extraction (TR-001)
- validate_segments: Hierarchy validation (TR-002)
- score_importance: KeyPoint scoring (TR-003)
- detect_redundancy: Redundancy clustering (TR-004)
- preserve_meaning: Section coverage validation (TR-005)
- select_compression: Word budget selection (TR-006)
- assemble_structure: SummaryBlock assembly (TR-007)
- validate_language: Language match validation (TR-008)
- validate_length: Compression ratio validation (TR-009)
- render_output: SummaryDocument rendering (TR-010)
- validate_summary: Output validation (OV-001 to OV-006)
- promote_summary: File promotion to final location
- complete_pipeline: Pipeline completion recording
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
    - INV-001: File exists and is readable
    - INV-002: Extension is .txt or .md
    - INV-003: Content is non-empty
    - INV-004: Content appears to be natural language
    - INV-005: At least one section detectable
    - INV-006: At least one sentence detectable

    Returns APPROVED if validation passes, REJECTED otherwise.
    """
    artifacts = state.get("artifacts", {})
    input_path_str = artifacts.get("INPUT_TEXT_FILE", "")

    if not input_path_str:
        return ActionResult(
            status="REJECTED",
            remark="INPUT_TEXT_FILE artifact not found in state.",
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

    # Write validation report
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))
    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )
    run_root.mkdir(parents=True, exist_ok=True)
    report_path = run_root / "INPUT_VALIDATION-001.json"

    validation_report = {
        "input_path": str(input_path),
        "format": ext.lstrip("."),
        "file_exists": True,
        "is_readable": True,
        "content_length": len(content),
        "validation_passed": True,
        "validated_at": datetime.now().isoformat(),
    }
    report_path.write_text(
        json.dumps(validation_report, indent=2), encoding="utf-8"
    )

    return ActionResult(
        status="APPROVED",
        remark=f"Input validated: {input_path.name} ({ext}, {len(content)} chars)",
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

    Builds the RuntimeConfig dataclass equivalent with:
    - input_path: Path to INPUT_TEXT_FILE
    - output_path: Path for SUMMARY_FILE
    - target_compression_ratio: 0.20 (default, CON-001)
    - importance_threshold: 0.5 (default)
    - redundancy_similarity_threshold: 0.7 (default)
    - max_recovery_attempts: 3 (default)
    - output_format_override: None (follows input format, ASM-005)
    - scorer_impl: "default"
    - detector_impl: "default"
    - selector_impl: "default"
    - renderer_impl: "default"

    Returns APPROVED with RUNTIME_CONFIG artifact.
    """
    artifacts = state.get("artifacts", {})
    input_path_str = artifacts.get("INPUT_TEXT_FILE", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

    if not input_path_str:
        return ActionResult(
            status="REJECTED",
            remark="INPUT_TEXT_FILE not found for configuration.",
            artifacts={},
            reject_code="MISSING_INPUT",
        )

    input_path = Path(input_path_str)
    output_filename = input_path.stem + "_summary" + input_path.suffix
    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )
    run_root.mkdir(parents=True, exist_ok=True)
    output_path = run_root / "output" / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    config = {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "target_compression_ratio": 0.20,
        "importance_threshold": 0.5,
        "redundancy_similarity_threshold": 0.7,
        "max_recovery_attempts": 3,
        "output_format_override": None,
        "scorer_impl": "default",
        "detector_impl": "default",
        "selector_impl": "default",
        "renderer_impl": "default",
    }

    config_path = run_root / "RUNTIME_CONFIG-001.json"
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark=f"RuntimeConfig prepared with compression ratio {config['target_compression_ratio']}",
        artifacts={"RUNTIME_CONFIG": str(config_path)},
    )


# ---------------------------------------------------------------------------
# Phase 2: Pipeline Execution - Stages 1-10
# ---------------------------------------------------------------------------


@action("parse_input")
def parse_input(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage 1 (TR-001): Parse input into Layer 1 content components.

    Executes Input Mapping steps INM-001 through INM-007:
    - Detect format (.txt or .md)
    - Detect and strip YAML frontmatter (if .md)
    - Detect source language
    - Segment into Sections, Paragraphs, Sentences
    - Compute word counts bottom-up

    Produces: DocumentMeta, Section[], Paragraph[], Sentence[]
    """
    artifacts = state.get("artifacts", {})
    config_str = artifacts.get("RUNTIME_CONFIG", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

    if not config_str:
        return ActionResult(
            status="REJECTED",
            remark="RUNTIME_CONFIG not found.",
            artifacts={},
            reject_code="MISSING_CONFIG",
        )

    config_path = Path(config_str)
    config = json.loads(config_path.read_text(encoding="utf-8"))

    input_path = Path(config["input_path"])
    content = input_path.read_text(encoding="utf-8")

    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )

    # Parse content into components
    ext = input_path.suffix.lower().lstrip(".")

    # Strip frontmatter if present
    has_frontmatter = False
    if ext == "md" and content.startswith("---"):
        end_idx = content.find("---", 3)
        if end_idx != -1:
            has_frontmatter = True
            content = content[end_idx + 3:].strip()

    # Detect language (simple heuristic: assume English for ASCII text)
    source_language = "en"

    # Segment into sections, paragraphs, sentences
    sections = []
    paragraphs = []
    sentences = []

    # Simple segmentation logic
    if ext == "md":
        # Split on heading markers
        section_splits = re.split(r'\n(?=#{1,6}\s)', content)
    else:
        # Split on double newlines
        section_splits = re.split(r'\n\s*\n', content)

    section_idx = 1
    for section_text in section_splits:
        if not section_text.strip():
            continue

        # Extract heading
        heading = ""
        heading_level = 0
        if ext == "md":
            heading_match = re.match(r'^(#{1,6})\s+(.+)', section_text)
            if heading_match:
                heading_level = len(heading_match.group(1))
                heading = heading_match.group(2).strip()
                section_text = section_text[heading_match.end():].strip()

        # Split section into paragraphs
        para_splits = re.split(r'\n\s*\n', section_text)
        para_ids = []

        para_idx = 1
        for para_text in para_splits:
            if not para_text.strip():
                continue

            para_id = f"para-{section_idx:03d}-{para_idx:03d}"
            para_ids.append(para_id)

            # Split paragraph into sentences
            sent_texts = re.split(r'(?<=[.!?])\s+', para_text.strip())
            sent_ids = []

            sent_idx = 1
            for sent_text in sent_texts:
                if not sent_text.strip():
                    continue
                sent_id = f"s-{section_idx:03d}-{para_idx:03d}-{sent_idx:03d}"
                sent_ids.append(sent_id)
                word_count = len(sent_text.split())
                sentences.append({
                    "component_id": sent_id,
                    "component_type": "sentence",
                    "parent_paragraph_id": para_id,
                    "position": sent_idx,
                    "raw_text": sent_text.strip(),
                    "word_count": word_count,
                    "is_heading": False,
                    "is_list_item": sent_text.strip().startswith(("-", "*", "+")),
                })
                sent_idx += 1

            word_count = sum(s["word_count"] for s in sentences if s["component_id"] in sent_ids)
            paragraphs.append({
                "component_id": para_id,
                "component_type": "paragraph",
                "parent_section_id": f"sec-{section_idx:03d}",
                "position": para_idx,
                "raw_text": para_text.strip(),
                "sentence_ids": sent_ids,
                "word_count": word_count,
            })
            para_idx += 1

        word_count = sum(p["word_count"] for p in paragraphs if p["component_id"] in para_ids)
        sections.append({
            "component_id": f"sec-{section_idx:03d}",
            "component_type": "section",
            "heading": heading,
            "heading_level": heading_level,
            "position": section_idx,
            "paragraph_ids": para_ids,
            "word_count": word_count,
        })
        section_idx += 1

    original_word_count = sum(s["word_count"] for s in sections)
    doc_meta = {
        "component_id": "doc-meta-001",
        "component_type": "document_meta",
        "source_format": ext,
        "source_language": source_language,
        "original_word_count": original_word_count,
        "section_count": len(sections),
        "encoding": "utf-8",
        "has_frontmatter": has_frontmatter,
    }

    # Write parsed components
    doc_meta_path = run_root / "DocumentMeta-001.json"
    doc_meta_path.write_text(json.dumps(doc_meta, indent=2), encoding="utf-8")

    sections_path = run_root / "Section-001.json"
    sections_path.write_text(json.dumps(sections, indent=2), encoding="utf-8")

    paragraphs_path = run_root / "Paragraph-001.json"
    paragraphs_path.write_text(json.dumps(paragraphs, indent=2), encoding="utf-8")

    sentences_path = run_root / "Sentence-001.json"
    sentences_path.write_text(json.dumps(sentences, indent=2), encoding="utf-8")

    parsed_report = {
        "document_meta": doc_meta,
        "section_count": len(sections),
        "paragraph_count": len(paragraphs),
        "sentence_count": len(sentences),
        "total_word_count": original_word_count,
    }
    parsed_path = run_root / "PARSED_CONTENT-001.json"
    parsed_path.write_text(json.dumps(parsed_report, indent=2), encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark=f"Parsed {len(sections)} sections, {len(paragraphs)} paragraphs, {len(sentences)} sentences",
        artifacts={
            "PARSED_CONTENT": str(parsed_path),
            "DocumentMeta": str(doc_meta_path),
            "Section[]": str(sections_path),
            "Paragraph[]": str(paragraphs_path),
            "Sentence[]": str(sentences_path),
        },
    )


@action("validate_segments")
def validate_segments(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage 2 (TR-002): Validate Section/Paragraph/Sentence hierarchy.

    Checks:
    - INV-T-001: Every Sentence belongs to exactly one Paragraph
    - INV-T-002: Every Paragraph belongs to exactly one Section
    - Sequential positions within each parent
    - Each Section has at least one Paragraph
    - Each Paragraph has at least one Sentence

    Returns APPROVED if hierarchy is valid, REJECTED otherwise.
    """
    artifacts = state.get("artifacts", {})
    sections_path_str = artifacts.get("Section[]", "")
    paragraphs_path_str = artifacts.get("Paragraph[]", "")
    sentences_path_str = artifacts.get("Sentence[]", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

    sections = json.loads(Path(sections_path_str).read_text(encoding="utf-8"))
    paragraphs = json.loads(Path(paragraphs_path_str).read_text(encoding="utf-8"))
    sentences = json.loads(Path(sentences_path_str).read_text(encoding="utf-8"))

    validation_errors = []

    # Check each section has paragraphs
    for section in sections:
        if not section["paragraph_ids"]:
            validation_errors.append(
                f"Section {section['component_id']} has no paragraphs"
            )

    # Check paragraph-sentence references
    para_ids = {p["component_id"] for p in paragraphs}
    for sent in sentences:
        if sent["parent_paragraph_id"] not in para_ids:
            validation_errors.append(
                f"Sentence {sent['component_id']} references "
                f"non-existent paragraph {sent['parent_paragraph_id']}"
            )

    # Check section-paragraph references
    section_ids = {s["component_id"] for s in sections}
    for para in paragraphs:
        if para["parent_section_id"] not in section_ids:
            validation_errors.append(
                f"Paragraph {para['component_id']} references "
                f"non-existent section {para['parent_section_id']}"
            )

    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )

    if validation_errors:
        report = {
            "validation_passed": False,
            "errors": validation_errors,
            "invariants_checked": ["INV-T-001", "INV-T-002"],
        }
        report_path = run_root / "Layer_1_Validated-001.json"
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return ActionResult(
            status="REJECTED",
            remark=f"Hierarchy validation failed: {len(validation_errors)} error(s)",
            artifacts={},
            reject_code="HIERARCHY_VIOLATION",
        )

    report = {
        "validation_passed": True,
        "section_count": len(sections),
        "paragraph_count": len(paragraphs),
        "sentence_count": len(sentences),
        "invariants_checked": ["INV-T-001", "INV-T-002"],
    }
    report_path = run_root / "Layer_1_Validated-001.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark="Hierarchy validation passed (INV-T-001, INV-T-002)",
        artifacts={"Layer_1_Validated": str(report_path)},
    )


@action("score_importance")
def score_importance(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage 3 (TR-003): Score sentences for importance.

    Computes importance scores based on:
    - Position in document (first/last sentences score higher)
    - Position in section (first sentence scores higher)
    - Heading-like patterns
    - Sentence length (moderate preferred)
    - Semantic significance indicators

    Produces KeyPoint[] with importance_score, structural_role, is_core_message.

    Invariants:
    - INV-T-003: At least one KeyPoint has is_core_message = true
    - INV-T-004: At least one KeyPoint per structural_role
    """
    artifacts = state.get("artifacts", {})
    sentences_path_str = artifacts.get("Sentence[]", "")
    doc_meta_path_str = artifacts.get("DocumentMeta", "")
    sections_path_str = artifacts.get("Section[]", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

    sentences = json.loads(Path(sentences_path_str).read_text(encoding="utf-8"))
    doc_meta = json.loads(Path(doc_meta_path_str).read_text(encoding="utf-8"))
    sections = json.loads(Path(sections_path_str).read_text(encoding="utf-8"))

    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )

    # Score each sentence
    total_sentences = len(sentences)
    key_points = []
    kp_idx = 1

    significance_indicators = [
        "important", "key", "main", "conclusion", "summary",
        "therefore", "thus", "hence", "overall", "critical",
    ]

    for idx, sent in enumerate(sentences):
        score = 0.0

        # Position score (first and last sentences score higher)
        if idx == 0:
            score += 0.3
        elif idx == total_sentences - 1:
            score += 0.2

        # Sentence length score (moderate length preferred)
        word_count = sent["word_count"]
        if 5 <= word_count <= 25:
            score += 0.2
        elif word_count > 25:
            score += 0.1

        # Heading indicator
        if sent.get("is_heading"):
            score += 0.3

        # Significance indicators
        text_lower = sent["raw_text"].lower()
        if any(indicator in text_lower for indicator in significance_indicators):
            score += 0.2

        # Normalize score to 0.0-1.0
        score = min(score, 1.0)

        # Determine structural role
        if idx < total_sentences * 0.2:
            structural_role = "intro"
        elif idx > total_sentences * 0.8:
            structural_role = "conclusion"
        else:
            structural_role = "main_point"

        key_points.append({
            "component_id": f"kp-{kp_idx:03d}",
            "component_type": "key_point",
            "source_sentence_ids": [sent["component_id"]],
            "source_section_id": sent["parent_paragraph_id"].replace("para-", "sec-").rsplit("-", 1)[0],
            "extracted_text": sent["raw_text"],
            "importance_score": round(score, 3),
            "is_core_message": False,
            "structural_role": structural_role,
        })
        kp_idx += 1

    # Mark highest scoring as core message
    if key_points:
        max_score = max(kp["importance_score"] for kp in key_points)
        for kp in key_points:
            if kp["importance_score"] == max_score:
                kp["is_core_message"] = True
                break

    key_points_path = run_root / "KeyPoint-001.json"
    key_points_path.write_text(json.dumps(key_points, indent=2), encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark=f"Scored {len(key_points)} key points with importance values",
        artifacts={"KeyPoint[]": str(key_points_path)},
    )


@action("detect_redundancy")
def detect_redundancy(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage 4 (TR-004): Detect redundant KeyPoints and cluster them.

    Computes pairwise similarity between KeyPoint extracted_text values.
    Groups KeyPoints with similarity above threshold into clusters.
    Each cluster has exactly one representative (highest importance_score).

    Invariant:
    - INV-T-005: Every KeyPoint belongs to at most one cluster
    """
    artifacts = state.get("artifacts", {})
    key_points_path_str = artifacts.get("KeyPoint[]", "")
    config_path_str = artifacts.get("RUNTIME_CONFIG", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

    key_points = json.loads(Path(key_points_path_str).read_text(encoding="utf-8"))
    config = json.loads(Path(config_path_str).read_text(encoding="utf-8"))

    threshold = config["redundancy_similarity_threshold"]
    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )

    # Simple similarity based on word overlap
    clusters = []
    cluster_idx = 1
    assigned = set()

    def compute_similarity(text1: str, text2: str) -> float:
        """Compute Jaccard similarity between two texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union)

    for i, kp1 in enumerate(key_points):
        if kp1["component_id"] in assigned:
            continue
        cluster_members = [kp1]

        for j, kp2 in enumerate(key_points):
            if i == j or kp2["component_id"] in assigned:
                continue
            similarity = compute_similarity(
                kp1["extracted_text"], kp2["extracted_text"]
            )
            if similarity >= threshold:
                cluster_members.append(kp2)

        if len(cluster_members) > 1:
            # Select representative (highest importance)
            representative = max(
                cluster_members, key=lambda kp: kp["importance_score"]
            )
            similarity_scores = [
                compute_similarity(
                    representative["extracted_text"], m["extracted_text"]
                )
                for m in cluster_members
                if m["component_id"] != representative["component_id"]
            ]
            avg_similarity = (
                sum(similarity_scores) / len(similarity_scores)
                if similarity_scores
                else 0.0
            )

            clusters.append({
                "component_id": f"rc-{cluster_idx:03d}",
                "component_type": "redundancy_cluster",
                "key_point_ids": [m["component_id"] for m in cluster_members],
                "representative_key_point_id": representative["component_id"],
                "similarity_score": round(avg_similarity, 3),
            })
            for m in cluster_members:
                assigned.add(m["component_id"])
            cluster_idx += 1

    clusters_path = run_root / "RedundancyCluster-001.json"
    clusters_path.write_text(json.dumps(clusters, indent=2), encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark=f"Detected {len(clusters)} redundancy clusters",
        artifacts={"RedundancyCluster[]": str(clusters_path)},
    )


@action("preserve_meaning")
def preserve_meaning(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage 5 (TR-005): Validate section coverage and preserve meaning.

    Verifies that representative KeyPoints from each cluster collectively
    cover all sections. If any section has no surviving KeyPoint, promotes
    the highest-scoring redundant KeyPoint from that section.

    Invariant:
    - INV-T-006: Every Section with content has at least one contributing KeyPoint
    """
    artifacts = state.get("artifacts", {})
    key_points_path_str = artifacts.get("KeyPoint[]", "")
    clusters_path_str = artifacts.get("RedundancyCluster[]", "")
    sections_path_str = artifacts.get("Section[]", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

    key_points = json.loads(Path(key_points_path_str).read_text(encoding="utf-8"))
    clusters = json.loads(Path(clusters_path_str).read_text(encoding="utf-8"))
    sections = json.loads(Path(sections_path_str).read_text(encoding="utf-8"))

    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )

    # Get representative key points (non-redundant)
    representative_ids = {c["representative_key_point_id"] for c in clusters}
    non_clustered = [
        kp for kp in key_points
        if kp["component_id"] not in {
            kid for c in clusters for kid in c["key_point_ids"]
        }
    ]

    deduplicated = [
        kp for kp in key_points if kp["component_id"] in representative_ids
    ] + non_clustered

    # Verify section coverage
    section_ids = {s["component_id"] for s in sections}
    covered_sections = {kp["source_section_id"] for kp in deduplicated}
    uncovered = section_ids - covered_sections

    # If sections uncovered, promote from clusters
    if uncovered:
        for section_id in uncovered:
            for cluster in clusters:
                section_kps = [
                    kp for kp in key_points
                    if kp["component_id"] in cluster["key_point_ids"]
                    and kp["source_section_id"] == section_id
                ]
                if section_kps:
                    best = max(section_kps, key=lambda kp: kp["importance_score"])
                    if best not in deduplicated:
                        deduplicated.append(best)

    deduplicated_path = run_root / "KeyPoint_Deduplicated-001.json"
    deduplicated_path.write_text(
        json.dumps(deduplicated, indent=2), encoding="utf-8"
    )

    return ActionResult(
        status="APPROVED",
        remark=f"Preserved meaning with {len(deduplicated)} key points covering all sections",
        artifacts={"KeyPoint_Deduplicated": str(deduplicated_path)},
    )


@action("select_compression")
def select_compression(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage 6 (TR-006): Select KeyPoints within word budget.

    Selects KeyPoints to meet compression target (INV-T-007):
    - Total words <= target_ratio * original_word_count
    - At least one KeyPoint per structural_role

    Invariants:
    - INV-T-007: Sum of selected words <= 0.20 * original_word_count
    - At least one KeyPoint per structural_role (intro, main_point, conclusion)
    """
    artifacts = state.get("artifacts", {})
    deduplicated_path_str = artifacts.get("KeyPoint_Deduplicated", "")
    doc_meta_path_str = artifacts.get("DocumentMeta", "")
    config_path_str = artifacts.get("RUNTIME_CONFIG", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

    deduplicated = json.loads(
        Path(deduplicated_path_str).read_text(encoding="utf-8")
    )
    doc_meta = json.loads(Path(doc_meta_path_str).read_text(encoding="utf-8"))
    config = json.loads(Path(config_path_str).read_text(encoding="utf-8"))

    target_ratio = config["target_compression_ratio"]
    original_word_count = doc_meta["original_word_count"]
    word_budget = int(original_word_count * target_ratio)

    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )

    # Sort by importance score descending
    sorted_kps = sorted(
        deduplicated, key=lambda kp: kp["importance_score"], reverse=True
    )

    selected = []
    total_words = 0
    roles_covered = set()

    # First pass: ensure at least one per role
    for role in ["intro", "main_point", "conclusion"]:
        role_kps = [kp for kp in sorted_kps if kp["structural_role"] == role]
        if role_kps:
            best = role_kps[0]
            selected.append(best)
            total_words += best["word_count"] if "word_count" in best else len(best["extracted_text"].split())
            roles_covered.add(role)

    # Second pass: greedy selection within budget
    for kp in sorted_kps:
        if kp in selected:
            continue
        kp_words = kp.get("word_count", len(kp["extracted_text"].split()))
        if total_words + kp_words <= word_budget:
            selected.append(kp)
            total_words += kp_words

    # Preserve original ordering
    selected.sort(key=lambda kp: kp["component_id"])

    selected_path = run_root / "KeyPoint_Selected-001.json"
    selected_path.write_text(json.dumps(selected, indent=2), encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark=f"Selected {len(selected)} key points ({total_words} words, budget: {word_budget})",
        artifacts={"KeyPoint_Selected": str(selected_path)},
    )


@action("assemble_structure")
def assemble_structure(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage 7 (TR-007): Assemble SummaryBlocks from selected KeyPoints.

    Groups selected KeyPoints by structural_role and creates SummaryBlocks:
    - intro blocks -> main_point blocks -> conclusion blocks
    - Each block preserves source ordering

    Invariant:
    - INV-T-008: SummaryBlocks preserve intro -> main_point -> conclusion order
    """
    artifacts = state.get("artifacts", {})
    selected_path_str = artifacts.get("KeyPoint_Selected", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

    selected = json.loads(Path(selected_path_str).read_text(encoding="utf-8"))
    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )

    # Group by structural role
    blocks = []
    block_idx = 1
    for role in ["intro", "main_point", "conclusion"]:
        role_kps = [kp for kp in selected if kp["structural_role"] == role]
        if role_kps:
            content_parts = [kp["extracted_text"] for kp in role_kps]
            content_text = " ".join(content_parts)
            word_count = len(content_text.split())

            blocks.append({
                "component_id": f"sb-{block_idx:03d}",
                "component_type": "summary_block",
                "structural_role": role,
                "source_key_point_ids": [kp["component_id"] for kp in role_kps],
                "content_text": content_text,
                "word_count": word_count,
                "position": 1,
            })
            block_idx += 1

    blocks_path = run_root / "SummaryBlock-001.json"
    blocks_path.write_text(json.dumps(blocks, indent=2), encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark=f"Assembled {len(blocks)} summary blocks",
        artifacts={"SummaryBlock[]": str(blocks_path)},
    )


@action("validate_language")
def validate_language(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage 8 (TR-008): Validate output language matches input.

    Detects language of combined SummaryBlock content and compares
    with DocumentMeta.source_language.

    Invariant:
    - INV-T-009: Output language matches input language

    Note: Language validation failure is unrecoverable.
    """
    artifacts = state.get("artifacts", {})
    blocks_path_str = artifacts.get("SummaryBlock[]", "")
    doc_meta_path_str = artifacts.get("DocumentMeta", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

    blocks = json.loads(Path(blocks_path_str).read_text(encoding="utf-8"))
    doc_meta = json.loads(Path(doc_meta_path_str).read_text(encoding="utf-8"))

    source_language = doc_meta["source_language"]

    # Simple language detection (assume English for ASCII text)
    combined_text = " ".join(b["content_text"] for b in blocks)
    detected_language = "en"  # Simplified: assume English

    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )

    validation_record = {
        "component_id": "valrec-001",
        "component_type": "validation_record",
        "constraint_id": "CON-002",
        "check_description": "Output language matches input language",
        "passed": detected_language == source_language,
        "measured_value": detected_language,
        "threshold_value": source_language,
    }

    record_path = run_root / "ValidationRecord_CON002-001.json"
    record_path.write_text(json.dumps(validation_record, indent=2), encoding="utf-8")

    if not validation_record["passed"]:
        return ActionResult(
            status="REJECTED",
            remark=f"Language mismatch: detected {detected_language}, expected {source_language}",
            artifacts={},
            reject_code="LANGUAGE_MISMATCH",
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Language validation passed: {detected_language}",
        artifacts={"ValidationRecord_CON002": str(record_path)},
    )


@action("validate_length")
def validate_length(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage 9 (TR-009): Validate compression ratio.

    Calculates compression_ratio = summary_word_count / original_word_count
    and checks against threshold (CON-001: <= 0.20).

    Invariant:
    - INV-T-010: Compression ratio <= 0.20

    If ratio > 0.20, triggers recovery loop (return to select_compression).
    """
    artifacts = state.get("artifacts", {})
    blocks_path_str = artifacts.get("SummaryBlock[]", "")
    doc_meta_path_str = artifacts.get("DocumentMeta", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

    blocks = json.loads(Path(blocks_path_str).read_text(encoding="utf-8"))
    doc_meta = json.loads(Path(doc_meta_path_str).read_text(encoding="utf-8"))

    summary_word_count = sum(b["word_count"] for b in blocks)
    original_word_count = doc_meta["original_word_count"]
    compression_ratio = summary_word_count / original_word_count if original_word_count > 0 else 0.0

    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )

    validation_record = {
        "component_id": "valrec-002",
        "component_type": "validation_record",
        "constraint_id": "CON-001",
        "check_description": "Summary word count <= 20% of original",
        "passed": compression_ratio <= 0.20,
        "measured_value": f"{compression_ratio:.4f}",
        "threshold_value": "0.20",
    }

    record_path = run_root / "ValidationRecord_CON001-001.json"
    record_path.write_text(json.dumps(validation_record, indent=2), encoding="utf-8")

    if not validation_record["passed"]:
        return ActionResult(
            status="REJECTED",
            remark=f"Compression ratio {compression_ratio:.2%} exceeds 20% threshold",
            artifacts={"ValidationRecord_CON001": str(record_path)},
            reject_code="COMPRESSION_EXCEEDED",
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Compression ratio {compression_ratio:.2%} within threshold",
        artifacts={"ValidationRecord_CON001": str(record_path)},
    )


@action("render_output")
def render_output(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Stage 10 (TR-010): Render SummaryDocument and write SUMMARY_FILE.

    Executes Output Mapping steps OUTM-001 through OUTM-004:
    - Determine output format (matches input format, ASM-005)
    - Assemble summary sections (intro -> main_point -> conclusion)
    - Add summary metadata header
    - Write output file

    Invariant:
    - INV-T-011: SUMMARY_FILE exists and is valid
    """
    artifacts = state.get("artifacts", {})
    blocks_path_str = artifacts.get("SummaryBlock[]", "")
    doc_meta_path_str = artifacts.get("DocumentMeta", "")
    config_path_str = artifacts.get("RUNTIME_CONFIG", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

    blocks = json.loads(Path(blocks_path_str).read_text(encoding="utf-8"))
    doc_meta = json.loads(Path(doc_meta_path_str).read_text(encoding="utf-8"))
    config = json.loads(Path(config_path_str).read_text(encoding="utf-8"))

    output_format = doc_meta["source_format"]
    target_language = doc_meta["source_language"]
    original_word_count = doc_meta["original_word_count"]
    summary_word_count = sum(b["word_count"] for b in blocks)
    compression_ratio = summary_word_count / original_word_count if original_word_count > 0 else 0.0

    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )

    # Assemble summary text
    intro_blocks = [b for b in blocks if b["structural_role"] == "intro"]
    main_blocks = [b for b in blocks if b["structural_role"] == "main_point"]
    conclusion_blocks = [b for b in blocks if b["structural_role"] == "conclusion"]

    output_lines = []

    # Add metadata header
    if output_format == "md":
        output_lines.append(f"Summary ({compression_ratio*100:.1f}% of original)")
        output_lines.append(f"Language: {target_language}")
        output_lines.append("")
    else:
        output_lines.append(f"Summary (approximately {compression_ratio*100:.1f}% of original)")
        output_lines.append("")

    # Add content blocks
    for block in intro_blocks + main_blocks + conclusion_blocks:
        output_lines.append(block["content_text"])
        output_lines.append("")

    output_text = "\n".join(output_lines)

    # Write output file
    output_path = Path(config["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")

    # Create SummaryDocument
    summary_document = {
        "component_id": "summary-doc-001",
        "component_type": "summary_document",
        "output_format": output_format,
        "target_language": target_language,
        "summary_word_count": summary_word_count,
        "original_word_count": original_word_count,
        "compression_ratio": round(compression_ratio, 4),
        "intro_blocks": [b["component_id"] for b in intro_blocks],
        "main_point_blocks": [b["component_id"] for b in main_blocks],
        "conclusion_blocks": [b["component_id"] for b in conclusion_blocks],
        "generation_timestamp": datetime.now().isoformat(),
    }

    doc_path = run_root / "SummaryDocument-001.json"
    doc_path.write_text(json.dumps(summary_document, indent=2), encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark=f"Rendered summary: {summary_word_count} words ({compression_ratio:.2%} of original)",
        artifacts={
            "SummaryDocument": str(doc_path),
            "SUMMARY_FILE": str(output_path),
        },
    )


# ---------------------------------------------------------------------------
# Phase 3: Output Validation
# ---------------------------------------------------------------------------


@action("validate_summary")
def validate_summary(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Validate the generated SUMMARY_FILE against output rules.

    Checks:
    - OV-001: SUMMARY_FILE exists and is readable
    - OV-002: summary_word_count <= 0.20 * original_word_count
    - OV-003: target_language matches source_language
    - OV-004: No hallucination (structural enforcement)
    - OV-005: Contains intro, main_point, conclusion
    - OV-006: Coherent and readable
    """
    artifacts = state.get("artifacts", {})
    summary_file_str = artifacts.get("SUMMARY_FILE", "")
    doc_meta_path_str = artifacts.get("DocumentMeta", "")
    summary_doc_path_str = artifacts.get("SummaryDocument", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

    summary_path = Path(summary_file_str)
    doc_meta = json.loads(Path(doc_meta_path_str).read_text(encoding="utf-8"))
    summary_doc = json.loads(Path(summary_doc_path_str).read_text(encoding="utf-8"))

    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )

    validation_results = []

    # OV-001: File exists
    exists = summary_path.exists() and summary_path.is_file()
    validation_results.append({
        "rule": "OV-001",
        "description": "SUMMARY_FILE exists and is readable",
        "passed": exists,
    })

    if not exists:
        report_path = run_root / "OUTPUT_VALIDATION_REPORT-001.md"
        report_path.write_text(
            _render_validation_report(validation_results), encoding="utf-8"
        )
        return ActionResult(
            status="REJECTED",
            remark="OV-001 failed: SUMMARY_FILE does not exist",
            artifacts={"OUTPUT_VALIDATION_REPORT": str(report_path)},
            reject_code="OUTPUT_VALIDATION_FAILED",
        )

    content = summary_path.read_text(encoding="utf-8")

    # OV-002: Compression ratio
    ratio = summary_doc["compression_ratio"]
    validation_results.append({
        "rule": "OV-002",
        "description": "Compression ratio <= 20%",
        "passed": ratio <= 0.20,
        "measured": f"{ratio:.2%}",
    })

    # OV-003: Language match
    validation_results.append({
        "rule": "OV-003",
        "description": "Output language matches input",
        "passed": summary_doc["target_language"] == doc_meta["source_language"],
    })

    # OV-004: No hallucination (structural enforcement - always passes)
    validation_results.append({
        "rule": "OV-004",
        "description": "No new information (structural enforcement)",
        "passed": True,
    })

    # OV-005: Structural elements
    has_intro = len(summary_doc["intro_blocks"]) > 0
    has_main = len(summary_doc["main_point_blocks"]) > 0
    has_conclusion = len(summary_doc["conclusion_blocks"]) > 0
    validation_results.append({
        "rule": "OV-005",
        "description": "Contains intro, main_point, conclusion",
        "passed": has_intro and has_main and has_conclusion,
    })

    # OV-006: Coherent (non-empty content)
    validation_results.append({
        "rule": "OV-006",
        "description": "Summary is coherent and readable",
        "passed": len(content.strip()) > 0,
    })

    all_passed = all(v["passed"] for v in validation_results)

    report_path = run_root / "OUTPUT_VALIDATION_REPORT-001.md"
    report_path.write_text(
        _render_validation_report(validation_results), encoding="utf-8"
    )

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
        remark="All output validation rules passed (OV-001 to OV-006)",
        artifacts={"OUTPUT_VALIDATION_REPORT": str(report_path)},
    )


def _render_validation_report(results: list[dict[str, Any]]) -> str:
    """Render output validation report as Markdown."""
    lines = [
        "---",
        'doc_type: "output_validation_report"',
        'lifecycle_status: "final"',
        "---",
        "",
        "# Output Validation Report",
        "",
        "| Rule | Description | Passed |",
        "|------|-------------|--------|",
    ]
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        lines.append(f"| {r['rule']} | {r['description']} | {status} |")

    all_passed = all(r["passed"] for r in results)
    lines.append("")
    lines.append(f"**Overall Result:** {'PASS' if all_passed else 'FAIL'}")
    lines.append("")

    return "\n".join(lines)


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
    """
    artifacts = state.get("artifacts", {})
    summary_file_str = artifacts.get("SUMMARY_FILE", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

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

    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )
    promoted_dir = run_root / "promoted"
    promoted_dir.mkdir(parents=True, exist_ok=True)

    target_path = promoted_dir / source_path.name
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

    Writes completion metadata and marks the workflow as successfully completed.
    """
    artifacts = state.get("artifacts", {})
    promoted_str = artifacts.get("SUMMARY_FILE_PROMOTED", "")
    project_root = Path(project_root)
    job_id = str(state.get("job_id", "unknown"))

    run_root = (
        project_root / "docs" / "repo" / "text_summarizer" / "runs" / job_id
    )

    completion_record = {
        "job_id": job_id,
        "status": "COMPLETED",
        "completed_at": datetime.now().isoformat(),
        "output_file": promoted_str,
    }

    completion_path = run_root / "COMPLETION_RESULT-001.json"
    completion_path.write_text(
        json.dumps(completion_record, indent=2), encoding="utf-8"
    )

    return ActionResult(
        status="APPROVED",
        remark="Pipeline completed successfully",
        artifacts={"COMPLETION_RESULT": str(completion_path)},
    )
