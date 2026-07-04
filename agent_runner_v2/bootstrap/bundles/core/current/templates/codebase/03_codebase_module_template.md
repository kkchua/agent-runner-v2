---
title: Codebase Module Template
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
created: 2026-07-04
template_id: CODEBASE-MOD-v1
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Codebase Module Template

> Artifact key: `CODEBASE_MODULE_TEMPLATE`

## Metadata

| Field | Value |
|---|---|
| Template ID | `CODEBASE-MOD-v1` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_templates` |
| Scope | Universal baseline — applies to all governed repositories |
| Status | `active` |
| Last Verified | 2026-07-04 |

This template defines the canonical structure for per-module reference documentation. Every module doc instance must conform to this structure.

---

## Instance Preamble

```yaml
---
title: Module — {MODULE_NAME}
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: codebase_doc
created: {DATE}
template_id: CODEBASE-MOD-v1
module_id: {MODULE_ID}
status: current
last_verified_by_change: {CHANGE_ID}
---
```

## Metadata

| Field | Value |
|---|---|
| Module ID | `{MODULE_ID}` |
| Module Name | `{MODULE_NAME}` |
| File Path | `{MODULE_PATH}` |
| Created | `{DATE}` |
| Last Updated | `{DATE}` |
| Last Verified by Change | `{CHANGE_ID_OR_SHA}` |
| Status | `current` / `needs_update` / `pending_review` / `superseded` |
| Owner Doc Path | `{DOC_PATH}` |
| Documentation Mode | `documented` |

## Module Overview

| Field | Value |
|---|---|
| Purpose | `{PURPOSE}` |
| Responsibility | `{RESPONSIBILITY}` |
| Key Abstractions | `{ABSTRACTIONS}` |
| Architecture Profile | `{PROFILE_IF_APPLICABLE}` |

## File Inventory

| File | Role | Status |
|---|---|---|
| `{FILE_PATH}` | `{ROLE}` | `current` / `needs_update` / `pending_review` |

## Architecture

| Aspect | Description |
|---|---|
| Internal Structure | `{DESCRIPTION}` |
| Design Patterns | `{PATTERNS}` |
| Key Invariants | `{INVARIANTS}` |

## Key Components

| Component | Description | Location |
|---|---|---|
| `{COMPONENT}` | `{DESCRIPTION}` | `{LOCATION}` |

## Public API

| Symbol | Type | Signature | Description |
|---|---|---|---|
| `{SYMBOL}` | `function` / `class` / `constant` | `{SIGNATURE}` | `{DESCRIPTION}` |

## Dependencies

| Dependency | Type | Direction | Notes |
|---|---|---|---|
| `{DEPENDENCY}` | `internal` / `external` | `imports` / `imported_by` | `{NOTES}` |

## Testing

| Aspect | Details |
|---|---|
| Test Location | `{TEST_PATH}` |
| Test Coverage | `{COVERAGE}` |
| Key Test Cases | `{CASES}` |

## Change Log

| Date | Change ID | Description | Author |
|---|---|---|---|
| `{DATE}` | `{CHANGE_ID}` | `{DESCRIPTION}` | `{AUTHOR}` |

## Notes

- {NOTE_1}
- {NOTE_2}
