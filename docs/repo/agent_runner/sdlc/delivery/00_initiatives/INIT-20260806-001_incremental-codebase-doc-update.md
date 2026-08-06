---
template_id: "SYS-03-IN"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "Approved initiative document in SDLC delivery chain"
managed_by: "workflow-generated"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "Approved"
effective_version: "SDLC00INIT-3tk8ukc4"
source_document: "DRAFT-INIT-20260806-001_incremental-codebase-doc-update.md"
---

# Incremental Codebase Documentation Updates with Git Hook Automation

## Initiative Metadata

- Initiative ID: INIT-20260806-001
- Source draft: DRAFT-INIT-20260806-001_incremental-codebase-doc-update.md
- Date: 2026-08-06
- Producing workflow: sdlc_00_init_doc_v1

## Objective

Provide automated, incremental codebase documentation updates for all agent-runner-v2 enabled repositories by implementing a reusable incremental-scan workflow and CLI commands for git hook lifecycle management. The initiative aims to replace the current model of full-repository scans with targeted, change-aware documentation regeneration that keeps module-level docs synchronized with source code after each commit.

## Problem Statement

### Current State

The platform uses the sdlc_00_codebase_v1 workflow to generate comprehensive codebase documentation. The current codebase inventory contains 141+ module documentation files under docs/repo/codebase/current/, along with an inventory file, component documents, and change impact reports. All agent-runner-v2 enabled repositories follow the same docs/repo/codebase/ directory structure. The full-scan workflow processes every module on every run regardless of how many source files actually changed.

### Pain Points

- Full scan processes all 141+ modules even when a commit touches only 1-2 files.
- Each full scan consumes significant time and computational resources (LLM tokens for prompt-driven rendering).
- Documentation updates require a manual trigger, causing docs to fall out of sync with code changes between refreshes.
- No automated mechanism exists to keep documentation current between manual full-scan runs.
- Every repository with codebase documentation faces the same synchronization problem independently, with no shared solution.

### Why This Initiative Is Needed

Developers need up-to-date codebase documentation to understand the system, but the cost of running a full scan on every commit is prohibitive. Without automation, documentation becomes stale quickly, reducing its value as a living reference. Since all agent-runner-v2 repositories share the same documentation structure, a single reusable solution can serve all of them.

### Impact of Not Undertaking This Initiative

- Codebase documentation will increasingly diverge from actual code across all agent-runner-v2 enabled repositories.
- Developers will rely less on generated documentation, preferring to read source code directly.
- The investment in comprehensive documentation generation (141+ module docs) is underutilized.
- Each repository must manage documentation updates manually, leading to inconsistency and drift.

## Expected Outcomes

1. A reusable update_codebase_docs_v1 workflow that performs incremental documentation updates in any agent-runner-v2 enabled repository, regenerating only the module docs affected by recent code changes.
2. Two new CLI subcommands (install-codebase-hook and uninstall-codebase-hook) added to the run_agent.py CLI entry point, supporting both current-directory default and an explicit --repo path flag.
3. A post-commit git hook script that automatically triggers the incremental update workflow when source code changes are committed.
4. Codebase documentation that remains synchronized with source code changes with zero manual intervention, reducing staleness from days/weeks to near-real-time.
5. Measurably reduced execution time and resource usage for typical commits (1-5 files changed) compared to full-scan runs.
6. A clear operational separation between incremental updates (frequent, lightweight, automated) and full-scan refreshes (periodic, comprehensive, manually triggered).

## Scope

### In Scope

- IN-001: Design and implement the update_codebase_docs_v1 workflow as an action-only workflow (no LLM involvement) for incremental documentation updates. The workflow must be repo-agnostic and work in any agent-runner-v2 enabled repository.
- IN-002: Implement the install-codebase-hook CLI subcommand in run_agent.py to install a post-commit git hook in any target repository.
- IN-003: Implement the uninstall-codebase-hook CLI subcommand in run_agent.py to cleanly remove the post-commit git hook from any target repository.
- IN-004: CLI commands support both current directory (default behavior) and an explicit --repo /path/to/repo flag for specifying a target repository.
- IN-005: Post-commit git hook script that detects source code changes and submits the update_codebase_docs_v1 workflow to the backend for execution.
- IN-006: Integration between the git hook, the backend API for workflow submission, and the daemon execution infrastructure.
- IN-007: A tracking mechanism (using a .last_sync_commit file) to determine what source files have changed since the last documentation update.
- IN-008: Automatic git commit of updated documentation files after successful incremental regeneration.
- IN-009: Error handling for edge cases including: no relevant changes since last sync, first run with no tracking file, concurrent workflow execution, missing standard documentation structure, and invalid tracking commit hash (e.g., after rebase or force-push).

### Out of Scope

- OUT-001: Modifications to the existing sdlc_00_codebase_v1 full-scan workflow. The full-scan workflow remains unchanged.
- OUT-002: Changes to the codebase documentation format, template structure, or rendering conventions.
- OUT-003: Support for repositories that do not follow the standard agent-runner-v2 docs/repo/codebase/ structure.
- OUT-004: Real-time or continuous documentation updates during development. Batch-per-commit is the intended granularity.
- OUT-005: Architecture decisions for backend API changes or daemon behavior modifications. Any required backend changes are assumed to be within existing API capabilities.
- OUT-006: Testing strategy and test implementation. Test planning belongs to subsequent SDLC workflow steps (planning, backlog, task).

### Boundary Conditions

- BC-001: The incremental workflow operates only on repositories that already have a populated docs/repo/codebase/current/ directory (created by codebase-init or sdlc_00_codebase_v1).
- BC-002: The git hook triggers only on commits that include relevant file types (*.py, workflow.toml, pyproject.toml, requirements.txt, constants.py). Changes to docs/, tests/, *.md, *.json, or generated files do not trigger updates.
- BC-003: If the .last_sync_commit tracking file is absent (first run), the workflow exits with a clear message directing the user to run sdlc_00_codebase_v1 first. It does not attempt a full scan.
- BC-004: If no relevant file changes are detected between the last sync commit and HEAD, the workflow exits successfully without regenerating any documentation.
- BC-005: The uninstall-codebase-hook command removes the hook script but preserves the .last_sync_commit tracking file, in case the user re-installs the hook later.
- BC-006: The incremental workflow is complementary to sdlc_00_codebase_v1. The full-scan workflow remains the authoritative mechanism for initial setup, major refactoring, and periodic comprehensive refresh.
- BC-007: If the commit hash stored in .last_sync_commit is no longer reachable (e.g., after a rebase or force-push), the workflow treats this as equivalent to BC-003 (missing tracking file) and exits with a message directing the user to run sdlc_00_codebase_v1 to re-establish the baseline.

### Assumptions

- ASSUMPTION-001: The existing BackendClient.submit_run() API in backend_client_v1.py can accept the new update_codebase_docs_v1 workflow name without backend modifications. If the backend requires workflow registration, that is a separate concern outside this initiative's scope.
- ASSUMPTION-002: The workflow spec at docs/repo/workflow_builder/specs/incremental-codebase-update.md represents the intended design. The initiative scope aligns with that spec.
- ASSUMPTION-003: The post-commit hook script will use the existing submit mechanism (ukbe-run-agent submit or equivalent CLI command) to submit the workflow to the backend. The hook itself does not implement workflow execution logic.
- ASSUMPTION-004: The .last_sync_commit tracking file stores a single commit hash (the HEAD at the time of the last successful documentation sync). The workflow uses git diff to determine changed files between that hash and the current HEAD.
- ASSUMPTION-005: The daemon must be running for the git hook submission to be processed. If the daemon is not running, the hook submission may fail or queue depending on backend configuration. See RISK-001 for mitigation approach. The initiative does not include daemon auto-start functionality.
- ASSUMPTION-006: Auto-commit of documentation files (IN-008) operates on repositories where branch protection rules permit direct commits to the working branch. If branch protection prevents auto-commit, the hook will log the updated files as uncommitted changes and exit with a warning. See RISK-004 for details.

## Constraints

- CON-001: The incremental workflow must reuse existing functions from codebase_docs.py (build_snapshot(), render_module_doc(), render_inventory(), render_change_impact()) rather than reimplementing scan and render logic.
- CON-002: The workflow must integrate with the existing backend/daemon architecture. Workflow submission uses the existing BackendClient.submit_run() API (backend_client_v1.py), and execution follows the standard daemon claim-execute-complete lifecycle using claim_work() (V2BackendClient in backend_client.py).
- CON-003: The git hook must be lightweight and non-blocking. It cannot delay or block the commit operation with heavy processing. Hook execution time should be minimal (submission only, not waiting for workflow completion).
- CON-004: The workflow must handle concurrent execution gracefully. If an incremental update is already running, subsequent hook triggers must skip submission rather than queue or fail. The hook should query the backend for active runs of update_codebase_docs_v1 before submitting.
- CON-005: The install-codebase-hook command must verify that the target repository has the standard docs/repo/codebase/current/ directory structure before installing the hook.
- CON-006: Both CLI commands (install and uninstall) must be idempotent. Running the same command multiple times must produce the same result without errors or side effects.
- CON-007: The incremental workflow must follow the Layer 2 runtime model for action steps. All steps are action-type steps that execute Python functions via the runner_actions.py ACTION_REGISTRY dispatch mechanism or the workflow package @action() decorator.
- CON-008: The workflow must produce its own meta.json sidecar through the standard action-step mechanism (runner writes sidecar from ActionResult), consistent with the Layer 2 step model.
- CON-009: The hook script must be stored within the agent-runner-v2 package and copied to the target repository's .git/hooks/ directory during installation.
- CON-010: The incremental workflow complements sdlc_00_codebase_v1 and does not replace it. The full-scan workflow must still be used for initial setup, major refactoring, or periodic comprehensive refresh.

## Dependencies

- DEP-001: The codebase_docs.py module must provide the following public functions: build_snapshot(), render_module_doc(), render_inventory(), render_change_impact(). These are confirmed present in the current codebase manifest (module: agent_runner_v2.codebase_docs).
- DEP-002: The existing backend API (BackendClient in backend_client_v1.py) must support workflow submission via submit_run(). The daemon step-claiming mechanism uses claim_step() on the same BackendClient class (backend_client_v1.py) and claim_work() on V2BackendClient (backend_client.py) for daemon polling.
- DEP-003: The existing daemon infrastructure (daemon_v2.py) must be capable of executing the new update_codebase_docs_v1 workflow using the standard action-step execution path.
- DEP-004: The standard docs/repo/codebase/current/ directory structure must exist in the target repository, populated by a prior run of codebase-init or sdlc_00_codebase_v1. This structure includes: 01_inventory/, 02_modules/, 03_components/, 04_changes/, and codebase_manifest.json.
- DEP-005: The target repository must be a git repository with post-commit hook support (standard .git/hooks/ directory).
- DEP-006: The run_agent.py CLI module uses if/elif command dispatch in its parse_args() function (not argparse subparsers). New subcommands are added as new if-blocks following the existing pattern used by codebase-init.
- DEP-007: The runner_actions.py module supports dispatching custom action functions registered via the ACTION_REGISTRY dictionary (runner_actions.py lines 42-56). New global actions are added by importing the function and adding it to ACTION_REGISTRY. Workflow package actions use the @action() decorator for package-local registration.
- DEP-008: The codebase_init_commands.py module provides a pattern for CLI command structure (argparse-based main() function) that the new hook commands should follow.
- DEP-009: The existing sync_codebase_docs action (actions/sync_codebase_docs.py) already calls build_snapshot(), render_module_doc(), render_inventory(), and render_change_impact() for the full-scan workflow. The incremental workflow will reuse these same rendering functions from codebase_docs.py, adding only change-detection and selective-regeneration logic. It does not duplicate or fork the existing action.

## Success Criteria

- SC-001: The update_codebase_docs_v1 workflow successfully regenerates only the affected module documentation files in any agent-runner-v2 enabled repository. Verified by comparing regenerated docs against full-scan output for the same set of changes.
- SC-002: The install-codebase-hook command installs a working post-commit git hook in any repository that has the standard docs/repo/codebase/current/ structure. Verified by making a test commit and confirming the hook triggers.
- SC-003: The uninstall-codebase-hook command cleanly removes the post-commit git hook without affecting the .last_sync_commit tracking file or any other repository state.
- SC-004: Both CLI commands work correctly with the default current-directory behavior and with the --repo /path/to/repo flag.
- SC-005: The git hook triggers the incremental workflow automatically after commits that include source code changes (*.py, workflow.toml, etc.).
- SC-006: Updated documentation files are committed automatically to the repository without manual intervention after a successful incremental update.
- SC-007: Incremental workflow execution time is measurably less than full-scan execution time for typical commits (1-5 files changed). Target: less than 50 percent of full-scan time for single-file changes.
- SC-008: No duplicate or concurrent workflow executions occur when the hook is triggered multiple times in rapid succession.
- SC-009: Clear, actionable error messages are produced when: (a) the .last_sync_commit tracking file is missing (directs user to run sdlc_00_codebase_v1), (b) the docs/repo/codebase/current/ structure is absent (directs user to run codebase-init), (c) no relevant changes are detected (silent success), (d) the stored commit hash is unreachable (directs user to run sdlc_00_codebase_v1).
- SC-010: Hook installation is idempotent. Running install-codebase-hook multiple times produces no errors and leaves exactly one hook script in place.

## Risk Assessment

- RISK-001: Git hook may fail silently if the daemon is not running. The hook submits the workflow via the backend API, and if the backend is unreachable, the submission fails. Without explicit feedback, the developer may not realize the documentation was not updated. Mitigation: The hook script should log submission results (success/failure) to a known file (e.g., .git/codebase-hook.log) and emit a console message on failure so the developer is aware. The .last_sync_commit file is only updated after successful workflow completion, so the next commit will re-trigger.
- RISK-002: Concurrent hook triggers on rapid commits could race on the .last_sync_commit file. If two commits occur in quick succession and both trigger the workflow, the .last_sync_commit update from the first workflow may conflict with the second workflow's change detection. Mitigation: Use file-based locking (atomic write with a lock file) for .last_sync_commit updates. The concurrency check in CON-004 prevents duplicate workflow submissions at the backend level.
- RISK-003: Incremental regeneration may produce different output than a full scan for the same module if the build_snapshot() context is incomplete (e.g., cross-module dependencies not captured by file-level diff). Mitigation: SC-001 requires comparison of incremental output against full-scan output for the same changes. If divergence is detected, the developer should be directed to run sdlc_00_codebase_v1 for a full refresh.
- RISK-004: Auto-commit of documentation (IN-008) may conflict with branch protection rules or pre-commit hooks in some repositories. If the target repository has branch protection that prevents direct commits, the auto-commit step will fail. Mitigation: If auto-commit fails due to branch protection, the workflow should log the updated files as uncommitted changes and exit with a non-zero status. The hook should emit a warning message. This is documented in ASSUMPTION-006.

## Stakeholders

- Sponsor: agent-runner-v2 platform maintenance team.
- Primary Users: Developers working in agent-runner-v2 enabled repositories who rely on codebase documentation for system understanding and onboarding.
- Review Authorities: Platform core maintainers responsible for Layer 2 constitution compliance; SDLC workflow owners responsible for workflow package quality.
- Affected Teams: All teams maintaining repositories that use the sdlc_00_codebase_v1 workflow for documentation generation. The new workflow and hook commands extend the existing tooling without breaking current workflows.

## Critique Resolution

### Finding TF-01: DEP-002 references incorrect module and non-existent method
**Resolution:** Corrected the module reference from backend_client.py to backend_client_v1.py for both submit_run() and claim_step(). Verified via codebase inspection that claim_step() exists on BackendClient in backend_client_v1.py (line 177). Added note about claim_work() on V2BackendClient for daemon polling. The critique's claim that claim_step() does not exist was based on incomplete inspection; the method is present in backend_client_v1.py.
**Affected section:** Dependencies (DEP-002)

### Finding TF-02: DEP-007 references non-existent @action() decorator
**Resolution:** Partially accepted. The @action() decorator does exist in the codebase (used in workflow packages and sdlc_shared_actions.py). However, runner_actions.py itself uses the ACTION_REGISTRY dictionary for global action dispatch. Updated DEP-007 to accurately describe both registration patterns: ACTION_REGISTRY for global actions (runner_actions.py) and @action() decorator for workflow package-local actions.
**Affected section:** Dependencies (DEP-007), Constraints (CON-007)

### Finding TF-03: DEP-006 is misleading about CLI dispatch architecture
**Resolution:** Accepted. Updated DEP-006 to correctly state that run_agent.py uses if/elif command dispatch in parse_args(), not argparse subparsers. Added reference to the codebase-init pattern as the model for new commands.
**Affected section:** Dependencies (DEP-006)

### Finding TF-04: Missing Risk Assessment section
**Resolution:** Accepted. Added Risk Assessment section with four risks: RISK-001 (silent hook failure when daemon not running), RISK-002 (concurrent .last_sync_commit races), RISK-003 (incremental vs. full-scan output divergence), RISK-004 (auto-commit conflict with branch protection). Each risk includes a mitigation approach.
**Affected section:** Risk Assessment (new section)

### Finding TF-05: Missing Initiative Metadata section
**Resolution:** Accepted. Added Initiative Metadata section after the title with Initiative ID, source draft reference, date, and producing workflow.
**Affected section:** Initiative Metadata (new section)

### Finding TF-06: Missing Source Reference section
**Resolution:** Accepted. Added Source Reference section at the end of the document cross-referencing the source draft and producing workflow.
**Affected section:** Source Reference (new section)

### Finding TF-07: Assumptions misplaced outside Scope section
**Resolution:** Accepted. Moved ASSUMPTION-001 through ASSUMPTION-005 into a new "Assumptions" subsection under Scope. Added ASSUMPTION-006 (auto-commit branch protection) based on RISK-004. Relocated NOTE-001 content into CON-010 (Constraints). Relocated NOTE-002 content into Source Reference. Removed the "Notes" section.
**Affected section:** Scope (new Assumptions subsection), Constraints (CON-010), Notes (removed), Source Reference

### Finding TF-08: Overlap with existing sync_codebase_docs action
**Resolution:** Accepted. Added DEP-009 explicitly acknowledging the existing sync_codebase_docs action and stating that the incremental workflow reuses the same codebase_docs.py rendering functions without duplicating logic.
**Affected section:** Dependencies (DEP-009)

### Recommendation 8: Address daemon availability check
**Resolution:** Addressed via RISK-001 mitigation. The hook should log submission results and emit a console message on failure. This is documented in the Risk Assessment section.
**Affected section:** Risk Assessment (RISK-001), Scope/Assumptions (ASSUMPTION-005 updated)

### Recommendation 9: Address .last_sync_commit invalidation
**Resolution:** Accepted. Added BC-007 specifying behavior when the stored commit hash is unreachable (e.g., after rebase or force-push): treat as equivalent to missing tracking file and direct user to run sdlc_00_codebase_v1. Also updated SC-009 to include this case.
**Affected section:** Scope/Boundary Conditions (BC-007), Success Criteria (SC-009)

### Recommendation 10: Acknowledge existing sync_codebase_docs action
**Resolution:** Addressed via DEP-009. Same as Finding TF-008.
**Affected section:** Dependencies (DEP-009)

### Recommendation 11: Add testing strategy
**Resolution:** Not addressed at initiative level. Testing strategy (unit tests, integration tests, verification procedures) belongs to the planning and task workflow steps, not the initiative document. Added OUT-006 to explicitly exclude testing strategy from initiative scope.
**Affected section:** Scope/Out of Scope (OUT-006)

### Recommendation 12: Consider branch protection interaction for auto-commit
**Resolution:** Addressed via RISK-004 and ASSUMPTION-006. Documented the risk and specified graceful degradation behavior.
**Affected section:** Risk Assessment (RISK-004), Scope/Assumptions (ASSUMPTION-006)

## Source Reference

This initiative was generated from draft initiative DRAFT-INIT-20260806-001_incremental-codebase-doc-update.md by the sdlc_00_init_doc_v1 workflow. Implementation planning, task breakdown, scheduling, and architecture decisions belong to subsequent SDLC workflow steps (planning, backlog, task, implementation).
