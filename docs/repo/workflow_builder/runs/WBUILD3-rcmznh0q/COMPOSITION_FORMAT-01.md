---
doc_type: "composition_format"
lifecycle_status: "draft"
layer: 2
binding_rule_count: 9
workflow_pattern_count: 6
domain: "workflow_builder"
spec_reference: "workflow_builder_v4.md"
generated_by: "generate_composition_format"
---

# Composition Format (Layer 2)

## Overview

This document defines Layer 2 of the three-layer composition architecture
for the workflow_builder domain. Layer 2 sits between Layer 1 (Component
Schema) and Layer 3 (Output Format). Its role is to define how components
from the Universal Component Schema are assembled into compositions.

Layer 1 (COMPONENT_SCHEMA-01.md) provides the building block library:
8 component types with their schemas and validation rules. Layer 2 takes
those building blocks and defines the rules for combining them.

Layer 2 answers these questions:

- What is the structure of a composition document?
- How are components bound to composition slots?
- What workflow patterns are available?
- How can component defaults be overridden?
- How are placeholder tokens resolved?
- What ordering constraints apply to step bindings?

Layer 2 does NOT answer these questions (they belong to other layers):

- What are the component types? (Layer 1)
- What files are produced? (Layer 3)
- How are files written to disk? (Layer 3)

**Layer boundaries:**
- Layer 1 is read-only authority for component types and schemas.
- Layer 2 is read-only authority for binding rules and composition structure.
- Layer 3 consumes Layer 2 output to produce files.

**Domain:** workflow_builder
**Composition format version:** 1.0.0
**Component types referenced:** 8 (from COMPONENT_SCHEMA-01.md)
**Binding rules defined:** 9 (8 base + 1 self-bootstrap)
**Workflow patterns defined:** 6

---

## Composition Structure

Every composition is a YAML document with a defined set of top-level
fields. These fields fall into three categories: identity fields,
pattern selection, and component bindings.

### Top-Level Fields

| Field | Type | Required | Description |
|---|---|---|---|
| builder_name | string | Yes | Unique builder identifier. Lowercase with underscores (e.g., workflow_builder_v3). Used as directory name in output. |
| builder_label | string | Yes | Human-readable display name (e.g., Workflow Builder v3). Used in documentation and user interfaces. |
| job_prefix | string | Yes | 4-6 character prefix for job IDs (e.g., WBUILD3). Must be uppercase alphanumeric. |
| builder_purpose | string | Yes | What this builder solves. A one-sentence description of the builder domain and goal. |
| workflow_pattern | enum | Yes | One of 6 defined patterns. Determines the overall structure of the generated workflow. |
| step_bindings | array | Yes | Ordered list of step_definition components. Defines the workflow execution sequence. |
| artifact_bindings | object | Yes | Unordered set of artifact_contract components. Defines all artifacts that flow through the workflow. |
| composition_standard_binding | object | Yes | Singleton composition_standard component. References the composition standard schema. |
| output_variances | array | No | Unordered set of output_variance components. Defines alternative output configurations. |
| domain_specs | array | No | Unordered set of domain_spec components. Defines accepted input specification types. |
| self_bootstrap_binding | object | Yes | Singleton self-bootstrap configuration. References the builder own spec for self-bootstrapping. |

### YAML Skeleton

```yaml
builder_name: "example_builder"
builder_label: "Example Builder"
job_prefix: "EXBLD"
builder_purpose: "Generates example workflows for testing"
workflow_pattern: "prompt_driven"

step_bindings:
  - step_name: "generate_output"
    step_type: "prompt"
    purpose: "Generate the primary output document"
    # ... additional step_definition properties

artifact_bindings:
  - artifact_key: "OUTPUT_FILE"
    description: "The primary output document"
    required: true
    # ... additional artifact_contract properties

composition_standard_binding:
  standard_name: "EXAMPLE_STANDARD"
  standard_version: "1.0.0"
  # ... additional composition_standard properties

output_variances: []

domain_specs:
  - spec_type: "example_spec"
    spec_version_range: "1.0.0 - 1.99.99"
    # ... additional domain_spec properties

self_bootstrap_binding:
  bootstrap_spec_key: "WORKFLOW_SPEC_FILE"
  bootstrap_spec_target: "Specs/example_builder.md"
  bootstrap_version: "1.0.0"
  next_version_pattern: "increment_major"
```

### Field Categories

**Identity fields** (builder_name, builder_label, job_prefix,
builder_purpose): These identify the builder and are used in output
directory naming, job tracking, and documentation.

**Pattern selection** (workflow_pattern): This selects one of 6
predefined workflow patterns that determines the overall structure.

**Component bindings** (step_bindings, artifact_bindings,
composition_standard_binding, output_variances, domain_specs,
self_bootstrap_binding): These bind component instances from Layer 1
to composition slots. Each binding has specific cardinality and
required status rules defined in the next section.

---

## Component Bindings

This section defines 9 binding rules that govern how the 8 component
types from Layer 1 are bound to composition slots. Eight rules map
one-to-one to the 8 component types. The ninth rule (self_bootstrap)
is a specialized binding for the domain_spec type that enables
self-bootstrapping.

### Binding Rule Summary

| Rule # | Binding Name | Component Type | Cardinality | Required |
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

### BR-001: steps (step_definition)

**Composition field:** step_bindings

**Cardinality:** Ordered list (N steps per workflow, where N >= 1).

**Required:** Yes. Every composition must define at least one step.

**Reference pattern:** Each entry is a step_definition component
instance with all required common properties plus type-specific
properties (step_name, step_type, purpose, produces,
enable_notifications, requires_human_approval_after).

**Ordering:** Steps are executed in the order they appear in the
array. The ordering must satisfy the constraints defined in the
Ordering Rules section.

**Constraints:**
- Each step must have a unique step_name (VR-006).
- step_type must be prompt or action (VR-007).
- produces must be non-empty with UPPER_SNAKE_CASE keys (VR-009).
- required_inputs must reference prior-produced artifacts (VR-012).

**Example:**

```yaml
step_bindings:
  - component_id: "step-generate_schema-01"
    component_type: "step_definition"
    name: "Generate Schema"
    version: "1.0.0"
    description: "Generate the component schema"
    step_name: "generate_schema"
    step_type: "prompt"
    purpose: "Generate the component schema for Layer 1"
    required_inputs:
      - "WORKFLOW_SPEC_FILE"
    produces:
      - "COMPONENT_SCHEMA_FILE"
    enable_notifications: false
    requires_human_approval_after: false
```

### BR-002: roles (role_policy)

**Composition field:** Inline within each step binding (embedded).

**Cardinality:** Singleton per step (exactly one role_policy per
step_definition).

**Required:** Yes. Every step must have exactly one role_policy
assignment.

**Reference pattern:** The role_policy is embedded within the step
definition using a coder sub-mapping. The policy_name must be one
of the 5 defined role policies (VR-008).

**Valid policy_name values:**
- architect_standard -- for generation steps
- reviewer_standard -- for review steps
- gatekeeper_standard -- for gatekeep steps
- validation_standard -- for deterministic validation action steps
- refine_standard -- for refinement steps

**Constraints:**
- Exactly one role_policy per step (not zero, not multiple).
- policy_name must match the step type (e.g., generation steps
  use architect_standard, review steps use reviewer_standard).

**Example:**

```yaml
step_bindings:
  - step_name: "generate_schema"
    step_type: "prompt"
    # ... other step properties
    coder:
      component_id: "role-architect_standard-01"
      component_type: "role_policy"
      name: "Architect Standard"
      version: "1.0.0"
      description: "Standard role for generation steps"
      policy_name: "architect_standard"
      assignment_rule: "Generation steps that create documents"
```

### BR-003: routing (routing_pattern)

**Composition field:** Inline within each step binding (embedded).

**Cardinality:** Singleton per step (exactly one routing_pattern per
step_definition).

**Required:** Yes. Every step must have routing defined.

**Reference pattern:** The routing_pattern is embedded within the
step definition using an onsuccess field and optional on_reject_refine
sub-mapping.

**Constraints:**
- onsuccess must reference a valid step_name in the workflow (VR-010).
- The last step in the workflow routes to step_completion.
- on_reject_refine is required for review and gatekeep steps.
- max_iterations is required if on_reject_refine is defined.

**Example:**

```yaml
step_bindings:
  - step_name: "gatekeep_schema"
    step_type: "action"
    # ... other step properties
    onsuccess: "generate_composition_format"
    on_reject_refine:
      step: "refine_component_schema"
      artifact: "COMPONENT_SCHEMA_FILE"
      max_iterations: 2
      exhausted_failure_code: "SCHEMA_GATEKEEP_EXHAUSTED"
      exhausted_failure_class: "HUMAN_RETRY_REQUIRED"
```

### BR-004: prompts (prompt_pattern)

**Composition field:** Embedded within prompt-type step bindings.

**Cardinality:** Unordered set per prompt-driven step.

**Required:** No. Only applicable to steps with step_type: prompt.
Action steps do not have prompt patterns.

**Reference pattern:** Each prompt_pattern is referenced by
pattern_name. The set of patterns determines which sections are
injected into the generated prompt template file.

**Required patterns per prompt step (VR-011):**
- self_critic -- always required
- self_validation -- always required

**Optional patterns:**
- context_verification
- reference_inputs
- generation_tasks
- forbidden_content
- output_instructions

**Constraints:**
- Every prompt step must include self_critic and self_validation.
- Patterns are unordered -- order of definition does not matter.
- Action steps must not include prompt patterns.

**Example:**

```yaml
step_bindings:
  - step_name: "generate_schema"
    step_type: "prompt"
    # ... other step properties
    prompt_patterns:
      - pattern_name: "self_critic"
        sections:
          - "Challenge your reasoning"
          - "Did you read the spec for each property"
      - pattern_name: "self_validation"
        sections:
          - "Verify all 8 component types are defined"
          - "Check validation rules are complete"
      - pattern_name: "reference_inputs"
        sections:
          - "Read WORKFLOW_SPEC_FILE before writing"
```

### BR-005: artifacts (artifact_contract)

**Composition field:** artifact_bindings

**Cardinality:** Unordered set per workflow.

**Required:** Yes. Every composition must define its artifact
contracts.

**Reference pattern:** Each entry is an artifact_contract component
with artifact_key, description, required, and optionally
filename_pattern and produced_by.

**Constraints:**
- artifact_key must be UPPER_SNAKE_CASE with _FILE suffix (VR-009).
- Every artifact consumed by a step must be produced by a prior
  step or declared as a workflow input (VR-012).
- The set is unordered -- order of definition does not matter.

**Example:**

```yaml
artifact_bindings:
  - component_id: "artifact-SCHEMA_FILE-01"
    component_type: "artifact_contract"
    name: "Schema File"
    version: "1.0.0"
    description: "Component schema for Layer 1"
    artifact_key: "COMPONENT_SCHEMA_FILE"
    filename_pattern: "COMPONENT_SCHEMA-{seq}.md"
    required: true
    produced_by: "generate_component_schema"
```

### BR-006: standard (composition_standard)

**Composition field:** composition_standard_binding

**Cardinality:** Singleton per workflow.

**Required:** Yes. Every composition must bind exactly one
composition_standard.

**Reference pattern:** The composition_standard component defines
the schema that the generated meta builder will use. It must define
all 3 schema layers (VR-013): Component Schema, Composition Format,
Output Format.

**Constraints:**
- Exactly one composition_standard per composition.
- schema_sections must contain exactly: "Component Schema",
  "Composition Format", "Output Format" (VR-013).
- component_types_defined must match the actual types used.

**Example:**

```yaml
composition_standard_binding:
  component_id: "standard-my_builder-01"
  component_type: "composition_standard"
  name: "My Builder Standard"
  version: "1.0.0"
  description: "Composition standard for my builder"
  standard_name: "MY_BUILDER_STANDARD"
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
  extensibility_model: "New types can be added without breaking existing compositions"
```

### BR-007: variances (output_variance)

**Composition field:** output_variances

**Cardinality:** Unordered set per workflow.

**Required:** No. Only used when the meta builder supports multiple
output configurations.

**Reference pattern:** Each entry is an output_variance component
with variance_name, variance_description, component_requirements,
and output_files.

**Constraints:**
- component_requirements must reference valid component types (VR-014).
- output_files must be non-empty.
- The set is unordered.

**Example:**

```yaml
output_variances:
  - component_id: "variance-prompt_only-01"
    component_type: "output_variance"
    name: "Prompt Only"
    version: "1.0.0"
    description: "Workflow with only prompt-driven steps"
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

### BR-008: domain_specs (domain_spec)

**Composition field:** domain_specs

**Cardinality:** Unordered set per workflow.

**Required:** No. Only used when the meta builder accepts external
specifications as input.

**Reference pattern:** Each entry is a domain_spec component with
spec_type, spec_version_range, required_sections, and optionally
example_specs.

**Constraints:**
- The set is unordered.
- Each spec_type must be unique within the composition.

**Example:**

```yaml
domain_specs:
  - component_id: "spec-composition_system-01"
    component_type: "domain_spec"
    name: "Composition System Spec"
    version: "1.0.0"
    description: "A composition system specification"
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
```

### BR-009: self_bootstrap (domain_spec)

**Composition field:** self_bootstrap_binding

**Cardinality:** Singleton per workflow.

**Required:** Yes. Every composition must define a self-bootstrap
binding.

**Reference pattern:** This is a specialized binding that references
the builder own spec for self-bootstrapping. It tells the builder
to embed its own input spec in the output Specs/ directory.

**Required fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| bootstrap_spec_key | string | Yes | Artifact key holding the input spec. Always "WORKFLOW_SPEC_FILE". |
| bootstrap_spec_target | string | Yes | Output path for the embedded spec. Always "Specs/{builder_name}.md". |
| bootstrap_version | string | Yes | Current builder version in MAJOR.MINOR.PATCH format. |
| next_version_pattern | string | Yes | How to derive the next version. Values: "increment_major", "increment_minor". |

**Constraints:**
- bootstrap_spec_key must always be "WORKFLOW_SPEC_FILE".
- bootstrap_spec_target must follow the pattern "Specs/{builder_name}.md".
- bootstrap_version must match the version in the composition.
- This binding enables the bootstrap chain: version N embeds its
  spec, version N+1 is generated from that embedded spec.

**Example:**

```yaml
self_bootstrap_binding:
  bootstrap_spec_key: "WORKFLOW_SPEC_FILE"
  bootstrap_spec_target: "Specs/workflow_builder_v3.md"
  bootstrap_version: "3.0.0"
  next_version_pattern: "increment_major"
```

### Binding Rule Summary by Category

**Singleton bindings** (exactly one per composition):
- BR-006: standard (composition_standard)
- BR-009: self_bootstrap (domain_spec)

**Singleton per step bindings** (one per step_definition):
- BR-002: roles (role_policy)
- BR-003: routing (routing_pattern)

**Ordered list bindings:**
- BR-001: steps (step_definition)

**Unordered set bindings:**
- BR-005: artifacts (artifact_contract)
- BR-007: variances (output_variance)
- BR-008: domain_specs (domain_spec)

**Unordered set per step bindings:**
- BR-004: prompts (prompt_pattern)

---

## Workflow Patterns

The workflow_pattern field selects one of 6 predefined patterns that
determine the overall structure of the generated workflow. Each
pattern prescribes the phase structure, step types, and routing
conventions.

### Pattern Summary

| Pattern | Phase Count | Step Types | Description |
|---|---|---|---|
| action_only | 1-3 | action | All deterministic Python operations |
| prompt_driven | 3-5 | prompt | LLM generates documents with review and refine |
| mixed | 3-7 | prompt + action | Combination of prompt and action steps |
| gatekeeper_pipeline | 5-9 | prompt + action | Multi-phase with QC gates between phases |
| meta_workflow_builder | 7-9 | prompt + action | Workflow that builds other workflows |
| meta_meta_builder | 9 | prompt + action | Workflow that builds meta builders |

### Pattern 1: action_only

**Description:** All steps are deterministic Python operations.
No LLM involvement. Used for data processing, file manipulation,
and validation pipelines.

**Structure:**
- 1-3 phases
- All steps have step_type: action
- No prompt patterns required
- Simple linear routing (no refine loops)

**Typical use cases:** Data validation, file transformation,
batch processing, deployment scripts.

**Example phase structure:**
```
Phase 1: Processing
  01 validate_input -> 02 transform_data -> 03 write_output
```

### Pattern 2: prompt_driven

**Description:** Steps are LLM-driven document generation with
human review and refinement loops. Used for content creation,
analysis, and design tasks.

**Structure:**
- 3-5 phases
- Steps have step_type: prompt
- Review and refine loops for quality control
- Prompt patterns required (self_critic, self_validation)

**Typical use cases:** Document generation, requirements analysis,
design specification, report creation.

**Example phase structure:**
```
Phase 1: Foundation
  01 generate_draft -> 02 review_draft -> [03 refine_draft]
Phase 2: Assembly
  04 compile_output -> 05 final_review
```

### Pattern 3: mixed

**Description:** Combines prompt-driven and action-driven steps in
the same workflow. Used when some steps benefit from LLM generation
while others require deterministic processing.

**Structure:**
- 3-7 phases
- Mix of prompt and action step types
- Review loops for prompt steps
- Linear routing for action steps

**Typical use cases:** Workflows that generate documents and then
validate or transform them programmatically.

**Example phase structure:**
```
Phase 1: Generation
  01 generate_document (prompt) -> 02 review_document -> [03 refine_document]
Phase 2: Processing
  04 validate_structure (action) -> 05 transform_output (action)
```

### Pattern 4: gatekeeper_pipeline

**Description:** Multi-phase workflow with quality control gates
between each phase. Each phase must pass a gatekeep check before
proceeding to the next phase. Used for high-stakes workflows where
quality must be enforced at every boundary.

**Structure:**
- 5-9 phases
- Each phase ends with a gatekeep step
- Gatekeep steps use gatekeeper_standard role
- Refine loops on gatekeep rejection
- Both prompt and action steps

**Typical use cases:** Compliance workflows, certification pipelines,
multi-stage approval processes.

**Example phase structure:**
```
Phase 1: Foundation
  01 generate_criteria -> 02 review_criteria -> [03 refine_criteria]
Phase 2: Schema
  04 generate_schema -> 05 gatekeep_schema
Phase 3: Format
  06 generate_format -> 07 gatekeep_format
```

### Pattern 5: meta_workflow_builder

**Description:** A workflow that builds other workflows. Takes a
specification as input and produces a complete executable workflow
package as output. Used for workflow generation and templating.

**Structure:**
- 7-9 phases
- Phases for analysis, design, generation, validation, and assembly
- Heavy use of prompt steps for creative generation
- Action steps for validation and file assembly
- Self-describing output (the generated workflow knows its structure)

**Typical use cases:** Template-based workflow generation, custom
workflow creation from specifications.

**Example phase structure:**
```
Phase 1: Foundation
  01 generate_test_criteria -> 02 review -> [03 refine]
Phase 2: Component Schema
  04 generate_component_schema -> 05 gatekeep
Phase 3: Composition Format
  06 generate_composition_format -> 07 gatekeep
Phase 4: Output Format
  08 generate_output_format -> 09 gatekeep
Phase 5: Assembly
  10 generate_package -> 11 validate -> 12 promote
```

### Pattern 6: meta_meta_builder

**Description:** A workflow that builds meta builders. This is the
most complex pattern. It generates composition systems that are
themselves capable of generating workflows. Supports
self-bootstrapping: the generated builder can process its own spec
to produce the next version.

**Structure:**
- 9 phases (Foundation, Component Schema, Composition Format, Output
  Format, Operational Workflow, Composition Standard, Meta Composition
  Spec, Package Assembly, Promotion)
- 22 steps across the 9 phases
- 3-part output: Standards/, Specs/, workflow package
- Self-bootstrap binding required
- Dynamic component discovery from generated standard

**Typical use cases:** Meta-meta workflow builders (e.g., Workflow
Builder v3, v4).

**Phase structure:**
```
Phase 1: Foundation (TDD Loop)
  01 generate_test_criteria -> 02 review_test_criteria -> [03 refine_test_criteria]
Phase 2: Component Schema (Layer 1)
  04 generate_component_schema -> 05 gatekeep_component_schema
Phase 3: Composition Format (Layer 2)
  06 generate_composition_format -> 07 gatekeep_composition_format
Phase 4: Output Format (Layer 3)
  08 generate_output_format -> 09 gatekeep_output_format
Phase 5: Operational Workflow
  10 generate_operational_workflow -> 11 gatekeep_operational_workflow
Phase 6: Composition Standard
  12 generate_composition_standard -> 13 gatekeep_composition_standard
Phase 7: Meta Composition Spec
  14 generate_meta_composition_spec
Phase 8: Package Assembly
  15 generate_package -> 16 embed_builder_spec -> 17 validate_package_deterministic
  -> 18 gatekeep_package -> 19 review_package -> [20 refine_package]
Phase 9: Promotion
  21 promote_workflow_package -> 22 step_completion
```

### Pattern Selection Rules

| Rule | Description |
|---|---|
| PS-001 | The workflow_pattern must be one of the 6 defined values. |
| PS-002 | The selected pattern determines the minimum and maximum phase count. |
| PS-003 | meta_meta_builder pattern requires self_bootstrap_binding. |
| PS-004 | action_only pattern must not include prompt patterns. |
| PS-005 | prompt_driven pattern must include review and refine steps. |
| PS-006 | gatekeeper_pipeline pattern must include gatekeep steps at phase boundaries. |

---

## Override Mechanism

Overrides allow per-composition customization of component properties
without modifying the original component definition. This enables
reuse of base components across different compositions while
allowing specific compositions to adjust behavior.

### Merge Semantics

Overrides use a shallow merge strategy:

1. Start with the base component properties (from Layer 1 schema).
2. Apply override values on top.
3. Override wins on conflict for type-specific properties.
4. Override wins on conflict for optional common properties
   (duration_range, platforms, tags).

### Non-Overridable Properties

The 5 required common properties CANNOT be overridden. These
properties define the identity and type of the component and must
remain stable across all compositions.

| Property | Overridable | Reason |
|---|---|---|
| component_id | No | Identity -- must remain stable for references |
| component_type | No | Type -- determines schema conformance |
| name | No | Identity -- used for display and lookup |
| version | No | Identity -- semantic version must not change |
| description | No | Identity -- describes the base component |

### Overridable Properties

Type-specific properties and optional common properties can be
overridden.

**Optional common properties (overridable):**
- duration_range -- adjust per-composition scope
- platforms -- restrict or expand target platforms
- tags -- add composition-specific classification

**Type-specific properties (overridable):**
- step_definition: purpose, enable_notifications,
  requires_human_approval_after
- role_policy: assignment_rule
- routing_pattern: max_iterations
- prompt_pattern: sections
- artifact_contract: filename_pattern
- composition_standard: extensibility_model
- output_variance: variance_description
- domain_spec: spec_version_range

### Override Syntax

Overrides are specified inline within the composition binding using
an override sub-mapping.

```yaml
step_bindings:
  - step_name: "generate_output"
    step_type: "prompt"
    # ... base properties ...
    override:
      purpose: "Customized purpose for this specific composition"
      enable_notifications: true
      duration_range: "10-20 minutes"
      tags: ["custom", "composition-specific"]
```

### Override Rules

| Rule | Description |
|---|---|
| OV-001 | Override values must conform to the type-specific schema. |
| OV-002 | Common identity properties (component_id, component_type, name, version, description) cannot be overridden. |
| OV-003 | Override values are merged shallowly -- nested structures are replaced, not deep-merged. |
| OV-004 | Override must not change the step_type of a step_definition. |
| OV-005 | Override must not change the policy_name of a role_policy. |

### Override Examples

**Example 1: Override step purpose and notifications**

```yaml
step_bindings:
  - step_name: "generate_schema"
    step_type: "prompt"
    purpose: "Generate the component schema"
    enable_notifications: false
    override:
      purpose: "Generate schema with extended type coverage"
      enable_notifications: true
```

After merge:
- purpose = "Generate schema with extended type coverage" (overridden)
- enable_notifications = true (overridden)
- step_type = "prompt" (unchanged, not overridable)

**Example 2: Override optional common properties**

```yaml
artifact_bindings:
  - artifact_key: "OUTPUT_FILE"
    description: "Primary output"
    duration_range: "5-10 minutes"
    tags: ["standard"]
    override:
      duration_range: "15-30 minutes"
      tags: ["extended", "custom"]
```

After merge:
- duration_range = "15-30 minutes" (overridden)
- tags = ["extended", "custom"] (overridden, replaces entire array)

---

## Placeholder Resolution

Compositions contain placeholder tokens written as {PLACEHOLDER_NAME}
that are resolved at workflow execution time. Placeholders allow
compositions to be written generically and instantiated with
specific values at runtime.

### Data Sources

Placeholder values come from 4 data sources, resolved in priority
order.

| Priority | Data Source | Fields Provided | Resolution Timing |
|---|---|---|---|
| 1 | Input Spec | WORKFLOW_SPEC_FILE, domain_name, builder_name, job_prefix | Loaded at workflow start |
| 2 | Governance | BASE_COMPOSITION_STANDARD, GOVERNANCE_RUNTIME_ROOT | Static paths from governance config |
| 3 | Runtime | job_id, seq, workspace_root, timestamp | Computed at execution time |
| 4 | Discovery | DISCOVERED_COMPONENT_TYPES, COMPOSITION_STANDARD_PATH | Computed after composition standard is generated |

### Data Source Details

**Source 1: Input Spec**

Fields from the input specification and composition identity:

| Placeholder | Source Field | Description |
|---|---|---|
| {WORKFLOW_SPEC_FILE} | Input artifact path | Absolute path to the input specification file |
| {domain_name} | builder_name or domain field | The domain identifier |
| {builder_name} | builder_name field | The builder identifier |
| {job_prefix} | job_prefix field | The job ID prefix |
| {builder_label} | builder_label field | Human-readable builder name |
| {builder_purpose} | builder_purpose field | Builder purpose description |

**Source 2: Governance**

Fields from the governance configuration:

| Placeholder | Source Field | Description |
|---|---|---|
| {BASE_COMPOSITION_STANDARD} | Governance config | Path to the base composition standard |
| {GOVERNANCE_RUNTIME_ROOT} | Governance config | Root directory for governance runtime |

**Source 3: Runtime**

Fields computed during workflow execution:

| Placeholder | Source Field | Description |
|---|---|---|
| {job_id} | Runtime state | Current job identifier (e.g., WBUILD3-abc123) |
| {seq} | Runtime state | Two-digit sequence number (e.g., 01, 02) |
| {workspace_root} | Runtime state | Root directory of the current workspace |
| {timestamp} | Runtime state | ISO 8601 timestamp of execution |

**Source 4: Discovery**

Fields computed from the generated composition standard:

| Placeholder | Source Field | Description |
|---|---|---|
| {DISCOVERED_COMPONENT_TYPES} | discover_component_types() | Comma-separated list of component type names |
| {COMPOSITION_STANDARD_PATH} | Runtime state | Absolute path to the generated composition standard |

### Resolution Order

1. Input Spec placeholders are resolved first (loaded from workflow
   input artifacts and composition identity fields).
2. Governance placeholders are resolved second (loaded from static
   governance configuration).
3. Runtime placeholders are resolved third (computed from execution
   context).
4. Discovery placeholders are resolved last (computed after the
   composition standard generation step completes).

If a placeholder appears in a prompt template, it must be resolved
from one of the 4 data sources. If resolution fails, the placeholder
is replaced with {UNRESOLVED: field_name} to make the failure
visible.

### Resolution Rules

| Rule | Description |
|---|---|
| PR-001 | Every {PLACEHOLDER} in a prompt template must be resolvable from one of the 4 data sources. |
| PR-002 | Input Spec fields are available to all steps. |
| PR-003 | Governance fields are available to all steps. |
| PR-004 | Runtime fields are available to all steps. |
| PR-005 | Discovery fields are available only to steps that execute after generate_composition_standard. |
| PR-006 | Unresolvable placeholders are replaced with {UNRESOLVED: field_name}. |
| PR-007 | Placeholder names use UPPER_SNAKE_CASE convention. |

---

## Ordering Rules

The step_bindings array defines an ordered execution sequence. The
following constraints must be satisfied to ensure correct workflow
execution.

### Foundation First

Steps in Phase 1 (Foundation) must appear before all other steps.
The foundation phase establishes the test criteria that subsequent
phases validate against.

| Rule | Description |
|---|---|
| OR-001 | Foundation phase steps (generate_test_criteria, review_test_criteria, refine_test_criteria) must be the first steps in step_bindings. |
| OR-002 | The refine step (if present) must appear after the review step. |

### Layer Sequence

The 3-layer architecture must be followed in order: Layer 1
(Component Schema) before Layer 2 (Composition Format) before
Layer 3 (Output Format).

| Rule | Description |
|---|---|
| OR-003 | Component Schema phase (generate + gatekeep) must appear before Composition Format phase. |
| OR-004 | Composition Format phase (generate + gatekeep) must appear before Output Format phase. |
| OR-005 | Output Format phase (generate + gatekeep) must appear before Operational Workflow phase. |

### Gatekeep After Generate

Each generate step in a gated phase must be followed by its
corresponding gatekeep step. The gatekeep step validates the
generated artifact before allowing the workflow to proceed.

| Rule | Description |
|---|---|
| OR-006 | Every gatekeep step must immediately follow its corresponding generate step (possibly with a refine loop in between). |
| OR-007 | A generate step must not be followed directly by another generate step in a gated phase -- a gatekeep step must intervene. |

### Terminal Last

The final steps in the workflow must be the promotion and
completion steps. No steps may follow step_completion.

| Rule | Description |
|---|---|
| OR-008 | promote_workflow_package must appear before step_completion. |
| OR-009 | step_completion must be the last step in step_bindings. |
| OR-010 | No step may have onsuccess routing to a step that appears earlier in the ordering (no backward jumps except refine loops). |

### Ordering Validation

The ordering constraints are validated as part of the composition
validation checks (CV-007 through CV-010).

---

## Composition Validation

The following 10 validation checks (CV-001 through CV-010) verify
that a composition document is well-formed and internally consistent.
These checks are applied by the gatekeep_composition_format step
and by downstream validation steps.

### CV-001: Required Fields Present

**Severity:** CRITICAL

All required top-level fields must be present in the composition:
builder_name, builder_label, job_prefix, builder_purpose,
workflow_pattern, step_bindings, artifact_bindings,
composition_standard_binding, self_bootstrap_binding.

### CV-002: Binding Rule Conformance

**Severity:** CRITICAL

Each of the 9 binding rules (BR-001 through BR-009) must be
satisfied. Required bindings must have at least one entry. Cardinality
constraints must be respected. Component types must match the
binding target type.

### CV-003: Workflow Pattern Validity

**Severity:** CRITICAL

The workflow_pattern field must be one of the 6 defined values:
action_only, prompt_driven, mixed, gatekeeper_pipeline,
meta_workflow_builder, meta_meta_builder.

### CV-004: Step Name Uniqueness

**Severity:** CRITICAL

No two step_bindings entries may share the same step_name value.
This enforces VR-006 at the composition level.

### CV-005: Artifact Flow Integrity

**Severity:** CRITICAL

Every artifact referenced in a step required_inputs must be produced
by a preceding step or declared as a workflow input. No dangling
references. This enforces VR-012 at the composition level.

### CV-006: Override Schema Conformance

**Severity:** HIGH

Override values must conform to the type-specific schema of the
target component. Non-overridable properties must not appear in
override blocks. This enforces OV-001 and OV-002.

### CV-007: Phase Ordering

**Severity:** CRITICAL

Steps must follow the phase ordering defined by the selected
workflow pattern. Foundation first, layer sequence respected,
gatekeep after generate, terminal last. This enforces OR-001
through OR-010.

### CV-008: Routing Completeness

**Severity:** CRITICAL

Every step must have onsuccess routing to a valid next step. The
last step routes to step_completion. Steps that support rejection
must have on_reject_refine defined. This enforces VR-010.

### CV-009: Prompt Pattern Completeness

**Severity:** HIGH

Every prompt-type step must include self_critic and self_validation
prompt patterns. This enforces VR-011 at the composition level.

### CV-010: Self-Bootstrap Consistency

**Severity:** CRITICAL

The self_bootstrap_binding must specify all 4 required fields
(bootstrap_spec_key, bootstrap_spec_target, bootstrap_version,
next_version_pattern). bootstrap_spec_key must be
"WORKFLOW_SPEC_FILE". bootstrap_spec_target must follow the
pattern "Specs/{builder_name}.md". This enforces TC-018.

---

## Example Compositions

### Example 1: Simple Prompt-Driven Builder

This composition defines a simple prompt-driven builder that
generates a requirements document from a specification input.

```yaml
builder_name: "requirements_builder"
builder_label: "Requirements Document Builder"
job_prefix: "REQBLD"
builder_purpose: "Generates requirements documents from specification inputs"
workflow_pattern: "prompt_driven"

step_bindings:
  - component_id: "step-generate_draft-01"
    component_type: "step_definition"
    name: "Generate Draft"
    version: "1.0.0"
    description: "Generate the initial requirements draft"
    step_name: "generate_draft"
    step_type: "prompt"
    purpose: "Generate the initial requirements document draft"
    required_inputs:
      - "WORKFLOW_SPEC_FILE"
    produces:
      - "DRAFT_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "architect_standard"
      assignment_rule: "Generation step"
    onsuccess: "review_draft"
    prompt_patterns:
      - pattern_name: "self_critic"
      - pattern_name: "self_validation"
      - pattern_name: "reference_inputs"

  - component_id: "step-review_draft-01"
    component_type: "step_definition"
    name: "Review Draft"
    version: "1.0.0"
    description: "Review the generated draft for quality"
    step_name: "review_draft"
    step_type: "prompt"
    purpose: "Review the draft for completeness and correctness"
    required_inputs:
      - "DRAFT_FILE"
    produces:
      - "REVIEW_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "reviewer_standard"
      assignment_rule: "Review step"
    onsuccess: "compile_output"
    on_reject_refine:
      step: "refine_draft"
      artifact: "DRAFT_FILE"
      max_iterations: 2
      exhausted_failure_code: "DRAFT_REVIEW_EXHAUSTED"
      exhausted_failure_class: "HUMAN_RETRY_REQUIRED"
    prompt_patterns:
      - pattern_name: "self_critic"
      - pattern_name: "self_validation"

  - component_id: "step-refine_draft-01"
    component_type: "step_definition"
    name: "Refine Draft"
    version: "1.0.0"
    description: "Refine the draft based on review feedback"
    step_name: "refine_draft"
    step_type: "prompt"
    purpose: "Improve the draft based on review comments"
    required_inputs:
      - "DRAFT_FILE"
      - "REVIEW_FILE"
    produces:
      - "DRAFT_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "refine_standard"
      assignment_rule: "Refinement step"
    onsuccess: "review_draft"
    prompt_patterns:
      - pattern_name: "self_critic"
      - pattern_name: "self_validation"

  - component_id: "step-compile_output-01"
    component_type: "step_definition"
    name: "Compile Output"
    version: "1.0.0"
    description: "Compile the final output document"
    step_name: "compile_output"
    step_type: "prompt"
    purpose: "Compile the reviewed draft into final output"
    required_inputs:
      - "DRAFT_FILE"
    produces:
      - "OUTPUT_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "architect_standard"
      assignment_rule: "Generation step"
    onsuccess: "step_completion"
    prompt_patterns:
      - pattern_name: "self_critic"
      - pattern_name: "self_validation"
      - pattern_name: "output_instructions"

artifact_bindings:
  - artifact_key: "WORKFLOW_SPEC_FILE"
    description: "Input specification file"
    required: true
  - artifact_key: "DRAFT_FILE"
    description: "Requirements draft document"
    filename_pattern: "DRAFT-{seq}.md"
    required: true
    produced_by: "generate_draft"
  - artifact_key: "REVIEW_FILE"
    description: "Review feedback document"
    filename_pattern: "REVIEW-{seq}.md"
    required: true
    produced_by: "review_draft"
  - artifact_key: "OUTPUT_FILE"
    description: "Final requirements document"
    filename_pattern: "OUTPUT-{seq}.md"
    required: true
    produced_by: "compile_output"

composition_standard_binding:
  standard_name: "REQUIREMENTS_BUILDER_STANDARD"
  standard_version: "1.0.0"
  component_types_defined:
    - "step_definition"
    - "role_policy"
    - "routing_pattern"
    - "prompt_pattern"
    - "artifact_contract"
    - "composition_standard"
  schema_sections:
    - "Component Schema"
    - "Composition Format"
    - "Output Format"
  extensibility_model: "New component types can be added without breaking existing compositions"

output_variances: []

domain_specs:
  - spec_type: "requirements_spec"
    spec_version_range: "1.0.0 - 2.99.99"
    required_sections:
      - "Project Overview"
      - "Functional Requirements"
      - "Non-Functional Requirements"

self_bootstrap_binding:
  bootstrap_spec_key: "WORKFLOW_SPEC_FILE"
  bootstrap_spec_target: "Specs/requirements_builder.md"
  bootstrap_version: "1.0.0"
  next_version_pattern: "increment_major"
```

### Example 2: Meta-Meta Builder (Workflow Builder v3)

This composition defines the Workflow Builder v3 meta-meta builder,
using the meta_meta_builder pattern with 9 phases and 22 steps.

```yaml
builder_name: "workflow_builder_v3"
builder_label: "Workflow Builder v3"
job_prefix: "WBUILD3"
builder_purpose: "Self-bootstrapping meta-meta builder that generates meta builders with 3-part output"
workflow_pattern: "meta_meta_builder"

step_bindings:
  - step_name: "generate_test_criteria"
    step_type: "prompt"
    purpose: "Generate acceptance criteria for the workflow"
    required_inputs:
      - "WORKFLOW_SPEC_FILE"
    produces:
      - "TEST_CRITERIA_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "architect_standard"
    onsuccess: "review_test_criteria"
    prompt_patterns:
      - pattern_name: "self_critic"
      - pattern_name: "self_validation"

  - step_name: "review_test_criteria"
    step_type: "prompt"
    purpose: "Review the generated test criteria"
    required_inputs:
      - "TEST_CRITERIA_FILE"
    produces:
      - "REVIEW_TEST_CRITERIA_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "reviewer_standard"
    onsuccess: "generate_component_schema"
    on_reject_refine:
      step: "refine_test_criteria"
      artifact: "TEST_CRITERIA_FILE"
      max_iterations: 2
      exhausted_failure_code: "TEST_CRITERIA_REVIEW_EXHAUSTED"
      exhausted_failure_class: "HUMAN_RETRY_REQUIRED"

  - step_name: "refine_test_criteria"
    step_type: "prompt"
    purpose: "Refine test criteria based on review feedback"
    required_inputs:
      - "TEST_CRITERIA_FILE"
      - "REVIEW_TEST_CRITERIA_FILE"
    produces:
      - "TEST_CRITERIA_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "refine_standard"
    onsuccess: "review_test_criteria"

  - step_name: "generate_component_schema"
    step_type: "prompt"
    purpose: "Generate the component schema for Layer 1"
    required_inputs:
      - "WORKFLOW_SPEC_FILE"
      - "TEST_CRITERIA_FILE"
    produces:
      - "COMPONENT_SCHEMA_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "architect_standard"
    onsuccess: "gatekeep_component_schema"

  - step_name: "gatekeep_component_schema"
    step_type: "action"
    purpose: "Validate component schema against test criteria"
    required_inputs:
      - "COMPONENT_SCHEMA_FILE"
      - "TEST_CRITERIA_FILE"
    produces:
      - "GATEKEEP_COMPONENT_SCHEMA_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "gatekeeper_standard"
    onsuccess: "generate_composition_format"
    on_reject_refine:
      step: "generate_component_schema"
      artifact: "COMPONENT_SCHEMA_FILE"
      max_iterations: 2
      exhausted_failure_code: "COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED"
      exhausted_failure_class: "HUMAN_RETRY_REQUIRED"

  - step_name: "generate_composition_format"
    step_type: "prompt"
    purpose: "Generate the composition format for Layer 2"
    required_inputs:
      - "WORKFLOW_SPEC_FILE"
      - "TEST_CRITERIA_FILE"
      - "COMPONENT_SCHEMA_FILE"
    produces:
      - "COMPOSITION_FORMAT_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "architect_standard"
    onsuccess: "gatekeep_composition_format"

  - step_name: "gatekeep_composition_format"
    step_type: "action"
    purpose: "Validate composition format against test criteria"
    required_inputs:
      - "COMPOSITION_FORMAT_FILE"
      - "TEST_CRITERIA_FILE"
    produces:
      - "GATEKEEP_COMPOSITION_FORMAT_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "gatekeeper_standard"
    onsuccess: "generate_output_format"
    on_reject_refine:
      step: "generate_composition_format"
      artifact: "COMPOSITION_FORMAT_FILE"
      max_iterations: 2
      exhausted_failure_code: "COMPOSITION_FORMAT_GATEKEEP_EXHAUSTED"
      exhausted_failure_class: "HUMAN_RETRY_REQUIRED"

  - step_name: "generate_output_format"
    step_type: "prompt"
    purpose: "Generate the output format for Layer 3"
    required_inputs:
      - "WORKFLOW_SPEC_FILE"
      - "COMPOSITION_FORMAT_FILE"
    produces:
      - "OUTPUT_FORMAT_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "architect_standard"
    onsuccess: "gatekeep_output_format"

  - step_name: "gatekeep_output_format"
    step_type: "action"
    purpose: "Validate output format against test criteria"
    required_inputs:
      - "OUTPUT_FORMAT_FILE"
      - "TEST_CRITERIA_FILE"
    produces:
      - "GATEKEEP_OUTPUT_FORMAT_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "gatekeeper_standard"
    onsuccess: "generate_operational_workflow"

  - step_name: "generate_operational_workflow"
    step_type: "prompt"
    purpose: "Generate the operational workflow design"
    required_inputs:
      - "WORKFLOW_SPEC_FILE"
      - "OUTPUT_FORMAT_FILE"
    produces:
      - "OPERATIONAL_WORKFLOW_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "architect_standard"
    onsuccess: "gatekeep_operational_workflow"

  - step_name: "gatekeep_operational_workflow"
    step_type: "action"
    purpose: "Validate operational workflow against test criteria"
    required_inputs:
      - "OPERATIONAL_WORKFLOW_FILE"
      - "TEST_CRITERIA_FILE"
    produces:
      - "GATEKEEP_OPERATIONAL_WORKFLOW_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "gatekeeper_standard"
    onsuccess: "generate_composition_standard"

  - step_name: "generate_composition_standard"
    step_type: "prompt"
    purpose: "Generate the composition standard"
    required_inputs:
      - "WORKFLOW_SPEC_FILE"
      - "COMPONENT_SCHEMA_FILE"
      - "COMPOSITION_FORMAT_FILE"
      - "OUTPUT_FORMAT_FILE"
    produces:
      - "COMPOSITION_STANDARD_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "architect_standard"
    onsuccess: "gatekeep_composition_standard"

  - step_name: "gatekeep_composition_standard"
    step_type: "action"
    purpose: "Validate composition standard"
    required_inputs:
      - "COMPOSITION_STANDARD_FILE"
      - "TEST_CRITERIA_FILE"
    produces:
      - "GATEKEEP_COMPOSITION_STANDARD_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "gatekeeper_standard"
    onsuccess: "generate_meta_composition_spec"

  - step_name: "generate_meta_composition_spec"
    step_type: "prompt"
    purpose: "Generate the meta composition specification"
    required_inputs:
      - "WORKFLOW_SPEC_FILE"
      - "COMPOSITION_STANDARD_FILE"
    produces:
      - "META_COMPOSITION_SPEC_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "architect_standard"
    onsuccess: "generate_package"

  - step_name: "generate_package"
    step_type: "prompt"
    purpose: "Generate the complete workflow package"
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
    coder:
      policy_name: "architect_standard"
    onsuccess: "embed_builder_spec"

  - step_name: "embed_builder_spec"
    step_type: "action"
    purpose: "Copy the input spec to the output Specs directory"
    required_inputs:
      - "WORKFLOW_SPEC_FILE"
      - "WORKFLOW_MANIFEST_FILE"
    produces:
      - "SPECS_BUILDER_SPEC_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "validation_standard"
    onsuccess: "validate_package_deterministic"

  - step_name: "validate_package_deterministic"
    step_type: "action"
    purpose: "Run deterministic validation checks on the package"
    required_inputs:
      - "WORKFLOW_MANIFEST_FILE"
      - "WORKFLOW_EXTENSIONS_FILE"
      - "WORKFLOW_ACTIONS_FILE"
      - "STANDARDS_COMPOSITION_STANDARD_FILE"
      - "SPECS_BUILDER_SPEC_FILE"
    produces:
      - "VALIDATION_REPORT_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "validation_standard"
    onsuccess: "gatekeep_package"

  - step_name: "gatekeep_package"
    step_type: "action"
    purpose: "Gatekeep the generated package"
    required_inputs:
      - "VALIDATION_REPORT_FILE"
      - "TEST_CRITERIA_FILE"
    produces:
      - "GATEKEEP_PACKAGE_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "gatekeeper_standard"
    onsuccess: "review_package"

  - step_name: "review_package"
    step_type: "prompt"
    purpose: "Final review of the generated package"
    required_inputs:
      - "WORKFLOW_MANIFEST_FILE"
      - "VALIDATION_REPORT_FILE"
      - "GATEKEEP_PACKAGE_FILE"
    produces:
      - "REVIEW_FILE_SUGGESTED"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "reviewer_standard"
    onsuccess: "promote_workflow_package"
    on_reject_refine:
      step: "refine_package"
      artifact: "REVIEW_FILE_SUGGESTED"
      max_iterations: 2
      exhausted_failure_code: "PACKAGE_REVIEW_EXHAUSTED"
      exhausted_failure_class: "HUMAN_RETRY_REQUIRED"

  - step_name: "refine_package"
    step_type: "prompt"
    purpose: "Refine the package based on review feedback"
    required_inputs:
      - "REVIEW_FILE_SUGGESTED"
      - "WORKFLOW_MANIFEST_FILE"
    produces:
      - "WORKFLOW_MANIFEST_FILE"
      - "WORKFLOW_EXTENSIONS_FILE"
      - "WORKFLOW_ACTIONS_FILE"
      - "STANDARDS_COMPOSITION_STANDARD_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "refine_standard"
    onsuccess: "embed_builder_spec"

  - step_name: "promote_workflow_package"
    step_type: "action"
    purpose: "Promote the workflow package to the workflows directory"
    required_inputs:
      - "WORKFLOW_MANIFEST_FILE"
    produces:
      - "WORKFLOW_PACKAGE_DIR_FILE"
    enable_notifications: false
    requires_human_approval_after: false
    coder:
      policy_name: "validation_standard"
    onsuccess: "step_completion"

  - step_name: "step_completion"
    step_type: "action"
    purpose: "Mark the workflow as complete"
    required_inputs:
      - "WORKFLOW_PACKAGE_DIR_FILE"
    produces: []
    enable_notifications: true
    requires_human_approval_after: false
    coder:
      policy_name: "validation_standard"
    onsuccess: "step_completion"

artifact_bindings:
  - artifact_key: "WORKFLOW_SPEC_FILE"
    description: "Composition system specification input"
    required: true
  - artifact_key: "TEST_CRITERIA_FILE"
    description: "Acceptance criteria for the workflow"
    filename_pattern: "TEST_CRITERIA-{seq}.md"
    required: true
    produced_by: "generate_test_criteria"
  - artifact_key: "REVIEW_TEST_CRITERIA_FILE"
    description: "Review of test criteria"
    filename_pattern: "REVIEW_TEST_CRITERIA-{seq}.md"
    required: true
    produced_by: "review_test_criteria"
  - artifact_key: "COMPONENT_SCHEMA_FILE"
    description: "Component schema for Layer 1"
    filename_pattern: "COMPONENT_SCHEMA-{seq}.md"
    required: true
    produced_by: "generate_component_schema"
  - artifact_key: "GATEKEEP_COMPONENT_SCHEMA_FILE"
    description: "Gatekeep result for component schema"
    filename_pattern: "GATEKEEP_COMPONENT_SCHEMA-{seq}.md"
    required: true
    produced_by: "gatekeep_component_schema"
  - artifact_key: "COMPOSITION_FORMAT_FILE"
    description: "Composition format for Layer 2"
    filename_pattern: "COMPOSITION_FORMAT-{seq}.md"
    required: true
    produced_by: "generate_composition_format"
  - artifact_key: "GATEKEEP_COMPOSITION_FORMAT_FILE"
    description: "Gatekeep result for composition format"
    filename_pattern: "GATEKEEP_COMPOSITION_FORMAT-{seq}.md"
    required: true
    produced_by: "gatekeep_composition_format"
  - artifact_key: "OUTPUT_FORMAT_FILE"
    description: "Output format for Layer 3"
    filename_pattern: "OUTPUT_FORMAT-{seq}.md"
    required: true
    produced_by: "generate_output_format"
  - artifact_key: "GATEKEEP_OUTPUT_FORMAT_FILE"
    description: "Gatekeep result for output format"
    filename_pattern: "GATEKEEP_OUTPUT_FORMAT-{seq}.md"
    required: true
    produced_by: "gatekeep_output_format"
  - artifact_key: "OPERATIONAL_WORKFLOW_FILE"
    description: "Operational workflow design"
    filename_pattern: "OPERATIONAL_WORKFLOW-{seq}.md"
    required: true
    produced_by: "generate_operational_workflow"
  - artifact_key: "GATEKEEP_OPERATIONAL_WORKFLOW_FILE"
    description: "Gatekeep result for operational workflow"
    filename_pattern: "GATEKEEP_OPERATIONAL_WORKFLOW-{seq}.md"
    required: true
    produced_by: "gatekeep_operational_workflow"
  - artifact_key: "COMPOSITION_STANDARD_FILE"
    description: "Composition standard"
    filename_pattern: "COMPOSITION_STANDARD-{seq}.md"
    required: true
    produced_by: "generate_composition_standard"
  - artifact_key: "GATEKEEP_COMPOSITION_STANDARD_FILE"
    description: "Gatekeep result for composition standard"
    filename_pattern: "GATEKEEP_COMPOSITION_STANDARD-{seq}.md"
    required: true
    produced_by: "gatekeep_composition_standard"
  - artifact_key: "META_COMPOSITION_SPEC_FILE"
    description: "Meta composition specification"
    filename_pattern: "META_COMPOSITION_SPEC-{seq}.md"
    required: true
    produced_by: "generate_meta_composition_spec"
  - artifact_key: "WORKFLOW_MANIFEST_FILE"
    description: "workflow.toml manifest"
    required: true
    produced_by: "generate_package"
  - artifact_key: "WORKFLOW_EXTENSIONS_FILE"
    description: "context_extensions.py"
    required: true
    produced_by: "generate_package"
  - artifact_key: "WORKFLOW_ACTIONS_FILE"
    description: "actions.py"
    required: true
    produced_by: "generate_package"
  - artifact_key: "WORKFLOW_PROMPTS_INDEX_FILE"
    description: "Prompts index"
    required: true
    produced_by: "generate_package"
  - artifact_key: "WORKFLOW_README_FILE"
    description: "README.md"
    required: true
    produced_by: "generate_package"
  - artifact_key: "STANDARDS_COMPOSITION_STANDARD_FILE"
    description: "Standards/COMPOSITION_STANDARD.md"
    required: true
    produced_by: "generate_package"
  - artifact_key: "SPECS_BUILDER_SPEC_FILE"
    description: "Specs/{builder_name}.md embedded spec"
    required: true
    produced_by: "embed_builder_spec"
  - artifact_key: "VALIDATION_REPORT_FILE"
    description: "Validation report from deterministic checks"
    filename_pattern: "VALIDATION_REPORT-{seq}.md"
    required: true
    produced_by: "validate_package_deterministic"
  - artifact_key: "GATEKEEP_PACKAGE_FILE"
    description: "Gatekeep result for package"
    filename_pattern: "GATEKEEP_PACKAGE-{seq}.md"
    required: true
    produced_by: "gatekeep_package"
  - artifact_key: "REVIEW_FILE_SUGGESTED"
    description: "Final review of the package"
    filename_pattern: "REVIEW-{seq}.md"
    required: true
    produced_by: "review_package"
  - artifact_key: "WORKFLOW_PACKAGE_DIR_FILE"
    description: "Promoted workflow directory path"
    required: true
    produced_by: "promote_workflow_package"

composition_standard_binding:
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

output_variances: []

domain_specs:
  - spec_type: "composition_system_spec"
    spec_version_range: "1.0.0 - 4.99.99"
    required_sections:
      - "Domain Overview"
      - "Component Schema"
      - "Composition Format"
      - "Output Format"
      - "Operational Requirements"

self_bootstrap_binding:
  bootstrap_spec_key: "WORKFLOW_SPEC_FILE"
  bootstrap_spec_target: "Specs/workflow_builder_v3.md"
  bootstrap_version: "3.0.0"
  next_version_pattern: "increment_major"
```

---

## Self-Validation

### Binding Rule Completeness

| Rule # | Binding Name | Component Type | Defined | Cardinality | Required Status |
|---|---|---|---|---|---|
| BR-001 | steps | step_definition | YES | Ordered list | Yes |
| BR-002 | roles | role_policy | YES | Singleton per step | Yes |
| BR-003 | routing | routing_pattern | YES | Singleton per step | Yes |
| BR-004 | prompts | prompt_pattern | YES | Unordered set per prompt step | No |
| BR-005 | artifacts | artifact_contract | YES | Unordered set | Yes |
| BR-006 | standard | composition_standard | YES | Singleton | Yes |
| BR-007 | variances | output_variance | YES | Unordered set | No |
| BR-008 | domain_specs | domain_spec | YES | Unordered set | No |
| BR-009 | self_bootstrap | domain_spec | YES | Singleton | Yes |

**Verification:** 9 binding rules defined. 8 component types covered.
TC-017 satisfied (8 base bindings + self_bootstrap = 9 total).

### Binding Category Verification

| Category | Bindings | Count |
|---|---|---|
| Singleton | standard, self_bootstrap | 2 |
| Singleton per step | roles, routing | 2 |
| Ordered list | steps | 1 |
| Unordered set | artifacts, variances, domain_specs | 3 |
| Unordered set per step | prompts | 1 |
| Total | | 9 |

### Workflow Pattern Completeness

| Pattern | Defined | Description |
|---|---|---|
| action_only | YES | All deterministic Python operations |
| prompt_driven | YES | LLM generates documents with review/refine |
| mixed | YES | Combination of prompt and action steps |
| gatekeeper_pipeline | YES | Multi-phase with QC gates |
| meta_workflow_builder | YES | Workflow that builds workflows |
| meta_meta_builder | YES | Workflow that builds meta builders |

**Verification:** 6 workflow patterns defined. TC-019 satisfied.
meta_meta_builder pattern is included.

### Override Mechanism Verification

| Requirement | Satisfied |
|---|---|
| Merge semantics defined | YES (shallow merge) |
| Non-overridable properties listed | YES (5 common identity properties) |
| Overridable properties listed | YES (type-specific + optional common) |
| Override syntax with example | YES (2 examples) |
| Override rules defined | YES (OV-001 through OV-005) |

**Verification:** TC-020 satisfied.

### Placeholder Resolution Verification

| Data Source | Fields | Resolution Timing |
|---|---|---|
| Input Spec | WORKFLOW_SPEC_FILE, domain_name, builder_name, job_prefix | Loaded at start |
| Governance | BASE_COMPOSITION_STANDARD, GOVERNANCE_RUNTIME_ROOT | Static paths |
| Runtime | job_id, seq, workspace_root, timestamp | Computed at execution |
| Discovery | DISCOVERED_COMPONENT_TYPES, COMPOSITION_STANDARD_PATH | Computed after standard generation |

**Verification:** 4 data sources defined. TC-021 satisfied.
Resolution order defined. Unresolved handling defined.

### Ordering Rules Verification

| Rule | Category | Defined |
|---|---|---|
| OR-001, OR-002 | Foundation First | YES |
| OR-003, OR-004, OR-005 | Layer Sequence | YES |
| OR-006, OR-007 | Gatekeep After Generate | YES |
| OR-008, OR-009, OR-010 | Terminal Last | YES |

**Verification:** 10 ordering rules defined across 4 categories.
TC-022 satisfied.

### Composition Validation Verification

| Check | Severity | Defined |
|---|---|---|
| CV-001: Required Fields | CRITICAL | YES |
| CV-002: Binding Conformance | CRITICAL | YES |
| CV-003: Pattern Validity | CRITICAL | YES |
| CV-004: Step Name Uniqueness | CRITICAL | YES |
| CV-005: Artifact Flow | CRITICAL | YES |
| CV-006: Override Conformance | HIGH | YES |
| CV-007: Phase Ordering | CRITICAL | YES |
| CV-008: Routing Completeness | CRITICAL | YES |
| CV-009: Prompt Patterns | HIGH | YES |
| CV-010: Self-Bootstrap | CRITICAL | YES |

**Verification:** 10 validation checks defined (CV-001 through
CV-010).

### Example Completeness

| Example | Pattern | Steps | Artifacts | Complete |
|---|---|---|---|---|
| Requirements Builder | prompt_driven | 4 | 4 | YES |
| Workflow Builder v3 | meta_meta_builder | 22 | 25 | YES |

**Verification:** 2 complete example compositions provided.

### Criteria Traceability

| Criteria | Status | Evidence |
|---|---|---|
| TC-017 | PASS | 9 binding rules defined (BR-001 through BR-009) |
| TC-018 | PASS | self_bootstrap binding has 4 required fields |
| TC-019 | PASS | 6 workflow patterns defined, including meta_meta_builder |
| TC-020 | PASS | Override mechanism with merge semantics and examples |
| TC-021 | PASS | 4 data sources: Input Spec, Governance, Runtime, Discovery |
| TC-022 | PASS | Ordering rules with 4 categories and 10 rules |

**Verification:** All Phase 3 criteria (TC-017 through TC-022) are
satisfied by this document.

---

End of Composition Format Document
