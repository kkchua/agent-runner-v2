---
doc_type: "composition_format"
lifecycle_status: "draft"
layer: 2
binding_rule_count: 9
workflow_pattern_count: 6
domain: "workflow_builder"
spec_reference: "workflow_builder_v4.md"
generated_by: "generate_composition_format"
composition_validation_count: 10
---

# Composition Format (Layer 2)

## Overview

This document defines the Layer 2 Composition Format for the
workflow_builder domain within the three-layer composition
architecture. Layer 2 specifies how the atomic components defined
in Layer 1 (COMPONENT_SCHEMA.md) are assembled into concrete
compositions that drive meta builder generation.

**Layer role:** Layer 2 bridges Layer 1 (component building blocks)
and Layer 3 (output format). It defines the binding rules that
connect component instances to composition fields, the workflow
patterns that determine step sequencing, the override mechanism
for composition-time customization, and the placeholder resolution
system that injects runtime values into templates.

**Domain:** workflow_builder
**Layer:** 2 (Composition Format)
**Binding rules defined:** 9 (8 base + 1 self_bootstrap)
**Workflow patterns defined:** 6
**Composition validation checks:** 10 (CV-001 through CV-010)
**Placeholder data sources:** 4 (Input Spec, Governance, Runtime, Discovery)

**Layer boundaries:**
- Layer 1 (COMPONENT_SCHEMA.md) is read-only. This document
  references the 8 component types and 16 validation rules
  defined there without redefining or extending them.
- Layer 3 (OUTPUT_FORMAT.md) consumes the bindings defined
  here to produce the 3-part output structure.

---

## Composition Structure

Every composition for the workflow_builder domain is a YAML document
with the following top-level fields. Each field binds to one or more
component types from Layer 1.

| Field | Type | Required | Description |
|---|---|---|---|
| builder_name | string | Yes | Unique builder identifier. Must be lowercase_with_underscores. Used to derive directory names, artifact paths, and the self-bootstrap spec filename. |
| builder_label | string | Yes | Human-readable display name for the builder. Used in documentation and user interfaces. |
| job_prefix | string | Yes | 4-6 character uppercase prefix for job IDs. Example: "WBUILD3", "WBUILD4". |
| builder_purpose | string | Yes | A detailed description of what problem this builder solves. Must explain the domain, the input type, and the expected output. |
| workflow_pattern | enum | Yes | One of the 6 defined workflow patterns (see Workflow Patterns section). Determines the step sequencing template. |
| step_bindings | array | Yes | Ordered array of step_definition component instances. The array order determines execution sequence. |
| artifact_bindings | object | Yes | Input and output artifact contracts for the composition. Each key maps to an artifact_contract component instance. |
| composition_standard_binding | object | Yes | References the composition_standard component that defines the generated meta builder's own component types. |
| self_bootstrap_binding | object | Yes | Defines how the builder references its own spec for self-bootstrapping. Contains exactly 4 fields (see Self-Bootstrap Binding section). |
| output_variances | array | No | Array of output_variance component instances. Each defines an alternative output configuration. |
| domain_specs | array | No | Array of domain_spec component instances. Each defines a type of user-provided specification the builder can process. |

**Required field count:** 8 required fields (builder_name, builder_label,
job_prefix, builder_purpose, workflow_pattern, step_bindings,
artifact_bindings, composition_standard_binding) plus 1 mandatory
self_bootstrap_binding, plus 2 optional fields (output_variances,
domain_specs).

**Example skeleton:**

```yaml
builder_name: "workflow_builder_v4"
builder_label: "Workflow Builder v4"
job_prefix: "WBUILD4"
builder_purpose: "Self-bootstrapping meta-meta builder that generates meta builders with 3-part output"
workflow_pattern: "meta_meta_builder"
step_bindings:
  - step_name: "generate_test_criteria"
    step_type: "prompt"
    # ... (step_definition properties)
artifact_bindings:
  input_artifacts:
    - artifact_key: "WORKFLOW_SPEC_FILE"
      # ...
  output_artifacts:
    - artifact_key: "COMPOSITION_FORMAT_FILE"
      # ...
composition_standard_binding:
  standard_name: "WORKFLOW_BUILDER_STANDARD"
  # ...
self_bootstrap_binding:
  bootstrap_spec_key: "WORKFLOW_SPEC_FILE"
  bootstrap_spec_target: "Specs/workflow_builder_v4.md"
  bootstrap_version: "4.0.0"
  next_version_pattern: "increment_major"
output_variances:
  - variance_name: "full_meta_builder"
    # ...
domain_specs:
  - spec_type: "composition_system_spec"
    # ...
```

---

## Component Bindings

This section defines the 9 binding rules that connect the 8 component
types from Layer 1 to the composition structure fields defined above.
Each rule specifies the binding name, the component type it binds to,
the cardinality constraint, whether it is required, and a description
of the binding semantics.

The 8 base bindings (one per component type) plus the additional
self_bootstrap binding (a specialized binding for domain_spec that
enables the self-bootstrapping capability) yield 9 total binding rules.

### Binding Rule 1: steps

| Property | Value |
|---|---|
| Binding name | steps |
| Component type | step_definition |
| Cardinality | Ordered list |
| Required | Yes |
| Reference pattern | step_bindings array in composition YAML |

**Description:** Binds step_definition components to the step_bindings
array. The array order determines the execution sequence of the
workflow. Each element in the array is a complete step_definition
instance with all required type-specific properties. At least one
step_definition must be present.

**Constraints:**
- Array order is significant -- position determines execution order.
- Each step_definition must have a unique step_name (VR-006).
- Every step must have a valid step_type of "prompt" or "action" (VR-007).

### Binding Rule 2: roles

| Property | Value |
|---|---|
| Binding name | roles |
| Component type | role_policy |
| Cardinality | Singleton per step |
| Required | Yes |
| Reference pattern | Embedded within each step_definition in step_bindings |

**Description:** Binds exactly one role_policy component to each
step_definition. The role_policy determines which coder backend and
instruction set handles the step execution. Every step must have
exactly one role_policy -- no step may be unassigned.

**Constraints:**
- Each step_definition must have exactly one role_policy (no more, no fewer).
- The policy_name must be one of the 5 valid values (VR-008).
- Typical assignments: architect_standard for generation steps,
  reviewer_standard for review steps, gatekeeper_standard for gatekeep
  steps, validation_standard for deterministic action steps,
  refine_standard for refinement steps.

### Binding Rule 3: routing

| Property | Value |
|---|---|
| Binding name | routing |
| Component type | routing_pattern |
| Cardinality | Singleton per step |
| Required | Yes |
| Reference pattern | Embedded within each step_definition in step_bindings |

**Description:** Binds exactly one routing_pattern component to each
step_definition. The routing_pattern controls the flow of execution
including the success path, reject-refine loops, and terminal failure
conditions.

**Constraints:**
- Each step_definition must have exactly one routing_pattern.
- The onsuccess field must reference a valid step_name that exists in
  the step_bindings (VR-010).
- If on_reject_refine is defined, it must include step, artifact,
  max_iterations, exhausted_failure_code, and exhausted_failure_class.
- The last step in the workflow may use a terminal routing pattern
  (onsuccess references step_completion or has no next step).

### Binding Rule 4: prompts

| Property | Value |
|---|---|
| Binding name | prompts |
| Component type | prompt_pattern |
| Cardinality | Unordered set per prompt step |
| Required | No |
| Reference pattern | Applied to prompt-type steps only |

**Description:** Binds prompt_pattern components to prompt-type
step_definitions. Each prompt-type step may have zero or more
prompt_patterns that define the structural sections injected into
the prompt template. The patterns are unordered -- their application
order is determined by the pattern_name enumeration, not by array
position.

**Constraints:**
- Only applicable to steps where step_type is "prompt". Action-type
  steps do not use prompt_patterns.
- Every prompt-type step must include at minimum the self_critic and
  self_validation patterns (VR-011).
- Valid pattern_name values: self_critic, self_validation,
  context_verification, reference_inputs, generation_tasks,
  forbidden_content, output_instructions.

### Binding Rule 5: artifacts

| Property | Value |
|---|---|
| Binding name | artifacts |
| Component type | artifact_contract |
| Cardinality | Unordered set |
| Required | Yes |
| Reference pattern | artifact_bindings object in composition YAML |

**Description:** Binds artifact_contract components to the
artifact_bindings object. Artifacts define the named files that
flow through the workflow. Each artifact_contract specifies the key,
format, and ownership of a single artifact.

**Constraints:**
- Every artifact_key must be UPPER_SNAKE_CASE with _FILE suffix for
  document artifacts (VR-009).
- Input artifacts must be declared at the workflow level and be
  available to all steps that reference them.
- Output artifacts must be produced by exactly one step (VR-012).
- Every required_inputs entry in a step must reference either a
  workflow-level input artifact or an artifact produced by a
  preceding step.

### Binding Rule 6: standard

| Property | Value |
|---|---|
| Binding name | standard |
| Component type | composition_standard |
| Cardinality | Singleton |
| Required | Yes |
| Reference pattern | composition_standard_binding object in composition YAML |

**Description:** Binds exactly one composition_standard component to
the composition_standard_binding field. This defines the composition
standard schema for the generated meta builder. It is the bridge
between Layer 1 (components) and the higher layers.

**Constraints:**
- Exactly one composition_standard per composition (singleton).
- The schema_sections must contain exactly 3 entries: "Component
  Schema", "Composition Format", "Output Format" (VR-013).
- The standard_name must uniquely identify the standard.
- The component_types_defined array must list all component types
  that the generated meta builder will use.

### Binding Rule 7: variances

| Property | Value |
|---|---|
| Binding name | variances |
| Component type | output_variance |
| Cardinality | Unordered set |
| Required | No |
| Reference pattern | output_variances array in composition YAML |

**Description:** Binds output_variance components to the
output_variances array. Each variance defines an alternative output
configuration the meta builder can produce. When no variances are
defined, the builder uses the default output configuration.

**Constraints:**
- Each variance_name must be unique within the composition.
- Each variance's component_requirements must reference only valid
  component types from the 8 base types (VR-014).
- The output_files array must be non-empty.

### Binding Rule 8: domain_specs

| Property | Value |
|---|---|
| Binding name | domain_specs |
| Component type | domain_spec |
| Cardinality | Unordered set |
| Required | No |
| Reference pattern | domain_specs array in composition YAML |

**Description:** Binds domain_spec components to the domain_specs
array. Each domain_spec defines a type of user-provided specification
the meta builder can process. This allows the builder to validate
incoming specs against expected structure before processing.

**Constraints:**
- Each spec_type must be unique within the composition.
- The spec_version_range must be a valid semantic version range.
- The required_sections array must list all sections the input
  specification must contain.

### Binding Rule 9: self_bootstrap

| Property | Value |
|---|---|
| Binding name | self_bootstrap |
| Component type | domain_spec |
| Cardinality | Singleton |
| Required | Yes |
| Reference pattern | self_bootstrap_binding object in composition YAML |

**Description:** Binds a specialized domain_spec configuration to the
self_bootstrap_binding field. This binding tells the builder how to
reference its own specification for self-bootstrapping. The builder
takes the input WORKFLOW_SPEC_FILE and embeds it into the output's
Specs/ directory, enabling the next version to use the embedded spec
as input.

**Constraints:**
- Exactly one self_bootstrap binding per composition.
- The bootstrap_spec_key must always be "WORKFLOW_SPEC_FILE".
- The bootstrap_spec_target must follow the pattern
  "Specs/{builder_name}.md".
- The bootstrap_version must match the builder's current version.
- The next_version_pattern must specify how to derive the next
  version (e.g., "increment_major", "increment_minor").

**Binding Rules Summary Table:**

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

---

## Workflow Patterns

This section defines the 6 workflow patterns available for use in
the workflow_pattern field of a composition. Each pattern determines
the step sequencing template and the structural characteristics of
the generated workflow.

### Pattern 1: action_only

| Property | Value |
|---|---|
| Pattern name | action_only |
| Description | All steps are deterministic Python operations. No LLM-driven prompt steps. |
| When to use | When the entire workflow can be expressed as a sequence of deterministic actions (file copies, validations, scans, promotions). No content generation is needed. |
| Step sequence | All steps have step_type "action". Typical sequence: validate -> process -> validate -> promote. |
| Typical step count | 3-8 steps |
| Gatekeeper steps | May include gatekeep steps for deterministic validation. |
| Review/refine loops | None (no LLM output to review). |

### Pattern 2: prompt_driven

| Property | Value |
|---|---|
| Pattern name | prompt_driven |
| Description | All steps are LLM-driven prompt steps with review and refine loops. |
| When to use | When the workflow produces documents, designs, or specifications that require LLM generation and quality review. |
| Step sequence | generate -> review -> refine (conditional) -> gatekeep. Each phase has its own generate-review-refine loop. |
| Typical step count | 5-12 steps |
| Gatekeeper steps | May include gatekeep steps for quality threshold enforcement. |
| Review/refine loops | Yes, for each generation step. Max iterations typically 2-3. |

### Pattern 3: mixed

| Property | Value |
|---|---|
| Pattern name | mixed |
| Description | Combination of prompt-driven and action steps. Some steps use LLM generation, others are deterministic. |
| When to use | When the workflow includes both content generation (LLM) and deterministic processing (validation, file operations). |
| Step sequence | Interleaved prompt and action steps. Typical: generate (prompt) -> validate (action) -> gatekeep (action) -> generate (prompt). |
| Typical step count | 6-15 steps |
| Gatekeeper steps | Action-type gatekeep steps for validation. |
| Review/refine loops | Yes, for prompt-type steps. Action steps route directly. |

### Pattern 4: gatekeeper_pipeline

| Property | Value |
|---|---|
| Pattern name | gatekeeper_pipeline |
| Description | Multi-phase pipeline with quality gates between phases. Each phase produces artifacts that are validated before the next phase begins. |
| When to use | When the workflow has distinct phases with clear boundaries and quality requirements between them. Each phase's output must pass validation before the next phase starts. |
| Step sequence | Phase 1: generate -> gatekeep. Phase 2: generate -> gatekeep. ... Final: promote. |
| Typical step count | 8-20 steps |
| Gatekeeper steps | Multiple gatekeep steps, one per phase boundary. |
| Review/refine loops | Yes, gatekeep steps can reject back to the generate step in the same phase. |

### Pattern 5: meta_workflow_builder

| Property | Value |
|---|---|
| Pattern name | meta_workflow_builder |
| Description | A workflow that builds other workflows. Follows the universal meta-workflow skeleton with the standard phase structure. |
| When to use | When generating a domain-specific workflow builder that produces concrete workflows for a particular domain. |
| Step sequence | Foundation (TDD) -> Requirements -> Artifacts -> Steps -> Package (generate, gatekeep, review, refine) -> Promotion. |
| Typical step count | 12-18 steps |
| Gatekeeper steps | 4+ gatekeep steps for each layer boundary. |
| Review/refine loops | Yes, at the package assembly phase. |

### Pattern 6: meta_meta_builder

| Property | Value |
|---|---|
| Pattern name | meta_meta_builder |
| Description | A workflow that builds meta builders (composition system workflows). Generates 3-part output: composition standard, builder spec, and workflow package. Self-bootstrapping capable. |
| When to use | When generating a composition system workflow that itself generates other workflows. The output includes its own composition standard enabling self-bootstrapping. |
| Step sequence | Foundation (TDD) -> Component Schema (Layer 1) -> Composition Format (Layer 2) -> Output Format (Layer 3) -> Operational Workflow -> Composition Standard -> Meta Composition Spec -> Package Assembly (generate, embed_spec, validate, gatekeep, review, refine) -> Promotion. |
| Typical step count | 20-24 steps |
| Gatekeeper steps | 6 gatekeep steps (one per layer phase) plus package gatekeep. |
| Review/refine loops | Yes, at foundation phase and package assembly phase. |
| Special features | embed_builder_spec step for self-bootstrapping. Dynamic component discovery from generated standard. |

**Workflow Patterns Summary Table:**

| # | Pattern | Type | Description |
|---|---|---|---|
| 1 | action_only | Deterministic | All Python operations, no LLM |
| 2 | prompt_driven | LLM | All prompt steps with review loops |
| 3 | mixed | Hybrid | Combination of prompt and action |
| 4 | gatekeeper_pipeline | Multi-phase | Phase boundaries with quality gates |
| 5 | meta_workflow_builder | Meta | Builds concrete workflows |
| 6 | meta_meta_builder | Meta-meta | Builds meta builders with self-bootstrap |

---

## Override Mechanism

The override mechanism allows per-composition customization of
component properties without modifying the original component
definitions from Layer 1. Overrides are applied at composition
time and merge with the base component properties.

### Merge Semantics

When a composition specifies an override for a component instance,
the override values are merged with the base component properties
using the following rules:

1. **Override wins on conflict:** If the override specifies a value
   for a property that also exists in the base component, the
   override value takes precedence.
2. **Base fills gaps:** Properties not specified in the override
   retain their base component values.
3. **Additive for arrays:** For array properties (e.g., tags,
   platforms), the override array replaces the base array entirely
   (no merging of individual elements).
4. **Deep merge for objects:** For object properties (e.g.,
   on_reject_refine), the override is deep-merged with the base.
   Override fields replace base fields; unspecified fields retain
   base values.

### Non-Overridable Properties

The following 5 required common properties cannot be overridden at
composition time. They are fixed by the component definition in
Layer 1 and are invariant across all compositions:

| Property | Reason |
|---|---|
| component_id | Identity must be stable across compositions |
| component_type | Type is structural, not configurable |
| name | Display name is part of the component identity |
| version | Version is part of the component contract |
| description | Description defines the component's purpose |

### Overridable Properties

The following properties can be overridden at composition time:

**Optional common properties:**
- duration_range
- platforms
- tags

**Type-specific properties:**
All type-specific properties defined for each component type in
COMPONENT_SCHEMA.md can be overridden, subject to the constraints
of the type-specific validation rules (VR-004).

### Schema Conformance

All override values must conform to the same schema as the base
component properties. An override cannot introduce properties that
are not defined for the declared component_type. Specifically:

- The override must not add properties undefined for the type (VR-004).
- Type-specific enum constraints still apply (e.g., step_type must
  still be "prompt" or "action" per VR-007).
- Validation rules still apply to the merged result.

### Override Syntax

Overrides are specified inline in the composition YAML by including
only the properties to override alongside the component_id reference:

```yaml
# Example: Override tags and duration_range on a step_definition
step_bindings:
  - component_id: "step-generate_package-01"
    # Override: add tags and set duration_range
    tags: ["package-assembly", "critical"]
    duration_range: "15-30 minutes"
    # All other properties retain base values from Layer 1
```

```yaml
# Example: Override a routing_pattern's max_iterations
routing:
  - component_id: "routing-gatekeep_package-01"
    # Override: increase max_iterations
    max_iterations: 3
    # onsuccess and other fields retain base values
```

```yaml
# Example: Override prompt_pattern sections
prompts:
  - component_id: "prompt-generation_tasks-01"
    # Override: customize sections for this composition
    sections:
      - "Generate the composition format document"
      - "Define all binding rules from the spec"
      - "Include self-validation checklist"
```

---

## Placeholder Resolution

The placeholder resolution mechanism specifies how {PLACEHOLDER}
tokens in templates are resolved at composition time. Placeholders
appear in prompt templates, composition fields, and output paths.

### Data Sources

There are 4 data sources for placeholder resolution, applied in
the following priority order:

#### Data Source 1: Input Spec

| Field | Description | Example |
|---|---|---|
| WORKFLOW_SPEC_FILE | Absolute path to the input specification file | /path/to/workflow_builder_v4.md |
| domain_name | The domain name from the spec | "workflow_builder" |
| job_prefix | The job prefix from the spec | "WBUILD4" |
| builder_name | The builder name from the composition | "workflow_builder_v4" |

**Resolution timing:** Loaded at workflow start from the input
specification and composition metadata.

#### Data Source 2: Governance

| Field | Description | Example |
|---|---|---|
| BASE_COMPOSITION_STANDARD | Filename of the base composition standard | COMPOSITION_SYSTEM_STANDARD.md |
| GOVERNANCE_RUNTIME_ROOT | Filename reference to governance runtime root | METADATA_CONTRACT.md |

**Resolution timing:** Static -- resolved from the governance
configuration at workflow initialization. References use filenames
only, not resolved filesystem paths.

#### Data Source 3: Runtime

| Field | Description | Example |
|---|---|---|
| job_id | The unique job identifier assigned at runtime | "WBUILD3-y7r4qrrs" |
| seq | Zero-padded sequence number for the artifact | "001" |
| workspace_root | The absolute path to the workspace root | "D:/MyProjectSpace/01_Workflows/agent-runner-v2" |
| output_dir | The absolute path to the output directory | "D:/.../runs/WBUILD3-y7r4qrrs/" |

**Resolution timing:** Computed at execution time by the runner
engine. These values are not known until the workflow starts
executing.

#### Data Source 4: Discovery

| Field | Description | Example |
|---|---|---|
| DISCOVERED_COMPONENT_TYPES | Comma-separated list of component types parsed from the generated composition standard | "step_definition, role_policy, routing_pattern, prompt_pattern, artifact_contract, composition_standard, output_variance, domain_spec" |
| COMPOSITION_STANDARD_PATH | Absolute path to the generated composition standard file | "/path/to/COMPOSITION_STANDARD-001.md" |

**Resolution timing:** Computed at runtime after the
generate_composition_standard step completes. The
discover_component_types function parses the standard to extract
the component type list dynamically. This enables the generated
workflow to use the actual component types from the standard rather
than hardcoded values.

### Resolution Order

Placeholders are resolved in the following order. If a placeholder
is found in an earlier data source, that value is used and later
sources are not consulted for that placeholder:

1. Input Spec (highest priority)
2. Governance
3. Runtime
4. Discovery (lowest priority)

### Unresolved Handling

If a placeholder cannot be resolved from any of the 4 data sources,
it is replaced with the literal string:

```
{UNRESOLVED: placeholder_name}
```

This ensures that unresolved placeholders are visible in the output
and can be detected by downstream validation steps. A composition
with unresolved placeholders should fail validation (see CV-007).

### Resolution Examples

| Placeholder | Data Source | Resolved Value |
|---|---|---|
| {WORKFLOW_SPEC_FILE} | Input Spec | /path/to/workflow_builder_v4.md |
| {job_id} | Runtime | WBUILD3-y7r4qrrs |
| {seq} | Runtime | 001 |
| {DISCOVERED_COMPONENT_TYPES} | Discovery | step_definition, role_policy, ... |
| {BASE_COMPOSITION_STANDARD} | Governance | COMPOSITION_SYSTEM_STANDARD.md |
| {unknown_field} | N/A | {UNRESOLVED: unknown_field} |

---

## Ordering Rules

The ordering rules define constraints on the sequence of steps in
the step_bindings array. These rules ensure that the workflow
executes in a logically correct order regardless of the chosen
workflow pattern.

### Rule O-001: Foundation First

The Foundation phase (Phase 1) steps must appear first in the
step_bindings array. The first step is always generate_test_criteria,
which produces the acceptance criteria that all subsequent phases
are measured against.

**Rationale:** Test-driven development requires acceptance criteria
to exist before any other artifacts are produced.

**Example:**
```yaml
step_bindings:
  - step_name: "generate_test_criteria"  # Must be first
    step_type: "prompt"
  - step_name: "review_test_criteria"
    step_type: "prompt"
  - step_name: "refine_test_criteria"    # Conditional
    step_type: "prompt"
  # ... subsequent phases follow
```

### Rule O-002: Layer Sequence

The three-layer sequence must be respected: Layer 1 (Component
Schema) before Layer 2 (Composition Format) before Layer 3
(Output Format). Each layer depends on the artifacts produced by
the preceding layer.

**Rationale:** Layer 2 binding rules reference Layer 1 component
types. Layer 3 output format references Layer 2 bindings. Breaking
the sequence would create dangling references.

**Enforced order:**
1. Component Schema (Layer 1) -- generate_component_schema
2. Composition Format (Layer 2) -- generate_composition_format
3. Output Format (Layer 3) -- generate_output_format

### Rule O-003: Gatekeep After Generate

Every gatekeep step must immediately follow its corresponding
generate step in the step_bindings. Gatekeep steps validate the
artifact produced by the generate step and must execute before
any subsequent phase begins.

**Rationale:** Quality gates must validate artifacts before they
are consumed by downstream steps. A gatekeep step that executes
after other steps have already consumed its input artifact would
allow invalid artifacts to propagate.

**Example:**
```yaml
step_bindings:
  - step_name: "generate_component_schema"     # Generate
    step_type: "prompt"
  - step_name: "gatekeep_component_schema"     # Gatekeep immediately after
    step_type: "action"
  - step_name: "generate_composition_format"   # Next phase
    step_type: "prompt"
```

### Rule O-004: Terminal Last

The terminal step (step_completion) must be the last entry in the
step_bindings array. No steps may follow the terminal step. The
terminal step records the final outcome and produces the
WORKFLOW_PACKAGE_DIR_FILE artifact.

**Rationale:** The terminal step marks the end of workflow execution.
Steps after the terminal step would never execute because the
workflow is considered complete.

**Example:**
```yaml
step_bindings:
  # ... all other steps
  - step_name: "promote_workflow_package"
    step_type: "action"
  - step_name: "step_completion"  # Must be last
    step_type: "action"
```

### Rule O-005: Refine Steps Are Conditional

Refine steps (e.g., refine_test_criteria, refine_package) are
conditional -- they execute only when the preceding review or
gatekeep step returns REJECTED. They are placed in the step_bindings
array but their routing is controlled by the on_reject_refine
configuration of the preceding step.

**Rationale:** Refine steps should only execute when there is
something to refine. Including them in step_bindings ensures they
are discoverable and have proper artifact declarations, even though
they are conditionally executed.

### Rule O-006: Embed Spec Before Validate

The embed_builder_spec action step must execute after
generate_package but before validate_package_deterministic. This
ensures the Specs/ directory exists before validation check 10
verifies its presence.

**Rationale:** Validation check 10 verifies that Specs/ contains
at least one .md file. If embed_builder_spec runs after validation,
check 10 would always fail.

### Rule O-007: Operational Workflow After All Layers

The Operational Workflow phase (Phase 5) must execute after all
three layers (Component Schema, Composition Format, Output Format)
are complete. The operational workflow references artifacts from
all three layers.

**Rationale:** The operational workflow defines the complete step
sequence and must reference the component types (Layer 1), binding
rules (Layer 2), and output format (Layer 3) defined in the
preceding phases.

### Rule O-008: Composition Standard Before Package

The Composition Standard phase (Phase 6) and Meta Composition Spec
phase (Phase 7) must execute before Package Assembly (Phase 8).
The generate_package step consumes the composition standard and
meta composition spec as inputs.

**Rationale:** The package assembly step generates workflow.toml
and other files that reference the composition standard. If the
standard does not exist yet, the package generation would have
dangling references.

---

## Composition Validation

The following 10 validation checks (CV-001 through CV-010) verify
the structural correctness and internal consistency of a composition
document. These checks are applied during the gatekeep_composition_format
step and by the validate_package_deterministic action.

| Check ID | Name | Description | Severity |
|---|---|---|---|
| CV-001 | Binding Rule Completeness | All 9 binding rules are defined and documented. Each rule specifies binding name, component type, cardinality, required flag, and description. | CRITICAL |
| CV-002 | Workflow Pattern Completeness | All 6 workflow patterns are defined. Each pattern includes name, description, when-to-use guidance, step sequence template, and typical step count. | CRITICAL |
| CV-003 | Composition Structure Fields | All required composition structure fields are present: builder_name, builder_label, job_prefix, builder_purpose, workflow_pattern, step_bindings, artifact_bindings, composition_standard_binding, self_bootstrap_binding. | CRITICAL |
| CV-004 | Self-Bootstrap Binding | The self_bootstrap_binding section contains exactly 4 fields: bootstrap_spec_key, bootstrap_spec_target, bootstrap_version, next_version_pattern. Each field has a type, required flag, and description. | CRITICAL |
| CV-005 | Override Mechanism | The override mechanism is defined with merge semantics, non-overridable properties (5 common properties), overridable properties, and schema conformance rules. At least one override syntax example is provided. | HIGH |
| CV-006 | Placeholder Resolution | The placeholder resolution mechanism defines exactly 4 data sources: Input Spec, Governance, Runtime, Discovery. Resolution order and unresolved handling are specified. | CRITICAL |
| CV-007 | Discovery Data Source | The Discovery data source includes DISCOVERED_COMPONENT_TYPES and COMPOSITION_STANDARD_PATH as resolvable values. | HIGH |
| CV-008 | Ordering Rules | Ordering rules are defined covering: foundation first, layer sequence, gatekeep after generate, terminal last, embed spec before validate. | CRITICAL |
| CV-009 | Bootstrap Chain Integrity | The composition structure specifies that the embedded spec in Specs/ must be content-identical to the input WORKFLOW_SPEC_FILE. | CRITICAL |
| CV-010 | STANDARDS_COMPOSITION_STANDARD_FILE Declaration | The composition format verifies that both generate_package and refine_package steps declare STANDARDS_COMPOSITION_STANDARD_FILE in their produces sections. | CRITICAL |

**Validation check application:**
- CV-001 through CV-008 are checked by the gatekeep_composition_format
  step during Phase 3.
- CV-009 and CV-010 are verified during Phase 8 (package assembly)
  by the validate_package_deterministic action.

---

## Example Compositions

### Example 1: Workflow Builder v4 (meta_meta_builder pattern)

This composition defines the Workflow Builder v4 meta-meta builder,
which generates meta builders with self-bootstrapping capability.

```yaml
builder_name: "workflow_builder_v4"
builder_label: "Workflow Builder v4"
job_prefix: "WBUILD4"
builder_purpose: >
  Self-bootstrapping meta-meta builder that generates meta builders
  (agents) with complete 3-part output: composition standard, builder
  spec, and workflow package. v4 can process its own spec to generate
  the next version with zero manual intervention.
workflow_pattern: "meta_meta_builder"

step_bindings:
  # Phase 1: Foundation (TDD Loop)
  - step_name: "generate_test_criteria"
    step_type: "prompt"
    purpose: "Generate acceptance criteria for all 9 phases"
    required_inputs: ["WORKFLOW_SPEC_FILE"]
    produces: ["TEST_CRITERIA_FILE"]
    enable_notifications: false
    requires_human_approval_after: false

  - step_name: "review_test_criteria"
    step_type: "prompt"
    purpose: "Review acceptance criteria quality"
    required_inputs: ["WORKFLOW_SPEC_FILE", "TEST_CRITERIA_FILE"]
    produces: ["REVIEW_TEST_CRITERIA_FILE"]
    enable_notifications: false
    requires_human_approval_after: false

  # Phase 2: Component Schema (Layer 1)
  - step_name: "generate_component_schema"
    step_type: "prompt"
    purpose: "Generate the component schema defining all 8 component types"
    required_inputs: ["WORKFLOW_SPEC_FILE", "TEST_CRITERIA_FILE"]
    produces: ["COMPONENT_SCHEMA_FILE"]
    enable_notifications: false
    requires_human_approval_after: false

  - step_name: "gatekeep_component_schema"
    step_type: "action"
    purpose: "Validate component schema against test criteria"
    required_inputs: ["WORKFLOW_SPEC_FILE", "COMPONENT_SCHEMA_FILE", "TEST_CRITERIA_FILE"]
    produces: ["GATEKEEP_COMPONENT_SCHEMA_FILE"]
    enable_notifications: false
    requires_human_approval_after: false

  # Phase 3: Composition Format (Layer 2)
  - step_name: "generate_composition_format"
    step_type: "prompt"
    purpose: "Generate the composition format defining binding rules and patterns"
    required_inputs: ["WORKFLOW_SPEC_FILE", "TEST_CRITERIA_FILE", "COMPONENT_SCHEMA_FILE"]
    produces: ["COMPOSITION_FORMAT_FILE"]
    enable_notifications: false
    requires_human_approval_after: false

  - step_name: "gatekeep_composition_format"
    step_type: "action"
    purpose: "Validate composition format against test criteria"
    required_inputs: ["WORKFLOW_SPEC_FILE", "COMPOSITION_FORMAT_FILE", "TEST_CRITERIA_FILE"]
    produces: ["GATEKEEP_COMPOSITION_FORMAT_FILE"]
    enable_notifications: false
    requires_human_approval_after: false

  # ... (Phases 4-8 continue similarly)

  # Phase 8: Package Assembly
  - step_name: "generate_package"
    step_type: "prompt"
    purpose: "Generate complete workflow package"
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

  - step_name: "embed_builder_spec"
    step_type: "action"
    purpose: "Copy input spec to Specs/ for self-bootstrapping"
    required_inputs: ["WORKFLOW_SPEC_FILE", "WORKFLOW_MANIFEST_FILE"]
    produces: ["SPECS_BUILDER_SPEC_FILE"]
    enable_notifications: false
    requires_human_approval_after: false

  - step_name: "validate_package_deterministic"
    step_type: "action"
    purpose: "Run 11 deterministic validation checks"
    required_inputs:
      - "WORKFLOW_MANIFEST_FILE"
      - "WORKFLOW_EXTENSIONS_FILE"
      - "WORKFLOW_ACTIONS_FILE"
      - "STANDARDS_COMPOSITION_STANDARD_FILE"
      - "SPECS_BUILDER_SPEC_FILE"
    produces: ["VALIDATION_REPORT_FILE"]
    enable_notifications: false
    requires_human_approval_after: false

  # Phase 9: Promotion
  - step_name: "promote_workflow_package"
    step_type: "action"
    purpose: "Deploy 3-part output to workflows/ directory"
    required_inputs: ["WORKFLOW_MANIFEST_FILE"]
    produces: ["WORKFLOW_PACKAGE_DIR_FILE"]
    enable_notifications: false
    requires_human_approval_after: false

  - step_name: "step_completion"
    step_type: "action"
    purpose: "Record final outcome and artifact summary"
    required_inputs: ["WORKFLOW_PACKAGE_DIR_FILE"]
    produces: []
    enable_notifications: true
    requires_human_approval_after: false

artifact_bindings:
  input_artifacts:
    - artifact_key: "WORKFLOW_SPEC_FILE"
      artifact_description: "Composition system specification"
      required: true
  output_artifacts:
    - artifact_key: "TEST_CRITERIA_FILE"
      artifact_description: "Acceptance criteria for all phases"
      filename_pattern: "TEST_CRITERIA-{seq}.md"
      required: true
      produced_by: "generate_test_criteria"
    - artifact_key: "COMPOSITION_FORMAT_FILE"
      artifact_description: "Layer 2 composition format"
      filename_pattern: "COMPOSITION_FORMAT-{seq}.md"
      required: true
      produced_by: "generate_composition_format"
    - artifact_key: "SPECS_BUILDER_SPEC_FILE"
      artifact_description: "Embedded builder spec for self-bootstrapping"
      filename_pattern: "Specs/{builder_name}.md"
      required: true
      produced_by: "embed_builder_spec"
    - artifact_key: "STANDARDS_COMPOSITION_STANDARD_FILE"
      artifact_description: "Composition standard in Standards/ directory"
      filename_pattern: "Standards/COMPOSITION_STANDARD.md"
      required: true
      produced_by: "generate_package"

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
  extensibility_model: >
    New component types can be added without breaking existing
    compositions. Existing compositions reference components by
    component_id, not by type enumeration.

self_bootstrap_binding:
  bootstrap_spec_key: "WORKFLOW_SPEC_FILE"
  bootstrap_spec_target: "Specs/workflow_builder_v4.md"
  bootstrap_version: "4.0.0"
  next_version_pattern: "increment_major"

domain_specs:
  - spec_type: "composition_system_spec"
    spec_version_range: "1.0.0 - 4.99.99"
    required_sections:
      - "Domain Overview"
      - "Component Schema"
      - "Composition Format"
      - "Output Format"
      - "Operational Requirements"
    example_specs:
      - "workflow_builder_v4.md"
```

### Example 2: Simple Prompt-Driven Builder (prompt_driven pattern)

This composition defines a simpler workflow builder that generates
prompt-driven workflows with review/refine loops but without
self-bootstrapping capability.

```yaml
builder_name: "content_workflow_builder"
builder_label: "Content Workflow Builder"
job_prefix: "CONTENT"
builder_purpose: >
  Generates prompt-driven workflows for content generation domains.
  Produces workflow packages with LLM-driven steps, review cycles,
  and quality gates. Does not support self-bootstrapping.
workflow_pattern: "prompt_driven"

step_bindings:
  # Phase 1: Foundation
  - step_name: "generate_test_criteria"
    step_type: "prompt"
    purpose: "Generate acceptance criteria"
    required_inputs: ["WORKFLOW_SPEC_FILE"]
    produces: ["TEST_CRITERIA_FILE"]
    enable_notifications: false
    requires_human_approval_after: false

  - step_name: "review_test_criteria"
    step_type: "prompt"
    purpose: "Review acceptance criteria"
    required_inputs: ["WORKFLOW_SPEC_FILE", "TEST_CRITERIA_FILE"]
    produces: ["REVIEW_TEST_CRITERIA_FILE"]
    enable_notifications: false
    requires_human_approval_after: false

  # Phase 2: Package Assembly
  - step_name: "generate_package"
    step_type: "prompt"
    purpose: "Generate workflow package"
    required_inputs:
      - "WORKFLOW_SPEC_FILE"
      - "TEST_CRITERIA_FILE"
    produces:
      - "WORKFLOW_MANIFEST_FILE"
      - "WORKFLOW_EXTENSIONS_FILE"
      - "WORKFLOW_ACTIONS_FILE"
      - "WORKFLOW_README_FILE"
    enable_notifications: false
    requires_human_approval_after: false

  - step_name: "validate_package"
    step_type: "action"
    purpose: "Validate package completeness"
    required_inputs:
      - "WORKFLOW_MANIFEST_FILE"
      - "WORKFLOW_EXTENSIONS_FILE"
    produces: ["VALIDATION_REPORT_FILE"]
    enable_notifications: false
    requires_human_approval_after: false

  - step_name: "review_package"
    step_type: "prompt"
    purpose: "Review package quality"
    required_inputs:
      - "WORKFLOW_MANIFEST_FILE"
      - "VALIDATION_REPORT_FILE"
    produces: ["REVIEW_FILE_SUGGESTED"]
    enable_notifications: false
    requires_human_approval_after: false

  - step_name: "promote_workflow_package"
    step_type: "action"
    purpose: "Deploy to workflows/ directory"
    required_inputs: ["WORKFLOW_MANIFEST_FILE"]
    produces: ["WORKFLOW_PACKAGE_DIR_FILE"]
    enable_notifications: false
    requires_human_approval_after: false

  - step_name: "step_completion"
    step_type: "action"
    purpose: "Record final outcome"
    required_inputs: ["WORKFLOW_PACKAGE_DIR_FILE"]
    produces: []
    enable_notifications: true
    requires_human_approval_after: false

artifact_bindings:
  input_artifacts:
    - artifact_key: "WORKFLOW_SPEC_FILE"
      artifact_description: "Content workflow specification"
      required: true
  output_artifacts:
    - artifact_key: "TEST_CRITERIA_FILE"
      artifact_description: "Acceptance criteria"
      filename_pattern: "TEST_CRITERIA-{seq}.md"
      required: true
      produced_by: "generate_test_criteria"
    - artifact_key: "WORKFLOW_MANIFEST_FILE"
      artifact_description: "workflow.toml manifest"
      filename_pattern: "workflow.toml"
      required: true
      produced_by: "generate_package"

composition_standard_binding:
  standard_name: "CONTENT_WORKFLOW_STANDARD"
  standard_version: "1.0.0"
  component_types_defined:
    - "step_definition"
    - "role_policy"
    - "routing_pattern"
    - "prompt_pattern"
    - "artifact_contract"
  schema_sections:
    - "Component Schema"
    - "Composition Format"
    - "Output Format"
  extensibility_model: >
    New component types can be added by defining them in the
    Component Schema section. Existing compositions are unaffected.

self_bootstrap_binding:
  bootstrap_spec_key: "WORKFLOW_SPEC_FILE"
  bootstrap_spec_target: "Specs/content_workflow_builder.md"
  bootstrap_version: "1.0.0"
  next_version_pattern: "increment_minor"

output_variances:
  - variance_name: "prompt_only_workflow"
    variance_description: >
      A workflow with only prompt-driven steps and no API
      action steps beyond validation.
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

---

## Self-Validation

This section verifies the completeness and internal consistency of
the composition format document itself.

### Binding Rules Completeness

| # | Binding Name | Component Type | Cardinality | Required | Defined |
|---|---|---|---|---|---|
| 1 | steps | step_definition | Ordered list | Yes | YES |
| 2 | roles | role_policy | Singleton per step | Yes | YES |
| 3 | routing | routing_pattern | Singleton per step | Yes | YES |
| 4 | prompts | prompt_pattern | Unordered set per prompt step | No | YES |
| 5 | artifacts | artifact_contract | Unordered set | Yes | YES |
| 6 | standard | composition_standard | Singleton | Yes | YES |
| 7 | variances | output_variance | Unordered set | No | YES |
| 8 | domain_specs | domain_spec | Unordered set | No | YES |
| 9 | self_bootstrap | domain_spec | Singleton | Yes | YES |

**Verification:** 9 binding rules defined. 8 base (one per component
type) plus 1 self_bootstrap. TC-023 and TC-025 satisfied.

### Workflow Patterns Completeness

| # | Pattern | Description | When to Use | Step Sequence | Defined |
|---|---|---|---|---|---|
| 1 | action_only | All deterministic | API-only workflows | All action steps | YES |
| 2 | prompt_driven | All LLM-driven | Document generation | Prompt + review loops | YES |
| 3 | mixed | Hybrid | Combined workflows | Interleaved | YES |
| 4 | gatekeeper_pipeline | Multi-phase | Layered validation | Phase gates | YES |
| 5 | meta_workflow_builder | Builds workflows | Domain builders | Standard skeleton | YES |
| 6 | meta_meta_builder | Builds meta builders | Composition systems | 3-layer + self-bootstrap | YES |

**Verification:** 6 workflow patterns defined. TC-027 and TC-028
satisfied.

### Composition Structure Completeness

| Field | Type | Required | Defined |
|---|---|---|---|
| builder_name | string | Yes | YES |
| builder_label | string | Yes | YES |
| job_prefix | string | Yes | YES |
| builder_purpose | string | Yes | YES |
| workflow_pattern | enum | Yes | YES |
| step_bindings | array | Yes | YES |
| artifact_bindings | object | Yes | YES |
| composition_standard_binding | object | Yes | YES |
| self_bootstrap_binding | object | Yes | YES |
| output_variances | array | No | YES |
| domain_specs | array | No | YES |

**Verification:** 11 fields defined (9 required + 2 optional).
TC-034 and TC-035 satisfied.

### Self-Bootstrap Binding Completeness

| Field | Type | Required | Defined |
|---|---|---|---|
| bootstrap_spec_key | string | Yes | YES |
| bootstrap_spec_target | string | Yes | YES |
| bootstrap_version | string | Yes | YES |
| next_version_pattern | string | Yes | YES |

**Verification:** 4 fields defined. TC-026 satisfied.

### Override Mechanism Completeness

| Aspect | Defined |
|---|---|
| Merge semantics | YES |
| Non-overridable properties (5 common) | YES |
| Overridable properties | YES |
| Schema conformance | YES |
| Override syntax with examples | YES |

**Verification:** TC-029 satisfied.

### Placeholder Resolution Completeness

| Data Source | Fields | Defined |
|---|---|---|
| Input Spec | WORKFLOW_SPEC_FILE, domain_name, job_prefix, builder_name | YES |
| Governance | BASE_COMPOSITION_STANDARD, GOVERNANCE_RUNTIME_ROOT | YES |
| Runtime | job_id, seq, workspace_root, output_dir | YES |
| Discovery | DISCOVERED_COMPONENT_TYPES, COMPOSITION_STANDARD_PATH | YES |

**Verification:** 4 data sources defined with resolution order and
unresolved handling. TC-030, TC-031, TC-032 satisfied.

### Ordering Rules Completeness

| Rule | Name | Defined |
|---|---|---|
| O-001 | Foundation First | YES |
| O-002 | Layer Sequence | YES |
| O-003 | Gatekeep After Generate | YES |
| O-004 | Terminal Last | YES |
| O-005 | Refine Steps Conditional | YES |
| O-006 | Embed Spec Before Validate | YES |
| O-007 | Operational Workflow After Layers | YES |
| O-008 | Composition Standard Before Package | YES |

**Verification:** 8 ordering rules defined. TC-033 satisfied.

### Composition Validation Checks Completeness

| Check | Name | Severity | Defined |
|---|---|---|---|
| CV-001 | Binding Rule Completeness | CRITICAL | YES |
| CV-002 | Workflow Pattern Completeness | CRITICAL | YES |
| CV-003 | Composition Structure Fields | CRITICAL | YES |
| CV-004 | Self-Bootstrap Binding | CRITICAL | YES |
| CV-005 | Override Mechanism | HIGH | YES |
| CV-006 | Placeholder Resolution | CRITICAL | YES |
| CV-007 | Discovery Data Source | HIGH | YES |
| CV-008 | Ordering Rules | CRITICAL | YES |
| CV-009 | Bootstrap Chain Integrity | CRITICAL | YES |
| CV-010 | STANDARDS_COMPOSITION_STANDARD_FILE Declaration | CRITICAL | YES |

**Verification:** 10 validation checks defined (CV-001 through
CV-010). TC-038 satisfied.

### Criteria Traceability

| Criteria | Status | Evidence |
|---|---|---|
| TC-023 | PASS | 9 binding rules defined in Component Bindings section |
| TC-024 | PASS | Each rule specifies binding name, component type, cardinality, required flag, description |
| TC-025 | PASS | self_bootstrap binding has domain_spec type, Singleton cardinality, required Yes |
| TC-026 | PASS | self_bootstrap_binding has 4 fields: bootstrap_spec_key, bootstrap_spec_target, bootstrap_version, next_version_pattern |
| TC-027 | PASS | 6 workflow patterns defined: action_only, prompt_driven, mixed, gatekeeper_pipeline, meta_workflow_builder, meta_meta_builder |
| TC-028 | PASS | Each pattern has name, description, when-to-use, step sequence |
| TC-029 | PASS | Override mechanism defined with merge semantics, non-overridable properties, examples |
| TC-030 | PASS | Placeholder resolution mechanism defined with 4 data sources and resolution order |
| TC-031 | PASS | 4 data sources: Input Spec, Governance, Runtime, Discovery |
| TC-032 | PASS | Discovery includes DISCOVERED_COMPONENT_TYPES and COMPOSITION_STANDARD_PATH |
| TC-033 | PASS | Ordering rules defined (O-001 through O-008) covering step sequence constraints |
| TC-034 | PASS | Composition structure table has all required fields matching spec Section 3.1 |
| TC-035 | PASS | Each field specifies type, required flag, and description |
| TC-036 | PASS | Bootstrap chain integrity specified: embedded spec must be content-identical to input |
| TC-037 | N/A | Gatekeep step produces GATEKEEP_COMPOSITION_FORMAT_FILE (verified by step 07) |
| TC-038 | PASS | CV-010 verifies both generate_package and refine_package declare STANDARDS_COMPOSITION_STANDARD_FILE |

**Verification:** All Phase 3 criteria (TC-023 through TC-038) are
satisfied by this document (TC-037 is a process criterion verified
at step execution time).

---

End of Composition Format Document
