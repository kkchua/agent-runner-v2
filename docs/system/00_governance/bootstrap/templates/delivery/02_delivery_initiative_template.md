---
title: Delivery Initiative Template
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
created: 2026-07-04
template_id: DELIVERY-INIT-v1
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Initiative Template

> Artifact key: `DELIVERY_INITIATIVE_TEMPLATE`

## Metadata

| Field | Value |
|---|---|
| Template ID | `DELIVERY-INIT-v1` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_templates` |
| Scope | Universal baseline — applies to all governed repositories |
| Architecture Profile | Conditional — populated from repository context |
| Migration Mode | Conditional — populated when repo standard is unclear or changing |
| Status | `active` |
| Last Verified | 2026-07-04 |

This template defines the canonical structure for a delivery initiative. Every initiative intake artifact must conform to this structure.

---

## Instance Preamble

> The following is the template body. When instantiated, replace placeholder values with actual content.

```yaml
---
title: Initiative — {INITIATIVE_ID}
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: initiative_intake_v1
created: {DATE}
template_id: DELIVERY-INIT-v1
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
| Initiative ID | `{INITIATIVE_ID}` |
| Created | `{DATE}` |
| Author / Agent | `{AGENT_ROLE}` |
| Status | `draft` / `approved` / `rejected` |
| Current Architecture Profile | `{CURRENT_PROFILE}` |
| Target Architecture Profile | `{TARGET_PROFILE}` |
| Migration Mode | `{MIGRATION_MODE}` |

**Profile and migration fields are conditional:**
- Populate `current_profile`, `target_profile`, and `migration_mode` when the repository standard is unclear or changing.
- When the repository standard is well-established and not changing, these fields MAY be populated with known values or set to `n/a`.
- When a profile change is underway, `migration_mode` MUST be one of: `active`, `greenfield`, `brownfield`, `n/a`.

## Initiative Description

| Field | Value |
|---|---|
| Initiative Title | `{TITLE}` |
| Summary | `{ONE_PARAGRAPH_SUMMARY}` |
| Motivation | `{WHY_THIS_INITIATIVE}` |
| Expected Outcome | `{DESIRED_STATE_AFTER_DELIVERY}` |

## Scope

### In Scope

- {ITEM_1}
- {ITEM_2}
- {ITEM_N}

### Out of Scope

- {ITEM_1}
- {ITEM_2}

### Affected Modules

| Module Path | Reason for Inclusion |
|---|---|
| `{MODULE_PATH}` | `{REASON}` |

### Likely Codebase Areas

| Area / Directory | Relevance |
|---|---|
| `{AREA}` | `{RELEVANCE}` |

## Documentation Scope

This section captures the documentation impact of the initiative at intake time.

| Field | Value |
|---|---|
| Documentation Required | `yes` / `no` / `partial` |
| New Documents Expected | `{COUNT_OR_NONE}` |
| Existing Documents to Update | `{COUNT_OR_NONE}` |
| Documents to Retire | `{COUNT_OR_NONE}` |
| Stale-Guidance Risk | `low` / `medium` / `high` |

### Stale-Guidance Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| {RISK_DESCRIPTION} | {LOW/MED/HIGH} | {LOW/MED/HIGH} | {MITIGATION} |

### Documentation Areas at Risk

- {AREA_1}
- {AREA_2}

## Acceptance Criteria

| # | Criterion | Verification Method |
|---|---|---|
| 1 | {CRITERION} | {METHOD} |
| 2 | {CRITERION} | {METHOD} |

## Dependencies

| Dependency | Type | Status | Notes |
|---|---|---|---|
| {DEPENDENCY} | `blocking` / `advisory` | {STATUS} | {NOTES} |

## Notes

- {NOTE_1}
- {NOTE_2}
