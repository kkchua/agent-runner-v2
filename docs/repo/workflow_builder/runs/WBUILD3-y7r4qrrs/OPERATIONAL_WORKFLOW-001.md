---
doc_type: "operational_workflow"
lifecycle_status: "draft"
domain: "workflow_builder"
step_count: 21
action_count: 3
prompt_step_count: 18
workflow_pattern: "meta_meta_builder"
phase_count: 9
review_loop_count: 8
generated_by: "generate_operational_workflow"
spec_reference: "workflow_builder_v4.md"
---

# Operational Workflow -- Workflow Builder v3

## Overview

This document defines the complete operational workflow for the
Workflow Builder v3 meta-meta builder. The workflow follows the
meta_meta_builder pattern from the 6 defined workflow patterns
(COMPOSITION_FORMAT.md). It executes a 9-phase pipeline of 21 steps
that processes a composition system specification (WORKFLOW_SPEC_FILE)
into a 3-part output: composition standard, builder spec, and
executable workflow package.

**Workflow pattern:** meta_meta_builder
**Total steps:** 21
**Prompt-type steps:** 18
**Action-type steps:** 3
**Phases:** 9
**Review/refine loops:** 8
**Input artifacts:** 1 (WORKFLOW_SPEC_FILE)
**Output artifacts:** 23 (see Artifact Contract section)

The 3 action-type steps are deterministic Python operations:
validate_package_deterministic (static analysis),
promote_workflow_package (3-part deployment), and step_completion
(final outcome recording). All other 18 steps are prompt-type,
driven by LLM coders with role-specific instruction sets.

**Phase summary:**

| Phase | Name | Steps | Purpose |
|---|---|---|---|
| 1 | Foundation (TDD Loop) | 3 | Generate and validate acceptance criteria |
| 2 | Component Schema | 2 | Define Layer 1 component types |
| 3 | Composition Format | 2 | Define Layer 2 binding rules and patterns |
| 4 | Output Format | 2 | Define Layer 3 output structure |
| 5 | Operational Workflow | 2 | Define the complete step sequence |
| 6 | Composition Standard | 2 | Define the generated builder standard |
| 7 | Meta Composition Spec | 1 | Produce self-bootstrapping spec |
| 8 | Package Assembly | 5 | Generate, validate, review, refine |
| 9 | Promotion | 2 | Deploy 3-part output to workflows/ |

---

## Workflow Phases

### Phase 1: Foundation (TDD Loop)

**Purpose:** Establish the acceptance criteria that all subsequent
phases are measured against. This phase implements test-driven
development by generating criteria first, then reviewing them for
quality, with a conditional refinement loop if the review rejects
the criteria.

**Steps:**

| Step # | Name | Type | Purpose |
|---|---|---|---|
| 01 | generate_test_criteria | prompt | Generate acceptance criteria for all 9 phases |
| 02 | review_test_criteria | prompt | Review acceptance criteria quality |
| 03 | refine_test_criteria | prompt | Refine rejected criteria (conditional) |

**Phase entry condition:** Workflow started, WORKFLOW_SPEC_FILE
available.
**Phase exit condition:** REVIEW_TEST_CRITERIA_FILE with APPROVED
verdict exists.
**Ordering rule:** O-001 (Foundation First) -- this phase must
execute before all others.

### Phase 2: Component Schema

**Purpose:** Define the Layer 1 Universal Component Schema with all
8 component types, common properties, validation rules (VR-001
through VR-016), and examples. This schema is the building block
library for the generated meta builder.

**Steps:**

| Step # | Name | Type | Purpose |
|---|---|---|---|
| 04 | generate_component_schema | prompt | Generate the component schema for Layer 1 |
| 05 | gatekeep_component_schema | prompt | Validate schema against test criteria |

**Phase entry condition:** TEST_CRITERIA_FILE and
REVIEW_TEST_CRITERIA_FILE (APPROVED) exist.
**Phase exit condition:** GATEKEEP_COMPONENT_SCHEMA_FILE with
APPROVED verdict exists.
**Ordering rule:** O-002 (Layer Sequence) -- Layer 1 before Layer 2.
**Ordering rule:** O-003 (Gatekeep After Generate).

### Phase 3: Composition Format

**Purpose:** Define the Layer 2 Composition Format with 9 binding
rules, 6 workflow patterns, override mechanism, placeholder
resolution (4 data sources), and 8 ordering rules. This format
specifies how components are assembled into compositions.

**Steps:**

| Step # | Name | Type | Purpose |
|---|---|---|---|
| 06 | generate_composition_format | prompt | Generate the composition format for Layer 2 |
| 07 | gatekeep_composition_format | prompt | Validate format against test criteria |

**Phase entry condition:** COMPONENT_SCHEMA_FILE and
GATEKEEP_COMPONENT_SCHEMA_FILE (APPROVED) exist.
**Phase exit condition:** GATEKEEP_COMPOSITION_FORMAT_FILE with
APPROVED verdict exists.
**Ordering rule:** O-002 (Layer Sequence) -- Layer 2 before Layer 3.
**Ordering rule:** O-003 (Gatekeep After Generate).

### Phase 4: Output Format

**Purpose:** Define the Layer 3 Output Format with 3-part directory
structure, 7 resolution rules (RR-001 through RR-007), 8 quality
requirements (QR-001 through QR-008), and 3 downstream extraction
contracts. This format specifies how compositions materialize into
files.

**Steps:**

| Step # | Name | Type | Purpose |
|---|---|---|---|
| 08 | generate_output_format | prompt | Generate the output format for Layer 3 |
| 09 | gatekeep_output_format | prompt | Validate format against test criteria |

**Phase entry condition:** COMPOSITION_FORMAT_FILE and
GATEKEEP_COMPOSITION_FORMAT_FILE (APPROVED) exist.
**Phase exit condition:** GATEKEEP_OUTPUT_FORMAT_FILE with APPROVED
verdict exists.
**Ordering rule:** O-002 (Layer Sequence) -- Layer 3 after Layer 2.
**Ordering rule:** O-003 (Gatekeep After Generate).

### Phase 5: Operational Workflow

**Purpose:** Define the complete operational workflow for the
generated meta builder, including its own phase structure, step
sequence, routing, and artifact contracts. This step produces the
operational workflow document that is itself an artifact of the v3
pipeline.

**Steps:**

| Step # | Name | Type | Purpose |
|---|---|---|---|
| 10 | generate_operational_workflow | prompt | Generate the operational workflow design |
| 11 | gatekeep_operational_workflow | prompt | Validate workflow against test criteria |

**Phase entry condition:** OUTPUT_FORMAT_FILE and
GATEKEEP_OUTPUT_FORMAT_FILE (APPROVED) exist.
**Phase exit condition:** GATEKEEP_OPERATIONAL_WORKFLOW_FILE with
APPROVED verdict exists.
**Ordering rule:** O-007 (Operational Workflow After All Layers).
**Ordering rule:** O-003 (Gatekeep After Generate).

### Phase 6: Composition Standard (v3 Innovation)

**Purpose:** Generate the composition standard for the meta builder
that v3 is creating. This standard defines the component types,
validation rules, and extensibility model that the generated builder
will use. It is the self-describing element that enables dynamic
component discovery.

**Steps:**

| Step # | Name | Type | Purpose |
|---|---|---|---|
| 12 | generate_composition_standard | prompt | Generate the composition standard |
| 13 | gatekeep_composition_standard | prompt | Validate standard against test criteria |

**Phase entry condition:** OPERATIONAL_WORKFLOW_FILE and
GATEKEEP_OPERATIONAL_WORKFLOW_FILE (APPROVED) exist.
**Phase exit condition:** GATEKEEP_COMPOSITION_STANDARD_FILE with
APPROVED verdict exists.
**Ordering rule:** O-008 (Composition Standard Before Package).
**Ordering rule:** O-003 (Gatekeep After Generate).

### Phase 7: Meta Composition Spec (v3 Innovation)

**Purpose:** Produce a self-bootstrapping meta composition
specification that consolidates all prior phase outputs into a
single document. This spec can serve as the WORKFLOW_SPEC_FILE input
to the next version of the builder, enabling the bootstrap chain.

**Steps:**

| Step # | Name | Type | Purpose |
|---|---|---|---|
| 14 | generate_meta_composition_spec | prompt | Generate the meta composition spec |

**Phase entry condition:** COMPOSITION_STANDARD_FILE and
GATEKEEP_COMPOSITION_STANDARD_FILE (APPROVED) exist.
**Phase exit condition:** META_COMPOSITION_SPEC_FILE exists.
**Ordering rule:** O-008 (Composition Standard Before Package).

### Phase 8: Package Assembly

**Purpose:** Assemble the complete workflow package from all prior
phase outputs. This phase generates workflow.toml, prompts,
context_extensions.py, actions.py, README.md, and the
Standards/COMPOSITION_STANDARD.md file. It then validates the
package with 11 deterministic checks, reviews the quality, and
refines if rejected.

**Steps:**

| Step # | Name | Type | Purpose |
|---|---|---|---|
| 15 | generate_package | prompt | Generate complete workflow package |
| 16 | validate_package_deterministic | action | Run 11 static validation checks |
| 17 | gatekeep_package | prompt | Review package quality gate |
| 18 | review_package | prompt | Review package and suggest changes |
| 19 | refine_package | prompt | Refine rejected package (conditional) |

**Phase entry condition:** META_COMPOSITION_SPEC_FILE,
COMPOSITION_STANDARD_FILE, and all prior gatekeep artifacts exist.
**Phase exit condition:** REVIEW_FILE_SUGGESTED with APPROVED
verdict, or all validation checks pass.
**Ordering rule:** O-008 (Composition Standard Before Package).

**Key ordering constraint:** validate_package_deterministic (16)
executes immediately after generate_package (15) and before
gatekeep_package (17). This ensures static analysis results are
available for the quality gate.

### Phase 9: Promotion

**Purpose:** Deploy the validated 3-part output to the workflows/
directory and record the final workflow outcome. The promote action
copies workflow files, Standards/, and workflow documentation to the
target location. The step_completion action records success.

**Steps:**

| Step # | Name | Type | Purpose |
|---|---|---|---|
| 20 | promote_workflow_package | action | Deploy output to workflows/ directory |
| 21 | step_completion | action | Record final outcome and artifact summary |

**Phase entry condition:** All Phase 8 artifacts validated and
approved.
**Phase exit condition:** WORKFLOW_PACKAGE_DIR_FILE records the
promoted path. step_completion records final outcome.
**Ordering rule:** O-004 (Terminal Last) -- step_completion is the
final step.

---

## Step Sequence

The complete step sequence defines all 21 steps in execution order.
Each step specifies its name, number, type, purpose, required
inputs, produced artifacts, and routing behavior.

### Step Sequence Table

| Step # | Name | Type | Purpose | Required Inputs | Produces | onsuccess | on_reject_refine |
|---|---|---|---|---|---|---|---|
| 01 | generate_test_criteria | prompt | Generate acceptance criteria for all 9 phases | WORKFLOW_SPEC_FILE | TEST_CRITERIA_FILE | review_test_criteria | -- |
| 02 | review_test_criteria | prompt | Review acceptance criteria quality | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE | REVIEW_TEST_CRITERIA_FILE | generate_component_schema | refine_test_criteria |
| 03 | refine_test_criteria | prompt | Refine rejected criteria per review feedback | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, REVIEW_TEST_CRITERIA_FILE | TEST_CRITERIA_FILE | review_test_criteria | -- |
| 04 | generate_component_schema | prompt | Generate the Layer 1 component schema | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE | COMPONENT_SCHEMA_FILE | gatekeep_component_schema | -- |
| 05 | gatekeep_component_schema | prompt | Validate component schema against criteria | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE | GATEKEEP_COMPONENT_SCHEMA_FILE | generate_composition_format | generate_component_schema |
| 06 | generate_composition_format | prompt | Generate the Layer 2 composition format | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE | COMPOSITION_FORMAT_FILE | gatekeep_composition_format | -- |
| 07 | gatekeep_composition_format | prompt | Validate composition format against criteria | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPOSITION_FORMAT_FILE | GATEKEEP_COMPOSITION_FORMAT_FILE | generate_output_format | generate_composition_format |
| 08 | generate_output_format | prompt | Generate the Layer 3 output format | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE | OUTPUT_FORMAT_FILE | gatekeep_output_format | -- |
| 09 | gatekeep_output_format | prompt | Validate output format against criteria | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, OUTPUT_FORMAT_FILE | GATEKEEP_OUTPUT_FORMAT_FILE | generate_operational_workflow | generate_output_format |
| 10 | generate_operational_workflow | prompt | Generate operational workflow design | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE | OPERATIONAL_WORKFLOW_FILE | gatekeep_operational_workflow | -- |
| 11 | gatekeep_operational_workflow | prompt | Validate operational workflow against criteria | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, OPERATIONAL_WORKFLOW_FILE | GATEKEEP_OPERATIONAL_WORKFLOW_FILE | generate_composition_standard | generate_operational_workflow |
| 12 | generate_composition_standard | prompt | Generate the composition standard | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE | COMPOSITION_STANDARD_FILE | gatekeep_composition_standard | -- |
| 13 | gatekeep_composition_standard | prompt | Validate composition standard against criteria | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPOSITION_STANDARD_FILE | GATEKEEP_COMPOSITION_STANDARD_FILE | generate_meta_composition_spec | generate_composition_standard |
| 14 | generate_meta_composition_spec | prompt | Generate meta composition spec for bootstrap | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE | META_COMPOSITION_SPEC_FILE | generate_package | -- |
| 15 | generate_package | prompt | Generate complete workflow package | WORKFLOW_SPEC_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE | validate_package_deterministic | -- |
| 16 | validate_package_deterministic | action | Run 11 static validation checks | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, STANDARDS_COMPOSITION_STANDARD_FILE | VALIDATION_REPORT_FILE | gatekeep_package | -- |
| 17 | gatekeep_package | prompt | Evaluate package quality gate | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, WORKFLOW_MANIFEST_FILE, VALIDATION_REPORT_FILE | GATEKEEP_PACKAGE_FILE | review_package | generate_package |
| 18 | review_package | prompt | Review package and suggest improvements | WORKFLOW_SPEC_FILE, WORKFLOW_MANIFEST_FILE, GATEKEEP_PACKAGE_FILE | REVIEW_FILE_SUGGESTED | promote_workflow_package | refine_package |
| 19 | refine_package | prompt | Refine rejected package per review | WORKFLOW_SPEC_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE, REVIEW_FILE_SUGGESTED | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE | validate_package_deterministic | -- |
| 20 | promote_workflow_package | action | Deploy 3-part output to workflows/ | WORKFLOW_MANIFEST_FILE | WORKFLOW_PACKAGE_DIR_FILE | step_completion | -- |
| 21 | step_completion | action | Record final outcome | WORKFLOW_PACKAGE_DIR_FILE | (none) | (terminal) | -- |

### Routing Summary

**Success path (happy path):**
01 -> 02 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 ->
12 -> 13 -> 14 -> 15 -> 16 -> 17 -> 18 -> 20 -> 21 -> END

**Refine loop A (Foundation):**
02 --REJECT--> 03 -> 02 (max 2 iterations)

**Refine loop B (Component Schema):**
05 --REJECT--> 04 -> 05 (max 2 iterations)

**Refine loop C (Composition Format):**
07 --REJECT--> 06 -> 07 (max 2 iterations)

**Refine loop D (Output Format):**
09 --REJECT--> 08 -> 09 (max 2 iterations)

**Refine loop E (Operational Workflow):**
11 --REJECT--> 10 -> 11 (max 2 iterations)

**Refine loop F (Composition Standard):**
13 --REJECT--> 12 -> 13 (max 2 iterations)

**Refine loop G (Package Gate):**
17 --REJECT--> 15 -> 16 -> 17 (max 2 iterations)

**Refine loop H (Package Review):**
18 --REJECT--> 19 -> 16 -> 17 -> 18 (max 2 iterations)

---

## Artifact Contract

### Input Artifacts

| Artifact Key | Description | Required | Source |
|---|---|---|---|
| WORKFLOW_SPEC_FILE | Composition system specification describing the target meta builder | Yes | External (user-provided) |

### Output Artifacts

| Artifact Key | Description | Produced By | Phase | Filename Pattern |
|---|---|---|---|---|
| TEST_CRITERIA_FILE | Acceptance criteria for all 9 phases | generate_test_criteria (01) | 1 | TEST_CRITERIA-{seq}.md |
| REVIEW_TEST_CRITERIA_FILE | Review verdict for test criteria | review_test_criteria (02) | 1 | REVIEW_TEST_CRITERIA-{seq}.md |
| COMPONENT_SCHEMA_FILE | Layer 1 component schema with 8 types | generate_component_schema (04) | 2 | COMPONENT_SCHEMA-{seq}.md |
| GATEKEEP_COMPONENT_SCHEMA_FILE | Gatekeep verdict for component schema | gatekeep_component_schema (05) | 2 | GATEKEEP_COMPONENT_SCHEMA-{seq}.md |
| COMPOSITION_FORMAT_FILE | Layer 2 composition format with 9 bindings | generate_composition_format (06) | 3 | COMPOSITION_FORMAT-{seq}.md |
| GATEKEEP_COMPOSITION_FORMAT_FILE | Gatekeep verdict for composition format | gatekeep_composition_format (07) | 3 | GATEKEEP_COMPOSITION_FORMAT-{seq}.md |
| OUTPUT_FORMAT_FILE | Layer 3 output format with 3-part structure | generate_output_format (08) | 4 | OUTPUT_FORMAT-{seq}.md |
| GATEKEEP_OUTPUT_FORMAT_FILE | Gatekeep verdict for output format | gatekeep_output_format (09) | 4 | GATEKEEP_OUTPUT_FORMAT-{seq}.md |
| OPERATIONAL_WORKFLOW_FILE | Operational workflow design with 21 steps | generate_operational_workflow (10) | 5 | OPERATIONAL_WORKFLOW-{seq}.md |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | Gatekeep verdict for operational workflow | gatekeep_operational_workflow (11) | 5 | GATEKEEP_OPERATIONAL_WORKFLOW-{seq}.md |
| COMPOSITION_STANDARD_FILE | Composition standard for generated builder | generate_composition_standard (12) | 6 | COMPOSITION_STANDARD-{seq}.md |
| GATEKEEP_COMPOSITION_STANDARD_FILE | Gatekeep verdict for composition standard | gatekeep_composition_standard (13) | 6 | GATEKEEP_COMPOSITION_STANDARD-{seq}.md |
| META_COMPOSITION_SPEC_FILE | Meta composition spec for self-bootstrapping | generate_meta_composition_spec (14) | 7 | META_COMPOSITION_SPEC-{seq}.md |
| WORKFLOW_MANIFEST_FILE | workflow.toml manifest | generate_package (15) | 8 | workflow.toml |
| WORKFLOW_EXTENSIONS_FILE | context_extensions.py module | generate_package (15) | 8 | context_extensions.py |
| WORKFLOW_ACTIONS_FILE | actions.py module | generate_package (15) | 8 | actions.py |
| WORKFLOW_PROMPTS_INDEX_FILE | Prompt index listing | generate_package (15) | 8 | prompts/index.txt |
| WORKFLOW_README_FILE | README.md documentation | generate_package (15) | 8 | README.md |
| STANDARDS_COMPOSITION_STANDARD_FILE | Standards/COMPOSITION_STANDARD.md | generate_package (15) | 8 | Standards/COMPOSITION_STANDARD.md |
| VALIDATION_REPORT_FILE | Validation report with 11 checks | validate_package_deterministic (16) | 8 | VALIDATION_REPORT-{seq}.md |
| GATEKEEP_PACKAGE_FILE | Package quality gate verdict | gatekeep_package (17) | 8 | GATEKEEP_PACKAGE-{seq}.md |
| REVIEW_FILE_SUGGESTED | Package review with suggestions | review_package (18) | 8 | REVIEW_SUGGESTED-{seq}.md |
| WORKFLOW_PACKAGE_DIR_FILE | Promoted package directory path | promote_workflow_package (20) | 9 | WORKFLOW_PACKAGE_DIR-{seq}.txt |

### Artifact Flow Chains

Each artifact flows through the pipeline in a traceable chain:

**Chain 1: Foundation**
WORKFLOW_SPEC_FILE -> [01] -> TEST_CRITERIA_FILE -> [02] ->
REVIEW_TEST_CRITERIA_FILE -> [04] (Phase 2)

**Chain 2: Layer 1**
TEST_CRITERIA_FILE -> [04] -> COMPONENT_SCHEMA_FILE -> [05] ->
GATEKEEP_COMPONENT_SCHEMA_FILE -> [06] (Phase 3)

**Chain 3: Layer 2**
COMPONENT_SCHEMA_FILE -> [06] -> COMPOSITION_FORMAT_FILE -> [07] ->
GATEKEEP_COMPOSITION_FORMAT_FILE -> [08] (Phase 4)

**Chain 4: Layer 3**
COMPOSITION_FORMAT_FILE -> [08] -> OUTPUT_FORMAT_FILE -> [09] ->
GATEKEEP_OUTPUT_FORMAT_FILE -> [10] (Phase 5)

**Chain 5: Operational Workflow**
OUTPUT_FORMAT_FILE -> [10] -> OPERATIONAL_WORKFLOW_FILE -> [11] ->
GATEKEEP_OPERATIONAL_WORKFLOW_FILE -> [12] (Phase 6)

**Chain 6: Composition Standard**
OPERATIONAL_WORKFLOW_FILE -> [12] -> COMPOSITION_STANDARD_FILE ->
[13] -> GATEKEEP_COMPOSITION_STANDARD_FILE -> [14] (Phase 7)

**Chain 7: Meta Spec**
COMPOSITION_STANDARD_FILE -> [14] -> META_COMPOSITION_SPEC_FILE ->
[15] (Phase 8)

**Chain 8: Package Assembly**
META_COMPOSITION_SPEC_FILE + COMPOSITION_STANDARD_FILE -> [15] ->
WORKFLOW_MANIFEST_FILE + WORKFLOW_EXTENSIONS_FILE +
WORKFLOW_ACTIONS_FILE + STANDARDS_COMPOSITION_STANDARD_FILE ->
[16] -> VALIDATION_REPORT_FILE -> [17] -> GATEKEEP_PACKAGE_FILE
-> [18] -> REVIEW_FILE_SUGGESTED -> [20] (Phase 9)

**Chain 9: Promotion**
WORKFLOW_MANIFEST_FILE -> [20] -> WORKFLOW_PACKAGE_DIR_FILE ->
[21] -> END

---

## Action Specifications

This section defines the 3 action-type steps in the v3 workflow.
Each action step is a deterministic Python operation implemented
in actions.py.

### Action 1: validate_package_deterministic

| Property | Value |
|---|---|
| Step number | 16 |
| Step name | validate_package_deterministic |
| Step type | action |
| Coder role | validation_standard |
| Phase | 8 (Package Assembly) |

**Purpose:** Run 11 deterministic static validation checks on the
generated workflow package. All checks must pass for the step to
return APPROVED.

**Required inputs:**

| Artifact Key | Description |
|---|---|
| WORKFLOW_MANIFEST_FILE | The workflow.toml to validate |
| WORKFLOW_EXTENSIONS_FILE | The context_extensions.py to validate |
| WORKFLOW_ACTIONS_FILE | The actions.py to validate |
| STANDARDS_COMPOSITION_STANDARD_FILE | The Standards/COMPOSITION_STANDARD.md to validate |

**Produces:** VALIDATION_REPORT_FILE

**Validation checks (11):**

| Check # | Name | Description | Severity |
|---|---|---|---|
| 1 | TOML Parse Validity | workflow.toml parses without errors | CRITICAL |
| 2 | Python Syntax | context_extensions.py and actions.py compile without syntax errors | CRITICAL |
| 3 | TYPE_CHECKING Detection | No if TYPE_CHECKING: runtime guards in Python files | HIGH |
| 4 | Artifact Binding Consistency | All required_inputs reference prior-produced artifacts or workflow inputs; all produces keys are unique | CRITICAL |
| 5 | Action Implementation Completeness | Every action step in workflow.toml has a matching function in actions.py | CRITICAL |
| 6 | Prompt File Existence | Every prompt-type step has a corresponding prompts/NN_{step_name}.txt file | CRITICAL |
| 7 | Prompt Placeholder Consistency (Unidirectional) | Every {PLACEHOLDER} in prompts is declared in step required_inputs or produces | CRITICAL |
| 8 | Artifact Key Coverage | Every artifact key in workflow.toml has a path entry in register_artifact_keys() | CRITICAL |
| 9 | Standards Directory Existence | Standards/COMPOSITION_STANDARD.md exists in output | CRITICAL |
| 10 | Placeholder Declaration Completeness | All prompt {PLACEHOLDER} tokens are declared in step artifacts (checked via bidirectional scan) | CRITICAL |
| 11 | STANDARDS_COMPOSITION_STANDARD_FILE Declaration | Both generate_package and refine_package declare STANDARDS_COMPOSITION_STANDARD_FILE in produces | CRITICAL |

**Routing:**
- All 11 checks pass -> APPROVED -> onsuccess: gatekeep_package (17)
- Any check fails -> REJECTED with details in VALIDATION_REPORT_FILE
  -> onsuccess: gatekeep_package (17) (gatekeep reviews the report)

**Implementation signature:**
```python
def validate_package_deterministic(*, context, state, step_cfg, project_root):
    """Run 11 deterministic validation checks on the workflow package."""
```

### Action 2: promote_workflow_package

| Property | Value |
|---|---|
| Step number | 20 |
| Step name | promote_workflow_package |
| Step type | action |
| Coder role | validation_standard |
| Phase | 9 (Promotion) |

**Purpose:** Deploy the validated workflow package to the
workflows/ directory. Copies all output files including the
workflow package and documentation to the target location.

**Required inputs:**

| Artifact Key | Description |
|---|---|
| WORKFLOW_MANIFEST_FILE | Source workflow.toml (determines output directory) |

**Produces:** WORKFLOW_PACKAGE_DIR_FILE

**Promotion contract:**

| Source | Target | Mandatory |
|---|---|---|
| output/workflow.toml | workflows/{slug}/workflow.toml | Yes |
| output/context_extensions.py | workflows/{slug}/context_extensions.py | Yes |
| output/actions.py | workflows/{slug}/actions.py | If exists |
| output/README.md | workflows/{slug}/README.md | Yes |
| output/prompts/ | workflows/{slug}/prompts/ | Yes |
| output/Standards/ | workflows/{slug}/Standards/ | Yes |
| output/.env.sample | workflows/{slug}/.env.sample | If exists |
| output/config.json.sample | workflows/{slug}/config.json.sample | If exists |

**Routing:**
- Promotion succeeds -> APPROVED -> onsuccess: step_completion (21)
- Promotion fails -> REJECTED with error details

**Implementation signature:**
```python
def promote_workflow_package(*, context, state, step_cfg, project_root):
    """Deploy workflow package to workflows/ directory."""
```

### Action 3: step_completion

| Property | Value |
|---|---|
| Step number | 21 |
| Step name | step_completion |
| Step type | action |
| Coder role | validation_standard |
| Phase | 9 (Promotion) |

**Purpose:** Record the final outcome of the workflow execution.
This is the terminal step (O-004: Terminal Last). It produces no
file artifacts but records success status and a summary of all
produced artifacts in the meta.json sidecar.

**Required inputs:**

| Artifact Key | Description |
|---|---|
| WORKFLOW_PACKAGE_DIR_FILE | The promoted package directory path |

**Produces:** (none -- outcome recorded in meta.json sidecar)

**Routing:**
- This is the terminal step. No onsuccess routing.
- enable_notifications: true (notify on completion)

**Implementation signature:**
```python
def step_completion(*, context, state, step_cfg, project_root):
    """Record final workflow outcome and artifact summary."""
```

---

## Review/Refine Loop Design

The v3 workflow implements 8 review/refine loops. Each loop
follows the pattern: generate/review -> approve (proceed) or
reject (refine and re-review). Loops have a maximum iteration
count to prevent infinite cycling.

### Loop Properties

| Loop ID | Name | Review Step | Refine Step | Max Iterations | Exhausted Code | Exhausted Class |
|---|---|---|---|---|---|---|
| LOOP-A | Foundation Review | review_test_criteria (02) | refine_test_criteria (03) | 2 | TEST_CRITERIA_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-B | Component Schema Gate | gatekeep_component_schema (05) | generate_component_schema (04) | 2 | COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-C | Composition Format Gate | gatekeep_composition_format (07) | generate_composition_format (06) | 2 | COMPOSITION_FORMAT_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-D | Output Format Gate | gatekeep_output_format (09) | generate_output_format (08) | 2 | OUTPUT_FORMAT_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-E | Operational Workflow Gate | gatekeep_operational_workflow (11) | generate_operational_workflow (10) | 2 | OPERATIONAL_WORKFLOW_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-F | Composition Standard Gate | gatekeep_composition_standard (13) | generate_composition_standard (12) | 2 | COMPOSITION_STANDARD_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-G | Package Gate | gatekeep_package (17) | generate_package (15) | 2 | PACKAGE_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-H | Package Review | review_package (18) | refine_package (19) | 2 | PACKAGE_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED |

### Loop Behavior

Each loop operates as follows:

1. The review/gatekeep step evaluates the artifact.
2. If APPROVED: proceed to the next step (onsuccess routing).
3. If REJECTED: route to the refine/regenerate step with the
   rejection feedback.
4. The refine step produces an updated artifact.
5. The updated artifact re-enters the review step.
6. If max_iterations is reached without APPROVED: terminal failure
   with the exhausted_failure_code and exhausted_failure_class.

### Loop Classification

**Type 1: Review-Refine Loops (explicit refine step)**
- LOOP-A: review_test_criteria -> refine_test_criteria -> review
- LOOP-H: review_package -> refine_package -> validate -> gatekeep
  -> review

These loops have a dedicated refine step that receives the review
feedback and produces an improved artifact.

**Type 2: Gatekeep-Regenerate Loops (regenerate from scratch)**
- LOOP-B through LOOP-G: gatekeep -> generate -> gatekeep

These loops route back to the generate step, which regenerates the
artifact incorporating the gatekeep rejection feedback from the
workflow state.

### Refine Step Artifact Flow

**LOOP-A (refine_test_criteria, step 03):**
- Reads: WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE,
  REVIEW_TEST_CRITERIA_FILE
- Produces: TEST_CRITERIA_FILE (overwrites previous)
- Routes to: review_test_criteria (02)

**LOOP-H (refine_package, step 19):**
- Reads: WORKFLOW_SPEC_FILE, COMPOSITION_STANDARD_FILE,
  META_COMPOSITION_SPEC_FILE, REVIEW_FILE_SUGGESTED
- Produces: WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE,
  WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE,
  WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE
- Routes to: validate_package_deterministic (16)

Note: After refine_package (19), the package re-enters the
validation pipeline (16 -> 17 -> 18), not directly back to
review_package. This ensures every refinement is validated before
re-review.

---

## Package File Inventory

This section defines the complete file inventory for the generated
workflow package. The inventory is divided into core files,
conditional files, prompt files, and supplementary files.

### Core Files

These files are always present in every generated workflow package.

| File | Description | Produced By | Mandatory |
|---|---|---|---|
| workflow.toml | Workflow manifest defining steps, artifacts, routing | generate_package (15) | Yes |
| context_extensions.py | Artifact path resolution and dynamic context | generate_package (15) | Yes |
| README.md | Human documentation (purpose, inputs, outputs, invocation) | generate_package (15) | Yes |
| Standards/COMPOSITION_STANDARD.md | Composition standard for generated builder | generate_package (15) | Yes |

### Conditional Files

These files are present only when the workflow requires them.

| File | Description | Condition | Produced By |
|---|---|---|---|
| actions.py | Action step implementations | When workflow has action steps beyond built-in | generate_package (15) |
| .env.sample | Sample environment variables | When workflow needs external credentials | generate_package (15) |
| config.json.sample | Sample runtime configuration | When workflow needs runtime config | generate_package (15) |

### Prompt Files

One prompt template file per prompt-type step. The naming convention
is NN_{step_name}.txt where NN is zero-padded step number.

| File | Step | Step # | Description |
|---|---|---|---|
| 01_generate_test_criteria.txt | generate_test_criteria | 01 | Acceptance criteria generation |
| 02_review_test_criteria.txt | review_test_criteria | 02 | Criteria quality review |
| 03_refine_test_criteria.txt | refine_test_criteria | 03 | Criteria refinement |
| 04_generate_component_schema.txt | generate_component_schema | 04 | Layer 1 schema generation |
| 05_gatekeep_component_schema.txt | gatekeep_component_schema | 05 | Schema quality gate |
| 06_generate_composition_format.txt | generate_composition_format | 06 | Layer 2 format generation |
| 07_gatekeep_composition_format.txt | gatekeep_composition_format | 07 | Format quality gate |
| 08_generate_output_format.txt | generate_output_format | 08 | Layer 3 format generation |
| 09_gatekeep_output_format.txt | gatekeep_output_format | 09 | Format quality gate |
| 10_generate_operational_workflow.txt | generate_operational_workflow | 10 | Operational workflow design |
| 11_gatekeep_operational_workflow.txt | gatekeep_operational_workflow | 11 | Workflow quality gate |
| 12_generate_composition_standard.txt | generate_composition_standard | 12 | Composition standard generation |
| 13_gatekeep_composition_standard.txt | gatekeep_composition_standard | 13 | Standard quality gate |
| 14_generate_meta_composition_spec.txt | generate_meta_composition_spec | 14 | Meta spec generation |
| 15_generate_package.txt | generate_package | 15 | Package assembly generation |
| 17_gatekeep_package.txt | gatekeep_package | 17 | Package quality gate |
| 18_review_package.txt | review_package | 18 | Package review |
| 19_refine_package.txt | refine_package | 19 | Package refinement |

**Prompt file count:** 18 files (one per prompt-type step)

### Supplementary Files

| File | Description | Location |
|---|---|---|
| prompts/index.txt | Index listing all prompt files with step numbers | prompts/ |

### Complete Directory Tree

```
{builder_name}/
|-- Standards/
|   +-- COMPOSITION_STANDARD.md
|-- workflow.toml
|-- context_extensions.py
|-- actions.py                          (conditional)
|-- prompts/
|   |-- index.txt
|   |-- 01_generate_test_criteria.txt
|   |-- 02_review_test_criteria.txt
|   |-- 03_refine_test_criteria.txt
|   |-- 04_generate_component_schema.txt
|   |-- 05_gatekeep_component_schema.txt
|   |-- 06_generate_composition_format.txt
|   |-- 07_gatekeep_composition_format.txt
|   |-- 08_generate_output_format.txt
|   |-- 09_gatekeep_output_format.txt
|   |-- 10_generate_operational_workflow.txt
|   |-- 11_gatekeep_operational_workflow.txt
|   |-- 12_generate_composition_standard.txt
|   |-- 13_gatekeep_composition_standard.txt
|   |-- 14_generate_meta_composition_spec.txt
|   |-- 15_generate_package.txt
|   |-- 17_gatekeep_package.txt
|   |-- 18_review_package.txt
|   +-- 19_refine_package.txt
|-- README.md
|-- .env.sample                         (conditional)
+-- config.json.sample                  (conditional)
```

---

## Self-Validation

This section verifies the completeness and internal consistency of
the operational workflow document.

### Phase Completeness

| Phase # | Name | Steps | Expected Count | Actual Count | Status |
|---|---|---|---|---|---|
| 1 | Foundation (TDD Loop) | 01, 02, 03 | 3 | 3 | PASS |
| 2 | Component Schema | 04, 05 | 2 | 2 | PASS |
| 3 | Composition Format | 06, 07 | 2 | 2 | PASS |
| 4 | Output Format | 08, 09 | 2 | 2 | PASS |
| 5 | Operational Workflow | 10, 11 | 2 | 2 | PASS |
| 6 | Composition Standard | 12, 13 | 2 | 2 | PASS |
| 7 | Meta Composition Spec | 14 | 1 | 1 | PASS |
| 8 | Package Assembly | 15, 16, 17, 18, 19 | 5 | 5 | PASS |
| 9 | Promotion | 20, 21 | 2 | 2 | PASS |
| **Total** | | | **21** | **21** | **PASS** |

**Verification:** All 9 phases defined with correct step counts.
Total step count is 21. TC-055 and TC-056 satisfied.

### Step Routing Completeness

| Step # | Name | Has onsuccess | Has on_reject_refine | Routing Valid |
|---|---|---|---|---|
| 01 | generate_test_criteria | YES (02) | N/A | PASS |
| 02 | review_test_criteria | YES (04) | YES (03) | PASS |
| 03 | refine_test_criteria | YES (02) | N/A | PASS |
| 04 | generate_component_schema | YES (05) | N/A | PASS |
| 05 | gatekeep_component_schema | YES (06) | YES (04) | PASS |
| 06 | generate_composition_format | YES (07) | N/A | PASS |
| 07 | gatekeep_composition_format | YES (08) | YES (06) | PASS |
| 08 | generate_output_format | YES (09) | N/A | PASS |
| 09 | gatekeep_output_format | YES (10) | YES (08) | PASS |
| 10 | generate_operational_workflow | YES (11) | N/A | PASS |
| 11 | gatekeep_operational_workflow | YES (12) | YES (10) | PASS |
| 12 | generate_composition_standard | YES (13) | N/A | PASS |
| 13 | gatekeep_composition_standard | YES (14) | YES (12) | PASS |
| 14 | generate_meta_composition_spec | YES (15) | N/A | PASS |
| 15 | generate_package | YES (16) | N/A | PASS |
| 16 | validate_package_deterministic | YES (17) | N/A | PASS |
| 17 | gatekeep_package | YES (18) | YES (15) | PASS |
| 18 | review_package | YES (20) | YES (19) | PASS |
| 19 | refine_package | YES (16) | N/A | PASS |
| 20 | promote_workflow_package | YES (21) | N/A | PASS |
| 21 | step_completion | TERMINAL | N/A | PASS |

**Verification:** All 21 steps have valid onsuccess routing. Step 21
is the terminal step with no onward routing. 8 steps have
on_reject_refine routing matching the 8 review/refine loops.
TC-057, TC-061, TC-062, TC-063, TC-064, TC-065 satisfied.

### Type Classification

| Type | Count | Steps |
|---|---|---|
| prompt | 18 | 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 17, 18, 19 |
| action | 3 | 16, 20, 21 |
| **Total** | **21** | |

**Verification:** 18 prompt-type steps + 3 action-type steps = 21
total. Matches frontmatter declarations. TC-059 satisfied.

### Artifact Flow Integrity

Every artifact consumed by a step is either:
(a) A workflow-level input (WORKFLOW_SPEC_FILE), or
(b) Produced by a preceding step.

| Artifact Key | Consumed By | Produced By | Valid |
|---|---|---|---|
| WORKFLOW_SPEC_FILE | 01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,17,18,19 | External input | PASS |
| TEST_CRITERIA_FILE | 02,03,04,05,06,07,08,09,10,11,12,13,14,17 | 01, 03 | PASS |
| REVIEW_TEST_CRITERIA_FILE | 03 | 02 | PASS |
| COMPONENT_SCHEMA_FILE | 05,06,07,08,09,10,11,12,13,14 | 04 | PASS |
| GATEKEEP_COMPONENT_SCHEMA_FILE | 06 | 05 | PASS |
| COMPOSITION_FORMAT_FILE | 07,08,09,10,11,12,13,14 | 06 | PASS |
| GATEKEEP_COMPOSITION_FORMAT_FILE | 08 | 07 | PASS |
| OUTPUT_FORMAT_FILE | 09,10,11,12,13,14 | 08 | PASS |
| GATEKEEP_OUTPUT_FORMAT_FILE | 10 | 09 | PASS |
| OPERATIONAL_WORKFLOW_FILE | 11,12,13,14 | 10 | PASS |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | 12 | 11 | PASS |
| COMPOSITION_STANDARD_FILE | 13,14,15,19 | 12 | PASS |
| GATEKEEP_COMPOSITION_STANDARD_FILE | 14 | 13 | PASS |
| META_COMPOSITION_SPEC_FILE | 15,19 | 14 | PASS |
| WORKFLOW_MANIFEST_FILE | 16,17,18,20 | 15, 19 | PASS |
| WORKFLOW_EXTENSIONS_FILE | 16 | 15, 19 | PASS |
| WORKFLOW_ACTIONS_FILE | 16 | 15, 19 | PASS |
| STANDARDS_COMPOSITION_STANDARD_FILE | 16 | 15, 19 | PASS |
| VALIDATION_REPORT_FILE | 17 | 16 | PASS |
| GATEKEEP_PACKAGE_FILE | 18 | 17 | PASS |
| REVIEW_FILE_SUGGESTED | 19 | 18 | PASS |
| WORKFLOW_PACKAGE_DIR_FILE | 21 | 20 | PASS |

**Verification:** No dangling references. Every consumed artifact
is either an input or produced by a preceding step.
TC-067 and TC-068 satisfied.

### Ordering Rule Compliance

| Rule | Description | Verified |
|---|---|---|
| O-001 | Foundation First | PASS -- Phase 1 steps (01-03) are first |
| O-002 | Layer Sequence | PASS -- Layer 1 (Phase 2) -> Layer 2 (Phase 3) -> Layer 3 (Phase 4) |
| O-003 | Gatekeep After Generate | PASS -- All gatekeep steps immediately follow their generate steps |
| O-004 | Terminal Last | PASS -- step_completion (21) is the final step |
| O-005 | Refine Steps Conditional | PASS -- Steps 03 and 19 execute only on rejection |
| O-006 | N/A (v4-specific) | N/A -- embed_builder_spec does not exist in v3 |
| O-007 | Operational Workflow After Layers | PASS -- Phase 5 (steps 10-11) follows Phases 2-4 |
| O-008 | Composition Standard Before Package | PASS -- Phases 6-7 precede Phase 8 |

### Review Loop Completeness

| Loop | Review Step | Refine/Regenerate Step | Max Iterations | Defined |
|---|---|---|---|---|
| LOOP-A | 02 | 03 | 2 | YES |
| LOOP-B | 05 | 04 | 2 | YES |
| LOOP-C | 07 | 06 | 2 | YES |
| LOOP-D | 09 | 08 | 2 | YES |
| LOOP-E | 11 | 10 | 2 | YES |
| LOOP-F | 13 | 12 | 2 | YES |
| LOOP-G | 17 | 15 | 2 | YES |
| LOOP-H | 18 | 19 | 2 | YES |

**Verification:** 8 review/refine loops defined. Each loop has a
review step, a refine/regenerate step, and a max iteration count.
TC-064 satisfied.

### v3 Innovation Phases

| Phase | Innovation | Steps | Present |
|---|---|---|---|
| Phase 6 | Composition Standard (self-describing builder) | 12, 13 | YES |
| Phase 7 | Meta Composition Spec (self-bootstrapping) | 14 | YES |

**Verification:** Both v3 innovation phases are present in the
operational workflow. TC-055 satisfied.

### Criteria Traceability Summary

| Criteria Range | Phase | Status |
|---|---|---|
| TC-055 through TC-056 | Phase completeness (9 phases) | PASS |
| TC-057 | Step count (21 steps) | PASS |
| TC-058 | Step definition completeness | PASS |
| TC-059 | Type classification (18 prompt + 3 action) | PASS |
| TC-060 | Gatekeep step behavior | PASS |
| TC-061 | Gatekeep routing | PASS |
| TC-062 | Review_test_criteria routing | PASS |
| TC-063 | Review_package routing | PASS |
| TC-064 | Conditional refine steps | PASS |
| TC-065 | Terminal step (step_completion) | PASS |
| TC-066 | N/A (v4-specific embed_builder_spec) | N/A |
| TC-067 | Artifact flow consistency | PASS |
| TC-068 | WORKFLOW_SPEC_FILE availability | PASS |
| TC-069 | Phase output availability | PASS |
| TC-070 | Gatekeep verdict format | PASS |

---

End of Operational Workflow Document
