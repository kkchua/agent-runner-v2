---
doc_type: "runtime_impl"
identity_locked: true
generator_name: "text_summarizer_ayz"
codename: "text_summarizer_ayz"
version: "1.0.0"
source_composition_spec: "COMPOSITION_SPEC-01.md"
source_requirement_analysis: "REQUIREMENT_ANALYSIS-01.md"
base_standard: "BASE_COMPOSITION_STANDARD_v1.0.md"
---

# Runtime Implementation Design -- Text Summarizer (Intermediate Notes)

## Implementation Architecture

### High-Level Structure

The default runtime implementation follows the three-layer Input Transformation
pattern defined in BASE_COMPOSITION_STANDARD_v1.0.md. It executes the
composition spec by:

1. Loading and parsing the SOURCE_TEXT_FILE into Layer 1 (ParsedDocument).
2. Executing the transformation pipeline (Layer 1 -> Layer 2 -> Layer 3).
3. Rendering output artifacts (CONDENSED_SUMMARY, KEY_POINTS_LIST).

### Component Modules

The implementation decomposes into five modules:

| Module | Responsibility |
|--------|---------------|
| InputLoader | File I/O, format detection, text validation |
| DocumentParser | Layer 1 decomposition (Sections, Paragraphs, Sentences) |
| TransformationEngine | Layer 2 analysis (key points, redundancy, meaning) |
| StructureValidator | Layer 2 ordering, bridging, compression check |
| OutputRenderer | Layer 3 serialization to CONDENSED_SUMMARY and KEY_POINTS_LIST |

### Data Flow

```
SOURCE_TEXT_FILE (path)
    |
    v
[InputLoader]
    | raw_text, file_metadata
    v
[DocumentParser]
    | ParsedDocument (Layer 1)
    v
[TransformationEngine]
    | KeyPoint[], RedundancyCluster[], ContentBlock[] (Layer 2)
    v
[StructureValidator]
    | Final ContentBlock[] with positions validated
    v
[OutputRenderer]
    | CONDENSED_SUMMARY (prose), KEY_POINTS_LIST (structured list)
    v
Output Directory
```

### Pipeline Execution Sequence

| Order | Step | Step ID | Type | Source |
|-------|------|---------|------|--------|
| 1 | Load Input | LOAD-001 | Action | MAP-001 |
| 2 | Parse Document | PARSE-001 | Action | MAP-002, MAP-003, MAP-004 |
| 3 | Validate Layer 1 | VAL-L1-001 | Action | INV-L1-001 through INV-L1-005 |
| 4 | Extract Key Points | STEP-EXT-001 | Prompt | COMPOSITION_SPEC Transformation Rules |
| 5 | Remove Redundancy | STEP-RED-001 | Prompt | COMPOSITION_SPEC Transformation Rules |
| 6 | Preserve Meaning | STEP-MEAN-001 | Prompt | COMPOSITION_SPEC Transformation Rules |
| 7 | Maintain Structure | STEP-STR-001 | Action | COMPOSITION_SPEC Transformation Rules |
| 8 | Validate Output | VAL-OUT-001 | Action | C-001, C-002, C-003 |
| 9 | Render Output | RENDER-001 | Action | MAP-OM-001, MAP-OM-002 |

---

## Input Loading

### File Access Strategy

The InputLoader module performs the following operations:

1. Accept SOURCE_TEXT_FILE as an absolute or relative file path.
2. Verify the file exists using OS-level file check.
3. Read the file content using UTF-8 encoding with fallback detection.
4. Detect format from file extension (.txt or .md).
5. Reject non-text files (binary detection via null byte scan).

### Parsing Strategy

The DocumentParser module decomposes raw text into Layer 1 components:

**For Markdown (.md) input:**
- Section boundaries are detected by heading markers (# through ######).
- Each heading creates a new Section with section_type determined by position.
- Paragraphs within sections are separated by blank lines.
- Sentences are delimited by . ! ? followed by whitespace or end-of-string.

**For Plain Text (.txt) input:**
- If the document has 3 or more paragraph blocks, assign first as
  "introduction", last as "conclusion", rest as "body".
- If fewer than 3 blocks, all are assigned "body" type.
- Paragraphs are separated by blank lines.
- Sentences use the same punctuation-based delimiting as .md.

### Layer 1 Validation

After parsing, validate all five Layer 1 invariants:

- INV-L1-001: Every Sentence has exactly one parent Paragraph.
- INV-L1-002: Every Paragraph has exactly one parent Section.
- INV-L1-003: Sum of Section word_counts matches total_word_count.
- INV-L1-004: Sum of Sentence word_counts matches total_word_count.
- INV-L1-005: total_word_count > 0.

If any invariant fails, halt with an error diagnostic.

---

## Transformation Engine

### Step: Extract Key Points (STEP-EXT-001)

This is a Prompt-driven step. The transformation engine:

1. Constructs a prompt containing the full ParsedDocument (all Sentences).
2. Sends the prompt to the LLM coder, requesting extraction of key points.
3. The prompt instructs the coder to:
   - Identify the most important sentences per section.
   - Assign importance_score in [0.0, 1.0].
   - Ensure at least 3 key points for documents with > 5 sentences.
   - Cover all sections (unless section has < 2 sentences).
4. Parse the coder's response into KeyPoint[] components.
5. Validate INV-L2-001 (each KeyPoint references at least one Sentence) and
   INV-L2-002 (importance_score in [0.0, 1.0]).

**Importance Scoring Algorithm (Default):**
- Position weight: sentences in introduction and conclusion get +0.15.
- Frequency weight: keyword density relative to document average.
- Uniqueness weight: semantic distance from previously selected key points.
- Final scores normalized to [0.0, 1.0] range.

### Step: Remove Redundancy (STEP-RED-001)

This is a Prompt-driven step. The transformation engine:

1. Constructs a prompt containing all Sentences from Layer 1.
2. Sends the prompt to the LLM coder, requesting redundancy analysis.
3. The prompt instructs the coder to:
   - Compare all sentence pairs for semantic similarity.
   - Group similar sentences into RedundancyCluster components.
   - Select the most concise and clear sentence as representative.
4. Parse the coder's response into RedundancyCluster[] components.
5. Validate INV-L2-003 (cluster sentences from same Section) and
   INV-L2-004 (representative_ref is a member).

**Redundancy Detection Algorithm (Default):**
- Cosine similarity on term-frequency vectors for initial candidate pairs.
- LLM confirmation for borderline cases (similarity 0.5 to 0.8).
- Clustering threshold: similarity >= 0.75 triggers cluster formation.
- Representative selection: shortest sentence with highest information density.

### Step: Preserve Meaning (STEP-MEAN-001)

This is a Prompt-driven step. The transformation engine:

1. Constructs a prompt containing:
   - All KeyPoint components (with importance scores).
   - All RedundancyCluster components (with representatives).
   - DocumentMetadata (for language and structure context).
2. Sends the prompt to the LLM coder, requesting meaning preservation.
3. The prompt instructs the coder to:
   - Compose summary_segment ContentBlocks from KeyPoints and source Sentences.
   - Ensure the core message (highest-importance KeyPoints) is present.
   - Verify no paraphrase introduces unsupported claims.
   - Maintain introduction -> body -> conclusion flow.
4. Parse the coder's response into ContentBlock[] components.
5. Validate INV-L2-005 (source_refs valid) and INV-L2-006 (no external info).

### Step: Maintain Structure (STEP-STR-001)

This is an Action-driven step (deterministic). The transformation engine:

1. Receives ordered ContentBlock[] from STEP-MEAN-001.
2. Verifies ContentBlock positions match Section positions from Layer 1.
3. Reorders blocks if necessary to maintain intro -> body -> conclusion flow.
4. Inserts structural_bridge ContentBlocks if transitions are needed between
   sections (deterministic template-based text).
5. Computes final word counts per block and aggregates for output.
6. Checks C-001: total summary_segment word count <= 20% of total_word_count.
   - If exceeded, trim lowest-importance ContentBlocks until constraint is met.

---

## Output Generation

### CONDENSED_SUMMARY Artifact

Produced by applying MAP-OM-001:

1. Select all ContentBlocks with block_type "summary_segment".
2. Order by position (ascending).
3. Concatenate content into prose form.
4. Preserve logical structure: introduction first, body in order, conclusion last.
5. Compute compression_ratio = output_word_count / total_word_count.
6. Validate C-001: compression_ratio <= 0.20.
7. Validate C-002: language matches source.
8. Write to output directory as Markdown file with YAML frontmatter.

**Output format:**
```markdown
---
artifact_key: "CONDENSED_SUMMARY"
source_document_id: "{id}"
compression_ratio: {ratio}
language: "{lang}"
generation_timestamp: "{iso8601}"
---

{Prose summary content}
```

### KEY_POINTS_LIST Artifact

Produced by applying MAP-OM-002:

1. Select all KeyPoint components from Layer 2.
2. Order by importance_score descending (default) or by position (document flow).
3. Format each point as a numbered list entry with importance_score annotation.
4. Validate C-003: every key point traces to source sentences (INV-L2-001).
5. Write to output directory as Markdown file with YAML frontmatter.

**Output format:**
```markdown
---
artifact_key: "KEY_POINTS_LIST"
source_document_id: "{id}"
keypoint_count: {count}
generation_timestamp: "{iso8601}"
---

## Key Points

1. {KeyPoint content} (importance: {score})
2. {KeyPoint content} (importance: {score})
...
```

---

## Configuration

### Runtime Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| max_compression_ratio | float | 0.20 | Maximum summary-to-source word ratio |
| min_keypoints | integer | 3 | Minimum key points for documents with > 5 sentences |
| redundancy_threshold | float | 0.75 | Semantic similarity threshold for clustering |
| importance_position_weight | float | 0.15 | Bonus for intro/conclusion sentences |
| output_format | enum | "markdown" | Output serialization format |
| language_detection | enum | "auto" | "auto" or explicit ISO 639-1 code |

### Parameter Overrides

Parameters can be overridden via:
1. Workflow invocation arguments (highest priority).
2. Environment variables (prefix: TEXTSUM_).
3. Default values in the implementation (lowest priority).

---

## Extension Interface

### Adding New Output Types

To add a new output type (e.g., "bullet_points"):

1. Implement the OutputRenderer protocol for the new type.
2. Add a new output rendering method that selects and formats ContentBlocks.
3. Declare the new output_type in the implementation's supported types list.
4. No changes required to Layer 1 or Layer 2 processing.

### Adding New Transformation Algorithms

To replace the default importance scoring or redundancy detection:

1. Implement the TransformationAlgorithm protocol.
2. Register the new algorithm in the implementation's component mapping.
3. Ensure all invariants (INV-L2-*) still hold with the new algorithm.
4. The pipeline executor resolves the algorithm at runtime from the mapping.

### Adding New Input Parsers

To support additional input formats (e.g., .pdf, .docx):

1. Implement the InputParser protocol.
2. Ensure the parser produces a ParsedDocument conforming to Layer 1 schema.
3. Register the parser for the new file extension.
4. Existing .txt and .md parsers remain unchanged.

---

## Error Handling

| Error Condition | Error Type | Recovery |
|----------------|------------|----------|
| File not found | FileNotFoundError | Halt with diagnostic message |
| Empty file | EmptyDocumentError | Halt with diagnostic message |
| Binary content detected | BinaryContentError | Halt with diagnostic message |
| No parseable sentences | NoContentError | Halt with diagnostic message |
| Layer 1 invariant violation | StructureError | Halt with diagnostic indicating which invariant |
| Compression ratio exceeded | ConstraintViolationError | Trim low-importance blocks; re-validate |
| Language mismatch | LanguageMismatchError | Halt with diagnostic |
| LLM coder response invalid | CoderResponseError | Retry up to 2 times; then halt |
| External info detected | ProvenanceError | Halt with diagnostic identifying the violating block |

---

## Self-Validation

| Check | Status | Notes |
|-------|--------|-------|
| All abstract steps mapped | PASS | STEP-EXT-001, STEP-RED-001, STEP-MEAN-001, STEP-STR-001 all have concrete behavior |
| Data flow is complete | PASS | Input to Layer 1 to Layer 2 to Layer 3 to Output |
| All constraints addressed | PASS | C-001, C-002, C-003 checked at appropriate stages |
| Error handling defined | PASS | All failure modes have recovery strategies |
| Extension points documented | PASS | InputParser, TransformationAlgorithm, OutputRenderer protocols |
| No invented scope | PASS | All content traces to COMPOSITION_SPEC-01.md |
| ASCII-only | PASS | No em-dashes, curly quotes, or Unicode |
