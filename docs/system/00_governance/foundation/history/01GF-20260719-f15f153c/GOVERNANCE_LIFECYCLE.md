---
template_id: SYS-00-GL
version: "1.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Layer 1 governance foundation document; required for operational scans"
layer: "layer1"
lifecycle_status: "published"
effective_version: "01GF-20260719-f15f153c"
managed_by: workflow-generated
---

> Managed by workflow: `01_governance_foundation_v1` / step: `publish_governance_foundation_set`
> This file is workflow-generated and protected from manual edits.

# Governance Lifecycle Standard

## Lifecycle States

Governed documents pass through the following lifecycle states. The
lifecycle is linear with allowed backward transitions for revision and
deprecation.

| State | Meaning | Allowed Transitions |
|---|---|---|
| `draft` | Workflow-generated but not yet approved. | -> `published` (after approval) |
| `published` | Approved and active. This is the current authoritative version. | -> `revised`, -> `deprecated`, -> `retired` |
| `revised` | A new draft has superseded this version. The previous published version is retained for history. | -> `retired` |
| `deprecated` | Still visible but no longer recommended for active use. | -> `retired` |
| `retired` | Explicitly removed from active consideration. Retired documents are retained for audit only. | (terminal) |

### Draft

`draft` is the initial state for all workflow-generated documents. A draft
document has been produced but has not yet passed review, validation,
audit, and human approval.

Staged run outputs always carry `lifecycle_status: "draft"`. The publish
step is the only step that may transition a document to `published`.

### Published

`published` is the active authoritative state. A published document is the
current version used for governance, compliance, or operational reference.

Only the publish step may set `lifecycle_status: "published"`. Review,
validation, and audit steps operate on draft documents and do not
independently publish them.

### Revised

When a new draft version of a published document is accepted, the prior
published version transitions to `revised`. Revised versions are retained
for traceability but are not authoritative.

### Deprecated

A published document may be deprecated when it is scheduled for removal.
Deprecated documents remain available for reference but carry a warning
that they are no longer recommended for active use.

Deprecation does not immediately retire a document. Retirement is a
separate, explicit step.

### Retired

A retired document is explicitly removed from active consideration. It is
retained for audit and historical traceability only. Retired is a terminal
state.

---

## Publication Rule

### Publication vs. Approval

Publication and approval are distinct governance actions.

**Approval** is a human decision obtained through the human approval gate.
It confirms that the document set is acceptable to the governance
authority.

**Publication** is the mechanical action that transitions documents from
`draft` to `published`, updates the publish manifest, marks the set as
active, and supersedes any prior active set.

Approval precedes publication. Publication without approval is invalid.
Approval without publication leaves the set in draft state.

### Publication Requirements

Publication requires all of:

1. review pass
2. validation pass
3. audit pass
4. human approval obtained
5. publish manifest updated to reflect the new active set
6. prior active set transitioned to `revised` or retained as superseded

### Publication Scope

Publication applies to the permanent governance set only. Temporary
evidence artifacts (review, validation, audit) are never published as part
of the permanent set.

### Publication Artifacts

Publication produces:

- updated frontmatter (`lifecycle_status: "published"`) on each permanent
  document
- an updated publish manifest recording the new active set
- an archived manifest snapshot for historical traceability

---

## Revision

A revision cycle begins when a new draft document set is generated and
follows the full review -> validation -> audit -> approval -> publication
pipeline.

The new set supersedes the prior published set. The prior set transitions
to `revised` upon successful publication of the new set.

Revision does not silently overwrite the prior published version. Both
versions are retained: the new version as `published`, the prior version as
`revised`.

---

## Deprecation

A governance document or set may be deprecated when it is no longer
recommended for active use but has not yet been fully retired.

Deprecation requires:

1. explicit deprecation notice
2. identification of the replacement document or set (if any)
3. transition of `lifecycle_status` to `deprecated`

Deprecation is distinct from retirement. A deprecated document is still
accessible but carries a non-recommendation warning.

---

## Retirement

Retirement is the terminal state for a governance document or set.

Retirement requires:

1. confirmation that the document is no longer needed for active governance
2. transition of `lifecycle_status` to `retired`
3. retention of the retired document for audit traceability

Retired documents must not be reactivated. A replacement document must go
through the full draft-to-publication pipeline.

---

## Promotion and Lifecycle Interaction

Promotion across layers is a separate governance action from lifecycle
state transitions. A document may be `published` within its own layer
without being promoted to a higher layer.

When a document is promoted:

1. it must undergo review against the target layer scope
2. it must be reclassified under the target layer metadata rules
3. it must be accepted by the owning authority of the target layer
4. it enters the target layer in `draft` state and must pass that layer's
   full review -> validation -> audit -> approval -> publication pipeline

Promotion does not skip lifecycle states. A promoted document starts as a
draft in the target layer, regardless of its status in the source layer.
