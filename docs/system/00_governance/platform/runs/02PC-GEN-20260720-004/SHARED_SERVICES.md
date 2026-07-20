---
template_id: SYS-02-SS
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 shared services contract; defines runtime services for Layer 3 bundles"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-004"
managed_by: workflow-generated
---

# Shared Services

## Purpose

This document defines the runtime services available to Layer 3 workflow
bundles running on agent-runner-v2. These services are provided by the
platform and consumed by bundles. Bundle authors depend on these
contracts but do not implement them.

All service references point to source code modules in the
`agent_runner_v2/` package.

## Context Extensions

### Pattern

Context extensions allow workflow bundles to inject custom variables
into the prompt rendering context. The runner calls
`build_context_extensions()` during context building, after the base
context (artifacts, paths, job state) is assembled.

### Implementation

A bundle provides context extensions by including an optional
`context_extensions.py` module in the bundle root. This module must
export a `build_context_extensions()` function that returns a dict of
additional context variables.

The `WorkflowBundle` dataclass (in `workflow_packages/base.py`) carries
a `context_extensions_path` field pointing to this module. The loader
(`workflow_packages/loader.py`) detects the file during bundle loading.

### Resolution Order

Context variables are resolved in this order:

1. Base context -- job state, artifact paths, runtime context
2. Artifact values -- resolved artifact content injected by key
3. Path placeholders -- `{CODEBASE_DOC_ROOT}`, `{DELIVERY_DOC_ROOT}`,
   etc. resolved to absolute paths
4. Context extensions -- bundle-specific variables from
   `build_context_extensions()`
5. Prompt literal substitutions -- platform-defined constant
   substitutions from `prompt_literal_substitutions()` in `constants.py`

### Rules

- Context extension keys must not shadow base context keys
- All injected path placeholders must use absolute paths
- Context extensions are read-only from the bundle's perspective -- the
  runner owns the context lifecycle

## Artifact Resolution

### `resolve_repo_or_runtime_path()`

Defined in `runtime_context.py`. This function resolves artifact paths
by checking:

1. **Job state** -- if the artifact has a resolved path in the current
   job state, use it
2. **Known artifact paths** -- fall back to `known_artifact_paths()`
   from `constants.py`

This allows workflows to reference artifacts that may or may not exist
yet in the current job. First-step artifacts that have not been produced
resolve to their canonical path location even before they exist on disk.

### Artifact Key System

Artifact keys flow through the layered constant system:

- `artifact_keys.py` -- canonical `ARTIFACT_KEY_*` literals
- `path_primitives.py` -- stable filename and root constants
- `path_catalog.py` -- `known_artifact_paths()` and
  `legacy_artifact_paths()` mappings
- `constants.py` -- single re-export point

Bundles reference artifacts by key, never by hardcoded path. The
platform resolves keys to paths at runtime.

### Path Proxy

`runtime_context.py` provides a `PathProxy` class that lazily resolves
paths from the current runtime context. This allows module-level path
constants (like `PROJECT_ROOT`, `RUNNER_ROOT`, `JOBS_ROOT`,
`ARTIFACT_ROOT`) to work correctly even when the context is set after
module import.

## Path Contracts

### `build_output_paths()`

A bundle may include an optional `output_paths.py` module that exports
a `build_output_paths()` function. This function returns a dict mapping
artifact keys to output path specifications.

The platform uses this to:

- validate that the bundle declares where its outputs go
- resolve output paths consistently across execution modes
- enforce write-path constraints during step execution

### Workflow Path Contracts

`workflow_path_contracts.py` defines output path mappings for known
workflows. Bootstrap workflows use `resolve_workflow_output_paths()`
to map their artifacts to canonical locations.

### Runtime Context Paths

The runtime context (`runtime_context.py`) provides these root paths:

| Constant | Description |
|---|---|
| `PROJECT_ROOT` | The repository root (workspace root). |
| `RUNNER_ROOT` | The global runner home (`~/.ukbe-runner/`). |
| `JOBS_ROOT` | The job state directory (`RUNNER_ROOT/jobs/`). |
| `ARTIFACT_ROOT` | The artifact storage root. |
| `PACKAGE_ROOT` | The `agent_runner_v2/` package directory. |

These are resolved at import time from the current context and may be
overridden via `set_context()` for testing.

## Meta Sidecar

### Contract

The `meta.json` sidecar is the sole communication channel between the
coder and the runner. The contract is:

1. The coder writes `meta.json` to the path specified by the runner
2. The runner reads `meta.json` after the coder process completes
3. The sidecar contains the step result: status, remark, artifacts,
   usage data

### Rules

- No pre-invocation sidecar writes -- the runner does not create the
  sidecar before the coder runs
- No stdout JSON parsing -- the runner reads only from the sidecar file
- No disk recovery functions -- if the sidecar is missing, the step
  fails with `MetaJsonMissingError`
- The sidecar settles after the coder completes -- the runner polls for
  the file with a configurable settle delay

### Sidecar Polling

`coder_adapters.py` implements sidecar polling:

- `SIDECAR_POLL_INTERVAL_SECONDS` -- polling interval (default: 3.0s)
- `SIDECAR_SETTLE_DELAY_SECONDS` -- delay after coder exit to allow
  file writing (default: 5.0s)
- `DEFAULT_SIDECAR_POST_COMPLETE_GRACE_SECONDS` -- grace period after
  completion before forced termination (default: 12.0s)

### Sidecar Schema

The meta.json sidecar must contain:

```
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED" | "REJECTED",
    "remark": "<string>",
    "artifacts": { "<key>": "<path>", ... },
    "recorded_at": "<ISO-8601 timestamp>",
    "usage": {
      "input_tokens": <number>,
      "output_tokens": <number>,
      "total_tokens": <number>
    }
  }
}
```

## Notification Integration

### Service

`notification_manager.py` provides the centralized notification service.
It wraps the lower-level `notifications.py` module with context
enrichment and configuration-driven event filtering.

### Available Events

| Event | Description |
|---|---|
| `STEP_COMPLETED` | A step finished successfully. |
| `STEP_REJECTED` | A step was rejected by the coder. |
| `STEP_FAILED` | A step encountered a hard failure. |
| `WORKFLOW_STARTED` | A workflow execution began. |
| `WORKFLOW_COMPLETED` | A workflow execution finished. |
| `APPROVAL_REQUIRED` | A step requires human approval. |

### Configuration

Notifications are configured in `~/.ukbe-runner/config.json`:

- `notification.enabled` -- global toggle
- `notification.step_events` -- per-event-type toggles
- Provider-specific settings (e.g., Pushover `api_token`,
  `user_key`)

### Bundle Integration

Bundles opt into notifications per-step via
`enable_notifications: true` in the step configuration. The
notification manager automatically enriches the notification context
with job ID, step name, workflow name, and artifact information.

## Backend Sync Protocol

### Backend Client

`backend_client.py` provides the `BackendClient` class for
communicating with the workflow backend API. The backend is used
primarily in daemon mode.

### Protocol Operations

| Operation | Description |
|---|---|
| Claim | Daemon polls for available workflow claims. |
| Status update | Runner reports step/job status to the backend. |
| Artifact sync | Runner uploads artifact metadata to the backend. |
| Approval | Human approval decisions are sent to the backend. |
| Job listing | Active runs are listed for monitoring. |

### Sync Payload

The job sync payload includes:

- Job ID and workflow name
- Current step and status
- Artifact mappings (null/empty artifacts are filtered out)
- Usage aggregation
- Step completion timestamps

### Daemon Communication

In daemon mode, `daemon_runtime.py` spawns a subprocess per workflow
invocation. The subprocess communicates results back through the job
state directory and backend API, not through stdout. The daemon itself
is a polling loop that checks for new claims and monitors subprocess
completion.

## Action Registration

### `@action()` Decorator

Defined in `workflow_packages/actions/__init__.py`. The decorator
registers a function as a named action in the global `REGISTERED_ACTIONS`
dict.

### Usage

```python
from agent_runner_v2.workflow_packages.actions import action

@action("my_custom_action")
def my_custom_action(*, context, state, step_cfg, project_root):
    # ... implementation ...
    return ActionResult(status="APPROVED", ...)
```

### Action Signature

All action functions must accept these keyword arguments:

| Parameter | Type | Description |
|---|---|---|
| `context` | `dict` | Rendered context variables. |
| `state` | `dict` | Current job state. |
| `step_cfg` | `dict` | Step configuration from the manifest. |
| `project_root` | `Path` | Repository root path. |

### Return Type

Actions must return an `ActionResult` (from `action_result.py`). The
`ActionResult` carries:

- `status` -- `"APPROVED"` or `"REJECTED"`
- `remark` -- human-readable summary
- `artifacts` -- mapping of artifact keys to paths

### Dispatch Order

When a step specifies `action = "some_action"`:

1. The runner checks `REGISTERED_ACTIONS` (populated by `@action()`
   decorators from loaded bundles)
2. If not found, the runner falls back to the global `ACTION_REGISTRY`
   in `actions/__init__.py`
3. If still not found, the step fails

### Bundle Loading and Action Registration

When `workflow_packages/loader.py` loads a bundle, it checks for an
`actions.py` module in the bundle root. If found, it imports the module
via `importlib`, which triggers the `@action()` decorators and
registers the functions. This happens before step execution begins.
