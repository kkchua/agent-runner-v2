---
title: "Module Documentation: agent_runner_v2.recovery_runtime"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/recovery_runtime.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-recovery-runtime.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-d46af7f2 / 2026-07-23T20:54:20+08:00"
created: "2026-07-23T20:54:20+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.recovery_runtime

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `state_defaults` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### handle_recovery_budget_exceeded()

**Signature**: `handle_recovery_budget_exceeded(*, state: dict[str, Any], step: str, reject_counts: dict[str, Any], set_last_failure: Callable[Ellipsis, None], append_failure_history: Callable[Ellipsis, None], set_job_status: Callable[, None])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `step` | `str` | -- | -- |
| `reject_counts` | `dict[str, Any]` | -- | -- |
| `set_last_failure` | `Callable[Ellipsis, None]` | -- | -- |
| `append_failure_history` | `Callable[Ellipsis, None]` | -- | -- |
| `set_job_status` | `Callable[, None]` | -- | -- |

**Returns**: `tuple[dict[str, Any], int]`

---

#### activate_refine_loop()

**Signature**: `activate_refine_loop(*, state: dict[str, Any], step: str, refine_step: str, target_artifact: str, review_file: str | None, iteration: int, now_iso: Callable[, str], clear_last_failure: Callable[, None], set_job_status: Callable[, None])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `step` | `str` | -- | -- |
| `refine_step` | `str` | -- | -- |
| `target_artifact` | `str` | -- | -- |
| `review_file` | `str | None` | -- | -- |
| `iteration` | `int` | -- | -- |
| `now_iso` | `Callable[, str]` | -- | -- |
| `clear_last_failure` | `Callable[, None]` | -- | -- |
| `set_job_status` | `Callable[, None]` | -- | -- |

**Returns**: `tuple[dict[str, Any], int]`

---

#### activate_replan()

**Signature**: `activate_replan(*, state: dict[str, Any], step: str, replan_step: str, target_artifact: str, review_file: str | None, replan_attempt: int, trigger_reason: str, artifacts: dict[str, Any], project_root: Path, checksum_file: Callable[, str], now_iso: Callable[, str], clear_last_failure: Callable[, None], set_job_status: Callable[, None])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `step` | `str` | -- | -- |
| `replan_step` | `str` | -- | -- |
| `target_artifact` | `str` | -- | -- |
| `review_file` | `str | None` | -- | -- |
| `replan_attempt` | `int` | -- | -- |
| `trigger_reason` | `str` | -- | -- |
| `artifacts` | `dict[str, Any]` | -- | -- |
| `project_root` | `Path` | -- | -- |
| `checksum_file` | `Callable[, str]` | -- | -- |
| `now_iso` | `Callable[, str]` | -- | -- |
| `clear_last_failure` | `Callable[, None]` | -- | -- |
| `set_job_status` | `Callable[, None]` | -- | -- |

**Returns**: `tuple[dict[str, Any], int]`

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
