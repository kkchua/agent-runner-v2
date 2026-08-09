---
doc_type: "component_schema"
identity_locked: true
template_id: "component_schema"
source_spec: "bootstrap.spec.md"
job_id: "AMB-zlk6p8rh"
generated_at: "2026-08-09"
base_schema_version: "1.0.0"
---

# Domain Component Schema

## Scope

This document defines the Layer 1 component schema for the target workflow domain (meta-workflow composition). It specifies the component types, their common properties, type-specific properties, validation rules, and fine-tuning decisions relative to the base schema.

The base schema conventions referenced here are defined in METADATA_STANDARD.md (Layer 1) and METADATA_CONTRACT.md (Layer 2). This document specializes those conventions for the meta-workflow composition domain.

Source: bootstrap.spec.md (runtime specification, Phase 2 deliverable).
Upstream inputs: DOMAIN_ANALYSIS-20260809-001.md (Phase 1), TEST_CRITERIA-20260809-001.md (acceptance criteria).

---

## Component Type Summary

The following 8 component types are derived from the target domain description in the runtime specification. Each type corresponds to a distinct deliverable in the target workflow pipeline.

| Type Identifier | Phase | Purpose | Required | Cardinality |
|---|---|---|---|---|
| domain_analysis | 1 | Extracts target identity, output type, natural phases, component inventory, and meta-test-criteria from the runtime specification. | true | 1 |
| component_schema | 2 | Defines Layer 1 -- component types, common and type-specific properties, and validation rules that govern all downstream components. | true | 1 |
| composition_format | 3 | Defines Layer 2 -- binding rules, override mechanism, placeholders, and ordering rules for component composition. | true | 1 |
| output_format | 4 | Defines Layer 3 -- 3-part output structure, resolution rules (RR-001 through RR-005), and quality requirements (QR-001 through QR-012). | true | 1 |
| artifact_contract | 5 | Declares artifact keys, filename patterns, and registry constraints for the target workflow. | true | 1 |
| step_sequence | 6 | Defines workflow steps, routing logic, and artifact delivery flow through the target pipeline. | true | 1 |
| runtime_standard | 7 | Consolidates all design phases (1 through 6) into a single composition standard document. | true | 1 |
| operational_workflow | 8 | Produces the executable workflow package -- TOML manifest, prompt files, action modules, and context extensions. | true | 1 |

Notes:
- All 8 types are required (cardinality 1 each) for a complete pipeline execution.
- Type identifiers are derived from the spec domain, not from any builder domain.
- Each type maps to exactly one design phase (Phase 1 through Phase 8).
- Traceability: each type description traces to a section in bootstrap.spec.md (Purpose, Output, Constraints, Success Criteria).

---

## Common Properties

All 8 component types share the following 7 required common properties. This set is consistent across every type -- no component may omit or rename a common property.

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| component_id | string | true | Unique identifier for this component instance within the pipeline. Format: {TYPE_PREFIX}-{PHASE}-{SEQ} (e.g., DA-1-001). |
| component_type | string | true | The type identifier matching one of the 8 declared types in this schema. |
| name | string | true | Human-readable display name for the component (e.g., "Domain Analysis", "Component Schema"). |
| version | string | true | Semantic version of this component artifact (e.g., "1.0.0"). |
| description | string | true | Human-readable description of the component purpose and content scope. |
| phase_origin | string | true | The pipeline phase number that produced this component ("1" through "8"). |
| identity_locked | boolean | true | Must be true for all artifacts. Declares that identity fields match the target spec, not any upstream builder. |

Data type constraints:
- string: Non-empty text value. No restrictions on length beyond practical limits.
- boolean: Must be exactly true or false.
- integer: Whole number.
- list: Ordered collection of values.
- object: Structured key-value map.

Optional common properties (shared across types, not required):

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| phase_position | integer | false | Zero-based step position within the originating phase. Default: 0. |
| depends_on | list | false | List of component_id values that this component depends on. Default: empty list. |

---

## Type-Specific Properties

### domain_analysis

Required type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| target_identity | object | true | Identity object extracted from the runtime spec YAML frontmatter. Contains standard_name, standard_version, standard_filename, workflow_name, and output_type. |
| output_type | string | true | Delivery type declared in the spec: "documented_versioned" or "direct". |
| natural_phases | list | true | List of phase entries (name, purpose) extracted from the spec domain overview. |
| component_inventory | list | true | List of component type entries (type_name, description) identified from the spec. |
| meta_test_criteria | list | true | List of exactly 4 invariant entries (INV-1 through INV-4) with id and description. |

Optional type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| input_spec_source | string | false | Filename of the source runtime specification. Default: "bootstrap.spec.md". |

Validation constraints:
- target_identity must contain all 5 identity fields (standard_name, standard_version, standard_filename, workflow_name, output_type).
- meta_test_criteria must contain exactly 4 entries.
- output_type must be "documented_versioned" or "direct".

### component_schema

Required type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| component_types | list | true | List of all component type declarations with type_id, phase, purpose, required, and cardinality. |
| common_properties | list | true | The 7 common property definitions (name, data_type, required, description). |
| validation_rules | list | true | Ordered list of VR-NNN rule definitions (id, applies_to, check, error_message). |
| fine_tuning_decisions | list | true | List of keep/add/drop/specialize decisions with rationale. |
| base_schema_version | string | true | Version of the base schema being specialized (e.g., "1.0.0"). |

Optional type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| schema_compliance_level | string | false | Compliance level declaration: "full" or "partial". Default: "full". |

Validation constraints:
- validation_rules must contain at least 8 entries (VR-001 through VR-008).
- common_properties must contain exactly 7 entries.
- base_schema_version must follow semantic versioning format (MAJOR.MINOR.PATCH).

### composition_format

Required type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| binding_rules | list | true | List of binding rules, one per component type. Each specifies references, cardinality, required flag, and phase mapping. |
| override_mechanism | object | true | Override syntax, precedence rules, identity override guarantee, and usage example. |
| placeholders | list | true | List of exactly 7 placeholder definitions (name, resolution_source, data_source, required). |
| ordering_rules | list | true | List of ordering constraints ensuring deterministic, acyclic component resolution. |

Optional type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| override_example_count | integer | false | Minimum number of override usage examples. Default: 1. |

Validation constraints:
- binding_rules count must match the number of declared component_types.
- placeholders must contain exactly 7 entries.
- override_mechanism must include identity_field_override set to "from_spec".

### output_format

Required type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| output_parts | list | true | List of exactly 3 output parts (layer, content_description, section_heading). |
| resolution_rules | list | true | List of RR-NNN resolution rule definitions (id, resolves, transformation, output_format). |
| quality_requirements | list | true | List of QR-NNN quality requirement definitions (id, condition, verification_method). |
| output_type | string | true | Delivery type: "documented_versioned" or "direct". Must match the spec declaration. |

Optional type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| standard_included | boolean | false | Whether the standard document is included in the output package. Default: true for documented_versioned, false for direct. |

Validation constraints:
- output_parts must contain exactly 3 entries (Layer 1, Layer 2, Layer 3).
- resolution_rules must contain at least 5 entries (RR-001 through RR-005).
- quality_requirements must contain at least 12 entries (QR-001 through QR-012).
- output_type must match the output_type from the domain_analysis.

### artifact_contract

Required type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| artifact_keys | list | true | List of artifact key declarations. Each key is unique, uppercase with underscores, ending in _FILE for file artifacts. |
| filename_patterns | list | true | List of filename pattern definitions mapping each artifact key to its output pattern. |
| conflict_check_passed | boolean | true | Must be true, confirming no collisions with the global artifact registry. |

Optional type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| total_artifact_count | integer | false | Total number of declared artifact keys. Default: computed from artifact_keys list length. |

Validation constraints:
- All artifact keys must be unique within the workflow.
- Artifact keys must follow uppercase-with-underscores naming convention.
- File artifact keys must end with _FILE suffix.
- filename_patterns must use forward slashes for directory separators.
- conflict_check_passed must be true.

### step_sequence

Required type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| steps | list | true | Ordered list of step definitions. Each step has step_id, step_type (prompt or action), role_policy, and required_inputs. |
| routing_rules | list | true | List of routing rules per step. Each specifies onsuccess target and optional on_reject_refine target with max_iterations. |
| delivery_mechanism | object | true | Delivery configuration matching the spec output_type. For documented_versioned: includes review, approval, and promotion steps. |
| start_step | string | true | Step identifier of the first step in the sequence. |
| terminal_steps | list | true | List of step identifiers for terminal (final) steps. |

Optional type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| max_refinement_iterations | integer | false | Default maximum refinement loop iterations. Default: 3. |

Validation constraints:
- start_step must reference an existing step_id.
- Each terminal step must have no onsuccess target (or terminal marker).
- No step may route to itself (no self-loops unless explicit refinement loop with max_iterations).
- All routing targets must reference existing step_ids.
- delivery_mechanism.output_type must match the spec output_type.

### runtime_standard

Required type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| consolidated_phases | list | true | List of references to phases 1 through 6 content (phase_number, component_type, content_location). |
| cross_phase_consistency | boolean | true | Must be true, indicating all phases are mutually consistent. |
| standard_filename | string | true | Target standard filename from spec frontmatter (must end with .md). |
| layer1_content | object | true | Reference to component schema section (component_schema component_id). |
| layer2_content | object | true | Reference to composition format section (composition_format component_id). |
| layer3_content | object | true | Reference to output format section (output_format component_id). |

Optional type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| embedded_spec_path | string | false | Path to the embedded self-bootstrap spec for recursive capability. Default: "Specs/bootstrap.spec.md". |

Validation constraints:
- consolidated_phases must reference all 6 design phases (1 through 6).
- standard_filename must end with .md.
- layer1_content, layer2_content, layer3_content must reference valid component_ids.
- cross_phase_consistency must be true.

### operational_workflow

Required type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| toml_manifest | object | true | workflow.toml definition content including name, steps, artifacts, and routing. |
| prompt_files | list | true | List of prompt file entries (path, step_reference, required_inputs). |
| action_modules | list | true | List of action module entries (path, function_name, step_reference). |
| context_extensions_class | string | true | Class name derived from the target workflow_name (e.g., TargetWorkflowNameContextExtensions). |
| self_bootstrap_spec | string | true | Path to the embedded builder spec for recursive chain self-bootstrapping. |

Optional type-specific properties:

| Property Name | Data Type | Required | Description |
|---|---|---|---|
| codename | string | false | Unique codename for this workflow version. Used in folder naming pattern: {base_workflow_name}_{codename}. |

Validation constraints:
- toml_manifest.name must match the target workflow_name from the spec.
- prompt_files must reference the target standard_filename (not any builder standard).
- context_extensions_class must be derived from the target workflow_name (not builder workflow_name).
- self_bootstrap_spec must point to a valid file within the workflow package Specs/ directory.

---

## Validation Rules

The following 8 validation rules apply to all components in the target workflow pipeline. Each rule is numbered sequentially and specifies the component types it applies to, a deterministic check, and the error message emitted on failure.

### VR-001: Required Common Fields Present

- Identifier: VR-001
- Applies to: all component types
- Check: The component contains all 7 required common fields (component_id, component_type, name, version, description, phase_origin, identity_locked) with non-empty values.
- Pass condition: All 7 fields are present and non-empty.
- Error message: "Missing required common field(s): {field_names}. All components must declare component_id, component_type, name, version, description, phase_origin, and identity_locked."

### VR-002: Valid Component Type

- Identifier: VR-002
- Applies to: all component types
- Check: The component_type value is one of the 8 types declared in this schema (domain_analysis, component_schema, composition_format, output_format, artifact_contract, step_sequence, runtime_standard, operational_workflow).
- Pass condition: component_type matches a declared type identifier exactly.
- Error message: "Unknown component_type '{value}'. Must be one of: domain_analysis, component_schema, composition_format, output_format, artifact_contract, step_sequence, runtime_standard, operational_workflow."

### VR-003: Unique Component Identifier

- Identifier: VR-003
- Applies to: all component types
- Check: The component_id value is unique across all component instances in the pipeline. No two components share the same component_id.
- Pass condition: component_id appears exactly once across all pipeline artifacts.
- Error message: "Duplicate component_id '{value}' found. Each component must have a unique identifier across the entire pipeline."

### VR-004: Type-Specific Schema Conformance

- Identifier: VR-004
- Applies to: all component types
- Check: All required type-specific properties for the declared component_type are present and have valid data types as defined in the Type-Specific Properties section.
- Pass condition: Every required property listed for the declared component_type exists in the component and has the correct data type.
- Error message: "Component of type '{type}' is missing required type-specific property '{property_name}' or has invalid data type. Expected type: {expected_type}."

### VR-005: Identity Locking Verified

- Identifier: VR-005
- Applies to: all component types
- Check: The identity_locked field is set to true. All identity fields (workflow_name, standard_name, standard_version, standard_filename) match the values declared in the runtime specification frontmatter.
- Pass condition: identity_locked is true and no identity field contains builder identity tokens.
- Error message: "identity_locked must be true for all artifacts. Identity fields must match the target runtime specification, not any upstream builder."

### VR-006: Phase Origin Matches Position

- Identifier: VR-006
- Applies to: all component types
- Check: The phase_origin value matches the expected pipeline position for the declared component_type. domain_analysis -> "1", component_schema -> "2", composition_format -> "3", output_format -> "4", artifact_contract -> "5", step_sequence -> "6", runtime_standard -> "7", operational_workflow -> "8".
- Pass condition: phase_origin matches the declared phase for the component_type.
- Error message: "phase_origin '{value}' does not match the expected phase '{expected}' for component_type '{type}'."

### VR-007: Base Schema Structural Validity

- Identifier: VR-007
- Applies to: all component types
- Check: The component document includes valid YAML frontmatter with required fields (doc_type, identity_locked). All section headings follow the template structure. All identifiers (VR-NNN, RR-NNN, QR-NNN) follow the declared naming convention. The base_schema_version field in the component_schema component follows semantic versioning format.
- Pass condition: YAML frontmatter is parseable, required sections are present, identifier formats match conventions, and version strings are valid semver.
- Error message: "Structural validity check failed: {detail}. Ensure YAML frontmatter is valid, section headings match the template, and all identifiers follow naming conventions (VR-NNN, RR-NNN, QR-NNN)."

### VR-008: Semantic Validity and Cross-Property Constraints

- Identifier: VR-008
- Applies to: all component types
- Check: Cross-property referential integrity is maintained across the pipeline. Specifically:
  (a) component_schema: All component_types referenced in binding_rules (composition_format) must exist in the component_types list.
  (b) composition_format: All component_types referenced in binding_rules must exist in component_schema.
  (c) output_format: All resolution_rules must reference placeholders that exist in composition_format.
  (d) artifact_contract: All artifact_keys must be unique and conflict-free with declared registries.
  (e) step_sequence: All artifact references in step inputs/outputs must exist in artifact_contract.
  (f) runtime_standard: All layer content references must resolve to valid component_ids.
- Pass condition: All cross-references resolve to existing declarations. No orphaned references.
- Error message: "Semantic validity check failed: {detail}. All cross-property references must resolve to existing declarations within the pipeline."

---

## Fine-Tuning Decisions

The following decisions document how the base schema (defined in METADATA_STANDARD.md and METADATA_CONTRACT.md) was adapted for the target domain (meta-workflow composition).

| Decision | Element | Action | Rationale |
|---|---|---|---|
| FTD-001 | 7 common properties (component_id, component_type, name, version, description, phase_origin, identity_locked) | keep | Required by test criteria TC-P2-023. These properties cover identity, traceability, versioning, and governance locking for all pipeline components. |
| FTD-002 | 8 component types (domain_analysis through operational_workflow) | keep | Each type maps to one of the 8 natural design phases identified in the domain analysis. All are derived from the spec domain description, not from any builder schema. |
| FTD-003 | target_identity property on domain_analysis type | specialize | The meta-workflow composition domain requires explicit identity extraction from runtime specs. The target_identity object captures the spec frontmatter identity as a structured sub-object, enabling downstream identity isolation checks (INV-1). |
| FTD-004 | base_schema_version property on component_schema type | add | The component_schema must declare which base schema version it specializes. This enables version compatibility checks and supports the recursive capability requirement (INV-4). |
| FTD-005 | meta_test_criteria property on domain_analysis type | specialize | The spec mandates exactly 4 invariants (INV-1 through INV-4) that are immutable across all phases. This property captures them as structured entries for propagation to downstream gatekeep prompts. |
| FTD-006 | override_mechanism property on composition_format type | add | The spec requires a documented override mechanism with syntax, precedence, identity override guarantee, and usage examples. This is domain-specific to the composition layer. |
| FTD-007 | conflict_check_passed property on artifact_contract type | add | The spec requires explicit confirmation that no artifact key collisions exist with the global registry. This boolean property provides a deterministic pass/fail signal. |
| FTD-008 | context_extensions_class property on operational_workflow type | specialize | The spec requires the class name to be derived from the target workflow_name, not the builder workflow_name. This property enables identity isolation verification at the code level. |
| FTD-009 | self_bootstrap_spec property on operational_workflow type | add | The spec requires recursive capability (INV-4). The embedded spec path enables the generated workflow to bootstrap the next version of itself. |
| FTD-010 | phase_position optional property | add | Supports granular ordering within phases for the step_sequence component. Marked optional because not all types need sub-phase positioning. |
| FTD-011 | depends_on optional property | add | Supports explicit dependency declarations between components. Enables VR-008 cross-reference validation and deterministic ordering in the composition_format. |
| FTD-012 | codename optional property on operational_workflow type | add | The spec requires a unique codename for version naming. The codename enables the {base_workflow_name}_{codename} folder naming pattern and prevents overwriting source workflows during recursive bootstrapping. |

---

## Self-Validation

### Completeness Checks

| Check | Result |
|---|---|
| All 8 component types have type-specific properties defined | PASS -- domain_analysis (5 required, 1 optional), component_schema (5 required, 1 optional), composition_format (4 required, 1 optional), output_format (4 required, 1 optional), artifact_contract (3 required, 1 optional), step_sequence (5 required, 1 optional), runtime_standard (6 required, 1 optional), operational_workflow (5 required, 1 optional) |
| All 7 common properties present and consistent | PASS -- component_id, component_type, name, version, description, phase_origin, identity_locked |
| VR-001 through VR-008 numbered and specific | PASS -- 8 rules, each with unique identifier, applicable types, deterministic check, pass condition, and error message |
| Component types derived from spec domain | PASS -- all 8 types trace to sections in bootstrap.spec.md (Purpose, Output, Constraints, Success Criteria) |
| No builder identity leakage | PASS -- no occurrence of builder workflow_name or builder standard_name as target identity values |
| ASCII-only content | PASS -- all text uses ASCII characters (code points 0-127) |
| Fine-tuning decisions present with rationale | PASS -- 12 decisions (FTD-001 through FTD-012), each with action and rationale |
| Frontmatter correct | PASS -- doc_type is "component_schema", identity_locked is true |
| Type-specific properties do not collide with common properties | PASS -- no type-specific property name matches a common property name |
| Validation rules reference only declared properties | PASS -- all VR rules reference properties that exist in the common or type-specific property definitions |

### Traceability Matrix

| Component Type | Phase | Type-Specific Properties Count | Validation Rules Applying |
|---|---|---|---|
| domain_analysis | 1 | 5 required, 1 optional | VR-001, VR-002, VR-003, VR-004, VR-005, VR-006, VR-007, VR-008 |
| component_schema | 2 | 5 required, 1 optional | VR-001, VR-002, VR-003, VR-004, VR-005, VR-006, VR-007, VR-008 |
| composition_format | 3 | 4 required, 1 optional | VR-001, VR-002, VR-003, VR-004, VR-005, VR-006, VR-007, VR-008 |
| output_format | 4 | 4 required, 1 optional | VR-001, VR-002, VR-003, VR-004, VR-005, VR-006, VR-007, VR-008 |
| artifact_contract | 5 | 3 required, 1 optional | VR-001, VR-002, VR-003, VR-004, VR-005, VR-006, VR-007, VR-008 |
| step_sequence | 6 | 5 required, 1 optional | VR-001, VR-002, VR-003, VR-004, VR-005, VR-006, VR-007, VR-008 |
| runtime_standard | 7 | 6 required, 1 optional | VR-001, VR-002, VR-003, VR-004, VR-005, VR-006, VR-007, VR-008 |
| operational_workflow | 8 | 5 required, 1 optional | VR-001, VR-002, VR-003, VR-004, VR-005, VR-006, VR-007, VR-008 |

### Test Criteria Coverage (Phase 2)

| Test Criterion | Coverage |
|---|---|
| TC-P2-001 (all types defined) | Covered -- 8 types in Component Type Summary |
| TC-P2-002 (unique type identifiers) | Covered -- all 8 identifiers are unique, alphanumeric with underscores |
| TC-P2-003 (no builder name collision) | Covered -- no type matches builder workflow_name or standard_name |
| TC-P2-004 (purpose description) | Covered -- each type has a purpose column in the summary table |
| TC-P2-005 (at least one type) | Covered -- 8 types defined |
| TC-P2-006 (exactly 7 common properties) | Covered -- 7 properties in Common Properties table |
| TC-P2-007 (name, data type, required flag) | Covered -- each common property has name, data_type, required, description |
| TC-P2-008 (unique property names) | Covered -- no duplicates in common properties |
| TC-P2-009 (valid data types) | Covered -- string, integer, boolean, list, object used |
| TC-P2-010 (description for each) | Covered -- description column present |
| TC-P2-011 (identifier property) | Covered -- component_id serves as unique identifier |
| TC-P2-012 (identical set across types) | Covered -- same 7 common properties for all types |
| TC-P2-013 (type-specific properties) | Covered -- each type has dedicated property section |
| TC-P2-014 (no name collision) | Covered -- type-specific names differ from common names |
| TC-P2-015 (naming and typing conventions) | Covered -- same conventions as common properties |
| TC-P2-016 (required marking) | Covered -- required column in each type-specific table |
| TC-P2-017 (optional with defaults) | Covered -- optional tables include default values |
| TC-P2-018 (at least 8 VR rules) | Covered -- VR-001 through VR-008 defined |
| TC-P2-019 (unique VR identifiers) | Covered -- VR-001 through VR-008, sequential |
| TC-P2-020 (applies_to specified) | Covered -- each VR lists applicable types |
| TC-P2-021 (deterministic check) | Covered -- each VR has explicit pass condition |
| TC-P2-022 (error message) | Covered -- each VR has error_message template |
| TC-P2-023 (VR-001 common fields) | Covered -- checks all 7 common fields |
| TC-P2-024 (VR-002 valid type) | Covered -- checks against 8 declared types |
| TC-P2-025 (VR-003 unique ID) | Covered -- uniqueness check across pipeline |
| TC-P2-026 (VR-004 type-specific conformance) | Covered -- checks required properties per type |
| TC-P2-027 (VR-005 identity lock) | Covered -- checks identity_locked is true |
| TC-P2-028 (VR-006 phase origin) | Covered -- checks phase_origin matches type position |
| TC-P2-029 (VR-007 structural validity) | Covered -- checks YAML, sections, naming conventions |
| TC-P2-030 (VR-008 semantic validity) | Covered -- checks cross-property referential integrity |
| TC-P2-031 (no builder references in VR) | Covered -- no VR references builder-specific types or names |
| TC-P2-032 (fine-tuning decisions array) | Covered -- 12 decisions in Fine-Tuning Decisions table |
| TC-P2-033 (rationale for each decision) | Covered -- each decision has rationale column |

---

**End of Domain Component Schema**
