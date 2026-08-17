---
title: "Module Documentation: agent_runner_v2.daemon_v2"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/daemon_v2.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-daemon-v2.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.daemon_v2

## 1. Module Overview

### 1.1 Purpose

V2 worker daemon supervisor -- self-contained, no V1 imports.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `logging.handlers` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `signal` | stdlib module | imported dependency |
| `subprocess` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `time` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `config_loader` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |
| `v2` | external module | repository dependency |
| `v2.backend_client` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### ChildExecution

**Decorators**: `@dataclass`

**Purpose**: Tracks state for a spawned child process executing a workflow step.

#### SupervisorConfig

**Decorators**: `@dataclass`

**Purpose**: Configuration for the daemon supervisor.

#### DaemonLogger

**Purpose**: JSONL logger for daemon events using standard library rotation.

**Methods**:

- `log(level: str, event: str, *, message: str = '', child: ChildExecution | None = None, details: dict[str, Any] | None = None)` -> `None` -- method


### 2.2 Functions

#### run_supervisor()

**Signature**: `run_supervisor(*, config: SupervisorConfig, v2_url: str)`

**Purpose**: V2 supervisor -- claim -> sync -> spawn -> report loop.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `config` | `SupervisorConfig` | -- | -- |
| `v2_url` | `str` | -- | -- |

**Returns**: `int`

---

#### main()

**Signature**: `main(argv: list[str] | None = None)`

**Purpose**: V2 daemon CLI entry point.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `argv` | `list[str] | None` | `None` | -- |

**Returns**: `int`

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
| 2026-08-17 | Initial baseline generated from repository scan | sdlc_00_codebase_scaffold_v1 |
