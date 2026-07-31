"""Unit tests for operator console runner_service module.

Tests CLI argument construction, output processing, JSON parsing,
error handling, and the invoke machinery.
"""
from __future__ import annotations

import json
import os

import pytest
from unittest.mock import MagicMock, patch

from agent_runner_v2.operator_console.models import GlobalSettings, WorkflowEntry
from agent_runner_v2.operator_console.services.runner_service import (
    ActionExecutionError,
    RunnerActionService,
    _extract_runs_from_json,
)


@pytest.fixture
def settings():
    return GlobalSettings(
        backend_url="http://127.0.0.1:8100",
        worker_id="worker-1",
        worker_label="live",
    )


@pytest.fixture
def service(settings):
    return RunnerActionService(settings)


@pytest.fixture
def workflow():
    return WorkflowEntry(name="SDLC Req", workflow_name="sdlc_10_requirement_v1")


# ---------------------------------------------------------------------------
# _extract_runs_from_json
# ---------------------------------------------------------------------------

class TestExtractRunsFromJson:
    def test_parses_list_format(self):
        data = json.dumps([
            {"id": "r1", "run_code": "J1", "workflow_name": "wf",
             "status": "running", "current_step": "s1", "updated_at": "2026-01-01"},
        ])
        runs = _extract_runs_from_json(data)
        assert len(runs) == 1
        assert runs[0].run_id == "r1"

    def test_parses_dict_with_runs_key(self):
        data = json.dumps({"runs": [
            {"id": "r1", "run_code": "J1", "workflow_name": "wf",
             "status": "running", "current_step": "s1", "updated_at": "2026-01-01"},
        ]})
        runs = _extract_runs_from_json(data)
        assert len(runs) == 1

    def test_parses_dict_with_items_key(self):
        data = json.dumps({"items": [
            {"id": "r1", "run_code": "J1", "workflow_name": "wf",
             "status": "running", "current_step": "s1", "updated_at": "2026-01-01"},
        ]})
        runs = _extract_runs_from_json(data)
        assert len(runs) == 1

    def test_parses_alternate_field_names(self):
        data = json.dumps([
            {"run_id": "r1", "job_id": "J1", "template_group": "wf",
             "job_status": "pending", "current_step_name": "s1",
             "modified_at": "2026-01-01", "target_worker_id": "w1",
             "target_project_root": "/repo"},
        ])
        runs = _extract_runs_from_json(data)
        assert len(runs) == 1
        assert runs[0].run_id == "r1"
        assert runs[0].run_code == "J1"
        assert runs[0].workflow_name == "wf"
        assert runs[0].status == "pending"
        assert runs[0].worker_id == "w1"
        assert runs[0].project_root == "/repo"

    def test_returns_empty_for_invalid_json(self):
        assert _extract_runs_from_json("not json") == []

    def test_returns_empty_for_none(self):
        assert _extract_runs_from_json(None) == []

    def test_skips_non_dict_items(self):
        data = json.dumps([42, "string", {"id": "r1", "run_code": "J1",
                     "workflow_name": "wf", "status": "running",
                     "current_step": "s1", "updated_at": "2026-01-01"}])
        runs = _extract_runs_from_json(data)
        assert len(runs) == 1

    def test_returns_empty_for_empty_list(self):
        assert _extract_runs_from_json("[]") == []


# ---------------------------------------------------------------------------
# submit_job
# ---------------------------------------------------------------------------

class TestSubmitJob:
    def test_builds_correct_argv(self, service, workflow, monkeypatch, tmp_path):
        captured = {}
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_submit(argv):
            captured["argv"] = list(argv or [])
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.submit_commands.main",
            fake_submit,
        )

        result = service.submit_job(
            repo_path=str(repo_path),
            workflow=workflow,
            input_artifacts={"INIT_FILE": "init.md"},
        )

        assert result == "ok"
        assert "--workflow-name" in captured["argv"]
        assert "sdlc_10_requirement_v1" in captured["argv"]
        assert "--worker-id" in captured["argv"]
        assert "worker-1" in captured["argv"]
        assert "--input" in captured["argv"]
        assert "INIT_FILE=init.md" in captured["argv"]

    def test_includes_start_step(self, service, workflow, monkeypatch, tmp_path):
        captured = {}
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_submit(argv):
            captured["argv"] = list(argv or [])
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.submit_commands.main",
            fake_submit,
        )

        service.submit_job(
            repo_path=str(repo_path),
            workflow=workflow,
            start_step="generate_docs",
        )

        assert "--start-step" in captured["argv"]
        assert "generate_docs" in captured["argv"]

    def test_no_input_artifacts_omits_input_flag(self, service, workflow, monkeypatch, tmp_path):
        captured = {}
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_submit(argv):
            captured["argv"] = list(argv or [])
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.submit_commands.main",
            fake_submit,
        )

        service.submit_job(repo_path=str(repo_path), workflow=workflow)

        assert "--input" not in captured["argv"]


# ---------------------------------------------------------------------------
# Backend API wrapper commands (invoke_from_anywhere)
# ---------------------------------------------------------------------------

class TestListRuns:
    def test_builds_argv_with_worker_id(self, service, monkeypatch):
        captured = {}

        def fake_list_runs(argv):
            captured["argv"] = list(argv or [])
            print('{"runs": []}')
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.list_runs_commands.main",
            fake_list_runs,
        )

        service.list_runs(worker_id="w1")
        assert "--worker-id" in captured["argv"]
        assert "w1" in captured["argv"]

    def test_default_status_group_is_non_terminal(self, service, monkeypatch):
        captured = {}

        def fake_list_runs(argv):
            captured["argv"] = list(argv or [])
            print('{"runs": []}')
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.list_runs_commands.main",
            fake_list_runs,
        )

        service.list_runs()
        assert "--status-group" in captured["argv"]
        assert "non_terminal" in captured["argv"]


class TestListActiveRunsForWorker:
    def test_parses_json_output(self, service, monkeypatch):
        def fake_list_runs(argv):
            print(json.dumps({"runs": [
                {"id": "r1", "run_code": "J1", "workflow_name": "wf",
                 "status": "running", "current_step": "s1", "updated_at": "t"},
            ]}))
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.list_runs_commands.main",
            fake_list_runs,
        )

        runs = service.list_active_runs_for_worker(worker_id="w1")
        assert len(runs) == 1
        assert runs[0].run_id == "r1"


class TestShowRun:
    def test_passes_run_id(self, service, monkeypatch):
        captured = {}

        def fake_show_run(argv):
            captured["argv"] = list(argv or [])
            print('{"id": "r1"}')
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.show_run_commands.main",
            fake_show_run,
        )

        service.show_run(run_id="r1")
        assert captured["argv"] == ["r1"]


class TestGetRunDetailDict:
    def test_returns_parsed_dict(self, service, monkeypatch):
        def fake_show_run(argv):
            print(json.dumps({"id": "r1", "status": "running"}))
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.show_run_commands.main",
            fake_show_run,
        )

        result = service.get_run_detail_dict(run_id="r1")
        assert result["id"] == "r1"
        assert result["status"] == "running"

    def test_returns_empty_dict_on_invalid_json(self, service, monkeypatch):
        def fake_show_run(argv):
            print("not json")
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.show_run_commands.main",
            fake_show_run,
        )

        result = service.get_run_detail_dict(run_id="r1")
        assert result == {}


class TestStopRun:
    def test_builds_argv_with_reason(self, service, monkeypatch):
        captured = {}

        def fake_stop(argv):
            captured["argv"] = list(argv or [])
            print('{"status": "ok"}')
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.stop_commands.main",
            fake_stop,
        )

        result = service.stop_run(run_id="r1", reason="Cancelled")
        assert captured["argv"] == ["r1", "--reason", "Cancelled"]
        assert '"status"' in result


class TestApprove:
    def test_approve_with_resume(self, service, monkeypatch):
        captured = {}

        def fake_approve(argv):
            captured["argv"] = list(argv or [])
            print('{"status": "ok"}')
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.approve_commands.main",
            fake_approve,
        )

        service.approve(run_id="r1", resume=True)
        assert captured["argv"] == ["r1", "--resume"]

    def test_approve_with_reject(self, service, monkeypatch):
        captured = {}

        def fake_approve(argv):
            captured["argv"] = list(argv or [])
            print('ok')
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.approve_commands.main",
            fake_approve,
        )

        service.approve(run_id="r1", reject=True, feedback="Needs work")
        assert "--reject" in captured["argv"]
        assert "--feedback" in captured["argv"]
        assert "Needs work" in captured["argv"]

    def test_approve_with_retry(self, service, monkeypatch):
        captured = {}

        def fake_approve(argv):
            captured["argv"] = list(argv or [])
            print('ok')
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.approve_commands.main",
            fake_approve,
        )

        service.approve(run_id="r1", retry=True)
        assert "--retry" in captured["argv"]


class TestResetStep:
    def test_builds_argv(self, service, monkeypatch):
        captured = {}

        def fake_reset(argv):
            captured["argv"] = list(argv or [])
            print('ok')
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.reset_step_commands.main",
            fake_reset,
        )

        service.reset_step(run_id="r1", step_name="audit_docs")
        assert captured["argv"] == ["r1", "audit_docs"]


# ---------------------------------------------------------------------------
# Step-level interventions
# ---------------------------------------------------------------------------

class TestStepInterventions:
    def test_approve_step_argv(self, service, monkeypatch, tmp_path):
        captured = {}
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_run_agent(argv):
            captured["argv"] = list(argv or [])
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.run_agent.main",
            fake_run_agent,
        )

        service.approve_step(
            repo_path=str(repo_path),
            template_group="wf_v1",
            job_id="J1",
            step_name="step_a",
        )

        assert captured["argv"] == [
            "run", "--template-group", "wf_v1",
            "--job-id", "J1", "--approve-step", "step_a",
        ]

    def test_reject_step_argv(self, service, monkeypatch, tmp_path):
        captured = {}
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_run_agent(argv):
            captured["argv"] = list(argv or [])
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.run_agent.main",
            fake_run_agent,
        )

        service.reject_step(
            repo_path=str(repo_path),
            template_group="wf_v1",
            job_id="J1",
            step_name="step_a",
        )

        assert "--reject-step" in captured["argv"]

    def test_resume_step_argv(self, service, monkeypatch, tmp_path):
        captured = {}
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_run_agent(argv):
            captured["argv"] = list(argv or [])
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.run_agent.main",
            fake_run_agent,
        )

        service.resume_step(
            repo_path=str(repo_path),
            template_group="wf_v1",
            job_id="J1",
            step_name="step_a",
        )

        assert "--resume-step" in captured["argv"]

    def test_retry_step_argv(self, service, monkeypatch, tmp_path):
        captured = {}
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_run_agent(argv):
            captured["argv"] = list(argv or [])
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.run_agent.main",
            fake_run_agent,
        )

        service.retry_step(
            repo_path=str(repo_path),
            template_group="wf_v1",
            job_id="J1",
            step_name="step_a",
        )

        assert "--retry-step" in captured["argv"]

    def test_cancel_run_argv(self, service, monkeypatch, tmp_path):
        captured = {}
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_run_agent(argv):
            captured["argv"] = list(argv or [])
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.run_agent.main",
            fake_run_agent,
        )

        service.cancel_run(
            repo_path=str(repo_path),
            template_group="wf_v1",
            job_id="J1",
        )

        assert "--cancel-run" in captured["argv"]

    def test_override_step_argv(self, service, monkeypatch, tmp_path):
        captured = {}
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_run_agent(argv):
            captured["argv"] = list(argv or [])
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.run_agent.main",
            fake_run_agent,
        )

        service.override_step(
            repo_path=str(repo_path),
            template_group="wf_v1",
            job_id="J1",
            step_name="step_b",
        )

        assert "--override-step" in captured["argv"]
        assert "step_b" in captured["argv"]


# ---------------------------------------------------------------------------
# Utility actions
# ---------------------------------------------------------------------------

class TestUtilityActions:
    def test_init_workspace_argv(self, service, monkeypatch, tmp_path):
        captured = {}
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_run_agent(argv):
            captured["argv"] = list(argv or [])
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.run_agent.main",
            fake_run_agent,
        )

        service.init_workspace(repo_path=str(repo_path))

        assert "init" in captured["argv"]
        assert "--workflow" in captured["argv"]

    def test_bootstrap_publish_argv(self, service, monkeypatch, tmp_path):
        captured = {}
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_run_agent(argv):
            captured["argv"] = list(argv or [])
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.run_agent.main",
            fake_run_agent,
        )

        service.bootstrap_publish(repo_path=str(repo_path))

        assert "bootstrap-publish" in captured["argv"]

    def test_sync_workflow_argv(self, service, monkeypatch, tmp_path):
        captured = {}
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_sync(argv):
            captured["argv"] = list(argv or [])
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.sync_workflows.main",
            fake_sync,
        )

        wf = WorkflowEntry(name="WF", workflow_name="wf_v1")
        service.sync_workflow(repo_path=str(repo_path), workflow=wf)

        assert "wf_v1" in captured["argv"]

    def test_quit_daemon_argv(self, service, monkeypatch, tmp_path):
        captured = {}
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_run_agent(argv):
            captured["argv"] = list(argv or [])
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.run_agent.main",
            fake_run_agent,
        )

        service.quit_daemon(repo_path=str(repo_path), reason="Shutdown")

        assert "daemon-quit" in captured["argv"]
        assert "--reason" in captured["argv"]
        assert "Shutdown" in captured["argv"]


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    def test_nonzero_exit_raises_action_execution_error(self, service, monkeypatch, tmp_path):
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_submit(argv):
            print("Error: something went wrong", flush=True)
            return 1

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.submit_commands.main",
            fake_submit,
        )

        with pytest.raises(ActionExecutionError):
            service.submit_job(
                repo_path=str(repo_path),
                workflow=WorkflowEntry(name="WF", workflow_name="wf"),
            )

    def test_exception_in_cli_raises_action_execution_error(self, service, monkeypatch, tmp_path):
        repo_path = tmp_path / "repo"
        repo_path.mkdir()

        def fake_submit(argv):
            raise RuntimeError("boom")

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.submit_commands.main",
            fake_submit,
        )

        with pytest.raises(ActionExecutionError):
            service.submit_job(
                repo_path=str(repo_path),
                workflow=WorkflowEntry(name="WF", workflow_name="wf"),
            )

    def test_stderr_only_returned_when_no_stdout(self, service, monkeypatch):
        def fake_list_runs(argv):
            import sys
            print("warning: deprecated", file=sys.stderr)
            return 0

        monkeypatch.setattr(
            "agent_runner_v2.operator_console.services.runner_service.list_runs_commands.main",
            fake_list_runs,
        )

        result = service.list_runs()
        assert "warning" in result
