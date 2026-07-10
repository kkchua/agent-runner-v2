---
template_id: "SOP-EXISTING"
title: "Existing Repository Workflow SOP"
status: "active"
generated: "2026-07-10T14:20:05+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Existing Repository Workflow SOP

## Purpose

This SOP describes the workflow sequences for an existing repository that has already completed initial setup. It covers:

- First-time setup chain for new workstations
- Normal governed delivery for day-to-day development
- Drift reconciliation after code changes
- Governance refresh after contract changes
- Batch file usage for convenience

## First-Time Setup

The first-time setup chain initializes a new workstation for governed delivery:

### Sequence

```
00_master_docs_bootstrap_v1 (or v2)
    └── 10_execution_scaffold_v1
```

### Step 1: Master Docs Bootstrap

**Command:**
```batch
run-00_master_docs_bootstrap_v2.bat
```

**Purpose:** Generate master system documentation

**Outputs:**
- `docs/system/00_governance/bootstrap/README.md`
- `docs/system/00_governance/bootstrap/PROJECT_ANALYSIS.md`
- `docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md`
- `docs/system/00_governance/bootstrap/BUSINESS_CAPABILITIES.md`
- `docs/system/00_governance/bootstrap/FUNCTIONAL_SPEC.md`
- `docs/system/00_governance/bootstrap/NON_FUNCTIONAL_REQUIREMENTS.md`
- `docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md`
- `docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md`
- `docs/system/00_governance/bootstrap/DECISION_LOG.md`
- `docs/system/00_governance/bootstrap/SYSTEM_FILE_STRUCTURE.md`
- `docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md`
- `docs/system/00_governance/bootstrap/RUNBOOK.md`
- `docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md`
- `docs/codebase/01_inventory/codebase_inventory.md`
- `docs/codebase/02_modules/*.md` (72 files)
- `docs/codebase/03_components/*.md` (6 files)

### Step 2: Execution Scaffold

**Command:**
```batch
run-10_execution_scaffold_v1.bat
```

**Purpose:** Generate delivery governance

**Outputs:**
- `docs/delivery/00_governance/DELIVERY_SOP.md`
- `docs/delivery/00_governance/DELIVERY_STATUS_RULES.md`
- `docs/delivery/00_governance/DELIVERY_TEMPLATE_REGISTRY.md`
- `docs/delivery/00_governance/DELIVERY_VALIDATION_TEMPLATE.md`
- `docs/delivery/00_governance/DELIVERY_AGENTS.md`
- `docs/codebase/00_governance/CODEBASE_DOC_SOP.md`
- `docs/codebase/00_governance/CODEBASE_DOC_STATUS_RULES.md`
- `docs/codebase/00_governance/CODEBASE_TEMPLATE_REGISTRY.md`
- `docs/codebase/01_templates/CODEBASE_INVENTORY_TEMPLATE.md`
- `docs/codebase/01_templates/CODEBASE_MODULE_TEMPLATE.md`
- `docs/codebase/01_templates/CODEBASE_COMPONENT_TEMPLATE.md`
- `docs/codebase/01_templates/CODEBASE_CHANGE_TEMPLATE.md`
- `docs/codebase/01_inventory/CODEBASE_INVENTORY.md`

## Normal Governed Delivery

The normal governed delivery chain for implementing changes:

### Sequence

```
20_initiative_intake_v1
    └── 30_delivery_planning_v1
            └── 31_task_execution_v1
```

### Step 1: Initiative Intake

**Command:**
```batch
run-20_initiative_intake_v1.bat <initiative-id>
```

**Purpose:** Capture and refine initiative requirements

**Inputs:** Draft initiative or enhancement idea
**Outputs:**
- `docs/delivery/02_initiatives/INIT-<id>.md`
- Refined requirements and scope

### Step 2: Delivery Planning

**Command:**
```batch
run-30_delivery_planning_v1.bat <initiative-id>
```

**Purpose:** Generate plan and task graph

**Outputs:**
- `docs/delivery/03_plans/PLAN-<id>.md`
- `docs/delivery/04_tasks/TASK-<id>-<seq>.md` (task graph)

### Step 3: Task Execution

**Command:**
```batch
run-31_task_execution_v1.bat <initiative-id> --task-id <task-id>
```

**Purpose:** Implement and validate tasks

**Outputs:**
- `docs/delivery/06_implementations/IMPL-<id>-<seq>.md`
- `docs/delivery/07_reviews/REVIEW-<id>-<seq>.md`
- `docs/delivery/08_validations/VALIDATION-<id>-<seq>.md`
- Code changes in repository

## Drift Reconciliation

The drift-recovery path via documentation sync:

### When to Run

- After code changes outside normal workflow
- When documentation becomes stale
- After merging external contributions
- Periodic maintenance

### Command

```batch
run-40_documentation_sync_v1.bat
```

**Purpose:** Reconcile codebase documentation with current repository state

**Outputs:**
- Refreshed `docs/codebase/01_inventory/codebase_inventory.md`
- Updated `docs/codebase/02_modules/*.md`
- Updated `docs/codebase/03_components/*.md`
- New `docs/codebase/04_changes/<change-id>-bootstrap.md`

### Rerunning After Drift

After significant drift or contract changes, rerun first-time setup:

```batch
run-00_master_docs_bootstrap_v2.bat
run-10_execution_scaffold_v1.bat
```

## Governance Refresh

The governance refresh path for updating SOPs and templates:

### When to Run

- After changing delivery SOPs
- After changing template structure
- After adding new workflow families
- After contract changes

### Command

```batch
run-10_execution_scaffold_v1.bat --refresh
```

**Purpose:** Regenerate delivery governance documents

## Architecture Communication

The architecture communication phase via HTML site generation:

### Command

```batch
run-50_architecture_site_v1.bat
```

**Purpose:** Publish browsable HTML architecture views

**Outputs:**
- `docs/sites/architecture/` (browsable HTML site)
- `docs/sites/architecture/index.html`
- Audience-specific views (stakeholder, developer, operator, tester, user)

### Audience Sites

```batch
run-51_stakeholder_docs_v1.bat
run-52_developer_docs_v1.bat
run-53_operator_docs_v1.bat
run-54_tester_docs_v1.bat
run-55_user_docs_v1.bat
```

## Batch Files

Convenience batch files for workflow execution:

| Batch File | Workflow | Purpose |
|------------|----------|---------|
| `run-00_master_docs_bootstrap_v1.bat` | 00_master_docs_bootstrap_v1 | Bootstrap system docs (v1) |
| `run-00_master_docs_bootstrap_v2.bat` | 00_master_docs_bootstrap_v2 | Bootstrap system docs (v2) |
| `run-10_execution_scaffold_v1.bat` | 10_execution_scaffold_v1 | Generate delivery governance |
| `run-20_initiative_intake_v1.bat` | 20_initiative_intake_v1 | Capture initiative |
| `run-21_bug_fix_intake_v1.bat` | 21_bug_fix_intake_v1 | Bug triage and fix |
| `run-30_delivery_planning_v1.bat` | 30_delivery_planning_v1 | Generate plan/task graph |
| `run-31_task_execution_v1.bat` | 31_task_execution_v1 | Implement tasks |
| `run-40_documentation_sync_v1.bat` | 40_documentation_sync_v1 | Reconcile docs |
| `run-50_architecture_site_v1.bat` | 50_architecture_site_v1 | Generate HTML site |

### Usage Pattern

```batch
.venv\Scripts\activate && ukbe-run-agent run <workflow> --initiative-id <id>
```

## Notes

### Workflow Categories

| Category | Workflows | Use Case |
|----------|-----------|----------|
| **Bootstrap** | 00_* | System and codebase documentation |
| **Scaffold** | 10_* | Delivery governance setup |
| **Intake** | 20_*, 21_* | Initiative and bug capture |
| **Planning** | 30_* | Plan and task generation |
| **Execution** | 31_* | Implementation and validation |
| **Sync** | 40_* | Documentation reconciliation |
| **Audience** | 41_*, 51-55_* | Audience-specific documentation |
| **Site** | 50_* | HTML site generation |

### Protected Documents

All documents in `docs/system/`, `docs/codebase/`, and `docs/delivery/` are **workflow-generated** and protected from manual edits. Changes must flow through the appropriate workflow.

### Rerunning Workflows

Workflows are idempotent where possible. Rerunning will:
- Refresh existing documents
- Add new documents for new initiatives
- Update change impact documents

### Daemon Mode

For continuous operation, use daemon mode:

```batch
ukbe-run-agent daemon
```

The daemon:
- Polls backend for available work
- Does NOT need restart for code changes
- Spawns fresh subprocesses for each step

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Workflow not found | Run `ukbe-run-agent init` |
| Bundle drift | Run `ukbe-run-agent init` to sync |
| Step hangs | Kill process and retry |
| Test failures | Check `tests/unit/` and `tests/integration/` |

### Related Documents

| Document | Purpose |
|----------|---------|
| [RUNBOOK.md](RUNBOOK.md) | Operational procedures |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Development setup |
