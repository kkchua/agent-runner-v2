---
template_id: "DELIVERY-REG-v1"
title: "Delivery Template Registry"
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

- **Template ID**: DELIVERY-REG-v1
- **Version**: 1.0
- **Owner**: Delivery Scaffold Workflow
- **Purpose**: Central registry of all delivery workflow artifact templates

# Registry Overview

This document defines the complete set of delivery workflow templates used across all initiative, planning, execution, review, and validation workflows. Each template provides a standardized structure for artifacts generated during the delivery lifecycle.

Templates are organized into families based on their role in the delivery process:

1. **Initiative Family** — Captures requirements and scope (templates 01-02)
2. **Planning Family** — Defines strategy and task decomposition (templates 03-04)
3. **Execution Family** — Guides implementation and documentation updates (templates 05-06)
4. **Quality Family** — Validates changes and preserves knowledge (templates 07-09)

All templates use YAML frontmatter with stable `template_id` values and include workflow-generated metadata blocks. Templates must be referenced using their exact artifact key names as defined below.

# Template Families

## Initiative Templates

| Artifact Key | Template File | Purpose |
|--------------|---------------|---------|
| `DELIVERY_INITIATIVE_TEMPLATE` | `02_delivery_initiative_template.md` | Captures initiative description, scope, documentation scope, acceptance criteria, dependencies, and notes |

## Planning Templates

| Artifact Key | Template File | Purpose |
|--------------|---------------|---------|
| `DELIVERY_PLAN_TEMPLATE` | `03_delivery_plan_template.md` | Defines plan objective, strategy overview, scope mapping, task breakdown, documentation strategy, risks, deliverables, acceptance criteria, and notes |
| `DELIVERY_TASK_GRAPH_TEMPLATE` | `04_delivery_task_graph_template.md` | Maps task graph objective, execution flow, documentation workstream, success criteria, cross-references, and notes |

## Execution Templates

| Artifact Key | Template File | Purpose |
|--------------|---------------|---------|
| `DELIVERY_TASK_TEMPLATE` | `05_delivery_task_template.md` | Specifies task objective, description, inputs, outputs, acceptance criteria, execution steps, validation criteria, documentation impact, dependencies, and notes |
| `DELIVERY_IMPL_TEMPLATE` | `06_delivery_impl_template.md` | Details implementation objective, overview, changes overview, implementation steps, code changes, documentation update plan, risk assessment, validation criteria, and notes |

## Quality Templates

| Artifact Key | Template File | Purpose |
|--------------|---------------|---------|
| `DELIVERY_REVIEW_TEMPLATE` | `07_delivery_review_template.md` | Covers review scope, summary, findings, code quality assessment, documentation compliance, verdict, resolution tracker, and notes |
| `DELIVERY_VALIDATION_TEMPLATE` | `08_delivery_validation_template.md` | Validates code changes and documentation synchronization with validation scope, code validation, documentation synchronization validation, validation issues, validation summary, verdict, approval, and notes |
| `DELIVERY_MEMORY_TEMPLATE` | `09_delivery_memory_template.md` | Preserves context, summary, outcomes, lessons learned, reusable patterns, anti-patterns, documentation notes, related memories, and notes |

# Usage Rules

1. **Template Selection**: Choose the template that matches your current workflow step. Do not mix template structures across families.

2. **Artifact Keys**: Always reference templates using their exact artifact key names (e.g., `DELIVERY_INITIATIVE_TEMPLATE`, not "initiative template"). These keys are used by the prompt rendering system to resolve actual file paths at runtime.

3. **Frontmatter Requirements**: Every generated artifact must include YAML frontmatter with:
   - `template_id`: Matching the template contract exactly
   - `managed_by`: Set to `workflow-generated`
   - `workflow`: The workflow family that generated this artifact
   - `step`: The specific step within the workflow

4. **Section Headings**: Use the exact section headings specified in each template. Do not rename or reorder sections unless explicitly authorized by the workflow router.

5. **Documentation Impact**: Task and implementation templates must include documentation-impact sections. Validation templates must validate both code changes and documentation synchronization.

6. **Profile Tracking**: When repository standards are unclear or changing, initiative, plan, task, and implementation templates must capture:
   - Current profile (what architecture standard is currently in use)
   - Target profile (what architecture standard is being adopted)
   - Migration mode (how the transition will occur)

7. **Baseline vs Profile-Specific Obligations**: Plan templates must distinguish between baseline documentation obligations (universal requirements) and profile-specific architectural obligations (DDD/EDA/migration-mode requirements).

# Cross-References

- **Codebase Templates**: See `CODEBASE_TEMPLATE_REGISTRY` for codebase documentation templates
- **Delivery SOP**: See `DELIVERY_SOP` for operational procedures governing template usage
- **Status Rules**: See `DELIVERY_STATUS_RULES` for artifact status definitions and lifecycle rules
- **Agent Contracts**: See `DELIVERY_AGENTS_MD` for agent role responsibilities in template generation
