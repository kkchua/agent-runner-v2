---
template_id: DELIVERY-INITIATIVE-v1
status: active
generated: "2026-07-03T23:30:00+08:00"
workflow: 10_execution_scaffold_v1
step: generate_templates
managed_by: workflow-generated
version: 1.0.0
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Initiative Template

## Metadata

| Field | Value |
|-------|-------|
| **Template ID** | `DELIVERY-INITIATIVE-v1` |
| **Initiative ID** | `[INIT-XXXX-v1]` |
| **Title** | `[Initiative Title]` |
| **Status** | `draft` / `proposed` / `approved` / `rejected` / `active` / `completed` / `cancelled` |
| **Created** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Updated** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Author** | `[Agent or human author]` |
| **Workflow** | `10_execution_scaffold_v1` |
| **Step** | `initiative_intake_v1` |
| **Managed By** | workflow-generated |
| **Current Profile** | `[Architecture profile, e.g., modular-monolith]` |
| **Target Profile** | `[Target architecture, if changing]` |
| **Migration Mode** | `[greenfield / incremental / refactoring / legacy-merge]` |

## Initiative Description

<!-- Provide a concise description of the initiative. -->

**Background**:
[What prompted this initiative?]

**Problem Statement**:
[What problem does this initiative solve?]

**Proposed Solution**:
[High-level approach to address the problem.]

## Scope

<!-- Define the boundaries of the initiative. -->

### In Scope
- [Item 1]
- [Item 2]

### Out of Scope
- [Item 1]
- [Item 2]

### Architecture Profile Assessment

| Dimension | Value |
|-----------|-------|
| **Current Architecture** | `[Describe current architecture standard]` |
| **Target Architecture** | `[Describe target architecture, if changing]` |
| **Migration Mode** | `[greenfield / incremental / refactoring / legacy-merge]` |
| **DDD/EDA Applicability** | `[Applicable / Not applicable — DDD/EDA are conditional standards, not universal defaults]` |
| **Profile Change Impact** | `[Low / Medium / High — impact on existing codebase and documentation]` |

## Documentation Scope

<!-- Capture the documentation impact of this initiative. -->

### Documentation Areas Affected
- [List documentation areas that will need updates]

### Likely Codebase Areas
- [Identify source files, modules, or components that will change]

### Stale-Guidance Risk

| Risk | Severity | Mitigation |
|------|----------|-----------|
| `[Description]` | `[Low / Medium / High]` | `[Mitigation approach]` |

### Documentation Artifacts Required
- [ ] Updated module docs (`docs/codebase/02_modules/`)
- [ ] Updated component docs (`docs/codebase/03_components/`)
- [ ] Change-impact record (`docs/codebase/04_changes/`)
- [ ] Updated inventory (`docs/codebase/01_inventory/codebase_inventory.md`)
- [ ] New or revised delivery docs (`docs/delivery/`)

## Acceptance Criteria

- [ ] Initiative description is clear and testable
- [ ] Scope boundaries are explicit (in-scope and out-of-scope)
- [ ] Architecture profile assessment is complete
- [ ] Documentation scope is defined
- [ ] Stakeholder approval is obtained

## Dependencies

| Type | ID | Description | Status |
|------|----|-------------|--------|
| `[initiative / task / external]` | `[ID]` | `[Description]` | `[Status]` |

## Notes

<!-- Additional context, decisions, or references. -->
