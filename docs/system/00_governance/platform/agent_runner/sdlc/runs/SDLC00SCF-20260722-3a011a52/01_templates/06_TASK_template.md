---
template_id: SYS-03-TK
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for approved Task Specification documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Task Specification (TASK)

## Purpose

This template defines the structure for approved task specification
documents (TASK-DOC). A task specification is produced by the
sdlc_50_implementation_v1 workflow from an approved backlog document
(BACKLOG-DOC). The TASK-DOC provides detailed instructions for a single
task or a small group of related tasks, ready for execution by
sdlc_60_execution_v1.

Task specification documents are stored in the tasks/ directory. Once
approved, they are immutable and form part of the SDLC audit trail.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-TK
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved task specification document produced by sdlc_50"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-TK | Fixed identifier for this template |
| version | "1.0.0" | Set by workflow on generation |
| doc_type | workflow_output | Workflow-generated delivery artifact |
| authority | workflow-generated | Produced by sdlc_50 |
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

A clear title for the task specification. Format as a level-1 heading.

### 2. Document Metadata

Structured metadata about the task specification:

- Document ID (e.g., TASK-20260722-001-01)
- Source backlog reference (BACKLOG file path)
- Task IDs covered from backlog
- Date of generation
- Producing workflow (sdlc_50_implementation_v1)
- Producing agent (AGENT-implementation-planner)

### 3. Task Overview

High-level description of what this task specification covers:

- Which backlog tasks are included.
- Scope of work for this specification.
- Expected outcome.

### 4. Detailed Implementation Steps

Step-by-step instructions for implementing the task. Each step MUST
include:

- Step number.
- Action description.
- Files to create or modify.
- Expected result after the step.

### 5. Technical Specifications

Detailed technical requirements:

- API contracts or interfaces to implement.
- Data structures or schemas.
- Configuration changes.
- Dependencies to install or configure.

### 6. Test Requirements

Test criteria for this task:

- Unit tests to write.
- Integration tests to update.
- Test coverage expectations.
- Edge cases to verify.

### 7. Acceptance Criteria

Specific acceptance criteria inherited from the backlog and requirements,
adapted for this task:

- Functional acceptance criteria.
- Technical acceptance criteria.
- Quality gates.

### 8. Definition of Done

Clear definition of what "done" means for this task:

- Code complete.
- Tests passing.
- Documentation updated.
- Review criteria met.

### 9. Source Reference

Cross-reference to the source backlog document and original requirements.

## Content Guidelines

### Tone and Style

- Use imperative, instruction-style language.
- Steps must be precise enough for an executor to follow without
  ambiguity.
- Include file paths and specific identifiers.

### Length

- Aim for 2-6 pages per task specification.
- Implementation steps should be granular but not excessively verbose.

### Completeness

- All required sections MUST be present.
- Each implementation step must be actionable.

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
TASK-{YYYYMMDD}-{NN}-{TT}_{slug}.md
```

| Component | Description |
|---|---|
| TASK | Fixed prefix |
| YYYYMMDD | Date of creation |
| NN | Two-digit initiative sequence number (01-99) |
| TT | Two-digit task number within initiative (01-99) |
| slug | Short hyphenated description of the initiative |

### Example

```
TASK-20260722-001-01_add-user-authentication.md
```

### Storage Location

Task specification documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/tasks/`

## Cross-References

### Related Templates

- **05_BACKLOG_template.md** (SYS-03-BL): The source backlog from which
  this task specification was derived.
- **07_IMPL_template.md** (SYS-03-IM): The output produced by sdlc_60
  from this task specification.

### Related Agent Contracts

- AGENT-implementation-planner: Used by sdlc_50 to generate task specs
  from backlog items.

### Related Workflows

- **sdlc_50_implementation_v1**: Produces this document from a
  BACKLOG-DOC.
- **sdlc_60_execution_v1**: Consumes this document to produce an
  IMPL-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.
