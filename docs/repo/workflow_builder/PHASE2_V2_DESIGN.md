# Phase 2: Designing workflow_builder_v2

> **Status:** DRAFT
> **Created:** 2026-08-07
> **Purpose:** Design v2's workflow to generate composition system workflows

---

## 1. What v2 Builds

v2 builds **composition system workflows** — workflows that operate on the component → composition → output pattern.

**v2's Output:** A complete composition system workflow package:
```
workflows/{workflow_name}/
├── workflow.toml              ← Meta-workflow for the composition system
├── context_extensions.py      ← Artifact key registration
├── actions.py                 ← Component scanning, composition resolution, output assembly
├── prompts/                   ← Prompt templates
├── component_schema/          ← Component type definitions (NEW)
│   ├── common_schema.yaml     ← Common properties
│   └── type_schemas/          ← Type-specific schemas
├── composition_format/        ← Composition format specification (NEW)
│   └── composition_schema.yaml
├── output_format/             ← Output format specification (NEW)
│   └── output_schema.yaml
└── README.md                  ← User guide
```

## 2. v2's Meta-Workflow Structure

Following the Meta-Workflow Builder Architecture standard:

```
Phase 1: Foundation (TDD Loop)
├── generate_test_criteria         — Define acceptance criteria for composition workflows
├── review_test_criteria           — Review criteria quality
└── refine_test_criteria           — Fix issues (conditional)

Phase 2: Component Schema Design
├── generate_component_schema      — Define component types and their schemas
├── gatekeep_component_schema      — Validate schema completeness
└── [review/refine if needed]

Phase 3: Composition Format Design
├── generate_composition_format    — Define how components compose
├── gatekeep_composition_format    — Validate composition format
└── [review/refine if needed]

Phase 4: Output Format Design
├── generate_output_format         — Define resolved output structure
├── gatekeep_output_format         — Validate output format
└── [review/refine if needed]

Phase 5: Operational Workflow Design
├── generate_operational_workflow  — Design scan → resolve → generate workflow
├── gatekeep_operational_workflow  — Validate workflow design
└── [review/refine if needed]

Phase 6: Package Assembly
├── generate_package               — Assemble complete composition system package
├── gatekeep_package               — Validate package completeness
├── review_package                 — Comprehensive quality review
└── refine_package                 — Fix issues (conditional, loops)

Phase 7: Promotion
├── promote                        — Deploy to workflows/ directory
└── stepCompletion                 — Terminal step
```

## 3. v2's Step Implementations

### 3.1 Generation Steps

**generate_test_criteria**
- Input: Workflow spec (composition system requirements)
- Output: Test criteria document
- Purpose: Define what makes a good composition system

**generate_component_schema**
- Input: Workflow spec + test criteria
- Output: Component schema (common properties + type-specific schemas)
- Purpose: Define the LEGO bricks for the domain

**generate_composition_format**
- Input: Component schema + workflow spec
- Output: Composition format specification
- Purpose: Define how bricks snap together

**generate_output_format**
- Input: Component schema + composition format
- Output: Output format specification
- Purpose: Define what the assembled result looks like

**generate_operational_workflow**
- Input: Component schema + composition format + output format
- Output: Operational workflow design (scan → resolve → generate)
- Purpose: Design the workflow that operates on this composition system

**generate_package**
- Input: All above artifacts
- Output: Complete composition system workflow package
- Purpose: Assemble everything into a deployable workflow

### 3.2 Gatekeeper Steps

**gatekeep_component_schema**
- Validates: All component types defined, schemas complete, validation rules present
- Checks: Common properties present, type-specific properties defined, extensibility model

**gatekeep_composition_format**
- Validates: Composition structure defined, reference rules clear, override mechanism specified
- Checks: Placeholder resolution defined, ordering constraints specified

**gatekeep_output_format**
- Validates: Output structure defined, resolution rules complete, downstream contracts specified
- Checks: Self-contained output, no dangling references, platform considerations

**gatekeep_operational_workflow**
- Validates: Scan/resolve/generate steps designed, artifact contract defined
- Checks: Step sequence logical, routing correct, error handling present

**gatekeep_package**
- Validates: All files present, aligned, complete
- Checks: workflow.toml matches design, prompts complete, actions implemented

### 3.3 Review/Refine Steps

**review_package**
- Comprehensive review of the entire composition system
- Checks: Component schema quality, composition format clarity, output format completeness, operational workflow correctness

**refine_package**
- Fixes issues found in review
- Updates files in-place
- Loops back to review

## 4. v2's Artifact Contract

**Input Artifacts:**
| Key | Description |
|---|---|
| `WORKFLOW_SPEC` | The composition system specification |

**Output Artifacts:**
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
| `GATEKEEP_COMPONENT_SCHEMA_FILE` | Gatekeeper report |
| `GATEKEEP_COMPOSITION_FORMAT_FILE` | Gatekeeper report |
| `GATEKEEP_OUTPUT_FORMAT_FILE` | Gatekeeper report |
| `GATEKEEP_OPERATIONAL_WORKFLOW_FILE` | Gatekeeper report |
| `GATEKEEP_PACKAGE_FILE` | Gatekeeper report |

## 5. Bootstrap Application: Traditional Workflow Composition System

For the bootstrap, v2 builds a "traditional workflow composition system" where:

**Component Types:**
- `workflow_manifest` — workflow.toml
- `context_extension` — context_extensions.py
- `action_module` — actions.py
- `prompt_template` — prompts/*.txt
- `documentation` — README.md
- `env_template` — .env.sample (optional)
- `config_template` — config.json.sample (optional)

**Composition Format:**
- YAML-based workflow specification
- References component types
- Defines step sequence, routing, artifacts

**Output Format:**
- Complete workflow package directory
- All components resolved and assembled

**Operational Workflow:**
- Scan: Parse workflow spec
- Resolve: Map spec to component types
- Generate: Produce each component following its schema
- Review: Validate completeness and quality

## 6. Next Steps

1. Create workflow_builder_v2 directory structure
2. Write workflow.toml with the meta-workflow skeleton
3. Write context_extensions.py with artifact key registration
4. Write prompts for each step
5. Write actions for component scanning, composition resolution, output assembly
6. Test with traditional workflow spec (e.g., agnes_media_gen_v1)
7. Validate output matches v1's output
8. Refine based on learnings

---

**End of Design**
