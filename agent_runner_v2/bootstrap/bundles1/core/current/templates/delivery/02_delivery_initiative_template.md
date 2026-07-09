---
template_id: "DELIVERY-INIT-v1"
title: "Delivery Initiative Template"
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

- **Template ID**: DELIVERY-INIT-v1
- **Artifact Key**: `DELIVERY_INITIATIVE_TEMPLATE`
- **Version**: 1.0
- **Owner**: Initiative Intake Workflow
- **Purpose**: Captures initiative requirements, scope, documentation obligations, and acceptance criteria for delivery planning

# Initiative Description

**Title**: [Initiative title]

**Summary**: [2-3 sentence overview of what this initiative aims to accomplish]

**Business Value**: [Why this initiative matters — business impact, user benefit, technical debt reduction]

**Current Profile**: [Describe current architecture standard in use, e.g., "none", "legacy monolith", "DDD baseline"]

**Target Profile**: [Describe target architecture standard, e.g., "DDD/EDA hybrid", "event-driven microservices", "migration mode active"]

**Migration Mode**: [If transitioning between profiles, describe migration approach: "big bang", "strangler fig", "parallel run", "not applicable"]

# Scope

## In Scope

- [List specific deliverables, features, or changes included in this initiative]
- [Be explicit about boundaries]

## Out of Scope

- [List items explicitly excluded to prevent scope creep]
- [Clarify what will NOT be addressed]

## Likely Codebase Areas

- [Identify modules, packages, or components likely to be modified]
- [Reference module documentation paths from codebase inventory]
- [Example: `agent_runner_v2/step_runner.py`, `docs/codebase/02_modules/step_runner.md`]

## Stale Guidance Risk

- [Identify documentation that may become stale due to this initiative]
- [Assess risk level: LOW/MEDIUM/HIGH]
- [Specify which docs need updates and why]

# Documentation Scope

## Documentation Obligations

- [List all documentation artifacts that must be created or updated]
- [Reference artifact keys: `SYSTEM_CONTEXT`, `COMPONENT_ARCHITECTURE`, `CODEBASE_INVENTORY`, etc.]
- [Distinguish between baseline obligations (universal) and profile-specific obligations (architecture-dependent)]

## Documentation Freshness Risks

- [Identify risks of documentation drift during implementation]
- [Specify mitigation strategies: sync workflows, change impact documents, manual reviews]

## Owner-Doc Path

- [Specify which documentation files are owned by which roles/teams]
- [Example: "Module docs owned by implementing developer; component docs owned by architect"]

## Documentation Mode

- [Specify documentation approach: "auto-generated", "manual curation", "hybrid"]
- [Define synchronization frequency and trigger conditions]

# Acceptance Criteria

## Functional Criteria

- [List measurable functional outcomes]
- [Example: "Workflow executes end-to-end without errors"]
- [Example: "All artifact keys resolve correctly at runtime"]

## Documentation Criteria

- [List measurable documentation outcomes]
- [Example: "All modified modules have updated documentation"]
- [Example: "Codebase inventory reflects new module count"]
- [Example: "Change impact document created for all significant changes"]

## Quality Criteria

- [List quality gates: test pass rate, coverage thresholds, review approvals]
- [Example: "Unit tests pass at 100%"]
- [Example: "Integration tests cover backend API contract"]

# Dependencies

## Internal Dependencies

- [List dependencies on other initiatives, plans, or tasks within this repository]
- [Reference task graph or plan IDs if applicable]

## External Dependencies

- [List dependencies on external systems, APIs, or teams]
- [Example: "Backend API contract must be finalized before worker mode testing"]
- [Example: "Pushover credentials required for notification testing"]

# Notes

- [Additional context, assumptions, or constraints not captured elsewhere]
- [Link to related initiatives, discussions, or decision logs]
- [Record any deviations from standard workflow SOP]
