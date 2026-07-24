"""Operator Console — Flet-based desktop GUI for managing agent-runner-v2 workflows.

Provides a universal launcher that replaces per-workflow batch files.  The console
dynamically detects each workflow's input requirements from ``workflow.toml`` and
generates appropriate UI fields (file pickers for file artifacts, text fields for
scalar values).

Actions
-------
- **Submit** — queue a workflow run via the backend API.
- **Approve** — approve a step awaiting human review.
- **Reject** — reject a step awaiting human review, sending it back for refinement.
- **Reset** — override the current step of an active run.
- **Cancel** — stop an active run.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from ..backend_client import BackendClient
from .config import ConsoleConfigError, load_console_config, load_global_settings
from .models import ActiveRunSummary, RepoEntry, WorkflowEntry
from .services.backend_service import BackendRunService
from .services.runner_service import ActionExecutionError, RunnerActionService
from ..workflow_packages.loader import load_workflow_package
from ..runtime_context import get_workflow_root

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SDLC artifact key → delivery subdirectory (relative to repo root)
# ---------------------------------------------------------------------------
SDLC_INPUT_DIRS: dict[str, str] = {
    "DRAFT_INIT_FILE": "docs/repo/agent_runner/sdlc/delivery/00_draft_initiatives",
    "INIT_FILE":       "docs/repo/agent_runner/sdlc/delivery/00_initiatives",
    "REQ_FILE":        "docs/repo/agent_runner/sdlc/delivery/10_requirements",
    "PLAN_FILE":       "docs/repo/agent_runner/sdlc/delivery/20_plans",
    "BACKLOG_FILE":    "docs/repo/agent_runner/sdlc/delivery/30_backlogs",
    "TASK_FILE":       "docs/repo/agent_runner/sdlc/delivery/40_tasks",
    "IMPL_FILE":       "docs/repo/agent_runner/sdlc/delivery/50_implementations",
    "EXEC_FILE":       "docs/repo/agent_runner/sdlc/delivery/60_executions",
    "VAL_FILE":        "docs/repo/agent_runner/sdlc/delivery/70_validations",
}


# ===========================================================================
# CLI entry point
# ===========================================================================

def main(argv: list[str] | None = None) -> int:
    """Launch the desktop operator console.

    Parses CLI arguments, loads runner and console configuration, then starts
    the Flet application.

    Parameters
    ----------
    argv :
        Optional argument list (defaults to ``sys.argv[1:]``).

    Returns
    -------
    int
        Exit code: 0 on success, 2 on configuration error.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [console] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    parser = argparse.ArgumentParser(
        prog="ukbe-run-agent console",
        description="Launch the desktop operator console.",
    )
    parser.add_argument("--config", default="", help="Override operator console config path.")
    parser.add_argument("--web", action="store_true", help="Open console in web browser instead of desktop window.")
    args = parser.parse_args(argv)

    try:
        import flet as ft
    except ImportError:
        print(
            "Flet is not installed. Install console dependencies with: pip install -e \".[console]\"",
            file=sys.stderr,
        )
        return 2

    try:
        settings = load_global_settings()
        console_config = load_console_config(args.config or None)
    except ConsoleConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    backend_service = BackendRunService(
        BackendClient(settings.backend_url), worker_id=settings.worker_id,
    )
    runner_service = RunnerActionService(settings)

    # -----------------------------------------------------------------------
    # Flet application
    # -----------------------------------------------------------------------

    def app(page: ft.Page) -> None:
        """Build the operator console UI and wire all event handlers."""
        page.title = "Agent Runner Operator Console"
        page.window_width = 980
        page.window_height = 760
        page.scroll = ft.ScrollMode.AUTO
        page.padding = 20

        # -- Actions --------------------------------------------------------
        actions = ["Submit", "Approve", "Reject", "Reset", "Cancel"]

        # -- State ----------------------------------------------------------
        input_fields: dict[str, ft.TextField] = {}
        active_runs: list[ActiveRunSummary] = []
        selected_run_id: str = ""

        # -- Shared UI controls ---------------------------------------------
        output = ft.TextField(
            label="Output", multiline=True,
            min_lines=14, max_lines=20, read_only=True, expand=True,
        )
        status_text = ft.Text(
            value=f"Backend: {settings.backend_url} | Worker: {settings.worker_id}",
        )
        action_dd = ft.Dropdown(
            label="Action",
            options=[ft.dropdown.Option(a) for a in actions],
            value=actions[0],
        )
        repo_dd = ft.Dropdown(
            label="Repo", hint_text="Select a repository", width=280,
            options=[ft.DropdownOption(key=r.name, text=r.name) for r in console_config.repos],
            value=console_config.repos[0].name if console_config.repos else None,
            disabled=not bool(console_config.repos),
        )
        workflow_dd = ft.Dropdown(
            label="Workflow", hint_text="Select a workflow",
            width=400, options=[], value="", disabled=True,
        )
        active_runs_dd = ft.Dropdown(label="Active Runs", options=[], width=1000)
        active_runs_container = ft.Container(
            content=active_runs_dd, border_radius=8, padding=12, width=1020,
        )
        feedback_tf = ft.TextField(
            label="Feedback / Reason", multiline=True,
            min_lines=2, max_lines=4, visible=False,
        )
        reset_step_dd = ft.Dropdown(
            label="Reset Target Step", width=580, visible=False,
        )

        # Dynamic workflow-inputs panel
        dynamic_inputs_column = ft.Column(spacing=8)
        dynamic_inputs_container = ft.Container(
            content=dynamic_inputs_column,
            border=ft.Border.all(width=1, color=ft.Colors.OUTLINE_VARIANT),
            border_radius=8, padding=12, visible=False,
        )

        # Shared file picker for all dynamic file inputs
        file_picker = ft.FilePicker()

        # ==================================================================
        # Selection helpers
        # ==================================================================

        def selected_repo() -> RepoEntry | None:
            """Return the RepoEntry matching the current repo dropdown value."""
            for repo in console_config.repos:
                if repo.name == repo_dd.value:
                    return repo
            return None

        def selected_repo_path() -> str:
            """Return the filesystem path of the selected repository."""
            repo = selected_repo()
            if repo is None:
                raise ActionExecutionError("Select a repo.")
            return repo.path

        def find_selected_workflow() -> WorkflowEntry | None:
            """Return the WorkflowEntry matching the current workflow dropdown value."""
            repo = selected_repo()
            if repo is None or not workflow_dd.value:
                return None
            return next((w for w in repo.workflows if w.name == workflow_dd.value), None)

        def selected_workflow(required: bool = True) -> WorkflowEntry | None:
            """Return the selected workflow, raising if *required* and none is selected."""
            workflow = find_selected_workflow()
            if workflow is None and required:
                raise ActionExecutionError("Select a workflow.")
            return workflow

        def _resolve_repo_and_workflow(workflow_name: str) -> tuple[str, WorkflowEntry | None]:
            """Find the repo path and WorkflowEntry matching a workflow_name.

            Scans all configured repos to find the first match for the given
            workflow name. Used when resolving approvable/resettable runs
            selected from a worker-scoped active runs list.

            Parameters
            ----------
            workflow_name :
                The name of the workflow to find.

            Returns
            -------
            tuple[str, WorkflowEntry | None]
                A tuple of (repo_path, WorkflowEntry or None if not found).
            """
            for repo in console_config.repos:
                for wf in repo.workflows:
                    if wf.workflow_name == workflow_name:
                        return repo.path, wf
            return "", None

        def create_workflow_options(repo: RepoEntry | None) -> list:
            """Build dropdown options for the workflows in *repo*."""
            if repo is None:
                return []
            return [ft.DropdownOption(key=w.name, text=w.name) for w in repo.workflows]

        def show_error(message: str) -> None:
            """Display a modal error dialog."""
            _log.error(message)
            page.show_dialog(ft.AlertDialog(
                modal=True, title=ft.Text("Console Error"),
                content=ft.Text(message),
                actions=[ft.TextButton("Close", on_click=lambda e: page.pop_dialog())],
            ))

        # ==================================================================
        # Dynamic input field generation from workflow.toml
        # ==================================================================

        def rebuild_input_fields() -> None:
            """Rebuild the dynamic input panel for the selected workflow.

            Loads the workflow's ``workflow.toml``, reads the init step's
            ``required_inputs``, and creates a TextField (+ Browse button for
            ``*_FILE`` keys) for each required input.
            """
            input_fields.clear()
            dynamic_inputs_column.controls.clear()

            workflow = find_selected_workflow()
            if workflow is None:
                dynamic_inputs_container.visible = False
                return

            bundle_dir = get_workflow_root() / workflow.workflow_name

            if not bundle_dir.exists():
                dynamic_inputs_column.controls.append(
                    ft.Text(f"Workflow directory not found: {bundle_dir}", color="red"),
                )
                dynamic_inputs_container.visible = True
                return

            try:
                bundle = load_workflow_package(bundle_dir)
            except Exception as exc:
                dynamic_inputs_column.controls.append(
                    ft.Text(f"Failed to load workflow: {exc}", color="red"),
                )
                dynamic_inputs_container.visible = True
                return

            init_step_name = bundle.init_step
            if not init_step_name or init_step_name not in bundle.steps:
                dynamic_inputs_column.controls.append(
                    ft.Text("No input artifacts required.", italic=True, color="grey"),
                )
                dynamic_inputs_container.visible = True
                return

            required_inputs = bundle.steps[init_step_name].required_inputs
            if not required_inputs:
                dynamic_inputs_column.controls.append(
                    ft.Text("No input artifacts required.", italic=True, color="grey"),
                )
                dynamic_inputs_container.visible = True
                return

            for key in required_inputs:
                if key.endswith("_FILE"):
                    tf = ft.TextField(
                        label=key, read_only=False, expand=True,
                        hint_text=f"Filename or browse for {key}",
                    )

                    async def on_browse_click(e, k=key, f=tf):
                        """Open file picker, optionally rooted at the SDLC delivery dir."""
                        if k in SDLC_INPUT_DIRS:
                            resolved = Path(selected_repo_path()) / SDLC_INPUT_DIRS[k]
                            if resolved.is_dir():
                                file_picker.root_directory = str(resolved)
                        else:
                            file_picker.root_directory = None
                        files = await file_picker.pick_files(
                            file_type=ft.FilePickerFileType.CUSTOM,
                            allowed_extensions=["md"],
                        )
                        if files:
                            f.value = files[0].path or ""
                            page.update()

                    btn = ft.ElevatedButton("Browse", on_click=on_browse_click)
                    input_fields[key] = tf
                    dynamic_inputs_column.controls.append(ft.Column([
                        ft.Text(key, weight=ft.FontWeight.BOLD, size=12),
                        ft.Row([tf, btn], spacing=8),
                    ], spacing=4))
                else:
                    tf = ft.TextField(label=key, expand=True, hint_text=f"Enter {key}")
                    input_fields[key] = tf
                    dynamic_inputs_column.controls.append(ft.Column([
                        ft.Text(key, weight=ft.FontWeight.BOLD, size=12),
                        ft.Row([tf], spacing=8),
                    ], spacing=4))

            dynamic_inputs_container.visible = True

        # ==================================================================
        # File resolution
        # ==================================================================

        def resolve_input_path(key: str, value: str, repo_path: Path) -> str:
            """Resolve an input value to an absolute path.

            - If *value* is an existing absolute path, return as-is.
            - If *key* is in ``SDLC_INPUT_DIRS``, resolve the filename against
              the known delivery subdirectory.
            - Non-file keys are returned as-is.
            """
            value = value.strip()
            if not value:
                return ""

            p = Path(value)
            if p.is_absolute() and p.exists():
                return str(p)

            if key in SDLC_INPUT_DIRS:
                resolved = repo_path / SDLC_INPUT_DIRS[key] / value
                if resolved.exists():
                    return str(resolved)
                raise ActionExecutionError(
                    f"File not found for {key}: {value}\n"
                    f"  Tried: {resolved}\n"
                    f"  Expected in: {SDLC_INPUT_DIRS[key]}/"
                )

            if not key.endswith("_FILE"):
                return value

            raise ActionExecutionError(
                f"Cannot resolve file path for {key}: {value}\n"
                f"  Provide a full path or browse for the file."
            )

        def collect_input_artifacts(repo_path: Path) -> dict[str, str]:
            """Collect and resolve all dynamic input field values."""
            result: dict[str, str] = {}
            for key, tf in input_fields.items():
                value = (tf.value or "").strip()
                if not value:
                    continue
                result[key] = resolve_input_path(key, value, repo_path)
            return result

        # ==================================================================
        # Dropdown event handlers
        # ==================================================================

        def on_repo_changed(_event=None) -> None:
            """Refresh the workflow dropdown when the repository changes."""
            try:
                repo = selected_repo()
                if repo is None:
                    workflow_dd.options = []
                    workflow_dd.value = None
                    workflow_dd.disabled = True
                    rebuild_input_fields()
                    page.update()
                    return

                workflow_dd.options = create_workflow_options(repo)
                if repo.workflows:
                    workflow_dd.value = repo.workflows[0].name
                    workflow_dd.disabled = False
                else:
                    workflow_dd.value = None
                    workflow_dd.disabled = True

                rebuild_input_fields()
                page.update()
            except Exception:
                _log.exception("Unexpected error while changing repository.")
                show_error("Unable to update the workflow list for the selected repository.")

        def on_workflow_changed(_event=None) -> None:
            """Rebuild dynamic input fields when the workflow selection changes."""
            try:
                rebuild_input_fields()
                page.update()
            except Exception:
                _log.exception("Unexpected error while changing workflow.")
                show_error("Unable to process the selected workflow.")

        def refresh_step_options(_event=None) -> None:
            """Populate the Reset Target Step dropdown from the workflow's step order."""
            workflow = selected_workflow(required=False)
            if workflow is None:
                reset_step_dd.options = []
                reset_step_dd.value = None
                page.update()
                return
            bundle_dir = get_workflow_root() / workflow.workflow_name
            try:
                bundle = load_workflow_package(bundle_dir)
                reset_step_dd.options = [ft.dropdown.Option(s) for s in bundle.step_order]
                if bundle.step_order:
                    reset_step_dd.value = bundle.step_order[0]
            except Exception as exc:
                reset_step_dd.options = []
                reset_step_dd.value = None
                output.value = f"Failed to load workflow steps: {exc}"
            page.update()

        # ==================================================================
        # Active runs
        # ==================================================================

        def refresh_active_runs(_event=None) -> None:
            """Fetch active runs from the backend and populate the dropdown."""
            nonlocal active_runs, selected_run_id
            try:
                active_runs = backend_service.list_active_runs_for_worker()
                if active_runs:
                    selected_run_id = active_runs[0].run_id
                    # Build display text with: repo_name, workflow_name, run_code, status, current_step
                    # We look up the repo for each run based on workflow_name
                    display_options = []
                    for run in active_runs:
                        repo_name = "-"
                        for repo in console_config.repos:
                            for wf in repo.workflows:
                                if wf.workflow_name == run.workflow_name:
                                    repo_name = repo.name
                                    break
                            if repo_name != "-":
                                break
                        display_text = f"[{repo_name}] [{run.workflow_name}] {run.run_code or run.run_id} | {run.status} | {run.current_step or '-'}"
                        display_options.append(ft.dropdown.Option(key=run.run_id, text=display_text))
                    active_runs_dd.options = display_options
                    active_runs_dd.value = active_runs[0].run_id
                else:
                    selected_run_id = ""
                    active_runs_dd.options = []
                    active_runs_dd.value = None
                output.value = f"Found {len(active_runs)} active run(s)."
                # Refresh repo/workflow dropdowns based on the currently selected run
                _on_active_run_selected()
            except Exception as exc:
                selected_run_id = ""
                active_runs_dd.options = []
                active_runs_dd.value = None
                output.value = str(exc)
                page.update()

        def _on_active_run_selected(_event=None) -> None:
            """Track which active run is selected and auto-populate repo/workflow dropdowns."""
            nonlocal selected_run_id
            selected_run_id = active_runs_dd.value or ""

            # Auto-populate repo and workflow dropdowns based on the selected run
            if not selected_run_id:
                return

            # Find the selected run
            selected_run = next((r for r in active_runs if r.run_id == selected_run_id), None)
            if not selected_run:
                return

            # Find the repo and workflow for this run's workflow_name
            found = False
            for repo in console_config.repos:
                for wf in repo.workflows:
                    if wf.workflow_name == selected_run.workflow_name:
                        # Update the dropdowns
                        repo_changed = repo_dd.value != repo.name
                        if repo_changed:
                            repo_dd.value = repo.name
                            repo_dd.disabled = False
                            # Update workflow dropdown
                            workflow_dd.options = create_workflow_options(repo)
                        if workflow_dd.value != wf.name:
                            workflow_dd.value = wf.name
                        workflow_dd.disabled = False
                        found = True
                        break
                if found:
                    break
            if found:
                page.update()

        # ==================================================================
        # Auto-refresh
        # ==================================================================

        async def _auto_refresh_loop() -> None:
            """Periodically refresh active runs every 5 seconds while enabled."""
            while auto_refresh_cb.value:
                await asyncio.sleep(5)
                if not auto_refresh_cb.value:
                    break
                try:
                    refresh_active_runs()
                except Exception:
                    _log.exception("[console] auto-refresh error")

        def _on_auto_refresh_changed(e) -> None:
            """Start the auto-refresh loop when the checkbox is enabled."""
            if auto_refresh_cb.value:
                page.run_task(_auto_refresh_loop)

        # ==================================================================
        # Visibility
        # ==================================================================

        def update_visibility(_event=None) -> None:
            """Show/hide UI sections based on the selected action."""
            action = action_dd.value or ""
            needs_active = action in {"Approve", "Reject", "Reset", "Cancel"}

            feedback_tf.visible = needs_active
            reset_step_dd.visible = action == "Reset"

            page.update()

            if needs_active:
                refresh_active_runs()

        # ==================================================================
        # Execute action
        # ==================================================================

        def execute_action(_event) -> None:
            """Dispatch the selected action to the appropriate service method."""
            try:
                action = action_dd.value or ""
                repo_path = selected_repo_path()
                workflow = selected_workflow(required=True)
                input_artifacts = collect_input_artifacts(Path(repo_path))

                if action == "Submit":
                    rendered = runner_service.submit_job(
                        repo_path=repo_path,
                        workflow=workflow,
                        input_artifacts=input_artifacts,
                    )

                elif action == "Approve":
                    run_id = str(selected_run_id or "").strip()
                    if not run_id:
                        raise ActionExecutionError("Select an active run to approve.")
                    detail = backend_service.get_run_detail(run_id=run_id)
                    run_payload = detail.get("run") or {}
                    step_name = str(run_payload.get("awaiting_human_step") or "").strip()
                    job_id = str(run_payload.get("run_code") or "").strip()
                    workflow_name = str(run_payload.get("workflow_name") or "").strip()
                    if not step_name or not job_id:
                        raise ActionExecutionError(
                            "Selected run is missing awaiting_human_step or run_code.",
                        )
                    # Resolve repo and workflow from the run's workflow_name for local runner call
                    resolved_repo_path, resolved_workflow = _resolve_repo_and_workflow(workflow_name)
                    if resolved_workflow is None:
                        raise ActionExecutionError(
                            f"Unable to find workflow '{workflow_name}' in configured repos."
                        )
                    rendered_local = runner_service.approve_step(
                        repo_path=resolved_repo_path,
                        template_group=resolved_workflow.template_group or resolved_workflow.workflow_name,
                        job_id=job_id, step_name=step_name,
                    )
                    backend_result = backend_service.approve_run(
                        run_id=run_id, reject=False,
                        feedback=feedback_tf.value or "",
                    )
                    rendered = f"Local: {rendered_local}\n\nBackend: {_render_result(backend_result)}"

                elif action == "Reject":
                    run_id = str(selected_run_id or "").strip()
                    if not run_id:
                        raise ActionExecutionError("Select an active run to reject.")
                    result = backend_service.approve_run(
                        run_id=run_id, reject=True,
                        feedback=feedback_tf.value or "",
                    )
                    rendered = _render_result(result)

                elif action == "Cancel":
                    run_id = str(selected_run_id or "").strip()
                    if not run_id:
                        raise ActionExecutionError("Select an active run to cancel.")
                    result = backend_service.stop_run(
                        run_id=run_id, reason=feedback_tf.value or "",
                    )
                    rendered = _render_result(result)

                elif action == "Reset":
                    step_name = str(reset_step_dd.value or "").strip()
                    if not step_name:
                        raise ActionExecutionError("Select a reset target step.")
                    run_id = str(selected_run_id or "").strip()
                    if not run_id:
                        raise ActionExecutionError("Select an active run.")
                    target_run = next((r for r in active_runs if r.run_id == run_id), None)
                    if target_run is None:
                        raise ActionExecutionError("Selected run not found in active list.")
                    if not target_run.run_code:
                        raise ActionExecutionError("Selected run has no run_code.")
                    # Resolve repo and workflow from the run's workflow_name for local runner call
                    resolved_repo_path, resolved_workflow = _resolve_repo_and_workflow(target_run.workflow_name)
                    if resolved_workflow is None:
                        raise ActionExecutionError(
                            f"Unable to find workflow '{target_run.workflow_name}' in configured repos."
                        )
                    rendered_local = runner_service.override_step(
                        repo_path=resolved_repo_path,
                        template_group=resolved_workflow.template_group or resolved_workflow.workflow_name,
                        job_id=target_run.run_code, step_name=step_name,
                    )
                    try:
                        backend_result = backend_service.reset_run_step(
                            run_id=target_run.run_id, step_name=step_name,
                        )
                        rendered = f"Local: {rendered_local}\n\nBackend: {_render_result(backend_result)}"
                    except RuntimeError as be:
                        _log.warning("[console] reset backend call failed: %s", be)
                        rendered = f"Local: {rendered_local}\n\nBackend (warning): {be}"

                else:
                    raise ActionExecutionError(f"Unsupported action: {action}")

                output.value = rendered
            except Exception as exc:
                output.value = str(exc)
            page.update()

        # ==================================================================
        # Button controls
        # ==================================================================

        refresh_button = ft.ElevatedButton("Refresh Active Runs", on_click=refresh_active_runs)
        execute_button = ft.ElevatedButton(
            "Run Action", on_click=execute_action,
            bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE,
            style=ft.ButtonStyle(text_style=ft.TextStyle(weight=ft.FontWeight.BOLD)),
        )
        auto_refresh_cb = ft.Checkbox(label="Auto-refresh", value=False)

        # ==================================================================
        # Initialise workflow dropdown for the first repo
        # ==================================================================

        initial_repo = console_config.repos[0] if console_config.repos else None
        if initial_repo:
            workflow_dd.options = create_workflow_options(initial_repo)
            if initial_repo.workflows:
                workflow_dd.value = initial_repo.workflows[0].name
                workflow_dd.disabled = False
            else:
                workflow_dd.value = None
                workflow_dd.disabled = True

        # -- Wire event handlers --------------------------------------------
        action_dd.on_change = update_visibility
        repo_dd.on_select = on_repo_changed
        workflow_dd.on_select = on_workflow_changed
        active_runs_dd.on_change = _on_active_run_selected
        auto_refresh_cb.on_change = _on_auto_refresh_changed

        page.services.append(file_picker)

        # ==================================================================
        # Page layout
        # ==================================================================

        page.add(ft.Column(controls=[
            ft.Text("Agent Runner Operator Console", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Choose a repository and its workflow.", size=14),
            ft.Divider(),
            ft.Row(
                controls=[repo_dd, workflow_dd, action_dd, execute_button],
                wrap=True, spacing=16, run_spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
            status_text,
            ft.Row(
                controls=[active_runs_container, ft.Column([refresh_button, auto_refresh_cb])],
                wrap=True, spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            reset_step_dd,
            feedback_tf,
            dynamic_inputs_container,
            output,
        ], spacing=16))

        # Initial population
        rebuild_input_fields()
        refresh_step_options()

    view = ft.AppView.WEB_BROWSER if args.web else None
    ft.run(main=app, view=view)
    return 0


# ===========================================================================
# Helpers
# ===========================================================================

def _render_result(payload: object) -> str:
    """Render a backend response payload as pretty-printed JSON."""
    return json.dumps(payload, indent=2, ensure_ascii=False)
