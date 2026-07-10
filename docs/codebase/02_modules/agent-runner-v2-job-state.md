---
title: "Module Documentation: agent_runner_v2.job_state"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/job_state.py"
module_area: "state"
documentation_mode: "full"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-job-state.md"
last_verified_by_change: "00_master_docs_bootstrap_v2 / 00DOC-20260710-0098bf53 / 2026-07-10T19:43:53+08:00"
created: "2026-07-10T19:43:53+08:00"
owner: "00_master_docs_bootstrap_v2"
---

# Module Documentation: agent_runner_v2.job_state

## 1. Module Overview

### 1.1 Purpose

job_state.py — All job.json lifecycle management for agent_runner_v2.

### 1.2 Responsibility

This module belongs to the `state` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `hashlib` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |
| `tempfile` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `doc_paths` | external module | repository dependency |
| `documentation_guardrails` | external module | repository dependency |
| `exceptions` | external module | repository dependency |
| `notification_manager` | external module | repository dependency |
| `notifications` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### now_iso()

**Signature**: `now_iso()`

**Returns**: `str`

---

#### get_job_status()

**Signature**: `get_job_status(state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |

**Returns**: `str`

---

#### set_job_status()

**Signature**: `set_job_status(state: dict[str, Any], value: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `value` | `str` | — | — |

**Returns**: `None`

---

#### ensure_dir()

**Signature**: `ensure_dir(path: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | — | — |

**Returns**: `None`

---

#### resolve_repo_path()

**Signature**: `resolve_repo_path(value: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `str` | — | — |

**Returns**: `Path`

---

#### normalize_repo_relative_path()

**Signature**: `normalize_repo_relative_path(value: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `str` | — | — |

**Returns**: `str`

---

#### group_dir()

**Signature**: `group_dir(group_name: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |

**Returns**: `Path`

---

#### job_dir()

**Signature**: `job_dir(group_name: str, job_id: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |
| `job_id` | `str` | — | — |

**Returns**: `Path`

---

#### job_state_path()

**Signature**: `job_state_path(group_name: str, job_id: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |
| `job_id` | `str` | — | — |

**Returns**: `Path`

---

#### get_step_index()

**Signature**: `get_step_index(group_cfg: dict[str, Any], step: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |

**Returns**: `int`

---

#### make_step_dir()

**Signature**: `make_step_dir(group_cfg: dict[str, Any], state: dict[str, Any], step: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |

**Returns**: `Path`

---

#### load_json()

**Signature**: `load_json(path: Path)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | — | — |

**Returns**: `dict[str, Any]`

---

#### save_json()

**Signature**: `save_json(path: Path, data: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | — | — |
| `data` | `dict[str, Any]` | — | — |

**Returns**: `None`

---

#### save_json_atomic()

**Signature**: `save_json_atomic(path: Path, data: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | — | — |
| `data` | `dict[str, Any]` | — | — |

**Returns**: `None`

---

#### save_text()

**Signature**: `save_text(path: Path, content: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | — | — |
| `content` | `str` | — | — |

**Returns**: `None`

---

#### set_last_failure()

**Signature**: `set_last_failure(*, state: dict[str, Any], failure_class: str, failure_code: str, failure_reason: str, failure_source: str, step: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `failure_class` | `str` | — | — |
| `failure_code` | `str` | — | — |
| `failure_reason` | `str` | — | — |
| `failure_source` | `str` | — | — |
| `step` | `str` | — | — |

**Returns**: `None`

---

#### clear_last_failure()

**Signature**: `clear_last_failure(state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |

**Returns**: `None`

---

#### append_failure_history()

**Signature**: `append_failure_history(*, state: dict[str, Any], step: str, failure_class: str, failure_code: str, failure_source: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `failure_class` | `str` | — | — |
| `failure_code` | `str` | — | — |
| `failure_source` | `str` | — | — |

**Returns**: `None`

---

#### build_failure_envelope()

**Signature**: `build_failure_envelope(*, failure_class: str, failure_code: str, failure_reason: str, failure_source: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `failure_class` | `str` | — | — |
| `failure_code` | `str` | — | — |
| `failure_reason` | `str` | — | — |
| `failure_source` | `str` | — | — |

**Returns**: `dict[str, str]`

---

#### record_step_usage()

**Signature**: `record_step_usage(state: dict[str, Any], step: str, usage_data: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `usage_data` | `dict[str, Any]` | — | — |

**Returns**: `None`

---

#### default_review_state()

**Signature**: `default_review_state()`

**Returns**: `dict[str, Any]`

---

#### default_task_execution_binding()

**Signature**: `default_task_execution_binding()`

**Returns**: `dict[str, Any]`

---

#### default_usage_summary()

**Signature**: `default_usage_summary()`

**Returns**: `dict[str, Any]`

---

#### make_job_id()

**Signature**: `make_job_id(group_name: str, group_cfg: dict[str, Any], seed_artifacts: dict[str, str])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |
| `group_cfg` | `dict[str, Any]` | — | — |
| `seed_artifacts` | `dict[str, str]` | — | — |

**Returns**: `str`

---

#### infer_seed_identity()

**Signature**: `infer_seed_identity(group_name: str, seed_artifacts: dict[str, str])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |
| `seed_artifacts` | `dict[str, str]` | — | — |

**Returns**: `tuple[str | None, str | None]`

---

#### create_job()

**Signature**: `create_job(group_name: str, group_cfg: dict[str, Any], seed_artifacts: dict[str, str])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |
| `group_cfg` | `dict[str, Any]` | — | — |
| `seed_artifacts` | `dict[str, str]` | — | — |

**Returns**: `dict[str, Any]`

---

#### load_job()

**Signature**: `load_job(group_name: str, job_id: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |
| `job_id` | `str` | — | — |

**Returns**: `dict[str, Any]`

---

#### save_job()

**Signature**: `save_job(group_name: str, job_id: str, state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |
| `job_id` | `str` | — | — |
| `state` | `dict[str, Any]` | — | — |

**Returns**: `None`

---

#### iter_group_jobs()

**Signature**: `iter_group_jobs(group_name: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |

**Returns**: `list[dict[str, Any]]`

---

#### find_matching_active_job()

**Signature**: `find_matching_active_job(*, group_name: str, seed_artifact_type: str, seed_artifact_path: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |
| `seed_artifact_type` | `str` | — | — |
| `seed_artifact_path` | `str` | — | — |

**Returns**: `str | None`

---

#### find_matching_completed_job()

**Signature**: `find_matching_completed_job(*, group_name: str, seed_artifact_type: str, seed_artifact_path: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |
| `seed_artifact_type` | `str` | — | — |
| `seed_artifact_path` | `str` | — | — |

**Returns**: `str | None`

---

#### migrate_job_state()

**Signature**: `migrate_job_state(state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |

**Returns**: `dict[str, Any]`

---

#### ensure_backward_compatible_state()

**Signature**: `ensure_backward_compatible_state(state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |

**Returns**: `dict[str, Any]`

---

#### reconcile_job_state()

**Signature**: `reconcile_job_state(state: dict[str, Any], group_cfg: dict[str, Any])`

**Purpose**: Auto-repair obvious routing inconsistencies on job load.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `group_cfg` | `dict[str, Any]` | — | — |

**Returns**: `dict[str, Any]`

---

#### reapply_routing()

**Signature**: `reapply_routing(state: dict[str, Any], group_cfg: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `group_cfg` | `dict[str, Any]` | — | — |

**Returns**: `dict[str, Any]`

---

#### recover_exhausted_planning_job()

**Signature**: `recover_exhausted_planning_job(state: dict[str, Any], group_cfg: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `group_cfg` | `dict[str, Any]` | — | — |

**Returns**: `dict[str, Any]`

---

#### check_preflight_artifact_status()

**Signature**: `check_preflight_artifact_status(*, step_cfg: dict[str, Any], state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `step_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |

**Returns**: `None`

---

#### task_queue_is_initialized()

**Signature**: `task_queue_is_initialized(state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |

**Returns**: `bool`

---

#### task_queue_current_item()

**Signature**: `task_queue_current_item(state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |

**Returns**: `dict[str, Any] | None`

---

#### next_pending_task_queue_item()

**Signature**: `next_pending_task_queue_item(state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |

**Returns**: `dict[str, Any] | None`

---

#### task_queue_has_remaining_work()

**Signature**: `task_queue_has_remaining_work(state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |

**Returns**: `bool`

---

#### extract_task_graph_nodes()

**Signature**: `extract_task_graph_nodes(task_graph_path: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `task_graph_path` | `str` | — | — |

**Returns**: `list[dict[str, Any]]`

---

#### find_task_graph_file_by_id()

**Signature**: `find_task_graph_file_by_id(task_graph_id: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `task_graph_id` | `str` | — | — |

**Returns**: `str`

---

#### find_plan_file_by_id()

**Signature**: `find_plan_file_by_id(plan_id: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `plan_id` | `str` | — | — |

**Returns**: `str`

---

#### build_task_execution_binding()

**Signature**: `build_task_execution_binding(*, task_graph_file: str, task_node_id: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `task_graph_file` | `str` | — | — |
| `task_node_id` | `str` | — | — |

**Returns**: `dict[str, Any]`

---

#### build_task_execution_binding_from_ids()

**Signature**: `build_task_execution_binding_from_ids(*, task_graph_id: str, task_node_id: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `task_graph_id` | `str` | — | — |
| `task_node_id` | `str` | — | — |

**Returns**: `dict[str, Any]`

---

#### task_execution_binding_identity()

**Signature**: `task_execution_binding_identity(binding: dict[str, Any] | None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `binding` | `dict[str, Any] | None` | — | — |

**Returns**: `tuple[str | None, str | None]`

---

#### task_execution_binding_current_item()

**Signature**: `task_execution_binding_current_item(state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |

**Returns**: `dict[str, Any] | None`

---

#### apply_task_execution_binding()

**Signature**: `apply_task_execution_binding(state: dict[str, Any], binding: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `binding` | `dict[str, Any]` | — | — |

**Returns**: `None`

---

#### initialize_task_generation_state()

**Signature**: `initialize_task_generation_state(state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |

**Returns**: `None`

---

#### ensure_planning_task_queue_integrity()

**Signature**: `ensure_planning_task_queue_integrity(state: dict[str, Any], *, step: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |

**Returns**: `None`

---

#### ensure_execution_task_binding_integrity()

**Signature**: `ensure_execution_task_binding_integrity(state: dict[str, Any], *, step: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |

**Returns**: `None`

---

#### get_next_step_skipping_refine_replan()

**Signature**: `get_next_step_skipping_refine_replan(group_cfg: dict[str, Any], state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |

**Returns**: `str | None`

---

#### get_next_step()

**Signature**: `get_next_step(group_cfg: dict[str, Any], state: dict[str, Any])`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |

**Returns**: `str | None`

---

#### advance_step()

**Signature**: `advance_step(*, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], result_status: str, coder_used: str)`

**Purpose**: Unified step advancement. Returns (state, exit_code): 0=continue, 1=waiting, 2=failed.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `step_cfg` | `dict[str, Any]` | — | — |
| `result_status` | `str` | — | — |
| `coder_used` | `str` | — | — |

**Returns**: `tuple[dict[str, Any], int]`

---

#### approve_step()

**Signature**: `approve_step(*, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |
| `group_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |

**Returns**: `dict[str, Any]`

---

#### force_approve_step()

**Signature**: `force_approve_step(*, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |
| `group_cfg` | `dict[str, Any]` | — | — |
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |

**Returns**: `dict[str, Any]`

---

#### prepare_state_for_retry()

**Signature**: `prepare_state_for_retry(*, group_name: str, state: dict[str, Any], step: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | — | — |
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |

**Returns**: `dict[str, Any]`

---

#### enforce_retry_limit_before_run()

**Signature**: `enforce_retry_limit_before_run(*, state: dict[str, Any], step: str, max_rejects: int)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | — | — |
| `step` | `str` | — | — |
| `max_rejects` | `int` | — | — |

**Returns**: `None`

---

#### looks_like_transient_error()

**Signature**: `looks_like_transient_error(message: str)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `message` | `str` | — | — |

**Returns**: `bool`

---

#### classify_pre_run_failure()

**Signature**: `classify_pre_run_failure(exc: Exception)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `exc` | `Exception` | — | — |

**Returns**: `dict[str, str]`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `CURRENT_SCHEMA_VERSION` | module configuration |
| `NON_TERMINAL_JOB_STATUSES` | module configuration |
| `REVIEW_DECISIONS` | module configuration |
| `HUMAN_DECISIONS` | module configuration |
| `FINAL_DECISION_SOURCES` | module configuration |
| `CONTROL_CLASSES` | module configuration |
| `FAILURE_SOURCES` | module configuration |
| `REVIEW_ARTIFACT_TYPES` | module configuration |


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
| 2026-07-10 | Initial baseline generated from repository scan | 00_master_docs_bootstrap_v2 |
