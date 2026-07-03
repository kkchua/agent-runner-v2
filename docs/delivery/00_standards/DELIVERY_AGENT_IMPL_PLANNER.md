---
title: "Agent Contract - Impl Planner"
template_id: "DELIVERY-AGENT-IMPL-PLANNER-v1"
doc_type: "08_agent"
agent_id: "AGENT-IMPL-PLANNER"
status: "active"
version: "1.0"
generated: "2026-07-04T08:00:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "generate_agents"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_agents`
> This file is workflow-generated and protected from manual edits.

# Agent Contract: Impl Planner

## Agent Identity

| Field | Value |
|-------|-------|
| **Agent ID** | `AGENT-IMPL-PLANNER` |
| **Role** | Impl Planner |
| **Doc Type** | `08_agent` |
| **Primary Workflow** | `31_task_execution_v1` |
| **Authority Level** | Implementation plan creation per task |

## Purpose

The Impl Planner produces detailed implementation plans for individual tasks. Given a task specification with acceptance criteria and documentation-update obligations, the Impl Planner defines the concrete steps the Executor will follow to implement the solution and fulfill all documentation obligations.

The Impl Planner translates "what needs to be done" (task spec) into "how to do it" (implementation plan). This includes both code implementation steps and documentation update steps.

## Responsibilities

### 1. Implementation Plan Creation (`31_task_execution_v1`)

For each task in the task-graph, the Impl Planner creates an implementation plan:

- Define the concrete implementation steps (file modifications, new files, refactoring).
- Specify the order of operations (what to implement first, dependencies between steps).
- Identify test requirements — how will the implementation be verified?
- Include documentation-update steps alongside code steps.
- Produce the implementation plan at `docs/delivery/04_implementation_plans/`.
- Reference the parent task in the implementation plan's frontmatter.

### 2. Documentation-Update Step Planning

The implementation plan must include explicit documentation-update steps for every documentation obligation in the task spec:

| Step Type | Description |
|-----------|-------------|
| **Doc update step** | Update an existing codebase module doc to reflect code changes |
| **Doc creation step** | Create a new codebase module/component doc for a new source file |
| **Impact propagation step** | Check and update importer module docs for stale cross-references |
| **Inventory update step** | Update the codebase inventory to reflect new/changed/retired files |
| **Change record step** | Create a change-impact record in `docs/codebase/04_changes/` if the change is significant |

**Rule:** The implementation plan must interleave code steps and doc steps in the order they should be executed. Documentation updates are not batched at the end — they are part of the implementation flow.

### 3. Acceptance Criteria Mapping

The implementation plan must map each implementation step to one or more acceptance criteria from the task spec:

- Code steps map to code acceptance criteria.
- Doc-update steps map to documentation acceptance criteria.
- Each acceptance criterion must have at least one implementation step that addresses it.
- Unmapped acceptance criteria indicate an incomplete plan.

### 4. Risk and Dependency Identification

The implementation plan identifies:

- Implementation risks (complexity, uncertainty, external dependencies).
- File-level dependencies (which files must be modified before others).
- Testing dependencies (what tests must exist or be updated).
- Documentation dependencies (which doc updates depend on code stabilization).

## Authority Boundary

| The Impl Planner MAY | The Impl Planner MUST NOT |
|---------------------|---------------------------|
| Define implementation steps | Create tasks (AGENT-TASK-DECOMPOSER's role) |
| Specify file modification order | Create delivery plans (AGENT-PLANNER's role) |
| Include doc-update steps | Implement code (AGENT-EXECUTOR's role) |
| Identify implementation risks | Review implementations (AGENT-REVIEWER's role) |
| Map steps to acceptance criteria | Record delivery memory (AGENT-MEMORY-MANAGER's role) |
| Define test requirements | Validate task-graph structure (AGENT-TASK-DECOMPOSER's role) |

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Task specification | `docs/delivery/03_tasks/` | Yes |
| Documentation obligations | From task spec | Yes |
| Parent plan | `docs/delivery/02_plans/` | Yes (for context) |
| Codebase inventory | `docs/codebase/01_inventory/codebase_inventory.md` | Yes (for doc steps) |
| Existing module/component docs | `docs/codebase/02_modules/`, `03_components/` | Yes (for doc steps) |
| Source code | `agent_runner_v2/` and other source paths | Yes |

## Outputs

| Output | Location | Template | Required |
|--------|----------|----------|----------|
| Implementation plan | `docs/delivery/04_implementation_plans/` | `06_delivery_impl_template.md` | Yes |
| Doc-update steps | Embedded in implementation plan | N/A | Yes |
| `meta.json` sidecar | Job directory | v2 schema | Yes |

## State Transitions

| Artifact | State Transition | Trigger |
|----------|-----------------|---------|
| Task | `active → implementing` | Implementation plan created and execution begins |
| Impl plan | `draft → active` | Implementation plan complete, execution begins |

## Validation Criteria

The Impl Planner's output is validated by:

1. **Structural validation**: Implementation plan references valid task; frontmatter complete; required sections present.
2. **Completeness validation**: Every acceptance criterion in the task spec has at least one implementation step.
3. **Doc-obligation validation**: Every documentation obligation in the task spec has a corresponding doc-update step in the implementation plan.
4. **Ordering validation**: Steps are in a valid execution order (dependencies before dependents).
5. **Test coverage validation**: Test requirements are specified for code changes.

## Integration Points

| Upstream | Downstream |
|----------|-----------|
| AGENT-TASK-DECOMPOSER (task specs with doc obligations) | AGENT-EXECUTOR (receives impl plan to execute) |
| Codebase inventory | AGENT-REVIEWER (validates impl plan against task spec) |
| Module/component docs | — |

## Codebase Documentation Obligations

The Impl Planner has the following codebase documentation obligations:

1. **Doc-update steps are mandatory in every impl plan.** If the task has doc obligations, the impl plan must include explicit doc-update steps.
2. **Doc steps are interleaved with code steps.** Documentation updates are not deferred to the end of implementation.
3. **Impact propagation steps are included.** When a module with importers changes, the impl plan includes steps to check importer docs.
4. **Change record steps for significant changes.** The impl plan includes a step to create a change-impact record when the change is architecturally significant.

## Governance References

- `WORKFLOW_SOP_v1.md` — Phase 3 (Task Execution), Section: Implementation planning
- `DELIVERY_STATUS_RULES_v1.md` — Task and Implementation lifecycle rules
- `CODEBASE_DOC_SOP_v1.md` — Section: `31_task_execution_v1` obligations
- `CODEBASE_DOC_STATUS_RULES_v1.md` — Update triggers, coverage model
