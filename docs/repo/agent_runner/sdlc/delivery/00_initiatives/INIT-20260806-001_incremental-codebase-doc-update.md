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
effective_version: "SDLC0RP-48s8745y"
source_document: "DRAFT-INIT-20260806-001_incremental-codebase-doc-update.md"
---

# Incremental Codebase Documentation Updates with Git Hook Automation

## Objective

Provide automated, incremental codebase documentation updates for all agent-runner-v2 enabled repositories by implementing a reusable workflow package and CLI-managed git hook commands. The initiative delivers a mechanism that regenerates only affected module documentation after source code commits, keeping codebase docs synchronized with minimal execution time and resource overhead.

## Problem Statement

### Current State

The platform uses the `sdlc_00_codebase_v1` workflow to generate comprehensive codebase documentation (141+ module docs, inventory, component docs, change impact reports). All agent-runner-v2 enabled repositories follow the same `docs/repo/codebase/` directory structure. The workflow performs a full scan of the entire repository on every run.

### Pain Points

- Full scan processes all modules even when only one or two files have changed
- Each full scan run takes significant time and computational resources
- Manual triggering means documentation frequently falls out of sync with code changes
- No automated mechanism exists to keep documentation current between manual refreshes
- Every repository with codebase documentation faces the same staleness problem independently

### Why This Initiative Is Needed

Developers need up-to-date codebase documentation to understand the system, but the cost of running a full scan on every commit is prohibitive. Without automation, documentation becomes stale quickly, reducing its value as a living reference. Since all agent-runner-v2 repositories share the same documentation structure, a single reusable solution can serve all of them.

### Impact of Not Undertaking This Initiative

- Codebase documentation will increasingly diverge from actual code across all repositories
- Developers will rely less on documentation, preferring to read source code directly
- The investment in comprehensive documentation generation is underutilized
- Each repository must manually manage documentation updates, leading to inconsistency across the ecosystem

## Expected Outcomes

1. A reusable `update_codebase_docs_v1` workflow package that performs incremental documentation updates and operates in any agent-runner-v2 repository
2. CLI commands (`install-codebase-hook`, `uninstall-codebase-hook`) to install and remove a post-commit git hook in any target repository
3. Post-commit git hook that automatically triggers incremental documentation updates when source code changes are committed
4. Codebase documentation stays synchronized with code changes with zero manual intervention after initial hook installation
5. Reduced execution time and resource consumption compared to full-scan workflow runs for typical commits (one to five files changed)
6. Clear separation between incremental updates (frequent, per-commit) and full documentation refresh (periodic, manual)
7. Tracking mechanism (`.last_sync_commit` file) to determine what changed since the last documentation update

## Scope

### In Scope

- Design and implement the `update_codebase_docs_v1` workflow package for incremental documentation updates, repo-agnostic across all agent-runner-v2 repositories
- Implement the `install-codebase-hook` CLI command to install a post-commit git hook in any repository
- Implement the `uninstall-codebase-hook` CLI command to remove the git hook from any repository
- CLI commands support both current directory (default) and `--repo /path/to/repo` flag for targeting arbitrary repositories
- Post-commit git hook script that submits the incremental update workflow to the backend
- Integration between the git hook, backend workflow submission, and daemon execution
- Tracking mechanism to determine what files changed since the last documentation update (`.last_sync_commit` reference)
- Automatic commit of updated documentation after incremental regeneration
- Error handling for edge cases: no source changes detected, first run without tracking file, concurrent workflow execution, missing `docs/repo/codebase/` structure
- Reuse of existing `codebase_docs.py` module functions for snapshot building and documentation rendering

### Out of Scope

- Modifications to the existing `sdlc_00_codebase_v1` full-scan workflow
- Changes to the codebase documentation format, structure, or template design
- Support for repositories that do not follow the standard agent-runner-v2 `docs/repo/codebase/` directory structure
- Real-time or continuous documentation updates (batch-per-commit is sufficient)
- Changes to the codebase manifest schema or artifact key naming conventions

### Boundary Conditions

- The incremental workflow operates on repositories that already have an initial codebase documentation set generated by `sdlc_00_codebase_v1` or `codebase-init`
- The workflow detects and skips repositories without the standard `docs/repo/codebase/current/` structure
- Concurrent execution is handled by skipping the run if an incremental update is already in progress
- The git hook is a post-commit hook only; pre-commit hooks and other git hook types are not affected
- The `.last_sync_commit` tracking file is preserved across uninstall/reinstall cycles

## Constraints

### Technical Constraints

- Must integrate with the existing `codebase_docs.py` module by reusing `build_snapshot()`, `render_module_doc()`, `render_inventory()`, and `render_change_impact()` functions
- Must work with the existing backend and daemon architecture (submit workflow, claim step, execute, complete)
- The post-commit git hook must be lightweight and must not block commits with heavy synchronous processing
- The workflow must handle concurrent execution gracefully by skipping if an update is already running
- The hook installation must verify the presence of `docs/repo/codebase/current/` before enabling
- Install and uninstall commands must be idempotent (safe to run multiple times without side effects)
- The workflow package must follow the existing workflow package structure (`workflow.toml`, `prompts/`, `actions.py`, `context_extensions.py`)

### Architectural Constraints

- Must comply with the Layer 3 workflow package conventions defined in the agent-runner-v2 platform
- Must use the existing artifact key and path resolution system (`artifact_keys.py`, `path_primitives.py`, `path_catalog.py`)
- Must produce a valid `meta.json` sidecar per the v2 sidecar schema
- The hook script must be stored in the agent-runner-v2 package (under `agent_runner_v2/`) and copied to the target repository's `.git/hooks/` directory during installation; the exact source path within the package will be finalized during planning
- Must not redefine or contradict Layer 1 governance or Layer 2 platform constitution rules

### Resource Constraints

- Incremental update execution time must achieve a target reduction of 50% or greater compared to full scan for typical commits (one to five files changed)
- The git hook script must not add noticeable latency to the commit operation itself
- The benchmark target (50% reduction) will be measured against the baseline full-scan execution time on the same repository under similar conditions

## Dependencies

### Prerequisite Initiatives

- The `sdlc_00_codebase_v1` full-scan workflow must have been executed at least once on the target repository to establish the initial documentation set
- The `codebase-init` command must have been run to create the standard `docs/repo/codebase/` directory structure

### Platform Dependencies

- Existing `codebase_docs.py` module with `build_snapshot()`, `render_module_doc()`, `render_inventory()`, and `render_change_impact()` functions
- Existing backend API for workflow submission (`BackendClient.submit_run()`) and step claiming (`BackendClient.claim_step()`)
- Existing daemon infrastructure for workflow execution (`daemon_v2.py`)
- Standard `docs/repo/codebase/` directory structure (created by `codebase-init` or `sdlc_00_codebase_v1`)
- Git repository with post-commit hook support (standard git functionality)
- The `@action()` decorator and `ActionResult` dataclass for registering action steps in the workflow package

### Infrastructure Dependencies

- The target repository must be a git repository with write access to `.git/hooks/`
- The agent-runner-v2 package must be installed and accessible in the Python environment
- The backend service must be running and reachable for workflow submission in daemon mode

## Success Criteria

1. The `update_codebase_docs_v1` workflow successfully regenerates only the affected module documentation files in any agent-runner-v2 repository that has the standard `docs/repo/codebase/` structure
2. The `install-codebase-hook` command installs a working post-commit git hook in any repository with the standard codebase documentation structure
3. The `uninstall-codebase-hook` command cleanly removes the post-commit hook while preserving the `.last_sync_commit` tracking file
4. CLI commands work correctly with both the current directory (default) and the `--repo /path/to/repo` flag
5. The git hook triggers the incremental workflow automatically after commits that include source code changes
6. Updated documentation is committed automatically to the repository without manual intervention
7. Workflow execution time for typical commits (one to five files changed) achieves at least 50% reduction compared to a full-scan run, measured under comparable conditions
8. No duplicate or concurrent workflow executions occur when multiple commits happen in rapid succession
9. Clear error messages are produced when the tracking file is missing (first run scenario) or when the `docs/repo/codebase/` structure is absent
10. Hook installation is idempotent -- running `install-codebase-hook` multiple times does not create duplicate hooks or errors
11. The workflow correctly identifies changed source files and regenerates only the corresponding module documentation files

## Stakeholders

### Sponsor

- Platform development team (agent-runner-v2 maintainers)

### Primary Users

- Developers working in agent-runner-v2 enabled repositories who need current codebase documentation
- Workflow authors who maintain codebase documentation across multiple repositories

### Review Authorities

- Platform architecture review (Layer 2 compliance validation)
- SDLC delivery chain review (artifact traceability and governance compliance)

### Affected Teams

- agent-runner-v2 core development team (CLI commands, workflow package, hook script)
- All teams operating agent-runner-v2 enabled repositories with codebase documentation
- Backend and daemon infrastructure team (workflow submission integration)

## Critique Resolution

### Finding 1: Define quantitative benchmark for execution time reduction
**Resolution:** Added explicit 50% reduction target to Resource Constraints and Success Criteria. Changed vague "significantly less" language to measurable benchmark. The target is 50% or greater reduction compared to full-scan for typical commits (1-5 files changed), measured under comparable conditions.
**Affected section:** Constraints (Resource Constraints), Success Criteria (item 7)

### Finding 2: Confirm exact hook script source path within the package
**Resolution:** The initiative correctly identifies that the hook script is stored in the agent-runner-v2 package. The exact source path within the package is an implementation detail that belongs to the planning phase. Added clarification that the path will be finalized during planning, and added a new bullet in Affected Codebase Areas for the hook script template storage location.
**Affected section:** Constraints (Architectural Constraints), Affected Codebase Areas

### Finding 3: Specify exact error message content and recovery actions
**Resolution:** No change made at the initiative level. The initiative correctly identifies error handling as in-scope and lists the specific edge cases to handle (no source changes detected, first run without tracking file, concurrent workflow execution, missing docs structure). The exact error message content and recovery actions are requirements-level details to be specified during the planning phase, as the critique itself notes ("During requirements, specify...").
**Affected section:** None (out of scope for initiative document)

### Finding 4: Evaluate manual trigger command for testing and debugging
**Resolution:** Strengthened the language from "may be considered" to "should be evaluated" with explicit justification that it supports testing and debugging scenarios. The manual trigger command remains out of the explicitly scoped items but is now more prominently noted as a planning-phase evaluation item.
**Affected section:** Notes (Assumptions)

### Finding 5: Consider pre-push hooks as alternative or complementary trigger
**Resolution:** Added a new assumption noting that pre-push hooks may be considered during planning as an alternative or complementary trigger for batching multiple commits. The post-commit approach remains the primary mechanism. This preserves the initiative's scope while acknowledging the alternative for planning-phase evaluation.
**Affected section:** Notes (Assumptions)

## Notes

### Assumptions

- The draft initiative references a workflow spec at `docs/repo/workflow_builder/specs/incremental-codebase-update.md`. This initiative assumes that spec is available as a design reference during the planning phase.
- The incremental workflow complements `sdlc_00_codebase_v1` and does not replace it. The full-scan workflow remains the authority for initial setup, major refactoring, and periodic refresh.
- The git hook should check daemon availability before submitting the workflow to avoid orphaned submissions.
- A manual trigger command for testing without committing should be evaluated during the planning phase, as it supports testing and debugging scenarios and reduces reliance on actual commits for verification.
- Pre-push hooks may be considered as an alternative or complementary trigger during planning, to support batching of multiple commits into a single documentation update. The post-commit approach remains the primary mechanism.

### Background

- The codebase documentation inventory currently contains 141+ module documentation files, 6 component documents, and change impact reports, all under `docs/repo/codebase/current/`.
- The existing `sdlc_00_codebase_v1` workflow was last executed with change ID `SDLC00CB-bgmxg5vi` and published on 2026-08-06.
- All agent-runner-v2 enabled repositories share the same `docs/repo/codebase/` directory structure, making a single reusable solution feasible.

### Affected Codebase Areas

Based on the current codebase inventory, the following areas are likely affected by this initiative:
- `agent_runner_v2/codebase_docs.py` -- confirmed existing module with `build_snapshot()`, `render_module_doc()`, `render_inventory()`, and `render_change_impact()` functions to be reused for incremental rendering
- `agent_runner_v2/actions/sync_codebase_docs.py` -- existing sync action module to be referenced or extended
- `agent_runner_v2/actions/scan_repo_codebase.py` -- existing scan action for understanding current scan patterns
- `agent_runner_v2/run_agent.py` -- new CLI subcommands for hook install/uninstall
- `workflows/` -- new workflow package directory for `update_codebase_docs_v1`
- CLI command modules following the existing pattern (e.g., `submit_commands.py`, `engine_commands.py`)
- A new location under `agent_runner_v2/` to store the hook script template (exact path to be determined during planning)
