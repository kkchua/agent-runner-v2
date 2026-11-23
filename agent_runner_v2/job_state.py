#!/usr/bin/env python3
"""
job_state.py — All job.json lifecycle management for agent_runner_v2.

Extracted from v1 run_agent.py. Key differences from v1:
- approve_step / force_approve_step no longer write back to markdown files
- migrate_job_state adds schema version 6: runner_version="v2"
- No extract_blocking_issues, review_converges, or sync_review_metadata
- replan_context.blocking_issues is always [] (content analysis is coder's job)
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

from .doc_paths import delivery_doc_rel

from .constants import ARTIFACT_KEY_REVIEW, ARTIFACT_PATHS
from .execution_support import (
    build_failure_envelope,
    classify_pre_run_failure,
    default_usage_summary,
)
from .failure_runtime import (
    append_failure_history,
    clear_last_failure,
    set_last_failure,
)
from .v2.routing_runtime import get_next_step_skipping_refine_replan
from .v2.transition_runtime import (
    advance_to_next_step,
    complete_recovery_step,
    mark_review_waiting_for_human,
    mark_task_exec_success,
)
from .exceptions import (
    ArtifactMissingError,
    MetaJsonInvalidError,
    MetaJsonMissingError,
    PreflightBlockedError,
    TransactionConflictError,
)
from .documentation_guardrails import MASTER_BOOTSTRAP_WORKFLOWS, master_bootstrap_artifact_candidates
from .runtime_context import JOBS_ROOT, PROJECT_ROOT, get_workflow_module
from .notifications import send_notification
from .notification_manager import send_workflow_notification, send_step_notification
from .state_defaults import (
    default_loop_context,
    default_replan_context,
    default_review_state,
    default_task_execution_binding,
)

CURRENT_SCHEMA_VERSION = 6  # v2 bumps to 6 (adds runner_version)

NON_TERMINAL_JOB_STATUSES = {
    "IN_PROGRESS",
    "WAITING_FOR_AUTO_RETRY",
    "WAITING_FOR_HUMAN_INTERVENTION",
    "WAITING_FOR_HUMAN_APPROVAL",
    "WAITING_FOR_HUMAN_MAXRETRIED",
}

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
    ARTIFACT_KEY_REVIEW: "REVIEW",
}


def _workflow_module():
    """Return the loaded workflow module, raising if it is not available."""
    module = get_workflow_module()
    if module is None:
        raise RuntimeError("Workflow module is not loaded. Runtime must use the global workflow bundle.")
    return module


def _artifact_keys() -> list[str]:
    """Return the canonical list of artifact key strings from the workflow module."""
    return list(_workflow_module().ARTIFACT_KEYS)


def _template_groups() -> dict[str, dict[str, Any]]:
    """Return the TEMPLATE_GROUPS dict mapping workflow names to their configs."""
    return _workflow_module().TEMPLATE_GROUPS


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    """Return the current local time as an ISO-8601 string (second precision)."""
    return dt.datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

def get_job_status(state: dict[str, Any]) -> str:
    """Return the current job status string, checking both status field names."""
    return str(state.get("job_status") or state.get("status") or "")


def set_job_status(state: dict[str, Any], value: str) -> None:
    """Set the job status on both ``job_status`` and ``status`` fields."""
    state["job_status"] = value
    state["status"] = value


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def ensure_dir(path: Path) -> None:
    """Create a directory and any missing parents (no error if it exists)."""
    path.mkdir(parents=True, exist_ok=True)


def resolve_repo_path(value: str) -> Path:
    """Resolve a path relative to PROJECT_ROOT, or return it if already absolute."""
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def normalize_repo_relative_path(value: str) -> str:
    """Return the repo-relative POSIX path for *value*, resolved against PROJECT_ROOT."""
    return str(resolve_repo_path(value).resolve().relative_to(PROJECT_ROOT.resolve()))


def _extract_date_from_job_id(job_id: str) -> str | None:
    """Extract the YYYYMMDD date from a job_id.

    Job IDs follow the format ``{PREFIX}-{SOURCE_ID}-{YYYYMMDD}-{NNN}``.
    The date is the second-to-last dash-separated segment.

    Returns None if the date cannot be extracted.
    """
    parts = job_id.split("-")
    if len(parts) >= 2:
        candidate = parts[-2]
        if len(candidate) == 8 and candidate.isdigit():
            return candidate
    return None


def group_dir(group_name: str, date: str | None = None) -> Path:
    """Return the jobs root directory for a workflow template group.

    Args:
        group_name: Workflow template group name.
        date: Optional YYYYMMDD date prefix. Defaults to today.
    """
    date_str = date or dt.datetime.now().strftime("%Y%m%d")
    return JOBS_ROOT / date_str / group_name


def _legacy_group_dir(group_name: str) -> Path:
    """Return the pre-date-prefix group directory (backward compat)."""
    return JOBS_ROOT / group_name


def job_dir(group_name: str, job_id: str) -> Path:
    """Return the directory containing a specific job's state and step folders.

    Resolution order:
    1. ``AGENT_RUNNER_JOB_DIR`` env var (set by daemon — authoritative).
    2. Date-based path using date extracted from job_id.
    3. Legacy path (``JOBS_ROOT / group_name / job_id``) for backward compat.
    """
    # Daemon mode: use the env var directly
    env_job_dir = os.environ.get("AGENT_RUNNER_JOB_DIR", "").strip()
    if env_job_dir:
        return Path(env_job_dir)

    # Extract date from job_id for path construction
    date = _extract_date_from_job_id(job_id)
    date_path = group_dir(group_name, date) / job_id

    # Prefer date-based path if it exists
    if date_path.exists():
        return date_path

    # Fall back to legacy path for pre-migration jobs
    legacy_path = _legacy_group_dir(group_name) / job_id
    if legacy_path.exists():
        return legacy_path

    # Default to date-based path (for new job creation)
    return date_path


def job_state_path(group_name: str, job_id: str) -> Path:
    """Return the path to a job's ``job.json`` state file."""
    return job_dir(group_name, job_id) / "job.json"


def get_step_index(group_cfg: dict[str, Any], step: str) -> int:
    """Return the 1-based position of *step* in the workflow's step list."""
    return group_cfg["steps"].index(step) + 1


def _allocate_unique_step_dir(base_dir: Path) -> Path:
    """Return *base_dir* if unused, otherwise append ``_runN`` to avoid collisions."""
    if not base_dir.exists():
        return base_dir
    next_run = 2
    while True:
        candidate = base_dir.with_name(f"{base_dir.name}_run{next_run}")
        if not candidate.exists():
            return candidate
        next_run += 1


def create_step_dir(
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    *,
    max_attempts: int = 20,
    retry_delay_seconds: float = 0.1,
) -> Path:
    """Allocate and create a unique step directory robustly.

    Windows can transiently deny access to an existing step folder during
    reruns or interrupted jobs. In that case, advance to the next ``_runN``
    suffix instead of failing the entire resume path immediately.
    """
    base_dir = make_step_dir(group_cfg, state, step)
    candidate = base_dir
    next_run = 2
    attempts = 0

    while attempts < max_attempts:
        try:
            candidate.mkdir(parents=True, exist_ok=False)
            return candidate
        except FileExistsError:
            attempts += 1
            candidate = base_dir.with_name(f"{base_dir.name}_run{next_run}")
            next_run += 1
        except PermissionError:
            attempts += 1
            if candidate.exists() and candidate.is_dir():
                candidate = base_dir.with_name(f"{base_dir.name}_run{next_run}")
                next_run += 1
                time.sleep(retry_delay_seconds)
                continue
            if attempts >= max_attempts:
                raise
            time.sleep(retry_delay_seconds * attempts)

    raise PermissionError(
        f"Unable to allocate writable step directory for step {step!r} after {max_attempts} attempts under {base_dir.parent}"
    )


def next_step_sequence_for_job(*, group_name: str, job_id: str) -> int:
    """Compute the next monotonic step sequence number from existing step folders."""
    job_root = job_dir(group_name, job_id)
    if not job_root.exists():
        return 1

    max_prefix = 0
    for child in job_root.iterdir():
        if not child.is_dir():
            continue
        match = re.match(r"^(\d+)_", child.name)
        if not match:
            continue
        try:
            max_prefix = max(max_prefix, int(match.group(1)))
        except ValueError:
            continue
    return max_prefix + 1 if max_prefix > 0 else 1


def make_step_dir(group_cfg: dict[str, Any], state: dict[str, Any], step: str) -> Path:
    """Build the canonical step directory path with sequence prefix and loop suffix.

    Uses a monotonic execution sequence based on existing step folders.
    """
    idx = next_step_sequence_for_job(
        group_name=state["template_group"],
        job_id=state["job_id"],
    )
    ctx = state.get("loop_context", {})
    if ctx.get("active") and step in (ctx.get("refine_step"), ctx.get("loop_step")):
        suffix = f"_iter{ctx['loop_iteration']}"
    else:
        suffix = ""
    base_dir = job_dir(state["template_group"], state["job_id"]) / f"{idx:02d}_{step}{suffix}"
    return _allocate_unique_step_dir(base_dir)


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict[str, Any]:
    """Read and parse a JSON file, returning the decoded dict."""
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Write *data* as JSON to *path* using atomic write semantics."""
    save_json_atomic(path, data)


def save_json_atomic(path: Path, data: dict[str, Any]) -> None:
    """Atomically write *data* as indented JSON via a temp-file rename.

    Retries on transient ``PermissionError`` (common on Windows) and
    cleans up the temp file on any failure.
    """
    ensure_dir(path.parent)
    attempts = 0
    while True:
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, path)
            return
        except PermissionError:
            attempts += 1
            Path(temp_name).unlink(missing_ok=True)
            if attempts >= 5:
                raise
            time.sleep(0.1 * attempts)
        except Exception:
            Path(temp_name).unlink(missing_ok=True)
            raise


def save_text(path: Path, content: str) -> None:
    """Write UTF-8 text to *path*, creating parent directories as needed."""
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def record_step_usage(state: dict[str, Any], step: str, usage_data: dict[str, Any]) -> None:
    """Store per-step token/cost usage and recompute the aggregate summary."""
    state.setdefault("step_usage", {})[step] = usage_data
    state["usage_summary"] = _recompute_usage_summary(state["step_usage"])


def _has_usage_metrics(usage: dict[str, Any]) -> bool:
    """Return True if *usage* contains at least one non-None metric field."""
    for field in ("input_tokens", "output_tokens", "total_tokens", "cost", "duration_ms"):
        if usage.get(field) is not None:
            return True
    return False


def _recompute_usage_summary(step_usage: dict[str, Any]) -> dict[str, Any]:
    """Aggregate per-step usage dicts into a single summary with totals."""
    summary = default_usage_summary()
    totals: dict[str, float] = {}
    for usage in step_usage.values():
        if not isinstance(usage, dict):
            continue
        if not _has_usage_metrics(usage):
            summary["steps_without_usage"] += 1
            continue
        summary["steps_with_usage"] += 1
        for field in ("input_tokens", "output_tokens", "total_tokens", "cost", "duration_ms"):
            value = usage.get(field)
            if value is None:
                continue
            totals[field] = totals.get(field, 0) + value
    for field, value in totals.items():
        summary[field] = value if field == "cost" else int(value)
    return summary


# ---------------------------------------------------------------------------
# Job ID generation
# ---------------------------------------------------------------------------

def _extract_short_id(file_path: str, prefix: str) -> str:
    """Extract a zero-padded sequence suffix from a dated filename (e.g. ``INIT01``)."""
    name = Path(file_path).name
    match = re.search(rf"{prefix}-(\d{{8}})-(\d+)", name)
    if match:
        return f"{prefix}{match.group(2).zfill(2)}"
    return prefix


def _extract_draft_short_id(file_path: str) -> str:
    """Extract a ``DRAFT<year>`` identifier from a draft initiative filename."""
    name = Path(file_path).name
    match = re.search(r"(\d{2})-(\d{4})(?=_)", name)
    return f"DRAFT{match.group(2)}" if match else "DRAFT"


def make_job_id(group_name: str, group_cfg: dict[str, Any], seed_artifacts: dict[str, str]) -> str:
    """Generate a unique job ID string with workflow prefix, source tag, date, and sequence number.

    The format is ``{PREFIX}-{SOURCE_ID}-{YYYYMMDD}-{NNN}`` where SOURCE_ID is
    derived from the seed artifact filename for workflows that carry one.
    """
    prefix = group_cfg.get("job_prefix", group_name.upper())
    today = dt.datetime.now().strftime("%Y%m%d")
    source_id = "GEN"
    if group_name == "delivery_planning_v1":
        init_file = seed_artifacts.get("INIT_FILE")
        if init_file:
            source_id = _extract_short_id(init_file, "INIT")
    elif group_name == "initiative_intake_v1":
        draft = seed_artifacts.get("DRAFT_INIT_FILE")
        if draft:
            source_id = _extract_draft_short_id(draft)
    elif group_name == "task_execution_v1":
        task_file = seed_artifacts.get("TASK_FILE")
        if task_file:
            source_id = _extract_short_id(task_file, "TASK")
    base = f"{prefix}-{source_id}-{today}-"

    # Search today's date folder and legacy folder for existing sequence numbers
    nums: list[int] = []
    for search_dir in (group_dir(group_name, today), _legacy_group_dir(group_name)):
        if not search_dir.exists():
            continue
        nums.extend(
            int(child.name[len(base):])
            for child in search_dir.iterdir()
            if child.is_dir() and child.name.startswith(base) and child.name[len(base):].isdigit()
        )

    return f"{base}{(max(nums) + 1 if nums else 1):03d}"


# ---------------------------------------------------------------------------
# Job CRUD
# ---------------------------------------------------------------------------

def infer_seed_identity(group_name: str, seed_artifacts: dict[str, str]) -> tuple[str | None, str | None]:
    """Determine the primary seed artifact type and repo-relative path for a workflow.

    Returns ``(artifact_type, normalized_path)`` or ``(None, None)`` when the
    workflow has no identifiable seed artifact.
    """
    if group_name == "task_execution_v1" and seed_artifacts.get("TASK_FILE"):
        return "TASK_FILE", normalize_repo_relative_path(seed_artifacts["TASK_FILE"])
    if group_name == "delivery_planning_v1" and seed_artifacts.get("INIT_FILE"):
        return "INIT_FILE", normalize_repo_relative_path(seed_artifacts["INIT_FILE"])
    if group_name == "initiative_intake_v1" and seed_artifacts.get("DRAFT_INIT_FILE"):
        return "DRAFT_INIT_FILE", normalize_repo_relative_path(seed_artifacts["DRAFT_INIT_FILE"])
    return None, None


def create_job(group_name: str, group_cfg: dict[str, Any], seed_artifacts: dict[str, str],
               mode: str = "manual", job_no: str = "") -> dict[str, Any]:
    """Create a new job state on disk and return the initialized state dict.

    Merges artifact keys from the workflow module, step configs, the governance
    artifact registry, and global ``ARTIFACT_PATHS``.  In daemon mode the
    caller-supplied *job_no* is used as the job ID; otherwise a unique ID is
    generated via :func:`make_job_id`.

    Args:
        group_name: Workflow template group name.
        group_cfg: Full workflow configuration dict.
        seed_artifacts: Pre-populated artifact key→path mappings.
        mode: ``"manual"`` or ``"daemon"``.
        job_no: Backend-assigned job number (daemon mode only).

    Returns:
        The newly created job state dict (also persisted to ``job.json``).

    Raises:
        ValueError: If a seed artifact key is not declared in the merged key set.
    """
    if mode == "daemon" and job_no:
        job_id = job_no
    else:
        job_id = make_job_id(group_name, group_cfg, seed_artifacts)
    ensure_dir(job_dir(group_name, job_id))
    artifact_keys = list(_artifact_keys())
    artifact_keys_set = set(artifact_keys)

    # Merge workflow-declared artifact keys (from workflow.toml steps)
    _STEP_ARTIFACT_FIELDS = (
        "required_inputs", "optional_inputs", "produces",
        "target_artifact", "promotes", "result_meta_key",
        "source", "dest",
    )
    for step_cfg in group_cfg.get("step_configs", {}).values():
        for field in _STEP_ARTIFACT_FIELDS:
            val = step_cfg.get(field)
            if isinstance(val, list):
                for k in val:
                    if isinstance(k, str) and k not in artifact_keys_set:
                        artifact_keys.append(k)
                        artifact_keys_set.add(k)
            elif isinstance(val, str) and val not in artifact_keys_set:
                artifact_keys.append(val)
                artifact_keys_set.add(val)

    # Merge governance artifact registry keys
    for a in group_cfg.get("artifact_registry", []):
        k = a.get("key", "")
        if isinstance(k, str) and k and k not in artifact_keys_set:
            artifact_keys.append(k)
            artifact_keys_set.add(k)

    # Merge globally registered artifact keys (from all workflows' register_artifact_keys())
    for k in ARTIFACT_PATHS:
        if k not in artifact_keys_set:
            artifact_keys.append(k)
            artifact_keys_set.add(k)

    artifacts: dict[str, Any] = {k: None for k in artifact_keys}
    for key, value in seed_artifacts.items():
        if key not in artifact_keys:
            raise ValueError(f"Unknown artifact key {key!r}.")
        artifacts[key] = value
    seed_artifact_type, seed_artifact_path = infer_seed_identity(group_name, seed_artifacts)
    state: dict[str, Any] = {
        "job_id": job_id,
        "template_group": group_name,
        "runner_version": "v2",
        "job_init_step": group_cfg["job_init_step"],
        "workflow_artifact_keys": [
            a["key"] for a in group_cfg.get("artifact_registry", [])
        ],
        "job_status": "IN_PROGRESS",
        "status": "IN_PROGRESS",
        "current_step": group_cfg["job_init_step"],
        "completed_steps": [],
        "failed_steps": [],
        "reject_counts": {},
        "step_coders": {},
        "step_usage": {},
        "usage_summary": default_usage_summary(),
        "pending_human_approval_for": None,
        "human_approvals": {},
        "model_approved_steps": [],
        "review_state": default_review_state(),
        "last_model_output": None,
        "retry_history": [],
        "pending_intervention_for": None,
        "last_failure_class": None,
        "last_failure_code": None,
        "last_failure_reason": None,
        "last_failure_source": None,
        "auto_retry_count_by_step": {},
        "human_retry_count_by_step": {},
        "failure_history": [],
        "seed_artifact_type": seed_artifact_type,
        "seed_artifact_path": seed_artifact_path,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "artifacts": artifacts,
        "loop_context": default_loop_context(),
        "loop_history": [],
        "replan_context": default_replan_context(),
        "replan_history": [],
        "planning_attempt_count": 0,
        "recovered_from_invalid_result": False,
        "recovery_code": None,
        "recovery_source": None,
        "task_generation_state_version": 1,
        "task_generation_state": None,
        "task_execution_binding": default_task_execution_binding(),
        "state_schema_version": CURRENT_SCHEMA_VERSION,
        "repair_history": [],
        "reconciled_from_failure": None,
    }
    save_json(job_state_path(group_name, job_id), state)
    return state


def load_job(group_name: str, job_id: str) -> dict[str, Any]:
    """Load a job state dict from ``job.json``, verifying group ownership.

    Args:
        group_name: Expected workflow template group name.
        job_id: The job identifier.

    Returns:
        The parsed job state dict.

    Raises:
        FileNotFoundError: If the job state file does not exist.
        ValueError: If the stored group does not match *group_name*.
    """
    path = job_state_path(group_name, job_id)
    if not path.exists():
        raise FileNotFoundError(f"Job state not found: {path}")
    state = load_json(path)
    # Backend-managed jobs store workflow_name instead of template_group.
    # Accept either as the group association proof.
    actual_group = state.get("template_group") or state.get("workflow_name")
    if actual_group is not None and actual_group != group_name:
        raise ValueError(
            f"Job {job_id} belongs to {actual_group!r}, not {group_name!r}"
        )
    return state


def save_job(group_name: str, job_id: str, state: dict[str, Any]) -> None:
    """Persist the job state dict to ``job.json``, syncing dual status fields."""
    state["updated_at"] = now_iso()
    if state.get("job_status") and not state.get("status"):
        state["status"] = state["job_status"]
    elif state.get("status") and not state.get("job_status"):
        state["job_status"] = state["status"]
    elif state.get("job_status") and state.get("status") != state.get("job_status"):
        state["status"] = state["job_status"]
    save_json(job_state_path(group_name, job_id), state)


# ---------------------------------------------------------------------------
# Job discovery
# ---------------------------------------------------------------------------

def iter_group_jobs(group_name: str) -> list[dict[str, Any]]:
    """Load all job states for a workflow group, applying backward-compat normalization.

    Searches across all date-prefixed folders and the legacy (non-dated) folder.
    """
    states: list[dict[str, Any]] = []
    seen_job_ids: set[str] = set()

    # Collect candidate directories: all date folders + legacy folder
    search_dirs: list[Path] = []
    jobs_root = Path(JOBS_ROOT)
    if jobs_root.exists():
        for date_dir in sorted(jobs_root.iterdir(), reverse=True):
            if date_dir.is_dir() and date_dir.name.isdigit() and len(date_dir.name) == 8:
                candidate = date_dir / group_name
                if candidate.exists():
                    search_dirs.append(candidate)
        # Legacy folder (non-dated)
        legacy = jobs_root / group_name
        if legacy.exists():
            search_dirs.append(legacy)

    for gd in search_dirs:
        for child in sorted(gd.iterdir()):
            if not child.is_dir() or child.name in seen_job_ids:
                continue
            path = child / "job.json"
            if not path.exists():
                continue
            seen_job_ids.add(child.name)
            states.append(ensure_backward_compatible_state(load_json(path)))
    return states


def find_matching_active_job(
    *, group_name: str, seed_artifact_type: str, seed_artifact_path: str,
) -> str | None:
    """Find the unique active job matching a seed artifact, or return None.

    Raises:
        ValueError: If multiple active jobs match the seed artifact.
    """
    matches: list[str] = []
    for state in iter_group_jobs(group_name):
        if get_job_status(state) not in NON_TERMINAL_JOB_STATUSES:
            continue
        existing_type = state.get("seed_artifact_type")
        existing_path = state.get("seed_artifact_path")
        if not existing_type or not existing_path:
            artifacts = state.get("artifacts", {})
            if seed_artifact_type in artifacts and artifacts.get(seed_artifact_type):
                existing_type = seed_artifact_type
                existing_path = normalize_repo_relative_path(artifacts[seed_artifact_type])
        if existing_type == seed_artifact_type and existing_path == seed_artifact_path:
            matches.append(state["job_id"])
    if len(matches) > 1:
        raise ValueError(
            f"Multiple active jobs match {seed_artifact_type}={seed_artifact_path!r}: {matches}. Use --job-id."
        )
    return matches[0] if matches else None


def find_matching_completed_job(
    *, group_name: str, seed_artifact_type: str, seed_artifact_path: str,
) -> str | None:
    """Find the unique completed job matching a seed artifact, or return None.

    Raises:
        ValueError: If multiple completed jobs match the seed artifact.
    """
    matches: list[str] = []
    for state in iter_group_jobs(group_name):
        if get_job_status(state) != "COMPLETED":
            continue
        if (state.get("seed_artifact_type") == seed_artifact_type
                and state.get("seed_artifact_path") == seed_artifact_path):
            matches.append(state["job_id"])
    if len(matches) > 1:
        raise ValueError(
            f"Multiple completed jobs match {seed_artifact_type}={seed_artifact_path!r}: {matches}. Use --job-id."
        )
    return matches[0] if matches else None


# ---------------------------------------------------------------------------
# State migration + backward compat
# ---------------------------------------------------------------------------

def migrate_job_state(state: dict[str, Any]) -> dict[str, Any]:
    """Apply sequential schema migrations to bring *state* to the current version.

    Each ``version < N`` block adds fields introduced in that schema version.
    Also fixes ``task_id`` → ``task_node_id`` aliasing in the execution binding.
    """
    version = int(state.get("state_schema_version", 1))

    if version < 2:
        state.setdefault("loop_context", default_loop_context())
        state["loop_context"].setdefault("pre_refine_checksum", None)
        state.setdefault("loop_history", [])
        version = 2

    if version < 3:
        if state.get("job_status") is None and state.get("status") is not None:
            state["job_status"] = state["status"]
        elif state.get("status") is None and state.get("job_status") is not None:
            state["status"] = state["job_status"]
        state.setdefault("review_state", default_review_state())
        version = 3

    if version < 4:
        state.setdefault("task_generation_state_version", 1)
        state.setdefault("task_generation_state", None)
        version = 4

    if version < 5:
        state.setdefault("task_execution_binding", default_task_execution_binding())
        version = 5

    if version < 6:
        # v2: add runner_version marker
        state.setdefault("runner_version", "v2")
        version = 6

    # Fix task_id → task_node_id aliasing
    binding = state.get("task_execution_binding")
    if isinstance(binding, dict):
        if not binding.get("task_node_id") and binding.get("task_id"):
            binding["task_node_id"] = binding.get("task_id")
        snapshot = binding.get("task_node_snapshot")
        if isinstance(snapshot, dict) and not snapshot.get("task_node_id") and snapshot.get("task_id"):
            snapshot["task_node_id"] = snapshot.get("task_id")

    state["state_schema_version"] = version
    return state


def ensure_backward_compatible_state(state: dict[str, Any]) -> dict[str, Any]:
    """Normalize a raw job state dict so all downstream code can rely on a uniform schema.

    Handles backend-managed job field aliases (``run_code`` → ``job_id``, etc.),
    applies ``setdefault`` for every field introduced across schema versions,
    recomputes usage summaries, infers seed identity, and repairs master
    bootstrap artifact paths.
    """
    # --- Backend-managed job normalization ---------------------------------
    # Backend daemon creates jobs with different field names (run_code,
    # current_step_name, context_payload). Map them to v2 runner fields
    # so all downstream handlers (override-step, check-job-status, etc.)
    # can use the normal field access patterns.
    if state.get("run_code") and not state.get("job_id"):
        state["job_id"] = state["run_code"]
    if state.get("workflow_name") and not state.get("template_group"):
        state["template_group"] = state["workflow_name"]
    if state.get("current_step_name") and not state.get("current_step"):
        state["current_step"] = state["current_step_name"]
    if state.get("context_payload") and not state.get("artifacts"):
        state["artifacts"] = state["context_payload"]

    state.setdefault("state_schema_version", 1)
    state.setdefault("runner_version", "v2")
    state.setdefault("step_usage", {})
    state.setdefault("usage_summary", default_usage_summary())
    state.setdefault("pending_human_approval_for", None)
    state.setdefault("human_approvals", {})
    state.setdefault("model_approved_steps", [])
    state.setdefault("job_status", state.get("status", "IN_PROGRESS"))
    state.setdefault("review_state", default_review_state())
    state.setdefault("last_model_output", None)
    if state.get("status") != state.get("job_status"):
        state["status"] = state["job_status"]
    state.setdefault("retry_history", [])
    state.setdefault("step_coders", {})
    state.setdefault("reject_counts", {})
    state.setdefault("failed_steps", [])
    state.setdefault("completed_steps", [])
    state.setdefault("artifacts", {k: None for k in _artifact_keys()})
    state.setdefault("pending_intervention_for", None)
    state.setdefault("last_failure_class", None)
    state.setdefault("last_failure_code", None)
    state.setdefault("last_failure_reason", None)
    state.setdefault("last_failure_source", None)
    state.setdefault("auto_retry_count_by_step", {})
    state.setdefault("human_retry_count_by_step", {})
    state.setdefault("failure_history", [])
    state.setdefault("repair_history", [])
    state.setdefault("reconciled_from_failure", None)
    state.setdefault("seed_artifact_type", None)
    state.setdefault("seed_artifact_path", None)
    state.setdefault("loop_context", default_loop_context())
    state["loop_context"].setdefault("pre_refine_checksum", None)
    state.setdefault("loop_history", [])
    state.setdefault("replan_context", default_replan_context())
    state.setdefault("replan_history", [])
    state.setdefault("planning_attempt_count", 0)
    state.setdefault("recovered_from_invalid_result", False)
    state.setdefault("recovery_code", None)
    state.setdefault("recovery_source", None)
    state.setdefault("task_generation_state_version", 1)
    state.setdefault("task_generation_state", None)
    state.setdefault("task_execution_binding", default_task_execution_binding())
    binding = state.get("task_execution_binding")
    if isinstance(binding, dict):
        if not binding.get("task_node_id") and binding.get("task_id"):
            binding["task_node_id"] = binding.get("task_id")
        snapshot = binding.get("task_node_snapshot")
        if isinstance(snapshot, dict) and not snapshot.get("task_node_id") and snapshot.get("task_id"):
            snapshot["task_node_id"] = snapshot.get("task_id")
    if not state.get("seed_artifact_type") or not state.get("seed_artifact_path"):
        inferred_type, inferred_path = infer_seed_identity(
            state.get("template_group", ""), state.get("artifacts", {})
        )
        if not inferred_type and state.get("template_group") == "task_execution_v1":
            b = state.get("task_execution_binding") or {}
            if b.get("task_graph_file") and b.get("task_node_id"):
                inferred_type = "TASK_EXECUTION_BINDING"
                inferred_path = f"{normalize_repo_relative_path(b['task_graph_file'])}::{b['task_node_id']}"
        if inferred_type and inferred_path:
            state["seed_artifact_type"] = inferred_type
            state["seed_artifact_path"] = inferred_path
    if state.get("step_usage"):
        state["usage_summary"] = _recompute_usage_summary(state["step_usage"])
    _repair_master_bootstrap_artifacts(state)
    return state


def _repair_master_bootstrap_artifacts(state: dict[str, Any]) -> None:
    """Repair artifact paths for master bootstrap workflows by selecting canonical locations.

    For known bootstrap workflows, checks each artifact candidate path and
    copies the first existing file to the canonical location so downstream
    code always finds artifacts at the expected path.
    """
    if state.get("template_group") not in MASTER_BOOTSTRAP_WORKFLOWS:
        return

    job_id = str(state.get("job_id") or "").strip()
    mode = str((state.get("current_step_cfg") or {}).get("mode") or state.get("current_mode") or "bootstrap")
    candidates = master_bootstrap_artifact_candidates(
        template_group=str(state.get("template_group") or ""),
        job_id=job_id,
        mode=mode,
    )
    artifacts = state.setdefault("artifacts", {})

    for artifact_key, path_candidates in candidates.items():
        if not path_candidates:
            continue
        canonical_rel = path_candidates[0]
        canonical_abs = resolve_repo_path(canonical_rel)
        current_rel = str(artifacts.get(artifact_key) or "").strip()

        chosen_rel = ""
        if current_rel:
            current_abs = resolve_repo_path(current_rel)
            if current_abs.exists() and current_abs.is_file():
                chosen_rel = current_rel

        if not chosen_rel:
            for candidate_rel in path_candidates:
                candidate_abs = resolve_repo_path(candidate_rel)
                if candidate_abs.exists() and candidate_abs.is_file():
                    chosen_rel = candidate_rel
                    break

        if not chosen_rel:
            continue

        chosen_abs = resolve_repo_path(chosen_rel)
        if chosen_rel != canonical_rel:
            ensure_dir(canonical_abs.parent)
            canonical_abs.write_text(chosen_abs.read_text(encoding="utf-8"), encoding="utf-8")
        artifacts[artifact_key] = canonical_rel


# ---------------------------------------------------------------------------
# Reconcile + routing repair
# ---------------------------------------------------------------------------

def reconcile_job_state(state: dict[str, Any], group_cfg: dict[str, Any]) -> dict[str, Any]:
    """Auto-repair obvious routing inconsistencies on job load.

    In v2 this only handles the delivery_planning_v1 task-step terminal case
    and the WAITING_FOR_HUMAN_INTERVENTION → refine loop reactivation.
    It does NOT call extract_blocking_issues or review_converges.
    """
    if (
        state.get("template_group") == "delivery_planning_v1"
        and state.get("current_step") in {"task", "review_task", "refine_task", "replan_task"}
        and not state.get("pending_human_approval_for")
    ):
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
        # Send notification for auto-completed delivery planning workflow
        send_workflow_notification("COMPLETED", dict(state))
        return state

    if get_job_status(state) in {"COMPLETED", "FAILED"}:
        return state

    ctx = state.get("loop_context", {})
    current_step = state.get("current_step")
    step_cfg = group_cfg.get("step_configs", {}).get(current_step, {})

    excluded_codes: set[str] = {"MISSING_REVIEW_ARTIFACT", "DUPLICATE_REVIEW_FILE"}
    on_reject_refine = step_cfg.get("on_reject_refine") or {}
    if on_reject_refine.get("exhausted_failure_code"):
        excluded_codes.add(on_reject_refine["exhausted_failure_code"])

    if (
        get_job_status(state) == "WAITING_FOR_HUMAN_INTERVENTION"
        and not ctx.get("active")
        and step_cfg.get("on_reject_refine")
        and state.get("artifacts", {}).get(ARTIFACT_KEY_REVIEW)
        and state.get("last_failure_source") == "model"
        and state.get("last_failure_code") not in excluded_codes
    ):
        return _apply_loop_routing(state, current_step, step_cfg, repair_type="AUTO_RECONCILE")

    return state


def _apply_loop_routing(
    state: dict[str, Any], step: str, step_cfg: dict[str, Any], *, repair_type: str = "LOOP_TRIGGER",
) -> dict[str, Any]:
    """Activate a refine loop on *state*, routing to the configured refine step.

    Records the trigger in ``reconciled_from_failure`` and ``repair_history``,
    clears last-failure state, and sets the job back to IN_PROGRESS.
    """
    on_reject_refine = _resolve_reject_route_for_state(state=state, step_cfg=step_cfg)
    review_file = state.get("artifacts", {}).get(ARTIFACT_KEY_REVIEW)
    state["reconciled_from_failure"] = {
        "class": state.get("last_failure_class"),
        "code": state.get("last_failure_code"),
        "reason": state.get("last_failure_reason"),
        "source": state.get("last_failure_source"),
    }
    existing_iter = state.get("loop_context", {}).get("loop_iteration", 0)
    state["loop_context"] = default_loop_context(
        active=True,
        loop_step=step,
        refine_step=on_reject_refine["step"],
        target_artifact=on_reject_refine["artifact"],
        review_file=review_file,
        iteration=max(existing_iter, 1),
    )
    state["current_step"] = on_reject_refine["step"]
    set_job_status(state, "IN_PROGRESS")
    clear_last_failure(state)
    state.setdefault("repair_history", []).append({"type": repair_type, "step": step, "timestamp": now_iso()})
    return state


def reapply_routing(state: dict[str, Any], group_cfg: dict[str, Any]) -> dict[str, Any]:
    """Re-evaluate routing for the current step and activate refine loops as needed.

    Called when a user manually requests routing repair (e.g. after overriding
    the current step).
    """
    current_step = state.get("current_step")
    step_cfg = group_cfg.get("step_configs", {}).get(current_step, {})
    on_reject_refine = _resolve_reject_route_for_state(state=state, step_cfg=step_cfg) or {}
    exhausted_code = on_reject_refine.get("exhausted_failure_code")

    if step_cfg.get("on_reject_refine") and state.get("artifacts", {}).get(ARTIFACT_KEY_REVIEW):
        return _apply_loop_routing(state, current_step, step_cfg, repair_type="USER_REAPPLY")

    return state


def _resolve_reject_route_for_state(*, state: dict[str, Any], step_cfg: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve a reject-route override using the last failure code when present."""
    routes = step_cfg.get("reject_code_routes") or {}
    failure_code = str(state.get("last_failure_code") or "").strip().upper()
    if failure_code and isinstance(routes, dict):
        candidate = routes.get(failure_code)
        if isinstance(candidate, dict) and candidate.get("step") and candidate.get("artifact"):
            return candidate
    default_route = step_cfg.get("on_reject_refine")
    return default_route if isinstance(default_route, dict) else None


def recover_exhausted_planning_job(state: dict[str, Any], group_cfg: dict[str, Any]) -> dict[str, Any]:
    """No-op — replan routing removed; backend handles exhaustion as standard SOP."""
    return state


# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------

def _extract_document_status(content: str) -> str | None:
    """Parse a markdown document's Status field from bullet or YAML-style lines."""
    pattern = re.compile(
        r"^\s*[-*]\s*(?:\*\*)?Status(?::(?:\*\*)?|\*\*:\s*|:)\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    for line in content.splitlines():
        match = pattern.match(line.strip())
        if match:
            return match.group(1).strip()
        if line.strip().lower().startswith("status:"):
            return line.strip().split(":", 1)[1].strip()
    return None


def _normalize_document_status(value: str) -> str:
    """Normalize a status string to lowercase with underscores (e.g. ``changes_requested``)."""
    return re.sub(r"\s+", "_", value.strip().lower().replace("-", "_"))


def _update_document_status(*, file_path: str, new_status: str) -> None:
    """Update the Status line in a markdown document file.

    Matches patterns like:
    - `- Status: draft`
    - `- **Status**: changes_requested`
    - `Status: Approved`
    - `**Status**: draft`
    """
    abs_path = resolve_repo_path(file_path)
    if not abs_path.exists():
        return
    content = abs_path.read_text(encoding="utf-8")
    # Match status line with various markdown formats
    pattern = re.compile(
        r"^(\s*(?:[-*]\s*)?(?:\*\*)?)Status((?:\*\*)?(?::(?:\*\*)?|\*\*:\s*|:)\s*).+?(\s*)$",
        re.IGNORECASE | re.MULTILINE,
    )
    def _replacer(match: re.Match) -> str:
        prefix = match.group(1) or ""
        separator = match.group(2) or ": "
        suffix = match.group(3) or ""
        return f"{prefix}Status{separator}{new_status}{suffix}"
    updated = pattern.sub(_replacer, content)
    # Fallback: match plain "Status: value" at start of line
    if updated == content:
        plain_pattern = re.compile(r"^(\s*Status:\s*).+?(\s*)$", re.MULTILINE)
        updated = plain_pattern.sub(lambda m: f"{m.group(1)}{new_status}{m.group(2)}", content)
    if updated != content:
        abs_path.write_text(updated, encoding="utf-8")


def check_preflight_artifact_status(*, step_cfg: dict[str, Any], state: dict[str, Any]) -> None:
    """Verify that an artifact document has the required status before step execution.

    Reads the artifact's Status field and raises :class:`PreflightBlockedError`
    if it does not match the ``required_status`` declared in the step config.
    Silently passes when no preflight check is configured or the artifact is
    missing.
    """
    check = step_cfg.get("preflight_status_check")
    if not check:
        return
    artifact_key = check["artifact"]
    required_status = _normalize_document_status(check["required_status"])
    artifact_path = state.get("artifacts", {}).get(artifact_key)
    if not artifact_path:
        return
    path = resolve_repo_path(artifact_path)
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8")
    actual_status = _extract_document_status(content)
    if actual_status is None:
        return
    if _normalize_document_status(actual_status) != required_status:
        raise PreflightBlockedError(
            f"Preflight status check failed: {artifact_key} has status "
            f"'{actual_status}', expected '{check['required_status']}'. "
            f"Approve the document before proceeding."
        )


# ---------------------------------------------------------------------------
# Task queue helpers
# ---------------------------------------------------------------------------

def task_queue_is_initialized(state: dict[str, Any]) -> bool:
    """Return True if the task generation queue has been populated with ordered tasks."""
    queue = state.get("task_generation_state")
    return isinstance(queue, dict) and bool(queue.get("ordered_tasks"))


def task_queue_current_item(state: dict[str, Any]) -> dict[str, Any] | None:
    """Return the task queue item currently being processed, or None."""
    queue = state.get("task_generation_state")
    if not isinstance(queue, dict):
        return None
    current_id = queue.get("current_queue_item_id")
    for item in queue.get("ordered_tasks", []):
        if item.get("queue_item_id") == current_id:
            return item
    return None


def next_pending_task_queue_item(state: dict[str, Any]) -> dict[str, Any] | None:
    """Return the first PENDING task queue item, or None if all are done."""
    queue = state.get("task_generation_state")
    if not isinstance(queue, dict):
        return None
    for item in queue.get("ordered_tasks", []):
        if item.get("status") == "PENDING":
            return item
    return None


def task_queue_has_remaining_work(state: dict[str, Any]) -> bool:
    """Return True if any task queue item has not yet been approved."""
    queue = state.get("task_generation_state")
    if not isinstance(queue, dict):
        return False
    return any(item.get("status") != "APPROVED" for item in queue.get("ordered_tasks", []))


def _make_task_queue_item_id(sequence: int) -> str:
    """Generate a deterministic queue item ID from a 1-based sequence number."""
    return f"tgq_{sequence:04d}"


def _extract_document_metadata_value(content: str, key: str) -> str | None:
    """Extract a metadata value from markdown by key, matching bullet or table-row formats."""
    bullet_pattern = re.compile(
        rf"^\s*[-*]\s*(?:\*\*)?{re.escape(key)}(?::(?:\*\*)?|\*\*:\s*|:)\s*(.+?)\s*$",
        re.IGNORECASE,
    )
    # Also match Markdown table rows: | Key | Value | or | Key | `Value` (extra text) |
    table_pattern = re.compile(
        rf"^\|\s*{re.escape(key)}\s*\|\s*(.+?)\s*\|",
        re.IGNORECASE,
    )
    for line in content.splitlines():
        match = bullet_pattern.match(line.strip())
        if match:
            return match.group(1).strip().strip("`")
        match = table_pattern.match(line.strip())
        if match:
            # Extract the first backtick-delimited token if present, else the full cell value
            raw = match.group(1).strip()
            bt = re.match(r"`([^`]+)`", raw)
            return bt.group(1).strip() if bt else raw
    return None


def extract_task_graph_nodes(task_graph_path: str) -> list[dict[str, Any]]:
    """Parse an approved task graph markdown file into an ordered list of task node dicts.

    Each node contains ``task_node_id``, ``title``, ``sequence``, and queue
    metadata.  Raises ``ValueError`` if the file is missing, unparseable, or
    contains duplicate node IDs.
    """
    path = resolve_repo_path(task_graph_path)
    if not path.exists() or not path.is_file():
        raise ValueError(f"Task graph artifact does not exist: {path}")
    content = path.read_text(encoding="utf-8")
    pattern = re.compile(r"^###\s+`(TASK-\d{8}-\d+)`\s+[—-]\s+(.+?)\s*$", re.MULTILINE)
    matches = pattern.findall(content)
    if not matches:
        raise ValueError(f"Approved task graph could not be parsed into ordered task nodes: {task_graph_path}")
    seen: set[str] = set()
    ordered: list[dict[str, Any]] = []
    for index, (task_node_id, title) in enumerate(matches, start=1):
        task_node_id = task_node_id.strip()
        title = title.strip()
        if task_node_id in seen:
            raise ValueError(f"Approved task graph contains duplicate task_node_id {task_node_id!r}")
        if not title:
            raise ValueError(f"Approved task graph contains task node {task_node_id!r} without a title")
        seen.add(task_node_id)
        ordered.append({
            "queue_item_id": _make_task_queue_item_id(index),
            "task_id": task_node_id, "task_node_id": task_node_id,
            "title": title, "sequence": index, "status": "PENDING",
            "task_file": None, "review_step": None, "approved_at": None,
        })
    return ordered


def _md5_file(path: Path) -> str:
    """Return the hex MD5 digest of a file's contents."""
    import hashlib as _hashlib
    return _hashlib.md5(path.read_bytes()).hexdigest()


def find_task_graph_file_by_id(task_graph_id: str) -> str:
    """Locate the unique approved task graph document matching *task_graph_id*.

    Scans ``docs/delivery/02_plans/artifacts/`` for markdown files whose
    ``Task Graph ID`` metadata matches.  Returns the repo-relative path.

    Raises:
        FileNotFoundError: If no matching file exists.
        ValueError: If the match is not approved or multiple files match.
    """
    task_graph_id = task_graph_id.strip()
    if not task_graph_id:
        raise ValueError("task_graph_id is required.")
    artifact_dir = PROJECT_ROOT / "docs" / "delivery" / "02_plans" / "artifacts"
    if not artifact_dir.exists():
        raise FileNotFoundError(f"Task graph artifact directory not found: {artifact_dir}")
    matches: list[str] = []
    for candidate in sorted(artifact_dir.glob("*.md")):
        content = candidate.read_text(encoding="utf-8")
        metadata_id = (_extract_document_metadata_value(content, "Task Graph ID") or "").strip()
        if metadata_id != task_graph_id:
            continue
        status = _normalize_document_status(_extract_document_status(content) or "")
        if status != "approved":
            raise ValueError(f"Task graph {task_graph_id!r} is not approved: {candidate.relative_to(PROJECT_ROOT)}")
        matches.append(str(candidate.relative_to(PROJECT_ROOT)))
    if not matches:
        raise FileNotFoundError(f"No approved task graph matches task_graph_id {task_graph_id!r}.")
    if len(matches) > 1:
        raise ValueError(f"Multiple approved task graphs match task_graph_id {task_graph_id!r}: {matches}")
    return matches[0]


def find_plan_file_by_id(plan_id: str) -> str:
    """Locate the unique approved plan document matching *plan_id*.

    Scans ``docs/delivery/02_plans/`` for markdown files whose ``Plan ID``
    metadata matches.  Returns the repo-relative path.

    Raises:
        FileNotFoundError: If no matching file exists.
        ValueError: If the match is not approved or multiple files match.
    """
    plan_id = plan_id.strip()
    if not plan_id:
        raise ValueError("plan_id is required.")
    plan_dir = PROJECT_ROOT / "docs" / "delivery" / "02_plans"
    if not plan_dir.exists():
        raise FileNotFoundError(f"Plan directory not found: {plan_dir}")
    matches: list[str] = []
    for candidate in sorted(plan_dir.glob("*.md")):
        content = candidate.read_text(encoding="utf-8")
        metadata_id = (_extract_document_metadata_value(content, "Plan ID") or "").strip()
        if metadata_id != plan_id:
            continue
        status = _normalize_document_status(_extract_document_status(content) or "")
        if status != "approved":
            raise ValueError(f"Plan {plan_id!r} is not approved: {candidate.relative_to(PROJECT_ROOT)}")
        matches.append(str(candidate.relative_to(PROJECT_ROOT)))
    if not matches:
        raise FileNotFoundError(f"No approved plan matches plan_id {plan_id!r}.")
    if len(matches) > 1:
        raise ValueError(f"Multiple approved plans match plan_id {plan_id!r}: {matches}")
    return matches[0]


def build_task_execution_binding(*, task_graph_file: str, task_node_id: str) -> dict[str, Any]:
    """Build a complete task execution binding dict for a specific task node.

    Parses the task graph, resolves the plan file, captures a checksum, and
    takes a snapshot of the task node metadata.

    Raises:
        ValueError: If the task node is not found, is duplicated, or the task
            graph is missing Plan ID metadata.
    """
    ordered_tasks = extract_task_graph_nodes(task_graph_file)
    matches = [item for item in ordered_tasks if item.get("task_node_id") == task_node_id]
    if not matches:
        raise ValueError(f"Task graph {task_graph_file!r} does not contain task_node_id {task_node_id!r}.")
    if len(matches) > 1:
        raise ValueError(f"Task graph {task_graph_file!r} contains duplicate task_node_id {task_node_id!r}.")
    task_graph_content = resolve_repo_path(task_graph_file).read_text(encoding="utf-8")
    task_graph_id = (_extract_document_metadata_value(task_graph_content, "Task Graph ID") or "").strip()
    plan_id = (_extract_document_metadata_value(task_graph_content, "Plan ID") or "").strip()
    if not plan_id:
        raise ValueError(f"Task graph {task_graph_file!r} is missing Plan ID metadata.")
    task_node = matches[0]
    return {
        "task_graph_id": task_graph_id or None,
        "task_graph_file": task_graph_file,
        "task_graph_checksum": _md5_file(resolve_repo_path(task_graph_file)),
        "plan_id": plan_id,
        "plan_file": find_plan_file_by_id(plan_id),
        "task_node_id": str(task_node.get("task_node_id") or ""),
        "task_title": str(task_node.get("title") or ""),
        "task_node_snapshot": {
            "task_node_id": str(task_node.get("task_node_id") or ""),
            "title": str(task_node.get("title") or ""),
            "sequence": int(task_node.get("sequence") or 0),
        },
        "bound_at": now_iso(),
    }


def build_task_execution_binding_from_ids(*, task_graph_id: str, task_node_id: str) -> dict[str, Any]:
    """Build a task execution binding by looking up the task graph file from its ID."""
    task_graph_file = find_task_graph_file_by_id(task_graph_id)
    binding = build_task_execution_binding(task_graph_file=task_graph_file, task_node_id=task_node_id)
    if not binding.get("task_graph_id"):
        binding["task_graph_id"] = task_graph_id.strip()
    return binding


def task_execution_binding_identity(binding: dict[str, Any] | None) -> tuple[str | None, str | None]:
    """Return ``(seed_artifact_type, seed_artifact_path)`` for a binding, or ``(None, None)``."""
    if not isinstance(binding, dict):
        return None, None
    task_graph_file = str(binding.get("task_graph_file") or "").strip()
    task_node_id = str(binding.get("task_node_id") or "").strip()
    if not task_graph_file or not task_node_id:
        return None, None
    return "TASK_EXECUTION_BINDING", f"{normalize_repo_relative_path(task_graph_file)}::{task_node_id}"


def task_execution_binding_current_item(state: dict[str, Any]) -> dict[str, Any] | None:
    """Return a lightweight dict of the currently bound task node, or None."""
    binding = state.get("task_execution_binding")
    if not isinstance(binding, dict):
        return None
    task_node_id = str(binding.get("task_node_id") or "").strip()
    if not task_node_id:
        return None
    return {
        "queue_item_id": "",
        "task_node_id": task_node_id,
        "title": str(binding.get("task_title") or "").strip(),
    }


def apply_task_execution_binding(state: dict[str, Any], binding: dict[str, Any]) -> None:
    """Apply a task execution binding to *state*, updating artifacts and seed identity."""
    normalized = default_task_execution_binding()
    normalized.update(binding)
    state["task_execution_binding"] = normalized
    artifacts = state.setdefault("artifacts", {})
    if normalized.get("task_graph_file"):
        artifacts["TASK_GRAPH_FILE"] = normalized["task_graph_file"]
    if normalized.get("plan_file"):
        artifacts["PLAN_FILE"] = normalized["plan_file"]
    seed_type, seed_path = task_execution_binding_identity(normalized)
    if seed_type and seed_path:
        state["seed_artifact_type"] = seed_type
        state["seed_artifact_path"] = seed_path


def initialize_task_generation_state(state: dict[str, Any]) -> None:
    """Parse the approved task graph and populate the task generation queue in *state*.

    Raises:
        ValueError: If the queue is already initialized or TASK_GRAPH_FILE is missing.
    """
    if task_queue_is_initialized(state):
        raise ValueError("Task generation queue is already initialized for this job.")
    task_graph_path = state.get("artifacts", {}).get("TASK_GRAPH_FILE")
    if not task_graph_path:
        raise ValueError("Cannot initialize task queue without TASK_GRAPH_FILE.")
    ordered_tasks = extract_task_graph_nodes(task_graph_path)
    checksum = _md5_file(resolve_repo_path(task_graph_path))
    first_item = ordered_tasks[0]
    state["task_generation_state_version"] = 1
    state["task_generation_state"] = {
        "source_task_graph": task_graph_path,
        "source_task_graph_checksum": checksum,
        "initialized_at": now_iso(),
        "current_task_id": first_item["task_node_id"],
        "current_queue_item_id": first_item["queue_item_id"],
        "ordered_tasks": ordered_tasks,
    }
    state.setdefault("artifacts", {})["TASK_FILE"] = None


def ensure_planning_task_queue_integrity(state: dict[str, Any], *, step: str) -> None:
    """Verify the task generation queue is intact for delivery planning steps.

    Checks initialization, source task graph existence, checksum integrity,
    and current-item availability.  Raises :class:`PreflightBlockedError` on
    any inconsistency.  No-op for non-planning workflows or unrelated steps.
    """
    if state.get("template_group") != "delivery_planning_v1":
        return
    if step not in {"task", "review_task", "refine_task", "replan_task"}:
        return
    queue = state.get("task_generation_state")
    if not isinstance(queue, dict):
        raise PreflightBlockedError(
            f"Task generation queue is not initialized for step {step!r}. "
            "Approve review_task_graph before generating or reviewing task documents."
        )
    task_graph_path = queue.get("source_task_graph")
    stored_checksum = queue.get("source_task_graph_checksum")
    if not task_graph_path or not stored_checksum:
        raise PreflightBlockedError(
            f"Task generation queue is missing source task graph binding for step {step!r}."
        )
    actual_path = resolve_repo_path(task_graph_path)
    if not actual_path.exists() or not actual_path.is_file():
        raise PreflightBlockedError(f"Approved source task graph is missing for step {step!r}: {task_graph_path}")
    if _md5_file(actual_path) != stored_checksum:
        raise PreflightBlockedError(
            f"Approved task graph has changed since queue initialization for step {step!r}."
        )
    current_item = task_queue_current_item(state)
    if current_item is None:
        if task_queue_has_remaining_work(state):
            raise PreflightBlockedError(
                f"Task generation queue has remaining work but no current queue item for step {step!r}."
            )
        raise PreflightBlockedError(f"Task generation queue is exhausted for step {step!r}.")


def ensure_execution_task_binding_integrity(state: dict[str, Any], *, step: str) -> None:
    """Verify the task execution binding is intact for task execution steps.

    Checks binding initialization, task graph existence, checksum integrity,
    and task node snapshot consistency.  Raises :class:`PreflightBlockedError`
    on any mismatch.  No-op for non-execution workflows or unrelated steps.
    """
    if state.get("template_group") != "task_execution_v1":
        return
    if step not in {"task", "review_task", "refine_task"}:
        return
    binding = state.get("task_execution_binding")
    if not isinstance(binding, dict):
        raise PreflightBlockedError(
            f"Execution task binding is not initialized for step {step!r}. "
            "Start execution with --task-graph-id and --task-node-id."
        )
    task_graph_path = str(binding.get("task_graph_file") or "").strip()
    task_graph_checksum = str(binding.get("task_graph_checksum") or "").strip()
    task_node_id = str(binding.get("task_node_id") or "").strip()
    task_snapshot = binding.get("task_node_snapshot")
    if not task_graph_path or not task_graph_checksum or not task_node_id or not isinstance(task_snapshot, dict):
        raise PreflightBlockedError(
            f"Execution task binding is incomplete for step {step!r}. Recreate the execution job."
        )
    actual_path = resolve_repo_path(task_graph_path)
    if not actual_path.exists() or not actual_path.is_file():
        raise PreflightBlockedError(f"Approved source task graph is missing for step {step!r}: {task_graph_path}")
    if _md5_file(actual_path) != task_graph_checksum:
        raise PreflightBlockedError(
            f"Approved task graph has changed since execution binding was created for step {step!r}."
        )
    ordered_tasks = extract_task_graph_nodes(task_graph_path)
    matches = [item for item in ordered_tasks if item.get("task_node_id") == task_node_id]
    if len(matches) != 1:
        raise PreflightBlockedError(
            f"Selected task_node_id {task_node_id!r} is not present exactly once in bound task graph."
        )
    current_node = matches[0]
    expected_snapshot = {
        "task_node_id": str(task_snapshot.get("task_node_id") or ""),
        "title": str(task_snapshot.get("title") or ""),
        "sequence": int(task_snapshot.get("sequence") or 0),
    }
    actual_snapshot = {
        "task_node_id": str(current_node.get("task_node_id") or ""),
        "title": str(current_node.get("title") or ""),
        "sequence": int(current_node.get("sequence") or 0),
    }
    if actual_snapshot != expected_snapshot:
        raise PreflightBlockedError(
            f"Task binding for task_node_id {task_node_id!r} no longer matches the approved task graph snapshot."
        )


# ---------------------------------------------------------------------------
# Step navigation
# ---------------------------------------------------------------------------

def get_next_step(group_cfg: dict[str, Any], state: dict[str, Any]) -> str | None:
    """Return the first incomplete step in the workflow, or None if all are done."""
    completed = set(state.get("completed_steps", []))
    for step in group_cfg["steps"]:
        if step not in completed:
            return step
    return None


# ---------------------------------------------------------------------------
# Step type detection
# ---------------------------------------------------------------------------

def _is_refine_step(group_cfg: dict[str, Any], step_name: str) -> bool:
    """Check if step is the target of any on_reject_refine config."""
    for step_cfg in group_cfg.get("step_configs", {}).values():
        on_reject = step_cfg.get("on_reject_refine") or {}
        if on_reject.get("step") == step_name:
            return True
    return False


# ---------------------------------------------------------------------------
# Step advancement state machine
# ---------------------------------------------------------------------------

def advance_step(
    *,
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
    result_status: str,
    coder_used: str,
    defer_notifications: bool = False,
) -> tuple[dict[str, Any], int]:
    """Unified step advancement. Returns (state, exit_code): 0=continue, 1=waiting, 2=failed.

    If defer_notifications=True, suppress STEP_COMPLETED notification.
    Caller dispatches notifications after authoritative save.
    """
    artifacts = state.setdefault("artifacts", {})
    reject_counts = state.setdefault("reject_counts", {})
    completed_steps = state.setdefault("completed_steps", [])
    state.setdefault("step_coders", {})[step] = coder_used

    if result_status != "APPROVED":
        return state, 1  # Handled by workflow_router

    # SUCCESS PATH
    state["completed_steps"] = list(dict.fromkeys(completed_steps + [step]))
    reject_counts[step] = 0
    state.setdefault("auto_retry_count_by_step", {})[step] = 0
    state.setdefault("human_retry_count_by_step", {})[step] = 0
    clear_last_failure(state)

    # Check for step-level notification configuration
    # Suppress if defer_notifications=True (caller will dispatch after save)
    if not defer_notifications:
        send_step_notification("STEP_COMPLETED", state, step, step_cfg)

    review_state = state.setdefault("review_state", default_review_state())
    if review_state.get("reviewer_step") == step and not step_cfg.get("requires_human_approval_after"):
        review_state["review_decision"] = "APPROVED"
        review_state["review_decided_at"] = now_iso()
        review_state["human_decision"] = "NOT_REQUIRED"
        review_state["human_decided_at"] = None
        review_state["human_actor"] = None
        review_state["final_decision"] = "APPROVED"
        review_state["final_decision_source"] = "MODEL"

    if _is_refine_step(group_cfg, step) and state.get("loop_context", {}).get("active"):
        return _handle_refine_success(state, step, step_cfg, artifacts)

    if step_cfg.get("requires_human_approval_after"):
        return _handle_review_approval(state, step, step_cfg, coder_used)

    if state.get("template_group") == "task_execution_v1" and step == "task":
        return _handle_task_exec_success(state, step)

    if (state.get("template_group") == "delivery_planning_v1"
            and step == "task" and task_queue_is_initialized(state)):
        return _handle_task_queue_success(state, step, artifacts)

    return _advance_to_next(group_cfg, state, step, step_cfg)


def _handle_refine_success(
    state: dict[str, Any], step: str, step_cfg: dict[str, Any], artifacts: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    """Complete a refine recovery step: verify content changed, update loop history, and return to the review step."""
    next_step = step_cfg.get("onsuccess", "")
    ctx = state.get("loop_context", {})
    target_key = ctx.get("loop_target_artifact") or step_cfg.get("target_artifact", "IMPL_FILE")
    state, exit_code = complete_recovery_step(
        state=state,
        step=step,
        target_key=target_key,
        artifacts=artifacts,
        pre_checksum=ctx.get("pre_refine_checksum"),
        no_op_failure_code="NO_OP_REFINEMENT",
        no_op_failure_reason="Refine step made no content change to the target artifact",
        history_key="loop_history",
        history_result_field="refine_result",
        history_time_field="refine_at",
        next_step=next_step,
        project_root=PROJECT_ROOT,
        now_iso=now_iso,
        set_last_failure=set_last_failure,
        append_failure_history=append_failure_history,
        set_job_status=set_job_status,
        checksum_file=_md5_file,
        reset_replan_context=False,
    )
    if exit_code == 0:
        # Clear stale review state so the outcome queue doesn't send a
        # contradictory review.decision=REJECTED alongside outcome=approved.
        review_state = state.get("review_state") or {}
        review_state["review_decision"] = None
        review_state["review_decided_at"] = None
        review_state["final_decision"] = None
        review_state["final_decision_source"] = None
        # Increment persistent revision counter for versioned artifacts (plan_first_review_v1 only)
        if state.get("template_group") == "plan_first_review_v1":
            state["plan_revision"] = state.get("plan_revision", 1) + 1
    return state, exit_code


def _handle_review_approval(
    state: dict[str, Any], step: str, step_cfg: dict[str, Any], coder_used: str,
) -> tuple[dict[str, Any], int]:
    """Transition the job to WAITING_FOR_HUMAN_APPROVAL after a successful model review."""
    return mark_review_waiting_for_human(
        state=state,
        step=step,
        coder_used=coder_used,
        default_review_state=default_review_state,
        now_iso=now_iso,
        set_job_status=set_job_status,
    )


def _handle_task_exec_success(state: dict[str, Any], step: str) -> tuple[dict[str, Any], int]:
    """Handle successful task step in the task_execution_v1 workflow."""
    return mark_task_exec_success(
        state=state,
        step=step,
        set_job_status=set_job_status,
    )


def _handle_task_queue_success(
    state: dict[str, Any], step: str, artifacts: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    """Advance the task generation queue after a successful task step in delivery_planning_v1.

    Marks the current queue item as DRAFT_CREATED and routes to review_task.
    If no current item exists, sets a failure and returns exit_code 1.
    """
    current_item = task_queue_current_item(state)
    if current_item is None:
        set_last_failure(state=state, failure_class="HUMAN_RETRY_REQUIRED",
                         failure_code="TASK_QUEUE_STATE_INVALID",
                         failure_reason="Task step approved but no current queue item is active.",
                         failure_source="runner", step=step)
        append_failure_history(state=state, step=step, failure_class="HUMAN_RETRY_REQUIRED",
                               failure_code="TASK_QUEUE_STATE_INVALID", failure_source="runner")
        state.setdefault("reject_counts", {})[step] = int(state.get("reject_counts", {}).get(step, 0)) + 1
        set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
        state["current_step"] = step
        return state, 1
    current_item["status"] = "DRAFT_CREATED"
    current_item["task_file"] = artifacts.get("TASK_FILE")
    current_item["review_step"] = "review_task"
    state["completed_steps"] = list(dict.fromkeys(state.setdefault("completed_steps", []) + [step]))
    set_job_status(state, "IN_PROGRESS")
    state["current_step"] = "review_task"
    return state, 0


def _advance_to_next(
    group_cfg: dict[str, Any], state: dict[str, Any], step: str, step_cfg: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], int]:
    """Advance to the next workflow step, or mark the job COMPLETED if none remains."""
    return advance_to_next_step(
        group_cfg=group_cfg,
        state=state,
        step=step,
        step_cfg=step_cfg,
        set_job_status=set_job_status,
        get_next_step_skipping_refine_replan=get_next_step_skipping_refine_replan,
        on_completed=lambda current_state: send_workflow_notification("COMPLETED", dict(current_state)),
    )


# ---------------------------------------------------------------------------
# Human approval commands
# ---------------------------------------------------------------------------

def _resolve_approval_target_artifact(*, group_name: str, step: str, group_cfg: dict, state: dict) -> str | None:
    """Resolve which artifact file should have its status updated on human approval.

    Returns (artifact_key, new_status) or None if no document should be updated.

    For most review steps, the target is the artifact referenced in on_reject_refine.artifact
    and the status is APPROVED.
    Special cases:
      - validator → TASK_FILE gets COMPLETED (task is fully done)
      - review_pre_init → PRE_INIT_FILE gets APPROVED
    """
    step_cfg = group_cfg["step_configs"].get(step)
    if not step_cfg:
        return None, None

    # Validator is special: it closes the task document
    if step == "validator":
        return "TASK_FILE", "COMPLETED"

    on_reject_refine = step_cfg.get("on_reject_refine") or {}
    if on_reject_refine.get("artifact"):
        return on_reject_refine["artifact"], "APPROVED"

    # Fallback for review_pre_init
    if step == "review_pre_init":
        return "PRE_INIT_FILE", "APPROVED"

    return None, None


def approve_step(
    *, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str,
) -> dict[str, Any]:
    """Record human approval for a step that passed model review.

    The step must be pending human approval (``pending_human_approval_for``)
    and must have a recorded model approval in ``model_approved_steps``.
    On success the review state is updated to APPROVED/HUMAN and the job
    advances to the next step (or completes if this was the last step).

    Args:
        group_name: Workflow template group name.
        group_cfg: Full workflow configuration dict.
        state: Mutable job state dict.
        step: Name of the step to approve.

    Returns:
        The updated job state dict.

    Raises:
        ValueError: If the step is not pending human approval, has no model
            approval, or the review decision is not APPROVED.
    """
    pending = state.get("pending_human_approval_for")
    if pending != step:
        raise ValueError(f"Step {step!r} is not pending human approval. Current pending: {pending!r}")
    if step not in state.setdefault("model_approved_steps", []):
        raise ValueError(f"Step {step!r} does not have recorded model approval.")
    review_state = state.setdefault("review_state", default_review_state())
    if review_state.get("review_decision") != "APPROVED":
        raise ValueError(f"Step {step!r} cannot be human-approved before review_decision=APPROVED.")

    state.setdefault("human_approvals", {})[step] = {
        "status": "APPROVED", "approved_at": now_iso(), "approved_by": "human",
    }
    review_state["human_decision"] = "APPROVED"
    review_state["human_decided_at"] = now_iso()
    review_state["human_actor"] = "human"
    review_state["final_decision"] = "APPROVED"
    review_state["final_decision_source"] = "HUMAN"

    # Update the main document's Status line on approval
    target_artifact, new_status = _resolve_approval_target_artifact(
        group_name=group_name, step=step, group_cfg=group_cfg, state=state,
    )
    if target_artifact:
        artifact_path = state.get("artifacts", {}).get(target_artifact)
        if artifact_path:
            _update_document_status(file_path=artifact_path, new_status=new_status)

    completed_steps = state.setdefault("completed_steps", [])

    if group_name == "initiative_intake_v1" and step == "review_pre_init":
        _promote_pre_init_to_init(state)
        state["completed_steps"] = list(dict.fromkeys(completed_steps + [step]))
        state["pending_human_approval_for"] = None
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
        save_job(group_name, state["job_id"], state)
        # Send notification for workflow completion
        send_workflow_notification("COMPLETED", dict(state))
        return state

    state["completed_steps"] = list(dict.fromkeys(completed_steps + [step]))
    state["pending_human_approval_for"] = None

    if group_name == "delivery_planning_v1" and step == "review_task_graph":
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
        save_job(group_name, state["job_id"], state)
        # Send notification for workflow completion
        send_workflow_notification("COMPLETED", dict(state))
        return state

    next_step = get_next_step_skipping_refine_replan(group_cfg, list(state.get("completed_steps", [])))
    if next_step is None:
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
        save_job(group_name, state["job_id"], state)
        # Send notification for workflow completion
        send_workflow_notification("COMPLETED", dict(state))
    else:
        set_job_status(state, "IN_PROGRESS")
        state["current_step"] = next_step
    save_job(group_name, state["job_id"], state)
    return state


def _get_effective_limit(state: dict[str, Any], on_reject_refine: dict[str, Any]) -> int:
    """Get the effective cumulative refinement limit.

    Combines base max_refinements with any extensions from refinement_extensions.

    Args:
        state: Job state dict.
        on_reject_refine: The on_reject_refine configuration dict.

    Returns:
        The effective limit (base + extensions).
    """
    base_limit = int(on_reject_refine.get("max_refinements", 0))
    extensions = state.get("refinement_extensions", [])
    extensions_sum = sum(ext.get("additional_allowance", 0) for ext in extensions)
    return base_limit + extensions_sum


def reject_step(
    *, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str,
) -> dict[str, Any]:
    """Reject a step pending human approval, triggering on_reject_refine routing.

    Clears the approval state, records the rejection, and either routes to
    the configured refine step (activating a loop context) or marks the job
    as FAILED if no refine route exists.

    Args:
        group_name: Workflow template group name.
        group_cfg: Full workflow configuration dict.
        state: Mutable job state dict.
        step: Name of the step to reject.

    Returns:
        The updated job state dict.

    Raises:
        ValueError: If the step is not pending human approval.
    """
    pending = state.get("pending_human_approval_for")
    if pending != step:
        raise ValueError(f"Step {step!r} is not pending human approval. Current pending: {pending!r}")

    step_cfg = group_cfg.get("step_configs", {}).get(step, {})
    on_reject_refine = step_cfg.get("on_reject_refine") or {}

    # Record rejection in review state
    review_state = state.setdefault("review_state", default_review_state())
    review_state["human_decision"] = "REJECTED"
    review_state["human_decided_at"] = now_iso()
    review_state["human_actor"] = "human"
    review_state["final_decision"] = "REJECTED"
    review_state["final_decision_source"] = "HUMAN"

    # Clear approval state
    state["pending_human_approval_for"] = None
    state.setdefault("human_approvals", {}).pop(step, None)

    # Increment BOTH reject_counts (existing) and human_reject_counts (new)
    state.setdefault("reject_counts", {})[step] = state.get("reject_counts", {}).get(step, 0) + 1
    human_reject_counts = state.setdefault("human_reject_counts", {})
    human_reject_counts[step] = human_reject_counts.get(step, 0) + 1
    current_human_count = human_reject_counts[step]

    if on_reject_refine.get("step") and on_reject_refine.get("artifact"):
        # ── Human rejection limit (opt-in, checked FIRST) ──
        max_human_rejects = int(on_reject_refine.get("max_human_rejections", 0))
        if max_human_rejects > 0 and current_human_count > max_human_rejects:
            human_exhausted_code = on_reject_refine.get("human_exhausted_failure_code") or "HUMAN_REJECTION_EXHAUSTED"
            set_last_failure(
                state=state,
                failure_class=on_reject_refine.get("exhausted_failure_class") or "HUMAN_RETRY_REQUIRED",
                failure_code=human_exhausted_code,
                failure_reason=f"Human rejected {current_human_count} times (max {max_human_rejects}) for step {step!r}.",
                failure_source="human_reject",
                step=step,
            )
            set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
            state["pending_intervention_for"] = step
            state["current_step"] = step
        # ── Cumulative refinement limit (checked SECOND, only for plan_first_review_v1) ──
        elif group_name == "plan_first_review_v1":
            effective_limit = _get_effective_limit(state, on_reject_refine)
            current_revision = state.get("plan_revision", 1)
            if effective_limit > 0 and current_revision > effective_limit:
                cumulative_exhausted_code = on_reject_refine.get("exhausted_failure_code") or "PLAN_REFINEMENT_EXHAUSTED"
                set_last_failure(
                    state=state,
                    failure_class=on_reject_refine.get("exhausted_failure_class") or "HUMAN_RETRY_REQUIRED",
                    failure_code=cumulative_exhausted_code,
                    failure_reason=f"Cumulative refinements ({current_revision}) exceeded effective limit ({effective_limit}) for step {step!r}.",
                    failure_source="human_reject",
                    step=step,
                )
                set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
                state["pending_intervention_for"] = step
                state["current_step"] = step
            else:
                # ── Existing model rejection limit (PRESERVED) ──
                max_iter = int(on_reject_refine.get("max_iterations", 2))
                current_count = state["reject_counts"][step]
                if current_count > max_iter:
                    exhausted_code = on_reject_refine.get("exhausted_failure_code") or "REFINEMENT_EXHAUSTED"
                    set_last_failure(
                        state=state,
                        failure_class=on_reject_refine.get("exhausted_failure_class") or "HUMAN_RETRY_REQUIRED",
                        failure_code=exhausted_code,
                        failure_reason=f"Reject count ({current_count}) exceeded max iterations ({max_iter}) for step {step!r}.",
                        failure_source="human_reject",
                        step=step,
                    )
                    set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
                    state["pending_intervention_for"] = step
                    state["current_step"] = step
                else:
                    # Activate refine loop
                    review_file = state.get("artifacts", {}).get(on_reject_refine["artifact"])
                    state["loop_context"] = default_loop_context(
                        active=True,
                        loop_step=step,
                        refine_step=on_reject_refine["step"],
                        target_artifact=on_reject_refine["artifact"],
                        review_file=review_file,
                        iteration=current_count,
                    )
                    state["current_step"] = on_reject_refine["step"]
                    set_job_status(state, "IN_PROGRESS")
        else:
            # ── Existing model rejection limit (PRESERVED, for non-plan_first_review_v1 workflows) ──
            max_iter = int(on_reject_refine.get("max_iterations", 2))
            current_count = state["reject_counts"][step]
            if current_count > max_iter:
                exhausted_code = on_reject_refine.get("exhausted_failure_code") or "REFINEMENT_EXHAUSTED"
                set_last_failure(
                    state=state,
                    failure_class=on_reject_refine.get("exhausted_failure_class") or "HUMAN_RETRY_REQUIRED",
                    failure_code=exhausted_code,
                    failure_reason=f"Reject count ({current_count}) exceeded max iterations ({max_iter}) for step {step!r}.",
                    failure_source="human_reject",
                    step=step,
                )
                set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
                state["pending_intervention_for"] = step
                state["current_step"] = step
            else:
                # Activate refine loop
                review_file = state.get("artifacts", {}).get(on_reject_refine["artifact"])
                state["loop_context"] = default_loop_context(
                    active=True,
                    loop_step=step,
                    refine_step=on_reject_refine["step"],
                    target_artifact=on_reject_refine["artifact"],
                    review_file=review_file,
                    iteration=current_count,
                )
                state["current_step"] = on_reject_refine["step"]
                set_job_status(state, "IN_PROGRESS")
    else:
        # No refine route — mark as failed
        set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
        state["pending_intervention_for"] = step
        state["current_step"] = step
        set_last_failure(
            state=state,
            failure_class="HUMAN_RETRY_REQUIRED",
            failure_code="HUMAN_REJECTED",
            failure_reason=f"Step {step!r} rejected by human. No on_reject_refine route configured.",
            failure_source="human_reject",
            step=step,
        )

    save_job(group_name, state["job_id"], state)
    return state


def force_approve_step(
    *, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str,
) -> dict[str, Any]:
    """Force-approve a step regardless of its current review decision.

    Unlike ``approve_step``, this does not require the step to be pending
    human approval or to have a model approval.  It sets the review decision
    to APPROVED, records a human approval with ``force_override: True``,
    clears failure state, and advances to the next step.

    Args:
        group_name: Workflow template group name.
        group_cfg: Full workflow configuration dict.
        state: Mutable job state dict.
        step: Name of the step to force-approve.

    Returns:
        The updated job state dict.

    Raises:
        ValueError: If the step is not defined in the workflow, or if the job is STOPPED_ARCHIVED.
    """
    # Guard: STOPPED_ARCHIVED is terminal — cannot be reactivated by force approval
    if get_job_status(state) == "STOPPED_ARCHIVED":
        raise ValueError(f"Cannot force-approve step: job {state['job_id']!r} is STOPPED_ARCHIVED (terminal).")

    step_cfg = group_cfg["step_configs"].get(step)
    if not step_cfg:
        raise ValueError(f"Step {step!r} is not defined for template group {group_name!r}")

    review_state = state.setdefault("review_state", default_review_state())
    review_state["review_decision"] = "APPROVED"
    review_state["review_decided_at"] = now_iso()
    review_state["human_decision"] = "APPROVED"
    review_state["human_decided_at"] = now_iso()
    review_state["human_actor"] = "human"
    review_state["final_decision"] = "APPROVED"
    review_state["final_decision_source"] = "HUMAN"

    state.setdefault("human_approvals", {})[step] = {
        "status": "APPROVED", "approved_at": now_iso(), "approved_by": "human", "force_override": True,
    }
    model_approved_steps = state.setdefault("model_approved_steps", [])
    if step not in model_approved_steps:
        model_approved_steps.append(step)

    # Update the main document's Status line on approval
    target_artifact, new_status = _resolve_approval_target_artifact(
        group_name=group_name, step=step, group_cfg=group_cfg, state=state,
    )
    if target_artifact:
        artifact_path = state.get("artifacts", {}).get(target_artifact)
        if artifact_path:
            _update_document_status(file_path=artifact_path, new_status=new_status)

    completed_steps = state.setdefault("completed_steps", [])
    state["completed_steps"] = list(dict.fromkeys(completed_steps + [step]))
    state["pending_human_approval_for"] = None
    clear_last_failure(state)

    if group_name == "initiative_intake_v1" and step == "review_pre_init":
        _promote_pre_init_to_init(state)
        state["pending_human_approval_for"] = None
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
        save_job(group_name, state["job_id"], state)
        # Send notification for workflow completion
        send_workflow_notification("COMPLETED", dict(state))
        return state

    if group_name == "delivery_planning_v1" and step == "review_task_graph":
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
        save_job(group_name, state["job_id"], state)
        # Send notification for workflow completion
        send_workflow_notification("COMPLETED", dict(state))
        return state

    next_step = get_next_step_skipping_refine_replan(group_cfg, list(state.get("completed_steps", [])))
    if next_step is None:
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
        save_job(group_name, state["job_id"], state)
        # Send notification for workflow completion
        send_workflow_notification("COMPLETED", dict(state))
    else:
        set_job_status(state, "IN_PROGRESS")
        state["current_step"] = next_step
    save_job(group_name, state["job_id"], state)
    return state


def resume_step(
    *, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str,
) -> dict[str, Any]:
    """Force-approve a step that is waiting for intervention or max-retried.

    Records human approval (with ``resume: True``), clears all failure state
    (loop context, pending intervention, last failure), and advances to the
    next step in the workflow.  If no next step exists the job is marked
    COMPLETED.

    Use this when the user has investigated and fixed the root cause
    (INTERVENTION) or decided the content is acceptable despite rejections
    (MAXRETRIED) and wants to move forward without re-executing the step.

    Args:
        group_name: Workflow template group name.
        group_cfg: Full workflow configuration dict.
        state: Mutable job state dict.
        step: Name of the step to resume.

    Returns:
        The updated job state dict.

    Raises:
        ValueError: If the job status is not WAITING_FOR_HUMAN_INTERVENTION
            or WAITING_FOR_HUMAN_MAXRETRIED.
    """
    current_status = get_job_status(state)
    if current_status not in {"WAITING_FOR_HUMAN_INTERVENTION", "WAITING_FOR_HUMAN_MAXRETRIED"}:
        raise ValueError(
            f"Step {step!r} cannot be resumed: job status is {current_status!r}, "
            f"expected WAITING_FOR_HUMAN_INTERVENTION or WAITING_FOR_HUMAN_MAXRETRIED."
        )

    state.setdefault("human_approvals", {})[step] = {
        "status": "APPROVED", "approved_at": now_iso(), "approved_by": "human", "resume": True,
    }

    review_state = state.setdefault("review_state", default_review_state())
    review_state["human_decision"] = "APPROVED"
    review_state["human_decided_at"] = now_iso()
    review_state["human_actor"] = "human"
    review_state["final_decision"] = "APPROVED"
    review_state["final_decision_source"] = "HUMAN"

    completed_steps = state.setdefault("completed_steps", [])
    state["completed_steps"] = list(dict.fromkeys(completed_steps + [step]))
    state["pending_intervention_for"] = None
    state["pending_human_approval_for"] = None
    state["loop_context"] = default_loop_context()
    clear_last_failure(state)

    next_step = get_next_step_skipping_refine_replan(group_cfg, list(state.get("completed_steps", [])))
    if next_step is None:
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
        save_job(group_name, state["job_id"], state)
        send_workflow_notification("COMPLETED", dict(state))
    else:
        set_job_status(state, "IN_PROGRESS")
        state["current_step"] = next_step
    save_job(group_name, state["job_id"], state)
    return state


def retry_step(
    *, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str,
) -> dict[str, Any]:
    """Reset failure and reject state so the step can be re-executed.

    Clears the reject count, auto/human retry counts, loop context, replan
    context, and last failure for the step.  The job returns to IN_PROGRESS
    with ``current_step`` unchanged so the daemon or next manual invocation
    picks up the same step with a fresh attempt budget.

    Unlike ``resume_step``, this does NOT advance to the next step and does
    NOT mark the step as completed — it gives the coder another chance to
    produce an acceptable result.

    Args:
        group_name: Workflow template group name.
        group_cfg: Full workflow configuration dict (unused but kept for
            API consistency with ``resume_step`` and ``approve_step``).
        state: Mutable job state dict.
        step: Name of the step to retry.

    Returns:
        The updated job state dict.

    Raises:
        ValueError: If the job status is not WAITING_FOR_HUMAN_INTERVENTION
            or WAITING_FOR_HUMAN_MAXRETRIED.
    """
    current_status = get_job_status(state)
    if current_status not in {"WAITING_FOR_HUMAN_INTERVENTION", "WAITING_FOR_HUMAN_MAXRETRIED"}:
        raise ValueError(
            f"Step {step!r} cannot be retried: job status is {current_status!r}, "
            f"expected WAITING_FOR_HUMAN_INTERVENTION or WAITING_FOR_HUMAN_MAXRETRIED."
        )

    state.setdefault("reject_counts", {})[step] = 0
    state.setdefault("auto_retry_count_by_step", {})[step] = 0
    state.setdefault("human_retry_count_by_step", {})[step] = 0
    state.setdefault("human_reject_counts", {}).pop(step, None)
    state["pending_intervention_for"] = None
    state["pending_human_approval_for"] = None
    state["loop_context"] = default_loop_context()
    state["replan_context"] = default_replan_context()
    clear_last_failure(state)

    set_job_status(state, "IN_PROGRESS")
    state["current_step"] = step
    save_job(group_name, state["job_id"], state)
    return state


def extend_refinement_limit(
    *, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any],
    additional_allowance: int, reason: str = "",
) -> dict[str, Any]:
    """Extend the cumulative refinement limit and reset per-step counters.

    Used when the workflow hits the cumulative refinement limit (max_refinements)
    but the user wants to continue. Adds additional_allowance to the effective
    limit, resets reject_counts for the review step, and reconstructs loop context
    to resume the refine loop.

    Only valid for plan_first_review_v1 workflow.

    Args:
        group_name: Workflow template group name.
        group_cfg: Full workflow configuration dict.
        state: Mutable job state dict.
        additional_allowance: Number of additional refinements to allow.
        reason: Optional reason for the extension (for audit trail).

    Returns:
        The updated job state dict.

    Raises:
        ValueError: If workflow is not plan_first_review_v1, or if job status
            is not WAITING_FOR_HUMAN_INTERVENTION.
    """
    if group_name != "plan_first_review_v1":
        raise ValueError(
            f"extend_refinement_limit is only valid for plan_first_review_v1, not {group_name!r}"
        )

    current_status = get_job_status(state)
    if current_status != "WAITING_FOR_HUMAN_INTERVENTION":
        raise ValueError(
            f"Cannot extend refinement limit: job status is {current_status!r}, "
            f"expected WAITING_FOR_HUMAN_INTERVENTION."
        )

    # Find the review step (codex_review) from the workflow config
    step_configs = group_cfg.get("step_configs", {})
    review_step = None
    on_reject_refine_cfg = None
    for step_name, cfg in step_configs.items():
        if "on_reject_refine" in cfg:
            review_step = step_name
            on_reject_refine_cfg = cfg["on_reject_refine"]
            break

    if review_step is None:
        raise ValueError(
            f"Workflow {group_name!r} has no step with on_reject_refine configuration"
        )

    # ── Validate positive allowance ──
    if additional_allowance <= 0:
        raise ValueError(
            f"additional_allowance must be positive, got {additional_allowance}"
        )

    # ── Validate pause was caused by cumulative exhaustion ──
    expected_code = on_reject_refine_cfg.get("exhausted_failure_code") or "PLAN_REFINEMENT_EXHAUSTED"
    actual_code = state.get("last_failure_code")
    if actual_code != expected_code:
        raise ValueError(
            f"Cannot extend refinement limit: last_failure_code is {actual_code!r}, "
            f"expected {expected_code!r} (cumulative exhaustion)."
        )

    # ── Validate resulting limit does not exceed max_ceiling ──
    max_ceiling = int(on_reject_refine_cfg.get("max_ceiling", 20))
    prospective_limit = _get_effective_limit(state, on_reject_refine_cfg) + additional_allowance
    if prospective_limit > max_ceiling:
        raise ValueError(
            f"Cannot extend refinement limit: prospective effective limit ({prospective_limit}) "
            f"would exceed max_ceiling ({max_ceiling})."
        )

    # Record the extension in refinement_extensions list
    extensions = state.setdefault("refinement_extensions", [])
    extensions.append({
        "additional_allowance": additional_allowance,
        "reason": reason,
        "granted_at": now_iso(),
    })

    # Reset per-step reject counter to allow continuation
    state.setdefault("reject_counts", {})[review_step] = 0

    # Reconstruct loop context to resume the refine loop
    refine_step = on_reject_refine_cfg.get("step", "")
    target_artifact = on_reject_refine_cfg.get("artifact", "")
    state["loop_context"] = default_loop_context(
        active=True,
        loop_step=review_step,
        refine_step=refine_step,
        target_artifact=target_artifact,
    )

    # Clear intervention state and transition to refine step
    state["pending_intervention_for"] = None
    state["pending_human_approval_for"] = None
    clear_last_failure(state)
    set_job_status(state, "IN_PROGRESS")
    state["current_step"] = refine_step

    save_job(group_name, state["job_id"], state)
    return state


def stop_and_archive(
    *,
    group_name: str,
    state: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    """Stop and archive a job (terminal status).

    Marks the job as STOPPED_ARCHIVED, preserving all artifacts.

    Args:
        group_name: Workflow template group name.
        state: Mutable job state dict.
        reason: Reason for stopping (for audit trail).

    Returns:
        The updated job state dict.
    """
    set_job_status(state, "STOPPED_ARCHIVED")
    state["stop_reason"] = reason
    state["stopped_at"] = now_iso()

    # Clear any pending interventions or approvals
    state["pending_intervention_for"] = None
    state["pending_human_approval_for"] = None

    # Deactivate loop context
    if "loop_context" in state:
        state["loop_context"]["active"] = False

    save_job(group_name, state["job_id"], state)
    return state


def execute_baseline_transaction(
    *,
    group_name: str,
    job_id: str,
    request_bytes: bytes,
    request_id: str | None = None,
    project_root: Path | None = None,
    reason: str | None = None,  # Change reason for history
    _authoritative_state: dict | None = None,  # For testing only - skips disk load
    _preferred_operation_id: str | None = None,  # Compatibility callers may supply one
    _committed_state_out: dict | None = None,  # For testing only - receives committed state
    _expected_ending_baseline: int | None = None,  # Legacy authority check
    _expected_new_baseline: int | None = None,  # Legacy authority check
) -> dict:
    """Execute a baseline transaction with full Phase B safety guarantees.

    This is the shared locked entry point for all baseline transactions.
    It provides:
    - Stable request identity (auto-generated if not provided)
    - Job-level locking
    - Authoritative raw state reload (unless _authoritative_state provided for testing)
    - Staging → publication → state commit flow
    - Complete immutable validation
    - Receipt writing and repair
    - Caller state isolation

    Returns the transaction result dict with status, baseline, request_id, operation_id.
    Raises TransactionConflictError on validation failure.
    """
    import copy
    from .constants import (
        ARTIFACT_PATH_BASELINE_DIR,
        ARTIFACT_PATH_BASELINE_REQUEST,
    )

    if project_root is None:
        project_root = PROJECT_ROOT

    # Generate stable request identity if not provided
    if request_id is None:
        request_id = f"req_{uuid.uuid4().hex[:16]}"

    # Compute request hash from actual bytes
    request_hash = hashlib.sha256(request_bytes).hexdigest()

    # Track stable identity + phase so failures can expose a reusable retry id.
    operation_id = _preferred_operation_id
    phase = "init"

    # Acquire job lock inside the identity/error boundary so a lock failure still
    # exposes the generated retry identity/phase.
    lock_path = _get_job_lock_path(group_name, job_id)
    lock_acquired = False

    try:
        _acquire_lock(lock_path)
        lock_acquired = True

        # Authoritative raw reload - ALWAYS from disk in production
        # _authoritative_state is ONLY for testing with mocked persistence
        if _authoritative_state is not None:
            # Testing path: use provided state
            authoritative_state = copy.deepcopy(_authoritative_state)
        else:
            # Production path: always reload from disk under lock
            authoritative_state = load_job(group_name, job_id)

        # Isolate working state from caller IMMEDIATELY
        working_state = copy.deepcopy(authoritative_state)
        phase = "reloaded"

        # Freeze the untouched authoritative raw ending state BEFORE any default,
        # ledger, reset or transition initialization is applied to working_state.
        raw_ending_snapshot = copy.deepcopy(authoritative_state)

        # Get commit ledger from WORKING state (not authoritative)
        commit_ledger = working_state.setdefault("baseline_commits", {})
        if not isinstance(commit_ledger, dict):
            raise TransactionConflictError("baseline_commits ledger is not an object")

        # Check for committed replay FIRST (before archived check).
        # Membership, not truthiness: a present empty/null/malformed value is
        # corruption of the idempotency authority, not an absent request.
        if request_id in commit_ledger:
            existing_commit = commit_ledger[request_id]
            if not isinstance(existing_commit, dict) or not existing_commit:
                raise TransactionConflictError(
                    f"Malformed commit ledger entry for request_id {request_id!r}; "
                    f"refusing to create another operation"
                )
            phase = "replay"
            # Committed replay - validate and return
            return _handle_committed_replay(
                request_id=request_id,
                request_bytes=request_bytes,
                request_hash=request_hash,
                existing_commit=existing_commit,
                authoritative_state=working_state,  # Use working state
                group_name=group_name,
                job_id=job_id,
                project_root=project_root,
            )

        # Guard: STOPPED_ARCHIVED is terminal for NEW transactions
        if get_job_status(working_state) == "STOPPED_ARCHIVED":
            raise TransactionConflictError(
                f"Job {job_id!r} is STOPPED_ARCHIVED (terminal). Cannot start new transaction."
            )

        # Discover existing evidence in trusted namespace
        planning_folder = get_planning_folder(working_state)
        ending_baseline = int(working_state.get("requirements_baseline", 1))
        new_baseline = ending_baseline + 1

        # Legacy authority check: reject a stale caller transition against the
        # authoritative (reloaded) baseline before any mutation.
        if _expected_ending_baseline is not None and ending_baseline != _expected_ending_baseline:
            raise TransactionConflictError(
                f"Authoritative ending baseline {ending_baseline} != caller-expected "
                f"{_expected_ending_baseline}; caller state is stale"
            )
        if _expected_new_baseline is not None and new_baseline != _expected_new_baseline:
            raise TransactionConflictError(
                f"Authoritative new baseline {new_baseline} != caller-expected "
                f"{_expected_new_baseline}; caller state is stale"
            )
        phase = "discovered"

        # Derive paths
        planning_path = project_root / planning_folder
        final_dir = planning_path / f"baseline_{new_baseline:02d}"

        # Complete trusted-namespace discovery BEFORE selecting any branch.
        # Inspect ALL staging candidates (ownership + completeness) even when a
        # matching final exists, so ambiguity cannot be hidden.
        staging_candidates: list[tuple[Path, dict]] = []
        for candidate in sorted(planning_path.glob(".staging_*")):
            if not candidate.is_dir():
                continue
            candidate_op_path = candidate / "operation.json"
            if not candidate_op_path.exists():
                raise TransactionConflictError(
                    f"Incomplete staging evidence: {candidate} has no operation.json - user intervention required"
                )
            try:
                candidate_op = json.loads(candidate_op_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                raise TransactionConflictError(
                    f"Staging has corrupt operation.json: {candidate} - user intervention required"
                )
            if candidate_op.get("group_name") != group_name:
                raise TransactionConflictError(
                    f"Staging in current namespace has different group_name: {candidate_op.get('group_name')} != {group_name}"
                )
            if candidate_op.get("job_id") != job_id:
                raise TransactionConflictError(
                    f"Staging in current namespace has different job_id: {candidate_op.get('job_id')} != {job_id}"
                )
            staging_candidates.append((candidate, candidate_op))

        if len(staging_candidates) > 1:
            raise TransactionConflictError(
                f"Multiple staging directories for job {job_id!r}: "
                f"{[str(d) for d, _ in staging_candidates]} - user intervention required"
            )

        # Inspect the final set. Simultaneous final + staging evidence is
        # ambiguous and must be rejected before any mutation.
        if final_dir.exists():
            if staging_candidates:
                raise TransactionConflictError(
                    f"Ambiguous evidence: final {final_dir} coexists with staging "
                    f"{[str(d) for d, _ in staging_candidates]} - user intervention required"
                )
            final_op_path = final_dir / "operation.json"
            if not final_op_path.exists():
                raise TransactionConflictError(
                    f"Final evidence incomplete: {final_dir} has no operation.json"
                )
            final_op = json.loads(final_op_path.read_text(encoding="utf-8"))
            if final_op.get("request_id") == request_id:
                if request_id in commit_ledger:
                    return commit_ledger[request_id].get("result", {})
                return _adopt_published_final(
                    final_dir=final_dir,
                    final_op=final_op,
                    working_state=working_state,
                    raw_ending_state=raw_ending_snapshot,
                    commit_ledger=commit_ledger,
                    group_name=group_name,
                    job_id=job_id,
                    request_bytes=request_bytes,
                    request_hash=request_hash,
                    reason=reason,
                    project_root=project_root,
                )
            raise TransactionConflictError(
                f"Final directory has conflicting request_id: {final_op.get('request_id')} != {request_id}"
            )

        # Select the single staging candidate (resume) or none (create new).
        staging_dir = None
        operation_id = None
        for candidate, candidate_op in staging_candidates:
            if candidate_op.get("request_id") != request_id:
                raise TransactionConflictError(
                    f"Staging request_id {candidate_op.get('request_id')} != incoming request_id {request_id}"
                )
            staging_request_path = candidate / "request.md"
            if not staging_request_path.exists():
                raise TransactionConflictError(
                    f"Incomplete staging evidence: {candidate} has no request.md - user intervention required"
                )
            persisted_staging_bytes = staging_request_path.read_bytes()
            if persisted_staging_bytes != request_bytes:
                raise TransactionConflictError(
                    "Staging request bytes differ from incoming request bytes"
                )
            persisted_staging_hash = hashlib.sha256(persisted_staging_bytes).hexdigest()
            if persisted_staging_hash != candidate_op.get("request_hash"):
                raise TransactionConflictError(
                    "Staging request hash != operation request_hash"
                )
            staging_dir = candidate
            operation_id = candidate_op["operation_id"]

        # Capture the untouched raw ending snapshot BEFORE any defaults/transition.
        ending_snapshot = raw_ending_snapshot
        is_new_staging = staging_dir is None

        if is_new_staging:
            # Build NEW immutable operation evidence only on this path.
            operation_id = _preferred_operation_id or f"op_{uuid.uuid4().hex[:12]}"
            staging_dir = planning_path / f".staging_{operation_id}"
            staging_dir.mkdir(parents=True, exist_ok=True)

            (staging_dir / "request.md").write_bytes(request_bytes)

            baseline_dir_rel = ARTIFACT_PATH_BASELINE_DIR(planning_folder, new_baseline)
            canonical_paths = {
                "request": ARTIFACT_PATH_BASELINE_REQUEST(planning_folder, new_baseline),
                "operation": f"{baseline_dir_rel}/operation.json",
                "ending_snapshot": f"{baseline_dir_rel}/ending_snapshot.json",
                "receipt": f"{baseline_dir_rel}/receipt.json",
            }

            staging_op = {
                "operation_id": operation_id,
                "request_id": request_id,
                "group_name": group_name,
                "job_id": job_id,
                "ending_baseline": ending_baseline,
                "new_baseline": new_baseline,
                "request_hash": request_hash,
                "canonical_paths": canonical_paths,
            }

            # Freeze the untouched ending snapshot into staging before publication.
            staging_snapshot_path = staging_dir / "ending_snapshot.json"
            staging_snapshot_path.write_text(
                json.dumps(ending_snapshot, indent=2), encoding="utf-8"
            )
            snapshot_bytes = staging_snapshot_path.read_bytes()
            snapshot_hash = hashlib.sha256(snapshot_bytes).hexdigest()
            ending_state_identity = _semantic_ending_identity(
                json.loads(snapshot_bytes.decode("utf-8"))
            )
            staging_op["ending_snapshot_hash"] = snapshot_hash
            staging_op["ending_state_identity"] = ending_state_identity

            op_for_digest = {k: v for k, v in staging_op.items() if k != "manifest_hash"}
            manifest_hash = hashlib.sha256(json.dumps(op_for_digest, sort_keys=True).encode()).hexdigest()
            staging_op["manifest_hash"] = manifest_hash

            staging_op_path = staging_dir / "operation.json"
            staging_op_path.write_text(json.dumps(staging_op, indent=2), encoding="utf-8")
        else:
            # RESUME: immutable evidence is already frozen. Validate it exactly as
            # replay/adoption would and never normalize or rewrite its digests.
            staging_op = json.loads(
                (staging_dir / "operation.json").read_text(encoding="utf-8")
            )
            staging_op = validate_immutable_operation(
                existing_op=staging_op,
                operation_id=operation_id,
                request_id=request_id,
                request_bytes=request_bytes,
                incoming_request_hash=request_hash,
                ending_baseline=ending_baseline,
                actual_dir=staging_dir,
                state=working_state,
                group_name=group_name,
                job_id=job_id,
                project_root=project_root,
                phase="staging",
            )
            snapshot_hash = staging_op["ending_snapshot_hash"]
            ending_state_identity = staging_op["ending_state_identity"]
            manifest_hash = staging_op["manifest_hash"]

            frozen = json.loads(
                (staging_dir / "ending_snapshot.json").read_text(encoding="utf-8")
            )
            if _semantic_ending_identity(frozen) != _semantic_ending_identity(ending_snapshot):
                raise TransactionConflictError(
                    "Staging ending state differs from frozen ending snapshot"
                )

        phase = "staging"

        # NOW publish: rename staging to final (complete immutable evidence)
        staging_dir.rename(final_dir)
        phase = "published"

        # Generate committed_at timestamp ONCE
        committed_at = now_iso()

        # Use the staging_op (now in final_dir) as the operation
        operation = staging_op

        # Build result with required timestamp
        result = {
            "status": "committed",
            "baseline": new_baseline,
            "operation_id": operation_id,
            "request_id": request_id,
            "committed_at": committed_at,
        }

        # Build commit record (envelope) with same timestamp
        commit_record = {
            "request_id": request_id,
            "operation_id": operation_id,
            "manifest_hash": manifest_hash,
            "operation": operation,
            "result": result,
            "committed_at": committed_at,
        }

        # Update working state (isolated from caller)
        working_state["requirements_baseline"] = new_baseline

        # Update artifact pointers to new baseline (part of durable commit)
        from .constants import (
            ARTIFACT_PATH_BASELINE_REQUEST,
            ARTIFACT_PATH_REQUIREMENTS,
            ARTIFACT_PATH_QWEN_PLAN,
            ARTIFACT_PATH_CODEX_REVIEW,
        )
        working_state.setdefault("artifacts", {})
        working_state["artifacts"]["RAW_REQUEST_FILE"] = str(
            project_root / ARTIFACT_PATH_BASELINE_REQUEST(planning_folder, new_baseline)
        )
        working_state["artifacts"]["REQUIREMENTS_FILE"] = str(
            project_root / ARTIFACT_PATH_REQUIREMENTS(planning_folder, new_baseline)
        )
        working_state["artifacts"]["QWEN_PLAN_FILE"] = str(
            project_root / ARTIFACT_PATH_QWEN_PLAN(planning_folder, revision=1, baseline=new_baseline)
        )
        working_state["artifacts"]["CODEX_REVIEW_FILE"] = str(
            project_root / ARTIFACT_PATH_CODEX_REVIEW(planning_folder, revision=1, baseline=new_baseline)
        )

        # Record change history (part of durable commit)
        if reason:
            working_state.setdefault("change_history", []).append({
                "baseline": new_baseline,
                "reason": reason,
                "changed_at": committed_at,
            })

        # Record in commit ledger
        commit_ledger[request_id] = commit_record

        # Apply state reset for new baseline
        _apply_baseline_reset(working_state)

        # Single authoritative state commit
        save_job(group_name, job_id, working_state)
        phase = "committed"

        # Write receipt AFTER state commit
        receipt_path = final_dir / "receipt.json"
        receipt = _derive_receipt(operation, commit_record)
        receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

        # Test/compat hook: expose the committed working state to the caller
        # without mutating the authoritative source on failure.
        if _committed_state_out is not None:
            _committed_state_out.clear()
            _committed_state_out.update(copy.deepcopy(working_state))

        return result

    finally:
        # Expose stable retry identity + phase on failures (including persistence
        # errors raised after an auto-generated ID was created), while leaving
        # the original exception type/message intact.
        _exc = sys.exc_info()[1]
        if _exc is not None:
            try:
                if not getattr(_exc, "request_id", None):
                    _exc.request_id = request_id
                if getattr(_exc, "operation_id", None) is None:
                    _exc.operation_id = operation_id
                if not getattr(_exc, "phase", None):
                    _exc.phase = phase
            except Exception:
                pass
        # Release ONLY a lock this invocation actually acquired.
        if lock_acquired:
            _release_lock(lock_path)


def _handle_committed_replay(
    *,
    request_id: str,
    request_bytes: bytes,
    request_hash: str,
    existing_commit: dict,
    authoritative_state: dict,
    group_name: str,
    job_id: str,
    project_root: Path,
) -> dict:
    """Handle committed replay through the shared immutable validator.

    This is the single historical replay contract:
    1. Validate the complete phase-aware immutable validator (manifest, snapshot
       bytes/hash, semantic identity, canonical paths, ownership, baselines).
    2. Enforce required ledger/envelope/result schema and binding.
    3. Repair only the derived receipt, then return the original result.

    Current eligibility and current semantic ending state are NOT applied to a
    valid historical operation.
    """
    # 1. Required envelope schema (fail closed on malformed ledger values).
    if not isinstance(existing_commit, dict) or not existing_commit:
        raise TransactionConflictError(
            f"Malformed commit ledger entry for request_id {request_id!r}"
        )
    existing_op = existing_commit.get("operation")
    result = existing_commit.get("result")
    if not isinstance(existing_op, dict) or not existing_op:
        raise TransactionConflictError("Commit envelope missing operation object")
    if not isinstance(result, dict) or not result:
        raise TransactionConflictError("Commit envelope missing result object")

    # 2. Three-way identity binding: ledger key == envelope == operation.
    envelope_request_id = existing_commit.get("request_id")
    envelope_operation_id = existing_commit.get("operation_id")
    envelope_manifest_hash = existing_commit.get("manifest_hash")
    for _name, _value in (
        ("envelope request_id", envelope_request_id),
        ("envelope operation_id", envelope_operation_id),
        ("envelope manifest_hash", envelope_manifest_hash),
    ):
        if not isinstance(_value, str) or not _value:
            raise TransactionConflictError(
                f"{_name} must be a nonempty string: {_value!r}"
            )
    op_request_id = existing_op.get("request_id")
    if envelope_request_id != request_id:
        raise TransactionConflictError(
            f"Ledger key {request_id} != envelope request_id {envelope_request_id}"
        )
    if op_request_id != request_id:
        raise TransactionConflictError(
            f"Operation request_id {op_request_id} != ledger key {request_id}"
        )

    # 3. Envelope must be bound to the embedded operation.
    if envelope_operation_id != existing_op.get("operation_id"):
        raise TransactionConflictError(
            "Envelope operation_id != operation operation_id"
        )
    if envelope_manifest_hash != existing_op.get("manifest_hash"):
        raise TransactionConflictError(
            "Envelope manifest_hash != operation manifest_hash"
        )

    # 4. Resolve the historical final directory.
    planning_folder = get_planning_folder(authoritative_state)
    new_baseline = existing_op.get("new_baseline")
    if not isinstance(new_baseline, int) or isinstance(new_baseline, bool):
        raise TransactionConflictError(
            f"Operation new_baseline is not an integer: {new_baseline}"
        )
    final_dir = project_root / planning_folder / f"baseline_{new_baseline:02d}"
    if not final_dir.exists():
        raise TransactionConflictError(f"Final directory missing: {final_dir}")

    operation_path = final_dir / "operation.json"
    if not operation_path.exists():
        raise TransactionConflictError(f"Operation file missing: {operation_path}")
    disk_operation = json.loads(operation_path.read_text(encoding="utf-8"))

    # 5. Full embedded/disk operation equality (not selected fields).
    if disk_operation != existing_op:
        raise TransactionConflictError("Disk operation != committed operation")

    # 6. Complete phase-aware immutable validation (same contract as resume/adoption).
    validate_immutable_operation(
        existing_op=disk_operation,
        operation_id=disk_operation.get("operation_id"),
        request_id=request_id,
        request_bytes=request_bytes,
        incoming_request_hash=request_hash,
        ending_baseline=disk_operation.get("ending_baseline"),
        actual_dir=final_dir,
        state=authoritative_state,
        group_name=group_name,
        job_id=job_id,
        project_root=project_root,
        phase="committed_replay",
        commit_ledger={request_id: existing_commit},
    )

    # 7. Result schema + binding.
    if result.get("status") != "committed":
        raise TransactionConflictError(f"Result status != committed: {result.get('status')}")
    result_request_id = result.get("request_id")
    result_operation_id = result.get("operation_id")
    if not isinstance(result_request_id, str) or not result_request_id:
        raise TransactionConflictError(
            f"Result request_id must be a nonempty string: {result_request_id!r}"
        )
    if not isinstance(result_operation_id, str) or not result_operation_id:
        raise TransactionConflictError(
            f"Result operation_id must be a nonempty string: {result_operation_id!r}"
        )
    if result_request_id != request_id:
        raise TransactionConflictError("Result request_id != ledger key")
    if result_operation_id != disk_operation.get("operation_id"):
        raise TransactionConflictError("Result operation_id != committed operation_id")
    result_baseline = result.get("baseline")
    if not isinstance(result_baseline, int) or isinstance(result_baseline, bool):
        raise TransactionConflictError(
            f"Result baseline must be an exact integer: {result_baseline!r}"
        )
    if result_baseline <= 0:
        raise TransactionConflictError(
            f"Result baseline must be positive: {result_baseline}"
        )
    if result_baseline != new_baseline:
        raise TransactionConflictError("Result baseline != committed new_baseline")

    # 8. Timestamp schema + required agreement.
    committed_at = existing_commit.get("committed_at")
    result_committed_at = result.get("committed_at")
    _require_iso_timestamp(committed_at, "envelope committed_at")
    _require_iso_timestamp(result_committed_at, "result committed_at")
    if committed_at != result_committed_at:
        raise TransactionConflictError("Envelope committed_at != result committed_at")

    # 9. Repair only the derived receipt, then return the original result.
    receipt_path = final_dir / "receipt.json"
    repair_derived_receipt(disk_operation, existing_commit, receipt_path)

    return result


def _adopt_published_final(
    *,
    final_dir: Path,
    final_op: dict,
    working_state: dict,
    commit_ledger: dict,
    group_name: str,
    job_id: str,
    request_bytes: bytes,  # Incoming request bytes for validation
    request_hash: str,  # Incoming request hash for validation
    raw_ending_state: dict | None = None,  # Untouched authoritative raw ending state
    reason: str | None = None,  # Change reason for history
    project_root: Path | None = None,  # For artifact path resolution
) -> dict:
    """Adopt published final evidence that exists but is not in the commit ledger.

    This is the B06 recovery path after publication succeeded but state commit failed.
    Validates:
    - Incoming request bytes match the published final
    - Final evidence is complete and valid
    - Owner/job_id match

    Returns the transaction result.
    """
    from .constants import (
        ARTIFACT_PATH_BASELINE_DIR,
        ARTIFACT_PATH_BASELINE_REQUEST,
    )

    operation_id = final_op.get("operation_id")
    request_id = final_op.get("request_id")
    new_baseline = final_op.get("new_baseline")

    # Apply the SAME complete required validator as replay/resume BEFORE any
    # adoption mutation. This rejects corrupt manifest/identity/digest, changed
    # canonical authority, and schema/owner/baseline mismatches.
    if project_root is None:
        project_root = PROJECT_ROOT
    final_op = validate_immutable_operation(
        existing_op=final_op,
        operation_id=operation_id,
        request_id=request_id,
        request_bytes=request_bytes,
        incoming_request_hash=request_hash,
        ending_baseline=int(
            working_state.get("requirements_baseline", final_op.get("ending_baseline", 1))
        ),
        actual_dir=final_dir,
        state=working_state,
        group_name=group_name,
        job_id=job_id,
        project_root=project_root,
        phase="final",
    )

    # CRITICAL: Validate incoming request bytes match the published final
    # This prevents adopting a different request's published final
    if request_hash != final_op.get("request_hash"):
        raise TransactionConflictError(
            f"Incoming request hash {request_hash} != published final hash {final_op.get('request_hash')}"
        )

    # Also verify the actual bytes match (not just hash)
    persisted_request_bytes = (final_dir / "request.md").read_bytes()
    if request_bytes != persisted_request_bytes:
        raise TransactionConflictError(
            "Incoming request bytes differ from published final bytes"
        )

    # Validate owner/job_id match
    if final_op.get("group_name") != group_name:
        raise TransactionConflictError(
            f"Published final group_name {final_op.get('group_name')} != {group_name}"
        )
    if final_op.get("job_id") != job_id:
        raise TransactionConflictError(
            f"Published final job_id {final_op.get('job_id')} != {job_id}"
        )

    # Validate operation.json
    operation_path = final_dir / "operation.json"
    if not operation_path.exists():
        raise TransactionConflictError(f"Operation file missing: {operation_path}")

    # Validate request.md exists
    request_path = final_dir / "request.md"
    if not request_path.exists():
        raise TransactionConflictError(f"Request file missing: {request_path}")

    # Validate persisted request hash matches operation
    persisted_request_hash = hashlib.sha256(persisted_request_bytes).hexdigest()
    if persisted_request_hash != final_op.get("request_hash"):
        raise TransactionConflictError("Persisted request hash != operation hash")

    # Validate ending_snapshot.json exists and hash matches (REQUIRED)
    snapshot_path = final_dir / "ending_snapshot.json"
    if not snapshot_path.exists():
        raise TransactionConflictError(f"Snapshot file missing: {snapshot_path}")

    ending_snapshot_hash = final_op.get("ending_snapshot_hash")
    if not ending_snapshot_hash:
        raise TransactionConflictError("Published final operation missing ending_snapshot_hash")

    snapshot_hash = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    if snapshot_hash != ending_snapshot_hash:
        raise TransactionConflictError("Snapshot hash != operation ending_snapshot_hash")

    # Validate semantic ending state: the current authoritative ending state must
    # match the frozen ending snapshot. A changed ending state (for example a
    # changed pending_intervention_for) must conflict, not adopt.
    try:
        frozen_snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise TransactionConflictError("Frozen ending snapshot is corrupt")

    frozen_identity = _semantic_ending_identity(frozen_snapshot)
    recorded_identity = final_op.get("ending_state_identity")
    if recorded_identity and recorded_identity != frozen_identity:
        raise TransactionConflictError(
            "Operation ending_state_identity != frozen ending snapshot identity"
        )

    identity_source = raw_ending_state if raw_ending_state is not None else working_state
    current_identity = _semantic_ending_identity(identity_source)
    if current_identity != frozen_identity:
        raise TransactionConflictError(
            "Current ending state differs from published final ending snapshot"
        )

    # Validate manifest hash (REQUIRED)
    manifest_hash = final_op.get("manifest_hash")
    if not manifest_hash:
        raise TransactionConflictError("Published final operation missing manifest_hash")

    # Recompute and verify manifest
    op_for_digest = {k: v for k, v in final_op.items() if k != "manifest_hash"}
    computed_manifest = hashlib.sha256(json.dumps(op_for_digest, sort_keys=True).encode()).hexdigest()
    if computed_manifest != manifest_hash:
        raise TransactionConflictError("Computed manifest != published final manifest")

    # Generate committed_at timestamp
    committed_at = now_iso()

    # Build result
    result = {
        "status": "committed",
        "baseline": new_baseline,
        "operation_id": operation_id,
        "request_id": request_id,
        "committed_at": committed_at,
    }

    # Build commit record
    commit_record = {
        "request_id": request_id,
        "operation_id": operation_id,
        "manifest_hash": final_op.get("manifest_hash"),
        "operation": final_op,
        "result": result,
        "committed_at": committed_at,
    }

    # Update working state with routing/history (same as fresh publication)
    working_state["requirements_baseline"] = new_baseline

    # Update artifact pointers to new baseline (part of durable commit)
    if project_root is None:
        project_root = PROJECT_ROOT

    planning_folder = get_planning_folder(working_state)
    from .constants import (
        ARTIFACT_PATH_BASELINE_REQUEST,
        ARTIFACT_PATH_REQUIREMENTS,
        ARTIFACT_PATH_QWEN_PLAN,
        ARTIFACT_PATH_CODEX_REVIEW,
    )
    working_state.setdefault("artifacts", {})
    working_state["artifacts"]["RAW_REQUEST_FILE"] = str(
        project_root / ARTIFACT_PATH_BASELINE_REQUEST(planning_folder, new_baseline)
    )
    working_state["artifacts"]["REQUIREMENTS_FILE"] = str(
        project_root / ARTIFACT_PATH_REQUIREMENTS(planning_folder, new_baseline)
    )
    working_state["artifacts"]["QWEN_PLAN_FILE"] = str(
        project_root / ARTIFACT_PATH_QWEN_PLAN(planning_folder, revision=1, baseline=new_baseline)
    )
    working_state["artifacts"]["CODEX_REVIEW_FILE"] = str(
        project_root / ARTIFACT_PATH_CODEX_REVIEW(planning_folder, revision=1, baseline=new_baseline)
    )

    # Record change history (part of durable commit)
    if reason:
        working_state.setdefault("change_history", []).append({
            "baseline": new_baseline,
            "reason": reason,
            "changed_at": committed_at,
        })

    # Record in commit ledger
    commit_ledger[request_id] = commit_record

    # Apply state reset
    _apply_baseline_reset(working_state)

    # Save state
    save_job(group_name, job_id, working_state)

    # Repair receipt if needed
    receipt_path = final_dir / "receipt.json"
    repair_derived_receipt(final_op, commit_record, receipt_path)

    return result


def _apply_baseline_reset(state: dict) -> None:
    """Apply full state reset for new baseline."""
    # Preserve prepare_request in completed_steps, clear all other steps
    completed = state.get("completed_steps", [])
    state["completed_steps"] = ["prepare_request"] if "prepare_request" in completed else []

    # Clear model approvals
    state["model_approved_steps"] = []

    # Clear pending approvals
    state["pending_human_approval_for"] = None

    # Clear stale human approvals
    state["human_approvals"] = {}

    # Reset review state
    state["review_state"] = default_review_state()

    # Clear failure state
    state["last_failure_class"] = None
    state["last_failure_code"] = None
    state["last_failure_reason"] = None
    state["last_failure_source"] = None
    state["last_failure_step"] = None

    # Reset counters
    state["reject_counts"] = {}
    state["human_reject_counts"] = {}
    state["auto_retry_count_by_step"] = {}
    state["human_retry_count_by_step"] = {}
    state["refinement_extensions"] = []

    # Reset usage/coder/revision bookkeeping together (retain declared histories:
    # change_history, baseline_commits and published baseline directories).
    state["step_usage"] = {}
    state["usage_summary"] = default_usage_summary()
    state["step_coders"] = {}
    state["revision_completions"] = {}

    # Reset plan revision
    state["plan_revision"] = 1

    # Deactivate loop and replan contexts
    state["loop_context"] = default_loop_context()
    state["replan_context"] = default_replan_context()

    # Clear intervention state
    state["pending_intervention_for"] = None

    # Transition to formalize_requirements
    state["current_step"] = "formalize_requirements"
    set_job_status(state, "IN_PROGRESS")


def _get_job_lock_path(group_name: str, job_id: str) -> Path:
    """Get the lock file path for a job."""
    return JOBS_ROOT / group_name / job_id / ".lock"


# Module-level dictionary to track lock file descriptors
_lock_fds: dict[str, Any] = {}

# Bounded contention window for the no-fcntl fallback lock. A stale lock that
# cannot be proven dead fails loudly after this instead of blocking forever.
_LOCK_TIMEOUT_SECONDS = 30.0
_LOCK_RETRY_INTERVAL_SECONDS = 0.1


def _acquire_lock(lock_path: Path) -> None:
    """Acquire an exclusive lock on the lock file.

    Unix: ``fcntl.flock`` — released automatically when the process exits, so a
    crash cannot leave a held lock behind.

    Fallback (no ``fcntl``, e.g. Windows): atomic ``O_CREAT|O_EXCL`` creation.
    Abandoned lock files are reclaimed when the recorded owner PID is provably
    dead (POSIX only). Acquisition is bounded by ``_LOCK_TIMEOUT_SECONDS`` so an
    unremovable stale lock fails loudly instead of blocking forever.
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Unix: use fcntl for proper file locking
        import fcntl
        lock_fd = open(lock_path, "w")
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)
        _lock_fds[str(lock_path)] = lock_fd
    except ImportError:
        # No fcntl: atomic file creation with bounded contention handling.
        lock_file = lock_path.with_suffix(".lockfile")
        import time
        deadline = time.monotonic() + _LOCK_TIMEOUT_SECONDS
        while True:
            try:
                # Atomic create - fails if file exists
                fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                _lock_fds[str(lock_path)] = lock_file
                return
            except FileExistsError:
                # Reclaim an abandoned lock left by a dead process, if provable.
                if _reclaim_stale_lock(lock_file):
                    continue
                if time.monotonic() >= deadline:
                    raise TransactionConflictError(
                        f"Timed out acquiring lock {lock_file} after "
                        f"{_LOCK_TIMEOUT_SECONDS:.0f}s; another process appears to "
                        f"hold it. If no transaction is running, remove the stale "
                        f"lock file manually and retry."
                    )
                time.sleep(_LOCK_RETRY_INTERVAL_SECONDS)
            except OSError as e:
                raise TransactionConflictError(f"Failed to acquire lock: {e}") from e


def _reclaim_stale_lock(lock_file: Path) -> bool:
    """Remove a fallback lock file whose recorded owner process is dead.

    Returns True if a stale file was removed and acquisition should retry.
    Only reliable on POSIX where ``os.kill(pid, 0)`` probes liveness safely; on
    Windows this conservatively returns False and the bounded timeout governs.
    """
    try:
        contents = lock_file.read_text(encoding="utf-8").strip()
    except OSError:
        return False
    try:
        owner_pid = int(contents)
    except ValueError:
        return False

    if owner_pid == os.getpid():
        # Same process: only reclaim if there is no active in-memory owner for
        # this lock file. A live contender must not be mistaken for a dead owner.
        for owner in _lock_fds.values():
            if isinstance(owner, Path) and owner == lock_file:
                return False
        try:
            lock_file.unlink()
            return True
        except OSError:
            return False

    if os.name == "nt":
        # No portable liveness probe without extra dependencies.
        return False

    try:
        os.kill(owner_pid, 0)
    except ProcessLookupError:
        try:
            lock_file.unlink()
            return True
        except OSError:
            return False
    except (PermissionError, OSError):
        return False
    return False


def _release_lock(lock_path: Path) -> None:
    """Release the exclusive lock."""
    lock_data = _lock_fds.pop(str(lock_path), None)
    if lock_data is None:
        return

    try:
        import fcntl
        # Unix: release fcntl lock
        if hasattr(lock_data, "fileno"):
            fcntl.flock(lock_data.fileno(), fcntl.LOCK_UN)
            lock_data.close()
    except ImportError:
        # Fallback: remove lock file (best effort)
        if isinstance(lock_data, Path) and lock_data.exists():
            try:
                lock_data.unlink()
            except OSError:
                pass


def change_requirements(
    *,
    group_name: str,
    state: dict[str, Any],
    new_requirements_file: str,
    reason: str,
    request_id: str | None = None,  # Stable retry identity (auto-generated if None)
    _use_in_memory_state: bool = False,  # For testing only - skips disk reload
) -> dict[str, Any]:
    """Change requirements and create a new baseline.

    DELEGATES to execute_baseline_transaction for full Phase B safety.

    Reads the new requirements file, delegates to the shared transaction
    entry point which handles locking, staging, publication, and state commit.

    Args:
        group_name: Workflow template group name.
        state: Job state dict (used for job_id extraction).
        new_requirements_file: Path to new requirements file.
        reason: Reason for the change (for audit trail).
        request_id: Optional stable request identity. Supplying the same value on
            retry lets the shared flow validate committed replay or recover a
            published-but-uncommitted final instead of creating a new baseline.
        _use_in_memory_state: For testing only - skips disk reload.
            Production should always reload from disk for safety.

    Returns:
        Combined result dict with state fields and result fields.
    """
    job_id = state.get("job_id")
    if not job_id:
        raise ValueError("State must have job_id")

    # NOTE: Do NOT pre-reject STOPPED_ARCHIVED here. The shared locked entry point
    # checks committed replay before the archived guard, so an identical historical
    # retry returns unchanged while genuinely new archived work still rejects.

    # Read request bytes
    new_req_src = Path(new_requirements_file)
    if not new_req_src.exists():
        raise ValueError(f"New requirements file does not exist: {new_requirements_file}")

    request_bytes = new_req_src.read_bytes()

    # Delegate to shared transaction entry point
    # Production: reload from disk for safety (_use_in_memory_state=False)
    # Testing: use in-memory state (_use_in_memory_state=True)
    try:
        result = execute_baseline_transaction(
            group_name=group_name,
            job_id=job_id,
            request_bytes=request_bytes,
            request_id=request_id,
            reason=reason,  # Pass reason for history
            _authoritative_state=state if _use_in_memory_state else None,
        )
    except TransactionConflictError as e:
        # Convert to ValueError for backward compatibility, but preserve the
        # stable retry identity/phase attached by the shared entry point.
        err = ValueError(str(e))
        for _attr in ("request_id", "operation_id", "phase"):
            if hasattr(e, _attr):
                setattr(err, _attr, getattr(e, _attr))
        raise err from e

    # For in-memory testing mode: update caller's state to match what was saved
    # For production: the authoritative state was reloaded from disk and saved
    # The caller's state is stale; reload it for consistency
    if _use_in_memory_state:
        # Testing mode: update caller's state to reflect the transaction
        new_baseline = result.get("baseline")
        planning_folder = state.get("artifacts", {}).get("PLANNING_FOLDER", "")

        if planning_folder and new_baseline:
            from .constants import (
                ARTIFACT_PATH_BASELINE_REQUEST,
                ARTIFACT_PATH_REQUIREMENTS,
                ARTIFACT_PATH_QWEN_PLAN,
                ARTIFACT_PATH_CODEX_REVIEW,
            )
            state.setdefault("artifacts", {})
            state["artifacts"]["RAW_REQUEST_FILE"] = str(
                PROJECT_ROOT / ARTIFACT_PATH_BASELINE_REQUEST(planning_folder, new_baseline)
            )
            state["artifacts"]["REQUIREMENTS_FILE"] = str(
                PROJECT_ROOT / ARTIFACT_PATH_REQUIREMENTS(planning_folder, new_baseline)
            )
            state["artifacts"]["QWEN_PLAN_FILE"] = str(
                PROJECT_ROOT / ARTIFACT_PATH_QWEN_PLAN(planning_folder, revision=1, baseline=new_baseline)
            )
            state["artifacts"]["CODEX_REVIEW_FILE"] = str(
                PROJECT_ROOT / ARTIFACT_PATH_CODEX_REVIEW(planning_folder, revision=1, baseline=new_baseline)
            )

        # Record change history for testing mode
        if reason:
            state.setdefault("change_history", []).append({
                "baseline": new_baseline,
                "reason": reason,
                "changed_at": result.get("committed_at"),
            })

        state["requirements_baseline"] = new_baseline
        state["current_step"] = "formalize_requirements"
        _apply_baseline_reset(state)
    else:
        # Production mode: reload state from disk to get the saved state
        state = load_job(group_name, job_id)

    # Return combined result: state fields for backward compatibility + result fields for CLI
    new_baseline = result.get("baseline")
    return {
        # State fields (for backward compatibility with existing tests/callers)
        **state,
        # Result fields (for CLI and new callers)
        "baseline": new_baseline,
        "request_id": result.get("request_id"),
        "operation_id": result.get("operation_id"),
        "status": result.get("status"),
        "committed_at": result.get("committed_at"),
        # Also provide requirements_baseline for backward compatibility
        "requirements_baseline": new_baseline,
    }


# ---------------------------------------------------------------------------
# PRE-INIT promotion (initiative_intake_v1 only)
# ---------------------------------------------------------------------------

def _derive_init_path_from_pre_init(pre_init_path: str) -> str:
    """Compute the INIT_FILE path by replacing the ``PRE-INIT-`` prefix with ``INIT-``."""
    rel = Path(pre_init_path)
    if rel.parent != Path(delivery_doc_rel("01_initiatives/pre_init")):
        raise ValueError(f"Unexpected PRE_INIT_FILE path for promotion: {pre_init_path!r}")
    name = rel.name
    if not name.startswith("PRE-INIT-"):
        raise ValueError(f"Unexpected PRE_INIT_FILE name for promotion: {pre_init_path!r}")
    init_name = "INIT-" + name.removeprefix("PRE-INIT-")
    return str(Path(delivery_doc_rel("01_initiatives")) / init_name)


def _promote_pre_init_to_init(state: dict[str, Any]) -> str:
    """Copy PRE_INIT_FILE to the canonical INIT_FILE location and update the artifact.

    Returns the repo-relative path of the promoted INIT_FILE.

    Raises:
        ValueError: If PRE_INIT_FILE is not set in the artifact dict.
        FileNotFoundError: If the PRE_INIT_FILE does not exist on disk.
    """
    artifacts = state.setdefault("artifacts", {})
    pre_init_path = str(artifacts.get("PRE_INIT_FILE") or "").strip()
    if not pre_init_path:
        raise ValueError("Cannot promote without PRE_INIT_FILE.")
    pre_init_abs = resolve_repo_path(pre_init_path)
    if not pre_init_abs.exists() or not pre_init_abs.is_file():
        raise FileNotFoundError(f"PRE_INIT_FILE is missing: {pre_init_abs}")
    target_rel = _derive_init_path_from_pre_init(pre_init_path)
    target_abs = resolve_repo_path(target_rel)
    if target_abs.exists():
        artifacts["INIT_FILE"] = target_rel
        return target_rel
    ensure_dir(target_abs.parent)
    target_abs.write_text(pre_init_abs.read_text(encoding="utf-8"), encoding="utf-8")
    artifacts["INIT_FILE"] = target_rel
    return target_rel


# ---------------------------------------------------------------------------
# Retry state helpers
# ---------------------------------------------------------------------------

def prepare_state_for_retry(*, group_name: str, state: dict[str, Any], step: str) -> dict[str, Any]:
    """Reset a waiting job back to IN_PROGRESS so the step can be re-executed.

    Handles three waiting statuses:
    - ``WAITING_FOR_AUTO_RETRY`` — clears status, keeps current_step.
    - ``WAITING_FOR_HUMAN_INTERVENTION`` — clears status and
      ``pending_intervention_for``.
    - ``WAITING_FOR_HUMAN_MAXRETRIED`` — clears status only.

    Also handles the special case where the job is IN_PROGRESS with an
    active loop context (refine loop was activated but step has not run yet).

    Args:
        group_name: Workflow template group name.
        state: Mutable job state dict.
        step: The step to set as current.

    Returns:
        The updated job state dict.
    """
    previous_status = get_job_status(state)
    if previous_status in {"WAITING_FOR_AUTO_RETRY", "WAITING_FOR_HUMAN_INTERVENTION", "WAITING_FOR_HUMAN_MAXRETRIED"}:
        set_job_status(state, "IN_PROGRESS")
        state["current_step"] = step
        if previous_status == "WAITING_FOR_HUMAN_INTERVENTION":
            state["pending_intervention_for"] = None
        save_job(group_name, state["job_id"], state)
    elif previous_status == "IN_PROGRESS" and state.get("loop_context", {}).get("active"):
        state["current_step"] = step
        save_job(group_name, state["job_id"], state)
    return state


def enforce_retry_limit_before_run(*, state: dict[str, Any], step: str, max_rejects: int) -> None:
    """Raise if the step has already exhausted its allowed reject count.

    Called before each step execution to prevent infinite retry loops.
    If ``max_rejects`` is 0, any prior reject is an error.  If positive,
    the current reject count must be strictly less than the limit.

    Args:
        state: Mutable job state dict (reads ``reject_counts``).
        step: Name of the step about to execute.
        max_rejects: Maximum allowed rejects for this step.

    Raises:
        ValueError: If the step has reached or exceeded max rejects.
    """
    current_count = int(state.get("reject_counts", {}).get(step, 0))
    exhausted = False
    if max_rejects == 0:
        exhausted = current_count > 0
    elif max_rejects > 0:
        exhausted = current_count >= max_rejects
    if exhausted:
        raise ValueError(
            f"Step {step!r} for job {state['job_id']} has reached max rejects "
            f"({current_count}/{max_rejects}). Use --new-job or reset the job explicitly."
        )


# ---------------------------------------------------------------------------
# Baseline Transaction Management (plan_first_review_v1)
# ---------------------------------------------------------------------------

def validate_immutable_operation(
    existing_op: dict,
    operation_id: str,
    request_id: str,
    request_bytes: bytes,
    incoming_request_hash: str,
    ending_baseline: int,
    actual_dir: Path,
    state: dict,
    group_name: str,
    job_id: str,
    project_root: Path,
    phase: str,  # "staging" | "final" | "committed_replay"
    commit_ledger: dict | None = None,
) -> dict:
    """Validate immutable operation object with phase awareness.

    Phase-specific directory handling:
    - "staging": actual_dir is .staging_<operation_id>, stored paths name final
    - "final": actual_dir is baseline_XX, stored paths name final
    - "committed_replay": actual_dir is baseline_XX, validated against commit ledger

    Returns validated operation object if all checks pass.
    Raises TransactionConflictError if any check fails.
    """
    from .artifact_keys import ARTIFACT_KEY_PLANNING_FOLDER
    from .constants import (
        ARTIFACT_PATH_BASELINE_DIR,
        ARTIFACT_PATH_BASELINE_REQUEST,
    )

    # 1. Valid schema/types and exact identity binding
    if not isinstance(existing_op, dict):
        raise TransactionConflictError("Operation is not a dict")

    stored_operation_id = existing_op.get("operation_id")
    stored_request_id = existing_op.get("request_id")
    stored_group_name = existing_op.get("group_name")
    stored_job_id = existing_op.get("job_id")
    stored_ending_baseline = existing_op.get("ending_baseline")
    stored_new_baseline = existing_op.get("new_baseline")

    # Required identity schema: nonempty strings, never ints/bools/None.
    for _field_name, _field_value in (
        ("operation_id", stored_operation_id),
        ("request_id", stored_request_id),
        ("group_name", stored_group_name),
        ("job_id", stored_job_id),
    ):
        if not isinstance(_field_value, str) or not _field_value:
            raise TransactionConflictError(
                f"{_field_name} must be a nonempty string: {_field_value!r}"
            )

    # Validate ownership
    if stored_operation_id != operation_id:
        raise TransactionConflictError(f"Operation ID mismatch: {stored_operation_id} != {operation_id}")
    if stored_request_id != request_id:
        raise TransactionConflictError(f"Request ID mismatch: {stored_request_id} != {request_id}")
    if stored_group_name != group_name:
        raise TransactionConflictError(f"Group name mismatch: {stored_group_name} != {group_name}")
    if stored_job_id != job_id:
        raise TransactionConflictError(f"Job ID mismatch: {stored_job_id} != {job_id}")

    # Validate exact-integer baselines
    if not isinstance(ending_baseline, int) or isinstance(ending_baseline, bool):
        raise TransactionConflictError(f"ending_baseline is not an integer: {ending_baseline}")
    if not isinstance(stored_ending_baseline, int) or isinstance(stored_ending_baseline, bool):
        raise TransactionConflictError(f"ending_baseline is not an integer: {stored_ending_baseline}")
    if not isinstance(stored_new_baseline, int) or isinstance(stored_new_baseline, bool):
        raise TransactionConflictError(f"new_baseline is not an integer: {stored_new_baseline}")
    if stored_ending_baseline <= 0:
        raise TransactionConflictError(f"ending_baseline must be positive: {stored_ending_baseline}")
    if stored_new_baseline <= 0:
        raise TransactionConflictError(f"new_baseline must be positive: {stored_new_baseline}")
    if stored_ending_baseline != ending_baseline:
        raise TransactionConflictError(f"Ending baseline mismatch: {stored_ending_baseline} != {ending_baseline}")
    if stored_new_baseline != ending_baseline + 1:
        raise TransactionConflictError(f"new_baseline != ending_baseline+1: {stored_new_baseline} != {ending_baseline + 1}")

    # 2. Phase-specific directory validation
    planning_folder = state.get("artifacts", {}).get(ARTIFACT_KEY_PLANNING_FOLDER, "")
    if not planning_folder:
        raise TransactionConflictError("Missing PLANNING_FOLDER in artifacts")

    if phase == "staging":
        # Staging directory is .staging_<operation_id>
        expected_staging_dir = project_root / planning_folder / f".staging_{operation_id}"
        if actual_dir.resolve() != expected_staging_dir.resolve():
            raise TransactionConflictError(f"Actual staging dir {actual_dir} != expected {expected_staging_dir}")
        # Stored canonical paths name the final location (validated below)
    elif phase == "final":
        # Final directory is baseline_XX
        expected_final_dir = project_root / planning_folder / f"baseline_{stored_new_baseline:02d}"
        if actual_dir.resolve() != expected_final_dir.resolve():
            raise TransactionConflictError(f"Actual final dir {actual_dir} != expected {expected_final_dir}")
    elif phase == "committed_replay":
        # Committed replay — validate against commit ledger
        if not commit_ledger:
            raise TransactionConflictError("Committed replay requires commit ledger")
        commit_record = commit_ledger.get(request_id)
        if not commit_record:
            raise TransactionConflictError(f"No commit record for request_id {request_id}")
        # Validate immutable operation matches commit record
        committed_op = commit_record.get("operation")
        if not committed_op:
            raise TransactionConflictError("Commit record missing operation payload")
        # Compare stored operation with committed operation
        if existing_op != committed_op:
            raise TransactionConflictError("Operation differs from committed record")
        # Validate final directory
        expected_final_dir = project_root / planning_folder / f"baseline_{stored_new_baseline:02d}"
        if actual_dir.resolve() != expected_final_dir.resolve():
            raise TransactionConflictError(f"Actual final dir != expected for committed replay")
    else:
        raise TransactionConflictError(f"Unknown phase: {phase}")

    # Validate stored canonical paths match expected (R8: 4 required keys)
    stored_paths = existing_op.get("canonical_paths", {})

    # All 4 canonical keys are required
    required_canonical_keys = ["request", "operation", "ending_snapshot", "receipt"]
    for key in required_canonical_keys:
        if key not in stored_paths:
            raise TransactionConflictError(f"Missing required canonical field: {key}")
        if not isinstance(stored_paths[key], str):
            raise TransactionConflictError(f"Canonical {key} is not a string: {type(stored_paths[key])}")

    # Build expected paths for all 4 keys
    baseline_dir_rel = ARTIFACT_PATH_BASELINE_DIR(planning_folder, stored_new_baseline)
    expected_paths = {
        "request": ARTIFACT_PATH_BASELINE_REQUEST(planning_folder, stored_new_baseline),
        "operation": f"{baseline_dir_rel}/operation.json",
        "ending_snapshot": f"{baseline_dir_rel}/ending_snapshot.json",
        "receipt": f"{baseline_dir_rel}/receipt.json",
    }

    # Validate each required canonical path
    for key, expected_value in expected_paths.items():
        if stored_paths[key] != expected_value:
            raise TransactionConflictError(
                f"Canonical {key} path mismatch: {stored_paths[key]} != {expected_value}"
            )

    # 3. Incoming and stored request hashes match
    stored_request_hash = existing_op.get("request_hash")
    if not stored_request_hash:
        raise TransactionConflictError("Missing request_hash")
    if incoming_request_hash != stored_request_hash:
        raise TransactionConflictError(f"Incoming request hash mismatch: {incoming_request_hash} != {stored_request_hash}")

    # 4. Require the snapshot digest (immutable evidence must bind the snapshot)
    stored_snapshot_hash = existing_op.get("ending_snapshot_hash")
    if not stored_snapshot_hash:
        raise TransactionConflictError("Missing ending_snapshot_hash")
    if not isinstance(stored_snapshot_hash, str):
        raise TransactionConflictError(
            f"ending_snapshot_hash is not a string: {type(stored_snapshot_hash)}"
        )

    # 4b. Require the recorded semantic ending identity (never optional)
    stored_identity = existing_op.get("ending_state_identity")
    if not stored_identity:
        raise TransactionConflictError("Missing ending_state_identity")
    if not isinstance(stored_identity, str):
        raise TransactionConflictError(
            f"ending_state_identity is not a string: {type(stored_identity)}"
        )

    # 5. Validate the stored manifest digest (REQUIRED, never optional)
    stored_manifest_hash = existing_op.get("manifest_hash")
    if not stored_manifest_hash:
        raise TransactionConflictError("Missing manifest_hash")

    op_for_digest = {k: v for k, v in existing_op.items() if k != "manifest_hash"}
    computed_manifest_hash = hashlib.sha256(json.dumps(op_for_digest, sort_keys=True).encode()).hexdigest()
    if computed_manifest_hash != stored_manifest_hash:
        raise TransactionConflictError(
            "Computed manifest != stored manifest_hash"
        )

    # 6. Hash the ACTUAL persisted bytes (not only the declared digest fields).
    request_file = actual_dir / "request.md"
    if not request_file.exists():
        raise TransactionConflictError(f"Missing request.md at {request_file}")
    persisted_request_bytes = request_file.read_bytes()
    if persisted_request_bytes != request_bytes:
        raise TransactionConflictError(
            "Persisted request bytes != incoming request bytes"
        )
    if hashlib.sha256(persisted_request_bytes).hexdigest() != stored_request_hash:
        raise TransactionConflictError("Persisted request hash != stored request_hash")

    snapshot_file = actual_dir / "ending_snapshot.json"
    if not snapshot_file.exists():
        raise TransactionConflictError(f"Missing ending_snapshot.json at {snapshot_file}")
    persisted_snapshot_bytes = snapshot_file.read_bytes()
    if hashlib.sha256(persisted_snapshot_bytes).hexdigest() != stored_snapshot_hash:
        raise TransactionConflictError("Persisted snapshot hash != stored ending_snapshot_hash")
    try:
        persisted_snapshot = json.loads(persisted_snapshot_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise TransactionConflictError("Persisted ending_snapshot.json is corrupt")
    if _semantic_ending_identity(persisted_snapshot) != stored_identity:
        raise TransactionConflictError(
            "Persisted snapshot semantic identity != stored ending_state_identity"
        )

    # Return a validated copy bound to the verified manifest
    validated_op = dict(existing_op)
    validated_op["manifest_hash"] = computed_manifest_hash

    return validated_op


def get_planning_folder(state: dict) -> str:
    """Extract planning_folder from state artifacts.

    Returns the planning folder string.
    Raises ValueError if missing.
    """
    from .artifact_keys import ARTIFACT_KEY_PLANNING_FOLDER

    planning_folder = state.get("artifacts", {}).get(ARTIFACT_KEY_PLANNING_FOLDER, "")
    if not planning_folder:
        raise ValueError("Missing PLANNING_FOLDER in state artifacts")
    return planning_folder


def _semantic_ending_identity(state: dict) -> str:
    """Compute a stable semantic identity for an ending state.

    Used to compare the current authoritative ending state against the frozen
    ending snapshot before adoption/resume. Volatile bookkeeping (``updated_at``)
    is excluded because it can change without changing the semantic ending
    state; every other field is compared.
    """
    projection = {k: v for k, v in state.items() if k != "updated_at"}
    return hashlib.sha256(
        json.dumps(projection, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def _require_iso_timestamp(value: Any, field: str) -> None:
    """Require a non-empty ISO-8601 timestamp string.

    Truthiness/equality alone is insufficient: equal invalid text must reject.
    """
    if not isinstance(value, str) or not value:
        raise TransactionConflictError(f"Missing or invalid {field}: {value!r}")
    try:
        dt.datetime.fromisoformat(value)
    except (ValueError, TypeError):
        raise TransactionConflictError(f"Invalid {field} format: {value!r}")


def _derive_receipt(operation: dict, commit_record: dict) -> dict:
    """Derive receipt from validated operation and commit record.

    Receipt is DERIVED, not independently authored.
    Used for both initial creation and repair of truncated/malformed receipts.
    """
    return {
        "request_id": operation["request_id"],
        "operation_id": operation["operation_id"],
        "baseline": operation["new_baseline"],
        "committed_at": commit_record["committed_at"],
        "manifest_hash": operation["manifest_hash"],
    }


def repair_derived_receipt(
    operation: dict,
    commit_record: dict,
    receipt_path: Path,
) -> bool:
    """Repair missing, malformed, or mismatched receipt.

    Called AFTER full immutable authority validation passes.
    Returns True if repair was needed.

    Handles:
    - Missing receipt file
    - Truncated or malformed receipt (JSON decode failure)
    - Invalid encoding (UnicodeDecodeError)
    - Mismatched receipt content

    Atomic replacement prevents partial receipt on retry.
    NO job save, NO new timestamp, NO accounting change.
    """
    expected_receipt = _derive_receipt(operation, commit_record)
    expected_bytes = json.dumps(expected_receipt, indent=2).encode("utf-8")

    need_repair = False

    if not receipt_path.exists():
        need_repair = True
    else:
        try:
            receipt_text = receipt_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Invalid encoding is derived-content corruption - replace it.
            need_repair = True
        except OSError as e:
            # Real I/O error - propagate to caller
            raise TransactionConflictError(
                f"Failed to read receipt at {receipt_path}: {e}"
            ) from e
        else:
            try:
                existing_receipt = json.loads(receipt_text)
                if existing_receipt != expected_receipt:
                    # Content mismatch - need repair
                    need_repair = True
            except json.JSONDecodeError:
                # Truncated or malformed - need repair
                need_repair = True

    if need_repair:
        # Atomic replacement using temp file
        temp_path = receipt_path.with_suffix(".tmp")
        try:
            temp_path.write_bytes(expected_bytes)
            temp_path.replace(receipt_path)  # Atomic on POSIX
        except OSError as e:
            raise TransactionConflictError(
                f"Failed to write receipt at {receipt_path}: {e}"
            ) from e
        finally:
            if temp_path.exists():
                temp_path.unlink()

    return need_repair


def complete_baseline_transaction(
    *,
    state: dict,
    group_name: str,
    job_id: str,
    request_id: str,
    operation_id: str,
    request_bytes: bytes,
    request_hash: str,
    ending_baseline: int,
    new_baseline: int,
    planning_folder: str,
    project_root: Path,
    commit_ledger: dict,
    _use_in_memory_state: bool = False,  # Test-only adapter; production reloads
) -> dict:
    """Compatibility entry point — delegates to the shared transaction flow.

    This wrapper no longer writes immutable evidence itself. It performs the
    legacy argument guards, then delegates to ``execute_baseline_transaction``
    so all callers share one locked transition builder, one validator and one
    writer (staging → publication → single state commit → derived receipt).

    Production (``_use_in_memory_state=False``) never trusts the supplied
    ``state``/``commit_ledger`` as authority: it delegates without an
    ``_authoritative_state`` override, so the shared flow reloads the raw job
    under the lock. The legacy baseline constraints are checked against the
    authoritative state (or a verified committed replay) — a stale caller cannot
    roll the disk baseline backwards.

    Idempotent: a matching committed ledger entry is handled by the shared
    committed-replay path, which validates evidence and repairs only the
    derived receipt.

    Returns the committed result dict.
    Raises TransactionConflictError on validation failure.
    """
    # Legacy guard: new baseline must be exactly ending + 1 (pure argument check).
    if new_baseline != ending_baseline + 1:
        raise TransactionConflictError(
            f"new_baseline {new_baseline} != ending_baseline {ending_baseline} + 1"
        )

    if _use_in_memory_state:
        # Test-only adapter: validate against the supplied caller state/ledger.
        existing_commit = commit_ledger.get(request_id)
        if existing_commit is not None:
            existing_op = existing_commit.get("operation", {})
            if existing_op.get("operation_id") != operation_id:
                raise TransactionConflictError(
                    f"Commit ledger has different operation_id for request_id {request_id}"
                )
        else:
            state_baseline = state.get("requirements_baseline", ending_baseline)
            if state_baseline != ending_baseline:
                raise TransactionConflictError(
                    f"State requirements_baseline {state_baseline} != ending_baseline {ending_baseline}"
                )

        return execute_baseline_transaction(
            group_name=group_name,
            job_id=job_id,
            request_bytes=request_bytes,
            request_id=request_id,
            project_root=project_root,
            _authoritative_state=state,
            _preferred_operation_id=operation_id,
            _committed_state_out=state,
            _expected_ending_baseline=ending_baseline,
            _expected_new_baseline=new_baseline,
        )

    # Production: reload authoritative state under the shared lock. A committed
    # replay is recognised before the legacy baseline checks (see shared flow).
    return execute_baseline_transaction(
        group_name=group_name,
        job_id=job_id,
        request_bytes=request_bytes,
        request_id=request_id,
        project_root=project_root,
        _preferred_operation_id=operation_id,
        _expected_ending_baseline=ending_baseline,
        _expected_new_baseline=new_baseline,
    )


# ---------------------------------------------------------------------------
# Attempt Tracking and Recovery (plan_first_review_v1)
# ---------------------------------------------------------------------------

def _create_recovery_snapshot_for_preparation(
    attempt_record: dict,
    state: dict,
    group_cfg: dict,
    group_name: str,
    planning_folder: str,
) -> dict:
    """Create complete recovery snapshot with actual loop field validation.

    Reads and validates all four actual loop fields before snapshot construction.
    Copies validated actual values into snapshot (no synthesis).

    For refine_plan: validates active, loop_step, refine_step, loop_target_artifact,
    loop_source_review, loop_iteration, pre_refine_checksum.

    For generate_plan: minimal inactive context (active=False).
    """
    from .constants import ARTIFACT_PATH_CODEX_REVIEW

    step = attempt_record.get("step")
    loop_context = state.get("loop_context", {})

    if step == "refine_plan":
        # Get codex_review step config
        step_configs = group_cfg.get("step_configs", {})
        codex_review_cfg = step_configs.get("codex_review", {})
        on_reject_refine = codex_review_cfg.get("on_reject_refine", {})

        # Validate required config fields
        configured_refine_step = on_reject_refine.get("step")
        if not configured_refine_step:
            raise ValueError("Missing on_reject_refine.step in codex_review config")
        if configured_refine_step != "refine_plan":
            raise ValueError(f"on_reject_refine.step {configured_refine_step} != refine_plan")

        configured_target_artifact = on_reject_refine.get("artifact")
        if not configured_target_artifact:
            raise ValueError("Missing on_reject_refine.artifact in codex_review config")

        # Compute canonical review path UNCONDITIONALLY
        baseline = attempt_record["baseline"]
        input_revision = attempt_record["input_revision"]
        canonical_review_path = ARTIFACT_PATH_CODEX_REVIEW(planning_folder, input_revision, baseline)

        # READ all four actual loop fields
        actual_active = loop_context.get("active")
        actual_loop_step = loop_context.get("loop_step")
        actual_refine_step = loop_context.get("refine_step")
        actual_target_artifact = loop_context.get("loop_target_artifact")
        actual_source_review = loop_context.get("loop_source_review")
        actual_iteration = loop_context.get("loop_iteration", 0)
        actual_pre_checksum = loop_context.get("pre_refine_checksum")

        # VALIDATE all four actual fields before snapshot construction
        # 1. actual active is exactly True
        if not isinstance(actual_active, bool) or actual_active is not True:
            raise ValueError(f"Actual loop_context.active is not exactly True: {actual_active}")

        # 2. actual loop_step equals codex_review
        if actual_loop_step != "codex_review":
            raise ValueError(f"Actual loop_step {actual_loop_step} != codex_review")

        # 3. actual refine_step equals current attempt step AND configured refine step
        if actual_refine_step != step:
            raise ValueError(f"Actual refine_step {actual_refine_step} != attempt step {step}")
        if actual_refine_step != configured_refine_step:
            raise ValueError(f"Actual refine_step {actual_refine_step} != configured {configured_refine_step}")

        # 4. actual loop_target_artifact equals configured artifact
        if actual_target_artifact != configured_target_artifact:
            raise ValueError(f"Actual loop_target_artifact {actual_target_artifact} != configured {configured_target_artifact}")

        # Validate source/checksum/iteration
        if not actual_source_review or not isinstance(actual_source_review, str):
            raise ValueError("Missing or invalid loop_source_review in actual context")
        if actual_source_review != canonical_review_path:
            raise ValueError(
                f"Actual loop_source_review {actual_source_review} != canonical {canonical_review_path}"
            )
        if not actual_pre_checksum or not isinstance(actual_pre_checksum, str):
            raise ValueError("Missing or invalid pre_refine_checksum in actual context")
        if not isinstance(actual_iteration, int) or isinstance(actual_iteration, bool):
            raise ValueError(f"loop_iteration is not int: {type(actual_iteration)}")
        if actual_iteration < 0:
            raise ValueError(f"loop_iteration is negative: {actual_iteration}")

        # COPY validated actual values into snapshot (no synthesis)
        return {
            # Identity with trusted group_name
            "job_id": state["job_id"],
            "group_name": group_name,
            "baseline": baseline,
            "step": step,
            "input_revision": input_revision,
            "target_revision": attempt_record["target_revision"],
            # Complete loop context with VALIDATED ACTUAL values
            "active": actual_active,  # Validated exactly True
            "loop_step": actual_loop_step,  # Validated == codex_review
            "refine_step": actual_refine_step,  # Validated == step == configured
            "loop_target_artifact": actual_target_artifact,  # Validated == configured
            "loop_source_review": actual_source_review,  # Validated == canonical
            "loop_iteration": actual_iteration,  # Validated exact int >= 0
            "pre_refine_checksum": actual_pre_checksum,  # Validated nonempty string
            "planning_folder": planning_folder,
        }
    elif step == "generate_plan":
        # Generation retains separate minimal inactive context
        return {
            "job_id": state["job_id"],
            "group_name": group_name,
            "baseline": attempt_record["baseline"],
            "step": step,
            "input_revision": None,
            "target_revision": 1,
            "active": False,
        }
    else:
        raise ValueError(f"Unknown step for recovery: {step}")


def prepare_plan_attempt(
    group_name: str,
    job_id: str,
    state: dict,
    step: str,
    step_cfg: dict,
    group_cfg: dict,
    prepared_context: dict,
    project_root: Path,
) -> dict:
    """Prepare attempt record with complete pre-save validation.

    Validates actual resolved context using same contract as recovery.
    Rejects invalid context before saving/invoking.

    Input/output rules:
    - generate_plan: input_revision=None, target_revision=1
    - refine_plan: input_revision=current_revision, target_revision=current_revision+1

    Saves attempt record AND active link atomically.
    """
    from .constants import ARTIFACT_PATH_QWEN_PLAN

    planning_folder = get_planning_folder(state)
    baseline = state.get("requirements_baseline", 1)
    current_revision = state.get("plan_revision", 1)

    # R20: A16-03 - Validate exact integer types BEFORE any processing
    if isinstance(baseline, bool):
        raise ValueError(f"requirements_baseline must be exact int, got bool True")
    if not isinstance(baseline, int):
        raise ValueError(f"requirements_baseline must be exact int, got {type(baseline).__name__}")

    if isinstance(current_revision, bool):
        raise ValueError(f"plan_revision must be exact int, got bool True")
    if not isinstance(current_revision, int):
        raise ValueError(f"plan_revision must be exact int, got {type(current_revision).__name__}")

    # R24: A16-03 - Validate positive ranges
    if baseline <= 0:
        raise ValueError(f"requirements_baseline must be positive int, got {baseline}")
    if current_revision <= 0:
        raise ValueError(f"plan_revision must be positive int, got {current_revision}")

    # Determine target revision
    if step == "generate_plan" and current_revision == 1:
        input_revision = None
        target_revision = 1
    elif step == "refine_plan":
        input_revision = current_revision
        target_revision = current_revision + 1
    else:
        raise ValueError(f"Unexpected step/revision: {step}/{current_revision}")

    # Resolve canonical output path
    output_path = ARTIFACT_PATH_QWEN_PLAN(planning_folder, target_revision, baseline)

    # Generate attempt ID
    attempt_id = f"att_{uuid.uuid4().hex[:12]}"

    # Create attempt record
    attempt_record = {
        "attempt_id": attempt_id,
        "workflow": group_name,
        "job_id": job_id,
        "baseline": baseline,
        "step": step,
        "input_revision": input_revision,
        "target_revision": target_revision,
        "output_path": output_path,
        "output_hash": None,
        "status": "prepared",
        "started_at": now_iso(),
        "applied_result": None,
        "recovered_context": None,
    }

    # Capture and validate complete recovery snapshot BEFORE saving
    # This uses the same validation contract as recovery
    recovery_snapshot = _create_recovery_snapshot_for_preparation(
        attempt_record=attempt_record,
        state=state,
        group_cfg=group_cfg,
        group_name=group_name,
        planning_folder=planning_folder,
    )

    # Snapshot creation already validated actual context
    # If we reach here, validation passed
    attempt_record["recovered_context"] = recovery_snapshot

    # Save attempt record AND active link AND recovery snapshot atomically
    state.setdefault("attempt_records", {})[attempt_id] = attempt_record
    state.setdefault("loop_context", {})["active_attempt_id"] = attempt_id
    save_job(group_name, job_id, state)

    return attempt_record


def compute_output_digest(file_path: Path) -> str:
    """Compute SHA256 digest of a file for output evidence.

    Returns hex digest string.
    Raises ValueError if file cannot be read.
    """
    try:
        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()
    except (OSError, IOError) as e:
        raise ValueError(f"Cannot read output file for digest: {file_path}: {e}")


def validate_revision_formula(
    step: str,
    input_revision: int | None,
    target_revision: int,
    current_revision: int,
) -> tuple[bool, str | None]:
    """Validate attempt input/target against revision formulas.

    Generation: input=None, target=1 (exact int, not bool), current_revision=1
    Refinement: input=current_revision (exact int >= 1), target=input+1 (exact int)

    Returns (valid, error_message).
    """
    if step == "generate_plan":
        if input_revision is not None:
            return False, f"Generation input must be None, got {input_revision}"
        # Reject bool before int check (bool is subclass of int)
        if isinstance(target_revision, bool) or not isinstance(target_revision, int):
            return False, f"Generation target must be exact int, got {type(target_revision)}"
        if target_revision != 1:
            return False, f"Generation target must be 1, got {target_revision}"
        if current_revision != 1:
            return False, f"Generation requires current_revision=1, got {current_revision}"
    elif step == "refine_plan":
        if input_revision is None:
            return False, "Refinement input cannot be None"
        # Reject bool before int check
        if isinstance(input_revision, bool) or not isinstance(input_revision, int):
            return False, f"Refinement input must be exact int, got {type(input_revision)}"
        if input_revision < 1:
            return False, f"Refinement input must be positive, got {input_revision}"
        if input_revision != current_revision:
            return False, f"Refinement input {input_revision} != current_revision {current_revision}"
        # Reject bool before int check for target
        if isinstance(target_revision, bool) or not isinstance(target_revision, int):
            return False, f"Refinement target must be exact int, got {type(target_revision)}"
        if target_revision != input_revision + 1:
            return False, f"Refinement target {target_revision} != input+1 {input_revision + 1}"
        # NOTE: No current_revision >= 2 check — first refinement is v1→v2 when current=1
    else:
        return False, f"Unknown step for revision formula: {step}"

    return True, None


