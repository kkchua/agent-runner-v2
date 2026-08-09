---
doc_type: "operational_workflow"
lifecycle_status: "draft"
domain: "ar_meta_builder"
step_count: 21
action_count: 3
prompt_step_count: 18
workflow_pattern: "meta_meta_builder"
---

# Operational Workflow

## Overview

This document defines the operational workflow for the AR Meta Builder v1
meta-meta builder. The meta-meta builder is a 9-phase, 21-step workflow that
produces a complete workflow package for the codebase_to_meta domain. The
generated workflow package, when deployed and executed, transforms codebase
documentation into audience-specific Rich Markdown meta content files.

**Workflow pattern:** meta_meta_builder

The meta_meta_builder pattern is characterized by:
- Layered artifact production: each phase produces a layer of the composition
  system specification (Layer 1 component schema, Layer 2 composition format,
  Layer 3 output format).
- Test-driven quality: Phase 1 establishes acceptance criteria that gate all
  subsequent phases.
- Gatekeep-review-refine loops: each layer passes through gatekeep review
  before advancing to the next phase.
- v3 innovation layers: Phases 6 and 7 produce a composition standard and a
  self-contained meta composition spec, elevating the output beyond a single
  workflow package.
- Deterministic validation: Phase 8 includes a deterministic validation action
  that verifies package integrity before human review.
- Promotion lifecycle: Phase 9 copies the validated package to the workflows/
  directory for deployment.

**Step classification summary:**

| Classification | Count | Steps |
|---|---|---|
| Prompt steps | 18 | 01-15, 17, 18, 19 |
| Action steps | 3 | 16, 20, 21 |
| Total steps | 21 | 01-21 |

**Traceability:** All 21 steps trace to the input specification
(codebase_to_meta_v1.md) and the test criteria (TEST_CRITERIA.md). The 9
phases correspond to the 9 test criteria sections. The step sequence is
derived from the composition system specification's layered architecture and
the v3 innovation phases (composition standard and meta composition spec).

---

## Workflow Phases

The workflow is organized into 9 phases. Each phase produces one or more
layered artifacts that feed subsequent phases. Phases are sequential; a phase
cannot begin until all preceding phases have completed successfully.

### Phase 1: Foundation (TDD Loop)

**Purpose:** Establish the acceptance criteria that all subsequent phases are
measured against. This phase implements a test-driven development loop:
generate criteria, review them, and refine if rejected.

**Steps:** 3 (Steps 01, 02, 03)

| Step | Name | Type | Purpose |
|---|---|---|---|
| 01 | generate_test_criteria | prompt | Produce the TEST_CRITERIA_FILE with 117 acceptance criteria covering all 9 phases |
| 02 | review_test_criteria | prompt | Review criteria against spec for completeness, specificity, and traceability |
| 03 | refine_test_criteria | prompt | Address reviewer feedback and revise criteria (conditional, max 2 iterations) |

**Artifacts produced:**
- TEST_CRITERIA_FILE (by Step 01, revised by Step 03)
- REVIEW_TEST_CRITERIA_FILE (by Step 02)

**Test criteria coverage:** TC-001 through TC-008

### Phase 2: Component Schema

**Purpose:** Define the Layer 1 component schema -- the foundational building
block library used to compose workflow definitions within the ar_meta_builder
domain. Covers 8 universal component types with 5 domain-active types.

**Steps:** 2 (Steps 04, 05)

| Step | Name | Type | Purpose |
|---|---|---|---|
| 04 | generate_component_schema | prompt | Produce COMPONENT_SCHEMA_FILE defining all 8 component types |
| 05 | gatekeep_component_schema | prompt | Gatekeep review against criteria TC-009 through TC-020 |

**Artifacts produced:**
- COMPONENT_SCHEMA_FILE (by Step 04)
- GATEKEEP_COMPONENT_SCHEMA_FILE (by Step 05)

**Test criteria coverage:** TC-009 through TC-020

### Phase 3: Composition Format

**Purpose:** Define the Layer 2 composition format -- how component instances
from Layer 1 are bound together into compositions. Covers binding rules,
override mechanisms, placeholder resolution, and ordering constraints.

**Steps:** 2 (Steps 06, 07)

| Step | Name | Type | Purpose |
|---|---|---|---|
| 06 | generate_composition_format | prompt | Produce COMPOSITION_FORMAT_FILE with 8 binding rules and 6 workflow patterns |
| 07 | gatekeep_composition_format | prompt | Gatekeep review against criteria TC-022 through TC-034 |

**Artifacts produced:**
- COMPOSITION_FORMAT_FILE (by Step 06)
- GATEKEEP_COMPOSITION_FORMAT_FILE (by Step 07)

**Test criteria coverage:** TC-022 through TC-034

### Phase 4: Output Format

**Purpose:** Define the Layer 3 output format -- concrete output file
structure, resolution rules, quality requirements, and downstream extraction
contracts for the generated workflow package.

**Steps:** 2 (Steps 08, 09)

| Step | Name | Type | Purpose |
|---|---|---|---|
| 08 | generate_output_format | prompt | Produce OUTPUT_FORMAT_FILE with 7 resolution rules and 8 quality requirements |
| 09 | gatekeep_output_format | prompt | Gatekeep review against criteria TC-036 through TC-046 |

**Artifacts produced:**
- OUTPUT_FORMAT_FILE (by Step 08)
- GATEKEEP_OUTPUT_FORMAT_FILE (by Step 09)

**Test criteria coverage:** TC-036 through TC-046

### Phase 5: Operational Workflow

**Purpose:** Define the complete operational workflow for the generated
codebase_to_meta workflow -- 5 phases, step sequence, routing, action step
definitions, and artifact declarations.

**Steps:** 2 (Steps 10, 11)

| Step | Name | Type | Purpose |
|---|---|---|---|
| 10 | generate_operational_workflow | prompt | Produce OPERATIONAL_WORKFLOW_FILE for the generated workflow's 5-phase structure |
| 11 | gatekeep_operational_workflow | prompt | Gatekeep review against criteria TC-048 through TC-061 |

**Artifacts produced:**
- GENERATED_OPERATIONAL_WORKFLOW_FILE (by Step 10)
- GATEKEEP_OPERATIONAL_WORKFLOW_FILE (by Step 11)

**Test criteria coverage:** TC-048 through TC-061

### Phase 6: Composition Standard (v3 Innovation)

**Purpose:** Produce a composition standard document that defines the schema
sections, component type expectations, naming conventions, and extensibility
model for the generated workflow package. This is a v3 innovation that
elevates the output beyond a single workflow package.

**Steps:** 2 (Steps 12, 13)

| Step | Name | Type | Purpose |
|---|---|---|---|
| 12 | generate_composition_standard | prompt | Produce COMPOSITION_STANDARD_FILE with standard_name, standard_version, component_type_count |
| 13 | gatekeep_composition_standard | prompt | Gatekeep review against criteria TC-063 through TC-069 |

**Artifacts produced:**
- COMPOSITION_STANDARD_FILE (by Step 12)
- GATEKEEP_COMPOSITION_STANDARD_FILE (by Step 13)

**Test criteria coverage:** TC-063 through TC-069

### Phase 7: Meta Composition Spec (v3 Innovation)

**Purpose:** Produce a self-contained meta composition specification that
consolidates all upstream layered documents (component schema, composition
format, output format, operational requirements) into a single reference
document. This enables downstream consumers to understand the domain without
referencing the original bootstrap spec.

**Steps:** 1 (Step 14)

| Step | Name | Type | Purpose |
|---|---|---|---|
| 14 | generate_meta_composition_spec | prompt | Produce META_COMPOSITION_SPEC_FILE with 5 consolidated sections |

**Artifacts produced:**
- META_COMPOSITION_SPEC_FILE (by Step 14)

**Test criteria coverage:** TC-071 through TC-077

### Phase 8: Package Assembly

**Purpose:** Assemble the complete workflow package from all upstream
artifacts. Generate workflow.toml, context_extensions.py, actions.py, prompt
templates, audience definitions, and README. Validate the package
deterministically before human review.

**Steps:** 5 (Steps 15, 16, 17, 18, 19)

| Step | Name | Type | Purpose |
|---|---|---|---|
| 15 | generate_package | prompt | Produce all workflow package files (workflow.toml, actions.py, context_extensions.py, prompts/, audiences/, README.md) |
| 16 | validate_package_deterministic | action | Deterministic validation: TOML validity, Python syntax, artifact key coverage, placeholder consistency |
| 17 | gatekeep_package | prompt | Gatekeep review against criteria TC-078 through TC-099 |
| 18 | review_package | prompt | Detailed review of package quality, completeness, and traceability |
| 19 | refine_package | prompt | Address review feedback and revise package files (conditional, max 2 iterations) |

**Artifacts produced:**
- WORKFLOW_MANIFEST_FILE (by Step 15)
- WORKFLOW_EXTENSIONS_FILE (by Step 15)
- WORKFLOW_ACTIONS_FILE (by Step 15)
- PROMPT_TEMPLATE_FILES (by Step 15)
- AUDIENCE_DEFINITION_FILES (by Step 15)
- WORKFLOW_README_FILE (by Step 15)
- RUNTIME_SPEC_FILE (by Step 15)
- VALIDATION_REPORT_FILE (by Step 16)
- GATEKEEP_PACKAGE_FILE (by Step 17)
- REVIEW_PACKAGE_FILE (by Step 18)

**Test criteria coverage:** TC-078 through TC-099

### Phase 9: Promotion

**Purpose:** Copy the validated workflow package to the workflows/ directory
under the global runner home. Record the promotion path and final completion
status.

**Steps:** 2 (Steps 20, 21)

| Step | Name | Type | Purpose |
|---|---|---|---|
| 20 | promote_workflow_package | action | Copy package to workflows/ar_meta_builder_v1/ and record WORKFLOW_PACKAGE_DIR_FILE |
| 21 | step_completion | action | Record final outcome, artifact summary, and completion status |

**Artifacts produced:**
- WORKFLOW_PACKAGE_DIR_FILE (by Step 20)
- COMPLETION_RECORD_FILE (by Step 21)

**Test criteria coverage:** TC-100 through TC-106

---

## Step Sequence

The following table defines the complete 21-step sequence with types, routing,
and artifact flows.

| Step # | Step Name | Type | Purpose | Required Inputs | Produces | onsuccess | on_reject_refine |
|---|---|---|---|---|---|---|---|
| 01 | generate_test_criteria | prompt | Produce acceptance criteria for all 9 phases | WORKFLOW_SPEC_FILE | TEST_CRITERIA_FILE | review_test_criteria | -- |
| 02 | review_test_criteria | prompt | Review criteria for completeness and traceability | TEST_CRITERIA_FILE, WORKFLOW_SPEC_FILE | REVIEW_TEST_CRITERIA_FILE | generate_component_schema | refine_test_criteria (max 2) |
| 03 | refine_test_criteria | prompt | Revise criteria addressing reviewer feedback | TEST_CRITERIA_FILE, REVIEW_TEST_CRITERIA_FILE, WORKFLOW_SPEC_FILE | TEST_CRITERIA_FILE | review_test_criteria | -- |
| 04 | generate_component_schema | prompt | Define 8 universal component types | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE | COMPONENT_SCHEMA_FILE | gatekeep_component_schema | -- |
| 05 | gatekeep_component_schema | prompt | Gatekeep component schema against criteria | COMPONENT_SCHEMA_FILE, TEST_CRITERIA_FILE, WORKFLOW_SPEC_FILE | GATEKEEP_COMPONENT_SCHEMA_FILE | generate_composition_format | generate_component_schema (max 2) |
| 06 | generate_composition_format | prompt | Define 8 binding rules and 6 workflow patterns | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE | COMPOSITION_FORMAT_FILE | gatekeep_composition_format | -- |
| 07 | gatekeep_composition_format | prompt | Gatekeep composition format against criteria | COMPOSITION_FORMAT_FILE, TEST_CRITERIA_FILE, WORKFLOW_SPEC_FILE, COMPONENT_SCHEMA_FILE | GATEKEEP_COMPOSITION_FORMAT_FILE | generate_output_format | generate_composition_format (max 2) |
| 08 | generate_output_format | prompt | Define 7 resolution rules and 8 quality requirements | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE | OUTPUT_FORMAT_FILE | gatekeep_output_format | -- |
| 09 | gatekeep_output_format | prompt | Gatekeep output format against criteria | OUTPUT_FORMAT_FILE, TEST_CRITERIA_FILE, WORKFLOW_SPEC_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE | GATEKEEP_OUTPUT_FORMAT_FILE | generate_operational_workflow | generate_output_format (max 2) |
| 10 | generate_operational_workflow | prompt | Define 5-phase generated workflow with step sequence | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE | GENERATED_OPERATIONAL_WORKFLOW_FILE | gatekeep_operational_workflow | -- |
| 11 | gatekeep_operational_workflow | prompt | Gatekeep operational workflow against criteria | GENERATED_OPERATIONAL_WORKFLOW_FILE, TEST_CRITERIA_FILE, WORKFLOW_SPEC_FILE | GATEKEEP_OPERATIONAL_WORKFLOW_FILE | generate_composition_standard | generate_operational_workflow (max 2) |
| 12 | generate_composition_standard | prompt | Produce composition standard with extensibility model | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, GENERATED_OPERATIONAL_WORKFLOW_FILE | COMPOSITION_STANDARD_FILE | gatekeep_composition_standard | -- |
| 13 | gatekeep_composition_standard | prompt | Gatekeep composition standard against criteria | COMPOSITION_STANDARD_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE | GATEKEEP_COMPOSITION_STANDARD_FILE | generate_meta_composition_spec | generate_composition_standard (max 2) |
| 14 | generate_meta_composition_spec | prompt | Consolidate all layers into self-contained spec | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, GENERATED_OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE | META_COMPOSITION_SPEC_FILE | generate_package | -- |
| 15 | generate_package | prompt | Assemble complete workflow package files | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, GENERATED_OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, PROMPT_TEMPLATE_FILES, AUDIENCE_DEFINITION_FILES, WORKFLOW_README_FILE, RUNTIME_SPEC_FILE | validate_package_deterministic | -- |
| 16 | validate_package_deterministic | action | Deterministic package integrity validation | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, PROMPT_TEMPLATE_FILES, AUDIENCE_DEFINITION_FILES | VALIDATION_REPORT_FILE | gatekeep_package | -- |
| 17 | gatekeep_package | prompt | Gatekeep package against criteria TC-078 through TC-099 | VALIDATION_REPORT_FILE, WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, PROMPT_TEMPLATE_FILES, AUDIENCE_DEFINITION_FILES, WORKFLOW_README_FILE, RUNTIME_SPEC_FILE, TEST_CRITERIA_FILE, WORKFLOW_SPEC_FILE | GATEKEEP_PACKAGE_FILE | review_package | generate_package (max 2) |
| 18 | review_package | prompt | Detailed quality and traceability review | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, PROMPT_TEMPLATE_FILES, AUDIENCE_DEFINITION_FILES, WORKFLOW_README_FILE, RUNTIME_SPEC_FILE, TEST_CRITERIA_FILE, WORKFLOW_SPEC_FILE | REVIEW_PACKAGE_FILE | promote_workflow_package | refine_package (max 2) |
| 19 | refine_package | prompt | Revise package files addressing review feedback | REVIEW_PACKAGE_FILE, WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, PROMPT_TEMPLATE_FILES, AUDIENCE_DEFINITION_FILES, TEST_CRITERIA_FILE, WORKFLOW_SPEC_FILE | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, PROMPT_TEMPLATE_FILES, AUDIENCE_DEFINITION_FILES, WORKFLOW_README_FILE | review_package | -- |
| 20 | promote_workflow_package | action | Copy validated package to workflows/ directory | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, PROMPT_TEMPLATE_FILES, AUDIENCE_DEFINITION_FILES, WORKFLOW_README_FILE, RUNTIME_SPEC_FILE | WORKFLOW_PACKAGE_DIR_FILE | step_completion | -- |
| 21 | step_completion | action | Record final outcome and completion status | WORKFLOW_PACKAGE_DIR_FILE | COMPLETION_RECORD_FILE | -- | -- |

### Step Type Summary

| Step # | Step Name | Type | Classification |
|---|---|---|---|
| 01 | generate_test_criteria | prompt | Generation |
| 02 | review_test_criteria | prompt | Review |
| 03 | refine_test_criteria | prompt | Refinement (conditional) |
| 04 | generate_component_schema | prompt | Generation |
| 05 | gatekeep_component_schema | prompt | Gatekeep |
| 06 | generate_composition_format | prompt | Generation |
| 07 | gatekeep_composition_format | prompt | Gatekeep |
| 08 | generate_output_format | prompt | Generation |
| 09 | gatekeep_output_format | prompt | Gatekeep |
| 10 | generate_operational_workflow | prompt | Generation |
| 11 | gatekeep_operational_workflow | prompt | Gatekeep |
| 12 | generate_composition_standard | prompt | Generation (v3) |
| 13 | gatekeep_composition_standard | prompt | Gatekeep (v3) |
| 14 | generate_meta_composition_spec | prompt | Generation (v3) |
| 15 | generate_package | prompt | Assembly |
| 16 | validate_package_deterministic | action | Validation |
| 17 | gatekeep_package | prompt | Gatekeep |
| 18 | review_package | prompt | Review |
| 19 | refine_package | prompt | Refinement (conditional) |
| 20 | promote_workflow_package | action | Promotion |
| 21 | step_completion | action | Terminal |

---

## Artifact Contract

### Input Artifacts

These artifacts are external inputs to the ar_meta_builder_v1 workflow. They
are not produced by any step within this workflow.

| Artifact Key | Description | Available To |
|---|---|---|
| WORKFLOW_SPEC_FILE | The bootstrap specification (codebase_to_meta_v1.md) that defines the codebase_to_meta composition system. Contains Sections 1-6 covering domain overview, component schema, composition format, output format, operational requirements, and references. | All steps |

### Internal Artifacts

These artifacts are produced and consumed within the workflow. Each artifact
is produced by exactly one step and consumed by zero or more subsequent steps.

| Artifact Key | Description | Produced By | Consumed By |
|---|---|---|---|
| TEST_CRITERIA_FILE | Acceptance criteria document with 117 criteria across 9 phases. TC-001 through TC-117. | Step 01 (revised by Step 03) | Steps 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 17, 18, 19 |
| REVIEW_TEST_CRITERIA_FILE | Structured review of test criteria with APPROVED/REJECTED verdict per category. | Step 02 | Steps 03 |
| COMPONENT_SCHEMA_FILE | Layer 1 component schema defining 8 universal component types. | Step 04 | Steps 05, 06, 07, 08, 10, 12, 13, 14, 15 |
| GATEKEEP_COMPONENT_SCHEMA_FILE | Gatekeep verdict for component schema. | Step 05 | (terminal for phase -- no downstream consumer) |
| COMPOSITION_FORMAT_FILE | Layer 2 composition format with 8 binding rules and 6 workflow patterns. | Step 06 | Steps 07, 08, 10, 12, 14, 15 |
| GATEKEEP_COMPOSITION_FORMAT_FILE | Gatekeep verdict for composition format. | Step 07 | (terminal for phase) |
| OUTPUT_FORMAT_FILE | Layer 3 output format with 7 resolution rules and 8 quality requirements. | Step 08 | Steps 09, 10, 12, 14, 15 |
| GATEKEEP_OUTPUT_FORMAT_FILE | Gatekeep verdict for output format. | Step 09 | (terminal for phase) |
| GENERATED_OPERATIONAL_WORKFLOW_FILE | Operational workflow definition for the generated codebase_to_meta workflow (5 phases, 5 steps). | Step 10 | Steps 11, 12, 14, 15 |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | Gatekeep verdict for generated operational workflow. | Step 11 | (terminal for phase) |
| COMPOSITION_STANDARD_FILE | v3 composition standard with standard_name, standard_version, component_type_count, and extensibility model. | Step 12 | Steps 13, 14, 15 |
| GATEKEEP_COMPOSITION_STANDARD_FILE | Gatekeep verdict for composition standard. | Step 13 | (terminal for phase) |
| META_COMPOSITION_SPEC_FILE | v3 self-contained meta composition spec consolidating all layers. | Step 14 | Step 15 |
| WORKFLOW_MANIFEST_FILE | workflow.toml declaring 5 steps, 5 artifacts, routing, and step types. | Step 15 | Steps 16, 17, 18, 19, 20 |
| WORKFLOW_EXTENSIONS_FILE | context_extensions.py with artifact key registrations and hardcoded paths. | Step 15 | Steps 16, 17, 18, 19, 20 |
| WORKFLOW_ACTIONS_FILE | actions.py implementing scan_audiences and publish_meta_content. | Step 15 | Steps 16, 17, 18, 19, 20 |
| PROMPT_TEMPLATE_FILES | Prompt templates for generate, review, refine steps (3 .txt files). | Step 15 | Steps 16, 17, 18, 19, 20 |
| AUDIENCE_DEFINITION_FILES | Audience plugin files: developer.md, architect.md, executive.md. | Step 15 | Steps 16, 17, 18, 19, 20 |
| WORKFLOW_README_FILE | README.md describing workflow purpose, inputs, outputs, invocation. | Step 15 | Steps 17, 18, 19, 20 |
| RUNTIME_SPEC_FILE | Copy of WORKFLOW_SPEC_FILE placed in Specs/codebase_to_meta_v1.md. | Step 15 | Steps 17, 18, 19, 20 |
| VALIDATION_REPORT_FILE | Deterministic validation report listing all checks and pass/fail status. | Step 16 | Step 17 |
| GATEKEEP_PACKAGE_FILE | Gatekeep verdict for workflow package. | Step 17 | (terminal for phase) |
| REVIEW_PACKAGE_FILE | Detailed review of package quality and traceability. | Step 18 | Step 19 |
| WORKFLOW_PACKAGE_DIR_FILE | Absolute path to the promoted workflow package directory. | Step 20 | Step 21 |
| COMPLETION_RECORD_FILE | Final outcome record with success status and artifact summary. | Step 21 | (terminal) |

### Artifact Flow Integrity Verification

Every artifact consumed by a step is either:
1. An external input (WORKFLOW_SPEC_FILE), or
2. Produced by a preceding step in the sequence.

No dangling references exist. The artifact flow forms a directed acyclic graph
(with the exception of review-refine loops which are bounded by max_iterations).

---

## Action Specifications

Three action steps perform deterministic operations within the workflow.
Action steps execute Python code rather than LLM invocations.

### Action 1: validate_package_deterministic (Step 16)

**Type:** action
**Phase:** Phase 8 (Package Assembly)
**Purpose:** Perform deterministic validation of the generated workflow
package to verify structural integrity before human review.

**Required inputs:**
- WORKFLOW_MANIFEST_FILE (workflow.toml)
- WORKFLOW_EXTENSIONS_FILE (context_extensions.py)
- WORKFLOW_ACTIONS_FILE (actions.py)
- PROMPT_TEMPLATE_FILES (3 .txt files)
- AUDIENCE_DEFINITION_FILES (3 .md files)

**Produces:** VALIDATION_REPORT_FILE

**Validation checks performed:**

| Check ID | Check Name | Description | Severity |
|---|---|---|---|
| VP-001 | TOML validity | Parse workflow.toml and verify it is valid TOML without errors. | CRITICAL |
| VP-002 | Python syntax (context_extensions) | Parse context_extensions.py and verify it is syntactically valid Python. | CRITICAL |
| VP-003 | Python syntax (actions) | Parse actions.py and verify it is syntactically valid Python. | CRITICAL |
| VP-004 | Step count | Verify workflow.toml declares exactly 5 steps. | CRITICAL |
| VP-005 | Step type correctness | Verify scan_audiences and publish_meta_content are "action"; the other 3 are "prompt". | CRITICAL |
| VP-006 | Artifact key coverage | Verify all 5 artifact keys are declared: AUDIENCE_INVENTORY_FILE, META_CONTENT_FILE, META_INDEX_FILE, REVIEW_FILE_SUGGESTED, META_MANIFEST_FILE. | CRITICAL |
| VP-007 | Routing completeness | Verify every step has an onsuccess target. Verify exactly one step routes to step_completion. | CRITICAL |
| VP-008 | Reject loop integrity | Verify review_meta_content has on_reject_refine = refine_meta_content with max_iterations = 2 and exhaustion_code = META_CONTENT_REVIEW_EXHAUSTED. | CRITICAL |
| VP-009 | Action implementation | Verify actions.py contains scan_audiences and publish_meta_content function definitions. | CRITICAL |
| VP-010 | Prompt file existence | Verify prompts/ directory contains generate_meta_content.txt, review_meta_content.txt, and refine_meta_content.txt. | CRITICAL |
| VP-011 | Audience file existence | Verify audiences/ directory contains developer.md, architect.md, and executive.md. | CRITICAL |
| VP-012 | Audience frontmatter validity | Verify each audience .md file has valid YAML frontmatter with audience_id, label, tone, focus_areas, section_structure. | CRITICAL |
| VP-013 | Unique audience_id | Verify no two audience files declare the same audience_id. | CRITICAL |
| VP-014 | Placeholder consistency | Verify every {PLACEHOLDER} in prompt templates corresponds to a declared artifact key in workflow.toml. | HIGH |
| VP-015 | Context variable registration | Verify context_extensions.py registers CODEBASE_DOC_ROOT, META_CONTENT_ROOT, AUDIENCE_DIR. | HIGH |
| VP-016 | README existence | Verify README.md exists in the package root. | HIGH |
| VP-017 | Spec copy integrity | Verify Specs/codebase_to_meta_v1.md exists. | HIGH |

**Returns:** APPROVED when all CRITICAL checks pass. HIGH checks are reported
but do not cause rejection.

**onsuccess:** gatekeep_package (Step 17)

### Action 2: promote_workflow_package (Step 20)

**Type:** action
**Phase:** Phase 9 (Promotion)
**Purpose:** Copy the validated workflow package to the workflows/ directory
under the global runner home for deployment.

**Required inputs:**
- WORKFLOW_MANIFEST_FILE
- WORKFLOW_EXTENSIONS_FILE
- WORKFLOW_ACTIONS_FILE
- PROMPT_TEMPLATE_FILES
- AUDIENCE_DEFINITION_FILES
- WORKFLOW_README_FILE
- RUNTIME_SPEC_FILE

**Produces:** WORKFLOW_PACKAGE_DIR_FILE

**Promotion stages:**

| Stage | Description |
|---|---|
| 1. Target creation | Create target directory: workflows/ar_meta_builder_v1/ |
| 2. Core file copy | Copy workflow.toml, context_extensions.py, actions.py, README.md to target |
| 3. Prompts copy | Copy prompts/ directory with all 3 template files to target/prompts/ |
| 4. Audiences copy | Copy audiences/ directory with all 3 definition files to target/audiences/ |
| 5. Specs copy | Copy Specs/ directory with codebase_to_meta_v1.md to target/Specs/ |
| 6. Standards copy | Copy Standards/ directory with COMPOSITION_STANDARD.md to target/Standards/ |
| 7. Path recording | Write WORKFLOW_PACKAGE_DIR_FILE with the absolute path to the promoted directory |

**Returns:** APPROVED when all files are copied and WORKFLOW_PACKAGE_DIR_FILE
is written.

**onsuccess:** step_completion (Step 21)

### Action 3: step_completion (Step 21)

**Type:** action
**Phase:** Phase 9 (Promotion)
**Purpose:** Record the final outcome of the workflow execution, including
success status, a summary of all produced artifacts, and the promoted package
path.

**Required inputs:**
- WORKFLOW_PACKAGE_DIR_FILE

**Produces:** COMPLETION_RECORD_FILE

**Completion record contents:**

| Field | Description |
|---|---|
| status | "success" or "failure" |
| workflow_name | "ar_meta_builder_v1" |
| promoted_path | Absolute path from WORKFLOW_PACKAGE_DIR_FILE |
| total_steps_executed | Count of steps that completed (up to 21) |
| total_artifacts_produced | Count of distinct artifacts written |
| phases_completed | List of phase numbers that completed successfully |
| reject_loops_triggered | List of review-refine loops that executed, with iteration counts |
| completed_at | ISO 8601 timestamp |

**Returns:** APPROVED. This is the terminal step.

**onsuccess:** (none -- terminal)

---

## Review/Refine Loop Design

The workflow contains 8 review/refine loops. Each loop consists of a review
or gatekeep step that evaluates an artifact and optionally routes to a refine
step for correction. Loops are bounded by max_iterations to prevent infinite
cycles.

### Loop Properties

Each loop is defined by the following properties:

| Property | Description |
|---|---|
| loop_id | Unique identifier for this loop |
| review_step | The step that evaluates the artifact |
| refine_step | The step that corrects the artifact (may be the same as the generate step) |
| max_iterations | Maximum number of refine cycles before exhaustion |
| exhaustion_code | Code emitted when max_iterations is reached |
| exhaustion_classification | Classification of the exhaustion event |
| artifact_under_review | The artifact being evaluated |
| criteria_range | The test criteria range used for evaluation |

### Loop Definitions

| Loop ID | Review Step | Refine Step | Max Iterations | Exhaustion Code | Exhaustion Classification | Artifact Under Review | Criteria Range |
|---|---|---|---|---|---|---|---|
| LOOP-001 | review_test_criteria (02) | refine_test_criteria (03) | 2 | TEST_CRITERIA_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED | TEST_CRITERIA_FILE | TC-001 to TC-008 |
| LOOP-002 | gatekeep_component_schema (05) | generate_component_schema (04) | 2 | COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED | COMPONENT_SCHEMA_FILE | TC-009 to TC-020 |
| LOOP-003 | gatekeep_composition_format (07) | generate_composition_format (06) | 2 | COMPOSITION_FORMAT_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED | COMPOSITION_FORMAT_FILE | TC-022 to TC-034 |
| LOOP-004 | gatekeep_output_format (09) | generate_output_format (08) | 2 | OUTPUT_FORMAT_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED | OUTPUT_FORMAT_FILE | TC-036 to TC-046 |
| LOOP-005 | gatekeep_operational_workflow (11) | generate_operational_workflow (10) | 2 | OPERATIONAL_WORKFLOW_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED | GENERATED_OPERATIONAL_WORKFLOW_FILE | TC-048 to TC-061 |
| LOOP-006 | gatekeep_composition_standard (13) | generate_composition_standard (12) | 2 | COMPOSITION_STANDARD_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED | COMPOSITION_STANDARD_FILE | TC-063 to TC-069 |
| LOOP-007 | gatekeep_package (17) | generate_package (15) | 2 | PACKAGE_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED | WORKFLOW_MANIFEST_FILE + all package files | TC-078 to TC-099 |
| LOOP-008 | review_package (18) | refine_package (19) | 2 | PACKAGE_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED | WORKFLOW_MANIFEST_FILE + all package files | TC-078 to TC-099 |

### Loop Behavior Specification

**Standard loop cycle:**

1. The review/gatekeep step evaluates the artifact against its criteria range.
2. If APPROVED: the loop exits and execution proceeds to onsuccess.
3. If REJECTED: execution routes to the refine step with specific failure
   reasons and failed criterion identifiers.
4. The refine step revises the artifact addressing all identified issues.
5. Execution returns to the review/gatekeep step for re-evaluation.
6. If max_iterations is reached without approval, the exhaustion_code is
   emitted with the specified classification.

**Loop types:**

- **Generate-Refine loops (LOOP-002 through LOOP-007):** The gatekeep step
  routes back to the generate step. The generate step re-produces the entire
  artifact from scratch, incorporating the gatekeep feedback. This ensures
  complete consistency rather than partial patches.

- **Review-Refine loops (LOOP-001, LOOP-008):** The review step routes to a
  dedicated refine step. The refine step modifies the existing artifact
  addressing specific issues. This preserves content that was not flagged.

**Exhaustion handling:**

All exhaustion events are classified as HUMAN_RETRY_REQUIRED. When a loop
exhausts, the workflow terminates with a rejection status. The exhaustion
code is recorded in the COMPLETION_RECORD_FILE. A human operator must
intervene to resolve the underlying issues before re-running the workflow.

---

## Package File Inventory

The workflow package produced by Phase 8 and promoted in Phase 9 consists of
the following files. This inventory matches the output structure defined in
the OUTPUT_FORMAT_FILE (Part 3: Workflow Package Files).

### Core Files

These files form the operational core of the workflow package.

| File | Description | Resolution Source |
|---|---|---|
| workflow.toml | Workflow manifest declaring 5 steps, 5 artifacts, routing, step types. Valid TOML. | RR-001, RR-002, RR-003 |
| context_extensions.py | Artifact key registration with hardcoded context variable paths. Valid Python. | RR-005, RR-007 |
| actions.py | Python implementations of scan_audiences and publish_meta_content. Valid Python. | RR-001 (action steps) |
| README.md | Human documentation describing purpose, inputs, outputs, audiences, invocation. | RR-006 |

### Prompt Files

Prompt template files for the 3 prompt-type steps in the generated workflow.

| File | Description | Resolution Source |
|---|---|---|
| prompts/generate_meta_content.txt | Prompt template for content generation. Includes all 6 prompt patterns. | RR-004 |
| prompts/review_meta_content.txt | Prompt template for quality review. Includes 4 mandatory patterns. | RR-004 |
| prompts/refine_meta_content.txt | Prompt template for content refinement. Includes all 6 prompt patterns. | RR-004 |

### Audience Definition Files

Plugin files defining the initial audience set. Each file has YAML frontmatter
with audience_id, label, tone, focus_areas, exclude (optional), and
section_structure.

| File | Description | Resolution Source |
|---|---|---|
| audiences/developer.md | Implementation-focused: module APIs, dependencies, setup, patterns, extension points. | RR-007 |
| audiences/architect.md | Design-focused: design decisions, patterns, relationships, dependency graphs, tech debt. | RR-007 |
| audiences/executive.md | Business-focused: project overview, metrics, risk, progress, cost indicators. | RR-007 |

### Supplementary Files

Supporting files that provide specification references and composition
standards for the deployed package.

| File | Description | Resolution Source |
|---|---|---|
| Specs/codebase_to_meta_v1.md | Runtime spec -- content-identical copy of WORKFLOW_SPEC_FILE. Preserves bootstrap chain. | Spec copy |
| Standards/COMPOSITION_STANDARD.md | Composition standard with standard_name, standard_version, component_type_count. | RR-006 |

### Conditional Files

These files may be present depending on the composition configuration.

| File | Condition | Description |
|---|---|---|
| audiences/{additional}.md | If additional audience definitions are added beyond the initial 3 | Additional audience plugin file |
| Per-audience format overrides | If output_variances (BR-007) are defined in the composition | Audience-specific format override files |

### Complete Directory Structure

```
ar_meta_builder_v1/
|
|-- Standards/
|   +-- COMPOSITION_STANDARD.md
|
|-- Specs/
|   +-- codebase_to_meta_v1.md
|
|-- workflow.toml
|-- context_extensions.py
|-- actions.py
|-- README.md
|
|-- prompts/
|   |-- generate_meta_content.txt
|   |-- review_meta_content.txt
|   +-- refine_meta_content.txt
|
+-- audiences/
    |-- developer.md
    |-- architect.md
    +-- executive.md
```

**Total file count:** 11 core files (4 core + 3 prompt + 3 audience + 2
supplementary, counting README as core). The directory structure matches the
3-part output defined in the OUTPUT_FORMAT_FILE.

---

## Self-Validation

This section verifies the completeness and internal consistency of this
operational workflow document.

### Phase Completeness

| Phase | Purpose | Steps Defined | Step Count | Criteria Coverage | Complete |
|---|---|---|---|---|---|
| 1 | Foundation (TDD Loop) | 01, 02, 03 | 3 | TC-001 to TC-008 | Yes |
| 2 | Component Schema | 04, 05 | 2 | TC-009 to TC-020 | Yes |
| 3 | Composition Format | 06, 07 | 2 | TC-022 to TC-034 | Yes |
| 4 | Output Format | 08, 09 | 2 | TC-036 to TC-046 | Yes |
| 5 | Operational Workflow | 10, 11 | 2 | TC-048 to TC-061 | Yes |
| 6 | Composition Standard (v3) | 12, 13 | 2 | TC-063 to TC-069 | Yes |
| 7 | Meta Composition Spec (v3) | 14 | 1 | TC-071 to TC-077 | Yes |
| 8 | Package Assembly | 15, 16, 17, 18, 19 | 5 | TC-078 to TC-099 | Yes |
| 9 | Promotion | 20, 21 | 2 | TC-100 to TC-106 | Yes |

**Total phases: 9. All phases defined.**
**Total steps: 3+2+2+2+2+2+1+5+2 = 21. Matches frontmatter step_count.**

### Step Routing Verification

Every step has valid onsuccess routing:

| Step # | onsuccess Target | Target Exists | Valid |
|---|---|---|---|
| 01 | review_test_criteria | Yes (Step 02) | Yes |
| 02 | generate_component_schema | Yes (Step 04) | Yes |
| 03 | review_test_criteria | Yes (Step 02) | Yes |
| 04 | gatekeep_component_schema | Yes (Step 05) | Yes |
| 05 | generate_composition_format | Yes (Step 06) | Yes |
| 06 | gatekeep_composition_format | Yes (Step 07) | Yes |
| 07 | generate_output_format | Yes (Step 08) | Yes |
| 08 | gatekeep_output_format | Yes (Step 09) | Yes |
| 09 | generate_operational_workflow | Yes (Step 10) | Yes |
| 10 | gatekeep_operational_workflow | Yes (Step 11) | Yes |
| 11 | generate_composition_standard | Yes (Step 12) | Yes |
| 12 | gatekeep_composition_standard | Yes (Step 13) | Yes |
| 13 | generate_meta_composition_spec | Yes (Step 14) | Yes |
| 14 | generate_package | Yes (Step 15) | Yes |
| 15 | validate_package_deterministic | Yes (Step 16) | Yes |
| 16 | gatekeep_package | Yes (Step 17) | Yes |
| 17 | review_package | Yes (Step 18) | Yes |
| 18 | promote_workflow_package | Yes (Step 20) | Yes |
| 19 | review_package | Yes (Step 18) | Yes |
| 20 | step_completion | Yes (Step 21) | Yes |
| 21 | (terminal) | N/A | Yes |

**All 21 steps have valid onsuccess routing. Step 21 is the sole terminal.**

### Reject Routing Verification

| Step # | on_reject_refine Target | Max Iterations | Exhaustion Code | Valid |
|---|---|---|---|---|
| 02 | refine_test_criteria (03) | 2 | TEST_CRITERIA_REVIEW_EXHAUSTED | Yes |
| 05 | generate_component_schema (04) | 2 | COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED | Yes |
| 07 | generate_composition_format (06) | 2 | COMPOSITION_FORMAT_GATEKEEP_EXHAUSTED | Yes |
| 09 | generate_output_format (08) | 2 | OUTPUT_FORMAT_GATEKEEP_EXHAUSTED | Yes |
| 11 | generate_operational_workflow (10) | 2 | OPERATIONAL_WORKFLOW_GATEKEEP_EXHAUSTED | Yes |
| 13 | generate_composition_standard (12) | 2 | COMPOSITION_STANDARD_GATEKEEP_EXHAUSTED | Yes |
| 17 | generate_package (15) | 2 | PACKAGE_GATEKEEP_EXHAUSTED | Yes |
| 18 | refine_package (19) | 2 | PACKAGE_REVIEW_EXHAUSTED | Yes |

**All 8 reject routes are valid. Each has max_iterations and exhaustion_code.**

### Artifact Flow Integrity

Every artifact consumed by a step is either an input or produced by a
preceding step:

| Artifact | Produced By | First Consumed By | Precedes? |
|---|---|---|---|
| TEST_CRITERIA_FILE | Step 01 | Step 02 | Yes (01 < 02) |
| REVIEW_TEST_CRITERIA_FILE | Step 02 | Step 03 | Yes (02 < 03) |
| COMPONENT_SCHEMA_FILE | Step 04 | Step 05 | Yes (04 < 05) |
| GATEKEEP_COMPONENT_SCHEMA_FILE | Step 05 | (none) | N/A |
| COMPOSITION_FORMAT_FILE | Step 06 | Step 07 | Yes (06 < 07) |
| GATEKEEP_COMPOSITION_FORMAT_FILE | Step 07 | (none) | N/A |
| OUTPUT_FORMAT_FILE | Step 08 | Step 09 | Yes (08 < 09) |
| GATEKEEP_OUTPUT_FORMAT_FILE | Step 09 | (none) | N/A |
| GENERATED_OPERATIONAL_WORKFLOW_FILE | Step 10 | Step 11 | Yes (10 < 11) |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | Step 11 | (none) | N/A |
| COMPOSITION_STANDARD_FILE | Step 12 | Step 13 | Yes (12 < 13) |
| GATEKEEP_COMPOSITION_STANDARD_FILE | Step 13 | (none) | N/A |
| META_COMPOSITION_SPEC_FILE | Step 14 | Step 15 | Yes (14 < 15) |
| WORKFLOW_MANIFEST_FILE | Step 15 | Step 16 | Yes (15 < 16) |
| WORKFLOW_EXTENSIONS_FILE | Step 15 | Step 16 | Yes (15 < 16) |
| WORKFLOW_ACTIONS_FILE | Step 15 | Step 16 | Yes (15 < 16) |
| PROMPT_TEMPLATE_FILES | Step 15 | Step 16 | Yes (15 < 16) |
| AUDIENCE_DEFINITION_FILES | Step 15 | Step 16 | Yes (15 < 16) |
| WORKFLOW_README_FILE | Step 15 | Step 17 | Yes (15 < 17) |
| RUNTIME_SPEC_FILE | Step 15 | Step 17 | Yes (15 < 17) |
| VALIDATION_REPORT_FILE | Step 16 | Step 17 | Yes (16 < 17) |
| GATEKEEP_PACKAGE_FILE | Step 17 | (none) | N/A |
| REVIEW_PACKAGE_FILE | Step 18 | Step 19 | Yes (18 < 19) |
| WORKFLOW_PACKAGE_DIR_FILE | Step 20 | Step 21 | Yes (20 < 21) |
| COMPLETION_RECORD_FILE | Step 21 | (terminal) | N/A |

**No dangling references. All artifact flow chains are valid.**

### Type Classification Verification

| Classification | Expected Count | Actual Count | Match |
|---|---|---|---|
| Prompt steps | 18 | 18 | Yes |
| Action steps | 3 | 3 | Yes |
| Total steps | 21 | 21 | Yes |

**Action steps identified:**
- Step 16: validate_package_deterministic (deterministic validation)
- Step 20: promote_workflow_package (file copy operations)
- Step 21: step_completion (terminal recording)

**Prompt steps identified:**
- Steps 01-15 (all generation, review, gatekeep, refine steps)
- Steps 17, 18, 19 (package gatekeep, review, refine)

**Total: 18 prompt + 3 action = 21 steps. Matches frontmatter.**

### Frontmatter Verification

| Field | Expected | Actual | Match |
|---|---|---|---|
| doc_type | "operational_workflow" | "operational_workflow" | Yes |
| lifecycle_status | "draft" | "draft" | Yes |
| domain | "ar_meta_builder" | "ar_meta_builder" | Yes |
| step_count | 21 | 21 | Yes |
| action_count | 3 | 3 | Yes |
| prompt_step_count | 18 | 18 | Yes |
| workflow_pattern | "meta_meta_builder" | "meta_meta_builder" | Yes |

### v3 Innovation Phase Verification

| Phase | Innovation | Steps | Present |
|---|---|---|---|
| Phase 6 | Composition Standard | 12, 13 | Yes |
| Phase 7 | Meta Composition Spec | 14 | Yes |

**Both v3 innovation phases are defined with correct step assignments.**

### Verification Checklist

- [x] Exactly 21 steps defined (Steps 01-21).
- [x] Exactly 9 phases defined (Phases 1-9).
- [x] Every step has valid onsuccess routing.
- [x] Step 21 is the sole terminal step (no onsuccess).
- [x] All 8 reject routes have max_iterations = 2 and exhaustion codes.
- [x] All artifact flow chains are valid (no dangling references).
- [x] v3 innovation phases (6 and 7) are included.
- [x] 18 prompt steps and 3 action steps classified correctly.
- [x] YAML frontmatter matches all required fields.
- [x] Package file inventory matches OUTPUT_FORMAT_FILE Part 3 structure.
- [x] ASCII-only content. No em-dashes, curly quotes, or Unicode.
- [x] All content traces to input specification and upstream artifacts.
- [x] Governance path references use filenames only, not filesystem paths.

---

**End of Operational Workflow Document**
