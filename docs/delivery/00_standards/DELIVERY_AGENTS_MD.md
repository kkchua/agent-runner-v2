---
title: Delivery Agent Contracts Registry
Doc Type: 08_agent
Agent ID: DELIVERY-AGENTS-REG
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_agents
created: 2026-07-04
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_agents`
> This file is workflow-generated and protected from manual edits.

# Delivery Agent Contracts Registry

## Metadata

| Field | Value |
|---|---|
| Doc Type | `08_agent` |
| Agent ID | `DELIVERY-AGENTS-REG` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_agents` |
| Scope | Universal baseline — applies to all governed repositories |
| Status | `active` |
| Last Verified | 2026-07-04 |

This document is the **agent registry** for the `10_execution_scaffold_v1` workflow bundle. It is the authoritative index of all agent role contracts that govern delivery execution and codebase documentation maintenance in this workflow.

## Purpose

This registry defines the agent roles that execute the delivery lifecycle. Every agent contract specifies:

1. The agent's role in the delivery state machine
2. Its responsibilities for codebase documentation as part of normal delivery execution
3. Its authority boundaries (approve / reject / escalate)
4. Its input and output contracts
5. Its interaction with other agents

## Agent Roster

| Agent ID | Agent Role | Artifact Key | File Path | Lifecycle Phase |
|---|---|---|---|---|
| `DELIVERY-PLANNER` | Planner | `DELIVERY_AGENT_PLANNER` | `docs/delivery/00_standards/DELIVERY_AGENT_PLANNER.md` | `20_initiative_intake_v1`, `30_delivery_planning_v1` |
| `DELIVERY-TASK-DECOMP` | Task Decomposer | `DELIVERY_AGENT_TASK_DECOMPOSER` | `docs/delivery/00_standards/DELIVERY_AGENT_TASK_DECOMPOSER.md` | `30_delivery_planning_v1` |
| `DELIVERY-IMPL-PLAN` | Impl Planner | `DELIVERY_AGENT_IMPL_PLANNER` | `docs/delivery/00_standards/DELIVERY_AGENT_IMPL_PLANNER.md` | `31_task_execution_v1` |
| `DELIVERY-EXECUTOR` | Executor | `DELIVERY_AGENT_EXECUTOR` | `docs/delivery/00_standards/DELIVERY_AGENT_EXECUTOR.md` | `31_task_execution_v1` |
| `DELIVERY-REVIEWER` | Reviewer | `DELIVERY_AGENT_REVIEWER` | `docs/delivery/00_standards/DELIVERY_AGENT_REVIEWER.md` | `31_task_execution_v1` |
| `DELIVERY-MEM-MGR` | Memory Manager | `DELIVERY_AGENT_MEMORY_MANAGER` | `docs/delivery/00_standards/DELIVERY_AGENT_MEMORY_MANAGER.md` | All phases |

## Core Principle

**Codebase documentation updates are part of normal delivery execution.**

Every agent that participates in delivery execution treats codebase documentation as a first-class deliverable. Documentation is not a follow-up activity — it is embedded in every phase of the delivery lifecycle:

- The **Planner** captures documentation scope and converts it into plan-level obligations.
- The **Task Decomposer** decomposes documentation obligations into task-level deliverables with explicit dependencies.
- The **Impl Planner** includes codebase-doc impact analysis in every implementation plan.
- The **Executor** writes code and documentation artifacts together in the same delivery step.
- The **Reviewer** validates documentation freshness alongside code correctness.
- The **Memory Manager** records documentation decisions and lessons learned across deliveries.

## Agent Authority Matrix

| Agent | Can Approve | Can Reject | Can Escalate |
|---|---|---|---|
| Planner | Initiative, Plan | Initiative, Plan | Yes |
| Task Decomposer | Task Graph | Task Graph | Yes |
| Impl Planner | Implementation Plan | Implementation Plan | Yes |
| Executor | — | — | Yes |
| Reviewer | Task, Delivery | Task, Delivery | Yes |
| Memory Manager | — | — | Yes |

## Cross-Cutting Obligations

### Documentation-First Execution

All agents operate under the document-first rule from `WORKFLOW_SOP_v1.md`:
- No code changes without an approved implementation plan
- No task decomposition without an approved delivery plan
- No initiative execution without an approved initiative document
- Documentation updates are part of the task, not a follow-up

### Sidecar Contract

Every agent that produces an artifact MUST emit a `meta.json` sidecar conforming to v2 schema:
- `schema_version`: `v2`
- `coder_result.status`: `APPROVED` or `REJECTED`
- `coder_result.artifacts`: exact paths of generated documents
- `coder_result.recorded_at`: ISO 8601 timestamp

### Codebase Documentation Obligations

Every agent MUST comply with:
- `CODEBASE_DOC_SOP_v1.md` — documentation lifecycle and coverage rules
- `CODEBASE_DOC_STATUS_RULES_v1.md` — status model and transition rules
- Freshness enforcement — documentation updated in the same delivery cycle as code changes
- Status tracking — every document carries explicit status

## Dependency Chain

```
DELIVERY-AGENTS-REG (this document)
├── DELIVERY-PLANNER
│   ├── Produces: initiative, delivery plan
│   ├── References: WORKFLOW_SOP_v1, DELIVERY_STATUS_RULES_v1, CODEBASE_DOC_SOP_v1
│   └── Downstream: DELIVERY-TASK-DECOMP
├── DELIVERY-TASK-DECOMP
│   ├── Produces: task graph
│   ├── References: DELIVERY-PLANNER output
│   └── Downstream: DELIVERY-IMPL-PLAN
├── DELIVERY-IMPL-PLAN
│   ├── Produces: implementation plan per task
│   ├── References: DELIVERY-TASK-DECOMP output, CODEBASE_DOC_SOP_v1
│   └── Downstream: DELIVERY-EXECUTOR
├── DELIVERY-EXECUTOR
│   ├── Produces: code + documentation artifacts
│   ├── References: DELIVERY-IMPL-PLAN output, CODEBASE_DOC_STATUS_RULES_v1
│   └── Downstream: DELIVERY-REVIEWER
├── DELIVERY-REVIEWER
│   ├── Produces: review findings, approval/rejection
│   ├── References: All upstream artifacts, CODEBASE_DOC_SOP_v1
│   └── Downstream: DELIVERY-MEM-MGR
└── DELIVERY-MEM-MGR
    ├── Produces: delivery memory records
    ├── References: All upstream artifacts
    └── Cross-cutting: observes all phases
```

## Cross-References

| Reference | Location |
|---|---|
| Delivery Workflow SOP | `docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md` |
| Delivery Status Rules | `docs/system/00_governance/bootstrap/DELIVERY_STATUS_RULES_v1.md` |
| Codebase Doc SOP | `docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md` |
| Codebase Doc Status Rules | `docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md` |
| Delivery Template Registry | `docs/system/00_governance/bootstrap/templates/delivery/01_delivery_template_registry.md` |
| Codebase Template Registry | `docs/system/00_governance/bootstrap/templates/codebase/01_codebase_template_registry.md` |
| Project Analysis | `docs/codebase/01_inventory/01_PROJECT_ANALYSIS.md` |
