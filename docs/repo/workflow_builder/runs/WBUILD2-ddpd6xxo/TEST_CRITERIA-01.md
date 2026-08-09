---
doc_type: "test_criteria"
lifecycle_status: "draft"
effective_version: "WBUILD2-ddpd6xxo"
domain: "composition_system"
criteria_count: 14_sections
layer_coverage: "layer1,layer2,layer3"
---

# Test Criteria for Composition System Workflow

## 1. Spec Objective Summary

The composition system workflow must implement a three-layer architecture that transforms reusable, standardized building blocks (components) through declarative assembly instructions (compositions) into complete, self-contained deliverables (resolved outputs). The end-to-end transformation is: component library plus composition definitions plus external data sources produce fully resolved output documents where every component reference is expanded, every override is applied, and every placeholder is filled or explicitly flagged.

The domain context is domain-agnostic composition: the system defines a universal component schema (Layer 1), a declarative composition format that references components by ID without duplicating content (Layer 2), and a resolved output format that is self-contained and ready for downstream consumption (Layer 3). The generated workflow must support the scan-plan-generate-review-refine pipeline pattern from the Composition System Standard, with gatekeeper validation at each layer boundary.

The ultimate success condition is: a user provides a component library and composition definitions, the workflow scans and validates components, resolves compositions against the library, fills placeholders from data sources, and produces outputs that downstream workflows can consume without needing to reference the original component library or composition files.

---

## 2. Criteria for generate_component_schema step (Phase 2)

These criteria define what the component schema document must contain to pass acceptance. The component schema is Layer 1 of the three-layer architecture.

### Type Completeness

2.1 TC-COMP-001: The schema defines a component type for every distinct building block implied by the workflow spec. Each type must map to a spec requirement, not to an invented category. Verification: enumerate all types in the schema, cross-reference each against the spec.

2.2 TC-COMP-002: The schema defines at least two component types. A single-type system does not benefit from composition.

2.3 TC-COMP-003: Each component type represents a distinct concern. Two types must not be semantically equivalent (e.g., "content_block" and "text_section" covering the same concept). Verification: for each pair of types, verify they have meaningfully different type-specific properties or serve different roles in the output.

### Common Properties

2.4 TC-COMP-004: The schema defines a "Common Properties" section listing all properties shared by every component regardless of type. At minimum: component_id (string, required), component_type (enum, required), name (string, required), version (string, required), description (string, required).

2.5 TC-COMP-005: Each common property has: name, type, required/optional indicator, and description. No common property is left without a type declaration.

2.6 TC-COMP-006: The common property list includes optional properties for extensibility: duration_range (optional), platforms (optional, array), tags (optional, array). These must not be marked required.

### Type-Specific Properties

2.7 TC-COMP-007: For each component type, the schema defines a "Type-Specific Properties" subsection listing properties unique to that type. Each property has: name, type (string/enum/number/boolean/array/object), required/optional, description, and example value.

2.8 TC-COMP-008: No type-specific property uses vague type declarations. Properties declared as "object" without sub-field definitions, or "any", or "varies" are defects. Every property must have a concrete type.

2.9 TC-COMP-009: Enum-type properties list their allowed values explicitly. For example, a hook_style property must enumerate its valid values (e.g., dramatic_reveal, question_hook, statistic_hook), not just say "enum".

2.10 TC-COMP-010: Type-specific property names use lowercase_with_underscores naming convention consistently across all types.

### Validation Rules

2.11 TC-COMP-011: The schema includes a "Validation Rules" section with rules applicable to all components: required fields present (component_id, component_type, name, version, description), valid component_type (must be in defined type list), unique component_id (no duplicates), type-specific schema conformance (all required properties for the declared type present), and semantic version format (MAJOR.MINOR.PATCH).

2.12 TC-COMP-012: Each component type has type-specific validation rules beyond the global rules. These rules must be concrete enough that a gatekeeper can pass/fail a component unambiguously. For example: "hook_style must be one of the defined enum values", "scene_script must not be empty", "duration_target must be a positive number".

2.13 TC-COMP-013: Validation rules distinguish between errors (block the workflow) and warnings (flagged but do not block). The schema states this distinction explicitly.

### Extensibility Model

2.14 TC-COMP-014: The schema includes an "Extensibility Model" section that describes how to add new component types without breaking existing compositions. The section must state that: (a) new types are added by defining their specific properties and documenting them, (b) existing compositions continue to work because they reference by component_id not type, (c) common properties remain stable.

2.15 TC-COMP-015: The extensibility model defines versioning rules: MAJOR version for breaking changes to type-specific schema, MINOR version for adding optional properties, PATCH version for documentation-only changes.

### Examples

2.16 TC-COMP-016: The schema includes at least one example component per type. Each example is formatted as YAML frontmatter (matching the component file format) with all required common properties and all required type-specific properties populated with realistic values.

2.17 TC-COMP-017: Example components use valid component_id values that follow a consistent naming pattern (e.g., "hook-dramatic-reveal-001", "scene-problem-001").

2.18 TC-COMP-018: Example component values are not placeholder text (e.g., "TBD", "TODO", "fill_in_later"). Every example must contain a concrete, realistic value.

### Component File Format

2.19 TC-COMP-019: The schema includes a "Component File Format" section showing the markdown-with-YAML-frontmatter format. The section includes at least one complete example component file.

### Self-Validation

2.20 TC-COMP-020: The schema includes a self-check statement or section that enumerates all component types defined and asserts completeness against the spec. A reviewer can verify the self-check by comparing the listed types against the spec's implied types.

### Negative Criteria

2.21 TC-COMP-N01: MUST NOT include component types that have no basis in the workflow spec. Every type must trace to a spec requirement.

2.22 TC-COMP-N02: MUST NOT define properties without type declarations. Every property must have an explicit type.

2.23 TC-COMP-N03: MUST NOT use non-ASCII characters anywhere in the schema document.

2.24 TC-COMP-N04: MUST NOT define duplicate component_ids in the example components.

2.25 TC-COMP-N05: MUST NOT omit the common properties section. Common properties are mandatory per the Composition System Standard.

---

## 3. Criteria for gatekeep_component_schema step (Phase 2)

These criteria define what the gatekeeper report must demonstrate to verify the component schema passed quality control.

### Type Completeness Verification

3.1 TC-GATE-COMP-001: The gatekeeper report includes a "Type Completeness" validation result with specific evidence. The evidence must list each component type from the schema and state whether it traces to a spec requirement. If any spec-implied type is missing, the gatekeeper must identify it.

3.2 TC-GATE-COMP-002: The gatekeeper report explicitly compares the set of schema-defined types against the set of types implied by the workflow spec. The comparison is not a generic "looks complete" statement.

### Schema Conformance Verification

3.3 TC-GATE-COMP-003: The gatekeeper report includes a "Schema Conformance" validation result. For each component type, the gatekeeper verifies that the common properties (component_id, component_type, name, version, description) are defined.

3.4 TC-GATE-COMP-004: The gatekeeper verifies that type-specific properties for each type have: name, type, required/optional, description, and example value. Missing elements are flagged as failures.

### Validation Rules Verification

3.5 TC-GATE-COMP-005: The gatekeeper report includes a "Validation Rules" validation result. The gatekeeper verifies that validation rules are present, enforceable, and cover: required fields, valid type, unique ID, type-specific conformance, and semantic version format.

3.6 TC-GATE-COMP-006: The gatekeeper verifies that each validation rule has a clear pass/fail condition. Rules stated as "should be reasonable" or "must make sense" are flagged as unenforceable.

### Uniqueness Verification

3.7 TC-GATE-COMP-007: The gatekeeper verifies that all component_ids used in example components are unique within the library. If duplicates exist, the gatekeeper identifies them.

### Evidence and Verdict

3.8 TC-GATE-COMP-008: The gatekeeper report includes a verdict of APPROVED or REJECTED. The verdict is on its own line at the end of the report.

3.9 TC-GATE-COMP-009: Each validation result in the gatekeeper report includes specific evidence quoted from the schema document, not paraphrased summaries. Evidence must reference specific sections, property names, or example values.

3.10 TC-GATE-COMP-010: If the verdict is REJECTED, the gatekeeper report includes a numbered list of specific issues, each with: the type or property affected, what is wrong, and what the fix should be.

### Negative Criteria

3.11 TC-GATE-COMP-N01: MUST NOT approve a schema with known missing types. If the gatekeeper identifies a missing type, it must REJECT.

3.12 TC-GATE-COMP-N02: MUST NOT approve a schema with vague validation rules that cannot be enforced. Rules must have clear pass/fail conditions.

3.13 TC-GATE-COMP-N03: MUST NOT produce a verdict without evidence. Every validation question must have an evidence column filled.

---

## 4. Criteria for generate_composition_format step (Phase 3)

These criteria define what the composition format document must contain to pass acceptance. The composition format is Layer 2 of the three-layer architecture.

### Composition Structure

4.1 TC-CFMT-001: The format defines a YAML structure for compositions with these fields: composition_id (string, required), name (string, required), target_metadata (object, domain-specific), component_bindings (dict, required). Each field has: name, type, required/optional, and description.

4.2 TC-CFMT-002: The format includes at least one complete example composition file in YAML format. The example demonstrates all structural elements (composition_id, name, target_metadata, component_bindings).

### Reference Pattern

4.3 TC-CFMT-003: The format explicitly states that components are referenced by component_id, not copied into compositions. The reference pattern shows how a binding maps a binding_name to a component_id.

4.4 TC-CFMT-004: The format states that the workflow resolves references against the component library at generation time. Compositions do not contain component content -- they contain references.

### Override Mechanism

4.5 TC-CFMT-005: The format defines an override mechanism where compositions can customize component properties without modifying the component itself. Overrides are expressed as a sub-dict within a binding.

4.6 TC-CFMT-006: Override rules state that overrides must conform to the component type's schema (no introducing properties not defined in the type). Overrides are merged with base properties, with override winning on conflict.

4.7 TC-CFMT-007: The format includes an example showing overrides in action: a binding that references a component and overrides specific properties with realistic values.

### Placeholder Resolution

4.8 TC-CFMT-008: The format defines how {placeholder} values in overrides are resolved from external data sources. The data sources for this domain are identified by name (e.g., "Product Master", "configuration files", "user input").

4.9 TC-CFMT-009: The format defines the handling of unresolved placeholders: they are flagged in the output as {UNRESOLVED: field_name}. The format states this explicitly.

4.10 TC-CFMT-010: The format includes an example showing placeholder resolution: a binding with a {placeholder} in an override value, with a comment indicating which data source provides the value.

### Ordering Rules

4.11 TC-CFMT-011: The format distinguishes between singleton bindings (one component per binding, e.g., voice_style) and ordered list bindings (multiple components in sequence, e.g., scenes). The distinction is documented with domain-specific reasoning for each binding type.

4.12 TC-CFMT-012: The format includes examples of both singleton and ordered list bindings, showing the YAML syntax for each.

### Optional Bindings

4.13 TC-CFMT-013: The format defines which bindings are required and which are optional. Required bindings must be present in every composition. Optional bindings can be omitted.

### Composition Validation

4.14 TC-CFMT-014: The format includes a "Composition Validation" section with rules: all referenced component_ids must exist in the component library, overrides must conform to component type schema, required bindings must be present, placeholders must be resolvable from declared data sources, ordering constraints must be satisfied.

### Examples

4.15 TC-CFMT-015: The format includes at least two complete example compositions. The examples demonstrate: different binding types (singleton vs ordered list), overrides with property customization, placeholder usage with data source references.

### Self-Validation

4.16 TC-CFMT-016: The format includes a self-check that all composition rules from the Composition System Standard (Section 4) are covered: references-not-duplicates, override mechanism, placeholder resolution, optional bindings, ordering.

### Negative Criteria

4.17 TC-CFMT-N01: MUST NOT duplicate component content inside compositions. Compositions contain references (component_id), not the component's properties.

4.18 TC-CFMT-N02: MUST NOT omit the override mechanism. Every composition format must support per-composition customization.

4.19 TC-CFMT-N03: MUST NOT omit placeholder resolution. The format must define how placeholders are resolved and what happens when they cannot be resolved.

4.20 TC-CFMT-N04: MUST NOT use non-ASCII characters anywhere in the format document.

4.21 TC-CFMT-N05: MUST NOT define override properties that do not exist in the component schema's type-specific properties. Overrides must reference real properties.

---

## 5. Criteria for gatekeep_composition_format step (Phase 3)

These criteria define what the gatekeeper report must demonstrate to verify the composition format passed quality control.

### Reference Integrity

5.1 TC-GATE-CFMT-001: The gatekeeper report includes a "Reference Pattern" validation result verifying that compositions reference components by component_id, not by copying content. The evidence must show that example compositions use component_id fields.

5.2 TC-GATE-CFMT-002: The gatekeeper verifies that all component_ids referenced in example compositions correspond to component types defined in the component schema. If an example references a type not in the schema, it is flagged.

### Override Conformance

5.3 TC-GATE-CFMT-003: The gatekeeper report includes an "Override Mechanism" validation result verifying that the override rules state overrides must conform to the component type's schema. The gatekeeper checks that override examples in the format use property names from the component schema.

5.4 TC-GATE-CFMT-004: The gatekeeper verifies that the merge rules are stated: override wins on conflict, base properties fill in the rest.

### Placeholder Resolvability

5.5 TC-GATE-CFMT-005: The gatekeeper report includes a "Placeholder Resolution" validation result verifying that data sources are identified for each placeholder used in examples. The gatekeeper checks that the {UNRESOLVED: field_name} handling is defined.

### Required Bindings

5.6 TC-GATE-CFMT-006: The gatekeeper report includes a "Required Bindings" validation result verifying that the format defines which bindings are required vs optional. The gatekeeper checks that required bindings are reasonable for the domain (not requiring all types in every composition).

### Ordering Constraints

5.7 TC-GATE-CFMT-007: The gatekeeper report includes an "Ordering Rules" validation result verifying that singleton vs ordered list bindings are defined with domain-specific reasoning.

### Evidence and Verdict

5.8 TC-GATE-CFMT-008: The gatekeeper report includes a verdict of APPROVED or REJECTED on its own line. Each validation result has specific evidence from the document.

5.9 TC-GATE-CFMT-009: If the verdict is REJECTED, each issue has: the specific element affected, what is wrong, and what the fix should be.

### Negative Criteria

5.10 TC-GATE-CFMT-N01: MUST NOT approve a format where override examples reference properties not defined in the component schema.

5.11 TC-GATE-CFMT-N02: MUST NOT approve a format without identified data sources for placeholder resolution.

---

## 6. Criteria for generate_output_format step (Phase 4)

These criteria define what the output format document must contain to pass acceptance. The output format is Layer 3 of the three-layer architecture.

### Output Structure

6.1 TC-OFMT-001: The format defines the output structure as markdown with YAML frontmatter. The frontmatter includes: composition_id (string), composition_name (string), metadata (object, domain-specific), component_count (integer), generation_date (string), lifecycle_status (string). Each field has: name, type, required/optional, description.

6.2 TC-OFMT-002: The format defines required sections in the output body. Each section has: name, purpose, content description. The section list is domain-appropriate (matches what the spec describes as the final deliverable structure).

6.3 TC-OFMT-003: The format includes at least one complete example output file showing: frontmatter, all required sections populated with resolved content.

### Resolution Rules

6.4 TC-OFMT-004: The format defines resolution rules for expanding component references: every component_id in a composition binding is replaced with the full component content (common properties + type-specific properties + overrides applied).

6.5 TC-OFMT-005: The format defines how overrides are applied during resolution: override values replace base component values, with override winning on conflict. The merged result is what appears in the output.

6.6 TC-OFMT-006: The format defines how placeholders are resolved: {placeholder} values are replaced with values from external data sources. Unresolved placeholders are replaced with {UNRESOLVED: field_name}.

6.7 TC-OFMT-007: The format includes an example showing the resolution process: a composition binding with overrides and placeholders, and the corresponding resolved output section showing the expanded result.

### Self-Contained Output

6.8 TC-OFMT-008: The format states that the output is self-contained: it contains all information needed to understand and use the deliverable. No need to reference the component library or composition file after the output is generated.

6.9 TC-OFMT-009: The format states that the output is downstream-agnostic: it describes WHAT the deliverable is, not HOW to produce it. Downstream workflows extract their specific concerns from the output.

### Quality Requirements

6.10 TC-OFMT-010: The format defines quality requirements for outputs: no dangling references (all component_ids resolved), no unresolved placeholders (all filled or explicitly flagged with {UNRESOLVED: field_name}), schema conformance (overrides applied correctly), completeness (all required sections present), consistency (no contradictions between sections).

### Downstream Extraction Contracts

6.11 TC-OFMT-011: The format defines downstream extraction contracts for at least two downstream workflows. Each contract specifies: which downstream workflow, what it extracts from the output, which sections/fields it reads, and what it produces.

6.12 TC-OFMT-012: Downstream extraction contracts reference sections that actually exist in the output structure. No contract references a section that is not defined in the required sections list.

### Self-Validation

6.13 TC-OFMT-013: The format includes a self-check that all required sections are covered, resolution rules are complete, and downstream contracts are defined.

### Negative Criteria

6.14 TC-OFMT-N01: MUST NOT produce outputs that require the reader to reference the component library or composition file. The output must be self-contained.

6.15 TC-OFMT-N02: MUST NOT leave placeholders unresolved without flagging them. Every unresolved placeholder must appear as {UNRESOLVED: field_name}.

6.16 TC-OFMT-N03: MUST NOT define downstream extraction contracts that reference sections not present in the output structure.

6.17 TC-OFMT-N04: MUST NOT use non-ASCII characters anywhere in the format document.

---

## 7. Criteria for gatekeep_output_format step (Phase 4)

These criteria define what the gatekeeper report must demonstrate to verify the output format passed quality control.

### Reference Expansion

7.1 TC-GATE-OFMT-001: The gatekeeper report includes a "Resolution Rules" validation result verifying that the format defines how component references are expanded. The evidence must show that the expansion process is unambiguous: component_id -> full component content with overrides applied.

### Placeholder Completeness

7.2 TC-GATE-OFMT-002: The gatekeeper report includes a "Placeholder Handling" validation result verifying that the format defines both resolution (from data sources) and fallback ({UNRESOLVED: field_name}). The gatekeeper checks that the example output demonstrates both cases.

### Section Completeness

7.3 TC-GATE-OFMT-003: The gatekeeper report includes a "Section Completeness" validation result verifying that all required sections are defined with name, purpose, and content description. The gatekeeper checks that the example output includes all required sections.

### Consistency

7.4 TC-GATE-OFMT-004: The gatekeeper report includes a "Consistency" validation result verifying that no contradictions exist between sections in the example output. For example, the Voice Direction section must not conflict with the Scene-by-Scene Breakdown section.

### Downstream Feasibility

7.5 TC-GATE-OFMT-005: The gatekeeper report includes a "Downstream Feasibility" validation result verifying that downstream extraction contracts reference actual sections in the output. The gatekeeper cross-references contract field names against the output structure.

7.6 TC-GATE-OFMT-006: The gatekeeper verifies that the output format enables at least two distinct downstream workflows to extract their concerns independently.

### Evidence and Verdict

7.7 TC-GATE-OFMT-007: The gatekeeper report includes a verdict of APPROVED or REJECTED on its own line. Each validation result has specific evidence.

7.8 TC-GATE-OFMT-008: If the verdict is REJECTED, each issue has: the specific element, what is wrong, and what the fix should be.

### Negative Criteria

7.9 TC-GATE-OFMT-N01: MUST NOT approve an output format where the example output has dangling component_id references (unresolved component references).

7.10 TC-GATE-OFMT-N02: MUST NOT approve an output format where downstream contracts reference sections not in the output structure.

---

## 8. Criteria for generate_operational_workflow step (Phase 5)

These criteria define what the operational workflow design document must contain to pass acceptance.

### Workflow Phases

8.1 TC-OW-001: The design defines all five workflow phases: (1) Scan phase -- discover and validate all components in the library, build component inventory with type classification and validation status; (2) Plan phase -- read compositions, resolve component references against the inventory, identify overrides and placeholder bindings, produce a resolution plan; (3) Generate phase -- for each composition, resolve all components and placeholders, apply overrides, assemble the complete output; (4) Review phase -- quality review of generated outputs against constraints and quality requirements; (5) Refine phase -- fix issues found in review (conditional).

8.2 TC-OW-002: Each phase has a clear purpose statement and describes what inputs it consumes and what outputs it produces.

### Step Sequence

8.3 TC-OW-003: The design includes a "Step Sequence" section as a table. Each row has: step name (lowercase_with_underscores), step type (prompt or action), purpose, required_inputs (artifact keys), produces (artifact keys), and routing (onsuccess, on_reject_refine if applicable).

8.4 TC-OW-004: The step sequence is logically ordered: scan steps come before plan steps, plan steps come before generate steps, generate steps come before review steps, review steps come before refine steps. No step depends on an artifact produced by a later step.

8.5 TC-OW-005: Every step's required_inputs references an artifact produced by a prior step (or an input artifact from the workflow's declared inputs). No step reads an artifact that no prior step produced.

### Artifact Contracts

8.6 TC-OW-006: The design includes an "Artifact Contract" section with: an input artifacts table (key, description, required/optional) and an output artifacts table (key, description, produced by which step). Every output artifact traces back to its producing step.

8.7 TC-OW-007: Artifact keys use UPPER_SNAKE_CASE naming convention consistently across all steps. No step uses lowercase or mixed-case artifact keys.

### Step Type Classification

8.8 TC-OW-008: Deterministic operations (file scanning, validation, data processing, directory operations) are classified as action-driven steps. LLM-judgment tasks (generation, review, refinement) are classified as prompt-driven steps. The classification is appropriate for each step.

8.9 TC-OW-009: The design provides justification for each step type classification. For example: "scan_components is an action because it reads files from a directory and runs validation rules -- this is deterministic, not requiring LLM judgment."

### Action Specifications

8.10 TC-OW-010: For each action-driven step, the design includes an action specification with: action name, purpose, inputs (context variables and files), outputs (files and data structures), logic (high-level description), and reused_from field ("existing_action_name" or "new").

8.11 TC-OW-011: The design checks existing reusable actions (promote_workflow_package, step_completion, validate_workflow_bundle) before proposing new actions. If an existing action covers the need, it is referenced instead of creating a new one.

### Routing

8.12 TC-OW-012: The design includes a routing diagram (ASCII art) showing the step flow: onsuccess arrows between sequential steps, on_reject_refine arrows from review steps to refine steps and back.

8.13 TC-OW-013: Review/refine loops are properly designed: review step has on_reject_refine pointing to the refine step, refine step has onsuccess pointing back to the review step. max_iterations is set (default 2). exhausted_failure_code is defined for each loop.

### Review/Refine Loop Design

8.14 TC-OW-014: The design includes a "Review/Refine Loop Design" section that lists: which steps have review/refine loops, what triggers refinement (REJECTED verdict), how many iterations allowed (max_iterations), and what happens when loops exhaust (exhausted_failure_code, exhausted_failure_class = HUMAN_RETRY_REQUIRED).

### Package File Inventory

8.15 TC-OW-015: The design includes a "Package File Inventory" section that enumerates EVERY file the generate_package step must create. Each file entry has: file name, relative path under the package root, and purpose (why this file must exist).

8.16 TC-OW-016: The package file inventory includes: core files (workflow.toml, context_extensions.py, README.md), conditional files (actions.py if action steps exist, .env.sample if env vars needed, config.json.sample if runtime config needed), prompt files (one prompts/NN_step_name.txt per prompt-driven step), and any supplementary data files the workflow needs at runtime.

8.17 TC-OW-017: Every supplementary data file mentioned anywhere in the step sequence or artifact contract is listed in the package file inventory. If a scan step reads from a directory at runtime (e.g., "audiences/"), every file in that directory is individually listed.

### Self-Validation

8.18 TC-OW-018: The design includes a self-check that all workflow phases are covered, artifact flow is traceable, and the package file inventory is complete.

### Negative Criteria

8.19 TC-OW-N01: MUST NOT include steps that are not justified by the workflow phases. Every step must map to a phase.

8.20 TC-OW-N02: MUST NOT have dangling artifact references -- no step reads an artifact no prior step produced.

8.21 TC-OW-N03: MUST NOT classify deterministic operations as prompt-driven or LLM-judgment tasks as action-driven.

8.22 TC-OW-N04: MUST NOT omit the package file inventory. Without it, generate_package cannot know what files to create.

8.23 TC-OW-N05: MUST NOT use non-ASCII characters anywhere in the design document.

---

## 9. Criteria for gatekeep_operational_workflow step (Phase 5)

These criteria define what the gatekeeper report must demonstrate to verify the operational workflow design passed quality control.

### Phase Completeness

9.1 TC-GATE-OW-001: The gatekeeper report includes a "Phase Completeness" validation result verifying that all five phases (scan, plan, generate, review, refine) are defined. The evidence must list each phase and the steps that implement it.

### Data Flow

9.2 TC-GATE-OW-002: The gatekeeper report includes a "Data Flow" validation result verifying that artifact flow traces from inputs to outputs. The gatekeeper checks every step's required_inputs against prior steps' produces. No dangling references.

9.3 TC-GATE-OW-003: The gatekeeper verifies that the artifact contract tables (input artifacts and output artifacts) are consistent with the step sequence table. Every key in the artifact contract appears in at least one step.

### Routing Validity

9.4 TC-GATE-OW-004: The gatekeeper report includes a "Routing" validation result verifying that: onsuccess targets reference valid step names, on_reject_refine targets reference valid refine steps, refine steps route back to the correct review step, and terminal routing reaches stepCompletion.

### Type Consistency

9.5 TC-GATE-OW-005: The gatekeeper report includes a "Type Consistency" validation result verifying that step types (prompt vs action) match the nature of the task. Deterministic operations are actions; LLM-judgment tasks are prompts.

### Action Feasibility

9.6 TC-GATE-OW-006: The gatekeeper report includes an "Action Feasibility" validation result verifying that each action specification has complete details (name, purpose, inputs, outputs, logic) and that the described logic is implementable. The gatekeeper checks that existing reusable actions were considered.

### Package File Inventory

9.7 TC-GATE-OW-007: The gatekeeper verifies that the package file inventory lists every file the generate_package step needs to create, including supplementary data files. Any runtime dependency mentioned in the step sequence but not listed in the inventory is flagged as a defect.

### Evidence and Verdict

9.8 TC-GATE-OW-008: The gatekeeper report includes a verdict of APPROVED or REJECTED on its own line. Each validation result has specific evidence.

9.9 TC-GATE-OW-009: If the verdict is REJECTED, each issue has: the specific step or element affected, what is wrong, and what the fix should be.

### Negative Criteria

9.10 TC-GATE-OW-N01: MUST NOT approve a design with dangling artifact references (steps reading artifacts no prior step produced).

9.11 TC-GATE-OW-N02: MUST NOT approve a design missing any of the five workflow phases.

9.12 TC-GATE-OW-N03: MUST NOT approve a design where runtime data files are referenced in the step sequence but not listed in the package file inventory.

---

## 10. Criteria for generate_package step (Phase 6)

These criteria define what the generated workflow package must contain to pass acceptance.

### File Completeness

10.1 TC-PKG-001: The package contains workflow.toml. Every domain step from the operational workflow design appears as a [[step]] block in order. Infrastructure steps (promote, stepCompletion) appear after domain steps.

10.2 TC-PKG-002: The package contains context_extensions.py with a WorkflowExtensions class that inherits correctly, has workflow_name matching the workflow directory name, has register_artifact_keys() returning relative paths with {job_id} and {seq} placeholders, and has build_context_extensions() returning absolute paths.

10.3 TC-PKG-003: The package contains README.md with sections: Overview, Prerequisites, Usage, Step Reference (table matching workflow.toml steps), Artifact Keys (table of all artifact keys with descriptions), and Architecture (how the three-layer architecture is implemented).

10.4 TC-PKG-004: If the operational workflow design declares action-driven steps, the package contains actions.py with @action decorated functions for each action. Infrastructure actions (promote_workflow_package) are referenced by name, not re-implemented.

10.5 TC-PKG-005: The package contains a prompts/ directory with one file per prompt-driven step. Each file is named NN_step_name.txt where NN is the step order number.

10.6 TC-PKG-006: If the operational workflow design specifies supplementary data files (audience definitions, templates, schemas, runtime configuration), those files are present in the package at the paths specified in the package file inventory.

### Design Fidelity

10.7 TC-PKG-007: workflow.toml step names, types (prompt/action), and routing match the operational workflow design exactly. No steps are added, removed, or reordered.

10.8 TC-PKG-008: Artifact bindings in workflow.toml are verbatim from the operational workflow design. For each step, the required_inputs and produces lists in workflow.toml match the design's Step Sequence table exactly. No keys are omitted or added.

10.9 TC-PKG-009: context_extensions.py register_artifact_keys() includes ALL artifact keys from workflow.toml -- both produces and required_inputs from all steps. No key is missing.

### Component Schema Integration

10.10 TC-PKG-010: The component schema from {COMPONENT_SCHEMA_FILE} is embedded or referenced in the workflow. Prompt-driven steps that need the component schema have the appropriate artifact key in their required_inputs.

### Composition Format Integration

10.11 TC-PKG-011: The composition format from {COMPOSITION_FORMAT_FILE} is embedded or referenced in the workflow. Prompt-driven steps that need the composition format have the appropriate artifact key in their required_inputs.

### Output Format Integration

10.12 TC-PKG-012: The output format from {OUTPUT_FORMAT_FILE} is embedded or referenced in the workflow. Prompt-driven steps that need the output format have the appropriate artifact key in their required_inputs.

### Prompt Quality

10.13 TC-PKG-013: Each prompt file has these sections: Objective (what to generate), Reference Inputs (what to read, using {ARTIFACT_KEY} placeholders), and Output Instructions (where to write, format requirements, file naming conventions).

10.14 TC-PKG-014: Each prompt file explicitly instructs the LLM to use file-writing tools to create actual files on disk. The prompt clarifies that the meta.json result field is for status/summary only, not artifact data.

10.15 TC-PKG-015: All artifact key placeholders in prompts use bare {KEY} format, never backtick-wrapped {KEY}. Every referenced key appears in that step's required_inputs (if consumed) or produces (if created) in workflow.toml.

### Action Implementations

10.16 TC-PKG-016: If actions.py exists, every @action function: has the @action("name") decorator with the correct name, returns ActionResult (not None or dict), includes error handling for missing context variables and missing files, uses type hints and docstrings.

10.17 TC-PKG-017: All runtime imports in actions.py are at the top level of the file, not inside TYPE_CHECKING blocks. Early-exit paths return empty artifacts dict (artifacts={}), not placeholder files.

### Self-Validation

10.18 TC-PKG-018: The generate_package step includes a self-check that all files implied by the operational workflow design are generated. The self-check cross-references the package file inventory against the generated file set.

### Negative Criteria

10.19 TC-PKG-N01: MUST NOT omit any file listed in the operational workflow design's package file inventory.

10.20 TC-PKG-N02: MUST NOT add files or steps not in the operational workflow design (scope creep).

10.21 TC-PKG-N03: MUST NOT put runtime imports inside TYPE_CHECKING blocks in actions.py.

10.22 TC-PKG-N04: MUST NOT have self-referential artifact bindings (same key in both required_inputs and produces of the same step).

10.23 TC-PKG-N05: MUST NOT use backtick-wrapped placeholders in prompt files.

10.24 TC-PKG-N06: MUST NOT use hardcoded absolute paths in register_artifact_keys().

10.25 TC-PKG-N07: MUST NOT use non-ASCII characters in any generated file.

10.26 TC-PKG-N08: MUST NOT use "WORKFLOW_PACKAGE" as a single summary artifact key in meta.json. Individual file keys must be used.

---

## 11. Criteria for gatekeep_package step (Phase 6)

These criteria define what the gatekeeper report must demonstrate to verify the generated package passed quality control.

### File Checklist

11.1 TC-GATE-PKG-001: The gatekeeper report includes a "File Completeness" validation result. The gatekeeper verifies that ALL files from the operational workflow design's package file inventory exist in the generated package. The evidence lists each expected file and whether it was found.

11.2 TC-GATE-PKG-002: If the operational workflow design declares action-driven steps, the gatekeeper verifies actions.py exists. If no action steps exist, the gatekeeper verifies actions.py is absent (not a stub).

11.3 TC-GATE-PKG-003: The gatekeeper verifies prompts/ contains exactly one file per prompt-driven step. The count of prompt files matches the count of prompt-driven steps in workflow.toml.

### Design Fidelity

11.4 TC-GATE-PKG-004: The gatekeeper report includes a "Design Fidelity" validation result. The gatekeeper compares workflow.toml steps against the operational workflow design's step sequence. Every step name, type, and routing matches exactly.

11.5 TC-GATE-PKG-005: The gatekeeper verifies that artifact bindings (required_inputs, produces) in workflow.toml are verbatim from the design. For each step, the gatekeeper compares the design's artifact lists against workflow.toml's lists.

11.6 TC-GATE-PKG-006: The gatekeeper detects scope shrink (domain steps dropped from the design) and scope creep (extra steps not in the design). Note: promote and stepCompletion are required infrastructure steps, not scope creep.

### Composition Integrity

11.7 TC-GATE-PKG-007: The gatekeeper report includes a "Composition Integrity" validation result verifying that the component schema, composition format, and output format are consistent with each other. Compositions reference components defined in the schema; outputs resolve compositions correctly.

### Prompt Completeness

11.8 TC-GATE-PKG-008: The gatekeeper verifies each prompt file has: Objective, Reference Inputs, Output Instructions sections. Placeholders use bare {KEY} format. All referenced artifact keys exist in the workflow's artifact contract.

### Action Completeness

11.9 TC-GATE-PKG-009: If actions.py exists, the gatekeeper verifies every action step in workflow.toml has a corresponding @action("name") function. Actions return ActionResult, have error handling, and follow the design specifications.

### Cross-File Consistency

11.10 TC-GATE-PKG-010: The gatekeeper verifies artifact keys are consistent between workflow.toml and context_extensions.py. Step names match prompt file naming convention. README.md matches actual package contents.

### Evidence and Verdict

11.11 TC-GATE-PKG-011: The gatekeeper report includes a verdict of APPROVED or REJECTED on its own line. Each validation result has specific evidence.

11.12 TC-GATE-PKG-012: If the verdict is REJECTED, each issue has: the specific file and location, what is wrong, and what the fix should be.

### Negative Criteria

11.13 TC-GATE-PKG-N01: MUST NOT approve a package with missing files from the inventory.

11.14 TC-GATE-PKG-N02: MUST NOT approve a package with deterministic validation errors (check VALIDATION_REPORT_FILE first).

11.15 TC-GATE-PKG-N03: MUST NOT approve a package where artifact bindings differ between the design and workflow.toml.

---

## 12. Criteria for review_package step (Phase 6)

These criteria define what the review report must demonstrate to verify comprehensive quality review was performed.

### Spec Fulfillment

12.1 TC-REV-001: The review verifies that the generated workflow actually implements the spec objective. For each phase in the spec, the review checks whether the corresponding generated step does what the spec describes. Evidence references specific files and step names.

12.2 TC-REV-002: The review verifies that the three-layer architecture is correctly implemented: component schema defines building blocks, composition format defines assembly, output format defines resolved deliverables.

### Component Quality

12.3 TC-REV-003: The review assesses whether components are truly reusable (not single-use). Components should be applicable across multiple compositions, not designed for one specific composition only.

12.4 TC-REV-004: The review assesses whether component type-specific properties are concrete and actionable, not vague.

### Composition Quality

12.5 TC-REV-005: The review assesses whether compositions reference components by ID (not duplicate content). Compositions should be clear and resolvable.

12.6 TC-REV-006: The review assesses whether the override mechanism and placeholder resolution work correctly in the examples.

### Output Quality

12.7 TC-REV-007: The review assesses whether outputs are self-contained and complete. No dangling references, no unresolved placeholders (except those flagged with {UNRESOLVED: field_name}).

12.8 TC-REV-008: The review assesses whether downstream extraction contracts are feasible -- can downstream workflows actually extract what they need from the output?

### Data Flow

12.9 TC-REV-009: The review traces information flow through the workflow: from component library through scan, through composition resolution, through output generation. No information is lost or orphaned at any layer boundary.

### No Hallucinations

12.10 TC-REV-010: The review verifies no extra configurations, wrong models, unnecessary inputs, or elements not in the spec are present. Every element in the generated package traces to the spec or to required infrastructure.

### Gatekeeper Effectiveness

12.11 TC-REV-011: The review checks whether all gatekeepers ran and approved. If any gatekeeper REJECTED, the review verifies issues were fixed before reaching this review. If gatekeepers missed issues that this review catches, the review notes this as a process failure.

### Test Criteria Verification

12.12 TC-REV-012: The review verifies ALL criteria in this test criteria document pass. Each criterion is checked with pass/fail status and evidence.

### Verdict

12.13 TC-REV-013: The review report ends with a verdict of APPROVED or REJECTED on its own line. If REJECTED, each issue has: the file, location, and specific fix required.

### Negative Criteria

12.14 TC-REV-N01: MUST NOT rubber-stamp the review. The review must contain at least one substantive finding beyond "looks good".

12.15 TC-REV-N02: MUST NOT approve a package with known spec fulfillment failures.

---

## 13. Criteria for refine_package step (Phase 6)

These criteria define what the refine step must accomplish when fixing issues.

### Completeness

13.1 TC-REF-001: The refine step addresses every issue listed in the review document. Each issue is explicitly fixed, not just acknowledged.

13.2 TC-REF-002: The refine step addresses every ERROR-level finding in the deterministic validation report (if it exists).

13.3 TC-REF-003: The refine step can fix ALL types of issues flagged in review: missing files, routing errors, artifact binding mismatches, prompt quality issues, action implementation gaps, README inaccuracies.

### Consistency

13.4 TC-REF-004: When the refine step changes an artifact key in one file, it updates the key in all files that reference it (workflow.toml, context_extensions.py, prompt files). Cross-file consistency is maintained.

13.5 TC-REF-005: When the refine step adds or modifies a step in workflow.toml, it verifies that: the step has a prompt file (if prompt-driven), the step's artifact keys are registered in context_extensions.py, and the step's routing targets reference existing step names.

### Root Cause

13.6 TC-REF-006: The refine step fixes root causes, not symptoms. If the review flags a NameError at runtime, the refine step checks all imports for the TYPE_CHECKING pattern, not just the specific line. If the review flags one artifact binding error, the refine step checks all step bindings.

13.7 TC-REF-007: After fixing, the refine step verifies the fix does not introduce new issues. For example, after changing imports, it verifies all function calls still resolve. After changing bindings, it verifies the full chain is consistent.

### Constraints

13.8 TC-REF-008: The refine step does not change content that was not flagged by the review or validation. It preserves the overall workflow structure, does not add new steps, and does not remove existing steps.

13.9 TC-REF-009: The refine step keeps all content ASCII-only.

### Negative Criteria

13.10 TC-REF-N01: MUST NOT add new workflow steps not justified by review findings.

13.11 TC-REF-N02: MUST NOT remove existing workflow steps.

13.12 TC-REF-N03: MUST NOT change the workflow name or job_prefix.

13.13 TC-REF-N04: MUST NOT introduce non-ASCII characters.

---

## 14. Prompt Quality Criteria (for prompt-driven steps)

These criteria apply to every prompt file generated in the prompts/ directory. They ensure that LLM-driven steps produce correct outputs.

### Output Mechanism

14.1 TC-PROMPT-001: Each prompt explicitly instructs the LLM to use file-writing tools (write_file, edit, or equivalent) to create actual files on disk at the specified artifact path. The prompt does not instruct the LLM to put artifact data in the meta.json result field.

14.2 TC-PROMPT-002: Each prompt clarifies that the meta.json result/remark field is for status and summary only (e.g., "Wrote the component schema successfully"), not for artifact content.

### Ambiguity Check

14.3 TC-PROMPT-003: Each prompt uses unambiguous language. No phrases that could be misinterpreted: "some value", "varies", "as needed", "appropriate", "properly". Every instruction has a concrete, verifiable outcome.

14.4 TC-PROMPT-004: Each prompt specifies exact file names, directory structures, and artifact keys. The LLM does not need to guess where to write files or what to name them.

### Common LLM Mistakes

14.5 TC-PROMPT-005: Each prompt guards against known failure modes:
  - For generation prompts: guards against vague output ("describe in general terms") by requiring specific structure and examples
  - For gatekeeper prompts: guards against rubber-stamping by requiring specific evidence for each validation question
  - For review prompts: guards against superficial review by requiring at least one substantive finding
  - For refine prompts: guards against symptom-fixing by requiring root cause analysis

14.6 TC-PROMPT-006: Prompts for code generation steps (generate_package, refine_package) include Code Quality Rules or reference them, preventing: TYPE_CHECKING runtime imports, self-referential artifact bindings, placeholder files on early exit, missing @action decorators.

### Completeness

14.7 TC-PROMPT-007: Each prompt specifies all required outputs: file names, format (ASCII-only, YAML frontmatter), required sections, and naming conventions.

14.8 TC-PROMPT-008: Each prompt includes a "Forbidden Content" section listing what must NOT appear: non-ASCII characters, vague descriptions, backtick-wrapped placeholders, hardcoded paths, etc.

### Self-Validation

14.9 TC-PROMPT-009: Each generation prompt includes a "Self-Validation" section that the LLM must perform before reporting APPROVED. The self-validation lists specific checks the LLM must perform on its own output.

14.10 TC-PROMPT-010: Each gatekeeper and review prompt includes a "Self-Critic" section that challenges the LLM to verify it is not rubber-stamping. The self-critic asks: "Am I finding at least one substantive issue, or am I just saying 'looks good'?"

### Reference Inputs

14.11 TC-PROMPT-011: Each prompt's Reference Inputs section lists all artifact keys the step needs, using bare {KEY} format. Every listed key must appear in the step's required_inputs in workflow.toml.

14.12 TC-PROMPT-012: Each prompt does NOT reference artifact keys that are not in the step's required_inputs or produces in workflow.toml. A prompt referencing {SOME_KEY} means the runner must provide that path -- if it is not declared, the runner will not provide it.

### Negative Criteria

14.13 TC-PROMPT-N01: MUST NOT instruct the LLM to put artifact content in the meta.json result field.

14.14 TC-PROMPT-N02: MUST NOT use backtick-wrapped placeholders like `{ARTIFACT_KEY}`. All placeholders must be bare {ARTIFACT_KEY}.

14.15 TC-PROMPT-N03: MUST NOT contain non-ASCII characters.

14.16 TC-PROMPT-N04: MUST NOT omit the Output Instructions section. Every prompt must tell the LLM exactly where to write and in what format.

---

## Appendix A: Criteria Index

| Section | Criteria Count | Negative Criteria |
|---------|---------------|-------------------|
| 2. generate_component_schema | 20 positive, 5 negative | TC-COMP-N01 through N05 |
| 3. gatekeep_component_schema | 10 positive, 3 negative | TC-GATE-COMP-N01 through N03 |
| 4. generate_composition_format | 16 positive, 5 negative | TC-CFMT-N01 through N05 |
| 5. gatekeep_composition_format | 9 positive, 2 negative | TC-GATE-CFMT-N01 through N02 |
| 6. generate_output_format | 13 positive, 4 negative | TC-OFMT-N01 through N04 |
| 7. gatekeep_output_format | 8 positive, 2 negative | TC-GATE-OFMT-N01 through N02 |
| 8. generate_operational_workflow | 18 positive, 5 negative | TC-OW-N01 through N05 |
| 9. gatekeep_operational_workflow | 9 positive, 3 negative | TC-GATE-OW-N01 through N03 |
| 10. generate_package | 18 positive, 8 negative | TC-PKG-N01 through N08 |
| 11. gatekeep_package | 12 positive, 3 negative | TC-GATE-PKG-N01 through N03 |
| 12. review_package | 13 positive, 2 negative | TC-REV-N01 through N02 |
| 13. refine_package | 9 positive, 4 negative | TC-REF-N01 through N04 |
| 14. prompt quality | 12 positive, 4 negative | TC-PROMPT-N01 through N04 |

Total: 157 positive criteria, 50 negative criteria = 207 criteria across 13 sections.

---

## Appendix B: Three-Layer Coverage Map

| Layer | Generation Criteria | Gatekeeper Criteria |
|-------|-------------------|-------------------|
| Layer 1 (Component Library) | Section 2 (TC-COMP) | Section 3 (TC-GATE-COMP) |
| Layer 2 (Composition Definitions) | Section 4 (TC-CFMT) | Section 5 (TC-GATE-CFMT) |
| Layer 3 (Resolved Outputs) | Section 6 (TC-OFMT) | Section 7 (TC-GATE-OFMT) |
| Workflow Operation | Section 8 (TC-OW) | Section 9 (TC-GATE-OW) |
| Package Assembly | Section 10 (TC-PKG) | Section 11 (TC-GATE-PKG) |
| Quality Review | Section 12 (TC-REV) | -- |
| Issue Resolution | Section 13 (TC-REF) | -- |
| Prompt Quality | Section 14 (TC-PROMPT) | -- |

---

End of Test Criteria Document
