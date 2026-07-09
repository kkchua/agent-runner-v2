---
template_id: "SYS-00-SOP"
managed_by: workflow-generated
generated: "2026-07-09T21:26:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Existing Repository Workflow SOP

## Purpose

This document describes the standard operating procedure for onboarding existing repositories to the agent-runner-v2 governed delivery framework and for rerunning workflows after drift or contract changes.

## First-Time Setup

The first-time setup chain initializes a repository for governed delivery:

### Step 1: Bootstrap System Documentation

**Workflow**: `00_master_docs_bootstrap_v1`

**Command**:
```bash
run-00_master_docs_bootstrap_v1.bat
```

**What it does**:
1. Scans repository structure
2. Generates project analysis
3. Creates system documentation (this doc set)
4. Establishes documentation standard
5. Creates bundle taxonomy and migration plan

**Artifacts**:
- `PROJECT_ANALYSIS.md`
- `SYSTEM_OVERVIEW.md`
- `FUNCTIONAL_SPEC.md`
- `COMPONENT_ARCHITECTURE.md` (this document)
- `DEVELOPER_GUIDE.md`
- `RUNBOOK.md`
- And 15+ other system documents

**When to rerun**:
- After significant repository restructuring
- When project analysis becomes stale
- When documentation standard changes

### Step 2: Scaffold Delivery Framework

**Workflow**: `10_execution_scaffold_v1`

**Command**:
```bash
run-10_execution_scaffold_v1.bat
```

**What it does**:
1. Analyzes project structure
2. Generates delivery SOP and status rules
3. Creates delivery templates
4. Generates agent contracts
5. Establishes `docs/delivery/` structure

**Artifacts**:
- `DELIVERY_SOP_v1.md`
- `DELIVERY_STATUS_RULES_v1.md`
- `AGENTS.md` + 6 agent contracts
- Delivery templates (initiative, plan, task, etc.)
- `CODEBASE_DOC_SOP_v1.md`

**When to rerun**:
- When delivery process changes
- When agent contracts need refresh
- When templates need update

**Order matters**: Must run after `00_master_docs_bootstrap_v1` completes successfully.

## Normal Governed Delivery

After first-time setup, normal work follows this chain:

### Step 1: Initiative Intake

**Workflow**: `20_initiative_intake_v1`

**Command**:
```bash
run-20_initiative_intake_v1.bat
```

**What it does**:
- Captures new initiative or enhancement
- Drafts pre-init document
- Reviews and refines requirements
- Creates `INIT_FILE` for approved initiatives

**Entry points**:
- New feature request
- Enhancement idea
- Technical debt item

**Artifacts**:
- `DRAFT_INIT_FILE` (draft)
- `PRE_INIT_FILE` (refined)
- `INIT_FILE` (approved)

### Step 2: Delivery Planning

**Workflow**: `30_delivery_planning_v1`

**Command**:
```bash
run-30_delivery_planning_v1.bat
```

**What it does**:
- Reads `INIT_FILE`
- Generates implementation plan
- Decomposes into task graph
- Creates task contracts

**Artifacts**:
- `PLAN_FILE`
- `TASK_GRAPH_FILE`
- `TASK_FILE` (per task)

**Loop behavior**:
- Plan may be rejected and replanned
- Task graph may be refined
- Replanning preserves approved artifacts

### Step 3: Task Execution

**Workflow**: `31_task_execution_v1`

**Command**:
```bash
run-31_task_execution_v1.bat
```

**What it does**:
- Plans implementation for each task
- Reviews and refines implementation plan
- Executes implementation
- Validates results

**Artifacts**:
- `IMPL_FILE`
- `REVIEW_FILE`
- `VALIDATION_FILE`

**Loop behavior**:
- Implementation may be rejected and refined
- Validation may trigger fixes
- Retries tracked in job state

## Drift Reconciliation

When documentation drifts from code or contracts change:

### Documentation Sync

**Workflow**: `40_documentation_sync_v1`

**Command**:
```bash
run-40_documentation_sync_v1.bat
```

**What it does**:
- Scans current repository state
- Identifies stale documentation
- Regenerates affected docs
- Preserves manual annotations (in unguarded sections)

**When to run**:
- After significant code changes
- When documentation appears stale
- Before major releases
- After contract changes

**Preservation rules**:
- Sections outside guarded blocks preserved
- Manual annotations in unguarded sections kept
- Workflow-generated sections refreshed

## Governance Refresh

After drift recovery, refresh governance:

### Step 1: Developer Documentation

**Workflow**: `41_developer_doc_v1`

**Command**:
```bash
run-41_developer_doc_v1.bat
```

### Step 2: Operator Documentation

**Workflow**: `41_operator_doc_v1`

**Command**:
```bash
run-41_operator_doc_v1.bat
```

### Step 3: Stakeholder Documentation

**Workflow**: `41_stakeholder_doc_v1`

**Command**:
```bash
run-41_stakeholder_doc_v1.bat
```

### Step 4: Architecture Site

**Workflow**: `50_architecture_site_v1`

**Command**:
```bash
run-50_architecture_site_v1.bat
```

**What it does**:
- Generates HTML architecture views
- Publishes browsable documentation
- Creates stakeholder/developer/operator/functional views

**Artifacts**:
- `docs/site/architecture/` (HTML)
- `ARCHITECTURE_SITE_INDEX`
- `ARCHITECTURE_SITE_MANIFEST`

## Batch Files

### Workflow Launchers

| Batch File | Purpose | Chain |
|------------|---------|-------|
| `run-00_master_docs_bootstrap_v1.bat` | Bootstrap system docs | First-time setup |
| `run-10_execution_scaffold_v1.bat` | Scaffold delivery framework | First-time setup |
| `run-20_initiative_intake_v1.bat` | New initiative | Normal delivery |
| `run-21_bug_fix_intake_v1.bat` | Bug fix intake | Normal delivery |
| `run-30_delivery_planning_v1.bat` | Delivery planning | Normal delivery |
| `run-31_task_execution_v1.bat` | Task execution | Normal delivery |
| `run-40_documentation_sync_v1.bat` | Documentation sync | Drift recovery |
| `run-50_architecture_site_v1.bat` | Architecture site | Governance refresh |
| `run-41_developer_doc_v1.bat` | Developer docs | Governance refresh |
| `run-41_operator_doc_v1.bat` | Operator docs | Governance refresh |
| `run-41_stakeholder_doc_v1.bat` | Stakeholder docs | Governance refresh |

### Submission Batch Files

| Batch File | Purpose |
|------------|---------|
| `submit-00_master_docs_bootstrap_v1.bat` | Submit bootstrap to backend |
| `submit-10_execution_scaffold_v1.bat` | Submit scaffold to backend |
| `submit-40_documentation_sync_v1.bat` | Submit sync to backend |

### Sync Batch Files

| Batch File | Purpose |
|------------|---------|
| `sync-workflows-to-backend.bat` | Sync workflow bundles |
| `sync-10_execution_scaffold_v1-workflow-spec.bat` | Sync scaffold spec |

## Notes

### Workflow Execution Modes

**Local Mode** (`run-*.bat`):
- Executes on local workstation
- Uses local coder tools
- Results stored in local job directories

**Backend Mode** (`submit-*.bat`):
- Submits to backend work queue
- Picked up by worker daemons
- Results tracked in backend database

### Re-Running Workflows

**After bootstrap changes**:
1. Update bootstrap source
2. Run sync batch files
3. Rerun affected workflows

**After prompt changes**:
1. Edit prompt templates
2. Run sync batch files
3. Test with `run-*.bat`

**After code changes**:
1. Run `run-40_documentation_sync_v1.bat` to update codebase docs
2. Review change impact document
3. Update affected system docs if needed

### Workflow Dependencies

```
00_master_docs_bootstrap_v1
    ↓ (required before)
10_execution_scaffold_v1
    ↓ (required before)
20_initiative_intake_v1 → 30_delivery_planning_v1 → 31_task_execution_v1
    ↓ (may trigger)
40_documentation_sync_v1 → 41_*_doc_v1 → 50_architecture_site_v1
```

### Approval Gates

Some steps require human approval:
- Pre-init review (`20_initiative_intake_v1`)
- Plan review (`30_delivery_planning_v1`)
- Implementation review (`31_task_execution_v1`)

Approval commands:
```bash
ukbe-run-agent approve <job-id>
ukbe-run-agent reject <job-id> [--reason "..."]
ukbe-run-agent force-approve <job-id>  # Emergency only
```

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 04_generate_architecture_docs*
