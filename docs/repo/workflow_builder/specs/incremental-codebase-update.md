# Workflow Specification: Incremental Codebase Doc Update

## Overview

**Workflow name:** `update_codebase_docs_v1`
**Label:** Incremental Codebase Doc Update
**Job prefix:** `UCBD`
**Description:** Incrementally updates codebase documentation by regenerating only the docs affected by recent code changes, triggered automatically by a post-commit git hook.

## Purpose

The full codebase scan workflow (`sdlc_00_codebase_v1`) processes all 141+ modules on every run, which is too heavy for frequent updates. Most commits only touch a few files, making a full scan overkill.

**Trigger:** A post-commit git hook submits this workflow to the backend when source code changes are detected.

**Outcome:** Only affected module docs are regenerated, keeping codebase documentation in sync with minimal overhead. The workflow auto-commits the updated docs.

## Workflow Type

**Action-only** — All steps are deterministic operations (git commands, file scanning, doc generation). No LLM involvement.

## Inputs

**LAST_SYNC_COMMIT_FILE** — Tracking file (`.last_sync_commit` in `docs/repo/codebase/current/`) containing the commit hash from the last doc sync. If missing, the workflow should exit with a message telling the user to run `sdlc_00_codebase_v1` first.

## Outputs

| Artifact Key | Description |
|---|---|
| `UPDATED_MODULE_DOCS` | Regenerated module docs in `docs/repo/codebase/current/02_modules/` for affected modules only |
| `UPDATED_INVENTORY` | Updated `codebase_inventory.md` reflecting any new/removed files |
| `UPDATED_CHANGE_IMPACT` | Change impact report for this incremental update |
| `UPDATED_MANIFEST` | Updated `codebase_manifest.json` with new sync commit hash |

## Step Sequence

### Step 1: detect_changes

```
Step: detect_changes
Type: action
Purpose: Read the last sync commit hash from the tracking file. Run git diff to get
  the list of changed files since that commit. Filter to relevant file types
  (*.py, workflow.toml, config files). If no relevant changes, exit early.
On success: → scan_affected_modules
```

### Step 2: scan_affected_modules

```
Step: scan_affected_modules
Type: action
Purpose: Map changed file paths to affected Python module names. Use the existing
  module classification logic from codebase_docs.py to determine which module
  docs need regeneration.
On success: → regenerate_docs
```

### Step 3: regenerate_docs

```
Step: regenerate_docs
Type: action
Purpose: Call codebase_docs.py functions (build_snapshot, render_module_doc,
  render_inventory, render_change_impact) to regenerate only the affected
  module docs, plus update the inventory and generate a change impact report.
On success: → commit_and_track
```

### Step 4: commit_and_track

```
Step: commit_and_track
Type: action
Purpose: Atomically update the tracking file, manifest, and commit all changes.
  1. Write the current HEAD commit hash to .last_sync_commit
  2. Update codebase_manifest.json with new sync metadata
  3. Git add docs/repo/codebase/current/ (includes .last_sync_commit)
  4. Git commit with message "docs: incremental codebase update {job_id}"
  If the commit fails, .last_sync_commit is not committed and retains its
  previous committed value on disk — the next run will re-detect the same
  changes and retry. This ensures the tracking file never points ahead of
  the committed state.
On success: → stepCompletion
```

### Terminal: stepCompletion

```
Step: stepCompletion
Type: action
```

## Context Variables

- `CODEBASE_CURRENT_ROOT` — Path to `docs/repo/codebase/current/`
- `LAST_SYNC_COMMIT_FILE` — Path to `.last_sync_commit` tracking file

## Special Requirements

- **Early exit on no changes** — If git diff shows no relevant file changes, the workflow should exit successfully without regenerating anything.
- **First-run fallback** — If `.last_sync_commit` doesn't exist, exit with a clear message telling the user to run `sdlc_00_codebase_v1` first. Do NOT attempt a full scan.
- **File filtering** — Only trigger on changes to: `*.py`, `workflow.toml`, `pyproject.toml`, `requirements.txt`, `constants.py`. Ignore changes to `docs/`, `tests/`, `*.md`, `*.json`, and generated files.
- **Atomic updates** — If any step fails, do not commit partial updates. Exit with error and leave docs unchanged.

## Custom Actions

The workflow needs custom actions that integrate with the existing `codebase_docs.py` module. The actions should reuse the existing scan and render functions rather than reimplementing them.

**Required action features:**
1. Git integration (diff, commit)
2. Module classification (map files to modules)
3. Incremental rendering (only affected modules)
4. Tracking file management (read/write last sync commit)
5. Error handling (graceful failure, no partial commits)

## Notes

**Git hook integration:**
- A post-commit hook script (`.git/hooks/post-commit`) will submit this workflow to the backend when source code changes are detected.
- The hook should check if the daemon is running before submitting.
- Concurrency handling: If the workflow is already running, the hook should skip submission.

**Relationship to sdlc_00_codebase_v1:**
- This workflow is complementary to the full scan workflow, not a replacement.
- Use `sdlc_00_codebase_v1` for initial setup, major refactoring, or periodic full refresh.
- Use `update_codebase_docs_v1` for routine incremental updates after code changes.
