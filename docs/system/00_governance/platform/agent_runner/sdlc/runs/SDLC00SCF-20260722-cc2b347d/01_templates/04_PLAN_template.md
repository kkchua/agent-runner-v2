---
template_id: SYS-03-PL
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for Plan documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Plan Document (PLAN-DOC)

## Purpose

This template defines the structure for approved plan documents
produced by the sdlc_30_backlog_v1 workflow. A plan document (PLAN-DOC)
transforms the approved requirements (REQ-DOC) into a structured,
execution-oriented plan that defines the approach, architecture, and
work breakdown for the initiative.

The PLAN-DOC is the third formal artifact in the SDLC delivery chain. It
represents the bridge between what needs to be built (requirements) and
how it will be built (tasks).

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-PL
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved plan document in SDLC delivery chain"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft" | "approved"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-PL | Fixed identifier for this template |
| version | Auto-assigned | Set by sdlc_30 workflow |
| doc_type | workflow_output | Generated workflow output |
| authority | workflow-generated | Produced by sdlc_30 workflow |
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

The workflow MUST add `source_document` referencing the requirements doc:

```
source_document: "REQ-{YYYYMMDD}-{NN}_{slug}.md"
```

## Required Content Sections

Instances of this template MUST contain the following sections in the
order shown:

### 1. Title

A clear title that identifies this plan document. Should reference the
initiative and be consistent with prior documents.

### 2. Plan Overview

A summary of the plan, including the approach taken and key decisions
made during planning. This section establishes context for the detailed
plan sections that follow.

### 3. Technical Approach

A description of the technical approach:

- **Architecture Overview**: High-level architecture decisions and
  rationale.
- **Technology Stack**: Key technologies, frameworks, and tools.
- **Design Patterns**: Design patterns or architectural styles to be
  used.
- **Key Design Decisions**: Significant design choices and their
  trade-offs.

### 4. Work Breakdown Structure

A hierarchical breakdown of the work required. Each work item should
include:

- **Work Item ID**: Unique identifier (WBS-001, WBS-002, etc.).
- **Description**: What work is to be performed.
- **Estimated Effort**: Person-hours or story points.
- **Dependencies**: Prerequisite work items.
- **Related Requirements**: Links to REQ-DOC requirement IDs.

### 5. Phases and Milestones

A timeline of phases and milestones:

- **Phase 1**: Description, duration, deliverables.
- **Phase 2**: Description, duration, deliverables.
- **Milestones**: Key checkpoints with completion criteria.

### 6. Resource Plan

Resource allocation for the initiative:

- **Roles Required**: Skills and expertise needed.
- **Team Allocation**: Who is assigned to which work items.
- **External Resources**: Third-party or specialized resources needed.

### 7. Risk Assessment

Identified risks and mitigation strategies:

| Risk ID | Description | Probability | Impact | Mitigation |
|---|---|---|---|---|
| RISK-001 | Description | High/Med/Low | High/Med/Low | Mitigation plan |

### 8. Dependencies and Assumptions

External dependencies and planning assumptions:

- Dependencies on other initiatives or external systems.
- Assumptions made during planning.
- Constraints that affect the plan.

### 9. Delivery Timeline

A summary timeline showing key dates:

- **Start Date**: Planned start.
- **Key Milestones**: Dates for each milestone.
- **Completion Date**: Planned completion.

## Content Guidelines

### Level of Detail

The plan should be detailed enough to enable task decomposition but
not so detailed that it becomes a task specification. Each work item
should be estimable (1-5 days of effort recommended).

### Traceability

Every work item should be traceable to one or more requirements from
REQ-DOC. This ensures that all requirements are addressed in the plan.

### Feasibility

The plan must be achievable within the constraints defined in INIT-DOC.
If timeline or resource constraints are violated, the plan should
document the gap and propose adjustments.

### ASCII-Only Requirement

All content MUST use ASCII characters only.

### Plain Text Headings

Section headings MUST use plain text only.

## Naming Convention for Instances

```
PLAN-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| PLAN | Fixed prefix |
| YYYYMMDD | Date of plan approval |
| NN | Two-digit sequence number |
| slug | Short hyphenated description (same as initiative) |

### Example

```
PLAN-20260722-001_add-user-authentication.md
```

### Storage Location

Plans are stored in:
`docs/repo/agent_runner/sdlc/delivery/plans/`

## Cross-References

### Related Templates

- **03_REQ_template.md** (SYS-03-RQ): Input document.
- **05_BACKLOG_template.md** (SYS-03-BL): Next document in chain.

### Related Agent Contracts

- AGENT-task-decomposer: Used by sdlc_30 to generate the plan from
  requirements.

### Related Workflows

- **sdlc_30_backlog_v1**: Produces this document.
- **sdlc_40_task_v1**: Consumes this document (must be approved).

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields.
- GOVERNANCE_LIFECYCLE.md: Lifecycle state transition rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform metadata extensions.
- VALIDATION_CONTRACT.md: Document validation patterns.
