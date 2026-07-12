from __future__ import annotations

from agent_runner_v2 import failure_runtime


def test_set_and_clear_last_failure_updates_pending_intervention() -> None:
    state: dict[str, object] = {}

    failure_runtime.set_last_failure(
        state=state,
        failure_class="HUMAN_RETRY_REQUIRED",
        failure_code="MODEL_REJECTED",
        failure_reason="needs retry",
        failure_source="model",
        step="validate_docs",
    )

    assert state["last_failure_class"] == "HUMAN_RETRY_REQUIRED"
    assert state["last_failure_code"] == "MODEL_REJECTED"
    assert state["pending_intervention_for"] == "validate_docs"

    failure_runtime.clear_last_failure(state)

    assert state["last_failure_class"] is None
    assert state["last_failure_code"] is None
    assert state["pending_intervention_for"] is None


def test_append_failure_history_records_entry() -> None:
    state: dict[str, object] = {}

    failure_runtime.append_failure_history(
        state=state,
        step="review_docs",
        failure_class="AUTO_RETRYABLE",
        failure_code="META_JSON_INVALID",
        failure_source="runner",
    )

    history = state["failure_history"]
    assert isinstance(history, list)
    assert history[0]["step"] == "review_docs"
    assert history[0]["failure_class"] == "AUTO_RETRYABLE"
    assert history[0]["failure_code"] == "META_JSON_INVALID"
    assert history[0]["failure_source"] == "runner"
    assert history[0]["timestamp"]
