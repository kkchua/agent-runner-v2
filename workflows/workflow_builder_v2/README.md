# Workflow Builder v2 — Composition System Builder

## Overview

**Workflow name:** `workflow_builder_v2`
**Job prefix:** `WBUILD2`
**Description:** Builds composition system workflows using the Composition System Standard. Generates component schemas, composition formats, output formats, and operational workflows.

## Purpose

workflow_builder_v2 is a meta-workflow builder that creates composition system workflows — workflows that operate on the component → composition → output pattern defined in the Composition System Standard.

Unlike workflow_builder_v1 (which builds traditional workflow packages), v2 builds workflows that understand:
- **Component schemas** — The LEGO bricks (component types and their properties)
- **Composition formats** — How bricks snap together (assembly instructions)
- **Output formats** — What the assembled result looks like
- **Operational workflows** — How to scan, resolve, and generate outputs

## Prerequisites

- Python 3.12+
- agent-runner-v2 installed (`pip install -e .`)
- Composition System Standard (`docs/repo/workflow_builder/standards/COMPOSITION_SYSTEM_STANDARD.md`)
- Meta-Workflow Builder Architecture (`docs/repo/workflow_builder/standards/META_WORKFLOW_BUILDER_ARCHITECTURE.md`)

## Usage

```bash
# Run via CLI
ukbe-run-agent run --template-group workflow_builder_v2 --workflow-spec path/to/spec.md

# Or submit via operator console
# Select workflow_builder_v2, provide WORKFLOW_SPEC input
```

## Step Reference

| # | Step Name | Type | Purpose |
|---|---|---|---|
| 1 | `generate_test_criteria` | prompt | Define acceptance criteria for the composition system |
| 2 | `review_test_criteria` | prompt | Review criteria quality |
| 3 | `refine_test_criteria` | prompt | Fix issues (conditional) |
| 4 | `generate_component_schema` | prompt | Define component types and their schemas |
| 5 | `gatekeep_component_schema` | prompt | Validate schema completeness |
| 6 | `generate_composition_format` | prompt | Define how components compose |
| 7 | `gatekeep_composition_format` | prompt | Validate composition format |
| 8 | `generate_output_format` | prompt | Define resolved output structure |
| 9 | `gatekeep_output_format` | prompt | Validate output format |
| 10 | `generate_operational_workflow` | prompt | Design scan → resolve → generate workflow |
| 11 | `gatekeep_operational_workflow` | prompt | Validate workflow design |
| 12 | `generate_package` | prompt | Assemble complete composition system package |
| 13 | `gatekeep_package` | prompt | Validate package completeness |
| 14 | `review_package` | prompt | Comprehensive quality review |
| 15 | `refine_package` | prompt | Fix issues (conditional) |
| 16 | `promote` | action | Deploy to workflows/ directory |
| 17 | `stepCompletion` | action | Terminal step |

## Artifact Keys

| Key | Description |
|---|---|
| `TEST_CRITERIA_FILE` | Acceptance criteria for the composition system |
| `COMPONENT_SCHEMA_FILE` | Component type definitions and schemas |
| `COMPOSITION_FORMAT_FILE` | Composition format specification |
| `OUTPUT_FORMAT_FILE` | Output format specification |
| `OPERATIONAL_WORKFLOW_FILE` | Operational workflow design |
| `WORKFLOW_MANIFEST_FILE` | workflow.toml for the composition system |
| `WORKFLOW_EXTENSIONS_FILE` | context_extensions.py |
| `WORKFLOW_ACTIONS_FILE` | actions.py (scan, resolve, assemble) |
| `WORKFLOW_PROMPTS_INDEX_FILE` | List of prompt files |
| `WORKFLOW_README_FILE` | README.md |
| `REVIEW_FILE_SUGGESTED` | Review document |

## Architecture

workflow_builder_v2 follows the Meta-Workflow Builder Architecture standard:

1. **Universal execution flow** — Same meta-workflow skeleton as v1
2. **5 gatekeepers** — Validate each layer (component schema, composition format, output format, operational workflow, package)
3. **Review/refine loops** — Quality assurance at multiple levels
4. **Self-criticism** — All prompts include self-critic sections

## Bootstrap Strategy

v2 uses a bootstrap strategy:
1. First, v2 builds a "traditional workflow composition system" (output ≈ v1's output)
2. Validate v2's output matches v1's output
3. Refine the standard based on learnings
4. Apply v2 to real composition systems (video_campaign_manuscript, etc.)

## References

- **Composition System Standard:** `docs/repo/workflow_builder/standards/COMPOSITION_SYSTEM_STANDARD.md`
- **Meta-Workflow Builder Architecture:** `docs/repo/workflow_builder/standards/META_WORKFLOW_BUILDER_ARCHITECTURE.md`
- **Phase 1 Analysis:** `docs/repo/workflow_builder/PHASE1_V1_AS_COMPOSITION_SYSTEM.md`
- **Phase 2 Design:** `docs/repo/workflow_builder/PHASE2_V2_DESIGN.md`
