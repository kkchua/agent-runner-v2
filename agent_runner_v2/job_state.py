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
import tempfile
from pathlib import Path
from typing import Any

from .exceptions import PreflightBlockedError
from .runtime_context import JOBS_ROOT, PROJECT_ROOT, get_workflow_module, ARTIFACT_ROOT

CURRENT_SCHEMA_VERSION = 6  # v2 bumps to 6 (adds runner_version)

NON_TERMINAL_JOB_STATUSES = {
    "IN_PROGRESS",
    "WAITING_FOR_AUTO_RETRY",
    "WAITING_FOR_HUMAN_INTERVENTION",
    "WAITING_FOR_HUMAN_APPROVAL",
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
    "REVIEW_FILE": "REVIEW",
}


def _workflow_module():
    module = get_workflow_module()
    if module is None:
        from . import template_groups as module  # type: ignore[no-redef]
    return module


def _artifact_keys() -> list[str]:
    return list(_workflow_module().ARTIFACT_KEYS)


def _template_groups() -> dict[str, dict[str, Any]]:
    return _workflow_module().TEMPLATE_GROUPS


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

def get_job_status(state: dict[str, Any]) -> str:
    return str(state.get("job_status") or state.get("status") or "")


def set_job_status(state: dict[str, Any], value: str) -> None:
    state["job_status"] = value
    state["status"] = value


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def resolve_repo_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def normalize_repo_relative_path(value: str) -> str:
    return str(resolve_repo_path(value).resolve().relative_to(PROJECT_ROOT.resolve()))


def group_dir(group_name: str) -> Path:
    return JOBS_ROOT / group_name


def job_dir(group_name: str, job_id: str) -> Path:
    return group_dir(group_name) / job_id


def job_state_path(group_name: str, job_id: str) -> Path:
    return job_dir(group_name, job_id) / "job.json"


def get_step_index(group_cfg: dict[str, Any], step: str) -> int:
    return group_cfg["steps"].index(step) + 1


def make_step_dir(group_cfg: dict[str, Any], state: dict[str, Any], step: str) -> Path:
    idx = get_step_index(group_cfg, step)
    ctx = state.get("loop_context", {})
    if ctx.get("active") and step in (ctx.get("refine_step"), ctx.get("loop_step")):
        suffix = f"_iter{ctx['loop_iteration']}"
    else:
        suffix = ""
    return job_dir(state["template_group"], state["job_id"]) / f"{idx:02d}_{step}{suffix}"


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def save_json_atomic(path: Path, data: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def save_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Failure tracking
# ---------------------------------------------------------------------------

def set_last_failure(
    *, state: dict[str, Any], failure_class: str, failure_code: str,
    failure_reason: str, failure_source: str, step: str,
) -> None:
    state["last_failure_class"] = failure_class
    state["last_failure_code"] = failure_code
    state["last_failure_reason"] = failure_reason
    state["last_failure_source"] = failure_source
    state["pending_intervention_for"] = step if failure_class == "HUMAN_RETRY_REQUIRED" else None


def clear_last_failure(state: dict[str, Any]) -> None:
    state["last_failure_class"] = None
    state["last_failure_code"] = None
    state["last_failure_reason"] = None
    state["last_failure_source"] = None
    state["pending_intervention_for"] = None


def append_failure_history(
    *, state: dict[str, Any], step: str, failure_class: str,
    failure_code: str, failure_source: str,
) -> None:
    state.setdefault("failure_history", []).append({
        "step": step,
        "failure_class": failure_class,
        "failure_code": failure_code,
        "failure_source": failure_source,
        "timestamp": now_iso(),
    })


def build_failure_envelope(
    *, failure_class: str, failure_code: str, failure_reason: str, failure_source: str,
) -> dict[str, str]:
    return {
        "failure_class": failure_class,
        "failure_code": failure_code,
        "failure_reason": failure_reason,
        "failure_source": failure_source,
    }


def record_step_usage(state: dict[str, Any], step: str, usage_data: dict[str, Any]) -> None:
    state.setdefault("step_usage", {})[step] = usage_data
    state["usage_summary"] = _recompute_usage_summary(state["step_usage"])


def _recompute_usage_summary(step_usage: dict[str, Any]) -> dict[str, Any]:
    summary = default_usage_summary()
    totals: dict[str, float] = {}
    for usage in step_usage.values():
        if not isinstance(usage, dict):
            continue
        if usage.get("usage_source") == "cli_reported":
            summary["steps_with_usage"] += 1
            for field in ("input_tokens", "output_tokens", "total_tokens", "cost", "duration_ms"):
                value = usage.get(field)
                if value is None:
                    continue
                totals[field] = totals.get(field, 0) + value
        else:
            summary["steps_without_usage"] += 1
    for field, value in totals.items():
        summary[field] = value if field == "cost" else int(value)
    return summary


# ---------------------------------------------------------------------------
# Default state constructors
# ---------------------------------------------------------------------------

def default_review_state() -> dict[str, Any]:
    return {
        "artifact_type": None, "artifact_key": None, "artifact_path": None,
        "reviewer_step": None, "review_iteration": 0, "review_decision": "PENDING",
        "review_decided_at": None, "coder_used": None, "human_decision": "PENDING",
        "human_decided_at": None, "human_actor": None,
        "final_decision": None, "final_decision_source": None,
    }


def default_task_execution_binding() -> dict[str, Any]:
    return {
        "task_graph_id": None, "task_graph_file": None, "task_graph_checksum": None,
        "plan_id": None, "plan_file": None, "task_node_id": None,
        "task_title": None, "task_node_snapshot": None, "bound_at": None,
    }


def default_usage_summary() -> dict[str, Any]:
    return {
        "steps_with_usage": 0, "steps_without_usage": 0,
        "input_tokens": None, "output_tokens": None,
        "total_tokens": None, "cost": None, "duration_ms": None,
    }


# ---------------------------------------------------------------------------
# Job ID generation
# ---------------------------------------------------------------------------

def _extract_short_id(file_path: str, prefix: str) -> str:
    name = Path(file_path).name
    match = re.search(rf"{prefix}-(\d{{8}})-(\d+)", name)
    if match:
        return f"{prefix}{match.group(2).zfill(2)}"
    return prefix


def _extract_draft_short_id(file_path: str) -> str:
    name = Path(file_path).name
    match = re.search(r"(\d{2})-(\d{4})(?=_)", name)
    return f"DRAFT{match.group(2)}" if match else "DRAFT"


def make_job_id(group_name: str, group_cfg: dict[str, Any], seed_artifacts: dict[str, str]) -> str:
    gd = group_dir(group_name)
    ensure_dir(gd)
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
    nums = [
        int(child.name[len(base):])
        for child in gd.iterdir()
        if child.is_dir() and child.name.startswith(base) and child.name[len(base):].isdigit()
    ]
    return f"{base}{(max(nums) + 1 if nums else 1):03d}"


# ---------------------------------------------------------------------------
# Job CRUD
# ---------------------------------------------------------------------------

def infer_seed_identity(group_name: str, seed_artifacts: dict[str, str]) -> tuple[str | None, str | None]:
    if group_name == "task_execution_v1" and seed_artifacts.get("TASK_FILE"):
        return "TASK_FILE", normalize_repo_relative_path(seed_artifacts["TASK_FILE"])
    if group_name == "delivery_planning_v1" and seed_artifacts.get("INIT_FILE"):
        return "INIT_FILE", normalize_repo_relative_path(seed_artifacts["INIT_FILE"])
    if group_name == "initiative_intake_v1" and seed_artifacts.get("DRAFT_INIT_FILE"):
        return "DRAFT_INIT_FILE", normalize_repo_relative_path(seed_artifacts["DRAFT_INIT_FILE"])
    return None, None


def create_job(group_name: str, group_cfg: dict[str, Any], seed_artifacts: dict[str, str]) -> dict[str, Any]:
    job_id = make_job_id(group_name, group_cfg, seed_artifacts)
    ensure_dir(job_dir(group_name, job_id))
    artifact_keys = _artifact_keys()
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
        "loop_context": {
            "active": False, "loop_step": None, "refine_step": None,
            "loop_target_artifact": None, "loop_source_review": None,
            "loop_iteration": 0, "pre_refine_checksum": None,
        },
        "loop_history": [],
        "replan_context": {
            "active": False, "source_review_step": None, "replan_step": None,
            "target_artifact": None, "source_review_file": None, "replan_attempt": 0,
            "pre_replan_checksum": None, "trigger_reason": None, "blocking_issues": [],
            "previous_blocking_issue_count": 0, "previous_blocking_issue_severity": 0,
        },
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
    path = job_state_path(group_name, job_id)
    if not path.exists():
        raise FileNotFoundError(f"Job state not found: {path}")
    state = load_json(path)
    if state.get("template_group") != group_name:
        raise ValueError(
            f"Job {job_id} belongs to template group {state.get('template_group')!r}, not {group_name!r}"
        )
    return state


def save_job(group_name: str, job_id: str, state: dict[str, Any]) -> None:
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
    gd = group_dir(group_name)
    if not gd.exists():
        return []
    states: list[dict[str, Any]] = []
    for child in sorted(gd.iterdir()):
        if not child.is_dir():
            continue
        path = child / "job.json"
        if not path.exists():
            continue
        states.append(ensure_backward_compatible_state(load_json(path)))
    return states


def find_matching_active_job(
    *, group_name: str, seed_artifact_type: str, seed_artifact_path: str,
) -> str | None:
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
    version = int(state.get("state_schema_version", 1))

    if version < 2:
        state.setdefault("loop_context", {
            "active": False, "loop_step": None, "refine_step": None,
            "loop_target_artifact": None, "loop_source_review": None,
            "loop_iteration": 0, "pre_refine_checksum": None,
        })
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
    state.setdefault("loop_context", {
        "active": False, "loop_step": None, "refine_step": None,
        "loop_target_artifact": None, "loop_source_review": None,
        "loop_iteration": 0, "pre_refine_checksum": None,
    })
    state["loop_context"].setdefault("pre_refine_checksum", None)
    state.setdefault("loop_history", [])
    state.setdefault("replan_context", {
        "active": False, "source_review_step": None, "replan_step": None,
        "target_artifact": None, "source_review_file": None, "replan_attempt": 0,
        "pre_replan_checksum": None, "trigger_reason": None, "blocking_issues": [],
        "previous_blocking_issue_count": 0, "previous_blocking_issue_severity": 0,
    })
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
    return state


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
        return state

    if get_job_status(state) in {"COMPLETED", "FAILED"}:
        return state

    ctx = state.get("loop_context", {})
    current_step = state.get("current_step")
    step_cfg = group_cfg.get("step_configs", {}).get(current_step, {})

    excluded_codes: set[str] = {"MISSING_REVIEW_ARTIFACT", "DUPLICATE_REVIEW_FILE"}
    on_reject_refine = step_cfg.get("on_reject_refine") or {}
    on_exhaust_replan = step_cfg.get("on_exhaust_replan") or {}
    if on_reject_refine.get("exhausted_failure_code"):
        excluded_codes.add(on_reject_refine["exhausted_failure_code"])
    if on_exhaust_replan.get("terminal_failure_code"):
        excluded_codes.add(on_exhaust_replan["terminal_failure_code"])

    if (
        get_job_status(state) == "WAITING_FOR_HUMAN_INTERVENTION"
        and not ctx.get("active")
        and step_cfg.get("on_reject_refine")
        and state.get("artifacts", {}).get("REVIEW_FILE")
        and state.get("last_failure_source") == "model"
        and state.get("last_failure_code") not in excluded_codes
    ):
        return _apply_loop_routing(state, current_step, step_cfg, repair_type="AUTO_RECONCILE")

    return state


def _apply_loop_routing(
    state: dict[str, Any], step: str, step_cfg: dict[str, Any], *, repair_type: str = "LOOP_TRIGGER",
) -> dict[str, Any]:
    on_reject_refine = step_cfg["on_reject_refine"]
    review_file = state.get("artifacts", {}).get("REVIEW_FILE")
    state["reconciled_from_failure"] = {
        "class": state.get("last_failure_class"),
        "code": state.get("last_failure_code"),
        "reason": state.get("last_failure_reason"),
        "source": state.get("last_failure_source"),
    }
    existing_iter = state.get("loop_context", {}).get("loop_iteration", 0)
    state["loop_context"] = {
        "active": True,
        "loop_step": step,
        "refine_step": on_reject_refine["step"],
        "loop_target_artifact": on_reject_refine["artifact"],
        "loop_source_review": review_file,
        "loop_iteration": max(existing_iter, 1),
        "pre_refine_checksum": None,
    }
    state["current_step"] = on_reject_refine["step"]
    set_job_status(state, "IN_PROGRESS")
    clear_last_failure(state)
    state.setdefault("repair_history", []).append({"type": repair_type, "step": step, "timestamp": now_iso()})
    return state


def _apply_replan_routing(
    state: dict[str, Any], step: str, step_cfg: dict[str, Any], *, repair_type: str = "REPLAN_TRIGGER",
) -> dict[str, Any]:
    on_exhaust_replan = step_cfg["on_exhaust_replan"]
    review_file = state.get("artifacts", {}).get("REVIEW_FILE")
    current_replan_attempt = int(state.get("replan_context", {}).get("replan_attempt", 0))
    state["reconciled_from_failure"] = {
        "class": state.get("last_failure_class"),
        "code": state.get("last_failure_code"),
        "reason": state.get("last_failure_reason"),
        "source": state.get("last_failure_source"),
    }
    # In v2, blocking_issues is always [] — content analysis is the coder's job
    state["replan_context"] = {
        "active": True,
        "source_review_step": step,
        "replan_step": on_exhaust_replan["step"],
        "target_artifact": on_exhaust_replan["artifact"],
        "source_review_file": review_file,
        "replan_attempt": current_replan_attempt + 1,
        "pre_replan_checksum": None,
        "trigger_reason": str((step_cfg.get("on_reject_refine") or {}).get("exhausted_failure_code") or "REFINEMENT_EXHAUSTED"),
        "blocking_issues": [],  # v2: coder decides adequacy, not runner
        "previous_blocking_issue_count": 0,
        "previous_blocking_issue_severity": 0,
    }
    target_path_value = state.get("artifacts", {}).get(on_exhaust_replan["artifact"])
    if target_path_value:
        target_path = PROJECT_ROOT / target_path_value
        if target_path.exists():
            state["replan_context"]["pre_replan_checksum"] = _md5_file(target_path)
    state.setdefault("replan_history", []).append({
        "source_review_step": step,
        "trigger_reason": state["replan_context"]["trigger_reason"],
        "source_review_file": review_file,
        "blocking_issues": [],
        "replan_step": on_exhaust_replan["step"],
        "replan_attempt": state["replan_context"]["replan_attempt"],
        "triggered_at": now_iso(),
        "replan_result": None, "review_result": None, "resolved_at": None,
    })
    state["loop_context"] = {
        "active": False, "loop_step": None, "refine_step": None,
        "loop_target_artifact": None, "loop_source_review": None,
        "loop_iteration": 0, "pre_refine_checksum": None,
    }
    clear_last_failure(state)
    state["current_step"] = on_exhaust_replan["step"]
    set_job_status(state, "IN_PROGRESS")
    state.setdefault("repair_history", []).append({"type": repair_type, "step": step, "timestamp": now_iso()})
    return state


def reapply_routing(state: dict[str, Any], group_cfg: dict[str, Any]) -> dict[str, Any]:
    current_step = state.get("current_step")
    step_cfg = group_cfg.get("step_configs", {}).get(current_step, {})
    on_reject_refine = step_cfg.get("on_reject_refine") or {}
    on_exhaust_replan = step_cfg.get("on_exhaust_replan") or {}
    exhausted_code = on_reject_refine.get("exhausted_failure_code")
    max_replans = int(on_exhaust_replan.get("max_replans", 0))
    current_replan_attempt = int(state.get("replan_context", {}).get("replan_attempt", 0))

    if (
        step_cfg.get("on_reject_refine")
        and state.get("artifacts", {}).get("REVIEW_FILE")
        and exhausted_code
        and state.get("last_failure_code") == exhausted_code
        and on_exhaust_replan.get("step")
        and current_replan_attempt < max_replans
    ):
        return _apply_replan_routing(state, current_step, step_cfg, repair_type="USER_REAPPLY_REPLAN")

    if step_cfg.get("on_reject_refine") and state.get("artifacts", {}).get("REVIEW_FILE"):
        return _apply_loop_routing(state, current_step, step_cfg, repair_type="USER_REAPPLY")

    return state


def recover_exhausted_planning_job(state: dict[str, Any], group_cfg: dict[str, Any]) -> dict[str, Any]:
    if get_job_status(state) != "FAILED":
        return state
    current_step = state.get("current_step")
    step_cfg = group_cfg.get("step_configs", {}).get(current_step, {})
    on_reject_refine = step_cfg.get("on_reject_refine") or {}
    on_exhaust_replan = step_cfg.get("on_exhaust_replan") or {}
    exhausted_code = on_reject_refine.get("exhausted_failure_code")
    max_replans = int(on_exhaust_replan.get("max_replans", 0))
    current_replan_attempt = int(state.get("replan_context", {}).get("replan_attempt", 0))
    if not exhausted_code or not on_exhaust_replan.get("step") or current_replan_attempt >= max_replans:
        return state
    has_exhausted_failure = any(
        entry.get("step") == current_step and entry.get("failure_code") == exhausted_code
        for entry in state.get("failure_history", [])
    )
    if not has_exhausted_failure or not state.get("artifacts", {}).get("REVIEW_FILE"):
        return state
    state = _apply_replan_routing(state, current_step, step_cfg, repair_type="RECOVERY_REPLAN_MIGRATION")
    save_job(state["template_group"], state["job_id"], state)
    return state


# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------

def _extract_document_status(content: str) -> str | None:
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
    queue = state.get("task_generation_state")
    return isinstance(queue, dict) and bool(queue.get("ordered_tasks"))


def task_queue_current_item(state: dict[str, Any]) -> dict[str, Any] | None:
    queue = state.get("task_generation_state")
    if not isinstance(queue, dict):
        return None
    current_id = queue.get("current_queue_item_id")
    for item in queue.get("ordered_tasks", []):
        if item.get("queue_item_id") == current_id:
            return item
    return None


def next_pending_task_queue_item(state: dict[str, Any]) -> dict[str, Any] | None:
    queue = state.get("task_generation_state")
    if not isinstance(queue, dict):
        return None
    for item in queue.get("ordered_tasks", []):
        if item.get("status") == "PENDING":
            return item
    return None


def task_queue_has_remaining_work(state: dict[str, Any]) -> bool:
    queue = state.get("task_generation_state")
    if not isinstance(queue, dict):
        return False
    return any(item.get("status") != "APPROVED" for item in queue.get("ordered_tasks", []))


def _make_task_queue_item_id(sequence: int) -> str:
    return f"tgq_{sequence:04d}"


def _extract_document_metadata_value(content: str, key: str) -> str | None:
    pattern = re.compile(
        rf"^\s*[-*]\s*(?:\*\*)?{re.escape(key)}(?::(?:\*\*)?|\*\*:\s*|:)\s*(.+?)\s*$",
        re.IGNORECASE,
    )
    for line in content.splitlines():
        match = pattern.match(line.strip())
        if match:
            return match.group(1).strip()
    return None


def extract_task_graph_nodes(task_graph_path: str) -> list[dict[str, Any]]:
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
    import hashlib as _hashlib
    return _hashlib.md5(path.read_bytes()).hexdigest()


def find_task_graph_file_by_id(task_graph_id: str) -> str:
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
    task_graph_file = find_task_graph_file_by_id(task_graph_id)
    binding = build_task_execution_binding(task_graph_file=task_graph_file, task_node_id=task_node_id)
    if not binding.get("task_graph_id"):
        binding["task_graph_id"] = task_graph_id.strip()
    return binding


def task_execution_binding_identity(binding: dict[str, Any] | None) -> tuple[str | None, str | None]:
    if not isinstance(binding, dict):
        return None, None
    task_graph_file = str(binding.get("task_graph_file") or "").strip()
    task_node_id = str(binding.get("task_node_id") or "").strip()
    if not task_graph_file or not task_node_id:
        return None, None
    return "TASK_EXECUTION_BINDING", f"{normalize_repo_relative_path(task_graph_file)}::{task_node_id}"


def task_execution_binding_current_item(state: dict[str, Any]) -> dict[str, Any] | None:
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

def get_next_step_skipping_refine_replan(
    group_cfg: dict[str, Any], state: dict[str, Any],
) -> str | None:
    completed = set(state.get("completed_steps", []))
    skip_steps: set[str] = set()
    for sc in group_cfg.get("step_configs", {}).values():
        for key in ("on_reject_refine", "on_exhaust_replan"):
            s = (sc.get(key) or {}).get("step")
            if s:
                skip_steps.add(s)
    for step in group_cfg["steps"]:
        if step not in completed and step not in skip_steps:
            return step
    return None


def get_next_step(group_cfg: dict[str, Any], state: dict[str, Any]) -> str | None:
    completed = set(state.get("completed_steps", []))
    for step in group_cfg["steps"]:
        if step not in completed:
            return step
    return None


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
) -> tuple[dict[str, Any], int]:
    """Unified step advancement. Returns (state, exit_code): 0=continue, 1=waiting, 2=failed."""
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

    if step_cfg.get("loop_returns_to"):
        return _handle_refine_success(state, step, step_cfg, artifacts)

    if step_cfg.get("replan_returns_to"):
        return _handle_replan_success(state, step, step_cfg, artifacts)

    if step_cfg.get("requires_human_approval_after"):
        return _handle_review_approval(state, step, step_cfg, coder_used)

    if state.get("template_group") == "task_execution_v1" and step == "task":
        return _handle_task_exec_success(state, step)

    if (state.get("template_group") == "delivery_planning_v1"
            and step == "task" and task_queue_is_initialized(state)):
        return _handle_task_queue_success(state, step, artifacts)

    return _advance_to_next(group_cfg, state, step)


def _handle_refine_success(
    state: dict[str, Any], step: str, step_cfg: dict[str, Any], artifacts: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    loop_returns_to = step_cfg["loop_returns_to"]
    ctx = state.get("loop_context", {})
    target_key = ctx.get("loop_target_artifact") or step_cfg.get("target_artifact", "IMPL_FILE")

    if not artifacts.get(target_key):
        set_last_failure(state=state, failure_class="HUMAN_RETRY_REQUIRED",
                         failure_code="MISSING_TARGET_ARTIFACT",
                         failure_reason=f"Refine step returned APPROVED but produced no {target_key}",
                         failure_source="runner", step=step)
        append_failure_history(state=state, step=step, failure_class="HUMAN_RETRY_REQUIRED",
                               failure_code="MISSING_TARGET_ARTIFACT", failure_source="runner")
        state.setdefault("reject_counts", {})[step] = int(state.get("reject_counts", {}).get(step, 0)) + 1
        set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
        state["current_step"] = step
        return state, 1

    pre_checksum = ctx.get("pre_refine_checksum")
    if pre_checksum:
        target_path = PROJECT_ROOT / artifacts[target_key]
        post_checksum = _md5_file(target_path) if target_path.exists() else None
        if post_checksum and post_checksum == pre_checksum:
            set_last_failure(state=state, failure_class="HUMAN_RETRY_REQUIRED",
                             failure_code="NO_OP_REFINEMENT",
                             failure_reason="Refine step made no content change to the target artifact",
                             failure_source="runner", step=step)
            append_failure_history(state=state, step=step, failure_class="HUMAN_RETRY_REQUIRED",
                                   failure_code="NO_OP_REFINEMENT", failure_source="runner")
            state.setdefault("reject_counts", {})[step] = int(state.get("reject_counts", {}).get(step, 0)) + 1
            set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
            state["current_step"] = step
            return state, 1

    history = state.get("loop_history", [])
    if history:
        history[-1]["refine_result"] = "APPROVED"
        history[-1]["refine_at"] = now_iso()
    state["loop_context"] = {
        "active": False, "loop_step": None, "refine_step": None,
        "loop_target_artifact": None, "loop_source_review": None,
        "loop_iteration": 0, "pre_refine_checksum": None,
    }
    state["current_step"] = loop_returns_to
    set_job_status(state, "IN_PROGRESS")
    return state, 0


def _handle_replan_success(
    state: dict[str, Any], step: str, step_cfg: dict[str, Any], artifacts: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    replan_returns_to = step_cfg["replan_returns_to"]
    ctx = state.get("replan_context", {})
    target_key = ctx.get("target_artifact") or step_cfg.get("target_artifact", "PLAN_FILE")

    if not artifacts.get(target_key):
        set_last_failure(state=state, failure_class="HUMAN_RETRY_REQUIRED",
                         failure_code="MISSING_TARGET_ARTIFACT",
                         failure_reason=f"Replan step returned APPROVED but produced no {target_key}",
                         failure_source="runner", step=step)
        append_failure_history(state=state, step=step, failure_class="HUMAN_RETRY_REQUIRED",
                               failure_code="MISSING_TARGET_ARTIFACT", failure_source="runner")
        state.setdefault("reject_counts", {})[step] = int(state.get("reject_counts", {}).get(step, 0)) + 1
        set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
        state["current_step"] = step
        return state, 1

    pre_checksum = ctx.get("pre_replan_checksum")
    if pre_checksum:
        target_path = PROJECT_ROOT / artifacts[target_key]
        post_checksum = _md5_file(target_path) if target_path.exists() else None
        if post_checksum and post_checksum == pre_checksum:
            set_last_failure(state=state, failure_class="HUMAN_RETRY_REQUIRED",
                             failure_code="NO_OP_REPLAN",
                             failure_reason="Replan step made no content change to the target artifact",
                             failure_source="runner", step=step)
            append_failure_history(state=state, step=step, failure_class="HUMAN_RETRY_REQUIRED",
                                   failure_code="NO_OP_REPLAN", failure_source="runner")
            state.setdefault("reject_counts", {})[step] = int(state.get("reject_counts", {}).get(step, 0)) + 1
            set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
            state["current_step"] = step
            return state, 1

    history = state.get("replan_history", [])
    if history:
        history[-1]["replan_result"] = "APPROVED"
        history[-1]["replan_at"] = now_iso()
    state["replan_context"] = {
        "active": False, "source_review_step": None, "replan_step": None,
        "target_artifact": None, "source_review_file": None, "replan_attempt": 0,
        "pre_replan_checksum": None, "trigger_reason": None, "blocking_issues": [],
        "previous_blocking_issue_count": 0, "previous_blocking_issue_severity": 0,
    }
    state["loop_context"] = {
        "active": False, "loop_step": None, "refine_step": None,
        "loop_target_artifact": None, "loop_source_review": None,
        "loop_iteration": 0, "pre_refine_checksum": None,
    }
    state["current_step"] = replan_returns_to
    set_job_status(state, "IN_PROGRESS")
    return state, 0


def _handle_review_approval(
    state: dict[str, Any], step: str, step_cfg: dict[str, Any], coder_used: str,
) -> tuple[dict[str, Any], int]:
    state["model_approved_steps"] = list(dict.fromkeys(
        state.setdefault("model_approved_steps", []) + [step]
    ))
    review_state = state.setdefault("review_state", default_review_state())
    review_state["reviewer_step"] = step
    review_state["coder_used"] = coder_used
    review_state["review_decision"] = "APPROVED"
    review_state["review_decided_at"] = now_iso()
    review_state["human_decision"] = "PENDING"
    set_job_status(state, "WAITING_FOR_HUMAN_APPROVAL")
    state["pending_human_approval_for"] = step
    state["current_step"] = step
    return state, 0


def _handle_task_exec_success(state: dict[str, Any], step: str) -> tuple[dict[str, Any], int]:
    state["completed_steps"] = list(dict.fromkeys(state.setdefault("completed_steps", []) + [step]))
    set_job_status(state, "IN_PROGRESS")
    state["current_step"] = "review_task"
    return state, 0


def _handle_task_queue_success(
    state: dict[str, Any], step: str, artifacts: dict[str, Any],
) -> tuple[dict[str, Any], int]:
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
    group_cfg: dict[str, Any], state: dict[str, Any], step: str,
) -> tuple[dict[str, Any], int]:
    state["completed_steps"] = list(dict.fromkeys(state.setdefault("completed_steps", []) + [step]))
    next_step = get_next_step_skipping_refine_replan(group_cfg, state)
    if next_step is None:
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
    else:
        set_job_status(state, "IN_PROGRESS")
        state["current_step"] = next_step
    return state, 0


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
        return state

    state["completed_steps"] = list(dict.fromkeys(completed_steps + [step]))
    state["pending_human_approval_for"] = None

    if group_name == "delivery_planning_v1" and step == "review_task_graph":
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
        save_job(group_name, state["job_id"], state)
        return state

    next_step = get_next_step_skipping_refine_replan(group_cfg, state)
    if next_step is None:
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
    else:
        set_job_status(state, "IN_PROGRESS")
        state["current_step"] = next_step
    save_job(group_name, state["job_id"], state)
    return state


def force_approve_step(
    *, group_name: str, group_cfg: dict[str, Any], state: dict[str, Any], step: str,
) -> dict[str, Any]:
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
        return state

    if group_name == "delivery_planning_v1" and step == "review_task_graph":
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
        save_job(group_name, state["job_id"], state)
        return state

    next_step = get_next_step_skipping_refine_replan(group_cfg, state)
    if next_step is None:
        set_job_status(state, "COMPLETED")
        state["current_step"] = None
    else:
        set_job_status(state, "IN_PROGRESS")
        state["current_step"] = next_step
    save_job(group_name, state["job_id"], state)
    return state


# ---------------------------------------------------------------------------
# PRE-INIT promotion (initiative_intake_v1 only)
# ---------------------------------------------------------------------------

def _derive_init_path_from_pre_init(pre_init_path: str) -> str:
    rel = Path(pre_init_path)
    if rel.parent != Path("docs/delivery/01_initiatives/pre_init"):
        raise ValueError(f"Unexpected PRE_INIT_FILE path for promotion: {pre_init_path!r}")
    name = rel.name
    if not name.startswith("PRE-INIT-"):
        raise ValueError(f"Unexpected PRE_INIT_FILE name for promotion: {pre_init_path!r}")
    init_name = "INIT-" + name.removeprefix("PRE-INIT-")
    return str(Path("docs/delivery/01_initiatives") / init_name)


def _promote_pre_init_to_init(state: dict[str, Any]) -> str:
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
    previous_status = get_job_status(state)
    if previous_status in {"WAITING_FOR_AUTO_RETRY", "WAITING_FOR_HUMAN_INTERVENTION"}:
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
    current_count = int(state.get("reject_counts", {}).get(step, 0))
    if max_rejects >= 0 and current_count >= max_rejects:
        raise ValueError(
            f"Step {step!r} for job {state['job_id']} has reached max rejects "
            f"({current_count}/{max_rejects}). Use --new-job or reset the job explicitly."
        )


# ---------------------------------------------------------------------------
# Pre-run failure classification
# ---------------------------------------------------------------------------

def looks_like_transient_error(message: str) -> bool:
    hints = ("connection error", "fetch failed", "timed out", "timeout", "temporar",
              "rate limit", "429", "service unavailable", "api error", "network error")
    return any(hint in message.lower() for hint in hints)


def classify_pre_run_failure(exc: Exception) -> dict[str, str]:
    message = str(exc).strip()
    lowered = message.lower()
    if looks_like_transient_error(message):
        return build_failure_envelope(
            failure_class="AUTO_RETRYABLE", failure_code="TRANSIENT_PRE_RUN_FAILURE",
            failure_reason=message, failure_source="runner",
        )
    if isinstance(exc, FileNotFoundError):
        code = "MISSING_REQUIRED_FILE"
        if "prompt file not found" in lowered or "missing static reference file" in lowered:
            code = "MISSING_TEMPLATE_OR_REFERENCE"
        elif "missing required job init input" in lowered or "missing required input artifact" in lowered:
            code = "MISSING_INPUT_ARTIFACT"
        elif "job state not found" in lowered:
            code = "MISSING_JOB_STATE"
        return build_failure_envelope(
            failure_class="HUMAN_RETRY_REQUIRED", failure_code=code,
            failure_reason=message, failure_source="runner",
        )
    if isinstance(exc, json.JSONDecodeError):
        return build_failure_envelope(
            failure_class="FATAL", failure_code="CORRUPTED_JOB_STATE",
            failure_reason=message, failure_source="runner",
        )
    if isinstance(exc, ValueError):
        if any(t in lowered for t in ("coder executable not found", "is not allowed for step", "no coder specified")):
            code = "UNKNOWN_CODER" if "coder executable not found" in lowered else "INVALID_RUNNER_CONFIGURATION"
            return build_failure_envelope(
                failure_class="HUMAN_RETRY_REQUIRED", failure_code=code,
                failure_reason=message, failure_source="runner",
            )
        if any(t in lowered for t in ("waiting for human approval", "waiting for human intervention",
                                       "multiple active jobs match", "has reached max rejects",
                                       "is not defined for template group")):
            if "waiting for human approval" in lowered:
                code = "WAITING_FOR_HUMAN_APPROVAL"
            elif "multiple active jobs match" in lowered:
                code = "MULTIPLE_ACTIVE_JOBS"
            elif "has reached max rejects" in lowered:
                code = "MAX_REJECTS_REACHED"
            else:
                code = "PRE_RUN_INTERVENTION_REQUIRED"
            return build_failure_envelope(
                failure_class="HUMAN_RETRY_REQUIRED", failure_code=code,
                failure_reason=message, failure_source="runner",
            )
    return build_failure_envelope(
        failure_class="FATAL", failure_code="PRE_RUN_FAILURE",
        failure_reason=message, failure_source="runner",
    )
