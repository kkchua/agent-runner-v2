---
Doc Type: 05_validation
Template Version: v1
Validation ID: VAL-{{YYYYMMDD}}-{{NN}}
Initiative ID: {{INITIATIVE_ID}}
Plan ID: {{PLAN_ID}}
Task ID: {{TASK_ID}}
Title: {{TITLE}}
Status: in_progress | validated | failed | superseded
Validator: {{VALIDATOR}}
Validated At: {{ISO_DATETIME}}
Approved At: {{ISO_DATETIME}}
---

# {{TITLE}}

## Validation Objective

<!-- What this validation is verifying and why. Reference the artifacts being validated. -->

## Validation Scope

<!-- Which artifacts, contracts, and behaviors this validation covers -->

| Artifact Type | Artifact ID | Path | Version |
|---|---|---|---|
| Task | {{TASK_ID}} | `{{TASK_PATH}}` | {{TASK_VERSION}} |
| Implementation Plan | {{IMPL_PLAN_ID}} | `{{IMPL_PLAN_PATH}}` | {{IMPL_PLAN_VERSION}} |
| Review | {{REVIEW_ID}} | `{{REVIEW_PATH}}` | {{REVIEW_VERSION}} |
| Implementation Record | {{IMPL_RECORD_ID}} | `{{IMPL_RECORD_PATH}}` | {{IMPL_RECORD_VERSION}} |

## Behavioral Validation

<!-- Deterministic checks: tests pass, contracts satisfied, outputs match expectations -->

| Check | Method | Expected | Actual | Result |
|---|---|---|---|---|
| {{CHECK_NAME}} | {{COMMAND_OR_SCRIPT}} | {{EXPECTED}} | {{ACTUAL}} | pass / fail |

### Test Results Summary

| Suite | Tests | Passed | Failed | Skipped |
|---|---|---|---|---|
| {{SUITE_NAME}} | {{TOTAL}} | {{PASSED}} | {{FAILED}} | {{SKIPPED}} |

## Contract Validation

<!-- Verify all required artifacts and sidecars exist and match expected schemas -->

| Contract Item | Required | Present | Valid | Notes |
|---|---|---|---|---|
| {{ARTIFACT}} | yes/no | yes/no | yes/no | {{COMMENT}} |

### Sidecar Presence Check

| Artifact | Sidecar Path | Present | Valid JSON | Schema Valid |
|---|---|---|---|---|
| {{ARTIFACT_NAME}} | `{{SIDECAR_PATH}}` | yes/no | yes/no | yes/no |

## Traceability Validation

<!-- Verify upward and downward traceability through the artifact chain -->

| Link | Expected | Actual | Valid |
|---|---|---|---|
| Task → Task Graph | {{TASK_GRAPH_ID}} | {{ACTUAL_GRAPH_ID}} | yes/no |
| Task Graph → Plan | {{PLAN_ID}} | {{ACTUAL_PLAN_ID}} | yes/no |
| Plan → Initiative | {{INITIATIVE_ID}} | {{ACTUAL_INITIATIVE_ID}} | yes/no |
| Review → Target Artifact | {{TARGET_ARTIFACT_ID}} | {{ACTUAL_TARGET_ID}} | yes/no |

## Evidence Validation

<!-- Verify completion evidence referenced in task spec exists and is accessible -->

| Evidence Item | Expected Path | Exists | Accessible | Notes |
|---|---|---|---|---|
| {{EVIDENCE_NAME}} | `{{EVIDENCE_PATH}}` | yes/no | yes/no | {{COMMENT}} |

## State Transition Validation

<!-- Verify the task/workflow state transitions are valid per SOP status rules -->

| Transition | From State | To State | Allowed | Notes |
|---|---|---|---|---|
| {{TRANSITION_NAME}} | {{FROM}} | {{TO}} | yes/no | {{COMMENT}} |

## Validation Summary

| Metric | Value |
|---|---|
| Total Checks | {{TOTAL_CHECKS}} |
| Passed | {{PASSED_CHECKS}} |
| Failed | {{FAILED_CHECKS}} |
| Warnings | {{WARNING_COUNT}} |

## Final Decision

| Field | Value |
|---|---|
| **Decision** | VALIDATED / FAILED |
| **Rationale** | {{WHY_THIS_DECISION}} |
| **Blocking Failures** | {{LIST_OF_BLOCKING_FAILURES_OR_NONE}} |
| **Non-Blocking Warnings** | {{LIST_OF_WARNINGS_OR_NONE}} |
| **Routing Destination** | {{NEXT_STEP_OR_REFINE_TARGET}} |

## Folder Map

<!-- Deterministic output manifest: all artifacts produced or modified during this validation -->

```json
{
  "validated_artifacts": [
    {"path": "{{ARTIFACT_PATH}}", "checksum": "{{SHA256}}", "bytes": {{SIZE}}}
  ],
  "sidecars": [
    {"path": "{{SIDECAR_PATH}}", "checksum": "{{SHA256}}", "bytes": {{SIZE}}}
  ],
  "validation_generated_at": "{{VALIDATED_AT}}"
}
```

## References

<!-- Source artifacts, SOP rules, validation scripts, or standards applied -->

-

## Notes

<!-- Additional validator observations, edge cases, or caveats -->
