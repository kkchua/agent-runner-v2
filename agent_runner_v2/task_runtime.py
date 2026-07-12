from __future__ import annotations

import datetime as dt
import hashlib
import re
from pathlib import Path
from typing import Any

from .exceptions import PreflightBlockedError
from .runtime_context import PROJECT_ROOT


def _now_iso() -> str:
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def _resolve_repo_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _normalize_document_status(value: str) -> str:
    return re.sub(r"\s+", "_", (value or "").strip().lower().replace("-", "_"))


def _extract_document_status(content: str) -> str | None:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("status:"):
            return stripped.split(":", 1)[1].strip()
    return None


def _extract_document_metadata_value(content: str, key: str) -> str | None:
    bullet_pattern = re.compile(
        rf"^\s*[-*]\s*(?:\*\*)?{re.escape(key)}(?::(?:\*\*)?|\*\*:\s*|:)\s*(.+?)\s*$",
        re.IGNORECASE,
    )
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
            raw = match.group(1).strip()
            backtick = re.match(r"`([^`]+)`", raw)
            return backtick.group(1).strip() if backtick else raw
    return None


def _md5_file(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _make_task_queue_item_id(sequence: int) -> str:
    return f"tgq_{sequence:04d}"


def task_queue_current_item(state: dict[str, Any]) -> dict[str, Any] | None:
    queue = state.get("task_generation_state")
    if not isinstance(queue, dict):
        return None
    current_id = queue.get("current_queue_item_id")
    for item in queue.get("ordered_tasks", []):
        if item.get("queue_item_id") == current_id:
            return item
    return None


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


def extract_task_graph_nodes(task_graph_path: str) -> list[dict[str, Any]]:
    path = _resolve_repo_path(task_graph_path)
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
        ordered.append(
            {
                "queue_item_id": _make_task_queue_item_id(index),
                "task_id": task_node_id,
                "task_node_id": task_node_id,
                "title": title,
                "sequence": index,
                "status": "PENDING",
                "task_file": None,
                "review_step": None,
                "approved_at": None,
            }
        )
    return ordered


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
    task_graph_content = _resolve_repo_path(task_graph_file).read_text(encoding="utf-8")
    task_graph_id = (_extract_document_metadata_value(task_graph_content, "Task Graph ID") or "").strip()
    plan_id = (_extract_document_metadata_value(task_graph_content, "Plan ID") or "").strip()
    if not plan_id:
        raise ValueError(f"Task graph {task_graph_file!r} is missing Plan ID metadata.")
    task_node = matches[0]
    return {
        "task_graph_id": task_graph_id or None,
        "task_graph_file": task_graph_file,
        "task_graph_checksum": _md5_file(_resolve_repo_path(task_graph_file)),
        "plan_id": plan_id,
        "plan_file": find_plan_file_by_id(plan_id),
        "task_node_id": str(task_node.get("task_node_id") or ""),
        "task_title": str(task_node.get("title") or ""),
        "task_node_snapshot": {
            "task_node_id": str(task_node.get("task_node_id") or ""),
            "title": str(task_node.get("title") or ""),
            "sequence": int(task_node.get("sequence") or 0),
        },
        "bound_at": _now_iso(),
    }


def build_task_execution_binding_from_ids(*, task_graph_id: str, task_node_id: str) -> dict[str, Any]:
    task_graph_file = find_task_graph_file_by_id(task_graph_id)
    binding = build_task_execution_binding(task_graph_file=task_graph_file, task_node_id=task_node_id)
    if not binding.get("task_graph_id"):
        binding["task_graph_id"] = task_graph_id.strip()
    return binding


def _task_queue_has_remaining_work(state: dict[str, Any]) -> bool:
    queue = state.get("task_generation_state")
    if not isinstance(queue, dict):
        return False
    return any(item.get("status") != "APPROVED" for item in queue.get("ordered_tasks", []))


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
    actual_path = _resolve_repo_path(str(task_graph_path))
    if not actual_path.exists() or not actual_path.is_file():
        raise PreflightBlockedError(f"Approved source task graph is missing for step {step!r}: {task_graph_path}")
    if _md5_file(actual_path) != stored_checksum:
        raise PreflightBlockedError(
            f"Approved task graph has changed since queue initialization for step {step!r}."
        )
    current_item = task_queue_current_item(state)
    if current_item is None:
        if _task_queue_has_remaining_work(state):
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
    actual_path = _resolve_repo_path(task_graph_path)
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
            f"Approved task node snapshot has changed since execution binding was created for step {step!r}."
        )
