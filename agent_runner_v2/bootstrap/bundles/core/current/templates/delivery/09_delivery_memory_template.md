---
title: Delivery Memory Template
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
created: 2026-07-04
template_id: DELIVERY-MEM-v1
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Memory Template

> Artifact key: `DELIVERY_MEMORY_TEMPLATE`

## Metadata

| Field | Value |
|---|---|
| Template ID | `DELIVERY-MEM-v1` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_templates` |
| Scope | Universal baseline — applies to all governed repositories |
| Status | `active` |
| Last Verified | 2026-07-04 |

This template defines the canonical structure for capturing delivery memory — outcomes, lessons, reusable patterns, and documentation notes from a completed delivery.

---

## Instance Preamble

```yaml
---
title: Delivery Memory — {MEMORY_ID}
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: memory_capture
created: {DATE}
template_id: DELIVERY-MEM-v1
memory_id: {MEMORY_ID}
initiative_id: {INITIATIVE_ID}
plan_id: {PLAN_ID}
status: draft
---
```

## Metadata

| Field | Value |
|---|---|
| Memory ID | `{MEMORY_ID}` |
| Initiative ID | `{INITIATIVE_ID}` |
| Plan ID | `{PLAN_ID}` |
| Created | `{DATE}` |
| Author / Agent | Memory Manager |
| Status | `draft` / `finalized` |

## Context

| Field | Value |
|---|---|
| Initiative Title | `{TITLE}` |
| Delivery Duration | `{DURATION}` |
| Team / Agents Involved | `{ROLES}` |
| Architecture Profile | `{PROFILE}` |
| Migration Mode | `{MODE}` |
| Key Context | `{CONTEXT_DESCRIPTION}` |

## Summary

| Field | Value |
|---|---|
| Executive Summary | `{ONE_PARAGRAPH_SUMMARY}` |
| Outcome | `success` / `partial` / `failure` |
| Key Achievements | `{ACHIEVEMENTS}` |
| Key Shortfalls | `{SHORTFALLS}` |

## Outcomes

| Outcome ID | Description | Category | Impact | Evidence |
|---|---|---|---|---|
| `{OUTCOME_ID}` | `{DESCRIPTION}` | `positive` / `negative` / `neutral` | `high` / `medium` / `low` | `{EVIDENCE}` |

## Lessons Learned

| Lesson ID | Lesson | Context | Applicability | Severity |
|---|---|---|---|---|
| `{LESSON_ID}` | `{LESSON}` | `{CONTEXT}` | `universal` / `profile_specific` | `critical` / `important` / `minor` |

## Reusable Patterns

| Pattern ID | Pattern Name | Description | When to Apply | Example |
|---|---|---|---|---|
| `{PATTERN_ID}` | `{NAME}` | `{DESCRIPTION}` | `{WHEN}` | `{EXAMPLE}` |

## Anti-Patterns

| Anti-Pattern ID | Anti-Pattern Name | Description | When to Avoid | Consequence |
|---|---|---|---|---|
| `{ANTIPATTERN_ID}` | `{NAME}` | `{DESCRIPTION}` | `{WHEN}` | `{CONSEQUENCE}` |

## Documentation Notes

This section captures documentation-specific observations from the delivery.

| Note ID | Note | Category | Action Required |
|---|---|---|---|
| `{NOTE_ID}` | `{NOTE}` | `freshness` / `stale` / `gap` / `improvement` | `{ACTION}` |

### Documentation Observations

- {OBSERVATION_1}
- {OBSERVATION_2}

### Documentation Debt Incurred

| Debt ID | Description | Location | Priority | Recommended Action |
|---|---|---|---|---|
| `{DEBT_ID}` | `{DESCRIPTION}` | `{LOCATION}` | `high` / `medium` / `low` | `{ACTION}` |

## Related Memories

| Memory ID | Relationship | Notes |
|---|---|---|
| `{MEMORY_ID}` | `supersedes` / `extends` / `contradicts` / `related` | {NOTES} |

## Notes

- {NOTE_1}
- {NOTE_2}
