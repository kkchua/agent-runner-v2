---
template_id: SYS-03-TR
version: "1.0.0"
doc_type: "bundle_definition"
authority: "sdlc-owned"
scan_policy: "include"
scan_reason: "Master index of all SDLC delivery document templates for governance scanning"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "SDLC00CS-1zcrrbbs"
---

> Managed by workflow: `sdlc_00_codebase_scaffold_v1` / step: `publish_sdlc_scaffold`
> This file is workflow-generated and protected from manual edits.

# SDLC Template Registry

## Purpose

This document is the master index of all SDLC delivery document templates
for the agent-runner-v2 platform. It maps each template to its purpose,
target workflow, producing workflow step, storage location, and current
version. This registry is the authoritative source of truth for which
template governs which SDLC artifact.

## Scope

This registry covers templates for Layer 3 AI-Driven SDLC workflow
delivery documents only. It does not cover Layer 1 governance templates,
Layer 2 platform constitution templates, or agent contract definitions
(which are cataloged in a separate registry under 02_agents/).

## Template Cross-Reference Table

| # | Template File | Template ID | Artifact Prefix | Producing Workflow | Input Source | Storage Folder |
|---|---|---|---|---|---|---|
| 01 | 01_DRAFT_INIT_template.md | SYS-03-DI | DRAFT-INIT | (user-authored) | Human input | draftinitiates/ |
| 02 | 02_INIT_template.md | SYS-03-IN | INIT | sdlc_10_requirement_v1 | DRAFT-INIT-DOC | initiatives/ |
| 03 | 03_REQ_template.md | SYS-03-RQ | REQ | sdlc_20_planning_v1 | INIT-DOC | requirements/ |
| 04 | 04_PLAN_template.md | SYS-03-PL | PLAN | sdlc_30_backlog_v1 | REQ-DOC | plans/ |
| 05 | 05_BACKLOG_template.md | SYS-03-BL | BACKLOG | sdlc_40_task_v1 | PLAN-DOC | backlogs/ |
| 06 | 06_TASK_template.md | SYS-03-TK | TASK | sdlc_50_implementation_v1 | BACKLOG-DOC | tasks/ |
| 07 | 07_IMPL_template.md | SYS-03-IM | IMPL | sdlc_60_execution_v1 | TASK-DOC | implementations/ |
| 08 | 08_VALID_template.md | SYS-03-VL | VALID | sdlc_70_validation_v1 | IMPL-DOC | validations/ |
| 09 | 09_REV_template.md | SYS-03-RV | REV | sdlc_80_review_v1 | VALIDATE-DOC | reviews/ |
| 10 | 10_MEM_template.md | SYS-03-MM | MEM | sdlc_80_review_v1 | VALIDATE-DOC | reviews/ |
| 11 | 11_CLOSE_template.md | SYS-03-CL | CLOSE | sdlc_80_review_v1 | VALIDATE-DOC | reviews/ |

## Template-to-Workflow Dependency Map

### Workflow Dependencies

Each template is consumed by a downstream workflow as an input reference:

| Template | Consumed By | Purpose |
|---|---|---|
| 01_DRAFT_INIT_template.md | sdlc_10_requirement_v1 | Template for user-authored draft initiative |
| 02_INIT_template.md | sdlc_20_planning_v1 | Template for approved initiative doc |
| 03_REQ_template.md | sdlc_30_backlog_v1 | Template for approved requirement doc |
| 04_PLAN_template.md | sdlc_40_task_v1 | Template for approved plan doc |
| 05_BACKLOG_template.md | sdlc_50_implementation_v1 | Template for approved backlog doc |
| 06_TASK_template.md | sdlc_60_execution_v1 | Template for approved task spec doc |
| 07_IMPL_template.md | sdlc_70_validation_v1 | Template for approved implementation doc |
| 08_VALID_template.md | sdlc_80_review_v1 | Template for approved validation doc |
| 09_REV_template.md | (closure) | Template for approved review doc |
| 10_MEM_template.md | (closure) | Template for approved memory doc |
| 11_CLOSE_template.md | (closure) | Template for approved closure doc |

### Artifact Flow Chain

```
DRAFT-INIT (user-authored, 01_DRAFT_INIT_template.md)
    | sdlc_10_requirement_v1
    v
INIT-DOC (02_INIT_template.md)
    | sdlc_20_planning_v1
    v
REQ-DOC (03_REQ_template.md)
    | sdlc_30_backlog_v1
    v
PLAN-DOC (04_PLAN_template.md)
    | sdlc_40_task_v1
    v
BACKLOG-DOC (05_BACKLOG_template.md)
    | sdlc_50_implementation_v1
    v
TASK-DOC (06_TASK_template.md)
    | sdlc_60_execution_v1
    v
IMPL-DOC (07_IMPL_template.md)
    | sdlc_70_validation_v1
    v
VALIDATE-DOC (08_VALID_template.md)
    | sdlc_80_review_v1
    v
REV-DOC + MEM-DOC + CLOSE-DOC (09_REV, 10_MEM, 11_CLOSE templates)
```

## Standard Step Pattern

All initiative workflows (sdlc_10 through sdlc_80) follow this standard
step pattern for document generation and approval:

1. generate_<artifact> (prompt) -- Generate the document from input.
2. technical_critique (prompt) -- Internal quality gate that evaluates
   feasibility and technical soundness.
3. address_critique (prompt) -- Address findings from technical critique,
   update document in-place, add Critique Resolution section.
4. review_<artifact> (prompt) -- Human approval gate that verifies
   critique was resolved and document meets standards.
5. refine_<artifact> (prompt, conditional) -- Refine based on review
   feedback.
6. promote_<artifact> (action) -- Promote document to approved status.
7. step_completion (action) -- Finalize and notify.

## Template Version History

| Version | Date | Change Summary |
|---|---|---|
| 1.0.0 | 2026-08-17 | Initial release. All 11 document templates plus registry and SOP. |

## Cross-References to Agent Contracts

The following table maps each template to its producing agent contract.
The authoritative agent-to-workflow mapping is defined in AGENTS.md.

| Template ID | Template Name | Producing Workflow | Agent Contract |
|---|---|---|---|
| SYS-03-DI | DRAFT_INIT | (user-authored) | (none) |
| SYS-03-IN | INIT | sdlc_10_requirement_v1 | (none -- workflow's own prompts) |
| SYS-03-RQ | REQ | sdlc_20_planning_v1 | AGENT-planner |
| SYS-03-PL | PLAN | sdlc_30_backlog_v1 | AGENT-task-decomposer |
| SYS-03-BL | BACKLOG | sdlc_40_task_v1 | AGENT-task-decomposer |
| SYS-03-TK | TASK | sdlc_50_implementation_v1 | AGENT-implementation-planner |
| SYS-03-IM | IMPL | sdlc_60_execution_v1 | AGENT-executor |
| SYS-03-VL | VALID | sdlc_70_validation_v1 | AGENT-reviewer |
| SYS-03-RV | REV | sdlc_80_review_v1 | AGENT-reviewer |
| SYS-03-MM | MEM | sdlc_80_review_v1 | AGENT-memory-manager |
| SYS-03-CL | CLOSE | sdlc_80_review_v1 | AGENT-memory-manager |

## Related Documents

- SDLC Workflow SOP: WORKFLOW_SOP_v1.md (this directory)
- Agent Contract Registry: 02_agents/AGENTS.md (separate registry)
- Layer 1 Metadata Standard: METADATA_STANDARD.md (governance foundation)
- Layer 2 Metadata Contract: METADATA_CONTRACT.md (platform constitution)
- Delivery Status Rules: 02_agents/DELIVERY_STATUS_RULES_v1.md