---
workflow_name: "ar_meta_builder_v2"
standard_name: "AMB_STANDARD"
standard_version: "v2.0.0"
standard_filename: "COMPOSITION_STANDARD.md"
output_type: "documented_versioned"
---

# Composition System Specification: AR Meta Builder v2

> Save to `docs/repo/workflow_builder/specs/ar_meta_builder_v2.md`.
> The composition system builder reads this document and generates a complete
> workflow package that implements the AR Meta Builder v2.
>
> **Key principle:** Describe the three-layer architecture — what the
> building blocks are (Layer 1), how they snap together (Layer 2), and
> what the assembled deliverable looks like (Layer 3). The builder infers
> the operational workflow and generates the complete workflow package.
>
> **Companion documents:**
> - [COMPOSITION_SYSTEM_STANDARD.md](../current/COMPOSITION_SYSTEM_STANDARD.md) — the universal pattern (v2)
> - [AMB_V2_DESIGN.md](../AMB_V2_DESIGN.md) — full design document with rationale
> - [BUILDER_REQUIREMENTS.md](../current/BUILDER_REQUIREMENTS.md) — what the builder enforces

---

## 1. Domain Overview

**Domain name:** `ar_meta_builder_v2`
**Label:** AR Meta Builder v2
**Job prefix:** `AMB`
**Init step:** `validate_input_spec`
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
- **TDD as DNA** — every phase follows a standardized test-driven pattern
- **Identity locking** — the target spec's identity is locked at Phase 1 and propagated
- **Fine-tuning from base schema** — component types are derived, not hardcoded
- **Output type distinction** — documented/versioned vs direct delivery

### 1.2 Domain Context

**Input:** A runtime spec (markdown with YAML frontmatter) that declares:
- Workflow identity (standard_name, standard_version, standard_filename)
- Output delivery type (documented_versioned or direct)
- Domain overview and natural phases
- Component types and their properties
- Composition and output format requirements

**Output:** A complete executable workflow package:
- `workflow.toml` — workflow definition with correct identity
- `context_extensions.py` — domain-specific artifact keys and path resolution
- `actions.py` — domain-specific action implementations
- `prompts/` — one prompt file per prompt-driven step
- `README.md` — describing the target workflow
- `Standards/{standard_filename}` — the target's composition standard
- `Specs/{builder_name}.md` — embedded builder spec (self-bootstrap)

**Recursive chain:** AMB v2 output is structurally identical to its own package.
Each generated standard specializes its parent's standard:
```
Workflow Builder v4 → AMB v2 → [target workflow]
```

**Trigger:** User submits a runtime spec via operator console or CLI.

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

---

## 3. Output Delivery

```yaml
output_type: documented_versioned
approval_before_execution: false
archive_after_approval: true
```

The meta-builder produces workflow packages that need versioning, audit trail,
approval gates, and promotion. The full documented/versioned pipeline applies:
generate → review → refine → approve → promote → archive.

---

## 4. Component Schema (Layer 1)

The meta-builder domain has 8 component types — one per design phase (Phases 1-8).
Each component type represents a category of design artifact produced during the
pipeline. Phase 9 (Package) is the assembly of all components into the final output.

### 4.1 Component Types

| Component Type | Phase | Purpose | Required? | Cardinality |
|---|---|---|---|---|
| `domain_analysis` | 1 | Domain understanding, identity, output type, meta-test-criteria | Yes | Singleton |
| `component_schema` | 2 | Fine-tuned base schema for target domain | Yes | Singleton |
| `composition_format` | 3 | How domain components bind together | Yes | Singleton |
| `output_format` | 4 | What the target workflow produces | Yes | Singleton |
| `artifact_contract` | 5 | Artifact keys and filename patterns | Yes | Singleton |
| `step_sequence` | 6 | Target workflow's step design + delivery mechanism | Yes | Singleton |
| `runtime_standard` | 7 | Consolidated composition standard for target | Yes | Singleton |
| `operational_workflow` | 8 | Concrete workflow implementation design | Yes | Singleton |

### 4.2 Common Properties

All design artifacts share these properties:

| Property | Type | Required | Description |
|---|---|---|---|
| `component_id` | string | Yes | Unique identifier (format: `{phase}-{type}-{workflow_name}`) |
| `component_type` | enum | Yes | One of the 8 types in 4.1 |
| `name` | string | Yes | Human-readable display name |
| `version` | string | Yes | Semantic version (matches target spec's standard_version) |
| `description` | string | Yes | What this artifact contains and its role in the pipeline |
| `phase_origin` | integer | Yes | Which phase produced this artifact (1-8) |
| `identity_locked` | boolean | Yes | True if identity fields match target spec (not builder) |

### 4.3 Type-Specific Properties

#### Type: `domain_analysis`

| Property | Type | Required | Description |
|---|---|---|---|
| `target_identity` | object | Yes | standard_name, standard_version, standard_filename from spec |
| `output_type` | enum | Yes | documented_versioned or direct |
| `natural_phases` | array | Yes | Target domain's natural workflow phases |
| `component_inventory` | array | Yes | Identified domain components |
| `meta_test_criteria` | array | Yes | Cross-phase invariants for all gatekeepers |

#### Type: `component_schema`

| Property | Type | Required | Description |
|---|---|---|---|
| `base_schema_version` | string | Yes | Version of COMPOSITION_SYSTEM_STANDARD.md used |
| `fine_tuning_decisions` | array | Yes | Keep/add/drop/specialize decisions with rationale |
| `domain_types` | array | Yes | Component types defined for the target domain |
| `validation_rules` | array | Yes | Domain-specific validation rules |

#### Type: `composition_format`

| Property | Type | Required | Description |
|---|---|---|---|
| `binding_rules` | array | Yes | How domain components bind together |
| `override_mechanism` | object | Yes | Per-composition customization rules |
| `placeholder_resolution` | object | Yes | External data source mapping |
| `examples` | array | No | Sample compositions |

#### Type: `output_format`

| Property | Type | Required | Description |
|---|---|---|---|
| `output_sections` | array | Yes | Structure of the target's output |
| `resolution_rules` | array | Yes | How references are expanded |
| `quality_requirements` | array | Yes | Measurable quality criteria |

#### Type: `artifact_contract`

| Property | Type | Required | Description |
|---|---|---|---|
| `artifact_keys` | array | Yes | Key → filename pattern → description mappings |
| `conflict_check_passed` | boolean | Yes | True if no conflicts with global registry |

#### Type: `step_sequence`

| Property | Type | Required | Description |
|---|---|---|---|
| `steps` | array | Yes | Step definitions (name, type, routing, role policy) |
| `review_loops` | array | No | Review/refine pairs (for documented/versioned type) |
| `approval_gates` | array | No | Steps requiring human approval |
| `delivery_mechanism` | object | Yes | How output is delivered (promote/archive or direct) |

#### Type: `runtime_standard`

| Property | Type | Required | Description |
|---|---|---|---|
| `standard_name` | string | Yes | From target spec identity |
| `standard_version` | string | Yes | From target spec identity |
| `consolidated_phases` | array | Yes | Phases 1-6 content consolidated |
| `cross_phase_consistency` | boolean | Yes | True if all phases are mutually consistent |

#### Type: `operational_workflow`

| Property | Type | Required | Description |
|---|---|---|---|
| `workflow_steps` | array | Yes | Concrete step sequence with routing |
| `prompt_files` | array | Yes | One per prompt-driven step |
| `action_implementations` | array | Yes | Python @action functions needed |
| `context_extensions` | object | Yes | Artifact keys and path resolution |

### 4.4 Validation Rules

All design artifacts must pass:

- **VR-001:** Required common fields present (component_id, component_type, name, version, description, phase_origin, identity_locked)
- **VR-002:** Valid component_type — must be one of the 8 types in 4.1
- **VR-003:** Unique component_id — no duplicates across the pipeline
- **VR-004:** Type-specific schema conformance — all required properties for the declared type present
- **VR-005:** identity_locked = true for all artifacts (identity matches target spec, not builder)
- **VR-006:** phase_origin matches the artifact's position in the pipeline
- **VR-007:** base_schema_version >= "2.0" (for component_schema type)
- **VR-008:** conflict_check_passed = true (for artifact_contract type)

---

## 5. Composition Format (Layer 2)

### 5.1 Composition Structure

The meta-builder's composition is the **pipeline dependency chain** — each
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

| Binding | Source Phase | Consumed By | Required? | Description |
|---|---|---|---|---|
| `domain_analysis` | Phase 1 | Phases 2-8 (via meta-test-criteria) | Yes | Identity, output type, natural phases |
| `component_schema` | Phase 2 | Phases 3, 7 | Yes | Fine-tuned schema for target domain |
| `composition_format` | Phase 3 | Phases 4, 7 | Yes | Binding rules for domain components |
| `output_format` | Phase 4 | Phases 6, 7 | Yes | Output structure and quality requirements |
| `artifact_contract` | Phase 5 | Phases 6, 8 | Yes | Artifact keys for target workflow |
| `step_sequence` | Phase 6 | Phases 7, 8 | Yes | Target workflow's step design |
| `runtime_standard` | Phase 7 | Phase 8 | Yes | Consolidated standard for implementation |
| `operational_workflow` | Phase 8 | Phase 9 | Yes | Concrete workflow implementation |

### 5.3 Override Mechanism

Overrides are used to inject spec-specific values into pipeline bindings:

```yaml
domain_analysis:
  overrides:
    target_identity: "{from WORKFLOW_SPEC_FILE}"  # Identity from spec, not builder
    output_type: "{from WORKFLOW_SPEC_FILE}"       # Output type from spec

component_schema:
  overrides:
    base_schema_path: "{BASE_COMPOSITION_STANDARD}"  # Path to base schema
```

**Override rules:**
- Identity fields ALWAYS come from the runtime spec — never derived or substituted
- Base schema path resolved at runtime via context_extensions
- Meta-test-criteria from domain_analysis injected into ALL subsequent gatekeep prompts

### 5.4 Placeholder Resolution

| Placeholder | Data Source | Required? |
|---|---|---|
| `{WORKFLOW_SPEC_FILE}` | Runtime spec file path | Yes |
| `{BASE_COMPOSITION_STANDARD}` | Base Component Schema file path | Yes |
| `{standard_name}` | From spec's identity section | Yes |
| `{standard_version}` | From spec's identity section | Yes |
| `{standard_filename}` | From spec's identity section | Yes |
| `{output_type}` | From spec's output delivery section | Yes |
| `{workflow_name}` | From spec's identity section | Yes |

### 5.5 Meta-Test-Criteria Binding

Phase 1's `meta_test_criteria` is a special binding — it's injected into ALL
subsequent phases' gatekeep prompts as cross-phase invariants:

```
meta_test_criteria:
  - "Generated workflow uses spec's identity, not builder's identity"
  - "Generated workflow structure matches spec's domain, not AMB's structure"
  - "Output delivery mechanism matches spec's declared output type"
  - "All component types derived from base schema fine-tuning, not hardcoded"
```

Every gatekeeper (Phases 2-8) checks both the phase-specific test criteria AND
these meta-test-criteria.

---

## 6. Output Format (Layer 3)

### 6.1 Output Structure

The resolved output is a complete executable workflow package:

| Output | Source Phase | Description |
|---|---|---|
| `workflow.toml` | Phase 8 + 9 | Complete workflow definition with correct identity |
| `context_extensions.py` | Phase 8 + 9 | Domain-specific class, artifact keys, path resolution |
| `actions.py` | Phase 8 + 9 | Domain-specific @action implementations |
| `prompts/*.txt` | Phase 8 + 9 | One prompt file per prompt-driven step |
| `README.md` | Phase 9 | Describes the target workflow (not the builder) |
| `Standards/{standard_filename}` | Phase 7 + 9 | Target's composition standard |
| `Specs/{builder_name}.md` | Phase 9 | Embedded AMB v2 spec (self-bootstrap) |

### 6.2 Resolution Rules

- **All phase outputs consolidated:** Phase 7 consolidates Phases 1-6 into the runtime standard
- **Identity resolved:** All identity fields come from the runtime spec, not the builder
- **Placeholders resolved:** All `{placeholders}` filled from spec and context
- **Self-contained:** The workflow package is fully executable without reference to the builder
- **Self-bootstrapping:** The builder's own spec is embedded in `Specs/` for recursive chain

### 6.3 Quality Requirements

- **QR-001:** Identity correctness — workflow.toml name matches spec's workflow_name
- **QR-002:** No builder leakage — no reference to `ar_meta_builder_v2` or `AMB_STANDARD` in output
- **QR-003:** Standard filename matches spec's standard_filename
- **QR-004:** All artifact keys unique and conflict-free with global registry
- **QR-005:** All prompt files exist for prompt-driven steps
- **QR-006:** Python syntax valid in context_extensions.py and actions.py
- **QR-007:** TOML parse valid in workflow.toml
- **QR-008:** Class name in context_extensions.py derived from workflow_name
- **QR-009:** Output delivery mechanism matches spec's output_type
- **QR-010:** Meta-test-criteria satisfied across all generated artifacts
- **QR-011:** Self-bootstrap spec present in Specs/ directory
- **QR-012:** Standards/ directory contains the composition standard with correct filename

---

## 7. Operational Requirements

### 7.1 TDD as DNA — Standardized Phase Pattern

TDD is NOT a separate phase. It is the operating principle embedded in every
phase (1-8). Each phase follows this standardized 5-step pattern:

```
1. generate_test_criteria_{phase}  — Define what "correct" means for this phase
2. review_test_criteria_{phase}    — Critic: do tests test the right thing?
   [on reject → refine_test_criteria_{phase} → re-review, max N]
3. generate_{phase}_artifact       — Produce the phase deliverable
4. validate_{phase}_artifact       — Deterministic: docs exist, parse, identity
5. gatekeep_{phase}_artifact       — LLM: run test criteria, pass/fail
   [on fail → refine_{phase}_artifact → back to validate, max N]
```

**Three-tier quality gate per phase:**
- **Critic** (step 2): Reviews the TEST quality — do these tests actually test the right thing?
- **Validate** (step 4): Deterministic checks — docs exist, parse correctly, identity matches
- **Gatekeeper** (step 5): Runs validated test criteria against artifact — pass/fail with evidence

### 7.2 Nine Phases

| Phase | Artifact | Validate Action | Key Test Criteria Focus |
|---|---|---|---|
| 1. Analyze Spec | Domain analysis + meta-test-criteria | `validate_input_spec` (pre-step) | Identity correctness, output type, meta-criteria coverage |
| 2. Domain Component Schema | Fine-tuned schema | `validate_design_artifact(phase="component_schema")` | Common properties retained, fine-tuning justified |
| 3. Composition Format | Binding rules | `validate_design_artifact(phase="composition_format")` | All types have bindings, overrides defined |
| 4. Output Format | Output structure | `validate_design_artifact(phase="output_format")` | Matches composition format, quality measurable |
| 5. Component Artifacts | Artifact contract | `validate_design_artifact(phase="component_artifacts")` | Key uniqueness, no global conflicts |
| 6. Domain Steps | Step sequence | `validate_design_artifact(phase="domain_steps")` | Routing valid, output delivery matches type |
| 7. Runtime Standard | Composition standard | `validate_design_artifact(phase="runtime_standard")` | All phases consolidated, identity correct |
| 8. Operational Workflow | Workflow design | `validate_design_artifact(phase="operational_workflow")` | Steps reference standard, prompts exist |
| 9. Package | Workflow package | `validate_package` | All files valid, identity consistent, self-bootstrap |

### 7.3 Validate Actions

Three validate action functions:

**`validate_input_spec`** (Phase 1 pre-step):
- Identity fields present: standard_name, standard_version, standard_filename
- Output type declared: documented_versioned or direct
- Domain overview section present
- At least one component or domain concept described
- On fail → AWAITING_INTERVENTION

**`validate_design_artifact`** (Phases 2-8, parameterized by `phase`):
- Common: all expected files exist, parse correctly, identity matches spec
- Phase-specific: type-specific validation rules (VR-001 through VR-008)
- Artifact key conflict check (Phase 5): no collisions with global registry
- Review/approval design check (Phase 6): present if output_type = documented_versioned

**`validate_package`** (Phase 9):
- All files present (workflow.toml, context_extensions.py, actions.py, prompts/)
- TOML parse validity, Python syntax
- Identity consistency across all files
- Standards/ directory with correct filename
- Specs/ directory with embedded builder spec
- Prompt placeholder vs required_inputs consistency
- Bidirectional artifact consistency (prompt ↔ workflow.toml)

### 7.4 Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `WORKFLOW_SPEC_FILE` | Runtime specification (markdown with YAML frontmatter) | Yes |
| `BASE_COMPOSITION_STANDARD` | Base Component Schema file path | Yes (resolved by context_extensions) |

### 7.5 Output Artifacts

| Artifact Key | Description |
|---|---|
| `DOMAIN_ANALYSIS_FILE` | Phase 1 output: domain analysis + meta-test-criteria |
| `DOMAIN_COMPONENT_SCHEMA_FILE` | Phase 2 output: fine-tuned schema |
| `COMPOSITION_FORMAT_FILE` | Phase 3 output: binding rules |
| `OUTPUT_FORMAT_FILE` | Phase 4 output: output structure |
| `ARTIFACT_CONTRACT_FILE` | Phase 5 output: artifact keys |
| `STEP_SEQUENCE_FILE` | Phase 6 output: step design |
| `RUNTIME_STANDARD_FILE` | Phase 7 output: consolidated standard |
| `OPERATIONAL_WORKFLOW_FILE` | Phase 8 output: workflow design |
| `WORKFLOW_PACKAGE_DIR_FILE` | Phase 9 output: complete workflow package |
| `STANDARDS_COMPOSITION_STANDARD_FILE` | Target's composition standard |
| `SPECS_BUILDER_SPEC_FILE` | Embedded AMB v2 spec (self-bootstrap) |
| `REVIEW_FILE_SUGGESTED` | Quality review of generated package |
| `TEST_CRITERIA_FILE` | Test criteria (per phase, accumulated) |

### 7.6 Domain-Specific Requirements

**Identity locking:** All prompts must include forbidden content rules:
- Do NOT use `ar_meta_builder_v2` as the workflow name
- Do NOT use `AMB_STANDARD` as the standard name
- Do NOT copy the builder's 9-phase structure
- Do NOT hardcode component types — derive from spec via fine-tuning
- Do NOT assume output type — check spec's declaration

**Base schema sync:** Prompts reference `{BASE_COMPOSITION_STANDARD}` (path
reference, not embedding). Validate action checks MIN_BASE_SCHEMA_VERSION = "2.0".

**Recursive self-bootstrap:** Phase 9 copies `WORKFLOW_SPEC_FILE` to
`Specs/ar_meta_builder_v2.md` in the output package.

**Meta-test-criteria propagation:** Phase 1's meta-test-criteria are injected
into ALL subsequent phases' gatekeep prompts via context_extensions.

---

## 8. References

- **AMB v2 Design Document:** `docs/repo/workflow_builder/AMB_V2_DESIGN.md`
- **Base Component Schema (v2):** `docs/repo/workflow_builder/current/COMPOSITION_SYSTEM_STANDARD.md`
- **AMB v1 job review (lessons learned):** `~/.ukbe-runner/jobs/20260809/ar_meta_builder_v1/AMB-ai99miop/`
- **Workflow Builder v4 (parent builder):** `docs/repo/workflow_builder/V4_BOOTSTRAP_SUMMARY.md`
- **Builder Requirements:** `docs/repo/workflow_builder/current/BUILDER_REQUIREMENTS.md`
- **Plugin Workflow System:** `docs/repo/workflow_builder/current/PLUGIN_WORKFLOW_SYSTEM.md`

---

**End of Specification**
