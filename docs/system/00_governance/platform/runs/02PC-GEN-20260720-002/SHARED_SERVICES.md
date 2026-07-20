---
template_id: SYS-02-SS
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 shared services contract; defines runtime services available to Layer 3 bundles"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-002"
---

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
    env: dict,
) -> dict[str, str]:
```

**Parameters:**

- `context`: The current prompt context dict (artifact paths, governance
  paths, workflow metadata).
- `state`: The current job state dict (step name, job ID, accumulated
  artifacts).
- `env`: The resolved environment dict (.env values, config values).

**Returns:** A dict of additional context variable names to their string
values. These are merged into the prompt rendering context and are
available as `{KEY}` placeholders in prompt templates.

**Example:**

```python
def build_context_extensions(context, state, env):
    return {
        "MY_BUNDLE_OUTPUT_ROOT": "docs/system/my_bundle/runs/{job_id}",
        "MY_BUNDLE_TEMPLATE": "templates/default.txt",
    }
```

### Context Loading

The runner (`step_runner.py`) loads context extensions during prompt
rendering. The workflow bundle's `context_extensions.py` is imported
dynamically via `importlib.util`. This allows each bundle to maintain its
own context injection logic without modifying the platform core.

## Artifact Resolution

### `resolve_repo_or_runtime_path()`

Provided by `runtime_context.py`, this function resolves artifact paths
using the repo/runtime namespace convention.

**Signature:**

```python
def resolve_repo_or_runtime_path(
    path_str: str,
    *,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
) -> Path:
```

**Resolution rules:**

- `docs/...` and other repo-owned paths resolve under the project root.
- `.ukbe-runner/...` paths resolve under the runner home.
- Other relative paths resolve under the jobs root.
- Absolute paths are returned unchanged.

### `known_artifact_paths()`

Provided by `constants.py`, this function maps artifact keys to their
canonical repository-relative paths.

**Signature:**

```python
def known_artifact_paths() -> dict[str, str]:
```

Returns a dict mapping artifact keys (e.g., `"REVIEW_FILE_SUGGESTED"`) to
repository-relative path strings. This is the primary mechanism for
resolving artifact paths in prompt templates via `{ARTIFACT_KEY_*}`
placeholders.

### Artifact Placeholder Resolution

Workflow prompt templates use `{ARTIFACT_KEY_*}` placeholders matching
keys from `artifact_keys.py`. The runner resolves these placeholders
during prompt rendering using `known_artifact_paths()` and the layered
constants system. Bundle authors should use artifact keys, not hardcoded
paths.

## Path Contracts

### `build_output_paths()`

Workflow bundles may define an `output_paths.py` module with a
`build_output_paths()` function. This function returns the bundle's owned
output path mappings.

**Signature:**

```python
def build_output_paths(
    job_id: str = "{job_id}",
    mode: str = "{mode}",
) -> dict[str, str]:
```

**Returns:** A dict of `{artifact_key: relative_path}` mappings for all
artifacts owned by this workflow bundle.

### Workflow Path Contracts

The platform module `workflow_path_contracts.py` provides
`resolve_workflow_output_paths()` which resolves a workflow bundle's
output path contract by template group name and job ID.

**Signature:**

```python
def resolve_workflow_output_paths(
    template_group: str,
    job_id: str = "{job_id}",
    mode: str = "{mode}",
) -> dict[str, str]:
```

### Layered Constants System

All path constants flow through a layered architecture:

1. `artifact_keys.py` - canonical artifact key literals (e.g.,
   `ARTIFACT_KEY_REVIEW`, `ARTIFACT_KEY_CODEBASE_INVENTORY`)
2. `path_primitives.py` - stable filename/root constants and helper
   functions
3. `path_catalog.py` - computed mappings from keys to paths
4. `constants.py` - re-exports everything as the single import surface

Bundle authors should import path constants from `constants.py` and use
artifact keys for all path references.

## Meta Sidecar

### `write_meta_sidecar()`

Provided by `runtime_context.py`, this function writes a v2-compliant
`meta.json` sidecar file. The meta.json sidecar is the sole communication
channel between a coder (or action) and the runner.

**Signature:**

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

**Parameters:**

- `meta_path_like`: Target path for the sidecar (repo-relative or absolute).
- `status`: `"APPROVED"` or `"REJECTED"`.
- `remark`: Human-readable summary of the result.
- `artifacts`: Dict mapping artifact keys to their file paths.
- `extra`: Optional extra fields to include in the payload.

### Sidecar Format

The meta.json sidecar uses the v2 schema:

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED",
    "remark": "Brief summary of what was accomplished",
    "artifacts": {
      "MY_ARTIFACT_KEY": "path/to/output.md"
    },
    "recorded_at": "2026-07-20T11:30:28+08:00"
  }
}
```

### Sidecar Contract

- The meta.json sidecar is the ONLY communication channel. No stdout JSON
  parsing, no pre-invocation sidecar writes, and no disk recovery functions.
- The runner reads the sidecar after coder/action execution and routes based
  on the `status` field.
- Artifact paths in the sidecar should be absolute or repo-runtime-relative.

## Notification Integration

### `send_workflow_notification()`

Provided by `notification_manager.py`, sends a workflow-level notification
about job lifecycle events (started, completed, failed, awaiting approval).

### `send_step_notification()`

Provided by `notification_manager.py`, sends a step-level notification
about step execution events (started, completed, rejected, failed).

### Configuration

Notifications are configured in `~/.ukbe-runner/config.json` under the
`notification` key. The platform supports Pushover and console
notification channels. Bundle steps opt into notifications via
`enable_notifications = true` in `workflow.toml`.

## Backend Sync Protocol

### Daemon-Worker Communication

When running in daemon mode, the daemon (`daemon.py`) communicates with a
backend service:

1. **Poll**: The daemon polls `GET /api/workflow/claim` at a configurable
   interval.
2. **Claim**: On receiving a claim, the daemon spawns a subprocess:
   `python -m agent_runner_v2.run_agent run --template-group <name>
   --project-root <path>`.
3. **Report**: After execution, the daemon reports results via
   `POST /api/execution/result`.
4. **Heartbeat**: The daemon maintains a heartbeat for claimed work.

### Job Sync Payload

The job sync payload (built by `job_state.py`) includes:

- Job ID and workflow name
- Current step and step index
- Step execution history
- Accumulated artifact references
- Execution status and failure information

### Backend Step Routing

When a step completes in daemon mode, the backend may provide the next
step route. The router (`workflow_router.py`) uses
`resolve_transition()` as a fallback when the backend does not send a
`next_step`, since the worker never sends its own `next_step`.

## Action Registration

### `@action()` Decorator

Custom actions in a bundle's `actions.py` are registered using the
`@action()` decorator from the platform action framework. This makes the
action callable by name from `workflow.toml` step configurations.

**Pattern:**

```python
from agent_runner_v2.actions import action

@action(name="my_custom_action")
def my_custom_action(state, context, env):
    # Perform action logic
    # Write meta.json sidecar with result
    return {"status": "APPROVED", "remark": "Action completed"}
```

### Platform Action Library

The platform ships with 30+ built-in actions in `agent_runner_v2/actions/`
covering:

- Validation (`validate_*` actions)
- Publishing (`publish_*` actions)
- Context collection (`collect_*` actions)
- File operations (copy, assemble, scan)
- Workflow lifecycle (`step_completion`, `human_approval`)

Bundle authors should use platform actions where possible and register
custom actions only for bundle-specific logic.

### Action Contract

Every action, whether platform-provided or bundle-custom, must:

1. Accept `state`, `context`, and `env` parameters.
2. Write a `meta.json` sidecar with `status` and `remark`.
3. Return a dict with at least `status` and `remark` keys.
4. Not write to markdown files or other artifacts directly (use the coder
   pattern for content generation).
