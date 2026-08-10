---
doc_type: "step_sequence"
identity_locked: true
generator_name: "text_summarizer_ayz"
version: "1.0.0"
source_artifact_contract: "ARTIFACT_CONTRACT-01"
source_runtime_impl: "RUNTIME_IMPL-01"
source_composition_spec: "COMPOSITION_SPEC-01"
job_id: "AGB-1p3xktl0"
generated_at: "2026-08-10"
total_steps: 18
output_types: "condensed_summary, key_points_list"
review_loop_count: 1
recovery_loop_count: 1
approval_gate_count: 0
phase_count: 4
pipeline_stage_count: 7
---

# Step Sequence

## Target Identity Reference

The following identity values are sourced from the upstream design artifacts
(RUNTIME_IMPL-01, COMPOSITION_SPEC-01, ARTIFACT_CONTRACT-01) and are
locked for this generated workflow. All step definitions in this document
inherit these identity constraints.

| Field | Value |
|---|---|
| generator_name | text_summarizer_ayz |
| codename | text_summarizer_ayz |
| version | 1.0.0 |
| pattern | Input Transformation (Pattern 2) |
| output_types | condensed_summary, key_points_list |
| input_artifact | SOURCE_TEXT |
| output_artifacts | CONDENSED_SUMMARY, KEY_POINTS_LIST |

Identity is locked: no downstream configuration may override or substitute
these values.

---

## Phase Overview

The generated text_summarizer_ayz workflow decomposes into 4 phases. Phase 1
handles input validation and configuration loading. Phase 2 executes the
7-stage transformation pipeline defined in RUNTIME_IMPL-01 (Stage 0 through
Stage 6). Phase 3 validates output quality and performs LLM-based review.
Phase 4 handles delivery and completion.

Each phase maps directly to the runtime implementation architecture
described in RUNTIME_IMPL-01.

| Phase | Name | Step Count | Step Types |
|---|---|---|---|
| 1 | Input Preparation | 2 | 2 action |
| 2 | Pipeline Execution | 12 | 12 action |
| 3 | Output Validation and Review | 2 | 1 action, 1 prompt |
| 4 | Delivery | 2 | 2 action |

Total primary steps: 18 (16 action, 2 prompt).
Auxiliary step (refinement only): 1 (adjust_parameters).
Grand total including auxiliary: 19.

Step type distribution across all phases:

| Step Type | Count | Description |
|---|---|---|
| action | 16 | Deterministic Python steps (validation, pipeline stages, rendering) |
| prompt | 2 | LLM-driven quality review and parameter adjustment |

---

## Step Definitions

Every step in the generated workflow is defined below. Each step has a
unique name, a type (action or prompt), routing configuration, and a
role_policy for prompt-driven coder assignment.

### Phase 1: Input Preparation

| # | Step Name | Type | onsuccess | on_reject_refine | Role Policy |
|---|---|---|---|---|---|
| 1 | validate_input | action | load_configuration | -- | (action) |
| 2 | load_configuration | action | parse_input | -- | (action) |

Phase 1 validates the external input artifact (SOURCE_TEXT) and constructs
the runtime configuration for pipeline execution.

Step 1 (validate_input) checks constraints V-MAP-IN-001 through V-MAP-IN-007
(file existence, extension .txt or .md, non-empty content, detectable
language, at least one structural section, non-empty text units, positive
word count). Empty text units (V-MAP-IN-006) are skipped with a logged
warning per RUNTIME_IMPL-01 error recovery strategy.

Step 2 (load_configuration) loads RUNTIME_CONFIG if present, merges with
default values, and produces the internal CONFIG_STATE artifact.
Configuration source priority: command-line arguments, environment variables,
configuration file, default values (per RUNTIME_IMPL-01 Configuration
Design).

### Phase 2: Pipeline Execution

| # | Step Name | Type | onsuccess | on_reject_refine | Role Policy |
|---|---|---|---|---|---|
| 3 | parse_input | action | score_importance | -- | (action) |
| 4 | score_importance | action | validate_importance | -- | (action) |
| 5 | validate_importance | action | detect_redundancy | -- | (action) |
| 6 | detect_redundancy | action | validate_redundancy | -- | (action) |
| 7 | validate_redundancy | action | extract_keypoints | -- | (action) |
| 8 | extract_keypoints | action | validate_keypoints | -- | (action) |
| 9 | validate_keypoints | action | compose_summary_blocks | -- | (action) |
| 10 | compose_summary_blocks | action | validate_summary_blocks | -- | (action) |
| 11 | validate_summary_blocks | action | assemble_output_documents | -- | (action) |
| 12 | assemble_output_documents | action | validate_assembly | -- | (action) |
| 13 | validate_assembly | action | render_outputs | -- | (action) |
| 14 | render_outputs | action | validate_outputs | -- | (action) |

Phase 2 implements the 7-stage transformation pipeline from RUNTIME_IMPL-01.
Each pipeline stage is decomposed into a transformation step followed by an
invariant validation step where applicable.

Stage mapping:

| Step | Pipeline Stage | Module | Invariant Enforced |
|---|---|---|---|
| parse_input | Stage 0: Input Loading | Module 1 (input_loader) | V-MAP-IN-005, V-MAP-IN-006 |
| score_importance | Stage 1: Importance Scoring | Module 2 (importance_scorer) | -- |
| validate_importance | Stage 1 Invariant Check | -- | INV-S1-001, INV-S1-002, INV-S1-003, INV-S1-004 |
| detect_redundancy | Stage 2: Redundancy Analysis | Module 3 (redundancy_detector) | -- |
| validate_redundancy | Stage 2 Invariant Check | -- | INV-S2-001, INV-S2-002, INV-S2-003, INV-S2-004 |
| extract_keypoints | Stage 3: Key Point Extraction | Module 4 (keypoint_extractor) | -- |
| validate_keypoints | Stage 3 Invariant Check | -- | INV-S3-001, INV-S3-002, INV-S3-003, INV-S3-004 |
| compose_summary_blocks | Stage 4: Summary Block Composition | Module 5 (summary_composer) | -- |
| validate_summary_blocks | Stage 4 Invariant Check | -- | INV-S4-001, INV-S4-002, INV-S4-003, INV-S4-004, INV-S4-005 |
| assemble_output_documents | Stage 5: Output Assembly | Module 6 (output_assembler) | -- |
| validate_assembly | Stage 5 Invariant Check | -- | INV-S5-001, INV-S5-002, INV-S5-003, INV-S5-004 |
| render_outputs | Module 8: Output Rendering | Module 8 (output_renderer) | GI-001, GI-002, GI-003, GI-004, GI-005 |

Extension protocols used per step:

| Step | Protocol | Reference |
|---|---|---|
| parse_input | EXT-001 (InputParser) | RUNTIME_IMPL-01 Module 1, COMPOSITION_SPEC EXT-001 |
| score_importance | EXT-002 (ImportanceScorer) | RUNTIME_IMPL-01 Module 2, COMPOSITION_SPEC EXT-002 |
| detect_redundancy | EXT-003 (RedundancyDetector) | RUNTIME_IMPL-01 Module 3, COMPOSITION_SPEC EXT-003 |
| render_outputs | EXT-004 (OutputRenderer) | RUNTIME_IMPL-01 Module 8, COMPOSITION_SPEC EXT-004 |

### Phase 3: Output Validation and Review

| # | Step Name | Type | onsuccess | on_reject_refine | Role Policy |
|---|---|---|---|---|---|
| 15 | validate_outputs | action | review_quality | score_importance | (action) |
| 16 | review_quality | prompt | promote_outputs | adjust_parameters | reviewer_standard |

Phase 3 evaluates the generated outputs against validation rules VR-001
through VR-007 and performs a quality review of the summary content.

Step 15 (validate_outputs) implements Stage 6 from RUNTIME_IMPL-01. For
each OutputDocument, it evaluates every assigned ValidationRule:
- VR-001: compression_ratio <= 0.20 (condensed_summary)
- VR-002: language match (condensed_summary, key_points_list)
- VR-003: structure preservation (condensed_summary)
- VR-004: no new information (condensed_summary, key_points_list)
- VR-005: importance scores present (key_points_list)
- VR-006: language match (key_points_list)
- VR-007: no new information (key_points_list)

If any rule fails, the step raises ValidationFailureError. Compression ratio
failures (VR-001) trigger the compression recovery loop. Language failures
(VR-002, VR-006) are unrecoverable.

Step 16 (review_quality) uses the reviewer_standard role policy to assess
output quality beyond structural constraints: core message capture, logical
coherence, information preservation, and readability.

### Phase 4: Delivery

| # | Step Name | Type | onsuccess | on_reject_refine | Role Policy |
|---|---|---|---|---|---|
| 17 | promote_outputs | action | complete_pipeline | -- | (action) |
| 18 | complete_pipeline | action | (terminal) | -- | (action) |

Phase 4 copies the output files to their final output location and records
the pipeline completion result.

Step 17 (promote_outputs) copies CONDENSED_SUMMARY and KEY_POINTS_LIST to
the output directory defined by {output_dir}.

Step 18 (complete_pipeline) writes the EXECUTION_LOG with stage timings and
records the pipeline completion result.

### Auxiliary Step (Refinement Only)

| # | Step Name | Type | onsuccess | on_reject_refine | Role Policy |
|---|---|---|---|---|---|
| 19 | adjust_parameters | prompt | parse_input | -- | architect_standard |

Step 19 is an auxiliary prompt step activated only during quality review
refinement. It modifies runtime configuration parameters
(compression_ratio, keypoint_threshold, similarity_threshold) based on
review feedback from step 16. After adjustment, the pipeline re-executes
from parse_input (step 3).

### Role Policy Distribution

| Role Policy | Count | Steps |
|---|---|---|
| reviewer_standard | 1 | review_quality (16) |
| architect_standard | 1 | adjust_parameters (19, auxiliary) |
| (action) | 16 | All other steps (1-15, 17-18) |

Total prompt-driven steps: 2 (review_quality, adjust_parameters).
Total action-driven steps: 16.

---

## Routing Logic

### Onsuccess Routing Chain

The primary execution path follows a linear chain through all 18 steps:

```
validate_input (1)
  -> load_configuration (2)
  -> parse_input (3)
  -> score_importance (4)
  -> validate_importance (5)
  -> detect_redundancy (6)
  -> validate_redundancy (7)
  -> extract_keypoints (8)
  -> validate_keypoints (9)
  -> compose_summary_blocks (10)
  -> validate_summary_blocks (11)
  -> assemble_output_documents (12)
  -> validate_assembly (13)
  -> render_outputs (14)
  -> validate_outputs (15)
  -> review_quality (16)
  -> promote_outputs (17)
  -> complete_pipeline (18)
  -> (terminal)
```

### Compression Recovery Loop

When validate_outputs (Step 15) detects that the compression_ratio exceeds
0.20 (VR-001 violation), the pipeline returns to score_importance (Step 4)
with a higher keypoint_threshold. This implements the recovery mechanism
defined in RUNTIME_IMPL-01 Error Handling Strategy.

| From Step | on_reject_refine Target | Max Iterations | Exhausted Code | Exhausted Class |
|---|---|---|---|---|
| validate_outputs (15) | score_importance (4) | 3 | COMPRESSION_RECOVERY_EXHAUSTED | PIPELINE_FAILURE |

Recovery loop mechanics:

1. Steps 3-15 execute normally.
2. validate_outputs (Step 15) checks compression_ratio <= 0.20
   (VR-001, GI-003).
3. If compression_ratio <= 0.20: onsuccess to review_quality (Step 16).
4. If compression_ratio > 0.20: on_reject_refine to score_importance
   (Step 4). The runtime configuration keypoint_threshold is increased to
   reduce keypoint count and thus summary size.
5. Steps 4-15 re-execute with tighter threshold.
6. This loop repeats up to 3 times.
7. If all 3 attempts fail, pipeline halts with
   COMPRESSION_RECOVERY_EXHAUSTED.

Trace: RUNTIME_IMPL-01 Error Handling Strategy, COMPOSITION_SPEC-01 VR-001,
GI-003.

### Quality Review Loop

When review_quality (Step 16) determines that the outputs do not meet
quality standards, the workflow enters an adjustment loop.

| From Step | on_reject_refine Target | Max Iterations | Exhausted Code | Exhausted Class |
|---|---|---|---|---|
| review_quality (16) | adjust_parameters (19) | 2 | QUALITY_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED |

Note: adjust_parameters (Step 19) is an auxiliary prompt step activated
only during refinement. It is not part of the primary execution chain.

Quality review loop mechanics:

1. review_quality (Step 16) evaluates output quality using
   reviewer_standard role.
2. If quality PASSES: onsuccess to promote_outputs (Step 17).
3. If quality REJECTS: on_reject_refine to adjust_parameters (Step 19).
4. adjust_parameters modifies pipeline parameters (e.g.,
   keypoint_threshold, similarity_threshold, compression_ratio) based on
   review feedback.
5. After adjustment, the pipeline re-executes from parse_input (Step 3)
   with updated parameters.
6. This loop repeats up to 2 times.
7. If all attempts fail, workflow halts with QUALITY_REVIEW_EXHAUSTED.

Trace: COMPOSITION_SPEC-01 VR-001 through VR-007.

### Language Validation Failure

When validate_outputs (Step 15) detects a language mismatch (VR-002 or
VR-006 violation), the pipeline halts immediately. Language validation
failure is unrecoverable as defined in RUNTIME_IMPL-01 Error Handling
Strategy.

| From Step | Failure Action | Error Code |
|---|---|---|
| validate_outputs (15) on VR-002/VR-006 | Halt pipeline | LANGUAGE_MISMATCH |

### Onsuccess Verification

| From Step | onsuccess Target | Target Exists | PASS |
|---|---|---|---|
| validate_input (1) | load_configuration (2) | Yes | PASS |
| load_configuration (2) | parse_input (3) | Yes | PASS |
| parse_input (3) | score_importance (4) | Yes | PASS |
| score_importance (4) | validate_importance (5) | Yes | PASS |
| validate_importance (5) | detect_redundancy (6) | Yes | PASS |
| detect_redundancy (6) | validate_redundancy (7) | Yes | PASS |
| validate_redundancy (7) | extract_keypoints (8) | Yes | PASS |
| extract_keypoints (8) | validate_keypoints (9) | Yes | PASS |
| validate_keypoints (9) | compose_summary_blocks (10) | Yes | PASS |
| compose_summary_blocks (10) | validate_summary_blocks (11) | Yes | PASS |
| validate_summary_blocks (11) | assemble_output_documents (12) | Yes | PASS |
| assemble_output_documents (12) | validate_assembly (13) | Yes | PASS |
| validate_assembly (13) | render_outputs (14) | Yes | PASS |
| render_outputs (14) | validate_outputs (15) | Yes | PASS |
| validate_outputs (15) | review_quality (16) | Yes | PASS |
| review_quality (16) | promote_outputs (17) | Yes | PASS |
| promote_outputs (17) | complete_pipeline (18) | Yes | PASS |
| complete_pipeline (18) | (terminal) | N/A | PASS |
| adjust_parameters (19) | parse_input (3) | Yes | PASS |

All 19 onsuccess links verified. No dangling references. PASS.

### On_Reject_Refine Verification

| From Step | on_reject_refine Target | Target Exists | Max Iterations | PASS |
|---|---|---|---|---|
| validate_outputs (15) | score_importance (4) | Yes | 3 | PASS |
| review_quality (16) | adjust_parameters (19) | Yes | 2 | PASS |

All 2 on_reject_refine links verified. All loops have max iterations
greater than 0 to prevent infinite loops. PASS.

### Dead-End Check

The only terminal step is complete_pipeline (Step 18), which has no
onsuccess (pipeline ends). All non-terminal steps have at least one exit
path (onsuccess or on_reject_refine). PASS.

### Self-Loop Check

No step routes to itself directly. The compression recovery loop goes
validate_outputs -> score_importance -> ... -> validate_outputs, which is
a multi-step cycle, not a self-loop. The quality loop goes
review_quality -> adjust_parameters -> parse_input -> ... -> review_quality,
also a multi-step cycle. PASS.

### Cycle Check

No unbounded cycles exist. Both loops have explicit max iteration limits:
- Compression recovery: max 3 iterations
- Quality review: max 2 iterations

PASS.

---

## Review Loops

### Review/Refine Loop Table

| # | Review Step | Refine Step | Max Iterations | Exhausted Code | Exhausted Class |
|---|---|---|---|---|---|
| 1 | review_quality (16) | adjust_parameters (19) | 2 | QUALITY_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED |

### Recovery Loop Table

| # | Trigger Step | Recovery Target | Max Iterations | Exhausted Code | Exhausted Class |
|---|---|---|---|---|---|
| 1 | validate_outputs (15) | score_importance (4) | 3 | COMPRESSION_RECOVERY_EXHAUSTED | PIPELINE_FAILURE |

### Loop Mechanics

#### Compression Recovery Loop

This loop implements the recovery mechanism from RUNTIME_IMPL-01
Error Handling Strategy. It is triggered when the compression ratio exceeds
the configured target (default 0.20 per VR-001, GI-003).

1. validate_outputs (Step 15) computes compression_ratio from
   OUTPUT_DOCUMENTS.
2. If compression_ratio > 0.20:
    a. Control transfers to score_importance (Step 4).
    b. Runtime configuration keypoint_threshold is increased to select fewer
       key points, reducing the summary word count.
    c. Steps 4-15 re-execute with the tighter threshold.
3. If compression_ratio <= 0.20:
    a. Control proceeds to review_quality (Step 16).
4. Maximum 3 recovery attempts before pipeline failure.

Trace: COMPOSITION_SPEC-01 VR-001, GI-003, INV-S4-002. RUNTIME_IMPL-01
Error Handling Strategy.

#### Quality Review Loop

This loop ensures the generated outputs meet quality standards beyond
the structural constraints. It is triggered when the LLM reviewer
determin the outputs are inadequate.

1. review_quality (Step 16) evaluates the outputs against quality
   criteria: core message capture, logical structure, coherence, and
   information preservation.
2. If quality passes: control proceeds to promote_outputs (Step 17).
3. If quality rejected:
    a. Control transfers to adjust_parameters (Step 19).
    b. adjust_parameters modifies runtime configuration parameters based on
       review feedback (e.g., adjust keypoint_threshold, modify
       similarity_threshold, adjust compression_ratio).
    c. Pipeline re-executes from parse_input (Step 3) with updated
       parameters.
4. Maximum 2 review cycles before human intervention required.

Trace: COMPOSITION_SPEC-01 VR-001 through VR-007.

---

## Human Approval

### Approval Gate Configuration

The generated text_summarizer_ayz workflow does NOT require explicit human
approval gates. All primary steps set requires_human_approval_after = false.

| Step | requires_human_approval_after | Rationale |
|---|---|---|
| validate_input (1) | false | Deterministic validation |
| load_configuration (2) | false | Configuration is parameter-driven |
| parse_input (3) | false | Deterministic parsing |
| score_importance (4) | false | Deterministic scoring |
| validate_importance (5) | false | Deterministic invariant check |
| detect_redundancy (6) | false | Deterministic clustering |
| validate_redundancy (7) | false | Deterministic invariant check |
| extract_keypoints (8) | false | Deterministic extraction |
| validate_keypoints (9) | false | Deterministic invariant check |
| compose_summary_blocks (10) | false | Deterministic composition |
| validate_summary_blocks (11) | false | Deterministic invariant check |
| assemble_output_documents (12) | false | Deterministic assembly |
| validate_assembly (13) | false | Deterministic invariant check |
| render_outputs (14) | false | Deterministic rendering |
| validate_outputs (15) | false | Deterministic validation rule check |
| review_quality (16) | false | Automated LLM review gate |
| promote_outputs (17) | false | Deterministic file copy |
| complete_pipeline (18) | false | Completion recording |
| adjust_parameters (19) | false | Parameter adjustment |

### Why No Human Approval Gates

The text_summarizer_ayz pipeline relies on automated quality gates rather
than human approval:

1. Structural constraints (VR-001 through VR-007, GI-001 through GI-006)
   are enforced by deterministic pipeline stages (Steps 5, 7, 9, 11, 13,
   15).
2. Quality review (Step 16) uses LLM-based assessment as an automated
   gate with a refinement loop.
3. Output validation rules (VR-001 through VR-007) are enforced by the
   validate_outputs action step (Step 15).
4. Recovery loops handle constraint violations automatically.

This design provides sufficient quality assurance without requiring
human intervention during normal pipeline execution.

---

## Artifact Flow Chains

This section traces each artifact from its producer step to its consumer
steps. Every artifact key from ARTIFACT_CONTRACT-01 is accounted for.
No temporal violations exist.

### Input Artifact Flows

| Artifact Key | Source | First Consumer | All Consumers |
|---|---|---|---|
| SOURCE_TEXT | External input | validate_input (1) | Steps 1, 3 |
| RUNTIME_CONFIG | External input (optional) | load_configuration (2) | Steps 2-15, 19 |

### Pipeline Configuration Flows

| Artifact Key | Producer Step | Consumer Steps |
|---|---|---|
| CONFIG_STATE | load_configuration (2) | Steps 3-15, 19 |

### Layer 1 Component Flows (Input Parsing)

| Artifact Key | Producer Step | Consumer Steps |
|---|---|---|
| PARSED_DOCUMENT (INT-AC-001) | parse_input (3) | Steps 4, 5, 10 |

### Layer 2 Component Flows (Transformation)

| Artifact Key | Producer Step | Consumer Steps |
|---|---|---|
| IMPORTANCE_ANALYSIS (INT-AC-002) | score_importance (4) | Steps 5, 6, 8, 10 |
| INV_REPORT_S1 | validate_importance (5) | Step 5 (gate check) |
| REDUNDANCY_CLUSTERS (INT-AC-003) | detect_redundancy (6) | Steps 7, 8, 10 |
| INV_REPORT_S2 | validate_redundancy (7) | Step 7 (gate check) |
| KEY_POINTS_RAW (INT-AC-004) | extract_keypoints (8) | Steps 9, 12 |
| INV_REPORT_S3 | validate_keypoints (9) | Step 9 (gate check) |
| SUMMARY_BLOCKS (INT-AC-005) | compose_summary_blocks (10) | Steps 11, 12 |
| INV_REPORT_S4 | validate_summary_blocks (11) | Step 11 (gate check) |

### Layer 3 Component Flows (Output Rendering)

| Artifact Key | Producer Step | Consumer Steps |
|---|---|---|
| OUTPUT_DOCUMENTS (INT-AC-006) | assemble_output_documents (12) | Steps 13, 14, 15 |
| INV_REPORT_S5 | validate_assembly (13) | Step 13 (gate check) |
| CONDENSED_SUMMARY (OUT-AC-001) | render_outputs (14) | Steps 15-17 |
| KEY_POINTS_LIST (OUT-AC-002) | render_outputs (14) | Steps 15-17 |

### Output Validation Flows

| Artifact Key | Producer Step | Consumer Steps |
|---|---|---|
| VALIDATION_REPORT (VAL-AC-001) | validate_outputs (15) | Step 16 |
| QUALITY_REVIEW_REPORT | review_quality (16) | Step 19 (if rejected) |
| ADJUSTED_CONFIG | adjust_parameters (19) | Step 3 (re-execution) |

### Error and Log Flows

| Artifact Key | Producer Step | Consumer Steps |
|---|---|---|
| ERROR_REPORT (VAL-AC-002) | Any step (on failure) | (terminal report) |
| EXECUTION_LOG (VAL-AC-003) | complete_pipeline (18) | (terminal deliverable) |

### Delivery Flows

| Artifact Key | Producer Step | Consumer Steps |
|---|---|---|
| CONDENSED_SUMMARY_PROMOTED | promote_outputs (17) | (terminal deliverable) |
| KEY_POINTS_LIST_PROMOTED | promote_outputs (17) | (terminal deliverable) |
| COMPLETION_RESULT | complete_pipeline (18) | (terminal marker) |

### Artifact Flow Verification

| Check | Result |
|---|---|
| All artifact keys from ARTIFACT_CONTRACT-01 are accounted for | PASS |
| No artifact is consumed before it is produced | PASS |
| Every produced artifact is consumed by at least one step or is terminal | PASS |
| No dangling references to undeclared artifact keys | PASS |
| Input artifacts (SOURCE_TEXT, RUNTIME_CONFIG) resolve from external sources | PASS |
| Terminal deliverables (CONDENSED_SUMMARY_PROMOTED, KEY_POINTS_LIST_PROMOTED) are final outputs | PASS |
| Intermediate artifacts (CONFIG_STATE, PARSED_DOCUMENT, etc.) are internal | PASS |
| Validation artifacts (VALIDATION_REPORT, ERROR_REPORT, EXECUTION_LOG) are produced correctly | PASS |

---

## Failure Handling

### Step-Level Failure Matrix

| Step | Failure Type | Error Code | Recovery | Trace |
|---|---|---|---|---|
| validate_input (1) | File not found | FILE_NOT_FOUND | Halt | V-MAP-IN-001 |
| validate_input (1) | Bad extension | UNSUPPORTED_FORMAT | Halt | V-MAP-IN-002 |
| validate_input (1) | Empty content | EMPTY_INPUT | Halt | V-MAP-IN-003, V-MAP-IN-007 |
| validate_input (1) | Language detection failed | LANGUAGE_UNDETECTABLE | Halt | V-MAP-IN-004 |
| parse_input (3) | No sections produced | NO_SECTIONS | Halt | V-MAP-IN-005 |
| parse_input (3) | Parse failure | PARSING_ERROR | Halt | MAP-IN-001 to MAP-IN-007 |
| score_importance (4) | Scoring error | SCORING_ERROR | Halt | INV-S1-001 |
| validate_importance (5) | Score out of range | S1_SCORE_RANGE | Halt | INV-S1-002 |
| validate_importance (5) | Rank violation | S1_RANK_VIOLATION | Halt | INV-S1-003, INV-S1-004 |
| detect_redundancy (6) | Clustering error | CLUSTERING_ERROR | Halt | INV-S2-001 |
| validate_redundancy (7) | Cluster reference invalid | S2_REF_VIOLATION | Halt | INV-S2-001, INV-S2-002 |
| validate_redundancy (7) | Representative wrong | S2_REP_VIOLATION | Halt | INV-S2-003 |
| extract_keypoints (8) | No keypoints selected | NO_KEYPOINTS | Halt | INV-S3-004 |
| validate_keypoints (9) | Duplicate source ref | S3_DUPLICATE | Halt | INV-S3-002 |
| validate_keypoints (9) | Ordering violation | S3_ORDER_VIOLATION | Halt | INV-S3-003 |
| compose_summary_blocks (10) | Missing section block | S4_MISSING_BLOCK | Halt | INV-S4-001 |
| validate_summary_blocks (11) | Word budget exceeded | S4_BUDGET_EXCEEDED | Halt | INV-S4-002 |
| validate_summary_blocks (11) | Order violation | S4_ORDER_VIOLATION | Halt | INV-S4-003 |
| validate_summary_blocks (11) | New info detected | S4_NEW_INFO | Halt | INV-S4-005 |
| assemble_output_documents (12) | No outputs produced | S5_NO_OUTPUT | Halt | INV-S5-001 |
| validate_assembly (13) | Language mismatch | S5_LANGUAGE_MISMATCH | Halt | INV-S5-002 |
| validate_assembly (13) | Empty output blocks | S5_EMPTY_BLOCKS | Halt | INV-S5-003 |
| render_outputs (14) | Write failure | WRITE_ERROR | Halt | MAP-OUT-003 |
| validate_outputs (15) | Compression exceeded | COMPRESSION_EXCEEDED | Recovery loop (3x) | VR-001, GI-003 |
| validate_outputs (15) | Language mismatch | LANGUAGE_MISMATCH | Halt (unrecoverable) | VR-002, VR-006, GI-001 |
| validate_outputs (15) | Structure violation | STRUCTURE_VIOLATION | Halt | VR-003, GI-005 |
| validate_outputs (15) | New info detected | NEW_INFO_DETECTED | Halt | VR-004, VR-007, GI-002 |
| validate_outputs (15) | Scores missing | SCORES_MISSING | Halt | VR-005 |
| review_quality (16) | Quality rejected | QUALITY_REVIEW_EXHAUSTED | Recovery loop (2x) | Quality criteria |
| promote_outputs (17) | Promotion failed | PROMOTION_ERROR | Halt | N/A |

### Exhaustion Handling

| Loop | Exhausted Code | Exhausted Class | Action |
|---|---|---|---|
| Compression recovery (3x) | COMPRESSION_RECOVERY_EXHAUSTED | PIPELINE_FAILURE | Halt pipeline, produce ERROR_REPORT |
| Quality review (2x) | QUALITY_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED | Halt pipeline, request human review |

---

## Self-Validation

### Check 1: Step Definition Completeness

| Check | Result |
|---|---|
| All 7 pipeline stages (Stage 0-6) have corresponding steps | PASS |
| Input parsing step (Stage 0) exists before pipeline execution | PASS |
| Invariant validation step exists after each pipeline stage (Stages 1-5) | PASS |
| Input validation step exists before pipeline execution | PASS |
| Output validation step exists after pipeline execution (Stage 6) | PASS |
| Quality review step exists before delivery | PASS |
| Completion step is terminal | PASS |
| Auxiliary refinement step (adjust_parameters) is defined | PASS |
| Output renderer step (Module 8) exists between assembly and validation | PASS |

### Check 2: Routing Validity

| Check | Result |
|---|---|
| All onsuccess targets reference existing steps | PASS |
| All on_reject_refine targets reference existing steps | PASS |
| No step routes to itself | PASS |
| No unbounded cycles | PASS |
| Terminal step has no exit path | PASS |
| All non-terminal steps have at least one exit | PASS |

### Check 3: Artifact Flow Validity

| Check | Result |
|---|---|
| SOURCE_TEXT consumed after external provision | PASS |
| RUNTIME_CONFIG consumed after external provision | PASS |
| CONFIG_STATE produced before any pipeline step consumes it | PASS |
| PARSED_DOCUMENT produced before Layer 2 steps consume it | PASS |
| IMPORTANCE_ANALYSIS produced before redundancy detection consumes it | PASS |
| REDUNDANCY_CLUSTERS produced before keypoint extraction consumes it | PASS |
| KEY_POINTS_RAW produced before output assembly consumes it | PASS |
| SUMMARY_BLOCKS produced before output assembly consumes it | PASS |
| OUTPUT_DOCUMENTS produced before rendering consumes it | PASS |
| CONDENSED_SUMMARY produced before validation consumes it | PASS |
| KEY_POINTS_LIST produced before validation consumes it | PASS |
| VALIDATION_REPORT produced before review consumes it | PASS |
| No step consumes an artifact before it is produced | PASS |

### Check 4: Constraint Enforcement

| Constraint | Enforced By | PASS |
|---|---|---|
| GI-001 (same language) | validate_outputs (15) via VR-002, VR-006 | PASS |
| GI-002 (no new information) | validate_summary_blocks (11) via INV-S4-005, validate_outputs (15) via VR-004, VR-007 | PASS |
| GI-003 (20% max compression) | validate_summary_blocks (11) via INV-S4-002, validate_outputs (15) via VR-001 + recovery loop | PASS |
| GI-004 (traceability) | validate_outputs (15) via VR-004, VR-007, structural tracing | PASS |
| GI-005 (structure preservation) | validate_outputs (15) via VR-003, validate_summary_blocks (11) via INV-S4-003 | PASS |

### Check 5: Invariant Coverage

| Invariant | Enforced By | PASS |
|---|---|---|
| INV-S1-001 (one ScoredUnit per TextUnit) | validate_importance (5) | PASS |
| INV-S1-002 (scores in [0.0, 1.0]) | validate_importance (5) | PASS |
| INV-S1-003 (sequential ranks) | validate_importance (5) | PASS |
| INV-S1-004 (unique ranks) | validate_importance (5) | PASS |
| INV-S2-001 (one cluster per TextUnit) | validate_redundancy (7) | PASS |
| INV-S2-002 (one representative per cluster) | validate_redundancy (7) | PASS |
| INV-S2-003 (representative has highest score) | validate_redundancy (7) | PASS |
| INV-S2-004 (consolidation_score in [0.0, 1.0]) | validate_redundancy (7) | PASS |
| INV-S3-001 (one TextUnit per KeyPoint) | validate_keypoints (9) | PASS |
| INV-S3-002 (unique TextUnit refs) | validate_keypoints (9) | PASS |
| INV-S3-003 (descending importance order) | validate_keypoints (9) | PASS |
| INV-S3-004 (above threshold) | validate_keypoints (9) | PASS |
| INV-S4-001 (one block per section) | validate_summary_blocks (11) | PASS |
| INV-S4-002 (total word count <= max) | validate_summary_blocks (11) | PASS |
| INV-S4-003 (section ordering) | validate_summary_blocks (11) | PASS |
| INV-S4-004 (non-empty blocks) | validate_summary_blocks (11) | PASS |
| INV-S4-005 (no new information) | validate_summary_blocks (11) | PASS |
| INV-S5-001 (at least one output) | validate_assembly (13) | PASS |
| INV-S5-002 (language match) | validate_assembly (13) | PASS |
| INV-S5-003 (non-empty blocks) | validate_assembly (13) | PASS |
| INV-S5-004 (validation rules satisfied) | validate_assembly (13) | PASS |
| INV-S6-001 (no output without passing rules) | validate_outputs (15) | PASS |
| INV-S6-002 (results traceable) | validate_outputs (15) via VALIDATION_REPORT | PASS |

### Check 6: Runtime Implementation Compliance

| RUNTIME_IMPL Section | Step Coverage | PASS |
|---|---|---|
| Module 1: input_loader (Stage 0) | Steps 1, 3 | PASS |
| Module 2: importance_scorer (Stage 1) | Steps 4, 5 | PASS |
| Module 3: redundancy_detector (Stage 2) | Steps 6, 7 | PASS |
| Module 4: keypoint_extractor (Stage 3) | Steps 8, 9 | PASS |
| Module 5: summary_composer (Stage 4) | Steps 10, 11 | PASS |
| Module 6: output_assembler (Stage 5) | Steps 12, 13 | PASS |
| Module 7: output_validator (Stage 6) | Step 15 | PASS |
| Module 8: output_renderer (EXT-004) | Step 14 | PASS |
| Configuration Design | Step 2 | PASS |
| Error Handling Strategy | Failure matrix, recovery loops | PASS |
| Extension Interface (4 Protocols) | Steps 3, 4, 6, 14 via registry | PASS |

### Check 7: Recovery Loop Validity

| Check | Result |
|---|---|
| Compression recovery: validate_outputs -> score_importance | PASS |
| Recovery re-executes Steps 4-15 only | PASS |
| Max 3 iterations prevents infinite loop | PASS |
| Language validation failure is unrecoverable | PASS |
| Quality review: review_quality -> adjust_parameters -> parse_input | PASS |
| Quality recovery re-executes Steps 3-16 | PASS |
| Max 2 iterations prevents infinite loop | PASS |

### Check 8: ASCII Compliance

| Check | Result |
|---|---|
| No em-dashes used | PASS |
| No curly quotes used | PASS |
| No Unicode characters used | PASS |
| YAML frontmatter uses plain ASCII | PASS |
| All identifiers use ASCII characters | PASS |

### Check 9: YAML Frontmatter Compliance

| Field | Value | Present |
|---|---|---|
| doc_type | "step_sequence" | PASS |
| identity_locked | true | PASS |
| generator_name | "text_summarizer_ayz" | PASS |
| version | "1.0.0" | PASS |
| source_artifact_contract | "ARTIFACT_CONTRACT-01" | PASS |
| source_runtime_impl | "RUNTIME_IMPL-01" | PASS |
| source_composition_spec | "COMPOSITION_SPEC-01" | PASS |
| job_id | "AGB-1p3xktl0" | PASS |
| generated_at | "2026-08-10" | PASS |
| total_steps | 18 | PASS |
| output_types | "condensed_summary, key_points_list" | PASS |
| review_loop_count | 1 | PASS |
| recovery_loop_count | 1 | PASS |
| approval_gate_count | 0 | PASS |
| phase_count | 4 | PASS |
| pipeline_stage_count | 7 | PASS |

All mandatory frontmatter fields present. PASS.

### Check 10: Step Count Summary

| Category | Count |
|---|---|
| Total primary steps | 18 |
| Prompt-driven steps | 2 (review_quality, adjust_parameters) |
| Action-driven steps | 16 |
| Input preparation steps | 2 |
| Pipeline execution steps | 12 |
| Output validation steps | 2 |
| Delivery steps | 2 |
| Auxiliary refinement steps | 1 |
| Pipeline stages covered | 7 (Stage 0 through Stage 6) |

---

## Artifact Contract Coverage

This section verifies that every artifact defined in ARTIFACT_CONTRACT-01
is produced and consumed by the step sequence.

### Input Artifact Coverage

| Contract Artifact | Step Producer | Step Consumer | PASS |
|---|---|---|---|
| IN-AC-001: SOURCE_TEXT | External input | validate_input (1), parse_input (3) | PASS |
| IN-AC-002: RUNTIME_CONFIG | External input | load_configuration (2) | PASS |

### Output Artifact Coverage

| Contract Artifact | Step Producer | Step Consumer | PASS |
|---|---|---|---|
| OUT-AC-001: CONDENSED_SUMMARY | render_outputs (14) | validate_outputs (15), promote_outputs (17) | PASS |
| OUT-AC-002: KEY_POINTS_LIST | render_outputs (14) | validate_outputs (15), promote_outputs (17) | PASS |

### Intermediate Artifact Coverage

| Contract Artifact | Step Producer | Step Consumer | PASS |
|---|---|---|---|
| INT-AC-001: PARSED_DOCUMENT | parse_input (3) | score_importance (4), compose_summary_blocks (10) | PASS |
| INT-AC-002: IMPORTANCE_ANALYSIS | score_importance (4) | detect_redundancy (6), extract_keypoints (8), compose_summary_blocks (10) | PASS |
| INT-AC-003: REDUNDANCY_CLUSTERS | detect_redundancy (6) | extract_keypoints (8), compose_summary_blocks (10) | PASS |
| INT-AC-004: KEY_POINTS_RAW | extract_keypoints (8) | assemble_output_documents (12) | PASS |
| INT-AC-005: SUMMARY_BLOCKS | compose_summary_blocks (10) | assemble_output_documents (12) | PASS |
| INT-AC-006: OUTPUT_DOCUMENTS | assemble_output_documents (12) | validate_assembly (13), render_outputs (14) | PASS |

### Validation Artifact Coverage

| Contract Artifact | Step Producer | Step Consumer | PASS |
|---|---|---|---|
| VAL-AC-001: VALIDATION_REPORT | validate_outputs (15) | review_quality (16) | PASS |
| VAL-AC-002: ERROR_REPORT | Any step (on failure) | (terminal report) | PASS |
| VAL-AC-003: EXECUTION_LOG | complete_pipeline (18) | (terminal deliverable) | PASS |

### Processing Order Constraint Coverage

| Constraint | Enforced By | PASS |
|---|---|---|
| ORD-001: PARSED_DOCUMENT before IMPORTANCE_ANALYSIS | parse_input (3) before score_importance (4) | PASS |
| ORD-002: IMPORTANCE_ANALYSIS before REDUNDANCY_CLUSTERS | score_importance (4) before detect_redundancy (6) | PASS |
| ORD-003: REDUNDANCY_CLUSTERS before KEY_POINTS_RAW | detect_redundancy (6) before extract_keypoints (8) | PASS |
| ORD-004: REDUNDANCY_CLUSTERS before SUMMARY_BLOCKS | detect_redundancy (6) before compose_summary_blocks (10) | PASS |
| ORD-005: KEY_POINTS_RAW before OUTPUT_DOCUMENTS | extract_keypoints (8) before assemble_output_documents (12) | PASS |
| ORD-006: SUMMARY_BLOCKS before OUTPUT_DOCUMENTS | compose_summary_blocks (10) before assemble_output_documents (12) | PASS |
| ORD-007: OUTPUT_DOCUMENTS before CONDENSED_SUMMARY | assemble_output_documents (12) before render_outputs (14) | PASS |
| ORD-008: OUTPUT_DOCUMENTS before KEY_POINTS_LIST | assemble_output_documents (12) before render_outputs (14) | PASS |
| ORD-009: VALIDATION_REPORT after all outputs | validate_outputs (15) after render_outputs (14) | PASS |
| ORD-010: RUNTIME_CONFIG loaded before Stage 0 | load_configuration (2) before parse_input (3) | PASS |

---

## Assumptions

| ID | Assumption | Rationale |
|---|---|---|
| ASM-SS-001 | Pipeline stages execute sequentially within a single process | RUNTIME_IMPL-01 Decision 1: Pipeline-Based Execution Model |
| ASM-SS-002 | Each pipeline stage and its invariant check are exposed as separate action steps for observability | Workflow best practice for traceability |
| ASM-SS-003 | The adjust_parameters step uses LLM review feedback to modify runtime configuration | COMPOSITION_SPEC-01 Extension Mechanism (variable components) |
| ASM-SS-004 | Extension implementations are resolved via RuntimeRegistry at pipeline startup | RUNTIME_IMPL-01 Decision 2: Protocol-Based Extension System |
| ASM-SS-005 | Recovery loop increases keypoint_threshold to reduce keypoint count | RUNTIME_IMPL-01 Error Handling Strategy |
| ASM-SS-006 | Invariant validation is performed in dedicated steps rather than inline | Separation of concerns for traceability |
| ASM-SS-007 | Both output types (condensed_summary, key_points_list) are produced in every run unless output_types config overrides | ARTIFACT_CONTRACT-01 default output_types list |
| ASM-SS-008 | Output renderer (Module 8) serializes both output types in a single step | RUNTIME_IMPL-01 Module 8 design |

---

End of Step Sequence Document
