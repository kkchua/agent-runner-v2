---
title: "Module Documentation: agent_runner_v2.cleanup_commands"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/cleanup_commands.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-cleanup-commands.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-ztsaenv1 / 2026-08-05T15:42:22+08:00"
created: "2026-08-05T15:42:22+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.cleanup_commands

## 1. Module Overview

### 1.1 Purpose

Cleanup command for agent_runner_v2 - remove old job history and runtime files.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `argparse` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `shutil` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `time` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `config_loader` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### CleanupSummary

**Decorators**: `@dataclass`

**Purpose**: Summary of cleanup operation for a single target.

**Methods**:

- `to_dict()` -> `dict[str, Any]` -- Convert summary to dictionary for JSON serialization.


### 2.2 Functions

#### cleanup_jobs()

**Signature**: `cleanup_jobs(runner_home: Path, keep_days: int, dry_run: bool)`

**Purpose**: Clean up job folders older than keep_days.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `runner_home` | `Path` | -- | Global runner home path |
| `keep_days` | `int` | -- | Number of days to keep |
| `dry_run` | `bool` | -- | If True, only report what would be deleted |

**Returns**: `CleanupSummary`

---

#### cleanup_runtime()

**Signature**: `cleanup_runtime(runner_home: Path, keep_days: int, dry_run: bool)`

**Purpose**: Clean up runtime worker files/folders older than keep_days.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `runner_home` | `Path` | -- | Global runner home path |
| `keep_days` | `int` | -- | Number of days to keep |
| `dry_run` | `bool` | -- | If True, only report what would be deleted |

**Returns**: `CleanupSummary`

---

#### main()

**Signature**: `main(argv: list[str] | None = None)`

**Purpose**: Main entry point for cleanup command.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `argv` | `list[str] | None` | `None` | Command line arguments |

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
| 2026-08-05 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
