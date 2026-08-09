# AR Meta Builder v2

**Version:** 2.0.0
**Job prefix:** AMB
**Layer:** layer3
**Platform:** agent-runner-v2

## Overview

AR Meta Builder v2 is a composition system meta-builder that transforms
a runtime specification into a complete, executable workflow package.
It uses a 9-phase TDD-driven pipeline with identity locking and base
schema fine-tuning to produce target workflows that are fully
self-contained and deployable.

The workflow follows the recursive chain:
Workflow Builder v4 -> AMB v2 -> [target workflow]

## Description

Given a runtime spec (markdown with YAML frontmatter), AMB v2:

1. Analyzes the target domain and generates acceptance criteria
2. Fine-tunes the Base Component Schema for the target domain (Layer 1)
3. Derives the Composition Format from the domain schema (Layer 2)
4. Derives the Output Format from the composition (Layer 3)
5. Defines the Artifact Contract for the target workflow
6. Designs the Step Sequence with routing and artifact flow
7. Consolidates all layers into a Runtime Standard
8. Designs the Operational Workflow implementation
9. Assembles the complete executable workflow package

Each phase follows the standardized TDD unit pattern:
generate -> review -> refine -> validate -> gatekeep

## Prerequisites

- Python 3.12+ with agent-runner-v2 installed
- Runtime spec file (markdown with YAML frontmatter) as input
- Base composition standard (COMPOSITION_SYSTEM_STANDARD.md) accessible
- Global runner home initialized (`ukbe-run-agent init`)

## Usage

### CLI Execution

```bash
ukbe-run-agent run --template-group ar_meta_builder_v2
```

### Daemon Execution

```bash
ukbe-run-agent daemon [worker-id]
```

The daemon polls the backend for job claims and spawns a child
subprocess per workflow invocation.

## Workflow Phases

| Phase | Name | Steps | Description |
|-------|------|-------|-------------|
| 0 | Input Validation | 1 | Validate input spec format and content |
| 1 | Analyze Spec | 6 | Domain analysis + meta test criteria (TDD) |
| 2 | Domain Component Schema | 5 | Layer 1: component types and validation rules |
| 3 | Composition Format | 5 | Layer 2: binding rules and override mechanisms |
| 4 | Output Format | 5 | Layer 3: output structure and resolution rules |
| 5 | Component Artifacts | 5 | Artifact contract: input/output per component |
| 6 | Domain Steps | 5 | Step sequence with routing and artifact flow |
| 7 | Runtime Standard | 5 | Consolidate all 3 layers into one standard |
| 8 | Operational Workflow | 5 | Concrete workflow implementation design |
| 9 | Package Assembly | 6 | Generate package files + promote |

## Step Reference

| # | Name | Type | Role Policy | Produces |
|---|------|------|-------------|----------|
| 1 | validate_input_spec | action | -- | VALIDATION_INPUT_SPEC_FILE |
| 2 | generate_test_criteria | prompt | architect_standard | TEST_CRITERIA_FILE |
| 3 | review_test_criteria | prompt | reviewer_standard | REVIEW_TEST_CRITERIA_FILE |
| 4 | refine_test_criteria | prompt | architect_standard | TEST_CRITERIA_FILE |
| 5 | generate_domain_analysis | prompt | architect_standard | DOMAIN_ANALYSIS_FILE |
| 6 | validate_domain_analysis | action | -- | VALIDATE_DOMAIN_ANALYSIS_FILE |
| 7 | gatekeep_domain_analysis | prompt | gatekeeper_standard | GATEKEEP_DOMAIN_ANALYSIS_FILE |
| 8 | generate_component_schema | prompt | architect_standard | DOMAIN_COMPONENT_SCHEMA_FILE |
| 9 | review_component_schema | prompt | reviewer_standard | REVIEW_COMPONENT_SCHEMA_FILE |
| 10 | refine_component_schema | prompt | architect_standard | DOMAIN_COMPONENT_SCHEMA_FILE |
| 11 | validate_component_schema | action | -- | VALIDATE_COMPONENT_SCHEMA_FILE |
| 12 | gatekeep_component_schema | prompt | gatekeeper_standard | GATEKEEP_COMPONENT_SCHEMA_FILE |
| 13 | generate_composition_format | prompt | architect_standard | COMPOSITION_FORMAT_FILE |
| 14 | review_composition_format | prompt | reviewer_standard | REVIEW_COMPOSITION_FORMAT_FILE |
| 15 | refine_composition_format | prompt | architect_standard | COMPOSITION_FORMAT_FILE |
| 16 | validate_composition_format | action | -- | VALIDATE_COMPOSITION_FORMAT_FILE |
| 17 | gatekeep_composition_format | prompt | gatekeeper_standard | GATEKEEP_COMPOSITION_FORMAT_FILE |
| 18 | generate_output_format | prompt | architect_standard | OUTPUT_FORMAT_FILE |
| 19 | review_output_format | prompt | reviewer_standard | REVIEW_OUTPUT_FORMAT_FILE |
| 20 | refine_output_format | prompt | architect_standard | OUTPUT_FORMAT_FILE |
| 21 | validate_output_format | action | -- | VALIDATE_OUTPUT_FORMAT_FILE |
| 22 | gatekeep_output_format | prompt | gatekeeper_standard | GATEKEEP_OUTPUT_FORMAT_FILE |
| 23 | generate_artifact_contract | prompt | architect_standard | ARTIFACT_CONTRACT_FILE |
| 24 | review_artifact_contract | prompt | reviewer_standard | REVIEW_ARTIFACT_CONTRACT_FILE |
| 25 | refine_artifact_contract | prompt | architect_standard | ARTIFACT_CONTRACT_FILE |
| 26 | validate_artifact_contract | action | -- | VALIDATE_ARTIFACT_CONTRACT_FILE |
| 27 | gatekeep_artifact_contract | prompt | gatekeeper_standard | GATEKEEP_ARTIFACT_CONTRACT_FILE |
| 28 | generate_step_sequence | prompt | architect_standard | STEP_SEQUENCE_FILE |
| 29 | review_step_sequence | prompt | reviewer_standard | REVIEW_STEP_SEQUENCE_FILE |
| 30 | refine_step_sequence | prompt | architect_standard | STEP_SEQUENCE_FILE |
| 31 | validate_step_sequence | action | -- | VALIDATE_STEP_SEQUENCE_FILE |
| 32 | gatekeep_step_sequence | prompt | gatekeeper_standard | GATEKEEP_STEP_SEQUENCE_FILE |
| 33 | generate_runtime_standard | prompt | architect_standard | RUNTIME_STANDARD_FILE |
| 34 | review_runtime_standard | prompt | reviewer_standard | REVIEW_RUNTIME_STANDARD_FILE |
| 35 | refine_runtime_standard | prompt | architect_standard | RUNTIME_STANDARD_FILE |
| 36 | validate_runtime_standard | action | -- | VALIDATE_RUNTIME_STANDARD_FILE |
| 37 | gatekeep_runtime_standard | prompt | gatekeeper_standard | GATEKEEP_RUNTIME_STANDARD_FILE |
| 38 | generate_operational_workflow | prompt | architect_standard | OPERATIONAL_WORKFLOW_FILE |
| 39 | review_operational_workflow | prompt | reviewer_standard | REVIEW_OPERATIONAL_WORKFLOW_FILE |
| 40 | refine_operational_workflow | prompt | architect_standard | OPERATIONAL_WORKFLOW_FILE |
| 41 | validate_operational_workflow | action | -- | VALIDATE_OPERATIONAL_WORKFLOW_FILE |
| 42 | gatekeep_operational_workflow | prompt | gatekeeper_standard | GATEKEEP_OPERATIONAL_WORKFLOW_FILE |
| 43 | generate_package | prompt | architect_standard | 7 package files |
| 44 | validate_package | action | -- | VALIDATION_REPORT_FILE |
| 45 | review_package | prompt | reviewer_standard | REVIEW_FILE_SUGGESTED |
| 46 | refine_package | prompt | architect_standard | 7 package files |
| 47 | promote_workflow_package | action | -- | WORKFLOW_PACKAGE_DIR_FILE |
| 48 | step_completion | action | -- | COMPLETION_RESULT |

## Artifact Keys

| Artifact Key | Description |
|--------------|-------------|
| WORKFLOW_SPEC_FILE | Runtime specification input |
| VALIDATION_INPUT_SPEC_FILE | Validated input spec |
| TEST_CRITERIA_FILE | Acceptance criteria for all phases |
| REVIEW_TEST_CRITERIA_FILE | Critic review of test criteria |
| DOMAIN_ANALYSIS_FILE | Domain analysis and context |
| GATEKEEP_DOMAIN_ANALYSIS_FILE | Gatekeep verdict for domain analysis |
| DOMAIN_COMPONENT_SCHEMA_FILE | Layer 1: domain component schema |
| REVIEW_COMPONENT_SCHEMA_FILE | Review of component schema |
| GATEKEEP_COMPONENT_SCHEMA_FILE | Gatekeep verdict for component schema |
| COMPOSITION_FORMAT_FILE | Layer 2: composition format |
| REVIEW_COMPOSITION_FORMAT_FILE | Review of composition format |
| GATEKEEP_COMPOSITION_FORMAT_FILE | Gatekeep verdict for composition format |
| OUTPUT_FORMAT_FILE | Layer 3: output format |
| REVIEW_OUTPUT_FORMAT_FILE | Review of output format |
| GATEKEEP_OUTPUT_FORMAT_FILE | Gatekeep verdict for output format |
| ARTIFACT_CONTRACT_FILE | Artifact input/output contract |
| REVIEW_ARTIFACT_CONTRACT_FILE | Review of artifact contract |
| GATEKEEP_ARTIFACT_CONTRACT_FILE | Gatekeep verdict for artifact contract |
| STEP_SEQUENCE_FILE | Step sequence with routing |
| REVIEW_STEP_SEQUENCE_FILE | Review of step sequence |
| GATEKEEP_STEP_SEQUENCE_FILE | Gatekeep verdict for step sequence |
| RUNTIME_STANDARD_FILE | Consolidated composition standard |
| REVIEW_RUNTIME_STANDARD_FILE | Review of runtime standard |
| GATEKEEP_RUNTIME_STANDARD_FILE | Gatekeep verdict for runtime standard |
| OPERATIONAL_WORKFLOW_FILE | Operational workflow design |
| REVIEW_OPERATIONAL_WORKFLOW_FILE | Review of operational workflow |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | Gatekeep verdict for operational workflow |
| WORKFLOW_MANIFEST_FILE | workflow.toml output |
| WORKFLOW_EXTENSIONS_FILE | context_extensions.py output |
| WORKFLOW_ACTIONS_FILE | actions.py output |
| WORKFLOW_PROMPTS_INDEX_FILE | prompts_index.json output |
| WORKFLOW_README_FILE | README.md output |
| STANDARDS_COMPOSITION_STANDARD_FILE | Standards/COMPOSITION_STANDARD.md |
| SPECS_BUILDER_SPEC_FILE | Specs/ directory placeholder |
| VALIDATION_REPORT_FILE | Deterministic validation report |
| REVIEW_FILE_SUGGESTED | Quality review of package |
| WORKFLOW_PACKAGE_DIR_FILE | Promoted package directory |

## Architecture

### 3-Layer Design

The workflow follows a 3-layer composition system architecture:

- **Layer 1 (Component Schema):** Domain-specific component types
  derived from the target spec via fine-tuning of the Base Component
  Schema. Defines types, properties, and validation rules.

- **Layer 2 (Composition Format):** Binding rules that define how
  components connect. Includes override mechanisms, placeholder
  resolution, and workflow patterns.

- **Layer 3 (Output Format):** The resolved output structure with
  directory layout, resolution rules, and quality requirements.

### TDD Unit Pattern

Each phase (1-8) follows the standardized TDD unit pattern:

1. **Generate** (architect_standard) -- Produce the design artifact
2. **Review** (reviewer_standard) -- Critic review with APPROVED/REJECTED
3. **Refine** (architect_standard) -- Fix review findings
4. **Validate** (action) -- Deterministic structural checks
5. **Gatekeep** (gatekeeper_standard) -- Test criteria verification

Review and gatekeep steps have on_reject_refine loops with
max_iterations=2 and exhaustion failure codes.

### Identity Locking

Every prompt enforces identity locking to prevent builder leakage:

- The builder's own name must NOT appear in generated output
- The builder's standard name must NOT appear in generated output
- The builder's phase structure must NOT be copied into output
- Component types are derived from the target spec, not hardcoded

### Recursive Chain

AMB v2 is part of a recursive composition chain:

```
Workflow Builder v4 --> AMB v2 --> [target workflow]
```

Workflow Builder v4 generates AMB v2. AMB v2 generates the target
workflow. Each level uses the same TDD unit pattern with identity
locking to ensure clean separation.

## File Structure

```
ar_meta_builder_v2/
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
    04_generate_domain_analysis.txt
    05_gatekeep_domain_analysis.txt
    06_generate_component_schema.txt
    07_review_component_schema.txt
    08_refine_component_schema.txt
    09_gatekeep_component_schema.txt
    10_generate_composition_format.txt
    11_review_composition_format.txt
    12_refine_composition_format.txt
    13_gatekeep_composition_format.txt
    14_generate_output_format.txt
    15_review_output_format.txt
    16_refine_output_format.txt
    17_gatekeep_output_format.txt
    18_generate_artifact_contract.txt
    19_review_artifact_contract.txt
    20_refine_artifact_contract.txt
    21_gatekeep_artifact_contract.txt
    22_generate_step_sequence.txt
    23_review_step_sequence.txt
    24_refine_step_sequence.txt
    25_gatekeep_step_sequence.txt
    26_generate_runtime_standard.txt
    27_review_runtime_standard.txt
    28_refine_runtime_standard.txt
    29_gatekeep_runtime_standard.txt
    30_generate_operational_workflow.txt
    31_review_operational_workflow.txt
    32_refine_operational_workflow.txt
    33_gatekeep_operational_workflow.txt
    34_generate_package.txt
    35_review_package.txt
    36_refine_package.txt
  prompts_index.json
  README.md
```
