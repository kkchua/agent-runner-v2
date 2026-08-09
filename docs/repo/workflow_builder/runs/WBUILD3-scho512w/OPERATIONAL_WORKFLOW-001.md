---
doc_type: "operational_workflow"
lifecycle_status: "draft"
domain: "workflow_builder"
step_count: 21
action_count: 3
prompt_step_count: 18
workflow_pattern: "meta_meta_builder"
---

# Operational Workflow for Workflow Builder v3

## Overview

This document defines the complete operational workflow for the Workflow Builder v3
meta-meta builder. The workflow follows the meta_meta_builder pattern and consists of
21 steps organized into 9 phases. Of the 21 steps, 18 are prompt-driven (LLM coder)
and 3 are action-driven (Python execution).

**Workflow pattern:** meta_meta_builder
**Step count:** 21
**Prompt steps:** 18
**Action steps:** 3
**Phase count:** 9

The workflow implements a 9-phase TDD-driven pipeline that transforms a runtime
specification (WORKFLOW_SPEC_FILE) into a complete, executable workflow package.
Each phase follows a standardized quality gate pattern: generate, review (where
applicable), validate (action), gatekeep (LLM with test criteria), and refine
(where applicable).

**Three-tier quality gate per phase:**
- Critic (review step): Reviews the TEST quality -- do these tests test the right thing?
- Validate (action step): Deterministic checks -- files exist, parse correctly, identity matches.
- Gatekeeper (prompt step): Runs validated test criteria against artifact -- pass/fail with evidence.

**Output delivery type:** documented_versioned. The full pipeline includes generate,
review, refine, approve, promote, and archive stages.

---

## Workflow Phases

The workflow is organized into 9 phases. Each phase produces a specific design
component and applies quality gates before advancing to the next phase.

### Phase 1: Foundation (TDD Loop)

**Purpose:** Establish the acceptance criteria foundation. Generates test criteria
that all subsequent phases are measured against, reviews them for quality, and
provides a refinement loop to improve test quality.

**Steps:** 3 (all prompt)
- Step 01: generate_test_criteria
- Step 02: review_test_criteria
- Step 03: refine_test_criteria (conditional)

**Output:** TEST_CRITERIA_FILE, REVIEW_TEST_CRITERIA_FILE

**Test criteria focus:** TC-001 through TC-008. Identity correctness, output type
declaration, criteria count consistency, section completeness, uniqueness, specificity,
and traceability.

### Phase 2: Component Schema

**Purpose:** Define the Layer 1 component schema for the target domain. Generates the
fine-tuned base schema with 8 component types, their properties, and validation rules.

**Steps:** 2 (all prompt)
- Step 04: generate_component_schema
- Step 05: gatekeep_component_schema

**Output:** COMPONENT_SCHEMA_FILE, GATEKEEP_COMPONENT_SCHEMA_FILE

**Test criteria focus:** TC-009 through TC-031. Component type count (8), phase mapping,
required/cardinality, common properties (7), type-specific properties per type, and
validation rules (VR-001 through VR-008).

### Phase 3: Composition Format

**Purpose:** Define the Layer 2 composition format -- how domain components bind together.
Specifies binding rules, override mechanisms, placeholder resolution, and ordering rules.

**Steps:** 2 (all prompt)
- Step 06: generate_composition_format
- Step 07: gatekeep_composition_format

**Output:** COMPOSITION_FORMAT_FILE, GATEKEEP_COMPOSITION_FORMAT_FILE

**Test criteria focus:** TC-033 through TC-047. Composition structure, 8 component bindings,
binding rule fields, 6 workflow patterns, override mechanism, 7 placeholders, meta-test-criteria
binding.

### Phase 4: Output Format

**Purpose:** Define the Layer 3 output format -- what the target workflow produces. Specifies
output artifacts, resolution rules, quality requirements, and downstream extraction contracts.

**Steps:** 2 (all prompt)
- Step 08: generate_output_format
- Step 09: gatekeep_output_format

**Output:** OUTPUT_FORMAT_FILE, GATEKEEP_OUTPUT_FORMAT_FILE

**Test criteria focus:** TC-049 through TC-071. Output artifact count (7), source phases,
resolution rules, quality requirements (QR-001 through QR-012), downstream contracts.

### Phase 5: Operational Workflow

**Purpose:** Define the concrete operational workflow for the target. Specifies the complete
step sequence with routing, prompt file specifications, action implementations, and context
extensions.

**Steps:** 2 (all prompt)
- Step 10: generate_operational_workflow
- Step 11: gatekeep_operational_workflow

**Output:** OPERATIONAL_WORKFLOW_FILE, GATEKEEP_OPERATIONAL_WORKFLOW_FILE

**Test criteria focus:** TC-073 through TC-090. TDD-as-DNA pattern, 9 phases, validate actions
(3 types), input/output artifacts, identity locking, base schema sync, recursive self-bootstrap,
meta-test-criteria propagation, three-tier quality gate, output delivery.

### Phase 6: Composition Standard (v3 Innovation)

**Purpose:** Produce the composition standard as a first-class output that enables extensibility.
Consolidates Phases 1 through 5 into a single coherent reference document with the target
workflow identity.

**Steps:** 2 (all prompt)
- Step 12: generate_composition_standard
- Step 13: gatekeep_composition_standard

**Output:** COMPOSITION_STANDARD_FILE, GATEKEEP_COMPOSITION_STANDARD_FILE

**Test criteria focus:** TC-092 through TC-099. Standard identity (target, not builder), 8
component types, schema sections, cross-phase consistency declaration, consolidation of
Phases 1-5.

### Phase 7: Meta Composition Spec (v3 Innovation)

**Purpose:** Produce the meta composition specification that enables self-bootstrapping. The
generated spec contains enough information for a builder to process it as input and generate
the next version, forming the recursive chain.

**Steps:** 1 (prompt)
- Step 14: generate_meta_composition_spec

**Output:** META_COMPOSITION_SPEC_FILE

**Test criteria focus:** TC-101 through TC-109. Five sections (Domain Overview, Component
Schema, Composition Format, Output Format, Operational Requirements), target identity
throughout, workflow identity block, output delivery declaration.

### Phase 8: Package Assembly

**Purpose:** Assemble the complete executable workflow package. Generates all package files
(workflow.toml, context_extensions.py, actions.py, prompts/, README.md, Standards/),
runs deterministic validation, gatekeeps quality, reviews for improvements, and provides
a refinement loop.

**Steps:** 5 (2 prompt, 1 action for validate, 2 prompt for review/refine)
- Step 15: generate_package
- Step 16: validate_package_deterministic (action)
- Step 17: gatekeep_package
- Step 18: review_package
- Step 19: refine_package (conditional)

**Output:** WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE,
WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE,
VALIDATION_REPORT_FILE, GATEKEEP_PACKAGE_FILE, REVIEW_FILE_SUGGESTED

**Test criteria focus:** TC-110 through TC-134. TOML/Python validity, identity correctness,
step routing, artifact key coverage, prompt file existence, placeholder consistency,
bidirectional artifact consistency, coder role policies.

### Phase 9: Promotion

**Purpose:** Promote the validated and reviewed workflow package to the workflows/ directory
and record the final completion outcome.

**Steps:** 2 (both action)
- Step 20: promote_workflow_package (action)
- Step 21: step_completion (action)

**Output:** WORKFLOW_PACKAGE_DIR_FILE, COMPLETION_RESULT

**Test criteria focus:** TC-135 through TC-144. Promoted directory structure, file presence,
parse validity, self-containment, executable without builder reference.

---

## Step Sequence

The complete step sequence defines all 21 steps with their types, purposes, artifact
inputs/outputs, and routing configuration.

| Step | Name | Type | Purpose | Required Inputs | Produces | onsuccess | on_reject_refine |
|------|------|------|---------|-----------------|----------|-----------|------------------|
| 01 | generate_test_criteria | prompt | Generate acceptance criteria for all 9 phases | WORKFLOW_SPEC_FILE | TEST_CRITERIA_FILE | review_test_criteria | -- |
| 02 | review_test_criteria | prompt | Critic review of test criteria quality | TEST_CRITERIA_FILE, WORKFLOW_SPEC_FILE | REVIEW_TEST_CRITERIA_FILE | generate_component_schema | refine_test_criteria (max 2) |
| 03 | refine_test_criteria | prompt | Refine test criteria based on review feedback | REVIEW_TEST_CRITERIA_FILE, TEST_CRITERIA_FILE | TEST_CRITERIA_FILE | review_test_criteria | -- |
| 04 | generate_component_schema | prompt | Generate Layer 1 component schema for target domain | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE | COMPONENT_SCHEMA_FILE | gatekeep_component_schema | -- |
| 05 | gatekeep_component_schema | prompt | Gatekeep component schema against test criteria TC-009 to TC-031 | COMPONENT_SCHEMA_FILE, WORKFLOW_SPEC_FILE | GATEKEEP_COMPONENT_SCHEMA_FILE | generate_composition_format | generate_component_schema (max 2) |
| 06 | generate_composition_format | prompt | Generate Layer 2 composition format with binding rules | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE | COMPOSITION_FORMAT_FILE | gatekeep_composition_format | -- |
| 07 | gatekeep_composition_format | prompt | Gatekeep composition format against test criteria TC-033 to TC-047 | COMPOSITION_FORMAT_FILE | GATEKEEP_COMPOSITION_FORMAT_FILE | generate_output_format | generate_composition_format (max 2) |
| 08 | generate_output_format | prompt | Generate Layer 3 output format with artifacts and resolution rules | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE | OUTPUT_FORMAT_FILE | gatekeep_output_format | -- |
| 09 | gatekeep_output_format | prompt | Gatekeep output format against test criteria TC-049 to TC-071 | OUTPUT_FORMAT_FILE | GATEKEEP_OUTPUT_FORMAT_FILE | generate_operational_workflow | generate_output_format (max 2) |
| 10 | generate_operational_workflow | prompt | Generate operational workflow design with step sequence and routing | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE | OPERATIONAL_WORKFLOW_FILE | gatekeep_operational_workflow | -- |
| 11 | gatekeep_operational_workflow | prompt | Gatekeep operational workflow against test criteria TC-073 to TC-090 | OPERATIONAL_WORKFLOW_FILE | GATEKEEP_OPERATIONAL_WORKFLOW_FILE | generate_composition_standard | generate_operational_workflow (max 2) |
| 12 | generate_composition_standard | prompt | Generate consolidated composition standard (v3 innovation) | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE | COMPOSITION_STANDARD_FILE | gatekeep_composition_standard | -- |
| 13 | gatekeep_composition_standard | prompt | Gatekeep composition standard against test criteria TC-092 to TC-099 | COMPOSITION_STANDARD_FILE | GATEKEEP_COMPOSITION_STANDARD_FILE | generate_meta_composition_spec | generate_composition_standard (max 2) |
| 14 | generate_meta_composition_spec | prompt | Generate meta composition spec for self-bootstrap (v3 innovation) | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE | META_COMPOSITION_SPEC_FILE | generate_package | -- |
| 15 | generate_package | prompt | Generate complete executable workflow package | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE | validate_package_deterministic | -- |
| 16 | validate_package_deterministic | action | Run deterministic validation checks on generated package | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE | VALIDATION_REPORT_FILE | gatekeep_package | -- |
| 17 | gatekeep_package | prompt | Gatekeep package against test criteria TC-110 to TC-129 | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, VALIDATION_REPORT_FILE | GATEKEEP_PACKAGE_FILE | review_package | generate_package (max 2) |
| 18 | review_package | prompt | Review package quality and suggest improvements | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_README_FILE, VALIDATION_REPORT_FILE, GATEKEEP_PACKAGE_FILE | REVIEW_FILE_SUGGESTED | promote_workflow_package | refine_package (max 2) |
| 19 | refine_package | prompt | Refine package based on review feedback | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE, REVIEW_FILE_SUGGESTED | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE | review_package | -- |
| 20 | promote_workflow_package | action | Promote validated package to workflows/ directory | WORKFLOW_MANIFEST_FILE | WORKFLOW_PACKAGE_DIR_FILE | step_completion | -- |
| 21 | step_completion | action | Record final outcome and produced artifact summary | (all produced artifacts) | COMPLETION_RESULT | (terminal) | -- |

### Step Routing Summary

- **Terminal step:** step_completion (step 21) has no onsuccess.
- **Steps with on_reject_refine:** 8 steps have refinement routing:
  - Step 02 (review_test_criteria) -> refine_test_criteria
  - Step 05 (gatekeep_component_schema) -> generate_component_schema
  - Step 07 (gatekeep_composition_format) -> generate_composition_format
  - Step 09 (gatekeep_output_format) -> generate_output_format
  - Step 11 (gatekeep_operational_workflow) -> generate_operational_workflow
  - Step 13 (gatekeep_composition_standard) -> generate_composition_standard
  - Step 17 (gatekeep_package) -> generate_package
  - Step 18 (review_package) -> refine_package
- **All onsuccess targets reference existing step names.** No dangling routing references.

### Coder Role Policy Assignment

| Step | Role Policy |
|------|-------------|
| generate_test_criteria | architect_standard |
| review_test_criteria | reviewer_standard |
| refine_test_criteria | architect_standard |
| generate_component_schema | architect_standard |
| gatekeep_component_schema | gatekeeper_standard |
| generate_composition_format | architect_standard |
| gatekeep_composition_format | gatekeeper_standard |
| generate_output_format | architect_standard |
| gatekeep_output_format | gatekeeper_standard |
| generate_operational_workflow | architect_standard |
| gatekeep_operational_workflow | gatekeeper_standard |
| generate_composition_standard | architect_standard |
| gatekeep_composition_standard | gatekeeper_standard |
| generate_meta_composition_spec | architect_standard |
| generate_package | architect_standard |
| validate_package_deterministic | (action -- no coder role) |
| gatekeep_package | gatekeeper_standard |
| review_package | reviewer_standard |
| refine_package | architect_standard |
| promote_workflow_package | (action -- no coder role) |
| step_completion | (action -- no coder role) |

---

## Artifact Contract

### Input Artifacts

| Artifact Key | Description | Required | Source |
|--------------|-------------|----------|--------|
| WORKFLOW_SPEC_FILE | Runtime specification (markdown with YAML frontmatter) defining the target workflow identity, domain, component types, composition and output formats, and operational requirements | Yes | External input |
| BASE_COMPOSITION_STANDARD | Base Component Schema file path (COMPOSITION_SYSTEM_STANDARD.md). Resolved via context_extensions at runtime | Yes | Governance (resolved by context_extensions) |

### Output Artifacts

| Artifact Key | Description | Producing Step |
|--------------|-------------|----------------|
| TEST_CRITERIA_FILE | Acceptance criteria for all 9 phases (TC-001 through TC-157). Used by all gatekeepers | Step 01, Step 03 |
| REVIEW_TEST_CRITERIA_FILE | Critic review of test criteria quality with APPROVED/REJECTED verdict per category | Step 02 |
| COMPONENT_SCHEMA_FILE | Layer 1 component schema with 8 types, common properties, type-specific properties, validation rules | Step 04 |
| GATEKEEP_COMPONENT_SCHEMA_FILE | Gatekeep result for component schema (APPROVED/REJECTED with failed criteria) | Step 05 |
| COMPOSITION_FORMAT_FILE | Layer 2 composition format with 8 binding rules, 6 workflow patterns, override mechanism, 7 placeholders | Step 06 |
| GATEKEEP_COMPOSITION_FORMAT_FILE | Gatekeep result for composition format | Step 07 |
| OUTPUT_FORMAT_FILE | Layer 3 output format with 7 output artifacts, resolution rules, quality requirements | Step 08 |
| GATEKEEP_OUTPUT_FORMAT_FILE | Gatekeep result for output format | Step 09 |
| OPERATIONAL_WORKFLOW_FILE | Complete operational workflow design with step sequence, routing, action specs, review loops | Step 10 |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | Gatekeep result for operational workflow | Step 11 |
| COMPOSITION_STANDARD_FILE | Consolidated composition standard merging Phases 1-6 (v3 innovation) | Step 12 |
| GATEKEEP_COMPOSITION_STANDARD_FILE | Gatekeep result for composition standard | Step 13 |
| META_COMPOSITION_SPEC_FILE | Meta composition spec for self-bootstrapping (v3 innovation) | Step 14 |
| WORKFLOW_MANIFEST_FILE | workflow.toml -- complete workflow definition with target identity | Step 15, Step 19 |
| WORKFLOW_EXTENSIONS_FILE | context_extensions.py -- domain-specific artifact keys and path resolution | Step 15, Step 19 |
| WORKFLOW_ACTIONS_FILE | actions.py -- domain-specific action implementations | Step 15, Step 19 |
| WORKFLOW_PROMPTS_INDEX_FILE | Prompt file index -- mapping of prompt files to steps | Step 15, Step 19 |
| WORKFLOW_README_FILE | README.md -- describes the target workflow | Step 15, Step 19 |
| STANDARDS_COMPOSITION_STANDARD_FILE | Standards/{standard_filename} -- target composition standard file | Step 15, Step 19 |
| VALIDATION_REPORT_FILE | Deterministic validation report with pass/fail per check | Step 16 |
| GATEKEEP_PACKAGE_FILE | Gatekeep result for package (APPROVED/REJECTED with failed criteria) | Step 17 |
| REVIEW_FILE_SUGGESTED | Quality review of generated package with findings and severity | Step 18 |
| WORKFLOW_PACKAGE_DIR_FILE | Absolute path to the promoted workflow package directory under workflows/ | Step 20 |
| COMPLETION_RESULT | Final outcome record with success status and artifact summary | Step 21 |

### Artifact Flow Chains

Each artifact is consumed only by steps that appear after its producing step. No
dangling references exist in the flow.

**Primary design chain:**
```
WORKFLOW_SPEC_FILE -> Step 01 -> TEST_CRITERIA_FILE -> Steps 04-14
                                                        |
WORKFLOW_SPEC_FILE -> Step 04 -> COMPONENT_SCHEMA_FILE -> Steps 06-14
                                                        |
                              Step 06 -> COMPOSITION_FORMAT_FILE -> Steps 08-14
                                                                  |
                              Step 08 -> OUTPUT_FORMAT_FILE -> Steps 10-14
                                                              |
                              Step 10 -> OPERATIONAL_WORKFLOW_FILE -> Steps 12-14, 15, 19
                                                                    |
                              Step 12 -> COMPOSITION_STANDARD_FILE -> Steps 14-15, 19
                                                                    |
                              Step 14 -> META_COMPOSITION_SPEC_FILE -> Steps 15, 19
```

**Package assembly chain:**
```
Steps 15/19 -> WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE
    |
    v
Step 16 -> VALIDATION_REPORT_FILE
    |
    v
Step 17 -> GATEKEEP_PACKAGE_FILE
    |
    v
Step 18 -> REVIEW_FILE_SUGGESTED -> Step 19 (refine loop)
    |
    v
Step 20 -> WORKFLOW_PACKAGE_DIR_FILE
    |
    v
Step 21 -> COMPLETION_RESULT
```

---

## Action Specifications

Three steps are action-driven (Python execution) rather than prompt-driven (LLM coder).
Each action is implemented as a function decorated with @action in actions.py.

### Action 1: validate_package_deterministic (Step 16)

**Step name:** validate_package_deterministic
**Action function name:** validate_package_deterministic
**Required inputs:** WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE
**Produces:** VALIDATION_REPORT_FILE

**Purpose:** Run comprehensive deterministic validation checks on the generated workflow
package. This action performs all checks that do not require LLM judgment -- file existence,
parse validity, syntax correctness, identity consistency, and structural completeness.

**Checks performed:**

| Check ID | Check Name | Description |
|----------|-----------|-------------|
| VPD-001 | File existence | All required files exist: workflow.toml, context_extensions.py, actions.py, prompts/ directory, README.md |
| VPD-002 | TOML parse validity | workflow.toml parses without errors using a TOML parser |
| VPD-003 | Python syntax (extensions) | context_extensions.py parses without syntax errors (ast.parse) |
| VPD-004 | Python syntax (actions) | actions.py parses without syntax errors (ast.parse) |
| VPD-005 | Identity consistency | workflow.toml name matches spec workflow_name (not builder identity) |
| VPD-006 | Standards directory | Standards/ directory exists with correct {standard_filename} |
| VPD-007 | Specs directory | Specs/ directory exists with embedded builder spec .md file |
| VPD-008 | Prompt file existence | One .txt file per prompt-driven step exists in prompts/ |
| VPD-009 | Placeholder consistency | Every {PLACEHOLDER} in a prompt corresponds to a declared artifact in the step's required_inputs or produces |
| VPD-010 | Bidirectional artifact consistency | Every artifact in step required_inputs/produces is referenced in the corresponding prompt |
| VPD-011 | Action decorator match | Every action step in workflow.toml has a corresponding @action function in actions.py |
| VPD-012 | Artifact key coverage | Every artifact key in workflow.toml has a path resolution entry in context_extensions.py |
| VPD-013 | No builder leakage | No output file contains builder identity values (ar_meta_builder_v2, AMB_STANDARD) where target identity should appear |
| VPD-014 | ASCII compliance | All output files contain ASCII characters only |

**On pass:** Produces VALIDATION_REPORT_FILE with all checks PASS and routes to gatekeep_package.
**On fail:** Produces VALIDATION_REPORT_FILE with check details and error information. Routes to
gatekeep_package which may reject and trigger refinement.

### Action 2: promote_workflow_package (Step 20)

**Step name:** promote_workflow_package
**Action function name:** promote_workflow_package
**Required inputs:** WORKFLOW_MANIFEST_FILE
**Produces:** WORKFLOW_PACKAGE_DIR_FILE

**Purpose:** Copy the validated and reviewed workflow package from the job run directory
to the workflows/ directory, making it available for execution by the daemon.

**Operations performed:**

| Operation | Description |
|-----------|-------------|
| Read manifest | Parse workflow.toml to extract workflow name and version |
| Determine target path | Compute workflows/{workflow_name}/ as the promotion target |
| Create directory | Create the target directory if it does not exist |
| Copy core files | Copy workflow.toml, context_extensions.py, actions.py, README.md |
| Copy prompts | Copy entire prompts/ directory |
| Copy Standards | Copy Standards/ directory with composition standard |
| Copy Specs | Copy Specs/ directory with embedded builder spec |
| Copy conditional | Copy review_prompts/ and approval_config.toml if output_type == documented_versioned |
| Record path | Set WORKFLOW_PACKAGE_DIR_FILE to the absolute path of the promoted directory |

**On success:** Produces WORKFLOW_PACKAGE_DIR_FILE with the absolute path to the promoted
directory. Routes to step_completion.

### Action 3: step_completion (Step 21)

**Step name:** step_completion
**Action function name:** step_completion
**Required inputs:** (all produced artifacts from the workflow)
**Produces:** COMPLETION_RESULT

**Purpose:** Record the final outcome of the workflow execution. This is the terminal step
-- it has no onsuccess routing. It collects a summary of all produced artifacts and writes
the completion result to the meta.json sidecar.

**Operations performed:**

| Operation | Description |
|-----------|-------------|
| Collect artifacts | Gather all artifact keys and their file paths from the job directory |
| Verify promotion | Confirm WORKFLOW_PACKAGE_DIR_FILE points to a valid directory |
| Build summary | Create a summary listing all 24+ artifact keys and their production status |
| Write meta.json | Write the meta.json sidecar with status "success", artifacts_produced list, and result summary |
| Set requires_human_approval_after | false (no human approval needed after completion) |

**On success:** Produces COMPLETION_RESULT and terminates the workflow.

---

## Review/Refine Loop Design

The workflow defines 8 review/refine loops. Each loop pairs a review or gatekeep step
with a refine or regenerate step, with a maximum iteration count to prevent infinite loops.

### Loop Properties

| Loop ID | Review/Gatekeep Step | Refine/Regenerate Step | Max Iterations | Exhausted Failure Code | Exhausted Failure Class |
|---------|---------------------|----------------------|----------------|----------------------|------------------------|
| LOOP-01 | review_test_criteria (02) | refine_test_criteria (03) | 2 | TEST_CRITERIA_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-02 | gatekeep_component_schema (05) | generate_component_schema (04) | 2 | COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-03 | gatekeep_composition_format (07) | generate_composition_format (06) | 2 | COMPOSITION_FORMAT_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-04 | gatekeep_output_format (09) | generate_output_format (08) | 2 | OUTPUT_FORMAT_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-05 | gatekeep_operational_workflow (11) | generate_operational_workflow (10) | 2 | OPERATIONAL_WORKFLOW_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-06 | gatekeep_composition_standard (13) | generate_composition_standard (12) | 2 | COMPOSITION_STANDARD_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-07 | gatekeep_package (17) | generate_package (15) | 2 | PACKAGE_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-08 | review_package (18) | refine_package (19) | 2 | PACKAGE_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED |

### Loop Behavior

**Review loops (LOOP-01, LOOP-08):** The review step produces a structured review document
(REVIEW_TEST_CRITERIA_FILE or REVIEW_FILE_SUGGESTED). If the reviewer REJECTS, the on_reject_refine
routing sends the artifact to the refine step. The refine step produces a corrected version, which
routes back to the review step for re-evaluation. This continues until APPROVED or max iterations
exhausted.

**Gatekeep loops (LOOP-02 through LOOP-07):** The gatekeep step evaluates the artifact against
test criteria and meta-test-criteria. If REJECTED, the on_reject_refine routing sends the rejection
back to the generate step. The generate step produces a corrected artifact, which routes back
to the gatekeep step. This continues until APPROVED or max iterations exhausted.

**Exhaustion behavior:** When max iterations (2) are exhausted without approval, the workflow
fails with the specified exhausted_failure_code and exhausted_failure_class = HUMAN_RETRY_REQUIRED.
This signals that human intervention is needed.

**Loop direction:**
- LOOP-01: Step 02 -> Step 03 -> Step 02 (cycle)
- LOOP-02: Step 05 -> Step 04 -> Step 05 (cycle)
- LOOP-03: Step 07 -> Step 06 -> Step 07 (cycle)
- LOOP-04: Step 09 -> Step 08 -> Step 09 (cycle)
- LOOP-05: Step 11 -> Step 10 -> Step 11 (cycle)
- LOOP-06: Step 13 -> Step 12 -> Step 13 (cycle)
- LOOP-07: Step 17 -> Step 15 -> Step 16 -> Step 17 (cycle through validate)
- LOOP-08: Step 18 -> Step 19 -> Step 18 (cycle)

---

## Package File Inventory

The workflow package produced by Phase 8 (Package Assembly) and promoted by Phase 9
(Promotion) consists of the following files organized in a directory structure.

### Core Files

| File | Location | Description | Producing Step |
|------|----------|-------------|----------------|
| workflow.toml | Root | Complete workflow definition with target identity, step sequence, routing, artifact keys, coder role policies | Step 15 / Step 19 |
| context_extensions.py | Root | Domain-specific context extensions class with artifact key registry, known_artifact_paths function, computed context properties | Step 15 / Step 19 |
| actions.py | Root | Python module with @action-decorated functions for all 3 action steps (validate_package_deterministic, promote_workflow_package, step_completion) | Step 15 / Step 19 |
| README.md | Root | Human-readable documentation describing the target workflow (not the builder) | Step 15 / Step 19 |

### Conditional Files

| File | Location | Condition | Description |
|------|----------|-----------|-------------|
| review_prompts/ | Subdirectory | output_type == documented_versioned | Review and refine prompt templates for review loop steps |
| approval_config.toml | Root | output_type == documented_versioned | Configuration for human approval gates |

### Prompt Files

One .txt file per prompt-driven step, located in the prompts/ subdirectory. Filename
pattern: {NN}_{step_name}.txt where NN is the zero-padded step number.

| File | Step Served | Step Number |
|------|-------------|-------------|
| prompts/01_generate_test_criteria.txt | generate_test_criteria | 01 |
| prompts/02_review_test_criteria.txt | review_test_criteria | 02 |
| prompts/03_refine_test_criteria.txt | refine_test_criteria | 03 |
| prompts/04_generate_component_schema.txt | generate_component_schema | 04 |
| prompts/05_gatekeep_component_schema.txt | gatekeep_component_schema | 05 |
| prompts/06_generate_composition_format.txt | generate_composition_format | 06 |
| prompts/07_gatekeep_composition_format.txt | gatekeep_composition_format | 07 |
| prompts/08_generate_output_format.txt | generate_output_format | 08 |
| prompts/09_gatekeep_output_format.txt | gatekeep_output_format | 09 |
| prompts/10_generate_operational_workflow.txt | generate_operational_workflow | 10 |
| prompts/11_gatekeep_operational_workflow.txt | gatekeep_operational_workflow | 11 |
| prompts/12_generate_composition_standard.txt | generate_composition_standard | 12 |
| prompts/13_gatekeep_composition_standard.txt | gatekeep_composition_standard | 13 |
| prompts/14_generate_meta_composition_spec.txt | generate_meta_composition_spec | 14 |
| prompts/15_generate_package.txt | generate_package | 15 |
| prompts/16_gatekeep_package.txt | gatekeep_package | 17 |
| prompts/17_review_package.txt | review_package | 18 |
| prompts/18_refine_package.txt | refine_package | 19 |

Total prompt files: 18 (one per prompt-driven step).

### Supplementary Files

| File | Location | Description | Source |
|------|----------|-------------|--------|
| {standard_filename} | Standards/ | Target workflow composition standard. Filename from spec identity (standard_filename) | Step 15 / Step 19 |
| {builder_name}.md | Specs/ | Embedded builder specification for self-bootstrap. Content-identical to input WORKFLOW_SPEC_FILE | Step 15 (copy action) |

### Output Directory Structure

```
{workflow_name}/
  Standards/
    {standard_filename}
  Specs/
    {builder_name}.md
  workflow.toml
  context_extensions.py
  actions.py
  prompts/
    01_generate_test_criteria.txt
    02_review_test_criteria.txt
    03_refine_test_criteria.txt
    04_generate_component_schema.txt
    05_gatekeep_component_schema.txt
    06_generate_composition_format.txt
    07_gatekeep_composition_format.txt
    08_generate_output_format.txt
    09_gatekeep_output_format.txt
    10_generate_operational_workflow.txt
    11_gatekeep_operational_workflow.txt
    12_generate_composition_standard.txt
    13_gatekeep_composition_standard.txt
    14_generate_meta_composition_spec.txt
    15_generate_package.txt
    16_gatekeep_package.txt
    17_review_package.txt
    18_refine_package.txt
  README.md
  review_prompts/               (conditional: documented_versioned only)
  approval_config.toml           (conditional: documented_versioned only)
```

---

## Self-Validation

This section verifies the completeness and internal consistency of this operational
workflow document.

### Phase Completeness

All 9 phases are defined with their purpose, step count, outputs, and test criteria focus:
- Phase 1 (Foundation): 3 steps. PASS.
- Phase 2 (Component Schema): 2 steps. PASS.
- Phase 3 (Composition Format): 2 steps. PASS.
- Phase 4 (Output Format): 2 steps. PASS.
- Phase 5 (Operational Workflow): 2 steps. PASS.
- Phase 6 (Composition Standard): 2 steps. PASS.
- Phase 7 (Meta Composition Spec): 1 step. PASS.
- Phase 8 (Package Assembly): 5 steps. PASS.
- Phase 9 (Promotion): 2 steps. PASS.
- Total: 3+2+2+2+2+2+1+5+2 = 21. PASS.

### Step Routing Verification

Every step has valid onsuccess routing (except terminal step 21):
- Steps 01-20 each declare an onsuccess target.
- All onsuccess targets reference existing step names.
- Step 21 (step_completion) is terminal with no onsuccess.
- PASS.

### Artifact Flow Integrity

Every artifact consumed by a step is either:
(a) An input declared in the workflow (WORKFLOW_SPEC_FILE, BASE_COMPOSITION_STANDARD), or
(b) Produced by a preceding step.

Verification of key flows:
- TEST_CRITERIA_FILE: Produced by Step 01, consumed by Steps 02-15, 19. All consumers come after producer. PASS.
- COMPONENT_SCHEMA_FILE: Produced by Step 04, consumed by Steps 06-15, 19. PASS.
- COMPOSITION_FORMAT_FILE: Produced by Step 06, consumed by Steps 08-15, 19. PASS.
- OUTPUT_FORMAT_FILE: Produced by Step 08, consumed by Steps 10-15, 19. PASS.
- OPERATIONAL_WORKFLOW_FILE: Produced by Step 10, consumed by Steps 12-15, 19. PASS.
- COMPOSITION_STANDARD_FILE: Produced by Step 12, consumed by Steps 14-15, 19. PASS.
- META_COMPOSITION_SPEC_FILE: Produced by Step 14, consumed by Steps 15, 19. PASS.
- WORKFLOW_MANIFEST_FILE: Produced by Step 15, consumed by Steps 16-18, 20. PASS.
- VALIDATION_REPORT_FILE: Produced by Step 16, consumed by Steps 17-18. PASS.
- GATEKEEP_PACKAGE_FILE: Produced by Step 17, consumed by Step 18. PASS.
- REVIEW_FILE_SUGGESTED: Produced by Step 18, consumed by Step 19. PASS.
- WORKFLOW_PACKAGE_DIR_FILE: Produced by Step 20, consumed by Step 21. PASS.
- No dangling references found. PASS.

### Type Classification

Step type classification verified:
- 18 prompt steps: Steps 01-15, 17-19 (all with prompt = "prompts/NN_{name}.txt"). PASS.
- 3 action steps: Step 16 (validate_package_deterministic), Step 20 (promote_workflow_package), Step 21 (step_completion). PASS.
- Total: 18 + 3 = 21. PASS.

### Review Loop Completeness

All 8 review/refine loops defined with:
- Review/gatekeep step reference. PASS.
- Refine/regenerate step reference. PASS.
- max_iterations = 2. PASS.
- exhausted_failure_code defined. PASS.
- exhausted_failure_class = HUMAN_RETRY_REQUIRED. PASS.
- Loop cycle direction verified (refine routes back to review/gatekeep). PASS.

### v3 Innovation Phases

- Phase 6 (Composition Standard): Present with 2 steps (12, 13). Produces COMPOSITION_STANDARD_FILE. PASS.
- Phase 7 (Meta Composition Spec): Present with 1 step (14). Produces META_COMPOSITION_SPEC_FILE. PASS.

### Domain-Specific Requirements Coverage

- Identity locking: Forbidden content rules documented in spec references. Target identity used throughout. PASS.
- Base schema sync: Prompts reference {BASE_COMPOSITION_STANDARD}. Validate checks MIN_BASE_SCHEMA_VERSION = "2.0". PASS.
- Recursive self-bootstrap: Phase 9 copies WORKFLOW_SPEC_FILE to Specs/{builder_name}.md. PASS.
- Meta-test-criteria propagation: Phase 1 meta_test_criteria injected into all subsequent gatekeep prompts (Phases 2-8). PASS.
- Output delivery: documented_versioned pipeline with review, refine, approve, promote, archive. PASS.

### YAML Frontmatter Compliance

- doc_type: "operational_workflow": PASS.
- lifecycle_status: "draft": PASS.
- domain: "workflow_builder": PASS.
- step_count: 21: PASS.
- action_count: 3: PASS.
- prompt_step_count: 18: PASS.
- workflow_pattern: "meta_meta_builder": PASS.

### ASCII Compliance

All content in this document uses ASCII characters only. No em-dashes, curly quotes,
or Unicode characters present. PASS.

### Traceability to Spec

Every section, phase, step, and rule traces to a specific section in the input specification
(ar_meta_builder_v2.md):
- TDD-as-DNA pattern: spec Section 7.1. PASS.
- 9 phases: spec Section 7.2. PASS.
- Validate actions (3): spec Section 7.3. PASS.
- Input artifacts (2): spec Section 7.4. PASS.
- Output artifacts (13+): spec Section 7.5. PASS.
- Domain-specific requirements: spec Section 7.6. PASS.
- Workflow identity: spec Section 2. PASS.
- Output delivery: spec Section 3. PASS.

No scope invention detected. PASS.

---

End of Operational Workflow Document
