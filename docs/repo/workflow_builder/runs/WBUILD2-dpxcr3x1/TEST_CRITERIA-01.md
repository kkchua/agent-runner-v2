---
doc_type: "test_criteria"
lifecycle_status: "draft"
effective_version: "WBUILD2-dpxcr3x1"
created_at: "2026-08-08"
source_spec: "video_campaign_manuscript_v2.md"
composition_standard: "COMPOSITION_SYSTEM_STANDARD.md"
builder_architecture: "META_WORKFLOW_BUILDER_ARCHITECTURE.md"
builder_workflow: "workflow_builder_v2"
---

# Test Criteria: Composition System Workflow (workflow_builder_v2)

## 1. Spec Objective Summary

The composition system workflow builder must produce a complete agent-runner-v2 workflow package that implements the three-layer composition architecture defined in COMPOSITION_SYSTEM_STANDARD.md, applied to a specific domain specification (e.g., video_campaign_manuscript_v2.md). The end-to-end transformation is: a domain specification declaring component types with their properties and validation rules (Layer 1), composition definitions that reference components by ID with overrides and placeholder resolution (Layer 2), and output format rules that produce self-contained deliverables with all references expanded and placeholders filled (Layer 3) enter the builder. The builder generates a fully operational workflow package (workflow.toml, context_extensions.py, actions.py, prompts/*.txt, README.md) that can (a) scan and validate a component library against the declared schema, (b) resolve declarative composition definitions by looking up components, applying overrides, and resolving placeholders from data sources, and (c) assemble complete manuscripts with all component content expanded, overrides merged, placeholders filled, and downstream extraction contracts satisfied. The domain context for the reference spec is short-form video campaign production, where manuscripts coordinate hooks, scenes, voice direction, visual treatment, audio mood, text overlays, and transitions across platforms (TikTok, Reels, Shorts). The builder must follow the universal meta-workflow skeleton from META_WORKFLOW_BUILDER_ARCHITECTURE.md: TDD loop first (generate_test_criteria), then sequential layer design (component schema, composition format, output format), each gated by gatekeeper validation, followed by operational workflow design, package assembly, deterministic validation, review, refinement, and promotion.

---

## 2. Criteria for review_test_criteria and refine_test_criteria Steps (Phase 1)

These criteria verify that the Phase 1 TDD loop (test criteria review and refinement) produces reliable, evidence-based validation of the test criteria document itself.

### Review Quality

1. TC-RTC-001: The review must cite specific evidence from the test criteria document for each finding. Each finding must reference the criterion ID (e.g., TC-CS-004), the section it appears in, and the specific deficiency observed.
2. TC-RTC-002: The review must classify each finding by severity: CRITICAL (missing layer coverage or absent criteria for an entire step), MAJOR (inaccurate criteria or missing gatekeeper checks), MINOR (wording ambiguity or structural numbering issues). Each classification must include explicit justification.
3. TC-RTC-003: The review must produce a structured verdict (APPROVED or REJECTED) with a findings table listing each issue, its severity, its location in the document, and the recommended fix.
4. TC-RTC-004: The review must cover every section of the test criteria document. No section may be skipped. Each section must be evaluated for completeness, specificity, and traceability to the source specification.
5. TC-RTC-005: The review must verify the Appendix A summary table by independently counting criteria per section and comparing against the table's stated counts. Any discrepancy must be flagged.
6. TC-RTC-006: The review must verify the traceability matrix (Appendix B) by checking that each criterion prefix maps to the correct source specification and section.

### Refinement Quality

7. TC-RFTC-001: The refinement must address each finding from the review report individually. It must produce a fix log listing each finding ID, the fix applied, the section modified, and the before/after state.
8. TC-RFTC-002: The refinement must not change content that was not flagged by the review. Every modification must trace to a specific review finding.
9. TC-RFTC-003: The refinement must maintain consistent sequential numbering within and across sections after additions or deletions.
10. TC-RFTC-004: The refinement must update all dependent cross-references (summary table counts, traceability matrix entries, appendix tables) when structural changes are made.
11. TC-RFTC-005: The refinement must include a revision notes section at the end of the document recording each fix applied, referencing the review finding it addresses.
12. TC-RFTC-006: The refinement must not introduce new criteria that are not traceable to review findings or the original specification.

### Negative Criteria

13. TC-RTC-N01: The review MUST NOT self-certify the test criteria. The reviewer step is distinct from the generator step.
14. TC-RTC-N02: The review MUST NOT issue a verdict without specific evidence. A generic "looks good" assessment without findings is a critical defect.
15. TC-RFTC-N01: The refinement MUST NOT skip any finding from the review report. Every finding must be addressed (fixed or explicitly justified as not requiring a fix).
16. TC-RFTC-N02: The refinement MUST NOT self-certify its fixes. After refinement, the document must return to the review step for re-validation.

---

## 3. Criteria for generate_component_schema Step (Phase 2)

These criteria verify that the component schema (Layer 1 definition) is complete, correct, and extensible for the target domain.

### Type Completeness

17. TC-CS-001: The schema must define every component type listed in the domain specification's "Component Types" table. For the video campaign manuscript spec, this means all 7 types: hook, scene, voice_style, visual_direction, audio_mood, text_style, transition. Each type must have a corresponding type definition section in the schema.
18. TC-CS-002: The schema must include a type enumeration that explicitly lists all recognized component types. This enumeration must match exactly the types from the domain specification -- no more, no fewer.
19. TC-CS-003: For each component type, the schema must declare its cardinality (singleton vs ordered list) and required/optional status as specified in the domain spec (e.g., hook is singleton and required, scene is ordered list and required with 3-8 instances, text_style is singleton and optional).

### Common Properties

20. TC-CS-004: Every component type definition must include all common properties from COMPOSITION_SYSTEM_STANDARD.md Section 3.1: component_id (string, required), component_type (enum, required), name (string, required), version (string, required), description (string, required), duration_range (string, optional), platforms (array, optional), tags (array, optional).
21. TC-CS-005: Each common property must specify its data type, required/optional status, and a description of its purpose.
22. TC-CS-006: The component_id property must specify the uniqueness constraint (no duplicates within the library) and the naming convention (format: {type}-{descriptor}-{seq}, e.g., hook-dramatic-001).
23. TC-CS-007: The version property must specify semantic versioning format (MAJOR.MINOR.PATCH) as its validation constraint.

### Type-Specific Properties

24. TC-CS-008: Each component type must define its type-specific properties as declared in the domain specification. For example: hook must define hook_style (enum), hook_script (string), visual_cue (string), energy_level (enum); scene must define scene_purpose (enum), scene_script (string), visual_direction (string), duration_target (string), camera_work (string, optional).
25. TC-CS-009: Each type-specific property must specify: property name, data type (string, enum, array, object), required/optional status, and a human-readable description.
26. TC-CS-010: Enum-type properties must list all valid values explicitly. For example: hook_style must list dramatic_reveal, question_hook, statistic_hook, visual_reveal, challenge_hook; energy_level must list low, medium, high; scene_purpose must list problem, solution, demo, testimonial, CTA, education, comparison.
27. TC-CS-011: Type-specific properties must not duplicate or conflict with common properties. A type-specific property must not be named component_id, component_type, name, version, or description.

### Validation Rules

28. TC-CS-012: The schema must define explicit validation rules for each component type beyond "required fields present." Rules must include: enum value validation (only declared values accepted), duration format validation (pattern \d+(-\d+)?s), placeholder syntax validation ({placeholder_name} in hook_script and scene_script), word count constraints (e.g., hook_script max 50 words).
29. TC-CS-013: Each validation rule must be stated in implementable form: condition (what to check), expected result (what constitutes pass), and error message (what to report on failure). Vague rules like "must be valid" are not acceptable.
30. TC-CS-014: The schema must define cross-property validation rules where applicable (e.g., if hook_style is visual_reveal, then visual_cue is mandatory; if scene has duration_target > 30s, then scene_script must have adequate word count).

### Extensibility Model

31. TC-CS-015: The schema must document how new component types can be added without breaking existing compositions: (a) define the new type's specific properties, (b) register the type in the type enumeration, (c) existing compositions continue to work because they reference by component_id not type.
32. TC-CS-016: The schema must specify versioning rules for type-specific property changes: MAJOR for breaking schema changes, MINOR for new optional properties, PATCH for documentation fixes only.
33. TC-CS-017: The schema must NOT require modifications to the common property set when adding new types. Common properties are stable; only type-specific properties extend.

### Examples

34. TC-CS-018: The schema must include at least one complete example component per component type. Each example must be a valid instance that passes all validation rules defined for that type.
35. TC-CS-019: Each example component must use the component file format defined in COMPOSITION_SYSTEM_STANDARD.md Section 3.3 (markdown file with YAML frontmatter containing common + type-specific properties, followed by markdown body with usage notes).
36. TC-CS-020: Example components must demonstrate realistic property values relevant to the domain (e.g., a hook with hook_style=dramatic_reveal and a real hook_script), not placeholder strings like "TODO" or "example_value".

### Self-Validation

37. TC-CS-021: The schema must include a self-check section that verifies all component types from the domain specification are covered. This must be an explicit checklist or cross-reference table mapping spec type names to schema definitions.
38. TC-CS-022: The self-check must flag any spec type that is missing from the schema definition, with the specific type name and the spec section where it was declared.

### Negative Criteria

39. TC-CS-N01: The schema MUST NOT define component types that are not present in the domain specification. Every type must trace to a spec source.
40. TC-CS-N02: The schema MUST NOT hardcode domain-specific values into the common properties. Common properties are domain-agnostic.
41. TC-CS-N03: The schema MUST NOT allow type-specific properties to override common property semantics (e.g., redefining component_id as optional).

---

## 4. Criteria for gatekeep_component_schema Step (Phase 2)

These criteria verify that the gatekeeper for the component schema performs thorough, evidence-based validation.

### Type Completeness Gate

42. TC-GCS-001: The gatekeeper must verify that ALL component types from the domain specification are defined in the schema. It must produce an explicit type coverage matrix listing each spec type and whether it is defined (YES/NO) in the schema.
43. TC-GCS-002: If any spec type is missing, the gatekeeper must REJECT with a finding that names the missing type(s) and references the spec section where each was declared.
44. TC-GCS-003: The gatekeeper must verify that no extra types exist in the schema beyond those declared in the spec. Each schema type must trace to a spec source.

### Schema Conformance Gate

45. TC-GCS-004: The gatekeeper must verify that each component type definition includes all required common properties (component_id, component_type, name, version, description) with correct types and required/optional markers.
46. TC-GCS-005: The gatekeeper must verify that each component type definition includes type-specific properties with complete metadata: name, data type, required/optional, description, and valid enum values where applicable.
47. TC-GCS-006: The gatekeeper must verify that enum-type properties have their valid values explicitly enumerated, not left as open strings. For example, hook_style must list all 5 valid values from the spec.

### Validation Rules Gate

48. TC-GCS-007: The gatekeeper must verify that validation rules exist for each component type. A type with zero validation rules must be flagged as a MAJOR deficiency.
49. TC-GCS-008: The gatekeeper must verify that each validation rule is stated in implementable form (condition + expected result + error message), not as vague prose like "must be valid".
50. TC-GCS-009: The gatekeeper must verify that cross-property validation rules are defined where type-specific properties have dependencies on each other.

### Uniqueness Gate

51. TC-GCS-010: The gatekeeper must verify that component_ids across all example components are unique. No two examples may share the same component_id.
52. TC-GCS-011: The gatekeeper must verify that component_ids follow the naming convention specified in the schema ({type}-{descriptor}-{sequence}).

### Evidence Requirement

53. TC-GCS-012: The gatekeeper verdict (APPROVED or REJECTED) must be justified with specific evidence. An APPROVED verdict must list the checks performed and confirm each passed. A REJECTED verdict must list each failing check with the specific finding and severity.
54. TC-GCS-013: The gatekeeper MUST NOT issue an APPROVED verdict without explicitly verifying type completeness against the spec. A statement like "schema looks good" is insufficient; it must name each type verified.
55. TC-GCS-014: The gatekeeper report must reference the specific artifact file(s) it validated, including file path and section numbers where findings were located.

### Negative Criteria

56. TC-GCS-N01: The gatekeeper MUST NOT skip validation of type-specific properties by only checking common properties.
57. TC-GCS-N02: The gatekeeper MUST NOT approve based on structural validity alone (e.g., "YAML parses correctly") without semantic checks (e.g., "all spec types covered, all enum values listed").

---

## 5. Criteria for generate_composition_format Step (Phase 3)

These criteria verify that the composition format (Layer 2 definition) correctly specifies how components are assembled into deliverables.

### Composition Structure

58. TC-CF-001: The format must define a YAML-based composition structure with these required top-level fields: composition_id (string, unique), name (string, human-readable), target_metadata (object, domain-specific metadata), data_sources (object, placeholder resolution data), component_bindings (object, assembly instructions).
59. TC-CF-002: The target_metadata must include domain-specific fields as declared in the spec: duration_target (string), target_platforms (array), campaign_type (string), brand (string). Each field must have type and required/optional designation.
60. TC-CF-003: The data_sources section must define available data sources and the fields each provides: product_master (product_name, product_category, brand_name, key_benefit, pain_point, target_audience), campaign_input (campaign_name, call_to_action_url, seasonal_angle, campaign_tagline), platform_config (platform_defaults, aspect_ratios, duration_limits, trending_formats -- optional).
61. TC-CF-004: The component_bindings section must support two binding modes: singleton bindings (one component per slot, for voice_style, visual_direction, etc.) and ordered list bindings (array of components, for scenes and transitions).

### Reference Pattern

62. TC-CF-005: The format must explicitly state that components are referenced by component_id, not copied or inlined. The composition file must never contain the full content of a component -- only the reference ID and any overrides.
63. TC-CF-006: The format must define the resolution process: at generation time, the workflow looks up each component_id in the component library, retrieves the full component content, merges any overrides (override wins on conflict), and produces the expanded output.
64. TC-CF-007: The format must include an example composition that demonstrates the reference pattern with at least 3 component_bindings referencing different component_ids, including both singleton and list bindings.

### Override Mechanism

65. TC-CF-008: The format must define override semantics: overrides are merged with the component's base properties, with override values taking precedence on conflict. Non-overridden properties retain their component-defined values.
66. TC-CF-009: The format must specify that overrides must conform to the component type's schema. An override cannot introduce properties that do not exist in the type definition, and must respect data type constraints and enum value restrictions.
67. TC-CF-010: The format must include an example showing overrides in action -- a composition that overrides at least one property of a referenced component, with the override value containing a {placeholder} resolved from a data source.

### Placeholder Resolution

68. TC-CF-011: The format must define the placeholder syntax as {placeholder_name} (curly braces around a field name). Placeholders can appear in override values and in component property values (specifically hook_script and scene_script).
69. TC-CF-012: The format must define how placeholders are resolved: looked up from declared external data sources (Product Master, Campaign Input, Platform Config). The format must specify which data sources provide which fields.
70. TC-CF-013: The format must define the behavior for unresolved placeholders: flagged in the output as {UNRESOLVED: field_name} rather than silently omitted or left as raw {placeholder} syntax.
71. TC-CF-014: The format must specify placeholder priority rules when multiple data sources provide the same field (e.g., Product Master fields take priority over Campaign Input).

### Binding Rules

72. TC-CF-015: The format must define binding rules for each binding slot, specifying: binding name, component type, cardinality (singleton vs ordered list), required/optional status. For the video manuscript domain: opening (hook, singleton, required), scenes (scene, ordered list, required, 3-8), voice (voice_style, singleton, required), visuals (visual_direction, singleton, required), audio (audio_mood, singleton, required), text (text_style, singleton, optional), transitions (transition, ordered list, required, count = scenes count - 1).
73. TC-CF-016: For ordered bindings, the format must define how ordering is determined (by position in the YAML array) and any constraints (e.g., transition count must equal scene count minus 1).
74. TC-CF-017: The format must explicitly state which bindings are required vs optional and the validation behavior for each case: missing required binding = error, absent optional binding = no error.

### Self-Validation

75. TC-CF-018: The format must include a self-check section that verifies all composition rules are covered: reference pattern, override mechanism, placeholder resolution, binding rules, ordering rules, optional bindings. Each rule must have a corresponding example or explicit statement.
76. TC-CF-019: The self-check must verify that the example composition(s) collectively exercise all defined features (reference, override, placeholder, ordering, optional omission).

### Negative Criteria

77. TC-CF-N01: The format MUST NOT allow compositions to inline full component content instead of referencing by component_id.
78. TC-CF-N02: The format MUST NOT allow overrides to introduce properties not defined in the component type schema.
79. TC-CF-N03: The format MUST NOT silently ignore unresolved placeholders. All must be resolved or explicitly flagged as {UNRESOLVED: field_name}.

---

## 6. Criteria for gatekeep_composition_format Step (Phase 3)

These criteria verify that the gatekeeper for the composition format enforces reference integrity, override conformance, and placeholder resolvability.

### Reference Integrity Gate

80. TC-GCF-001: The gatekeeper must verify that every component_id referenced in every composition exists in the component library (or component schema examples). It must produce a reference list with status (RESOLVED/MISSING) for each reference.
81. TC-GCF-002: If any referenced component_id does not exist, the gatekeeper must REJECT with a finding that names the missing component_id, the composition it appears in, and the binding slot.
82. TC-GCF-003: The gatekeeper must verify that referenced component_ids match the expected component_type for their binding slot. A binding declared for a "hook" slot must not reference a component of type "scene".

### Override Conformance Gate

83. TC-GCF-004: The gatekeeper must verify that all override properties in compositions conform to the referenced component's type schema. Each override key must be a valid property for that component type.
84. TC-GCF-005: The gatekeeper must verify that override values respect data type constraints (e.g., a string property must not be overridden with a number, an enum property must use a valid enum value).
85. TC-GCF-006: The gatekeeper must verify that enum-type properties are only overridden with values from their valid value list.

### Placeholder Resolvability Gate

86. TC-GCF-007: The gatekeeper must verify that all {placeholder} values in compositions can be resolved from the declared data sources. It must produce a placeholder inventory listing each placeholder, its source, and resolution status (RESOLVABLE/UNRESOLVABLE).
87. TC-GCF-008: If a placeholder cannot be resolved from any declared data source, the gatekeeper must flag it with severity MAJOR (not CRITICAL, since unresolved placeholders are handled with {UNRESOLVED: field_name} flagging in the output).
88. TC-GCF-009: The gatekeeper must verify that the data source declarations in the composition match the actual data source availability.

### Required Bindings Gate

89. TC-GCF-010: The gatekeeper must verify that all required bindings are present in each composition. Missing required bindings must be flagged as CRITICAL.
90. TC-GCF-011: The gatekeeper must verify that optional bindings that are present contain valid content (valid component_id reference, conforming overrides).

### Ordering Constraints Gate

91. TC-GCF-012: The gatekeeper must verify that ordered bindings satisfy ordering constraints (e.g., transition count = scene count - 1, scenes are in narrative order, scene count between 3-8).
92. TC-GCF-013: The gatekeeper must verify that singleton bindings contain exactly one component reference (not a list).

### Evidence Requirement

93. TC-GCF-014: The gatekeeper verdict must include a composition-by-composition analysis. Each composition must be individually assessed with specific findings.
94. TC-GCF-015: The gatekeeper MUST NOT issue an APPROVED verdict if any CRITICAL findings exist. CRITICAL findings always require REJECT.
95. TC-GCF-016: The gatekeeper report must list the total count of compositions checked, references verified, overrides validated, and placeholders resolved.

### Negative Criteria

96. TC-GCF-N01: The gatekeeper MUST NOT skip reference integrity checks by only verifying YAML syntax.
97. TC-GCF-N02: The gatekeeper MUST NOT approve compositions with broken references, even if the overall structure is valid.

---

## 7. Criteria for generate_output_format Step (Phase 4)

These criteria verify that the output format (Layer 3 definition) correctly specifies how resolved deliverables are structured.

### Output Structure

98. TC-OF-001: The format must define the output as a markdown file with YAML frontmatter containing: composition_id, composition_name, metadata (domain-specific fields), component_count (integer), generation_date (ISO date), lifecycle_status (enum: draft/review/final), unresolved_placeholder_count (integer).
99. TC-OF-002: The format must define all required output sections. For the video manuscript domain: Opening (Hook), Voice Direction, Visual Treatment, Scene-by-Scene Breakdown (with interleaved transitions), Audio Direction, Text Overlay (if text_style binding present), Production Notes. Each section must have a defined purpose and content specification.
100. TC-OF-003: The format must define the internal structure of each section -- what resolved component data populates it, how it is formatted, and how overrides are reflected.
101. TC-OF-004: The format must include a complete example output skeleton demonstrating all required sections with realistic content structure.

### Resolution Rules

102. TC-OF-005: The format must specify that all component_id references are expanded in the output. Every reference is replaced with the full component content (common properties + type-specific properties + overrides applied).
103. TC-OF-006: The format must define the expansion process: look up component by ID, apply overrides (override wins), merge with base properties, render into the appropriate output section.
104. TC-OF-007: The format must specify how ordered list bindings are rendered: each component rendered in sequence order with clear section breaks and numbering. For scenes, each scene gets its own subsection; transitions are interleaved between scenes (scene_1 -> transition_1 -> scene_2 -> transition_2 -> ... -> scene_N).
105. TC-OF-008: The format must specify how singleton bindings are rendered: the component's properties are presented in a dedicated section (e.g., "Voice Direction" section populated from voice_style component).

### Placeholder Filling

106. TC-OF-009: The format must specify that all {placeholder} values are replaced with values from the resolved data sources. The replacement must be exact -- no partial replacements or leftover syntax.
107. TC-OF-010: The format must specify the handling of unresolved placeholders: rendered as {UNRESOLVED: field_name} in the output, making it immediately visible to reviewers that a value is missing.
108. TC-OF-011: The format must include a placeholder resolution summary in the output (either inline in Production Notes or as metadata) listing all placeholders encountered, their source, and resolution status.

### Self-Contained Requirement

109. TC-OF-012: The format must guarantee that the output is self-contained -- a reader can understand and use the deliverable without referencing the component library, composition file, or data sources.
110. TC-OF-013: The format must ensure that no component_id references appear in the final output as unresolved references. A residual "see component_id: hook-001" in the output is a defect.
111. TC-OF-014: The format must ensure the output includes enough context for downstream workflows to extract their specific concerns without needing the original components.

### Downstream Contracts

112. TC-OF-015: The format must define extraction contracts for downstream workflows, specifying what fields/sections downstream workflows can expect to find and in what format. For example: voiceover generation extracts scene_script fields in order combined with voice_style properties.
113. TC-OF-016: The format must specify that the output is downstream-agnostic -- it describes WHAT the deliverable is, not HOW to produce it. Downstream workflows determine their own production logic.
114. TC-OF-017: The format must include platform-specific notes in the Production Notes section covering aspect ratio safety, duration limits, and trending format considerations.

### Unresolved Handling

115. TC-OF-018: The format must define the exact syntax for unresolved placeholders: {UNRESOLVED: field_name}. This must be consistent throughout the output -- no alternative syntaxes like "TODO", "[MISSING]", or raw {placeholder}.
116. TC-OF-019: The format must specify that outputs with unresolved placeholders are valid but must be flagged with lifecycle_status "draft" (not "final") until all placeholders are resolved.

### Self-Validation

117. TC-OF-020: The format must include a self-check section that verifies all output sections are covered. Each required section must have a definition, content specification, and example content.
118. TC-OF-021: The self-check must verify that the example output demonstrates all resolution rules (reference expansion, placeholder filling, override application, unresolved flagging).

### Negative Criteria

119. TC-OF-N01: The format MUST NOT produce outputs that require the reader to consult the component library to understand the content.
120. TC-OF-N02: The format MUST NOT leave raw {placeholder} syntax in the output without either resolving or flagging as {UNRESOLVED: field_name}.
121. TC-OF-N03: The format MUST NOT omit any required section from the output. Missing sections are a defect.

---

## 8. Criteria for gatekeep_output_format Step (Phase 4)

These criteria verify that the gatekeeper for the output format enforces reference expansion, placeholder completeness, and section integrity.

### Reference Expansion Gate

122. TC-GOF-001: The gatekeeper must verify that all component_id references in the output are fully expanded. It must scan the output for any residual component_id references and flag each occurrence.
123. TC-GOF-002: The gatekeeper must verify that expanded content matches the source component. For each expanded component, the gatekeeper must confirm the output contains all common properties and type-specific properties, with overrides correctly applied.
124. TC-GOF-003: The gatekeeper must verify that override application is correct. If a composition overrides a property, the output must show the override value, not the original component value.

### Placeholder Completeness Gate

125. TC-GOF-004: The gatekeeper must verify that all placeholders are either resolved (replaced with actual values) or flagged ({UNRESOLVED: field_name}). No raw {placeholder} syntax may appear without flagging.
126. TC-GOF-005: The gatekeeper must produce a placeholder resolution report listing each placeholder, its expected source, and its resolution status (RESOLVED/UNRESOLVED).
127. TC-GOF-006: The gatekeeper must verify that the {UNRESOLVED: field_name} syntax is used consistently -- no alternative flagging syntax is present.

### Section Completeness Gate

128. TC-GOF-007: The gatekeeper must verify that all required output sections are present in the output. Missing sections must be flagged as CRITICAL.
129. TC-GOF-008: The gatekeeper must verify that each section contains content appropriate to its defined purpose. An empty section or a section with only placeholder content must be flagged.
130. TC-GOF-009: The gatekeeper must verify that the YAML frontmatter is present and contains all required fields (composition_id, composition_name, metadata, component_count, generation_date, lifecycle_status, unresolved_placeholder_count).

### Consistency Gate

131. TC-GOF-010: The gatekeeper must verify no contradictions exist between sections. For example, the Voice Direction section must not specify a pace that contradicts the energy_level in the Opening section.
132. TC-GOF-011: The gatekeeper must verify that component_count in frontmatter matches the actual number of distinct components expanded in the output.
133. TC-GOF-012: The gatekeeper must verify that lifecycle_status is appropriate: if any {UNRESOLVED: field_name} flags exist, status must be "draft", not "final".
134. TC-GOF-013: The gatekeeper must verify timing consistency: scene durations sum to within duration_target range, transition count = scene count - 1.

### Downstream Feasibility Gate

135. TC-GOF-014: The gatekeeper must verify that downstream workflows can extract their required concerns from the output. For each declared extraction contract, the gatekeeper must confirm the relevant data is present and accessible.
136. TC-GOF-015: The gatekeeper must verify that the output structure supports programmatic extraction (consistent section headings, predictable field placement, machine-parseable metadata).

### Evidence Requirement

137. TC-GOF-016: The gatekeeper verdict must include section-by-section analysis with specific findings per section.
138. TC-GOF-017: The gatekeeper MUST NOT approve an output with unresolved CRITICAL findings (missing sections, broken references, contradictions).

### Negative Criteria

139. TC-GOF-N01: The gatekeeper MUST NOT approve based on overall "look and feel" without verifying each section individually.
140. TC-GOF-N02: The gatekeeper MUST NOT ignore placeholder resolution status when determining lifecycle_status correctness.

---

## 9. Criteria for generate_operational_workflow Step (Phase 5)

These criteria verify that the operational workflow design correctly sequences all phases and steps for the composition system.

### Workflow Phases

141. TC-OW-001: The operational workflow design must define all five composition system phases from COMPOSITION_SYSTEM_STANDARD.md Section 6.1: Scan phase (discover and validate components in the library), Plan phase (resolve compositions against inventory, identify overrides and placeholders), Generate phase (expand all components, apply overrides, resolve placeholders, assemble outputs), Review phase (quality review of generated outputs), Refine phase (fix issues, conditional). These are the phases of the TARGET workflow being built, not the builder's own phases.
142. TC-OW-002: Each phase must have a clear objective statement describing what the phase accomplishes and what artifacts it produces.
143. TC-OW-003: Phase boundaries must be explicit -- the output of one phase is the defined input to the next phase.

### Step Sequence

144. TC-OW-004: The step sequence must be logically ordered: scan before plan, plan before generate, generate before review, review before refine. No step may execute before its required inputs are available.
145. TC-OW-005: The step sequence must be complete -- no gaps. Every necessary operation (component discovery, schema validation, composition parsing, reference resolution, output assembly, quality review, issue refinement) must have a dedicated step.
146. TC-OW-006: The step sequence must include at least one action step for deterministic operations (component scanning, file I/O, schema validation) and at least one prompt-driven step for LLM-judgment operations (output generation, quality review, refinement).

### Artifact Contracts

147. TC-OW-007: Every step must declare its input artifacts (artifact keys) and output artifacts (artifact keys). No step may consume an artifact that no prior step produces.
148. TC-OW-008: Artifact keys must follow the naming convention from the spec: COMPONENT_INVENTORY_FILE, VALIDATION_REPORT_FILE, RESOLUTION_PLAN_FILE, OUTPUT_FILE, REVIEW_FILE_SUGGESTED.
149. TC-OW-009: The workflow must declare all input artifacts from the spec Section 5.2: COMPONENT_LIBRARY_DIR, COMPOSITIONS_DIR, DATA_SOURCE_DIR.
150. TC-OW-010: The workflow must declare all output artifacts from the spec Section 5.3: COMPONENT_INVENTORY_FILE, VALIDATION_REPORT_FILE, RESOLUTION_PLAN_FILE, OUTPUT_FILE, REVIEW_FILE_SUGGESTED.

### Action Implementations

151. TC-OW-011: Deterministic operations must be identified as action steps. The spec identifies two: scan_components (scan library, parse frontmatter, classify by type, validate) and plan_compositions (resolve references, validate overrides, check binding constraints, inventory placeholders).
152. TC-OW-012: Each action step must specify: action name, input parameters, output artifacts, error handling behavior, and whether it reuses an existing action or is new.
153. TC-OW-013: The workflow must identify opportunities for action reuse from existing workflows (e.g., validate_workflow_bundle from workflow_builder_v1).

### Prompt-Driven Steps

154. TC-OW-014: LLM-judgment steps must be identified as prompt-driven: output generation (assembling human-readable manuscripts), quality review (assessing output against quality requirements), refinement (fixing semantic issues).
155. TC-OW-015: Each prompt-driven step must specify: step name, prompt template reference, input artifacts injected as context, expected output artifact, and success criteria.
156. TC-OW-016: Prompt-driven steps must specify which upstream artifact content is injected into the prompt template for context continuity (e.g., generate_output needs COMPONENT_INVENTORY_FILE, RESOLUTION_PLAN_FILE, and the component schema).

### Routing

157. TC-OW-017: Each step must define its routing: onsuccess (next step on success) and optionally on_reject_refine (refinement loop on rejection).
158. TC-OW-018: The review step must route to on_reject_refine when issues are found, creating a review-refine loop. The refine step must route back to review for re-validation.
159. TC-OW-019: The workflow must define an exhaustion condition for the review-refine loop (e.g., maximum 2 iterations) and a terminal failure path when exhaustion is reached.
160. TC-OW-020: The terminal step must be step_completion, which marks the workflow as successfully finished.

### Self-Validation

161. TC-OW-021: The workflow design must include a self-check that verifies all five composition system phases (scan, plan, generate, review, refine) are covered by at least one step.
162. TC-OW-022: The self-check must verify that the artifact flow is complete -- every step's inputs are produced by prior steps or declared as workflow inputs.
163. TC-OW-023: The self-check must verify that the step sequence has no orphan steps (steps with no incoming or outgoing routing).

### Negative Criteria

164. TC-OW-N01: The workflow MUST NOT define steps that have no corresponding phase in the composition system standard.
165. TC-OW-N02: The workflow MUST NOT skip the scan phase -- component discovery and validation must precede composition resolution.
166. TC-OW-N03: The workflow MUST NOT have prompt-driven steps for purely deterministic operations (e.g., file scanning must be an action, not a prompt).

---

## 10. Criteria for gatekeep_operational_workflow Step (Phase 5)

These criteria verify that the gatekeeper for the operational workflow enforces phase completeness, data flow, routing validity, and step type correctness.

### Phase Completeness Gate

167. TC-GOW-001: The gatekeeper must verify that all five composition system phases are represented in the step sequence. It must produce a phase coverage matrix: Scan (covered by step X), Plan (covered by step Y), Generate (covered by step Z), Review (covered by step W), Refine (covered by step V).
168. TC-GOW-002: If any phase is missing, the gatekeeper must REJECT with a finding that names the missing phase and explains its role in the composition system.

### Data Flow Gate

169. TC-GOW-003: The gatekeeper must verify that artifact flow is correct from workflow inputs through all steps to workflow outputs. It must trace each artifact from producer to consumer and flag any broken chains.
170. TC-GOW-004: The gatekeeper must verify that every step's declared input artifacts are produced by a prior step or declared as workflow-level inputs.
171. TC-GOW-005: The gatekeeper must verify that every step's declared output artifacts are consumed by at least one subsequent step or declared as workflow-level outputs.

### Routing Validity Gate

172. TC-GOW-006: The gatekeeper must verify that every step has valid onsuccess routing to a subsequent step (except the terminal step, which has no successor).
173. TC-GOW-007: The gatekeeper must verify that review-refine loops are correctly wired: review routes to refine on rejection, refine routes back to review for re-validation.
174. TC-GOW-008: The gatekeeper must verify that exhaustion conditions are defined for all review-refine loops, with a terminal failure step on exhaustion.
175. TC-GOW-009: The gatekeeper must verify there are no routing cycles outside of the explicit review-refine loop pattern.

### Type Consistency Gate

176. TC-GOW-010: The gatekeeper must verify that each step's type (action vs prompt) matches the nature of the task. Deterministic operations must be actions; judgment operations must be prompts.
177. TC-GOW-011: The gatekeeper must verify that action steps have complete specifications: action name, input parameters, output artifacts, error handling.
178. TC-GOW-012: The gatekeeper must verify that prompt-driven steps have complete specifications: prompt template reference, context injection plan, expected output, success criteria.

### Action Feasibility Gate

179. TC-GOW-013: The gatekeeper must verify that each action step's specification is implementable in Python within the agent-runner-v2 framework. Actions must use available libraries and follow the action module pattern.
180. TC-GOW-014: The gatekeeper must verify that action steps claiming to reuse existing actions (e.g., validate_workflow_bundle) reference actions that actually exist in the codebase.
181. TC-GOW-015: The gatekeeper must verify that no action step requires capabilities beyond the agent-runner-v2 runtime.

### Evidence Requirement

182. TC-GOW-016: The gatekeeper verdict must include a step-by-step analysis with routing diagram, data flow trace, and specific findings per step.
183. TC-GOW-017: The gatekeeper MUST NOT approve a workflow with broken artifact chains or missing phases.

### Negative Criteria

184. TC-GOW-N01: The gatekeeper MUST NOT approve based on step count alone without verifying phase coverage and data flow.
185. TC-GOW-N02: The gatekeeper MUST NOT ignore routing validity. Even if all steps exist, incorrect routing is a REJECT.

---

## 11. Criteria for generate_package Step (Phase 6)

These criteria verify that the package generation produces all required files with correct content.

### File Completeness

186. TC-GP-001: The generated package must include workflow.toml -- the workflow manifest defining all steps, routing, artifact declarations, and coder role assignments.
187. TC-GP-002: The generated package must include context_extensions.py -- the artifact key registration and context injection module that resolves artifact placeholders.
188. TC-GP-003: The generated package must include a prompts/ directory with one .txt file per prompt-driven step identified in the operational workflow.
189. TC-GP-004: The generated package must include README.md -- user guide describing the workflow's purpose, inputs, outputs, execution command, and expected behavior.
190. TC-GP-005: If the operational workflow includes action steps beyond reusable existing actions, the package must include actions.py with implementations for those custom actions.
191. TC-GP-006: If the workflow requires external configuration (API keys, service URLs), the package must include .env.sample and/or config.json.sample templates.

### Design Fidelity

192. TC-GP-007: The workflow.toml must exactly match the operational workflow design -- same steps, same routing, same artifact declarations, same coder roles. No deviation between design and implementation.
193. TC-GP-008: The context_extensions.py must register all artifact keys declared in the operational workflow. Every artifact key referenced in workflow.toml must have a corresponding path registration in context_extensions.py.
194. TC-GP-009: Each prompt template file in prompts/ must correspond to a prompt-driven step in the operational workflow. The file name must match the step name or step sequence number.

### Component Schema Embedding

195. TC-GP-010: The component schema defined in Phase 2 must be embedded or referenced in the generated package. Either the schema is included as a standalone file or it is embedded within the workflow's validation action or prompt templates.
196. TC-GP-011: The component schema in the package must be identical to the schema validated by the gatekeeper in Phase 2. No modifications or omissions are permitted.

### Composition Format Embedding

197. TC-GP-012: The composition format defined in Phase 3 must be embedded or referenced in the generated package. Either the format specification is included as a standalone file or it is documented in the README and enforced by validation logic or prompt instructions.
198. TC-GP-013: The composition format in the package must be identical to the format validated by the gatekeeper in Phase 3.

### Output Format Embedding

199. TC-GP-014: The output format defined in Phase 4 must be embedded or referenced in the generated package. The output generation prompt must encode the format rules, or a separate output format specification file must be included.
200. TC-GP-015: The output format in the package must be identical to the format validated by the gatekeeper in Phase 4.

### Prompt Quality

201. TC-GP-016: Each prompt template must have a clear objective section stating what the LLM must produce.
202. TC-GP-017: Each prompt template must list all input artifacts that are injected as context, using {ARTIFACT_KEY} placeholder syntax for resolution by context_extensions.py.
203. TC-GP-018: Each prompt template must specify the exact output file path using {ARTIFACT_KEY} placeholder syntax and the required format (YAML frontmatter, markdown body, etc.).
204. TC-GP-019: Each prompt template must include a self-critic section instructing the LLM to verify its own output before completing.
205. TC-GP-020: Each prompt template must include explicit file-writing instructions -- the LLM must be told to use file-writing tools to create actual files on disk, not merely describe what the files should contain.

### Action Implementations

206. TC-GP-021: If custom action steps exist in the operational workflow, actions.py must contain Python implementations for each. Each action must follow the agent-runner-v2 action module pattern.
207. TC-GP-022: Each action implementation must accept the parameters declared in the operational workflow's step specification and produce the declared output artifacts.
208. TC-GP-023: Action implementations must include error handling for expected failure modes (file not found, invalid format, validation failure).

### Self-Validation

209. TC-GP-024: The generate_package step must include a self-check that verifies all files implied by the operational workflow are generated. This must be a file checklist comparing expected files to actual generated files.
210. TC-GP-025: The self-check must flag any missing files and any extra files not implied by the operational workflow.

### Negative Criteria

211. TC-GP-N01: The package MUST NOT contain files not implied by the operational workflow design. No "bonus" files or unrelated content.
212. TC-GP-N02: The package MUST NOT contain hardcoded path strings. All paths must use the layered constant system or {ARTIFACT_KEY} placeholders.
213. TC-GP-N03: The package MUST NOT include prompt templates that output to stdout instead of writing files to disk.

---

## 12. Criteria for validate_package_deterministic Step (Phase 6)

These criteria verify that the deterministic validation action performs thorough structural checks on the generated package.

### File Structure Validation

214. TC-VPD-001: The action must parse workflow.toml as valid TOML and verify it contains all required sections: [workflow], [[steps]], and [step.artifacts] declarations. A malformed manifest must be flagged as CRITICAL.
215. TC-VPD-002: The action must verify that all prompt files referenced in workflow.toml step definitions exist on disk in the prompts/ directory. Each missing prompt file must be flagged with the step name and expected file path.
216. TC-VPD-003: The action must verify that context_extensions.py exists and is syntactically valid Python. It must check that the file contains artifact key path registrations for all artifact keys declared in workflow.toml.
217. TC-VPD-004: If actions.py is present, the action must verify it is syntactically valid Python and that it contains function implementations for all action steps declared in workflow.toml that are not marked as reusable existing actions.

### Artifact Key Cross-Validation

218. TC-VPD-005: The action must verify that every artifact key declared in workflow.toml [step.artifacts] sections has a corresponding path registration in context_extensions.py. Unregistered artifact keys must be flagged as errors.
219. TC-VPD-006: The action must detect duplicate artifact key registrations in context_extensions.py.
220. TC-VPD-007: The action must verify that artifact key references in prompt templates (using {ARTIFACT_KEY} syntax) correspond to keys declared in workflow.toml.

### Routing Validation

221. TC-VPD-008: The action must verify that the step sequence in workflow.toml forms a valid directed acyclic graph (DAG). Every step's onsuccess target must reference an existing step name (except the terminal step).
222. TC-VPD-009: The action must verify there are no orphan steps -- every step must have at least one incoming route (except the first step) and at least one outgoing route (except the terminal step).
223. TC-VPD-010: The action must verify that review-refine loops are correctly paired: each on_reject_refine target routes back to a review step, and the loop has an exhaustion condition defined.

### Validation Report Format

224. TC-VPD-011: The action must produce a structured validation report (VALIDATION_REPORT_FILE) that includes: files checked (list with pass/fail per file), artifact key cross-validation results, routing validation results, total error count, and overall verdict (PASS/FAIL).
225. TC-VPD-012: The validation report must list each error found with its severity (CRITICAL, MAJOR, MINOR), the file where it was detected, and a description of the issue.
226. TC-VPD-013: The action must be fully deterministic -- given the same input files, it must always produce the same validation report.

### Negative Criteria

227. TC-VPD-N01: The action MUST NOT skip validation of any file declared in the workflow package.
228. TC-VPD-N02: The action MUST NOT report a PASS verdict when any CRITICAL errors are present.

---

## 13. Criteria for gatekeep_package Step (Phase 6)

These criteria verify that the gatekeeper for the package performs thorough file-level and cross-file validation.

### File Checklist

229. TC-GPK-001: The gatekeeper must verify that ALL expected files exist on disk. It must produce a file checklist with status (PRESENT/MISSING) for each expected file: workflow.toml, context_extensions.py, actions.py (if applicable), prompts/*.txt, README.md, .env.sample (if applicable), config.json.sample (if applicable).
230. TC-GPK-002: The gatekeeper must verify that no unexpected files exist in the package directory. Every file must trace to a requirement from the operational workflow.

### Design Fidelity

231. TC-GPK-003: The gatekeeper must verify that workflow.toml matches the operational workflow design by comparing: step names, step sequence, routing (onsuccess, on_reject_refine), artifact declarations, coder role assignments.
232. TC-GPK-004: The gatekeeper must verify that context_extensions.py registers all artifact keys used in workflow.toml. Any artifact key in the manifest without a path registration is a defect.
233. TC-GPK-005: The gatekeeper must verify that the prompts/ directory contains exactly one file per prompt-driven step, with filenames matching step names or sequence numbers.

### Composition Integrity

234. TC-GPK-006: The gatekeeper must verify that the component schema, composition format, and output format are consistent across all files. The schema referenced in validation actions must match the schema from Phase 2; the composition rules in prompts must match the format from Phase 3; the output structure in generation prompts must match the format from Phase 4.
235. TC-GPK-007: The gatekeeper must verify that no contradictions exist between files -- for example, workflow.toml declaring an artifact key that context_extensions.py does not register, or a prompt template referencing an undeclared artifact key.

### Prompt Completeness

236. TC-GPK-008: The gatekeeper must verify that each prompt template has: objective section, reference inputs section, output instructions section, self-critic section, file-writing instructions.
237. TC-GPK-009: The gatekeeper must verify that prompt templates use {ARTIFACT_KEY} syntax for all artifact references, not hardcoded paths.

### Scope Check

238. TC-GPK-010: The gatekeeper must detect scope shrink -- any requirement from the operational workflow not implemented in the package files.
239. TC-GPK-011: The gatekeeper must detect scope creep -- any functionality in the package files not implied by the operational workflow.

### Evidence Requirement

240. TC-GPK-012: The gatekeeper verdict must include a file-by-file analysis with specific findings per file.
241. TC-GPK-013: The gatekeeper MUST NOT approve a package with MISSING files or CRITICAL design fidelity issues.

### Negative Criteria

242. TC-GPK-N01: The gatekeeper MUST NOT approve based on file count alone without verifying content correctness.
243. TC-GPK-N02: The gatekeeper MUST NOT ignore cross-file consistency issues (e.g., artifact key mismatches between workflow.toml and context_extensions.py).

---

## 14. Criteria for review_package Step (Phase 6)

These criteria verify that the review step performs comprehensive quality assessment of the complete package.

### Spec Fulfillment

244. TC-RP-001: The review must verify that the generated workflow actually implements the composition system specification objective. It must confirm that the workflow can scan components, resolve compositions, and generate self-contained outputs.
245. TC-RP-002: The review must verify that all three layers of the composition architecture are addressed: Layer 1 (component schema with types, properties, validation), Layer 2 (composition format with bindings, overrides, placeholders), Layer 3 (output format with resolution, self-containment, downstream contracts).

### Component Quality

246. TC-RP-003: The review must verify that components are truly reusable, not single-use. Each component type must be applicable across multiple compositions, not tailored to one specific composition.
247. TC-RP-004: The review must verify that component definitions are well-defined -- clear descriptions, complete property sets, explicit validation rules, realistic examples.
248. TC-RP-005: The review must verify that example components demonstrate realistic usage relevant to the domain, not trivial or degenerate cases.

### Composition Quality

249. TC-RP-006: The review must verify that compositions are clear and resolvable. A human reader must be able to understand which components are assembled and how, by reading the composition definition.
250. TC-RP-007: The review must verify that compositions correctly use the reference pattern (reference by ID, not duplicate content).
251. TC-RP-008: The review must verify that overrides are meaningful and necessary, not gratuitous. Each override should serve a clear customization purpose.

### Output Quality

252. TC-RP-009: The review must verify that outputs are self-contained and complete. A downstream consumer must be able to use the output without accessing any other artifact.
253. TC-RP-010: The review must verify that outputs contain no dangling references, no unresolved raw placeholders, and no contradictions between sections.
254. TC-RP-011: The review must verify that the output format is suitable for downstream extraction -- sections are clearly delineated, fields are consistently named, metadata is complete.

### Data Flow

255. TC-RP-012: The review must verify that information flows correctly through the workflow -- scan results feed the plan, plan feeds the generate step, generate output feeds the review. No information is lost or corrupted between steps.
256. TC-RP-013: The review must verify that artifact contracts preserve state continuity -- each step has access to all information it needs from prior steps.

### No Hallucinations

257. TC-RP-014: The review must verify that the package contains no extra configurations, wrong model references, or unnecessary input requirements not implied by the spec.
258. TC-RP-015: The review must verify that no fabricated API endpoints, non-existent libraries, or imaginary capabilities are referenced in the generated files.
259. TC-RP-016: The review must verify that all examples, component IDs, and composition structures are consistent with the domain specification, not invented from training data.

### Gatekeeper Effectiveness

260. TC-RP-017: The review must assess whether the gatekeeper steps in the workflow would catch real defects. It must evaluate whether gatekeeper criteria are specific enough to reject bad artifacts and approve good ones.
261. TC-RP-018: The review must identify any gaps in gatekeeper coverage -- layers or aspects not validated by any gatekeeper step.

### Comprehensive Verification

262. TC-RP-019: The review must explicitly verify ALL criteria in this TEST_CRITERIA document. It must produce a checklist showing each criterion ID and its pass/fail status for the generated package.
263. TC-RP-020: The review verdict (APPROVED or REJECTED) must be justified with specific evidence per criterion category. An APPROVED verdict must confirm all critical and major criteria pass.

### Negative Criteria

264. TC-RP-N01: The review MUST NOT be a superficial "looks good" assessment. Each category must have specific findings with evidence.
265. TC-RP-N02: The review MUST NOT skip the hallucination check. Generated content must be verified against actual spec content.

---

## 15. Criteria for refine_package Step (Phase 6)

These criteria verify that the refine step can effectively fix all types of issues flagged in review.

### Completeness

266. TC-RFP-001: The refine step must be capable of fixing ALL types of issues flagged in the review report: missing content, incorrect content, structural issues, consistency issues, validation failures.
267. TC-RFP-002: The refine step must address each finding individually. It must produce a fix log listing each finding, the fix applied, and the files modified.
268. TC-RFP-003: The refine step must not introduce new issues while fixing existing ones. The fix log must include verification that each fix does not break other aspects of the package.

### Consistency

269. TC-RFP-004: Refinement must maintain cross-file consistency. If a component schema change is made, the change must propagate to all files that reference the schema (validation actions, prompt templates, README).
270. TC-RFP-005: If a step is added, removed, or modified, the workflow.toml routing, context_extensions.py artifact registrations, and prompt templates must all be updated consistently.
271. TC-RFP-006: The refine step must verify consistency after each fix, not assume that fixing one file automatically updates related files.

### Root Cause

272. TC-RFP-007: The refine step must fix root causes, not symptoms. For example, if a prompt template produces incorrect output because it lacks context injection, the fix must add the missing context injection, not just edit the output.
273. TC-RFP-008: The refine step must not apply cosmetic fixes to structural problems. If the workflow routing is wrong, the fix must correct the routing in workflow.toml, not just add a comment explaining the intended behavior.
274. TC-RFP-009: After refinement, the package must go through the review step again for re-validation. The refine step must not self-certify its fixes.

### Negative Criteria

275. TC-RFP-N01: The refine step MUST NOT skip issues from the review report. Every finding must be addressed (fixed or explicitly justified as not requiring a fix).
276. TC-RFP-N02: The refine step MUST NOT make changes outside the scope of the review findings. Refinement is corrective, not additive.

---

## 16. Criteria for promote Step (Phase 7)

These criteria verify that the promote step correctly copies the validated workflow package to its target location.

### Promotion Completeness

277. TC-PR-001: The promote step must copy all validated package files (workflow.toml, context_extensions.py, actions.py if present, prompts/*.txt, README.md, .env.sample if present, config.json.sample if present) to the target workflows/ directory.
278. TC-PR-002: The promote step must verify that all files were successfully copied to the target location. A missing file at the target after promotion must be flagged as an error.
279. TC-PR-003: The promote step must produce a promotion report listing all files promoted, their source paths, and their target paths.

### Configuration Correctness

280. TC-PR-004: The promote step must use the configured target locations from the workflow's configuration. It must not use hardcoded paths.

### Negative Criteria

281. TC-PR-N01: The promote step MUST NOT promote files that did not pass validation (validate_package_deterministic and gatekeep_package). Only validated packages may be promoted.
282. TC-PR-N02: The promote step MUST NOT overwrite existing files at the target location without explicit configuration to do so.

---

## 17. Prompt Quality Criteria (for Prompt-Driven Steps)

These criteria apply to every prompt template in the generated package's prompts/ directory.

### Output Mechanism

283. TC-PQ-001: Each prompt must explicitly instruct the LLM to use file-writing tools (e.g., write_file, create_file) to create actual files on disk at the specified {ARTIFACT_KEY} path.
284. TC-PQ-002: The prompt must specify the exact output file path using {ARTIFACT_KEY} placeholder syntax. The LLM must know WHERE to write, not just WHAT to write.
285. TC-PQ-003: The prompt must instruct the LLM to write the meta.json sidecar after completing the output file, including the required fields (status, remark, artifacts).

### Ambiguity Check

286. TC-PQ-004: The prompt must not contain phrases that could be misinterpreted. Instructions must be explicit: "Write a YAML file defining the component schema to {COMPONENT_SCHEMA_FILE}" rather than "generate a component schema."
287. TC-PQ-005: The prompt must define all domain-specific terms used, or reference a glossary. The LLM must not need to guess what "composition", "binding", or "resolution" means in this context.
288. TC-PQ-006: The prompt must not use vague qualifiers like "as needed", "if appropriate", "when necessary" without defining the specific conditions that trigger the action.

### Common LLM Mistakes

289. TC-PQ-007: The prompt must guard against the LLM outputting content to stdout instead of writing files. It must include: "Do NOT print the content as your response. Write it to the file using file-writing tools."
290. TC-PQ-008: The prompt must guard against the LLM inventing content not supported by the input artifacts. It must include: "Only use information from the referenced input artifacts and the specification. Do not invent component types, composition rules, or output sections not present in the inputs."
291. TC-PQ-009: The prompt must guard against the LLM producing partial output. It must include: "The output file must be complete. Do not use '...' or 'TODO' or 'remaining sections as above' as substitutes for actual content."
292. TC-PQ-010: The prompt must guard against the LLM ignoring YAML frontmatter requirements. It must include: "The output file MUST begin with YAML frontmatter delimited by --- markers, containing all required fields."
293. TC-PQ-011: The prompt must guard against ASCII violations. It must include: "Use ASCII characters only. Do not use em-dashes, curly quotes, or Unicode symbols."

### Completeness

294. TC-PQ-012: Each prompt must specify all required output sections and their expected content. The LLM must know exactly what sections the output file must contain.
295. TC-PQ-013: Each prompt must specify the required format (YAML frontmatter fields, markdown structure, section headings).
296. TC-PQ-014: Each prompt must specify the required file naming convention and output path.
297. TC-PQ-015: Each prompt must list all input artifacts that are injected as context, so the LLM knows what information is available.

### Self-Validation

298. TC-PQ-016: Each prompt must include a self-critic section that instructs the LLM to verify its own output before completing. The self-critic must list specific checks: "Verify that all required sections are present. Verify that all {ARTIFACT_KEY} references are resolved. Verify that the YAML frontmatter contains all required fields."
299. TC-PQ-017: The self-critic must instruct the LLM to re-read its own output file after writing and confirm it matches the requirements.
300. TC-PQ-018: The self-critic must instruct the LLM to check for common errors: missing sections, incomplete content, formatting violations, placeholder residues.

### Negative Criteria

301. TC-PQ-N01: Prompt templates MUST NOT be generic "do a good job" instructions. Each must be specific to its step's domain requirements.
302. TC-PQ-N02: Prompt templates MUST NOT omit file-writing instructions. A prompt that produces content without instructing file creation is a critical defect.
303. TC-PQ-N03: Prompt templates MUST NOT reference artifact keys that are not registered in context_extensions.py.

---

## Appendix A: Criteria Summary

| Section | Criteria Count | Positive | Negative |
|---|---|---|---|
| 2. review_test_criteria / refine_test_criteria | 16 | 12 | 4 |
| 3. generate_component_schema | 25 | 22 | 3 |
| 4. gatekeep_component_schema | 16 | 14 | 2 |
| 5. generate_composition_format | 22 | 19 | 3 |
| 6. gatekeep_composition_format | 18 | 16 | 2 |
| 7. generate_output_format | 24 | 21 | 3 |
| 8. gatekeep_output_format | 19 | 17 | 2 |
| 9. generate_operational_workflow | 26 | 23 | 3 |
| 10. gatekeep_operational_workflow | 19 | 17 | 2 |
| 11. generate_package | 28 | 25 | 3 |
| 12. validate_package_deterministic | 15 | 13 | 2 |
| 13. gatekeep_package | 15 | 13 | 2 |
| 14. review_package | 22 | 20 | 2 |
| 15. refine_package | 11 | 9 | 2 |
| 16. promote | 6 | 4 | 2 |
| 17. prompt_quality | 21 | 18 | 3 |
| **TOTAL** | **303** | **263** | **40** |

---

## Appendix B: Traceability Matrix

| Criterion Prefix | Source Specification | Spec Section |
|---|---|---|
| TC-RTC | META_WORKFLOW_BUILDER_ARCHITECTURE.md | Section 2 (Universal Meta-Workflow Skeleton), Section 3.4 (Review Step Interface) |
| TC-RFTC | META_WORKFLOW_BUILDER_ARCHITECTURE.md | Section 2 (Universal Meta-Workflow Skeleton), Section 3.5 (Refine Step Interface) |
| TC-CS | COMPOSITION_SYSTEM_STANDARD.md Section 3, video_campaign_manuscript_v2.md Section 2 | Universal Component Schema, Domain Component Types |
| TC-GCS | COMPOSITION_SYSTEM_STANDARD.md Section 3.4, video_campaign_manuscript_v2.md Section 2.5 | Validation Rules, Domain Validation Rules |
| TC-CF | COMPOSITION_SYSTEM_STANDARD.md Section 4, video_campaign_manuscript_v2.md Section 3 | Composition Format Standard, Domain Composition Format |
| TC-GCF | COMPOSITION_SYSTEM_STANDARD.md Section 4.3, video_campaign_manuscript_v2.md Section 3 | Composition Validation, Domain Binding Rules |
| TC-OF | COMPOSITION_SYSTEM_STANDARD.md Section 5, video_campaign_manuscript_v2.md Section 4 | Output Format Standard, Domain Output Format |
| TC-GOF | COMPOSITION_SYSTEM_STANDARD.md Section 5.3, video_campaign_manuscript_v2.md Section 4.3 | Output Quality, Domain Quality Requirements |
| TC-OW | COMPOSITION_SYSTEM_STANDARD.md Section 6, video_campaign_manuscript_v2.md Section 5 | Universal Workflow Pattern, Domain Operational Requirements |
| TC-GOW | META_WORKFLOW_BUILDER_ARCHITECTURE.md Section 2 | Universal Meta-Workflow Skeleton |
| TC-GP | workflow_builder_v2 workflow.toml, META_WORKFLOW_BUILDER_ARCHITECTURE.md Section 3.2 | Phase 6 Package Assembly, Generation Step Interface |
| TC-VPD | workflow_builder_v2 workflow.toml | validate_package_deterministic action step |
| TC-GPK | META_WORKFLOW_BUILDER_ARCHITECTURE.md Section 3.3 | Gatekeeper Step Interface |
| TC-RP | COMPOSITION_SYSTEM_STANDARD.md Sections 3-5, video_campaign_manuscript_v2.md Sections 2-4 | Three-Layer Architecture Quality |
| TC-RFP | META_WORKFLOW_BUILDER_ARCHITECTURE.md Section 3.5 | Refine Step Interface |
| TC-PR | workflow_builder_v2 workflow.toml | promote action step |
| TC-PQ | META_WORKFLOW_BUILDER_ARCHITECTURE.md Section 3.2, Section 2.2 | Generation Step Interface, Self-Criticism |

---

## Appendix C: Layer Coverage Verification

| Composition Layer | Generation Step | Gatekeeper Step | Criteria Coverage |
|---|---|---|---|
| Phase 1: TDD Loop | review_test_criteria (Section 2) | refine_test_criteria (Section 2) | TC-RTC-001 through TC-RFTC-N02 |
| Layer 1: Component Library | generate_component_schema (Section 3) | gatekeep_component_schema (Section 4) | TC-CS-001 through TC-CS-N03, TC-GCS-001 through TC-GCS-N02 |
| Layer 2: Composition Definitions | generate_composition_format (Section 5) | gatekeep_composition_format (Section 6) | TC-CF-001 through TC-CF-N03, TC-GCF-001 through TC-GCF-N02 |
| Layer 3: Resolved Outputs | generate_output_format (Section 7) | gatekeep_output_format (Section 8) | TC-OF-001 through TC-OF-N03, TC-GOF-001 through TC-GOF-N02 |
| Workflow Design | generate_operational_workflow (Section 9) | gatekeep_operational_workflow (Section 10) | TC-OW-001 through TC-OW-N03, TC-GOW-001 through TC-GOW-N02 |
| Package Assembly | generate_package (Section 11) | validate_package_deterministic (Section 12), gatekeep_package (Section 13) | TC-GP-001 through TC-GP-N03, TC-VPD-001 through TC-VPD-N02, TC-GPK-001 through TC-GPK-N02 |
| Quality Review | review_package (Section 14) | -- | TC-RP-001 through TC-RP-N02 |
| Issue Resolution | refine_package (Section 15) | -- | TC-RFP-001 through TC-RFP-N02 |
| Promotion | promote (Section 16) | -- | TC-PR-001 through TC-PR-N02 |
| Prompt Templates | prompt_quality (Section 17) | -- | TC-PQ-001 through TC-PQ-N03 |

---

**End of Test Criteria Document**
