---
doc_type: "runtime_impl"
identity_locked: true
generator_name: "text_summarizer"
version: "1.0.0"
source_composition_spec: "COMPOSITION_SPEC-01"
source_requirement_analysis: "REQUIREMENT_ANALYSIS-01"
designed_at: "2026-08-10"
---

# Runtime Implementation Design

## Implementation Architecture

### High-Level Structure

The runtime implementation is a sequential pipeline that transforms
an input text file (INPUT_TEXT_FILE) into a summary output file
(SUMMARY_FILE) by executing a four-stage transformation process
corresponding to the three-layer architecture defined in
COMPOSITION_SPEC-01.

```
Entry Point: run_summarizer(config: RuntimeConfig) -> PipelineResult
    |
    +-- [Stage T1] Key Point Extraction  -> L2-KP[] (from L1-DOC)
    +-- [Stage T2] Redundancy Removal    -> L2-RC[], pruned L2-KP[]
    +-- [Stage T3] Structure Assembly    -> L2-CB[], L2-SM
    +-- [Stage T4] Output Rendering      -> L3-OD, SUMMARY_FILE
```

The pipeline is orchestrated by a PipelineRunner class that:

1. Accepts a RuntimeConfig dataclass (see Configuration section)
2. Loads and validates input via InputParser (IP-001 protocol)
3. Executes stages T1 through T4 in strict sequential order
4. Validates invariants after each stage before proceeding
5. Raises explicit exceptions on invariant violation
6. Produces a PipelineResult containing all generated components

### Component Modules

| Module | Responsibility | Protocol |
|--------|---------------|----------|
| InputParser | Read and parse INPUT_TEXT_FILE into L1-DOC | IP-001 |
| ImportanceScorer | Assign importance_score to each sentence | TA-001 |
| SemanticSimilarity | Compute similarity between keypoint texts | TA-002 |
| WordCounter | Count words in text segments | TA-003 |
| OutputRenderer | Render L2-SM into L3-OD and write SUMMARY_FILE | OR-001 |
| PipelineRunner | Orchestrate stages, validate invariants | Internal |

### Data Flow

```
INPUT_TEXT_FILE (Path)
  |
  v
[InputParser] (IP-001)
  -> L1-DOC containing L1-SEC[], L1-PAR[], L1-SEN[]
  |
  v  (Input Validation: IV-001 through IV-006)
  |
  v
[Stage T1: Key Point Extraction]
  Uses: ImportanceScorer (TA-001), WordCounter (TA-003)
  -> L2-KP[] with importance_score, category, source_sentence_ids
  |
  v  (Invariant check: T1-INV-001, T1-INV-002)
  |
  v
[Stage T2: Redundancy Removal]
  Uses: SemanticSimilarity (TA-002)
  -> L2-RC[], pruned L2-KP[]
  |
  v  (Invariant check: T2-INV-001, T2-INV-002, T2-INV-003)
  |
  v
[Stage T3: Structure Assembly]
  -> L2-CB[], L2-SM
  |
  v  (Invariant check: T3-INV-001, T3-INV-002, T3-INV-003)
  |
  v
[Stage T4: Output Rendering]
  Uses: OutputRenderer (OR-001), WordCounter (TA-003)
  -> L3-OD, L3-OB[], L3-MD
  |
  v  (Invariant check: T4-INV-001 through T4-INV-004)
  v  (Output Validation: OV-001 through OV-007)
  |
  v
SUMMARY_FILE written to disk
```

---

## Input Loading

### File Reading and Parsing Logic

The InputParser (IP-001) loads INPUT_TEXT_FILE as UTF-8 text and
decomposes it into the Layer 1 meta schema.

| Step | Operation | Reference |
|------|-----------|-----------|
| INP-001 | Verify file exists and is readable | IV-001 |
| INP-002 | Validate file extension is .txt or .md | IV-002, PR-002 |
| INP-003 | Read file content as UTF-8 bytes | PR-001 |
| INP-004 | Detect source_format from file extension | Input Mapping table |
| INP-005 | If .md format, detect heading markers (# through ######) | PR-003 |
| INP-006 | Segment text into L1-SEC components | PR-003 |
| INP-007 | Within each section, split on blank lines into L1-PAR | PR-004 |
| INP-008 | Within each paragraph, split into L1-SEN | PR-005 |
| INP-009 | Compute word_count for each L1-SEN, L1-PAR, L1-SEC | PR-006 |
| INP-010 | Compute total_word_count for L1-DOC | PR-006 |
| INP-011 | Detect language and set detected_language | PR-007 |
| INP-012 | Assign unique IDs to all components | Schema requirement |

### Parsing Rules Applied

- PR-001: UTF-8 decoding. If decoding fails, raise InvalidEncodingError
  (IV-004 violation).
- PR-002: Extension check. Only .txt and .md accepted. Otherwise raise
  UnsupportedFormatError (IV-002 violation).
- PR-003: Heading detection. If .md file contains heading markers, each
  heading starts a new L1-SEC with section_type "heading" and
  heading_level from the marker depth. If no headings, create a single
  L1-SEC with section_type "implicit".
- PR-004: Paragraph splitting. Within each section, text is split on
  blank lines (two or more consecutive newlines).
- PR-005: Sentence boundary detection. Uses the tokenization method
  defined by the InputParser implementation (IP-001 protocol).
- PR-006: Word counting. Uses the WordCounter (TA-003) protocol for
  consistent counting across all components.
- PR-007: Language detection. Uses the detect_language method from
  IP-001 protocol. Returns ISO 639-1 code.

### Validation of Input Format

| Rule ID | Check | Failure Action | Traceability |
|---------|-------|---------------|--------------|
| IV-001 | File exists and readable | Raise FileReadError | V-IN-001 |
| IV-002 | Extension .txt or .md | Raise UnsupportedFormatError | V-IN-002, C-004 |
| IV-003 | total_word_count > 0 | Raise EmptyInputError | V-IN-003 |
| IV-004 | UTF-8 decodable | Raise InvalidEncodingError | V-IN-004 |
| IV-005 | At least one L1-SEN parsed | Raise EmptyInputError | Derived from IV-003 |
| IV-006 | Sentence ordering consistent | Raise ParsingError | Structural integrity |

Validation failures abort the pipeline with a specific error identifying
the failing rule.

### Conversion to Meta Content Structure

The parsed content is assembled into the L1-DOC component hierarchy:

- L1-DOC: document_id assigned, source_artifact_key = "INPUT_TEXT_FILE",
  source_format from extension, detected_language from IP-001,
  total_word_count from sum of sentences.
- L1-SEC[]: Ordered by position (1-based). Each has section_id,
  section_type, optional heading_text/heading_level, paragraphs array.
- L1-PAR[]: Within each section, ordered by position. Each has
  paragraph_id, sentences array, word_count.
- L1-SEN[]: Within each paragraph, ordered by position. Each has
  sentence_id, text, word_count.

---

## Transformation Engine

### Step-by-Step Transformation Process

The transformation engine executes four stages as defined in
COMPOSITION_SPEC-01 Transformation Rules. Each stage produces
components in the Layer 2 meta schema.

#### Stage T1: Key Point Extraction (TR-001)

Input: L1-DOC (all sentences)
Output: Array of L2-KP

Process:
1. For each L1-SEN in the document, compute importance_score using the
   ImportanceScorer protocol (TA-001).
2. Determine category for each sentence based on its section_position:
   - First section sentences -> "intro"
   - Last section sentences -> "conclusion"
   - Middle section sentences -> "main_point" or "supporting"
3. Select sentences with importance_score above the relevance_threshold
   (runtime parameter, default 0.5).
4. For each selected sentence, create L2-KP:
   - keypoint_id: unique identifier
   - source_sentence_ids: [sentence_id]
   - importance_score: computed score
   - consolidated_text: sentence.text
   - section_position: parent L1-SEC position
   - category: as determined above

Invariant T1-INV-001: Every L2-KP.source_sentence_ids references a
valid L1-SEN in the source L1-DOC.

Invariant T1-INV-002: The total_word_count of all selected keypoints
must not exceed the budget (20% of source word count) after redundancy
removal. This is a preliminary check; final enforcement occurs at T4.

#### Stage T2: Redundancy Removal (TR-002)

Input: Array of L2-KP
Output: Array of L2-RC, pruned array of L2-KP

Process:
1. Compute pairwise semantic similarity between all L2-KP
   consolidated_text values using SemanticSimilarity (TA-002).
2. Cluster L2-KPs where similarity exceeds the redundancy_threshold
   (runtime parameter, default 0.8). Each keypoint belongs to exactly
   one cluster (T2-INV-002).
3. For each cluster (L2-RC):
   - cluster_id: unique identifier
   - keypoint_ids: all keypoints in the cluster
   - representative_keypoint_id: the keypoint with highest
     importance_score
   - redundancy_score: average pairwise similarity within cluster
4. Remove non-representative keypoints from the active set.

Invariant T2-INV-001: Every L2-RC.keypoint_ids references valid L2-KP
components.

Invariant T2-INV-002: Every L2-KP belongs to exactly one L2-RC.

Invariant T2-INV-003: The representative keypoint's consolidated_text
preserves the semantic content of the cluster (enforced by selecting
the highest-scored keypoint).

#### Stage T3: Structure Assembly (TR-004)

Input: Pruned array of L2-KP, L1-DOC structure
Output: Array of L2-CB, L2-SM

Process:
1. Group retained L2-KPs by category into content blocks:
   - category "intro" -> L2-CB with block_type "intro"
   - category "main_point" and "supporting" -> L2-CB with block_type
     "main_body"
   - category "conclusion" -> L2-CB with block_type "conclusion"
2. Order keypoints within each block by section_position.
3. Order content blocks: intro (position=1), main_body (position=2),
   conclusion (position=3).
4. Create L2-SM:
   - map_id: unique identifier
   - source_document_id: reference to L1-DOC
   - content_blocks: ordered array of L2-CB
   - total_keypoints: count before redundancy removal
   - retained_keypoints: count after redundancy removal

Invariant T3-INV-001: Output contains exactly one "intro" block, at
least one "main_body" block, and exactly one "conclusion" block.

Invariant T3-INV-002: Block ordering preserves logical flow (intro
before main_body before conclusion).

Invariant T3-INV-003: Every retained L2-KP is referenced by exactly
one L2-CB.

#### Stage T4: Output Rendering (TR-003)

Input: L2-SM
Output: L3-OD

Process:
1. For each L2-CB in the structure map:
   a. Concatenate the consolidated_text of all keypoints in the block.
   b. Create L3-OB with the concatenated text, block_type from L2-CB,
      and source_keypoint_ids from L2-CB.keypoint_ids.
2. Create L3-OD:
   - document_id: unique identifier
   - output_type: declared by the runtime implementation
   - structure_map_id: reference to L2-SM
   - content_blocks: array of L3-OB
   - metadata: L3-MD with computed fields
3. Compute L3-MD:
   - source_word_count: from L1-DOC.total_word_count
   - output_word_count: sum of word counts across all L3-OB content
   - compression_ratio: output_word_count / source_word_count
   - language: L1-DOC.detected_language
   - generator_version: from configuration
4. Run output validation rules OV-001 through OV-007.

Invariant T4-INV-001: Every L3-OB.source_keypoint_ids references valid
L2-KP components.

Invariant T4-INV-002: compression_ratio <= 0.20 (C-001).

Invariant T4-INV-003: L3-MD.language == L1-DOC.detected_language
(C-002).

Invariant T4-INV-004: All text in L3-OB.content is traceable to
L1-SEN.text via chain L3-OB -> L2-KP -> L1-SEN (C-003).

### How Composition Spec Rules Are Applied

| Composition Spec Rule | Applied In | Mechanism |
|----------------------|-----------|-----------|
| TR-001 (Extract Key Points) | Stage T1 | ImportanceScorer (TA-001) |
| TR-002 (Remove Redundancy) | Stage T2 | SemanticSimilarity (TA-002) |
| TR-003 (Preserve Meaning) | Stage T4 | Structural: output from source only |
| TR-004 (Maintain Structure) | Stage T3 | Category-based block assembly |
| C-001 (Length <= 20%) | Stage T4 | compression_ratio check (T4-INV-002) |
| C-002 (Same language) | Stage T4 | Language passthrough (T4-INV-003) |
| C-003 (No new information) | Stage T4 | Source-only text (T4-INV-004) |
| C-004 (Input .txt/.md) | Input Loading | Extension check (IV-002) |

### Error Handling and Recovery

| Error Type | Condition | Recovery |
|-----------|-----------|----------|
| FileReadError | INPUT_TEXT_FILE unreadable | Halt, report IV-001 |
| UnsupportedFormatError | Extension not .txt or .md | Halt, report IV-002 |
| EmptyInputError | No content after parsing | Halt, report IV-003 |
| InvalidEncodingError | UTF-8 decode failure | Halt, report IV-004 |
| InvariantViolationError | Post-stage invariant fails | Halt, report failing invariant |
| CompressionExceededError | T4-INV-002 fails (ratio > 0.20) | Adjust relevance_threshold, retry T1 |

Recovery from compression failure: If compression_ratio > 0.20 after
T4, the pipeline raises CompressionExceededError. The caller may
optionally re-invoke with a higher relevance_threshold to reduce
keypoint count. The pipeline itself does not retry automatically.

Language validation failure (T4-INV-003) is unrecoverable since the
pipeline does not translate content. It halts with an error.

---

## Output Generation

### Rendering and Assembly Logic

The OutputRenderer (OR-001) produces output from the L2-SM according
to the declared output_type.

| Rendering Rule | Implementation | Reference |
|---------------|---------------|-----------|
| OR-001 | Each L3-OB content field rendered as text segment | COMPOSITION_SPEC Output Mapping |
| OR-002 | OutputBlocks concatenated in position order | COMPOSITION_SPEC OR-002 |
| OR-003 | "summary" type: paragraphs with blank-line separators | COMPOSITION_SPEC OR-003 |
| OR-004 | "bullet_points" type: bullet item with list marker prefix | COMPOSITION_SPEC OR-004 |
| OR-005 | "key_phrases" type: delimited list of phrases | COMPOSITION_SPEC OR-005 |
| OR-006 | Output written as plain text file | COMPOSITION_SPEC OR-006 |
| OR-007 | compression_ratio computed and checked | COMPOSITION_SPEC OR-007 |

The default runtime implementation targets output_type "summary",
producing a prose summary. Alternative output types are supported
through different OutputRenderer implementations.

### File Writing and Formatting

| Step | Operation | Reference |
|------|-----------|-----------|
| OUT-001 | Assemble L3-OB content into single text string | OR-002 |
| OUT-002 | Apply output_type-specific formatting | OR-003/004/005 |
| OUT-003 | Write text to SUMMARY_FILE with UTF-8 encoding | OR-006 |
| OUT-004 | Compute final compression_ratio | OR-007 |

The output file extension is determined by the OutputRenderer
implementation (get_file_extension method). The default implementation
uses .txt.

### Validation of Output Format

| Rule ID | Constraint | Enforcement | Traceability |
|---------|-----------|-------------|--------------|
| OV-001 | Output word count > 0 | After rendering | Basic validity |
| OV-002 | compression_ratio <= 0.20 | After rendering | C-001, T4-INV-002 |
| OV-003 | Output language matches input language | After rendering | C-002, T4-INV-003 |
| OV-004 | No content untraceable to source | After rendering | C-003, T4-INV-004 |
| OV-005 | Contains intro, main_body, conclusion blocks | After rendering | TR-004, T3-INV-001 |
| OV-006 | All source_keypoint_ids reference valid L2-KP | After rendering | Traceability integrity |
| OV-007 | All keypoint_ids in L2-CB reference valid L2-KP | After rendering | Internal consistency |

OV-004 is enforced structurally: since output text is assembled only
from L2-KP.consolidated_text values (which derive from L1-SEN.text),
no new information can be introduced. This satisfies C-003 at the
architectural level.

---

## Configuration

### Runtime Parameters

The pipeline accepts a RuntimeConfig dataclass:

| Parameter | Type | Default | Description | Reference |
|-----------|------|---------|-------------|-----------|
| input_path | Path | (required) | Path to INPUT_TEXT_FILE | IV-001 |
| output_path | Path | (required) | Path for SUMMARY_FILE | Output Mapping |
| output_type | str | "summary" | Output type discriminator | OR-001 |
| relevance_threshold | float | 0.5 | Minimum importance_score for selection | T1, TA-001 |
| redundancy_threshold | float | 0.8 | Similarity threshold for clustering | T2, TA-002 |
| target_compression_ratio | float | 0.20 | Maximum compression ratio | C-001, T4-INV-002 |
| scorer_impl | str | "default" | ImportanceScorer implementation name | TA-001 |
| similarity_impl | str | "default" | SemanticSimilarity implementation name | TA-002 |
| word_counter_impl | str | "default" | WordCounter implementation name | TA-003 |
| renderer_impl | str | "default" | OutputRenderer implementation name | OR-001 |

### Default Values and Overrides

Default values are derived from the composition spec constraints:

- target_compression_ratio = 0.20 (from C-001)
- relevance_threshold = 0.5 (midpoint of 0.0-1.0 score range)
- redundancy_threshold = 0.8 (high similarity required for clustering)

Configuration can be overridden by:
1. Direct parameter passing to run_summarizer(config)
2. Configuration file (TOML format) loaded into RuntimeConfig
3. Environment variables with prefix TEXT_SUMMARIZER_

### Environment-Specific Settings

No environment-specific settings are required. The runtime operates
purely on file I/O with no external service dependencies. All
configuration is self-contained in the RuntimeConfig dataclass.

---

## Extension Interface

### Interfaces New Implementations Must Follow

All extension interfaces are defined as Protocol contracts using
Python's typing.Protocol with @runtime_checkable. Runtime
implementations must provide concrete classes satisfying these
Protocols.

#### IP-001: InputParser Protocol

```
@runtime_checkable
class InputParser(Protocol):
    def parse(self, input_path: Path) -> DocumentStructure:
        """Parse input file into L1-DOC.
        Must satisfy IV-001 through IV-006.
        """
        ...

    def detect_language(self, text: str) -> str:
        """Return ISO 639-1 language code."""
        ...

    def tokenize_sentences(self, text: str) -> list[str]:
        """Split text into sentence strings."""
        ...

    def count_words(self, text: str) -> int:
        """Count whitespace-delimited tokens."""
        ...
```

#### TA-001: ImportanceScorer Protocol

```
@runtime_checkable
class ImportanceScorer(Protocol):
    def score(self, sentence: Sentence, context: DocumentStructure) -> float:
        """Return importance score in [0.0, 1.0].
        Must be deterministic for same input.
        Must consider position, content, and surrounding context.
        """
        ...
```

#### TA-002: SemanticSimilarity Protocol

```
@runtime_checkable
class SemanticSimilarity(Protocol):
    def compute_similarity(self, text_a: str, text_b: str) -> float:
        """Return similarity in [0.0, 1.0].
        0.0 = unrelated, 1.0 = identical meaning.
        """
        ...
```

#### TA-003: WordCounter Protocol

```
@runtime_checkable
class WordCounter(Protocol):
    def count(self, text: str) -> int:
        """Return non-negative word count.
        Must be consistent: same text always produces same count.
        """
        ...
```

#### OR-001: OutputRenderer Protocol

```
@runtime_checkable
class OutputRenderer(Protocol):
    def render(self, structure_map: StructureMap, output_type: str) -> OutputDocument:
        """Produce L3-OD satisfying OV-001 through OV-007."""
        ...

    def get_output_type(self) -> str:
        """Return the output type this renderer produces."""
        ...

    def get_file_extension(self) -> str:
        """Return file extension for output (e.g., '.txt')."""
        ...
```

### Extension Points

| Extension Point | Protocol | Variability | COMPOSITION_SPEC Reference |
|----------------|----------|-------------|---------------------------|
| Sentence boundary detection | InputParser.tokenize_sentences | Implementation choice | Variable Components table |
| Language detection | InputParser.detect_language | Implementation choice | Variable Components table |
| Importance scoring | ImportanceScorer | TF-IDF, TextRank, frequency | TA-001 |
| Relevance threshold | Runtime parameter | Configurable value | T1 |
| Semantic similarity | SemanticSimilarity | Cosine, Jaccard, embedding | TA-002 |
| Similarity threshold | Runtime parameter | Configurable value | T2 |
| Output type | OutputRenderer | summary, bullet_points, key_phrases | OR-001 |
| File extension | OutputRenderer.get_file_extension | .txt, .md, etc. | OR-001 |
| Word counting | WordCounter | Whitespace-split, linguistic | TA-003 |

### Registration of New Implementations

New implementations are registered using a dispatch registry:

```
EXTENSION_REGISTRY: dict[str, dict[str, Any]] = {
    "importance_scorer": {
        "default": DefaultImportanceScorer(),
    },
    "semantic_similarity": {
        "default": DefaultSemanticSimilarity(),
    },
    "word_counter": {
        "default": WhitespaceWordCounter(),
    },
    "output_renderer": {
        "default": SummaryRenderer(),
        "bullet_points": BulletPointRenderer(),
        "key_phrases": KeyPhraseRenderer(),
    },
}
```

To add a new implementation:
1. Create a class conforming to the appropriate Protocol.
2. Register it in EXTENSION_REGISTRY under the correct extension key.
3. Reference it by name in RuntimeConfig (e.g., scorer_impl = "tfidf").

---

## Self-Validation

### Composition Spec Compliance

| Check | Status | Evidence |
|-------|--------|----------|
| Implements all four stages (T1, T2, T3, T4) | PASS | Transformation Engine section maps each stage |
| Produces all Layer 1 components (L1-DOC, L1-SEC, L1-PAR, L1-SEN) | PASS | Input Loading section |
| Produces all Layer 2 components (L2-KP, L2-RC, L2-CB, L2-SM) | PASS | Transformation Engine section |
| Produces all Layer 3 components (L3-OD, L3-OB, L3-MD) | PASS | Output Generation section |
| Enforces input validation IV-001 through IV-006 | PASS | Input Loading validation table |
| Enforces output validation OV-001 through OV-007 | PASS | Output Generation validation table |
| Satisfies T1-INV-001, T1-INV-002 | PASS | Stage T1 description |
| Satisfies T2-INV-001, T2-INV-002, T2-INV-003 | PASS | Stage T2 description |
| Satisfies T3-INV-001, T3-INV-002, T3-INV-003 | PASS | Stage T3 description |
| Satisfies T4-INV-001 through T4-INV-004 | PASS | Stage T4 description |
| Enforces C-001 (20% compression) | PASS | T4-INV-002, OV-002 |
| Enforces C-002 (same language) | PASS | T4-INV-003, OV-003 |
| Enforces C-003 (no new information) | PASS | T4-INV-004, OV-004, structural enforcement |
| Enforces C-004 (input format) | PASS | IV-002 |
| Supports all extension protocols | PASS | Extension Interface section |

### Three-Layer Architecture Compliance

| Layer | Components | Implementation | Status |
|-------|-----------|----------------|--------|
| Layer 1 (Input Parsing) | L1-DOC, L1-SEC, L1-PAR, L1-SEN | InputParser (IP-001) | PASS |
| Layer 2 (Transformation) | L2-KP, L2-RC, L2-CB, L2-SM | Stages T1, T2, T3 | PASS |
| Layer 3 (Output Rendering) | L3-OD, L3-OB, L3-MD | Stage T4, OutputRenderer (OR-001) | PASS |

### Input Variation Handling

| Variation | Handling | Reference |
|-----------|----------|-----------|
| .txt input | Single L1-SEC with section_type "implicit" | PR-003, INP-005 |
| .md input with headings | One L1-SEC per heading | PR-003, INP-005 |
| .md input without headings | Single implicit section | PR-003 |
| Very short input (< 100 words) | Pipeline still applies, ratio enforced | T4-INV-002 |
| Very long input (> 10000 words) | Pipeline scales, word budget scales | T1-INV-002 |
| Single-paragraph document | One section, one paragraph, multiple sentences | INP-006, INP-007 |
| Multi-section document | Each section contributes keypoints | Stage T3 grouping |

### ASCII Compliance

| Check | Status |
|-------|--------|
| No em-dashes used | PASS |
| No curly quotes used | PASS |
| No Unicode characters used | PASS |
| YAML frontmatter uses plain ASCII | PASS |
| All identifiers use ASCII characters | PASS |

### Traceability Summary

| Design Section | Source Artifact | Trace |
|---------------|----------------|-------|
| Four-stage pipeline (T1-T4) | COMPOSITION_SPEC-01 Transformation Rules | Stages T1-T4 |
| Input parsing (INP-001 to INP-012) | COMPOSITION_SPEC-01 Parsing Rules | PR-001 to PR-007 |
| Output rendering (OUT-001 to OUT-004) | COMPOSITION_SPEC-01 Rendering Rules | OR-001 to OR-007 |
| Extension interfaces (5 Protocols) | COMPOSITION_SPEC-01 Extension Mechanism | IP-001, TA-001/002/003, OR-001 |
| Constraints (C-001 to C-004) | REQUIREMENT_ANALYSIS-01 Constraints | C-001 to C-004 |
| Generator identity | COMPOSITION_SPEC-01 frontmatter | Document Metadata |
| Invariants (T1 through T4) | COMPOSITION_SPEC-01 Invariants Summary | Invariants table |
| Validation rules (IV, OV) | COMPOSITION_SPEC-01 Input/Output Mapping | IV-001 to IV-006, OV-001 to OV-007 |

---

End of Runtime Implementation Design
