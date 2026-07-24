---
template_id: SYS-03-IM
version: "1.0.0"
doc_type: "bundle_definition"
authority: "sdlc-owned"
scan_policy: "include"
scan_reason: "SDLC delivery document template for approved Implementation documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "SDLC00SCF-20260722-3a011a52"
---

> Managed by workflow: `sdlc_00_delivery_scaffold_v1` / step: `publish_sdlc_scaffold`
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Implementation (IMPL)

## Purpose

This template defines the structure for approved implementation documents
(IMPL-DOC). An implementation document is produced by the
sdlc_60_execution_v1 workflow from an approved task specification
(TASK-DOC). The IMPL-DOC records the actual implementation work
performed, including code changes, test results, and execution notes. It
serves as input to sdlc_70_validation_v1.

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

- Document ID (e.g., IMPL-20260722-001-01)
- Source task specification reference (TASK file path)
- Date of execution
- Producing workflow (sdlc_60_execution_v1)
- Producing agent (AGENT-executor)

### 3. Execution Summary

A high-level summary of the implementation work:

- Tasks completed.
- Files created or modified.
- Overall approach taken.
- Deviations from the task specification (if any).

### 4. Implementation Details

Detailed record of the implementation:

- Code changes with file paths and descriptions.
- Configuration changes.
- New files created.
- Dependencies added or updated.

### 5. Test Execution Report

Results of tests executed during implementation:

- Unit tests run and results.
- Integration tests run and results.
- Test coverage metrics (if available).
- Any tests that were skipped and why.

### 6. Deviations and Decisions

Record of any deviations from the task specification:

- What was changed and why.
- Alternative approaches considered.
- Decisions made during execution.
- Impact on acceptance criteria.

### 7. Known Issues

Any known issues discovered during implementation:

- Issue description.
- Severity assessment.
- Recommended follow-up.

### 8. Acceptance Criteria Verification

Self-assessment against the task specification acceptance criteria:

- Each criterion marked as met or not met.
- Evidence for each assessment.

### 9. Source Reference

Cross-reference to the source task specification document.

## Content Guidelines

### Tone and Style

- Use factual, objective language.
- Report what was done, not what was intended.
- Include specific file paths, function names, and line references.

### Length

- Aim for 3-10 pages depending on task complexity.
- Implementation details section should be thorough.

### Completeness

- All required sections MUST be present.
- All files created or modified must be listed.
- All tests executed must be reported.

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
IMPL-20260722-001-01_add-user-authentication.md
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

- AGENT-executor: Used by sdlc_60 to execute the task and produce this
  implementation document.

### Related Workflows

- **sdlc_60_execution_v1**: Produces this document from a TASK-DOC.
- **sdlc_70_validation_v1**: Consumes this document to produce a
  VALID-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.