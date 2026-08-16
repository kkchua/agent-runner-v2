# Workflow Specification: Incremental Codebase Doc Update

> Save to `docs/repo/workflow_builder/specs/update_codebase_docs_v1.md`.
> The workflow builder reads this document and generates the complete
> workflow package.
>
> **Key principle:** Describe WHAT the workflow does. The builder infers HOW
> to structure it (step sequence, routing, role policies, gatekeepers).
> See [BUILDER_REQUIREMENTS.md](../current/BUILDER_REQUIREMENTS.md) for what
> the builder enforces automatically.

## Overview

**Workflow name:** `update_codebase_docs_v1`
**Label:** Incremental Codebase Doc Update
**Job prefix:** `UCBD`
**Init step:** `detect_changes`
**Description:** Incrementally updates codebase documentation by regenerating only the docs affected by recent code changes, triggered automatically by a post-commit git hook.

## Purpose

The full codebase scan workflow (`sdlc_00_codebase_v1`) processes all 141+ modules on every run, which is too heavy for frequent updates. Most commits only touch a few files, making a full scan overkill.

**Trigger:** A post-commit git hook submits this workflow to the backend when source code changes are detected.

**Outcome:** Only affected module docs are regenerated, keeping codebase documentation in sync with minimal overhead. The workflow auto-commits the updated docs.

## Workflow Type

**Action-only** — All steps are deterministic operations (git commands, file scanning, doc generation). No LLM involvement.

## Input Artifacts

**No user-provided inputs.** The workflow reads a tracking file from the repo structure:

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| `CODEBASE_CURRENT_ROOT` | `{repo_root}/docs/repo/codebase/current/` | Codebase documentation root |
| `LAST_SYNC_COMMIT_FILE` | `{CODEBASE_CURRENT_ROOT}/.last_sync_commit` | Tracking file with last sync commit hash |

If `.last_sync_commit` doesn't exist, the workflow exits with a clear message telling the user to run `sdlc_00_codebase_v1` first. Do NOT attempt a full scan.

## Output Artifacts

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `UPDATED_MODULE_DOCS_FILE` | `current/02_modules/{module_name}.md` | Regenerated module docs for affected modules only |
| `UPDATED_INVENTORY_FILE` | `current/codebase_inventory.md` | Updated inventory reflecting any new/removed files |
| `UPDATED_CHANGE_IMPACT_FILE` | `current/change_impact.md` | Change impact report for this incremental update |
| `UPDATED_MANIFEST_FILE` | `current/codebase_manifest.json` | Updated manifest with new sync commit hash |

## Custom Actions

**Two actions.** This workflow integrates with the existing `codebase_docs.py` module. Reuse existing scan and render functions rather than reimplementing them.

### Action: detect_and_regenerate

**Purpose:** Read the last sync commit hash from `.last_sync_commit`. Run `git diff --name-only <last_sync>..HEAD` to get changed files. Filter to relevant file types (`*.py`, `workflow.toml`, `pyproject.toml`, `requirements.txt`). If no relevant changes, return APPROVED with empty output (early exit). Map changed files to affected Python module names using the existing module classification logic from `codebase_docs.py`. For each affected module, call `codebase_docs.py` functions: `render_module_doc()` for module docs, `render_inventory()` for the inventory, `render_change_impact()` for the change report. Write all rendered files to the run directory.

**Inputs:** CODEBASE_CURRENT_ROOT, LAST_SYNC_COMMIT_FILE

**Outputs:** UPDATED_MODULE_DOCS_FILE (one or more files), UPDATED_INVENTORY_FILE, UPDATED_CHANGE_IMPACT_FILE

**Configuration:** None. All paths resolved from context variables.

**Error handling:**
- If `.last_sync_commit` doesn't exist, return REJECTED with reject_code `NO_SYNC_HISTORY` and remark telling user to run `sdlc_00_codebase_v1` first.
- If `git diff` fails (not a git repo, corrupt history), return REJECTED with reject_code `GIT_DIFF_FAILED`.
- If a module render fails, return REJECTED with reject_code `RENDER_FAILED` — do NOT write partial output. All renders must succeed before any files are written.
- If no relevant file changes detected, return APPROVED with empty outputs (early exit, no regeneration needed).

**Returns:** APPROVED when all affected modules rendered successfully (or no changes detected). REJECTED on git failure, render failure, or missing sync history.

### Action: commit_updates

**Purpose:** Atomically update the codebase documentation. Copy rendered files from the run directory to `docs/repo/codebase/current/` (overwriting existing files). Update `.last_sync_commit` with the current HEAD commit hash. Run `git add docs/repo/codebase/current/` and `git commit -m "docs: incremental codebase update {job_id}"`.

**Inputs:** UPDATED_MODULE_DOCS_FILE, UPDATED_INVENTORY_FILE, UPDATED_CHANGE_IMPACT_FILE, UPDATED_MANIFEST_FILE

**Outputs:** UPDATED_MANIFEST_FILE (updated with new sync commit hash)

**Configuration:** None.

**Error handling:**
- If `git commit` fails (nothing to commit, merge conflict), return REJECTED with reject_code `COMMIT_FAILED`. The `.last_sync_commit` file is written AFTER the commit succeeds, so a failed commit leaves the tracking file pointing at the previous successful sync — the next run will re-detect the same changes and retry.
- If copy to `current/` fails (permissions, disk full), return REJECTED with reject_code `COPY_FAILED` — do NOT update `.last_sync_commit`.

**Returns:** APPROVED when commit succeeds. REJECTED on copy or commit failure.

## Quality Requirements

- **Early exit on no changes** — If git diff shows no relevant file changes, exit successfully without regenerating anything.
- **File filtering** — Only trigger on changes to: `*.py`, `workflow.toml`, `pyproject.toml`, `requirements.txt`, `constants.py`. Ignore changes to `docs/`, `tests/`, `*.md`, `*.json`, and generated files.
- **Atomic updates** — If any step fails, do not commit partial updates. Exit with error and leave docs unchanged.
- **Tracking file consistency** — The `.last_sync_commit` file must never point ahead of the committed state. If the commit fails, the tracking file retains its previous committed value on disk, so the next run re-detects the same changes and retries.
- **Module classification** — Map changed file paths to affected Python module names using the existing module classification logic from `codebase_docs.py`.

## Builder Instructions

**Domain phases** (builder determines step sequence):

1. **Detect** — Read last sync commit, run git diff, filter to relevant file types (action: `detect_and_regenerate`)
2. **Commit** — Atomically update tracking file, manifest, and git commit (action: `commit_updates`)

**Domain constraints:**

- The workflow must reuse `codebase_docs.py` functions: `build_snapshot`, `render_module_doc`, `render_inventory`, `render_change_impact`.
- Git commit message format: `"docs: incremental codebase update {job_id}"`
- If no relevant changes detected, exit successfully without regenerating.
- No prompt-driven steps — this is a pure action-only workflow.

**Similar workflow:** `sdlc_00_codebase_v1` (full scan, same output structure).

## Notes

**Git hook integration:**
- A post-commit hook script (`.git/hooks/post-commit`) submits this workflow to the backend when source code changes are detected.
- The hook checks if the daemon is running before submitting.
- Concurrency handling: If the workflow is already running, the hook skips submission.

**Relationship to sdlc_00_codebase_v1:**
- This workflow is complementary to the full scan workflow, not a replacement.
- Use `sdlc_00_codebase_v1` for initial setup, major refactoring, or periodic full refresh.
- Use `update_codebase_docs_v1` for routine incremental updates after code changes.
