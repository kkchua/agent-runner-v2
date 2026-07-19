---
template_id: "SYS-00-GL"
version: "0.1.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "defines lifecycle rules for all governed documents across layers"
layer: "layer1"
lifecycle_status: "published"
effective_version: "01GF-20260719-4e51c88b"
managed_by: "workflow-generated"
---

> Managed by workflow: `01_governance_foundation_v1` / step: `publish_governance_foundation_set`
> This file is workflow-generated and protected from manual edits.

# Governance Lifecycle

## Purpose

This standard defines the lifecycle expectations for governed documents
across all three layers. It establishes the states a document may occupy,
the rules for transitioning between states, and the relationship between
lifecycle, promotion, and publication.

## Lifecycle States

Every governed document that participates in workflow scanning,
classification, review, or publication should carry a `lifecycle_status`
field. The following states form the baseline vocabulary.

### Standard Lifecycle States

| State | Meaning | Typical Context |
|---|---|---|
| `draft` | The document is in active development or generation. It has not been reviewed or approved. | Staged run outputs before review. |
| `review` | The document is under formal review. Findings may require refinement. | During review and refine cycles. |
| `approved` | The document has passed review, validation, and any required human approval. It is ready for publication but has not yet been marked active. | After approval gate, before publish. |
| `published` | The document is the active canonical version. It has been published to the designated current-set location and recorded in the publish manifest. | Active governance or platform constitution set. |
| `deprecated` | The document is still present but should no longer be used as the primary reference. A replacement or successor exists. | Prior active set after a new version is published. |
| `retired` | The document has been explicitly withdrawn. It may be archived but must not be treated as authoritative. | Removed standards or obsolete bundles. |

### Lifecycle State Transition Diagram

```
draft --> review --> approved --> published --> deprecated --> retired
  ^                    |                           |
  |     (rejected)     |                           |
  +--------------------+                           |
  |                                                |
  +-------- (re-promotion after major revision) ---+
```

### Transition Rules

**draft -> review**: A draft document enters review when the generating
workflow completes its initial generation step and a review step is
triggered.

**review -> draft**: If review or validation identifies fixable defects,
the document returns to draft for refinement. This cycle may repeat up to
a defined maximum before the workflow fails.

**review -> approved**: If review, validation, and audit all pass, and
any required human approval is obtained, the document transitions to
approved.

**approved -> published**: An approved document is published by the
publish step, which moves it to the active current-set location, records
it in the publish manifest, and sets its status to published.

**published -> deprecated**: When a new version of the document set is
published, the prior published set transitions to deprecated. Deprecated
documents remain accessible for audit trail but carry a clear indicator
that a successor exists.

**deprecated -> retired**: A deprecated document may be explicitly
retired when it is no longer needed for historical reference. Retired
documents are removed from the active document map.

**retired -> draft**: In rare cases, a retired standard may be
re-activated through a major revision. This requires a full lifecycle
cycle starting from draft.

## Publication Rule

### Approval vs Publication

Approval and publication are distinct lifecycle events:

- **Approval** confirms that the document set is correct, complete, and
  compliant with governance rules. Approval is the gate that allows
  publication to proceed.
- **Publication** marks the document set as the active canonical version.
  Publication includes writing the documents to the designated current-set
  location, recording a publish manifest, and superseding any prior
  active set.

A document set that is approved but not yet published is `approved`.
A document set that has been activated is `published`. The distinction
exists because approval may occur in a workflow step that is separate
from the publish action.

### Publication Requirements

Publication must only occur after all of the following are satisfied:

1. Review passes with no unresolved defects
2. Validation passes with no deterministic failures
3. Audit confirms semantic correctness and layer-boundary accuracy
4. Any required human approval is explicitly obtained
5. The publish manifest is complete and accurate

### Historical Traceability

Publication must preserve historical traceability:

- Prior active sets must be retained as deprecated versions, not silently
  discarded
- Prior publish manifests must be archived or retained in a history
  location
- The active publish manifest must record which prior version it
  supersedes
- Evidence artifacts from the publishing run must remain separate from the
  permanent document set

## Promotion And Lifecycle Interaction

### Promotion vs Lifecycle

Promotion (movement to a higher layer) is distinct from lifecycle
progression. A document can progress through its lifecycle within its
own layer without changing layers. Promotion to a higher layer is a
separate deliberate act.

### Promotion Lifecycle Rules

When a document is promoted to a higher layer:

1. It must be reclassified under the target layer metadata rules
2. Its `lifecycle_status` resets to `draft` in the target layer
3. It must pass through the full review, validation, audit, and approval
   cycle at the target layer
4. The original lower-layer document is not automatically deprecated or
   retired: that is a separate decision for the owning authority of the
   source layer

### Promotion Does Not Propagate Automatically

Promoting a document to a higher layer does not automatically promote or
deprecate its source:

- The source document remains at its original lifecycle status in its
  original layer
- The promoted copy is a new document governed by the target layer
- The relationship between source and promoted copy should be documented
  but does not create an automatic dependency

### Revision and Supersession

**Minor revisions** (wording fixes, clarifications, metadata corrections)
may transition from `published` back to `draft` for a targeted refine
cycle without fully deprecating the published version.

**Major revisions** (scope changes, structural reorganization, conceptual
redesign) should treat the new version as a separate artifact set:
the prior version is deprecated when the new version is published.

### Lifecycle for Temporary Evidence Artifacts

Temporary evidence artifacts (review, validation, audit outputs) do not
follow the full lifecycle. They:

- Are scoped to a specific workflow run
- Do not carry `lifecycle_status: "published"`
- Are not published to the permanent document set
- May carry `lifecycle_status: "draft"` or omit the field
- Are retained for audit trail but must not be presented as canonical
  authority

### Lifecycle for Human-Authored Documents

Human-authored documents (such as `masterplan/` reference blueprints)
may carry `lifecycle_status` for informational purposes, but their
lifecycle is managed by human maintainers, not by workflow automation.

### Lifecycle Metadata Consistency

All documents in a governed set should carry consistent lifecycle
metadata:

- A document set under active development should show consistent draft
  status across all members
- A published document set should show `lifecycle_status: "published"`
  across all members
- Mixed lifecycle status within a set is a defect requiring correction
