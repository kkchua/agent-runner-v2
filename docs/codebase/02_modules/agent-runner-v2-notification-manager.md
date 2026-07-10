---
title: "Module Documentation: agent_runner_v2.notification_manager"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/notification_manager.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-notification-manager.md"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260710-004 / 2026-07-10T09:40:54+08:00"
created: "2026-07-10T09:40:54+08:00"
owner: "00_master_docs_bootstrap_v1"
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
| `status` | `str` | — | One of COMPLETED, FAILED, WAITING_FOR_HUMAN_INTERVENTION |
| `context` | `dict[str, Any]` | — | Job state dict or relevant context |

**Returns**: `bool`

---

#### send_step_notification()

**Signature**: `send_step_notification(status: str, context: dict[str, Any], step: str, step_cfg: dict[str, Any])`

**Purpose**: Send step-level notification (STEP_COMPLETED, STEP_FAILED).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `status` | `str` | — | One of STEP_COMPLETED, STEP_FAILED |
| `context` | `dict[str, Any]` | — | Job state dict |
| `step` | `str` | — | Step name |
| `step_cfg` | `dict[str, Any]` | — | Step configuration dict (to check enable_notifications) |

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
| 2026-07-10 | Initial baseline generated from repository scan | 00_master_docs_bootstrap_v1 |
