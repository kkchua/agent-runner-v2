---
doc_type: "test_criteria"
lifecycle_status: "draft"
domain: "ar_meta_builder"
total_criteria_count: 134
---

# Test Criteria for AR Meta Builder v1 Meta-Meta Builder

## Introduction

### Scope

This document defines the acceptance criteria for the AR Meta Builder v1 meta-meta builder workflow. These criteria apply to every artifact produced during the 9-phase, 21-step execution of the workflow. Each criterion is specific, verifiable, and traceable to the composition system specification provided as input (WORKFLOW_SPEC_FILE).

### Purpose

The criteria serve three purposes:

1. Gatekeep decisions at each phase boundary -- the gatekeeper reviews use these criteria to approve or reject artifacts.
2. Reviewer guidance -- the reviewer uses these criteria to produce actionable feedback.
3. Refinement targeting -- when an artifact is rejected, the refine step uses failed criteria to scope the correction.

### Applicability

All criteria in this document apply to the AR Meta Builder v1 workflow. The input specification (WORKFLOW_SPEC_FILE) describes the requirements of the generated meta builder. The criteria verify that the workflow correctly processes that specification into the required 3-part output: Standards/COMPOSITION_STANDARD.md, Specs/{name}.md, and the workflow package.

### Structure

- TC-001 through TC-008: Foundation Phase (Phase 1)
- TC-009 through TC-026: Component Schema (Phase 2)
- TC-027 through TC-042: Composition Format (Phase 3)
- TC-043 through TC-053: Output Format (Phase 4)
- TC-054 through TC-074: Operational Workflow (Phase 5)
- TC-075 through TC-083: Composition Standard (Phase 6)
- TC-084 through TC-091: Meta Composition Spec (Phase 7)
- TC-092 through TC-116: Package Assembly (Phase 8)
- TC-117 through TC-122: Promotion (Phase 9)
- TC-123 through TC-129: Negative Criteria
- TC-130 through TC-134: Self-Validation

---

## Criteria for Foundation Phase (Phase 1)

This phase contains 3 steps: generate_test_criteria (01), review_test_criteria (02), and refine_test_criteria (03, conditional). The phase produces the acceptance criteria document that all subsequent phases are measured against.

TC-001: The generated TEST_CRITERIA_FILE exists at the path declared in workflow.toml for the TEST_CRITERIA_FILE artifact key.

TC-002: The TEST_CRITERIA_FILE contains YAML frontmatter with the following mandatory fields: doc_type set to "test_criteria", lifecycle_status, domain set to "ar_meta_builder", and total_criteria_count.

TC-003: The total_criteria_count value in the frontmatter matches the actual number of TC-NNN entries in the document body.

TC-004: The document contains exactly 12 top-level sections: Introduction, Criteria for Foundation Phase (Phase 1), Criteria for Component Schema (Phase 2), Criteria for Composition Format (Phase 3), Criteria for Output Format (Phase 4), Criteria for Operational Workflow (Phase 5), Criteria for Composition Standard (Phase 6), Criteria for Meta Composition Spec (Phase 7), Criteria for Package Assembly (Phase 8), Criteria for Promotion (Phase 9), Negative Criteria, and Self-Validation.

TC-005: Every criterion identifier (TC-NNN) is unique across the entire document -- no duplicates exist.

TC-006: Every criterion uses specific, verifiable language -- no criterion contains vague phrases such as "must work properly", "must be correct", "should be good", or "must be handled appropriately".

TC-007: Every criterion traces to a specific requirement in the input specification (WORKFLOW_SPEC_FILE) -- no criterion invents requirements absent from the spec.

TC-008: The REVIEW_TEST_CRITERIA_FILE produced by step 02 contains a structured review with explicit APPROVED or REJECTED verdict per criterion category, and REJECTED categories include specific failure reasons with criterion identifiers.

---

## Criteria for Component Schema (Phase 2)

This phase contains 2 steps: generate_component_schema (04) and gatekeep_component_schema (05). It defines the Layer 1 component schema.

TC-009: The COMPONENT_SCHEMA_FILE defines exactly 8 component types as listed in Section 2.1 of the spec: step_definition, role_policy, routing_pattern, prompt_pattern, artifact_contract, composition_standard, output_variance, domain_spec.

TC-010: Each of the 8 component types includes a purpose description that explains what the component represents in the workflow system.

TC-011: Each of the 8 component types includes a required/optional flag matching the spec table (step_definition, role_policy, routing_pattern, artifact_contract, composition_standard are required; prompt_pattern, output_variance, domain_spec are optional).

TC-012: Each of the 8 component types includes a cardinality specification matching the spec table (step_definition is "Ordered list", role_policy/routing_pattern are "Singleton per step", prompt_pattern is "Unordered set per prompt step", artifact_contract is "Unordered set", composition_standard is "Singleton", output_variance/domain_spec are "Unordered set").

TC-013: The component schema defines exactly 5 required common properties: component_id, component_type, name, version, description.

TC-014: The component_id property specifies a format of {type}-{name}-{seq} as defined in Section 2.2.

TC-015: The component_type property specifies an enum type that must be one of the 8 types defined in Section 2.1.

TC-016: Type-specific properties are defined for all 8 component types, matching the property tables in Section 2.3. The step_definition type includes: step_name, step_type, purpose, required_inputs, produces, enable_notifications, requires_human_approval_after.

TC-017: The role_policy type-specific properties include policy_name (enum with values: architect_standard, reviewer_standard, gatekeeper_standard, validation_standard, refine_standard) and assignment_rule (string).

TC-018: The routing_pattern type-specific properties include onsuccess, on_reject_refine object, max_iterations, exhausted_failure_code, and exhausted_failure_class. The on_reject_refine sub-object (Section 2.3.2) includes: step, artifact, max_iterations, exhausted_failure_code, exhausted_failure_class.

TC-019: The artifact_contract type-specific properties include artifact_key, description, filename_pattern, required, and produced_by.

TC-020: The composition_standard type-specific properties include standard_name, standard_version, component_types_defined, schema_sections, and extensibility_model, matching Section 2.3 type composition_standard.

TC-021: The output_variance type-specific properties include variance_name, variance_description, component_requirements, and output_files. The domain_spec type-specific properties include spec_type, spec_version_range, required_sections, and example_specs.

TC-022: The schema includes validation rules VR-001 through VR-014, each with a unique rule identifier and a specific verifiable rule statement. The rules cover: step name uniqueness (VR-001), valid step_type values (VR-002), valid policy_name values (VR-003), artifact key format UPPER_SNAKE_CASE with _FILE suffix (VR-004), routing completeness (VR-005), prompt pattern completeness for self_critic and self_validation (VR-006), artifact flow integrity (VR-007), composition standard completeness covering all 3 layers (VR-008), output variance feasibility (VR-009), and additional rules through VR-014 as enumerated in the spec.

TC-023 (supplement to TC-022): Each validation rule (VR-001 through VR-014) defines a condition that can be objectively checked against a component instance -- no rule uses subjective language.

TC-024: The schema includes at least one example for each component type showing a valid instance with all required properties populated, matching the example column in Section 2.3 tables.

TC-025: The GATEKEEP_COMPONENT_SCHEMA_FILE produced by step 05 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-009 through TC-024) that failed.

TC-026: The gatekeep review confirms that no component type present in the spec (Section 2.1) is absent from the generated schema.

---

## Criteria for Composition Format (Phase 3)

This phase contains 2 steps: generate_composition_format (06) and gatekeep_composition_format (07). It defines the Layer 2 composition format.

TC-027: The COMPOSITION_FORMAT_FILE defines exactly 8 binding rules matching Section 3.2 of the spec: steps, roles, routing, prompts, artifacts, standard, variances, domain_specs.

TC-028: Each binding rule specifies the binding name, component type, cardinality, required flag, and description.

TC-029: The steps binding specifies component type step_definition, cardinality "Ordered list", and required flag true.

TC-030: The roles binding specifies component type role_policy, cardinality "Singleton per step", and required flag true. The routing binding specifies component type routing_pattern, cardinality "Singleton per step", and required flag true.

TC-031: The standard binding specifies component type composition_standard, cardinality "Singleton", and required flag true. This binding represents the composition standard that the generated meta builder will use.

TC-032: The composition format defines exactly 6 workflow patterns as specified in Section 3.1.1: action_only, prompt_driven, mixed, gatekeeper_pipeline, meta_workflow_builder, meta_meta_builder.

TC-033: Each workflow pattern includes a name, description, and the step sequence it implies. The meta_meta_builder pattern is documented as NEW in v3 with its specific step sequence starting from generate_test_criteria through stepCompletion.

TC-034: The composition format defines an override mechanism (Section 3.3) that specifies how composition-time values can override schema defaults. The mechanism shows a YAML example with step_bindings, role, routing, and prompt_patterns override structure.

TC-035: The override mechanism specifies rules: every step must bind a role_policy, every step must bind a routing_pattern, prompt-driven steps must bind self_critic and self_validation patterns, and action-driven steps do not bind prompt_patterns.

TC-036: The composition format defines a placeholder resolution mechanism (Section 3.4) with exactly 3 data sources: Input Spec (WORKFLOW_SPEC_FILE, domain_name, job_prefix), Governance (BASE_COMPOSITION_STANDARD, GOVERNANCE_RUNTIME_ROOT), and Runtime (job_id, seq, workspace_root).

TC-037: The placeholder resolution mechanism specifies that placeholders in prompt templates are resolved at runtime, artifact paths are resolved via context_extensions.py, and governance paths are resolved via runtime_context module.

TC-038: The composition format defines a composition structure (Section 3.1) with 9 fields: builder_name, builder_label, job_prefix, builder_purpose, workflow_pattern, step_bindings, artifact_bindings, composition_standard_binding, output_variances. Each field specifies its type, required flag, and description.

TC-039: The composition_standard_binding section (Section 3.6) defines exactly 5 fields: standard_name, standard_version, component_types_defined, schema_sections, extensibility_model. Each field has type, required flag, and description.

TC-040: The output_variances section (Section 3.7) defines exactly 4 fields: variance_name, variance_description, component_requirements, output_files. Each field has type, required flag, and description.

TC-041: The composition format includes an example composition (Section 3.5) demonstrating builder_name, workflow_pattern, step_bindings, artifact_bindings, composition_standard_binding, and output_variances in valid YAML structure.

TC-042: The GATEKEEP_COMPOSITION_FORMAT_FILE produced by step 07 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-027 through TC-041) that failed.

---

## Criteria for Output Format (Phase 4)

This phase contains 2 steps: generate_output_format (08) and gatekeep_output_format (09). It defines the Layer 3 output format.

TC-043: The OUTPUT_FORMAT_FILE defines the 3-part output structure matching Section 4.1: Standards/COMPOSITION_STANDARD.md, Specs/{name}.md, and the workflow package (workflow.toml, context_extensions.py, actions.py, prompts/, README.md).

TC-044: The output format specifies the directory tree structure (Section 4.4) showing all required and conditional files. Conditional files .env.sample and config.json.sample are explicitly marked as conditional.

TC-045: The output format defines exactly 7 resolution rules (Section 4.2): all step_definitions expanded into workflow.toml [[step]] sections, all role_policies resolved to [step.coder] values, all routing_patterns resolved to onsuccess and [step.on_reject_refine] configurations, all prompt_patterns expanded into prompt template sections, composition standard generated as Standards/COMPOSITION_STANDARD.md, meta composition spec generated as Specs/{name}.md, and artifact paths resolved via context_extensions.py.

TC-046: Each resolution rule specifies a source (what is being resolved) and a target (what it resolves to in the output).

TC-047: The output format defines quality requirements (Section 4.3) covering: no dangling step references, no dangling artifact references, complete prompt patterns (self_critic and self_validation), valid role assignments, artifact flow integrity, composition standard completeness, output variance feasibility, and self-bootstrapping capability.

TC-048: The "no dangling step references" requirement specifies that every onsuccess and on_reject_refine step must exist in the workflow. The condition is checkable via cross-reference.

TC-049: The "no dangling artifact references" requirement specifies that every required_inputs artifact must be produced by a prior step or be an input artifact. The condition is checkable via artifact flow tracing.

TC-050: The "complete prompt patterns" requirement specifies that every prompt-driven step must have self_critic and self_validation sections in its prompt template. The condition is checkable via prompt file inspection.

TC-051: The "composition standard completeness" requirement specifies that the generated COMPOSITION_STANDARD.md must define all 3 layers (Component Schema, Composition Format, Output Format). The condition is checkable via content inspection.

TC-052: The "self-bootstrapping capability" requirement specifies that the generated meta builder should be able to process specs in its domain. The condition is checkable by verifying the meta builder's spec is in Specs/ and can be used as WORKFLOW_SPEC_FILE input.

TC-053: The GATEKEEP_OUTPUT_FORMAT_FILE produced by step 09 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-043 through TC-052) that failed.

---

## Criteria for Operational Workflow (Phase 5)

This phase contains 2 steps: generate_operational_workflow (10) and gatekeep_operational_workflow (11). It defines the complete operational workflow.

TC-054: The OPERATIONAL_WORKFLOW_FILE defines exactly 9 phases matching the phase table in Section 5.1: Foundation (TDD Loop), Component Schema, Composition Format, Output Format, Operational Workflow, Composition Standard, Meta Composition Spec, Package Assembly, Promotion.

TC-055: Each phase has a unique phase number (1 through 9) and a clearly stated purpose matching the spec.

TC-056: The operational workflow defines all 21 steps matching the step sequence derived from Section 5.3: steps 01 through 21, including the conditional steps 03 (refine_test_criteria) and the refine step in Phase 8.

TC-057: Each step definition includes: step name, step type (prompt or action), the artifact it produces, and its routing behavior.

TC-058: The prompt-type steps are correctly identified: generate_test_criteria (01), review_test_criteria (02), refine_test_criteria (03), generate_component_schema (04), generate_composition_format (06), generate_output_format (08), generate_operational_workflow (10), generate_composition_standard (12), generate_meta_composition_spec (14), generate_package (15), review_package (19), and refine_package (conditional in Phase 8).

TC-059: The action-type steps are correctly identified: gatekeep_component_schema (05), gatekeep_composition_format (07), gatekeep_output_format (09), gatekeep_operational_workflow (11), gatekeep_composition_standard (13), validate_package_deterministic, gatekeep_package (18), promote_workflow_package, and step_completion.

TC-060: Each gatekeep step is an action-type step that produces a GATEKEEP_* artifact with an APPROVED or REJECTED verdict.

TC-061: The routing from each gatekeep step is defined: APPROVED routes to the next phase's first step, REJECTED routes to the previous generate step in the same phase.

TC-062: The routing from review_test_criteria (02) is defined: APPROVED routes to Phase 2 (generate_component_schema), REJECTED routes to refine_test_criteria (03).

TC-063: The refine step (03) is conditional -- it executes only when review_test_criteria returns REJECTED. The refine step routes back to review_test_criteria after refinement.

TC-064: The routing from review_package is defined: APPROVED routes to promote_workflow_package, REJECTED routes to refine_package (conditional).

TC-065: The refine_package step is conditional and routes back to review_package or gatekeep_package after refinement.

TC-066: The operational workflow includes the step_completion step as the final action-type step in Phase 9. Step completion records the final outcome and produced artifacts.

TC-067: The artifact flow is consistent: every artifact consumed by a step is either the input artifact (WORKFLOW_SPEC_FILE) or produced by a preceding step.

TC-068: The WORKFLOW_SPEC_FILE is declared as the sole input artifact (Section 5.2) and is available to all steps that reference it in their required_inputs.

TC-069: Each phase's output artifacts are available as context to all subsequent phases. The OPERATIONAL_WORKFLOW_FILE documents which artifacts from each phase feed into later phases.

TC-070: The action steps section (Section 5.4) defines exactly 2 custom action steps: validate_package_deterministic and promote_workflow_package. Each action step has a clearly documented purpose and behavior.

TC-071: The validate_package_deterministic action is documented to check: workflow.toml syntax, step references, artifact references, role policies, prompt file existence, composition standard file existence and well-formedness, and meta composition spec file existence and well-formedness.

TC-072: The promote_workflow_package action is documented to copy: workflow.toml, context_extensions.py, actions.py, prompts/, README.md, .env.sample (if present), config.json.sample (if present), Standards/COMPOSITION_STANDARD.md, and Specs/ directory (if present).

TC-073: The domain-specific requirements (Section 5.5) are all reflected in the operational workflow: self-bootstrapping, three outputs, dynamic component discovery, output variances, folder-based domain separation, consistent standard filename, TDD loop universal, gatekeeper pattern, action reuse, and self-critic/self-validation.

TC-074: The GATEKEEP_OPERATIONAL_WORKFLOW_FILE produced by step 11 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-054 through TC-073) that failed.

---

## Criteria for Composition Standard (Phase 6)

This phase contains 2 steps: generate_composition_standard (12) and gatekeep_composition_standard (13). This is a v3 innovation -- every generated meta builder has its own composition standard.

TC-075: The COMPOSITION_STANDARD_FILE defines a composition standard with a top-level structure including YAML frontmatter and a body with component type definitions.

TC-076: The composition standard includes a standard_name field that uniquely identifies the standard for the generated meta builder's domain (e.g., "WORKFLOW_BUILDER_STANDARD").

TC-077: The composition standard includes a standard_version field with a semantic version string (MAJOR.MINOR.PATCH format).

TC-078: The composition standard defines all component types from Phase 2's output (8 types minimum from Section 2.1), each in a subsection with heading format "#### Type N: type_name".

TC-079: The composition standard includes a component_types_defined field (array, required) listing all component types the generated meta builder's domain uses.

TC-080: The composition standard includes a schema_sections field (array, required) listing the sections that generated schemas must contain: Component Schema (Layer 1), Composition Format (Layer 2), Output Format (Layer 3).

TC-081: The composition standard includes an extensibility_model section (string, required) that describes how new component types can be added without breaking existing compositions.

TC-082: The composition standard is self-describing: it can be used independently without requiring external documents to understand the meta builder's component schema, composition format, and output format.

TC-083: The GATEKEEP_COMPOSITION_STANDARD_FILE produced by step 13 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-075 through TC-082) that failed.

---

## Criteria for Meta Composition Spec (Phase 7)

This phase contains 1 step: generate_meta_composition_spec (14). This is a v3 innovation -- the generated meta builder carries its own spec in Specs/.

TC-084: The META_COMPOSITION_SPEC_FILE defines a meta composition specification with exactly 5 sections.

TC-085: Section 1 of the meta composition spec is a Domain Overview that includes domain name, label, job prefix, description, purpose, and three-part output definition.

TC-086: Section 2 of the meta composition spec covers Component Schema (Layer 1) requirements, defining all 8 component types, common properties, type-specific properties, and validation rules from Phase 2.

TC-087: Section 3 of the meta composition spec covers Composition Format (Layer 2) requirements, defining binding rules, workflow patterns, override mechanism, and placeholder resolution from Phase 3.

TC-088: Section 4 of the meta composition spec covers Output Format (Layer 3) requirements, defining the 3-part output structure, resolution rules, and quality requirements from Phase 4.

TC-089: Section 5 of the meta composition spec covers Operational Requirements, including the 9 phases, step sequence, action steps, artifact declarations, and domain-specific requirements from Phase 5.

TC-090: The meta composition spec is self-bootstrapping -- it contains enough information for the builder to process it as WORKFLOW_SPEC_FILE input and generate the next version. Every section referenced in the spec can be resolved from the spec itself without external dependencies.

TC-091: The GATEKEEP review or quality check of the meta composition spec verifies that all 5 sections are present, each section's content is consistent with the corresponding phase output, and the self-bootstrapping invariant holds.

---

## Criteria for Package Assembly (Phase 8)

This phase contains steps: generate_package (15), validate_package_deterministic, gatekeep_package (18), review_package (19), and refine_package (conditional). It produces the executable workflow package.

TC-092: The WORKFLOW_MANIFEST_FILE (workflow.toml) produced by generate_package is valid TOML and parses without errors.

TC-093: The workflow.toml declares all steps in the correct order matching the step sequence, with correct step names, types, artifact keys, and routing.

TC-094: The workflow.toml declares all input artifacts (WORKFLOW_SPEC_FILE) in a required_inputs section.

TC-095: The workflow.toml declares all output artifacts in a produces section for each step, matching the artifact table in Section 5.3.

TC-096: The WORKFLOW_EXTENSIONS_FILE (context_extensions.py) produced by generate_package is syntactically valid Python that parses without errors.

TC-097: The context_extensions.py includes artifact key registration via a register_artifact_keys() function or equivalent, mapping each artifact key to its resolved file path.

TC-098: The context_extensions.py artifact key coverage is complete -- every artifact key declared in workflow.toml has a corresponding path resolution in context_extensions.py.

TC-099: The WORKFLOW_ACTIONS_FILE (actions.py) produced by generate_package is syntactically valid Python that parses without errors.

TC-100: The actions.py implements all action steps declared in workflow.toml: validate_package_deterministic and promote_workflow_package.

TC-101: The validate_package_deterministic action implements checks for: TOML parse validity, Python syntax validity, artifact binding consistency, action step implementation completeness, prompt file existence, prompt placeholder vs required_inputs consistency, context_extensions.py artifact key coverage, composition standard file existence, and meta composition spec file existence.

TC-102: All prompt template files (prompts/NN_{step_name}.txt) exist for every prompt-type step. The NN prefix is a zero-padded step number.

TC-103: Each {PLACEHOLDER} in each prompt template is declared in the corresponding step's required_inputs or produces in workflow.toml.

TC-104: Every prompt-driven step's template includes self-critic and self-validation sections as required by the spec Section 5.5.

TC-105: The WORKFLOW_PROMPTS_INDEX_FILE (prompts_index.json) is valid JSON and lists all prompt files with their associated step names and artifact keys.

TC-106: The WORKFLOW_README_FILE (README.md) exists and describes the workflow's purpose, inputs, outputs, how to invoke it, and the 3-part output structure (Standards/, Specs/, workflow package).

TC-107: The generate_package prompt template uses {DISCOVERED_COMPONENT_TYPES} or equivalent dynamic reference rather than hardcoded component type lists, supporting the dynamic component discovery requirement from Section 5.5.

TC-108: Both generate_package and refine_package steps (if present) declare STANDARDS_COMPOSITION_STANDARD_FILE in their produces sections, ensuring the composition standard is properly tracked.

TC-109: The VALIDATION_REPORT_FILE produced by validate_package_deterministic lists each check performed, its pass/fail status, and details for any failures.

TC-110: The GATEKEEP_PACKAGE_FILE produced by gatekeep_package contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-092 through TC-109) that failed.

TC-111: The REVIEW_FILE_SUGGESTED produced by review_package contains a structured quality review with explicit feedback on completeness, correctness, and adherence to the spec.

TC-112: The refine_package step (conditional) produces corrections targeting only the criteria that failed in the review, without introducing scope changes.

TC-113: The generated package includes the Standards/ directory containing COMPOSITION_STANDARD.md as Part 1 of the 3-part output.

TC-114: The generated package includes the Specs/ directory containing the meta composition spec as Part 2 of the 3-part output.

TC-115: The folder-based domain separation is maintained: each meta builder has its own folder with Standards/ and Specs/ subdirectories alongside the workflow package files.

TC-116: The composition standard filename is always COMPOSITION_STANDARD.md (consistent naming per Section 5.5).

---

## Criteria for Promotion (Phase 9)

This phase contains steps: promote_workflow_package and step_completion.

TC-117: The promote_workflow_package action copies workflow.toml, context_extensions.py, actions.py (if exists), README.md, and prompts/ directory to the target workflows/ directory.

TC-118: The promote_workflow_package action copies the Standards/ directory including COMPOSITION_STANDARD.md to the target.

TC-119: The promote_workflow_package action copies the Specs/ directory (if present) to the target, preserving the embedded builder spec.

TC-120: The promote_workflow_package action copies conditional files (.env.sample, config.json.sample) only if they exist in the source.

TC-121: The step_completion step records the final outcome of the workflow execution, including success status and a summary of all produced artifacts.

TC-122: The promoted directory structure matches the expected layout: {builder_name}/workflow.toml, {builder_name}/context_extensions.py, {builder_name}/actions.py, {builder_name}/README.md, {builder_name}/prompts/, {builder_name}/Standards/COMPOSITION_STANDARD.md, {builder_name}/Specs/.

---

## Negative Criteria

These criteria define what MUST NOT appear in any output artifact. Violation of any negative criterion is an automatic rejection.

TC-123: No output file contains non-ASCII characters. All files must use ASCII-only content. No em-dashes, no curly quotes, no Unicode characters.

TC-124: No output file contains a dangling reference -- every artifact key reference ({ARTIFACT_KEY}) in a prompt template must correspond to a declared artifact in the step's required_inputs or produces in workflow.toml.

TC-125: No output file contains scope invention -- every requirement, component type, binding rule, or step in the output must trace back to the input specification (WORKFLOW_SPEC_FILE). No new component types, patterns, or phases may be introduced beyond what the spec defines.

TC-126: No YAML frontmatter block is missing any mandatory field specified for that document type.

TC-127: No output file contains vague criteria or requirements such as "must work properly", "must be correct", "should handle edge cases", or "must be robust".

TC-128: No output file contains resolved filesystem paths to governance or platform documents. Only filenames (e.g., METADATA_STANDARD.md) are permitted, not full paths.

TC-129: No output file redefines, contradicts, or extends Layer 1 (governance) or Layer 2 (platform constitution) content. These layers are read-only authority.

---

## Self-Validation

These criteria verify the completeness and internal consistency of the test criteria document itself.

TC-130: The test criteria document covers all 9 phases defined in the specification (Section 5.1): Foundation, Component Schema, Composition Format, Output Format, Operational Workflow, Composition Standard, Meta Composition Spec, Package Assembly, and Promotion.

TC-131: The test criteria document covers all 21 steps defined in the workflow: every step has at least one criterion that verifies its output or behavior.

TC-132: The test criteria document includes criteria for both v3 innovations: the Composition Standard (Phase 6, TC-075 through TC-083) and the Meta Composition Spec (Phase 7, TC-084 through TC-091).

TC-133: Every criterion (TC-001 through TC-129) is independently verifiable by a gatekeeper. Each criterion states a specific, checkable condition -- the gatekeeper can verify it by examining the produced artifact and comparing it against the input specification, without needing additional context.

TC-134: The total_criteria_count in the YAML frontmatter equals the actual count of TC-NNN entries in the document body. This self-referential check ensures the metadata is consistent with content.

End of Test Criteria Document
