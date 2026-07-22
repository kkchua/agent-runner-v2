---
template_id: SYS-03-VL
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "SDLC delivery document template for Validation documents"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_templates
> This file is workflow-generated and protected from manual edits.

# SDLC Template: Validation Document (VALID-DOC)

## Purpose

This template defines the structure for approved validation documents
produced by the sdlc_70_validation_v1 workflow. A validation document
(VALID-DOC) records the results of executing the implementation plan
(IMPL-DOC) and validating that the implementation meets the task
specification and acceptance criteria.

The VALID-DOC is the seventh formal artifact in the SDLC delivery chain.
It represents the formal validation that code changes were implemented
correctly and meet the defined quality standards.

## Required Frontmatter (for instances of this template)

Every instance of this template MUST include the following YAML
frontmatter fields at the top of the file:

```
---
template_id: SYS-03-VL
version: "<semver>"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved validation document in SDLC delivery chain"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft" | "approved"
---
```

### Frontmatter Field Rules

| Field | Value | Notes |
|---|---|---|
| template_id | SYS-03-VL | Fixed identifier for this template |
| version | Auto-assigned | Set by sdlc_70 workflow |
| doc_type | workflow_output | Generated workflow output |
| authority | workflow-generated | Produced by sdlc_70 workflow |
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

The workflow MUST add `source_document` referencing the implementation
doc:

```
source_document: "IMPL-{YYYYMMDD}-{NN}-{TT}_{slug}.md"
```

## Required Content Sections

Instances of this template MUST contain the following sections in the
order shown:

### 1. Title

A clear title that identifies this validation document. Should reference
the implementation document it validates.

### 2. Validation Objective

A statement of what was validated and the scope of the validation effort.
Summarize which task and implementation were executed.

### 3. Preflight Check

Results of the preflight validation gate:

- Input documents all present and approved: Pass/Fail.
- Codebase context available: Pass/Fail.
- Required tools and environment ready: Pass/Fail.
- Dependencies satisfied: Pass/Fail.

### 4. Execution Summary

A summary of what was executed:

- Task(s) executed (references to TASK-DOC).
- Implementation(s) followed (references to IMPL-DOC).
- Files created, modified, or deleted.
- Time taken and iteration count.

### 5. Files Reviewed

A list of all files that were reviewed during validation:

- **Created**: Paths of new files created.
- **Modified**: Paths of modified files.
- **Deleted**: Paths of deleted files.
- **Unchanged**: Key files verified to be unchanged (regression check).

### 6. Validation Findings

Detailed findings from the validation process. Each finding MUST include:

- **Finding ID**: Unique identifier (VF-001, VF-002, etc.).
- **Severity**: Critical, Major, Minor, Info.
- **Category**: Functionality, Performance, Security, Style, etc.
- **Description**: What was found.
- **Expected vs Actual**: What was expected vs what was observed.
- **Status**: Pass, Fail, or Not Applicable.

### 7. Acceptance Criteria Verification

For each acceptance criterion from the task specification, record the
verification result:

| Criterion | Status | Evidence |
|---|---|---|
| Criterion 1 | Pass/Fail | Evidence or explanation |
| Criterion 2 | Pass/Fail | Evidence or explanation |

### 8. Test Results

Results of all tests executed:

- **Unit Tests**: Number passed/failed/skipped, coverage percentage.
- **Integration Tests**: Number passed/failed/skipped.
- **Manual Tests**: Steps performed and results.
- **Regression Tests**: Any existing tests that broke.

### 9. Quality Assessment

An overall quality assessment:

- Code quality observations.
- Adherence to coding standards.
- Documentation completeness.
- Test coverage adequacy.
- Potential issues or concerns.

### 10. Issues Found

Any issues discovered during validation:

| Issue ID | Description | Severity | Status |
|---|---|---|---|
| ISS-001 | Description of issue | Critical/Major/Minor | Open/Resolved |

### 11. Conclusion

A final determination:

- **Pass**: All criteria met, implementation validated.
- **Fail**: Criteria not met, requires refinement.
- **Conditional Pass**: Minor issues found but acceptable.

If fail, include specific instructions for what needs to be refined.

## Content Guidelines

### Objectivity

Validation findings should be objective and evidence-based. Each finding
must be verifiable and reproducible.

### Completeness

The validation must cover:

- All acceptance criteria from the task specification.
- All implementation steps from the implementation document.
- Test execution and results.
- Code quality and standards compliance.
- Regression checking.

### Evidence

Each finding should reference specific evidence:

- File paths and line numbers for code issues.
- Test output or log excerpts for test failures.
- Screenshots or command output for manual verification steps.

### ASCII-Only Requirement

All content MUST use ASCII characters only.

### Plain Text Headings

Section headings MUST use plain text only.

## Naming Convention for Instances

```
VALID-{YYYYMMDD}-{NN}_{slug}.md
```

| Component | Description |
|---|---|
| VALID | Fixed prefix |
| YYYYMMDD | Date of validation approval |
| NN | Two-digit initiative sequence number |
| slug | Short hyphenated description (same as initiative) |

### Example

```
VALID-20260722-001_add-user-authentication.md
```

### Storage Location

Validations are stored in:
`docs/repo/agent_runner/sdlc/delivery/validations/`

## Cross-References

### Related Templates

- **07_IMPL_template.md** (SYS-03-IM): Input document.
- **09_REV_template.md** (SYS-03-RV): Next document in chain.

### Related Agent Contracts

- AGENT-reviewer: Used by sdlc_70 to validate the IMPL-DOC.
- AGENT-executor (upstream): Produced the IMPL-DOC in sdlc_60.

### Related Workflows

- **sdlc_70_validation_v1**: Produces this document.
- **sdlc_80_review_v1**: Consumes this document (must be approved).

### Layer 1 Governance References

- METADATA_STANDARD.md: Required frontmatter fields.
- GOVERNANCE_LIFECYCLE.md: Lifecycle state transition rules.

### Layer 2 Platform References

- METADATA_CONTRACT.md: Platform metadata extensions.
- VALIDATION_CONTRACT.md: Document validation patterns.
