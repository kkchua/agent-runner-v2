---
template_id: SYS-02-RM
version: "1.0"
doc_type: "platform_standard"
authority: "platform-owned"
scan_policy: "include"
scan_reason: "permanent Layer 2 runtime model; defines the execution architecture for agent-runner-v2"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "02PC-20260720-fd35ddf1"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `publish_platform_core_set`
> This file is workflow-generated and protected from manual edits.

# Runtime Model

## Overview

The agent-runner-v2 runtime executes multi-step workflows defined in TOML
manifests. Each step is either prompt-driven (invoking an LLM coder) or
action-driven (calling a Python function). The runtime supports three
execution modes: CLI, daemon, and manual. The meta.json sidecar is the
sole communication channel between the coder and the runner.

## Step Model

### Prompt-Driven Steps

A prompt-driven step sends a rendered prompt template to an LLM coder.
The coder processes the prompt, writes output artifacts to disk, and
produces a `meta.json` sidecar reporting its result.

The module `step_runner.py` is the core execution engine. It:

1. Renders the prompt template with context variables (artifact paths,
   governance rules, job metadata).
2. Invokes the coder via `coder_adapters.py`.
3. Reads the `meta.json` sidecar produced by the coder.
4. Validates that required artifacts exist on disk.
5. Enriches the sidecar with execution metadata.

The meta.json sidecar is the ONLY communication channel. No stdout JSON
parsing, no pre-invocation sidecar writes, and no disk recovery functions
are used.

### Action-Driven Steps

An action-driven step calls a registered Python function decorated with
the `@action()` decorator. Actions perform deterministic operations such
as validation, publishing, context collection, or workflow completion.

Actions are defined in:

- `agent_runner_v2/actions/` : platform-level action modules (30+ actions:
  copy, validate, scan, publish, assemble, and others)
- The workflow bundle's `actions.py` : bundle-specific custom actions

After execution, the action writes a `meta.json` sidecar, following the
same contract as prompt-driven steps.

### Step Types

The platform recognizes these step intents:

| Step Type | Execution | Description |
|---|---|---|
| `generate` | Prompt-driven | Creates draft artifacts using an LLM coder. |
| `review` | Prompt-driven | Performs scope and quality review with pass/reject outcome. |
| `refine` | Prompt-driven | Revises artifacts after fixable review findings. |
| `audit` | Prompt-driven | Performs final semantic verification before approval. |
| `collect_context` | Action-driven | Gathers curated reference inputs for later steps. |
| `validate` | Action-driven | Runs deterministic rules against artifacts. |
| `publish` | Action-driven | Marks an approved set as active and records tracking metadata. |
| `step_completion` | Action-driven | Closes the workflow. |
| `human_approval` | Action-driven | Obtains explicit human acceptance before activation. |

Step intent is declared in the workflow's `workflow.toml` manifest. The
runner does not enforce step type semantics : it executes the step as
configured and routes based on the coder's reported status.

## Execution Paths

### CLI Mode

**Entry point:** `ukbe-run-agent run --template-group <name>`

The CLI invokes `run_agent.py` directly. The runner:

1. Loads the workflow bundle identified by `--template-group`.
2. Resolves the current step from job state or the workflow's init step.
3. Renders the prompt or dispatches the action.
4. Reads the `meta.json` sidecar.
5. Routes to the next step based on the coder's result status and the
   workflow's routing configuration in `workflow_router.py`.

CLI mode is typically used from batch files (`run-*.bat`) for direct,
interactive execution.

### Daemon Mode

**Entry point:** `ukbe-run-agent daemon [worker-id]`

The daemon (`daemon.py`) is a backend-polling supervisor. It:

1. Polls the backend for claimed workflow steps.
2. Spawns a fresh subprocess per step: `python -m agent_runner_v2.run_agent run ...`
   (identical to the CLI path).
3. Monitors child process liveness.
4. Writes child-scoped heartbeats keyed by `workflow_step_run_id`.
5. Continuously polls until terminated.

Because the daemon spawns a fresh subprocess for each workflow invocation,
code changes to the runner (except `daemon.py` itself) are picked up
automatically without restarting the daemon.

The daemon delegates to the same `run_agent.py` execution path used by CLI
mode. There is no separate daemon-only execution logic.

### Manual Mode

**Entry point:** `ukbe-run-agent run --mode manual`

Manual mode adds a human-in-the-loop approval gate. After each step that
requires approval (`requires_human_approval_after: true` in the step
config), the runner pauses and waits for human action through the approval
mechanism (batch file `run-approve-step.bat` or operator console).

## Job Lifecycle

### Init

A workflow begins when a job is created. The init step is resolved from
the workflow bundle's `init_step` field in `workflow.toml`. Job state is
written to `~/.ukbe-runner/jobs/<workflow_name>/<job_id>/job.json`.

### Execute

Each step is executed by `step_runner.py`. The runner:

1. Renders the prompt (or dispatches the action).
2. Invokes the coder via `coder_adapters.py`.
3. Reads `meta.json` from the coder's output.
4. Validates required artifacts exist.
5. Records usage data (tokens, duration, cost) in job state.

### Route

After execution, `workflow_router.py` determines the next step based on:

- The coder's reported status (`APPROVED` or `REJECTED`)
- The step's routing configuration (`on_approve`, `on_reject_refine`,
  `on_exhaust_replan`, `reject_code_routes`)
- Human approval requirements (`requires_human_approval_after`)

### Review / Refine Loop

When a review step returns `REJECTED` with fixable findings, the router
activates a refine loop (`on_reject_refine`). The refine step attempts to
correct the defects. The loop has a maximum iteration count
(`max_iterations`). If exhausted, the router activates a replan step
(`on_exhaust_replan`) or routes to failure.

### Approve

When a step requires human approval, the runner writes
`WAITING_FOR_HUMAN_INTERVENTION` status to job state and pauses. Human
approval is provided through `run-approve-step.bat` or the operator
console.

### Publish

The publish action copies approved artifacts from the staged run directory
to the active `current/` directory, records a publish manifest, and
archives a historical snapshot.

### Completion

The `step_completion` action closes the workflow, transitions the job to
terminal status, and may trigger backend cleanup via the backend sync
protocol.

### Job State Schema

Job state is managed by `job_state.py` (current schema version: 6). Key
state fields include:

- `status` : Current job status (`IN_PROGRESS`,
  `WAITING_FOR_HUMAN_INTERVENTION`, `COMPLETED`, `FAILED`, and others)
- `current_step` : The step currently executing or awaiting approval
- `history` : Ordered record of completed steps with usage data
- `accumulated_artifacts` : Map of artifact keys to file paths
- `review_state` : Current review status and iteration count
- `replan_context` : State for replan recovery
- `failure_history` : Record of past failures for diagnostics

## Coder Integration

### Coder Invocation

The `coder_adapters.py` module handles LLM invocation. It:

1. Resolves the coder command from the coder registry
   (`coder_registry.py`).
2. Builds the invocation payload (prompt, context, instructions).
3. Calls the coder process (subprocess invocation).
4. Collects usage data (tokens, duration, cost).
5. Returns the coder's output directory containing artifacts and
   `meta.json`.

### Coder Roles

The platform uses role-based coder configuration. Roles (e.g.,
`architect_standard`, `reviewer_standard`, `refine_standard`,
`validation_standard`) map to coder configurations resolved by
`coder_registry.py`.

Role resolution uses a dual-path discovery:

1. **Workflow-level registry** : `workflows/<name>/_registry/`
2. **Runtime-level registry** : `~/.ukbe-runner/workflows/default/_registry/`

The runtime registry provides fallback defaults. The workflow registry
allows bundle-specific overrides.

### Role Policies

A role policy (e.g., `architect_standard`, `reviewer_standard`) defines:

- `coder_role_policy` : Maps to a role entry in `coder_roles.json`
- `coder_allowed_roles` : Whitelist of roles allowed for this step
- `coder_must_differ` : Whether consecutive steps must use different coders

The step configuration in `workflow.toml` declares these policies per step
in the `[step.coder]` section.

## Rejection And Retry

### Rejection Model

A step is rejected when the coder returns `REJECTED` status in its
`meta.json` sidecar. The rejection may include:

- `reject_code` : Machine-readable rejection category
- `remark` : Human-readable explanation
- `findings` : Structured list of defects with citations

The runner (`workflow_router.py`) does not perform content analysis on
rejected outputs. The coder owns the rejection decision and the runner
trusts the coder's `REJECTED` status.

### Refine Loop

When a review step reports fixable defects, the router activates the
configured refine step (`on_reject_refine.refine_step`). The refine step
receives the review findings and the original artifact. It attempts to
correct the defects.

The refine loop is bounded:

- `max_iterations` : Maximum refine attempts before escalating
- `on_exhaust_replan` : Replan step activated when max iterations are
  exhausted

### Replan

When the refine loop is exhausted, the router activates a replan. The
replan step receives the accumulated review and refine history. It may:

- Propose an alternative approach to the original step
- Reclassify defects as non-blocking
- Recommend workflow failure if defects are unfixable

The coder decides whether the replan was adequate. The runner does not
perform convergence checks on replan output.

### Failure Routing

When a step cannot succeed after refine and replan attempts, the router
routes to failure. Failure is recorded in `failure_history` in job state.
The job transitions to `FAILED` status. Failure routing is handled by
`failure_runtime.py` and `recovery_runtime.py`.

### Reject Code Routing

Steps may configure `reject_code_routes` in `workflow.toml` to route
specific rejection categories to different recovery paths. For example,
metadata defects may route to a targeted fix step while content defects
route to refine.

## Notification Model

### Notification Integration

The platform supports notifications through `notification_manager.py`:

- **Pushover** : Push notifications to mobile devices (requires Pushover
  API credentials in `.env`)
- **Console** : Text output for local visibility

### Notification Events

Notifications are sent for:

- `STEP_COMPLETED` : Step finished with `APPROVED` status
- `STEP_REJECTED` : Step finished with `REJECTED` status
- `STEP_FAILED` : Step execution failed
- `WAITING_FOR_HUMAN_INTERVENTION` : Step is awaiting human approval
- Workflow start and completion events

### Configuration

Notification settings are configured in `~/.ukbe-runner/config.json` under
the `notification` key:

- `enabled` : Global on/off
- `step_events` : Per-event-type toggles (`completed`, `rejected`,
  `failed`)

Per-step notification control is available through the
`enable_notifications` flag in the step's `workflow.toml` configuration.
