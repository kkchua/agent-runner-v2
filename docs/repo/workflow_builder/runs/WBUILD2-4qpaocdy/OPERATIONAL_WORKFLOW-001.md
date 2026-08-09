---
doc_type: "operational_workflow"
lifecycle_status: "draft"
effective_version: "WBUILD2-4qpaocdy"
domain: "workflow_builder"
step_count: 21
action_count: 3
prompt_step_count: 18
spec_source: "workflow_builder_v3.md"
composition_standard: "COMPOSITION_SYSTEM_STANDARD.md"
workflow_pattern: "meta_meta_builder"
---

# Operational Workflow Design: Workflow Builder v3

## Overview

This document defines the operational workflow for the Workflow Builder v3 meta-meta builder -- a composition system that generates other meta builders (agents). Each generated meta builder is itself a composition system with its own composition standard, enabling extensibility and self-bootstrapping. The end-to-end transformation reads a single composition system specification (WORKFLOW_SPEC_FILE) describing component types, composition rules, and output structures for a target domain, and produces three deliverables: (1) a Standards/COMPOSITION_STANDARD.md that defines the component schema, composition format, and output format for the generated meta builder's domain, (2) a Specs/ directory structure accepting user-provided specifications at runtime, and (3) an executable workflow package (workflow.toml, prompts/, actions.py, context_extensions.py, README.md) that implements the three-layer architecture. The workflow follows the meta_meta_builder pattern from the Composition Format (COMPOSITION_FORMAT-001.md) and the universal workflow pattern from the Composition System Standard (COMPOSITION_SYSTEM_STANDARD.md Section 6): scan components, plan composition bindings, generate resolved outputs, review quality, and refine issues.

---

## Workflow Phases

The workflow is organized into 9 phases as defined in the specification (workflow_builder_v3.md Section 5.1). Each phase corresponds to a distinct stage of the meta-meta builder construction pipeline. Phases execute sequentially, with each phase consuming artifacts produced by prior phases.

### Phase 1: Foundation (TDD Loop)

**Purpose:** Establish acceptance criteria before any design work begins. This is the universal TDD loop present in all workflows built by this system.

**Steps:**
- generate_test_criteria: Reads the input specification (WORKFLOW_SPEC_FILE) and produces comprehensive acceptance criteria covering all 9 phases, all component types, all composition rules, and all output quality requirements. The criteria are specific, enumerable, and traceable to the spec.
- review_test_criteria: Reviews the acceptance criteria for completeness, correctness, and testability. Checks that every spec section is covered, every criterion is verifiable, and no criteria are vague or redundant.
- refine_test_criteria (conditional): Fixes issues identified in review. Loops back to review_test_criteria until approved or max_iterations exhausted.

**Validation performed:** Criterion specificity (no vague language), coverage completeness (all spec sections addressed), traceability (each criterion links to a spec section).

### Phase 2: Component Schema

**Purpose:** Generate the component schema (Layer 1) defining all 8 component types for the workflow_builder domain: step_definition, role_policy, routing_pattern, prompt_pattern, artifact_contract, composition_standard, output_variance, domain_spec.

**Steps:**
- generate_component_schema: Reads WORKFLOW_SPEC_FILE and TEST_CRITERIA_FILE. Defines common properties (component_id, component_type, name, version, description), type-specific properties for each of the 8 types, validation rules (VR-001 through VR-014), and example components.
- gatekeep_component_schema: Validates the generated schema against spec requirements. Checks: type count equals 8, all common properties defined, all type-specific properties match spec, all validation rules present, examples included. Produces APPROVED/REJECTED verdict.

**Validation performed:** Component type count verification, schema conformance, validation rule completeness, example coverage.

### Phase 3: Composition Format

**Purpose:** Generate the composition format (Layer 2) defining how components are assembled into compositions.

**Steps:**
- generate_composition_format: Reads WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, and COMPONENT_SCHEMA_FILE. Defines the YAML composition structure (builder_name, builder_label, job_prefix, builder_purpose, workflow_pattern, step_bindings, artifact_bindings, composition_standard_binding, output_variances, domain_specs), 8 binding rules, 6 workflow patterns, override mechanism, placeholder resolution, and ordering rules.
- gatekeep_composition_format: Validates the composition format against spec requirements. Checks: all 8 binding rules defined, all 6 workflow patterns documented, override mechanism correct, placeholder resolution complete, required vs optional bindings accurate.

**Validation performed:** Binding rule completeness, workflow pattern enumeration, override schema conformance, placeholder resolvability.

### Phase 4: Output Format

**Purpose:** Generate the output format (Layer 3) defining the resolved output structure.

**Steps:**
- generate_output_format: Reads WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, and COMPOSITION_FORMAT_FILE. Defines the 3-part output structure (Standards/COMPOSITION_STANDARD.md, Specs/ directory, Workflow package), 7 resolution rules (RR-001 through RR-007), quality requirements (QR-001 through QR-008), and downstream extraction contracts.
- gatekeep_output_format: Validates the output format against spec requirements. Checks: 3-part structure defined, all resolution rules present, quality requirements specific and verifiable, downstream contracts feasible.

**Validation performed:** Output structure completeness, resolution rule coverage, quality requirement enforceability, cross-section consistency.

### Phase 5: Operational Workflow

**Purpose:** Generate the operational workflow design (this document) that defines how the workflow operates end-to-end.

**Steps:**
- generate_operational_workflow: Reads WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, and OUTPUT_FORMAT_FILE. Defines all 9 phases, the complete step sequence with types and routing, artifact contracts, action specifications, review/refine loop design, and package file inventory.
- gatekeep_operational_workflow: Validates the operational workflow against spec requirements. Checks: all 9 phases defined, step sequence follows meta_meta_builder pattern, artifact flow integrity (no dangling references), action specifications complete, routing valid.

**Validation performed:** Phase completeness, step routing validity, artifact flow integrity, action feasibility, type consistency.

### Phase 6: Composition Standard (v3 Innovation)

**Purpose:** Generate the composition standard for the meta builder. This is the key v3 innovation -- every generated meta builder has its own composition standard that defines its component types, composition format, and output format.

**Steps:**
- generate_composition_standard: Reads WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, and OPERATIONAL_WORKFLOW_FILE. Generates Standards/COMPOSITION_STANDARD.md with all 3 layers (Component Schema, Composition Format, Output Format) for the target domain, including standard_name, standard_version, component_types_defined, schema_sections, and extensibility_model.
- gatekeep_composition_standard: Validates the composition standard for well-formedness, layer completeness, extensibility model quality, and self-description capability. Checks: standard_name and standard_version correct, component_types_defined non-empty, schema_sections has exactly 3 entries, extensibility_model concrete.

**Validation performed:** Standard well-formedness, layer completeness (all 3 layers defined), extensibility model verification, self-description capability.

### Phase 7: Meta Composition Spec (v3 Innovation)

**Purpose:** Generate the meta composition spec that the generated meta builder will process. This spec defines component types, composition rules, and output structure in a format that can be fed as input to the generated workflow (self-bootstrapping capability).

**Steps:**
- generate_meta_composition_spec: Reads WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, and COMPOSITION_STANDARD_FILE. Generates a spec document with 5 sections: Domain Overview, Component Schema, Composition Format, Output Format, and Operational Requirements. The spec must be self-contained and processable by the generated meta builder.

**Validation performed:** Section completeness (5 required sections), example coverage, self-bootstrapping capability, consistency with composition standard.

### Phase 8: Package Assembly

**Purpose:** Assemble the complete executable workflow package from all prior phase outputs.

**Steps:**
- generate_package: Reads all prior artifacts (WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE). Generates the workflow package files: workflow.toml, context_extensions.py, actions.py, prompts/*.txt, README.md, and conditional files (.env.sample, config.json.sample).
- validate_package_deterministic: Action step. Performs static analysis on the generated package: TOML syntax, Python syntax, artifact binding consistency, action implementation completeness, prompt file existence, placeholder coverage.
- gatekeep_package: LLM review of the generated package. Checks file completeness, design fidelity, composition integrity, prompt quality, and scope check (no shrink, no creep).
- review_package: Comprehensive quality review against all spec requirements. Checks spec fulfillment, component quality, composition quality, output quality, data flow, no hallucinations.
- refine_package (conditional): Fixes issues identified in review. Loops back to review_package until approved or max_iterations exhausted.

**Validation performed:** Deterministic static analysis, file completeness, design fidelity, cross-file consistency, prompt quality, scope verification.

### Phase 9: Promotion

**Purpose:** Deploy the validated workflow package to the target workflows/ directory.

**Steps:**
- promote_workflow_package: Action step. Copies the generated package (workflow.toml, context_extensions.py, actions.py, prompts/, README.md, and conditional files) to workflows/{slug}/. Creates backup of existing target if present.
- step_completion: Built-in framework action. Marks workflow execution as complete.

**Validation performed:** File copy verification (action handles this internally).

---

## Step Sequence

| # | Step Name | Type | Purpose | required_inputs | produces | onsuccess | on_reject_refine |
|---|---|---|---|---|---|---|---|
| 1 | generate_test_criteria | prompt | Generate acceptance criteria for the meta-meta builder | WORKFLOW_SPEC_FILE | TEST_CRITERIA_FILE | review_test_criteria | -- |
| 2 | review_test_criteria | prompt | Review acceptance criteria for completeness and correctness | TEST_CRITERIA_FILE | REVIEW_TEST_CRITERIA_FILE | generate_component_schema | step=refine_test_criteria, artifact=REVIEW_TEST_CRITERIA_FILE, max=2 |
| 3 | refine_test_criteria | prompt | Fix issues in acceptance criteria identified by review | REVIEW_TEST_CRITERIA_FILE, TEST_CRITERIA_FILE | TEST_CRITERIA_FILE | review_test_criteria | -- |
| 4 | generate_component_schema | prompt | Generate component schema defining all 8 component types for Layer 1 | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE | COMPONENT_SCHEMA_FILE | gatekeep_component_schema | -- |
| 5 | gatekeep_component_schema | prompt | Gatekeep validation of component schema | COMPONENT_SCHEMA_FILE | GATEKEEP_COMPONENT_SCHEMA_FILE | generate_composition_format | step=generate_component_schema, artifact=GATEKEEP_COMPONENT_SCHEMA_FILE, max=2 |
| 6 | generate_composition_format | prompt | Generate composition format defining binding rules, overrides, and patterns for Layer 2 | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE | COMPOSITION_FORMAT_FILE | gatekeep_composition_format | -- |
| 7 | gatekeep_composition_format | prompt | Gatekeep validation of composition format | COMPOSITION_FORMAT_FILE | GATEKEEP_COMPOSITION_FORMAT_FILE | generate_output_format | step=generate_composition_format, artifact=GATEKEEP_COMPOSITION_FORMAT_FILE, max=2 |
| 8 | generate_output_format | prompt | Generate output format defining resolution rules and quality requirements for Layer 3 | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE | OUTPUT_FORMAT_FILE | gatekeep_output_format | -- |
| 9 | gatekeep_output_format | prompt | Gatekeep validation of output format | OUTPUT_FORMAT_FILE | GATEKEEP_OUTPUT_FORMAT_FILE | generate_operational_workflow | step=generate_output_format, artifact=GATEKEEP_OUTPUT_FORMAT_FILE, max=2 |
| 10 | generate_operational_workflow | prompt | Generate operational workflow design defining all 9 phases and step sequence | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE | OPERATIONAL_WORKFLOW_FILE | gatekeep_operational_workflow | -- |
| 11 | gatekeep_operational_workflow | prompt | Gatekeep validation of operational workflow design | OPERATIONAL_WORKFLOW_FILE | GATEKEEP_OPERATIONAL_WORKFLOW_FILE | generate_composition_standard | step=generate_operational_workflow, artifact=GATEKEEP_OPERATIONAL_WORKFLOW_FILE, max=2 |
| 12 | generate_composition_standard | prompt | Generate the composition standard for the generated meta builder (v3 innovation) | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE | COMPOSITION_STANDARD_FILE | gatekeep_composition_standard | -- |
| 13 | gatekeep_composition_standard | prompt | Gatekeep validation of composition standard | COMPOSITION_STANDARD_FILE | GATEKEEP_COMPOSITION_STANDARD_FILE | generate_meta_composition_spec | step=generate_composition_standard, artifact=GATEKEEP_COMPOSITION_STANDARD_FILE, max=2 |
| 14 | generate_meta_composition_spec | prompt | Generate the meta composition spec for self-bootstrapping (v3 innovation) | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE | META_COMPOSITION_SPEC_FILE | generate_package | -- |
| 15 | generate_package | prompt | Assemble the complete executable workflow package from all prior artifacts | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE | validate_package_deterministic | -- |
| 16 | validate_package_deterministic | action | Deterministic static analysis of generated package files | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE | VALIDATION_REPORT_FILE | gatekeep_package | -- |
| 17 | gatekeep_package | prompt | Gatekeep review of generated workflow package | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, VALIDATION_REPORT_FILE | GATEKEEP_PACKAGE_FILE | review_package | step=generate_package, artifact=GATEKEEP_PACKAGE_FILE, max=2 |
| 18 | review_package | prompt | Comprehensive quality review of the complete workflow package | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_README_FILE, VALIDATION_REPORT_FILE, GATEKEEP_PACKAGE_FILE | REVIEW_FILE_SUGGESTED | promote_workflow_package | step=refine_package, artifact=REVIEW_FILE_SUGGESTED, max=2 |
| 19 | refine_package | prompt | Fix issues identified in comprehensive review | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE, REVIEW_FILE_SUGGESTED | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE | review_package | -- |
| 20 | promote_workflow_package | action | Deploy workflow package to workflows/ directory | WORKFLOW_MANIFEST_FILE | (none -- copies files) | step_completion | -- |
| 21 | step_completion | action | Mark workflow execution as complete | (none) | (none) | (terminal) | -- |

**Step count:** 21 (18 prompt, 3 action)
**Action count:** 3 (validate_package_deterministic, promote_workflow_package, step_completion)

---

## Artifact Contract

### Input Artifacts

| Artifact Key | Description | Required/Optional |
|---|---|---|
| WORKFLOW_SPEC_FILE | Composition system specification defining component types, composition rules, and output structure for the target meta builder | Required |

### Output Artifacts

| Artifact Key | Description | Produced By Step |
|---|---|---|
| TEST_CRITERIA_FILE | Acceptance criteria for the meta-meta builder covering all 9 phases | generate_test_criteria |
| REVIEW_TEST_CRITERIA_FILE | Review verdict for acceptance criteria | review_test_criteria |
| COMPONENT_SCHEMA_FILE | Component schema defining all 8 component types for Layer 1 | generate_component_schema |
| GATEKEEP_COMPONENT_SCHEMA_FILE | Gatekeep verdict for component schema | gatekeep_component_schema |
| COMPOSITION_FORMAT_FILE | Composition format defining binding rules and patterns for Layer 2 | generate_composition_format |
| GATEKEEP_COMPOSITION_FORMAT_FILE | Gatekeep verdict for composition format | gatekeep_composition_format |
| OUTPUT_FORMAT_FILE | Output format defining resolution rules for Layer 3 | generate_output_format |
| GATEKEEP_OUTPUT_FORMAT_FILE | Gatekeep verdict for output format | gatekeep_output_format |
| OPERATIONAL_WORKFLOW_FILE | Operational workflow design defining all 9 phases and step sequence | generate_operational_workflow |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | Gatekeep verdict for operational workflow | gatekeep_operational_workflow |
| COMPOSITION_STANDARD_FILE | The composition standard for the generated meta builder (v3 innovation) | generate_composition_standard |
| GATEKEEP_COMPOSITION_STANDARD_FILE | Gatekeep verdict for composition standard | gatekeep_composition_standard |
| META_COMPOSITION_SPEC_FILE | The meta composition spec for self-bootstrapping (v3 innovation) | generate_meta_composition_spec |
| WORKFLOW_MANIFEST_FILE | Generated workflow.toml | generate_package (also refine_package) |
| WORKFLOW_EXTENSIONS_FILE | Generated context_extensions.py | generate_package (also refine_package) |
| WORKFLOW_ACTIONS_FILE | Generated actions.py | generate_package (also refine_package) |
| WORKFLOW_PROMPTS_INDEX_FILE | Generated prompts index | generate_package (also refine_package) |
| WORKFLOW_README_FILE | Generated README.md | generate_package (also refine_package) |
| VALIDATION_REPORT_FILE | Deterministic validation report | validate_package_deterministic |
| GATEKEEP_PACKAGE_FILE | Gatekeep verdict for workflow package | gatekeep_package |
| REVIEW_FILE_SUGGESTED | Comprehensive review of workflow package | review_package |

### Traceability

Every output artifact traces back to its producing step. Every step's required_inputs reference either the input artifact (WORKFLOW_SPEC_FILE) or an artifact produced by a prior step. No dangling references exist.

**Artifact flow chain:**
```
WORKFLOW_SPEC_FILE (input)
  -> TEST_CRITERIA_FILE (step 1)
    -> REVIEW_TEST_CRITERIA_FILE (step 2)
      -> COMPONENT_SCHEMA_FILE (step 4)
        -> GATEKEEP_COMPONENT_SCHEMA_FILE (step 5)
          -> COMPOSITION_FORMAT_FILE (step 6)
            -> GATEKEEP_COMPOSITION_FORMAT_FILE (step 7)
              -> OUTPUT_FORMAT_FILE (step 8)
                -> GATEKEEP_OUTPUT_FORMAT_FILE (step 9)
                  -> OPERATIONAL_WORKFLOW_FILE (step 10)
                    -> GATEKEEP_OPERATIONAL_WORKFLOW_FILE (step 11)
                      -> COMPOSITION_STANDARD_FILE (step 12)
                        -> GATEKEEP_COMPOSITION_STANDARD_FILE (step 13)
                          -> META_COMPOSITION_SPEC_FILE (step 14)
                            -> WORKFLOW_MANIFEST_FILE + others (step 15)
                              -> VALIDATION_REPORT_FILE (step 16)
                                -> GATEKEEP_PACKAGE_FILE (step 17)
                                  -> REVIEW_FILE_SUGGESTED (step 18)
                                    -> promote (step 20)
                                      -> step_completion (step 21)
```

---

## Action Specifications

### Action 1: validate_package_deterministic

**Action name:** validate_package_deterministic
**Purpose:** Run static analysis on generated package files to catch runtime defects before LLM gatekeeper review.
**reused_from:** existing action (implemented in workflow_builder_v2/actions.py)

**Inputs:**
- WORKFLOW_MANIFEST_FILE (workflow.toml) -- required
- WORKFLOW_EXTENSIONS_FILE (context_extensions.py) -- required
- WORKFLOW_ACTIONS_FILE (actions.py) -- optional
- Prompts directory (under bundle root) -- discovered from manifest
- Standards/COMPOSITION_STANDARD.md -- discovered from bundle root

**Outputs:**
- VALIDATION_REPORT_FILE -- Markdown report with findings table

**Logic:**
1. Parse workflow.toml using TOML parser. Report TOML_PARSE_ERROR if invalid.
2. Parse context_extensions.py and actions.py using Python AST. Report PYTHON_SYNTAX_ERROR if invalid.
3. Detect TYPE_CHECKING imports used at runtime in actions.py. Report TYPE_CHECKING_RUNTIME_IMPORT.
4. Check artifact binding consistency: detect self-referential bindings (artifact in both required_inputs and produces), and required_inputs referencing artifacts not produced by any prior step. Report SELF_REFERENTIAL_ARTIFACT and UNRESOLVABLE_INPUT_ARTIFACT.
5. Check action step completeness: verify all action steps in workflow.toml have corresponding @action implementations in actions.py. Report MISSING_ACTION_IMPLEMENT.
6. Check prompt file existence: verify all prompt files referenced in workflow.toml exist on disk. Report MISSING_PROMPT_FILE.
7. Check prompt placeholder vs required_inputs consistency: verify artifact placeholders in prompt files match declared required_inputs in workflow.toml. Report PROMPT_INPUT_MISMATCH.
8. Check context_extensions.py artifact key coverage: verify all artifact keys used in workflow.toml are registered in context_extensions.py. Report UNREGISTERED_ARTIFACT_KEYS.
9. Render findings as Markdown report. Return REJECTED if any errors found, APPROVED otherwise.

### Action 2: promote_workflow_package

**Action name:** promote_workflow_package
**Purpose:** Deploy the generated workflow package to the workflows/ directory in the repository.
**reused_from:** existing action (implemented in workflow_builder_v2/actions.py)

**Inputs:**
- WORKFLOW_MANIFEST_FILE -- to determine source directory
- WORKFLOW_SPEC_FILE -- to derive target slug

**Outputs:**
- No artifact produced. Copies files to workflows/{slug}/.
- Returns WORKFLOW_PACKAGE_DIR_FILE with target directory path.

**Logic:**
1. Extract slug from WORKFLOW_SPEC_FILE path (filename stem).
2. Locate source directory from WORKFLOW_MANIFEST_FILE parent.
3. Create backup of existing target directory if present (timestamped backup).
4. Create target directory workflows/{slug}/.
5. Copy always-present files: workflow.toml, context_extensions.py, README.md.
6. Copy conditional files if present: actions.py, .env.sample, config.json.sample.
7. Copy directories if present: prompts/.
8. Return APPROVED with list of copied files, or REJECTED if no files found.

### Action 3: step_completion

**Action name:** step_completion
**Purpose:** Mark workflow execution as complete. Terminal step with no onsuccess routing.
**reused_from:** framework built-in (ACTION_REGISTRY in agent_runner_v2)

**Inputs:** None
**Outputs:** None (returns COMPLETION_RESULT)
**Logic:** Framework-provided. No custom implementation needed.

---

## Routing Diagram

```
                                    +------------------------------+
                                    | Phase 1: Foundation (TDD)    |
                                    +------------------------------+
                                    |                              |
                                    v                              |
                         +---------------------+                   |
                    +--->| generate_test_      |                   |
                    |    | criteria             |                   |
                    |    +----------+----------+                   |
                    |               |                              |
                    |               v                              |
                    |    +---------------------+                   |
                    |    | review_test_        |---APPROVED--------+
                    |    | criteria            |                   |
                    |    +----------+----------+                   |
                    |         REJECTED|                            |
                    |               |                              |
                    |               v                              |
                    |    +---------------------+                   |
                    +----| refine_test_        | (max 2 iterations)|
                         | criteria            |-------------------+
                         +----------+----------+
                                    | APPROVED
                                    v
                         +---------------------+
                         | generate_component_ |
                         | schema              |
                         +----------+----------+
                                    |
                                    v
                         +---------------------+
                    +--->| gatekeep_component_ |---APPROVED--------+
                    |    | schema              |                   |
                    |    +----------+----------+                   |
                    |         REJECTED|                            |
                    |               |                              |
                    |               v                              |
                    +----(regenerate)------------------------------+
                         (max 2 iterations)

                                    | APPROVED
                                    v
    +---------------------------------------------+
    | Phase 3: Composition Format                 |
    | generate_composition_format                 |
    |   -> gatekeep_composition_format            |
    |      [REJECTED -> regenerate, max 2]        |
    +---------------------------------------------+
                    | APPROVED
                    v
    +---------------------------------------------+
    | Phase 4: Output Format                      |
    | generate_output_format                      |
    |   -> gatekeep_output_format                 |
    |      [REJECTED -> regenerate, max 2]        |
    +---------------------------------------------+
                    | APPROVED
                    v
    +---------------------------------------------+
    | Phase 5: Operational Workflow               |
    | generate_operational_workflow               |
    |   -> gatekeep_operational_workflow           |
    |      [REJECTED -> regenerate, max 2]        |
    +---------------------------------------------+
                    | APPROVED
                    v
    +---------------------------------------------+
    | Phase 6: Composition Standard (v3)          |
    | generate_composition_standard               |
    |   -> gatekeep_composition_standard           |
    |      [REJECTED -> regenerate, max 2]        |
    +---------------------------------------------+
                    | APPROVED
                    v
    +---------------------------------------------+
    | Phase 7: Meta Composition Spec (v3)         |
    | generate_meta_composition_spec              |
    +---------------------------------------------+
                    |
                    v
    +---------------------------------------------+
    | Phase 8: Package Assembly                   |
    | generate_package                            |
    |   -> validate_package_deterministic (action)|
    |      -> gatekeep_package                    |
    |         [REJECTED -> regenerate, max 2]     |
    |         -> review_package                   |
    |            [REJECTED -> refine_package]     |
    |               -> review_package (loop)      |
    |               [max 2 iterations]            |
    +---------------------------------------------+
                    | APPROVED
                    v
    +---------------------------------------------+
    | Phase 9: Promotion                          |
    | promote_workflow_package (action)           |
    |   -> step_completion (action)               |
    +---------------------------------------------+
```

---

## Review/Refine Loop Design

### Loop 1: Test Criteria Review/Refine

| Property | Value |
|---|---|
| Review step | review_test_criteria |
| Refine step | refine_test_criteria |
| Trigger | REJECTED verdict from review_test_criteria |
| Artifact under review | REVIEW_TEST_CRITERIA_FILE |
| max_iterations | 2 |
| exhausted_failure_code | TEST_CRITERIA_REVIEW_EXHAUSTED |
| exhausted_failure_class | HUMAN_RETRY_REQUIRED |
| Loop path | review_test_criteria --REJECTED--> refine_test_criteria --onsuccess--> review_test_criteria |

### Loop 2: Component Schema Gatekeep

| Property | Value |
|---|---|
| Gatekeep step | gatekeep_component_schema |
| Refine step | generate_component_schema (re-generates) |
| Trigger | REJECTED verdict from gatekeep_component_schema |
| Artifact under review | GATEKEEP_COMPONENT_SCHEMA_FILE |
| max_iterations | 2 |
| exhausted_failure_code | COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED |
| exhausted_failure_class | HUMAN_RETRY_REQUIRED |
| Loop path | gatekeep_component_schema --REJECTED--> generate_component_schema --onsuccess--> gatekeep_component_schema |

### Loop 3: Composition Format Gatekeep

| Property | Value |
|---|---|
| Gatekeep step | gatekeep_composition_format |
| Refine step | generate_composition_format (re-generates) |
| Trigger | REJECTED verdict from gatekeep_composition_format |
| Artifact under review | GATEKEEP_COMPOSITION_FORMAT_FILE |
| max_iterations | 2 |
| exhausted_failure_code | COMPOSITION_FORMAT_GATEKEEP_EXHAUSTED |
| exhausted_failure_class | HUMAN_RETRY_REQUIRED |
| Loop path | gatekeep_composition_format --REJECTED--> generate_composition_format --onsuccess--> gatekeep_composition_format |

### Loop 4: Output Format Gatekeep

| Property | Value |
|---|---|
| Gatekeep step | gatekeep_output_format |
| Refine step | generate_output_format (re-generates) |
| Trigger | REJECTED verdict from gatekeep_output_format |
| Artifact under review | GATEKEEP_OUTPUT_FORMAT_FILE |
| max_iterations | 2 |
| exhausted_failure_code | OUTPUT_FORMAT_GATEKEEP_EXHAUSTED |
| exhausted_failure_class | HUMAN_RETRY_REQUIRED |
| Loop path | gatekeep_output_format --REJECTED--> generate_output_format --onsuccess--> gatekeep_output_format |

### Loop 5: Operational Workflow Gatekeep

| Property | Value |
|---|---|
| Gatekeep step | gatekeep_operational_workflow |
| Refine step | generate_operational_workflow (re-generates) |
| Trigger | REJECTED verdict from gatekeep_operational_workflow |
| Artifact under review | GATEKEEP_OPERATIONAL_WORKFLOW_FILE |
| max_iterations | 2 |
| exhausted_failure_code | OPERATIONAL_WORKFLOW_GATEKEEP_EXHAUSTED |
| exhausted_failure_class | HUMAN_RETRY_REQUIRED |
| Loop path | gatekeep_operational_workflow --REJECTED--> generate_operational_workflow --onsuccess--> gatekeep_operational_workflow |

### Loop 6: Composition Standard Gatekeep

| Property | Value |
|---|---|
| Gatekeep step | gatekeep_composition_standard |
| Refine step | generate_composition_standard (re-generates) |
| Trigger | REJECTED verdict from gatekeep_composition_standard |
| Artifact under review | GATEKEEP_COMPOSITION_STANDARD_FILE |
| max_iterations | 2 |
| exhausted_failure_code | COMPOSITION_STANDARD_GATEKEEP_EXHAUSTED |
| exhausted_failure_class | HUMAN_RETRY_REQUIRED |
| Loop path | gatekeep_composition_standard --REJECTED--> generate_composition_standard --onsuccess--> gatekeep_composition_standard |

### Loop 7: Package Gatekeep

| Property | Value |
|---|---|
| Gatekeep step | gatekeep_package |
| Refine step | generate_package (re-generates) |
| Trigger | REJECTED verdict from gatekeep_package |
| Artifact under review | GATEKEEP_PACKAGE_FILE |
| max_iterations | 2 |
| exhausted_failure_code | PACKAGE_GATEKEEP_EXHAUSTED |
| exhausted_failure_class | HUMAN_RETRY_REQUIRED |
| Loop path | gatekeep_package --REJECTED--> generate_package --onsuccess--> validate_package_deterministic --> gatekeep_package |

### Loop 8: Package Review/Refine

| Property | Value |
|---|---|
| Review step | review_package |
| Refine step | refine_package |
| Trigger | REJECTED verdict from review_package |
| Artifact under review | REVIEW_FILE_SUGGESTED |
| max_iterations | 2 |
| exhausted_failure_code | PACKAGE_REVIEW_EXHAUSTED |
| exhausted_failure_class | HUMAN_RETRY_REQUIRED |
| Loop path | review_package --REJECTED--> refine_package --onsuccess--> review_package |

**Total loops:** 8 (6 gatekeep loops, 1 TDD review/refine loop, 1 package review/refine loop)

---

## Package File Inventory

The generate_package step (step 15) must create every file listed below. The refine_package step (step 19) must recreate these same files when fixing review issues. If a file is not listed here, it will not be generated.

### Core Files

| # | File Name | Relative Path | Purpose |
|---|---|---|---|
| 1 | workflow.toml | ./workflow.toml | Workflow manifest defining all 21 steps with routing, coder roles, artifact bindings. The central configuration file that the workflow runner consumes. |
| 2 | context_extensions.py | ./context_extensions.py | Artifact key registration module. Maps every artifact_key to its filename pattern. Provides register_artifact_keys() and build_context_extensions() for runtime path resolution. |
| 3 | README.md | ./README.md | Workflow documentation. Describes purpose, setup instructions, step sequence, artifact contracts, and usage guide for the generated meta builder. |

### Conditional Files

| # | File Name | Relative Path | Purpose | Condition |
|---|---|---|---|---|
| 4 | actions.py | ./actions.py | Custom action implementations. Contains @action-decorated functions for validate_package_deterministic and promote_workflow_package. | Required: the workflow has 2 custom action steps (validate_package_deterministic, promote_workflow_package). Always generated for this builder. |
| 5 | .env.sample | ./.env.sample | Sample environment variables. Documents required API keys or credentials if the workflow uses external APIs. | Conditional: only if the generated meta builder requires environment variables for action steps. |
| 6 | config.json.sample | ./config.json.sample | Sample runtime configuration. Documents configuration parameters needed at runtime. | Conditional: only if the generated meta builder requires runtime configuration. |

### Prompt Files

| # | File Name | Relative Path | Purpose |
|---|---|---|---|
| 7 | 01_generate_test_criteria.txt | ./prompts/01_generate_test_criteria.txt | Prompt template for generating acceptance criteria |
| 8 | 02_review_test_criteria.txt | ./prompts/02_review_test_criteria.txt | Prompt template for reviewing acceptance criteria |
| 9 | 03_refine_test_criteria.txt | ./prompts/03_refine_test_criteria.txt | Prompt template for refining acceptance criteria |
| 10 | 04_generate_component_schema.txt | ./prompts/04_generate_component_schema.txt | Prompt template for generating component schema |
| 11 | 05_gatekeep_component_schema.txt | ./prompts/05_gatekeep_component_schema.txt | Prompt template for gatekeeping component schema |
| 12 | 06_generate_composition_format.txt | ./prompts/06_generate_composition_format.txt | Prompt template for generating composition format |
| 13 | 07_gatekeep_composition_format.txt | ./prompts/07_gatekeep_composition_format.txt | Prompt template for gatekeeping composition format |
| 14 | 08_generate_output_format.txt | ./prompts/08_generate_output_format.txt | Prompt template for generating output format |
| 15 | 09_gatekeep_output_format.txt | ./prompts/09_gatekeep_output_format.txt | Prompt template for gatekeeping output format |
| 16 | 10_generate_operational_workflow.txt | ./prompts/10_generate_operational_workflow.txt | Prompt template for generating operational workflow design |
| 17 | 11_gatekeep_operational_workflow.txt | ./prompts/11_gatekeep_operational_workflow.txt | Prompt template for gatekeeping operational workflow |
| 18 | 12_generate_composition_standard.txt | ./prompts/12_generate_composition_standard.txt | Prompt template for generating composition standard (v3) |
| 19 | 13_gatekeep_composition_standard.txt | ./prompts/13_gatekeep_composition_standard.txt | Prompt template for gatekeeping composition standard |
| 20 | 14_generate_meta_composition_spec.txt | ./prompts/14_generate_meta_composition_spec.txt | Prompt template for generating meta composition spec (v3) |
| 21 | 15_generate_package.txt | ./prompts/15_generate_package.txt | Prompt template for assembling the workflow package |
| 22 | 16_gatekeep_package.txt | ./prompts/16_gatekeep_package.txt | Prompt template for gatekeeping the workflow package |
| 23 | 17_review_package.txt | ./prompts/17_review_package.txt | Prompt template for comprehensive package review |
| 24 | 18_refine_package.txt | ./prompts/18_refine_package.txt | Prompt template for refining the workflow package |

### Supplementary Files

| # | File Name | Relative Path | Purpose |
|---|---|---|---|
| 25 | COMPOSITION_STANDARD.md | ./Standards/COMPOSITION_STANDARD.md | The composition standard for the generated meta builder. Defines the 3-layer schema (Component Schema, Composition Format, Output Format) for the target domain. Consistent filename per spec Section 5.5. |
| 26 | (empty directory) | ./Specs/ | Directory for user-provided specifications. Empty at generation time; receives specs at runtime. Establishes folder-based domain separation. |

### File Count Summary

| Category | Count |
|---|---|
| Core files | 3 |
| Conditional files | 1-3 (actions.py always; .env.sample and config.json.sample conditional) |
| Prompt files | 18 |
| Supplementary files | 2 (Standards/COMPOSITION_STANDARD.md + Specs/ directory) |
| **Total (minimum)** | **24** |
| **Total (maximum)** | **26** |

---

## Self-Validation

### Phase Completeness

| # | Phase | Steps Defined | Status |
|---|---|---|---|
| 1 | Foundation (TDD Loop) | generate_test_criteria, review_test_criteria, refine_test_criteria | COVERED |
| 2 | Component Schema | generate_component_schema, gatekeep_component_schema | COVERED |
| 3 | Composition Format | generate_composition_format, gatekeep_composition_format | COVERED |
| 4 | Output Format | generate_output_format, gatekeep_output_format | COVERED |
| 5 | Operational Workflow | generate_operational_workflow, gatekeep_operational_workflow | COVERED |
| 6 | Composition Standard (v3) | generate_composition_standard, gatekeep_composition_standard | COVERED |
| 7 | Meta Composition Spec (v3) | generate_meta_composition_spec | COVERED |
| 8 | Package Assembly | generate_package, validate_package_deterministic, gatekeep_package, review_package, refine_package | COVERED |
| 9 | Promotion | promote_workflow_package, step_completion | COVERED |

**Phase count:** 9/9 defined. TC-OW-001 satisfied.

### Step Routing Completeness

Every step has valid onsuccess routing except step_completion (terminal). No dead-end steps exist.

| Step | onsuccess | Target Exists? |
|---|---|---|
| generate_test_criteria | review_test_criteria | YES |
| review_test_criteria | generate_component_schema | YES |
| refine_test_criteria | review_test_criteria | YES |
| generate_component_schema | gatekeep_component_schema | YES |
| gatekeep_component_schema | generate_composition_format | YES |
| generate_composition_format | gatekeep_composition_format | YES |
| gatekeep_composition_format | generate_output_format | YES |
| generate_output_format | gatekeep_output_format | YES |
| gatekeep_output_format | generate_operational_workflow | YES |
| generate_operational_workflow | gatekeep_operational_workflow | YES |
| gatekeep_operational_workflow | generate_composition_standard | YES |
| generate_composition_standard | gatekeep_composition_standard | YES |
| gatekeep_composition_standard | generate_meta_composition_spec | YES |
| generate_meta_composition_spec | generate_package | YES |
| generate_package | validate_package_deterministic | YES |
| validate_package_deterministic | gatekeep_package | YES |
| gatekeep_package | review_package | YES |
| review_package | promote_workflow_package | YES |
| refine_package | review_package | YES |
| promote_workflow_package | step_completion | YES |
| step_completion | (terminal) | N/A |

**Routing check:** 20/20 non-terminal steps have valid onsuccess. TC-OW-027 satisfied.

### Artifact Flow Integrity

Every step's required_inputs reference an artifact produced by a prior step or the input artifact.

| Step | required_inputs | All Inputs Produced Before This Step? |
|---|---|---|
| generate_test_criteria | WORKFLOW_SPEC_FILE | YES (input artifact) |
| review_test_criteria | TEST_CRITERIA_FILE | YES (step 1) |
| refine_test_criteria | REVIEW_TEST_CRITERIA_FILE, TEST_CRITERIA_FILE | YES (steps 2, 1) |
| generate_component_schema | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE | YES (input, step 1) |
| gatekeep_component_schema | COMPONENT_SCHEMA_FILE | YES (step 4) |
| generate_composition_format | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE | YES (input, step 1, step 4) |
| gatekeep_composition_format | COMPOSITION_FORMAT_FILE | YES (step 6) |
| generate_output_format | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE | YES (input, steps 1, 4, 6) |
| gatekeep_output_format | OUTPUT_FORMAT_FILE | YES (step 8) |
| generate_operational_workflow | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE | YES (input, steps 1, 4, 6, 8) |
| gatekeep_operational_workflow | OPERATIONAL_WORKFLOW_FILE | YES (step 10) |
| generate_composition_standard | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE | YES (input, steps 1, 4, 6, 8, 10) |
| gatekeep_composition_standard | COMPOSITION_STANDARD_FILE | YES (step 12) |
| generate_meta_composition_spec | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE | YES (input, steps 1, 4, 6, 8, 10, 12) |
| generate_package | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE | YES (input, steps 1, 4, 6, 8, 10, 12, 14) |
| validate_package_deterministic | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE | YES (step 15) |
| gatekeep_package | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, VALIDATION_REPORT_FILE | YES (step 15, step 16) |
| review_package | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_README_FILE, VALIDATION_REPORT_FILE, GATEKEEP_PACKAGE_FILE | YES (step 15, steps 16, 17) |
| refine_package | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE, REVIEW_FILE_SUGGESTED | YES (input, prior steps, step 18) |
| promote_workflow_package | WORKFLOW_MANIFEST_FILE | YES (step 15) |
| step_completion | (none) | N/A |

**Artifact flow check:** 0 dangling references. TC-OW-016 satisfied.

### Step Type Classification

| Step | Type | Classification Rationale |
|---|---|---|
| generate_test_criteria | prompt | Requires LLM judgment to derive criteria from spec |
| review_test_criteria | prompt | Requires LLM judgment to evaluate criteria quality |
| refine_test_criteria | prompt | Requires LLM judgment to fix criteria issues |
| generate_component_schema | prompt | Requires LLM judgment to design component types |
| gatekeep_component_schema | prompt | Requires LLM judgment to validate schema |
| generate_composition_format | prompt | Requires LLM judgment to design binding rules |
| gatekeep_composition_format | prompt | Requires LLM judgment to validate composition format |
| generate_output_format | prompt | Requires LLM judgment to design resolution rules |
| gatekeep_output_format | prompt | Requires LLM judgment to validate output format |
| generate_operational_workflow | prompt | Requires LLM judgment to design workflow |
| gatekeep_operational_workflow | prompt | Requires LLM judgment to validate workflow |
| generate_composition_standard | prompt | Requires LLM judgment to design standard |
| gatekeep_composition_standard | prompt | Requires LLM judgment to validate standard |
| generate_meta_composition_spec | prompt | Requires LLM judgment to design meta spec |
| generate_package | prompt | Requires LLM judgment to assemble package |
| validate_package_deterministic | action | Deterministic static analysis |
| gatekeep_package | prompt | Requires LLM judgment to validate package |
| review_package | prompt | Requires LLM judgment for comprehensive review |
| refine_package | prompt | Requires LLM judgment to fix package issues |
| promote_workflow_package | action | Deterministic file copy operation |
| step_completion | action | Framework built-in completion marker |

**Type classification check:** All deterministic operations are action steps. All LLM-judgment tasks are prompt steps. TC-GOW-012 through TC-GOW-015 satisfied.

### Test Criteria Alignment (Sections 8-9)

| Test Criteria ID | Requirement | Satisfied? |
|---|---|---|
| TC-OW-001 | All 9 phases defined | YES -- see Phase Completeness table |
| TC-OW-002 | Foundation phase has generate, review, refine | YES -- steps 1, 2, 3 |
| TC-OW-003 | Each phase has generate + gatekeep | YES -- phases 2-6 each have generate + gatekeep |
| TC-OW-004 | Composition Standard phase has generate + gatekeep (v3) | YES -- steps 12, 13 |
| TC-OW-005 | Meta Composition Spec phase has generate (v3) | YES -- step 14 |
| TC-OW-006 | Package Assembly has all 5 steps | YES -- steps 15-19 |
| TC-OW-007 | Promotion has promote + stepCompletion | YES -- steps 20, 21 |
| TC-OW-008 | Step inputs from prior steps | YES -- see Artifact Flow Integrity |
| TC-OW-009 | Follows meta_meta_builder pattern | YES -- step sequence matches spec Section 3.1.1 |
| TC-OW-010 | Gatekeep follows generate immediately | YES |
| TC-OW-011 | Review follows gatekeep | YES -- review_package follows gatekeep_package |
| TC-OW-012 | Refine follows review | YES -- refine_package follows review_package |
| TC-OW-013 | WORKFLOW_SPEC_FILE declared as input | YES |
| TC-OW-014 | All output artifacts declared | YES -- 21 output artifacts |
| TC-OW-015 | Each artifact has description, required, produced_by | YES |
| TC-OW-016 | Artifact flow integrity | YES -- see Artifact Flow Integrity table |
| TC-OW-017 | validate_package_deterministic is action step | YES -- step 16 |
| TC-OW-018 | validate checks all required items | YES -- 8 checks documented |
| TC-OW-019 | promote_workflow_package is action step | YES -- step 20 |
| TC-OW-020 | promote copies all required files | YES -- file list matches output format |
| TC-OW-021 | Deterministic ops are action steps | YES |
| TC-OW-022 | All generation steps are prompt | YES |
| TC-OW-023 | All gatekeeper steps are prompt | YES |
| TC-OW-024 | All review steps are prompt | YES |
| TC-OW-025 | All refine steps are prompt | YES |
| TC-OW-026 | All prompt steps include self_critic, self_validation | YES -- enforced by prompt pattern rules |
| TC-OW-027 | Every step has onsuccess | YES -- except terminal step |
| TC-OW-028 | Review steps have on_reject_refine | YES -- 8 review/gatekeep steps |
| TC-OW-029 | Refine steps loop back to review | YES |
| TC-OW-030 | on_reject_refine has all 5 fields | YES |
| TC-OW-031 | stepCompletion is terminal | YES |
| TC-OW-032 | Self-bootstrapping supported | YES -- meta composition spec enables it |
| TC-OW-033 | Three outputs supported | YES -- Standards/, Specs/, workflow package |
| TC-OW-034 | Dynamic component discovery | YES -- reads standard dynamically |
| TC-OW-035 | Output variances supported | YES -- defined in composition format |
| TC-OW-036 | Folder-based domain separation | YES -- Standards/ and Specs/ directories |
| TC-OW-037 | Action reuse checked | YES -- see Action Specifications (reused_from fields) |
| TC-OW-038 | Self-check covers all 9 phases | YES -- see Phase Completeness |
| TC-OW-039 | Self-check verifies routing | YES -- see Step Routing Completeness |
| TC-OW-040 | Self-check verifies artifact flow | YES -- see Artifact Flow Integrity |

### Standard Conformance

| Standard Requirement | Satisfied? |
|---|---|
| Universal workflow pattern (Section 6): scan, plan, generate, review, refine | YES -- phases map to this pattern |
| Mixed workflow type (prompt + action) | YES -- 18 prompt, 3 action |
| Review/refine loop design | YES -- 8 loops with max_iterations |
| ASCII-only output | YES |
| Layer boundaries respected | YES -- L1/L2 read-only |

---

**End of Operational Workflow Design**
