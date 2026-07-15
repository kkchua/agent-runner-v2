# Daemon Manual Execution Unification Plan

## Purpose

This document defines the target refactor for unifying manual execution and
daemon execution.

The user intent is explicit:

- manual execution should run through `run_agent.py`
- daemon mode should not own a separate execution engine
- daemon should claim work from backend, invoke the same runner execution path
  used by manual mode, wait for completion, read generated files, and sync the
  result back to backend

This document supersedes any design direction where daemon execution keeps its
own workflow-loading, role-policy, coder-resolution, or prompt-resolution
logic.

## Problem Statement

The current split is wrong:

- manual mode runs through `agent_runner_v2/run_agent.py`
- daemon/backend mode runs through `agent_runner_v2/backend_execution.py`
- backend/daemon execution reconstructs workflow bundle context separately
- this has already caused runtime drift such as:
  - different workflow-bundle root resolution
  - different `_registry` resolution
  - different `role_policies.json` load behavior
  - bootstrap-path fallback showing up in daemon mode

That architecture is too fragile.

## Core Decision

`run_agent.py` must become the single workflow step execution engine.

Daemon mode must become transport/orchestration only.

Target responsibility split:

### `run_agent.py`

Owns:

- workflow bundle resolution
- `_registry` resolution
- coder role resolution
- role policy resolution
- connection resolution
- prompt resolution
- action execution
- step execution
- artifact writing
- `job.json` updates
- `meta.json` sidecar generation
- progress file generation

### Daemon

Owns only:

- worker registration
- heartbeat
- claiming step-runs from backend
- translating a claimed backend step into a `run_agent.py` machine-mode request
- launching `run_agent.py`
- waiting for completion
- harvesting output files
- POSTing completion/artifacts/progress/review back to backend

### Backend

Owns only:

- worker registry
- workflow/run/step persistence
- queueing and claiming
- artifact/event/review persistence
- approval state transitions
- storing workflow definitions

Backend must not become a second execution runtime.

## Target Execution Model

The intended steady-state daemon flow is:

1. daemon registers worker
2. daemon heartbeats
3. daemon claims a pending step from backend
4. daemon writes a local machine request payload
5. daemon launches `run_agent.py` in a strict single-step machine mode
6. `run_agent.py` executes the claimed step using the same runtime path as
   manual mode
7. `run_agent.py` writes normal local outputs
8. daemon waits for process exit
9. daemon reads the generated output files
10. daemon maps those outputs back into backend API calls
11. daemon heartbeats final status and loops for the next claim

The intended steady-state manual flow is:

1. user launches `run_agent.py`
2. `run_agent.py` resolves workflow and executes directly
3. `run_agent.py` writes the same normal local outputs

The only difference between daemon and manual should be:

- who initiates execution
- whether backend transport is involved

The step execution engine must be the same.

## Filesystem Truth Model

The daemon must treat local runner output files as the execution source of
truth.

At minimum:

- `job.json`
- step `meta.json`
- step artifacts
- `progress.jsonl`
- optional review sidecars / review markdown files where applicable

Daemon should not infer authoritative completion details from stdout.

Stdout/stderr are debugging surfaces only.

## Design Requirement

The daemon must not call the old backend-only execute-step path as the
authoritative runtime.

Instead, daemon should invoke a dedicated machine-mode entry in
`run_agent.py`, for example:

```text
ukbe-run-agent execute-claimed-step --request-json <path>
```

Equivalent naming is acceptable, but the contract must be explicit:

- execute exactly one claimed step
- do not perform manual CLI flow resolution beyond what is needed for the
  claimed step
- emit deterministic machine-readable outputs through the normal runner files

## Request Payload Contract

Daemon should translate a claimed backend step into a local request payload.

The request JSON should contain at least:

- `workflow_name`
- `template_group`
- `job_id` or `run_code`
- `step_name`
- `step_sequence_no`
- `workflow_run_id`
- `workflow_step_run_id`
- `project_root`
- `target_project_root` if applicable
- `input_payload`
- `context_payload`
- `env_overrides`
- `coder_override` if any
- `backend_url`
- `worker_id`
- `worker_label`

Optional:

- precomputed backend `step_execution_spec`
- backend transport metadata
- retry/attempt metadata if backend tracks it

## Machine-Mode `run_agent.py` Contract

`run_agent.py` needs a dedicated single-step machine mode.

It should:

1. load request JSON
2. resolve workflow bundle using the same installed-global logic as manual mode
3. reconstruct execution state from the request payload
4. execute exactly the requested step
5. write normal runner outputs
6. write a small deterministic machine result JSON
7. exit with stable status codes

The machine result JSON should contain at least:

- `status`
- `workflow_name`
- `template_group`
- `job_id`
- `step_name`
- `step_dir`
- `meta_json_path`
- `job_json_path`
- `progress_jsonl_path` when present
- `artifacts`
- `return_code`
- `error_class`
- `error_message`

## Why Not Reuse Backend Execution As-Is

The existing backend execution adapter grew into a second runtime:

- bundle reconstruction
- bundle-root fallback logic
- step-spec to step-config interpretation
- daemon-specific runtime branching

That is precisely what caused drift.

The target is not to keep improving that split.

The target is to remove that split from the execution core.

## Phase Plan

### Phase 1

Define the machine-mode execution contract inside `run_agent.py`.

Deliverables:

- new `run_agent.py` subcommand for claimed-step execution
- request JSON schema/contract
- result JSON schema/contract
- unit tests for request parsing and result emission

### Phase 2

Refactor shared execution so manual mode and machine mode call the same step
execution orchestration.

Deliverables:

- shared helper for “execute one prepared step from provided state/request”
- no duplicate workflow/coder/prompt resolution path for daemon mode
- manual mode behavior unchanged

### Phase 3

Convert daemon to launch `run_agent.py` instead of using its own backend-only
execution engine.

Deliverables:

- daemon claim loop writes request JSON
- daemon invokes `run_agent.py` subprocess
- daemon waits for completion and captures exit status
- daemon reads local runner output files

### Phase 4

Map local runner outputs back into backend persistence APIs.

Deliverables:

- completion payload submission from filesystem truth
- artifact registration from generated artifact files
- progress sync from `progress.jsonl`
- review/result sync from `meta.json` and related review artifacts

### Phase 5

Deprecate backend-only execution runtime paths.

Deliverables:

- shrink `backend_execution.py` to compatibility or transport helpers only
- remove bootstrap-based runtime fallback from daemon execution
- remove duplicate runtime interpretation where no longer needed

### Phase 6

Harden operational behavior.

Deliverables:

- clearer daemon logs showing:
  - claimed workflow
  - template group
  - step name
  - resolved coder role
  - resolved coder
  - connection/provider
  - model
- timeout, cancellation, and crash-handling coverage
- deterministic recovery on subprocess failure

## Detailed Work Breakdown

### Workstream A: `run_agent.py` Machine Mode

Tasks:

- add dedicated subcommand for claimed-step execution
- load request JSON from file
- reuse manual workflow-root resolution
- reuse normal step execution/preparation helpers
- emit deterministic machine result file
- ensure non-zero exit codes are stable and documented

### Workstream B: Daemon Request Translation

Tasks:

- map backend claim response into request JSON
- persist request JSON under the step job folder
- launch subprocess with explicit working directory
- stream or snapshot stderr/stdout for diagnostics only

### Workstream C: Output Harvesting

Tasks:

- read `job.json`
- read step `meta.json`
- detect progress file path
- collect artifact paths/checksums
- collect review decisions/findings where present
- map local result into backend completion payload

### Workstream D: Compatibility Boundary

Tasks:

- preserve current backend API contract for claim/complete where feasible
- make daemon translation responsible for contract adaptation
- do not let backend execution semantics leak back into `run_agent.py`

### Workstream E: Drift Elimination

Tasks:

- remove runtime use of packaged bootstrap registry in daemon execution
- ensure both modes resolve:
  - workflow root
  - `_registry/coder_roles.json`
  - `_registry/coder_connections.json`
  - `_registry/role_policies.json`
  from the same installed-global workflow root

## Logging Requirements

Daemon logs should clearly show:

- claimed run id / step-run id
- workflow name
- template group
- local request file path
- launched `run_agent.py` command
- local output file paths
- resolved coder role
- resolved coder executable
- resolved connection/provider
- resolved model
- backend completion submission result

`unknown` or missing identifiers should be treated as defects in the mapping
layer.

## Error Handling Rules

If `run_agent.py` fails before writing `meta.json`:

- daemon marks the step as failed
- daemon includes stderr/stdout snippets for diagnostics
- daemon persists a structured failure reason to backend

If `run_agent.py` writes `meta.json` but exits non-zero:

- daemon should still read and trust the written sidecar/result files first
- process exit code alone must not override valid local result files

If output files are partially written:

- daemon should classify the result as transportable failure
- include which required files were missing or invalid

## Testing Strategy

Required test coverage:

### Unit Tests

- request JSON parsing
- machine-mode result emission
- daemon request translation
- filesystem result harvesting
- registry resolution parity between manual and daemon

### Integration Tests

- daemon claim -> `run_agent.py` -> backend completion
- approval-required step path
- rejected/refine loop path
- artifact registration path
- progress sync path
- crash before sidecar path

### Regression Tests

- manual mode and daemon mode resolve the same:
  - workflow root
  - role policies
  - coder roles
  - coder connections
- daemon no longer uses packaged bootstrap registry as runtime source

## Migration Constraints

- do not break current manual execution behavior
- do not require backend schema changes in the first pass
- preserve current local artifact and sidecar conventions
- keep daemon transport backward-compatible where possible during transition

## Acceptance Criteria

This refactor is complete when:

1. daemon does not own a separate execution engine
2. daemon invokes `run_agent.py` for claimed step execution
3. manual mode and daemon mode resolve the same installed-global workflow root
4. manual mode and daemon mode load the same `_registry` files
5. backend receives completion/artifact/progress results derived from runner
   output files
6. packaged bootstrap is no longer used as a runtime fallback for daemon step
   execution
7. role policy, coder role, connection, and prompt resolution behavior is the
   same in manual and daemon execution

## Recommended Implementation Order

1. add machine-mode subcommand to `run_agent.py`
2. refactor daemon to write request JSON and launch `run_agent.py`
3. harvest `meta.json` / `job.json` / artifacts back into backend
4. remove bootstrap-based runtime fallback from daemon execution
5. deprecate or shrink old backend-only execution helpers

## Current Recommendation

Do not continue expanding `backend_execution.py` as a second execution path.

Use it only as a temporary bridge until daemon fully shells into the
`run_agent.py` machine mode and the old duplicate runtime path can be retired.
