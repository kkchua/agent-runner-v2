---
template_id: DELIVERY-REGISTRY-v1
status: active
generated: "2026-07-03T23:30:00+08:00"
workflow: 10_execution_scaffold_v1
step: generate_templates
managed_by: workflow-generated
version: 1.0.0
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Template Registry

## Metadata

| Field | Value |
|-------|-------|
| **Template ID** | `DELIVERY-REGISTRY-v1` |
| **Status** | Active |
| **Generated** | 2026-07-03 |
| **Workflow** | `10_execution_scaffold_v1` |
| **Step** | `generate_templates` |
| **Version** | 1.0.0 |
| **Managed By** | workflow-generated |

## Registry Overview

This registry is the authoritative index of all delivery-process templates used by the `10_execution_scaffold_v1` workflow and any downstream workflows that consume delivery scaffolding. Every delivery document produced by the workflow must use one of the templates listed here.

The registry supports:
- **Universal ecosystem baseline**: All delivery templates work for any repository regardless of architecture.
- **Repo-selected architecture profiles**: Templates include fields for `current_profile`, `target_profile`, and `migration_mode` when the repository standard is unclear or changing.
- **Migration modes**: Greenfield, incremental, refactoring, and legacy-merge modes are all supported.
- **DDD/EDA as conditional standards**: Domain-Driven Design and Event-Driven Architecture are treated as optional profiles, not universal defaults.

## Template Families

### Delivery Templates

| Template ID | File | Purpose | Status |
|-------------|------|---------|--------|
| `DELIVERY-INITIATIVE-v1` | `02_delivery_initiative_template.md` | Initiative intake and scope capture | Active |
| `DELIVERY-PLAN-v1` | `03_delivery_plan_template.md` | Delivery plan with task breakdown | Active |
| `DELIVERY-TASK-GRAPH-v1` | `04_delivery_task_graph_template.md` | Task decomposition and dependencies | Active |
| `DELIVERY-TASK-v1` | `05_delivery_task_template.md` | Individual task execution | Active |
| `DELIVERY-IMPL-v1` | `06_delivery_impl_template.md` | Implementation plan and tracking | Active |
| `DELIVERY-REVIEW-v1` | `07_delivery_review_template.md` | Code and documentation review | Active |
| `DELIVERY-VALIDATION-v1` | `08_delivery_validation_template.md` | Code + documentation synchronization validation | Active |
| `DELIVERY-MEMORY-v1` | `09_delivery_memory_template.md` | Session memory and lessons learned | Active |

### Codebase Templates

| Template ID | File | Purpose | Status |
|-------------|------|---------|--------|
| `CODEBASE-REGISTRY-v1` | `../codebase/01_codebase_template_registry.md` | Codebase template registry | Active |
| `CODEBASE-INV-v1` | `../codebase/02_codebase_inventory_template.md` | Codebase inventory entry | Active |
| `CODEBASE-MOD-v1` | `../codebase/03_codebase_module_template.md` | Module documentation | Active |
| `CODEBASE-COMP-v1` | `../codebase/04_codebase_component_template.md` | Component documentation | Active |
| `CODEBASE-CHANGE-v1` | `../codebase/05_codebase_change_template.md` | Change-impact tracking | Active |

## Usage Rules

1. **Template Selection**: Every delivery document must use exactly one template from this registry. The `template_id` in YAML frontmatter must match the registry entry.

2. **Profile Fields**: When a repository's architecture standard is unclear, changing, or explicitly declares a profile:
   - Set `current_profile` to the existing architecture (e.g., `modular-monolith`, `ddd/eda`, `layered`).
   - Set `target_profile` to the intended architecture.
   - Set `migration_mode` to one of: `greenfield`, `incremental`, `refactoring`, `legacy-merge`.

3. **DDD/EDA Conditionality**: Domain-Driven Design and Event-Driven Architecture patterns are **conditional standards**. They appear in templates as optional profile selections, not as required defaults.

4. **Documentation Scope**: All delivery templates that produce code changes must include documentation-impact sections. Documentation updates are co-equal to code changes in the delivery lifecycle.

5. **Cross-Reference Integrity**: Templates that reference other templates must use the canonical `template_id` values listed in this registry.

6. **Versioning**: Template versions follow semver. Breaking changes increment the major version; additions increment the minor version.

## Cross-References

- **Codebase Template Registry**: See `../codebase/01_codebase_template_registry.md`
- **Workflow SOP**: See `../../WORKFLOW_SOP_v1.md`
- **Delivery Status Rules**: See `../../DELIVERY_STATUS_RULES_v1.md`
- **Project Analysis**: See `../../../../delivery/project_analysis.md`

## Artifact Keys

The following literal artifact keys are the canonical identifiers for delivery templates. These keys must be used in workflow configurations, runner scripts, and any cross-references that resolve delivery templates programmatically.

| Artifact Key | Template ID | File |
|-------------|-------------|------|
| `DELIVERY_INITIATIVE_TEMPLATE` | `DELIVERY-INITIATIVE-v1` | `02_delivery_initiative_template.md` |
| `DELIVERY_PLAN_TEMPLATE` | `DELIVERY-PLAN-v1` | `03_delivery_plan_template.md` |
| `DELIVERY_TASK_GRAPH_TEMPLATE` | `DELIVERY-TASK-GRAPH-v1` | `04_delivery_task_graph_template.md` |
| `DELIVERY_TASK_TEMPLATE` | `DELIVERY-TASK-v1` | `05_delivery_task_template.md` |
| `DELIVERY_IMPL_TEMPLATE` | `DELIVERY-IMPL-v1` | `06_delivery_impl_template.md` |
| `DELIVERY_REVIEW_TEMPLATE` | `DELIVERY-REVIEW-v1` | `07_delivery_review_template.md` |
| `DELIVERY_VALIDATION_TEMPLATE` | `DELIVERY-VALIDATION-v1` | `08_delivery_validation_template.md` |
| `DELIVERY_MEMORY_TEMPLATE` | `DELIVERY-MEMORY-v1` | `09_delivery_memory_template.md` |
