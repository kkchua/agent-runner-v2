---
template_id: SYS-03-RQ
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for Requirement documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Requirement Document (REQ-DOC)

## Purpose

This template defines the structure for approved requirement documents
produced by the sdlc_20_planning_v1 workflow. A requirement document
(REQ-DOC) transforms the approved initiative (INIT-DOC) into detailed,
structured requirements suitable for planning and design.

The REQ-DOC is the second formal artifact in the SDLC delivery chain. It
represents the detailed functional and non-functional requirements that
must be delivered by the initiative.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-RQ
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved requirement document in SDLC delivery chain"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft" | "approved"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-RQ | Fixed identifier for this template |
| version | Auto-assigned | Set by sdlc_20 workflow |
| doc_type | workflow_output | Generated workflow output |
| authority | workflow-generated | Produced by sdlc_20 workflow |
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

The workflow MUST add `source_document` referencing the initiative:

```
source_document: "INIT-{YYYYMMDD}-{NN}_{slug}.md"
```

## Required Content Sections

Instances of this template MUST contain the following sections in the
order shown:

### 1. Title

A clear title that identifies this requirement document. Should reference
the parent initiative.

### 2. Requirement Overview

A summary of the requirements and how they relate to the initiative
objective. This section establishes traceability back to the approved
INIT-DOC.

### 3. Functional Requirements

A numbered list of functional requirements. Each requirement MUST
include:

- **Requirement ID**: Unique identifier (FR-001, FR-002, etc.).
- **Description**: What the system must do.
- **Priority**: Must-have, Should-have, Could-have, Won't-have (MoSCoW).
- **Dependencies**: Links to other requirements or external factors.
- **Acceptance Criteria**: Specific conditions that verify this
  requirement is met.

### 4. Non-Functional Requirements

A numbered list of non-functional requirements. Each requirement MUST
include:

- **Requirement ID**: Unique identifier (NFR-001, NFR-002, etc.).
- **Category**: Performance, Security, Usability, Reliability, etc.
- **Description**: The quality attribute or constraint.
- **Priority**: Must-have, Should-have, Could-have, Won't-have.
- **Acceptance Criteria**: Specific, measurable verification conditions.

### 5. Data Requirements

If applicable, describe data-related requirements:

- Data entities or structures that must be created or modified.
- Data migration or transformation needs.
- Data retention, privacy, or compliance requirements.
- Data volume and performance expectations.

### 6. Integration Requirements

If applicable, describe integration requirements:

- External systems or services that must be integrated.
- API contracts or interface specifications.
- Authentication and authorization requirements.
- Data exchange formats and protocols.

### 7. User Stories (Optional)

If the team uses user stories, include a set of user stories that
capture the functional requirements in an end-user format:

- "As a <role>, I want <capability>, so that <benefit>."

### 8. Assumptions and Constraints

Document any assumptions made during requirements analysis and any
constraints that affect requirements:

- Assumptions about the operating environment.
- Assumptions about user behavior or capabilities.
- Technical or business constraints on requirements.
- Legal or regulatory constraints.

### 9. Traceability Matrix

A table linking requirements to initiative outcomes:

| Requirement ID | Outcome Reference | Priority |
|---|---|---|
| FR-001 | Outcome 1 | Must-have |
| FR-002 | Outcome 2 | Should-have |

## Content Guidelines

### Requirements Quality

Each requirement should be:

- **Unambiguous**: Can only be interpreted one way.
- **Testable**: Can be verified through inspection, analysis, or testing.
- **Complete**: Contains all the information needed for implementation.
- **Consistent**: Does not contradict other requirements.
- **Feasible**: Can be implemented within the defined constraints.
- **Necessary**: Directly supports the initiative objective.

### Prioritization

Use the MoSCoW method:

- **Must-have**: Required for the initiative to be successful.
- **Should-have**: Important but not strictly necessary for launch.
- **Could-have**: Desirable but low-impact.
- **Won't-have**: Explicitly deferred to a future initiative.

### ASCII-Only Requirement

All content MUST use ASCII characters only.

### Plain Text Headings

Section headings MUST use plain text only.

## Naming Convention for Instances

```
REQ-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| REQ | Fixed prefix |
| YYYYMMDD | Date of requirement approval |
| NN | Two-digit sequence number |
| slug | Short hyphenated description (same as initiative) |

### Example

```
REQ-20260722-001_add-user-authentication.md
```

### Storage Location

Requirements are stored in:
`docs/repo/agent_runner/sdlc/delivery/requirements/`

## Cross-References

### Related Templates

- **02_INIT_template.md** (SYS-03-IN): Input document.
- **04_PLAN_template.md** (SYS-03-PL): Next document in chain.

### Related Agent Contracts

- AGENT-planner: Used by sdlc_20 to generate requirements.

### Related Workflows

- **sdlc_20_planning_v1**: Produces this document.
- **sdlc_30_backlog_v1**: Consumes this document (must be approved).

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields.
- GOVERNANCE_LIFECYCLE.md: Lifecycle state transition rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform metadata extensions.
- VALIDATION_CONTRACT.md: Document validation patterns.
