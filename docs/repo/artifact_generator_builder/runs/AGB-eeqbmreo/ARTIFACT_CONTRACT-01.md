---
doc_type: "artifact_contract"
identity_locked: true
generator_name: "text_summarizer"
version: "1.0.0"
source_composition_spec: "COMPOSITION_SPEC-01"
source_requirement_analysis: "REQUIREMENT_ANALYSIS-01"
source_runtime_impl: "RUNTIME_IMPL-01"
contracted_at: "2026-08-10"
---

# Artifact Contract: text_summarizer

## Input Artifacts

The following artifacts are accepted as input by the generated workflow.

### INPUT_TEXT_FILE

| Attribute | Value |
|-----------|-------|
| Artifact key | INPUT_TEXT_FILE |
| Type | file |
| Accepted formats | .txt, .md |
| Encoding | UTF-8 |
| Required | Yes |
| Description | A text document to be summarized. Accepts plain text (.txt) or Markdown (.md) files. |
| Path pattern | {job_dir}/input/{input_filename} |

Validation rules enforced on this artifact:

| Rule ID | Constraint | Reference |
|---------|------------|-----------|
| IV-001 | File must exist and be readable | REQUIREMENT_ANALYSIS V-IN-001 |
| IV-002 | File extension must be .txt or .md | REQUIREMENT_ANALYSIS V-IN-002, C-004 |
| IV-003 | File must contain non-empty text (total_word_count > 0) | REQUIREMENT_ANALYSIS V-IN-003 |
| IV-004 | File must be decodable as UTF-8 | REQUIREMENT_ANALYSIS V-IN-004 |
| IV-005 | At least one sentence must be parsed | COMPOSITION_SPEC IV-005 |
| IV-006 | Sentence ordering must be consistent | COMPOSITION_SPEC IV-006 |

Traceability: REQUIREMENT_ANALYSIS Input Specification, COMPOSITION_SPEC Input Mapping.


## Output Artifacts

The following artifacts are produced by the generated workflow.

### SUMMARY_FILE

| Attribute | Value |
|-----------|-------|
| Artifact key | SUMMARY_FILE |
| Type | file |
| Format | Plain text (extension determined by OutputRenderer) |
| Encoding | UTF-8 |
| Required | Yes |
| Description | A condensed summary of the input text, at most 20% of the original word count. |
| Path pattern | {job_dir}/output/{output_filename} |

Quality constraints enforced on this artifact:

| Rule ID | Constraint | Reference |
|---------|------------|-----------|
| OV-001 | Output word count > 0 | COMPOSITION_SPEC OV-001 |
| OV-002 | compression_ratio <= 0.20 | COMPOSITION_SPEC OV-002, C-001 |
| OV-003 | Output language matches input language | COMPOSITION_SPEC OV-003, C-002 |
| OV-004 | No content untraceable to source | COMPOSITION_SPEC OV-004, C-003 |
| OV-005 | Contains intro, main_body, conclusion blocks | COMPOSITION_SPEC OV-005 |
| OV-006 | All source_keypoint_ids reference valid L2-KP | COMPOSITION_SPEC OV-006 |
| OV-007 | All keypoint_ids in L2-CB reference valid L2-KP | COMPOSITION_SPEC OV-007 |

Traceability: REQUIREMENT_ANALYSIS Output Specification, COMPOSITION_SPEC Output Mapping, RUNTIME_IMPL Output Generation.


## Intermediate Artifacts

The following artifacts are produced during internal processing. They represent the three-layer meta schema defined in COMPOSITION_SPEC and the pipeline state described in RUNTIME_IMPL.

### Layer 1 Meta Content

#### DOC_STRUCTURE_FILE

| Attribute | Value |
|-----------|-------|
| Artifact key | DOC_STRUCTURE_FILE |
| Type | meta content file |
| Format | JSON |
| Required | No (optional diagnostic output) |
| Description | Serialized L1-DOC (DocumentStructure) containing the parsed document hierarchy: L1-SEC[], L1-PAR[], L1-SEN[]. |
| Path pattern | {job_dir}/meta/layer1/doc_structure.json |
| Produced by | Stage: Input Parsing (InputParser IP-001) |
| Consumed by | Stage T1 (Key Point Extraction) |

#### INPUT_VALIDATION_REPORT

| Attribute | Value |
|-----------|-------|
| Artifact key | INPUT_VALIDATION_REPORT |
| Type | validation report |
| Format | JSON |
| Required | No (optional diagnostic output) |
| Description | Results of input validation rules IV-001 through IV-006. |
| Path pattern | {job_dir}/meta/layer1/input_validation.json |
| Produced by | Stage: Input Parsing (validation phase) |
| Consumed by | Pipeline orchestrator (gate check) |

### Layer 2 Meta Content

#### KEYPOINT_LIST_FILE

| Attribute | Value |
|-----------|-------|
| Artifact key | KEYPOINT_LIST_FILE |
| Type | meta content file |
| Format | JSON |
| Required | No (optional diagnostic output) |
| Description | Array of L2-KP (KeyPoint) components produced by key point extraction. Each keypoint includes importance_score, category, source_sentence_ids, and consolidated_text. |
| Path pattern | {job_dir}/meta/layer2/keypoints.json |
| Produced by | Stage T1 (Key Point Extraction, TR-001) |
| Consumed by | Stage T2 (Redundancy Removal, TR-002) |

#### REDUNDANCY_MAP_FILE

| Attribute | Value |
|-----------|-------|
| Artifact key | REDUNDANCY_MAP_FILE |
| Type | meta content file |
| Format | JSON |
| Required | No (optional diagnostic output) |
| Description | Array of L2-RC (RedundancyCluster) components and the pruned L2-KP set produced by redundancy removal. |
| Path pattern | {job_dir}/meta/layer2/redundancy_map.json |
| Produced by | Stage T2 (Redundancy Removal, TR-002) |
| Consumed by | Stage T3 (Structure Assembly, TR-004) |

#### CONTENT_BLOCK_LIST_FILE

| Attribute | Value |
|-----------|-------|
| Artifact key | CONTENT_BLOCK_LIST_FILE |
| Type | meta content file |
| Format | JSON |
| Required | No (optional diagnostic output) |
| Description | Array of L2-CB (ContentBlock) components grouping keypoints by category (intro, main_body, conclusion). |
| Path pattern | {job_dir}/meta/layer2/content_blocks.json |
| Produced by | Stage T3 (Structure Assembly, TR-004) |
| Consumed by | Stage T3 (aggregate into L2-SM), Stage T4 (Output Rendering) |

#### STRUCTURE_MAP_FILE

| Attribute | Value |
|-----------|-------|
| Artifact key | STRUCTURE_MAP_FILE |
| Type | meta content file |
| Format | JSON |
| Required | No (optional diagnostic output) |
| Description | L2-SM (StructureMap) aggregate: ordered content blocks, total_keypoints, retained_keypoints, reference to source L1-DOC. |
| Path pattern | {job_dir}/meta/layer2/structure_map.json |
| Produced by | Stage T3 (Structure Assembly, TR-004) |
| Consumed by | Stage T4 (Output Rendering, TR-003) |

#### TRANSFORMATION_INVARIANT_REPORT

| Attribute | Value |
|-----------|-------|
| Artifact key | TRANSFORMATION_INVARIANT_REPORT |
| Type | validation report |
| Format | JSON |
| Required | No (optional diagnostic output) |
| Description | Results of invariant checks T1-INV-001 through T4-INV-004, recorded after each transformation stage. |
| Path pattern | {job_dir}/meta/layer2/invariant_report.json |
| Produced by | Pipeline orchestrator (post-stage invariant checks) |
| Consumed by | Pipeline orchestrator (gate check) |

### Layer 3 Meta Content

#### OUTPUT_DOC_FILE

| Attribute | Value |
|-----------|-------|
| Artifact key | OUTPUT_DOC_FILE |
| Type | meta content file |
| Format | JSON |
| Required | No (optional diagnostic output) |
| Description | L3-OD (OutputDocument) containing rendered output blocks (L3-OB[]), metadata (L3-MD), and validation results. |
| Path pattern | {job_dir}/meta/layer3/output_doc.json |
| Produced by | Stage T4 (Output Rendering, TR-003) |
| Consumed by | Output writer (writes SUMMARY_FILE), OUTPUT_VALIDATION_REPORT |

#### OUTPUT_METADATA_FILE

| Attribute | Value |
|-----------|-------|
| Artifact key | OUTPUT_METADATA_FILE |
| Type | meta content file |
| Format | JSON |
| Required | No (optional diagnostic output) |
| Description | L3-MD (OutputMetadata): source_word_count, output_word_count, compression_ratio, language, generator_version. |
| Path pattern | {job_dir}/meta/layer3/output_metadata.json |
| Produced by | Stage T4 (Output Rendering, TR-003) |
| Consumed by | OUTPUT_VALIDATION_REPORT |

#### OUTPUT_VALIDATION_REPORT

| Attribute | Value |
|-----------|-------|
| Artifact key | OUTPUT_VALIDATION_REPORT |
| Type | validation report |
| Format | JSON |
| Required | No (optional diagnostic output) |
| Description | Results of output validation rules OV-001 through OV-007. |
| Path pattern | {job_dir}/meta/layer3/output_validation.json |
| Produced by | Stage T4 (post-rendering validation) |
| Consumed by | Pipeline orchestrator (final gate check) |

### Processing Artifacts

#### RUNTIME_CONFIG_FILE

| Attribute | Value |
|-----------|-------|
| Artifact key | RUNTIME_CONFIG_FILE |
| Type | processing file |
| Format | JSON or TOML |
| Required | No (optional diagnostic output) |
| Description | Snapshot of the RuntimeConfig dataclass used for this pipeline execution. Includes all parameters: relevance_threshold, redundancy_threshold, target_compression_ratio, output_type, and implementation names. |
| Path pattern | {job_dir}/meta/runtime_config.json |
| Produced by | Pipeline orchestrator (at startup) |
| Consumed by | All pipeline stages (read-only reference) |


## Artifact Relationships

### Dependency Graph

```
INPUT_TEXT_FILE
  |
  +--> [Input Parsing]
  |      |
  |      +--> DOC_STRUCTURE_FILE (L1-DOC)
  |      +--> INPUT_VALIDATION_REPORT
  |
  v
DOC_STRUCTURE_FILE
  |
  +--> [Stage T1: Key Point Extraction]
  |      |
  |      +--> KEYPOINT_LIST_FILE (L2-KP[])
  |      +--> TRANSFORMATION_INVARIANT_REPORT (T1-INV-001, T1-INV-002)
  |
  v
KEYPOINT_LIST_FILE
  |
  +--> [Stage T2: Redundancy Removal]
  |      |
  |      +--> REDUNDANCY_MAP_FILE (L2-RC[], pruned L2-KP[])
  |      +--> TRANSFORMATION_INVARIANT_REPORT (T2-INV-001, T2-INV-002, T2-INV-003)
  |
  v
REDUNDANCY_MAP_FILE
  |
  +--> [Stage T3: Structure Assembly]
  |      |
  |      +--> CONTENT_BLOCK_LIST_FILE (L2-CB[])
  |      +--> STRUCTURE_MAP_FILE (L2-SM)
  |      +--> TRANSFORMATION_INVARIANT_REPORT (T3-INV-001, T3-INV-002, T3-INV-003)
  |
  v
STRUCTURE_MAP_FILE
  |
  +--> [Stage T4: Output Rendering]
         |
         +--> OUTPUT_DOC_FILE (L3-OD)
         +--> OUTPUT_METADATA_FILE (L3-MD)
         +--> TRANSFORMATION_INVARIANT_REPORT (T4-INV-001 to T4-INV-004)
         +--> OUTPUT_VALIDATION_REPORT
         +--> SUMMARY_FILE
```

### Processing Order Constraints

| Order | Artifact | Depends On | Constraint |
|-------|----------|------------|------------|
| 1 | RUNTIME_CONFIG_FILE | (none) | Must exist before any stage executes |
| 2 | DOC_STRUCTURE_FILE | INPUT_TEXT_FILE | Input parsing must complete |
| 3 | INPUT_VALIDATION_REPORT | DOC_STRUCTURE_FILE | Generated during parsing |
| 4 | KEYPOINT_LIST_FILE | DOC_STRUCTURE_FILE | Stage T1 requires parsed document |
| 5 | REDUNDANCY_MAP_FILE | KEYPOINT_LIST_FILE | Stage T2 requires keypoints |
| 6 | CONTENT_BLOCK_LIST_FILE | REDUNDANCY_MAP_FILE | Stage T3 requires pruned keypoints |
| 7 | STRUCTURE_MAP_FILE | CONTENT_BLOCK_LIST_FILE | Stage T3 aggregate step |
| 8 | OUTPUT_DOC_FILE | STRUCTURE_MAP_FILE | Stage T4 requires structure map |
| 9 | OUTPUT_METADATA_FILE | OUTPUT_DOC_FILE | Computed during rendering |
| 10 | OUTPUT_VALIDATION_REPORT | OUTPUT_DOC_FILE, OUTPUT_METADATA_FILE | Post-rendering checks |
| 11 | SUMMARY_FILE | OUTPUT_VALIDATION_REPORT | Written after all validation passes |
| 12 | TRANSFORMATION_INVARIANT_REPORT | Each stage | Updated incrementally after each stage |

### Required vs Optional Artifacts

| Artifact | Required | Rationale |
|----------|----------|-----------|
| INPUT_TEXT_FILE | Yes | Primary input; pipeline cannot start without it |
| SUMMARY_FILE | Yes | Primary output; pipeline purpose is to produce it |
| RUNTIME_CONFIG_FILE | No | Diagnostic; pipeline uses in-memory config |
| DOC_STRUCTURE_FILE | No | Diagnostic; intermediate in-memory structure |
| INPUT_VALIDATION_REPORT | No | Diagnostic; validation errors halt pipeline inline |
| KEYPOINT_LIST_FILE | No | Diagnostic; intermediate in-memory structure |
| REDUNDANCY_MAP_FILE | No | Diagnostic; intermediate in-memory structure |
| CONTENT_BLOCK_LIST_FILE | No | Diagnostic; intermediate in-memory structure |
| STRUCTURE_MAP_FILE | No | Diagnostic; intermediate in-memory structure |
| TRANSFORMATION_INVARIANT_REPORT | No | Diagnostic; invariant failures halt pipeline inline |
| OUTPUT_DOC_FILE | No | Diagnostic; intermediate in-memory structure |
| OUTPUT_METADATA_FILE | No | Diagnostic; intermediate in-memory structure |
| OUTPUT_VALIDATION_REPORT | No | Diagnostic; validation errors halt pipeline inline |

All intermediate artifacts (Layer 1, 2, 3 meta content and validation reports) are computed in-memory by default. They may be serialized to disk for diagnostic or debugging purposes by setting the appropriate runtime configuration flag. The only mandatory on-disk artifacts are INPUT_TEXT_FILE and SUMMARY_FILE.


## Naming Conventions

### Path Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| {job_dir} | Root directory for the current pipeline execution | runs/JOB-001 |
| {input_filename} | Original filename of the input artifact | article.md |
| {output_filename} | Output filename derived from input or configuration | article_summary.txt |
| {job_id} | Unique identifier for the pipeline run | JOB-001 |
| {seq} | Sequence number for versioned artifacts | 01 |

### Path Patterns

| Artifact | Path Pattern |
|----------|--------------|
| INPUT_TEXT_FILE | {job_dir}/input/{input_filename} |
| SUMMARY_FILE | {job_dir}/output/{output_filename} |
| DOC_STRUCTURE_FILE | {job_dir}/meta/layer1/doc_structure.json |
| INPUT_VALIDATION_REPORT | {job_dir}/meta/layer1/input_validation.json |
| KEYPOINT_LIST_FILE | {job_dir}/meta/layer2/keypoints.json |
| REDUNDANCY_MAP_FILE | {job_dir}/meta/layer2/redundancy_map.json |
| CONTENT_BLOCK_LIST_FILE | {job_dir}/meta/layer2/content_blocks.json |
| STRUCTURE_MAP_FILE | {job_dir}/meta/layer2/structure_map.json |
| TRANSFORMATION_INVARIANT_REPORT | {job_dir}/meta/layer2/invariant_report.json |
| OUTPUT_DOC_FILE | {job_dir}/meta/layer3/output_doc.json |
| OUTPUT_METADATA_FILE | {job_dir}/meta/layer3/output_metadata.json |
| OUTPUT_VALIDATION_REPORT | {job_dir}/meta/layer3/output_validation.json |
| RUNTIME_CONFIG_FILE | {job_dir}/meta/runtime_config.json |

### Naming Rules

1. All artifact keys use UPPER_SNAKE_CASE with _FILE suffix for file artifacts.
2. Meta content files use lower_snake_case filenames with .json extension.
3. Directory structure follows the three-layer hierarchy: layer1/, layer2/, layer3/.
4. Input files are placed under input/ subdirectory.
5. Output files are placed under output/ subdirectory.
6. No absolute paths in the contract; all paths are relative to {job_dir}.
7. No hardcoded job IDs or sequence numbers in path patterns.


## Self-Validation

### Input Coverage

| Requirement Source | Input Artifact | Covered | Contract Section |
|-------------------|---------------|---------|-----------------|
| REQUIREMENT_ANALYSIS Input Specification | INPUT_TEXT_FILE | Yes | Input Artifacts |
| COMPOSITION_SPEC Input Mapping | INPUT_TEXT_FILE -> L1-DOC | Yes | Input Artifacts |
| RUNTIME_IMPL Input Loading | INPUT_TEXT_FILE parsing | Yes | Input Artifacts, Intermediate Artifacts |

### Output Coverage

| Requirement Source | Output Artifact | Covered | Contract Section |
|-------------------|----------------|---------|-----------------|
| REQUIREMENT_ANALYSIS Output Specification | SUMMARY_FILE | Yes | Output Artifacts |
| COMPOSITION_SPEC Output Mapping | L3-OD -> SUMMARY_FILE | Yes | Output Artifacts, Layer 3 Meta Content |
| RUNTIME_IMPL Output Generation | SUMMARY_FILE rendering | Yes | Output Artifacts |

### Intermediate Coverage

| Requirement Source | Intermediate Artifact | Covered | Contract Section |
|-------------------|----------------------|---------|-----------------|
| COMPOSITION_SPEC Layer 1 Components | DOC_STRUCTURE_FILE | Yes | Layer 1 Meta Content |
| COMPOSITION_SPEC Layer 2 Components | KEYPOINT_LIST_FILE | Yes | Layer 2 Meta Content |
| COMPOSITION_SPEC Layer 2 Components | REDUNDANCY_MAP_FILE | Yes | Layer 2 Meta Content |
| COMPOSITION_SPEC Layer 2 Components | CONTENT_BLOCK_LIST_FILE | Yes | Layer 2 Meta Content |
| COMPOSITION_SPEC Layer 2 Components | STRUCTURE_MAP_FILE | Yes | Layer 2 Meta Content |
| COMPOSITION_SPEC Layer 3 Components | OUTPUT_DOC_FILE | Yes | Layer 3 Meta Content |
| COMPOSITION_SPEC Layer 3 Components | OUTPUT_METADATA_FILE | Yes | Layer 3 Meta Content |
| COMPOSITION_SPEC Input Validation Rules | INPUT_VALIDATION_REPORT | Yes | Layer 1 Meta Content |
| COMPOSITION_SPEC Output Validation Rules | OUTPUT_VALIDATION_REPORT | Yes | Layer 3 Meta Content |
| COMPOSITION_SPEC Invariants Summary | TRANSFORMATION_INVARIANT_REPORT | Yes | Layer 2 Meta Content |
| RUNTIME_IMPL Configuration | RUNTIME_CONFIG_FILE | Yes | Processing Artifacts |

### Relationship Completeness

| Check | Status | Evidence |
|-------|--------|----------|
| All input artifacts listed | PASS | INPUT_TEXT_FILE documented |
| All output artifacts listed | PASS | SUMMARY_FILE documented |
| All Layer 1 components mapped | PASS | DOC_STRUCTURE_FILE covers L1-DOC (contains L1-SEC, L1-PAR, L1-SEN) |
| All Layer 2 components mapped | PASS | KEYPOINT_LIST, REDUNDANCY_MAP, CONTENT_BLOCK_LIST, STRUCTURE_MAP |
| All Layer 3 components mapped | PASS | OUTPUT_DOC_FILE, OUTPUT_METADATA_FILE |
| Validation reports for all rule sets | PASS | INPUT_VALIDATION, TRANSFORMATION_INVARIANT, OUTPUT_VALIDATION |
| Processing order constraints defined | PASS | 12-step ordering table |
| Required vs optional classified | PASS | Classification table in Relationships section |
| Path patterns consistent | PASS | All use {job_dir} prefix, no absolute paths |
| No hardcoded values | PASS | All paths use placeholders |

### Extension Point Traceability

| Extension Point | Artifact Impact | Covered |
|----------------|----------------|---------|
| EP-001 (Alternative formats) | Different OutputRenderer produces different SUMMARY_FILE content | Yes (output_type parameter) |
| EP-002 (Multi-level) | Different target_compression_ratio in RUNTIME_CONFIG_FILE | Yes |
| EP-003 (Metadata enrichment) | OUTPUT_METADATA_FILE, OUTPUT_VALIDATION_REPORT | Yes |
| EP-005 (Additional artifacts) | New artifact keys could be added to this contract | Yes (contract extensible) |

### Completeness Statement

All input artifacts, output artifacts, and intermediate artifacts traceable
to the REQUIREMENT_ANALYSIS-01, COMPOSITION_SPEC-01, and RUNTIME_IMPL-01
have been documented in this contract. The two mandatory on-disk artifacts
(INPUT_TEXT_FILE, SUMMARY_FILE) are identified. All 11 intermediate
artifacts (meta content files, validation reports, processing config) are
documented as optional diagnostic outputs. Artifact relationships,
processing order, and naming conventions are fully specified.

No artifacts have been invented beyond what is traceable to the input
documents. Ambiguities from the source specifications (output file
extension, word counting method) are resolved by runtime configuration
as documented in RUNTIME_IMPL-01.


---

End of Artifact Contract.
