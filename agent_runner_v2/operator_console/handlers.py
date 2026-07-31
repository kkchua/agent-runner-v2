"""Event handlers for the operator console.

This module extracts event handler functions from app.py's closures
into standalone methods. Handlers operate on ConsoleState and are
explicitly bound to UI events.
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

import flet as ft

from ..runtime_context import get_workflow_root
from ..workflow_packages.hooks import get_extension
from ..workflow_packages.loader import load_workflow_package
from .models import ActiveRunSummary, WorkflowEntry

if TYPE_CHECKING:
    from .services.runner_service import RunnerActionService
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
        self.state.repo_dd.disabled = len(repos) == 0
        self.state.repo_dd.update()

        # Clear workflow selection
        if self.state.workflow_dd:
            self.state.workflow_dd.options = []
            self.state.workflow_dd.value = None
            self.state.workflow_dd.disabled = False
            self.state.workflow_dd.update()

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
        self.state.workflow_dd.disabled = False
        self.state.workflow_dd.update()

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

    # ==================================================================
    # Action Change Handler
    # ==================================================================

    def on_action_changed(self, _event: ft.ControlEvent | None = None) -> None:
        """Handle action dropdown change.

        Shows/hides UI sections based on selected action.
        """
        if self.state.action_dd is None:
            return

        action = self.state.action_dd.value or ""
        needs_active = action in {"Approve", "Reject", "Resume", "Retry", "Reset", "Cancel"}

        if self.state.feedback_tf:
            self.state.feedback_tf.visible = needs_active
        if self.state.reset_step_dd:
            self.state.reset_step_dd.visible = action == "Reset"
        if self.state.start_step_dd:
            self.state.start_step_dd.visible = action == "Submit"

        self.state.update()

    # ==================================================================
    # Refresh Handlers
    # ==================================================================

    def refresh_step_options(self, _event: ft.ControlEvent | None = None) -> None:
        """Populate step dropdown for Reset action.

        Loads workflow bundle and extracts step names.
        """
        if self.state.reset_step_dd is None or self.state.workflow_dd is None:
            return

        workflow_name = self.state.workflow_dd.value
        if not workflow_name or not self.state.selected_repo:
            self.state.reset_step_dd.options = []
            self.state.reset_step_dd.value = None
            self.state.update()
            return

        workflow = next(
            (w for w in self.state.selected_repo.workflows if w.name == workflow_name),
            None,
        )
        if not workflow:
            self.state.reset_step_dd.options = []
            self.state.reset_step_dd.value = None
            self.state.update()
            return

        try:
            bundle = self._load_workflow_bundle(workflow)
            if bundle:
                step_names = list(bundle.steps.keys())
                self.state.reset_step_dd.options = [
                    ft.DropdownOption(key=s, text=s) for s in step_names
                ]
            else:
                self.state.reset_step_dd.options = []
        except Exception as err:
            _log.error("Failed to load steps: %s", err)
            self.state.reset_step_dd.options = []

        self.state.reset_step_dd.value = None
        self.state.update()

    def refresh_active_runs(
        self, _event: ft.ControlEvent | None = None
    ) -> None:
        """Load active runs from backend and populate dropdown."""
        if self.state.active_runs_dd is None:
            return

        service = self.state.runner_service
        if service is None:
            return

        try:
            runs = service.list_active_runs_for_worker(
                worker_id=self.state.selected_worker_id,
            )
        except Exception as err:
            _log.error("Failed to fetch active runs: %s", err)
            runs = []

        self.state.active_runs = runs
        self.state.active_runs_dd.options = [
            ft.DropdownOption(
                key=run.run_id,
                text=f"{run.run_code} — {run.workflow_name} [{run.status}] ({run.current_step})",
            )
            for run in runs
        ]
        self.state.selected_run_id = runs[0].run_id if runs else ""
        self.state.active_runs_dd.value = self.state.selected_run_id
        self.state.active_runs_dd.update()

    def on_active_run_selected(self, _event: ft.ControlEvent | None = None) -> None:
        """Handle active run dropdown selection change."""
        if self.state.active_runs_dd is not None:
            self.state.selected_run_id = self.state.active_runs_dd.value or ""

    def on_auto_refresh_changed(
        self, e: ft.ControlEvent | None = None
    ) -> None:
        """Toggle auto-refresh when checkbox state changes."""
        if self.state.auto_refresh_cb and self.state.auto_refresh_cb.value:
            if self.state.page:
                self.state.page.run_task(self._auto_refresh_loop)

    async def _auto_refresh_loop(self) -> None:
        """Background task for auto-refreshing active runs every 5 seconds."""
        while True:
            await asyncio.sleep(5)
            if self.state.auto_refresh_cb is None or not self.state.auto_refresh_cb.value:
                break
            try:
                self.refresh_active_runs()
            except Exception:
                _log.exception("[console] auto-refresh error")

    # ==================================================================
    # Execute Action
    # ==================================================================

    async def execute_action(
        self,
        runner_service: RunnerActionService,
        output_callback: Callable[[str], None],
    ) -> None:
        """Dispatch the selected action to the appropriate service method.

        Args:
            runner_service: Service for invoking runner actions.
            output_callback: Callback to append output text.
        """
        if self.state.action_dd is None:
            return

        action = self.state.action_dd.value or ""

        try:
            if action == "Submit":
                await self._execute_submit(runner_service, output_callback)
            elif action == "Approve":
                await self._execute_approve(runner_service, output_callback)
            elif action == "Reject":
                await self._execute_reject(runner_service, output_callback)
            elif action == "Resume":
                await self._execute_resume(runner_service, output_callback)
            elif action == "Retry":
                await self._execute_retry(runner_service, output_callback)
            elif action == "Reset":
                await self._execute_reset(runner_service, output_callback)
            elif action == "Cancel":
                await self._execute_cancel(runner_service, output_callback)
            elif action == "Quit Daemon":
                await self._execute_quit_daemon(runner_service, output_callback)
            else:
                output_callback(f"Unknown action: {action}")
        except Exception as err:
            _log.exception("Action execution failed")
            output_callback(f"Error: {err}")

    async def _execute_submit(
        self,
        runner_service: RunnerActionService,
        output_callback: Callable[[str], None],
    ) -> None:
        """Execute Submit action."""
        repo = self.state.selected_repo
        workflow = self.state.selected_workflow
        if not repo or not workflow:
            output_callback("Error: Select a repo and workflow first.")
            return

        # Build input artifacts from input fields
        input_artifacts: dict[str, str] = {}
        for key, field in self.state.input_fields.items():
            if field.value:
                # Resolve relative paths: prepend input directory for file inputs
                input_dir = _get_input_dir_for_key(key, workflow.workflow_name)
                if input_dir and not Path(field.value).is_absolute():
                    input_artifacts[key] = str(Path(repo.path) / input_dir / field.value)
                else:
                    input_artifacts[key] = field.value

        # Show submit details in confirmation
        details = {
            "repo_name": repo.name,
            "workflow_name": workflow.workflow_name,
            "worker_id": self.state.selected_worker_id,
            "input_count": len(input_artifacts),
        }

        confirmed = await self._confirm_action(
            "Submit",
            submit_details=details,
        )
        if not confirmed:
            output_callback("Submit cancelled.")
            return

        output_callback(f"Submitting {workflow.workflow_name}...")

        result = runner_service.submit_job(
            repo_path=repo.path,
            workflow=workflow,
            input_artifacts=input_artifacts,
            worker_id=self.state.selected_worker_id or None,
            os_type=repo.os_type,
            start_step=self.state.start_step_dd.value if self.state.start_step_dd else "",
        )
        output_callback(result)

    async def _execute_approve(
        self,
        runner_service: RunnerActionService,
        output_callback: Callable[[str], None],
    ) -> None:
        """Execute Approve action."""
        await self._execute_step_action(
            "Approve", runner_service.approve_step, runner_service, output_callback
        )

    async def _execute_reject(
        self,
        runner_service: RunnerActionService,
        output_callback: Callable[[str], None],
    ) -> None:
        """Execute Reject action."""
        await self._execute_step_action(
            "Reject", runner_service.reject_step, runner_service, output_callback
        )

    async def _execute_resume(
        self,
        runner_service: RunnerActionService,
        output_callback: Callable[[str], None],
    ) -> None:
        """Execute Resume action."""
        await self._execute_step_action(
            "Resume", runner_service.resume_step, runner_service, output_callback
        )

    async def _execute_retry(
        self,
        runner_service: RunnerActionService,
        output_callback: Callable[[str], None],
    ) -> None:
        """Execute Retry action."""
        await self._execute_step_action(
            "Retry", runner_service.retry_step, runner_service, output_callback
        )

    async def _execute_step_action(
        self,
        action_name: str,
        action_func: Any,
        runner_service: RunnerActionService,
        output_callback: Callable[[str], None],
    ) -> None:
        """Execute a step-level action (Approve/Reject/Resume/Retry)."""
        run = self._get_selected_run()
        if not run:
            output_callback(f"Error: Select an active run to {action_name.lower()}.")
            return

        confirmed = await self._confirm_action(
            action_name,
            run=run,
        )
        if not confirmed:
            output_callback(f"{action_name} cancelled.")
            return

        output_callback(f"{action_name} run {run.run_code}...")

        result = action_func(
            repo_path=run.project_root,
            template_group=run.workflow_name,
            job_id=run.run_id,
            step_name=run.current_step,
        )
        output_callback(result)

    async def _execute_reset(
        self,
        runner_service: RunnerActionService,
        output_callback: Callable[[str], None],
    ) -> None:
        """Execute Reset action."""
        run = self._get_selected_run()
        if not run:
            output_callback("Error: Select an active run to reset.")
            return

        step_name = self.state.reset_step_dd.value if self.state.reset_step_dd else None
        if not step_name:
            output_callback("Error: Select a target step.")
            return

        confirmed = await self._confirm_action(
            "Reset",
            run=run,
        )
        if not confirmed:
            output_callback("Reset cancelled.")
            return

        output_callback(f"Resetting {run.run_code} to step {step_name}...")

        result = runner_service.reset_step(
            run_id=run.run_id,
            step_name=step_name,
        )
        output_callback(result)

    async def _execute_cancel(
        self,
        runner_service: RunnerActionService,
        output_callback: Callable[[str], None],
    ) -> None:
        """Execute Cancel action."""
        run = self._get_selected_run()
        if not run:
            output_callback("Error: Select an active run to cancel.")
            return

        confirmed = await self._confirm_action(
            "Cancel",
            run=run,
        )
        if not confirmed:
            output_callback("Cancel cancelled.")
            return

        output_callback(f"Cancelling run {run.run_code}...")

        result = runner_service.stop_run(
            run_id=run.run_id,
            reason=self.state.feedback_tf.value if self.state.feedback_tf else "",
        )
        output_callback(result)

    async def _execute_quit_daemon(
        self,
        runner_service: RunnerActionService,
        output_callback: Callable[[str], None],
    ) -> None:
        """Execute Quit Daemon action."""
        repo = self.state.selected_repo
        if not repo:
            output_callback("Error: Select a repo.")
            return

        confirmed = await self._confirm_action(
            "Quit Daemon",
            submit_details={"repo_name": repo.name, "message": "Request daemon shutdown"},
        )
        if not confirmed:
            output_callback("Quit Daemon cancelled.")
            return

        output_callback("Submitting quit daemon command...")

        result = runner_service.quit_daemon(
            repo_path=repo.path,
            worker_id=self.state.selected_worker_id,
            reason="Quit requested from operator console",
        )
        output_callback(result)

    def _get_selected_run(self) -> ActiveRunSummary | None:
        """Get the currently selected run from dropdown.

        Returns:
            Selected run summary or None.
        """
        run_id = self.state.active_runs_dd.value if self.state.active_runs_dd else None
        if not run_id:
            return None

        for run in self.state.active_runs:
            if run.run_id == run_id:
                return run
        return None

    # ==================================================================
    # Confirmation Dialog
    # ==================================================================

    async def _confirm_action(
        self,
        action: str,
        *,
        run: ActiveRunSummary | None = None,
        submit_details: dict[str, Any] | None = None,
    ) -> bool:
        """Show confirmation dialog for actions.

        Args:
            action: Action name to confirm.
            run: Run summary for existing run actions.
            submit_details: Details for submit action.

        Returns:
            True if user confirms, False otherwise.
        """
        result_container: dict[str, bool] = {"confirmed": False}

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Confirm {action}", weight=ft.FontWeight.BOLD),
            content=None,  # Set below based on action type
            actions=[],
        )

        def _on_confirm(e: ft.ControlEvent | None) -> None:
            result_container["confirmed"] = True
            dialog.open = False
            if self.state.page:
                self.state.page.pop_dialog()

        def _on_cancel(e: ft.ControlEvent | None) -> None:
            result_container["confirmed"] = False
            dialog.open = False
            if self.state.page:
                self.state.page.pop_dialog()

        # Build dialog content based on action type
        if action == "Submit" and submit_details:
            content = ft.Column([
                ft.Text("You are about to submit a new job:"),
                ft.Divider(),
                ft.Text(f"Repo: {submit_details.get('repo_name', 'N/A')}"),
                ft.Text(f"Workflow: {submit_details.get('workflow_name', 'N/A')}", weight=ft.FontWeight.BOLD),
                ft.Text(f"Worker: {submit_details.get('worker_id', 'N/A')}"),
                ft.Text(f"Input artifacts: {submit_details.get('input_count', 0)}"),
            ], tight=True, spacing=8)
        elif action == "Quit Daemon" and submit_details:
            content = ft.Column([
                ft.Text("You are about to quit the daemon:"),
                ft.Divider(),
                ft.Text(f"Repo: {submit_details.get('repo_name', 'N/A')}"),
                ft.Text("This will gracefully shut down the daemon after current work completes.", italic=True),
            ], tight=True, spacing=8)
        elif run:
            content = ft.Column([
                ft.Text(f"You are about to {action.lower()} the following run:"),
                ft.Divider(),
                ft.Text(f"Run Code: {run.run_code or 'N/A'}", weight=ft.FontWeight.BOLD),
                ft.Text(f"Workflow: {run.workflow_name}"),
                ft.Text(f"Status: {run.status}"),
                ft.Text(f"Current Step: {run.current_step or 'N/A'}"),
            ], tight=True, spacing=8)
        else:
            return False

        dialog.content = content
        dialog.actions = [
            ft.TextButton("No", on_click=_on_cancel),
            ft.ElevatedButton(
                f"Yes, {action}",
                on_click=_on_confirm,
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
            ),
        ]

        if self.state.page:
            dialog.open = True
            self.state.page.show_dialog(dialog)
            while dialog.open:
                await asyncio.sleep(0.05)

        return result_container["confirmed"]
