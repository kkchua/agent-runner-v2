"""Unit tests for operator_console builders module.

Tests that builder functions create correct widgets with proper event handlers
(on_select, not on_change), state references, and configuration.
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from agent_runner_v2.operator_console.builders import (
    build_action_dropdown,
    build_active_runs_section,
    build_execute_button,
    build_feedback_field,
    build_file_picker,
    build_job_inputs_column,
    build_main_layout,
    build_output_field,
    build_repo_dropdown,
    build_status_section,
    build_step_dropdowns,
    build_worker_dropdown,
    build_workflow_dropdown,
    UIBuilder,
)
from agent_runner_v2.operator_console.state import ConsoleState


@pytest.fixture
def mock_state():
    state = MagicMock(spec=ConsoleState)
    state.worker_id_dd = None
    state.repo_dd = None
    state.workflow_dd = None
    state.action_dd = None
    state.reset_step_dd = None
    state.start_step_dd = None
    state.active_runs_dd = None
    state.auto_refresh_cb = None
    state.file_picker = None
    state.status_text = None
    state.output = None
    state.feedback_tf = None
    state.dynamic_inputs_column = None
    state.dynamic_inputs_container = None
    state.all_worker_ids.return_value = ["worker-1", "worker-2"]
    return state


@pytest.fixture
def mock_handlers():
    return MagicMock()


class TestBuildWorkerDropdown:
    def test_creates_dropdown_with_worker_options(self, mock_state, mock_handlers):
        dd = build_worker_dropdown(mock_state, mock_handlers)
        assert dd is not None
        assert len(dd.options) == 2
        assert dd.options[0].key == "worker-1"
        assert dd.options[1].key == "worker-2"

    def test_stores_reference_in_state(self, mock_state, mock_handlers):
        dd = build_worker_dropdown(mock_state, mock_handlers)
        assert mock_state.worker_id_dd is dd

    def test_uses_on_select_not_on_change(self, mock_state, mock_handlers):
        dd = build_worker_dropdown(mock_state, mock_handlers)
        assert dd.on_select is not None
        assert callable(dd.on_select)

    def test_empty_workers_creates_empty_dropdown(self, mock_handlers):
        state = MagicMock(spec=ConsoleState)
        state.worker_id_dd = None
        state.all_worker_ids.return_value = []
        dd = build_worker_dropdown(state, mock_handlers)
        assert len(dd.options) == 0

    def test_on_select_triggers_handler(self, mock_state, mock_handlers):
        build_worker_dropdown(mock_state, mock_handlers)
        event = MagicMock()
        mock_state.worker_id_dd.on_select(event)
        mock_handlers.on_worker_id_changed.assert_called_once()


class TestBuildRepoDropdown:
    def test_creates_dropdown(self, mock_state, mock_handlers):
        dd = build_repo_dropdown(mock_state, mock_handlers)
        assert dd is not None
        assert dd.label == "Repository"

    def test_stores_reference_in_state(self, mock_state, mock_handlers):
        dd = build_repo_dropdown(mock_state, mock_handlers)
        assert mock_state.repo_dd is dd

    def test_uses_on_select_not_on_change(self, mock_state, mock_handlers):
        dd = build_repo_dropdown(mock_state, mock_handlers)
        assert dd.on_select is not None
        assert callable(dd.on_select)

    def test_initially_not_disabled(self, mock_state, mock_handlers):
        dd = build_repo_dropdown(mock_state, mock_handlers)
        assert dd.disabled is False

    def test_on_select_triggers_handler(self, mock_state, mock_handlers):
        build_repo_dropdown(mock_state, mock_handlers)
        event = MagicMock()
        mock_state.repo_dd.on_select(event)
        mock_handlers.on_repo_changed.assert_called_once()


class TestBuildWorkflowDropdown:
    def test_creates_dropdown(self, mock_state, mock_handlers):
        dd = build_workflow_dropdown(mock_state, mock_handlers)
        assert dd is not None
        assert dd.label == "Workflow"

    def test_stores_reference_in_state(self, mock_state, mock_handlers):
        dd = build_workflow_dropdown(mock_state, mock_handlers)
        assert mock_state.workflow_dd is dd

    def test_uses_on_select_not_on_change(self, mock_state, mock_handlers):
        dd = build_workflow_dropdown(mock_state, mock_handlers)
        assert dd.on_select is not None
        assert callable(dd.on_select)

    def test_on_select_triggers_handler(self, mock_state, mock_handlers):
        build_workflow_dropdown(mock_state, mock_handlers)
        event = MagicMock()
        mock_state.workflow_dd.on_select(event)
        mock_handlers.on_workflow_changed.assert_called_once()


class TestBuildActionDropdown:
    def test_has_all_8_actions(self, mock_state, mock_handlers):
        dd = build_action_dropdown(mock_state, mock_handlers)
        action_keys = [opt.key for opt in dd.options]
        assert action_keys == [
            "Submit", "Approve", "Reject", "Resume",
            "Retry", "Reset", "Cancel", "Quit Daemon",
        ]

    def test_default_value_is_submit(self, mock_state, mock_handlers):
        dd = build_action_dropdown(mock_state, mock_handlers)
        assert dd.value == "Submit"

    def test_stores_reference_in_state(self, mock_state, mock_handlers):
        dd = build_action_dropdown(mock_state, mock_handlers)
        assert mock_state.action_dd is dd

    def test_uses_on_select_not_on_change(self, mock_state, mock_handlers):
        dd = build_action_dropdown(mock_state, mock_handlers)
        assert dd.on_select is not None
        assert callable(dd.on_select)

    def test_on_select_triggers_handler(self, mock_state, mock_handlers):
        build_action_dropdown(mock_state, mock_handlers)
        event = MagicMock()
        mock_state.action_dd.on_select(event)
        mock_handlers.on_action_changed.assert_called_once()


class TestBuildActiveRunsSection:
    def test_creates_dropdown_container_checkbox(self, mock_state, mock_handlers):
        runs_dd, container, auto_cb = build_active_runs_section(mock_state, mock_handlers)
        assert runs_dd is not None
        assert container is not None
        assert auto_cb is not None

    def test_stores_references_in_state(self, mock_state, mock_handlers):
        runs_dd, _, auto_cb = build_active_runs_section(mock_state, mock_handlers)
        assert mock_state.active_runs_dd is runs_dd
        assert mock_state.auto_refresh_cb is auto_cb

    def test_runs_dropdown_has_on_select(self, mock_state, mock_handlers):
        runs_dd, _, _ = build_active_runs_section(mock_state, mock_handlers)
        assert runs_dd.on_select is not None
        assert callable(runs_dd.on_select)

    def test_on_select_triggers_handler(self, mock_state, mock_handlers):
        runs_dd, _, _ = build_active_runs_section(mock_state, mock_handlers)
        event = MagicMock()
        runs_dd.on_select(event)
        mock_handlers.on_active_run_selected.assert_called_once()

    def test_auto_refresh_default_off(self, mock_state, mock_handlers):
        _, _, auto_cb = build_active_runs_section(mock_state, mock_handlers)
        assert auto_cb.value is False


class TestBuildJobInputsColumn:
    def test_creates_column_and_container(self, mock_state):
        column, container = build_job_inputs_column(mock_state)
        assert column is not None
        assert container is not None

    def test_container_initially_hidden(self, mock_state):
        _, container = build_job_inputs_column(mock_state)
        assert container.visible is False

    def test_stores_references_in_state(self, mock_state):
        column, container = build_job_inputs_column(mock_state)
        assert mock_state.dynamic_inputs_column is column
        assert mock_state.dynamic_inputs_container is container


class TestBuildFilePicker:
    def test_creates_picker_and_stores_in_state(self, mock_state):
        picker = build_file_picker(mock_state)
        assert picker is not None
        assert mock_state.file_picker is picker


class TestBuildStatusSection:
    def test_creates_status_text(self, mock_state):
        status = build_status_section(mock_state)
        assert status.value == "Ready"
        assert mock_state.status_text is status


class TestBuildOutputField:
    def test_creates_readonly_multiline_field(self, mock_state):
        output = build_output_field(mock_state)
        assert output.label == "Output"
        assert output.multiline is True
        assert output.read_only is True
        assert output.min_lines == 14
        assert output.max_lines == 20
        assert mock_state.output is output


class TestBuildFeedbackField:
    def test_creates_hidden_field(self, mock_state):
        feedback = build_feedback_field(mock_state)
        assert feedback.label == "Feedback / Reason"
        assert feedback.multiline is True
        assert feedback.visible is False
        assert mock_state.feedback_tf is feedback


class TestBuildStepDropdowns:
    def test_creates_both_dropdowns(self, mock_state):
        reset_dd, start_dd = build_step_dropdowns(mock_state)
        assert reset_dd is not None
        assert start_dd is not None

    def test_reset_step_starts_hidden(self, mock_state):
        reset_dd, _ = build_step_dropdowns(mock_state)
        assert reset_dd.visible is False

    def test_start_step_starts_visible(self, mock_state):
        _, start_dd = build_step_dropdowns(mock_state)
        assert start_dd.visible is True

    def test_stores_references_in_state(self, mock_state):
        reset_dd, start_dd = build_step_dropdowns(mock_state)
        assert mock_state.reset_step_dd is reset_dd
        assert mock_state.start_step_dd is start_dd


class TestBuildExecuteButton:
    def test_creates_button_with_handler(self, mock_state):
        callback = MagicMock()
        btn = build_execute_button(mock_state, callback)
        assert btn is not None
        assert btn.content == "Run Action"
        assert btn.on_click is callback


class TestBuildMainLayout:
    def test_returns_column(self, mock_state, mock_handlers):
        import flet as ft
        callback = MagicMock()
        layout = build_main_layout(mock_state, mock_handlers, callback)
        assert isinstance(layout, ft.Column)

    def test_all_dropdowns_built(self, mock_state, mock_handlers):
        callback = MagicMock()
        build_main_layout(mock_state, mock_handlers, callback)
        assert mock_state.worker_id_dd is not None
        assert mock_state.repo_dd is not None
        assert mock_state.workflow_dd is not None
        assert mock_state.action_dd is not None
        assert mock_state.active_runs_dd is not None

    def test_all_use_on_select(self, mock_state, mock_handlers):
        callback = MagicMock()
        build_main_layout(mock_state, mock_handlers, callback)
        assert mock_state.worker_id_dd.on_select is not None
        assert mock_state.repo_dd.on_select is not None
        assert mock_state.workflow_dd.on_select is not None
        assert mock_state.action_dd.on_select is not None


class TestUIBuilder:
    def test_init_stores_args(self):
        mock_state = MagicMock()
        mock_handlers = MagicMock()
        mock_callback = MagicMock()
        builder = UIBuilder(mock_state, mock_handlers, mock_callback)
        assert builder.state is mock_state
        assert builder.handlers is mock_handlers
        assert builder.on_execute is mock_callback

    def test_build_returns_layout(self):
        mock_state = MagicMock(spec=ConsoleState)
        mock_state.worker_id_dd = None
        mock_state.repo_dd = None
        mock_state.workflow_dd = None
        mock_state.action_dd = None
        mock_state.reset_step_dd = None
        mock_state.start_step_dd = None
        mock_state.active_runs_dd = None
        mock_state.auto_refresh_cb = None
        mock_state.file_picker = None
        mock_state.status_text = None
        mock_state.output = None
        mock_state.feedback_tf = None
        mock_state.dynamic_inputs_column = None
        mock_state.dynamic_inputs_container = None
        mock_state.all_worker_ids.return_value = []
        mock_handlers = MagicMock()
        mock_callback = MagicMock()
        builder = UIBuilder(mock_state, mock_handlers, mock_callback)
        result = builder.build()
        assert result is not None
