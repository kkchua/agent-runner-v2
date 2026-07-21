from __future__ import annotations

import argparse
import json
import logging
import sys

from ..backend_client import BackendClient
from .config import (
    ConsoleConfigError,
    load_console_config,
    load_global_settings,
)
from .services.backend_service import BackendRunService
from .services.runner_service import RunnerActionService


_log = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    """
    Launch the Agent Runner desktop operator console.
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

    parser.add_argument(
        "--config",
        default="",
        help="Override operator console config path.",
    )

    args = parser.parse_args(argv)

    try:
        import flet as ft
    except ImportError:
        print(
            'Flet is not installed. Install console dependencies with: '
            'pip install -e ".[console]"',
            file=sys.stderr,
        )
        return 2

    try:
        settings = load_global_settings()
        console_config = load_console_config(args.config or None)
    except ConsoleConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    # These services are ready for the later console actions.
    backend_service = BackendRunService(
        BackendClient(settings.backend_url),
        worker_id=settings.worker_id,
    )

    runner_service = RunnerActionService(settings)

    def app(page: ft.Page) -> None:
        page.title = "Agent Runner Operator Console"

        # Window settings may depend on the installed Flet version.
        page.window.width = 980
        page.window.height = 760

        page.scroll = ft.ScrollMode.AUTO
        page.padding = 20

        # ---------------------------------------------------------
        # Initial data
        # ---------------------------------------------------------

        initial_repo = (
            console_config.repos[0]
            if console_config.repos
            else None
        )

        initial_workflows = (
            initial_repo.workflows
            if initial_repo
            else ()
        )

        # ---------------------------------------------------------
        # Display controls
        # ---------------------------------------------------------

        selection_status = ft.Text(
            value="Select a repository and workflow.",
            size=14,
        )

        repo_details = ft.Text(
            value="",
            selectable=True,
        )

        workflow_details = ft.Text(
            value="",
            selectable=True,
        )

        # ---------------------------------------------------------
        # Helper functions
        # ---------------------------------------------------------

        def find_selected_repo():
            """
            Return the RepoEntry matching the current dropdown value.
            """

            selected_value = repo_dd.value

            if not selected_value:
                return None

            return next(
                (
                    repo
                    for repo in console_config.repos
                    if repo.name == selected_value
                ),
                None,
            )

        def find_selected_workflow():
            """
            Return the WorkflowEntry matching the current dropdown value.
            """

            repo = find_selected_repo()

            if repo is None or not workflow_dd.value:
                return None

            return next(
                (
                    workflow
                    for workflow in repo.workflows
                    if workflow.name == workflow_dd.value
                ),
                None,
            )

        def create_workflow_options(repo):
            """
            Build dropdown options for the selected repository.
            """

            if repo is None:
                return []

            return [
                ft.DropdownOption(
                    key=workflow.name,
                    text=workflow.name,
                )
                for workflow in repo.workflows
            ]

        def update_selection_display() -> None:
            """
            Update the informational text below the dropdowns.
            """

            repo = find_selected_repo()
            workflow = find_selected_workflow()

            if repo is None:
                selection_status.value = "No repository selected."
                repo_details.value = ""
                workflow_details.value = ""
                return

            repo_details.value = f"Selected repository: {repo.name}"

            if workflow is None:
                selection_status.value = (
                    f"Repository '{repo.name}' has no workflow selected."
                )
                workflow_details.value = ""
                return

            selection_status.value = (
                f"Selected: {repo.name} / {workflow.name}"
            )

            workflow_details.value = (
                f"Selected workflow: {workflow.name}"
            )

        def show_error(message: str) -> None:
            """
            Display an error message in the console UI.
            """

            _log.error(message)

            page.show_dialog(
                ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Console Error"),
                    content=ft.Text(message),
                    actions=[
                        ft.TextButton(
                            "Close",
                            on_click=lambda event: page.pop_dialog(),
                        )
                    ],
                )
            )

        # ---------------------------------------------------------
        # Event handlers
        # ---------------------------------------------------------

        def on_repo_selected(event) -> None:
            """
            Refresh the workflow dropdown when the repository changes.
            """

            try:
                _log.info(
                    "Repository selection event fired: value=%s, data=%s",
                    repo_dd.value,
                    getattr(event, "data", None),
                )

                repo = find_selected_repo()

                if repo is None:
                    _log.warning(
                        "Selected repository could not be found: %s",
                        repo_dd.value,
                    )

                    workflow_dd.options = []
                    workflow_dd.value = None
                    workflow_dd.disabled = True

                    update_selection_display()
                    page.update()
                    return

                _log.info(
                    "Selected repository: %s; workflows=%s",
                    repo.name,
                    [
                        workflow.name
                        for workflow in repo.workflows
                    ],
                )

                workflow_dd.options = create_workflow_options(repo)

                if repo.workflows:
                    workflow_dd.value = repo.workflows[0].name
                    workflow_dd.disabled = False
                else:
                    workflow_dd.value = None
                    workflow_dd.disabled = True

                update_selection_display()

                # Refresh the page because both the workflow dropdown and
                # the informational text have changed.
                page.update()

            except Exception:
                _log.exception(
                    "Unexpected error while changing repository."
                )

                show_error(
                    "Unable to update the workflow list for the "
                    "selected repository."
                )

        def on_workflow_selected(event) -> None:
            """
            Handle workflow selection changes.
            """

            try:
                _log.info(
                    "Workflow selection event fired: value=%s, data=%s",
                    workflow_dd.value,
                    getattr(event, "data", None),
                )

                workflow = find_selected_workflow()

                if workflow is None:
                    _log.warning(
                        "Selected workflow could not be found: %s",
                        workflow_dd.value,
                    )
                else:
                    _log.info(
                        "Selected workflow: %s",
                        workflow.name,
                    )

                update_selection_display()
                page.update()

            except Exception:
                _log.exception(
                    "Unexpected error while changing workflow."
                )

                show_error(
                    "Unable to process the selected workflow."
                )

        # ---------------------------------------------------------
        # Dropdown controls
        # ---------------------------------------------------------

        repo_dd = ft.Dropdown(
            label="Repository",
            hint_text="Select a repository",
            width=280,
            options=[
                ft.DropdownOption(
                    key=repo.name,
                    text=repo.name,
                )
                for repo in console_config.repos
            ],
            value=initial_repo.name if initial_repo else None,
            disabled=not bool(console_config.repos),
            on_select=on_repo_selected,
        )

        workflow_dd = ft.Dropdown(
            label="Workflow",
            hint_text="Select a workflow",
            width=400,
            options=create_workflow_options(initial_repo),
            value=(
                initial_workflows[0].name
                if initial_workflows
                else None
            ),
            disabled=not bool(initial_workflows),
            on_select=on_workflow_selected,
        )

        # Initialise the display text using the initial values.
        update_selection_display()

        # ---------------------------------------------------------
        # Page layout
        # ---------------------------------------------------------

        page.add(
            ft.SafeArea(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Agent Runner Operator Console",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "Choose a repository and its workflow.",
                            size=14,
                        ),
                        ft.Divider(),
                        ft.Row(
                            controls=[
                                repo_dd,
                                workflow_dd,
                            ],
                            wrap=True,
                            spacing=16,
                            run_spacing=12,
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    selection_status,
                                    repo_details,
                                    workflow_details,
                                ],
                                spacing=6,
                            ),
                            padding=16,
                            border=ft.Border.all(
                                width=1,
                                color=ft.Colors.OUTLINE_VARIANT,
                            ),
                            border_radius=8,
                        ),
                    ],
                    spacing=16,
                )
            )
        )

        _log.info(
            "Operator console loaded: initial_repo=%s, "
            "initial_workflow=%s",
            repo_dd.value,
            workflow_dd.value,
        )

    # Run the Flet application.
    ft.run(app)

    # Keep references alive and make the intended service setup explicit.
    _ = backend_service
    _ = runner_service

    return 0


def _render_result(payload: object) -> str:
    """
    Convert an action result into formatted JSON for display.
    """

    return json.dumps(
        payload,
        indent=2,
        ensure_ascii=False,
        default=str,
    )