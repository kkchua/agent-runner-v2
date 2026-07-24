"""Runner action service for the operator console.

Wraps the CLI entry points (``run_agent.main``, ``submit_commands.main``,
``sync_workflows.main``) so the console can invoke them in-process with
captured stdout/stderr.
"""
from __future__ import annotations

import contextlib
import io
import logging
import os
from pathlib import Path
from typing import Callable

from ... import run_agent, submit_commands, sync_workflows
from ...backend_client import BackendClient
from ..models import GlobalSettings, WorkflowEntry

_log = logging.getLogger(__name__)


class ActionExecutionError(RuntimeError):
    """Raised when a runner action fails or produces a non-zero exit code."""


class RunnerActionService:
    """Invoke runner CLI commands in-process for the operator console.

    Each method builds an argument list and delegates to ``_invoke()``, which
    redirects stdout/stderr, runs the CLI function, and returns the captured
    output as a string.
    """

    def __init__(self, settings: GlobalSettings):
        self._settings = settings

    def submit_job(
        self,
        *,
        repo_path: str,
        workflow: WorkflowEntry,
        input_artifacts: dict[str, str] | None = None,
        worker_id: str | None = None,
    ) -> str:
        """Submit a workflow run to the backend queue.

        Parameters
        ----------
        repo_path :
            Working directory for the invocation.
        workflow :
            The workflow entry to submit.
        input_artifacts :
            Optional dict of ``{KEY: VALUE}`` pairs passed as ``--input`` flags.
        worker_id :
            Override worker ID. Falls back to global settings if not provided.
        """
        args = ["--workflow-name", workflow.workflow_name]
        args.extend(["--backend-url", self._settings.backend_url])
        effective_worker_id = worker_id or self._settings.worker_id
        if effective_worker_id:
            args.extend(["--worker-id", effective_worker_id])
        if self._settings.worker_label:
            args.extend(["--worker-label", self._settings.worker_label])
        if input_artifacts:
            for key, value in input_artifacts.items():
                args.extend(["--input", f"{key}={value}"])
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
        args.extend(["--backend-url", self._settings.backend_url])
        return self._invoke(repo_path=repo_path, func=sync_workflows.main, argv=args)

    def cleanup_execution(self, *, workflow_name: str, dry_run: bool = False) -> str:
        """Delete execution records from the backend."""
        import json
        client = BackendClient(self._settings.backend_url)
        result = client.cleanup_execution(workflow_name=workflow_name, dry_run=dry_run)
        return json.dumps(result, indent=2)

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
        """Execute a CLI function in-process with captured stdout/stderr.

        Changes the working directory to *repo_path*, redirects stdout and
        stderr, calls *func(argv)*, and returns the captured output.  Raises
        ``ActionExecutionError`` on non-zero exit or exception.
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
