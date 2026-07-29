"""UI builders for the operator console.

This module extracts UI construction logic from app.py into
separate functions and classes, separating view construction
from event handling.
"""
from __future__ import annotations

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
        width=580,
        options=[
            ft.DropdownOption(key=w.worker_id, text=w.worker_id)
            for w in state.config.workers
        ],
        on_change=handlers.on_worker_id_changed,
    )
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
        width=580,
        disabled=True,
        on_change=handlers.on_repo_changed,
    )
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
        width=580,
        disabled=True,
        on_change=handlers.on_workflow_changed,
    )
    state.workflow_dd = dd
    return dd


def build_action_dropdown() -> ft.Dropdown:
    """Build action type dropdown.

    Returns:
        Configured dropdown widget.
    """
    return ft.Dropdown(
        label="Action",
        width=580,
        value="submit",
        options=[
            ft.DropdownOption(key="submit", text="Submit Job"),
            ft.DropdownOption(key="approval", text="Approve/Reject Step"),
            ft.DropdownOption(key="reset", text="Reset Step"),
            ft.DropdownOption(key="cancel", text="Cancel Job"),
        ],
    )


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


def build_main_layout(
    state: ConsoleState,
    handlers: EventHandlers,
) -> ft.Column:
    """Build main application layout.

    Constructs the complete UI structure with all dropdowns,
    inputs, and action buttons.

    Args:
        state: Console state.
        handlers: Event handlers.

    Returns:
        Root column containing all UI elements.
    """
    worker_dd = build_worker_dropdown(state, handlers)
    repo_dd = build_repo_dropdown(state, handlers)
    workflow_dd = build_workflow_dropdown(state, handlers)
    action_dd = build_action_dropdown()
    inputs_column, inputs_container = build_job_inputs_column(state)
    file_picker = build_file_picker(state)

    return ft.Column(
        [
            ft.Text("Agent Runner Console", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            file_picker,
            ft.Row([ft.Text("Worker:", width=100), worker_dd]),
            ft.Row([ft.Text("Repository:", width=100), repo_dd]),
            ft.Row([ft.Text("Workflow:", width=100), workflow_dd]),
            ft.Row([ft.Text("Action:", width=100), action_dd]),
            ft.Divider(),
            ft.Text("Job Inputs", weight=ft.FontWeight.BOLD),
            inputs_container,
            ft.Divider(),
            ft.ElevatedButton("Execute", on_click=lambda e: None),  # Placeholder
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
    )


class UIBuilder:
    """Extracted UI building logic.

    This class replaces nested UI construction code in app.py.
    It uses ConsoleState for widget references and EventHandlers
    for event binding.
    """

    def __init__(self, state: ConsoleState, handlers: EventHandlers):
        self.state = state
        self.handlers = handlers

    def build(self) -> ft.Column:
        """Build complete UI layout.

        Returns:
            Root column with all UI elements.
        """
        return build_main_layout(self.state, self.handlers)
