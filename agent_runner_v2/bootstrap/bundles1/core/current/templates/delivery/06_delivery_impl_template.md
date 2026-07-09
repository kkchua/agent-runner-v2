---
template_id: "DELIVERY-IMPL-v1"
title: "Delivery Implementation Template"
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

- **Template ID**: DELIVERY-IMPL-v1
- **Artifact Key**: `DELIVERY_IMPL_TEMPLATE`
- **Version**: 1.0
- **Owner**: Task Execution Workflow
- **Purpose**: Details implementation objective, overview, changes overview, implementation steps, code changes, documentation update plan, risk assessment, validation criteria, and notes for deterministic code generation

# Implementation Objective

**Task Reference**: [Link to DELIVERY_TASK_TEMPLATE that originated this implementation]

**Task Graph Reference**: [Link to parent DELIVERY_TASK_GRAPH_TEMPLATE if applicable]

**Plan Reference**: [Link to parent DELIVERY_PLAN_TEMPLATE if applicable]

**Implementation Summary**: [2-3 sentence overview of what this implementation accomplishes]

**Current Profile**: [Describe current architecture standard in use, if applicable]

**Target Profile**: [Describe target architecture standard being adopted, if applicable]

**Migration Mode**: [If transitioning between profiles, describe migration approach, if applicable]

# Overview

## Problem Statement

[Describe the problem or requirement this implementation addresses]

## Solution Approach

[Describe the high-level approach to solving the problem]

## Key Design Decisions

[List major design decisions made during implementation planning]

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| [Decision 1] | [Why this approach was chosen] | [Other approaches considered and why rejected] |
| [Decision 2] | [Why this approach was chosen] | [Other approaches considered and why rejected] |

# Changes Overview

## Files Modified

[List all files that will be modified]

| File Path | Change Type | Purpose | Lines Changed (Est.) |
|-----------|-------------|---------|---------------------|
| [path/to/file.py] | new/modified/deleted | [What this change does] | [+X/-Y] |
| [path/to/file.md] | new/modified/deleted | [What this change does] | [+X/-Y] |

## New Modules/Components

[List any new modules or components being introduced]

| Module/Component | Path | Purpose | Dependencies |
|------------------|------|---------|--------------|
| [Module name] | [path/to/module.py] | [What this module does] | [Depends on...] |

## Removed Modules/Components

[List any modules or components being removed]

| Module/Component | Path | Reason for Removal | Migration Plan |
|------------------|------|-------------------|----------------|
| [Module name] | [path/to/module.py] | [Why it's being removed] | [How functionality is replaced/migrated] |

# Implementation Steps

## Step 1: [Step Name]

### Objective

[What this step accomplishes]

### Changes

[Detailed description of code changes in this step]

**File**: `[path/to/file.py]`

```python
# Code changes or pseudocode
def new_function():
    """Implementation details"""
    pass
```

### Validation

[How to verify this step succeeded]

- [ ] [Validation check 1]
- [ ] [Validation check 2]

## Step 2: [Step Name]

### Objective

[What this step accomplishes]

### Changes

[Detailed description of code changes in this step]

**File**: `[path/to/file.py]`

```python
# Code changes or pseudocode
def another_function():
    """Implementation details"""
    pass
```

### Validation

[How to verify this step succeeded]

- [ ] [Validation check 1]
- [ ] [Validation check 2]

[Continue for all implementation steps...]

# Code Changes

## Detailed Diffs

[Provide detailed before/after comparisons for significant changes]

### Change 1: [Change Description]

**File**: `[path/to/file.py]`

**Before**:
```python
# Original code
```

**After**:
```python
# Updated code
```

**Rationale**: [Why this change was made]

### Change 2: [Change Description]

**File**: `[path/to/file.py]`

**Before**:
```python
# Original code
```

**After**:
```python
# Updated code
```

**Rationale**: [Why this change was made]

[Continue for all significant changes...]

## Constants and Path Updates

[Document any updates to centralized constants in `constants.py`]

| Constant Name | Old Value | New Value | Reason |
|---------------|-----------|-----------|--------|
| [CONSTANT_NAME] | [old_value] | [new_value] | [Why this change was needed] |

**Validation**: Ensure no hardcoded paths remain in core modules after these changes.

# Documentation Update Plan

## Affected Documentation

[List all documentation artifacts this implementation affects]

| Documentation | Artifact Key | Action Required | Owner | Priority |
|---------------|--------------|-----------------|-------|----------|
| [Doc name] | [ARTIFACT_KEY] | create/update/retire | [Role] | HIGH/MED/LOW |

## Documentation Update Steps

[Describe how documentation will be updated as part of this implementation]

### Step 1: [Documentation Update Step]

**Artifact**: `[ARTIFACT_KEY]`

**Action**: [create/update/retire]

**Details**: [What needs to be updated and why]

**Validation**: [How to verify documentation accuracy]

### Step 2: [Documentation Update Step]

**Artifact**: `[ARTIFACT_KEY]`

**Action**: [create/update/retire]

**Details**: [What needs to be updated and why]

**Validation**: [How to verify documentation accuracy]

[Continue for all documentation update steps...]

## Documentation Freshness Verification

[Define how documentation freshness will be verified after implementation]

- [Verification method 1: e.g., "Compare code examples in docs against actual implementation"]
- [Verification method 2: e.g., "Validate all referenced artifact keys resolve correctly"]
- [Verification method 3: e.g., "Run documentation sync workflow to detect drift"]

## Stale Guidance Handling

[Identify any documentation that may become stale due to this implementation and define handling rules]

| Potentially Stale Doc | Artifact Key | Handling Rule | Trigger |
|-----------------------|--------------|---------------|---------|
| [Doc name] | [ARTIFACT_KEY] | update/mark_needs_update/supersede | [Condition that triggers this action] |

## Baseline vs Profile-Specific Documentation

[Distinguish between universal documentation obligations and architecture-profile-specific obligations]

**Baseline (Universal)**:
- [List documentation updates required for all implementations]

**Profile-Specific**:
- [List documentation updates required only for specific architecture profiles]

# Risk Assessment

## Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Technical risk description] | LOW/MED/HIGH | LOW/MED/HIGH | [How this risk will be mitigated] |

## Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Operational risk description] | LOW/MED/HIGH | LOW/MED/HIGH | [How this risk will be mitigated] |

## Documentation Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Documentation risk description] | LOW/MED/HIGH | LOW/MED/HIGH | [How this risk will be mitigated] |

## Rollback Plan

[Describe how to revert these changes if necessary]

1. [Step 1: e.g., "git revert <commit-hash>"]
2. [Step 2: e.g., "Restore previous constants.py values"]
3. [Step 3: e.g., "Revert documentation updates"]

# Validation Criteria

## Automated Validation

[List checks that can be automated]

- [ ] [Check 1: e.g., "pytest unit tests pass for affected modules"]
- [ ] [Check 2: e.g., "No hardcoded paths detected in modified files"]
- [ ] [Check 3: e.g., "All artifact key placeholders resolve correctly"]

## Manual Validation

[List checks requiring human judgment]

- [ ] [Check 1: e.g., "Code review approves architectural approach"]
- [ ] [Check 2: e.g., "Documentation clarity and accuracy verified"]
- [ ] [Check 3: e.g., "Integration with existing workflows validated"]

## Validation Commands

[Provide exact commands to run validation]

```bash
# Example validation commands
pytest tests/unit/test_affected_module.py -v
python -m agent_runner_v2.tools.validate_constants --check-hardcoded-paths
ukbe-run-agent run 40_documentation_sync_v1 --dry-run
```

## Success Indicators

[Define observable outcomes that indicate successful implementation]

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] No hardcoded paths in core modules
- [ ] Documentation reflects current state
- [ ] Workflow executes end-to-end without errors

# Notes

- [Additional context, assumptions, or constraints]
- [Link to related implementations, discussions, or decision logs]
- [Record any deviations from standard implementation SOP]
- [Note any special considerations for Windows compatibility if applicable]
- [Document any temporary workarounds that need cleanup later]
