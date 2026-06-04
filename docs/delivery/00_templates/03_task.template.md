---
Doc Type: 03_task
Template Version: v1
Task ID: TASK-{{YYYYMMDD}}-{{NN}}
Plan ID: {{PLAN_ID}}
Title: {{TITLE}}
Status: pending | in_progress | in_review | approved | rejected | completed
Priority: P1 | P2 | P3 | P4
Assigned To: {{ASSIGNEE}}
Created At: {{ISO_DATETIME}}
Due At: {{ISO_DATETIME}}
---

# {{TITLE}}

## Objective

<!-- One paragraph: what this task achieves within the agent-runner-v2 delivery pipeline. Focus on WHAT, not HOW. -->

## Inputs

| Type | Reference |
|---|---|
| Source Plan | docs/delivery/02_plans/{{PLAN_FILE}} |
| Dependencies | `TASK-{{NN}}`, `TASK-{{NN}}` or — |
| Required Documents | {{DOC_1}}, {{DOC_2}} |
| Required Data/APIs | {{API_OR_DATA_SOURCE}} |

## Outputs

| Artifact | Path | Description |
|---|---|---|
| {{OUTPUT_1}} | docs/delivery/{{PATH}} | {{DESCRIPTION}} |
| {{OUTPUT_2}} | docs/delivery/{{PATH}} | {{DESCRIPTION}} |

### Completion Evidence

> What proves this task is done: meta.json sidecar at `{artifact}.meta.json` with valid schema per llm_response_schema.json, pytest outputs, review approval in docs/delivery/05_reviews/, successful `ukbe-run-agent` execution with exit_code=0.

- {{EVIDENCE_1}}
- {{EVIDENCE_2}}

## Implementation Details

### Technical Notes

{{TECHNICAL_NOTES}}

### API/Contract Notes

> Interfaces this task introduces or modifies: new step types in template_groups.py, sidecar schema extensions, CLI flags in run_agent.py, coder adapter changes in coder_adapters.py, or model alias entries in model_mapping.json.

| Interface | Direction | Schema/Contract | Notes |
|---|---|---|---|
| {{INTERFACE_1}} | {{IN/OUT}} | {{SCHEMA_REF}} | {{NOTES}} |

### Data/Schema Notes

> Data structures, JSON schemas, or migrations: job_schema.json, usage_schema.json, dataclasses in step_runner.py (StepResult, UsageData, InvocationManifest, InvocationResult), job_state.py lifecycle management, workflow_router.py routing logic, artifact_paths.py path computation.

{{DATA_SCHEMA_NOTES}}

## Execution Steps

> Ordered steps within the agent-runner-v2 workflow. Reference the appropriate workflow template group.

1. {{STEP_1}}
2. {{STEP_2}}
3. {{STEP_3}}

## Validation Criteria

### Acceptance Checks

- {{CHECK_1}}
- {{CHECK_2}}

### Test Cases

| Test ID | Scenario | Expected Result |
|---|---|---|
| {{TEST_1}} | {{SCENARIO}} | {{EXPECTED}} |
| {{TEST_2}} | {{SCENARIO}} | {{EXPECTED}} |

### Review Requirements

> What a reviewer must verify: code style (type hints, `from __future__ import annotations`), dataclass usage, explicit exception types from exceptions.py, no implicit error recovery, meta.json sidecar contract compliance, deterministic outputs.

- {{REVIEW_REQ_1}}
- {{REVIEW_REQ_2}}

## Risks / Blockers

| Risk / Blocker | Impact | Mitigation / Resolution |
|---|---|---|
| {{RISK_1}} | {{IMPACT}} | {{MITIGATION}} |
| {{RISK_2}} | {{IMPACT}} | {{MITIGATION}} |

## References

| Reference | Link | Purpose |
|---|---|---|
| Parent Plan | docs/delivery/02_plans/{{PLAN_FILE}} | Task source |
| Task Graph | docs/delivery/02_plans/artifacts/{{TASK_GRAPH_FILE}} | Dependency map |
| Related Task | docs/delivery/03_tasks/{{RELATED_TASK}} | Upstream/downstream |
| Workflow SOP | docs/delivery/00_templates/WORKFLOW_SOP_v1.md | Agent roles and handoff rules |

## Notes

{{ADDITIONAL_NOTES}}
