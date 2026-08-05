---
title: "Module Documentation: agent_runner_v2.engine_commands"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/engine_commands.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-engine-commands.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-bgmxg5vi / 2026-08-06T07:04:04+08:00"
created: "2026-08-06T07:04:04+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.engine_commands

## 1. Module Overview

### 1.1 Purpose

Engine version management for agent_runner_v2.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `argparse` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `shutil` | stdlib module | imported dependency |
| `subprocess` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `tarfile` | stdlib module | imported dependency |
| `tempfile` | stdlib module | imported dependency |
| `urllib.request` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### cmd_snapshot()

**Signature**: `cmd_snapshot(project_root: Path)`

**Purpose**: Snapshot the live package source into repo-local SNAPSHOT version.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `project_root` | `Path` | -- | -- |

**Returns**: `None`

---

#### cmd_install()

**Signature**: `cmd_install(tag: str, github_repo: str, global_install: bool = True, from_path: str | None = None, project_root: Path | None = None)`

**Purpose**: Install engine from a local path or a GitHub tag.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `tag` | `str` | -- | -- |
| `github_repo` | `str` | -- | -- |
| `global_install` | `bool` | `True` | -- |
| `from_path` | `str | None` | `None` | -- |
| `project_root` | `Path | None` | `None` | -- |

**Returns**: `None`

---

#### cmd_use()

**Signature**: `cmd_use(project_root: Path, version: str, local: bool = False, repo_root: str = '')`

**Purpose**: Set the active engine version in config.json.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `project_root` | `Path` | -- | -- |
| `version` | `str` | -- | -- |
| `local` | `bool` | `False` | -- |
| `repo_root` | `str` | `''` | -- |

**Returns**: `None`

---

#### cmd_list()

**Signature**: `cmd_list(project_root: Path)`

**Purpose**: List all installed engine versions (global + repo-local).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `project_root` | `Path` | -- | -- |

**Returns**: `None`

---

#### main()

**Signature**: `main(argv: list[str] | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `argv` | `list[str] | None` | `None` | -- |

**Returns**: `int`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `DEFAULT_GITHUB_REPO` | module configuration |


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
| 2026-08-06 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
