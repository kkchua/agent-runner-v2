---
doc_type: "review_artifact"
authority: "workflow-generated"
scan_policy: "exclude"
scan_reason: "run-scoped platform core review; temporary evidence artifact"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-20260720-fd35ddf1"
---

# Platform Core Review

## Decision

**APPROVED**

The staged Layer 2 platform core constitution set is accepted for
deterministic validation. All six permanent documents are present,
correctly structured, properly metadata-classified, and conform to Layer 2
scope boundaries. No forbidden content was detected.

## Layer Boundary Findings

### Layer 1 Governance Redefinition

**Result: PASS**

No document redefines or contradicts Layer 1 governance.

- README.md explicitly declares: "Layer 1 is inherited, not modified" and
  lists four specific non-modification commitments (does not change doc_type
  meanings, does not alter three-layer architecture, does not modify
  ownership/promotion rules, does not assert authority beyond this platform).
- METADATA_CONTRACT.md explicitly states: "This contract does not modify or
  contradict Layer 1 baseline values." It extends vocabulary with
  platform-specific semantics for existing Layer 1 values
  (bundle_definition, platform_standard, platform-owned, bundle-owned)
  without introducing new literal strings or changing baseline meanings.
- No document redefines layer definitions, cross-ecosystem ownership rules,
  generic document authority rules, or generic metadata classification rules.
- No document contains forbidden Layer 1 content (runtime internals,
  bootstrap mechanics, install/publish/deploy procedures, path resolution
  logic, platform-specific validation rules as Layer 1 authority).
- BUNDLE_AUTHORING_CONTRACT.md correctly constrains Layer 3 bundles:
  "Layer 3 bundles must operate within this contract. They must not modify
  Layer 1 ecosystem governance or this Layer 2 platform constitution."

### Layer 3 Bundle-Specific Drift

**Result: PASS**

No document contains bundle-specific outputs or examples presented as
platform-wide rules.

- BUNDLE_AUTHORING_CONTRACT.md defines the interface contract for Layer 3
  bundles (required files, TOML format, metadata compliance) at the
  platform level. It specifies what bundles must provide, not what any
  specific bundle produces.
- Examples in SHARED_SERVICES.md and VALIDATION_CONTRACT.md are schematic
  interface examples (function signatures, decorator patterns) that
  illustrate the platform service contract. They are clearly labeled as
  examples and do not present bundle-specific outputs as platform rules.
- No document contains concrete workflow bundle inventories, specific
  prompt content, or bundle-local artifact mappings masquerading as
  platform standards.
- Known workflow bundles are referenced by name only in the context
  inventory (a temporary evidence artifact), not in permanent docs.

### Forbidden Operational Content

**Result: PASS**

No operational bootstrap mechanics or repository setup instructions were
found. The documents describe the platform operating model, not how to
bootstrap a repository or install the platform. RUNTIME_MODEL.md describes
execution modes conceptually (how CLI, daemon, and manual modes work)
without providing installation or setup procedures.

### Platform Identity

**Result: PASS**

Platform identity is clear and consistent across all six documents.

- All six documents carry `platform: "agent-runner-v2"` in YAML frontmatter.
- README.md defines the platform identity in its Platform Identity section:
  "agent-runner-v2 is a standalone, multi-step AI workflow runner."
- Every document references agent-runner-v2 by name in its content.
- The platform is consistently described as a Layer 2 platform core
  throughout.

## Structure Findings

### Required Document Inventory

**Result: PASS**

All six required permanent documents are present in the staged set:

| Document | File | Template ID | Present |
|---|---|---|---|
| Platform Index | README.md | SYS-02-IDX | Yes |
| Runtime Model | RUNTIME_MODEL.md | SYS-02-RM | Yes |
| Bundle Authoring Contract | BUNDLE_AUTHORING_CONTRACT.md | SYS-02-BAC | Yes |
| Shared Services | SHARED_SERVICES.md | SYS-02-SS | Yes |
| Metadata Contract | METADATA_CONTRACT.md | SYS-02-MC | Yes |
| Validation Contract | VALIDATION_CONTRACT.md | SYS-02-VC | Yes |

### Document Map Completeness

**Result: PASS**

The README.md document map includes all six documents including itself.
The map explicitly states: "The document map includes itself. The published
set inventory remains six documents, not five companion documents plus an
implicit index."

### Required Sections Per Document

**Result: PASS**

All mandatory sections are present in each document:

- README.md: Platform Identity, Document Map, Layer 1 Inheritance,
  Relationship to Other Layers, Audience.
- RUNTIME_MODEL.md: Step Model (prompt-driven, action-driven, step types),
  Execution Paths (CLI, Daemon, Manual), Job Lifecycle (Init, Execute,
  Route, Review/Refine, Approve, Publish, Completion), Coder Integration
  (invocation, roles, role policies), Rejection And Retry (rejection model,
  refine loop, replan, failure routing, reject code routing), Notification
  Model (integration, events, configuration).
- BUNDLE_AUTHORING_CONTRACT.md: Required Bundle Files, workflow.toml Format
  (all sections documented), Artifact Key Conventions, Bundle Governance
  Requirements, Metadata Compliance.
- SHARED_SERVICES.md: Context Extensions, Artifact Resolution, Path
  Contracts, Meta Sidecar, Notification Integration, Backend Sync Protocol,
  Action Registration.
- METADATA_CONTRACT.md: Platform doc_type Values, Platform authority Values,
  Additional Frontmatter Fields, Inheritance Rules, Scan Policy
  Expectations.
- VALIDATION_CONTRACT.md: ValidationPlan Pattern, Section Checks,
  Frontmatter Enforcement, File Existence Checks, Bundle Validator
  Composition (with guidance for validate_* actions).

### Evidence Artifact Separation

**Result: PASS**

No evidence artifacts are presented as permanent platform standards. The
six permanent documents are all classified as `doc_type: "platform_standard"`
with `authority: "workflow-generated"`. Temporary evidence artifacts
(context inventory, review, validation, audit) are properly separated and
carry appropriate evidence doc_types.

## Metadata Findings

### Frontmatter Compliance

**Result: PASS**

All six permanent documents carry compliant YAML frontmatter:

| Field | README | RUNTIME | BAC | SS | MC | VC |
|---|---|---|---|---|---|---|
| template_id | SYS-02-IDX | SYS-02-RM | SYS-02-BAC | SYS-02-SS | SYS-02-MC | SYS-02-VC |
| version | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| doc_type | platform_standard | platform_standard | platform_standard | platform_standard | platform_standard | platform_standard |
| authority | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated |
| scan_policy | include | include | include | include | include | include |
| scan_reason | present | present | present | present | present | present |
| layer | layer2 | layer2 | layer2 | layer2 | layer2 | layer2 |
| platform | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 |
| lifecycle_status | draft | draft | draft | draft | draft | draft |
| effective_version | 02PC-... | 02PC-... | 02PC-... | 02PC-... | 02PC-... | 02PC-... |
| managed_by | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated |

### Layer 1 Baseline Compliance

**Result: PASS**

- All `doc_type` values (`platform_standard`) are defined in Layer 1
  vocabulary.
- All `authority` values (`workflow-generated`) are defined in Layer 1
  vocabulary.
- All `scan_policy` values (`include`) are defined in Layer 1 vocabulary.
- No document claims `human-authored` authority (correct for generated
  docs).
- No generated document presents itself as derived from a human-authored
  source.

### Lifecycle State

**Result: PASS**

All six staged documents carry `lifecycle_status: "draft"`. No document
uses `published` or `active` values, which would be inappropriate for
staged (non-published) content.

## Cited Evidence

No offending content was found. The following positive citations confirm
compliance:

1. README.md, Layer 1 Inheritance section: "Layer 1 is inherited, not
   modified. This platform constitution: Does not change the meaning of
   any Layer 1 doc_type or authority value."

2. METADATA_CONTRACT.md, Overview section: "This contract does not modify
   or contradict Layer 1 baseline values. Layer 1 defines the common field
   names and baseline vocabulary. This document extends them for the
   agent-runner-v2 platform."

3. README.md, Document Map section: "The document map includes itself. The
   published set inventory remains six documents, not five companion
   documents plus an implicit index."

4. All six documents: `lifecycle_status: "draft"` in frontmatter confirms
   correct staged-state classification.

5. All six documents: `platform: "agent-runner-v2"` in frontmatter confirms
   consistent platform identity.

6. BUNDLE_AUTHORING_CONTRACT.md, Overview: "Layer 3 bundles must operate
   within this contract. They must not modify Layer 1 ecosystem governance
   or this Layer 2 platform constitution." -- correctly positions the
   contract as a Layer 2 interface definition, not Layer 3 drift.

## Next Action

The staged Layer 2 platform core constitution set is ready for
deterministic validation. Proceed to the validation step
(`validate_platform_core_docs`) to run machine-checkable rules against
the six permanent documents.
