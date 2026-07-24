---
template_id: SYS-03-BL
version: "1.0.0"
doc_type: "bundle_definition"
authority: "sdlc-owned"
scan_policy: "include"
scan_reason: "SDLC delivery document template for approved Backlog documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "SDLC00SCF-20260722-3a011a52"
---

> Managed by workflow: `sdlc_00_delivery_scaffold_v1` / step: `publish_sdlc_scaffold`
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Backlog (BACKLOG)

## Purpose

This template defines the structure for approved backlog documents
(BACKLOG-DOC). A backlog document is produced by the sdlc_40_task_v1
workflow from an approved plan document (PLAN-DOC). The BACKLOG-DOC
contains the decomposed task list with priorities, estimates, and
assignment guidance. It serves as input to sdlc_50_implementation_v1.

Backlog documents are stored in the backlogs/ directory. Once approved,
they are immutable and form part of the SDLC audit trail.

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
scan_reason: "Approved backlog document produced by sdlc_40"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-BL | Fixed identifier for this template |
| version | "1.0.0" | Set by workflow on generation |
| doc_type | workflow_output | Workflow-generated delivery artifact |
| authority | workflow-generated | Produced by sdlc_40 |
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

A clear title for the backlog document. Format as a level-1 heading.

### 2. Document Metadata

Structured metadata about the backlog document:

- Document ID (e.g., BACKLOG-20260722-001)
- Source plan reference (PLAN file path)
- Date of generation
- Producing workflow (sdlc_40_task_v1)
- Producing agent (AGENT-task-decomposer)

### 3. Backlog Overview

Summary of the backlog contents:

- Total number of tasks.
- Summary of effort estimates.
- High-level ordering rationale.

### 4. Task List

Numbered list of backlog tasks. Each task MUST include:

- Task ID (e.g., BL-001).
- Task title.
- Description of the work to be done.
- Parent work package (from the plan document).
- Priority (critical, high, medium, low).
- Estimated effort (story points or hours).
- Dependencies on other tasks.
- Required skills or expertise.

### 5. Task Ordering

The recommended execution order with justification:

- Sequential dependencies.
- Parallel opportunities.
- Critical path identification.

### 6. Effort Summary

Aggregated effort estimates:

- Total estimated effort.
- Effort breakdown by work package.
- Confidence level for estimates.

### 7. Risk Items

Backlog-specific risks:

- Tasks with high uncertainty.
- Tasks requiring external dependencies.
- Mitigation strategies.

### 8. Source Reference

Cross-reference to the source plan document.

## Content Guidelines

### Tone and Style

- Use action-oriented language for task descriptions.
- Each task should be independently understandable.
- Estimates should include basis for estimation.

### Length

- Aim for 3-10 pages depending on initiative complexity.
- The Task List section will typically be the longest.

### Completeness

- All required sections MUST be present.
- Every task must have an ID, title, description, and estimate.

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
BACKLOG-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| BACKLOG | Fixed prefix |
| YYYYMMDD | Date of creation |
| NN | Two-digit sequence number (01-99) |
| slug | Short hyphenated description of the initiative |

### Example

```
BACKLOG-20260722-001_add-user-authentication.md
```

### Storage Location

Backlog documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/backlogs/`

## Cross-References

### Related Templates

- **04_PLAN_template.md** (SYS-03-PL): The source plan from which this
  backlog was derived.
- **06_TASK_template.md** (SYS-03-TK): The output produced by sdlc_50
  from this backlog document.

### Related Agent Contracts

- AGENT-task-decomposer: Used by sdlc_40 to decompose the plan into
  backlog tasks.

### Related Workflows

- **sdlc_40_task_v1**: Produces this document from a PLAN-DOC.
- **sdlc_50_implementation_v1**: Consumes this document to produce
  TASK-DOC files.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.