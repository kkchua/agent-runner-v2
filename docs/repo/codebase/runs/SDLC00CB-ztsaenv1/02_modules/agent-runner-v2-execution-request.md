---
title: "Module Documentation: agent_runner_v2.execution_request"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/execution_request.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-execution-request.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-ztsaenv1 / 2026-08-05T15:42:22+08:00"
created: "2026-08-05T15:42:22+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.execution_request

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

#### ExecutionRequest

**Decorators**: `@dataclass`

**Purpose**: Base execution request for running a workflow step.

**Methods**:

- `from_dict(payload: dict[str, Any])` -> `'ExecutionRequest'` -- method

#### WorkerRequest

**Decorators**: `@dataclass`

**Purpose**: Machine-mode execution request from daemon/backend claiming.

**Methods**:

- `from_dict(payload: dict[str, Any])` -> `'WorkerRequest'` -- Parse and validate worker request from JSON payload.
- `from_file(path: str | Path)` -> `'WorkerRequest'` -- Load and validate worker request from JSON file.
- `to_dict()` -> `dict[str, Any]` -- Convert to dictionary for serialization.


### 2.2 Functions

No public functions.


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
