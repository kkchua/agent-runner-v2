---
template_id: "SYS-00-GL"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "authoritative governance lifecycle standard for the ecosystem"
layer: "layer1"
lifecycle_status: "draft"
effective_version: "01GF-20260719-61ae0105"
managed_by: "workflow-generated"
---

> Managed by workflow: `01_governance_foundation_v1` / step: `refine_governance_foundation_docs`
> This file is workflow-generated and protected from manual edits.

# Governance Lifecycle Standard

## Purpose

This standard defines the lifecycle expectations for governed documents
across Layer 1, Layer 2, and Layer 3. It establishes consistent states,
transitions, and rules for creation, review, approval, publication,
revision, deprecation, and retirement.

## Scope

This standard applies to permanent governed documents at all three layers.
Temporary evidence artifacts (review, validation, audit) are not governed
by this lifecycle; they are run-scoped and do not participate in
publication or promotion.

## Lifecycle States

Every permanent governed document exists in exactly one of these states:

| State | Meaning |
|---|---|
| `draft` | The document has been generated but not yet reviewed or approved. |
| `reviewed` | The document has passed review but has not been approved. |
| `approved` | The document has passed review and validation and is accepted as correct. |
| `published` | The document is the active canonical version for its scope. |
| `superseded` | The document has been replaced by a newer version. |
| `deprecated` | The document is no longer recommended for use but remains available for reference. |
| `retired` | The document has been formally withdrawn and should not be relied upon. |

## State Transitions

### Allowed Transitions

```
draft --> reviewed --> approved --> published
  |                                    |
  |                                    v
  +--> deprecated ------------> superseded
  |                                    |
  +--> retired                <--------+
```

- `draft` may transition to `reviewed`, `deprecated`, or `retired`.
- `reviewed` may transition to `approved`, `deprecated`, or `retired`.
- `approved` may transition to `published`, `deprecated`, or `retired`.
- `published` may transition to `superseded`, `deprecated`, or `retired`.
- `superseded` may transition to `retired`.
- `deprecated` may transition to `retired`.
- `retired` is a terminal state.

### Forbidden Transitions

- No state may transition backward to `draft`.
- `published` may not transition directly back to `approved` without
  creating a new version.
- `superseded` may not transition back to `published`.
- `retired` may not transition to any other state.

## Creation

Creation is the act of generating a new governed document.

Rules:

1. A new document enters the lifecycle in `draft` state.
2. The `lifecycle_status` frontmatter field must be set to `draft`.
3. The `effective_version` field must identify the run or change that
   produced the draft.
4. Creation does not imply approval or publication.

## Review

Review is the act of evaluating a document for scope, correctness, and
layer-boundary compliance.

Rules:

1. A document in `draft` state may be submitted for review.
2. Review must evaluate content against the layer's scope rules.
3. Review produces a `review_artifact` with explicit pass/reject findings.
4. A passing review allows transition to `reviewed` state.
5. A failing review routes to refinement or rejection.

Review must reject if:

- the document contains content that belongs in a different layer
- the document claims authority above its actual scope
- required sections are missing
- metadata classification is inconsistent with content

## Approval

Approval is the act of accepting a document as correct and complete for
its intended scope.

Rules:

1. A document must be in `reviewed` state before approval.
2. Approval may require human confirmation for governance-sensitive
   documents.
3. Approval transitions the document to `approved` state.
4. Approval does not yet make the document the active canonical version.

## Publication Rule

Approval and publication are distinct acts:

- **Approval** confirms the document is correct.
- **Publication** activates the document as the canonical version for its
  scope.

Rules:

1. A document must be `approved` before it can be published.
2. Publication transitions the document to `published` state.
3. Publication must record the change in a publish manifest.
4. Publication must supersede any prior active version of the same
   document.
5. Prior versions transition to `superseded` state upon publication of a
  successor.

## Revision

Revision is the act of updating a governed document.

Rules:

1. A new version of a `published` document starts in `draft` state.
2. The new version follows the full lifecycle: draft, review, approval,
   publication.
3. The existing `published` version remains active until the new version
   is published.
4. Upon publication of the new version, the prior version transitions to
   `superseded`.

## Deprecation

Deprecation is the act of signaling that a document is no longer
recommended.

Rules:

1. Any non-terminal state may transition to `deprecated`.
2. Deprecation must include a reason and, where applicable, a pointer to
   the replacement document.
3. Deprecated documents remain available for reference but should not be
   used as active authority.
4. Deprecated documents may later transition to `retired`.

## Retirement

Retirement is the formal withdrawal of a document.

Rules:

1. Retirement is a terminal state.
2. A retired document should not be relied upon for any governance
   decision.
3. Retirement must be recorded and communicated.
4. Retired documents may be archived but should not be presented as
   active authority.

## Promotion And Lifecycle Interaction

Lifecycle states do not automatically confer higher-layer authority.

Rules:

1. A `published` Layer 3 document does not become Layer 2 authority.
2. A `published` Layer 2 document does not become Layer 1 governance.
3. Cross-layer promotion requires explicit reclassification under the
   target layer's metadata rules, review against the target layer scope,
   and acceptance by the owning authority of the target layer.
4. Promotion creates a new document in the target layer's lifecycle,
   starting at `draft`.

## Lifecycle State in Frontmatter

Every permanent governed document must declare its lifecycle state in
frontmatter:

```yaml
lifecycle_status: "draft" | "reviewed" | "approved" | "published" |
                  "superseded" | "deprecated" | "retired"
```

Temporary evidence artifacts may omit this field or use `draft` for
tracking purposes, but they are not governed by this lifecycle.

## Version Tracking

Each governed document should carry:

- `effective_version`: identifies the run, change, or version that
  produced this state
- `lifecycle_status`: current lifecycle state
- `version`: semantic version of the document content

The publish manifest provides the machine-readable record of which
version is currently `published` and which versions have been
`superseded`.

## Cross-Layer Consistency

All three layers share this lifecycle model:

- Layer 1 governance standards follow this lifecycle.
- Layer 2 platform standards follow this lifecycle.
- Layer 3 bundle definitions and workflow outputs follow this lifecycle.

Each layer may add layer-specific transition rules, but no layer may
remove or redefine the core states or the publication/approval
distinction.