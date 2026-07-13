# Backend Execution Refactor Plan

## Summary

This document is the single source of truth for the backend execution refactor.

There are two operation modes:

1. Manual local mode
   - Triggered directly by the user
   - Runs through `agent-runner-v2`
   - Does not depend on backend API orchestration

2. Daemon mode
   - Backend-driven worker/daemon execution
   - Backend API is used only for this mode
   - Backend owns run/step persistence, worker coordination, approvals, and daemon routing

The shared plugin workflow execution logic is authored in `agent-runner-v2`, then copied into `agent-runner-backend` as a vendored module for consistency.

`00_core_governance_bootstrap_v1` is the first validated migrated workflow and is the regression baseline for this refactor.

## Migration Scope Guardrail

- Only `00_core_governance_bootstrap_v1` is currently in migration scope
- Non-migrated workflows must remain unchanged during this phase, including:
  - `00_master_docs_bootstrap_v2`
  - `10_execution_scaffold_v2`
- If a broader workflow rule is discovered during analysis, apply it only to the migrated workflow unless a separate migration phase is explicitly started for the other workflow
- Do not tighten loader/package invariants in ways that force edits to non-migrated workflows during the current phase

## Current Status

Completed:

- `00_core_governance_bootstrap_v1` was migrated onto the local common workflow execution path
- The workflow completed successfully in local manual mode
- Deterministic validation and semantic audit passed
- `agent-runner-v2` already contains partial common execution pieces:
  - `execution_request.py`
  - `execution_result.py`
  - `execution_core.py`
  - backend-oriented `execute-step` handling
- Phase 2 slice 1 completed:
  - failure-envelope helpers were extracted from `job_state.py`
  - `execution_core.py` now uses injected routing/failure callbacks instead of importing `workflow_router.py` directly
- Phase 3 slice 1 completed:
  - daemon/backend `execute-step` and worker helpers were extracted into `agent_runner_v2/backend_execution.py`
  - `run_agent.py` now keeps CLI/test compatibility through thin wrapper functions
- Phase 2 slice 2 completed:
  - step preparation and execution helpers were extracted into `agent_runner_v2/step_execution_runtime.py`
  - prompt-governance injection and coder-resolution logic now sit behind `run_agent.py` compatibility wrappers
- Phase 2 slice 3 completed:
  - workflow loading, delivery-folder setup, static-reference validation, and artifact-discovery helpers were extracted into `agent_runner_v2/workflow_runtime.py`
  - `run_agent.py` now retains compatibility wrappers for these shared runtime helpers
- Phase 3 slice 2 completed:
  - manual local job-resolution flow was extracted into `agent_runner_v2/manual_runtime.py`
  - new-job, resume, completed-seed, and current-step selection logic now sit behind a compatibility call from `run_agent.py`
- Phase 3 slice 3 completed:
  - admin command handling and CLI status/failure rendering helpers were extracted into `agent_runner_v2/cli_runtime.py`
  - `run_agent.py` now delegates `--single-step`, job inspection/approval overrides, and status/failure formatting through compatibility wrappers
- Phase 2 slice 4 completed:
  - task queue / task execution binding helpers used by the shared execution path were extracted into `agent_runner_v2/task_runtime.py`
  - shared execution callers now depend on `task_runtime.py` instead of importing those helpers directly from `job_state.py`
- Phase 3 slice 4 completed:
  - CLI/admin approval and routing helpers now resolve through injected `run_agent.py` hooks instead of direct `cli_runtime.py -> job_state.py` imports
  - the manual/CLI orchestration boundary is cleaner without changing user-facing command behavior
- Phase 3 slice 5 completed:
  - duplicated admin-command handling was removed from `run_agent.py`
  - `cli_runtime.py` is now the single orchestration path for admin/manual control commands before normal execution continues
- Phase 2 slice 5 completed:
  - approved-step next-route prediction for backend worker mode was extracted into `agent_runner_v2/routing_runtime.py`
  - backend execution no longer calls the broader `advance_step()` state machine just to determine the next step after a successful worker step
- Phase 2 slice 6 completed:
  - failure bookkeeping helpers (`set_last_failure`, `clear_last_failure`, `append_failure_history`) were extracted into `agent_runner_v2/failure_runtime.py`
  - run/route/runtime code now shares those helpers without depending on `job_state.py` for basic failure-state mutation
- Phase 2 slice 7 completed:
  - default “next non-refine/non-replan step” progression now resolves through `agent_runner_v2/routing_runtime.py`
  - both backend next-step prediction and `job_state.py` default forward progression now share the same routing helper
- Phase 2 slice 8 completed:
  - simple approved-step transition helpers were extracted into `agent_runner_v2/transition_runtime.py`
  - review-approval waiting, task-exec success routing, and default forward progression no longer need to live inline inside `job_state.py`
- Phase 2 slice 9 completed:
  - shared loop/replan success transition handling was extracted into `agent_runner_v2/transition_runtime.py`
  - refine-success and replan-success now reuse a common recovery-transition helper instead of duplicating artifact-change / no-op / reset logic inside `job_state.py`
- Phase 2 slice 10 completed:
  - shared loop/replan trigger mechanics were extracted into `agent_runner_v2/recovery_runtime.py`
  - workflow-router loop/replan activation now reuses common budget-exceeded handling and common trigger-context/history setup helpers
- Phase 3 slice 6 completed:
  - backend step-execution-spec to `group_cfg` / `step_cfg` translation was extracted into `agent_runner_v2/backend_execution.py`
  - `run_agent.py` now delegates that daemon-only spec-building helper through a compatibility wrapper instead of owning the implementation directly
- Phase 3 slice 7 completed:
  - shadowed legacy backend/shared helper bodies were removed from `agent_runner_v2/run_agent.py`
  - `run_agent.py` now keeps a single active compatibility wrapper surface for backend/shared runtime hooks
  - thin local utility hooks (`_save_text`, `_save_json`, `_now_iso`) were retained because the extracted runtime modules still depend on them
- Phase 3 slice 8 completed:
  - a hook-surface contract test was added for `run_agent.py` so extracted runtime modules cannot silently lose required compatibility symbols during future cleanup
  - backend worker `execute-step` tests remain the regression gate for daemon mode while the new hook-surface test protects manual/local orchestration compatibility
- Phase 3 slice 9 completed:
  - manual review-start bookkeeping was extracted from `run_agent.py` into `agent_runner_v2/transition_runtime.py`
  - `run_agent.py` now delegates that review-state mutation through a compatibility wrapper, continuing the move toward a thinner orchestration shell
- Phase 3 slice 10 completed:
  - generic path/time/file helpers were extracted from `run_agent.py` into `agent_runner_v2/runtime_utils.py`
  - `run_agent.py` retains the same compatibility hook names while delegating to the shared utility module, reducing direct ownership of non-orchestration concerns
- Phase 3 Slice B completed:
  - `agent_runner_v2/workflow_runtime.py` now uses a direct-import shared-runtime contract for:
    - delivery-folder setup
    - workflow loading
    - static-reference validation
    - artifact discovery
  - wrapper callers in `manual_runtime_deps.py`, `shared_runtime_deps.py`, and `run_agent.py` were updated together
  - wrapper-boundary tests were added so future signature drift is caught before runtime
- Phase 3 Slice C completed:
  - pure helper logic in `agent_runner_v2/step_execution_runtime.py` now uses a direct-import shared-runtime contract for:
    - generated-doc prompt augmentation
    - master bootstrap frontmatter contract generation
    - master bootstrap frontmatter row resolution
    - coder resolution
  - adapter-driven orchestration entrypoints remain hook-based:
    - `prepare_step_execution()`
    - `execute_prepared_step()`
  - wrapper callers in `shared_runtime_deps.py` and `run_agent.py` were updated together
  - wrapper-boundary tests were added for the new direct helper signatures
- Phase 3 Slice D completed:
  - `manual_runtime_deps.py` was reduced to a thinner manual-only adapter:
    - direct shared-runtime calls remain for artifact discovery and key-value parsing
    - CLI status-summary formatting no longer requires module-self hook injection
  - `shared_runtime_deps.py` was reduced to a thinner daemon-only adapter:
    - stale prompt-governance, workflow-loader, and coder-resolution symbol ownership was removed where those responsibilities now live in direct-import shared modules
    - only the live daemon adapter surface remains for backend execution and hook-based orchestration entrypoints
  - hook-surface tests were updated to match the actual adapter contract instead of the older broader compatibility surface
- Phase 3 Slice E completed:
  - wrapper-boundary regression coverage now includes:
    - `manual_runtime_deps.py -> workflow_runtime.py`
    - `manual_runtime_deps.py -> cli_runtime.py`
    - `shared_runtime_deps.py -> workflow_runtime.py`
    - `shared_runtime_deps.py -> step_execution_runtime.py`
    - `run_agent.py -> workflow_runtime.py`
    - `run_agent.py -> step_execution_runtime.py`
  - hook-based adapter seams are now explicitly tested for:
    - shared runtime direct-call wrappers
    - pure helper direct-call wrappers
    - hook-preserving prepare/execute wrappers
  - the reverted mixed-signature regression pattern is now covered by tests before runtime

Incomplete:

- The common execution logic is not yet fully standalone
- It still has orchestration coupling to:
  - `job_state.py`
  - `run_agent.py`
- Backend has `api`, `services`, and `database` folders, but the behavioral split is still weak
- Backend route handlers still contain too much query and orchestration logic
- Phase 4 slice 4.2 is now started:
- Phase 4 slice 4.2 is now completed:
  - backend vendored runtime package was created at `agent_runner_backend/vendored_runtime/`
  - the first dependency-light shared-core files were copied mechanically from `agent-runner-v2`
  - the initial copy baseline now exists inside backend without runtime imports from `agent_runner_v2`
- Phase 4 slice 4.3 is now started and partially completed:
  - `agent_runner_backend/workers/agent_worker.py` no longer owns a parallel worker loop implementation
  - the backend worker now delegates through vendored `backend_execution.worker_command(...)`
  - backend-specific wrappers remain in `agent_worker.py` so the backend adapter surface stays outside the vendored package
- Phase 4 slice 4.4 is now started and partially completed:
  - `arb-agent` is now a real backend worker CLI entrypoint
  - backend worker CLI reads the single global config file
  - backend worker supports:
    - worker id
    - worker label
    - backend url
    - poll seconds
    - host name
    - engine root override
    - `--once`
  - backend-local execute-step entry wiring now exists:
    - `agent_runner_backend.workers.execute_step_entry`
    - `agent_runner_backend.workers.execute_step_runtime_deps`
  - backend worker adapter now delegates its live hook surface through the backend execute-step runtime deps instead of keeping placeholder subprocess/finalization bodies
  - backend vendored runtime now includes the minimal additional shared-runtime bridge pieces needed by daemon mode:
    - `execution_core.py`
    - minimal `runner_actions.py`
    - backend-safe terminal `step_completion` action
  - daemon notifications are now optional at backend finalization time; missing notification modules no longer break worker completion
  - targeted backend worker regression reached full end-to-end step progression for the migrated workflow before the notification import gap was fixed
- current blocker is backend integration test environment stability:
    - resolved: the deadlocks were caused by parallel backend `pytest` runs against the same shared `agentrunner` database
    - serial reruns of the backend migrated-workflow regressions passed
- Phase 4 slice 4.6 is now completed:
  - backend unit contract coverage was added for the vendored runtime boundary:
    - `ExecutionRequest.from_dict(...)`
    - `ExecutionResult.to_dict(...)`
    - backend worker request payload building
    - execute-step subprocess wiring
    - worker result submission normalization
    - worker finalization envelope behavior when notification modules are absent
  - new test file:
    - `tests/unit/test_vendored_runtime_contract.py`
  - contract test result:
    - `10 passed`
  - serial backend daemon regressions remain green:
    - worker-loop subset: `2 passed`
    - migrated-workflow API subset: `6 passed`
- Phase 4 slice 4.7 is now completed:
  - daemon-mode migrated workflow acceptance is now covered by backend worker integration tests for `00_core_governance_bootstrap_v1`
  - acceptance coverage now includes:
    - straight-through worker completion path
    - worker-driven `review -> refine` loop re-entry
    - worker-driven `validation -> refine` loop re-entry
    - artifact registration through the worker completion flow
    - final workflow completion through the backend worker bridge
  - acceptance tests:
    - existing worker happy-path integration: `2 passed` subset includes `test_core_governance_worker_loop_via_backend_worker`
    - new refine-cycle daemon acceptance:
      - `test_core_governance_worker_loop_handles_refine_cycles_via_backend_worker`
      - result: `1 passed`
- Backend worker config resolution was aligned with the single global config path:
  - `C:\Users\kengk\.ukbe-runner\config.json`
  - the old backend worker assumption about `~/.ukbe-runner/engine/config.json` was removed

Phase 3 audit status after revert and baseline verification:

- Manual local regression baseline is green again on `00_core_governance_bootstrap_v1`
  - verified with job `00CORE-GEN-20260713-008`
- The latest post-commit decoupling attempt was reverted because it introduced mixed hook-contract regressions in manual mode
- The remaining Phase 3 work is not "extract more files"
  - it is "stabilize dependency contracts across already-extracted modules"
- `Slice B` is now complete
- `Slice C` is now complete
- `Slice D` is now complete
- `Slice E` is now complete
- Phase 3 is now complete enough to proceed to Phase 4 vendor-copy work, with `00_core_governance_bootstrap_v1` remaining the manual regression gate

## Phase 3 Boundary Audit

This audit defines which extracted modules are intended to become pure shared runtime modules, which are intended to remain manual-only or daemon-only adapters, and which are currently mixed and must be cleaned up before Phase 4 vendor-copy.

### Category A: Pure shared-runtime modules

These modules are good candidates to be vendored into backend with minimal import-root adjustment:

- `execution_request.py`
- `execution_result.py`
- `execution_core.py`
- `failure_runtime.py`
- `routing_runtime.py`
- `transition_runtime.py`
- `recovery_runtime.py`
- `task_runtime.py`
- `runtime_utils.py`
- `state_defaults.py`

Rules for this category:

- no dependency on `run_agent.py`
- no dependency on CLI/manual argument parsing
- no backend API/persistence logic
- avoid `sys.modules[__name__]` hook indirection unless there is a deliberate adapter boundary

### Category B: Manual-only orchestration modules

These modules are not part of the vendored shared execution core. They should remain local to `agent-runner-v2`:

- `manual_runtime.py`
- `cli_runtime.py`
- `manual_runtime_deps.py`

Rules for this category:

- may depend on `job_state.py`
- may own CLI/admin/manual resume semantics
- must not become a dependency of daemon/backend execution paths

### Category C: Daemon-only orchestration modules

These modules are daemon/backend adapters. They are not part of the manual-mode source of truth:

- `backend_execution.py`
- `shared_runtime_deps.py`

Rules for this category:

- may depend on backend worker payloads, job-json persistence, worker claim/completion flow, and backend client behavior
- must not become required for local manual execution

### Category D: Mixed-contract modules with intentional split boundaries

These modules are extracted and intentionally split between pure helpers and hook-based orchestration entrypoints:

- `workflow_runtime.py`
- `step_execution_runtime.py`

Current status:

- `workflow_runtime.py` shared helper surface is now normalized to direct-import runtime helpers
- `step_execution_runtime.py` mixes:
  - generic one-step preparation/execution logic
  - prompt-governance augmentation logic
  - coder-resolution logic
  - hook-based access to manual/daemon shims
- in `step_execution_runtime.py`, the split is now explicit:
  - pure helpers use direct imports
  - orchestration entrypoints remain adapter-driven by design
- wrapper-boundary tests now guard both halves of the split contract

## Remaining Phase 3 Checklist

The goal is to make the boundaries explicit and stable, not to maximize extraction count.

### Slice A: Freeze module intent before further edits

- Treat Category A modules as shared-core candidates
- Treat Category B modules as manual-only
- Treat Category C modules as daemon-only
- Do not move Category B or C modules into the vendored shared core

Exit criteria:

- every extracted module is explicitly assigned to one boundary category in this document

### Slice B: Normalize `workflow_runtime.py` contract

- Decide one contract and apply it consistently:
  - either keep it as a hook-based adapter module
  - or convert it fully to direct-import shared-runtime helpers
- Do not partially convert individual functions while leaving sibling wrappers/callers on the old contract
- If converted to direct imports, update both:
  - `manual_runtime_deps.py`
  - `shared_runtime_deps.py`
- Add targeted tests that call the wrapper modules through the real function signatures they expose

Exit criteria:

- no `workflow_runtime.py` helper has ambiguous "sometimes hooks, sometimes direct import" calling expectations

### Slice C: Normalize `step_execution_runtime.py` contract

- Split the work by responsibility instead of editing opportunistically:
  - one-step prepare/execute flow
  - coder resolution
  - generated-doc prompt augmentation/frontmatter rules
- Decide which pieces are pure shared-core helpers and which pieces remain adapter-driven
- Update wrapper call sites in both:
  - `run_agent.py`
  - `shared_runtime_deps.py`
- Keep manual workflow behavior unchanged while tightening the signature boundary

Exit criteria:

- `step_execution_runtime.py` no longer mixes changed function signatures with stale wrappers

### Slice D: Keep CLI/manual and daemon shims thin

- `manual_runtime_deps.py` should only expose the minimum hook surface required by `manual_runtime.py` and manual CLI helpers
- `shared_runtime_deps.py` should only expose the minimum hook surface required by daemon/backend execution
- Remove duplicated helper ownership where a stable shared module already exists
- Do not let `shared_runtime_deps.py` become a second source of truth for generic runtime behavior

Exit criteria:

- both shim modules are narrow adapters, not partial implementations

### Slice E: Add boundary-regression tests before Phase 4

- keep the existing governance workflow manual rerun as the main regression gate
- add wrapper-smoke tests for:
  - `manual_runtime_deps.py -> workflow_runtime.py`
  - `shared_runtime_deps.py -> workflow_runtime.py`
  - `run_agent.py -> step_execution_runtime.py`
  - `shared_runtime_deps.py -> step_execution_runtime.py`
- ensure tests fail if a function signature is changed without synchronizing wrappers

Exit criteria:

- the specific regression pattern from the reverted decoupling slice is covered by tests

Status:

- completed

## Target Architecture

### Shared Execution Core

Source repo: `agent-runner-v2`

Responsibilities:

- execution request/result schemas
- one-step execution orchestration
- prompt resolution/rendering
- action/coder invocation flow
- step failure normalization
- normalized step result emission

Non-responsibilities:

- manual-mode job progression
- backend persistence
- worker claim logic
- approval routing policy
- CLI command parsing
- daemon supervision

### Manual Local Mode

Owned by `agent-runner-v2`

Responsibilities:

- local CLI/manual workflow execution
- local job state and resume behavior
- local retry/approval/routing behavior
- local workflow progression

### Daemon Mode

Owned by `agent-runner-backend`

Responsibilities:

- workflow sync and storage
- worker registration / heartbeat / claim
- daemon-mode run and step persistence
- approvals, transitions, and status progression
- artifact / event / review / progress persistence

## Implementation Phases

### Phase 1: Keep `00_core_governance_bootstrap_v1` as the regression baseline

- Use it to verify local manual mode throughout the refactor
- Do not redesign workflow behavior during the extraction work
- Do not modify non-migrated workflows while using this workflow as the regression baseline

Exit criteria:

- repeated local execution remains successful

### Phase 2: Finalize the standalone common execution module in `agent-runner-v2`

- Identify the exact shared execution files and boundaries
- Remove or isolate hard dependencies on manual orchestration internals
- Move failure normalization out of `job_state.py`
- Remove direct routing imports from the shared execution module
- Keep orchestration adapters outside the shared module

Exit criteria:

- the shared execution logic can be copied as a unit
- local manual mode still passes with the governance workflow

### Phase 3: Separate manual orchestration from daemon orchestration

- Make the code split explicit:
  - shared execution core
  - manual local orchestration
  - daemon/backend adapters
- Ensure backend API does not leak into manual local mode
- Ensure local job-state progression does not become daemon source of truth

Exit criteria:

- operation-mode boundaries are explicit and stable

### Phase 4: Vendor-copy the finalized common execution module into backend

- Copy the finalized shared execution module from `agent-runner-v2` into backend
- Preserve logic and structure
- Only adjust package/import roots
- Add backend adapters outside the vendored module
- Keep backend migration scope limited to migrated plugin workflows only
- Do not reintroduce backend seeding or non-migrated workflow fixtures

Exit criteria:

- backend uses the same execution logic as `agent-runner-v2`

#### Phase 4 Guardrails

- `agent-runner-v2` remains the source of truth for shared execution logic
- Backend receives vendor-copied modules; it does not become the design source
- Only migrated plugin workflows are in daemon/backend execution scope during this phase
- `00_core_governance_bootstrap_v1` is the only mandatory workflow regression target for this phase
- Manual local mode must remain unchanged while Phase 4 work proceeds
- Backend API remains daemon-mode only
- Backend must not restore `seed_workflow_definitions()`
- Non-migrated workflows must not be changed as collateral during Phase 4

#### Phase 4 Current Baseline

- Phase 3 is complete enough to begin vendor-copy work
- Backend already has a first backend-local worker adapter shell under:
  - `agent_runner_backend/workers/backend_client.py`
  - `agent_runner_backend/workers/agent_worker.py`
- That worker shell is incomplete by design:
  - CLI wiring is still placeholder
  - execute-step subprocess wiring is still placeholder
  - it is not yet using the full shared execution core
- Backend integration tests have already been narrowed to migrated-workflow scope:
  - the test fixture syncs `00_core_governance_bootstrap_v1`
  - legacy backend seeding assumptions were removed from the active integration path

#### Phase 4 Detailed Slices

##### Slice 4.1: Freeze the vendor-copy boundary

- Define the exact modules copied from `agent-runner-v2` into backend as the shared execution core
- Keep the copied surface limited to shared execution logic, not manual-mode orchestration
- Preserve code shape as closely as possible so future diff-sync stays mechanical
- Record the owning source modules in this plan before further backend edits

Modules intended for vendor-copy in this phase:

- `execution_request.py`
- `execution_result.py`
- `execution_core.py`
- `failure_runtime.py`
- `routing_runtime.py`
- `transition_runtime.py`
- `recovery_runtime.py`
- `task_runtime.py`
- `runtime_utils.py`
- `state_defaults.py`
- the shared-runtime portions of:
  - `backend_execution.py`
  - `workflow_runtime.py`
  - `step_execution_runtime.py`

Exit criteria:

- the vendor-copy scope is explicit
- backend-only adapters are clearly excluded from the copied core

##### Slice 4.2: Create the backend vendored execution package

- Add a dedicated backend package for the vendor-copied execution core
- Copy files from `agent-runner-v2` with import-root changes only
- Do not opportunistically redesign file structure during the copy
- Keep backend-specific wrappers outside the vendored package

Required outcome:

- backend has a stable internal execution package that can be refreshed from `agent-runner-v2`

Exit criteria:

- copied modules import cleanly under backend package roots
- no copied module imports `agent_runner_v2` directly at runtime

##### Slice 4.3: Add backend runtime adapters around the vendored core

- Build backend-local adapters equivalent to `shared_runtime_deps.py`
- Backend adapters should provide:
  - backend client access
  - workflow job-json helpers if still required
  - backend worker result submission/finalization hooks
  - config loading
  - execution subprocess bridging
- Keep these adapters thin; they are not allowed to become a second execution implementation

Exit criteria:

- backend worker path can call the vendored execution core through backend-owned adapters
- adapter functions remain thin wrappers, not reimplementations

##### Slice 4.4: Finish backend worker CLI and engine-resolution path

- Replace placeholder `arb-agent` worker entrypoint behavior with a real CLI
- Read the single global config:
  - `C:\Users\kengk\.ukbe-runner\config.json`
- Support:
  - worker id
  - worker label
  - backend url
  - poll interval
  - optional engine root override
  - single-shot / once mode if still useful for tests
- Wire execute-step subprocess invocation through the vendored shared execution path

Important constraint:

- backend worker may resolve an installed engine version from the global engine store
- backend worker must not require the `agent-runner-v2` source repo on `PYTHONPATH`

Exit criteria:

- `arb-agent` is a real backend worker command
- worker configuration uses the single global config path
- engine resolution and execute-step invocation work end-to-end

##### Slice 4.5: Narrow backend sync/test scope to migrated workflows only

- Keep backend sync behavior focused on plugin workflows that are already migrated
- Keep backend integration fixtures limited to `00_core_governance_bootstrap_v1` until further workflow migrations are explicitly approved
- Remove or quarantine stale tests that assume backend-owned legacy workflows

Exit criteria:

- backend tests do not rely on non-migrated workflow fixtures
- backend daemon-mode regression coverage is aligned with the current migration scope

##### Slice 4.6: Validate the copied-core contract

- Add contract tests proving backend vendored modules still match `agent-runner-v2` expectations
- Focus on stable payload boundaries:
  - `ExecutionRequest`
  - `ExecutionResult`
  - failure envelope shape
  - backend `step_execution_spec`
- Add smoke coverage for:
  - worker request payload building
  - execute-step subprocess wiring
  - worker result submission/finalization

Exit criteria:

- future drift between copied backend logic and `agent-runner-v2` is detectable by tests

##### Slice 4.7: Run the first daemon-mode migrated workflow through backend

- Use `00_core_governance_bootstrap_v1` as the only mandatory daemon-mode proof workflow
- Verify:
  - workflow sync to backend
  - worker claim / heartbeat / completion
  - review/refine/validate transitions
  - artifact registration
  - final completion path
- Keep this as the Phase 4 acceptance gate before broader backend-layer refactoring

Exit criteria:

- `00_core_governance_bootstrap_v1` runs successfully through backend daemon mode using backend-owned worker/runtime code

#### Phase 4 Execution Order

Work the slices in this order:

1. Slice 4.1
2. Slice 4.2
3. Slice 4.3
4. Slice 4.4
5. Slice 4.5
6. Slice 4.6
7. Slice 4.7

#### Phase 4 Done Definition

Phase 4 is complete only when all of the following are true:

- backend contains a vendor-copied shared execution core from `agent-runner-v2`
- backend worker CLI is real, not placeholder
- backend uses the single global config path
- backend daemon-mode tests are migrated-workflow only
- `00_core_governance_bootstrap_v1` succeeds through backend daemon mode
- manual local mode remains green in `agent-runner-v2`

### Phase 5: Refactor backend into `API -> Services -> DB`

API layer:

- split route modules by concern
- handlers do validation, service calls, response mapping only

Services layer:

- own workflow sync, claim, completion, approval, transition, and cleanup logic

DB layer:

- repositories own ORM queries only
- services own transaction boundaries and orchestration

Exit criteria:

- no orchestration-heavy route handlers
- no direct query-heavy persistence in API endpoints

### Phase 6: Repair backend tests and fixtures

- remove stale workflow seeding assumptions
- reduce ad hoc cross-repo imports
- add service-layer unit tests
- preserve integration coverage for daemon-mode flows

Exit criteria:

- backend tests reflect daemon-only architecture

### Phase 7: Migrate additional workflows

- keep governance bootstrap as regression baseline
- migrate one coder-heavy workflow
- migrate one action-heavy workflow
- migrate one daemon-relevant workflow

Exit criteria:

- multiple workflows succeed through the same shared execution core

## Stable Interfaces

These interfaces stay stable during the refactor:

- manual local CLI behavior in `agent-runner-v2`
- backend daemon API behavior
- `ExecutionRequest`
- `ExecutionResult`
- failure envelope shape
- backend `step_execution_spec`

## Test Strategy

Manual local mode:

- rerun `00_core_governance_bootstrap_v1`
- confirm validation and audit remain clean

Shared core:

- unit tests for request/result/failure handling
- unit tests for one-step execution orchestration with injected routers

Backend:

- service-level tests for workflow sync, claim, completion, transition, approval, and cleanup
- API integration tests for daemon-mode flows

Cross-repo:

- contract tests for request/result/failure/spec compatibility
- vendored-sync verification checks

## Assumptions

- Manual local mode remains a supported long-term mode
- Backend API is daemon-only
- Shared execution logic is authored in `agent-runner-v2` first
- Backend receives the vendored module from `agent-runner-v2`
- `00_core_governance_bootstrap_v1` remains the regression baseline during the refactor
- Non-migrated workflows remain read-only until their own migration phase is explicitly approved
