---
doc_type: "artifact_contract"
identity_locked: true
source_codename: "text_summarizer_ayz"
source_version: "1.0.0"
standard_reference: "BASE_COMPOSITION_STANDARD_v1.0.md"
requirement_analysis: "REQUIREMENT_ANALYSIS-01.md"
composition_spec: "COMPOSITION_SPEC-01.md"
runtime_impl: "RUNTIME_IMPL-01.md"
contract_date: "2026-08-10"
---

# Artifact Contract: Text Summarizer Generator

## Scope

This document defines the complete artifact contract for the text_summarizer_ayz
generator (v1.0.0). It specifies every artifact consumed, produced, and generated
internally by the workflow, including types, path patterns, relationships, and
naming conventions.

This contract is traceable to:
- REQUIREMENT_ANALYSIS-01.md (input/output requirements)
- COMPOSITION_SPEC-01.md (meta schema and transformation rules)
- RUNTIME_IMPL-01.md (runtime architecture and pipeline stages)

---

## Input Artifacts

These are the artifacts that the generated workflow accepts from upstream or
from the operator at invocation time.

### IN-AC-001: SOURCE_TEXT

| Field | Value |
|---|---|
| Artifact Key | SOURCE_TEXT |
| Description | The source text document to be summarized |
| File Type | .txt or .md |
| Format | UTF-8 encoded plain text or Markdown |
| Required | Yes |
| Path Pattern | {input_dir}/SOURCE_TEXT.{ext} |
| Traceability | REQUIREMENT_ANALYSIS IN-001, COMPOSITION_SPEC Input Artifact |

Validation rules at intake:
- V-MAP-IN-001: File must exist and be readable.
- V-MAP-IN-002: File extension must be .txt or .md.
- V-MAP-IN-003: Content must contain at least one sentence.
- V-MAP-IN-004: Content must be in a detectable natural language.
- V-MAP-IN-007: Word count must be greater than zero.

### IN-AC-002: RUNTIME_CONFIG

| Field | Value |
|---|---|
| Artifact Key | RUNTIME_CONFIG |
| Description | Optional configuration file for runtime parameters |
| File Type | .json or .yaml |
| Format | Key-value pairs for tuning pipeline behavior |
| Required | No |
| Path Pattern | {input_dir}/RUNTIME_CONFIG.{ext} |
| Traceability | RUNTIME_IMPL Configuration Design section |

Supported configuration parameters:
- compression_ratio (float, default 0.20)
- keypoint_threshold (float, default 0.30)
- similarity_threshold (float, default 0.60)
- output_format (string, default "md")
- output_types (list, default ["condensed_summary", "key_points_list"])
- scoring_method (string, default "positional_tfidf")
- clustering_method (string, default "keyword_overlap")
- language_detection (string, default "auto")

Configuration source priority (highest first): command-line arguments,
environment variables, configuration file, default values.

---

## Output Artifacts

These are the artifacts that the generated workflow produces as final deliverables.

### OUT-AC-001: CONDENSED_SUMMARY

| Field | Value |
|---|---|
| Artifact Key | CONDENSED_SUMMARY |
| Description | Prose summary preserving introduction-main-conclusion structure |
| File Type | .md (default) or .txt |
| Format | Continuous prose paragraphs |
| Required | Yes (when output_types includes "condensed_summary") |
| Path Pattern | {output_dir}/CONDENSED_SUMMARY.{ext} |
| Traceability | REQUIREMENT_ANALYSIS OUT-001, COMPOSITION_SPEC MAP-OUT-001 |

Content constraints:
- Word count must not exceed 20% of source word count (GI-003, VR-001).
- Language must match source language (GI-001, VR-002).
- Must preserve logical structure: introduction, main points, conclusion (GI-005, VR-003).
- Must not introduce new information beyond source (GI-002, VR-004).
- All content traces to source TextUnits (INV-S4-005).

### OUT-AC-002: KEY_POINTS_LIST

| Field | Value |
|---|---|
| Artifact Key | KEY_POINTS_LIST |
| Description | Ordered list of extracted key points with importance scores |
| File Type | .md (default) or .txt |
| Format | Numbered list with importance score per item |
| Required | Yes (when output_types includes "key_points_list") |
| Path Pattern | {output_dir}/KEY_POINTS_LIST.{ext} |
| Traceability | REQUIREMENT_ANALYSIS OUT-002, COMPOSITION_SPEC MAP-OUT-002 |

Content constraints:
- Each key point must include an importance score (VR-005).
- Items must be ordered by descending importance score (INV-S3-003).
- Each key point must trace to a source TextUnit (VR-007).
- Language must match source language (VR-006).
- Importance scores must be in [0.0, 1.0] range (INV-S1-002).

---

## Intermediate Artifacts

These are internal processing artifacts produced during the 6-stage pipeline.
They are used for traceability, debugging, and validation. They are not part of
the final deliverable set.

### INT-AC-001: PARSED_DOCUMENT

| Field | Value |
|---|---|
| Artifact Key | PARSED_DOCUMENT |
| Description | Layer 1 structured representation of the source document |
| File Type | .json |
| Stage | Stage 0 (Input Loading) |
| Path Pattern | {work_dir}/intermediate/PARSED_DOCUMENT-{seq}.json |
| Traceability | COMPOSITION_SPEC COMP-L1-001, COMP-L1-002, COMP-L1-003 |

Contains: SourceDocument with all StructuralSection and TextUnit components.
This is the output of the input_loader module.

### INT-AC-002: IMPORTANCE_ANALYSIS

| Field | Value |
|---|---|
| Artifact Key | IMPORTANCE_ANALYSIS |
| Description | Layer 2 importance scoring results |
| File Type | .json |
| Stage | Stage 1 (Importance Scoring) |
| Path Pattern | {work_dir}/intermediate/IMPORTANCE_ANALYSIS-{seq}.json |
| Traceability | COMPOSITION_SPEC COMP-L2-001, COMP-L2-002 |

Contains: ImportanceAnalysis with ScoredUnit array. Each TextUnit has an
assigned importance_score in [0.0, 1.0] and a rank.

Invariants enforced: INV-S1-001 through INV-S1-004.

### INT-AC-003: REDUNDANCY_CLUSTERS

| Field | Value |
|---|---|
| Artifact Key | REDUNDANCY_CLUSTERS |
| Description | Layer 2 redundancy analysis results |
| File Type | .json |
| Stage | Stage 2 (Redundancy Analysis) |
| Path Pattern | {work_dir}/intermediate/REDUNDANCY_CLUSTERS-{seq}.json |
| Traceability | COMPOSITION_SPEC COMP-L2-003 |

Contains: Array of RedundancyCluster objects, each with a representative
unit and constituent unit references.

Invariants enforced: INV-S2-001 through INV-S2-004.

### INT-AC-004: KEY_POINTS_RAW

| Field | Value |
|---|---|
| Artifact Key | KEY_POINTS_RAW |
| Description | Layer 2 extracted key points before rendering |
| File Type | .json |
| Stage | Stage 3 (Key Point Extraction) |
| Path Pattern | {work_dir}/intermediate/KEY_POINTS_RAW-{seq}.json |
| Traceability | COMPOSITION_SPEC COMP-L2-004 |

Contains: Array of KeyPoint objects, each referencing a source TextUnit
with inherited importance score and section reference.

Invariants enforced: INV-S3-001 through INV-S3-004.

### INT-AC-005: SUMMARY_BLOCKS

| Field | Value |
|---|---|
| Artifact Key | SUMMARY_BLOCKS |
| Description | Layer 2 summary blocks composed per structural section |
| File Type | .json |
| Stage | Stage 4 (Summary Block Composition) |
| Path Pattern | {work_dir}/intermediate/SUMMARY_BLOCKS-{seq}.json |
| Traceability | COMPOSITION_SPEC COMP-L2-005 |

Contains: Array of SummaryBlock objects, one per StructuralSection.
Each block has content, word count, and source unit references.

Invariants enforced: INV-S4-001 through INV-S4-005.

### INT-AC-006: OUTPUT_DOCUMENTS

| Field | Value |
|---|---|
| Artifact Key | OUTPUT_DOCUMENTS |
| Description | Layer 3 assembled output documents before validation |
| File Type | .json |
| Stage | Stage 5 (Output Assembly) |
| Path Pattern | {work_dir}/intermediate/OUTPUT_DOCUMENTS-{seq}.json |
| Traceability | COMPOSITION_SPEC COMP-L3-001, COMP-L3-002, COMP-L3-003 |

Contains: Array of OutputDocument objects with their OutputBlocks and
assigned ValidationRules.

Invariants enforced: INV-S5-001 through INV-S5-004.

---

## Validation Artifacts

These are reports produced by the validation stage and error handling subsystems.

### VAL-AC-001: VALIDATION_REPORT

| Field | Value |
|---|---|
| Artifact Key | VALIDATION_REPORT |
| Description | Results of Stage 6 output validation |
| File Type | .json |
| Stage | Stage 6 (Output Validation) |
| Path Pattern | {work_dir}/reports/VALIDATION_REPORT-{seq}.json |
| Traceability | COMPOSITION_SPEC INV-S6-001, INV-S6-002 |

Contains: For each OutputDocument, the result of evaluating every assigned
ValidationRule. Records which rules passed or failed.

Rules evaluated:
- VR-001: compression_ratio <= 0.20 (condensed_summary)
- VR-002: language match (condensed_summary, key_points_list)
- VR-003: structure preservation (condensed_summary)
- VR-004: no new information (condensed_summary, key_points_list)
- VR-005: importance scores present (key_points_list)
- VR-006: language match (key_points_list)
- VR-007: no new information (key_points_list)

### VAL-AC-002: ERROR_REPORT

| Field | Value |
|---|---|
| Artifact Key | ERROR_REPORT |
| Description | Structured error report if the pipeline fails |
| File Type | .json |
| Stage | Any (on failure) |
| Path Pattern | {work_dir}/reports/ERROR_REPORT-{seq}.json |
| Traceability | RUNTIME_IMPL Error Handling Strategy section |

Contains:
- Error class name
- Stage ID where error occurred
- Specific invariant or rule ID violated
- Context data (affected TextUnit, OutputDocument, etc.)
- Human-readable description

Error types covered:
- InputValidationError (V-MAP-IN-001 through V-MAP-IN-005, V-MAP-IN-007)
- InvariantViolationError (any INV-S* or GI-* violation)
- ValidationFailureError (any VR-* rule failure)
- ConfigurationError (invalid configuration values)
- UnsupportedFormatError (unknown input format or output type)

### VAL-AC-003: EXECUTION_LOG

| Field | Value |
|---|---|
| Artifact Key | EXECUTION_LOG |
| Description | Runtime execution log with stage timings and events |
| File Type | .log |
| Stage | All stages |
| Path Pattern | {work_dir}/logs/EXECUTION_LOG-{seq}.log |
| Traceability | RUNTIME_IMPL Error Reporting section |

Contains: Timestamped entries for stage entry/exit, skipped TextUnits
(V-MAP-IN-006 recovery), configuration values used, and component counts.

---

## Artifact Relationships

This section defines the dependency graph and processing order constraints.

### Dependency Graph

```
SOURCE_TEXT (IN-AC-001)
    |
    v
PARSED_DOCUMENT (INT-AC-001)
    |
    v
IMPORTANCE_ANALYSIS (INT-AC-002)
    |
    v
REDUNDANCY_CLUSTERS (INT-AC-003)
    |
    +---> KEY_POINTS_RAW (INT-AC-004) --+
    |                                    |
    +---> SUMMARY_BLOCKS (INT-AC-005) --+---> OUTPUT_DOCUMENTS (INT-AC-006)
                                              |
                                              v
                                     +--------+--------+
                                     |                 |
                                     v                 v
                            CONDENSED_SUMMARY    KEY_POINTS_LIST
                              (OUT-AC-001)        (OUT-AC-002)
                                     |                 |
                                     +--------+--------+
                                              |
                                              v
                                    VALIDATION_REPORT
                                      (VAL-AC-001)
```

### Processing Order Constraints

| Constraint ID | Description |
|---|---|
| ORD-001 | PARSED_DOCUMENT must be produced before IMPORTANCE_ANALYSIS. |
| ORD-002 | IMPORTANCE_ANALYSIS must be produced before REDUNDANCY_CLUSTERS. |
| ORD-003 | REDUNDANCY_CLUSTERS must be produced before KEY_POINTS_RAW. |
| ORD-004 | REDUNDANCY_CLUSTERS must be produced before SUMMARY_BLOCKS. |
| ORD-005 | KEY_POINTS_RAW must be produced before OUTPUT_DOCUMENTS. |
| ORD-006 | SUMMARY_BLOCKS must be produced before OUTPUT_DOCUMENTS. |
| ORD-007 | OUTPUT_DOCUMENTS must be produced before CONDENSED_SUMMARY. |
| ORD-008 | OUTPUT_DOCUMENTS must be produced before KEY_POINTS_LIST. |
| ORD-009 | VALIDATION_REPORT is produced after all output artifacts are finalized. |
| ORD-010 | RUNTIME_CONFIG, if present, must be loaded before Stage 0 begins. |

### Required vs Optional

| Artifact | Required? | Condition |
|---|---|---|
| SOURCE_TEXT | Yes | Always required. |
| RUNTIME_CONFIG | No | Optional. Defaults are used if absent. |
| CONDENSED_SUMMARY | Conditional | Required if output_types includes "condensed_summary". |
| KEY_POINTS_LIST | Conditional | Required if output_types includes "key_points_list". |
| PARSED_DOCUMENT | Yes | Always produced in Stage 0. |
| IMPORTANCE_ANALYSIS | Yes | Always produced in Stage 1. |
| REDUNDANCY_CLUSTERS | Yes | Always produced in Stage 2. |
| KEY_POINTS_RAW | Yes | Always produced in Stage 3. |
| SUMMARY_BLOCKS | Yes | Always produced in Stage 4. |
| OUTPUT_DOCUMENTS | Yes | Always produced in Stage 5. |
| VALIDATION_REPORT | Yes | Always produced in Stage 6. |
| ERROR_REPORT | Conditional | Produced only if the pipeline fails. |
| EXECUTION_LOG | Yes | Always produced during execution. |

---

## Naming Conventions

### Path Variables

| Variable | Description | Example |
|---|---|---|
| {job_id} | Unique identifier for the workflow run | AGB-1p3xktl0 |
| {seq} | Zero-padded sequence number for versioning | 01, 02, 03 |
| {input_dir} | Directory containing input artifacts | {job_dir}/input |
| {output_dir} | Directory for final output artifacts | {job_dir}/output |
| {work_dir} | Directory for intermediate and report artifacts | {job_dir}/work |
| {ext} | File extension based on format | txt, md, json |

### Path Patterns Summary

| Artifact | Path Pattern |
|---|---|
| SOURCE_TEXT | {input_dir}/SOURCE_TEXT.{ext} |
| RUNTIME_CONFIG | {input_dir}/RUNTIME_CONFIG.{ext} |
| CONDENSED_SUMMARY | {output_dir}/CONDENSED_SUMMARY.{ext} |
| KEY_POINTS_LIST | {output_dir}/KEY_POINTS_LIST.{ext} |
| PARSED_DOCUMENT | {work_dir}/intermediate/PARSED_DOCUMENT-{seq}.json |
| IMPORTANCE_ANALYSIS | {work_dir}/intermediate/IMPORTANCE_ANALYSIS-{seq}.json |
| REDUNDANCY_CLUSTERS | {work_dir}/intermediate/REDUNDANCY_CLUSTERS-{seq}.json |
| KEY_POINTS_RAW | {work_dir}/intermediate/KEY_POINTS_RAW-{seq}.json |
| SUMMARY_BLOCKS | {work_dir}/intermediate/SUMMARY_BLOCKS-{seq}.json |
| OUTPUT_DOCUMENTS | {work_dir}/intermediate/OUTPUT_DOCUMENTS-{seq}.json |
| VALIDATION_REPORT | {work_dir}/reports/VALIDATION_REPORT-{seq}.json |
| ERROR_REPORT | {work_dir}/reports/ERROR_REPORT-{seq}.json |
| EXECUTION_LOG | {work_dir}/logs/EXECUTION_LOG-{seq}.log |

### Naming Rules

1. All artifact keys use UPPER_SNAKE_CASE.
2. Intermediate artifacts use the stage output name as the key prefix.
3. Sequence numbers ({seq}) are zero-padded to 2 digits for sort order.
4. File extensions match the content format (json for structured data, log for
   text logs, md or txt for rendered output).
5. No absolute paths appear in any artifact definition.
6. No hardcoded job IDs or sequence numbers appear in the contract.

---

## Self-Validation

### Input Coverage

| Requirement | Contract Artifact | Status |
|---|---|---|
| IN-001: Source text document | IN-AC-001: SOURCE_TEXT | COVERED |
| V-IN-001: File exists and readable | Mapped to V-MAP-IN-001 | COVERED |
| V-IN-002: Extension .txt or .md | Mapped to V-MAP-IN-002 | COVERED |
| V-IN-003: Non-empty content | Mapped to V-MAP-IN-003, V-MAP-IN-007 | COVERED |
| V-IN-004: Detectable language | Mapped to V-MAP-IN-004 | COVERED |

### Output Coverage

| Requirement | Contract Artifact | Status |
|---|---|---|
| OUT-001: Condensed Summary | OUT-AC-001: CONDENSED_SUMMARY | COVERED |
| OUT-002: Key Points List | OUT-AC-002: KEY_POINTS_LIST | COVERED |
| Q-OUT-001: Capture core message | GI-002, VR-004 | COVERED |
| Q-OUT-002: No new information | GI-002, VR-004, VR-007 | COVERED |
| Q-OUT-003: Logical flow | GI-005, VR-003 | COVERED |
| Q-OUT-004: At most 20% word count | GI-003, VR-001 | COVERED |
| Q-OUT-005: Trace to source | GI-004, VR-007 | COVERED |
| Q-OUT-006: Importance scores present | VR-005 | COVERED |
| Q-OUT-007: Ordered key points | INV-S3-003 | COVERED |
| C-PERF-001: 20% compression | GI-003, VR-001 | COVERED |
| C-FMT-001: Input .txt/.md | V-MAP-IN-002 | COVERED |
| C-FMT-002: Summary is prose | MAP-OUT-001 block_type | COVERED |
| C-FMT-003: Key points ordered with scores | MAP-OUT-002 block_type | COVERED |
| C-FMT-004: Same language | GI-001, VR-002, VR-006 | COVERED |
| C-CMP-001: No new information | GI-002, VR-004, VR-007 | COVERED |
| C-CMP-002: Preserve source language | GI-001, INV-S5-002 | COVERED |
| C-CMP-003: Preserve logical structure | GI-005, INV-S4-003 | COVERED |

### Pipeline Stage Coverage

| Stage | Input Artifact | Output Artifact |
|---|---|---|
| Stage 0: Input Loading | SOURCE_TEXT | PARSED_DOCUMENT |
| Stage 1: Importance Scoring | PARSED_DOCUMENT | IMPORTANCE_ANALYSIS |
| Stage 2: Redundancy Analysis | IMPORTANCE_ANALYSIS | REDUNDANCY_CLUSTERS |
| Stage 3: Key Point Extraction | REDUNDANCY_CLUSTERS | KEY_POINTS_RAW |
| Stage 4: Summary Block Composition | REDUNDANCY_CLUSTERS, PARSED_DOCUMENT | SUMMARY_BLOCKS |
| Stage 5: Output Assembly | KEY_POINTS_RAW, SUMMARY_BLOCKS | OUTPUT_DOCUMENTS |
| Stage 6: Output Validation | OUTPUT_DOCUMENTS | VALIDATION_REPORT |

All 7 stages (0 through 6) from RUNTIME_IMPL are covered by intermediate artifacts.

### Consistency Check

| Check | Status |
|---|---|
| All input artifacts from requirement are listed | PASS |
| All output artifacts from requirement are listed | PASS |
| Path patterns use variables, not absolute paths | PASS |
| Path patterns use {job_id} and {seq} consistently | PASS |
| Relationships form a valid DAG (no cycles) | PASS |
| Required/optional status is declared for every artifact | PASS |
| Every intermediate artifact traces to a pipeline stage | PASS |
| Every validation artifact traces to a validation rule set | PASS |
| No non-ASCII characters in the contract | PASS |

---

## References

- REQUIREMENT_ANALYSIS-01.md -- Source requirement analysis
- COMPOSITION_SPEC-01.md -- Composition specification with meta schema
- RUNTIME_IMPL-01.md -- Runtime implementation design notes
- BASE_COMPOSITION_STANDARD_v1.0.md -- Universal composition standard

---

**End of Artifact Contract**
