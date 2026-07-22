---
template_id: SYS-03-IN
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for Initiative documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Initiative Document (INIT-DOC)

## Purpose

This template defines the structure for approved initiative documents
produced by the sdlc_10_requirement_v1 workflow. An initiative document
(INIT-DOC) is the structured, reviewed, and approved version of a
human-authored draft initiative.

The INIT-DOC is the first formal artifact in the SDLC delivery chain. It
represents the agreed-upon scope, objectives, and boundaries for an SDLC
initiative after the sdlc_10 workflow has processed the draft through
review and approval gates.

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
scan_reason: "Approved initiative document in SDLC delivery chain"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft" | "approved"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-IN | Fixed identifier for this template |
| version | Auto-assigned | Set by sdlc_10 workflow |
| doc_type | workflow_output | Generated workflow output |
| authority | workflow-generated | Produced by sdlc_10 workflow |
| scan_policy | include | Permanent delivery document |
| scan_reason | Auto-assigned | Describe purpose for scanning |
| managed_by | workflow-generated | Workflow-generated document |
| layer | layer3 | SDLC delivery layer |
| platform | agent-runner-v2 | Platform identifier |
| lifecycle_status | draft/approved | "draft" during generation, "approved" after gate |

### Additional Field: effective_version

The workflow MUST add `effective_version` when promoting to `approved`:

```
effective_version: "<workflow-run-id>"
```

### Additional Field: source_document

The workflow MUST add `source_document` referencing the draft initiative:

```
source_document: "DRAFT-INIT-{YYYYMMDD}-{NN}_{slug}.md"
```

## Required Content Sections

Instances of this template MUST contain the following sections in the
order shown:

### 1. Title

A clear, concise title for the initiative. Should match or improve upon
the draft initiative title.

### 2. Objective

A refined statement of what this initiative aims to achieve. This section
should be more precise than the draft version, incorporating any
clarifications from the review process.

### 3. Problem Statement

A refined description of the problem or opportunity. Include:

- Current state and its specific pain points (as validated by review).
- Why this initiative is needed (business or technical justification).
- Impact of not undertaking this initiative.

### 4. Expected Outcomes

A prioritized bullet list of concrete, measurable outcomes. Each outcome
must be:

- Specific enough to verify.
- Aligned with the problem statement.
- Achievable within the defined scope.

### 5. Scope

Clearly defined boundaries:

- **In Scope**: Specific work items, features, or changes covered.
- **Out of Scope**: Items explicitly excluded.
- **Boundary Conditions**: Where the initiative interfaces with external
  systems or other initiatives.

### 6. Constraints

All constraints that apply:

- Technical constraints (mandated platform, language, framework).
- Time constraints (must-complete dates, milestones).
- Resource constraints (team, budget, infrastructure).
- Regulatory or compliance constraints.
- Architectural or design constraints.

### 7. Dependencies

All external dependencies:

- Prerequisite initiatives or projects.
- Required third-party systems, services, or APIs.
- Data or infrastructure needs.
- Organizational approvals or stakeholder sign-offs.
- Other SDLC initiatives that must complete first.

### 8. Success Criteria

Specific, testable criteria that determine initiative success. Each
criterion should be:

- **Measurable**: Can be objectively verified.
- **Complete**: Covers the full scope of expected outcomes.
- **Aligned**: Directly linked to the objective and problem statement.

### 9. Stakeholders

List of key stakeholders:

- Initiative sponsor or requester.
- Primary users or beneficiaries.
- Review and approval authorities.
- Teams or individuals affected by the initiative.

### 10. Notes (Optional)

Any additional context, assumptions, or background that aids
understanding. This section is optional.

## Content Guidelines

### Relationship to Draft

The INIT-DOC is a refinement of the DRAFT-INIT, not a replacement. Key
differences:

- Language should be more precise and structured.
- Scope boundaries should be clearer and more explicit.
- Outcomes should be more measurable.
- Constraints and dependencies should be more complete.
- The overall structure should follow this template exactly.

### Completeness

- All required sections MUST be present.
- Within each section, all listed sub-items MUST be addressed.
- If a sub-item does not apply, state "None" explicitly.
- The document must be self-contained and understandable without
  reference to the draft.

### ASCII-Only Requirement

All content MUST use ASCII characters only:

- Use plain hyphens (-) for dashes. Do NOT use em-dashes or en-dashes.
- Use straight quotes (" and ') for quotations. Do NOT use curly quotes.
- Do NOT use any other Unicode characters.

### Plain Text Headings

Section headings MUST use plain text only. Do NOT add backticks, bold,
italics, or other inline formatting.

## Naming Convention for Instances

Instances of this template MUST follow this naming convention:

```
INIT-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| INIT | Fixed prefix |
| YYYYMMDD | Date of initiative approval |
| NN | Two-digit sequence number (01-99) |
| slug | Short hyphenated description (same as draft) |

### Example

```
INIT-20260722-001_add-user-authentication.md
```

### Storage Location

Initiatives are stored in:
`docs/repo/agent_runner/sdlc/delivery/initiatives/`

## Cross-References

### Related Templates

- **01_DRAFT_INIT_template.md** (SYS-03-DI): The input draft that this
  initiative was generated from.
- **03_REQ_template.md** (SYS-03-RQ): The next document in the delivery
  chain, produced from this initiative.

### Related Agent Contracts

- AGENT-planner: Used by sdlc_10 to generate this document from the
  draft initiative.

### Related Workflows

- **sdlc_10_requirement_v1**: Produces this document.
- **sdlc_20_planning_v1**: Consumes this document (must be approved).

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields.
- GOVERNANCE_LIFECYCLE.md: Lifecycle state transition rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform metadata extensions.
- VALIDATION_CONTRACT.md: Document validation patterns.
