from __future__ import annotations

from pathlib import Path

from agent_runner_v2.v2.transition_runtime import complete_recovery_step


def test_complete_recovery_step_resets_loop_and_advances(tmp_path: Path) -> None:
    target = tmp_path / "artifact.md"
    target.write_text("updated", encoding="utf-8")
    statuses: list[str] = []
    state = {
        "reject_counts": {},
        "loop_history": [{"refine_result": None, "refine_at": None}],
        "loop_context": {"active": True},
    }

    updated, exit_code = complete_recovery_step(
        state=state,
        step="refine_docs",
        target_key="DOC",
        artifacts={"DOC": "artifact.md"},
        pre_checksum="before",
        no_op_failure_code="NO_OP_REFINEMENT",
        no_op_failure_reason="no change",
        history_key="loop_history",
        history_result_field="refine_result",
        history_time_field="refine_at",
        next_step="review_docs",
        project_root=tmp_path,
        now_iso=lambda: "2026-07-12T12:00:00",
        set_last_failure=lambda **kwargs: (_ for _ in ()).throw(AssertionError("unexpected failure")),
        append_failure_history=lambda **kwargs: (_ for _ in ()).throw(AssertionError("unexpected history append")),
        set_job_status=lambda s, v: (statuses.append(v), s.__setitem__("job_status", v), s.__setitem__("status", v)),
        checksum_file=lambda p: "after",
        reset_replan_context=False,
    )

    assert exit_code == 0
    assert updated["current_step"] == "review_docs"
    assert updated["loop_history"][-1]["refine_result"] == "APPROVED"
    assert updated["loop_history"][-1]["refine_at"] == "2026-07-12T12:00:00"
    assert updated["loop_context"]["active"] is False
    assert statuses == ["IN_PROGRESS"]


def test_complete_recovery_step_handles_no_op_failure(tmp_path: Path) -> None:
    target = tmp_path / "artifact.md"
    target.write_text("unchanged", encoding="utf-8")
    failures: list[dict] = []
    history: list[dict] = []
    statuses: list[str] = []
    state = {"reject_counts": {}}

    updated, exit_code = complete_recovery_step(
        state=state,
        step="replan_docs",
        target_key="DOC",
        artifacts={"DOC": "artifact.md"},
        pre_checksum="same",
        no_op_failure_code="NO_OP_REPLAN",
        no_op_failure_reason="replan no change",
        history_key="replan_history",
        history_result_field="replan_result",
        history_time_field="replan_at",
        next_step="generate_docs",
        project_root=tmp_path,
        now_iso=lambda: "2026-07-12T12:00:00",
        set_last_failure=lambda **kwargs: failures.append(kwargs),
        append_failure_history=lambda **kwargs: history.append(kwargs),
        set_job_status=lambda s, v: (statuses.append(v), s.__setitem__("job_status", v), s.__setitem__("status", v)),
        checksum_file=lambda p: "same",
        reset_replan_context=True,
    )

    assert exit_code == 1
    assert updated["current_step"] == "replan_docs"
    assert updated["reject_counts"]["replan_docs"] == 1
    assert failures[0]["failure_code"] == "NO_OP_REPLAN"
    assert history[0]["failure_code"] == "NO_OP_REPLAN"
    assert statuses == ["WAITING_FOR_HUMAN_INTERVENTION"]
