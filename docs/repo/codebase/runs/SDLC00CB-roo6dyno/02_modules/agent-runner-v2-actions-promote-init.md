---
title: "Module Documentation: agent_runner_v2.actions.promote_init"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/actions/promote_init.py"
module_area: "actions"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-actions-promote-init.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-roo6dyno / 2026-08-05T23:43:32+08:00"
created: "2026-08-05T23:43:32+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.actions.promote_init

## 1. Module Overview

### 1.1 Purpose

actions/promote_init.py -- Promote a reviewed PRE_INIT_FILE to an official INIT_FILE.

### 1.2 Responsibility

This module belongs to the `actions` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |
| `action_result` | external module | repository dependency |
| `constants` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### promote_init()

**Signature**: `promote_init(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path)`

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

| Name | Purpose |
|------|--------|
| `_INIT_ID_RE` | module configuration |
| `_STATUS_RE` | module configuration |


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
