---
title: "Module Documentation: agent_runner_v2.notification_manager"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/notification_manager.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-notification-manager.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-c66bc6aa / 2026-07-23T20:12:07+08:00"
created: "2026-07-23T20:12:07+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.notification_manager

## 1. Module Overview

### 1.1 Purpose

notification_manager.py - Centralized notification management for all execution modes.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `notifications` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### should_send_notifications()

**Signature**: `should_send_notifications()`

**Purpose**: Check if notifications are enabled globally.

**Returns**: `bool`

---

#### send_workflow_notification()

**Signature**: `send_workflow_notification(status: str, context: dict[str, Any])`

**Purpose**: Send workflow-level notification (COMPLETED, FAILED, WAITING_FOR_HUMAN_INTERVENTION).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `status` | `str` | -- | One of COMPLETED, FAILED, WAITING_FOR_HUMAN_INTERVENTION |
| `context` | `dict[str, Any]` | -- | Job state dict or relevant context |

**Returns**: `bool`

---

#### send_step_notification()

**Signature**: `send_step_notification(status: str, context: dict[str, Any], step: str, step_cfg: dict[str, Any])`

**Purpose**: Send step-level notification (STEP_COMPLETED, STEP_FAILED, STEP_REJECTED).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `status` | `str` | -- | One of STEP_COMPLETED, STEP_FAILED, STEP_REJECTED |
| `context` | `dict[str, Any]` | -- | Job state dict |
| `step` | `str` | -- | Step name |
| `step_cfg` | `dict[str, Any]` | -- | Step configuration dict (to check enable_notifications) |

**Returns**: `bool`

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
| 2026-07-23 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
