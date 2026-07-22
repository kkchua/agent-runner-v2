---
template_id: SYS-AG-DS
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Delivery status lifecycle rules for all SDLC delivery documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_agent_contracts
> This file is workflow-generated and protected from manual edits.

# SDLC Delivery Status Rules v1

## Purpose

This document defines the lifecycle status rules for all delivery
documents produced by the SDLC initiative workflows (sdlc_10 through
sdlc_80). It establishes the state machine, transition rules,
promotion patterns, and audit trail requirements that govern how
delivery documents move from initial creation to approved immutable
records.

## Scope

These rules apply to all delivery document types in the SDLC family:

| Document Type | Prefix | Status Values |
|---|---|---|
| Draft Initiative | DRAFT-INIT | draft (user-authored) |
| Initiative | INIT | draft -> approved |
| Requirement | REQ | draft -> approved |
| Plan | PLAN | draft -> approved |
| Backlog | BACKLOG | draft -> approved |
| Task | TASK | draft -> approved |
| Implementation | IMPL | draft -> approved |
| Validation | VALID | draft -> approved |
| Review | REV | draft -> approved |
| Memory | MEM | draft -> approved |
| Closure | CLOSE | draft -> approved |

These rules do not apply to:

- Layer 1 governance documents (which follow the Layer 1 governance
  lifecycle).
- Layer 2 platform constitution documents (which follow the Layer 2
  lifecycle).
- The sdlc_00_delivery_scaffold_v1 bootstrap workflow (which has its
  own review and promotion process).
- The sdlc_00_codebase_v1 maintenance workflow (which operates
  outside the approval-gate model).

## Lifecycle State Machine

### Status Values

| Status | Meaning |
|---|---|
| draft | Initial document generated. Not yet reviewed or promoted. |
| changes_requested | Review identified fixable defects. Document is being refined. |
| approved | All gates passed. Document is immutable. |

### State Transitions

```
draft --> changes_requested --> draft (refine loop) --> approved
  ^                                                     |
  |                                                     |
  +--- (new generation)                                 v
                                                  (immutable, no
                                                   further changes)
```

### Transition Rules

1. **draft -> changes_requested**: Occurs when the internal review
   step identifies fixable defects. The review agent produces a
   REVIEW_FILE_SUGGESTED with findings, and the document status
   transitions to `changes_requested`.

2. **changes_requested -> draft**: Occurs when the refine step
   addresses the review findings. The document returns to `draft`
   status for re-review.

3. **draft -> approved**: Occurs when the review step passes and
   human approval is granted. The promote action changes the
   frontmatter status from `draft` to `approved`.

4. **No backward transitions from approved**: Once a document reaches
   `approved` status, it is immutable. No workflow may modify its
   content or change its status except through deprecation or
   supersession (which requires a new initiative or formal amendment).

### Refine Loop Rules

1. Each refine loop iteration counts against a maximum budget
   (typically 2 iterations, configurable per workflow).
2. If the budget is exhausted, the workflow fails with a specific
   rejection code (e.g., `PLAN_REFINEMENT_EXHAUSTED`).
3. Non-fixable defects (wrong scope, invalid input, conceptual
   mismatch) must cause immediate workflow failure, not enter the
   refine loop.
4. The refine loop returns the document to `draft` status before
   re-entering the review step.

## Preflight Status Check

### Input Validation Rule

Every SDLC initiative workflow MUST verify before execution that its
predecessor output has `lifecycle_status: "approved"` in its YAML
frontmatter.

```
preflight_status_check:
  artifact: "INPUT_ARTIFACT_KEY"
  required_status: "approved"
```

If the check fails, the workflow MUST report a dependency violation
and terminate without producing output.

### Output Initial Status Rule

Every produced document MUST start with `lifecycle_status: "draft"`
in its YAML frontmatter.

```
produced_document_status:
  artifact: "OUTPUT_ARTIFACT_KEY"
  initial_status: "draft"
```

## Promotion Patterns

SDLC workflows use three promotion patterns to transition documents
from `draft` to `approved`.

### Single Artifact Promotion

Used by: sdlc_10, sdlc_20, sdlc_30, sdlc_40, sdlc_50, sdlc_60,
sdlc_70

```yaml
promote_artifact:
  promotes: "OUTPUT_ARTIFACT_KEY"
```

The frontmatter `lifecycle_status` is changed from `draft` to
`approved` on the same file. No new file is created.

**Properties:**
- One file changes status in place.
- The file path remains the same before and after promotion.
- The audit trail records the status change timestamp and the
  promoting workflow/step.

### Two-File Promotion

Used by: sdlc_10 (only)

```yaml
promote_to_initiative:
  source: "DRAFT_INIT_DOC"
  creates: "INIT_DOC"
  status: "approved"
```

A new file (INIT_DOC) is created from the draft source file
(DRAFT_INIT_DOC). Both files are preserved for audit trail.

**Properties:**
- The source draft file remains unchanged.
- A new approved file is created with a different prefix and path.
- Both files carry cross-references to each other.
- This pattern is used only for the draft-to-initiative transition
  because the DRAFT-INIT is user-authored while the INIT is
  workflow-generated.

### Multi-Artifact Promotion

Used by: sdlc_80 (only)

```yaml
promote_all:
  promotes:
    - "REV_FILE"
    - "MEM_FILE"
    - "CLOSE_FILE"
```

All three output documents are promoted to `approved` simultaneously.

**Properties:**
- All documents must pass review before any are promoted.
- The promotion is atomic: either all three are promoted or none are.
- The audit trail records a single promotion event covering all three
  documents.

## Promotion Pattern by Workflow

| Workflow | Pattern | Documents Promoted |
|---|---|---|
| sdlc_10_requirement_v1 | Two-File | DRAFT_INIT -> INIT |
| sdlc_20_planning_v1 | Single | REQ |
| sdlc_30_backlog_v1 | Single | PLAN |
| sdlc_40_task_v1 | Single | BACKLOG |
| sdlc_50_implementation_v1 | Single | TASK |
| sdlc_60_execution_v1 | Single | IMPL |
| sdlc_70_validation_v1 | Single | VALID |
| sdlc_80_review_v1 | Multi-Artifact | REV + MEM + CLOSE |

## Audit Trail Requirements

### Immutable Audit Trail

The complete set of delivery documents forms an immutable audit trail
from initiative inception through closure. The audit trail has the
following properties:

1. Each document links to its predecessor through frontmatter
   cross-references.
2. Each document records the workflow and step that generated it.
3. Each document records its creation date and approval date.
4. Once approved, no document may be modified.

### Traceability Requirements

Every delivery document MUST include:

1. **Upstream reference**: The document that served as input (e.g.,
   the REQ document references the INIT document that produced it).
2. **Downstream reference**: The document it produced (added when the
   downstream workflow creates its output).
3. **Generation metadata**: The workflow name, step name, and job ID
   that generated the document.
4. **Timestamps**: Creation date and, after promotion, approval date.

### Logging Requirements

Each workflow step that creates or modifies a document MUST log:

1. The step name and workflow identifier.
2. The document file path and its lifecycle status before and after.
3. The timestamp of the operation.
4. The coder role or action that performed the operation.

### Status Change Records

Every status transition MUST be recorded with:

1. Previous status.
2. New status.
3. Timestamp of transition.
4. The workflow step that triggered the transition.
5. Reason for transition (e.g., "review passed", "refine applied",
   "human approved").

## Metadata Frontmatter Rules

### Required Fields for Delivery Documents

Every delivery document instance MUST include these YAML frontmatter
fields:

| Field | Required | Value |
|---|---|---|
| template_id | Yes | SYS-03-XX matching the template |
| version | Yes | Document instance version |
| doc_type | Yes | "workflow_output" |
| authority | Yes | "workflow-generated" |
| scan_policy | Yes | "include" |
| scan_reason | Yes | Describes why scan policy was chosen |
| layer | Yes | "layer3" |
| platform | Yes | "agent-runner-v2" |
| lifecycle_status | Yes | "draft" initially, "approved" after promotion |
| managed_by | Yes | "workflow-generated" |
| initiative_id | Yes | Initiative identifier (e.g., "20260722-001") |
| cross_references | Yes | Links to predecessor/successor documents |

### Frontmatter Immutability After Approval

Once a document carries `lifecycle_status: "approved"`, its frontmatter
is immutable. No field may be changed except through a formal
deprecation or supersession process managed by a new initiative.

## Relationship to Layer 1 Governance Lifecycle

These delivery status rules are a specialized subset of the Layer 1
Governance Lifecycle (GOVERNANCE_LIFECYCLE.md). The Layer 1 lifecycle
defines seven states (draft, review, approved, published, superseded,
deprecated, retired). The SDLC delivery status rules use three states
(draft, changes_requested, approved) because:

1. SDLC delivery documents are not governance documents. They do not
   require publication to a governed active set.
2. The `changes_requested` state replaces the Layer 1 `review` state
   for SDLC purposes, making the refine loop semantics explicit.
3. SDLC delivery documents become immutable upon approval. They do not
   transition through published, superseded, deprecated, or retired
   states within the SDLC pipeline.

If an approved SDLC delivery document needs to be superseded or
deprecated, this must be done through a new initiative or a formal
amendment process outside the standard SDLC pipeline.

## Constraints

1. These rules apply to all SDLC initiative workflows (sdlc_10 through
   sdlc_80).
2. They do not apply to bootstrap or maintenance workflows.
3. They inherit from and must not contradict the Layer 1 Governance
   Lifecycle.
4. They inherit from and must not contradict the Layer 2 platform
   metadata contract.
5. Any deviation from these rules requires explicit review and
   documentation.

## References

- AGENTS.md (this directory) -- Master agent index
- WORKFLOW_SOP_v1.md -- Workflow sequence and naming conventions
- 01_templates/template_registry.md -- Template cross-reference
- Layer 1 Governance Lifecycle: docs/system/00_governance/foundation/current/GOVERNANCE_LIFECYCLE.md
- Layer 1 Metadata Standard: docs/system/00_governance/foundation/current/METADATA_STANDARD.md
- Layer 2 Runtime Model: docs/system/00_governance/platform/agent_runner/current/RUNTIME_MODEL.md
- L3 SDLC Specification: masterplan/LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md

## Version History

| Version | Date | Change Summary |
|---|---|---|
| 1.0.0 | 2026-07-22 | Initial release. Defines delivery status state machine, promotion patterns, and audit trail rules. |
