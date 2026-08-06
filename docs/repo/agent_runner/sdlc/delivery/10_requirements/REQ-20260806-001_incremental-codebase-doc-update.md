---
template_id: "SYS-03-RQ"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "structured requirements derived from approved initiative"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "Approved"
effective_version: "SDLC10REQ-f4pti3uv"
managed_by: "workflow-generated"
source_document: "INIT-20260806-001_incremental-codebase-doc-update.md"
---

# Requirements: Incremental Codebase Documentation Updates with Git Hook Automation

## Document Metadata

- Document ID: REQ-20260806-001
- Source initiative: INIT-20260806-001_incremental-codebase-doc-update.md
- Date of generation: 2026-08-06
- Producing workflow: sdlc_20_planning_v1
- Producing agent: Workflow Architect

# Requirements Overview

This document specifies the structured requirements for implementing incremental codebase documentation updates with git hook automation in the agent-runner-v2 platform. The requirements are derived from approved initiative INIT-20260806-001 (Incremental Codebase Documentation Updates with Git Hook Automation).

## Initiative Summary

The current sdlc_00_codebase_v1 workflow performs full-repository scans on every run, processing all 141+ module documentation files regardless of how many source files actually changed. This initiative requires replacing the full-scan model (for routine updates) with a targeted, change-aware incremental regeneration approach that keeps module-level docs synchronized with source code after each commit, while preserving the full-scan workflow for initial setup and periodic refresh.

## Solution Deliverables Summary

The solution must deliver five primary capabilities:

1. A reusable incremental documentation update workflow (update_codebase_docs_v1) that regenerates only module docs affected by recent source code changes.
2. Two CLI subcommands (install-codebase-hook, uninstall-codebase-hook) for git hook lifecycle management in run_agent.py.
3. A post-commit git hook script that automatically triggers the incremental workflow after relevant commits.
4. A commit tracking mechanism (.last_sync_commit) to determine changed source files between documentation updates.
5. Automatic git commit of updated documentation files after successful regeneration.

The solution must operate across any agent-runner-v2 enabled repository that follows the standard docs/repo/codebase/ directory structure, reuse existing rendering functions from codebase_docs.py, and integrate with the existing backend/daemon execution infrastructure.

## Codebase Context

The agent-runner-v2 codebase manifest (codebase_manifest.json) tracks 140 module documentation entries under docs/repo/codebase/current/. The current full-scan workflow generates documentation for all modules on each run. The existing codebase_docs.py module provides the core rendering functions (build_snapshot, render_module_doc, render_inventory, render_change_impact, render_component_doc) that the incremental workflow must reuse where applicable.

# Functional Requirements

## FR-001: Incremental Documentation Update Workflow

The system shall provide a reusable workflow named update_codebase_docs_v1 that performs incremental documentation updates in any agent-runner-v2 enabled repository. The workflow must be action-only (no LLM involvement) and repo-agnostic.

Priority: must-have

Acceptance criteria: The workflow executes successfully in any agent-runner-v2 enabled repository with the standard docs/repo/codebase/current/ structure. No LLM calls are made during execution.

Traceability: IN-001, Expected Outcome 1

## FR-002: Changed File Detection

The workflow shall determine which source files have changed since the last documentation update by comparing the commit hash stored in .last_sync_commit against the current HEAD using git diff.

Priority: must-have

Acceptance criteria: The workflow correctly identifies all changed files between the stored commit hash and HEAD. Only files matching the relevant file type filter (*.py, workflow.toml, pyproject.toml, requirements.txt, constants.py) are included.

Traceability: IN-007, ASSUMPTION-004

## FR-003: Selective Module Regeneration

The workflow shall regenerate documentation artifacts for modules and supporting structures affected by changed source files. The output categories are:

1. Module documentation files in docs/repo/codebase/current/02_modules/ for affected modules, using render_module_doc().
2. The codebase inventory file (codebase_inventory.md in 01_inventory/) using render_inventory().
3. A change impact report (in 04_changes/) using render_change_impact().
4. The codebase manifest (codebase_manifest.json) updated with new sync metadata.

The workflow must reuse build_snapshot(), render_module_doc(), render_inventory(), and render_change_impact() functions from codebase_docs.py. Component documents (03_components/) are not regenerated during incremental updates; they remain the responsibility of the full-scan workflow (see OUT-002a).

Priority: must-have

Acceptance criteria: After an incremental run, only module docs for affected modules are regenerated in 02_modules/. The inventory file and change impact report are regenerated. The codebase manifest is updated. Component documents remain unchanged.

Traceability: IN-001, CON-001, DEP-001, DEP-009

## FR-004: Install Git Hook CLI Command

The system shall provide an install-codebase-hook CLI subcommand in run_agent.py that installs a post-commit git hook in a target repository. The command must verify that the target repository has the standard docs/repo/codebase/current/ directory structure before installing the hook.

Priority: must-have

Acceptance criteria: Running install-codebase-hook in a repository with the standard structure installs a working post-commit hook. Running it in a repository without the standard structure produces a clear error message.

Traceability: IN-002, CON-005

## FR-005: Uninstall Git Hook CLI Command

The system shall provide an uninstall-codebase-hook CLI subcommand in run_agent.py that cleanly removes the post-commit git hook from a target repository. The command must preserve the .last_sync_commit tracking file.

Priority: must-have

Acceptance criteria: Running uninstall-codebase-hook removes the hook script. The .last_sync_commit file is preserved. Other repository state is unaffected.

Traceability: IN-003, BC-005

## FR-006: CLI Repository Targeting

Both CLI commands shall support a default current-directory behavior and an explicit --repo /path/to/repo flag for specifying a target repository.

Priority: must-have

Acceptance criteria: Both install and uninstall commands work correctly with the default (current directory) and with --repo flag.

Traceability: IN-004

## FR-007: Post-Commit Git Hook Script

The system shall provide a post-commit git hook script that detects whether the commit includes relevant source code file changes (*.py, workflow.toml, pyproject.toml, requirements.txt, constants.py) and, if so, submits the update_codebase_docs_v1 workflow to the backend for execution.

Priority: must-have

Acceptance criteria: After a commit that includes relevant file changes, the hook triggers workflow submission. After a commit with only irrelevant changes (docs/, tests/, *.md, *.json), no submission occurs.

Traceability: IN-005, BC-002

## FR-008: Backend Workflow Submission

The git hook shall submit the workflow to the backend by invoking a CLI command (ukbe-run-agent submit or equivalent) that internally uses BackendClient.submit_run() from agent_runner_v2/v2/backend_client_v1.py. The hook script itself is a shell script and must not implement workflow execution logic. The hook must resolve the backend URL from the runner configuration (~/.ukbe-runner/config.json).

Priority: must-have

Acceptance criteria: The hook successfully submits the workflow via the CLI command. The BackendClient.submit_run() API is used internally by the CLI command, not called directly from the shell script.

Traceability: IN-006, ASSUMPTION-003, DEP-002

## FR-009: Tracking File Management

The system shall maintain a .last_sync_commit tracking file that stores a single commit hash (the HEAD at the time of the last successful documentation sync). The tracking file must be updated only after successful workflow completion.

Priority: must-have

Acceptance criteria: After a successful incremental run, .last_sync_commit contains the current HEAD hash. After a failed run, .last_sync_commit retains its previous value.

Traceability: IN-007, ASSUMPTION-004

## FR-010: Automatic Documentation Commit

The workflow shall automatically commit updated documentation files to the repository after successful incremental regeneration, without manual intervention.

Priority: should-have

Acceptance criteria: Updated docs are committed with a descriptive commit message (e.g., "docs: incremental codebase update {job_id}"). No manual git operations are required.

Traceability: IN-008

## FR-011: Missing Tracking File Handling

When the .last_sync_commit tracking file is absent (first run), the workflow shall exit with a clear message directing the user to run sdlc_00_codebase_v1 first. The workflow shall not attempt a full scan.

Priority: must-have

Acceptance criteria: With no .last_sync_commit file, the workflow exits with a message directing the user to run sdlc_00_codebase_v1. No documentation regeneration is attempted.

Traceability: BC-003, SC-009

## FR-012: No Relevant Changes Handling

When no relevant file changes are detected between the last sync commit and HEAD, the workflow shall exit successfully without regenerating any documentation.

Priority: must-have

Acceptance criteria: With no relevant changes, the workflow exits with status 0 and produces no file changes.

Traceability: BC-004, SC-009

## FR-013: Unreachable Tracking Commit Handling

When the commit hash stored in .last_sync_commit is no longer reachable (e.g., after a rebase or force-push), the workflow shall treat this as equivalent to a missing tracking file and exit with a message directing the user to run sdlc_00_codebase_v1 to re-establish the baseline.

Priority: must-have

Acceptance criteria: With an unreachable commit hash, the workflow exits with a message directing the user to run sdlc_00_codebase_v1. No documentation regeneration is attempted.

Traceability: BC-007, SC-009

## FR-014: Missing Documentation Structure Handling

When the target repository lacks the standard docs/repo/codebase/current/ directory structure, the system shall produce a clear, actionable error message directing the user to run codebase-init.

Priority: must-have

Acceptance criteria: Without the standard directory structure, both the workflow and the install command produce a message directing the user to run codebase-init.

Traceability: BC-001, SC-009

## FR-015: Hook Logging on Failure

When the git hook fails to submit the workflow (e.g., daemon not running, backend unreachable), the hook shall log the submission result (success/failure) to a known file (e.g., .git/codebase-hook.log) and emit a console message on failure.

Priority: must-have

Acceptance criteria: On submission failure, a message is written to .git/codebase-hook.log and a console warning is displayed. On success, the log file records the success.

Traceability: RISK-001, SC-009

## FR-016: Concurrent Execution Prevention

The hook shall query the backend for active runs of update_codebase_docs_v1 before submitting. The hook shall use BackendClient.list_runs() (agent_runner_v2/v2/backend_client_v1.py) with workflow_name and status_group filters to check for active runs. If an incremental update is already running, subsequent hook triggers shall skip submission rather than queue or fail.

Priority: should-have

Acceptance criteria: When a workflow run is already active, a subsequent hook trigger does not submit a duplicate run. The skip is logged.

Traceability: CON-004, SC-008

## FR-017: Auto-Commit Failure Handling

When auto-commit of documentation files fails due to branch protection rules or pre-commit hooks, the workflow shall log the updated files as uncommitted changes and exit with a non-zero status. The hook shall emit a warning message.

Priority: should-have

Acceptance criteria: On auto-commit failure, the updated files remain as uncommitted changes in the working tree. The hook emits a warning. The .last_sync_commit file is not updated.

Traceability: RISK-004, ASSUMPTION-006

## FR-018: Codebase Manifest Update

The workflow shall update codebase_manifest.json with new sync metadata after a successful incremental regeneration. The manifest update shall include the current HEAD commit hash and the timestamp of the incremental sync. This corresponds to Step 4 (update_manifest) in the workflow spec.

Priority: must-have

Acceptance criteria: After a successful incremental run, codebase_manifest.json reflects the new sync commit hash and timestamp. The manifest remains valid JSON.

Traceability: IN-001, Workflow Spec Step 4

# Non-Functional Requirements

## NFR-001: Lightweight Non-Blocking Hook

The post-commit git hook must be lightweight and non-blocking. It must not delay or block the commit operation with heavy processing. Hook execution shall be limited to submission only, not waiting for workflow completion. Hook execution (excluding network latency for the backend call) shall complete within 2 seconds of local processing time.

Category: performance, usability

Traceability: CON-003

## NFR-002: CLI Command Idempotency

Both install-codebase-hook and uninstall-codebase-hook commands must be idempotent. Running the same command multiple times must produce the same result without errors or side effects.

Category: usability, reliability

Traceability: CON-006, SC-010

## NFR-003: Concurrent Execution Safety

The system must handle concurrent execution gracefully. If an incremental update is already running, subsequent hook triggers must not cause duplicate or conflicting workflow executions. The concurrency check must operate at the backend level.

Category: reliability, concurrency

Traceability: CON-004, SC-008, RISK-002

## NFR-004: Existing Function Reuse

The incremental workflow must reuse existing functions from codebase_docs.py (build_snapshot(), render_module_doc(), render_inventory(), render_change_impact()) rather than reimplementing scan and render logic.

Category: maintainability

Traceability: CON-001, DEP-001

## NFR-005: Layer 2 Action Step Compliance

The incremental workflow must follow the Layer 2 runtime model for action steps. All steps must be action-type steps that execute Python functions via the runner_actions.py ACTION_REGISTRY dispatch mechanism or the workflow package @action() decorator.

Category: compliance

Traceability: CON-007

## NFR-006: Standard Sidecar Production

The workflow must produce its own meta.json sidecar through the standard action-step mechanism (runner writes sidecar from ActionResult), consistent with the Layer 2 step model.

Category: compliance

Traceability: CON-008

## NFR-007: Hook Script Packaging

The hook script must be stored within the agent-runner-v2 package and copied to the target repository's .git/hooks/ directory during installation.

Category: packaging, deployability

Traceability: CON-009

## NFR-008: Performance Efficiency

Incremental workflow execution time must be measurably less than full-scan execution time for typical commits (1-5 files changed). The target is less than 50 percent of full-scan time for single-file changes.

Category: performance

Traceability: SC-007, Expected Outcome 5

## NFR-009: Repo-Agnostic Design

The workflow must operate in any agent-runner-v2 enabled repository that follows the standard docs/repo/codebase/ directory structure, without hardcoding repository-specific paths or assumptions.

Category: portability

Traceability: IN-001, BC-001

## NFR-010: CLI Pattern Consistency

The new CLI commands shall follow the existing pattern used by codebase-init in run_agent.py. The run_agent.py module uses if/elif command dispatch in its parse_args() function, which is an established convention specific to that module. Note: AGENTS.md prohibits if/elif chains for dispatch in coder_adapters.py (which uses CODER_REGISTRY instead), but run_agent.py CLI dispatch is a known exception to that general coding standard.

Category: consistency, maintainability

Traceability: DEP-006, DEP-008

# Scope Definition

## In Scope

- IN-001: Design and implement the update_codebase_docs_v1 workflow as an action-only workflow (no LLM involvement) for incremental documentation updates. The workflow must be repo-agnostic and work in any agent-runner-v2 enabled repository.
- IN-002: Implement the install-codebase-hook CLI subcommand in run_agent.py to install a post-commit git hook in any target repository.
- IN-003: Implement the uninstall-codebase-hook CLI subcommand in run_agent.py to cleanly remove the post-commit git hook from any target repository.
- IN-004: CLI commands support both current directory (default behavior) and an explicit --repo /path/to/repo flag for specifying a target repository.
- IN-005: Post-commit git hook script that detects source code changes and submits the update_codebase_docs_v1 workflow to the backend for execution.
- IN-006: Integration between the git hook, the backend API for workflow submission, and the daemon execution infrastructure.
- IN-007: A tracking mechanism (using a .last_sync_commit file) to determine what source files have changed since the last documentation update.
- IN-008: Automatic git commit of updated documentation files after successful incremental regeneration.
- IN-009: Error handling for edge cases including: no relevant changes since last sync, first run with no tracking file, concurrent workflow execution, missing standard documentation structure, and invalid tracking commit hash (e.g., after rebase or force-push).

## Out of Scope

- OUT-001: Modifications to the existing sdlc_00_codebase_v1 full-scan workflow. The full-scan workflow remains unchanged.
- OUT-002: Changes to the codebase documentation format, template structure, or rendering conventions.
- OUT-002a: Regeneration of component documents (03_components/) during incremental updates. Component documents aggregate cross-module data and are not suitable for incremental regeneration based on single-commit file-level diffs. They remain the responsibility of the full-scan workflow (sdlc_00_codebase_v1). The render_component_doc() function in codebase_docs.py is available but not invoked by the incremental workflow.
- OUT-003: Support for repositories that do not follow the standard agent-runner-v2 docs/repo/codebase/ structure.
- OUT-004: Real-time or continuous documentation updates during development. Batch-per-commit is the intended granularity.
- OUT-005: Architecture decisions for backend API changes or daemon behavior modifications. Any required backend changes are assumed to be within existing API capabilities.
- OUT-006: Testing strategy and test implementation. Test planning belongs to subsequent SDLC workflow steps (planning, backlog, task).

## Boundary Conditions

- BC-001: The incremental workflow operates only on repositories that already have a populated docs/repo/codebase/current/ directory (created by codebase-init or sdlc_00_codebase_v1).
- BC-002: The git hook triggers only on commits that include relevant file types (*.py, workflow.toml, pyproject.toml, requirements.txt, constants.py). Changes to docs/, tests/, *.md, *.json, or generated files do not trigger updates.
- BC-003: If the .last_sync_commit tracking file is absent (first run), the workflow exits with a clear message directing the user to run sdlc_00_codebase_v1 first.
- BC-004: If no relevant file changes are detected between the last sync commit and HEAD, the workflow exits successfully without regenerating any documentation.
- BC-005: The uninstall-codebase-hook command removes the hook script but preserves the .last_sync_commit tracking file, in case the user re-installs the hook later.
- BC-006: The incremental workflow is complementary to sdlc_00_codebase_v1. The full-scan workflow remains the authoritative mechanism for initial setup, major refactoring, and periodic comprehensive refresh.
- BC-007: If the commit hash stored in .last_sync_commit is no longer reachable (e.g., after a rebase or force-push), the workflow treats this as equivalent to BC-003 (missing tracking file) and exits with a message directing the user to run sdlc_00_codebase_v1 to re-establish the baseline.

## Assumptions

- ASSUMPTION-001: The existing BackendClient.submit_run() API in backend_client_v1.py can accept the new update_codebase_docs_v1 workflow name without backend modifications. If the backend requires workflow registration, that is a separate concern outside this initiative scope.
- ASSUMPTION-002: The workflow spec at docs/repo/workflow_builder/specs/incremental-codebase-update.md represents the intended design. The initiative scope aligns with that spec.
- ASSUMPTION-003: The post-commit hook script will use the existing submit mechanism (ukbe-run-agent submit or equivalent CLI command) to submit the workflow to the backend. The hook itself does not implement workflow execution logic. The CLI command internally uses BackendClient.submit_run().
- ASSUMPTION-004: The .last_sync_commit tracking file stores a single commit hash (the HEAD at the time of the last successful documentation sync). The workflow uses git diff to determine changed files between that hash and the current HEAD.
- ASSUMPTION-005: The daemon must be running for the git hook submission to be processed. If the daemon is not running, the hook submission may fail or queue depending on backend configuration. See RISK-001 for mitigation approach. The initiative does not include daemon auto-start functionality.
- ASSUMPTION-006: Auto-commit of documentation files (IN-008) operates on repositories where branch protection rules permit direct commits to the working branch. If branch protection prevents auto-commit, the hook will log the updated files as uncommitted changes and exit with a warning. See RISK-004 for details.

# Acceptance Criteria

## AC-001: Incremental Output Correctness

The update_codebase_docs_v1 workflow shall successfully regenerate only the affected module documentation files and supporting artifacts (inventory, change impact, manifest) in any agent-runner-v2 enabled repository. Module docs produced by incremental update shall be structurally identical to module docs produced by full-scan when both operate on the same codebase state, excluding timestamps and ordering variations. Comparison shall be performed at the structural level (section headings, content blocks, code references) rather than byte-for-byte, to accommodate non-deterministic elements such as generation timestamps.

Traceability: SC-001, FR-001, FR-003

## AC-002: Hook Installation

The install-codebase-hook command shall install a working post-commit git hook in any repository that has the standard docs/repo/codebase/current/ structure. Verified by making a test commit and confirming the hook triggers.

Traceability: SC-002, FR-004

## AC-003: Clean Hook Removal

The uninstall-codebase-hook command shall cleanly remove the post-commit git hook without affecting the .last_sync_commit tracking file or any other repository state.

Traceability: SC-003, FR-005

## AC-004: CLI Targeting Modes

Both CLI commands shall work correctly with the default current-directory behavior and with the --repo /path/to/repo flag.

Traceability: SC-004, FR-006

## AC-005: Automatic Hook Triggering

The git hook shall trigger the incremental workflow automatically after commits that include source code changes (*.py, workflow.toml, etc.).

Traceability: SC-005, FR-007

## AC-006: Automatic Documentation Commit

Updated documentation files shall be committed automatically to the repository without manual intervention after a successful incremental update.

Traceability: SC-006, FR-010

## AC-007: Performance Improvement

Incremental workflow execution time shall be measurably less than full-scan execution time for typical commits (1-5 files changed). Target: less than 50 percent of full-scan time for single-file changes.

Traceability: SC-007, NFR-008

## AC-008: No Duplicate Executions

No duplicate or concurrent workflow executions shall occur when the hook is triggered multiple times in rapid succession.

Traceability: SC-008, FR-016, NFR-003

## AC-009: Actionable Error Messages

Clear, actionable error messages shall be produced when: (a) the .last_sync_commit tracking file is missing (directs user to run sdlc_00_codebase_v1), (b) the docs/repo/codebase/current/ structure is absent (directs user to run codebase-init), (c) no relevant changes are detected (silent success), (d) the stored commit hash is unreachable (directs user to run sdlc_00_codebase_v1).

Traceability: SC-009, FR-011, FR-012, FR-013, FR-014, FR-015

## AC-010: Idempotent Installation

Hook installation shall be idempotent. Running install-codebase-hook multiple times shall produce no errors and leave exactly one hook script in place.

Traceability: SC-010, NFR-002

## AC-011: Manifest Update Correctness

After a successful incremental run, codebase_manifest.json shall reflect the new sync commit hash and timestamp, and remain valid JSON.

Traceability: FR-018

# Dependencies and Constraints

## External Dependencies

- DEP-001: The codebase_docs.py module (agent_runner_v2/codebase_docs.py) must provide the following public functions: build_snapshot(), render_module_doc(), render_inventory(), render_change_impact(). Verified present in current codebase. Note: render_component_doc() also exists but is excluded from incremental workflow scope per OUT-002a.
- DEP-002: The existing backend API (BackendClient in agent_runner_v2/v2/backend_client_v1.py) must support workflow submission via submit_run() and step claiming via claim_step(). The daemon polling uses claim_work() on V2BackendClient (agent_runner_v2/v2/backend_client.py). Verified present in current codebase.
- DEP-003: The existing daemon infrastructure (daemon_v2.py) must be capable of executing the new update_codebase_docs_v1 workflow using the standard action-step execution path. Verified present in current codebase.
- DEP-004: The standard docs/repo/codebase/current/ directory structure must exist in the target repository, populated by a prior run of codebase-init or sdlc_00_codebase_v1. This structure includes: 01_inventory/, 02_modules/, 03_components/, 04_changes/, and codebase_manifest.json.
- DEP-005: The target repository must be a git repository with post-commit hook support (standard .git/hooks/ directory).
- DEP-006: The run_agent.py CLI module uses if/elif command dispatch in its parse_args() function (not argparse subparsers). New subcommands are added as new if-blocks following the existing pattern used by codebase-init. Verified present in current codebase.
- DEP-007: The runner_actions.py module supports dispatching custom action functions registered via the ACTION_REGISTRY dictionary (runner_actions.py lines 42-56). New global actions are added by importing the function and adding it to ACTION_REGISTRY. Workflow package actions use the @action() decorator for package-local registration. Verified present in current codebase.
- DEP-008: The codebase_init_commands.py module provides a pattern for CLI command structure (argparse-based main() function) that the new hook commands should follow. Verified present in current codebase.
- DEP-009: The existing sync_codebase_docs action (agent_runner_v2/actions/sync_codebase_docs.py) already calls build_snapshot(), render_module_doc(), render_inventory(), and render_change_impact() for the full-scan workflow. The incremental workflow will reuse these same rendering functions from codebase_docs.py, adding only change-detection and selective-regeneration logic. It does not duplicate or fork the existing action.
- DEP-010: BackendClient.list_runs() (agent_runner_v2/v2/backend_client_v1.py) supports filtering by workflow_name and status_group, enabling the concurrency check required by FR-016. Verified present in current codebase.

## Technical Constraints

- CON-001: The incremental workflow must reuse existing functions from codebase_docs.py (build_snapshot(), render_module_doc(), render_inventory(), render_change_impact()) rather than reimplementing scan and render logic.
- CON-002: The workflow must integrate with the existing backend/daemon architecture. Workflow submission uses the existing BackendClient.submit_run() API (agent_runner_v2/v2/backend_client_v1.py), and execution follows the standard daemon claim-execute-complete lifecycle using claim_work() (V2BackendClient in agent_runner_v2/v2/backend_client.py).
- CON-003: The git hook must be lightweight and non-blocking. It cannot delay or block the commit operation with heavy processing. Hook execution time should be minimal (submission only, not waiting for workflow completion).
- CON-004: The workflow must handle concurrent execution gracefully. If an incremental update is already running, subsequent hook triggers must skip submission rather than queue or fail. The hook should query the backend for active runs of update_codebase_docs_v1 before submitting.
- CON-005: The install-codebase-hook command must verify that the target repository has the standard docs/repo/codebase/current/ directory structure before installing the hook.
- CON-006: Both CLI commands (install and uninstall) must be idempotent. Running the same command multiple times must produce the same result without errors or side effects.
- CON-007: The incremental workflow must follow the Layer 2 runtime model for action steps. All steps are action-type steps that execute Python functions via the runner_actions.py ACTION_REGISTRY dispatch mechanism or the workflow package @action() decorator.
- CON-008: The workflow must produce its own meta.json sidecar through the standard action-step mechanism (runner writes sidecar from ActionResult), consistent with the Layer 2 step model.
- CON-009: The hook script must be stored within the agent-runner-v2 package and copied to the target repository's .git/hooks/ directory during installation.
- CON-010: The incremental workflow complements sdlc_00_codebase_v1 and does not replace it. The full-scan workflow must still be used for initial setup, major refactoring, or periodic comprehensive refresh.

# Risk Assessment

## RISK-001: Silent Hook Failure When Daemon Not Running

Description: The git hook may fail silently if the daemon is not running. The hook submits the workflow via the backend API, and if the backend is unreachable, the submission fails. Without explicit feedback, the developer may not realize the documentation was not updated.

Probability: Medium

Impact: Medium

Mitigation: The hook script shall log submission results (success/failure) to a known file (e.g., .git/codebase-hook.log) and emit a console message on failure so the developer is aware. The .last_sync_commit file is only updated after successful workflow completion, so the next commit will re-trigger. Addressed by FR-015 and AC-009.

## RISK-002: Concurrent Tracking File Races

Description: Concurrent hook triggers on rapid commits could race on the .last_sync_commit file. If two commits occur in quick succession and both trigger the workflow, the .last_sync_commit update from the first workflow may conflict with the second workflow's change detection.

Probability: Low

Impact: Medium

Mitigation: Use file-based locking (atomic write with a lock file) for .last_sync_commit updates. The concurrency check in CON-004 prevents duplicate workflow submissions at the backend level. Addressed by NFR-003, AC-008.

## RISK-003: Incremental vs Full-Scan Output Divergence

Description: Incremental regeneration may produce different output than a full scan for the same module if the build_snapshot() context is incomplete (e.g., cross-module dependencies not captured by file-level diff).

Probability: Low

Impact: Medium

Mitigation: AC-001 requires comparison of incremental output against full-scan output for the same changes. If divergence is detected, the developer should be directed to run sdlc_00_codebase_v1 for a full refresh. The .last_sync_commit tracking allows re-sync to a known-good state.

## RISK-004: Auto-Commit Conflict with Branch Protection

Description: Auto-commit of documentation (IN-008) may conflict with branch protection rules or pre-commit hooks in some repositories. If the target repository has branch protection that prevents direct commits, the auto-commit step will fail.

Probability: Medium

Impact: Low

Mitigation: If auto-commit fails due to branch protection, the workflow shall log the updated files as uncommitted changes and exit with a non-zero status. The hook shall emit a warning message. This is documented in ASSUMPTION-006 and addressed by FR-017.

## RISK-005: Backend Workflow Registration Requirement

Description: The existing BackendClient.submit_run() API may require the workflow name to be pre-registered in the backend before submission. If the backend does not automatically accept unknown workflow names, the update_codebase_docs_v1 workflow may need to be registered separately.

Probability: Medium

Impact: High

Mitigation: ASSUMPTION-001 states this is assumed to work without backend modifications. If it does not, backend registration becomes a prerequisite dependency that must be resolved before the incremental workflow can be submitted. This is acknowledged in the initiative as a separate concern outside its scope.

# Traceability Matrix

## Initiative Scope to Requirements

| Initiative Item | Requirement Coverage |
|---|---|
| IN-001 (incremental workflow) | FR-001, FR-003, FR-009, FR-010, FR-011, FR-012, FR-018 |
| IN-002 (install hook CLI) | FR-004, FR-006 |
| IN-003 (uninstall hook CLI) | FR-005 |
| IN-004 (CLI targeting) | FR-006 |
| IN-005 (hook script) | FR-007 |
| IN-006 (backend integration) | FR-008 |
| IN-007 (tracking mechanism) | FR-002, FR-009 |
| IN-008 (auto-commit) | FR-010, FR-017 |
| IN-009 (error handling) | FR-011, FR-012, FR-013, FR-014, FR-015 |

## Boundary Conditions to Requirements

| BC Item | Requirement Coverage |
|---|---|
| BC-001 | FR-014, DEP-004 |
| BC-002 | FR-007 |
| BC-003 | FR-011 |
| BC-004 | FR-012 |
| BC-005 | FR-005 |
| BC-006 | FR-001, NFR-004 |
| BC-007 | FR-013 |

## Success Criteria to Acceptance Criteria

| SC Item | AC Coverage |
|---|---|
| SC-001 | AC-001 |
| SC-002 | AC-002 |
| SC-003 | AC-003 |
| SC-004 | AC-004 |
| SC-005 | AC-005 |
| SC-006 | AC-006 |
| SC-007 | AC-007, NFR-008 |
| SC-008 | AC-008, NFR-003 |
| SC-009 | AC-009 |
| SC-010 | AC-010, NFR-002 |

## Risk Coverage

| Risk | Requirement Coverage |
|---|---|
| RISK-001 (silent hook failure) | FR-015, AC-009 |
| RISK-002 (concurrent races) | NFR-003, AC-008 |
| RISK-003 (output divergence) | AC-001 |
| RISK-004 (branch protection) | FR-017, ASSUMPTION-006 |
| RISK-005 (backend registration) | ASSUMPTION-001 |

## Workflow Spec Coverage

| Spec Element | Requirement Coverage |
|---|---|
| Step 1: detect_changes | FR-002, FR-007, FR-011, FR-012, FR-013 |
| Step 2: scan_affected_modules | FR-003, FR-002 |
| Step 3: regenerate_docs | FR-003 |
| Step 4: update_manifest | FR-009, FR-018 |
| Step 5: commit_changes | FR-010, FR-017 |
| Output: UPDATED_MODULE_DOCS | FR-003 |
| Output: UPDATED_INVENTORY | FR-003 |
| Output: UPDATED_CHANGE_IMPACT | FR-003 |
| Output: UPDATED_MANIFEST | FR-018 |

# Open Questions

None at this time. All identified ambiguities from the initiative have been resolved through the boundary conditions and assumptions documented above.

# Critique Resolution

### Finding 1: template_id is wrong (SYS-03-REQ instead of SYS-03-RQ)
**Resolution:** Fixed. Changed template_id from "SYS-03-REQ" to "SYS-03-RQ" in the YAML frontmatter to match the required value from 03_REQ_template.md.
**Affected section:** YAML frontmatter

### Finding 2: Missing required template sections (Title, Document Metadata, Traceability Matrix, Open Questions, Source Reference)
**Resolution:** Fixed. Added all five missing sections: (1) Document title as H1 heading at the top. (2) Document Metadata section with Document ID, source initiative, date, producing workflow, and producing agent. (3) Traceability Matrix section with formal tables mapping initiative items, boundary conditions, success criteria, risks, and workflow spec elements to requirements. (4) Open Questions section (currently empty, none identified). (5) Source Reference section at the end cross-referencing the source initiative.
**Affected section:** Title, Document Metadata, Traceability Matrix, Open Questions, Source Reference (all new sections)

### Finding 3: FR-003 scope is internally inconsistent (limits to 02_modules/ but names functions producing outputs elsewhere)
**Resolution:** Fixed. Expanded FR-003 to explicitly list all four output categories: module docs (02_modules/), inventory (01_inventory/), change impact report (04_changes/), and manifest (codebase_manifest.json). Removed the contradictory "only" qualifier that previously limited scope to 02_modules/.
**Affected section:** FR-003, AC-001 (updated to reflect expanded scope), Workflow Spec Coverage table (updated from PARTIAL/GAP to COVERED)

### Finding 4: No requirement covers codebase_manifest.json update
**Resolution:** Fixed. Added FR-018 explicitly requiring codebase_manifest.json update with new sync metadata (commit hash and timestamp) after successful incremental regeneration. Added AC-011 for verification.
**Affected section:** Functional Requirements (FR-018), Acceptance Criteria (AC-011), Traceability Matrix (IN-001 coverage, Workflow Spec Step 4)

### Finding 5: No MoSCoW priority on any functional requirement
**Resolution:** Fixed. Added Priority field to every functional requirement (FR-001 through FR-018). Classifications: FR-001 through FR-009, FR-011 through FR-015, FR-018 as must-have; FR-010, FR-016, FR-017 as should-have.
**Affected section:** All Functional Requirements (FR-001 through FR-018)

### Finding 6: No NFR category on any non-functional requirement
**Resolution:** Fixed. Added Category field to every non-functional requirement (NFR-001 through NFR-010) with appropriate classifications (performance, usability, reliability, concurrency, maintainability, compliance, packaging, deployability, portability, consistency).
**Affected section:** All Non-Functional Requirements (NFR-001 through NFR-010)

### Finding 7: Individual FRs lack per-requirement acceptance criteria
**Resolution:** Fixed. Added an "Acceptance criteria" field to each functional requirement (FR-001 through FR-018) describing the specific verifiable condition for that requirement. The separate AC section (AC-001 through AC-011) is preserved for consolidated cross-referencing.
**Affected section:** All Functional Requirements (FR-001 through FR-018)

### Finding 8: FR-008 misidentifies the calling mechanism (shell script cannot call Python API directly)
**Resolution:** Fixed. Rewrote FR-008 to clarify that the hook invokes a CLI command (ukbe-run-agent submit or equivalent) that internally uses BackendClient.submit_run(). Aligned FR-008 with ASSUMPTION-003. Updated ASSUMPTION-003 to explicitly state that the CLI command internally uses BackendClient.submit_run().
**Affected section:** FR-008, ASSUMPTION-003

### Finding 9: render_component_doc() omitted from function reuse list
**Resolution:** Fixed. Added OUT-002a explicitly stating that component document regeneration is out of scope for incremental updates, with rationale (component docs aggregate cross-module data not suitable for single-commit file-level diffs). Updated FR-003 to note that component documents are not regenerated. Updated DEP-001 to mention render_component_doc() exists but is excluded.
**Affected section:** FR-003, Out of Scope (OUT-002a), DEP-001

### Finding 10: NFR-001 lightweight hook has no measurable threshold
**Resolution:** Fixed. Added measurable threshold: "Hook execution (excluding network latency for the backend call) shall complete within 2 seconds of local processing time."
**Affected section:** NFR-001

### Finding 11: AC-001 comparison methodology undefined
**Resolution:** Fixed. Updated AC-001 to specify that comparison shall be performed at the structural level (section headings, content blocks, code references) rather than byte-for-byte, to accommodate non-deterministic elements such as generation timestamps.
**Affected section:** AC-001

### Finding 12: Concurrency check API feasibility (no reference to specific API)
**Resolution:** Fixed. Updated FR-016 to explicitly reference BackendClient.list_runs() (agent_runner_v2/v2/backend_client_v1.py) with workflow_name and status_group filters as the mechanism for the concurrency check. Added DEP-010 documenting this API dependency.
**Affected section:** FR-016, Dependencies (DEP-010)

### Finding 13: NFR-010 references if/elif dispatch pattern without acknowledging AGENTS.md tension
**Resolution:** Fixed. Added explicit note to NFR-010 clarifying that run_agent.py CLI dispatch uses if/elif chains as an established convention specific to that module, and is a known exception to the registry pattern required elsewhere by AGENTS.md.
**Affected section:** NFR-010

### Finding 14: DEP-002 module path abbreviation (missing v2/ subdirectory in paths)
**Resolution:** Fixed. Updated DEP-002 to use fully qualified paths: "agent_runner_v2/v2/backend_client_v1.py" for BackendClient and "agent_runner_v2/v2/backend_client.py" for V2BackendClient. Also updated CON-002 for consistency.
**Affected section:** DEP-002, CON-002

## Source Reference

This requirements document was derived from approved initiative INIT-20260806-001_incremental-codebase-doc-update.md by the sdlc_20_planning_v1 workflow. The workflow specification at docs/repo/workflow_builder/specs/incremental-codebase-update.md was used as a supplementary design reference. Implementation planning, task breakdown, scheduling, and architecture decisions belong to subsequent SDLC workflow steps (planning, backlog, task, implementation).
