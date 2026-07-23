---
title: "Module Documentation: agent_runner_v2.operator_console.services.backend_service"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/operator_console/services/backend_service.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-operator-console-services-backend-service.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-945a0559 / 2026-07-23T19:30:10+08:00"
created: "2026-07-23T19:30:10+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.operator_console.services.backend_service

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `backend_client` | external module | repository dependency |
| `models` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### BackendRunService

**Purpose**: Public class

**Methods**:

- `list_active_runs(*, repo_path: str, workflow_name: str | None = None)` -> `list[ActiveRunSummary]` -- method
- `stop_run(*, run_id: str, reason: str = '')` -> `dict[str, Any]` -- method
- `approve_run(*, run_id: str, reject: bool = False, feedback: str = '')` -> `dict[str, Any]` -- method
- `get_run_detail(*, run_id: str)` -> `dict[str, Any]` -- method
- `reset_run_step(*, run_id: str, step_name: str)` -> `dict[str, Any]` -- method


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
| 2026-07-23 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
