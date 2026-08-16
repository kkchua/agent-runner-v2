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


def test_refine_target_step_without_active_loop_uses_normal_advance(monkeypatch) -> None:
    """A step that is a refine target must NOT go through _handle_refine_success
    when no refine loop is active (first-attempt success).  Regression test for
    MISSING_TARGET_ARTIFACT false positive on generate steps in workflow_builder_v2."""
    monkeypatch.setattr(job_state, "send_step_notification", lambda *args, **kwargs: None)
    monkeypatch.setattr(job_state, "clear_last_failure", lambda state: None)
    monkeypatch.setattr(job_state, "now_iso", lambda: "2026-08-07T23:00:00")

    advanced_steps: list[str] = []
    monkeypatch.setattr(
        job_state,
        "_advance_to_next",
        lambda group_cfg, state, step, step_cfg=None: (
            advanced_steps.append(step) or (state, 0)
        ),
    )

    # gatekeep_component_schema has on_reject_refine pointing to generate_component_schema
    group_cfg = {
        "step_configs": {
            "gatekeep_component_schema": {
                "on_reject_refine": {
                    "step": "generate_component_schema",
                    "artifact": "GATEKEEP_COMPONENT_SCHEMA_FILE",
                },
            },
        },
    }

    state = {
        "template_group": "workflow_builder_v2",
        "completed_steps": [],
        "reject_counts": {},
        "auto_retry_count_by_step": {},
        "human_retry_count_by_step": {},
        "loop_context": {"active": False},
        "review_state": {
            "reviewer_step": "gatekeep_component_schema",
            "coder_used": "opencode",
            "review_decision": "PENDING",
            "review_decided_at": None,
            "human_decision": "PENDING",
            "human_decided_at": None,
            "human_actor": None,
            "final_decision": None,
            "final_decision_source": None,
            "review_iteration": 1,
        },
        "artifacts": {
            "COMPONENT_SCHEMA_FILE": "runs/WBUILD2-930stvid/COMPONENT_SCHEMA-01.md",
        },
    }

    updated, exit_code = job_state.advance_step(
        group_cfg=group_cfg,
        state=state,
        step="generate_component_schema",
        step_cfg={},
        result_status="APPROVED",
        coder_used="opencode",
    )

    assert exit_code == 0
    assert advanced_steps == ["generate_component_schema"]
    # Must NOT have set MISSING_TARGET_ARTIFACT failure
    assert updated.get("last_failure_code") != "MISSING_TARGET_ARTIFACT"
    assert updated.get("job_status") != "WAITING_FOR_HUMAN_INTERVENTION"


def test_enforce_retry_limit_before_run_allows_initial_attempt_when_max_rejects_zero() -> None:
    state = {
        "job_id": "00BOOT-GEN-TEST-001",
        "reject_counts": {
            "validate_bootstrap_lifecycle_sources": 0,
        },
    }

    job_state.enforce_retry_limit_before_run(
        state=state,
        step="validate_bootstrap_lifecycle_sources",
        max_rejects=0,
    )


def test_enforce_retry_limit_before_run_blocks_retry_when_max_rejects_zero() -> None:
    state = {
        "job_id": "00BOOT-GEN-TEST-001",
        "reject_counts": {
            "validate_bootstrap_lifecycle_sources": 1,
        },
    }

    try:
        job_state.enforce_retry_limit_before_run(
            state=state,
            step="validate_bootstrap_lifecycle_sources",
            max_rejects=0,
        )
        raise AssertionError("Expected ValueError when retrying with max_rejects=0")
    except ValueError as exc:
        assert "has reached max rejects" in str(exc)
