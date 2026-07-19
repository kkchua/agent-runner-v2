---
template_id: "SYS-00-GL"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Layer 1 governance lifecycle standard"
layer: "layer1"
lifecycle_status: "published"
effective_version: "01GF-20260719-0864b1f2"
managed_by: workflow-generated
---

> Managed by workflow: `01_governance_foundation_v1` / step: `publish_governance_foundation_set`
> This file is workflow-generated and protected from manual edits.

# Governance Lifecycle

## Overview

This document defines the lifecycle states, approval and publication
rules, revision, deprecation, and retirement rules for governed documents
across all layers.

The lifecycle model ensures that every governed document has a known
state, a clear path through creation to retirement, and explicit rules
governing transitions between states.

## Lifecycle States

Every governed document exists in exactly one lifecycle state at any
given time.

| State | Description |
|---|---|
| `draft` | The document is being authored or generated. It is not yet active or authoritative. |
| `review` | The document is under formal review. Findings must be resolved before advancing. |
| `approved` | The document has passed review, validation, and audit gates. It is accepted but not yet published as the active version. |
| `published` | The document is the active, authoritative version within its layer and scope. |
| `revised` | A new version of a published document is being prepared. The prior version remains active until the revision is published. |
| `deprecated` | The document is still accessible but no longer authoritative. Consumers should migrate to a replacement. |
| `retired` | The document is archived and no longer in active use. It is preserved for historical traceability only. |

### State Transition Rules

The following transitions are allowed:

- `draft` -> `review`: document is submitted for formal review
- `review` -> `approved`: review findings resolved and accepted
- `review` -> `draft`: review returned fixable findings, returned to
  authoring
- `approved` -> `published`: document is activated as the current
  authoritative version
- `published` -> `revised`: a new revision is initiated
- `revised` -> `review`: the revised draft is submitted for review
- `published` -> `deprecated`: the document is no longer authoritative
- `deprecated` -> `retired`: the document is fully retired and archived

Transitions not listed above are not allowed without explicit governance
approval.

## Publication Rule

### Approval Versus Publication

Approval and publication are distinct lifecycle events.

- **Approval** means the document has passed all review, validation, and
  audit gates and is accepted by the relevant authority.
- **Publication** means the document is activated as the current
  authoritative version within its layer and scope.

A document may be approved without being published (for example, when a
prior version is still active). A document must never be published without
approval.

### Publication Requirements

Before a document can be published, the following conditions must be met:

1. The document has passed all required review, validation, and audit
   gates.
2. Human approval has been obtained for the layer and document class
   involved.
3. Any prior active version has been explicitly superseded.
4. A publish manifest or equivalent tracking record has been created.
5. Historical versions are retained or archived for traceability.

### Superseding

When a new version of a document is published, the prior version must be
explicitly superseded. The superseded version moves to `deprecated` or
`retired` state depending on whether it should remain accessible for
reference.

Superseded documents must not be deleted or overwritten. They must be
preserved for audit trail and historical traceability.

### Publish Manifest

Every publication event should produce a machine-readable manifest that
records at minimum:

- the document or document set published
- the version or effective run identifier
- the publication timestamp
- the superseded version, if any
- the authority that approved the publication

## Revision

### Initiating a Revision

A published document may be revised when:

- governance requirements change
- defects are discovered in the current version
- new layers, bundles, or platform cores require updated rules

A revision is initiated by creating a new `draft` version while the
current published version remains active. The draft progresses through the
normal lifecycle (review -> approved -> published) before replacing the
active version.

### Revision Constraints

During revision:

- the active published version remains authoritative
- the draft must be reviewed against the same gates as the original
- changes must be explicitly documented
- the prior version must be superseded upon publication of the revision

## Deprecation

A document enters `deprecated` state when:

- a replacement has been published
- the document is no longer needed for active governance
- the owning authority has explicitly deprecated it

Deprecated documents remain accessible for reference and historical
context but must not be treated as authoritative. Consumers should migrate
to the replacement document.

## Retirement

A document enters `retired` state when:

- it has been deprecated and the owning authority determines it is no
  longer needed for reference
- it is superseded and the replacement has been stable for a sufficient
  period

Retired documents are archived and preserved for historical traceability.
They must not be deleted, as the audit trail depends on their continued
existence.

## Promotion And Lifecycle Interaction

### Promotion Across Layers

When a document is promoted from a lower layer to a higher layer (for
example, a Layer 3 bundle guide being promoted to a Layer 2 platform
standard), the lifecycle resets for the target layer.

The promotion process follows these steps:

1. The document is reviewed against the target layer scope.
2. It is reclassified under the target layer metadata rules.
3. It enters the target layer lifecycle at `draft` state.
4. It progresses through the target layer's review, approval, and
   publication gates independently of its origin layer.

### Promotion Does Not Preserve State

A document promoted to a higher layer does not carry its lower-layer
lifecycle state with it. A `published` document in Layer 3 does not
automatically become `published` in Layer 2. It must pass through the
Layer 2 lifecycle gates.

### Lifecycle and Layer Boundaries

The lifecycle of a document is scoped to the layer that owns it:

- Layer 1 documents follow the lifecycle defined here, governed by
  ecosystem authority.
- Layer 2 documents may extend these states with platform-specific
  substates, but must not contradict the baseline states.
- Layer 3 documents follow the lifecycle defined by their parent Layer 2
  core, which in turn inherits from this baseline.
