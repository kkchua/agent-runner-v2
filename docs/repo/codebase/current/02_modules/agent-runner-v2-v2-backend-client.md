---
title: "Module Documentation: agent_runner_v2.v2.backend_client"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/v2/backend_client.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-v2-backend-client.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.v2.backend_client

## 1. Module Overview

### 1.1 Purpose

V2 Backend API client for the new state-machine backend.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

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

#### V2BackendClient

**Decorators**: `@dataclass`

**Purpose**: HTTP client for the V2 backend API.

**Methods**:

- `register_worker(*, worker_id: str, worker_label: str = 'live', capabilities: dict[str, Any] | None = None)` -> `dict[str, Any]` -- method
- `get_worker(*, worker_id: str)` -> `dict[str, Any]` -- Fetch worker details including status. Returns worker dict or raises if not found.
- `heartbeat(*, worker_id: str, status: str = 'idle', current_run_id: str | None = None, current_step_run_id: str | None = None)` -> `dict[str, Any]` -- method
- `claim_work(*, worker_id: str)` -> `dict[str, Any]` -- Claim next available work. Returns work_type + run/step details.
- `stop_worker(*, worker_id: str)` -> `dict[str, Any]` -- method
- `get_run(*, run_id: str)` -> `dict[str, Any]` -- method
- `list_runs(*, status: str | None = None, worker_id: str | None = None)` -> `dict[str, Any]` -- method
- `request_action(*, run_id: str, action: str, feedback: str | None = None, force: bool = False)` -> `dict[str, Any]` -- method
- `reset_step(*, run_id: str, step_name: str)` -> `dict[str, Any]` -- method
- `report_outcome(*, step_run_id: str, outcome: str, failure_class: str | None = None, artifacts: dict[str, str] | None = None, review: dict[str, Any] | None = None, error_message: str | None = None, usage_summary: dict[str, Any] | None = None, job_dir: str | None = None)` -> `dict[str, Any]` -- Report step outcome -- backend computes next state via state machine.
- `sync_workflow(*, workflow_name: str, definition: dict[str, Any])` -> `dict[str, Any]` -- method


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
| 2026-08-17 | Initial baseline generated from repository scan | sdlc_00_codebase_scaffold_v1 |
