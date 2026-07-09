---
template_id: "CODEBASE-REG-v1"
title: "Codebase Template Registry"
status: "active"
generated: "2026-07-09T10:35:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "07_generate_templates"
change_id: "10SCAFFOLD-20260708-8a4445fc"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Metadata

- **Template ID**: CODEBASE-REG-v1
- **Version**: 1.0
- **Owner**: Codebase Documentation Workflow
- **Purpose**: Central registry of all codebase documentation artifact templates

# Registry Overview

This document defines the complete set of codebase documentation templates used for documenting modules, components, changes, and maintaining inventory across the repository. Each template provides a standardized structure for artifacts generated during codebase documentation workflows.

Templates are organized into families based on their role in the documentation process:

1. **Inventory Family** — Tracks module/component inventory and status (templates 01-02)
2. **Module/Component Family** — Documents individual modules and components (templates 03-04)
3. **Change Family** — Tracks change impacts and documentation updates (template 05)

All templates use YAML frontmatter with stable `template_id` values and include workflow-generated metadata blocks. Templates must be referenced using their exact artifact key names as defined below.

# Template Families

## Inventory Templates

| Artifact Key | Template File | Purpose |
|--------------|---------------|---------|
| `CODEBASE_INVENTORY_TEMPLATE` | `02_codebase_inventory_template.md` | Defines template fields, entry template, status definitions, and file type coverage for codebase inventory management |
| `CODEBASE_INVENTORY` | `codebase_inventory.md` | Actual inventory document listing all modules/components with status tracking |

## Module/Component Templates

| Artifact Key | Template File | Purpose |
|--------------|---------------|---------|
| `CODEBASE_MODULE_TEMPLATE` | `03_codebase_module_template.md` | Documents individual Python modules with module overview, file inventory, architecture, key components, public API, dependencies, testing, change log, documentation governance, and notes |
| `CODEBASE_COMPONENT_TEMPLATE` | `04_codebase_component_template.md` | Documents higher-level components (packages, suites) with component overview, file coverage, interface, implementation details, dependencies, testing, change log, documentation governance, and notes |

## Change Templates

| Artifact Key | Template File | Purpose |
|--------------|---------------|---------|
| `CODEBASE_CHANGE_TEMPLATE` | `05_codebase_change_template.md` | Tracks change summary, changed files, documentation updates, stale documentation removal, documentation freshness verification, cross-references, and notes |

# Usage Rules

1. **Template Selection**: Choose the template that matches your documentation scope. Use module templates for individual `.py` files, component templates for packages/suites, and change templates for tracking modifications.

2. **Artifact Keys**: Always reference templates using their exact artifact key names (e.g., `CODEBASE_MODULE_TEMPLATE`, not "module template"). These keys are used by the prompt rendering system to resolve actual file paths at runtime.

3. **Frontmatter Requirements**: Every generated artifact must include YAML frontmatter with:
   - `template_id`: Matching the template contract exactly
   - `managed_by`: Set to `workflow-generated`
   - `workflow`: The workflow family that generated this artifact
   - `step`: The specific step within the workflow

4. **Section Headings**: Use the exact section headings specified in each template. Do not rename or reorder sections unless explicitly authorized by the workflow router.

5. **Documentation Governance**: Module and component templates must include a `Documentation Governance` section covering documentation status tracking, freshness checks, stale guidance handling, review and validation expectations, and synchronization requirements.

6. **Status Vocabulary**: Inventory must support four statuses: `current`, `needs_update`, `pending_review`, and `superseded`. All inventory entries must use one of these four statuses.

7. **Profile Metadata**: When a change introduces or replaces a declared architecture standard, inventory entries must include repo profile metadata documenting the architectural shift.

8. **Template ID Alignment**: Generated codebase inventory output must use the registry-aligned template id `CODEBASE-INV-v1`, not legacy markers like `CB-01`.

# Cross-References

- **Delivery Templates**: See `DELIVERY_TEMPLATE_REGISTRY` for delivery workflow templates
- **Codebase SOP**: See `CODEBASE_DOC_SOP` for operational procedures governing codebase documentation
- **Status Rules**: See `CODEBASE_DOC_STATUS_RULES` for documentation status definitions and lifecycle rules
- **Project Analysis**: See `PROJECT_ANALYSIS` for repository context informing documentation scope
