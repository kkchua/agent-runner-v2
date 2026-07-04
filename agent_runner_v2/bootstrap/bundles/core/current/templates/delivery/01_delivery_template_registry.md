---
title: Delivery Template Registry
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
created: 2026-07-04
template_id: DELIVERY-REG-v1
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Template Registry

## Metadata

| Field | Value |
|---|---|
| Template ID | `DELIVERY-REG-v1` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_templates` |
| Scope | Universal baseline — applies to all governed repositories |
| Architecture Profile | Universal (profile-agnostic) |
| Migration Mode | Neutral — registry supports both greenfield and existing-repo deliveries |
| Status | `active` |
| Last Verified | 2026-07-04 |

This registry is the authoritative index of all delivery templates produced by `10_execution_scaffold_v1`. Each template listed here has a stable artifact key, a fixed file path, and a defined role in the delivery lifecycle.

## Registry Overview

The delivery template family covers the complete lifecycle of a governed delivery, from initiative intake through memory capture. Every template is workflow-generated, protected from manual edits, and emitted with YAML frontmatter containing a stable `template_id`.

| Artifact Key | Template ID | File Path | Role |
|---|---|---|---|
| `DELIVERY_TEMPLATE_REGISTRY` | `DELIVERY-REG-v1` | `docs/system/00_governance/bootstrap/templates/delivery/01_delivery_template_registry.md` | This document. Master index of all delivery templates. |
| `DELIVERY_INITIATIVE_TEMPLATE` | `DELIVERY-INIT-v1` | `docs/system/00_governance/bootstrap/templates/delivery/02_delivery_initiative_template.md` | Captures initiative scope, documentation scope, architecture profile context, and acceptance criteria. |
| `DELIVERY_PLAN_TEMPLATE` | `DELIVERY-PLAN-v1` | `docs/system/00_governance/bootstrap/templates/delivery/03_delivery_plan_template.md` | Translates initiative into scoped plan with documentation strategy and freshness-risk assessment. |
| `DELIVERY_TASK_GRAPH_TEMPLATE` | `DELIVERY-TG-v1` | `docs/system/00_governance/bootstrap/templates/delivery/04_delivery_task_graph_template.md` | Dependency graph of tasks with documentation workstream coverage. |
| `DELIVERY_TASK_TEMPLATE` | `DELIVERY-TASK-v1` | `docs/system/00_governance/bootstrap/templates/delivery/05_delivery_task_template.md` | Atomic task with deterministic documentation obligations and validation expectations. |
| `DELIVERY_IMPL_TEMPLATE` | `DELIVERY-IMPL-v1` | `docs/system/00_governance/bootstrap/templates/delivery/06_delivery_impl_template.md` | Per-task implementation plan with documentation update plan and risk assessment. |
| `DELIVERY_REVIEW_TEMPLATE` | `DELIVERY-REV-v1` | `docs/system/00_governance/bootstrap/templates/delivery/07_delivery_review_template.md` | Review scope, findings, code quality assessment, documentation compliance verdict. |
| `DELIVERY_VALIDATION_TEMPLATE` | `DELIVERY-VAL-v1` | `docs/system/00_governance/bootstrap/templates/delivery/08_delivery_validation_template.md` | Validates both code changes and documentation synchronization. |
| `DELIVERY_MEMORY_TEMPLATE` | `DELIVERY-MEM-v1` | `docs/system/00_governance/bootstrap/templates/delivery/09_delivery_memory_template.md` | Captures delivery outcomes, lessons learned, reusable patterns, and documentation notes. |

## Template Families

### Lifecycle Templates
Templates that cover a single delivery from intake to completion:

- `DELIVERY_INITIATIVE_TEMPLATE` — intake and scope capture
- `DELIVERY_PLAN_TEMPLATE` — strategy and task breakdown
- `DELIVERY_TASK_GRAPH_TEMPLATE` — dependency ordering
- `DELIVERY_TASK_TEMPLATE` — atomic work unit
- `DELIVERY_IMPL_TEMPLATE` — implementation detail
- `DELIVERY_REVIEW_TEMPLATE` — quality gate
- `DELIVERY_VALIDATION_TEMPLATE` — correctness + doc-sync gate
- `DELIVERY_MEMORY_TEMPLATE` — retrospective capture

### Governance Templates
Templates that define the governance framework itself:

- `DELIVERY_TEMPLATE_REGISTRY` — this document

### Cross-Cutting Concerns
The following concerns are embedded across multiple templates rather than isolated in one:

| Concern | Templates that address it |
|---|---|
| Architecture profile (current/target/migration mode) | `DELIVERY_INITIATIVE_TEMPLATE`, `DELIVERY_PLAN_TEMPLATE`, `DELIVERY_TASK_TEMPLATE`, `DELIVERY_IMPL_TEMPLATE` |
| Documentation impact | `DELIVERY_TASK_TEMPLATE`, `DELIVERY_IMPL_TEMPLATE`, `DELIVERY_VALIDATION_TEMPLATE` |
| Documentation freshness risk | `DELIVERY_PLAN_TEMPLATE`, `DELIVERY_VALIDATION_TEMPLATE` |
| Sidecar contract compliance | All templates (via frontmatter + banner) |

## Usage Rules

1. **Every instance must carry the template_id.** When a workflow step produces an artifact from a template, the output YAML frontmatter MUST include the `template_id` of the source template.

2. **Section headings are fixed.** The section headings defined in each template are mandatory. Additional sections may be appended but existing headings must not be renamed or removed.

3. **Profile fields are conditional.** Templates that include architecture-profile fields (`current_profile`, `target_profile`, `migration_mode`) MUST populate them when the repository standard is unclear or changing. When the repository standard is well-established, the fields MAY be populated with the known values.

4. **Documentation obligations are deterministic.** Every task and implementation template instance MUST specify what documentation will be created, updated, or retired as a result of the work. "No documentation impact" is a valid answer but must be stated explicitly.

5. **Validation must cover both code and docs.** Every validation instance MUST include sections for code validation AND documentation synchronization validation.

6. **Registry is append-only within a major version.** New template IDs may be added to the registry. Existing template IDs must not be removed or repurposed within the same major version.

7. **Template instances are workflow-generated.** Every artifact produced from a template inherits the workflow-generated protection banner and `managed_by: workflow-generated` frontmatter.

## Cross-References

| Reference | Location |
|---|---|
| Delivery Workflow SOP | `docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md` |
| Delivery Status Rules | `docs/system/00_governance/bootstrap/DELIVERY_STATUS_RULES_v1.md` |
| Existing Repo Workflow SOP | `docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md` |
| Codebase Template Registry | `docs/system/00_governance/bootstrap/templates/codebase/01_codebase_template_registry.md` |
| Codebase Doc SOP | `docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md` |
| Codebase Doc Status Rules | `docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md` |
| Delivery Agents | `docs/delivery/00_standards/DELIVERY_AGENTS_MD.md` |
| Delivery Folder Map | `docs/delivery/DELIVERY_FOLDER_MAP.json` |
| Project Analysis | `docs/system/00_governance/bootstrap/project_analysis.md` |
