from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from ..backend_client import BackendClient
from .config import ConsoleConfigError, load_console_config, load_global_settings
from .models import ActiveRunSummary, WorkflowEntry
from .services.backend_service import BackendRunService
from .services.runner_service import ActionExecutionError, RunnerActionService
from ..workflow_packages.loader import load_workflow_package

_log = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
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

    backend_service = BackendRunService(BackendClient(settings.backend_url), worker_id=settings.worker_id)
    runner_service = RunnerActionService(settings)

    def app(page: ft.Page) -> None:
        page.title = "Agent Runner Operator Console"
        page.window_width = 980
        page.window_height = 760
        page.scroll = ft.ScrollMode.AUTO
        page.padding = 20

        actions = [
            "submit job",
            "approval",
            "cancel job",
            "reset step",
            "bootstrap",
            "init",
            "sync",
            "cleanup",
        ]
        repo_options = [ft.dropdown.Option(repo.name) for repo in console_config.repos]
        workflow_options = [ft.dropdown.Option(workflow.name) for workflow in console_config.workflows]

        output = ft.TextField(
            label="Output",
            multiline=True,
            min_lines=14,
            max_lines=20,
            read_only=True,
            expand=True,
        )
        status_text = ft.Text(value=f"Backend: {settings.backend_url} | Worker: {settings.worker_id}")
        action_dd = ft.Dropdown(label="Action", options=[ft.dropdown.Option(value) for value in actions], value=actions[0])
        repo_dd = ft.Dropdown(
            label="Repo",
            options=repo_options,
            width=280,
            value=console_config.repos[0].name if console_config.repos else None,
        )
        workflow_dd = ft.Dropdown(
            label="Workflow",
            options=workflow_options,
            width=400,
            value=console_config.workflows[0].name if console_config.workflows else None,
        )
        selected_run_id: str = ""
        active_runs_dd = ft.Dropdown(
            label="Active Runs",
            options=[],
            width=880,
        )
        active_runs_container = ft.Container(
            content=active_runs_dd,
            border_radius=8,
            padding=12,
            width=900,
        )
        feedback_tf = ft.TextField(label="Feedback / Reason", multiline=True, min_lines=2, max_lines=4)
        initiative_tf = ft.TextField(label="Initiative ID")
        coder_tf = ft.TextField(label="Coder Override")
        reset_step_dd = ft.Dropdown(label="Reset Target Step", width=580)
        bundle_domain_tf = ft.TextField(label="Bundle Domain", value="general")
        bundle_profile_tf = ft.TextField(label="Bundle Profile", value="core+workflow")
        reject_cb = ft.Checkbox(label="Reject approval action", value=False)
        cleanup_dry_run_cb = ft.Checkbox(label="Cleanup dry-run (preview only)", value=True)

        active_runs: list[ActiveRunSummary] = []
        dynamic_section = ft.Column(spacing=12)

        def selected_repo_path() -> str:
            for repo in console_config.repos:
                if repo.name == repo_dd.value:
                    return repo.path
            raise ActionExecutionError("Select a repo.")

        def selected_workflow(required: bool = True) -> WorkflowEntry | None:
            for workflow in console_config.workflows:
                if workflow.name == workflow_dd.value:
                    return workflow
            if required:
                raise ActionExecutionError("Select a workflow.")
            return None

        def refresh_step_options(_event=None) -> None:
            try:
                workflow = selected_workflow(required=False)
                if workflow is None:
                    reset_step_dd.options = []
                    reset_step_dd.value = None
                    page.update()
                    return
                repo_root = Path(selected_repo_path())
                bundle_dir = repo_root / "workflows" / workflow.workflow_name
                bundle = load_workflow_package(bundle_dir)
                reset_step_dd.options = [ft.dropdown.Option(step_name) for step_name in bundle.step_order]
                if bundle.step_order:
                    reset_step_dd.value = bundle.step_order[0]
            except Exception as exc:
                reset_step_dd.options = []
                reset_step_dd.value = None
                output.value = f"Failed to load workflow steps: {exc}"
            page.update()

        def refresh_active_runs(_event=None) -> None:
            nonlocal active_runs, selected_run_id
            try:
                workflow = selected_workflow(required=False)
                active_runs = backend_service.list_active_runs(
                    repo_path=selected_repo_path(),
                    workflow_name=workflow.workflow_name if workflow else None,
                )
                if active_runs:
                    selected = active_runs[0]
                    selected_run_id = selected.run_id
                    active_runs_dd.options = [
                        ft.dropdown.Option(
                            key=run.run_id,
                            text=f"{run.run_code or run.run_id} | {run.status} | {run.current_step or '-'}",
                        )
                        for run in active_runs
                    ]
                    active_runs_dd.value = active_runs[0].run_id
                else:
                    selected_run_id = ""
                    active_runs_dd.options = []
                    active_runs_dd.value = None
                output.value = f"Found {len(active_runs)} active run(s)."
            except Exception as exc:
                selected_run_id = ""
                active_runs_dd.options = []
                active_runs_dd.value = None
                output.value = str(exc)
            page.update()

        def _on_active_run_selected(_event=None) -> None:
            nonlocal selected_run_id
            selected_run_id = active_runs_dd.value or ""

        def update_visibility(_event=None) -> None:
            action = action_dd.value or ""
            needs_run = action in {"approval", "cancel job", "reset step"}
            workflow_dd.visible = action in {"submit job", "approval", "cancel job", "reset step", "init", "sync", "cleanup"}
            cleanup_dry_run_cb.visible = action == "cleanup"
            page.update()
            if needs_run and repo_dd.value and workflow_dd.value:
                refresh_active_runs()

        def execute_action(_event) -> None:
            try:
                action = action_dd.value or ""
                repo_path = selected_repo_path()
                if action == "submit job":
                    rendered = runner_service.submit_job(
                        repo_path=repo_path,
                        workflow=selected_workflow(required=True),
                        initiative_id=initiative_tf.value or "",
                        coder=coder_tf.value or "",
                    )
                elif action == "approval":
                    run_id = str(selected_run_id or "").strip()
                    if not run_id:
                        raise ActionExecutionError("Select an active run for approval.")
                    if reject_cb.value:
                        result = backend_service.approve_run(
                            run_id=run_id,
                            reject=True,
                            feedback=feedback_tf.value or "",
                        )
                        rendered = _render_result(result)
                    else:
                        detail = backend_service.get_run_detail(run_id=run_id)
                        run_payload = detail.get("run") or {}
                        step_name = str(run_payload.get("awaiting_human_step") or "").strip()
                        job_id = str(run_payload.get("run_code") or "").strip()
                        workflow = selected_workflow(required=True)
                        if not step_name or not job_id:
                            raise ActionExecutionError("Selected run is missing awaiting_human_step or run_code.")
                        rendered_local = runner_service.approve_step(
                            repo_path=repo_path,
                            template_group=workflow.workflow_name,
                            job_id=job_id,
                            step_name=step_name,
                        )
                        backend_result = backend_service.approve_run(
                            run_id=run_id,
                            reject=False,
                            feedback=feedback_tf.value or "",
                        )
                        rendered = f"Local: {rendered_local}\n\nBackend: {_render_result(backend_result)}"
                elif action == "cancel job":
                    run_id = str(selected_run_id or "").strip()
                    if not run_id:
                        raise ActionExecutionError("Select an active run to cancel.")
                    result = backend_service.stop_run(run_id=run_id, reason=feedback_tf.value or "")
                    rendered = _render_result(result)
                elif action == "reset step":
                    workflow = selected_workflow(required=True)
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
                    _log.info("[console] reset_step run_id=%s run_code=%s step=%s workflow=%s",
                              target_run.run_id, target_run.run_code, step_name, workflow.workflow_name)
                    rendered_local = runner_service.override_step(
                        repo_path=repo_path,
                        template_group=workflow.workflow_name,
                        job_id=target_run.run_code,
                        step_name=step_name,
                    )
                    _log.info("[console] reset_step local override complete: %s", rendered_local[:200])
                    try:
                        backend_result = backend_service.reset_run_step(
                            run_id=target_run.run_id,
                            step_name=step_name,
                        )
                        _log.info("[console] reset_step backend update: %s", _render_result(backend_result)[:200])
                        rendered = f"Local: {rendered_local}\n\nBackend: {_render_result(backend_result)}"
                    except RuntimeError as be:
                        _log.warning("[console] reset_step backend call failed (endpoint may need restart): %s", be)
                        rendered = f"Local: {rendered_local}\n\nBackend (warning): {be}"
                elif action == "bootstrap":
                    rendered = runner_service.bootstrap_publish(repo_path=repo_path)
                elif action == "init":
                    workflow = selected_workflow(required=True)
                    rendered = runner_service.init_workspace(
                        repo_path=repo_path,
                        workflow_name=workflow.workflow_name,
                        bundle_domain=bundle_domain_tf.value or "general",
                        bundle_profile=bundle_profile_tf.value or "core+workflow",
                    )
                elif action == "sync":
                    rendered = runner_service.sync_workflow(
                        repo_path=repo_path,
                        workflow=selected_workflow(required=True),
                    )
                elif action == "cleanup":
                    workflow = selected_workflow(required=True)
                    rendered = runner_service.cleanup_execution(
                        workflow_name=workflow.workflow_name,
                        dry_run=cleanup_dry_run_cb.value,
                    )
                else:
                    raise ActionExecutionError(f"Unsupported action: {action}")
                output.value = rendered
            except Exception as exc:
                output.value = str(exc)
            page.update()

        refresh_button = ft.ElevatedButton("Refresh Active Runs", on_click=refresh_active_runs)
        execute_button = ft.ElevatedButton("Run Action", on_click=execute_action)
        run_row = ft.Row([refresh_button, execute_button], wrap=True)
        submit_row = ft.Row([initiative_tf, coder_tf], wrap=True)
        init_row = ft.Row([bundle_domain_tf, bundle_profile_tf], wrap=True)

        action_dd.on_change = update_visibility
        repo_dd.on_change = refresh_active_runs
        workflow_dd.on_change = refresh_active_runs
        active_runs_dd.on_change = _on_active_run_selected

        page.add(
            ft.Column(
                controls=[
                    ft.Text("Agent Runner Operator Console", size=28, weight=ft.FontWeight.BOLD),
                    status_text,
                    ft.Row([action_dd, repo_dd, workflow_dd], wrap=True),
                    run_row,
                    active_runs_container,
                    reset_step_dd,
                    feedback_tf,
                    reject_cb,
                    cleanup_dry_run_cb,
                    submit_row,
                    init_row,
                    output,
                ],
                spacing=16,
            )
        )
        repo_dd.on_change = lambda e: (refresh_step_options(e), refresh_active_runs(e))
        workflow_dd.on_change = lambda e: (refresh_step_options(e), refresh_active_runs(e))
        refresh_step_options()
        update_visibility()

    ft.app(target=app)
    return 0


def _render_result(payload: object) -> str:
    import json

    return json.dumps(payload, indent=2, ensure_ascii=False)
