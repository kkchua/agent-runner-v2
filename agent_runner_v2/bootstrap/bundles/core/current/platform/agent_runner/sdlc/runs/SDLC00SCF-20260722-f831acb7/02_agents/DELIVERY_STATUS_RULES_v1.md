---
template_id: SYS-AG-DS
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Delivery document lifecycle status rules for SDLC agent contracts"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_agent_contracts
> This file is workflow-generated and protected from manual edits.

# SDLC Delivery Status Rules

## Purpose

This document defines the lifecycle status rules for all SDLC delivery
documents produced by agent contracts. It establishes the state machine
that delivery documents follow from creation through approval, the
promotion patterns used by different workflows, and the audit trail
requirements that ensure traceability across the delivery chain.

## Scope

These rules apply to all delivery document instances (INIT, REQ, PLAN,
BACKLOG, TASK, IMPL, VALID, REV, MEM, CLOSE) produced by SDLC initiative
workflows (sdlc_10 through sdlc_80). They do not apply to:

- The DRAFT-INIT document (user-authored, not workflow-generated).
- Agent contract definitions (which carry lifecycle_status: "template").
- Layer 1 or Layer 2 governance documents (which follow their own
  lifecycle rules defined in GOVERNANCE_LIFECYCLE.md).

## Lifecycle States for Delivery Documents

SDLC delivery documents use a simplified subset of the full Layer 1
governance lifecycle. The states and transitions are:

### States

| Status | Meaning |
|---|---|
| draft | Initial document generated. Not yet reviewed. |
| changes_requested | Review identified fixable defects. Document must be refined. |
| approved | All gates passed. Document is immutable. |

### State Machine

```
draft --> changes_requested --> draft (refine loop)
  |                                  |
  |  (approval gate passes)          |
  v                                  |
approved                             |
  |                                  |
  v (immutable -- no further state   |
      transitions allowed)           |
                                     v
                           (if budget exhausted,
                            workflow fails)
```

### State Transitions

| From | To | Trigger |
|---|---|---|
| (none) | draft | Document generation by an agent or workflow |
| draft | changes_requested | Review step identifies fixable defects |
| changes_requested | draft | Refinement step corrects the defects |
| draft | approved | Human approval gate passes |
| approved | (none) | Terminal state. Document is immutable. |

### Invalid Transitions

The following transitions are explicitly forbidden:

- approved -> draft (cannot revert an approved document).
- approved -> changes_requested (cannot request changes on approved).
- changes_requested -> approved (must return to draft first).
- draft -> draft (a new generation replaces, does not transition).

## Promotion Patterns

SDLC workflows use three distinct promotion patterns depending on the
number and relationship of output documents.

### Single Artifact Promotion

Used by: sdlc_20, sdlc_30, sdlc_40, sdlc_50, sdlc_60, sdlc_70

The workflow produces a single output document. The promotion action
changes lifecycle_status from "draft" to "approved" on the same file.

```
<DOC>-{date}-{NN}_{slug}.md
  lifecycle_status: "draft"  -->  lifecycle_status: "approved"
```

Rules:
- The file path does not change.
- Only the frontmatter lifecycle_status field changes.
- No other content modifications are permitted during promotion.

### Two-File Promotion

Used by: sdlc_10_requirement_v1

The workflow creates a new document (INIT-DOC) from a draft input
(DRAFT-INIT-DOC). Both files are preserved for audit trail. The new
file follows standard single artifact promotion for its own lifecycle.

```
DRAFT-INIT-{date}-{NN}_{slug}.md  (user-authored, not promoted)
         |
         v  sdlc_10 generates
INIT-{date}-{NN}_{slug}.md  (lifecycle: draft -> approved)
```

Rules:
- The DRAFT-INIT file is not modified by the workflow.
- The INIT file is a new document with its own lifecycle.
- Both files are retained in the audit trail.

### Multi-Artifact Promotion

Used by: sdlc_80_review_v1

The workflow produces three output documents (REV-DOC, MEM-DOC,
CLOSE-DOC). All three are promoted to "approved" simultaneously as
a single atomic promotion action.

```
REV-{date}-{NN}_{slug}.md    lifecycle: "draft" -> "approved"
MEM-{date}-{NN}_{slug}.md    lifecycle: "draft" -> "approved"
CLOSE-{date}-{NN}_{slug}.md  lifecycle: "draft" -> "approved"
```

Rules:
- All three documents must be in "draft" status before promotion.
- Promotion is atomic: either all three are promoted or none are.
- If any document fails validation, the entire promotion is blocked.
- All three documents share the same initiative slug and date.

## Refine Loop Rules

### Trigger Conditions

The refine loop is triggered when:

1. The review step identifies fixable defects in a draft document.
2. The document status is set to "changes_requested".
3. The workflow enters the refine step.

### Refine Loop Cycle

Each refine loop cycle follows this pattern:

1. Document is in "changes_requested" status.
2. Refine step processes the review findings.
3. Document content is corrected.
4. Document status returns to "draft".
5. Document re-enters the review step.

### Budget Constraints

- Maximum refine loop iterations: 3 (configurable per workflow).
- Each iteration counts against the budget.
- After exhausting the budget, the workflow fails and must be restarted.
- The iteration counter resets for each new workflow run.

### Non-Fixable Defects

The following defects are NOT eligible for refinement and must cause
immediate workflow failure:

- Wrong scope (document addresses a different initiative).
- Invalid input (source document is not approved or is malformed).
- Missing critical sections that indicate generation failure.
- Layer boundary violations (document contains governance content).

## Audit Trail Requirements

### Document Chain Traceability

Every delivery document MUST include cross-references that establish
traceability through the delivery chain:

| Document | Must Reference |
|---|---|
| INIT-DOC | Source DRAFT-INIT |
| REQ-DOC | Source INIT-DOC |
| PLAN-DOC | Source REQ-DOC |
| BACKLOG-DOC | Source PLAN-DOC |
| TASK-DOC | Source BACKLOG-DOC |
| IMPL-DOC | Source TASK-DOC |
| VALID-DOC | Source IMPL-DOC, reference TASK-DOC and REQ-DOC |
| REV-DOC | Source VALID-DOC |
| MEM-DOC | Source VALID-DOC, REV-DOC |
| CLOSE-DOC | Source VALID-DOC, REV-DOC, MEM-DOC |

### Frontmatter Audit Fields

Every delivery document MUST include these frontmatter fields for
audit trail purposes:

| Field | Purpose |
|---|---|
| template_id | Identifies the template that governs this document |
| version | Document version at generation time |
| lifecycle_status | Current lifecycle state |
| managed_by | Identifies the workflow that manages this document |
| layer | Must be "layer3" for all SDLC delivery documents |
| platform | Must be "agent-runner-v2" |

### Immutability After Approval

Once a delivery document reaches "approved" status:

- The file content MUST NOT be modified.
- The frontmatter MUST NOT be changed (except by deprecation or
  supersession processes governed by Layer 1).
- The file serves as an immutable audit trail record.
- Any required changes must go through a new initiative or formal
  amendment process.

### Logging Requirements

Each workflow step that creates or modifies a document MUST log:

- The step name and workflow ID.
- The document file path.
- The lifecycle status before and after the operation.
- The timestamp of the operation.
- The agent or action that performed the operation.

## Status Validation Rules

### Pre-Promotion Checks

Before promoting any document to "approved", the workflow MUST verify:

1. The document is currently in "draft" status.
2. All required frontmatter fields are present and valid.
3. All required content sections are present and non-empty.
4. The document uses ASCII-only characters.
5. The file name matches the required naming convention.
6. The file is stored in the correct directory.
7. All cross-references to source documents are present.
8. The document has passed the review step (no outstanding findings).

### Post-Promotion Verification

After promotion to "approved", the workflow MUST verify:

1. The lifecycle_status field is "approved" in the file.
2. No other content has been modified during promotion.
3. The file is accessible and readable.
4. The promotion is recorded in the workflow log.

## Error Handling

### Validation Failures

If a document fails validation during promotion:

1. The promotion is blocked.
2. The document remains in "draft" status.
3. The specific validation failure is logged.
4. The workflow enters the refine loop if defects are fixable.
5. The workflow fails if defects are not fixable or budget is exhausted.

### Promotion Failures

If the promotion action itself fails:

1. The document status is verified to ensure it was not partially updated.
2. If partial update occurred, the workflow attempts rollback.
3. If rollback fails, the workflow fails and escalates.
4. The failure is logged with full context.

## Agent Contract Interaction

Each agent contract produces documents with lifecycle_status: "draft".
The agents do not perform promotion. Promotion is handled by the
workflow's promote step (an action step, not a prompt step).

The refine loop operates as follows:

1. Agent generates document (status: "draft").
2. Review step evaluates the document.
3. If fixable defects: status -> "changes_requested", then refine step
   invokes the agent again (status -> "draft" after refinement).
4. If no defects: promote step changes status to "approved".
5. If non-fixable defects: workflow fails immediately.

## Related Documents

- Agent Index: AGENTS.md (this directory)
- Layer 1 Governance Lifecycle: GOVERNANCE_LIFECYCLE.md (foundation/current/)
- Workflow SOP: 01_templates/WORKFLOW_SOP_v1.md
- Template Registry: 01_templates/template_registry.md
- Layer 2 Metadata Contract: METADATA_CONTRACT.md (platform/current/)
