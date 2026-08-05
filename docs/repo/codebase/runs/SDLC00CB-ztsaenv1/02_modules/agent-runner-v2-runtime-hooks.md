---
title: "Module Documentation: agent_runner_v2.runtime_hooks"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/runtime_hooks.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-runtime-hooks.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-ztsaenv1 / 2026-08-05T15:42:22+08:00"
created: "2026-08-05T15:42:22+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.runtime_hooks

## 1. Module Overview

### 1.1 Purpose

Runtime hooks implementation with lazy module loading.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `importlib.util` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `hooks_protocols` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### RuntimeHooks

**Purpose**: Central hook implementation with lazy module loading.

**Methods**:

- `missing_artifacts(keys: list[str], state: dict[str, Any])` -> `list[str]` -- Return list of artifact keys that are missing from state.
- `build_group_cfg_from_execution_spec(spec: dict[str, Any], template_group: str, step_name: str)` -> `tuple[dict[str, Any], dict[str, Any]]` -- Build group and step config from execution spec.
- `resolve_step_coder(*, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], cli_coder: str | None)` -> `tuple[str, dict[str, Any]] | tuple[str, str | None, str | None, dict[str, Any]]` -- Resolve the coder for a step.
- `prepare_step_execution(*, template_group: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], project_root: Path, workflow_key_override: str = '', cli_coder: str | None = None, hooks: Any = None)` -> `Any` -- Prepare a step for execution.
- `execute_prepared_step(*, prepared: Any, template_group: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], effective_root: Path, hooks: Any = None)` -> `Any` -- Execute a prepared step.
- `invoke_prepared_step(prepared: Any)` -> `Any` -- Invoke a prepared step.
- `load_job(job_id: str, project_root: Path)` -> `dict[str, Any]` -- Load job state.
- `save_job(job_id: str, state: dict[str, Any], project_root: Path)` -> `None` -- Save job state.
- `load_project_config(workspace_root: Path)` -> `dict[str, Any]` -- Load project configuration.
- `load_workflow_module(workspace_root: Path, bundle_name: str, *, config: dict[str, Any] | None = None)` -> `Any` -- Load workflow module.
- `resolve_workflow_root(workspace_root: Path, bundle_name: str, *, config: dict[str, Any] | None = None)` -> `Path` -- Resolve workflow root path.
- `ensure_delivery_folders(target_root: Path)` -> `None` -- Ensure delivery folders exist.
- `load_group(group_name: str, workspace_root: Path | None = None, workflow_root: Path | None = None)` -> `dict[str, Any]` -- Load workflow group configuration.
- `validate_static_reference_files(workspace_root: Path, group_cfg: dict[str, Any] | None = None, template_group: str = '')` -> `None` -- Validate static reference files.

#### ManualHooks

**Purpose**: Hooks implementation for manual mode operations.

**Methods**:

- `missing_artifacts(keys: list[str], state: dict)` -> `list[str]` -- Return list of missing artifact keys.
- `parse_key_value_pairs(values: list[str])` -> `dict[str, str]` -- Parse key=value pairs into dict.
- `step_progress_label(group_cfg: dict, step: str | None)` -> `str` -- Get step progress label.
- `format_job_status_summary(state: dict, group_cfg: dict)` -> `str` -- Format job status summary.
- `clear_last_failure(state: dict)` -> `None` -- Clear last failure from state.
- `default_loop_context()` -> `dict` -- Return default loop context.
- `default_replan_context()` -> `dict` -- Return default replan context.


### 2.2 Functions

#### get_workflow_guardrails()

**Signature**: `get_workflow_guardrails(workflow_name: str)`

**Purpose**: Discover and return guardrail module for a workflow.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `workflow_name` | `str` | -- | Template group name (e.g., "agnes_media_gen_v1"). |

**Returns**: `StepGuardrails | None`

---


### 2.3 Constants / Configuration

No public constants.


## 3. Error Handling

No documented exceptions.


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| (none) | No test references found |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-08-05 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
