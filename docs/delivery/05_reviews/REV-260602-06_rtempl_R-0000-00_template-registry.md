# Template Registry Review

## Metadata
| Field | Value |
| --- | --- |
| Review ID | REV-260602-06_rtempl_R-0000-00 |
| Review Type | Template Registry Review |
| Decision | REJECTED |
| Reviewer Role | Template Reviewer |

## Targets
- `docs/delivery/00_templates/template_registry.md`
- `docs/delivery/00_templates/01_initiative.template.md`
- `docs/delivery/00_templates/02_plan.template.md`
- `docs/delivery/00_templates/02b_task_graph.template.md`
- `docs/delivery/00_templates/03_task.template.md`
- `docs/delivery/00_templates/04_implementation_plan.template.md`
- `docs/delivery/00_templates/04_review.template.md`
- `docs/delivery/00_templates/06_memory.template.md`

## Governing References
- `delivery_scaffold_v1/SCAFFOLD-GEN-20260602-003/00_project_analysis/project_analysis.json`
- `docs/delivery/00_templates/delivery_sop.json`
- `docs/delivery/00_templates/delivery_status_rules.json`

## Findings

### 1. Placeholder variables remain inconsistent across templates
The templates do not use a single deterministic placeholder contract:
- `03_task.template.md` uses `{{PATH}}` for the source plan even though the same template defines the source-plan path as `{{PLAN_PATH}}`.
- `02_plan.template.md` uses `{{scope item}}`, and `02b_task_graph.template.md` uses `{{validation gate}}`. These space-containing lowercase placeholders conflict with the uppercase underscore-separated convention used by the rest of the templates.
- `06_memory.template.md` renders upstream artifact versions as `v{{INITIATIVE_VERSION}}`, `v{{PLAN_VERSION}}`, `v{{TASK_VERSION}}`, and `v{{REVIEW_VERSION}}`, while the other templates use version placeholders directly. Since metadata versions are represented as values such as `v1`, direct reuse can produce inconsistent values such as `vv1`.

Required correction: standardize the placeholder names and version-value contract so each runtime variable has one spelling and one representation across templates.

### 2. The registry advertises a validation template that does not exist
`template_registry.md` maps Validation to Doc Type `05_validation` and its usage instructions say to select the appropriate template from the registry for each delivery stage. No `05_validation.template.md` exists in `docs/delivery/00_templates/`, and the registry does not explain an alternate generation source for the mandatory validation artifact. This differs from the Implementation Record stage, which is explicitly described as generated per task.

The SOP requires a validation artifact and matching sidecar before completion.

Required correction: add the missing validation template or explicitly document the deterministic generation mechanism and source used for validation artifacts.

### 3. Artifact lifecycle values do not match the governed lifecycle spelling
The status-rules lifecycle uses `Draft`, `Approved`, `Completed`, `Superseded`, `Final`, `Active`, and `Archived`. The initiative, plan, task-graph, implementation-plan, review, and memory templates emit lowercase alternatives such as `draft`, `approved`, and `final`. The task template already uses the governed title-case spelling.

Required correction: use the governed lifecycle values consistently unless the runner contract explicitly defines case normalization.

## Coverage Summary
All eight review targets were checked against the project analysis, SOP, and status rules. Each artifact template contains a metadata block with `Doc Type` and `Template Version`. The prior workflow-ordering, validation-scope, traceability-field, review-placeholder, and duplicate task-node findings were corrected. The remaining placeholder-contract, validation-registry, and lifecycle-value defects prevent approval.

## Decision
REJECTED
