---
template_id: SYS-03-SO
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Standard operating procedure for SDLC delivery system workflow sequence, approval gates, naming conventions, and audit trail rules"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Workflow Standard Operating Procedure

## Purpose

This document defines the standard operating procedure (SOP) for all
Layer 3 AI-Driven SDLC workflow bundles running on the agent-runner-v2
platform. It establishes the workflow sequence, approval gate model,
naming conventions, artifact rules, and audit trail requirements that
every SDLC workflow must follow.

## Scope

This SOP applies to all initiative workflows in the SDLC family:
sdlc_10_requirement_v1 through sdlc_80_review_v1. It does not apply to
sdlc_00_delivery_scaffold_v1 or sdlc_00_codebase_v1, which are bootstrap
and maintenance workflows with their own operating rules.

## Workflow Sequence

### Mandatory Order

SDLC initiative workflows MUST execute in the following order. Each
workflow depends on the previous workflow's approved output:

1. sdlc_10_requirement_v1 (INIT from DRAFT-INIT)
2. sdlc_20_planning_v1 (REQ from INIT)
3. sdlc_30_backlog_v1 (PLAN from REQ)
4. sdlc_40_task_v1 (BACKLOG from PLAN)
5. sdlc_50_implementation_v1 (TASK from BACKLOG)
6. sdlc_60_execution_v1 (IMPL from TASK)
7. sdlc_70_validation_v1 (VALID from IMPL)
8. sdlc_80_review_v1 (REV + MEM + CLOSE from VALID)

### Sequence Enforcement

Each workflow MUST verify before execution that its predecessor output
has `lifecycle_status: "approved"` in its YAML frontmatter. If the
required status is not met, the workflow MUST fail and report the
dependency violation.

### Workflow Steps Pattern

Every SDLC workflow follows this general step pattern:

1. **generate_<artifact>** (prompt) -- Generate the document from input
2. **review_<artifact>** (prompt) -- Internal review of the document
3. **refine_<artifact>** (prompt, conditional) -- Refine based on review
4. **promote_<artifact>** (action) -- Promote document to approved status
5. **step_completion** (action) -- Finalize and notify

## Approval Gate Model

### Standard Approval Gate

Each initiative workflow (sdlc_10 through sdlc_80) has a human approval
gate that controls whether the output document transitions from `draft`
to `approved` lifecycle status.

### Lifecycle States

Delivery documents follow these lifecycle states during a workflow run:

```
draft -> changes_requested -> draft (refine loop) -> approved
```

### Lifecycle Status Values

| Status | Meaning |
|---|---|
| draft | Initial document generated. Not yet reviewed. |
| changes_requested | Review identified fixable defects. |
| approved | All gates passed. Document is immutable. |

### Promotion Rules

1. A document MUST be in `draft` status to enter review.
2. A document MUST pass human approval to reach `approved`.
3. An `approved` document is immutable and MUST NOT be modified by any
   subsequent workflow.
4. Any changes to an approved document require a new initiative or a
   formal amendment process.

### Refine Loop Rules

1. If review identifies fixable defects, status returns to `draft` for
   refinement.
2. The refine loop has a maximum iteration budget (typically 3).
3. After exhausting the budget, the workflow fails and must be restarted.
4. Defects that are not fixable through refinement (e.g., wrong scope,
   invalid input) MUST cause immediate workflow failure.

## Naming Conventions

### Document File Names

All delivery documents MUST follow this naming convention:

```
<PREFIX>-{YYYYMMDD}-{NN}[-{TT}]_{slug}.md
```

| Component | Description |
|---|---|
| PREFIX | Document type prefix (see table below) |
| YYYYMMDD | Date of creation |
| NN | Two-digit initiative sequence number (01-99) |
| TT | Two-digit task number within initiative (01-99, optional) |
| slug | Short hyphenated description of the initiative |

### Prefix Table

| Document Type | Prefix | Example |
|---|---|---|
| Draft Initiative | DRAFT-INIT | DRAFT-INIT-20260722-001_add-auth-feature.md |
| Initiative | INIT | INIT-20260722-001_add-auth-feature.md |
| Requirement | REQ | REQ-20260722-001_add-auth-feature.md |
| Plan | PLAN | PLAN-20260722-001_add-auth-feature.md |
| Backlog | BACKLOG | BACKLOG-20260722-001_add-auth-feature.md |
| Task | TASK | TASK-20260722-001-01_add-auth-feature.md |
| Implementation | IMPL | IMPL-20260722-001-01_add-auth-feature.md |
| Validation | VALID | VALID-20260722-001_add-auth-feature.md |
| Review | REV | REV-20260722-001_add-auth-feature.md |
| Memory | MEM | MEM-20260722-001_add-auth-feature.md |
| Closure | CLOSE | CLOSE-20260722-001_add-auth-feature.md |

### Slug Rules

- Must be lowercase ASCII letters and hyphens only.
- Must be a short (3-10 word) description of the initiative.
- Must be consistent across all documents for the same initiative.
- Must use hyphens, not underscores, to separate words.
- Must not contain special characters, spaces, or Unicode.

## Artifact Rules

### Storage Locations

Delivery documents are stored under:
`docs/repo/agent_runner/sdlc/delivery/`

| Document Type | Subdirectory |
|---|---|
| Draft initiatives | draft_initiatives/ |
| Initiatives | initiatives/ |
| Requirements | requirements/ |
| Plans | plans/ |
| Backlogs | backlogs/ |
| Tasks | tasks/ |
| Implementations | implementations/ |
| Validations | validations/ |
| Reviews, Memory, Closure | reviews/ |

### Artifact Immutability

Once a delivery document carries `lifecycle_status: "approved"` in its
frontmatter, it is immutable:

- No workflow may modify the document content.
- No workflow may change its frontmatter status except through the
  deprecation or supersession process.
- The document serves as an immutable audit trail record.

### Artifact Promotion Patterns

SDLC workflows use three promotion patterns:

1. **Single Artifact Promotion** (most workflows): Change `lifecycle_status`
   from `draft` to `approved` on the same file.

2. **Two-File Promotion** (sdlc_10 only): Create a new file (INIT-DOC) from
   the draft file (DRAFT-INIT-DOC). Both files are preserved for audit
   trail.

3. **Multi-Artifact Promotion** (sdlc_80 only): Promote all three output
   documents (REV, MEM, CLOSE) to `approved` simultaneously.

### Artifact Validation

Every output document MUST pass these validation checks before promotion:

1. YAML frontmatter has all required fields with valid values.
2. Document content has all required sections as defined by the template.
3. Document uses ASCII-only characters.
4. Naming convention matches the required pattern.
5. Storage location matches the required subdirectory.

## Audit Trail Rules

### Immutable Audit Trail

The complete set of delivery documents forms an immutable audit trail
from initiative inception through closure. Each document links to its
predecessor and successor documents through its frontmatter and content
cross-references.

### Audit Trail Traceability

Every document MUST include:

- Reference to the input document that produced it (via cross_references).
- Reference to the output document it produced (via cross_references).
- The workflow and step that generated it (via managed_by or generation
  metadata).
- The date of generation or approval.

### Logging

Each workflow step that creates or modifies a document MUST log:

- The step name and workflow ID.
- The document file path and its lifecycle status before and after.
- The timestamp of the operation.
- The coder or action that performed the operation.

## Metadata Requirements

### Frontmatter Fields

Every delivery document instance MUST include the following YAML
frontmatter fields, as inherited from Layer 1 and Layer 2:

| Field | Required | Value / Guidance |
|---|---|---|
| template_id | Yes | SYS-03-XX identifier matching the template |
| version | Yes | Document instance version (e.g., "1.0.0") |
| doc_type | Yes | Must be "workflow_output" for delivery docs |
| authority | Yes | Must be "workflow-generated" for generated docs |
| scan_policy | Yes | Must be "include" for permanent delivery docs |
| scan_reason | Yes | Must describe why scan policy was chosen |
| layer | Yes | Must be "layer3" for SDLC delivery docs |
| platform | Yes | Must be "agent-runner-v2" |
| lifecycle_status | Yes | "draft" or "approved" depending on state |
| managed_by | Conditional | Required for workflow-generated docs |

### Template ID Mapping

| Template | Template ID |
|---|---|
| 01_DRAFT_INIT_template.md | SYS-03-DI |
| 02_INIT_template.md | SYS-03-IN |
| 03_REQ_template.md | SYS-03-RQ |
| 04_PLAN_template.md | SYS-03-PL |
| 05_BACKLOG_template.md | SYS-03-BL |
| 06_TASK_template.md | SYS-03-TK |
| 07_IMPL_template.md | SYS-03-IM |
| 08_VALID_template.md | SYS-03-VL |
| 09_REV_template.md | SYS-03-RV |
| 10_MEM_template.md | SYS-03-MM |
| 11_CLOSE_template.md | SYS-03-CL |

## Error Handling

### Validation Failures

If a generated document fails validation:

1. Log the specific validation failure.
2. Return to the refine loop for correction.
3. If max iterations exceeded, fail the workflow.

### Review Rejections

If a human reviewer rejects the document:

1. Capture the rejection reason and specific feedback.
2. Return to draft status for refinement.
3. After refinement, re-enter review.
4. If max iterations exceeded, fail the workflow.

### Coder Failures

If a coder (AI backend) fails to generate a valid response:

1. Retry with the same coder once.
2. If the second attempt fails, try an alternative coder backend.
3. If all coders fail, fail the workflow and escalate.

## Related Documents

- SDLC Template Registry: template_registry.md (this directory)
- Agent Contract Definitions: 02_agents/ (separate directory)
- Layer 2 Platform Constitution: PLATFORM_RUNTIME_ROOT (inherited)
- Layer 1 Governance: GOVERNANCE_RUNTIME_ROOT (inherited)
- Delivery Status Rules: 02_agents/DELIVERY_STATUS_RULES_v1.md
