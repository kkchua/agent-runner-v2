---
title: "Module Documentation: agent_runner_v2.transition_runtime"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/transition_runtime.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/02_modules/agent-runner-v2-transition-runtime.md"
last_verified_by_change: "00_repo_master_docs_bootstrap_v1 / 00RMD-20260716-5ee28fa5 / 2026-07-16T22:09:16+08:00"
created: "2026-07-16T22:09:16+08:00"
owner: "00_repo_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.transition_runtime

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

#### mark_review_started()

**Signature**: `mark_review_started(*, state: dict[str, Any], step: str, step_cfg: dict[str, Any], coder_used: str, default_review_state: Callable[, dict[str, Any]])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `step_cfg` | `dict[str, Any]` | — | — |
| `coder_used` | `str` | — | — |
| `default_review_state` | `Callable[, dict[str, Any]]` | — | — |

**Returns**: `None`

---

#### mark_review_waiting_for_human()

**Signature**: `mark_review_waiting_for_human(*, state: dict[str, Any], step: str, coder_used: str, default_review_state: Callable[, dict[str, Any]], now_iso: Callable[, str], set_job_status: Callable[, None])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `coder_used` | `str` | — | — |
| `default_review_state` | `Callable[, dict[str, Any]]` | — | — |
| `now_iso` | `Callable[, str]` | — | — |
| `set_job_status` | `Callable[, None]` | — | — |

**Returns**: `tuple[dict[str, Any], int]`

---

#### mark_task_exec_success()

**Signature**: `mark_task_exec_success(*, state: dict[str, Any], step: str, set_job_status: Callable[, None])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `set_job_status` | `Callable[, None]` | — | — |

**Returns**: `tuple[dict[str, Any], int]`

---

#### advance_to_next_step()

**Signature**: `advance_to_next_step(*, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any] | None, set_job_status: Callable[, None], get_next_step_skipping_refine_replan: Callable[, str | None], on_completed: Callable[, None])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `step_cfg` | `dict[str, Any] | None` | — | — |
| `set_job_status` | `Callable[, None]` | — | — |
| `get_next_step_skipping_refine_replan` | `Callable[, str | None]` | — | — |
| `on_completed` | `Callable[, None]` | — | — |

**Returns**: `tuple[dict[str, Any], int]`

---

#### complete_recovery_step()

**Signature**: `complete_recovery_step(*, state: dict[str, Any], step: str, target_key: str, artifacts: dict[str, Any], pre_checksum: str | None, no_op_failure_code: str, no_op_failure_reason: str, history_key: str, history_result_field: str, history_time_field: str, next_step: str, project_root: Path, now_iso: Callable[, str], set_last_failure: Callable[Ellipsis, None], append_failure_history: Callable[Ellipsis, None], set_job_status: Callable[, None], checksum_file: Callable[, str], reset_replan_context: bool)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `target_key` | `str` | — | — |
| `artifacts` | `dict[str, Any]` | — | — |
| `pre_checksum` | `str | None` | — | — |
| `no_op_failure_code` | `str` | — | — |
| `no_op_failure_reason` | `str` | — | — |
| `history_key` | `str` | — | — |
| `history_result_field` | `str` | — | — |
| `history_time_field` | `str` | — | — |
| `next_step` | `str` | — | — |
| `project_root` | `Path` | — | — |
| `now_iso` | `Callable[, str]` | — | — |
| `set_last_failure` | `Callable[Ellipsis, None]` | — | — |
| `append_failure_history` | `Callable[Ellipsis, None]` | — | — |
| `set_job_status` | `Callable[, None]` | — | — |
| `checksum_file` | `Callable[, str]` | — | — |
| `reset_replan_context` | `bool` | — | — |

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
| 2026-07-16 | Initial baseline generated from repository scan | 00_repo_master_docs_bootstrap_v1 |
