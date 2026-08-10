---
doc_type: "artifact_contract"
identity_locked: true
generator_name: "text_summarizer"
version: "1.0.0"
source_runtime_impl: "RUNTIME_IMPL-001"
source_composition_spec: "COMPOSITION_SPEC-001"
source_requirement_analysis: "REQUIREMENT_ANALYSIS-001"
defined_at: "2026-08-10"
---

# Artifact Contract

## 1. Input Artifacts

Artifacts accepted by the generated text_summarizer workflow.

| Artifact Key | Type | Expected Format | Path Pattern | Required | Description |
|---|---|---|---|---|---|
| INPUT_TEXT_FILE | file | Plain text (.txt) or Markdown (.md), UTF-8 encoded | {input_dir}/{job_id}/{input_filename} | Yes | The source document to be summarized. Contains natural language prose. May include YAML frontmatter if .md format. |

### 1.1 Input Artifact Details

INPUT_TEXT_FILE
- Source: External user-provided input
- Validation rules: INV-001 (exists/readable), INV-002 (extension .txt or .md), INV-003 (non-empty content), INV-004 (natural language), INV-005 (at least one section), INV-006 (at least one sentence)
- Format: FMT-001 (input format requirement)
- Trace: REQUIREMENT_ANALYSIS Input Artifacts table; COMPOSITION_SPEC Section 3
- Constraints: No minimum or maximum length (ASM-001, ASM-002)

---

## 2. Output Artifacts

Artifacts produced by the generated text_summarizer workflow.

| Artifact Key | Type | Expected Format | Path Pattern | Required | Description |
|---|---|---|---|---|---|
| SUMMARY_FILE | file | Plain text or Markdown matching input format | {output_dir}/{job_id}/{output_filename} | Yes | The condensed summary document. Must satisfy CON-001, CON-002, CON-003. |

### 2.1 Output Artifact Details

SUMMARY_FILE
- Produced by: Stage 10 (TR-010, OutputRenderer)
- Format: Matches source_format of DocumentMeta (ASM-005: txt in -> txt out, md in -> md out)
- Quality requirements:
  - SUMMARY-QR-001: word count <= 20% of original (CON-001)
  - SUMMARY-QR-002: same language as input (CON-002)
  - SUMMARY-QR-003: no new information (CON-003)
  - SUMMARY-QR-004: captures core message (INV-T-003)
  - SUMMARY-QR-005: maintains intro -> main points -> conclusion structure (FMT-003, INV-T-008)
- Validation rules: OV-001 (exists/readable), OV-002 (ratio <= 0.20), OV-003 (language match), OV-004 (no hallucination), OV-005 (structural elements present), OV-006 (coherent and readable)
- Trace: REQUIREMENT_ANALYSIS Output Artifacts table; COMPOSITION_SPEC Section 4

---

## 3. Intermediate Artifacts

Internal processing artifacts produced during pipeline execution. These are not part of the external artifact contract but are generated as part of the transformation pipeline.

### 3.1 Layer 1 Content Components (Stages 1-2)

Produced by: Stage 1 (InputParser), Stage 2 (SegmentValidator)

| Component Type | component_id Pattern | Count | Description |
|---|---|---|---|
| DocumentMeta | doc-meta-001 | 1 | Top-level metadata: source_format, source_language, original_word_count, section_count, encoding, has_frontmatter |
| Section | sec-{index} | 1..N | Logical section with heading, position, paragraph_ids, word_count |
| Paragraph | para-{section_index}-{para_index} | 1..N per section | Paragraph with parent_section_id, raw_text, sentence_ids, word_count |
| Sentence | s-{section}-{para}-{sent} | 1..N per paragraph | Sentence with parent_paragraph_id, raw_text, word_count, is_heading, is_list_item |

Validation rules: VR-001 through VR-007
Invariants: INV-T-001, INV-T-002
Trace: COMPOSITION_SPEC Section 2.1

### 3.2 Layer 2 Composition Components (Stages 3-7)

Produced by: Stages 3-7 (ImportanceScorer, RedundancyDetector, MeaningPreserver, CompressionSelector, StructureMaintainer)

| Component Type | component_id Pattern | Count | Description |
|---|---|---|---|
| KeyPoint | kp-{index} | 1..N | Key point with source_sentence_ids, extracted_text, importance_score, is_core_message, structural_role |
| RedundancyCluster | rc-{index} | 0..N | Cluster of overlapping key points with representative_key_point_id, similarity_score |
| SummaryBlock | sb-{index} | 1..N | Summary block with structural_role, source_key_point_ids, content_text, word_count, position |

Validation rules: VR-008, VR-009, VR-012
Invariants: INV-T-003 through INV-T-008
Trace: COMPOSITION_SPEC Section 2.2

### 3.3 Layer 3 Output Components (Stages 8-10)

Produced by: Stages 8-10 (ValidationEngine, OutputRenderer)

| Component Type | component_id Pattern | Count | Description |
|---|---|---|---|
| SummaryDocument | summary-doc-001 | 1 | Complete summary with output_format, target_language, compression_ratio, block references, generation_timestamp |
| ValidationRecord | valrec-{index} | 2+ | Validation results for CON-001 and CON-002 with constraint_id, passed, measured_value, threshold_value |

Validation rules: VR-010, VR-011
Invariants: INV-T-009, INV-T-010, INV-T-011
Trace: COMPOSITION_SPEC Section 2.3

### 3.4 Pipeline Configuration

| Artifact Key | Type | Path Pattern | Description |
|---|---|---|---|
| RUNTIME_CONFIG | dataclass (in-memory) | N/A | RuntimeConfig with input_path, output_path, target_compression_ratio, importance_threshold, redundancy_similarity_threshold, max_recovery_attempts, output_format_override, scorer_impl, detector_impl, selector_impl, renderer_impl |

Trace: RUNTIME_IMPL Section 5

### 3.5 Pipeline Orchestration Output

| Artifact Key | Type | Path Pattern | Description |
|---|---|---|---|
| PIPELINE_RESULT | dataclass (in-memory) | N/A | Contains all generated components from all 10 stages. Produced by PipelineRunner. |

Trace: RUNTIME_IMPL Section 1.4

---

## 4. Artifact Relationships

### 4.1 Dependency Graph

```
INPUT_TEXT_FILE (external input)
  |
  v
[Stage 1: InputParser]
  -> DocumentMeta, Section[], Paragraph[], Sentence[]   (Layer 1)
  |
  v
[Stage 2: SegmentValidator]
  -> Validated Layer 1 hierarchy                        (Layer 1)
  |
  v
[Stage 3: ImportanceScorer]
  -> KeyPoint[] with importance_score                   (Layer 2)
  |
  v
[Stage 4: RedundancyDetector]
  -> RedundancyCluster[], deduplicated KeyPoint[]       (Layer 2)
  |
  v
[Stage 5: MeaningPreserver]
  -> Validated KeyPoint set                             (Layer 2)
  |
  v
[Stage 6: CompressionSelector]
  -> Selected KeyPoint[]                                (Layer 2)
  |
  v
[Stage 7: StructureMaintainer]
  -> SummaryBlock[]                                     (Layer 2)
  |
  v
[Stage 8: ValidationEngine (Language)]
  -> ValidationRecord[] for CON-002                     (Layer 3)
  |
  v
[Stage 9: ValidationEngine (Length)]
  -> ValidationRecord[] for CON-001                     (Layer 3)
  |
  v
[Stage 10: OutputRenderer]
  -> SummaryDocument + SUMMARY_FILE                     (Layer 3)
```

### 4.2 Processing Order Constraints

| Constraint | Description | Trace |
|---|---|---|
| Stage 1 before Stage 2 | Layer 1 components must exist before hierarchy validation | INV-T-001, INV-T-002 |
| Stage 2 before Stage 3 | Validated hierarchy required before importance scoring | TR-002 -> TR-003 |
| Stage 3 before Stage 4 | KeyPoints must exist before redundancy detection | TR-003 -> TR-004 |
| Stage 4 before Stage 5 | Deduplicated set required before meaning preservation | TR-004 -> TR-005 |
| Stage 5 before Stage 6 | Validated KeyPoints required before compression | TR-005 -> TR-006 |
| Stage 6 before Stage 7 | Selected KeyPoints required before structure assembly | TR-006 -> TR-007 |
| Stage 7 before Stage 8 | SummaryBlocks must exist before language validation | TR-007 -> TR-008 |
| Stage 8 before Stage 9 | Language validation must pass before length validation | TR-008 -> TR-009 |
| Stage 9 before Stage 10 | Length validation must pass before output rendering | TR-009 -> TR-010 |
| Stage 9 failure recovery | If compression_ratio > 0.20, return to Stage 6 (max 3 attempts) | RUNTIME_IMPL Section 3.4 |

### 4.3 Required vs Optional Artifacts

| Artifact Key | Required/Optional | Condition |
|---|---|---|
| INPUT_TEXT_FILE | Required | Always required to begin pipeline |
| DocumentMeta | Required | Always produced by Stage 1 |
| Section[] | Required | At least 1 section required (INV-005) |
| Paragraph[] | Required | At least 1 paragraph per section |
| Sentence[] | Required | At least 1 sentence per paragraph |
| KeyPoint[] | Required | At least 1 per structural_role (INV-T-004) |
| RedundancyCluster[] | Optional | May be 0 if no redundancy detected |
| SummaryBlock[] | Required | At least 1 per structural_role |
| ValidationRecord[] | Required | At least 2 records (CON-001, CON-002) |
| SummaryDocument | Required | Always produced by Stage 10 |
| SUMMARY_FILE | Required | Always written by Stage 10 |
| RUNTIME_CONFIG | Required | Configuration for pipeline execution |
| PIPELINE_RESULT | Required | Orchestration output |

---

## 5. Naming Conventions

### 5.1 Path Placeholders

| Placeholder | Description | Example |
|---|---|---|
| {job_id} | Unique identifier for the current pipeline run | AGB-t0jk63sn |
| {seq} | Sequence number for document versioning | 001 |
| {input_dir} | Base directory for input files | data/inputs |
| {output_dir} | Base directory for output files | data/outputs |
| {input_filename} | User-provided input file name | article.md |
| {output_filename} | Generated output file name | article_summary.md |
| {index} | Numeric index for component identification | 001, 002, ... |
| {section_index} | Section ordinal position | 1, 2, 3 |
| {para_index} | Paragraph ordinal within section | 1, 2, 3 |
| {sent} | Sentence ordinal within paragraph | 1, 2, 3 |

### 5.2 Component ID Patterns

| Component Type | ID Pattern | Example |
|---|---|---|
| DocumentMeta | doc-meta-001 | doc-meta-001 |
| Section | sec-{index} | sec-001, sec-002 |
| Paragraph | para-{section_index}-{para_index} | para-001-001, para-002-003 |
| Sentence | s-{section}-{para}-{sent} | s-001-001-001, s-002-003-005 |
| KeyPoint | kp-{index} | kp-001, kp-002 |
| RedundancyCluster | rc-{index} | rc-001, rc-002 |
| SummaryBlock | sb-{index} | sb-001, sb-002 |
| SummaryDocument | summary-doc-001 | summary-doc-001 |
| ValidationRecord | valrec-{index} | valrec-001, valrec-002 |

### 5.3 Artifact Key Naming Rules

- All artifact keys use UPPER_SNAKE_CASE
- All artifact keys end with _FILE for file-type artifacts
- Intermediate dataclass artifacts use descriptive names (RUNTIME_CONFIG, PIPELINE_RESULT)
- No absolute paths are used in the contract
- No hardcoded job IDs or sequence numbers in patterns

---

## 6. Self-Validation

### 6.1 Input Artifact Coverage

| Requirement Source | Artifact | Covered | Contract Section |
|---|---|---|---|
| REQUIREMENT_ANALYSIS Input Artifacts table | INPUT_TEXT_FILE | PASS | Section 1 |
| COMPOSITION_SPEC Section 3 (Input Mapping) | INPUT_TEXT_FILE | PASS | Section 1 |
| RUNTIME_IMPL Section 2 (Input Loading) | INPUT_TEXT_FILE | PASS | Section 1 |

### 6.2 Output Artifact Coverage

| Requirement Source | Artifact | Covered | Contract Section |
|---|---|---|---|
| REQUIREMENT_ANALYSIS Output Artifacts table | SUMMARY_FILE | PASS | Section 2 |
| COMPOSITION_SPEC Section 4 (Output Mapping) | SUMMARY_FILE | PASS | Section 2 |
| RUNTIME_IMPL Section 4 (Output Generation) | SUMMARY_FILE | PASS | Section 2 |

### 6.3 Intermediate Artifact Coverage

| Requirement Source | Artifact(s) | Covered | Contract Section |
|---|---|---|---|
| COMPOSITION_SPEC Section 2.1 (Layer 1) | DocumentMeta, Section, Paragraph, Sentence | PASS | Section 3.1 |
| COMPOSITION_SPEC Section 2.2 (Layer 2) | KeyPoint, RedundancyCluster, SummaryBlock | PASS | Section 3.2 |
| COMPOSITION_SPEC Section 2.3 (Layer 3) | SummaryDocument, ValidationRecord | PASS | Section 3.3 |
| RUNTIME_IMPL Section 5 (Configuration) | RuntimeConfig | PASS | Section 3.4 |
| RUNTIME_IMPL Section 1.4 (Orchestration) | PipelineResult | PASS | Section 3.5 |

### 6.4 Relationship Coverage

| Requirement Source | Dependency | Covered | Contract Section |
|---|---|---|---|
| REQUIREMENT_ANALYSIS Dependency Trace | INPUT_TEXT_FILE -> TR-001..TR-010 -> SUMMARY_FILE | PASS | Section 4.1 |
| COMPOSITION_SPEC Section 5.2 (Stages 1-10) | Stage ordering and invariants | PASS | Section 4.2 |
| RUNTIME_IMPL Section 3.4 (Error Handling) | Stage 9 recovery to Stage 6 | PASS | Section 4.2 |

### 6.5 Naming Convention Coverage

| Check | Status | Evidence |
|---|---|---|
| Uses {job_id} placeholder | PASS | Section 5.1 |
| Uses {seq} placeholder | PASS | Section 5.1 |
| Uses {index} patterns for components | PASS | Section 5.2 |
| No absolute paths | PASS | All paths use placeholders |
| No hardcoded job IDs | PASS | All examples use placeholder descriptions |
| ASCII-only | PASS | No em-dashes, curly quotes, or Unicode |
| Consistent naming patterns | PASS | UPPER_SNAKE_CASE for keys, hyphenated for component IDs |

### 6.6 Constraint Traceability

| Constraint | Input | Output | Intermediate | Contract Coverage |
|---|---|---|---|---|
| CON-001 (20% max compression) | original_word_count from INPUT_TEXT_FILE | SUMMARY_FILE word count check (OV-002) | INV-T-007, INV-T-010 | Sections 1, 2, 3.2, 3.3 |
| CON-002 (same language) | source_language from INPUT_TEXT_FILE | target_language in SUMMARY_FILE | INV-T-009, ValidationRecord | Sections 1, 2, 3.2, 3.3 |
| CON-003 (no new information) | Content from INPUT_TEXT_FILE | Structural enforcement in SUMMARY_FILE | KeyPoint extraction from source only | Sections 1, 2, 3.2 |
| FMT-001 (input format) | Extension check on INPUT_TEXT_FILE | N/A | DocumentMeta.source_format | Sections 1, 3.1 |
| FMT-002 (output format) | N/A | SUMMARY_FILE format check (OV-001) | SummaryDocument.output_format | Sections 2, 3.3 |
| FMT-003 (logical flow) | N/A | SUMMARY_FILE structure check (OV-005) | INV-T-008, SummaryBlock ordering | Sections 2, 3.2 |

### 6.7 Completeness Summary

| Check | Status | Notes |
|---|---|---|
| All input artifacts from requirement listed | PASS | 1 input: INPUT_TEXT_FILE |
| All output artifacts from requirement listed | PASS | 1 output: SUMMARY_FILE |
| All intermediate artifacts from composition spec listed | PASS | 9 component types across 3 layers + config + result |
| Path patterns consistent | PASS | Placeholders used throughout |
| Relationships clear | PASS | Linear pipeline with recovery loop documented |
| No scope invention | PASS | All content traceable to input documents |
| ASCII-only content | PASS | No em-dashes, curly quotes, or Unicode |
| YAML frontmatter correct | PASS | doc_type: artifact_contract, identity_locked: true |

---

End of Artifact Contract
