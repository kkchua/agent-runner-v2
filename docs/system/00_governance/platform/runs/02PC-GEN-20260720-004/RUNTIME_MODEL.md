---
template_id: SYS-02-RM
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 runtime model; defines platform execution architecture"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-004"
managed_by: workflow-generated
---

# Runtime Model

## Purpose

This document defines the execution architecture of agent-runner-v2.
It describes the step model, execution paths, job lifecycle, coder
integration, rejection and retry model, and notification model.

All module references in this document point to source code files in
the `agent_runner_v2/` package. These modules are read-only reference
for this constitution -- they are not modified by the constitution
generation process.

## Step Model

agent-runner-v2 executes workflows as ordered sequences of steps. Each
step is defined in a `workflow.toml` manifest and loaded into a
`StepConfig` dataclass (defined in `workflow_packages/base.py`).

### Step Types

Every step is one of two kinds:

**Prompt-driven steps** render a prompt template (a `.txt` file in the
bundle's `prompts/` directory) with context variables, send it to a
coder (LLM), and read the result from a `meta.json` sidecar written by
the coder. The coder is the sole communication channel -- no stdout
parsing, no pre-invocation sidecar writes.

**Action-driven steps** invoke a registered Python function. Actions
are registered via the `@action()` decorator (defined in
`workflow_packages/actions/__init__.py`) and dispatched by the runner
before falling back to the global action registry.

### Step Configuration

Each `StepConfig` carries:

- **name** -- unique step identifier within the workflow
- **prompt_file** or **action** -- exactly one of these is set
- **artifact contract** -- `produces`, `required_inputs`,
  `optional_inputs`, `result_meta_key`, `target_artifact`, `edit_mode`
- **coder configuration** -- `coder_default`, `coder_allowed`,
  `coder_role_policy`, `coder_default_role`, `coder_allowed_roles`,
  `coder_must_differ`
- **routing** -- `on_approve`, `on_reject_refine`, `on_exhaust_replan`,
  `reject_code_routes`
- **review gating** -- `requires_human_approval_after`
- **behavior flags** -- `enable_notifications`, `post_action`

### Step Execution Contract

The core execution contract is implemented in `step_runner.py`:

1. Resolve the `meta.json` sidecar path
2. Validate the step's write contract
3. Invoke the coder (for prompt-driven steps) or dispatch the action
4. Read `meta.json` -- this is the sole communication channel
5. Validate that declared artifacts exist on disk
6. Return a `StepResult` with status, remark, artifacts, and usage data

The `StepResult` dataclass carries:

- `status` -- `"APPROVED"` or `"REJECTED"`
- `remark` -- human-readable summary
- `artifacts` -- mapping of artifact keys to file paths
- `reject_code` -- optional rejection classification
- `usage_data` -- token usage from the coder invocation

## Execution Paths

agent-runner-v2 supports three execution modes, all converging on the
same step execution core (`step_runner.py` + `workflow_router.py`).

### CLI Mode

Entry point: `run_agent.py` (CLI command `ukbe-run-agent run`).

The CLI loads configuration, resolves the job, runs preflight checks,
renders the prompt, calls `run_step()`, and routes the result via
`route_after_step()`. This is the direct execution path used from batch
files or terminal invocations.

### Daemon Mode

Entry point: `daemon_runtime.py` (CLI command `ukbe-run-agent daemon`).

The daemon polls a backend API for workflow claims. When a claim
arrives, the daemon spawns a fresh subprocess running
`python -m agent_runner_v2.run_agent run ...` for each workflow
invocation. This means code changes are picked up automatically without
restarting the daemon itself. Only changes to `daemon_runtime.py`
require a daemon restart.

The daemon is a fire-and-forget messaging layer. It does not contain
execution logic -- it delegates to the standard CLI subprocess path.

### Manual Mode

Entry point: `run_agent.py` with `--mode manual`.

Manual mode is identical to CLI mode but enables human-in-the-loop
approval gating. Steps with `requires_human_approval_after: true`
pause execution and wait for explicit human decision before continuing.

### Execution Core

All three modes share the same execution core:

- `step_runner.py` -- invokes coder, reads meta.json, validates
  artifacts
- `workflow_router.py` -- routes after step completion (approve, reject,
  refine, fail)
- `job_state.py` -- manages on-disk job state (job.json)
- `execution_core.py` -- `execute_routed_step()` and
  `invoke_prepared_step()` orchestration helpers

## Job Lifecycle

A job progresses through these lifecycle stages:

1. **Creation** -- `create_job()` in `job_state.py` initializes the job
   directory and `job.json` state file
2. **Preflight** -- `check_preflight_artifact_status()` validates that
   required input artifacts exist
3. **Step execution** -- each step runs through `run_step()` and
   `route_after_step()`
4. **Review/refine loops** -- rejected steps may enter refinement cycles
   controlled by `on_reject_refine` configuration
5. **Human approval** -- steps with approval gating pause for human
   decision via `approve_step()` or `force_approve_step()`
6. **Completion** -- final step completes the workflow; job status
   transitions to `COMPLETED` or `FAILED`
7. **Failure routing** -- `route_after_failure()` handles hard failures
  (coder invocation errors, missing meta.json, missing artifacts)

### Job State Schema

Job state is persisted in `job.json` within the job directory. The state
includes:

- `status` -- current job status
- `current_step` -- active step name
- `step_order` -- ordered list of step names
- `artifacts` -- mapping of artifact keys to resolved paths
- `reject_counts` -- per-step rejection counters
- `retry_history` -- log of retry attempts
- `completed_steps` -- list of successfully completed steps
- `usage` -- aggregated token usage

## Coder Integration

### Coder Invocation

Coders are invoked via `coder_adapters.py`. The `invoke_coder()`
function:

1. Resolves the coder command from configuration
2. Writes the prompt to a temporary file
3. Spawns a subprocess with the configured coder CLI
4. Polls for the `meta.json` sidecar to appear
5. Reads and returns the result as an `InvocationResult`

The `InvocationResult` dataclass carries:

- `return_code` -- process exit code
- `stdout` / `stderr` -- captured output
- `parsed_result` -- parsed meta.json content
- `usage` -- `UsageData` with token counts and duration
- `manifest` -- `InvocationManifest` with command, checksum, timestamps

### Coder Roles and Policies

Coder roles are resolved by `coder_registry.py`. The registry loads:

- **coder_connections.json** -- defines available coder connections
  (CLI commands, API endpoints, model configurations)
- **role_policies.json** -- maps role names to coder configurations
  (e.g., `architect_standard`, `reviewer_standard`, `refine_standard`,
  `validation_standard`)

Role resolution follows a priority chain:

1. Step-level override in `workflow.toml` (`[step.coder]` section)
2. Workflow-level registry in `_registry/role_policies.json`
3. Global runtime registry in `~/.ukbe-runner/_registry/`

### Coder Must-Differ

The `coder_must_differ` flag on a step enforces that the coder used for
that step must be different from the coder used for the previous step.
This prevents the same LLM from reviewing its own output without an
independent perspective.

## Rejection And Retry

### Post-Step Routing

After each step completes, `workflow_router.py` routes the job based on
the `StepResult`:

- **APPROVED** -- advance to the next step via `advance_step()`
- **REJECTED** -- check rejection routing:
  - If `on_reject_refine` is configured, enter the refinement loop
  - If rejection count exceeds `default_max_rejects`, fail the workflow
  - Otherwise, retry the same step

### Refinement Loop

The refinement loop is configured per-step in `workflow.toml`:

```
[step.on_reject_refine]
refine_step = "refine_name"
artifact = "ARTIFACT_KEY"
max_iterations = 3
exhausted_failure_code = "REFINE_EXHAUSTED"
```

When a step is rejected:

1. The reject count for that step increments
2. If the count exceeds `max_iterations`, the workflow fails with the
   `exhausted_failure_code`
3. Otherwise, execution routes to the `refine_step`
4. After refinement, execution returns to the original step

### Replan

If refinement is exhausted, `on_exhaust_replan` may route to a replan
step that restructures the approach before retrying.

### Reject Code Routes

Steps may define `reject_code_routes` to route specific rejection codes
to different handling paths. This allows fine-grained control over which
rejection reasons trigger refinement versus immediate failure.

### Failure Routing

Hard failures (coder invocation errors, missing meta.json, missing
artifacts) are routed by `route_after_failure()`. These are not
retryable through the refinement loop -- they indicate infrastructure or
contract violations.

## Notification Model

Notifications are managed by `notification_manager.py`. The notification
system provides:

- **Step notifications** -- sent after step completion, rejection, or
  failure
- **Workflow notifications** -- sent for workflow-level events (start,
  completion, approval requests)

### Configuration

Notifications are configured in `~/.ukbe-runner/config.json` under the
`notification` key:

- `enabled` -- global on/off switch
- `step_events` -- per-event-type toggles (`completed`, `rejected`,
  `failed`)
- Provider configuration (e.g., Pushover tokens)

### Integration

Steps opt into notifications via `enable_notifications: true` in their
`workflow.toml` configuration. The notification manager enriches the
context with job metadata before sending.

The notification system is independent of the execution path -- it works
identically in CLI, daemon, and manual modes.
