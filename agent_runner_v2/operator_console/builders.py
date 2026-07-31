"""UI builders for the operator console.

This module extracts UI construction logic from app.py into
separate functions and classes, separating view construction
from event handling.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from .handlers import EventHandlers
    from .models import RepoEntry
    from .state import ConsoleState


def build_worker_dropdown(
    state: ConsoleState,
    handlers: EventHandlers,
) -> ft.Dropdown:
    """Build worker ID dropdown with event handler.

    Args:
        state: Console state.
        handlers: Event handlers.

    Returns:
        Configured dropdown widget.
    """
    dd = ft.Dropdown(
        label="Worker ID",
        width=250,
        options=[
            ft.DropdownOption(key=wid, text=wid)
            for wid in state.all_worker_ids()
        ],
    )
    dd.on_select = lambda e: handlers.on_worker_id_changed(e)
    state.worker_id_dd = dd
    return dd


def build_repo_dropdown(
    state: ConsoleState,
    handlers: EventHandlers,
) -> ft.Dropdown:
    """Build repository dropdown with event handler.

    Args:
        state: Console state.
        handlers: Event handlers.

    Returns:
        Configured dropdown widget.
    """
    dd = ft.Dropdown(
        label="Repository",
        width=250,
        disabled=False,
    )
    dd.on_select = lambda e: handlers.on_repo_changed(e)
    state.repo_dd = dd
    return dd


def build_workflow_dropdown(
    state: ConsoleState,
    handlers: EventHandlers,
) -> ft.Dropdown:
    """Build workflow dropdown with event handler.

    Args:
        state: Console state.
        handlers: Event handlers.

    Returns:
        Configured dropdown widget.
    """
    dd = ft.Dropdown(
        label="Workflow",
        width=250,
        disabled=False,
    )
    dd.on_select = lambda e: handlers.on_workflow_changed(e)
    state.workflow_dd = dd
    return dd


def build_action_dropdown(
    state: ConsoleState,
    handlers: EventHandlers,
) -> ft.Dropdown:
    """Build action type dropdown.

    Args:
        state: Console state.
        handlers: Event handlers.

    Returns:
        Configured dropdown widget.
    """
    dd = ft.Dropdown(
        label="Action",
        width=250,
        value="Submit",
        options=[
            ft.DropdownOption(key="Submit", text="Submit"),
            ft.DropdownOption(key="Approve", text="Approve"),
            ft.DropdownOption(key="Reject", text="Reject"),
            ft.DropdownOption(key="Resume", text="Resume"),
            ft.DropdownOption(key="Retry", text="Retry"),
            ft.DropdownOption(key="Reset", text="Reset"),
            ft.DropdownOption(key="Cancel", text="Cancel"),
            ft.DropdownOption(key="Quit Daemon", text="Quit Daemon"),
        ],
    )
    dd.on_select = lambda e: handlers.on_action_changed(e)
    state.action_dd = dd
    return dd


def build_job_inputs_column(
    state: ConsoleState,
) -> tuple[ft.Column, ft.Container]:
    """Build dynamic inputs column and container.

    Args:
        state: Console state.

    Returns:
        Tuple of (column, container) widgets.
    """
    column = ft.Column(spacing=8)
    container = ft.Container(
        content=column,
        border=ft.Border.all(width=1, color=ft.Colors.OUTLINE_VARIANT),
        border_radius=8,
        padding=12,
        visible=False,
    )
    state.dynamic_inputs_column = column
    state.dynamic_inputs_container = container
    return column, container


def build_file_picker(state: ConsoleState) -> ft.FilePicker:
    """Build shared file picker.

    Args:
        state: Console state.

    Returns:
        File picker widget.
    """
    picker = ft.FilePicker()
    state.file_picker = picker
    return picker


def build_status_section(state: ConsoleState) -> ft.Text:
    """Build status text display.

    Args:
        state: Console state.

    Returns:
        Status text widget.
    """
    status = ft.Text(value="Ready")
    state.status_text = status
    return status


def build_output_field(state: ConsoleState) -> ft.TextField:
    """Build output text field.

    Args:
        state: Console state.

    Returns:
        Output text field widget.
    """
    output = ft.TextField(
        label="Output",
        multiline=True,
        min_lines=14,
        max_lines=20,
        read_only=True,
        expand=True,
    )
    state.output = output
    return output


def build_feedback_field(state: ConsoleState) -> ft.TextField:
    """Build feedback/reason text field.

    Args:
        state: Console state.

    Returns:
        Feedback text field widget.
    """
    feedback = ft.TextField(
        label="Feedback / Reason",
        multiline=True,
        min_lines=2,
        max_lines=4,
        visible=False,
    )
    state.feedback_tf = feedback
    return feedback


def build_step_dropdowns(state: ConsoleState) -> tuple[ft.Dropdown, ft.Dropdown]:
    """Build reset step and start step dropdowns.

    Args:
        state: Console state.

    Returns:
        Tuple of (reset_step_dd, start_step_dd).
    """
    reset_dd = ft.Dropdown(
        label="Reset Target Step",
        width=250,
        visible=False,
    )
    start_dd = ft.Dropdown(
        label="Start Step (optional)",
        width=250,
        visible=True,
        hint_text="Leave empty to start from beginning",
    )
    state.reset_step_dd = reset_dd
    state.start_step_dd = start_dd
    return reset_dd, start_dd


def build_active_runs_section(
    state: ConsoleState,
    handlers: EventHandlers,
) -> tuple[ft.Dropdown, ft.Container, ft.Checkbox]:
    """Build active runs dropdown with refresh button and auto-refresh checkbox.

    Args:
        state: Console state.
        handlers: Event handlers.

    Returns:
        Tuple of (active_runs_dd, container, auto_refresh_cb).
    """
    runs_dd = ft.Dropdown(label="Active Runs", options=[], width=1000)
    runs_dd.on_select = lambda e: handlers.on_active_run_selected(e)

    container = ft.Container(
        content=runs_dd,
        border_radius=8,
        padding=12,
        width=1020,
    )

    refresh_btn = ft.ElevatedButton(
        "Refresh Active Runs",
        on_click=handlers.refresh_active_runs,
    )

    auto_cb = ft.Checkbox(
        label="Auto-refresh every 5s",
        value=False,
        on_change=handlers.on_auto_refresh_changed,
    )

    state.active_runs_dd = runs_dd
    state.auto_refresh_cb = auto_cb

    return runs_dd, container, auto_cb


def build_execute_button(
    state: ConsoleState,
    on_click: Callable[[ft.ControlEvent], None],
) -> ft.ElevatedButton:
    """Build execute action button.

    Args:
        state: Console state.
        on_click: Click handler for the button.

    Returns:
        Execute button widget.
    """
    return ft.ElevatedButton(
        "Run Action",
        on_click=on_click,
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(text_style=ft.TextStyle(weight=ft.FontWeight.BOLD)),
    )


def build_main_layout(
    state: ConsoleState,
    handlers: EventHandlers,
    on_execute: Callable[[ft.ControlEvent], None],
) -> ft.Column:
    """Build main application layout.

    Compact layout matching the original UI: Execute button on same row
    as dropdowns, Active Runs immediately below — no scrolling needed
    for core operations.

    Args:
        state: Console state.
        handlers: Event handlers.
        on_execute: Execute button click handler.

    Returns:
        Root column containing all UI elements.
    """
    worker_dd = build_worker_dropdown(state, handlers)
    repo_dd = build_repo_dropdown(state, handlers)
    workflow_dd = build_workflow_dropdown(state, handlers)
    action_dd = build_action_dropdown(state, handlers)
    inputs_column, inputs_container = build_job_inputs_column(state)
    file_picker = build_file_picker(state)
    status_text = build_status_section(state)
    output_field = build_output_field(state)
    feedback_field = build_feedback_field(state)
    reset_step_dd, start_step_dd = build_step_dropdowns(state)
    runs_dd, runs_container, auto_cb = build_active_runs_section(state, handlers)
    execute_btn = build_execute_button(state, on_execute)

    refresh_btn = ft.ElevatedButton("Refresh Active Runs", on_click=handlers.refresh_active_runs)

    return ft.Column(
        [
            ft.Text("Agent Runner Operator Console", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row(
                controls=[worker_dd, repo_dd, workflow_dd, action_dd],
                wrap=True, spacing=12, run_spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
            ft.Row(
                controls=[execute_btn],
                alignment=ft.MainAxisAlignment.END,
            ),
            status_text,
            ft.Row(
                controls=[runs_container, ft.Column([refresh_btn, auto_cb])],
                wrap=True, spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            reset_step_dd,
            start_step_dd,
            feedback_field,
            inputs_container,
            output_field,
        ],
        spacing=8,
    )


class UIBuilder:
    """Extracted UI building logic.

    This class replaces nested UI construction code in app.py.
    It uses ConsoleState for widget references and EventHandlers
    for event binding.
    """

    def __init__(
        self,
        state: ConsoleState,
        handlers: EventHandlers,
        on_execute: Callable[[ft.ControlEvent], None],
    ):
        self.state = state
        self.handlers = handlers
        self.on_execute = on_execute

    def build(self) -> ft.Column:
        """Build complete UI layout.

        Returns:
            Root column with all UI elements.
        """
        return build_main_layout(self.state, self.handlers, self.on_execute)
