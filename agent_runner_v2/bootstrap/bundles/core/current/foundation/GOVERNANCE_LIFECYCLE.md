---
template_id: SYS-00-GL
version: "1.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 1 governance lifecycle standard; defines lifecycle states and promotion rules"
layer: "layer1"
lifecycle_status: "published"
effective_version: "01GF-20260719-c5e882c3"
managed_by: workflow-generated
---

> Managed by workflow: `01_governance_foundation_v1` / step: `publish_governance_foundation_set`
> This file is workflow-generated and protected from manual edits.

# Governance Lifecycle

## Purpose

This document defines the lifecycle model for governed documents across
all three layers. It establishes the states a document may occupy, the
rules for transitioning between states, and the relationship between
lifecycle and layer promotion.

## Lifecycle States

Every governed document exists in one of the following lifecycle states.

| State | Meaning |
|---|---|
| `draft` | Initial or in-progress content. Not yet reviewed or approved. |
| `review` | Under active review. Findings may route back to draft for refinement. |
| `approved` | Passed review, validation, and audit. Ready for publication. |
| `published` | Active and authoritative. The current governed version. |
| `superseded` | Replaced by a newer version. Retained for audit trail. |
| `deprecated` | No longer recommended for use. Still available for reference. |
| `retired` | Removed from active governance. Historical record only. |

### State Transitions

```
draft --> review --> approved --> published --> superseded
  ^         |           |                          |
  |         v           |                          |
  +--- refine loop      |                          |
                        v                          |
                    deprecated --> retired <-------+
```

### Draft

The initial state for all generated or authored content before any review
gate.

**Entry**: Document creation.

**Exit**:
- To `review`: when submitted for formal review.
- To `deprecated`: if abandoned before review.

### Review

The document is under active review. Findings may require refinement.

**Entry**: From `draft` when submitted for review.

**Exit**:
- To `draft`: if refinements are needed (refine loop).
- To `approved`: if review, validation, and audit all pass.
- To `deprecated`: if rejected and the owning authority decides not to
  proceed.

### Approved

The document has passed all review, validation, and audit gates. It is
ready for publication but is not yet the active version.

**Entry**: From `review` when all gates pass.

**Exit**:
- To `published`: when explicitly published by the owning workflow or
  authority.
- To `deprecated`: if the owning authority withdraws approval before
  publication.

### Published

The document is the active, authoritative version. It is the canonical
source for its governed scope.

**Entry**: From `approved` when explicitly published.

**Exit**:
- To `superseded`: when a newer version is published.
- To `deprecated`: if the owning authority withdraws the document without
  a replacement.

### Superseded

The document has been replaced by a newer version. It is retained for
audit trail and historical reference.

**Entry**: From `published` when a newer version is published.

**Exit**:
- To `retired`: after the retention period or when no longer needed for
  audit.

### Deprecated

The document is no longer recommended for use but remains available for
reference.

**Entry**: From any state when the owning authority decides to withdraw
without immediate replacement or retirement.

**Exit**:
- To `retired`: when formally retired.

### Retired

The document is removed from active governance. It exists only as a
historical record.

**Entry**: From `superseded` or `deprecated`.

**Exit**: None. Retired is a terminal state.

## Publication Rule

### Approval vs. Publication

Approval and publication are distinct states:

- **Approval** means the content has passed all governance gates (review,
  validation, audit) and is accepted by the owning authority. An approved
  document is *ready* to become active but is not yet the canonical
  version.

- **Publication** means the approved content is now the active,
  authoritative version. Publication must update tracking metadata
  (frontmatter `lifecycle_status` and the publish manifest) and supersede
  any prior active version.

A document must be approved before it can be published. Approval without
publication means the document is ready but not yet active.

### Publication Metadata

Publication must record:

- the effective version identifier
- the publishing workflow and step
- the publication timestamp
- the superseded version (if any)
- the active-set flag

This metadata is maintained in the publish manifest and in each document's
frontmatter.

### Superseding Without Destruction

When a new version is published:

1. The prior published version transitions to `superseded`.
2. The prior version is retained in its original location or archived to a
   history location.
3. The new version carries the superseded version identifier in its
   tracking metadata.
4. The publish manifest is updated to reflect the new active set.

Historical versions must never be silently discarded. The audit trail
remains intact.

## Promotion and Lifecycle Interaction

### Lifecycle vs. Layer Promotion

Lifecycle state changes are independent of layer promotion:

- A document can move from `draft` to `published` within its owning layer
  without changing layers.
- Layer promotion (moving a document from Layer 3 to Layer 2, or from
  Layer 2 to Layer 1) is a separate governance action that requires
  explicit review and acceptance by the target layer authority.

### Promotion Constraints

A document being promoted to a higher layer must:

1. pass review against the target layer's scope rules
2. be reclassified under the target layer's metadata conventions
3. be accepted by the target layer's owning authority
4. reset its lifecycle to `draft` or `review` in the target layer context

A document does not retain its original layer's lifecycle state after
promotion. It enters the target layer at the appropriate state for newly
introduced content.

### Promotion Gate Interaction

When a document is promoted, its lifecycle in the source layer is
unaffected. It remains available at its current state in the source layer
while the promoted copy proceeds independently in the target layer.

## Revision

### What Triggers Revision

A document may be revised when:

- a review identifies fixable defects
- a validation check fails
- an audit identifies scope or boundary issues
- the owning authority requests changes

### Revision Scope

Revisions may address:

- missing required sections
- weak or ambiguous wording
- metadata omission or misclassification
- minor scope leakage that can be removed cleanly

Revisions must not:

- rewrite the document for a different layer
- change the document's fundamental purpose
- silently absorb responsibilities from another layer

### Refine Loop

When a review or validation identifies fixable defects, the document
returns to `draft` for refinement, then re-enters `review`. This
refine-review loop may repeat until all fixable defects are resolved or
the workflow exhausts its refinement budget.

Defects that are not fixable through refinement (conceptual layer
mismatch, wrong document inventory, invalid promotion scope) must route to
failure, not to an indefinite refine loop.

## Deprecation

### When to Deprecate

A document should be deprecated when:

- it is no longer needed in active governance
- it has been replaced by a different document (not a newer version of the
  same document)
- the owning authority decides to withdraw it

### Deprecation Metadata

A deprecated document must:

- carry `lifecycle_status: "deprecated"` in its frontmatter
- include a deprecation notice explaining the reason and, if applicable,
  the replacement document

### Deprecation vs. Superseding

- **Superseding** replaces one version of a document with a newer version
  of the same document.
- **Deprecation** withdraws a document without necessarily replacing it
  with a versioned successor.

## Retirement

### When to Retire

A document should be retired when:

- it has been superseded or deprecated for a sufficient retention period
- it is no longer needed for audit or historical reference
- the owning authority decides to archive it

### Retirement Metadata

A retired document must:

- carry `lifecycle_status: "retired"` in its frontmatter
- include a retirement notice

### Retention

Retirement does not mean deletion. Retired documents remain in the
repository as historical records. The publish manifest records the
retirement for audit trail completeness.

## Lifecycle in Staged vs. Published Contexts

### Staged Run Outputs

Documents generated during a workflow run but not yet published are
staged run outputs. They carry:

- `lifecycle_status: "draft"`

They live under a run-specific path and are not treated as authoritative.

### Published Active Set

After publication, the documents carry:

- `lifecycle_status: "published"`

They live under the active-set path and are the canonical governed
version.
