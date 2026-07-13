from __future__ import annotations

from typing import Any


def default_review_state() -> dict[str, Any]:
    return {
        "artifact_type": None,
        "artifact_key": None,
        "artifact_path": None,
        "reviewer_step": None,
        "review_iteration": 0,
        "review_decision": "PENDING",
        "review_decided_at": None,
        "coder_used": None,
        "human_decision": "PENDING",
        "human_decided_at": None,
        "human_actor": None,
        "final_decision": None,
        "final_decision_source": None,
    }


def default_task_execution_binding() -> dict[str, Any]:
    return {
        "task_graph_id": None,
        "task_graph_file": None,
        "task_graph_checksum": None,
        "plan_id": None,
        "plan_file": None,
        "task_node_id": None,
        "task_title": None,
        "task_node_snapshot": None,
        "bound_at": None,
    }


def default_loop_context(
    *,
    active: bool = False,
    loop_step: str | None = None,
    refine_step: str | None = None,
    target_artifact: str | None = None,
    review_file: str | None = None,
    iteration: int = 0,
    pre_refine_checksum: str | None = None,
) -> dict[str, Any]:
    return {
        "active": active,
        "loop_step": loop_step,
        "refine_step": refine_step,
        "loop_target_artifact": target_artifact,
        "loop_source_review": review_file,
        "loop_iteration": iteration,
        "pre_refine_checksum": pre_refine_checksum,
    }


def default_replan_context(
    *,
    active: bool = False,
    source_review_step: str | None = None,
    replan_step: str | None = None,
    target_artifact: str | None = None,
    review_file: str | None = None,
    replan_attempt: int = 0,
    pre_replan_checksum: str | None = None,
    trigger_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "active": active,
        "source_review_step": source_review_step,
        "replan_step": replan_step,
        "target_artifact": target_artifact,
        "source_review_file": review_file,
        "replan_attempt": replan_attempt,
        "pre_replan_checksum": pre_replan_checksum,
        "trigger_reason": trigger_reason,
        "blocking_issues": [],
        "previous_blocking_issue_count": 0,
        "previous_blocking_issue_severity": 0,
    }
