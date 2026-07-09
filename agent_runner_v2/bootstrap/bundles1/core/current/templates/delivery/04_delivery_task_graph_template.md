---
template_id: "DELIVERY-TG-v1"
title: "Delivery Task Graph Template"
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

- **Template ID**: DELIVERY-TG-v1
- **Artifact Key**: `DELIVERY_TASK_GRAPH_TEMPLATE`
- **Version**: 1.0
- **Owner**: Delivery Planning Workflow
- **Purpose**: Maps task dependencies, execution flow, documentation workstream coverage, success criteria, and cross-references for initiative execution

# Task Graph Objective

**Plan Reference**: [Link to parent plan document]

**Initiative Reference**: [Link to originating initiative]

**Graph Summary**: [2-3 sentence overview of what this task graph accomplishes]

**Current Profile**: [Describe current architecture standard in use]

**Target Profile**: [Describe target architecture standard being adopted]

**Migration Mode**: [If transitioning between profiles, describe migration approach]

# Task Graph

## Tasks

[Enumerate all tasks with unique IDs, descriptions, and metadata]

### T-001: [Task Name]

- **Description**: [What this task accomplishes]
- **Effort**: [S/M/L/XL]
- **Agent Role**: [Planner/Executor/Reviewer/etc.]
- **Documentation Impact**: [List documentation artifacts affected]
- **Dependencies**: [List task IDs this depends on, or "None"]

### T-002: [Task Name]

- **Description**: [What this task accomplishes]
- **Effort**: [S/M/L/XL]
- **Agent Role**: [Planner/Executor/Reviewer/etc.]
- **Documentation Impact**: [List documentation artifacts affected]
- **Dependencies**: [List task IDs this depends on, or "None"]

[Continue for all tasks...]

## Dependency Map

[Visualize task dependencies as a directed graph]

```
T-001 → T-002 → T-004
         ↘
           T-003 → T-005
```

## Critical Path

[Identify the longest dependency chain that determines total execution time]

**Critical Path**: T-XXX → T-XXX → T-XXX → ...

**Estimated Total Effort**: [Sum of effort along critical path]

# Execution Flow

## Phase 1: [Phase Name]

[Tasks executed in this phase]

- T-001: [Brief description]
- T-002: [Brief description]

**Exit Criteria**: [Conditions that must be met before proceeding to next phase]

## Phase 2: [Phase Name]

[Tasks executed in this phase]

- T-003: [Brief description]
- T-004: [Brief description]

**Exit Criteria**: [Conditions that must be met before proceeding to next phase]

[Continue for all phases...]

## Parallel Execution Opportunities

[Identify tasks that can run in parallel to reduce total wall-clock time]

| Parallel Group | Tasks | Shared Dependencies | Risks |
|----------------|-------|---------------------|-------|
| Group 1 | T-XXX, T-XXX | [Shared resources] | [Risk description] |
| Group 2 | T-XXX, T-XXX | [Shared resources] | [Risk description] |

# Documentation Workstream

## Documentation Tasks

[Identify dedicated documentation tasks within the task graph]

### T-DOC-001: [Documentation Task Name]

- **Description**: [What documentation this task creates or updates]
- **Artifacts**: [List artifact keys: `SYSTEM_CONTEXT`, `CODEBASE_INVENTORY`, etc.]
- **Dependencies**: [List code tasks that must complete first]
- **Validation**: [How documentation completeness will be verified]

### T-DOC-002: [Documentation Task Name]

- **Description**: [What documentation this task creates or updates]
- **Artifacts**: [List artifact keys]
- **Dependencies**: [List code tasks that must complete first]
- **Validation**: [How documentation completeness will be verified]

[Continue for all documentation tasks...]

## Documentation Coverage Map

[Map each code change to its corresponding documentation update]

| Code Change | Documentation Update | Artifact Key | Owner |
|-------------|---------------------|--------------|-------|
| [Modified file] | [Updated doc] | [Artifact key] | [Role] |
| [New module] | [New module doc] | [Artifact key] | [Role] |

## Baseline vs Profile-Specific Documentation

[Distinguish between universal documentation obligations and architecture-profile-specific obligations]

**Baseline (Universal)**:
- [List documentation tasks required for all initiatives]

**Profile-Specific**:
- [List documentation tasks required only for specific architecture profiles]

# Success Criteria

## Functional Success

[List criteria indicating functional completeness]

- [ ] All tasks executed without fatal errors
- [ ] All artifact keys resolve correctly at runtime
- [ ] All meta.json sidecars written successfully

## Documentation Success

[List criteria indicating documentation completeness]

- [ ] All modified modules have updated documentation
- [ ] Codebase inventory reflects current state
- [ ] Change impact documents created for significant changes
- [ ] Documentation freshness verified against code baseline

## Quality Success

[List criteria indicating quality gates passed]

- [ ] Unit tests pass at required threshold
- [ ] Integration tests cover critical paths
- [ ] Code reviews approved by designated reviewers
- [ ] No hardcoded paths in core modules

# Cross-References

- **Parent Plan**: [Link to DELIVERY_PLAN_TEMPLATE]
- **Originating Initiative**: [Link to DELIVERY_INITIATIVE_TEMPLATE]
- **Task Templates**: [Links to individual DELIVERY_TASK_TEMPLATE instances]
- **Implementation Plans**: [Links to DELIVERY_IMPL_TEMPLATE instances]
- **Review Documents**: [Links to DELIVERY_REVIEW_TEMPLATE instances]
- **Validation Documents**: [Links to DELIVERY_VALIDATION_TEMPLATE instances]

# Notes

- [Additional context about task ordering or dependencies]
- [Assumptions about resource availability or agent capacity]
- [Record any deviations from standard task decomposition SOP]
- [Link to related task graphs or planning discussions]
