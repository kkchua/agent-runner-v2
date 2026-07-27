"""Runner action service for the operator console.

Wraps CLI entry points so the console can invoke them in-process with
captured stdout/stderr. All operations go through the CLI — no direct
backend API calls.

Architecture: Console → CLI → Backend (CLI owns all backend communication).
"""
from __future__ import annotations

import contextlib
import io
import logging
import os
import sys
from pathlib import Path
from typing import Callable

from ... import run_agent, submit_commands, sync_workflows
from ... import list_runs_commands
from ... import show_run_commands
from ... import stop_commands
from ... import approve_commands
from ... import reset_step_commands
from ..models import ActiveRunSummary, GlobalSettings, WorkflowEntry

_log = logging.getLogger(__name__)


class ActionExecutionError(RuntimeError):
    """Raised when a runner action fails or produces a non-zero exit code."""


def _extract_runs_from_json(json_str: str) -> list[ActiveRunSummary]:
    """Parse CLI list-runs JSON output into ActiveRunSummary objects."""
    import json as _json
    try:
        payload = _json.loads(json_str)
    except (ValueError, TypeError):
        return []
    items = payload if isinstance(payload, list) else payload.get("runs") or payload.get("items") or payload.get("data") or []
    results: list[ActiveRunSummary] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        current_step = (
            str(item.get("current_step") or "").strip()
            or str(item.get("current_step_name") or "").strip()
        )
        results.append(ActiveRunSummary(
            run_id=str(item.get("id") or item.get("run_id") or "").strip(),
            run_code=str(item.get("run_code") or item.get("job_id") or "").strip(),
            workflow_name=str(item.get("workflow_name") or item.get("template_group") or "").strip(),
            status=str(item.get("status") or item.get("job_status") or item.get("run_status") or "").strip(),
            current_step=current_step,
            updated_at=str(item.get("updated_at") or item.get("modified_at") or "").strip(),
            worker_id=str(item.get("worker_id") or item.get("target_worker_id") or "").strip(),
            project_root=str(item.get("project_root") or item.get("target_project_root") or "").strip(),
        ))
    return results


class RunnerActionService:
    """Invoke runner CLI commands in-process for the operator console.

    Each method builds an argument list and delegates to ``_invoke()`` or
    ``_invoke_from_anywhere()``, which redirects stdout/stderr, runs the CLI
    function, and returns the captured output as a string.

    All backend communication goes through the CLI — this service never
    imports or uses BackendClient directly.
    """

    def __init__(self, settings: GlobalSettings):
        self._settings = settings

    # ------------------------------------------------------------------
    # Backend API wrapper commands (no chdir needed, run from anywhere)
    # ------------------------------------------------------------------

    def list_runs(
        self, *, worker_id: str = "", status_group: str = "non_terminal",
        workflow_name: str = "",
    ) -> str:
        """List workflow runs via CLI (backend API wrapper). Returns raw JSON."""
        args = ["list-runs"]
        if worker_id:
            args.extend(["--worker-id", worker_id])
        if status_group and status_group != "all":
            args.extend(["--status-group", status_group])
        if workflow_name:
            args.extend(["--workflow-name", workflow_name])
        return self._invoke_from_anywhere(func=list_runs_commands.main, argv=args)

    def list_active_runs_for_worker(self, *, worker_id: str = "") -> list[ActiveRunSummary]:
        """List active runs for a worker, returning ActiveRunSummary objects.

        This is the direct replacement for BackendRunService.list_active_runs_for_worker().
        Calls the CLI and parses the JSON output into ActiveRunSummary objects.
        """
        json_str = self.list_runs(worker_id=worker_id, status_group="non_terminal")
        return _extract_runs_from_json(json_str)

    def show_run(self, *, run_id: str) -> str:
        """Show a single run's details via CLI (backend API wrapper). Returns raw JSON."""
        return self._invoke_from_anywhere(
            func=show_run_commands.main, argv=["show-run", run_id],
        )

    def get_run_detail_dict(self, *, run_id: str) -> dict:
        """Show run detail and return parsed dict (replaces backend_service.get_run_detail)."""
        import json as _json
        json_str = self.show_run(run_id=run_id)
        try:
            return _json.loads(json_str)
        except (ValueError, TypeError):
            return {}

    def stop_run(self, *, run_id: str, reason: str = "") -> str:
        """Stop/cancel a run via CLI (comprehensive cancel)."""
        args = ["stop", run_id]
        if reason:
            args.extend(["--reason", reason])
        return self._invoke_from_anywhere(func=stop_commands.main, argv=args)

    def approve(
        self, *, run_id: str, reject: bool = False, feedback: str = "",
        resume: bool = False, retry: bool = False,
    ) -> str:
        """Approve, reject, resume, or retry a run via CLI."""
        args = ["approve", run_id]
        if reject:
            args.append("--reject")
        if resume:
            args.append("--resume")
        if retry:
            args.append("--retry")
        if feedback:
            args.extend(["--feedback", feedback])
        return self._invoke_from_anywhere(func=approve_commands.main, argv=args)

    def reset_step(self, *, run_id: str, step_name: str) -> str:
        """Reset a run's current step via CLI."""
        return self._invoke_from_anywhere(
            func=reset_step_commands.main, argv=["reset-step", run_id, step_name],
        )

    # ------------------------------------------------------------------
    # Execution commands (need chdir to repo path)
    # ------------------------------------------------------------------

    def submit_job(
        self,
        *,
        repo_path: str,
        workflow: WorkflowEntry,
        input_artifacts: dict[str, str] | None = None,
        worker_id: str | None = None,
        os_type: str = "",
        start_step: str = "",
    ) -> str:
        """Submit a workflow run to the backend queue via CLI.

        Parameters
        ----------
        repo_path :
            Working directory for the invocation (becomes project_root).
        workflow :
            The workflow entry to submit.
        input_artifacts :
            Optional dict of ``{KEY: VALUE}`` pairs passed as ``--input`` flags.
        worker_id :
            Override worker ID. Falls back to global settings if not provided.
        os_type :
            Repo OS type (unused — CLI handles all paths natively).
        start_step :
            Override the starting step for a new job (skip earlier steps).
        """
        args = ["--workflow-name", workflow.workflow_name]
        effective_worker_id = worker_id or self._settings.worker_id
        if effective_worker_id:
            args.extend(["--worker-id", effective_worker_id])
        if self._settings.worker_label:
            args.extend(["--worker-label", self._settings.worker_label])
        if input_artifacts:
            for key, value in input_artifacts.items():
                args.extend(["--input", f"{key}={value}"])
        if start_step:
            args.extend(["--start-step", start_step])
        return self._invoke(repo_path=repo_path, func=submit_commands.main, argv=args)

    def init_workspace(
        self,
        *,
        repo_path: str,
        workflow_name: str = "default",
        bundle_domain: str = "general",
        bundle_profile: str = "core+workflow",
    ) -> str:
        """Run ``ukbe-run-agent init`` to seed workflow bundles."""
        args = [
            "init", "--workflow", workflow_name,
            "--bundle-domain", bundle_domain,
            "--bundle-profile", bundle_profile,
        ]
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=args)

    def bootstrap_publish(self, *, repo_path: str) -> str:
        """Run ``ukbe-run-agent bootstrap-publish`` to publish bootstrap bundles."""
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=["bootstrap-publish"])

    def sync_workflow(
        self, *, repo_path: str, workflow: WorkflowEntry | None = None,
    ) -> str:
        """Sync workflow definitions to the backend."""
        args: list[str] = []
        if workflow is not None:
            args.append(workflow.workflow_name)
        return self._invoke(repo_path=repo_path, func=sync_workflows.main, argv=args)

    # ------------------------------------------------------------------
    # Local CLI admin commands (need chdir to repo path, read job.json)
    # ------------------------------------------------------------------

    def approve_step(
        self, *, repo_path: str, template_group: str,
        job_id: str, step_name: str,
    ) -> str:
        """Approve a specific step in a running job (local runner invocation)."""
        args = [
            "run", "--template-group", template_group,
            "--job-id", job_id, "--approve-step", step_name,
        ]
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=args)

    def reject_step(
        self, *, repo_path: str, template_group: str,
        job_id: str, step_name: str,
    ) -> str:
        """Reject a specific step in a running job (local runner invocation)."""
        args = [
            "run", "--template-group", template_group,
            "--job-id", job_id, "--reject-step", step_name,
        ]
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=args)

    def resume_step(
        self, *, repo_path: str, template_group: str,
        job_id: str, step_name: str,
    ) -> str:
        """Resume a step waiting for intervention or max-retried (force-approve, advance)."""
        args = [
            "run", "--template-group", template_group,
            "--job-id", job_id, "--resume-step", step_name,
        ]
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=args)

    def retry_step(
        self, *, repo_path: str, template_group: str,
        job_id: str, step_name: str,
    ) -> str:
        """Retry a step waiting for intervention or max-retried (reset counts, re-execute)."""
        args = [
            "run", "--template-group", template_group,
            "--job-id", job_id, "--retry-step", step_name,
        ]
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=args)

    def cancel_run(
        self, *, repo_path: str, template_group: str,
        job_id: str,
    ) -> str:
        """Cancel an entire run — set job status to STOPPED and sync to backend."""
        args = [
            "run", "--template-group", template_group,
            "--job-id", job_id, "--cancel-run",
        ]
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=args)

    def override_step(
        self, *, repo_path: str, template_group: str,
        job_id: str, step_name: str,
    ) -> str:
        """Override the current step of a running job to a different step."""
        args = [
            "run", "--template-group", template_group,
            "--job-id", job_id, "--override-step", step_name,
        ]
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=args)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _invoke(
        self, *, repo_path: str,
        func: Callable[[list[str] | None], int] | Callable[[], int],
        argv: list[str],
    ) -> str:
        """Execute a CLI function in-process with chdir to repo_path.

        Changes the working directory to *repo_path*, redirects stdout and
        stderr, calls *func(argv)*, and returns the captured output.
        Raises ``ActionExecutionError`` on non-zero exit or exception.
        """
        workdir = Path(repo_path).resolve()
        func_name = getattr(func, "__name__", str(func))
        _log.info("[console] _invoke func=%s argv=%s cwd=%s", func_name, argv, workdir)

        stdout = io.StringIO()
        stderr = io.StringIO()
        exit_code = 1
        try:
            with _pushd(workdir), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                if argv:
                    exit_code = func(argv)  # type: ignore[misc]
                else:
                    exit_code = func()  # type: ignore[misc]
        except Exception as exc:
            error_text = stderr.getvalue().strip()
            rendered = stdout.getvalue().strip()
            detail = error_text or rendered or str(exc)
            _log.error("[console] _invoke exception func=%s: %s", func_name, detail)
            raise ActionExecutionError(detail) from exc

        return self._process_output(func_name, exit_code, stdout, stderr)

    def _invoke_from_anywhere(
        self, *,
        func: Callable[[list[str] | None], int] | Callable[[], int],
        argv: list[str],
    ) -> str:
        """Execute a CLI function without chdir (for backend API wrapper commands).

        These commands read backend_url from config.json and make HTTP calls.
        They don't need any repo context or working directory.
        """
        func_name = getattr(func, "__name__", str(func))
        _log.info("[console] _invoke_from_anywhere func=%s argv=%s", func_name, argv)

        stdout = io.StringIO()
        stderr = io.StringIO()
        exit_code = 1
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                if argv:
                    exit_code = func(argv)  # type: ignore[misc]
                else:
                    exit_code = func()  # type: ignore[misc]
        except Exception as exc:
            error_text = stderr.getvalue().strip()
            rendered = stdout.getvalue().strip()
            detail = error_text or rendered or str(exc)
            _log.error("[console] _invoke_from_anywhere exception func=%s: %s", func_name, detail)
            raise ActionExecutionError(detail) from exc

        return self._process_output(func_name, exit_code, stdout, stderr)

    def _process_output(
        self, func_name: str, exit_code: int,
        stdout: io.StringIO, stderr: io.StringIO,
    ) -> str:
        """Process captured stdout/stderr and raise on failure."""
        rendered = stdout.getvalue().strip()
        error_text = stderr.getvalue().strip()
        _log.info(
            "[console] _invoke done func=%s exit=%d stdout_len=%d stderr_len=%d",
            func_name, exit_code, len(rendered), len(error_text),
        )
        if exit_code != 0:
            detail = error_text or rendered or f"command failed with exit code {exit_code}"
            raise ActionExecutionError(detail)
        if error_text and not rendered:
            return error_text
        if rendered and error_text:
            return rendered + os.linesep + error_text
        return rendered or error_text or "ok"


@contextlib.contextmanager
def _pushd(path: Path):
    """Context manager to temporarily change the working directory."""
    original = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)
