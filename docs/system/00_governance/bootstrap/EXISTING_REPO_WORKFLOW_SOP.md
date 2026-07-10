---
template_id: "SYS-00-SOP"
title: "Existing Repo Workflow SOP - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:56:49+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04_generate_architecture_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Existing Repo Workflow SOP: agent-runner-v2

## Purpose

This SOP defines the standard operating procedure for working with the agent-runner-v2 repository, including first-time setup, normal governed delivery, drift reconciliation, and governance refresh.

## First-Time Setup

### Step 1: Run 00_master_docs_bootstrap_v2

**Purpose**: Generate master system documentation bundle.

**Command**:
```bash
run-00_master_docs_bootstrap_v2.bat
```

**Outputs**:
- `docs/system/00_governance/bootstrap/PROJECT_ANALYSIS.md`
- `docs/system/00_governance/bootstrap/README.md`
- `docs/system/00_governance/bootstrap/SYSTEM_OVERVIEW.md`
- `docs/system/00_governance/bootstrap/BUSINESS_CAPABILITIES.md`
- `docs/system/00_governance/bootstrap/FUNCTIONAL_SPEC.md`
- `docs/system/00_governance/bootstrap/NON_FUNCTIONAL_REQUIREMENTS.md`
- `docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md`
- `docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md`
- `docs/system/00_governance/bootstrap/BUNDLE_MIGRATION_PLAN.md`
- `docs/system/00_governance/bootstrap/SYSTEM_CONTEXT.md`
- `docs/system/00_governance/bootstrap/COMPONENT_ARCHITECTURE.md`
- `docs/system/00_governance/bootstrap/DECISION_LOG.md`
- `docs/system/00_governance/bootstrap/SYSTEM_FILE_STRUCTURE.md`
- `docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md`
- `docs/system/00_governance/bootstrap/RUNBOOK.md`
- `docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md`

### Step 2: Run 10_execution_scaffold_v2

**Purpose**: Establish delivery governance (SOPs, templates, agents).

**Command**:
```bash
run-10_execution_scaffold_v2.bat
```

**Outputs**:
- `docs/delivery/` - Delivery SOPs and templates
- `docs/codebase/` - Codebase documentation governance
- Agent contracts

### First-Time Setup Chain

```
00_master_docs_bootstrap_v2
    ↓
10_execution_scaffold_v2
    ↓
[Repository ready for normal governed delivery]
```

## Normal Governed Delivery

### Step 1: Run 20_initiative_intake_v1

**Purpose**: Capture initiative requirements and generate draft documents.

**Command**:
```bash
run-20_initiative_intake_v1.bat
```

**Inputs**: User provides initiative description

**Outputs**:
- `docs/delivery/01_initiatives/INIT-<id>.md`

### Step 2: Run 30_delivery_planning_v1

**Purpose**: Generate plan, task graph, and task contracts from initiative.

**Command**:
```bash
run-30_delivery_planning_v1.bat
```

**Inputs**: `INIT_FILE` from previous step

**Outputs**:
- `docs/delivery/02_plans/PLAN-<id>.md`
- `docs/delivery/03_task_graphs/TASK_GRAPH-<id>.md`
- `docs/delivery/05_tasks/TASK-<id>-<n>.md`

### Step 3: Run 31_task_execution_v1

**Purpose**: Execute implementation, review, validation.

**Command**:
```bash
run-31_task_execution_v1.bat
```

**Inputs**: `TASK_FILE` from previous step

**Outputs**:
- `docs/delivery/06_impls/IMPL-<id>-<n>.md`
- `docs/delivery/07_reviews/REVIEW-<id>-<n>.md`
- `docs/delivery/08_validations/VALIDATION-<id>-<n>.md`

### Normal Governed Delivery Chain

```
20_initiative_intake_v1
    ↓
30_delivery_planning_v1
    ↓
31_task_execution_v1
    ↓
[Task complete, documentation synchronized]
```

## Drift Reconciliation

### When to Run

Run `40_documentation_sync_v1` when:
- Code changes occurred outside normal workflow
- Documentation is stale or incomplete
- Repository structure changed significantly
- Need to regenerate codebase documentation

### Step: Run 40_documentation_sync_v1

**Purpose**: Reconcile codebase documentation with current repository state.

**Command**:
```bash
run-40_documentation_sync_v1.bat
```

**Outputs**:
- Updated `docs/codebase/01_inventory/codebase_inventory.md`
- Updated module documentation
- Updated component documentation
- Change impact documentation

### Drift Recovery Path

```
[Drift detected]
    ↓
40_documentation_sync_v1
    ↓
[Documentation synchronized]
```

## Governance Refresh

### When to Run

Re-run `00_master_docs_bootstrap_v2` and `10_execution_scaffold_v2` when:
- Significant architectural changes
- New workflow families added
- Documentation standards changed
- Contract definitions updated

### Governance Refresh Chain

```
00_master_docs_bootstrap_v2
    ↓
10_execution_scaffold_v2
    ↓
40_documentation_sync_v1
    ↓
[Governance refreshed]
```

## Architecture Communication Phase

### Step: Run 50_architecture_site_v1

**Purpose**: Publish browsable HTML architecture views.

**Command**:
```bash
run-50_architecture_site_v1.bat
```

**Outputs**:
- `docs/system/00_governance/bootstrap/stakeholders.html`
- `docs/system/00_governance/bootstrap/developers.html`
- `docs/system/00_governance/bootstrap/operators.html`
- `docs/system/00_governance/bootstrap/functional.html`
- `docs/system/00_governance/bootstrap/runtime.html`

### Architecture Communication Path

```
[After governance refresh or normal delivery]
    ↓
50_architecture_site_v1
    ↓
[HTML sites published]
```

## Complete Delivery Lifecycle

```
First-Time Setup:
├── 00_master_docs_bootstrap_v2
└── 10_execution_scaffold_v2

Normal Delivery:
├── 20_initiative_intake_v1
├── 30_delivery_planning_v1
└── 31_task_execution_v1

Drift Recovery:
└── 40_documentation_sync_v1

Architecture Communication:
└── 50_architecture_site_v1
```

## Batch Files

| Batch File | Workflow | Purpose |
|------------|----------|---------|
| `run-00_master_docs_bootstrap_v2.bat` | `00_master_docs_bootstrap_v2` | Generate master system docs |
| `run-10_execution_scaffold_v2.bat` | `10_execution_scaffold_v2` | Establish delivery governance |
| `run-20_initiative_intake_v1.bat` | `20_initiative_intake_v1` | Initiative intake |
| `run-21_bug_fix_intake_v1.bat` | `21_bug_fix_intake_v1` | Bug fix workflow |
| `run-30_delivery_planning_v1.bat` | `30_delivery_planning_v1` | Delivery planning |
| `run-31_task_execution_v1.bat` | `31_task_execution_v1` | Task execution |
| `run-40_documentation_sync_v1.bat` | `40_documentation_sync_v1` | Documentation reconciliation |
| `run-50_architecture_site_v1.bat` | `50_architecture_site_v1` | Generate architecture sites |

## Notes

### Workflow Re-execution After Drift

When repository code or contracts change:

1. **Minor changes**: Run `40_documentation_sync_v1` only
2. **Major changes**: Run full governance refresh chain
3. **Contract changes**: May require `00_master_docs_bootstrap_v2` re-run

### Bootstrap vs Runtime Distinction

- **Bootstrap source**: `agent_runner_v2/bootstrap/workflows/default/`
- **Runtime bundles**: `~/.ukbe-runner/workflows/`
- **Changes to bootstrap**: Must sync to runtime via `sync_workflows.py`

### Plugin Workflow System

The repository is migrating from monolithic `TEMPLATE_GROUPS` to plugin workflow packages:

- **Legacy**: `template_groups.py` dict
- **New**: `workflows/<name>/workflow.toml` packages
- **Current state**: Both supported via adapter pattern

### Test Coverage

- **Unit tests**: `tests/unit/` (45 passing)
- **Integration tests**: `tests/integration/`
- **Run before commit**: `pytest`

---

*Last updated: 2026-07-10T19:56:49+08:00 via workflow `00_master_docs_bootstrap_v2`*
