---
template_id: SYS-03-RV
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for approved Review documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_codebase_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Review (REV)

## Purpose

This template defines the structure for approved review documents
(REV-DOC). A review document is produced by the sdlc_80_review_v1
workflow from an approved validation document (VALIDATE-DOC). The
REV-DOC contains the final review assessment, quality evaluation, and
recommendations for the initiative. It is one of three documents
produced by sdlc_80 (along with MEM-DOC and CLOSE-DOC).

Review documents are stored in the reviews/ directory. Once approved,
they are immutable and form part of the SDLC audit trail.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-RV
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved review document produced by sdlc_80"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-RV | Fixed identifier for this template |
| version | "1.0.0" | Set by workflow on generation |
| doc_type | workflow_output | Workflow-generated delivery artifact |
| authority | workflow-generated | Produced by sdlc_80 |
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

A clear title for the review document. Format as a level-1 heading.

### 2. Document Metadata

Structured metadata about the review document:

- Document ID (e.g., REV-20260817-001)
- Source validation reference (VALID file path)
- Date of generation
- Producing workflow (sdlc_80_review_v1)
- Producing agent (AGENT-reviewer)

### 3. Review Summary

A high-level summary of the review findings and overall assessment.

### 4. Quality Assessment

Evaluation of the implementation quality across dimensions:

- Code quality.
- Test coverage adequacy.
- Documentation completeness.
- Architecture compliance.

### 5. Requirements Compliance

Assessment of whether all requirements were satisfied, referencing the
validation results.

### 6. Process Compliance

Assessment of whether the SDLC process was followed correctly:

- All workflow steps completed in order.
- All approval gates passed.
- All critique findings addressed.

### 7. Recommendations

Recommendations for:

- Follow-up work or enhancements.
- Process improvements.
- Technical debt items to address.

### 8. Critique Resolution

Results from the technical_critique and address_critique steps. Lists
each finding, its severity, and the resolution applied.

### 9. Overall Verdict

The overall review verdict:

- APPROVED: Initiative completed successfully.
- APPROVED WITH CONDITIONS: Minor issues remain; acceptable with
  documented plan.
- NOT APPROVED: Critical issues prevent closure.

### 10. Source Reference

Cross-reference to the source validation document.

## Content Guidelines

### Tone and Style

- Use objective, balanced language.
- Assessment claims must reference specific evidence.
- Recommendations must be actionable.

### Length

- Aim for 2-5 pages for the complete review document.
- Each section should be thorough but concise.

### Completeness

- All required sections MUST be present.
- Every quality dimension must be assessed.
- Every recommendation must be specific and actionable.

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
REV-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| REV | Fixed prefix |
| YYYYMMDD | Date of creation |
| NN | Two-digit sequence number (01-99) |
| slug | Short hyphenated description of the initiative |

### Example

```
REV-20260817-001_add-user-authentication.md
```

### Storage Location

Review documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/reviews/`

## Cross-References

### Related Templates

- **08_VALID_template.md** (SYS-03-VL): The source validation document
  from which this review was derived.
- **10_MEM_template.md** (SYS-03-MM): The companion memory document
  produced by sdlc_80.
- **11_CLOSE_template.md** (SYS-03-CL): The companion closure document
  produced by sdlc_80.

### Related Agent Contracts

- AGENT-reviewer: Used by sdlc_80 to produce this review document from
  the validation document.

### Related Workflows

- **sdlc_80_review_v1**: Produces this document (along with MEM-DOC and
  CLOSE-DOC) from a VALIDATE-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.
