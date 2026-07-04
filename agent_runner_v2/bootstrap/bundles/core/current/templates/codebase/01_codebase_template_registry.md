---
title: Codebase Template Registry
managed_by: workflow-generated
workflow: 10_execution_scaffold_v1
step: generate_templates
created: 2026-07-04
template_id: CODEBASE-REG-v1
version: 1
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Codebase Template Registry

## Metadata

| Field | Value |
|---|---|
| Template ID | `CODEBASE-REG-v1` |
| Owner Workflow | `10_execution_scaffold_v1` |
| Owner Step | `generate_templates` |
| Scope | Universal baseline — applies to all governed repositories |
| Status | `active` |
| Last Verified | 2026-07-04 |

This registry is the authoritative index of all codebase-documentation templates produced by `10_execution_scaffold_v1`. Each template has a stable artifact key, a fixed file path, and a defined role in the codebase-documentation lifecycle.

## Registry Overview

The codebase template family covers documentation for the repository source: inventory of all code files, module reference docs, component groupings, and change-impact records. Every template is workflow-generated, protected from manual edits, and emitted with YAML frontmatter containing a stable `template_id`.

| Artifact Key | Template ID | File Path | Role |
|---|---|---|---|
| `CODEBASE_TEMPLATE_REGISTRY` | `CODEBASE-REG-v1` | `docs/system/00_governance/bootstrap/templates/codebase/01_codebase_template_registry.md` | This document. Master index of all codebase templates. |
| `CODEBASE_INVENTORY_TEMPLATE` | `CODEBASE-INV-TEMPLATE-v1` | `docs/system/00_governance/bootstrap/templates/codebase/02_codebase_inventory_template.md` | Defines the structure for codebase inventory entries. Covers all source file types and supports statuses: `current`, `needs_update`, `pending_review`, `superseded`. |
| `CODEBASE_MODULE_TEMPLATE` | `CODEBASE-MOD-v1` | `docs/system/00_governance/bootstrap/templates/codebase/03_codebase_module_template.md` | Defines the structure for per-module reference documentation. |
| `CODEBASE_COMPONENT_TEMPLATE` | `CODEBASE-COMP-v1` | `docs/system/00_governance/bootstrap/templates/codebase/04_codebase_component_template.md` | Defines the structure for component grouping documentation. |
| `CODEBASE_CHANGE_TEMPLATE` | `CODEBASE-CHG-v1` | `docs/system/00_governance/bootstrap/templates/codebase/05_codebase_change_template.md` | Defines the structure for change-impact records tracking changed files, updated docs, and stale-doc removal. |
| `CODEBASE_INVENTORY` | `CODEBASE-INV-v1` | `docs/codebase/01_inventory/codebase_inventory.md` | The live codebase inventory for this repository. Conforms to `CODEBASE_INVENTORY_TEMPLATE`. |

## Template Families

### Inventory Templates
Templates that track and enumerate codebase assets:

- `CODEBASE_INVENTORY_TEMPLATE` — defines entry structure
- `CODEBASE_INVENTORY` — the live inventory instance

### Reference Templates
Templates that document code structure:

- `CODEBASE_MODULE_TEMPLATE` — per-module documentation
- `CODEBASE_COMPONENT_TEMPLATE` — per-component documentation

### Change Tracking Templates
Templates that record and trace changes:

- `CODEBASE_CHANGE_TEMPLATE` — change-impact records

### Governance Templates
Templates that define the codebase-docs framework itself:

- `CODEBASE_TEMPLATE_REGISTRY` — this document

## Usage Rules

1. **Every instance must carry the template_id.** When a workflow step produces a codebase-doc artifact from a template, the output YAML frontmatter MUST include the `template_id` of the source template.

2. **Section headings are fixed.** The section headings defined in each template are mandatory. Additional sections may be appended but existing headings must not be renamed or removed.

3. **Inventory must cover all source file types.** The codebase inventory MUST include entries for all file types discovered in the repository: Python modules, JSON configs, prompt templates, shell scripts, markdown context files, architecture-site outputs.

4. **Status vocabulary is fixed.** Every inventory entry MUST use one of the four defined statuses:
   - `current` — the entry accurately reflects the current state of the code
   - `needs_update` — the code has changed and the entry is stale
   - `pending_review` — the entry may be stale and requires human or agent review
   - `superseded` — the entry has been replaced by a newer entry

5. **Inventory uses registry-aligned template IDs.** The live codebase inventory MUST use `CODEBASE-INV-v1` as its `template_id`, not the legacy `CB-01` marker.

6. **Change-impact records must track three categories:** changed files, updated docs, and stale-doc removal.

7. **Profile metadata is supported but conditional.** When a change introduces or replaces a declared architecture standard, inventory entries MAY carry profile metadata fields.

8. **Inventory entries include owner-doc path, documentation mode, status, and last-verified-by-change fields.**

## Cross-References

| Reference | Location |
|---|---|
| Delivery Template Registry | `docs/system/00_governance/bootstrap/templates/delivery/01_delivery_template_registry.md` |
| Codebase Doc SOP | `docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md` |
| Codebase Doc Status Rules | `docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md` |
| Delivery Workflow SOP | `docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md` |
| Project Analysis | `docs/system/00_governance/bootstrap/project_analysis.md` |
| Existing Repo Workflow SOP | `docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md` |
