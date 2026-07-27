"""Unit tests for daemon_runtime sync payload construction.

Tests the pure functions that build sync payloads and map job status.
These functions have no external dependencies - they take dicts as input
and produce dicts as output, making them straightforward to unit test.
"""
from __future__ import annotations

from agent_runner_v2.daemon_runtime import (
    build_job_sync_payload,
    _map_job_status_to_run_status,
)


class TestMapJobStatusToRunStatus:
    """Test the job status to run_status mapping."""

    def test_in_progress_maps_to_pending(self) -> None:
        assert _map_job_status_to_run_status("IN_PROGRESS") == "pending"

    def test_completed_maps_to_completed(self) -> None:
        assert _map_job_status_to_run_status("COMPLETED") == "completed"

    def test_failed_maps_to_failed(self) -> None:
        assert _map_job_status_to_run_status("FAILED") == "failed"

    def test_waiting_for_human_approval_maps_to_awaiting_human(self) -> None:
        assert _map_job_status_to_run_status("WAITING_FOR_HUMAN_APPROVAL") == "awaiting_human"

    def test_waiting_for_human_intervention_maps_to_awaiting_human(self) -> None:
        assert _map_job_status_to_run_status("WAITING_FOR_HUMAN_INTERVENTION") == "awaiting_human"

    def test_waiting_for_human_maxretried_maps_to_awaiting_human(self) -> None:
        assert _map_job_status_to_run_status("WAITING_FOR_HUMAN_MAXRETRIED") == "awaiting_human"

    def test_waiting_for_auto_retry_maps_to_pending(self) -> None:
        assert _map_job_status_to_run_status("WAITING_FOR_AUTO_RETRY") == "pending"

    def test_unknown_status_defaults_to_pending(self) -> None:
        assert _map_job_status_to_run_status("UNKNOWN_STATUS") == "pending"

    def test_lowercase_input_works(self) -> None:
        assert _map_job_status_to_run_status("in_progress") == "pending"

    def test_mixed_case_input_works(self) -> None:
        assert _map_job_status_to_run_status("In_Progress") == "pending"


class TestBuildJobSyncPayload:
    """Test the sync payload construction from job state."""

    def test_builds_basic_payload_with_pending_status(self) -> None:
        """Test payload construction for a running job."""
        job = {
            "job_status": "IN_PROGRESS",
            "current_step": "generate_prompts",
            "artifacts": {"DOC_1": "/path/to/doc.md"},
            "completed_steps": ["init"],
            "failed_steps": [],
        }
        step_result = {
            "status": "APPROVED",
            "outcome": "approved",
            "coder_used": "qwen-coder",
            "remark": "Step completed",
        }

        payload = build_job_sync_payload(
            job=job,
            step_result=step_result,
            step_run_id="step-run-abc",
        )

        assert payload["run_status"] == "pending"
        assert payload["next_step_name"] == "generate_prompts"
        assert payload["step_status"] == "approved"
        assert payload["step_coder"] == "qwen-coder"
        assert len(payload["artifacts"]) == 1
        assert payload["artifacts"][0]["artifact_key"] == "DOC_1"

    def test_builds_payload_for_completed_job(self) -> None:
        """Test payload construction for a completed job."""
        job = {
            "job_status": "COMPLETED",
            "current_step": None,
            "artifacts": {"OUTPUT_FILE": "/path/to/output.md"},
            "completed_steps": ["init", "generate", "review"],
            "failed_steps": [],
        }
        step_result = {
            "status": "APPROVED",
            "outcome": "approved",
            "coder_used": "qwen-coder",
            "remark": "Workflow completed",
        }

        payload = build_job_sync_payload(
            job=job,
            step_result=step_result,
            step_run_id="step-run-final",
        )

        assert payload["run_status"] == "completed"
        assert payload["next_step_name"] is None
        assert payload["step_status"] == "approved"

    def test_builds_payload_for_failed_job(self) -> None:
        """Test payload construction for a failed job."""
        job = {
            "job_status": "FAILED",
            "current_step": "generate",
            "artifacts": {},
            "completed_steps": ["init"],
            "failed_steps": ["generate"],
            "last_failure_reason": "Coder crashed",
        }
        step_result = {
            "status": "FAILED",
            "outcome": "failed",
            "coder_used": "qwen-coder",
            "remark": "Step failed",
        }

        payload = build_job_sync_payload(
            job=job,
            step_result=step_result,
            step_run_id="step-run-failed",
        )

        assert payload["run_status"] == "failed"
        assert payload["error_message"] == "Coder crashed"
        assert any(e["event_type"] == "RUN_FAILED" for e in payload["events"])

    def test_builds_payload_for_awaiting_human(self) -> None:
        """Test payload construction for human approval wait."""
        job = {
            "job_status": "WAITING_FOR_HUMAN_APPROVAL",
            "current_step": "review",
            "artifacts": {"REVIEW_FILE": "/path/to/review.md"},
            "completed_steps": ["init", "generate"],
            "failed_steps": [],
            "review_state": {
                "final_decision": "PENDING",
            },
        }
        step_result = {
            "status": "APPROVED",
            "outcome": "approved",
            "coder_used": "reviewer",
            "remark": "Review completed, awaiting human",
        }

        payload = build_job_sync_payload(
            job=job,
            step_result=step_result,
            step_run_id="step-run-review",
        )

        assert payload["run_status"] == "awaiting_human"
        assert any(e["event_type"] == "HUMAN_APPROVAL_REQUIRED" for e in payload["events"])

    def test_filters_null_artifacts(self) -> None:
        """Test that null/empty artifacts are filtered out."""
        job = {
            "job_status": "IN_PROGRESS",
            "current_step": "next_step",
            "artifacts": {
                "VALID_DOC": "/path/to/valid.md",
                "NULL_DOC": None,
                "EMPTY_DOC": "",
            },
            "completed_steps": [],
            "failed_steps": [],
        }
        step_result = {
            "status": "APPROVED",
            "outcome": "approved",
        }

        payload = build_job_sync_payload(
            job=job,
            step_result=step_result,
            step_run_id="step-run-test",
        )

        artifact_keys = [a["artifact_key"] for a in payload["artifacts"]]
        assert "VALID_DOC" in artifact_keys
        assert "NULL_DOC" not in artifact_keys
        assert "EMPTY_DOC" not in artifact_keys

    def test_normalizes_windows_paths_in_artifacts(self) -> None:
        """Test that Windows backslashes are converted to forward slashes."""
        job = {
            "job_status": "IN_PROGRESS",
            "current_step": "next_step",
            "artifacts": {"DOC": r"D:\path\to\doc.md"},
            "completed_steps": [],
            "failed_steps": [],
        }
        step_result = {
            "status": "APPROVED",
            "outcome": "approved",
        }

        payload = build_job_sync_payload(
            job=job,
            step_result=step_result,
            step_run_id="step-run-test",
        )

        # Artifact path should use forward slashes
        assert payload["artifacts"][0]["file_path"] == "D:/path/to/doc.md"

    def test_includes_review_when_decision_made(self) -> None:
        """Test that review payload is included when decision is final."""
        job = {
            "job_status": "IN_PROGRESS",
            "current_step": "next_step",
            "artifacts": {},
            "completed_steps": [],
            "failed_steps": [],
            "review_state": {
                "final_decision": "APPROVED",
                "remark": "Looks good",
                "findings": ["Minor typo"],
            },
        }
        step_result = {
            "status": "APPROVED",
            "outcome": "approved",
            "remark": "Review approved",
        }

        payload = build_job_sync_payload(
            job=job,
            step_result=step_result,
            step_run_id="step-run-review",
        )

        assert payload["review"] is not None
        assert payload["review"]["decision"] == "APPROVED"
        assert payload["review"]["remark"] == "Looks good"

    def test_skips_review_when_decision_pending(self) -> None:
        """Test that review payload is omitted when decision is PENDING."""
        job = {
            "job_status": "IN_PROGRESS",
            "current_step": "next_step",
            "artifacts": {},
            "completed_steps": [],
            "failed_steps": [],
            "review_state": {
                "final_decision": "PENDING",
            },
        }
        step_result = {
            "status": "APPROVED",
            "outcome": "approved",
        }

        payload = build_job_sync_payload(
            job=job,
            step_result=step_result,
            step_run_id="step-run-review",
        )

        assert payload["review"] is None

    def test_filters_artifacts_to_allowed_keys_when_specified(self) -> None:
        """Test that artifacts are filtered to workflow-declared keys."""
        job = {
            "job_status": "IN_PROGRESS",
            "current_step": "next_step",
            "artifacts": {
                "DECLARED_KEY": "/path/to/declared.md",
                "UNDECLARED_KEY": "/path/to/undeclared.md",
            },
            "completed_steps": [],
            "failed_steps": [],
            "workflow_artifact_keys": ["DECLARED_KEY"],
        }
        step_result = {
            "status": "APPROVED",
            "outcome": "approved",
        }

        payload = build_job_sync_payload(
            job=job,
            step_result=step_result,
            step_run_id="step-run-test",
        )

        artifact_keys = [a["artifact_key"] for a in payload["artifacts"]]
        assert "DECLARED_KEY" in artifact_keys
        assert "UNDECLARED_KEY" not in artifact_keys