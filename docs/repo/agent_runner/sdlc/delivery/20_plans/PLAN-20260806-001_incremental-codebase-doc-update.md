---
template_id: "SYS-03-PL"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "solution architecture plan for initiative"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "Approved"
effective_version: "SDLC0RP-48s8745y"
managed_by: "workflow-generated"
source_document: "REQ-20260806-001_incremental-codebase-doc-update.md"
---

# Solution Architecture Plan: Incremental Codebase Documentation Updates with Git Hook Automation

## Plan Overview

This plan defines the solution architecture for automating incremental codebase documentation updates in agent-runner-v2 enabled repositories. The solution addresses the problem that the existing full-scan workflow (`sdlc_00_codebase_v1`) processes all 141+ module documentation files on every run, even when only a small number of source files have changed.

The solution delivers three integrated capabilities:

1. A reusable workflow package (`update_codebase_docs_v1`) that identifies source files changed since the last documentation update and regenerates only the affected module documentation files.
2. CLI commands (`install-codebase-hook`, `uninstall-codebase-hook`) to manage post-commit git hooks in any target repository.
3. A post-commit git hook mechanism that automatically triggers the incremental documentation update workflow when source code commits occur.

The architecture reuses existing platform infrastructure (`codebase_docs.py` module functions, `BackendClient.submit_run()`, daemon execution) and follows the established workflow package conventions declared in BUNDLE_AUTHORING_CONTRACT.md. The solution complements `sdlc_00_codebase_v1` and does not modify it.

### Design Principles

- Reuse over reinvention: leverage existing `codebase_docs.py` functions and the existing workflow execution pipeline.
- Non-blocking hook: the git hook must not add latency to the commit operation.
- Idempotent operations: CLI install/uninstall and the workflow itself must be safe to run repeatedly.
- Layer compliance: this plan operates within Layer 3 and treats Layer 1 governance and Layer 2 platform constitution as read-only.

---

## Requirement Traceability

All solution components trace back to the approved requirement document (REQ-20260806-001) and its source initiative (INIT-20260806-001).

| Requirement | Solution Component | Plan Section |
|---|---|---|
| FR-001, FR-002, FR-008 | Workflow Package: `update_codebase_docs_v1` | Component Breakdown - Workflow Package |
| FR-003, FR-004, FR-005, FR-006 | Incremental detection and selective rendering | Solution Architecture - Incremental Detection Strategy |
| FR-007 | Auto-commit action step | Component Breakdown - Workflow Package - Step: Commit Changes |
| FR-009, FR-010, FR-011, FR-012 | CLI commands in `run_agent.py` | Component Breakdown - CLI Commands |
| FR-013, FR-014, FR-015, FR-016 | CLI install/uninstall validation logic | Component Breakdown - CLI Commands - Install Validation |
| FR-017, FR-018, FR-019, FR-020 | Git hook script template and submission logic | Component Breakdown - Git Hook Script |
| FR-021 | No-change detection and skip logic | Solution Architecture - Incremental Detection Strategy |
| FR-022, FR-023, FR-024, FR-025 | Error handling guards | Solution Architecture - Error Handling |
| NFR-001, NFR-003 | Incremental vs full-scan performance target | Solution Architecture - Performance Strategy |
| NFR-002, NFR-014 | Lightweight non-blocking hook | Component Breakdown - Git Hook Script |
| NFR-004, NFR-005 | Concurrency guard and tracking file preservation | Solution Architecture - Concurrency and State Management |
| NFR-009, NFR-010, NFR-011, NFR-012 | Non-modification of existing full-scan workflow | Plan Overview - Design Principles |
| SC-IN-001 through SC-IN-010 | All three components | Component Breakdown |
| AC-001 through AC-016 | Validation approach | Risk Assessment, Integration Points |

### Initiative Traceability

| Initiative Outcome | Solution Component |
|---|---|
| Outcome 1: Reusable workflow package | Component A: `update_codebase_docs_v1` |
| Outcome 2: CLI hook management commands | Component B: `install-codebase-hook` / `uninstall-codebase-hook` |
| Outcome 3: Automatic post-commit trigger | Component C: Git hook script |
| Outcome 4: Zero manual intervention after setup | Integration of Components A, B, and C |
| Outcome 5: Reduced execution time | Incremental detection strategy (50%+ reduction target) |
| Outcome 6: Separation of incremental and full refresh | Explicit boundary with `sdlc_00_codebase_v1` |
| Outcome 7: Tracking mechanism (`.last_sync_commit`) | State management via `.last_sync_commit` file |

---

## Solution Architecture

### High-Level Architecture

The solution consists of three components that interact through the existing platform execution pipeline:

```
[Developer commits code]
         |
         v
[Post-commit git hook]  ---- (lightweight, non-blocking)
         |
         v
[Backend workflow submission]  ---- (BackendClient.submit_run)
         |
         v
[Daemon claims and executes workflow]  ---- (update_codebase_docs_v1)
         |
         +---> Detect changed files (git diff since .last_sync_commit)
         +---> Build filtered snapshot for affected modules
         +---> Render affected module docs
         +---> Update inventory and change impact
         +---> Update .last_sync_commit
         +---> Auto-commit documentation changes
```

### Incremental Detection Strategy

The core technical approach for incremental documentation updates:

1. **Baseline Reference**: The `.last_sync_commit` file at the repository root stores the commit hash from the last successful documentation update. This file is created during the initial full-scan workflow or by the first successful incremental run.

2. **Change Detection**: The workflow uses `git diff --name-only <last_sync_commit>..HEAD` to identify source files that have changed since the last documentation sync. This is a lightweight git operation that produces a list of changed file paths.

3. **File-to-Document Mapping**: Each changed source file is mapped to its owner documentation path using the public `build_snapshot()` output. The snapshot's `items` list contains `ScanItem` records, each with a `rel_path` and `owner_doc_path` field. The incremental workflow builds the snapshot once and then uses this mapping to identify which documentation files correspond to changed source files. This approach uses only public APIs (`build_snapshot()` and the `ScanItem` dataclass) and avoids importing private implementation functions such as `_classify_file()` or `_module_doc_path()`. For Python source files under the package root, the owner doc path follows the pattern `docs/repo/codebase/current/02_modules/<slugified-path>.md`, which is produced by the classification logic inside `build_snapshot()`.

4. **Selective Rendering**: Only the module documentation files corresponding to changed source files are regenerated using `render_module_doc()`. The `render_inventory()` function is called with the full snapshot to update the inventory listing. The `render_change_impact()` function is called with the actual `changed_files` list.

5. **Snapshot Strategy**: The `build_snapshot()` function currently scans all repository files. For the incremental workflow, the approach is:
   - Call `build_snapshot()` to obtain the full snapshot (this provides the module records needed for rendering).
   - Filter the snapshot to identify only the affected module records.
   - Call `render_module_doc()` only for affected modules.
   - This approach avoids modifying `build_snapshot()` itself (preserving NFR-010) while achieving the performance target through selective rendering rather than selective scanning.

   **Alternative considered**: Adding an optional `file_filter` parameter to `build_snapshot()`. This was rejected because it would modify the existing function's contract and risk backward compatibility with `sdlc_00_codebase_v1`. The selective rendering approach is sufficient for the 50% performance target since the expensive step is documentation rendering (AST parsing, text generation), not file listing.

6. **Tracking Update**: After successful documentation regeneration and commit, the `.last_sync_commit` file is updated with the current HEAD commit hash.

### Error Handling

| Condition | Detection Method | Behavior | Requirement |
|---|---|---|---|
| No source changes detected | `git diff` returns empty list | Skip documentation update, log message, advance `.last_sync_commit` to HEAD | FR-021 |
| Missing `.last_sync_commit` | File not found at expected path | Produce clear error message with recovery instructions (run full-scan first) | FR-022 |
| Concurrent execution in progress | Lock file or backend workflow status check | Skip run, log message | FR-023 |
| Missing `docs/repo/codebase/current/` | Directory not found | Produce clear error message or skip repository | FR-024 |
| Backend unavailable (hook submission) | Connection timeout or error in hook script | Log error, do not block commit | FR-020, NFR-006 |

### Concurrency and State Management

- **Lock mechanism**: The workflow uses a lock file (e.g., `.ukbe-runner/incremental_codebase_update.lock`) to prevent concurrent executions. If the lock file exists and its timestamp is within a reasonable window, the workflow skips execution.
- **Atomic tracking update**: The `.last_sync_commit` file is updated only after all documentation files have been successfully written and committed. This ensures the tracking reference always points to a state where documentation is in sync.
- **Tracking file preservation**: The `uninstall-codebase-hook` command removes only the git hook script. The `.last_sync_commit` file is preserved across uninstall/reinstall cycles (NFR-005, FR-016).

### Performance Strategy

The 50% reduction target (NFR-001) is achieved through:

1. **Selective rendering**: Only affected module docs are re-rendered. For a typical commit of 1-5 files, this means 1-5 module docs instead of 141+.
2. **Lightweight change detection**: `git diff --name-only` is a fast operation that does not require reading file contents.
3. **Skipping unnecessary work**: When no source files have changed (e.g., documentation-only commits), the workflow skips entirely.

The `build_snapshot()` call still scans all files, but this is a fast operation (file listing and classification) compared to the AST parsing and text generation in `render_module_doc()`.

---

## Component Breakdown

### Component A: Workflow Package (`update_codebase_docs_v1`)

**Location**: `workflows/update_codebase_docs_v1/`

**Structure**:
```
workflows/update_codebase_docs_v1/
  workflow.toml
  bundle_governance.toml
  bundle_governance/
    core_governance.md
    prompt_sop.md
    prompt_layout.md
    action_policy.md
    review_audit_contract.md
  actions.py
  context_extensions.py
  prompts/
    (no prompt-driven steps expected; all steps are action-driven)
```

**Workflow Steps** (declaration order):

| Step Name | Type | Action | Purpose | Produces |
|---|---|---|---|---|
| `detect_changes` | action | `detect_incremental_changes` | Identify changed files since `.last_sync_commit`, validate preconditions | `INCREMENTAL_CHANGE_LIST` |
| `render_incremental_docs` | action | `render_incremental_codebase_docs` | Build filtered snapshot, render affected module docs, update inventory and change impact | `INCREMENTAL_MODULE_DOCS`, `INCREMENTAL_INVENTORY`, `INCREMENTAL_CHANGE_IMPACT` |
| `update_tracking` | action | `update_last_sync_commit` | Write current HEAD to `.last_sync_commit` | `TRACKING_UPDATE_MANIFEST` |
| `commit_changes` | action | `commit_changes` | Auto-commit updated documentation files | (none) |
| `stepCompletion` | action | `step_completion` | Close workflow | (none) |

**Step Details**:

1. **`detect_incremental_changes`**: Reads `.last_sync_commit`, runs `git diff --name-only <ref>..HEAD`, builds a snapshot via `build_snapshot()` and uses the `items` list (each `ScanItem` has `rel_path` and `owner_doc_path`) to map changed files to their owner documentation paths. Filters to only files that have corresponding module documentation. If no changes detected, the workflow terminates early with a skip status. Error conditions: missing `.last_sync_commit` (FR-022), missing `docs/repo/codebase/current/` (FR-024).

2. **`render_incremental_codebase_docs`**: Calls `build_snapshot()` for the full snapshot, filters to affected module records, calls `render_module_doc()` for each affected module, calls `render_inventory()` and `render_change_impact()` with the changed files list. Writes output files to `docs/repo/codebase/current/` in-place (overwriting affected module docs and updating inventory and change impact).

3. **`update_last_sync_commit`**: Writes the current HEAD commit hash to `.last_sync_commit` at the repository root.

4. **`commit_changes`**: Uses the existing `commit_changes` action to auto-commit the updated documentation files.

**Artifact Keys** (new):

| Key | Path | Description |
|---|---|---|
| `INCREMENTAL_CHANGE_LIST` | `docs/repo/codebase/runs/{job_id}/incremental_change_list.json` | JSON list of changed files and their affected doc paths |
| `INCREMENTAL_MODULE_DOCS` | `docs/repo/codebase/current/02_modules/*.md` (affected only) | Rendered module documentation files |
| `INCREMENTAL_INVENTORY` | `docs/repo/codebase/current/01_inventory/codebase_inventory.md` | Updated inventory |
| `INCREMENTAL_CHANGE_IMPACT` | `docs/repo/codebase/current/04_changes/{job_id}-reconcile.md` | Change impact report |
| `TRACKING_UPDATE_MANIFEST` | `docs/repo/codebase/runs/{job_id}/tracking_update.json` | Record of `.last_sync_commit` update |

### Component B: CLI Commands

**Location**: New subcommands in `agent_runner_v2/run_agent.py` following the existing CLI structure.

**Commands**:

1. **`install-codebase-hook`**
   - Default: operates on current working directory
   - Flag: `--repo /path/to/repo` for arbitrary repositories
   - Validation:
     - Verify target is a git repository (`.git/` exists)
     - Verify `docs/repo/codebase/current/` exists (FR-013)
     - Check if hook is already installed (idempotent, FR-014)
   - Action:
     - Copy hook script template from `agent_runner_v2/` package to `.git/hooks/post-commit`
     - Set executable permissions (Unix) or ensure compatibility (Windows)
     - Preserve existing `.last_sync_commit` if present

2. **`uninstall-codebase-hook`**
   - Default: operates on current working directory
   - Flag: `--repo /path/to/repo` for arbitrary repositories
   - Validation:
     - Check if hook exists (idempotent, FR-015)
   - Action:
     - Remove `.git/hooks/post-commit` (or the hook script if named differently)
     - Preserve `.last_sync_commit` tracking file (FR-016)

**Hook Script Template Storage**:
- **Location**: `agent_runner_v2/data/hooks/post_commit_codebase_update.py`
- The hook script is a Python script stored as package data within the `agent_runner_v2` package.
- During installation, it is copied from the package data location to the target repository's `.git/hooks/post-commit`.
- The script includes a shebang line (`#!/usr/bin/env python3`) and is made executable on Unix systems.
- For Windows compatibility, the hook script is a Python script that can be invoked by git's hook mechanism (git on Windows supports `.py` hooks when Python is in PATH, or a small `.bat` wrapper can be generated).

**Cross-Platform Strategy** (addressing Risk R-002):
- The hook script template is written in Python for maximum portability.
- On Unix (Linux/macOS), the script is installed directly as `.git/hooks/post-commit` with executable permissions.
- On Windows, a small batch file wrapper (`.git/hooks/post-commit.bat` or `.git/hooks/post-commit`) invokes the Python script via the system Python interpreter.
- The `install-codebase-hook` command detects the platform and generates the appropriate hook file.

### Component C: Git Hook Script

**Behavior**:

1. After a commit, the hook script executes.
2. It checks for daemon/backend availability (ASSUMPTION-003). If unavailable, logs a warning and exits without blocking the commit.
3. It checks for concurrent execution by looking for the lock file (FR-023). If another update is in progress, exits silently.
4. It submits the `update_codebase_docs_v1` workflow to the backend via `BackendClient.submit_run()` (or via CLI `ukbe-run-agent run update_codebase_docs_v1`).
5. The hook exits immediately after submission (fire-and-forget), ensuring it does not block the commit operation (NFR-002, FR-020).

**Hook Script Location**: `agent_runner_v2/data/hooks/post_commit_codebase_update.py`

**Key Design Decisions**:
- The hook submits the workflow to the backend rather than executing it inline. This keeps the hook lightweight and leverages the existing daemon execution pipeline.
- The hook does not advance `.last_sync_commit`. That responsibility belongs to the workflow itself (after confirmed successful execution).
- If the backend is unavailable, the commit is not blocked. The documentation update is deferred until the next successful hook execution or manual trigger.

---

## Integration Points

### Integration Point 1: Workflow Package and `codebase_docs.py`

The workflow package's `render_incremental_codebase_docs` action imports and calls four functions from `codebase_docs.py`:

| Function | Usage in Incremental Workflow |
|---|---|
| `build_snapshot(project_root, *, mode, job_id, step, workflow_name)` | Called with full project root to obtain module records and scan items for all files. The snapshot `items` list provides the file-to-document mapping via `ScanItem.owner_doc_path` fields. The `python_modules` list is filtered to identify affected module records. |
| `render_module_doc(snapshot, module_record)` | Called once per affected module to generate updated documentation text. |
| `render_inventory(snapshot, *, title)` | Called with the full snapshot to regenerate the complete inventory listing (since the inventory covers all modules, not just changed ones). |
| `render_change_impact(snapshot, *, title, changed_files, docs_created, docs_updated, stale_docs)` | Called with the list of changed source files to produce the change impact report. |

**Integration constraint**: The `build_snapshot()` function is not modified. The incremental filtering happens after the snapshot is built, in the action logic.

**Public API dependency note**: The file-to-document mapping uses only public APIs: the `build_snapshot()` function and the `ScanItem` dataclass (which exposes `rel_path` and `owner_doc_path`). The workflow does not import or call private implementation functions (`_classify_file()`, `_module_doc_path()`), avoiding coupling to internal implementation details. If the `ScanItem` fields or `build_snapshot()` output structure change in the future, only the action logic that reads snapshot items needs to be updated.

### Integration Point 2: Workflow Package and Backend/Daemon

The workflow is submitted via `BackendClient.submit_run()` and executed by the daemon via the standard step execution pipeline:
- `BackendClient.submit_run()` creates a job for `update_codebase_docs_v1`.
- The daemon claims steps via `BackendClient.claim_step()`.
- Each action step executes via `run_action()` in `step_runner.py`.
- The `meta.json` sidecar is written per the v2 sidecar schema (CON-010).

### Integration Point 3: CLI Commands and Git Hook

The `install-codebase-hook` command copies the hook script template from the package to the target repository. The hook script, once installed, invokes the workflow submission mechanism.

### Integration Point 4: Git Hook and Backend

The hook script communicates with the backend via `BackendClient.submit_run()` or via the CLI command `ukbe-run-agent run update_codebase_docs_v1`. The preferred approach is CLI invocation because:
- It avoids importing `agent_runner_v2` internals in the hook script.
- It uses the same submission path as manual triggers.
- It is more robust to package restructuring.

### Integration Point 5: Path Resolution System

The workflow uses the existing artifact key and path resolution system:
- Artifact keys are registered in the workflow's `output_paths.py` or declared in `workflow.toml` `[step.artifacts]`.
- Paths are resolved via `artifact_keys.py`, `path_primitives.py`, and `path_catalog.py` (CON-009).
- The `.last_sync_commit` file path follows the repository root convention (not managed by the path catalog, as it is a per-repository tracking file, not a platform artifact).

---

## Data Flow

### Flow 1: Normal Incremental Update

```
1. Developer runs: git commit -m "update module X"
2. Post-commit hook fires
3. Hook checks: daemon available? lock file absent?
4. Hook invokes: ukbe-run-agent run update_codebase_docs_v1
5. Workflow step: detect_incremental_changes
   - Reads .last_sync_commit -> gets commit hash "abc123"
   - Runs: git diff --name-only abc123..HEAD
   - Result: ["agent_runner_v2/codebase_docs.py", "agent_runner_v2/run_agent.py"]
    - Maps to doc paths using snapshot items (ScanItem.owner_doc_path):
      - "agent-runner-v2-codebase-docs.md"
      - "agent-runner-v2-run-agent.md"
    - Writes INCREMENTAL_CHANGE_LIST artifact
 6. Workflow step: render_incremental_codebase_docs
    - Uses snapshot from step 5 (or rebuilds if needed)
    - Filters python_modules to affected records
    - Calls render_module_doc() for each affected module
   - Calls render_inventory() with full snapshot
   - Calls render_change_impact() with changed files list
   - Writes updated docs to docs/repo/codebase/current/02_modules/
   - Writes updated inventory to docs/repo/codebase/current/01_inventory/
   - Writes change impact to docs/repo/codebase/current/04_changes/
7. Workflow step: update_last_sync_commit
   - Gets current HEAD commit hash
   - Writes to .last_sync_commit
8. Workflow step: commit_changes
   - Runs: git add docs/repo/codebase/current/
   - Runs: git commit -m "docs: incremental codebase update [auto]"
9. Workflow step: stepCompletion
```

### Flow 2: No Changes Detected

```
1-4. Same as Flow 1
5. Workflow step: detect_incremental_changes
   - git diff --name-only returns empty list
   - Workflow skips remaining steps with "no changes" status
```

### Flow 3: First Run (Missing Tracking File)

```
1-4. Same as Flow 1
5. Workflow step: detect_incremental_changes
   - .last_sync_commit not found
   - Workflow fails with clear error message:
     "No .last_sync_commit file found. Run the full-scan workflow
      (sdlc_00_codebase_v1) first to establish the initial documentation set."
```

### Flow 4: Hook Installation

```
1. Developer runs: ukbe-run-agent install-codebase-hook --repo /path/to/repo
2. CLI validates:
   - .git/ exists in target repo
   - docs/repo/codebase/current/ exists
3. CLI copies hook script template to .git/hooks/post-commit
4. CLI sets executable permissions (Unix) or creates .bat wrapper (Windows)
5. CLI reports: "Hook installed successfully"
```

### Flow 5: Hook Uninstallation

```
1. Developer runs: ukbe-run-agent uninstall-codebase-hook --repo /path/to/repo
2. CLI checks if hook exists at .git/hooks/post-commit
3. CLI removes hook file
4. CLI preserves .last_sync_commit (does not delete it)
5. CLI reports: "Hook removed successfully"
```

---

## Risk Assessment

### Risk PLAN-R-001: `build_snapshot()` Performance Overhead

**Description**: The `build_snapshot()` function scans all repository files even in incremental mode. For very large repositories, the scan itself may become a bottleneck.

**Impact**: Medium -- affects NFR-001 (50% reduction target).

**Mitigation**: The snapshot scan is file listing and classification only (no AST parsing). The expensive operations are in `render_module_doc()` (AST parsing, text generation). Selective rendering of affected modules should achieve the 50% target even with full snapshot scanning. If needed in the future, `build_snapshot()` can be extended with an optional file filter parameter in a backward-compatible manner (new keyword-only argument with default `None`).

**Traces to**: NFR-001, FR-005, R-001

### Risk PLAN-R-002: Git Hook Cross-Platform Compatibility

**Description**: Git hooks are platform-sensitive. The hook script must work on Windows, Linux, and macOS.

**Impact**: Medium -- affects FR-009, FR-017, AC-005, AC-010.

**Mitigation**: The hook script is written in Python. On Unix, it is installed as an executable script with a shebang line. On Windows, a small batch file wrapper invokes the Python script. The `install-codebase-hook` command detects the platform using `sys.platform` and generates the appropriate hook file. Testing covers all three platforms.

**Traces to**: R-002, NFR-002

### Risk PLAN-R-003: Race Condition on `.last_sync_commit`

**Description**: If two incremental runs overlap (despite the concurrency guard), they could both read the same `.last_sync_commit` value and produce conflicting documentation commits.

**Impact**: Medium -- affects NFR-004, FR-023.

**Mitigation**: The concurrency guard uses a lock file with a timestamp. If the lock is older than a reasonable timeout (e.g., 10 minutes), it is considered stale and can be overridden. The lock file is created at the start of `detect_incremental_changes` and removed at the end of `commit_changes`. The `.last_sync_commit` update is the last write operation before commit, ensuring it reflects the actual HEAD after the documentation commit.

**Traces to**: R-003, NFR-004

### Risk PLAN-R-004: Backend Unavailability During Hook Execution

**Description**: If the backend is unavailable when the hook fires, the documentation update is lost. The `.last_sync_commit` is not advanced (correct behavior), but documentation may accumulate drift.

**Impact**: Low -- the next successful commit + hook execution will catch up.

**Mitigation**: The hook checks daemon availability before submitting. If unavailable, it logs a warning and exits without blocking the commit. The `.last_sync_commit` is not advanced until the workflow completes successfully, so the next run will include all accumulated changes since the last successful sync. This provides natural catch-up behavior.

**Traces to**: R-004, NFR-006

### Risk PLAN-R-005: In-Place Overwrite of Existing Documentation

**Description**: The incremental workflow writes directly to `docs/repo/codebase/current/`, overwriting existing module docs. If the rendering produces incorrect output, the existing documentation is lost.

**Impact**: Low -- the full-scan workflow (`sdlc_00_codebase_v1`) can regenerate all documentation from scratch as a recovery mechanism.

**Mitigation**: The `render_module_doc()` function is the same function used by the full-scan workflow. It produces deterministic output from the source code. Git history provides a full audit trail and rollback capability. The auto-commit message clearly identifies incremental updates for easy identification.

**Traces to**: NFR-009, NFR-011

---

## Dependencies

### Platform Dependencies

| ID | Dependency | Verification Status |
|---|---|---|
| PLAN-DEP-001 | `codebase_docs.py` with `build_snapshot()`, `render_module_doc()`, `render_inventory()`, `render_change_impact()`, and `ScanItem` dataclass | Verified: functions confirmed present in source code at expected signatures; `ScanItem` at line 122 with `rel_path` and `owner_doc_path` fields |
| PLAN-DEP-002 | `BackendClient.submit_run()` for workflow submission | Verified: present in `v2/backend_client_v1.py` |
| PLAN-DEP-003 | `daemon_v2.py` for workflow execution | Verified: module confirmed present |
| PLAN-DEP-004 | `@action()` decorator and `ActionResult` dataclass for action steps | Verified: present in `runner_actions.py` |
| PLAN-DEP-005 | `commit_changes` action for auto-committing documentation | Verified: existing action used by `sdlc_00_codebase_scaffold_v1` |
| PLAN-DEP-006 | Workflow package loader and registry | Verified: existing infrastructure in `workflow_packages/` |
| PLAN-DEP-007 | Artifact key and path resolution system (`artifact_keys.py`, `path_primitives.py`, `path_catalog.py`) | Verified: existing infrastructure |

### Prerequisite Dependencies

| ID | Dependency | Notes |
|---|---|---|
| PLAN-DEP-008 | Target repository has initial codebase documentation from `sdlc_00_codebase_v1` or `codebase-init` | BC-001 |
| PLAN-DEP-009 | Target repository has `docs/repo/codebase/current/` directory structure | FR-013 |
| PLAN-DEP-010 | Target repository is a git repository with write access to `.git/hooks/` | DEP-009 |

### Infrastructure Dependencies

| ID | Dependency | Notes |
|---|---|---|
| PLAN-DEP-011 | Python 3.12+ runtime available in the target environment | Platform requirement |
| PLAN-DEP-012 | `agent-runner-v2` package installed and accessible | DEP-010 |
| PLAN-DEP-013 | Backend service running and reachable for workflow submission in daemon mode | DEP-011 |

---

## Open Questions

### OQ-001: Hook Script Exact Storage Path Within Package

**Status**: Deferred to implementation phase.
**Description**: The exact path for the hook script template within the `agent_runner_v2/` package needs to be finalized. The proposed location is `agent_runner_v2/data/hooks/post_commit_codebase_update.py`. This requires verifying that the package data configuration (`pyproject.toml` or `setup.cfg`) includes the `data/hooks/` directory in the package distribution.
**Affects**: FR-019, CON-011
**Resolution approach**: Check the existing `pyproject.toml` for package data inclusion patterns and select a path consistent with them.

### OQ-002: Concurrency Guard Implementation Detail

**Status**: Deferred to implementation phase.
**Description**: The concurrency guard mechanism (lock file vs. backend workflow status check) needs to be finalized. A lock file at `.ukbe-runner/incremental_codebase_update.lock` is proposed, but the backend may also expose workflow status that can be queried. The lock file approach is simpler and does not require backend connectivity.
**Affects**: FR-023, NFR-004
**Resolution approach**: Evaluate during implementation. Default to lock file approach for simplicity.

### OQ-003: Windows Hook Wrapper Strategy

**Status**: Deferred to implementation phase.
**Description**: On Windows, git hooks can be `.bat` files or executable scripts. The strategy for generating a Windows-compatible hook wrapper needs to be validated on an actual Windows environment. Options: (a) `.bat` wrapper that calls `python <hook_script>`, (b) Python script with `.py` extension if git on Windows supports it, (c) Use `ukbe-run-agent` CLI directly in a `.bat` hook.
**Affects**: R-002, FR-009
**Resolution approach**: Test on Windows during implementation. Option (c) may be simplest -- the hook is a `.bat` file that runs `ukbe-run-agent run update_codebase_docs_v1`.

### OQ-004: Benchmark Protocol for NFR-001

**Status**: To be defined during backlog phase.
**Description**: The 50% reduction target (NFR-001) requires a defined benchmark protocol. The protocol should specify: test repository, baseline measurement (full-scan time), incremental measurement (1-5 file changes), system conditions, and measurement methodology (wall-clock time for full workflow execution).
**Affects**: NFR-001, NFR-003, AC-012
**Resolution approach**: Define benchmark protocol during backlog/task planning phase. Risk R-005 in the requirements document already identifies this as a planning-phase deliverable.

### OQ-005: Manual Trigger Command Evaluation

**Status**: Evaluation deferred; not committed to scope.
**Description**: The initiative notes (ASSUMPTION-004) suggest evaluating a manual trigger command for testing without committing. This is an evaluation item, not a committed requirement. If promoted to requirement, it must go through the initiative amendment process.
**Affects**: ASSUMPTION-004
**Resolution approach**: Evaluate during planning review. If the `ukbe-run-agent run update_codebase_docs_v1` CLI invocation is sufficient for manual testing, no additional command is needed.

---

## Critique Resolution

**Source Critique:** incremental-codebase-doc-update-CRITIQUE-20260806-001.md
**Critique Decision:** APPROVED
**Critique Date:** 2026-08-12
**Critical Findings:** 0
**Major Findings:** 0
**Minor Observations:** 1 (non-blocking)

### Finding 1: Private Function Dependency on `_classify_file()` and `_module_doc_path()`

**Finding summary:** The plan referenced `_classify_file()` and `_module_doc_path()` (private functions prefixed with underscore) in the Incremental Detection Strategy section for file-to-document mapping. The critique noted this creates a minor coupling risk to internal implementation details.

**Resolution:** The plan has been updated to eliminate the dependency on private functions. The file-to-document mapping is now described as using the public `build_snapshot()` output, specifically the `items` list of `ScanItem` records, where each record contains `rel_path` and `owner_doc_path` fields. This approach uses only public APIs: `build_snapshot()` and the `ScanItem` dataclass. No private function imports are required. The following sections were updated:

1. **Incremental Detection Strategy - File-to-Document Mapping**: Replaced the reference to `_classify_file()` and `_module_doc_path()` with a description of using `build_snapshot()` output and `ScanItem.owner_doc_path` for mapping.
2. **Step Details - `detect_incremental_changes`**: Updated to describe using the snapshot `items` list for file-to-document mapping.
3. **Data Flow - Flow 1**: Updated step 5 to note that doc path mapping uses snapshot items.
4. **Integration Point 1**: Added a "Public API dependency note" paragraph clarifying that only public APIs (`build_snapshot()` and `ScanItem`) are used, explicitly noting that private functions (`_classify_file()`, `_module_doc_path()`) are not imported.
5. **Platform Dependencies - PLAN-DEP-001**: Updated to include `ScanItem` dataclass as a verified dependency, with its location and key fields documented.

**Affected sections:** Incremental Detection Strategy, Component A Step Details, Data Flow, Integration Point 1, Platform Dependencies
