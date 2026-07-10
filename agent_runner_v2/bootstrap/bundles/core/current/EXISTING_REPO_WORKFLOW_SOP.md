---
template_id: "SOP-01-ERW"
title: "Existing Repo Workflow SOP"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
managed_by: workflow-generated
generated: "2026-07-10T09:52:38+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Existing Repo Workflow SOP

## Purpose

This SOP defines the standard operating procedure for existing repositories using the agent-runner-v2 workflow system. It covers first-time setup, normal governed delivery, drift reconciliation, and governance refresh workflows.

## First-Time Setup

For repositories that have not yet bootstrapped the delivery governance system:

### Step 1: Run Master Docs Bootstrap

**Command**:
```batch
run-00_master_docs_bootstrap_v1.bat
```

**What it does**:
- Generates PROJECT_ANALYSIS.md
- Generates system overview documents (SYSTEM_OVERVIEW.md, BUSINESS_CAPABILITIES.md, FUNCTIONAL_SPEC.md, NON_FUNCTIONAL_REQUIREMENTS.md)
- Generates architecture documents (SYSTEM_CONTEXT.md, COMPONENT_ARCHITECTURE.md, DECISION_LOG.md, SYSTEM_FILE_STRUCTURE.md, DEVELOPER_GUIDE.md, RUNBOOK.md)
- Generates integration and failure documents
- Generates EXISTING_REPO_WORKFLOW_SOP.md

**Duration**: ~30-60 minutes
**Artifacts**: 13 documents in `docs/system/00_governance/bootstrap/`

### Step 2: Run Execution Scaffold

**Command**:
```batch
run-10_execution_scaffold_v1.bat
```

**What it does**:
- Generates delivery SOP and status rules
- Generates codebase doc SOP and status rules
- Generates template registry and templates
- Generates agent contracts (AGENTS.md + 6 individual)

**Duration**: ~45-90 minutes
**Artifacts**: 9 delivery templates + 6 codebase templates + 7 agent contracts

**Setup Chain**: `00_master_docs_bootstrap_v1` → `10_execution_scaffold_v1`

## Normal Governed Delivery

For day-to-day development work after initial setup:

### Chain: Initiative Intake → Delivery Planning → Task Execution

```
20_initiative_intake_v1 → 30_delivery_planning_v1 → 31_task_execution_v1
```

### Step 1: Initiative Intake

**Command**:
```batch
run-20_initiative_intake_v1.bat
```

**What it does**:
- Captures requirement and documentation scope
- Drafts initiative pre-init document
- Reviews and refines initiative
- Produces INIT_FILE

**Duration**: ~20-40 minutes
**Output**: `docs/delivery/01_initiatives/`

### Step 2: Delivery Planning

**Command**:
```batch
run-30_delivery_planning_v1.bat
```

**What it does**:
- Generates plan from initiative
- Creates task graph
- Generates individual tasks
- Produces PLAN_FILE, TASK_GRAPH_FILE, TASK_FILEs

**Duration**: ~30-60 minutes
**Output**: `docs/delivery/02_plans/`, `docs/delivery/03_task_graphs/`, `docs/delivery/04_tasks/`

### Step 3: Task Execution

**Command**:
```batch
run-31_task_execution_v1.bat
```

**What it does**:
- Creates implementation plan
- Executes implementation
- Reviews and refines
- Validates output
- Produces IMPL_FILE, REVIEW_FILE, VALIDATION_FILE

**Duration**: ~60-180 minutes (varies by task size)
**Output**: `docs/delivery/05_implementations/`, `docs/delivery/06_reviews/`

**Delivery Chain**: `20_initiative_intake_v1` → `30_delivery_planning_v1` → `31_task_execution_v1`

## Drift Reconciliation

When code changes occur outside normal workflow or documentation becomes stale:

### Run Documentation Sync

**Command**:
```batch
run-40_documentation_sync_v1.bat
```

**What it does**:
- Scans repository for changes
- Updates codebase inventory
- Syncs module documentation
- Syncs component documentation
- Validates documentation

**Duration**: ~20-40 minutes
**Output**: Updated `docs/codebase/`

**Drift Recovery Path**: `40_documentation_sync_v1`

**When to run**:
- After significant code changes outside workflow
- When documentation appears stale
- After manual code edits
- Weekly maintenance

## Governance Refresh

After bootstrap drift or contract changes:

### Re-run Master Docs Bootstrap

**Command**:
```batch
run-00_master_docs_bootstrap_v1.bat
```

**What it does**:
- Refreshes system documentation
- Updates architecture documents
- Reconciles with current codebase

**When to run**:
- After major architectural changes
- When system docs become stale
- After workflow system updates

### Re-run Execution Scaffold

**Command**:
```batch
run-10_execution_scaffold_v1.bat
```

**What it does**:
- Refreshes delivery SOPs and templates
- Updates agent contracts

**When to run**:
- After changing delivery process
- When templates need updates
- After agent role changes

## Architecture Communication

Publishing browsable HTML documentation for stakeholders:

### Run Architecture Site

**Command**:
```batch
run-50_architecture_site_v1.bat
```

**What it does**:
- Generates stakeholder HTML view
- Generates developer HTML view
- Validates generated sites

**Duration**: ~15-30 minutes
**Output**: HTML site in `docs/architecture-site/`

**Architecture Communication Phase**: `50_architecture_site_v1`

**When to run**:
- After system docs are updated
- Before stakeholder presentations
- For onboarding new team members

## Batch Files

All workflows have launcher batch files:

| Batch File | Purpose |
|------------|---------|
| `run-00_master_docs_bootstrap_v1.bat` | First-time bootstrap |
| `run-10_execution_scaffold_v1.bat` | Governance scaffold |
| `run-20_initiative_intake_v1.bat` | Initiative capture |
| `run-21_bug_fix_intake_v1.bat` | Bug fix workflow |
| `run-30_delivery_planning_v1.bat` | Plan generation |
| `run-31_task_execution_v1.bat` | Task execution |
| `run-40_documentation_sync_v1.bat` | Drift reconciliation |
| `run-50_architecture_site_v1.bat` | HTML site generation |

### Batch File Pattern

All batch files follow this pattern:
```batch
@echo off
setlocal enabledelayedexpansion
cd /d "D:\MyProjectSpace\01_Workflows\agent-runner-v2"
call .venv\Scripts\activate.bat
ukbe-run-agent run <workflow> --initiative-id "%%1" %*
```

## Notes

### Workflow Families

The repository defines 21 workflow families with 290+ steps:

| Workflow | Steps | Purpose |
|----------|-------|---------|
| `00_master_docs_bootstrap_v1` | 13 | System documentation bootstrap |
| `10_execution_scaffold_v1` | 13 | Delivery governance scaffold |
| `20_initiative_intake_v1` | 5 | Initiative capture |
| `21_bug_fix_intake_v1` | 7 | Bug triage and fix |
| `30_delivery_planning_v1` | 10 | Plan generation |
| `31_task_execution_v1` | 12 | Task execution |
| `40_documentation_sync_v1` | 5 | Doc reconciliation |
| `50_architecture_site_v1` | 2 | HTML site generation |
| `41_*_doc_v1` | 4 each | Audience-specific docs |
| `51-55_*_docs_v1` | 1-4 each | Site generation workflows |
| Media workflows | 3-10 | Image/video pipelines |

### Bootstrap vs Runtime

**Important**: Changes to bootstrap files only take effect after syncing to runtime:

```
Repo bootstrap → %USERPROFILE%\.ukbe-runner\workflows\default\ → Runtime
```

**Sync commands**:
```batch
ukbe-run-agent init --force
# Or
run-bootstrap-publish.bat
```

### Review/Refine Loops

Most workflows include review steps:
1. Generate artifact
2. Review produces REVIEW_FILE_SUGGESTED
3. If rejected → refine with `edit_mode: in_place`
4. Loop back to review
5. Max iterations enforced

### Approval Gates

Steps can require human approval:
- Status becomes `WAITING_FOR_HUMAN_APPROVAL`
- Notification sent
- Approve via: `ukbe-run-agent approve-step <job> <step>`

### Generated Document Protection

Workflow-generated documents have:
```yaml
managed_by: workflow-generated
```

**Do not edit these files directly**. Update the source prompts instead.

### Running Workflows After Drift

When code has changed outside workflow:

1. **Update codebase docs**: `run-40_documentation_sync_v1.bat`
2. **Run initiative workflow**: `run-20_initiative_intake_v1.bat`
3. **Continue normal chain**: Planning → Execution

### Emergency Procedures

**Reset stuck job**:
```batch
run-reset-step.bat <workflow> <step> <job_id>
```

**Clean generated docs**:
```batch
run-cleanup-generated-docs.bat
```

**Approve stuck step**:
```batch
run-approve-step.bat <job_id> <step_id>
```

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04_generate_architecture_docs` on 2026-07-10T09:52:38+08:00*
