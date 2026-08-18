---
template_id: SYS-03-IM
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for approved Implementation documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_codebase_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Implementation (IMPL)

## Purpose

This template defines the structure for approved implementation documents
(IMPL-DOC). An implementation document is produced by the
sdlc_60_execution_v1 workflow from an approved task specification
(TASK-DOC). The IMPL-DOC records what was actually implemented, the
files changed, tests added, and execution results. It serves as input
to sdlc_70_validation_v1.

Implementation documents are stored in the implementations/ directory.
Once approved, they are immutable and form part of the SDLC audit trail.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-IM
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved implementation document produced by sdlc_60"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-IM | Fixed identifier for this template |
| version | "1.0.0" | Set by workflow on generation |
| doc_type | workflow_output | Workflow-generated delivery artifact |
| authority | workflow-generated | Produced by sdlc_60 |
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

A clear title for the implementation document. Format as a level-1
heading.

### 2. Document Metadata

Structured metadata about the implementation document:

- Document ID (e.g., IMPL-20260817-001-01)
- Source task reference (TASK file path)
- Date of generation
- Producing workflow (sdlc_60_execution_v1)
- Producing agent (AGENT-executor)

### 3. Implementation Summary

A high-level summary of what was implemented and how it maps to the
task specification.

### 4. Changes Made

Detailed list of all changes made:

- Files created.
- Files modified.
- Files deleted.
- Configuration changes.

### 5. Test Results

Results of all tests executed:

- Unit test results.
- Integration test results.
- Test coverage information.
- Any skipped or failed tests with explanations.

### 6. Acceptance Criteria Verification

For each acceptance criterion from the task specification, document
whether it was met and provide evidence.

### 7. Deviations from Task Specification

Any deviations from the original task specification, with justification
for each deviation.

### 8. Known Issues

Any known issues, limitations, or TODO items remaining after
implementation.

### 9. Critique Resolution

Results from the technical_critique and address_critique steps. Lists
each finding, its severity, and the resolution applied.

### 10. Source Reference

Cross-reference to the source task specification document.

## Content Guidelines

### Tone and Style

- Use factual, evidence-based language.
- All claims about implementation must be backed by test results or
  file references.
- Deviations must include clear justification.

### Length

- Aim for 3-8 pages depending on implementation complexity.
- Test results may be summarized with references to full logs.

### Completeness

- All required sections MUST be present.
- Every file change must be listed.
- Every acceptance criterion must have a verification result.

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
IMPL-{YYYYMMDD}-{NN}-{TT}_{slug}.md
```

| Component | Description |
|---|---|
| IMPL | Fixed prefix |
| YYYYMMDD | Date of creation |
| NN | Two-digit initiative sequence number (01-99) |
| TT | Two-digit task number within initiative (01-99) |
| slug | Short hyphenated description of the initiative |

### Example

```
IMPL-20260817-001-01_add-user-authentication.md
```

### Storage Location

Implementation documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/implementations/`

## Cross-References

### Related Templates

- **06_TASK_template.md** (SYS-03-TK): The source task specification
  from which this implementation was executed.
- **08_VALID_template.md** (SYS-03-VL): The output produced by sdlc_70
  from this implementation document.

### Related Agent Contracts

- AGENT-executor: Used by sdlc_60 to produce this implementation
  document from the task specification.

### Related Workflows

- **sdlc_60_execution_v1**: Produces this document from a TASK-DOC.
- **sdlc_70_validation_v1**: Consumes this document to produce a
  VALID-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.
