---
template_id: SYS-03-CL
version: "1.0.0"
doc_type: "bundle_definition"
authority: "sdlc-owned"
scan_policy: "include"
scan_reason: "SDLC delivery document template for approved Initiative Closure documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "SDLC00SCF-20260722-3a011a52"
---

> Managed by workflow: `sdlc_00_delivery_scaffold_v1` / step: `publish_sdlc_scaffold`
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Initiative Closure (CLOSE)

## Purpose

This template defines the structure for approved initiative closure
documents (CLOSE-DOC). A closure document is produced by the
sdlc_80_review_v1 workflow from an approved validation document
(VALIDATE-DOC). The CLOSE-DOC formally records the completion of the
initiative, summarizing deliverables, outcomes, and final status. It is
one of three outputs from sdlc_80, alongside REV-DOC and MEM-DOC.

Closure documents are stored in the reviews/ directory (co-located with
the review and memory documents for the same initiative). Once approved,
they are immutable and form part of the SDLC audit trail.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-CL
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved initiative closure document produced by sdlc_80"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-CL | Fixed identifier for this template |
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

A clear title for the closure document. Format as a level-1 heading.

### 2. Document Metadata

Structured metadata about the closure document:

- Document ID (e.g., CLOSE-20260722-001)
- Source validation reference (VALID file path)
- Date of closure
- Producing workflow (sdlc_80_review_v1)
- Producing agent (AGENT-memory-manager)

### 3. Initiative Summary

A high-level summary of the initiative:

- Initiative ID and title.
- Duration (start date to closure date).
- Original objectives (from INIT-DOC).
- Final disposition (completed, partially completed, terminated).

### 4. Deliverables Summary

List of all deliverables produced during the initiative:

- Document deliverables (with file references).
- Code deliverables (with repository references).
- Configuration changes.
- Other artifacts.

### 5. Outcome Assessment

Assessment of outcomes against original objectives:

- Objectives achieved.
- Objectives partially achieved.
- Objectives not achieved (with explanation).
- Unplanned outcomes (if any).

### 6. Resource Summary

Summary of resources consumed:

- Workflow runs executed.
- Estimated total effort.
- Tools and services used.

### 7. Audit Trail Summary

Summary of the complete audit trail for this initiative:

- List of all documents produced across the SDLC chain.
- Document status for each (all should be "approved").
- Cross-references to all related documents.

### 8. Closure Declaration

Formal declaration of initiative closure:

- Closure decision (closed successfully, closed with exceptions, etc.).
- Date of closure.
- Responsible authority.
- Conditions of closure (if any).

### 9. Post-Closure Actions

Any follow-up actions required after closure:

- Maintenance items.
- Monitoring requirements.
- Future enhancement opportunities.

### 10. Source Reference

Cross-reference to the source validation document and the complete
audit trail.

## Content Guidelines

### Tone and Style

- Use formal, conclusive language.
- Be factual and objective.
- Summarize comprehensively but concisely.

### Length

- Aim for 2-5 pages for the closure document.
- The deliverables and audit trail sections should be thorough.

### Completeness

- All required sections MUST be present.
- All documents in the audit trail must be listed.
- All objectives must have an outcome assessment.

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
CLOSE-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| CLOSE | Fixed prefix |
| YYYYMMDD | Date of creation |
| NN | Two-digit sequence number (01-99) |
| slug | Short hyphenated description of the initiative |

### Example

```
CLOSE-20260722-001_add-user-authentication.md
```

### Storage Location

Closure documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/reviews/`

## Cross-References

### Related Templates

- **08_VALID_template.md** (SYS-03-VL): The source validation that
  informed the closure decision.
- **09_REV_template.md** (SYS-03-RV): Review document produced
  alongside this closure document by sdlc_80.
- **10_MEM_template.md** (SYS-03-MM): Memory document produced
  alongside this closure document by sdlc_80.

### Related Agent Contracts

- AGENT-memory-manager: Used by sdlc_80 to produce this closure
  document.
- AGENT-reviewer: Produces the companion REV-DOC in sdlc_80.

### Related Workflows

- **sdlc_80_review_v1**: Produces this document (along with REV-DOC and
  MEM-DOC) from a VALIDATE-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.