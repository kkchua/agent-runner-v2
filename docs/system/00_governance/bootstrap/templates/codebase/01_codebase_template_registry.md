---
template_id: CODEBASE-REGISTRY-v1
status: active
generated: "2026-07-03T23:30:00+08:00"
workflow: 10_execution_scaffold_v1
step: generate_templates
managed_by: workflow-generated
version: 1.0.0
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Codebase Template Registry

## Metadata

| Field | Value |
|-------|-------|
| **Template ID** | `CODEBASE-REGISTRY-v1` |
| **Status** | Active |
| **Generated** | 2026-07-03 |
| **Workflow** | `10_execution_scaffold_v1` |
| **Step** | `generate_templates` |
| **Version** | 1.0.0 |
| **Managed By** | workflow-generated |

## Registry Overview

This registry is the authoritative index of all codebase-documentation templates used by the `10_execution_scaffold_v1` workflow and any downstream workflows that produce or maintain codebase documentation. Every codebase document produced by the workflow must use one of the templates listed here.

The registry supports:
- **Universal ecosystem baseline**: All codebase templates work for any repository regardless of language or architecture.
- **File type coverage**: Templates cover all source file types — Python, JavaScript, configuration files, scripts, tests, documentation, and workflow files.
- **Status vocabulary**: All entries use a consistent status set — `current`, `needs_update`, `pending_review`, `superseded`.
- **Profile metadata support**: Inventory entries include room for repo profile metadata when a change introduces or replaces a declared architecture standard.
- **Ownership tracking**: Each entry tracks owner-doc path, documentation mode, and last-verified-by-change fields.

## Template Families

### Codebase Documentation Templates

| Template ID | File | Purpose | Status |
|-------------|------|---------|--------|
| `CODEBASE-INV-v1` | `02_codebase_inventory_template.md` | Codebase inventory entry template | Active |
| `CODEBASE-MOD-v1` | `03_codebase_module_template.md` | Module documentation template | Active |
| `CODEBASE-COMP-v1` | `04_codebase_component_template.md` | Component documentation template | Active |
| `CODEBASE-CHANGE-v1` | `05_codebase_change_template.md` | Change-impact tracking template | Active |

### Related Delivery Templates

| Template ID | File | Purpose | Status |
|-------------|------|---------|--------|
| `DELIVERY-REGISTRY-v1` | `../delivery/01_delivery_template_registry.md` | Delivery template registry | Active |
| `DELIVERY-TASK-v1` | `../delivery/05_delivery_task_template.md` | Task template with doc impact | Active |
| `DELIVERY-IMPL-v1` | `../delivery/06_delivery_impl_template.md` | Impl template with doc update plan | Active |
| `DELIVERY-VALIDATION-v1` | `../delivery/08_delivery_validation_template.md` | Validation with doc sync check | Active |

## Usage Rules

1. **Template Selection**: Every codebase document must use exactly one template from this registry. The `template_id` in YAML frontmatter must match the registry entry.

2. **Status Vocabulary**: All codebase documents use a standard status set:
   - `current` — up-to-date with the source code
   - `needs_update` — source code has changed; doc is behind
   - `pending_review` — updated; awaiting validation
   - `superseded` — replaced by a newer document

3. **File Type Coverage**: The inventory template covers ALL file types in the repository:
   - Source files (`.py`, `.js`, `.ts`, `.go`, `.rs`, etc.)
   - Configuration files (`pyproject.toml`, `.json`, `.yaml`, `.env`)
   - Scripts (`.sh`, `.bat`, `.ps1`)
   - Test files (`test_*.py`, `*_test.py`)
   - Workflow files (prompt templates, JSON workflows)
   - Documentation files (`.md` in `docs/`)

4. **Ownership Tracking**: Each inventory entry must specify:
   - `owner_doc_path` — path to the owning module or component doc
   - `documentation_mode` — `stub` / `summary` / `full`
   - `status` — one of the standard statuses
   - `last_verified_by_change` — change record that last verified this doc

5. **Profile Metadata**: When a change introduces or replaces an architecture standard, the inventory must record:
   - Previous profile
   - New profile
   - Migration mode

6. **Cross-Reference Integrity**: Templates that reference other templates must use the canonical `template_id` values listed in this registry.

## Cross-References

- **Delivery Template Registry**: See `../delivery/01_delivery_template_registry.md`
- **Workflow SOP**: See `../../WORKFLOW_SOP_v1.md`
- **Codebase Doc SOP**: See `../../../../codebase/00_standards/CODEBASE_DOC_SOP_v1.md`

## Artifact Keys

The following literal artifact keys are the canonical identifiers for codebase templates. These keys must be used in workflow configurations, runner scripts, and any cross-references that resolve codebase templates programmatically.

| Artifact Key | Template ID | File |
|-------------|-------------|------|
| `CODEBASE_TEMPLATE_REGISTRY` | `CODEBASE-REGISTRY-v1` | `01_codebase_template_registry.md` |
| `CODEBASE_INVENTORY_TEMPLATE` | `CODEBASE-INV-v1` | `02_codebase_inventory_template.md` |
| `CODEBASE_MODULE_TEMPLATE` | `CODEBASE-MOD-v1` | `03_codebase_module_template.md` |
| `CODEBASE_COMPONENT_TEMPLATE` | `CODEBASE-COMP-v1` | `04_codebase_component_template.md` |
| `CODEBASE_CHANGE_TEMPLATE` | `CODEBASE-CHANGE-v1` | `05_codebase_change_template.md` |
| `CODEBASE_INVENTORY` | `CODEBASE-INV-v1` | `docs/codebase/01_inventory/codebase_inventory.md` |
