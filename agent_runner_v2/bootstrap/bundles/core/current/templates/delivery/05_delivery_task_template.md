---
title: Delivery Task Template
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
created: 2026-07-04
template_id: DELIVERY-TASK-v1
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Task Template

> Artifact key: `DELIVERY_TASK_TEMPLATE`

## Metadata

| Field | Value |
|---|---|
| Template ID | `DELIVERY-TASK-v1` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_templates` |
| Scope | Universal baseline — applies to all governed repositories |
| Status | `active` |
| Last Verified | 2026-07-04 |

This template defines the canonical structure for an atomic delivery task. Every task artifact must conform to this structure.

---

## Instance Preamble

```yaml
---
title: Task — {TASK_ID}
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: task_execution_v1
created: {DATE}
template_id: DELIVERY-TASK-v1
task_id: {TASK_ID}
plan_id: {PLAN_ID}
graph_id: {GRAPH_ID}
initiative_id: {INITIATIVE_ID}
status: pending
current_profile: {CURRENT_PROFILE}
target_profile: {TARGET_PROFILE}
migration_mode: {MIGRATION_MODE}
---
```

## Metadata

| Field | Value |
|---|---|
| Task ID | `{TASK_ID}` |
| Plan ID | `{PLAN_ID}` |
| Task Graph ID | `{GRAPH_ID}` |
| Initiative ID | `{INITIATIVE_ID}` |
| Created | `{DATE}` |
| Author / Agent | Task Decomposer |
| Assigned To | `{AGENT_ROLE}` |
| Status | `pending` / `in_progress` / `review` / `approved` / `rejected` |
| Current Architecture Profile | `{CURRENT_PROFILE}` |
| Target Architecture Profile | `{TARGET_PROFILE}` |
| Migration Mode | `{MIGRATION_MODE}` |

## Objective

| Field | Value |
|---|---|
| Objective | `{OBJECTIVE}` |
| Success Definition | `{WHAT_DONE_LOOKS_LIKE}` |

## Task Description

| Field | Value |
|---|---|
| Summary | `{ONE_PARAGRAPH_SUMMARY}` |
| Detailed Description | `{DETAILED_DESCRIPTION}` |
| Context / Background | `{CONTEXT}` |

## Inputs

| Input | Source | Path / Reference |
|---|---|---|
| Source Plan | `DELIVERY_PLAN_TEMPLATE` | `{PLAN_PATH}` |
| Source Task Graph | `DELIVERY_TASK_GRAPH_TEMPLATE` | `{GRAPH_PATH}` |
| {INPUT} | {SOURCE} | {PATH} |

**Note:** This task explicitly references plan `{PLAN_ID}` and task graph `{GRAPH_ID}` as its origin.

## Outputs

| Output | Type | Path | Status |
|---|---|---|---|
| `{OUTPUT}` | `code` / `doc` / `config` / `sidecar` | `{PATH}` | `pending` |

## Acceptance Criteria

| # | Criterion | Verification Method |
|---|---|---|
| 1 | {CRITERION} | {METHOD} |

## Execution Steps

| Step | Description | Expected Output | Verification |
|---|---|---|---|
| 1 | {DESCRIPTION} | {OUTPUT} | {METHOD} |
| 2 | {DESCRIPTION} | {OUTPUT} | {METHOD} |

## Validation Criteria

| # | Criterion | Type | Method |
|---|---|---|---|
| 1 | {CRITERION} | `code` / `doc` / `sidecar` | {METHOD} |
| 2 | Documentation impact section is complete | `doc` | Manual review |
| 3 | Sidecar contract satisfied | `sidecar` | `validate_delivery_docs` |

## Documentation Impact

This section is **mandatory** for every task instance. "No documentation impact" is a valid answer but must be stated explicitly.

| Field | Value |
|---|---|
| Documentation Required | `yes` / `no` |
| Impact Type | `create` / `update` / `retire` / `none` |

### Documentation Actions

| Action | Document Path | Type | Description |
|---|---|---|---|
| {ACTION} | `{PATH}` | `create` / `update` / `retire` | {DESCRIPTION} |

### Documentation Obligations

| Obligation | Scope | Verification |
|---|---|---|
| {OBLIGATION} | {SCOPE} | {METHOD} |

### Validation Expectations for Documentation

| Expectation | Verification Method | Gate |
|---|---|---|
| {EXPECTATION} | {METHOD} | `{GATE_TYPE}` |

## Dependencies

| Dependency | Type | Status | Notes |
|---|---|---|---|
| Plan `{PLAN_ID}` | `origin` | `approved` | Source plan for this task |
| Task Graph `{GRAPH_ID}` | `origin` | `approved` | Source task graph for this task |
| {DEPENDENCY} | `blocking` / `advisory` | {STATUS} | {NOTES} |

## Notes

- This task is part of plan `{PLAN_ID}` and task graph `{GRAPH_ID}`.
- Documentation obligations in this task MUST be fulfilled before the task can advance to `approved` status.
- If documentation impact is `none`, the "No documentation impact" statement MUST appear in the Documentation Impact section.
- {NOTE_2}
