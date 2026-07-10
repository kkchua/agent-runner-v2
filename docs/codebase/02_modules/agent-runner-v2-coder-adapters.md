---
title: "Module Documentation: agent_runner_v2.coder_adapters"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/coder_adapters.py"
module_area: "coder"
documentation_mode: "full"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-coder-adapters.md"
last_verified_by_change: "00_master_docs_bootstrap_v2 / 00DOC-20260710-0098bf53 / 2026-07-10T19:43:53+08:00"
created: "2026-07-10T19:43:53+08:00"
owner: "00_master_docs_bootstrap_v2"
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
| `time` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `uuid` | stdlib module | imported dependency |
| `model_config` | external module | repository dependency |
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
| `value` | `UsageData | InvocationManifest` | — | — |

**Returns**: `dict[str, Any]`

---

#### invoke_coder()

**Signature**: `invoke_coder(*, coder: str, step: str, prompt_text: str, cwd: Path, schema_path: Path, prompt_checksum: str, now_iso_fn, coder_config: dict[str, Any] | None = None, sidecar_path: Path | None = None, timeout_seconds_override: int | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `coder` | `str` | — | — |
| `step` | `str` | — | — |
| `prompt_text` | `str` | — | — |
| `cwd` | `Path` | — | — |
| `schema_path` | `Path` | — | — |
| `prompt_checksum` | `str` | — | — |
| `now_iso_fn` | — | — | — |
| `coder_config` | `dict[str, Any] | None` | `None` | — |
| `sidecar_path` | `Path | None` | `None` | — |
| `timeout_seconds_override` | `int | None` | `None` | — |

**Returns**: `InvocationResult`

---

#### merge_usage()

**Signature**: `merge_usage(target: dict[str, Any], source: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `target` | `dict[str, Any]` | — | — |
| `source` | `dict[str, Any]` | — | — |

**Returns**: `None`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `DEFAULT_CODER_TIMEOUT_SECONDS` | module configuration |
| `SIDECAR_POLL_INTERVAL_SECONDS` | module configuration |
| `SIDECAR_SETTLE_DELAY_SECONDS` | module configuration |
| `DEFAULT_SIDECAR_POST_COMPLETE_GRACE_SECONDS` | module configuration |


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
| 2026-07-10 | Initial baseline generated from repository scan | 00_master_docs_bootstrap_v2 |
