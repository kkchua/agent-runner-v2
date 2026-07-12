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

Incomplete:

- The common execution logic is not yet fully standalone
- It still has orchestration coupling to:
  - `job_state.py`
  - `workflow_router.py`
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
