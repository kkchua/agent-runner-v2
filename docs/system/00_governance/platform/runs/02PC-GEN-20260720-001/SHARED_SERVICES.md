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
effective_version: "02PC-GEN-20260720-001"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `generate_platform_core_docs`
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

- `context` - The current context dictionary (artifact paths, governance
  rules, job metadata).
- `state` - The current job state (current step, accumulated artifacts,
  backend coordination data).
- `step_config` - The `StepConfig` dataclass for the current step.

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
them available as `{KEY_NAME}` placeholders in prompts.

## Artifact Resolution

### `resolve_repo_or_runtime_path()`

The platform provides `resolve_repo_or_runtime_path()` in
`runtime_context.py` for resolving artifact paths across two namespaces:

- **Repo namespace** (`docs/...`, `archive/...`, `scripts/...`,
  `temp/...`) - resolves under the project root.
- **Runtime namespace** (`.ukbe-runner/...`) - resolves under the global
  runner home.
- **Absolute paths** - returned unchanged.

**Signature:**

```python
def resolve_repo_or_runtime_path(
    path_str: str,
    *,
    project_root: Path | None = None,
    runtime_root: Path | None = None,
) -> Path:
```

**Usage in bundles:**

Bundle actions and context extensions use this function to resolve
artifact paths that may live in either the repository or the runner's
runtime directories:

```python
from agent_runner_v2.runtime_context import resolve_repo_or_runtime_path

artifact_path = resolve_repo_or_runtime_path("docs/output/my_artifact.md")
```

### `known_artifact_paths()`

`agent_runner_v2/constants.py` exports `known_artifact_paths()`, which
returns a mapping of canonical artifact keys to their resolved file paths.
This is the primary mechanism for resolving artifact key placeholders
like `{REVIEW_FILE_SUGGESTED}` in prompt templates.

Bundles should reference artifact keys rather than hardcoding paths. The
platform resolves keys to paths at render time.

## Path Contracts

### `build_output_paths()`

Workflow bundles may define a `output_paths.py` module with a
`build_output_paths()` function. This function returns a dictionary
mapping artifact keys to their target file paths (relative to the project
root or job directory).

**Signature:**

```python
def build_output_paths(job_id: str, project_root: Path) -> dict[str, str]:
    """Return a mapping of artifact key -> relative output path."""
```

**Example:**

```python
def build_output_paths(job_id, project_root):
    run_dir = f"docs/system/00_governance/platform/runs/{job_id}"
    return {
        "L2_PLATFORM_INDEX": f"{run_dir}/README.md",
        "L2_RUNTIME_MODEL": f"{run_dir}/RUNTIME_MODEL.md",
    }
```

The runner uses `build_output_paths()` to determine where the coder
should write each artifact. The returned paths are injected into the
prompt context so the coder knows where to place outputs.

### Workflow-Owned Path Contracts

`agent_runner_v2/workflow_path_contracts.py` defines output path mappings
for bootstrap workflows. These contracts use the pattern
`resolve_workflow_output_paths()` to compute paths based on the job ID
and project root.

Layer 3 bundles define their own path contracts in `output_paths.py`.
Platform-level path contracts should not be modified by bundles.

## Meta Sidecar

### `meta.json` Contract

The `meta.json` sidecar is the sole communication channel between the
coder and the runner. After every step execution, the coder writes a
`meta.json` file alongside its output artifacts.

**Sidecar structure (v2 schema):**

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED",
    "remark": "Brief summary of what was accomplished",
    "artifacts": {
      "MY_OUTPUT_KEY": "path/to/output.md"
    },
    "recorded_at": "2026-07-20T01:10:33+08:00"
  }
}
```

**Required fields:**

| Field | Required | Description |
|---|---|---|
| `schema_version` | Yes | Must be `"v2"`. |
| `coder_result.status` | Yes | `"APPROVED"` or `"REJECTED"`. |
| `coder_result.remark` | Yes | Human-readable summary of the step outcome. |
| `coder_result.artifacts` | Yes | Map of artifact keys to their file paths. Keys must match the step's `produces` list. |
| `coder_result.recorded_at` | Yes | ISO 8601 timestamp with timezone offset. |

**Additional fields:**

| Field | Required | Description |
|---|---|---|
| `coder_result.reject_code` | No | Machine-readable rejection code (e.g., `"LAYER1_REDEFINITION"`). |
| `coder_result.reject_reason` | No | Human-readable explanation for rejection. |
| `coder_result.reject_citations` | No | List of citations to offending content. |

### `write_meta_sidecar()`

The platform provides `write_meta_sidecar()` in `runtime_context.py` for
writing a properly formatted meta.json sidecar:

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

**Usage:**

```python
from agent_runner_v2.runtime_context import write_meta_sidecar

write_meta_sidecar(
    "path/to/meta.json",
    status="APPROVED",
    remark="Generated platform core docs",
    artifacts={"L2_PLATFORM_INDEX": "path/to/README.md"},
)
```

### `artifact_rel_to_meta_rel()`

Given a relative artifact path, `artifact_rel_to_meta_rel()` returns the
corresponding meta.json sibling path:

```python
artifact_rel_to_meta_rel("docs/output/my_doc.md")
# Returns: "docs/output/my_doc.meta.json"
```

### Context Key Construction

When a step's `produces` list includes artifact keys, the runner
automatically constructs `_METAJSON` context keys for each:

```
{ARTIFACT_KEY_NAME}        -> absolute path to the artifact
{ARTIFACT_KEY_NAME}_METAJSON -> absolute path to its meta.json sidecar
```

For example, if a step produces `MY_OUTPUT`, the prompt context includes:
- `{MY_OUTPUT}` - path to the output file
- `{MY_OUTPUT}_METAJSON` - path to its sidecar

## Notification Integration

### `notification_manager.py`

The notification manager provides a unified interface for sending
workflow and step notifications across all execution modes. Bundles
control notification behavior through `workflow.toml` configuration
rather than calling the notification API directly.

### Configuration

Notifications are configured globally in `~/.ukbe-runner/config.json`:

```json
{
  "notification": {
    "enabled": true,
    "pushover_user_key": "...",
    "pushover_api_token": "..."
  }
}
```

### Step-Level Control

Each step sets `enable_notifications = true` or `false` in
`workflow.toml`. The runner calls the notification manager automatically
before and after step execution when enabled.

### Notification Events

The runner emits notifications for:

- Step started (with step name and job ID)
- Step completed (with status: APPROVED or REJECTED)
- Human approval required
- Workflow completed or failed

Bundle actions do not need to call notification APIs directly. The runner
handles notification dispatch based on step configuration.

## Backend Sync Protocol

### Daemon Communication

In daemon mode, the worker communicates with a backend service for:

- **Work claims**: Polling `GET /api/work/claim` for pending steps.
- **Result reporting**: Posting step results to the backend.
- **Heartbeats**: Sending periodic liveness signals keyed by
  `workflow_step_run_id`.
- **Approval polling**: Checking for human approval decisions on steps
  that require it.

### `backend_client.py`

The backend client module handles API communication. Daemon workers use
it to claim work and report results. Manual mode may also use it when a
backend URL is configured.

### `backend_execution.py`

The backend execution module handles the execution contract for
backend-driven steps. It maps backend workflow definitions to local
runner invocations.

### Job Sync Payload

When reporting to the backend, the runner builds a job sync payload
containing:

- Job ID and workflow name
- Current step and step index
- Step status (running, completed, failed, awaiting_approval)
- Artifact key-to-path mappings (with null artifacts filtered out)
- Timestamps

Layer 3 bundles do not need to interact with the backend protocol
directly. The platform handles sync automatically.

## Action Registration

### `@action()` Decorator

Custom actions in a bundle's `actions.py` are registered using the
`@action()` decorator:

```python
from agent_runner_v2.workflow_packages.actions import action

@action(name="my_custom_action")
def my_custom_action(context, state, step_config):
    """Perform a custom action and return a result."""
    # ... implementation ...
    return {"status": "APPROVED", "remark": "Action completed"}
```

The runner discovers actions through the workflow package loader
(`workflow_packages/loader.py`). Actions are referenced by name in
`workflow.toml`:

```toml
[[step]]
name = "custom_step"
action = "my_custom_action"
```

### Platform Actions

Platform-level actions in `agent_runner_v2/actions/` are available to all
bundles. These include:

- `collect_context` - Gather curated reference inputs
- `validate` - Run deterministic validation rules
- `publish` - Activate an approved artifact set
- `step_completion` - Close the workflow
- `copy`, `scan`, `assemble` - General-purpose document operations

### Action Result Contract

Actions must return a dictionary with at least:

```python
{
    "status": "APPROVED",      # or "REJECTED"
    "remark": "Description",   # Human-readable summary
    "artifacts": {             # Map of artifact key -> path
        "KEY": "path/to/file"
    }
}
```

The action result is written to the `meta.json` sidecar by the runner
after the action completes.
