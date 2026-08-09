---
doc_type: "domain_analysis"
identity_locked: true
standard_name: "COMPOSITION_STANDARD"
standard_version: "v2.0.0"
standard_filename: "COMPOSITION_STANDARD.md"
output_type: "documented_versioned"
source_spec: "bootstrap.spec.md"
generated_at: "2026-08-09"
---

# Domain Analysis -- Composition Standard Workflow


## Target Identity

The following identity fields are extracted from the bootstrap specification
and represent the TARGET workflow's identity. These values propagate to all
subsequent phases and must never be replaced by builder identity tokens.

| Field              | Value                      | Source                  |
|--------------------|----------------------------|-------------------------|
| standard_name      | COMPOSITION_STANDARD       | spec frontmatter        |
| standard_version   | v2.0.0                     | spec frontmatter        |
| standard_filename  | COMPOSITION_STANDARD.md    | spec frontmatter        |

Identity isolation is absolute. The builder workflow name and builder standard
name must never appear in any generated output. All downstream artifacts
reference the target identity exclusively.

Builder identity tokens excluded from all output:
- Builder workflow name (forbidden in all artifacts)
- Builder standard name (forbidden in all artifacts)
- Builder job-specific identifiers (forbidden in all artifacts)


## Output Type

Declared output type from the specification: documented_versioned

This means the target workflow produces a versioned standard document
(COMPOSITION_STANDARD.md) as its primary deliverable. The standard document
contains all three architectural layers and serves as the authoritative
reference for the target domain. No direct-output shortcut applies.


## Natural Phases

The target domain's natural workflow phases, derived from the specification's
constraints and structural requirements. Each phase produces distinct artifacts
and follows the test-driven development pattern (generation, review,
validation, gatekeeping).

PHASE-01: Specification Analysis
  Purpose: Extract target identity, output type, domain description, component
           types, and composition requirements from the runtime specification.
  Input: Runtime specification file (markdown with YAML frontmatter).
  Output: Parsed identity, output type declaration, domain constraints.

PHASE-02: Component Schema Design
  Purpose: Define Layer 1 -- the component types, their common properties,
           type-specific properties, and validation rules.
  Input: Domain description and component requirements from Phase 1.
  Output: Component type registry, property schemas, validation rules.

PHASE-03: Composition Format Design
  Purpose: Define Layer 2 -- binding rules, placeholder definitions, override
           mechanisms, and ordering rules for how components compose.
  Input: Component schema from Phase 2.
  Output: Binding rule set, placeholder registry, ordering specification.

PHASE-04: Output Format Design
  Purpose: Define Layer 3 -- resolved output structure, resolution rules,
           and quality requirements for the final deliverables.
  Input: Composition format from Phase 3.
  Output: Resolution rule set, quality requirement set, output templates.

PHASE-05: Artifact Contract Definition
  Purpose: Define artifact keys, filename patterns, and registry constraints
           for the target workflow.
  Input: All prior phase outputs.
  Output: Artifact key registry, filename pattern catalog.

PHASE-06: Step Sequence Design
  Purpose: Define workflow steps, routing logic, artifact delivery flow,
           and refinement loops.
  Input: Artifact contract from Phase 5.
  Output: Step definitions, routing table, delivery manifest.

PHASE-07: Runtime Standard Consolidation
  Purpose: Consolidate all previous phases into a single runtime standard
           document (the target COMPOSITION_STANDARD.md).
  Input: Outputs from Phases 1 through 6.
  Output: Complete COMPOSITION_STANDARD.md with all three layers.

PHASE-08: Operational Package Assembly
  Purpose: Produce the executable workflow package -- TOML definition, prompt
           files, action implementations, and context extensions.
  Input: Runtime standard from Phase 7, step sequence from Phase 6.
  Output: Complete workflow package directory ready for execution.


## Component Inventory

The domain components identified from the specification. Each component maps
to a distinct deliverable type in the target workflow's output package.

CMP-001: workflow_definition
  Type: manifest
  Name: Workflow Definition
  Description: TOML-format workflow manifest declaring steps, artifacts,
               coder roles, and routing logic.
  Phase Origin: PHASE-08

CMP-002: context_extensions
  Type: python_module
  Name: Context Extensions
  Description: Python module implementing path resolution, artifact key
               mapping, and context injection for the target workflow.
  Phase Origin: PHASE-08

CMP-003: custom_actions
  Type: python_module
  Name: Custom Actions
  Description: Python action implementations for deterministic steps
               (validation, scanning, copying, publishing).
  Phase Origin: PHASE-08

CMP-004: prompt_templates
  Type: prompt_collection
  Name: Prompt Templates
  Description: One prompt template per generation and review step, with
               artifact references, self-validation, and forbidden content.
  Phase Origin: PHASE-08

CMP-005: documentation
  Type: readme
  Name: Documentation
  Description: Human-readable README describing the workflow package,
               its purpose, execution instructions, and artifact inventory.
  Phase Origin: PHASE-08

CMP-006: composition_standard
  Type: standard_document
  Name: Composition Standard
  Description: The primary versioned standard document containing all three
               architectural layers (components, composition, resolved output).
  Phase Origin: PHASE-07

CMP-007: embedded_specification
  Type: specification
  Name: Embedded Specification
  Description: The runtime specification embedded in the output package to
               enable recursive bootstrap capability.
  Phase Origin: PHASE-08


## Meta-Test-Criteria

Exactly four invariants that propagate from this domain analysis to all
subsequent phases. Each invariant is objectively verifiable.

INV-1: Identity Invariant
  The generated workflow uses the target identity exclusively. The target
  standard_name is COMPOSITION_STANDARD, the target standard_version is
  v2.0.0, and the target standard_filename is COMPOSITION_STANDARD.md.
  No builder identity token (builder workflow name, builder standard name,
  builder job identifiers) may appear in any generated artifact. Verification
  method: string search across all output files for forbidden tokens.

INV-2: Structure Invariant
  The generated structure matches the target domain's three-layer architecture.
  Layer 1 contains component definitions with common properties and type-
  specific extensions. Layer 2 contains the composition format with binding
  rules, placeholders, and ordering. Layer 3 contains the resolved output
  with resolution rules and quality requirements. Verification method:
  section presence check and cross-layer reference validation.

INV-3: Output Delivery Invariant
  The output delivery type matches the specification's declared type:
  documented_versioned. The target workflow produces COMPOSITION_STANDARD.md
  as a final deliverable containing all three layers. The standard document
  is versioned and self-contained. Verification method: file existence check
  and frontmatter content validation.

INV-4: Derivation Invariant
  All component types in the target domain are derived from the base schema
  through fine-tuning. The base schema defines exactly 7 common properties
  shared by every component type. Type-specific properties extend the base
  without modifying or omitting any common property. Validation rules
  reference only properties that exist in the schema. Verification method:
  property set comparison across all component types.


## Common Properties

The following 7 common properties are defined for every component type in
the target domain. This set is identical across all component types -- no
type may omit, rename, or alter a common property.

PROP-001: component_id
  Data Type: string
  Required: true
  Description: Unique identifier for the component within the target workflow.
               Format: uppercase alphanumeric with hyphens (e.g., CMP-001).
               Serves as the primary key for cross-referencing.

PROP-002: component_type
  Data Type: string
  Required: true
  Description: Classification of the component (e.g., manifest, python_module,
               prompt_collection, standard_document). Determines which
               type-specific properties apply.

PROP-003: name
  Data Type: string
  Required: true
  Description: Human-readable display name for the component. Used in
               documentation and user-facing interfaces.

PROP-004: version
  Data Type: string
  Required: true
  Description: Semantic version of the component (MAJOR.MINOR.PATCH format).
               Tracks component evolution independently of the standard version.

PROP-005: description
  Data Type: string
  Required: true
  Description: Purpose and role description explaining what the component
               does, why it exists, and how it fits into the workflow.

PROP-006: phase_origin
  Data Type: string
  Required: true
  Description: Identifier of the natural phase (PHASE-01 through PHASE-08)
               where this component is first defined or produced. Enables
               traceability from component to its origin phase.

PROP-007: identity_locked
  Data Type: boolean
  Required: true
  Description: When true, indicates this component belongs to the target
               domain and must not be modified to reference builder identity.
               Always set to true for all target domain components.


## Self-Validation

Verification that this domain analysis is internally consistent and correctly
extracted from the source specification.

SV-001: Target standard_name (COMPOSITION_STANDARD) differs from builder
        standard name. PASS -- the values are distinct strings.

SV-002: Target standard_version (v2.0.0) matches the semver format declared
        in the spec frontmatter. PASS -- matches exactly.

SV-003: Target standard_filename (COMPOSITION_STANDARD.md) ends with .md
        suffix and differs from any builder-owned filename. PASS.

SV-004: Output type (documented_versioned) is one of the two valid values
        (documented_versioned, direct). PASS -- exact match to spec.

SV-005: All 7 common properties are defined with name, data type, required
        flag, and description. PASS -- 7 properties enumerated.

SV-006: identity_locked property is defined and its description states it
        is always true for target domain components. PASS.

SV-007: All 4 meta-test-criteria (INV-1 through INV-4) are present and
        specific. PASS -- each has a verification method.

SV-008: No builder identity tokens appear in this document. PASS -- the
        builder workflow name and builder standard name are referenced only
        in the exclusion list, not as target values.

SV-009: Component inventory (7 components) is traceable to the spec Output
        section. PASS -- each component maps to a listed output type.

SV-010: Natural phases (8 phases) are traceable to the spec constraints
        (three-layer architecture, test-driven development, recursive
        capability, artifact tracking). PASS.
