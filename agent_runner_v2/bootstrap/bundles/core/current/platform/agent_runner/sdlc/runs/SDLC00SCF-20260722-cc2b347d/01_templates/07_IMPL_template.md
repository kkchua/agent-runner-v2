---
template_id: SYS-03-IM
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for Implementation documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Implementation Document (IMPL-DOC)

## Purpose

This template defines the structure for approved implementation
documents produced by the sdlc_60_execution_v1 workflow. An
implementation document (IMPL-DOC) records the execution of a task
specification (TASK-DOC), documenting what was implemented, how it was
implemented, and the results of implementation.

The IMPL-DOC is the sixth formal artifact in the SDLC delivery chain. It
represents the record of actual code changes made during task execution.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-IM
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved implementation document in SDLC delivery chain"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft" | "approved"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-IM | Fixed identifier for this template |
| version | Auto-assigned | Set by sdlc_60 workflow |
| doc_type | workflow_output | Generated workflow output |
| authority | workflow-generated | Produced by sdlc_60 workflow |
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

The workflow MUST add `source_document` referencing the task spec:

```
source_document: "TASK-{YYYYMMDD}-{NN}-{TT}_{slug}.md"
```

## Required Content Sections

Instances of this template MUST contain the following sections in the
order shown:

### 1. Title

A clear title that identifies this implementation document. Should
reference the task specification it implements.

### 2. Implementation Summary

A concise summary of what was implemented:

- Task reference (TASK-DOC file path).
- Brief description of the implementation approach.
- Key decisions made during implementation.

### 3. Files Created

A list of all new files created during implementation:

- **File Path**: Full path relative to repository root.
- **Purpose**: Why this file was created.
- **Key Contents**: Major functions, classes, or components.

### 4. Files Modified

A list of all existing files modified during implementation:

- **File Path**: Full path relative to repository root.
- **Changes Made**: What was changed and why.
- **Scope of Changes**: Major or minor modifications.

### 5. Files Deleted

A list of any files deleted during implementation:

- **File Path**: Full path relative to repository root.
- **Reason**: Why the file was deleted.

### 6. Implementation Details

Detailed description of the implementation:

- **Architecture**: How the implementation fits into the existing
  architecture.
- **Design Decisions**: Key design choices and trade-offs.
- **Algorithms or Logic**: Non-trivial algorithms or logic implemented.
- **Configuration Changes**: Any configuration or environment changes.

### 7. Acceptance Criteria Verification

For each acceptance criterion from the task specification, record how
it was satisfied:

| Criterion | Status | Evidence |
|---|---|---|
| Criterion 1 from TASK-DOC | Met | How it was satisfied |
| Criterion 2 from TASK-DOC | Met | How it was satisfied |

### 8. Test Results

Results of tests executed during implementation:

- **Tests Added**: New tests created.
- **Tests Passed**: Existing and new tests that pass.
- **Tests Failed**: Any tests that fail (with explanation).
- **Coverage**: Code coverage metrics if available.

### 9. Implementation Notes

Any notes, observations, or issues encountered:

- Deviations from the task specification and why.
- Unexpected challenges or discoveries.
- Recommendations for future work.

## Content Guidelines

### Accuracy

All file paths, code references, and implementation details must be
accurate and verifiable. The IMPL-DOC serves as the authoritative record
of what was actually done.

### Completeness

Every acceptance criterion from the TASK-DOC must be addressed. If a
criterion was not fully met, document the gap and why.

### Traceability

The implementation must be traceable back to the task specification and,
through it, to the requirements and initiative.

### ASCII-Only Requirement

All content MUST use ASCII characters only.

### Plain Text Headings

Section headings MUST use plain text only.

## Naming Convention for Instances

```
IMPL-{YYYYMMDD}-{NN}-{TT}_{slug}.md
```

| Component | Description |
|---|---|
| IMPL | Fixed prefix |
| YYYYMMDD | Date of implementation approval |
| NN | Two-digit initiative sequence number |
| TT | Two-digit task number (01-99) |
| slug | Short hyphenated description (same as initiative) |

### Example

```
IMPL-20260722-001-01_add-user-authentication.md
```

### Storage Location

Implementations are stored in:
`docs/repo/agent_runner/sdlc/delivery/implementations/`

## Cross-References

### Related Templates

- **06_TASK_template.md** (SYS-03-TK): Input document.
- **08_VALID_template.md** (SYS-03-VL): Next document in chain.

### Related Agent Contracts

- AGENT-executor: Used by sdlc_60 to execute the task and produce this
  document.

### Related Workflows

- **sdlc_60_execution_v1**: Produces this document.
- **sdlc_70_validation_v1**: Consumes this document (must be approved).

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields.
- GOVERNANCE_LIFECYCLE.md: Lifecycle state transition rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform metadata extensions.
- VALIDATION_CONTRACT.md: Document validation patterns.
