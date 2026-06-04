# Template Registry Review

## Metadata
| Field | Value |
| --- | --- |
| Review ID | REV-260602-04_rtempl_R-0000-00 |
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

### 1. The registry orders validation before implementation review
`template_registry.md` defines `Code -> Validation -> Review -> Memory`. The SOP state machine requires `EXECUTION_IN_PROGRESS -> IMPLEMENTATION_REVIEWED -> VALIDATION_IN_PROGRESS`.

Required correction: place implementation review before validation in the registry flow and stage descriptions.

### 2. Artifact status options do not match the governed lifecycles
Several metadata blocks introduce unsupported statuses or omit required statuses:
- `01_initiative.template.md` adds `in_review` and omits `completed`.
- `02_plan.template.md` adds `in_review` and `in_progress`.
- `02b_task_graph.template.md` adds `in_review`, `in_progress`, and `completed`.
- `04_implementation_plan.template.md` adds `in_review`.
- `04_review.template.md` uses decision-like statuses instead of the required `Draft -> Final` lifecycle.
- `06_memory.template.md` omits `draft`.

Required correction: align each metadata status list with the artifact lifecycle defined by the status rules. Keep review lifecycle status separate from its `APPROVED` or `REJECTED` decision.

### 3. Task dependency placeholders still conflict with the task ID contract
`03_task.template.md` lists dependencies as `TASK-{{MM}}` and `TASK-{{KK}}`, while task IDs elsewhere use `TASK-{{YYYYMMDD}}-{{NN}}`.

Required correction: use the complete task ID format for dependency references.

### 4. The review template is missing mandatory review decision fields
The status rules require every review artifact to record target artifact ID, version, and path; decision; findings; evidence; and follow-up with required corrections, owner, and routing destination. `04_review.template.md` lacks explicit target version, target path, evidence, follow-up owner, and routing destination fields. Its decision options also include unsupported `needs_revision`.

Required correction: add the required structured review fields and restrict the final decision to `APPROVED` or `REJECTED`.

### 5. The implementation-plan template omits required evidence and rollback notes
The SOP requires an implementation plan to define scoped changes, tests, evidence, and rollback notes. `04_implementation_plan.template.md` includes scoped edits and tests but has no evidence plan or rollback section.

Required correction: add explicit implementation-evidence and rollback sections.

### 6. Traceability metadata is incomplete across templates
The status rules require every artifact to preserve upstream IDs, source paths, versions, contract references, relevant snapshot hashes, and supersession linkage where applicable. The templates do not consistently provide these fields. For example, plan, task graph, task, and implementation-plan metadata omit artifact version and supersession fields; review metadata omits target version and path; initiative metadata does not capture the enforced budget or snapshot/contract traceability.

Required correction: add the applicable deterministic traceability fields to each artifact template.

### 7. Registry sidecar coverage is incomplete
`template_registry.md` says generated markdown artifacts require sidecars, but the SOP requires sidecars for additional mandatory artifacts and decisions, including snapshot manifests and gate decisions. These are not represented in the registry.

Required correction: document all sidecar-required artifacts and decisions, including non-markdown outputs.

### 8. The documented naming convention does not cover an actual template
`template_registry.md` says all templates follow `{NN}_{name}.template.md`, but `02b_task_graph.template.md` uses an alphanumeric prefix.

Required correction: update the documented convention to include the task-graph naming form or rename the template consistently.

## Coverage Summary
All eight reviewed files were checked. Each artifact template has a metadata block containing `Doc Type` and `Template Version`, and the previously reported task lifecycle, task-graph Doc Type, folder mapping, and malformed memory-comment issues were corrected. The remaining defects prevent SOP-aligned deterministic generation.

## Decision
REJECTED
