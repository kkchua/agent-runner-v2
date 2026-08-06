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
effective_version: "SDLC20PLN-1qaeewl8"
managed_by: "workflow-generated"
---

# Plan: Incremental Codebase Documentation Updates with Git Hook Automation

## Document Metadata

- Document ID: PLAN-20260806-001
- Source requirement: REQ-20260806-001_incremental-codebase-doc-update.md
- Date of generation: 2026-08-06
- Producing workflow: sdlc_20_planning_v1
- Producing agent: Workflow Architect

## Plan Overview

This plan defines the solution architecture for implementing incremental codebase documentation updates with git hook automation in the agent-runner-v2 platform. The solution replaces the full-scan model (for routine updates) with a targeted, change-aware incremental regeneration approach that keeps module-level docs synchronized with source code after each commit.

The solution consists of three major components:

1. An action-only workflow (update_codebase_docs_v1) with four sequential steps for incremental documentation regeneration.
2. Two CLI subcommands (install-codebase-hook, uninstall-codebase-hook) for git hook lifecycle management.
3. A post-commit git hook shell script that detects relevant source code changes and triggers the workflow via backend submission.

The architecture reuses existing rendering functions from codebase_docs.py (build_snapshot, render_module_doc, render_inventory, render_change_impact) rather than reimplementing scan and render logic. The workflow follows the Layer 2 action step model, executing Python functions via the workflow package @action() decorator and runner_actions.py dispatch mechanism.

**Work stream separation:** The solution has two independent work streams. Work stream 1 (workflow package generation) is handled by workflow_builder_v1 using the existing spec at docs/repo/workflow_builder/specs/incremental-codebase-update.md — this produces the update_codebase_docs_v1 workflow package (workflow.toml + actions.py). Work stream 2 (CLI commands and hook infrastructure) is the implementation scope of this plan — it covers the install-codebase-hook and uninstall-codebase-hook CLI subcommands, the post-commit hook script template, and the run_agent.py dispatch integration.

## Requirement Traceability

This plan covers all functional and non-functional requirements from REQ-20260806-001. The traceability matrix maps requirements to architectural components.

### Functional Requirements Coverage

| Requirement | Component | Plan Section |
|---|---|---|
| FR-001 (Incremental workflow) | update_codebase_docs_v1 workflow | Solution Architecture, Component Breakdown |
| FR-002 (Changed file detection) | detect_changes action step | Data Flow |
| FR-003 (Selective regeneration) | scan_affected_modules + regenerate_docs steps | Component Breakdown, Data Flow |
| FR-004 (Install CLI) | codebase_hook_commands.py (install) | Component Breakdown |
| FR-005 (Uninstall CLI) | codebase_hook_commands.py (uninstall) | Component Breakdown |
| FR-006 (CLI targeting) | codebase_hook_commands.py (--repo flag) | Component Breakdown |
| FR-007 (Post-commit hook) | post-commit hook script | Component Breakdown |
| FR-008 (Backend submission) | Hook script via ukbe-run-agent submit | Integration Points |
| FR-009 (Tracking file) | commit_and_track action step | Data Flow |
| FR-010 (Auto-commit) | commit_and_track action step | Data Flow |
| FR-011 (Missing tracking file) | detect_changes step early exit | Data Flow |
| FR-012 (No relevant changes) | detect_changes step early exit | Data Flow |
| FR-013 (Unreachable commit) | detect_changes step early exit | Data Flow |
| FR-014 (Missing doc structure) | Validation in detect_changes + install command | Component Breakdown |
| FR-015 (Hook logging) | Hook script error handling | Component Breakdown |
| FR-016 (Concurrency prevention) | Hook script concurrency check | Integration Points |
| FR-017 (Auto-commit failure) | commit_and_track step error handling | Data Flow |
| FR-018 (Manifest update) | commit_and_track action step | Data Flow |

### Non-Functional Requirements Coverage

| Requirement | Design Decision | Plan Section |
|---|---|---|
| NFR-001 (Lightweight hook) | Hook only performs submission, no blocking | Component Breakdown |
| NFR-002 (CLI idempotency) | Install checks for existing hook; uninstall checks for absence | Component Breakdown |
| NFR-003 (Concurrency safety) | Backend-level active run check via list_runs() | Integration Points |
| NFR-004 (Function reuse) | Direct import of codebase_docs.py functions | Solution Architecture |
| NFR-005 (Action step compliance) | All steps use @action() decorator (package-local), resolved via runner_actions.py _resolve_action_fn() | Solution Architecture |
| NFR-006 (Standard sidecar) | Runner writes sidecar from ActionResult | Solution Architecture |
| NFR-007 (Hook packaging) | Hook stored in agent-runner-v2 package, copied during install | Component Breakdown |
| NFR-008 (Performance) | Selective regeneration reduces scope to affected modules | Solution Architecture |
| NFR-009 (Repo-agnostic) | No hardcoded repository paths; uses docs/repo/codebase/current/ contract | Solution Architecture |
| NFR-010 (CLI pattern) | Follows run_agent.py if/elif dispatch convention | Component Breakdown |

## Solution Architecture

The solution architecture follows a three-component design that separates concerns between the automated trigger mechanism (git hook), the execution engine (daemon/backend), and the documentation logic (action steps).

### Architectural Pattern

The solution uses a **trigger-execute** pattern:

1. **Trigger layer**: The post-commit git hook detects source code changes and submits the workflow to the backend. This is a lightweight shell script that delegates all logic to the CLI.

2. **Execution layer**: The daemon claims the submitted workflow and executes it through the standard action step lifecycle. Each step is a Python function registered via @action() decorator in the workflow package's actions.py, resolved by runner_actions.py _resolve_action_fn() (package-local first, then global fallback).

3. **Logic layer**: The action steps reuse existing rendering functions from codebase_docs.py and add incremental logic (change detection, selective regeneration, tracking file management).

### Key Architecture Decisions

**AD-001: Action-only workflow (no LLM involvement)**

The update_codebase_docs_v1 workflow uses only action steps. This eliminates LLM cost, latency, and non-determinism. All operations are deterministic Python functions. This decision is driven by NFR-005 and CON-007.

**AD-002: Reuse of existing rendering functions**

The incremental workflow imports and calls build_snapshot(), render_module_doc(), render_inventory(), and render_change_impact() directly from codebase_docs.py. This avoids code duplication and ensures output consistency with the full-scan workflow. The only new logic is the change detection and module selection filter. This decision is driven by CON-001 and DEP-001.

**Known limitation:** build_snapshot() (codebase_docs.py:762) performs a full repository scan via _iter_repo_files() and _scan_python_module() regardless of the mode parameter. The mode value ("incremental" vs "reconcile") is stored in the snapshot dict but does not filter which files are scanned. Therefore, snapshot construction is O(all files) even for single-file changes. The performance benefit of the incremental approach comes solely from selective module doc rendering (render_module_doc() called only for affected modules), not from the snapshot construction phase. This is documented as a known limitation in Risk Assessment (RISK-006).

**AD-003: CLI-based hook submission**

The post-commit hook invokes `ukbe-run-agent submit --workflow-name update_codebase_docs_v1` via a shell command. The hook does not implement workflow execution logic. The CLI command internally uses BackendClient.submit_run(). This decision is driven by FR-008 and ASSUMPTION-003.

**AD-004: Separate CLI command module**

The install/uninstall hook commands are implemented in a new module (codebase_hook_commands.py) following the codebase_init_commands.py pattern. This separates hook management from the core CLI dispatch and keeps the command implementation self-contained. The dispatch entry point is added to run_agent.py using the established if/elif pattern.

**AD-005: Tracking file at docs/repo/codebase/current/.last_sync_commit**

The .last_sync_commit file is stored inside the codebase current directory. This co-locates the tracking state with the documentation it references, making it easy to find and manage. The file contains a single commit hash string.

**AD-006: Component docs excluded from incremental regeneration**

Component documents (03_components/) aggregate cross-module data and are not suitable for incremental regeneration based on single-commit file-level diffs. They remain the responsibility of the full-scan workflow (sdlc_00_codebase_v1). This is documented as OUT-002a in the requirements.

**AD-007: Backend-level concurrency check**

The hook checks for active runs of update_codebase_docs_v1 before submitting. This is done via BackendClient.list_runs() with workflow_name and status_group filters at the backend level, not via file-based locking. This prevents duplicate workflow executions when commits occur in rapid succession.

### Workflow Step Architecture

The update_codebase_docs_v1 workflow follows a four-step linear pipeline:

```
detect_changes -> scan_affected_modules -> regenerate_docs -> commit_and_track -> stepCompletion
```

Each step is an action step that receives context, state, step_cfg, and project_root, and returns an ActionResult.

## Component Breakdown

### Component 1: update_codebase_docs_v1 Workflow

**Type:** Action-only workflow package

**Responsibility:** Incremental documentation regeneration for changed source files.

**Generation:** This workflow package is generated by workflow_builder_v1 from the existing spec at docs/repo/workflow_builder/specs/incremental-codebase-update.md. The spec is the single source of truth for the workflow's step sequence, action implementations, and artifact declarations. The builder produces both workflow.toml and actions.py under workflows/update_codebase_docs_v1/.

**Steps (from spec):**

| Step | Action Function | Responsibility |
|---|---|---|
| detect_changes | detect_changes | Read .last_sync_commit; git diff to find changed files; filter relevant types; early exit on no changes or missing/unreachable tracking file |
| scan_affected_modules | scan_affected_modules | Map changed file paths to affected module names using codebase_docs.py classification logic |
| regenerate_docs | regenerate_docs | Call build_snapshot(), render_module_doc() for affected modules only, render_inventory(), render_change_impact() |
| commit_and_track | commit_and_track | Write HEAD hash to .last_sync_commit, update codebase_manifest.json, git add + commit atomically |

**Action Registration:**

Package-local via @action() decorator in the workflow package's actions.py (generated by workflow_builder_v1). The runner's _resolve_action_fn() (runner_actions.py:108-120) checks package-local actions first before falling back to the global ACTION_REGISTRY.

### Component 2: CLI Hook Commands

**Type:** CLI subcommands in run_agent.py

**Responsibility:** Install and uninstall the post-commit git hook in target repositories.

**New Module:** `agent_runner_v2/codebase_hook_commands.py`

This module follows the pattern established by codebase_init_commands.py. It provides a main() function with argparse-based argument parsing.

**Subcommands:**

| Command | Purpose | Key Behavior |
|---|---|---|
| install-codebase-hook | Install post-commit hook | Validates docs/repo/codebase/current/ structure exists; copies hook script from package to .git/hooks/; idempotent |
| uninstall-codebase-hook | Remove post-commit hook | Removes .git/hooks/post-commit if it is the agent-runner hook; preserves .last_sync_commit; idempotent |

**CLI Flags:**

Both commands support:
- Default: current directory as target repository
- `--repo /path/to/repo`: explicit target repository path

**Hook Script Template:**

The hook script is stored within the agent-runner-v2 package (e.g., `agent_runner_v2/data/hooks/post-commit`) and copied to the target repository's .git/hooks/ directory during installation. The install command marks the hook with a recognizable identifier (e.g., a comment header) so uninstall can distinguish it from user-created hooks.

**Affected Source Files:**

- New file: `agent_runner_v2/codebase_hook_commands.py` (CLI command implementation)
- New file: `agent_runner_v2/data/hooks/post-commit` (hook script template)
- Modified: `agent_runner_v2/run_agent.py` (add if-blocks for install-codebase-hook and uninstall-codebase-hook)

### Component 3: Post-Commit Hook Script

**Type:** Shell script (bash/git-bash compatible)

**Responsibility:** Detect relevant source code changes after a commit and submit the incremental workflow to the backend.

**Hook Script Logic:**

```
1. Get the list of changed files in the current commit (git diff-tree)
2. Filter to relevant file types (*.py, workflow.toml, pyproject.toml, requirements.txt, constants.py)
3. If no relevant changes, exit 0 silently
4. Check for active runs of update_codebase_docs_v1 (via CLI or backend query)
5. If active run exists, log skip and exit 0
6. Submit workflow via: ukbe-run-agent submit --workflow-name update_codebase_docs_v1
7. Log result to .git/codebase-hook.log
8. On failure, emit console warning
```

**CLI Path Resolution Strategy:**

The hook script must resolve the `ukbe-run-agent` CLI binary to submit the workflow. On Windows, the executable is installed via pip as a console script entry point, which may or may not be on the system PATH. The hook uses the following resolution strategy:

1. First, attempt direct invocation: `ukbe-run-agent submit --workflow-name update_codebase_docs_v1`
2. If the CLI is not found on PATH, fall back to: `python -m agent_runner_v2 run_agent submit --workflow-name update_codebase_docs_v1`
3. The install-codebase-hook command may optionally detect the CLI path during installation and embed it in the hook script template as a configurable variable, avoiding runtime PATH resolution.

This strategy ensures the hook works across platforms (Windows Git Bash, Linux, macOS) regardless of whether the CLI is installed as a console script or used via `python -m`.

**Key Properties:**

- Lightweight and non-blocking (NFR-001): The hook performs only detection and submission, not workflow execution. Network call is the only blocking operation.
- Hook identifies itself with a comment header for safe uninstall.
- Hook logs success/failure to .git/codebase-hook.log for auditability.

**Affected Source Files:**

- New file: `agent_runner_v2/data/hooks/post-commit` (shared with Component 2)

## Integration Points

### IP-001: Hook to Backend via CLI

The post-commit hook invokes `ukbe-run-agent submit --workflow-name update_codebase_docs_v1`. The CLI command (submit_commands.py) internally creates a BackendClient and calls submit_run(). The hook does not call any Python API directly.

**Data exchanged:**
- Hook passes: workflow_name (fixed), optionally project-root or context overrides.
- Backend returns: run_id, status.
- Hook logs the result.

### IP-002: Backend to Daemon

The backend queues the submitted run. The daemon polls for work via claim_work() on V2BackendClient. When the daemon claims the run, it spawns a child process that executes the action steps sequentially.

**Data exchanged:**
- Backend provides: workflow definition, step configuration, context variables.
- Daemon reports: step outcomes via report_outcome().

### IP-003: Workflow Steps to codebase_docs.py

The action steps import and call functions from codebase_docs.py:

- build_snapshot(project_root, mode, job_id, step, workflow_name) -- builds a codebase snapshot dict
- render_module_doc(snapshot, module_record) -- renders a single module doc
- render_inventory(snapshot, title) -- renders the inventory file
- render_change_impact(snapshot, title, changed_files, docs_created, docs_updated, stale_docs) -- renders change impact report

These functions are called with the same parameters as the full-scan workflow (sync_codebase_docs.py) to ensure output consistency.

**Important note on build_snapshot():** The build_snapshot() function (codebase_docs.py:762) performs a full repository scan regardless of mode. It iterates ALL files via _iter_repo_files() and scans ALL Python modules via _scan_python_module(). The mode parameter does not filter the scan scope. This means the snapshot build step is O(all files) even for incremental runs. The performance improvement from the incremental approach is achieved through selective render_module_doc() calls for affected modules only, not through reduced snapshot scope. If render_inventory() requires the full snapshot (it iterates snapshot["items"]), this full scan is unavoidable without introducing a separate lighter snapshot builder. See OQ-003 and RISK-006.

### IP-004: Workflow Steps to Git

The detect_changes step uses git diff to compare commits. The commit_and_track step uses git add and git commit. These are invoked via subprocess (consistent with how codebase_docs.py uses subprocess).

### IP-005: Concurrency Check

The hook script (or a helper invoked by the hook) queries the backend for active runs using BackendClient.list_runs() with workflow_name="update_codebase_docs_v1" and status_group="active". If any active runs exist, the hook skips submission.

Note: Since the hook is a shell script, the concurrency check is performed by invoking a CLI command that wraps the list_runs() call. Alternatively, the CLI could be extended with a lightweight check subcommand. The plan assumes the hook calls a CLI helper for this.

### IP-006: CLI Commands to Package Data

The install-codebase-hook command reads the hook script template from the agent-runner-v2 package data directory and writes it to the target repository's .git/hooks/ directory. This requires the hook script to be packaged with the agent-runner-v2 distribution.

## Data Flow

### Workflow Execution Data Flow

```
[Post-commit Hook]
  |
  | git diff-tree (changed files)
  | Filter to relevant types
  | Check concurrency via CLI
  | ukbe-run-agent submit
  v
[Backend API]
  |
  | Queue run for update_codebase_docs_v1
  v
[Daemon Worker]
  |
  | claim_work() -> step: detect_changes
  v
[Step 1: detect_changes]
  | Input: .last_sync_commit (commit hash)
  | Process: git diff <last_sync>..HEAD -> changed files list
  | Filter: *.py, workflow.toml, pyproject.toml, requirements.txt, constants.py
  | Output: changed_files list passed to next step via state
  | Early exit: If .last_sync_commit missing -> exit with message (FR-011)
  | Early exit: If commit unreachable -> exit with message (FR-013)
  | Early exit: If no relevant changes -> exit success (FR-012)
  v
[Step 2: scan_affected_modules]
  | Input: changed_files list
  | Process: Map file paths to module names using codebase_docs.py classification
  | Output: affected_modules list (module_record dicts or module names)
  v
[Step 3: regenerate_docs]
  | Input: affected_modules list, project_root
  | Process:
  |   1. build_snapshot(project_root, mode="incremental", ...)
  |   2. For each affected module: render_module_doc(snapshot, module_record)
  |   3. render_inventory(snapshot, title=repo_name)
  |   4. render_change_impact(snapshot, title=..., changed_files, ...)
  | Output: Written files in docs/repo/codebase/current/
  |   - 02_modules/<affected>.md (regenerated)
  |   - 01_inventory/codebase_inventory.md (regenerated)
  |   - 04_changes/<change_id>.md (new change impact report)
  v
[Step 4: commit_and_track]
  | Input: project_root
  | Process:
  |   1. Get current HEAD commit hash (git rev-parse HEAD)
  |   2. Write hash to docs/repo/codebase/current/.last_sync_commit
  |   3. Update codebase_manifest.json with sync metadata
  |   4. git add docs/repo/codebase/current/ (includes .last_sync_commit)
  |   5. git commit -m "docs: incremental codebase update {job_id}"
  | Output: Git commit with updated documentation and tracking file
  | On failure: .last_sync_commit is not committed, retains previous committed
  |   value. Next run re-detects same changes and retries (FR-017)
  v
[stepCompletion]
  | Mark workflow as complete
  | Runner writes meta.json sidecar automatically
```

### Hook Trigger Data Flow

```
[Developer runs git commit]
  |
  | Git triggers .git/hooks/post-commit
  v
[Post-commit Hook]
  | git diff-tree --no-commit-id --name-only -r HEAD
  | Filter to relevant file patterns
  | If no relevant files -> exit 0
  v
[Concurrency Check]
  | CLI command queries backend for active runs
  | If active run exists -> log skip, exit 0
  v
[Workflow Submission]
  | ukbe-run-agent submit --workflow-name update_codebase_docs_v1
  | Log result to .git/codebase-hook.log
  | If success -> log success, exit 0
  | If failure -> log failure, emit console warning, exit 0
```

Note: The hook always exits 0 to avoid blocking the commit. Submission failure is logged but does not fail the commit (FR-015).

## Risk Assessment

This plan inherits all risks from REQ-20260806-001 and maps them to architectural mitigation strategies.

### RISK-001: Silent Hook Failure When Daemon Not Running

**Architectural Mitigation:** The hook script logs all submission results to .git/codebase-hook.log and emits a console message on failure. The .last_sync_commit file is only updated after successful workflow completion (Step 4), so the next commit will re-trigger the hook. This ensures eventual consistency without silent data loss.

### RISK-002: Concurrent Tracking File Races

**Architectural Mitigation:** The concurrency check in IP-005 prevents duplicate workflow submissions at the backend level. If two commits occur in rapid succession, the second hook invocation finds an active run and skips submission. The .last_sync_commit update is performed atomically within the workflow (Step 4), not by the hook.

### RISK-003: Incremental vs Full-Scan Output Divergence

**Architectural Mitigation:** The incremental workflow uses the same build_snapshot() and render functions as the full-scan workflow. The snapshot is built from the current repository state, not from cached data. The only difference is the module selection filter. If divergence is detected during validation, the user can run sdlc_00_codebase_v1 for a full refresh.

### RISK-004: Auto-Commit Conflict with Branch Protection

**Architectural Mitigation:** The commit_and_track step (Step 4) writes .last_sync_commit and commits it atomically in the same git add + commit operation. If the commit fails, .last_sync_commit is not committed and retains its previous committed value on disk. The updated doc files remain as uncommitted changes in the working tree. On the next commit, the hook re-triggers and the workflow re-runs from the last successful sync point, re-detecting the same changes.

### RISK-005: Backend Workflow Registration Requirement

**Architectural Mitigation:** The plan assumes the backend accepts the update_codebase_docs_v1 workflow name without pre-registration (ASSUMPTION-001). If this assumption fails, the submit command returns a "workflow not found" error (handled by _build_error_payload in submit_commands.py). The hook logs this error. Resolution requires backend workflow registration as a separate prerequisite.

### Additional Risk: Hook Script Portability

**Description:** The hook script must work on Windows (Git Bash), Linux, and macOS. Shell script compatibility may vary.

**Mitigation:** The hook script uses only POSIX-compatible commands (git, which/where for CLI resolution). On Windows, the hook can use a .bat wrapper or Git Bash sh script. The install command detects the platform and installs the appropriate script variant if needed.

### RISK-006: build_snapshot() Full Scan May Undermine Performance Target

**Description:** The build_snapshot() function (codebase_docs.py:762-804) performs a full repository scan (all files, all Python modules) regardless of the mode parameter. This means the snapshot construction step is O(all files) even when only a single file has changed. The performance benefit of the incremental approach comes solely from selective render_module_doc() calls for affected modules, not from snapshot construction. For large repositories, the snapshot build time may dominate total execution time, potentially making the NFR-008 target (less than 50 percent of full-scan time for single-file changes) difficult to achieve.

**Architectural Mitigation:** This is accepted as a known limitation for the initial implementation. The rationale is: (1) CON-001 mandates reuse of existing rendering functions rather than reimplementing scan logic; (2) render_inventory() iterates snapshot["items"], requiring the full snapshot for correct output; (3) the snapshot is built from current repository state (no caching), so correctness is maintained. If NFR-008 testing shows the full-scan bottleneck is significant, the backlog phase should evaluate whether a lighter snapshot builder (scanning only affected modules) can be introduced without breaking render_inventory() consistency. This evaluation is captured in OQ-003.

## Dependencies

### External Dependencies

| ID | Dependency | Source | Status |
|---|---|---|---|
| DEP-001 | codebase_docs.py rendering functions | agent_runner_v2/codebase_docs.py | Verified present |
| DEP-002 | BackendClient.submit_run() and list_runs() | agent_runner_v2/v2/backend_client_v1.py | Verified present |
| DEP-003 | Daemon execution infrastructure | agent_runner_v2/daemon_v2.py | Verified present |
| DEP-004 | Standard docs/repo/codebase/current/ structure | Target repository | Prerequisite |
| DEP-005 | Git repository with .git/hooks/ support | Target repository | Prerequisite |
| DEP-006 | run_agent.py if/elif dispatch pattern | agent_runner_v2/run_agent.py | Verified present |
| DEP-007 | ACTION_REGISTRY dispatch in runner_actions.py | agent_runner_v2/runner_actions.py | Verified present |
| DEP-008 | codebase_init_commands.py CLI pattern | agent_runner_v2/codebase_init_commands.py | Verified present |
| DEP-009 | sync_codebase_docs.py action pattern | agent_runner_v2/actions/sync_codebase_docs.py | Verified present |
| DEP-010 | BackendClient.list_runs() filtering | agent_runner_v2/v2/backend_client_v1.py | Verified present |

### Internal Dependencies (New)

| ID | Dependency | Purpose |
|---|---|---|
| NEW-DEP-001 | Workflow package actions: workflows/update_codebase_docs_v1/actions.py | Action functions for the 4 workflow steps (package-local via @action decorator) |
| NEW-DEP-002 | New CLI module: codebase_hook_commands.py | Install/uninstall hook commands |
| NEW-DEP-003 | Hook script template: data/hooks/post-commit | Packaged hook script for installation |
| NEW-DEP-004 | Workflow package: workflows/update_codebase_docs_v1/ | Workflow manifest and package actions (generated by workflow_builder_v1 from spec) |

### Prerequisites

1. The target repository must have a populated docs/repo/codebase/current/ directory (created by codebase-init or sdlc_00_codebase_v1).
2. The daemon must be running for hook-triggered workflow submissions to be processed.
3. The backend must accept the update_codebase_docs_v1 workflow name for submission.
4. The user must have git commit permissions on the target repository for auto-commit.
5. The workflow spec at docs/repo/workflow_builder/specs/incremental-codebase-update.md must be processed through workflow_builder_v1 to generate the update_codebase_docs_v1 workflow package before the CLI/hook infrastructure can be tested end-to-end.

## Open Questions

### OQ-001: Hook Script Concurrency Check Mechanism

The hook script needs to check for active runs before submitting. Two options exist:
(a) The hook calls a new CLI subcommand (e.g., `ukbe-run-agent check-active-run --workflow-name update_codebase_docs_v1`) that wraps BackendClient.list_runs().
(b) The hook calls `ukbe-run-agent submit` and lets the backend handle duplicate rejection.

The plan currently assumes option (a) for explicit control. The choice affects the hook script design and whether a new CLI subcommand is needed. This should be resolved during the backlog phase.

### OQ-002: commit_and_track Action Implementation

The commit_and_track step merges tracking file update and git commit into a single atomic action. The existing commit_changes action in sdlc_shared_actions.py already stages all of docs/repo/codebase/ and commits — it could be extended to also write .last_sync_commit before staging. Alternatively, a new action function specific to this workflow may be cleaner. The workflow spec (docs/repo/workflow_builder/specs/incremental-codebase-update.md) defines the required behavior. This should be resolved during the backlog phase.

### OQ-003: build_snapshot() Mode Parameter and Full Scan Behavior

The build_snapshot() function accepts a `mode` parameter. The full-scan workflow uses mode="reconcile". The incremental workflow needs to determine the appropriate mode value for incremental operation. However, the mode parameter does NOT affect the scan scope -- build_snapshot() always performs a full repository scan (iterating ALL files via _iter_repo_files() and ALL Python modules via _scan_python_module()). The mode value is stored in the snapshot dict but does not filter what files are scanned.

This creates a known performance limitation: even for single-file changes, the snapshot construction is O(all files). The performance benefit of the incremental approach comes solely from selective render_module_doc() calls for affected modules.

If render_inventory() requires the full snapshot (it iterates snapshot["items"]), then the full scan is unavoidable for correct output. This may make the NFR-008 target (less than 50 percent of full-scan time for single-file changes) difficult to achieve for large repositories.

This should be resolved during the backlog phase. Options include: (a) accept the full scan as a known limitation and validate performance against NFR-008; (b) introduce a lighter snapshot builder for incremental mode that scans only affected modules, if render_inventory() can tolerate partial data; (c) investigate whether snapshot caching is feasible.

### OQ-004: Windows Hook Script Compatibility

The post-commit hook script must work on Windows (where PowerShell is the default shell but Git uses bash for hooks). The plan assumes a bash-compatible shell script works under Git for Windows. If platform-specific variants are needed, the install command must detect the OS and install the appropriate script. This should be verified during implementation.

## Critique Resolution

### Finding 1: build_snapshot() full scan may undermine performance target (Major - V-001)
**Resolution:** Addressed. Updated AD-002 to document the known limitation that build_snapshot() performs a full repository scan regardless of mode parameter. Updated IP-003 to explain the performance implications in detail. Added new risk RISK-006 documenting this as an accepted limitation with architectural mitigation rationale. Updated OQ-003 to reflect the verified behavior (mode does not filter scan scope) and enumerate the resolution options for the backlog phase. The plan now clearly states that the performance benefit comes from selective render_module_doc() calls, not from snapshot construction.
**Affected section:** AD-002, IP-003, OQ-003, RISK-006 (new), Risk Assessment

### Finding 2: Open questions are well-scoped (Minor - D-001, Informational)
**Resolution:** No change needed. The critique confirms the four open questions (OQ-001 through OQ-004) are appropriate for backlog-phase resolution. This finding is informational only and requires no plan revision.
**Affected section:** None

### Finding 3: Hook CLI path resolution on Windows not formalized (Minor - T-001)
**Resolution:** Addressed. Added a "CLI Path Resolution Strategy" subsection to Component 3 (Post-Commit Hook Script) documenting the three-tier resolution approach: (1) direct invocation via PATH, (2) fallback to `python -m agent_runner_v2`, (3) optional install-time CLI path detection and embedding in the hook template. This formalizes the path resolution strategy that was previously only mentioned in the portability risk mitigation.
**Affected section:** Component 3: Post-Commit Hook Script

### Finding 4: Action registration strategy ambiguity (Minor - T-002)
**Resolution:** Addressed. Chose package-local @action() decorator registration as the sole strategy for this workflow's actions. Removed the dual-registration approach (both global ACTION_REGISTRY and package-local). Updated the "Action Registration" section to clearly state package-local registration via @action() decorator in workflows/update_codebase_docs_v1/actions.py. Updated the "Affected Source Files" list to remove the global action module (incremental_codebase_update.py) and the modification to runner_actions.py. Updated the internal dependencies table (NEW-DEP-001) to reference the workflow package actions. Updated NFR-005 traceability entry and the architectural pattern description to reflect the chosen approach.
**Affected section:** Plan Overview, Architectural Pattern (execution layer), Action Registration, Affected Source Files, Internal Dependencies, NFR-005 traceability
