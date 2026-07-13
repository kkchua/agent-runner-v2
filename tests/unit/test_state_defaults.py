from __future__ import annotations

from agent_runner_v2.state_defaults import (
    default_loop_context,
    default_replan_context,
    default_review_state,
    default_task_execution_binding,
)


def test_default_review_state_shape() -> None:
    state = default_review_state()

    assert state["review_decision"] == "PENDING"
    assert state["human_decision"] == "PENDING"
    assert state["final_decision"] is None


def test_default_task_execution_binding_shape() -> None:
    binding = default_task_execution_binding()

    assert binding["task_graph_id"] is None
    assert binding["task_node_id"] is None
    assert binding["bound_at"] is None


def test_default_loop_context_supports_active_values() -> None:
    ctx = default_loop_context(
        active=True,
        loop_step="review_docs",
        refine_step="refine_docs",
        target_artifact="SYSTEM_DOCS_INDEX",
        review_file="docs/review.md",
        iteration=2,
    )

    assert ctx["active"] is True
    assert ctx["loop_step"] == "review_docs"
    assert ctx["loop_iteration"] == 2


def test_default_replan_context_supports_active_values() -> None:
    ctx = default_replan_context(
        active=True,
        source_review_step="review_docs",
        replan_step="replan_docs",
        target_artifact="SYSTEM_DOCS_INDEX",
        review_file="docs/review.md",
        replan_attempt=3,
        trigger_reason="validation_failed",
    )

    assert ctx["active"] is True
    assert ctx["replan_step"] == "replan_docs"
    assert ctx["replan_attempt"] == 3
    assert ctx["blocking_issues"] == []
