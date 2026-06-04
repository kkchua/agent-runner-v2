---
Doc Type: 02_plan
Template Version: v1
Plan ID: PLAN-{{YYYYMMDD}}-{{NN}}
Initiative ID: {{INITIATIVE_ID}}
Title: {{TITLE}}
Status: draft | in_review | approved | finalized | superseded
Created By: {{AUTHOR}}
Created At: {{ISO_DATETIME}}
Reviewed By: {{REVIEWER}}
Reviewed At: {{ISO_DATETIME}}
Approved By: {{APPROVER}}
Approved At: {{ISO_DATETIME}}
Finalized At: {{ISO_DATETIME}}
---

# {{TITLE}}

## Plan Objective

<!-- One paragraph: what this plan delivers and how it advances the parent initiative within the agent-runner-v2 orchestration engine. -->

## Strategy Overview

> Reference workflow gates from WORKFLOW_SOP_v1.md and status transitions from DELIVERY_STATUS_RULES_v1.md. Do not redefine approval authority — the authority model lives in the status rules document.

- **Workflow Gate:** {{GATE_REFERENCE}}
- **Review Layer:** {{REVIEW_CONFIG}}
- **Validation Points:** {{VALIDATION_POINTS}}

## System Design

### Components

| Component | Responsibility | Owner |
|---|---|---|
| {{COMPONENT_1}} | {{RESPONSIBILITY}} | {{OWNER}} |
| {{COMPONENT_2}} | {{RESPONSIBILITY}} | {{OWNER}} |

### Data Flow

> Describe how data moves through the system: prompt template rendering from `prompts/<workflow>/<step>.txt` with context injection → coder invocation via coder_adapters.py (Claude CLI, Codex CLI, Qwen CLI) → meta.json sidecar polling → schema validation against llm_response_schema.json → routing through workflow_router.py (APPROVED → advance; REJECTED → refine loop or replan; EXCEPTION → classify_failure → route_after_failure).

1. {{DATA_FLOW_STEP_1}}
2. {{DATA_FLOW_STEP_2}}

### Integrations

| Integration | Direction | Protocol/Interface | Notes |
|---|---|---|---|
| {{INTEGRATION_1}} | {{IN/OUT}} | {{PROTOCOL}} | {{NOTES}} |
| {{INTEGRATION_2}} | {{IN/OUT}} | {{PROTOCOL}} | {{NOTES}} |

### Key Design Decisions

| Decision | Rationale | Alternatives Considered |
|---|---|---|
| {{DECISION_1}} | {{RATIONALE}} | {{ALTERNATIVES}} |
| {{DECISION_2}} | {{RATIONALE}} | {{ALTERNATIVES}} |

## Task Breakdown

| Task ID | Task Name | Description | Owner | Priority | Depends On |
|---|---|---|---|---|---|
| TASK-{{NN}} | {{TASK_NAME}} | {{DESCRIPTION}} | {{OWNER}} | {{P1-P4}} | TASK-{{NN}} or — |
| TASK-{{NN}} | {{TASK_NAME}} | {{DESCRIPTION}} | {{OWNER}} | {{P1-P4}} | TASK-{{NN}} or — |

## Scope Mapping

> Map tasks to scope items from the parent initiative.

- `TASK-{{NN}}` → {{SCOPE_ITEM}}
- `TASK-{{NN}}` → {{SCOPE_ITEM}}

## Explicitly Excluded / Not Planned

> Items that were considered but deliberately left out of this plan.

- {{EXCLUDED_ITEM_1}}
- {{EXCLUDED_ITEM_2}}

## Deliverables

| Deliverable | Artifact Type | Path | Acceptance Gate |
|---|---|---|---|
| {{DELIVERABLE_1}} | {{ARTIFACT_TYPE}} | {{PATH}} | {{GATE}} |
| {{DELIVERABLE_2}} | {{ARTIFACT_TYPE}} | {{PATH}} | {{GATE}} |

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| {{RISK_1}} | {{H/M/L}} | {{H/M/L}} | {{MITIGATION}} |
| {{RISK_2}} | {{H/M/L}} | {{H/M/L}} | {{MITIGATION}} |

## Execution Flow

> Ordered phases with parallelism notes. Independent task-graph branches may run in parallel per task_execution_v1 workflow rules. Refine loops have a max iteration budget (typically 2); replan attempts limited to 1. Planning attempt budget: max 5.

1. **Phase 1 — {{PHASE_NAME}}**
   - Tasks: `TASK-{{NN}}`, `TASK-{{NN}}`
   - Parallel: {{YES/NO}} — {{DETAILS}}
2. **Phase 2 — {{PHASE_NAME}}**
   - Tasks: `TASK-{{NN}}`, `TASK-{{NN}}`
   - Parallel: {{YES/NO}} — {{DETAILS}}

## Acceptance Criteria

> Conditions that must be met before this plan is considered fully delivered: all artifacts generated with matching meta.json sidecars, all reviews approved per DELIVERY_STATUS_RULES_v1.md, tests passing via pytest, job state transitions verified through job_state.py.

- {{CRITERION_1}}
- {{CRITERION_2}}

## References

| Reference | Link | Purpose |
|---|---|---|
| Parent Initiative | docs/delivery/01_initiatives/{{INIT_FILE}} | Scope and objectives |
| Workflow SOP | docs/delivery/00_templates/WORKFLOW_SOP_v1.md | Process rules and agent contracts |
| Status Rules | docs/delivery/00_templates/DELIVERY_STATUS_RULES_v1.md | Lifecycle authority and state transitions |
| Template Registry | docs/delivery/00_templates/template_registry.md | Artifact type definitions |
| Model Mapping | agent_runner_v2/model_mapping.json | Coder alias definitions |

## Notes

{{ADDITIONAL_NOTES}}

## Approval

| Role | Name | Date | Signature |
|---|---|---|---|
| Plan Author | {{AUTHOR}} | {{DATE}} | |
| Reviewer | {{REVIEWER}} | {{DATE}} | |
| Architect / Sponsor | {{APPROVER}} | {{DATE}} | |
