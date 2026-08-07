# Workflow Specification: Incremental Codebase Doc Update

> Save to `docs/repo/workflow_builder/specs/incremental-codebase-update.md`.
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
| `UPDATED_MODULE_DOCS` | `current/02_modules/{module_name}.md` | Regenerated module docs for affected modules only |
| `UPDATED_INVENTORY` | `current/codebase_inventory.md` | Updated inventory reflecting any new/removed files |
| `UPDATED_CHANGE_IMPACT` | `current/change_impact.md` | Change impact report for this incremental update |
| `UPDATED_MANIFEST` | `current/codebase_manifest.json` | Updated manifest with new sync commit hash |

## Quality Requirements

- **Early exit on no changes** — If git diff shows no relevant file changes, exit successfully without regenerating anything.
- **File filtering** — Only trigger on changes to: `*.py`, `workflow.toml`, `pyproject.toml`, `requirements.txt`, `constants.py`. Ignore changes to `docs/`, `tests/`, `*.md`, `*.json`, and generated files.
- **Atomic updates** — If any step fails, do not commit partial updates. Exit with error and leave docs unchanged.
- **Tracking file consistency** — The `.last_sync_commit` file must never point ahead of the committed state. If the commit fails, the tracking file retains its previous committed value on disk, so the next run re-detects the same changes and retries.
- **Module classification** — Map changed file paths to affected Python module names using the existing module classification logic from `codebase_docs.py`.

## Custom Actions

The workflow integrates with the existing `codebase_docs.py` module. Reuse existing scan and render functions rather than reimplementing them.

**Required capabilities:**
1. Git integration (diff since last sync commit, atomic commit)
2. Module classification (map changed files to affected modules)
3. Incremental rendering (only affected modules, plus inventory and change impact)
4. Tracking file management (read/write last sync commit hash)
5. Error handling (graceful failure, no partial commits)

## Builder Instructions

**Domain phases** (builder determines step sequence):

1. **Detect** — Read last sync commit, run git diff, filter to relevant file types
2. **Scan** — Map changed files to affected module names
3. **Regenerate** — Call `codebase_docs.py` functions to render affected module docs
4. **Commit** — Atomically update tracking file, manifest, and git commit

**Domain constraints:**

- The workflow must reuse `codebase_docs.py` functions: `build_snapshot`, `render_module_doc`, `render_inventory`, `render_change_impact`.
- Git commit message format: `"docs: incremental codebase update {job_id}"`
- If no relevant changes detected, exit successfully without regenerating.

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
