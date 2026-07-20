---
template_id: SYS-02-SS
version: "1.0"
doc_type: "platform_standard"
authority: "platform-owned"
scan_policy: "include"
scan_reason: "permanent Layer 2 shared services contract; defines runtime services available to Layer 3 bundles"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "02PC-20260720-fd35ddf1"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `publish_platform_core_set`
> This file is workflow-generated and protected from manual edits.

# Shared Services

## Overview

This document defines the runtime services available to Layer 3 workflow
bundles on the agent-runner-v2 platform. These services are provided by
the platform runtime and are consumed by bundles through documented APIs
and conventions.

Layer 3 bundles use these services to:

- Inject workflow-specific context into prompt templates
- Resolve artifact paths across repo and runtime namespaces
- Define workflow-owned output path contracts
- Write and read meta.json sidecar files
- Send notifications
- Synchronize with the backend in daemon mode
- Register custom actions

## Context Extensions

### `build_context_extensions()`

Every workflow bundle may define a `context_extensions.py` module with a
`build_context_extensions()` function. This function is called by the
runner during prompt rendering to inject workflow-specific context
variables into the prompt template.

**Signature:**

```python
def build_context_extensions(
    context: dict,
    state: dict,
    step_config: StepConfig,
) -> dict:
    """Return additional context key-value pairs for prompt rendering."""
```

**Parameters:**

- `context` : The current context dictionary (artifact paths, governance
  rules, job metadata).
- `state` : The current job state (current step, accumulated artifacts,
  backend coordination data).
- `step_config` : The `StepConfig` dataclass for the current step.

**Returns:** A dictionary of additional context key-value pairs to merge
into the prompt rendering context.

**Example:**

```python
def build_context_extensions(context, state, step_config):
    return {
        "MY_CUSTOM_PATH": str(Path("docs/output/custom.md").resolve()),
        "WORKFLOW_NAME": state.get("template_group", "unknown"),
    }
```

The runner in `step_runner.py` calls `build_context_extensions()` (if the
module exists) after building the base context but before rendering the
prompt template. The returned keys are merged into the context, making
them available as `{KEY_NAME}` placeholders in prompt templates.

### Context Injection Rules

- Context extensions must not override platform-level context keys.
- Path values must use absolute paths.
- Extensions are workflow-specific and must not inject bundle-local logic
  into the platform context.

## Artifact Resolution

### `resolve_repo_or_runtime_path()`

The platform provides a path resolution function
(`runtime_context.py`) that resolves paths using the repo/runtime
namespace convention.

**Signature:**

```python
def resolve_repo_or_runtime_path(
    path_str: str,
    *,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
) -> Path:
```

**Convention:**

- `docs/...` and other repo-owned content resolve under the project root.
- Runtime job paths resolve under the runner jobs root.
- Absolute paths are returned unchanged.

**Usage context:**

This function is used internally by the runner during prompt rendering.
Bundle authors typically do not call it directly. Instead, they reference
paths through artifact key placeholders (`{ARTIFACT_KEY_NAME}`) which the
runner resolves automatically.

### `known_artifact_paths()`

The platform provides a centralized artifact path mapping
(`constants.py`) that converts artifact keys to concrete file paths. All
prompt template placeholders are resolved through this function.

```python
from agent_runner_v2.constants import known_artifact_paths

paths = known_artifact_paths(job_id="02PC-20260720-fd35ddf1")
# Returns dict mapping artifact keys to absolute paths
```

## Path Contracts

### `build_output_paths()`

Workflow bundles may define a `output_paths.py` module with a
`build_output_paths()` function. This function returns a dictionary
mapping artifact keys to concrete output paths, allowing the bundle to
define custom artifact locations beyond the platform defaults.

**Signature:**

```python
def build_output_paths(
    *,
    job_id: str,
    project_root: Path,
) -> dict:
    """Return a dict of artifact_key -> output_path."""
```

**Example:**

```python
def build_output_paths(*, job_id, project_root):
    run_dir = project_root / "docs" / "runs" / job_id
    return {
        "MY_OUTPUT": str(run_dir / "my_output.md"),
        "MY_REVIEW": str(run_dir / "my_review.md"),
    }
```

The runner merges bundle-defined output paths with platform defaults.
Bundle paths take precedence for keys the bundle owns.

### Workflow Path Contracts

The module `workflow_path_contracts.py` defines platform-level path
contracts for known workflows. Bundle-specific path contracts should go in
the bundle's own `output_paths.py`.

## Meta Sidecar

### meta.json Contract

The `meta.json` sidecar is the sole communication channel between the
coder and the runner. Every step execution : prompt-driven or
action-driven : must produce a `meta.json` file.

**Required structure:**

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED",
    "remark": "Brief summary of what was accomplished",
    "artifacts": {
      "ARTIFACT_KEY": "absolute/path/to/artifact.md"
    },
    "recorded_at": "2026-07-20T12:00:00+08:00"
  }
}
```

**Fields:**

| Field | Required | Description |
|---|---|---|
| `schema_version` | Yes | Must be `"v2"`. |
| `coder_result.status` | Yes | `"APPROVED"` or `"REJECTED"`. |
| `coder_result.remark` | Yes | Human-readable summary. |
| `coder_result.artifacts` | Yes | Map of artifact keys to absolute paths. |
| `coder_result.recorded_at` | Yes | ISO-8601 timestamp. |

**Status semantics:**

- `APPROVED` : The coder considers the step successful. Required artifacts
  exist on disk.
- `REJECTED` : The coder cannot complete the step. May include findings
  for the refine step.

**Additional optional fields:**

- `coder_result.findings` : Structured defect list (for `REJECTED` status)
- `coder_result.reject_code` : Machine-readable rejection category
- `coder_result.usage` : Token and cost data

### meta.json Handling

The runner (`step_runner.py`) reads the `meta.json` sidecar after coder
invocation. It:

1. Validates the JSON structure.
2. Verifies that declared artifacts exist on disk.
3. Enriches the sidecar with execution metadata (timing, usage).
4. Passes the enriched result to the router (`workflow_router.py`) for
   next-step determination.

The runner never writes to the coder's output files. The sidecar is the
only data exchange path.

### Sidecar Injection

The runner automatically appends sidecar template instructions to prompt
templates before sending them to the coder. These instructions tell the
coder the required `meta.json` format and the artifact paths it must
produce. Bundle authors do not need to include sidecar instructions in
their prompt templates.

## Notification Integration

### Sending Notifications

The platform provides notification services through
`notification_manager.py`. Workflow bundles use this service for
step-level and workflow-level notifications.

**Available functions:**

- `send_step_notification(status, context)` : Send a step event
  notification.
- `send_workflow_notification(status, context)` : Send a workflow event
  notification.
- `should_send_notifications()` : Check if notifications are globally
  enabled.

**Usage context:**

Notifications are typically triggered by the runner automatically after
step execution and routing. Bundle authors configure notification behavior
through the `enable_notifications` flag in `workflow.toml` and the global
notification settings in `~/.ukbe-runner/config.json`.

### Notification Configuration

Notification settings in `~/.ukbe-runner/config.json`:

```json
{
  "notification": {
    "enabled": true,
    "step_events": {
      "completed": true,
      "rejected": true,
      "failed": true
    }
  }
}
```

Pushover credentials are configured in `.env` (project root) with the
keys `PUSHOVER_USER_KEY` and `PUSHOVER_API_TOKEN`.

## Backend Sync Protocol

### Daemon-to-Backend Communication

In daemon mode, the runner communicates with a backend service
(`backend_client.py`) for:

- **Claiming work** : The daemon polls `GET /api/worker/claim` to claim
  pending workflow steps.
- **Heartbeats** : The daemon sends child-scoped heartbeats keyed by
  `workflow_step_run_id` to `POST /api/worker/heartbeat`.
- **Step completion** : After step execution, the runner reports results
  and usage data to the backend.
- **Job sync** : The runner pushes workflow definitions and bundle
  metadata to the backend for discovery and scheduling.

### Backend Execution Model

The module `backend_execution.py` handles the backend-specific execution
model:

- `BackendClient` : HTTP client for backend API communication.
- `daemon_runtime.py` : Runtime coordination for daemon mode.

### Sync Protocol

The workflow sync protocol (`sync_workflows.py`) pushes workflow bundle
definitions to the backend. This enables the backend to:

- Discover available workflows
- Validate workflow configurations
- Schedule workflow runs
- Coordinate worker assignments

Bundle authors do not need to implement sync logic. The platform handles
sync through `ukbe-run-agent sync` or the operator console.

## Action Registration

### `@action()` Decorator

Custom actions are registered using the `@action()` decorator. Actions are
Python functions that perform deterministic operations.

**Registration pattern:**

```python
# In actions.py of the workflow bundle

from agent_runner_v2.actions import action

@action(name="my_custom_action")
def my_custom_action(
    *,
    state: dict,
    step_cfg: dict,
    job_dir: Path,
    context: dict,
) -> dict:
    """Perform a custom action and return a meta.json-compatible result."""
    # Action logic here
    return {
        "status": "APPROVED",
        "remark": "Action completed successfully",
        "artifacts": {},
    }
```

### Action Result Contract

An action must return a dictionary compatible with the `meta.json` format:

| Field | Required | Description |
|---|---|---|
| `status` | Yes | `"APPROVED"` or `"REJECTED"`. |
| `remark` | Yes | Human-readable summary. |
| `artifacts` | Yes | Map of artifact keys to absolute paths (may be empty). |

### Action Execution Context

The action receives:

- `state` : Current job state dictionary.
- `step_cfg` : Current step configuration from `workflow.toml`.
- `job_dir` : Job state directory path.
- `context` : Current context dictionary (paths, governance rules, etc.).

### Platform-Level Actions

The platform provides 30+ built-in actions in `agent_runner_v2/actions/`:

- `validate` : Deterministic validation against rules
- `publish` : Activate approved artifacts
- `copy` : Copy files between locations
- `scan` : Scan documents for patterns
- `assemble` : Combine multiple artifacts
- `collect_context` : Gather curated reference inputs
- `step_completion` : Close the workflow

Bundle authors may use these platform actions by referencing their
registered names in the `action` field of a `[[step]]` in
`workflow.toml`.

### Action Discovery

Actions are discovered through the workflow package loader
(`workflow_packages/loader.py`). The loader imports the bundle's
`actions.py` module (if present) and registers any `@action()`-decorated
functions. Platform-level actions in `agent_runner_v2/actions/` are always
available.
