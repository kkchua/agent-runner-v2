---
doc_type: "composition_standard"
identity_locked: true
generator_codename: "text_summarizer_ayz"
generator_name: "Text Summarizer"
version: "1.0.0"
architecture_pattern: "Pattern2_Input_Transformation"
base_standard: "BASE_COMPOSITION_STANDARD_v1.0.md"
---

# Composition Standard: Text Summarizer (text_summarizer_ayz)

## 1. Overview

This composition standard defines the step contracts, transformation rules,
invariants, extension interfaces, and input/output contracts for the
text_summarizer_ayz generator. It is derived from
BASE_COMPOSITION_STANDARD_v1.0.md (Sections 1 through 9) and tailored
to the text summarization domain.

This generator follows Pattern 2 (Input Transformation) with a three-layer
pipeline:

  Layer 1: Input Parsing
  Layer 2: Transformation
  Layer 3: Output Rendering

Two output implementations are supported:
  - summary (default): Condensed prose summary
  - key_points: Ordered list with importance scores

All content traces to COMPOSITION_SPEC-01.md, RUNTIME_IMPL-01.md, and
BASE_COMPOSITION_STANDARD_v1.0.md. No scope has been invented.


## 2. Three-Layer Architecture

### Layer 1: Input Parsing

Parse the input document into a structured intermediate representation.
Extracts document metadata, text segments at sentence and paragraph
granularity, and paragraph groupings.

Result: ParsedDocument containing DocumentContext, TextSegments, Paragraphs.

### Layer 2: Transformation

Analyze the parsed document through five ordered stages:
  TR-S1: Region Classification
  TR-S2: Redundancy Detection
  TR-S3: Importance Scoring
  TR-S4: Core Message Identification
  TR-S5: Profile Assembly

Result: AnalysisResult containing AnalyzedSegments, RedundancyClusters,
DocumentProfile.

### Layer 3: Output Rendering

Render the final output from the analyzed content. The rendering strategy
varies by implementation:
  - summary: Three-block prose (intro, main_points, conclusion)
  - key_points: Numbered list with importance scores

Result: OutputDocument with implementation-specific content blocks.


## 3. Step Contracts

Each step has a defined purpose, input/output contract, and constraints.

### Step 1: parse_input

| Property | Value |
|---|---|
| Step name | parse_input |
| Step type | Action-driven |
| Action function | parse_input_document |
| Extension point | EP-001 (InputParser Protocol) |
| Pipeline layer | Layer 1: Input Parsing |

Purpose: Validate the input file and parse it into a structured intermediate
representation.

Input: INPUT_FILE (.txt or .md)

Output: PARSED_DOCUMENT (JSON)
  Contains: DocumentContext (M-DOC-001), TextSegments (M-SEG-001),
  Paragraphs (M-PAR-001)

Constraints:
  - IP-VAL-01: File exists and is readable
  - IP-VAL-02: File extension is .txt or .md
  - IP-VAL-03: File is non-empty
  - IP-VAL-04: File encoding is UTF-8 compatible
  - IM-VAL-01: Word count consistency (5% tolerance)
  - IM-VAL-02: All paragraph references valid
  - IM-VAL-03: Sequential contiguous positions
  - IM-VAL-04: Valid ISO 639-1 language code

### Step 2: analyze_structure

| Property | Value |
|---|---|
| Step name | analyze_structure |
| Step type | Prompt-driven |
| Prompt template | prompts/02_analyze_structure.txt |
| Role policy | analyst |
| Pipeline layer | Layer 2: Transformation (first phase) |

Purpose: Assign each TextSegment to a logical region (intro, body,
conclusion) and detect semantic redundancy clusters.

Input: PARSED_DOCUMENT

Output: ANALYZED_STRUCTURE (JSON)
  Contains: AnalyzedSegments with region and redundancy info,
  RedundancyClusters (M-CLU-001)

Invariants:
  - IV-S1: Every TextSegment has exactly one region (HARD)
  - IV-S2: Cluster representative has is_redundant = false (HARD)

Transformation stages: TR-S1, TR-S2

Review loop: self-referencing, max_iterations = 1

### Step 3: score_importance

| Property | Value |
|---|---|
| Step name | score_importance |
| Step type | Prompt-driven |
| Prompt template | prompts/03_score_importance.txt |
| Role policy | analyst |
| Pipeline layer | Layer 2: Transformation (second phase) |

Purpose: Score each AnalyzedSegment by informational significance.

Input: ANALYZED_STRUCTURE

Output: SCORED_SEGMENTS (JSON)
  Contains: AnalyzedSegments with importance_score populated

Invariants:
  - IV-S3 (partial): Scores enable core message identification (HARD)

Transformation stages: TR-S3

Review loop: self-referencing, max_iterations = 1

### Step 4: identify_core_message

| Property | Value |
|---|---|
| Step name | identify_core_message |
| Step type | Prompt-driven |
| Prompt template | prompts/04_identify_core_message.txt |
| Role policy | analyst |
| Pipeline layer | Layer 2: Transformation (third phase) |

Purpose: Identify the central thesis and assemble the complete
DocumentProfile.

Input: SCORED_SEGMENTS

Output: ANALYSIS_RESULT (JSON)
  Contains: AnalyzedSegments with is_core_message flags,
  DocumentProfile (M-PRF-001)

Invariants:
  - IV-S3: Core message segment has highest importance score (HARD)
  - IV-S4: core_thesis is non-empty and matches a core message segment (HARD)
  - IV-S5: total_unique_assertions matches non-redundant segment count (HARD)

Transformation stages: TR-S4, TR-S5

Review loop: self-referencing, max_iterations = 1

### Step 5: render_output

| Property | Value |
|---|---|
| Step name | render_output |
| Step type | Action-driven |
| Default action | render_summary |
| Override action (key_points) | render_key_points |
| Extension point | EP-003 (OutputRenderer Protocol) |
| Pipeline layer | Layer 3: Output Rendering |

Purpose: Render the final output document from the analysis result.

Input: ANALYSIS_RESULT

Output: OUTPUT_DOCUMENT (JSON)
  Contains: OutputDocument (M-OUT-001), OutputMetadata (M-OUT-002),
  content blocks (M-OUT-003 for summary, M-OUT-004 for key_points)

Rendering rules:
  - OR-001 (summary): Three-block prose (intro, main_points, conclusion)
  - OR-002 (key_points): Numbered list ordered by importance descending

Invariants:
  - IV-G1: source_language preserved (HARD)
  - IV-G2: original_content immutable (HARD)
  - IV-G3: total word count invariant (HARD)

### Step 6: validate_output

| Property | Value |
|---|---|
| Step name | validate_output |
| Step type | Action-driven |
| Default action | validate_summary |
| Override action (key_points) | validate_key_points |
| Extension point | EP-004 (ValidationStrategy Protocol) |
| Pipeline layer | Layer 3: Output Rendering (validation) |

Purpose: Validate the rendered output against all applicable quality rules.

Input: OUTPUT_DOCUMENT, ANALYSIS_RESULT

Output: VALIDATION_RESULT (JSON), OUTPUT_SUMMARY or OUTPUT_KEY_POINTS

Validation rules (summary):
  - OV-001: Compression ratio <= 0.20
  - OV-002: Source language preserved
  - OV-003: No new information introduced
  - OV-004: Core message retained
  - OV-005: Logical flow preserved (intro -> main -> conclusion)
  - OV-009: Single coherent document

Validation rules (key_points):
  - OV-002: Source language preserved
  - OV-003: No new information introduced
  - OV-004: Core message retained
  - OV-006: Points ordered by importance descending
  - OV-007: Original wording preserved (no paraphrase)
  - OV-008: All importance scores valid in [0.0, 1.0]
  - OV-009: Single coherent document

### Step 7: step_completion

| Property | Value |
|---|---|
| Step name | step_completion |
| Step type | Action-driven |
| Action function | step_completion |
| Pipeline layer | Terminal |

Purpose: Finalize job execution and write meta.json sidecar.

Input: VALIDATION_RESULT

Output: META_SIDECAR (meta.json)


## 4. Meta Schema

### Layer 1 Components

M-DOC-001 DocumentContext:
  source_language (string, required) -- ISO 639-1 code
  source_format (enum: txt|md, required) -- File format
  source_word_count (int, required) -- Total word count
  source_file_path (string, required) -- Absolute path to input
  paragraph_count (int, required) -- Number of paragraphs
  sentence_count (int, required) -- Number of sentences

M-SEG-001 TextSegment:
  segment_id (string, required) -- Unique identifier
  content (string, required) -- Verbatim text content
  segment_type (enum: sentence|paragraph, required) -- Granularity
  position (int, required) -- Ordinal position (1-based)
  region (enum: intro|body|conclusion, optional) -- Logical region
  word_count (int, required) -- Word count of this segment

M-PAR-001 Paragraph:
  paragraph_id (string, required) -- Unique identifier
  segment_ids (list[string], required) -- Ordered TextSegment IDs
  position (int, required) -- Ordinal position
  word_count (int, required) -- Total word count

### Layer 2 Components

M-ANL-001 AnalyzedSegment:
  segment_id (string, required) -- Reference to source TextSegment
  importance_score (float, required) -- Score from 0.0 to 1.0
  is_redundant (bool, required) -- Whether duplicates another segment
  redundancy_cluster_id (string, optional) -- Cluster reference
  is_core_message (bool, required) -- Whether expresses central thesis
  original_content (string, required) -- Verbatim text (immutable)

M-CLU-001 RedundancyCluster:
  cluster_id (string, required) -- Unique identifier
  representative_segment_id (string, required) -- Representative segment
  member_segment_ids (list[string], required) -- All member segment IDs
  redundancy_type (enum: repetition|elaboration|restatement, required)

M-PRF-001 DocumentProfile:
  core_thesis (string, required) -- Central message of the document
  region_segments (map, required) -- Segment IDs grouped by region
  total_unique_assertions (int, required) -- Non-redundant segment count
  importance_distribution (list[float], required) -- Sorted scores descending
  mean_importance (float, required) -- Average importance score

### Layer 3 Components

M-OUT-001 OutputDocument:
  output_type (enum: summary|key_points, required)
  metadata (OutputMetadata, required)
  content_blocks (list, required)
  validation_status (enum: pass|fail|warn, required)

M-OUT-002 OutputMetadata:
  source_language (string, required) -- Must match input language
  source_word_count (int, required)
  output_word_count (int, required)
  compression_ratio (float, required)
  implementation (string, required)
  generation_timestamp (string, required) -- ISO 8601

M-OUT-003 SummaryContentBlock:
  block_type (enum: intro|main_points|conclusion, required)
  prose (string, required)
  source_segment_ids (list[string], required)

M-OUT-004 KeyPointContentBlock:
  rank (int, required) -- Position in importance ordering
  original_text (string, required) -- Verbatim text
  importance_score (float, required)
  source_segment_id (string, required)


## 5. Invariants Summary

| Invariant | Stage | Condition | Severity |
|---|---|---|---|
| IV-S1 | TR-S1 | Every TextSegment has exactly one region | HARD |
| IV-S2 | TR-S2 | Cluster representative is not marked redundant | HARD |
| IV-S3 | TR-S3/S4 | Core message segment has highest importance score | HARD |
| IV-S4 | TR-S4 | core_thesis is non-empty and matches core message segment | HARD |
| IV-S5 | TR-S5 | unique_assertions count matches non-redundant count | HARD |
| IV-G1 | Global | source_language preserved throughout pipeline | HARD |
| IV-G2 | Global | No segment content is modified (immutable) | HARD |
| IV-G3 | Global | Total word count is invariant across all layers | HARD |


## 6. Extension Interfaces

### EP-001: InputParser Protocol

  parse(input_file_path: string) -> ParsedDocument
    Precondition: input_file_path exists and passes IP-VAL rules
    Postcondition: returns valid DocumentContext + TextSegments + Paragraphs
    Must satisfy: IM-VAL-01 through IM-VAL-04

Allowed variations:
  - Different sentence segmentation algorithms
  - Different language detection methods
  - Different paragraph boundary detection

### EP-002: TransformationEngine Protocol

  analyze(parsed_document: ParsedDocument) -> AnalysisResult
    Precondition: valid ParsedDocument (all IM-VAL rules pass)
    Postcondition: returns valid AnalysisResult
    Must satisfy: IV-S1 through IV-S5, IV-G1 through IV-G3

Allowed variations:
  - Different importance scoring algorithms
  - Different redundancy detection algorithms
  - Different core message identification strategies

### EP-003: OutputRenderer Protocol

  render(analysis_result: AnalysisResult, output_type: enum) -> OutputDocument
    Precondition: valid AnalysisResult + supported output_type
    Postcondition: returns valid OutputDocument
    Must satisfy: OV rules applicable to output_type

Allowed variations:
  - Different prose generation strategies for summary
  - Different list formatting for key_points
  - Different output file formats (.txt, .md, .html)

### EP-004: ValidationStrategy Protocol

  validate_output(output_doc, source_doc, analysis_result) -> ValidationResult
    Precondition: valid OutputDocument and ParsedDocument
    Postcondition: returns pass/fail/warn with rule violations
    Must check: all OV rules applicable to the output_type

Allowed variations:
  - Rule-based validation
  - ML-based semantic validation
  - Hybrid approaches


## 7. Input/Output Contracts

### Input Contract

| Artifact | Type | Format | Required | Consumed by |
|---|---|---|---|---|
| INPUT_FILE | File | .txt or .md | Yes | parse_input |

Validation rules: IP-VAL-01 through IP-VAL-04.
Content constraints: arbitrary prose, no specific structure required.

### Output Contracts

| Implementation | Artifact | Format | Produced by |
|---|---|---|---|
| summary | OUTPUT_SUMMARY | .txt | validate_output |
| key_points | OUTPUT_KEY_POINTS | .txt | validate_output |

OUTPUT_SUMMARY and OUTPUT_KEY_POINTS are mutually exclusive. Exactly one
is produced per invocation, determined by the selected implementation.

### Delivery Location

Output artifacts are delivered to:
  {job_id}/output/OUTPUT_SUMMARY-{seq}.txt
  {job_id}/output/OUTPUT_KEY_POINTS-{seq}.txt

Intermediate artifacts reside in:
  {job_id}/intermediate/{ARTIFACT_KEY}-{seq}.json


## 8. Implementation Override Model

The default implementation is defined entirely in workflow.toml. Every
step has its prompt or action assigned. Alternative implementations
provide an impl.yaml that overrides only the steps that differ.

### Default Implementation (summary)

All steps use their workflow.toml assignment:
  parse_input: parse_input_document
  analyze_structure: prompts/02_analyze_structure.txt
  score_importance: prompts/03_score_importance.txt
  identify_core_message: prompts/04_identify_core_message.txt
  render_output: render_summary
  validate_output: validate_summary
  step_completion: step_completion

### key_points Implementation

Overrides only two steps (via impls/key_points/impl.yaml):
  render_output: render_key_points (instead of render_summary)
  validate_output: validate_key_points (instead of validate_summary)

All other steps inherit from workflow.toml unchanged.


## 9. References

- BASE_COMPOSITION_STANDARD_v1.0.md -- Source architecture standard
- COMPOSITION_SPEC-01.md -- Generator composition specification
- RUNTIME_IMPL-01.md -- Runtime implementation design
- ARTIFACT_CONTRACT-01.md -- Artifact key definitions
- STEP_SEQUENCE-01.md -- Step sequence and routing
- simple_text_summarizer.md -- Original requirement document
