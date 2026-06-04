---
Doc Type: 06_memory
Template Version: v1
Memory ID: MEM-{{YYYYMMDD}}-{{NN}}
Title: {{TITLE}}
Version: {{VERSION}}
Status: active | superseded | archived
Last Updated: {{ISO_DATETIME}}
Owner: {{OWNER}}
---

# {{TITLE}}

## Purpose

<!-- Why this memory record exists and what durable knowledge it preserves for the agent-runner-v2 delivery pipeline. -->

## Key Decisions

> Decisions made during the initiative that future teams need to know.

| Decision | Rationale | Date | Decision Maker |
|---|---|---|---|
| {{DECISION_1}} | {{RATIONALE}} | {{DATE}} | {{WHO}} |
| {{DECISION_2}} | {{RATIONALE}} | {{DATE}} | {{WHO}} |

## Architecture Notes

> Architectural choices, patterns, or constraints: artifact_paths.py as single source of truth for path computation, dataclass patterns for StepResult/UsageData/InvocationManifest/InvocationResult, PathProxy in runtime_context.py, job state machine lifecycle in job_state.py, model alias resolution in model_config.py, coder invocation layer in coder_adapters.py, failure classification matrix (AUTO_RETRYABLE, HUMAN_RETRY_REQUIRED, FATAL).

{{ARCHITECTURE_NOTES}}

## Important References

### Initiative IDs

- `INIT-{{YYYYMMDD}}-{{NN}}` — {{PURPOSE}}

### Plan IDs

- `PLAN-{{YYYYMMDD}}-{{NN}}` — {{PURPOSE}}

### Task IDs

- `TASK-{{YYYYMMDD}}-{{NN}}` — {{PURPOSE}}

### Review IDs

- `REVIEW-{{YYYYMMDD}}-{{NN}}` — {{PURPOSE}}

### External References

| Reference | Link | Purpose |
|---|---|---|
| {{EXT_REF_1}} | {{LINK}} | {{PURPOSE}} |
| {{EXT_REF_2}} | {{LINK}} | {{PURPOSE}} |

## Known Issues

> Issues, limitations, or technical debt recorded during delivery.

| Issue | Impact | Workaround | Tracking ID |
|---|---|---|---|
| {{ISSUE_1}} | {{IMPACT}} | {{WORKAROUND}} | {{TICKET_ID}} |
| {{ISSUE_2}} | {{IMPACT}} | {{WORKAROUND}} | {{TICKET_ID}} |

## Learnings

> Lessons learned that should inform future work on the orchestration engine or delivery workflows.

- {{LEARNING_1}}
- {{LEARNING_2}}

## Change Log

| Date | Change | Author |
|---|---|---|
| {{YYYY-MM-DD}} | {{CHANGE_DESCRIPTION}} | {{AUTHOR}} |
| {{YYYY-MM-DD}} | {{CHANGE_DESCRIPTION}} | {{AUTHOR}} |

## Notes

{{ADDITIONAL_NOTES}}
