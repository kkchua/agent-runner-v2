---
template_id: SYS-00-DA
version: "1.0"
doc_type: "system"
authority: "workflow-generated"
managed_by: workflow-generated
scan_policy: "include"
scan_reason: "Layer 1 governance standard; included in operational scans"
layer: "layer1"
lifecycle_status: "published"
effective_version: "01GF-20260719-96e730ab"
---

> Managed by workflow: `01_governance_foundation_v1` / step: `publish_governance_foundation_set`
> This file is workflow-generated and protected from manual edits.

# Document Authority

## Overview

This document defines the authority vocabulary, document authority matrix,
promotion constraints, and permanent-versus-temporary artifact rules for
the ecosystem.

Every governed document carries an explicit authority classification.
This prevents two common failures:

- Generated artifacts pretending to be constitutional documents.
- Reference blueprints being mistaken for operational system outputs.

## Authority Vocabulary

### Authority Values

Every document must declare its authority using one of the following
values:

| Value | Meaning |
|-------|---------|
| `human-authored` | Canonical content is maintained directly by humans. |
| `workflow-generated` | Canonical content is produced and maintained by a workflow. |
| `platform-owned` | Canonical content is owned by a specific Layer 2 platform core. |
| `bundle-owned` | Canonical content is owned by a specific Layer 3 bundle. |
| `derived` | Content is generated from another authoritative source and is not itself the root authority. |

### Interpretation Rules

- `human-authored` means humans maintain the authoritative source text.
- `workflow-generated` means the workflow is the authoritative producer
  for that document.
- `platform-owned` means the owning Layer 2 core governs the content.
- `bundle-owned` means the owning Layer 3 bundle governs the content.
- `derived` means the artifact was produced from another source and should
  not be treated as the origin of truth.

### Permanent versus Temporary Artifacts

Ecosystem artifacts fall into two permanence classes:

**Permanent artifacts** are the governed document set that represents
stable authority for a layer. They:

- Carry `doc_type: "system"`, `"platform_standard"`, or `"bundle_definition"`.
- Carry authority values of `human-authored`, `workflow-generated`,
  `platform-owned`, or `bundle-owned`.
- Are subject to lifecycle management (creation, review, approval,
  publication, revision, deprecation, retirement).

**Temporary evidence artifacts** are run-scoped outputs that support
review, validation, and audit processes. They:

- Carry `doc_type: "review_artifact"`, `"validation_artifact"`, or
  `"audit_artifact"`.
- Carry authority values of `workflow-generated` or `derived`.
- Must never be treated as permanent Layer 1 authority.
- Must never be promoted to permanent status without explicit review
  and reclassification.

## Document Authority Matrix

The authority matrix defines the expected ownership model for every
document class across all three layers.

| Layer | Document Class | Typical `doc_type` | Allowed `authority` | Notes |
|-------|---------------|-------------------|--------------------|-------|
| Layer 1 | Master plan / blueprint | `masterplan` | `human-authored` | Reference-only architecture source. Normally excluded from operational scans. |
| Layer 1 | Governance standard | `system` | `human-authored`, `workflow-generated` | Must represent ecosystem-wide governance only. |
| Layer 1 | Review / audit evidence | `review_artifact`, `audit_artifact`, `validation_artifact` | `workflow-generated`, `derived` | Evidence is not constitutional authority. |
| Layer 2 | Platform constitution | `platform_standard`, `system` | `platform-owned`, `human-authored`, `workflow-generated` | Owns platform-specific operating standards. |
| Layer 2 | Platform-generated evidence | `review_artifact`, `validation_artifact`, `audit_artifact` | `workflow-generated`, `derived` | Supports Layer 2 compliance and evolution. |
| Layer 3 | Bundle definition | `bundle_definition` | `bundle-owned`, `human-authored`, `workflow-generated` | Concrete bundle contract within a Layer 2 context. |
| Layer 3 | Workflow output | `workflow_output` | `workflow-generated`, `bundle-owned`, `derived` | May be canonical for the bundle output, but not for higher-layer governance. |
| Layer 3 | Review / validation / audit outputs | `review_artifact`, `validation_artifact`, `audit_artifact` | `workflow-generated`, `derived` | Operational evidence only. |

### Authority Constraints by Layer

**Layer 1 constraints:**

- A Layer 1 `masterplan` must normally be `human-authored`.
- A Layer 1 governance standard may be `workflow-generated` only if the
  generating workflow itself is governed by an accepted Layer 1 model.
- Layer 1 evidence artifacts must never be mistaken for permanent
  constitutional documents.

**Layer 2 constraints:**

- Layer 2 platform standards must clearly identify the owning platform.
- Layer 2 must not label platform-specific operating rules as generic
  ecosystem authority.

**Layer 3 constraints:**

- Layer 3 outputs may be authoritative for the bundle that owns them.
- Layer 3 outputs must not claim Layer 1 or Layer 2 constitutional
  authority unless explicitly promoted through a higher-layer process.

### Conflict Rule

If document authority conflicts with document content, content scope wins
for classification and the document must be flagged.

Examples of misclassification:

- A document marked `masterplan` that contains operational runbook detail.
- A document marked `workflow_output` that tries to define ecosystem
  governance.
- A document marked `system` but limited to one platform (belongs in
  Layer 2, not Layer 1).
- A review artifact marked as a system authority document.
- A generated artifact claiming `human-authored` authority.
- A platform-specific standard pretending to be Layer 1 governance.

## Promotion Rules

### Promotion Requirement

Documents do not become higher-layer authority merely because they are
useful, widely reused, or frequently referenced.

Promotion to a higher layer requires all three conditions:

1. **Explicit review** against the target layer scope.
2. **Reclassification** under the target layer metadata rules (including
   `doc_type`, `authority`, `scan_policy`, and `layer` fields).
3. **Acceptance** by the owning authority of that higher layer.

### Promotion Examples

- A Layer 3 bundle guide does not become a Layer 2 platform standard by
  convention alone.
- A Layer 2 platform standard does not become Layer 1 governance because
  multiple platforms copied it.
- A generated document that originated in a lower layer stays in that
  layer until explicitly promoted.

### Anti-Promotion Rule

No lower-layer artifact may silently absorb the authority of a higher
layer. If a document's content scope expands beyond its declared layer,
the document must be either:

- Reclassified and promoted through the formal promotion process, or
- Scoped back to its declared layer.

### Evidence Promotion Prohibition

Temporary evidence artifacts (`review_artifact`, `validation_artifact`,
`audit_artifact`) must never be promoted directly to permanent authority.
If evidence content informs a permanent standard, a new permanent document
must be created through the normal generation, review, and approval
process.

### Authority and Lifecycle Interaction

Authority classification interacts with lifecycle state as follows:

- A document with `authority: "workflow-generated"` in `lifecycle_status:
  "draft"` is a staged output, not yet active.
- A document becomes authoritative for its layer only after publication
  (`lifecycle_status: "published"`).
- A document with `authority: "derived"` must never reach
  `lifecycle_status: "published"` as a permanent standard.
- Retired documents retain their authority classification for audit
  traceability but carry `lifecycle_status: "retired"`.
