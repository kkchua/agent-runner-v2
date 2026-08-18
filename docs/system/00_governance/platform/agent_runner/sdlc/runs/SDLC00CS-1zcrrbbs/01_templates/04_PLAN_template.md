---
template_id: SYS-03-PL
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for approved Plan documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_codebase_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Plan (PLAN)

## Purpose

This template defines the structure for approved plan documents
(PLAN-DOC). A plan document is produced by the sdlc_30_backlog_v1
workflow from an approved requirement document (REQ-DOC). The PLAN-DOC
defines the implementation approach, architecture decisions, and
high-level work breakdown. It serves as input to sdlc_40_task_v1.

Plan documents are stored in the plans/ directory. Once approved, they
are immutable and form part of the SDLC audit trail.

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
scan_reason: "Approved plan document produced by sdlc_30"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-PL | Fixed identifier for this template |
| version | "1.0.0" | Set by workflow on generation |
| doc_type | workflow_output | Workflow-generated delivery artifact |
| authority | workflow-generated | Produced by sdlc_30 |
| scan_policy | include | Include in operational scans |
| scan_reason | Fixed or contextual | Describe scan inclusion reason |
| managed_by | workflow-generated | Maintained by workflow |
| layer | layer3 | SDLC delivery layer |
| platform | agent-runner-v2 | Platform identifier |
| lifecycle_status | draft or approved | "draft" during workflow; "approved" after promotion |

## Required Content Sections

Instances of this template MUST contain the following sections in the
order shown:

### 1. Title

A clear title for the plan document. Format as a level-1 heading.

### 2. Document Metadata

Structured metadata about the plan document:

- Document ID (e.g., PLAN-20260817-001)
- Source requirement reference (REQ file path)
- Date of generation
- Producing workflow (sdlc_30_backlog_v1)
- Producing agent (AGENT-task-decomposer)

### 3. Implementation Approach

A description of the chosen implementation approach, including:

- Architecture overview.
- Technology choices and rationale.
- Integration points.
- Design patterns to be used.

### 4. Work Breakdown Structure

A hierarchical decomposition of the work into major deliverables and
work packages. Each work package should be identifiable as a future
backlog item.

### 5. Task Decomposition Strategy

Description of how work packages will be further decomposed into
individual tasks during the backlog phase.

### 6. Technical Constraints

Technical constraints that the implementation must respect:

- Platform constraints.
- Performance requirements.
- Security requirements.
- Compatibility requirements.

### 7. Risk Mitigation Plan

For each identified risk from the initiative, describe the mitigation
approach in the implementation.

### 8. Dependencies

Internal and external dependencies that affect the implementation plan.

### 9. Acceptance Criteria Summary

Consolidated acceptance criteria from the requirements document,
organized by work package.

### 10. Critique Resolution

Results from the technical_critique and address_critique steps. Lists
each finding, its severity, and the resolution applied.

### 11. Source Reference

Cross-reference to the source requirement document.

## Content Guidelines

### Tone and Style

- Use technical, precise language.
- Architecture decisions must include rationale.
- Work breakdown must be clear and actionable.

### Length

- Aim for 3-8 pages depending on initiative complexity.
- Technical sections may be longer for complex architectures.

### Completeness

- All required sections MUST be present.
- Every work package must be clearly defined.

### ASCII-Only Requirement

All content MUST use ASCII characters only:

- Use plain hyphens (-) for dashes. Do NOT use em-dashes or en-dashes.
- Use straight quotes (" and ') for quotations. Do NOT use curly quotes.
- Do NOT use any other Unicode characters.

### Plain Text Headings

Section headings MUST use plain text only. Do NOT add backticks, bold,
italics, or other inline formatting to section headings.

## Naming Convention for Instances

Instances of this template MUST follow this naming convention:

```
PLAN-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| PLAN | Fixed prefix |
| YYYYMMDD | Date of creation |
| NN | Two-digit sequence number (01-99) |
| slug | Short hyphenated description of the initiative |

### Example

```
PLAN-20260817-001_add-user-authentication.md
```

### Storage Location

Plan documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/plans/`

## Cross-References

### Related Templates

- **03_REQ_template.md** (SYS-03-RQ): The source requirements from
  which this plan was derived.
- **05_BACKLOG_template.md** (SYS-03-BL): The output produced by sdlc_40
  from this plan document.

### Related Agent Contracts

- AGENT-task-decomposer: Used by sdlc_30 to generate the plan from
  requirements.

### Related Workflows

- **sdlc_30_backlog_v1**: Produces this document from a REQ-DOC.
- **sdlc_40_task_v1**: Consumes this document to produce a BACKLOG-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.
