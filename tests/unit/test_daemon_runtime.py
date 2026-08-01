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


def test_build_job_sync_payload_resolves_relative_artifacts_from_target_project_root() -> None:
    payload = build_job_sync_payload(
        job={
            "job_status": "IN_PROGRESS",
            "target_project_root": "D:/repo-target",
            "artifacts": {"CODEBASE_SCAN_SNAPSHOT": "docs/repo/codebase/04_changes/snapshot.json"},
            "review_state": {},
        },
        step_result={"status": "APPROVED", "outcome": "approved", "remark": "ok"},
        step_run_id="step-1",
    )

    assert payload["output_payload"]["CODEBASE_SCAN_SNAPSHOT"].replace("\\", "/") == (
        "D:/repo-target/docs/repo/codebase/04_changes/snapshot.json"
    )


def test_build_job_sync_payload_clears_one_shot_run_control_flags() -> None:
    payload = build_job_sync_payload(
        job={
            "job_status": "COMPLETED",
            "review_state": {},
            "context_payload": {
                "__run_control": {
                    "approve_requested": True,
                    "retry_requested": True,
                    "action_step": "review_step",
                    "feedback": "operator note",
                }
            },
        },
        step_result={"status": "APPROVED", "outcome": "approved", "remark": "ok"},
        step_run_id="step-1",
    )

    assert payload["context_payload"]["__run_control"] == {
        "approve_requested": False,
        "reject_requested": False,
        "resume_requested": False,
        "retry_requested": False,
        "stop_requested": False,
        "action_step": None,
        "feedback": None,
    }
