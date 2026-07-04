---
title: Codebase Change Template
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
created: 2026-07-04
template_id: CODEBASE-CHG-v1
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Codebase Change Template

> Artifact key: `CODEBASE_CHANGE_TEMPLATE`

## Metadata

| Field | Value |
|---|---|
| Template ID | `CODEBASE-CHG-v1` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_templates` |
| Scope | Universal baseline — applies to all governed repositories |
| Status | `active` |
| Last Verified | 2026-07-04 |

This template defines the canonical structure for change-impact records. Every change-impact artifact must conform to this structure. Change-impact records track three mandatory categories: changed files, updated documentation, and stale documentation removal.

---

## Instance Preamble

```yaml
---
title: Change Impact — {CHANGE_ID}
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: codebase_doc
created: {DATE}
template_id: CODEBASE-CHG-v1
change_id: {CHANGE_ID}
initiative_id: {INITIATIVE_ID}
plan_id: {PLAN_ID}
status: current
---
```

## Metadata

| Field | Value |
|---|---|
| Change ID | `{CHANGE_ID}` |
| Initiative ID | `{INITIATIVE_ID}` |
| Plan ID | `{PLAN_ID}` |
| Created | `{DATE}` |
| Author / Agent | `{ROLE}` |
| Status | `current` / `needs_update` / `pending_review` / `superseded` |
| Architecture Profile Impact | `{PROFILE_IF_CHANGING}` |

## Change Summary

| Field | Value |
|---|---|
| Title | `{TITLE}` |
| Summary | `{SUMMARY}` |
| Change Type | `feature` / `bugfix` / `refactor` / `docs_only` / `config` / `migration` |
| Scope | `{SCOPE_DESCRIPTION}` |

## Changed Files

This section tracks every source file modified, created, or deleted by this change.

| File Path | Change Type | Description | Module |
|---|---|---|---|
| `{FILE_PATH}` | `created` / `modified` / `deleted` | `{DESCRIPTION}` | `{MODULE}` |

### Changed Files Summary

| Category | Count |
|---|---|
| Files Created | `{N}` |
| Files Modified | `{N}` |
| Files Deleted | `{N}` |
| **Total** | `{N}` |

## Documentation Updates

This section tracks every documentation file that was created or updated as a result of this change.

| Doc Path | Action | Description | Status |
|---|---|---|---|
| `{DOC_PATH}` | `created` / `updated` | `{DESCRIPTION}` | `current` / `pending_review` |

### Documentation Update Summary

| Category | Count |
|---|---|
| Docs Created | `{N}` |
| Docs Updated | `{N}` |
| **Total** | `{N}` |

## Stale Documentation Removal

This section tracks documentation that was identified as stale and removed or superseded as a result of this change.

| Stale Doc Path | Reason for Staleness | Action Taken | Superseded By |
|---|---|---|---|
| `{DOC_PATH}` | `{REASON}` | `removed` / `superseded` / `archived` | `{NEW_PATH_OR_NA}` |

### Stale Doc Removal Summary

| Category | Count |
|---|---|
| Docs Removed | `{N}` |
| Docs Superseded | `{N}` |
| Docs Archived | `{N}` |
| **Total** | `{N}` |

## Documentation Freshness Verification

This section records the verification that all touched modules have fresh documentation after this change.

| Module | Doc Path | Verified? | Verification Method | Verified By |
|---|---|---|---|---|
| `{MODULE}` | `{DOC_PATH}` | `yes` / `no` | `{METHOD}` | `{VERIFIER}` |

### Freshness Check Summary

| Check | Result | Notes |
|---|---|---|
| All touched modules have current docs | `pass` / `fail` | {NOTES} |
| No stale docs remain | `pass` / `fail` | {NOTES} |
| Change-impact record complete | `pass` / `fail` | {NOTES} |

## Cross-References

| Reference | Location |
|---|---|
| Source Initiative | `{INITIATIVE_PATH}` |
| Source Plan | `{PLAN_PATH}` |
| Related Module Docs | `{MODULE_DOC_PATHS}` |
| Related Component Docs | `{COMPONENT_DOC_PATHS}` |

## Notes

- This change-impact record MUST include entries in all three mandatory sections: Changed Files, Documentation Updates, and Stale Documentation Removal.
- If no documentation was updated, the Documentation Updates section MUST state "No documentation updates" explicitly.
- If no stale documentation was removed, the Stale Documentation Removal section MUST state "No stale documentation removed" explicitly.
- {NOTE_2}
