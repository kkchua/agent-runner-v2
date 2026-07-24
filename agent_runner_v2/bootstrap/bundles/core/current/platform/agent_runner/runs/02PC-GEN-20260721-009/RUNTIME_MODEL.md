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
effective_version: "02PC-GEN-20260721-009"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `generate_platform_core_docs`
> This file is workflow-generated and subject to review, validation, audit, and human approval before publication.

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
sidecar file.

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
Contract and Shared Services documents).

Action step types:

- `collect_context` -- Gathers curated reference inputs.
- `validate` -- Runs deterministic rules against artifacts.
- `publish` -- Marks an approved artifact set as active.
- `step_completion` -- Closes the workflow execution.
- `human_approval` -- Obtains explicit operator acceptance before
  activation.

### Execution Contracts

Both step types share the same execution contract in the runner core.
The central entry point is `run_step()` in `step_runner.py` for
prompt-driven steps and `run_action()` for action steps. Both return a
`StepResult` containing:

- `status` -- `"APPROVED"` or `"REJECTED"`
- `remark` -- Human-readable summary
- `artifacts` -- Dict of artifact key to file path
- `reject_code` -- Optional categorized rejection reason
- `meta_json_path` -- Path to the communication sidecar
- `usage_data` -- Token usage and duration metrics

## Execution Paths

### Daemon Mode

In daemon mode, a long-lived worker supervisor (`daemon.py`) polls a
backend server for work. When work is available, the daemon:

1. Claims a step from the backend via `BackendClient.claim_step()`.
2. Spawns a child process running `run_agent.py run`.
3. Monitors child liveness with heartbeat pings and watchdog timers
   (stalled detection, step timeout, kill grace).
4. Collects the child's `result.json` on completion.
5. Synchronizes job state back to the backend via
   `BackendClient.sync_job_state()`.

The daemon handles multiple concurrent children up to a configured
`max_parallel` limit. It supports stop requests mid-execution, worker
registration, and graceful shutdown via SIGINT/SIGTERM.

### Manual Mode

In manual mode, a user invokes the runner directly from the command
line:

```
python -m agent_runner_v2.run_agent run \
  --project-root <path> \
  --template-group <group> \
  --job <step_name>
```

The runner loads the workflow bundle, resolves the step configuration,
invokes the coder (or action), validates results, and writes outcomes
to the local job directory. No backend server is required.

### Shared Execution Core

Both daemon and manual mode share the same `run_step()` / `run_action()`
execution core. The daemon wraps this core with backend polling,
heartbeats, and child process management. Manual mode invokes the core
directly from the CLI. This ensures consistent step behavior across
both paths.

## Job Lifecycle

A job represents one complete workflow execution. Its lifecycle stages:

1. **Init** -- The job directory is created under the jobs root
   (`.ukbe-runner/jobs/<template_group>/<job_id>/`). Initial state is
   written to `job.json`.

2. **Execute** -- Each step runs in sequence. Prompt-driven steps
   invoke a coder subprocess; action steps invoke a registered function.
   Step results are recorded in step subdirectories (e.g.,
   `01_generate/`, `02_review/`). A `result.json` or `meta.json` is
   written per step.

3. **Review/Refine Loops** -- If a review step returns REJECTED, the
   workflow may route to a refine step to fix identified defects, then
   back to review. This loop is constrained by the workflow's
   `[step.on_reject_refine]` configuration.

4. **Validation** -- A validate step runs deterministic checks against
   the produced artifacts.

5. **Audit** -- An audit step performs final semantic verification.

6. **Human Approval** -- A human_approval step requires an operator to
   explicitly accept the output before publication.

7. **Completion** -- The step_completion action closes the workflow.
   The backend is notified, notifications are sent, and the job state
   is finalized.

## Coder Integration

The coder integration is managed by `coder_adapters.py`. Supported
coder backends:

- `codex` -- OpenAI Codex CLI
- `claude` -- Anthropic Claude Code CLI
- `qwen` -- Qwen Code CLI
- `opencode` -- OpenCode CLI
- Plain mode -- Any executable that reads a prompt on stdin

### Invocation Protocol

The `invoke_coder()` function:

1. Loads environment variables from `.env` files (project root, then
   runner home fallback).
2. Resolves API keys from the coder registry (`coder_registry.py`).
3. Builds the appropriate CLI command for the selected coder backend.
4. Launches the coder as a subprocess via `_run_with_sidecar_poll()`.
5. Pipes the prompt text to the subprocess stdin.

### Sidecar-Based Early Exit

The runner polls for a `meta.json` sidecar file during coder execution.
When the sidecar becomes valid (contains valid JSON with `status`,
`artifacts`, and `recorded_at`), the runner terminates the coder
subprocess early and proceeds with result validation. This avoids
waiting for the full coder timeout after work is complete.

### Coder Communication Contract

Every prompt-driven step includes instructions for the coder to write a
`meta.json` sidecar file. The sidecar path is resolved before invocation
and passed to the coder as part of the prompt context.

The meta.json sidecar is the primary communication channel between the
coder and the runner. However, the runner also implements a repair
fallback in `step_runner.py` via `_repair_or_validate_meta_json()`. If
the coder fails to write a valid meta.json sidecar, the runner attempts
to construct one from the coder's direct stdout output (parsed JSON).
This repair handles cases where the coder emits a result object directly
instead of writing the meta.json file.

### Coder Registry

Coder backends are configured in the coder registry (`coder_registry.py`).
Each coder entry specifies:

- Connection type (e.g., `openai`, `anthropic`)
- Model identifier
- Authentication configuration (API key environment variable, base URL)
- CLI flags and invocation parameters

## Rejection And Retry

### Rejection Model

A step may return `REJECTED` with an optional `reject_code`. Common
reject codes include:

- `MISSING_ARTIFACT` -- Required output files are absent.
- `STRUCTURAL_FAILURE` -- Document structure does not match template.
- `SCOPE_DRIFT` -- Content violates layer boundaries.
- `METADATA_NONCOMPLIANCE` -- Frontmatter does not meet the required
  standard.
- `CONTENT_INVALID` -- Factual or semantic errors detected.

### Retry Routing

When a step is rejected, the workflow configuration (`[step.on_reject_refine]`)
determines the routing:

- If a refine step is configured, execution routes to refine with the
  review findings.
- After refinement, execution routes back to review or validation.
- If no refine step is configured or the defect is conceptual (layer
  mismatch, wrong document inventory), the workflow fails.

### Loop Constraints

Review-refine loops are constrained to prevent infinite refinement:

- Loop iteration tracking via `loop_context` state.
- Distinct step directories per iteration (e.g., `03_review/`,
  `04_refine/`, `05_review_iter2/`).
- Maximum refinement count configurable per workflow.

## Notification Model

The notification system is managed by `notification_manager.py`.
Notifications are sent for:

- Workflow lifecycle events (started, completed, failed)
- Step lifecycle events (completed, rejected, failed)
- Human approval requests

### Notification Configuration

Notifications are globally enabled/disabled in the runner config
(`~/.ukbe-runner/config.json`) under the `notification` key.
Step-level events can be selectively enabled by event type.

### Notification Channels

The notification system supports pluggable channels configured in the
runner config. Each channel defines a type (e.g., webhook, email) and
channel-specific parameters. Notifications include enriched context:
workflow name, step name, status, artifacts, and timing data.

### Notification Contract

Notifications are sent by the runner after each step completes, before
human approval gates, and on workflow completion/failure. They are
informational and do not block execution. Failure to send a notification
does not cause step or workflow failure.
