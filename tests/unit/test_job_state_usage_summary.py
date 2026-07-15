from __future__ import annotations

from agent_runner_v2.job_state import record_step_usage


def test_record_step_usage_counts_duration_only_usage() -> None:
    state = {"step_usage": {}}

    record_step_usage(
        state,
        "generate_docs",
        {
            "usage_source": "not_available",
            "duration_ms": 1250,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "cost": None,
        },
    )
    record_step_usage(state, "validate_docs", {})

    assert state["usage_summary"] == {
        "steps_with_usage": 1,
        "steps_without_usage": 1,
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "cost": None,
        "duration_ms": 1250,
    }
