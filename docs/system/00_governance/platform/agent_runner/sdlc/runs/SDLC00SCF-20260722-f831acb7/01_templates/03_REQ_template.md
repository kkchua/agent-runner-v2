---
template_id: SYS-03-RQ
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for approved Requirement documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Requirement (REQ)

## Purpose

This template defines the structure for approved requirement documents
(REQ-DOC). A requirement document is produced by the
sdlc_20_planning_v1 workflow from an approved initiative document
(INIT-DOC). The REQ-DOC details the functional and non-functional
requirements for the initiative and serves as input to
sdlc_30_backlog_v1.

Requirement documents are stored in the requirements/ directory. Once
approved, they are immutable and form part of the SDLC audit trail.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-RQ
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved requirement document produced by sdlc_20"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-RQ | Fixed identifier for this template |
| version | "1.0.0" | Set by workflow on generation |
| doc_type | workflow_output | Workflow-generated delivery artifact |
| authority | workflow-generated | Produced by sdlc_20 |
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

A clear title for the requirements document. Format as a level-1
heading.

### 2. Document Metadata

Structured metadata about the requirements document:

- Document ID (e.g., REQ-20260722-001)
- Source initiative reference (INIT file path)
- Date of generation
- Producing workflow (sdlc_20_planning_v1)
- Producing agent (AGENT-planner)

### 3. Requirements Overview

A summary of the requirements, linking back to the initiative
objectives.

### 4. Functional Requirements

Numbered list of functional requirements. Each requirement MUST include:

- Requirement ID (e.g., FR-001).
- Description.
- Acceptance criteria.
- Priority (must-have, should-have, nice-to-have).

### 5. Non-Functional Requirements

Numbered list of non-functional requirements. Each requirement MUST
include:

- Requirement ID (e.g., NFR-001).
- Description.
- Measurable threshold or target.
- Category (performance, security, usability, etc.).

### 6. Constraints and Assumptions

List of constraints inherited from the initiative and any additional
constraints discovered during requirements analysis.

### 7. Traceability Matrix

A table mapping each requirement to its source initiative objective,
ensuring full traceability.

### 8. Dependencies

Dependencies between requirements and any external dependencies.

### 9. Open Questions

Any unresolved questions or ambiguities that need clarification before
planning can proceed.

### 10. Source Reference

Cross-reference to the source initiative document.

## Content Guidelines

### Tone and Style

- Use precise, unambiguous language.
- Each requirement must be testable and verifiable.
- Avoid subjective qualifiers ("fast", "easy", "user-friendly") without
  measurable thresholds.

### Length

- Aim for 3-8 pages depending on initiative complexity.
- Each requirement should be a single, clear statement.

### Completeness

- All required sections MUST be present.
- Every requirement must have an ID, description, and acceptance
  criteria.

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
REQ-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| REQ | Fixed prefix |
| YYYYMMDD | Date of creation |
| NN | Two-digit sequence number (01-99) |
| slug | Short hyphenated description of the initiative |

### Example

```
REQ-20260722-001_add-user-authentication.md
```

### Storage Location

Requirement documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/requirements/`

## Cross-References

### Related Templates

- **02_INIT_template.md** (SYS-03-IN): The source initiative from which
  these requirements were derived.
- **04_PLAN_template.md** (SYS-03-PL): The output produced by sdlc_30
  from this requirement document.

### Related Agent Contracts

- AGENT-planner: Used by sdlc_20 to produce this document from the
  INIT-DOC.

### Related Workflows

- **sdlc_20_planning_v1**: Produces this document from an INIT-DOC.
- **sdlc_30_backlog_v1**: Consumes this document to produce a PLAN-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.
