---
doc_type: "step_sequence"
identity_locked: true
generator_name: "text_summarizer_ayz"
version: "1.0.0"
source_artifact_contract: "ARTIFACT_CONTRACT-01.md"
source_runtime_impl: "RUNTIME_IMPL-01.md"
source_composition_spec: "COMPOSITION_SPEC-01.md"
---

# Step Sequence Design -- Text Summarizer

## Overview

This document defines the complete step sequence for the text_summarizer_ayz
generated workflow. It specifies all steps, their types, routing logic,
artifact flow, review loops, and human approval points. The design follows
the pipeline defined in RUNTIME_IMPL-01.md and respects the artifact
dependency graph in ARTIFACT_CONTRACT-01.md.

The workflow consists of 9 execution steps organized into 4 phases:
1. Input Processing (steps 1-3): Load, parse, and validate input
2. Transformation (steps 4-7): Extract, deduplicate, preserve meaning, structure
3. Validation (step 8): Check all constraints and invariants
4. Output (step 9): Render final artifacts

---

## Step Definitions

### Step 1: load_input

| Property | Value |
|---|---|
| Step Name | load_input |
| Step ID | LOAD-001 |
| Step Type | Action (action-driven) |
| Source Module | InputLoader |
| Trace | RUNTIME_IMPL-01.md Pipeline Step 1, MAP-001 |

**Purpose:** Load the source text file from disk, verify existence, detect
format, and reject binary content.

**Behavior:**
- Accept SOURCE_TEXT_FILE path (absolute or relative).
- Verify file exists via OS-level check.
- Read file content using UTF-8 encoding.
- Detect format from file extension (.txt or .md).
- Reject non-text files (binary detection via null byte scan).
- Produce raw text and file metadata for downstream parsing.

**Required Inputs:**

| Artifact Key | Format | Source |
|---|---|---|
| SOURCE_TEXT_FILE | .txt or .md | External caller |

**Produces:**

| Artifact Key | Format | Description |
|---|---|---|
| PARSED_DOCUMENT | JSON (partial) | Raw text content and file metadata |

**Result Meta Key:** `LOAD_RESULT`

**Error Handling:**

| Error Condition | Error Type | Recovery |
|---|---|---|
| File not found | FileNotFoundError | Halt with diagnostic |
| Empty file | EmptyDocumentError | Halt with diagnostic |
| Binary content | BinaryContentError | Halt with diagnostic |

---

### Step 2: parse_document

| Property | Value |
|---|---|
| Step Name | parse_document |
| Step ID | PARSE-001 |
| Step Type | Action (action-driven) |
| Source Module | DocumentParser |
| Trace | RUNTIME_IMPL-01.md Pipeline Step 2, MAP-002, MAP-003, MAP-004 |

**Purpose:** Decompose raw text into Layer 1 structured document tree
(DocumentMetadata, Section[], Paragraph[], Sentence[]).

**Behavior:**
- For Markdown (.md): detect sections by heading markers, assign section_type
  by position (introduction, body, conclusion).
- For Plain Text (.txt): identify paragraphs by blank lines, assign section_type
  by position if 3+ blocks exist.
- Decompose paragraphs into sentences using punctuation delimiters.
- Compute word counts at all levels (document, section, paragraph, sentence).
- Assign unique identifiers to all components.

**Required Inputs:**

| Artifact Key | Format | Source |
|---|---|---|
| PARSED_DOCUMENT | JSON (partial, from load_input) | Step 1 (LOAD-001) |

**Produces:**

| Artifact Key | Format | Description |
|---|---|---|
| PARSED_DOCUMENT | JSON (complete) | Full Layer 1 document tree |

**Result Meta Key:** `PARSE_RESULT`

**Error Handling:**

| Error Condition | Error Type | Recovery |
|---|---|---|
| No parseable sentences | NoContentError | Halt with diagnostic |

---

### Step 3: validate_layer_1

| Property | Value |
|---|---|
| Step Name | validate_layer_1 |
| Step ID | VAL-L1-001 |
| Step Type | Action (action-driven) |
| Source Module | StructureValidator |
| Trace | RUNTIME_IMPL-01.md Pipeline Step 3, INV-L1-001 through INV-L1-005 |

**Purpose:** Validate all five Layer 1 invariants before proceeding to
transformation.

**Behavior:**
- Check INV-L1-001: Every Sentence belongs to exactly one Paragraph.
- Check INV-L1-002: Every Paragraph belongs to exactly one Section.
- Check INV-L1-003: Sum of Section word_counts equals total_word_count.
- Check INV-L1-004: Sum of Sentence word_counts equals total_word_count.
- Check INV-L1-005: total_word_count > 0.
- Write validation results to VALIDATION_REPORT (Layer 1 section).
- If any invariant fails, halt with error diagnostic identifying the failing
  invariant.

**Required Inputs:**

| Artifact Key | Format | Source |
|---|---|---|
| PARSED_DOCUMENT | JSON | Step 2 (PARSE-001) |

**Produces:**

| Artifact Key | Format | Description |
|---|---|---|
| VALIDATION_REPORT | Markdown (partial) | Layer 1 validation results |

**Result Meta Key:** `VAL_L1_RESULT`

**Routing:**
- onsuccess: step 4 (extract_key_points)
- on_failure: halt workflow with StructureError

---

### Step 4: extract_key_points

| Property | Value |
|---|---|
| Step Name | extract_key_points |
| Step ID | STEP-EXT-001 |
| Step Type | Prompt (prompt-driven) |
| Role Policy | architect_standard |
| Source Module | TransformationEngine |
| Trace | RUNTIME_IMPL-01.md Pipeline Step 4, COMPOSITION_SPEC STEP-EXT-001 |

**Purpose:** Identify the most important sentences from the parsed document
and assign importance scores.

**Behavior:**
- Construct prompt containing full ParsedDocument (all Sentences).
- Instruct coder to:
  - Identify most important sentences per section.
  - Assign importance_score in [0.0, 1.0].
  - Ensure at least 3 key points for documents with > 5 sentences.
  - Cover all sections (unless section has < 2 sentences).
- Parse coder response into KeyPoint[] components.
- Validate INV-L2-001 (each KeyPoint references at least one Sentence).
- Validate INV-L2-002 (importance_score in [0.0, 1.0]).

**Required Inputs:**

| Artifact Key | Format | Source |
|---|---|---|
| PARSED_DOCUMENT | JSON | Step 2 (PARSE-001) |

**Produces:**

| Artifact Key | Format | Description |
|---|---|---|
| KEY_POINTS_DATA | JSON | Array of KeyPoint components |

**Result Meta Key:** `KEY_POINTS_DATA`

**Routing:**
- onsuccess: step 5 (remove_redundancy)
- on_reject_refine: step 4 itself (retry extract_key_points)
  - artifact: KEY_POINTS_DATA
  - max_iterations: 2
  - exhausted_failure_code: "EXT_KEYPOINTS_RETRY_EXHAUSTED"
  - exhausted_failure_class: "HUMAN_RETRY_REQUIRED"

**Stage Invariant:**
- KeyPoint set must cover all major sections (no section unrepresented unless
  it contains fewer than 2 sentences).

---

### Step 5: remove_redundancy

| Property | Value |
|---|---|
| Step Name | remove_redundancy |
| Step ID | STEP-RED-001 |
| Step Type | Prompt (prompt-driven) |
| Role Policy | architect_standard |
| Source Module | TransformationEngine |
| Trace | RUNTIME_IMPL-01.md Pipeline Step 5, COMPOSITION_SPEC STEP-RED-001 |

**Purpose:** Identify and cluster sentences expressing the same idea,
selecting the most concise representative from each cluster.

**Behavior:**
- Construct prompt containing all Sentences from Layer 1.
- Instruct coder to:
  - Compare all sentence pairs for semantic similarity.
  - Group similar sentences into RedundancyCluster components.
  - Select most concise and clear sentence as representative.
- Parse coder response into RedundancyCluster[] components.
- Validate INV-L2-003 (cluster sentences from same Section).
- Validate INV-L2-004 (representative_ref is a member of member_sentence_refs).

**Required Inputs:**

| Artifact Key | Format | Source |
|---|---|---|
| PARSED_DOCUMENT | JSON | Step 2 (PARSE-001) |
| KEY_POINTS_DATA | JSON | Step 4 (STEP-EXT-001) |

**Produces:**

| Artifact Key | Format | Description |
|---|---|---|
| REDUNDANCY_CLUSTERS | JSON | Array of RedundancyCluster components |

**Result Meta Key:** `REDUNDANCY_CLUSTERS`

**Routing:**
- onsuccess: step 6 (preserve_meaning)
- on_reject_refine: step 5 itself (retry remove_redundancy)
  - artifact: REDUNDANCY_CLUSTERS
  - max_iterations: 2
  - exhausted_failure_code: "REDUNDANCY_RETRY_EXHAUSTED"
  - exhausted_failure_class: "HUMAN_RETRY_REQUIRED"

**Stage Invariant:**
- No two KeyPoints should reference sentences that belong to the same
  RedundancyCluster. If they do, merge the KeyPoints.

---

### Step 6: preserve_meaning

| Property | Value |
|---|---|
| Step Name | preserve_meaning |
| Step ID | STEP-MEAN-001 |
| Step Type | Prompt (prompt-driven) |
| Role Policy | architect_standard |
| Source Module | TransformationEngine |
| Trace | RUNTIME_IMPL-01.md Pipeline Step 6, COMPOSITION_SPEC STEP-MEAN-001 |

**Purpose:** Compose summary_segment ContentBlocks from KeyPoints and source
Sentences, ensuring the core message is captured without introducing external
information.

**Behavior:**
- Construct prompt containing:
  - All KeyPoint components (with importance scores).
  - All RedundancyCluster components (with representatives).
  - DocumentMetadata (for language and structure context).
- Instruct coder to:
  - Compose summary_segment ContentBlocks from KeyPoints and source Sentences.
  - Ensure core message (highest-importance KeyPoints) is present.
  - Verify no paraphrase introduces unsupported claims.
  - Maintain introduction -> body -> conclusion flow.
- Parse coder response into ContentBlock[] components.
- Validate INV-L2-005 (source_refs valid).
- Validate INV-L2-006 (no external info introduced).

**Required Inputs:**

| Artifact Key | Format | Source |
|---|---|---|
| KEY_POINTS_DATA | JSON | Step 4 (STEP-EXT-001) |
| REDUNDANCY_CLUSTERS | JSON | Step 5 (STEP-RED-001) |
| PARSED_DOCUMENT | JSON | Step 2 (PARSE-001) |

**Produces:**

| Artifact Key | Format | Description |
|---|---|---|
| CONTENT_BLOCKS | JSON | Array of ContentBlock components (draft) |

**Result Meta Key:** `CONTENT_BLOCKS`

**Routing:**
- onsuccess: step 7 (maintain_structure)
- on_reject_refine: step 6 itself (retry preserve_meaning)
  - artifact: CONTENT_BLOCKS
  - max_iterations: 2
  - exhausted_failure_code: "MEANING_RETRY_EXHAUSTED"
  - exhausted_failure_class: "HUMAN_RETRY_REQUIRED"

**Stage Invariant:**
- ContentBlocks with block_type "summary_segment" must contain references
  from every section_type in the source document (introduction, body,
  conclusion), assuming those sections exist.

---

### Step 7: maintain_structure

| Property | Value |
|---|---|
| Step Name | maintain_structure |
| Step ID | STEP-STR-001 |
| Step Type | Action (action-driven) |
| Source Module | TransformationEngine |
| Trace | RUNTIME_IMPL-01.md Pipeline Step 7, COMPOSITION_SPEC STEP-STR-001 |

**Purpose:** Ensure output preserves the logical flow of the original document
by reordering content blocks, inserting structural bridges, and enforcing
compression constraint.

**Behavior:**
- Receive ordered ContentBlock[] from STEP-MEAN-001.
- Verify ContentBlock positions match Section positions from Layer 1.
- Reorder blocks to maintain introduction -> body -> conclusion flow.
- Insert structural_bridge ContentBlocks if transitions are needed between
  sections (deterministic template-based text).
- Compute final word counts per block and aggregate for output.
- Check C-001: total summary_segment word count <= 20% of total_word_count.
  - If exceeded, trim lowest-importance ContentBlocks until constraint is met.

**Required Inputs:**

| Artifact Key | Format | Source |
|---|---|---|
| CONTENT_BLOCKS | JSON | Step 6 (STEP-MEAN-001) |
| PARSED_DOCUMENT | JSON | Step 2 (PARSE-001) |

**Produces:**

| Artifact Key | Format | Description |
|---|---|---|
| CONTENT_BLOCKS | JSON | Final ordered ContentBlock[] |

**Result Meta Key:** `STRUCTURE_RESULT`

**Error Handling:**

| Error Condition | Error Type | Recovery |
|---|---|---|
| Compression ratio exceeded after trim | ConstraintViolationError | Halt with diagnostic |

---

### Step 8: validate_output

| Property | Value |
|---|---|
| Step Name | validate_output |
| Step ID | VAL-OUT-001 |
| Step Type | Action (action-driven) |
| Source Module | StructureValidator |
| Trace | RUNTIME_IMPL-01.md Pipeline Step 8, C-001, C-002, C-003 |

**Purpose:** Perform final validation of all constraints (C-001, C-002, C-003)
and Layer 3 invariants before rendering output. Assemble the OutputDocument.

**Behavior:**
- Validate C-001: compression_ratio = output_word_count / total_word_count
  <= 0.20.
- Validate C-002: output language matches source language.
- Validate C-003: every ContentBlock source_refs traces to Layer 1 Sentences.
- Validate INV-L3-001: OutputMetadata.language equals DocumentMetadata.language.
- Validate INV-L3-002: All content_blocks have valid references to Layer 2
  components.
- Validate INV-L3-003: Validation rules include all required constraints.
- Assemble OutputDocument with OutputMetadata, content_blocks, and
  validation_rules.
- Update VALIDATION_REPORT with Layer 2/3 results.
- If any constraint or invariant fails, halt with appropriate diagnostic.

**Required Inputs:**

| Artifact Key | Format | Source |
|---|---|---|
| CONTENT_BLOCKS | JSON | Step 7 (STEP-STR-001) |
| PARSED_DOCUMENT | JSON | Step 2 (PARSE-001) |
| KEY_POINTS_DATA | JSON | Step 4 (STEP-EXT-001) |

**Produces:**

| Artifact Key | Format | Description |
|---|---|---|
| OUTPUT_ASSEMBLY | JSON | OutputDocument with metadata and validation rules |
| VALIDATION_REPORT | Markdown (complete) | Full validation results |

**Result Meta Key:** `VAL_OUT_RESULT`

**Routing:**
- onsuccess: step 9 (render_output)
- on_failure: halt workflow with ConstraintViolationError or ProvenanceError

---

### Step 9: render_output

| Property | Value |
|---|---|
| Step Name | render_output |
| Step ID | RENDER-001 |
| Step Type | Action (action-driven) |
| Source Module | OutputRenderer |
| Trace | RUNTIME_IMPL-01.md Pipeline Step 9, MAP-OM-001, MAP-OM-002 |

**Purpose:** Render the final output artifacts (CONDENSED_SUMMARY and
KEY_POINTS_LIST) from the validated OutputDocument.

**Behavior:**

**CONDENSED_SUMMARY (MAP-OM-001):**
- Select all ContentBlocks with block_type "summary_segment".
- Order by position (ascending).
- Concatenate content into prose form.
- Preserve logical structure: introduction, body, conclusion.
- Compute compression_ratio = output_word_count / total_word_count.
- Write Markdown file with YAML frontmatter.

**KEY_POINTS_LIST (MAP-OM-002):**
- Select all KeyPoint components from Layer 2.
- Order by importance_score descending.
- Format each point as numbered list entry with importance_score annotation.
- Write Markdown file with YAML frontmatter.

**Required Inputs:**

| Artifact Key | Format | Source |
|---|---|---|
| OUTPUT_ASSEMBLY | JSON | Step 8 (VAL-OUT-001) |
| CONTENT_BLOCKS | JSON | Step 7 (STEP-STR-001) |
| KEY_POINTS_DATA | JSON | Step 4 (STEP-EXT-001) |

**Produces:**

| Artifact Key | Format | Description |
|---|---|---|
| CONDENSED_SUMMARY | Markdown | Prose summary with YAML frontmatter |
| KEY_POINTS_LIST | Markdown | Structured list with YAML frontmatter |

**Result Meta Key:** `RENDER_RESULT`

---

## Routing Logic

### Forward Routing (onsuccess)

The primary execution path follows a linear pipeline:

```
load_input
    | (onsuccess)
    v
parse_document
    | (onsuccess)
    v
validate_layer_1
    | (onsuccess)
    v
extract_key_points
    | (onsuccess)
    v
remove_redundancy
    | (onsuccess)
    v
preserve_meaning
    | (onsuccess)
    v
maintain_structure
    | (onsuccess)
    v
validate_output
    | (onsuccess)
    v
render_output
    | (onsuccess)
    v
[workflow complete]
```

### Refinement Routing (on_reject_refine)

Three prompt-driven steps have self-refinement loops:

| Step | Refine Target | Max Iterations | Exhaustion Code | Exhaustion Class |
|---|---|---|---|---|
| extract_key_points (step 4) | itself | 2 | EXT_KEYPOINTS_RETRY_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| remove_redundancy (step 5) | itself | 2 | REDUNDANCY_RETRY_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| preserve_meaning (step 6) | itself | 2 | MEANING_RETRY_EXHAUSTED | HUMAN_RETRY_REQUIRED |

Each refinement loop follows this pattern:
1. Step produces output artifact.
2. Validation (built into the step or next step) detects invariant violation.
3. If violation found, the step is re-invoked with the validation feedback.
4. After max_iterations (2) failures, workflow halts with HUMAN_RETRY_REQUIRED.

### Failure Handling

| Step | Failure Condition | Action |
|---|---|---|
| load_input | File not found, empty, or binary | Halt immediately |
| parse_document | No parseable sentences | Halt immediately |
| validate_layer_1 | Any INV-L1 violation | Halt with diagnostic |
| extract_key_points | Retry exhausted (2 attempts) | Halt with HUMAN_RETRY_REQUIRED |
| remove_redundancy | Retry exhausted (2 attempts) | Halt with HUMAN_RETRY_REQUIRED |
| preserve_meaning | Retry exhausted (2 attempts) | Halt with HUMAN_RETRY_REQUIRED |
| maintain_structure | Compression ratio exceeded after trim | Halt with diagnostic |
| validate_output | Any constraint violation (C-001/C-002/C-003) | Halt with diagnostic |
| render_output | File write failure | Halt with diagnostic |

---

## Artifact Flow

### Complete Artifact Flow Diagram

```
SOURCE_TEXT_FILE (external input)
    |
    v
[Step 1: load_input] --> PARSED_DOCUMENT (partial: raw text + metadata)
    |
    v
[Step 2: parse_document] --> PARSED_DOCUMENT (complete: Layer 1 tree)
    |
    v
[Step 3: validate_layer_1] --> VALIDATION_REPORT (Layer 1 section)
    |
    v
[Step 4: extract_key_points] --> KEY_POINTS_DATA
    |
    v
[Step 5: remove_redundancy] --> REDUNDANCY_CLUSTERS
    |   (requires PARSED_DOCUMENT + KEY_POINTS_DATA)
    |
    v
[Step 6: preserve_meaning] --> CONTENT_BLOCKS (draft)
    |   (requires KEY_POINTS_DATA + REDUNDANCY_CLUSTERS + PARSED_DOCUMENT)
    |
    v
[Step 7: maintain_structure] --> CONTENT_BLOCKS (final, ordered)
    |   (requires CONTENT_BLOCKS + PARSED_DOCUMENT)
    |
    v
[Step 8: validate_output] --> OUTPUT_ASSEMBLY + VALIDATION_REPORT (complete)
    |   (requires CONTENT_BLOCKS + PARSED_DOCUMENT + KEY_POINTS_DATA)
    |
    v
[Step 9: render_output] --> CONDENSED_SUMMARY + KEY_POINTS_LIST
        (requires OUTPUT_ASSEMBLY + CONTENT_BLOCKS + KEY_POINTS_DATA)
```

### Artifact Production and Consumption Summary

| Artifact Key | Produced By | Consumed By |
|---|---|---|
| SOURCE_TEXT_FILE | External caller | Step 1 (load_input) |
| PARSED_DOCUMENT | Step 1 (load_input), Step 2 (parse_document) | Steps 2, 3, 4, 5, 6, 7, 8 |
| VALIDATION_REPORT | Step 3 (validate_layer_1), Step 8 (validate_output) | Workflow runner |
| KEY_POINTS_DATA | Step 4 (extract_key_points) | Steps 5, 6, 8, 9 |
| REDUNDANCY_CLUSTERS | Step 5 (remove_redundancy) | Step 6 (preserve_meaning) |
| CONTENT_BLOCKS | Step 6 (preserve_meaning), Step 7 (maintain_structure) | Steps 7, 8, 9 |
| OUTPUT_ASSEMBLY | Step 8 (validate_output) | Step 9 (render_output) |
| CONDENSED_SUMMARY | Step 9 (render_output) | External consumer |
| KEY_POINTS_LIST | Step 9 (render_output) | External consumer |

---

## Review Loops

### Quality Gates

The workflow implements quality assurance at multiple levels:

**1. Layer 1 Validation Gate (Step 3)**

This is a hard gate. All five Layer 1 invariants must pass before the
transformation pipeline begins. No retry is possible because parsing is
deterministic -- if invariants fail, the input is fundamentally unparseable.

- Gate type: Hard halt
- Retry allowed: No
- Failure action: Halt workflow with StructureError

**2. Key Point Extraction Review (Step 4)**

The LLM output is validated against INV-L2-001 and INV-L2-002. If validation
fails, the step retries with feedback about the violation.

- Gate type: Self-refinement loop
- Retry allowed: Yes (max 2 iterations)
- Validation checks: INV-L2-001 (sentence references), INV-L2-002 (score range)
- Exhaustion action: Halt with HUMAN_RETRY_REQUIRED

**3. Redundancy Removal Review (Step 5)**

The LLM output is validated against INV-L2-003 and INV-L2-004. If validation
fails, the step retries with feedback.

- Gate type: Self-refinement loop
- Retry allowed: Yes (max 2 iterations)
- Validation checks: INV-L2-003 (same section), INV-L2-004 (member reference)
- Exhaustion action: Halt with HUMAN_RETRY_REQUIRED

**4. Meaning Preservation Review (Step 6)**

The LLM output is validated against INV-L2-005 and INV-L2-006. If validation
fails, the step retries with feedback.

- Gate type: Self-refinement loop
- Retry allowed: Yes (max 2 iterations)
- Validation checks: INV-L2-005 (valid refs), INV-L2-006 (no external info)
- Exhaustion action: Halt with HUMAN_RETRY_REQUIRED

**5. Output Validation Gate (Step 8)**

Final hard gate. All constraints (C-001, C-002, C-003) and Layer 3 invariants
must pass. No retry because this is deterministic validation.

- Gate type: Hard halt
- Retry allowed: No
- Validation checks: C-001, C-002, C-003, INV-L3-001, INV-L3-002, INV-L3-003
- Failure action: Halt workflow with ConstraintViolationError or ProvenanceError

### Review Loop Summary

| Step | Loop Type | Max Iterations | Exhaustion Code | Exhaustion Class |
|---|---|---|---|---|
| extract_key_points | Self-refine | 2 | EXT_KEYPOINTS_RETRY_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| remove_redundancy | Self-refine | 2 | REDUNDANCY_RETRY_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| preserve_meaning | Self-refine | 2 | MEANING_RETRY_EXHAUSTED | HUMAN_RETRY_REQUIRED |

---

## Human Approval

### Approval Points

The generated workflow has zero mandatory human approval points during
normal execution. All quality gates are automated (validation actions or
self-refinement loops).

Human intervention is required only when:

| Trigger | Condition | Action Required |
|---|---|---|
| Retry exhaustion | Any prompt step exceeds max_iterations (2) | Human reviews LLM output quality and decides: fix input, adjust parameters, or abort |
| Layer 1 validation failure | Input document is structurally invalid | Human provides valid input or fixes source file |
| Constraint violation | C-001/C-002/C-003 fails at step 8 | Human reviews and decides: adjust compression threshold, accept partial output, or abort |
| File I/O error | Input file inaccessible or output directory unwritable | Human resolves filesystem permissions |

### Notification Configuration

| Step | Notifications Enabled | Description |
|---|---|---|
| load_input | false | Action step, no notification needed |
| parse_document | false | Action step, no notification needed |
| validate_layer_1 | true | Hard gate; notify on failure |
| extract_key_points | true | Prompt step; notify on retry exhaustion |
| remove_redundancy | true | Prompt step; notify on retry exhaustion |
| preserve_meaning | true | Prompt step; notify on retry exhaustion |
| maintain_structure | false | Action step, no notification needed |
| validate_output | true | Hard gate; notify on failure |
| render_output | true | Final output; notify on completion or failure |

---

## Self-Validation

### Routing Validity Check

| Check | Status | Notes |
|---|---|---|
| No routing cycles | PASS | All onsuccess routes move forward in pipeline order. Refinement loops (steps 4, 5, 6) target themselves, not prior steps. |
| No dangling references | PASS | All onsuccess and on_reject_refine targets reference defined step names. |
| All artifacts produced before consumed | PASS | PARSED_DOCUMENT produced in steps 1-2 before consumed in steps 3-8. KEY_POINTS_DATA produced in step 4 before consumed in steps 5-9. REDUNDANCY_CLUSTERS produced in step 5 before consumed in step 6. CONTENT_BLOCKS produced in steps 6-7 before consumed in steps 7-9. OUTPUT_ASSEMBLY produced in step 8 before consumed in step 9. |
| All inputs have sources | PASS | SOURCE_TEXT_FILE from external caller. All other inputs trace to upstream steps. |
| All outputs have consumers | PASS | PARSED_DOCUMENT consumed by 7 downstream steps. KEY_POINTS_DATA consumed by 4 downstream steps. REDUNDANCY_CLUSTERS consumed by step 6. CONTENT_BLOCKS consumed by steps 7-9. OUTPUT_ASSEMBLY consumed by step 9. CONDENSED_SUMMARY and KEY_POINTS_LIST are final outputs. |
| Review loops properly configured | PASS | Three prompt steps have self-refine loops with max_iterations=2, exhaustion codes, and exhaustion classes. |
| No undefined artifacts referenced | PASS | All artifact keys match ARTIFACT_CONTRACT-01.md definitions. |
| Follows runtime implementation | PASS | Step sequence matches RUNTIME_IMPL-01.md pipeline execution sequence (steps 1-9 in order). |

### Constraint Coverage Check

| Constraint | Where Checked | Action on Failure |
|---|---|---|
| C-001 (compression <= 20%) | Step 7 (maintain_structure) -- trim; Step 8 (validate_output) -- validate | Trim then validate; halt if still exceeded |
| C-002 (language match) | Step 8 (validate_output) | Halt with LanguageMismatchError |
| C-003 (no external info) | Step 6 (preserve_meaning) -- validate; Step 8 (validate_output) -- validate | Retry in step 6; halt if fails at step 8 |

### Invariant Coverage Check

| Invariant | Where Checked | Step |
|---|---|---|
| INV-L1-001 | validate_layer_1 | Step 3 |
| INV-L1-002 | validate_layer_1 | Step 3 |
| INV-L1-003 | validate_layer_1 | Step 3 |
| INV-L1-004 | validate_layer_1 | Step 3 |
| INV-L1-005 | validate_layer_1 | Step 3 |
| INV-L2-001 | extract_key_points | Step 4 |
| INV-L2-002 | extract_key_points | Step 4 |
| INV-L2-003 | remove_redundancy | Step 5 |
| INV-L2-004 | remove_redundancy | Step 5 |
| INV-L2-005 | preserve_meaning | Step 6 |
| INV-L2-006 | preserve_meaning | Step 6 |
| INV-L3-001 | validate_output | Step 8 |
| INV-L3-002 | validate_output | Step 8 |
| INV-L3-003 | validate_output | Step 8 |

### Traceability Check

| Section | Source Artifact | Trace Points |
|---|---|---|
| Step sequence (9 steps) | RUNTIME_IMPL-01.md Pipeline Execution Sequence | Steps 1-9 match Orders 1-9 |
| Artifact flow | ARTIFACT_CONTRACT-01.md Dependency Graph | All artifacts and dependencies mapped |
| Review loops | RUNTIME_IMPL-01.md Error Handling (LLM retry up to 2) | Max iterations = 2 for prompt steps |
| Constraints | COMPOSITION_SPEC-01.md Constraints Section | C-001, C-002, C-003 all covered |
| Invariants | COMPOSITION_SPEC-01.md Invariants Summary | All 14 invariants assigned to steps |
| Error handling | RUNTIME_IMPL-01.md Error Handling table | All error conditions mapped to steps |

### No Invented Scope Check

| Check | Status | Notes |
|---|---|---|
| All steps from runtime implementation | PASS | 9 steps match exactly |
| No additional steps added | PASS | No steps beyond those in RUNTIME_IMPL-01.md |
| No features beyond declared scope | PASS | No extra capabilities introduced |
| ASCII-only output | PASS | No em-dashes, curly quotes, or Unicode |
| YAML frontmatter correct | PASS | doc_type: "step_sequence", identity_locked: true |
