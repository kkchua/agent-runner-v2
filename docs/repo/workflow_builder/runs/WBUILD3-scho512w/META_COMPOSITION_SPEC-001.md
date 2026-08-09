---
doc_type: "meta_composition_spec"
lifecycle_status: "draft"
domain: "ar_meta_builder_v2"
self_bootstrap_capable: true
---

# Meta Composition Spec: AR Meta Builder v2

## 1. Domain Overview

**Domain name:** ar_meta_builder_v2
**Label:** AR Meta Builder v2
**Job prefix:** AMB
**Init step:** validate_input_spec
**Description:** Transforms a runtime specification into a complete, executable
workflow package by fine-tuning the Base Component Schema for the target domain
and assembling the design through a 9-phase TDD-driven pipeline.

### 1.1 Purpose

The agent-runner-v2 platform uses workflow packages to define executable
workflows. Creating these packages manually is error-prone and inconsistent.
A meta-builder automates the creation process: given a runtime spec that
describes the target workflow's domain, the meta-builder designs and generates
a complete workflow package with correct identity, proper artifact tracking,
domain-appropriate step structure, and full test coverage.

AMB v2 is the second iteration. v1 failed because it copied its own 9-phase/22-step
structure and identity into every generated workflow. v2 fixes this through:
- TDD as DNA -- every phase follows a standardized test-driven pattern
- Identity locking -- the target spec's identity is locked at Phase 1 and propagated
- Fine-tuning from base schema -- component types are derived, not hardcoded
- Output type distinction -- documented/versioned vs direct delivery

### 1.2 Domain Context

**Input:** A runtime spec (markdown with YAML frontmatter) that declares:
- Workflow identity (standard_name, standard_version, standard_filename)
- Output delivery type (documented_versioned or direct)
- Domain overview and natural phases
- Component types and their properties
- Composition and output format requirements

**Output:** A complete executable workflow package:
- workflow.toml -- workflow definition with correct identity
- context_extensions.py -- domain-specific artifact keys and path resolution
- actions.py -- domain-specific action implementations
- prompts/ -- one prompt file per prompt-driven step
- README.md -- describing the target workflow
- Standards/{standard_filename} -- the target's composition standard
- Specs/{builder_name}.md -- embedded builder spec (self-bootstrap)

### 1.3 Recursive Chain

AMB v2 output is structurally identical to its own package. Each generated
standard specializes its parent's standard:

```
Workflow Builder v4 -> AMB v2 -> [target workflow]
```

This meta composition spec is designed to be consumed as input by the
generated meta builder, enabling the recursive self-bootstrap chain. The
spec contains all information necessary to define the component types,
composition format, and output format for a builder that processes runtime
specifications into executable workflow packages.

---

## 2. Workflow Identity

```yaml
workflow_name: "ar_meta_builder_v2"
standard_name: "AMB_STANDARD"
standard_version: "2.0.0"
standard_filename: "AMB_STANDARD-v2.md"
```

These values are the meta-builder's OWN identity. They must NOT leak into
generated output. The generated workflow uses the TARGET spec's identity.

All artifacts in this pipeline must set identity_locked = true, confirming
that identity fields match the target spec and not the builder.

---

## 3. Output Delivery

```yaml
output_type: "documented_versioned"
approval_before_execution: false
archive_after_approval: true
```

The meta-builder produces workflow packages that need versioning, audit trail,
approval gates, and promotion. The full documented/versioned pipeline applies:
generate, review, refine, approve, promote, archive.

---

## 4. Component Schema

### 4.1 Component Types

The meta-builder domain has exactly 8 component types. Each type corresponds
to one of the 8 design phases (Phases 1-8). Phase 9 (Package) is the
assembly of all components into the final deliverable and does not introduce
an additional component type.

| # | Component Type | Phase | Purpose | Required | Cardinality |
|---|---------------|-------|---------|----------|-------------|
| 1 | domain_analysis | 1 | Domain understanding, identity, output type, meta-test-criteria | Yes | Singleton |
| 2 | component_schema | 2 | Fine-tuned base schema for target domain | Yes | Singleton |
| 3 | composition_format | 3 | How domain components bind together | Yes | Singleton |
| 4 | output_format | 4 | What the target workflow produces | Yes | Singleton |
| 5 | artifact_contract | 5 | Artifact keys and filename patterns | Yes | Singleton |
| 6 | step_sequence | 6 | Target workflow step design and delivery mechanism | Yes | Singleton |
| 7 | runtime_standard | 7 | Consolidated composition standard for target | Yes | Singleton |
| 8 | operational_workflow | 8 | Concrete workflow implementation design | Yes | Singleton |

### 4.2 Common Properties

All 8 component types share a common property set. These properties provide
identity, provenance, and governance for every design artifact produced
during the pipeline.

There are exactly 7 required common properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| component_id | string | Yes | Unique identifier. Format: {phase}-{type}-{workflow_name}. Example: "phase-1-domain_analysis-my_workflow" |
| component_type | enum | Yes | One of the 8 component types defined in section 4.1 |
| name | string | Yes | Human-readable display name for the component instance |
| version | string | Yes | Semantic version string. Matches the target spec standard_version |
| description | string | Yes | What this artifact contains and its role in the pipeline |
| phase_origin | integer | Yes | Which phase produced this artifact. Must be an integer from 1 to 8 |
| identity_locked | boolean | Yes | True if all identity fields match the target spec and not the builder |

Optional common properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| duration_range | object | No | Estimated time range for producing this component |
| platforms | array | No | List of platforms this component targets |
| tags | array | No | Free-form tags for categorization and search |

### 4.3 Type-Specific Properties

#### Type 1: domain_analysis (Phase 1)

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| target_identity | object | Yes | Identity fields from runtime spec: standard_name, standard_version, standard_filename |
| output_type | enum | Yes | Output delivery type: "documented_versioned" or "direct" |
| natural_phases | array | Yes | Target domain natural workflow phases |
| component_inventory | array | Yes | Identified domain components |
| meta_test_criteria | array | Yes | Cross-phase invariants for all gatekeepers |

#### Type 2: component_schema (Phase 2)

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| base_schema_version | string | Yes | Version of COMPOSITION_SYSTEM_STANDARD.md used. Must be >= "2.0" |
| fine_tuning_decisions | array | Yes | Keep/add/drop/specialize decisions with rationale |
| domain_types | array | Yes | Component types defined for the target domain |
| validation_rules | array | Yes | Domain-specific validation rules |

#### Type 3: composition_format (Phase 3)

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| binding_rules | array | Yes | How domain components bind together |
| override_mechanism | object | Yes | Per-composition customization rules |
| placeholder_resolution | object | Yes | External data source mapping |
| examples | array | No | Sample compositions |

#### Type 4: output_format (Phase 4)

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| output_sections | array | Yes | Structure of the target output |
| resolution_rules | array | Yes | How references are expanded |
| quality_requirements | array | Yes | Measurable quality criteria (QR-NNN) |

#### Type 5: artifact_contract (Phase 5)

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| artifact_keys | array | Yes | Key-to-filename-pattern-to-description mappings |
| conflict_check_passed | boolean | Yes | True if no conflicts with global registry |

#### Type 6: step_sequence (Phase 6)

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| steps | array | Yes | Step definitions (name, type, routing, role policy) |
| review_loops | array | No | Review/refine pairs (for documented_versioned) |
| approval_gates | array | No | Steps requiring human approval |
| delivery_mechanism | object | Yes | How output is delivered (promote/archive or direct) |

#### Type 7: runtime_standard (Phase 7)

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| standard_name | string | Yes | From target spec identity |
| standard_version | string | Yes | From target spec identity |
| consolidated_phases | array | Yes | Phases 1-6 content consolidated |
| cross_phase_consistency | boolean | Yes | True if all phases are mutually consistent |

#### Type 8: operational_workflow (Phase 8)

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| workflow_steps | array | Yes | Concrete step sequence with routing |
| prompt_files | array | Yes | One per prompt-driven step |
| action_implementations | array | Yes | Python @action functions needed |
| context_extensions | object | Yes | Artifact keys and path resolution |

### 4.4 Validation Rules

These 8 validation rules apply to all component instances across the pipeline.

**VR-001: Required Common Fields Present**
All 7 required common fields must be present in every component instance:
component_id, component_type, name, version, description, phase_origin,
identity_locked. Missing any field is a validation failure.

**VR-002: Valid Component Type**
The component_type field must be one of the 8 types defined in section 4.1:
domain_analysis, component_schema, composition_format, output_format,
artifact_contract, step_sequence, runtime_standard, operational_workflow.

**VR-003: Unique Component Identifier**
The component_id value must be unique across all component instances in the
pipeline. No two components may share the same component_id. Format:
{phase}-{type}-{workflow_name}.

**VR-004: Type-Specific Schema Conformance**
All required properties for the declared component_type must be present.
Each type-specific property must match its declared type.

**VR-005: Identity Locking Verified**
The identity_locked field must be true for all component instances. This
confirms identity fields match the target spec and not the builder.

**VR-006: Phase Origin Matches Position**
The phase_origin field must be an integer from 1 to 8 and must match the
artifact's position in the pipeline.

**VR-007: Base Schema Version Check**
For component_schema type artifacts, the base_schema_version must be >= "2.0".

**VR-008: Artifact Contract Conflict Check**
For artifact_contract type artifacts, the conflict_check_passed must be true.

---

## 5. Composition Format

### 5.1 Composition Structure

The meta-builder's composition is the pipeline dependency chain -- each
phase's output binds to subsequent phases as input.

```yaml
composition_id: "amb-pipeline-{workflow_name}"
name: "AMB v2 Pipeline for {workflow_name}"
target_metadata:
  workflow_name: "{from spec}"
  standard_name: "{from spec}"
  output_type: "{from spec}"

component_bindings:
  domain_analysis:
    component_id: "phase-1-domain_analysis-{workflow_name}"
    overrides:
      target_identity: "{from WORKFLOW_SPEC_FILE}"
      output_type: "{from WORKFLOW_SPEC_FILE}"

  component_schema:
    component_id: "phase-2-component_schema-{workflow_name}"
    overrides:
      base_schema_path: "{BASE_COMPOSITION_STANDARD}"

  composition_format:
    component_id: "phase-3-composition_format-{workflow_name}"

  output_format:
    component_id: "phase-4-output_format-{workflow_name}"

  artifact_contract:
    component_id: "phase-5-artifact_contract-{workflow_name}"

  step_sequence:
    component_id: "phase-6-step_sequence-{workflow_name}"

  runtime_standard:
    component_id: "phase-7-runtime_standard-{workflow_name}"

  operational_workflow:
    component_id: "phase-8-operational_workflow-{workflow_name}"
```

### 5.2 Binding Rules

Exactly 8 binding rules are defined -- one per component type.

| # | Binding | Source Phase | Consumed By | Required | Pattern |
|---|---------|-------------|-------------|----------|---------|
| 1 | domain_analysis | 1 | 2, 3, 4, 5, 6, 7, 8 | Yes | foundation_broadcast |
| 2 | component_schema | 2 | 3, 7 | Yes | selective_downstream |
| 3 | composition_format | 3 | 4, 7 | Yes | adjacent_consolidation |
| 4 | output_format | 4 | 6, 7 | Yes | skip_consolidation |
| 5 | artifact_contract | 5 | 6, 8 | Yes | adjacent_assembly |
| 6 | step_sequence | 6 | 7, 8 | Yes | sequential_handoff |
| 7 | runtime_standard | 7 | 8 | Yes | sequential_handoff |
| 8 | operational_workflow | 8 | 9 | Yes | sequential_handoff |

**Binding Rule 1: domain_analysis**
Source: Phase 1. Consumed by: Phases 2-8. Provides identity, output type,
natural phases, and meta-test-criteria. This is the foundation binding --
it feeds ALL subsequent phases. Reference pattern: {component_id} resolved
via artifact key DOMAIN_ANALYSIS_FILE.

**Binding Rule 2: component_schema**
Source: Phase 2. Consumed by: Phases 3, 7. Provides the fine-tuned base
schema for the target domain. Reference pattern: {component_id} resolved
via artifact key DOMAIN_COMPONENT_SCHEMA_FILE.

**Binding Rule 3: composition_format**
Source: Phase 3. Consumed by: Phases 4, 7. Defines how domain components
bind together. Reference pattern: {component_id} resolved via artifact key
COMPOSITION_FORMAT_FILE.

**Binding Rule 4: output_format**
Source: Phase 4. Consumed by: Phases 6, 7. Defines what the target
workflow produces. Reference pattern: {component_id} resolved via artifact
key OUTPUT_FORMAT_FILE.

**Binding Rule 5: artifact_contract**
Source: Phase 5. Consumed by: Phases 6, 8. Defines artifact keys and
filename patterns. Reference pattern: {component_id} resolved via artifact
key ARTIFACT_CONTRACT_FILE.

**Binding Rule 6: step_sequence**
Source: Phase 6. Consumed by: Phases 7, 8. Defines the target workflow
step design. Reference pattern: {component_id} resolved via artifact key
STEP_SEQUENCE_FILE.

**Binding Rule 7: runtime_standard**
Source: Phase 7. Consumed by: Phase 8. Consolidated composition standard
merging Phases 1-6. Reference pattern: {component_id} resolved via
artifact key RUNTIME_STANDARD_FILE.

**Binding Rule 8: operational_workflow**
Source: Phase 8. Consumed by: Phase 9. Concrete workflow implementation
design. Reference pattern: {component_id} resolved via artifact key
OPERATIONAL_WORKFLOW_FILE.

All 8 bindings are singleton. All 8 are required.

### 5.3 Override Mechanism

Overrides use a shallow merge strategy. Override values replace corresponding
base values at the property level. Nested objects are replaced entirely.
Properties not mentioned in the override remain at their base values.

**Non-overridable common properties:**
All 7 required common properties (component_id, component_type, name,
version, description, phase_origin, identity_locked) are non-overridable.
These are set by the pipeline itself.

**Override Rule 1: Identity fields ALWAYS come from the runtime spec.**
The target_identity and output_type in the domain_analysis binding are
always sourced from WORKFLOW_SPEC_FILE. Never derived or substituted.

```yaml
domain_analysis:
  overrides:
    target_identity:
      standard_name: "{from WORKFLOW_SPEC_FILE}"
      standard_version: "{from WORKFLOW_SPEC_FILE}"
      standard_filename: "{from WORKFLOW_SPEC_FILE}"
    output_type: "{from WORKFLOW_SPEC_FILE}"
```

**Override Rule 2: Base schema path resolved via context_extensions.**

```yaml
component_schema:
  overrides:
    base_schema_path: "{BASE_COMPOSITION_STANDARD}"
```

**Override Rule 3: Meta-test-criteria injected into all subsequent gatekeep prompts.**
The meta_test_criteria from domain_analysis are injected into ALL subsequent
phases' gatekeep prompts (Phases 2-8) as cross-phase invariants.

```yaml
meta_test_criteria_injection:
  source_binding: "domain_analysis"
  source_property: "meta_test_criteria"
  target_phases: [2, 3, 4, 5, 6, 7, 8]
  target: "gatekeep prompts"
```

### 5.4 Placeholder Resolution

Exactly 7 placeholders are defined. All 7 are required.

| # | Placeholder | Data Source | Required | Description |
|---|-------------|-------------|----------|-------------|
| 1 | {WORKFLOW_SPEC_FILE} | Input Spec | Yes | Runtime spec file path |
| 2 | {BASE_COMPOSITION_STANDARD} | Governance | Yes | Base component schema file path |
| 3 | {standard_name} | Input Spec | Yes | From spec identity section |
| 4 | {standard_version} | Input Spec | Yes | From spec identity section |
| 5 | {standard_filename} | Input Spec | Yes | From spec identity section |
| 6 | {output_type} | Input Spec | Yes | From spec output delivery section |
| 7 | {workflow_name} | Input Spec | Yes | From spec identity section |

**Resolution order:**
1. Identity placeholders first: {workflow_name}, {standard_name},
   {standard_version}, {standard_filename}.
2. Configuration placeholders second: {output_type}.
3. File path placeholders third: {WORKFLOW_SPEC_FILE} and
   {BASE_COMPOSITION_STANDARD}.

If a placeholder cannot be resolved, the pipeline halts with an explicit
error identifying the unresolved placeholder and its expected data source.

### 5.5 Meta-Test-Criteria Binding

Phase 1's meta_test_criteria are a special binding that propagates across
the entire pipeline. The meta_test_criteria must contain at minimum 4
invariants:

1. **Identity invariant:** Generated workflow uses spec identity, not builder
   identity. The workflow_name, standard_name, standard_version, and
   standard_filename must all come from the runtime spec.

2. **Structure invariant:** Generated workflow structure matches spec domain,
   not the builder's structure. The component types and phase structure are
   derived from the target domain, not copied from the builder.

3. **Output delivery invariant:** Output delivery mechanism matches the spec
   declared output type. If the spec says documented_versioned, the pipeline
   includes review/approve/archive. If direct, it does not.

4. **Derivation invariant:** All component types are derived from base schema
   fine-tuning, not hardcoded. The component_schema binding records the
   keep/add/drop/specialize decisions with rationale.

Every gatekeeper (Phases 2-8) checks both the phase-specific test criteria
AND the meta-test-criteria from domain_analysis.

---

## 6. Output Format

### 6.1 Output Structure

The resolved output is a complete executable workflow package organized into
a 3-part directory structure.

#### Part 1: Standards Directory

**Location:** Standards/

| File | Source Phase | Description |
|------|-------------|-------------|
| {standard_filename} | Phase 7 + Phase 9 | Target's composition standard. Filename from spec identity. Contains consolidated domain analysis, component schema, composition format, output format, artifact contract, and step sequence. |

#### Part 2: Specs Directory

**Location:** Specs/

| File | Source Phase | Description |
|------|-------------|-------------|
| {builder_name}.md | Phase 9 | Content-identical copy of input WORKFLOW_SPEC_FILE. Enables recursive self-bootstrap. |

#### Part 3: Workflow Package

**Location:** Root of workflow package directory.

| File | Source Phase | Description |
|------|-------------|-------------|
| workflow.toml | Phase 8 + Phase 9 | Complete workflow definition with correct identity from target spec |
| context_extensions.py | Phase 8 + Phase 9 | Domain-specific artifact keys and path resolution |
| actions.py | Phase 8 + Phase 9 | Domain-specific @action implementations |
| prompts/*.txt | Phase 8 + Phase 9 | One prompt file per prompt-driven step |
| README.md | Phase 9 | Describes the target workflow (not the builder) |

**Conditional files (output_type == documented_versioned):**

| File | Condition | Description |
|------|-----------|-------------|
| review_prompts/ | output_type == documented_versioned | Review and refine prompt templates |
| approval_config.toml | output_type == documented_versioned | Configuration for human approval gates |

**Total output artifacts:** 7 required plus conditional files based on
output_type.

### 6.2 Resolution Rules

Exactly 5 resolution rules govern the transformation from abstract
composition to physical deliverable.

**RR-001: All phase outputs consolidated.** Phase 7 consolidates Phases 1-6
into the runtime standard. The consolidated standard merges all design
decisions, binding rules, and quality requirements into a single coherent
reference.

**RR-002: Identity resolved.** All identity fields come from the runtime
spec, not the builder. The workflow_name, standard_name, standard_version,
and standard_filename in all output files match the target spec identity.

**RR-003: Placeholders resolved.** All {placeholders} are filled from spec
and context before output materialization. All 7 placeholders must be
resolved. No unresolved placeholders may remain.

**RR-004: Self-contained.** The workflow package is fully executable without
reference to the builder. The package contains all necessary files:
workflow.toml, context_extensions.py, actions.py, prompts/, README.md,
Standards/, and Specs/.

**RR-005: Self-bootstrapping.** The builder's own spec is embedded in Specs/
for the recursive chain. Phase 9 copies WORKFLOW_SPEC_FILE to
Specs/{builder_name}.md in the output package.

### 6.3 Quality Requirements

Exactly 12 quality requirements govern the output.

**QR-001: Identity Correctness.** workflow.toml name matches spec's
workflow_name. Verification: parse workflow.toml and compare name field to
spec's workflow_name.

**QR-002: No Builder Leakage.** No reference to "ar_meta_builder_v2" or
"AMB_STANDARD" appears in generated output in contexts where the target's
identity should appear. Verification: grep all output files for builder
identity values.

**QR-003: Standard Filename Match.** The standard file is placed at
Standards/{standard_filename} where standard_filename comes from the spec
identity. Verification: check Standards/ directory contents.

**QR-004: Artifact Key Uniqueness.** All artifact keys are unique and
conflict-free with the global registry. Verification: compare all artifact
keys against the global registry.

**QR-005: Prompt File Existence.** All prompt files exist for prompt-driven
steps. Verification: check prompts/ directory for one .txt file per
prompt-type step.

**QR-006: Python Syntax Valid.** Python syntax is valid in
context_extensions.py and actions.py. Verification: ast.parse() succeeds
on both files.

**QR-007: TOML Parse Valid.** TOML parse is valid in workflow.toml.
Verification: TOML parser succeeds without errors.

**QR-008: Class Name Derived.** Class name in context_extensions.py is
derived from workflow_name. Verification: check class name against
workflow_name convention.

**QR-009: Output Delivery Match.** Output delivery mechanism matches spec's
output_type. Verification: check workflow.toml for review/refine/approve
steps when output_type is documented_versioned.

**QR-010: Meta-Test-Criteria Satisfied.** Meta-test-criteria are satisfied
across all generated artifacts. Verification: check identity, structure,
output delivery, and derivation invariants.

**QR-011: Self-Bootstrap Spec Present.** Self-bootstrap spec is present in
Specs/ directory. Verification: check Specs/ contains at least one .md file
with content matching WORKFLOW_SPEC_FILE.

**QR-012: Standards Directory Present.** Standards/ directory contains the
composition standard with correct filename. Verification: check
Standards/{standard_filename} exists and contains correct standard_name and
standard_version.

---

## 7. Operational Requirements

### 7.1 TDD as DNA -- Standardized Phase Pattern

TDD is NOT a separate phase. It is the operating principle embedded in every
phase (1-8). Each phase follows this standardized 5-step pattern:

```
1. generate_test_criteria_{phase}  -- Define what "correct" means for this phase
2. review_test_criteria_{phase}    -- Critic: do tests test the right thing?
   [on reject -> refine_test_criteria_{phase} -> re-review, max N]
3. generate_{phase}_artifact       -- Produce the phase deliverable
4. validate_{phase}_artifact       -- Deterministic: docs exist, parse, identity
5. gatekeep_{phase}_artifact       -- LLM: run test criteria, pass/fail
   [on fail -> refine_{phase}_artifact -> back to validate, max N]
```

**Three-tier quality gate per phase:**
- **Critic** (step 2): Reviews the TEST quality -- do these tests actually test the right thing?
- **Validate** (step 4): Deterministic checks -- docs exist, parse correctly, identity matches
- **Gatekeeper** (step 5): Runs validated test criteria against artifact -- pass/fail with evidence

### 7.2 Nine Phases

| Phase | Artifact | Validate Action | Key Test Criteria Focus |
|-------|----------|-----------------|------------------------|
| 1. Analyze Spec | Domain analysis + meta-test-criteria | validate_input_spec (pre-step) | Identity correctness, output type, meta-criteria coverage |
| 2. Domain Component Schema | Fine-tuned schema | validate_design_artifact(phase="component_schema") | Common properties retained, fine-tuning justified |
| 3. Composition Format | Binding rules | validate_design_artifact(phase="composition_format") | All types have bindings, overrides defined |
| 4. Output Format | Output structure | validate_design_artifact(phase="output_format") | Matches composition format, quality measurable |
| 5. Component Artifacts | Artifact contract | validate_design_artifact(phase="component_artifacts") | Key uniqueness, no global conflicts |
| 6. Domain Steps | Step sequence | validate_design_artifact(phase="domain_steps") | Routing valid, output delivery matches type |
| 7. Runtime Standard | Composition standard | validate_design_artifact(phase="runtime_standard") | All phases consolidated, identity correct |
| 8. Operational Workflow | Workflow design | validate_design_artifact(phase="operational_workflow") | Steps reference standard, prompts exist |
| 9. Package | Workflow package | validate_package | All files valid, identity consistent, self-bootstrap |

### 7.3 Validate Actions

Three validate action functions:

**validate_input_spec** (Phase 1 pre-step):
- Identity fields present: standard_name, standard_version, standard_filename
- Output type declared: documented_versioned or direct
- Domain overview section present
- At least one component or domain concept described
- On fail -> AWAITING_INTERVENTION

**validate_design_artifact** (Phases 2-8, parameterized by phase):
- Common: all expected files exist, parse correctly, identity matches spec
- Phase-specific: type-specific validation rules (VR-001 through VR-008)
- Artifact key conflict check (Phase 5): no collisions with global registry
- Review/approval design check (Phase 6): present if output_type = documented_versioned

**validate_package** (Phase 9):
- All files present (workflow.toml, context_extensions.py, actions.py, prompts/)
- TOML parse validity, Python syntax
- Identity consistency across all files
- Standards/ directory with correct filename
- Specs/ directory with embedded builder spec
- Prompt placeholder vs required_inputs consistency
- Bidirectional artifact consistency (prompt <-> workflow.toml)

### 7.4 Input Artifacts

| Artifact Key | Description | Required? |
|--------------|-------------|-----------|
| WORKFLOW_SPEC_FILE | Runtime specification (markdown with YAML frontmatter) | Yes |
| BASE_COMPOSITION_STANDARD | Base Component Schema file path (resolved by context_extensions) | Yes |

### 7.5 Output Artifacts

| Artifact Key | Description |
|--------------|-------------|
| DOMAIN_ANALYSIS_FILE | Phase 1 output: domain analysis + meta-test-criteria |
| DOMAIN_COMPONENT_SCHEMA_FILE | Phase 2 output: fine-tuned schema |
| COMPOSITION_FORMAT_FILE | Phase 3 output: binding rules |
| OUTPUT_FORMAT_FILE | Phase 4 output: output structure |
| ARTIFACT_CONTRACT_FILE | Phase 5 output: artifact keys |
| STEP_SEQUENCE_FILE | Phase 6 output: step design |
| RUNTIME_STANDARD_FILE | Phase 7 output: consolidated standard |
| OPERATIONAL_WORKFLOW_FILE | Phase 8 output: workflow design |
| WORKFLOW_PACKAGE_DIR_FILE | Phase 9 output: complete workflow package |
| STANDARDS_COMPOSITION_STANDARD_FILE | Target's composition standard |
| SPECS_BUILDER_SPEC_FILE | Embedded AMB v2 spec (self-bootstrap) |
| REVIEW_FILE_SUGGESTED | Quality review of generated package |
| TEST_CRITERIA_FILE | Test criteria (per phase, accumulated) |

### 7.6 Domain-Specific Requirements

**Identity locking:** All prompts must include forbidden content rules:
- Do NOT use ar_meta_builder_v2 as the workflow name
- Do NOT use AMB_STANDARD as the standard name
- Do NOT copy the builder's 9-phase structure
- Do NOT hardcode component types -- derive from spec via fine-tuning
- Do NOT assume output type -- check spec's declaration

**Base schema sync:** Prompts reference {BASE_COMPOSITION_STANDARD} (path
reference, not embedding). Validate action checks MIN_BASE_SCHEMA_VERSION = "2.0".

**Recursive self-bootstrap:** Phase 9 copies WORKFLOW_SPEC_FILE to
Specs/ar_meta_builder_v2.md in the output package.

**Meta-test-criteria propagation:** Phase 1's meta_test_criteria are injected
into ALL subsequent phases' gatekeep prompts via context_extensions.

---

End of Meta Composition Spec Document
