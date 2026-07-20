---
template_id: SYS-02-RM
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 runtime model; defines the execution architecture for agent-runner-v2"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-001"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `generate_platform_core_docs`
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
   governance rules, workflow state).
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

- `agent_runner_v2/actions/` - platform-level action modules (30+ actions:
  copy, validate, scan, publish, assemble, etc.)
- The workflow bundle's `actions.py` - bundle-specific custom actions

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
runner does not enforce step type semantics - it executes the step as
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

The daemon (`daemon.py`) is a long-running supervisor that:

1. Polls a backend for work claims at a configurable interval.
2. On claim, spawns a fresh subprocess: `python -m agent_runner_v2.run_agent run ...`
   - identical to the CLI invocation.
3. Monitors the child process lifecycle.
4. Reports results back to the backend.

The daemon spawns a fresh subprocess for each workflow invocation. Code
changes are picked up automatically without restarting the daemon itself.
Only changes to `daemon.py` require a daemon restart.

The daemon delegates execution to the same `run_agent.py` path used by CLI
mode. There is no separate daemon execution pipeline.

### Manual Mode

**Entry point:** `ukbe-run-agent run --mode manual`

Manual mode supports human-in-the-loop workflows. After each step that
has `requires_human_approval_after: true`, the runner pauses and waits for
an explicit approval or rejection through:

- The operator console (`ukbe-run-agent console`)
- The approve-step batch file
- The backend API (when connected)

Approval routes to the `on_approve` next step. Rejection routes through
the `on_reject_refine` refinement loop if configured.

## Job Lifecycle

### Job State

Job state is managed on disk by `job_state.py`. Each job has a unique job
ID and a state directory under `~/.ukbe-runner/jobs/<workflow_name>/<job_id>/`.

State includes:

- Current step name and index
- Template group (workflow name)
- Step execution history
- Accumulated artifacts
- Backend coordination data (when running in daemon mode)

### Lifecycle Phases

1. **Init**: The workflow's init step is determined from the `workflow.toml`
   `[workflow]` section. Job state is created.

2. **Execute**: Each step is executed in sequence. Prompt-driven steps
   invoke a coder; action-driven steps call a Python function.

3. **Route**: After execution, `workflow_router.py` determines the next
   step based on:
   - The coder's reported status (`APPROVED` or `REJECTED`)
   - The step's `on_approve` routing
   - Any `on_reject_refine` refinement loop configuration
   - Any `on_exhaust_replan` replan configuration
   - Backend-provided routing (when in daemon mode)

4. **Review/Refine Loop**: If review rejects with fixable defects, the
   workflow routes to the refine step, then back to review. This loop
   continues until the step passes or the refinement budget is exhausted.

5. **Approve**: When all gates pass and human approval is obtained (if
   required), the workflow proceeds to publish.

6. **Publish**: The publish action marks the approved set as active,
   updates frontmatter and the publish manifest, and supersedes any prior
   active version.

7. **Complete**: The `step_completion` action closes the workflow and
   records final state.

## Coder Integration

### Coder Adapters

`coder_adapters.py` provides the LLM invocation abstraction. It:

- Manages coder connections (local CLI tools, API endpoints)
- Renders prompts with context variables
- Invokes the coder as a subprocess
- Captures the invocation result (return code, stdout, stderr)
- Records usage data (tokens, cost, duration)

The adapter does not parse the coder's stdout for results. The coder
communicates exclusively through the `meta.json` sidecar.

### Coder Registry

`coder_registry.py` resolves coder roles to connection configurations:

- `coder_connections.json` - maps connection names to API endpoints,
  models, and authentication
- `coder_roles.json` - maps semantic role names (e.g., `architect`,
  `reviewer`, `refine`, `validator`) to coder connections
- `role_policies.json` - defines role policies that group roles into
  policies (e.g., `architect_standard`, `reviewer_standard`,
  `refine_standard`, `validation_standard`)

Role policies are resolved through a dual-path discovery: the workflow
bundle's `_registry/` directory first, then the global runner home
`~/.ukbe-runner/workflows/default/_registry/`.

### Role Policies

A role policy maps to a set of allowed coder roles. The policy is declared
per step in `workflow.toml`:

```toml
[step.coder]
role_policy = "architect_standard"
must_differ = false
allowed_roles = ["architect", "architect_alt"]
```

`must_differ: true` ensures the coder assigned to this step differs from
the coder used in the previous step, preventing self-review.

## Rejection And Retry

### Rejection Model

A step is rejected when the coder's `meta.json` reports
`status: "REJECTED"`. The router (`workflow_router.py`) handles rejection
based on step configuration.

### Refinement Loop

The `[step.on_reject_refine]` configuration defines the refinement loop:

```toml
[step.on_reject_refine]
refine_step = "refine_docs"
artifact = "REVIEW_FILE_SUGGESTED"
max_iterations = 3
exhausted = { failure_code = "REFINE_EXHAUSTED" }
```

When a step is rejected:

1. The refine step runs, receiving the review artifact.
2. The refined artifact is routed back to the original step.
3. This loop repeats until the step passes or `max_iterations` is reached.
4. On exhaustion, the workflow fails with the configured failure code.

### Replan

The `[step.on_exhaust_replan]` configuration provides an alternative path
when refinement is exhausted:

```toml
[step.on_exhaust_replan]
replan_step = "replan_docs"
replan_artifact = "REVIEW_FILE_SUGGESTED"
```

This routes to a different step that may take a fundamentally different
approach rather than continuing to refine.

### Reject Code Routing

`reject_code_routes` maps specific rejection codes to custom routing:

```toml
[step.reject_code_routes]
LAYER1_REDEFINITION = { route = "fail" }
METADATA_NONCOMPLIANCE = { route = "refine" }
```

This allows the workflow to distinguish between fixable defects (route to
refine) and conceptual failures (route to fail).

## Notification Model

### Notification Manager

`notification_manager.py` provides centralized notification management
for all execution modes. It supports:

- **Pushover notifications** - for daemon/worker mode alerts
- **Console notifications** - for CLI and manual mode

### Notification Configuration

Notifications are configured in `~/.ukbe-runner/config.json`:

```json
{
  "notification": {
    "enabled": true,
    "pushover_user_key": "...",
    "pushover_api_token": "..."
  }
}
```

### Step-Level Notification Control

Each step can enable or disable notifications via
`enable_notifications` in `workflow.toml`:

```toml
[[step]]
name = "generate_docs"
enable_notifications = true
```

When enabled, notifications are sent on step start, step completion
(success or failure), and when human approval is required.

### Notification Events

The notification manager emits events for:

- **Step started**: When a step begins execution
- **Step completed**: When a step finishes (with status)
- **Human approval required**: When a step pauses for human decision
- **Workflow completed**: When the workflow finishes
- **Workflow failed**: When the workflow terminates with an error
