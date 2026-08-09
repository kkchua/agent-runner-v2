---
doc_type: "component_schema"
lifecycle_status: "draft"
effective_version: "WBUILD2-4qpaocdy"
domain: "workflow_builder"
component_type_count: 8
spec_source: "workflow_builder_v3.md"
composition_standard: "COMPOSITION_SYSTEM_STANDARD.md"
---

# Component Schema: Workflow Builder v3

## Overview

This document defines the component library (Layer 1) for the workflow_builder domain. The workflow_builder domain is a meta-meta builder that generates meta builders (agents). Each generated meta builder is itself a composition system with its own composition standard, enabling extensibility and self-bootstrapping. The component library defines 8 standardized building blocks that represent the structural elements of meta builders: workflow steps, coder role assignments, routing patterns, prompt structure elements, artifact contracts, composition standards, output variances, and domain specifications. These components are the reusable LEGO bricks that compositions (Layer 2) reference to assemble complete workflow packages.

**Domain:** workflow_builder
**Component type count:** 8
**Schema pattern:** Universal Component Schema (per COMPOSITION_SYSTEM_STANDARD.md Section 3)

---

## Common Properties

All components in this schema share the following common properties, regardless of component_type. These properties form the stable foundation of the universal component schema.

| Property | Type | Required | Description |
|---|---|---|---|
| component_id | string | Yes | Unique identifier within the component library. Format: {type}-{name}-{seq} (e.g., step-generate-component-schema-001) |
| component_type | enum | Yes | One of the 8 defined types: step_definition, role_policy, routing_pattern, prompt_pattern, artifact_contract, composition_standard, output_variance, domain_spec |
| name | string | Yes | Human-readable display name for the component |
| version | string | Yes | Semantic version in MAJOR.MINOR.PATCH format (e.g., 1.0.0) |
| duration_range | string | No | Applicable duration or scope constraint (domain-specific; rarely used in workflow_builder domain) |
| platforms | array | No | Target platforms or runtime contexts where this component applies (e.g., ["daemon", "cli"]) |
| tags | array | No | Classification tags for search, filtering, and categorization |
| description | string | Yes | What this component does and when to use it |

**Notes:**
- The 5 required properties (component_id, component_type, name, version, description) are always present on every component.
- The 3 optional properties (duration_range, platforms, tags) are inherited from the Universal Component Schema and may be used when domain context benefits from them.
- component_id format uses lowercase-with-hyphens for the name portion, matching the step_name convention.
- component_type enum values are lowercase_with_underscores.

---

## Component Types

This schema defines exactly 8 component types as specified in workflow_builder_v3.md Section 2.1. No additional types are defined. No types are omitted.

### Type 1: step_definition

**Purpose:** Defines a workflow step with its type, purpose, inputs, and outputs. This is the fundamental building block of any workflow -- each step represents a discrete unit of work in the pipeline.

**Required:** Yes
**Cardinality:** Ordered list (N steps per workflow)

#### Type-Specific Properties

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| step_name | string | Yes | Unique step identifier, lowercase with underscores | "generate_component_schema" |
| step_type | enum | Yes | Execution type. Values: prompt, action | "prompt" |
| purpose | string | Yes | What this step achieves in the workflow | "Generate the component schema for Layer 1" |
| required_inputs | array | No | Artifact keys this step reads as input | ["WORKFLOW_SPEC_FILE", "TEST_CRITERIA_FILE"] |
| produces | array | Yes | Artifact keys this step writes as output | ["COMPONENT_SCHEMA_FILE"] |
| enable_notifications | boolean | Yes | Whether to send notifications on completion | true |
| requires_human_approval_after | boolean | Yes | Whether to pause and wait for human approval after this step completes | false |

#### Validation Rules (step_definition)

- step_name must be unique within the workflow (no duplicate step_name values)
- step_type must be one of: prompt, action
- produces must be a non-empty array
- required_inputs, if present, must reference artifact keys that exist in the artifact contract
- step_name must be lowercase_with_underscores

#### Example Component

```yaml
component_id: "step-generate-component-schema-001"
component_type: "step_definition"
name: "Generate Component Schema"
version: "1.0.0"
tags: [layer1, generation, schema]
description: "Generates the component schema document defining all 8 component types for Layer 1 of the composition system"
step_name: "generate_component_schema"
step_type: "prompt"
purpose: "Generate the component schema for Layer 1"
required_inputs:
  - "WORKFLOW_SPEC_FILE"
  - "TEST_CRITERIA_FILE"
produces:
  - "COMPONENT_SCHEMA_FILE"
enable_notifications: true
requires_human_approval_after: false
```

---

### Type 2: role_policy

**Purpose:** Defines a coder role assignment for a workflow step. Each step is assigned exactly one role policy that determines which coder standard (architect, reviewer, gatekeeper, validation, or refine) governs how the step is executed.

**Required:** Yes
**Cardinality:** Singleton per step

#### Type-Specific Properties

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| policy_name | enum | Yes | The role policy to apply. Values: architect_standard, reviewer_standard, gatekeeper_standard, validation_standard, refine_standard | "architect_standard" |
| assignment_rule | string | Yes | When and why this policy is assigned to a step | "Generation steps (create documents, designs)" |

#### Validation Rules (role_policy)

- policy_name must be one of the 5 defined values: architect_standard, reviewer_standard, gatekeeper_standard, validation_standard, refine_standard
- assignment_rule must be a non-empty string
- Every step_definition must have exactly one role_policy bound to it

#### Example Component

```yaml
component_id: "role-architect-standard-001"
component_type: "role_policy"
name: "Architect Standard"
version: "1.0.0"
tags: [role, generation, architect]
description: "Standard for generation steps that create documents, designs, and schemas. Emphasizes completeness, traceability, and adherence to spec requirements."
policy_name: "architect_standard"
assignment_rule: "Generation steps (create documents, designs)"
```

---

### Type 3: routing_pattern

**Purpose:** Defines how steps connect to each other -- the flow control of the workflow. Specifies the next step on success, and optionally defines a refinement loop for rejected outputs.

**Required:** Yes
**Cardinality:** Singleton per step

#### Type-Specific Properties

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| onsuccess | string | Yes | Name of the next step to execute on success | "gatekeep_component_schema" |
| on_reject_refine | object | No | Refinement loop configuration when the output is rejected | See sub-structure below |
| max_iterations | integer | No | Maximum number of refine iterations (used with on_reject_refine) | 2 |
| exhausted_failure_code | string | No | Terminal failure code when max_iterations is exhausted | "COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED" |
| exhausted_failure_class | string | No | Failure classification when refinement is exhausted | "HUMAN_RETRY_REQUIRED" |

#### on_reject_refine Sub-Structure

| Field | Type | Required | Description |
|---|---|---|---|
| step | string | Yes | Step name to jump to on rejection |
| artifact | string | Yes | Artifact key that triggered the rejection |
| max_iterations | integer | Yes | Maximum number of refine loop iterations |
| exhausted_failure_code | string | Yes | Terminal failure code when iterations are exhausted |
| exhausted_failure_class | string | Yes | Failure class for exhausted refinement |

#### Validation Rules (routing_pattern)

- onsuccess is required for every step
- onsuccess must reference an existing step_name (no dangling references)
- If the step is a review or gatekeep step, on_reject_refine should be defined
- If on_reject_refine is defined, it must contain all 5 required sub-fields (step, artifact, max_iterations, exhausted_failure_code, exhausted_failure_class)
- The step referenced in on_reject_refine.step must exist in the workflow
- max_iterations must be a positive integer if present

#### Example Component

```yaml
component_id: "routing-generate-component-schema-001"
component_type: "routing_pattern"
name: "Generate Component Schema Routing"
version: "1.0.0"
tags: [routing, generation, gatekeeper]
description: "Routes generate_component_schema to gatekeep step on success; no refine loop for generation steps"
onsuccess: "gatekeep_component_schema"
```

---

### Type 4: prompt_pattern

**Purpose:** Defines structural elements that are injected into prompt templates for prompt-driven steps. These patterns enforce quality practices like self-criticism, self-validation, and reference input handling.

**Required:** No
**Cardinality:** Unordered set per prompt-driven step

#### Type-Specific Properties

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| pattern_name | enum | Yes | The prompt pattern type. Values: self_critic, self_validation, context_verification, reference_inputs, generation_tasks, forbidden_content, output_instructions | "self_critic" |
| sections | array | Yes | List of prompt section descriptions this pattern contributes | ["Challenge your reasoning before checking completeness"] |

#### Validation Rules (prompt_pattern)

- pattern_name must be one of the 7 defined values: self_critic, self_validation, context_verification, reference_inputs, generation_tasks, forbidden_content, output_instructions
- sections must be a non-empty array of strings
- Every prompt-driven step (step_type = "prompt") must have at least the self_critic and self_validation patterns bound to it
- prompt_patterns are not used for action-driven steps (step_type = "action")

#### Example Component

```yaml
component_id: "prompt-self-critic-001"
component_type: "prompt_pattern"
name: "Self Critic Pattern"
version: "1.0.0"
tags: [prompt, quality, self-critic]
description: "Injects a self-criticism section into the prompt that challenges the LLM to question its reasoning before declaring the output complete"
pattern_name: "self_critic"
sections:
  - "Challenge your reasoning before checking completeness"
  - "Identify assumptions that may not be supported by input artifacts"
  - "Verify no scope invention beyond what the spec requires"
```

---

### Type 5: artifact_contract

**Purpose:** Defines an input or output artifact that flows through the workflow. Each artifact has a unique key, a description, and metadata about how it is produced and consumed.

**Required:** Yes
**Cardinality:** Unordered set per workflow

#### Type-Specific Properties

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| artifact_key | string | Yes | Unique artifact identifier in UPPER_SNAKE_CASE | "COMPONENT_SCHEMA_FILE" |
| description | string | Yes | What this artifact contains | "Component schema for Layer 1" |
| filename_pattern | string | No | Filename pattern with placeholders for sequence numbers and extensions | "COMPONENT_SCHEMA-{seq}.md" |
| required | boolean | Yes | Whether this artifact is required for the workflow to proceed | true |
| produced_by | string | No | The step_name of the step that produces this artifact | "generate_component_schema" |

#### Validation Rules (artifact_contract)

- artifact_key format must be UPPER_SNAKE_CASE
- Document artifacts must have the _FILE suffix (e.g., COMPONENT_SCHEMA_FILE)
- artifact_key must be unique within the workflow
- If produced_by is specified, it must reference an existing step_name
- required must be a boolean value (true or false)
- Every step's required_inputs must reference an artifact that is either an input artifact (required=true, no produced_by) or produced by a prior step

#### Example Component

```yaml
component_id: "artifact-component-schema-file-001"
component_type: "artifact_contract"
name: "Component Schema File"
version: "1.0.0"
tags: [artifact, layer1, output]
description: "The generated component schema document defining all 8 component types, their properties, validation rules, and examples for Layer 1"
artifact_key: "COMPONENT_SCHEMA_FILE"
filename_pattern: "COMPONENT_SCHEMA-{seq}.md"
required: true
produced_by: "generate_component_schema"
```

---

### Type 6: composition_standard

**Purpose:** Defines the composition standard schema that the generated meta builder will use. This is the key v3 innovation -- every generated meta builder has its own composition standard that defines its component types, composition format, and output format across the 3-layer architecture.

**Required:** Yes
**Cardinality:** Singleton (defines the base standard for the meta builder)

#### Type-Specific Properties

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| standard_name | string | Yes | Name of the composition standard | "BASE_COMPOSITION_STANDARD" |
| standard_version | string | Yes | Version of the standard in semantic version format | "1.0.0" |
| component_types_defined | array | Yes | List of component types this standard defines for its domain | ["step_definition", "role_policy", "routing_pattern", "prompt_pattern", "artifact_contract", "composition_standard", "output_variance", "domain_spec"] |
| schema_sections | array | Yes | Sections of the 3-layer schema this standard covers | ["Component Schema", "Composition Format", "Output Format"] |
| extensibility_model | string | Yes | Description of how new component types can be added without breaking existing compositions | "New component types can be added to the standard without breaking existing compositions" |

#### Validation Rules (composition_standard)

- standard_name must be a non-empty string following UPPER_SNAKE_CASE convention
- standard_version must follow semantic version format (MAJOR.MINOR.PATCH)
- component_types_defined must be a non-empty array of valid component type names
- schema_sections must contain exactly 3 entries: "Component Schema", "Composition Format", "Output Format"
- extensibility_model must be a concrete, non-vague description of the extensibility mechanism
- There must be exactly one composition_standard per workflow

#### Example Component

```yaml
component_id: "standard-base-composition-001"
component_type: "composition_standard"
name: "Base Composition Standard"
version: "1.0.0"
tags: [standard, layer1, v3-innovation]
description: "The foundational composition standard for the workflow_builder domain. Defines all 8 component types and the 3-layer schema (Component Schema, Composition Format, Output Format) that every generated meta builder inherits."
standard_name: "BASE_COMPOSITION_STANDARD"
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
extensibility_model: "New component types can be added to the standard without breaking existing compositions. Existing compositions reference components by component_id, not by type, so adding new types does not affect them."
```

---

### Type 7: output_variance

**Purpose:** Defines a specific output configuration that the meta builder can produce. Output variances enable the meta builder to generate different types of workflows (e.g., prompt-only vs. mixed with API actions) based on the input specification.

**Required:** No
**Cardinality:** Unordered set (defines different output types the builder can produce)

#### Type-Specific Properties

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| variance_name | string | Yes | Name identifying this output variance | "prompt_only_workflow" |
| variance_description | string | Yes | What this variance produces and when to use it | "A workflow with only prompt-driven steps (no API actions)" |
| component_requirements | array | Yes | Which component types are required for this variance | ["step_definition", "role_policy", "routing_pattern"] |
| output_files | array | Yes | Files produced when this variance is selected | ["workflow.toml", "prompts/*.txt", "context_extensions.py"] |

#### Validation Rules (output_variance)

- variance_name must be a non-empty string, lowercase_with_underscores
- variance_description must be a non-empty string
- component_requirements must be a non-empty array of valid component_type values
- output_files must be a non-empty array of file path patterns
- Each variance must have a feasible combination of component_requirements (i.e., the required component types must be sufficient to produce the declared output_files)

#### Example Component

```yaml
component_id: "variance-prompt-only-001"
component_type: "output_variance"
name: "Prompt Only Workflow"
version: "1.0.0"
tags: [variance, prompt-only, simple]
description: "A simplified workflow variance that uses only prompt-driven steps. Suitable for workflows that do not require custom API integrations or deterministic action steps."
variance_name: "prompt_only_workflow"
variance_description: "A workflow with only prompt-driven steps (no API actions)"
component_requirements:
  - "step_definition"
  - "role_policy"
  - "routing_pattern"
output_files:
  - "workflow.toml"
  - "prompts/*.txt"
  - "context_extensions.py"
  - "README.md"
```

---

### Type 8: domain_spec

**Purpose:** Defines a type of user-provided specification that the meta builder can process. Domain specs describe the input contract -- what sections and structure the input specification must have for the meta builder to process it.

**Required:** No
**Cardinality:** Unordered set (defines input spec types the builder accepts)

#### Type-Specific Properties

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| spec_type | string | Yes | The type identifier for this kind of specification | "creative_workflow_spec" |
| spec_version_range | string | Yes | Compatible specification version range | "1.0.0 - 3.99.99" |
| required_sections | array | Yes | Sections the specification document must contain | ["Domain Overview", "Component Schema", "Composition Format", "Output Format"] |
| example_specs | array | No | Example specification filenames for reference | ["world_building_v1.md", "story_design_v1.md"] |

#### Validation Rules (domain_spec)

- spec_type must be a non-empty string, lowercase_with_underscores
- spec_version_range must be a valid version range expression
- required_sections must be a non-empty array of section name strings
- required_sections must include at minimum the 3-layer sections: "Component Schema", "Composition Format", "Output Format"
- example_specs, if present, must be an array of filename strings

#### Example Component

```yaml
component_id: "domainspec-creative-workflow-001"
component_type: "domain_spec"
name: "Creative Workflow Specification"
version: "1.0.0"
tags: [spec, creative, input]
description: "Defines the input specification format for creative workflow builders. Accepts specs that describe creative media production workflows with component types, composition rules, and output structures."
spec_type: "creative_workflow_spec"
spec_version_range: "1.0.0 - 3.99.99"
required_sections:
  - "Domain Overview"
  - "Component Schema"
  - "Composition Format"
  - "Output Format"
  - "Operational Requirements"
example_specs:
  - "video_campaign_manuscript_v2.md"
  - "creative_workflow_builder_v1.md"
```

---

## Validation Rules (Global)

The following validation rules apply to all components in the library. These rules are enforced by the gatekeeper during component validation.

### VR-001: Required Fields Present

Every component must have all 5 required common properties populated with non-empty values:
- component_id
- component_type
- name
- version
- description

### VR-002: Valid component_type

The component_type field must be one of the 8 defined types:
- step_definition
- role_policy
- routing_pattern
- prompt_pattern
- artifact_contract
- composition_standard
- output_variance
- domain_spec

Any other value is invalid.

### VR-003: Unique component_id

No two components in the library may share the same component_id. Each component_id must be globally unique within the component library scope.

### VR-004: Type-Specific Schema Conformance

Each component must conform to the type-specific property schema for its declared component_type. All required type-specific properties must be present with correct types. Optional properties, if present, must conform to their declared types.

### VR-005: Semantic Version Format

The version field must follow the semantic version format: MAJOR.MINOR.PATCH
- MAJOR: integer (breaking changes)
- MINOR: integer (new optional features)
- PATCH: integer (bug fixes, documentation)
- Example: "1.0.0", "2.3.1"

### VR-006: Step Name Uniqueness

No duplicate step_name values are allowed within a single workflow. Each step_definition must have a unique step_name.

### VR-007: Valid step_type

The step_type field (in step_definition components) must be one of: prompt, action. No other values are permitted.

### VR-008: Valid policy_name

The policy_name field (in role_policy components) must be one of the 5 defined role policies:
- architect_standard
- reviewer_standard
- gatekeeper_standard
- validation_standard
- refine_standard

### VR-009: Artifact Key Format

The artifact_key field (in artifact_contract components) must follow the format:
- UPPER_SNAKE_CASE (all uppercase letters, digits, and underscores)
- Document artifacts must have the _FILE suffix (e.g., COMPONENT_SCHEMA_FILE)

### VR-010: Routing Completeness

Every step_definition must have an onsuccess routing to a valid next step. Review and gatekeep steps that can reject must also have an on_reject_refine configuration. No step may have an onsuccess pointing to a non-existent step.

### VR-011: Prompt Pattern Completeness

Every prompt-driven step (step_type = "prompt") must have at least the self_critic and self_validation prompt patterns bound to it. These patterns are mandatory for quality assurance.

### VR-012: Artifact Flow Integrity

Every step's required_inputs must reference an artifact that is either:
- An input artifact declared at the workflow level (no produced_by), or
- Produced by a step that executes before the consuming step in the ordered step sequence

No step may consume an artifact that has not been produced by a prior step or declared as an input.

### VR-013: Composition Standard Completeness

The composition_standard component must define all 3 layers in its schema_sections:
- "Component Schema" (Layer 1)
- "Composition Format" (Layer 2)
- "Output Format" (Layer 3)

Omitting any layer is a validation failure.

### VR-014: Output Variance Feasibility

Each output_variance must have a valid and feasible combination of component_requirements. The declared component types must be sufficient to produce the declared output_files. For example, a variance that declares action step outputs must include step_definition in its component_requirements.

---

## Extensibility Model

### Adding New Component Types

New component types can be added to this schema without breaking existing compositions. The process is:

1. **Define the new type's specific properties** -- Create a property table following the same format as existing types (name, type, required/optional, description, example).
2. **Document the type in the component schema** -- Add a new section under "Component Types" following the established structure (Type Overview, Type-Specific Properties, Validation Rules, Example Component).
3. **Add the type to the component_type enum** -- Update VR-002 to include the new type value.
4. **Provide at least one example component** -- Demonstrate the new type with a complete, realistic example.
5. **Update composition_standard.component_types_defined** -- The composition_standard component should list the new type.

### Backward Compatibility Rules

- **Existing compositions continue to work** because they reference components by component_id, not by component_type. Adding a new type does not affect any existing component_id reference.
- **Common properties remain stable** -- The 5 required common properties (component_id, component_type, name, version, description) and 3 optional properties (duration_range, platforms, tags) do not change when new types are added.
- **Existing validation rules are unaffected** -- Global validation rules (VR-001 through VR-014) continue to apply. New types may introduce additional type-specific validation rules without modifying existing ones.
- **Forward compatibility** -- Compositions may reference component_ids that do not yet exist. These are flagged as gaps during resolution but do not cause validation failure.

### Versioning Rules

Component versions follow semantic versioning (MAJOR.MINOR.PATCH):

| Change Type | Version Bump | Example |
|---|---|---|
| Add a new optional property to a type | MINOR | 1.0.0 -> 1.1.0 |
| Add a new component type | MINOR | 1.0.0 -> 1.1.0 |
| Remove or rename a required property | MAJOR | 1.0.0 -> 2.0.0 |
| Change a property's type or semantics | MAJOR | 1.0.0 -> 2.0.0 |
| Fix documentation or examples | PATCH | 1.0.0 -> 1.0.1 |
| Add a new validation rule for existing type | MINOR | 1.0.0 -> 1.1.0 |
| Change a required property to optional | MINOR | 1.0.0 -> 1.1.0 |
| Change an optional property to required | MAJOR | 1.0.0 -> 2.0.0 |

### Schema Evolution Principles

- The common property set is governed by the Universal Component Schema (COMPOSITION_SYSTEM_STANDARD.md Section 3). Changes to common properties require a standard version increment.
- Type-specific properties are owned by the domain and can evolve independently per the versioning rules above.
- The extensibility_model field in the composition_standard component should be updated whenever the schema evolves to document the current extensibility mechanism.

---

## Component File Format

Components in the workflow_builder domain are not stored as individual files on disk. They are defined inline in the workflow composition (Layer 2) and materialized as workflow.toml sections, prompt files, and Python code during the output resolution phase (Layer 3).

However, when components are documented or exchanged in standalone form, they use the following format: Markdown with YAML frontmatter.

### File Structure

```
---
component_id: "{type}-{name}-{seq}"
component_type: "{type}"
name: "{Display Name}"
version: "{MAJOR.MINOR.PATCH}"
# Optional common properties
duration_range: "{range}"       # if applicable
platforms: [{platform1}]        # if applicable
tags: [{tag1}, {tag2}]          # if applicable
description: "{description}"

# Type-specific properties follow
{type_specific_property_1}: {value}
{type_specific_property_2}: {value}
---

# {Component Display Name}

Additional documentation, usage notes, examples...
```

### Complete Example Component File

```markdown
---
component_id: "step-generate-component-schema-001"
component_type: "step_definition"
name: "Generate Component Schema"
version: "1.0.0"
tags: [layer1, generation, schema]
description: "Generates the component schema document defining all 8 component types for Layer 1 of the composition system"
step_name: "generate_component_schema"
step_type: "prompt"
purpose: "Generate the component schema for Layer 1"
required_inputs:
  - "WORKFLOW_SPEC_FILE"
  - "TEST_CRITERIA_FILE"
produces:
  - "COMPONENT_SCHEMA_FILE"
enable_notifications: true
requires_human_approval_after: false
---

# Generate Component Schema

This step reads the workflow specification and test criteria to produce the component schema for Layer 1. It defines all 8 component types, their common and type-specific properties, validation rules, and example components.

## Usage Notes

- This step must be executed before any composition format or output format steps, as they depend on the component types defined here.
- The output is validated by the gatekeep_component_schema step.
```

---

## Self-Validation

This section verifies the completeness and correctness of the component schema defined above.

### Component Type Enumeration

The following 8 component types are defined in this schema:

| # | Component Type | Required | Cardinality | Status |
|---|---|---|---|---|
| 1 | step_definition | Yes | Ordered list | DEFINED |
| 2 | role_policy | Yes | Singleton per step | DEFINED |
| 3 | routing_pattern | Yes | Singleton per step | DEFINED |
| 4 | prompt_pattern | No | Unordered set per prompt-driven step | DEFINED |
| 5 | artifact_contract | Yes | Unordered set per workflow | DEFINED |
| 6 | composition_standard | Yes | Singleton | DEFINED |
| 7 | output_variance | No | Unordered set | DEFINED |
| 8 | domain_spec | No | Unordered set | DEFINED |

**Count verification:** 8 types defined. Matches spec requirement (TC-CS-001, TC-CS-003).

### Common Property Verification

All 8 component types share these 5 required common properties:

| Property | Present on All Types |
|---|---|
| component_id | Yes |
| component_type | Yes |
| name | Yes |
| version | Yes |
| description | Yes |

Plus 3 optional common properties inherited from the Universal Component Schema:

| Property | Optional on All Types |
|---|---|
| duration_range | Yes |
| platforms | Yes |
| tags | Yes |

**Verification:** All common properties documented (TC-CS-005, TC-CS-006).

### Type-Specific Property Verification

| Component Type | Type-Specific Properties Count | Has Example |
|---|---|---|
| step_definition | 7 properties | Yes |
| role_policy | 2 properties | Yes |
| routing_pattern | 5 properties + sub-structure | Yes |
| prompt_pattern | 2 properties | Yes |
| artifact_contract | 5 properties | Yes |
| composition_standard | 5 properties | Yes |
| output_variance | 4 properties | Yes |
| domain_spec | 4 properties | Yes |

**Verification:** All types have type-specific properties documented with name, type, required/optional, description, and example values (TC-CS-018, TC-CS-032, TC-CS-033).

### Validation Rule Verification

| Rule ID | Rule Description | Present |
|---|---|---|
| VR-001 | Required fields present | Yes |
| VR-002 | Valid component_type | Yes |
| VR-003 | Unique component_id | Yes |
| VR-004 | Type-specific schema conformance | Yes |
| VR-005 | Semantic version format | Yes |
| VR-006 | Step name uniqueness | Yes |
| VR-007 | Valid step_type | Yes |
| VR-008 | Valid policy_name | Yes |
| VR-009 | Artifact key format | Yes |
| VR-010 | Routing completeness | Yes |
| VR-011 | Prompt pattern completeness | Yes |
| VR-012 | Artifact flow integrity | Yes |
| VR-013 | Composition standard completeness | Yes |
| VR-014 | Output variance feasibility | Yes |

**Verification:** All validation rules from spec Section 2.5 are present (TC-CS-019 through TC-CS-028). VR-001 through VR-005 correspond to the global rules. VR-006 through VR-014 correspond to the domain-specific rules in spec Section 2.5.

### Spec Traceability

Every component type and property in this schema traces back to workflow_builder_v3.md Section 2 (Component Schema). No types were invented. No types were omitted. The schema is a faithful expansion of the spec's definitions into a complete, enforceable component schema document.

---

**End of Component Schema**
