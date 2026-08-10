---
doc_type: "runtime_impl"
identity_locked: true
generator_name: "text_summarizer"
version: "1.0.0"
source_composition_spec: "COMPOSITION_SPEC-001"
source_requirement_analysis: "REQUIREMENT_ANALYSIS-001"
designed_at: "2026-08-10"
---

# Runtime Implementation Design

## 1. Implementation Architecture

### 1.1 High-Level Structure

The runtime implementation is a single-entry-point pipeline that transforms
an input text file (INPUT_TEXT_FILE) into a summary output file (SUMMARY_FILE)
by executing a 10-stage transformation pipeline.

```
Entry Point: run_summarizer(config) -> SummaryDocument
    |
    +-- [Stage 1]  Input Parser       -> Layer 1 Content Components
    +-- [Stage 2]  Segment Validator  -> Validated hierarchy
    +-- [Stage 3]  Importance Scorer  -> KeyPoint[] (Layer 2)
    +-- [Stage 4]  Redundancy Detector -> RedundancyCluster[] + deduplicated set
    +-- [Stage 5]  Meaning Preserver  -> Validated KeyPoint set
    +-- [Stage 6]  Compression Selector -> Selected KeyPoints (<= 20% budget)
    +-- [Stage 7]  Structure Maintainer -> SummaryBlock[] (Layer 2)
    +-- [Stage 8]  Language Validator  -> ValidationRecord[] (CON-002)
    +-- [Stage 9]  Length Validator    -> ValidationRecord[] (CON-001)
    +-- [Stage 10] Output Renderer    -> SummaryDocument (Layer 3) + SUMMARY_FILE
```

### 1.2 Component Modules

| Module | Responsibility | Interface Pattern |
|--------|---------------|-------------------|
| InputParser | Read and parse INPUT_TEXT_FILE into Layer 1 components | Protocol (InputParserHook) |
| SegmentValidator | Verify Section/Paragraph/Sentence hierarchy | Internal function |
| ImportanceScorer | Assign importance_score to sentences | Protocol (ImportanceScorerHook) |
| RedundancyDetector | Group similar KeyPoints into clusters | Protocol (RedundancyDetectorHook) |
| MeaningPreserver | Verify coverage and promote fallbacks | Internal function |
| CompressionSelector | Select KeyPoints within word budget | Protocol (CompressionSelectorHook) |
| StructureMaintainer | Assemble SummaryBlocks from KeyPoints | Protocol (StructureMaintainerHook) |
| ValidationEngine | Check CON-001, CON-002, CON-003 | Internal function |
| OutputRenderer | Render SummaryDocument to SUMMARY_FILE | Protocol (OutputRendererHook) |

### 1.3 Data Flow

```
INPUT_TEXT_FILE (str path)
  |
  v
[InputParser]
  -> DocumentMeta, Section[], Paragraph[], Sentence[]   (Layer 1)
  |
  v
[SegmentValidator]
  -> Validated hierarchy (invariants INV-T-001, INV-T-002)
  |
  v
[ImportanceScorer]
  -> KeyPoint[] with importance_score, structural_role    (Layer 2)
  |
  v
[RedundancyDetector]
  -> RedundancyCluster[], deduplicated KeyPoint[]         (Layer 2)
  |
  v
[MeaningPreserver]
  -> Validated KeyPoint set (invariant INV-T-006)
  |
  v
[CompressionSelector]
  -> Selected KeyPoint[] (invariant INV-T-007)
  |
  v
[StructureMaintainer]
  -> SummaryBlock[] (invariant INV-T-008)                 (Layer 2)
  |
  v
[ValidationEngine]
  -> ValidationRecord[] for CON-001, CON-002              (Layer 3)
  |
  v
[OutputRenderer]
  -> SummaryDocument + SUMMARY_FILE written to disk       (Layer 3)
```

### 1.4 Orchestration Logic

The pipeline is orchestrated by a single `PipelineRunner` class that:

1. Accepts a `RuntimeConfig` dataclass (see Section 7)
2. Resolves each stage's implementation from a registry
3. Executes stages in strict sequential order (no parallelism)
4. Validates invariants after each stage before proceeding
5. Raises explicit exceptions on invariant violation (never returns None)
6. Produces a `PipelineResult` containing all generated components

This follows the repository's established patterns: dataclass configuration
objects, Protocol-based interfaces, registry dispatch, and exception-based
error handling.

---

## 2. Input Loading

### 2.1 File Reading

The InputParser module reads INPUT_TEXT_FILE as a UTF-8 encoded text file.

| Step | Operation | Reference |
|------|-----------|-----------|
| INM-001 | Detect file extension (.txt or .md) | COMPOSITION_SPEC Section 3.2.1 |
| INM-002 | Detect and strip YAML frontmatter (if .md) | COMPOSITION_SPEC Section 3.2.2 |
| INM-003 | Detect source language (ISO 639-1) | COMPOSITION_SPEC Section 3.2.3 |

The InputParser reads the file content as raw bytes and decodes to UTF-8.
If the file cannot be read, a `FileReadError` exception is raised.

### 2.2 Parsing Logic

| Step | Operation | Output | Reference |
|------|-----------|--------|-----------|
| INM-004 | Segment into Sections | Section[] | COMPOSITION_SPEC Section 3.2.4 |
| INM-005 | Segment Sections into Paragraphs | Paragraph[] | COMPOSITION_SPEC Section 3.2.5 |
| INM-006 | Segment Paragraphs into Sentences | Sentence[] | COMPOSITION_SPEC Section 3.2.6 |
| INM-007 | Compute word counts (bottom-up) | All word_count fields | COMPOSITION_SPEC Section 3.2.7 |

For Markdown input, sections are split on heading markers (# through ######).
For plain text input, sections are split on double-newline boundaries.
Paragraphs are split on blank lines within each section.
Sentences are split on sentence-ending punctuation (. ! ?) followed by
whitespace or end-of-text.

### 2.3 Validation of Input Format

| Rule | Validation | Action on Failure | Reference |
|------|-----------|-------------------|-----------|
| INV-001 | File exists and is readable | Raise FileReadError | COMPOSITION_SPEC Section 3.3 |
| INV-002 | Extension is .txt or .md | Raise UnsupportedFormatError | COMPOSITION_SPEC Section 3.3 |
| INV-003 | Content is non-empty after frontmatter removal | Raise EmptyInputError | COMPOSITION_SPEC Section 3.3 |
| INV-004 | Content appears to be natural language | Raise InvalidContentError | COMPOSITION_SPEC Section 3.3 |
| INV-005 | At least one Section detected | Raise ParsingError | COMPOSITION_SPEC Section 3.3 |
| INV-006 | At least one Sentence detected | Raise ParsingError | COMPOSITION_SPEC Section 3.3 |

### 2.4 Conversion to Meta Content Structure

The parsed content is converted into the Layer 1 meta schema components
defined in COMPOSITION_SPEC Section 2.1:

- DocumentMeta (component_id: "doc-meta-001")
- Section[] (component_id: "sec-{index}")
- Paragraph[] (component_id: "para-{section_index}-{para_index}")
- Sentence[] (component_id: "s-{section}-{para}-{sent}")

Each component carries parent references (parent_section_id,
parent_paragraph_id) and ordered child references (paragraph_ids,
sentence_ids) forming the hierarchical graph described in
COMPOSITION_SPEC Section 2.4.

---

## 3. Transformation Engine

### 3.1 Step-by-Step Transformation Process

The transformation engine executes 10 stages as defined in
COMPOSITION_SPEC Section 5.2. Each stage has:

- **Pre-condition:** Invariants that must hold before entry
- **Logic:** The processing defined for the stage
- **Post-condition:** Invariants that must hold after completion
- **Output:** The components produced or modified

### 3.2 Stage Execution Rules

| Stage | ID | Pre-condition | Post-invariant | Trace |
|-------|----|---------------|----------------|-------|
| 1 | TR-001 | INPUT_TEXT_FILE valid | Word count invariant | INV-T-001, INV-T-002 |
| 2 | TR-002 | Layer 1 components exist | Hierarchy validated | INV-T-001, INV-T-002 |
| 3 | TR-003 | Sentences exist | KeyPoints with core message | INV-T-003, INV-T-004 |
| 4 | TR-004 | KeyPoints exist | Max one cluster per KeyPoint | INV-T-005 |
| 5 | TR-005 | Deduplicated KeyPoints | All sections covered | INV-T-006 |
| 6 | TR-006 | Validated KeyPoints | Word budget met | INV-T-007 |
| 7 | TR-007 | Selected KeyPoints | Block order preserved | INV-T-008 |
| 8 | TR-008 | SummaryBlocks exist | Language matches | INV-T-009 |
| 9 | TR-009 | SummaryBlocks complete | Ratio <= 0.20 | INV-T-010 |
| 10 | TR-010 | All validations pass | SUMMARY_FILE written | INV-T-011 |

### 3.3 How Composition Spec Rules Are Applied

Each stage applies the rules defined in COMPOSITION_SPEC Section 5.2:

- **Stage 3** applies the importance scoring algorithm (pluggable via
  ImportanceScorer interface). The default implementation uses positional
  weighting, heading detection, and semantic indicators.
- **Stage 4** applies redundancy detection (pluggable via
  RedundancyDetector interface). The default uses pairwise similarity
  above a configurable threshold.
- **Stage 5** applies meaning preservation by checking section coverage
  and promoting fallback KeyPoints from uncovered sections.
- **Stage 6** applies compression selection (pluggable via
  CompressionSelector interface). The default uses greedy selection
  by importance_score, ensuring at least one KeyPoint per structural_role.
- **Stages 8-9** enforce hard constraints CON-001 and CON-002.

### 3.4 Error Handling and Recovery

| Error Type | Condition | Recovery Action |
|-----------|-----------|-----------------|
| FileReadError | INPUT_TEXT_FILE unreadable | Halt pipeline, report error |
| UnsupportedFormatError | Extension not .txt or .md | Halt pipeline, report error |
| EmptyInputError | No content after parsing | Halt pipeline, report error |
| InvariantViolationError | Post-condition check fails | Halt pipeline, report failing invariant |
| CompressionExceededError | Stage 9 fails (ratio > 0.20) | Return to Stage 6 with tighter budget |

Recovery from compression failures (Stage 9) follows COMPOSITION_SPEC
Section 5.2.9: if compression_ratio > 0.20, return to Stage 6 and
reduce the KeyPoint selection. This loop repeats at most 3 times before
raising a CompressionExceededError.

Language validation failure (Stage 8) is unrecoverable: the pipeline
halts and reports the language mismatch.

---

## 4. Output Generation

### 4.1 Rendering and Assembly Logic

The OutputRenderer assembles the final summary from SummaryBlocks
following COMPOSITION_SPEC Section 4.2:

1. **Determine output format** (OUTM-001): Match DocumentMeta.source_format
   to select the appropriate renderer (TextRenderer or MarkdownRenderer).
2. **Assemble sections** (OUTM-002): Concatenate SummaryBlocks in order:
   intro blocks -> main_point blocks -> conclusion blocks.
3. **Add metadata header** (OUTM-003):
   - For "md": "Summary ({ratio*100}% of original)\nLanguage: {lang}"
   - For "txt": "Summary (approximately {ratio*100}% of original)"
4. **Write to file** (OUTM-004): Write assembled text to SUMMARY_FILE
   with UTF-8 encoding.

### 4.2 File Writing and Formatting

The output file is written using standard UTF-8 encoding. No additional
encoding transformations are applied. The file is written atomically
(write to temporary file, then rename) to prevent partial outputs.

### 4.3 Validation of Output Format

| Rule | Validation | Error Condition | Reference |
|------|-----------|-----------------|-----------|
| OV-001 | SUMMARY_FILE exists and is readable | Write failure | COMPOSITION_SPEC Section 4.3 |
| OV-002 | summary_word_count <= 0.20 * original_word_count | Exceeds 20% limit | COMPOSITION_SPEC Section 4.3 |
| OV-003 | target_language matches source_language | Language mismatch | COMPOSITION_SPEC Section 4.3 |
| OV-004 | Summary contains no information not in source | Hallucination | COMPOSITION_SPEC Section 4.3 |
| OV-005 | Summary contains intro, main_point, conclusion | Missing structure | COMPOSITION_SPEC Section 4.3 |
| OV-006 | Summary is coherent and readable | Integrity failure | COMPOSITION_SPEC Section 4.3 |

OV-004 is enforced structurally: since the summary is assembled only
from KeyPoint extracted_text values (which are derived from source
sentences), no new information can be introduced. This satisfies
CON-003 at the architectural level.

---

## 5. Configuration

### 5.1 Runtime Parameters

The pipeline accepts a `RuntimeConfig` dataclass with the following
configurable parameters:

| Parameter | Type | Default | Description | Reference |
|-----------|------|---------|-------------|-----------|
| input_path | Path | (required) | Path to INPUT_TEXT_FILE | TR-001 |
| output_path | Path | (required) | Path for SUMMARY_FILE | TR-010 |
| target_compression_ratio | float | 0.20 | Maximum compression ratio | VAR-001 |
| importance_threshold | float | 0.5 | Minimum score for KeyPoint selection | Stage 3 |
| redundancy_similarity_threshold | float | 0.7 | Similarity threshold for clustering | Stage 4 |
| max_recovery_attempts | int | 3 | Max loops from Stage 9 back to Stage 6 | Recovery |
| output_format_override | str or None | None | Force output format ("txt" or "md") | VAR-004 |
| scorer_impl | str | "default" | Importance scorer implementation name | EXT |
| detector_impl | str | "default" | Redundancy detector implementation name | EXT |
| selector_impl | str | "default" | Compression selector implementation name | EXT |
| renderer_impl | str | "default" | Output renderer implementation name | EXT |

### 5.2 Default Values and Overrides

All parameters have sensible defaults derived from the composition spec:

- target_compression_ratio = 0.20 (from CON-001)
- importance_threshold = 0.5 (midpoint of 0.0-1.0 range)
- redundancy_similarity_threshold = 0.7 (high similarity required)

Configuration can be overridden by:
1. Direct parameter passing to `run_summarizer(config)`
2. Configuration file (TOML format) loaded into RuntimeConfig
3. Environment variables with prefix `TEXT_SUMMARIZER_`

### 5.3 Environment-Specific Settings

No environment-specific settings are required. The runtime operates
purely on file I/O with no external service dependencies. All
configuration is self-contained in the RuntimeConfig dataclass.

---

## 6. Extension Interface

### 6.1 Interfaces for New Implementations

Each pluggable component follows a Protocol-based interface defined
using Python's `typing.Protocol` with `@runtime_checkable`. This
matches the established pattern in the codebase (see hooks_protocols.py).

#### 6.1.1 InputParser Interface

```
@runtime_checkable
class InputParser(Protocol):
    def parse(self, input_path: Path) -> ParseResult:
        """Parse input file into Layer 1 components.

        Returns:
            ParseResult containing DocumentMeta, Section[], Paragraph[], Sentence[]
        Raises:
            FileReadError: If file cannot be read
            UnsupportedFormatError: If format not .txt or .md
            EmptyInputError: If content is empty
            ParsingError: If segmentation fails
        """
        ...
```

#### 6.1.2 ImportanceScorer Interface

As defined in COMPOSITION_SPEC Section 6.2.2:

```
@runtime_checkable
class ImportanceScorer(Protocol):
    def score(self, sentences: list[Sentence],
              document_meta: DocumentMeta) -> list[float]:
        """Score each sentence for importance.

        Returns list of floats (0.0 to 1.0) in same order as input.
        Must be deterministic for the same input.
        """
        ...
```

#### 6.1.3 RedundancyDetector Interface

As defined in COMPOSITION_SPEC Section 6.2.3:

```
@runtime_checkable
class RedundancyDetector(Protocol):
    def detect(self, key_points: list[KeyPoint],
               threshold: float) -> list[RedundancyCluster]:
        """Detect redundant KeyPoints and group into clusters.

        Each KeyPoint appears in at most one cluster.
        Each cluster has exactly one representative.
        """
        ...
```

#### 6.1.4 CompressionSelector Interface

As defined in COMPOSITION_SPEC Section 6.2.4:

```
@runtime_checkable
class CompressionSelector(Protocol):
    def select(self, key_points: list[KeyPoint],
               target_ratio: float,
               original_word_count: int) -> list[KeyPoint]:
        """Select KeyPoints within word budget.

        Result satisfies INV-T-007 (words <= target_ratio * original).
        Result includes at least one KeyPoint per structural_role.
        Preserves relative ordering.
        """
        ...
```

#### 6.1.5 StructureMaintainer Interface

```
@runtime_checkable
class StructureMaintainer(Protocol):
    def assemble(self, selected_key_points: list[KeyPoint]) -> list[SummaryBlock]:
        """Assemble SummaryBlocks from selected KeyPoints.

        Blocks preserve intro -> main_point -> conclusion order.
        Each block has a structural_role and sequential position.
        """
        ...
```

#### 6.1.6 OutputRenderer Interface

As defined in COMPOSITION_SPEC Section 6.2.1:

```
@runtime_checkable
class OutputRenderer(Protocol):
    supported_formats: list[str]

    def render(self, summary_document: SummaryDocument,
               blocks: list[SummaryBlock]) -> str:
        """Render summary to string for writing to disk.

        Must not modify input components.
        Must respect target_language and output_format.
        Must pass all output validation rules (OV-001 to OV-006).
        """
        ...
```

### 6.2 Extension Points and Hooks

| Extension Point | Protocol | Registry Key | Default Implementation |
|----------------|----------|-------------|----------------------|
| Importance scoring | ImportanceScorer | "importance_scorer" | DefaultImportanceScorer |
| Redundancy detection | RedundancyDetector | "redundancy_detector" | DefaultRedundancyDetector |
| Compression selection | CompressionSelector | "compression_selector" | GreedyCompressionSelector |
| Structure assembly | StructureMaintainer | "structure_maintainer" | RoleGroupingMaintainer |
| Output rendering | OutputRenderer | "output_renderer" | TextRenderer, MarkdownRenderer |

### 6.3 How to Register New Implementations

New implementations are registered using a dispatch registry following
the CODER_REGISTRY pattern:

```
EXTENSION_REGISTRY: dict[str, dict[str, Any]] = {
    "importance_scorer": {
        "default": DefaultImportanceScorer(),
        "tfidf": TfIdfImportanceScorer(),
    },
    "redundancy_detector": {
        "default": DefaultRedundancyDetector(),
        "embedding": EmbeddingRedundancyDetector(),
    },
    "compression_selector": {
        "default": GreedyCompressionSelector(),
        "balanced": BalancedCompressionSelector(),
    },
    "structure_maintainer": {
        "default": RoleGroupingMaintainer(),
    },
    "output_renderer": {
        "default": TextRenderer(),
        "markdown": MarkdownRenderer(),
        "json": JSONRenderer(),
        "yaml": YAMLRenderer(),
    },
}
```

To add a new implementation:
1. Create a class conforming to the appropriate Protocol
2. Register it in EXTENSION_REGISTRY under the correct key
3. Reference it by name in RuntimeConfig (e.g., scorer_impl = "tfidf")

### 6.4 Extension Examples (from COMPOSITION_SPEC Section 6.3)

| Extension | New Components | Changed Stages | New Renderer |
|-----------|---------------|----------------|-------------|
| Bullet-point summary (EXT-001) | BulletPoint, BulletListDocument | Stage 7 | BulletListRenderer |
| Executive summary (EXT-002) | None | Stage 6 (target_ratio) | (reuse existing) |
| Key phrases extraction (EXT-003) | KeyPhrase, KeyPhraseList | Stage 3 variant | KeyPhraseListRenderer |
| Section-by-section summary (EXT-004) | SectionSummary, SectionedSummaryDocument | Stage 7 | SectionedRenderer |

---

## 7. Self-Validation

### 7.1 Composition Spec Compliance

| Check | Status | Evidence |
|-------|--------|----------|
| Implements all 10 stages (TR-001 to TR-010) | PASS | Section 3.2 maps each stage to a pipeline step |
| Produces all Layer 1 components | PASS | Section 2.1 defines DocumentMeta, Section, Paragraph, Sentence |
| Produces all Layer 2 components | PASS | Section 2.2 defines KeyPoint, RedundancyCluster, SummaryBlock |
| Produces all Layer 3 components | PASS | Section 2.3 defines SummaryDocument, ValidationRecord |
| Enforces all input validation rules (INV-001 to INV-006) | PASS | Section 2.3 lists all rules with error types |
| Enforces all output validation rules (OV-001 to OV-006) | PASS | Section 4.3 lists all rules with checks |
| Enforces all component validation rules (VR-001 to VR-012) | PASS | Each component creation enforces relevant rules |
| Maintains all invariants (INV-T-001 to INV-T-011) | PASS | Section 3.2 maps each invariant to a stage |
| Enforces CON-001 (20% compression) | PASS | Stage 6 + Stage 9 with recovery loop |
| Enforces CON-002 (same language) | PASS | Stage 8 with halt on failure |
| Enforces CON-003 (no new information) | PASS | Structural: summary from source sentences only |
| Supports all extension points | PASS | Section 6 defines 6 Protocol interfaces |

### 7.2 Three-Layer Architecture Compliance

| Layer | Requirement | Implementation | Status |
|-------|-------------|----------------|--------|
| Layer 1 | Content Components | InputParser produces DocumentMeta + Section + Paragraph + Sentence | PASS |
| Layer 2 | Composition Definitions | Stages 3-7 produce KeyPoint + RedundancyCluster + SummaryBlock | PASS |
| Layer 3 | Resolved Outputs | Stage 10 produces SummaryDocument + ValidationRecord + SUMMARY_FILE | PASS |

### 7.3 Repository Pattern Compliance

| Pattern | Requirement | Implementation | Status |
|---------|-------------|----------------|--------|
| Protocol interfaces | Hooks use Protocol, not ABC | All 6 interfaces use @runtime_checkable Protocol | PASS |
| Registry dispatch | Use registry, not if/elif | EXTENSION_REGISTRY dict with string keys | PASS |
| Dataclass config | Config objects use dataclass | RuntimeConfig is a dataclass | PASS |
| Exception errors | Raise exceptions, not return None | All errors raise named exception types | PASS |
| No scope invention | Only declared content | All content traces to COMPOSITION_SPEC | PASS |

### 7.4 Input Variation Handling

| Variation | Handling | Reference |
|-----------|----------|-----------|
| .txt input | TextParser handles plain text segmentation | Section 2.2, INM-004 |
| .md input with frontmatter | Frontmatter detection and stripping | Section 2.2, INM-002 |
| .md input without frontmatter | Normal parsing, has_frontmatter = false | Section 2.2, INM-002 |
| Very short input (< 100 words) | Pipeline produces shorter summary, still meets ratio | ASM-001 |
| Very long input (> 10000 words) | Same pipeline, word budget scales with input | ASM-002 |
| Multi-section document | Each section contributes KeyPoints | Stage 5 coverage check |
| Single-paragraph document | Single section, multiple paragraphs/sentences | Section 2.2, INM-004 |

### 7.5 ASCII Compliance

| Check | Status |
|-------|--------|
| No em-dashes used | PASS |
| No curly quotes used | PASS |
| No Unicode characters used | PASS |
| YAML frontmatter uses plain ASCII | PASS |
| All identifiers use ASCII characters | PASS |

### 7.6 Traceability Summary

| Design Section | Source Artifact | Trace |
|---------------|----------------|-------|
| 10-stage pipeline | COMPOSITION_SPEC Section 5.2 | TRACE-ID-004 |
| Input parsing (INM-001 to INM-007) | COMPOSITION_SPEC Section 3.2 | TRACE-ID-002 |
| Output rendering (OUTM-001 to OUTM-004) | COMPOSITION_SPEC Section 4.2 | TRACE-ID-003 |
| Extension interfaces (6 Protocols) | COMPOSITION_SPEC Section 6.2 | TRACE-ID-006 |
| Constraints (CON-001, CON-002, CON-003) | REQUIREMENT_ANALYSIS Constraints | TRACE-ID-005 |
| Generator identity | COMPOSITION_SPEC frontmatter | TRACE-ID-001 |

---

End of Runtime Implementation Design
