---
template_id: SYS-03-MM
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for approved Memory (Lessons Learned) documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_codebase_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Memory (MEM)

## Purpose

This template defines the structure for approved memory (lessons learned)
documents (MEM-DOC). A memory document is produced by the
sdlc_80_review_v1 workflow from an approved validation document
(VALIDATE-DOC). The MEM-DOC captures lessons learned, reusable patterns,
and knowledge artifacts from the initiative. It is one of three
documents produced by sdlc_80 (along with REV-DOC and CLOSE-DOC).

Memory documents are stored in the reviews/ directory. Once approved,
they are immutable and form part of the SDLC audit trail.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-MM
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved memory (lessons learned) document produced by sdlc_80"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-MM | Fixed identifier for this template |
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

A clear title for the memory document. Format as a level-1 heading.

### 2. Document Metadata

Structured metadata about the memory document:

- Document ID (e.g., MEM-20260817-001)
- Source validation reference (VALID file path)
- Date of generation
- Producing workflow (sdlc_80_review_v1)
- Producing agent (AGENT-memory-manager)

### 3. Lessons Learned Summary

A high-level summary of the key lessons learned from this initiative.

### 4. What Went Well

List of positive outcomes and successful practices:

- Technical decisions that worked well.
- Process aspects that were effective.
- Collaboration patterns that succeeded.

### 5. What Could Be Improved

List of areas for improvement:

- Technical approaches that had issues.
- Process bottlenecks encountered.
- Communication gaps identified.

### 6. Reusable Patterns

Patterns, techniques, or solutions discovered during the initiative
that could be reused in future work:

- Code patterns.
- Architecture patterns.
- Testing strategies.
- Workflow optimizations.

### 7. Technical Debt Items

Technical debt accumulated during the initiative:

- Known shortcuts taken.
- Deferred improvements.
- Suggested future refactoring.

### 8. Knowledge Artifacts

Links or references to any reusable knowledge artifacts created:

- Documentation produced.
- Scripts or tools developed.
- Configuration templates.

### 9. Critique Resolution

Results from the technical_critique and address_critique steps. Lists
each finding, its severity, and the resolution applied.

### 10. Source Reference

Cross-reference to the source validation document.

## Content Guidelines

### Tone and Style

- Use reflective, constructive language.
- Lessons must be specific and actionable.
- Avoid blame; focus on systemic improvements.

### Length

- Aim for 2-5 pages for the complete memory document.
- Each lesson should be concise but include enough context to be
  useful.

### Completeness

- All required sections MUST be present.
- Every lesson must include context and recommendation.
- Every reusable pattern must include usage guidance.

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
MEM-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| MEM | Fixed prefix |
| YYYYMMDD | Date of creation |
| NN | Two-digit sequence number (01-99) |
| slug | Short hyphenated description of the initiative |

### Example

```
MEM-20260817-001_add-user-authentication.md
```

### Storage Location

Memory documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/reviews/`

## Cross-References

### Related Templates

- **08_VALID_template.md** (SYS-03-VL): The source validation document
  from which this memory was derived.
- **09_REV_template.md** (SYS-03-RV): The companion review document
  produced by sdlc_80.
- **11_CLOSE_template.md** (SYS-03-CL): The companion closure document
  produced by sdlc_80.

### Related Agent Contracts

- AGENT-memory-manager: Used by sdlc_80 to produce this memory document
  from the validation document.

### Related Workflows

- **sdlc_80_review_v1**: Produces this document (along with REV-DOC and
  CLOSE-DOC) from a VALIDATE-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.
