---
template_id: SYS-02-RM
version: "1.0"
doc_type: "platform_standard"
authority: "platform-owned"
scan_policy: "include"
scan_reason: "permanent Layer 2 runtime model; defines execution architecture for this platform"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "02PC-20260720-86359b88"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `publish_platform_core_set`
> This file is workflow-generated and protected from manual edits.

# Runtime Model

## Purpose

This document defines the execution architecture of the agent-runner-v2
platform. It describes the step model, execution paths, job lifecycle,
coder integration, rejection and retry model, and notification model.

All module references below are source code modules within the
`agent_runner_v2` package. They are cited as read-only evidence of the
runtime architecture.

## Step Model

Every workflow on this platform is composed of discrete steps. Each step
is either prompt-driven or action-driven. A step produces one or more
artifacts and declares its routing behavior on success, rejection, or
failure.

### Prompt-Driven Steps

A prompt-driven step renders a prompt template with runtime context,
sends it to a coder (LLM), and reads the result from a `meta.json`
sidecar written by the coder.

Key modules:

- `step_runner.py` -- core step execution contract: invoke coder, read
  meta.json, validate artifacts, enrich sidecar.
- `coder_adapters.py` -- coder invocation abstraction: builds the
  subprocess command, manages timeouts, parses usage data.
- `coder_registry.py` -- resolves coder connections, semantic roles, and
  role policies to concrete coder configurations.

Prompt-driven steps are the primary mechanism for generating documents,
reviews, audits, and other content that requires LLM reasoning.

### Action-Driven Steps

An action-driven step invokes a registered Python function directly
without LLM involvement. Actions are deterministic operations such as
validation, publishing, context collection, or step completion.

Key modules:

- `actions/__init__.py` -- action registry and built-in action exports.
- Individual action modules under `actions/` implement specific
  operations (e.g., `documentation_validation_core.py`,
  `step_completion.py`).

Action steps do not produce a `meta.json` sidecar from a coder. Instead,
the action function returns a result directly to the runner.

### Step Configuration

Each step is declared in the workflow's `workflow.toml` manifest. The
`StepConfig` dataclass (defined in `workflow_packages/base.py`) holds the
validated step configuration including:

- step name
- prompt file or action function
- artifact contract (produces, required inputs, optional inputs)
- coder configuration (role policy, allowed roles, must_differ)
- routing rules (on_approve, on_reject_refine, on_exhaust_replan)
- human approval gating

### Step Types

The platform supports these step types:

| Step Type | Driver | Purpose |
|---|---|---|
| `generate` | Prompt | Create draft artifacts via LLM |
| `review` | Prompt | Evaluate artifacts with pass/reject outcome |
| `refine` | Prompt | Revise artifacts after fixable findings |
| `audit` | Prompt | Final semantic verification before approval |
| `collect_context` | Action | Gather curated reference inputs |
| `validate` | Action | Run deterministic checks against artifacts |
| `publish` | Action | Activate an approved artifact set |
| `human_approval` | Control | Obtain explicit human acceptance |
| `step_completion` | Action | Close the workflow |

## Execution Paths

The platform supports three execution modes. All three modes use the
same underlying step execution pipeline.

### CLI Mode

Entry point: `run_agent.py` invoked via `ukbe-run-agent run`.

The CLI mode executes a workflow directly from a terminal or batch file.
It loads the workflow definition, resolves the step sequence, and
executes each step in order.

Key modules:

- `run_agent.py` -- CLI entry point and argument parsing.
- `step_runner.py` -- step execution contract.
- `workflow_router.py` -- post-step routing decisions.

### Daemon Mode

Entry point: `daemon.py` invoked via `ukbe-run-agent daemon`.

The daemon is a long-running supervisor process that polls a backend API
for workflow claims. For each claimed step, it spawns a fresh subprocess
running the standard `run` command (identical to CLI mode).

Key modules:

- `daemon.py` -- backend polling supervisor: claims work, spawns child
  processes, monitors liveness, writes local logs, emits heartbeats.
- `daemon_runtime.py` -- daemon subprocess execution helpers.
- `backend_client.py` -- backend API communication (claim, complete,
  approve, heartbeat).
- `backend_execution.py` -- backend-coordinated execution logic.

The daemon spawns a fresh subprocess per workflow invocation. Code
changes are picked up automatically without restarting the daemon. Only
changes to `daemon.py` itself require a daemon restart.

### Manual Mode

Entry point: `run_agent.py` invoked via `ukbe-run-agent run --mode manual`.

Manual mode is identical to CLI mode but adds human-in-the-loop approval
gating. Steps flagged with `requires_human_approval_after` pause
execution and wait for explicit human decision before continuing.

Key modules:

- `manual_runtime.py` -- manual approval execution helpers.
- `job_state.py` -- on-disk job state management including approval
  decisions.

## Job Lifecycle

A job represents a single workflow execution. The lifecycle progresses
through these stages:

### 1. Initialization

- The runner loads the workflow definition from the workflow package.
- Runtime context is set (`runtime_context.py`): project root, runner
  root, jobs root, artifact root.
- Job state directory is created under `~/.ukbe-runner/jobs/`.
- Initial job state is written (`job_state.py`).

### 2. Step Execution

- For each step, the runner resolves the step configuration from the
  workflow manifest.
- Context is built: artifact values, path placeholders, governance
  blocks, workflow-specific extensions.
- The step is executed (prompt-driven or action-driven).
- The result is read and validated.
- Post-step routing determines the next step.

### 3. Review and Refine Loops

- If a step produces a rejection result, the router checks for a
  configured refine loop (`on_reject_refine`).
- Refine loops have a maximum iteration count.
- If the iteration limit is exceeded, the workflow may replan or fail.

### 4. Human Approval

- Steps with `requires_human_approval_after: true` pause execution.
- In daemon mode, the backend coordinates approval via API.
- In manual mode, the runner waits for local approval input.

### 5. Publication

- After all steps succeed and approvals pass, the publish action
  activates the approved artifacts.
- The publish manifest is updated.
- Historical snapshots are preserved.

### 6. Completion

- The `step_completion` action closes the workflow.
- Final notifications are sent.
- Job state is marked complete.

## Coder Integration

Coders (LLM agents) are invoked for prompt-driven steps. The platform
abstracts coder interaction through a layered architecture.

### Coder Connections

Coder connections define how to reach a specific LLM backend. They are
stored in `coder_connections.json` within the workflow registry.

Key module: `coder_registry.py` -- `load_coder_connections()`.

### Coder Roles

Each step may declare a coder role (e.g., `architect_standard`,
`reviewer_standard`, `refine_standard`). Roles map to role policies that
control coder selection and behavior.

Key module: `coder_registry.py` -- `load_role_policies()`,
`resolve_effective_coder()`.

### Role Policies

Role policies define constraints on coder selection:

- `coder_default` -- the default coder connection for this role.
- `coder_allowed` -- list of allowed coder connections.
- `coder_must_differ` -- whether consecutive steps must use different
  coders.

### Invocation Contract

The coder invocation follows this contract:

1. The runner renders the prompt template with context.
2. The runner writes the prompt to a temporary file.
3. The runner spawns the coder subprocess (`coder_adapters.py`).
4. The coder processes the prompt and writes results to `meta.json`.
5. The runner polls for `meta.json` appearance.
6. The runner reads and validates the sidecar content.
7. The runner extracts artifact paths and usage data.

The `meta.json` sidecar is the **sole communication channel** between
coder and runner. No stdout JSON parsing, no pre-invocation sidecar
writes, no disk recovery functions.

### Usage Tracking

Each coder invocation records usage data (`coder_adapters.py`):

- input tokens, output tokens, total tokens
- cost (if available)
- duration
- coder identity
- invocation manifest (command, cwd, prompt checksum, timestamps)

## Rejection And Retry

The platform supports structured rejection and retry through refine
loops and replan mechanisms.

### Refine Loop

When a step's result indicates rejection (e.g., a review step returns
`REJECTED`), the workflow router (`workflow_router.py`) checks for a
configured `on_reject_refine` rule.

The refine loop:

1. Routes execution back to a designated refine step.
2. The refine step receives the rejection feedback as context.
3. The refine step produces revised artifacts.
4. The revised artifacts are re-reviewed or re-validated.
5. The loop continues until acceptance or iteration exhaustion.

### Iteration Limits

Each refine loop has a `max_iterations` count. When the limit is
exceeded:

- If `on_exhaust_replan` is configured, the workflow routes to a replan
  step.
- If no replan is configured, the workflow fails with a budget-exceeded
  error.

Key module: `recovery_runtime.py` -- `activate_refine_loop()`,
`activate_replan()`, `handle_recovery_budget_exceeded()`.

### Failure Routing

When a step fails (as opposed to being rejected), the router invokes
`route_after_failure()` in `workflow_router.py`. Failure routing:

- Records the failure in job state.
- Sends failure notifications if configured.
- Marks the job as failed unless recovery is possible.

### Rejection Codes

Rejection results carry structured codes that determine routing:

- Fixable defects route to refine.
- Conceptual defects (layer violation, wrong scope) route to fail.
- The coder defines rejection semantics in its `meta.json` response.

## Notification Model

The platform provides a centralized notification system for workflow
events.

Key module: `notification_manager.py` -- unified notification interface.

### Notification Triggers

Notifications may be sent on:

- step completion
- step rejection
- step failure
- human approval required
- workflow completion

### Configuration

Notifications are configured in `~/.ukbe-runner/config.json` under the
`notification` key. Settings include:

- enabled/disabled flag
- provider configuration (e.g., Pushover tokens)
- per-event enablement (completed, rejected, failed)

### Delivery

The notification manager enriches notification context with workflow
identity, step name, job ID, and result summary before dispatching
through the configured provider.

Key module: `notifications.py` -- low-level notification dispatch.
