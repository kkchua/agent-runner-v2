---
Doc Type: 02b_task_graph
Template Version: v1
Task Graph ID: TASK-GRAPH-{{YYYYMMDD}}-{{NN}}
Plan ID: {{PLAN_ID}}
Initiative ID: {{INITIATIVE_ID}}
Title: {{TITLE}}
Status: draft | in_review | approved | superseded
Reviewed By: {{REVIEWER}}
Reviewed At: {{ISO_DATETIME}}
Approved By: {{APPROVER}}
Approved At: {{ISO_DATETIME}}
---

# Task Graph — {{TITLE}}

## Task Graph Objective

<!-- One paragraph: what this task graph decomposes and why this structure was chosen for the agent-runner-v2 delivery pipeline. -->

## Task Graph

### TASK-{{NN}} — {{TASK_TITLE}}

- **Description:** {{DESCRIPTION}}
- **Owner:** {{OWNER}}
- **Priority:** {{P1-P4}}
- **Depends On:** `TASK-{{NN}}` or —
- **Scope:** {{SCOPE_BOUNDARY}}
- **Deliverables:**
  - {{DELIVERABLE_1}}
  - {{DELIVERABLE_2}}
- **Testability:** {{HOW_THIS_TASK_IS_TESTED}} — e.g., unit test in tests/, integration test via `ukbe-run-agent --dry-run`, pytest fixture exercising step_runner.py or coder_adapters.py
- **Review Criteria:**
  - {{CRITERION_1}}
  - {{CRITERION_2}}

### TASK-{{NN}} — {{TASK_TITLE}}

- **Description:** {{DESCRIPTION}}
- **Owner:** {{OWNER}}
- **Priority:** {{P1-P4}}
- **Depends On:** `TASK-{{NN}}` or —
- **Scope:** {{SCOPE_BOUNDARY}}
- **Deliverables:**
  - {{DELIVERABLE_1}}
  - {{DELIVERABLE_2}}
- **Testability:** {{HOW_THIS_TASK_IS_TESTED}}
- **Review Criteria:**
  - {{CRITERION_1}}
  - {{CRITERION_2}}

## Execution Flow

> Tracks with parallelism and validation layer. Tasks with no mutual dependencies may execute in parallel under task_execution_v1 workflow rules. Each phase includes a validation gate that verifies meta.json sidecars and artifact structure.

```
Phase 1: TASK-01, TASK-02  [parallel: YES]
  └── Validation: {{VALIDATION_GATE_1}}
Phase 2: TASK-03             [depends: TASK-01, TASK-02]
  └── Validation: {{VALIDATION_GATE_2}}
Phase 3: TASK-04, TASK-05  [parallel: YES, depends: TASK-03]
  └── Validation: {{VALIDATION_GATE_3}}
```

## Task Success Criteria

> Conditions for the entire task graph to be considered complete: all task artifacts generated at canonical paths under docs/delivery/, all meta.json sidecars valid per llm_response_schema.json, all reviews approved per DELIVERY_STATUS_RULES_v1.md, no pending refine loops, job status transitions through job_state.py verified.

- {{GRAPH_CRITERION_1}}
- {{GRAPH_CRITERION_2}}

## References

| Reference | Link | Purpose |
|---|---|---|
| Parent Plan | docs/delivery/02_plans/{{PLAN_FILE}} | Task source and strategy |
| Parent Initiative | docs/delivery/01_initiatives/{{INIT_FILE}} | Scope authority |
| Workflow SOP | docs/delivery/00_templates/WORKFLOW_SOP_v1.md | Agent roles and handoff rules |
| Task Execution Workflow | template_groups.py → task_execution_v1 | Execution binding and refine loops |

## Notes

{{ADDITIONAL_NOTES}}
