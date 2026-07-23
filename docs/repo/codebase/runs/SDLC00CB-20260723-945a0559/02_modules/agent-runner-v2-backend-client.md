---
title: "Module Documentation: agent_runner_v2.backend_client"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/backend_client.py"
module_area: "backend"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-backend-client.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-945a0559 / 2026-07-23T19:30:10+08:00"
created: "2026-07-23T19:30:10+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.backend_client

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `backend` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `urllib` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

#### BackendClient

**Decorators**: `@dataclass`

**Purpose**: Public class

**Methods**:

- `submit_run(*, workflow_name: str, initiative_id: str | None = None, target_worker_id: str | None = None, assigned_provider: str | None = None, coder_override: str | None = None, project_root: str | None = None, target_project_root: str | None = None, workspace_path: str | None = None, repo_url: str | None = None, repo_ref: str | None = None, worker_label: str = 'live', env_overrides: dict[str, Any] | None = None, input_payload: dict[str, Any] | None = None, context_payload: dict[str, Any] | None = None)` -> `dict[str, Any]` -- method
- `approve_run(*, run_id: str, action: str = 'approve', feedback: str | None = None, outcome: str | None = None)` -> `dict[str, Any]` -- method
- `get_run(*, run_id: str)` -> `dict[str, Any]` -- method
- `list_runs(*, repo_path: str | None = None, workflow_name: str | None = None, status_group: str | None = None, worker_id: str | None = None)` -> `dict[str, Any]` -- method
- `stop_run(*, run_id: str, reason: str | None = None, mode: str = 'after_current_step')` -> `dict[str, Any]` -- method
- `reset_run_step(*, run_id: str, step_name: str)` -> `dict[str, Any]` -- method
- `register_worker(*, worker_id: str, host_name: str | None = None, capabilities: dict[str, Any] | None = None, worker_label: str = 'live')` -> `dict[str, Any]` -- method
- `heartbeat(*, worker_id: str, status: str | None = None, current_step_run_id: str | None = None, workflow_run_id: str | None = None, workflow_step_run_id: str | None = None, run_code: str | None = None, pid: int | None = None, state: str | None = None, log_file: str | None = None, watchdog_reason: str | None = None, exit_code: int | None = None)` -> `dict[str, Any]` -- method
- `claim_step(*, worker_id: str)` -> `dict[str, Any]` -- method
- `complete_step_run(*, step_run_id: str, payload: dict[str, Any])` -> `dict[str, Any]` -- method
- `sync_job_state(*, step_run_id: str, payload: dict[str, Any])` -> `dict[str, Any]` -- method
- `create_artifact(*, run_id: str, payload: dict[str, Any])` -> `dict[str, Any]` -- method
- `create_event(*, run_id: str, payload: dict[str, Any])` -> `dict[str, Any]` -- method
- `cleanup_execution(*, workflow_name: str, dry_run: bool = False)` -> `dict[str, Any]` -- method


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
