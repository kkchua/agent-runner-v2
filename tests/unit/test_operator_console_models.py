"""Unit tests for operator_console models module.

Tests dataclass definitions, field defaults, immutability, and relationships.
"""
from __future__ import annotations

import pytest

from agent_runner_v2.operator_console.models import (
    ActiveRunSummary,
    ConsoleConfig,
    GlobalSettings,
    RepoEntry,
    WorkflowEntry,
)


class TestGlobalSettings:
    def test_required_fields(self):
        settings = GlobalSettings(
            backend_url="http://localhost:8100",
            worker_id="worker-1",
            worker_label="",
        )
        assert settings.backend_url == "http://localhost:8100"
        assert settings.worker_id == "worker-1"
        assert settings.worker_label == ""

    def test_all_fields_set(self):
        settings = GlobalSettings(
            backend_url="http://example.com:8080",
            worker_id="worker-42",
            worker_label="production",
        )
        assert settings.backend_url == "http://example.com:8080"
        assert settings.worker_id == "worker-42"
        assert settings.worker_label == "production"

    def test_frozen_dataclass_is_immutable(self):
        settings = GlobalSettings(
            backend_url="http://localhost:8100",
            worker_id="worker-1",
            worker_label="",
        )
        with pytest.raises(AttributeError):
            settings.worker_id = "new-worker"


class TestWorkflowEntry:
    def test_required_fields(self):
        entry = WorkflowEntry(name="My Workflow", workflow_name="my_workflow_v1")
        assert entry.name == "My Workflow"
        assert entry.workflow_name == "my_workflow_v1"
        assert entry.template_group is None

    def test_template_group_optional(self):
        entry = WorkflowEntry(
            name="My Workflow",
            workflow_name="my_workflow_v1",
            template_group="my_template_v1",
        )
        assert entry.template_group == "my_template_v1"

    def test_frozen_dataclass_is_immutable(self):
        entry = WorkflowEntry(name="WF", workflow_name="wf_v1")
        with pytest.raises(AttributeError):
            entry.name = "New Name"


class TestRepoEntry:
    def test_required_fields_and_defaults(self):
        entry = RepoEntry(name="My Repo", path="/path/to/repo")
        assert entry.name == "My Repo"
        assert entry.path == "/path/to/repo"
        assert entry.worker_id == ""
        assert entry.os_type == ""
        assert entry.workflows == ()

    def test_all_fields_set(self):
        workflows = (
            WorkflowEntry(name="WF1", workflow_name="wf1"),
            WorkflowEntry(name="WF2", workflow_name="wf2"),
        )
        entry = RepoEntry(
            name="My Repo",
            path="/path/to/repo",
            worker_id="worker-1",
            os_type="windows",
            workflows=workflows,
        )
        assert entry.worker_id == "worker-1"
        assert entry.os_type == "windows"
        assert len(entry.workflows) == 2

    def test_frozen_dataclass_is_immutable(self):
        entry = RepoEntry(name="Repo", path="/path")
        with pytest.raises(AttributeError):
            entry.path = "/new/path"


class TestConsoleConfig:
    def test_empty_repos(self):
        config = ConsoleConfig(repos=())
        assert config.repos == ()

    def test_repos_tuple(self):
        repos = (
            RepoEntry(name="Repo1", path="/path/1"),
            RepoEntry(name="Repo2", path="/path/2"),
        )
        config = ConsoleConfig(repos=repos)
        assert len(config.repos) == 2

    def test_frozen_dataclass_is_immutable(self):
        config = ConsoleConfig(repos=())
        with pytest.raises(AttributeError):
            config.repos = (RepoEntry(name="New", path="/new"),)


class TestActiveRunSummary:
    def test_required_fields(self):
        run = ActiveRunSummary(
            run_id="run-uuid-123",
            run_code="JOB-001",
            workflow_name="my_workflow",
            status="running",
            current_step="step_01",
            updated_at="2026-07-30T10:00:00",
        )
        assert run.run_id == "run-uuid-123"
        assert run.run_code == "JOB-001"
        assert run.workflow_name == "my_workflow"
        assert run.status == "running"
        assert run.current_step == "step_01"
        assert run.updated_at == "2026-07-30T10:00:00"
        assert run.worker_id == ""
        assert run.project_root == ""

    def test_optional_fields(self):
        run = ActiveRunSummary(
            run_id="run-1",
            run_code="JOB-001",
            workflow_name="wf",
            status="pending",
            current_step="",
            updated_at="2026-07-30T10:00:00",
            worker_id="worker-1",
            project_root="/path/to/project",
        )
        assert run.worker_id == "worker-1"
        assert run.project_root == "/path/to/project"

    def test_frozen_dataclass_is_immutable(self):
        run = ActiveRunSummary(
            run_id="r1",
            run_code="J1",
            workflow_name="wf",
            status="running",
            current_step="s1",
            updated_at="2026-07-30T10:00:00",
        )
        with pytest.raises(AttributeError):
            run.status = "completed"


class TestDataclassRelationships:
    def test_full_config_hierarchy(self):
        workflows = (
            WorkflowEntry(name="WF1", workflow_name="wf1_v1"),
            WorkflowEntry(name="WF2", workflow_name="wf2_v1"),
        )
        repos = (
            RepoEntry(name="Main", path="/path", worker_id="w1", workflows=workflows),
        )
        config = ConsoleConfig(repos=repos)
        assert len(config.repos) == 1
        assert len(config.repos[0].workflows) == 2

    def test_active_run_can_reference_workflow(self):
        config = ConsoleConfig(repos=(
            RepoEntry(
                name="Repo",
                path="/path",
                workflows=(WorkflowEntry(name="My WF", workflow_name="my_wf"),),
            ),
        ))
        run = ActiveRunSummary(
            run_id="r1",
            run_code="J1",
            workflow_name="my_wf",
            status="running",
            current_step="s1",
            updated_at="2026-07-30T10:00:00",
        )
        matches = [
            wf for repo in config.repos for wf in repo.workflows
            if wf.workflow_name == run.workflow_name
        ]
        assert len(matches) == 1
        assert matches[0].name == "My WF"
