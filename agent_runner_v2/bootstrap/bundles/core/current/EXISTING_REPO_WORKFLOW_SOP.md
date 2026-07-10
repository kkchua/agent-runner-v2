---
title: "Existing Repository Workflow SOP"
change_id: "00DOC-20260710-15f76235"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
managed_by: workflow-generated
generated: "2026-07-10T11:57:31+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Existing Repository Workflow SOP

## Purpose

This SOP defines the standard operating procedure for onboarding existing repositories to the agent-runner-v2 governed delivery model. It covers the complete lifecycle from first-time setup through normal delivery, drift reconciliation, and governance refresh.

**Scope**: Any repository with existing code that needs structured workflow governance.

**Prerequisites**: Agent-runner-v2 installed and `ukbe-run-agent` CLI available.

## First-Time Setup

The first-time setup establishes documentation governance for an existing repository through a two-phase bootstrap process.

### Phase 1: Master Documentation Bootstrap (`00_master_docs_bootstrap_v1`)

**Purpose**: Generate master system documentation for the repository.

**When to run**:
- New repository onboarding
- Major structural changes
- Documentation governance initialization

**Command**:
```bash
run-00_master_docs_bootstrap_v1.bat
```

**What it does**:
1. **Step 01**: `scan_repo_codebase` - Generate codebase inventory
2. **Step 02**: `generate_project_analysis` - Analyze repository structure
3. **Step 03**: `generate_system_overview_docs` - Create overview documents
4. **Step 04**: `generate_architecture_docs` - Create architecture documents (this step)
5. **Step 05**: `review_master_system_docs` - Review generated docs
6. **Step 06**: `refine_master_system_docs` - Refine based on review

**Outputs**:
- `docs/system/00_governance/bootstrap/` - Master system documentation
- `docs/codebase/01_inventory/codebase_inventory.md` - Codebase inventory
- `docs/codebase/02_modules/*.md` - Module documentation
- `docs/codebase/03_components/*.md` - Component documentation

**Post-conditions**:
- Master system docs exist and are validated
- Codebase inventory current
- Module and component docs generated

### Phase 2: Execution Scaffold (`10_execution_scaffold_v1`)

**Purpose**: Establish delivery and codebase governance SOPs.

**When to run**: After Phase 1 completes successfully.

**Command**:
```bash
run-10_execution_scaffold_v1.bat
```

**What it does**:
1. **Step 01**: `project_analysis` - Analyze for scaffold needs
2. **Step 02**: `generate_sop` - Generate delivery SOP
3. **Step 03**: `generate_templates` - Generate document templates
4. **Step 04**: `generate_agents` - Generate agent contracts
5. **Steps 05-08**: Review/refine SOP, templates, agents

**Outputs**:
- `docs/delivery/` - Delivery governance documents
- `docs/codebase/00_standards/` - Codebase standards
- Agent contracts in system governance

**Post-conditions**:
- Delivery SOP established
- Document templates available
- Agent contracts defined

### Setup Verification

After both phases complete:

```bash
# Verify system docs exist
ls docs/system/00_governance/bootstrap/

# Verify delivery scaffold exists
ls docs/delivery/
ls docs/codebase/00_standards/

# Run validation
run-40_documentation_sync_v1.bat
```

## Normal Governed Delivery

After first-time setup, normal delivery follows a three-phase workflow chain.

### Phase 1: Initiative Intake (`20_initiative_intake_v1`)

**Purpose**: Capture and refine new work initiatives.

**When to run**: Starting new feature, enhancement, or task.

**Command**:
```bash
run-20_initiative_intake_v1.bat
```

**Workflow**:
1. **Step 01**: `pre_init` - Draft initiative document
2. **Step 02**: `review_pre_init` - Review draft
3. **Step 03**: `refine_pre_init` - Refine based on review

**Outputs**:
- `docs/delivery/01_initiatives/INIT-*.md` - Initiative documents

**Post-conditions**:
- Initiative documented and reviewed
- Ready for planning

### Phase 2: Delivery Planning (`30_delivery_planning_v1`)

**Purpose**: Create plans, task graphs, and task contracts.

**When to run**: After initiative intake completes.

**Command**:
```bash
run-30_delivery_planning_v1.bat
```

**Workflow**:
1. **Step 02**: `planner` - Generate delivery plan
2. **Step 03**: `review_planner` - Review plan
3. **Step 04**: `task_graph` - Generate task graph
4. **Step 05**: `review_task_graph` - Review task graph
5. **Step 06**: `task` - Generate task contracts
6. **Step 07**: `review_task` - Review tasks

**Outputs**:
- `docs/delivery/02_plans/PLAN-*.md` - Delivery plans
- `docs/delivery/02_plans/TASK-GRAPH-*.md` - Task graphs
- `docs/delivery/03_tasks/TASK-*.md` - Task contracts

**Post-conditions**:
- Plan approved
- Task graph defined
- Tasks ready for execution

### Phase 3: Task Execution (`31_task_execution_v1`)

**Purpose**: Execute implementation, review, validation.

**When to run**: For each task from planning phase.

**Command**:
```bash
run-31_task_execution_v1.bat
```

**Workflow**:
1. **Step 08**: `impl_task` - Implementation planning
2. **Step 09**: `review_impl_task` - Review implementation
3. **Step 10**: `executor` - Execute code changes
4. **Step 11**: `validate` - Validate results

**Outputs**:
- `docs/delivery/03_tasks/IMPL-*.md` - Implementation plans
- `docs/delivery/03_tasks/REVIEW-*.md` - Review documents
- `docs/delivery/04_validation/VALIDATION-*.md` - Validation reports

**Post-conditions**:
- Code implemented
- Tests passing
- Documentation updated

## Drift Reconciliation

When code changes occur outside normal workflows, documentation drifts from reality. Drift reconciliation brings documentation back into alignment.

### Documentation Sync (`40_documentation_sync_v1`)

**Purpose**: Reconcile codebase documentation with current repository state.

**When to run**:
- After code changes outside workflow
- After manual edits to code
- Periodic maintenance
- Before architecture site generation

**Command**:
```bash
run-40_documentation_sync_v1.bat
```

**Workflow**:
1. **Step 01**: `sync_docs` - Scan and sync documentation
2. **Step 02**: `review_docs` - Review sync results
3. **Step 03**: `refine_docs` - Refine documentation
4. **Step 04**: `validate_doc_sync` - Validate sync completed

**Outputs**:
- Updated `docs/codebase/01_inventory/codebase_inventory.md`
- Refreshed `docs/codebase/02_modules/*.md`
- Refreshed `docs/codebase/03_components/*.md`
- Change impact document

**Drift Triggers**:
| Change Type | Drift Risk | Action |
|-------------|------------|--------|
| New file added | Inventory | Run sync |
| File deleted | Inventory | Run sync |
| Function signature change | Module doc | Run sync |
| New module | Module + Component | Run sync |
| API change | Multiple docs | Run sync + manual review |

### Recovery from Significant Drift

For significant drift (major refactoring, many changes):

1. **Run documentation sync**:
   ```bash
   run-40_documentation_sync_v1.bat
   ```

2. **Review changes**:
   ```bash
   git diff docs/codebase/
   ```

3. **Commit sync results**:
   ```bash
   git add docs/codebase/
   git commit -m "docs: Sync documentation after code changes"
   ```

## Governance Refresh

Periodically, governance documents themselves need refresh. This includes SOPs, templates, and agent contracts.

### Architecture Site Generation (`50_architecture_site_v1`)

**Purpose**: Generate browsable HTML architecture views.

**When to run**:
- After documentation sync
- Before stakeholder reviews
- Periodic publication

**Command**:
```bash
run-50_architecture_site_v1.bat
```

**Workflow**:
1. **Step 01**: `generate_architecture_site` - Generate HTML site
2. **Step 02**: `validate_architecture_site` - Validate site

**Outputs**:
- `docs/output/architecture_site/` - HTML site
- `stakeholders.html` - Stakeholder view
- `developers.html` - Developer view
- `operators.html` - Operator view
- `testers.html` - Tester view
- `users.html` - User view

**Audience Views**:
| Audience | Focus | Primary Documents |
|----------|-------|-------------------|
| Stakeholders | Business capabilities | SYSTEM_OVERVIEW, BUSINESS_CAPABILITIES |
| Developers | Implementation details | FUNCTIONAL_SPEC, DEVELOPER_GUIDE |
| Operators | Deployment, monitoring | RUNBOOK, NON_FUNCTIONAL_REQUIREMENTS |
| Testers | Validation | FUNCTIONAL_SPEC, test docs |
| Users | Usage | User guides |

### Audience-Specific Documentation

For targeted audience documentation:

```bash
# Developer documentation
run-41_developer_doc_v1.bat

# Operator documentation
run-41_operator_doc_v1.bat

# Stakeholder documentation
run-41_stakeholder_doc_v1.bat

# Tester documentation
run-41_tester_doc_v1.bat

# User documentation
run-41_user_doc_v1.bat
```

### Complete Site Generation

For all audience sites:

```bash
run-51_stakeholder_docs_v1.bat
run-52_developer_docs_v1.bat
run-53_operator_docs_v1.bat
run-54_tester_docs_v1.bat
run-55_user_docs_v1.bat
```

## Batch Files

The following batch files are available for workflow execution:

### Bootstrap Workflows

| Batch File | Purpose | Phase |
|------------|---------|-------|
| `run-00_master_docs_bootstrap_v1.bat` | Generate master system docs | First-time setup |
| `run-10_execution_scaffold_v1.bat` | Scaffold delivery governance | First-time setup |

### Delivery Workflows

| Batch File | Purpose | Chain Position |
|------------|---------|----------------|
| `run-20_initiative_intake_v1.bat` | Initiative intake | Phase 1 |
| `run-21_bug_fix_intake_v1.bat` | Bug fix workflow | Alternative Phase 1 |
| `run-30_delivery_planning_v1.bat` | Delivery planning | Phase 2 |
| `run-31_task_execution_v1.bat` | Task execution | Phase 3 |

### Maintenance Workflows

| Batch File | Purpose | When |
|------------|---------|------|
| `run-40_documentation_sync_v1.bat` | Sync docs | Drift reconciliation |
| `run-41_developer_doc_v1.bat` | Developer docs | Audience-specific |
| `run-41_operator_doc_v1.bat` | Operator docs | Audience-specific |
| `run-41_stakeholder_doc_v1.bat` | Stakeholder docs | Audience-specific |
| `run-41_tester_doc_v1.bat` | Tester docs | Audience-specific |
| `run-41_user_doc_v1.bat` | User docs | Audience-specific |
| `run-50_architecture_site_v1.bat` | Generate site | Governance refresh |
| `run-51_stakeholder_docs_v1.bat` | Stakeholder site | Audience site |
| `run-52_developer_docs_v1.bat` | Developer site | Audience site |
| `run-53_operator_docs_v1.bat` | Operator site | Audience site |
| `run-54_tester_docs_v1.bat` | Tester site | Audience site |
| `run-55_user_docs_v1.bat` | User site | Audience site |

### Utility Scripts

| Batch File | Purpose |
|------------|---------|
| `run-daemon.bat` | Start daemon |
| `run-approve-step.bat` | Approve waiting step |
| `run-reset-step.bat` | Reset step for retry |
| `run-tests.bat` | Run unit tests |
| `run-integration-tests.bat` | Run integration tests |
| `run-all-tests.bat` | Run all tests |
| `run-cleanup-generated-docs.bat` | Clean generated docs |
| `run-bootstrap-publish.bat` | Sync bootstrap to runtime |

### Batch File Template

Each batch file follows this pattern:

```batch
@echo off
setlocal enabledelayedexpansion

REM --- Activate .venv ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

REM --- Configuration ---
set "AGENT_RUNNER_ROOT=<path>"
set "TEMPLATE_GROUP=<workflow_name>"
set "TARGET_PROJECT_ROOT=<path>"
set "JOB_ID="
set "DRY_RUN=false"
set "NEW_JOB=false"

REM --- Execution ---
call "%AGENT_RUNNER_ROOT%\scripts\ukbe-run-delivery.bat" ^
    --project-root "!AGENT_RUNNER_ROOT!" ^
    --template-group "!TEMPLATE_GROUP!" ^
    --target-project-root "!TARGET_PROJECT_ROOT!" !FLAGS!
```

## Notes

### Workflow Chain Summary

**First-Time Setup Chain**:
```
00_master_docs_bootstrap_v1 → 10_execution_scaffold_v1
     ↓                              ↓
Master system docs          Delivery governance
```

**Normal Governed Delivery Chain**:
```
20_initiative_intake_v1 → 30_delivery_planning_v1 → 31_task_execution_v1
        ↓                        ↓                      ↓
   Initiative docs          Plan docs              Code + validation
```

**Drift Recovery Chain**:
```
40_documentation_sync_v1 → 50_architecture_site_v1
         ↓                          ↓
   Updated codebase docs      Published HTML site
```

### Rerunning Workflows

Workflows are idempotent - rerunning produces consistent results:

| Workflow | Rerun Trigger |
|----------|---------------|
| `00_master_docs_bootstrap_v1` | Major structural changes |
| `10_execution_scaffold_v1` | Governance changes |
| `40_documentation_sync_v1` | Code changes |
| `50_architecture_site_v1` | Documentation updates |

### Job ID Management

- Leave `JOB_ID` blank in batch files to auto-create new jobs
- Set `JOB_ID` to resume existing jobs
- Jobs persist in `~/.ukbe-runner/jobs/`

### Dry Run Mode

Set `DRY_RUN=true` to render prompts without invoking LLM:

```batch
set "DRY_RUN=true"
```

### Bootstrap Bundle Changes

After modifying bootstrap templates:

1. Edit files in `agent_runner_v2/bootstrap/workflows/default/`
2. Run `run-bootstrap-publish.bat` or `ukbe-run-agent init`
3. Runtime bundle syncs to `~/.ukbe-runner/workflows/`

### Troubleshooting

| Issue | Check |
|-------|-------|
| Workflow not found | Runtime bundle synced? |
| Job not resuming | Correct JOB_ID? |
| Step failures | Logs in `~/.ukbe-runner/jobs/<wf>/<job>/<step>/logs/` |
| Notification failures | Pushover config in `~/.ukbe-runner/config.json` |
| Backend connection | Engine config in `~/.ukbe-runner/engine/config.json` |

### Support Resources

- **Developer Guide**: `docs/system/00_governance/bootstrap/DEVELOPER_GUIDE.md`
- **Runbook**: `docs/system/00_governance/bootstrap/RUNBOOK.md`
- **Decision Log**: `docs/system/00_governance/bootstrap/DECISION_LOG.md`
