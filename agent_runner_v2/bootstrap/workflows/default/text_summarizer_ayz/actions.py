"""Shared action functions for Text Summarizer workflow (text_summarizer_ayz).

Contains action implementations for action-driven steps that are shared
across all implementations (default and key_points). Implementation-specific
actions live in impls/{name}/actions.py.

Action-driven steps in this workflow:
  Step 1: parse_input_document  -- Input parsing and validation
  Step 5: render_summary        -- Default output rendering (3-block prose)
  Step 6: validate_summary      -- Default output validation
  Step 7: step_completion       -- Terminal job finalization

Extension points implemented:
  EP-001: InputParser Protocol (parse_input_document)
  EP-003: OutputRenderer Protocol (render_summary)
  EP-004: ValidationStrategy Protocol (validate_summary)
"""

import json
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class DocumentContext:
    """M-DOC-001: Top-level container for parsed document metadata."""

    source_language: str
    source_format: str
    source_word_count: int
    source_file_path: str
    paragraph_count: int
    sentence_count: int


@dataclass
class TextSegment:
    """M-SEG-001: A single text unit extracted from the document."""

    segment_id: str
    content: str
    segment_type: str  # "sentence" or "paragraph"
    position: int
    region: str | None  # None, "intro", "body", "conclusion"
    word_count: int


@dataclass
class Paragraph:
    """M-PAR-001: A grouping of sequential text segments."""

    paragraph_id: str
    segment_ids: list[str]
    position: int
    word_count: int


@dataclass
class AnalyzedSegment:
    """M-ANL-001: A TextSegment enriched with analysis metadata."""

    segment_id: str
    importance_score: float
    is_redundant: bool
    redundancy_cluster_id: str | None
    is_core_message: bool
    original_content: str


@dataclass
class RedundancyCluster:
    """M-CLU-001: A group of semantically redundant segments."""

    cluster_id: str
    representative_segment_id: str
    member_segment_ids: list[str]
    redundancy_type: str  # "repetition", "elaboration", "restatement"


@dataclass
class DocumentProfile:
    """M-PRF-001: Summary analysis of the entire document."""

    core_thesis: str
    region_segments: dict[str, list[str]]
    total_unique_assertions: int
    importance_distribution: list[float]
    mean_importance: float


@dataclass
class OutputMetadata:
    """M-OUT-002: Provenance information for the output document."""

    source_language: str
    source_word_count: int
    output_word_count: int
    compression_ratio: float
    implementation: str
    generation_timestamp: str


@dataclass
class SummaryContentBlock:
    """M-OUT-003: Content block for summary output type."""

    block_type: str  # "intro", "main_points", "conclusion"
    prose: str
    source_segment_ids: list[str]


@dataclass
class KeyPointContentBlock:
    """M-OUT-004: Content block for key_points output type."""

    rank: int
    original_text: str
    importance_score: float
    source_segment_id: str


@dataclass
class OutputDocument:
    """M-OUT-001: Polymorphic output container."""

    output_type: str  # "summary" or "key_points"
    metadata: OutputMetadata
    content_blocks: list
    validation_status: str  # "pass", "fail", "warn"


@dataclass
class Violation:
    """A single validation rule violation."""

    rule_id: str
    code: str
    detail: str


@dataclass
class ValidationResult:
    """Output of the validation step."""

    status: str  # "pass", "fail", "warn"
    violations: list[Violation] = field(default_factory=list)


# =============================================================================
# Helper Functions
# =============================================================================

_VALID_LANGUAGES = {
    "en", "zh", "ja", "ko", "fr", "de", "es", "pt", "ru",
    "ar", "hi", "bn", "id", "ms", "it", "nl", "sv", "pl",
    "th", "vi", "tr", "uk", "cs", "ro", "da", "fi", "hu",
    "el", "he", "no", "sk", "bg", "hr", "lt", "sl", "et",
    "lv", "mt", "ga", "cy", "ca", "eu", "gl",
}

_SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+")


def _detect_language(content: str) -> str:
    """Detect language of text content using character frequency analysis.

    Falls back to 'en' if detection confidence is below threshold.
    A production implementation would use a language detection library.
    """
    # Simple heuristic: check for CJK characters
    cjk_count = sum(
        1 for c in content if "\u4e00" <= c <= "\u9fff"
    )
    total = len(content)
    if total == 0:
        return "en"
    if cjk_count / total > 0.3:
        return "zh"

    # Check for Japanese-specific characters
    jp_count = sum(
        1 for c in content if ("\u3040" <= c <= "\u309f") or ("\u30a0" <= c <= "\u30ff")
    )
    if jp_count / total > 0.1:
        return "ja"

    # Check for Korean characters
    kr_count = sum(1 for c in content if "\uac00" <= c <= "\ud7af")
    if kr_count / total > 0.1:
        return "ko"

    # Default to English for Latin-script languages
    return "en"


def _split_paragraphs(content: str) -> list[str]:
    """Split content into paragraphs by blank lines."""
    paragraphs = []
    current = []
    for line in content.splitlines():
        if line.strip() == "":
            if current:
                paragraphs.append(" ".join(current))
                current = []
        else:
            current.append(line.strip())
    if current:
        paragraphs.append(" ".join(current))
    return [p for p in paragraphs if p.strip()]


def _split_sentences(content: str) -> list[str]:
    """Split content into sentences by punctuation followed by whitespace."""
    parts = _SENTENCE_PATTERN.split(content.strip())
    return [s.strip() for s in parts if s.strip()]


# =============================================================================
# Step 1: parse_input_document
# Implements EP-001 InputParser Protocol
# =============================================================================

def parse_input_document(
    state: dict[str, Any],
    ctx: dict[str, str],
    step_cfg: dict[str, Any],
) -> dict[str, Any]:
    """Parse input document into structured intermediate representation.

    Validates input against IP-VAL-01 through IP-VAL-04, then extracts
    DocumentContext (M-DOC-001), TextSegments (M-SEG-001), and
    Paragraphs (M-PAR-001). Validates input mapping invariants
    IM-VAL-01 through IM-VAL-04.

    Returns a ParsedDocument as a JSON-serializable dict.
    """
    input_file_path = ctx.get("INPUT_FILE", "")
    if not input_file_path:
        artifacts = state.get("artifacts") or {}
        input_file_path = artifacts.get("INPUT_FILE", "")

    if not input_file_path:
        raise FileNotFoundError("INPUT_FILE not provided in context or artifacts")

    # IP-VAL-01: File exists and is readable
    if not os.path.isfile(input_file_path):
        raise FileNotFoundError(
            f"INPUT_NOT_FOUND: {input_file_path}"
        )

    # IP-VAL-02: File extension is .txt or .md
    ext = os.path.splitext(input_file_path)[1].lower()
    if ext not in (".txt", ".md"):
        raise ValueError(
            f"INVALID_FORMAT: expected .txt or .md, got {ext}"
        )

    # IP-VAL-03: File is non-empty
    file_size = os.path.getsize(input_file_path)
    if file_size == 0:
        raise ValueError("EMPTY_INPUT: input file is empty")

    # IP-VAL-04: File encoding is UTF-8 compatible
    with open(input_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError("EMPTY_INPUT: input file contains only whitespace")

    # Extract DocumentContext (M-DOC-001)
    source_language = _detect_language(content)
    source_format = "md" if ext == ".md" else "txt"
    source_word_count = len(content.split())
    paragraphs = _split_paragraphs(content)
    paragraph_count = len(paragraphs)
    sentences = _split_sentences(content)
    sentence_count = len(sentences)

    doc_ctx = DocumentContext(
        source_language=source_language,
        source_format=source_format,
        source_word_count=source_word_count,
        source_file_path=os.path.abspath(input_file_path),
        paragraph_count=paragraph_count,
        sentence_count=sentence_count,
    )

    # Extract TextSegments (M-SEG-001) -- sentence type
    sentence_segments: list[TextSegment] = []
    sent_position = 0
    for par_idx, para in enumerate(paragraphs):
        sents = _SENTENCE_PATTERN.split(para.strip())
        for sent_idx, sent in enumerate(sents):
            sent = sent.strip()
            if not sent:
                continue
            sent_position += 1
            seg_id = f"seg_p{par_idx + 1:03d}_s{sent_idx + 1:03d}"
            sentence_segments.append(TextSegment(
                segment_id=seg_id,
                content=sent,
                segment_type="sentence",
                position=sent_position,
                region=None,
                word_count=len(sent.split()),
            ))

    # Extract TextSegments (M-SEG-001) -- paragraph type
    paragraph_segments: list[TextSegment] = []
    for par_idx, para in enumerate(paragraphs):
        para = para.strip()
        if not para:
            continue
        paragraph_segments.append(TextSegment(
            segment_id=f"par_{par_idx + 1:03d}",
            content=para,
            segment_type="paragraph",
            position=par_idx + 1,
            region=None,
            word_count=len(para.split()),
        ))

    all_segments = sentence_segments + paragraph_segments

    # Build Paragraph groupings (M-PAR-001)
    result_paragraphs: list[Paragraph] = []
    sent_idx = 0
    for par_idx, para in enumerate(paragraphs):
        para = para.strip()
        if not para:
            continue
        seg_ids = []
        while sent_idx < len(sentence_segments):
            seg = sentence_segments[sent_idx]
            if seg.content.strip() in para:
                seg_ids.append(seg.segment_id)
                sent_idx += 1
            else:
                break
        result_paragraphs.append(Paragraph(
            paragraph_id=f"par_{par_idx + 1:03d}",
            segment_ids=seg_ids,
            position=par_idx + 1,
            word_count=sum(
                s.word_count for s in sentence_segments
                if s.segment_id in seg_ids
            ),
        ))

    # IM-VAL-01: Word count consistency (5% tolerance)
    total_seg_words = sum(
        s.word_count for s in all_segments if s.segment_type == "sentence"
    )
    tolerance = doc_ctx.source_word_count * 0.05
    if abs(total_seg_words - doc_ctx.source_word_count) > tolerance:
        raise ValueError(
            f"WORD_COUNT_MISMATCH: expected ~{doc_ctx.source_word_count}, "
            f"got {total_seg_words}"
        )

    # IM-VAL-02: All paragraph segment_ids reference existing segments
    all_seg_ids = {s.segment_id for s in all_segments}
    for par in result_paragraphs:
        for sid in par.segment_ids:
            if sid not in all_seg_ids:
                raise ValueError(f"ORPHAN_REFERENCE: {sid}")

    # IM-VAL-03: Sequential contiguous positions
    for i, seg in enumerate(all_segments):
        expected_pos = i + 1
        if seg.position != expected_pos:
            raise ValueError(
                f"POSITION_GAP: expected {expected_pos}, got {seg.position}"
            )

    # IM-VAL-04: Valid ISO 639-1 language code
    if doc_ctx.source_language not in _VALID_LANGUAGES:
        raise ValueError(
            f"INVALID_LANGUAGE: {doc_ctx.source_language}"
        )

    # Build output
    parsed_document = {
        "document_context": asdict(doc_ctx),
        "text_segments": [asdict(s) for s in all_segments],
        "paragraphs": [asdict(p) for p in result_paragraphs],
    }

    return parsed_document


# =============================================================================
# Step 5: render_summary (default implementation)
# Implements EP-003 OutputRenderer Protocol
# =============================================================================

def render_summary(
    state: dict[str, Any],
    ctx: dict[str, str],
    step_cfg: dict[str, Any],
) -> dict[str, Any]:
    """Render condensed prose summary from analysis result.

    Produces a three-block summary (intro, main_points, conclusion)
    using the highest-importance non-redundant segments from each region.
    Satisfies OR-001 rendering rules.

    Returns an OutputDocument as a JSON-serializable dict.
    """
    analysis_result = _load_json_artifact(state, ctx, "ANALYSIS_RESULT")
    parsed_doc = _load_json_artifact(state, ctx, "PARSED_DOCUMENT")

    doc_ctx = parsed_doc["document_context"]
    text_segments = parsed_doc["text_segments"]
    analyzed_segments = analysis_result["analyzed_segments"]

    # Build segment lookup
    seg_lookup = {s["segment_id"]: s for s in text_segments}

    # Select top non-redundant segments per region by importance
    source_word_count = doc_ctx["source_word_count"]

    intro_segs = _select_top_segments(
        analyzed_segments, seg_lookup,
        region="intro",
        max_words=int(source_word_count * 0.05),
    )
    main_segs = _select_top_segments(
        analyzed_segments, seg_lookup,
        region="body",
        max_words=int(source_word_count * 0.10),
    )
    conclusion_segs = _select_top_segments(
        analyzed_segments, seg_lookup,
        region="conclusion",
        max_words=int(source_word_count * 0.05),
    )

    # Build content blocks
    content_blocks = []
    for block_type, segs in [
        ("intro", intro_segs),
        ("main_points", main_segs),
        ("conclusion", conclusion_segs),
    ]:
        prose_parts = [
            seg_lookup[s["segment_id"]]["content"]
            for s in segs
            if s["segment_id"] in seg_lookup
        ]
        prose = " ".join(prose_parts)
        source_ids = [s["segment_id"] for s in segs]
        content_blocks.append({
            "block_type": block_type,
            "prose": prose,
            "source_segment_ids": source_ids,
        })

    # Compute output word count
    output_word_count = sum(
        len(block["prose"].split()) for block in content_blocks
    )
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
        "implementation": "summary",
        "generation_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    output_document = {
        "output_type": "summary",
        "metadata": metadata,
        "content_blocks": content_blocks,
        "validation_status": "pass",
    }

    return output_document


# =============================================================================
# Step 6: validate_summary (default implementation)
# Implements EP-004 ValidationStrategy Protocol
# =============================================================================

def validate_summary(
    state: dict[str, Any],
    ctx: dict[str, str],
    step_cfg: dict[str, Any],
) -> dict[str, Any]:
    """Validate summary output against applicable OV rules.

    Checks:
      OV-001: Compression ratio <= 0.20
      OV-002: Source language preserved
      OV-003: No new information (segment ID reference check)
      OV-004: Core message retained
      OV-005: Logical flow preserved (intro -> main -> conclusion)
      OV-009: Single coherent document

    Also writes the final OUTPUT_SUMMARY file.
    Returns a ValidationResult as a JSON-serializable dict.
    """
    output_doc = _load_json_artifact(state, ctx, "OUTPUT_DOCUMENT")
    parsed_doc = _load_json_artifact(state, ctx, "PARSED_DOCUMENT")
    analysis_result = _load_json_artifact(state, ctx, "ANALYSIS_RESULT")

    violations: list[dict[str, str]] = []

    # OV-001: Compression ratio <= 0.20
    if output_doc["metadata"]["compression_ratio"] > 0.20:
        violations.append({
            "rule_id": "OV-001",
            "code": "COMPRESSION_EXCEEDED",
            "detail": (
                f"Ratio {output_doc['metadata']['compression_ratio']} > 0.20"
            ),
        })

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
    all_source_ids: set[str] = set()
    for block in output_doc.get("content_blocks", []):
        all_source_ids.update(block.get("source_segment_ids", []))
    valid_ids = {s["segment_id"] for s in parsed_doc["text_segments"]}
    unknown_ids = all_source_ids - valid_ids
    if unknown_ids:
        violations.append({
            "rule_id": "OV-003",
            "code": "NEW_INFO_DETECTED",
            "detail": f"Output references unknown segments: {unknown_ids}",
        })

    # OV-004: Core message retained
    core_seg_ids = {
        a["segment_id"]
        for a in analysis_result.get("analyzed_segments", [])
        if a.get("is_core_message")
    }
    if not (all_source_ids & core_seg_ids):
        violations.append({
            "rule_id": "OV-004",
            "code": "CORE_MESSAGE_LOST",
            "detail": "No content block references the core message segment",
        })

    # OV-005: Logical flow preserved
    block_types = [b["block_type"] for b in output_doc.get("content_blocks", [])]
    expected_order = ["intro", "main_points", "conclusion"]
    if block_types != expected_order:
        violations.append({
            "rule_id": "OV-005",
            "code": "STRUCTURE_BROKEN",
            "detail": f"Block order {block_types} != {expected_order}",
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
    _write_summary_file(output_doc, state, ctx)

    validation_result = {
        "status": status,
        "violations": violations,
    }

    return validation_result


# =============================================================================
# Step 7: step_completion
# Terminal action
# =============================================================================

def step_completion(
    state: dict[str, Any],
    ctx: dict[str, str],
    step_cfg: dict[str, Any],
) -> dict[str, Any]:
    """Finalize job execution and write meta.json sidecar.

    The meta.json is the sole communication channel between the
    workflow and the runner. Contains execution status, artifact
    references, and result summary.
    """
    validation_result = _load_json_artifact(state, ctx, "VALIDATION_RESULT")
    overall_status = validation_result.get("status", "unknown")

    # Collect output artifact references
    artifacts = state.get("artifacts") or {}
    output_artifacts = {}
    for key in ("OUTPUT_SUMMARY", "OUTPUT_KEY_POINTS"):
        if key in artifacts:
            output_artifacts[key] = artifacts[key]

    completion = {
        "status": overall_status,
        "output_artifacts": output_artifacts,
        "violations": validation_result.get("violations", []),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    return completion


# =============================================================================
# Internal Helpers
# =============================================================================

def _load_json_artifact(
    state: dict[str, Any],
    ctx: dict[str, str],
    artifact_key: str,
) -> dict[str, Any]:
    """Load a JSON artifact from disk using the resolved path.

    Looks up the artifact path from state['artifacts'] or ctx,
    reads the file, and returns the parsed JSON.
    """
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


def _select_top_segments(
    analyzed_segments: list[dict[str, Any]],
    seg_lookup: dict[str, dict[str, Any]],
    region: str,
    max_words: int,
) -> list[dict[str, Any]]:
    """Select highest-importance non-redundant segments for a region.

    Greedily adds segments in descending importance order until the
    word budget is exhausted.
    """
    candidates = [
        a for a in analyzed_segments
        if not a.get("is_redundant", False)
        and seg_lookup.get(a["segment_id"], {}).get("region") == region
    ]
    candidates.sort(
        key=lambda a: a.get("importance_score", 0.0), reverse=True
    )

    selected = []
    used_words = 0
    for cand in candidates:
        seg = seg_lookup.get(cand["segment_id"])
        if seg and used_words + seg.get("word_count", 0) <= max_words:
            selected.append(cand)
            used_words += seg.get("word_count", 0)

    return selected


def _write_summary_file(
    output_doc: dict[str, Any],
    state: dict[str, Any],
    ctx: dict[str, str],
) -> None:
    """Write summary output as plain text prose to OUTPUT_SUMMARY path."""
    artifacts = state.get("artifacts") or {}
    output_path = artifacts.get("OUTPUT_SUMMARY", "")
    if not output_path:
        output_path = ctx.get("OUTPUT_SUMMARY", "")
    if not output_path:
        return

    blocks = {
        b["block_type"]: b
        for b in output_doc.get("content_blocks", [])
    }

    lines: list[str] = []
    if "intro" in blocks:
        lines.append(blocks["intro"]["prose"])
        lines.append("")
    if "main_points" in blocks:
        lines.append(blocks["main_points"]["prose"])
        lines.append("")
    if "conclusion" in blocks:
        lines.append(blocks["conclusion"]["prose"])

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
