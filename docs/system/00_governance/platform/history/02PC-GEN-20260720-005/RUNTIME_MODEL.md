---
template_id: SYS-02-RM
version: "1.0"
doc_type: "platform_standard"
authority: "platform-owned"
scan_policy: "include"
scan_reason: "permanent Layer 2 runtime model; defines the platform execution architecture"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "02PC-GEN-20260720-005"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `publish_platform_core_set`
> This file is workflow-generated and protected from manual edits.

# Runtime Model

## Purpose

This document defines the execution architecture of agent-runner-v2.
It describes the step model, execution paths, job lifecycle, coder
integration, and rejection and retry model that Layer 3 workflow bundles
operate within.

This document references source code modules as factual evidence of the
runtime architecture. Module names are cited to ground platform
statements in verifiable implementation.

## Step Model

Every workflow execution is organized as a sequence of steps. Each step
is defined in a `workflow.toml` manifest and loaded as a `StepConfig`
dataclass by the workflow package loader (`workflow_packages/loader.py`).

### Step Types

The platform supports two fundamental step types:

**Prompt-driven steps** invoke an LLM coder agent with a rendered prompt
template. The coder produces artifact files and a `meta.json` sidecar as
the sole communication channel. The runner reads the sidecar to determine
success or failure.

**Action-driven steps** invoke a Python function registered in the
platform's action system. The function receives context, state, step
configuration, and project root, and returns an `ActionResult` dataclass
(defined in `action_result.py`) with status, remark, artifacts, and
optional reject code.

### Step Configuration

Each step carries the following configuration (from `StepConfig` in
`workflow_packages/base.py`):

- **name**: unique step identifier within the workflow
- **prompt_file** or **action**: exactly one of these is set
- **produces**: artifact keys this step generates
- **required_inputs** and **optional_inputs**: artifact keys consumed
- **coder_role_policy**: which coder role policy applies
- **on_approve**: routing target on success
- **on_reject_refine**: refinement loop configuration
- **on_exhaust_replan**: replan configuration when refinement is exhausted
- **requires_human_approval_after**: whether a human gate follows this step
- **enable_notifications**: whether push notifications fire

### Step Execution Contract

The core execution contract is implemented in `step_runner.py`:

1. Render the prompt template with context (for prompt-driven steps), or
   dispatch to the registered action function (for action-driven steps).
2. For prompt-driven steps: invoke the coder subprocess, wait for
   completion, and read the `meta.json` sidecar.
3. Validate that declared output artifacts exist on disk.
4. Enrich the sidecar with usage data and invocation metadata.
5. Return the result to the caller for routing.

The `meta.json` sidecar is the sole communication channel between coder
and runner for prompt-driven steps. There is no stdout JSON parsing, no
pre-invocation sidecar writing, and no disk recovery fallback.

## Execution Paths

The platform supports three execution modes, each entering the same
step execution core through different paths.

### CLI Mode

Entry point: `run_agent.py` invoked with `run --template-group <name>`.

The CLI mode executes a workflow directly from a terminal or batch file.
It loads the workflow configuration, resolves the step sequence, and
executes each step sequentially. Batch files (`run-*.bat`) activate the
virtual environment and invoke `ukbe-run-agent`.

### Daemon Mode

Entry point: `daemon.py` invoked with `daemon [worker-id]`.

The daemon is a supervisor process that polls a backend API for claimed
workflow steps. For each claimed step, it spawns a fresh child subprocess
running the standard `run_agent.py run` command. This architecture means:

- Code changes are picked up automatically without restarting the daemon.
- Only changes to `daemon.py` itself require a daemon restart.
- Each child process has its own isolated execution context.
- The daemon monitors child liveness and emits heartbeats to the backend.

The daemon reads configuration from `~/.ukbe-runner/config.json` and
supports engine version pinning, backend step spec sources (global,
backend, hybrid), and configurable polling intervals.

### Manual Mode

Entry point: `run_agent.py` invoked with `run --mode manual`.

Manual mode provides human-in-the-loop execution with approval gating.
Steps with `requires_human_approval_after: true` pause execution until
an explicit approval decision is recorded.

### Execution Core

All three modes converge on the same step execution core:

- `step_runner.py` handles the invoke-validate-sidecar contract.
- `backend_execution.py` handles execution request deserialization and
   context setup for daemon-spawned subprocesses.
- `execution_core.py` provides the shared `execute_routed_step` and
  `invoke_prepared_step` functions.

## Job Lifecycle

A workflow job progresses through the following lifecycle stages:

1. **Submission**: A workflow run is submitted via CLI or backend API.
   The backend assigns a job ID and workflow name.

2. **Initialization**: The runner loads the workflow bundle, resolves
   the step sequence, and sets up the job state directory under
   `~/.ukbe-runner/jobs/<workflow_name>/<job_id>/`.

3. **Step execution**: Each step is executed in sequence. The runner
   resolves artifact paths, renders prompts or dispatches actions, and
   records results in job state.

4. **Routing**: After each step, the router determines the next step
   based on the step result:
   - Success routes to `on_approve` target or the next sequential step.
   - Rejection routes to `on_reject_refine` refinement loop.
   - Refinement exhaustion routes to `on_exhaust_replan`.
   - Failure routes through `route_after_failure()`.

5. **Human approval** (optional): Steps with human gating pause until
   an approval decision is recorded via the approval mechanism.

6. **Completion**: The workflow reaches its final step or a terminal
   failure state. Notifications are sent if enabled.

7. **Backend sync**: For daemon mode, the runner syncs job state and
   artifact paths back to the backend API via `backend_client.py`.

### Job State

Job state is managed on disk by `job_state.py`. Each job has a directory
containing step results, artifact paths, and loop context. The state
persists across step boundaries and supports resumption.

## Coder Integration

Prompt-driven steps invoke LLM coder agents through the abstraction
layer in `coder_adapters.py`.

### Coder Invocation

The `invoke_coder()` function in `coder_adapters.py`:

1. Resolves the coder connection (CLI command, API endpoint, or other
   backend) from the coder registry.
2. Writes the rendered prompt to a temporary file.
3. Spawns the coder subprocess with the prompt as input.
4. Polls for the `meta.json` sidecar with configurable timeout and
   settle delay.
5. Returns an `InvocationResult` with return code, parsed result,
   usage data, and invocation manifest.

### Coder Roles and Policies

The `coder_registry.py` module resolves coder configurations based on
role policies. It loads three registry files:

- `coder_connections.json`: defines available coder backends and their
  connection parameters.
- `role_policies.json`: defines named policies (e.g.,
  `architect_standard`, `reviewer_standard`, `refine_standard`,
  `validation_standard`) that map to coder configurations.
- `coder_roles.json`: maps role names to their resolved configurations.

Registry files can be provided at the bundle level (under
`_registry/` within the bundle directory) or at the runtime level
(under `~/.ukbe-runner/_registry/`). Bundle-level registries take
precedence over runtime-level registries.

### Usage Tracking

Each coder invocation records usage data via the `UsageData` dataclass
in `coder_adapters.py`: input tokens, output tokens, total tokens, cost,
duration, and timestamps. This data is written to the meta.json sidecar
and synced to the backend.

## Rejection And Retry

The platform provides a structured rejection and retry model for
prompt-driven steps.

### Refinement Loop

When a step is configured with `on_reject_refine`, a rejection triggers
a refinement cycle:

1. The reject step receives the rejection feedback as context.
2. The coder re-generates the artifact with the feedback incorporated.
3. The runner validates the revised artifact.
4. If the revision passes, execution continues to the next step.
5. If the revision is rejected again, the loop repeats.

The `default_max_rejects` field on `WorkflowBundle` (default: 3) limits
the number of refinement iterations. When the limit is reached, the
`on_exhaust_replan` configuration determines the next action.

### Replan

When refinement is exhausted, the `on_exhaust_replan` configuration
directs execution to a replan step. The replan step receives the full
rejection history and generates a revised approach. This may route back
to the original step or to an alternative step.

### Reject Codes

Action-driven steps return an `ActionResult` with an optional
`reject_code` field. The step configuration may define
`reject_code_routes` to map specific reject codes to different routing
targets, enabling fine-grained failure handling.

### Notification Model

The `notification_manager.py` module provides centralized notification
management across all execution modes. It supports:

- Step-level events: completion, rejection, failure.
- Configurable event filtering via `~/.ukbe-runner/config.json`.
- Context enrichment with workflow name, step name, job ID, and status.
- Integration with external notification providers (e.g., Pushover).

Notifications are opt-in per step via the `enable_notifications` flag
in the step configuration. The global notification enable/disable is
controlled in the runner configuration.
