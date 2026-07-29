# Design Document: job_state.py Extraction

**Status:** Draft  
**Created:** 2026-07-29  
**Scope:** Split job_state.py (~2,238 lines, 83 functions) into focused modules

---

## Current State Analysis

### File Statistics
- **Lines:** ~2,238
- **Functions:** 83 (including private helpers)
- **Primary Responsibilities:**
  1. State migration and backward compatibility (3 functions)
  2. Artifact tracking and status (8 functions)
  3. Review management and decisions (8 functions)
  4. Task execution binding (7 functions)
  5. Job lifecycle (create/load/save) (8 functions)
  6. Step advancement and routing (12 functions)
  7. Task queue management (6 functions)
  8. Document status tracking (4 functions)
  9. Path utilities (7 functions)
  10. Usage metrics (3 functions)

### Problems
- Violates Single Responsibility Principle
- Mixed abstraction levels (high-level job logic + low-level path utilities)
- Changes to review logic risk breaking job persistence
- Testing requires mocking entire job state

---

## Proposed New Module Structure

```
agent_runner_v2/
├── job_state.py                 # Core job lifecycle (~400 lines)
├── state_migration.py           # Migration and backward compatibility
├── artifact_tracker.py          # Artifact status and tracking
├── review_manager.py            # Review decisions and approval flow
├── task_execution.py            # Task binding and execution
├── job_persistence.py           # Job create/load/save
└── state_routing.py             # Step advancement and routing
```

---

## Module 1: state_migration.py

### Purpose
Job state migration between schema versions, backward compatibility

### Functions to Move (3 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `migrate_job_state` | 649 | Migrate job state to current schema version |
| `ensure_backward_compatible_state` | 698 | Ensure backward compatible state structure |
| `_repair_master_bootstrap_artifacts` | 787 | Repair master bootstrap artifacts |

### Interface Contract

```python
# state_migration.py

from typing import Any

CURRENT_SCHEMA_VERSION = 6  # v2 bumps to 6 (adds runner_version)

def migrate_job_state(state: dict[str, Any]) -> dict[str, Any]:
    """Migrate job state to current schema version.
    
    Handles migrations from older schema versions to current.
    Updates schema_version field after migration.
    
    Args:
        state: Job state dictionary (may be older version)
        
    Returns:
        Migrated state dictionary (current version)
    """
    ...

def ensure_backward_compatible_state(state: dict[str, Any]) -> dict[str, Any]:
    """Ensure state has all required fields for current version.
    
    Adds missing fields with default values.
    Does not change schema_version.
    
    Args:
        state: Job state dictionary
        
    Returns:
        State with all required fields present
    """
    ...

def repair_master_bootstrap_artifacts(state: dict[str, Any]) -> None:
    """Repair master bootstrap artifacts in state.
    
    Fixes artifact paths and metadata for master bootstrap workflows.
    Mutates state in place.
    
    Args:
        state: Job state dictionary (mutated)
    """
    ...
```

### Dependencies
- `agent_runner_v2.state_defaults`
- `agent_runner_v2.constants`
- `agent_runner_v2.documentation_guardrails`

---

## Module 2: artifact_tracker.py

### Purpose
Artifact status tracking, preflight checks, document status updates

### Functions to Move (8 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `get_job_status` | 113 | Get current job status |
| `set_job_status` | 118 | Set job status |
| `check_preflight_artifact_status` | 1096 | Validate preflight artifacts |
| `_update_document_status` | 1064 | Update document status metadata |
| `_extract_document_status` | 1044 | Extract status from document |
| `_normalize_document_status` | 1059 | Normalize status value |
| `_md5_file` | 1231 | Compute file MD5 hash |
| `_extract_document_metadata_value` | 1173 | Extract metadata from document |

### Interface Contract

```python
# artifact_tracker.py

from pathlib import Path
from typing import Any
from dataclasses import dataclass

@dataclass
class ArtifactStatus:
    """Artifact status information."""
    key: str
    path: Path | None
    exists: bool
    md5: str | None
    status: str | None

# Constants from job_state.py
NON_TERMINAL_JOB_STATUSES = {
    "IN_PROGRESS",
    "WAITING_FOR_AUTO_RETRY",
    "WAITING_FOR_HUMAN_INTERVENTION",
    "WAITING_FOR_HUMAN_APPROVAL",
    "WAITING_FOR_HUMAN_MAXRETRIED",
}

def get_job_status(state: dict[str, Any]) -> str:
    """Get current job status from state."""
    ...

def set_job_status(state: dict[str, Any], value: str) -> None:
    """Set job status in state."""
    ...

def check_preflight_artifacts(
    *,
    step_cfg: dict[str, Any],
    state: dict[str, Any]
) -> list[ArtifactStatus]:
    """Check preflight artifact status for a step.
    
    Validates that all required input artifacts exist.
    
    Args:
        step_cfg: Step configuration
        state: Job state
        
    Returns:
        List of artifact status objects
        
    Raises:
        PreflightBlockedError: If required artifacts are missing
    """
    ...

def update_document_status(
    *,
    file_path: str,
    new_status: str
) -> None:
    """Update document lifecycle_status in YAML frontmatter.
    
    Args:
        file_path: Path to document
        new_status: New lifecycle_status value
    """
    ...

def extract_document_status(content: str) -> str | None:
    """Extract lifecycle_status from document YAML frontmatter."""
    ...

def normalize_document_status(value: str) -> str:
    """Normalize document status to canonical value."""
    ...

def compute_file_md5(path: Path) -> str:
    """Compute MD5 hash of file contents."""
    ...
```

---

## Module 3: review_manager.py

### Purpose
Review decisions: approve, reject, force approve, resume, retry

### Functions to Move (8 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `approve_step` | 1746 | Approve a step (review approval) |
| `reject_step` | 1834 | Reject a step (send to refine) |
| `force_approve_step` | 1927 | Force approve (human override) |
| `resume_step` | 2015 | Resume a failed/waiting step |
| `retry_step` | 2080 | Retry a step (reset failure state) |
| `prepare_state_for_retry` | 2177 | Prepare state for retry |
| `enforce_retry_limit_before_run` | 2210 | Check retry limit before run |
| `_resolve_approval_target_artifact` | 1716 | Resolve approval target artifact |

### Interface Contract

```python
# review_manager.py

from typing import Any
from dataclasses import dataclass
from enum import Enum

class ReviewDecision(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class HumanDecision(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NOT_REQUIRED = "NOT_REQUIRED"

# Constants from job_state.py
REVIEW_DECISIONS = {"PENDING", "APPROVED", "REJECTED"}
HUMAN_DECISIONS = {"PENDING", "APPROVED", "REJECTED", "NOT_REQUIRED"}
FINAL_DECISION_SOURCES = {"MODEL", "HUMAN"}
CONTROL_CLASSES = {"AUTO_RETRYABLE", "HUMAN_RETRY_REQUIRED", "FATAL"}
FAILURE_SOURCES = {"runner", "adapter", "model", "validator"}
REVIEW_ARTIFACT_TYPES = {
    "PRE_INIT_FILE": "PRE_INIT",
    "INIT_FILE": "INIT",
    "PLAN_FILE": "PLAN",
    "TASK_GRAPH_FILE": "TASK_GRAPH",
    "TASK_FILE": "TASK",
    "IMPL_FILE": "IMPL",
    "VALIDATION_FILE": "VALIDATION",
}

def approve_step(
    *,
    group_name: str,
    job_id: str,
    step: str,
    state: dict[str, Any],
    group_cfg: dict[str, Any],
    reviewer: str = "human"
) -> dict[str, Any]:
    """Approve a step and advance workflow.
    
    Called when human reviewer approves step output.
    Updates review decision and advances to next step.
    
    Args:
        group_name: Template group name
        job_id: Job ID
        step: Step name
        state: Current job state
        group_cfg: Group configuration
        reviewer: Reviewer identifier (default: "human")
        
    Returns:
        Updated state dictionary
    """
    ...

def reject_step(
    *,
    group_name: str,
    job_id: str,
    step: str,
    state: dict[str, Any],
    group_cfg: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    """Reject a step and route to refine.
    
    Called when human reviewer rejects step output.
    Routes to on_reject_refine step if configured.
    
    Args:
        group_name: Template group name
        job_id: Job ID
        step: Step name
        state: Current job state
        group_cfg: Group configuration
        reason: Rejection reason
        
    Returns:
        Updated state dictionary
    """
    ...

def force_approve_step(
    *,
    group_name: str,
    job_id: str,
    step: str,
    state: dict[str, Any],
    group_cfg: dict[str, Any],
) -> dict[str, Any]:
    """Force approve a step (human override).
    
    Bypasses normal approval flow.
    Used for recovery scenarios.
    
    Args:
        group_name: Template group name
        job_id: Job ID
        step: Step name
        state: Current job state
        group_cfg: Group configuration
        
    Returns:
        Updated state dictionary
    """
    ...

def resume_step(
    *,
    group_name: str,
    job_id: str,
    step: str,
    state: dict[str, Any],
    group_cfg: dict[str, Any],
) -> dict[str, Any]:
    """Resume a failed or waiting step.
    
    Marks step for re-execution.
    Clears failure state if present.
    
    Args:
        group_name: Template group name
        job_id: Job ID
        step: Step name
        state: Current job state
        group_cfg: Group configuration
        
    Returns:
        Updated state dictionary
    """
    ...

def retry_step(
    *,
    group_name: str,
    job_id: str,
    step: str,
    state: dict[str, Any],
    group_cfg: dict[str, Any],
) -> dict[str, Any]:
    """Retry a step (reset and re-execute).
    
    Similar to resume but with full state reset.
    Used for explicit retry actions.
    
    Args:
        group_name: Template group name
        job_id: Job ID
        step: Step name
        state: Current job state
        group_cfg: Group configuration
        
    Returns:
        Updated state dictionary
    """
    ...

def prepare_state_for_retry(
    *,
    group_name: str,
    state: dict[str, Any],
    step: str
) -> dict[str, Any]:
    """Prepare state for retry by resetting failure counters.
    
    Args:
        group_name: Template group name
        state: Current job state
        step: Step name
        
    Returns:
        State prepared for retry
    """
    ...

def enforce_retry_limit(
    *,
    state: dict[str, Any],
    step: str,
    max_rejects: int
) -> None:
    """Enforce retry limit before running a step.
    
    Raises exception if retry limit exceeded.
    
    Args:
        state: Job state
        step: Step name
        max_rejects: Maximum allowed rejects
        
    Raises:
        RuntimeError: If retry limit exceeded
    """
    ...
```

---

## Module 4: task_execution.py

### Purpose
Task execution binding: create bindings, manage task queue

### Functions to Move (7 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `build_task_execution_binding` | 1303 | Build task execution binding |
| `build_task_execution_binding_from_ids` | 1342 | Build binding from IDs |
| `task_execution_binding_identity` | 1351 | Extract identity from binding |
| `task_execution_binding_current_item` | 1362 | Get current binding item |
| `apply_task_execution_binding` | 1377 | Apply binding to state |
| `initialize_task_generation_state` | 1393 | Initialize task generation |
| `extract_task_graph_nodes` | 1197 | Extract nodes from task graph |

### Interface Contract

```python
# task_execution.py

from typing import Any
from dataclasses import dataclass

@dataclass
class TaskExecutionBinding:
    """Task execution binding information."""
    task_graph_id: str
    task_node_id: str
    task_graph_path: str

def build_task_execution_binding(
    *,
    task_graph_file: str,
    task_node_id: str
) -> dict[str, Any]:
    """Build task execution binding from file path and node ID.
    
    Args:
        task_graph_file: Path to task graph file
        task_node_id: Task node identifier
        
    Returns:
        Task execution binding dictionary
    """
    ...

def build_task_execution_binding_from_ids(
    *,
    task_graph_id: str,
    task_node_id: str
) -> dict[str, Any]:
    """Build task execution binding from IDs.
    
    Args:
        task_graph_id: Task graph ID
        task_node_id: Task node identifier
        
    Returns:
        Task execution binding dictionary
    """
    ...

def task_execution_binding_identity(
    binding: dict[str, Any] | None
) -> tuple[str | None, str | None]:
    """Extract task graph ID and node ID from binding.
    
    Args:
        binding: Task execution binding or None
        
    Returns:
        Tuple of (task_graph_id, task_node_id)
    """
    ...

def apply_task_execution_binding(
    state: dict[str, Any],
    binding: dict[str, Any]
) -> None:
    """Apply task execution binding to job state.
    
    Mutates state in place.
    
    Args:
        state: Job state (mutated)
        binding: Task execution binding to apply
    """
    ...

def extract_task_graph_nodes(
    task_graph_path: str
) -> list[dict[str, Any]]:
    """Extract task nodes from task graph file.
    
    Args:
        task_graph_path: Path to task graph file
        
    Returns:
        List of task node dictionaries
    """
    ...

def initialize_task_generation_state(state: dict[str, Any]) -> None:
    """Initialize task generation state in job.
    
    Mutates state in place.
    
    Args:
        state: Job state (mutated)
    """
    ...
```

---

## Module 5: job_persistence.py

### Purpose
Job creation, loading, saving, directory management

### Functions to Move (8 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `create_job` | 413 | Create new job |
| `load_job` | 535 | Load job from disk |
| `save_job` | 563 | Save job to disk |
| `iter_group_jobs` | 579 | Iterate group jobs |
| `find_matching_active_job` | 595 | Find matching active job |
| `find_matching_completed_job` | 623 | Find matching completed job |
| `infer_seed_identity` | 398 | Infer seed identity |
| `make_job_id` | 362 | Generate job ID |

### Path Utilities (7 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `ensure_dir` | 128 | Ensure directory exists |
| `resolve_repo_path` | 133 | Resolve repo path |
| `normalize_repo_relative_path` | 141 | Normalize repo relative path |
| `group_dir` | 146 | Get group directory |
| `job_dir` | 151 | Get job directory |
| `job_state_path` | 156 | Get job state path |
| `create_step_dir` | 178 | Create step directory |

### JSON Utilities (3 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `load_json` | 263 | Load JSON file |
| `save_json` | 268 | Save JSON file |
| `save_json_atomic` | 273 | Atomic JSON save |

### Interface Contract

```python
# job_persistence.py

from pathlib import Path
from typing import Any

def create_job(
    group_name: str,
    group_cfg: dict[str, Any],
    seed_artifacts: dict[str, str],
    *,
    resume_if_exists: bool = True,
) -> tuple[str, dict[str, Any]]:
    """Create a new job.
    
    Args:
        group_name: Template group name
        group_cfg: Group configuration
        seed_artifacts: Initial artifacts for job
        resume_if_exists: If True, resume existing job if found
        
    Returns:
        Tuple of (job_id, job_state)
    """
    ...

def load_job(group_name: str, job_id: str) -> dict[str, Any]:
    """Load job state from disk.
    
    Args:
        group_name: Template group name
        job_id: Job ID
        
    Returns:
        Job state dictionary
        
    Raises:
        FileNotFoundError: If job not found
    """
    ...

def save_job(
    group_name: str,
    job_id: str,
    state: dict[str, Any]
) -> None:
    """Save job state to disk.
    
    Args:
        group_name: Template group name
        job_id: Job ID
        state: Job state to save
    """
    ...

def find_matching_job(
    group_name: str,
    seed_artifacts: dict[str, str],
    status_filter: set[str] | None = None
) -> dict[str, Any] | None:
    """Find existing job matching seed artifacts.
    
    Args:
        group_name: Template group name
        seed_artifacts: Seed artifacts to match
        status_filter: Optional status filter
        
    Returns:
        Matching job state or None
    """
    ...

def get_job_dir(group_name: str, job_id: str) -> Path:
    """Get job directory path."""
    ...

def get_job_state_path(group_name: str, job_id: str) -> Path:
    """Get job state file path."""
    ...

def ensure_directory(path: Path) -> None:
    """Ensure directory exists (mkdir -p)."""
    ...

def load_json_file(path: Path) -> dict[str, Any]:
    """Load JSON file."""
    ...

def save_json_file(path: Path, data: dict[str, Any]) -> None:
    """Save JSON file atomically."""
    ...
```

---

## Module 6: state_routing.py

### Purpose
Step advancement, routing logic, step sequencing

### Functions to Move (12 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `get_next_step` | 1517 | Get next step |
| `advance_step` | 1530 | Advance to next step |
| `_advance_to_next` | 1697 | Internal: advance to next |
| `_handle_refine_success` | 1587 | Handle refine success |
| `_handle_replan_success` | 1616 | Handle replan success |
| `_handle_review_approval` | 1645 | Handle review approval |
| `_handle_task_exec_success` | 1659 | Handle task exec success |
| `_handle_task_queue_success` | 1668 | Handle task queue success |
| `reapply_routing` | 968 | Reapply routing rules |
| `reconcile_job_state` | 840 | Reconcile job state |
| `_apply_loop_routing` | 886 | Apply loop routing |
| `_apply_replan_routing` | 918 | Apply replan routing |
| `_resolve_reject_route_for_state` | 999 | Resolve reject route |
| `recover_exhausted_planning_job` | 1011 | Recover exhausted planning |
| `_promote_pre_init_to_init` | 2146 | Promote pre-init to init |
| `_derive_init_path_from_pre_init` | 2134 | Derive init path |

### Task Queue Functions (6 functions)

| Function | Line | Purpose |
|----------|------|---------|
| `task_queue_is_initialized` | 1131 | Check if queue initialized |
| `task_queue_current_item` | 1137 | Get current queue item |
| `next_pending_task_queue_item` | 1149 | Get next pending item |
| `task_queue_has_remaining_work` | 1160 | Check if work remains |
| `_make_task_queue_item_id` | 1168 | Make queue item ID |
| `ensure_planning_task_queue_integrity` | 1419 | Ensure queue integrity |
| `ensure_execution_task_binding_integrity` | 1458 | Ensure binding integrity |

### Interface Contract

```python
# state_routing.py

from typing import Any

def get_next_step(
    group_cfg: dict[str, Any],
    state: dict[str, Any]
) -> str | None:
    """Get next step based on current state and routing rules.
    
    Args:
        group_cfg: Group configuration
        state: Current job state
        
    Returns:
        Next step name or None if workflow complete
    """
    ...

def advance_step(
    *,
    group_name: str,
    job_id: str,
    state: dict[str, Any],
    group_cfg: dict[str, Any],
    decision: str = "APPROVED",
) -> dict[str, Any]:
    """Advance workflow to next step.
    
    Args:
        group_name: Template group name
        job_id: Job ID
        state: Current job state
        group_cfg: Group configuration
        decision: Step decision (APPROVED, REJECTED, etc.)
        
    Returns:
        Updated state dictionary
    """
    ...

def reapply_routing(
    state: dict[str, Any],
    group_cfg: dict[str, Any]
) -> dict[str, Any]:
    """Reapply routing rules to state.
    
    Used after manual state modifications.
    
    Args:
        state: Current job state
        group_cfg: Group configuration
        
    Returns:
        Updated state with routing applied
    """
    ...

def reconcile_job_state(
    state: dict[str, Any],
    group_cfg: dict[str, Any]
) -> dict[str, Any]:
    """Reconcile job state with group configuration.
    
    Args:
        state: Current job state
        group_cfg: Group configuration
        
    Returns:
        Reconciled state dictionary
    """
    ...

def get_task_queue_status(state: dict[str, Any]) -> dict[str, Any]:
    """Get task queue status.
    
    Args:
        state: Job state
        
    Returns:
        Task queue status dictionary
    """
    ...

def next_pending_task(state: dict[str, Any]) -> dict[str, Any] | None:
    """Get next pending task from queue.
    
    Args:
        state: Job state
        
    Returns:
        Next pending task or None if queue empty
    """
    ...
```

---

## Usage Metrics (Keep in job_state.py or move to separate)

| Function | Line | Purpose |
|----------|------|---------|
| `record_step_usage` | 307 | Record step usage metrics |
| `_has_usage_metrics` | 313 | Check if has usage metrics |
| `_recompute_usage_summary` | 321 | Recompute usage summary |

**Recommendation:** Move to `usage_metrics.py` or keep in `job_state.py` as small module.

---

## Migration Plan

### Phase 1: Create New Modules (No Breaking Changes)

1. Create `state_migration.py`
2. Create `artifact_tracker.py`
3. Create `review_manager.py`
4. Create `task_execution.py`
5. Create `job_persistence.py`
6. Create `state_routing.py`

### Phase 2: Update job_state.py

```python
# New imports in job_state.py
from .state_migration import migrate_job_state, ensure_backward_compatible_state
from .artifact_tracker import get_job_status, set_job_status, check_preflight_artifacts
from .review_manager import approve_step, reject_step, force_approve_step, resume_step, retry_step
from .task_execution import build_task_execution_binding, apply_task_execution_binding
from .job_persistence import create_job, load_job, save_job
from .state_routing import get_next_step, advance_step, reapply_routing
```

### Phase 3: Update Import Paths

Update all files importing from `job_state.py` to use new modules:

```python
# BEFORE
from agent_runner_v2.job_state import approve_step, reject_step

# AFTER (option A - re-export)
from agent_runner_v2.job_state import approve_step, reject_step

# AFTER (option B - direct import)
from agent_runner_v2.review_manager import approve_step, reject_step
```

---

## Dependencies Graph

```
job_state.py
├── state_migration.py (uses: state_defaults, constants)
├── artifact_tracker.py (uses: exceptions, doc_paths, notification_manager)
├── review_manager.py (uses: exceptions, routing_runtime, transition_runtime)
├── task_execution.py (uses: job_persistence, constants)
├── job_persistence.py (uses: runtime_context, constants)
├── state_routing.py (uses: review_manager, task_execution, routing_runtime)
└── Other: usage metrics, path utilities
```

---

## Success Criteria

- [ ] Each new module < 500 lines
- [ ] job_state.py < 400 lines (re-exports only)
- [ ] All existing tests pass
- [ ] No circular imports between new modules
- [ ] Clear dependency direction: persistence → tracking → routing → review
