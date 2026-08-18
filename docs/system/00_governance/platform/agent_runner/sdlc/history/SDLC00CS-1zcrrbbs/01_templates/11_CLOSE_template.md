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
effective_version: "SDLC00CS-1zcrrbbs"
---

> Managed by workflow: `sdlc_00_codebase_scaffold_v1` / step: `publish_sdlc_scaffold`
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Initiative Closure (CLOSE)

## Purpose

This template defines the structure for approved initiative closure
documents (CLOSE-DOC). A closure document is produced by the
sdlc_80_review_v1 workflow from an approved validation document
(VALIDATE-DOC). The CLOSE-DOC formally closes the initiative,
summarizing outcomes, confirming deliverables, and recording the final
status. It is one of three documents produced by sdlc_80 (along with
REV-DOC and MEM-DOC).

Closure documents are stored in the reviews/ directory. Once approved,
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

- Document ID (e.g., CLOSE-20260817-001)
- Source validation reference (VALID file path)
- Date of generation
- Producing workflow (sdlc_80_review_v1)
- Producing agent (AGENT-memory-manager)

### 3. Initiative Closure Summary

A summary of the initiative and its closure status.

### 4. Outcome Verification

For each expected outcome from the initiative document, document
whether it was achieved:

- Outcome description.
- Achievement status (achieved, partially achieved, not achieved).
- Evidence of achievement.

### 5. Deliverables Inventory

Complete list of all deliverables produced during the initiative:

- Document deliverables (with file paths).
- Code deliverables (with commit references).
- Test deliverables (with test suite references).

### 6. Success Criteria Evaluation

For each success criterion from the initiative document, document
whether it was met:

- Success criterion.
- Evaluation result.
- Measurement evidence.

### 7. Initiative Timeline

Summary of the initiative timeline:

- Start date.
- Key milestones and dates.
- Closure date.
- Duration versus planned duration.

### 8. Resource Utilization

Summary of resources consumed:

- Workflow steps executed.
- Coder invocations and token usage.
- Review iterations.

### 9. Critique Resolution

Results from the technical_critique and address_critique steps. Lists
each finding, its severity, and the resolution applied.

### 10. Closure Declaration

Formal declaration of initiative closure:

- Closure status: CLOSED, CLOSED WITH CONDITIONS, or NOT CLOSED.
- Conditions or follow-up items, if any.
- Authorization reference.

### 11. Source Reference

Cross-reference to the source validation document.

## Content Guidelines

### Tone and Style

- Use formal, conclusive language.
- Every claim about outcomes must reference evidence.
- Closure declaration must be unambiguous.

### Length

- Aim for 2-5 pages for the complete closure document.
- Each section should be thorough but concise.

### Completeness

- All required sections MUST be present.
- Every outcome must have an achievement status.
- Every deliverable must be listed.

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
CLOSE-20260817-001_add-user-authentication.md
```

### Storage Location

Closure documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/reviews/`

## Cross-References

### Related Templates

- **08_VALID_template.md** (SYS-03-VL): The source validation document
  from which this closure was derived.
- **09_REV_template.md** (SYS-03-RV): The companion review document
  produced by sdlc_80.
- **10_MEM_template.md** (SYS-03-MM): The companion memory document
  produced by sdlc_80.

### Related Agent Contracts

- AGENT-memory-manager: Used by sdlc_80 to produce this closure
  document from the validation document.

### Related Workflows

- **sdlc_80_review_v1**: Produces this document (along with REV-DOC and
  MEM-DOC) from a VALIDATE-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.