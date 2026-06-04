---
Doc Type: 04_implementation_plan
Template Version: v1
Plan ID: {{PLAN_ID}}
Task ID: {{TASK_ID}}
Title: {{TITLE}}
Status: draft | in_review | approved | superseded
Created At: {{ISO_DATETIME}}
Author: {{AUTHOR}}
---

# {{TITLE}}

## Objective

<!-- HOW this task will be implemented within the agent-runner-v2 architecture — not WHAT. -->

## Inputs

| Type | Reference |
|---|---|
| Task Document | docs/delivery/03_tasks/{{TASK_FILE}} |
| Design / Spec | {{SPEC_PATH}} |
| Existing Code | agent_runner_v2/{{CODE_PATH}} |
| Dependencies | `TASK-{{NN}}` or — |

## Outputs

| Artifact | Path | Description |
|---|---|---|
| {{OUTPUT_1}} | {{PATH}} | {{DESCRIPTION}} |
| {{OUTPUT_2}} | {{PATH}} | {{DESCRIPTION}} |

## Scope Clarification

### Included

- {{SCOPE_ITEM_1}}
- {{SCOPE_ITEM_2}}

### Excluded

- {{EXCLUDED_ITEM_1}}
- {{EXCLUDED_ITEM_2}}

## File Plan

> MANDATORY — tree of files to create or modify with [NEW] / [MODIFY] tags.

```
agent_runner_v2/
├── [NEW]   {{NEW_MODULE}}.py              # {{PURPOSE}}
├── [NEW]   test_{{NEW_TEST_FILE}}.py      # {{PURPOSE}}
├── [MODIFY] {{EXISTING_FILE}}.py          # {{CHANGE_SUMMARY}}
├── [NEW]   prompts/{{WORKFLOW}}/{{STEP}}.txt  # {{PURPOSE}}
└── [MODIFY] template_groups.py            # {{CHANGE_SUMMARY}}

tests/
├── [NEW]   test_{{NEW_MODULE}}.py         # {{PURPOSE}}
└── [MODIFY] test_{{EXISTING_TEST}}.py     # {{CHANGE_SUMMARY}}

docs/delivery/
└── [NEW]   {{DELIVERY_ARTIFACT}}.md       # {{PURPOSE}}
```

## Module Responsibilities

> What each new or modified module is responsible for within the runner architecture.

| Module | Responsibility |
|---|---|
| {{MODULE_1}} | {{RESPONSIBILITY}} |
| {{MODULE_2}} | {{RESPONSIBILITY}} |

## Reuse Strategy

> What existing code, libraries, or patterns this implementation reuses: artifact_paths.py for path computation, runner_logger.py for structured logging, exceptions.py for custom error types, dataclass patterns from step_runner.py, PathProxy in runtime_context.py.

- Reuse `{{EXISTING_MODULE}}` for {{PURPOSE}}
- Follow pattern from `agent_runner_v2/{{REFERENCE_FILE}}.py`

## Data Flow

> How data moves through the new or modified code: prompt template rendering → coder invocation via coder_adapters.py → meta.json sidecar polling → schema validation → routing through workflow_router.py → job state update via job_state.py.

1. {{FLOW_STEP_1}}
2. {{FLOW_STEP_2}}
3. {{FLOW_STEP_3}}

## Test Plan

### Test Files

| Test File | Covers |
|---|---|
| test_{{FILE_1}}.py | {{COVERAGE}} |
| test_{{FILE_2}}.py | {{COVERAGE}} |

### Test Cases

| Test ID | Scenario | Expected | Assertions |
|---|---|---|---|
| T-001 | {{SCENARIO}} | {{EXPECTED}} | {{ASSERTIONS}} |
| T-002 | {{SCENARIO}} | {{EXPECTED}} | {{ASSERTIONS}} |

### Test Constraints

- {{CONSTRAINT_1}} — e.g., requires coder CLIs installed, API keys set in environment
- {{CONSTRAINT_2}} — e.g., Python 3.11+, pytest>=8.2.0, pytest-cov>=5.0.0

## Constraints

> Technical or operational constraints.

- Python 3.11+ with type hints and `from __future__ import annotations`
- Dataclasses for structured data (StepResult, UsageData, InvocationManifest, InvocationResult)
- Explicit exception types from exceptions.py — no implicit error paths
- meta.json sidecar is the ONLY communication channel — no stdout JSON parsing
- No pre-invocation sidecar writes by the runner
- Explicit exception routing — hard failures go to route_after_failure() immediately
- Deterministic outputs: stable IDs, normalized structure
- Supersession links required when replacing approved artifacts

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| {{RISK_1}} | {{H/M/L}} | {{H/M/L}} | {{MITIGATION}} |
| {{RISK_2}} | {{H/M/L}} | {{H/M/L}} | {{MITIGATION}} |

## Dependencies

> Code, services, or data this implementation depends on.

| Dependency | Version / Source | Notes |
|---|---|---|
| {{DEP_1}} | {{VERSION}} | {{NOTES}} |
| {{DEP_2}} | {{VERSION}} | {{NOTES}} |

## Notes

{{ADDITIONAL_NOTES}}

## Ready for Execution

> Checklist before handing off to the executor.

- [ ] File plan reviewed and complete
- [ ] Test plan covers all acceptance criteria
- [ ] Dependencies identified and available
- [ ] Scope boundaries are explicit (included vs excluded)
- [ ] Risks documented with mitigations
- [ ] Approved by {{APPROVER}}
