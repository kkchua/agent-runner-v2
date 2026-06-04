# Template Registry Review

## Metadata
| Field | Value |
| --- | --- |
| Review ID | REV-260602-03_rtempl_R-0000-00 |
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
- `docs/delivery/00_templates/WORKFLOW_SOP_v1.md`
- `docs/delivery/00_templates/DELIVERY_STATUS_RULES_v1.md`

## Findings

### 1. Task identifiers are inconsistent across templates
`02_plan.template.md` and `02b_task_graph.template.md` use `TASK-{{NN}}`, while `03_task.template.md` defines the task ID as `TASK-{{YYYYMMDD}}-{{NN}}`. Graph dependencies and examples also use the shorter form. Generated plans, graphs, and task artifacts cannot preserve deterministic linkage with these conflicting formats.

Required correction: define one task ID format and use it consistently in plan breakdowns, task-graph nodes and dependencies, task metadata, and references.

### 2. The task template does not align with the governed task lifecycle
`03_task.template.md` exposes `pending / in_progress / in_review / approved / rejected / superseded`. The SOP and status rules require `Pending`, `In Progress`, `Implemented`, and `Approved`, and also allow `Blocked`, `Cancelled`, and `Superseded` transitions. The template omits `Implemented`, `Blocked`, and `Cancelled` and introduces statuses that are not part of the governed lifecycle.

Required correction: align task status values exactly with the runner-enforced lifecycle.

### 3. Required upstream traceability is incomplete
The status rules require tasks to link task graphs and plans, but `03_task.template.md` has no Task Graph ID. The implementation-plan artifact links the task but has no distinct Implementation Plan ID. The memory template does not provide explicit snapshot references or supersession links required by the SOP's memory-management rules.

Required correction: add stable artifact identity and required upstream linkage fields for each affected artifact.

### 4. The registry is inconsistent with the SOP folder structure
`template_registry.md` maps task graphs to `02_plans/artifacts` and implementation plans to `04_implementation_plans`. The SOP defines `docs/delivery/02_plans/` for plans and task graphs and `docs/delivery/04_implementation/` for implementation plans and implementation records.

Required correction: use the governing SOP folder map.

### 5. The registry does not represent mandatory workflow artifacts and phases
The registry flow is `Initiative -> Plan -> Task Graph -> Task -> Implementation Plan -> Code -> Review -> Memory`. The SOP requires an implementation record for each task, independent validation artifacts before completion, and matching sidecars. The registry omits implementation records, validation, and sidecar expectations, so it does not describe the enforced workflow.

Required correction: include the required workflow artifacts and phases, or explicitly document which templates generate each mandatory artifact.

### 6. The task-graph Doc Type conflicts with the registry mapping
`template_registry.md` declares the task-graph Doc Type as `02b_task_graph`, but `02b_task_graph.template.md` declares `02_plan_artifact`.

Required correction: use one Doc Type consistently.

### 7. The memory template contains malformed comment placeholders
`06_memory.template.md` starts HTML comments under `Core Patterns`, `Known Constraints`, and `Integration Points` without closing them. Renderers will hide the remainder of the document after the first malformed placeholder, including later required sections.

Required correction: close each placeholder comment.

## Coverage Summary
All seven artifact templates contain a metadata table with `Doc Type` and `Template Version`. The registry lists the seven generated templates. However, the identifier, lifecycle, traceability, folder-map, workflow-phase, Doc Type, and Markdown-structure defects above prevent deterministic generation and SOP alignment.

## Decision
REJECTED
