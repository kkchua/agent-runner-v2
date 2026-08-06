---
template_id: SYS-03-DI
version: "1.0.0"
doc_type: "workflow_output"
authority: "human-authored"
scan_policy: "include"
scan_reason: "SDLC initiative input for incremental codebase doc automation"
managed_by: "human-authored"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "draft"
---

# Incremental Codebase Documentation Updates with Git Hook Automation

## Objective

Provide automated incremental codebase documentation updates for all agent-runner-v2 enabled repositories by implementing a reusable workflow and git hook management commands.

## Problem Statement

### Current State

The platform uses `sdlc_00_codebase_v1` to generate comprehensive codebase documentation (141+ module docs, inventory, component docs, change impact reports). All agent-runner-v2 enabled repos follow the same `docs/repo/codebase/` structure. The workflow performs a full scan of the entire repository on every run.

### Pain Points

- Full scan processes all modules even when only 1-2 files changed
- Each run takes significant time and computational resources
- Manual trigger means docs often fall out of sync with code changes
- No automated mechanism to keep docs current between manual refreshes
- Every repo with codebase docs faces the same problem independently

### Why This Initiative Is Needed

Developers need up-to-date codebase documentation to understand the system, but the cost of running a full scan on every commit is prohibitive. Without automation, docs become stale quickly, reducing their value as a living reference. Since all agent-runner-v2 repos share the same docs structure, a single solution can serve all of them.

### Impact of Not Undertaking This Initiative

- Codebase documentation will increasingly diverge from actual code across all repos
- Developers will rely less on docs, preferring to read code directly
- The investment in comprehensive doc generation is underutilized
- Each repo must manually manage doc updates, leading to inconsistency

## Expected Outcomes

- Reusable `update_codebase_docs_v1` workflow that works in any agent-runner-v2 repo
- CLI commands to install and uninstall git hook in any repo (current directory or specified path)
- Post-commit git hook that automatically triggers incremental updates on code changes
- Codebase documentation stays in sync with code changes with zero manual intervention
- Reduced execution time and resource usage compared to full scans
- Clear separation between incremental updates (frequent) and full refresh (periodic)

## Scope

### In Scope

- Design and implement `update_codebase_docs_v1` workflow for incremental updates (repo-agnostic)
- Implement `install-codebase-hook` CLI command to install git hook in any repo
- Implement `uninstall-codebase-hook` CLI command to remove git hook
- CLI commands support both current directory (default) and `--repo /path/to/repo` flag
- Post-commit git hook script that submits workflow to backend
- Integration between git hook, backend, and daemon execution
- Tracking mechanism to determine what changed since last doc update
- Auto-commit of updated documentation
- Error handling for edge cases (no changes, first run, concurrent execution, missing docs structure)

### Out of Scope

- Modifications to the existing `sdlc_00_codebase_v1` full scan workflow
- Changes to the codebase documentation format or structure
- Support for repos that don't follow the standard agent-runner-v2 docs structure
- Real-time or continuous documentation updates (batch per commit is sufficient)

## Constraints

- Must integrate with existing `codebase_docs.py` module (reuse scan and render functions)
- Must work with existing backend/daemon architecture (submit workflow, claim, execute)
- Git hook must be lightweight (cannot block commits with heavy processing)
- Workflow must handle concurrent execution gracefully (skip if already running)
- Must detect if repo has the standard codebase docs structure before enabling
- Install/uninstall commands must be idempotent (safe to run multiple times)

## Dependencies

- Existing `codebase_docs.py` module with `build_snapshot()`, `render_module_doc()`, `render_inventory()`, `render_change_impact()` functions
- Existing backend API for workflow submission and claiming
- Existing daemon infrastructure for workflow execution
- Standard `docs/repo/codebase/` structure (created by `codebase-init` or `sdlc_00_codebase_v1`)
- Git repository with post-commit hook support

## Success Criteria

- Workflow successfully regenerates only affected module docs in any agent-runner-v2 repo
- `install-codebase-hook` command installs working git hook in any repo with standard structure
- `uninstall-codebase-hook` command cleanly removes the git hook
- CLI commands work with both current directory and `--repo` flag
- Git hook triggers workflow automatically after commits with source code changes
- Updated docs are committed automatically without manual intervention
- Workflow execution time is significantly less than full scan for typical commits (1-5 files changed)
- No duplicate or concurrent workflow executions
- Clear error messages when tracking file is missing (first run) or docs structure is absent
- Hook installation is idempotent (can run multiple times safely)

## Notes

- Workflow spec already created at `docs/repo/workflow_builder/specs/incremental-codebase-update.md`
- The incremental workflow complements `sdlc_00_codebase_v1`, not replaces it
- Full scan workflow should still be used for initial setup, major refactoring, or periodic refresh
- Git hook should check daemon status before submitting workflow
- The `install-codebase-hook` command should verify the repo has `docs/repo/codebase/current/` before installing
- The `uninstall-codebase-hook` command should remove the hook but leave the `.last_sync_commit` tracking file (in case user re-installs later)
- CLI commands default to current directory, but support `--repo /path/to/repo` for convenience
- Consider adding a manual trigger command for testing without committing
- Hook script should be stored in agent-runner-v2 package and copied to target repo's `.git/hooks/`
