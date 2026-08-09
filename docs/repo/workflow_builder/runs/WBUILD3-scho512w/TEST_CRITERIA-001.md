---
doc_type: "test_criteria"
lifecycle_status: "draft"
domain: "workflow_builder"
total_criteria_count: 157
---

# Test Criteria for Workflow Builder v3 Meta-Meta Builder

## Introduction

### Scope

This document defines the acceptance criteria for the Workflow Builder v3 meta-meta builder workflow. These criteria apply to every artifact produced during the 9-phase, 21-step execution of workflow_builder_v3. Each criterion is specific, verifiable, and traceable to the composition system specification provided as input (WORKFLOW_SPEC_FILE: ar_meta_builder_v2.md).

### Purpose

The criteria serve three purposes:

1. Gatekeep decisions at each phase boundary -- the gatekeeper reviews use these criteria to approve or reject artifacts.
2. Reviewer guidance -- the reviewer uses these criteria to produce actionable feedback.
3. Refinement targeting -- when an artifact is rejected, the refine step uses failed criteria to scope the correction.

### Applicability

All criteria in this document apply to the Workflow Builder v3 workflow. The input specification (ar_meta_builder_v2.md) describes the requirements of the AR Meta Builder v2 -- the target workflow that the builder must generate. The criteria verify that v3 correctly processes that specification into the required output: a complete executable workflow package with composition standard and self-bootstrap spec.

### Structure

- TC-001 through TC-008: Foundation Phase (Phase 1)
- TC-009 through TC-032: Component Schema (Phase 2)
- TC-033 through TC-048: Composition Format (Phase 3)
- TC-049 through TC-072: Output Format (Phase 4)
- TC-073 through TC-091: Operational Workflow (Phase 5)
- TC-092 through TC-100: Composition Standard (Phase 6)
- TC-101 through TC-109: Meta Composition Spec (Phase 7)
- TC-110 through TC-134: Package Assembly (Phase 8)
- TC-135 through TC-144: Promotion (Phase 9)
- TC-145 through TC-152: Negative Criteria
- TC-153 through TC-157: Self-Validation

---

## Criteria for Foundation Phase (Phase 1)

This phase contains 3 steps: generate_test_criteria (01), review_test_criteria (02), and refine_test_criteria (03, conditional). The phase produces the acceptance criteria document that all subsequent phases are measured against.

TC-001: The generated TEST_CRITERIA_FILE exists at the path declared in workflow.toml for the TEST_CRITERIA_FILE artifact key, under the runs/{job_id}/ directory.

TC-002: The TEST_CRITERIA_FILE contains YAML frontmatter with the following mandatory fields: doc_type set to "test_criteria", lifecycle_status, domain set to "workflow_builder", and total_criteria_count as an integer.

TC-003: The total_criteria_count value in the frontmatter equals the actual count of TC-NNN identifiers present in the document body.

TC-004: The document contains exactly 12 sections: Introduction, Criteria for Foundation Phase (Phase 1), Criteria for Component Schema (Phase 2), Criteria for Composition Format (Phase 3), Criteria for Output Format (Phase 4), Criteria for Operational Workflow (Phase 5), Criteria for Composition Standard (Phase 6), Criteria for Meta Composition Spec (Phase 7), Criteria for Package Assembly (Phase 8), Criteria for Promotion (Phase 9), Negative Criteria, and Self-Validation.

TC-005: Every criterion identifier (TC-NNN) is unique across the entire document -- no duplicate identifiers exist.

TC-006: Every criterion uses specific, verifiable language. No criterion contains vague phrases such as "must work properly", "must be correct", "should be good", or "must be handled appropriately".

TC-007: Every criterion traces to a specific requirement in the input specification (ar_meta_builder_v2.md). No criterion invents requirements absent from the spec sections 1 through 7.

TC-008: The REVIEW_TEST_CRITERIA_FILE produced by step 02 contains a structured review with explicit APPROVED or REJECTED verdict per criterion category, and REJECTED categories include specific failure reasons with criterion identifiers (TC-NNN references).

---

## Criteria for Component Schema (Phase 2)

This phase contains 2 steps: generate_component_schema (04) and gatekeep_component_schema (05). It defines the Layer 1 component schema for the target domain.

TC-009: The COMPONENT_SCHEMA_FILE defines exactly 8 component types as listed in spec Section 4.1: domain_analysis, component_schema, composition_format, output_format, artifact_contract, step_sequence, runtime_standard, operational_workflow.

TC-010: Each of the 8 component types includes a phase mapping matching spec Section 4.1: domain_analysis maps to Phase 1, component_schema to Phase 2, composition_format to Phase 3, output_format to Phase 4, artifact_contract to Phase 5, step_sequence to Phase 6, runtime_standard to Phase 7, operational_workflow to Phase 8.

TC-011: Each of the 8 component types is marked as Required = Yes, matching the spec Section 4.1 table where all 8 types have "Yes" in the Required column.

TC-012: Each of the 8 component types has Cardinality = Singleton, matching the spec Section 4.1 table where all 8 types have "Singleton" in the Cardinality column.

TC-013: The component schema defines exactly 7 required common properties matching spec Section 4.2: component_id (string), component_type (enum), name (string), version (string), description (string), phase_origin (integer), identity_locked (boolean).

TC-014: The component_id format is defined as "{phase}-{type}-{workflow_name}" matching the description in spec Section 4.2.

TC-015: Type-specific properties are defined for each of the 8 component types matching spec Section 4.3. For domain_analysis: target_identity (object, required), output_type (enum, required), natural_phases (array, required), component_inventory (array, required), meta_test_criteria (array, required).

TC-016: Type-specific properties for component_schema match spec Section 4.3: base_schema_version (string, required), fine_tuning_decisions (array, required), domain_types (array, required), validation_rules (array, required).

TC-017: Type-specific properties for composition_format match spec Section 4.3: binding_rules (array, required), override_mechanism (object, required), placeholder_resolution (object, required), examples (array, optional).

TC-018: Type-specific properties for output_format match spec Section 4.3: output_sections (array, required), resolution_rules (array, required), quality_requirements (array, required).

TC-019: Type-specific properties for artifact_contract match spec Section 4.3: artifact_keys (array, required), conflict_check_passed (boolean, required).

TC-020: Type-specific properties for step_sequence match spec Section 4.3: steps (array, required), review_loops (array, optional), approval_gates (array, optional), delivery_mechanism (object, required).

TC-021: Type-specific properties for runtime_standard match spec Section 4.3: standard_name (string, required), standard_version (string, required), consolidated_phases (array, required), cross_phase_consistency (boolean, required).

TC-022: Type-specific properties for operational_workflow match spec Section 4.3: workflow_steps (array, required), prompt_files (array, required), action_implementations (array, required), context_extensions (object, required).

TC-023: The schema includes exactly 8 validation rules: VR-001 through VR-008, each with a unique rule identifier and a specific verifiable rule statement matching spec Section 4.4.

TC-024: VR-001 verifies that all 7 required common fields are present (component_id, component_type, name, version, description, phase_origin, identity_locked).

TC-025: VR-002 verifies that component_type is one of the 8 valid types defined in Section 4.1.

TC-026: VR-003 verifies that component_id values are unique across the pipeline -- no duplicates.

TC-027: VR-004 verifies that type-specific schema conformance is met -- all required properties for the declared component_type are present.

TC-028: VR-005 verifies that identity_locked = true for all artifacts, confirming identity matches the target spec and not the builder.

TC-029: VR-006 verifies that phase_origin matches the artifact's position in the pipeline (integer 1-8).

TC-030: VR-007 verifies that base_schema_version >= "2.0" for component_schema type artifacts.

TC-031: VR-008 verifies that conflict_check_passed = true for artifact_contract type artifacts.

TC-032: The GATEKEEP_COMPONENT_SCHEMA_FILE produced by step 05 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-009 through TC-031) that failed.

---

## Criteria for Composition Format (Phase 3)

This phase contains 2 steps: generate_composition_format (06) and gatekeep_composition_format (07). It defines the Layer 2 composition format -- how domain components bind together.

TC-033: The COMPOSITION_FORMAT_FILE defines the composition structure matching spec Section 5.1, including composition_id, name, target_metadata (with workflow_name, standard_name, output_type), and component_bindings.

TC-034: The composition format defines exactly 8 component bindings matching spec Section 5.1: domain_analysis, component_schema, composition_format, output_format, artifact_contract, step_sequence, runtime_standard, operational_workflow.

TC-035: Each component binding includes a component_id field following the format "phase-{N}-{type}-{workflow_name}" matching spec Section 5.1.

TC-036: The composition format defines exactly 8 binding rules matching spec Section 5.2: domain_analysis (consumed by Phases 2-8), component_schema (consumed by Phases 3 and 7), composition_format (consumed by Phases 4 and 7), output_format (consumed by Phases 6 and 7), artifact_contract (consumed by Phases 6 and 8), step_sequence (consumed by Phases 7 and 8), runtime_standard (consumed by Phase 8), operational_workflow (consumed by Phase 9).

TC-037: Each binding rule specifies: binding name, source phase, consumed-by phases, required flag (all Yes), and description, matching spec Section 5.2.

TC-038: The composition format defines an override mechanism matching spec Section 5.3, including: identity fields ALWAYS sourced from the runtime spec (never derived), base_schema_path resolved via context_extensions, and meta-test-criteria injected into all subsequent gatekeep prompts.

TC-039: The override mechanism specifies that domain_analysis overrides include target_identity and output_type, both sourced from WORKFLOW_SPEC_FILE.

TC-040: The override mechanism specifies that component_schema overrides include base_schema_path sourced from BASE_COMPOSITION_STANDARD.

TC-041: The composition format defines a placeholder resolution mechanism matching spec Section 5.4 with exactly 7 placeholders: {WORKFLOW_SPEC_FILE}, {BASE_COMPOSITION_STANDARD}, {standard_name}, {standard_version}, {standard_filename}, {output_type}, {workflow_name}.

TC-042: Each placeholder specifies its data source matching spec Section 5.4: WORKFLOW_SPEC_FILE resolves to runtime spec file path, BASE_COMPOSITION_STANDARD to base schema file path, standard_name/standard_version/standard_filename/workflow_name from spec identity section, output_type from spec output delivery section.

TC-043: All 7 placeholders are marked as Required = Yes, matching spec Section 5.4.

TC-044: The composition format defines the meta-test-criteria binding matching spec Section 5.5, specifying that Phase 1's meta_test_criteria are injected into ALL subsequent phases' gatekeep prompts as cross-phase invariants.

TC-045: The meta-test-criteria include at minimum the 4 invariants from spec Section 5.5: identity uses spec not builder, structure matches spec domain not AMB structure, output delivery matches spec output type, component types derived from base schema fine-tuning not hardcoded.

TC-046: The composition format specifies that every gatekeeper (Phases 2-8) checks both phase-specific test criteria AND the meta-test-criteria from domain_analysis.

TC-047: The domain_analysis binding override correctly maps target_identity to values extracted from WORKFLOW_SPEC_FILE, and output_type to the value from WORKFLOW_SPEC_FILE, matching spec Section 5.3.

TC-048: The GATEKEEP_COMPOSITION_FORMAT_FILE produced by step 07 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-033 through TC-047) that failed.

---

## Criteria for Output Format (Phase 4)

This phase contains 2 steps: generate_output_format (08) and gatekeep_output_format (09). It defines the Layer 3 output format -- what the target workflow produces.

TC-049: The OUTPUT_FORMAT_FILE defines exactly 7 output artifacts matching spec Section 6.1: workflow.toml (Phase 8+9), context_extensions.py (Phase 8+9), actions.py (Phase 8+9), prompts/*.txt (Phase 8+9), README.md (Phase 9), Standards/{standard_filename} (Phase 7+9), Specs/{builder_name}.md (Phase 9).

TC-050: Each output artifact specifies its source phase and description matching spec Section 6.1.

TC-051: The output format specifies that workflow.toml contains the complete workflow definition with correct identity (from target spec, not builder).

TC-052: The output format specifies that context_extensions.py contains domain-specific artifact keys and path resolution.

TC-053: The output format specifies that actions.py contains domain-specific action implementations.

TC-054: The output format specifies that prompts/*.txt contains one prompt file per prompt-driven step.

TC-055: The output format specifies that README.md describes the target workflow (not the builder).

TC-056: The output format specifies that Standards/{standard_filename} contains the target's composition standard with filename from spec identity.

TC-057: The output format specifies that Specs/{builder_name}.md contains the embedded AMB v2 spec for self-bootstrap.

TC-058: The output format defines exactly 5 resolution rules matching spec Section 6.2: (1) all phase outputs consolidated -- Phase 7 consolidates Phases 1-6 into the runtime standard, (2) identity resolved -- all identity fields from runtime spec not builder, (3) placeholders resolved -- all {placeholders} filled from spec and context, (4) self-contained -- workflow package executable without reference to builder, (5) self-bootstrapping -- builder's own spec embedded in Specs/ for recursive chain.

TC-059: The output format defines exactly 12 quality requirements matching spec Section 6.3: QR-001 through QR-012.

TC-060: QR-001 verifies identity correctness -- workflow.toml name matches spec's workflow_name.

TC-061: QR-002 verifies no builder leakage -- no reference to "ar_meta_builder_v2" or "AMB_STANDARD" in generated output.

TC-062: QR-003 verifies standard filename matches spec's standard_filename.

TC-063: QR-004 verifies all artifact keys are unique and conflict-free with global registry.

TC-064: QR-005 verifies all prompt files exist for prompt-driven steps.

TC-065: QR-006 verifies Python syntax is valid in context_extensions.py and actions.py.

TC-066: QR-007 verifies TOML parse is valid in workflow.toml.

TC-067: QR-008 verifies class name in context_extensions.py is derived from workflow_name.

TC-068: QR-009 verifies output delivery mechanism matches spec's output_type.

TC-069: QR-010 verifies meta-test-criteria satisfied across all generated artifacts.

TC-070: QR-011 verifies self-bootstrap spec present in Specs/ directory.

TC-071: QR-012 verifies Standards/ directory contains the composition standard with correct filename.

TC-072: The GATEKEEP_OUTPUT_FORMAT_FILE produced by step 09 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-049 through TC-071) that failed.

---

## Criteria for Operational Workflow (Phase 5)

This phase contains 2 steps: generate_operational_workflow (10) and gatekeep_operational_workflow (11). It defines the complete operational workflow for the target.

TC-073: The OPERATIONAL_WORKFLOW_FILE defines the TDD-as-DNA pattern matching spec Section 7.1: each phase follows the standardized 5-step pattern (generate_test_criteria, review_test_criteria [with refine loop], generate_artifact, validate_artifact, gatekeep_artifact [with refine loop]).

TC-074: The operational workflow defines exactly 9 phases matching spec Section 7.2: (1) Analyze Spec, (2) Domain Component Schema, (3) Composition Format, (4) Output Format, (5) Component Artifacts, (6) Domain Steps, (7) Runtime Standard, (8) Operational Workflow, (9) Package.

TC-075: Each phase in the operational workflow specifies its artifact, validate action, and key test criteria focus matching spec Section 7.2.

TC-076: Phase 1 validate action is validate_input_spec (pre-step), checking identity fields, output type, domain overview, and at least one component concept.

TC-077: Phases 2-8 validate action is validate_design_artifact, parameterized by phase, checking common file existence, parse correctness, identity match, and phase-specific rules (VR-001 through VR-008).

TC-078: Phase 9 validate action is validate_package, checking all files present, TOML/Python validity, identity consistency, Standards/ and Specs/ directories, prompt placeholder consistency, and bidirectional artifact consistency.

TC-079: The operational workflow defines exactly 2 input artifacts matching spec Section 7.4: WORKFLOW_SPEC_FILE (required) and BASE_COMPOSITION_STANDARD (required, resolved by context_extensions).

TC-080: The operational workflow defines output artifacts matching spec Section 7.5, including: DOMAIN_ANALYSIS_FILE, DOMAIN_COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, ARTIFACT_CONTRACT_FILE, STEP_SEQUENCE_FILE, RUNTIME_STANDARD_FILE, OPERATIONAL_WORKFLOW_FILE, WORKFLOW_PACKAGE_DIR_FILE, STANDARDS_COMPOSITION_STANDARD_FILE, SPECS_BUILDER_SPEC_FILE, REVIEW_FILE_SUGGESTED, TEST_CRITERIA_FILE.

TC-081: The operational workflow includes identity locking rules matching spec Section 7.6: do NOT use ar_meta_builder_v2 as workflow name, do NOT use AMB_STANDARD as standard name, do NOT copy the builder's 9-phase structure, do NOT hardcode component types, do NOT assume output type.

TC-082: The operational workflow includes base schema sync requirement: prompts reference {BASE_COMPOSITION_STANDARD} and validate action checks MIN_BASE_SCHEMA_VERSION = "2.0".

TC-083: The operational workflow includes recursive self-bootstrap: Phase 9 copies WORKFLOW_SPEC_FILE to Specs/ar_meta_builder_v2.md in the output package.

TC-084: The operational workflow includes meta-test-criteria propagation: Phase 1's meta_test_criteria are injected into ALL subsequent phases' gatekeep prompts via context_extensions.

TC-085: The three-tier quality gate per phase is defined: Critic (review step) reviews test quality, Validate (action step) performs deterministic checks, Gatekeeper (prompt step) runs test criteria against artifact with pass/fail and evidence.

TC-086: The validate_input_spec action is defined with specific checks: identity fields present (standard_name, standard_version, standard_filename), output type declared (documented_versioned or direct), domain overview section present, at least one component or domain concept described, on fail routes to AWAITING_INTERVENTION.

TC-087: The validate_design_artifact action is parameterized by phase and defines phase-specific validation: common checks (file existence, parse, identity), type-specific rules (VR-001 through VR-008), artifact key conflict check (Phase 5), review/approval design check (Phase 6 if output_type = documented_versioned).

TC-088: The validate_package action defines comprehensive checks: all files present (workflow.toml, context_extensions.py, actions.py, prompts/), TOML parse validity, Python syntax, identity consistency, Standards/ directory with correct filename, Specs/ directory with embedded builder spec, prompt placeholder vs required_inputs consistency, bidirectional artifact consistency.

TC-089: The operational workflow defines the output delivery as documented_versioned matching spec Section 3: generate, review, refine, approve, promote, archive pipeline applies.

TC-090: The artifact flow is consistent: every artifact consumed by a step is either an input declared in the workflow (WORKFLOW_SPEC_FILE, BASE_COMPOSITION_STANDARD) or produced by a preceding step.

TC-091: The GATEKEEP_OPERATIONAL_WORKFLOW_FILE produced by step 11 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-073 through TC-090) that failed.

---

## Criteria for Composition Standard (Phase 6)

This phase contains 2 steps: generate_composition_standard (12) and gatekeep_composition_standard (13). This is a v3 innovation -- the composition standard is a first-class output that enables extensibility.

TC-092: The COMPOSITION_STANDARD_FILE defines a composition standard with standard_name field matching the target spec's identity (not the builder's AMB_STANDARD).

TC-093: The composition standard includes a standard_version field with a semantic version string matching the target spec's declared version.

TC-094: The composition standard defines all 8 component types from the target domain (Phase 2 output), each in its own subsection with type name, purpose, required/optional flag, and cardinality.

TC-095: The composition standard includes a component_types_defined listing that enumerates all component types by name, matching the 8 types from Phase 2.

TC-096: The composition standard includes schema_sections that define the sections generated schemas must contain, derived from the common properties and type-specific properties defined in Phase 2.

TC-097: The composition standard includes a cross_phase_consistency declaration matching spec Section 4.3 (runtime_standard required property), specifying that all phases use consistent naming conventions, artifact key formats, validation patterns, and identity locking rules -- ensuring that components from different phases compose without naming or format conflicts.

TC-098: The composition standard consolidates content from Phases 1 through 5 (domain_analysis, component_schema, composition_format, output_format, and step_sequence) into a single coherent reference document.

TC-099: The identity fields in the composition standard (standard_name, standard_version) match the target spec identity, not the builder's identity (AMB_STANDARD, 2.0.0).

TC-100: The GATEKEEP_COMPOSITION_STANDARD_FILE produced by step 13 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-092 through TC-099) that failed.

---

## Criteria for Meta Composition Spec (Phase 7)

This phase contains 1 step: generate_meta_composition_spec (14). This is a v3 innovation -- the meta composition spec enables self-bootstrapping (the generated workflow can itself be processed by a builder to produce the next version).

TC-101: The META_COMPOSITION_SPEC_FILE defines a meta composition specification with exactly 5 sections: (1) Domain Overview, (2) Component Schema, (3) Composition Format, (4) Output Format, (5) Operational Requirements.

TC-102: Section 1 (Domain Overview) includes: domain name, label, job prefix, init step, description, purpose (transforming spec into workflow package), domain context (input/output definitions), and recursive chain explanation.

TC-103: Section 2 (Component Schema) covers the 8 component types from Phase 2, common properties (7 required), type-specific properties for each type, and validation rules (VR-001 through VR-008).

TC-104: Section 3 (Composition Format) covers the composition structure, 8 binding rules from Phase 3, override mechanism, placeholder resolution (7 placeholders), and meta-test-criteria binding.

TC-105: Section 4 (Output Format) covers the 7 output artifacts, resolution rules (5 rules), and quality requirements (QR-001 through QR-012) from Phase 4.

TC-106: Section 5 (Operational Requirements) covers the TDD pattern, 9 phases, validate actions (validate_input_spec, validate_design_artifact, validate_package), input/output artifact declarations, and domain-specific requirements (identity locking, base schema sync, recursive self-bootstrap, meta-test-criteria propagation). The spec must be self-bootstrapping -- it contains enough information for the builder to process it as input and generate the next version.

TC-107: The meta composition spec uses the TARGET identity (standard_name, standard_version, standard_filename from the input spec) throughout -- not the builder's own identity values.

TC-108: The meta composition spec includes workflow identity block matching spec Section 2: workflow_name, standard_name, standard_version, standard_filename -- all from the target spec, explicitly locked.

TC-109: The meta composition spec includes output delivery declaration matching spec Section 3: output_type (documented_versioned or direct), approval_before_execution, archive_after_approval.

---

## Criteria for Package Assembly (Phase 8)

This phase contains 5 steps: generate_package (15), validate_package_deterministic (16), gatekeep_package (17), review_package (18), and refine_package (19, conditional). This phase assembles the complete executable workflow package.

TC-110: The WORKFLOW_MANIFEST_FILE (workflow.toml) produced by step 15 is valid TOML and parses without errors.

TC-111: The workflow.toml declares the target workflow's identity (name, version, label, job_prefix) matching the spec's identity section -- NOT the builder's identity (ar_meta_builder_v2, AMB_STANDARD).

TC-112: The workflow.toml declares all steps in correct order with correct step names, types (prompt or action), artifact keys, and routing behavior matching the operational workflow from Phase 5.

TC-113: The workflow.toml declares WORKFLOW_SPEC_FILE as a required_input for the workflow, matching spec Section 7.4.

TC-114: The workflow.toml includes step routing: each step's onsuccess points to the correct next step, and on_reject_refine (where applicable) routes to the correct refine step with max_iterations defined.

TC-115: The WORKFLOW_EXTENSIONS_FILE (context_extensions.py) produced by step 15 is syntactically valid Python that parses without errors (verifiable via python -c "import ast; ast.parse(open(file).read())").

TC-116: The context_extensions.py class name is derived from the target workflow_name (matching QR-008), not the builder's class name.

TC-117: The context_extensions.py defines artifact key coverage -- every artifact key declared in workflow.toml has a corresponding path resolution entry.

TC-118: The WORKFLOW_ACTIONS_FILE (actions.py) produced by step 15 is syntactically valid Python that parses without errors.

TC-119: The actions.py implements all action steps declared in the workflow.toml with @action decorators matching the action names in step definitions.

TC-120: The validate_package_deterministic action implements deterministic validation checks: file existence, TOML parse validity, Python syntax, identity consistency, Standards/ directory presence, Specs/ directory presence, prompt placeholder consistency, bidirectional artifact consistency.

TC-121: The generate_package step produces all required outputs: WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE.

TC-122: The refine_package step (step 19) produces the same set of outputs as generate_package (step 15): WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, STANDARDS_COMPOSITION_STANDARD_FILE.

TC-123: Both generate_package and refine_package declare STANDARDS_COMPOSITION_STANDARD_FILE in their produces sections.

TC-124: All prompt template files (prompts/NN_{step_name}.txt) exist for every prompt-type step declared in workflow.toml.

TC-125: Each {PLACEHOLDER} in each prompt template is declared in the corresponding step's required_inputs or produces in workflow.toml -- no dangling references.

TC-126: The WORKFLOW_README_FILE (README.md) exists and describes the target workflow's purpose, inputs, outputs, and how to invoke it -- not the builder.

TC-127: The STANDARDS_COMPOSITION_STANDARD_FILE is placed at Standards/{standard_filename} where standard_filename comes from the target spec's identity section.

TC-128: The embedded spec file in Specs/{builder_name}.md is content-identical to the input WORKFLOW_SPEC_FILE (recursive self-bootstrap per spec Section 7.6).

TC-129: No output file contains the builder's identity values (ar_meta_builder_v2, AMB_STANDARD, AMB) in contexts where the target's identity should appear.

TC-130: The GATEKEEP_PACKAGE_FILE produced by step 17 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-110 through TC-129) that failed.

TC-131: The REVIEW_FILE_SUGGESTED produced by step 18 contains a structured review with explicit verdict and, if issues found, lists specific findings with severity levels and affected file references.

TC-132: The workflow.toml coder role policies match the operational workflow design: architect_standard for generate steps, gatekeeper_standard for gatekeep steps, reviewer_standard for review steps.

TC-133: The validate_package_deterministic step (16) produces a VALIDATION_REPORT_FILE that documents all checks performed, their pass/fail status, and any error details.

TC-134: Prompt placeholder vs required_inputs bidirectional consistency: every {PLACEHOLDER} in a prompt is declared in the step's required_inputs or produces, AND every artifact in the step's required_inputs/produces that looks like a placeholder IS referenced in the prompt.

---

## Criteria for Promotion (Phase 9)

This phase contains 2 steps: promote_workflow_package (20) and step_completion (21).

TC-135: The WORKFLOW_PACKAGE_DIR_FILE artifact records the absolute path to the promoted workflow package directory under workflows/.

TC-136: The step_completion action (step 21) records the final outcome of the workflow execution in COMPLETION_RESULT, including success status and a summary of produced artifacts.

TC-137: The promoted directory contains workflow.toml at its root, and the TOML parses without errors.

TC-138: The promoted directory contains context_extensions.py at its root, and the Python file parses without syntax errors.

TC-139: The promoted directory contains actions.py at its root, and the Python file parses without syntax errors.

TC-140: The promoted directory contains a prompts/ subdirectory with all prompt template files (one per prompt-driven step).

TC-141: The promoted directory contains a Standards/ subdirectory with the composition standard file named {standard_filename} from the target spec.

TC-142: The promoted directory contains a Specs/ subdirectory with at least one .md file (the embedded builder spec -- content-identical to input WORKFLOW_SPEC_FILE).

TC-143: The promoted directory contains a README.md describing the target workflow.

TC-144: The promoted workflow package is fully self-contained and executable without reference to the builder that generated it.

---

## Negative Criteria

These criteria define what MUST NOT appear in any output artifact. Violation of any negative criterion is an automatic rejection.

TC-145: No output file contains non-ASCII characters. All files must use ASCII-only content. No em-dashes, no curly quotes, no Unicode characters.

TC-146: No output file contains a dangling reference -- every artifact key reference ({ARTIFACT_KEY}) in a prompt template must correspond to a declared artifact in the step's required_inputs or produces in workflow.toml.

TC-147: No output file contains scope invention -- every requirement, component type, binding rule, or step in the output must trace back to the input specification (ar_meta_builder_v2.md). No new component types, patterns, or phases may be introduced beyond what the spec defines.

TC-148: No YAML frontmatter block is missing any mandatory field specified for that document type.

TC-149: No output file contains vague criteria or requirements such as "must work properly", "must be correct", "should handle edge cases", or "must be robust".

TC-150: No output file contains resolved filesystem paths to governance or platform documents. Only filenames (e.g., COMPOSITION_SYSTEM_STANDARD.md) are permitted, not full paths.

TC-151: No output file redefines, contradicts, or extends Layer 1 (governance) or Layer 2 (platform constitution) content. These layers are read-only.

TC-152: No output file leaks the builder's identity into the generated workflow -- the workflow name must NOT be "ar_meta_builder_v2", the standard name must NOT be "AMB_STANDARD", and the standard filename must NOT be "AMB_STANDARD-v2.md" unless those are the target spec's values.

---

## Self-Validation

These criteria verify the completeness and internal consistency of the test criteria document itself.

TC-153: The test criteria document covers all 9 phases defined in the specification (Section 7.2): Analyze Spec, Domain Component Schema, Composition Format, Output Format, Component Artifacts, Domain Steps, Runtime Standard, Operational Workflow, and Package.

TC-154: The test criteria document covers all 21 steps in the workflow_builder_v3 step sequence: every step from 01 to 21 has at least one criterion that verifies its output or behavior.

TC-155: The test criteria document includes criteria for both v3 innovations: the Composition Standard (Phase 6, TC-092 through TC-100) and the Meta Composition Spec (Phase 7, TC-101 through TC-109).

TC-156: Every criterion (TC-001 through TC-152) is independently verifiable -- a gatekeeper can check each criterion without needing additional context beyond the input spec and the produced artifact.

TC-157: The total_criteria_count in the YAML frontmatter equals the actual count of TC-NNN entries in the document body. This self-referential check ensures the metadata is consistent with content.

End of Test Criteria Document
