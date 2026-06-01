"""Tests for agent_runner_v2.job_state — Job lifecycle, state machine, migration, and more."""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

import pytest

from agent_runner_v2.job_state import (
    CURRENT_SCHEMA_VERSION,
    NON_TERMINAL_JOB_STATUSES,
    REVIEW_DECISIONS,
    HUMAN_DECISIONS,
    FINAL_DECISION_SOURCES,
    CONTROL_CLASSES,
    FAILURE_SOURCES,
    now_iso,
    get_job_status,
    set_job_status,
    ensure_dir,
    resolve_repo_path,
    normalize_repo_relative_path,
    group_dir,
    job_dir,
    job_state_path,
    get_step_index,
    make_step_dir,
    load_json,
    save_json,
    save_json_atomic,
    save_text,
    set_last_failure,
    clear_last_failure,
    append_failure_history,
    build_failure_envelope,
    record_step_usage,
    default_review_state,
    default_task_execution_binding,
    default_usage_summary,
    make_job_id,
    infer_seed_identity,
    create_job,
    load_job,
    save_job,
    iter_group_jobs,
    find_matching_active_job,
    find_matching_completed_job,
    migrate_job_state,
    ensure_backward_compatible_state,
    reconcile_job_state,
    reapply_routing,
    recover_exhausted_planning_job,
    _extract_document_status,
    _normalize_document_status,
    _update_document_status,
    check_preflight_artifact_status,
    task_queue_is_initialized,
    task_queue_current_item,
    next_pending_task_queue_item,
    task_queue_has_remaining_work,
    _make_task_queue_item_id,
    _extract_document_metadata_value,
    extract_task_graph_nodes,
    _md5_file,
    get_next_step_skipping_refine_replan,
    get_next_step,
    advance_step,
    approve_step,
    force_approve_step,
    prepare_state_for_retry,
    enforce_retry_limit_before_run,
    looks_like_transient_error,
    classify_pre_run_failure,
    task_execution_binding_identity,
    task_execution_binding_current_item,
    apply_task_execution_binding,
    initialize_task_generation_state,
    ensure_planning_task_queue_integrity,
)
from agent_runner_v2.exceptions import PreflightBlockedError


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_schema_version(self):
        assert CURRENT_SCHEMA_VERSION == 6

    def test_non_terminal_statuses(self):
        assert "IN_PROGRESS" in NON_TERMINAL_JOB_STATUSES
        assert "COMPLETED" not in NON_TERMINAL_JOB_STATUSES
        assert "FAILED" not in NON_TERMINAL_JOB_STATUSES

    def test_review_decisions(self):
        assert REVIEW_DECISIONS == {"PENDING", "APPROVED", "REJECTED"}

    def test_human_decisions(self):
        assert "NOT_REQUIRED" in HUMAN_DECISIONS

    def test_failure_sources(self):
        assert "runner" in FAILURE_SOURCES
        assert "adapter" in FAILURE_SOURCES
        assert "model" in FAILURE_SOURCES
        assert "validator" in FAILURE_SOURCES


# ---------------------------------------------------------------------------
# now_iso
# ---------------------------------------------------------------------------

class TestNowIso:
    def test_returns_iso_string(self):
        result = now_iso()
        assert isinstance(result, str)
        # Should parse as ISO
        dt.datetime.fromisoformat(result)

    def test_has_seconds_precision(self):
        result = now_iso()
        # Should not have microseconds (timespec="seconds")
        parsed = dt.datetime.fromisoformat(result)
        assert parsed.microsecond == 0


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

class TestJobStatus:
    def test_get_from_job_status(self):
        state = {"job_status": "IN_PROGRESS"}
        assert get_job_status(state) == "IN_PROGRESS"

    def test_get_from_status_fallback(self):
        state = {"status": "COMPLETED"}
        assert get_job_status(state) == "COMPLETED"

    def test_job_status_takes_priority(self):
        state = {"job_status": "FAILED", "status": "IN_PROGRESS"}
        assert get_job_status(state) == "FAILED"

    def test_empty_fallback(self):
        state = {}
        assert get_job_status(state) == ""

    def test_set_both_keys(self):
        state = {}
        set_job_status(state, "WAITING_FOR_HUMAN_APPROVAL")
        assert state["job_status"] == "WAITING_FOR_HUMAN_APPROVAL"
        assert state["status"] == "WAITING_FOR_HUMAN_APPROVAL"


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

class TestPathHelpers:
    def test_ensure_dir_creates_nested(self, tmp_path):
        target = tmp_path / "a" / "b" / "c"
        ensure_dir(target)
        assert target.is_dir()

    def test_ensure_dir_idempotent(self, tmp_path):
        target = tmp_path / "existing"
        target.mkdir()
        ensure_dir(target)
        assert target.is_dir()

    def test_resolve_repo_path_relative(self, tmp_workspace, fake_workflow, set_context):
        path = resolve_repo_path("sub/file.txt")
        assert path.is_absolute()
        assert path == tmp_workspace.workspace_root / "sub" / "file.txt"

    def test_resolve_repo_path_absolute(self):
        path = resolve_repo_path("/absolute/path.txt")
        assert path == Path("/absolute/path.txt")

    def test_normalize_repo_relative(self, tmp_workspace, fake_workflow, set_context):
        result = normalize_repo_relative_path("some/nested/file.md")
        # Should be a relative path string
        assert Path(result) == Path("some/nested/file.md")

    def test_group_dir(self, tmp_workspace, fake_workflow, set_context):
        gd = group_dir("my_group")
        assert gd == tmp_workspace.runner_home / "jobs" / "my_group"

    def test_job_dir(self, tmp_workspace, fake_workflow, set_context):
        jd = job_dir("my_group", "JOB-001")
        assert jd == tmp_workspace.runner_home / "jobs" / "my_group" / "JOB-001"

    def test_job_state_path(self, tmp_workspace, fake_workflow, set_context):
        jsp = job_state_path("my_group", "JOB-001")
        assert jsp.name == "job.json"
        assert jsp.parent == job_dir("my_group", "JOB-001")


class TestGetStepIndex:
    def test_first_step_is_1(self):
        cfg = {"steps": ["a", "b", "c"]}
        assert get_step_index(cfg, "a") == 1

    def test_second_step_is_2(self):
        cfg = {"steps": ["a", "b", "c"]}
        assert get_step_index(cfg, "b") == 2

    def test_raises_on_unknown_step(self):
        cfg = {"steps": ["a", "b"]}
        with pytest.raises(ValueError):
            get_step_index(cfg, "z")


class TestMakeStepDir:
    def test_basic_step_dir(self, tmp_workspace, fake_workflow, set_context):
        state = {"template_group": "delivery_planning_v1", "job_id": "DEL-001"}
        cfg = {"steps": ["task", "review_task"]}
        path = make_step_dir(cfg, state, "task")
        assert path.name == "01_task"

    def test_loop_iteration_suffix(self, tmp_workspace, fake_workflow, set_context):
        state = {
            "template_group": "delivery_planning_v1",
            "job_id": "DEL-001",
            "loop_context": {
                "active": True,
                "refine_step": "refine_task",
                "loop_step": "review_task",
                "loop_iteration": 3,
            },
        }
        cfg = {"steps": ["task", "review_task", "refine_task"]}
        path = make_step_dir(cfg, state, "refine_task")
        assert path.name == "03_refine_task_iter3"


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

class TestJsonHelpers:
    def test_save_and_load(self, tmp_path):
        data = {"key": "value", "num": 42}
        path = tmp_path / "test.json"
        save_json(path, data)
        assert path.exists()
        loaded = load_json(path)
        assert loaded == data

    def test_save_creates_parent_dirs(self, tmp_path):
        path = tmp_path / "deep" / "nested" / "data.json"
        save_json(path, {"x": 1})
        assert path.exists()

    def test_save_text(self, tmp_path):
        path = tmp_path / "file.txt"
        save_text(path, "hello world")
        assert path.read_text() == "hello world"

    def test_save_json_atomic_roundtrip(self, tmp_path):
        path = tmp_path / "atomic.json"
        data = {"atomic": True, "count": 99}
        save_json_atomic(path, data)
        loaded = load_json(path)
        assert loaded == data

    def test_save_json_atomic_is_atomic(self, tmp_path):
        """After save_json_atomic, no temp file should remain."""
        path = tmp_path / "atomic.json"
        save_json_atomic(path, {"ok": True})
        temp_files = list(tmp_path.glob(".atomic.json.*"))
        assert len(temp_files) == 0


# ---------------------------------------------------------------------------
# Failure tracking
# ---------------------------------------------------------------------------

class TestFailureTracking:
    def test_set_last_failure(self):
        state = {}
        set_last_failure(
            state=state,
            failure_class="HUMAN_RETRY_REQUIRED",
            failure_code="MISSING_ARTIFACT",
            failure_reason="Artifact not found",
            failure_source="runner",
            step="review_task",
        )
        assert state["last_failure_class"] == "HUMAN_RETRY_REQUIRED"
        assert state["last_failure_code"] == "MISSING_ARTIFACT"
        assert state["pending_intervention_for"] == "review_task"

    def test_set_last_failure_auto_retryable_no_intervention(self):
        state = {}
        set_last_failure(
            state=state,
            failure_class="AUTO_RETRYABLE",
            failure_code="TRANSIENT",
            failure_reason="timeout",
            failure_source="adapter",
            step="task",
        )
        assert state["pending_intervention_for"] is None

    def test_clear_last_failure(self):
        state = {
            "last_failure_class": "FATAL",
            "last_failure_code": "ERR",
            "last_failure_reason": "reason",
            "last_failure_source": "runner",
            "pending_intervention_for": "task",
        }
        clear_last_failure(state)
        assert state["last_failure_class"] is None
        assert state["last_failure_code"] is None
        assert state["last_failure_reason"] is None
        assert state["last_failure_source"] is None
        assert state["pending_intervention_for"] is None

    def test_append_failure_history(self):
        state = {}
        append_failure_history(
            state=state, step="task", failure_class="FATAL",
            failure_code="ERR", failure_source="model",
        )
        history = state["failure_history"]
        assert len(history) == 1
        assert history[0]["step"] == "task"
        assert "timestamp" in history[0]

    def test_append_multiple_entries(self):
        state = {"failure_history": []}
        append_failure_history(
            state=state, step="a", failure_class="FATAL", failure_code="A", failure_source="runner",
        )
        append_failure_history(
            state=state, step="b", failure_class="AUTO_RETRYABLE", failure_code="B", failure_source="model",
        )
        assert len(state["failure_history"]) == 2

    def test_build_failure_envelope(self):
        env = build_failure_envelope(
            failure_class="FATAL", failure_code="ERR", failure_reason="boom", failure_source="adapter",
        )
        assert env["failure_class"] == "FATAL"
        assert env["failure_code"] == "ERR"


# ---------------------------------------------------------------------------
# Usage tracking
# ---------------------------------------------------------------------------

class TestUsageTracking:
    def test_record_step_usage(self):
        state = {"step_usage": {}}
        record_step_usage(state, "task", {
            "usage_source": "cli_reported",
            "input_tokens": 100,
            "output_tokens": 200,
        })
        assert state["step_usage"]["task"]["input_tokens"] == 100
        summary = state["usage_summary"]
        assert summary["steps_with_usage"] == 1
        assert summary["input_tokens"] == 100
        assert summary["output_tokens"] == 200

    def test_record_usage_without_source(self):
        state = {"step_usage": {}}
        record_step_usage(state, "task", {"no_source": True})
        assert state["usage_summary"]["steps_without_usage"] == 1


# ---------------------------------------------------------------------------
# Default constructors
# ---------------------------------------------------------------------------

class TestDefaults:
    def test_default_review_state(self):
        rs = default_review_state()
        assert rs["review_decision"] == "PENDING"
        assert rs["review_iteration"] == 0

    def test_default_task_execution_binding(self):
        b = default_task_execution_binding()
        assert b["task_node_id"] is None
        assert b["task_graph_id"] is None

    def test_default_usage_summary(self):
        s = default_usage_summary()
        assert s["steps_with_usage"] == 0
        assert s["input_tokens"] is None


# ---------------------------------------------------------------------------
# Job ID generation
# ---------------------------------------------------------------------------

class TestMakeJobId:
    def test_first_job_is_001(self, tmp_workspace, fake_workflow, set_context):
        cfg = {"job_prefix": "DEL"}
        job_id = make_job_id("delivery_planning_v1", cfg, {})
        assert job_id.endswith("-001")

    def test_second_job_is_002(self, tmp_workspace, fake_workflow, set_context):
        cfg = {"job_prefix": "DEL"}
        first = make_job_id("delivery_planning_v1", cfg, {})
        # Create the directory for the first job so it's counted
        gd = group_dir("delivery_planning_v1")
        first_dir = gd / first
        first_dir.mkdir(parents=True, exist_ok=True)
        second = make_job_id("delivery_planning_v1", cfg, {})
        assert second.endswith("-002")

    def test_task_execution_prefix(self, tmp_workspace, fake_workflow, set_context):
        cfg = {"job_prefix": "TASK"}
        job_id = make_job_id("task_execution_v1", cfg, {})
        assert job_id.startswith("TASK-")


class TestInferSeedIdentity:
    def test_delivery_planning(self):
        t, p = infer_seed_identity("delivery_planning_v1", {"INIT_FILE": "docs/init-01.md"})
        assert t == "INIT_FILE"

    def test_task_execution(self):
        t, p = infer_seed_identity("task_execution_v1", {"TASK_FILE": "docs/task-01.md"})
        assert t == "TASK_FILE"

    def test_unknown_group(self):
        t, p = infer_seed_identity("unknown_v1", {})
        assert t is None
        assert p is None


# ---------------------------------------------------------------------------
# Job CRUD
# ---------------------------------------------------------------------------

class TestCreateJob:
    def test_creates_job_on_disk(self, tmp_workspace, fake_workflow, set_context):
        cfg = {"job_prefix": "DEL", "job_init_step": "project_analysis", "steps": ["project_analysis"]}
        state = create_job("delivery_planning_v1", cfg, {})
        assert state["job_id"].startswith("DEL-")
        assert state["runner_version"] == "v2"
        assert state["state_schema_version"] == 6
        # Verify file was written
        path = job_state_path("delivery_planning_v1", state["job_id"])
        assert path.exists()
        disk_state = load_json(path)
        assert disk_state["job_id"] == state["job_id"]

    def test_raises_on_unknown_artifact_key(self, tmp_workspace, fake_workflow, set_context):
        cfg = {"job_prefix": "DEL", "job_init_step": "x", "steps": ["x"]}
        with pytest.raises(ValueError, match="Unknown artifact key"):
            create_job("delivery_planning_v1", cfg, {"UNKNOWN_KEY": "foo"})

    def test_seed_artifacts_populated(self, tmp_workspace, fake_workflow, set_context):
        cfg = {"job_prefix": "DEL", "job_init_step": "project_analysis", "steps": ["project_analysis"]}
        state = create_job("delivery_planning_v1", cfg, {"INIT_FILE": "docs/init.md"})
        assert state["artifacts"]["INIT_FILE"] == "docs/init.md"
        assert state["seed_artifact_type"] == "INIT_FILE"


class TestLoadJob:
    def test_load_existing_job(self, tmp_workspace, fake_workflow, set_context, real_job_on_disk):
        state = load_job(real_job_on_disk.group_name, real_job_on_disk.job_id)
        assert state["job_id"] == real_job_on_disk.job_id

    def test_load_missing_job_raises(self, tmp_workspace, fake_workflow, set_context):
        with pytest.raises(FileNotFoundError, match="Job state not found"):
            load_job("delivery_planning_v1", "NONEXISTENT-001")

    def test_load_wrong_group_raises(self, tmp_workspace, fake_workflow, set_context, real_job_on_disk):
        # Write a job with template_group="delivery_planning_v1" under the
        # delivery_planning_v1 group, then try to load it as task_execution_v1.
        from agent_runner_v2.job_state import save_json as _save
        import copy
        orig = load_job(real_job_on_disk.group_name, real_job_on_disk.job_id)
        bad = copy.deepcopy(orig)
        bad["job_id"] = "DEL-WRONG-001"
        bad["template_group"] = "delivery_planning_v1"
        path = tmp_workspace.jobs_root / "task_execution_v1" / "DEL-WRONG-001" / "job.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        _save(path, bad)
        with pytest.raises(ValueError, match="belongs to template group"):
            load_job("task_execution_v1", "DEL-WRONG-001")


class TestSaveJob:
    def test_save_updates_timestamp(self, tmp_workspace, fake_workflow, set_context, real_job_on_disk):
        state = load_job(real_job_on_disk.group_name, real_job_on_disk.job_id)
        old_ts = state["updated_at"]
        import time
        time.sleep(0.01)
        save_job(real_job_on_disk.group_name, real_job_on_disk.job_id, state)
        assert state["updated_at"] != old_ts

    def test_save_syncs_status_and_job_status(self, tmp_workspace, fake_workflow, set_context, real_job_on_disk):
        state = load_job(real_job_on_disk.group_name, real_job_on_disk.job_id)
        state["job_status"] = "COMPLETED"
        state.pop("status", None)
        save_job(real_job_on_disk.group_name, real_job_on_disk.job_id, state)
        assert state["status"] == "COMPLETED"


# ---------------------------------------------------------------------------
# Job discovery
# ---------------------------------------------------------------------------

class TestIterGroupJobs:
    def test_empty_group(self, tmp_workspace, fake_workflow, set_context):
        result = iter_group_jobs("delivery_planning_v1")
        assert result == []

    def test_nonexistent_group(self, tmp_workspace, fake_workflow, set_context):
        result = iter_group_jobs("nonexistent_group")
        assert result == []

    def test_returns_single_job(self, tmp_workspace, fake_workflow, set_context, real_job_on_disk):
        result = iter_group_jobs(real_job_on_disk.group_name)
        assert len(result) == 1
        assert result[0]["job_id"] == real_job_on_disk.job_id

    def test_returns_sorted(self, tmp_workspace, fake_workflow, set_context):
        cfg = {"job_prefix": "DEL", "job_init_step": "x", "steps": ["x"]}
        j2 = create_job("delivery_planning_v1", cfg, {})
        # The second call should create 002
        j3 = create_job("delivery_planning_v1", cfg, {})
        results = iter_group_jobs("delivery_planning_v1")
        ids = [r["job_id"] for r in results]
        assert ids == sorted(ids)


class TestFindMatchingActiveJob:
    def test_finds_active_job(self, tmp_workspace, fake_workflow, set_context):
        cfg = {"job_prefix": "DEL", "job_init_step": "x", "steps": ["x"]}
        state = create_job("delivery_planning_v1", cfg, {"INIT_FILE": "docs/init.md"})
        found = find_matching_active_job(
            group_name="delivery_planning_v1",
            seed_artifact_type="INIT_FILE",
            seed_artifact_path=state["seed_artifact_path"],
        )
        assert found == state["job_id"]

    def test_does_not_find_completed_job(self, tmp_workspace, fake_workflow, set_context):
        cfg = {"job_prefix": "DEL", "job_init_step": "x", "steps": ["x"]}
        state = create_job("delivery_planning_v1", cfg, {"INIT_FILE": "docs/init.md"})
        set_job_status(state, "COMPLETED")
        save_job("delivery_planning_v1", state["job_id"], state)
        found = find_matching_active_job(
            group_name="delivery_planning_v1",
            seed_artifact_type="INIT_FILE",
            seed_artifact_path=state["seed_artifact_path"],
        )
        assert found is None

    def test_raises_on_multiple_matches(self, tmp_workspace, fake_workflow, set_context):
        cfg = {"job_prefix": "DEL", "job_init_step": "x", "steps": ["x"]}
        s1 = create_job("delivery_planning_v1", cfg, {"INIT_FILE": "docs/init.md"})
        s2 = create_job("delivery_planning_v1", cfg, {"INIT_FILE": "docs/init.md"})
        with pytest.raises(ValueError, match="Multiple active jobs"):
            find_matching_active_job(
                group_name="delivery_planning_v1",
                seed_artifact_type="INIT_FILE",
                seed_artifact_path=s1["seed_artifact_path"],
            )


class TestFindMatchingCompletedJob:
    def test_finds_completed_job(self, tmp_workspace, fake_workflow, set_context):
        cfg = {"job_prefix": "DEL", "job_init_step": "x", "steps": ["x"]}
        state = create_job("delivery_planning_v1", cfg, {"INIT_FILE": "docs/init.md"})
        set_job_status(state, "COMPLETED")
        save_job("delivery_planning_v1", state["job_id"], state)
        found = find_matching_completed_job(
            group_name="delivery_planning_v1",
            seed_artifact_type="INIT_FILE",
            seed_artifact_path=state["seed_artifact_path"],
        )
        assert found == state["job_id"]

    def test_does_not_find_active_job(self, tmp_workspace, fake_workflow, set_context):
        cfg = {"job_prefix": "DEL", "job_init_step": "x", "steps": ["x"]}
        create_job("delivery_planning_v1", cfg, {"INIT_FILE": "docs/init.md"})
        found = find_matching_completed_job(
            group_name="delivery_planning_v1",
            seed_artifact_type="INIT_FILE",
            seed_artifact_path="docs/init.md",
        )
        assert found is None


# ---------------------------------------------------------------------------
# State migration
# ---------------------------------------------------------------------------

class TestMigrateJobState:
    def test_v1_to_v6(self):
        state = {"state_schema_version": 1}
        result = migrate_job_state(state)
        assert result["state_schema_version"] == 6
        assert result["runner_version"] == "v2"
        assert "loop_context" in result
        assert "review_state" in result
        assert "task_execution_binding" in result

    def test_v5_to_v6(self):
        state = {"state_schema_version": 5}
        result = migrate_job_state(state)
        assert result["state_schema_version"] == 6
        assert result["runner_version"] == "v2"

    def test_already_v6_unchanged(self):
        state = {"state_schema_version": 6, "runner_version": "v2"}
        result = migrate_job_state(state)
        assert result["state_schema_version"] == 6

    def test_fixes_task_id_aliasing(self):
        state = {
            "state_schema_version": 6,
            "task_execution_binding": {
                "task_id": "TASK-001",
                "task_node_snapshot": {"task_id": "TASK-001"},
            },
        }
        result = migrate_job_state(state)
        assert result["task_execution_binding"]["task_node_id"] == "TASK-001"
        assert result["task_execution_binding"]["task_node_snapshot"]["task_node_id"] == "TASK-001"


class TestEnsureBackwardCompatible:
    def test_minimal_state_gets_defaults(self, tmp_workspace, fake_workflow, set_context):
        state = {"template_group": "delivery_planning_v1"}
        result = ensure_backward_compatible_state(state)
        assert result["runner_version"] == "v2"
        assert result["state_schema_version"] == 1
        assert "review_state" in result
        assert "loop_context" in result
        assert "replan_context" in result


# ---------------------------------------------------------------------------
# Reconcile + routing repair
# ---------------------------------------------------------------------------

class TestReconcileJobState:
    def test_completes_terminal_delivery_task_step(self):
        state = {
            "template_group": "delivery_planning_v1",
            "current_step": "task",
            "pending_human_approval_for": None,
            "job_status": "IN_PROGRESS",
        }
        cfg = {"steps": [], "step_configs": {}}
        result = reconcile_job_state(state, cfg)
        assert get_job_status(result) == "COMPLETED"
        assert result["current_step"] is None

    def test_does_not_reconcile_completed(self):
        state = {"template_group": "delivery_planning_v1", "current_step": "task", "job_status": "COMPLETED"}
        cfg = {"steps": [], "step_configs": {}}
        result = reconcile_job_state(state, cfg)
        assert get_job_status(result) == "COMPLETED"

    def test_does_not_reconcile_failed(self):
        state = {
            "template_group": "delivery_planning_v1",
            "current_step": "generate_sop",
            "job_status": "FAILED",
            "status": "FAILED",
            "pending_human_approval_for": None,
        }
        cfg = {"steps": [], "step_configs": {}}
        result = reconcile_job_state(state, cfg)
        assert get_job_status(result) == "FAILED"


class TestReapplyRouting:
    def test_returns_state_when_no_review_file(self):
        state = {
            "current_step": "review_task",
            "artifacts": {},
            "last_failure_code": "REFINEMENT_EXHAUSTED",
            "replan_context": {"replan_attempt": 0},
        }
        cfg = {
            "step_configs": {
                "review_task": {
                    "on_reject_refine": {"exhausted_failure_code": "REFINEMENT_EXHAUSTED"},
                    "on_exhaust_replan": {"max_replans": 2, "step": "replan_task"},
                },
            },
        }
        result = reapply_routing(state, cfg)
        assert result is state

    def test_user_reapply_replan_when_exhausted(self, tmp_workspace, fake_workflow, set_context):
        state = {
            "current_step": "review_task",
            "artifacts": {"REVIEW_FILE": "docs/review.md"},
            "last_failure_code": "REFINEMENT_EXHAUSTED",
            "last_failure_class": "HUMAN_RETRY_REQUIRED",
            "last_failure_reason": "test",
            "last_failure_source": "model",
            "replan_context": {"replan_attempt": 0},
        }
        cfg = {
            "step_configs": {
                "review_task": {
                    "on_reject_refine": {
                        "exhausted_failure_code": "REFINEMENT_EXHAUSTED",
                        "step": "refine_task",
                        "artifact": "IMPL_FILE",
                    },
                    "on_exhaust_replan": {
                        "max_replans": 2,
                        "step": "replan_task",
                        "artifact": "PLAN_FILE",
                    },
                },
            },
        }
        result = reapply_routing(state, cfg)
        assert result["replan_context"]["active"] is True


class TestRecoverExhaustedPlanningJob:
    def test_noop_when_not_failed(self):
        state = {"job_status": "IN_PROGRESS", "current_step": "task"}
        cfg = {"step_configs": {"task": {}}}
        result = recover_exhausted_planning_job(state, cfg)
        assert result is state

    def test_noop_when_no_exhausted_failure_in_history(self):
        state = {
            "job_status": "FAILED",
            "current_step": "task",
            "failure_history": [{"step": "other", "failure_code": "X"}],
            "replan_context": {"replan_attempt": 0},
            "artifacts": {"REVIEW_FILE": "docs/review.md"},
        }
        cfg = {
            "step_configs": {
                "task": {
                    "on_reject_refine": {"exhausted_failure_code": "X", "step": "refine"},
                    "on_exhaust_replan": {"max_replans": 2, "step": "replan"},
                },
            },
        }
        result = recover_exhausted_planning_job(state, cfg)
        assert result is state


# ---------------------------------------------------------------------------
# Preflight status check
# ---------------------------------------------------------------------------

class TestExtractDocumentStatus:
    def test_dash_status(self):
        content = "- Status: draft"
        assert _extract_document_status(content) == "draft"

    def test_bold_status(self):
        content = "- **Status**: approved"
        assert _extract_document_status(content) == "approved"

    def test_plain_status(self):
        content = "Status: changes_requested"
        assert _extract_document_status(content) == "changes_requested"

    def test_no_status_returns_none(self):
        assert _extract_document_status("# Title\nSome text") is None


class TestNormalizeDocumentStatus:
    def test_spaces_to_underscores(self):
        assert _normalize_document_status("changes requested") == "changes_requested"

    def test_lowercases(self):
        assert _normalize_document_status("APPROVED") == "approved"

    def test_dashes_to_underscores(self):
        assert _normalize_document_status("in-progress") == "in_progress"


class TestUpdateDocumentStatus:
    def test_updates_dash_status(self, tmp_workspace, fake_workflow, set_context):
        p = tmp_workspace.workspace_root / "doc.md"
        p.write_text("- Status: draft\n\nContent")
        _update_document_status(file_path="doc.md", new_status="approved")
        assert "approved" in p.read_text()

    def test_noop_when_file_missing(self, tmp_workspace, fake_workflow, set_context):
        _update_document_status(file_path="nonexistent.md", new_status="approved")
        # Should not raise


class TestCheckPreflightArtifactStatus:
    def test_no_check_in_config(self):
        state = {"artifacts": {}}
        check_preflight_artifact_status(step_cfg={}, state=state)

    def test_artifact_missing_no_raise(self, tmp_workspace, fake_workflow, set_context):
        state = {"artifacts": {"INIT_FILE": "docs/missing.md"}}
        check_preflight_artifact_status(
            step_cfg={"preflight_status_check": {"artifact": "INIT_FILE", "required_status": "approved"}},
            state=state,
        )

    def test_passes_when_matches(self, tmp_workspace, fake_workflow, set_context):
        p = tmp_workspace.workspace_root / "init.md"
        p.write_text("- Status: approved")
        state = {"artifacts": {"INIT_FILE": "init.md"}}
        check_preflight_artifact_status(
            step_cfg={"preflight_status_check": {"artifact": "INIT_FILE", "required_status": "approved"}},
            state=state,
        )

    def test_raises_when_mismatch(self, tmp_workspace, fake_workflow, set_context):
        p = tmp_workspace.workspace_root / "init.md"
        p.write_text("- Status: draft")
        state = {"artifacts": {"INIT_FILE": "init.md"}}
        with pytest.raises(PreflightBlockedError, match="Preflight status check failed"):
            check_preflight_artifact_status(
                step_cfg={"preflight_status_check": {"artifact": "INIT_FILE", "required_status": "approved"}},
                state=state,
            )


# ---------------------------------------------------------------------------
# Task queue helpers
# ---------------------------------------------------------------------------

class TestTaskQueueHelpers:
    def test_is_initialized_false(self):
        assert task_queue_is_initialized({}) is False

    def test_is_initialized_true(self):
        state = {"task_generation_state": {"ordered_tasks": [{"id": 1}]}}
        assert task_queue_is_initialized(state) is True

    def test_current_item_found(self):
        state = {
            "task_generation_state": {
                "current_queue_item_id": "tgq_0002",
                "ordered_tasks": [
                    {"queue_item_id": "tgq_0001", "status": "APPROVED"},
                    {"queue_item_id": "tgq_0002", "status": "PENDING"},
                ],
            },
        }
        item = task_queue_current_item(state)
        assert item["queue_item_id"] == "tgq_0002"

    def test_current_item_none(self):
        state = {"task_generation_state": {"current_queue_item_id": "tgq_999", "ordered_tasks": []}}
        assert task_queue_current_item(state) is None

    def test_next_pending(self):
        state = {
            "task_generation_state": {
                "ordered_tasks": [
                    {"status": "APPROVED"},
                    {"status": "PENDING", "title": "next"},
                ],
            },
        }
        item = next_pending_task_queue_item(state)
        assert item["title"] == "next"

    def test_has_remaining_work(self):
        state = {"task_generation_state": {"ordered_tasks": [{"status": "PENDING"}]}}
        assert task_queue_has_remaining_work(state) is True

    def test_no_remaining_work(self):
        state = {"task_generation_state": {"ordered_tasks": [{"status": "APPROVED"}]}}
        assert task_queue_has_remaining_work(state) is False

    def test_make_task_queue_item_id(self):
        assert _make_task_queue_item_id(1) == "tgq_0001"
        assert _make_task_queue_item_id(42) == "tgq_0042"


class TestExtractTaskGraphNodes:
    def test_parses_valid_task_graph(self, tmp_workspace, fake_workflow, set_context):
        content = (
            "---\n- **Task Graph ID**: TG-001\n- **Plan ID**: PL-001\n---\n"
            "### `TASK-20260601-1` — First task\n\nBody\n\n"
            "### `TASK-20260601-2` — Second task\n\nBody\n"
        )
        p = tmp_workspace.workspace_root / "task_graph.md"
        p.write_text(content)
        nodes = extract_task_graph_nodes("task_graph.md")
        assert len(nodes) == 2
        assert nodes[0]["task_node_id"] == "TASK-20260601-1"
        assert nodes[1]["title"] == "Second task"
        assert nodes[0]["sequence"] == 1

    def test_raises_on_missing_file(self, tmp_workspace, fake_workflow, set_context):
        with pytest.raises(ValueError, match="does not exist"):
            extract_task_graph_nodes("missing.md")

    def test_raises_on_no_tasks(self, tmp_workspace, fake_workflow, set_context):
        p = tmp_workspace.workspace_root / "empty_graph.md"
        p.write_text("No tasks here")
        with pytest.raises(ValueError, match="could not be parsed"):
            extract_task_graph_nodes("empty_graph.md")

    def test_raises_on_duplicate_id(self, tmp_workspace, fake_workflow, set_context):
        content = (
            "### `TASK-20260601-1` — First\n"
            "### `TASK-20260601-1` — Duplicate\n"
        )
        p = tmp_workspace.workspace_root / "dup.md"
        p.write_text(content)
        with pytest.raises(ValueError, match="duplicate"):
            extract_task_graph_nodes("dup.md")


class TestMd5File:
    def test_md5_consistent(self, tmp_path):
        p = tmp_path / "test.bin"
        p.write_bytes(b"hello world")
        h1 = _md5_file(p)
        h2 = _md5_file(p)
        assert h1 == h2
        assert len(h1) == 32  # MD5 hex length


# ---------------------------------------------------------------------------
# Step navigation
# ---------------------------------------------------------------------------

class TestStepNavigation:
    def test_get_next_step(self):
        cfg = {"steps": ["a", "b", "c"]}
        state = {"completed_steps": ["a"]}
        assert get_next_step(cfg, state) == "b"

    def test_get_next_step_none_when_all_done(self):
        cfg = {"steps": ["a", "b"]}
        state = {"completed_steps": ["a", "b"]}
        assert get_next_step(cfg, state) is None

    def test_get_next_step_skipping_refine_replan(self):
        cfg = {
            "steps": ["a", "refine", "b", "replan"],
            "step_configs": {
                "a": {"on_reject_refine": {"step": "refine"}},
                "b": {"on_exhaust_replan": {"step": "replan"}},
            },
        }
        state = {"completed_steps": []}
        assert get_next_step_skipping_refine_replan(cfg, state) == "a"

    def test_skip_refine_when_completed(self):
        cfg = {
            "steps": ["a", "refine", "b"],
            "step_configs": {"a": {"on_reject_refine": {"step": "refine"}}},
        }
        state = {"completed_steps": ["a"]}
        result = get_next_step_skipping_refine_replan(cfg, state)
        assert result == "b"


# ---------------------------------------------------------------------------
# Step advancement state machine
# ---------------------------------------------------------------------------

class TestAdvanceStep:
    def test_non_approved_returns_waiting(self):
        state = {}
        cfg = {"steps": ["a"]}
        step_cfg = {}
        new_state, exit_code = advance_step(
            group_cfg=cfg, state=state, step="a", step_cfg=step_cfg,
            result_status="REJECTED", coder_used="qwen",
        )
        assert exit_code == 1

    def test_approved_normal_step_advances(self):
        state = {"completed_steps": [], "artifacts": {}, "reject_counts": {}}
        cfg = {"steps": ["a", "b"]}
        step_cfg = {}
        new_state, exit_code = advance_step(
            group_cfg=cfg, state=state, step="a", step_cfg=step_cfg,
            result_status="APPROVED", coder_used="qwen",
        )
        assert exit_code == 0
        assert "a" in new_state["completed_steps"]
        assert new_state["current_step"] == "b"

    def test_approved_last_step_completes(self):
        state = {"completed_steps": [], "artifacts": {}, "reject_counts": {}}
        cfg = {"steps": ["a"]}
        step_cfg = {}
        new_state, exit_code = advance_step(
            group_cfg=cfg, state=state, step="a", step_cfg=step_cfg,
            result_status="APPROVED", coder_used="qwen",
        )
        assert exit_code == 0
        assert get_job_status(new_state) == "COMPLETED"
        assert new_state["current_step"] is None

    def test_review_step_sets_waiting_approval(self, tmp_workspace, fake_workflow, set_context):
        state = {"completed_steps": [], "artifacts": {}, "reject_counts": {}}
        cfg = {"steps": ["review_sop"]}
        step_cfg = {"requires_human_approval_after": True}
        new_state, exit_code = advance_step(
            group_cfg=cfg, state=state, step="review_sop", step_cfg=step_cfg,
            result_status="APPROVED", coder_used="qwen",
        )
        assert exit_code == 0
        assert get_job_status(new_state) == "WAITING_FOR_HUMAN_APPROVAL"
        assert new_state["pending_human_approval_for"] == "review_sop"

    def test_refine_success_with_missing_artifact(self, tmp_workspace, fake_workflow, set_context):
        state = {"completed_steps": [], "artifacts": {}, "reject_counts": {}}
        cfg = {"steps": ["refine", "review"]}
        step_cfg = {"loop_returns_to": "review", "target_artifact": "IMPL_FILE"}
        new_state, exit_code = advance_step(
            group_cfg=cfg, state=state, step="refine", step_cfg=step_cfg,
            result_status="APPROVED", coder_used="qwen",
        )
        assert exit_code == 1
        assert get_job_status(new_state) == "WAITING_FOR_HUMAN_INTERVENTION"


# ---------------------------------------------------------------------------
# Human approval
# ---------------------------------------------------------------------------

class TestApproveStep:
    def test_raises_when_not_pending(self, tmp_workspace, fake_workflow, set_context):
        state = {"pending_human_approval_for": "other_step", "model_approved_steps": ["step_x"]}
        cfg = {"step_configs": {"step_x": {}}}
        with pytest.raises(ValueError, match="not pending"):
            approve_step(group_name="delivery_planning_v1", group_cfg=cfg, state=state, step="step_x")

    def test_raises_when_no_model_approval(self, tmp_workspace, fake_workflow, set_context):
        state = {"pending_human_approval_for": "step_x", "model_approved_steps": []}
        cfg = {"step_configs": {"step_x": {}}}
        with pytest.raises(ValueError, match="does not have recorded model approval"):
            approve_step(group_name="delivery_planning_v1", group_cfg=cfg, state=state, step="step_x")

    def test_raises_when_review_not_approved(self, tmp_workspace, fake_workflow, set_context):
        state = {
            "pending_human_approval_for": "step_x",
            "model_approved_steps": ["step_x"],
            "review_state": {"review_decision": "REJECTED"},
        }
        cfg = {"step_configs": {"step_x": {}}}
        with pytest.raises(ValueError, match="cannot be human-approved before review_decision"):
            approve_step(group_name="delivery_planning_v1", group_cfg=cfg, state=state, step="step_x")

    def test_successful_approval(self, tmp_workspace, fake_workflow, set_context):
        state = {
            "pending_human_approval_for": "review_sop",
            "model_approved_steps": ["review_sop"],
            "review_state": default_review_state(),
            "completed_steps": [],
            "human_approvals": {},
            "artifacts": {},
            "job_id": "DEL-001",
            "template_group": "delivery_planning_v1",
            "job_status": "WAITING_FOR_HUMAN_APPROVAL",
            "status": "WAITING_FOR_HUMAN_APPROVAL",
            "current_step": "review_sop",
        }
        state["review_state"]["review_decision"] = "APPROVED"
        cfg = {
            "steps": ["review_sop", "generate_plan", "refine_sop", "replan_task"],
            "step_configs": {
                "review_sop": {
                    "requires_human_approval_after": True,
                },
                "refine_sop": {},
                "replan_task": {},
            },
        }
        result = approve_step(
            group_name="delivery_planning_v1", group_cfg=cfg, state=state, step="review_sop",
        )
        assert result["human_approvals"]["review_sop"]["status"] == "APPROVED"
        # After approval of a non-terminal step, should advance to next step
        assert result["pending_human_approval_for"] is None


class TestForceApproveStep:
    def test_raises_on_undefined_step(self, tmp_workspace, fake_workflow, set_context):
        state = {"model_approved_steps": [], "human_approvals": {}, "completed_steps": []}
        cfg = {"step_configs": {}}
        with pytest.raises(ValueError, match="not defined"):
            force_approve_step(group_name="delivery_planning_v1", group_cfg=cfg, state=state, step="bogus")

    def test_successful_force_approval(self, tmp_workspace, fake_workflow, set_context):
        state = {
            "model_approved_steps": [],
            "human_approvals": {},
            "completed_steps": [],
            "review_state": default_review_state(),
            "job_id": "DEL-001",
            "template_group": "delivery_planning_v1",
            "job_status": "IN_PROGRESS",
            "status": "IN_PROGRESS",
            "current_step": "review_sop",
            "pending_human_approval_for": None,
            "artifacts": {},
        }
        cfg = {
            "steps": ["review_sop", "generate_plan", "refine_sop"],
            "step_configs": {
                "review_sop": {"requires_human_approval_after": True},
                "generate_plan": {},
                "refine_sop": {},
            },
        }
        result = force_approve_step(
            group_name="delivery_planning_v1", group_cfg=cfg, state=state, step="review_sop",
        )
        assert "review_sop" in result["model_approved_steps"]
        assert result["human_approvals"]["review_sop"]["force_override"] is True


# ---------------------------------------------------------------------------
# Retry helpers
# ---------------------------------------------------------------------------

class TestPrepareStateForRetry:
    def test_from_auto_retry(self, tmp_workspace, fake_workflow, set_context, real_job_on_disk):
        state = load_job(real_job_on_disk.group_name, real_job_on_disk.job_id)
        set_job_status(state, "WAITING_FOR_AUTO_RETRY")
        save_job(real_job_on_disk.group_name, real_job_on_disk.job_id, state)
        result = prepare_state_for_retry(
            group_name=real_job_on_disk.group_name, state=state, step="project_analysis",
        )
        assert get_job_status(result) == "IN_PROGRESS"

    def test_from_human_intervention(self, tmp_workspace, fake_workflow, set_context, real_job_on_disk):
        state = load_job(real_job_on_disk.group_name, real_job_on_disk.job_id)
        set_job_status(state, "WAITING_FOR_HUMAN_INTERVENTION")
        state["pending_intervention_for"] = "task"
        save_job(real_job_on_disk.group_name, real_job_on_disk.job_id, state)
        result = prepare_state_for_retry(
            group_name=real_job_on_disk.group_name, state=state, step="task",
        )
        assert state["pending_intervention_for"] is None


class TestEnforceRetryLimit:
    def test_no_error_under_limit(self):
        state = {"job_id": "X-001", "reject_counts": {"task": 2}}
        enforce_retry_limit_before_run(state=state, step="task", max_rejects=3)

    def test_raises_at_limit(self):
        state = {"job_id": "X-001", "reject_counts": {"task": 3}}
        with pytest.raises(ValueError, match="max rejects"):
            enforce_retry_limit_before_run(state=state, step="task", max_rejects=3)

    def test_negative_max_rejects_disables_check(self):
        state = {"job_id": "X-001", "reject_counts": {"task": 999}}
        enforce_retry_limit_before_run(state=state, step="task", max_rejects=-1)


# ---------------------------------------------------------------------------
# Failure classification
# ---------------------------------------------------------------------------

class TestLooksLikeTransientError:
    @pytest.mark.parametrize("msg", [
        "Connection error: refused",
        "fetch failed for api",
        "Request timed out",
        "timeout exceeded",
        "temporary failure",
        "rate limit exceeded",
        "Got 429 from API",
        "service unavailable",
        "API error: 500",
        "network error: unreachable",
    ])
    def test_transient(self, msg):
        assert looks_like_transient_error(msg) is True

    @pytest.mark.parametrize("msg", [
        "File not found",
        "Invalid JSON",
        "coder executable not found",
        "unknown error",
    ])
    def test_not_transient(self, msg):
        assert looks_like_transient_error(msg) is False


class TestClassifyPreRunFailure:
    def test_transient(self):
        exc = RuntimeError("Connection error: refused")
        result = classify_pre_run_failure(exc)
        assert result["failure_class"] == "AUTO_RETRYABLE"
        assert result["failure_code"] == "TRANSIENT_PRE_RUN_FAILURE"

    def test_file_not_found_generic(self):
        exc = FileNotFoundError("some file missing")
        result = classify_pre_run_failure(exc)
        assert result["failure_class"] == "HUMAN_RETRY_REQUIRED"
        assert result["failure_code"] == "MISSING_REQUIRED_FILE"

    def test_json_decode_error(self):
        exc = json.JSONDecodeError("bad json", "", 0)
        result = classify_pre_run_failure(exc)
        assert result["failure_class"] == "FATAL"
        assert result["failure_code"] == "CORRUPTED_JOB_STATE"

    def test_valueerror_unknown_coder(self):
        exc = ValueError("coder executable not found: /bin/bad")
        result = classify_pre_run_failure(exc)
        assert result["failure_code"] == "UNKNOWN_CODER"

    def test_valueerror_waiting_approval(self):
        exc = ValueError("waiting for human approval")
        result = classify_pre_run_failure(exc)
        assert result["failure_code"] == "WAITING_FOR_HUMAN_APPROVAL"

    def test_unknown_exception_is_fatal(self):
        exc = TypeError("something weird")
        result = classify_pre_run_failure(exc)
        assert result["failure_class"] == "FATAL"
        assert result["failure_code"] == "PRE_RUN_FAILURE"


# ---------------------------------------------------------------------------
# Task execution binding
# ---------------------------------------------------------------------------

class TestTaskExecutionBinding:
    def test_identity_none_binding(self):
        assert task_execution_binding_identity(None) == (None, None)

    def test_identity_empty_binding(self):
        assert task_execution_binding_identity({}) == (None, None)

    def test_current_item_none_binding(self):
        assert task_execution_binding_current_item({}) is None

    def test_current_item_valid(self):
        state = {
            "task_execution_binding": {
                "task_node_id": "TASK-001",
                "task_title": "Do stuff",
            },
        }
        item = task_execution_binding_current_item(state)
        assert item["task_node_id"] == "TASK-001"
        assert item["title"] == "Do stuff"

    def test_apply_binding(self, tmp_workspace, fake_workflow, set_context):
        state = {"artifacts": {}}
        binding = {
            "task_graph_file": "docs/graph.md",
            "plan_file": "docs/plan.md",
            "task_node_id": "TASK-001",
            "task_graph_checksum": "abc123",
            "task_node_snapshot": {"task_node_id": "TASK-001", "title": "T", "sequence": 1},
        }
        apply_task_execution_binding(state, binding)
        assert state["artifacts"]["TASK_GRAPH_FILE"] == "docs/graph.md"
        assert state["seed_artifact_type"] == "TASK_EXECUTION_BINDING"


# ---------------------------------------------------------------------------
# Initialize task generation state
# ---------------------------------------------------------------------------

class TestInitializeTaskGenerationState:
    def test_raises_when_already_initialized(self):
        state = {"task_generation_state": {"ordered_tasks": [{"id": 1}]}}
        with pytest.raises(ValueError, match="already initialized"):
            initialize_task_generation_state(state)

    def test_raises_without_task_graph_file(self):
        state = {"artifacts": {}}
        with pytest.raises(ValueError, match="without TASK_GRAPH_FILE"):
            initialize_task_generation_state(state)

    def test_successful_init(self, tmp_workspace, fake_workflow, set_context):
        content = (
            "---\n- **Task Graph ID**: TG-001\n- **Plan ID**: PL-001\n---\n"
            "### `TASK-20260601-1` — First task\n"
        )
        p = tmp_workspace.workspace_root / "tg.md"
        p.write_text(content)
        state = {"artifacts": {"TASK_GRAPH_FILE": "tg.md"}}
        initialize_task_generation_state(state)
        assert task_queue_is_initialized(state) is True
        assert state["task_generation_state"]["source_task_graph"] == "tg.md"
        assert state["artifacts"]["TASK_FILE"] is None


# ---------------------------------------------------------------------------
# Planning task queue integrity
# ---------------------------------------------------------------------------

class TestEnsurePlanningTaskQueueIntegrity:
    def test_noop_wrong_group(self):
        state = {"template_group": "other_v1"}
        ensure_planning_task_queue_integrity(state, step="task")

    def test_noop_wrong_step(self, tmp_workspace, fake_workflow, set_context):
        state = {"template_group": "delivery_planning_v1"}
        ensure_planning_task_queue_integrity(state, step="project_analysis")

    def test_raises_when_queue_not_initialized(self, tmp_workspace, fake_workflow, set_context):
        state = {"template_group": "delivery_planning_v1"}
        with pytest.raises(PreflightBlockedError, match="not initialized"):
            ensure_planning_task_queue_integrity(state, step="task")

    def test_raises_when_source_missing(self, tmp_workspace, fake_workflow, set_context):
        state = {
            "template_group": "delivery_planning_v1",
            "task_generation_state": {
                "source_task_graph": "missing_tg.md",
                "source_task_graph_checksum": "abc",
                "ordered_tasks": [{"queue_item_id": "tgq_0001", "status": "PENDING"}],
                "current_queue_item_id": "tgq_0001",
            },
        }
        with pytest.raises(PreflightBlockedError, match="missing"):
            ensure_planning_task_queue_integrity(state, step="task")
