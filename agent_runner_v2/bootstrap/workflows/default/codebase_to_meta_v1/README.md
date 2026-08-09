# AR Meta Builder v1

## Overview

AR Meta Builder v1 is a meta-meta builder that generates composition system workflows (meta builders). Each generated meta builder is itself a composition system with its own composition standard, enabling extensibility and self-bootstrapping.

**Domain:** ar_meta_builder
**Job Prefix:** AMB
**Workflow Pattern:** meta_meta_builder
**Total Steps:** 21 (18 prompt-type, 3 action-type)
**Phases:** 9

The workflow follows the meta_meta_builder pattern across 9 phases:
Foundation (TDD), Component Schema (Layer 1), Composition Format (Layer 2), Output Format (Layer 3), Operational Workflow, Composition Standard, Meta Composition Spec, Package Assembly, and Promotion.

### Three-Part Output

Every generated meta builder includes:
1. `Standards/COMPOSITION_STANDARD.md` -- The composition standard defining component types and validation rules.
2. `Specs/` -- Directory for user-provided specifications at runtime.
3. Workflow package -- workflow.toml, context_extensions.py, actions.py, prompts/, README.md.

## Prerequisites

- Python 3.12+
- agent-runner-v2 installed and configured
- Runner engine initialized: `ukbe-run-agent init`
- WORKFLOW_SPEC_FILE: A composition system specification describing the target meta builder (Markdown with YAML frontmatter)

## Usage

### CLI Mode

```bash
ukbe-run-agent run --template-group ar_meta_builder_v1
```

The runner will prompt for the WORKFLOW_SPEC_FILE path.

### Daemon Mode

Submit a job to the backend with:
- `template_group`: "ar_meta_builder_v1"
- `artifacts.WORKFLOW_SPEC_FILE`: absolute path to the input specification

### Required Input

| Artifact Key | Description | Format |
|---|---|---|
| WORKFLOW_SPEC_FILE | Composition system specification describing the target meta builder | Markdown with YAML frontmatter |

## Step Reference

| # | Step Name | Type | Phase | Purpose |
|---|---|---|---|---|
| 01 | generate_test_criteria | prompt | Foundation | Generate acceptance criteria |
| 02 | review_test_criteria | prompt | Foundation | Review criteria quality |
| 03 | refine_test_criteria | prompt | Foundation | Refine rejected criteria |
| 04 | generate_component_schema | prompt | Component Schema | Generate Layer 1 schema |
| 05 | gatekeep_component_schema | prompt | Component Schema | Validate schema |
| 06 | generate_composition_format | prompt | Composition Format | Generate Layer 2 format |
| 07 | gatekeep_composition_format | prompt | Composition Format | Validate format |
| 08 | generate_output_format | prompt | Output Format | Generate Layer 3 format |
| 09 | gatekeep_output_format | prompt | Output Format | Validate format |
| 10 | generate_operational_workflow | prompt | Operational Workflow | Generate workflow design |
| 11 | gatekeep_operational_workflow | prompt | Operational Workflow | Validate workflow |
| 12 | generate_composition_standard | prompt | Composition Standard | Generate standard |
| 13 | gatekeep_composition_standard | prompt | Composition Standard | Validate standard |
| 14 | generate_meta_composition_spec | prompt | Meta Composition Spec | Generate meta spec |
| 15 | generate_package | prompt | Package Assembly | Generate complete package |
| 16 | validate_package_deterministic | action | Package Assembly | Run 9 validation checks |
| 17 | gatekeep_package | prompt | Package Assembly | Quality gate review |
| 18 | review_package | prompt | Package Assembly | Final review |
| 19 | refine_package | prompt | Package Assembly | Refine rejected package |
| 20 | promote_workflow_package | action | Promotion | Deploy to workflows/ |
| 21 | step_completion | action | Promotion | Record final outcome |

## Artifact Keys

| Key | Description | Produced By |
|---|---|---|
| WORKFLOW_SPEC_FILE | Input specification | External (user) |
| TEST_CRITERIA_FILE | Acceptance criteria | Step 01 |
| REVIEW_TEST_CRITERIA_FILE | Criteria review | Step 02 |
| COMPONENT_SCHEMA_FILE | Layer 1 schema | Step 04 |
| GATEKEEP_COMPONENT_SCHEMA_FILE | Schema gate | Step 05 |
| COMPOSITION_FORMAT_FILE | Layer 2 format | Step 06 |
| GATEKEEP_COMPOSITION_FORMAT_FILE | Format gate | Step 07 |
| OUTPUT_FORMAT_FILE | Layer 3 format | Step 08 |
| GATEKEEP_OUTPUT_FORMAT_FILE | Format gate | Step 09 |
| OPERATIONAL_WORKFLOW_FILE | Workflow design | Step 10 |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | Workflow gate | Step 11 |
| COMPOSITION_STANDARD_FILE | Composition standard | Step 12 |
| GATEKEEP_COMPOSITION_STANDARD_FILE | Standard gate | Step 13 |
| META_COMPOSITION_SPEC_FILE | Meta composition spec | Step 14 |
| WORKFLOW_MANIFEST_FILE | workflow.toml | Step 15 |
| WORKFLOW_EXTENSIONS_FILE | context_extensions.py | Step 15 |
| WORKFLOW_ACTIONS_FILE | actions.py | Step 15 |
| WORKFLOW_PROMPTS_INDEX_FILE | Prompt index | Step 15 |
| WORKFLOW_README_FILE | README.md | Step 15 |
| STANDARDS_COMPOSITION_STANDARD_FILE | Standards/COMPOSITION_STANDARD.md | Step 15 |
| VALIDATION_REPORT_FILE | Validation report | Step 16 |
| GATEKEEP_PACKAGE_FILE | Package gate | Step 17 |
| REVIEW_FILE_SUGGESTED | Package review | Step 18 |
| WORKFLOW_PACKAGE_DIR_FILE | Promoted path | Step 20 |

## Architecture

### Three-Layer Composition System

```
Layer 1: Component Schema    -- 8 component types, 14 validation rules
Layer 2: Composition Format  -- 8 binding rules, 6 workflow patterns
Layer 3: Output Format       -- 3-part output, 7 resolution rules, 8 quality checks
```

### Review/Refine Loops

The workflow implements 8 review/refine loops with max 2 iterations each:
- LOOP-A: review_test_criteria -> refine_test_criteria
- LOOP-B: gatekeep_component_schema -> generate_component_schema
- LOOP-C: gatekeep_composition_format -> generate_composition_format
- LOOP-D: gatekeep_output_format -> generate_output_format
- LOOP-E: gatekeep_operational_workflow -> generate_operational_workflow
- LOOP-F: gatekeep_composition_standard -> generate_composition_standard
- LOOP-G: gatekeep_package -> generate_package
- LOOP-H: review_package -> refine_package

## File Structure

```
ar_meta_builder_v1/
|-- Standards/
|   +-- COMPOSITION_STANDARD.md     # Composition standard (v3 innovation)
|-- Specs/
|   +-- .gitkeep                     # Runtime spec directory
|-- workflow.toml                     # Workflow manifest (21 steps)
|-- context_extensions.py             # Artifact key registration
|-- actions.py                        # Action step implementations
|-- prompts_index.json                # Prompt file index
|-- README.md                         # This file
+-- prompts/
    |-- 01_generate_test_criteria.txt
    |-- 02_review_test_criteria.txt
    |-- 03_refine_test_criteria.txt
    |-- 04_generate_component_schema.txt
    |-- 05_gatekeep_component_schema.txt
    |-- 06_generate_composition_format.txt
    |-- 07_gatekeep_composition_format.txt
    |-- 08_generate_output_format.txt
    |-- 09_gatekeep_output_format.txt
    |-- 10_generate_operational_workflow.txt
    |-- 11_gatekeep_operational_workflow.txt
    |-- 12_generate_composition_standard.txt
    |-- 13_gatekeep_composition_standard.txt
    |-- 14_generate_meta_composition_spec.txt
    |-- 15_generate_package.txt
    |-- 16_gatekeep_package.txt
    |-- 17_review_package.txt
    +-- 18_refine_package.txt
```

## Version History

- 1.0.0: Initial release with 9-phase meta_meta_builder pattern, 3-part output, composition standard innovation, and meta composition spec innovation.
