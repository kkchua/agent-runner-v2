# Template Registry Review

## Metadata
| Field | Value |
| --- | --- |
| Review ID | REV-260602-05_rtempl_R-0000-00 |
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

### 1. The registry places the implementation record before code execution
`template_registry.md` defines `Implementation Plan -> Implementation Record -> Code -> Review`. The SOP defines execution as implementing, testing, and recording evidence, with the implementation record accepted before the task becomes `Implemented` and before implementation review.

Required correction: place code execution before the implementation record, then implementation review, then validation.

### 2. The registry understates the validation phase
`template_registry.md` describes validation as a deterministic structural check of delivery artifacts against templates. The SOP requires independent validation of behavior, contracts, deterministic outputs, evidence, tests, traceability, sidecar presence, and approved state transitions.

Required correction: describe validation with the full governed scope.

### 3. Upstream traceability fields remain incomplete
The status rules require every artifact to preserve upstream IDs, source paths, versions, contract references, and relevant snapshot hashes. Several templates retain IDs but omit upstream paths and versions. For example, the plan has an initiative ID but no initiative path or version; the task graph has plan and initiative IDs but no source paths or versions; the task has graph and plan IDs but no upstream versions and only a plan path in its body; the implementation plan has plan and task IDs and a task-spec path but no upstream versions. The memory reference lists capture IDs without paths or versions.

Required correction: add applicable upstream source paths and artifact versions so generated documents preserve deterministic traceability.

### 4. The review template uses inconsistent placeholders for the related document type
`04_review.template.md` uses `{{DOC_TYPE}}` in metadata but `{{RELATED_DOC_TYPE}}` in the naming contract. The placeholders refer to the same value but are not consistent.

Required correction: use one placeholder name for the related document type.

### 5. The task-graph example emits duplicate task IDs under direct substitution
`02b_task_graph.template.md` contains two sample task nodes and both headings use `TASK-{{YYYYMMDD}}-{{NN}}`. Direct substitution produces duplicate IDs in one generated graph.

Required correction: use distinct placeholders for distinct sample nodes or make the repeated-node substitution contract explicit and deterministic.

## Coverage Summary
All eight review targets were checked against the project analysis, SOP, and status rules. Each artifact template contains a metadata block with `Doc Type` and `Template Version`. Prior lifecycle, sidecar-coverage, review-field, rollback, and naming-convention findings were corrected. The remaining workflow-ordering, validation-scope, traceability, and placeholder defects prevent approval.

## Decision
REJECTED
