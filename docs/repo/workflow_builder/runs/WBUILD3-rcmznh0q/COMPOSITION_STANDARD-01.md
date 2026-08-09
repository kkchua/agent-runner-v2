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
validation_rule_count: 16
binding_rule_count: 9
resolution_rule_count: 9
quality_requirement_count: 12
---

# Composition Standard: Workflow Builder Standard v1.0.0

## Overview

This document is the composition standard for the workflow_builder
domain. It is the authoritative reference that defines what component
types are available, how they are assembled into compositions, and how
compositions are resolved into executable output files.

This standard is the key self-describing element of the Workflow
Builder v3 meta-meta builder. Every generated meta builder includes
its own composition standard, making the builder aware of its own
component types and structure. Subsequent workflow steps discover
component types dynamically from this document rather than relying
on hardcoded lists.

**Standard name:** WORKFLOW_BUILDER_STANDARD
**Standard version:** 1.0.0
**Domain:** workflow_builder
**Component types defined:** 8
**Schema layers:** 3 (Component Schema, Composition Format, Output
Format)
**Validation rules:** 16 (VR-001 through VR-016)
**Binding rules:** 9 (BR-001 through BR-009)
**Resolution rules:** 9 (RR-001 through RR-009)
**Quality requirements:** 12 (QR-001 through QR-012)

The three layers of this standard are:

- **Layer 1 -- Component Schema:** Defines the 8 component types
  with their schemas, validation rules, and examples. This is the
  building block library.
- **Layer 2 -- Composition Format:** Defines how components from
  Layer 1 are assembled into compositions with binding rules,
  workflow patterns, override mechanisms, and placeholder resolution.
- **Layer 3 -- Output Format:** Defines how compositions from
  Layer 2 are resolved into concrete output files with resolution
  rules, quality requirements, and downstream extraction contracts.

**Layer boundaries are absolute.** Layer 1 is read-only authority
for component types and schemas. Layer 2 is read-only authority for
binding rules and composition structure. Layer 3 consumes Layer 2
output and produces files. No layer redefines or contradicts the
layers below it.

---

## Component Schema

This section defines Layer 1 of the three-layer architecture. Layer 1
is the Universal Component Schema for the workflow_builder domain. It
provides the foundational building block library from which all meta
builder compositions are constructed.

### Common Properties

All 8 component types share the following common properties regardless
of their component_type value. These form the stable foundation of
the schema.

#### Required Common Properties (5)

Every component instance must include all 5 of these properties.

| Property | Type | Required | Description |
|---|---|---|---|
| component_id | string | Yes | Unique identifier. Format: {type}-{name}-{seq}. Must be unique across all components in a composition. |
| component_type | enum | Yes | One of the 8 defined types (see below). |
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

### Component Types

The following 8 component types are defined in this standard. Each
type is described with its purpose, required status, cardinality,
type-specific properties, validation rules, and an example.

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
  extensibility_model: "New component types can be added to the standard without breaking existing compositions"
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
| VR-014 | output_variance component_requirements must be feasible (valid component types). | HIGH |
| VR-015 | Steps referencing WORKFLOW_SPEC_FILE in prompt must declare it in required_inputs. | CRITICAL |
| VR-016 | Both generate_package and refine_package must declare STANDARDS_COMPOSITION_STANDARD_FILE in produces. | CRITICAL |

### Dynamic Discovery Mechanism

This standard supports dynamic discovery of component types. The
discover_component_types function parses this document to extract
the list of component type names at runtime.

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

---

## Composition Format

This section defines Layer 2 of the three-layer architecture. Layer 2
takes the building blocks from Layer 1 and defines the rules for
assembling them into compositions. It answers how components are
bound, what patterns are available, how placeholders are resolved,
and what ordering constraints apply.

### Composition Structure

Every composition is a YAML document with the following top-level
fields:

| Field | Type | Required | Description |
|---|---|---|---|
| builder_name | string | Yes | Unique builder identifier. |
| builder_label | string | Yes | Human-readable display name. |
| job_prefix | string | Yes | 4-6 character prefix for job IDs. |
| builder_purpose | string | Yes | What this builder solves. |
| workflow_pattern | enum | Yes | One of 6 defined patterns. |
| step_bindings | array | Yes | Ordered step definitions. |
| artifact_bindings | object | Yes | Artifact contracts. |
| composition_standard_binding | object | Yes | The composition standard reference. |
| output_variances | array | No | Output configurations. |
| self_bootstrap_binding | object | Yes | Self-bootstrapping configuration. |

### Binding Rules

9 binding rules govern how the 8 component types are bound to
composition slots.

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
definitions. Each entry is a step_definition component with all
required common and type-specific properties. Steps execute in
array order. Each step must have a unique step_name (VR-006).

**BR-002 (roles):** Each step has an embedded coder sub-mapping
that assigns a role_policy. Exactly one role_policy per step.
policy_name must be one of the 5 valid values (VR-008).

**BR-003 (routing):** Each step has embedded routing via onsuccess
and optional on_reject_refine. The last step routes to
step_completion.

**BR-004 (prompts):** Prompt-type steps include prompt_pattern
components. Every prompt step must include self_critic and
self_validation (VR-011).

**BR-005 (artifacts):** The artifact_bindings array defines all
artifact contracts. Each artifact_key must be UPPER_SNAKE_CASE
with _FILE suffix (VR-009).

**BR-006 (standard):** Exactly one composition_standard per
composition. Must define all 3 schema layers (VR-013).

**BR-007 (variances):** Optional output variances. Each must have
feasible component_requirements (VR-014).

**BR-008 (domain_specs):** Optional accepted specification types.

**BR-009 (self_bootstrap):** Required self-bootstrap binding with
4 fields: bootstrap_spec_key (always "WORKFLOW_SPEC_FILE"),
bootstrap_spec_target (always "Specs/{builder_name}.md"),
bootstrap_version, and next_version_pattern.

### Workflow Patterns

6 workflow patterns are defined:

| Pattern | Phase Count | Step Types | Description |
|---|---|---|---|
| action_only | 1-3 | action | All deterministic Python operations. |
| prompt_driven | 3-5 | prompt | LLM-driven with review and refine. |
| mixed | 3-7 | prompt + action | Combination of prompt and action. |
| gatekeeper_pipeline | 5-9 | prompt + action | Multi-phase with QC gates. |
| meta_workflow_builder | 7-9 | prompt + action | Builds other workflows. |
| meta_meta_builder | 9 | prompt + action | Builds meta builders with self-bootstrap. |

### Override Mechanism

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
- OV-001: Override values must conform to type-specific schema.
- OV-002: Common identity properties cannot be overridden.
- OV-003: Override values are merged shallowly.
- OV-004: Override must not change step_type.
- OV-005: Override must not change policy_name.

### Placeholder Resolution

Placeholder tokens ({PLACEHOLDER_NAME}) are resolved at runtime from
4 data sources in priority order:

| Priority | Data Source | Examples |
|---|---|---|
| 1 | Input Spec | {WORKFLOW_SPEC_FILE}, {builder_name}, {job_prefix} |
| 2 | Governance | {BASE_COMPOSITION_STANDARD}, {GOVERNANCE_RUNTIME_ROOT} |
| 3 | Runtime | {job_id}, {seq}, {workspace_root}, {timestamp} |
| 4 | Discovery | {DISCOVERED_COMPONENT_TYPES}, {COMPOSITION_STANDARD_PATH} |

**Resolution rules:**
- PR-001: Every placeholder must be resolvable from one source.
- PR-002: Input Spec fields available to all steps.
- PR-003: Governance fields available to all steps.
- PR-004: Runtime fields available to all steps.
- PR-005: Discovery fields available only after generate_composition_standard.
- PR-006: Unresolvable placeholders replaced with {UNRESOLVED: field_name}.
- PR-007: Placeholder names use UPPER_SNAKE_CASE.

### Ordering Rules

Step bindings must satisfy ordering constraints:

- OR-001: Foundation phase steps must be first.
- OR-002: Refine steps follow their review steps.
- OR-003: Layer 1 before Layer 2 before Layer 3.
- OR-004: Composition Format before Output Format.
- OR-005: Output Format before Operational Workflow.
- OR-006: Gatekeep steps follow generate steps.
- OR-007: No consecutive generate steps in gated phases.
- OR-008: promote_workflow_package before step_completion.
- OR-009: step_completion must be last.
- OR-010: No backward jumps except refine loops.

---

## Output Format

This section defines Layer 3 of the three-layer architecture. Layer 3
consumes Layer 2 compositions and resolves them into concrete output
files on disk. It defines the output structure, resolution rules,
quality requirements, and downstream extraction contracts.

### Output Structure

Every workflow builder execution produces a 3-part output:

**Part 1: Standards/COMPOSITION_STANDARD.md**

The composition standard for the generated meta builder. Contains
YAML frontmatter, component type definitions, schema layers, and
extensibility model.

Artifact key: STANDARDS_COMPOSITION_STANDARD_FILE
Produced by: generate_package and refine_package steps.

**Part 2: Specs/{builder_name}.md**

The builder's own specification, embedded as a copy of the input
WORKFLOW_SPEC_FILE. Enables self-bootstrapping.

Artifact key: SPECS_BUILDER_SPEC_FILE
Produced by: embed_builder_spec step.

**Part 3: Workflow Package**

The executable workflow package directory containing:

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

### Promotion Contract

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

### Resolution Rules

9 resolution rules define how composition components become output
files:

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

### Quality Requirements

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

### Downstream Extraction Contracts

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

## Extensibility Model

This section describes how new component types can be added to this
standard without breaking existing compositions.

### Principles

1. **Identity stability:** Existing compositions reference components
   by component_id, not by type. Adding new types does not affect
   existing component references.

2. **Common property stability:** The 5 required common properties
   (component_id, component_type, name, version, description) and 3
   optional common properties (duration_range, platforms, tags)
   remain stable. New types inherit these without modification.

3. **Additive extension:** New types are added by defining their
   type-specific properties in the Component Types section. Existing
   types are not modified.

4. **Validation rule isolation:** New types may introduce additional
   type-specific validation rules. These are scoped to the new type
   and do not modify existing global rules (VR-001 through VR-016).

5. **Discovery compatibility:** The dynamic discovery mechanism
   (discover_component_types) automatically picks up new types from
   the generated composition standard via heading scan. No code
   changes are needed for discovery.

6. **Backward compatibility:** Compositions created before a new type
   is added continue to function. They simply do not use the new type.

### Procedure for Adding a New Component Type

1. Define the new type name in the Component Types section using the
   heading pattern "#### Type N: {type_name}".
2. Specify its required and optional type-specific properties.
3. Add any type-specific validation rules (appending to VR-NNN).
4. Update component_type_count in the YAML frontmatter.
5. Provide at least one example component.
6. Update the extensibility_model description if constraints change.

### Concrete Extensibility Rules

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

## Self-Validation

This section verifies that this composition standard satisfies all
defined requirements.

### Component Type Completeness

| Number | Type | Defined | Has Properties | Has Validation | Has Example |
|---|---|---|---|---|---|
| 1 | step_definition | YES | YES (7 type-specific) | YES (VR-006, VR-007, VR-009, VR-012, VR-015) | YES |
| 2 | role_policy | YES | YES (2 type-specific) | YES (VR-008) | YES |
| 3 | routing_pattern | YES | YES (5 type-specific) | YES (VR-010) | YES |
| 4 | prompt_pattern | YES | YES (2 type-specific) | YES (VR-011) | YES |
| 5 | artifact_contract | YES | YES (5 type-specific) | YES (VR-009) | YES |
| 6 | composition_standard | YES | YES (5 type-specific) | YES (VR-013) | YES |
| 7 | output_variance | YES | YES (4 type-specific) | YES (VR-014) | YES |
| 8 | domain_spec | YES | YES (4 type-specific) | YES (common rules only) | YES |

**Verification:** All 8 component types defined with properties,
validation rules, and examples. TC-046 satisfied.

### Schema Layers Completeness

| Layer | Section | Defined | Content |
|---|---|---|---|
| Layer 1 | Component Schema | YES | 8 types, 5+3 common properties, 16 validation rules, discovery mechanism |
| Layer 2 | Composition Format | YES | 9 binding rules, 6 workflow patterns, override mechanism, placeholder resolution, ordering rules |
| Layer 3 | Output Format | YES | 3-part structure, 9 resolution rules, 12 quality requirements, 3 extraction contracts |

**Verification:** All 3 schema layers defined. VR-013 satisfied.

### Frontmatter Completeness

| Field | Value | Present |
|---|---|---|
| standard_name | WORKFLOW_BUILDER_STANDARD | YES |
| standard_version | 1.0.0 | YES |
| component_type_count | 8 | YES |
| schema_sections | [Component Schema, Composition Format, Output Format] | YES |
| domain | workflow_builder | YES |
| doc_type | composition_standard | YES |
| lifecycle_status | draft | YES |

**Verification:** All required frontmatter fields present. TC-044,
TC-045, TC-047 satisfied.

### Validation Rules Completeness

| Rule ID | Severity | Defined |
|---|---|---|
| VR-001 | CRITICAL | YES |
| VR-002 | CRITICAL | YES |
| VR-003 | CRITICAL | YES |
| VR-004 | HIGH | YES |
| VR-005 | MEDIUM | YES |
| VR-006 | CRITICAL | YES |
| VR-007 | CRITICAL | YES |
| VR-008 | CRITICAL | YES |
| VR-009 | HIGH | YES |
| VR-010 | CRITICAL | YES |
| VR-011 | HIGH | YES |
| VR-012 | CRITICAL | YES |
| VR-013 | CRITICAL | YES |
| VR-014 | HIGH | YES |
| VR-015 | CRITICAL | YES |
| VR-016 | CRITICAL | YES |

**Verification:** 16 validation rules defined. TC-011 satisfied.

### Extensibility Model Verification

| Requirement | Satisfied |
|---|---|
| Concrete description of extension procedure | YES (6 principles + 7 rules + procedure) |
| Identity stability guaranteed | YES (component_id-based references) |
| Common property stability guaranteed | YES (5+3 properties unchanged) |
| Discovery compatibility guaranteed | YES (heading scan auto-discovers) |
| Backward compatibility guaranteed | YES (additive-only changes) |

**Verification:** TC-049 satisfied.

### Criteria Traceability

| Criteria | Status | Evidence |
|---|---|---|
| TC-044 | PASS | standard_name in frontmatter: "WORKFLOW_BUILDER_STANDARD" |
| TC-045 | PASS | standard_version in frontmatter: "1.0.0" |
| TC-046 | PASS | 8 component types defined in Component Schema section |
| TC-047 | PASS | component_type_count: 8 in frontmatter, matches 8 type definitions |
| TC-048 | PASS | schema_sections: 3 layers defined with type schemas |
| TC-049 | PASS | Extensibility Model section with concrete procedure |
| TC-050 | PASS | (Gatekeep step validates this document against TC-044 to TC-049) |

**Verification:** All Phase 6 criteria (TC-044 through TC-050) are
satisfied by this document.

### Discovery Mechanism Verification

| Requirement | Satisfied |
|---|---|
| Headings match "#### Type N: {type_name}" pattern | YES |
| component_type_count in frontmatter | YES (value: 8) |
| discover_component_types function defined | YES |
| Fallback to 8 base types | YES |

**Verification:** The discover_component_types function can parse this
document and return all 8 component type names.

---

End of Composition Standard Document
