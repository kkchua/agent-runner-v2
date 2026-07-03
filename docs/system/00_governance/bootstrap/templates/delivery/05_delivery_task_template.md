---
template_id: DELIVERY-TASK-v1
status: active
generated: "2026-07-03T23:30:00+08:00"
workflow: 10_execution_scaffold_v1
step: generate_templates
managed_by: workflow-generated
version: 1.0.0
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Task Template

## Metadata

| Field | Value |
|-------|-------|
| **Template ID** | `DELIVERY-TASK-v1` |
| **Task ID** | `[TASK-XXXX-v1]` |
| **Title** | `[Task Title]` |
| **Status** | `pending` / `blocked` / `active` / `in-review` / `complete` / `failed` / `skipped` |
| **Priority** | `P1` (critical) / `P2` (high) / `P3` (normal) |
| **Plan ID** | `[PLAN-XXXX-v1]` |
| **Task Graph ID** | `[TASK-GRAPH-XXXX-v1]` |
| **Created** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Updated** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Author** | `[Agent or human author]` |
| **Assignee** | `[Agent role or human]` |
| **Workflow** | `10_execution_scaffold_v1` |
| **Step** | `task_execution_v1` |
| **Managed By** | workflow-generated |
| **Current Profile** | `[Architecture profile]` |
| **Target Profile** | `[Target architecture, if changing]` |
| **Migration Mode** | `[greenfield / incremental / refactoring / legacy-merge]` |

## Objective

<!-- What this task achieves. -->

**Objective**: [What this task accomplishes]

**Task Type**: `[code / doc / config / review / refactor]`

## Task Description

<!-- Detailed description of the task. -->

[Provide a clear, actionable description of what needs to be done.]

## Inputs

<!-- What this task needs to start. -->

| Input | Source | Description |
|-------|--------|-------------|
| `[Input name]` | `[File / Initiative / Plan / Task Graph]` | `[Description]` |

### Originating References

| Reference Type | ID | Path |
|---------------|----|------|
| **Plan** | `[PLAN-XXXX-v1]` | `[path to plan document]` |
| **Task Graph** | `[TASK-GRAPH-XXXX-v1]` | `[path to task graph document]` |

## Outputs

<!-- What this task produces. -->

| Output | Type | Path | Description |
|--------|------|------|-------------|
| `[Output name]` | `[file / doc / config]` | `[Path]` | `[Description]` |

## Acceptance Criteria

<!-- Conditions that must be met for the task to be considered complete. -->

- [ ] `[Criterion 1]`
- [ ] `[Criterion 2]`
- [ ] All code changes are validated
- [ ] All documentation is synchronized
- [ ] Review gate passed

## Execution Steps

<!-- Step-by-step instructions for completing the task. -->

| Step | Action | Output | Validation |
|------|--------|--------|-----------|
| 1 | `[Action]` | `[Output]` | `[Check]` |
| 2 | `[Action]` | `[Output]` | `[Check]` |

## Validation Criteria

<!-- How to verify the task output is correct. -->

- [ ] Code compiles/passes linting
- [ ] Tests pass (existing and new)
- [ ] Documentation is updated and consistent
- [ ] No regression in existing functionality
- [ ] Validation record exists in sidecar

## Documentation Impact

<!-- Deterministic documentation obligations and validation expectations. -->

### Required Documentation Updates

| Document | Path | Update Type | Status |
|----------|------|-------------|--------|
| `[Document name]` | `[Path]` | `[create / update / remove]` | `[pending / complete]` |

### Documentation Obligations

- [ ] **Module docs**: Update `docs/codebase/02_modules/` for any changed modules
- [ ] **Component docs**: Update `docs/codebase/03_components/` for any changed components
- [ ] **Inventory**: Update `docs/codebase/01_inventory/codebase_inventory.md`
- [ ] **Change record**: Create entry in `docs/codebase/04_changes/`
- [ ] **Cross-references**: Verify all cross-references remain valid

### Documentation Validation Expectations

| Validation | Check | Status |
|------------|-------|--------|
| Template ID consistency | All docs use registry template IDs | `[ ]` |
| Status currency | All statuses reflect current state | `[ ]` |
| Cross-reference validity | All links resolve | `[ ]` |
| Stale content removal | Outdated content is removed | `[ ]` |

## Dependencies

| Type | ID | Description | Status | Blocker |
|------|----|-------------|--------|---------|
| `[task / initiative / external]` | `[ID]` | `[Description]` | `[Status]` | `[Yes / No]` |

## Notes

<!-- Additional context, decisions, or references. -->
