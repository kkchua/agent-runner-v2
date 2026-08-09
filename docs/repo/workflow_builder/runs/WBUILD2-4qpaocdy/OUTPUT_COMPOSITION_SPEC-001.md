---
doc_type: "output_composition_spec"
lifecycle_status: "draft"
effective_version: "WBUILD2-4qpaocdy"
domain: "workflow_builder"
component_type_count: 7
artifact_count: 21
composition_pattern: "output_assembly"
---

# Output Composition Specification: Workflow Builder v3

## Overview

This document defines the output composition system for the Workflow Builder v3
meta-meta builder. It treats the workflow's 21 output artifacts as a composable
component library organized into 7 component types. Downstream users can add new
output types (compositions) by combining existing component types or defining new
ones, without modifying the workflow code.

### Output Artifact Inventory

The Workflow Builder v3 produces 21 output artifacts across 9 workflow phases.
These artifacts are grouped into 7 component types based on their structural
role and extensibility characteristics.

| Component Type | Artifacts Covered | Count |
|---|---|---|
| test_criterion | TEST_CRITERIA_FILE, REVIEW_TEST_CRITERIA_FILE | 2 |
| layer_design | COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE | 3 |
| operational_design | OPERATIONAL_WORKFLOW_FILE | 1 |
| composition_system | COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE | 2 |
| package_file | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE | 5 |
| gatekeep_verdict | GATEKEEP_COMPONENT_SCHEMA_FILE, GATEKEEP_COMPOSITION_FORMAT_FILE, GATEKEEP_OUTPUT_FORMAT_FILE, GATEKEEP_OPERATIONAL_WORKFLOW_FILE, GATEKEEP_COMPOSITION_STANDARD_FILE, GATEKEEP_PACKAGE_FILE | 6 |
| quality_report | VALIDATION_REPORT_FILE, REVIEW_FILE_SUGGESTED | 2 |

### Categorization Rationale

The 7 component types are derived from the workflow's phase structure and the
role each artifact plays in the pipeline:

1. **test_criterion** -- Foundation-phase outputs that establish acceptance
   criteria before design work begins. These are the TDD backbone present in
   all workflows built by this system.

2. **layer_design** -- Layer-specific design documents that define the
   three-layer architecture (Component Schema, Composition Format, Output Format).
   Each layer document is independently extensible.

3. **operational_design** -- The operational workflow design that defines
   all phases, step sequence, and routing. A singleton artifact per workflow.

4. **composition_system** -- v3-specific outputs that make the generated
   meta builder self-describing (composition standard + meta spec).

5. **package_file** -- The executable workflow package files. These are the
   materialized outputs that downstream runners consume.

6. **gatekeep_verdict** -- Quality gate verdicts from gatekeep steps. Each
   gatekeep produces an APPROVED/REJECTED verdict for a specific artifact.

7. **quality_report** -- Quality verification reports from deterministic
   validation and comprehensive review steps.

### Extensibility Story

New output types can be added without modifying the workflow by:

1. Defining a new component type in the component schema (Layer 1).
2. Creating a composition that binds the new component type to the output
   pipeline (Layer 2).
3. The resolved output includes the new component without changes to
   workflow.toml, prompts, or actions.

This follows the same extensibility model as the three-layer architecture
defined in COMPOSITION_SYSTEM_STANDARD.md, applied to the workflow's own
outputs rather than to domain-specific deliverables.

---

## Component Schema (Layer 1)

### Common Properties

All output components share these properties:

| Property | Type | Required | Description |
|---|---|---|---|
| component_id | string | Yes | Unique identifier (format: {type}-{name}-{seq}) |
| component_type | enum | Yes | One of the 7 types defined below |
| name | string | Yes | Human-readable display name |
| version | string | Yes | Semantic version (MAJOR.MINOR.PATCH) |
| description | string | Yes | What this output component represents |
| artifact_key | string | Yes | The artifact key for this output |
| produced_by | string | Yes | The step that produces this artifact |
| format | string | Yes | Output format: markdown, toml, python, plaintext |

### Component Types

#### Type 1: test_criterion

Foundation-phase acceptance criteria outputs.

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| phase | string | Yes | Workflow phase this criteria covers | "foundation" |
| criteria_scope | string | Yes | What the criteria validate | "All 9 phases, component types, composition rules" |
| review_verdict | string | No | APPROVED or REJECTED (for review artifacts) | "APPROVED" |

**Artifact instances:**

| Artifact Key | Description | Produced By |
|---|---|---|
| TEST_CRITERIA_FILE | Acceptance criteria for the meta-meta builder | generate_test_criteria |
| REVIEW_TEST_CRITERIA_FILE | Review verdict for acceptance criteria | review_test_criteria |

#### Type 2: layer_design

Layer-specific design documents for the three-layer architecture.

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| layer_number | integer | Yes | Architecture layer (1, 2, or 3) | 1 |
| layer_name | string | Yes | Layer name | "Component Schema" |
| design_scope | string | Yes | What the design defines | "All 8 component types, properties, validation rules" |
| section_count | integer | No | Number of sections in the document | 6 |

**Artifact instances:**

| Artifact Key | Layer | Description | Produced By |
|---|---|---|---|
| COMPONENT_SCHEMA_FILE | 1 | Component schema defining all 8 component types | generate_component_schema |
| COMPOSITION_FORMAT_FILE | 2 | Composition format defining binding rules and patterns | generate_composition_format |
| OUTPUT_FORMAT_FILE | 3 | Output format defining resolution rules and quality | generate_output_format |

#### Type 3: operational_design

Operational workflow design defining phases, steps, and routing.

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| workflow_pattern | string | Yes | Pattern type from spec | "meta_meta_builder" |
| phase_count | integer | Yes | Number of workflow phases | 9 |
| step_count | integer | Yes | Total number of steps | 21 |
| action_count | integer | Yes | Number of action steps | 3 |
| prompt_step_count | integer | Yes | Number of prompt steps | 18 |
| review_loop_count | integer | Yes | Number of review/refine loops | 8 |

**Artifact instances:**

| Artifact Key | Description | Produced By |
|---|---|---|
| OPERATIONAL_WORKFLOW_FILE | Operational workflow design | generate_operational_workflow |

#### Type 4: composition_system

v3-specific composition system outputs that enable self-description.

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| standard_name | string | Yes | Name of the composition standard | "WORKFLOW_BUILDER_STANDARD" |
| standard_version | string | Yes | Version of the standard | "1.0.0" |
| component_types_defined | array | Yes | List of component types in the standard | ["step_definition", "role_policy", ...] |
| schema_layer_count | integer | Yes | Number of schema layers | 3 |
| self_bootstrap_capable | boolean | Yes | Can process its own spec | true |

**Artifact instances:**

| Artifact Key | Description | Produced By |
|---|---|---|
| COMPOSITION_STANDARD_FILE | Composition standard for the generated meta builder | generate_composition_standard |
| META_COMPOSITION_SPEC_FILE | Meta composition spec for self-bootstrapping | generate_meta_composition_spec |

#### Type 5: package_file

Executable workflow package files materialized from prior design artifacts.

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| file_name | string | Yes | Filename of the package file | "workflow.toml" |
| file_format | string | Yes | File format | "toml" |
| file_category | enum | Yes | Category: core, conditional, prompt, supplementary | "core" |
| required_for_execution | boolean | Yes | Must be present for workflow to run | true |

**Artifact instances:**

| Artifact Key | File | Format | Category | Produced By |
|---|---|---|---|---|
| WORKFLOW_MANIFEST_FILE | workflow.toml | toml | core | generate_package |
| WORKFLOW_EXTENSIONS_FILE | context_extensions.py | python | core | generate_package |
| WORKFLOW_ACTIONS_FILE | actions.py | python | conditional | generate_package |
| WORKFLOW_PROMPTS_INDEX_FILE | PROMPTS_INDEX-{seq}.md | markdown | supplementary | generate_package |
| WORKFLOW_README_FILE | README.md | markdown | core | generate_package |

#### Type 6: gatekeep_verdict

Quality gate verdicts produced by gatekeep steps.

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| verdict | enum | Yes | APPROVED or REJECTED | "APPROVED" |
| artifact_under_review | string | Yes | The artifact key being reviewed | "COMPONENT_SCHEMA_FILE" |
| review_phase | string | Yes | The phase this gatekeep belongs to | "component_schema" |
| max_iterations | integer | Yes | Max refine loop iterations | 2 |
| exhausted_failure_code | string | Yes | Terminal failure code | "COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED" |

**Artifact instances:**

| Artifact Key | Artifact Reviewed | Phase | Produced By |
|---|---|---|---|
| GATEKEEP_COMPONENT_SCHEMA_FILE | COMPONENT_SCHEMA_FILE | component_schema | gatekeep_component_schema |
| GATEKEEP_COMPOSITION_FORMAT_FILE | COMPOSITION_FORMAT_FILE | composition_format | gatekeep_composition_format |
| GATEKEEP_OUTPUT_FORMAT_FILE | OUTPUT_FORMAT_FILE | output_format | gatekeep_output_format |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | OPERATIONAL_WORKFLOW_FILE | operational_workflow | gatekeep_operational_workflow |
| GATEKEEP_COMPOSITION_STANDARD_FILE | COMPOSITION_STANDARD_FILE | composition_standard | gatekeep_composition_standard |
| GATEKEEP_PACKAGE_FILE | All package files | package_assembly | gatekeep_package |

#### Type 7: quality_report

Quality verification reports from validation and review steps.

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| report_type | enum | Yes | deterministic or comprehensive | "deterministic" |
| check_count | integer | Yes | Number of checks performed | 8 |
| error_count | integer | Yes | Number of errors found | 0 |
| warning_count | integer | No | Number of warnings found | 0 |

**Artifact instances:**

| Artifact Key | Report Type | Checks | Produced By |
|---|---|---|---|
| VALIDATION_REPORT_FILE | deterministic | 8 static analysis checks | validate_package_deterministic |
| REVIEW_FILE_SUGGESTED | comprehensive | spec fulfillment, scope, quality | review_package |

### Validation Rules

| Rule ID | Rule | Applies To |
|---|---|---|
| VR-OC-001 | component_id must be unique within the composition | All types |
| VR-OC-002 | component_type must be one of the 7 defined types | All types |
| VR-OC-003 | artifact_key must be UPPER_SNAKE_CASE with _FILE suffix | All types |
| VR-OC-004 | produced_by must reference a valid step name | All types |
| VR-OC-005 | format must be one of: markdown, toml, python, plaintext | All types |
| VR-OC-006 | layer_number must be 1, 2, or 3 | layer_design |
| VR-OC-007 | file_category must be one of: core, conditional, prompt, supplementary | package_file |
| VR-OC-008 | verdict must be APPROVED or REJECTED | gatekeep_verdict |
| VR-OC-009 | report_type must be deterministic or comprehensive | quality_report |
| VR-OC-010 | All artifact instances must trace to a producing step | All types |

---

## Composition Format (Layer 2)

### Composition Structure

An output composition is a declarative definition specifying which component
types to include, how they are bound, and what overrides to apply.

| Field | Type | Required | Description |
|---|---|---|---|
| composition_id | string | Yes | Unique identifier for this composition |
| composition_name | string | Yes | Human-readable display name |
| target_output | string | Yes | What this composition produces |
| component_bindings | object | Yes | Map of binding name to component references |
| overrides | object | No | Per-composition customizations |
| ordering | object | No | Ordering constraints for ordered bindings |

### Binding Rules

| Binding Name | Component Type | Cardinality | Required | Description |
|---|---|---|---|---|
| test_criteria | test_criterion | Ordered list | Yes | Acceptance criteria sequence |
| layer_designs | layer_design | Ordered list | Yes | Layer documents in order (1, 2, 3) |
| operational | operational_design | Singleton | Yes | Operational workflow design |
| composition_outputs | composition_system | Unordered set | Yes | v3 composition system outputs |
| packages | package_file | Unordered set | Yes | Package file set |
| gatekeeps | gatekeep_verdict | Unordered set | Yes | Quality gate verdicts |
| quality_reports | quality_report | Unordered set | No | Quality verification reports |

### Override Mechanism

Overrides allow per-composition customization without modifying the component
type definitions. Override values are merged with base component properties;
override wins on conflict.

```yaml
overrides:
  test_criterion:
    phase: "custom_phase"
    criteria_scope: "Custom scope description"
  layer_design:
    - layer_number: 1
      design_scope: "Custom Layer 1 scope"
  package_file:
    - file_name: "custom_config.json"
      file_format: "json"
      file_category: "conditional"
      required_for_execution: false
```

### Placeholder Resolution

| Data Source | Fields Provided | Required |
|---|---|---|
| Input Spec | domain_name, job_prefix | Yes |
| Runtime | job_id, seq, workspace_root | Yes |
| Component Library | component_id lookups | Yes |

### Example Composition

This example defines a composition that produces the standard Workflow Builder
v3 output set with an additional custom package file.

```yaml
composition_id: "output-composition-standard-v3-001"
composition_name: "Standard V3 Output Composition"
target_output: "Complete meta-meta builder package with all 21 artifacts"

component_bindings:
  test_criteria:
    - component_id: "test-criterion-acceptance-001"
      overrides:
        phase: "foundation"
        criteria_scope: "All 9 phases, 8 component types, composition rules"
    - component_id: "test-criterion-review-001"
  layer_designs:
    - component_id: "layer-design-schema-001"
      overrides:
        layer_number: 1
        layer_name: "Component Schema"
    - component_id: "layer-design-format-001"
      overrides:
        layer_number: 2
        layer_name: "Composition Format"
    - component_id: "layer-design-output-001"
      overrides:
        layer_number: 3
        layer_name: "Output Format"
  operational:
    component_id: "operational-design-workflow-001"
    overrides:
      workflow_pattern: "meta_meta_builder"
      phase_count: 9
      step_count: 21
  composition_outputs:
    - component_id: "composition-system-standard-001"
      overrides:
        standard_name: "WORKFLOW_BUILDER_STANDARD"
        self_bootstrap_capable: true
    - component_id: "composition-system-metaspec-001"
  packages:
    - component_id: "package-file-manifest-001"
      overrides:
        file_name: "workflow.toml"
        file_category: "core"
    - component_id: "package-file-extensions-001"
    - component_id: "package-file-actions-001"
    - component_id: "package-file-readme-001"
  gatekeeps:
    - component_id: "gatekeep-verdict-schema-001"
    - component_id: "gatekeep-verdict-format-001"
    - component_id: "gatekeep-verdict-output-001"
    - component_id: "gatekeep-verdict-operational-001"
    - component_id: "gatekeep-verdict-standard-001"
    - component_id: "gatekeep-verdict-package-001"
  quality_reports:
    - component_id: "quality-report-validation-001"
      overrides:
        report_type: "deterministic"
        check_count: 8
    - component_id: "quality-report-review-001"
      overrides:
        report_type: "comprehensive"

ordering:
  test_criteria: "sequential by phase"
  layer_designs: "ascending by layer_number"
```

---

## Output Format (Layer 3)

### Resolved Output Structure

When a composition is resolved, it produces the following output directory:

```
{builder_name}/
+-- Standards/
|   +-- COMPOSITION_STANDARD.md          # composition_system component
+-- Specs/
|   +-- (user-provided specs go here)    # directory established by composition
+-- workflow.toml                         # package_file: WORKFLOW_MANIFEST_FILE
+-- context_extensions.py                 # package_file: WORKFLOW_EXTENSIONS_FILE
+-- actions.py                            # package_file: WORKFLOW_ACTIONS_FILE (conditional)
+-- prompts/
|   +-- 01_{step_name}.txt                # package_file: prompt files
|   +-- ...
|   +-- NN_{step_name}.txt
+-- README.md                             # package_file: WORKFLOW_README_FILE
+-- .env.sample                           # conditional package_file
+-- config.json.sample                    # conditional package_file
```

### Resolution Rules

#### RR-OC-001: test_criterion Resolution

**Source:** test_criteria bindings in the composition.
**Target:** TEST_CRITERIA_FILE and REVIEW_TEST_CRITERIA_FILE.

Each test_criterion component is expanded into its producing step's prompt
template. The criteria are generated by the generate_test_criteria step and
reviewed by review_test_criteria. The phase and criteria_scope overrides are
injected into the prompt.

#### RR-OC-002: layer_design Resolution

**Source:** layer_designs bindings in the composition.
**Target:** COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE.

Each layer_design component is expanded into its producing step's output.
The layer_number determines which layer document is produced. The design_scope
override customizes the document's focus. Each layer document feeds the next
layer's generation step as a required input.

#### RR-OC-003: operational_design Resolution

**Source:** operational binding in the composition.
**Target:** OPERATIONAL_WORKFLOW_FILE.

The operational_design component is expanded into the full operational workflow
document. The workflow_pattern, phase_count, step_count, and other properties
are written directly into the document's frontmatter and body.

#### RR-OC-004: composition_system Resolution

**Source:** composition_outputs bindings in the composition.
**Target:** COMPOSITION_STANDARD_FILE and META_COMPOSITION_SPEC_FILE.

Each composition_system component is expanded into its target file. The
standard_name and standard_version overrides are written into the
COMPOSITION_STANDARD.md frontmatter. The self_bootstrap_capable flag
determines whether the META_COMPOSITION_SPEC_FILE is self-contained.

#### RR-OC-005: package_file Resolution

**Source:** packages bindings in the composition.
**Target:** All workflow package files on disk.

Each package_file component is expanded into its target file. Core files are
always written. Conditional files are written only if their condition is met.
The file_format determines the syntax (TOML, Python, Markdown, plaintext).

#### RR-OC-006: gatekeep_verdict Resolution

**Source:** gatekeeps bindings in the composition.
**Target:** GATEKEEP_*_FILE artifacts.

Each gatekeep_verdict component is expanded into its producing step's output.
The verdict (APPROVED/REJECTED) is determined by the gatekeep step's LLM
evaluation. The artifact_under_review identifies which artifact is being
validated.

#### RR-OC-007: quality_report Resolution

**Source:** quality_reports bindings in the composition.
**Target:** VALIDATION_REPORT_FILE and REVIEW_FILE_SUGGESTED.

Each quality_report component is expanded into its producing step's output.
The report_type determines the check methodology. The check_count and
error_count are computed during execution.

### Quality Requirements

All resolved outputs must pass these quality checks:

| Rule ID | Requirement | Severity |
|---|---|---|
| QR-OC-001 | All component references resolved (no dangling component_ids) | CRITICAL |
| QR-OC-002 | All artifact keys trace to producing steps | CRITICAL |
| QR-OC-003 | All package files present on disk | CRITICAL |
| QR-OC-004 | All prompt files present for prompt-driven steps | CRITICAL |
| QR-OC-005 | No contradictions between output sections | CRITICAL |
| QR-OC-006 | Composition standard defines all 3 layers | CRITICAL |
| QR-OC-007 | Artifact flow integrity (no temporal violations) | CRITICAL |
| QR-OC-008 | Cross-file consistency (step names, artifact keys match) | CRITICAL |

### Example Output Skeleton

This example shows a resolved output for the standard Workflow Builder v3
composition with 21 artifacts:

```
workflow_builder_v3/
+-- Standards/
|   +-- COMPOSITION_STANDARD.md
|       ---
|       doc_type: "composition_standard"
|       lifecycle_status: "active"
|       effective_version: "1.0.0"
|       domain: "workflow_builder"
|       standard_name: "WORKFLOW_BUILDER_STANDARD"
|       component_type_count: 8
|       schema_layer_count: 3
|       ---
+-- Specs/
|   +-- (empty, accepts user specs at runtime)
+-- workflow.toml
|   [workflow]
|   name = "workflow_builder_v3"
|   label = "Workflow Builder v3"
|   job_prefix = "WBUILD3"
|   pattern = "meta_meta_builder"
|
|   [[step]]
|   name = "generate_test_criteria"
|   type = "prompt"
|   onsuccess = "review_test_criteria"
|   ... (21 step sections)
+-- context_extensions.py
|   ARTIFACT_KEY_REGISTRY = {
|     "TEST_CRITERIA_FILE": "TEST_CRITERIA-{seq}.md",
|     "COMPONENT_SCHEMA_FILE": "COMPONENT_SCHEMA-{seq}.md",
|     ... (21 artifact keys)
|   }
+-- actions.py
|   @action
|   def validate_package_deterministic(...): ...
|   @action
|   def promote_workflow_package(...): ...
+-- prompts/
|   +-- 01_generate_test_criteria.txt
|   +-- 02_review_test_criteria.txt
|   +-- ...
|   +-- 18_refine_package.txt
+-- README.md
|   # Workflow Builder v3
|   Meta-meta builder that generates other meta builders...
```

### Resolution Trace

The following table traces how each output artifact resolves from its
composition binding:

| Output Artifact | Component Type | Resolution Rule | Producing Step |
|---|---|---|---|
| TEST_CRITERIA_FILE | test_criterion | RR-OC-001 | generate_test_criteria |
| REVIEW_TEST_CRITERIA_FILE | test_criterion | RR-OC-001 | review_test_criteria |
| COMPONENT_SCHEMA_FILE | layer_design | RR-OC-002 | generate_component_schema |
| COMPOSITION_FORMAT_FILE | layer_design | RR-OC-002 | generate_composition_format |
| OUTPUT_FORMAT_FILE | layer_design | RR-OC-002 | generate_output_format |
| OPERATIONAL_WORKFLOW_FILE | operational_design | RR-OC-003 | generate_operational_workflow |
| COMPOSITION_STANDARD_FILE | composition_system | RR-OC-004 | generate_composition_standard |
| META_COMPOSITION_SPEC_FILE | composition_system | RR-OC-004 | generate_meta_composition_spec |
| WORKFLOW_MANIFEST_FILE | package_file | RR-OC-005 | generate_package |
| WORKFLOW_EXTENSIONS_FILE | package_file | RR-OC-005 | generate_package |
| WORKFLOW_ACTIONS_FILE | package_file | RR-OC-005 | generate_package |
| WORKFLOW_PROMPTS_INDEX_FILE | package_file | RR-OC-005 | generate_package |
| WORKFLOW_README_FILE | package_file | RR-OC-005 | generate_package |
| GATEKEEP_COMPONENT_SCHEMA_FILE | gatekeep_verdict | RR-OC-006 | gatekeep_component_schema |
| GATEKEEP_COMPOSITION_FORMAT_FILE | gatekeep_verdict | RR-OC-006 | gatekeep_composition_format |
| GATEKEEP_OUTPUT_FORMAT_FILE | gatekeep_verdict | RR-OC-006 | gatekeep_output_format |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | gatekeep_verdict | RR-OC-006 | gatekeep_operational_workflow |
| GATEKEEP_COMPOSITION_STANDARD_FILE | gatekeep_verdict | RR-OC-006 | gatekeep_composition_standard |
| GATEKEEP_PACKAGE_FILE | gatekeep_verdict | RR-OC-006 | gatekeep_package |
| VALIDATION_REPORT_FILE | quality_report | RR-OC-007 | validate_package_deterministic |
| REVIEW_FILE_SUGGESTED | quality_report | RR-OC-007 | review_package |

---

## Extension Guide

This section provides step-by-step instructions for extending the output
composition system. New output types can be added without modifying the
workflow's workflow.toml, prompts, or actions.

### Adding a New Component Type

To add a new output artifact category (e.g., "deployment_config" for
deployment-related outputs):

1. **Define the type in the component schema (Layer 1):**

   Add a new entry to the component_types enum:
   ```yaml
   component_type: deployment_config
   ```

   Define type-specific properties:
   ```yaml
   | Property | Type | Required | Description |
   |---|---|---|---|
   | deploy_target | string | Yes | Target environment (dev, staging, prod) |
   | config_format | string | Yes | Configuration format (yaml, json, env) |
   | secret_count | integer | No | Number of secrets referenced |
   ```

   Define validation rules:
   ```yaml
   VR-OC-NEW-001: deploy_target must be one of: dev, staging, prod
   VR-OC-NEW-002: config_format must be one of: yaml, json, env
   ```

2. **Define the artifact instances:**
   ```yaml
   | Artifact Key | Description | Produced By |
   |---|---|---|
   | DEPLOY_CONFIG_FILE | Deployment configuration | generate_deploy_config |
   ```

3. **Update the component type count** in the YAML frontmatter:
   ```yaml
   component_type_count: 8  # was 7
   ```

**No workflow code changes required.** The workflow reads component types
dynamically from the standard (COMPOSITION_STANDARD.md).

### Adding a New Composition

To add a new output configuration (e.g., a "minimal" composition that produces
only essential package files):

1. **Define the composition in Layer 2 format:**

   ```yaml
   composition_id: "output-composition-minimal-001"
   composition_name: "Minimal Output Composition"
   target_output: "Essential package files only (workflow.toml, context_extensions.py, README.md)"

   component_bindings:
     test_criteria:
       - component_id: "test-criterion-acceptance-001"
     layer_designs:
       - component_id: "layer-design-schema-001"
       - component_id: "layer-design-format-001"
       - component_id: "layer-design-output-001"
     operational:
       component_id: "operational-design-workflow-001"
     composition_outputs:
       - component_id: "composition-system-standard-001"
     packages:
       - component_id: "package-file-manifest-001"
       - component_id: "package-file-extensions-001"
       - component_id: "package-file-readme-001"
     gatekeeps:
       - component_id: "gatekeep-verdict-package-001"
   ```

2. **Save the composition file** to the Specs/ directory or a compositions
   directory alongside the workflow.

3. **No workflow code changes required.** The composition is a declarative
   file that the workflow reads and resolves.

### Adding a New Artifact Instance

To add a new artifact within an existing component type (e.g., adding a
"PERFORMANCE_TEST_FILE" to the test_criterion type):

1. **Define the artifact instance:**
   ```yaml
   | Artifact Key | Description | Produced By |
   |---|---|---|
   | PERFORMANCE_TEST_FILE | Performance acceptance criteria | generate_performance_test |
   ```

2. **Add the artifact to the context_extensions.py registry:**
   ```python
   "PERFORMANCE_TEST_FILE": "PERFORMANCE_TEST-{seq}.md",
   ```

3. **Add a corresponding step** to the workflow (this is the one case where
   a workflow.toml change is needed, but only to add the new step, not to
   modify existing steps).

### Extension Compatibility Rules

| Rule | Description |
|---|---|
| Backward compatible | New component types do not break existing compositions |
| Additive only | New compositions add to the output set; they do not remove existing outputs |
| Schema stable | Common properties (component_id, component_type, name, version, description) are never changed |
| Override safe | Overrides can only modify type-specific properties, not common properties |

### Extension Checklist

Before declaring an extension complete, verify:

- [ ] New component type added to the component schema (Layer 1)
- [ ] Type-specific properties defined with types and required/optional flags
- [ ] Validation rules defined for the new type
- [ ] At least one artifact instance defined
- [ ] Composition bindings updated if the new type is required
- [ ] Example composition updated to include the new type
- [ ] Resolution rule added (Layer 3) for the new type
- [ ] Quality requirements updated if the new type affects output quality
- [ ] YAML frontmatter component_type_count updated
- [ ] No existing compositions broken by the change

---

## Self-Validation

### Component Type Completeness

| Check ID | Check | Result |
|---|---|---|
| SV-001 | All 7 component types defined | PASS |
| SV-002 | Common properties defined for all types | PASS |
| SV-003 | Type-specific properties defined for each type | PASS |
| SV-004 | Validation rules defined (VR-OC-001 through VR-OC-010) | PASS |
| SV-005 | Artifact instances mapped for each type | PASS |

### Composition Format Quality

| Check ID | Check | Result |
|---|---|---|
| SV-006 | Composition structure defined | PASS |
| SV-007 | 7 binding rules defined | PASS |
| SV-008 | Override mechanism documented | PASS |
| SV-009 | Placeholder resolution defined | PASS |
| SV-010 | Example composition provided | PASS |

### Output Format Quality

| Check ID | Check | Result |
|---|---|---|
| SV-011 | Resolved output structure defined | PASS |
| SV-012 | 7 resolution rules defined (RR-OC-001 through RR-OC-007) | PASS |
| SV-013 | 8 quality requirements defined (QR-OC-001 through QR-OC-008) | PASS |
| SV-014 | Example output skeleton provided | PASS |
| SV-015 | Resolution trace table provided | PASS |

### Extension Guide Quality

| Check ID | Check | Result |
|---|---|---|
| SV-016 | Step-by-step instructions for adding new component type | PASS |
| SV-017 | Step-by-step instructions for adding new composition | PASS |
| SV-018 | Step-by-step instructions for adding new artifact instance | PASS |
| SV-019 | Compatibility rules documented | PASS |
| SV-020 | Extension checklist provided | PASS |

### Artifact Coverage

All 21 output artifacts from OPERATIONAL_WORKFLOW-001.md Section 4 are
covered by this specification:

| Artifact Key | Component Type | Covered |
|---|---|---|
| TEST_CRITERIA_FILE | test_criterion | YES |
| REVIEW_TEST_CRITERIA_FILE | test_criterion | YES |
| COMPONENT_SCHEMA_FILE | layer_design | YES |
| GATEKEEP_COMPONENT_SCHEMA_FILE | gatekeep_verdict | YES |
| COMPOSITION_FORMAT_FILE | layer_design | YES |
| GATEKEEP_COMPOSITION_FORMAT_FILE | gatekeep_verdict | YES |
| OUTPUT_FORMAT_FILE | layer_design | YES |
| GATEKEEP_OUTPUT_FORMAT_FILE | gatekeep_verdict | YES |
| OPERATIONAL_WORKFLOW_FILE | operational_design | YES |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | gatekeep_verdict | YES |
| COMPOSITION_STANDARD_FILE | composition_system | YES |
| GATEKEEP_COMPOSITION_STANDARD_FILE | gatekeep_verdict | YES |
| META_COMPOSITION_SPEC_FILE | composition_system | YES |
| WORKFLOW_MANIFEST_FILE | package_file | YES |
| WORKFLOW_EXTENSIONS_FILE | package_file | YES |
| WORKFLOW_ACTIONS_FILE | package_file | YES |
| WORKFLOW_PROMPTS_INDEX_FILE | package_file | YES |
| WORKFLOW_README_FILE | package_file | YES |
| VALIDATION_REPORT_FILE | quality_report | YES |
| GATEKEEP_PACKAGE_FILE | gatekeep_verdict | YES |
| REVIEW_FILE_SUGGESTED | quality_report | YES |

**Coverage: 21/21 artifacts covered.**

### Three-Layer Conformance

| Layer | Defined | Content |
|---|---|---|
| Layer 1: Component Schema | YES | 7 component types, common properties, type-specific properties, validation rules |
| Layer 2: Composition Format | YES | Composition structure, 7 binding rules, override mechanism, placeholder resolution, example |
| Layer 3: Output Format | YES | Resolved output structure, 7 resolution rules, 8 quality requirements, example skeleton |

### Consistency with Prior Artifacts

| Check | Source | Result |
|---|---|---|
| Artifact count matches OPERATIONAL_WORKFLOW-001.md | 21 output artifacts | MATCH |
| Producing steps match OPERATIONAL_WORKFLOW-001.md | Step sequence table | MATCH |
| Output structure matches OUTPUT_FORMAT-001.md | 3-part directory | MATCH |
| Resolution rules align with OUTPUT_FORMAT-001.md | RR-001 through RR-007 | ALIGNED |
| Quality requirements align with OUTPUT_FORMAT-001.md | QR-001 through QR-008 | ALIGNED |
| Composition pattern follows COMPOSITION_SYSTEM_STANDARD.md | Three-layer architecture | CONFORMANT |

---

**End of Output Composition Specification**
