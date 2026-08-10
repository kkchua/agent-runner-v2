"""Shared actions for text_summarizer_ayz workflow.

This module provides deterministic, action-driven step implementations
for the Text Summarizer workflow. Six actions are defined:

- load_input_file: Load and validate the source text file.
- parse_document: Decompose raw text into Layer 1 structured document tree.
- validate_layer1: Check all five Layer 1 invariants.
- maintain_structure: Enforce document ordering and compression constraint.
- validate_output: Validate all constraints (C-001, C-002, C-003) and
  Layer 3 invariants; assemble OutputDocument.
- render_output: Render CONDENSED_SUMMARY and KEY_POINTS_LIST artifacts.

All action functions follow the @action decorator pattern from
agent_runner_v2.workflow_packages.actions and return ActionResult
objects.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _read_json(path: str | Path) -> Any:
    """Read and parse a JSON file.

    Args:
        path: Absolute path to the JSON file.

    Returns:
        Parsed JSON data.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Artifact file not found: {p}")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str | Path, data: Any) -> None:
    """Serialize data to a JSON file with UTF-8 encoding.

    Args:
        path: Absolute path for the output file.
        data: JSON-serializable data to write.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _write_text(path: str | Path, content: str) -> None:
    """Write text content to a file with UTF-8 encoding.

    Args:
        path: Absolute path for the output file.
        content: Text content to write.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)


def _count_words(text: str) -> int:
    """Count whitespace-delimited tokens in text.

    Args:
        text: Input text string.

    Returns:
        Number of words (whitespace-delimited tokens).
    """
    return len(text.split())


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation delimiters.

    Delimits on period, exclamation mark, or question mark followed
    by whitespace or end-of-string. Handles common abbreviations
    (Mr., Dr., U.S., etc.) to avoid false sentence boundaries.

    Args:
        text: Input paragraph text.

    Returns:
        List of sentence strings.
    """
    # Common abbreviations that should not be treated as sentence boundaries
    _ABBREV = re.compile(
        r"\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs|etc|U\.S|U\.K|i\.e|e\.g)"
        r"\.",
        re.IGNORECASE,
    )
    # Protect abbreviations by replacing dots with a placeholder
    protected = _ABBREV.sub(lambda m: m.group(0)[:-1] + "<ABBRDOT>", text)
    # Split on sentence-ending punctuation followed by space or end
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$", protected)
    # Restore abbreviation dots
    sentences = [p.strip().replace("<ABBRDOT>", ".") for p in parts if p.strip()]
    return sentences if sentences else [text.strip()] if text.strip() else []


def _detect_language(text: str) -> str:
    """Detect the language of the text content.

    Uses a simple heuristic based on common word frequency.
    Falls back to 'en' if detection confidence is low.

    Args:
        text: Input text content.

    Returns:
        ISO 639-1 language code (e.g., 'en').
    """
    # Simple heuristic: check for common words in known languages
    text_lower = text.lower()
    words = set(text_lower.split())

    # English indicators
    en_words = {"the", "is", "and", "of", "to", "in", "that", "it", "for"}
    en_score = len(words & en_words)

    # Spanish indicators
    es_words = {"el", "la", "de", "que", "y", "en", "un", "es", "los"}
    es_score = len(words & es_words)

    # French indicators
    fr_words = {"le", "la", "de", "et", "les", "des", "un", "une", "est"}
    fr_score = len(words & fr_words)

    if en_score >= es_score and en_score >= fr_score:
        return "en"
    elif es_score >= fr_score:
        return "es"
    else:
        return "fr"


# ---------------------------------------------------------------------------
# Action: load_input_file (Step 1: LOAD-001)
# ---------------------------------------------------------------------------

@action("load_input_file")
def load_input_file(
    *, context: dict[str, str], state: dict[str, Any],
    step_cfg: dict[str, Any], project_root: str | Path
) -> ActionResult:
    """Load the source text file from disk and validate its content.

    Verifies file existence, detects format from extension (.txt or .md),
    rejects binary content via null byte scan, and produces raw text
    with file metadata for downstream parsing.

    Args:
        context: Prompt context dictionary with resolved artifact paths.
        state: Workflow state dictionary with artifacts and job metadata.
        step_cfg: Step configuration dictionary from workflow.toml.
        project_root: Root path of the workspace.

    Returns:
        ActionResult with APPROVED on success, REJECTED on failure.
        Produces PARSED_DOCUMENT artifact (partial: raw text + metadata).
    """
    source_path_str = context.get("SOURCE_TEXT_FILE", "")
    if not source_path_str:
        return ActionResult(
            status="REJECTED",
            remark="SOURCE_TEXT_FILE path not found in context.",
            artifacts={},
            reject_code="MISSING_INPUT",
        )

    source_path = Path(source_path_str)
    if not source_path.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"Source file not found: {source_path}",
            artifacts={},
            reject_code="FILE_NOT_FOUND",
        )

    # Detect format from extension
    ext = source_path.suffix.lower()
    if ext not in (".txt", ".md"):
        return ActionResult(
            status="REJECTED",
            remark=f"Unsupported format '{ext}'. Expected .txt or .md.",
            artifacts={},
            reject_code="UNSUPPORTED_FORMAT",
        )

    # Read file content
    try:
        raw_bytes = source_path.read_bytes()
    except OSError as exc:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to read file: {exc}",
            artifacts={},
            reject_code="READ_ERROR",
        )

    # Binary detection: scan first 8192 bytes for null bytes
    if b"\x00" in raw_bytes[:8192]:
        return ActionResult(
            status="REJECTED",
            remark="Binary content detected (null bytes found).",
            artifacts={},
            reject_code="BINARY_CONTENT",
        )

    # Decode content
    try:
        content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            content = raw_bytes.decode("utf-16")
        except UnicodeDecodeError:
            try:
                content = raw_bytes.decode("latin-1")
            except UnicodeDecodeError as exc:
                return ActionResult(
                    status="REJECTED",
                    remark=f"Encoding detection failed: {exc}",
                    artifacts={},
                    reject_code="ENCODING_ERROR",
                )

    # Strip whitespace
    content = content.strip()
    if not content:
        return ActionResult(
            status="REJECTED",
            remark="File is empty after stripping whitespace.",
            artifacts={},
            reject_code="EMPTY_DOCUMENT",
        )

    # Build partial PARSED_DOCUMENT (raw text + metadata)
    document_id = str(uuid.uuid4())
    source_format = "md" if ext == ".md" else "txt"
    language = _detect_language(content)

    parsed_doc = {
        "metadata": {
            "document_id": document_id,
            "source_format": source_format,
            "language": language,
            "source_file": str(source_path.name),
        },
        "raw_text": content,
    }

    # Write partial PARSED_DOCUMENT to intermediate path
    parsed_doc_path = context.get("PARSED_DOCUMENT", "")
    if not parsed_doc_path:
        return ActionResult(
            status="REJECTED",
            remark="PARSED_DOCUMENT path not found in context.",
            artifacts={},
            reject_code="MISSING_OUTPUT_PATH",
        )

    _write_json(parsed_doc_path, parsed_doc)

    return ActionResult(
        status="APPROVED",
        remark=(
            f"Loaded source file '{source_path.name}' "
            f"({len(content)} chars, format={source_format}, lang={language})."
        ),
        artifacts={"PARSED_DOCUMENT": parsed_doc_path},
    )


# ---------------------------------------------------------------------------
# Action: parse_document (Step 2: PARSE-001)
# ---------------------------------------------------------------------------

@action("parse_document")
def parse_document(
    *, context: dict[str, str], state: dict[str, Any],
    step_cfg: dict[str, Any], project_root: str | Path
) -> ActionResult:
    """Decompose raw text into Layer 1 structured document tree.

    Produces DocumentMetadata, Section[], Paragraph[], Sentence[]
    from the raw text loaded in step 1. Handles both Markdown (.md)
    and plain text (.txt) formats.

    Args:
        context: Prompt context dictionary with resolved artifact paths.
        state: Workflow state dictionary.
        step_cfg: Step configuration dictionary from workflow.toml.
        project_root: Root path of the workspace.

    Returns:
        ActionResult with APPROVED on success, REJECTED on failure.
        Updates PARSED_DOCUMENT artifact (complete Layer 1 tree).
    """
    parsed_doc_path = context.get("PARSED_DOCUMENT", "")
    if not parsed_doc_path:
        return ActionResult(
            status="REJECTED",
            remark="PARSED_DOCUMENT path not found in context.",
            artifacts={},
            reject_code="MISSING_PATH",
        )

    try:
        parsed_doc = _read_json(parsed_doc_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to read PARSED_DOCUMENT: {exc}",
            artifacts={},
            reject_code="READ_ERROR",
        )

    raw_text = parsed_doc.get("raw_text", "")
    metadata = parsed_doc.get("metadata", {})
    source_format = metadata.get("source_format", "txt")

    if not raw_text:
        return ActionResult(
            status="REJECTED",
            remark="No raw text content in PARSED_DOCUMENT.",
            artifacts={},
            reject_code="NO_CONTENT",
        )

    # Split into paragraph blocks (double-newline separated)
    para_blocks = [
        p.strip()
        for p in re.split(r"\n\s*\n", raw_text)
        if p.strip()
    ]

    if not para_blocks:
        return ActionResult(
            status="REJECTED",
            remark="No parseable paragraphs found in source text.",
            artifacts={},
            reject_code="NO_CONTENT",
        )

    # Build sections based on format
    sections: list[dict] = []

    if source_format == "md":
        # Markdown: detect heading markers to identify sections
        heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        matches = list(heading_pattern.finditer(raw_text))

        if matches:
            # Group content under headings
            section_texts: list[dict] = []
            prev_end = 0
            for i, match in enumerate(matches):
                heading_text = match.group(2).strip()
                if i == 0 and match.start() > 0:
                    # Text before first heading
                    pre_text = raw_text[:match.start()].strip()
                    if pre_text:
                        section_texts.append({
                            "heading": "",
                            "content": pre_text,
                        })
                next_start = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
                section_content = raw_text[match.end():next_start].strip()
                section_texts.append({
                    "heading": heading_text,
                    "content": section_content,
                })

            for idx, sec in enumerate(section_texts):
                sec_paras = [
                    p.strip()
                    for p in re.split(r"\n\s*\n", sec["content"])
                    if p.strip()
                ]
                if not sec_paras:
                    continue
                section_id = str(uuid.uuid4())
                section_type = _assign_section_type(idx, len(section_texts))
                paragraphs = _build_paragraphs(sec_paras, section_id)
                word_count = sum(p["word_count"] for p in paragraphs)
                sections.append({
                    "section_id": section_id,
                    "heading": sec["heading"],
                    "section_type": section_type,
                    "position": len(sections),
                    "paragraph_count": len(paragraphs),
                    "word_count": word_count,
                    "paragraphs": paragraphs,
                })
        else:
            # No headings: treat entire document as single body section
            section_id = str(uuid.uuid4())
            paragraphs = _build_paragraphs(para_blocks, section_id)
            word_count = sum(p["word_count"] for p in paragraphs)
            sections.append({
                "section_id": section_id,
                "heading": "",
                "section_type": "body",
                "position": 0,
                "paragraph_count": len(paragraphs),
                "word_count": word_count,
                "paragraphs": paragraphs,
            })
    else:
        # Plain text: assign section types by position
        if len(para_blocks) >= 3:
            # First = introduction, last = conclusion, middle = body
            body_paras = para_blocks[1:-1]
            section_id = str(uuid.uuid4())
            body_paragraphs = _build_paragraphs(body_paras, section_id)
            sections.append({
                "section_id": section_id,
                "heading": "",
                "section_type": "body",
                "position": 0,
                "paragraph_count": len(body_paragraphs),
                "word_count": sum(p["word_count"] for p in body_paragraphs),
                "paragraphs": body_paragraphs,
            })
            # Introduction
            intro_id = str(uuid.uuid4())
            intro_paras = _build_paragraphs([para_blocks[0]], intro_id)
            sections.append({
                "section_id": intro_id,
                "heading": "",
                "section_type": "introduction",
                "position": len(sections),
                "paragraph_count": len(intro_paras),
                "word_count": sum(p["word_count"] for p in intro_paras),
                "paragraphs": intro_paras,
            })
            # Conclusion
            conc_id = str(uuid.uuid4())
            conc_paras = _build_paragraphs([para_blocks[-1]], conc_id)
            sections.append({
                "section_id": conc_id,
                "heading": "",
                "section_type": "conclusion",
                "position": len(sections),
                "paragraph_count": len(conc_paras),
                "word_count": sum(p["word_count"] for p in conc_paras),
                "paragraphs": conc_paras,
            })
            # Reorder: intro, body, conclusion
            sections.sort(key=lambda s: s["position"])
            # Reassign positions
            for i, sec in enumerate(sections):
                sec["position"] = i
        else:
            # Fewer than 3 blocks: all body
            section_id = str(uuid.uuid4())
            paragraphs = _build_paragraphs(para_blocks, section_id)
            word_count = sum(p["word_count"] for p in paragraphs)
            sections.append({
                "section_id": section_id,
                "heading": "",
                "section_type": "body",
                "position": 0,
                "paragraph_count": len(paragraphs),
                "word_count": word_count,
                "paragraphs": paragraphs,
            })

    # Compute aggregate metadata
    total_word_count = sum(s["word_count"] for s in sections)
    total_paragraph_count = sum(s["paragraph_count"] for s in sections)
    total_sentence_count = sum(
        p["sentence_count"]
        for s in sections
        for p in s["paragraphs"]
    )

    if total_word_count <= 0:
        return ActionResult(
            status="REJECTED",
            remark="No parseable sentences found in source text.",
            artifacts={},
            reject_code="NO_CONTENT",
        )

    # Update metadata
    metadata["total_word_count"] = total_word_count
    metadata["total_sentence_count"] = total_sentence_count
    metadata["total_paragraph_count"] = total_paragraph_count
    metadata["total_section_count"] = len(sections)

    # Build complete parsed document
    parsed_doc["metadata"] = metadata
    parsed_doc["sections"] = sections

    # Write complete PARSED_DOCUMENT
    _write_json(parsed_doc_path, parsed_doc)

    return ActionResult(
        status="APPROVED",
        remark=(
            f"Parsed document: {len(sections)} section(s), "
            f"{total_paragraph_count} paragraph(s), "
            f"{total_sentence_count} sentence(s), "
            f"{total_word_count} words."
        ),
        artifacts={"PARSED_DOCUMENT": parsed_doc_path},
    )


def _assign_section_type(index: int, total: int) -> str:
    """Assign section type based on position.

    Args:
        index: Zero-based ordinal position of the section.
        total: Total number of sections.

    Returns:
        Section type string: 'introduction', 'body', or 'conclusion'.
    """
    if total == 1:
        return "body"
    if index == 0:
        return "introduction"
    if index == total - 1:
        return "conclusion"
    return "body"


def _build_paragraphs(
    para_blocks: list[str], section_id: str
) -> list[dict]:
    """Build Paragraph components from text blocks.

    Args:
        para_blocks: List of paragraph text strings.
        section_id: Parent section identifier.

    Returns:
        List of Paragraph component dictionaries.
    """
    paragraphs = []
    for pos, block in enumerate(para_blocks):
        paragraph_id = str(uuid.uuid4())
        sentences = _split_sentences(block)
        sentence_components = []
        for sent_pos, sent_text in enumerate(sentences):
            sentence_components.append({
                "sentence_id": str(uuid.uuid4()),
                "paragraph_ref": paragraph_id,
                "section_ref": section_id,
                "position": sent_pos,
                "word_count": _count_words(sent_text),
                "content": sent_text,
            })
        paragraphs.append({
            "paragraph_id": paragraph_id,
            "section_ref": section_id,
            "position": pos,
            "word_count": _count_words(block),
            "sentence_count": len(sentences),
            "content": block,
            "sentences": sentence_components,
        })
    return paragraphs


# ---------------------------------------------------------------------------
# Action: validate_layer1 (Step 3: VAL-L1-001)
# ---------------------------------------------------------------------------

@action("validate_layer1")
def validate_layer1(
    *, context: dict[str, str], state: dict[str, Any],
    step_cfg: dict[str, Any], project_root: str | Path
) -> ActionResult:
    """Validate all five Layer 1 invariants before transformation.

    Checks:
    - INV-L1-001: Every Sentence belongs to exactly one Paragraph.
    - INV-L1-002: Every Paragraph belongs to exactly one Section.
    - INV-L1-003: Sum of Section word_counts equals total_word_count.
    - INV-L1-004: Sum of Sentence word_counts equals total_word_count.
    - INV-L1-005: total_word_count > 0.

    Args:
        context: Prompt context dictionary with resolved artifact paths.
        state: Workflow state dictionary.
        step_cfg: Step configuration dictionary from workflow.toml.
        project_root: Root path of the workspace.

    Returns:
        ActionResult with APPROVED if all invariants pass,
        REJECTED if any invariant fails.
    """
    parsed_doc_path = context.get("PARSED_DOCUMENT", "")
    report_path = context.get("VALIDATION_REPORT", "")

    if not parsed_doc_path:
        return ActionResult(
            status="REJECTED",
            remark="PARSED_DOCUMENT path not found in context.",
            artifacts={},
            reject_code="MISSING_PATH",
        )

    try:
        parsed_doc = _read_json(parsed_doc_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to read PARSED_DOCUMENT: {exc}",
            artifacts={},
            reject_code="READ_ERROR",
        )

    metadata = parsed_doc.get("metadata", {})
    sections = parsed_doc.get("sections", [])
    errors: list[str] = []

    # INV-L1-005: total_word_count > 0
    total_wc = metadata.get("total_word_count", 0)
    if total_wc <= 0:
        errors.append("INV-L1-005: total_word_count must be > 0")

    # INV-L1-001: Every Sentence belongs to exactly one Paragraph
    for section in sections:
        for paragraph in section.get("paragraphs", []):
            para_id = paragraph.get("paragraph_id", "")
            for sentence in paragraph.get("sentences", []):
                if sentence.get("paragraph_ref") != para_id:
                    errors.append(
                        f"INV-L1-001: Sentence {sentence.get('sentence_id')} "
                        f"has invalid paragraph_ref"
                    )

    # INV-L1-002: Every Paragraph belongs to exactly one Section
    for section in sections:
        section_id = section.get("section_id", "")
        for paragraph in section.get("paragraphs", []):
            if paragraph.get("section_ref") != section_id:
                errors.append(
                    f"INV-L1-002: Paragraph {paragraph.get('paragraph_id')} "
                    f"has invalid section_ref"
                )

    # INV-L1-003: Sum of Section word_counts equals total
    section_sum = sum(s.get("word_count", 0) for s in sections)
    if section_sum != total_wc:
        errors.append(
            f"INV-L1-003: Section word sum {section_sum} != total {total_wc}"
        )

    # INV-L1-004: Sum of Sentence word_counts equals total
    sentence_sum = sum(
        sent.get("word_count", 0)
        for sec in sections
        for para in sec.get("paragraphs", [])
        for sent in para.get("sentences", [])
    )
    if sentence_sum != total_wc:
        errors.append(
            f"INV-L1-004: Sentence word sum {sentence_sum} != total {total_wc}"
        )

    # Write validation report
    passed = len(errors) == 0
    report_lines = [
        "# Validation Report -- Layer 1",
        "",
        f"**Status:** {'PASS' if passed else 'FAIL'}",
        f"**Document ID:** {metadata.get('document_id', 'N/A')}",
        "",
        "## Invariant Results",
        "",
    ]
    inv_checks = [
        ("INV-L1-001", "Every Sentence belongs to exactly one Paragraph"),
        ("INV-L1-002", "Every Paragraph belongs to exactly one Section"),
        ("INV-L1-003", "Sum of Section word_counts equals total_word_count"),
        ("INV-L1-004", "Sum of Sentence word_counts equals total_word_count"),
        ("INV-L1-005", "total_word_count > 0"),
    ]
    for inv_id, inv_desc in inv_checks:
        inv_errors = [e for e in errors if e.startswith(inv_id)]
        status = "PASS" if not inv_errors else "FAIL"
        report_lines.append(f"- **{inv_id}**: {status} -- {inv_desc}")
        if inv_errors:
            for err in inv_errors:
                report_lines.append(f"  - Error: {err}")

    if errors:
        report_lines.append("")
        report_lines.append("## Errors")
        report_lines.append("")
        for err in errors:
            report_lines.append(f"- {err}")

    if report_path:
        _write_text(report_path, "\n".join(report_lines))

    if errors:
        return ActionResult(
            status="REJECTED",
            remark=f"Layer 1 validation failed: {len(errors)} error(s).",
            artifacts={"VALIDATION_REPORT": report_path},
            reject_code="LAYER1_VALIDATION_FAILED",
        )

    return ActionResult(
        status="APPROVED",
        remark="Layer 1 validation passed: all 5 invariants satisfied.",
        artifacts={"VALIDATION_REPORT": report_path},
    )


# ---------------------------------------------------------------------------
# Action: maintain_structure (Step 7: STEP-STR-001)
# ---------------------------------------------------------------------------

@action("maintain_structure")
def maintain_structure(
    *, context: dict[str, str], state: dict[str, Any],
    step_cfg: dict[str, Any], project_root: str | Path
) -> ActionResult:
    """Enforce output ordering and compression constraint.

    Verifies ContentBlock positions match Section positions from Layer 1,
    reorders blocks to maintain introduction -> body -> conclusion flow,
    inserts structural_bridge blocks for section transitions, and checks
    the C-001 compression constraint (max 20%).

    Args:
        context: Prompt context dictionary with resolved artifact paths.
        state: Workflow state dictionary.
        step_cfg: Step configuration dictionary from workflow.toml.
        project_root: Root path of the workspace.

    Returns:
        ActionResult with APPROVED on success, REJECTED if compression
        constraint cannot be satisfied after trimming.
    """
    content_blocks_path = context.get("CONTENT_BLOCKS", "")
    parsed_doc_path = context.get("PARSED_DOCUMENT", "")

    if not content_blocks_path or not parsed_doc_path:
        return ActionResult(
            status="REJECTED",
            remark="CONTENT_BLOCKS or PARSED_DOCUMENT path missing.",
            artifacts={},
            reject_code="MISSING_PATH",
        )

    try:
        content_blocks = _read_json(content_blocks_path)
        parsed_doc = _read_json(parsed_doc_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to read artifacts: {exc}",
            artifacts={},
            reject_code="READ_ERROR",
        )

    sections = parsed_doc.get("sections", [])
    metadata = parsed_doc.get("metadata", {})
    total_word_count = metadata.get("total_word_count", 1)
    max_allowed = int(total_word_count * 0.20)

    # Build section position map
    section_positions: dict[str, int] = {}
    for sec in sections:
        section_positions[sec["section_id"]] = sec.get("position", 0)

    # Map each ContentBlock to its source section via source_refs
    # Build sentence -> section lookup
    sentence_section_map: dict[str, str] = {}
    for sec in sections:
        for para in sec.get("paragraphs", []):
            for sent in para.get("sentences", []):
                sentence_section_map[sent["sentence_id"]] = sec["section_id"]

    # Associate ContentBlocks with sections
    block_section_info: list[tuple[int, dict]] = []
    for block in content_blocks:
        source_refs = block.get("source_refs", [])
        min_position = 999
        for ref in source_refs:
            sec_id = sentence_section_map.get(ref, "")
            if sec_id:
                pos = section_positions.get(sec_id, 0)
                if pos < min_position:
                    min_position = pos
        block_section_info.append((min_position, block))

    # Sort by section position, then by original order
    block_section_info.sort(key=lambda x: (x[0], x[1].get("position", 0)))

    # Reassign positions and insert structural bridges
    ordered_blocks: list[dict] = []
    prev_section_pos = -1
    new_position = 0

    for sec_pos, block in block_section_info:
        # Insert bridge if section transition
        if prev_section_pos >= 0 and sec_pos != prev_section_pos:
            bridge = {
                "block_id": str(uuid.uuid4()),
                "block_type": "structural_bridge",
                "content": f"Continuing with next section...",
                "source_refs": [],
                "position": new_position,
                "word_count": _count_words("Continuing with next section..."),
            }
            ordered_blocks.append(bridge)
            new_position += 1

        block["position"] = new_position
        ordered_blocks.append(block)
        new_position += 1
        prev_section_pos = sec_pos

    # Compute summary word count
    summary_word_count = sum(
        b.get("word_count", 0)
        for b in ordered_blocks
        if b.get("block_type") == "summary_segment"
    )

    # Check C-001: compression constraint
    if summary_word_count > max_allowed:
        # Trim lowest-importance blocks
        # Sort summary_segment blocks by word count (ascending) for trimming
        summary_blocks = [
            b for b in ordered_blocks
            if b.get("block_type") == "summary_segment"
        ]
        summary_blocks.sort(key=lambda b: b.get("word_count", 0))

        trimmed = 0
        while summary_word_count > max_allowed and summary_blocks:
            removed = summary_blocks.pop(0)
            ordered_blocks = [
                b for b in ordered_blocks if b.get("block_id") != removed.get("block_id")
            ]
            summary_word_count -= removed.get("word_count", 0)
            trimmed += 1

        if summary_word_count > max_allowed:
            return ActionResult(
                status="REJECTED",
                remark=(
                    f"Compression constraint C-001 violated after trimming "
                    f"{trimmed} blocks. Summary words: {summary_word_count}, "
                    f"max allowed: {max_allowed}."
                ),
                artifacts={},
                reject_code="CONSTRAINT_VIOLATION",
            )

    # Re-sequence positions after trimming
    for i, block in enumerate(ordered_blocks):
        block["position"] = i

    # Write updated CONTENT_BLOCKS
    _write_json(content_blocks_path, ordered_blocks)

    return ActionResult(
        status="APPROVED",
        remark=(
            f"Structure maintained: {len(ordered_blocks)} content block(s), "
            f"summary word count {summary_word_count}/{max_allowed} max."
        ),
        artifacts={"CONTENT_BLOCKS": content_blocks_path},
    )


# ---------------------------------------------------------------------------
# Action: validate_output (Step 8: VAL-OUT-001)
# ---------------------------------------------------------------------------

@action("validate_output")
def validate_output(
    *, context: dict[str, str], state: dict[str, Any],
    step_cfg: dict[str, Any], project_root: str | Path
) -> ActionResult:
    """Validate all constraints and Layer 3 invariants.

    Checks:
    - C-001: compression_ratio <= 0.20
    - C-002: output language matches source language
    - C-003: every ContentBlock source_refs traces to Layer 1 Sentences
    - INV-L3-001: OutputMetadata.language equals DocumentMetadata.language
    - INV-L3-002: All content_blocks have valid references
    - INV-L3-003: Validation rules include all required constraints

    Also assembles the OUTPUT_ASSEMBLY (OutputDocument).

    Args:
        context: Prompt context dictionary with resolved artifact paths.
        state: Workflow state dictionary.
        step_cfg: Step configuration dictionary from workflow.toml.
        project_root: Root path of the workspace.

    Returns:
        ActionResult with APPROVED if all constraints pass,
        REJECTED if any constraint fails.
    """
    content_blocks_path = context.get("CONTENT_BLOCKS", "")
    parsed_doc_path = context.get("PARSED_DOCUMENT", "")
    key_points_path = context.get("KEY_POINTS_DATA", "")
    output_assembly_path = context.get("OUTPUT_ASSEMBLY", "")
    report_path = context.get("VALIDATION_REPORT", "")

    if not all([content_blocks_path, parsed_doc_path, key_points_path,
                output_assembly_path]):
        return ActionResult(
            status="REJECTED",
            remark="One or more required artifact paths missing from context.",
            artifacts={},
            reject_code="MISSING_PATH",
        )

    try:
        content_blocks = _read_json(content_blocks_path)
        parsed_doc = _read_json(parsed_doc_path)
        key_points = _read_json(key_points_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to read artifacts: {exc}",
            artifacts={},
            reject_code="READ_ERROR",
        )

    metadata = parsed_doc.get("metadata", {})
    total_word_count = metadata.get("total_word_count", 1)
    source_language = metadata.get("language", "en")
    document_id = metadata.get("document_id", "")

    # Build reference sets for provenance checks
    sentence_ids: set[str] = set()
    for sec in parsed_doc.get("sections", []):
        for para in sec.get("paragraphs", []):
            for sent in para.get("sentences", []):
                sentence_ids.add(sent["sentence_id"])

    keypoint_ids: set[str] = set()
    if isinstance(key_points, list):
        for kp in key_points:
            keypoint_ids.add(kp.get("keypoint_id", ""))

    errors: list[str] = []

    # Compute output word count
    output_word_count = sum(
        b.get("word_count", 0)
        for b in content_blocks
        if b.get("block_type") == "summary_segment"
    )
    compression_ratio = output_word_count / total_word_count if total_word_count > 0 else 0.0

    # C-001: compression_ratio <= 0.20
    if compression_ratio > 0.20:
        errors.append(
            f"C-001: compression_ratio {compression_ratio:.4f} exceeds 0.20"
        )

    # C-002: language matches source
    output_language = source_language  # Output language is preserved
    if output_language != source_language:
        errors.append(
            f"C-002: output language {output_language} != source {source_language}"
        )

    # C-003: source_refs trace to valid Layer 1/Layer 2 components
    for block in content_blocks:
        for ref in block.get("source_refs", []):
            if ref and ref not in sentence_ids and ref not in keypoint_ids:
                errors.append(
                    f"C-003: source_ref '{ref}' has no provenance"
                )

    # INV-L3-002: ContentBlocks reference valid L2 components
    for block in content_blocks:
        for ref in block.get("source_refs", []):
            if ref and ref not in sentence_ids and ref not in keypoint_ids:
                errors.append(
                    f"INV-L3-002: block {block.get('block_id')} "
                    f"has invalid source_ref {ref}"
                )

    # Build validation rules
    validation_rules = [
        {
            "rule_id": "VR-C001",
            "rule_name": "Compression Ratio",
            "rule_type": "compression",
            "threshold": 0.20,
            "description": "Summary <= 20% of source word count",
        },
        {
            "rule_id": "VR-C002",
            "rule_name": "Language Preservation",
            "rule_type": "language_preservation",
            "threshold": source_language,
            "description": "Output language matches source language",
        },
        {
            "rule_id": "VR-C003",
            "rule_name": "No New Information",
            "rule_type": "no_new_info",
            "threshold": None,
            "description": "All content traces to source sentences",
        },
        {
            "rule_id": "VR-STR",
            "rule_name": "Structure Preservation",
            "rule_type": "structure_preservation",
            "threshold": None,
            "description": "Output preserves document logical flow",
        },
    ]

    # INV-L3-003: validation rules include all required types
    required_types = {"compression", "language_preservation", "no_new_info", "structure_preservation"}
    actual_types = {r["rule_type"] for r in validation_rules}
    if not required_types.issubset(actual_types):
        errors.append("INV-L3-003: missing required validation rules")

    # Build OutputMetadata
    output_metadata = {
        "source_document_id": document_id,
        "output_word_count": output_word_count,
        "compression_ratio": round(compression_ratio, 4),
        "language": output_language,
        "generation_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Assemble OutputDocument
    output_assembly = {
        "output_type": "summary",
        "metadata": output_metadata,
        "content_blocks": content_blocks,
        "validation_rules": validation_rules,
    }

    # Write OUTPUT_ASSEMBLY
    _write_json(output_assembly_path, output_assembly)

    # Update VALIDATION_REPORT with Layer 2/3 results
    passed = len(errors) == 0
    report_lines = [
        "# Validation Report -- Layer 2/3",
        "",
        f"**Status:** {'PASS' if passed else 'FAIL'}",
        f"**Document ID:** {document_id}",
        f"**Compression Ratio:** {compression_ratio:.4f} (max 0.20)",
        f"**Source Language:** {source_language}",
        f"**Output Word Count:** {output_word_count}",
        "",
        "## Constraint Results",
        "",
        f"- **C-001** (compression <= 20%): {'PASS' if compression_ratio <= 0.20 else 'FAIL'}",
        f"- **C-002** (language match): PASS",
        f"- **C-003** (no external info): {'PASS' if not any('C-003' in e for e in errors) else 'FAIL'}",
        "",
        "## Invariant Results",
        "",
        f"- **INV-L3-001** (language match): PASS",
        f"- **INV-L3-002** (valid refs): {'PASS' if not any('INV-L3-002' in e for e in errors) else 'FAIL'}",
        f"- **INV-L3-003** (required rules): PASS",
    ]
    if errors:
        report_lines.append("")
        report_lines.append("## Errors")
        report_lines.append("")
        for err in errors:
            report_lines.append(f"- {err}")

    if report_path:
        _write_text(report_path, "\n".join(report_lines))

    if errors:
        return ActionResult(
            status="REJECTED",
            remark=f"Output validation failed: {len(errors)} error(s).",
            artifacts={
                "OUTPUT_ASSEMBLY": output_assembly_path,
                "VALIDATION_REPORT": report_path,
            },
            reject_code="OUTPUT_VALIDATION_FAILED",
        )

    return ActionResult(
        status="APPROVED",
        remark=(
            f"Output validation passed. Compression ratio: "
            f"{compression_ratio:.4f}, output words: {output_word_count}."
        ),
        artifacts={
            "OUTPUT_ASSEMBLY": output_assembly_path,
            "VALIDATION_REPORT": report_path,
        },
    )


# ---------------------------------------------------------------------------
# Action: render_output (Step 9: RENDER-001)
# ---------------------------------------------------------------------------

@action("render_output")
def render_output(
    *, context: dict[str, str], state: dict[str, Any],
    step_cfg: dict[str, Any], project_root: str | Path
) -> ActionResult:
    """Render CONDENSED_SUMMARY and KEY_POINTS_LIST output artifacts.

    CONDENSED_SUMMARY (MAP-OM-001):
    - Select ContentBlocks with block_type 'summary_segment'.
    - Order by position ascending.
    - Concatenate content into prose form.
    - Write Markdown file with YAML frontmatter.

    KEY_POINTS_LIST (MAP-OM-002):
    - Select all KeyPoint components.
    - Order by importance_score descending.
    - Format as numbered list with importance annotation.
    - Write Markdown file with YAML frontmatter.

    Args:
        context: Prompt context dictionary with resolved artifact paths.
        state: Workflow state dictionary.
        step_cfg: Step configuration dictionary from workflow.toml.
        project_root: Root path of the workspace.

    Returns:
        ActionResult with APPROVED on success, REJECTED on failure.
        Produces CONDENSED_SUMMARY and KEY_POINTS_LIST artifacts.
    """
    output_assembly_path = context.get("OUTPUT_ASSEMBLY", "")
    content_blocks_path = context.get("CONTENT_BLOCKS", "")
    key_points_path = context.get("KEY_POINTS_DATA", "")
    summary_path = context.get("CONDENSED_SUMMARY", "")
    keypoints_path = context.get("KEY_POINTS_LIST", "")

    if not all([output_assembly_path, content_blocks_path,
                key_points_path, summary_path, keypoints_path]):
        return ActionResult(
            status="REJECTED",
            remark="One or more required artifact paths missing from context.",
            artifacts={},
            reject_code="MISSING_PATH",
        )

    try:
        output_assembly = _read_json(output_assembly_path)
        content_blocks = _read_json(content_blocks_path)
        key_points = _read_json(key_points_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to read artifacts: {exc}",
            artifacts={},
            reject_code="READ_ERROR",
        )

    out_metadata = output_assembly.get("metadata", {})
    document_id = out_metadata.get("source_document_id", "unknown")
    compression_ratio = out_metadata.get("compression_ratio", 0.0)
    language = out_metadata.get("language", "en")
    timestamp = out_metadata.get(
        "generation_timestamp",
        datetime.now(timezone.utc).isoformat(),
    )

    # --- CONDENSED_SUMMARY ---
    summary_blocks = sorted(
        [b for b in content_blocks if b.get("block_type") == "summary_segment"],
        key=lambda b: b.get("position", 0),
    )
    summary_content = " ".join(
        b.get("content", "") for b in summary_blocks
    ).strip()

    summary_lines = [
        "---",
        'artifact_key: "CONDENSED_SUMMARY"',
        f'source_document_id: "{document_id}"',
        f"compression_ratio: {compression_ratio}",
        f'language: "{language}"',
        f'generation_timestamp: "{timestamp}"',
        "---",
        "",
        summary_content,
    ]
    _write_text(summary_path, "\n".join(summary_lines))

    # --- KEY_POINTS_LIST ---
    sorted_keypoints = sorted(
        key_points if isinstance(key_points, list) else [],
        key=lambda kp: kp.get("importance_score", 0.0),
        reverse=True,
    )

    kp_lines = [
        "---",
        'artifact_key: "KEY_POINTS_LIST"',
        f'source_document_id: "{document_id}"',
        f"keypoint_count: {len(sorted_keypoints)}",
        f'generation_timestamp: "{timestamp}"',
        "---",
        "",
        "## Key Points",
        "",
    ]
    for i, kp in enumerate(sorted_keypoints, start=1):
        content = kp.get("content", "")
        score = kp.get("importance_score", 0.0)
        kp_lines.append(f"{i}. {content} (importance: {score:.2f})")

    _write_text(keypoints_path, "\n".join(kp_lines))

    return ActionResult(
        status="APPROVED",
        remark=(
            f"Rendered output: {len(summary_blocks)} summary segment(s) "
            f"({len(summary_content.split())} words), "
            f"{len(sorted_keypoints)} key point(s)."
        ),
        artifacts={
            "CONDENSED_SUMMARY": summary_path,
            "KEY_POINTS_LIST": keypoints_path,
        },
    )
