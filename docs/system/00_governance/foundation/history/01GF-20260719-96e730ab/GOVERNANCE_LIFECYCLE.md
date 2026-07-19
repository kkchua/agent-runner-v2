---
template_id: SYS-00-GL
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

# Governance Lifecycle

## Overview

This document defines the lifecycle model for governed documents across
all three layers of the ecosystem.

Every permanent governed document moves through a defined set of
lifecycle states. Temporary evidence artifacts follow a simpler,
run-scoped lifecycle and must never enter the permanent publication
pipeline.

## Lifecycle States

### State Definitions

| State | Description |
|-------|-------------|
| `draft` | The document has been generated or authored but has not yet passed review, validation, and approval. Draft documents carry no active governance authority. |
| `in_review` | The document is under active review. Review findings may result in refinement or rejection. |
| `approved` | The document has passed review, validation, and audit and has received explicit human approval. It is ready for publication but is not yet the active version. |
| `published` | The document is the active, authoritative version for its layer and scope. Only one version of a given permanent document should be `published` at a time. |
| `superseded` | A previously published version that has been replaced by a newer published version. Superseded documents are retained for historical traceability. |
| `deprecated` | The document is still accessible but is no longer recommended for use. Deprecation is a warning state before retirement. |
| `retired` | The document is no longer active and should not be used as governance authority. Retired documents are retained for audit purposes only. |

### State Transitions

```
draft --> in_review --> approved --> published --> superseded
  |          |            |                          |
  |          |            |                          v
  |          |            |                       (retained in history)
  |          |            |
  |          v            v
  +------> refine <-------+
  |          |
  |          v
  +------> rejected
             |
             v
          (end state: no further processing unless re-initiated)

published --> deprecated --> retired
```

### Draft State

- All staged workflow outputs enter at `draft`.
- Draft documents carry no governance authority.
- A draft document may be revised freely during refinement.

### In-Review State

- A document enters `in_review` when a review step is active.
- Review may result in:
  - Approval (proceed to validation and audit).
  - Rejection with fixable findings (route to refine).
  - Rejection with non-fixable findings (terminal rejection).

### Approved State

- A document reaches `approved` after passing review, validation, audit,
  and explicit human approval.
- An approved document is ready for publication but is not yet the active
  version.
- Approval is a gate, not an endpoint.

### Published State

- A published document is the active, authoritative version for its layer
  and scope.
- Publication replaces any previously published version of the same
  document, which transitions to `superseded`.
- Only permanent documents may be published. Temporary evidence artifacts
  must never enter the published state.

### Superseded State

- A superseded document was previously the active published version.
- Superseded documents are retained indefinitely for historical
  traceability and audit.
- A superseded document may be referenced but must not be treated as
  current authority.

### Deprecated State

- Deprecation signals that a document is approaching retirement.
- During deprecation, consumers should migrate to the replacement
  document.
- Deprecation is a transitional state; a deprecated document should
  eventually be retired.

### Retired State

- A retired document is no longer active governance authority.
- Retired documents are retained for audit purposes only.
- Retirement is permanent. A retired document must not be reactivated
  without going through the full creation and review process again.

## Publication Rule

### Approval versus Publication

Approval and publication are distinct lifecycle events:

- **Approval** confirms that the document content meets governance
  standards. An approved document is correct but not yet active.
- **Publication** activates the document as the current authoritative
  version. Publication is the act of making the approved document the
  active governance reference.

A document must be approved before it can be published. Approval alone
does not confer active authority.

### Publication Requirements

Publication requires:

1. The document has passed review with no outstanding findings.
2. The document has passed deterministic validation.
3. The document has passed semantic audit.
4. The document has received explicit human approval.
5. A publish manifest or tracking record is created or updated to reflect
   the new active version.

### Publication Side Effects

When a document is published:

- Any previously published version of the same document transitions to
  `superseded`.
- The publish manifest is updated to record the new active version.
- The superseded version is retained in history for audit traceability.
- The new published version becomes the authoritative reference for its
  layer and scope.

### Anti-Publication Rules

The following must never be published as permanent active authority:

- Temporary evidence artifacts (`review_artifact`, `validation_artifact`,
  `audit_artifact`).
- Documents that have not passed all required gates.
- Documents whose metadata conflicts with their content scope.
- Documents claiming authority above the layer their content supports.

## Promotion And Lifecycle Interaction

### Promotion Lifecycle Path

When a document is promoted to a higher layer, it must follow the full
lifecycle path for the target layer:

1. The document is reclassified under the target layer metadata rules.
2. The document enters `draft` in the target layer context.
3. The document proceeds through review, validation, audit, and approval
   under the target layer's governance process.
4. Upon publication, the document becomes active authority in the target
   layer.

### Promotion Does Not Skip States

A document promoted from Layer 3 to Layer 2 does not automatically carry
its Layer 3 approval status. The promotion process requires fresh review
against Layer 2 scope and standards.

A document promoted from Layer 2 to Layer 1 requires fresh review against
Layer 1 scope and standards.

### Lifecycle State Reset on Promotion

When a document is promoted across layers, its lifecycle state resets to
`draft` in the target layer context. The document's prior lifecycle
history in the source layer is preserved for traceability but does not
confer authority in the target layer.

### Lifecycle and Authority Interaction

- A document in `draft` or `in_review` carries no active governance
  authority regardless of its declared `authority` value.
- A document becomes authoritative only at `published` state.
- A document in `superseded`, `deprecated`, or `retired` state retains
  its authority classification for audit traceability but is not active
  governance authority.
- Temporary evidence artifacts in any state must not carry authority
  values reserved for permanent documents.

### Revision Lifecycle

When a published document is revised:

1. A new draft version is created.
2. The existing published version remains active while the revision is
   in progress.
3. The revision proceeds through review, validation, audit, and approval.
4. Upon publication of the revision, the prior version transitions to
   `superseded`.
5. The revision becomes the new active published version.

### Deprecation and Retirement Lifecycle

- A document may be deprecated when a replacement is available or when
  the content is no longer applicable.
- Deprecation must include a reference to the replacement document when
  one exists.
- After a deprecation period, the document should be retired.
- Retirement is permanent and irreversible.
