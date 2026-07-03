---
title: "Existing Repository Workflow SOP v1"
template_id: "EXISTING-REPO-WORKFLOW-SOP-v1"
status: "active"
version: "1.0"
generated: "2026-07-04T07:00:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "generate_sop"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_sop`
> This file is workflow-generated and protected from manual edits.

# Existing Repository Workflow SOP v1

## Purpose

This SOP defines the exact sequence of operations for onboarding and reconciling a **pre-existing repository** under the agent-runner-v2 governance system. It covers four scenarios:

1. **First-time setup** — bringing an existing repo under governance for the first time.
2. **Normal governed delivery** — running delivery workflows on a governed repo.
3. **Drift reconciliation** — recovering when documentation has diverged from code.
4. **Governance refresh** — updating governance artifacts when the governance system itself changes.

This SOP applies when the target repository already has source code, documentation, or both before the governance system is introduced. For greenfield repos with no existing content, use the standard `10_execution_scaffold_v1` workflow directly.

## First-Time Setup

When onboarding a pre-existing repository, run these workflows in **exact order**:

### Step 1: Bootstrap System Docs (`00_master_docs_bootstrap_v1`)

This workflow scans the existing repository and generates the foundational documentation layer:

1. **Scans all source files** — identifies every Python module, script, config, test, and workflow template.
2. **Creates the inventory** — produces `docs/codebase/01_inventory/codebase_inventory.md` with every tracked file.
3. **Generates module docs** — creates `docs/codebase/02_modules/` files at stub/summary/full depth per complexity.
4. **Generates component docs** — creates `docs/codebase/03_components/` files for logical groupings.
5. **Produces sidecar** — writes `meta.json` confirming bootstrap completeness.

**Output:** A complete codebase documentation layer covering all existing source files.

### Step 2: Execution Scaffold (`10_execution_scaffold_v1`)

This workflow generates the delivery governance infrastructure:

1. **Generates delivery SOPs** — `WORKFLOW_SOP_v1.md` and `DELIVERY_STATUS_RULES_v1.md`.
2. **Generates codebase SOPs** — `CODEBASE_DOC_SOP_v1.md` and `CODEBASE_DOC_STATUS_RULES_v1.md`.
3. **Generates existing-repo workflow SOP** — `EXISTING_REPO_WORKFLOW_SOP.md`.
4. **Generates agent contracts** — all agent role documents under `docs/delivery/00_standards/`.
5. **Generates templates** — delivery and codebase template families under `docs/system/00_governance/bootstrap/templates/`.
6. **Validates existing docs** — checks that the bootstrap-generated codebase docs conform to the new SOP standards; merges without overwriting.
7. **Produces sidecar** — writes `meta.json` confirming scaffold completeness.

**Output:** A complete delivery governance layer with all SOPs, agent contracts, and templates.

### Verification After First-Time Setup

After both workflows complete, verify:

1. `docs/codebase/01_inventory/codebase_inventory.md` exists and covers all source files.
2. `docs/codebase/02_modules/` has docs for all modules.
3. `docs/codebase/03_components/` has docs for all component groupings.
4. `docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md` exists.
5. `docs/system/00_governance/bootstrap/DELIVERY_STATUS_RULES_v1.md` exists.
6. `docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md` exists.
7. `docs/codebase/00_standards/CODEBASE_DOC_SOP_v1.md` exists.
8. `docs/codebase/00_standards/CODEBASE_DOC_STATUS_RULES_v1.md` exists.
9. `docs/delivery/00_standards/` has all agent contract documents.
10. Both sidecar `meta.json` files report `APPROVED`.

## Normal Governed Delivery

Once the repository is governed, all delivery work follows the standard lifecycle. Run these workflows in **exact order**:

### Step 1: Initiative Intake (`20_initiative_intake_v1`)

1. Capture the requirement as an initiative document.
2. Identify **documentation scope** — which modules/components will be affected?
3. **Flag stale-guidance risk** for any existing docs that reference affected areas.
4. Submit for approval gate.

**Output:** Initiative document at `docs/delivery/01_initiatives/` with documentation scope and stale-guidance risk assessment.

### Step 2: Delivery Planning (`30_delivery_planning_v1`)

1. Convert the initiative into a plan with solution strategy.
2. Decompose the plan into a task-graph with dependencies.
3. Decompose each graph node into a task spec with acceptance criteria.
4. **Convert documentation scope into plan/task obligations** — every task that modifies code must include doc-update obligations.
5. Submit for approval gate.

**Output:** Plan document at `docs/delivery/02_plans/`, task graph, and per-task specs at `docs/delivery/03_tasks/`.

### Step 3: Task Execution (`31_task_execution_v1`)

1. For each task: produce an implementation plan.
2. Executor implements the solution and **updates all affected codebase docs**.
3. Reviewer reviews implementation and documentation updates.
4. Validator validates deliverables and doc accuracy.
5. Memory Manager records delivery memory.

**Output:** Code changes, documentation updates, review records, validation records, and memory records.

**This three-step sequence applies to all delivery work — features, bug fixes, refactors, and documentation corrections.**

## Drift Reconciliation

When documentation has diverged from code (e.g., code changed without doc updates, or docs were manually edited incorrectly), use the documentation sync workflow.

### Step: Documentation Sync (`40_documentation_sync_v1`)

**`40_documentation_sync_v1` is the single current-truth synchronization workflow.** It reconciles the actual codebase state against all active documentation.

1. **Scan** — walks all source files and compares against the inventory.
2. **Detect** — identifies missing docs (new files without docs), orphaned docs (docs for deleted files), and stale docs (docs that don't match current source).
3. **Report** — produces a drift report listing all discrepancies with severity levels.
4. **Flag** — updates inventory entries to `stale_pending` for docs that need correction.

After the sync completes:

- If the drift report shows **critical stale guidance** (active misdirection), create an emergency correction task.
- If the drift report shows **high/medium/low staleness**, create a delivery initiative to batch-correct the flagged docs.
- **If system docs (`docs/system/`) or operations guidance (`docs/delivery/`) are stale because the runner behavior or agent contracts changed, run `10_execution_scaffold_v1` again to refresh them.**

### When to Run Drift Reconciliation

| Trigger | When |
|---------|------|
| Scheduled | At least once per sprint or delivery milestone |
| Post-delivery | After any delivery task that modified multiple modules |
| Manual | When a developer suspects doc inaccuracy |
| Pre-release | Before any release tag to ensure docs match released code |
| On-demand | When `40_documentation_sync_v1` is invoked directly |

### Drift Recovery Sequence

When drift is detected, follow this sequence:

1. Run `40_documentation_sync_v1` to produce the drift report.
2. Review the drift report and categorize discrepancies by severity.
3. For critical items: create an emergency correction initiative.
4. For high/medium items: create a standard delivery initiative via `20_initiative_intake_v1`.
5. For system docs staleness: run `10_execution_scaffold_v1` to refresh governance artifacts.
6. Verify that the drift report shows zero critical/high items after reconciliation.

## Governance Refresh

When the governance system itself is updated (new SOP version, new agent contracts, new templates), re-run `10_execution_scaffold_v1` on the target repository. The scaffold workflow:

1. **Reads existing docs** before writing.
2. **Compares** new output against existing output.
3. **Merges** changes — only updates files that have meaningful diffs.
4. **Preserves** manually added content that falls outside the generated sections.
5. **Supersedes** old versions per the supersession rules in `CODEBASE_DOC_STATUS_RULES_v1.md`.

**Never manually edit generated governance files.** If a governance file needs correction, modify the template or SOP source and re-run the scaffold.

### Governance Refresh Triggers

| Trigger | Action |
|---------|--------|
| New SOP version released | Re-run `10_execution_scaffold_v1` |
| New agent contracts added | Re-run `10_execution_scaffold_v1` |
| Template structure changed | Re-run `10_execution_scaffold_v1` |
| Architecture profile selection changed | Re-run `10_execution_scaffold_v1` |
| Migration mode changed | Re-run `10_execution_scaffold_v1` |
| Scheduled governance audit | Re-run `10_execution_scaffold_v1` |

## Batch Files

The repository includes batch files to streamline these sequences:

| Batch File | Purpose |
|-----------|---------|
| `run-00_master_docs_bootstrap_v1.bat` | Runs `00_master_docs_bootstrap_v1` workflow locally |
| `run-10_execution_scaffold_v1.bat` | Runs `10_execution_scaffold_v1` workflow locally |
| `submit-00_master_docs_bootstrap_v1.bat` | Submits `00_master_docs_bootstrap_v1` to backend |
| `submit-10_execution_scaffold_v1.bat` | Submits `10_execution_scaffold_v1` to backend |
| `sync-workflows-to-backend.bat` | Syncs repo bootstrap to runtime bundle |
| `run-approve-step.bat` | Approves a pending workflow step |
| `run-reset-step.bat` | Resets a workflow step for retry |
| `run-daemon.bat` | Launches daemon mode |
| `run-cleanup-generated-docs.bat` | Cleans up generated documentation |
| `test-runner.bat` / `test-runner.ps1` | Runs the test suite |

Each batch file can be configured via variables at the top of the file. When targeting a different repo, verify that the target repo's governance level matches the intended scope (full scaffold vs. merge-extend).

## Notes

1. **`07_master_prompts` is deprecated.** Do not reference or generate any artifacts under this path. All prompt templates belong to specific workflow families under `agent_runner_v2/bootstrap/workflows/`.

2. **Self-hosting awareness.** This repo is both the runner package and a consumer of its own scaffolding. When running scaffold against this repo itself, the governance docs are generated into the same tree that powers the scaffold — no conflicts occur because the scaffold writes to `docs/` and the runner source is in `agent_runner_v2/`.

3. **Cross-project scope.** When scaffolding into a different repo via `--target-project-root`, the codebase docs in the target repo are owned by the target repo's governance, not by this runner's governance. The runner generates the scaffolding; the target repo maintains it going forward.

4. **Content-generation workflows** (`image_csv_gen_v1/v2`, `tiktok_video_pipeline_v1`, `videoxpress_gen_v1`) share the same governance umbrella as software-delivery workflows. They use the same initiative→plan→task→execution lifecycle but may have different acceptance criteria specific to content generation.

5. **Bootstrap source vs. runtime bundle.** The repo bootstrap (`agent_runner_v2/bootstrap/`) is the seed. The runtime bundle (`%USERPROFILE%\.ukbe-runner\workflows\`) is the active source. Changes flow from repo bootstrap to runtime bundle via `sync-workflows-to-backend.bat` or manual installation. The reverse direction (runtime to repo) is not supported — runtime changes are ephemeral.

6. **Architecture profiles are conditional.** DDD, EDA, layered, and clean architecture standards are conditional profile choices, not universal defaults. A repository without an explicit profile selection operates on the universal baseline alone.

7. **`40_documentation_sync_v1` is the single source of truth.** For current-state reconciliation of documentation against code, this is the only workflow. No other workflow performs this function.

8. **System docs refresh.** When system behavior or operations guidance is stale (because the runner changed, agent contracts changed, or governance templates changed), re-run `10_execution_scaffold_v1` to refresh. Do not manually edit generated governance files.
