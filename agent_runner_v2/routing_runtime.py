from __future__ import annotations

from typing import Any

from .task_runtime import task_queue_current_item


def get_next_step_skipping_refine_replan(group_cfg: dict[str, Any], completed_steps: list[str]) -> str | None:
    completed = set(completed_steps)
    skip_steps: set[str] = set()
    for sc in group_cfg.get("step_configs", {}).values():
        for key in ("on_reject_refine", "on_exhaust_replan"):
            candidate = (sc.get(key) or {}).get("step")
            if candidate:
                skip_steps.add(str(candidate))
    for step in group_cfg.get("steps", []):
        lowered = str(step).lower()
        if "replan" in lowered or "refine" in lowered:
            skip_steps.add(str(step))
    for step in group_cfg.get("steps", []):
        if step not in completed and step not in skip_steps:
            return str(step)
    return None


def predict_next_step_after_approved(
    *,
    group_cfg: dict[str, Any],
    state: dict[str, Any],
    step: str,
    step_cfg: dict[str, Any],
) -> str | None:
    if step_cfg.get("loop_returns_to"):
        return str(step_cfg["loop_returns_to"])

    if step_cfg.get("replan_returns_to"):
        return str(step_cfg["replan_returns_to"])

    if step_cfg.get("requires_human_approval_after"):
        return step

    template_group = str(state.get("template_group") or "")
    if template_group == "task_execution_v1" and step == "task":
        return "review_task"

    if template_group == "delivery_planning_v1" and step == "task":
        queue = state.get("task_generation_state")
        if isinstance(queue, dict) and queue.get("ordered_tasks"):
            return "review_task" if task_queue_current_item(state) is not None else step

    completed_steps = list(dict.fromkeys(list(state.get("completed_steps", [])) + [step]))
    onsuccess = str(step_cfg.get("onsuccess") or "").strip()
    if onsuccess:
        return onsuccess
    return get_next_step_skipping_refine_replan(group_cfg, completed_steps)
