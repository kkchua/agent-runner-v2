# Template Review Findings

Reviewed templates against `delivery_scaffold_v1/SCAFFOLD-GEN-20260604-001/00_project_analysis/project_analysis.json`, `docs/delivery/00_templates/delivery_sop.json`, and `docs/delivery/00_templates/delivery_status_rules.json`.

## Decision

REJECTED

## Findings

1. `docs/delivery/00_templates/template_registry.md` is inconsistent with the actual template set and the SOP workflow phases. `docs/delivery/00_templates/05_validation.template.md` exists on disk, and both the SOP and status rules include Validation as a required workflow phase/artifact, but the registry omits it from the mapping, flow, stage descriptions, and versioned template inventory.
2. `docs/delivery/00_templates/03_task.template.md` uses task statuses `pending | in_progress | in_review | approved | rejected | completed`, which do not match the governed lifecycle in `delivery_status_rules.json` (`Pending`, `In Progress`, `Implemented`, `Approved`, `Blocked`, `Failed`, `Cancelled`, `Superseded`) or the SOP state machine. This drops required states and introduces unsupported ones.
3. `docs/delivery/00_templates/04_review.template.md` uses `Status: in_progress | approved | rejected`, but the status rules define the Review lifecycle as `Draft -> Final`, with the approval decision stored separately as `APPROVED` or `REJECTED`. The template currently conflates lifecycle state with decision state.
4. `docs/delivery/00_templates/06_memory.template.md` uses `Status: active | superseded | archived`, but the status rules explicitly state the Memory lifecycle is `Draft -> Final` and note that operational labels like `active` or `archived` are not artifact lifecycle states.
5. `docs/delivery/00_templates/04_implementation_plan.template.md` is missing an Implementation Plan identifier metadata field and instead starts with `Plan ID`. The governing naming convention in the SOP/status rules is `IMPL-YYYYMMDD-NN`, so the template metadata does not fully identify the artifact it is supposed to represent.
6. Placeholder conventions are not fully consistent across templates. Example: review metadata uses `Related Doc Type: {{01_initiative / 02_plan / 02b_task_graph / 03_task / 04_implementation_plan}}`, which embeds literal options inside a placeholder instead of using the normal `{{PLACEHOLDER_NAME}}` form used elsewhere.

## Scope Notes

- The targeted templates all include `Doc Type` and `Template Version` metadata fields.
- Required body sections are broadly present, but the lifecycle/state misalignment above is blocking because these templates are meant to drive runner-enforced workflow transitions.
