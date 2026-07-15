from __future__ import annotations

import agent_runner_v2.job_state as job_state


def test_advance_step_finalizes_model_review_state_without_human_approval(
    monkeypatch,
) -> None:
    monkeypatch.setattr(job_state, "send_step_notification", lambda *args, **kwargs: None)
    monkeypatch.setattr(job_state, "clear_last_failure", lambda state: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-07-14T16:10:00")
    monkeypatch.setattr(
        job_state,
        "_advance_to_next",
        lambda group_cfg, state, step, step_cfg=None: (state, 0),
    )

    state = {
        "template_group": "00_core_governance_bootstrap_v1",
        "completed_steps": [],
        "reject_counts": {},
        "auto_retry_count_by_step": {},
        "human_retry_count_by_step": {},
        "review_state": {
            "reviewer_step": "review_core_governance_docs",
            "coder_used": "qwen",
            "review_decision": "PENDING",
            "review_decided_at": None,
            "human_decision": "PENDING",
            "human_decided_at": None,
            "human_actor": None,
            "final_decision": None,
            "final_decision_source": None,
            "review_iteration": 1,
        },
    }

    updated, exit_code = job_state.advance_step(
        group_cfg={"steps": ["review_core_governance_docs"]},
        state=state,
        step="review_core_governance_docs",
        step_cfg={},
        result_status="APPROVED",
        coder_used="qwen",
    )

    assert exit_code == 0
    review_state = updated["review_state"]
    assert review_state["review_decision"] == "APPROVED"
    assert review_state["review_decided_at"] == "2026-07-14T16:10:00"
    assert review_state["human_decision"] == "NOT_REQUIRED"
    assert review_state["human_decided_at"] is None
    assert review_state["human_actor"] is None
    assert review_state["final_decision"] == "APPROVED"
    assert review_state["final_decision_source"] == "MODEL"
