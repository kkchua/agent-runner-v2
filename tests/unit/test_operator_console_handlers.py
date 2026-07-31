"""Unit tests for operator_console handlers module.

Tests EventHandlers operational behavior: dropdown cascading, action dispatch,
active run refresh, dynamic input building, and confirmation dialogs.
"""
from __future__ import annotations

import asyncio
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from agent_runner_v2.operator_console.handlers import (
    EventHandlers,
    _get_input_dir_for_key,
    _is_cross_os,
    _resolve_file_picker_root,
    SDLC_INPUT_DIRS,
    KNOWN_FILE_INPUTS,
)
from agent_runner_v2.operator_console.models import (
    ActiveRunSummary,
    ConsoleConfig,
    RepoEntry,
    WorkflowEntry,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_run(run_id="run-1", run_code="JOB-001", workflow_name="wf",
              status="running", current_step="step1", **kwargs):
    return ActiveRunSummary(
        run_id=run_id,
        run_code=run_code,
        workflow_name=workflow_name,
        status=status,
        current_step=current_step,
        updated_at="2026-07-30T10:00:00",
        **kwargs,
    )


def _make_state(**overrides):
    state = MagicMock()
    state.worker_id_dd = MagicMock()
    state.worker_id_dd.value = "worker-1"
    state.repo_dd = MagicMock()
    state.workflow_dd = MagicMock()
    state.action_dd = MagicMock()
    state.reset_step_dd = MagicMock()
    state.start_step_dd = MagicMock()
    state.active_runs_dd = MagicMock()
    state.feedback_tf = MagicMock()
    state.dynamic_inputs_column = MagicMock()
    state.dynamic_inputs_container = MagicMock()
    state.file_picker = None
    state.page = MagicMock()
    state.selected_worker_id = ""
    state.selected_repo = None
    state.selected_workflow = None
    state.selected_run_id = ""
    state.active_runs = []
    state.input_fields = {}
    state.runner_service = None
    state.config = MagicMock()
    state.config.repos = []
    state.repos_for_worker.return_value = []
    state.create_workflow_options.return_value = []
    state.update = MagicMock()
    for k, v in overrides.items():
        setattr(state, k, v)
    return state


# ---------------------------------------------------------------------------
# Pure helper function tests
# ---------------------------------------------------------------------------

class TestIsCrossOs:
    def test_same_os_returns_false(self):
        import sys
        if sys.platform == "win32":
            assert _is_cross_os("windows") is False
        else:
            assert _is_cross_os("linux") is False

    def test_different_os_returns_true(self):
        import sys
        if sys.platform == "win32":
            assert _is_cross_os("linux") is True
        else:
            assert _is_cross_os("windows") is True

    def test_empty_string_returns_false(self):
        assert _is_cross_os("") is False


class TestResolveFilePickerRoot:
    def test_cross_os_returns_home(self):
        import sys
        from pathlib import Path
        cross_os = "linux" if sys.platform == "win32" else "windows"
        result = _resolve_file_picker_root("/repo", "docs/input", cross_os)
        assert result == str(Path.home())

    def test_input_dir_resolved(self, tmp_path):
        input_dir = tmp_path / "docs" / "input"
        input_dir.mkdir(parents=True)
        result = _resolve_file_picker_root(str(tmp_path), "docs/input", "")
        assert result == str(input_dir)

    def test_falls_back_to_repo_path(self):
        result = _resolve_file_picker_root("/repo", None, "")
        assert result == "/repo"

    def test_dot_input_dir_falls_back_to_repo(self):
        result = _resolve_file_picker_root("/repo", ".", "")
        assert result == "/repo"


class TestGetInputDirForKey:
    def test_known_key_returns_dir(self):
        result = _get_input_dir_for_key("DRAFT_INIT_FILE", "nonexistent_wf")
        assert result is not None
        assert "00_draft_initiatives" in result

    def test_unknown_key_returns_none(self):
        result = _get_input_dir_for_key("UNKNOWN_KEY", "nonexistent_wf")
        assert result is None


class TestSdlcConstants:
    def test_all_known_file_inputs_are_in_sdlc_dirs(self):
        assert KNOWN_FILE_INPUTS.issubset(set(SDLC_INPUT_DIRS.keys()))

    def test_known_file_inputs_not_empty(self):
        assert len(KNOWN_FILE_INPUTS) > 0


# ---------------------------------------------------------------------------
# on_worker_id_changed
# ---------------------------------------------------------------------------

class TestOnWorkerIdChanged:
    def test_returns_early_when_widgets_none(self):
        state = _make_state(worker_id_dd=None, repo_dd=None)
        handlers = EventHandlers(state)
        handlers.on_worker_id_changed()
        state.update.assert_not_called()

    def test_updates_selected_worker_id(self):
        state = _make_state()
        state.worker_id_dd.value = "worker-2"
        handlers = EventHandlers(state)
        handlers.on_worker_id_changed()
        assert state.selected_worker_id == "worker-2"

    def test_populates_repo_dropdown_with_filtered_repos(self):
        repo1 = MagicMock()
        repo1.name = "RepoA"
        repo2 = MagicMock()
        repo2.name = "RepoB"
        state = _make_state()
        state.repos_for_worker.return_value = [repo1, repo2]
        handlers = EventHandlers(state)

        handlers.on_worker_id_changed()

        assert len(state.repo_dd.options) == 2
        assert state.repo_dd.options[0].key == "RepoA"
        assert state.repo_dd.options[1].key == "RepoB"

    def test_disables_repo_dropdown_when_no_repos(self):
        state = _make_state()
        state.repos_for_worker.return_value = []
        handlers = EventHandlers(state)

        handlers.on_worker_id_changed()

        assert state.repo_dd.disabled is True

    def test_enables_repo_dropdown_when_repos_exist(self):
        state = _make_state()
        state.repos_for_worker.return_value = [MagicMock()]
        handlers = EventHandlers(state)

        handlers.on_worker_id_changed()

        assert state.repo_dd.disabled is False

    def test_clears_repo_selection(self):
        state = _make_state()
        state.repo_dd.value = "old-repo"
        handlers = EventHandlers(state)

        handlers.on_worker_id_changed()

        assert state.repo_dd.value is None

    def test_clears_workflow_dropdown(self):
        state = _make_state()
        state.workflow_dd.value = "old-wf"
        state.workflow_dd.options = [MagicMock()]
        handlers = EventHandlers(state)

        handlers.on_worker_id_changed()

        assert state.workflow_dd.options == []
        assert state.workflow_dd.value is None

    def test_clears_dynamic_inputs(self):
        state = _make_state()
        state.input_fields = {"key1": MagicMock()}
        state.dynamic_inputs_column.controls = [MagicMock()]
        state.dynamic_inputs_container.visible = True
        handlers = EventHandlers(state)

        handlers.on_worker_id_changed()

        assert len(state.input_fields) == 0
        assert state.dynamic_inputs_container.visible is False

    def test_handles_none_worker_value(self):
        state = _make_state()
        state.worker_id_dd.value = None
        handlers = EventHandlers(state)

        handlers.on_worker_id_changed()

        assert state.selected_worker_id == ""


# ---------------------------------------------------------------------------
# on_repo_changed
# ---------------------------------------------------------------------------

class TestOnRepoChanged:
    def test_returns_early_when_widgets_none(self):
        state = _make_state(repo_dd=None, workflow_dd=None)
        handlers = EventHandlers(state)
        handlers.on_repo_changed()
        state.update.assert_not_called()

    def test_finds_repo_by_name(self):
        repo1 = MagicMock()
        repo1.name = "Repo1"
        repo2 = MagicMock()
        repo2.name = "Repo2"
        state = _make_state()
        state.config.repos = [repo1, repo2]
        state.repo_dd.value = "Repo2"
        handlers = EventHandlers(state)

        handlers.on_repo_changed()

        assert state.selected_repo is repo2

    def test_sets_selected_repo_to_none_when_not_found(self):
        state = _make_state()
        state.config.repos = []
        state.repo_dd.value = "nonexistent"
        handlers = EventHandlers(state)

        handlers.on_repo_changed()

        assert state.selected_repo is None

    def test_populates_workflow_dropdown(self):
        repo = MagicMock()
        repo.name = "Repo1"
        state = _make_state()
        state.config.repos = [repo]
        state.repo_dd.value = "Repo1"
        wf_options = [MagicMock()]
        state.create_workflow_options.return_value = wf_options
        handlers = EventHandlers(state)

        handlers.on_repo_changed()

        assert state.workflow_dd.options is wf_options
        assert state.workflow_dd.value is None

    def test_clears_dynamic_inputs(self):
        state = _make_state()
        state.input_fields = {"key": MagicMock()}
        handlers = EventHandlers(state)

        handlers.on_repo_changed()

        assert len(state.input_fields) == 0


# ---------------------------------------------------------------------------
# on_workflow_changed
# ---------------------------------------------------------------------------

class TestOnWorkflowChanged:
    def test_returns_early_when_widget_none(self):
        state = _make_state(workflow_dd=None)
        handlers = EventHandlers(state)
        handlers.on_workflow_changed()
        state.update.assert_not_called()

    def test_clears_selection_when_no_repo(self):
        state = _make_state()
        state.selected_repo = None
        state.workflow_dd.value = "wf1"
        handlers = EventHandlers(state)

        handlers.on_workflow_changed()

        assert state.selected_workflow is None

    def test_finds_workflow_in_selected_repo(self):
        wf1 = MagicMock()
        wf1.name = "WF1"
        wf2 = MagicMock()
        wf2.name = "WF2"
        repo = MagicMock()
        repo.workflows = [wf1, wf2]
        state = _make_state()
        state.selected_repo = repo
        state.workflow_dd.value = "WF2"
        handlers = EventHandlers(state)

        handlers.on_workflow_changed()

        assert state.selected_workflow is wf2

    def test_clears_inputs_when_workflow_not_found(self):
        repo = MagicMock()
        repo.workflows = []
        state = _make_state()
        state.selected_repo = repo
        state.workflow_dd.value = "nonexistent"
        handlers = EventHandlers(state)

        handlers.on_workflow_changed()

        assert state.selected_workflow is None


# ---------------------------------------------------------------------------
# on_action_changed
# ---------------------------------------------------------------------------

class TestOnActionChanged:
    def test_returns_early_when_widget_none(self):
        state = _make_state(action_dd=None)
        handlers = EventHandlers(state)
        handlers.on_action_changed()
        state.update.assert_not_called()

    @pytest.mark.parametrize("action", ["Approve", "Reject", "Resume", "Retry", "Reset", "Cancel"])
    def test_shows_feedback_for_actions_needing_active_run(self, action):
        state = _make_state()
        state.action_dd.value = action
        handlers = EventHandlers(state)

        handlers.on_action_changed()

        assert state.feedback_tf.visible is True

    @pytest.mark.parametrize("action", ["Submit", "Quit Daemon"])
    def test_hides_feedback_for_other_actions(self, action):
        state = _make_state()
        state.action_dd.value = action
        handlers = EventHandlers(state)

        handlers.on_action_changed()

        assert state.feedback_tf.visible is False

    def test_shows_reset_step_only_for_reset(self):
        state = _make_state()
        state.action_dd.value = "Reset"
        handlers = EventHandlers(state)

        handlers.on_action_changed()

        assert state.reset_step_dd.visible is True

    def test_hides_reset_step_for_other_actions(self):
        state = _make_state()
        state.action_dd.value = "Submit"
        handlers = EventHandlers(state)

        handlers.on_action_changed()

        assert state.reset_step_dd.visible is False

    def test_shows_start_step_for_submit(self):
        state = _make_state()
        state.action_dd.value = "Submit"
        handlers = EventHandlers(state)

        handlers.on_action_changed()

        assert state.start_step_dd.visible is True

    def test_hides_start_step_for_non_submit(self):
        state = _make_state()
        state.action_dd.value = "Cancel"
        handlers = EventHandlers(state)

        handlers.on_action_changed()

        assert state.start_step_dd.visible is False


# ---------------------------------------------------------------------------
# on_active_run_selected
# ---------------------------------------------------------------------------

class TestOnActiveRunSelected:
    def test_updates_selected_run_id(self):
        state = _make_state()
        state.active_runs_dd.value = "run-uuid-123"
        handlers = EventHandlers(state)

        handlers.on_active_run_selected()

        assert state.selected_run_id == "run-uuid-123"

    def test_handles_none_value(self):
        state = _make_state()
        state.active_runs_dd.value = None
        handlers = EventHandlers(state)

        handlers.on_active_run_selected()

        assert state.selected_run_id == ""

    def test_handles_none_dropdown(self):
        state = _make_state(active_runs_dd=None)
        handlers = EventHandlers(state)
        handlers.on_active_run_selected()  # Should not raise


# ---------------------------------------------------------------------------
# refresh_active_runs
# ---------------------------------------------------------------------------

class TestRefreshActiveRuns:
    def test_returns_early_when_dropdown_none(self):
        state = _make_state(active_runs_dd=None)
        handlers = EventHandlers(state)
        handlers.refresh_active_runs()
        # No error

    def test_returns_early_when_no_service(self):
        state = _make_state()
        state.runner_service = None
        handlers = EventHandlers(state)
        handlers.refresh_active_runs()
        state.update.assert_not_called()

    def test_fetches_runs_from_service(self):
        service = MagicMock()
        runs = [_make_run("r1", "J1"), _make_run("r2", "J2")]
        service.list_active_runs_for_worker.return_value = runs
        state = _make_state()
        state.runner_service = service
        state.selected_worker_id = "worker-1"
        handlers = EventHandlers(state)

        handlers.refresh_active_runs()

        service.list_active_runs_for_worker.assert_called_once_with(worker_id="worker-1")
        assert state.active_runs == runs

    def test_populates_dropdown_options(self):
        service = MagicMock()
        runs = [_make_run("r1", "JOB-001", "wf_a", "running", "step1")]
        service.list_active_runs_for_worker.return_value = runs
        state = _make_state()
        state.runner_service = service
        handlers = EventHandlers(state)

        handlers.refresh_active_runs()

        assert len(state.active_runs_dd.options) == 1
        assert state.active_runs_dd.options[0].key == "r1"
        assert "JOB-001" in state.active_runs_dd.options[0].text
        assert "wf_a" in state.active_runs_dd.options[0].text

    def test_auto_selects_first_run(self):
        service = MagicMock()
        runs = [_make_run("r1"), _make_run("r2")]
        service.list_active_runs_for_worker.return_value = runs
        state = _make_state()
        state.runner_service = service
        handlers = EventHandlers(state)

        handlers.refresh_active_runs()

        assert state.selected_run_id == "r1"
        assert state.active_runs_dd.value == "r1"

    def test_clears_selection_when_no_runs(self):
        service = MagicMock()
        service.list_active_runs_for_worker.return_value = []
        state = _make_state()
        state.runner_service = service
        state.selected_run_id = "old-run"
        handlers = EventHandlers(state)

        handlers.refresh_active_runs()

        assert state.selected_run_id == ""
        assert state.active_runs == []

    def test_handles_service_exception_gracefully(self):
        service = MagicMock()
        service.list_active_runs_for_worker.side_effect = RuntimeError("Backend down")
        state = _make_state()
        state.runner_service = service
        handlers = EventHandlers(state)

        handlers.refresh_active_runs()

        assert state.active_runs == []
        assert len(state.active_runs_dd.options) == 0


# ---------------------------------------------------------------------------
# refresh_step_options
# ---------------------------------------------------------------------------

class TestRefreshStepOptions:
    def test_returns_early_when_widgets_none(self):
        state = _make_state(reset_step_dd=None, workflow_dd=None)
        handlers = EventHandlers(state)
        handlers.refresh_step_options()
        state.update.assert_not_called()

    def test_clears_when_no_workflow_selected(self):
        state = _make_state()
        state.workflow_dd.value = None
        state.selected_repo = MagicMock()
        handlers = EventHandlers(state)

        handlers.refresh_step_options()

        assert state.reset_step_dd.options == []
        assert state.reset_step_dd.value is None

    def test_clears_when_no_repo(self):
        state = _make_state()
        state.workflow_dd.value = "wf1"
        state.selected_repo = None
        handlers = EventHandlers(state)

        handlers.refresh_step_options()

        assert state.reset_step_dd.options == []


# ---------------------------------------------------------------------------
# _get_selected_run
# ---------------------------------------------------------------------------

class TestGetSelectedRun:
    def test_returns_none_when_dropdown_none(self):
        state = _make_state(active_runs_dd=None)
        handlers = EventHandlers(state)
        assert handlers._get_selected_run() is None

    def test_returns_none_when_no_value(self):
        state = _make_state()
        state.active_runs_dd.value = None
        handlers = EventHandlers(state)
        assert handlers._get_selected_run() is None

    def test_finds_run_by_id(self):
        run1 = _make_run("r1")
        run2 = _make_run("r2")
        state = _make_state()
        state.active_runs_dd.value = "r2"
        state.active_runs = [run1, run2]
        handlers = EventHandlers(state)

        assert handlers._get_selected_run() is run2

    def test_returns_none_when_not_found(self):
        state = _make_state()
        state.active_runs_dd.value = "nonexistent"
        state.active_runs = [_make_run("r1")]
        handlers = EventHandlers(state)

        assert handlers._get_selected_run() is None


# ---------------------------------------------------------------------------
# execute_action dispatch
# ---------------------------------------------------------------------------

class TestExecuteAction:
    @pytest.fixture
    def setup(self):
        state = _make_state()
        handlers = EventHandlers(state)
        service = MagicMock()
        callback = MagicMock()
        return handlers, state, service, callback

    def test_returns_early_when_action_dd_none(self, setup):
        handlers, state, service, callback = setup
        handlers.state.action_dd = None
        asyncio.run(handlers.execute_action(service, callback))
        callback.assert_not_called()

    def test_unknown_action_outputs_error(self, setup):
        handlers, state, service, callback = setup
        state.action_dd.value = "BogusAction"
        asyncio.run(handlers.execute_action(service, callback))
        callback.assert_called_once()
        assert "Unknown action" in callback.call_args[0][0]

    def test_submit_calls_execute_submit(self, setup):
        handlers, state, service, callback = setup
        state.action_dd.value = "Submit"
        state.selected_repo = None  # Will cause early return with error
        asyncio.run(handlers.execute_action(service, callback))
        callback.assert_called()
        assert "Error" in callback.call_args[0][0] or "Select" in callback.call_args[0][0]

    def test_cancel_requires_selected_run(self, setup):
        handlers, state, service, callback = setup
        state.action_dd.value = "Cancel"
        state.active_runs_dd.value = None
        asyncio.run(handlers.execute_action(service, callback))
        callback.assert_called()
        assert "Select" in callback.call_args[0][0] or "Error" in callback.call_args[0][0]


# ---------------------------------------------------------------------------
# _clear_dynamic_inputs
# ---------------------------------------------------------------------------

class TestClearDynamicInputs:
    def test_clears_input_fields(self):
        state = _make_state()
        state.input_fields = {"key1": MagicMock(), "key2": MagicMock()}
        handlers = EventHandlers(state)

        handlers._clear_dynamic_inputs()

        assert len(state.input_fields) == 0

    def test_clears_column_controls(self):
        state = _make_state()
        state.dynamic_inputs_column.controls = [MagicMock(), MagicMock()]
        handlers = EventHandlers(state)

        handlers._clear_dynamic_inputs()

        assert len(state.dynamic_inputs_column.controls) == 0

    def test_hides_container(self):
        state = _make_state()
        state.dynamic_inputs_container.visible = True
        handlers = EventHandlers(state)

        handlers._clear_dynamic_inputs()

        assert state.dynamic_inputs_container.visible is False

    def test_handles_none_column(self):
        state = _make_state()
        state.dynamic_inputs_column = None
        state.dynamic_inputs_container = None
        state.input_fields = {"key": MagicMock()}
        handlers = EventHandlers(state)

        handlers._clear_dynamic_inputs()

        assert len(state.input_fields) == 0


# ---------------------------------------------------------------------------
# _confirm_action
# ---------------------------------------------------------------------------

class TestConfirmAction:
    def test_returns_false_when_no_page(self):
        state = _make_state()
        state.page = None
        handlers = EventHandlers(state)
        result = asyncio.run(
            handlers._confirm_action("Submit", submit_details={"repo_name": "test"})
        )
        assert result is False

    def test_returns_false_when_no_details_or_run(self):
        state = _make_state()
        handlers = EventHandlers(state)
        result = asyncio.run(handlers._confirm_action("SomeAction"))
        assert result is False

    def test_returns_true_when_dialog_confirmed(self):
        state = _make_state()

        def fake_show_dialog(dialog):
            # Trigger the confirm button (second action = "Yes, ...")
            confirm_btn = dialog.actions[1]
            confirm_btn.on_click(None)

        state.page.show_dialog.side_effect = fake_show_dialog
        handlers = EventHandlers(state)

        result = asyncio.run(
            handlers._confirm_action("Submit", submit_details={"repo_name": "R"})
        )
        assert result is True

    def test_creates_dialog_with_run_info(self):
        state = _make_state()

        def fake_show_dialog(dialog):
            confirm_btn = dialog.actions[1]
            confirm_btn.on_click(None)

        state.page.show_dialog.side_effect = fake_show_dialog
        handlers = EventHandlers(state)

        run = _make_run("r1", "JOB-001", "my_wf", "running", "step_a")
        result = asyncio.run(handlers._confirm_action("Cancel", run=run))
        assert result is True
        state.page.show_dialog.assert_called_once()
