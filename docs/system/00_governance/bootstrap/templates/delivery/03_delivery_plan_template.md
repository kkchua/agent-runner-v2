---
template_id: DELIVERY-PLAN-v1
status: active
generated: "2026-07-03T23:30:00+08:00"
workflow: 10_execution_scaffold_v1
step: generate_templates
managed_by: workflow-generated
version: 1.0.0
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Delivery Plan Template

## Metadata

| Field | Value |
|-------|-------|
| **Template ID** | `DELIVERY-PLAN-v1` |
| **Plan ID** | `[PLAN-XXXX-v1]` |
| **Title** | `[Plan Title]` |
| **Status** | `draft` / `proposed` / `approved` / `active` / `completed` / `abandoned` |
| **Initiative ID** | `[INIT-XXXX-v1]` |
| **Created** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Updated** | `[YYYY-MM-DDTHH:MM:SS+TZ]` |
| **Author** | `[Agent or human author]` |
| **Workflow** | `10_execution_scaffold_v1` |
| **Step** | `delivery_planning_v1` |
| **Managed By** | workflow-generated |
| **Current Profile** | `[Architecture profile, e.g., modular-monolith]` |
| **Target Profile** | `[Target architecture, if changing]` |
| **Migration Mode** | `[greenfield / incremental / refactoring / legacy-merge]` |

## Plan Objective

<!-- State the primary objective of this delivery plan. -->

**Objective**: [What this plan achieves]

**Success Metric**: [How success is measured]

## Strategy Overview

<!-- High-level approach to achieving the plan objective. -->

### Architecture Profile Assessment

| Dimension | Value |
|-----------|-------|
| **Current Architecture** | `[Describe current architecture standard]` |
| **Target Architecture** | `[Describe target architecture, if changing]` |
| **Migration Mode** | `[greenfield / incremental / refactoring / legacy-merge]` |
| **DDD/EDA Applicability** | `[Applicable / Not applicable — conditional standards]` |

### Baseline vs Profile-Specific Obligations

| Obligation Type | Required | Description |
|----------------|----------|-------------|
| **Baseline: Module docs** | Always | Update `docs/codebase/02_modules/` for changed modules |
| **Baseline: Component docs** | Always | Update `docs/codebase/03_components/` for changed components |
| **Baseline: Inventory sync** | Always | Update `docs/codebase/01_inventory/codebase_inventory.md` |
| **Baseline: Change record** | Always | Create `docs/codebase/04_changes/` entry |
| **Profile: DDD aggregates** | Profile-specific | Document aggregate boundaries and bounded contexts |
| **Profile: EDA events** | Profile-specific | Document event schemas and stream contracts |
| **Profile: [other]** | Profile-specific | [Profile-specific documentation requirement] |

## Scope Mapping

<!-- Map plan scope to source code areas and documentation areas. -->

| Source Area | Documentation Area | Impact Level |
|-------------|-------------------|--------------|
| `[Module / file path]` | `[Corresponding doc]` | `[Low / Medium / High]` |

## Task Breakdown

<!-- Break the plan into executable tasks. -->

| Task ID | Description | Priority | Dependencies | Estimate |
|---------|-------------|----------|--------------|----------|
| `[TASK-XXXX]` | `[Description]` | `[P1/P2/P3]` | `[Dependencies]` | `[Estimate]` |

## Documentation Strategy

<!-- Define how documentation will be maintained throughout the delivery. -->

### Baseline Documentation Obligations
- [ ] All code changes have corresponding documentation updates
- [ ] Module docs updated in `docs/codebase/02_modules/`
- [ ] Component docs updated in `docs/codebase/03_components/`
- [ ] Inventory refreshed in `docs/codebase/01_inventory/codebase_inventory.md`
- [ ] Change-impact record created in `docs/codebase/04_changes/`

### Profile-Specific Documentation Obligations
- [ ] `[Profile-specific doc requirement]`

### Documentation Freshness Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| `[Description]` | `[Low / Medium / High]` | `[Mitigation approach]` |

### Documentation Review Gates
- [ ] Documentation review at task completion
- [ ] Documentation validation at implementation completion
- [ ] Documentation synchronization check at plan completion

## Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|-----------|
| `[Description]` | `[Low / Medium / High]` | `[Low / Medium / High]` | `[Mitigation approach]` |

## Deliverables

| Deliverable | Type | Description | Status |
|-------------|------|-------------|--------|
| `[Name]` | `[code / doc / config]` | `[Description]` | `[Pending / In Progress / Complete]` |

## Acceptance Criteria

- [ ] All tasks in the breakdown are completed
- [ ] All code changes pass validation
- [ ] All documentation is synchronized with code changes
- [ ] Architecture profile obligations are met
- [ ] Documentation freshness is verified

## Notes

<!-- Additional context, decisions, or references. -->
