---
title: Codebase Component Template
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
created: 2026-07-04
template_id: CODEBASE-COMP-v1
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Codebase Component Template

> Artifact key: `CODEBASE_COMPONENT_TEMPLATE`

## Metadata

| Field | Value |
|---|---|
| Template ID | `CODEBASE-COMP-v1` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_templates` |
| Scope | Universal baseline — applies to all governed repositories |
| Status | `active` |
| Last Verified | 2026-07-04 |

This template defines the canonical structure for component grouping documentation. Every component doc instance must conform to this structure.

---

## Instance Preamble

```yaml
---
title: Component — {COMPONENT_NAME}
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: codebase_doc
created: {DATE}
template_id: CODEBASE-COMP-v1
component_id: {COMPONENT_ID}
status: current
last_verified_by_change: {CHANGE_ID}
---
```

## Metadata

| Field | Value |
|---|---|
| Component ID | `{COMPONENT_ID}` |
| Component Name | `{COMPONENT_NAME}` |
| Created | `{DATE}` |
| Last Updated | `{DATE}` |
| Last Verified by Change | `{CHANGE_ID_OR_SHA}` |
| Status | `current` / `needs_update` / `pending_review` / `superseded` |
| Owner Doc Path | `{DOC_PATH}` |
| Documentation Mode | `documented` |

## Component Overview

| Field | Value |
|---|---|
| Purpose | `{PURPOSE}` |
| Responsibility | `{RESPONSIBILITY}` |
| Architectural Role | `{ROLE}` |
| Architecture Profile | `{PROFILE_IF_APPLICABLE}` |

## File Coverage

| Module / File | Role in Component | Status |
|---|---|---|
| `{PATH}` | `{ROLE}` | `current` / `needs_update` / `pending_review` |

## Interface

| Interface Element | Type | Description | Consumers |
|---|---|---|---|
| `{ELEMENT}` | `function` / `class` / `event` / `api` | `{DESCRIPTION}` | `{CONSUMERS}` |

## Implementation Details

| Aspect | Description |
|---|---|
| Internal Architecture | `{DESCRIPTION}` |
| Key Design Decisions | `{DECISIONS}` |
| State Management | `{DESCRIPTION}` |
| Error Handling | `{DESCRIPTION}` |

## Dependencies

| Dependency | Type | Direction | Notes |
|---|---|---|---|
| `{DEPENDENCY}` | `internal` / `external` | `requires` / `provides_to` | `{NOTES}` |

## Testing

| Aspect | Details |
|---|---|
| Test Location | `{TEST_PATH}` |
| Integration Tests | `{DESCRIPTION}` |
| Contract Tests | `{DESCRIPTION}` |

## Change Log

| Date | Change ID | Description | Author |
|---|---|---|---|
| `{DATE}` | `{CHANGE_ID}` | `{DESCRIPTION}` | `{AUTHOR}` |

## Notes

- {NOTE_1}
- {NOTE_2}
