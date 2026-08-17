---
title: "Module Documentation: agent_runner_v2.qwenpaw_client"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/qwenpaw_client.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-qwenpaw-client.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.qwenpaw_client

## 1. Module Overview

### 1.1 Purpose

qwenpaw_client.py -- Client for interacting with the QwenPaw Agent REST API 

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `urllib.error` | stdlib module | imported dependency |
| `urllib.request` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### notify_qwenpaw_agent()

**Signature**: `notify_qwenpaw_agent(message: str, session_id: str | None = None, agent_id: str | None = None, base_url: str | None = None, user_id: str = 'agent-runner-v2', timeout: int = 10)`

**Purpose**: Sends a message to the QwenPaw Console.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `message` | `str` | -- | -- |
| `session_id` | `str | None` | `None` | -- |
| `agent_id` | `str | None` | `None` | -- |
| `base_url` | `str | None` | `None` | -- |
| `user_id` | `str` | `'agent-runner-v2'` | -- |
| `timeout` | `int` | `10` | -- |

**Returns**: `bool`

---

#### notify_telegram()

**Signature**: `notify_telegram(message: str, bot_token: str | None = None, chat_id: str | None = None, timeout: int = 10)`

**Purpose**: Sends a message directly to Telegram via the Official Bot API.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `message` | `str` | -- | -- |
| `bot_token` | `str | None` | `None` | -- |
| `chat_id` | `str | None` | `None` | -- |
| `timeout` | `int` | `10` | -- |

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
| 2026-08-17 | Initial baseline generated from repository scan | sdlc_00_codebase_scaffold_v1 |
