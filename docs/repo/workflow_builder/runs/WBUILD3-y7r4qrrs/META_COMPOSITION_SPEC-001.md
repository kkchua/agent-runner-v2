---
doc_type: "meta_composition_spec"
lifecycle_status: "draft"
domain: "workflow_builder"
self_bootstrap_capable: true
spec_reference: "workflow_builder_v4.md"
source_composition_standard: "COMPOSITION_STANDARD-001.md"
component_type_count: 8
binding_rule_count: 9
workflow_pattern: "meta_meta_builder"
phase_count: 9
step_count: 22
generated_by: "generate_meta_composition_spec"
---

# Meta Composition Spec -- Workflow Builder v4

## Introduction

### Scope

This document is the Meta Composition Specification for the Workflow
Builder v4 meta-meta builder. It consolidates all upstream phase
outputs -- Component Schema (Layer 1), Composition Format (Layer 2),
Output Format (Layer 3), and Operational Workflow -- into a single
self-contained specification.

### Purpose

This spec serves three purposes:

1. It is the sole input to the generated meta builder, enabling
   the builder to process it as WORKFLOW_SPEC_FILE and generate the
   next version (v5) with zero additional context.

2. It provides the component type inventory extracted from the
   generated composition standard, enabling dynamic discovery rather
   than hardcoded type lists.

3. It documents the complete operational workflow including the
   self-bootstrapping embed_builder_spec step and the 3-part
   promotion contract.

### Traceability

All content in this document traces back to the following upstream
artifacts:

| Source Artifact | Section Used |
|---|---|
| workflow_builder_v4.md (WORKFLOW_SPEC_FILE) | All 5 sections |
| COMPONENT_SCHEMA-001.md (COMPONENT_SCHEMA_FILE) | Section 2: Component Schema |
| COMPOSITION_FORMAT-001.md (COMPOSITION_FORMAT_FILE) | Section 3: Composition Format |
| OUTPUT_FORMAT-001.md (OUTPUT_FORMAT_FILE) | Section 4: Output Format |
| OPERATIONAL_WORKFLOW-001.md (OPERATIONAL_WORKFLOW_FILE) | Section 5: Operational Requirements |
| COMPOSITION_STANDARD-001.md (COMPOSITION_STANDARD_FILE) | Sections 2, 3, 4 |

### Self-Bootstrap Invariant

This spec is designed to be self-bootstrapping. When fed as input
to a meta builder (as WORKFLOW_SPEC_FILE), the builder produces:

1. A new meta builder with its own composition standard
2. A copy of this spec embedded in Specs/
3. A complete executable workflow package

The bootstrap chain: v3 (this run) -> this spec -> v4 builder ->
v4's Specs/ copy of this spec -> v5 builder -> ...

---

## Domain Overview

### Target Domain

| Property | Value |
|---|---|
| Domain name | workflow_builder |
| Label | Workflow Builder v4 |
| Job prefix | WBUILD4 |
| Workflow pattern | meta_meta_builder |
| Standard name | WORKFLOW_BUILDER_STANDARD |
| Standard version | 1.0.0 |

### Builder Purpose

Workflow Builder v4 is a self-bootstrapping meta-meta builder that
generates meta builders (agents) with complete 3-part output. Each
generated meta builder includes its own composition standard, its
own spec in Specs/, and a fully executable workflow package. v4 can
process its own spec to generate v5.

### Three-Part Output (Enforced)

Every generated meta builder must produce exactly 3 parts:

| Part | Location | Description | Mandatory |
|---|---|---|---|
| Part 1 | Standards/COMPOSITION_STANDARD.md | The composition standard for the generated meta builder | Yes |
| Part 2 | Specs/{builder_name}.md | The builder's own spec (enables self-bootstrapping) | Yes |
| Part 3 | Workflow package directory | workflow.toml, context_extensions.py, actions.py, prompts/, README.md | Yes |

### Multi-Level Architecture

```
Level 0: v4 builder (creates agents, self-bootstrapping)
Level 1: Agent Workflow Spec (composition standard per agent)
Level 2: User Workflows (composition specs per use case)
Level 3: Agent execution outputs (deliverables)
```

### Key Innovations Over v3

| Aspect | v3 | v4 |
|---|---|---|
| Promotion | Standards/Specs/ copied only if actions.py runs | Enforced -- promote action always copies 3-part output |
| Self-bootstrapping | Described but not implemented | Implemented -- embed_builder_spec step copies own spec to Specs/ |
| Component discovery | Hardcoded in prompts (8 types) | Dynamic -- reads from generated COMPOSITION_STANDARD.md |
| Validation | 9 checks | 11 checks -- adds Specs/ content check and bidirectional placeholder check |
| Bootstrap chain | v3 -> v4 (manual) | v4 -> v5 (automatic) -- Specs/workflow_builder_v4.md is the input |

### Lessons Incorporated

| Issue | Root Cause | v4 Fix |
|---|---|---|
| PROMPT_INPUT_MISMATCH | Prompts referenced artifacts not declared in step | All steps declaring {WORKFLOW_SPEC_FILE} in prompt list it in required_inputs |
| STEP_CONTRACT_MISMATCH | refine_package produced artifact not in produces list | Both generate_package and refine_package declare STANDARDS_COMPOSITION_STANDARD_FILE |
| Missing Standards/Specs/ in promoted output | v2 promote action did not know about these dirs | promote action explicitly copies Standards/ and Specs/ |
| Untracked output files | LLM generated extra files not in artifact registry | Strict artifact key discipline |

---

## Component Schema

This section defines the Layer 1 component schema extracted from the
composition standard (COMPOSITION_STANDARD-001.md). It specifies the
8 component types that serve as the universal building blocks for all
meta builders in the workflow_builder domain.

### Common Properties

All 8 component types share the following common properties.

#### Required Common Properties (5)

Every component instance must include all 5 of these properties.
Missing any required property is a validation failure (VR-001).

| Property | Type | Required | Description |
|---|---|---|---|
| component_id | string | Yes | Unique identifier. Format: {type-prefix}-{name}-{seq}. Must be globally unique within a composition (VR-003). |
| component_type | enum | Yes | One of the 8 defined types. Unknown types are rejected (VR-002). |
| name | string | Yes | Human-readable display name for documentation and traceability. |
| version | string | Yes | Semantic version in MAJOR.MINOR.PATCH format (VR-005). |
| description | string | Yes | Detailed description of purpose and applicability. At least 10 characters. |

#### Optional Common Properties (3)

These properties may be included on any component type for
additional classification and filtering metadata.

| Property | Type | Required | Description |
|---|---|---|---|
| duration_range | string | No | Duration or scope constraint. Example: "5-15 minutes". |
| platforms | array | No | Target platforms. Example: ["windows", "linux"]. |
| tags | array | No | Classification tags. Example: ["generation", "validation"]. |

### Component Types

The following 8 component types are extracted from the composition
standard (COMPOSITION_STANDARD-001.md). Discovered types:
step_definition, role_policy, routing_pattern, prompt_pattern,
artifact_contract, composition_standard, output_variance, domain_spec.

#### Type 1: step_definition

**Purpose:** Defines a single workflow step with its execution type,
purpose, required inputs, and produced outputs. Each step is an
atomic unit of work. Steps are ordered and their execution sequence
is determined by their position in the step_bindings array.

**Required:** Yes. Every workflow must define at least one.
**Cardinality:** Ordered list (N steps per workflow).

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| step_name | string | Yes | Unique step identifier. Lowercase with underscores. Must be unique across all steps (VR-006). |
| step_type | enum | Yes | Execution type: "prompt" or "action" (VR-007). |
| purpose | string | Yes | What this step achieves. Non-empty descriptive string. |
| required_inputs | array | No | Artifact keys this step reads. Each must reference a prior-produced artifact or workflow input (VR-012, VR-015). |
| produces | array | Yes | Artifact keys this step writes. Must be non-empty. UPPER_SNAKE_CASE with _FILE suffix (VR-009). |
| enable_notifications | boolean | Yes | Whether to send notifications on completion. Default: false. |
| requires_human_approval_after | boolean | Yes | Whether to pause for human approval. Default: false. |

**Validation Rules Applied:** VR-006, VR-007, VR-009, VR-012, VR-015.

#### Type 2: role_policy

**Purpose:** Defines a coder role assignment for a workflow step.
Each step must be bound to exactly one role_policy that determines
which coder backend and instruction set handles execution.

**Required:** Yes. Every step must have a role_policy.
**Cardinality:** Singleton per step.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| policy_name | enum | Yes | Must be one of: architect_standard, reviewer_standard, gatekeeper_standard, validation_standard, refine_standard (VR-008). |
| assignment_rule | string | Yes | Description of when and why this policy is assigned. |

**Valid policy_name values and typical assignments:**

| policy_name | Typical Assignment |
|---|---|
| architect_standard | Generation steps that create documents or designs |
| reviewer_standard | Review steps that evaluate artifacts for quality |
| gatekeeper_standard | Gatekeep steps that enforce quality thresholds |
| validation_standard | Deterministic validation action steps |
| refine_standard | Refinement steps that improve rejected artifacts |

**Validation Rules Applied:** VR-008.

#### Type 3: routing_pattern

**Purpose:** Defines how steps connect to each other. Controls the
flow of execution including success path, reject-refine loops, and
terminal failure conditions.

**Required:** Yes. Every step must have a routing_pattern.
**Cardinality:** Singleton per step.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| onsuccess | string | Yes | Name of the next step on success. Must reference a valid step_name (VR-010). |
| on_reject_refine | object | No | Refinement loop configuration. Required for review and gatekeep steps. |
| max_iterations | integer | No | Maximum refine loop iterations. Required if on_reject_refine is defined. |
| exhausted_failure_code | string | No | Terminal failure code when iterations exhausted. UPPER_SNAKE_CASE. |
| exhausted_failure_class | string | No | Failure classification. Typical: "HUMAN_RETRY_REQUIRED". |

**on_reject_refine sub-structure:**

| Field | Type | Required | Description |
|---|---|---|---|
| step | string | Yes | Step name to jump to on rejection. |
| artifact | string | Yes | Artifact key that triggered the rejection. |
| max_iterations | integer | Yes | Maximum refine loop iterations before terminal failure. |
| exhausted_failure_code | string | Yes | Terminal failure code when iterations exhausted. |
| exhausted_failure_class | string | Yes | Failure classification for exhausted iterations. |

**Validation Rules Applied:** VR-010.

#### Type 4: prompt_pattern

**Purpose:** Defines structural elements injected into prompt
templates. Each pattern adds a specific section to the prompt,
ensuring consistent quality checks across all prompt-driven steps.

**Required:** No. Only applicable to prompt-type steps.
**Cardinality:** Unordered set per prompt-driven step.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| pattern_name | enum | Yes | Must be one of: self_critic, self_validation, context_verification, reference_inputs, generation_tasks, forbidden_content, output_instructions. |
| sections | array | Yes | List of prompt section descriptions this pattern contributes. |

**Validation Rules Applied:** VR-011 (every prompt-type step must
include self_critic and self_validation patterns).

#### Type 5: artifact_contract

**Purpose:** Defines an input or output artifact that flows through
the workflow. Each contract specifies the key, format, and ownership
of a single artifact.

**Required:** Yes. Every workflow must define its artifact contracts.
**Cardinality:** Unordered set per workflow.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| artifact_key | string | Yes | Unique artifact identifier. UPPER_SNAKE_CASE with _FILE suffix (VR-009). |
| artifact_description | string | Yes | What this artifact contains and its purpose. |
| filename_pattern | string | No | Filename pattern with placeholders (e.g., "COMPONENT_SCHEMA-{seq}.md"). |
| required | boolean | Yes | Whether this artifact is required for execution. |
| produced_by | string | No | The step_name that produces this artifact. Required for outputs. |

**Validation Rules Applied:** VR-009.

#### Type 6: composition_standard

**Purpose:** Defines the composition standard schema for the
generated meta builder. This is the self-describing element that
makes each generated builder aware of its own component types.

**Required:** Yes. Every meta builder must define exactly one.
**Cardinality:** Singleton per workflow.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| standard_name | string | Yes | Name of the standard (e.g., "WORKFLOW_BUILDER_STANDARD"). |
| standard_version | string | Yes | Version in MAJOR.MINOR.PATCH format. |
| component_types_defined | array | Yes | List of component type names defined in this standard. |
| schema_sections | array | Yes | Must contain exactly 3 entries: "Component Schema", "Composition Format", "Output Format" (VR-013). |
| extensibility_model | string | Yes | Description of how new types can be added. |

**Validation Rules Applied:** VR-013.

#### Type 7: output_variance

**Purpose:** Defines a specific output configuration the meta builder
can produce. Variances allow the same workflow to generate different
deliverables based on input and composition-time choices.

**Required:** No. Only used when multiple output configurations are
supported.
**Cardinality:** Unordered set per workflow.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| variance_name | string | Yes | Name identifying this variance. Unique within workflow. |
| variance_description | string | Yes | What this variance produces. |
| component_requirements | array | Yes | Which component types are required. Each must be a valid type from the 8 base types (VR-014). |
| output_files | array | Yes | Files produced when this variance is selected. Non-empty. |

**Validation Rules Applied:** VR-014.

#### Type 8: domain_spec

**Purpose:** Defines a type of user-provided specification the meta
builder can process. Allows validation of incoming specs against
expected structure and version compatibility.

**Required:** No. Only used when the builder accepts external specs.
**Cardinality:** Unordered set per workflow.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| spec_type | string | Yes | Type identifier (e.g., "composition_system_spec"). |
| spec_version_range | string | Yes | Compatible version range (e.g., "1.0.0 - 4.99.99"). |
| required_sections | array | Yes | Sections the specification must contain. |
| example_specs | array | No | Example specification filenames for reference. |

**Validation Rules Applied:** Common rules only.

### Validation Rules (Global)

The following 16 validation rules apply to all component instances.

| Rule ID | Rule | Severity |
|---|---|---|
| VR-001 | Every component must have all 5 required common properties: component_id, component_type, name, version, description. | CRITICAL |
| VR-002 | component_type must be one of the 8 defined types. Unknown types are rejected. | CRITICAL |
| VR-003 | No two components within a composition may share the same component_id. | CRITICAL |
| VR-004 | Each component must conform to its type-specific schema. Undefined properties are rejected. | HIGH |
| VR-005 | version must follow MAJOR.MINOR.PATCH format with non-negative integer segments. | MEDIUM |
| VR-006 | No duplicate step_name values within a workflow. | CRITICAL |
| VR-007 | step_type must be "prompt" or "action". No other values permitted. | CRITICAL |
| VR-008 | policy_name must be one of: architect_standard, reviewer_standard, gatekeeper_standard, validation_standard, refine_standard. | CRITICAL |
| VR-009 | artifact_key must be UPPER_SNAKE_CASE with _FILE suffix for document artifacts. | HIGH |
| VR-010 | Every step must have onsuccess routing to a valid next step_name in step_bindings. | CRITICAL |
| VR-011 | Every prompt-type step must include self_critic and self_validation prompt patterns. | HIGH |
| VR-012 | Every required_inputs artifact must reference a prior-produced artifact or a declared workflow input. | CRITICAL |
| VR-013 | composition_standard schema_sections must contain exactly: "Component Schema", "Composition Format", "Output Format". | CRITICAL |
| VR-014 | output_variance component_requirements must reference only valid component types from the 8 base types. | HIGH |
| VR-015 | Every step referencing WORKFLOW_SPEC_FILE in its prompt must declare WORKFLOW_SPEC_FILE in required_inputs. Bidirectional check. | CRITICAL |
| VR-016 | Both generate_package and refine_package must declare STANDARDS_COMPOSITION_STANDARD_FILE in produces. | CRITICAL |

### Dynamic Discovery Mechanism

Instead of hardcoding the 8 component types in prompts, the
generated meta builder discovers them from the composition standard
at runtime:

```python
def discover_component_types(standard_path: str) -> str:
    """Parse COMPOSITION_STANDARD.md and return comma-separated type list.

    Reads the YAML frontmatter field component_type_count and
    scans for '#### Type N:' headings in the Component Types section.
    Returns a comma-separated string of discovered type names.
    """
```

The discover_component_types function:
1. Reads the generated COMPOSITION_STANDARD.md file.
2. Parses the YAML frontmatter for component_type_count.
3. Scans for "#### Type N: type_name" headings.
4. Returns the discovered type names as a comma-separated string.
5. If discovery fails, falls back to the 8 base types.

Discovered types are injected into prompt context as
{DISCOVERED_COMPONENT_TYPES}.

---

## Composition Format

This section defines the Layer 2 composition format extracted from
the composition standard and composition format documents. It
specifies how the 8 component types are bound into compositions,
how placeholders are resolved, and how overrides are applied.

### Composition Structure

Every composition for the workflow_builder domain is a YAML document
with the following top-level fields:

| Field | Type | Required | Description |
|---|---|---|---|
| builder_name | string | Yes | Unique builder identifier. Lowercase with underscores. |
| builder_label | string | Yes | Human-readable display name. |
| job_prefix | string | Yes | 4-6 character uppercase prefix for job IDs. |
| builder_purpose | string | Yes | Description of what problem this builder solves. |
| workflow_pattern | enum | Yes | One of the 6 defined workflow patterns. |
| step_bindings | array | Yes | Ordered array of step_definition instances. |
| artifact_bindings | object | Yes | Input and output artifact contracts. |
| composition_standard_binding | object | Yes | References the composition_standard component. |
| self_bootstrap_binding | object | Yes | Self-bootstrapping configuration (4 fields). |
| output_variances | array | No | Alternative output configurations. |
| domain_specs | array | No | User-provided spec types the builder processes. |

### Binding Rules

The following 9 binding rules connect the 8 component types to the
composition structure fields.

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

**Binding Rule 1 (steps):** Binds step_definition components to
step_bindings. Array order determines execution sequence.

**Binding Rule 2 (roles):** Binds exactly one role_policy to each
step_definition. policy_name must be one of 5 valid values (VR-008).

**Binding Rule 3 (routing):** Binds exactly one routing_pattern to
each step_definition. onsuccess must reference a valid step_name
(VR-010).

**Binding Rule 4 (prompts):** Binds prompt_pattern components to
prompt-type steps. Every prompt-type step must include self_critic
and self_validation patterns (VR-011).

**Binding Rule 5 (artifacts):** Binds artifact_contract components
to artifact_bindings. Every artifact_key must be UPPER_SNAKE_CASE
with _FILE suffix (VR-009).

**Binding Rule 6 (standard):** Binds exactly one
composition_standard. schema_sections must contain exactly 3 entries
(VR-013).

**Binding Rule 7 (variances):** Binds output_variance components.
component_requirements must reference valid types (VR-014).

**Binding Rule 8 (domain_specs):** Binds domain_spec components.
Each spec_type must be unique within the composition.

**Binding Rule 9 (self_bootstrap):** Binds the self_bootstrap_binding
configuration. bootstrap_spec_key must be "WORKFLOW_SPEC_FILE".
bootstrap_spec_target must follow "Specs/{builder_name}.md".

### Self-Bootstrap Binding

The self_bootstrap_binding defines how the builder references its
own spec for self-bootstrapping:

| Field | Type | Required | Description |
|---|---|---|---|
| bootstrap_spec_key | string | Yes | Artifact key holding the builder's own spec (always "WORKFLOW_SPEC_FILE"). |
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
Gatekeeper steps: 6 gatekeep steps plus package gatekeep.
Special features: embed_builder_spec step for self-bootstrapping.
Dynamic component discovery from generated standard.

### Override Mechanism

The override mechanism allows per-composition customization without
modifying Layer 1 component definitions.

**Merge semantics:**

1. Override wins on conflict: override value takes precedence.
2. Base fills gaps: unspecified properties retain base values.
3. Array replacement: override array replaces base array entirely.
4. Deep merge for objects: override fields replace base fields.

**Non-overridable properties (5):** component_id, component_type,
name, version, description. These are fixed by Layer 1.

**Overridable properties:** All 3 optional common properties
(duration_range, platforms, tags) and all type-specific properties.

**Schema conformance:** All override values must conform to the same
schema as the base component properties.

### Placeholder Resolution

There are 4 data sources for placeholder resolution, applied in
priority order:

| Priority | Data Source | Fields Provided |
|---|---|---|
| 1 (highest) | Input Spec | WORKFLOW_SPEC_FILE, domain_name, job_prefix, builder_name |
| 2 | Governance | BASE_COMPOSITION_STANDARD, GOVERNANCE_RUNTIME_ROOT |
| 3 | Runtime | job_id, seq, workspace_root, output_dir |
| 4 (lowest) | Discovery | DISCOVERED_COMPONENT_TYPES, COMPOSITION_STANDARD_PATH |

**Discovery data source:** DISCOVERED_COMPONENT_TYPES is computed at
runtime after generate_composition_standard completes. The
discover_component_types() function parses the standard dynamically.

**Unresolved handling:** Unresolvable placeholders become:
{UNRESOLVED: placeholder_name}

### Ordering Rules

The following 8 ordering rules constrain the step sequence:

| Rule | Name | Description |
|---|---|---|
| O-001 | Foundation First | Phase 1 steps must appear first. |
| O-002 | Layer Sequence | Layer 1 before Layer 2 before Layer 3. |
| O-003 | Gatekeep After Generate | Every gatekeep step immediately follows its generate step. |
| O-004 | Terminal Last | step_completion must be the last entry. |
| O-005 | Refine Steps Conditional | Refine steps execute only on rejection. |
| O-006 | Embed Spec Before Validate | embed_builder_spec after generate_package, before validate. |
| O-007 | Operational Workflow After Layers | Phase 5 after all three layers. |
| O-008 | Composition Standard Before Package | Phases 6-7 before Phase 8. |

---

## Output Format

This section defines the Layer 3 output format extracted from the
composition standard and output format documents. It specifies how
compositions materialize into concrete output files.

### Output Structure

The output is a 3-part directory structure:

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

### Part 1: Standards Directory

| File | Mandatory | Description |
|---|---|---|
| Standards/COMPOSITION_STANDARD.md | Yes | Composition standard defining all component types, validation rules, and extensibility model. |

**Format:** Markdown with YAML frontmatter containing standard_name,
standard_version, component_type_count, schema_sections. Body
contains component type definitions in "#### Type N: type_name"
format.

### Part 2: Specs Directory

| File | Mandatory | Description |
|---|---|---|
| Specs/{builder_name}.md | Yes | Content-identical copy of input WORKFLOW_SPEC_FILE. |

**Format:** Must be content-identical to the input
WORKFLOW_SPEC_FILE. Enforced by embed_builder_spec action and
validation check 10.

### Part 3: Workflow Package

| File | Mandatory | Description |
|---|---|---|
| workflow.toml | Yes | Workflow manifest defining steps, artifacts, routing. |
| context_extensions.py | Yes | Python module for artifact path resolution. |
| actions.py | Conditional | Python module with action step implementations. |
| prompts/NN_{step_name}.txt | Yes (per prompt step) | Prompt template files. NN is zero-padded step number. |
| README.md | Yes | Human documentation (purpose, inputs, outputs, invocation). |
| .env.sample | Conditional | Sample environment variables. |
| config.json.sample | Conditional | Sample runtime configuration. |

### Resolution Rules

The following 7 resolution rules define how component types are
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

**RR-001:** Each step_definition becomes a [[step]] section in
workflow.toml.

**RR-002:** Each role_policy policy_name becomes the coder_role
field.

**RR-003:** Each routing_pattern onsuccess and on_reject_refine
become routing fields.

**RR-004:** Each prompt_pattern sections array becomes content in
the prompt template file.

**RR-005:** Each artifact_contract becomes a registration in
register_artifact_keys().

**RR-006:** The composition_standard becomes
Standards/COMPOSITION_STANDARD.md with YAML frontmatter.

**RR-007:** All {PLACEHOLDER} tokens resolved using 4 data sources
in priority order.

### Quality Requirements

The following quality requirements validate the output:

| Rule ID | Requirement | Severity |
|---|---|---|
| QR-001 | TOML parse validity of workflow.toml. | CRITICAL |
| QR-002 | Python syntax validity of context_extensions.py and actions.py. | CRITICAL |
| QR-003 | No TYPE_CHECKING runtime import guards. | HIGH |
| QR-004 | Artifact binding consistency. Every required_inputs references prior-produced or workflow input. | CRITICAL |
| QR-005 | Action step implementation completeness. Every action step has matching function in actions.py. | CRITICAL |
| QR-006 | Prompt file existence. Every prompt step has corresponding prompts/NN_{step_name}.txt. | CRITICAL |
| QR-007 | Prompt placeholder consistency (unidirectional). Every {PLACEHOLDER} declared in step artifacts. | CRITICAL |
| QR-008 | context_extensions.py artifact key coverage. Every artifact key registered. | CRITICAL |
| QR-009 | Standards/ directory exists and contains COMPOSITION_STANDARD.md. | CRITICAL |
| QR-010 | Specs/ directory exists and contains at least one .md file. | CRITICAL |
| QR-011 | All prompt {PLACEHOLDER} tokens declared in step required_inputs or produces (bidirectional). | CRITICAL |
| QR-012 | Both generate_package and refine_package declare STANDARDS_COMPOSITION_STANDARD_FILE. | CRITICAL |

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

**Enforcement:** If Standards/ or Specs/ is missing, the promote
action REJECTS with error message:
"Required output directory '{name}/' not found. v4 requires 3-part
output: Standards/, Specs/, workflow files."

### Downstream Extraction Contracts

| Contract ID | Target | Consumer | Format |
|---|---|---|---|
| DEC-001 | workflow.toml | Runner engine, step_runner | TOML |
| DEC-002 | prompts/ directory | step_runner, coder_adapters | Plain text |
| DEC-003 | Standards/COMPOSITION_STANDARD.md | context_extensions.py, downstream builders | Markdown |

---

## Operational Requirements

This section defines the complete operational workflow for the
Workflow Builder v4 meta-meta builder, extracted from the operational
workflow document and the input specification.

### Workflow Phases (9 phases)

| Phase | Name | Purpose | Steps |
|---|---|---|---|
| 1 | Foundation (TDD Loop) | Generate and validate acceptance criteria | 01, 02, 03 |
| 2 | Component Schema (Layer 1) | Define Layer 1 component types | 04, 05 |
| 3 | Composition Format (Layer 2) | Define Layer 2 binding rules and patterns | 06, 07 |
| 4 | Output Format (Layer 3) | Define Layer 3 output structure | 08, 09 |
| 5 | Operational Workflow | Define complete step sequence | 10, 11 |
| 6 | Composition Standard (v3 Innovation) | Define generated builder standard | 12, 13 |
| 7 | Meta Composition Spec (v3 Innovation) | Produce self-bootstrapping spec | 14 |
| 8 | Package Assembly | Generate, embed spec, validate, review, refine | 15, 16, 17, 18, 19, 20 |
| 9 | Promotion | Deploy 3-part output | 21, 22 |

### Step Sequence (22 steps)

| Step # | Name | Type | Purpose | Required Inputs | Produces | onsuccess |
|---|---|---|---|---|---|---|
| 01 | generate_test_criteria | prompt | Generate acceptance criteria | WORKFLOW_SPEC_FILE | TEST_CRITERIA_FILE | review_test_criteria |
| 02 | review_test_criteria | prompt | Review criteria quality | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE | REVIEW_TEST_CRITERIA_FILE | generate_component_schema |
| 03 | refine_test_criteria | prompt | Refine rejected criteria | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, REVIEW_TEST_CRITERIA_FILE | TEST_CRITERIA_FILE | review_test_criteria |
| 04 | generate_component_schema | prompt | Generate Layer 1 component schema | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE | COMPONENT_SCHEMA_FILE | gatekeep_component_schema |
| 05 | gatekeep_component_schema | action | Validate schema against criteria | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE | GATEKEEP_COMPONENT_SCHEMA_FILE | generate_composition_format |
| 06 | generate_composition_format | prompt | Generate Layer 2 composition format | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE | COMPOSITION_FORMAT_FILE | gatekeep_composition_format |
| 07 | gatekeep_composition_format | action | Validate format against criteria | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPOSITION_FORMAT_FILE | GATEKEEP_COMPOSITION_FORMAT_FILE | generate_output_format |
| 08 | generate_output_format | prompt | Generate Layer 3 output format | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE | OUTPUT_FORMAT_FILE | gatekeep_output_format |
| 09 | gatekeep_output_format | action | Validate format against criteria | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, OUTPUT_FORMAT_FILE | GATEKEEP_OUTPUT_FORMAT_FILE | generate_operational_workflow |
| 10 | generate_operational_workflow | prompt | Generate operational workflow design | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE | OPERATIONAL_WORKFLOW_FILE | gatekeep_operational_workflow |
| 11 | gatekeep_operational_workflow | action | Validate workflow against criteria | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, OPERATIONAL_WORKFLOW_FILE | GATEKEEP_OPERATIONAL_WORKFLOW_FILE | generate_composition_standard |
| 12 | generate_composition_standard | prompt | Generate the composition standard | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE | COMPOSITION_STANDARD_FILE | gatekeep_composition_standard |
| 13 | gatekeep_composition_standard | action | Validate standard against criteria | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPOSITION_STANDARD_FILE | GATEKEEP_COMPOSITION_STANDARD_FILE | generate_meta_composition_spec |
| 14 | generate_meta_composition_spec | prompt | Generate meta composition spec | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE | META_COMPOSITION_SPEC_FILE | generate_package |
| 15 | generate_package | prompt | Generate complete workflow package | WORKFLOW_SPEC_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE | embed_builder_spec |
| 16 | embed_builder_spec | action | Copy input spec to Specs/ | WORKFLOW_SPEC_FILE, WORKFLOW_MANIFEST_FILE | SPECS_BUILDER_SPEC_FILE | validate_package_deterministic |
| 17 | validate_package_deterministic | action | Run 11 static validation checks | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, STANDARDS_COMPOSITION_STANDARD_FILE, SPECS_BUILDER_SPEC_FILE | VALIDATION_REPORT_FILE | gatekeep_package |
| 18 | gatekeep_package | action | Evaluate package quality gate | WORKFLOW_SPEC_FILE, TEST_CRITERIA_FILE, WORKFLOW_MANIFEST_FILE, VALIDATION_REPORT_FILE | GATEKEEP_PACKAGE_FILE | review_package |
| 19 | review_package | prompt | Review package and suggest improvements | WORKFLOW_SPEC_FILE, WORKFLOW_MANIFEST_FILE, GATEKEEP_PACKAGE_FILE | REVIEW_FILE_SUGGESTED | promote_workflow_package |
| 20 | refine_package | prompt | Refine rejected package | WORKFLOW_SPEC_FILE, COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE, REVIEW_FILE_SUGGESTED | WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE | validate_package_deterministic |
| 21 | promote_workflow_package | action | Deploy 3-part output to workflows/ | WORKFLOW_MANIFEST_FILE | WORKFLOW_PACKAGE_DIR_FILE | step_completion |
| 22 | step_completion | action | Record final outcome | WORKFLOW_PACKAGE_DIR_FILE | (none -- meta.json sidecar) | (terminal) |

### Type Classification

| Type | Count | Steps |
|---|---|---|
| prompt | 12 | 01, 02, 03, 04, 06, 08, 10, 12, 14, 15, 19, 20 |
| action | 10 | 05, 07, 09, 11, 13, 16, 17, 18, 21, 22 |
| Total | 22 | |

### Routing Summary

**Success path (happy path):**
01 -> 02 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 ->
12 -> 13 -> 14 -> 15 -> 16 -> 17 -> 18 -> 19 -> 21 -> 22 -> END

**Refine loop A (Foundation):**
02 --REJECT--> 03 -> 02 (max 2 iterations)

**Refine loop B (Component Schema):**
05 --REJECT--> 04 -> 05 (max 2 iterations)

**Refine loop C (Composition Format):**
07 --REJECT--> 06 -> 07 (max 2 iterations)

**Refine loop D (Output Format):**
09 --REJECT--> 08 -> 09 (max 2 iterations)

**Refine loop E (Operational Workflow):**
11 --REJECT--> 10 -> 11 (max 2 iterations)

**Refine loop F (Composition Standard):**
13 --REJECT--> 12 -> 13 (max 2 iterations)

**Refine loop G (Package Gate):**
18 --REJECT--> 15 -> 16 -> 17 -> 18 (max 2 iterations)

**Refine loop H (Package Review):**
19 --REJECT--> 20 -> 16 -> 17 -> 18 -> 19 (max 2 iterations)

### Review/Refine Loop Design

| Loop ID | Name | Review Step | Refine Step | Max Iterations | Exhausted Code | Exhausted Class |
|---|---|---|---|---|---|---|
| LOOP-A | Foundation Review | review_test_criteria (02) | refine_test_criteria (03) | 2 | TEST_CRITERIA_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-B | Component Schema Gate | gatekeep_component_schema (05) | generate_component_schema (04) | 2 | COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-C | Composition Format Gate | gatekeep_composition_format (07) | generate_composition_format (06) | 2 | COMPOSITION_FORMAT_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-D | Output Format Gate | gatekeep_output_format (09) | generate_output_format (08) | 2 | OUTPUT_FORMAT_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-E | Operational Workflow Gate | gatekeep_operational_workflow (11) | generate_operational_workflow (10) | 2 | OPERATIONAL_WORKFLOW_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-F | Composition Standard Gate | gatekeep_composition_standard (13) | generate_composition_standard (12) | 2 | COMPOSITION_STANDARD_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-G | Package Gate | gatekeep_package (18) | generate_package (15) | 2 | PACKAGE_GATEKEEP_EXHAUSTED | HUMAN_RETRY_REQUIRED |
| LOOP-H | Package Review | review_package (19) | refine_package (20) | 2 | PACKAGE_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED |

### Artifact Contracts

#### Input Artifacts

| Artifact Key | Description | Required | Source |
|---|---|---|---|
| WORKFLOW_SPEC_FILE | Composition system specification | Yes | External (user-provided) |

#### Output Artifacts

| Artifact Key | Description | Produced By | Phase | Filename Pattern |
|---|---|---|---|---|
| TEST_CRITERIA_FILE | Acceptance criteria | generate_test_criteria (01) | 1 | TEST_CRITERIA-{seq}.md |
| REVIEW_TEST_CRITERIA_FILE | Review verdict | review_test_criteria (02) | 1 | REVIEW_TEST_CRITERIA-{seq}.md |
| COMPONENT_SCHEMA_FILE | Layer 1 component schema | generate_component_schema (04) | 2 | COMPONENT_SCHEMA-{seq}.md |
| GATEKEEP_COMPONENT_SCHEMA_FILE | Gatekeep verdict | gatekeep_component_schema (05) | 2 | GATEKEEP_COMPONENT_SCHEMA-{seq}.md |
| COMPOSITION_FORMAT_FILE | Layer 2 composition format | generate_composition_format (06) | 3 | COMPOSITION_FORMAT-{seq}.md |
| GATEKEEP_COMPOSITION_FORMAT_FILE | Gatekeep verdict | gatekeep_composition_format (07) | 3 | GATEKEEP_COMPOSITION_FORMAT-{seq}.md |
| OUTPUT_FORMAT_FILE | Layer 3 output format | generate_output_format (08) | 4 | OUTPUT_FORMAT-{seq}.md |
| GATEKEEP_OUTPUT_FORMAT_FILE | Gatekeep verdict | gatekeep_output_format (09) | 4 | GATEKEEP_OUTPUT_FORMAT-{seq}.md |
| OPERATIONAL_WORKFLOW_FILE | Operational workflow design | generate_operational_workflow (10) | 5 | OPERATIONAL_WORKFLOW-{seq}.md |
| GATEKEEP_OPERATIONAL_WORKFLOW_FILE | Gatekeep verdict | gatekeep_operational_workflow (11) | 5 | GATEKEEP_OPERATIONAL_WORKFLOW-{seq}.md |
| COMPOSITION_STANDARD_FILE | Composition standard | generate_composition_standard (12) | 6 | COMPOSITION_STANDARD-{seq}.md |
| GATEKEEP_COMPOSITION_STANDARD_FILE | Gatekeep verdict | gatekeep_composition_standard (13) | 6 | GATEKEEP_COMPOSITION_STANDARD-{seq}.md |
| META_COMPOSITION_SPEC_FILE | Meta composition spec | generate_meta_composition_spec (14) | 7 | META_COMPOSITION_SPEC-{seq}.md |
| WORKFLOW_MANIFEST_FILE | workflow.toml | generate_package (15) | 8 | workflow.toml |
| WORKFLOW_EXTENSIONS_FILE | context_extensions.py | generate_package (15) | 8 | context_extensions.py |
| WORKFLOW_ACTIONS_FILE | actions.py | generate_package (15) | 8 | actions.py |
| WORKFLOW_PROMPTS_INDEX_FILE | Prompt index | generate_package (15) | 8 | prompts/index.txt |
| WORKFLOW_README_FILE | README.md | generate_package (15) | 8 | README.md |
| STANDARDS_COMPOSITION_STANDARD_FILE | Standards/COMPOSITION_STANDARD.md | generate_package (15) | 8 | Standards/COMPOSITION_STANDARD.md |
| SPECS_BUILDER_SPEC_FILE | Specs/{builder_name}.md | embed_builder_spec (16) | 8 | Specs/{builder_name}.md |
| VALIDATION_REPORT_FILE | Validation report | validate_package_deterministic (17) | 8 | VALIDATION_REPORT-{seq}.md |
| GATEKEEP_PACKAGE_FILE | Package gate verdict | gatekeep_package (18) | 8 | GATEKEEP_PACKAGE-{seq}.md |
| REVIEW_FILE_SUGGESTED | Package review | review_package (19) | 8 | REVIEW_SUGGESTED-{seq}.md |
| WORKFLOW_PACKAGE_DIR_FILE | Promoted package path | promote_workflow_package (21) | 9 | WORKFLOW_PACKAGE_DIR-{seq}.txt |

### Action Specifications

#### Action 1: embed_builder_spec

| Property | Value |
|---|---|
| Step number | 16 |
| Step name | embed_builder_spec |
| Step type | action |
| Coder role | validation_standard |
| Phase | 8 (Package Assembly) |

**Purpose:** Copy the input WORKFLOW_SPEC_FILE into the output
Specs/ directory. Creates Specs/ if it does not exist.

**Required inputs:** WORKFLOW_SPEC_FILE, WORKFLOW_MANIFEST_FILE
**Produces:** SPECS_BUILDER_SPEC_FILE

**Implementation:**
```python
@action("embed_builder_spec")
def embed_builder_spec(*, context, state, step_cfg, project_root):
    """Copy the input spec into the output Specs/ folder."""
    spec_path = Path(context["WORKFLOW_SPEC_FILE"])
    output_dir = Path(context["WORKFLOW_MANIFEST_FILE"]).parent
    specs_dir = output_dir / "Specs"
    specs_dir.mkdir(exist_ok=True)
    target = specs_dir / f"{spec_path.stem}.md"
    shutil.copy2(spec_path, target)
    return ActionResult(
        status="APPROVED",
        remark=f"Embedded builder spec at {target}",
        artifacts={"SPECS_BUILDER_SPEC_FILE": str(target)},
    )
```

#### Action 2: validate_package_deterministic

| Property | Value |
|---|---|
| Step number | 17 |
| Step name | validate_package_deterministic |
| Step type | action |
| Coder role | validation_standard |
| Phase | 8 (Package Assembly) |

**Purpose:** Run 11 deterministic static validation checks on the
generated workflow package.

**Required inputs:** WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE,
WORKFLOW_ACTIONS_FILE, STANDARDS_COMPOSITION_STANDARD_FILE,
SPECS_BUILDER_SPEC_FILE
**Produces:** VALIDATION_REPORT_FILE

**Validation checks (11):**

| Check # | Name | Description | Severity |
|---|---|---|---|
| 1 | TOML Parse Validity | workflow.toml parses without errors | CRITICAL |
| 2 | Python Syntax | context_extensions.py and actions.py compile | CRITICAL |
| 3 | TYPE_CHECKING Detection | No runtime TYPE_CHECKING guards | HIGH |
| 4 | Artifact Binding Consistency | required_inputs references valid; produces unique | CRITICAL |
| 5 | Action Implementation Completeness | Every action step has matching function | CRITICAL |
| 6 | Prompt File Existence | Every prompt step has prompts/NN_{step_name}.txt | CRITICAL |
| 7 | Prompt Placeholder Consistency | Every {PLACEHOLDER} declared in step artifacts | CRITICAL |
| 8 | Artifact Key Coverage | Every key registered in register_artifact_keys() | CRITICAL |
| 9 | Standards Directory Existence | Standards/COMPOSITION_STANDARD.md exists | CRITICAL |
| 10 | Specs Directory Existence | Specs/ exists and contains at least one .md file | CRITICAL |
| 11 | Bidirectional Placeholder Check | All placeholders declared AND all declared artifacts used | CRITICAL |

#### Action 3: promote_workflow_package

| Property | Value |
|---|---|
| Step number | 21 |
| Step name | promote_workflow_package |
| Step type | action |
| Coder role | validation_standard |
| Phase | 9 (Promotion) |

**Purpose:** Deploy the validated 3-part output to the workflows/
directory. Enforces Standards/ and Specs/ presence.

**Required inputs:** WORKFLOW_MANIFEST_FILE
**Produces:** WORKFLOW_PACKAGE_DIR_FILE

**Enforcement:** If Standards/ or Specs/ is missing from the output,
the action REJECTS with:
"Required output directory '{name}/' not found. v4 requires 3-part
output: Standards/, Specs/, workflow files."

#### Action 4: step_completion

| Property | Value |
|---|---|
| Step number | 22 |
| Step name | step_completion |
| Step type | action |
| Coder role | validation_standard |
| Phase | 9 (Promotion) |

**Purpose:** Record the final outcome of the workflow execution.
Terminal step (O-004). No file artifacts produced.

**Required inputs:** WORKFLOW_PACKAGE_DIR_FILE
**Produces:** (none -- outcome recorded in meta.json sidecar)
**enable_notifications:** true

### Domain-Specific Requirements

- **Self-bootstrapping enforced:** Every generated meta builder MUST
  have its own spec in Specs/. The embed_builder_spec action ensures
  this.

- **Dynamic discovery mandatory:** generate_package and
  generate_meta_composition_spec prompts MUST use
  {DISCOVERED_COMPONENT_TYPES} instead of hardcoded type lists.

- **Promotion completeness:** The promote action MUST copy all 3
  parts. Missing Standards/ or Specs/ causes rejection.

- **Bidirectional artifact consistency:** Every {PLACEHOLDER} in a
  prompt must be declared in the step's artifacts, AND every artifact
  in the step's artifacts that looks like a placeholder must appear
  in the prompt.

- **Bootstrap chain integrity:** The spec in Specs/ must be
  content-identical to the WORKFLOW_SPEC_FILE that was the input.
  This enables the next version to use it as input.

- **VR-016 compliance:** Both generate_package and refine_package
  steps must declare STANDARDS_COMPOSITION_STANDARD_FILE in their
  produces lists.

### Self-Bootstrapping: v4 -> v5

v4 can generate v5 by feeding its own spec back into itself:

1. v4 is installed at workflows/workflow_builder_v4/
2. v4's Specs/ contains workflow_builder_v4.md (embedded by
   embed_builder_spec)
3. Submit workflow_builder_v4.md as WORKFLOW_SPEC_FILE to
   workflow_builder_v4
4. v4 processes the spec -> generates workflow_builder_v5/
   - Standards/COMPOSITION_STANDARD.md (v5's standard)
   - Specs/workflow_builder_v4.md (embedded copy of input)
   - workflow.toml, prompts/, actions.py, context_extensions.py
5. Promote workflow_builder_v5 to workflows/workflow_builder_v5/
6. v5 can now bootstrap v6 using its own Specs/ copy

**Bootstrap invariant:** Every version N embeds its own spec in
Specs/. Version N+1 is generated from that embedded spec. The chain
is unbroken.

---

## Self-Validation

### Section Completeness

| Section | Required | Present | Evidence |
|---|---|---|---|
| 1. Domain Overview | Yes | YES | Domain name, label, job prefix, purpose, 3-part output |
| 2. Component Schema | Yes | YES | 8 component types, 5+3 common properties, 16 validation rules |
| 3. Composition Format | Yes | YES | 9 binding rules, 6 patterns, override, placeholder resolution |
| 4. Output Format | Yes | YES | 3-part structure, 7+5 resolution rules, 12 quality requirements |
| 5. Operational Requirements | Yes | YES | 9 phases, 22 steps, artifact contracts, action specs |

**Verification:** All 5 required sections present. TC-078 through
TC-083 satisfied.

### Self-Bootstrap Capability

| Property | Value | Verified |
|---|---|---|
| self_bootstrap_capable | true | YES |
| Contains component types from standard | YES -- 8 types extracted | YES |
| Contains binding rules | YES -- 9 rules extracted | YES |
| Contains output structure | YES -- 3-part structure defined | YES |
| Contains step sequence | YES -- 22 steps with routing | YES |
| Contains action specifications | YES -- 4 actions specified | YES |
| Contains artifact contracts | YES -- 1 input + 24 output artifacts | YES |
| Can serve as sole WORKFLOW_SPEC_FILE input | YES -- all 5 sections self-contained | YES |

### Criteria Traceability

| Criteria | Status | Evidence |
|---|---|---|
| TC-078 | PASS | 5 sections: Domain Overview, Component Schema, Composition Format, Output Format, Operational Requirements |
| TC-079 | PASS | Section 1 includes domain name (workflow_builder), label (Workflow Builder v4), job prefix (WBUILD4), description, purpose, 3-part output definition |
| TC-080 | PASS | Section 2 covers 8 component types with properties and 16 validation rules from Phase 2 |
| TC-081 | PASS | Section 3 covers 9 binding rules, 6 workflow patterns, override mechanism, 4 placeholder data sources from Phase 3 |
| TC-082 | PASS | Section 4 covers 3-part output structure and resolution rules from Phase 4 |
| TC-083 | PASS | Section 5 covers 9 phases, 22-step sequence, 4 action specifications, artifact declarations. Self-bootstrapping capable. |

### Layer Boundary Compliance

| Check | Status | Evidence |
|---|---|---|
| Does not redefine Layer 1 (governance) content | PASS | Component types extracted from COMPOSITION_STANDARD-001.md |
| Does not redefine Layer 2 (platform) content | PASS | Binding rules reference composition standard |
| ASCII-only content | PASS | No em-dashes, curly quotes, or Unicode characters |
| No resolved filesystem paths in governance references | PASS | Uses filenames only |
| No scope invention | PASS | All content traces to upstream artifacts |

---

End of Meta Composition Spec Document
