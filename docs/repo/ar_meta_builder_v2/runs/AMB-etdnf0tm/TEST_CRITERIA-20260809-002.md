---
doc_type: "test_criteria"
lifecycle_status: "draft"
---

# Test Criteria: Target Workflow Acceptance Criteria

## Introduction

This document defines the comprehensive acceptance criteria for the target
workflow produced by the composition system meta-builder pipeline. These
criteria apply to the TARGET workflow described in the runtime specification
(NOT the builder itself).

The target workflow is whatever executable workflow package the meta-builder
generates from a given runtime spec. All criteria below are written in terms
of "target workflow_name", "target standard_name", "target standard_version",
and "target standard_filename" -- these values come from the runtime spec's
YAML frontmatter identity section.

Scope:
- 8 design phases (Phases 1-8), each with phase-specific acceptance criteria
- Cross-phase invariants (meta-test-criteria) that ALL gatekeepers must check
- Negative criteria defining what MUST NOT appear in generated output
- Self-validation criteria ensuring complete coverage

These criteria are accumulated into a single TEST_CRITERIA_FILE and injected
into ALL subsequent gatekeep prompts (Phases 2-8) as the baseline for
pass/fail decisions.

---

## Criteria for Phase 1 (Analyze Spec)

Phase 1 produces the domain_analysis component. The following criteria
verify its correctness:

### Identity Correctness

- TC-P1-001: The domain_analysis artifact contains a target_identity object
  with standard_name, standard_version, and standard_filename fields extracted
  from the runtime spec's YAML frontmatter.
- TC-P1-002: The target_identity.standard_name value matches exactly the
  standard_name declared in the spec frontmatter (character-for-character).
- TC-P1-003: The target_identity.standard_version value matches exactly the
  standard_version declared in the spec frontmatter.
- TC-P1-004: The target_identity.standard_filename value matches exactly the
  standard_filename declared in the spec frontmatter.
- TC-P1-005: The domain_analysis does NOT contain the builder's identity
  values (ar_meta_builder_v2, AMB_STANDARD) as the target identity.

### Output Type Extraction

- TC-P1-006: The domain_analysis contains an output_type field with value
  "documented_versioned" or "direct", matching the spec's declaration.
- TC-P1-007: If the spec declares output_type as "documented_versioned", the
  domain_analysis includes review/approval requirements in the natural phases.
- TC-P1-008: If the spec declares output_type as "direct", the domain_analysis
  does NOT include review/approval gates in the delivery mechanism.

### Meta-Test-Criteria Coverage

- TC-P1-009: The domain_analysis contains a meta_test_criteria array with
  exactly 4 invariant entries.
- TC-P1-010: Meta-test-criterion 1 states that the generated workflow uses
  the spec's identity, not the builder's identity.
- TC-P1-011: Meta-test-criterion 2 states that the generated workflow
  structure matches the spec's domain, not the builder's structure.
- TC-P1-012: Meta-test-criterion 3 states that the output delivery mechanism
  matches the spec's declared output type.
- TC-P1-013: Meta-test-criterion 4 states that all component types are
  derived from base schema fine-tuning, not hardcoded.

### Natural Phase Extraction

- TC-P1-014: The domain_analysis contains a natural_phases array listing
  the target domain's workflow phases as described in the spec.
- TC-P1-015: Each natural phase entry includes a name and purpose description
  traceable to the spec's domain overview section.

### Component Inventory

- TC-P1-016: The domain_analysis contains a component_inventory array
  identifying the domain components described in the spec.
- TC-P1-017: Each component inventory entry includes a type name and
  description that can be traced to the spec's component type definitions.

---

## Criteria for Phase 2 (Component Schema)

Phase 2 produces the component_schema component. The following criteria
verify the fine-tuned schema for the target domain:

### All Component Types Defined

- TC-P2-001: The component_schema defines all component types required by
  the target domain, as identified in Phase 1's component_inventory.
- TC-P2-002: Each component type has a unique name (no duplicate type names).
- TC-P2-003: Each component type declaration includes a purpose description
  explaining its role in the target workflow.

### 7 Common Properties

- TC-P2-004: The component_schema retains all 7 common properties from the
  base schema: component_id, component_type, name, version, description,
  phase_origin, identity_locked.
- TC-P2-005: The component_id property specifies format as
  "{phase}-{type}-{workflow_name}" matching the base schema pattern.
- TC-P2-006: The identity_locked property is defined as boolean type with
  required=true, enforcing identity verification on all artifacts.
- TC-P2-007: The phase_origin property is defined as integer type with
  valid range 1-8.

### Type-Specific Properties

- TC-P2-008: Each component type in the schema includes its type-specific
  properties as defined in the spec's component type definitions.
- TC-P2-009: Required type-specific properties are marked as required=true.
- TC-P2-010: Optional type-specific properties are marked as required=false
  with appropriate default values.

### Validation Rules VR-001 through VR-008

- TC-P2-011: Validation rule VR-001 is defined: all required common fields
  must be present (component_id, component_type, name, version, description,
  phase_origin, identity_locked).
- TC-P2-012: Validation rule VR-002 is defined: component_type must be one
  of the types declared in the component_schema (not hardcoded to the
  builder's 8 types).
- TC-P2-013: Validation rule VR-003 is defined: component_id must be unique
  across all artifacts in the pipeline.
- TC-P2-014: Validation rule VR-004 is defined: all required type-specific
  properties for the declared type must be present.
- TC-P2-015: Validation rule VR-005 is defined: identity_locked must be true
  for all artifacts (identity matches target spec, not builder).
- TC-P2-016: Validation rule VR-006 is defined: phase_origin must match the
  artifact's position in the pipeline.
- TC-P2-017: Validation rule VR-007 is defined: base_schema_version must be
  >= "2.0" for component_schema type artifacts.
- TC-P2-018: Validation rule VR-008 is defined: conflict_check_passed must
  be true for artifact_contract type artifacts.

### Fine-Tuning Decisions

- TC-P2-019: The component_schema includes a fine_tuning_decisions array
  with keep/add/drop/specialize decisions for each base schema element.
- TC-P2-020: Each fine-tuning decision includes a rationale explaining why
  the decision was made for the target domain.

---

## Criteria for Phase 3 (Composition Format)

Phase 3 produces the composition_format component. The following criteria
verify the binding rules for the target domain:

### Binding Rules (One Per Type)

- TC-P3-001: The composition_format defines exactly one binding rule per
  component type declared in the component_schema.
- TC-P3-002: Each binding rule specifies the source phase that produces the
  component and the consuming phases that depend on it.
- TC-P3-003: Each binding rule specifies whether the binding is required
  or optional.
- TC-P3-004: The binding chain forms a valid dependency graph with no cycles.

### Override Mechanism

- TC-P3-005: The composition_format defines an override mechanism for
  injecting spec-specific values into pipeline bindings.
- TC-P3-006: The override mechanism specifies that identity fields ALWAYS
  come from the runtime spec, never derived or substituted.
- TC-P3-007: The override mechanism specifies how base schema path is
  resolved at runtime via context_extensions.
- TC-P3-008: The override mechanism specifies that meta-test-criteria from
  Phase 1 are injected into ALL subsequent gatekeep prompts.

### 7 Placeholders

- TC-P3-009: The composition_format defines all 7 required placeholders:
  {WORKFLOW_SPEC_FILE}, {BASE_COMPOSITION_STANDARD}, {standard_name},
  {standard_version}, {standard_filename}, {output_type}, {workflow_name}.
- TC-P3-010: Each placeholder has a documented data source mapping indicating
  where the value comes from (spec frontmatter, context, or runtime).
- TC-P3-011: All 7 placeholders are marked as required.

### Ordering Rules

- TC-P3-012: The composition_format specifies that phases execute in
  sequential order (Phase 1 through Phase 8).
- TC-P3-013: Each phase's output is available as input to all subsequent
  phases via the binding chain.
- TC-P3-014: The composition_id follows the pattern
  "{prefix}-pipeline-{workflow_name}" using the target workflow_name.

---

## Criteria for Phase 4 (Output Format)

Phase 4 produces the output_format component. The following criteria verify
the target workflow's output structure:

### 3-Part Output Structure

- TC-P4-001: The output_format defines the 3-part output structure:
  (1) workflow manifest and code files, (2) composition standard,
  (3) embedded builder spec for self-bootstrap.
- TC-P4-002: Part 1 includes workflow.toml, context_extensions.py, actions.py,
  prompts/*.txt, and README.md.
- TC-P4-003: Part 2 includes the composition standard at
  Standards/{standard_filename} using the target's standard_filename.
- TC-P4-004: Part 3 includes the embedded builder spec at
  Specs/{builder_name}.md for recursive chain support.

### Resolution Rules RR-001 through RR-005

- TC-P4-005: Resolution rule RR-001 is defined: all phase outputs are
  consolidated into the runtime standard (Phase 7 consolidates Phases 1-6).
- TC-P4-006: Resolution rule RR-002 is defined: all identity fields come
  from the runtime spec, not the builder.
- TC-P4-007: Resolution rule RR-003 is defined: all {placeholders} are
  filled from spec and context at resolution time.
- TC-P4-008: Resolution rule RR-004 is defined: the workflow package is
  fully self-contained and executable without reference to the builder.
- TC-P4-009: Resolution rule RR-005 is defined: the builder's own spec is
  embedded in Specs/ for recursive chain self-bootstrapping.

### Quality Requirements QR-001 through QR-012

- TC-P4-010: Quality requirement QR-001 is defined: identity correctness --
  workflow.toml name matches the spec's workflow_name.
- TC-P4-011: Quality requirement QR-002 is defined: no builder leakage --
  no reference to the builder's workflow_name or standard_name in output.
- TC-P4-012: Quality requirement QR-003 is defined: standard filename
  matches the spec's standard_filename.
- TC-P4-013: Quality requirement QR-004 is defined: all artifact keys are
  unique and conflict-free with the global registry.
- TC-P4-014: Quality requirement QR-005 is defined: all prompt files exist
  for prompt-driven steps.
- TC-P4-015: Quality requirement QR-006 is defined: Python syntax is valid
  in context_extensions.py and actions.py.
- TC-P4-016: Quality requirement QR-007 is defined: TOML parse is valid
  in workflow.toml.
- TC-P4-017: Quality requirement QR-008 is defined: class name in
  context_extensions.py is derived from the target workflow_name.
- TC-P4-018: Quality requirement QR-009 is defined: output delivery mechanism
  matches the spec's output_type declaration.
- TC-P4-019: Quality requirement QR-010 is defined: meta-test-criteria are
  satisfied across all generated artifacts.
- TC-P4-020: Quality requirement QR-011 is defined: self-bootstrap spec is
  present in the Specs/ directory.
- TC-P4-021: Quality requirement QR-012 is defined: Standards/ directory
  contains the composition standard with the correct filename.

---

## Criteria for Phase 5 (Artifact Contract)

Phase 5 produces the artifact_contract component. The following criteria
verify the artifact key definitions:

### Key Uniqueness

- TC-P5-001: All artifact keys defined in the contract are unique (no
  duplicate keys).
- TC-P5-002: Each artifact key follows the naming convention: uppercase
  letters, digits, and underscores only, ending with _FILE suffix.
- TC-P5-003: Each artifact key has a corresponding filename pattern that
  is unique within the target workflow's artifact set.

### Filename Patterns

- TC-P5-004: Each artifact key maps to a filename pattern that includes
  the target workflow_name or a domain-specific prefix.
- TC-P5-005: Filename patterns use {seq} placeholder for sequence numbering
  where multiple iterations are expected.
- TC-P5-006: Filename patterns use forward slashes for directory separators
  (platform-independent).

### No Global Registry Conflicts

- TC-P5-007: The artifact_contract includes a conflict_check_passed field
  set to true, confirming no collisions with the global artifact registry.
- TC-P5-008: The conflict check verifies that no artifact key in the target
  workflow conflicts with keys registered by other workflow packages.
- TC-P5-009: The conflict check verifies that no filename pattern in the
  target workflow overlaps with patterns used by other workflow packages.

---

## Criteria for Phase 6 (Step Sequence)

Phase 6 produces the step_sequence component. The following criteria verify
the target workflow's step design:

### Routing Valid

- TC-P6-001: Every step in the sequence has a valid onsuccess routing to
  the next step (or terminal state for the last step).
- TC-P6-002: Steps with review loops have valid on_reject_refine routing
  to the corresponding refine step.
- TC-P6-003: Refine steps route back to their corresponding review step,
  forming a valid refinement loop.
- TC-P6-004: All routing targets reference steps that exist in the sequence
  (no forward references to undefined steps).

### No Dangling References

- TC-P6-005: Every step referenced in an onsuccess or on_reject_refine
  routing is defined in the step sequence.
- TC-P6-006: Every required_input artifact key referenced by a step is
  either produced by a prior step or declared as a workflow input.
- TC-P6-007: Every produced artifact key is consumed by at least one
  subsequent step or is a declared workflow output.

### Output Delivery Matches Spec Type

- TC-P6-008: If the spec declares output_type as "documented_versioned",
  the step sequence includes review steps, refine steps, approval gates,
  and promotion/archival steps.
- TC-P6-009: If the spec declares output_type as "direct", the step sequence
  does NOT include review/approval gates and delivers output directly.
- TC-P6-010: The delivery_mechanism object in the step_sequence matches the
  output_type declared in the spec (promote/archive for documented_versioned,
  direct copy for direct).

### Step Type Correctness

- TC-P6-011: Each step has a declared type: "prompt" for LLM-driven steps
  or "action" for deterministic Python steps.
- TC-P6-012: Prompt-driven steps reference a prompt file path that exists
  in the prompts/ directory.
- TC-P6-013: Action steps reference an action function name that is
  implemented in actions.py.
- TC-P6-014: Each step declares its role_policy for coder assignment
  (e.g., architect_standard, reviewer_standard).

---

## Criteria for Phase 7 (Runtime Standard)

Phase 7 produces the runtime_standard component. The following criteria
verify the consolidated composition standard:

### All Phases Consolidated

- TC-P7-001: The runtime_standard contains consolidated content from all
  6 design phases (Phases 1-6): domain analysis, component schema,
  composition format, output format, artifact contract, and step sequence.
- TC-P7-002: The consolidated content preserves all validation rules
  (VR-001 through VR-008) from Phase 2.
- TC-P7-003: The consolidated content preserves all resolution rules
  (RR-001 through RR-005) from Phase 4.
- TC-P7-004: The consolidated content preserves all quality requirements
  (QR-001 through QR-012) from Phase 4.
- TC-P7-005: The consolidated content preserves all binding rules and
  placeholder definitions from Phase 3.

### Identity Correct

- TC-P7-006: The runtime_standard's standard_name matches the target
  spec's standard_name (not the builder's standard_name).
- TC-P7-007: The runtime_standard's standard_version matches the target
  spec's standard_version.
- TC-P7-008: The runtime_standard does NOT contain the builder's identity
  values as its own identity.

### Cross-Phase Consistency

- TC-P7-009: The cross_phase_consistency field is true, indicating all
  phases are mutually consistent.
- TC-P7-010: Component types referenced in Phase 3 (composition format)
  match the types defined in Phase 2 (component schema).
- TC-P7-011: Artifact keys referenced in Phase 6 (step sequence) match
  the keys defined in Phase 5 (artifact contract).
- TC-P7-012: Output structure defined in Phase 4 is achievable given the
  step sequence designed in Phase 6.
- TC-P7-013: The meta-test-criteria from Phase 1 are satisfied by the
  consolidated content across all phases.

---

## Criteria for Phase 8 (Operational Workflow)

Phase 8 produces the operational_workflow component. The following criteria
verify the concrete workflow implementation design:

### Steps Reference Standard

- TC-P8-001: Every step in the operational workflow references the runtime
  standard for its design specification.
- TC-P8-002: Step names in the operational workflow match the step names
  defined in the step_sequence (Phase 6).
- TC-P8-003: Step routing (onsuccess, on_reject_refine) in the operational
  workflow matches the routing defined in the step_sequence.

### Prompt Files Exist

- TC-P8-004: The operational_workflow declares one prompt file per
  prompt-driven step.
- TC-P8-005: Each prompt file path follows the pattern prompts/{NN}_{step_name}.txt
  where NN is a zero-padded sequence number.
- TC-P8-006: Each prompt file's required_inputs placeholders match the
  step's declared required_inputs in workflow.toml.

### Action Implementations Present

- TC-P8-007: The operational_workflow declares all action implementations
  needed by action-driven steps.
- TC-P8-008: Each action implementation is a Python function decorated
  with @action("action_name").
- TC-P8-009: Action implementations accept the standard parameter signature:
  context, state, step_cfg, project_root.

### Context Extensions

- TC-P8-010: The operational_workflow defines context_extensions with a
  class name derived from the target workflow_name.
- TC-P8-011: The context_extensions class registers all artifact keys
  defined in the artifact_contract (Phase 5).
- TC-P8-012: The context_extensions class resolves all artifact keys to
  absolute filesystem paths.

---

## Negative Criteria

The following define what MUST NOT appear in the generated target workflow.
These are fail-fast criteria -- any violation causes immediate rejection.

### Builder Identity Leakage

- NC-001: The generated workflow.toml MUST NOT contain "ar_meta_builder_v2"
  as the workflow name.
- NC-002: The generated workflow.toml MUST NOT contain "AMB_STANDARD" as
  the standard name.
- NC-003: The generated context_extensions.py MUST NOT contain class names
  derived from "ar_meta_builder_v2" (e.g., ArMetaBuilderV2Extensions).
- NC-004: The generated prompts/ MUST NOT contain references to the
  builder's identity as if it were the target workflow.
- NC-005: The generated README.md MUST NOT describe the builder -- it must
  describe the target workflow.

### Structural Leakage

- NC-006: The generated workflow MUST NOT copy the builder's 9-phase/22-step
  structure unless the target spec independently requires that structure.
- NC-007: The generated workflow MUST NOT hardcode the builder's 8 component
  types -- component types must be derived from the target spec via
  fine-tuning.
- NC-008: The generated workflow MUST NOT assume output_type -- it must
  check the spec's declaration.

### Content Prohibitions

- NC-009: The generated artifacts MUST NOT contain non-ASCII characters
  (em-dashes, curly quotes, Unicode symbols).
- NC-010: The generated artifacts MUST NOT contain scope invented beyond
  what the target spec defines.
- NC-011: The generated artifacts MUST NOT contain vague criteria like
  "must work properly" or "must be correct" without specific verification
  methods.
- NC-012: The generated workflow MUST NOT contain hardcoded file paths
  from the builder's environment.

---

## Self-Validation

This section verifies that the test criteria document itself is complete
and usable by gatekeepers.

### Coverage of All Spec Sections

- SV-001: Section 1 (Domain Overview) is covered by TC-P1-014 through
  TC-P1-017 (natural phases and component inventory).
- SV-002: Section 2 (Workflow Identity) is covered by TC-P1-001 through
  TC-P1-005 and NC-001 through NC-005.
- SV-003: Section 3 (Output Delivery) is covered by TC-P1-006 through
  TC-P1-008 and TC-P6-008 through TC-P6-009.
- SV-004: Section 4 (Component Schema) is covered by TC-P2-001 through
  TC-P2-020.
- SV-005: Section 5 (Composition Format) is covered by TC-P3-001 through
  TC-P3-014.
- SV-006: Section 6 (Output Format) is covered by TC-P4-001 through
  TC-P4-021.
- SV-007: Section 7 (Operational Requirements) is covered by TC-P6-001
  through TC-P6-014, TC-P7-001 through TC-P7-013, TC-P8-001 through
  TC-P8-012.

### All Criteria Are Verifiable

- SV-008: Every criterion has a specific, observable condition that a
  gatekeeper can check by reading the artifact content.
- SV-009: No criterion uses vague language like "must be correct" or
  "must work properly" -- all criteria specify what "correct" means.
- SV-010: Every criterion is traceable to a specific section or rule in
  the runtime specification.
- SV-011: The 4 meta-test-criteria invariants are explicitly enumerated
  and referenced by phase-specific criteria.
- SV-012: Negative criteria provide concrete string patterns or structural
  checks that can be verified by content search.

### Meta-Test-Criteria Propagation

- SV-013: The test criteria document explicitly states that the 4
  meta-test-criteria must be injected into ALL subsequent gatekeep prompts
  (Phases 2-8).
- SV-014: Each phase's gatekeep criteria include both phase-specific
  criteria AND the cross-phase meta-test-criteria.
- SV-015: The meta-test-criteria are immutable once established in Phase 1
  -- they cannot be modified by subsequent phases.

---

## Summary of Criteria Counts

| Section | Criteria Count |
|---|---|
| Phase 1 (Analyze Spec) | 17 |
| Phase 2 (Component Schema) | 20 |
| Phase 3 (Composition Format) | 14 |
| Phase 4 (Output Format) | 21 |
| Phase 5 (Artifact Contract) | 9 |
| Phase 6 (Step Sequence) | 14 |
| Phase 7 (Runtime Standard) | 13 |
| Phase 8 (Operational Workflow) | 12 |
| Negative Criteria | 12 |
| Self-Validation | 15 |
| **Total** | **147** |

---

**End of Test Criteria Document**
