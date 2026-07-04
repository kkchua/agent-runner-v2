---
title: Delivery Implementation Template
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
created: 2026-07-04
template_id: DELIVERY-IMPL-v1
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Implementation Template

> Artifact key: `DELIVERY_IMPL_TEMPLATE`

## Metadata

| Field | Value |
|---|---|
| Template ID | `DELIVERY-IMPL-v1` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_templates` |
| Scope | Universal baseline — applies to all governed repositories |
| Status | `active` |
| Last Verified | 2026-07-04 |

This template defines the canonical structure for a per-task implementation plan. Every implementation plan artifact must conform to this structure.

---

## Instance Preamble

```yaml
---
title: Implementation Plan — {IMPL_ID}
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: task_execution_v1
created: {DATE}
template_id: DELIVERY-IMPL-v1
impl_id: {IMPL_ID}
task_id: {TASK_ID}
plan_id: {PLAN_ID}
initiative_id: {INITIATIVE_ID}
status: draft
current_profile: {CURRENT_PROFILE}
target_profile: {TARGET_PROFILE}
migration_mode: {MIGRATION_MODE}
---
```

## Metadata

| Field | Value |
|---|---|
| Implementation Plan ID | `{IMPL_ID}` |
| Task ID | `{TASK_ID}` |
| Plan ID | `{PLAN_ID}` |
| Initiative ID | `{INITIATIVE_ID}` |
| Created | `{DATE}` |
| Author / Agent | Impl Planner |
| Status | `draft` / `approved` / `rejected` |
| Current Architecture Profile | `{CURRENT_PROFILE}` |
| Target Architecture Profile | `{TARGET_PROFILE}` |
| Migration Mode | `{MIGRATION_MODE}` |

## Implementation Objective

| Field | Value |
|---|---|
| Objective | `{OBJECTIVE}` |
| Derived From Task | `{TASK_ID}` |
| Success Definition | `{WHAT_DONE_LOOKS_LIKE}` |

## Overview

| Field | Value |
|---|---|
| Approach | `{APPROACH_DESCRIPTION}` |
| Key Design Decisions | `{DECISIONS}` |
| Constraints | `{CONSTRAINTS}` |

## Changes Overview

| Change ID | File / Module | Change Type | Description |
|---|---|---|---|
| `{CHANGE_ID}` | `{PATH}` | `create` / `modify` / `delete` | `{DESCRIPTION}` |

## Implementation Steps

| Step | Description | Files Affected | Expected Output | Verification |
|---|---|---|---|---|
| 1 | {DESCRIPTION} | `{PATHS}` | {OUTPUT} | {METHOD} |
| 2 | {DESCRIPTION} | `{PATHS}` | {OUTPUT} | {METHOD} |

## Code Changes

### Change 1: `{CHANGE_ID}`

| Field | Value |
|---|---|
| File | `{FILE_PATH}` |
| Type | `create` / `modify` / `delete` |
| Description | `{DESCRIPTION}` |
| Diff Summary | `{SUMMARY}` |

```diff
# Expected diff outline
+ {ADDED_LINE}
- {REMOVED_LINE}
```

### Change N: `{CHANGE_ID}`

(Repeat structure for each code change)

## Documentation Update Plan

This section is **mandatory** for every implementation plan. It describes how documentation will be updated alongside code changes.

| Field | Value |
|---|---|
| Documentation Update Required | `yes` / `no` |
| Update Strategy | `{STRATEGY}` |

### Documentation Actions

| Action | Document Path | Type | Description | Timing |
|---|---|---|---|---|
| {ACTION} | `{PATH}` | `create` / `update` / `retire` | {DESCRIPTION} | `before_code` / `with_code` / `after_code` |

### Module Doc Freshness

| Module | Doc Path | Action Required | Verification |
|---|---|---|---|
| `{MODULE}` | `{DOC_PATH}` | `update` / `verify_current` / `create` | {METHOD} |

### Documentation-Code Synchronization

| Code Change | Documentation Change | Synchronization Rule |
|---|---|---|
| `{CODE_CHANGE_ID}` | `{DOC_ACTION}` | {RULE} |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| {RISK} | {LOW/MED/HIGH} | {LOW/MED/HIGH} | {MITIGATION} | `{OWNER}` |

### Documentation Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Module doc drift after code change | Medium | Medium | Validate via `validate_codebase_docs` |
| Stale guidance in existing docs | {LEVEL} | {LEVEL} | {MITIGATION} |

## Validation Criteria

| # | Criterion | Type | Method |
|---|---|---|---|
| 1 | {CRITERION} | `code` | {METHOD} |
| 2 | Documentation update plan executed | `doc` | Manual review |
| 3 | Sidecar contract satisfied | `sidecar` | `validate_delivery_docs` |
| 4 | Module docs fresh for all touched modules | `doc` | `validate_codebase_docs` |

## Notes

- This implementation plan is derived from task `{TASK_ID}` and plan `{PLAN_ID}`.
- The Documentation Update Plan MUST be executed alongside code changes, not deferred.
- If no documentation updates are required, the Documentation Update Plan MUST state "No documentation updates required" explicitly.
- {NOTE_2}
