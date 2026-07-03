---
template_id: DELIVERY-TASK-GRAPH-v1
status: active
generated: "2026-07-03T23:30:00+08:00"
workflow: 10_execution_scaffold_v1
step: generate_templates
managed_by: workflow-generated
version: 1.0.0
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Task Graph Template

## Metadata

| Field | Value |
|-------|-------|
| **Template ID** | `DELIVERY-TASK-GRAPH-v1` |
| **Graph ID** | `[TASK-GRAPH-XXXX-v1]` |
| **Title** | `[Task Graph Title]` |
| **Status** | `draft` / `proposed` / `approved` / `active` / `completed` / `abandoned` |
| **Plan ID** | `[PLAN-XXXX-v1]` |
| **Created** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Updated** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Author** | `[Agent or human author]` |
| **Workflow** | `10_execution_scaffold_v1` |
| **Step** | `delivery_planning_v1` |
| **Managed By** | workflow-generated |

## Task Graph Objective

<!-- State what this task graph achieves. -->

**Objective**: [What this task graph accomplishes]

**Plan Reference**: [PLAN-XXXX-v1]

## Task Graph

<!-- Define tasks as nodes in a directed acyclic graph. -->

| Task ID | Description | Type | Priority | Depends On | Status |
|---------|-------------|------|----------|------------|--------|
| `[TASK-XXXX]` | `[Description]` | `[code / doc / config / review]` | `[P1/P2/P3]` | `[Dependencies]` | `[pending / blocked / active / complete]` |

### Task Types

| Type | Description | Documentation Required |
|------|-------------|----------------------|
| `code` | Source code changes | Yes — module and component docs |
| `doc` | Documentation-only changes | Yes — inventory update |
| `config` | Configuration changes | Yes — inventory update |
| `review` | Review and validation | Yes — review record |

## Execution Flow

<!-- Define the execution order respecting dependencies. -->

### Phase 1 — `[Phase Name]`
<!-- Tasks that can execute in parallel (no inter-dependencies). -->

| Task ID | Description | Status |
|---------|-------------|--------|
| `[TASK-XXXX]` | `[Description]` | `[Status]` |

### Phase 2 — `[Phase Name]`

| Task ID | Description | Status |
|---------|-------------|--------|
| `[TASK-XXXX]` | `[Description]` | `[Status]` |

## Documentation Workstream

<!-- Document workstream coverage for documentation tasks. -->

### Documentation Tasks

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| `[TASK-XXXX]` | `[Documentation task]` | `[Code task that triggers it]` | `[Status]` |

### Documentation Coverage Matrix

| Source Area | Module Doc | Component Doc | Inventory Update | Change Record | Status |
|-------------|-----------|---------------|-----------------|---------------|--------|
| `[Area]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[Status]` |

### Workstream Rules
- Every code task MUST have a corresponding documentation task.
- Documentation tasks execute in parallel with or immediately after their code tasks.
- The documentation workstream is complete only when ALL code tasks have synchronized documentation.

## Success Criteria

- [ ] All tasks in the graph are completed
- [ ] All dependencies are satisfied
- [ ] Documentation workstream is complete
- [ ] No orphaned code changes without documentation
- [ ] Execution flow was followed (or deviations were documented)

## Cross-References

- **Plan**: `[PLAN-XXXX-v1]` — `docs/delivery/plans/[PLAN-ID].md`
- **Initiative**: `[INIT-XXXX-v1]` — `docs/delivery/initiatives/[INIT-ID].md`

## Notes

<!-- Additional context, decisions, or references. -->
