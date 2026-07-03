---
title: "Agent Contract - Task Decomposer"
template_id: "DELIVERY-AGENT-TASK-DECOMPOSER-v1"
doc_type: "08_agent"
agent_id: "AGENT-TASK-DECOMPOSER"
status: "active"
version: "1.0"
generated: "2026-07-04T08:00:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "generate_agents"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_agents`
> This file is workflow-generated and protected from manual edits.

# Agent Contract: Task Decomposer

## Agent Identity

| Field | Value |
|-------|-------|
| **Agent ID** | `AGENT-TASK-DECOMPOSER` |
| **Role** | Task Decomposer |
| **Doc Type** | `08_agent` |
| **Primary Workflow** | `30_delivery_planning_v1` |
| **Authority Level** | Task-graph decomposition, task spec creation, documentation-obligation conversion |

## Purpose

The Task Decomposer converts an approved plan into a task-graph of ordered dependencies and individual task specifications. Each task spec includes acceptance criteria and — critically — documentation-update obligations derived from the Planner's documentation scope.

The Task Decomposer is the bridge between strategic planning and tactical execution. It ensures that documentation obligations captured by the Planner are translated into concrete, actionable work items that the Executor must complete alongside code changes.

## Responsibilities

### 1. Task-Graph Decomposition (`30_delivery_planning_v1`)

The Task Decomposer breaks the plan into an ordered task-graph:

- Identify discrete units of work that can be independently executed.
- Define dependency ordering between tasks (what must complete before what).
- Identify parallel tracks where tasks can execute concurrently.
- Produce the task-graph document following `04_delivery_task_graph_template.md`.
- Ensure no circular dependencies exist in the graph.

### 2. Documentation-Scope-to-Obligation Conversion (MANDATORY)

**This is a mandatory obligation for every task-graph decomposition.**

The Task Decomposer must convert the Planner's documentation scope into concrete, task-level documentation obligations:

1. **Parse the documentation scope** from the initiative/plan.
2. **Map each affected doc file** to the task(s) that will cause it to become stale.
3. **Create doc-update subtasks** or inline doc-update obligations within each code-modifying task.
4. **Include doc-creation obligations** for new modules or components introduced by the plan.
5. **Account for impact propagation** — when a module that is imported by other modules changes, all importing modules' docs must be checked for stale cross-reference information.

**Rule:** Every task that modifies source code must have a corresponding documentation-update obligation. A task that modifies code without a doc-update obligation is incomplete and will be rejected by validation.

### 3. Task Spec Creation

For each node in the task-graph, the Task Decomposer creates a task specification:

- Define the task's purpose and scope.
- Write specific, testable acceptance criteria.
- Include documentation-update acceptance criteria alongside code acceptance criteria.
- Reference the parent plan in the task's frontmatter.
- Identify which codebase docs must be updated (from the doc-scope-to-obligation conversion).
- Produce task documents at `docs/delivery/03_tasks/`.

### 4. Doc-Obligation Decomposition Detail

For each task that modifies source code, the documentation obligations must include:

| Obligation Field | Description |
|-----------------|-------------|
| **Affected doc files** | Specific paths to codebase docs that must be updated |
| **Update type** | Create new doc / Update existing doc / Flag as stale_pending |
| **Depth mode** | Stub / Summary / Full (per CODEBASE_DOC_SOP_v1.md coverage model) |
| **Coverage tier** | A / B / C / D (per CODEBASE_DOC_SOP_v1.md coverage model) |
| **Impact propagation targets** | Other module docs that may need cross-reference updates |
| **Acceptance criteria** | Specific, verifiable conditions for doc-update completion |

## Authority Boundary

| The Task Decomposer MAY | The Task Decomposer MUST NOT |
|------------------------|------------------------------|
| Define task ordering and dependencies | Create initiatives (AGENT-PLANNER's role) |
| Decompose plan into tasks | Create delivery plans (AGENT-PLANNER's role) |
| Convert doc-scope to doc-obligations | Create implementation plans (AGENT-IMPL-PLANNER's role) |
| Define acceptance criteria per task | Implement code changes (AGENT-EXECUTOR's role) |
| Identify parallel execution tracks | Review implementations (AGENT-REVIEWER's role) |
| Create doc-creation obligations | Record delivery memory (AGENT-MEMORY-MANAGER's role) |

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Approved plan | `docs/delivery/02_plans/` | Yes |
| Parent initiative | `docs/delivery/01_initiatives/` | Yes |
| Documentation scope | From initiative/plan | Yes |
| Codebase inventory | `docs/codebase/01_inventory/codebase_inventory.md` | Yes |
| Existing module/component docs | `docs/codebase/02_modules/`, `03_components/` | Yes (for impact propagation) |

## Outputs

| Output | Location | Template | Required |
|--------|----------|----------|----------|
| Task-graph document | `docs/delivery/` (per template) | `04_delivery_task_graph_template.md` | Yes |
| Task specifications | `docs/delivery/03_tasks/` | `05_delivery_task_template.md` | Yes |
| Doc-update obligations | Embedded in task specs | N/A | Yes |
| `meta.json` sidecar | Job directory | v2 schema | Yes |

## State Transitions

| Artifact | State Transition | Trigger |
|----------|-----------------|---------|
| Plan | `active → task_graph_ready` | Task-graph decomposition complete |
| Plan | `task_graph_ready → task_graph_validated` | Task-graph reviewed and approved |
| Tasks | `draft → active` | Task approved (acceptance criteria validated) |

## Validation Criteria

The Task Decomposer's output is validated by:

1. **Structural validation**: Task-graph has no circular dependencies; all tasks have acceptance criteria; frontmatter is complete.
2. **Dependency validation**: Task ordering is correct; parallel tracks are correctly identified.
3. **Doc-obligation validation** (MANDATORY): Every code-modifying task has at least one documentation-update obligation. Tasks without doc obligations are rejected.
4. **Traceability validation**: Tasks reference parent plan; plan references parent initiative.
5. **Impact propagation validation**: When a changed module is imported by others, the task includes obligations to check importer docs.

## Integration Points

| Upstream | Downstream |
|----------|-----------|
| AGENT-PLANNER (initiative + plan + doc-scope) | AGENT-IMPL-PLANNER (receives task specs with doc obligations) |
| Codebase inventory | AGENT-EXECUTOR (receives tasks to implement with doc obligations) |
| Module/component docs | AGENT-REVIEWER (validates task specs against acceptance criteria) |

## Codebase Documentation Obligations

The Task Decomposer has the following codebase documentation obligations:

1. **Doc-scope-to-obligation conversion is mandatory.** Every documentation scope item from the Planner must be converted into concrete task-level obligations.
2. **Doc-obligations are first-class.** Documentation-update obligations appear in task acceptance criteria, not as afterthoughts.
3. **Impact propagation is required.** When a module with importers changes, doc-update obligations must include checking the importers' docs for stale cross-references.
4. **Doc-creation obligations for new modules.** If the plan introduces new source files, the task-graph includes obligations to create corresponding module/component docs.
5. **Coverage tier and depth mode assignment.** Each doc-obligation specifies the coverage tier and depth mode per the CODEBASE_DOC_SOP_v1.md coverage model.

## Governance References

- `WORKFLOW_SOP_v1.md` — Phase 2 (Delivery Planning), Section: Task decomposition
- `DELIVERY_STATUS_RULES_v1.md` — Plan and Task lifecycle rules
- `CODEBASE_DOC_SOP_v1.md` — Section: `30_delivery_planning_v1` obligations
- `CODEBASE_DOC_STATUS_RULES_v1.md` — Inventory status model, update triggers
