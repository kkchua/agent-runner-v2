---
template_id: "SYS-03-ERWS"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:22:07+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# Existing Repo Workflow SOP: agent-runner-v2

## Purpose

This Standard Operating Procedure (SOP) defines the onboarding, reconciliation, and governance workflow sequence for repositories using `agent-runner-v2`. It establishes the order of operations for maintaining documentation governance and handling drift between code and documentation.

## First-Time Setup

### Prerequisites

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kkchua/agent-runner-v2.git
   cd agent-runner-v2
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -e .
   ```

3. **Configure environment**:
   ```bash
   copy .env.example .env
   # Edit .env with Pushover credentials (optional)
   ```

### Initial Bootstrap Sequence

Run bootstrap workflows in order:

1. **Initialize job state**:
   ```bash
   run-init.bat
   ```
   This creates the initial job directory structure.

2. **Run Layer 1 Governance Bootstrap**:
   ```bash
   run-00_layer1_governance_bootstrap_v1.bat
   ```
   This generates ecosystem governance under `docs/system/00_governance/bootstrap/`.

3. **Run Repo Master Docs Bootstrap**:
   ```bash
   run-00_repo_master_docs_bootstrap_v1.bat
   ```
   This generates repo master docs under `docs/repo/governance/`.

### Verification

After bootstrap completion:

1. Verify `docs/system/00_governance/bootstrap/` contains governance docs
2. Verify `docs/repo/governance/` contains master docs
3. Verify `docs/repo/codebase/` contains codebase inventory

## Normal Governed Delivery

### Workflow Sequence

For ongoing development with governance:

1. **Make code changes** in feature branch
2. **Re-run codebase scan** if structural changes:
   ```bash
   run-00_repo_master_docs_bootstrap_v1.bat
   ```
3. **Review generated changes** in `docs/repo/codebase/`
4. **Commit documentation updates** alongside code changes
5. **Merge to main branch** after approval

### Documentation Review Gates

Before merging:

1. Check codebase inventory reflects current modules
2. Check change impact document describes modifications
3. Check governance docs are consistent with changes

## Drift Reconciliation

### Detecting Drift

Documentation drift occurs when:
- Code changes without corresponding documentation updates
- New modules are added without codebase inventory update
- Architecture changes are not reflected in governance docs

To detect drift:
```bash
run-00_repo_master_docs_bootstrap_v1.bat
```

The workflow will:
1. Scan repository for current state
2. Compare with existing documentation
3. Generate updated documentation
4. Report changes in bootstrap change log

### Reconciling Drift

When drift is detected:

1. **Review change log**: `docs/repo/governance/*-bootstrap-change-log.md`
2. **Verify changes**: Compare generated docs with previous versions
3. **Commit updates**: Add updated documentation to branch
4. **Run governance refresh**: Re-run Layer 1 if governance changes needed

## Governance Refresh

### Layer 1 Refresh

When ecosystem governance needs refresh:

```bash
run-00_layer1_governance_bootstrap_v1.bat
```

This regenerates:
- `DOCUMENTATION_STANDARD.md`
- `BUNDLE_TAXONOMY.md`
- `RUNTIME_GOVERNANCE.md`
- Agent instructions (AGENTS.md, CLAUDE.md, QWEN.md)

### Layer 2 Refresh

When repo master docs need refresh:

```bash
run-00_repo_master_docs_bootstrap_v1.bat
```

This regenerates:
- `SYSTEM_CONTEXT.md`
- `COMPONENT_ARCHITECTURE.md`
- `DECISION_LOG.md`
- `SYSTEM_FILE_STRUCTURE.md`
- `DEVELOPER_GUIDE.md`
- `RUNBOOK.md`
- This document (`EXISTING_REPO_WORKFLOW_SOP.md`)

### Full Governance Refresh

To refresh all governance:

```bash
run-init.bat
run-00_layer1_governance_bootstrap_v1.bat
run-00_repo_master_docs_bootstrap_v1.bat
```

## Batch Files

### Active Batch Files

| Batch File | Purpose | Status |
|------------|---------|--------|
| `run-init.bat` | Initialize new job | Active |
| `run-00_layer1_governance_bootstrap_v1.bat` | Run Layer 1 governance bootstrap | Active |
| `run-00_repo_master_docs_bootstrap_v1.bat` | Run repo master docs bootstrap | Active |
| `run-00_bootstrap_lifecycle_admin_v1.bat` | Run bootstrap lifecycle admin | Active |
| `run-bootstrap-publish.bat` | Publish bootstrap bundles | Active |
| `run-daemon.bat` | Start daemon worker | Active |
| `run-approve-step.bat` | Approve current step | Active |
| `run-reset-step.bat` | Reset step for retry | Active |
| `run-cleanup-workflow.bat` | Cleanup workflow artifacts | Active |
| `submit-00_bootstrap_lifecycle_admin_v1.bat` | Submit bootstrap lifecycle job | Active |
| `submit-00_layer1_governance_bootstrap_v1.bat` | Submit Layer 1 governance job | Active |
| `submit-00_repo_master_docs_bootstrap_v1.bat` | Submit master docs job | Active |
| `sync-workflows-to-backend.bat` | Sync workflow packages | Active |

### Archived Batch Files

**None currently present.** The repository does not have an `archive/` directory with legacy batch files.

### Pending Restoration

The following workflow families are documented in migration plans but are **not currently operational**:

| Workflow Family | Status | Notes |
|-----------------|--------|-------|
| `10_execution_scaffold_v2` | Pending restoration | Previously in `archive/workflows/` |
| `20_initiative_intake_v1` | Pending restoration | Previously in `archive/workflows/` |
| `30_delivery_planning_v1` | Pending restoration | Previously in `archive/workflows/` |
| `31_task_execution_v1` | Pending restoration | Previously in `archive/workflows/` |
| `40_documentation_sync_v1` | Pending restoration | Previously in `archive/workflows/` |
| `50_architecture_site_v1` | Pending restoration | Previously in `archive/workflows/` |

These workflows are targeted for restoration as part of the AI-Driven SDLC migration plan (see `docs/system/03_ai_driven_sdlc_migration_plan.md`).

## Notes

### Layer Dependency Chain

Bootstrap workflows must run in order:

```
Layer 1 (00_layer1_governance_bootstrap_v1)
    ↓ required
Layer 2 (00_repo_master_docs_bootstrap_v1)
    ↓ required
Layer 3+ (SDLC workflows - pending)
```

**Important**: Layer 3+ workflows cannot run until Layer 2 is complete.

### Zero Source Mutation

Bootstrap workflows are designed to generate documentation only. They must not:
- Modify source code files
- Delete existing documentation without explicit approval
- Change repository configuration

### Documentation Authority

The authoritative sources for documentation structure are:
- `DOCUMENTATION_STANDARD.md` (Layer 1)
- This document (Layer 2)

Manual edits to workflow-generated documentation may be overwritten on next bootstrap run.

### Change Log Pattern

Each bootstrap run produces a change log:
- Location: `docs/repo/governance/<job-id>-bootstrap-change-log.md`
- Purpose: Summary of refreshed documents and key findings
- Retention: Until next bootstrap run

### Testing Before Bootstrap

Before running bootstrap in production:

```bash
pytest tests/unit/
pytest tests/integration/
```

Ensure all tests pass before modifying governance documentation.