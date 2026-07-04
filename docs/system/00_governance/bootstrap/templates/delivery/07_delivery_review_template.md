---
title: Delivery Review Template
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
created: 2026-07-04
template_id: DELIVERY-REV-v1
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Review Template

> Artifact key: `DELIVERY_REVIEW_TEMPLATE`

## Metadata

| Field | Value |
|---|---|
| Template ID | `DELIVERY-REV-v1` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_templates` |
| Scope | Universal baseline — applies to all governed repositories |
| Status | `active` |
| Last Verified | 2026-07-04 |

This template defines the canonical structure for a delivery review. Every review artifact must conform to this structure.

---

## Instance Preamble

```yaml
---
title: Review — {REVIEW_ID}
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: review
created: {DATE}
template_id: DELIVERY-REV-v1
review_id: {REVIEW_ID}
task_id: {TASK_ID}
impl_id: {IMPL_ID}
initiative_id: {INITIATIVE_ID}
status: draft
verdict: pending
---
```

## Metadata

| Field | Value |
|---|---|
| Review ID | `{REVIEW_ID}` |
| Task ID | `{TASK_ID}` |
| Implementation Plan ID | `{IMPL_ID}` |
| Initiative ID | `{INITIATIVE_ID}` |
| Created | `{DATE}` |
| Reviewer / Agent | Reviewer |
| Status | `draft` / `in_progress` / `completed` |
| Verdict | `approved` / `rejected` / `pending` |

## Review Scope

| Field | Value |
|---|---|
| Review Type | `code` / `doc` / `combined` |
| Scope Description | `{DESCRIPTION}` |
| Files Reviewed | `{COUNT}` |
| Documentation Files Reviewed | `{COUNT}` |

## Summary

| Field | Value |
|---|---|
| Overall Assessment | `{ASSESSMENT}` |
| Critical Issues | `{COUNT}` |
| Major Issues | `{COUNT}` |
| Minor Issues | `{COUNT}` |
| Recommendations | `{COUNT}` |

## Findings

| Finding ID | Severity | Category | Title | Description | File | Line | Resolution |
|---|---|---|---|---|---|---|---|
| `{FINDING_ID}` | `critical` / `major` / `minor` / `recommendation` | `correctness` / `security` / `performance` / `documentation` / `style` | `{TITLE}` | `{DESCRIPTION}` | `{FILE}` | `{LINE}` | `{RESOLUTION}` |

## Code Quality Assessment

| Dimension | Rating | Notes |
|---|---|---|
| Correctness | `pass` / `fail` / `partial` | {NOTES} |
| Security | `pass` / `fail` / `partial` | {NOTES} |
| Performance | `pass` / `fail` / `partial` | {NOTES} |
| Maintainability | `pass` / `fail` / `partial` | {NOTES} |
| Test Coverage | `pass` / `fail` / `partial` | {NOTES} |
| Error Handling | `pass` / `fail` / `partial` | {NOTES} |

## Documentation Compliance

| Check | Status | Notes |
|---|---|---|
| Touched modules have fresh docs | `pass` / `fail` / `n/a` | {NOTES} |
| Change-impact record created | `pass` / `fail` | {NOTES} |
| Documentation update plan executed | `pass` / `fail` / `n/a` | {NOTES} |
| Protected-doc banners present | `pass` / `fail` / `n/a` | {NOTES} |
| Sidecar contract satisfied | `pass` / `fail` | {NOTES} |
| Stale docs removed | `pass` / `fail` / `n/a` | {NOTES} |
| Profile-specific doc obligations met | `pass` / `fail` / `n/a` | {NOTES} |

## Verdict

| Field | Value |
|---|---|
| Verdict | `approved` / `rejected` |
| Rationale | `{RATIONALE}` |
| Conditions for Approval | `{CONDITIONS}` |
| Rejection Reasons (if rejected) | `{REASONS}` |

## Resolution Tracker

| Finding ID | Resolution Status | Resolved By | Verified | Notes |
|---|---|---|---|---|
| `{FINDING_ID}` | `resolved` / `deferred` / `wont_fix` | `{RESOLVER}` | `yes` / `no` | {NOTES} |

## Notes

- {NOTE_1}
- {NOTE_2}
