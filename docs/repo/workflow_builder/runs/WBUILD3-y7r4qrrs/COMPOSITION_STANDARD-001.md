---
doc_type: "composition_standard"
lifecycle_status: "draft"
standard_name: "WORKFLOW_BUILDER_STANDARD"
standard_version: "1.0.0"
component_type_count: 8
schema_sections:
  - "Component Schema"
  - "Composition Format"
  - "Output Format"
domain: "workflow_builder"
spec_reference: "workflow_builder_v4.md"
generated_by: "generate_composition_standard"
component_types_defined:
  - "step_definition"
  - "role_policy"
  - "routing_pattern"
  - "prompt_pattern"
  - "artifact_contract"
  - "composition_standard"
  - "output_variance"
  - "domain_spec"
---

# Composition Standard -- WORKFLOW_BUILDER_STANDARD v1.0.0

## Overview

This document defines the composition standard for the
workflow_builder domain. It is the key v3 innovation: every generated
meta builder has its own composition standard that defines its
component types, composition format, and output format across the
3-layer architecture.

**Standard name:** WORKFLOW_BUILDER_STANDARD
**Standard version:** 1.0.0
**Domain:** workflow_builder
**Component type count:** 8
**Schema sections:** 3 (Component Schema, Composition Format, Output
Format)

This standard serves three roles:

1. **Self-description:** Each generated meta builder carries its own
   composition standard, making it self-describing. The builder's
   component types, binding rules, and output format are all defined
   within this single standard document.

2. **Dynamic discovery:** The discover_component_types() function in
   the generated context_extensions.py parses this standard at runtime
   to extract the list of component types dynamically, replacing
   hardcoded type lists in prompts.

3. **Bootstrap chain:** When embedded in the Standards/ directory of
   the generated workflow package, this standard becomes the input
   contract for subsequent workflow generations. The generated meta
   builder reads its own standard to determine what components it
   can compose.

**Layer architecture:**

```
Layer 1: Component Schema   -- Defines the 8 component types and
                               their properties (building blocks)
Layer 2: Composition Format  -- Defines how components are bound
                               into compositions (assembly rules)
Layer 3: Output Format       -- Defines how compositions become
                               concrete output files (materialization)
```

**Traceability:** All content in this document traces back to the
input specification (WORKFLOW_SPEC_FILE: workflow_builder_v4.md) and
the upstream phase outputs: COMPONENT_SCHEMA_FILE,
COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, and
OPERATIONAL_WORKFLOW_FILE.

---

## Component Schema

This section defines the Layer 1 component schema for the
workflow_builder domain. It specifies the 8 component types that
serve as the universal building blocks for all meta builders in this
domain. Each generated meta builder is composed of instances of these
8 types.

**Schema layer:** Layer 1 (Component Schema)
**Component type count:** 8
**Validation rules defined:** 16 (VR-001 through VR-016)

### Common Properties

All 8 component types share the following common properties. These
form the stable foundation of the Universal Component Schema.

#### Required Common Properties (5)

Every component instance must include all 5 of these properties.
A component missing any one of them fails validation (VR-001).

| Property | Type | Required | Description |
|---|---|---|---|
| component_id | string | Yes | Unique identifier for this component instance. Format: {type-prefix}-{name}-{seq}. Must be globally unique across all components within a single composition (VR-003). |
| component_type | enum | Yes | One of the 8 defined types: step_definition, role_policy, routing_pattern, prompt_pattern, artifact_contract, composition_standard, output_variance, domain_spec. Unknown types are rejected (VR-002). |
| name | string | Yes | Human-readable display name for this component. Used in documentation, traceability tables, and user interfaces. |
| version | string | Yes | Semantic version in MAJOR.MINOR.PATCH format (e.g., "1.0.0"). Each segment must be a non-negative integer (VR-005). |
| description | string | Yes | A detailed description of what this component does, its purpose within the workflow, and when it is applicable. Must be a non-empty string of at least 10 characters. |

#### Optional Common Properties (3)

These properties may be included on any component type. They are
not required but provide additional classification and filtering
metadata.

| Property | Type | Required | Description |
|---|---|---|---|
| duration_range | string | No | An applicable duration or scope constraint for this component. Example: "5-15 minutes" or "single phase". |
| platforms | array | No | Target platforms or runtime contexts where this component is applicable. Example: ["windows", "linux"]. |
| tags | array | No | Classification tags for search, filtering, and traceability. Example: ["generation", "validation", "qc"]. |

### Component Types

This section defines each of the 8 component types with their
purpose, required/optional flag, cardinality, type-specific
properties, validation rules, and a complete YAML example.

#### Type 1: step_definition

**Purpose:** Defines a single workflow step with its execution type,
purpose, required inputs, and produced outputs. Each step is an
atomic unit of work in the workflow pipeline. Steps are ordered and
their execution sequence is determined by their position in the
step_bindings array.

**Required:** Yes. Every workflow must define at least one
step_definition.

**Cardinality:** Ordered list (N steps per workflow).

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| step_name | string | Yes | Unique step identifier within the workflow. Must be lowercase with underscores. Must be unique across all steps (VR-006). |
| step_type | enum | Yes | The execution type of this step. Allowed values: "prompt" or "action" (VR-007). |
| purpose | string | Yes | What this step achieves. Must be a non-empty descriptive string. |
| required_inputs | array | No | Artifact keys this step reads as inputs. Each entry must reference an artifact produced by a preceding step or declared as a workflow-level input (VR-012, VR-015). |
| produces | array | Yes | Artifact keys this step writes as outputs. Must be non-empty for every step. Each key must use UPPER_SNAKE_CASE with _FILE suffix (VR-009). |
| enable_notifications | boolean | Yes | Whether to send notifications on step completion. Default: false. |
| requires_human_approval_after | boolean | Yes | Whether to pause workflow execution for human approval after this step completes. Default: false. |

**Validation Rules Applied:** VR-006, VR-007, VR-009, VR-012, VR-015.

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

#### Type 2: role_policy

**Purpose:** Defines a coder role assignment for a workflow step.
Each step must be bound to exactly one role_policy that determines
which coder backend and instruction set handles the step execution.

**Required:** Yes. Every step must have a role_policy.

**Cardinality:** Singleton per step (exactly one role_policy per
step_definition).

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| policy_name | enum | Yes | The role policy to assign. Must be one of: architect_standard, reviewer_standard, gatekeeper_standard, validation_standard, refine_standard (VR-008). |
| assignment_rule | string | Yes | A description of when and why this policy is assigned. Specifies the conditions under which this role is appropriate. |

**Validation Rules Applied:** VR-008.

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

#### Type 3: routing_pattern

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
| on_reject_refine | object | No | Refinement loop configuration. Required for review and gatekeep steps that support rejection. |
| max_iterations | integer | No | Maximum number of refine loop iterations. Required if on_reject_refine is defined. |
| exhausted_failure_code | string | No | Terminal failure code when max_iterations is exhausted. Required if on_reject_refine is defined. Format: UPPER_SNAKE_CASE. |
| exhausted_failure_class | string | No | Failure classification when refine iterations are exhausted. Required if on_reject_refine is defined. |

**Validation Rules Applied:** VR-010.

**Example:**

```yaml
- component_id: "routing-generate_component_schema-01"
  component_type: "routing_pattern"
  name: "Generate Component Schema Routing"
  version: "1.0.0"
  description: "Routes to gatekeep step on success"
  onsuccess: "gatekeep_component_schema"
```

#### Type 4: prompt_pattern

**Purpose:** Defines structural elements that are injected into prompt
templates. Each pattern adds a specific section to the prompt,
ensuring consistent quality checks, self-criticism, and output
structure across all prompt-driven steps.

**Required:** No. Only applicable to prompt-type steps.

**Cardinality:** Unordered set per prompt-driven step.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| pattern_name | enum | Yes | The pattern to inject. Must be one of: self_critic, self_validation, context_verification, reference_inputs, generation_tasks, forbidden_content, output_instructions. |
| sections | array | Yes | List of prompt section descriptions that this pattern contributes to the prompt template. |

**Validation Rules Applied:** VR-011 (every prompt-type step must
include self_critic and self_validation patterns).

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

#### Type 5: artifact_contract

**Purpose:** Defines an input or output artifact that flows through
the workflow. Artifacts are named files produced and consumed by
steps. Each artifact_contract specifies the key, format, and
ownership of a single artifact.

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

**Validation Rules Applied:** VR-009.

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

#### Type 6: composition_standard

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
| component_types_defined | array | Yes | List of component type names defined in this standard. Must match the actual type definitions. |
| schema_sections | array | Yes | Must contain exactly 3 entries: "Component Schema", "Composition Format", "Output Format" (VR-013). |
| extensibility_model | string | Yes | Description of how new component types can be added without breaking existing compositions. |

**Validation Rules Applied:** VR-013.

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
  extensibility_model: >
    New component types can be added to the standard without breaking
    existing compositions. Existing compositions reference components
    by component_id, not by type enumeration.
```

#### Type 7: output_variance

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
| variance_name | string | Yes | Name identifying this output variance. Must be unique within the workflow. |
| variance_description | string | Yes | What this variance produces and how it differs from other variances. |
| component_requirements | array | Yes | Which component types are required for this variance. Each entry must be a valid component_type from the 8 base types (VR-014). |
| output_files | array | Yes | Files produced when this variance is selected. Must be non-empty. |

**Validation Rules Applied:** VR-014.

**Example:**

```yaml
- component_id: "variance-prompt_only_workflow-01"
  component_type: "output_variance"
  name: "Prompt Only Workflow"
  version: "1.0.0"
  description: "A workflow with only prompt-driven steps and no API action steps beyond validation"
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

#### Type 8: domain_spec

**Purpose:** Defines a type of user-provided specification the meta
builder can process. This allows the builder to validate incoming
specs against expected structure and version compatibility before
processing.

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

**Validation Rules Applied:** Common rules only. Type-specific
validation is deferred to the composition format layer (Layer 2).

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

### Validation Rules (Global)

The following 16 validation rules apply to all component instances
across all 8 component types.

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
| VR-015 | Every step that references the WORKFLOW_SPEC_FILE artifact key in its prompt template must declare WORKFLOW_SPEC_FILE in its required_inputs array. Bidirectional check required. | CRITICAL |
| VR-016 | Both generate_package and refine_package steps must declare STANDARDS_COMPOSITION_STANDARD_FILE in their produces lists in workflow.toml. If either step omits this declaration, validation fails. | CRITICAL |

---

## Composition Format

This section defines the Layer 2 composition format for the
workflow_builder domain. It specifies how the 8 component types from
Layer 1 are bound into compositions, how placeholders are resolved,
and how overrides are applied at composition time.

**Schema layer:** Layer 2 (Composition Format)
**Binding rules defined:** 9 (8 base + 1 self_bootstrap)
**Workflow patterns defined:** 6
**Ordering rules defined:** 8 (O-001 through O-008)
**Placeholder data sources:** 4 (Input Spec, Governance, Runtime,
Discovery)

### Composition Structure

Every composition for the workflow_builder domain is a YAML document
with the following top-level fields:

| Field | Type | Required | Description |
|---|---|---|---|
| builder_name | string | Yes | Unique builder identifier. Must be lowercase_with_underscores. |
| builder_label | string | Yes | Human-readable display name for the builder. |
| job_prefix | string | Yes | 4-6 character uppercase prefix for job IDs. |
| builder_purpose | string | Yes | A detailed description of what problem this builder solves. |
| workflow_pattern | enum | Yes | One of the 6 defined workflow patterns. |
| step_bindings | array | Yes | Ordered array of step_definition component instances. |
| artifact_bindings | object | Yes | Input and output artifact contracts for the composition. |
| composition_standard_binding | object | Yes | References the composition_standard component. |
| self_bootstrap_binding | object | Yes | Defines how the builder references its own spec for self-bootstrapping. |
| output_variances | array | No | Array of output_variance component instances. |
| domain_specs | array | No | Array of domain_spec component instances. |

### Binding Rules

The following 9 binding rules connect the 8 component types from
Layer 1 to the composition structure fields.

| # | Binding Name | Component Type | Cardinality | Required |
|---|---|---|---|---|
| 1 | steps | step_definition | Ordered list | Yes |
| 2 | roles | role_policy | Singleton per step | Yes |
| 3 | routing | routing_pattern | Singleton per step | Yes |
| 4 | prompts | prompt_pattern | Unordered set per prompt step | No |
| 5 | artifacts | artifact_contract | Unordered set | Yes |
| 6 | standard | composition_standard | Singleton | Yes |
| 7 | variances | output_variance | Unordered set | No |
| 8 | domain_specs | domain_spec | Unordered set | No |
| 9 | self_bootstrap | domain_spec | Singleton | Yes |

**Binding Rule 1 (steps):** Binds step_definition components to the
step_bindings array. Array order determines execution sequence.

**Binding Rule 2 (roles):** Binds exactly one role_policy to each
step_definition. The policy_name must be one of 5 valid values
(VR-008).

**Binding Rule 3 (routing):** Binds exactly one routing_pattern to
each step_definition. The onsuccess field must reference a valid
step_name (VR-010).

**Binding Rule 4 (prompts):** Binds prompt_pattern components to
prompt-type steps only. Every prompt-type step must include at
minimum self_critic and self_validation patterns (VR-011).

**Binding Rule 5 (artifacts):** Binds artifact_contract components
to the artifact_bindings object. Every artifact_key must be
UPPER_SNAKE_CASE with _FILE suffix (VR-009).

**Binding Rule 6 (standard):** Binds exactly one composition_standard
component. The schema_sections must contain exactly 3 entries
(VR-013).

**Binding Rule 7 (variances):** Binds output_variance components.
Each variance's component_requirements must reference only valid
component types (VR-014).

**Binding Rule 8 (domain_specs):** Binds domain_spec components.
Each spec_type must be unique within the composition.

**Binding Rule 9 (self_bootstrap):** Binds a specialized
domain_spec configuration to the self_bootstrap_binding field.
The bootstrap_spec_key must always be "WORKFLOW_SPEC_FILE".
The bootstrap_spec_target must follow "Specs/{builder_name}.md".

### Self-Bootstrap Binding

The self_bootstrap_binding defines how the builder references its
own spec for self-bootstrapping:

| Field | Type | Required | Description |
|---|---|---|---|
| bootstrap_spec_key | string | Yes | Artifact key that holds the builder's own spec (always "WORKFLOW_SPEC_FILE"). |
| bootstrap_spec_target | string | Yes | Where to embed in output (always "Specs/{builder_name}.md"). |
| bootstrap_version | string | Yes | Current builder version (e.g., "4.0.0"). |
| next_version_pattern | string | Yes | How to derive next version (e.g., "increment_major"). |

### Workflow Patterns

The following 6 workflow patterns are available:

| # | Pattern | Type | Description |
|---|---|---|---|
| 1 | action_only | Deterministic | All Python operations, no LLM |
| 2 | prompt_driven | LLM | All prompt steps with review loops |
| 3 | mixed | Hybrid | Combination of prompt and action |
| 4 | gatekeeper_pipeline | Multi-phase | Phase boundaries with quality gates |
| 5 | meta_workflow_builder | Meta | Builds concrete workflows |
| 6 | meta_meta_builder | Meta-meta | Builds meta builders with self-bootstrap |

**meta_meta_builder pattern** (used by this domain): Foundation
(TDD) -> Component Schema (Layer 1) -> Composition Format (Layer 2)
-> Output Format (Layer 3) -> Operational Workflow -> Composition
Standard -> Meta Composition Spec -> Package Assembly (generate,
embed_spec, validate, gatekeep, review, refine) -> Promotion.
Typical step count: 20-24 steps.

### Override Mechanism

The override mechanism allows per-composition customization of
component properties without modifying the original component
definitions from Layer 1.

**Merge semantics:**
1. Override wins on conflict: If the override specifies a value
   for a property that exists in the base component, the override
   value takes precedence.
2. Base fills gaps: Properties not specified in the override retain
   their base component values.
3. Additive for arrays: For array properties, the override array
   replaces the base array entirely (no element merging).
4. Deep merge for objects: For object properties, the override is
   deep-merged with the base.

**Non-overridable properties (5):** component_id, component_type,
name, version, description. These are fixed by the component
definition in Layer 1.

**Overridable properties:** All 3 optional common properties
(duration_range, platforms, tags) and all type-specific properties
defined for each component type.

**Schema conformance:** All override values must conform to the same
schema as the base component properties. An override cannot introduce
properties that are not defined for the declared component_type.

### Placeholder Resolution

The placeholder resolution mechanism specifies how {PLACEHOLDER}
tokens in templates are resolved at composition time. There are 4
data sources applied in priority order:

| Priority | Data Source | Fields Provided |
|---|---|---|
| 1 (highest) | Input Spec | WORKFLOW_SPEC_FILE, domain_name, job_prefix, builder_name |
| 2 | Governance | BASE_COMPOSITION_STANDARD, GOVERNANCE_RUNTIME_ROOT |
| 3 | Runtime | job_id, seq, workspace_root, output_dir |
| 4 (lowest) | Discovery | DISCOVERED_COMPONENT_TYPES, COMPOSITION_STANDARD_PATH |

**Discovery data source:** The DISCOVERED_COMPONENT_TYPES field is
computed at runtime after the generate_composition_standard step
completes. The discover_component_types() function parses the
generated composition standard to extract the component type list
dynamically. This enables the generated workflow to use the actual
component types from the standard rather than hardcoded values.

**Unresolved handling:** If a placeholder cannot be resolved from
any data source, it is replaced with:
{UNRESOLVED: placeholder_name}

### Ordering Rules

The following 8 ordering rules constrain the step sequence:

| Rule | Name | Description |
|---|---|---|
| O-001 | Foundation First | Phase 1 steps must appear first. |
| O-002 | Layer Sequence | Layer 1 before Layer 2 before Layer 3. |
| O-003 | Gatekeep After Generate | Every gatekeep step must immediately follow its generate step. |
| O-004 | Terminal Last | step_completion must be the last entry. |
| O-005 | Refine Steps Conditional | Refine steps execute only on rejection. |
| O-006 | Embed Spec Before Validate | embed_builder_spec must execute after generate_package but before validate_package_deterministic. |
| O-007 | Operational Workflow After Layers | Phase 5 must execute after all three layers are complete. |
| O-008 | Composition Standard Before Package | Phases 6 and 7 must execute before Phase 8. |

---

## Output Format

This section defines the Layer 3 output format for the
workflow_builder domain. It specifies how compositions materialize
into concrete output files, the resolution rules that map each
component type to its output target, and the quality requirements
that validate the output.

**Schema layer:** Layer 3 (Output Format)
**Output parts:** 3 (Standards, Specs, Workflow Package)
**Resolution rules defined:** 7 (RR-001 through RR-007)
**Quality requirements defined:** 8 (QR-001 through QR-008)

### Output Structure

The Layer 3 output is a 3-part directory structure:

```
{builder_name}/
|-- Standards/
|   +-- COMPOSITION_STANDARD.md     # Part 1: Composition standard
|-- Specs/
|   +-- {builder_name}.md           # Part 2: Builder's own spec
|-- workflow.toml                    # Part 3: Workflow manifest
|-- context_extensions.py            # Part 3: Artifact path resolution
|-- actions.py                       # Part 3: Action implementations
|-- prompts/                         # Part 3: Prompt templates
|   +-- NN_{step_name}.txt
|-- README.md                        # Part 3: Human documentation
|-- .env.sample                      # Part 3: Conditional
+-- config.json.sample               # Part 3: Conditional
```

**Part 1: Standards Directory**
Contains Standards/COMPOSITION_STANDARD.md -- the composition
standard defining all component types, validation rules, and
extensibility model for the generated meta builder. Mandatory.

**Part 2: Specs Directory**
Contains Specs/{builder_name}.md -- a content-identical copy of the
input WORKFLOW_SPEC_FILE enabling self-bootstrapping. Mandatory.

**Part 3: Workflow Package**
Contains workflow.toml (manifest), context_extensions.py (path
resolution), actions.py (action implementations, conditional),
prompts/NN_{step_name}.txt (prompt templates), README.md
(documentation), .env.sample (conditional), config.json.sample
(conditional).

### Resolution Rules

The following 7 resolution rules define how each component type is
materialized into output files:

| Rule ID | Source | Target | Mandatory |
|---|---|---|---|
| RR-001 | step_definition instances | workflow.toml [[step]] sections | Yes |
| RR-002 | role_policy per step | workflow.toml coder_role field | Yes |
| RR-003 | routing_pattern per step | workflow.toml onsuccess/on_reject_refine | Yes |
| RR-004 | prompt_pattern per prompt step | prompts/NN_{step_name}.txt files | Yes (prompt steps) |
| RR-005 | artifact_contract instances | context_extensions.py register_artifact_keys() | Yes |
| RR-006 | composition_standard binding | Standards/COMPOSITION_STANDARD.md | Yes |
| RR-007 | 4 placeholder data sources | All template files and output paths | Yes |

**RR-001:** Each step_definition is materialized as a [[step]] section
in workflow.toml with step_name, step_type, purpose, required_inputs,
produces, enable_notifications, requires_human_approval_after.

**RR-002:** Each step's role_policy policy_name becomes the coder_role
field in the corresponding [[step]] section.

**RR-003:** Each step's routing_pattern onsuccess and on_reject_refine
values become the routing fields in the [[step]] section.

**RR-004:** Each prompt-type step's prompt_pattern sections are
materialized as content in prompts/NN_{step_name}.txt files.

**RR-005:** Each artifact_contract is materialized as a registration
entry in the register_artifact_keys() function of
context_extensions.py.

**RR-006:** The composition_standard binding is materialized as
Standards/COMPOSITION_STANDARD.md with YAML frontmatter containing
standard_name, standard_version, component_type_count, and
schema_sections.

**RR-007:** All {PLACEHOLDER} tokens are resolved using the 4 data
sources in priority order: Input Spec, Governance, Runtime, Discovery.

### Quality Requirements

The following 8 quality requirements validate the Layer 3 output:

| Rule ID | Requirement | Severity |
|---|---|---|
| QR-001 | TOML parse validity of workflow.toml. File must parse without errors. | CRITICAL |
| QR-002 | Python syntax validity of context_extensions.py and actions.py. Both must compile without syntax errors. | CRITICAL |
| QR-003 | No TYPE_CHECKING runtime import guards in Python files. | HIGH |
| QR-004 | Artifact binding consistency. Every required_inputs entry references a prior-produced artifact or workflow input. Every produces key is unique. | CRITICAL |
| QR-005 | Action step implementation completeness. Every action-type step in workflow.toml has a matching function in actions.py. | CRITICAL |
| QR-006 | Prompt file existence. Every prompt-type step has a corresponding prompts/NN_{step_name}.txt file. | CRITICAL |
| QR-007 | Prompt placeholder vs required_inputs consistency. Every {PLACEHOLDER} in prompts is declared in the step's required_inputs or produces. | CRITICAL |
| QR-008 | context_extensions.py artifact key coverage. Every artifact key in workflow.toml has a path entry in register_artifact_keys(). | CRITICAL |

### Promotion Contract

The promote_workflow_package action must copy all 3 parts:

| Source | Target | Mandatory |
|---|---|---|
| output/workflow.toml | workflows/{slug}/workflow.toml | Yes |
| output/context_extensions.py | workflows/{slug}/context_extensions.py | Yes |
| output/actions.py | workflows/{slug}/actions.py | If exists |
| output/README.md | workflows/{slug}/README.md | Yes |
| output/prompts/ | workflows/{slug}/prompts/ | Yes |
| output/Standards/ | workflows/{slug}/Standards/ | Yes (enforced) |
| output/Specs/ | workflows/{slug}/Specs/ | Yes (enforced) |
| output/.env.sample | workflows/{slug}/.env.sample | If exists |
| output/config.json.sample | workflows/{slug}/config.json.sample | If exists |

If Standards/ or Specs/ is missing from the output, the promote
action REJECTS with a clear error message.

### Downstream Extraction Contracts

| Contract ID | Target | Consumer | Format |
|---|---|---|---|
| DEC-001 | workflow.toml | Runner engine, step_runner | TOML |
| DEC-002 | prompts/ directory | step_runner, coder_adapters | Plain text with {PLACEHOLDER} tokens |
| DEC-003 | Standards/COMPOSITION_STANDARD.md | context_extensions.py, downstream meta builders | Markdown with YAML frontmatter |

---

## Extensibility Model

New component types can be added to this standard without breaking
existing compositions. The extensibility model follows these
principles:

1. **Identity stability:** Existing compositions reference components
   by component_id, not by type enumeration. Adding new types does
   not affect existing component references.

2. **Common property stability:** The 5 required common properties
   (component_id, component_type, name, version, description) and
   3 optional common properties (duration_range, platforms, tags)
   remain stable across all types. New types inherit these without
   modification.

3. **Additive extension:** New types are added by defining their
   type-specific properties in the Component Types section. Existing
   types are not modified or removed.

4. **Validation rule isolation:** New types may introduce additional
   type-specific validation rules. These rules are scoped to the new
   type and do not modify existing global rules (VR-001 through
   VR-016). New rules are appended with incrementing identifiers
   (VR-017, VR-018, etc.).

5. **Discovery compatibility:** The dynamic discovery mechanism
   (discover_component_types) automatically picks up new types from
   the generated composition standard by scanning for "#### Type N:"
   headings. No code changes are needed for discovery.

6. **Backward compatibility:** Compositions created before a new type
   is added continue to function without modification. They simply
   do not use the new type.

**Procedure for adding a new component type:**

1. Define the new type name in the Component Types section with
   heading format "#### Type N: type_name".
2. Specify its required and optional type-specific properties.
3. Add any type-specific validation rules (appending to the global
   rule sequence).
4. Update component_type_count in the YAML frontmatter.
5. Provide at least one example component with all required
   properties.
6. Update the component_types_defined array in the frontmatter.

---

## Self-Validation

This section verifies the completeness and internal consistency of
the composition standard document itself.

### Component Type Completeness

| Number | Component Type | Defined | Has Properties | Has Validation Rules | Has Example |
|---|---|---|---|---|---|
| 1 | step_definition | YES | YES (7 type-specific) | YES (VR-006, VR-007, VR-009, VR-012, VR-015) | YES |
| 2 | role_policy | YES | YES (2 type-specific) | YES (VR-008) | YES |
| 3 | routing_pattern | YES | YES (5 type-specific) | YES (VR-010) | YES |
| 4 | prompt_pattern | YES | YES (2 type-specific) | YES (VR-011) | YES |
| 5 | artifact_contract | YES | YES (5 type-specific) | YES (VR-009) | YES |
| 6 | composition_standard | YES | YES (5 type-specific) | YES (VR-013) | YES |
| 7 | output_variance | YES | YES (4 type-specific) | YES (VR-014) | YES |
| 8 | domain_spec | YES | YES (4 type-specific) | YES (common rules only) | YES |

**Verification:** All 8 component types are defined with properties,
validation rules, and at least one complete example.

### Schema Sections Completeness

| Section | Layer | Defined | Content |
|---|---|---|---|
| Component Schema | Layer 1 | YES | 8 types, 5+3 common properties, 16 validation rules |
| Composition Format | Layer 2 | YES | 9 binding rules, 6 patterns, override mechanism, 4 data sources, 8 ordering rules |
| Output Format | Layer 3 | YES | 3-part structure, 7 resolution rules, 8 quality requirements, promotion contract |

**Verification:** All 3 schema sections are defined. VR-013
satisfied.

### Layer Boundary Compliance

| Check | Status | Evidence |
|---|---|---|
| Layer 1 does not redefine governance content | PASS | Component types and validation rules derived from WORKFLOW_SPEC_FILE Section 2 |
| Layer 2 does not redefine Layer 1 | PASS | Binding rules reference Layer 1 types without modification |
| Layer 3 does not redefine Layer 1 or Layer 2 | PASS | Resolution rules consume Layer 1 types and Layer 2 bindings |
| ASCII-only content | PASS | No em-dashes, curly quotes, or Unicode characters used |
| No resolved filesystem paths in governance references | PASS | Uses filenames only (COMPONENT_SCHEMA.md, COMPOSITION_FORMAT.md) |

### Frontmatter Completeness

| Field | Expected | Actual | Status |
|---|---|---|---|
| doc_type | "composition_standard" | "composition_standard" | PASS |
| lifecycle_status | "draft" | "draft" | PASS |
| standard_name | from spec | "WORKFLOW_BUILDER_STANDARD" | PASS |
| standard_version | from spec | "1.0.0" | PASS |
| component_type_count | 8 | 8 | PASS |
| schema_sections | 3 entries | ["Component Schema", "Composition Format", "Output Format"] | PASS |
| component_types_defined | 8 types | 8 types listed | PASS |
| domain | "workflow_builder" | "workflow_builder" | PASS |

### Criteria Traceability

| Criteria | Status | Evidence |
|---|---|---|
| TC-071 | PASS | YAML frontmatter with standard_name, standard_version, component_type_count, and body with component type definitions in "#### Type N:" format |
| TC-072 | PASS | standard_name = "WORKFLOW_BUILDER_STANDARD" in frontmatter |
| TC-073 | PASS | standard_version = "1.0.0" in frontmatter (semantic version) |
| TC-074 | PASS | All 8 component types defined with "#### Type N: type_name" headings |
| TC-075 | PASS | schema_sections field in frontmatter lists exactly 3 sections |
| TC-076 | PASS | Extensibility Model section describes how new types can be added |

### Validation Rules Completeness

| Rule ID | Defined | Severity | Scope |
|---|---|---|---|
| VR-001 | YES | CRITICAL | Common properties presence |
| VR-002 | YES | CRITICAL | Valid component_type enumeration |
| VR-003 | YES | CRITICAL | Unique component_id |
| VR-004 | YES | HIGH | Type-specific schema conformance |
| VR-005 | YES | MEDIUM | Semantic version format |
| VR-006 | YES | CRITICAL | Unique step_name |
| VR-007 | YES | CRITICAL | Valid step_type |
| VR-008 | YES | CRITICAL | Valid policy_name |
| VR-009 | YES | HIGH | Artifact key format |
| VR-010 | YES | CRITICAL | Routing completeness |
| VR-011 | YES | HIGH | Prompt pattern completeness |
| VR-012 | YES | CRITICAL | Artifact flow integrity |
| VR-013 | YES | CRITICAL | Composition standard 3 layers |
| VR-014 | YES | HIGH | Output variance feasibility |
| VR-015 | YES | CRITICAL | WORKFLOW_SPEC_FILE bidirectional consistency |
| VR-016 | YES | CRITICAL | STANDARDS_COMPOSITION_STANDARD_FILE declaration |

**Verification:** 16 validation rules defined (VR-001 through
VR-016).

---

End of Composition Standard Document
