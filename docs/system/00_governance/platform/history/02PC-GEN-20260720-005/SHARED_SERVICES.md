---
template_id: SYS-02-SS
version: "1.0"
doc_type: "platform_standard"
authority: "platform-owned"
scan_policy: "include"
scan_reason: "permanent Layer 2 shared services contract; defines runtime services for Layer 3 bundles"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "published"
effective_version: "02PC-GEN-20260720-005"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `publish_platform_core_set`
> This file is workflow-generated and protected from manual edits.

# Shared Services

## Purpose

This document defines the runtime services available to Layer 3 workflow
bundles on agent-runner-v2. These services are provided by the platform
runtime and consumed by bundles during execution. Bundles must use these
services through their documented interfaces rather than reimplementing
equivalent logic.

## Context Extensions

Workflow bundles can inject custom data into the prompt rendering context
through the context extension pattern.

### Pattern

A bundle provides a `context_extensions.py` module at the bundle root.
This module exposes a `build_context_extensions()` function that returns
a dictionary of additional key-value pairs to merge into the prompt
rendering context.

### Loading

The `WorkflowBundle` dataclass in `workflow_packages/base.py` carries an
optional `context_extensions_path` field pointing to the module. The
runner loads this module via `importlib` at execution time and calls
`build_context_extensions()` to obtain the extension dictionary.

### Contract

The `build_context_extensions()` function receives the current runtime
context (project root, job state, workflow configuration) and returns a
flat dictionary of string keys to string values. These values are merged
into the template rendering context before prompt rendering occurs.

### Rules

- Context extension keys must not collide with platform-reserved keys
  (artifact keys, runtime context keys).
- Context extension values must be strings or values that serialize
  cleanly to strings for template rendering.
- Context extensions are read-only during prompt rendering; they must
  not mutate job state.
- Workflow-specific paths (e.g., custom output directories) belong in
  context extensions, not in core runner code.

## Artifact Resolution

The platform provides a centralized artifact path resolution system
through `runtime_context.py` and `constants.py`.

### `resolve_repo_or_runtime_path()`

This function in `runtime_context.py` resolves an artifact path by
checking multiple resolution strategies:

1. Check if the artifact exists in the current job state.
2. Check if the artifact exists at the known canonical path from
   `known_artifact_paths()` in `constants.py`.
3. Return the resolved absolute path or raise an error if the artifact
   cannot be found.

### Path Resolution Rules

- All artifact paths are resolved to absolute paths before injection
  into prompt context.
- Path placeholders in prompt templates (e.g., `{CODEBASE_DOC_ROOT}`)
  must use absolute paths.
- The `artifact_path()` function in `constants.py` constructs paths from
  artifact keys and folder keys without hardcoded strings.
- The `known_artifact_paths()` function returns the complete mapping of
  artifact keys to their canonical relative paths.

### Runtime Context

The `runtime_context.py` module provides process-local context including:

- `PROJECT_ROOT`: the workspace root directory.
- `RUNNER_ROOT`: the runner package root directory.
- `JOBS_ROOT`: the job state directory root.
- `ARTIFACT_ROOT`: the artifact output root.
- `GLOBAL_RUNNER_HOME`: the global runner home (`~/.ukbe-runner/`).
- `PACKAGE_ROOT`: the `agent_runner_v2` package directory.

These are resolved at import time from the runtime environment. The
`set_context()` function allows overriding context in tests.

## Path Contracts

Workflow bundles can declare their own output path contracts through the
`output_paths.py` module.

### Pattern

A bundle provides an `output_paths.py` module at the bundle root. This
module exposes a `build_output_paths()` function that returns a
dictionary mapping artifact keys to their output path patterns.

### Platform Path Contracts

The platform defines workflow-owned output path contracts in
`workflow_path_contracts.py`. This module maps workflow names to their
expected output path structures. For example, bootstrap workflows use
`resolve_workflow_output_paths()` to determine where generated documents
should be placed.

### Rules

- Output paths must be declared in the bundle's `output_paths.py` or in
  the platform's `workflow_path_contracts.py`.
- Path contracts must use relative paths from the project root.
- Path contracts must not hardcode absolute paths.
- The platform's `constants.py` is the single source of truth for
  folder keys and path construction patterns.

## Meta Sidecar

The `meta.json` sidecar is the sole communication channel between coder
and runner for prompt-driven steps.

### Sidecar Contract

After a prompt-driven step completes, the coder writes a `meta.json`
file adjacent to the output artifact. The sidecar contains:

- `schema_version`: the sidecar schema version (currently `"v2"`).
- `coder_result`: the result object with status, remark, artifacts, and
  usage data.

### Runner Behavior

The `step_runner.py` module:

1. Polls for the sidecar file after the coder subprocess exits.
2. Reads and validates the sidecar JSON structure.
3. Enriches the sidecar with invocation manifest data (command,
   checksums, timestamps).
4. Uses the sidecar content to determine step success or failure.

### Rules

- The runner does not write the sidecar before invocation.
- The runner does not parse stdout for JSON results.
- The runner does not attempt disk recovery of missing sidecars.
- If the sidecar is missing or invalid, the step fails with
  `MetaJsonMissingError` or `MetaJsonInvalidError`.

## Notification Integration

The platform provides centralized notification management through
`notification_manager.py`.

### Service Interface

The notification manager exposes:

- `should_send_notifications()`: checks if notifications are globally
  enabled in the runner configuration.
- `send_notification()`: sends a notification with enriched context
  (workflow name, step name, job ID, status).

### Configuration

Notifications are configured in `~/.ukbe-runner/config.json` under the
`notification` key:

- `enabled`: global on/off switch.
- `step_events`: per-event-type filtering (completed, rejected, failed).
- Provider-specific settings (e.g., Pushover token, user key).

### Integration Pattern

Steps opt into notifications via the `enable_notifications` flag in
their `workflow.toml` configuration. When enabled, the runner sends
notifications at step completion, rejection, or failure. The
notification manager handles context enrichment and provider dispatch.

## Backend Sync Protocol

For daemon mode execution, the platform communicates with a backend API
through `backend_client.py`.

### BackendClient

The `BackendClient` dataclass provides the API interface:

- `submit_run()`: submits a new workflow run to the backend.
- `claim_step()`: claims a pending step for execution (used by daemon).
- `report_result()`: reports step completion and artifact paths.
- `send_heartbeat()`: emits liveness heartbeats for active runs.
- `approve_step()`: records human approval decisions.
- `stop_run()`: cancels an active run.

### Sync Protocol

The daemon sync protocol follows this sequence:

1. **Poll**: The daemon polls the backend for pending claims.
2. **Claim**: The daemon claims a step and receives the execution
   specification.
3. **Execute**: The daemon spawns a child subprocess to execute the step.
4. **Report**: The child process reports results back to the backend
   via `report_result()`.
5. **Heartbeat**: The daemon sends periodic heartbeats during execution.

### Execution Request

The `ExecutionRequest` dataclass in `execution_request.py` carries the
full execution context from backend to child process: workflow name,
step name, job ID, workspace root, project root, and step execution
spec. The `ExecutionResult` dataclass in `execution_result.py` carries
the completion result back.

## Action Registration

The platform provides a decorator-based action registration system for
bundle-local custom actions.

### `@action()` Decorator

The `@action()` decorator in `workflow_packages/actions/__init__.py`
registers a Python function as a named runner action:

```python
from agent_runner_v2.workflow_packages.actions import action

@action("my_custom_action")
def my_custom_action(*, context, state, step_cfg, project_root):
    return ActionResult(status="APPROVED", remark="Done", artifacts={...})
```

### Registration Flow

1. When a workflow bundle is loaded, its `actions.py` module is imported.
2. Any functions decorated with `@action()` are registered in the
   `REGISTERED_ACTIONS` global dictionary.
3. When the runner encounters an action-driven step, it checks
   `REGISTERED_ACTIONS` first, then falls back to the global
   `ACTION_REGISTRY` in `actions/__init__.py`.

### Action Function Signature

Every action function must accept these keyword arguments:

- `context`: the current rendering context dictionary.
- `state`: the current job state dictionary.
- `step_cfg`: the `StepConfig` for the current step.
- `project_root`: the absolute path to the project root.

### Return Type

Action functions must return an `ActionResult` dataclass (from
`action_result.py`):

- `status`: `"APPROVED"` or `"REJECTED"`.
- `remark`: human-readable summary.
- `artifacts`: dictionary mapping artifact keys to file paths.
- `reject_code`: optional code for routing rejection handling.

### Global Actions

The platform provides a set of built-in actions in the `actions/`
directory (e.g., `step_completion`, `validate_system_docs`,
`finalize_bootstrap`). These are registered in the global action
registry and available to all bundles. Bundle-local actions take
precedence over global actions when names collide.
