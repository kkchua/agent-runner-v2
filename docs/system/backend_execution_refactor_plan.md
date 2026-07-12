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

Incomplete:

- The common execution logic is not yet fully standalone
- It still has orchestration coupling to:
  - `job_state.py`
  - `run_agent.py`
- Backend has `api`, `services`, and `database` folders, but the behavioral split is still weak
- Backend route handlers still contain too much query and orchestration logic

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

- Copy the shared module from `agent-runner-v2` into backend
- Preserve logic and structure
- Only adjust package/import roots
- Add backend adapters outside the vendored module

Exit criteria:

- backend uses the same execution logic as `agent-runner-v2`

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
