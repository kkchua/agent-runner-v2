---
doc_type: "test_criteria"
lifecycle_status: "draft"
effective_version: "WBUILD2-4qpaocdy"
job_id: "WBUILD2-4qpaocdy"
spec_source: "workflow_builder_v3.md"
composition_standard: "COMPOSITION_SYSTEM_STANDARD.md"
architecture_reference: "META_WORKFLOW_BUILDER_ARCHITECTURE.md"
---

# Test Criteria: Composition System Workflow Builder v2

## 1. Spec Objective Summary

The composition system workflow builder must generate a meta-meta workflow that produces three outputs from a composition system specification: (1) a Standards directory containing a COMPOSITION_STANDARD.md that defines the component schema, composition format, and output format for a target domain; (2) a Specs directory accepting user-provided composition specs; and (3) an executable workflow package (workflow.toml, prompts/, actions.py, context_extensions.py, README.md) that implements the composition system's three-layer architecture (Component Library, Composition Definitions, Resolved Outputs). The domain is workflow_builder -- the generated workflow is itself a composition system that can build meta builders with their own composition standards, enabling extensibility and self-bootstrapping. The end-to-end transformation reads a composition system spec defining component types, composition rules, and output structures, and produces a complete workflow package that dynamically discovers components, resolves compositions by reference, and assembles self-contained outputs.

---

## 2. Criteria for generate_component_schema (Phase 2 - Layer 1 Quality)

### 2.1 Component Type Completeness

1. TC-CS-001: The component schema MUST define exactly 8 component types as specified in workflow_builder_v3.md Section 2.1: step_definition, role_policy, routing_pattern, prompt_pattern, artifact_contract, composition_standard, output_variance, domain_spec.
2. TC-CS-002: Each component type MUST be listed with its Purpose, Required status, and Cardinality matching the spec table (e.g., step_definition is Required with Ordered list cardinality, prompt_pattern is Optional with Unordered set per prompt-driven step).
3. TC-CS-003: MUST NOT omit any component type from the spec. Count the types defined and verify the count equals 8.
4. TC-CS-004: MUST NOT invent component types not listed in the spec Section 2.1 table.

### 2.2 Common Properties

5. TC-CS-005: The schema MUST define all 5 common properties shared by all components: component_id (string, required), component_type (enum, required), name (string, required), version (string, required), description (string, required).
6. TC-CS-006: Each common property MUST specify its type, required status, and description matching the spec Section 2.2 table.
7. TC-CS-007: The component_id format MUST be documented as {type}-{name}-{seq} per spec Section 2.2.
8. TC-CS-008: The component_type enum MUST be documented as one of the 8 types from Section 2.1.

### 2.3 Type-Specific Properties

9. TC-CS-009: The step_definition type MUST define these properties: step_name (string, required), step_type (enum: prompt/action, required), purpose (string, required), required_inputs (array, optional), produces (array, required), enable_notifications (boolean, required), requires_human_approval_after (boolean, required).
10. TC-CS-010: The role_policy type MUST define these properties: policy_name (enum with 5 values: architect_standard, reviewer_standard, gatekeeper_standard, validation_standard, refine_standard, required), assignment_rule (string, required).
11. TC-CS-011: The routing_pattern type MUST define these properties: onsuccess (string, required), on_reject_refine (object, optional), max_iterations (integer, optional), exhausted_failure_code (string, optional), exhausted_failure_class (string, optional).
12. TC-CS-012: The on_reject_refine sub-structure MUST define: step (string, required), artifact (string, required), max_iterations (integer, required), exhausted_failure_code (string, required), exhausted_failure_class (string, required).
13. TC-CS-013: The prompt_pattern type MUST define: pattern_name (enum with 7 values: self_critic, self_validation, context_verification, reference_inputs, generation_tasks, forbidden_content, output_instructions, required), sections (array, required).
14. TC-CS-014: The artifact_contract type MUST define: artifact_key (string, required), description (string, required), filename_pattern (string, optional), required (boolean, required), produced_by (string, optional).
15. TC-CS-015: The composition_standard type MUST define: standard_name (string, required), standard_version (string, required), component_types_defined (array, required), schema_sections (array, required), extensibility_model (string, required).
16. TC-CS-016: The output_variance type MUST define: variance_name (string, required), variance_description (string, required), component_requirements (array, required), output_files (array, required).
17. TC-CS-017: The domain_spec type MUST define: spec_type (string, required), spec_version_range (string, required), required_sections (array, required), example_specs (array, optional).
18. TC-CS-018: Each type-specific property MUST include name, type, required/optional status, description, and an example value matching the spec Section 2.3 tables.

### 2.4 Validation Rules

19. TC-CS-019: The schema MUST include validation rules for step_name uniqueness (no duplicate step_name values within a workflow).
20. TC-CS-020: The schema MUST include validation rule that step_type must be one of: prompt, action.
21. TC-CS-021: The schema MUST include validation rule that policy_name must be one of the 5 role policies.
22. TC-CS-022: The schema MUST include validation rule that artifact_key format is UPPER_SNAKE_CASE with _FILE suffix for documents.
23. TC-CS-023: The schema MUST include validation rule for routing completeness: every step must have onsuccess; review/refine steps must have on_reject_refine.
24. TC-CS-024: The schema MUST include validation rule for prompt pattern completeness: every prompt-driven step must have self_critic and self_validation patterns.
25. TC-CS-025: The schema MUST include validation rule for artifact flow integrity: every step's required_inputs must reference an artifact produced by a prior step or an input artifact.
26. TC-CS-026: The schema MUST include validation rule for composition_standard completeness: must define all 3 layers (Component Schema, Composition Format, Output Format).
27. TC-CS-027: The schema MUST include validation rule for output_variance feasibility: each variance must have a valid combination of component_requirements.
28. TC-CS-028: MUST NOT omit any validation rule from the spec Section 2.5 list.

### 2.5 Extensibility Model

29. TC-CS-029: The schema MUST document how new component types can be added without breaking existing compositions.
30. TC-CS-030: The schema MUST state that common properties remain stable across all types.
31. TC-CS-031: The extensibility model MUST explain that existing compositions continue to work because they reference by component_id, not type.

### 2.6 Examples

32. TC-CS-032: The schema MUST include at least one example component for each of the 8 component types.
33. TC-CS-033: Each example MUST demonstrate the complete component structure with common properties and type-specific properties populated.
34. TC-CS-034: Example values MUST match or be consistent with the example values shown in spec Section 2.3 tables.

### 2.7 Self-Validation

35. TC-CS-035: The schema document MUST include a self-check section or comment that enumerates all 8 component types and verifies each is defined.
36. TC-CS-036: The self-check MUST verify that each type has its common properties and type-specific properties documented.

---

## 3. Criteria for gatekeep_component_schema (Phase 2 - Gatekeeper QC)

### 3.1 Type Completeness Verification

37. TC-GCS-001: The gatekeeper report MUST explicitly count the component types defined and verify the count equals 8.
38. TC-GCS-002: The gatekeeper report MUST list each type by name (step_definition, role_policy, routing_pattern, prompt_pattern, artifact_contract, composition_standard, output_variance, domain_spec) and confirm its presence.
39. TC-GCS-003: The gatekeeper report MUST verify each type's Required/Optional status matches the spec (step_definition=Yes, prompt_pattern=No, etc.).
40. TC-GCS-004: The gatekeeper report MUST verify each type's Cardinality matches the spec (step_definition=Ordered list, role_policy=Singleton per step, etc.).

### 3.2 Schema Conformance

41. TC-GCS-005: The gatekeeper report MUST verify each component type defines all 5 common properties (component_id, component_type, name, version, description).
42. TC-GCS-006: The gatekeeper report MUST verify each type-specific property has name, type, required/optional status, description, and example value.
43. TC-GCS-007: The gatekeeper report MUST verify the component_id format is documented as {type}-{name}-{seq}.

### 3.3 Validation Rules Verification

44. TC-GCS-008: The gatekeeper report MUST enumerate all validation rules from the schema and verify they match the 9 rules in spec Section 2.5.
45. TC-GCS-009: The gatekeeper report MUST verify each validation rule is specific enough to be enforceable (not vague like "must be correct").

### 3.4 Uniqueness and Integrity

46. TC-GCS-010: The gatekeeper report MUST verify that no duplicate component type names exist.
47. TC-GCS-011: The gatekeeper report MUST verify artifact flow integrity rule is present (required_inputs must trace to prior step or input artifact).

### 3.5 Evidence and Verdict

48. TC-GCS-012: The gatekeeper report MUST provide a clear APPROVED or REJECTED verdict.
49. TC-GCS-013: The verdict MUST be justified with specific evidence referencing the schema content (e.g., "step_definition type defines 7 properties as required" not "schema looks good").
50. TC-GCS-014: If REJECTED, the report MUST list specific findings with severity (CRITICAL, MAJOR, MINOR) and describe what is missing or incorrect.
51. TC-GCS-015: MUST NOT approve a schema that omits any of the 8 component types.

---

## 4. Criteria for generate_composition_format (Phase 3 - Layer 2 Quality)

### 4.1 Composition Structure

52. TC-CF-001: The composition format MUST define a YAML structure with these required fields: builder_name (string), builder_label (string), job_prefix (string), builder_purpose (string), workflow_pattern (enum), step_bindings (array), artifact_bindings (object), composition_standard_binding (object).
53. TC-CF-002: The composition format MUST define optional fields: output_variances (array), domain_specs (array).
54. TC-CF-003: Each field MUST specify its type, required status, and description matching the spec Section 3.1 table.

### 4.2 Workflow Patterns

55. TC-CF-004: The format MUST define all 6 workflow patterns from spec Section 3.1.1: action_only, prompt_driven, mixed, gatekeeper_pipeline, meta_workflow_builder, meta_meta_builder.
56. TC-CF-005: Each pattern MUST include its description and the step sequence it implies.
57. TC-CF-006: The meta_meta_builder pattern MUST be documented as NEW in v3 with its specific step sequence.

### 4.3 Reference Pattern (Bindings)

58. TC-CF-007: The format MUST define 8 binding rules matching spec Section 3.2: steps (step_definition, Ordered list, Required), roles (role_policy, Singleton per step, Required), routing (routing_pattern, Singleton per step, Required), prompts (prompt_pattern, Unordered set per prompt step, Optional), artifacts (artifact_contract, Unordered set, Required), standard (composition_standard, Singleton, Required), variances (output_variance, Unordered set, Optional), domain_specs (domain_spec, Unordered set, Optional).
59. TC-CF-008: Components MUST be referenced by component_id, not copied inline. The format MUST enforce the "references, not duplicates" principle.
60. TC-CF-009: The format MUST define that every step must bind a role_policy and a routing_pattern.

### 4.4 Override Mechanism

61. TC-CF-010: The format MUST define how compositions override component properties per spec Section 3.3.
62. TC-CF-011: Overrides MUST conform to the component type's schema (no invalid properties allowed).
63. TC-CF-012: Overrides MUST merge with base component properties (override wins on conflict).
64. TC-CF-013: The format MUST include a YAML example demonstrating override syntax.

### 4.5 Placeholder Resolution

65. TC-CF-014: The format MUST define the placeholder resolution data sources from spec Section 3.4: Input Spec (WORKFLOW_SPEC_FILE, domain_name, job_prefix), Governance (BASE_COMPOSITION_STANDARD, GOVERNANCE_RUNTIME_ROOT), Runtime (job_id, seq, workspace_root).
66. TC-CF-015: The format MUST specify resolution rules: placeholders in prompt templates resolved at runtime, artifact paths resolved via context_extensions.py, governance paths resolved via runtime_context module.
67. TC-CF-016: Unresolved placeholders MUST be flagged as {UNRESOLVED: field_name} in the output.

### 4.6 Ordering Rules

68. TC-CF-017: The format MUST distinguish between ordered bindings (step_bindings are ordered lists) and singleton bindings (role_policy is singleton per step).
69. TC-CF-018: The format MUST specify which bindings can be omitted (optional) vs. which are mandatory (required).

### 4.7 Composition Standard Binding (v3 Innovation)

70. TC-CF-019: The format MUST define the composition_standard_binding structure from spec Section 3.6 with fields: standard_name (string, required), standard_version (string, required), component_types_defined (array, required), schema_sections (array, required), extensibility_model (string, required).
71. TC-CF-020: The composition_standard_binding MUST be documented as the key innovation of v3 -- every generated meta builder has its own composition standard.

### 4.8 Output Variances (v3 Innovation)

72. TC-CF-021: The format MUST define the output_variances structure from spec Section 3.7 with fields: variance_name (string, required), variance_description (string, required), component_requirements (array, required), output_files (array, required).
73. TC-CF-022: The format MUST document that output variances enable the meta builder to produce different output types based on the input spec.

### 4.9 Example Composition

74. TC-CF-023: The format MUST include at least one complete example composition demonstrating all binding rules, override syntax, placeholder usage, composition_standard_binding, and output_variances.
75. TC-CF-024: The example MUST be valid YAML that could be parsed and validated against the defined structure.

### 4.10 Self-Validation

76. TC-CF-025: The composition format document MUST include a self-check that verifies all 8 binding rules are defined.
77. TC-CF-026: The self-check MUST verify all 6 workflow patterns are documented.
78. TC-CF-027: The self-check MUST verify placeholder resolution data sources are complete.

---

## 5. Criteria for gatekeep_composition_format (Phase 3 - Gatekeeper QC)

### 5.1 Reference Integrity

79. TC-GCF-001: The gatekeeper report MUST verify that compositions reference components by component_id, not by copying content inline.
80. TC-GCF-002: The gatekeeper report MUST verify all referenced component_ids exist in the component library (no dangling references).
81. TC-GCF-003: The gatekeeper report MUST verify the binding rules enforce that roles and routing are bound to every step.

### 5.2 Override Conformance

82. TC-GCF-004: The gatekeeper report MUST verify overrides conform to component type schemas (no invalid properties in overrides).
83. TC-GCF-005: The gatekeeper report MUST verify override merge semantics (override wins on conflict with base properties).

### 5.3 Placeholder Resolvability

84. TC-GCF-006: The gatekeeper report MUST verify all placeholders can be resolved from the declared data sources (Input Spec, Governance, Runtime).
85. TC-GCF-007: The gatekeeper report MUST verify unresolved placeholder handling is defined ({UNRESOLVED: field_name}).

### 5.4 Required Bindings

86. TC-GCF-008: The gatekeeper report MUST verify all required bindings are present: steps, roles, routing, artifacts, standard.
87. TC-GCF-009: The gatekeeper report MUST verify optional bindings (prompts, variances, domain_specs) are correctly marked as optional.

### 5.5 Ordering Constraints

88. TC-GCF-010: The gatekeeper report MUST verify ordering rules are satisfied (step_bindings are ordered, singleton bindings have at most one value).
89. TC-GCF-011: The gatekeeper report MUST verify the workflow_pattern enum values are valid (one of the 6 defined patterns).

### 5.6 Composition Standard Binding

90. TC-GCF-012: The gatekeeper report MUST verify composition_standard_binding is present and defines all required fields.
91. TC-GCF-013: The gatekeeper report MUST verify schema_sections includes all 3 layers (Component Schema, Composition Format, Output Format).

### 5.7 Evidence and Verdict

92. TC-GCF-014: The gatekeeper report MUST provide a clear APPROVED or REJECTED verdict with specific evidence.
93. TC-GCF-015: If REJECTED, the report MUST list specific findings with severity levels.
94. TC-GCF-016: MUST NOT approve a composition format that omits required bindings or has dangling references.

---

## 6. Criteria for generate_output_format (Phase 4 - Layer 3 Quality)

### 6.1 Output Structure

95. TC-OF-001: The output format MUST define the 3-part output structure from spec Section 4.1: (1) Standards/COMPOSITION_STANDARD.md from composition_standard_binding, (2) Specs/{name}.md as meta composition spec, (3) Workflow package from step_bindings + routing + artifacts.
96. TC-OF-002: The workflow package output MUST include: workflow.toml, context_extensions.py, actions.py (if needed), prompts/ directory, README.md.
97. TC-OF-003: The output format MUST define the output file structure matching spec Section 4.4 example skeleton.
98. TC-OF-004: The Standards/ directory MUST always contain COMPOSITION_STANDARD.md (consistent filename per spec Section 5.5).

### 6.2 Resolution Rules

99. TC-OF-005: The output format MUST define that all step_definitions are expanded into workflow.toml [[step]] sections with [step.artifacts] and [step.coder].
100. TC-OF-006: The output format MUST define that all role_policies are resolved to [step.coder] role_policy values.
101. TC-OF-007: The output format MUST define that all routing_patterns are resolved to onsuccess and [step.on_reject_refine] configurations.
102. TC-OF-008: The output format MUST define that all prompt_patterns are expanded into prompt template sections.
103. TC-OF-009: The output format MUST define that the composition standard is generated as Standards/COMPOSITION_STANDARD.md.
104. TC-OF-010: The output format MUST define that artifact paths are resolved via context_extensions.py register_artifact_keys().

### 6.3 Placeholder Filling

105. TC-OF-011: The output format MUST define that all {placeholder} values are replaced with values from external data sources.
106. TC-OF-012: Unresolved placeholders MUST be explicitly flagged as {UNRESOLVED: field_name}.

### 6.4 Self-Contained Output

107. TC-OF-013: The output MUST contain all information needed to understand and use the deliverable without referencing the component library or composition file.
108. TC-OF-014: The output MUST NOT require external lookups to understand step definitions, routing, or artifact contracts.

### 6.5 Downstream Contracts

109. TC-OF-015: The output format MUST define extraction contracts for downstream workflows (what fields downstream workflows can extract).
110. TC-OF-016: The output format MUST specify that the output describes WHAT the deliverable is, not HOW to produce it (downstream-agnostic per Composition System Standard Section 5.2).

### 6.6 Quality Requirements

111. TC-OF-017: The output format MUST define these quality requirements from spec Section 4.3: no dangling step references, no dangling artifact references, complete prompt patterns, valid role assignments, artifact flow integrity, composition standard completeness, output variance feasibility, self-bootstrapping capability.
112. TC-OF-018: The output format MUST include criteria for verifying no contradictions between output sections.

### 6.7 Self-Validation

113. TC-OF-019: The output format document MUST include a self-check that verifies all output sections are covered.
114. TC-OF-020: The self-check MUST verify all resolution rules are defined for each component type.
115. TC-OF-021: The self-check MUST verify the output structure matches the 3-part specification.

---

## 7. Criteria for gatekeep_output_format (Phase 4 - Gatekeeper QC)

### 7.1 Reference Expansion

116. TC-GOF-001: The gatekeeper report MUST verify all component_ids are expanded into their full content in the output.
117. TC-GOF-002: The gatekeeper report MUST verify all step_definitions are expanded into workflow.toml [[step]] sections.
118. TC-GOF-003: The gatekeeper report MUST verify no dangling step references exist (every onsuccess and on_reject_refine target must exist as a defined step).

### 7.2 Placeholder Completeness

119. TC-GOF-004: The gatekeeper report MUST verify all placeholders are resolved or explicitly flagged as {UNRESOLVED: field_name}.
120. TC-GOF-005: The gatekeeper report MUST verify no unresolved placeholders remain without the UNRESOLVED marker.

### 7.3 Section Completeness

121. TC-GOF-006: The gatekeeper report MUST verify all 3 output parts are present: Standards/COMPOSITION_STANDARD.md, Specs/ directory structure, Workflow package files.
122. TC-GOF-007: The gatekeeper report MUST verify the workflow package includes all required files: workflow.toml, context_extensions.py, prompts/, README.md.
123. TC-GOF-008: The gatekeeper report MUST verify actions.py is present if any action steps are defined.

### 7.4 Consistency

124. TC-GOF-009: The gatekeeper report MUST verify no contradictions exist between output sections (e.g., step names in workflow.toml must match step names in prompts/).
125. TC-GOF-010: The gatekeeper report MUST verify artifact keys are consistent across workflow.toml, context_extensions.py, and prompt templates.

### 7.5 Downstream Feasibility

126. TC-GOF-011: The gatekeeper report MUST verify downstream workflows can extract their concerns from the output (extraction contracts are defined and fulfillable).
127. TC-GOF-012: The gatekeeper report MUST verify the output is self-contained and does not require external references to be understood.

### 7.6 Evidence and Verdict

128. TC-GOF-013: The gatekeeper report MUST provide a clear APPROVED or REJECTED verdict with specific evidence.
129. TC-GOF-014: MUST NOT approve an output format that has dangling references or missing required sections.

---

## 8. Criteria for generate_operational_workflow (Phase 5 - Workflow Correctness)

### 8.1 Workflow Phases

130. TC-OW-001: The operational workflow MUST define all 9 phases from spec Section 5.1: Foundation (TDD Loop), Component Schema, Composition Format, Output Format, Operational Workflow, Composition Standard, Meta Composition Spec, Package Assembly, Promotion.
131. TC-OW-002: The Foundation phase MUST include generate_test_criteria, review_test_criteria, and refine_test_criteria (conditional) steps.
132. TC-OW-003: Each of the Component Schema, Composition Format, Output Format, Operational Workflow phases MUST include a generate step followed by a gatekeep step.
133. TC-OW-004: The Composition Standard phase MUST include generate_composition_standard and gatekeep_composition_standard steps (NEW in v3).
134. TC-OW-005: The Meta Composition Spec phase MUST include generate_meta_composition_spec step (NEW in v3).
135. TC-OW-006: The Package Assembly phase MUST include generate_package, validate_package_deterministic, gatekeep_package, review_package, and refine_package steps.
136. TC-OW-007: The Promotion phase MUST include promote_workflow_package and stepCompletion steps.

### 8.2 Step Sequence

137. TC-OW-008: The step sequence MUST be logical: each step's inputs must be produced by prior steps or be input artifacts.
138. TC-OW-009: The step sequence MUST follow the meta_meta_builder workflow pattern from spec Section 3.1.1.
139. TC-OW-010: Gatekeeper steps MUST immediately follow their corresponding generate steps.
140. TC-OW-011: Review steps MUST follow gatekeep steps (when gatekeep approves).
141. TC-OW-012: Refine steps MUST follow review steps (when review rejects).

### 8.3 Artifact Contracts

142. TC-OW-013: All input artifacts MUST be declared: WORKFLOW_SPEC_FILE (required).
143. TC-OW-014: All output artifacts MUST be declared matching spec Section 5.3: TEST_CRITERIA_FILE, REVIEW_TEST_CRITERIA_FILE, COMPONENT_SCHEMA_FILE, GATEKEEP_COMPONENT_SCHEMA_FILE, COMPOSITION_FORMAT_FILE, GATEKEEP_COMPOSITION_FORMAT_FILE, OUTPUT_FORMAT_FILE, GATEKEEP_OUTPUT_FORMAT_FILE, OPERATIONAL_WORKFLOW_FILE, GATEKEEP_OPERATIONAL_WORKFLOW_FILE, COMPOSITION_STANDARD_FILE, GATEKEEP_COMPOSITION_STANDARD_FILE, META_COMPOSITION_SPEC_FILE, WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_INDEX_FILE, WORKFLOW_README_FILE, VALIDATION_REPORT_FILE, GATEKEEP_PACKAGE_FILE, REVIEW_FILE_SUGGESTED.
144. TC-OW-015: Each artifact MUST have a description, required status, and produced_by step.
145. TC-OW-016: Artifact flow integrity: every step's required_inputs must reference an artifact produced by a prior step or an input artifact.

### 8.4 Action Implementations

146. TC-OW-017: The workflow MUST identify validate_package_deterministic as an action step (not prompt-driven) per spec Section 5.4.
147. TC-OW-018: The validate_package_deterministic action MUST check: workflow.toml syntax, step references exist, artifact references valid, role policies valid, prompt files exist, composition standard file exists, meta composition spec file exists.
148. TC-OW-019: The workflow MUST identify promote_workflow_package as an action step per spec Section 5.4.
149. TC-OW-020: The promote_workflow_package action MUST copy: workflow.toml, context_extensions.py, actions.py, prompts/, README.md, .env.sample (if present), config.json.sample (if present), Standards/COMPOSITION_STANDARD.md, Specs/ directory (if present).
150. TC-OW-021: Deterministic operations MUST be identified as action steps, not prompt-driven steps.

### 8.5 Prompt-Driven Steps

151. TC-OW-022: All generation steps (generate_test_criteria, generate_component_schema, generate_composition_format, generate_output_format, generate_operational_workflow, generate_composition_standard, generate_meta_composition_spec, generate_package) MUST be prompt-driven.
152. TC-OW-023: All gatekeeper steps MUST be prompt-driven (they require LLM judgment).
153. TC-OW-024: All review steps MUST be prompt-driven.
154. TC-OW-025: All refine steps MUST be prompt-driven.
155. TC-OW-026: Every prompt-driven step MUST include self_critic and self_validation prompt patterns (mandatory per spec Section 2.5).

### 8.6 Routing

156. TC-OW-027: Every step MUST have an onsuccess routing to the next step.
157. TC-OW-028: Review steps that can reject MUST have on_reject_refine routing to the corresponding refine step.
158. TC-OW-029: Refine steps MUST have onsuccess routing back to the review step (forming a loop).
159. TC-OW-030: All on_reject_refine configurations MUST include: step, artifact, max_iterations, exhausted_failure_code, exhausted_failure_class.
160. TC-OW-031: The stepCompletion step MUST be the terminal step with no onsuccess.

### 8.7 Domain-Specific Requirements

161. TC-OW-032: The workflow MUST support self-bootstrapping (can process its own composition spec to generate the next version) per spec Section 5.5.
162. TC-OW-033: The workflow MUST support three outputs: Standards/COMPOSITION_STANDARD.md, Specs/{name}.md, and workflow package per spec Section 5.5.
163. TC-OW-034: The workflow MUST support dynamic component discovery (reads composition standard dynamically, not hardcoded) per spec Section 5.5.
164. TC-OW-035: The workflow MUST support output variances (can produce different output types based on input spec) per spec Section 5.5.
165. TC-OW-036: The workflow MUST use folder-based domain separation (each meta builder has Standards/ and Specs/ subdirectories) per spec Section 5.5.
166. TC-OW-037: The workflow MUST verify that action step implementations check for existing reusable actions in the actions/ directory before generating custom implementations per spec Section 5.5.

### 8.8 Self-Validation

167. TC-OW-038: The operational workflow design MUST include a self-check that verifies all 9 phases are covered.
168. TC-OW-039: The self-check MUST verify step routing is complete (no dead-end steps except stepCompletion).
169. TC-OW-040: The self-check MUST verify artifact flow integrity (no orphaned artifacts).

---

## 9. Criteria for gatekeep_operational_workflow (Phase 5 - Gatekeeper QC)

### 9.1 Phase Completeness

170. TC-GOW-001: The gatekeeper report MUST verify all 9 workflow phases are defined with their required steps.
171. TC-GOW-002: The gatekeeper report MUST verify the Foundation phase includes generate_test_criteria, review_test_criteria, refine_test_criteria.
172. TC-GOW-003: The gatekeeper report MUST verify the Composition Standard phase includes generate_composition_standard and gatekeep_composition_standard (v3 innovation).
173. TC-GOW-004: The gatekeeper report MUST verify the Meta Composition Spec phase includes generate_meta_composition_spec (v3 innovation).

### 9.2 Data Flow

174. TC-GOW-005: The gatekeeper report MUST verify artifact flow from inputs (WORKFLOW_SPEC_FILE) through all phases to final outputs.
175. TC-GOW-006: The gatekeeper report MUST trace each output artifact back to its producing step.
176. TC-GOW-007: The gatekeeper report MUST verify no artifact is consumed before it is produced (temporal ordering).

### 9.3 Routing Validity

177. TC-GOW-008: The gatekeeper report MUST verify every step has valid onsuccess routing to an existing step.
178. TC-GOW-009: The gatekeeper report MUST verify review/refine loops are correctly configured (review -> refine -> review).
179. TC-GOW-010: The gatekeeper report MUST verify stepCompletion is the terminal step.
180. TC-GOW-011: The gatekeeper report MUST verify exhausted_failure_code and exhausted_failure_class are defined for all on_reject_refine routes.

### 9.4 Type Consistency

181. TC-GOW-012: The gatekeeper report MUST verify step types match task nature: deterministic operations are action steps, LLM-judgment tasks are prompt steps.
182. TC-GOW-013: The gatekeeper report MUST verify validate_package_deterministic is an action step.
183. TC-GOW-014: The gatekeeper report MUST verify promote_workflow_package is an action step.
184. TC-GOW-015: The gatekeeper report MUST verify all generation, gatekeep, review, and refine steps are prompt-driven.

### 9.5 Action Feasibility

185. TC-GOW-016: The gatekeeper report MUST verify action step specifications are implementable (clear inputs, outputs, logic).
186. TC-GOW-017: The gatekeeper report MUST verify validate_package_deterministic checks are specific and enumerable (not vague).
187. TC-GOW-018: The gatekeeper report MUST verify promote_workflow_package file list is complete and matches the output format.

### 9.6 Evidence and Verdict

188. TC-GOW-019: The gatekeeper report MUST provide a clear APPROVED or REJECTED verdict with specific evidence.
189. TC-GOW-020: MUST NOT approve an operational workflow that has broken routing or missing phases.

---

## 9A. Criteria for generate_composition_standard and gatekeep_composition_standard (Phase 6 - Composition Standard Quality and Gatekeeper QC)

### 9A.1 Composition Standard Structure

190. TC-CSN-001: The composition standard MUST define standard_name (string, required) following the naming convention {DOMAIN}_STANDARD (e.g., WORKFLOW_BUILDER_STANDARD).
191. TC-CSN-002: The composition standard MUST define standard_version (string, required) in semantic version format (MAJOR.MINOR.PATCH).
192. TC-CSN-003: The composition standard MUST define component_types_defined (array, required) listing all component types the generated meta builder's domain uses.
193. TC-CSN-004: The component_types_defined list MUST match the component types specified in the input composition system spec (WORKFLOW_SPEC_FILE Section 2.1).
194. TC-CSN-005: The composition standard MUST define schema_sections (array, required) containing all 3 layers: "Component Schema", "Composition Format", "Output Format".
195. TC-CSN-006: The composition standard MUST define extensibility_model (string, required) explaining how new component types can be added to the meta builder's domain.

### 9A.2 Layer 1 Completeness (Component Schema)

196. TC-CSN-007: The composition standard MUST include a Component Schema section that defines all domain-specific component types for the target meta builder.
197. TC-CSN-008: Each component type in the Component Schema section MUST include: type name, purpose, required/optional status, cardinality, and type-specific properties.
198. TC-CSN-009: The Component Schema section MUST define common properties shared across all component types (component_id, component_type, name, version, description).
199. TC-CSN-010: The Component Schema section MUST include validation rules for the domain-specific component types.

### 9A.3 Layer 2 Completeness (Composition Format)

200. TC-CSN-011: The composition standard MUST include a Composition Format section that defines the binding rules for the target domain.
201. TC-CSN-012: The Composition Format section MUST define how compositions reference components by component_id (references, not duplicates principle).
202. TC-CSN-013: The Composition Format section MUST define the override mechanism for per-composition customization.
203. TC-CSN-014: The Composition Format section MUST define placeholder resolution data sources for the target domain.
204. TC-CSN-015: The Composition Format section MUST include at least one example composition demonstrating the binding rules.

### 9A.4 Layer 3 Completeness (Output Format)

205. TC-CSN-016: The composition standard MUST include an Output Format section that defines the output structure for the target domain.
206. TC-CSN-017: The Output Format section MUST define resolution rules for expanding component references and filling placeholders.
207. TC-CSN-018: The Output Format section MUST define quality requirements (no dangling references, no unresolved placeholders, completeness, consistency).
208. TC-CSN-019: The Output Format section MUST include a skeleton or example demonstrating the expected output structure.

### 9A.5 Self-Description Capability

209. TC-CSN-020: The composition standard MUST be self-describing: it can be used independently without requiring external documents to understand the meta builder's component schema, composition format, and output format.
210. TC-CSN-021: The composition standard MUST explicitly state which workflow builder version it is compatible with (e.g., "Compatible with workflow_builder_v3 and later").
211. TC-CSN-022: The composition standard MUST include a self-check section that verifies all 3 layers are defined and complete.

### 9A.6 Gatekeeper: Well-Formedness Verification

212. TC-GCSN-001: The gatekeeper report MUST verify the composition standard defines standard_name and standard_version with correct formats.
213. TC-GCSN-002: The gatekeeper report MUST verify the composition standard defines component_types_defined as a non-empty array.
214. TC-GCSN-003: The gatekeeper report MUST verify schema_sections contains exactly 3 entries: "Component Schema", "Composition Format", "Output Format".
215. TC-GCSN-004: The gatekeeper report MUST verify extensibility_model is present and provides a concrete description (not a placeholder or vague statement).

### 9A.7 Gatekeeper: Layer Completeness Verification

216. TC-GCSN-005: The gatekeeper report MUST verify the Component Schema layer defines all component types listed in component_types_defined.
217. TC-GCSN-006: The gatekeeper report MUST verify each component type in the Component Schema has type-specific properties documented.
218. TC-GCSN-007: The gatekeeper report MUST verify the Composition Format layer defines binding rules, override mechanism, and placeholder resolution.
219. TC-GCSN-008: The gatekeeper report MUST verify the Output Format layer defines resolution rules, quality requirements, and output structure.

### 9A.8 Gatekeeper: Extensibility Model Verification

220. TC-GCSN-009: The gatekeeper report MUST verify the extensibility_model explains how new component types can be added without breaking existing compositions.
221. TC-GCSN-010: The gatekeeper report MUST verify the extensibility_model states that common properties remain stable across all types.
222. TC-GCSN-011: The gatekeeper report MUST verify the extensibility_model explains that existing compositions continue to work via component_id references.

### 9A.9 Gatekeeper: Self-Description Verification

223. TC-GCSN-012: The gatekeeper report MUST verify the composition standard can be understood independently (no external references required for core content).
224. TC-GCSN-013: The gatekeeper report MUST verify the self-check section enumerates all 3 layers and confirms each is defined.

### 9A.10 Gatekeeper: Evidence and Verdict

225. TC-GCSN-014: The gatekeeper report MUST provide a clear APPROVED or REJECTED verdict with specific evidence referencing the composition standard content.
226. TC-GCSN-015: If REJECTED, the report MUST list specific findings with severity (CRITICAL, MAJOR, MINOR) and describe what is missing or incorrect.
227. TC-GCSN-016: MUST NOT approve a composition standard that omits any of the 3 layers (Component Schema, Composition Format, Output Format).

---

## 9B. Criteria for generate_meta_composition_spec (Phase 7 - Meta Spec Quality)

### 9B.1 Spec Structure (Per COMPOSITION_SYSTEM_STANDARD.md Section 11.1)

228. TC-MCS-001: The meta composition spec MUST include Section 1: Domain Overview with domain name, purpose, and context.
229. TC-MCS-002: The meta composition spec MUST include Section 2: Component Schema defining the component types for the target domain (Layer 1).
230. TC-MCS-003: The meta composition spec MUST include Section 3: Composition Format defining binding rules, override mechanism, and placeholder resolution (Layer 2).
231. TC-MCS-004: The meta composition spec MUST include Section 4: Output Format defining output structure, resolution rules, and quality requirements (Layer 3).
232. TC-MCS-005: The meta composition spec MUST include Section 5: Operational Requirements defining workflow phases, artifacts, action steps, and domain constraints.
233. TC-MCS-006: The sections MUST appear in the order specified above (1 through 5).

### 9B.2 Component Types Definition

234. TC-MCS-007: The Component Schema section (Section 2) MUST define all component types specific to the target domain of the generated meta builder.
235. TC-MCS-008: Each component type MUST include: type name, purpose, required/optional status, cardinality, and type-specific properties with names, types, and descriptions.
236. TC-MCS-009: The component types defined MUST be consistent with the component_types_defined in the composition standard (Section 9A).
237. TC-MCS-010: The Component Schema section MUST include at least one example component demonstrating the complete component structure.

### 9B.3 Composition Format Rules

238. TC-MCS-011: The Composition Format section (Section 3) MUST define the binding rules specifying which component types can be assembled and in what cardinality.
239. TC-MCS-012: The Composition Format section MUST define the override mechanism for per-composition customization of component properties.
240. TC-MCS-013: The Composition Format section MUST define placeholder resolution data sources for the target domain.
241. TC-MCS-014: The Composition Format section MUST include at least one example composition demonstrating the binding rules and override syntax.

### 9B.4 Output Format Structure

242. TC-MCS-015: The Output Format section (Section 4) MUST define the output structure specifying what files and sections the generated outputs contain.
243. TC-MCS-016: The Output Format section MUST define resolution rules for expanding component references and filling placeholders.
244. TC-MCS-017: The Output Format section MUST define quality requirements for the output (no dangling references, completeness, consistency).
245. TC-MCS-018: The Output Format section MUST include a skeleton or example demonstrating the expected output structure.

### 9B.5 Examples (Per COMPOSITION_SYSTEM_STANDARD.md Section 11.2)

246. TC-MCS-019: The meta composition spec MUST include at least one example component in the Component Schema section.
247. TC-MCS-020: The meta composition spec MUST include at least one example composition in the Composition Format section.
248. TC-MCS-021: The meta composition spec MUST include at least one example output skeleton in the Output Format section.
249. TC-MCS-022: All examples MUST be concrete and consistent with each other (same domain, same component types).

### 9B.6 Self-Bootstrapping Capability

250. TC-MCS-023: The meta composition spec MUST be structured so that it could be fed as input to the generated workflow builder (self-bootstrapping test).
251. TC-MCS-024: The meta composition spec MUST define component types, composition rules, and output structure in a way that the generated workflow can process dynamically (not hardcoded).
252. TC-MCS-025: The meta composition spec MUST include all information needed for the generated meta builder to understand its domain without external references.

### 9B.7 Self-Validation

253. TC-MCS-026: The generate_meta_composition_spec step MUST include a self-check that verifies all 5 required sections are present.
254. TC-MCS-027: The self-check MUST verify each section contains the required content (component types, binding rules, output structure, operational requirements).
255. TC-MCS-028: The self-check MUST verify examples are included for each layer.

---

## 10. Criteria for generate_package (Phase 8 - File Completeness and Consistency)

### 10.1 File Completeness

256. TC-GP-001: The generated package MUST include workflow.toml with all steps defined as [[step]] sections.
257. TC-GP-002: The generated package MUST include context_extensions.py with register_artifact_keys() defining all artifact keys.
258. TC-GP-003: The generated package MUST include actions.py if any action steps are defined (validate_package_deterministic, promote_workflow_package).
259. TC-GP-004: The generated package MUST include a prompts/ directory with one .txt file per prompt-driven step, named sequentially (NN_step_name.txt matching the step sequence in workflow.toml).
260. TC-GP-005: The generated package MUST include README.md documenting the workflow.
261. TC-GP-006: The generated package MUST include Standards/COMPOSITION_STANDARD.md (v3 innovation).
262. TC-GP-007: The generated package MUST include Specs/ directory structure (v3 innovation).
263. TC-GP-008: The generated package MUST include .env.sample if environment variables are needed.
264. TC-GP-009: The generated package MUST include config.json.sample if runtime configuration is needed.

### 10.2 Design Fidelity

265. TC-GP-010: The workflow.toml MUST match the operational workflow design: same step names, same routing, same artifact bindings.
266. TC-GP-011: The context_extensions.py MUST register all artifact keys declared in the operational workflow.
267. TC-GP-012: The actions.py MUST implement all action steps from the operational workflow (validate_package_deterministic, promote_workflow_package).
268. TC-GP-013: Each prompt file MUST correspond to a prompt-driven step in the operational workflow.

### 10.3 Component Schema Integration

269. TC-GP-014: The component schema from Phase 2 MUST be correctly reflected in the generated workflow's understanding of component types.
270. TC-GP-015: The Standards/COMPOSITION_STANDARD.md MUST define the component schema for the generated meta builder's domain.

### 10.4 Composition Format Integration

271. TC-GP-016: The composition format from Phase 3 MUST be correctly reflected in the generated workflow's composition resolution logic.
272. TC-GP-017: The Standards/COMPOSITION_STANDARD.md MUST define the composition format for the generated meta builder's domain.

### 10.5 Output Format Integration

273. TC-GP-018: The output format from Phase 4 MUST be correctly reflected in the generated workflow's output assembly logic.
274. TC-GP-019: The Standards/COMPOSITION_STANDARD.md MUST define the output format for the generated meta builder's domain.

### 10.6 Prompt Quality

275. TC-GP-020: Each prompt MUST have a clear objective stating what the step produces.
276. TC-GP-021: Each prompt MUST specify reference inputs using {ARTIFACT_KEY} placeholders.
277. TC-GP-022: Each prompt MUST specify output instructions including file path and format.
278. TC-GP-023: Each prompt MUST include a self-critic section challenging the generation before completing.
279. TC-GP-024: Each prompt MUST include a self-validation section verifying completeness.
280. TC-GP-025: Gatekeeper prompts MUST include decision rules (when to APPROVE vs REJECT).
281. TC-GP-026: Review prompts MUST include a comprehensive review checklist.
282. TC-GP-027: Refine prompts MUST include refinement rules and constraints (what NOT to change).

### 10.7 Action Implementations

283. TC-GP-028: If action steps exist, they MUST be implemented as Python functions in actions.py.
284. TC-GP-029: Action implementations MUST have clear input parameters and return values.
285. TC-GP-030: Action implementations MUST be deterministic (same input produces same output).

### 10.8 Action Reuse

286. TC-GP-031: The generate_package step MUST verify that action step implementations check for existing reusable actions in the actions/ directory before generating custom implementations per spec Section 5.5.
287. TC-GP-032: If an equivalent reusable action exists in the codebase (e.g., copy actions, validation actions, promotion actions from other workflows), the generated workflow MUST reference or reuse it rather than duplicating the implementation.

### 10.9 Self-Validation

288. TC-GP-033: The generate_package step MUST include a self-check that verifies all files implied by the operational workflow are generated.
289. TC-GP-034: The self-check MUST verify file count matches the expected file list.
290. TC-GP-035: The self-check MUST verify no files are missing from the package.

---

## 11. Criteria for gatekeep_package (Phase 8 - Gatekeeper QC)

### 11.1 File Checklist

291. TC-GPKG-001: The gatekeeper report MUST verify ALL expected files exist: workflow.toml, context_extensions.py, actions.py (if needed), prompts/*.txt, README.md, Standards/COMPOSITION_STANDARD.md.
292. TC-GPKG-002: The gatekeeper report MUST verify prompts/ has one .txt file per prompt-driven step (count matches).
293. TC-GPKG-003: The gatekeeper report MUST verify Specs/ directory exists with correct structure.

### 11.2 Design Fidelity

294. TC-GPKG-004: The gatekeeper report MUST verify workflow.toml step sequence matches the operational workflow design.
295. TC-GPKG-005: The gatekeeper report MUST verify routing in workflow.toml matches the operational workflow design (onsuccess, on_reject_refine).
296. TC-GPKG-006: The gatekeeper report MUST verify artifact keys in workflow.toml match context_extensions.py registrations.
297. TC-GPKG-007: The gatekeeper report MUST verify prompt file names match step names in workflow.toml using the NN_step_name.txt naming convention.

### 11.3 Composition Integrity

298. TC-GPKG-008: The gatekeeper report MUST verify component schema (from Phase 2) is consistently reflected across workflow.toml, prompts, and Standards/COMPOSITION_STANDARD.md.
299. TC-GPKG-009: The gatekeeper report MUST verify composition format (from Phase 3) is consistently reflected across workflow.toml and Standards/COMPOSITION_STANDARD.md.
300. TC-GPKG-010: The gatekeeper report MUST verify output format (from Phase 4) is consistently reflected across workflow.toml and Standards/COMPOSITION_STANDARD.md.

### 11.4 Prompt Completeness

301. TC-GPKG-011: The gatekeeper report MUST verify each prompt file has: objective, reference inputs, output instructions, self-critic section.
302. TC-GPKG-012: The gatekeeper report MUST verify gatekeeper prompts have decision rules (APPROVE vs REJECT criteria).
303. TC-GPKG-013: The gatekeeper report MUST verify review prompts have review checklists.

### 11.5 Scope Check

304. TC-GPKG-014: The gatekeeper report MUST detect scope shrink (files or steps missing compared to operational workflow design).
305. TC-GPKG-015: The gatekeeper report MUST detect scope creep (extra files or steps not in operational workflow design).
306. TC-GPKG-016: The gatekeeper report MUST verify no extra configurations, wrong models, or unnecessary inputs are present.

### 11.6 Evidence and Verdict

307. TC-GPKG-017: The gatekeeper report MUST provide a clear APPROVED or REJECTED verdict with specific evidence.
308. TC-GPKG-018: MUST NOT approve a package that has missing files or design fidelity issues.

---

## 12. Criteria for review_package (Phase 8 - Comprehensive Review)

### 12.1 Spec Fulfillment

309. TC-RP-001: The review MUST verify the workflow actually implements the spec objective: generating a meta-meta builder with Standards, Specs, and workflow package.
310. TC-RP-002: The review MUST verify all 8 component types from the spec are handled by the generated workflow.
311. TC-RP-003: The review MUST verify all 6 workflow patterns from the spec are documented in the generated workflow.
312. TC-RP-004: The review MUST verify the 3-layer architecture (Component Library, Composition Definitions, Resolved Outputs) is implemented.

### 12.2 Component Quality

313. TC-RP-005: The review MUST verify components are truly reusable (not single-use specific to one workflow instance).
314. TC-RP-006: The review MUST verify each component has complete type-specific properties documented.
315. TC-RP-007: The review MUST verify component validation rules are specific and enforceable.

### 12.3 Composition Quality

316. TC-RP-008: The review MUST verify compositions are clear and resolvable (references by ID, not duplicated content).
317. TC-RP-009: The review MUST verify override mechanisms are well-defined and schema-conformant.
318. TC-RP-010: The review MUST verify placeholder resolution is complete (all data sources declared).

### 12.4 Output Quality

319. TC-RP-011: The review MUST verify outputs are self-contained (all references expanded, no external dependencies).
320. TC-RP-012: The review MUST verify outputs are complete (all required sections present).
321. TC-RP-013: The review MUST verify outputs are consistent (no contradictions between sections).

### 12.5 Data Flow

322. TC-RP-014: The review MUST verify information flows correctly through the workflow: input spec -> test criteria -> component schema -> composition format -> output format -> operational workflow -> composition standard -> meta composition spec -> package.
323. TC-RP-015: The review MUST verify no information is lost between phases (each phase builds on prior phase outputs).

### 12.6 No Hallucinations

324. TC-RP-016: The review MUST verify no extra configurations are present that are not required by the spec.
325. TC-RP-017: The review MUST verify no wrong models or APIs are referenced.
326. TC-RP-018: The review MUST verify no unnecessary inputs are required beyond WORKFLOW_SPEC_FILE.

### 12.7 Gatekeeper Effectiveness

327. TC-RP-019: The review MUST assess whether gatekeepers caught issues early (did gatekeep steps find real problems?).
328. TC-RP-020: The review MUST verify gatekeeper verdicts are justified with specific evidence.

### 12.8 Comprehensive Verification

329. TC-RP-021: The review MUST verify ALL criteria in this test criteria document pass (sections 2 through 16).
330. TC-RP-022: The review MUST provide a clear APPROVED or REJECTED verdict.
331. TC-RP-023: If REJECTED, the review MUST list specific issues with severity and suggested fixes.

---

## 13. Criteria for refine_package (Phase 8 - Issue Resolution)

### 13.1 Completeness of Fixes

332. TC-RFP-001: The refine step MUST be able to fix ALL types of issues flagged in review: missing files, design fidelity issues, prompt quality issues, composition integrity issues.
333. TC-RFP-002: The refine step MUST fix each issue identified in the review report (no issues left unfixed).
334. TC-RFP-003: The refine step MUST produce updated artifacts that address all review findings.

### 13.2 Cross-File Consistency

335. TC-RFP-004: Refinement MUST maintain cross-file consistency: changes to workflow.toml must be reflected in context_extensions.py, prompts/, and actions.py.
336. TC-RFP-005: Refinement MUST NOT introduce new inconsistencies while fixing existing issues.
337. TC-RFP-006: If a component type is added/modified, all references to it (in workflow.toml, prompts, Standards/COMPOSITION_STANDARD.md) MUST be updated consistently.

### 13.3 Root Cause Fixes

338. TC-RFP-007: Refinement MUST fix root causes, not symptoms. For example, if a prompt is ambiguous, fix the prompt template, not just the output it produced.
339. TC-RFP-008: Refinement MUST NOT add scope (new features, new steps) beyond what the spec requires.
340. TC-RFP-009: Refinement MUST preserve the operational workflow design unless the design itself is the root cause of an issue.

### 13.4 Iteration Control

341. TC-RFP-010: The refine step MUST respect max_iterations from the on_reject_refine configuration.
342. TC-RFP-011: If max_iterations is exhausted, the workflow MUST fail with the configured exhausted_failure_code.

---

## 14. Prompt Quality Criteria (for all prompt-driven steps)

### 14.1 Output Mechanism

343. TC-PQ-001: Each prompt MUST explicitly instruct the LLM to use file-writing tools (write_file or equivalent) to create actual files on disk at the specified artifact paths.
344. TC-PQ-002: Each prompt MUST specify the exact file path using {ARTIFACT_KEY} placeholders that resolve to absolute paths.
345. TC-PQ-003: Each prompt MUST NOT instruct the LLM to output content to stdout or return it as a response -- all output MUST be written to files.

### 14.2 Ambiguity Check

346. TC-PQ-004: Prompts MUST NOT contain vague instructions like "generate appropriate content" or "create suitable structure" without specifying what "appropriate" or "suitable" means in concrete terms.
347. TC-PQ-005: Prompts MUST specify exact section names, field names, and structural requirements (not leave them to LLM interpretation).
348. TC-PQ-006: Prompts MUST NOT use ambiguous terms that could be interpreted differently by different LLMs (e.g., "comprehensive" without defining what comprehensive includes).

### 14.3 Common LLM Mistakes

349. TC-PQ-007: Prompts MUST guard against the LLM inventing component types not in the spec (for generate_component_schema).
350. TC-PQ-008: Prompts MUST guard against the LLM hardcoding component types instead of reading them dynamically from the spec (for generate_package).
351. TC-PQ-009: Prompts MUST guard against the LLM producing incomplete outputs (for all generation steps, the prompt MUST enumerate all required sections).
352. TC-PQ-010: Prompts MUST guard against the LLM producing superficial reviews (for review steps, the prompt MUST include specific checklists).
353. TC-PQ-011: Prompts MUST guard against the LLM fixing symptoms instead of root causes (for refine steps, the prompt MUST instruct root cause analysis).

### 14.4 Completeness

354. TC-PQ-012: Each generation prompt MUST specify all required output sections with their expected content.
355. TC-PQ-013: Each generation prompt MUST specify the output file format (YAML frontmatter, markdown body, etc.).
356. TC-PQ-014: Each generation prompt MUST specify file naming conventions (e.g., TEST_CRITERIA-{seq}.md, COMPONENT_SCHEMA-{seq}.md).
357. TC-PQ-015: Each gatekeeper prompt MUST specify the validation criteria to check (not just "validate the artifact").
358. TC-PQ-016: Each review prompt MUST specify the review checklist (not just "review the package").
359. TC-PQ-017: Each refine prompt MUST specify what issues to fix and constraints on what NOT to change.

### 14.5 Self-Validation

360. TC-PQ-018: Each generation prompt MUST include a self-validation section that instructs the LLM to verify its output against the spec before completing.
361. TC-PQ-019: Each self-validation section MUST include specific checks (e.g., "count the component types and verify it equals 8").
362. TC-PQ-020: Each gatekeeper prompt MUST include a self-critic section that challenges the gatekeeper to verify it did not miss any issues.
363. TC-PQ-021: Each review prompt MUST include a self-critic section that challenges superficial reviews.
364. TC-PQ-022: Each refine prompt MUST include a self-critic section that verifies root cause fixes, not symptom fixes.

### 14.6 Reference Inputs

365. TC-PQ-023: Each prompt MUST specify reference inputs using {ARTIFACT_KEY} placeholders that will be resolved at runtime.
366. TC-PQ-024: Prompts MUST instruct the LLM to read ALL reference inputs before producing any output (read-before-write principle).
367. TC-PQ-025: Prompts MUST specify which sections of reference inputs are relevant (not just "read the file").

### 14.7 Forbidden Content

368. TC-PQ-026: Prompts MUST include a forbidden content section specifying what NOT to include (vague criteria, non-ASCII characters, criteria that cannot be verified).
369. TC-PQ-027: Prompts MUST forbid the LLM from asking clarifying questions (the workflow must execute autonomously).
370. TC-PQ-028: Prompts MUST forbid the LLM from inventing scope beyond what the spec requires.

---

## Appendix A: Negative Criteria Summary

The following MUST NOT appear in any generated artifact:

371. TC-NEG-001: MUST NOT include component types not defined in the spec Section 2.1.
372. TC-NEG-002: MUST NOT include workflow patterns not defined in the spec Section 3.1.1.
373. TC-NEG-003: MUST NOT duplicate component content inline in compositions (must reference by ID).
374. TC-NEG-004: MUST NOT leave placeholders unresolved without the {UNRESOLVED: field_name} marker.
375. TC-NEG-005: MUST NOT include dangling step references (onsuccess/on_reject_refine to non-existent steps).
376. TC-NEG-006: MUST NOT include dangling artifact references (required_inputs referencing non-existent artifacts).
377. TC-NEG-007: MUST NOT include vague criteria like "must be correct" or "must work properly" in test criteria.
378. TC-NEG-008: MUST NOT include non-ASCII characters in any generated file.
379. TC-NEG-009: MUST NOT include extra configurations, wrong models, or unnecessary inputs beyond what the spec requires.
380. TC-NEG-010: MUST NOT omit any of the 9 workflow phases from the operational workflow.
381. TC-NEG-011: MUST NOT omit self_critic or self_validation sections from any prompt-driven step.
382. TC-NEG-012: MUST NOT produce outputs that require external references to be understood (outputs must be self-contained).

---

## Appendix B: Criteria Traceability Matrix

| Criteria Section | Spec Source | Layer | Phase |
|---|---|---|---|
| Section 2 (generate_component_schema) | Spec Section 2.1-2.5 | Layer 1 | Phase 2 |
| Section 3 (gatekeep_component_schema) | Spec Section 2.5 | Layer 1 | Phase 2 |
| Section 4 (generate_composition_format) | Spec Section 3.1-3.7 | Layer 2 | Phase 3 |
| Section 5 (gatekeep_composition_format) | Spec Section 3.2-3.4 | Layer 2 | Phase 3 |
| Section 6 (generate_output_format) | Spec Section 4.1-4.3 | Layer 3 | Phase 4 |
| Section 7 (gatekeep_output_format) | Spec Section 4.3 | Layer 3 | Phase 4 |
| Section 8 (generate_operational_workflow) | Spec Section 5.1-5.5 | Operational | Phase 5 |
| Section 9 (gatekeep_operational_workflow) | Spec Section 5.1-5.4 | Operational | Phase 5 |
| Section 9A (generate_composition_standard + gatekeep_composition_standard) | Spec Section 4.3, 5.1 (Phase 6), Standard Section 11.1 | v3 Innovation | Phase 6 |
| Section 9B (generate_meta_composition_spec) | Spec Section 5.1 (Phase 7), Standard Section 11.1-11.2 | v3 Innovation | Phase 7 |
| Section 10 (generate_package) | Spec Section 4.4, 5.1-5.5 | Package | Phase 8 |
| Section 11 (gatekeep_package) | Spec Section 4.3-4.4 | Package | Phase 8 |
| Section 12 (review_package) | Spec Sections 1-5 | All | Phase 8 |
| Section 13 (refine_package) | Spec Section 5.1 | All | Phase 8 |
| Section 14 (prompt quality) | Spec Section 2.5, Standard Section 6 | Cross-cutting | All |

Total criteria count: 382

---

## Revision Notes

The following fixes were applied to address findings in REV_TEST_CRITERIA-001.md:

**CRITICAL Issue 1 (Missing gatekeep_composition_standard criteria):**
- Added Section 9A "Criteria for generate_composition_standard and gatekeep_composition_standard (Phase 6 - Composition Standard Quality and Gatekeeper QC)" with 38 new criteria (TC-CSN-001 through TC-CSN-022 for generation quality, TC-GCSN-001 through TC-GCSN-016 for gatekeeper verification).
- Section covers: composition standard structure (standard_name, standard_version, component_types_defined, schema_sections, extensibility_model), 3-layer completeness (Component Schema, Composition Format, Output Format), self-description capability, and dedicated gatekeeper verification for well-formedness, layer completeness, extensibility model, and self-description.

**CRITICAL Issue 2 (Missing generate_meta_composition_spec content quality criteria):**
- Added Section 9B "Criteria for generate_meta_composition_spec (Phase 7 - Meta Spec Quality)" with 28 new criteria (TC-MCS-001 through TC-MCS-028).
- Section covers: spec structure per COMPOSITION_SYSTEM_STANDARD.md Section 11.1 (5 required sections), component types definition, composition format rules, output format structure, examples per Section 11.2, self-bootstrapping capability, and self-validation.

**MAJOR Issue 3 (Missing action reuse criteria):**
- Added TC-OW-037 to Section 8.7 (Domain-Specific Requirements): workflow must verify action step implementations check for existing reusable actions before generating custom ones.
- Added TC-GP-031 and TC-GP-032 to Section 10.8 (new subsection "Action Reuse"): generate_package must verify action reuse, and must reference or reuse equivalent actions from the codebase.

**MINOR Issue 4 (TC-GP-004 naming convention specificity):**
- Enhanced TC-GP-004 (now item 259) to specify prompt file naming convention: "named sequentially (NN_step_name.txt matching the step sequence in workflow.toml)."
- Also added corresponding gatekeeper verification in TC-GPKG-007 (now item 297) requiring the gatekeeper to verify prompt file names match the NN_step_name.txt convention.

**Recommendation 5 (Update Appendix B):**
- Added two new rows to the traceability matrix for Section 9A and Section 9B with their spec sources.

**Recommendation 6 (Update total criteria count):**
- Updated total criteria count from 313 to 382 (313 original + 38 Section 9A + 28 Section 9B + 1 TC-OW-037 + 2 TC-GP-031/032 = 382).

**Additional adjustments for consistency:**
- Renumbered criteria from TC-OW-037 onward in Section 8.8 to TC-OW-038 through TC-OW-040 to accommodate the new TC-OW-037.
- Renumbered Section 10 criteria (previously TC-GP-001 through TC-GP-033) to TC-GP-001 through TC-GP-035 to accommodate the 2 new action reuse criteria (TC-GP-031, TC-GP-032).
- Renumbered Section 11 criteria (previously TC-GPKG-001 through TC-GPKG-018) to TC-GPKG-001 through TC-GPKG-018 (no net change in count, but sequential numbering preserved).
- Renumbered Section 12, 13, 14, and Appendix A criteria to maintain sequential global numbering.
- Updated TC-RP-014 data flow description to explicitly include composition standard and meta composition spec phases.
- Updated TC-RP-021 section reference from "sections 2 through 14" to "sections 2 through 16" to reflect new sections.

---

**End of Test Criteria Document**
