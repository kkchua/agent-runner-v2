from __future__ import annotations

from agent_runner_v2.daemon_runtime import build_job_sync_payload


def test_build_job_sync_payload_uses_review_decision_fields() -> None:
    payload = build_job_sync_payload(
        job={
            "job_status": "COMPLETED",
            "completed_steps": ["audit_docs"],
            "artifacts": {"REVIEW_FILE_SUGGESTED": "docs/review.md"},
            "review_state": {
                "review_decision": "APPROVED",
                "human_decision": "NOT_REQUIRED",
                "final_decision": "APPROVED",
                "remark": "Audit passed.",
                "findings": [],
            },
        },
        step_result={"status": "APPROVED", "outcome": "approved", "remark": "Audit passed."},
        step_run_id="step-1",
    )

    assert payload["review"] == {
        "review_type": "step_review",
        "decision": "APPROVED",
        "remark": "Audit passed.",
        "findings": [],
        "evidence": None,
        "full_result": None,
    }
