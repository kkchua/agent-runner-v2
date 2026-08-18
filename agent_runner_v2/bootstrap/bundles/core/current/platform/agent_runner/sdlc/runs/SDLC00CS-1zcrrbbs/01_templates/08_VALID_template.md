---
template_id: SYS-03-VL
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for approved Validation documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_codebase_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Validation (VALID)

## Purpose

This template defines the structure for approved validation documents
(VALID-DOC). A validation document is produced by the
sdlc_70_validation_v1 workflow from an approved implementation document
(IMPL-DOC). The VALID-DOC records the validation results, including
whether the implementation meets all requirements, passes all tests,
and satisfies the acceptance criteria. It serves as input to
sdlc_80_review_v1.

Validation documents are stored in the validations/ directory. Once
approved, they are immutable and form part of the SDLC audit trail.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-VL
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved validation document produced by sdlc_70"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-VL | Fixed identifier for this template |
| version | "1.0.0" | Set by workflow on generation |
| doc_type | workflow_output | Workflow-generated delivery artifact |
| authority | workflow-generated | Produced by sdlc_70 |
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

A clear title for the validation document. Format as a level-1 heading.

### 2. Document Metadata

Structured metadata about the validation document:

- Document ID (e.g., VALID-20260817-001)
- Source implementation reference (IMPL file path)
- Date of generation
- Producing workflow (sdlc_70_validation_v1)
- Producing agent (AGENT-reviewer)

### 3. Validation Summary

A high-level summary of the validation outcome: pass or fail, with
key findings.

### 4. Requirements Verification

For each functional requirement (FR) from the requirements document,
document whether the implementation satisfies it:

- Requirement ID.
- Verification method (test, inspection, analysis).
- Result (pass, fail, partial).
- Evidence reference.

### 5. Non-Functional Requirements Verification

For each non-functional requirement (NFR), document whether the
implementation meets the measurable threshold:

- Requirement ID.
- Measured value.
- Required threshold.
- Result (pass, fail).

### 6. Test Execution Summary

Summary of all test executions:

- Total tests run.
- Passed, failed, skipped counts.
- Coverage metrics.
- Test log references.

### 7. Acceptance Criteria Validation

For each acceptance criterion from the original initiative, document
whether it is satisfied by the implementation.

### 8. Validation Defects

Any defects found during validation:

- Defect ID.
- Description.
- Severity (critical, major, minor).
- Impact assessment.

### 9. Critique Resolution

Results from the technical_critique and address_critique steps. Lists
each finding, its severity, and the resolution applied.

### 10. Validation Verdict

The overall validation verdict:

- PASS: All requirements met, all tests pass, no critical defects.
- CONDITIONAL PASS: Minor issues remain, acceptable with documented
  rationale.
- FAIL: Critical requirements not met or critical defects found.

### 11. Source Reference

Cross-reference to the source implementation document.

## Content Guidelines

### Tone and Style

- Use objective, evidence-based language.
- Every validation claim must reference specific evidence.
- Defect descriptions must be reproducible.

### Length

- Aim for 3-8 pages depending on initiative complexity.
- Verification tables may be long for complex requirements sets.

### Completeness

- All required sections MUST be present.
- Every requirement must have a verification result.
- Every defect must have a severity and impact assessment.

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
VALID-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| VALID | Fixed prefix |
| YYYYMMDD | Date of creation |
| NN | Two-digit sequence number (01-99) |
| slug | Short hyphenated description of the initiative |

### Example

```
VALID-20260817-001_add-user-authentication.md
```

### Storage Location

Validation documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/validations/`

## Cross-References

### Related Templates

- **07_IMPL_template.md** (SYS-03-IM): The source implementation that
  was validated.
- **09_REV_template.md** (SYS-03-RV): The output produced by sdlc_80
  from this validation document.
- **10_MEM_template.md** (SYS-03-MM): The memory document produced by
  sdlc_80 from this validation document.
- **11_CLOSE_template.md** (SYS-03-CL): The closure document produced
  by sdlc_80 from this validation document.

### Related Agent Contracts

- AGENT-reviewer: Used by sdlc_70 to produce this validation document
  from the implementation.

### Related Workflows

- **sdlc_70_validation_v1**: Produces this document from an IMPL-DOC.
- **sdlc_80_review_v1**: Consumes this document to produce REV-DOC,
  MEM-DOC, and CLOSE-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.
