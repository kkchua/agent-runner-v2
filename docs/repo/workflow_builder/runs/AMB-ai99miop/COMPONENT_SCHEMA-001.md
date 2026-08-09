---
doc_type: "component_schema"
lifecycle_status: "draft"
domain: "ar_meta_builder"
component_type_count: 8
---

# Component Schema (Layer 1)

## Overview

This document defines the Layer 1 component schema for the AR Meta Builder v1 composition system. The schema establishes the foundational building block library used to compose workflow definitions within the ar_meta_builder domain.

**Domain context:** The codebase_to_meta domain transforms codebase documentation into audience-specific Rich Markdown meta content files. The composition system uses 5 of the 8 universal component types to define its workflow: step_definition, role_policy, routing_pattern, prompt_pattern, and artifact_contract. The remaining 3 universal types (composition_standard, output_variance, domain_spec) are part of the universal component library but are not instantiated by this specific domain's workflow.

**Component type count:** 8 universal types defined in this schema.

**Schema pattern reference:** Each component type follows a common property structure (component_id, component_type, name, version, description) with type-specific extensions. Components are validated against global validation rules (VR-001 through VR-014) and type-specific constraints.

**Traceability:** All 5 domain-active component types trace directly to the input specification (codebase_to_meta_v1.md, Section 2). The 3 additional universal types are acknowledged in the specification (Section 2, paragraph 1: "This composition system uses 5 of the 8 universal component types") and are defined here for completeness of the universal schema.

---

## Common Properties

Every component instance in this schema shares the following common properties. These form the base structure that all 8 component types inherit.

### Required Common Properties

| Property | Type | Description |
|---|---|---|
| component_id | string | Unique identifier for this component instance. Format: {TYPE_PREFIX}-{NNN} where TYPE_PREFIX is derived from the component_type (e.g., STEP, ROLE, ROUTE, PROMPT, ARTIFACT, STD, VAR, DOM). |
| component_type | string | Must be one of the 8 defined type names: step_definition, role_policy, routing_pattern, prompt_pattern, artifact_contract, composition_standard, output_variance, domain_spec. |
| name | string | Human-readable name for the component. Used in documentation and display. |
| version | string | Semantic version of this component definition (e.g., "1.0.0"). |
| description | string | Purpose and scope of this component instance. |

### Optional Common Properties

| Property | Type | Description |
|---|---|---|
| duration_range | object | Expected execution duration with min and max values (e.g., {"min": "5s", "max": "30s"}). Applicable primarily to step_definition components. |
| platforms | array | List of platform identifiers where this component is valid (e.g., ["windows", "linux"]). |
| tags | array | Free-form labels for classification and search (e.g., ["action", "scan", "audit"]). |

---

## Component Types

### Type 1: step_definition

**Purpose:** Defines a single executable step within the workflow. Each step represents a discrete unit of work -- either a deterministic action (Python code) or a prompt-driven LLM invocation.

**Required/Optional:** Required. Every workflow must define at least one step.

**Cardinality:** One or more (1..N). The codebase_to_meta domain defines exactly 5 steps.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| step_name | string | Yes | Unique step identifier within the workflow (e.g., "scan_audiences"). |
| step_type | string | Yes | Either "prompt" (LLM-driven) or "action" (deterministic Python). |
| purpose | string | Yes | Human-readable description of what this step accomplishes. |
| produces | array | Yes | List of artifact keys produced by this step. |
| phase | string | No | The workflow phase this step belongs to (e.g., "Scan", "Generate"). |
| error_handling | object | No | Error handling rules including reject_codes and conditions. |

**Validation Rules:**
- step_name must be unique within the workflow.
- step_type must be either "prompt" or "action".
- produces must contain at least one artifact key for action steps.
- If step_type is "action", no role_policy reference is needed.
- If step_type is "prompt", a role_policy must reference this step.

**Example:**

```yaml
component_id: STEP-001
component_type: step_definition
name: scan_audiences
version: "1.0.0"
description: >
  Discover audience definitions from the audiences/ directory.
  Parses YAML frontmatter from each .md file to build an audience
  inventory with metadata.
step_name: scan_audiences
step_type: action
purpose: >
  Recursively scan AUDIENCE_DIR for .md files. Parse YAML frontmatter
  from each file. Build an audience inventory with audience_id, label,
  tone, focus_areas, exclude, section_structure, and file path.
produces:
  - AUDIENCE_INVENTORY_FILE
phase: Scan
duration_range:
  min: "1s"
  max: "10s"
error_handling:
  reject_codes:
    - code: NO_AUDIENCES_FOUND
      condition: "audiences/ directory missing or contains no .md files"
      classification: REJECT
    - code: DUPLICATE_AUDIENCE_ID
      condition: "Two files define the same audience_id"
      classification: REJECT
  warnings:
    - condition: "File has invalid YAML frontmatter"
      action: "log warning and skip"
tags:
  - action
  - scan
  - audit
```

---

### Type 2: role_policy

**Purpose:** Assigns a coder role (policy) to a prompt-type step. Determines which LLM persona and constraints are applied when executing the step. Action steps do not have role assignments.

**Required/Optional:** Required for each prompt-type step. Not applicable to action steps.

**Cardinality:** Zero or more (0..N). One role_policy per prompt-type step.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| step_name | string | Yes | The step this role policy applies to. Must reference a valid step_definition. |
| policy_name | string | Yes | The role/policy identifier (e.g., "architect_standard", "reviewer_standard"). Use "(action -- no role)" for action steps. |
| rationale | string | No | Explanation of why this role is appropriate for the step. |

**Validation Rules:**
- step_name must reference an existing step_definition.
- policy_name must not be assigned to action-type steps.
- Each prompt-type step must have exactly one role_policy.
- Action-type steps must not have a role_policy entry.

**Example:**

```yaml
component_id: ROLE-001
component_type: role_policy
name: generate_meta_content_role
version: "1.0.0"
description: >
  Assigns the architect_standard role to the generate_meta_content
  step. This role is appropriate for content generation from
  structured source documentation.
step_name: generate_meta_content
policy_name: architect_standard
rationale: >
  Content generation from structured source requires architectural
  analysis and synthesis skills. The architect_standard role provides
  the appropriate LLM persona for organizing technical documentation
  into audience-specific views.
```

---

### Type 3: routing_pattern

**Purpose:** Defines the control flow between steps. Specifies where execution goes on success (onsuccess) and on rejection/refinement request (on_reject_refine). Supports iteration limits and exhaustion codes.

**Required/Optional:** Required. Every workflow must define routing between its steps.

**Cardinality:** One per step (1..1 per step). Total count matches step count.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| step_name | string | Yes | The source step for this routing rule. |
| onsuccess | string | Yes | Target step on successful completion. Use "step_completion" for terminal steps. |
| on_reject_refine | string | No | Target step on rejection/rejection-refine. If absent, rejection terminates the workflow. |
| max_iterations | integer | No | Maximum number of times the reject-refine loop can execute. |
| exhaustion_code | string | No | Code emitted when max_iterations is reached. |
| exhaustion_classification | string | No | Classification of the exhaustion event (e.g., "HUMAN_RETRY_REQUIRED"). |

**Validation Rules:**
- step_name must reference an existing step_definition.
- onsuccess must reference an existing step_definition or "step_completion".
- on_reject_refine must reference an existing step_definition if present.
- max_iterations must be a positive integer if specified.
- exhaustion_code must be present if max_iterations is specified.
- Exactly one step must route to "step_completion" as its onsuccess target.
- Routing must not create unresolvable cycles (refine loops must have max_iterations).

**Example:**

```yaml
component_id: ROUTE-003
component_type: routing_pattern
name: review_meta_content_routing
version: "1.0.0"
description: >
  Routes from review_meta_content. On success, proceeds to
  publish_meta_content. On rejection, routes to
  refine_meta_content with a maximum of 2 iterations. If
  refinement is exhausted, emits META_CONTENT_REVIEW_EXHAUSTED
  with classification HUMAN_RETRY_REQUIRED.
step_name: review_meta_content
onsuccess: publish_meta_content
on_reject_refine: refine_meta_content
max_iterations: 2
exhaustion_code: META_CONTENT_REVIEW_EXHAUSTED
exhaustion_classification: HUMAN_RETRY_REQUIRED
```

---

### Type 4: prompt_pattern

**Purpose:** Defines reusable sections that are assembled into prompt templates for prompt-type steps. Each pattern represents a structural block within a prompt (e.g., reference inputs, generation tasks, self-critique instructions).

**Required/Optional:** Required for prompt-type steps. Not applicable to action steps.

**Cardinality:** One or more per prompt-type step (1..N). The codebase_to_meta domain defines 6 patterns.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| pattern_name | string | Yes | Identifier for this prompt pattern (e.g., "reference_inputs", "generation_tasks"). |
| applied_to | array | Yes | List of step_names this pattern applies to. |
| content_description | string | Yes | Description of what this pattern contributes to the prompt. |
| placeholder_style | string | No | Convention for placeholders within this pattern (e.g., "{PLACEHOLDER}"). |

**Validation Rules:**
- pattern_name must be unique within the schema.
- applied_to must reference existing prompt-type step_definitions.
- Every prompt-type step must have at least the reference_inputs, self_critic, self_validation, and output_instructions patterns applied.
- Patterns applied to generate or refine steps should include generation_tasks and forbidden_content.

**Example:**

```yaml
component_id: PROMPT-001
component_type: prompt_pattern
name: reference_inputs
version: "1.0.0"
description: >
  Lists input artifacts with {PLACEHOLDER} paths at the top of
  each prompt. Provides the LLM with explicit references to all
  input files it should read before generating output.
pattern_name: reference_inputs
applied_to:
  - generate_meta_content
  - review_meta_content
  - refine_meta_content
content_description: >
  Enumerates all input artifacts the step requires. Each artifact
  is referenced by its {ARTIFACT_KEY} placeholder which is resolved
  to an absolute path at runtime. This pattern ensures the LLM
  knows exactly which files to read before producing output.
placeholder_style: "{ARTIFACT_KEY}"
```

---

### Type 5: artifact_contract

**Purpose:** Defines a named output artifact produced by the workflow. Specifies the artifact key, filename pattern, which step produces it, and whether it is required.

**Required/Optional:** Required. Every workflow must define its output artifacts.

**Cardinality:** One or more (1..N). The codebase_to_meta domain defines 5 artifacts.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| artifact_key | string | Yes | Unique key identifying this artifact (e.g., "AUDIENCE_INVENTORY_FILE"). |
| filename_pattern | string | Yes | Pattern for the output filename. May include placeholders like {date}, {seq}, {audience_id}, {AUD}, {slug}. |
| produced_by | string | Yes | The step_name that produces this artifact. |
| required | boolean | Yes | Whether this artifact must be produced for workflow success. |
| description | string | No | Human-readable description of the artifact's purpose. |

**Validation Rules:**
- artifact_key must be unique across the entire schema.
- produced_by must reference an existing step_definition.
- filename_pattern must not contain filesystem-incompatible characters.
- Every step_definition's produces array must reference valid artifact_keys.
- Required artifacts must be produced by a step that is always executed (not conditional-only).

**Example:**

```yaml
component_id: ARTIFACT-002
component_type: artifact_contract
name: META_CONTENT_FILE
version: "1.0.0"
description: >
  One Rich Markdown meta content file per discovered audience.
  Each file is self-contained, audience-faithful, and source-attributed.
  The audience_id becomes the output subdirectory name and the AUD
  code in the filename is derived from audience_id at runtime.
artifact_key: META_CONTENT_FILE
filename_pattern: "{audience_id}/META-{AUD}-{date}-{seq}.md"
produced_by: generate_meta_content
required: true
```

---

### Type 6: composition_standard

**Purpose:** Defines a reusable composition standard that governs how component types are assembled into workflow packages. Establishes naming conventions, required schema sections, and extensibility rules for the domain.

**Required/Optional:** Optional. Not instantiated by the codebase_to_meta domain's component schema directly; consumed at Phase 6 (composition standard generation).

**Cardinality:** Zero or more (0..N).

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| standard_name | string | Yes | Identifier for the standard (e.g., "CODEBASE_TO_META_STANDARD"). |
| standard_version | string | Yes | Semantic version of the standard. |
| component_type_count | integer | Yes | Number of component types this standard defines or references. |
| schema_sections | array | No | List of sections that generated schemas must contain. |
| extensibility_model | string | No | Description of how new types or definitions can be added. |

**Validation Rules:**
- standard_name must be unique within the schema.
- standard_version must follow semantic versioning format (MAJOR.MINOR.PATCH).
- component_type_count must match the actual number of type definitions in the standard body.
- This type is part of the universal component library. The codebase_to_meta domain acknowledges 8 universal types (spec Section 2, paragraph 1) but does not instantiate composition_standard at the component schema layer.

**Example:**

```yaml
component_id: STD-001
component_type: composition_standard
name: CODEBASE_TO_META_STANDARD
version: "1.0.0"
description: >
  Universal composition standard for the codebase_to_meta domain.
  Defines the schema sections, component type expectations, and
  extensibility model for workflow packages in this domain.
  Note: This type is part of the universal component library and
  is not directly instantiated at the Layer 1 component schema
  level for this domain. It is consumed at Phase 6 when the
  composition standard artifact is generated.
standard_name: CODEBASE_TO_META_STANDARD
standard_version: "1.0.0"
component_type_count: 8
schema_sections:
  - component_schema
  - composition_format
  - output_format
  - operational_requirements
extensibility_model: >
  New audience definitions can be added by dropping .md files
  into the audiences/ directory. New component types may be added
  to the universal library without breaking existing compositions
  as long as common properties are preserved.
```

---

### Type 7: output_variance

**Purpose:** Defines variations in output format that a domain may produce. Captures resolution rules, quality requirements, and format constraints that differ across audiences or output targets.

**Required/Optional:** Optional. Not instantiated by the codebase_to_meta domain's component schema directly; output format details are handled at Phase 4 (output format generation).

**Cardinality:** Zero or more (0..N).

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| variance_name | string | Yes | Identifier for this output variance (e.g., "developer_output", "executive_output"). |
| target_audience | string | No | The audience_id this variance applies to. |
| resolution_rules | array | No | List of resolution rule identifiers (e.g., "RR-META-001"). |
| quality_requirements | array | No | List of quality requirement identifiers (e.g., "QR-META-001"). |
| frontmatter_schema | object | No | YAML frontmatter fields required for this output variant. |

**Validation Rules:**
- variance_name must be unique within the schema.
- target_audience must reference a valid audience_id if specified.
- resolution_rules must follow the naming convention RR-{DOMAIN}-{NNN}.
- quality_requirements must follow the naming convention QR-{DOMAIN}-{NNN}.
- This type is part of the universal component library. The codebase_to_meta domain acknowledges 8 universal types but does not instantiate output_variance at the component schema layer. Output format variations are defined at Phase 4 (Layer 3).

**Example:**

```yaml
component_id: VAR-001
component_type: output_variance
name: developer_output_variance
version: "1.0.0"
description: >
  Defines the output format variance for the developer audience.
  Captures the resolution rules (RR-META-001 through RR-META-007)
  and quality requirements (QR-META-001 through QR-META-007) that
  apply to developer-targeted meta content files. Note: This type
  is part of the universal component library and is not directly
  instantiated at the Layer 1 component schema level for this
  domain. Output format details are captured at Phase 4.
variance_name: developer_output_variance
target_audience: developer
resolution_rules:
  - RR-META-001
  - RR-META-002
  - RR-META-003
  - RR-META-004
  - RR-META-005
  - RR-META-006
  - RR-META-007
quality_requirements:
  - QR-META-001
  - QR-META-002
  - QR-META-003
  - QR-META-004
  - QR-META-005
  - QR-META-006
  - QR-META-007
frontmatter_schema:
  title: string
  audience: string
  audience_label: string
  generated_date: string
  source_version: string
  section_count: integer
```

---

### Type 8: domain_spec

**Purpose:** Captures domain-level metadata and context that applies across all components in a composition. Includes domain name, label, job prefix, workflow pattern, and contextual variables.

**Required/Optional:** Optional. Not instantiated by the codebase_to_meta domain's component schema directly; domain metadata is captured in the workflow spec frontmatter and context_extensions.

**Cardinality:** Zero or one (0..1) per domain.

**Type-Specific Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| domain_name | string | Yes | Machine-readable domain identifier (e.g., "codebase_to_meta"). |
| domain_label | string | Yes | Human-readable domain name (e.g., "Codebase to Meta Content v1"). |
| job_prefix | string | Yes | Prefix for job identifiers (e.g., "META"). |
| workflow_pattern | string | Yes | Execution pattern: "mixed", "prompt-only", or "action-only". |
| context_variables | array | No | List of context variable names and their resolved paths. |
| purpose | string | No | High-level description of what this domain accomplishes. |

**Validation Rules:**
- domain_name must be unique across all domains.
- job_prefix must be a non-empty uppercase string.
- workflow_pattern must be one of: "mixed", "prompt-only", "action-only".
- context_variables entries must include both a variable name and a resolved path.
- This type is part of the universal component library. The codebase_to_meta domain acknowledges 8 universal types but does not instantiate domain_spec at the component schema layer. Domain metadata is captured in the workflow spec (codebase_to_meta_v1.md, Section 1) frontmatter.

**Example:**

```yaml
component_id: DOM-001
component_type: domain_spec
name: codebase_to_meta_domain
version: "1.0.0"
description: >
  Domain-level metadata for the codebase_to_meta composition
  system. Captures the domain identity, job prefix, workflow
  pattern, and context variables. Note: This type is part of
  the universal component library and is not directly instantiated
  at the Layer 1 component schema level for this domain. Domain
  metadata is captured in the workflow spec frontmatter.
domain_name: codebase_to_meta
domain_label: "Codebase to Meta Content v1"
job_prefix: META
workflow_pattern: mixed
context_variables:
  - name: CODEBASE_DOC_ROOT
    resolved_path: "{repo_root}/docs/repo/codebase/current/"
  - name: META_CONTENT_ROOT
    resolved_path: "{repo_root}/docs/repo/meta_content/"
  - name: AUDIENCE_DIR
    resolved_path: "{workflow_package}/audiences/"
purpose: >
  Transforms codebase documentation into audience-specific Rich
  Markdown meta content files via plugin-extensible audience
  definitions.
```

---

## Validation Rules (Global)

The following validation rules apply across all component types in the schema. Rules are organized by severity: CRITICAL rules must pass for any composition to be valid; HIGH rules must pass for production-quality output.

### CRITICAL Severity

| Rule ID | Rule Name | Description |
|---|---|---|
| VR-001 | Audiences directory exists | The audiences/ directory must exist with at least one .md file. Checked by scan_audiences action step. |
| VR-002 | Frontmatter validity | Each audience .md file must have valid YAML frontmatter containing all required fields: audience_id, label, tone, focus_areas, section_structure. |
| VR-003 | Unique audience_id | No two audience definition files may declare the same audience_id. Checked by scan_audiences with reject_code DUPLICATE_AUDIENCE_ID. |
| VR-004 | Codebase manifest exists | The file CODEBASE_DOC_ROOT/codebase_manifest.json must exist. Required by generate_meta_content to understand the full doc inventory. |
| VR-005 | No hallucination | No information may be invented beyond what codebase documentation provides. Every factual claim must trace to a source file. |
| VR-006 | Component ID uniqueness | Every component_id must be unique within the schema. No two components may share the same identifier. |
| VR-007 | Step name uniqueness | Every step_name must be unique within the workflow. No two step_definitions may share the same step_name. |
| VR-008 | Routing completeness | Every step must have exactly one routing_pattern defining its onsuccess target. Exactly one step must route to step_completion. |

### HIGH Severity

| Rule ID | Rule Name | Description |
|---|---|---|
| VR-009 | Self-contained output | Each meta content file must be readable without reference to source codebase documentation. |
| VR-010 | Source attribution | Every factual claim in output must trace to a specific codebase doc file via inline reference. |
| VR-011 | Audience fidelity | Tone, focus_areas, and section_structure in output must match the corresponding audience definition frontmatter. |
| VR-012 | YAML frontmatter on output | Each generated meta content file must include required frontmatter fields: title, audience, audience_label, generated_date, source_version, section_count. |
| VR-013 | Artifact key coverage | Every artifact_key referenced in a step_definition's produces array must have a corresponding artifact_contract definition. |
| VR-014 | Role-step consistency | Every prompt-type step must have exactly one role_policy entry. Action-type steps must not have role_policy entries. |

---

## Extensibility Model

The component schema supports extensibility at three levels without breaking existing compositions.

### Level 1: Adding New Component Instances

New instances of existing component types can be added freely:
- New step_definitions can be added to extend the workflow.
- New audience definition files can be dropped into audiences/ without any workflow logic changes.
- New artifact_contracts can be defined for additional outputs.

This is the primary extensibility mechanism for the codebase_to_meta domain. The plugin-extensible audience model (spec Section 1.1) allows new audiences by simply adding a .md file.

### Level 2: Adding New Component Types to the Universal Library

New component types can be added to the universal library (beyond the 8 defined here) provided:
- The new type includes all 5 required common properties (component_id, component_type, name, version, description).
- The new type does not alter or remove any existing type's properties.
- The new type's validation rules do not conflict with existing global rules (VR-001 through VR-014).
- Existing compositions remain valid without modification.

### Level 3: Domain Adaptation

Different domains may use different subsets of the 8 universal types:
- The codebase_to_meta domain uses 5 of 8 types.
- Other domains may use different subsets or additional types from the universal library.
- Each domain's component schema declares which types it instantiates.
- Unused types remain defined in the universal schema but carry no instances.

### Backward Compatibility Guarantee

Any composition valid under version N of this schema remains valid under version N+1, provided:
- No required common property is removed.
- No existing type-specific property changes from optional to required.
- No validation rule severity is increased from HIGH to CRITICAL for existing rules.
- New types are added as optional, not required.

---

## Component File Format

### Storage Format

Components are stored as YAML documents. Each file contains a single component instance with all required common properties and type-specific properties populated.

### File Naming Convention

Component files follow the naming pattern: {COMPONENT_ID}.yaml

Examples:
- STEP-001.yaml
- ROLE-001.yaml
- ROUTE-003.yaml
- PROMPT-001.yaml
- ARTIFACT-002.yaml

### Exchange Format

For bulk exchange (e.g., embedding in workflow packages), components may be aggregated into a single YAML document using a top-level components array:

```yaml
schema_version: "1.0.0"
domain: codebase_to_meta
components:
  - component_id: STEP-001
    component_type: step_definition
    ...
  - component_id: ROLE-001
    component_type: role_policy
    ...
```

### Frontmatter Requirements

When a component file is part of a larger document (such as this schema document), the document's YAML frontmatter must include:
- doc_type: "component_schema"
- lifecycle_status: "draft" | "review" | "approved" | "deprecated"
- domain: the domain identifier
- component_type_count: total number of component types defined

### Validation at Load Time

When a component file is loaded:
1. Parse YAML and verify syntactic validity.
2. Check all 5 required common properties are present.
3. Verify component_type matches one of the 8 defined types.
4. Validate type-specific required properties.
5. Check global validation rules (VR-001 through VR-014) where applicable.
6. Verify component_id uniqueness against already-loaded components.

---

## Self-Validation

This section verifies the completeness of the component schema document.

### Type Coverage

| # | Component Type | Defined | Properties Listed | Validation Rules | Example Provided | Domain Status |
|---|---|---|---|---|---|---|
| 1 | step_definition | Yes | Yes | Yes | Yes (STEP-001 scan_audiences) | Active (5 instances) |
| 2 | role_policy | Yes | Yes | Yes | Yes (ROLE-001 generate_meta_content_role) | Active (3 instances) |
| 3 | routing_pattern | Yes | Yes | Yes | Yes (ROUTE-003 review_meta_content_routing) | Active (5 instances) |
| 4 | prompt_pattern | Yes | Yes | Yes | Yes (PROMPT-001 reference_inputs) | Active (6 instances) |
| 5 | artifact_contract | Yes | Yes | Yes | Yes (ARTIFACT-002 META_CONTENT_FILE) | Active (5 instances) |
| 6 | composition_standard | Yes | Yes | Yes | Yes (STD-001 CODEBASE_TO_META_STANDARD) | Universal (not instantiated) |
| 7 | output_variance | Yes | Yes | Yes | Yes (VAR-001 developer_output_variance) | Universal (not instantiated) |
| 8 | domain_spec | Yes | Yes | Yes | Yes (DOM-001 codebase_to_meta_domain) | Universal (not instantiated) |

### Verification Checklist

- [x] All 8 component types are defined (step_definition, role_policy, routing_pattern, prompt_pattern, artifact_contract, composition_standard, output_variance, domain_spec).
- [x] Each type has: purpose, required/optional status, cardinality, type-specific properties table, validation rules, and a complete YAML example.
- [x] 5 required common properties are defined (component_id, component_type, name, version, description).
- [x] 3 optional common properties are defined (duration_range, platforms, tags).
- [x] 14 global validation rules (VR-001 through VR-014) are defined with severity levels.
- [x] The 5 domain-active types (step_definition, role_policy, routing_pattern, prompt_pattern, artifact_contract) include all content from spec Section 2.
- [x] The 5 step_definitions match spec Section 2.1: scan_audiences (action), generate_meta_content (prompt), review_meta_content (prompt), refine_meta_content (prompt), publish_meta_content (action).
- [x] The role assignments match spec Section 2.2.
- [x] The routing patterns match spec Section 2.3 including the META_CONTENT_REVIEW_EXHAUSTED exhaustion code.
- [x] The 6 prompt patterns match spec Section 2.4 with correct step applicability.
- [x] The 5 artifact contracts match spec Section 2.5.
- [x] The 9 validation rules from spec Section 2.7 are incorporated into VR-001 through VR-014.
- [x] Extensibility model covers 3 levels of extension.
- [x] Component file format defines storage, naming, exchange, and loading validation.
- [x] ASCII-only content. No em-dashes, curly quotes, or Unicode characters.
- [x] All content traces to the input specification (codebase_to_meta_v1.md). No scope invention.

### Domain Instance Summary

The codebase_to_meta domain instantiates the following components:

**step_definition (5 instances):**
- STEP-001: scan_audiences (action)
- STEP-002: generate_meta_content (prompt)
- STEP-003: review_meta_content (prompt)
- STEP-004: refine_meta_content (prompt)
- STEP-005: publish_meta_content (action)

**role_policy (3 instances):**
- ROLE-001: generate_meta_content -> architect_standard
- ROLE-002: review_meta_content -> reviewer_standard
- ROLE-003: refine_meta_content -> architect_standard

**routing_pattern (5 instances):**
- ROUTE-001: scan_audiences -> generate_meta_content
- ROUTE-002: generate_meta_content -> review_meta_content
- ROUTE-003: review_meta_content -> publish_meta_content (onsuccess) / refine_meta_content (on_reject_refine, max 2)
- ROUTE-004: refine_meta_content -> review_meta_content
- ROUTE-005: publish_meta_content -> step_completion

**prompt_pattern (6 instances):**
- PROMPT-001: reference_inputs (all 3 prompt steps)
- PROMPT-002: generation_tasks (generate, refine)
- PROMPT-003: self_critic (all 3 prompt steps)
- PROMPT-004: self_validation (all 3 prompt steps)
- PROMPT-005: forbidden_content (generate, refine)
- PROMPT-006: output_instructions (all 3 prompt steps)

**artifact_contract (5 instances):**
- ARTIFACT-001: AUDIENCE_INVENTORY_FILE
- ARTIFACT-002: META_CONTENT_FILE
- ARTIFACT-003: META_INDEX_FILE
- ARTIFACT-004: REVIEW_FILE_SUGGESTED
- ARTIFACT-005: META_MANIFEST_FILE

**composition_standard, output_variance, domain_spec:** Defined as universal types but not instantiated at the Layer 1 component schema level for this domain. These types are consumed at later phases (Phase 4 for output_variance, Phase 6 for composition_standard) or captured in the workflow spec frontmatter (domain_spec).

---

**End of Component Schema Document**
