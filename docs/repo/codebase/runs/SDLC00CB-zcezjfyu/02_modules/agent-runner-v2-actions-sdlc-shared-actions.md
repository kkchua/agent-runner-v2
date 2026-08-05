---
title: "Module Documentation: agent_runner_v2.actions.sdlc_shared_actions"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/actions/sdlc_shared_actions.py"
module_area: "actions"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-actions-sdlc-shared-actions.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-zcezjfyu / 2026-08-05T13:02:54+08:00"
created: "2026-08-05T13:02:54+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.actions.sdlc_shared_actions

## 1. Module Overview

### 1.1 Purpose

sdlc_shared_actions.py -- Shared actions for AI-Driven SDLC workflows.

### 1.2 Responsibility

This module belongs to the `actions` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |
| `shutil` | stdlib module | imported dependency |
| `subprocess` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `agent_runner_v2.action_result` | internal module | repository dependency |
| `agent_runner_v2.runtime_context` | internal module | repository dependency |
| `agent_runner_v2.workflow_packages.actions` | internal module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### promote_artifact()

**Decorators**: `@action`

**Signature**: `promote_artifact(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Purpose**: Promote a single artifact by changing its lifecycle_status to approved.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `project_root` | `Path` | -- | -- |

**Returns**: `ActionResult`

---

#### promote_to_requirement()

**Decorators**: `@action`

**Signature**: `promote_to_requirement(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Purpose**: Promote PRE-REQ to REQ by creating a new approved file.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `project_root` | `Path` | -- | -- |

**Returns**: `ActionResult`

---

#### promote_all()

**Decorators**: `@action`

**Signature**: `promote_all(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Purpose**: Promote multiple artifacts to approved status.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `project_root` | `Path` | -- | -- |

**Returns**: `ActionResult`

---

#### aggregate_executions()

**Decorators**: `@action`

**Signature**: `aggregate_executions(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Purpose**: Aggregate all EXEC documents for an initiative.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `project_root` | `Path` | -- | -- |

**Returns**: `ActionResult`

---

#### create_backup()

**Decorators**: `@action`

**Signature**: `create_backup(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Purpose**: Create a backup of codebase documentation before sync.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `project_root` | `Path` | -- | -- |

**Returns**: `ActionResult`

---

#### generate_sync_log()

**Decorators**: `@action`

**Signature**: `generate_sync_log(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Purpose**: Generate a sync log documenting changes made during codebase sync.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `project_root` | `Path` | -- | -- |

**Returns**: `ActionResult`

---

#### commit_changes()

**Decorators**: `@action`

**Signature**: `commit_changes(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

**Purpose**: Commit codebase documentation changes to git.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `context` | `dict[str, str]` | -- | -- |
| `state` | `dict` | -- | -- |
| `step_cfg` | `dict` | -- | -- |
| `project_root` | `Path` | -- | -- |

**Returns**: `ActionResult`

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
