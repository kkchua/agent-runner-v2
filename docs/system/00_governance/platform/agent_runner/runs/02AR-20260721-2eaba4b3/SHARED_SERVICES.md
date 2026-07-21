---
template_id: "SYS-02-SS"
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 shared services contract for agent-runner-v2"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02AR-20260721-2eaba4b3"
---

# agent-runner-v2 Shared Services

This document defines the runtime services available to Layer 3 workflow bundles on the agent-runner-v2 platform.

## Context Extensions

Layer 3 bundles may inject additional context variables into the prompt rendering pipeline by providing a `context_extensions.py` module with a `build_context_extensions()` function.

### Function Signature

```
def build_context_extensions( *, state: dict, step: str, step_cfg: dict, ctx: dict[str, str], project_root: Path | None = None, ) -> dict[str, str]:
```

The function receives:

- `state`: The current job state dictionary.
- `step`: The current step name.
- `step_cfg`: The current step configuration dictionary.
- `ctx`: The base context dictionary already populated by the runner.
- `project_root`: The project root directory path (optional).

It returns a dictionary of additional context variables that are merged into the prompt rendering context. Keys become template variables available in prompt files. Common extension variables include artifact path mappings, reference file paths, and dynamic identifiers.

### Pattern

Bundles declare their context extensions convention by implementing `build_context_extensions()` in `context_extensions.py`. The runner discovers this module through the bundle's `workflow.toml` configuration and calls it during context assembly before rendering each prompt.

The returned dictionary may include any string keys. When a key matches an artifact key, the runner automatically derives corresponding `_PATH` and `_METAJSON` suffixed variants. Paths are resolved using `resolve_repo_or_runtime_path()` to produce absolute paths that the coder can use directly.

## Artifact Resolution

The `resolve_repo_or_runtime_path()` function is the single entry point for resolving artifact paths from their namespace-qualified string forms to absolute filesystem paths.

### Function Signature

```
def resolve_repo_or_runtime_path( path_str: str, *, project_root: Path | None = None, runtime_root: Path | None = None, ) -> Path:
```

### Resolution Order

The function dispatches by path prefix (namespace routing):

1. **Absolute paths** are returned unchanged. If the path is already absolute, no resolution is performed.

2. **Repository-owned paths**: Paths starting with `docs/`, `archive/`, `scripts/`, or `temp/` resolve under the project root. These are files that belong to the repository working tree. The resolved path is `project_root / path_str`.

3. **Runner-home paths**: Paths starting with `.ukbe-runner/` resolve under the runner home directory. The prefix `.ukbe-runner/` is stripped and the remainder is joined to the runner home.

4. **Everything else**: Any path that does not match the above prefixes resolves under the jobs root (`runner_home / "jobs"`). This covers job-scoped runtime artifacts that live outside the repository.

If `project_root` is not provided, falls back to the current workspace root from the runtime context. If `runtime_root` is not provided, falls back to the runner home for `.ukbe-runner/` paths or the jobs root for everything else.

## Path Contracts

Layer 3 bundles may define their own artifact path mappings by providing an `output_paths.py` module with a `build_output_paths()` function.

### Function Signature

The required signature for `build_output_paths()` is:

```
def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:
```

Bundle implementations may accept additional optional parameters (e.g., `loop_iteration`) for their own internal use. The runner calls this function through the bundle's `output_paths.py` module, passing the `job_id` and `mode` values.

The function returns a dictionary mapping artifact keys to their relative paths within the repository or runtime storage.

### Pattern

The returned dictionary maps artifact keys (e.g., `MY_OUTPUT_FILE`) to relative paths (e.g., `docs/my_output/{job_id}/output.md`). The runner uses these mappings to:

- Resolve the expected write path for each produced artifact.
- Validate that approved steps have actually written the declared files.
- Populate context variables so prompt templates can reference output paths by key.

The `{job_id}` and `{mode}` placeholders are filled by the caller. Additional placeholders may be added by bundle-specific implementations.

## Meta Sidecar

The meta.json sidecar is the primary communication channel between the coding agent and the runner for each step.

### Sidecar Format

The sidecar uses the v2 schema:

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED",
    "remark": "Brief summary of what was accomplished.",
    "artifacts": {
      "MY_OUTPUT_FILE": "docs/my_output/abc123/output.md"
    },
    "recorded_at": "2026-07-22T00:01:00+08:00",
    "usage": {
      "input_tokens": 12345,
      "output_tokens": 678,
      "total_tokens": 13023
    }
  }
}
```

### Write Function

```
def write_meta_sidecar(meta_path_like: str | Path, *, status: str, remark: str, artifacts: dict, project_root: Path | None = None, runtime_root: Path | None = None, extra: dict[str, Any] | None = None) -> Path:
```

This function writes a v2 meta.json sidecar using the shared path resolver. It accepts a status string (`APPROVED` or `REJECTED`), a remark, an artifacts dictionary, and optional extra fields. Artifact paths are formatted to absolute paths for consistency using `format_report_artifacts()`. The file is written atomically via a temporary file and rename.

### Repair Fallback

While the meta.json sidecar is the primary communication channel, the runner also supports a repair fallback through `_repair_or_validate_meta_json()` in `step_runner.py`. This function handles cases where the coder produced a direct result object (e.g., `{"status": "APPROVED", "remark": "...", "artifacts": {...}}`) instead of the wrapped v2 sidecar format. The repair function coerces the direct result into the expected v2 schema and writes the corrected sidecar to disk. This ensures robustness against common coder output patterns without sacrificing the primary sidecar contract.

The runner reads the sidecar after the coder completes. The coder must write this file to the expected path (provided in the prompt via sidecar instructions). If the file is missing and no repairable direct result is available, the runner raises `MetaJsonMissingError`.

## Notification Integration

The notification system (`notification_manager.py`) provides a unified interface for sending workflow and step notifications.

### Public Functions

- `should_send_notifications()` -- Returns `True` if notifications are globally enabled in the runner config.
- `send_workflow_notification(status, context)` -- Sends a workflow-level notification. Accepts status strings: `COMPLETED`, `FAILED`, `WAITING_FOR_HUMAN_INTERVENTION`.
- `send_step_notification(status, context, step, step_cfg)` -- Sends a step-level notification. Accepts status strings: `STEP_COMPLETED`, `STEP_FAILED`, `STEP_REJECTED`. Requires `enable_notifications: true` in the step configuration and checks per-event config toggles.

### Integration Pattern

Bundles do not call notification functions directly. The runner calls them automatically at job lifecycle transitions (completion, failure, human-wait states) and at step lifecycle transitions (completion, rejection, failure). Bundle authors control notification behavior through:

1. The global notification config (`~/.ukbe-runner/config.json`).
2. Step-level `enable_notifications` flag in `workflow.toml`.
3. Per-event toggles (`notification.step_events.completed`, `.rejected`, `.failed`).

## Backend Sync Protocol

In daemon/backend mode, the runner communicates with a remote backend via the `BackendClient` class (`backend_client.py`).

### Configuration

The backend URL is configured in the runner config file or via environment variables. The client sends JSON payloads over HTTP to the backend API.

### BackendClient

The `BackendClient` class exposes the following public methods:

- `submit_run()`
- `approve_run()`
- `get_run()`
- `list_runs()`
- `stop_run()`
- `reset_run_step()`
- `register_worker()`
- `heartbeat()`
- `claim_step()`
- `complete_step_run()`
- `sync_job_state()`
- `create_artifact()`
- `create_event()`
- `cleanup_execution()`

Each method sends an HTTP request to the backend API and returns the parsed JSON response as a dictionary. The client handles HTTP error status codes and URL errors by raising `RuntimeError` with diagnostic information.

### Protocol Flow

1. The daemon registers via `register_worker()`.
2. Work is claimed via `claim_step()`.
3. During child execution, liveness is reported via `heartbeat()` with child-scoped state information.
4. On completion, results are submitted via `complete_step_run()`.
5. Job state synchronization is done via `sync_job_state()`.
6. Artifacts and events may be created via `create_artifact()` and `create_event()`.

## Action Registration

Action functions are Python functions decorated with `@action()` that the runner can dispatch to as non-coder steps.

### Decorator

```
def action(name: str | None = None) -> Callable[[ActionFn], ActionFn]:
```

Usage:

```python
from agent_runner_v2.workflow_packages.actions import action
from agent_runner_v2.action_result import ActionResult

@action("my_custom_action")
def my_custom_action(*, context, state, step_cfg, project_root):
    # ... implementation ...
    return ActionResult(status="APPROVED", remark="Done.", artifacts={})
```

The `name` parameter specifies the action name used in `workflow.toml` (`action = "my_custom_action"`). When omitted, the function's own `__name__` is used.

### Registration and Discovery

Actions registered via the `@action()` decorator are collected into `REGISTERED_ACTIONS` when the bundle's `actions.py` module is loaded. The runner discovers actions in two ways:

1. **Bundle-local actions**: When a bundle's `actions.py` module is imported, all `@action()`-decorated functions within that module are automatically registered. The runner dispatches to these actions before consulting the global registry.

2. **Global actions**: Platform-level actions are registered in the global `ACTION_REGISTRY` and are available to all bundles.

### ActionResult

Action functions must return an `ActionResult` dataclass:

```python
@dataclass
class ActionResult:
    status: str           # "APPROVED" | "REJECTED"
    remark: str
    artifacts: dict
    reject_code: str | None = None
```

The runner automatically writes a meta.json sidecar from the `ActionResult` after the action completes.
