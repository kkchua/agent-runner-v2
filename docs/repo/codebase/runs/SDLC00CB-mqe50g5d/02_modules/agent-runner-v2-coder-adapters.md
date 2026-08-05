---
title: "Module Documentation: agent_runner_v2.coder_adapters"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/coder_adapters.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-coder-adapters.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-mqe50g5d / 2026-08-06T05:49:37+08:00"
created: "2026-08-06T05:49:37+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.coder_adapters

## 1. Module Overview

### 1.1 Purpose

Coder invocation adapters for agent_runner_v2.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `shutil` | stdlib module | imported dependency |
| `subprocess` | stdlib module | imported dependency |
| `tempfile` | stdlib module | imported dependency |
| `threading` | stdlib module | imported dependency |
| `time` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `uuid` | stdlib module | imported dependency |
| `coder_registry` | external module | repository dependency |
| `runner_logger` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### CoderInvocationError

**Inherits from**: `Exception`

**Decorators**: `@dataclass`

**Purpose**: Exception raised when a coder subprocess fails.

#### UsageData

**Decorators**: `@dataclass`

**Purpose**: Token usage and cost metrics from a coder invocation.

#### InvocationManifest

**Decorators**: `@dataclass`

**Purpose**: Metadata record for a single coder invocation.

#### InvocationResult

**Decorators**: `@dataclass`

**Purpose**: Complete result from invoke_coder() including output, usage, and manifest.


### 2.2 Functions

#### dataclass_dict()

**Signature**: `dataclass_dict(value: UsageData | InvocationManifest)`

**Purpose**: Convert a dataclass instance to a dictionary for JSON serialization.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `UsageData | InvocationManifest` | -- | -- |

**Returns**: `dict[str, Any]`

---

#### abort_active_coder_processes()

**Signature**: `abort_active_coder_processes(*, reason: str = 'interrupt')`

**Purpose**: Terminate all currently tracked coder process trees.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `reason` | `str` | `'interrupt'` | -- |

**Returns**: `int`

---

#### invoke_coder()

**Signature**: `invoke_coder(*, coder: str, step: str, prompt_text: str, cwd: Path, prompt_checksum: str, now_iso_fn, coder_config: dict[str, Any] | None = None, sidecar_path: Path | None = None, timeout_seconds_override: int | None = None)`

**Purpose**: Invoke a coder process with the given prompt and return the result.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `coder` | `str` | -- | Coder backend name (qwen, claude, codex, opencode, or a custom CLI). |
| `step` | `str` | -- | Step name for logging and manifest. |
| `prompt_text` | `str` | -- | Full prompt text to send to the coder. |
| `cwd` | `Path` | -- | Working directory for the coder process. |
| `prompt_checksum` | `str` | -- | SHA-256 checksum of the prompt for audit. |
| `now_iso_fn` | -- | -- | Function returning current ISO timestamp. |
| `coder_config` | `dict[str, Any] | None` | `None` | Resolved coder configuration (model, connection, auth). |
| `sidecar_path` | `Path | None` | `None` | Path to meta.json for early-exit polling. |
| `timeout_seconds_override` | `int | None` | `None` | Override timeout for this invocation. |

**Returns**: `InvocationResult`

**Raises**:

- `CoderInvocationError` -- If the coder process fails or times out.

---

#### merge_usage()

**Signature**: `merge_usage(target: dict[str, Any], source: dict[str, Any])`

**Purpose**: Merge usage metrics from source into target using canonical aliases.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `target` | `dict[str, Any]` | -- | -- |
| `source` | `dict[str, Any]` | -- | -- |

**Returns**: `None`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `DEFAULT_CODER_TIMEOUT_SECONDS` | module configuration |
| `SIDECAR_POLL_INTERVAL_SECONDS` | module configuration |
| `SIDECAR_SETTLE_DELAY_SECONDS` | module configuration |
| `DEFAULT_SIDECAR_POST_COMPLETE_GRACE_SECONDS` | module configuration |
| `_ACTIVE_CODER_PROCS_LOCK` | module configuration |


## 3. Error Handling

| Exception | When | Raised By |
|-----------|------|----------|
| `CoderInvocationError` | If the coder process fails or times out. | `invoke_coder` |


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| (none) | No test references found |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-08-06 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
