---
title: "Module Documentation: agent_runner_v2.job_state"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/job_state.py"
module_area: "state"
documentation_mode: "full"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-job-state.md"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260704-002 / 2026-07-04T10:47:08+08:00"
created: "2026-07-04T10:47:08+08:00"
owner: "00_master_docs_bootstrap_v1"
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
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| | | |

### 2.2 Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `now_iso` | `()` | public function |
| `get_job_status` | `(state)` | public function |
| `set_job_status` | `(state, value)` | public function |
| `ensure_dir` | `(path)` | public function |
| `resolve_repo_path` | `(value)` | public function |
| `normalize_repo_relative_path` | `(value)` | public function |
| `group_dir` | `(group_name)` | public function |
| `job_dir` | `(group_name, job_id)` | public function |
| `job_state_path` | `(group_name, job_id)` | public function |
| `get_step_index` | `(group_cfg, step)` | public function |
| `make_step_dir` | `(group_cfg, state, step)` | public function |
| `load_json` | `(path)` | public function |
| `save_json` | `(path, data)` | public function |
| `save_json_atomic` | `(path, data)` | public function |
| `save_text` | `(path, content)` | public function |
| `set_last_failure` | `()` | public function |
| `clear_last_failure` | `(state)` | public function |
| `append_failure_history` | `()` | public function |
| `build_failure_envelope` | `()` | public function |
| `record_step_usage` | `(state, step, usage_data)` | public function |
| `default_review_state` | `()` | public function |
| `default_task_execution_binding` | `()` | public function |
| `default_usage_summary` | `()` | public function |
| `make_job_id` | `(group_name, group_cfg, seed_artifacts)` | public function |
| `infer_seed_identity` | `(group_name, seed_artifacts)` | public function |
| `create_job` | `(group_name, group_cfg, seed_artifacts)` | public function |
| `load_job` | `(group_name, job_id)` | public function |
| `save_job` | `(group_name, job_id, state)` | public function |
| `iter_group_jobs` | `(group_name)` | public function |
| `find_matching_active_job` | `()` | public function |
| `find_matching_completed_job` | `()` | public function |
| `migrate_job_state` | `(state)` | public function |
| `ensure_backward_compatible_state` | `(state)` | public function |
| `reconcile_job_state` | `(state, group_cfg)` | Auto-repair obvious routing inconsistencies on job load. |
| `reapply_routing` | `(state, group_cfg)` | public function |
| `recover_exhausted_planning_job` | `(state, group_cfg)` | public function |
| `check_preflight_artifact_status` | `()` | public function |
| `task_queue_is_initialized` | `(state)` | public function |
| `task_queue_current_item` | `(state)` | public function |
| `next_pending_task_queue_item` | `(state)` | public function |
| `task_queue_has_remaining_work` | `(state)` | public function |
| `extract_task_graph_nodes` | `(task_graph_path)` | public function |
| `find_task_graph_file_by_id` | `(task_graph_id)` | public function |
| `find_plan_file_by_id` | `(plan_id)` | public function |
| `build_task_execution_binding` | `()` | public function |
| `build_task_execution_binding_from_ids` | `()` | public function |
| `task_execution_binding_identity` | `(binding)` | public function |
| `task_execution_binding_current_item` | `(state)` | public function |
| `apply_task_execution_binding` | `(state, binding)` | public function |
| `initialize_task_generation_state` | `(state)` | public function |
| `ensure_planning_task_queue_integrity` | `(state)` | public function |
| `ensure_execution_task_binding_integrity` | `(state)` | public function |
| `get_next_step_skipping_refine_replan` | `(group_cfg, state)` | public function |
| `get_next_step` | `(group_cfg, state)` | public function |
| `advance_step` | `()` | Unified step advancement. Returns (state, exit_code): 0=continue, 1=waiting, 2=failed. |
| `approve_step` | `()` | public function |
| `force_approve_step` | `()` | public function |
| `prepare_state_for_retry` | `()` | public function |
| `enforce_retry_limit_before_run` | `()` | public function |
| `looks_like_transient_error` | `(message)` | public function |
| `classify_pre_run_failure` | `(exc)` | public function |

### 2.3 Constants / Configuration

| Name | Value / Type | Purpose |
|------|-------------|---------|
| `CURRENT_SCHEMA_VERSION` | constant | module configuration |
| `NON_TERMINAL_JOB_STATUSES` | constant | module configuration |
| `REVIEW_DECISIONS` | constant | module configuration |
| `HUMAN_DECISIONS` | constant | module configuration |
| `FINAL_DECISION_SOURCES` | constant | module configuration |
| `CONTROL_CLASSES` | constant | module configuration |
| `FAILURE_SOURCES` | constant | module configuration |
| `REVIEW_ARTIFACT_TYPES` | constant | module configuration |

## 3. Internal Implementation

### 3.1 Key Data Structures

Auto-generated baseline documentation derived from the current source tree.

### 3.2 Algorithm / Flow

See the source module for implementation details; this document captures the public contract and scan-derived summary.

## 4. I/O Contract

### 4.1 Inputs

Derived from function parameters, imports, and file-level responsibilities.

### 4.2 Outputs

Derived from function return values and side effects observed in the source file.

### 4.3 Side Effects

Tracked at a baseline level by the repository scan.

## 5. Error Handling

| Error Condition | Handling | Recovery |
|----------------|----------|----------|
| | | |

## 6. Testing

### 6.1 Test Coverage

| Test File | Coverage Area |
|-----------|--------------|
| `tests/test_run_agent_status.py` | `agent_runner_v2.job_state` |

### 6.2 Known Gaps

Auto-generated baseline. Review and refine as the codebase evolves.

## 7. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-04 | Initial baseline generated from repository scan | 00_master_docs_bootstrap_v1 |
