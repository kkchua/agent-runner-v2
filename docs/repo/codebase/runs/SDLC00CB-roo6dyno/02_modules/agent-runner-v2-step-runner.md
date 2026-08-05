---
title: "Module Documentation: agent_runner_v2.step_runner"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/step_runner.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-step-runner.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-roo6dyno / 2026-08-05T23:43:32+08:00"
created: "2026-08-05T23:43:32+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.step_runner

## 1. Module Overview

### 1.1 Purpose

step_runner.py -- Core step execution contract for agent_runner_v2.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `hashlib` | stdlib module | imported dependency |
| `importlib.util` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |
| `shutil` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `tempfile` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `artifact_paths` | external module | repository dependency |
| `bundle_governance` | external module | repository dependency |
| `coder_adapters` | external module | repository dependency |
| `constants` | external module | repository dependency |
| `doc_paths` | external module | repository dependency |
| `documentation_guardrails` | external module | repository dependency |
| `exceptions` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### StepResult

**Decorators**: `@dataclass`

**Purpose**: Result of a step execution (run_step or run_action).


### 2.2 Functions

#### run_step()

**Signature**: `run_step(*, group_name: str, group_cfg: dict, state: dict, step: str, step_cfg: dict, coder: str, coder_config: dict | None, prompt_text: str, checksum: str, step_dir: Path, project_root: Path, context: dict[str, str])`

**Purpose**: Invoke coder, read meta.json contract, validate artifacts, enrich sidecar.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | -- |
| `group_cfg` | `dict` | -- | -- |
| `state` | `dict` | -- | -- |
| `step` | `str` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `coder` | `str` | -- | -- |
| `coder_config` | `dict | None` | -- | -- |
| `prompt_text` | `str` | -- | -- |
| `checksum` | `str` | -- | -- |
| `step_dir` | `Path` | -- | -- |
| `project_root` | `Path` | -- | -- |
| `context` | `dict[str, str]` | -- | -- |

**Returns**: `StepResult`

**Raises**:

- `CoderInvocationError` -- coder process failed (caller routes to failure)
- `MetaJsonMissingError` -- coder did not write meta.json (hard failure)
- `MetaJsonInvalidError` -- meta.json present but schema invalid (hard failure)
- `ArtifactMissingError` -- meta.json references paths that don't exist on disk

---

#### run_action()

**Signature**: `run_action(*, action_name: str, state: dict, step: str, step_cfg: dict, step_dir: Path, project_root: Path, context: dict[str, str])`

**Purpose**: Execute a runner action (non-coder step).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `action_name` | `str` | -- | -- |
| `state` | `dict` | -- | -- |
| `step` | `str` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `step_dir` | `Path` | -- | -- |
| `project_root` | `Path` | -- | -- |
| `context` | `dict[str, str]` | -- | -- |

**Returns**: `StepResult`

**Raises**:

- `Exception` -- action-specific failures (caller routes to failure).

---

#### enrich_sidecar()

**Signature**: `enrich_sidecar(*, meta_path: Path, step: str, coder_used: str, invoked_at: str, finished_at: str, prompt_checksum: str, project_root: Path, allowed_write_paths: list[str], changed_paths: list[str])`

**Purpose**: Atomically append runner_data section to existing meta.json.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `meta_path` | `Path` | -- | -- |
| `step` | `str` | -- | -- |
| `coder_used` | `str` | -- | -- |
| `invoked_at` | `str` | -- | -- |
| `finished_at` | `str` | -- | -- |
| `prompt_checksum` | `str` | -- | -- |
| `project_root` | `Path` | -- | -- |
| `allowed_write_paths` | `list[str]` | -- | -- |
| `changed_paths` | `list[str]` | -- | -- |

**Returns**: `None`

---

#### build_context()

**Signature**: `build_context(state: dict, *, step: str = '', step_cfg: dict | None = None, project_root: Path | None = None)`

**Purpose**: Build the full context dict for prompt rendering.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict` | -- | -- |
| `step` | `str` | `''` | -- |
| `step_cfg` | `dict | None` | `None` | -- |
| `project_root` | `Path | None` | `None` | -- |

**Returns**: `dict[str, str]`

---

#### render_prompt()

**Signature**: `render_prompt(template_text: str, context: dict[str, str], step_cfg: dict | None = None)`

**Purpose**: Render a prompt template by substituting context variables.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_text` | `str` | -- | The prompt template with {KEY} placeholders. |
| `context` | `dict[str, str]` | -- | Dict mapping placeholder keys to values. |
| `step_cfg` | `dict | None` | `None` | Optional step configuration for sidecar injection. |

**Returns**: `str`

---

#### prompt_checksum()

**Signature**: `prompt_checksum(prompt_text: str)`

**Purpose**: Compute SHA-256 checksum of prompt text for integrity verification.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `prompt_text` | `str` | -- | The prompt text to hash. |

**Returns**: `str`

---

#### resolve_prompt_path()

**Signature**: `resolve_prompt_path(*, step_cfg: dict, coder: str, model_id: str | None = None)`

**Purpose**: Resolve prompt file path with three-level fallback.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `step_cfg` | `dict` | -- | -- |
| `coder` | `str` | -- | -- |
| `model_id` | `str | None` | `None` | -- |

**Returns**: `Path`

---


### 2.3 Constants / Configuration

No public constants.


## 3. Error Handling

| Exception | When | Raised By |
|-----------|------|----------|
| `ArtifactMissingError` | meta.json references paths that don't exist on disk | `run_step` |
| `CoderInvocationError` | coder process failed (caller routes to failure) | `run_step` |
| `Exception` | action-specific failures (caller routes to failure). | `run_action` |
| `MetaJsonInvalidError` | meta.json present but schema invalid (hard failure) | `run_step` |
| `MetaJsonMissingError` | coder did not write meta.json (hard failure) | `run_step` |


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| (none) | No test references found |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-08-05 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
