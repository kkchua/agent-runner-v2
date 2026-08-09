---
doc_type: "composition_standard"
lifecycle_status: "draft"
standard_name: "AR_META_BUILDER_STANDARD"
standard_version: "1.0.0"
component_type_count: 8
schema_sections:
  - component_schema
  - composition_format
  - output_format
domain: "codebase_to_meta"
spec_reference: "codebase_to_meta_v1.md"
---

# Composition Standard: AR_META_BUILDER_STANDARD

## Overview

**Standard name:** AR_META_BUILDER_STANDARD

**Standard version:** 1.0.0

**Domain context:** The codebase_to_meta domain transforms codebase documentation (approximately 155 files under docs/repo/codebase/current/) into audience-specific Rich Markdown meta content files. The transformation is driven by plugin-extensible audience definitions. Each audience is a Markdown file with YAML frontmatter placed in the workflow's audiences/ directory. The set of audiences is extensible without workflow logic changes.

**Standard purpose:** This composition standard defines the schema contract for the codebase_to_meta workflow package. It establishes the component type library, the binding rules that assemble components into compositions, the output format requirements for generated meta content, and the extensibility model that allows new audience definitions and component types to be added without breaking existing compositions.

**Traceability:** All content in this standard traces to the input specification (codebase_to_meta_v1.md). The standard name "AR_META_BUILDER_STANDARD" is declared in the specification (Section 1 header, standard field). The 8 component types correspond to the universal component library defined in the specification Section 2 and elaborated in the component schema (COMPONENT_SCHEMA.md). The 3 schema sections correspond to the 3 layers of the composition architecture.

**Schema sections:** This standard requires exactly 3 schema sections in compliant workflow definitions:

1. Component Schema -- Defines the building block library (Layer 1).
2. Composition Format -- Defines how components are bound into compositions (Layer 2).
3. Output Format -- Defines the concrete output structure and quality requirements (Layer 3).

---

## Component Schema (Layer 1)

This section defines the 8 universal component types that form the building block library for the codebase_to_meta domain. Each type specifies its purpose, required properties, cardinality, and validation rules.

The codebase_to_meta domain uses 5 of these 8 types as domain-active components (step_definition, role_policy, routing_pattern, prompt_pattern, artifact_contract). The remaining 3 types (composition_standard, output_variance, domain_spec) are part of the universal library and are consumed at later phases of the meta-builder workflow.

**Common properties inherited by all 8 types:**

| Property | Type | Required | Description |
|---|---|---|---|
| component_id | string | Yes | Unique identifier. Format: {TYPE_PREFIX}-{NNN}. |
| component_type | string | Yes | Must be one of the 8 defined type names. |
| name | string | Yes | Human-readable name for display and documentation. |
| version | string | Yes | Semantic version (e.g., "1.0.0"). |
| description | string | Yes | Purpose and scope of this component instance. |

### Type Definitions

#### Type 1: step_definition

**Purpose:** Defines a single executable step within the workflow. Each step represents a discrete unit of work -- either a deterministic action (Python code) or a prompt-driven LLM invocation.

**Cardinality:** One or more (1..N). The codebase_to_meta domain defines exactly 5 steps.

**Required properties:**

| Property | Type | Description |
|---|---|---|
| step_name | string | Unique step identifier within the workflow. |
| step_type | string | Either "prompt" (LLM-driven) or "action" (deterministic Python). |
| purpose | string | Human-readable description of what this step accomplishes. |
| produces | array | List of artifact keys produced by this step. |

**Domain instances (5):**

| step_name | step_type | Phase | Purpose |
|---|---|---|---|
| scan_audiences | action | Scan | Discover audience definitions from audiences/ directory. |
| generate_meta_content | prompt | Generate | Produce one meta content file per discovered audience. |
| review_meta_content | prompt | Review | Quality review of all generated meta files. |
| refine_meta_content | prompt | Refine | Fix issues found in review (conditional). |
| publish_meta_content | action | Publish | Backup, history, copy to current/ with manifest. |

**Validation rules:**
- step_name must be unique within the workflow.
- step_type must be either "prompt" or "action".
- produces must contain at least one artifact key for action steps.
- If step_type is "action", no role_policy reference is needed.
- If step_type is "prompt", a role_policy must reference this step.

**Traceability:** Spec Section 2.1 (5 steps across 5 phases).

#### Type 2: role_policy

**Purpose:** Assigns a coder role (policy) to a prompt-type step. Determines which LLM persona and constraints are applied when executing the step. Action steps do not have role assignments.

**Cardinality:** Zero or more (0..N). One role_policy per prompt-type step.

**Required properties:**

| Property | Type | Description |
|---|---|---|
| step_name | string | The step this role policy applies to. |
| policy_name | string | The role/policy identifier (e.g., "architect_standard"). |

**Domain instances (3):**

| step_name | policy_name | Rationale |
|---|---|---|
| generate_meta_content | architect_standard | Content generation from structured source. |
| review_meta_content | reviewer_standard | Quality review against constraints. |
| refine_meta_content | architect_standard | Content regeneration addressing review. |

**Validation rules:**
- step_name must reference an existing step_definition.
- policy_name must not be assigned to action-type steps.
- Each prompt-type step must have exactly one role_policy.
- Action-type steps must not have a role_policy entry.

**Traceability:** Spec Section 2.2 (role assignments for 3 prompt steps).

#### Type 3: routing_pattern

**Purpose:** Defines the control flow between steps. Specifies where execution goes on success (onsuccess) and on rejection/refinement request (on_reject_refine). Supports iteration limits and exhaustion codes.

**Cardinality:** One per step (1..1 per step). Total count matches step count.

**Required properties:**

| Property | Type | Description |
|---|---|---|
| step_name | string | The source step for this routing rule. |
| onsuccess | string | Target step on successful completion. |

**Optional properties:**

| Property | Type | Description |
|---|---|---|
| on_reject_refine | string | Target step on rejection/rejection-refine. |
| max_iterations | integer | Maximum number of reject-refine loop iterations. |
| exhaustion_code | string | Code emitted when max_iterations is reached. |
| exhaustion_classification | string | Classification of the exhaustion event. |

**Domain instances (5):**

| step_name | onsuccess | on_reject_refine | Max iterations |
|---|---|---|---|
| scan_audiences | generate_meta_content | -- | -- |
| generate_meta_content | review_meta_content | -- | -- |
| review_meta_content | publish_meta_content | refine_meta_content | 2 |
| refine_meta_content | review_meta_content | -- | -- |
| publish_meta_content | step_completion | -- | -- |

**Exhaustion code for review_meta_content:** META_CONTENT_REVIEW_EXHAUSTED, classification HUMAN_RETRY_REQUIRED.

**Validation rules:**
- step_name must reference an existing step_definition.
- onsuccess must reference an existing step_definition or "step_completion".
- Exactly one step must route to "step_completion" as its onsuccess target.
- Routing must not create unresolvable cycles.
- max_iterations must be specified if on_reject_refine is present.

**Traceability:** Spec Section 2.3 (routing table with exhaustion codes).

#### Type 4: prompt_pattern

**Purpose:** Defines reusable sections that are assembled into prompt templates for prompt-type steps. Each pattern represents a structural block within a prompt.

**Cardinality:** One or more per prompt-type step (1..N). The codebase_to_meta domain defines 6 patterns.

**Required properties:**

| Property | Type | Description |
|---|---|---|
| pattern_name | string | Identifier for this prompt pattern. |
| applied_to | array | List of step_names this pattern applies to. |
| content_description | string | Description of what this pattern contributes. |

**Domain instances (6):**

| pattern_name | applied_to | Description |
|---|---|---|
| reference_inputs | generate, review, refine | List input artifacts with placeholder paths. |
| generation_tasks | generate, refine | Specific content generation instructions per audience. |
| self_critic | generate, review, refine | Challenge reasoning, verify audience alignment. |
| self_validation | generate, review, refine | Check completeness, attribution, no hallucination. |
| forbidden_content | generate, refine | No hallucination, no information beyond source docs. |
| output_instructions | generate, review, refine | File path, YAML frontmatter format, ASCII-only. |

**Validation rules:**
- pattern_name must be unique within the schema.
- applied_to must reference existing prompt-type step_definitions.
- Every prompt-type step must have at least reference_inputs, self_critic, self_validation, and output_instructions patterns applied.
- Generate and refine steps must also include generation_tasks and forbidden_content.

**Traceability:** Spec Section 2.4 (6 prompt patterns with applicability rules).

#### Type 5: artifact_contract

**Purpose:** Defines a named output artifact produced by the workflow. Specifies the artifact key, filename pattern, which step produces it, and whether it is required.

**Cardinality:** One or more (1..N). The codebase_to_meta domain defines 5 artifacts.

**Required properties:**

| Property | Type | Description |
|---|---|---|
| artifact_key | string | Unique key identifying this artifact. |
| filename_pattern | string | Pattern for the output filename. May include placeholders. |
| produced_by | string | The step_name that produces this artifact. |
| required | boolean | Whether this artifact must be produced for workflow success. |

**Domain instances (5):**

| artifact_key | filename_pattern | produced_by | Required |
|---|---|---|---|
| AUDIENCE_INVENTORY_FILE | AUDIENCE_INV-{date}-{seq}_{slug}.md | scan_audiences | Yes |
| META_CONTENT_FILE | {audience_id}/META-{AUD}-{date}-{seq}.md | generate_meta_content | Yes |
| META_INDEX_FILE | meta_index.json | generate_meta_content | Yes |
| REVIEW_FILE_SUGGESTED | META-REV-{date}-{seq}_{slug}.md | review_meta_content | Yes |
| META_MANIFEST_FILE | meta_manifest.json | publish_meta_content | Yes |

**Validation rules:**
- artifact_key must be unique across the entire schema.
- produced_by must reference an existing step_definition.
- filename_pattern must not contain filesystem-incompatible characters.
- Every step_definition's produces array must reference valid artifact_keys.
- Required artifacts must be produced by a step that is always executed.

**Traceability:** Spec Section 2.5 (5 artifact contracts with filename patterns).

#### Type 6: composition_standard

**Purpose:** Defines a reusable composition standard that governs how component types are assembled into workflow packages. Establishes naming conventions, required schema sections, and extensibility rules for the domain.

**Cardinality:** Zero or more (0..N).

**Required properties:**

| Property | Type | Description |
|---|---|---|
| standard_name | string | Identifier for the standard. |
| standard_version | string | Semantic version of the standard. |
| component_type_count | integer | Number of component types this standard references. |

**Optional properties:**

| Property | Type | Description |
|---|---|---|
| schema_sections | array | List of sections that generated schemas must contain. |
| extensibility_model | string | Description of how new types or definitions can be added. |

**Domain status:** Part of the universal component library. Not instantiated at the Layer 1 component schema level for this domain. Consumed at Phase 6 (composition standard generation).

**Validation rules:**
- standard_name must be unique within the schema.
- standard_version must follow semantic versioning format (MAJOR.MINOR.PATCH).
- component_type_count must match the actual number of type definitions in the standard body.

**Traceability:** Spec Section 2 (8 universal component types acknowledged).

#### Type 7: output_variance

**Purpose:** Defines variations in output format that a domain may produce. Captures resolution rules, quality requirements, and format constraints that differ across audiences or output targets.

**Cardinality:** Zero or more (0..N).

**Required properties:**

| Property | Type | Description |
|---|---|---|
| variance_name | string | Identifier for this output variance. |

**Optional properties:**

| Property | Type | Description |
|---|---|---|
| target_audience | string | The audience_id this variance applies to. |
| resolution_rules | array | List of resolution rule identifiers. |
| quality_requirements | array | List of quality requirement identifiers. |
| frontmatter_schema | object | YAML frontmatter fields required for this output variant. |

**Domain status:** Part of the universal component library. Not instantiated at the Layer 1 component schema level for this domain. Output format details are captured at Phase 4 (Layer 3).

**Validation rules:**
- variance_name must be unique within the schema.
- resolution_rules must follow the naming convention RR-{DOMAIN}-{NNN}.
- quality_requirements must follow the naming convention QR-{DOMAIN}-{NNN}.

**Traceability:** Spec Section 4 (output format and quality requirements).

#### Type 8: domain_spec

**Purpose:** Captures domain-level metadata and context that applies across all components in a composition. Includes domain name, label, job prefix, workflow pattern, and contextual variables.

**Cardinality:** Zero or one (0..1) per domain.

**Required properties:**

| Property | Type | Description |
|---|---|---|
| domain_name | string | Machine-readable domain identifier. |
| domain_label | string | Human-readable domain name. |
| job_prefix | string | Prefix for job identifiers. |
| workflow_pattern | string | Execution pattern: "mixed", "prompt-only", or "action-only". |

**Optional properties:**

| Property | Type | Description |
|---|---|---|
| context_variables | array | List of context variable names and their resolved paths. |
| purpose | string | High-level description of what this domain accomplishes. |

**Domain status:** Part of the universal component library. Not instantiated at the Layer 1 component schema level for this domain. Domain metadata is captured in the workflow spec frontmatter.

**Validation rules:**
- domain_name must be unique across all domains.
- job_prefix must be a non-empty uppercase string.
- workflow_pattern must be one of: "mixed", "prompt-only", "action-only".

**Traceability:** Spec Section 1 (domain overview, context variables).

---

## Composition Format (Layer 2)

This section defines how component instances from Layer 1 are bound together into compositions that drive workflow execution. It specifies binding rules, override mechanisms, and placeholder resolution for the codebase_to_meta domain.

### Binding Rules

The composition format defines 8 binding rules, one per component type. Each rule specifies how instances of that component type participate in a composition.

| Binding Rule | Component Type | Cardinality | Required | Pattern |
|---|---|---|---|---|
| step_bindings | step_definition | 1..N | Yes | Ordered list |
| role_bindings | role_policy | 0..N | Conditional | Unordered set |
| routing_bindings | routing_pattern | 1 per step | Yes | Ordered list |
| prompt_bindings | prompt_pattern | 1..N per step | Conditional | Unordered set |
| artifact_bindings | artifact_contract | 1..N | Yes | Unordered set |
| composition_standard_binding | composition_standard | 0..1 | No | Singleton |
| output_variances | output_variance | 0..N | No | Unordered set |
| domain_specs | domain_spec | 0..1 | Yes | Singleton |

**Binding constraints:**
- step_bindings order must be consistent with routing_bindings.
- Each prompt-type step must have exactly one role_policy in role_bindings.
- Action-type steps must NOT have a role_policy entry.
- Every step must have exactly one routing_pattern in routing_bindings.
- Every artifact_key must be unique across the composition.
- produced_by must reference an existing step in step_bindings.

**Input data bindings (from spec Section 3.2):**

In addition to the 8 component type bindings, 3 input data bindings describe how external data sources are bound at runtime:

| Binding Name | Source | Cardinality | Required |
|---|---|---|---|
| codebase_docs | Codebase documentation files | Ordered set | Yes |
| codebase_manifest | codebase_manifest.json | Singleton | Yes |
| audience_defs | Audience plugin .md files | Unordered set | Yes |

### Override Mechanism

Per-audience customization is achieved through audience definition frontmatter fields. These are NOT component-level overrides in the traditional sense. They are audience-specific configuration parameters that drive the LLM's content generation behavior.

| Override Field | Type | Required | Overrides |
|---|---|---|---|
| tone | string | Yes | Default writing style for this audience. |
| focus_areas | array | Yes | Which codebase sections to emphasize. |
| exclude | array | No | Which content to omit from output. |
| section_structure | array | Yes | Output section order for this audience. |

**Key distinction:** Traditional component overrides modify component properties. Audience overrides modify the generation context. The components themselves remain unchanged; only the input context varies per audience.

**Non-overridable properties:** The following are set at the composition level and cannot be overridden per audience: builder_name, builder_label, job_prefix, workflow_pattern, step_bindings, routing_bindings, artifact_bindings, domain_specs.

**Merge semantics:** When the generate_meta_content step processes a single audience:
1. Start with the base content model from codebase documentation and codebase_manifest.
2. Apply the audience's focus_areas to select which sections to emphasize.
3. Apply the audience's exclude list to filter out omitted topics.
4. Apply the audience's tone to set the writing style.
5. Apply the audience's section_structure to order the output sections.

Each audience produces an independent output file. There is no cross-audience merging.

### Placeholder Resolution

Placeholders in prompt templates and composition definitions are resolved from 4 data sources in priority order. The first source that provides a value wins.

| Priority | Data Source | Fields Provided | Description |
|---|---|---|---|
| 1 (highest) | Runtime context | CODEBASE_DOC_ROOT, META_CONTENT_ROOT, AUDIENCE_DIR | Hardcoded paths from context_extensions.py. Resolved at workflow start. |
| 2 | Audience definition | audience_id, label, tone, focus_areas, section_structure | Per-audience frontmatter fields from the audience plugin file. |
| 3 | Codebase manifest | doc_inventory, section_list, total_doc_count | Metadata from codebase_manifest.json. |
| 4 (lowest) | Job runtime | job_id, seq, workspace_root | Execution-time values from the job runner context. |

**Unresolved placeholder handling:**
- Artifact key placeholders ({ARTIFACT_KEY}) must be declared in the step's required_inputs or produces.
- Context variable placeholder failures are a CRITICAL error.
- Audience field placeholder failures indicate missing required frontmatter.
- Job runtime placeholder failures indicate runner configuration errors.

---

## Output Format (Layer 3)

This section defines the concrete output structure, resolution rules, and quality requirements for the generated workflow package and its runtime output (meta content files).

### Output Structure

The Layer 3 output is organized into 3 parts:

| Part | Location | Purpose |
|---|---|---|
| Part 1 | Standards/COMPOSITION_STANDARD.md | Composition standard defining schema sections and extensibility model. |
| Part 2 | Specs/codebase_to_meta_v1.md | Runtime specification -- content-identical copy of the bootstrap spec. |
| Part 3 | Workflow package files | Operational workflow package deployable to the global runner home. |

**Part 3 contents:**

| File/Directory | Description |
|---|---|
| workflow.toml | Workflow manifest declaring 5 steps, 5 artifacts, routing. |
| context_extensions.py | Artifact key registration with hardcoded context variable paths. |
| actions.py | Python implementations of scan_audiences and publish_meta_content. |
| prompts/ | Prompt template files for 3 prompt-type steps. |
| audiences/ | Audience definition plugin files (3 initial). |
| README.md | Human documentation for the workflow package. |

### Resolution Rules

The following 7 resolution rules define how abstract component types resolve into concrete files in the output structure.

| Rule ID | Component Type | Resolution Target |
|---|---|---|
| RR-001 | step_definition | workflow.toml + actions.py or prompts/ |
| RR-002 | role_policy | workflow.toml [step] role field |
| RR-003 | routing_pattern | workflow.toml routing directives |
| RR-004 | prompt_pattern | prompts/*.txt template files |
| RR-005 | artifact_contract | workflow.toml + context_extensions.py |
| RR-006 | composition_standard | Standards/COMPOSITION_STANDARD.md |
| RR-007 | placeholder | Runtime values in all output files |

### Quality Requirements

The following quality requirements apply to all output files.

| Rule ID | Requirement | Severity | Verifiable Condition |
|---|---|---|---|
| QR-001 | Completeness | CRITICAL | All codebase sections represented in each audience output (filtered by focus_areas/exclude). |
| QR-002 | Audience fidelity | CRITICAL | Tone, focus, and section structure match audience definition frontmatter. |
| QR-003 | Self-contained | HIGH | Each meta content file is readable without reference to source docs. |
| QR-004 | Source attribution | HIGH | Every factual claim traces to a specific codebase doc file. |
| QR-005 | No hallucination | CRITICAL | No information invented beyond what codebase docs provide. |
| QR-006 | YAML frontmatter | HIGH | All required frontmatter fields present with correct values. |
| QR-007 | ASCII-only | HIGH | No em-dashes, no curly quotes, no Unicode characters. |
| QR-008 | Package traceability | HIGH | Every file in the output is traceable to a resolution rule. |

### Meta Content File Format

Each generated meta content file uses Rich Markdown with YAML frontmatter:

**Required frontmatter fields:**

| Field | Type | Description |
|---|---|---|
| title | string | Human-readable document title. |
| audience | string | Machine-readable audience identifier. |
| audience_label | string | Human-readable audience name. |
| generated_date | string | Date of generation (YYYY-MM-DD). |
| source_version | string | Version identifier of the source codebase. |
| section_count | integer | Number of sections in the document. |

**Meta content resolution rules (from spec Section 4.2):**

| Rule | Description |
|---|---|
| RR-META-001 | Each audience produces exactly one meta content file. |
| RR-META-002 | Filename uses audience_id prefix: META-{AUD}-{date}-{seq}.md. |
| RR-META-003 | Output subdirectory matches audience_id. |
| RR-META-004 | Section order follows audience section_structure. |
| RR-META-005 | Tone follows audience tone field. |
| RR-META-006 | Excluded topics must not appear in output. |
| RR-META-007 | Source attribution via inline references to codebase doc filenames. |

---

## Extensibility Model

This section describes concretely how the AR_META_BUILDER_STANDARD supports extension without breaking existing compositions.

### Extension Level 1: Adding New Audience Definitions

New audience definitions can be added by dropping a new .md file into the audiences/ directory. No changes to workflow.toml, actions.py, context_extensions.py, or prompt templates are required.

**Procedure:**
1. Create a new Markdown file in audiences/ (e.g., audiences/security.md).
2. Include YAML frontmatter with all 6 required fields: audience_id, label, tone, focus_areas, section_structure, and optionally exclude.
3. Ensure the audience_id is unique (no other file in audiences/ declares the same audience_id).
4. Run the workflow. The scan_audiences action step discovers the new file automatically. The generate step produces a new meta content file for the new audience.

**What changes:** The audience inventory includes one more entry. The output directory gains one more subdirectory. The meta_manifest.json includes one more file entry.

**What does NOT change:** workflow.toml, actions.py, context_extensions.py, prompt templates, routing, role assignments. All remain identical.

**Constraint:** The new audience definition must conform to the frontmatter schema (6 fields defined in Type 5: artifact_contract section and spec Section 2.6). Invalid frontmatter causes the file to be skipped with a warning.

### Extension Level 2: Adding New Component Types to the Universal Library

New component types can be added to the universal library (beyond the 8 defined in this standard) provided:

1. The new type includes all 5 required common properties: component_id, component_type, name, version, description.
2. The new type does not alter or remove any existing type's properties.
3. The new type's validation rules do not conflict with existing global validation rules.
4. Existing compositions remain valid without modification.
5. The new type is added as optional, not required.

**Procedure:**
1. Define the new type's schema in the component schema document (COMPONENT_SCHEMA.md) with all required sections: purpose, cardinality, properties table, validation rules, example.
2. Assign a unique type prefix for component_id generation.
3. Update the component_type_count in the composition standard frontmatter.
4. If the new type requires binding, add a corresponding binding rule to the composition format.
5. If the new type produces output, add a corresponding resolution rule to the output format.

**What changes:** The component_type_count increases. A new type definition subsection appears. Optionally, a new binding rule and resolution rule appear.

**What does NOT change:** All existing component types, instances, binding rules, and resolution rules remain unmodified.

**Constraint:** The standard_version must be incremented (MAJOR version for breaking changes, MINOR version for backward-compatible additions).

### Extension Level 3: Domain Adaptation

Different domains may use different subsets of the 8 universal types. The codebase_to_meta domain uses 5 of 8 types. Other domains may use different subsets or additional types from the universal library.

**Procedure:**
1. Declare which universal types the domain instantiates in the component schema.
2. Define domain-specific instances for each active type.
3. Unused types remain defined in the universal schema but carry no instances for this domain.

**Constraint:** The schema_sections field in the composition standard frontmatter must list the sections relevant to the domain. The 3 required sections (component_schema, composition_format, output_format) apply to all domains.

### Backward Compatibility Guarantee

Any composition valid under version N of this standard remains valid under version N+1, provided:
- No required common property is removed.
- No existing type-specific property changes from optional to required.
- No validation rule severity is increased from HIGH to CRITICAL for existing rules.
- New types are added as optional, not required.
- New audience definitions conform to the existing frontmatter schema.

---

## Self-Validation

This section verifies the completeness and internal consistency of this composition standard document.

### Component Type Coverage

| # | Type Name | Heading Format | Domain Status | Instances | Properties Defined | Validation Rules |
|---|---|---|---|---|---|---|
| 1 | step_definition | Type 1: step_definition | Active | 5 | Yes | Yes |
| 2 | role_policy | Type 2: role_policy | Active | 3 | Yes | Yes |
| 3 | routing_pattern | Type 3: routing_pattern | Active | 5 | Yes | Yes |
| 4 | prompt_pattern | Type 4: prompt_pattern | Active | 6 | Yes | Yes |
| 5 | artifact_contract | Type 5: artifact_contract | Active | 5 | Yes | Yes |
| 6 | composition_standard | Type 6: composition_standard | Universal | 0 (not instantiated) | Yes | Yes |
| 7 | output_variance | Type 7: output_variance | Universal | 0 (not instantiated) | Yes | Yes |
| 8 | domain_spec | Type 8: domain_spec | Universal | 0 (not instantiated) | Yes | Yes |

**Count: 8 component types defined. Matches frontmatter component_type_count: 8.**

### Schema Section Coverage

| # | Section Name | Layer | Defined |
|---|---|---|---|
| 1 | component_schema | Layer 1 | Yes |
| 2 | composition_format | Layer 2 | Yes |
| 3 | output_format | Layer 3 | Yes |

**Count: 3 schema sections defined. Matches frontmatter schema_sections array length: 3.**

### Layer Coverage

| Layer | Section Heading | Content | Defined |
|---|---|---|---|
| Layer 1 | Component Schema (Layer 1) | 8 component type definitions with properties, instances, validation | Yes |
| Layer 2 | Composition Format (Layer 2) | 8 binding rules, override mechanism, placeholder resolution | Yes |
| Layer 3 | Output Format (Layer 3) | 3-part output structure, 7 resolution rules, 8 quality requirements | Yes |

**All 3 layers are defined.**

### Extensibility Model Coverage

| Level | Extension Type | Procedure Defined | Constraints Defined | Backward Compatibility |
|---|---|---|---|---|
| Level 1 | Adding new audience definitions | Yes (4-step procedure) | Yes (frontmatter schema conformance) | Yes |
| Level 2 | Adding new component types | Yes (5-step procedure) | Yes (common properties, version increment) | Yes |
| Level 3 | Domain adaptation | Yes (3-step procedure) | Yes (schema_sections alignment) | Yes |

**Extensibility model is concrete with specific procedures, constraints, and backward compatibility guarantees.**

### Frontmatter Verification

| Field | Expected | Actual | Match |
|---|---|---|---|
| doc_type | "composition_standard" | "composition_standard" | Yes |
| lifecycle_status | "draft" | "draft" | Yes |
| standard_name | (from spec) | "AR_META_BUILDER_STANDARD" | Yes |
| standard_version | semantic version | "1.0.0" | Yes |
| component_type_count | 8 | 8 | Yes |
| schema_sections | 3 entries | 3 entries | Yes |

### Verification Checklist

- [x] Standard name "AR_META_BUILDER_STANDARD" is from the spec (Section 1 header).
- [x] Standard version "1.0.0" follows semantic versioning format.
- [x] All 8 component types are defined in "#### Type N: type_name" subsection format.
- [x] component_type_count (8) matches actual number of type definitions in the body.
- [x] schema_sections lists exactly 3 sections: component_schema, composition_format, output_format.
- [x] All 3 layers (Layer 1, Layer 2, Layer 3) are defined.
- [x] Extensibility model is concrete with 3 levels, each with specific procedures and constraints.
- [x] Backward compatibility guarantee is stated with specific conditions.
- [x] Binding rules reference component types from the component schema section.
- [x] Placeholder resolution defines 4 priority-ordered data sources.
- [x] Override mechanism covers all 4 audience fields: tone, focus_areas, exclude, section_structure.
- [x] Resolution rules and quality requirements reference spec Sections 4.2 and 4.3.
- [x] All content traces to the input specification (codebase_to_meta_v1.md). No scope invention.
- [x] ASCII-only content. No em-dashes, curly quotes, or Unicode characters.
- [x] Governance path references use filenames only (COMPONENT_SCHEMA.md, COMPOSITION_FORMAT.md, OUTPUT_FORMAT.md), not filesystem paths.

---

**End of Composition Standard Document**
