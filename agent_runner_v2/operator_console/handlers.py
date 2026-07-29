"""Event handlers for the operator console.

This module extracts event handler functions from app.py's closures
into standalone methods. Handlers operate on ConsoleState and are
explicitly bound to UI events.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import flet as ft

from ..runtime_context import get_workflow_root
from ..workflow_packages.hooks import get_extension
from ..workflow_packages.loader import load_workflow_package
from .models import WorkflowEntry

if TYPE_CHECKING:
    from .state import ConsoleState

_log = logging.getLogger(__name__)

# SDLC artifact key → delivery subdirectory (relative to repo root)
SDLC_INPUT_DIRS: dict[str, str] = {
    "DRAFT_INIT_FILE": "docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives",
    "INIT_FILE": "docs/repo/agent_runner/sdlc/delivery/00_initiatives",
    "REQ_FILE": "docs/repo/agent_runner/sdlc/delivery/10_requirements",
    "PLAN_FILE": "docs/repo/agent_runner/sdlc/delivery/20_plans",
    "BACKLOG_FILE": "docs/repo/agent_runner/sdlc/delivery/30_backlogs",
    "TASK_FILE": "docs/repo/agent_runner/sdlc/delivery/40_tasks",
    "IMPL_FILE": "docs/repo/agent_runner/sdlc/delivery/50_implementations",
    "EXEC_FILE": "docs/repo/agent_runner/sdlc/delivery/60_executions",
    "VAL_FILE": "docs/repo/agent_runner/sdlc/delivery/70_validations",
    "WORKFLOW_SPEC": ".",
}

# All artifact keys that should show a file picker
KNOWN_FILE_INPUTS: frozenset[str] = frozenset(SDLC_INPUT_DIRS.keys())


def _get_input_dir_for_key(key: str, workflow_name: str) -> str | None:
    """Resolve the input subdirectory for *key* from workflow extensions.

    Calls ``register_artifact_keys()`` on the workflow's ``WorkflowExtensions``
    subclass and extracts the directory portion of the registered path.
    Falls back to the hardcoded ``SDLC_INPUT_DIRS`` when extension is
    unavailable.

    Args:
        key: The artifact key to resolve.
        workflow_name: The workflow name to get extension for.

    Returns:
        Directory path relative to repo root, or None if unknown.
    """
    ext = get_extension(workflow_name)
    if ext is not None:
        try:
            paths = ext.register_artifact_keys()
            if key in paths:
                rel_path = paths[key]
                if "/" in rel_path:
                    return rel_path.rsplit("/", 1)[0]
                return "."
        except Exception:
            _log.debug("register_artifact_keys() failed for %s", workflow_name, exc_info=True)
    return SDLC_INPUT_DIRS.get(key)


def _is_cross_os(os_type: str) -> bool:
    """Return True when *os_type* indicates different OS from console.

    Args:
        os_type: Repository OS type ("windows" or "linux").

    Returns:
        True if repository is on different OS than console.
    """
    import sys

    if not os_type:
        return False
    repo_is_windows = os_type.lower() == "windows"
    console_is_windows = sys.platform == "win32"
    return repo_is_windows != console_is_windows


def _resolve_file_picker_root(
    repo_path: str,
    input_dir: str | None,
    os_type: str,
) -> str:
    """Determine file picker root directory.

    Extracted from deeply nested if/elif/else in original on_browse_click.

    Args:
        repo_path: Path to repository.
        input_dir: Input directory relative to repo.
        os_type: Repository OS type.

    Returns:
        Absolute path to use as file picker root.
    """
    if _is_cross_os(os_type):
        return str(Path.home())

    if input_dir and input_dir != ".":
        resolved = Path(repo_path) / input_dir
        if resolved.is_dir():
            return str(resolved)

    return repo_path


class EventHandlers:
    """Extracted event handlers as class methods.

    This class replaces the nested closure functions in app.py.
    Each method operates on self.state and is bound to UI events.
    """

    def __init__(self, state: ConsoleState):
        self.state = state

    # ==================================================================
    # File Picker Handler
    # ==================================================================

    async def on_browse_click(
        self,
        e: ft.ControlEvent,
        *,
        key: str,
        field: ft.TextField,
        input_dir: str | None,
    ) -> None:
        """Handle file browse button click.

        Opens file picker rooted at the appropriate directory based on
        repository OS type and input key configuration.

        Args:
            e: Control event.
            key: Artifact key being browsed for.
            field: Text field to update with selected filename.
            input_dir: Input directory relative to repo root.
        """
        if self.state.file_picker is None:
            return

        try:
            repo_path = self.state.selected_repo_path()
            repo = self.state.selected_repo
            os_type = repo.os_type if repo else ""

            root = _resolve_file_picker_root(repo_path, input_dir, os_type)
            self.state.file_picker.root_directory = root

            files = await self.state.file_picker.pick_files(
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["md"],
            )

            if files and field:
                picked = files[0]
                field.value = str(Path(picked.path).name) if picked.path else picked.name
                self.state.update()
        except Exception as err:
            self.state.show_error(f"File browse failed: {err}")

    # ==================================================================
    # Selection Change Handlers
    # ==================================================================

    def on_worker_id_changed(self, _event: ft.ControlEvent | None = None) -> None:
        """Handle worker ID dropdown change.

        Updates repo dropdown to show only repos for selected worker.
        """
        if self.state.worker_id_dd is None or self.state.repo_dd is None:
            return

        self.state.selected_worker_id = self.state.worker_id_dd.value or ""
        repos = self.state.repos_for_worker(self.state.selected_worker_id)

        self.state.repo_dd.options = [
            ft.DropdownOption(key=r.name, text=r.name) for r in repos
        ]
        self.state.repo_dd.value = None
        self.state.repo_dd.disabled = not repos

        # Clear workflow selection
        if self.state.workflow_dd:
            self.state.workflow_dd.options = []
            self.state.workflow_dd.value = None
            self.state.workflow_dd.disabled = True

        self._clear_dynamic_inputs()
        self.state.update()

    def on_repo_changed(self, _event: ft.ControlEvent | None = None) -> None:
        """Handle repository dropdown change.

        Updates selected_repo and populates workflow dropdown.
        """
        if self.state.repo_dd is None or self.state.workflow_dd is None:
            return

        repo_name = self.state.repo_dd.value
        self.state.selected_repo = next(
            (r for r in self.state.config.repos if r.name == repo_name), None
        )

        # Update workflow dropdown
        self.state.workflow_dd.options = self.state.create_workflow_options()
        self.state.workflow_dd.value = None
        self.state.workflow_dd.disabled = self.state.selected_repo is None

        self._clear_dynamic_inputs()
        self.state.update()

    def on_workflow_changed(self, _event: ft.ControlEvent | None = None) -> None:
        """Handle workflow dropdown change.

        Updates selected_workflow and builds dynamic inputs.
        """
        if self.state.workflow_dd is None:
            return

        workflow_name = self.state.workflow_dd.value
        if not workflow_name or not self.state.selected_repo:
            self.state.selected_workflow = None
            self._clear_dynamic_inputs()
            self.state.update()
            return

        self.state.selected_workflow = next(
            (w for w in self.state.selected_repo.workflows if w.name == workflow_name),
            None,
        )

        if self.state.selected_workflow:
            self._build_dynamic_inputs(self.state.selected_workflow)
        else:
            self._clear_dynamic_inputs()

        self.state.update()

    # ==================================================================
    # Helper Methods
    # ==================================================================

    def _clear_dynamic_inputs(self) -> None:
        """Clear dynamic input fields and hide container."""
        self.state.input_fields.clear()
        if self.state.dynamic_inputs_column:
            self.state.dynamic_inputs_column.controls.clear()
        if self.state.dynamic_inputs_container:
            self.state.dynamic_inputs_container.visible = False

    def _build_dynamic_inputs(self, workflow: WorkflowEntry) -> None:
        """Build dynamic input controls for the selected workflow.

        Loads workflow bundle and creates input fields for required
        artifacts based on the workflow's init step configuration.

        Args:
            workflow: Selected workflow entry.
        """
        if self.state.dynamic_inputs_column is None:
            return

        self.state.input_fields.clear()
        self.state.dynamic_inputs_column.controls.clear()

        try:
            bundle = self._load_workflow_bundle(workflow)
            if bundle is None:
                self._show_bundle_error(workflow)
                return

            init_step_name = bundle.init_step or ""
            if not init_step_name or init_step_name not in bundle.steps:
                self._show_no_inputs_needed()
                return

            required = bundle.steps[init_step_name].required_inputs
            if not required:
                self._show_no_inputs_needed()
                return

            self._create_input_fields(required, workflow)

        except Exception as err:
            _log.error("Failed to build dynamic inputs: %s", err)
            self.state.show_error(f"Failed to load workflow: {err}")

    def _load_workflow_bundle(self, workflow: WorkflowEntry) -> Any:
        """Load workflow bundle from filesystem.

        Args:
            workflow: Workflow entry to load.

        Returns:
            Loaded workflow bundle or None.
        """
        try:
            workflow_root = get_workflow_root()
            pkg_dir = workflow_root / workflow.workflow_name
            if pkg_dir.exists():
                return load_workflow_package(pkg_dir)
        except Exception as err:
            _log.debug("Failed to load from workflow root: %s", err)

        # Fallback: load from repo
        if self.state.selected_repo:
            repo_workflows = Path(self.state.selected_repo.path) / "workflows"
            pkg_dir = repo_workflows / workflow.workflow_name
            if pkg_dir.exists():
                return load_workflow_package(pkg_dir)

        return None

    def _show_bundle_error(self, workflow: WorkflowEntry) -> None:
        """Display error when workflow bundle cannot be loaded."""
        self.state.dynamic_inputs_column.controls.append(
            ft.Text(
                f"Workflow '{workflow.workflow_name}' not found in local bundles or repo.",
                color="red",
            )
        )
        if self.state.dynamic_inputs_container:
            self.state.dynamic_inputs_container.visible = True

    def _show_no_inputs_needed(self) -> None:
        """Display message when no inputs are required."""
        self.state.dynamic_inputs_column.controls.append(
            ft.Text("No input artifacts required.", italic=True, color="grey")
        )
        if self.state.dynamic_inputs_container:
            self.state.dynamic_inputs_container.visible = True

    def _create_input_fields(
        self, required_inputs: list[str], workflow: WorkflowEntry
    ) -> None:
        """Create input field controls for required artifacts.

        Args:
            required_inputs: List of required artifact keys.
            workflow: Workflow entry for context.
        """
        for key in required_inputs:
            input_dir = _get_input_dir_for_key(key, workflow.workflow_name)
            is_file = (
                input_dir is not None
                or key in KNOWN_FILE_INPUTS
                or key.endswith("_FILE")
            )

            if is_file:
                self._create_file_input(key, input_dir)
            else:
                self._create_text_input(key)

        if self.state.dynamic_inputs_container:
            self.state.dynamic_inputs_container.visible = True

    def _create_file_input(self, key: str, input_dir: str | None) -> None:
        """Create file input field with browse button.

        Args:
            key: Artifact key.
            input_dir: Input directory relative to repo.
        """
        if self.state.dynamic_inputs_column is None:
            return

        text_field = ft.TextField(
            label=key,
            read_only=False,
            expand=True,
            hint_text=f"Filename or browse for {key}",
        )

        # Create bound handler with key-specific values
        async def on_click(e: ft.ControlEvent) -> None:
            await self.on_browse_click(e, key=key, field=text_field, input_dir=input_dir)

        browse_btn = ft.ElevatedButton("Browse", on_click=on_click)
        self.state.input_fields[key] = text_field

        self.state.dynamic_inputs_column.controls.append(
            ft.Column(
                [
                    ft.Text(key, weight=ft.FontWeight.BOLD, size=12),
                    ft.Row([text_field, browse_btn], spacing=8),
                ],
                spacing=4,
            )
        )

    def _create_text_input(self, key: str) -> None:
        """Create text input field for scalar value.

        Args:
            key: Artifact key.
        """
        if self.state.dynamic_inputs_column is None:
            return

        text_field = ft.TextField(
            label=key, expand=True, hint_text=f"Enter {key}"
        )
        self.state.input_fields[key] = text_field

        self.state.dynamic_inputs_column.controls.append(
            ft.Column(
                [
                    ft.Text(key, weight=ft.FontWeight.BOLD, size=12),
                    ft.Row([text_field], spacing=8),
                ],
                spacing=4,
            )
        )
