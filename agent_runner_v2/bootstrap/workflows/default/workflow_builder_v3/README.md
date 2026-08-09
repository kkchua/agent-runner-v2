# Workflow Builder v3

Meta-meta builder that generates composition system workflows (meta builders).
Each generated meta builder is itself a composition system with its own
composition standard, enabling extensibility and self-bootstrapping.

## Overview

Workflow Builder v3 is a 21-step workflow that reads a single composition
system specification and produces three deliverables:

1. **Standards/COMPOSITION_STANDARD.md** -- The composition standard for
   the generated meta builder, defining its component types, composition
   format, and output format across the 3-layer architecture.

2. **Specs/ directory** -- A directory structure accepting user-provided
   specifications at runtime.

3. **Executable workflow package** -- workflow.toml, context_extensions.py,
   actions.py, prompts/, README.md implementing the generated meta builder.

**Workflow pattern:** meta_meta_builder
**Step count:** 21 (18 prompt, 3 action)
**Review loops:** 8

## Prerequisites

- Python 3.12+ with agent-runner-v2 installed
- The agent-runner-v2 virtual environment activated
- A valid composition system specification file (WORKFLOW_SPEC_FILE)
- Global runner home initialized (`ukbe-run-agent init`)

## Usage

### CLI Mode

```bash
ukbe-run-agent run --template-group workflow_builder_v3
```

### Daemon Mode

```bash
ukbe-run-agent daemon
# The daemon polls the backend and claims workflow_builder_v3 jobs
```

### Providing Input

Place the composition system specification in:
```
docs/repo/workflow_builder/specs/{spec_name}.md
```

The spec must follow the format defined in COMPOSITION_SYSTEM_STANDARD.md.

## Step Reference

| # | Step Name | Type | Phase | Purpose |
|---|---|---|---|---|
| 1 | generate_test_criteria | prompt | Foundation | Generate acceptance criteria |
| 2 | review_test_criteria | prompt | Foundation | Review criteria completeness |
| 3 | refine_test_criteria | prompt | Foundation | Fix review issues |
| 4 | generate_component_schema | prompt | Component Schema | Generate Layer 1 component types |
| 5 | gatekeep_component_schema | prompt | Component Schema | Validate component schema |
| 6 | generate_composition_format | prompt | Composition Format | Generate Layer 2 bindings |
| 7 | gatekeep_composition_format | prompt | Composition Format | Validate composition format |
| 8 | generate_output_format | prompt | Output Format | Generate Layer 3 resolution |
| 9 | gatekeep_output_format | prompt | Output Format | Validate output format |
| 10 | generate_operational_workflow | prompt | Operational | Generate workflow design |
| 11 | gatekeep_operational_workflow | prompt | Operational | Validate workflow design |
| 12 | generate_composition_standard | prompt | Composition Std | Generate v3 composition standard |
| 13 | gatekeep_composition_standard | prompt | Composition Std | Validate composition standard |
| 14 | generate_meta_composition_spec | prompt | Meta Spec | Generate self-bootstrap spec |
| 15 | generate_package | prompt | Package | Assemble workflow package |
| 16 | validate_package_deterministic | action | Package | Static analysis of package |
| 17 | gatekeep_package | prompt | Package | Gatekeep review of package |
| 18 | review_package | prompt | Package | Comprehensive quality review |
| 19 | refine_package | prompt | Package | Fix review issues |
| 20 | promote_workflow_package | action | Promotion | Deploy to workflows/ |
| 21 | step_completion | action | Promotion | Mark workflow complete |

## Artifact Keys

| Artifact Key | Description | Produced By |
|---|---|---|
| WORKFLOW_SPEC_FILE | Input: composition system specification | (external input) |
| TEST_CRITERIA_FILE | Acceptance criteria for the meta builder | generate_test_criteria |
| REVIEW_TEST_CRITERIA_FILE | Review verdict for acceptance criteria | review_test_criteria |
| COMPONENT_SCHEMA_FILE | Component schema (Layer 1) | generate_component_schema |
| GATEKEEP_COMPONENT_SCHEMA_FILE | Gatekeep verdict for component schema | gatekeep_component_schema |
| COMPOSITION_FORMAT_FILE | Composition format (Layer 2) | generate_composition_format |
| GATEKEEP_COMPOSITION_FORMAT_FILE | Gatekeep verdict for composition format | gatekeep_composition_format |
| OUTPUT_FORMAT_FILE | Output format (Layer 3) | generate_output_format |
| GATEKEEP_OUTPUT_FORMAT_FILE | Gatekeep verdict for output format | gatekeep_output_format |
| OPERATIONAL_WORKFLOW_FILE | Operational workflow design | generate_operational_workflow |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | Gatekeep verdict for operational workflow | gatekeep_operational_workflow |
| COMPOSITION_STANDARD_FILE | Composition standard for meta builder | generate_composition_standard |
| GATEKEEP_COMPOSITION_STANDARD_FILE | Gatekeep verdict for composition standard | gatekeep_composition_standard |
| META_COMPOSITION_SPEC_FILE | Meta composition spec for self-bootstrap | generate_meta_composition_spec |
| WORKFLOW_MANIFEST_FILE | Generated workflow.toml | generate_package |
| WORKFLOW_EXTENSIONS_FILE | Generated context_extensions.py | generate_package |
| WORKFLOW_ACTIONS_FILE | Generated actions.py | generate_package |
| WORKFLOW_PROMPTS_INDEX_FILE | Generated prompts index | generate_package |
| WORKFLOW_README_FILE | Generated README.md | generate_package |
| STANDARDS_COMPOSITION_STANDARD_FILE | Composition standard in output package (v3) | generate_package |
| VALIDATION_REPORT_FILE | Deterministic validation report | validate_package_deterministic |
| GATEKEEP_PACKAGE_FILE | Gatekeep verdict for workflow package | gatekeep_package |
| REVIEW_FILE_SUGGESTED | Comprehensive review of package | review_package |
| WORKFLOW_PACKAGE_DIR_FILE | Target directory path after promotion | promote_workflow_package |

## Architecture

### Three-Layer Architecture

The workflow follows the composition system standard's 3-layer architecture:

- **Layer 1: Component Schema** -- Defines 8 component types for the
  workflow_builder domain. These are the building blocks of meta builders.

- **Layer 2: Composition Format** -- Defines how components are assembled
  into compositions (8 binding rules, 6 workflow patterns, override
  mechanism, placeholder resolution).

- **Layer 3: Output Format** -- Defines the resolved output structure
  (3-part output, 7 resolution rules, 8 quality requirements).

### v3 Innovation: Self-Describing Meta Builders

Every generated meta builder has its own composition standard (Phase 6)
and meta composition spec (Phase 7), enabling:

- **Self-description**: The meta builder's capabilities are encoded in
  its own composition standard.
- **Self-bootstrapping**: The meta builder can process its own spec.
- **Extensibility**: New component types can be added to the meta
  builder without modifying the workflow code.

### Review/Refine Loops

The workflow includes 8 review/refine loops:
- 1 TDD loop (test criteria)
- 5 gatekeep loops (one per phase with generate+gatekeep)
- 1 package gatekeep loop
- 1 comprehensive review/refine loop

Each loop has max_iterations=2 with exhausted_failure_code and
exhausted_failure_class for failure handling.

## File Structure

```
workflow_builder_v3/
+-- workflow.toml              # Workflow manifest (21 steps)
+-- context_extensions.py      # Artifact key registration
+-- actions.py                 # Action implementations
+-- prompts/                   # 18 prompt templates
|   +-- 01_generate_test_criteria.txt
|   +-- ...
|   +-- 18_refine_package.txt
+-- prompts_index.json         # Prompt file index
+-- Standards/                 # v3: self-describing composition standard
|   +-- COMPOSITION_STANDARD.md
+-- Specs/                     # v3: directory for user-provided specs
|   +-- .gitkeep
+-- README.md                  # This file
```

---

## Refinement Summary (Iter 1)

The following fixes were applied to address REV_PACKAGE-001 findings:

- Added STANDARDS_COMPOSITION_STANDARD_FILE to Artifact Keys table.
- Updated File Structure to include Standards/ and Specs/ directories.

## Refinement Summary (Iter 2)

All 3 review issues from REV_PACKAGE-001 verified as resolved:

- Issue 1 (MAJOR): Standards/COMPOSITION_STANDARD.md present (331 lines,
  YAML frontmatter with doc_type composition_standard, all 3 layers).
- Issue 2 (MAJOR): Specs/ directory present with .gitkeep file.
- Issue 3 (MINOR): Untracked OUTPUT_COMPOSITION_SPEC.md removed.

Verification results:
- 21 steps (18 prompt, 3 action), all routing valid.
- 24 artifact keys registered in context_extensions.py.
- No self-referential artifact bindings.
- All prompt files exist and match step names.
- Both @action decorators present and returning ActionResult.
- Deterministic validation: 0 errors, 0 warnings (PASS).
- No content changes required.
