---
doc_type: "masterplan"
authority: "human-authored"
scan_policy: "exclude"
scan_reason: "design specification for Layer 1 governance; exclude from operational scans"
---

# Layer 1 Governance Specification

## Status

This document defines the target specification for Layer 1 governance.

It is a design document, not an implementation artifact. It exists to
translate the layer architecture master plan into a concrete workflow
design before any new Layer 1 workflow package is created.

## Purpose

The purpose of the Layer 1 workflow is to produce and maintain the
ecosystem governance baseline.

This workflow must not be derived from the legacy Layer 1 package by minor
adjustment. It should be designed from Layer 1 scope first, then
implemented from that design.

## Design Objective

The new Layer 1 workflow must:

- generate only Layer 1 governance artifacts
- reject Layer 2 and Layer 3 operational drift
- separate permanent standards from temporary evidence
- attach explicit metadata to all outputs
- be stable across multiple future Layer 2 cores

## Workflow Identity

### Workflow Bundle Name

`01_governance_foundation_v1`

### Workflow Class

Governance workflow.

### Owning Layer

Layer 1.

### Primary Authority

Ecosystem governance authority.

### Output Authority Model

- permanent governance docs may be `workflow-generated`
- review, validation, and audit outputs are temporary evidence artifacts
- master plan and design spec inputs remain `human-authored`

## Bundle Governance Package

The workflow bundle should include an explicit bundle-governance package.

This package exists to govern how the workflow itself is authored and
maintained, especially:

- prompt structure
- allowed action types
- review and audit behavior
- metadata discipline
- anti-drift rules for the bundle itself

The new Layer 1 workflow should not rely on undocumented prompt style or
legacy bundle conventions.

### Required Bundle-Governance Files

The bundle should define at least:

1. `bundle_governance/core_governance.md`
2. `bundle_governance/prompt_sop.md`
3. `bundle_governance/prompt_layout.md`
4. `bundle_governance/action_policy.md`
5. `bundle_governance/review_audit_contract.md`
6. `bundle_governance/prompt_contract.json`

These files govern the workflow bundle itself. They are not part of the
permanent Layer 1 generated governance set.

### `core_governance.md`

Purpose:

- define the local governance rules for the workflow bundle
- declare the bundle's scope, non-goals, and anti-drift policy

Must include:

- bundle purpose
- owning layer
- permitted artifact classes
- permanent versus temporary artifact rule
- prohibition on runtime/platform operational drift

### `prompt_sop.md`

Purpose:

- define how prompts for this bundle are authored, revised, and reviewed

Must include:

- prompt authoring principles
- scope discipline rules
- required citation behavior for review and audit prompts
- refinement constraints
- prompt-change review expectations

### `prompt_layout.md`

Purpose:

- define the standard structure and ordering for prompts in this bundle

Must include guidance for sections such as:

- objective
- scope
- required inputs
- artifact responsibilities
- acceptance criteria
- rejection criteria
- output instructions

The exact headings may vary by step, but the logical order should remain
stable.

### `action_policy.md`

Purpose:

- define what non-prompt actions this workflow is allowed to perform

Must include:

- allowed action types
- forbidden action types
- required separation between governance generation and code mutation
- publish-control expectations

### `review_audit_contract.md`

Purpose:

- define the minimum review and audit obligations for the workflow

Must include:

- what review must reject
- what audit must verify
- defect classes
- routing expectations for refine versus fail

### `prompt_contract.json`

Purpose:

- define machine-checkable prompt constraints where practical

Should validate at least:

- required prompt files exist
- prompts contain required sections or markers where the implementation
  supports this
- review and audit prompts contain explicit rejection logic
- refine prompt contains no instructions that normalize lower-layer drift

## Allowed Step Taxonomy

The workflow should use only a small, explicit set of step intents.

### Prompt-Driven Step Types

Allowed:

- `generate`
- `review`
- `refine`
- `audit`

Definitions:

- `generate` creates draft governance artifacts
- `review` performs scope and quality review with pass/reject outcome
- `refine` revises artifacts after fixable findings
- `audit` performs final semantic verification before approval

### Action Step Types

Allowed:

- `collect_context`
- `validate`
- `publish`
- `step_completion`

Definitions:

- `collect_context` gathers reference and comparison inputs
- `validate` runs deterministic rules against artifacts
- `publish` marks an approved set as active and records tracking metadata
- `step_completion` closes the workflow

### Human-Control Step Type

Allowed:

- `human_approval`

Definition:

- `human_approval` obtains explicit governance-owner acceptance before
  activation of the Layer 1 set

## Forbidden Action Intent

The Layer 1 workflow bundle must not perform actions intended to:

- mutate platform runtime code as part of governance generation
- implement repository bootstrap mechanics
- perform platform-specific operational setup
- generate Layer 2 constitutions
- generate Layer 3 bundle-local prompts or artifact mappings
- rewrite the `masterplan/` source documents

If such behavior is required, it belongs in another workflow layer or a
separate engineering task.

## Prompt Design Rules

All prompts in this bundle should follow these rules:

- they must state the owning layer explicitly
- they must distinguish permanent artifacts from temporary evidence
- they must define forbidden lower-layer content explicitly
- review and audit prompts must require direct citations for findings
- refine prompts must prioritize reclassification or rejection over
  polishing wrong-scope content
- prompts must treat masterplan inputs as authoritative references, not as
  editable outputs

## Review and Audit Defect Classes

The bundle-governance package should classify at least these defects:

- `scope_drift`
- `authority_misclassification`
- `metadata_noncompliance`
- `missing_required_structure`
- `forbidden_operational_content`
- `wrong_document_inventory`
- `invalid_promotion_scope`

These defect classes should drive routing decisions for refine versus fail.

## Routing Policy

The bundle-governance package should define a strict routing policy:

- fixable defects route to refine
- conceptual layer mismatch routes to fail
- wrong document inventory routes to fail
- invalid promotion scope routes to fail
- metadata omission or minor structure defects may route to refine

This policy should be reflected consistently in prompts, validators, and
workflow step wiring.

### Design Input Access Model

The workflow should receive both masterplan inputs as explicit reference
files in prompt context for generate, review, refine, and audit steps.

The initial design assumption should be:

- reference files are passed by fixed repository path
- the workflow treats them as read-only design authority
- the workflow must not rewrite or publish changes back into
  `masterplan/`

## Workflow Scope

### In Scope

The workflow may:

- generate Layer 1 governance documents
- refine Layer 1 governance documents after review findings
- validate Layer 1 governance documents against deterministic rules
- audit accepted Layer 1 governance documents for layer-boundary accuracy
- emit temporary evidence artifacts for review, validation, and audit

### Out of Scope

The workflow must not:

- define runtime architecture
- define install, publish, deploy, or registry mechanics
- define repository operating structure for a specific platform
- define bundle-local prompts, validators, or artifact mappings
- define Layer 2 platform standards
- define Layer 3 bundle outputs
- mutate implementation code as part of the governance generation run

If the workflow needs to describe how a platform operates, that content
belongs in a future Layer 2 workflow instead.

## Source Inputs

The workflow should treat the following as primary human-authored design
inputs:

- `masterplan/LAYER_ARCHITECTURE_MASTERPLAN.md`
- this specification document

These are reference blueprints and should not themselves be rewritten by
the workflow.

The workflow implementation should expose them to prompt-driven steps as a
declared reference-file set rather than relying on implicit filesystem
discovery.

## Target Permanent Document Set

The first implementation of the new Layer 1 workflow should generate
exactly these permanent Layer 1 governance artifacts:

1. `README.md`
2. `LAYER_MODEL.md`
3. `DOCUMENT_AUTHORITY.md`
4. `BUNDLE_TAXONOMY.md`
5. `GOVERNANCE_LIFECYCLE.md`
6. `METADATA_STANDARD.md`

This set is intentionally governance-focused and excludes runtime manuals.

## Permanent Document Roles

### `README.md`

Purpose:

- index the Layer 1 governance set
- define the high-level mission of Layer 1
- summarize the relationship between Layer 1, Layer 2, and Layer 3

Must include:

- governance set overview
- document map
- intended audience summary
- statement that Layer 1 excludes runtime/platform implementation

### `LAYER_MODEL.md`

Purpose:

- define the three-layer architecture
- establish scope boundaries for each layer
- define allowed dependency direction and change direction

Must include:

- role and objective for Layer 1, Layer 2, and Layer 3
- ownership boundary summary
- promotion overview
- boundary decision rule

### `DOCUMENT_AUTHORITY.md`

Purpose:

- define document authority classes
- define ownership and promotion rules
- define permanent versus temporary artifact distinction

Must include:

- authority vocabulary
- authority matrix
- promotion constraints
- conflict rule for metadata versus content

### `BUNDLE_TAXONOMY.md`

Purpose:

- define the conceptual bundle taxonomy for the ecosystem

Must include:

- bundle class definitions at governance level
- ownership summary by bundle class
- explicit statement that workflow-specific contracts are not owned by
  Layer 1

### `GOVERNANCE_LIFECYCLE.md`

Purpose:

- define lifecycle expectations across Layer 1, Layer 2, and Layer 3

Must include:

- lifecycle states
- creation, review, approval, revision, deprecation, and retirement rules
- promotion interaction rule
- publication versus approval rule

### `METADATA_STANDARD.md`

Purpose:

- define cross-ecosystem metadata rules for governed documents

Must include:

- required metadata fields
- allowed baseline values
- scan-policy rule
- scanner compliance expectations
- validation expectations

## Permanent Document Exclusions

The permanent Layer 1 set must not include documents whose primary purpose
is:

- runtime governance
- runtime operating procedures
- repository bootstrap mechanics
- installation or publish flow
- registry operations
- platform-specific validation logic

Those subjects belong in Layer 2 or lower.

## Output Location

The permanent Layer 1 output location should be a workflow-generated
system-governance path.

The exact path can be decided during implementation, but it should satisfy
these rules:

- it belongs under workflow-generated system docs, not `masterplan/`
- it is clearly distinguished from temporary evidence artifacts
- it is stable across runs
- it is treated as the active Layer 1 governance set only after approval

## Temporary Evidence Artifacts

The workflow should generate separate temporary artifacts for governance
control:

- review artifact
- validation artifact
- audit artifact

These artifacts must never be part of the permanent governance set.

## Artifact Classification

### Permanent Artifacts

Permanent Layer 1 artifacts should carry metadata consistent with:

- `doc_type: "system"`
- `authority: "workflow-generated"`
- `scan_policy: "include"`

### Temporary Evidence

Temporary artifacts should carry metadata consistent with:

- `doc_type: "review_artifact"` or `validation_artifact` or
  `audit_artifact`
- `authority: "workflow-generated"` or `derived`
- `scan_policy: "conditional"` or `exclude`

## Tracking and Publish Metadata Model

Artifact tracking should use two layers of metadata:

- per-file frontmatter for document-local classification
- a publish manifest for run-level tracking and active-set resolution

### Per-File Frontmatter

Every permanent Layer 1 markdown document should carry frontmatter for at
least:

- `doc_type`
- `authority`
- `scan_policy`
- `scan_reason`
- `layer`
- `lifecycle_status`
- `effective_version`

Temporary evidence artifacts should carry the same classification fields
where practical, but they do not need `effective_version` unless the
implementation benefits from it.

### Publish Manifest

The workflow should emit a machine-readable publish manifest as a separate
control artifact.

The initial design assumption should be one manifest per published
governance set version, for example:

- `governance_set_manifest.json`

The manifest should record at least:

- workflow id
- workflow layer
- change or run id
- change class
- artifact inventory
- artifact permanence class
- authority
- lifecycle status
- source step
- published timestamp
- effective version
- active set flag
- supersedes
- superseded by

The manifest is the primary machine-readable source for tracking which
generated set is active.

## Step Model

The workflow should use a small number of explicit steps with different
roles.

### Step 1: Collect Governance Context

Purpose:

- gather the reference and comparison context required to prevent
  duplication and lower-layer drift

Responsibilities:

- load the Layer 1 masterplan and this specification
- gather any declared Layer 2 or Layer 3 canonical inventories available
  to the implementation
- expose the collected context as read-only input to later steps

Output:

- governance context inventory

### Step 2: Generate Governance Set

Purpose:

- generate the initial permanent Layer 1 governance documents

Responsibilities:

- use the master plan and this specification as design input
- use the governance context inventory as comparison input
- generate all permanent target docs together so terminology stays aligned
- avoid platform/runtime operational content

Output:

- the full permanent governance set draft

### Step 3: Review Governance Set

Purpose:

- perform layer-boundary and governance-scope review

Responsibilities:

- detect Layer 2 or Layer 3 drift
- detect duplication with known lower-layer standards when comparison
  context exists
- detect missing required sections
- detect authority or metadata mismatch
- reject runtime/platform operational detail

Output:

- review artifact with findings and explicit pass/reject decision

### Step 4: Refine Governance Set

Purpose:

- revise the permanent docs only when review or validation identified
  fixable governance defects

Responsibilities:

- correct scope, structure, and terminology defects
- preserve Layer 1 boundaries
- refuse to "polish" content that belongs in a lower layer

Output:

- revised permanent governance set

### Step 5: Validate Governance Set

Purpose:

- run deterministic checks against the permanent docs

Responsibilities:

- confirm metadata presence and baseline validity
- confirm change classification is declared when the implementation
  supports a publish manifest
- confirm required document inventory exists
- confirm required sections exist
- confirm prohibited topics are absent or below threshold
- confirm permanent and temporary artifacts are separated

Output:

- validation artifact

### Step 6: Audit Governance Accuracy

Purpose:

- perform a final semantic audit after refinement and validation

Responsibilities:

- verify the accepted docs still belong in Layer 1
- verify promoted concepts were properly abstracted
- verify no temporary evidence was normalized into permanent standards

Output:

- audit artifact with explicit acceptance or rejection

Audit rejection routing:

- if audit finds fixable Layer 1 defects, route back to refine
- if audit finds conceptual layer mismatch, wrong document inventory, or
  invalid promotion scope, fail the workflow clearly

### Step 7: Human Approval Gate

Purpose:

- obtain explicit governance-owner acceptance before activation

Responsibilities:

- present the approved permanent set plus review, validation, and audit
  evidence
- require acceptance by the ecosystem governance owner or equivalent
  authority

Output:

- explicit approval decision

### Step 8: Publish Active Governance Set

Purpose:

- mark the approved permanent set as the active Layer 1 set

Responsibilities:

- publish only after review, validation, audit, and human approval succeed
- keep evidence artifacts separate from the permanent set
- mark the published set as active in both frontmatter and publish manifest
- supersede any prior active set without destroying historical traceability
- archive or retain prior manifests and prior generated sets as superseded
  versions rather than overwriting history blindly
- write final publish metadata as needed by the implementation

Output:

- active Layer 1 governance set

## Review Gates

The review step must reject if any of the following are present:

- runtime architecture details
- install, publish, deploy, or registry procedure definitions
- platform-specific implementation detail
- repository-specific operating instructions
- concrete Layer 3 artifact mappings
- generated evidence being described as permanent Layer 1 authority
- missing mandatory permanent documents
- missing mandatory sections in a permanent document

Review should produce direct citations to the offending content.

If lower-layer inventory context exists, review should also flag duplicate
material that properly belongs to Layer 2 or Layer 3.

## Validation Gates

Validation should enforce at least:

- all target permanent files exist
- all required metadata fields exist
- metadata values are valid against Layer 1 baseline vocabulary
- publish-manifest fields exist when publishing is attempted
- all required major sections exist
- required cross-document consistency holds
- forbidden operational topics are absent
- evidence artifacts are not classified as permanent system documents

## Audit Gates

Audit should focus on semantic correctness, especially:

- content truly belongs in Layer 1
- governance principles were not replaced by operational prose
- platform-specific detail was not abstracted incorrectly
- promotion language does not overclaim authority

## Rejection and Refinement Policy

Refinement should be allowed only for fixable defects such as:

- missing required section
- weak wording
- metadata omission
- missing publish-manifest field or tracking field
- minor scope leakage that can be removed cleanly

Refinement should not be used when:

- the document set is conceptually Layer 2 instead of Layer 1
- a document has the wrong purpose entirely
- the target document inventory is wrong

In such cases, the workflow should fail clearly rather than repeatedly
refining the wrong artifact.

## Artifact Tracking Requirements

The workflow should record enough metadata for each artifact to support
tracking:

- workflow id
- workflow layer
- artifact type
- authority
- permanence class
- lifecycle status where applicable
- source step
- change class
- change or run id

This is required so governance outputs and evidence can be distinguished
reliably.

Per-file frontmatter should hold document-local classification. The publish
manifest should hold run-level and active-set tracking state.

## Naming and Metadata Rules

The implementation should ensure:

- permanent Layer 1 docs are easy to identify as the active governance set
- evidence artifacts are clearly non-authoritative
- human-authored `masterplan/` docs remain excluded from operational scans
- generated Layer 1 docs do not claim `human-authored`
- prior active sets are retained or archived as superseded rather than
  silently discarded

## Non-Goals

This workflow is not intended to:

- create Layer 2 platform constitutions
- create Layer 3 bundles
- manage runtime implementation code
- define repository-local system operations
- act as a generic docs generator for unrelated domains

## Success Criteria

The new Layer 1 workflow is successful when:

- it produces a stable governance-only document set
- review rejects lower-layer drift reliably
- validation catches classification and structure defects deterministically
- audit confirms semantic Layer 1 correctness
- the generated output can govern multiple future Layer 2 cores without
  rewrite

## Implementation Readiness Checklist

The workflow is ready to implement when these decisions are accepted:

1. the target permanent document set
2. the temporary evidence artifact set
3. the review, validation, and audit gate definitions
4. the Layer 1 metadata baseline
5. the publication rule for the active governance set
6. the human approval gate
7. the publish-manifest tracking model

Only after these are accepted should the workflow package structure,
prompts, validators, and output paths be created.
