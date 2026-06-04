# Template Registry Review

## Metadata
| Field | Value |
| --- | --- |
| Review ID | REV-260602-08_rtempl_R-0000-00 |
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

### 1. The implementation-plan task-path placeholder is inconsistent with the shared traceability contract
`04_implementation_plan.template.md` identifies its upstream task with `{{TASK_ID}}` and `{{TASK_VERSION}}`, but its task path is only represented as `{{TASK_SPEC_PATH}}` in the Inputs table. Other templates use `{{TASK_PATH}}` for the same upstream task-artifact path, including `06_memory.template.md` and the registered `05_validation.template.md`.

The status rules require each artifact to preserve upstream IDs, source paths, and versions. Using two runtime placeholder names for the same task path makes deterministic substitution dependent on template-specific aliases and leaves the implementation-plan metadata block without an explicit upstream task path.

Required correction: add the upstream Task Path field to implementation-plan metadata and use the shared `{{TASK_PATH}}` placeholder consistently.

### 2. The registered validation template does not match the governed validation lifecycle
`template_registry.md` maps validation to `05_validation`, and `05_validation.template.md` exists as the actual registered template. Its metadata status field allows `Draft / Approved / Failed / Superseded`.

The status rules define the Validation artifact lifecycle as `Draft -> Final`, with a separate final decision of `APPROVED` or `REJECTED`. The template's `Final Decision` section instead uses `Approved / Failed`. This conflates lifecycle status with decision and emits `Failed`, which is not the governed rejection decision.

Required correction: use `Draft / Final` for validation artifact status and `Approved / Rejected` for the final decision, consistent with the governed validation contract.

## Coverage Summary
The requested registry and seven listed artifact templates were reviewed against the project analysis, SOP, and status rules. The registry's referenced validation template was also checked for actual-template consistency. Every artifact template has a metadata block with `Doc Type` and `Template Version`, and the registry now includes the previously missing Implementation Record and Memory sidecar rows. The remaining placeholder and validation-lifecycle defects prevent approval.

## Decision
REJECTED
