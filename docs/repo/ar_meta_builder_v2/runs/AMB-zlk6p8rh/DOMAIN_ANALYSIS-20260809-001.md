---
doc_type: "domain_analysis"
template_id: "domain_analysis"
identity_locked: true
source_spec: "bootstrap.spec.md"
job_id: "AMB-zlk6p8rh"
generated_at: "2026-08-09"
---

# Domain Analysis

## Target Identity

The following identity values are extracted character-for-character from the runtime specification YAML frontmatter. These define the TARGET workflow identity that must propagate to all downstream artifacts. The identity is locked: no downstream phase may override, reinterpret, or substitute these values.

| Field | Value |
|---|---|
| workflow_name | ar_meta_builder_v2 |
| standard_name | AMB_STANDARD |
| standard_version | v2.0.0 |
| standard_filename | COMPOSITION_STANDARD.md |
| output_type | documented_versioned |

Source: bootstrap.spec.md, lines 2-6 (YAML frontmatter).

Self-validation:
- standard_name matches spec frontmatter exactly: YES (AMB_STANDARD)
- standard_version matches spec frontmatter exactly: YES (v2.0.0)
- standard_filename matches spec frontmatter exactly and ends with .md: YES (COMPOSITION_STANDARD.md)
- workflow_name matches spec frontmatter exactly: YES (ar_meta_builder_v2)
- output_type matches spec frontmatter exactly: YES (documented_versioned)
- identity_locked is set to true: YES

## Output Type

Declared output type: documented_versioned

Implications:
- The target standard document (COMPOSITION_STANDARD.md) must be included as a final deliverable in the generated workflow package.
- The standard document contains all 3 layers (component schema, composition format, resolved output).
- The step sequence must include review steps, refine steps, approval gates, and promotion/archival steps.
- The workflow package output directory follows the naming pattern: {base_workflow_name}_{codename}

## Natural Phases

The target domain (meta-workflow composition) naturally decomposes into the following phases. These phases describe the TARGET workflow's operational structure -- not the builder's internal pipeline.

| Phase | Name | Purpose |
|---|---|---|
| 1 | Analyze Spec | Extract identity, output type, domain description, component types, and composition requirements from the runtime specification. |
| 2 | Component Schema | Define Layer 1 -- component types, their common and type-specific properties, and validation rules. |
| 3 | Composition Format | Define Layer 2 -- binding rules, override mechanism, placeholders, and ordering rules. |
| 4 | Output Format | Define Layer 3 -- 3-part output structure, resolution rules, and quality requirements. |
| 5 | Artifact Contract | Define artifact keys, filename patterns, and registry constraints for the target workflow. |
| 6 | Step Sequence | Define workflow steps, routing logic, and artifact delivery flow. |
| 7 | Runtime Standard | Consolidate all design phases into the target composition standard document. |
| 8 | Operational Workflow | Produce the executable workflow package -- TOML, prompts, actions, context extensions. |

Each phase follows the test-driven pattern: generation step, review step, validation step, gatekeeping step.

## Component Inventory

The following component types are identified from the spec domain description. Each component type maps to a distinct layer or artifact in the target workflow output.

| Component Type | Description |
|---|---|
| domain_analysis | Phase 1 output. Contains target identity, output type, natural phases, component inventory, and meta-test-criteria. |
| component_schema | Phase 2 output. Defines Layer 1 -- all component types, common properties, type-specific properties, and validation rules. |
| composition_format | Phase 3 output. Defines Layer 2 -- binding rules, override mechanism, placeholders, and ordering rules. |
| output_format | Phase 4 output. Defines Layer 3 -- 3-part output structure, resolution rules, and quality requirements. |
| artifact_contract | Phase 5 output. Defines artifact keys, filename patterns, and registry constraints. |
| step_sequence | Phase 6 output. Defines workflow steps, routing, and artifact delivery flow. |
| runtime_standard | Phase 7 output. Consolidated composition standard document containing all layers. |
| operational_workflow | Phase 8 output. Executable workflow package -- TOML manifest, prompts, actions, context extensions. |

All component types are derived from the spec's description of the target workflow's purpose, constraints, and success criteria.

## Meta-Test-Criteria

The following 4 invariants are established in this phase and are IMMUTABLE across all subsequent phases. They must be injected into ALL gatekeep prompts (Phases 2-8).

### INV-1: Identity Isolation

The generated workflow uses the spec identity exclusively. The builder identity tokens (workflow_name, standard_name, standard_version) of any upstream builder must never appear in generated output as the target identity. All identity fields in the target workflow come from the runtime spec frontmatter.

Builder tokens that must be excluded from all downstream artifacts:
- Builder workflow_name must not appear as the target workflow_name
- Builder standard_name must not appear as the target standard_name
- Builder standard_version must not appear as the target standard_version

### INV-2: Three-Layer Architecture

Layer 1 (component definitions), Layer 2 (composition format), and Layer 3 (resolved outputs) must each be present and distinct in the generated target workflow. Every generated artifact must be traceable to exactly one layer. The 3-part output structure must appear in the final standard document regardless of output type.

### INV-3: Test-Driven Development

Each subsequent phase must include the following step types:
- Generation step (creates the artifact)
- Review step (LLM validates quality)
- Validation step (deterministic checks)
- Gatekeeping step (final approval)

This structural requirement ensures every artifact passes through multiple quality gates before promotion.

### INV-4: Recursive Capability

The generated workflow must accept its own output type as valid input for self-bootstrapping. Given its own output spec as input, it must produce a functionally equivalent workflow package with a new codename. The output goes to a new folder, never overwriting the source workflow. The builder's own spec must be embedded in Specs/ for recursive chain self-bootstrapping.

## Common Properties

All components in the target workflow must include exactly these 7 common properties. This set is consistent across every component type -- no component may omit or rename a common property.

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| component_id | string | true | Unique identifier for this component instance within the pipeline. |
| component_type | string | true | The type identifier matching one of the declared component types in the schema. |
| name | string | true | Human-readable display name for the component. |
| version | string | true | Semantic version of this component artifact. |
| description | string | true | Human-readable description of the component's purpose and content. |
| phase_origin | string | true | The pipeline phase number that produced this component (e.g., "1", "2", ... "8"). |
| identity_locked | boolean | true | Must be true for all artifacts. Declares that identity fields match the target spec, not any builder. |

## Self-Validation Summary

| Check | Result |
|---|---|
| standard_name matches spec frontmatter | PASS -- AMB_STANDARD |
| standard_version matches spec frontmatter | PASS -- v2.0.0 |
| standard_filename matches spec and ends with .md | PASS -- COMPOSITION_STANDARD.md |
| workflow_name matches spec frontmatter | PASS -- ar_meta_builder_v2 |
| output_type matches spec frontmatter | PASS -- documented_versioned |
| identity_locked declared true | PASS |
| 4 meta-test-criteria present | PASS -- INV-1 through INV-4 |
| 7 common properties defined | PASS |
| Natural phases traceable to spec | PASS -- 8 phases matching spec structure |
| Component inventory traceable to spec | PASS -- 8 component types |
| No builder identity leakage in target_identity | PASS -- values match spec frontmatter only |
