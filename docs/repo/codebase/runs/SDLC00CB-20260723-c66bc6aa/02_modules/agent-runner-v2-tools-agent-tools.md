---
title: "Module Documentation: agent_runner_v2.tools.agent_tools"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/tools/agent_tools.py"
module_area: "tools"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-tools-agent-tools.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-c66bc6aa / 2026-07-23T20:12:07+08:00"
created: "2026-07-23T20:12:07+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.tools.agent_tools

## 1. Module Overview

### 1.1 Purpose

agent_tools.py -- Task coder tool functions for agent-runner steps.

### 1.2 Responsibility

This module belongs to the `tools` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `urllib.request` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### create_todos()

**Signature**: `create_todos(step_id: str, todos: list)`

**Purpose**: Register all todo items for this step. All start as pending.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `step_id` | `str` | -- | -- |
| `todos` | `list` | -- | -- |

**Returns**: `dict`

---

#### mark_process()

**Signature**: `mark_process(step_id: str, todo_index: int, notes: str = '')`

**Purpose**: Mark the todo at 1-based index as processing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `step_id` | `str` | -- | -- |
| `todo_index` | `int` | -- | -- |
| `notes` | `str` | `''` | -- |

**Returns**: `dict`

---

#### mark_complete()

**Signature**: `mark_complete(step_id: str, todo_index: int, notes: str = '')`

**Purpose**: Mark the todo at 1-based index as completed, resolving the original item description.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `step_id` | `str` | -- | -- |
| `todo_index` | `int` | -- | -- |
| `notes` | `str` | `''` | -- |

**Returns**: `dict`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `PROGRESS_FILE` | module configuration |
| `BACKEND_URL` | module configuration |
| `STEP_RUN_ID` | module configuration |


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
