"""Flet-based operator console for Agent Runner.

Provides a universal launcher that replaces per-workflow batch files.  The console
dynamically detects each workflow's input requirements from ``workflow.toml`` and
generates appropriate UI fields (file pickers for file artifacts, text fields for
scalar values).

Actions
-------
- **Submit** — queue a workflow run via the backend API.
- **Approve** — approve a step awaiting human review.
- **Reject** — reject a step awaiting human review, sending it back for refinement.
- **Resume** — resume a step waiting for intervention.
- **Retry** — retry a step that failed or was rejected.
- **Reset** — override the current step of an active run.
- **Cancel** — stop an active run.
- **Quit Daemon** — gracefully shut down the daemon.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

import flet as ft

from .builders import UIBuilder
from .config import ConsoleConfigError, load_console_config, load_global_settings
from .handlers import EventHandlers
from .services.runner_service import RunnerActionService
from .state import ConsoleState

_log = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    """Run the operator console.

    Args:
        argv: Command line arguments.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    parser = argparse.ArgumentParser(
        prog="ukbe-run-agent console",
        description="Launch the desktop operator console.",
    )
    parser.add_argument("--config", default="", help="Override operator console config path.")
    parser.add_argument("--web", action="store_true", help="Open console in web browser instead of desktop window.")
    args = parser.parse_args(argv)

    # Single instance enforcement - only one console can run
    from ..single_instance import check_single_instance
    check_single_instance(
        "ukbe-runner-console",
        "Console is already running. Close the existing window first."
    )

    try:
        import flet as ft  # noqa: F401
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

    runner_service = RunnerActionService(settings)

    # -----------------------------------------------------------------------
    # Flet application
    # -----------------------------------------------------------------------

    def app(page: ft.Page) -> None:
        """Build the operator console UI using refactored architecture."""
        page.title = "Agent Runner Operator Console"
        page.window_width = 980
        page.window_height = 760
        page.scroll = ft.ScrollMode.AUTO
        page.padding = 20

        # Create state and handlers
        state = ConsoleState(page=page, config=console_config)
        state.runner_service = runner_service
        handlers = EventHandlers(state)

        # Output callback for execute_action
        def append_output(text: str) -> None:
            if state.output:
                state.output.value = (state.output.value or "") + text + "\n"
                state.update()

        # Execute handler
        async def on_execute(_event: ft.ControlEvent) -> None:
            await handlers.execute_action(runner_service, append_output)

        # Build UI
        builder = UIBuilder(state, handlers, on_execute)
        page.add(builder.build())

        # Add file picker to services (required for Flet FilePicker to work)
        if state.file_picker:
            page.services.append(state.file_picker)

        # Initial population
        handlers.on_worker_id_changed()
        handlers.refresh_step_options()

    view = ft.AppView.WEB_BROWSER if args.web else None
    ft.run(main=app, view=view)
    return 0


if __name__ == "__main__":
    sys.exit(main())
