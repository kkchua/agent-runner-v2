---
doc_type: "masterplan"
authority: "human-authored"
scan_policy: "exclude"
scan_reason: "implementation plan for sdlc_00_codebase_v1 workflow; exclude from operational scans"
---

# sdlc_00_codebase_v1 Implementation Plan

## Status

**Draft** — Implementation plan for the codebase sync maintenance workflow.

## Purpose

Implement the `sdlc_00_codebase_v1` workflow — a Layer 3 maintenance workflow
that periodically syncs repository code to `docs/repo/codebase/` documentation.

This workflow follows the **L2 platform staging pattern** (same as
`sdlc_00_delivery_scaffold_v1`): outputs are staged in a run-scoped folder,
reviewed, approved by a human, then published to a stable `current/` folder.
Previous versions are archived to `history/`.

This workflow is **not** part of the initiative flow (sdlc_10 through sdlc_80).
It is a standalone maintenance workflow.

## Workflow Identity

| Field | Value |
|-------|-------|
| Workflow name | `sdlc_00_codebase_v1` |
| Layer | Layer 3 |
| Platform | agent-runner-v2 |
| Job prefix | `SDLC00CB` |
| Class | Maintenance workflow |
| Human approval | Yes (before publish) |
| Publish step | Yes (copies staged docs to `current/`) |

## Relationship to codebase-init CLI

`ukbe-run-agent codebase-init` is a one-time CLI command that creates the
initial `docs/repo/codebase/` directory structure and seed files. It is not
a workflow and has no review/refine loop.

`sdlc_00_codebase_v1` is the **periodic maintenance** counterpart — it
re-scans the repository and updates codebase docs when code changes. It
includes staging, review, human approval, and publish steps.

Expected usage:
1. Run `codebase-init` once to set up the directory structure
2. Run `sdlc_00_codebase_v1` periodically to keep docs in sync

## Output Folder Structure

Following the L2 platform staging pattern under `docs/repo/codebase/`:

```
docs/repo/codebase/
├── runs/<job_id>/              ← staged (draft) artifacts during a run
│   ├── 01_inventory/           ← synced codebase inventory
│   ├── 02_modules/             ← synced module docs
│   ├── 03_components/          ← synced component docs
│   ├── 04_changes/             ← change impact + validation
│   └── sync_logs/              ← sync log + review evidence
│
├── current/                    ← active published codebase docs (stable)
│   ├── 01_inventory/
│   ├── 02_modules/
│   ├── 03_components/
│   └── codebase_manifest.json  ← publish manifest
│
├── history/<job_id>/           ← archived published snapshots
│   └── codebase_manifest.json
│
└── backups/BACKUP-<timestamp>/ ← pre-sync backup (optional)
```

The `current/` folder is what other workflows (sdlc_10 through sdlc_80)
read as their codebase context. It always contains the last approved version.

## Step Model

```
create_backup (action)
    -> sync_codebase_docs (action)         <- writes to runs/<job_id>/
    -> generate_sync_log (action)
    -> review_sync_log (prompt)            <- human approval gate
    -> [on reject] refine_codebase_docs (prompt) -> loop back to review
    -> validate_codebase_docs (action)
    -> publish_codebase_docs (action)      <- copies runs/ to current/, archives old current/ to history/
    -> commit_changes (action)
    -> stepCompletion (action)
```

### Step Details

| # | Step Name | Type | Action/Prompt | Produces | Description |
|---|-----------|------|---------------|----------|-------------|
| 1 | `create_backup` | action | `create_backup` | `CODEBASE_BACKUP` | Backup current codebase docs to `backups/BACKUP-{timestamp}/` |
| 2 | `sync_codebase_docs` | action | `sync_codebase_docs` | `CODEBASE_CHANGE_IMPACT`, `CODEBASE_INVENTORY` | Scan repo and sync all codebase docs to `runs/<job_id>/` staging area |
| 3 | `generate_sync_log` | action | `generate_sync_log` | `SYNC_LOG` | Generate sync report documenting all changes |
| 4 | `review_sync_log` | prompt | `prompts/04_review_sync_log.txt` | `REVIEW_FILE_SUGGESTED` | Review sync log and staged codebase docs for errors |
| 5 | `refine_codebase_docs` | prompt | `prompts/05_refine_codebase_docs.txt` | `CODEBASE_INVENTORY` | Refine staged codebase docs based on review findings |
| 6 | `validate_codebase_docs` | action | `validate_codebase_docs` | `VALIDATION_FILE` | Deterministic validation of staged codebase doc structure |
| 7 | `publish_codebase_docs` | action | `publish_codebase_docs` | `CODEBASE_PUBLISH_MANIFEST`, `CODEBASE_PUBLISH_MANIFEST_HISTORY` | Archive old `current/` to `history/`, copy staged docs to `current/` |
| 8 | `commit_changes` | action | `commit_changes` | — | Commit all codebase doc changes to git |
| 9 | `stepCompletion` | action | `step_completion` | — | Finalize workflow |

### Human Approval Gate

Step 4 (`review_sync_log`) has `requires_human_approval_after = true`.
The human reviews the sync log and staged docs before approving publish.

### Refinement Loop

- Review step has `on_reject_refine` pointing to `refine_codebase_docs`
- Max iterations: 2
- Exhausted failure code: `CODEBASE_SYNC_REFINEMENT_EXHAUSTED`
- Refine step uses `loop_returns_to = "review_sync_log"`

## Files to Create

### 1. `workflows/sdlc_00_codebase_v1/workflow.toml`

Step definitions, routing, coder roles, artifact contracts.

Key design decisions:
- `init_step = "create_backup"`
- `default_max_rejects = 2`
- `requires_human_approval_after = true` on review step (before publish)
- Review step uses `reviewer_standard` role policy
- Refine step uses `architect_standard` role policy
- Publish step uses new `publish_codebase_docs` action

### 2. `workflows/sdlc_00_codebase_v1/bundle_governance.toml`

Canonical artifact registry declaring all artifact keys:

| Key | Path Template | Required |
|-----|---------------|----------|
| `CODEBASE_BACKUP` | `docs/repo/codebase/backups/BACKUP-<job_id>/` | false |
| `CODEBASE_CHANGE_IMPACT` | `docs/repo/codebase/runs/<job_id>/04_changes/<job_id>-reconcile.md` | true |
| `CODEBASE_INVENTORY` | `docs/repo/codebase/runs/<job_id>/01_inventory/codebase_inventory.md` | true |
| `SYNC_LOG` | `docs/repo/codebase/runs/<job_id>/sync_logs/SYNC-<job_id>.md` | false |
| `REVIEW_FILE_SUGGESTED` | `docs/repo/codebase/runs/<job_id>/sync_logs/<job_id>-review.md` | false |
| `VALIDATION_FILE` | `docs/repo/codebase/runs/<job_id>/04_changes/<job_id>-reconcile-validation.md` | false |
| `CODEBASE_PUBLISH_MANIFEST` | `docs/repo/codebase/current/codebase_manifest.json` | false |
| `CODEBASE_PUBLISH_MANIFEST_HISTORY` | `docs/repo/codebase/history/<job_id>/codebase_manifest.json` | false |

### 3. `workflows/sdlc_00_codebase_v1/context_extensions.py`

`WorkflowExtensions` subclass implementing:
- `register_artifact_keys()` — artifact key to relative-path mappings
- `build_context_extensions()` — resolve absolute paths for prompt context

Key context variables:
- `CODEBASE_DOC_ROOT` — project-local codebase root (`docs/repo/codebase/`)
- `CODEBASE_CURRENT_ROOT` — `docs/repo/codebase/current/`
- `CODEBASE_HISTORY_ROOT` — `docs/repo/codebase/history/<job_id>/`
- All artifact keys resolved to absolute paths

### 4. `workflows/sdlc_00_codebase_v1/prompts/04_review_sync_log.txt`

Review prompt for the sync log and codebase documentation. Must:
- Read the sync log at `{SYNC_LOG}`
- Read the codebase inventory at `{CODEBASE_INVENTORY}`
- Read the change impact at `{CODEBASE_CHANGE_IMPACT}`
- Check for unexpected changes, missing docs, structural issues
- Produce review output at `{REVIEW_FILE_SUGGESTED}`
- Pass or reject with explicit findings

### 5. `workflows/sdlc_00_codebase_v1/prompts/05_refine_codebase_docs.txt`

Refine prompt for fixing codebase docs after review findings. Must:
- Read the review at `{REVIEW_FILE_SUGGESTED}`
- Read current codebase docs
- Fix identified issues in-place
- Preserve Layer 2 boundaries and codebase doc standards

## Existing Code to Reuse

| Action | Location | Used By Step |
|--------|----------|-------------|
| `create_backup` | `agent_runner_v2/actions/sdlc_shared_actions.py` | Step 1 |
| `sync_codebase_docs` | `agent_runner_v2/actions/sync_codebase_docs.py` | Step 2 |
| `generate_sync_log` | `agent_runner_v2/actions/sdlc_shared_actions.py` | Step 3 |
| `validate_codebase_docs` | `agent_runner_v2/actions/validate_codebase_docs.py` | Step 6 |
| `commit_changes` | `agent_runner_v2/actions/sdlc_shared_actions.py` | Step 8 |

## New Code Required

### `publish_codebase_docs` action (Step 7)

A new action following the same pattern as `publish_sdlc_scaffold`
(in `sdlc_00_delivery_scaffold_v1/actions.py`):

1. Archive current `docs/repo/codebase/current/` to `docs/repo/codebase/history/<job_id>/`
2. Copy staged docs from `docs/repo/codebase/runs/<job_id>/` to `docs/repo/codebase/current/`
3. Write `codebase_manifest.json` to `current/` with run metadata
4. Write historical manifest to `history/<job_id>/`

This action can live in the workflow's local `actions.py` or in
`sdlc_shared_actions.py` if it should be reusable.

### `sync_codebase_docs` modification (Step 2)

The existing `sync_codebase_docs` action currently writes directly to
`docs/repo/codebase/01_inventory/`, `02_modules/`, etc. It needs to
support a configurable staging root so it writes to
`docs/repo/codebase/runs/<job_id>/` instead.

Options:
- Add a `staging_root` parameter to `step_cfg` that overrides the default
  output base path
- Or create a thin wrapper action that delegates to `sync_codebase_docs`
  with the staging root

## Batch Files

### `run-sdlc_00_codebase_v1.bat` / `.sh`

Standard run batch file following the existing pattern:
- Activate `.venv`
- Invoke `ukbe-run-agent run --template-group sdlc_00_codebase_v1`

### `submit-sdlc_00_codebase_v1.bat` / `.sh`

Standard submit batch file for daemon mode:
- Activate `.venv`
- Invoke `ukbe-run-agent submit --template-group sdlc_00_codebase_v1`

## Implementation Sequence

1. Create `workflows/sdlc_00_codebase_v1/` directory
2. Write `workflow.toml` with all step definitions
3. Write `bundle_governance.toml` with artifact registry
4. Write `context_extensions.py` with `WorkflowExtensions` subclass
5. Write `prompts/04_review_sync_log.txt`
6. Write `prompts/05_refine_codebase_docs.txt`
7. Write `actions.py` with `publish_codebase_docs` action
8. Modify `sync_codebase_docs` to support staging root (or create wrapper)
9. Write `run-sdlc_00_codebase_v1.bat` and `run-sdlc_00_codebase_v1.sh`
10. Write `submit-sdlc_00_codebase_v1.bat` and `submit-sdlc_00_codebase_v1.sh`

## Verification

1. **Structural validation:** Run `ukbe-run-agent sync-workflows sdlc_00_codebase_v1`
   to verify the workflow bundle validates and syncs to backend.

2. **Unit tests:** Verify existing action tests still pass:
   ```
   .venv\Scripts\python -m pytest tests/unit/ -v -k "codebase or backup or sync_log or commit"
   ```

3. **Manual dry run (optional):** Run the workflow in manual mode against
   the current repo to verify end-to-end behavior:
   ```
   .venv\Scripts\python -m agent_runner_v2.run_agent run --template-group sdlc_00_codebase_v1 --mode manual
   ```

## Non-Goals

- This workflow does NOT modify source code
- This workflow does NOT participate in the initiative flow (sdlc_10 through sdlc_80)
- This workflow does NOT replace `codebase-init` CLI command (that is one-time setup)
