---
doc_type: "artifact_contract"
identity_locked: true
generator_name: "text_summarizer_ayz"
version: "1.0.0"
source_composition_spec: "COMPOSITION_SPEC-01.md"
source_runtime_impl: "RUNTIME_IMPL-01.md"
source_requirement_analysis: "REQUIREMENT_ANALYSIS-01.md"
---

# Artifact Contract -- Text Summarizer

## Input Artifacts

The following artifacts are accepted as input by the generated workflow.

| Artifact Key | Format | Required | Path Pattern | Description |
|---|---|---|---|---|
| SOURCE_TEXT_FILE | .txt or .md | Yes | {input_dir}/{source_file_name} | The source text document to be summarized. Must contain readable text content. |

**Input Artifact Details:**

- SOURCE_TEXT_FILE: Plain text or Markdown file. The caller provides an absolute or relative file path. The workflow resolves the path and reads the file content.
- Accepted formats: .txt (plain text), .md (Markdown).
- Validation: file must exist, must not be empty, must not contain binary data.
- Trace: REQUIREMENT_ANALYSIS-01.md Input Specification (SOURCE_TEXT), COMPOSITION_SPEC-01.md Input Mapping (SOURCE_TEXT_FILE), RUNTIME_IMPL-01.md Input Loading.

---

## Output Artifacts

The following artifacts are produced by the generated workflow.

| Artifact Key | Format | Path Pattern | Description |
|---|---|---|---|
| CONDENSED_SUMMARY | Markdown (.md) | {output_dir}/CONDENSED_SUMMARY-{seq}.md | Prose summary preserving source language and logical structure. |
| KEY_POINTS_LIST | Markdown (.md) | {output_dir}/KEY_POINTS_LIST-{seq}.md | Ordered list of key points extracted from source, each annotated with importance score. |

**Output Artifact Details:**

- CONDENSED_SUMMARY:
  - Format: Markdown file with YAML frontmatter (artifact_key, source_document_id, compression_ratio, language, generation_timestamp).
  - Content: Prose concatenation of summary_segment ContentBlocks ordered by position.
  - Validation: compression_ratio <= 0.20 (C-001), language matches source (C-002).
  - Trace: COMPOSITION_SPEC-01.md MAP-OM-001, RUNTIME_IMPL-01.md CONDENSED_SUMMARY Artifact.

- KEY_POINTS_LIST:
  - Format: Markdown file with YAML frontmatter (artifact_key, source_document_id, keypoint_count, generation_timestamp).
  - Content: Numbered list entries with importance_score annotation, ordered by score or document flow.
  - Validation: at least 1 key point (VAL-OM-003), all points trace to source sentences (C-003).
  - Trace: COMPOSITION_SPEC-01.md MAP-OM-002, RUNTIME_IMPL-01.md KEY_POINTS_LIST Artifact.

---

## Intermediate Artifacts

The following artifacts are produced during internal processing. They are not delivered as final output but are required for pipeline execution.

| Artifact Key | Type | Path Pattern | Description |
|---|---|---|---|
| PARSED_DOCUMENT | Meta content (Layer 1) | {work_dir}/intermediate/PARSED_DOCUMENT-{seq}.json | Structured document tree: DocumentMetadata, Section[], Paragraph[], Sentence[]. |
| KEY_POINTS_DATA | Meta content (Layer 2) | {work_dir}/intermediate/KEY_POINTS_DATA-{seq}.json | Array of KeyPoint components after extraction step. |
| REDUNDANCY_CLUSTERS | Meta content (Layer 2) | {work_dir}/intermediate/REDUNDANCY_CLUSTERS-{seq}.json | Array of RedundancyCluster components after redundancy removal step. |
| CONTENT_BLOCKS | Meta content (Layer 2) | {work_dir}/intermediate/CONTENT_BLOCKS-{seq}.json | Array of ContentBlock components after meaning preservation and structure maintenance. |
| OUTPUT_ASSEMBLY | Meta content (Layer 3) | {work_dir}/intermediate/OUTPUT_ASSEMBLY-{seq}.json | Final OutputDocument assembly with OutputMetadata and ValidationRule[]. |
| VALIDATION_REPORT | Report | {work_dir}/reports/VALIDATION_REPORT-{seq}.md | Validation results for all invariants (INV-L1, INV-L2, INV-L3) and constraints (C-001, C-002, C-003). |

**Intermediate Artifact Details:**

- PARSED_DOCUMENT:
  - Produced by: LOAD-001, PARSE-001, VAL-L1-001 (pipeline steps 1-3).
  - Contains: DocumentMetadata, Section[], Paragraph[], Sentence[].
  - Consumed by: STEP-EXT-001, STEP-RED-001, STEP-MEAN-001, STEP-STR-001, OUTPUT_ASSEMBLY.

- KEY_POINTS_DATA:
  - Produced by: STEP-EXT-001 (pipeline step 4).
  - Contains: KeyPoint[] with importance_score values.
  - Consumed by: STEP-RED-001, STEP-MEAN-001, OUTPUT_ASSEMBLY.

- REDUNDANCY_CLUSTERS:
  - Produced by: STEP-RED-001 (pipeline step 5).
  - Contains: RedundancyCluster[] with representative_ref selections.
  - Consumed by: STEP-MEAN-001.

- CONTENT_BLOCKS:
  - Produced by: STEP-MEAN-001, STEP-STR-001 (pipeline steps 6-7).
  - Contains: ContentBlock[] (summary_segment, key_point_entry, structural_bridge).
  - Consumed by: OUTPUT_ASSEMBLY, CONDENSED_SUMMARY rendering.

- OUTPUT_ASSEMBLY:
  - Produced by: VAL-OUT-001 (pipeline step 8).
  - Contains: OutputDocument with OutputMetadata, content_blocks, validation_rules.
  - Consumed by: RENDER-001 (CONDENSED_SUMMARY, KEY_POINTS_LIST).

- VALIDATION_REPORT:
  - Produced by: VAL-L1-001, VAL-OUT-001 (pipeline steps 3, 8).
  - Contains: Pass/fail results for each invariant and constraint.
  - Consumed by: Workflow runner (success/failure determination).

---

## Artifact Relationships

### Dependency Graph

```
SOURCE_TEXT_FILE
    |
    v
PARSED_DOCUMENT (Layer 1)
    |
    +--> KEY_POINTS_DATA (Layer 2, via STEP-EXT-001)
    |        |
    |        +--> REDUNDANCY_CLUSTERS (Layer 2, via STEP-RED-001)
    |        |        |
    |        |        +--> CONTENT_BLOCKS (Layer 2, via STEP-MEAN-001)
    |        |                   |
    |        |                   +--> CONTENT_BLOCKS (refined, via STEP-STR-001)
    |        |                              |
    |        +------------------------------+
    |                                       |
    +--> VALIDATION_REPORT (Layer 1 checks) |
                                            v
                                    OUTPUT_ASSEMBLY (Layer 3)
                                        |
                                        +--> CONDENSED_SUMMARY (via MAP-OM-001)
                                        |
                                        +--> KEY_POINTS_LIST (via MAP-OM-002)
                                        |
                                        +--> VALIDATION_REPORT (Layer 2/3 checks)
```

### Processing Order Constraints

| Order | From Artifact | To Artifact | Constraint |
|---|---|---|---|
| 1 | SOURCE_TEXT_FILE | PARSED_DOCUMENT | Input must be loaded before parsing can begin. |
| 2 | PARSED_DOCUMENT | KEY_POINTS_DATA | Layer 1 must be complete before extraction. |
| 3 | PARSED_DOCUMENT, KEY_POINTS_DATA | REDUNDANCY_CLUSTERS | Extraction must complete before redundancy analysis. |
| 4 | KEY_POINTS_DATA, REDUNDANCY_CLUSTERS, PARSED_DOCUMENT | CONTENT_BLOCKS | Extraction and redundancy must complete before meaning preservation. |
| 5 | CONTENT_BLOCKS, PARSED_DOCUMENT | OUTPUT_ASSEMBLY | Content blocks must be finalized before output assembly. |
| 6 | OUTPUT_ASSEMBLY | CONDENSED_SUMMARY | Output assembly must be complete before rendering. |
| 7 | OUTPUT_ASSEMBLY | KEY_POINTS_LIST | Output assembly must be complete before rendering. |
| 8 | PARSED_DOCUMENT | VALIDATION_REPORT | Layer 1 invariants checked after parsing. |
| 9 | OUTPUT_ASSEMBLY, PARSED_DOCUMENT | VALIDATION_REPORT | Layer 2/3 invariants and constraints checked after assembly. |

### Required vs Optional Artifacts

| Artifact Key | Required/Optional | Notes |
|---|---|---|
| SOURCE_TEXT_FILE | Required | Workflow cannot execute without input. |
| PARSED_DOCUMENT | Required | Core intermediate; all downstream steps depend on it. |
| KEY_POINTS_DATA | Required | Required for redundancy removal and key points output. |
| REDUNDANCY_CLUSTERS | Required | Required for meaning preservation step. |
| CONTENT_BLOCKS | Required | Required for output assembly and rendering. |
| OUTPUT_ASSEMBLY | Required | Required for final output rendering. |
| CONDENSED_SUMMARY | Required | Primary output artifact. |
| KEY_POINTS_LIST | Required | Primary output artifact. |
| VALIDATION_REPORT | Required | Must pass for outputs to be delivered. |

---

## Naming Conventions

### Path Variable Definitions

| Variable | Description | Example |
|---|---|---|
| {job_id} | Unique job identifier for this workflow run | AGB-43hev804 |
| {seq} | Zero-padded sequence number for artifact versioning | 01, 02, 03 |
| {input_dir} | Directory containing input artifacts | jobs/{job_id}/input |
| {output_dir} | Directory for final output artifacts | jobs/{job_id}/output |
| {work_dir} | Directory for intermediate processing artifacts | jobs/{job_id}/work |
| {source_file_name} | Original filename of the source text file | document.md |

### Path Pattern Templates

| Artifact Key | Path Template |
|---|---|
| SOURCE_TEXT_FILE | jobs/{job_id}/input/{source_file_name} |
| CONDENSED_SUMMARY | jobs/{job_id}/output/CONDENSED_SUMMARY-{seq}.md |
| KEY_POINTS_LIST | jobs/{job_id}/output/KEY_POINTS_LIST-{seq}.md |
| PARSED_DOCUMENT | jobs/{job_id}/work/intermediate/PARSED_DOCUMENT-{seq}.json |
| KEY_POINTS_DATA | jobs/{job_id}/work/intermediate/KEY_POINTS_DATA-{seq}.json |
| REDUNDANCY_CLUSTERS | jobs/{job_id}/work/intermediate/REDUNDANCY_CLUSTERS-{seq}.json |
| CONTENT_BLOCKS | jobs/{job_id}/work/intermediate/CONTENT_BLOCKS-{seq}.json |
| OUTPUT_ASSEMBLY | jobs/{job_id}/work/intermediate/OUTPUT_ASSEMBLY-{seq}.json |
| VALIDATION_REPORT | jobs/{job_id}/work/reports/VALIDATION_REPORT-{seq}.md |

### Naming Rules

1. All artifact file names use UPPER_SNAKE_CASE for the artifact key portion.
2. Sequence numbers ({seq}) are zero-padded to two digits (01, 02, ...).
3. Output artifacts use .md extension (Markdown with YAML frontmatter).
4. Intermediate artifacts use .json extension (structured meta content).
5. Validation reports use .md extension (human-readable report format).
6. No absolute paths shall appear in artifact path patterns.
7. Job-specific isolation is enforced via {job_id} directory nesting.

---

## Self-Validation

| Check | Status | Notes |
|---|---|---|
| All input artifacts from requirement listed | PASS | SOURCE_TEXT_FILE from REQUIREMENT_ANALYSIS-01.md SOURCE_TEXT, COMPOSITION_SPEC-01.md Input Mapping, RUNTIME_IMPL-01.md Input Loading. |
| All output artifacts from requirement listed | PASS | CONDENSED_SUMMARY and KEY_POINTS_LIST from REQUIREMENT_ANALYSIS-01.md Output Specification, COMPOSITION_SPEC-01.md Output Mapping, RUNTIME_IMPL-01.md Output Generation. |
| All intermediate artifacts covered | PASS | PARSED_DOCUMENT, KEY_POINTS_DATA, REDUNDANCY_CLUSTERS, CONTENT_BLOCKS, OUTPUT_ASSEMBLY, VALIDATION_REPORT from COMPOSITION_SPEC-01.md Meta Schema and RUNTIME_IMPL-01.md Data Flow. |
| Path patterns consistent | PASS | All paths use {job_id} and {seq} variables; no absolute paths or hardcoded values. |
| Relationships clear | PASS | Dependency graph and processing order constraints defined for all artifacts. |
| Required vs optional declared | PASS | All artifacts marked as Required; no optional artifacts in current scope. |
| Naming conventions defined | PASS | UPPER_SNAKE_CASE keys, zero-padded sequence, extension conventions documented. |
| Traceability to source artifacts | PASS | Each artifact traces to REQUIREMENT_ANALYSIS-01.md, COMPOSITION_SPEC-01.md, or RUNTIME_IMPL-01.md. |
| No invented scope | PASS | All artifacts trace to input documents. No features added beyond declared scope. |
| ASCII-only output | PASS | No em-dashes, curly quotes, or Unicode characters used. |
| YAML frontmatter correct | PASS | doc_type: "artifact_contract", identity_locked: true present. |
