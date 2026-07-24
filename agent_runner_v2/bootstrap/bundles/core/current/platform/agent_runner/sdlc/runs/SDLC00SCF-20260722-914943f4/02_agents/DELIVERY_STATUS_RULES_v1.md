---
template_id: SYS-AG-DSR
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Lifecycle status rules and approval gate model for all SDLC delivery documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_agent_contracts
> This file is workflow-generated and protected from manual edits.

# SDLC Delivery Status Rules v1

## Purpose

This document defines the authoritative lifecycle status rules, approval
gate model, state machine transitions, promotion patterns, and audit
trail requirements for all Layer 3 SDLC delivery documents on the
agent-runner-v2 platform.

These rules govern every delivery document from creation through
approval and archival. They ensure deterministic state transitions,
explicit approval discipline, and immutable audit trails.

## Scope

This document applies to all delivery documents produced by SDLC
initiative workflows (sdlc_10 through sdlc_80). It does not apply to
maintenance workflows (sdlc_00_codebase_v1) which operate outside the
approval-gate model.

## Core Principles

1. Status is explicit: No hidden or implicit state changes.

2. Approval is centralized: Only human approval advances documents to
   the "approved" state through the runner-owned approval action.

3. Execution does not equal approval: Completed work must still be
   reviewed and approved.

4. Workflow truth is durable: Workflow truth lives in runner state plus
   durable artifacts, not in conversation memory.

5. Rejection stops progression: Rejected artifacts cannot be used for
   downstream execution until the issue is resolved.

6. Authority precedence is explicit: When interpretation conflicts
   occur, precedence is:
   - Layer 1 governance (METADATA_STANDARD.md)
   - Layer 2 platform contract (METADATA_CONTRACT.md)
   - This document (DELIVERY_STATUS_RULES_v1.md)
   - WORKFLOW_SOP_v1.md
   - AGENTS.md
   - Individual agent contract

   Lower-precedence layers may describe but MUST NOT override
   higher-precedence layers.

## Lifecycle Status Values

All delivery documents use the following lifecycle_status values in
their YAML frontmatter:

| Value | Meaning |
|---|---|
| draft | Initial or in-progress content. Not yet reviewed or approved. |
| changes_requested | Review feedback received. Requires refinement before approval. |
| approved | Passed all governance gates and human approval. Ready for downstream use. |

### Additional Values (context-specific)

| Value | Meaning |
|---|---|
| superseded | Replaced by a newer version. Retained for audit trail. Must not be used as execution source. |
| archived | Initiative closed. Document preserved for historical reference. |

## State Machine

### Standard Transition Flow

Every delivery document follows this state machine:

```
draft --> changes_requested --> draft (refine loop)
  |
  v
approved
```

### Transition Details

| From | To | Trigger | Authority |
|---|---|---|---|
| (none) | draft | Document created by agent | Producing agent |
| draft | changes_requested | Review step identifies issues | Reviewer agent |
| changes_requested | draft | Refine step addresses feedback | Producing agent |
| draft | approved | Human approval granted | Human (via runner approval action) |
| approved | superseded | Newer version created | Workflow or human |

### Forbidden Transitions

The following transitions are invalid and MUST be rejected:

- draft --> approved without review and human approval
- changes_requested --> approved without returning to draft first
- approved --> draft (approved documents are immutable)
- Any transition on a superseded document
- Silent overwrite of an approved document

## Preflight Enforcement Rules

These rules apply BEFORE any workflow step executes. The runner MUST
apply all checks in order. If any check fails, the step MUST NOT
execute.

### PREFLIGHT-01: Read lifecycle_status independently

Before executing a step, the runner MUST read the current
lifecycle_status of the target document from the YAML frontmatter. Do
not infer lifecycle_status from job status or any other field.

### PREFLIGHT-02: Verify input document status

Before executing a step, the runner MUST verify that the input document
from the predecessor workflow has lifecycle_status "approved". If not,
the step MUST be rejected.

### PREFLIGHT-03: Validate intended transition

The runner MUST verify that the step is authorized to perform its
intended lifecycle_status transition per this document. If the intended
transition is not listed in the transition table, the step is blocked
and MUST be rejected.

### PREFLIGHT-04: Reject steps targeting approved documents

If lifecycle_status is "approved", the runner MUST reject any step that
attempts to mutate the document. Approved documents are immutable.

## Step-Completion Enforcement Rules

These rules apply AFTER a step completes. The runner MUST apply all
requirements. Skipping any write is a violation.

### COMPLETE-01: Record execution outcome

After the step completes, the runner MUST record the execution outcome.
This is independent of any lifecycle_status update.

### COMPLETE-02: Write lifecycle_status when authorized

If the step is authorized to transition lifecycle_status, and the step
completed successfully, the runner MUST write the new lifecycle_status
value. This write is independent of the execution outcome record.

### COMPLETE-03: No automatic derivation

The runner MUST NOT derive lifecycle_status from execution outcome, or
execution outcome from lifecycle_status. Each is written by its
authorizing process only.

### COMPLETE-04: Record transition evidence

The runner MUST log the lifecycle_status transition with the
authorizing step identity and a timestamp. This log is required for
audit and traceability.

### COMPLETE-05: Do not write unauthorized transitions

If a step completes but is not authorized to perform a lifecycle_status
transition, the runner MUST NOT mutate lifecycle_status.

## Promotion Patterns

After review and human approval, workflows use one of these promotion
patterns to advance documents to "approved" status.

### Single Artifact Promotion

Used by: sdlc_10 through sdlc_70 (most workflows)

```
promote_artifact:
  promotes: "OUTPUT_ARTIFACT_KEY"
```

Changes lifecycle_status from "draft" to "approved" on the same file.
The file content does not change during promotion -- only the frontmatter
status field is updated.

### Two-File Promotion

Used by: sdlc_10 (alternative pattern for draft-to-initiative)

```
promote_to_approved:
  source: "DRAFT_FILE"
  target: "APPROVED_FILE"
  status: "approved"
```

Creates or promotes the target file with approved status. Both the
source and target files are preserved for audit trail.

### Multi-Artifact Promotion

Used by: sdlc_80 only

```
promote_all:
  promotes: ["REV_FILE", "MEM_FILE", "CLOSE_FILE"]
```

Promotes multiple artifacts together after all have been reviewed and
human approval has been granted. All artifacts must reach "approved"
status as a group.

## Promotion Pattern by Workflow

| Workflow | Pattern | Artifacts Promoted |
|---|---|---|
| sdlc_10_requirement_v1 | Single artifact | INIT-DOC |
| sdlc_20_planning_v1 | Single artifact | REQ-DOC |
| sdlc_30_backlog_v1 | Single artifact | PLAN-DOC |
| sdlc_40_task_v1 | Single artifact | BACKLOG-DOC |
| sdlc_50_implementation_v1 | Single artifact | TASK-DOC |
| sdlc_60_execution_v1 | Single artifact | IMPL-DOC |
| sdlc_70_validation_v1 | Single artifact | VALID-DOC |
| sdlc_80_review_v1 | Multi-artifact | REV-DOC + MEM-DOC + CLOSE-DOC |

## Review-Refine Loop Model

### Standard Pattern

Every workflow follows this review-refine pattern before promotion:

1. Agent produces output document with lifecycle_status "draft".
2. Review step assesses the document.
3. If issues are found:
   a. lifecycle_status transitions to "changes_requested".
   b. Refine step addresses the feedback.
   c. lifecycle_status transitions back to "draft".
   d. Return to step 2.
4. If no issues are found:
   a. Human approval is requested.
   b. Upon approval, lifecycle_status transitions to "approved".

### Maximum Iterations

The review-refine loop MUST have a maximum iteration count to prevent
infinite loops. The specific maximum is defined per workflow but
typically should not exceed 3-5 iterations. If the maximum is reached
without approval, the workflow MUST escalate for human intervention.

## Document Immutability After Approval

Once a delivery document has lifecycle_status "approved" in its YAML
frontmatter:

- It CANNOT be modified by any workflow or agent.
- It provides an immutable audit trail.
- Any changes require a new initiative or a formal amendment process.
- The document MAY be superseded by a newer version, but the original
  file is never modified.

## Audit Trail Requirements

### Delivery Document Chain

Every initiative produces a traceable chain of documents:

```
DRAFT-INIT --> INIT --> REQ --> PLAN --> BACKLOG --> TASK --> IMPL --> VALID --> REV + MEM + CLOSE
```

Each document in the chain MUST:
- Reference its predecessor document(s) by filename.
- Preserve the Initiative ID from the chain origin.
- Preserve all upstream IDs (Plan ID, Task ID, etc.) where applicable.
- Have lifecycle_status "approved" before the next document in the
  chain is created.

### Transition Log

Every lifecycle_status transition MUST be recorded with:
- Document filename
- Previous status
- New status
- Authorizing step identity
- Timestamp
- Reason for transition (where applicable)

## Global Workflow Discipline

The following rules apply to all SDLC initiative workflows:

1. No phase skipping: Each workflow must execute in sequence.
2. No out-of-order execution: A workflow cannot start before its
   predecessor has produced an approved output.
3. No use of superseded artifacts: Superseded documents must not be
   used as active execution sources.
4. No downstream execution from rejected artifacts: If a document is
   rejected, no downstream workflow may proceed until the issue is
   resolved.
5. No silent overwrite of approved artifacts: Approved documents are
   immutable.
6. Manual edits alone do not advance workflow: Changing a document's
   frontmatter manually does not constitute a valid state transition.
   State transitions must be performed by the runner.

## Authority Model

### Human (Architect)

- Approves documents for promotion to "approved" status.
- Makes final go/no-go decisions.
- Can request escalation when review loops exceed maximum iterations.

### Producing Agents

- Create documents with lifecycle_status "draft".
- Refine documents when lifecycle_status is "changes_requested".
- Must not self-approve documents.

### Reviewer Agent

- Assesses document quality and correctness.
- Sets lifecycle_status to "changes_requested" when issues are found.
- Does not approve -- only human approval promotes to "approved".

### Runner

- Enforces preflight and step-completion rules.
- Performs lifecycle_status transitions as authorized.
- Records transition evidence for audit.
- Rejects unauthorized transitions.

## Relationship to Layer 1 and Layer 2

This document operates within the Layer 3 SDLC delivery system. It:

- Inherits the lifecycle_status vocabulary from Layer 1
  (METADATA_STANDARD.md) without redefining it.
- Inherits the platform metadata contract from Layer 2
  (METADATA_CONTRACT.md) without redefining it.
- Adds SDLC-specific transition rules and promotion patterns that are
  specific to the Layer 3 delivery workflow.
- Does not override or contradict Layer 1 or Layer 2 rules.

## References

- Agent Registry: AGENTS.md
- Workflow SOP: 01_templates/WORKFLOW_SOP_v1.md
- Layer 1 Metadata Standard: foundation/current/METADATA_STANDARD.md
- Layer 2 Metadata Contract: current/METADATA_CONTRACT.md
- Layer 3 SDLC Specification: masterplan/LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md
