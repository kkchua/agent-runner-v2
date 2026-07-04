---
title: Delivery Plan Template
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
created: 2026-07-04
template_id: DELIVERY-PLAN-v1
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Plan Template

> Artifact key: `DELIVERY_PLAN_TEMPLATE`

## Metadata

| Field | Value |
|---|---|
| Template ID | `DELIVERY-PLAN-v1` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_templates` |
| Scope | Universal baseline — applies to all governed repositories |
| Architecture Profile | Conditional — populated from repository context |
| Migration Mode | Conditional — populated when repo standard is unclear or changing |
| Status | `active` |
| Last Verified | 2026-07-04 |

This template defines the canonical structure for a delivery plan. Every plan artifact must conform to this structure.

---

## Instance Preamble

```yaml
---
title: Delivery Plan — {PLAN_ID}
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: delivery_planning_v1
created: {DATE}
template_id: DELIVERY-PLAN-v1
plan_id: {PLAN_ID}
initiative_id: {INITIATIVE_ID}
status: draft
current_profile: {CURRENT_PROFILE}
target_profile: {TARGET_PROFILE}
migration_mode: {MIGRATION_MODE}
---
```

## Metadata

| Field | Value |
|---|---|
| Plan ID | `{PLAN_ID}` |
| Initiative ID | `{INITIATIVE_ID}` |
| Created | `{DATE}` |
| Author / Agent | Planner |
| Status | `draft` / `approved` / `rejected` |
| Current Architecture Profile | `{CURRENT_PROFILE}` |
| Target Architecture Profile | `{TARGET_PROFILE}` |
| Migration Mode | `{MIGRATION_MODE}` |

**Profile and migration fields are conditional:**
- MUST be populated when the repository standard is unclear or changing.
- When the repo standard is well-established and not changing, the fields MAY carry the known values or `n/a`.

## Plan Objective

| Field | Value |
|---|---|
| Objective | `{OBJECTIVE}` |
| Success Definition | `{WHAT_DONE_LOOKS_LIKE}` |
| Key Results | `{MEASURABLE_OUTCOMES}` |

## Strategy Overview

| Field | Value |
|---|---|
| Approach | `{APPROACH_DESCRIPTION}` |
| Phasing | `{PHASING_STRATEGY}` |
| Constraints | `{KNOWN_CONSTRAINTS}` |
| Non-Goals | `{EXPLICIT_NON_GOALS}` |

## Scope Mapping

### Baseline Documentation Obligations (Universal)

These obligations apply to every delivery regardless of architecture profile:

| Obligation | Scope | Verification |
|---|---|---|
| Touch-module doc freshness | Every modified module must have a current `docs/codebase/02_modules/` entry | `validate_codebase_docs` action |
| Sidecar contract compliance | Every step emits v2 `meta.json` | `validate_delivery_docs` action |
| Change-impact record | `docs/codebase/04_changes/` entry for the delivery | Manual review |
| Protected-doc banner | All generated docs carry workflow banner | Automated check |

### Profile-Specific Architectural Obligations (Conditional)

These obligations apply only when the delivery introduces or changes an architecture profile:

| Obligation | Profile | Verification |
|---|---|---|
| {PROFILE_OBLIGATION} | `{PROFILE_NAME}` | `{METHOD}` |

**Rule:** Baseline obligations are always active. Profile-specific obligations are activated only when the initiative's `current_profile` or `target_profile` fields are populated with a non-universal value.

### Affected Modules

| Module | Change Type | Documentation Required |
|---|---|---|
| `{MODULE_PATH}` | `create` / `modify` / `delete` | `yes` / `no` |

## Task Breakdown

| Task ID | Title | Estimated Effort | Documentation Required | Dependencies |
|---|---|---|---|---|
| `{TASK_ID}` | `{TITLE}` | `{EFFORT}` | `yes` / `no` | `{DEPS}` |

## Documentation Strategy

| Field | Value |
|---|---|
| Documentation Approach | `{APPROACH}` |
| New Documents | `{COUNT_AND_TYPES}` |
| Updated Documents | `{COUNT_AND_PATHS}` |
| Retired Documents | `{COUNT_AND_PATHS}` |
| Documentation Owner | `{ROLE_OR_AGENT}` |

### Documentation Freshness Risks

| Risk | Likelihood | Impact | Mitigation | Trigger |
|---|---|---|---|---|
| {RISK} | {LOW/MED/HIGH} | {LOW/MED/HIGH} | {MITIGATION} | {TRIGGER_CONDITION} |

### Baseline vs Profile-Specific Documentation Obligations

| Obligation Type | Obligations |
|---|---|
| Baseline (universal) | {BASELINE_ITEMS} |
| Profile-specific (conditional) | {PROFILE_ITEMS} |

## Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| {RISK} | {LOW/MED/HIGH} | {LOW/MED/HIGH} | {MITIGATION} | `{OWNER}` |

## Deliverables

| Deliverable | Type | Path | Acceptance Criterion |
|---|---|---|---|
| `{DELIVERABLE}` | `code` / `doc` / `config` | `{PATH}` | `{CRITERION}` |

## Acceptance Criteria

| # | Criterion | Verification Method |
|---|---|---|
| 1 | {CRITERION} | {METHOD} |

## Notes

- {NOTE_1}
- {NOTE_2}
