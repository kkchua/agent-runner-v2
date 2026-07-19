from __future__ import annotations

from pathlib import Path

from agent_runner_v2.recovery_runtime import (
    activate_refine_loop,
    activate_replan,
    handle_recovery_budget_exceeded,
)


def test_handle_recovery_budget_exceeded_sets_failure_and_waiting() -> None:
    failures: list[dict] = []
    history: list[dict] = []
    statuses: list[str] = []
    state = {}
    reject_counts = {}

    updated, exit_code = handle_recovery_budget_exceeded(
        state=state,
        step="review_docs",
        reject_counts=reject_counts,
        set_last_failure=lambda **kwargs: failures.append(kwargs),
        append_failure_history=lambda **kwargs: history.append(kwargs),
        set_job_status=lambda s, v: (statuses.append(v), s.__setitem__("job_status", v), s.__setitem__("status", v)),
    )

    assert exit_code == 1
    assert updated["current_step"] == "review_docs"
    assert reject_counts["review_docs"] == 1
    assert failures[0]["failure_code"] == "PLANNING_ATTEMPT_BUDGET_EXCEEDED"
    assert history[0]["failure_code"] == "PLANNING_ATTEMPT_BUDGET_EXCEEDED"
    assert statuses == ["WAITING_FOR_HUMAN_INTERVENTION"]


def test_activate_refine_loop_sets_loop_context_and_history() -> None:
    statuses: list[str] = []
    cleared: list[dict] = []
    state = {}

    updated, exit_code = activate_refine_loop(
        state=state,
        step="review_docs",
        refine_step="refine_docs",
        target_artifact="DOC",
        review_file="docs/review.md",
        iteration=2,
        now_iso=lambda: "2026-07-12T13:00:00",
        clear_last_failure=lambda s: cleared.append(dict(s)),
        set_job_status=lambda s, v: (statuses.append(v), s.__setitem__("job_status", v), s.__setitem__("status", v)),
    )

    assert exit_code == 0
    assert updated["current_step"] == "refine_docs"
    assert updated["loop_context"]["loop_iteration"] == 2
    assert updated["loop_history"][-1]["reject_step"] == "review_docs"
    assert updated["loop_history"][-1]["reject_kind"] == "review"
    assert updated["loop_history"][-1]["reject_result"] == "REJECTED"
    assert updated["loop_history"][-1]["review_file"] == "docs/review.md"
    assert updated["loop_history"][-1]["review_result"] == "REJECTED"
    assert updated["loop_history"][-1]["started_at"] == "2026-07-12T13:00:00"
    assert statuses == ["IN_PROGRESS"]
    assert len(cleared) == 1


def test_activate_refine_loop_tracks_validation_reject_without_mislabeling_review() -> None:
    statuses: list[str] = []
    cleared: list[dict] = []
    state = {}

    updated, exit_code = activate_refine_loop(
        state=state,
        step="validate_layer1_governance_docs",
        refine_step="refine_layer1_governance_docs",
        target_artifact="SYSTEM_DOCS_INDEX",
        review_file="docs/system/00_governance/bootstrap/JOB-validation.md",
        iteration=1,
        now_iso=lambda: "2026-07-18T16:09:47",
        clear_last_failure=lambda s: cleared.append(dict(s)),
        set_job_status=lambda s, v: (statuses.append(v), s.__setitem__("job_status", v), s.__setitem__("status", v)),
    )

    assert exit_code == 0
    entry = updated["loop_history"][-1]
    assert entry["reject_step"] == "validate_layer1_governance_docs"
    assert entry["reject_kind"] == "validation"
    assert entry["reject_result"] == "REJECTED"
    assert entry["reject_file"] == "docs/system/00_governance/bootstrap/JOB-validation.md"
    assert entry["reject_at"] == "2026-07-18T16:09:47"
    assert entry["review_result"] is None
    assert entry["review_at"] is None
    assert entry["started_at"] == "2026-07-18T16:09:47"
    assert statuses == ["IN_PROGRESS"]
    assert len(cleared) == 1


def test_activate_replan_sets_context_history_and_resets_loop(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    target = tmp_path / "plan.md"
    target.write_text("plan", encoding="utf-8")
    statuses: list[str] = []
    cleared: list[dict] = []
    state = {}

    updated, exit_code = activate_replan(
        state=state,
        step="review_docs",
        replan_step="replan_docs",
        target_artifact="PLAN",
        review_file="docs/review.md",
        replan_attempt=1,
        trigger_reason="REFINEMENT_EXHAUSTED",
        artifacts={"PLAN": "plan.md"},
        project_root=tmp_path,
        checksum_file=lambda p: "checksum",
        now_iso=lambda: "2026-07-12T13:00:00",
        clear_last_failure=lambda s: cleared.append(dict(s)),
        set_job_status=lambda s, v: (statuses.append(v), s.__setitem__("job_status", v), s.__setitem__("status", v)),
    )

    assert exit_code == 0
    assert updated["current_step"] == "replan_docs"
    assert updated["replan_context"]["trigger_reason"] == "REFINEMENT_EXHAUSTED"
    assert updated["replan_context"]["pre_replan_checksum"] == "checksum"
    assert updated["loop_context"]["active"] is False
    assert updated["replan_history"][-1]["replan_attempt"] == 1
    assert statuses == ["IN_PROGRESS"]
    assert len(cleared) == 1
