---
template_id: SYS-AG-IDX
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

# SDLC Agents Index

## Purpose

This document is the master index of all agent contract definitions for
the Layer 3 AI-Driven SDLC delivery system. It provides a role summary
table, workflow assignments, template cross-references, and dependency
relationships between agents.

Each agent contract defines the responsibilities, input/output
boundaries, behavior rules, and execution flow for one AI agent role
that participates in the SDLC workflow family.

## Scope

This index covers all agents used by the SDLC initiative workflows
(sdlc_10 through sdlc_80). It does not cover:

- Layer 1 governance agents (if any)
- Layer 2 platform agents (if any)
- The sdlc_00 bootstrap agents
- The sdlc_00_codebase maintenance workflow (which operates outside
  the approval-gate model)

## Agent Summary Table

| # | Agent ID | Agent Role | Template ID | Workflow(s) | Input Doc | Output Doc |
|---|---|---|---|---|---|---|
| 1 | AGENT-planner | Solution Architect | SYS-AG-PL | sdlc_20_planning_v1 | INIT-DOC (approved) | REQ document |
| 2 | AGENT-task-decomposer | Task Decomposer | SYS-AG-TD | sdlc_30_backlog_v1, sdlc_40_task_v1 | REQ or PLAN (approved) | PLAN or BACKLOG document |
| 3 | AGENT-implementation-planner | Implementation Planner | SYS-AG-IP | sdlc_50_implementation_v1 | BACKLOG (approved) | TASK document |
| 4 | AGENT-executor | Code Executor | SYS-AG-EX | sdlc_60_execution_v1 | TASK (approved) | IMPL document + code changes |
| 5 | AGENT-reviewer | Independent Reviewer | SYS-AG-RV | sdlc_70_validation_v1, sdlc_80_review_v1 | IMPL or VALID (approved) | VALID or REV document |
| 6 | AGENT-memory-manager | Memory Manager | SYS-AG-MM | sdlc_80_review_v1 | Approved artifacts, summaries | MEM document + CLOSE document |

## Agent-to-Workflow Assignment Matrix

| Agent | sdlc_10 | sdlc_20 | sdlc_30 | sdlc_40 | sdlc_50 | sdlc_60 | sdlc_70 | sdlc_80 |
|---|---|---|---|---|---|---|---|---|
| AGENT-planner | - | Yes | - | - | - | - | - | - |
| AGENT-task-decomposer | - | - | Yes (REQ->PLAN) | Yes (PLAN->BACKLOG) | - | - | - | - |
| AGENT-implementation-planner | - | - | - | - | Yes | - | - | - |
| AGENT-executor | - | - | - | - | - | Yes | - | - |
| AGENT-reviewer | - | - | - | - | - | - | Yes (IMPL->VALID) | Yes (VALID->REV) |
| AGENT-memory-manager | - | - | - | - | - | - | - | Yes |

Note: sdlc_10 uses no agent contract from this set. The initiative
capture step is driven by human-authored draft initiative input and
the sdlc_10 workflow's own prompts.

## Agent-to-Template Cross-Reference

| Agent | Templates Used (as output shape) | Templates Consumed (as input shape) |
|---|---|---|
| AGENT-planner | 03_REQ_template (SYS-03-RQ) | 02_INIT_template (SYS-03-IN) |
| AGENT-task-decomposer (sdlc_30) | 04_PLAN_template (SYS-03-PL) | 03_REQ_template (SYS-03-RQ) |
| AGENT-task-decomposer (sdlc_40) | 05_BACKLOG_template (SYS-03-BL) | 04_PLAN_template (SYS-03-PL) |
| AGENT-implementation-planner | 06_TASK_template (SYS-03-TK) | 05_BACKLOG_template (SYS-03-BL) |
| AGENT-executor | 07_IMPL_template (SYS-03-IM) | 06_TASK_template (SYS-03-TK) |
| AGENT-reviewer (sdlc_70) | 08_VALID_template (SYS-03-VL) | 07_IMPL_template (SYS-03-IM) |
| AGENT-reviewer (sdlc_80) | 09_REV_template (SYS-03-RV) | 08_VALID_template (SYS-03-VL) |
| AGENT-memory-manager | 10_MEM_template (SYS-03-MM), 11_CLOSE_template (SYS-03-CL) | 09_REV_template (SYS-03-RV), all upstream docs |

## Agent Contract File Locations

| Agent Contract | File Name | Template ID |
|---|---|---|
| Agent Planner | AGENT-planner.md | SYS-AG-PL |
| Task Decomposer | AGENT-task-decomposer.md | SYS-AG-TD |
| Implementation Planner | AGENT-implementation-planner.md | SYS-AG-IP |
| Code Executor | AGENT-executor.md | SYS-AG-EX |
| Independent Reviewer | AGENT-reviewer.md | SYS-AG-RV |
| Memory Manager | AGENT-memory-manager.md | SYS-AG-MM |
| Delivery Status Rules | DELIVERY_STATUS_RULES_v1.md | SYS-AG-DS |

All agent contracts reside in the 02_agents/ directory of the SDLC
delivery scaffold output.

## Agent Dependency Chain

```
AGENT-planner
    |
    v
AGENT-task-decomposer (sdlc_30 mode)
    |
    v
AGENT-task-decomposer (sdlc_40 mode)
    |
    v
AGENT-implementation-planner
    |
    v
AGENT-executor
    |
    v
AGENT-reviewer (sdlc_70 mode)
    |
    v
AGENT-reviewer (sdlc_80 mode) ---+
    |                             |
    v                             v
AGENT-memory-manager         (closure)
```

Each agent depends on the approved output of the preceding agent's
workflow. No agent may begin until its predecessor workflow has
produced an approved document.

## Shared Behavior Rules

All agents in this contract set share the following universal rules:

1. MUST operate within the Layer 1 governance model and Layer 2 platform
   contract. They must not redefine or contradict either layer.
2. MUST accept only inputs that carry `lifecycle_status: "approved"` in
   their YAML frontmatter (unless otherwise specified).
3. MUST produce outputs with `lifecycle_status: "draft"` initially.
   Promotion to `approved` is controlled by the workflow review and
   human approval gates.
4. MUST follow the naming conventions defined in the SDLC Workflow SOP
   (WORKFLOW_SOP_v1.md).
5. MUST include all required YAML frontmatter fields as defined by the
   Layer 1 Metadata Standard and Layer 2 Metadata Contract.
6. MUST NOT modify approved documents from prior workflows.
7. MUST use ASCII-only characters in all generated documents.
8. MUST cross-reference predecessor and successor documents in their
   outputs for audit trail traceability.

## Related Documents

- SDLC Template Registry: 01_templates/template_registry.md
- SDLC Workflow SOP: 01_templates/WORKFLOW_SOP_v1.md
- Delivery Status Rules: DELIVERY_STATUS_RULES_v1.md (this directory)
- Layer 1 Metadata Standard: docs/system/00_governance/foundation/current/METADATA_STANDARD.md
- Layer 1 Governance Lifecycle: docs/system/00_governance/foundation/current/GOVERNANCE_LIFECYCLE.md
- Layer 2 Runtime Model: docs/system/00_governance/platform/agent_runner/current/RUNTIME_MODEL.md
- Layer 2 Bundle Authoring Contract: docs/system/00_governance/platform/agent_runner/current/BUNDLE_AUTHORING_CONTRACT.md
- L3 SDLC Specification: masterplan/LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md

## Version History

| Version | Date | Change Summary |
|---|---|---|
| 1.0.0 | 2026-07-22 | Initial release. Six agent contracts plus delivery status rules. |
