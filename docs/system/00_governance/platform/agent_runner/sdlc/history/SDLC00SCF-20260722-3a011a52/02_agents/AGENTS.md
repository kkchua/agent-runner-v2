---
template_id: SYS-AG-ID
version: "1.0.0"
doc_type: "bundle_definition"
authority: "sdlc-owned"
scan_policy: "include"
scan_reason: "Master index of all SDLC agent contracts for governance scanning"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "SDLC00SCF-20260722-3a011a52"
---

> Managed by workflow: `sdlc_00_delivery_scaffold_v1` / step: `publish_sdlc_scaffold`
> This file is workflow-generated and protected from manual edits.

# SDLC Agent Contract Registry

## Purpose

This document is the master index of all agent contract definitions for the
Layer 3 AI-Driven SDLC delivery system running on the agent-runner-v2 platform.
It maps each agent to its role, target workflow assignments, input/output
document transformations, and storage location. This registry is the
authoritative source of truth for agent-to-workflow assignments within the
SDLC system.

## Scope

This registry covers agent contracts for the SDLC delivery workflows
(sdlc_10 through sdlc_80). It does not cover Layer 1 governance agents,
Layer 2 platform agents, or template definitions (which are cataloged
separately under 01_templates/).

## Agent-to-Workflow Mapping (Authoritative)

The following table is the single authoritative agent-to-workflow mapping.
All cross-references in templates, the template registry, and individual
agent contracts MUST be consistent with this table.

| Workflow | Agent(s) | Transformation |
|---|---|---|
| sdlc_10_requirement_v1 | (none -- uses workflow's own prompts) | DRAFT-INIT -> INIT-DOC |
| sdlc_20_planning_v1 | AGENT-planner | INIT-DOC -> REQ-DOC |
| sdlc_30_backlog_v1 | AGENT-task-decomposer | REQ-DOC -> PLAN-DOC |
| sdlc_40_task_v1 | AGENT-task-decomposer | PLAN-DOC -> BACKLOG-DOC |
| sdlc_50_implementation_v1 | AGENT-implementation-planner | BACKLOG-DOC -> TASK-DOC |
| sdlc_60_execution_v1 | AGENT-executor | TASK-DOC -> IMPL-DOC |
| sdlc_70_validation_v1 | AGENT-reviewer | IMPL-DOC -> VALID-DOC |
| sdlc_80_review_v1 | AGENT-reviewer, AGENT-memory-manager | VALID-DOC -> REV-DOC + MEM-DOC + CLOSE-DOC |

## Agent Registry Summary

| # | Agent Contract File | Template ID | Agent ID | Role | Workflow(s) | Input Doc | Output Doc(s) |
|---|---|---|---|---|---|---|---|
| 01 | AGENT-planner.md | SYS-AG-PL | AGENT-planner | Solution Architect | sdlc_20_planning_v1 | INIT-DOC | REQ-DOC |
| 02 | AGENT-task-decomposer.md | SYS-AG-TD | AGENT-task-decomposer | Task Decomposer | sdlc_30, sdlc_40 | REQ-DOC (sdlc_30), PLAN-DOC (sdlc_40) | PLAN-DOC (sdlc_30), BACKLOG-DOC (sdlc_40) |
| 03 | AGENT-implementation-planner.md | SYS-AG-IP | AGENT-implementation-planner | Implementation Planner | sdlc_50_implementation_v1 | BACKLOG-DOC | TASK-DOC |
| 04 | AGENT-executor.md | SYS-AG-EX | AGENT-executor | Code Executor | sdlc_60_execution_v1 | TASK-DOC | IMPL-DOC |
| 05 | AGENT-reviewer.md | SYS-AG-RV | AGENT-reviewer | Independent Reviewer | sdlc_70, sdlc_80 | IMPL-DOC (sdlc_70), VALID-DOC (sdlc_80) | VALID-DOC (sdlc_70), REV-DOC (sdlc_80) |
| 06 | AGENT-memory-manager.md | SYS-AG-MM | AGENT-memory-manager | Memory Manager | sdlc_80_review_v1 | VALID-DOC | MEM-DOC, CLOSE-DOC |

## Agent Roles Summary

### AGENT-planner (Solution Architect)

Transforms an approved initiative document (INIT-DOC) into a structured
requirement document (REQ-DOC). Operates in sdlc_20_planning_v1 only.

### AGENT-task-decomposer (Task Decomposer)

Operates in two modes:
- sdlc_30 mode: Transforms an approved requirement document (REQ-DOC) into
  a plan document (PLAN-DOC).
- sdlc_40 mode: Transforms an approved plan document (PLAN-DOC) into a
  backlog document (BACKLOG-DOC).

### AGENT-implementation-planner (Implementation Planner)

Transforms an approved backlog document (BACKLOG-DOC) into a task
specification document (TASK-DOC). Operates in
sdlc_50_implementation_v1 only.

### AGENT-executor (Code Executor)

Transforms an approved task specification (TASK-DOC) into an implementation
record (IMPL-DOC) by implementing code and tests. Operates in
sdlc_60_execution_v1 only.

### AGENT-reviewer (Independent Reviewer)

Operates in two modes:
- sdlc_70 mode: Validates an approved implementation document (IMPL-DOC) and
  produces a validation report (VALID-DOC).
- sdlc_80 mode: Reviews a validated implementation (VALID-DOC) and produces
  a review decision document (REV-DOC).

### AGENT-memory-manager (Memory Manager)

Persists stable, reusable delivery knowledge after initiative completion.
Operates in sdlc_80_review_v1. Produces MEM-DOC and CLOSE-DOC from
an approved validation document (VALID-DOC).

## Agent-to-Template Cross-Reference

| Agent Contract | Consumes Template | Produces Document (Template) |
|---|---|---|
| AGENT-planner | 02_INIT_template.md | 03_REQ_template.md |
| AGENT-task-decomposer (sdlc_30) | 03_REQ_template.md | 04_PLAN_template.md |
| AGENT-task-decomposer (sdlc_40) | 04_PLAN_template.md | 05_BACKLOG_template.md |
| AGENT-implementation-planner | 05_BACKLOG_template.md | 06_TASK_template.md |
| AGENT-executor | 06_TASK_template.md | 07_IMPL_template.md |
| AGENT-reviewer (sdlc_70) | 07_IMPL_template.md | 08_VALID_template.md |
| AGENT-reviewer (sdlc_80) | 08_VALID_template.md | 09_REV_template.md |
| AGENT-memory-manager | 08_VALID_template.md | 10_MEM_template.md, 11_CLOSE_template.md |

## Delivery Status Rules

All agents MUST comply with the delivery status rules defined in:
02_agents/DELIVERY_STATUS_RULES_v1.md

Key rules:
- All output documents follow the lifecycle: draft -> changes_requested -> draft -> approved
- Approved documents are immutable
- Each workflow has a human approval gate before promotion
- Agents MUST NOT modify approved documents
- Agents MUST preserve upstream document linkage

## Document Lifecycle

Delivery documents produced or consumed by agents follow these lifecycle
states:

```
draft -> changes_requested -> draft (refine loop) -> approved
```

| Status | Meaning |
|---|---|
| draft | Initial document generated. Not yet reviewed. |
| changes_requested | Review identified fixable defects. |
| approved | All gates passed. Document is immutable. |

## Agent Contract Files

| File | Path |
|---|---|
| SDLC_AGENTS_INDEX | 02_agents/AGENTS.md |
| SDLC_AGENT_PLANNER | 02_agents/AGENT-planner.md |
| SDLC_AGENT_TASK_DECOMPOSER | 02_agents/AGENT-task-decomposer.md |
| SDLC_AGENT_IMPL_PLANNER | 02_agents/AGENT-implementation-planner.md |
| SDLC_AGENT_EXECUTOR | 02_agents/AGENT-executor.md |
| SDLC_AGENT_REVIEWER | 02_agents/AGENT-reviewer.md |
| SDLC_AGENT_MEMORY_MANAGER | 02_agents/AGENT-memory-manager.md |
| SDLC_DELIVERY_STATUS_RULES | 02_agents/DELIVERY_STATUS_RULES_v1.md |

## Cross-Agent Coordination Rules

### Rule 1 -- Role Isolation
Each agent MUST stay within its assigned role. No silent cross-role behavior.

### Rule 2 -- Document-First
Every meaningful output MUST exist as a file artifact following the correct
template and naming convention.

### Rule 3 -- No Scope Drift
Agents MUST NOT silently widen objectives, redesign architecture, or add
unapproved features.

### Rule 4 -- Explicit Decisions
Review and validation artifacts MUST include an explicit decision and
supporting evidence.

### Rule 5 -- Canonical Linking
Every output MUST preserve upstream IDs: Initiative ID, Plan ID, Task ID,
and any related review or validation IDs.

### Rule 6 -- Deterministic Naming
All output files MUST follow the naming convention defined in
WORKFLOW_SOP_v1.md.

### Rule 7 -- Approved Inputs Only
Agents MUST use approved upstream artifacts as input. If operating on
non-approved materials, this MUST be explicitly stated.

### Rule 8 -- Rejected Means Stop
If a review or validation result is rejected, no downstream execution may
continue until the issue is resolved.

### Rule 9 -- Superseded Means Inactive
Superseded artifacts MUST NOT be used as execution sources.

### Rule 10 -- Traceability is Mandatory
Every output MUST reference the governing input documents and key
dependencies.

## Workflow Sequence

SDLC initiative workflows execute in mandatory order. Each workflow depends
on the approved output of the previous workflow:

1. sdlc_10_requirement_v1 -- INIT-DOC from DRAFT-INIT (no agent)
2. sdlc_20_planning_v1 -- REQ-DOC from INIT-DOC (AGENT-planner)
3. sdlc_30_backlog_v1 -- PLAN-DOC from REQ-DOC (AGENT-task-decomposer)
4. sdlc_40_task_v1 -- BACKLOG-DOC from PLAN-DOC (AGENT-task-decomposer)
5. sdlc_50_implementation_v1 -- TASK-DOC from BACKLOG-DOC (AGENT-implementation-planner)
6. sdlc_60_execution_v1 -- IMPL-DOC from TASK-DOC (AGENT-executor)
7. sdlc_70_validation_v1 -- VALID-DOC from IMPL-DOC (AGENT-reviewer)
8. sdlc_80_review_v1 -- REV-DOC + MEM-DOC + CLOSE-DOC from VALID-DOC (AGENT-reviewer, AGENT-memory-manager)

## Related Documents

- SDLC Template Registry: 01_templates/template_registry.md
- SDLC Workflow SOP: 01_templates/WORKFLOW_SOP_v1.md
- Delivery Status Rules: 02_agents/DELIVERY_STATUS_RULES_v1.md
- Layer 1 Metadata Standard: GOVERNANCE_RUNTIME_ROOT/METADATA_STANDARD.md
- Layer 2 Metadata Contract: PLATFORM_RUNTIME_ROOT/METADATA_CONTRACT.md
- L3 SDLC Specification: masterplan/LAYER3_AI_DRIVEN_SDLC_SPECIFICATION.md

## Version History

| Version | Date | Change Summary |
|---|---|---|
| 1.0.0 | 2026-07-22 | Initial release. All 6 agent contracts plus index and status rules. |