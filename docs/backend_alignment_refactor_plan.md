# agent_runner_v2 Backend Alignment Refactor Plan

## Objective

Refactor `agent_runner_v2` so it stops owning workflow orchestration state and becomes a backend-driven step execution runtime aligned with the new `agent-runner-backend` schema and API.

The backend now owns:

- workflow definitions
- workflow runs
- workflow step runs
- worker claiming
- human approval gates
- artifact/event/review persistence

`agent_runner_v2` should own only:

- prompt resolution and rendering
- execution context assembly
- coder invocation
- action execution
- sidecar/meta validation
- deterministic step result emission back to backend

## Current Architecture

### Runner-owned orchestration today

- `run_agent.py`
  - parses CLI
  - creates/loads jobs
  - resolves current step
  - handles admin commands
  - executes step and routes aftermath
- `job_state.py`
  - local `job.json` persistence
  - retry counters
  - loop and replan state
  - status transitions
  - job discovery/resume logic
- `workflow_router.py`
  - post-step routing
  - approval/rejection consequences
  - retry/failure classification aftermath
- `template_groups.py`
  - live workflow truth at execution time

### Execution core worth keeping

- `step_runner.py`
- `coder_adapters.py`
- `runner_actions.py`
- `artifact_paths.py`
- `runtime_context.py`
- prompt templates and action modules

## Target Architecture

Refactor into three layers.

### 1. Execution Core

Pure step execution with no ownership of workflow progression.

Responsibilities:

- build step context from a supplied execution request
- resolve prompt file and render prompt
- invoke coder or action
- validate `meta.json`
- validate output artifacts
- return normalized step result

Target modules:

- `step_runner.py`
- `coder_adapters.py`
- `runner_actions.py`
- extracted request/response schemas

### 2. Backend Worker Adapter

New backend-facing runtime layer.

Responsibilities:

- fetch or accept a claimed step-run payload
- map backend payload into local execution request
- execute exactly one step
- post step completion, review payload, artifacts, events, and failure envelopes back to backend

Target new modules:

- `backend_client.py`
- `worker_protocol.py`
- `execute_step.py` or equivalent adapter layer

### 3. Legacy Local Orchestrator

Temporary compatibility layer only.

Responsibilities:

- keep current `run` CLI working during migration
- bridge local job.json state into new execution request shape where needed
- gradually shrink until removable

Modules to phase down:

- `run_agent.py`
- `job_state.py`
- `workflow_router.py`

## Main Refactor Principle

The runner must no longer decide the next step.

That means:

- no local workflow advancement as source of truth
- no local retry policy as source of truth
- no human approval state owned in local `job.json`
- no local workflow definition lookup required for routing decisions

The backend should send enough information for one step execution, and the runner should return one step result.

## Proposed Execution Request Contract

Introduce a single backend-friendly execution request object.

```json
{
  "workflow_name": "initiative_intake_v1",
  "template_group": "initiative_intake_v1",
  "workflow_run_id": "uuid",
  "workflow_step_run_id": "uuid",
  "step_name": "pre_init",
  "project_root": "/workspace/projects/repo",
  "workspace_root": "/workspace/projects/repo",
  "delivery_root": "/workspace/projects/repo",
  "context_payload": {},
  "input_artifacts": {},
  "env_overrides": {},
  "coder_override": null,
  "step_config": {},
  "workflow_config": {}
}
```

Notes:

- `step_config` can initially still come from local `template_groups.py` if backend does not yet provide it.
- long term, backend should provide canonical step config payload directly.
- `template_group` may remain as a compatibility alias for `workflow_name` during transition.

## Proposed Execution Result Contract

Runner returns a normalized payload that backend can persist directly.

```json
{
  "status": "completed|failed",
  "outcome": "approved|rejected|success|fatal|auto_retryable",
  "step_name": "pre_init",
  "coder_used": "claude",
  "remark": "...",
  "artifacts": {},
  "meta_json_path": "...",
  "review": null,
  "usage": {},
  "failure": null
}
```

For failure cases:

```json
{
  "status": "failed",
  "outcome": "fatal",
  "failure": {
    "failure_class": "FATAL|AUTO_RETRYABLE|HUMAN_RETRY_REQUIRED",
    "failure_code": "...",
    "failure_reason": "...",
    "failure_source": "runner|adapter|model|validator"
  }
}
```

## Refactor Phases

## Phase 1: Define the seam

Goal:

- create explicit request/response types for single-step execution
- isolate current step execution from orchestration logic

Tasks:

- add `execution_request.py` and `execution_result.py` or equivalent types
- wrap current `run_step()` invocation behind a new `execute_single_step(request)` function
- move any state mutation not required for execution out of the direct execution path

Exit criteria:

- one step can be executed from a plain request object without loading local job state

## Phase 2: Extract backend-facing worker mode

Goal:

- add a new CLI mode dedicated to backend-driven step execution

Tasks:

- add new command, for example:
  - `ukbe-run-agent execute-step --request-file ...`
  - or `ukbe-run-agent worker --backend-url ... --worker-id ...`
- implement backend payload ingestion
- emit structured JSON result only

Exit criteria:

- a backend worker process can call the runner without invoking local workflow routing

## Phase 3: Minimize `job_state.py`

Goal:

- stop using `job.json` as the primary orchestration store

Tasks:

- identify which `job_state.py` functions are still needed only for local compatibility
- split into:
  - local compatibility helpers
  - deprecated orchestration helpers
- stop introducing new logic into job-state routing helpers

Functions likely to deprecate first:

- `create_job`
- `advance_step`
- local retry and rejection counters
- local job discovery/resume functions
- approval mutation helpers tied to `job.json`

Exit criteria:

- backend mode runs without `create_job`, `load_job`, or `save_job` in the hot path

## Phase 4: Quarantine `workflow_router.py`

Goal:

- prevent local routing from remaining a hidden source of truth

Tasks:

- restrict `workflow_router.py` to legacy CLI path only
- create a backend-mode execution path that never calls `route_after_step()` or `route_after_failure()`

Exit criteria:

- backend worker path only reports results, never advances step state locally

## Phase 5: Reduce dependency on `template_groups.py`

Goal:

- make workflow definition lookup backend-driven over time

Short term:

- still use local `template_groups.py` for prompt/config lookup
- optionally allow backend payload to override selected fields

Medium term:

- backend sends step config payload directly
- runner validates shape but does not own canonical workflow definitions

Exit criteria:

- local workflow definitions are cache/input data, not orchestration truth

## Phase 6: Remove obsolete local workflow commands

Goal:

- retire local orchestration mode once backend worker path is stable

Tasks:

- deprecate `--approve-step`, `--force-approve-step`, `--override-step`, local resume/reapply routing commands
- remove local loop/replan ownership from the default path

Exit criteria:

- `run_agent.py` becomes a thin CLI over execution and worker commands

## File-by-File Plan

### `run_agent.py`

Keep for now, but split into:

- legacy local orchestration command
- new backend execution command
- shared request-building helpers

### `step_runner.py`

Primary extraction target.

Changes:

- accept execution request data instead of implicit local job state assumptions
- keep sidecar validation logic
- keep artifact validation logic
- make result payload backend-ready

### `coder_adapters.py`

Keep and harden.

Changes:

- normalize invocation result format across coders
- keep model selection and sidecar path support
- make error envelopes backend-friendly

### `job_state.py`

Shrink aggressively.

Changes:

- stop using as the default source for backend mode
- move only compatibility-safe helpers forward
- mark orchestration-heavy functions as legacy path

### `workflow_router.py`

Freeze for legacy mode only.

Changes:

- no new backend-mode logic here
- add explicit comments that this module is deprecated for backend-driven execution

### `template_groups.py`

Keep short term.

Changes:

- no new routing logic
- prepare for eventual export/consumption model with backend

## First Implementation Slice

This is the slice to build next, before any large deletions.

1. Add explicit execution request/result dataclasses.
2. Add `execute-step` CLI command.
3. Implement a code path that executes one step from a provided request file.
4. Ensure output is structured JSON only.
5. Keep legacy `run` command untouched except for sharing execution helpers.

This slice is enough to let the backend worker integration begin without finishing the full cleanup.

## Existing Local Changes To Preserve

Current branch already contains relevant local edits in:

- `step_runner.py`
  - producing-step `meta.json` fallback support
- `job_state.py`
  - skip refine/replan steps in next-step resolution
- `coder_adapters.py`
  - Claude model and permission-mode adjustments

These should be preserved and carried into the refactor, not discarded.

## Risks

### Dual workflow truth

Biggest architecture risk.

If both backend and runner keep independently evolving workflow routing behavior, the system will drift. Avoid adding new routing behavior locally.

### Hidden local state dependencies

`step_runner` and prompt context logic still assume local workspace/job directory conventions. These assumptions need to be surfaced explicitly in the execution request.

### Mixed compatibility surface

Keeping both legacy local orchestration and backend mode temporarily is necessary, but it increases confusion. New work should target backend mode only.

## Success Criteria

The refactor is successful when:

- a worker can execute a claimed backend step-run without local job orchestration
- `agent_runner_v2` returns normalized step results only
- backend owns advancement, retries, approvals, and event persistence
- local `job.json` is no longer required for the primary runtime path

## Immediate Next Tasks

1. Add execution request/result schemas.
2. Add `execute-step` CLI path in `run_agent.py`.
3. Extract shared single-step execution helper from current `main()` path.
4. Add a minimal backend client contract placeholder.
5. Add tests for backend-mode single-step execution.
