---
Doc Type: 01_initiative
Template Version: v1
Initiative ID: INIT-{{YYYYMMDD}}-{{NN}}
Title: {{TITLE}}
Status: draft | in_review | approved | superseded | archived
Owner: {{OWNER}}
Workflow Governance In Scope: WORKFLOW_SOP_v1, DELIVERY_STATUS_RULES_v1
Created At: {{ISO_DATETIME}}
Approved At: {{ISO_DATETIME}}
---

# {{TITLE}}

## Objective

<!-- One paragraph: what this initiative aims to achieve and why it matters for the agent-runner-v2 LLM workflow orchestration engine. -->

## Problem Statement

<!-- Describe the problem or gap this initiative addresses within the runner's orchestration capabilities, coder adapter layer, workflow template system, or delivery pipeline architecture. -->

## Expected Outcomes

### Business

<!-- Measurable business impact or operational improvement. -->

### Technical

<!-- Technical improvements: new workflow template groups, coder adapter extensions, model alias additions, job state machine enhancements, or delivery governance improvements. -->

### User

<!-- End-user or developer experience improvements for the `ukbe-run-agent` CLI or delivery pipeline users. -->

## Scope

### Included

<!-- What is explicitly in scope. Use bullet points. -->

### Excluded

<!-- What is explicitly out of scope. Use bullet points. -->

## Constraints

<!-- Hard boundaries: backward compatibility with direct-execution path, meta.json sidecar as only communication channel, no pre-invocation sidecar writes, explicit exception routing to route_after_failure(), preservation of existing workflow template groups. -->

## Dependencies

<!-- Other initiatives, systems, or artifacts this initiative depends on. Reference by ID. Include external dependencies like PostgreSQL for daemon mode, coder CLI tools, or API keys. -->

## Success Criteria

<!-- Specific, testable conditions: all pytest tests pass, new workflow template registered in template_groups.py, meta.json sidecars valid per llm_response_schema.json, job state transitions verified through job_state.py. -->

## References

<!-- Links to QWEN.md, job_schema.json, llm_response_schema.json, workflow SOP, delivery status rules, or external specifications. -->

## Notes

<!-- Additional context, trade-off discussions, or open questions about runner architecture, coder adapter contracts, or delivery governance. -->

## Approval

| Role | Name | Decision | Date |
|------|------|----------|------|
| Architect | {{ARCHITECT}} | approved | {{ISO_DATETIME}} |
