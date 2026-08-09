---
doc_type: "test_criteria"
lifecycle_status: "draft"
domain: "workflow_builder"
total_criteria_count: 125
---

# Test Criteria for Workflow Builder v3 Meta-Meta Builder

## Introduction

### Scope

This document defines the acceptance criteria for the Workflow Builder v3 meta-meta builder workflow. These criteria apply to every artifact produced during the 9-phase, 22-step execution of workflow_builder_v3. Each criterion is specific, verifiable, and traceable to the composition system specification provided as input (WORKFLOW_SPEC_FILE).

### Purpose

The criteria serve three purposes:

1. Gatekeep decisions at each phase boundary -- the gatekeeper reviews use these criteria to approve or reject artifacts.
2. Reviewer guidance -- the reviewer uses these criteria to produce actionable feedback.
3. Refinement targeting -- when an artifact is rejected, the refine step uses failed criteria to scope the correction.

### Applicability

All criteria in this document apply to the Workflow Builder v3 workflow. The input specification (workflow_builder_v4.md) describes the requirements of the generated meta builder. The criteria verify that v3 correctly processes that specification into the required 3-part output.

### Structure

- TC-001 through TC-008: Foundation Phase (Phase 1)
- TC-009 through TC-022: Component Schema (Phase 2)
- TC-023 through TC-038: Composition Format (Phase 3)
- TC-039 through TC-052: Output Format (Phase 4)
- TC-053 through TC-068: Operational Workflow (Phase 5)
- TC-069 through TC-075: Composition Standard (Phase 6)
- TC-076 through TC-081: Meta Composition Spec (Phase 7)
- TC-082 through TC-106: Package Assembly (Phase 8)
- TC-107 through TC-113: Promotion (Phase 9)
- TC-114 through TC-120: Negative Criteria
- TC-121 through TC-125: Self-Validation

---

## Criteria for Foundation Phase (Phase 1)

This phase contains 3 steps: generate_test_criteria (01), review_test_criteria (02), and refine_test_criteria (03, conditional). The phase produces the acceptance criteria document that all subsequent phases are measured against.

TC-001: The generated TEST_CRITERIA_FILE exists at the path declared in workflow.toml for the TEST_CRITERIA_FILE artifact key.

TC-002: The TEST_CRITERIA_FILE contains YAML frontmatter with the following mandatory fields: doc_type set to "test_criteria", lifecycle_status, domain set to "workflow_builder", and total_criteria_count.

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

TC-014: The component schema defines exactly 3 optional common properties: duration_range, platforms, tags.

TC-015: Type-specific properties are defined for each component type where the spec indicates distinguishing properties beyond the common set.

TC-016: The schema includes validation rules VR-001 through VR-016, each with a unique rule identifier and a specific verifiable rule statement.

TC-017: Each validation rule (VR-001 through VR-016) defines a condition that can be objectively checked against a component instance -- no rule uses subjective language.

TC-018: VR-015 verifies that the WORKFLOW_SPEC_FILE artifact key is declared in the workflow package. The rule specifies a checkable condition (presence of WORKFLOW_SPEC_FILE declaration) and a clear pass/fail outcome.

TC-019: VR-016 verifies that STANDARDS_COMPOSITION_STANDARD_FILE is declared in the produces section of both the generate_package step and the refine_package step in workflow.toml. The rule specifies both steps must declare this artifact and defines failure as either step omitting it.

TC-020: The schema includes at least one example for each component type showing a valid instance with all required properties populated.

TC-021: The GATEKEEP_COMPONENT_SCHEMA_FILE produced by step 05 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-009 through TC-020) that failed.

TC-022: The gatekeep review confirms that no component type present in the spec (Section 2.1) is absent from the generated schema.

---

## Criteria for Composition Format (Phase 3)

This phase contains 2 steps: generate_composition_format (06) and gatekeep_composition_format (07). It defines the Layer 2 composition format.

TC-023: The COMPOSITION_FORMAT_FILE defines exactly 9 binding rules matching Section 3.2 of the spec.

TC-024: Each binding rule specifies the binding name, component type, cardinality, required flag, and description.

TC-025: The binding rules include a self_bootstrap binding with component type domain_spec, cardinality Singleton, and required flag set to true, matching the spec Section 3.2 addition.

TC-026: The composition format defines a self_bootstrap_binding section matching spec Section 3.4, containing exactly four fields: bootstrap_spec_key, bootstrap_spec_target, bootstrap_version, and next_version_pattern. Each field has a type, required flag, and description.

TC-027: The composition format defines exactly 6 workflow patterns as specified in Section 3.3, including the meta_meta_builder pattern.

TC-028: Each workflow pattern includes a name, description of when to use it, and the step sequence it implies.

TC-029: The composition format defines an override mechanism that specifies how composition-time values can override schema defaults, including precedence rules.

TC-030: The composition format defines a placeholder resolution mechanism that specifies how {PLACEHOLDER} tokens in templates are resolved at composition time.

TC-031: The placeholder resolution mechanism identifies exactly 4 data sources for resolution as specified in the spec: Step Metadata, Composition Context, Standards, and Discovery.

TC-032: The Discovery data source includes DISCOVERED_COMPONENT_TYPES and COMPOSITION_STANDARD_PATH as resolvable values, matching spec Section 3.5.

TC-033: The composition format defines ordering rules for step_bindings, specifying how the ordered list of steps determines execution sequence.

TC-034: The composition format includes a composition structure table matching Section 3.1 of the spec, with fields: builder_name, builder_label, job_prefix, builder_purpose, workflow_pattern, step_bindings, artifact_bindings, composition_standard_binding, self_bootstrap_binding, output_variances.

TC-035: Each field in the composition structure specifies its type, required flag, and description.

TC-036: The bootstrap chain integrity is verifiable: the composition structure specifies that the embedded spec in Specs/ must be content-identical to the input WORKFLOW_SPEC_FILE, as defined in spec Section 7.

TC-037: The GATEKEEP_COMPOSITION_FORMAT_FILE produced by step 07 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-023 through TC-036) that failed.

TC-038: The composition format verifies that both generate_package and refine_package steps declare STANDARDS_COMPOSITION_STANDARD_FILE in their produces sections of workflow.toml, as required by spec Section 5.7.

---

## Criteria for Output Format (Phase 4)

This phase contains 2 steps: generate_output_format (08) and gatekeep_output_format (09). It defines the Layer 3 output format.

TC-039: The OUTPUT_FORMAT_FILE defines the 3-part output structure matching Section 4.1: Standards/COMPOSITION_STANDARD.md, Specs/{builder_name}.md, and the workflow package directory (workflow.toml, context_extensions.py, actions.py, prompts/, README.md).

TC-040: The output format specifies the directory tree structure showing all required and conditional files (.env.sample and config.json.sample marked as conditional).

TC-041: The output format defines exactly 9 resolution rules (RR-001 through RR-009) as specified in the spec.

TC-042: Each resolution rule (RR-001 through RR-009) specifies a source and a target, defining how a placeholder is resolved to an output artifact.

TC-043: RR-008 specifies that self_bootstrap_binding resolves to Specs/{builder_name}.md, matching spec Section 4.3. The rule defines the source (self_bootstrap_binding) and the target path pattern.

TC-044: RR-009 specifies that DISCOVERED_COMPONENT_TYPES resolves to all prompt templates, matching spec Section 4.3. The rule defines the source (DISCOVERED_COMPONENT_TYPES) and the target (prompt template files).

TC-045: The output format defines quality requirements QR-001 through QR-012 as specified in the spec.

TC-046: Each quality requirement (QR-001 through QR-012) specifies a verifiable condition and a severity level.

TC-047: QR-009 verifies that a Standards/ directory exists in the output. The condition is checkable (directory presence) and the severity level is defined.

TC-048: QR-010 verifies that a Specs/ directory exists and contains at least one .md file. The condition is checkable and the severity level is defined.

TC-049: QR-011 verifies that all placeholders in prompt templates are declared in the corresponding step's required_inputs or produces. The condition is checkable via cross-reference and the severity level is defined.

TC-050: QR-012 verifies that STANDARDS_COMPOSITION_STANDARD_FILE is declared in the produces of both generate_package and refine_package steps. The condition is checkable and the severity level is defined.

TC-051: The output format includes a promotion contract section specifying which source files map to which target paths in the workflows/ directory.

TC-052: The promotion contract distinguishes mandatory files (workflow.toml, context_extensions.py, README.md, prompts/) from conditional files (.env.sample, config.json.sample, actions.py).

TC-053: The output format includes a file naming convention for prompt templates matching the pattern NN_{step_name}.txt where NN is a zero-padded step number.

TC-054: The GATEKEEP_OUTPUT_FORMAT_FILE produced by step 09 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-039 through TC-053) that failed.

---

## Criteria for Operational Workflow (Phase 5)

This phase contains 2 steps: generate_operational_workflow (10) and gatekeep_operational_workflow (11). It defines the complete operational workflow.

TC-055: The OPERATIONAL_WORKFLOW_FILE defines exactly 9 phases matching the phase table in Section 5.1: Foundation, Component Schema, Composition Format, Output Format, Operational Workflow, Composition Standard, Meta Composition Spec, Package Assembly, Promotion.

TC-056: Each phase has a unique phase number (1 through 9) and a clearly stated purpose.

TC-057: The operational workflow defines all 22 steps matching the step sequence in Section 6: steps 01 through 22, including the conditional steps 03 (refine_test_criteria) and 20 (refine_package), and step 22 (step_completion).

TC-058: Each step definition includes: step name, step number, step type (prompt or action), the artifact it produces, and its routing behavior.

TC-059: Each step is classified as either prompt-type or action-type. The 12 prompt-type steps are: 01 (generate_test_criteria), 02 (review_test_criteria), 03 (refine_test_criteria), 04 (generate_component_schema), 06 (generate_composition_format), 08 (generate_output_format), 10 (generate_operational_workflow), 12 (generate_composition_standard), 14 (generate_meta_composition_spec), 15 (generate_package), 19 (review_package), 20 (refine_package). The 10 action-type steps are: 05 (gatekeep_component_schema), 07 (gatekeep_composition_format), 09 (gatekeep_output_format), 11 (gatekeep_operational_workflow), 13 (gatekeep_composition_standard), 16 (embed_builder_spec), 17 (validate_package_deterministic), 18 (gatekeep_package), 21 (promote_workflow_package), 22 (step_completion).

TC-060: Each gatekeep step (05, 07, 09, 11, 13, 18) is an action-type step that produces a GATEKEEP_* artifact with an APPROVED or REJECTED verdict.

TC-061: The routing from each gatekeep step is defined: APPROVED routes to the next phase's first step, REJECTED routes to the previous generate step in the same phase.

TC-062: The routing from review_test_criteria (02) is defined: APPROVED routes to Phase 2, REJECTED routes to refine_test_criteria (03).

TC-063: The routing from review_package (19) is defined: APPROVED routes to promote_workflow_package (21), REJECTED routes to refine_package (20).

TC-064: The refine steps (03 and 20) are conditional -- they execute only when the preceding review step returns REJECTED.

TC-065: The operational workflow includes step 22 (step_completion) as an action-type step in Phase 9. Step 22 is the final step in the sequence and its routing behavior is defined.

TC-066: The bootstrap chain invariant is preserved in the operational workflow: step 16 (embed_builder_spec) copies the input WORKFLOW_SPEC_FILE into Specs/{builder_name}.md, and the workflow verifies that this embedded spec is content-identical to the input, as specified in spec Section 7.

TC-067: The artifact flow is consistent: every artifact consumed by a step is either an input declared in the workflow or produced by a preceding step.

TC-068: The WORKFLOW_SPEC_FILE is declared as an input to the workflow and is available to all steps that reference it.

TC-069: Each phase's output artifacts are available as context to all subsequent phases.

TC-070: The GATEKEEP_OPERATIONAL_WORKFLOW_FILE produced by step 11 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-055 through TC-069) that failed.

---

## Criteria for Composition Standard (Phase 6)

This phase contains 2 steps: generate_composition_standard (12) and gatekeep_composition_standard (13). This is a v3 innovation.

TC-071: The COMPOSITION_STANDARD_FILE defines a composition standard with the following top-level structure: a YAML frontmatter block containing standard_name, standard_version, component_type_count, and a body with component type definitions.

TC-072: The composition standard includes a standard_name field that uniquely identifies the standard (e.g., "WORKFLOW_BUILDER_STANDARD").

TC-073: The composition standard includes a standard_version field with a semantic version string (e.g., "1.0.0").

TC-074: The composition standard defines all component types from Phase 2's output (8 types minimum), each in a subsection with heading format "#### Type N: type_name".

TC-075: The composition standard includes a schema_sections field or equivalent listing the sections that generated schemas must contain.

TC-076: The composition standard includes an extensibility_model section that describes how new component types can be added without breaking existing compositions.

TC-077: The GATEKEEP_COMPOSITION_STANDARD_FILE produced by step 13 contains an explicit APPROVED or REJECTED verdict and, if REJECTED, lists specific criterion identifiers (from TC-071 through TC-076) that failed.

---

## Criteria for Meta Composition Spec (Phase 7)

This phase contains 1 step: generate_meta_composition_spec (14). This is a v3 innovation.

TC-078: The META_COMPOSITION_SPEC_FILE defines a meta composition specification with exactly 5 sections as required by the spec.

TC-079: Section 1 of the meta composition spec is a Domain Overview that includes domain name, label, job prefix, description, purpose, and three-part output definition.

TC-080: Section 2 of the meta composition spec covers Component Schema requirements, referencing or reproducing the 8 component types and validation rules from Phase 2.

TC-081: Section 3 of the meta composition spec covers Composition Format requirements, referencing or reproducing the binding rules, workflow patterns, and placeholder resolution from Phase 3.

TC-082: Section 4 of the meta composition spec covers Output Format requirements, referencing or reproducing the 3-part output structure and resolution rules from Phase 4.

TC-083: Section 5 of the meta composition spec covers Operational Requirements, including the 9 phases, step sequence, action steps, and artifact declarations. The spec must be self-bootstrapping -- it must contain enough information for the builder to process it as input and generate the next version.

---

## Criteria for Package Assembly (Phase 8)

This phase contains 6 steps: generate_package (15), embed_builder_spec (16), validate_package_deterministic (17), gatekeep_package (18), review_package (19), and refine_package (20, conditional).

TC-084: The WORKFLOW_MANIFEST_FILE (workflow.toml) produced by step 15 is valid TOML and parses without errors.

TC-085: The workflow.toml declares all steps in the correct order matching the step sequence from Section 6, with correct step names, types, artifact keys, and routing.

TC-086: The workflow.toml declares all input artifacts in a required_inputs section matching Section 5.6.

TC-087: The workflow.toml declares all output artifacts in a produces section for each step, matching Section 5.7.

TC-088: The WORKFLOW_EXTENSIONS_FILE (context_extensions.py) produced by step 15 is syntactically valid Python that parses without errors.

TC-089: The context_extensions.py includes a discover_component_types function that parses a COMPOSITION_STANDARD.md file path and returns a list of component type names.

TC-090: The context_extensions.py artifact key coverage is complete -- every artifact key declared in workflow.toml has a corresponding path resolution in context_extensions.py.

TC-091: The WORKFLOW_ACTIONS_FILE (actions.py) produced by step 15 is syntactically valid Python that parses without errors.

TC-092: The actions.py implements all action steps declared in workflow.toml: validate_package_deterministic, embed_builder_spec, and promote_workflow_package.

TC-093: The validate_package_deterministic action implements all 11 validation checks listed in Section 5.3, numbered 1 through 11.

TC-094: Validation check 10 verifies that the Specs/ directory exists and contains at least one .md file.

TC-095: The embedded spec file in Specs/{builder_name}.md is content-identical to the input WORKFLOW_SPEC_FILE, verifying bootstrap chain integrity per spec Section 7.

TC-096: Validation check 11 verifies bidirectional placeholder consistency: every {PLACEHOLDER} in a prompt is declared in the step's required_inputs or produces, AND every artifact in the step's required_inputs/produces that looks like a placeholder IS referenced in the prompt.

TC-097: The embed_builder_spec action copies the input WORKFLOW_SPEC_FILE into the output's Specs/ directory, creating the Specs/ directory if it does not exist.

TC-098: The promote_workflow_package action copies all 3 parts of the output: Standards/ directory, Specs/ directory, and workflow package files.

TC-099: The promote_workflow_package action rejects with a clear error if Standards/ or Specs/ is missing from the output.

TC-100: All prompt template files (prompts/NN_{step_name}.txt) exist for every prompt-type step, and each {PLACEHOLDER} in each prompt is declared in the corresponding step's required_inputs or produces in workflow.toml.

TC-101: The generate_package prompt template contains the {DISCOVERED_COMPONENT_TYPES} placeholder and does NOT contain hardcoded component type lists. The generate_meta_composition_spec prompt template also uses {DISCOVERED_COMPONENT_TYPES} instead of hardcoded type lists, matching spec Section 5.5.

TC-102: Both the generate_package step and the refine_package step declare STANDARDS_COMPOSITION_STANDARD_FILE in their produces sections of workflow.toml, matching spec Section 5.7 and VR-016.

TC-103: The WORKFLOW_README_FILE (README.md) exists and describes the workflow's purpose, inputs, outputs, and how to invoke it.

TC-104: The workflow.toml includes step 22 (step_completion) as an action-type step in Phase 9, with correct artifact keys and routing behavior.

TC-105: The workflow.toml declares VR-015 and VR-016 validation rules in the appropriate section, referencing WORKFLOW_SPEC_FILE and STANDARDS_COMPOSITION_STANDARD_FILE respectively.

TC-106: The workflow.toml declares all 9 binding rules including the self_bootstrap binding with component type domain_spec, matching the composition format output from Phase 3.

---

## Criteria for Promotion (Phase 9)

This phase contains 2 steps: promote_workflow_package (21) and step_completion (22).

TC-107: The WORKFLOW_PACKAGE_DIR_FILE artifact records the absolute path to the promoted workflow package directory under workflows/.

TC-108: The step_completion action (step 22) records the final outcome of the workflow execution, including success status and a summary of produced artifacts.

TC-109: The promoted directory contains workflow.toml at its root.

TC-110: The promoted directory contains context_extensions.py and actions.py at its root.

TC-111: The promoted directory contains a prompts/ subdirectory with all prompt template files.

TC-112: The promoted directory contains a Standards/ subdirectory with COMPOSITION_STANDARD.md.

TC-113: The promoted directory contains a Specs/ subdirectory with at least one .md file (the embedded builder spec).

---

## Negative Criteria

These criteria define what MUST NOT appear in any output artifact. Violation of any negative criterion is an automatic rejection.

TC-114: No output file contains non-ASCII characters. All files must use ASCII-only content. No em-dashes, no curly quotes, no Unicode characters.

TC-115: No output file contains a dangling reference -- every artifact key reference ({ARTIFACT_KEY}) in a prompt template must correspond to a declared artifact in the step's required_inputs or produces in workflow.toml.

TC-116: No output file contains scope invention -- every requirement, component type, binding rule, or step in the output must trace back to the input specification (WORKFLOW_SPEC_FILE). No new component types, patterns, or phases may be introduced beyond what the spec defines.

TC-117: No YAML frontmatter block is missing any mandatory field specified for that document type.

TC-118: No output file contains vague criteria or requirements such as "must work properly", "must be correct", "should handle edge cases", or "must be robust".

TC-119: No output file contains resolved filesystem paths to governance or platform documents. Only filenames (e.g., METADATA_STANDARD.md) are permitted, not full paths.

TC-120: No output file redefines, contradicts, or extends Layer 1 (governance) or Layer 2 (platform constitution) content. These layers are read-only.

---

## Self-Validation

These criteria verify the completeness and internal consistency of the test criteria document itself.

TC-121: The test criteria document covers all 9 phases defined in the specification (Section 5.1): Foundation, Component Schema, Composition Format, Output Format, Operational Workflow, Composition Standard, Meta Composition Spec, Package Assembly, and Promotion.

TC-122: The test criteria document covers all 22 steps defined in the step sequence (Section 6): every step from 01 to 22 has at least one criterion that verifies its output.

TC-123: The test criteria document includes criteria for both v3 innovations: the Composition Standard (Phase 6, TC-071 through TC-077) and the Meta Composition Spec (Phase 7, TC-078 through TC-083).

TC-124: Every criterion (TC-001 through TC-120) is independently verifiable -- a gatekeeper can check each criterion without needing additional context beyond the input spec and the produced artifact.

TC-125: The total_criteria_count in the YAML frontmatter equals the actual count of TC-NNN entries in the document body. This self-referential check ensures the metadata is consistent with content.

End of Test Criteria Document
