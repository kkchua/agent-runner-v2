---
doc_type: "component_schema"
lifecycle_status: "draft"
domain: "workflow_builder"
component_type_count: 8
---

# Component Schema for Workflow Builder v3

## Overview

This document defines the Layer 1 component schema for the Workflow Builder v3
composition system. It specifies the foundational building block library used by
the workflow_builder domain.

The schema defines exactly 8 component types, each corresponding to one of the
8 design phases (Phases 1-8) in the pipeline. Phase 9 (Package) is the assembly
of all components into the final deliverable and does not introduce an additional
component type.

**Schema pattern reference:** COMPOSITION_SYSTEM_STANDARD.md (v2). The component
types defined here are fine-tuned from the base composition system standard for
the workflow_builder domain. All 8 types are required and have singleton
cardinality -- exactly one instance of each is produced per pipeline execution.

**Component type count:** 8

| Phase | Component Type | Purpose |
|-------|---------------|---------|
| 1 | domain_analysis | Domain understanding, identity, output type, meta-test-criteria |
| 2 | component_schema | Fine-tuned base schema for target domain |
| 3 | composition_format | How domain components bind together |
| 4 | output_format | What the target workflow produces |
| 5 | artifact_contract | Artifact keys and filename patterns |
| 6 | step_sequence | Target workflow step design and delivery mechanism |
| 7 | runtime_standard | Consolidated composition standard for target |
| 8 | operational_workflow | Concrete workflow implementation design |

---

## Common Properties

All 8 component types share a common property set. These properties provide
identity, provenance, and governance for every design artifact produced during
the pipeline.

### Required Common Properties

There are exactly 7 required common properties. Every component instance must
declare all of them.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| component_id | string | Yes | Unique identifier. Format: {phase}-{type}-{workflow_name}. Example: "phase-1-domain_analysis-my_workflow" |
| component_type | enum | Yes | One of the 8 component types defined in the Component Types section. The enum values are: domain_analysis, component_schema, composition_format, output_format, artifact_contract, step_sequence, runtime_standard, operational_workflow |
| name | string | Yes | Human-readable display name for the component instance |
| version | string | Yes | Semantic version string. Matches the target spec standard_version (e.g., "1.0.0") |
| description | string | Yes | What this artifact contains and its role in the pipeline |
| phase_origin | integer | Yes | Which phase produced this artifact. Must be an integer from 1 to 8, matching the phase-to-type mapping |
| identity_locked | boolean | Yes | True if all identity fields (workflow_name, standard_name, standard_version, standard_filename) match the target spec and not the builder. Must be true for all artifacts |

### Optional Common Properties

The following optional properties may be included when applicable:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| duration_range | object | No | Estimated time range for producing this component (e.g., {min: "2m", max: "10m"}) |
| platforms | array | No | List of platforms this component targets (e.g., ["cli", "daemon"]) |
| tags | array | No | Free-form tags for categorization and search |

---

## Component Types

### Type 1: domain_analysis

**Phase:** 1
**Purpose:** Captures domain understanding, target identity, output type
declaration, natural phases, component inventory, and meta-test-criteria that
are propagated to all subsequent phases.
**Required:** Yes
**Cardinality:** Singleton

#### Type-Specific Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| target_identity | object | Yes | Identity fields extracted from the runtime spec: standard_name (string), standard_version (string), standard_filename (string) |
| output_type | enum | Yes | The declared output delivery type: "documented_versioned" or "direct" |
| natural_phases | array | Yes | The target domain natural workflow phases as identified from the spec |
| component_inventory | array | Yes | Identified domain components from the spec |
| meta_test_criteria | array | Yes | Cross-phase invariants for all gatekeepers. Injected into all subsequent phase gatekeep prompts |

#### Validation Rules

- target_identity must contain standard_name, standard_version, and standard_filename
- output_type must be one of: "documented_versioned", "direct"
- natural_phases must be a non-empty array
- meta_test_criteria must contain at minimum 4 invariants covering: identity uses spec not builder, structure matches spec domain, output delivery matches spec output type, component types derived not hardcoded

#### Example

```yaml
component_id: "phase-1-domain_analysis-my_workflow"
component_type: "domain_analysis"
name: "Domain Analysis for my_workflow"
version: "1.0.0"
description: "Domain understanding, target identity, output type, and meta-test-criteria for the my_workflow pipeline"
phase_origin: 1
identity_locked: true
target_identity:
  standard_name: "MY_WORKFLOW_STANDARD"
  standard_version: "1.0.0"
  standard_filename: "MY_WORKFLOW_STANDARD-v1.md"
output_type: "documented_versioned"
natural_phases:
  - "Analyze requirements"
  - "Define component schema"
  - "Design composition"
  - "Specify outputs"
  - "Define artifacts"
  - "Design steps"
  - "Consolidate standard"
  - "Implement workflow"
component_inventory:
  - "requirements_analysis"
  - "schema_definition"
  - "composition_design"
meta_test_criteria:
  - "Generated workflow uses spec identity, not builder identity"
  - "Generated workflow structure matches spec domain, not AMB structure"
  - "Output delivery mechanism matches spec declared output type"
  - "All component types derived from base schema fine-tuning, not hardcoded"
```

---

### Type 2: component_schema

**Phase:** 2
**Purpose:** The fine-tuned base component schema for the target domain. Records
which base schema types were kept, added, dropped, or specialized, with
rationale for each decision.
**Required:** Yes
**Cardinality:** Singleton

#### Type-Specific Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| base_schema_version | string | Yes | Version of COMPOSITION_SYSTEM_STANDARD.md used as the base. Must be >= "2.0" |
| fine_tuning_decisions | array | Yes | List of keep/add/drop/specialize decisions with rationale for each base schema type |
| domain_types | array | Yes | The component types defined for the target domain after fine-tuning |
| validation_rules | array | Yes | Domain-specific validation rules derived from fine-tuning decisions |

#### Validation Rules

- base_schema_version must be a valid semver string >= "2.0"
- fine_tuning_decisions must be a non-empty array; each entry must include decision type (keep/add/drop/specialize) and rationale
- domain_types must contain exactly the 8 types defined for this domain
- validation_rules must be a non-empty array of specific, enforceable rules

#### Example

```yaml
component_id: "phase-2-component_schema-my_workflow"
component_type: "component_schema"
name: "Component Schema for my_workflow"
version: "1.0.0"
description: "Fine-tuned base component schema for the my_workflow domain, derived from COMPOSITION_SYSTEM_STANDARD.md v2"
phase_origin: 2
identity_locked: true
base_schema_version: "2.0.0"
fine_tuning_decisions:
  - decision: "keep"
    type: "requirements_analysis"
    rationale: "Base type aligns with domain requirement for spec analysis"
  - decision: "specialize"
    type: "schema_definition"
    rationale: "Narrowed to component schema subset for workflow domain"
  - decision: "add"
    type: "composition_design"
    rationale: "Domain requires explicit composition binding rules"
domain_types:
  - "domain_analysis"
  - "component_schema"
  - "composition_format"
  - "output_format"
  - "artifact_contract"
  - "step_sequence"
  - "runtime_standard"
  - "operational_workflow"
validation_rules:
  - "VR-001: Required common fields present"
  - "VR-002: Valid component_type from the 8 defined types"
```

---

### Type 3: composition_format

**Phase:** 3
**Purpose:** Defines how domain components bind together. Specifies binding
rules, override mechanisms, placeholder resolution, and optional examples.
**Required:** Yes
**Cardinality:** Singleton

#### Type-Specific Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| binding_rules | array | Yes | How domain components bind together. Each rule specifies source phase, consumed-by phases, required flag, and description |
| override_mechanism | object | Yes | Per-composition customization rules. Identity fields always sourced from runtime spec, never derived |
| placeholder_resolution | object | Yes | External data source mapping for all placeholders used in the composition |
| examples | array | No | Sample compositions demonstrating binding patterns |

#### Validation Rules

- binding_rules must contain exactly 8 entries, one per component type
- Each binding rule must specify: binding name, source_phase (integer 1-8), consumed_by_phases (array), required (boolean), description (string)
- override_mechanism must specify identity field sourcing rules and meta-test-criteria injection
- placeholder_resolution must cover all 7 placeholders: WORKFLOW_SPEC_FILE, BASE_COMPOSITION_STANDARD, standard_name, standard_version, standard_filename, output_type, workflow_name

#### Example

```yaml
component_id: "phase-3-composition_format-my_workflow"
component_type: "composition_format"
name: "Composition Format for my_workflow"
version: "1.0.0"
description: "Defines how the 8 domain components bind together in the my_workflow pipeline"
phase_origin: 3
identity_locked: true
binding_rules:
  - binding: "domain_analysis"
    source_phase: 1
    consumed_by_phases: [2, 3, 4, 5, 6, 7, 8]
    required: true
    description: "Identity, output type, natural phases, and meta-test-criteria"
  - binding: "component_schema"
    source_phase: 2
    consumed_by_phases: [3, 7]
    required: true
    description: "Fine-tuned schema for target domain"
  - binding: "composition_format"
    source_phase: 3
    consumed_by_phases: [4, 7]
    required: true
    description: "Binding rules for domain components"
  - binding: "output_format"
    source_phase: 4
    consumed_by_phases: [6, 7]
    required: true
    description: "Output structure and quality requirements"
  - binding: "artifact_contract"
    source_phase: 5
    consumed_by_phases: [6, 8]
    required: true
    description: "Artifact keys for target workflow"
  - binding: "step_sequence"
    source_phase: 6
    consumed_by_phases: [7, 8]
    required: true
    description: "Target workflow step design"
  - binding: "runtime_standard"
    source_phase: 7
    consumed_by_phases: [8]
    required: true
    description: "Consolidated standard for implementation"
  - binding: "operational_workflow"
    source_phase: 8
    consumed_by_phases: [9]
    required: true
    description: "Concrete workflow implementation"
override_mechanism:
  identity_sourcing: "runtime_spec"
  meta_test_criteria_injection: true
  base_schema_resolution: "context_extensions"
placeholder_resolution:
  WORKFLOW_SPEC_FILE:
    source: "runtime spec file path"
    required: true
  BASE_COMPOSITION_STANDARD:
    source: "base schema file path"
    required: true
  standard_name:
    source: "spec identity section"
    required: true
  standard_version:
    source: "spec identity section"
    required: true
  standard_filename:
    source: "spec identity section"
    required: true
  output_type:
    source: "spec output delivery section"
    required: true
  workflow_name:
    source: "spec identity section"
    required: true
examples:
  - name: "Sample binding chain"
    description: "domain_analysis feeds all subsequent phases via meta-test-criteria"
```

---

### Type 4: output_format

**Phase:** 4
**Purpose:** Defines what the target workflow produces -- the output artifacts,
resolution rules, and quality requirements.
**Required:** Yes
**Cardinality:** Singleton

#### Type-Specific Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| output_sections | array | Yes | Structure of the target output. Each entry specifies the output artifact, its source phase, and description |
| resolution_rules | array | Yes | How references are expanded and consolidated into the final deliverable |
| quality_requirements | array | Yes | Measurable quality criteria (QR-NNN) that the output must satisfy |

#### Validation Rules

- output_sections must list all output artifacts with their source phases and descriptions
- resolution_rules must be a non-empty array of specific, actionable rules
- quality_requirements must use QR-NNN identifiers with specific verifiable statements
- No quality requirement may use vague language such as "must work properly" or "must be correct"

#### Example

```yaml
component_id: "phase-4-output_format-my_workflow"
component_type: "output_format"
name: "Output Format for my_workflow"
version: "1.0.0"
description: "Defines the 7 output artifacts, resolution rules, and quality requirements for the my_workflow pipeline"
phase_origin: 4
identity_locked: true
output_sections:
  - artifact: "workflow.toml"
    source_phase: "8+9"
    description: "Complete workflow definition with correct identity"
  - artifact: "context_extensions.py"
    source_phase: "8+9"
    description: "Domain-specific artifact keys and path resolution"
  - artifact: "actions.py"
    source_phase: "8+9"
    description: "Domain-specific action implementations"
  - artifact: "prompts/*.txt"
    source_phase: "8+9"
    description: "One prompt file per prompt-driven step"
  - artifact: "README.md"
    source_phase: 9
    description: "Describes the target workflow"
  - artifact: "Standards/{standard_filename}"
    source_phase: "7+9"
    description: "Target composition standard"
  - artifact: "Specs/{builder_name}.md"
    source_phase: 9
    description: "Embedded builder spec for self-bootstrap"
resolution_rules:
  - "All phase outputs consolidated: Phase 7 consolidates Phases 1-6 into the runtime standard"
  - "Identity resolved: All identity fields from runtime spec, not builder"
  - "Placeholders resolved: All placeholders filled from spec and context"
  - "Self-contained: Workflow package executable without reference to builder"
  - "Self-bootstrapping: Builder spec embedded in Specs/ for recursive chain"
quality_requirements:
  - id: "QR-001"
    rule: "Identity correctness: workflow.toml name matches spec workflow_name"
  - id: "QR-002"
    rule: "No builder leakage: no reference to builder identity in output"
```

---

### Type 5: artifact_contract

**Phase:** 5
**Purpose:** Defines the artifact keys, filename patterns, and conflict check
status for the target workflow.
**Required:** Yes
**Cardinality:** Singleton

#### Type-Specific Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| artifact_keys | array | Yes | Key-to-filename-pattern-to-description mappings. Each entry defines an artifact key, its filename pattern, and its description |
| conflict_check_passed | boolean | Yes | True if no conflicts detected with the global artifact key registry |

#### Validation Rules

- artifact_keys must be a non-empty array
- Each entry must include: key (string), filename_pattern (string), description (string)
- All artifact key names must be unique within this contract
- conflict_check_passed must be true for the artifact to be accepted

#### Example

```yaml
component_id: "phase-5-artifact_contract-my_workflow"
component_type: "artifact_contract"
name: "Artifact Contract for my_workflow"
version: "1.0.0"
description: "Defines artifact keys, filename patterns, and conflict check status for my_workflow"
phase_origin: 5
identity_locked: true
artifact_keys:
  - key: "WORKFLOW_SPEC_FILE"
    filename_pattern: "WORKFLOW_SPEC_FILE"
    description: "Runtime specification input file"
  - key: "OUTPUT_FILE"
    filename_pattern: "OUTPUT-{seq}.md"
    description: "Primary output artifact"
  - key: "MANIFEST_FILE"
    filename_pattern: "MANIFEST-{seq}.toml"
    description: "Workflow manifest definition"
conflict_check_passed: true
```

---

### Type 6: step_sequence

**Phase:** 6
**Purpose:** Defines the target workflow step design, including step definitions,
optional review loops, optional approval gates, and the delivery mechanism.
**Required:** Yes
**Cardinality:** Singleton

#### Type-Specific Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| steps | array | Yes | Step definitions. Each entry specifies: step name, step type (prompt or action), artifact keys produced/consumed, and routing configuration |
| review_loops | array | No | Review and refine step pairs. Applicable when output_type is documented_versioned |
| approval_gates | array | No | Steps requiring human approval before proceeding |
| delivery_mechanism | object | Yes | How the output is delivered. For documented_versioned: promote and archive. For direct: immediate delivery |

#### Validation Rules

- steps must be a non-empty array
- Each step entry must include: name (string), type (enum: "prompt" or "action"), routing (object with onsuccess and optional on_reject_refine)
- review_loops, when present, must define paired review and refine steps with max_iterations
- delivery_mechanism must match the output_type declared in domain_analysis

#### Example

```yaml
component_id: "phase-6-step_sequence-my_workflow"
component_type: "step_sequence"
name: "Step Sequence for my_workflow"
version: "1.0.0"
description: "Defines the step design, review loops, and delivery mechanism for my_workflow"
phase_origin: 6
identity_locked: true
steps:
  - name: "analyze_input"
    type: "action"
    routing:
      onsuccess: "generate_output"
  - name: "generate_output"
    type: "prompt"
    routing:
      onsuccess: "validate_output"
      on_reject_refine: "refine_output"
  - name: "validate_output"
    type: "action"
    routing:
      onsuccess: "deliver"
review_loops:
  - review_step: "review_output"
    refine_step: "refine_output"
    max_iterations: 3
approval_gates:
  - step: "approve_output"
    condition: "output_type == documented_versioned"
delivery_mechanism:
  type: "documented_versioned"
  promote_action: "promote_package"
  archive_action: "archive_package"
```

---

### Type 7: runtime_standard

**Phase:** 7
**Purpose:** Consolidates the content from Phases 1-6 into a single coherent
runtime composition standard for the target workflow.
**Required:** Yes
**Cardinality:** Singleton

#### Type-Specific Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| standard_name | string | Yes | From target spec identity. This is the target standard name, not the builder standard name |
| standard_version | string | Yes | From target spec identity. Semantic version string |
| consolidated_phases | array | Yes | Content from Phases 1-6 consolidated into a single reference. Each entry maps a phase number to its consolidated content summary |
| cross_phase_consistency | boolean | Yes | True if all phases are mutually consistent -- consistent naming conventions, artifact key formats, validation patterns, and identity locking rules |

#### Validation Rules

- standard_name must match the target spec identity (not the builder)
- standard_version must match the target spec identity
- consolidated_phases must cover Phases 1 through 6
- cross_phase_consistency must be true; if false, the artifact fails validation

#### Example

```yaml
component_id: "phase-7-runtime_standard-my_workflow"
component_type: "runtime_standard"
name: "Runtime Standard for my_workflow"
version: "1.0.0"
description: "Consolidated composition standard for my_workflow, merging Phases 1-6 into a single coherent reference"
phase_origin: 7
identity_locked: true
standard_name: "MY_WORKFLOW_STANDARD"
standard_version: "1.0.0"
consolidated_phases:
  - phase: 1
    type: "domain_analysis"
    summary: "Domain identity, output type, natural phases, meta-test-criteria"
  - phase: 2
    type: "component_schema"
    summary: "Fine-tuned schema with 8 domain types and validation rules"
  - phase: 3
    type: "composition_format"
    summary: "Binding rules, override mechanism, placeholder resolution"
  - phase: 4
    type: "output_format"
    summary: "7 output artifacts, 5 resolution rules, quality requirements"
  - phase: 5
    type: "artifact_contract"
    summary: "Artifact key registry with conflict check passed"
  - phase: 6
    type: "step_sequence"
    summary: "Step definitions, review loops, delivery mechanism"
cross_phase_consistency: true
```

---

### Type 8: operational_workflow

**Phase:** 8
**Purpose:** Defines the concrete workflow implementation design, including the
actual step sequence with routing, prompt file specifications, action
implementations needed, and context extensions for artifact key resolution.
**Required:** Yes
**Cardinality:** Singleton

#### Type-Specific Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| workflow_steps | array | Yes | Concrete step sequence with routing. Each entry specifies: step name, step type (prompt or action), onsuccess routing, and optional on_reject_refine routing |
| prompt_files | array | Yes | One entry per prompt-driven step. Each entry specifies the prompt filename and the step it serves |
| action_implementations | array | Yes | Python action functions needed. Each entry specifies the action name, function signature, and behavior description |
| context_extensions | object | Yes | Artifact key definitions and path resolution logic for the target workflow |

#### Validation Rules

- workflow_steps must be a non-empty array with valid routing (every onsuccess target must reference an existing step)
- prompt_files must contain exactly one entry per prompt-type step in workflow_steps
- action_implementations must contain exactly one entry per action-type step in workflow_steps
- context_extensions must define all artifact keys referenced in workflow_steps

#### Example

```yaml
component_id: "phase-8-operational_workflow-my_workflow"
component_type: "operational_workflow"
name: "Operational Workflow for my_workflow"
version: "1.0.0"
description: "Concrete workflow implementation design for my_workflow with step routing, prompt files, actions, and context extensions"
phase_origin: 8
identity_locked: true
workflow_steps:
  - name: "analyze_input"
    type: "action"
    routing:
      onsuccess: "generate_design"
  - name: "generate_design"
    type: "prompt"
    routing:
      onsuccess: "validate_design"
      on_reject_refine: "refine_design"
  - name: "validate_design"
    type: "action"
    routing:
      onsuccess: "deliver"
  - name: "deliver"
    type: "action"
    routing:
      onsuccess: null
prompt_files:
  - filename: "prompts/02_generate_design.txt"
    step: "generate_design"
action_implementations:
  - name: "analyze_input"
    signature: "def analyze_input(ctx)"
    description: "Reads and validates the input spec"
  - name: "validate_design"
    signature: "def validate_design(ctx)"
    description: "Deterministic checks on generated design artifact"
  - name: "deliver"
    signature: "def deliver(ctx)"
    description: "Promotes the validated package to the output directory"
context_extensions:
  class_name: "MyWorkflowContextExtensions"
  artifact_keys:
    - key: "WORKFLOW_SPEC_FILE"
      path_pattern: "{job_dir}/WORKFLOW_SPEC_FILE"
    - key: "OUTPUT_FILE"
      path_pattern: "{job_dir}/OUTPUT-{seq}.md"
```

---

## Validation Rules (Global)

These 8 validation rules apply to all component instances across the pipeline.
Each rule is specific, enforceable, and independently verifiable.

**VR-001: Required Common Fields Present**
All 7 required common fields must be present in every component instance:
component_id, component_type, name, version, description, phase_origin,
identity_locked. Missing any field is a validation failure.

**VR-002: Valid Component Type**
The component_type field must be one of the 8 types defined in the Component
Types section: domain_analysis, component_schema, composition_format,
output_format, artifact_contract, step_sequence, runtime_standard,
operational_workflow. Any other value is a validation failure.

**VR-003: Unique Component Identifier**
The component_id value must be unique across all component instances in the
pipeline. No two components may share the same component_id. The format must
follow: {phase}-{type}-{workflow_name}.

**VR-004: Type-Specific Schema Conformance**
All required properties for the declared component_type must be present in the
component instance. Each type-specific property must match its declared type
(string, enum, array, object, boolean, integer).

**VR-005: Identity Locking Verified**
The identity_locked field must be true for all component instances. This
confirms that identity fields (workflow_name, standard_name, standard_version,
standard_filename) match the target spec and not the builder.

**VR-006: Phase Origin Matches Position**
The phase_origin field must be an integer from 1 to 8 and must match the
artifact's position in the pipeline. Phase 1 produces domain_analysis, Phase 2
produces component_schema, and so on through Phase 8 which produces
operational_workflow.

**VR-007: Base Schema Version Check**
For component_schema type artifacts, the base_schema_version field must be a
valid semantic version string that is >= "2.0". Versions below 2.0 are not
compatible with the current composition system standard.

**VR-008: Artifact Contract Conflict Check**
For artifact_contract type artifacts, the conflict_check_passed field must be
true. A false value indicates that artifact key conflicts were detected with
the global registry, and the contract cannot be accepted until conflicts are
resolved.

---

## Extensibility Model

The component schema supports extensibility through the following mechanisms,
ensuring that new types can be added without breaking existing compositions.

**Adding New Component Types:**
New component types may be added to the schema in a future version. Each new
type must:
1. Declare a unique component_type enum value.
2. Define its own type-specific properties with clear required/optional status.
3. Map to a specific phase_origin value.
4. Have at least one validation rule specific to the new type.
5. Include a complete example component in YAML format.

**Backward Compatibility:**
Adding new types does not invalidate existing compositions. Existing components
retain their validation rules and property definitions. The common property set
(7 required, 3 optional) remains unchanged. New types are additive -- they do
not modify the behavior of existing types.

**Schema Versioning:**
The base schema version (tracked in component_schema type via
base_schema_version) follows semantic versioning. Minor version increments
indicate additive changes (new types, new optional properties). Major version
increments indicate breaking changes that require migration of existing
compositions.

**Fine-Tuning Protocol:**
When a new domain adopts this schema, it uses the fine-tuning mechanism
(recorded in component_schema type via fine_tuning_decisions) to decide which
base types to keep, add, drop, or specialize. This allows domain-specific
adaptation while maintaining traceability to the base schema.

---

## Component File Format

Components are stored and exchanged as YAML documents embedded within Markdown
files. The file format ensures both human readability and machine parseability.

**File Structure:**
Each component file is a Markdown document with YAML frontmatter followed by
structured sections.

```markdown
---
doc_type: "{component_type}"
lifecycle_status: "draft"
domain: "{domain_name}"
---

# {Component Name}

## Overview
...

## Properties
...

## Validation Rules
...

## Example

```yaml
component_id: "phase-{N}-{type}-{workflow_name}"
component_type: "{type}"
name: "..."
version: "..."
description: "..."
phase_origin: {N}
identity_locked: true
# type-specific properties follow
```
```

**Frontmatter Requirements:**
Every component file must include YAML frontmatter with at minimum:
- doc_type: Set to the component_type value (e.g., "domain_analysis")
- lifecycle_status: One of "draft", "review", "approved", "archived"
- domain: The domain name (e.g., "workflow_builder")

**Naming Convention:**
Component files follow the pattern: {COMPONENT_TYPE_UPPER}-{seq}.md
For example: COMPONENT_SCHEMA-001.md, DOMAIN_ANALYSIS-001.md

**Storage Location:**
Component files are stored under the job run directory:
runs/{job_id}/{COMPONENT_TYPE_UPPER}-{seq}.md

**Exchange Format:**
When components are consumed by subsequent pipeline phases, they are referenced
by their artifact key (e.g., DOMAIN_ANALYSIS_FILE). The artifact key resolves
to the absolute file path via context_extensions. Components are never embedded
inline -- they are always referenced by path to maintain single-source-of-truth
semantics.

---

## Self-Validation

This section verifies the completeness and internal consistency of this
component schema document.

**Check 1: Type Count**
Exactly 8 component types are defined: domain_analysis, component_schema,
composition_format, output_format, artifact_contract, step_sequence,
runtime_standard, operational_workflow. Count verified: 8. PASS.

**Check 2: Phase Mapping**
Each type maps to its correct phase:
- domain_analysis -> Phase 1: PASS
- component_schema -> Phase 2: PASS
- composition_format -> Phase 3: PASS
- output_format -> Phase 4: PASS
- artifact_contract -> Phase 5: PASS
- step_sequence -> Phase 6: PASS
- runtime_standard -> Phase 7: PASS
- operational_workflow -> Phase 8: PASS

**Check 3: Required and Cardinality**
All 8 types are marked Required = Yes and Cardinality = Singleton. PASS.

**Check 4: Common Properties**
7 required common properties defined: component_id, component_type, name,
version, description, phase_origin, identity_locked. PASS.

**Check 5: Type-Specific Properties**
Each of the 8 types has type-specific properties defined with name, type,
required status, and description. PASS.
- domain_analysis: 5 properties (target_identity, output_type, natural_phases,
  component_inventory, meta_test_criteria)
- component_schema: 4 properties (base_schema_version, fine_tuning_decisions,
  domain_types, validation_rules)
- composition_format: 4 properties (binding_rules, override_mechanism,
  placeholder_resolution, examples)
- output_format: 3 properties (output_sections, resolution_rules,
  quality_requirements)
- artifact_contract: 2 properties (artifact_keys, conflict_check_passed)
- step_sequence: 4 properties (steps, review_loops, approval_gates,
  delivery_mechanism)
- runtime_standard: 4 properties (standard_name, standard_version,
  consolidated_phases, cross_phase_consistency)
- operational_workflow: 4 properties (workflow_steps, prompt_files,
  action_implementations, context_extensions)

**Check 6: Validation Rules**
8 validation rules defined (VR-001 through VR-008), each with unique
identifier and specific verifiable statement. PASS.

**Check 7: Examples**
Each of the 8 types includes a complete YAML example with all common properties
and type-specific properties populated. PASS.

**Check 8: ASCII Compliance**
All content in this document uses ASCII characters only. No em-dashes, curly
quotes, or Unicode characters present. PASS.

---

End of Component Schema Document
