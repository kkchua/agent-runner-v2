---
doc_type: "runtime_impl"
identity_locked: true
generator_name: "text_summarizer_ayz"
codename: "text_summarizer_ayz"
version: "1.0.0"
spec_reference: "COMPOSITION_SPEC-01.md"
standard_reference: "BASE_COMPOSITION_STANDARD_v1.0.md"
pattern: "Input Transformation (Pattern 2)"
design_date: "2026-08-10"
---

# Runtime Implementation Design Notes

## Overview

This document contains the intermediate design notes for the default runtime
implementation of the text_summarizer_ayz generator. It captures the architectural
decisions, data flow analysis, component module decomposition, and error handling
strategy that will be formalized in the default.impl.md deliverable.

The runtime implementation satisfies the composition specification defined in
COMPOSITION_SPEC-01.md and follows Pattern 2 (Input Transformation) from the
BASE_COMPOSITION_STANDARD_v1.0.md.

---

## Architecture Decisions

### Decision 1: Pipeline-Based Execution Model

The runtime uses a linear pipeline with 6 sequential stages matching the
composition spec transformation rules. Each stage consumes the output of the
previous stage and produces structured intermediate results.

**Rationale:** The composition spec mandates a fixed stage ordering (Stage 1
through Stage 6). A linear pipeline is the simplest correct execution model.
Future implementations could introduce parallelism for independent stages, but
the default implementation keeps stages sequential for correctness and
debuggability.

**Data flow:**
```
Input File
    |
    v
[Stage 0: Input Loading] -> SourceDocument (Layer 1)
    |
    v
[Stage 1: Importance Scoring] -> ImportanceAnalysis (Layer 2)
    |
    v
[Stage 2: Redundancy Analysis] -> RedundancyCluster[] (Layer 2)
    |
    v
[Stage 3: Key Point Extraction] -> KeyPoint[] (Layer 2)
    |
    v
[Stage 4: Summary Block Composition] -> SummaryBlock[] (Layer 2)
    |
    v
[Stage 5: Output Assembly] -> OutputDocument[] (Layer 3)
    |
    v
[Stage 6: Output Validation] -> Validated OutputDocument[]
    |
    v
Output Files (CONDENSED_SUMMARY, KEY_POINTS_LIST)
```

### Decision 2: Protocol-Based Extension System

The four extension protocols from the composition spec (EXT-001 through EXT-004)
are implemented as abstract base classes (or Protocol classes). The runtime
uses a registry pattern to select concrete implementations at startup.

**Rationale:** The composition spec defines these as variable components. The
registry pattern allows swapping implementations without modifying the pipeline
logic.

**Registry structure:**
```
RuntimeRegistry:
    input_parsers: Map[format_string, InputParser]
    importance_scorer: ImportanceScorer
    redundancy_detector: RedundancyDetector
    output_renderers: Map[output_type, OutputRenderer]
```

### Decision 3: Data Structure Representation

All Layer 1, Layer 2, and Layer 3 components are represented as dataclass
instances. This provides:
- Type safety via Python type hints
- Immutable-after-creation semantics (frozen dataclasses)
- Easy serialization to dict/JSON for debugging
- Clear field validation at construction time

### Decision 4: Error Handling Strategy

Three categories of errors:
1. **Abort errors** -- Input validation failures (V-MAP-IN-*). Pipeline halts.
2. **Recovery errors** -- Minor data issues (empty text unit). Skip and log.
3. **Invariant violations** -- Post-condition failures. Pipeline halts.

Each stage validates its own invariants before returning. If an invariant
fails, the runtime raises an InvariantViolationError with the stage ID and
the specific invariant ID.

---

## Component Module Design

### Module 1: input_loader

**Responsibility:** Implement Stage 0 (Input Loading) and the EXT-001 InputParser
protocol.

**Sub-components:**
- `DefaultInputParser`: Dispatches to format-specific parsers
- `TxtParser`: Handles .txt files (MAP-IN-005 blank-line decomposition)
- `MdParser`: Handles .md files (MAP-IN-005 heading-based decomposition)
- `LanguageDetector`: Implements MAP-IN-003 (language detection)
- `TextSegmenter`: Implements MAP-IN-006 (sentence segmentation)

**Data flow:**
```
file_path -> InputParser.parse() -> SourceDocument
```

**Error handling:**
- V-MAP-IN-001: FileNotFoundError -> abort
- V-MAP-IN-002: UnsupportedExtensionError -> abort
- V-MAP-IN-003: EmptyContentError -> abort
- V-MAP-IN-004: LanguageDetectionError -> abort
- V-MAP-IN-006: EmptyTextUnit -> skip, log warning

### Module 2: importance_scorer

**Responsibility:** Implement Stage 1 (Importance Scoring) and the EXT-002
ImportanceScorer protocol.

**Default implementation:** `PositionalTFIDFScorer`
- Combines positional weighting (introduction/conclusion boost) with
  term-frequency analysis
- Produces normalized scores in [0.0, 1.0]

**Algorithm outline:**
1. Compute TF-IDF-like scores for each TextUnit
2. Apply positional boost: introduction units get 1.2x, conclusion units get 1.1x
3. Normalize all scores to [0.0, 1.0] by dividing by max score
4. Sort by descending score, assign ranks 1, 2, 3, ...
5. Verify invariants INV-S1-001 through INV-S1-004

### Module 3: redundancy_detector

**Responsibility:** Implement Stage 2 (Redundancy Analysis) and the EXT-003
RedundancyDetector protocol.

**Default implementation:** `KeywordOverlapClusterer`
- Uses word-level overlap (Jaccard similarity) to detect redundancy
- Threshold-based grouping (default similarity threshold: 0.6)

**Algorithm outline:**
1. For each TextUnit, compute word set (lowercased, stop-words removed)
2. For each pair of TextUnits, compute Jaccard similarity
3. Group pairs exceeding similarity_threshold using union-find
4. For each cluster, select representative as unit with highest importance_score
5. Compute consolidation_score as average pairwise similarity within cluster
6. Verify invariants INV-S2-001 through INV-S2-004

### Module 4: keypoint_extractor

**Responsibility:** Implement Stage 3 (Key Point Extraction).

**Algorithm outline:**
1. For each RedundancyCluster, get the representative ScoredUnit
2. If representative.importance_score >= keypoint_threshold (default: 0.3):
   - Create KeyPoint with content from source TextUnit
   - Inherit importance_score, section_ref
3. Sort KeyPoints by descending importance_score
4. Assign sequential ranks
5. Verify invariants INV-S3-001 through INV-S3-004

### Module 5: summary_composer

**Responsibility:** Implement Stage 4 (Summary Block Composition).

**Algorithm outline:**
1. Compute max_words = floor(0.20 * source_word_count)
2. For each StructuralSection:
   a. Get all TextUnits belonging to this section
   b. Remove TextUnits that are non-representative cluster members
   c. Sort remaining by descending importance_score
   d. Allocate budget = floor(max_words * section_word_count / source_word_count)
   e. Greedily select top-ranked units until budget exhausted
   f. Compose SummaryBlock.content from selected units (concatenated sentences)
3. Verify total block_word_count <= max_words (INV-S4-002)
4. Verify section ordering (INV-S4-003)
5. Verify no new information (INV-S4-005) -- all content traces to source

### Module 6: output_assembler

**Responsibility:** Implement Stage 5 (Output Assembly).

**Logic:**
1. Based on requested output_types, create OutputDocument instances
2. For condensed_summary: apply MAP-OUT-001
3. For key_points_list: apply MAP-OUT-002
4. Assign ValidationRules per output type
5. Verify INV-S5-001 through INV-S5-004

### Module 7: output_validator

**Responsibility:** Implement Stage 6 (Output Validation).

**Logic:**
1. For each OutputDocument, evaluate each assigned ValidationRule
2. VR-001: Check compression_ratio <= 0.20
3. VR-002/VR-006: Check language match
4. VR-003: Check section structure preservation
5. VR-004/VR-007: Check content traceability to source
6. VR-005: Check importance scores present
7. If any rule fails, raise ValidationFailureError
8. Record validation results for traceability (INV-S6-002)

### Module 8: output_renderer

**Responsibility:** Implement the EXT-004 OutputRenderer protocol. Serialize
OutputDocument instances to disk.

**Default implementations:**
- `MarkdownRenderer`: Outputs .md files with structured formatting
- `PlainTextRenderer`: Outputs .txt files

**Serialization rules (MAP-OUT-003):**
- Preserve all OutputBlock content text
- Preserve ordering from position fields
- Preserve scores from metadata (for scored_item blocks)
- Preserve language provenance

---

## Configuration Design

### Runtime Configuration Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| compression_ratio | float | 0.20 | Maximum summary/source word count ratio |
| keypoint_threshold | float | 0.30 | Minimum importance score for key point extraction |
| similarity_threshold | float | 0.60 | Jaccard similarity threshold for redundancy clustering |
| output_format | string | "md" | Default serialization format (md, txt) |
| output_types | list | ["condensed_summary", "key_points_list"] | Which output types to produce |
| scoring_method | string | "positional_tfidf" | Which ImportanceScorer to use |
| clustering_method | string | "keyword_overlap" | Which RedundancyDetector to use |
| language_detection | string | "auto" | Language detection method |

### Configuration Sources (Priority Order)

1. Command-line arguments (highest)
2. Environment variables (e.g., TS_COMPRESSION_RATIO)
3. Configuration file (optional, per-run)
4. Default values (lowest)

---

## Error Handling Strategy

### Error Types

| Error Class | Trigger | Action |
|---|---|---|
| InputValidationError | V-MAP-IN-001 through V-MAP-IN-005, V-MAP-IN-007 | Abort pipeline, report error |
| InvariantViolationError | Any INV-S* or GI-* violation | Abort pipeline, report stage and invariant ID |
| ValidationFailureError | Any VR-* rule failure in Stage 6 | Abort pipeline, report violated rules |
| ConfigurationError | Invalid configuration values | Abort before pipeline starts |
| UnsupportedFormatError | Unknown input format or output type | Abort with clear message |

### Error Recovery

- Stage-level recovery: If a TextUnit has empty content (V-MAP-IN-006), skip
  it and log a warning. Do not abort.
- No other stage supports recovery. All other failures are fatal.

### Error Reporting

All errors include:
- Error class name
- Stage ID where error occurred
- Specific invariant/rule ID violated
- Context data (e.g., which TextUnit, which OutputDocument)
- Human-readable description

---

## Extension Interface Design

### Extension Registration

Extensions register via a RuntimeRegistry:

```
registry = RuntimeRegistry()
registry.register_parser("txt", TxtParser())
registry.register_parser("md", MdParser())
registry.set_scorer(PositionalTFIDFScorer())
registry.set_detector(KeywordOverlapClusterer())
registry.register_renderer("condensed_summary", MarkdownRenderer())
registry.register_renderer("key_points_list", MarkdownRenderer())
```

### Adding a New Output Type

1. Implement an OutputRenderer that produces OutputDocument with the new type
2. Define ValidationRules for the new type
3. Register the renderer in the RuntimeRegistry
4. The pipeline handles the rest (Stage 5 creates OutputDocument, Stage 6
   validates against assigned rules)

### Adding a New Input Format

1. Implement an InputParser that produces SourceDocument
2. Register the parser for the file extension
3. The pipeline handles the rest (Layer 1 components flow through unchanged)

### Adding a New Scoring Algorithm

1. Implement the ImportanceScorer protocol
2. Register as the scorer (or make it selectable via configuration)
3. Must satisfy INV-S1-001 through INV-S1-004

### Adding a New Clustering Algorithm

1. Implement the RedundancyDetector protocol
2. Register as the detector (or make it selectable via configuration)
3. Must satisfy INV-S2-001 through INV-S2-004

---

## Traceability Matrix

| Design Element | Source | Traced To |
|---|---|---|
| 6-stage pipeline | Composition spec | Transformation Rules section, Stages 1-6 |
| InputParser protocol | Composition spec | EXT-001 |
| ImportanceScorer protocol | Composition spec | EXT-002 |
| RedundancyDetector protocol | Composition spec | EXT-003 |
| OutputRenderer protocol | Composition spec | EXT-004 |
| Dataclass representation | BASE_COMPOSITION_STANDARD | Section 3 (Universal Component Schema) |
| Registry pattern | CODER_IMPLEMENTATION_SOP | Pattern Compliance Rules |
| Compression ratio 20% | Requirement doc | C-PERF-001, GI-003, VR-001 |
| Same language constraint | Requirement doc | C-FMT-004, GI-001 |
| No new information | Requirement doc | C-CMP-001, GI-002 |
| Structure preservation | Requirement doc | C-CMP-003, GI-005 |
| Key points with scores | Requirement doc | OUT-002, Q-OUT-006 |
| Ordered key points | Requirement doc | Q-OUT-007 |

---

## Explicit Assumptions

| ID | Assumption | Resolution |
|---|---|---|
| A-IMPL-001 | Default scoring uses positional + TF-IDF hybrid | Stated in design; swappable via EXT-002 |
| A-IMPL-002 | Default clustering uses keyword overlap (Jaccard) | Stated in design; swappable via EXT-003 |
| A-IMPL-003 | Stop words are removed for clustering but not scoring | Standard NLP practice for this domain |
| A-IMPL-004 | Sentence boundary detection uses punctuation heuristics | . ? ! followed by whitespace |
| A-IMPL-005 | Default output format is Markdown | Matches both .txt and .md input support |
| A-IMPL-006 | Language detection uses a heuristic approach | No external ML library required for default |
| A-IMPL-007 | Maximum input size not enforced at runtime level | Runtime may add a configurable limit later |

---

**End of Runtime Implementation Design Notes**
