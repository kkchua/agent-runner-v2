---
template_id: SYS-03-BL
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for Backlog documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Backlog Document (BACKLOG-DOC)

## Purpose

This template defines the structure for approved backlog documents
produced by the sdlc_40_task_v1 workflow. A backlog document
(BACKLOG-DOC) transforms the approved plan (PLAN-DOC) into an ordered,
prioritized backlog of work items ready for task specification.

The BACKLOG-DOC is the fourth formal artifact in the SDLC delivery chain.
It represents the prioritized inventory of work that needs to be
completed, organized for efficient task decomposition and execution.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-BL
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved backlog document in SDLC delivery chain"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft" | "approved"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-BL | Fixed identifier for this template |
| version | Auto-assigned | Set by sdlc_40 workflow |
| doc_type | workflow_output | Generated workflow output |
| authority | workflow-generated | Produced by sdlc_40 workflow |
| scan_policy | include | Permanent delivery document |
| scan_reason | Auto-assigned | Describe purpose for scanning |
| managed_by | workflow-generated | Workflow-generated document |
| layer | layer3 | SDLC delivery layer |
| platform | agent-runner-v2 | Platform identifier |
| lifecycle_status | draft/approved | "draft" during generation, "approved" after gate |

### Additional Field: effective_version

The workflow MUST add `effective_version` when promoting to `approved`:

```
effective_version: "<workflow-run-id>"
```

### Additional Field: source_document

The workflow MUST add `source_document` referencing the plan document:

```
source_document: "PLAN-{YYYYMMDD}-{NN}_{slug}.md"
```

## Required Content Sections

Instances of this template MUST contain the following sections in the
order shown:

### 1. Title

A clear title that identifies this backlog document. Should reference the
initiative and be consistent with prior documents.

### 2. Backlog Overview

A summary of the backlog, including the total number of items, priority
distribution, and relationship to the plan.

### 3. Prioritized Backlog Items

An ordered list of backlog items. Each item MUST include:

- **Backlog Item ID**: Unique identifier (BL-001, BL-002, etc.).
- **Title**: Short descriptive title.
- **Description**: What work is to be done.
- **Priority**: Critical, High, Medium, Low.
- **Estimated Effort**: Person-hours or story points.
- **Dependencies**: Prerequisite items or external factors.
- **Related Requirements**: Links to REQ-DOC requirement IDs.
- **Related Plan Items**: Links to PLAN-DOC work item IDs.

### 4. Item Dependencies

A dependency map showing relationships between backlog items:

| Item | Depends On | Required By | Notes |
|---|---|---|---|
| BL-002 | BL-001 | -- | Must complete BL-001 first |
| BL-003 | BL-001, BL-002 | -- | Requires both predecessors |

### 5. Priority Rationale

Explanation of prioritization decisions:

- Factors that influenced priority ordering.
- Business value considerations.
- Technical dependencies driving order.
- Risk reduction rationale.

### 6. Acceptance Criteria

High-level acceptance criteria for the overall backlog:

- Definition of Done for backlog items.
- Quality gates that items must pass.
- Review and approval expectations.

### 7. Estimates Summary

A summary of effort estimates:

- **Total Estimated Effort**: Sum of all item estimates.
- **Effort Distribution**: By priority level.
- **Confidence Level**: How reliable the estimates are.

### 8. Notes (Optional)

Any additional context, assumptions, or notes about the backlog.

## Content Guidelines

### Granularity

Backlog items should be small enough to be completed in a single task
iteration (typically 1-3 days of work). Items larger than this should
be broken down further.

### Prioritization

Priority should reflect:

- **Critical**: Blockers that prevent other work.
- **High**: Important features with clear business value.
- **Medium**: Desirable functionality, not time-sensitive.
- **Low**: Nice-to-have, can be deferred.

### Independence

Backlog items should be as independent as possible. Minimize
dependencies between items to allow parallel execution and flexible
ordering.

### ASCII-Only Requirement

All content MUST use ASCII characters only.

### Plain Text Headings

Section headings MUST use plain text only.

## Naming Convention for Instances

```
BACKLOG-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| BACKLOG | Fixed prefix |
| YYYYMMDD | Date of backlog approval |
| NN | Two-digit sequence number |
| slug | Short hyphenated description (same as initiative) |

### Example

```
BACKLOG-20260722-001_add-user-authentication.md
```

### Storage Location

Backlogs are stored in:
`docs/repo/agent_runner/sdlc/delivery/backlogs/`

## Cross-References

### Related Templates

- **04_PLAN_template.md** (SYS-03-PL): Input document.
- **06_TASK_template.md** (SYS-03-TK): Next document in chain.

### Related Agent Contracts

- AGENT-task-decomposer: Used by sdlc_40 to generate the backlog from
  the plan.

### Related Workflows

- **sdlc_40_task_v1**: Produces this document.
- **sdlc_50_implementation_v1**: Consumes this document (must be
  approved).

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields.
- GOVERNANCE_LIFECYCLE.md: Lifecycle state transition rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform metadata extensions.
- VALIDATION_CONTRACT.md: Document validation patterns.
