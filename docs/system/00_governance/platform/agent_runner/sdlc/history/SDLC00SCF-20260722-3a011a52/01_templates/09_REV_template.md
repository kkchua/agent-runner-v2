---
template_id: SYS-03-RV
version: "1.0.0"
doc_type: "bundle_definition"
authority: "sdlc-owned"
scan_policy: "include"
scan_reason: "SDLC delivery document template for approved Review documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "SDLC00SCF-20260722-3a011a52"
---

> Managed by workflow: `sdlc_00_delivery_scaffold_v1` / step: `publish_sdlc_scaffold`
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Review (REV)

## Purpose

This template defines the structure for approved review documents
(REV-DOC). A review document is produced by the sdlc_80_review_v1
workflow from an approved validation document (VALIDATE-DOC). The REV-DOC
contains the final review findings, overall quality assessment, and
recommendations for the initiative. It is one of three outputs from
sdlc_80, alongside MEM-DOC and CLOSE-DOC.

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

- Document ID (e.g., REV-20260722-001)
- Source validation reference (VALID file path)
- Date of review
- Producing workflow (sdlc_80_review_v1)
- Producing agent (AGENT-reviewer)

### 3. Review Summary

High-level summary of the review outcome:

- Overall initiative assessment.
- Key strengths identified.
- Key weaknesses or concerns.
- Final recommendation.

### 4. Quality Assessment

Comprehensive quality assessment of the initiative:

- Requirements quality.
- Implementation quality.
- Testing quality.
- Documentation quality.
- Process adherence.

### 5. Findings Summary

Consolidated findings from the review:

- Critical findings.
- Major findings.
- Minor findings.
- Observations.

### 6. Recommendations

Actionable recommendations:

- Immediate actions required.
- Short-term improvements.
- Long-term considerations.

### 7. Initiative Outcome Assessment

Assessment of whether the initiative achieved its objectives:

- Original objectives from INIT-DOC.
- Actual outcomes achieved.
- Gap analysis (if any).

### 8. Final Disposition

The final review disposition:

- Approved, approved with conditions, or rejected.
- Conditions for approval (if applicable).
- Rationale for the disposition.

### 9. Source Reference

Cross-reference to the source validation document.

## Content Guidelines

### Tone and Style

- Use balanced, professional language.
- Acknowledge both strengths and weaknesses.
- Recommendations must be specific and actionable.

### Length

- Aim for 3-6 pages for the review document.
- Each finding should be concise but complete.

### Completeness

- All required sections MUST be present.
- Every finding must have a severity classification.

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
REV-20260722-001_add-user-authentication.md
```

### Storage Location

Review documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/reviews/`

## Cross-References

### Related Templates

- **08_VALID_template.md** (SYS-03-VL): The source validation that was
  reviewed.
- **10_MEM_template.md** (SYS-03-MM): Memory document produced
  alongside this review by sdlc_80.
- **11_CLOSE_template.md** (SYS-03-CL): Closure document produced
  alongside this review by sdlc_80.

### Related Agent Contracts

- AGENT-reviewer: Used by sdlc_80 to produce this review document.
- AGENT-memory-manager: Produces the companion MEM-DOC in sdlc_80.

### Related Workflows

- **sdlc_80_review_v1**: Produces this document (along with MEM-DOC and
  CLOSE-DOC) from a VALIDATE-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.