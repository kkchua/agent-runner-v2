---
template_id: SYS-02-RM
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 runtime model; defines the execution architecture of agent-runner-v2"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02AR-20260721-f004b712"
---

# Runtime Model

## Purpose

This document defines the execution architecture of agent-runner-v2. It
describes the step model, the two execution paths (daemon and manual),
the job lifecycle, coder integration, the rejection and retry model,
and the notification model.

## Step Model

agent-runner-v2 executes workflows as a sequence of steps. Each step is
one of two fundamental types:

### Prompt-Driven Steps

A prompt-driven step sends a prompt to an external coding assistant
(coder) via CLI subprocess invocation. The coder reads the prompt,
performs the requested work, and reports results through a meta.json
sidecar file. The runner manages coder invocation through the
`invoke_coder()` function in `coder_adapters.py`.

Prompt-driven step types:

- `generate` -- Creates draft artifacts (documents, plans, code).
- `review` -- Examines artifacts for scope, quality, and boundary
  compliance. Returns an APPROVED or REJECTED status.
- `refine` -- Revises artifacts after fixable review or validation findings.
- `audit` -- Performs final semantic verification before approval.

### Action Steps

An action step invokes a registered Python function within the runner
process. No external coder subprocess is spawned. Action functions are
registered via the `@action()` decorator (see the Bundle Authoring
Contract and Shared Services documents). Action steps are dispatched by
`run_action()` in `step_runner.py`.

Action step types:

- `collect_context` -- Gathers curated reference inputs.
- `validate` -- Runs deterministic rules against artifacts.
- `publish` -- Marks an approved artifact set as active.
- `step_completion` -- Closes the workflow execution.
- `human_approval` -- Obtains explicit operator acceptance before
  activation.

### Step Execution

Prompt-driven steps and action steps share a common return contract.
Both produce a `StepResult` dataclass (`step_runner.py`) containing:

- `status` -- "APPROVED" or "REJECTED"
- `remark` -- Human-readable summary
- `artifacts` -- Dict of artifact key to file path
- `reject_code` -- Optional reason code for rejection
- `meta_json_path` -- Repository-relative path of the meta.json file
- `usage_data` -- Token usage and cost metrics

## Execution Paths

agent-runner-v2 supports two execution modes: daemon and manual.

### Daemon Mode

In daemon mode (`daemon.py`, `daemon_runtime.py`), the runner runs as a
long-lived worker process that communicates with a remote backend
server. The daemon:

1. Registers itself with the backend via `BackendClient.register_worker()`.
2. Polls for available workflow steps via `BackendClient.claim_step()`.
3. Executes each claimed step through the shared `run_step()` /
   `run_action()` entry points in `step_runner.py`.
4. Reports results back to the backend via `BackendClient.sync_job_state()`.
5. Sends periodic heartbeats via `BackendClient.heartbeat()`.

The daemon uses the `BackendClient` class (`backend_client.py`) for all
backend communication. Job state is managed by `job_state.py` and
synchronized through `backend_execution.py`.

### Manual Mode

In manual mode (`manual_runtime.py`, `manual_runtime_deps.py`), an
operator invokes the runner directly via CLI. The runner:

1. Loads the workflow bundle from disk via `bundle_loader.py`.
2. Walks the step sequence defined in the workflow manifest.
3. Executes each step through the same `run_step()` / `run_action()`
   entry points.
4. Reports results to stdout and the local file system.

Manual mode uses the same execution core (`execution_core.py`) as
daemon mode. The execution logic is shared; only the orchestration
wrapper differs.

### Shared Execution Core

Both modes converge on the same execution functions:

- `run_step()` in `step_runner.py` -- Executes prompt-driven steps.
- `run_action()` in `step_runner.py` -- Executes action steps.

The `execution_core.py` module provides shared workflow-run lifecycle
management used by both paths. The `execution_support.py` module
provides auxiliary helpers such as logging, file system operations, and
step transition wiring.

## Job Lifecycle

A workflow job transitions through a defined lifecycle managed by
`execution_core.py` and tracked in `job_state.py`.

### Lifecycle States

1. **Init** -- The job is created. The workflow manifest is loaded,
   the step sequence is validated, and the initial context is built.
   Managed by `execution_request.py`.

2. **Execute** -- Steps are executed in order. Each step's coder
   configuration is resolved from `coder_registry.py`. The step
   produces artifacts and returns a status (APPROVED or REJECTED).

3. **Review / Refine Loop** -- When a step returns REJECTED, the
   workflow checks the `on_reject_refine` configuration in
   `workflow.toml`. If a refine step is declared and iteration budget
   remains, the workflow routes to the refine step, then returns to
   the rejected step. This loop continues until the step is approved
   or the budget is exhausted.

4. **Approve** -- When all steps in the main sequence return APPROVED,
   the workflow proceeds to the publish step. The approved artifacts
   are marked for activation.

5. **Publish** -- The publish step moves approved artifacts from the
   staged (`runs/`) location to the active (`current/`) location,
   updates the publish manifest, and supersedes any prior active
   version. Historical snapshots are retained under `history/`.

6. **Complete** -- The workflow emits a final notification, records
   completion state, and terminates.

### State Tracking

The job's current state is persisted in `job.json` (`job_state.py`),
which records:

- Current step and step index
- Completed step outcomes
- Artifacts produced
- Loop iteration count
- Coder used per step
- Event history

State is synchronized to the backend via `sync_job_state()` for
daemon runs and written to the local file system for manual runs.

## Coder Integration

### Coder Roles

The platform supports multiple coding agent backends, each identified
by a coder name (e.g., `qwen`, `claude`, `codex`, `opencode`). Coder
selection is configured per step in `workflow.toml` via the
`[step.coder]` subsection.

### Coder Registry

The `coder_registry.py` module maintains the registry of available
coder backends. Each entry defines:

- Coder name and metadata
- Model identifier
- Connection profile (API endpoint, auth type)
- Role policies (allowed roles per coder)
- Default timeout and configuration

### Coder Adapters

The `coder_adapters.py` module implements the coder invocation protocol.
Key functions:

- `invoke_coder()` -- Spawns a coder subprocess with the rendered prompt.
  Handles timeout, sidecar path injection, stdin prompt delivery, and
  exit-code handling. Returns an `InvocationResult` dataclass. Raises
  `CoderInvocationError` on process failure.

- `sidcar_poll` -- The coder is expected to write a meta.json sidecar
  before exiting. The runner polls for this file with a configurable
  interval (`SIDECAR_POLL_INTERVAL_SECONDS`) and a settle delay
  (`SIDECAR_SETTLE_DELAY_SECONDS`).

### Invocation Protocol

1. The runner renders the prompt with all context variables.
2. The runner resolves the meta.json sidecar path.
3. The runner invokes the coder CLI with the prompt and sidecar path.
4. The coder performs the requested work.
5. The coder writes the meta.json sidecar before exiting.
6. The runner reads and validates the sidecar, then enriches it with
   runner metadata.

## Rejection And Retry

### Rejection Model

A step returns REJECTED when the coder (or action function) determines
the work cannot be approved. Rejections carry an optional `reject_code`
to classify the reason:

- `scope_violation` -- Output violates layer boundaries.
- `quality_defect` -- Output has fixable quality issues.
- `missing_content` -- Required sections or artifacts are absent.
- `metadata_error` -- Frontmatter or classification is incorrect.
- `systemic_failure` -- The defect cannot be fixed through refinement.

### Refinement Loop

When a step returns REJECTED:

1. The runner inspects the step's `on_reject_refine` configuration.
2. If a `refine_step` is declared and `max_iterations` has not been
   reached, the workflow routes to the refine step.
3. The refine step revises the artifacts and returns control to the
   original step.
4. The original step re-executes. If it returns APPROVED, the loop ends.
5. If `max_iterations` is exhausted, the workflow routes to failure or
   an `on_exhaust_replan` step.

### Routing Rules

- Fixable defects route to refine (quality_defect, missing_content,
  metadata_error).
- Conceptual layer mismatch (scope_violation, systemic_failure) routes
  to failure without refinement.
- Wrong document inventory routes to failure.
- Platform identity missing routes to failure if systemic, refine if
  isolated.

### Failure Handling

When a step fails (coder crash, timeout, irrecoverable rejection), the
workflow transitions to a failure state managed by `failure_runtime.py`.
The failure handler:

1. Logs the error details.
2. Sends a failure notification (if notifications are enabled).
3. Records the failure in job state.
4. Syncs the failed state to the backend.

### Notification Model

The notification system (`notification_manager.py`,
`notifications.py`) sends alerts at key lifecycle events:

- Workflow started, completed, failed
- Step completed, rejected, failed
- Human approval requested
- Daemon worker status changes

Notifications are configured through the runner config file
(`~/.ukbe-runner/config.json`) and dispatched through configurable
channels (webhook, console).

### Meta Sidecar as Communication Channel

The meta.json sidecar is the primary communication channel between the
coder and the runner. The coder writes results to this file, which the
runner reads after coder completion.

The runner also provides a repair fallback via
`_repair_or_validate_meta_json()` in `step_runner.py`. If the coder
does not write a meta.json file, the runner inspects the coder's
parsed stdout output. If that output contains a result object with
`status` and `artifacts` fields, the runner constructs a valid
meta.json from that output. If the sidecar exists but fails schema
validation, the runner attempts to coerce the invalid content into a
valid v2 payload. This repair ensures compatibility with coders that
emit results directly rather than writing a sidecar file. Bundles
should not rely on this repair; they should always instruct the coder
to write the sidecar explicitly.
