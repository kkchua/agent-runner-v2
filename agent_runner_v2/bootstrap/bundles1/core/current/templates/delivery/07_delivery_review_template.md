---
template_id: "DELIVERY-REV-v1"
title: "Delivery Review Template"
status: "active"
generated: "2026-07-09T10:35:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "07_generate_templates"
change_id: "10SCAFFOLD-20260708-8a4445fc"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Metadata

- **Template ID**: DELIVERY-REV-v1
- **Artifact Key**: `DELIVERY_REVIEW_TEMPLATE`
- **Version**: 1.0
- **Owner**: Task Execution Workflow (Review Step)
- **Purpose**: Covers review scope, summary, findings, code quality assessment, documentation compliance, verdict, resolution tracker, and notes for systematic code and documentation review

# Review Scope

**Implementation Reference**: [Link to DELIVERY_IMPL_TEMPLATE being reviewed]

**Task Reference**: [Link to parent DELIVERY_TASK_TEMPLATE]

**Reviewer**: [Name or role of reviewer]

**Review Date**: [Date review was conducted]

**Review Type**: [Code review / Documentation review / Combined review]

## Scope Boundaries

### In Scope

- [List specific files, modules, or documentation included in this review]
- [Example: "All Python files modified in implementation"]
- [Example: "Module documentation for changed components"]

### Out of Scope

- [List items explicitly excluded from this review]
- [Example: "Unchanged legacy code not touched by this implementation"]
- [Example: "Third-party dependencies not modified"]

## Review Criteria

[List criteria used to evaluate the implementation]

- [Criterion 1: e.g., "Code follows project conventions"]
- [Criterion 2: e.g., "No hardcoded paths in core modules"]
- [Criterion 3: e.g., "Documentation reflects current state"]
- [Criterion 4: e.g., "Tests cover new functionality"]

# Summary

## Overall Assessment

[Provide 2-3 sentence summary of overall review outcome]

**Verdict Preview**: [APPROVED / APPROVED_WITH_COMMENTS / REJECTED / NEEDS_MAJOR_CHANGES]

## Change Summary

[Brief description of what was changed and why]

| Category | Count | Notes |
|----------|-------|-------|
| Files Modified | [N] | [Brief note] |
| Lines Added | [+N] | [Brief note] |
| Lines Removed | [-N] | [Brief note] |
| New Modules | [N] | [Brief note] |
| Documentation Updated | [N] | [Brief note] |

## Key Strengths

[List notable positive aspects of the implementation]

1. [Strength 1: e.g., "Clean separation of concerns in new module structure"]
2. [Strength 2: e.g., "Comprehensive test coverage for edge cases"]
3. [Strength 3: e.g., "Documentation updates are thorough and accurate"]

## Key Concerns

[List notable issues or risks identified during review]

1. [Concern 1: e.g., "Hardcoded path found in constants.py update"]
2. [Concern 2: e.g., "Missing error handling for backend API failure"]
3. [Concern 3: e.g., "Documentation example outdated"]

# Findings

## Critical Findings

[List findings that must be addressed before approval]

### Finding C-001: [Finding Title]

**Severity**: CRITICAL

**Location**: `[path/to/file.py:line_number]`

**Description**: [Detailed description of the issue]

**Impact**: [What could go wrong if this is not fixed]

**Recommendation**: [How to fix this issue]

**Status**: [OPEN/RESOLVED]

### Finding C-002: [Finding Title]

**Severity**: CRITICAL

**Location**: `[path/to/file.py:line_number]`

**Description**: [Detailed description of the issue]

**Impact**: [What could go wrong if this is not fixed]

**Recommendation**: [How to fix this issue]

**Status**: [OPEN/RESOLVED]

## High-Priority Findings

[List findings that should be addressed but may not block approval]

### Finding H-001: [Finding Title]

**Severity**: HIGH

**Location**: `[path/to/file.py:line_number]`

**Description**: [Detailed description of the issue]

**Impact**: [What could go wrong if this is not fixed]

**Recommendation**: [How to fix this issue]

**Status**: [OPEN/RESOLVED/WONT_FIX]

## Medium-Priority Findings

[List findings that are nice to have but not urgent]

### Finding M-001: [Finding Title]

**Severity**: MEDIUM

**Location**: `[path/to/file.py:line_number]`

**Description**: [Detailed description of the issue]

**Impact**: [What could go wrong if this is not fixed]

**Recommendation**: [How to fix this issue]

**Status**: [OPEN/RESOLVED/WONT_FIX]

## Low-Priority Findings

[List minor suggestions or observations]

### Finding L-001: [Finding Title]

**Severity**: LOW

**Location**: `[path/to/file.py:line_number]`

**Description**: [Detailed description of the issue]

**Impact**: [Minimal impact, cosmetic or style issue]

**Recommendation**: [Optional improvement suggestion]

**Status**: [OPEN/RESOLVED/WONT_FIX]

# Code Quality Assessment

## Correctness

[Evaluate whether the code does what it claims to do]

**Assessment**: [PASS/FAIL/PARTIAL]

**Observations**:
- [Observation 1: e.g., "Function correctly handles all documented edge cases"]
- [Observation 2: e.g., "Error paths properly covered with appropriate exceptions"]

**Issues Found**: [List any correctness issues from findings above]

## Security

[Evaluate security implications of the changes]

**Assessment**: [PASS/FAIL/PARTIAL]

**Observations**:
- [Observation 1: e.g., "No secrets exposed in code or commits"]
- [Observation 2: e.g., "Input validation present for all external data"]

**Issues Found**: [List any security issues from findings above]

## Maintainability

[Evaluate how easy the code is to understand and modify]

**Assessment**: [PASS/FAIL/PARTIAL]

**Observations**:
- [Observation 1: e.g., "Function names clearly describe their purpose"]
- [Observation 2: e.g., "Complex logic broken into understandable helper functions"]

**Issues Found**: [List any maintainability issues from findings above]

## Performance

[Evaluate performance implications of the changes]

**Assessment**: [PASS/FAIL/N_A]

**Observations**:
- [Observation 1: e.g., "No unnecessary loops or redundant computations"]
- [Observation 2: e.g., "Database queries use appropriate indexes"]

**Issues Found**: [List any performance issues from findings above]

## Conventions

[Evaluate adherence to project coding conventions]

**Assessment**: [PASS/FAIL/PARTIAL]

**Observations**:
- [Observation 1: e.g., "Naming follows project conventions consistently"]
- [Observation 2: e.g., "Import order matches project style guide"]
- [Observation 3: e.g., "No hardcoded paths; all paths reference constants.py"]

**Issues Found**: [List any convention violations from findings above]

# Documentation Compliance

## Documentation Completeness

[Evaluate whether all required documentation has been created or updated]

**Assessment**: [PASS/FAIL/PARTIAL]

**Required Documentation**:
- [ ] Module documentation for all changed modules exists and is updated
- [ ] Codebase inventory reflects current module count
- [ ] Change impact document created for significant changes
- [ ] System documentation updated if architectural changes made

**Observations**:
- [Observation 1: e.g., "All modified modules have corresponding documentation"]
- [Observation 2: e.g., "Change impact document thoroughly describes effects"]

**Issues Found**: [List any missing documentation from findings above]

## Documentation Accuracy

[Evaluate whether documentation accurately reflects the implementation]

**Assessment**: [PASS/FAIL/PARTIAL]

**Observations**:
- [Observation 1: e.g., "Code examples in docs match actual implementation"]
- [Observation 2: e.g., "API signatures in docs match function definitions"]

**Issues Found**: [List any accuracy issues from findings above]

## Documentation Freshness

[Evaluate risk of documentation becoming stale]

**Risk Level**: [LOW/MEDIUM/HIGH]

**Freshness Verification**:
- [Verification method 1: e.g., "Compared doc examples against actual code"]
- [Verification method 2: e.g., "Validated all referenced artifact keys resolve"]

**Stale Guidance Handling**:
- [Describe any documentation identified as potentially stale and handling plan]

## Baseline vs Profile-Specific Documentation

[Distinguish between universal documentation obligations and architecture-profile-specific obligations]

**Baseline (Universal) Compliance**: [PASS/FAIL/PARTIAL]
- [List baseline documentation requirements met or missed]

**Profile-Specific Compliance**: [PASS/FAIL/PARTIAL/N_A]
- [List profile-specific documentation requirements met or missed]

# Verdict

## Overall Verdict

**Decision**: [APPROVED / APPROVED_WITH_COMMENTS / REJECTED / NEEDS_MAJOR_CHANGES]

**Rationale**: [Explain why this verdict was reached]

## Conditions for Approval

[If APPROVED_WITH_COMMENTS or REJECTED, list conditions that must be met]

### Condition 1: [Condition Description]

**Type**: [Must fix / Should fix / Nice to have]

**Details**: [What needs to be done]

**Priority**: [HIGH/MEDIUM/LOW]

### Condition 2: [Condition Description]

**Type**: [Must fix / Should fix / Nice to have]

**Details**: [What needs to be done]

**Priority**: [HIGH/MEDIUM/LOW]

[Continue for all conditions...]

## Re-review Required

**Re-review Needed**: [YES/NO]

**Scope of Re-review**: [What specifically needs re-review after changes]

**Expected Effort**: [S/M/L/XL]

# Resolution Tracker

## Open Items

[List findings or conditions that remain unresolved]

| Item ID | Description | Owner | Due Date | Status |
|---------|-------------|-------|----------|--------|
| [Finding ID] | [Brief description] | [Who will fix] | [When] | OPEN |

## Resolved Items

[List findings or conditions that have been resolved]

| Item ID | Description | Resolution | Resolved By | Date |
|---------|-------------|------------|-------------|------|
| [Finding ID] | [Brief description] | [How it was fixed] | [Who fixed it] | [When] |

## Deferred Items

[List findings or conditions deferred to future work]

| Item ID | Description | Reason for Deferral | Planned For |
|---------|-------------|---------------------|-------------|
| [Finding ID] | [Brief description] | [Why deferred] | [Future task/initiative] |

# Notes

- [Additional context about the review process]
- [Link to related reviews, discussions, or decision logs]
- [Record any deviations from standard review SOP]
- [Note any special considerations for Windows compatibility if applicable]
- [Document reviewer confidence level in findings and verdict]
