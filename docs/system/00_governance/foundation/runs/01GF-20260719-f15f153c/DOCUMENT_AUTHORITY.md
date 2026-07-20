---
template_id: SYS-00-DA
version: "1.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Layer 1 governance foundation document; required for operational scans"
layer: "layer1"
lifecycle_status: "draft"
effective_version: "01GF-20260719-f15f153c"
managed_by: workflow-generated
---

> Managed by workflow: `01_governance_foundation_v1` / step: `refine_governance_foundation_docs`
> This file is workflow-generated and protected from manual edits.

# Document Authority Standard

## Authority Vocabulary

The following authority values define who owns the truth of a governed
document.

| Authority | Meaning |
|---|---|
| `human-authored` | Canonical content is maintained directly by humans. |
| `workflow-generated` | Canonical content is produced and maintained by a workflow. |
| `platform-owned` | Canonical content is owned by a specific Layer 2 platform core. |
| `bundle-owned` | Canonical content is owned by a specific Layer 3 bundle. |
| `derived` | Content is generated from another authoritative source and is not itself the root authority. |

Layer 2 and Layer 3 may introduce narrower authority values, but they must
preserve the distinction between canonical and derived content.

### Interpretation

- `human-authored`: humans maintain the authoritative source text
- `workflow-generated`: the workflow is the authoritative producer for
  that document
- `platform-owned`: the owning Layer 2 core governs the content
- `bundle-owned`: the owning Layer 3 bundle governs the content
- `derived`: the artifact was produced from another source and should not
  be treated as the origin of truth

---

## Document Authority Matrix

The authority matrix defines the expected ownership model for every
document class. This prevents two common failures:

- generated artifacts pretending to be constitutional documents
- reference blueprints being mistaken for operational system outputs

| Layer | Document Class | Typical `doc_type` | Allowed `authority` | Notes |
|---|---|---|---|---|
| Layer 1 | Master plan / blueprint | `masterplan` | `human-authored` | Reference-only architecture source. Normally excluded from operational scans. |
| Layer 1 | Governance standard | `system` | `human-authored`, `workflow-generated` | Must represent ecosystem-wide governance only. |
| Layer 1 | Review / audit evidence | `review_artifact`, `audit_artifact`, `validation_artifact` | `workflow-generated`, `derived` | Evidence is not constitutional authority. |
| Layer 2 | Platform constitution | `platform_standard`, `system` | `platform-owned`, `human-authored`, `workflow-generated` | Owns platform-specific operating standards. |
| Layer 2 | Platform-generated evidence | `review_artifact`, `validation_artifact`, `audit_artifact` | `workflow-generated`, `derived` | Supports Layer 2 compliance and evolution. |
| Layer 3 | Bundle definition | `bundle_definition` | `bundle-owned`, `human-authored`, `workflow-generated` | Concrete bundle contract within a Layer 2 context. |
| Layer 3 | Workflow output | `workflow_output` | `workflow-generated`, `bundle-owned`, `derived` | May be canonical for the bundle output, but not for higher-layer governance. |
| Layer 3 | Review / validation / audit outputs | `review_artifact`, `validation_artifact`, `audit_artifact` | `workflow-generated`, `derived` | Operational evidence only. |

### Authority Constraints By Layer

**Layer 1 constraints:**

- a Layer 1 `masterplan` should normally be `human-authored`
- a Layer 1 governance standard may be `workflow-generated` only if the
  generating workflow itself is governed by an accepted Layer 1 model
- Layer 1 evidence artifacts must never be mistaken for permanent
  constitutional documents

**Layer 2 constraints:**

- Layer 2 platform standards must clearly identify the owning platform
- Layer 2 must not label platform-specific operating rules as generic
  ecosystem authority

**Layer 3 constraints:**

- Layer 3 outputs may be authoritative for the bundle that owns them
- Layer 3 outputs must not claim Layer 1 or Layer 2 constitutional
  authority unless explicitly promoted through a higher-layer process

### Conflict Rule

If document authority conflicts with document content, content scope wins
for classification and the document should be flagged.

Examples:

- a document marked `masterplan` that contains operational runbook detail
  is misclassified
- a document marked `workflow_output` that tries to define ecosystem
  governance is misclassified
- a document marked `system` but limited to one platform probably belongs
  in Layer 2, not Layer 1

---

## Promotion Rules

### Promotion Principle

Documents do not become higher-layer authority merely because they are
useful, widely reused, or frequently referenced. Promotion is an explicit,
governed action.

### Promotion Requirements

Promotion to a higher layer requires all of:

1. explicit review against the target layer scope
2. reclassification under the target layer metadata rules
3. acceptance by the owning authority of that higher layer

### Promotion Examples

- a Layer 3 bundle guide does not become a Layer 2 platform standard by
  convention alone
- a Layer 2 platform standard does not become Layer 1 governance because
  multiple platforms copied it

### Permanent vs. Temporary Artifacts

**Permanent artifacts** are documents that form part of an active
governance or operating set. They carry `lifecycle_status` values such as
`draft`, `published`, `revised`, `deprecated`, or `retired`.

**Temporary artifacts** are run-scoped evidence outputs (review, audit,
validation) that support governance decisions but are never themselves
part of the permanent set. They carry appropriate `doc_type` classification
and must not be mistaken for constitutional documents.

A temporary artifact does not become permanent by surviving multiple runs.
Promotion from temporary to permanent requires explicit reclassification
and acceptance by the owning authority.

### Metadata Inheritance

The metadata convention inherits downward across layers:

- Layer 1 defines the common field names and baseline vocabulary
- Layer 2 may extend value sets for platform-specific needs
- Layer 3 may apply platform-specific values defined by its parent Layer 2
- no lower layer may redefine the meaning of Layer 1 baseline values

This preserves interoperability while allowing platform-specific detail
where needed.
