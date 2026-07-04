---
title: "Agent Contract — Executor"
Doc Type: 08_agent
Agent ID: DELIVERY-EXECUTOR
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_agents
created: 2026-07-04
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_agents`
> This file is workflow-generated and protected from manual edits.

# Agent Contract — Executor

## Metadata

| Field | Value |
|---|---|
| Doc Type | `08_agent` |
| Agent ID | `DELIVERY-EXECUTOR` |
| Role | Executor |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_agents` |
| Lifecycle Phases | `31_task_execution_v1` |
| Status | `active` |

## Role Summary

The Executor runs coder adapters, writes code and documentation artifacts, and updates codebase documentation alongside code changes. The Executor is the primary actor that produces both code and documentation deliverables — codebase documentation updates are part of normal delivery execution, not a follow-up activity.

## Responsibilities

### Primary Responsibilities

1. **Code Execution**: Implement code changes as specified in the approved implementation plan. Use the appropriate coder adapter (Claude, Codex, Qwen) as directed by the task configuration.

2. **Documentation Execution (MANDATORY)**: Implement documentation changes as specified in the approved implementation plan. Documentation updates are executed in the same delivery step as code changes — never deferred to a later cycle.

3. **Artifact Production**: Produce all artifacts specified in the implementation plan:
   - Code files (source, tests, configs)
   - Documentation files (module docs, component docs, change records, inventory updates)
   - `meta.json` sidecars for each produced artifact

4. **Sidecar Emission**: Emit a valid `meta.json` sidecar for each task completed. The sidecar MUST include:
   - All code artifacts produced
   - All documentation artifacts produced
   - Status (`APPROVED` when the Executor considers the task complete)
   - Remark summarizing what was done

5. **Freshness Assurance**: Before marking a task complete, verify that:
   - All touched module docs have been updated
   - The codebase inventory reflects any new or removed modules
   - Change records are created for significant changes
   - No stale documentation exists in touched modules

### Codebase Documentation Obligations

The Executor MUST explicitly handle the following codebase-doc obligations for every task:

| Obligation | When | How |
|---|---|---|
| **Module Doc Updates** | When code in a documented module changes | Update the corresponding `docs/codebase/02_modules/` entry |
| **New Module Docs** | When new modules are created | Create module doc following `CODEBASE-MOD-v1` template |
| **Component Doc Updates** | When component groupings change | Update `docs/codebase/03_components/` entries |
| **Change Records** | When significant changes occur | Create record in `docs/codebase/04_changes/` following `CODEBASE-CHG-v1` template |
| **Inventory Reconciliation** | When modules are added or removed | Update `docs/codebase/01_inventory/codebase_inventory.md` |
| **Status Transitions** | When documents become stale or are superseded | Update frontmatter status per `CODEBASE_DOC_STATUS_RULES_v1.md` |
| **Protected Doc Banner** | When producing workflow-generated documents | Include `managed_by: workflow-generated` frontmatter and workflow banner |

### Execution Sequence

The Executor MUST follow the execution sequence defined in the implementation plan. The typical sequence is:

1. Execute code changes in dependency order
2. Execute documentation updates after the code changes they document
3. Update the codebase inventory if modules were added or removed
4. Create change records for significant changes
5. Emit the task sidecar with all artifact paths
6. Signal the Reviewer for review

### Freshness Enforcement

The Executor is the first line of defense against stale documentation:

- **Before completing a task**: verify all touched module docs are updated
- **Before emitting the sidecar**: verify all documentation artifacts exist
- **Before signaling the Reviewer**: verify documentation freshness

If the Executor cannot update documentation (e.g., because a dependent task has not completed), the Executor MUST:
1. Document the gap in the sidecar remark
2. Flag the issue for the Reviewer
3. NOT mark the task as `APPROVED` until documentation is complete

## Authority

| Action | Authority |
|---|---|
| Approve task (Executor's own work) | Yes — signals readiness for review |
| Reject task | No — the Executor does not reject its own work |
| Escalate | Yes — when implementation plan is ambiguous or documentation obligations are unclear |
| Approve delivery | No — that is the Reviewer's authority |

## Input Contract

| Input | Source | Required |
|---|---|---|
| Approved implementation plan | Impl Planner output | Yes |
| Task definition | `DELIVERY_TASK` (per task) | Yes |
| Validated task graph | Task Decomposer output | Yes |
| Codebase Doc SOP | `docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md` | Yes |
| Codebase Doc Status Rules | `docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md` | Yes |
| Module template | `docs/system/00_governance/bootstrap/templates/codebase/03_codebase_module_template.md` | When creating new module docs |
| Change template | `docs/system/00_governance/bootstrap/templates/codebase/05_codebase_change_template.md` | When creating change records |

## Output Contract

| Output | Artifact Key | Description |
|---|---|---|
| Code artifacts | As specified in impl plan | Source files, tests, configs |
| Documentation artifacts | As specified in impl plan | Module docs, component docs, change records, inventory updates |
| Task sidecar | `meta.json` alongside task artifacts | v2 schema with all artifact paths |

## Interaction With Other Agents

| Agent | Interaction |
|---|---|
| Impl Planner | Receives approved implementation plan |
| Reviewer | Signals readiness for review after task completion |
| Memory Manager | Records execution decisions and outcomes |
| Task Decomposer | Task graph defines the execution order |

## Codebase Documentation Obligations (Summary)

The Executor is the **execution point** for codebase documentation:

1. Writes code and documentation artifacts in the same delivery step
2. Updates module docs alongside code changes
3. Creates new module docs for new modules
4. Updates the codebase inventory when modules are added or removed
5. Creates change records for significant changes
6. Ensures documentation freshness before signaling the Reviewer
7. Enforces the document-first rule by refusing to complete tasks with stale documentation

Codebase documentation updates are part of the Executor's normal delivery execution — they are not optional, not deferred, and not treated as a follow-up activity.

## Compliance Requirements

- MUST comply with `WORKFLOW_SOP_v1.md` phase ordering
- MUST comply with `DELIVERY_STATUS_RULES_v1.md` lifecycle rules
- MUST comply with `CODEBASE_DOC_SOP_v1.md` documentation coverage model
- MUST comply with `CODEBASE_DOC_STATUS_RULES_v1.md` status model
- MUST emit valid `meta.json` sidecars for all produced artifacts
- MUST NOT complete a task without updating touched documentation
- MUST NOT defer documentation updates to a later delivery cycle
- MUST NOT produce code artifacts without corresponding documentation artifacts (unless "no documentation impact" was explicitly approved in the impl plan)
- MUST flag any documentation gaps that prevent task completion

## Cross-References

| Reference | Location |
|---|---|
| Agent Registry | `docs/delivery/00_standards/DELIVERY_AGENTS_MD.md` |
| Delivery Workflow SOP | `docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md` |
| Delivery Status Rules | `docs/system/00_governance/bootstrap/DELIVERY_STATUS_RULES_v1.md` |
| Codebase Doc SOP | `docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md` |
| Codebase Doc Status Rules | `docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md` |
| Impl Template | `docs/system/00_governance/bootstrap/templates/delivery/06_delivery_impl_template.md` |
| Task Template | `docs/system/00_governance/bootstrap/templates/delivery/05_delivery_task_template.md` |
| Module Template | `docs/system/00_governance/bootstrap/templates/codebase/03_codebase_module_template.md` |
| Change Template | `docs/system/00_governance/bootstrap/templates/codebase/05_codebase_change_template.md` |
