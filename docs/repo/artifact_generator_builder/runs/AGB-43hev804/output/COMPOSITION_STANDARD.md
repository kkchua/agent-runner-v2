---
doc_type: "composition_standard"
identity_locked: true
generator_name: "text_summarizer_ayz"
codename: "text_summarizer_ayz"
version: "1.0.0"
base_standard: "BASE_COMPOSITION_STANDARD_v1.0.md"
pattern: "Input Transformation"
---

# Composition Standard -- Text Summarizer

## Purpose

This document is the generator-specific composition standard for the
Text Summarizer (codename: text_summarizer_ayz). It adapts the universal
pattern defined in BASE_COMPOSITION_STANDARD_v1.0.md to the text
summarization domain.

This standard defines the abstract step interfaces, meta schema,
transformation rules, invariants, constraints, and extension interfaces
for the text summarizer generator. It is the contract that all runtime
implementations must satisfy.

**Reference:** BASE_COMPOSITION_STANDARD_v1.0.md, Section 10 (Meta-Workflow
Builder Factory), Section 13 (Composition Spec vs Runtime Implementation).

---

## 1. Three-Layer Architecture

The Text Summarizer follows Pattern 2 (Input Transformation) from the
base standard. Content is transformed through three layers:

```
Layer 1: INPUT PARSING
  Parse input into structured document tree
  Document -> Sections -> Paragraphs -> Sentences
      |
      v
Layer 2: TRANSFORMATION
  Analyze, transform, and compose intermediate results
  Sentences -> KeyPoints -> RedundancyClusters -> ContentBlocks
      |
      v
Layer 3: OUTPUT RENDERING
  Render final output from transformed components
  ContentBlocks -> CONDENSED_SUMMARY, KEY_POINTS_LIST
```

### Separation of Concerns

- **Layer 1 (Input Parsing):** Defines HOW to decompose input text into
  structured intermediate form.
- **Layer 2 (Transformation):** Defines HOW to analyze and compose
  intermediate results (key points, redundancy clusters, content blocks).
- **Layer 3 (Output Rendering):** Defines HOW to produce final deliverables
  (condensed summary, key points list).

---

## 2. Meta Schema Definition

The meta schema defines the intermediate representation across three layers.

### 2.1 Layer 1: Parsed Document

Layer 1 decomposes raw input text into a structured document tree.

**Component: DocumentMetadata**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| document_id | string | Yes | Unique identifier for this parsed document |
| source_format | enum | Yes | Original format: "txt" or "md" |
| language | string | Yes | Detected or declared language (ISO 639-1) |
| total_word_count | integer | Yes | Total words in source document |
| total_sentence_count | integer | Yes | Total sentences in source document |
| total_paragraph_count | integer | Yes | Total paragraphs in source document |
| total_section_count | integer | Yes | Total top-level sections identified |

**Component: Section**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| section_id | string | Yes | Unique identifier for this section |
| heading | string | No | Section heading text (empty for unstructured) |
| section_type | enum | Yes | Role: "introduction", "body", "conclusion" |
| position | integer | Yes | Zero-based ordinal position within document |
| paragraph_count | integer | Yes | Number of paragraphs in this section |
| word_count | integer | Yes | Total words in this section |

**Component: Paragraph**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| paragraph_id | string | Yes | Unique identifier for this paragraph |
| section_ref | string | Yes | Reference to parent Section.section_id |
| position | integer | Yes | Zero-based position within section |
| word_count | integer | Yes | Number of words in this paragraph |
| sentence_count | integer | Yes | Number of sentences in this paragraph |
| content | string | Yes | Raw text content of the paragraph |

**Component: Sentence**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| sentence_id | string | Yes | Unique identifier for this sentence |
| paragraph_ref | string | Yes | Reference to parent Paragraph.paragraph_id |
| section_ref | string | Yes | Reference to grandparent Section.section_id |
| position | integer | Yes | Zero-based position within paragraph |
| word_count | integer | Yes | Number of words in this sentence |
| content | string | Yes | Raw text content of the sentence |

**Layer 1 Invariants:**

- INV-L1-001: Every Sentence belongs to exactly one Paragraph.
- INV-L1-002: Every Paragraph belongs to exactly one Section.
- INV-L1-003: Sum of Section word_counts equals total_word_count.
- INV-L1-004: Sum of Sentence word_counts equals total_word_count.
- INV-L1-005: total_word_count must be greater than zero.

### 2.2 Layer 2: Transformed Content

Layer 2 analyzes the parsed document to extract key points, identify
redundancies, and compose content blocks.

**Component: KeyPoint**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| keypoint_id | string | Yes | Unique identifier for this key point |
| source_sentence_refs | array[string] | Yes | References to source Sentence components |
| content | string | Yes | Extracted or reformulated content |
| importance_score | float | Yes | Score between 0.0 and 1.0 |
| section_ref | string | Yes | Reference to source Section |
| position | integer | Yes | Ordinal position within key points list |

**Component: RedundancyCluster**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| cluster_id | string | Yes | Unique identifier for this cluster |
| member_sentence_refs | array[string] | Yes | References to sentences expressing same idea |
| representative_ref | string | Yes | Reference to selected representative sentence |
| similarity_score | float | Yes | Score between 0.0 and 1.0 indicating overlap |

**Component: ContentBlock**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| block_id | string | Yes | Unique identifier for this block |
| block_type | enum | Yes | "summary_segment", "key_point_entry", "structural_bridge" |
| content | string | Yes | Text content of this block |
| source_refs | array[string] | Yes | References to source Sentence or KeyPoint |
| position | integer | Yes | Ordinal position within output sequence |
| word_count | integer | Yes | Number of words in this block |

**Layer 2 Invariants:**

- INV-L2-001: Every KeyPoint references at least one Sentence from Layer 1.
- INV-L2-002: importance_score values must be in [0.0, 1.0].
- INV-L2-003: Every sentence in a RedundancyCluster must belong to the
  same Section.
- INV-L2-004: representative_ref must be a member of member_sentence_refs.
- INV-L2-005: ContentBlock source_refs must resolve to valid Layer 1 or
  Layer 2 components.
- INV-L2-006: No information may originate from outside the source document.

### 2.3 Layer 3: Output Document (Interface)

Layer 3 defines a generic output interface. Different runtime
implementations produce different concrete outputs by satisfying this
interface.

**Interface: OutputDocument**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| output_type | enum | Yes | "summary", "bullet_points", "key_phrases", "section_summary" |
| metadata | OutputMetadata | Yes | Metadata about the output |
| content_blocks | array[ContentBlock] | Yes | Ordered content blocks composing output |
| validation_rules | array[ValidationRule] | Yes | Rules that must pass for valid output |

**Component: OutputMetadata**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| source_document_id | string | Yes | Reference to source DocumentMetadata |
| output_word_count | integer | Yes | Total words in output |
| compression_ratio | float | Yes | Output/input word ratio (must be <= 0.2) |
| language | string | Yes | Output language (must match source) |
| generation_timestamp | string | Yes | ISO 8601 timestamp |

**Component: ValidationRule**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| rule_id | string | Yes | Unique identifier |
| rule_name | string | Yes | Human-readable name |
| rule_type | enum | Yes | "compression", "language_preservation", "no_new_info", "structure_preservation" |
| threshold | any | No | Rule-specific threshold |
| description | string | Yes | Human-readable description |

**Layer 3 Invariants:**

- INV-L3-001: OutputMetadata.language must equal DocumentMetadata.language.
- INV-L3-002: All content_blocks must have valid references to Layer 2
  components.
- INV-L3-003: validation_rules must include all required constraint types.

---

## 3. Abstract Step Interfaces

Each workflow step is defined as an abstract interface. Runtime
implementations provide concrete behavior for each step.

### 3.1 Step: load_input (LOAD-001)

| Property | Value |
|----------|-------|
| Step Name | load_input |
| Step Type | Action (deterministic) |
| Purpose | Load source text file, detect format, validate content |
| Input Contract | SOURCE_TEXT_FILE (file path) |
| Output Contract | Partial PARSED_DOCUMENT (raw text + metadata) |
| Constraints | File must exist, be non-empty, be text (not binary) |

### 3.2 Step: parse_document (PARSE-001)

| Property | Value |
|----------|-------|
| Step Name | parse_document |
| Step Type | Action (deterministic) |
| Purpose | Decompose raw text into Layer 1 document tree |
| Input Contract | Partial PARSED_DOCUMENT (raw text) |
| Output Contract | Complete PARSED_DOCUMENT (Layer 1 tree) |
| Constraints | Must produce at least one Sentence; all L1 invariants must hold |

### 3.3 Step: validate_layer_1 (VAL-L1-001)

| Property | Value |
|----------|-------|
| Step Name | validate_layer_1 |
| Step Type | Action (deterministic) |
| Purpose | Validate all five Layer 1 invariants |
| Input Contract | PARSED_DOCUMENT |
| Output Contract | VALIDATION_REPORT (Layer 1 results) |
| Constraints | All five INV-L1-* invariants must pass |

### 3.4 Step: extract_key_points (STEP-EXT-001)

| Property | Value |
|----------|-------|
| Step Name | extract_key_points |
| Step Type | Prompt (LLM-driven) |
| Purpose | Identify most important sentences with importance scores |
| Input Contract | PARSED_DOCUMENT (all Sentences) |
| Output Contract | KEY_POINTS_DATA (KeyPoint[]) |
| Constraints | INV-L2-001 (non-empty refs), INV-L2-002 (score range) |

### 3.5 Step: remove_redundancy (STEP-RED-001)

| Property | Value |
|----------|-------|
| Step Name | remove_redundancy |
| Step Type | Prompt (LLM-driven) |
| Purpose | Cluster semantically similar sentences |
| Input Contract | PARSED_DOCUMENT (Sentences), KEY_POINTS_DATA |
| Output Contract | REDUNDANCY_CLUSTERS (RedundancyCluster[]) |
| Constraints | INV-L2-003 (same section), INV-L2-004 (member ref) |

### 3.6 Step: preserve_meaning (STEP-MEAN-001)

| Property | Value |
|----------|-------|
| Step Name | preserve_meaning |
| Step Type | Prompt (LLM-driven) |
| Purpose | Compose summary segments from key points and source sentences |
| Input Contract | KEY_POINTS_DATA, REDUNDANCY_CLUSTERS, PARSED_DOCUMENT |
| Output Contract | CONTENT_BLOCKS (ContentBlock[]) draft |
| Constraints | INV-L2-005 (valid refs), INV-L2-006 (no external info) |

### 3.7 Step: maintain_structure (STEP-STR-001)

| Property | Value |
|----------|-------|
| Step Name | maintain_structure |
| Step Type | Action (deterministic) |
| Purpose | Enforce document ordering and compression constraint |
| Input Contract | CONTENT_BLOCKS, PARSED_DOCUMENT |
| Output Contract | CONTENT_BLOCKS (final ordered) |
| Constraints | C-001 (summary <= 20% of source) |

### 3.8 Step: validate_output (VAL-OUT-001)

| Property | Value |
|----------|-------|
| Step Name | validate_output |
| Step Type | Action (deterministic) |
| Purpose | Validate all constraints and Layer 3 invariants |
| Input Contract | CONTENT_BLOCKS, PARSED_DOCUMENT, KEY_POINTS_DATA |
| Output Contract | OUTPUT_ASSEMBLY, VALIDATION_REPORT (complete) |
| Constraints | C-001, C-002, C-003, INV-L3-001, INV-L3-002, INV-L3-003 |

### 3.9 Step: render_output (RENDER-001)

| Property | Value |
|----------|-------|
| Step Name | render_output |
| Step Type | Action (deterministic) |
| Purpose | Render final CONDENSED_SUMMARY and KEY_POINTS_LIST |
| Input Contract | OUTPUT_ASSEMBLY, CONTENT_BLOCKS, KEY_POINTS_DATA |
| Output Contract | CONDENSED_SUMMARY, KEY_POINTS_LIST |
| Constraints | Output format must match declared output_type |

---

## 4. Input Mapping

### 4.1 Input Artifact Contract

| Artifact Key | Format | Required | Description |
|--------------|--------|----------|-------------|
| SOURCE_TEXT_FILE | .txt or .md | Yes | Source text document |

Per BASE_COMPOSITION_STANDARD_v1.0.md Section 6.5, the `_FILE` suffix
indicates this is a file input. The caller provides a file path.

### 4.2 Input Parsing Rules

**MAP-001: File Access and Validation**
- Verify file exists and is readable.
- Verify file is not empty.
- Verify file contains text (not binary).
- Detect format from extension (.txt or .md).

**MAP-002: DocumentMetadata Extraction**
- Generate document_id at parse time.
- Detect source_format from file extension.
- Detect language from content analysis.
- Count words (whitespace-delimited), sentences (punctuation-delimited),
  paragraphs (blank-line-separated), sections (heading-based or position-based).

**MAP-003: Section Identification**
- Markdown: headings (# through ######) define sections.
- Plain text: paragraph blocks define sections by position.
- Section type assigned by position: introduction, body, conclusion.

**MAP-004: Paragraph and Sentence Decomposition**
- Paragraphs separated by blank lines.
- Sentences delimited by . ! ? followed by whitespace or end-of-string.
- Unique IDs assigned to all components.

---

## 5. Output Mapping

### 5.1 Output Artifact Contract

| Artifact Key | Format | Description |
|--------------|--------|-------------|
| CONDENSED_SUMMARY | Markdown | Prose summary with YAML frontmatter |
| KEY_POINTS_LIST | Markdown | Ordered key points with importance scores |

### 5.2 Output Rendering Rules

**MAP-OM-001: CONDENSED_SUMMARY Rendering**
1. Select ContentBlocks with block_type "summary_segment".
2. Order by position ascending.
3. Concatenate into prose form.
4. Preserve introduction -> body -> conclusion structure.
5. Compute compression_ratio = output_word_count / total_word_count.

**MAP-OM-002: KEY_POINTS_LIST Rendering**
1. Select all KeyPoint components.
2. Order by importance_score descending.
3. Format as numbered list with importance annotation.

### 5.3 Output Delivery Contract

Per BASE_COMPOSITION_STANDARD_v1.0.md Section 6.6, final output artifacts
are written to the declared output location after all validation passes.

| Artifact Key | Delivery Location |
|--------------|-------------------|
| CONDENSED_SUMMARY | Workflow output directory |
| KEY_POINTS_LIST | Workflow output directory |

---

## 6. Constraints

All runtime implementations MUST satisfy these hard constraints.

| ID | Constraint | Measured At |
|----|------------|-------------|
| C-001 | Summary word count <= 20% of original word count | After STEP-STR-001 |
| C-002 | Summary language must match input document language | After STEP-MEAN-001 |
| C-003 | Must not introduce information not in original | After STEP-MEAN-001 |

---

## 7. Invariants Summary

| ID | Invariant | Layer | Stage |
|----|-----------|-------|-------|
| INV-L1-001 | Every Sentence belongs to exactly one Paragraph | L1 | Input Parsing |
| INV-L1-002 | Every Paragraph belongs to exactly one Section | L1 | Input Parsing |
| INV-L1-003 | Sum of Section word_counts equals total | L1 | Input Parsing |
| INV-L1-004 | Sum of Sentence word_counts equals total | L1 | Input Parsing |
| INV-L1-005 | total_word_count > 0 | L1 | Input Parsing |
| INV-L2-001 | KeyPoint references at least one Sentence | L2 | Extract Key Points |
| INV-L2-002 | importance_score in [0.0, 1.0] | L2 | Extract Key Points |
| INV-L2-003 | Cluster sentences from same Section | L2 | Remove Redundancy |
| INV-L2-004 | representative_ref in cluster members | L2 | Remove Redundancy |
| INV-L2-005 | ContentBlock source_refs valid | L2 | All steps |
| INV-L2-006 | No external information introduced | L2 | Preserve Meaning |
| INV-L3-001 | Output language matches source | L3 | Output Rendering |
| INV-L3-002 | ContentBlocks reference valid L2 components | L3 | Output Rendering |
| INV-L3-003 | Validation rules include all constraints | L3 | Output Rendering |

---

## 8. Extension Interfaces

### 8.1 Protocol: InputParser

```
InputParser:
  parse(source_file: str) -> ParsedDocument
  validate(parsed: ParsedDocument) -> ValidationResult
```

Implementations may provide specialized parsers for different input formats
while producing the same Layer 1 schema.

### 8.2 Protocol: TransformationAlgorithm

```
TransformationAlgorithm:
  extract_key_points(parsed: ParsedDocument) -> KeyPoint[]
  remove_redundancy(keypoints: KeyPoint[], parsed: ParsedDocument) -> RedundancyCluster[]
  preserve_meaning(keypoints: KeyPoint[], clusters: RedundancyCluster[]) -> ContentBlock[]
  maintain_structure(blocks: ContentBlock[], parsed: ParsedDocument) -> ContentBlock[]
```

Implementations may use different algorithms (TF-IDF, TextRank, embedding-based)
while satisfying the same abstract step contracts.

### 8.3 Protocol: OutputRenderer

```
OutputRenderer:
  render_summary(blocks: ContentBlock[], metadata: OutputMetadata) -> str
  render_keypoints(points: KeyPoint[], metadata: OutputMetadata) -> str
  supports_output_type(output_type: str) -> bool
```

Implementations provide renderers for specific output types and formats.

### 8.4 Protocol: ValidationStrategy

```
ValidationStrategy:
  validate_output(output: OutputDocument, parsed: ParsedDocument) -> ValidationResult
  check_constraint(constraint_id: str, output: OutputDocument) -> ConstraintResult
```

Implementations may use rule-based or ML-based validation approaches.

---

## 9. Extension Points

Future extension opportunities identified from the requirement analysis.

| ID | Extension Opportunity | Impact on Spec |
|----|----------------------|----------------|
| E-001 | Multi-language support with target language selection | Adds translation step to Layer 2 |
| E-002 | Configurable summary length (10%, 30%) | Makes C-001 threshold configurable |
| E-003 | Bullet-point summary format | New output_type in Layer 3 |
| E-004 | Section-level summaries for structured documents | New output_type |
| E-005 | Importance threshold filtering for key points | Adds filter parameter to STEP-EXT-001 |

---

## 10. Fixed vs Variable Parts

### Fixed (cannot vary across implementations)

- Layer 1 meta schema (ParsedDocument structure).
- Layer 2 meta schema (KeyPoint, RedundancyCluster structure).
- Abstract step interfaces (LOAD-001 through RENDER-001).
- All invariants (INV-L1 through INV-L3).
- All constraints (C-001 through C-003).
- Input mapping rules (MAP-001 through MAP-004).

### Variable (may differ across implementations)

- Layer 3 OutputDocument.output_type enum value.
- Content block ordering strategy in STEP-STR-001.
- Importance scoring algorithm in STEP-EXT-001.
- Redundancy detection algorithm in STEP-RED-001.
- Output serialization format (Markdown, JSON, plain text, HTML).

---

## 11. Runtime Implementation Model

The composition standard defines abstract step interfaces. Each runtime
implementation provides concrete behavior by mapping steps to prompt
templates and action functions.

### Implementation Component Mapping

Each implementation SHALL provide:
1. Prompt template -- for prompt-driven steps
2. Action function -- for action-driven steps

Implementations MAY reuse shared components from the workflow package
or provide implementation-specific components.

### Component Architecture

```
workflows/text_summarizer_ayz/
    actions.py              -- shared action functions
    prompts/                -- shared prompt templates
    workflow.toml           -- step sequence (fixed)
    impls/
        default/
            default.impl.md -- component mapping
            prompts/        -- impl-specific prompts
            actions.py      -- impl-specific actions
```

---

## Self-Validation

| Check | Status | Notes |
|-------|--------|-------|
| Meta schema well-defined | PASS | Layer 1, 2, 3 components fully specified |
| Input reliably mappable | PASS | MAP-001 through MAP-004 defined |
| Output reliably generable | PASS | MAP-OM-001, MAP-OM-002 defined |
| Extension mechanism clear | PASS | Protocol interfaces defined |
| Follows base standard | PASS | Pattern 2 three-layer architecture applied |
| Abstract step interfaces defined | PASS | 9 steps with input/output contracts |
| All constraints included | PASS | C-001, C-002, C-003 from requirement |
| All invariants documented | PASS | 14 invariants (INV-L1 through INV-L3) |
| Input uses _FILE suffix | PASS | SOURCE_TEXT_FILE follows Section 6.5 |
| Output delivery declared | PASS | Output delivery contract section present |
| Identity locked | PASS | codename = text_summarizer_ayz |
| ASCII-only | PASS | No em-dashes, curly quotes, or Unicode |
