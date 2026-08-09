---
doc_type: "meta_composition_spec"
lifecycle_status: "draft"
domain: "workflow_builder"
self_bootstrap_capable: true
section_count: 5
component_type_count: 8
binding_rule_count: 9
resolution_rule_count: 9
quality_requirement_count: 12
phase_count: 9
step_count: 21
spec_reference: "workflow_builder_v4.md"
generated_by: "generate_meta_composition_spec"
---

# Meta Composition Spec: Workflow Builder v3

## Overview

This document is the meta composition specification for the Workflow
Builder v3 domain. It consolidates all three layers of the composition
architecture (Component Schema, Composition Format, Output Format) and
the operational workflow design into a single self-contained document.

This specification is designed to be processable by the generated meta
builder without requiring any other artifacts. A downstream workflow
can use this single document as input to generate a complete,
executable workflow package including its own composition standard,
builder specification, and workflow files.

**Domain:** workflow_builder
**Builder name:** workflow_builder_v3
**Builder label:** Workflow Builder v3
**Job prefix:** WBUILD3
**Workflow pattern:** meta_meta_builder
**Standard name:** WORKFLOW_BUILDER_STANDARD
**Standard version:** 1.0.0

This specification satisfies test criteria TC-051 (5 required sections)
and TC-052 (self-bootstrapping capability description).

---

## Section 1: Domain Overview

### 1.1 Target Domain Description

**Domain name:** workflow_builder
**Label:** Workflow Builder v3
**Job prefix:** WBUILD3

The workflow_builder domain is a meta-meta composition system. It
generates meta builders -- agents that are themselves capable of
generating executable workflow packages from specification inputs. Each
generated meta builder includes a composition standard, a builder
specification for self-bootstrapping, and a complete workflow package.

### 1.2 Builder Purpose

Workflow Builder v3 is a self-bootstrapping meta-meta builder that
generates meta builders with complete 3-part output:

1. Standards/COMPOSITION_STANDARD.md -- The composition standard for
   the generated meta builder
2. Specs/{builder_name}.md -- The builder's own spec (enables
   self-bootstrapping)
3. Workflow package -- workflow.toml, prompts/, actions.py,
   context_extensions.py, README.md

The builder addresses the need for reproducible, self-describing
workflow generation systems. Each generated meta builder knows its own
component types and structure, and can process its own specification to
produce the next version.

### 1.3 Workflow Pattern Type

**Pattern:** meta_meta_builder
**Pattern index:** 6 of 6 defined patterns

The meta_meta_builder pattern is the most complex of the 6 defined
workflow patterns. It requires:

- 9 phases (Foundation, Component Schema, Composition Format, Output
  Format, Operational Workflow, Composition Standard, Meta Composition
  Spec, Package Assembly, Promotion)
- 21 steps across the 9 phases (18 prompt, 3 action)
- 3-part output: Standards/, Specs/, workflow package
- Self-bootstrap binding required
- Dynamic component discovery from generated standard

### 1.4 Multi-Level Architecture

```
Level 0: v3 builder (creates meta builders, self-bootstrapping)
Level 1: Agent Workflow Spec (composition standard per agent)
Level 2: User Workflows (composition specs per use case)
Level 3: Agent execution outputs (deliverables)
```

### 1.5 Trigger and Outcome

**Trigger:** User provides a composition system spec describing a meta
builder as the WORKFLOW_SPEC_FILE input artifact.

**Outcome:** Three outputs, all promoted correctly:
1. Standards/COMPOSITION_STANDARD.md -- Composition standard
2. Specs/{builder_name}.md -- Builder's own spec (copy of
   WORKFLOW_SPEC_FILE)
3. Workflow package -- Executable workflow with all files

---

## Section 2: Component Schema

This section defines Layer 1 of the three-layer architecture. Layer 1
is the Universal Component Schema for the workflow_builder domain. It
provides the foundational building block library from which all meta
builder compositions are constructed.

### 2.1 Common Properties

All 8 component types share the following common properties regardless
of their component_type value.

#### Required Common Properties (5)

Every component instance must include all 5 of these properties.

| Property | Type | Required | Description |
|---|---|---|---|
| component_id | string | Yes | Unique identifier. Format: {type}-{name}-{seq}. Must be unique across all components in a composition. |
| component_type | enum | Yes | One of the 8 defined types. |
| name | string | Yes | Human-readable display name. |
| version | string | Yes | Semantic version in MAJOR.MINOR.PATCH format. |
| description | string | Yes | Detailed description of the component purpose. Must be non-empty. |

#### Optional Common Properties (3)

These may be included on any component type for additional metadata.

| Property | Type | Required | Description |
|---|---|---|---|
| duration_range | string | No | Applicable duration or scope constraint. |
| platforms | array | No | Target platforms (e.g., ["windows", "linux"]). |
| tags | array | No | Classification tags for filtering. |

### 2.2 Component Types

The following 8 component types are defined in this standard.

#### Type 1: step_definition

**Purpose:** Defines a workflow step with its type, purpose, inputs,
and outputs. Each step is a unit of work in the workflow pipeline.

**Required:** Yes. Every workflow must have at least one
step_definition.

**Cardinality:** Ordered list (N steps per workflow).

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| step_name | string | Yes | Unique step identifier. Lowercase with underscores. |
| step_type | enum | Yes | Execution type: prompt or action (VR-007). |
| purpose | string | Yes | What this step achieves. Non-empty descriptive string. |
| required_inputs | array | No | Artifact keys this step reads as inputs. |
| produces | array | Yes | Artifact keys this step writes as outputs. UPPER_SNAKE_CASE with _FILE suffix (VR-009). |
| enable_notifications | boolean | Yes | Whether to send notifications on completion. Default: false. |
| requires_human_approval_after | boolean | Yes | Whether to pause for human approval. Default: false. |

**Validation Rules:** VR-006 (unique step_name), VR-007 (valid
step_type), VR-009 (artifact key format), VR-012 (input artifact
flow), VR-015 (WORKFLOW_SPEC_FILE prompt-input consistency).

**Example:**

```yaml
- component_id: "step-generate_component_schema-01"
  component_type: "step_definition"
  name: "Generate Component Schema"
  version: "1.0.0"
  description: "Generate the component schema for Layer 1"
  step_name: "generate_component_schema"
  step_type: "prompt"
  purpose: "Generate the component schema for Layer 1"
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
which coder handles the step.

**Required:** Yes. Every step must have a role_policy.

**Cardinality:** Singleton per step.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| policy_name | enum | Yes | One of: architect_standard, reviewer_standard, gatekeeper_standard, validation_standard, refine_standard (VR-008). |
| assignment_rule | string | Yes | When and why this policy is assigned. |

**Validation Rules:** VR-008 (valid policy_name).

**Example:**

```yaml
- component_id: "role-architect_standard-01"
  component_type: "role_policy"
  name: "Architect Standard"
  version: "1.0.0"
  description: "Standard role for generation steps"
  policy_name: "architect_standard"
  assignment_rule: "Generation steps that create documents"
```

#### Type 3: routing_pattern

**Purpose:** Defines how steps connect to each other. Controls
execution flow including success paths and reject-refine loops.

**Required:** Yes. Every step must have a routing_pattern.

**Cardinality:** Singleton per step.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| onsuccess | string | Yes | Next step name on success (VR-010). |
| on_reject_refine | object | No | Refinement loop configuration. |
| max_iterations | integer | No | Maximum refine iterations (required if on_reject_refine defined). |
| exhausted_failure_code | string | No | Terminal failure code when iterations exhausted. |
| exhausted_failure_class | string | No | Failure classification (e.g., HUMAN_RETRY_REQUIRED). |

**Validation Rules:** VR-010 (valid onsuccess target).

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

**Purpose:** Defines structural elements injected into prompt
templates. Each pattern adds a specific section to the prompt,
ensuring consistent quality checks across all prompt-driven steps.

**Required:** No. Only applicable to prompt-type steps.

**Cardinality:** Unordered set per prompt-driven step.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| pattern_name | enum | Yes | One of: self_critic, self_validation, context_verification, reference_inputs, generation_tasks, forbidden_content, output_instructions. |
| sections | array | Yes | Prompt section descriptions this pattern contributes. |

**Validation Rules:** VR-011 (every prompt step must include
self_critic and self_validation).

**Example:**

```yaml
- component_id: "prompt-self_critic-01"
  component_type: "prompt_pattern"
  name: "Self Critic Pattern"
  version: "1.0.0"
  description: "Challenges the coder to question its reasoning"
  pattern_name: "self_critic"
  sections:
    - "Challenge your reasoning"
    - "Did you read the spec for each property"
```

#### Type 5: artifact_contract

**Purpose:** Defines an input or output artifact that flows through
the workflow. Artifacts are named files produced and consumed by
steps.

**Required:** Yes. Every workflow must define its artifact contracts.

**Cardinality:** Unordered set per workflow.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| artifact_key | string | Yes | Unique artifact identifier. UPPER_SNAKE_CASE with _FILE suffix (VR-009). |
| description | string | Yes | What this artifact contains and its purpose. |
| filename_pattern | string | No | Filename pattern with placeholders. |
| required | boolean | Yes | Whether this artifact is required. |
| produced_by | string | No | Step name that produces this artifact. |

**Validation Rules:** VR-009 (artifact key format).

**Example:**

```yaml
- component_id: "artifact-COMPONENT_SCHEMA_FILE-01"
  component_type: "artifact_contract"
  name: "Component Schema File"
  version: "1.0.0"
  description: "Component schema defining all 8 component types"
  artifact_key: "COMPONENT_SCHEMA_FILE"
  filename_pattern: "COMPONENT_SCHEMA-{seq}.md"
  required: true
  produced_by: "generate_component_schema"
```

#### Type 6: composition_standard

**Purpose:** Defines the composition standard schema for the
generated meta builder. This is the self-describing element that
makes each generated meta builder aware of its own component types.

**Required:** Yes. Every meta builder must define exactly one
composition_standard.

**Cardinality:** Singleton per workflow.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| standard_name | string | Yes | Name of the standard (e.g., "WORKFLOW_BUILDER_STANDARD"). |
| standard_version | string | Yes | Version in MAJOR.MINOR.PATCH format. |
| component_types_defined | array | Yes | List of component type names defined. |
| schema_sections | array | Yes | Must contain exactly 3 entries: "Component Schema", "Composition Format", "Output Format" (VR-013). |
| extensibility_model | string | Yes | Description of how new types can be added. |

**Validation Rules:** VR-013 (must define all 3 schema layers).

**Example:**

```yaml
- component_id: "standard-workflow_builder-01"
  component_type: "composition_standard"
  name: "Workflow Builder Standard"
  version: "1.0.0"
  description: "The composition standard for the workflow_builder domain"
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
  extensibility_model: "New component types can be added without breaking existing compositions"
```

#### Type 7: output_variance

**Purpose:** Defines a specific output configuration the meta
builder can produce. Output variances allow the same workflow to
generate different types of deliverables based on the input spec.

**Required:** No. Only used when the meta builder supports multiple
output configurations.

**Cardinality:** Unordered set per workflow.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| variance_name | string | Yes | Name identifying this output variance. |
| variance_description | string | Yes | What this variance produces. |
| component_requirements | array | Yes | Which component types are required (VR-014). |
| output_files | array | Yes | Files produced. Must be non-empty. |

**Validation Rules:** VR-014 (feasible component_requirements).

**Example:**

```yaml
- component_id: "variance-prompt_only_workflow-01"
  component_type: "output_variance"
  name: "Prompt Only Workflow"
  version: "1.0.0"
  description: "A workflow with only prompt-driven steps"
  variance_name: "prompt_only_workflow"
  variance_description: "All steps are LLM-driven"
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
builder can process. Allows validation of incoming specs against
expected structure and version compatibility.

**Required:** No. Only used when the meta builder accepts external
specifications as input.

**Cardinality:** Unordered set per workflow.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| spec_type | string | Yes | Type identifier for this specification. |
| spec_version_range | string | Yes | Compatible version range. |
| required_sections | array | Yes | Sections the specification must contain. |
| example_specs | array | No | Example specification filenames. |

**Validation Rules:** None beyond common property rules.

**Example:**

```yaml
- component_id: "spec-composition_system_spec-01"
  component_type: "domain_spec"
  name: "Composition System Specification"
  version: "1.0.0"
  description: "A composition system spec the workflow builder processes"
  spec_type: "composition_system_spec"
  spec_version_range: "1.0.0 - 4.99.99"
  required_sections:
    - "Domain Overview"
    - "Component Schema"
    - "Component Schema"
    - "Composition Format"
    - "Output Format"
    - "Operational Requirements"
  example_specs:
    - "workflow_builder_v3.md"
    - "workflow_builder_v4.md"
```

### 2.3 Validation Rules (Global)

The following 16 validation rules apply to all component instances
across all 8 component types.

| Rule ID | Rule | Severity |
|---|---|---|
| VR-001 | Every component must have all 5 required common properties. | CRITICAL |
| VR-002 | component_type must be one of the 8 defined types. | CRITICAL |
| VR-003 | No two components may share the same component_id. | CRITICAL |
| VR-004 | Each component must conform to its type-specific schema. | HIGH |
| VR-005 | version must follow MAJOR.MINOR.PATCH format. | MEDIUM |
| VR-006 | No duplicate step_name values within a workflow. | CRITICAL |
| VR-007 | step_type must be prompt or action. | CRITICAL |
| VR-008 | policy_name must be one of the 5 defined role policies. | CRITICAL |
| VR-009 | artifact_key must be UPPER_SNAKE_CASE with _FILE suffix. | HIGH |
| VR-010 | Every step must have onsuccess routing to a valid next step. | CRITICAL |
| VR-011 | Every prompt step must include self_critic and self_validation patterns. | HIGH |
| VR-012 | Every required_inputs artifact must reference a prior-produced artifact or workflow input. | CRITICAL |
| VR-013 | composition_standard must define all 3 schema layers. | CRITICAL |
| VR-014 | output_variance component_requirements must be feasible. | HIGH |
| VR-015 | Steps referencing WORKFLOW_SPEC_FILE in prompt must declare it in required_inputs. | CRITICAL |
| VR-016 | Both generate_package and refine_package must declare STANDARDS_COMPOSITION_STANDARD_FILE in produces. | CRITICAL |

### 2.4 Dynamic Discovery Mechanism

This standard supports dynamic discovery of component types. The
discover_component_types function parses the composition standard
document to extract the list of component type names at runtime.

**Function signature:**

```python
def discover_component_types(standard_path: str) -> list[str]:
    """Parse COMPOSITION_STANDARD.md and return list of component type names.

    Reads the YAML frontmatter field component_type_count and scans for
    Type N: type_name headings in the Component Schema section.
    Returns list of type names found.
    """
```

**How it works:**

1. Parse YAML frontmatter for component_type_count (expected: 8).
2. Scan for headings matching the pattern "#### Type N: {type_name}"
   in the Component Schema section.
3. Extract type names from matched headings.
4. Return the list of discovered type names.

**Fallback:** If discovery fails (malformed standard, missing
frontmatter), fall back to the 8 base types: step_definition,
role_policy, routing_pattern, prompt_pattern, artifact_contract,
composition_standard, output_variance, domain_spec.

### 2.5 Extensibility Model

New component types can be added to this schema without breaking
existing compositions.

**Principles:**

1. Identity stability: Existing compositions reference components by
   component_id, not by type. Adding new types does not affect
   existing references.
2. Common property stability: The 5 required + 3 optional common
   properties remain stable across all types.
3. Additive extension: New types are added by defining their
   type-specific properties. Existing types are not modified.
4. Validation rule isolation: New types may introduce additional
   type-specific validation rules scoped to the new type.
5. Discovery compatibility: The dynamic discovery mechanism
   automatically picks up new types via heading scan.
6. Backward compatibility: Compositions created before a new type
   continue to function without using the new type.

**Extension rules:**

| Rule | Description |
|---|---|
| EX-001 | New types must include all 5 required common properties. |
| EX-002 | New types must have a unique component_type enum value. |
| EX-003 | New types must not modify the schema of existing types. |
| EX-004 | New types must include at least one complete example. |
| EX-005 | New types must define a heading matching "#### Type N: {name}" for discovery. |
| EX-006 | New binding rules must follow the BR-NNN numbering sequence. |
| EX-007 | New validation rules must follow the VR-NNN numbering sequence. |

---

## Section 3: Composition Format

This section defines Layer 2 of the three-layer architecture. Layer 2
takes the building blocks from Layer 1 and defines the rules for
assembling them into compositions.

### 3.1 Composition Structure

Every composition is a YAML document with the following top-level
fields:

| Field | Type | Required | Description |
|---|---|---|---|
| builder_name | string | Yes | Unique builder identifier. Lowercase with underscores. |
| builder_label | string | Yes | Human-readable display name. |
| job_prefix | string | Yes | 4-6 character prefix for job IDs. Uppercase alphanumeric. |
| builder_purpose | string | Yes | What this builder solves. |
| workflow_pattern | enum | Yes | One of 6 defined patterns. |
| step_bindings | array | Yes | Ordered step definitions. |
| artifact_bindings | object | Yes | Artifact contracts. |
| composition_standard_binding | object | Yes | The composition standard reference. |
| output_variances | array | No | Output configurations. |
| self_bootstrap_binding | object | Yes | Self-bootstrapping configuration. |

### 3.2 Binding Rules

9 binding rules govern how the 8 component types from Layer 1 are
bound to composition slots.

| Rule | Binding Name | Component Type | Cardinality | Required |
|---|---|---|---|---|
| BR-001 | steps | step_definition | Ordered list | Yes |
| BR-002 | roles | role_policy | Singleton per step | Yes |
| BR-003 | routing | routing_pattern | Singleton per step | Yes |
| BR-004 | prompts | prompt_pattern | Unordered set per prompt step | No |
| BR-005 | artifacts | artifact_contract | Unordered set | Yes |
| BR-006 | standard | composition_standard | Singleton | Yes |
| BR-007 | variances | output_variance | Unordered set | No |
| BR-008 | domain_specs | domain_spec | Unordered set | No |
| BR-009 | self_bootstrap | domain_spec | Singleton | Yes |

**BR-001 (steps):** The step_bindings array defines ordered step
definitions. Steps execute in array order. Each step must have a
unique step_name (VR-006).

**BR-002 (roles):** Each step has an embedded coder sub-mapping that
assigns a role_policy. Exactly one role_policy per step. policy_name
must be one of the 5 valid values (VR-008).

**BR-003 (routing):** Each step has embedded routing via onsuccess
and optional on_reject_refine. The last step routes to
step_completion.

**BR-004 (prompts):** Prompt-type steps include prompt_pattern
components. Every prompt step must include self_critic and
self_validation (VR-011).

**BR-005 (artifacts):** The artifact_bindings array defines all
artifact contracts. Each artifact_key must be UPPER_SNAKE_CASE with
_FILE suffix (VR-009).

**BR-006 (standard):** Exactly one composition_standard per
composition. Must define all 3 schema layers (VR-013).

**BR-007 (variances):** Optional output variances. Each must have
feasible component_requirements (VR-014).

**BR-008 (domain_specs):** Optional accepted specification types.

**BR-009 (self_bootstrap):** Required self-bootstrap binding with 4
fields: bootstrap_spec_key (always "WORKFLOW_SPEC_FILE"),
bootstrap_spec_target (always "Specs/{builder_name}.md"),
bootstrap_version, and next_version_pattern.

### 3.3 Workflow Patterns

6 workflow patterns are defined:

| Pattern | Phase Count | Step Types | Description |
|---|---|---|---|
| action_only | 1-3 | action | All deterministic Python operations. |
| prompt_driven | 3-5 | prompt | LLM-driven with review and refine. |
| mixed | 3-7 | prompt + action | Combination of prompt and action. |
| gatekeeper_pipeline | 5-9 | prompt + action | Multi-phase with QC gates. |
| meta_workflow_builder | 7-9 | prompt + action | Builds other workflows. |
| meta_meta_builder | 9 | prompt + action | Builds meta builders with self-bootstrap. |

**Pattern selection rules:**

| Rule | Description |
|---|---|
| PS-001 | The workflow_pattern must be one of the 6 defined values. |
| PS-002 | The selected pattern determines the minimum and maximum phase count. |
| PS-003 | meta_meta_builder pattern requires self_bootstrap_binding. |
| PS-004 | action_only pattern must not include prompt patterns. |
| PS-005 | prompt_driven pattern must include review and refine steps. |
| PS-006 | gatekeeper_pipeline pattern must include gatekeep steps at phase boundaries. |

### 3.4 Override Mechanism

Overrides allow per-composition customization of component properties
without modifying the original component definition.

**Merge semantics:** Shallow merge. Override values win on conflict
for type-specific and optional common properties.

**Non-overridable properties:** The 5 required common properties
(component_id, component_type, name, version, description) cannot
be overridden.

**Overridable properties:** Optional common properties (duration_range,
platforms, tags) and type-specific properties (purpose,
enable_notifications, assignment_rule, max_iterations, sections,
filename_pattern, extensibility_model, variance_description,
spec_version_range).

**Override rules:**

| Rule | Description |
|---|---|
| OV-001 | Override values must conform to type-specific schema. |
| OV-002 | Common identity properties cannot be overridden. |
| OV-003 | Override values are merged shallowly. |
| OV-004 | Override must not change step_type. |
| OV-005 | Override must not change policy_name. |

### 3.5 Placeholder Resolution

Placeholder tokens ({PLACEHOLDER_NAME}) are resolved at runtime from
4 data sources in priority order:

| Priority | Data Source | Examples |
|---|---|---|
| 1 | Input Spec | {WORKFLOW_SPEC_FILE}, {builder_name}, {job_prefix} |
| 2 | Governance | {BASE_COMPOSITION_STANDARD}, {GOVERNANCE_RUNTIME_ROOT} |
| 3 | Runtime | {job_id}, {seq}, {workspace_root}, {timestamp} |
| 4 | Discovery | {DISCOVERED_COMPONENT_TYPES}, {COMPOSITION_STANDARD_PATH} |

**Resolution rules:**

| Rule | Description |
|---|---|
| PR-001 | Every placeholder must be resolvable from one source. |
| PR-002 | Input Spec fields available to all steps. |
| PR-003 | Governance fields available to all steps. |
| PR-004 | Runtime fields available to all steps. |
| PR-005 | Discovery fields available only after generate_composition_standard. |
| PR-006 | Unresolvable placeholders replaced with {UNRESOLVED: field_name}. |
| PR-007 | Placeholder names use UPPER_SNAKE_CASE. |

### 3.6 Ordering Rules

Step bindings must satisfy ordering constraints:

| Rule | Description |
|---|---|
| OR-001 | Foundation phase steps must be first. |
| OR-002 | Refine steps follow their review steps. |
| OR-003 | Layer 1 (Component Schema) before Layer 2 (Composition Format) before Layer 3 (Output Format). |
| OR-004 | Composition Format phase before Output Format phase. |
| OR-005 | Output Format phase before Operational Workflow phase. |
| OR-006 | Gatekeep steps follow generate steps. |
| OR-007 | No consecutive generate steps in gated phases. |
| OR-008 | promote_workflow_package before step_completion. |
| OR-009 | step_completion must be last. |
| OR-010 | No backward jumps except refine loops. |

### 3.7 Composition Validation

10 composition validation checks (CV-001 through CV-010) verify that
a composition document is well-formed and internally consistent.

| Check | Severity | Description |
|---|---|---|
| CV-001 | CRITICAL | Required fields present. |
| CV-002 | CRITICAL | Binding rule conformance (BR-001 through BR-009). |
| CV-003 | CRITICAL | Workflow pattern validity (one of 6 values). |
| CV-004 | CRITICAL | Step name uniqueness. |
| CV-005 | CRITICAL | Artifact flow integrity (no dangling references). |
| CV-006 | HIGH | Override schema conformance. |
| CV-007 | CRITICAL | Phase ordering. |
| CV-008 | CRITICAL | Routing completeness. |
| CV-009 | HIGH | Prompt pattern completeness. |
| CV-010 | CRITICAL | Self-bootstrap consistency. |

---

## Section 4: Output Format

This section defines Layer 3 of the three-layer architecture. Layer 3
consumes Layer 2 compositions and resolves them into concrete output
files on disk.

### 4.1 Output Structure

Every workflow builder execution produces a 3-part output:

#### Part 1: Composition Standard

**Directory:** Standards/
**Primary file:** Standards/COMPOSITION_STANDARD.md

Contains the composition standard for the generated meta builder.
Includes YAML frontmatter, component type definitions, schema layers,
and extensibility model.

**Artifact key:** STANDARDS_COMPOSITION_STANDARD_FILE
**Produced by:** generate_package and refine_package steps.

#### Part 2: Builder Specification

**Directory:** Specs/
**Primary file:** Specs/{builder_name}.md

Contains the builder's own specification, embedded as a copy of the
input WORKFLOW_SPEC_FILE. Enables self-bootstrapping.

**Artifact key:** SPECS_BUILDER_SPEC_FILE
**Produced by:** embed_builder_spec step.

#### Part 3: Workflow Package

**Root directory:** {builder_name}/

Contains the executable workflow package.

| File | Required | Description |
|---|---|---|
| workflow.toml | Yes | Workflow manifest with steps, artifacts, routing. |
| context_extensions.py | Yes | Artifact registration, context injection, discovery. |
| actions.py | Conditional | Custom action implementations. |
| prompts/ | Yes | One .txt per prompt step. |
| README.md | Yes | Package documentation. |
| .env.sample | Conditional | Sample environment variables. |
| config.json.sample | Conditional | Sample configuration. |

**Complete directory tree:**

```
{builder_name}/
|-- Standards/
|   +-- COMPOSITION_STANDARD.md
|-- Specs/
|   +-- {builder_name}.md
|-- workflow.toml
|-- context_extensions.py
|-- actions.py
|-- prompts/
|   |-- 01_generate_test_criteria.txt
|   |-- ...
|   +-- NN_{step_name}.txt
|-- README.md
|-- .env.sample              (conditional)
+-- config.json.sample       (conditional)
```

### 4.2 Promotion Contract

The promote_workflow_package action copies 3-part output to
workflows/{slug}/:

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

If Standards/ or Specs/ is missing, the promote action REJECTS with
error code MISSING_REQUIRED_OUTPUT_DIR.

### 4.3 Resolution Rules

9 resolution rules define how composition components become output
files.

**RR-001: step_definition Resolution**
Source: step_bindings -> Target: workflow.toml [[step]] sections.
Each step_definition maps to a TOML step table with step_name, type,
purpose, required_inputs, produces, coder, and routing.

**RR-002: role_policy Resolution**
Source: inline coder bindings -> Target: workflow.toml [[step]].coder.
policy_name maps to coder.role, assignment_rule maps to
coder.assignment_rule.

**RR-003: routing_pattern Resolution**
Source: inline routing -> Target: workflow.toml onsuccess and
on_reject_refine fields.

**RR-004: prompt_pattern Resolution**
Source: inline prompt_patterns -> Target: prompts/NN_{step_name}.txt
files. Each pattern_name maps to a prompt section template.

**RR-005: artifact_contract Resolution**
Source: artifact_bindings -> Target: context_extensions.py
register_artifact_keys() and workflow.toml [artifacts] section.

**RR-006: composition_standard Resolution**
Source: composition_standard_binding -> Target:
Standards/COMPOSITION_STANDARD.md. Must define all 3 schema layers.

**RR-007: placeholder Resolution**
Source: {PLACEHOLDER} tokens -> Target: Resolved values from 4 data
sources per Layer 2 placeholder resolution rules.

**RR-008: self_bootstrap Resolution**
Source: self_bootstrap_binding -> Target: Specs/{builder_name}.md.
The embed_builder_spec action copies WORKFLOW_SPEC_FILE to the
Specs/ directory.

**RR-009: dynamic_discovery Resolution**
Source: DISCOVERED_COMPONENT_TYPES -> Target: All prompt templates
that reference component types. The discover_component_types()
function parses the composition standard and returns type names.

### 4.4 Quality Requirements

12 quality requirements define output acceptance criteria:

| Rule ID | Requirement | Severity |
|---|---|---|
| QR-001 | TOML parse validity of workflow.toml | CRITICAL |
| QR-002 | Python syntax validity of context_extensions.py and actions.py | CRITICAL |
| QR-003 | TYPE_CHECKING runtime import detection (no runtime imports under guards) | CRITICAL |
| QR-004 | Artifact binding consistency (no dangling references) | CRITICAL |
| QR-005 | Action step implementation completeness | CRITICAL |
| QR-006 | Prompt file existence (one .txt per prompt step) | CRITICAL |
| QR-007 | Prompt placeholder vs required_inputs consistency | CRITICAL |
| QR-008 | context_extensions.py artifact key coverage | CRITICAL |
| QR-009 | Standards/ directory exists with COMPOSITION_STANDARD.md | CRITICAL |
| QR-010 | Specs/ directory exists with at least one .md file | CRITICAL |
| QR-011 | Bidirectional prompt placeholder vs artifact declaration consistency | CRITICAL |
| QR-012 | Both generate_package and refine_package declare STANDARDS_COMPOSITION_STANDARD_FILE | CRITICAL |

### 4.5 Downstream Extraction Contracts

3 extraction contracts define how consumers use the output:

**DEC-001: Workflow Manifest Extraction**
Consumer: Workflow runner (step_runner.py, coder_adapters.py)
Source: workflow.toml
Method: TOML parser extracts step definitions, coder roles, routing,
artifact declarations.

**DEC-002: Prompt Template Extraction**
Consumer: Coder adapters (coder_adapters.py)
Source: prompts/*.txt
Method: Plain text read with placeholder substitution.

**DEC-003: Composition Standard Extraction**
Consumer: context_extensions.py discover_component_types()
Source: Standards/COMPOSITION_STANDARD.md
Method: YAML frontmatter parse + heading scan for component types.

---

## Section 5: Operational Requirements

This section defines the complete operational workflow design for the
Workflow Builder v3 meta-meta builder.

### 5.1 Workflow Phases

The workflow is organized into 9 sequential phases.

| Phase | Purpose | Steps |
|---|---|---|
| 1 | Foundation (TDD Loop) | 01 generate_test_criteria, 02 review_test_criteria, 03 refine_test_criteria |
| 2 | Component Schema (Layer 1) | 04 generate_component_schema, 05 gatekeep_component_schema |
| 3 | Composition Format (Layer 2) | 06 generate_composition_format, 07 gatekeep_composition_format |
| 4 | Output Format (Layer 3) | 08 generate_output_format, 09 gatekeep_output_format |
| 5 | Operational Workflow | 10 generate_operational_workflow, 11 gatekeep_operational_workflow |
| 6 | Composition Standard | 12 generate_composition_standard, 13 gatekeep_composition_standard |
| 7 | Meta Composition Spec | 14 generate_meta_composition_spec |
| 8 | Package Assembly | 15 generate_package, 16 validate_package_deterministic, 17 gatekeep_package, 18 review_package, 19 refine_package |
| 9 | Promotion | 20 promote_workflow_package, 21 step_completion |

### 5.2 Step Sequence

| Step | Name | Type | Purpose | Required Inputs | Produces | Onsuccess |
|------|------|------|---------|-----------------|----------|-----------|
| 01 | generate_test_criteria | prompt | Generate acceptance criteria | WORKFLOW_SPEC_FILE | TEST_CRITERIA_FILE | review_test_criteria |
| 02 | review_test_criteria | prompt | Review test criteria | TEST_CRITERIA_FILE | REVIEW_TEST_CRITERIA_FILE | generate_component_schema |
| 03 | refine_test_criteria | prompt | Refine test criteria (conditional) | TEST_CRITERIA_FILE, REVIEW_TEST_CRITERIA_FILE | TEST_CRITERIA_FILE | review_test_criteria |
| 04 | generate_component_schema | prompt | Generate component schema Layer 1 | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE | COMPONENT_SCHEMA_FILE | gatekeep_component_schema |
| 05 | gatekeep_component_schema | prompt | Validate component schema | COMPONENT_SCHEMA_FILE, TEST_CRITERIA_FILE | GATEKEEP_COMPONENT_SCHEMA_FILE | generate_composition_format |
| 06 | generate_composition_format | prompt | Generate composition format Layer 2 | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE | COMPOSITION_FORMAT_FILE | gatekeep_composition_format |
| 07 | gatekeep_composition_format | prompt | Validate composition format | COMPOSITION_FORMAT_FILE, TEST_CRITERIA_FILE | GATEKEEP_COMPOSITION_FORMAT_FILE | generate_output_format |
| 08 | generate_output_format | prompt | Generate output format Layer 3 | WORKFLOW_SPEC_FILE, COMPOSITION_FORMAT_FILE | OUTPUT_FORMAT_FILE | gatekeep_output_format |
| 09 | gatekeep_output_format | prompt | Validate output format | OUTPUT_FORMAT_FILE, TEST_CRITERIA_FILE | GATEKEEP_OUTPUT_FORMAT_FILE | generate_operational_workflow |
| 10 | generate_operational_workflow | prompt | Generate operational workflow | WORKFLOW_SPEC_FILE, OUTPUT_FORMAT_FILE | OPERATIONAL_WORKFLOW_FILE | gatekeep_operational_workflow |
| 11 | gatekeep_operational_workflow | prompt | Validate operational workflow | OPERATIONAL_WORKFLOW_FILE, TEST_CRITERIA_FILE | GATEKEEP_OPERATIONAL_WORKFLOW_FILE | generate_composition_standard |
| 12 | generate_composition_standard | prompt | Generate composition standard | WORKFLOW_SPEC_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE | COMPOSITION_STANDARD_FILE | gatekeep_composition_standard |
| 13 | gatekeep_composition_standard | prompt | Validate composition standard | COMPOSITION_STANDARD_FILE, TEST_CRITERIA_FILE | GATEKEEP_COMPOSITION_STANDARD_FILE | generate_meta_composition_spec |
| 14 | generate_meta_composition_spec | prompt | Generate meta composition spec | WORKFLOW_SPEC_FILE, COMPOSITION_STANDARD_FILE | META_COMPOSITION_SPEC_FILE | generate_package |
| 15 | generate_package | prompt | Generate complete workflow package | WORKFLOW_SPEC_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE | validate_package_deterministic |
| 16 | validate_package_deterministic | action | Run 11 validation checks | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, STANDARDS_COMPOSITION_STANDARD_FILE, SPECS_BUILDER_SPEC_FILE | VALIDATION_REPORT_FILE | gatekeep_package |
| 17 | gatekeep_package | prompt | Gatekeep the package | VALIDATION_REPORT_FILE, TEST_CRITERIA_FILE | GATEKEEP_PACKAGE_FILE | review_package |
| 18 | review_package | prompt | Final review of package | GATEKEEP_PACKAGE_FILE, TEST_CRITERIA_FILE | REVIEW_FILE_SUGGESTED | promote_workflow_package |
| 19 | refine_package | prompt | Refine package (conditional) | GATEKEEP_PACKAGE_FILE, REVIEW_FILE_SUGGESTED | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE | review_package |
| 20 | promote_workflow_package | action | Promote 3-part output to workflows/ | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE, SPECS_BUILDER_SPEC_FILE, WORKFLOW_PROMPTS_INDEX_FILE | WORKFLOW_PACKAGE_DIR_FILE | step_completion |
| 21 | step_completion | action | Mark workflow complete | WORKFLOW_PACKAGE_DIR_FILE | -- | -- |

**Step type summary:**
- Prompt steps: 18 (steps 01 through 15, 17 through 19)
- Action steps: 3 (steps 16, 20, 21)

**Conditional steps:**
- Step 03 (refine_test_criteria): Executes only if step 02 returns REJECTED
- Step 19 (refine_package): Executes only if step 18 returns REJECTED

### 5.3 Artifact Contracts

#### Input Artifacts

| Artifact Key | Description | Required | Source |
|---|---|---|---|
| WORKFLOW_SPEC_FILE | Composition system specification defining the meta builder | Yes | User input at workflow startup |

#### Output Artifacts

| Artifact Key | Description | Filename Pattern | Produced By |
|---|---|---|---|
| TEST_CRITERIA_FILE | Acceptance criteria | TEST_CRITERIA-{seq}.md | 01 generate_test_criteria |
| REVIEW_TEST_CRITERIA_FILE | Review of test criteria | REVIEW_TEST_CRITERIA-{seq}.md | 02 review_test_criteria |
| COMPONENT_SCHEMA_FILE | Component schema (8 types) | COMPONENT_SCHEMA-{seq}.md | 04 generate_component_schema |
| GATEKEEP_COMPONENT_SCHEMA_FILE | Gatekeep review | GATEKEEP_COMPONENT_SCHEMA-{seq}.md | 05 gatekeep_component_schema |
| COMPOSITION_FORMAT_FILE | Composition format (9 bindings) | COMPOSITION_FORMAT-{seq}.md | 06 generate_composition_format |
| GATEKEEP_COMPOSITION_FORMAT_FILE | Gatekeep review | GATEKEEP_COMPOSITION_FORMAT-{seq}.md | 07 gatekeep_composition_format |
| OUTPUT_FORMAT_FILE | Output format (3-part structure) | OUTPUT_FORMAT-{seq}.md | 08 generate_output_format |
| GATEKEEP_OUTPUT_FORMAT_FILE | Gatekeep review | GATEKEEP_OUTPUT_FORMAT-{seq}.md | 09 gatekeep_output_format |
| OPERATIONAL_WORKFLOW_FILE | Operational workflow design | OPERATIONAL_WORKFLOW-{seq}.md | 10 generate_operational_workflow |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | Gatekeep review | GATEKEEP_OPERATIONAL_WORKFLOW-{seq}.md | 11 gatekeep_operational_workflow |
| COMPOSITION_STANDARD_FILE | Composition standard | COMPOSITION_STANDARD-{seq}.md | 12 generate_composition_standard |
| GATEKEEP_COMPOSITION_STANDARD_FILE | Gatekeep review | GATEKEEP_COMPOSITION_STANDARD-{seq}.md | 13 gatekeep_composition_standard |
| META_COMPOSITION_SPEC_FILE | Meta composition spec (this document type) | META_COMPOSITION_SPEC-{seq}.md | 14 generate_meta_composition_spec |
| WORKFLOW_MANIFEST_FILE | Workflow manifest | workflow.toml | 15 generate_package |
| WORKFLOW_EXTENSIONS_FILE | Context extensions | context_extensions.py | 15 generate_package |
| WORKFLOW_ACTIONS_FILE | Custom actions | actions.py | 15 generate_package |
| WORKFLOW_PROMPTS_INDEX_FILE | Prompts index | prompts/index.txt | 15 generate_package |
| WORKFLOW_README_FILE | Package documentation | README.md | 15 generate_package |
| STANDARDS_COMPOSITION_STANDARD_FILE | Standards/ composition standard | Standards/COMPOSITION_STANDARD.md | 15 generate_package, 19 refine_package |
| SPECS_BUILDER_SPEC_FILE | Embedded builder spec | Specs/{builder_name}.md | 15 generate_package |
| VALIDATION_REPORT_FILE | Validation report (11 checks) | VALIDATION_REPORT-{seq}.md | 16 validate_package_deterministic |
| GATEKEEP_PACKAGE_FILE | Gatekeep review | GATEKEEP_PACKAGE-{seq}.md | 17 gatekeep_package |
| REVIEW_FILE_SUGGESTED | Final review | REVIEW-{seq}.md | 18 review_package |
| WORKFLOW_PACKAGE_DIR_FILE | Promoted package directory | workflows/{slug}/ | 20 promote_workflow_package |

**Artifact flow integrity:** Every artifact consumed by a step is
produced by a preceding step or declared as a workflow input. No
dangling references exist.

### 5.4 Routing

#### Reject-Refine Loops

**Loop 1 (LOOP-001): Test Criteria Review/Refine (Phase 1)**
- Review step: 02 review_test_criteria
- Refine step: 03 refine_test_criteria
- Artifact: TEST_CRITERIA_FILE
- Max iterations: 2
- Exhausted failure code: TEST_CRITERIA_REVIEW_EXHAUSTED
- Exhausted failure class: HUMAN_RETRY_REQUIRED

**Loop 2 (LOOP-002): Package Review/Refine (Phase 8)**
- Review step: 18 review_package
- Refine step: 19 refine_package
- Artifact: WORKFLOW_MANIFEST_FILE (and associated package files)
- Max iterations: 2
- Exhausted failure code: PACKAGE_REVIEW_EXHAUSTED
- Exhausted failure class: HUMAN_RETRY_REQUIRED

#### Gatekeep Loops (Phases 2 through 6)

| Phase | Gatekeep Step | Generate Step | Max Iterations | Exhausted Failure Code |
|---|---|---|---|---|
| 2 | 05 gatekeep_component_schema | 04 generate_component_schema | 2 | COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED |
| 3 | 07 gatekeep_composition_format | 06 generate_composition_format | 2 | COMPOSITION_FORMAT_GATEKEEP_EXHAUSTED |
| 4 | 09 gatekeep_output_format | 08 generate_output_format | 2 | OUTPUT_FORMAT_GATEKEEP_EXHAUSTED |
| 5 | 11 gatekeep_operational_workflow | 10 generate_operational_workflow | 2 | OPERATIONAL_WORKFLOW_GATEKEEP_EXHAUSTED |
| 6 | 13 gatekeep_composition_standard | 12 generate_composition_standard | 2 | COMPOSITION_STANDARD_GATEKEEP_EXHAUSTED |

### 5.5 Action Specifications

#### Action 1: validate_package_deterministic (Step 16)

**Step name:** validate_package_deterministic
**Step type:** action
**Coder role:** validation_standard

**Purpose:** Run 11 deterministic validation checks on the generated
workflow package.

**Required inputs:**
- WORKFLOW_MANIFEST_FILE (workflow.toml)
- WORKFLOW_EXTENSIONS_FILE (context_extensions.py)
- WORKFLOW_ACTIONS_FILE (actions.py)
- STANDARDS_COMPOSITION_STANDARD_FILE (Standards/COMPOSITION_STANDARD.md)
- SPECS_BUILDER_SPEC_FILE (Specs/{builder_name}.md)

**Produces:** VALIDATION_REPORT_FILE

**Validation checks (11):**

| Check | Description | Severity |
|---|---|---|
| 1 | TOML parse validity of workflow.toml | CRITICAL |
| 2 | Python syntax validity of context_extensions.py and actions.py | CRITICAL |
| 3 | TYPE_CHECKING runtime import detection | CRITICAL |
| 4 | Artifact binding consistency (no dangling references) | CRITICAL |
| 5 | Action step implementation completeness | CRITICAL |
| 6 | Prompt file existence (one .txt per prompt step) | CRITICAL |
| 7 | Prompt placeholder vs required_inputs consistency | CRITICAL |
| 8 | context_extensions.py artifact key coverage | CRITICAL |
| 9 | Standards/COMPOSITION_STANDARD.md existence | CRITICAL |
| 10 | Specs/ directory exists with at least one .md file | CRITICAL |
| 11 | Bidirectional prompt placeholder vs artifact declaration consistency | CRITICAL |

**Routing:** On completion, routes to gatekeep_package (step 17).

#### Action 2: promote_workflow_package (Step 20)

**Step name:** promote_workflow_package
**Step type:** action
**Coder role:** validation_standard

**Purpose:** Copy the validated 3-part output to the workflows/
directory. Enforces that Standards/ and Specs/ are present.

**Required inputs:**
- WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE
- WORKFLOW_README_FILE, WORKFLOW_PROMPTS_INDEX_FILE
- STANDARDS_COMPOSITION_STANDARD_FILE, SPECS_BUILDER_SPEC_FILE

**Produces:** WORKFLOW_PACKAGE_DIR_FILE

**Enforcement:** If Standards/ or Specs/ is missing, the action
REJECTS with status REJECTED and error code
MISSING_REQUIRED_OUTPUT_DIR.

#### Action 3: step_completion (Step 21)

**Step name:** step_completion
**Step type:** action
**Coder role:** validation_standard

**Purpose:** Mark the workflow as complete. Terminal step that
executes only after promote_workflow_package returns APPROVED.

**Required inputs:** WORKFLOW_PACKAGE_DIR_FILE
**Produces:** None (terminal step)

### 5.6 Self-Bootstrapping Capability

This section describes how the generated builder can process its own
specification to produce the next version, including the bootstrap
chain invariant.

#### Bootstrap Mechanism

The self-bootstrapping capability is enabled by two elements:

1. **Spec embedding (RR-008):** The embed_builder_spec action step
   copies the input WORKFLOW_SPEC_FILE to the output Specs/ directory
   as Specs/{builder_name}.md. This ensures every generated meta
   builder carries its own specification within its output.

2. **Self-bootstrap binding (BR-009):** The composition includes a
   self_bootstrap_binding that defines:
   - bootstrap_spec_key: "WORKFLOW_SPEC_FILE" (the input artifact)
   - bootstrap_spec_target: "Specs/{builder_name}.md" (the output path)
   - bootstrap_version: Current builder version (e.g., "3.0.0")
   - next_version_pattern: How to derive next version (e.g.,
     "increment_major")

#### Bootstrap Chain Process

```
1. Builder v3 is installed at workflows/workflow_builder_v3/
2. v3's Specs/ contains workflow_builder_v3.md (embedded by embed_builder_spec)
3. Submit workflow_builder_v3.md as WORKFLOW_SPEC_FILE to workflow_builder_v3
4. v3 processes the spec, generates workflow_builder_v4/
   - Standards/COMPOSITION_STANDARD.md (v4's standard)
   - Specs/workflow_builder_v3.md (embedded copy of input)
   - workflow.toml, prompts/, actions.py, context_extensions.py, README.md
5. Promote workflow_builder_v4 to workflows/workflow_builder_v4/
6. v4 can now bootstrap v5 using its own Specs/ copy
```

#### Bootstrap Chain Invariant

Every version N embeds its own specification in Specs/. Version N+1
is generated from that embedded specification. The chain is unbroken:

- v3 embeds workflow_builder_v3.md in Specs/
- Feeding workflow_builder_v3.md back into v3 produces v4
- v4 embeds workflow_builder_v4.md in Specs/ (via its own
  embed_builder_spec step)
- Feeding workflow_builder_v4.md back into v4 produces v5
- The chain continues indefinitely

This invariant ensures that the composition system is self-sustaining.
Each generation carries forward the complete knowledge needed to
produce the next generation, including the specification that defines
the builder's own structure.

#### Zero-Manual-Intervention Guarantee

The self-bootstrapping process requires zero manual intervention:

1. The input spec is automatically embedded in Specs/ by the
   embed_builder_spec action (step 16 in the v4 sequence, or step 15
   in v3's package generation).
2. The embedded spec is automatically promoted along with the rest
   of the 3-part output by promote_workflow_package.
3. The next version reads the embedded spec as its WORKFLOW_SPEC_FILE
   input and generates the subsequent version.
4. Dynamic component discovery (via discover_component_types) ensures
   the generated builder adapts to whatever component types are
   defined in its input spec, rather than relying on hardcoded lists.

---

## Self-Validation

### Section Completeness

| Section | Required | Present | Content |
|---|---|---|---|
| 1. Domain Overview | Yes | YES | Domain description, builder purpose, workflow pattern type |
| 2. Component Schema | Yes | YES | 8 types, common properties, validation rules, discovery |
| 3. Composition Format | Yes | YES | 9 binding rules, 6 patterns, override, placeholders, ordering |
| 4. Output Format | Yes | YES | 3-part structure, 9 resolution rules, 12 quality requirements |
| 5. Operational Requirements | Yes | YES | 9 phases, 21 steps, artifacts, routing, actions, bootstrap |

**Verification:** All 5 required sections present. TC-051 satisfied.

### Self-Bootstrapping Capability

| Requirement | Satisfied |
|---|---|
| Describes how builder processes own spec | YES (Section 5.6) |
| Explains bootstrap chain process | YES (Section 5.6 Bootstrap Chain Process) |
| Defines bootstrap chain invariant | YES (Section 5.6 Bootstrap Chain Invariant) |
| Zero-manual-intervention guarantee | YES (Section 5.6) |

**Verification:** TC-052 satisfied.

### Criteria Traceability

| Criteria | Status | Evidence |
|---|---|---|
| TC-051 | PASS | 5 sections present: Domain Overview, Component Schema, Composition Format, Output Format, Operational Requirements |
| TC-052 | PASS | Self-bootstrapping capability description in Section 5.6 with bootstrap chain invariant |

---

End of Meta Composition Spec Document
