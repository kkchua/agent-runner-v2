"""Unit tests for operator_console state module.

Tests ConsoleState dataclass: worker filtering, repo lookup, workflow options,
error display, and default values.
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from agent_runner_v2.operator_console.models import ConsoleConfig, RepoEntry, WorkflowEntry
from agent_runner_v2.operator_console.state import ConsoleState


@pytest.fixture
def mock_page():
    page = MagicMock()
    page.update = MagicMock()
    return page


@pytest.fixture
def sample_config():
    return ConsoleConfig(
        repos=(
            RepoEntry(
                name="Repo1",
                path="/path/to/repo1",
                worker_id="worker-1",
                os_type="windows",
                workflows=(
                    WorkflowEntry(name="WF1", workflow_name="wf1"),
                    WorkflowEntry(name="WF2", workflow_name="wf2"),
                ),
            ),
            RepoEntry(
                name="Repo2",
                path="/path/to/repo2",
                worker_id="worker-1",
                os_type="linux",
                workflows=(
                    WorkflowEntry(name="WF3", workflow_name="wf3"),
                ),
            ),
            RepoEntry(
                name="Repo3",
                path="/path/to/repo3",
                worker_id="worker-2",
                os_type="windows",
                workflows=(),
            ),
            RepoEntry(
                name="NoWorker",
                path="/path/to/noworker",
                worker_id="",
                workflows=(),
            ),
        )
    )


@pytest.fixture
def console_state(mock_page, sample_config):
    return ConsoleState(page=mock_page, config=sample_config)


class TestAllWorkerIds:
    def test_returns_unique_sorted(self, console_state):
        assert console_state.all_worker_ids() == ["worker-1", "worker-2"]

    def test_empty_when_no_workers(self, mock_page):
        config = ConsoleConfig(repos=(
            RepoEntry(name="R", path="/p", worker_id=""),
        ))
        state = ConsoleState(page=mock_page, config=config)
        assert state.all_worker_ids() == []

    def test_deduplicates_same_worker(self, console_state):
        ids = console_state.all_worker_ids()
        assert ids.count("worker-1") == 1


class TestReposForWorker:
    def test_filters_correctly(self, console_state):
        result = console_state.repos_for_worker("worker-1")
        assert len(result) == 2
        assert {r.name for r in result} == {"Repo1", "Repo2"}

    def test_single_match(self, console_state):
        result = console_state.repos_for_worker("worker-2")
        assert len(result) == 1
        assert result[0].name == "Repo3"

    def test_empty_when_no_match(self, console_state):
        result = console_state.repos_for_worker("nonexistent")
        assert result == []

    def test_empty_worker_id_matches_repos_without_worker(self, console_state):
        result = console_state.repos_for_worker("")
        assert len(result) == 1
        assert result[0].name == "NoWorker"


class TestSelectedRepoPath:
    def test_raises_when_none(self, console_state):
        from agent_runner_v2.operator_console.services.runner_service import ActionExecutionError
        console_state.selected_repo = None
        with pytest.raises(ActionExecutionError, match="Select a repo"):
            console_state.selected_repo_path()

    def test_returns_path_when_selected(self, console_state):
        console_state.selected_repo = console_state.config.repos[0]
        assert console_state.selected_repo_path() == "/path/to/repo1"


class TestFindWorkflow:
    def test_finds_by_workflow_name(self, console_state):
        repo_path, workflow = console_state.find_workflow("wf2")
        assert repo_path == "/path/to/repo1"
        assert workflow is not None
        assert workflow.name == "WF2"

    def test_finds_in_second_repo(self, console_state):
        repo_path, workflow = console_state.find_workflow("wf3")
        assert repo_path == "/path/to/repo2"
        assert workflow is not None
        assert workflow.name == "WF3"

    def test_returns_none_when_not_found(self, console_state):
        repo_path, workflow = console_state.find_workflow("nonexistent")
        assert repo_path == ""
        assert workflow is None


class TestCreateWorkflowOptions:
    def test_empty_when_no_repo(self, console_state):
        console_state.selected_repo = None
        assert console_state.create_workflow_options() == []

    def test_returns_dropdown_options(self, console_state):
        console_state.selected_repo = console_state.config.repos[0]
        result = console_state.create_workflow_options()
        assert len(result) == 2
        assert result[0].key == "WF1"
        assert result[0].text == "WF1"
        assert result[1].key == "WF2"

    def test_empty_workflows_tuple(self, console_state):
        console_state.selected_repo = console_state.config.repos[2]  # Repo3, no workflows
        assert console_state.create_workflow_options() == []


class TestUpdate:
    def test_calls_page_update(self, console_state, mock_page):
        console_state.update()
        mock_page.update.assert_called_once()

    def test_does_nothing_when_no_page(self, mock_page, sample_config):
        state = ConsoleState(page=mock_page, config=sample_config)
        state.page = None
        state.update()  # Should not raise


class TestShowError:
    def test_shows_dialog(self, console_state, mock_page):
        console_state.show_error("Test error message")
        mock_page.show_dialog.assert_called_once()

    def test_dialog_contains_message(self, console_state, mock_page):
        console_state.show_error("Specific error text")
        dialog = mock_page.show_dialog.call_args[0][0]
        assert "Specific error text" in str(dialog.content.value)


class TestDefaults:
    def test_default_worker_id_is_empty(self, mock_page):
        state = ConsoleState(page=mock_page, config=ConsoleConfig(repos=()))
        assert state.selected_worker_id == ""

    def test_default_repo_is_none(self, mock_page):
        state = ConsoleState(page=mock_page, config=ConsoleConfig(repos=()))
        assert state.selected_repo is None

    def test_default_workflow_is_none(self, mock_page):
        state = ConsoleState(page=mock_page, config=ConsoleConfig(repos=()))
        assert state.selected_workflow is None

    def test_default_run_id_is_empty(self, mock_page):
        state = ConsoleState(page=mock_page, config=ConsoleConfig(repos=()))
        assert state.selected_run_id == ""

    def test_default_active_runs_is_empty_list(self, mock_page):
        state = ConsoleState(page=mock_page, config=ConsoleConfig(repos=()))
        assert state.active_runs == []

    def test_default_input_fields_is_empty_dict(self, mock_page):
        state = ConsoleState(page=mock_page, config=ConsoleConfig(repos=()))
        assert state.input_fields == {}

    def test_default_runner_service_is_none(self, mock_page):
        state = ConsoleState(page=mock_page, config=ConsoleConfig(repos=()))
        assert state.runner_service is None

    def test_all_widget_refs_default_to_none(self, mock_page):
        state = ConsoleState(page=mock_page, config=ConsoleConfig(repos=()))
        assert state.file_picker is None
        assert state.worker_id_dd is None
        assert state.repo_dd is None
        assert state.workflow_dd is None
        assert state.action_dd is None
        assert state.reset_step_dd is None
        assert state.start_step_dd is None
        assert state.active_runs_dd is None
        assert state.dynamic_inputs_column is None
        assert state.dynamic_inputs_container is None
        assert state.feedback_tf is None
        assert state.status_text is None
        assert state.output is None
        assert state.auto_refresh_cb is None
