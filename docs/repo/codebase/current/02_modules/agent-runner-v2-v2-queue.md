---
title: "Module Documentation: agent_runner_v2.v2.queue"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/v2/queue.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-v2-queue.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.v2.queue

## 1. Module Overview

### 1.1 Purpose

V2 outcome queue -- file-based handoff between CLI and daemon.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `tempfile` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### get_queue_dir()

**Signature**: `get_queue_dir(queue_root: Path, workflow_name: str, job_id: str, *, date: str | None = None)`

**Purpose**: Return the queue directory for a specific job.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `queue_root` | `Path` | -- | Queue root path (e.g. ~/.ukbe-runner/queue). |
| `workflow_name` | `str` | -- | Workflow name. |
| `job_id` | `str` | -- | Job identifier (e.g. AMGEN-20260804-001). |
| `date` | `str | None` | `None` | Date prefix (YYYYMMDD). Defaults to today. |

**Returns**: `Path`

---

#### ensure_queue_dir()

**Signature**: `ensure_queue_dir(queue_dir: Path)`

**Purpose**: Create the queue directory and its archive/failed subfolders.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `queue_dir` | `Path` | -- | -- |

**Returns**: `None`

---

#### write_outcome()

**Signature**: `write_outcome(queue_dir: Path, step_run_id: str, outcome_data: dict[str, Any])`

**Purpose**: Atomically write an outcome file to the queue directory.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `queue_dir` | `Path` | -- | Job's queue directory. |
| `step_run_id` | `str` | -- | Step run UUID (used as filename). |
| `outcome_data` | `dict[str, Any]` | -- | Outcome payload dict. |

**Returns**: `Path`

---

#### read_outcome()

**Signature**: `read_outcome(file_path: Path)`

**Purpose**: Read and parse an outcome file from the queue.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `file_path` | `Path` | -- | Path to the outcome JSON file. |

**Returns**: `dict[str, Any] | None`

---

#### archive_outcome()

**Signature**: `archive_outcome(file_path: Path)`

**Purpose**: Move a successfully processed outcome file to the archive subfolder.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `file_path` | `Path` | -- | Path to the outcome file. |

**Returns**: `bool`

---

#### fail_outcome()

**Signature**: `fail_outcome(file_path: Path)`

**Purpose**: Move a failed outcome file to the failed subfolder.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `file_path` | `Path` | -- | Path to the outcome file. |

**Returns**: `bool`

---

#### list_pending_outcomes()

**Signature**: `list_pending_outcomes(queue_root: Path)`

**Purpose**: Scan the queue root for all pending outcome files.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `queue_root` | `Path` | -- | Queue root path (e.g. ~/.ukbe-runner/queue). |

**Returns**: `list[Path]`

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
