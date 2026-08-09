---
doc_type: "component_schema"
lifecycle_status: "draft"
domain: "workflow_builder"
component_type_count: 8
spec_reference: "workflow_builder_v4.md"
generated_by: "generate_component_schema"
validation_rule_count: 16
---

# Component Schema (Layer 1)

## Overview

This document defines the Universal Component Schema for the
workflow_builder domain at Layer 1 of the three-layer composition
architecture. It is the foundational building block library for the
Workflow Builder v3 meta-meta composition system.

The schema defines exactly 8 component types that represent the
structural building blocks of every meta builder produced by this
system. Each generated meta builder is composed of instances of these
8 types.

**Domain:** workflow_builder
**Schema layer:** Layer 1 (Component Schema)
**Component type count:** 8
**Validation rules defined:** 16 (VR-001 through VR-016)
**Schema pattern reference:** Three-layer architecture -- Component
Schema (Layer 1), Composition Format (Layer 2), Output Format (Layer 3)

The 8 component types are:

| Type Number | Type Name | Purpose |
|---|---|---|
| 1 | step_definition | A workflow step with type, purpose, inputs, outputs |
| 2 | role_policy | Coder role assignment for a step |
| 3 | routing_pattern | How steps connect (success, reject, refine) |
| 4 | prompt_pattern | Prompt structure elements |
| 5 | artifact_contract | Input/output artifact definitions |
| 6 | composition_standard | The composition standard schema for the generated meta builder |
| 7 | output_variance | A specific output configuration |
| 8 | domain_spec | A user-provided spec type the builder processes |

---

## Common Properties

All 8 component types share the following common properties regardless
of their component_type value. These form the stable foundation of the
Universal Component Schema.

### Required Common Properties (5)

Every component instance must include all 5 of these properties. A
component missing any one of them fails validation.

| Property | Type | Required | Description |
|---|---|---|---|
| component_id | string | Yes | Unique identifier for this component instance. Format: {type-prefix}-{name}-{seq}. Must be globally unique across all components within a single composition. |
| component_type | enum | Yes | One of the 8 defined types: step_definition, role_policy, routing_pattern, prompt_pattern, artifact_contract, composition_standard, output_variance, domain_spec. |
| name | string | Yes | Human-readable display name for this component. Used in documentation, traceability tables, and user interfaces. |
| version | string | Yes | Semantic version in MAJOR.MINOR.PATCH format (e.g., "1.0.0"). Each segment must be a non-negative integer. |
| description | string | Yes | A detailed description of what this component does, its purpose within the workflow, and when it is applicable. Must be a non-empty string of at least 10 characters. |

### Optional Common Properties (3)

These properties may be included on any component type. They are not
required but provide additional classification and filtering metadata.

| Property | Type | Required | Description |
|---|---|---|---|
| duration_range | string | No | An applicable duration or scope constraint for this component. Example: "5-15 minutes" or "single phase". |
| platforms | array | No | Target platforms or runtime contexts where this component is applicable. Example: ["windows", "linux"]. |
| tags | array | No | Classification tags for search, filtering, and traceability. Example: ["generation", "validation", "qc"]. |

---

## Component Types

This section defines each of the 8 component types with their
type-specific properties, type-specific validation rules, and a
complete YAML example.

### Type 1: step_definition

**Purpose:** Defines a single workflow step with its execution type,
purpose, required inputs, and produced outputs. Each step is an atomic
unit of work in the workflow pipeline. Steps are ordered and their
execution sequence is determined by their position in the step_bindings
array.

**Required:** Yes. Every workflow must define at least one
step_definition.

**Cardinality:** Ordered list (N steps per workflow).

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| step_name | string | Yes | Unique step identifier within the workflow. Must be lowercase with underscores (e.g., generate_component_schema). Must be unique across all steps in the workflow (VR-006). |
| step_type | enum | Yes | The execution type of this step. Allowed values: "prompt" or "action". Determines whether this step is driven by an LLM coder or a deterministic Python action (VR-007). |
| purpose | string | Yes | What this step achieves. Must be a non-empty descriptive string explaining the step goal. |
| required_inputs | array | No | Artifact keys this step reads as inputs. Each entry must reference an artifact produced by a preceding step or declared as a workflow-level input (VR-012, VR-015). |
| produces | array | Yes | Artifact keys this step writes as outputs. Must be non-empty for every step. Each key must use UPPER_SNAKE_CASE with _FILE suffix (VR-009). |
| enable_notifications | boolean | Yes | Whether to send notifications on step completion. Default: false. |
| requires_human_approval_after | boolean | Yes | Whether to pause workflow execution for human approval after this step completes. Default: false. |

**Validation Rules Applied:**
- VR-006: No duplicate step_name values within a workflow.
- VR-007: step_type must be "prompt" or "action".
- VR-009: All artifact keys in produces must be UPPER_SNAKE_CASE with _FILE suffix.
- VR-012: Every required_inputs entry must reference a prior-produced artifact or a declared workflow input.
- VR-015: If the step prompt references WORKFLOW_SPEC_FILE, it must declare WORKFLOW_SPEC_FILE in required_inputs.

**Example:**

```yaml
- component_id: "step-generate_component_schema-01"
  component_type: "step_definition"
  name: "Generate Component Schema"
  version: "1.0.0"
  description: "Generate the component schema for Layer 1 of the composition system"
  step_name: "generate_component_schema"
  step_type: "prompt"
  purpose: "Generate the component schema defining all component types for Layer 1"
  required_inputs:
    - "WORKFLOW_SPEC_FILE"
    - "TEST_CRITERIA_FILE"
  produces:
    - "COMPONENT_SCHEMA_FILE"
  enable_notifications: false
  requires_human_approval_after: false
```

### Type 2: role_policy

**Purpose:** Defines a coder role assignment for a workflow step. Each
step must be bound to exactly one role_policy that determines which
coder backend and instruction set handles the step execution.

**Required:** Yes. Every step must have a role_policy.

**Cardinality:** Singleton per step (exactly one role_policy per
step_definition).

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| policy_name | enum | Yes | The role policy to assign. Must be one of: architect_standard, reviewer_standard, gatekeeper_standard, validation_standard, refine_standard (VR-008). |
| assignment_rule | string | Yes | A description of when and why this policy is assigned. Specifies the conditions under which this role is appropriate for a step. |

**Valid policy_name values and their typical assignments:**

| policy_name | Typical Assignment |
|---|---|
| architect_standard | Generation steps that create documents or designs |
| reviewer_standard | Review steps that evaluate artifacts for quality |
| gatekeeper_standard | Gatekeep steps that enforce quality thresholds |
| validation_standard | Deterministic validation action steps |
| refine_standard | Refinement steps that improve rejected artifacts |

**Validation Rules Applied:**
- VR-008: policy_name must be one of the 5 defined role policies.

**Example:**

```yaml
- component_id: "role-architect_standard-01"
  component_type: "role_policy"
  name: "Architect Standard"
  version: "1.0.0"
  description: "Standard role for generation steps that create documents"
  policy_name: "architect_standard"
  assignment_rule: "Applied to generation steps that create documents, designs, or schemas"
```

### Type 3: routing_pattern

**Purpose:** Defines how steps connect to each other within the
workflow. Controls the flow of execution including the success path,
reject-refine loops, and terminal failure conditions.

**Required:** Yes. Every step must have a routing_pattern.

**Cardinality:** Singleton per step (exactly one routing_pattern per
step_definition).

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| onsuccess | string | Yes | Name of the next step to execute on success. Must reference a valid step_name that exists in the workflow (VR-010). |
| on_reject_refine | object | No | Refinement loop configuration. Required for review and gatekeep steps that support rejection. Contains the reject-refine sub-structure. |
| max_iterations | integer | No | Maximum number of refine loop iterations. Required if on_reject_refine is defined. Typical values: 1-5. |
| exhausted_failure_code | string | No | Terminal failure code when max_iterations is exhausted. Required if on_reject_refine is defined. Format: UPPER_SNAKE_CASE. |
| exhausted_failure_class | string | No | Failure classification when refine iterations are exhausted. Required if on_reject_refine is defined. Typical value: "HUMAN_RETRY_REQUIRED". |

**on_reject_refine sub-structure:**

| Field | Type | Required | Description |
|---|---|---|---|
| step | string | Yes | Step name to jump to on rejection. |
| artifact | string | Yes | Artifact key that triggered the rejection. |
| max_iterations | integer | Yes | Maximum refine loop iterations before terminal failure. |
| exhausted_failure_code | string | Yes | Terminal failure code when iterations are exhausted. |
| exhausted_failure_class | string | Yes | Failure classification for exhausted iterations. |

**Validation Rules Applied:**
- VR-010: Every step must have onsuccess routing to a valid next step name.

**Example (simple routing):**

```yaml
- component_id: "routing-generate_component_schema-01"
  component_type: "routing_pattern"
  name: "Generate Component Schema Routing"
  version: "1.0.0"
  description: "Routes to gatekeep step on success"
  onsuccess: "gatekeep_component_schema"
```

**Example (with reject-refine loop):**

```yaml
- component_id: "routing-gatekeep_component_schema-01"
  component_type: "routing_pattern"
  name: "Gatekeep Component Schema Routing"
  version: "1.0.0"
  description: "Routes to next phase on approval, or back to refinement on rejection"
  onsuccess: "generate_composition_format"
  on_reject_refine:
    step: "refine_component_schema"
    artifact: "COMPONENT_SCHEMA_FILE"
    max_iterations: 2
    exhausted_failure_code: "COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED"
    exhausted_failure_class: "HUMAN_RETRY_REQUIRED"
```

### Type 4: prompt_pattern

**Purpose:** Defines structural elements that are injected into prompt
templates. Each pattern adds a specific section to the prompt, ensuring
consistent quality checks, self-criticism, and output structure across
all prompt-driven steps.

**Required:** No. Only applicable to prompt-type steps.

**Cardinality:** Unordered set per prompt-driven step.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| pattern_name | enum | Yes | The pattern to inject into the prompt template. Must be one of: self_critic, self_validation, context_verification, reference_inputs, generation_tasks, forbidden_content, output_instructions. |
| sections | array | Yes | List of prompt section descriptions that this pattern contributes to the prompt template. Each entry is a human-readable description of the section content. |

**Valid pattern_name values:**

| pattern_name | Purpose |
|---|---|
| self_critic | Challenges the coder to question its own reasoning before finalizing output |
| self_validation | Requires the coder to verify completeness and correctness of its output |
| context_verification | Instructs the coder to verify it has read all reference inputs |
| reference_inputs | Lists the input files the coder must read before producing output |
| generation_tasks | Describes the specific content generation tasks for the step |
| forbidden_content | Specifies content patterns that must not appear in the output |
| output_instructions | Defines the file output format, path, and writing instructions |

**Validation Rules Applied:**
- VR-011: Every prompt-type step must include self_critic and self_validation patterns. Missing either pattern is a validation failure.

**Example:**

```yaml
- component_id: "prompt-self_critic-01"
  component_type: "prompt_pattern"
  name: "Self Critic Pattern"
  version: "1.0.0"
  description: "Challenges the coder to question its reasoning before checking completeness"
  pattern_name: "self_critic"
  sections:
    - "Challenge your reasoning"
    - "Did you read the spec for each property or invent them"
    - "Are your rules specific and enforceable"
```

### Type 5: artifact_contract

**Purpose:** Defines an input or output artifact that flows through the
workflow. Artifacts are named files produced and consumed by steps.
Each artifact_contract specifies the key, format, and ownership of a
single artifact.

**Required:** Yes. Every workflow must define its artifact contracts.

**Cardinality:** Unordered set per workflow.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| artifact_key | string | Yes | Unique artifact identifier. Must be UPPER_SNAKE_CASE with _FILE suffix for document artifacts (VR-009). |
| artifact_description | string | Yes | What this artifact contains and its purpose in the workflow data flow. |
| filename_pattern | string | No | Filename pattern with placeholders (e.g., "COMPONENT_SCHEMA-{seq}.md"). |
| required | boolean | Yes | Whether this artifact is required for workflow execution. |
| produced_by | string | No | The step_name that produces this artifact. Required for output artifacts. |

**Validation Rules Applied:**
- VR-009: artifact_key must be UPPER_SNAKE_CASE with _FILE suffix for document artifacts.

**Example:**

```yaml
- component_id: "artifact-COMPONENT_SCHEMA_FILE-01"
  component_type: "artifact_contract"
  name: "Component Schema File"
  version: "1.0.0"
  description: "Component schema defining all 8 component types for Layer 1"
  artifact_key: "COMPONENT_SCHEMA_FILE"
  artifact_description: "Defines the component schema with all type definitions, validation rules, and examples"
  filename_pattern: "COMPONENT_SCHEMA-{seq}.md"
  required: true
  produced_by: "generate_component_schema"
```

### Type 6: composition_standard

**Purpose:** Defines the composition standard schema for the generated
meta builder. This is the key self-describing element that makes each
generated meta builder aware of its own component types and structure.
It is the bridge between Layer 1 (components) and the higher layers.

**Required:** Yes. Every meta builder must define exactly one
composition_standard.

**Cardinality:** Singleton per workflow.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| standard_name | string | Yes | Name of the composition standard (e.g., "WORKFLOW_BUILDER_STANDARD"). |
| standard_version | string | Yes | Version of the standard in MAJOR.MINOR.PATCH format. |
| component_types_defined | array | Yes | List of component type names defined in this standard. Must match the actual type definitions in the schema. |
| schema_sections | array | Yes | Must contain exactly 3 entries: "Component Schema", "Composition Format", "Output Format" (VR-013). |
| extensibility_model | string | Yes | Description of how new component types can be added without breaking existing compositions. |

**Validation Rules Applied:**
- VR-013: composition_standard must define all 3 schema layers. The schema_sections array must contain exactly: "Component Schema", "Composition Format", "Output Format".

**Example:**

```yaml
- component_id: "standard-workflow_builder-01"
  component_type: "composition_standard"
  name: "Workflow Builder Standard"
  version: "1.0.0"
  description: "The composition standard for the workflow_builder domain defining all component types and schema layers"
  standard_name: "WORKFLOW_BUILDER_STANDARD"
  standard_version: "1.0.0"
  component_types_defined:
    - "step_definition"
    - "role_policy"
    - "routing_pattern"
    - "prompt_pattern"
    - "artifact_contract"
    - "composition_standard"
    - "output_variance"
    - "domain_spec"
  schema_sections:
    - "Component Schema"
    - "Composition Format"
    - "Output Format"
  extensibility_model: "New component types can be added to the standard without breaking existing compositions. Existing compositions reference components by component_id, not by type enumeration."
```

### Type 7: output_variance

**Purpose:** Defines a specific output configuration the meta builder
can produce. Output variances allow the same workflow to generate
different types of deliverables based on the input specification and
composition-time choices.

**Required:** No. Only used when the meta builder supports multiple
output configurations.

**Cardinality:** Unordered set per workflow.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| variance_name | string | Yes | Name identifying this output variance (e.g., "prompt_only_workflow"). Must be unique within the workflow. |
| variance_description | string | Yes | What this variance produces and how it differs from other variances. |
| component_requirements | array | Yes | Which component types are required for this variance. Each entry must be a valid component_type from the 8 base types (VR-014). |
| output_files | array | Yes | Files produced when this variance is selected. Must be non-empty. |

**Validation Rules Applied:**
- VR-014: output_variance component_requirements must be feasible. Each entry must be a defined component type from the 8 base types.

**Example:**

```yaml
- component_id: "variance-prompt_only_workflow-01"
  component_type: "output_variance"
  name: "Prompt Only Workflow"
  version: "1.0.0"
  description: "A workflow with only prompt-driven steps and no deterministic action steps beyond gatekeeping"
  variance_name: "prompt_only_workflow"
  variance_description: "A workflow with only prompt-driven steps (no API action steps beyond validation)"
  component_requirements:
    - "step_definition"
    - "role_policy"
    - "routing_pattern"
    - "prompt_pattern"
    - "artifact_contract"
  output_files:
    - "workflow.toml"
    - "prompts/*.txt"
    - "context_extensions.py"
    - "README.md"
```

### Type 8: domain_spec

**Purpose:** Defines a type of user-provided specification the meta
builder can process. This allows the builder to validate incoming specs
against expected structure and version compatibility before processing.

**Required:** No. Only used when the meta builder accepts external
specifications as input.

**Cardinality:** Unordered set per workflow.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| spec_type | string | Yes | Type identifier for this specification (e.g., "composition_system_spec"). |
| spec_version_range | string | Yes | Compatible version range (e.g., "1.0.0 - 4.99.99"). |
| required_sections | array | Yes | Sections the specification must contain. Each entry is a section heading name. |
| example_specs | array | No | Example specification filenames for reference. |

**Validation Rules Applied:**
- No type-specific validation rules beyond the common property rules.
  Type-specific validation is deferred to the composition format layer
  (Layer 2).

**Example:**

```yaml
- component_id: "spec-composition_system_spec-01"
  component_type: "domain_spec"
  name: "Composition System Specification"
  version: "1.0.0"
  description: "A composition system spec that the workflow builder processes as input"
  spec_type: "composition_system_spec"
  spec_version_range: "1.0.0 - 4.99.99"
  required_sections:
    - "Domain Overview"
    - "Component Schema"
    - "Composition Format"
    - "Output Format"
    - "Operational Requirements"
  example_specs:
    - "workflow_builder_v3.md"
    - "workflow_builder_v4.md"
```

---

## Validation Rules (Global)

The following 16 validation rules apply to all component instances
across all 8 component types. Each rule has a unique identifier, a
machine-readable condition, and a severity level.

| Rule ID | Rule | Severity |
|---|---|---|
| VR-001 | Every component must have all 5 required common properties: component_id, component_type, name, version, description. Missing any required property is a validation failure. | CRITICAL |
| VR-002 | component_type must be one of the 8 defined types: step_definition, role_policy, routing_pattern, prompt_pattern, artifact_contract, composition_standard, output_variance, domain_spec. Unknown types are rejected. | CRITICAL |
| VR-003 | No two components within a single composition may share the same component_id. Duplicate identifiers cause immediate rejection. | CRITICAL |
| VR-004 | Each component must conform to its type-specific schema as defined in the Component Types section. Properties not defined for the declared type are rejected. | HIGH |
| VR-005 | version must follow MAJOR.MINOR.PATCH format where each segment is a non-negative integer (e.g., "1.0.0"). Non-conforming versions are rejected. | MEDIUM |
| VR-006 | No duplicate step_name values within a workflow. Each step_definition must have a unique step_name across all steps in the same workflow. | CRITICAL |
| VR-007 | step_type must be one of: "prompt" or "action". No other values are permitted. | CRITICAL |
| VR-008 | policy_name must be one of the 5 defined role policies: architect_standard, reviewer_standard, gatekeeper_standard, validation_standard, refine_standard. | CRITICAL |
| VR-009 | artifact_key must be UPPER_SNAKE_CASE with _FILE suffix for document artifacts. Keys not matching this pattern are rejected. | HIGH |
| VR-010 | Every step must have onsuccess routing to a valid next step. The referenced step_name must exist in the workflow step_bindings. | CRITICAL |
| VR-011 | Every prompt-type step must include self_critic and self_validation prompt patterns. Missing either pattern is a validation failure. | HIGH |
| VR-012 | Every required_inputs artifact must reference an artifact produced by a preceding step or declared as a workflow-level input artifact. Temporal ordering must be respected. | CRITICAL |
| VR-013 | composition_standard must define all 3 schema layers. The schema_sections array must contain exactly: "Component Schema", "Composition Format", "Output Format". | CRITICAL |
| VR-014 | output_variance component_requirements must be feasible. Each entry must be a valid defined component type from the 8 base types. | HIGH |
| VR-015 | Every step that references the WORKFLOW_SPEC_FILE artifact key in its prompt template must declare WORKFLOW_SPEC_FILE in its required_inputs array. Bidirectional check: if WORKFLOW_SPEC_FILE is declared in required_inputs, it must appear as a placeholder in the prompt. Absence of either direction is a failure. | CRITICAL |
| VR-016 | Both generate_package and refine_package steps must declare STANDARDS_COMPOSITION_STANDARD_FILE in their produces lists in workflow.toml. If either step omits this declaration, validation fails. This ensures the composition standard is always generated during package assembly. | CRITICAL |

---

## Extensibility Model

New component types can be added to this schema without breaking
existing compositions. The extensibility model follows these principles:

1. **Identity stability:** Existing compositions reference components by
   component_id, not by type enumeration. Adding new types does not
   affect existing component references.

2. **Common property stability:** The 5 required common properties
   (component_id, component_type, name, version, description) and 3
   optional common properties (duration_range, platforms, tags) remain
   stable across all types. New types inherit these without modification.

3. **Additive extension:** New types are added by defining their
   type-specific properties in the Component Types section. Existing
   types are not modified or removed.

4. **Validation rule isolation:** New types may introduce additional
   type-specific validation rules. These rules are scoped to the new
   type and do not modify existing global rules (VR-001 through VR-016).
   New rules are appended with incrementing identifiers (VR-017, VR-018,
   etc.).

5. **Discovery compatibility:** The dynamic discovery mechanism
   (discover_component_types) automatically picks up new types from the
   generated composition standard, so no code changes are needed for
   discovery.

6. **Backward compatibility:** Compositions created before a new type
   is added continue to function without modification. They simply do
   not use the new type.

**Procedure for adding a new component type:**

1. Define the new type name in the Component Types section.
2. Specify its required and optional type-specific properties.
3. Add any type-specific validation rules (appending to the global
   rule sequence).
4. Update component_type_count in the YAML frontmatter.
5. Provide at least one example component with all required properties.
6. Update the extensibility_model description if constraints change.

---

## Component File Format

Components are not stored as individual files. They are defined inline
in the workflow composition (Layer 2) and materialized as output
artifacts in the Layer 3 output structure.

### Storage Model

| Storage Location | Format | Description |
|---|---|---|
| workflow.toml | TOML | step_definition, role_policy, routing_pattern are materialized as [[step]] sections |
| prompts/*.txt | Plain text | prompt_pattern components are materialized as prompt template sections |
| context_extensions.py | Python | artifact_contract components are registered via register_artifact_keys() |
| Standards/COMPOSITION_STANDARD.md | Markdown with YAML frontmatter | composition_standard component is materialized here |
| Inline in composition | YAML | output_variance and domain_spec components are defined in the composition YAML |

### Exchange Format

When components are exchanged between tools or stored for reference,
they use YAML format with the common properties as top-level keys and
type-specific properties alongside them. Each component is a YAML
mapping (dictionary).

### Example Complete Component (YAML)

```yaml
component_id: "step-generate_package-01"
component_type: "step_definition"
name: "Generate Package"
version: "1.0.0"
description: "Generate the complete workflow package with all files"
step_name: "generate_package"
step_type: "prompt"
purpose: "Generate workflow.toml, prompts, actions, and composition standard"
required_inputs:
  - "WORKFLOW_SPEC_FILE"
  - "COMPOSITION_STANDARD_FILE"
  - "META_COMPOSITION_SPEC_FILE"
produces:
  - "WORKFLOW_MANIFEST_FILE"
  - "WORKFLOW_EXTENSIONS_FILE"
  - "WORKFLOW_ACTIONS_FILE"
  - "WORKFLOW_PROMPTS_INDEX_FILE"
  - "WORKFLOW_README_FILE"
  - "STANDARDS_COMPOSITION_STANDARD_FILE"
enable_notifications: false
requires_human_approval_after: false
```

---

## Self-Validation

### Component Type Completeness

| Number | Component Type | Defined | Has Properties | Has Validation Rules | Has Example |
|---|---|---|---|---|---|
| 1 | step_definition | YES | YES (7 type-specific) | YES (VR-006, VR-007, VR-009, VR-012, VR-015) | YES |
| 2 | role_policy | YES | YES (2 type-specific) | YES (VR-008) | YES |
| 3 | routing_pattern | YES | YES (5 type-specific) | YES (VR-010) | YES (2 examples) |
| 4 | prompt_pattern | YES | YES (2 type-specific) | YES (VR-011) | YES |
| 5 | artifact_contract | YES | YES (5 type-specific) | YES (VR-009) | YES |
| 6 | composition_standard | YES | YES (5 type-specific) | YES (VR-013) | YES |
| 7 | output_variance | YES | YES (4 type-specific) | YES (VR-014) | YES |
| 8 | domain_spec | YES | YES (4 type-specific) | YES (common rules only) | YES |

**Verification:** All 8 component types are defined with properties,
validation rules, and at least one complete example. TC-009 through
TC-012 satisfied.

### Common Properties Completeness

| Property | Required | Type | Defined |
|---|---|---|---|
| component_id | Yes | string | YES |
| component_type | Yes | enum | YES |
| name | Yes | string | YES |
| version | Yes | string | YES |
| description | Yes | string | YES |
| duration_range | No | string | YES |
| platforms | No | array | YES |
| tags | No | array | YES |

**Verification:** 5 required + 3 optional = 8 common properties.
TC-013 and TC-014 satisfied.

### Validation Rules Completeness

| Rule ID | Defined | Severity | Scope |
|---|---|---|---|
| VR-001 | YES | CRITICAL | Common properties presence |
| VR-002 | YES | CRITICAL | Valid component_type enumeration |
| VR-003 | YES | CRITICAL | Unique component_id within composition |
| VR-004 | YES | HIGH | Type-specific schema conformance |
| VR-005 | YES | MEDIUM | Semantic version format |
| VR-006 | YES | CRITICAL | Unique step_name within workflow |
| VR-007 | YES | CRITICAL | Valid step_type (prompt/action) |
| VR-008 | YES | CRITICAL | Valid policy_name (5 role policies) |
| VR-009 | YES | HIGH | Artifact key format (UPPER_SNAKE_CASE _FILE) |
| VR-010 | YES | CRITICAL | Routing completeness (onsuccess) |
| VR-011 | YES | HIGH | Prompt pattern completeness |
| VR-012 | YES | CRITICAL | Artifact flow integrity |
| VR-013 | YES | CRITICAL | Composition standard 3 layers |
| VR-014 | YES | HIGH | Output variance feasibility |
| VR-015 | YES | CRITICAL | WORKFLOW_SPEC_FILE prompt-input bidirectional consistency |
| VR-016 | YES | CRITICAL | STANDARDS_COMPOSITION_STANDARD_FILE in both generate_package and refine_package produces |

**Verification:** 16 validation rules defined (VR-001 through VR-016).
TC-016 through TC-019 satisfied.

### Example Completeness

| Component Type | Example Provided | All Required Properties Populated |
|---|---|---|
| step_definition | YES | YES (component_id, component_type, name, version, description, step_name, step_type, purpose, produces, enable_notifications, requires_human_approval_after) |
| role_policy | YES | YES (component_id, component_type, name, version, description, policy_name, assignment_rule) |
| routing_pattern | YES (2 examples) | YES (component_id, component_type, name, version, description, onsuccess) |
| prompt_pattern | YES | YES (component_id, component_type, name, version, description, pattern_name, sections) |
| artifact_contract | YES | YES (component_id, component_type, name, version, description, artifact_key, artifact_description, required, produced_by) |
| composition_standard | YES | YES (component_id, component_type, name, version, description, standard_name, standard_version, component_types_defined, schema_sections, extensibility_model) |
| output_variance | YES | YES (component_id, component_type, name, version, description, variance_name, variance_description, component_requirements, output_files) |
| domain_spec | YES | YES (component_id, component_type, name, version, description, spec_type, spec_version_range, required_sections, example_specs) |

**Verification:** All 8 types have at least one example with all
required properties populated. TC-020 satisfied.

### Criteria Traceability

| Criteria | Status | Evidence |
|---|---|---|
| TC-009 | PASS | 8 types defined in Component Types section, matching Section 2.1 of spec |
| TC-010 | PASS | Each type has a purpose description explaining its role |
| TC-011 | PASS | Required/optional flags match spec (5 required, 3 optional types) |
| TC-012 | PASS | Cardinality matches spec for all 8 types |
| TC-013 | PASS | 5 required common properties defined in Common Properties section |
| TC-014 | PASS | 3 optional common properties defined (duration_range, platforms, tags) |
| TC-015 | PASS | Type-specific properties defined for each type |
| TC-016 | PASS | 16 rules VR-001 to VR-016 with IDs and descriptions |
| TC-017 | PASS | All rules use specific verifiable conditions |
| TC-018 | PASS | VR-015 specifies bidirectional WORKFLOW_SPEC_FILE check |
| TC-019 | PASS | VR-016 specifies both generate_package and refine_package declare STANDARDS_COMPOSITION_STANDARD_FILE |
| TC-020 | PASS | All 8 types have complete YAML examples |

**Verification:** All Phase 2 criteria (TC-009 through TC-020) are
satisfied by this document.

---

End of Component Schema Document
