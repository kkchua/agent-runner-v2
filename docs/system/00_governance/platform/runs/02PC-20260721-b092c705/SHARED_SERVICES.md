---
template_id: SYS-02-SS
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 shared services document; defines runtime services available to Layer 3 bundles on agent-runner-v2"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-20260721-b092c705"
managed_by: workflow-generated
---

# Shared Services

## Purpose

This document defines the runtime services available to Layer 3 workflow
bundles on agent-runner-v2. These services are provided by the platform
runtime and are consumed by bundles through well-defined interfaces.

## Context Extensions

Layer 3 bundles may define a `context_extensions.py` module that exports
a `build_context_extensions()` function. This function is called by the
runner before each step to inject bundle-specific variables into the
prompt context.

### Function Signature

Taken from the actual platform source (any bundled `context_extensions.py`):

```python
def build_context_extensions(
    *,
    state: dict,
    step: str,
    step_cfg: dict,
    ctx: dict[str, str],
    project_root: Path | None = None,
) -> dict[str, str]:
```

### Parameters

- `state` -- The current workflow state dictionary (includes `job_id`,
  `template_group`, `loop_context`, and other runtime state).
- `step` -- The name of the current step being executed.
- `step_cfg` -- The step configuration dictionary from `workflow.toml`
  and template groups.
- `ctx` -- The current context dictionary (may contain pre-populated
  artifact paths and platform variables).
- `project_root` -- The absolute path to the project root directory.

### Returns

A dictionary of variable name to string value. These variables are
merged into the prompt context and available as `{VARIABLE_NAME}`
placeholders in prompt files.

### Usage

The function typically:

1. Resolves artifact keys to absolute file paths using
   `resolve_repo_or_runtime_path()`.
2. Injects artifact key aliases (`{KEY}_PATH`, `{KEY}_METAJSON`).
3. Exposes reference file paths (masterplan, governance roots).
4. Returns the enriched dictionary.

### When Defined

`context_extensions.py` is optional. When absent, the runner uses only
the platform-provided context variables (workspace root, job ID, step
name, runtime roots).

## Artifact Resolution

### `resolve_repo_or_runtime_path()`

Resolves a relative path string to an absolute `Path` using a prefix-based
namespace dispatch convention. This is the single artifact resolution
function used throughout the platform.

### Function Signature

Taken from the actual platform source (`runtime_context.py`):

```python
def resolve_repo_or_runtime_path(
    path_str: str,
    *,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
) -> Path:
```

### Resolution Order

The function dispatches by path prefix. It does not check the filesystem
for existence before resolving.

1. **Absolute paths** -- Returned unchanged. If `path_str` is already an
   absolute path, it is returned as-is.

2. **Repo-owned prefixes** -- Paths starting with `docs/`, `archive/`,
   `scripts/`, or `temp/` are resolved under the project root
   (typically the workspace root).

3. **Runner-home paths** -- Paths starting with `.ukbe-runner/` are
   resolved under the runner home directory (`~/.ukbe-runner`).

4. **Default (jobs root)** -- All other relative paths are resolved
   under the jobs root (`~/.ukbe-runner/jobs/`).

### Parameters

- `path_str` -- The relative or absolute path string to resolve.
- `project_root` -- Optional override for the project root. Defaults to
  the current workspace root.
- `runtime_root` -- Optional override for the root used by the
  `.ukbe-runner/` prefix. Defaults to the runner home.

## Path Contracts

### `build_output_paths()`

Each Layer 3 bundle may define a `build_output_paths()` function in an
optional `output_paths.py` module. This function maps artifact keys to
repo-relative file paths.

### Function Signature

Taken from the actual platform source (any bundled `output_paths.py`):

```python
def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
```

### Parameters

- `job_id` -- The job identifier used in path templates (e.g., run root
  subdirectory).
- `mode` -- The execution mode (e.g., `"bootstrap"`, `"daemon"`).

### Returns

A dictionary mapping artifact key to repo-relative path. Paths use
forward slashes and are relative to the project root.

### Path Convention

All paths should use the canonical governance structure:

- Permanent artifacts: `docs/system/00_governance/platform/runs/{job_id}/`
  (staged) or `docs/system/00_governance/platform/current/` (published)
- History snapshots: `docs/system/00_governance/platform/history/{job_id}/`

The path contract is resolved at runtime by the runner, which writes
step outputs to the declared locations.

## Meta Sidecar

The meta.json sidecar is the primary communication channel between the
coding agent (coder) and the runner. Every prompt-driven step instructs
the coder to write a `meta.json` file containing the step result.

### Sidecar Schema

The meta.json uses a v2 schema:

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED",
    "remark": "Brief summary of what was accomplished",
    "artifacts": {
      "KEY": "path/to/artifact.md"
    },
    "recorded_at": "2026-07-21T16:43:45+08:00",
    "usage": {
      "input_tokens": 1234,
      "output_tokens": 567,
      "total_tokens": 1801
    }
  }
}
```

### Required Fields

- `schema_version` -- Must be `"v2"`.
- `coder_result.status` -- Must be `"APPROVED"` or `"REJECTED"`.
- `coder_result.artifacts` -- Dict of artifact key to file path.
- `coder_result.recorded_at` -- ISO 8601 timestamp.

### Sidecar Resolution

The runner resolves the meta.json path before coder invocation using
`_resolve_meta_json_path()` in `step_runner.py`. Resolution priority:

1. `result_meta_key_from_context` -- A context variable pointing to the
   artifact path (the sidecar path is derived by replacing the file
   extension with `.meta.json`).
2. `result_meta_key` -- A precomputed `{KEY}_METAJSON` context variable.
3. Step directory fallback -- Defaults to `<step_dir>/meta.json`.

### Sidecar Repair

The meta.json sidecar is the primary channel, but the runner also
repairs missing or invalid sidecars. The `_repair_or_validate_meta_json()`
function in `step_runner.py` handles two repair scenarios:

1. **Missing sidecar** -- If the coder wrote no meta.json file, the
   runner inspects the coder's stdout output (parsed JSON). If the
   stdout contains a result object with `status` and `artifacts` fields,
   the runner constructs a valid meta.json from that output.

2. **Invalid sidecar** -- If the sidecar exists but fails schema
   validation (wrong version, missing fields, etc.), the runner attempts
   to repair it by:
   - First, checking if the invalid sidecar content can be coerced into
     a valid v2 payload.
   - If not, falling back to the coder's parsed stdout result.
   - If neither works, the step fails with a `MetaJsonInvalidError`.

This repair ensures that coders that emit results directly (rather than
writing a sidecar file) are still compatible with the platform contract.
Bundles should not rely on this repair; they should always instruct the
coder to write the sidecar explicitly.

### `write_meta_sidecar()`

The runtime provides a helper for writing meta.json sidecars. Defined in
`runtime_context.py`:

```python
def write_meta_sidecar(
    meta_path_like: str | Path,
    *,
    status: str,
    remark: str,
    artifacts: dict,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
    extra: dict[str, Any] | None = None,
) -> Path:
```

This function:

1. Resolves the meta path using `resolve_repo_or_runtime_path()`.
2. Creates parent directories.
3. Formats artifact paths to absolute paths.
4. Writes the v2 schema JSON atomically (via tempfile + replace).

## Notification Integration

The notification system (`notification_manager.py`) provides a
centralized interface for sending workflow and step notifications. It
is called by the runner after key lifecycle events.

### Notification Events

- Workflow started, completed, failed
- Step completed, rejected, failed
- Human approval requested

### Enabling Notifications

Notifications are enabled via the runner config file
(`~/.ukbe-runner/config.json`):

```json
{
  "notification": {
    "enabled": true,
    "step_events": {
      "completed": true,
      "rejected": true,
      "failed": true
    },
    "channels": {
      "webhook": {
        "type": "webhook",
        "url": "https://example.com/hook"
      }
    }
  }
}
```

### Calling from Bundles

Action functions in Layer 3 bundles may call `send_notification()` from
`agent_runner_v2.notifications` to send custom notifications. This
should be used sparingly and only for bundle-specific events.

## Backend Sync Protocol

The backend sync protocol enables the daemon to communicate with a
remote backend server for workflow orchestration. The daemon uses
`BackendClient` from `backend_client.py` for all backend communication.

### BackendClient

The `BackendClient` class wraps HTTP calls to the backend API. Each
method maps to a specific backend endpoint.

```python
@dataclass
class BackendClient:
    base_url: str
    timeout_seconds: int = 30
```

Public methods:

- `submit_run()` -- Submit a new workflow run to the backend.
- `approve_run()` -- Approve or reject a run at a human approval gate.
- `get_run()` -- Retrieve details for a specific workflow run.
- `list_runs()` -- List workflow runs with optional filters.
- `stop_run()` -- Request a running workflow to stop.
- `reset_run_step()` -- Reset a specific step in a workflow run.
- `register_worker()` -- Register a worker daemon with the backend.
- `heartbeat()` -- Send a worker heartbeat with current status and
  child execution details.
- `claim_step()` -- Claim the next available step for execution.
- `complete_step_run()` -- Submit a completed step result to the
  backend.
- `sync_job_state()` -- Synchronize the full job state (from
  `job.json`) to the backend.
- `create_artifact()` -- Create an artifact record associated with a
  run.
- `create_event()` -- Create an event record (log, status change)
  associated with a run.
- `cleanup_execution()` -- Clean up stale executions for a workflow.

### Sync Flow

1. Worker registers via `register_worker()`.
2. Worker polls via `claim_step()`. Backend returns a step to execute.
3. Worker spawns child, monitors, collects result.
4. Worker synchronizes result via `sync_job_state()`.
5. Worker heartbeats periodically via `heartbeat()`.
6. On shutdown, worker sends final heartbeat.

### Job State Synchronization

The `sync_job_state()` method is the preferred submission path. It
sends a comprehensive payload derived from `job.json`, including:

- Current run and step status
- Step outcomes and coder used
- Next step routing
- Artifacts produced
- Events emitted
- Error details if applicable

The `complete_step_run()` method is a fallback used when `job.json` is
not available.

## Action Registration

Action functions are registered via the `@action()` decorator, defined
in the platform's action registry. Actions are Python functions that
execute within the runner process (no coder subprocess).

### Decorator Usage

```python
from agent_runner_v2.workflow_packages.actions import action

@action("validate_docs")
def validate_docs(*, context, state, step_cfg, project_root):
    """Validate the generated documentation set."""
    # ... validation logic ...
    return ActionResult(
        status="APPROVED",
        remark="All checks passed",
        artifacts={"VALIDATION_REPORT": "docs/system/00_governance/platform/runs/{job_id}/validation.md"}
    )
```

### Action Function Contract

Every action function must accept keyword arguments:
- `context` -- Dict of context variables (artifact paths, platform vars).
- `state` -- Dict of workflow state.
- `step_cfg` -- Dict of step configuration.
- `project_root` -- Path to the project root.

Every action function must return an `ActionResult`:
```python
@dataclass
class ActionResult:
    status: str           # "APPROVED" | "REJECTED"
    remark: str
    artifacts: dict
    reject_code: str | None = None
```

### Action Resolution

When a step is configured with `action = "function_name"`, the runner
looks up the function in the action registry. Actions may be defined in:

- The bundle's own `actions.py` module
- The platform's built-in action modules

The runner automatically writes a meta.json from the `ActionResult` and
validates that produced artifacts exist on disk.
