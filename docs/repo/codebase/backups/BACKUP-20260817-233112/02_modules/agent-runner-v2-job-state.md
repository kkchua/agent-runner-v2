---
title: "Module Documentation: agent_runner_v2.job_state"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/job_state.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-job-state.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-bgmxg5vi / 2026-08-06T07:04:04+08:00"
created: "2026-08-06T07:04:04+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.job_state

## 1. Module Overview

### 1.1 Purpose

job_state.py -- All job.json lifecycle management for agent_runner_v2.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

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
| `time` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `constants` | external module | repository dependency |
| `doc_paths` | external module | repository dependency |
| `documentation_guardrails` | external module | repository dependency |
| `exceptions` | external module | repository dependency |
| `execution_support` | external module | repository dependency |
| `failure_runtime` | external module | repository dependency |
| `notification_manager` | external module | repository dependency |
| `notifications` | external module | repository dependency |
| `routing_runtime` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |
| `state_defaults` | external module | repository dependency |
| `transition_runtime` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### now_iso()

**Signature**: `now_iso()`

**Purpose**: Return the current local time as an ISO-8601 string (second precision).

**Returns**: `str`

---

#### get_job_status()

**Signature**: `get_job_status(state: dict[str, Any])`

**Purpose**: Return the current job status string, checking both status field names.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `str`

---

#### set_job_status()

**Signature**: `set_job_status(state: dict[str, Any], value: str)`

**Purpose**: Set the job status on both ``job_status`` and ``status`` fields.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `value` | `str` | -- | -- |

**Returns**: `None`

---

#### ensure_dir()

**Signature**: `ensure_dir(path: Path)`

**Purpose**: Create a directory and any missing parents (no error if it exists).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | -- | -- |

**Returns**: `None`

---

#### resolve_repo_path()

**Signature**: `resolve_repo_path(value: str)`

**Purpose**: Resolve a path relative to PROJECT_ROOT, or return it if already absolute.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `str` | -- | -- |

**Returns**: `Path`

---

#### normalize_repo_relative_path()

**Signature**: `normalize_repo_relative_path(value: str)`

**Purpose**: Return the repo-relative POSIX path for *value*, resolved against PROJECT_ROOT.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `str` | -- | -- |

**Returns**: `str`

---

#### group_dir()

**Signature**: `group_dir(group_name: str, date: str | None = None)`

**Purpose**: Return the jobs root directory for a workflow template group.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | Workflow template group name. |
| `date` | `str | None` | `None` | Optional YYYYMMDD date prefix. Defaults to today. |

**Returns**: `Path`

---

#### job_dir()

**Signature**: `job_dir(group_name: str, job_id: str)`

**Purpose**: Return the directory containing a specific job's state and step folders.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | -- |
| `job_id` | `str` | -- | -- |

**Returns**: `Path`

---

#### job_state_path()

**Signature**: `job_state_path(group_name: str, job_id: str)`

**Purpose**: Return the path to a job's ``job.json`` state file.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | -- |
| `job_id` | `str` | -- | -- |

**Returns**: `Path`

---

#### get_step_index()

**Signature**: `get_step_index(group_cfg: dict[str, Any], step: str)`

**Purpose**: Return the 1-based position of *step* in the workflow's step list.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `step` | `str` | -- | -- |

**Returns**: `int`

---

#### create_step_dir()

**Signature**: `create_step_dir(group_cfg: dict[str, Any], state: dict[str, Any], step: str, *, max_attempts: int = 20, retry_delay_seconds: float = 0.1)`

**Purpose**: Allocate and create a unique step directory robustly.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `state` | `dict[str, Any]` | -- | -- |
| `step` | `str` | -- | -- |
| `max_attempts` | `int` | `20` | -- |
| `retry_delay_seconds` | `float` | `0.1` | -- |

**Returns**: `Path`

---

#### next_step_sequence_for_job()

**Signature**: `next_step_sequence_for_job(*, group_name: str, job_id: str)`

**Purpose**: Compute the next monotonic step sequence number from existing step folders.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | -- |
| `job_id` | `str` | -- | -- |

**Returns**: `int`

---

#### make_step_dir()

**Signature**: `make_step_dir(group_cfg: dict[str, Any], state: dict[str, Any], step: str)`

**Purpose**: Build the canonical step directory path with sequence prefix and loop suffix.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `state` | `dict[str, Any]` | -- | -- |
| `step` | `str` | -- | -- |

**Returns**: `Path`

---

#### load_json()

**Signature**: `load_json(path: Path)`

**Purpose**: Read and parse a JSON file, returning the decoded dict.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | -- | -- |

**Returns**: `dict[str, Any]`

---

#### save_json()

**Signature**: `save_json(path: Path, data: dict[str, Any])`

**Purpose**: Write *data* as JSON to *path* using atomic write semantics.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | -- | -- |
| `data` | `dict[str, Any]` | -- | -- |

**Returns**: `None`

---

#### save_json_atomic()

**Signature**: `save_json_atomic(path: Path, data: dict[str, Any])`

**Purpose**: Atomically write *data* as indented JSON via a temp-file rename.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | -- | -- |
| `data` | `dict[str, Any]` | -- | -- |

**Returns**: `None`

---

#### save_text()

**Signature**: `save_text(path: Path, content: str)`

**Purpose**: Write UTF-8 text to *path*, creating parent directories as needed.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | -- | -- |
| `content` | `str` | -- | -- |

**Returns**: `None`

---

#### record_step_usage()

**Signature**: `record_step_usage(state: dict[str, Any], step: str, usage_data: dict[str, Any])`

**Purpose**: Store per-step token/cost usage and recompute the aggregate summary.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `step` | `str` | -- | -- |
| `usage_data` | `dict[str, Any]` | -- | -- |

**Returns**: `None`

---

#### make_job_id()

**Signature**: `make_job_id(group_name: str, group_cfg: dict[str, Any], seed_artifacts: dict[str, str])`

**Purpose**: Generate a unique job ID string with workflow prefix, source tag, date, and sequence number.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | -- |
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `seed_artifacts` | `dict[str, str]` | -- | -- |

**Returns**: `str`

---

#### infer_seed_identity()

**Signature**: `infer_seed_identity(group_name: str, seed_artifacts: dict[str, str])`

**Purpose**: Determine the primary seed artifact type and repo-relative path for a workflow.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | -- |
| `seed_artifacts` | `dict[str, str]` | -- | -- |

**Returns**: `tuple[str | None, str | None]`

---

#### create_job()

**Signature**: `create_job(group_name: str, group_cfg: dict[str, Any], seed_artifacts: dict[str, str], mode: str = 'manual', job_no: str = '')`

**Purpose**: Create a new job state on disk and return the initialized state dict.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | Workflow template group name. |
| `group_cfg` | `dict[str, Any]` | -- | Full workflow configuration dict. |
| `seed_artifacts` | `dict[str, str]` | -- | Pre-populated artifact key->path mappings. |
| `mode` | `str` | `'manual'` | ``"manual"`` or ``"daemon"``. |
| `job_no` | `str` | `''` | Backend-assigned job number (daemon mode only). |

**Returns**: `dict[str, Any]`

**Raises**:

- `ValueError` -- If a seed artifact key is not declared in the merged key set.

---

#### load_job()

**Signature**: `load_job(group_name: str, job_id: str)`

**Purpose**: Load a job state dict from ``job.json``, verifying group ownership.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | Expected workflow template group name. |
| `job_id` | `str` | -- | The job identifier. |

**Returns**: `dict[str, Any]`

**Raises**:

- `FileNotFoundError` -- If the job state file does not exist.
- `ValueError` -- If the stored group does not match *group_name*.

---

#### save_job()

**Signature**: `save_job(group_name: str, job_id: str, state: dict[str, Any])`

**Purpose**: Persist the job state dict to ``job.json``, syncing dual status fields.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | -- |
| `job_id` | `str` | -- | -- |
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `None`

---

#### iter_group_jobs()

**Signature**: `iter_group_jobs(group_name: str)`

**Purpose**: Load all job states for a workflow group, applying backward-compat normalization.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | -- |

**Returns**: `list[dict[str, Any]]`

---

#### find_matching_active_job()

**Signature**: `find_matching_active_job(*, group_name: str, seed_artifact_type: str, seed_artifact_path: str)`

**Purpose**: Find the unique active job matching a seed artifact, or return None.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | -- |
| `seed_artifact_type` | `str` | -- | -- |
| `seed_artifact_path` | `str` | -- | -- |

**Returns**: `str | None`

**Raises**:

- `ValueError` -- If multiple active jobs match the seed artifact.

---

#### find_matching_completed_job()

**Signature**: `find_matching_completed_job(*, group_name: str, seed_artifact_type: str, seed_artifact_path: str)`

**Purpose**: Find the unique completed job matching a seed artifact, or return None.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | -- |
| `seed_artifact_type` | `str` | -- | -- |
| `seed_artifact_path` | `str` | -- | -- |

**Returns**: `str | None`

**Raises**:

- `ValueError` -- If multiple completed jobs match the seed artifact.

---

#### migrate_job_state()

**Signature**: `migrate_job_state(state: dict[str, Any])`

**Purpose**: Apply sequential schema migrations to bring *state* to the current version.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `dict[str, Any]`

---

#### ensure_backward_compatible_state()

**Signature**: `ensure_backward_compatible_state(state: dict[str, Any])`

**Purpose**: Normalize a raw job state dict so all downstream code can rely on a uniform schema.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `dict[str, Any]`

---

#### reconcile_job_state()

**Signature**: `reconcile_job_state(state: dict[str, Any], group_cfg: dict[str, Any])`

**Purpose**: Auto-repair obvious routing inconsistencies on job load.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `group_cfg` | `dict[str, Any]` | -- | -- |

**Returns**: `dict[str, Any]`

---

#### reapply_routing()

**Signature**: `reapply_routing(state: dict[str, Any], group_cfg: dict[str, Any])`

**Purpose**: Re-evaluate routing for the current step and activate replan or refine loops as needed.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `group_cfg` | `dict[str, Any]` | -- | -- |

**Returns**: `dict[str, Any]`

---

#### recover_exhausted_planning_job()

**Signature**: `recover_exhausted_planning_job(state: dict[str, Any], group_cfg: dict[str, Any])`

**Purpose**: Attempt to recover a FAILED job by activating replan routing if budget allows.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `group_cfg` | `dict[str, Any]` | -- | -- |

**Returns**: `dict[str, Any]`

---

#### check_preflight_artifact_status()

**Signature**: `check_preflight_artifact_status(*, step_cfg: dict[str, Any], state: dict[str, Any])`

**Purpose**: Verify that an artifact document has the required status before step execution.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `step_cfg` | `dict[str, Any]` | -- | -- |
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `None`

---

#### task_queue_is_initialized()

**Signature**: `task_queue_is_initialized(state: dict[str, Any])`

**Purpose**: Return True if the task generation queue has been populated with ordered tasks.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `bool`

---

#### task_queue_current_item()

**Signature**: `task_queue_current_item(state: dict[str, Any])`

**Purpose**: Return the task queue item currently being processed, or None.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `dict[str, Any] | None`

---

#### next_pending_task_queue_item()

**Signature**: `next_pending_task_queue_item(state: dict[str, Any])`

**Purpose**: Return the first PENDING task queue item, or None if all are done.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `dict[str, Any] | None`

---

#### task_queue_has_remaining_work()

**Signature**: `task_queue_has_remaining_work(state: dict[str, Any])`

**Purpose**: Return True if any task queue item has not yet been approved.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `bool`

---

#### extract_task_graph_nodes()

**Signature**: `extract_task_graph_nodes(task_graph_path: str)`

**Purpose**: Parse an approved task graph markdown file into an ordered list of task node dicts.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `task_graph_path` | `str` | -- | -- |

**Returns**: `list[dict[str, Any]]`

---

#### find_task_graph_file_by_id()

**Signature**: `find_task_graph_file_by_id(task_graph_id: str)`

**Purpose**: Locate the unique approved task graph document matching *task_graph_id*.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `task_graph_id` | `str` | -- | -- |

**Returns**: `str`

**Raises**:

- `FileNotFoundError` -- If no matching file exists.
- `ValueError` -- If the match is not approved or multiple files match.

---

#### find_plan_file_by_id()

**Signature**: `find_plan_file_by_id(plan_id: str)`

**Purpose**: Locate the unique approved plan document matching *plan_id*.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `plan_id` | `str` | -- | -- |

**Returns**: `str`

**Raises**:

- `FileNotFoundError` -- If no matching file exists.
- `ValueError` -- If the match is not approved or multiple files match.

---

#### build_task_execution_binding()

**Signature**: `build_task_execution_binding(*, task_graph_file: str, task_node_id: str)`

**Purpose**: Build a complete task execution binding dict for a specific task node.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `task_graph_file` | `str` | -- | -- |
| `task_node_id` | `str` | -- | -- |

**Returns**: `dict[str, Any]`

**Raises**:

- `ValueError` -- If the task node is not found, is duplicated, or the task graph is missing Plan ID metadata.

---

#### build_task_execution_binding_from_ids()

**Signature**: `build_task_execution_binding_from_ids(*, task_graph_id: str, task_node_id: str)`

**Purpose**: Build a task execution binding by looking up the task graph file from its ID.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `task_graph_id` | `str` | -- | -- |
| `task_node_id` | `str` | -- | -- |

**Returns**: `dict[str, Any]`

---

#### task_execution_binding_identity()

**Signature**: `task_execution_binding_identity(binding: dict[str, Any] | None)`

**Purpose**: Return ``(seed_artifact_type, seed_artifact_path)`` for a binding, or ``(None, None)``.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `binding` | `dict[str, Any] | None` | -- | -- |

**Returns**: `tuple[str | None, str | None]`

---

#### task_execution_binding_current_item()

**Signature**: `task_execution_binding_current_item(state: dict[str, Any])`

**Purpose**: Return a lightweight dict of the currently bound task node, or None.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `dict[str, Any] | None`

---

#### apply_task_execution_binding()

**Signature**: `apply_task_execution_binding(state: dict[str, Any], binding: dict[str, Any])`

**Purpose**: Apply a task execution binding to *state*, updating artifacts and seed identity.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `binding` | `dict[str, Any]` | -- | -- |

**Returns**: `None`

---

#### initialize_task_generation_state()

**Signature**: `initialize_task_generation_state(state: dict[str, Any])`

**Purpose**: Parse the approved task graph and populate the task generation queue in *state*.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `None`

**Raises**:

- `ValueError` -- If the queue is already initialized or TASK_GRAPH_FILE is missing.

---

#### ensure_planning_task_queue_integrity()

**Signature**: `ensure_planning_task_queue_integrity(state: dict[str, Any], *, step: str)`

**Purpose**: Verify the task generation queue is intact for delivery planning steps.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `step` | `str` | -- | -- |

**Returns**: `None`

---

#### ensure_execution_task_binding_integrity()

**Signature**: `ensure_execution_task_binding_integrity(state: dict[str, Any], *, step: str)`

**Purpose**: Verify the task execution binding is intact for task execution steps.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | -- |
| `step` | `str` | -- | -- |

**Returns**: `None`

---

#### get_next_step()

**Signature**: `get_next_step(group_cfg: dict[str, Any], state: dict[str, Any])`

**Purpose**: Return the first incomplete step in the workflow, or None if all are done.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `state` | `dict[str, Any]` | -- | -- |

**Returns**: `str | None`

---

#### advance_step()

**Signature**: `advance_step(*, group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any], result_status: str, coder_used: str)`

**Purpose**: Unified step advancement. Returns (state, exit_code): 0=continue, 1=waiting, 2=failed.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_cfg` | `dict[str, Any]` | -- | -- |
| `state` | `dict[str, Any]` | -- | -- |
| `step` | `str` | -- | -- |
| `step_cfg` | `dict[str, Any]` | -- | -- |
| `result_status` | `str` | -- | -- |
| `coder_used` | `str` | -- | -- |

**Returns**: `tuple[dict[str, Any], int]`

---

#### approve_step()

**Signature**: `approve_step(*, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str)`

**Purpose**: Record human approval for a step that passed model review.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | Workflow template group name. |
| `group_cfg` | `dict[str, Any]` | -- | Full workflow configuration dict. |
| `state` | `dict[str, Any]` | -- | Mutable job state dict. |
| `step` | `str` | -- | Name of the step to approve. |

**Returns**: `dict[str, Any]`

**Raises**:

- `ValueError` -- If the step is not pending human approval, has no model approval, or the review decision is not APPROVED.

---

#### reject_step()

**Signature**: `reject_step(*, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str)`

**Purpose**: Reject a step pending human approval, triggering on_reject_refine routing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | Workflow template group name. |
| `group_cfg` | `dict[str, Any]` | -- | Full workflow configuration dict. |
| `state` | `dict[str, Any]` | -- | Mutable job state dict. |
| `step` | `str` | -- | Name of the step to reject. |

**Returns**: `dict[str, Any]`

**Raises**:

- `ValueError` -- If the step is not pending human approval.

---

#### force_approve_step()

**Signature**: `force_approve_step(*, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str)`

**Purpose**: Force-approve a step regardless of its current review decision.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | Workflow template group name. |
| `group_cfg` | `dict[str, Any]` | -- | Full workflow configuration dict. |
| `state` | `dict[str, Any]` | -- | Mutable job state dict. |
| `step` | `str` | -- | Name of the step to force-approve. |

**Returns**: `dict[str, Any]`

**Raises**:

- `ValueError` -- If the step is not defined in the workflow.

---

#### resume_step()

**Signature**: `resume_step(*, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str)`

**Purpose**: Force-approve a step that is waiting for intervention or max-retried.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | Workflow template group name. |
| `group_cfg` | `dict[str, Any]` | -- | Full workflow configuration dict. |
| `state` | `dict[str, Any]` | -- | Mutable job state dict. |
| `step` | `str` | -- | Name of the step to resume. |

**Returns**: `dict[str, Any]`

**Raises**:

- `ValueError` -- If the job status is not WAITING_FOR_HUMAN_INTERVENTION or WAITING_FOR_HUMAN_MAXRETRIED.

---

#### retry_step()

**Signature**: `retry_step(*, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str)`

**Purpose**: Reset failure and reject state so the step can be re-executed.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | Workflow template group name. |
| `group_cfg` | `dict[str, Any]` | -- | Full workflow configuration dict (unused but kept for |
| `state` | `dict[str, Any]` | -- | Mutable job state dict. |
| `step` | `str` | -- | Name of the step to retry. |

**Returns**: `dict[str, Any]`

**Raises**:

- `ValueError` -- If the job status is not WAITING_FOR_HUMAN_INTERVENTION or WAITING_FOR_HUMAN_MAXRETRIED.

---

#### prepare_state_for_retry()

**Signature**: `prepare_state_for_retry(*, group_name: str, state: dict[str, Any], step: str)`

**Purpose**: Reset a waiting job back to IN_PROGRESS so the step can be re-executed.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_name` | `str` | -- | Workflow template group name. |
| `state` | `dict[str, Any]` | -- | Mutable job state dict. |
| `step` | `str` | -- | The step to set as current. |

**Returns**: `dict[str, Any]`

---

#### enforce_retry_limit_before_run()

**Signature**: `enforce_retry_limit_before_run(*, state: dict[str, Any], step: str, max_rejects: int)`

**Purpose**: Raise if the step has already exhausted its allowed reject count.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `state` | `dict[str, Any]` | -- | Mutable job state dict (reads ``reject_counts``). |
| `step` | `str` | -- | Name of the step about to execute. |
| `max_rejects` | `int` | -- | Maximum allowed rejects for this step. |

**Returns**: `None`

**Raises**:

- `ValueError` -- If the step has reached or exceeded max rejects.

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

| Exception | When | Raised By |
|-----------|------|----------|
| `FileNotFoundError` | If the job state file does not exist. | `load_job`, `find_task_graph_file_by_id`, `find_plan_file_by_id` |
| `ValueError` | If a seed artifact key is not declared in the merged key set. | `create_job`, `load_job`, `find_matching_active_job` |


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| (none) | No test references found |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-08-06 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
