---
title: Delivery Validation Template
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
created: 2026-07-04
template_id: DELIVERY-VAL-v1
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Validation Template

> Artifact key: `DELIVERY_VALIDATION_TEMPLATE`

## Metadata

| Field | Value |
|---|---|
| Template ID | `DELIVERY-VAL-v1` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_templates` |
| Scope | Universal baseline — applies to all governed repositories |
| Status | `active` |
| Last Verified | 2026-07-04 |

This template defines the canonical structure for delivery validation. Every validation artifact must conform to this structure. Validation MUST cover both code changes AND documentation synchronization.

---

## Instance Preamble

```yaml
---
title: Validation — {VALIDATION_ID}
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: validation
created: {DATE}
template_id: DELIVERY-VAL-v1
validation_id: {VALIDATION_ID}
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
| Validation ID | `{VALIDATION_ID}` |
| Task ID | `{TASK_ID}` |
| Implementation Plan ID | `{IMPL_ID}` |
| Initiative ID | `{INITIATIVE_ID}` |
| Created | `{DATE}` |
| Validator / Agent | `{ROLE}` |
| Status | `draft` / `in_progress` / `completed` |
| Verdict | `approved` / `rejected` / `pending` |

## Validation Scope

| Field | Value |
|---|---|
| Scope Description | `{DESCRIPTION}` |
| Validation Type | `combined` (code + documentation synchronization) |
| Code Files Validated | `{COUNT}` |
| Documentation Files Validated | `{COUNT}` |

## Code Validation

### Functional Validation

| Test ID | Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| `CV-001` | {DESCRIPTION} | {EXPECTED} | {ACTUAL} | `pass` / `fail` / `skip` |

### Code Quality Validation

| Check | Method | Result | Notes |
|---|---|---|---|
| Linting | `{TOOL}` | `pass` / `fail` | {NOTES} |
| Type Checking | `{TOOL}` | `pass` / `fail` / `n/a` | {NOTES} |
| Unit Tests | `pytest` / `{TOOL}` | `pass` / `fail` | {NOTES} |
| Integration Tests | `{TOOL}` | `pass` / `fail` / `n/a` | {NOTES} |
| Coverage | `{TOOL}` | `{PERCENTAGE}` | {NOTES} |
| Sidecar Schema | `validate_delivery_docs` | `pass` / `fail` | {NOTES} |

### Regression Validation

| Check | Method | Result | Notes |
|---|---|---|---|
| Existing tests still pass | `pytest` | `pass` / `fail` | {NOTES} |
| No unintended behavior changes | `{METHOD}` | `pass` / `fail` | {NOTES} |

## Documentation Synchronization Validation

### Module Doc Freshness

| Module | Doc Path | Last Code Change | Doc Last Updated | Fresh? | Action |
|---|---|---|---|---|---|
| `{MODULE}` | `{DOC_PATH}` | `{DATE_OR_SHA}` | `{DATE_OR_SHA}` | `yes` / `no` | `{ACTION}` |

### Change-Impact Record Validation

| Check | Result | Notes |
|---|---|---|
| Change-impact record exists for this delivery | `pass` / `fail` | {NOTES} |
| Change-impact record references correct files | `pass` / `fail` | {NOTES} |
| Change-impact record lists documentation updates | `pass` / `fail` / `n/a` | {NOTES} |

### Stale Documentation Detection

| Document | Staleness Indicator | Severity | Action Required |
|---|---|---|---|
| `{DOC_PATH}` | `{INDICATOR}` | `high` / `medium` / `low` | `{ACTION}` |

### Protected-Doc Compliance

| Check | Result | Notes |
|---|---|---|
| All generated docs carry workflow banner | `pass` / `fail` | {NOTES} |
| All generated docs carry `managed_by` frontmatter | `pass` / `fail` | {NOTES} |
| No manual edits to protected docs | `pass` / `fail` | {NOTES} |

### Documentation Freshness Risk Assessment

| Risk | Status | Mitigation Applied | Notes |
|---|---|---|---|
| Module doc drift | `mitigated` / `unmitigated` | {MITIGATION} | {NOTES} |
| Stale guidance | `mitigated` / `unmitigated` | {MITIGATION} | {NOTES} |
| Bundle map divergence | `mitigated` / `unmitigated` / `n/a` | {MITIGATION} | {NOTES} |

## Validation Issues

| Issue ID | Category | Severity | Description | File | Resolution | Status |
|---|---|---|---|---|---|---|
| `{ISSUE_ID}` | `code` / `doc` / `sidecar` | `critical` / `major` / `minor` | `{DESCRIPTION}` | `{FILE}` | `{RESOLUTION}` | `open` / `resolved` / `deferred` |

## Validation Summary

| Category | Total Checks | Passed | Failed | Skipped |
|---|---|---|---|---|
| Code Validation | `{N}` | `{N}` | `{N}` | `{N}` |
| Documentation Synchronization | `{N}` | `{N}` | `{N}` | `{N}` |
| **Overall** | `{N}` | `{N}` | `{N}` | `{N}` |

## Verdict

| Field | Value |
|---|---|
| Verdict | `approved` / `rejected` |
| Code Validation Verdict | `pass` / `fail` |
| Documentation Sync Verdict | `pass` / `fail` |
| Rationale | `{RATIONALE}` |
| Blocking Issues | `{ISSUES}` |
| Conditions (if conditional approval) | `{CONDITIONS}` |

## Approval

| Field | Value |
|---|---|
| Approved By | `{ROLE_OR_AGENT}` |
| Approved At | `{TIMESTAMP}` |
| Approval Basis | `{BASIS}` |

## Notes

- Validation MUST cover both code validation AND documentation synchronization validation.
- A validation that passes code checks but fails documentation synchronization is a `rejected` verdict.
- Documentation freshness risks identified in the plan MUST be explicitly checked here.
- {NOTE_2}
