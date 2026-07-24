---
template_id: SYS-03-IN
version: "1.0.0"
doc_type: "bundle_definition"
authority: "sdlc-owned"
scan_policy: "include"
scan_reason: "SDLC delivery document template for approved Initiative documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "SDLC00SCF-20260722-3a011a52"
---

> Managed by workflow: `sdlc_00_delivery_scaffold_v1` / step: `publish_sdlc_scaffold`
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Initiative (INIT)

## Purpose

This template defines the structure for approved initiative documents
(INIT-DOC). An initiative document is produced by the
sdlc_10_requirement_v1 workflow from a user-authored draft initiative
(DRAFT-INIT). The INIT-DOC is a structured, validated representation of
the initiative that serves as input to sdlc_20_planning_v1.

Initiative documents are stored in the initiatives/ directory. Once
approved, they are immutable and form part of the SDLC audit trail.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-IN
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved initiative document produced by sdlc_10"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-IN | Fixed identifier for this template |
| version | "1.0.0" | Set by workflow on generation |
| doc_type | workflow_output | Workflow-generated delivery artifact |
| authority | workflow-generated | Produced by sdlc_10 |
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

A clear, concise title for the initiative. Format as a level-1 heading.

### 2. Initiative Metadata

Structured metadata about the initiative:

- Initiative ID (e.g., INIT-20260722-001)
- Source draft reference (DRAFT-INIT file path)
- Date of approval
- Producing workflow (sdlc_10_requirement_v1)

### 3. Objective

A precise statement of what the initiative aims to achieve. This is
refined from the draft initiative to be more specific and measurable.

### 4. Problem Statement

A structured description of the problem or opportunity, including:

- Current state analysis.
- Impact of the problem.
- Justification for the initiative.

### 5. Expected Outcomes

A numbered list of concrete, measurable outcomes. Each outcome must be
verifiable at initiative completion.

### 6. Scope

Detailed scope definition:

- **In Scope**: Specific deliverables and boundaries.
- **Out of Scope**: Explicit exclusions.
- **Assumptions**: Assumptions made during scoping.

### 7. Constraints

Comprehensive constraints list:

- Technical constraints.
- Time constraints.
- Resource constraints.
- Compliance constraints.

### 8. Dependencies

Complete dependencies list:

- Upstream dependencies.
- External system dependencies.
- Data prerequisites.
- Required approvals.

### 9. Success Criteria

Testable success criteria with acceptance thresholds.

### 10. Risk Assessment

Identified risks and mitigation strategies:

- Technical risks.
- Schedule risks.
- Resource risks.
- Mitigation approach for each risk.

### 11. Source Reference

Cross-reference to the source draft initiative document.

## Content Guidelines

### Tone and Style

- Use precise, formal language suitable for a governance document.
- All claims must be supported by evidence or reasoning.
- Avoid ambiguous terms; use measurable descriptors.

### Length

- Aim for 2-5 pages for the complete initiative document.
- Each section should be thorough but concise.

### Completeness

- All required sections MUST be present.
- Empty sections MUST contain "None" or "N/A" with a brief explanation.

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
INIT-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| INIT | Fixed prefix |
| YYYYMMDD | Date of creation |
| NN | Two-digit sequence number (01-99) |
| slug | Short hyphenated description of the initiative |

### Example

```
INIT-20260722-001_add-user-authentication.md
```

### Storage Location

Initiative documents are stored in:
`docs/repo/agent_runner/sdlc/delivery/initiatives/`

## Cross-References

### Related Templates

- **01_DRAFT_INIT_template.md** (SYS-03-DI): The source draft from which
  this initiative was derived.
- **03_REQ_template.md** (SYS-03-RQ): The output produced by sdlc_20
  from this initiative.

### Related Agent Contracts

- AGENT-planner: Consumes this document in sdlc_20. INIT-DOC is
  produced by sdlc_10 using its own prompts (no agent).

### Related Workflows

- **sdlc_10_requirement_v1**: Produces this document from a DRAFT-INIT.
- **sdlc_20_planning_v1**: Consumes this document to produce a REQ-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.