---
template_id: SYS-04-IX
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Master index of all SDLC agent contracts for governance scanning"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_agent_contracts
> This file is workflow-generated and protected from manual edits.

# SDLC Agent Contract Index

## Purpose

This document is the master index of all SDLC agent contracts for the
agent-runner-v2 platform. It maps each agent to its role, assigned
workflows, input/output document types, and version. This index is the
authoritative source of truth for which agent contract governs which
workflow step in the SDLC delivery pipeline.

## Scope

This index covers agent contracts for Layer 3 AI-Driven SDLC workflow
delivery only. It does not cover Layer 1 governance agents, Layer 2
platform agents, or bootstrap workflow agents (which are defined in
their respective bundle governance directories).

## Agent-to-Workflow Mapping

The following table is the authoritative agent-to-workflow mapping. All
cross-references in templates, the template registry, and individual
agent contracts MUST be consistent with this table.

| # | Agent ID | Agent File | Role | Workflow(s) | Input Doc | Output Doc |
|---|---|---|---|---|---|---|
| 1 | AGENT-planner | AGENT-planner.md | Solution Architect | sdlc_20_planning_v1 | INIT-DOC | REQ-DOC |
| 2 | AGENT-task-decomposer | AGENT-task-decomposer.md | Task Decomposer | sdlc_30_backlog_v1, sdlc_40_task_v1 | REQ-DOC / PLAN-DOC | PLAN-DOC / BACKLOG-DOC |
| 3 | AGENT-implementation-planner | AGENT-implementation-planner.md | Implementation Planner | sdlc_50_implementation_v1 | BACKLOG-DOC | TASK-DOC |
| 4 | AGENT-executor | AGENT-executor.md | Code Executor | sdlc_60_execution_v1 | TASK-DOC | IMPL-DOC |
| 5 | AGENT-reviewer | AGENT-reviewer.md | Independent Reviewer | sdlc_70_validation_v1, sdlc_80_review_v1 | IMPL-DOC / VALID-DOC | VALID-DOC / REV-DOC |
| 6 | AGENT-memory-manager | AGENT-memory-manager.md | Memory Manager | sdlc_80_review_v1 | Approved artifacts | MEM-DOC + CLOSE-DOC |

## Transformation Chain

The complete artifact transformation chain through all SDLC workflows:

```
DRAFT-INIT (user-authored)
    | sdlc_10_requirement_v1 (no agent -- workflow's own prompts)
    v
INIT-DOC
    | sdlc_20_planning_v1 (AGENT-planner)
    v
REQ-DOC
    | sdlc_30_backlog_v1 (AGENT-task-decomposer)
    v
PLAN-DOC
    | sdlc_40_task_v1 (AGENT-task-decomposer)
    v
BACKLOG-DOC
    | sdlc_50_implementation_v1 (AGENT-implementation-planner)
    v
TASK-DOC
    | sdlc_60_execution_v1 (AGENT-executor)
    v
IMPL-DOC
    | sdlc_70_validation_v1 (AGENT-reviewer)
    v
VALID-DOC
    | sdlc_80_review_v1 (AGENT-reviewer + AGENT-memory-manager)
    v
REV-DOC + MEM-DOC + CLOSE-DOC
```

## Agent Contracts

| Agent ID | Template ID | Contract File | Description |
|---|---|---|---|
| AGENT-planner | SYS-AG-PL | AGENT-planner.md | Transforms approved initiative into structured requirements |
| AGENT-task-decomposer | SYS-AG-TD | AGENT-task-decomposer.md | Breaks down requirements into plans, plans into backlog and tasks |
| AGENT-implementation-planner | SYS-AG-IP | AGENT-implementation-planner.md | Generates detailed implementation docs from backlog items |
| AGENT-executor | SYS-AG-EX | AGENT-executor.md | Implements code and tests per approved task specification |
| AGENT-reviewer | SYS-AG-RV | AGENT-reviewer.md | Independently validates implementations against requirements |
| AGENT-memory-manager | SYS-AG-MM | AGENT-memory-manager.md | Persists delivery knowledge after completion |

## Agent-to-Template Cross-Reference

| Agent ID | Produces Template | Template ID | Template File |
|---|---|---|---|
| AGENT-planner | REQ | SYS-03-RQ | 03_REQ_template.md |
| AGENT-task-decomposer | PLAN | SYS-03-PL | 04_PLAN_template.md |
| AGENT-task-decomposer | BACKLOG | SYS-03-BL | 05_BACKLOG_template.md |
| AGENT-implementation-planner | TASK | SYS-03-TK | 06_TASK_template.md |
| AGENT-executor | IMPL | SYS-03-IM | 07_IMPL_template.md |
| AGENT-reviewer | VALID | SYS-03-VL | 08_VALID_template.md |
| AGENT-reviewer | REV | SYS-03-RV | 09_REV_template.md |
| AGENT-memory-manager | MEM | SYS-03-MM | 10_MEM_template.md |
| AGENT-memory-manager | CLOSE | SYS-03-CL | 11_CLOSE_template.md |

## Workflows Without Agent Contracts

| Workflow | Agent Status | Notes |
|---|---|---|
| sdlc_00_delivery_scaffold_v1 | No agent | Bootstrap workflow |
| sdlc_00_codebase_v1 | No agent | Maintenance workflow |
| sdlc_10_requirement_v1 | No agent | Uses workflow's own prompts |

## Delivery Status Rules

All delivery documents produced by agents follow the lifecycle status
rules defined in DELIVERY_STATUS_RULES_v1.md in this directory.

## Agent Contract Version History

| Version | Date | Change Summary |
|---|---|---|
| 1.0.0 | 2026-07-22 | Initial release. All 6 agent contracts plus index and status rules. |

## Related Documents

- SDLC Template Registry: 01_templates/template_registry.md
- SDLC Workflow SOP: 01_templates/WORKFLOW_SOP_v1.md
- Delivery Status Rules: DELIVERY_STATUS_RULES_v1.md (this directory)
- Layer 1 Governance Lifecycle: GOVERNANCE_LIFECYCLE.md (foundation/current/)
- Layer 2 Metadata Contract: METADATA_CONTRACT.md (platform/current/)
