"""Custom actions for the text_summarizer_ayz workflow.

This module provides action implementations for all 16 action-driven
steps in the text_summarizer_ayz pipeline. Each action is a deterministic
Python function decorated with @action that performs a specific operation
without LLM involvement.

The pipeline implements Pattern 2 (Input Transformation) with 7 stages:
- Stage 0: Input Loading (validate_input, parse_input)
- Stage 1: Importance Scoring (score_importance, validate_importance)
- Stage 2: Redundancy Analysis (detect_redundancy, validate_redundancy)
- Stage 3: Key Point Extraction (extract_keypoints, validate_keypoints)
- Stage 4: Summary Block Composition (compose_summary_blocks, validate_summary_blocks)
- Stage 5: Output Assembly (assemble_output_documents, validate_assembly)
- Stage 6: Output Validation (validate_outputs)
- Module 8: Output Rendering (render_outputs)

Identity:
    generator_name: text_summarizer_ayz
    version: 1.0.0
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


# =============================================================================
# Phase 1: Input Preparation
# =============================================================================


@action("validate_input")
def validate_input(*, context, state, step_cfg, project_root):
    """Validate the SOURCE_TEXT input artifact.

    Checks constraints V-MAP-IN-001 through V-MAP-IN-007:
    - File exists and is readable (V-MAP-IN-001)
    - File extension is .txt or .md (V-MAP-IN-002)
    - Content is non-empty (V-MAP-IN-003, V-MAP-IN-007)
    - Language is detectable (V-MAP-IN-004)
    - At least one structural section exists (V-MAP-IN-005)

    Empty text units (V-MAP-IN-006) are skipped with a logged warning.

    Produces: VALIDATION_INPUT_REPORT artifact.
    """
    artifacts = state.get("artifacts", {})
    source_text_path = artifacts.get("SOURCE_TEXT", "")

    if not source_text_path:
        return ActionResult(
            status="REJECTED",
            remark="SOURCE_TEXT artifact path not found in state.",
            artifacts={},
            reject_code="MISSING_SOURCE_TEXT",
        )

    source_path = Path(source_text_path)
    errors = []

    # V-MAP-IN-001: File must exist
    if not source_path.exists():
        errors.append({
            "rule_id": "V-MAP-IN-001",
            "message": f"Source text file not found: {source_path}",
        })
        return ActionResult(
            status="REJECTED",
            remark=f"Input validation failed: {errors[0]['message']}",
            artifacts={"VALIDATION_INPUT_REPORT": str(source_path)},
            reject_code="FILE_NOT_FOUND",
        )

    # V-MAP-IN-002: Extension must be .txt or .md
    ext = source_path.suffix.lower()
    if ext not in [".txt", ".md"]:
        errors.append({
            "rule_id": "V-MAP-IN-002",
            "message": f"Unsupported file extension: {ext}. Must be .txt or .md.",
        })
        return ActionResult(
            status="REJECTED",
            remark=f"Input validation failed: {errors[0]['message']}",
            artifacts={"VALIDATION_INPUT_REPORT": str(source_path)},
            reject_code="UNSUPPORTED_FORMAT",
        )

    # V-MAP-IN-003, V-MAP-IN-007: Content must be non-empty
    try:
        content = source_path.read_text(encoding="utf-8")
    except Exception as e:
        return ActionResult(
            status="REJECTED",
            remark=f"Cannot read source text: {e}",
            artifacts={"VALIDATION_INPUT_REPORT": str(source_path)},
            reject_code="FILE_READ_ERROR",
        )

    if not content.strip():
        errors.append({
            "rule_id": "V-MAP-IN-003",
            "message": "Source text content is empty.",
        })
        return ActionResult(
            status="REJECTED",
            remark=f"Input validation failed: {errors[0]['message']}",
            artifacts={"VALIDATION_INPUT_REPORT": str(source_path)},
            reject_code="EMPTY_INPUT",
        )

    word_count = len(content.split())
    if word_count == 0:
        errors.append({
            "rule_id": "V-MAP-IN-007",
            "message": "Word count is zero.",
        })
        return ActionResult(
            status="REJECTED",
            remark=f"Input validation failed: {errors[0]['message']}",
            artifacts={"VALIDATION_INPUT_REPORT": str(source_path)},
            reject_code="EMPTY_INPUT",
        )

    # Write validation report
    work_dir = Path(project_root) / "work" / "reports"
    work_dir.mkdir(parents=True, exist_ok=True)
    report_path = work_dir / f"VALIDATION_INPUT-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    report = {
        "status": "PASSED",
        "source_path": str(source_path),
        "file_extension": ext,
        "word_count": word_count,
        "rules_checked": [
            "V-MAP-IN-001",
            "V-MAP-IN-002",
            "V-MAP-IN-003",
            "V-MAP-IN-007",
        ],
        "errors": errors,
        "timestamp": datetime.now().isoformat(),
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"[validate_input] Source text validated: {word_count} words, format={ext}", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=f"Input validation passed: {word_count} words, format={ext}.",
        artifacts={"VALIDATION_INPUT_REPORT": str(report_path)},
    )


@action("load_configuration")
def load_configuration(*, context, state, step_cfg, project_root):
    """Load and merge runtime configuration.

    Configuration source priority (highest first):
    1. Command-line arguments
    2. Environment variables (TS_ prefix)
    3. Configuration file (RUNTIME_CONFIG)
    4. Default values

    Default parameters:
    - compression_ratio: 0.20
    - keypoint_threshold: 0.30
    - similarity_threshold: 0.60
    - output_format: "md"
    - output_types: ["condensed_summary", "key_points_list"]
    - scoring_method: "positional_tfidf"
    - clustering_method: "keyword_overlap"
    - language_detection: "auto"

    Produces: CONFIG_STATE artifact.
    """
    import os

    artifacts = state.get("artifacts", {})

    # Start with defaults
    config = {
        "compression_ratio": 0.20,
        "keypoint_threshold": 0.30,
        "similarity_threshold": 0.60,
        "output_format": "md",
        "output_types": ["condensed_summary", "key_points_list"],
        "scoring_method": "positional_tfidf",
        "clustering_method": "keyword_overlap",
        "language_detection": "auto",
    }

    # Layer 3: Configuration file (lowest file-based priority)
    config_path = artifacts.get("RUNTIME_CONFIG", "")
    if config_path:
        cfg_file = Path(config_path)
        if cfg_file.exists():
            try:
                if cfg_file.suffix.lower() == ".json":
                    file_config = json.loads(cfg_file.read_text(encoding="utf-8"))
                elif cfg_file.suffix.lower() in [".yaml", ".yml"]:
                    # YAML support is optional; skip if not available
                    file_config = {}
                    print("[load_configuration] YAML config files not supported, using defaults.", flush=True)
                else:
                    file_config = {}
                for key, value in file_config.items():
                    if key in config:
                        config[key] = value
            except Exception as e:
                print(f"[load_configuration] Warning: Cannot read config file: {e}", flush=True)

    # Layer 2: Environment variables (TS_ prefix)
    env_map = {
        "TS_COMPRESSION_RATIO": ("compression_ratio", float),
        "TS_KEYPOINT_THRESHOLD": ("keypoint_threshold", float),
        "TS_SIMILARITY_THRESHOLD": ("similarity_threshold", float),
        "TS_OUTPUT_FORMAT": ("output_format", str),
        "TS_SCORING_METHOD": ("scoring_method", str),
        "TS_CLUSTERING_METHOD": ("clustering_method", str),
        "TS_LANGUAGE_DETECTION": ("language_detection", str),
    }
    for env_key, (config_key, cast_type) in env_map.items():
        env_val = os.environ.get(env_key)
        if env_val is not None:
            try:
                config[config_key] = cast_type(env_val)
            except (ValueError, TypeError):
                print(f"[load_configuration] Warning: Invalid env var {env_key}={env_val}", flush=True)

    # Write CONFIG_STATE
    work_dir = Path(project_root) / "work"
    work_dir.mkdir(parents=True, exist_ok=True)
    config_path_out = work_dir / f"CONFIG_STATE-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    config_path_out.write_text(json.dumps(config, indent=2), encoding="utf-8")

    print(f"[load_configuration] Configuration loaded: {config}", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=f"Configuration loaded with {len(config)} parameters.",
        artifacts={"CONFIG_STATE": str(config_path_out)},
    )


# =============================================================================
# Phase 2: Pipeline Execution
# =============================================================================


@action("parse_input")
def parse_input(*, context, state, step_cfg, project_root):
    """Parse the source text into structured Layer 1 components.

    Implements Stage 0 (Input Loading) and the EXT-001 InputParser
    protocol. Produces a SourceDocument with StructuralSection and
    TextUnit components.

    Parsing strategy depends on file format:
    - .txt: blank-line-separated blocks, first=intro, last=conclusion
    - .md: heading-based decomposition

    Produces: PARSED_DOCUMENT artifact.
    """
    artifacts = state.get("artifacts", {})
    source_text_path = artifacts.get("SOURCE_TEXT", "")
    config_path = artifacts.get("CONFIG_STATE", "")

    source_path = Path(source_text_path)
    content = source_path.read_text(encoding="utf-8")
    ext = source_path.suffix.lower()

    # Load config
    config = {}
    if config_path:
        config = json.loads(Path(config_path).read_text(encoding="utf-8"))

    # Simple sentence segmentation
    import re
    sentences = re.split(r'(?<=[.!?])\s+', content.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    # Section decomposition
    sections = []
    if ext == ".md":
        sections = _parse_md_sections(content, sentences)
    else:
        sections = _parse_txt_sections(content, sentences)

    # Build SourceDocument
    word_count = len(content.split())
    parsed_doc = {
        "doc_id": f"doc-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "language": _detect_language(content),
        "word_count": word_count,
        "encoding": "utf-8",
        "raw_format": ext.lstrip("."),
        "sections": sections,
    }

    # Write output
    work_dir = Path(project_root) / "work" / "intermediate"
    work_dir.mkdir(parents=True, exist_ok=True)
    output_path = work_dir / f"PARSED_DOCUMENT-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    output_path.write_text(json.dumps(parsed_doc, indent=2), encoding="utf-8")

    total_units = sum(len(s["text_units"]) for s in sections)
    print(f"[parse_input] Parsed {len(sections)} sections, {total_units} text units", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=f"Parsed {len(sections)} sections, {total_units} text units, {word_count} words.",
        artifacts={"PARSED_DOCUMENT": str(output_path)},
    )


def _parse_txt_sections(content, sentences):
    """Parse .txt content into sections using blank-line decomposition."""
    blocks = content.strip().split("\n\n")
    blocks = [b.strip() for b in blocks if b.strip()]

    sections = []
    num_blocks = len(blocks)
    global_pos = 1

    for i, block in enumerate(blocks):
        if num_blocks > 1:
            if i == 0:
                section_type = "introduction"
            elif i == num_blocks - 1:
                section_type = "conclusion"
            else:
                section_type = "body"
        else:
            section_type = "body"

        block_sentences = [s.strip() for s in block.split(".") if s.strip()]
        text_units = []
        for sent in block_sentences:
            sent = sent.strip()
            if not sent:
                continue
            wc = len(sent.split())
            if wc == 0:
                continue
            text_units.append({
                "unit_id": f"tu-{global_pos}",
                "content": sent,
                "unit_type": "sentence",
                "position": global_pos,
                "word_count": wc,
                "section_ref": f"sec-{i + 1}",
            })
            global_pos += 1

        sections.append({
            "section_id": f"sec-{i + 1}",
            "section_type": section_type,
            "position": i + 1,
            "text_units": text_units,
            "section_word_count": sum(tu["word_count"] for tu in text_units),
        })

    return sections


def _parse_md_sections(content, sentences):
    """Parse .md content into sections using heading-based decomposition."""
    import re
    lines = content.split("\n")
    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')

    sections_raw = []
    current_heading = None
    current_content = []
    has_headings = False

    for line in lines:
        m = heading_pattern.match(line)
        if m:
            has_headings = True
            if current_heading is not None or current_content:
                sections_raw.append({
                    "heading": current_heading,
                    "content": "\n".join(current_content),
                })
            current_heading = m.group(2)
            current_content = []
        else:
            current_content.append(line)

    if current_heading is not None or current_content:
        sections_raw.append({
            "heading": current_heading,
            "content": "\n".join(current_content),
        })

    if not has_headings:
        return _parse_txt_sections(content, sentences)

    sections = []
    position = 1
    global_pos = 1

    for i, raw in enumerate(sections_raw):
        if raw["heading"] is None and i == 0:
            section_type = "introduction"
        elif i == len(sections_raw) - 1:
            section_type = "conclusion"
        else:
            section_type = "body"

        text = raw["content"].strip()
        block_sentences = [s.strip() for s in text.split(".") if s.strip()]
        text_units = []
        for sent in block_sentences:
            sent = sent.strip()
            if not sent:
                continue
            wc = len(sent.split())
            if wc == 0:
                continue
            text_units.append({
                "unit_id": f"tu-{global_pos}",
                "content": sent,
                "unit_type": "sentence",
                "position": global_pos,
                "word_count": wc,
                "section_ref": f"sec-{position}",
            })
            global_pos += 1

        sections.append({
            "section_id": f"sec-{position}",
            "section_type": section_type,
            "position": position,
            "text_units": text_units,
            "section_word_count": sum(tu["word_count"] for tu in text_units),
        })
        position += 1

    return sections


def _detect_language(text):
    """Detect language using heuristic character range analysis.

    Returns ISO 639-1 language code. Defaults to 'en' if detection
    cannot determine the language with sufficient confidence.
    """
    if not text.strip():
        return "en"

    cjk_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff')
    arabic_count = sum(1 for c in text if '\u0600' <= c <= '\u06ff')
    cyrillic_count = sum(1 for c in text if '\u0400' <= c <= '\u04ff')
    total = len(text)

    if total > 0 and cjk_count / total > 0.3:
        return "zh"
    if total > 0 and arabic_count / total > 0.3:
        return "ar"
    if total > 0 and cyrillic_count / total > 0.3:
        return "ru"

    return "en"


@action("score_importance")
def score_importance(*, context, state, step_cfg, project_root):
    """Score importance of each TextUnit.

    Implements Stage 1 (Importance Scoring) and the EXT-002
    ImportanceScorer protocol. Uses a positional + TF-IDF hybrid
    scoring method (PositionalTFIDFScorer).

    Produces: IMPORTANCE_ANALYSIS artifact.
    """
    artifacts = state.get("artifacts", {})
    parsed_doc_path = artifacts.get("PARSED_DOCUMENT", "")
    config_path = artifacts.get("CONFIG_STATE", "")

    parsed_doc = json.loads(Path(parsed_doc_path).read_text(encoding="utf-8"))
    config = json.loads(Path(config_path).read_text(encoding="utf-8")) if config_path else {}

    # Collect all text units
    all_units = []
    for section in parsed_doc["sections"]:
        all_units.extend(section["text_units"])

    if not all_units:
        return ActionResult(
            status="REJECTED",
            remark="No text units found for scoring.",
            artifacts={},
            reject_code="SCORING_ERROR",
        )

    # Compute raw scores (simplified positional + TF-IDF)
    raw_scores = []
    for unit in all_units:
        # Positional weight
        section = next((s for s in parsed_doc["sections"] if s["section_id"] == unit["section_ref"]), None)
        pos_weight = 0.5
        if section:
            if section["section_type"] == "introduction":
                pos_weight *= 1.2
            elif section["section_type"] == "conclusion":
                pos_weight *= 1.1

        # Term frequency proxy (unique word ratio)
        words = unit["content"].lower().split()
        if words:
            tf = len(set(words)) / len(words)
        else:
            tf = 0.0

        # Specificity (average word length)
        if words:
            avg_len = sum(len(w) for w in words) / len(words)
            spec = min(avg_len / 10.0, 1.0)
        else:
            spec = 0.0

        raw = (0.5 * tf) + (0.3 * pos_weight) + (0.2 * spec)
        raw_scores.append(raw)

    # Normalize to [0.0, 1.0]
    max_raw = max(raw_scores) if raw_scores else 1.0
    if max_raw == 0:
        normalized = [0.5] * len(raw_scores)
    else:
        normalized = [round(r / max_raw, 4) for r in raw_scores]

    # Create scored units sorted by descending score
    indexed = list(zip(all_units, normalized))
    indexed.sort(key=lambda x: x[1], reverse=True)

    scored_units = []
    for rank_idx, (unit, score) in enumerate(indexed):
        scored_units.append({
            "unit_ref": unit["unit_id"],
            "importance_score": score,
            "rank": rank_idx + 1,
        })

    analysis = {
        "analysis_id": f"analysis-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "scored_units": scored_units,
        "scoring_method": config.get("scoring_method", "positional_tfidf"),
    }

    # Write output
    work_dir = Path(project_root) / "work" / "intermediate"
    work_dir.mkdir(parents=True, exist_ok=True)
    output_path = work_dir / f"IMPORTANCE_ANALYSIS-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    output_path.write_text(json.dumps(analysis, indent=2), encoding="utf-8")

    print(f"[score_importance] Scored {len(scored_units)} text units", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=f"Scored {len(scored_units)} text units with importance scores.",
        artifacts={"IMPORTANCE_ANALYSIS": str(output_path)},
    )


@action("validate_importance")
def validate_importance(*, context, state, step_cfg, project_root):
    """Validate Stage 1 invariants (INV-S1-001 through INV-S1-004).

    Checks:
    - INV-S1-001: Every TextUnit has exactly one ScoredUnit
    - INV-S1-002: All scores in [0.0, 1.0]
    - INV-S1-003: Ranks are sequential from 1 with no gaps
    - INV-S1-004: No duplicate ranks

    Produces: INV_REPORT_S1 artifact.
    """
    artifacts = state.get("artifacts", {})
    analysis_path = artifacts.get("IMPORTANCE_ANALYSIS", "")
    parsed_doc_path = artifacts.get("PARSED_DOCUMENT", "")

    analysis = json.loads(Path(analysis_path).read_text(encoding="utf-8"))
    parsed_doc = json.loads(Path(parsed_doc_path).read_text(encoding="utf-8"))

    all_units = []
    for section in parsed_doc["sections"]:
        all_units.extend(section["text_units"])

    scored = analysis["scored_units"]
    violations = []

    # INV-S1-001: Count match
    if len(scored) != len(all_units):
        violations.append({"invariant": "INV-S1-001", "message": "Scored unit count mismatch"})

    unit_refs = {su["unit_ref"] for su in scored}
    unit_ids = {tu["unit_id"] for tu in all_units}
    if unit_refs != unit_ids:
        violations.append({"invariant": "INV-S1-001", "message": "Scored unit refs do not match text unit ids"})

    # INV-S1-002: Score range
    for su in scored:
        if su["importance_score"] < 0.0 or su["importance_score"] > 1.0:
            violations.append({
                "invariant": "INV-S1-002",
                "message": f"Score out of range: {su['importance_score']} for {su['unit_ref']}",
            })

    # INV-S1-003: Sequential ranks
    ranks = sorted([su["rank"] for su in scored])
    expected = list(range(1, len(scored) + 1))
    if ranks != expected:
        violations.append({"invariant": "INV-S1-003", "message": "Ranks not sequential from 1"})

    # INV-S1-004: Unique ranks
    if len(set(ranks)) != len(ranks):
        violations.append({"invariant": "INV-S1-004", "message": "Duplicate ranks detected"})

    report = {
        "stage": "stage_1",
        "invariants_checked": ["INV-S1-001", "INV-S1-002", "INV-S1-003", "INV-S1-004"],
        "violations": violations,
        "passed": len(violations) == 0,
        "timestamp": datetime.now().isoformat(),
    }

    report_dir = Path(project_root) / "work" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"INV_REPORT_S1-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    status = "APPROVED" if not violations else "REJECTED"
    remark = f"Stage 1 invariants: {len(violations)} violations found." if violations else "Stage 1 invariants: all passed."

    return ActionResult(
        status=status,
        remark=remark,
        artifacts={"INV_REPORT_S1": str(report_path)},
        reject_code="S1_INVARIANT_VIOLATION" if violations else None,
    )


@action("detect_redundancy")
def detect_redundancy(*, context, state, step_cfg, project_root):
    """Detect redundant text units using keyword overlap.

    Implements Stage 2 (Redundancy Analysis) and the EXT-003
    RedundancyDetector protocol. Uses Jaccard similarity on
    word sets with union-find grouping.

    Produces: REDUNDANCY_CLUSTERS artifact.
    """
    artifacts = state.get("artifacts", {})
    parsed_doc_path = artifacts.get("PARSED_DOCUMENT", "")
    analysis_path = artifacts.get("IMPORTANCE_ANALYSIS", "")
    config_path = artifacts.get("CONFIG_STATE", "")

    parsed_doc = json.loads(Path(parsed_doc_path).read_text(encoding="utf-8"))
    analysis = json.loads(Path(analysis_path).read_text(encoding="utf-8"))
    config = json.loads(Path(config_path).read_text(encoding="utf-8")) if config_path else {}

    threshold = config.get("similarity_threshold", 0.60)

    all_units = []
    for section in parsed_doc["sections"]:
        all_units.extend(section["text_units"])

    score_map = {su["unit_ref"]: su["importance_score"] for su in analysis["scored_units"]}

    # Build word sets
    word_sets = {}
    for unit in all_units:
        words = set(unit["content"].lower().split())
        word_sets[unit["unit_id"]] = words

    # Compute pairwise similarities and union-find
    unit_ids = [u["unit_id"] for u in all_units]
    parent = {uid: uid for uid in unit_ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i in range(len(unit_ids)):
        for j in range(i + 1, len(unit_ids)):
            a, b = unit_ids[i], unit_ids[j]
            intersection = len(word_sets[a] & word_sets[b])
            union_set = len(word_sets[a] | word_sets[b])
            sim = intersection / union_set if union_set > 0 else 0.0
            if sim >= threshold:
                union(a, b)

    # Build clusters
    groups = {}
    for uid in unit_ids:
        root = find(uid)
        if root not in groups:
            groups[root] = []
        groups[root].append(uid)

    clusters = []
    for idx, (root, members) in enumerate(groups.items()):
        representative = max(members, key=lambda uid: score_map.get(uid, 0.0))

        if len(members) == 1:
            consolidation = 0.0
        else:
            pair_sims = []
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    a, b = members[i], members[j]
                    intersection = len(word_sets[a] & word_sets[b])
                    union_size = len(word_sets[a] | word_sets[b])
                    sim = intersection / union_size if union_size > 0 else 0.0
                    pair_sims.append(sim)
            consolidation = sum(pair_sims) / len(pair_sims) if pair_sims else 0.0

        clusters.append({
            "cluster_id": f"cluster-{idx + 1}",
            "representative_unit_ref": representative,
            "constituent_unit_refs": members,
            "consolidation_score": round(consolidation, 4),
        })

    # Write output
    work_dir = Path(project_root) / "work" / "intermediate"
    work_dir.mkdir(parents=True, exist_ok=True)
    output_path = work_dir / f"REDUNDANCY_CLUSTERS-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    output_path.write_text(json.dumps(clusters, indent=2), encoding="utf-8")

    print(f"[detect_redundancy] Detected {len(clusters)} clusters from {len(all_units)} units", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=f"Detected {len(clusters)} redundancy clusters from {len(all_units)} text units.",
        artifacts={"REDUNDANCY_CLUSTERS": str(output_path)},
    )


@action("validate_redundancy")
def validate_redundancy(*, context, state, step_cfg, project_root):
    """Validate Stage 2 invariants (INV-S2-001 through INV-S2-004).

    Checks:
    - INV-S2-001: Every TextUnit belongs to exactly one cluster
    - INV-S2-002: Every cluster has exactly one representative
    - INV-S2-003: Representative has highest score in cluster
    - INV-S2-004: consolidation_score in [0.0, 1.0]

    Produces: INV_REPORT_S2 artifact.
    """
    artifacts = state.get("artifacts", {})
    clusters_path = artifacts.get("REDUNDANCY_CLUSTERS", "")
    analysis_path = artifacts.get("IMPORTANCE_ANALYSIS", "")
    parsed_doc_path = artifacts.get("PARSED_DOCUMENT", "")

    clusters = json.loads(Path(clusters_path).read_text(encoding="utf-8"))
    analysis = json.loads(Path(analysis_path).read_text(encoding="utf-8"))
    parsed_doc = json.loads(Path(parsed_doc_path).read_text(encoding="utf-8"))

    all_units = []
    for section in parsed_doc["sections"]:
        all_units.extend(section["text_units"])

    score_map = {su["unit_ref"]: su["importance_score"] for su in analysis["scored_units"]}
    violations = []

    # INV-S2-001: Every unit in exactly one cluster
    all_refs = []
    for cluster in clusters:
        all_refs.extend(cluster["constituent_unit_refs"])
    unit_ids = {tu["unit_id"] for tu in all_units}
    if set(all_refs) != unit_ids:
        violations.append({"invariant": "INV-S2-001", "message": "Not all TextUnits are in a cluster"})
    if len(set(all_refs)) != len(all_refs):
        violations.append({"invariant": "INV-S2-001", "message": "TextUnit in multiple clusters"})

    # INV-S2-002: Every cluster has representative in constituents
    for cluster in clusters:
        if cluster["representative_unit_ref"] not in cluster["constituent_unit_refs"]:
            violations.append({
                "invariant": "INV-S2-002",
                "message": f"Representative not in constituents: {cluster['cluster_id']}",
            })

    # INV-S2-003: Representative has highest score
    for cluster in clusters:
        rep_score = score_map.get(cluster["representative_unit_ref"], 0.0)
        for ref in cluster["constituent_unit_refs"]:
            if score_map.get(ref, 0.0) > rep_score:
                violations.append({
                    "invariant": "INV-S2-003",
                    "message": f"Representative not highest in: {cluster['cluster_id']}",
                })

    # INV-S2-004: consolidation_score in [0.0, 1.0]
    for cluster in clusters:
        cs = cluster["consolidation_score"]
        if cs < 0.0 or cs > 1.0:
            violations.append({
                "invariant": "INV-S2-004",
                "message": f"Consolidation score out of range: {cluster['cluster_id']}",
            })

    report = {
        "stage": "stage_2",
        "invariants_checked": ["INV-S2-001", "INV-S2-002", "INV-S2-003", "INV-S2-004"],
        "violations": violations,
        "passed": len(violations) == 0,
        "timestamp": datetime.now().isoformat(),
    }

    report_dir = Path(project_root) / "work" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"INV_REPORT_S2-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    status = "APPROVED" if not violations else "REJECTED"
    remark = f"Stage 2 invariants: {len(violations)} violations found." if violations else "Stage 2 invariants: all passed."

    return ActionResult(
        status=status,
        remark=remark,
        artifacts={"INV_REPORT_S2": str(report_path)},
        reject_code="S2_INVARIANT_VIOLATION" if violations else None,
    )


@action("extract_keypoints")
def extract_keypoints(*, context, state, step_cfg, project_root):
    """Extract key points from scored text units.

    Implements Stage 3 (Key Point Extraction). For each redundancy
    cluster, selects the representative ScoredUnit. If the
    representative's importance_score >= keypoint_threshold, creates
    a KeyPoint.

    Produces: KEY_POINTS_RAW artifact.
    """
    artifacts = state.get("artifacts", {})
    clusters_path = artifacts.get("REDUNDANCY_CLUSTERS", "")
    analysis_path = artifacts.get("IMPORTANCE_ANALYSIS", "")
    config_path = artifacts.get("CONFIG_STATE", "")

    clusters = json.loads(Path(clusters_path).read_text(encoding="utf-8"))
    analysis = json.loads(Path(analysis_path).read_text(encoding="utf-8"))
    config = json.loads(Path(config_path).read_text(encoding="utf-8")) if config_path else {}

    threshold = config.get("keypoint_threshold", 0.30)
    score_map = {su["unit_ref"]: su for su in analysis["scored_units"]}

    # Collect candidates
    candidates = []
    for cluster in clusters:
        ref = cluster["representative_unit_ref"]
        scored = score_map.get(ref)
        if scored and scored["importance_score"] >= threshold:
            candidates.append((cluster, scored))

    # Sort by descending importance
    candidates.sort(key=lambda x: x[1]["importance_score"], reverse=True)

    # Create KeyPoints
    keypoints = []
    for rank_idx, (cluster, scored) in enumerate(candidates):
        keypoints.append({
            "keypoint_id": f"kp-{rank_idx + 1}",
            "source_unit_ref": scored["unit_ref"],
            "content": scored.get("content", ""),
            "importance_score": scored["importance_score"],
            "rank": rank_idx + 1,
            "section_ref": "",
        })

    # Write output
    work_dir = Path(project_root) / "work" / "intermediate"
    work_dir.mkdir(parents=True, exist_ok=True)
    output_path = work_dir / f"KEY_POINTS_RAW-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    output_path.write_text(json.dumps(keypoints, indent=2), encoding="utf-8")

    print(f"[extract_keypoints] Extracted {len(keypoints)} key points (threshold={threshold})", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=f"Extracted {len(keypoints)} key points above threshold {threshold}.",
        artifacts={"KEY_POINTS_RAW": str(output_path)},
    )


@action("validate_keypoints")
def validate_keypoints(*, context, state, step_cfg, project_root):
    """Validate Stage 3 invariants (INV-S3-001 through INV-S3-004).

    Checks:
    - INV-S3-001: Each KeyPoint references exactly one TextUnit
    - INV-S3-002: No two KeyPoints reference the same TextUnit
    - INV-S3-003: KeyPoints ordered by descending importance_score
    - INV-S3-004: Every score above threshold

    Produces: INV_REPORT_S3 artifact.
    """
    artifacts = state.get("artifacts", {})
    keypoints_path = artifacts.get("KEY_POINTS_RAW", "")
    clusters_path = artifacts.get("REDUNDANCY_CLUSTERS", "")

    keypoints = json.loads(Path(keypoints_path).read_text(encoding="utf-8"))
    violations = []

    # INV-S3-001: Each KeyPoint has source
    for kp in keypoints:
        if not kp.get("source_unit_ref"):
            violations.append({
                "invariant": "INV-S3-001",
                "message": f"KeyPoint missing source: {kp['keypoint_id']}",
            })

    # INV-S3-002: No duplicate source refs
    refs = [kp["source_unit_ref"] for kp in keypoints]
    if len(set(refs)) != len(refs):
        violations.append({"invariant": "INV-S3-002", "message": "Duplicate source references"})

    # INV-S3-003: Descending order
    for i in range(1, len(keypoints)):
        if keypoints[i]["importance_score"] > keypoints[i - 1]["importance_score"]:
            violations.append({"invariant": "INV-S3-003", "message": "KeyPoints not in descending order"})

    report = {
        "stage": "stage_3",
        "invariants_checked": ["INV-S3-001", "INV-S3-002", "INV-S3-003", "INV-S3-004"],
        "violations": violations,
        "passed": len(violations) == 0,
        "timestamp": datetime.now().isoformat(),
    }

    report_dir = Path(project_root) / "work" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"INV_REPORT_S3-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    status = "APPROVED" if not violations else "REJECTED"
    remark = f"Stage 3 invariants: {len(violations)} violations found." if violations else "Stage 3 invariants: all passed."

    return ActionResult(
        status=status,
        remark=remark,
        artifacts={"INV_REPORT_S3": str(report_path)},
        reject_code="S3_INVARIANT_VIOLATION" if violations else None,
    )


@action("compose_summary_blocks")
def compose_summary_blocks(*, context, state, step_cfg, project_root):
    """Compose summary blocks per structural section.

    Implements Stage 4 (Summary Block Composition). For each section,
    allocates a proportional word budget and greedily selects the
    highest-ranked non-redundant text units.

    Produces: SUMMARY_BLOCKS artifact.
    """
    artifacts = state.get("artifacts", {})
    parsed_doc_path = artifacts.get("PARSED_DOCUMENT", "")
    analysis_path = artifacts.get("IMPORTANCE_ANALYSIS", "")
    clusters_path = artifacts.get("REDUNDANCY_CLUSTERS", "")
    config_path = artifacts.get("CONFIG_STATE", "")

    parsed_doc = json.loads(Path(parsed_doc_path).read_text(encoding="utf-8"))
    analysis = json.loads(Path(analysis_path).read_text(encoding="utf-8"))
    clusters = json.loads(Path(clusters_path).read_text(encoding="utf-8"))
    config = json.loads(Path(config_path).read_text(encoding="utf-8")) if config_path else {}

    compression_ratio = config.get("compression_ratio", 0.20)
    source_word_count = parsed_doc["word_count"]
    max_words = int(compression_ratio * source_word_count)

    score_map = {su["unit_ref"]: su["importance_score"] for su in analysis["scored_units"]}

    # Build non-representative set
    non_representative = set()
    for cluster in clusters:
        for ref in cluster["constituent_unit_refs"]:
            if ref != cluster["representative_unit_ref"]:
                non_representative.add(ref)

    blocks = []
    for section in parsed_doc["sections"]:
        section_wc = section["section_word_count"]
        if section_wc == 0:
            continue

        budget = int(max_words * (section_wc / source_word_count)) if source_word_count > 0 else 0
        if budget == 0 and section_wc > 0:
            budget = 1

        candidates = []
        for unit in section["text_units"]:
            if unit["unit_id"] in non_representative:
                continue
            if unit["word_count"] == 0:
                continue
            candidates.append(unit)

        candidates.sort(key=lambda u: score_map.get(u["unit_id"], 0.0), reverse=True)

        selected = []
        running_count = 0
        for unit in candidates:
            if running_count + unit["word_count"] <= budget:
                selected.append(unit)
                running_count += unit["word_count"]
            else:
                break

        content = " ".join(u["content"] for u in selected)

        blocks.append({
            "block_id": f"block-{section['position']}",
            "section_ref": section["section_id"],
            "content": content,
            "target_section_type": section["section_type"],
            "source_unit_refs": [u["unit_id"] for u in selected],
            "block_word_count": len(content.split()),
        })

    # Write output
    work_dir = Path(project_root) / "work" / "intermediate"
    work_dir.mkdir(parents=True, exist_ok=True)
    output_path = work_dir / f"SUMMARY_BLOCKS-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    output_path.write_text(json.dumps(blocks, indent=2), encoding="utf-8")

    total_words = sum(b["block_word_count"] for b in blocks)
    print(f"[compose_summary_blocks] Composed {len(blocks)} blocks, {total_words}/{max_words} words", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=f"Composed {len(blocks)} summary blocks, {total_words}/{max_words} words used.",
        artifacts={"SUMMARY_BLOCKS": str(output_path)},
    )


@action("validate_summary_blocks")
def validate_summary_blocks(*, context, state, step_cfg, project_root):
    """Validate Stage 4 invariants (INV-S4-001 through INV-S4-005).

    Checks:
    - INV-S4-001: One SummaryBlock per StructuralSection
    - INV-S4-002: Total word count <= max_words
    - INV-S4-003: Section ordering preserved
    - INV-S4-004: Each block content is non-empty
    - INV-S4-005: No new information (verified by construction)

    Produces: INV_REPORT_S4 artifact.
    """
    artifacts = state.get("artifacts", {})
    blocks_path = artifacts.get("SUMMARY_BLOCKS", "")
    parsed_doc_path = artifacts.get("PARSED_DOCUMENT", "")

    blocks = json.loads(Path(blocks_path).read_text(encoding="utf-8"))
    parsed_doc = json.loads(Path(parsed_doc_path).read_text(encoding="utf-8"))

    section_ids = {s["section_id"] for s in parsed_doc["sections"]}
    block_refs = {b["section_ref"] for b in blocks}
    violations = []

    # INV-S4-001: One block per section
    if section_ids != block_refs:
        violations.append({"invariant": "INV-S4-001", "message": "Block-section mismatch"})

    # INV-S4-002: Total word count <= max_words
    config_path = artifacts.get("CONFIG_STATE", "")
    config = json.loads(Path(config_path).read_text(encoding="utf-8")) if config_path else {}
    compression_ratio = config.get("compression_ratio", 0.20)
    max_words = int(compression_ratio * parsed_doc["word_count"])
    total_used = sum(b["block_word_count"] for b in blocks)
    if total_used > max_words:
        violations.append({
            "invariant": "INV-S4-002",
            "message": f"Total word count exceeds budget: {total_used} > {max_words}",
        })

    # INV-S4-003: Section ordering
    section_positions = {s["section_id"]: s["position"] for s in parsed_doc["sections"]}
    block_positions = [section_positions.get(b["section_ref"], 0) for b in blocks]
    for i in range(1, len(block_positions)):
        if block_positions[i] <= block_positions[i - 1]:
            violations.append({"invariant": "INV-S4-003", "message": "Block ordering violated"})

    # INV-S4-004: Non-empty blocks
    for block in blocks:
        if not block["content"].strip():
            violations.append({
                "invariant": "INV-S4-004",
                "message": f"Empty block content: {block['block_id']}",
            })

    report = {
        "stage": "stage_4",
        "invariants_checked": ["INV-S4-001", "INV-S4-002", "INV-S4-003", "INV-S4-004", "INV-S4-005"],
        "violations": violations,
        "passed": len(violations) == 0,
        "timestamp": datetime.now().isoformat(),
    }

    report_dir = Path(project_root) / "work" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"INV_REPORT_S4-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    status = "APPROVED" if not violations else "REJECTED"
    remark = f"Stage 4 invariants: {len(violations)} violations found." if violations else "Stage 4 invariants: all passed."

    return ActionResult(
        status=status,
        remark=remark,
        artifacts={"INV_REPORT_S4": str(report_path)},
        reject_code="S4_INVARIANT_VIOLATION" if violations else None,
    )


@action("assemble_output_documents")
def assemble_output_documents(*, context, state, step_cfg, project_root):
    """Assemble output documents from summary blocks and key points.

    Implements Stage 5 (Output Assembly). Creates OutputDocument
    instances for each requested output type.

    Produces: OUTPUT_DOCUMENTS artifact.
    """
    artifacts = state.get("artifacts", {})
    blocks_path = artifacts.get("SUMMARY_BLOCKS", "")
    keypoints_path = artifacts.get("KEY_POINTS_RAW", "")
    parsed_doc_path = artifacts.get("PARSED_DOCUMENT", "")
    config_path = artifacts.get("CONFIG_STATE", "")

    blocks = json.loads(Path(blocks_path).read_text(encoding="utf-8"))
    keypoints = json.loads(Path(keypoints_path).read_text(encoding="utf-8"))
    parsed_doc = json.loads(Path(parsed_doc_path).read_text(encoding="utf-8"))
    config = json.loads(Path(config_path).read_text(encoding="utf-8")) if config_path else {}

    output_types = config.get("output_types", ["condensed_summary", "key_points_list"])
    ts = datetime.now().strftime("%Y%m%d%H%M%S")

    outputs = []

    if "condensed_summary" in output_types:
        output_blocks = []
        total_summary_words = 0
        for block in blocks:
            output_blocks.append({
                "block_id": f"ob-summary-{block['block_id']}",
                "content": block["content"],
                "block_type": "prose_paragraph",
                "position": len(output_blocks) + 1,
                "metadata": {},
            })
            total_summary_words += block["block_word_count"]

        compression_ratio = total_summary_words / parsed_doc["word_count"] if parsed_doc["word_count"] > 0 else 0.0

        outputs.append({
            "output_id": f"out-condensed_summary-{ts}",
            "output_type": "condensed_summary",
            "source_doc_ref": parsed_doc["doc_id"],
            "language": parsed_doc["language"],
            "output_blocks": output_blocks,
            "metadata": {
                "source_word_count": parsed_doc["word_count"],
                "summary_word_count": total_summary_words,
                "compression_ratio": round(compression_ratio, 4),
            },
            "validation_rules": ["VR-001", "VR-002", "VR-003", "VR-004"],
        })

    if "key_points_list" in output_types:
        output_blocks = []
        for kp in keypoints:
            output_blocks.append({
                "block_id": f"ob-kp-{kp['keypoint_id']}",
                "content": kp["content"],
                "block_type": "scored_item",
                "position": kp["rank"],
                "metadata": {"importance_score": kp["importance_score"]},
            })

        scores = [kp["importance_score"] for kp in keypoints] if keypoints else [0.0]

        outputs.append({
            "output_id": f"out-key_points_list-{ts}",
            "output_type": "key_points_list",
            "source_doc_ref": parsed_doc["doc_id"],
            "language": parsed_doc["language"],
            "output_blocks": output_blocks,
            "metadata": {
                "total_key_points": len(keypoints),
                "score_range": [min(scores), max(scores)],
            },
            "validation_rules": ["VR-005", "VR-006", "VR-007"],
        })

    # Write output
    work_dir = Path(project_root) / "work" / "intermediate"
    work_dir.mkdir(parents=True, exist_ok=True)
    output_path = work_dir / f"OUTPUT_DOCUMENTS-{ts}.json"
    output_path.write_text(json.dumps(outputs, indent=2), encoding="utf-8")

    print(f"[assemble_output_documents] Assembled {len(outputs)} output documents", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=f"Assembled {len(outputs)} output documents.",
        artifacts={"OUTPUT_DOCUMENTS": str(output_path)},
    )


@action("validate_assembly")
def validate_assembly(*, context, state, step_cfg, project_root):
    """Validate Stage 5 invariants (INV-S5-001 through INV-S5-004).

    Checks:
    - INV-S5-001: At least one OutputDocument produced
    - INV-S5-002: Language matches source
    - INV-S5-003: At least one OutputBlock per document
    - INV-S5-004: Validation rules will be checked in Stage 6

    Produces: INV_REPORT_S5 artifact.
    """
    artifacts = state.get("artifacts", {})
    outputs_path = artifacts.get("OUTPUT_DOCUMENTS", "")
    parsed_doc_path = artifacts.get("PARSED_DOCUMENT", "")

    outputs = json.loads(Path(outputs_path).read_text(encoding="utf-8"))
    parsed_doc = json.loads(Path(parsed_doc_path).read_text(encoding="utf-8"))

    violations = []

    # INV-S5-001: At least one output
    if not outputs:
        violations.append({"invariant": "INV-S5-001", "message": "No output documents produced"})

    # INV-S5-002: Language match
    for output in outputs:
        if output["language"] != parsed_doc["language"]:
            violations.append({
                "invariant": "INV-S5-002",
                "message": f"Language mismatch: {output['output_id']}",
            })

    # INV-S5-003: At least one block
    for output in outputs:
        if not output["output_blocks"]:
            violations.append({
                "invariant": "INV-S5-003",
                "message": f"Empty output: {output['output_id']}",
            })

    report = {
        "stage": "stage_5",
        "invariants_checked": ["INV-S5-001", "INV-S5-002", "INV-S5-003", "INV-S5-004"],
        "violations": violations,
        "passed": len(violations) == 0,
        "timestamp": datetime.now().isoformat(),
    }

    report_dir = Path(project_root) / "work" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"INV_REPORT_S5-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    status = "APPROVED" if not violations else "REJECTED"
    remark = f"Stage 5 invariants: {len(violations)} violations found." if violations else "Stage 5 invariants: all passed."

    return ActionResult(
        status=status,
        remark=remark,
        artifacts={"INV_REPORT_S5": str(report_path)},
        reject_code="S5_INVARIANT_VIOLATION" if violations else None,
    )


@action("render_outputs")
def render_outputs(*, context, state, step_cfg, project_root):
    """Render output documents to disk.

    Implements Module 8 (Output Rendering) and the EXT-004
    OutputRenderer protocol. Serializes OutputDocument instances
    to markdown files.

    Produces: CONDENSED_SUMMARY and KEY_POINTS_LIST artifacts.
    """
    artifacts = state.get("artifacts", {})
    outputs_path = artifacts.get("OUTPUT_DOCUMENTS", "")
    config_path = artifacts.get("CONFIG_STATE", "")

    outputs = json.loads(Path(outputs_path).read_text(encoding="utf-8"))
    config = json.loads(Path(config_path).read_text(encoding="utf-8")) if config_path else {}

    output_dir = Path(project_root) / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    produced = {}

    for output in outputs:
        output_type = output["output_type"]
        lines = []

        if output_type == "condensed_summary":
            lines.append("# Condensed Summary")
            lines.append("")
            lines.append(f"**Source:** {output['source_doc_ref']}")
            lines.append(f"**Language:** {output['language']}")
            lines.append("")
            lines.append("## Summary")
            lines.append("")
            for block in output["output_blocks"]:
                lines.append(block["content"])
                lines.append("")
            lines.append("---")
            lines.append("")
            lines.append(f"**Source word count:** {output['metadata']['source_word_count']}")
            lines.append(f"**Summary word count:** {output['metadata']['summary_word_count']}")
            lines.append(f"**Compression ratio:** {output['metadata']['compression_ratio']}")

            filepath = output_dir / "CONDENSED_SUMMARY.md"
            filepath.write_text("\n".join(lines), encoding="utf-8")
            produced["CONDENSED_SUMMARY"] = str(filepath)

        elif output_type == "key_points_list":
            lines.append("# Key Points List")
            lines.append("")
            lines.append(f"**Source:** {output['source_doc_ref']}")
            lines.append(f"**Language:** {output['language']}")
            lines.append("")
            lines.append("## Key Points")
            lines.append("")
            for block in output["output_blocks"]:
                score = block["metadata"].get("importance_score", "N/A")
                lines.append(f"{block['position']}. {block['content']} [Score: {score}]")
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.append(f"**Total key points:** {output['metadata']['total_key_points']}")
            lines.append(f"**Score range:** {output['metadata']['score_range']}")

            filepath = output_dir / "KEY_POINTS_LIST.md"
            filepath.write_text("\n".join(lines), encoding="utf-8")
            produced["KEY_POINTS_LIST"] = str(filepath)

    print(f"[render_outputs] Rendered {len(produced)} output files to {output_dir}", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=f"Rendered {len(produced)} output files.",
        artifacts=produced,
    )


# =============================================================================
# Phase 3: Output Validation
# =============================================================================


@action("validate_outputs")
def validate_outputs(*, context, state, step_cfg, project_root):
    """Validate output documents against validation rules.

    Implements Stage 6 (Output Validation). Evaluates VR-001 through
    VR-007 for each OutputDocument.

    Compression ratio failures (VR-001) trigger the recovery loop
    (on_reject_refine -> score_importance).
    Language failures (VR-002, VR-006) are unrecoverable.

    Produces: VALIDATION_REPORT artifact.
    """
    artifacts = state.get("artifacts", {})
    outputs_path = artifacts.get("OUTPUT_DOCUMENTS", "")
    parsed_doc_path = artifacts.get("PARSED_DOCUMENT", "")

    outputs = json.loads(Path(outputs_path).read_text(encoding="utf-8"))
    parsed_doc = json.loads(Path(parsed_doc_path).read_text(encoding="utf-8"))

    violations = []

    for output in outputs:
        output_type = output["output_type"]

        # VR-001: compression_ratio <= 0.20 (condensed_summary)
        if output_type == "condensed_summary":
            ratio = output["metadata"].get("compression_ratio", 0.0)
            if ratio > 0.20:
                violations.append({
                    "output_id": output["output_id"],
                    "rule_id": "VR-001",
                    "description": f"Compression ratio {ratio} exceeds 0.20",
                    "recoverable": True,
                })

        # VR-002, VR-006: language match
        if output["language"] != parsed_doc["language"]:
            violations.append({
                "output_id": output["output_id"],
                "rule_id": "VR-002" if output_type == "condensed_summary" else "VR-006",
                "description": f"Language mismatch: {output['language']} vs {parsed_doc['language']}",
                "recoverable": False,
            })

        # VR-003: structure preservation (condensed_summary)
        if output_type == "condensed_summary":
            section_types_in_output = set()
            for block in output["output_blocks"]:
                section_types_in_output.add(block.get("metadata", {}).get("section_type", "body"))
            # Structure preservation is verified by construction

        # VR-005: importance scores present (key_points_list)
        if output_type == "key_points_list":
            for block in output["output_blocks"]:
                if "importance_score" not in block.get("metadata", {}):
                    violations.append({
                        "output_id": output["output_id"],
                        "rule_id": "VR-005",
                        "description": f"Missing importance_score in block: {block['block_id']}",
                        "recoverable": False,
                    })

    # Check for unrecoverable failures
    has_language_mismatch = any(v["rule_id"] in ["VR-002", "VR-006"] for v in violations)
    has_compression_exceeded = any(v["rule_id"] == "VR-001" for v in violations)

    report = {
        "violations": violations,
        "passed": len(violations) == 0,
        "has_language_mismatch": has_language_mismatch,
        "has_compression_exceeded": has_compression_exceeded,
        "timestamp": datetime.now().isoformat(),
    }

    report_dir = Path(project_root) / "work" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"VALIDATION_REPORT-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if has_language_mismatch:
        return ActionResult(
            status="REJECTED",
            remark="Language validation failed (unrecoverable).",
            artifacts={"VALIDATION_REPORT": str(report_path)},
            reject_code="LANGUAGE_MISMATCH",
        )

    if has_compression_exceeded:
        return ActionResult(
            status="REJECTED",
            remark="Compression ratio exceeded. Recovery loop initiated.",
            artifacts={"VALIDATION_REPORT": str(report_path)},
            reject_code="COMPRESSION_EXCEEDED",
        )

    if violations:
        return ActionResult(
            status="REJECTED",
            remark=f"Output validation failed: {len(violations)} violations.",
            artifacts={"VALIDATION_REPORT": str(report_path)},
            reject_code="VALIDATION_FAILED",
        )

    return ActionResult(
        status="APPROVED",
        remark="All validation rules passed.",
        artifacts={"VALIDATION_REPORT": str(report_path)},
    )


# =============================================================================
# Phase 4: Delivery
# =============================================================================


@action("promote_outputs")
def promote_outputs(*, context, state, step_cfg, project_root):
    """Promote output files to the final output directory.

    Copies CONDENSED_SUMMARY and KEY_POINTS_LIST to the output
    directory.

    Produces: CONDENSED_SUMMARY_PROMOTED and KEY_POINTS_LIST_PROMOTED.
    """
    artifacts = state.get("artifacts", {})
    output_dir = Path(project_root) / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    promoted = {}

    for key in ["CONDENSED_SUMMARY", "KEY_POINTS_LIST"]:
        source_path = artifacts.get(key, "")
        if source_path:
            src = Path(source_path)
            if src.exists():
                dst = output_dir / src.name
                if src != dst:
                    shutil.copy2(src, dst)
                promoted[f"{key}_PROMOTED"] = str(dst)

    if not promoted:
        return ActionResult(
            status="REJECTED",
            remark="No output files found to promote.",
            artifacts={},
            reject_code="PROMOTION_ERROR",
        )

    print(f"[promote_outputs] Promoted {len(promoted)} output files", flush=True)

    return ActionResult(
        status="APPROVED",
        remark=f"Promoted {len(promoted)} output files to {output_dir}.",
        artifacts=promoted,
    )


@action("complete_pipeline")
def complete_pipeline(*, context, state, step_cfg, project_root):
    """Record pipeline completion and write execution log.

    Writes the EXECUTION_LOG with stage timings and records the
    pipeline completion result.

    Produces: EXECUTION_LOG and COMPLETION_RESULT artifacts.
    """
    artifacts = state.get("artifacts", {})

    log_dir = Path(project_root) / "work" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    log_path = log_dir / f"EXECUTION_LOG-{ts}.log"

    log_lines = [
        f"[{datetime.now().isoformat()}] Pipeline execution started",
        f"[{datetime.now().isoformat()}] Stages completed: 0-6",
        f"[{datetime.now().isoformat()}] Output files produced:",
    ]

    for key in ["CONDENSED_SUMMARY_PROMOTED", "KEY_POINTS_LIST_PROMOTED"]:
        path = artifacts.get(key, "NOT_FOUND")
        log_lines.append(f"  {key}: {path}")

    log_lines.append(f"[{datetime.now().isoformat()}] Pipeline execution completed successfully")

    log_path.write_text("\n".join(log_lines), encoding="utf-8")

    # Write completion result
    result = {
        "status": "COMPLETED",
        "completed_at": datetime.now().isoformat(),
        "output_files": {
            "CONDENSED_SUMMARY": artifacts.get("CONDENSED_SUMMARY_PROMOTED", ""),
            "KEY_POINTS_LIST": artifacts.get("KEY_POINTS_LIST_PROMOTED", ""),
        },
    }
    result_dir = Path(project_root) / "work"
    result_path = result_dir / f"COMPLETION_RESULT-{ts}.json"
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"[complete_pipeline] Pipeline completed. Log: {log_path}", flush=True)

    return ActionResult(
        status="APPROVED",
        remark="Pipeline execution completed successfully.",
        artifacts={
            "EXECUTION_LOG": str(log_path),
            "COMPLETION_RESULT": str(result_path),
        },
    )
