---
doc_type: "composition_format"
lifecycle_status: "draft"
layer: 2
binding_rule_count: 8
workflow_pattern_count: 6
domain: "ar_meta_builder"
spec_reference: "codebase_to_meta_v1.md Section 3"
---

# Composition Format (Layer 2)

## Overview

This document defines the Layer 2 composition format for the AR Meta Builder v1 composition system. Layer 2 sits between Layer 1 (component schema -- the building block library) and Layer 3 (output format -- the audience-specific meta content files). Its role is to define HOW components from Layer 1 are assembled into compositions that drive workflow execution.

**Layer 2 role in the 3-layer architecture:**

- Layer 1 (COMPONENT_SCHEMA.md) -- Defines the 8 universal component types and their schemas. Read-only authority for component definitions.
- Layer 2 (this document) -- Defines how component instances are bound together into compositions. Specifies binding rules, override mechanisms, placeholder resolution, and ordering constraints.
- Layer 3 (OUTPUT_FORMAT.md) -- Defines the output file format, resolution rules, and quality requirements for generated meta content.

**Domain context:** The codebase_to_meta domain transforms codebase documentation into audience-specific Rich Markdown meta content files. A "composition" in this domain is the combination of codebase documentation inputs with audience definitions, processed through a mixed workflow of action and prompt steps.

**Composition principle:** There are no user-provided input artifacts. All paths are resolved from the repo structure at runtime via context variables (spec Section 1.3). The composition binds codebase docs with audience definitions and produces per-audience output.

**Traceability:** All content in this document traces to the input specification (codebase_to_meta_v1.md, Section 3) and the component schema (COMPONENT_SCHEMA.md, Phase 2 output). The 8 binding rules correspond to the 8 component types defined in the component schema. The 6 workflow patterns correspond to structural patterns observable in the specification's operational requirements.

---

## Composition Structure

A composition in the codebase_to_meta domain is defined by the following top-level structure. This structure assembles component instances from Layer 1 into a coherent workflow definition.

### YAML Structure

```yaml
# Composition metadata
builder_name: string          # Machine-readable composition identifier
builder_label: string         # Human-readable display name
job_prefix: string            # Prefix for job identifiers (e.g., "META")
builder_purpose: string       # High-level description of what this composition produces

# Workflow pattern selection
workflow_pattern: string      # One of the 6 defined patterns (see Workflow Patterns)

# Component bindings (one per component type)
step_bindings:                # step_definition instances (ordered list)
artifact_bindings:            # artifact_contract instances (unordered set)
role_bindings:                # role_policy instances (unordered set)
routing_bindings:             # routing_pattern instances (ordered list)
prompt_bindings:              # prompt_pattern instances (unordered set)
composition_standard_binding: # composition_standard instance (singleton, optional)
output_variances:             # output_variance instances (unordered set, optional)
domain_specs:                 # domain_spec instance (singleton)

# Input data bindings (from spec Section 3.2)
input_bindings:
  codebase_docs:              # Ordered set, required
  codebase_manifest:          # Singleton, required
  audience_defs:              # Unordered set, required
```

### Field Descriptions

| Field | Type | Required | Description |
|---|---|---|---|
| builder_name | string | Yes | Machine-readable identifier for this composition (e.g., "codebase_to_meta_v1"). |
| builder_label | string | Yes | Human-readable display name (e.g., "Codebase to Meta Content v1"). |
| job_prefix | string | Yes | Prefix for job identifiers. Must be uppercase non-empty string (e.g., "META"). |
| builder_purpose | string | Yes | High-level description of what this composition produces. |
| workflow_pattern | string | Yes | Execution pattern identifier. Must be one of the 6 defined patterns. |
| step_bindings | ordered list | Yes | Ordered sequence of step_definition component instances. |
| artifact_bindings | unordered set | Yes | Set of artifact_contract component instances. |
| role_bindings | unordered set | Conditional | Set of role_policy instances. Required for each prompt-type step. |
| routing_bindings | ordered list | Yes | Ordered routing rules defining control flow between steps. |
| prompt_bindings | unordered set | Conditional | Set of prompt_pattern instances. Required for each prompt-type step. |
| composition_standard_binding | singleton | No | Optional reference to a composition_standard instance. |
| output_variances | unordered set | No | Optional set of output_variance instances for per-audience format control. |
| domain_specs | singleton | Yes | Single domain_spec instance providing domain-level metadata. |
| input_bindings | object | Yes | Input data binding group containing the 3 spec Section 3.2 bindings. |

---

## Component Bindings

This section defines 8 binding rules, one per component type from the component schema (COMPONENT_SCHEMA.md). Each binding rule specifies how instances of that component type participate in a composition.

### BR-001: step_definition Binding

| Property | Value |
|---|---|
| Binding name | step_bindings |
| Component type | step_definition |
| Cardinality | One or more (1..N) |
| Required | Yes |
| Binding pattern | Ordered list |
| Reference pattern | Each entry references a step_definition component_id |

**Description:** The step_bindings field contains an ordered list of step_definition instances. The order defines the canonical execution sequence. For the codebase_to_meta domain, exactly 5 steps are bound: scan_audiences, generate_meta_content, review_meta_content, refine_meta_content, publish_meta_content.

**Constraints:**
- The ordering must be consistent with routing_bindings (onsuccess targets must appear after source steps, except for refine loops).
- Each step must have a unique step_name.
- Action-type steps (scan_audiences, publish_meta_content) must not have role_bindings entries.
- Prompt-type steps (generate_meta_content, review_meta_content, refine_meta_content) must have role_bindings and prompt_bindings entries.

### BR-002: role_policy Binding

| Property | Value |
|---|---|
| Binding name | role_bindings |
| Component type | role_policy |
| Cardinality | Zero or more (0..N) |
| Required | Conditional (required for each prompt-type step) |
| Binding pattern | Unordered set |
| Reference pattern | Each entry references a role_policy component_id and binds to a step_name |

**Description:** The role_bindings field maps coder roles to prompt-type steps. Each entry assigns a policy_name (e.g., architect_standard, reviewer_standard) to a specific step. Action-type steps do not participate in this binding.

**Constraints:**
- Each prompt-type step must have exactly one role_policy entry.
- Action-type steps must NOT have a role_policy entry.
- The step_name in each role_policy must reference a valid step_definition in step_bindings.

### BR-003: routing_pattern Binding

| Property | Value |
|---|---|
| Binding name | routing_bindings |
| Component type | routing_pattern |
| Cardinality | One per step (1..1 per step) |
| Required | Yes |
| Binding pattern | Ordered list |
| Reference pattern | Each entry references a routing_pattern component_id and binds to a step_name |

**Description:** The routing_bindings field defines control flow between steps. Each entry specifies onsuccess and optional on_reject_refine targets. The ordering matches step_bindings order. Exactly one step must route to "step_completion" as its terminal target.

**Constraints:**
- Every step in step_bindings must have exactly one routing_pattern entry.
- onsuccess targets must reference existing step_definitions or "step_completion".
- on_reject_refine targets must reference existing step_definitions.
- Refine loops must specify max_iterations and exhaustion_code.
- Routing must not create unresolvable cycles.

### BR-004: prompt_pattern Binding

| Property | Value |
|---|---|
| Binding name | prompt_bindings |
| Component type | prompt_pattern |
| Cardinality | One or more per prompt step (1..N) |
| Required | Conditional (required for each prompt-type step) |
| Binding pattern | Unordered set |
| Reference pattern | Each entry references a prompt_pattern component_id and lists applied_to steps |

**Description:** The prompt_bindings field defines reusable prompt sections assembled into prompt templates. Each pattern specifies which steps it applies to via the applied_to array. For the codebase_to_meta domain, 6 patterns are defined: reference_inputs, generation_tasks, self_critic, self_validation, forbidden_content, output_instructions.

**Constraints:**
- Every prompt-type step must have at least reference_inputs, self_critic, self_validation, and output_instructions patterns applied.
- Generate and refine steps must also include generation_tasks and forbidden_content.
- applied_to must reference existing prompt-type step_definitions.

### BR-005: artifact_contract Binding

| Property | Value |
|---|---|
| Binding name | artifact_bindings |
| Component type | artifact_contract |
| Cardinality | One or more (1..N) |
| Required | Yes |
| Binding pattern | Unordered set |
| Reference pattern | Each entry references an artifact_contract component_id |

**Description:** The artifact_bindings field declares all output artifacts produced by the composition. Each entry specifies the artifact_key, filename_pattern, produced_by step, and required flag. For the codebase_to_meta domain, 5 artifacts are declared: AUDIENCE_INVENTORY_FILE, META_CONTENT_FILE, META_INDEX_FILE, REVIEW_FILE_SUGGESTED, META_MANIFEST_FILE.

**Constraints:**
- Every artifact_key must be unique across the composition.
- produced_by must reference an existing step in step_bindings.
- Every step's produces array must reference valid artifact_keys in artifact_bindings.
- Required artifacts must be produced by steps that are always executed.

### BR-006: composition_standard Binding

| Property | Value |
|---|---|
| Binding name | composition_standard_binding |
| Component type | composition_standard |
| Cardinality | Zero or one (0..1) |
| Required | No |
| Binding pattern | Singleton |
| Reference pattern | References a composition_standard component_id |

**Description:** The composition_standard_binding field optionally references a composition_standard that governs naming conventions, required schema sections, and extensibility rules. For the codebase_to_meta domain, this binding is consumed at Phase 6 (composition standard generation) rather than at the Layer 1 schema level.

**Constraints:**
- At most one composition_standard may be bound.
- standard_version must follow semantic versioning format.
- component_type_count must match the standard body.

### BR-007: output_variance Binding

| Property | Value |
|---|---|
| Binding name | output_variances |
| Component type | output_variance |
| Cardinality | Zero or more (0..N) |
| Required | No |
| Binding pattern | Unordered set |
| Reference pattern | Each entry references an output_variance component_id |

**Description:** The output_variances field defines per-audience output format variations. Each entry captures resolution rules, quality requirements, and frontmatter schema for a specific audience target. For the codebase_to_meta domain, these are consumed at Phase 4 (output format generation).

**Constraints:**
- variance_name must be unique within the composition.
- target_audience must reference a valid audience_id if specified.
- Resolution rules follow RR-{DOMAIN}-{NNN} naming convention.
- Quality requirements follow QR-{DOMAIN}-{NNN} naming convention.

### BR-008: domain_spec Binding

| Property | Value |
|---|---|
| Binding name | domain_specs |
| Component type | domain_spec |
| Cardinality | Zero or one (0..1) per domain |
| Required | Yes |
| Binding pattern | Singleton |
| Reference pattern | References a domain_spec component_id |

**Description:** The domain_specs field provides domain-level metadata for the composition. It captures the domain identity (domain_name, domain_label), job prefix, workflow pattern, and context variables. For the codebase_to_meta domain, the domain_spec captures CODEBASE_DOC_ROOT, META_CONTENT_ROOT, and AUDIENCE_DIR context variables.

**Constraints:**
- domain_name must be unique across all domains.
- job_prefix must be a non-empty uppercase string.
- workflow_pattern must be one of the defined pattern identifiers.
- context_variables entries must include both variable name and resolved path.

### Input Data Bindings (spec Section 3.2)

In addition to the 8 component type bindings above, the composition format defines 3 input data bindings from the specification Section 3.2. These describe how external data sources are bound into the composition at runtime.

#### codebase_docs (Ordered set, required)

| Property | Value |
|---|---|
| Binding name | codebase_docs |
| Source | Codebase documentation files |
| Cardinality | Ordered set |
| Required | Yes |
| Maps to | artifact_contract instances representing codebase documentation files |

All .md files under CODEBASE_DOC_ROOT. The ordered set preserves the directory hierarchy and manifest ordering. For the codebase_to_meta domain, approximately 155 files are bound.

#### codebase_manifest (Singleton, required)

| Property | Value |
|---|---|
| Binding name | codebase_manifest |
| Source | codebase_manifest.json |
| Cardinality | Singleton |
| Required | Yes |
| Maps to | The codebase_manifest.json artifact |

Full doc inventory with metadata. Located at CODEBASE_DOC_ROOT/codebase_manifest.json. Provides doc_inventory, section_list, and total_doc_count for placeholder resolution.

#### audience_defs (Unordered set, required)

| Property | Value |
|---|---|
| Binding name | audience_defs |
| Source | Audience plugin .md files |
| Cardinality | Unordered set |
| Required | Yes |
| Maps to | Audience plugin files |

All audience definitions from the audiences/ directory. Each file is a Markdown file with YAML frontmatter containing audience_id, label, tone, focus_areas, exclude (optional), and section_structure. The initial audience set consists of 3 files: developer.md, architect.md, and executive.md.

---

## Override Mechanism

Per-audience customization is achieved through the audience definition frontmatter fields. This section defines the override semantics, constraints, and syntax.

### Override Fields

| Field | Overrides | Type | Required | Description |
|---|---|---|---|---|
| tone | Default writing style | string | Yes | Controls the LLM's writing voice and technical depth for this audience. |
| focus_areas | Default content emphasis | array | Yes | Overrides which codebase sections to emphasize during content generation. |
| exclude | Default content inclusion | array | No | Overrides which content to omit from the output. |
| section_structure | Default section order | array | Yes | Overrides the output section order for this audience. |

### Nature of Overrides

These are NOT component-level overrides in the traditional sense. They are audience-specific configuration parameters that drive the LLM's content generation behavior. The composition does not override component properties -- it provides per-audience context that shapes how the generate and refine prompt steps produce content.

**Key distinction:** Traditional component overrides modify component properties (e.g., changing a step's parameters). Audience overrides modify the generation context (e.g., changing what content to emphasize). The components themselves remain unchanged; only the input context varies per audience.

### Merge Semantics

When the generate_meta_content step processes a single audience:

1. Start with the base content model defined by the codebase documentation and codebase_manifest.
2. Apply the audience's focus_areas to select which sections of the codebase to emphasize.
3. Apply the audience's exclude list to filter out omitted topics.
4. Apply the audience's tone to set the writing style.
5. Apply the audience's section_structure to order the output sections.

Each audience produces an independent output file. There is no cross-audience merging -- each audience's overrides are applied independently to the same source data.

### Schema Conformance

All override fields must conform to the audience definition frontmatter schema defined in the component schema (COMPONENT_SCHEMA.md, Section 2.6):

- tone: string, required. Non-empty.
- focus_areas: array of strings, required. At least one entry.
- exclude: array of strings, optional. May be empty or absent.
- section_structure: array of strings, required. At least one entry. Defines output section order.

### Common Properties Non-Overridable

The following properties are set at the composition level and CANNOT be overridden per audience:

- builder_name, builder_label, job_prefix -- Composition identity.
- workflow_pattern -- Execution pattern is fixed for the composition.
- step_bindings -- Step sequence is identical for all audiences.
- routing_bindings -- Control flow is identical for all audiences.
- artifact_bindings -- Output artifact declarations are identical for all audiences.
- domain_specs -- Domain metadata is shared across all audiences.

### Override Syntax Example

```yaml
# Audience: developer.md
---
audience_id: developer
label: Developer
tone: technical, hands-on, code-first
focus_areas:
  - module APIs and signatures
  - dependency relationships
  - setup and contribution guides
  - code patterns and conventions
  - extension points
exclude:
  - high-level business summaries
  - cost/effort estimates
section_structure:
  - overview
  - module_catalog
  - api_reference
  - dependency_map
  - developer_guide
---
```

In this example, the developer audience overrides:
- tone: from default (neutral technical) to "technical, hands-on, code-first"
- focus_areas: emphasizes module APIs, dependencies, setup, patterns, extension points
- exclude: omits business summaries and cost estimates
- section_structure: orders output as overview, module_catalog, api_reference, dependency_map, developer_guide

---

## Placeholder Resolution

Placeholders in prompt templates and composition definitions are resolved from 4 data sources in priority order. When a placeholder is encountered, the resolution engine searches data sources from highest to lowest priority. The first source that provides a value wins.

### Resolution Data Sources

| Priority | Data Source | Fields Provided | Description |
|---|---|---|---|
| 1 (highest) | Runtime context | CODEBASE_DOC_ROOT, META_CONTENT_ROOT, AUDIENCE_DIR | Hardcoded paths from context_extensions.py. Resolved at workflow start. |
| 2 | Audience definition | audience_id, label, tone, focus_areas, section_structure | Per-audience frontmatter fields from the audience plugin file. |
| 3 | Codebase manifest | doc_inventory, section_list, total_doc_count | Metadata from CODEBASE_DOC_ROOT/codebase_manifest.json. |
| 4 (lowest) | Job runtime | job_id, seq, workspace_root | Execution-time values from the job runner context. |

### Resolution Order

For each placeholder {PLACEHOLDER_NAME} encountered during step execution:

1. **Check Runtime context (Priority 1):** If the placeholder name matches a context variable name (CODEBASE_DOC_ROOT, META_CONTENT_ROOT, AUDIENCE_DIR), resolve to the hardcoded path value. These are always available and never change during execution.

2. **Check Audience definition (Priority 2):** If the placeholder name matches an audience frontmatter field (audience_id, label, tone, focus_areas, section_structure), resolve to the value from the current audience's definition. This resolution is per-audience -- different audiences produce different values.

3. **Check Codebase manifest (Priority 3):** If the placeholder name matches a codebase manifest field (doc_inventory, section_list, total_doc_count), resolve to the value from codebase_manifest.json. This is the same for all audiences within a single workflow run.

4. **Check Job runtime (Priority 4):** If the placeholder name matches a job runtime field (job_id, seq, workspace_root), resolve to the current job's execution context. These values change per workflow invocation.

### Unresolved Placeholder Handling

If a placeholder cannot be resolved from any of the 4 data sources:

- **For artifact key placeholders ({ARTIFACT_KEY}):** The placeholder must be declared in the step's required_inputs or produces in the workflow manifest. If not declared, this is a validation error (CV-006).
- **For context variable placeholders:** Resolution failure is a CRITICAL error. The step cannot execute without required context.
- **For audience field placeholders:** Resolution failure indicates the audience definition is missing a required frontmatter field. This is caught by audience definition validation (VR-002).
- **For job runtime placeholders:** Resolution failure indicates a runner configuration error. The job context must always provide job_id, seq, and workspace_root.

### Resolution Example

Given the placeholder {CODEBASE_DOC_ROOT} in a prompt template:

1. Priority 1 (Runtime context): CODEBASE_DOC_ROOT resolves to {repo_root}/docs/repo/codebase/current/. Resolved.

Given the placeholder {audience_id} in a prompt template:

1. Priority 1 (Runtime context): Not found.
2. Priority 2 (Audience definition): audience_id resolves to "developer" (for the developer audience). Resolved.

Given the placeholder {job_id} in a filename pattern:

1. Priority 1 (Runtime context): Not found.
2. Priority 2 (Audience definition): Not found.
3. Priority 3 (Codebase manifest): Not found.
4. Priority 4 (Job runtime): job_id resolves to "AMB-ai99miop". Resolved.

---

## Ordering Rules

The composition format enforces ordering constraints on step_bindings and routing_bindings to ensure correct workflow execution. These constraints derive from the routing patterns defined in the component schema (COMPONENT_SCHEMA.md).

### Rule OR-001: Foundation First

The first step in step_bindings must be a foundation step that produces inputs required by all subsequent steps. For codebase_to_meta, scan_audiences is the foundation step -- it discovers audience definitions that all subsequent steps consume.

**Constraint:** step_bindings[0] must be an action-type step that produces inventory or discovery artifacts.

### Rule OR-002: Layer Sequence

Steps must follow the logical layer sequence: Scan -> Generate -> Review -> Refine (conditional) -> Publish. The step_bindings order must reflect this sequence.

**Constraint:** The canonical order for codebase_to_meta is:
1. scan_audiences (Scan phase)
2. generate_meta_content (Generate phase)
3. review_meta_content (Review phase)
4. refine_meta_content (Refine phase -- conditional)
5. publish_meta_content (Publish phase)

### Rule OR-003: Gatekeep After Generate

Review/gatekeep steps must appear after generate steps. The review step evaluates output from the generate step and cannot execute until generation is complete.

**Constraint:** review_meta_content must appear after generate_meta_content in step_bindings.

### Rule OR-004: Terminal Last

The step that routes to "step_completion" must be the final step in step_bindings. For codebase_to_meta, publish_meta_content is the terminal step.

**Constraint:** The last entry in step_bindings must have onsuccess = "step_completion" in its routing_bindings entry.

### Rule OR-005: Refine Loop Placement

The refine step must appear immediately after the review step in step_bindings. The review-refine loop (review -> refine -> review) requires adjacent positioning for correct iteration tracking.

**Constraint:** refine_meta_content must appear at position step_bindings.index(review_meta_content) + 1.

### Rule OR-006: Routing Consistency

The routing_bindings order must match the step_bindings order. Each routing entry's step_name must correspond to the step at the same positional index in step_bindings.

**Constraint:** For all i, routing_bindings[i].step_name == step_bindings[i].step_name.

### Rule OR-007: No Forward References in onsuccess

A step's onsuccess target must reference a step that appears later in step_bindings (or "step_completion"). No step may route forward to a step that precedes it in the binding order, except for the refine loop.

**Constraint:** For the refine loop exception, review_meta_content routes to refine_meta_content (position +1), and refine_meta_content routes back to review_meta_content (position -1). This is the only allowed backward reference.

### Rule OR-008: Input Data Ordering

The input data bindings follow a logical dependency order:
1. codebase_docs (source data -- no dependencies)
2. codebase_manifest (index of source data -- depends on codebase_docs existing)
3. audience_defs (audience plugins -- independent of codebase data, but consumed alongside it)

**Constraint:** codebase_manifest must be resolvable before generate_meta_content executes. audience_defs must be resolvable before scan_audiences executes.

---

## Composition Validation

The following validation checks verify that a composition is correctly formed. Each check has an identifier (CV-NNN), a severity level, and a verifiable condition.

### CV-001: Required Bindings Present

**Severity:** CRITICAL
**Condition:** All required bindings are present in the composition. Specifically: step_bindings is non-empty, artifact_bindings is non-empty, routing_bindings is non-empty, domain_specs is present, and all 3 input_bindings (codebase_docs, codebase_manifest, audience_defs) are declared.

### CV-002: Step Name Uniqueness

**Severity:** CRITICAL
**Condition:** Every step_name in step_bindings is unique. No two step_definition instances share the same step_name. This corresponds to VR-007 in the component schema.

### CV-003: Routing Completeness

**Severity:** CRITICAL
**Condition:** Every step in step_bindings has exactly one routing_pattern in routing_bindings. Exactly one step routes to "step_completion" as its onsuccess target. This corresponds to VR-008.

### CV-004: Role-Step Consency

**Severity:** CRITICAL
**Condition:** Every prompt-type step has exactly one role_policy in role_bindings. No action-type step has a role_policy entry. This corresponds to VR-014.

### CV-005: Artifact Key Coverage

**Severity:** CRITICAL
**Condition:** Every artifact_key referenced in any step_definition's produces array has a corresponding artifact_contract in artifact_bindings. This corresponds to VR-013.

### CV-006: Placeholder Resolution Completeness

**Severity:** CRITICAL
**Condition:** Every {PLACEHOLDER} in prompt templates is resolvable from at least one of the 4 data sources (Runtime context, Audience definition, Codebase manifest, Job runtime). Every artifact key placeholder corresponds to a declared artifact in the step's required_inputs or produces.

### CV-007: Audience Definition Validity

**Severity:** CRITICAL
**Condition:** Each audience definition file in audience_defs has valid YAML frontmatter containing all required fields: audience_id, label, tone, focus_areas, section_structure. No two audience definitions share the same audience_id. This corresponds to VR-001, VR-002, VR-003.

### CV-008: Ordering Constraints Satisfied

**Severity:** HIGH
**Condition:** The step_bindings order satisfies all ordering rules (OR-001 through OR-008). Foundation step is first. Terminal step is last. Review-refine loop is correctly positioned. Routing order matches step order.

### CV-009: Override Conformance

**Severity:** HIGH
**Condition:** All audience override fields (tone, focus_areas, exclude, section_structure) conform to the schema defined in the Override Mechanism section. Tone is non-empty string. focus_areas has at least one entry. section_structure has at least one entry. Common properties are not overridden.

### CV-010: Pattern Compliance

**Severity:** HIGH
**Condition:** The composition's workflow_pattern matches the actual structural pattern of the step_bindings and routing_bindings. If workflow_pattern is "mixed", the composition must contain both action-type and prompt-type steps. If "linear", there must be no reject-refine loops. The declared pattern must accurately describe the composition's structure.

---

## Workflow Patterns

The composition format defines 6 workflow patterns that characterize the structural shape of a composition. Each composition declares which pattern it follows via the workflow_pattern field.

### Pattern 1: linear_pipeline

**Description:** Sequential step execution without loops or conditional branches. Each step routes to the next step in sequence. The final step routes to step_completion.

**Structural signature:** All routing_patterns have onsuccess targets and no on_reject_refine targets. Steps form a single linear chain.

**Example in codebase_to_meta:** If the review-refine loop were removed, the composition would be a linear pipeline: scan -> generate -> review -> publish.

### Pattern 2: review_refine_loop

**Description:** A cyclic pattern where a review step evaluates output and may route to a refine step for correction. The refine step routes back to review for re-evaluation. The loop has a maximum iteration count and an exhaustion code.

**Structural signature:** One routing_pattern has both onsuccess (forward) and on_reject_refine (to refine step). The refine step's onsuccess routes back to the review step. max_iterations and exhaustion_code are specified.

**Example in codebase_to_meta:** review_meta_content routes to publish_meta_content on success, or to refine_meta_content on rejection (max 2 iterations, exhaustion code META_CONTENT_REVIEW_EXHAUSTED).

### Pattern 3: plugin_extensible_audience

**Description:** A pattern where the set of processing targets (audiences) is defined by drop-in plugin files rather than hardcoded configuration. Adding a new target requires only adding a new plugin file -- no workflow logic changes.

**Structural signature:** The audience_defs input binding is an unordered set. The scan_audiences action step dynamically discovers plugins at runtime. Output fan-out is driven by the discovered plugin set.

**Example in codebase_to_meta:** The audiences/ directory contains .md plugin files. Adding a new audience (e.g., security.md) requires only dropping a new file -- no changes to workflow.toml, actions.py, or prompt templates.

### Pattern 4: staging_publish_lifecycle

**Description:** A multi-stage publishing pattern that progresses through staging, review, refinement, backup, history, and final publish. Ensures safe deployment with rollback capability.

**Structural signature:** The terminal action step implements a multi-stage lifecycle: (1) backup existing output, (2) move to history, (3) copy new output, (4) write manifest. Uses the standard staging directories: current/, runs/, history/, backups/.

**Example in codebase_to_meta:** publish_meta_content implements: backup current/ to backups/BACKUP-{timestamp}/, move current/ to history/{job_id}/, copy generated files to current/{audience_id}/, write meta_manifest.json.

### Pattern 5: mixed_step_types

**Description:** A composition that combines both action-type steps (deterministic Python code) and prompt-type steps (LLM-driven content generation). Action steps handle infrastructure tasks (scanning, publishing); prompt steps handle content tasks (generation, review, refinement).

**Structural signature:** step_bindings contains at least one step with step_type "action" and at least one step with step_type "prompt". Action steps have no role_bindings. Prompt steps have role_bindings and prompt_bindings.

**Example in codebase_to_meta:** scan_audiences and publish_meta_content are action steps. generate_meta_content, review_meta_content, and refine_meta_content are prompt steps.

### Pattern 6: multi_audience_fanout

**Description:** A single workflow execution produces multiple output files, one per discovered audience. The generate step iterates over the audience inventory and produces independent output for each audience.

**Structural signature:** The generate step's artifact_contract uses a per-audience filename pattern ({audience_id}/META-{AUD}-{date}-{seq}.md). The output directory structure contains one subdirectory per audience_id.

**Example in codebase_to_meta:** generate_meta_content produces one META_CONTENT_FILE per audience. If 3 audiences are discovered (developer, architect, executive), 3 meta content files are generated, each in its own subdirectory.

---

## Example Compositions

### Example 1: codebase_to_meta_v1 (Default)

This is the standard composition for the codebase_to_meta domain as defined in the specification.

```yaml
builder_name: codebase_to_meta_v1
builder_label: "Codebase to Meta Content v1"
job_prefix: META
builder_purpose: >
  Transforms codebase documentation into audience-specific Rich
  Markdown meta content files via plugin-extensible audience
  definitions.
workflow_pattern: mixed

# Step bindings (ordered list, 5 steps)
step_bindings:
  - component_id: STEP-001
    step_name: scan_audiences
    step_type: action
    phase: Scan
  - component_id: STEP-002
    step_name: generate_meta_content
    step_type: prompt
    phase: Generate
  - component_id: STEP-003
    step_name: review_meta_content
    step_type: prompt
    phase: Review
  - component_id: STEP-004
    step_name: refine_meta_content
    step_type: prompt
    phase: Refine
  - component_id: STEP-005
    step_name: publish_meta_content
    step_type: action
    phase: Publish

# Artifact bindings (unordered set, 5 artifacts)
artifact_bindings:
  - component_id: ARTIFACT-001
    artifact_key: AUDIENCE_INVENTORY_FILE
    produced_by: scan_audiences
    required: true
  - component_id: ARTIFACT-002
    artifact_key: META_CONTENT_FILE
    produced_by: generate_meta_content
    required: true
  - component_id: ARTIFACT-003
    artifact_key: META_INDEX_FILE
    produced_by: generate_meta_content
    required: true
  - component_id: ARTIFACT-004
    artifact_key: REVIEW_FILE_SUGGESTED
    produced_by: review_meta_content
    required: true
  - component_id: ARTIFACT-005
    artifact_key: META_MANIFEST_FILE
    produced_by: publish_meta_content
    required: true

# Role bindings (unordered set, 3 entries for prompt steps)
role_bindings:
  - component_id: ROLE-001
    step_name: generate_meta_content
    policy_name: architect_standard
  - component_id: ROLE-002
    step_name: review_meta_content
    policy_name: reviewer_standard
  - component_id: ROLE-003
    step_name: refine_meta_content
    policy_name: architect_standard

# Routing bindings (ordered list, 5 entries)
routing_bindings:
  - component_id: ROUTE-001
    step_name: scan_audiences
    onsuccess: generate_meta_content
  - component_id: ROUTE-002
    step_name: generate_meta_content
    onsuccess: review_meta_content
  - component_id: ROUTE-003
    step_name: review_meta_content
    onsuccess: publish_meta_content
    on_reject_refine: refine_meta_content
    max_iterations: 2
    exhaustion_code: META_CONTENT_REVIEW_EXHAUSTED
    exhaustion_classification: HUMAN_RETRY_REQUIRED
  - component_id: ROUTE-004
    step_name: refine_meta_content
    onsuccess: review_meta_content
  - component_id: ROUTE-005
    step_name: publish_meta_content
    onsuccess: step_completion

# Prompt bindings (unordered set, 6 patterns)
prompt_bindings:
  - component_id: PROMPT-001
    pattern_name: reference_inputs
    applied_to: [generate_meta_content, review_meta_content, refine_meta_content]
  - component_id: PROMPT-002
    pattern_name: generation_tasks
    applied_to: [generate_meta_content, refine_meta_content]
  - component_id: PROMPT-003
    pattern_name: self_critic
    applied_to: [generate_meta_content, review_meta_content, refine_meta_content]
  - component_id: PROMPT-004
    pattern_name: self_validation
    applied_to: [generate_meta_content, review_meta_content, refine_meta_content]
  - component_id: PROMPT-005
    pattern_name: forbidden_content
    applied_to: [generate_meta_content, refine_meta_content]
  - component_id: PROMPT-006
    pattern_name: output_instructions
    applied_to: [generate_meta_content, review_meta_content, refine_meta_content]

# Domain spec (singleton)
domain_specs:
  component_id: DOM-001
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

# Input data bindings (from spec Section 3.2)
input_bindings:
  codebase_docs:
    source: "CODEBASE_DOC_ROOT"
    cardinality: ordered_set
    required: true
  codebase_manifest:
    source: "CODEBASE_DOC_ROOT/codebase_manifest.json"
    cardinality: singleton
    required: true
  audience_defs:
    source: "AUDIENCE_DIR"
    cardinality: unordered_set
    required: true
```

### Example 2: codebase_to_meta_v1 with Extended Audience Set

This composition extends the audience set by adding a security-focused audience. No workflow logic changes are needed -- only a new audience plugin file.

```yaml
builder_name: codebase_to_meta_v1_extended
builder_label: "Codebase to Meta Content v1 (Extended Audiences)"
job_prefix: META
builder_purpose: >
  Transforms codebase documentation into audience-specific Rich
  Markdown meta content files. Extended with security audience.
workflow_pattern: mixed

# Step bindings -- identical to Example 1
step_bindings:
  - component_id: STEP-001
    step_name: scan_audiences
    step_type: action
  - component_id: STEP-002
    step_name: generate_meta_content
    step_type: prompt
  - component_id: STEP-003
    step_name: review_meta_content
    step_type: prompt
  - component_id: STEP-004
    step_name: refine_meta_content
    step_type: prompt
  - component_id: STEP-005
    step_name: publish_meta_content
    step_type: action

# Artifact bindings -- identical to Example 1
artifact_bindings:
  - component_id: ARTIFACT-001
    artifact_key: AUDIENCE_INVENTORY_FILE
    produced_by: scan_audiences
    required: true
  - component_id: ARTIFACT-002
    artifact_key: META_CONTENT_FILE
    produced_by: generate_meta_content
    required: true
  - component_id: ARTIFACT-003
    artifact_key: META_INDEX_FILE
    produced_by: generate_meta_content
    required: true
  - component_id: ARTIFACT-004
    artifact_key: REVIEW_FILE_SUGGESTED
    produced_by: review_meta_content
    required: true
  - component_id: ARTIFACT-005
    artifact_key: META_MANIFEST_FILE
    produced_by: publish_meta_content
    required: true

# Role bindings -- identical to Example 1
role_bindings:
  - component_id: ROLE-001
    step_name: generate_meta_content
    policy_name: architect_standard
  - component_id: ROLE-002
    step_name: review_meta_content
    policy_name: reviewer_standard
  - component_id: ROLE-003
    step_name: refine_meta_content
    policy_name: architect_standard

# Routing bindings -- identical to Example 1
routing_bindings:
  - component_id: ROUTE-001
    step_name: scan_audiences
    onsuccess: generate_meta_content
  - component_id: ROUTE-002
    step_name: generate_meta_content
    onsuccess: review_meta_content
  - component_id: ROUTE-003
    step_name: review_meta_content
    onsuccess: publish_meta_content
    on_reject_refine: refine_meta_content
    max_iterations: 2
    exhaustion_code: META_CONTENT_REVIEW_EXHAUSTED
    exhaustion_classification: HUMAN_RETRY_REQUIRED
  - component_id: ROUTE-004
    step_name: refine_meta_content
    onsuccess: review_meta_content
  - component_id: ROUTE-005
    step_name: publish_meta_content
    onsuccess: step_completion

# Prompt bindings -- identical to Example 1
prompt_bindings:
  - component_id: PROMPT-001
    pattern_name: reference_inputs
    applied_to: [generate_meta_content, review_meta_content, refine_meta_content]
  - component_id: PROMPT-002
    pattern_name: generation_tasks
    applied_to: [generate_meta_content, refine_meta_content]
  - component_id: PROMPT-003
    pattern_name: self_critic
    applied_to: [generate_meta_content, review_meta_content, refine_meta_content]
  - component_id: PROMPT-004
    pattern_name: self_validation
    applied_to: [generate_meta_content, review_meta_content, refine_meta_content]
  - component_id: PROMPT-005
    pattern_name: forbidden_content
    applied_to: [generate_meta_content, refine_meta_content]
  - component_id: PROMPT-006
    pattern_name: output_instructions
    applied_to: [generate_meta_content, review_meta_content, refine_meta_content]

# Domain spec -- identical to Example 1
domain_specs:
  component_id: DOM-001
  domain_name: codebase_to_meta
  domain_label: "Codebase to Meta Content v1"
  job_prefix: META
  workflow_pattern: mixed

# Input data bindings -- audience_defs now includes 4 files
input_bindings:
  codebase_docs:
    source: "CODEBASE_DOC_ROOT"
    cardinality: ordered_set
    required: true
  codebase_manifest:
    source: "CODEBASE_DOC_ROOT/codebase_manifest.json"
    cardinality: singleton
    required: true
  audience_defs:
    source: "AUDIENCE_DIR"
    cardinality: unordered_set
    required: true
    # Audience files: developer.md, architect.md, executive.md, security.md
    # The security.md file adds a new audience without workflow changes.
```

**Difference from Example 1:** The audience_defs binding now includes a 4th file (security.md). The scan_audiences action discovers it automatically. The generate step produces a 4th meta content file. The publish step includes it in the manifest. No changes to step_bindings, routing_bindings, role_bindings, or prompt_bindings are required. This demonstrates the plugin_extensible_audience pattern.

### Example Input/Output Structure (spec Section 3.5)

```
Input:
  CODEBASE_DOC_ROOT/
  |-- codebase_manifest.json
  |-- standards/
  |   |-- CODING_STANDARD.md
  |   +-- DOCUMENTATION_STANDARD.md
  |-- modules/
  |   |-- agent_runner_v2.md
  |   |-- step_runner.md
  |   +-- ...
  +-- inventory/
      +-- CODEBASE_INVENTORY.md

  audiences/
  |-- developer.md
  |-- architect.md
  +-- executive.md

Output:
  docs/repo/meta_content/current/
  |-- developer/
  |   +-- META-DEV-20260808-001.md
  |-- architect/
  |   +-- META-ARCH-20260808-001.md
  |-- executive/
  |   +-- META-EXEC-20260808-001.md
  +-- meta_manifest.json
```

---

## Self-Validation

This section verifies the completeness and correctness of the composition format document.

### Binding Rule Coverage

| # | Binding Rule | Component Type | Cardinality | Required | Pattern | Defined |
|---|---|---|---|---|---|---|
| BR-001 | step_bindings | step_definition | 1..N | Yes | Ordered list | Yes |
| BR-002 | role_bindings | role_policy | 0..N | Conditional | Unordered set | Yes |
| BR-003 | routing_bindings | routing_pattern | 1 per step | Yes | Ordered list | Yes |
| BR-004 | prompt_bindings | prompt_pattern | 1..N per step | Conditional | Unordered set | Yes |
| BR-005 | artifact_bindings | artifact_contract | 1..N | Yes | Unordered set | Yes |
| BR-006 | composition_standard_binding | composition_standard | 0..1 | No | Singleton | Yes |
| BR-007 | output_variances | output_variance | 0..N | No | Unordered set | Yes |
| BR-008 | domain_specs | domain_spec | 0..1 | Yes | Singleton | Yes |

**Count: 8 binding rules defined. Matches frontmatter binding_rule_count: 8.**

### Input Data Binding Coverage (spec Section 3.2)

| # | Binding Name | Cardinality | Required | Maps To | Defined |
|---|---|---|---|---|---|
| 1 | codebase_docs | Ordered set | Yes | artifact_contract (source docs) | Yes |
| 2 | codebase_manifest | Singleton | Yes | codebase_manifest.json artifact | Yes |
| 3 | audience_defs | Unordered set | Yes | Audience plugin files | Yes |

**Count: 3 input data bindings defined. Matches spec Section 3.2.**

### Workflow Pattern Coverage

| # | Pattern | Description | Structural Signature | Defined |
|---|---|---|---|---|
| 1 | linear_pipeline | Sequential steps, no loops | All onsuccess, no on_reject_refine | Yes |
| 2 | review_refine_loop | Cyclic review-refine with iteration limit | on_reject_refine + max_iterations | Yes |
| 3 | plugin_extensible_audience | Drop-in audience plugins | Unordered audience_defs, dynamic discovery | Yes |
| 4 | staging_publish_lifecycle | Multi-stage backup/history/publish | Terminal action with 4-stage lifecycle | Yes |
| 5 | mixed_step_types | Action + prompt steps combined | Both step_type values present | Yes |
| 6 | multi_audience_fanout | Per-audience output generation | Per-audience filename pattern | Yes |

**Count: 6 workflow patterns defined. Matches frontmatter workflow_pattern_count: 6.**

### Validation Check Coverage

| # | Check ID | Severity | Defined |
|---|---|---|---|
| 1 | CV-001 | CRITICAL | Yes |
| 2 | CV-002 | CRITICAL | Yes |
| 3 | CV-003 | CRITICAL | Yes |
| 4 | CV-004 | CRITICAL | Yes |
| 5 | CV-005 | CRITICAL | Yes |
| 6 | CV-006 | CRITICAL | Yes |
| 7 | CV-007 | CRITICAL | Yes |
| 8 | CV-008 | HIGH | Yes |
| 9 | CV-009 | HIGH | Yes |
| 10 | CV-010 | HIGH | Yes |

**Count: 10 validation checks defined (CV-001 through CV-010).**

### Verification Checklist

- [x] Exactly 8 binding rules defined (BR-001 through BR-008), one per component type.
- [x] 3 input data bindings from spec Section 3.2 defined (codebase_docs, codebase_manifest, audience_defs).
- [x] Each binding rule specifies: binding name, component type, cardinality, required status, binding pattern, reference pattern.
- [x] 6 workflow patterns defined (linear_pipeline, review_refine_loop, plugin_extensible_audience, staging_publish_lifecycle, mixed_step_types, multi_audience_fanout).
- [x] Override mechanism covers all 4 audience fields: tone, focus_areas, exclude, section_structure.
- [x] Override mechanism clarifies audience-specific configuration vs. traditional component-level overrides.
- [x] Placeholder resolution defines 4 priority-ordered data sources: Runtime context (1), Audience definition (2), Codebase manifest (3), Job runtime (4).
- [x] Placeholder resolution includes unresolved handling rules.
- [x] Ordering rules cover: foundation first, layer sequence, gatekeep after generate, terminal last, refine loop placement, routing consistency, no forward references, input data ordering.
- [x] 10 composition validation checks (CV-001 through CV-010) with severity levels.
- [x] 2 complete example compositions provided.
- [x] Example input/output directory structure from spec Section 3.5 included.
- [x] Composition structure YAML includes all required fields: builder_name, builder_label, job_prefix, builder_purpose, workflow_pattern, step_bindings, artifact_bindings, role_bindings, routing_bindings, prompt_bindings, composition_standard_binding, output_variances, domain_specs, input_bindings.
- [x] 3 initial audience files specified: developer.md, architect.md, executive.md.
- [x] Audience definition frontmatter schema includes 6 fields: audience_id, label, tone, focus_areas, exclude, section_structure.
- [x] Constraint preserved: no user-provided input artifacts; all paths resolved from repo structure at runtime.
- [x] Binding rules correctly reference component types from COMPONENT_SCHEMA.md.
- [x] Placeholder resolution data sources are consistent with workflow runtime context.
- [x] Routing patterns consistent with Phase 2 output (ROUTE-001 through ROUTE-005).
- [x] ASCII-only content. No em-dashes, curly quotes, or Unicode characters.
- [x] All content traces to the input specification (codebase_to_meta_v1.md). No scope invention.
- [x] YAML frontmatter includes: doc_type, lifecycle_status, layer, binding_rule_count, workflow_pattern_count.
- [x] Governance path references use filenames only (METADATA_STANDARD.md, COMPONENT_SCHEMA.md), not filesystem paths.

---

**End of Composition Format Document**
