---
template_id: "DELIVERY-VAL-v1"
title: "Delivery Validation Template"
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

- **Template ID**: DELIVERY-VAL-v1
- **Artifact Key**: `DELIVERY_VALIDATION_TEMPLATE`
- **Version**: 1.0
- **Owner**: Task Execution Workflow (Validation Step)
- **Purpose**: Validates code changes and documentation synchronization with validation scope, code validation, documentation synchronization validation, validation issues, validation summary, verdict, approval, and notes for systematic quality assurance

# Validation Scope

**Implementation Reference**: [Link to DELIVERY_IMPL_TEMPLATE being validated]

**Review Reference**: [Link to DELIVERY_REVIEW_TEMPLATE if review was conducted]

**Task Reference**: [Link to parent DELIVERY_TASK_TEMPLATE]

**Validator**: [Name or role of validator]

**Validation Date**: [Date validation was conducted]

**Validation Type**: [Automated / Manual / Combined]

## Scope Boundaries

### In Scope

- [List specific validation areas included in this validation]
- [Example: "All Python files modified in implementation"]
- [Example: "Documentation artifacts for changed modules"]
- [Example: "Integration tests for backend API contract"]

### Out of Scope

- [List items explicitly excluded from this validation]
- [Example: "Unchanged legacy code not touched by this implementation"]
- [Example: "Third-party dependencies not modified"]

## Validation Criteria

[List criteria used to validate the implementation]

- [Criterion 1: e.g., "All unit tests pass"]
- [Criterion 2: e.g., "No hardcoded paths in core modules"]
- [Criterion 3: e.g., "Documentation reflects current state"]
- [Criterion 4: e.g., "Meta.json sidecars written for all steps"]

# Code Validation

## Unit Test Validation

[Evaluate whether unit tests pass and cover new functionality]

**Status**: [PASS/FAIL/PARTIAL]

**Test Results**:

| Test Suite | Tests Run | Passed | Failed | Skipped | Coverage |
|------------|-----------|--------|--------|---------|----------|
| [Suite name] | [N] | [N] | [N] | [N] | [XX%] |

**Issues Found**:
- [Issue 1: e.g., "test_new_function.py::test_edge_case failed with AssertionError"]
- [Issue 2: e.g., "Coverage dropped below threshold in modified module"]

**Validation Commands**:
```bash
pytest tests/unit/test_affected_module.py -v --cov=agent_runner_v2
```

## Integration Test Validation

[Evaluate whether integration tests pass and cover critical paths]

**Status**: [PASS/FAIL/PARTIAL/N_A]

**Test Results**:

| Test Suite | Tests Run | Passed | Failed | Skipped | Notes |
|------------|-----------|--------|--------|---------|-------|
| [Suite name] | [N] | [N] | [N] | [N] | [Brief note] |

**Issues Found**:
- [Issue 1: e.g., "test_backend_worker.py failed due to missing backend API"]
- [Issue 2: e.g., "Notification test skipped due to missing Pushover credentials"]

**Validation Commands**:
```bash
pytest tests/integration/test_backend_worker_mode.py -v
```

## Static Analysis Validation

[Evaluate code quality via static analysis tools]

**Status**: [PASS/FAIL/PARTIAL]

**Linting Results**:
- [Tool 1: e.g., "ruff check: 0 errors, 2 warnings"]
- [Tool 2: e.g., "mypy type checking: 0 errors"]

**Hardcoded Path Check**:
- [ ] No hardcoded paths detected in core modules
- [ ] All paths reference constants.py appropriately

**Issues Found**:
- [Issue 1: e.g., "Hardcoded path found in step_runner.py line 123"]
- [Issue 2: e.g., "Unused import in new module"]

**Validation Commands**:
```bash
ruff check agent_runner_v2/
python -m agent_runner_v2.tools.validate_constants --check-hardcoded-paths
```

## Artifact Validation

[Evaluate whether all required artifacts were created and are valid]

**Status**: [PASS/FAIL/PARTIAL]

**Required Artifacts**:

| Artifact | Artifact Key | Exists | Valid | Notes |
|----------|--------------|--------|-------|-------|
| [Artifact name] | [ARTIFACT_KEY] | YES/NO | YES/NO | [Brief note] |
| [Artifact name] | [ARTIFACT_KEY] | YES/NO | YES/NO | [Brief note] |

**Meta.json Sidecar Check**:
- [ ] All step meta.json sidecars exist
- [ ] All sidecars have valid schema_version
- [ ] All sidecars have coder_result with status APPROVED

**Issues Found**:
- [Issue 1: e.g., "meta.json missing for step 03_generate_templates"]
- [Issue 2: e.g., "Sidecar schema_version mismatch"]

## Functional Validation

[Evaluate whether implementation meets functional requirements]

**Status**: [PASS/FAIL/PARTIAL]

**Functional Checks**:

| Check | Expected Result | Actual Result | Status |
|-------|----------------|---------------|--------|
| [Check 1: e.g., "Workflow executes end-to-end"] | [Expected] | [Actual] | PASS/FAIL |
| [Check 2: e.g., "Artifact keys resolve correctly"] | [Expected] | [Actual] | PASS/FAIL |

**Issues Found**:
- [Issue 1: e.g., "Workflow fails at step 05 due to missing input artifact"]
- [Issue 2: e.g., "Placeholder {PROJECT_ANALYSIS} does not resolve"]

# Documentation Synchronization Validation

## Documentation Completeness Validation

[Evaluate whether all required documentation has been created or updated]

**Status**: [PASS/FAIL/PARTIAL]

**Required Documentation Checklist**:

- [ ] Module documentation exists for all changed Python modules
- [ ] Codebase inventory reflects current module count
- [ ] Change impact document created for significant changes
- [ ] System documentation updated if architectural changes made
- [ ] Delivery templates updated if delivery process changed
- [ ] Agent contracts updated if agent roles changed

**Module Documentation Check**:

| Module | Module Doc Exists | Doc Updated | Accuracy Verified |
|--------|-------------------|-------------|-------------------|
| [module_name.py] | YES/NO | YES/NO | YES/NO |
| [module_name.py] | YES/NO | YES/NO | YES/NO |

**Issues Found**:
- [Issue 1: e.g., "Module doc missing for new action module"]
- [Issue 2: e.g., "Codebase inventory still shows old module count"]

## Documentation Accuracy Validation

[Evaluate whether documentation accurately reflects the current implementation]

**Status**: [PASS/FAIL/PARTIAL]

**Accuracy Checks**:

| Documentation | Artifact Key | Examples Match Code | API Signatures Match | References Valid |
|---------------|--------------|---------------------|---------------------|------------------|
| [Doc name] | [ARTIFACT_KEY] | YES/NO | YES/NO | YES/NO |
| [Doc name] | [ARTIFACT_KEY] | YES/NO | YES/NO | YES/NO |

**Verification Methods**:
- [Method 1: e.g., "Compared code examples in docs against actual implementation"]
- [Method 2: e.g., "Validated function signatures in docs match definitions"]
- [Method 3: e.g., "Checked all referenced artifact keys resolve correctly"]

**Issues Found**:
- [Issue 1: e.g., "Code example in module doc uses old API signature"]
- [Issue 2: e.g., "Referenced artifact key {OLD_KEY} no longer exists"]

## Documentation Freshness Validation

[Evaluate risk of documentation becoming stale and verify freshness]

**Freshness Risk Level**: [LOW/MEDIUM/HIGH]

**Last Verified Dates**:

| Documentation | Artifact Key | Last Verified By | Last Verified Date | Next Review Due |
|---------------|--------------|------------------|-------------------|-----------------|
| [Doc name] | [ARTIFACT_KEY] | [Name/Role] | [Date] | [Date] |
| [Doc name] | [ARTIFACT_KEY] | [Name/Role] | [Date] | [Date] |

**Stale Documentation Check**:
- [ ] No documentation marked as superseded without replacement
- [ ] No documentation marked as needs_update without action plan
- [ ] All documentation has owner assigned
- [ ] All documentation has next review date within acceptable window

**Issues Found**:
- [Issue 1: e.g., "Module doc for legacy_module.py marked needs_update 6 months ago"]
- [Issue 2: e.g., "Change impact document has no owner assigned"]

## Stale Guidance Handling Validation

[Evaluate whether stale guidance has been properly handled]

**Status**: [PASS/FAIL/PARTIAL]

**Stale Guidance Inventory**:

| Potentially Stale Doc | Artifact Key | Current Status | Handling Rule Applied | Verification |
|-----------------------|--------------|----------------|----------------------|--------------|
| [Doc name] | [ARTIFACT_KEY] | current/needs_update/pending_review/superseded | [Rule applied] | VERIFIED/NOT_VERIFIED |
| [Doc name] | [ARTIFACT_KEY] | current/needs_update/pending_review/superseded | [Rule applied] | VERIFIED/NOT_VERIFIED |

**Handling Rules Applied**:
- [Rule 1: e.g., "Updated module doc to reflect new function signatures"]
- [Rule 2: e.g., "Marked legacy guide as needs_update with action plan"]
- [Rule 3: e.g., "Superseded old architecture doc with new DDD profile doc"]

**Issues Found**:
- [Issue 1: e.g., "Stale doc marked as current despite major code changes"]
- [Issue 2: e.g., "No handling rule applied to outdated change impact doc"]

## Baseline vs Profile-Specific Documentation Validation

[Distinguish between universal documentation obligations and architecture-profile-specific obligations]

**Baseline (Universal) Compliance**: [PASS/FAIL/PARTIAL]

Baseline Requirements Met:
- [ ] All modified modules have updated documentation
- [ ] Codebase inventory reflects current state
- [ ] Change impact documents created for significant changes
- [ ] Documentation has owner and review schedule

**Profile-Specific Compliance**: [PASS/FAIL/PARTIAL/N_A]

Profile-Specific Requirements Met:
- [ ] [Requirement 1: e.g., "DDD aggregate boundaries documented"]
- [ ] [Requirement 2: e.g., "Event schema registry updated for EDA profile"]
- [ ] [Requirement 3: e.g., "Migration mode documented for transition"]

**Issues Found**:
- [Issue 1: e.g., "DDD profile requires aggregate boundary docs but none found"]
- [Issue 2: e.g., "Baseline requirement met but profile-specific gap identified"]

# Validation Issues

## Critical Issues

[List issues that must be resolved before approval]

### Issue CI-001: [Issue Title]

**Category**: [Code/Documentation/Artifact/Functional]

**Severity**: CRITICAL

**Location**: `[path/to/file.py:line_number]` or `[Artifact Key]`

**Description**: [Detailed description of the issue]

**Impact**: [What could go wrong if this is not fixed]

**Recommendation**: [How to fix this issue]

**Status**: [OPEN/RESOLVED]

## High-Priority Issues

[List issues that should be resolved but may not block approval]

### Issue HI-001: [Issue Title]

**Category**: [Code/Documentation/Artifact/Functional]

**Severity**: HIGH

**Location**: `[path/to/file.py:line_number]` or `[Artifact Key]`

**Description**: [Detailed description of the issue]

**Impact**: [What could go wrong if this is not fixed]

**Recommendation**: [How to fix this issue]

**Status**: [OPEN/RESOLVED/WONT_FIX]

## Medium-Priority Issues

[List issues that are nice to have but not urgent]

### Issue MI-001: [Issue Title]

**Category**: [Code/Documentation/Artifact/Functional]

**Severity**: MEDIUM

**Location**: `[path/to/file.py:line_number]` or `[Artifact Key]`

**Description**: [Detailed description of the issue]

**Impact**: [Minimal impact, improvement opportunity]

**Recommendation**: [Optional improvement suggestion]

**Status**: [OPEN/RESOLVED/WONT_FIX]

# Validation Summary

## Overall Statistics

| Category | Total Checks | Passed | Failed | Partial | N/A |
|----------|--------------|--------|--------|---------|-----|
| Code Validation | [N] | [N] | [N] | [N] | [N] |
| Documentation Validation | [N] | [N] | [N] | [N] | [N] |
| **Total** | **[N]** | **[N]** | **[N]** | **[N]** | **[N]** |

## Pass Rate

**Overall Pass Rate**: [XX%]

**Code Validation Pass Rate**: [XX%]

**Documentation Validation Pass Rate**: [XX%]

## Key Findings

**Strengths**:
- [Strength 1: e.g., "All unit tests pass with good coverage"]
- [Strength 2: e.g., "No hardcoded paths detected in core modules"]

**Weaknesses**:
- [Weakness 1: e.g., "Module documentation incomplete for new modules"]
- [Weakness 2: e.g., "Stale guidance not properly handled"]

# Verdict

## Overall Verdict

**Decision**: [APPROVED / APPROVED_WITH_CONDITIONS / REJECTED]

**Rationale**: [Explain why this verdict was reached based on validation results]

## Conditions for Approval

[If APPROVED_WITH_CONDITIONS or REJECTED, list conditions that must be met]

### Condition 1: [Condition Description]

**Type**: [Must fix / Should fix / Nice to have]

**Details**: [What needs to be done to satisfy this condition]

**Priority**: [HIGH/MEDIUM/LOW]

**Validation Method**: [How to verify this condition is met]

### Condition 2: [Condition Description]

**Type**: [Must fix / Should fix / Nice to have]

**Details**: [What needs to be done to satisfy this condition]

**Priority**: [HIGH/MEDIUM/LOW]

**Validation Method**: [How to verify this condition is met]

[Continue for all conditions...]

## Re-validation Required

**Re-validation Needed**: [YES/NO]

**Scope of Re-validation**: [What specifically needs re-validation after fixes]

**Expected Effort**: [S/M/L/XL]

# Approval

## Approver Information

**Approver Name**: [Name or role of approver]

**Approval Date**: [Date approval was granted]

**Approval Basis**: [What validation results informed this approval decision]

## Approval Statement

[Provide formal approval statement]

"I approve this implementation and documentation synchronization based on the validation results documented above. All critical and high-priority issues have been resolved or appropriately deferred. The implementation meets functional requirements and documentation reflects the current state."

**Signed**: [Approver signature or identifier]

## Post-Approval Actions

[List actions to take after approval]

- [ ] [Action 1: e.g., "Merge changes to main branch"]
- [ ] [Action 2: e.g., "Update project changelog"]
- [ ] [Action 3: e.g., "Notify stakeholders of changes"]

# Notes

- [Additional context about the validation process]
- [Link to related validations, discussions, or decision logs]
- [Record any deviations from standard validation SOP]
- [Note any special considerations for Windows compatibility if applicable]
- [Document validator confidence level in findings and verdict]
- [Note any temporary workarounds accepted with plans for future cleanup]
