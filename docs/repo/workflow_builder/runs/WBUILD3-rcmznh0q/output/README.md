# Workflow Builder v3

Self-bootstrapping meta-meta builder that generates meta builders
with complete 3-part output. Each generated meta builder includes
its own composition standard, its own spec in Specs/, and a fully
executable workflow package.

**Workflow pattern:** meta_meta_builder
**Total steps:** 21 (18 prompt, 3 action)
**Total phases:** 9
**Job prefix:** WBUILD3

---

## Overview

Workflow Builder v3 is a meta-meta composition system. It generates
meta builders -- agents that are themselves capable of generating
executable workflow packages from specification inputs.

The key innovation of v3 is the 3-part output structure:

1. **Standards/COMPOSITION_STANDARD.md** -- The composition standard
   for the generated meta builder. Defines component types, schemas,
   and extensibility model.

2. **Specs/{builder_name}.md** -- The builder's own specification,
   embedded for self-bootstrapping. Enables the generated builder
   to process its own spec to produce the next version.

3. **Workflow package** -- The executable workflow definition:
   workflow.toml, context_extensions.py, actions.py, prompts/,
   README.md.

**Multi-level architecture:**

```
Level 0: v3 builder (creates meta builders, self-bootstrapping)
Level 1: Agent Workflow Spec (composition standard per agent)
Level 2: User Workflows (composition specs per use case)
Level 3: Agent execution outputs (deliverables)
```

---

## Prerequisites

- Python 3.12+ with the agent-runner-v2 package installed.
- Access to the agent-runner-backend-v2 API (port 8200) for
  daemon mode.
- A composition system specification file as input
  (WORKFLOW_SPEC_FILE).
- Virtual environment activated:
  ```
  .venv\Scripts\activate
  ```

---

## Usage

### CLI Mode

```bash
ukbe-run-agent run --template-group workflow_builder_v3
```

### Daemon Mode

```bash
ukbe-run-agent daemon
```

The daemon will claim jobs from the backend and execute them
using the workflow_builder_v3 workflow definition.

### Input

Provide a composition system specification as the
WORKFLOW_SPEC_FILE input artifact. The spec must follow the
composition system format defined in the base standard.

### Output

After successful execution, the output is promoted to:

```
workflows/{builder_name}/
```

The promoted directory contains the complete 3-part output
structure.

---

## Step Reference

| Step | Name | Type | Purpose | Onsuccess |
|------|------|------|---------|-----------|
| 01 | generate_test_criteria | prompt | Generate acceptance criteria | review_test_criteria |
| 02 | review_test_criteria | prompt | Review test criteria | generate_component_schema |
| 03 | refine_test_criteria | prompt | Refine test criteria (conditional) | review_test_criteria |
| 04 | generate_component_schema | prompt | Generate component schema Layer 1 | gatekeep_component_schema |
| 05 | gatekeep_component_schema | prompt | Validate component schema | generate_composition_format |
| 06 | generate_composition_format | prompt | Generate composition format Layer 2 | gatekeep_composition_format |
| 07 | gatekeep_composition_format | prompt | Validate composition format | generate_output_format |
| 08 | generate_output_format | prompt | Generate output format Layer 3 | gatekeep_output_format |
| 09 | gatekeep_output_format | prompt | Validate output format | generate_operational_workflow |
| 10 | generate_operational_workflow | prompt | Generate operational workflow | gatekeep_operational_workflow |
| 11 | gatekeep_operational_workflow | prompt | Validate operational workflow | generate_composition_standard |
| 12 | generate_composition_standard | prompt | Generate composition standard | gatekeep_composition_standard |
| 13 | gatekeep_composition_standard | prompt | Validate composition standard | generate_meta_composition_spec |
| 14 | generate_meta_composition_spec | prompt | Generate meta composition spec | generate_package |
| 15 | generate_package | prompt | Generate complete workflow package | validate_package_deterministic |
| 16 | validate_package_deterministic | action | Run 11 validation checks | gatekeep_package |
| 17 | gatekeep_package | prompt | Gatekeep the package | review_package |
| 18 | review_package | prompt | Final review of package | promote_workflow_package |
| 19 | refine_package | prompt | Refine package (conditional) | review_package |
| 20 | promote_workflow_package | action | Promote 3-part output | step_completion |
| 21 | step_completion | action | Mark workflow complete | -- |

**Review/Refine loops:**

- **LOOP-001** (Phase 1): review_test_criteria -> refine_test_criteria
  (max 2 iterations, TEST_CRITERIA_FILE)
- **LOOP-002** (Phase 8): review_package -> refine_package
  (max 2 iterations, REVIEW_FILE_SUGGESTED)

**Gatekeep loops** (Phases 2-6): Each gatekeep step can route back
to its corresponding generate step on rejection (max 2 iterations).

---

## Artifact Keys

### Input Artifacts

| Artifact Key | Description | Source |
|--------------|-------------|--------|
| WORKFLOW_SPEC_FILE | Composition system specification | User input |

### Output Artifacts

| Artifact Key | Description | Filename Pattern | Produced By |
|--------------|-------------|------------------|-------------|
| TEST_CRITERIA_FILE | Acceptance criteria | TEST_CRITERIA-{seq}.md | 01 |
| REVIEW_TEST_CRITERIA_FILE | Review of test criteria | REVIEW_TEST_CRITERIA-{seq}.md | 02 |
| COMPONENT_SCHEMA_FILE | Component schema Layer 1 | COMPONENT_SCHEMA-{seq}.md | 04 |
| GATEKEEP_COMPONENT_SCHEMA_FILE | Gatekeep review | GATEKEEP_COMPONENT_SCHEMA-{seq}.md | 05 |
| COMPOSITION_FORMAT_FILE | Composition format Layer 2 | COMPOSITION_FORMAT-{seq}.md | 06 |
| GATEKEEP_COMPOSITION_FORMAT_FILE | Gatekeep review | GATEKEEP_COMPOSITION_FORMAT-{seq}.md | 07 |
| OUTPUT_FORMAT_FILE | Output format Layer 3 | OUTPUT_FORMAT-{seq}.md | 08 |
| GATEKEEP_OUTPUT_FORMAT_FILE | Gatekeep review | GATEKEEP_OUTPUT_FORMAT-{seq}.md | 09 |
| OPERATIONAL_WORKFLOW_FILE | Operational workflow design | OPERATIONAL_WORKFLOW-{seq}.md | 10 |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | Gatekeep review | GATEKEEP_OPERATIONAL_WORKFLOW-{seq}.md | 11 |
| COMPOSITION_STANDARD_FILE | Composition standard | COMPOSITION_STANDARD-{seq}.md | 12 |
| GATEKEEP_COMPOSITION_STANDARD_FILE | Gatekeep review | GATEKEEP_COMPOSITION_STANDARD-{seq}.md | 13 |
| META_COMPOSITION_SPEC_FILE | Meta composition spec | META_COMPOSITION_SPEC-{seq}.md | 14 |
| WORKFLOW_MANIFEST_FILE | Workflow manifest | workflow.toml | 15, 19 |
| WORKFLOW_EXTENSIONS_FILE | Context extensions | context_extensions.py | 15, 19 |
| WORKFLOW_ACTIONS_FILE | Custom actions | actions.py | 15, 19 |
| WORKFLOW_PROMPTS_INDEX_FILE | Prompts index | prompts_index.json | 15, 19 |
| WORKFLOW_README_FILE | Package documentation | README.md | 15, 19 |
| STANDARDS_COMPOSITION_STANDARD_FILE | Standards composition standard | Standards/COMPOSITION_STANDARD.md | 15, 19 |
| SPECS_BUILDER_SPEC_FILE | Embedded builder spec | Specs/{builder_name}.md | 15 |
| VALIDATION_REPORT_FILE | Validation report | VALIDATION_REPORT-{seq}.md | 16 |
| GATEKEEP_PACKAGE_FILE | Gatekeep review | GATEKEEP_PACKAGE-{seq}.md | 17 |
| REVIEW_FILE_SUGGESTED | Final review | REVIEW-{seq}.md | 18 |
| WORKFLOW_PACKAGE_DIR_FILE | Promoted package directory | workflows/{slug}/ | 20 |

---

## Architecture

### Three-Layer Composition Architecture

The workflow builder generates composition systems using a
three-layer architecture:

**Layer 1 -- Component Schema:** Defines 8 component types with
their schemas, validation rules, and examples. The building block
library.

**Layer 2 -- Composition Format:** Defines how components are
assembled into compositions with binding rules, workflow patterns,
override mechanisms, and placeholder resolution.

**Layer 3 -- Output Format:** Defines how compositions are resolved
into concrete output files with resolution rules, quality
requirements, and downstream extraction contracts.

### 8 Component Types

| Type | Purpose | Required |
|------|---------|----------|
| step_definition | Workflow step definition | Yes |
| role_policy | Coder role assignment | Yes |
| routing_pattern | Step routing and flow | Yes |
| prompt_pattern | Prompt structure elements | No |
| artifact_contract | Input/output artifacts | Yes |
| composition_standard | Self-describing standard | Yes |
| output_variance | Output configurations | No |
| domain_spec | Accepted spec types | No |

### Validation

Step 16 runs 11 deterministic validation checks:

| Check | Description |
|-------|-------------|
| 1 | TOML parse validity of workflow.toml |
| 2 | Python syntax of context_extensions.py and actions.py |
| 3 | TYPE_CHECKING runtime import detection |
| 4 | Artifact binding consistency |
| 5 | Action step implementation completeness |
| 6 | Prompt file existence |
| 7 | Prompt placeholder vs required_inputs consistency |
| 8 | context_extensions.py artifact key coverage |
| 9 | Standards/COMPOSITION_STANDARD.md existence |
| 10 | Specs/ directory with at least one .md file |
| 11 | Bidirectional prompt placeholder consistency |

---

## File Structure

```
workflow_builder_v3/
|-- Standards/
|   +-- COMPOSITION_STANDARD.md
|-- Specs/
|   +-- workflow_builder_v3.md
|-- workflow.toml
|-- context_extensions.py
|-- actions.py
|-- prompts_index.json
|-- prompts/
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
+-- README.md
```

### Standards/ Directory

Contains the composition standard that defines what component types
are available, how they are assembled, and how compositions are
resolved into output files. This is the v3 self-describing element.

### Specs/ Directory

Contains the builder's own specification for self-bootstrapping.
The embedded spec enables the generated builder to process its own
spec to produce the next version.

---

## Self-Bootstrapping

Workflow Builder v3 supports self-bootstrapping:

1. The builder embeds its own spec in Specs/ during package
   assembly.
2. Feed the embedded spec back as WORKFLOW_SPEC_FILE.
3. The builder produces the next version.
4. The chain continues indefinitely.

**Bootstrap invariant:** Every version N embeds its own spec in
Specs/. Version N+1 is generated from that embedded spec.

---

*Generated by Workflow Builder v3 (WBUILD3)*
