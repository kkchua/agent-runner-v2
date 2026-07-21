---
template_id: "SYS-02-RM"
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 runtime model for agent-runner-v2"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02AR-20260721-2eaba4b3"
---

# agent-runner-v2 Runtime Model

## Step Model

The platform distinguishes two fundamental step types that run in different execution paths within the same runner process.

### Prompt-Driven Steps

Prompt-driven steps invoke an external coding agent (a CLI coder such as Claude Code or Qwen Code) to process a rendered prompt and produce artifact outputs.

The primary execution entry point is `run_step()` in `step_runner.py`. This function:

1. Resolves the meta.json path from step configuration and context.
2. Validates the step's write contract (produces/updates declarations).
3. Snapshots the allowed write paths for filesystem audit.
4. Invokes the coder via `invoke_coder()` from `coder_adapters.py`.
5. Reads and validates the coder-produced meta.json sidecar.
6. Validates that declared produced artifacts exist on disk.
7. Enriches the sidecar with runner metadata and returns a `StepResult`.

The meta.json sidecar (`schema_version: "v2"`) is the primary communication channel between the coder and the runner. The coder writes this file to an expected path; the runner reads it to determine success/rejection and to discover the produced artifact paths.

The runner also repairs missing or invalid sidecars through `_repair_or_validate_meta_json()` in `step_runner.py`. If the coder produced a direct result object (shaped like `{"status": "APPROVED", "remark": "...", "artifacts": {...}}`) instead of the wrapped v2 sidecar format, the repair function coerces it into the expected schema. This repair fallback handles common coder output patterns where the model returns a result directly without wrapping it in a full meta.json sidecar. The docs must accurately describe both the primary sidecar channel and this repair fallback.

Prompt-driven step types include:

- `generate` -- creates draft artifacts
- `review` -- performs scope and quality review with pass/reject outcome
- `refine` -- revises artifacts after fixable findings
- `audit` -- performs final semantic verification

### Action Steps

Action steps execute Python functions registered via the `@action()` decorator. They do not invoke an external coder.

The execution entry point is `run_action()` in `step_runner.py`. This function:

1. Resolves the meta.json path.
2. Calls `execute()` from `runner_actions.py` to dispatch the action function.
3. Writes a meta.json from the returned `ActionResult`.
4. Validates produced artifacts and enriches the sidecar.

Action steps produce their own meta.json automatically -- action functions return an `ActionResult` dataclass and the runner writes the sidecar on their behalf.

Action step types include:

- `collect_context` -- gathers curated reference inputs
- `validate` -- runs deterministic rules against artifacts
- `publish` -- marks an approved set as active
- `step_completion` -- closes the workflow

### Human-Control Steps

A `human_approval` step type pauses execution to obtain explicit platform-owner acceptance before activation. This is typically used as a gate before publication.

## Execution Paths

The platform supports two execution paths, implemented by the same runner engine but with different top-level flows.

### Daemon Mode

In daemon mode, a long-running worker process polls a backend for work, claims steps, and spawns child processes.

The daemon is implemented in `daemon.py` and invoked via:

```
ukbe-run-agent daemon [worker-id]
```

The daemon lifecycle:

1. Registers with the backend via `BackendClient.register_worker()`.
2. Enters a polling loop, calling `BackendClient.claim_step()` for available work.
3. On claim, spawns a child process running the daemon worker mode.
4. Monitors child liveness with a watchdog loop (heartbeats, timeout detection).
5. On child completion, reads the result, submits to backend via `BackendClient.complete_step_run()`, and loops for more work.

Communication with the backend is via `BackendClient` in `backend_client.py`. The daemon sends periodic heartbeats keyed by `workflow_step_run_id` and reports child state changes.

### Manual Mode

In manual mode, a single workflow run is executed directly without a backend dependency:

```
ukbe-run-agent run <workflow_name> [options]
```

The runner accepts the workflow name, job_id, and optional overrides as CLI arguments. Daemon-like state management (polling, backend sync, worker registration) is bypassed. The same step execution engine handles both paths.

## Job Lifecycle

A job represents one complete workflow execution, consisting of a sequence of steps.

### Lifecycle States

1. **Init**: The job is created with state containing the workflow template, step list, and initial context. Backend mode: created via `BackendClient.submit_run()`. Manual mode: created via CLI arguments.

2. **Execute**: Steps run sequentially. Each step invokes either a coder (prompt-driven) or an action function, writes a meta.json sidecar, and returns a `StepResult` with `APPROVED` or `REJECTED` status.

3. **Loop (review/refine)**: If a step is configured with `on_reject_refine`, a `REJECTED` result triggers a loop: the runner executes a refine step and reruns the original step. Loops are bounded by maximum iteration counts declared in the step configuration.

4. **Approve**: When all required steps complete with `APPROVED`, the job state transitions to approval. A `human_approval` step may gate this transition.

5. **Publish**: An approved job may execute a `publish` action that copies the produced artifact set into the active published location, updates frontmatter from `draft` to `published`, and writes a publish manifest.

6. **Complete/Fail**: The job terminates either successfully (all steps approved, optional publish executed) or with a failure (coder error, irrecoverable rejection, backend error).

### Rejection Flow

When a step returns `REJECTED`, the runner checks the step configuration:

- If `on_reject_refine` is configured, the rejection routes into a refine loop (back to the generator step for correction).
- If no refinement is configured, or if the maximum loop count is exceeded, the job fails with the reject code and remark recorded in the step's meta.json.

## Coder Integration

The platform integrates with external coding agents through a pluggable adapter model.

### Coder Adapters

Coder adapters are implemented in `coder_adapters.py`. The `invoke_coder()` function accepts a coder name, step information, prompt text, working directory, and sidecar path. It:

1. Resolves the coder command from configuration.
2. Renders the prompt with platform-supplied context extensions.
3. Writes the prompt to a temporary file or pipes it to stdin.
4. Executes the coder process with a timeout.
5. Captures stdout, stderr, and raw events.
6. Attempts to parse a structured result from stdout (for the repair fallback).
7. Returns an `InvocationResult` containing the return code, stdout, stderr, usage data, and parsed result.

Coders are expected to write their result to the meta.json sidecar path passed via the prompt's sidecar instructions. The runner reads this file after the coder process completes.

### Coder Registry

The `coder_registry.py` module manages available coder configurations, including command paths, role assignments, and connection settings for each supported coding agent.

### Role Policies

Coder roles and their allowed operations are governed by role policies. For example, a review step may use a different coder model than a generate step, and a refine step may use yet another model. Role selection is declared per step in the workflow configuration.

## Rejection And Retry

The rejection model is built on explicit status codes returned through the meta.json sidecar.

### Rejection Sources

A step may be rejected by:

1. **Coder rejection**: The coder writes a meta.json with `status: "REJECTED"` and an optional `reject_code`. This is a deliberate rejection -- the coder determined the input or output was unacceptable.

2. **Runner rejection**: The runner rejects a step when:
   - The coder process fails (non-zero return code, timeout) -- raises `CoderInvocationError`.
   - The meta.json is missing (`MetaJsonMissingError`).
   - The meta.json is invalid (`MetaJsonInvalidError`).
   - Declared produced artifacts are missing on disk (`ArtifactMissingError`).
   - A validation action returns `REJECTED`.

3. **Backend rejection**: In daemon mode, the backend may reject a run or step externally.

### Retry Model

Retry is implemented through the `on_reject_refine` mechanism, not through blind automatic retry. When a step is rejected:

- If `on_reject_refine` is configured, the runner invokes the refine prompt, then reruns the original step. Each cycle increments a loop iteration counter.
- If `on_reject_refine` is not configured, or the maximum loop count is exceeded, the job fails.
- Execution errors (coder crashes, timeouts) are not retried -- they immediately fail the job.

### Notification Model

Notifications are managed by `notification_manager.py` and are optional, driven by user configuration.

The notification system distinguishes two event levels:

- **Workflow notifications**: Sent on job completion, failure, or when waiting for human intervention. Managed by `send_workflow_notification()`.
- **Step notifications**: Sent on step completion, failure, or rejection. Managed by `send_step_notification()`.

Notifications are enabled globally via the runner config file (`~/.ukbe-runner/config.json`, key `notification.enabled`). Individual step events can be toggled via `notification.step_events` settings. Step-level notifications also require the step configuration field `enable_notifications: true`.

In daemon mode, notifications are integrated with the backend sync protocol and leverage the same `BackendClient` for delivery when a backend is configured.
