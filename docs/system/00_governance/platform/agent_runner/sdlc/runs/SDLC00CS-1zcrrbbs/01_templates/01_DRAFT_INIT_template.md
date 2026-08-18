---
template_id: SYS-03-DI
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for Draft Initiative documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_codebase_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Draft Initiative (DRAFT-INIT)

## Purpose

This template defines the structure for user-authored draft initiative
documents. A draft initiative is the input to the sdlc_10_requirement_v1
workflow, which transforms it into a structured, approved initiative
document (INIT-DOC).

Draft initiatives are authored by humans and stored in the
draftinitiates/ directory. They represent the initial problem
statement, objective, and scope definition that triggers an SDLC
initiative.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-DI
version: "<semver>"
doc_type: "workflow_output"
authority: "human-authored"
scan_policy: "include"
scan_reason: "Draft initiative document input to sdlc_10 workflow"
managed_by: "human-authored"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-DI | Fixed identifier for this template |
| version | User-defined | Start at "1.0.0" for initial draft |
| doc_type | workflow_output | Draft is a workflow input artifact |
| authority | human-authored | Drafts are authored by humans |
| scan_policy | include | Include in operational scans |
| scan_reason | User-defined | Describe why this doc should be scanned |
| managed_by | human-authored | Authored by human, not workflow |
| layer | layer3 | SDLC delivery layer |
| platform | agent-runner-v2 | Platform identifier |
| lifecycle_status | draft | Must be "draft" until processed |

## Required Content Sections

Instances of this template MUST contain the following sections in the
order shown:

### 1. Title

A clear, concise title for the initiative. Format as a level-1 heading
(# Title).

### 2. Objective

A statement of what this initiative aims to achieve. This should be a
single paragraph describing the desired outcome.

### 3. Problem Statement

A description of the problem or opportunity that this initiative
addresses. Include:

- Current state and its pain points.
- Why this initiative is needed.
- What happens if the initiative is not undertaken.

### 4. Expected Outcomes

A bullet list of concrete, measurable outcomes that will result from
this initiative. Each outcome should be specific enough to verify.

### 5. Scope

Define the boundaries of the initiative:

- **In Scope**: What the initiative will cover.
- **Out of Scope**: What the initiative will explicitly not cover.

### 6. Constraints

Any constraints that the initiative must work within:

- Technical constraints (platform, language, framework requirements).
- Time constraints (deadlines, milestones).
- Resource constraints (team size, budget).
- Regulatory or compliance constraints.

### 7. Dependencies

List any external dependencies that this initiative relies on:

- Other initiatives or projects.
- Third-party systems or services.
- Data or infrastructure prerequisites.
- Organizational approvals needed.

### 8. Success Criteria

Define how success will be measured. These should be specific,
testable criteria that can be evaluated at initiative completion.

### 9. Notes (Optional)

Any additional context, background information, or notes that may
help the workflow process the draft initiative. This section is
optional and may be omitted if not needed.

## Content Guidelines

### Tone and Style

- Use clear, direct language. Avoid marketing or promotional language.
- Be specific and precise. Avoid vague statements.
- Use active voice where possible.
- Keep paragraphs short and focused.

### Length

- Aim for 1-3 pages for the complete draft.
- Each section should be concise but complete.
- The Problem Statement and Scope sections may be longer than others.

### Completeness

- All required sections MUST be present.
- Optional sections (Notes) may be omitted.
- Within required sections, all listed sub-items SHOULD be addressed
  if applicable. If a sub-item does not apply, state "None" or "N/A"
  explicitly rather than omitting it.

### ASCII-Only Requirement

All content MUST use ASCII characters only:

- Use plain hyphens (-) for dashes. Do NOT use em-dashes or en-dashes.
- Use straight quotes (" and ') for quotations. Do NOT use curly quotes.
- Do NOT use any other Unicode characters (bullets, arrows, ellipsis,
  etc.).

### Plain Text Headings

Section headings MUST use plain text only. Do NOT add backticks, bold,
italics, or other inline formatting to section headings.

## Naming Convention for Instances

Instances of this template MUST follow this naming convention:

```
DRAFT-INIT-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| DRAFT-INIT | Fixed prefix |
| YYYYMMDD | Date of draft creation |
| NN | Two-digit sequence number (01-99) |
| slug | Short hyphenated description of the initiative |

### Example

```
DRAFT-INIT-20260817-001_add-user-authentication.md
```

### Storage Location

Draft initiatives are stored in:
`docs/repo/agent_runner/sdlc/delivery/draftinitiates/`

## Cross-References

### Related Templates

- **02_INIT_template.md** (SYS-03-IN): The output produced by sdlc_10
  from this draft initiative.

### Related Agent Contracts

- This draft is input to the sdlc_10 workflow. sdlc_10 uses its own
  prompts (no agent contract) to transform the draft into an INIT-DOC.
- **AGENT-planner**: Consumes the resulting INIT-DOC in sdlc_20 as
  input for generating the REQ-DOC.

### Related Workflows

- **sdlc_10_requirement_v1**: Consumes this draft and produces an
  approved INIT-DOC.

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields and values.
- DOCUMENT_AUTHORITY.md: Authority classification rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform-specific metadata extensions.
