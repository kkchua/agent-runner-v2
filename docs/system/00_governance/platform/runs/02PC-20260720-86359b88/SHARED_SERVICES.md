---
template_id: SYS-02-SS
version: "1.0"
doc_type: "platform_standard"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "permanent Layer 2 shared services reference; defines runtime services available to Layer 3 bundles"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-20260720-86359b88"
managed_by: workflow-generated
---

> Managed by workflow: `02_platform_core_foundation_v1` / step: `generate_platform_core_docs`
> This file is workflow-generated and protected from manual edits.

# Shared Services

## Purpose

This document defines the runtime services available to Layer 3 workflow
bundles on the agent-runner-v2 platform. These services are provided by
the platform runtime and may be consumed by any conforming bundle.

Layer 3 bundles should use these services rather than reimplementing
equivalent logic. The services are implemented in the `agent_runner_v2`
package and are stable across bundle versions.

## Context Extensions

The context extension pattern allows bundles to inject workflow-specific
data into the prompt rendering context.

### Pattern

A bundle provides a `context_extensions.py` module at the bundle root.
This module exports a `build_context_extensions()` function that returns
a dictionary of additional context values.

```python
def build_context_extensions(context: dict) -> dict:
    """Return additional key-value pairs for prompt rendering."""
    return {"CUSTOM_PATH": "/some/workflow/specific/path"}
```

### Execution

The step runner (`step_runner.py`) calls `build_context_extensions()`
during context construction. The returned values are merged into the
prompt rendering context alongside platform-provided values.

### Use Cases

Context extensions are appropriate for:

- workflow-specific directory prefixes or paths.
- computed values derived from workflow state.
- bundle-local constants needed in prompt templates.

Context extensions must not:

- override platform-provided context keys.
- perform filesystem mutations or side effects.
- contain workflow-specific directory prefixes that belong in
  `runtime_context.py`.

## Artifact Resolution

The platform provides a unified artifact path resolution service.

### Function

`resolve_repo_or_runtime_path()` in `runtime_context.py` resolves a
path that may exist either in the repository working tree or in the
runtime artifact store.

### Resolution Order

1. Check the repository working tree first.
2. Fall back to the runtime artifact root.
3. Return the resolved absolute path.

### Usage

Bundles use artifact resolution to locate input artifacts that may have
been produced by prior workflows or by the current workflow's earlier
steps. The resolution is transparent: the caller receives an absolute
path regardless of where the artifact physically resides.

### Path Constants

All artifact path resolution flows through the layered constants system:

- `artifact_keys.py` -- canonical key literals.
- `path_primitives.py` -- stable filename and root constants.
- `path_catalog.py` -- `known_artifact_paths()` computed mappings.
- `constants.py` -- layered re-export.

No hardcoded path strings are permitted.

## Path Contracts

The path contract system allows bundles to declare their output path
mappings explicitly.

### Pattern

A bundle provides an `output_paths.py` module at the bundle root. This
module exports a `build_output_paths()` function that returns a
dictionary mapping artifact keys to output paths.

```python
def build_output_paths(job_id: str, run_root: Path) -> dict:
    """Return artifact key to output path mappings."""
    return {
        "MY_ARTIFACT": run_root / "my_artifact.md",
    }
```

### Platform Path Contracts

The platform provides `workflow_path_contracts.py` which defines output
path mappings for platform-known workflows. The function
`resolve_workflow_output_paths()` resolves paths for bootstrap and
platform workflows.

### Integration

The step runner consults path contracts when determining where to expect
artifact outputs. Bundles that declare path contracts enable deterministic
artifact location without runtime discovery.

## Meta Sidecar

The `meta.json` sidecar is the sole communication channel between a
coder (LLM) and the runner. No stdout JSON parsing, no pre-invocation
sidecar writes, no disk recovery functions.

### Contract

After executing a prompt-driven step, the coder writes a `meta.json`
file containing:

```json
{
  "status": "APPROVED",
  "remark": "Summary of what was accomplished.",
  "artifacts": {
    "ARTIFACT_KEY": "path/to/artifact.md"
  },
  "usage": {
    "input_tokens": 1000,
    "output_tokens": 500,
    "total_tokens": 1500
  }
}
```

### Runner Behavior

The step runner (`step_runner.py`):

1. Polls for `meta.json` appearance after coder invocation.
2. Reads and validates the sidecar content.
3. Extracts artifact paths from the `artifacts` dictionary.
4. Validates that required artifacts exist on disk.
5. Records usage data for tracking.

### Sidecar Rules

- The coder writes `meta.json` after completing its work.
- The runner does not write `meta.json` before invocation.
- The runner does not attempt to recover missing sidecars from disk.
- Missing or malformed `meta.json` results in step failure.
- The sidecar path is deterministic: it is located next to the step's
  primary output artifact.

### Context Key Construction

When artifact values are injected into prompt context, meta sidecar
keys follow a specific construction rule: `_METAJSON` context keys must
not double the suffix. The platform handles this normalization in
`step_runner.py`.

## Notification Integration

The platform provides centralized notification services for workflow
events.

### Service

`notification_manager.py` provides the unified notification interface.
It enriches notification context with workflow identity, step name, job
ID, and result summary.

### Bundle Integration

Bundles may enable notifications per step via the `workflow.toml`
manifest:

```toml
[[step]]
name = "generate_docs"
enable_notifications = true
```

### Configuration

Notification delivery is configured in `~/.ukbe-runner/config.json`:

```json
{
  "notification": {
    "enabled": true,
    "provider": "pushover",
    "step_events": {
      "completed": true,
      "rejected": true,
      "failed": true
    }
  }
}
```

### Low-Level Dispatch

`notifications.py` handles the low-level dispatch to configured
providers. Bundles do not call this module directly; they rely on the
notification manager's automatic integration.

## Backend Sync Protocol

The backend sync protocol enables daemon-mode workflow execution and
backend-coordinated job management.

### Protocol Overview

The daemon (`daemon.py`) communicates with a backend API through the
`backend_client.py` module. The protocol supports:

- **Claim**: The daemon polls for available workflow steps and claims
  one for execution.
- **Heartbeat**: The daemon emits periodic heartbeats keyed by
  `workflow_step_run_id` to signal liveness.
- **Completion**: After step execution, the daemon reports the result
  to the backend.
- **Approval**: For steps requiring human approval, the backend
  coordinates the approval decision.

### Sync Payload

The function `build_job_sync_payload()` constructs the payload sent to
the backend after step completion. The payload includes:

- job identity (workflow name, job ID, step name).
- artifact values (filtered to exclude null/empty artifacts).
- usage data (tokens, duration, coder identity).
- step result (status, remark).

### Step Spec Source

The daemon resolves step specifications from one of three sources,
configured in `~/.ukbe-runner/config.json`:

| Source | Description |
|---|---|
| `backend` | Step specs are provided by the backend API in the claim response. |
| `global` | Step specs are loaded from the global workflow registry. |
| `hybrid` | Backend provides overrides; global provides defaults. |

### Job Sync

The `sync_workflows.py` module handles syncing workflow definitions to
the backend. This ensures the backend has current workflow metadata for
scheduling and routing.

## Action Registration

The platform provides an action registration system for bundles that
define custom action steps.

### Built-In Actions

The platform ships with a set of built-in actions in `actions/`:

- `documentation_validation_core.py` -- shared validation helpers.
- `step_completion.py` -- workflow completion action.
- `validate_system_docs.py` -- system documentation validation.
- `validate_codebase_docs.py` -- codebase documentation validation.
- `sync_system_docs.py` -- system documentation sync.
- `sync_codebase_docs.py` -- codebase documentation sync.
- `scan_repo_codebase.py` -- repository codebase scanning.
- `finalize_bootstrap.py` -- bootstrap finalization.

### Custom Actions

Bundles may define custom actions in their `actions.py` module. The
action function is referenced by name in the `workflow.toml` manifest:

```toml
[[step]]
name = "validate_output"
action = "validate_my_artifacts"
```

The step runner resolves the action function by name from:

1. The bundle's `actions.py` module (if present).
2. The platform's built-in action registry (`actions/__init__.py`).

### Action Contract

An action function receives the step context and returns a result:

```python
def validate_my_artifacts(context: dict) -> dict:
    """Validate bundle-specific artifacts."""
    return {
        "status": "APPROVED",
        "remark": "All artifacts valid.",
        "artifacts": {},
    }
```

The return value follows the same structure as the coder `meta.json`
response, ensuring uniform routing behavior for both prompt-driven and
action-driven steps.
