"""Phase A caller/persistence regressions using the actual workflow manifest."""
from __future__ import annotations

import copy
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest

from agent_runner_v2 import job_state as js, run_agent, runtime_context
from agent_runner_v2.constants import ARTIFACT_PATH_CODEX_REVIEW, ARTIFACT_PATH_QWEN_PLAN
from agent_runner_v2.step_runner import StepResult
from agent_runner_v2.v2 import workflow_router as router

GROUP = "plan_first_review_v1"
MISSING = object()


@pytest.fixture
def runtime(tmp_path, monkeypatch):
    manifest = Path(__file__).resolve().parents[2] / "workflows" / GROUP / "workflow.toml"
    steps = tomllib.loads(manifest.read_text())["step"]
    config = {"steps": [s["name"] for s in steps], "step_configs": {s["name"]: s for s in steps}}
    saves, notifications, coder_calls = [], [], []
    original_save = js.save_job

    def job_path(group, job_id):
        return tmp_path / "jobs" / group / job_id / "job.json"

    def save(group, job_id, state):
        original_save(group, job_id, state)
        saves.append(copy.deepcopy(state))

    def notify(status, *args, **kwargs):
        notifications.append(status)

    monkeypatch.setattr(js, "job_state_path", job_path)
    monkeypatch.setattr(js, "job_dir", lambda group, job_id: job_path(group, job_id).parent)
    monkeypatch.setattr(js, "save_job", save)
    monkeypatch.setattr(router, "save_job", save)
    for module in (runtime_context, js, router):
        monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    for module in (js, router):
        monkeypatch.setattr(module, "send_step_notification", notify)
        monkeypatch.setattr(module, "send_workflow_notification", notify)

    state = {
        "job_id": "closure", "template_group": GROUP,
        "job_status": "IN_PROGRESS", "status": "IN_PROGRESS",
        "current_step": "generate_plan", "requirements_baseline": 1,
        "plan_revision": 1, "artifacts": {"PLANNING_FOLDER": "Planning/closure"},
        "loop_context": {}, "attempt_records": {}, "completed_steps": [],
    }

    def route(state, step, result):
        return router.route_after_step(
            group_name=GROUP, group_cfg=config, state=state, step=step,
            step_cfg=config["step_configs"][step], step_result=result,
            coder_used="test-coder", max_rejects=3,
        )

    def execute(state, step):
        return run_agent._execute_prepared_step_with_plan_first_attempt(
            prepared=SimpleNamespace(action_name=None, context={}),
            template_group=GROUP, group_cfg=config, state=state, step=step,
            step_cfg=config["step_configs"][step], effective_root=tmp_path,
        )

    def prepare(state):
        return js.prepare_plan_attempt(
            GROUP, state["job_id"], state, "generate_plan",
            config["step_configs"]["generate_plan"], config, {}, tmp_path,
        )

    return SimpleNamespace(
        root=tmp_path, state=state, config=config, saves=saves,
        notifications=notifications, coder_calls=coder_calls, route=route,
        execute=execute, prepare=prepare, path=job_path,
        load=lambda: js.load_job(GROUP, state["job_id"]),
    )


def outcome(path=None, *, status="APPROVED", attempt_id=None):
    return StepResult(
        status=status, remark="same outcome", artifacts={"QWEN_PLAN_FILE": path} if path else {},
        reject_code=None, meta_json_path="", usage_data={}, attempt_id=attempt_id,
    )


@pytest.mark.parametrize("changed", [False, True], ids=["no-op", "changed"])
@pytest.mark.parametrize("absolute_review", [False, True], ids=["relative-review", "absolute-review"])
def test_real_producer_chain(runtime, monkeypatch, changed, absolute_review):
    """Produced review context must survive real preparation and actual recovery."""
    rt = runtime
    folder = rt.state["artifacts"]["PLANNING_FOLDER"]
    prepared_ids, recovery_results = [], []
    original_advance = router.advance_step

    def observe_advance(**kwargs):
        state, code = original_advance(**kwargs)
        if kwargs["step"] == "refine_plan":
            recovery_results.append((code, state.get("last_failure_code")))
        return state, code

    def coder(**kwargs):
        step = kwargs["step"]
        persisted = rt.load()
        aid = persisted["loop_context"]["active_attempt_id"]
        record = persisted["attempt_records"][aid]
        assert record["status"] == "prepared"
        assert record["recovered_context"]["step"] == step
        prepared_ids.append(aid)
        rt.coder_calls.append(step)
        if step == "refine_plan":
            previous = rt.root / ARTIFACT_PATH_QWEN_PLAN(folder, 1, 1)
            assert record["recovered_context"]["pre_refine_checksum"] == js._md5_file(previous)
        relative = record["output_path"]
        target = rt.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("version two" if step == "refine_plan" and changed else "version one")
        return outcome(str(target))  # Actual artifact reporting supports absolute paths.

    monkeypatch.setattr(run_agent, "_execute_prepared_step", coder)
    monkeypatch.setattr(router, "advance_step", observe_advance)
    generated = rt.execute(rt.state, "generate_plan")
    assert generated.attempt_id == prepared_ids[-1]
    state, code = rt.route(rt.state, "generate_plan", generated)
    assert code == 0
    state = rt.load()
    state["artifacts"]["REVIEW_FILE_SUGGESTED"] = "stale-review.md"
    review_relative = ARTIFACT_PATH_CODEX_REVIEW(folder, 1, 1)
    review = rt.root / review_relative
    review.write_text("needs refinement")
    rejected = outcome(status="REJECTED")
    rejected.artifacts = {"CODEX_REVIEW_FILE": str(review) if absolute_review else review_relative}
    state, code = rt.route(state, "codex_review", rejected)
    assert code == 0 and state["current_step"] == "refine_plan"
    state = rt.load()
    assert state["loop_context"]["loop_source_review"] == review_relative
    assert state["artifacts"]["REVIEW_FILE_SUGGESTED"] == review_relative
    baseline_revision = state["plan_revision"]
    before_saves, before_notifications = len(rt.saves), len(rt.notifications)
    refined = rt.execute(state, "refine_plan")
    assert refined.attempt_id == prepared_ids[-1] != generated.attempt_id
    state, code = rt.route(state, "refine_plan", refined)
    assert len(rt.saves) == before_saves + 2  # preparation and authoritative outcome
    persisted = rt.load()
    record = persisted["attempt_records"][refined.attempt_id]
    if changed:
        assert recovery_results == [(0, None)]
        assert code == 0 and record["status"] == "applied"
        assert persisted["plan_revision"] == baseline_revision + 1 == 2
        assert persisted["loop_context"]["active"] is False
        assert persisted["revision_completions"]["b1_r2"]["attempt_id"] == refined.attempt_id
        assert "refine_plan" in persisted["completed_steps"]
        assert rt.notifications[before_notifications:] == ["STEP_COMPLETED"]
    else:
        assert recovery_results == [(1, "NO_OP_REFINEMENT")]
        assert code == 1 and record["status"] == "failed"
        assert persisted["last_failure_code"] == "APPLICATION_FAILURE"
        assert persisted["plan_revision"] == baseline_revision == 1
        assert "refine_plan" not in persisted["completed_steps"]
        assert "b1_r2" not in persisted.get("revision_completions", {})
        assert "STEP_COMPLETED" not in rt.notifications[before_notifications:]
    snapshot = copy.deepcopy(persisted)
    disk = rt.path(GROUP, persisted["job_id"]).read_bytes()
    counts = len(rt.saves), len(rt.notifications), len(rt.coder_calls)
    replayed, replay_code = rt.route(persisted, "refine_plan", refined)
    assert replay_code == code
    assert replayed == persisted == snapshot
    assert counts == (len(rt.saves), len(rt.notifications), len(rt.coder_calls))
    assert rt.path(GROUP, persisted["job_id"]).read_bytes() == disk


@pytest.mark.parametrize("absolute_first", [False, True])
@pytest.mark.parametrize("terminal", ["applied", "failed"])
def test_writer_reload_equivalent_replay(runtime, absolute_first, terminal):
    rt = runtime
    record = rt.prepare(rt.state)
    relative = record["output_path"]
    path = rt.root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("plan")
    first = outcome(str(path) if absolute_first else relative, attempt_id=record["attempt_id"])
    if terminal == "failed":
        committed, expected_code = router._commit_application_failure_from_baseline(
            baseline=rt.state, group_name=GROUP, attempt_id=record["attempt_id"],
            step_result=first, failure_reason="injected application failure", step="generate_plan",
        )
    else:
        committed, expected_code = rt.route(rt.state, "generate_plan", first)
    assert expected_code == (1 if terminal == "failed" else 0)
    assert committed["attempt_records"][record["attempt_id"]]["status"] == terminal
    loaded = rt.load()
    before = copy.deepcopy(loaded)
    disk = rt.path(GROUP, loaded["job_id"]).read_bytes()
    counts = len(rt.saves), len(rt.notifications)
    replay = outcome(relative if absolute_first else str(path), attempt_id=record["attempt_id"])
    state, code = rt.route(loaded, "generate_plan", replay)
    assert code == expected_code
    assert state.get("last_failure_code") == ("APPLICATION_FAILURE" if terminal == "failed" else None)
    assert state == loaded == before
    assert counts == (len(rt.saves), len(rt.notifications))
    assert rt.path(GROUP, loaded["job_id"]).read_bytes() == disk


@pytest.mark.parametrize("value", [MISSING, None, True, False, 1.0, 0, -1, 2, 1],
                         ids=["missing", "none", "true", "false", "float", "zero", "negative", "foreign", "valid"])
def test_record_baseline_validation_through_actual_gate(runtime, value):
    rt = runtime
    record = rt.prepare(rt.state)
    relative = record["output_path"]
    path = rt.root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("plan")
    if value is MISSING:
        record.pop("baseline")
    else:
        record["baseline"] = value
    before = copy.deepcopy(rt.state)
    state, code = rt.route(rt.state, "generate_plan", outcome(relative, attempt_id=record["attempt_id"]))
    valid = type(value) is int and value == 1
    assert code == (0 if valid else 1)
    assert rt.state == before
    if valid:
        assert state["attempt_records"][record["attempt_id"]]["status"] == "applied"
    else:
        assert state["last_failure_code"] == "ELIGIBILITY_FAILURE"
        assert state["attempt_records"][record["attempt_id"]]["status"] == "prepared"
        assert not state.get("revision_completions")


@pytest.mark.parametrize("field", ["requirements_baseline", "plan_revision"])
@pytest.mark.parametrize("value", [None, True, False, 1.0, 0, -1])
def test_invalid_wrapper_state_has_no_save_or_coder(runtime, monkeypatch, field, value):
    rt = runtime
    rt.state[field] = value
    before = copy.deepcopy(rt.state)

    def unexpected_coder(**kwargs):
        rt.coder_calls.append(kwargs["step"])
        pytest.fail("invalid preparation reached coder")

    monkeypatch.setattr(run_agent, "_execute_prepared_step", unexpected_coder)
    with pytest.raises(ValueError):
        rt.execute(rt.state, "generate_plan")
    assert rt.state == before
    assert rt.saves == rt.coder_calls == rt.notifications == []
    assert not rt.path(GROUP, rt.state["job_id"]).exists()


@pytest.mark.parametrize("kind", ["missing-id", "conflicting-owner"])
def test_gate_save_failure_preserves_caller_and_disk(runtime, monkeypatch, kind):
    rt = runtime
    record = rt.prepare(rt.state)
    result = outcome(attempt_id=record["attempt_id"])
    if kind == "missing-id":
        result.attempt_id = None
    else:
        rt.state["attempt_records"][record["attempt_id"]]["job_id"] = "foreign-job"
    js.save_job(GROUP, rt.state["job_id"], rt.state)
    before = copy.deepcopy(rt.state)
    old = rt.path(GROUP, rt.state["job_id"]).read_bytes()
    notifications = list(rt.notifications)
    replacements = []

    def fail_before_replace(src, dst):
        replacements.append((src, dst))
        raise RuntimeError("injected pre-replacement failure")

    monkeypatch.setattr(js.os, "replace", fail_before_replace)
    with pytest.raises(RuntimeError, match="injected pre-replacement failure"):
        rt.route(rt.state, "generate_plan", result)
    assert len(replacements) == 1
    assert rt.state == before
    assert rt.path(GROUP, rt.state["job_id"]).read_bytes() == old
    assert rt.notifications == notifications
