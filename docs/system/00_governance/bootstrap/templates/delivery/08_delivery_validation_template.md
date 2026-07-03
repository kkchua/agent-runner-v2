---
template_id: DELIVERY-VALIDATION-v1
status: active
generated: "2026-07-03T23:30:00+08:00"
workflow: 10_execution_scaffold_v1
step: generate_templates
managed_by: workflow-generated
version: 1.0.0
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Validation Template

## Metadata

| Field | Value |
|-------|-------|
| **Template ID** | `DELIVERY-VALIDATION-v1` |
| **Validation ID** | `[VALID-XXXX-v1]` |
| **Title** | `[Validation Title]` |
| **Status** | `draft` / `in-progress` / `complete` / `failed` |
| **Task ID** | `[TASK-XXXX-v1]` |
| **Impl ID** | `[IMPL-XXXX-v1]` |
| **Review ID** | `[REVIEW-XXXX-v1]` |
| **Validator** | `[Agent role or human]` |
| **Created** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Updated** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Workflow** | `10_execution_scaffold_v1` |
| **Step** | `task_execution_v1` |
| **Managed By** | workflow-generated |

## Validation Scope

<!-- What is being validated. -->

| Artifact | Type | Path | Version |
|----------|------|------|---------|
| `[Artifact name]` | `[code / doc / config]` | `[Path]` | `[Version/commit]` |

## Code Validation

<!-- Validate the code changes. -->

| Check | Result | Details |
|-------|--------|---------|
| **Syntax / Compilation** | `[Pass / Fail]` | `[Details]` |
| **Linting** | `[Pass / Fail]` | `[Details]` |
| **Unit Tests** | `[Pass / Fail]` | `[Details]` |
| **Integration Tests** | `[Pass / Fail / N/A]` | `[Details]` |
| **Regression Check** | `[Pass / Fail]` | `[Details]` |
| **Edge Case Coverage** | `[Pass / Fail]` | `[Details]` |
| **Security Scan** | `[Pass / Fail / N/A]` | `[Details]` |

### Code Validation Issues

| ID | Issue | Severity | File | Resolution |
|----|-------|----------|------|-----------|
| `[CV-001]` | `[Description]` | `[Critical / High / Medium / Low]` | `[Path]` | `[Resolved / Open]` |

## Documentation Synchronization Validation

<!-- Validate that documentation is synchronized with code changes. -->

### Documentation Completeness

| Document | Expected | Present | Content Valid | Notes |
|----------|----------|---------|--------------|-------|
| **Module docs** | `[Yes / No]` | `[Yes / No]` | `[Yes / No]` | `[Notes]` |
| **Component docs** | `[Yes / No]` | `[Yes / No]` | `[Yes / No]` | `[Notes]` |
| **Inventory** | `[Yes / No]` | `[Yes / No]` | `[Yes / No]` | `[Notes]` |
| **Change record** | `[Yes / No]` | `[Yes / No]` | `[Yes / No]` | `[Notes]` |

### Documentation Accuracy

| Check | Result | Details |
|-------|--------|---------|
| **Template ID consistency** | `[Pass / Fail]` | `[All docs use registry template IDs]` |
| **Status currency** | `[Pass / Fail]` | `[Statuses reflect current state]` |
| **Cross-reference validity** | `[Pass / Fail]` | `[All links resolve]` |
| **Stale content detection** | `[Pass / Fail]` | `[No outdated content remains]` |
| **Metadata completeness** | `[Pass / Fail]` | `[All required metadata fields present]` |

### Documentation Synchronization Issues

| ID | Issue | Severity | Document | Resolution |
|----|-------|----------|---------|-----------|
| `[DV-001]` | `[Description]` | `[Critical / High / Medium / Low]` | `[Path]` | `[Resolved / Open]` |

## Validation Issues

<!-- Consolidated list of all validation issues. -->

| ID | Category | Issue | Severity | Artifact | Status | Resolution |
|----|----------|-------|----------|---------|--------|-----------|
| `[V-001]` | `[code / doc]` | `[Description]` | `[Critical / High / Medium / Low]` | `[Path]` | `[Open / Resolved]` | `[How resolved]` |

## Validation Summary

| Dimension | Result | Issues |
|-----------|--------|--------|
| **Code Validation** | `[Pass / Fail]` | `[N issues]` |
| **Documentation Validation** | `[Pass / Fail]` | `[N issues]` |
| **Overall** | `[Pass / Fail]` | `[N total issues]` |

## Verdict

| Aspect | Verdict |
|--------|---------|
| **Code Quality** | `[Valid / Invalid]` |
| **Documentation Sync** | `[Valid / Invalid]` |
| **Overall Validation** | `[Valid / Invalid]` |

### Conditions for Validity
<!-- Items that must be resolved for the validation to pass. -->

- [ ] `[Condition 1]`
- [ ] `[Condition 2]`

## Approval

| Role | Name / Agent | Status | Date | Notes |
|------|-------------|--------|------|-------|
| **Validator** | `[Agent role]` | `[Approved / Rejected]` | `[Date]` | `[Notes]` |
| **Approver** | `[Agent role / Human]` | `[Approved / Rejected / Pending]` | `[Date]` | `[Notes]` |

## Notes

<!-- Additional context, decisions, or references. -->
