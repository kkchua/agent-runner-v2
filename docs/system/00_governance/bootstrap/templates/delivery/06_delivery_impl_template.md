---
template_id: DELIVERY-IMPL-v1
status: active
generated: "2026-07-03T23:30:00+08:00"
workflow: 10_execution_scaffold_v1
step: generate_templates
managed_by: workflow-generated
version: 1.0.0
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Implementation Plan Template

## Metadata

| Field | Value |
|-------|-------|
| **Template ID** | `DELIVERY-IMPL-v1` |
| **Impl ID** | `[IMPL-XXXX-v1]` |
| **Title** | `[Implementation Title]` |
| **Status** | `draft` / `active` / `in-review` / `complete` / `failed` |
| **Task ID** | `[TASK-XXXX-v1]` |
| **Plan ID** | `[PLAN-XXXX-v1]` |
| **Created** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Updated** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Author** | `[Agent or human author]` |
| **Workflow** | `10_execution_scaffold_v1` |
| **Step** | `task_execution_v1` |
| **Managed By** | workflow-generated |
| **Current Profile** | `[Architecture profile]` |
| **Target Profile** | `[Target architecture, if changing]` |
| **Migration Mode** | `[greenfield / incremental / refactoring / legacy-merge]` |

## Implementation Objective

<!-- What this implementation achieves. -->

**Objective**: [What this implementation delivers]

**Task Reference**: [TASK-XXXX-v1]

## Overview

<!-- High-level overview of the implementation approach. -->

### Architecture Profile Context

| Dimension | Value |
|-----------|-------|
| **Current Architecture** | `[Current architecture standard]` |
| **Target Architecture** | `[Target architecture, if changing]` |
| **Migration Mode** | `[greenfield / incremental / refactoring / legacy-merge]` |
| **DDD/EDA Applicability** | `[Applicable / Not applicable — conditional standards]` |

## Changes Overview

<!-- Summary of all changes made in this implementation. -->

| File | Type | Change Type | Description |
|------|------|-------------|-------------|
| `[Path]` | `[source / test / config / doc]` | `[create / modify / delete]` | `[Brief description]` |

## Implementation Steps

<!-- Step-by-step implementation details. -->

| Step | Action | Files Affected | Validation |
|------|--------|---------------|-----------|
| 1 | `[Action]` | `[Files]` | `[Check]` |
| 2 | `[Action]` | `[Files]` | `[Check]` |

## Code Changes

<!-- Detailed code changes organized by file. -->

### `[file_path]`

**Change Type**: `[create / modify / delete]`

**Before**:
```
[Relevant code before change or description]
```

**After**:
```
[Relevant code after change or description]
```

**Rationale**: [Why this change was made]

## Documentation Update Plan

<!-- Plan for keeping documentation synchronized with code changes. -->

### Documentation Updates Required

| Document | Path | Update Type | Priority | Status |
|----------|------|-------------|----------|--------|
| `[Document name]` | `[Path]` | `[create / update / remove]` | `[P1 / P2 / P3]` | `[pending / in-progress / complete]` |

### Documentation Update Steps

| Step | Document | Action | Validation |
|------|----------|--------|-----------|
| 1 | `[Doc path]` | `[Update module doc]` | `[Verify template ID and status]` |
| 2 | `[Doc path]` | `[Update inventory]` | `[Verify file count and status]` |
| 3 | `[Doc path]` | `[Create change record]` | `[Verify cross-references]` |

### Stale Documentation Detection

| Potentially Stale Doc | Reason for Review | Action |
|----------------------|-------------------|--------|
| `[Path]` | `[Reason content may be outdated]` | `[Update / Remove / Keep]` |

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|-----------|
| `[Description]` | `[Low / Medium / High]` | `[Low / Medium / High]` | `[Mitigation approach]` |

## Validation Criteria

<!-- How to verify the implementation is correct. -->

### Code Validation
- [ ] Code compiles and passes linting
- [ ] All tests pass (existing and new)
- [ ] No regression in existing functionality
- [ ] Edge cases are handled

### Documentation Validation
- [ ] All affected module docs are updated
- [ ] All affected component docs are updated
- [ ] Inventory is refreshed
- [ ] Change record is created
- [ ] No stale documentation remains

### Integration Validation
- [ ] Changes integrate cleanly with existing code
- [ ] API contracts are maintained or versioned
- [ ] Cross-references in docs are valid

## Notes

<!-- Additional context, decisions, or references. -->
