---
template_id: SYS-03-AI
version: "1.0.0"
doc_type: "bundle_definition"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Master index of all SDLC agent contract definitions for governance scanning"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "template"
---

> Managed by workflow: sdlc_00_delivery_scaffold_v1 / step: generate_agent_contracts
> This file is workflow-generated and protected from manual edits.

# SDLC Agent Contract Registry

## Purpose

This document is the master index of all agent contract definitions for
the Layer 3 AI-Driven SDLC workflow family on the agent-runner-v2
platform. It maps each agent to its role, workflow assignment, primary
inputs, primary outputs, and template cross-references.

This registry is the authoritative source of truth for which agent
contract governs which SDLC workflow phase.

## Scope

This registry covers agent contracts for Layer 3 SDLC workflows only.
It does not cover Layer 1 governance rules, Layer 2 platform contract,
or delivery document templates (which are cataloged separately under
01_templates/).

Agent contracts are universal: they are shared across all repositories
via the global runtime path and are not repository-specific.

## Agent Registry Table

| # | Agent Contract File | Agent ID | Agent Role | Workflow Assignment | Primary Input | Primary Output |
|---|---|---|---|---|---|---|
| 1 | AGENT-planner.md | AGENT-PLANNER | Solution Architect | sdlc_20_planning_v1 | INIT-DOC (approved) | REQ-DOC |
| 2 | AGENT-task-decomposer.md | AGENT-TASK-DECOMPOSER | Task Decomposer | sdlc_30_backlog_v1, sdlc_40_task_v1 | REQ-DOC or PLAN-DOC (approved) | PLAN-DOC or BACKLOG-DOC |
| 3 | AGENT-implementation-planner.md | AGENT-IMPL-PLANNER | Implementation Planner | sdlc_50_implementation_v1 | BACKLOG-DOC (approved) | TASK-DOC |
| 4 | AGENT-executor.md | AGENT-EXECUTOR | Code Executor | sdlc_60_execution_v1 | TASK-DOC (approved) | IMPL-DOC, code changes |
| 5 | AGENT-reviewer.md | AGENT-REVIEWER | Independent Reviewer | sdlc_70_validation_v1, sdlc_80_review_v1 | IMPL-DOC or VALID-DOC (approved) | VALID-DOC or REV-DOC |
| 6 | AGENT-memory-manager.md | AGENT-MEMORY-MGR | Memory Manager | sdlc_80_review_v1 | Approved artifacts, delivery summaries | MEM-DOC, CLOSE-DOC |

## Workflow-to-Agent Assignment Map

| Workflow | Agent(s) Used | Role(s) |
|---|---|---|
| sdlc_10_requirement_v1 | (none -- workflow-driven from user draft) | N/A |
| sdlc_20_planning_v1 | AGENT-PLANNER | Solution Architect |
| sdlc_30_backlog_v1 | AGENT-TASK-DECOMPOSER | Task Decomposer (REQ -> PLAN mode) |
| sdlc_40_task_v1 | AGENT-TASK-DECOMPOSER | Task Decomposer (PLAN -> BACKLOG mode) |
| sdlc_50_implementation_v1 | AGENT-IMPL-PLANNER | Implementation Planner |
| sdlc_60_execution_v1 | AGENT-EXECUTOR | Code Executor |
| sdlc_70_validation_v1 | AGENT-REVIEWER | Independent Reviewer (validation mode) |
| sdlc_80_review_v1 | AGENT-REVIEWER + AGENT-MEMORY-MGR | Reviewer + Memory Manager |

## Agent-to-Template Cross-Reference

| Agent | Produces Artifact | Template Used | Template ID |
|---|---|---|---|
| AGENT-PLANNER | REQ-DOC | 03_REQ_template.md | SYS-03-RQ |
| AGENT-TASK-DECOMPOSER (sdlc_30) | PLAN-DOC | 04_PLAN_template.md | SYS-03-PL |
| AGENT-TASK-DECOMPOSER (sdlc_40) | BACKLOG-DOC | 05_BACKLOG_template.md | SYS-03-BL |
| AGENT-IMPL-PLANNER | TASK-DOC | 06_TASK_template.md | SYS-03-TK |
| AGENT-EXECUTOR | IMPL-DOC | 07_IMPL_template.md | SYS-03-IM |
| AGENT-REVIEWER (sdlc_70) | VALID-DOC | 08_VALID_template.md | SYS-03-VL |
| AGENT-REVIEWER (sdlc_80) | REV-DOC | 09_REV_template.md | SYS-03-RV |
| AGENT-MEMORY-MGR | MEM-DOC | 10_MEM_template.md | SYS-03-MM |
| AGENT-MEMORY-MGR | CLOSE-DOC | 11_CLOSE_template.md | SYS-03-CL |

## Handoff Chain

The following describes the document-driven handoff chain across agents.
Each agent produces an artifact that becomes the approved input for the
next agent in the chain.

```
DRAFT-INIT (user-authored)
    | sdlc_10 (workflow-driven, no agent)
    v
INIT-DOC (approved)
    | AGENT-PLANNER (sdlc_20)
    v
REQ-DOC (approved)
    | AGENT-TASK-DECOMPOSER (sdlc_30)
    v
PLAN-DOC (approved)
    | AGENT-TASK-DECOMPOSER (sdlc_40)
    v
BACKLOG-DOC (approved)
    | AGENT-IMPL-PLANNER (sdlc_50)
    v
TASK-DOC (approved)
    | AGENT-EXECUTOR (sdlc_60)
    v
IMPL-DOC (approved)
    | AGENT-REVIEWER (sdlc_70)
    v
VALID-DOC (approved)
    | AGENT-REVIEWER + AGENT-MEMORY-MGR (sdlc_80)
    v
REV-DOC + MEM-DOC + CLOSE-DOC (approved)
```

## Cross-Agent Rules

All agents MUST comply with these universal rules:

1. Role Isolation: Each agent MUST stay within its assigned role. No
   silent cross-role behavior.

2. Document-First: Every meaningful output MUST exist as a file artifact.

3. No Scope Drift: Agents MUST NOT silently widen objectives, redesign
   architecture, or add unapproved features.

4. Explicit Decisions: Review and validation artifacts MUST include an
   explicit decision and supporting evidence.

5. Canonical Linking: Every output MUST preserve upstream IDs (Initiative
   ID, Plan ID, Task ID, and related review/validation IDs).

6. Deterministic Naming: All output files MUST follow the naming
   convention defined in WORKFLOW_SOP_v1.md.

7. Approved Inputs Only: Downstream agents MUST prefer approved upstream
   artifacts. If operating on draft materials, that fact MUST be
   explicitly stated.

8. Rejected Means Stop: If a review or validation result is rejected, no
   downstream execution may continue until the issue is resolved.

9. Superseded Means Inactive: Superseded artifacts MUST NOT be used as
   execution sources.

10. Traceability is Mandatory: Every output MUST reference the governing
    input documents and key dependencies.

## Authority Precedence

When interpretation conflicts occur across governing documents, the
precedence order is:

1. Layer 1 governance (METADATA_STANDARD.md)
2. Layer 2 platform contract (METADATA_CONTRACT.md and siblings)
3. DELIVERY_STATUS_RULES_v1.md (this directory)
4. WORKFLOW_SOP_v1.md (01_templates/)
5. AGENTS.md (this file)
6. Individual agent contract file

Lower-precedence layers may describe but MUST NOT override
higher-precedence layers.

## Governing Documents

All agents MUST follow:

1. DELIVERY_STATUS_RULES_v1.md (this directory)
2. WORKFLOW_SOP_v1.md (01_templates/)
3. Their own individual agent contract
4. This registry (AGENTS.md)

## Agent Contract Version History

| Version | Date | Change Summary |
|---|---|---|
| 1.0.0 | 2026-07-22 | Initial release. Six agent contracts plus registry and status rules. |

## Related Documents

- Template Registry: 01_templates/template_registry.md
- Workflow SOP: 01_templates/WORKFLOW_SOP_v1.md
- Delivery Status Rules: DELIVERY_STATUS_RULES_v1.md (this directory)
- Layer 1 Metadata Standard: METADATA_STANDARD.md (governance foundation)
- Layer 2 Metadata Contract: METADATA_CONTRACT.md (platform constitution)
- Layer 3 SDLC Specification: masterplan/LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md
