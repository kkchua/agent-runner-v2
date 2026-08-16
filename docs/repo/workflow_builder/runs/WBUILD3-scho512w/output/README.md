# Workflow Builder v3

Meta-meta builder that generates composition system workflows (meta builders).
Each generated meta builder is itself a composition system with its own
composition standard, enabling extensibility and self-bootstrapping.

## Overview

Workflow Builder v3 is a 21-step, 9-phase TDD-driven pipeline that transforms
a runtime specification into a complete, executable workflow package. The
workflow follows the `meta_meta_builder` pattern with 18 prompt-driven steps
and 3 action-driven steps.

**Workflow name:** workflow_builder_v3
**Version:** 1.0.0
**Job prefix:** WBUILD3
**Output delivery type:** documented_versioned
**Layer:** layer3
**Platform:** agent-runner-v2

## Prerequisites

- Python 3.12+ with agent-runner-v2 installed
- Runtime spec file (markdown with YAML frontmatter) as input
- Base composition standard (COMPOSITION_SYSTEM_STANDARD.md) accessible

## Usage

### CLI Execution

```bash
ukbe-run-agent run --template-group workflow_builder_v3
```

### Daemon Execution

```bash
ukbe-run-agent daemon [worker-id]
```

The daemon polls the backend for job claims and spawns a child subprocess
per workflow invocation.

## Workflow Phases

| Phase | Purpose | Steps |
|-------|---------|-------|
| 1. Foundation (TDD Loop) | Generate, review, and refine acceptance criteria | 3 |
| 2. Component Schema (Layer 1) | Define 8 component types and validation rules | 2 |
| 3. Composition Format (Layer 2) | Define binding rules and override mechanisms | 2 |
| 4. Output Format (Layer 3) | Define output structure and resolution rules | 2 |
| 5. Operational Workflow | Define step sequence with routing | 2 |
| 6. Composition Standard (v3) | Consolidate all layers into standard | 2 |
| 7. Meta Composition Spec (v3) | Produce self-bootstrapping spec | 1 |
| 8. Package Assembly | Generate workflow package files | 5 |
| 9. Promotion | Deploy to workflows/ directory | 2 |

## Step Reference

| Step | Name | Type | Role Policy | Produces |
|------|------|------|-------------|----------|
| 01 | generate_test_criteria | prompt | architect_standard | TEST_CRITERIA_FILE |
| 02 | review_test_criteria | prompt | reviewer_standard | REVIEW_TEST_CRITERIA_FILE |
| 03 | refine_test_criteria | prompt | architect_standard | TEST_CRITERIA_FILE |
| 04 | generate_component_schema | prompt | architect_standard | COMPONENT_SCHEMA_FILE |
| 05 | gatekeep_component_schema | prompt | gatekeeper_standard | GATEKEEP_COMPONENT_SCHEMA_FILE |
| 06 | generate_composition_format | prompt | architect_standard | COMPOSITION_FORMAT_FILE |
| 07 | gatekeep_composition_format | prompt | gatekeeper_standard | GATEKEEP_COMPOSITION_FORMAT_FILE |
| 08 | generate_output_format | prompt | architect_standard | OUTPUT_FORMAT_FILE |
| 09 | gatekeep_output_format | prompt | gatekeeper_standard | GATEKEEP_OUTPUT_FORMAT_FILE |
| 10 | generate_operational_workflow | prompt | architect_standard | OPERATIONAL_WORKFLOW_FILE |
| 11 | gatekeep_operational_workflow | prompt | gatekeeper_standard | GATEKEEP_OPERATIONAL_WORKFLOW_FILE |
| 12 | generate_composition_standard | prompt | architect_standard | COMPOSITION_STANDARD_FILE |
| 13 | gatekeep_composition_standard | prompt | gatekeeper_standard | GATEKEEP_COMPOSITION_STANDARD_FILE |
| 14 | generate_meta_composition_spec | prompt | architect_standard | META_COMPOSITION_SPEC_FILE |
| 15 | generate_package | prompt | architect_standard | WORKFLOW_MANIFEST_FILE + 5 files |
| 16 | validate_package_deterministic | action | -- | VALIDATION_REPORT_FILE |
| 17 | gatekeep_package | prompt | gatekeeper_standard | GATEKEEP_PACKAGE_FILE |
| 18 | review_package | prompt | reviewer_standard | REVIEW_FILE_SUGGESTED |
| 19 | refine_package | prompt | architect_standard | WORKFLOW_MANIFEST_FILE + 5 files |
| 20 | promote_workflow_package | action | -- | WORKFLOW_PACKAGE_DIR_FILE |
| 21 | step_completion | action | -- | COMPLETION_RESULT |

## Artifact Keys

| Artifact Key | Description |
|--------------|-------------|
| WORKFLOW_SPEC_FILE | Runtime specification input |
| TEST_CRITERIA_FILE | Acceptance criteria for all 9 phases |
| REVIEW_TEST_CRITERIA_FILE | Critic review of test criteria |
| COMPONENT_SCHEMA_FILE | Layer 1 component schema |
| GATEKEEP_COMPONENT_SCHEMA_FILE | Gatekeep verdict for schema |
| COMPOSITION_FORMAT_FILE | Layer 2 composition format |
| GATEKEEP_COMPOSITION_FORMAT_FILE | Gatekeep verdict for format |
| OUTPUT_FORMAT_FILE | Layer 3 output format |
| GATEKEEP_OUTPUT_FORMAT_FILE | Gatekeep verdict for output |
| OPERATIONAL_WORKFLOW_FILE | Operational workflow design |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | Gatekeep verdict for workflow |
| COMPOSITION_STANDARD_FILE | Consolidated composition standard |
| GATEKEEP_COMPOSITION_STANDARD_FILE | Gatekeep verdict for standard |
| META_COMPOSITION_SPEC_FILE | Meta composition spec (self-bootstrap) |
| WORKFLOW_MANIFEST_FILE | workflow.toml |
| WORKFLOW_EXTENSIONS_FILE | context_extensions.py |
| WORKFLOW_ACTIONS_FILE | actions.py |
| WORKFLOW_PROMPTS_INDEX_FILE | prompts_index.json |
| WORKFLOW_README_FILE | README.md |
| STANDARDS_COMPOSITION_STANDARD_FILE | Standards/COMPOSITION_STANDARD.md |
| VALIDATION_REPORT_FILE | Deterministic validation report |
| GATEKEEP_PACKAGE_FILE | Gatekeep verdict for package |
| REVIEW_FILE_SUGGESTED | Quality review of package |
| WORKFLOW_PACKAGE_DIR_FILE | Promoted package directory path |
| COMPLETION_RESULT | Final outcome record |

## Architecture

### 3-Layer Design

The workflow follows a 3-layer composition system architecture:

- **Layer 1 (Component Schema):** Defines 8 component types with common
  properties, type-specific properties, and 8 validation rules (VR-001
  through VR-008).

- **Layer 2 (Composition Format):** Defines how components bind together
  with 8 binding rules, 6 workflow patterns, override mechanism, and
  7 placeholders.

- **Layer 3 (Output Format):** Defines the resolved output with 3-part
  directory structure, 7 resolution rules, and quality requirements.

### Three-Tier Quality Gate

Each phase applies a three-tier quality gate:

1. **Critic (review):** Reviews the test quality -- do these tests test
   the right thing?
2. **Validate (action):** Deterministic checks -- files exist, parse
   correctly, identity matches.
3. **Gatekeeper (prompt):** Runs validated test criteria against artifact
   with pass/fail and evidence.

### v3 Innovations

1. **Composition Standard (Phase 6):** Every generated meta builder has
   its own self-describing composition standard, enabling extensibility.

2. **Meta Composition Spec (Phase 7):** Enables self-bootstrapping -- the
   generated spec can be fed as input to the builder to produce the next
   version.

## File Structure

```
workflow_builder_v3/
  Standards/
    COMPOSITION_STANDARD.md
  Specs/
    (user-provided specs at runtime)
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
  prompts_index.json
  README.md
```
