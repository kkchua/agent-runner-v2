---
template_id: SYS-03-TK
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for Task specification documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Task Specification Document (TASK-DOC)

## Purpose

This template defines the structure for approved task specification
documents produced by the sdlc_50_implementation_v1 workflow. A task
specification document (TASK-DOC) transforms a backlog item from the
approved backlog (BACKLOG-DOC) into a detailed, actionable task
specification ready for implementation.

The TASK-DOC is the fifth formal artifact in the SDLC delivery chain. It
represents the detailed instruction set that guides the implementation
workflow (sdlc_60).

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-TK
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved task specification document in SDLC delivery chain"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft" | "approved"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-TK | Fixed identifier for this template |
| version | Auto-assigned | Set by sdlc_50 workflow |
| doc_type | workflow_output | Generated workflow output |
| authority | workflow-generated | Produced by sdlc_50 workflow |
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

The workflow MUST add `source_document` referencing the backlog item:

```
source_document: "BACKLOG-{YYYYMMDD}-{NN}_{slug}.md"
```

## Required Content Sections

Instances of this template MUST contain the following sections in the
order shown:

### 1. Title

A clear title that identifies this task specification. Should reference
the backlog item it implements and include a task sequence number.

### 2. Task Summary

A concise summary of what this task accomplishes:

- Reference to parent backlog item (BL-XXX).
- One-line description of the task.
- Priority and estimated effort.

### 3. Implementation Requirements

Detailed requirements for the implementation:

- **Functional Requirements**: What the implementation must do.
- **Non-Functional Requirements**: Performance, security, quality
  constraints.
- **Acceptance Criteria**: Specific conditions that verify task
  completion. Each criterion must be testable.
- **Definition of Done**: All criteria that must be met.

### 4. Technical Guidance

Technical guidance for the implementer:

- **Files to Create**: Specific files that need to be created.
- **Files to Modify**: Specific files that need to be changed.
- **Design Patterns**: Patterns or conventions to follow.
- **Code Style Requirements**: Standards and linting rules.
- **Testing Requirements**: Unit, integration, or manual tests needed.

### 5. Input Specifications

Inputs that the implementer needs:

- **Required Documents**: Approved documents to reference.
- **External Data**: Sample data, configuration, or fixtures.
- **Access Requirements**: Permissions or credentials needed.

### 6. Verification Steps

Steps that will be used to verify the implementation:

- **Build Verification**: Does the code compile/build?
- **Test Execution**: What tests must pass?
- **Manual Verification**: Steps for manual review.
- **Regression Checks**: Existing functionality that must not break.

### 7. Dependencies

Dependencies that must be satisfied:

- Prerequisite tasks (other TASK-DOCs that must complete first).
- External systems or services required.
- Data or infrastructure prerequisites.

### 8. Output Specifications

Expected outputs from the task:

- **Deliverables**: Files, configurations, or artifacts to produce.
- **Documentation**: Updates to docs, README, or comments.
- **Tests**: Test files or test data to create.

### 9. Notes (Optional)

Any additional context, tips, or guidance for the implementer.

## Content Guidelines

### Actionability

Every task must be actionable. The implementer should be able to read
the task specification and know exactly what to do without requiring
additional clarification.

### Specificity

- Reference exact file paths, function names, and module locations.
- Specify exact code changes where possible.
- Define clear boundaries of what the task does and does not cover.

### Testability

Each acceptance criterion must be objectively verifiable:

- Code compiles without errors.
- Specific test cases pass.
- Particular behaviors can be observed.
- Performance metrics are met.

### ASCII-Only Requirement

All content MUST use ASCII characters only.

### Plain Text Headings

Section headings MUST use plain text only.

## Naming Convention for Instances

```
TASK-{YYYYMMDD}-{NN}-{TT}_{slug}.md
```

| Component | Description |
|---|---|
| TASK | Fixed prefix |
| YYYYMMDD | Date of task approval |
| NN | Two-digit initiative sequence number |
| TT | Two-digit task number (01-99) |
| slug | Short hyphenated description (same as initiative) |

### Example

```
TASK-20260722-001-01_add-user-authentication.md
```

### Storage Location

Tasks are stored in:
`docs/repo/agent_runner/sdlc/delivery/tasks/`

## Cross-References

### Related Templates

- **05_BACKLOG_template.md** (SYS-03-BL): Input document.
- **07_IMPL_template.md** (SYS-03-IM): Next document in chain.

### Related Agent Contracts

- AGENT-task-decomposer: Used by sdlc_50 to generate task specs from
  backlog items.

### Related Workflows

- **sdlc_50_implementation_v1**: Produces this document.
- **sdlc_60_execution_v1**: Consumes this document (must be approved).

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields.
- GOVERNANCE_LIFECYCLE.md: Lifecycle state transition rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform metadata extensions.
- VALIDATION_CONTRACT.md: Document validation patterns.
