---
title: "Agent Registry - Delivery Workflow Agents"
template_id: "DELIVERY-AGENTS-MD-v1"
doc_type: "08_agent"
agent_id: "AGENT-REGISTRY"
status: "active"
version: "1.0"
generated: "2026-07-04T08:00:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "generate_agents"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_agents`
> This file is workflow-generated and protected from manual edits.

# Agent Registry

This document is the **agent registry** for the `10_execution_scaffold_v1` workflow bundle. It defines the complete set of delivery agents, their responsibilities, authority boundaries, and integration points within the governed delivery lifecycle.

All agents operate under the authority precedence defined in `WORKFLOW_SOP_v1.md`. No agent may override another agent's artifacts without going through the review loop defined in `DELIVERY_STATUS_RULES_v1.md`.

## Registry Summary

| Agent ID | Role | Primary Workflow Phase(s) | Authority Scope |
|----------|------|--------------------------|-----------------|
| `AGENT-PLANNER` | Planner | `20_initiative_intake_v1`, `30_delivery_planning_v1` | Initiative capture, plan creation, documentation-scope identification |
| `AGENT-TASK-DECOMPOSER` | Task Decomposer | `30_delivery_planning_v1` | Task-graph decomposition, task spec creation, doc-scope-to-obligation conversion |
| `AGENT-IMPL-PLANNER` | Impl Planner | `31_task_execution_v1` | Implementation plan creation per task |
| `AGENT-EXECUTOR` | Executor | `31_task_execution_v1` | Code implementation, codebase documentation updates, deliverable production |
| `AGENT-REVIEWER` | Reviewer | `31_task_execution_v1` | Implementation review, doc-accuracy verification, acceptance criteria validation |
| `AGENT-MEMORY-MANAGER` | Memory Manager | `31_task_execution_v1`, `40_documentation_sync_v1` | Delivery memory recording, governance artifact maintenance, codebase-doc reconciliation flagging |

## Design Principles

1. **Single responsibility per agent.** Each agent owns exactly one phase of the delivery lifecycle. No agent performs work outside its authority boundary.

2. **Document-first execution.** Every agent produces documents before producing code. Code is secondary to governance artifacts.

3. **Codebase documentation as first-class obligation.** Codebase documentation updates are not optional cleanup — they are part of normal delivery execution. The Executor creates and updates codebase docs; the Reviewer verifies doc accuracy; the Memory Manager records doc state.

4. **Documentation-scope capture is mandatory.** The Planner captures documentation scope at initiative intake. The Task Decomposer converts that scope into concrete task-level obligations. No task that touches code may proceed without documented obligations.

5. **Sidecar-verified output.** Every agent step produces a `meta.json` sidecar. The sidecar is the only structured output channel between coder steps and the runner.

6. **Supersession over deletion.** When an agent's output is replaced, the old version is marked `superseded` with a pointer to the replacement. No artifact is ever deleted.

## Authority Boundaries

```
                    ┌─────────────────────┐
                    │  AGENT-PLANNER      │
                    │  Initiative + Plan  │
                    │  + Doc-Scope        │
                    └─────────┬───────────┘
                              │ initiative, plan, doc-scope
                              ▼
                    ┌─────────────────────┐
                    │ AGENT-TASK-         │
                    │ DECOMPOSER          │
                    │ Task-graph + Tasks  │
                    │ + Doc-Obligations   │
                    └─────────┬───────────┘
                              │ task specs with doc obligations
                              ▼
                    ┌─────────────────────┐
                    │ AGENT-IMPL-PLANNER  │
                    │ Implementation Plan │
                    └─────────┬───────────┘
                              │ impl plan
                              ▼
                    ┌─────────────────────┐
                    │  AGENT-EXECUTOR     │
                    │  Code + Doc Updates │
                    └─────────┬───────────┘
                              │ implementation + doc changes
                              ▼
                    ┌─────────────────────┐
                    │  AGENT-REVIEWER     │
                    │  Review + Doc Check │
                    └─────────┬───────────┘
                              │ review verdict
                              ▼
                    ┌─────────────────────┐
                    │ AGENT-MEMORY-       │
                    │ MANAGER             │
                    │ Memory + Doc Flags  │
                    └─────────────────────┘
```

## Cross-Agent Contracts

### Planner → Task Decomposer

| Contract Field | Requirement |
|---------------|-------------|
| Input | Initiative document, Plan document, Documentation Scope |
| Output | Task-graph, Task specs with doc-update obligations |
| Invariant | Every code-modifying task has a corresponding doc-update obligation |
| Authority boundary | Planner does not decompose; Decomposer does not scope |

### Task Decomposer → Impl Planner

| Contract Field | Requirement |
|---------------|-------------|
| Input | Task spec (with acceptance criteria and doc obligations) |
| Output | Implementation plan |
| Invariant | Impl plan references valid task and covers both code and doc work |
| Authority boundary | Decomposer does not plan implementation; Impl Planner does not decompose |

### Impl Planner → Executor

| Contract Field | Requirement |
|---------------|-------------|
| Input | Implementation plan |
| Output | Code changes, codebase doc updates, deliverable artifacts |
| Invariant | Code changes have corresponding doc updates in same delivery |
| Authority boundary | Impl Planner does not implement; Executor does not plan |

### Executor → Reviewer

| Contract Field | Requirement |
|---------------|-------------|
| Input | Implementation, codebase doc updates, deliverables |
| Output | Review verdict (approve / request rework) |
| Invariant | Review checks both code correctness AND doc accuracy |
| Authority boundary | Executor does not review own work; Reviewer does not implement |

### Reviewer → Memory Manager

| Contract Field | Requirement |
|---------------|-------------|
| Input | Approved review, completed delivery chain |
| Output | Memory record, stale-doc flags, governance updates |
| Invariant | Every completed delivery produces a memory record |
| Authority boundary | Reviewer does not record memory; Memory Manager does not review |

## Codebase Documentation Obligations by Agent

| Agent | Doc Obligation |
|-------|---------------|
| **Planner** | Capture documentation scope at initiative intake; identify stale-guidance risks |
| **Task Decomposer** | Convert documentation scope into concrete task-level doc obligations |
| **Impl Planner** | Include doc-update work in implementation plan |
| **Executor** | Execute codebase doc updates alongside code changes (co-change rule) |
| **Reviewer** | Verify doc accuracy matches code changes; reject if doc is stale or missing |
| **Memory Manager** | Record doc state in memory; flag stale docs for future correction |

## Agent Document Locations

All agent contracts reside at:

```
docs/delivery/00_standards/
  DELIVERY_AGENTS_MD.md                    (this file — agent registry)
  DELIVERY_AGENT_PLANNER.md                (AGENT-PLANNER contract)
  DELIVERY_AGENT_TASK_DECOMPOSER.md        (AGENT-TASK-DECOMPOSER contract)
  DELIVERY_AGENT_IMPL_PLANNER.md           (AGENT-IMPL-PLANNER contract)
  DELIVERY_AGENT_EXECUTOR.md               (AGENT-EXECUTOR contract)
  DELIVERY_AGENT_REVIEWER.md               (AGENT-REVIEWER contract)
  DELIVERY_AGENT_MEMORY_MANAGER.md         (AGENT-MEMORY-MANAGER contract)
```

## Governance References

| Reference | Path |
|-----------|------|
| Delivery Workflow SOP | `docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md` |
| Delivery Status Rules | `docs/system/00_governance/bootstrap/DELIVERY_STATUS_RULES_v1.md` |
| Codebase Documentation SOP | `docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md` |
| Codebase Documentation Status Rules | `docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md` |
| Delivery Template Registry | `docs/system/00_governance/bootstrap/templates/delivery/01_delivery_template_registry.md` |
| Project Analysis | `docs/delivery/project_analysis.md` |

## Deprecated

The `07_master_prompts` directory is **deprecated** and must not appear in any governance reference, template, or SOP produced by any agent.
