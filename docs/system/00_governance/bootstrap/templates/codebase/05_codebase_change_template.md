---
template_id: CODEBASE-CHANGE-v1
status: active
generated: "2026-07-03T23:30:00+08:00"
workflow: 10_execution_scaffold_v1
step: generate_templates
managed_by: workflow-generated
version: 1.0.0
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Codebase Change Template

## Metadata

| Field | Value |
|-------|-------|
| **Template ID** | `CODEBASE-CHANGE-v1` |
| **Change ID** | `[CHANGE-XXXX-v1]` |
| **Title** | `[Change Title]` |
| **Status** | `draft` / `in-progress` / `complete` / `rolled-back` |
| **Task ID** | `[TASK-XXXX-v1]` |
| **Impl ID** | `[IMPL-XXXX-v1]` |
| **Author** | `[Agent role or human]` |
| **Created** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Updated** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Workflow** | `10_execution_scaffold_v1` |
| **Step** | `task_execution_v1` |
| **Managed By** | workflow-generated |

## Change Summary

<!-- Summary of what changed and why. -->

**Description**: [What changed]

**Rationale**: [Why the change was made]

**Impact Level**: `[Low / Medium / High]`

### Architecture Profile Impact

| Dimension | Value |
|-----------|-------|
| **Profile Changed** | `[Yes / No]` |
| **Previous Profile** | `[Previous architecture standard, or "none"]` |
| **New Profile** | `[New architecture standard, or unchanged]` |
| **Migration Mode** | `[greenfield / incremental / refactoring / legacy-merge / none]` |
| **DDD/EDA Impact** | `[Applicable / Not applicable — DDD/EDA are conditional standards, not universal defaults]` |

## Changed Files

<!-- All files that were changed, created, or deleted. -->

| File | Action | Type | Lines Changed | Description |
|------|--------|------|--------------|-------------|
| `[path]` | `[created / modified / deleted]` | `[source / test / config / doc]` | `[+N / -N]` | `[Brief description]` |

### Summary Statistics

| Metric | Count |
|--------|-------|
| **Files Created** | `[N]` |
| **Files Modified** | `[N]` |
| **Files Deleted** | `[N]` |
| **Total Lines Added** | `[N]` |
| **Total Lines Removed** | `[N]` |

## Documentation Updates

<!-- All documentation files that were updated as part of this change. -->

| Document | Action | Description | Validated |
|----------|--------|-------------|-----------|
| `[path]` | `[created / updated]` | `[What was updated]` | `[Yes / No]` |

### Documentation Update Matrix

| Doc Type | Path | Updated | Validated |
|----------|------|---------|-----------|
| **Module doc** | `[docs/codebase/02_modules/*.md]` | `[Yes / No / N/A]` | `[Yes / No]` |
| **Component doc** | `[docs/codebase/03_components/*.md]` | `[Yes / No / N/A]` | `[Yes / No]` |
| **Inventory** | `[docs/codebase/01_inventory/codebase_inventory.md]` | `[Yes / No]` | `[Yes / No]` |
| **This change record** | `[docs/codebase/04_changes/CHANGE-XXXX.md]` | `[Yes]` | `[Yes]` |

## Stale Documentation Removal

<!-- Documentation that was identified as stale and removed or flagged. -->

| Document | Reason for Removal | Action Taken | Validated |
|----------|-------------------|-------------|-----------|
| `[path]` | `[Reason content is outdated]` | `[removed / flagged / updated]` | `[Yes / No]` |

### Stale Documentation Detection

| Detection Method | Result |
|-----------------|--------|
| **Cross-reference validation** | `[All links valid / Broken links found]` |
| **Content-to-code comparison** | `[Content accurate / Discrepancies found]` |
| **Status currency check** | `[All current / Some stale]` |

## Documentation Freshness Verification

<!-- Verify that all documentation is fresh and synchronized. -->

| Verification Check | Result | Details |
|-------------------|--------|---------|
| **Template ID consistency** | `[Pass / Fail]` | `[All docs use registry template IDs]` |
| **Status currency** | `[Pass / Fail]` | `[All statuses reflect current state]` |
| **Cross-reference validity** | `[Pass / Fail]` | `[All links resolve]` |
| **No stale content** | `[Pass / Fail]` | `[No outdated content remains]` |
| **Inventory synchronization** | `[Pass / Fail]` | `[Inventory reflects all changed files]` |

## Cross-References

<!-- Related documents and records. -->

| Reference Type | ID | Path |
|---------------|----|------|
| **Task** | `[TASK-XXXX-v1]` | `[path]` |
| **Implementation** | `[IMPL-XXXX-v1]` | `[path]` |
| **Review** | `[REVIEW-XXXX-v1]` | `[path]` |
| **Validation** | `[VALID-XXXX-v1]` | `[path]` |

## Notes

<!-- Additional context, decisions, or references. -->
