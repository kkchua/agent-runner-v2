---
title: "Module Documentation: agent_runner_v2.hooks_protocols"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/hooks_protocols.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-hooks-protocols.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-roo6dyno / 2026-08-05T23:43:32+08:00"
created: "2026-08-05T23:43:32+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.hooks_protocols

## 1. Module Overview

### 1.1 Purpose

Protocol definitions for hook interfaces to enable type-safe dependency injection.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

#### ArtifactHooks

**Inherits from**: `Protocol`

**Decorators**: `@runtime_checkable`

**Purpose**: Protocol for artifact-related operations.

**Methods**:

- `missing_artifacts(keys: list[str], state: dict[str, Any])` -> `list[str]` -- Return list of artifact keys that are missing from state.

#### WorkflowHooks

**Inherits from**: `Protocol`

**Decorators**: `@runtime_checkable`

**Purpose**: Protocol for workflow configuration operations.

**Methods**:

- `build_group_cfg_from_execution_spec(spec: dict[str, Any], template_group: str, step_name: str)` -> `tuple[dict[str, Any], dict[str, Any]]` -- Build group and step config from execution spec.

#### CoderHooks

**Inherits from**: `Protocol`

**Decorators**: `@runtime_checkable`

**Purpose**: Protocol for coder resolution operations.

**Methods**:

- `resolve_step_coder(*, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], cli_coder: str | None)` -> `tuple[str, dict[str, Any]] | tuple[str, str | None, str | None, dict[str, Any]]` -- Resolve the coder for a step.

#### StepExecutionHooks

**Inherits from**: `Protocol`

**Decorators**: `@runtime_checkable`

**Purpose**: Combined protocol for step execution operations.

**Methods**:

- `missing_artifacts(keys: list[str], state: dict[str, Any])` -> `list[str]` -- Return list of artifact keys that are missing from state.
- `check_preflight_artifact_status(*, step_cfg: dict[str, Any], state: dict[str, Any])` -> `None` -- Check preflight artifact status.
- `ensure_planning_task_queue_integrity(state: dict[str, Any], step: str)` -> `None` -- Ensure planning task queue integrity.
- `ensure_execution_task_binding_integrity(state: dict[str, Any], step: str)` -> `None` -- Ensure execution task binding integrity.
- `make_step_dir(group_cfg: dict[str, Any], state: dict[str, Any], step: str)` -> `Path` -- Create and return step directory.
- `build_context(state: dict[str, Any], *, step: str, step_cfg: dict[str, Any], project_root: Path)` -> `dict[str, str]` -- Build context dictionary for prompt rendering.
- `resolve_prompt_path(*, step_cfg: dict[str, Any], coder: str, model_id: str | None)` -> `Path` -- Resolve prompt file path.
- `render_prompt(template: str, context: dict[str, str], *, step_cfg: dict[str, Any])` -> `str` -- Render prompt template with context.
- `prompt_checksum(text: str)` -> `str` -- Calculate checksum for prompt text.
- `run_action(*, action_name: str, state: dict[str, Any], step: str, step_cfg: dict[str, Any], step_dir: Path, project_root: Path, context: dict[str, str])` -> `Any` -- Run an action.
- `run_step(*, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], coder: str, coder_config: dict[str, Any] | None, prompt_text: str, checksum: str, step_dir: Path, project_root: Path, context: dict[str, str])` -> `Any` -- Run a step with coder.
- `resolve_step_coder(*, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], cli_coder: str | None)` -> `tuple[str, dict[str, Any]] | tuple[str, str | None, str | None, dict[str, Any]]` -- Resolve the coder for a step.
- `build_group_cfg_from_execution_spec(spec: dict[str, Any], template_group: str, step_name: str)` -> `tuple[dict[str, Any], dict[str, Any]]` -- Build group and step config from execution spec.
- `prepare_step_execution(*, template_group: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], project_root: Path, workflow_key_override: str, cli_coder: str | None, hooks: Any)` -> `Any` -- Prepare a step for execution.

#### ExecutionHooks

**Inherits from**: `Protocol`

**Decorators**: `@runtime_checkable`

**Purpose**: Protocol for execution-related operations.

**Methods**:

- `invoke_prepared_step(prepared: Any)` -> `Any` -- Invoke a prepared step.

#### JobHooks

**Inherits from**: `Protocol`

**Decorators**: `@runtime_checkable`

**Purpose**: Protocol for job state operations.

**Methods**:

- `load_job(job_id: str, project_root: Path)` -> `dict[str, Any]` -- Load job state.
- `save_job(job_id: str, state: dict[str, Any], project_root: Path)` -> `None` -- Save job state.

#### StepGuardrails

**Inherits from**: `Protocol`

**Decorators**: `@runtime_checkable`

**Purpose**: Protocol for step guardrail validation hooks.

**Methods**:

- `pre_check(*, step: str, step_cfg: dict[str, Any], state: dict[str, Any], prepared: Any)` -> `tuple[bool, str | None, str | None]` -- Validate inputs before step execution.
- `post_check(*, step: str, step_cfg: dict[str, Any], state: dict[str, Any], step_result: Any)` -> `tuple[bool, str | None, str | None]` -- Validate outputs after step execution.

#### BundleHooks

**Inherits from**: `Protocol`

**Decorators**: `@runtime_checkable`

**Purpose**: Protocol for bundle loading operations.

**Methods**:

- `load_project_config(workspace_root: Path)` -> `dict[str, Any]` -- Load project configuration.
- `load_workflow_module(workspace_root: Path, bundle_name: str, *, config: dict[str, Any] | None = None)` -> `Any` -- Load workflow module.
- `resolve_workflow_root(workspace_root: Path, bundle_name: str, *, config: dict[str, Any] | None = None)` -> `Path` -- Resolve workflow root path.


### 2.2 Functions

No public functions.


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
