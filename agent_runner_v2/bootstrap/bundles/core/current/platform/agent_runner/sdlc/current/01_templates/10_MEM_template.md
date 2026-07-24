---
template_id: SYS-03-MM
version: "1.0.0"
doc_type: "bundle_definition"
authority: "sdlc-owned"
scan_policy: "include"
scan_reason: "SDLC delivery document template for approved Memory and Lessons Learned documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "SDLC00SCF-20260722-3a011a52"
---

> Managed by workflow: `sdlc_00_delivery_scaffold_v1` / step: `publish_sdlc_scaffold`
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Memory / Lessons Learned (MEM)

## Purpose

This template defines the structure for approved memory and lessons
learned documents (MEM-DOC). A memory document is produced by the
sdlc_80_review_v1 workflow from an approved validation document
(VALIDATE-DOC). The MEM-DOC captures lessons learned, reusable patterns,
and institutional knowledge from the initiative. It is one of three
outputs from sdlc_80, alongside REV-DOC and CLOSE-DOC.

Memory documents are stored in the reviews/ directory (co-located with
the review and closure documents for the same initiative). Once
approved, they are immutable and form part of the SDLC audit trail.

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
scan_reason: "Approved memory and lessons learned document produced by sdlc_80"
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

- Document ID (e.g., MEM-20260722-001)
- Source validation reference (VALID file path)
- Date of creation
- Producing workflow (sdlc_80_review_v1)
- Producing agent (AGENT-memory-manager)

### 3. Executive Summary

A brief summary of the key lessons learned and knowledge captured.

### 4. Lessons Learned

Categorized lessons from the initiative:

- **What Went Well**: Practices and decisions that produced positive
  outcomes.
- **What Could Be Improved**: Areas where the process or approach fell
  short.
- **Unexpected Challenges**: Surprises encountered and how they were
  handled.

### 5. Reusable Patterns

Patterns, techniques, or solutions discovered during the initiative
that may be reusable in future work:

- Pattern description.
- Context of applicability.
- Implementation notes.

### 6. Knowledge Artifacts

Knowledge captured for future reference:

- Technical insights.
- Process improvements.
- Tool or framework discoveries.
- Integration patterns.

### 7. Recommendations for Future Initiatives

Actionable recommendations based on lessons learned:

- Process recommendations.
- Technical recommendations.
- Organizational recommendations.

### 8. Knowledge Retention Actions

Specific actions to retain the captured knowledge:

- Documentation updates needed.
- Training or onboarding material to create.
- Knowledge base entries to add.

### 9. Source Reference

Cross-reference to the source validation document.

## Content Guidelines

### Tone and Style

- Use reflective, constructive language.
- Focus on learning, not blame.
- Be specific enough for future practitioners to apply the lessons.

### Length

- Aim for 2-5 pages for the memory document.
- Each lesson should be concise but include context.

### Completeness

- All required sections MUST be present.
- At least 3 lessons learned should be captured.
- At least 1 reusable pattern should be documented.

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
MEM-20260722-001_add-user-authentication.md
```

### Storage Location

Memory documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/reviews/`

## Cross-References

### Related Templates

- **08_VALID_template.md** (SYS-03-VL): The source validation that
  informed the lessons learned.
- **09_REV_template.md** (SYS-03-RV): Review document produced
  alongside this memory document by sdlc_80.
- **11_CLOSE_template.md** (SYS-03-CL): Closure document produced
  alongside this memory document by sdlc_80.

### Related Agent Contracts

- AGENT-memory-manager: Used by sdlc_80 to produce this memory document.
- AGENT-reviewer: Produces the companion REV-DOC in sdlc_80.

### Related Workflows

- **sdlc_80_review_v1**: Produces this document (along with REV-DOC and
  CLOSE-DOC) from a VALIDATE-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.