---
Doc Type: 04_review
Template Version: v1
Review ID: REVIEW-{{YYYYMMDD}}-{{NN}}
Related Doc Type: {{01_initiative / 02_plan / 02b_task_graph / 03_task / 04_implementation_plan}}
Related Doc ID: {{RELATED_DOC_ID}}
Title: {{TITLE}}
Reviewer: {{REVIEWER}}
Status: in_progress | approved | rejected
Review Date: {{ISO_DATETIME}}
---

# Review — {{TITLE}}

## Review Objective

<!-- What this review is assessing and why. Reference the artifact being reviewed and the agent-runner-v2 workflow context. -->

## Summary of Reviewed Content

<!-- Brief summary of the document under review, including which template group produced it, which step, and which coder was invoked. -->

## Strengths

<!-- What the document does well: clear scope boundaries, correct meta.json sidecar references, proper exception routing alignment, adherence to WORKFLOW_SOP_v1.md agent contracts, meta.json-only communication contract compliance. -->

- {{STRENGTH_1}}
- {{STRENGTH_2}}

## Issues Identified

| Issue | Severity | Recommendation |
|---|---|---|
| {{ISSUE_1}} | {{CRITICAL/HIGH/MEDIUM/LOW}} | {{RECOMMENDATION}} |
| {{ISSUE_2}} | {{CRITICAL/HIGH/MEDIUM/LOW}} | {{RECOMMENDATION}} |

## Suggested Improvements

> Non-blocking suggestions for clarity, robustness, or maintainability.

- {{IMPROVEMENT_1}}
- {{IMPROVEMENT_2}}

## Validation Against Acceptance Criteria

| Criterion | Result | Notes |
|---|---|---|
| {{CRITERION_1}} | {{PASS/FAIL/N/A}} | {{NOTES}} |
| {{CRITERION_2}} | {{PASS/FAIL/N/A}} | {{NOTES}} |

## Final Decision

| Field | Value |
|---|---|
| Decision | APPROVED | REJECTED | CONDITIONAL |
| Rationale | {{RATIONALE}} |
| Required Next Action | {{ACTION_IF_REJECTED_OR_CONDITIONAL}} |

## References

| Reference | Link | Purpose |
|---|---|---|
| Reviewed Document | docs/delivery/{{PATH}} | Artifact under review |
| Review Criteria | docs/delivery/00_templates/DELIVERY_STATUS_RULES_v1.md | Authority model and state transitions |
| Workflow SOP | docs/delivery/00_templates/WORKFLOW_SOP_v1.md | Agent roles and handoff rules |
| LLM Response Schema | agent_runner_v2/llm_response_schema.json | Expected coder output structure |

## Notes

{{ADDITIONAL_NOTES}}

## Naming Contract

> Review files must be named: `REVIEW-{{YYYYMMDD}}-{{NN}}_review-of-{{RELATED_DOC_SLUG}}.md` in docs/delivery/05_reviews/. Each review must have a matching *.meta.json sidecar with the reviewer's structured decision.
