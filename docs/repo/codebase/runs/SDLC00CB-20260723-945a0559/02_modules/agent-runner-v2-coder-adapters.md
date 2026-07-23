---
title: "Module Documentation: agent_runner_v2.coder_adapters"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/coder_adapters.py"
module_area: "coder"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-coder-adapters.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-945a0559 / 2026-07-23T19:30:10+08:00"
created: "2026-07-23T19:30:10+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.coder_adapters

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `coder` area and is documented as `full`.

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

**Purpose**: Public class

#### UsageData

**Decorators**: `@dataclass`

**Purpose**: Public class

#### InvocationManifest

**Decorators**: `@dataclass`

**Purpose**: Public class

#### InvocationResult

**Decorators**: `@dataclass`

**Purpose**: Public class


### 2.2 Functions

#### dataclass_dict()

**Signature**: `dataclass_dict(value: UsageData | InvocationManifest)`

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

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `coder` | `str` | -- | -- |
| `step` | `str` | -- | -- |
| `prompt_text` | `str` | -- | -- |
| `cwd` | `Path` | -- | -- |
| `prompt_checksum` | `str` | -- | -- |
| `now_iso_fn` | -- | -- | -- |
| `coder_config` | `dict[str, Any] | None` | `None` | -- |
| `sidecar_path` | `Path | None` | `None` | -- |
| `timeout_seconds_override` | `int | None` | `None` | -- |

**Returns**: `InvocationResult`

---

#### merge_usage()

**Signature**: `merge_usage(target: dict[str, Any], source: dict[str, Any])`

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

No documented exceptions.


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| (none) | No test references found |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-23 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
