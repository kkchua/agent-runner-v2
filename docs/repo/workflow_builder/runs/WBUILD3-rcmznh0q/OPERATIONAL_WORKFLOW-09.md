---
doc_type: "operational_workflow"
lifecycle_status: "draft"
domain: "workflow_builder"
step_count: 21
action_count: 3
prompt_step_count: 18
workflow_pattern: "meta_meta_builder"
---

# Operational Workflow: Workflow Builder v3

## Overview

This document defines the operational workflow design for the Workflow
Builder v3 meta-meta builder. It specifies all 9 phases, the complete
step sequence with types and routing, artifact contracts, action
specifications, review/refine loop design, and package file inventory.

**Workflow pattern:** meta_meta_builder
**Total steps:** 21 (18 prompt, 3 action)
**Total phases:** 9
**Input artifacts:** 1 (WORKFLOW_SPEC_FILE)
**Output artifacts:** 24 (including conditional artifacts)
**Review/refine loops:** 2 (Phase 1 and Phase 8)

The meta_meta_builder pattern is the most complex of the 6 defined
workflow patterns. It generates composition systems that are themselves
capable of generating workflows. The pattern enforces a 9-phase
structure with layered architecture (Component Schema, Composition
Format, Output Format) and supports self-bootstrapping through
spec embedding.

---

## Workflow Phases

The workflow is organized into 9 sequential phases. Each phase
produces one or more artifacts that feed subsequent phases. Phases
2-6 follow a generate-then-gatekeep pattern to enforce quality at
layer boundaries.

### Phase 1: Foundation (TDD Loop)

**Purpose:** Establish the acceptance criteria that all subsequent
phases validate against. The TDD (Test-Driven Development) loop
ensures criteria are reviewed and refined before use.

**Steps:** 3
- Step 01: generate_test_criteria (prompt)
- Step 02: review_test_criteria (prompt)
- Step 03: refine_test_criteria (prompt) -- conditional

**Artifacts produced:** TEST_CRITERIA_FILE, REVIEW_TEST_CRITERIA_FILE

**Review/refine loop:** Between steps 02 and 03. If the review
returns REJECTED, the refine step executes and produces an updated
TEST_CRITERIA_FILE. The loop has a maximum of 2 iterations.

**Criteria coverage:** TC-001 through TC-007

### Phase 2: Component Schema (Layer 1)

**Purpose:** Generate the component schema defining all 8 component
types with their schemas, validation rules, and examples. This is
Layer 1 of the three-layer architecture.

**Steps:** 2
- Step 04: generate_component_schema (prompt)
- Step 05: gatekeep_component_schema (prompt)

**Artifacts produced:** COMPONENT_SCHEMA_FILE, GATEKEEP_COMPONENT_SCHEMA_FILE

**Gatekeep enforcement:** The gatekeep step validates the generated
schema against criteria TC-008 through TC-015. If validation fails,
the workflow routes back to step 04 for regeneration.

**Criteria coverage:** TC-008 through TC-016

### Phase 3: Composition Format (Layer 2)

**Purpose:** Generate the composition format defining binding rules,
workflow patterns, override mechanisms, and placeholder resolution.
This is Layer 2 of the three-layer architecture.

**Steps:** 2
- Step 06: generate_composition_format (prompt)
- Step 07: gatekeep_composition_format (prompt)

**Artifacts produced:** COMPOSITION_FORMAT_FILE, GATEKEEP_COMPOSITION_FORMAT_FILE

**Gatekeep enforcement:** The gatekeep step validates the generated
format against criteria TC-017 through TC-023. If validation fails,
the workflow routes back to step 06 for regeneration.

**Criteria coverage:** TC-017 through TC-023

### Phase 4: Output Format (Layer 3)

**Purpose:** Generate the output format defining file structure,
resolution rules, quality requirements, and downstream extraction
contracts. This is Layer 3 of the three-layer architecture.

**Steps:** 2
- Step 08: generate_output_format (prompt)
- Step 09: gatekeep_output_format (prompt)

**Artifacts produced:** OUTPUT_FORMAT_FILE, GATEKEEP_OUTPUT_FORMAT_FILE

**Gatekeep enforcement:** The gatekeep step validates the generated
format against criteria TC-024 through TC-033. If validation fails,
the workflow routes back to step 08 for regeneration.

**Criteria coverage:** TC-024 through TC-034

### Phase 5: Operational Workflow

**Purpose:** Generate the operational workflow design defining all
phases, step sequences, routing, and artifact contracts. This is a
self-describing step -- it produces the blueprint for the workflow
itself.

**Steps:** 2
- Step 10: generate_operational_workflow (prompt)
- Step 11: gatekeep_operational_workflow (prompt)

**Artifacts produced:** OPERATIONAL_WORKFLOW_FILE, GATEKEEP_OPERATIONAL_WORKFLOW_FILE

**Gatekeep enforcement:** The gatekeep step validates the generated
workflow against criteria TC-035 through TC-043. If validation fails,
the workflow routes back to step 10 for regeneration.

**Criteria coverage:** TC-035 through TC-043

### Phase 6: Composition Standard (v3 Innovation)

**Purpose:** Generate the composition standard that the meta builder
will enforce on its own compositions. This is a v3 innovation that
makes the generated meta builder self-describing -- it knows its own
component types and structure.

**Steps:** 2
- Step 12: generate_composition_standard (prompt)
- Step 13: gatekeep_composition_standard (prompt)

**Artifacts produced:** COMPOSITION_STANDARD_FILE, GATEKEEP_COMPOSITION_STANDARD_FILE

**Gatekeep enforcement:** The gatekeep step validates the generated
standard against criteria TC-044 through TC-049. If validation fails,
the workflow routes back to step 12 for regeneration.

**Criteria coverage:** TC-044 through TC-050

### Phase 7: Meta Composition Spec (v3 Innovation)

**Purpose:** Generate the meta composition specification that
consolidates all layers into a single spec document. This is a v3
innovation that provides a comprehensive reference for the generated
meta builder.

**Steps:** 1
- Step 14: generate_meta_composition_spec (prompt)

**Artifacts produced:** META_COMPOSITION_SPEC_FILE

**No gatekeep:** This phase has no gatekeep step. The meta composition
spec is validated as part of the package validation in Phase 8.

**Criteria coverage:** TC-051, TC-052

### Phase 8: Package Assembly

**Purpose:** Assemble the complete workflow package from all prior
artifacts. This phase generates the executable workflow files, embeds
the builder spec, validates the package, and performs final review.

**Steps:** 5
- Step 15: generate_package (prompt)
- Step 16: validate_package_deterministic (action)
- Step 17: gatekeep_package (prompt)
- Step 18: review_package (prompt)
- Step 19: refine_package (prompt) -- conditional

**Artifacts produced:** WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE,
WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE,
STANDARDS_COMPOSITION_STANDARD_FILE, SPECS_BUILDER_SPEC_FILE,
VALIDATION_REPORT_FILE, GATEKEEP_PACKAGE_FILE, REVIEW_FILE_SUGGESTED

**Review/refine loop:** Between steps 18 and 19. If the review
returns REJECTED, the refine step executes and produces an updated
package. The loop has a maximum of 2 iterations.

**Criteria coverage:** TC-053 through TC-060

### Phase 9: Promotion

**Purpose:** Promote the validated 3-part output to the workflows/
directory. This phase copies all files to their final deployment
location and marks the workflow as complete.

**Steps:** 2
- Step 20: promote_workflow_package (action)
- Step 21: step_completion (action)

**Artifacts produced:** WORKFLOW_PACKAGE_DIR_FILE

**Enforcement:** The promote action enforces 3-part promotion. If
Standards/ or Specs/ is missing from the output, the action REJECTS
with error code MISSING_REQUIRED_OUTPUT_DIR.

**Criteria coverage:** TC-061 through TC-064

---

## Step Sequence

The following table defines the complete step sequence for the
Workflow Builder v3. Each step has a unique step number, name, type,
purpose, required inputs, produced outputs, and routing configuration.

| Step | Name | Type | Purpose | Required Inputs | Produces | Onsuccess | On_reject_refine |
|------|------|------|---------|-----------------|----------|-----------|------------------|
| 01 | generate_test_criteria | prompt | Generate acceptance criteria for the workflow | WORKFLOW_SPEC_FILE | TEST_CRITERIA_FILE | review_test_criteria | -- |
| 02 | review_test_criteria | prompt | Review the generated test criteria | TEST_CRITERIA_FILE | REVIEW_TEST_CRITERIA_FILE | generate_component_schema | refine_test_criteria (TEST_CRITERIA_FILE, max: 2) |
| 03 | refine_test_criteria | prompt | Refine test criteria based on review feedback | TEST_CRITERIA_FILE, REVIEW_TEST_CRITERIA_FILE | TEST_CRITERIA_FILE | review_test_criteria | -- |
| 04 | generate_component_schema | prompt | Generate the component schema for Layer 1 | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE | COMPONENT_SCHEMA_FILE | gatekeep_component_schema | -- |
| 05 | gatekeep_component_schema | prompt | Validate component schema against test criteria | COMPONENT_SCHEMA_FILE, TEST_CRITERIA_FILE | GATEKEEP_COMPONENT_SCHEMA_FILE | generate_composition_format | generate_component_schema (COMPONENT_SCHEMA_FILE, max: 2) |
| 06 | generate_composition_format | prompt | Generate the composition format for Layer 2 | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE | COMPOSITION_FORMAT_FILE | gatekeep_composition_format | -- |
| 07 | gatekeep_composition_format | prompt | Validate composition format against test criteria | COMPOSITION_FORMAT_FILE, TEST_CRITERIA_FILE | GATEKEEP_COMPOSITION_FORMAT_FILE | generate_output_format | generate_composition_format (COMPOSITION_FORMAT_FILE, max: 2) |
| 08 | generate_output_format | prompt | Generate the output format for Layer 3 | WORKFLOW_SPEC_FILE, COMPOSITION_FORMAT_FILE | OUTPUT_FORMAT_FILE | gatekeep_output_format | -- |
| 09 | gatekeep_output_format | prompt | Validate output format against test criteria | OUTPUT_FORMAT_FILE, TEST_CRITERIA_FILE | GATEKEEP_OUTPUT_FORMAT_FILE | generate_operational_workflow | generate_output_format (OUTPUT_FORMAT_FILE, max: 2) |
| 10 | generate_operational_workflow | prompt | Generate the operational workflow design | WORKFLOW_SPEC_FILE, OUTPUT_FORMAT_FILE | OPERATIONAL_WORKFLOW_FILE | gatekeep_operational_workflow | -- |
| 11 | gatekeep_operational_workflow | prompt | Validate operational workflow against test criteria | OPERATIONAL_WORKFLOW_FILE, TEST_CRITERIA_FILE | GATEKEEP_OPERATIONAL_WORKFLOW_FILE | generate_composition_standard | generate_operational_workflow (OPERATIONAL_WORKFLOW_FILE, max: 2) |
| 12 | generate_composition_standard | prompt | Generate the composition standard | WORKFLOW_SPEC_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE | COMPOSITION_STANDARD_FILE | gatekeep_composition_standard | -- |
| 13 | gatekeep_composition_standard | prompt | Validate composition standard against test criteria | COMPOSITION_STANDARD_FILE, TEST_CRITERIA_FILE | GATEKEEP_COMPOSITION_STANDARD_FILE | generate_meta_composition_spec | generate_composition_standard (COMPOSITION_STANDARD_FILE, max: 2) |
| 14 | generate_meta_composition_spec | prompt | Generate the meta composition specification | WORKFLOW_SPEC_FILE, COMPOSITION_STANDARD_FILE | META_COMPOSITION_SPEC_FILE | generate_package | -- |
| 15 | generate_package | prompt | Generate the complete workflow package | WORKFLOW_SPEC_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE | validate_package_deterministic | -- |
| 16 | validate_package_deterministic | action | Run deterministic validation checks on the package | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, STANDARDS_COMPOSITION_STANDARD_FILE, SPECS_BUILDER_SPEC_FILE | VALIDATION_REPORT_FILE | gatekeep_package | -- |
| 17 | gatekeep_package | prompt | Gatekeep the generated package | VALIDATION_REPORT_FILE, TEST_CRITERIA_FILE | GATEKEEP_PACKAGE_FILE | review_package | validate_package_deterministic (VALIDATION_REPORT_FILE, max: 2) |
| 18 | review_package | prompt | Final review of the generated package | GATEKEEP_PACKAGE_FILE, TEST_CRITERIA_FILE | REVIEW_FILE_SUGGESTED | promote_workflow_package | refine_package (REVIEW_FILE_SUGGESTED, max: 2) |
| 19 | refine_package | prompt | Refine the package based on review feedback | GATEKEEP_PACKAGE_FILE, REVIEW_FILE_SUGGESTED | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE | review_package | -- |
| 20 | promote_workflow_package | action | Promote the 3-part output to workflows/ directory | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE, SPECS_BUILDER_SPEC_FILE, WORKFLOW_PROMPTS_INDEX_FILE | WORKFLOW_PACKAGE_DIR_FILE | step_completion | -- |
| 21 | step_completion | action | Mark workflow as complete | WORKFLOW_PACKAGE_DIR_FILE | -- | -- | -- |

**Step type summary:**
- Prompt steps: 18 (steps 01-15, 17-19)
- Action steps: 3 (steps 16, 20, 21)

**Conditional steps:**
- Step 03 (refine_test_criteria): Executes only if step 02 returns REJECTED
- Step 19 (refine_package): Executes only if step 18 returns REJECTED

---

## Artifact Contract

### Input Artifacts

Input artifacts are provided to the workflow at startup. They are
not produced by any step within the workflow.

| Artifact Key | Description | Required | Source |
|--------------|-------------|----------|--------|
| WORKFLOW_SPEC_FILE | Composition system specification defining the meta builder to be generated | Yes | User input at workflow startup |

### Output Artifacts

Output artifacts are produced by workflow steps. Each artifact has
a unique key, a filename pattern, and a producing step.

| Artifact Key | Description | Filename Pattern | Produced By Step | Required |
|--------------|-------------|------------------|------------------|----------|
| TEST_CRITERIA_FILE | Acceptance criteria for the workflow | TEST_CRITERIA-{seq}.md | 01 generate_test_criteria | Yes |
| REVIEW_TEST_CRITERIA_FILE | Review of the test criteria | REVIEW_TEST_CRITERIA-{seq}.md | 02 review_test_criteria | Yes |
| COMPONENT_SCHEMA_FILE | Component schema defining 8 component types for Layer 1 | COMPONENT_SCHEMA-{seq}.md | 04 generate_component_schema | Yes |
| GATEKEEP_COMPONENT_SCHEMA_FILE | Gatekeep review of component schema | GATEKEEP_COMPONENT_SCHEMA-{seq}.md | 05 gatekeep_component_schema | Yes |
| COMPOSITION_FORMAT_FILE | Composition format defining binding rules for Layer 2 | COMPOSITION_FORMAT-{seq}.md | 06 generate_composition_format | Yes |
| GATEKEEP_COMPOSITION_FORMAT_FILE | Gatekeep review of composition format | GATEKEEP_COMPOSITION_FORMAT-{seq}.md | 07 gatekeep_composition_format | Yes |
| OUTPUT_FORMAT_FILE | Output format defining file structure for Layer 3 | OUTPUT_FORMAT-{seq}.md | 08 generate_output_format | Yes |
| GATEKEEP_OUTPUT_FORMAT_FILE | Gatekeep review of output format | GATEKEEP_OUTPUT_FORMAT-{seq}.md | 09 gatekeep_output_format | Yes |
| OPERATIONAL_WORKFLOW_FILE | Operational workflow design with phases and steps | OPERATIONAL_WORKFLOW-{seq}.md | 10 generate_operational_workflow | Yes |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | Gatekeep review of operational workflow | GATEKEEP_OPERATIONAL_WORKFLOW-{seq}.md | 11 gatekeep_operational_workflow | Yes |
| COMPOSITION_STANDARD_FILE | Composition standard for the generated meta builder | COMPOSITION_STANDARD-{seq}.md | 12 generate_composition_standard | Yes |
| GATEKEEP_COMPOSITION_STANDARD_FILE | Gatekeep review of composition standard | GATEKEEP_COMPOSITION_STANDARD-{seq}.md | 13 gatekeep_composition_standard | Yes |
| META_COMPOSITION_SPEC_FILE | Meta composition specification consolidating all layers | META_COMPOSITION_SPEC-{seq}.md | 14 generate_meta_composition_spec | Yes |
| WORKFLOW_MANIFEST_FILE | Workflow manifest (workflow.toml) | workflow.toml | 15 generate_package | Yes |
| WORKFLOW_EXTENSIONS_FILE | Context extensions module (context_extensions.py) | context_extensions.py | 15 generate_package | Yes |
| WORKFLOW_ACTIONS_FILE | Custom action implementations (actions.py) | actions.py | 15 generate_package | Yes |
| WORKFLOW_PROMPTS_INDEX_FILE | Index of prompt template files | prompts/index.txt | 15 generate_package | Yes |
| WORKFLOW_README_FILE | Workflow package documentation (README.md) | README.md | 15 generate_package | Yes |
| STANDARDS_COMPOSITION_STANDARD_FILE | Standards directory composition standard | Standards/COMPOSITION_STANDARD.md | 15 generate_package, 19 refine_package | Yes |
| SPECS_BUILDER_SPEC_FILE | Embedded builder spec for self-bootstrap | Specs/{builder_name}.md | 15 generate_package | Yes |
| VALIDATION_REPORT_FILE | Validation report with 11 check results | VALIDATION_REPORT-{seq}.md | 16 validate_package_deterministic | Yes |
| GATEKEEP_PACKAGE_FILE | Gatekeep review of the package | GATEKEEP_PACKAGE-{seq}.md | 17 gatekeep_package | Yes |
| REVIEW_FILE_SUGGESTED | Final review of the package | REVIEW-{seq}.md | 18 review_package | Yes |
| WORKFLOW_PACKAGE_DIR_FILE | Promoted workflow package directory path | workflows/{slug}/ | 20 promote_workflow_package | Yes |

**Artifact flow integrity:** Every artifact consumed by a step is
produced by a preceding step or declared as a workflow input. No
dangling references exist in the artifact flow.

---

## Action Specifications

Three steps in the workflow are implemented as deterministic Python
actions rather than LLM-driven prompts. These actions perform
structural validation, file copying, and deployment operations that
require exact, repeatable behavior.

### Action 1: validate_package_deterministic (Step 16)

**Step name:** validate_package_deterministic
**Step type:** action
**Coder role:** validation_standard
**Position:** Phase 8, after generate_package

**Purpose:** Run 11 deterministic validation checks on the generated
workflow package. This action performs static analysis to verify
structural correctness before the gatekeep and review steps.

**Required inputs:**
- WORKFLOW_MANIFEST_FILE (workflow.toml)
- WORKFLOW_EXTENSIONS_FILE (context_extensions.py)
- WORKFLOW_ACTIONS_FILE (actions.py)
- STANDARDS_COMPOSITION_STANDARD_FILE (Standards/COMPOSITION_STANDARD.md)
- SPECS_BUILDER_SPEC_FILE (Specs/{builder_name}.md)

**Produces:** VALIDATION_REPORT_FILE

**Validation checks (11):**

| Check # | Description | Severity |
|---------|-------------|----------|
| 1 | TOML parse validity of workflow.toml | CRITICAL |
| 2 | Python syntax validity of context_extensions.py and actions.py | CRITICAL |
| 3 | TYPE_CHECKING runtime import detection | CRITICAL |
| 4 | Artifact binding consistency (no dangling references) | CRITICAL |
| 5 | Action step implementation completeness | CRITICAL |
| 6 | Prompt file existence (one .txt per prompt step) | CRITICAL |
| 7 | Prompt placeholder vs required_inputs consistency | CRITICAL |
| 8 | context_extensions.py artifact key coverage | CRITICAL |
| 9 | Standards/COMPOSITION_STANDARD.md existence | CRITICAL |
| 10 | Specs/ directory exists with at least one .md file | CRITICAL |
| 11 | Bidirectional prompt placeholder vs artifact declaration consistency | CRITICAL |

**Output format:** The VALIDATION_REPORT_FILE contains a table listing
each of the 11 checks with pass/fail status and specific failure
messages for any check that does not pass.

**Routing:** On completion (all checks pass), routes to
gatekeep_package (step 17). If any check fails, the report still
produces output but gatekeep_package will reject.

**Implementation pattern:**
```python
@action("validate_package_deterministic")
def validate_package_deterministic(*, context, state, step_cfg, project_root):
    """Run 11 deterministic validation checks on the package."""
    checks = []
    # Check 1: TOML parse validity
    # Check 2: Python syntax check
    # Check 3: TYPE_CHECKING runtime import detection
    # Check 4: Artifact binding consistency
    # Check 5: Action step implementation completeness
    # Check 6: Prompt file existence
    # Check 7: Prompt placeholder vs required_inputs consistency
    # Check 8: context_extensions.py artifact key coverage
    # Check 9: Standards/COMPOSITION_STANDARD.md existence
    # Check 10: Specs/ directory with .md files
    # Check 11: Bidirectional placeholder consistency
    return {
        "status": "APPROVED" if all(c["passed"] for c in checks) else "REJECTED",
        "remark": f"Validation complete: {sum(c['passed'] for c in checks)}/11 checks passed",
        "artifacts": {"VALIDATION_REPORT_FILE": str(report_path)},
    }
```

### Action 2: promote_workflow_package (Step 20)

**Step name:** promote_workflow_package
**Step type:** action
**Coder role:** validation_standard
**Position:** Phase 9, after review_package

**Purpose:** Copy the validated 3-part output to the workflows/
directory. This action enforces that all 3 parts (Standards/, Specs/,
workflow package) are present before promotion.

**Required inputs:**
- WORKFLOW_MANIFEST_FILE (workflow.toml)
- WORKFLOW_EXTENSIONS_FILE (context_extensions.py)
- WORKFLOW_ACTIONS_FILE (actions.py)
- WORKFLOW_README_FILE (README.md)
- STANDARDS_COMPOSITION_STANDARD_FILE (Standards/COMPOSITION_STANDARD.md)
- SPECS_BUILDER_SPEC_FILE (Specs/{builder_name}.md)
- WORKFLOW_PROMPTS_INDEX_FILE (prompts/index.txt)

**Produces:** WORKFLOW_PACKAGE_DIR_FILE

**Promotion contract (9 file/directory mappings):**

| Source | Target | Mandatory |
|--------|--------|-----------|
| output/workflow.toml | workflows/{slug}/workflow.toml | Yes |
| output/context_extensions.py | workflows/{slug}/context_extensions.py | Yes |
| output/actions.py | workflows/{slug}/actions.py | If exists |
| output/README.md | workflows/{slug}/README.md | Yes |
| output/prompts/ | workflows/{slug}/prompts/ | Yes |
| output/Standards/ | workflows/{slug}/Standards/ | Yes (enforced) |
| output/Specs/ | workflows/{slug}/Specs/ | Yes (enforced) |
| output/.env.sample | workflows/{slug}/.env.sample | If exists |
| output/config.json.sample | workflows/{slug}/config.json.sample | If exists |

**Enforcement:** If Standards/ or Specs/ is missing from the output,
the action REJECTS with status REJECTED and error code
MISSING_REQUIRED_OUTPUT_DIR. This prevents silent omission of
required output directories.

**Implementation pattern:**
```python
@action("promote_workflow_package")
def promote_workflow_package(*, context, state, step_cfg, project_root):
    """Promote the 3-part output to the workflows/ directory."""
    source_dir = Path(context["WORKFLOW_MANIFEST_FILE"]).parent
    slug = context["builder_name"]
    target_dir = Path(project_root) / "workflows" / slug
    
    # Enforcement: reject if Standards/ or Specs/ missing
    for required_dir in ["Standards", "Specs"]:
        src = source_dir / required_dir
        if not src.is_dir():
            return {
                "status": "REJECTED",
                "remark": f"Required output directory '{required_dir}/' not found. "
                          f"v3 requires 3-part output: Standards/, Specs/, workflow files.",
                "reject_code": "MISSING_REQUIRED_OUTPUT_DIR",
            }
    
    # Copy all files and directories
    # ...
    return {
        "status": "APPROVED",
        "remark": f"Promoted 3-part output to workflows/{slug}/",
        "artifacts": {"WORKFLOW_PACKAGE_DIR_FILE": str(target_dir)},
    }
```

### Action 3: step_completion (Step 21)

**Step name:** step_completion
**Step type:** action
**Coder role:** validation_standard
**Position:** Phase 9, final step

**Purpose:** Mark the workflow as complete. This is the terminal step
that executes only after promote_workflow_package returns APPROVED
status. It performs final cleanup and notification.

**Required inputs:**
- WORKFLOW_PACKAGE_DIR_FILE (promoted workflow directory path)

**Produces:** None (terminal step)

**Routing:** No onsuccess routing (terminal step).

**Execution condition:** This step executes only if step 20
(promote_workflow_package) returns APPROVED status. If promotion
fails, this step does not execute.

**Implementation pattern:**
```python
@action("step_completion")
def step_completion(*, context, state, step_cfg, project_root):
    """Mark workflow as complete."""
    workflow_dir = context["WORKFLOW_PACKAGE_DIR_FILE"]
    return {
        "status": "APPROVED",
        "remark": f"Workflow complete. Package deployed at: {workflow_dir}",
        "artifacts": {},
    }
```

---

## Review/Refine Loop Design

The workflow defines 2 review/refine loops that enforce quality
through iterative improvement. Each loop has a review step that
evaluates an artifact and a refine step that improves it if rejected.

### Loop 1: Test Criteria Review/Refine (Phase 1)

**Loop ID:** LOOP-001
**Review step:** 02 review_test_criteria
**Refine step:** 03 refine_test_criteria
**Artifact under review:** TEST_CRITERIA_FILE
**Maximum iterations:** 2
**Exhausted failure code:** TEST_CRITERIA_REVIEW_EXHAUSTED
**Exhausted failure class:** HUMAN_RETRY_REQUIRED

**Loop flow:**
1. Step 01 produces TEST_CRITERIA_FILE
2. Step 02 reviews TEST_CRITERIA_FILE and produces REVIEW_TEST_CRITERIA_FILE
3. If step 02 returns APPROVED: workflow proceeds to step 04
4. If step 02 returns REJECTED: workflow routes to step 03
5. Step 03 refines TEST_CRITERIA_FILE based on REVIEW_TEST_CRITERIA_FILE
6. Step 03 routes back to step 02 for re-review
7. If step 02 rejects again after 2 iterations: terminal failure

**Entry condition:** Step 03 executes only when step 02 returns
REJECTED status.

**Exit condition:** Step 02 returns APPROVED status, or maximum
iterations (2) are exhausted.

### Loop 2: Package Review/Refine (Phase 8)

**Loop ID:** LOOP-002
**Review step:** 18 review_package
**Refine step:** 19 refine_package
**Artifact under review:** WORKFLOW_MANIFEST_FILE (and associated package files)
**Maximum iterations:** 2
**Exhausted failure code:** PACKAGE_REVIEW_EXHAUSTED
**Exhausted failure class:** HUMAN_RETRY_REQUIRED

**Loop flow:**
1. Step 15 produces the complete workflow package
2. Step 16 validates the package (11 checks)
3. Step 17 gatekeeps the package
4. Step 18 reviews the package and produces REVIEW_FILE_SUGGESTED
5. If step 18 returns APPROVED: workflow proceeds to step 20
6. If step 18 returns REJECTED: workflow routes to step 19
7. Step 19 refines the package based on REVIEW_FILE_SUGGESTED
8. Step 19 routes back to step 18 for re-review
9. If step 18 rejects again after 2 iterations: terminal failure

**Entry condition:** Step 19 executes only when step 18 returns
REJECTED status.

**Exit condition:** Step 18 returns APPROVED status, or maximum
iterations (2) are exhausted.

**Refine scope:** The refine_package step (step 19) regenerates the
entire package including:
- WORKFLOW_MANIFEST_FILE (workflow.toml)
- WORKFLOW_EXTENSIONS_FILE (context_extensions.py)
- WORKFLOW_ACTIONS_FILE (actions.py)
- WORKFLOW_PROMPTS_INDEX_FILE (prompts/index.txt)
- WORKFLOW_README_FILE (README.md)
- STANDARDS_COMPOSITION_STANDARD_FILE (Standards/COMPOSITION_STANDARD.md)

This ensures that both generate_package (step 15) and refine_package
(step 19) declare STANDARDS_COMPOSITION_STANDARD_FILE in their
produces lists, satisfying validation rule VR-016.

### Gatekeep Loops (Phases 2-6)

Phases 2 through 6 each have a gatekeep step that can route back to
the preceding generate step if validation fails. These are not
full review/refine loops -- they are single-step rejection loops
where the generate step is re-executed.

| Phase | Gatekeep Step | Generate Step | Max Iterations | Exhausted Failure Code |
|-------|---------------|---------------|----------------|------------------------|
| 2 | 05 gatekeep_component_schema | 04 generate_component_schema | 2 | COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED |
| 3 | 07 gatekeep_composition_format | 06 generate_composition_format | 2 | COMPOSITION_FORMAT_GATEKEEP_EXHAUSTED |
| 4 | 09 gatekeep_output_format | 08 generate_output_format | 2 | OUTPUT_FORMAT_GATEKEEP_EXHAUSTED |
| 5 | 11 gatekeep_operational_workflow | 10 generate_operational_workflow | 2 | OPERATIONAL_WORKFLOW_GATEKEEP_EXHAUSTED |
| 6 | 13 gatekeep_composition_standard | 12 generate_composition_standard | 2 | COMPOSITION_STANDARD_GATEKEEP_EXHAUSTED |

**Gatekeep loop flow:**
1. Generate step produces artifact
2. Gatekeep step validates artifact against test criteria
3. If gatekeep returns APPROVED: workflow proceeds to next phase
4. If gatekeep returns REJECTED: workflow routes back to generate step
5. If gatekeep rejects again after 2 iterations: terminal failure

---

## Package File Inventory

The generated workflow package consists of core files, conditional
files, prompt files, and supplementary files. All files are produced
during Phase 8 (Package Assembly) and promoted during Phase 9.

### Core Files

Core files are always present in the generated package. They form
the executable workflow definition.

| File | Artifact Key | Description |
|------|--------------|-------------|
| workflow.toml | WORKFLOW_MANIFEST_FILE | Workflow manifest with step definitions, artifact bindings, routing, and coder role assignments |
| context_extensions.py | WORKFLOW_EXTENSIONS_FILE | Python module providing artifact key registration, context injection, and placeholder resolution |
| actions.py | WORKFLOW_ACTIONS_FILE | Python module containing custom action step implementations |
| README.md | WORKFLOW_README_FILE | Human-readable documentation for the workflow package |

### Conditional Files

Conditional files are present only if the workflow requires external
configuration or credentials.

| File | Artifact Key | Condition | Description |
|------|--------------|-----------|-------------|
| .env.sample | -- | If workflow requires environment variables | Sample environment variables file |
| config.json.sample | -- | If workflow requires JSON configuration | Sample configuration file |

### Prompt Files

Prompt files are generated in the prompts/ directory. One .txt file
is created per prompt-type step. Files are named with a two-digit
step sequence prefix and the step name.

| File | Step | Description |
|------|------|-------------|
| prompts/01_generate_test_criteria.txt | 01 | Prompt template for generating acceptance criteria |
| prompts/02_review_test_criteria.txt | 02 | Prompt template for reviewing test criteria |
| prompts/03_refine_test_criteria.txt | 03 | Prompt template for refining test criteria |
| prompts/04_generate_component_schema.txt | 04 | Prompt template for generating component schema |
| prompts/05_gatekeep_component_schema.txt | 05 | Prompt template for gatekeeping component schema |
| prompts/06_generate_composition_format.txt | 06 | Prompt template for generating composition format |
| prompts/07_gatekeep_composition_format.txt | 07 | Prompt template for gatekeeping composition format |
| prompts/08_generate_output_format.txt | 08 | Prompt template for generating output format |
| prompts/09_gatekeep_output_format.txt | 09 | Prompt template for gatekeeping output format |
| prompts/10_generate_operational_workflow.txt | 10 | Prompt template for generating operational workflow |
| prompts/11_gatekeep_operational_workflow.txt | 11 | Prompt template for gatekeeping operational workflow |
| prompts/12_generate_composition_standard.txt | 12 | Prompt template for generating composition standard |
| prompts/13_gatekeep_composition_standard.txt | 13 | Prompt template for gatekeeping composition standard |
| prompts/14_generate_meta_composition_spec.txt | 14 | Prompt template for generating meta composition spec |
| prompts/15_generate_package.txt | 15 | Prompt template for generating the complete package |
| prompts/17_gatekeep_package.txt | 17 | Prompt template for gatekeeping the package |
| prompts/18_review_package.txt | 18 | Prompt template for final package review |
| prompts/19_refine_package.txt | 19 | Prompt template for refining the package |

**Prompt file count:** 18 files (one per prompt-type step)

**Prompt file naming convention:** NN_{step_name}.txt where NN is
the two-digit step sequence number and {step_name} is the step name
from the step sequence table.

### Supplementary Files

Supplementary files are generated in the Standards/ and Specs/
directories. These files implement the 3-part output structure.

| File | Artifact Key | Directory | Description |
|------|--------------|-----------|-------------|
| Standards/COMPOSITION_STANDARD.md | STANDARDS_COMPOSITION_STANDARD_FILE | Standards/ | Composition standard for the generated meta builder |
| Specs/{builder_name}.md | SPECS_BUILDER_SPEC_FILE | Specs/ | Embedded builder spec for self-bootstrapping |

**3-part output structure:**
```
{builder_name}/
|-- Standards/
|   +-- COMPOSITION_STANDARD.md
|-- Specs/
|   +-- {builder_name}.md
|-- workflow.toml
|-- context_extensions.py
|-- actions.py
|-- prompts/
|   |-- 01_generate_test_criteria.txt
|   |-- ...
|   +-- 19_refine_package.txt
|-- README.md
|-- .env.sample              (conditional)
+-- config.json.sample       (conditional)
```

---

## Self-Validation

This section verifies that the operational workflow document satisfies
all defined requirements and constraints.

### Phase Completeness

| Phase | Purpose | Step Count | Expected | Actual | Status |
|-------|---------|------------|----------|--------|--------|
| 1 | Foundation (TDD Loop) | 3 | 3 | 3 | PASS |
| 2 | Component Schema (Layer 1) | 2 | 2 | 2 | PASS |
| 3 | Composition Format (Layer 2) | 2 | 2 | 2 | PASS |
| 4 | Output Format (Layer 3) | 2 | 2 | 2 | PASS |
| 5 | Operational Workflow | 2 | 2 | 2 | PASS |
| 6 | Composition Standard (v3) | 2 | 2 | 2 | PASS |
| 7 | Meta Composition Spec (v3) | 1 | 1 | 1 | PASS |
| 8 | Package Assembly | 5 | 5 | 5 | PASS |
| 9 | Promotion | 2 | 2 | 2 | PASS |
| **Total** | | **21** | **21** | **21** | **PASS** |

**Verification:** All 9 phases defined. Step counts match. TC-035
satisfied.

### Step Routing Completeness

| Step | Onsuccess | Valid Target | On_reject_refine | Valid Target |
|------|-----------|--------------|------------------|--------------|
| 01 | review_test_criteria | YES (step 02) | -- | -- |
| 02 | generate_component_schema | YES (step 04) | refine_test_criteria | YES (step 03) |
| 03 | review_test_criteria | YES (step 02) | -- | -- |
| 04 | gatekeep_component_schema | YES (step 05) | -- | -- |
| 05 | generate_composition_format | YES (step 06) | generate_component_schema | YES (step 04) |
| 06 | gatekeep_composition_format | YES (step 07) | -- | -- |
| 07 | generate_output_format | YES (step 08) | generate_composition_format | YES (step 06) |
| 08 | gatekeep_output_format | YES (step 09) | -- | -- |
| 09 | generate_operational_workflow | YES (step 10) | generate_output_format | YES (step 08) |
| 10 | gatekeep_operational_workflow | YES (step 11) | -- | -- |
| 11 | generate_composition_standard | YES (step 12) | generate_operational_workflow | YES (step 10) |
| 12 | gatekeep_composition_standard | YES (step 13) | -- | -- |
| 13 | generate_meta_composition_spec | YES (step 14) | generate_composition_standard | YES (step 12) |
| 14 | generate_package | YES (step 15) | -- | -- |
| 15 | validate_package_deterministic | YES (step 16) | -- | -- |
| 16 | gatekeep_package | YES (step 17) | -- | -- |
| 17 | review_package | YES (step 18) | validate_package_deterministic | YES (step 16) |
| 18 | promote_workflow_package | YES (step 20) | refine_package | YES (step 19) |
| 19 | review_package | YES (step 18) | -- | -- |
| 20 | step_completion | YES (step 21) | -- | -- |
| 21 | -- | -- (terminal) | -- | -- |

**Verification:** All 21 steps have valid onsuccess routing (except
terminal step 21). All reject-refine loops route to valid targets.
TC-038 satisfied.

### Artifact Flow Integrity

Every artifact consumed by a step must be produced by a preceding
step or declared as a workflow input.

| Artifact Key | Produced By | Consumed By | Flow Valid |
|--------------|-------------|-------------|------------|
| WORKFLOW_SPEC_FILE | User input | 01, 04, 06, 08, 10, 12, 14, 15 | YES |
| TEST_CRITERIA_FILE | 01 (and 03) | 02, 03, 04, 05, 06, 07, 09, 11, 13, 17, 18 | YES |
| REVIEW_TEST_CRITERIA_FILE | 02 | 03 | YES |
| COMPONENT_SCHEMA_FILE | 04 | 05, 06, 12 | YES |
| GATEKEEP_COMPONENT_SCHEMA_FILE | 05 | (not consumed) | YES |
| COMPOSITION_FORMAT_FILE | 06 | 07, 08, 12 | YES |
| GATEKEEP_COMPOSITION_FORMAT_FILE | 07 | (not consumed) | YES |
| OUTPUT_FORMAT_FILE | 08 | 09, 10, 12 | YES |
| GATEKEEP_OUTPUT_FORMAT_FILE | 09 | (not consumed) | YES |
| OPERATIONAL_WORKFLOW_FILE | 10 | 11 | YES |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | 11 | (not consumed) | YES |
| COMPOSITION_STANDARD_FILE | 12 | 13, 14, 15 | YES |
| GATEKEEP_COMPOSITION_STANDARD_FILE | 13 | (not consumed) | YES |
| META_COMPOSITION_SPEC_FILE | 14 | 15 | YES |
| WORKFLOW_MANIFEST_FILE | 15 (and 19) | 16, 20 | YES |
| WORKFLOW_EXTENSIONS_FILE | 15 (and 19) | 16, 20 | YES |
| WORKFLOW_ACTIONS_FILE | 15 (and 19) | 16, 20 | YES |
| WORKFLOW_PROMPTS_INDEX_FILE | 15 (and 19) | 20 | YES |
| WORKFLOW_README_FILE | 15 (and 19) | 20 | YES |
| STANDARDS_COMPOSITION_STANDARD_FILE | 15 (and 19) | 16, 20 | YES |
| SPECS_BUILDER_SPEC_FILE | 15 | 16, 20 | YES |
| VALIDATION_REPORT_FILE | 16 | 17 | YES |
| GATEKEEP_PACKAGE_FILE | 17 | 18, 19 | YES |
| REVIEW_FILE_SUGGESTED | 18 | 19 | YES |
| WORKFLOW_PACKAGE_DIR_FILE | 20 | 21 | YES |

**Verification:** All artifact flows are valid. No dangling references.
Every consumed artifact is produced by a preceding step or declared
as a workflow input. TC-043 satisfied.

### Type Classification

| Step Type | Count | Steps |
|-----------|-------|-------|
| prompt | 18 | 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 17, 18, 19 |
| action | 3 | 16, 20, 21 |
| **Total** | **21** | |

**Verification:** 18 prompt steps + 3 action steps = 21 total steps.
Matches frontmatter declaration.

### v3 Innovation Phases

| Phase | Innovation | Present | Verified |
|-------|------------|---------|----------|
| 6 | Composition Standard generation | YES | TC-044 to TC-050 |
| 7 | Meta Composition Spec generation | YES | TC-051 to TC-052 |

**Verification:** Both v3 innovation phases (6 and 7) are defined
in the operational workflow.

### Criteria Traceability

| Criteria | Status | Evidence |
|----------|--------|----------|
| TC-035 | PASS | 9 phases defined in Workflow Phases section |
| TC-036 | PASS | 21 steps defined across 9 phases |
| TC-037 | PASS | Each step declares step_type (prompt or action) |
| TC-038 | PASS | All steps have onsuccess routing; reject-refine loops defined |
| TC-039 | PASS | Phase 1 has steps 01, 02, 03 with refine loop |
| TC-040 | PASS | Phase 8 has steps 15-19 with validation and review |
| TC-041 | PASS | Phase 9 has steps 20, 21 (promote and completion) |
| TC-042 | PASS | All input/output artifacts declared per step |
| TC-043 | PASS | Artifact flow integrity verified in table above |

**Verification:** All Phase 5 criteria (TC-035 through TC-043) are
satisfied by this document.

---

End of Operational Workflow Document
