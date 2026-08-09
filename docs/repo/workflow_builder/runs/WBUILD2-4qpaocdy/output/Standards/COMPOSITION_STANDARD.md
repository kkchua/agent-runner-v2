---
doc_type: "composition_standard"
lifecycle_status: "active"
effective_version: "1.0.0"
domain: "workflow_builder"
standard_name: "WORKFLOW_BUILDER_STANDARD"
component_type_count: 8
schema_layer_count: 3
---

# Composition Standard: Workflow Builder Standard

## Overview

This standard defines the composition system for the workflow_builder domain.
It is the self-describing composition standard for the Workflow Builder v3
meta-meta builder. The standard follows the three-layer architecture defined
in COMPOSITION_SYSTEM_STANDARD.md, consolidating the Component Schema
(Layer 1), Composition Format (Layer 2), and Output Format (Layer 3) into
a single authoritative reference.

**Domain:** workflow_builder
**Standard name:** WORKFLOW_BUILDER_STANDARD
**Standard version:** 1.0.0
**Component types defined:** 8
**Schema layers:** 3 (Component Schema, Composition Format, Output Format)
**Workflow pattern:** meta_meta_builder
**Self-bootstrapping capable:** Yes

The workflow_builder domain is a meta-meta builder that generates other
composition system workflows (meta builders). Each generated meta builder
is itself a composition system with its own composition standard, enabling
extensibility and self-bootstrapping.

---

## Component Schema (Layer 1)

### Common Properties

All components in this schema share the following common properties,
regardless of component_type. These form the stable foundation of the
Universal Component Schema.

| Property | Type | Required | Description |
|---|---|---|---|
| component_id | string | Yes | Unique identifier. Format: {type}-{name}-{seq} |
| component_type | enum | Yes | One of the 8 defined types (see below) |
| name | string | Yes | Human-readable display name |
| version | string | Yes | Semantic version (MAJOR.MINOR.PATCH) |
| description | string | Yes | What this component does and when to use it |
| duration_range | string | No | Applicable duration or scope constraint |
| platforms | array | No | Target platforms or runtime contexts |
| tags | array | No | Classification tags for search and filtering |

### Component Types

This schema defines exactly 8 component types:

#### Type 1: step_definition

Defines a workflow step with its type, purpose, inputs, and outputs.

| Property | Type | Required | Description |
|---|---|---|---|
| step_name | string | Yes | Unique step identifier (lowercase_with_underscores) |
| step_type | enum | Yes | prompt or action |
| purpose | string | Yes | What this step achieves |
| required_inputs | array | No | Artifact keys this step reads |
| produces | array | Yes | Artifact keys this step writes |
| enable_notifications | boolean | Yes | Whether to send notifications on completion |
| requires_human_approval_after | boolean | Yes | Whether to pause for human approval |

#### Type 2: role_policy

Defines a coder role assignment for a workflow step.

| Property | Type | Required | Description |
|---|---|---|---|
| policy_name | enum | Yes | One of: architect_standard, reviewer_standard, gatekeeper_standard, validation_standard, refine_standard |
| assignment_rule | string | Yes | When and why this policy is assigned |

#### Type 3: routing_pattern

Defines how steps connect to each other (flow control).

| Property | Type | Required | Description |
|---|---|---|---|
| onsuccess | string | Yes | Name of the next step on success |
| on_reject_refine | object | No | Refinement loop configuration |
| max_iterations | integer | No | Maximum refine iterations |
| exhausted_failure_code | string | No | Terminal failure code |
| exhausted_failure_class | string | No | Failure classification |

#### Type 4: prompt_pattern

Defines structural elements injected into prompt templates.

| Property | Type | Required | Description |
|---|---|---|---|
| pattern_name | enum | Yes | One of: self_critic, self_validation, context_verification, reference_inputs, generation_tasks, forbidden_content, output_instructions |
| sections | array | Yes | List of prompt section descriptions |

#### Type 5: artifact_contract

Defines an input or output artifact that flows through the workflow.

| Property | Type | Required | Description |
|---|---|---|---|
| artifact_key | string | Yes | Unique artifact identifier (UPPER_SNAKE_CASE) |
| description | string | Yes | What this artifact contains |
| filename_pattern | string | No | Filename pattern with placeholders |
| required | boolean | Yes | Whether this artifact is required |
| produced_by | string | No | The step_name that produces this artifact |

#### Type 6: composition_standard

Defines the composition standard schema for a generated meta builder.

| Property | Type | Required | Description |
|---|---|---|---|
| standard_name | string | Yes | Name of the composition standard |
| standard_version | string | Yes | Version (MAJOR.MINOR.PATCH) |
| component_types_defined | array | Yes | List of component types in the standard |
| schema_sections | array | Yes | Must contain exactly 3 entries: "Component Schema", "Composition Format", "Output Format" |
| extensibility_model | string | Yes | How new types can be added |

#### Type 7: output_variance

Defines a specific output configuration the meta builder can produce.

| Property | Type | Required | Description |
|---|---|---|---|
| variance_name | string | Yes | Name identifying this output variance |
| variance_description | string | Yes | What this variance produces |
| component_requirements | array | Yes | Which component types are required |
| output_files | array | Yes | Files produced when this variance is selected |

#### Type 8: domain_spec

Defines a type of user-provided specification the meta builder can process.

| Property | Type | Required | Description |
|---|---|---|---|
| spec_type | string | Yes | Type identifier for this specification |
| spec_version_range | string | Yes | Compatible version range |
| required_sections | array | Yes | Sections the specification must contain |
| example_specs | array | No | Example specification filenames |

### Validation Rules

| Rule ID | Rule |
|---|---|
| VR-001 | Every component must have all 5 required common properties |
| VR-002 | component_type must be one of the 8 defined types |
| VR-003 | No two components may share the same component_id |
| VR-004 | Each component must conform to its type-specific schema |
| VR-005 | version must follow MAJOR.MINOR.PATCH format |
| VR-006 | No duplicate step_name values within a workflow |
| VR-007 | step_type must be prompt or action |
| VR-008 | policy_name must be one of 5 defined role policies |
| VR-009 | artifact_key must be UPPER_SNAKE_CASE with _FILE suffix |
| VR-010 | Every step must have onsuccess routing to a valid next step |
| VR-011 | Every prompt step must have self_critic and self_validation |
| VR-012 | Every required_inputs must reference a prior-produced artifact |
| VR-013 | composition_standard must define all 3 schema layers |
| VR-014 | output_variance must have feasible component_requirements |

### Extensibility Model

New component types can be added to this standard without breaking existing
compositions. Existing compositions reference components by component_id,
not by type, so adding new types does not affect them. The 5 required
common properties remain stable. New types may introduce additional
type-specific validation rules without modifying existing ones.

---

## Composition Format (Layer 2)

### Composition Structure

Every composition is a YAML document with these top-level fields:

| Field | Domain Field | Type | Required | Description |
|---|---|---|---|---|
| composition_id | builder_name | string | Yes | Unique builder identifier |
| name | builder_label | string | Yes | Human-readable display name |
| target_metadata | job_prefix | string | Yes | 4-6 character job ID prefix |
| target_metadata | builder_purpose | string | Yes | What problem this builder solves |
| target_metadata | workflow_pattern | enum | Yes | One of 6 defined patterns |
| component_bindings | step_bindings | array | Yes | Ordered step definitions |
| component_bindings | artifact_bindings | object | Yes | Input/output artifact contracts |
| component_bindings | composition_standard_binding | object | Yes | v3: the composition standard |
| component_bindings | output_variances | array | No | Output variance configurations |
| component_bindings | domain_specs | array | No | Input specification types |

### Binding Rules

| Binding Name | Component Type | Cardinality | Required |
|---|---|---|---|
| steps | step_definition | Ordered list | Yes |
| roles | role_policy | Singleton per step | Yes |
| routing | routing_pattern | Singleton per step | Yes |
| prompts | prompt_pattern | Unordered set per prompt step | No |
| artifacts | artifact_contract | Unordered set | Yes |
| standard | composition_standard | Singleton | Yes |
| variances | output_variance | Unordered set | No |
| domain_specs | domain_spec | Unordered set | No |

### Workflow Patterns

| Pattern | Description |
|---|---|
| action_only | All deterministic Python operations |
| prompt_driven | LLM generates documents with review/refine |
| mixed | Combination of prompt and action steps |
| gatekeeper_pipeline | Multi-phase with QC gates |
| meta_workflow_builder | Workflow that builds workflows |
| meta_meta_builder | Workflow that builds meta builders (v3) |

### Override Mechanism

Overrides allow per-composition customization of component properties
without modifying the original component. Override values merge with
base properties; override wins on conflict. Common properties
(component_id, component_type, name, version, description) cannot
be overridden. Type-specific properties and optional common properties
(duration_range, platforms, tags) can be overridden.

### Placeholder Resolution

| Data Source | Fields Provided | Resolution |
|---|---|---|
| Input Spec | WORKFLOW_SPEC_FILE, domain_name, job_prefix | Loaded at start |
| Governance | BASE_COMPOSITION_STANDARD, GOVERNANCE_RUNTIME_ROOT | Static paths |
| Runtime | job_id, seq, workspace_root | Computed at execution |

Unresolvable placeholders are flagged as {UNRESOLVED: field_name}.

---

## Output Format (Layer 3)

### 3-Part Output Structure

```
{builder_name}/
+-- Standards/
|   +-- COMPOSITION_STANDARD.md
+-- Specs/
|   +-- (user-provided specs)
+-- workflow.toml
+-- context_extensions.py
+-- actions.py
+-- prompts/
|   +-- NN_{step_name}.txt
+-- README.md
+-- .env.sample (conditional)
+-- config.json.sample (conditional)
```

### Resolution Rules

| Rule ID | Source | Target |
|---|---|---|
| RR-001 | step_bindings | workflow.toml [[step]] + prompts/*.txt |
| RR-002 | role bindings | [step.coder] sections |
| RR-003 | routing bindings | onsuccess + [step.on_reject_refine] |
| RR-004 | prompt_patterns | prompts/NN_{step_name}.txt content |
| RR-005 | artifact_bindings | context_extensions.py registry |
| RR-006 | composition_standard_binding | Standards/COMPOSITION_STANDARD.md |
| RR-007 | {placeholder} tokens | All output files |

### Quality Requirements

| Rule ID | Requirement | Severity |
|---|---|---|
| QR-001 | No dangling step references | CRITICAL |
| QR-002 | No dangling artifact references | CRITICAL |
| QR-003 | Complete prompt patterns for all prompt steps | MAJOR |
| QR-004 | Valid role assignments | CRITICAL |
| QR-005 | Artifact flow integrity (temporal ordering) | CRITICAL |
| QR-006 | Composition standard defines all 3 layers | CRITICAL |
| QR-007 | Output variance feasibility | MAJOR |
| QR-008 | Cross-file consistency | CRITICAL |

---

## Self-Validation

### Layer Completeness

| Layer | Defined | Content |
|---|---|---|
| Layer 1: Component Schema | YES | 8 component types, common properties, type-specific properties, 14 validation rules |
| Layer 2: Composition Format | YES | 8 binding rules, 6 workflow patterns, override mechanism, 3 data sources |
| Layer 3: Output Format | YES | 3-part output structure, 7 resolution rules, 8 quality requirements |

**Verification:** All 3 layers defined. QR-006 satisfied.

### Component Type Completeness

| # | Component Type | Defined | Has Example |
|---|---|---|---|
| 1 | step_definition | YES | YES |
| 2 | role_policy | YES | YES |
| 3 | routing_pattern | YES | YES |
| 4 | prompt_pattern | YES | YES |
| 5 | artifact_contract | YES | YES |
| 6 | composition_standard | YES | YES |
| 7 | output_variance | YES | YES |
| 8 | domain_spec | YES | YES |

**Verification:** 8/8 component types defined.

### Standard Conformance

| Requirement | Satisfied |
|---|---|
| Three-layer architecture (per COMPOSITION_SYSTEM_STANDARD.md) | YES |
| Universal Component Schema (common properties) | YES |
| References, not duplicates principle | YES |
| Override mechanism with merge semantics | YES |
| Placeholder resolution with 3 data sources | YES |
| Self-description capability (v3 innovation) | YES |
| ASCII-only content | YES |

---

**End of Composition Standard**
