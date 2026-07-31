"""Console state management for the operator console.

This module provides a centralized state container that replaces the
closure-based state management in app.py. All mutable state is explicitly
declared in the ConsoleState class, making data flow clearer and
testing easier.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import flet as ft

from .config import ConsoleConfig
from .models import RepoEntry, WorkflowEntry

_log = logging.getLogger(__name__)


@dataclass
class ConsoleState:
    """Holds all mutable console state, replacing closure variables.

    This class centralizes all state that was previously captured in
    closures within the app() function. It provides explicit attribute
    access and makes dependencies clear.

    Attributes:
        page: The Flet page instance for UI updates.
        config: The loaded console configuration.
        selected_worker_id: Currently selected worker ID.
        selected_repo: Currently selected repository entry.
        selected_workflow: Currently selected workflow entry.
        selected_run_id: Currently selected active run ID.
        active_runs: List of currently active runs.
        input_fields: Map of artifact key to text field widget.
        file_picker: Shared file picker instance for file inputs.
        worker_id_dd: Worker ID dropdown widget.
        repo_dd: Repository dropdown widget.
        workflow_dd: Workflow dropdown widget.
        action_dd: Action dropdown widget.
        reset_step_dd: Reset step dropdown widget.
        start_step_dd: Start step dropdown widget.
        active_runs_dd: Active runs dropdown widget.
        dynamic_inputs_column: Column containing dynamic input fields.
        dynamic_inputs_container: Container for dynamic inputs section.
        feedback_tf: Feedback/reason text field.
        status_text: Status display text.
        output: Output text field.
        auto_refresh_cb: Auto-refresh checkbox.
    """

    page: ft.Page
    config: ConsoleConfig

    # Selection state
    selected_worker_id: str = ""
    selected_repo: RepoEntry | None = None
    selected_workflow: WorkflowEntry | None = None
    selected_run_id: str = ""

    # Runtime state
    active_runs: list[Any] = field(default_factory=list)

    # Input state
    input_fields: dict[str, ft.TextField] = field(default_factory=dict)

    # Service reference (set after construction, used by refresh handlers)
    runner_service: Any = None

    # Widget references (initialized after UI construction)
    file_picker: ft.FilePicker | None = None
    worker_id_dd: ft.Dropdown | None = None
    repo_dd: ft.Dropdown | None = None
    workflow_dd: ft.Dropdown | None = None
    action_dd: ft.Dropdown | None = None
    reset_step_dd: ft.Dropdown | None = None
    start_step_dd: ft.Dropdown | None = None
    active_runs_dd: ft.Dropdown | None = None
    dynamic_inputs_column: ft.Column | None = None
    dynamic_inputs_container: ft.Container | None = None
    feedback_tf: ft.TextField | None = None
    status_text: ft.Text | None = None
    output: ft.TextField | None = None
    auto_refresh_cb: ft.Checkbox | None = None

    def update(self) -> None:
        """Trigger page update if page is available."""
        if self.page:
            self.page.update()

    def show_error(self, message: str) -> None:
        """Display a modal error dialog.

        Args:
            message: Error message to display.
        """
        _log = logging.getLogger(__name__)
        _log.error(message)

        def close_dialog(e: ft.ControlEvent | None = None) -> None:
            self.page.pop_dialog()

        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Console Error"),
                content=ft.Text(message),
                actions=[ft.TextButton("Close", on_click=close_dialog)],
            )
        )

    def all_worker_ids(self) -> list[str]:
        """Return unique worker IDs from all repos.

        Returns:
            Sorted list of unique worker IDs.
        """
        return sorted({r.worker_id for r in self.config.repos if r.worker_id})

    def repos_for_worker(self, worker_id: str) -> list[RepoEntry]:
        """Return repos matching the given worker_id.

        Args:
            worker_id: Worker ID to filter by.

        Returns:
            List of matching repository entries.
        """
        return [r for r in self.config.repos if r.worker_id == worker_id]

    def selected_repo_path(self) -> str:
        """Return the filesystem path of the selected repository.

        Returns:
            Repository path string.

        Raises:
            ActionExecutionError: If no repo is selected.
        """
        from .services.runner_service import ActionExecutionError

        if self.selected_repo is None:
            raise ActionExecutionError("Select a repo.")
        return self.selected_repo.path

    def find_workflow(self, workflow_name: str) -> tuple[str, WorkflowEntry | None]:
        """Find repo path and WorkflowEntry by workflow name.

        Scans all configured repos to find the first match.

        Args:
            workflow_name: The workflow name to find.

        Returns:
            Tuple of (repo_path, WorkflowEntry or None).
        """
        for repo in self.config.repos:
            for wf in repo.workflows:
                if wf.workflow_name == workflow_name:
                    return repo.path, wf
        return "", None

    def create_workflow_options(self) -> list[ft.DropdownOption]:
        """Build dropdown options for workflows in selected repo.

        Order matches the config file — user controls sort order there.

        Returns:
            List of dropdown options.
        """
        if self.selected_repo is None:
            return []
        return [
            ft.DropdownOption(key=w.name, text=w.name)
            for w in self.selected_repo.workflows
        ]
