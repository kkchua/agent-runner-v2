"""Runner action service for the operator console.

Wraps CLI entry points so the console can invoke them in-process with
captured stdout/stderr. All operations go through the CLI — no direct
backend API calls.

Architecture: Console → CLI → Backend (CLI owns all backend communication).

All operations are triggered from the operator console. There is no
separate "local manual trigger" — the console is the single entry point
for all workflow management operations.

Method Categories:
------------------

OPERATOR CONSOLE ACTIONS (all triggered from console UI):

  Pure Backend Operations (no local job folder needed):
    These set flags/state in the backend DB. The daemon picks up changes
    and acts on them.

    - list_runs() / list_active_runs_for_worker() — Read runs from backend
    - show_run() / get_run_detail_dict() — Read run details from backend
    - submit_job() — Submit new workflow to backend queue
    - stop_run() — Request stop (sets flag in backend DB)
    - approve() — Approve/reject/resume/retry at backend level
    - reset_step() — Reset step at backend level

  Step-Level Interventions (require local job folder):
    These are also triggered from the console. They load local job.json,
    modify it, save it, then sync to backend. Used for step-level
    interventions when the operator needs to manually approve/reject/
    resume/retry a specific step.

    - approve_step() — Approve a specific step
    - reject_step() — Reject a specific step
    - resume_step() — Resume a waiting step
    - retry_step() — Retry a waiting step

  Daemon Actions (called by daemon, not console):
    - cancel_run() — Actually terminate a running job (daemon calls this
      when it detects a stop request from the console)

UTILITY ACTIONS (setup/admin operations, no daemon mapping):
    - init_workspace() — Seed workflow bundles to global runner home
    - bootstrap_publish() — Publish bootstrap bundles
    - sync_workflow() — Sync workflow definitions to backend

Console → Daemon Mapping:
-------------------------
Each console action that modifies state has a corresponding daemon
behavior that processes the change:

  Console Action          →  Backend DB          →  Daemon Behavior
  ----------------------     ------------------      -------------------------
  stop_run()             →  stop_requested flag  →  calls cancel_run()
  approve()              →  step status update   →  picks up next step
  reset_step()           →  current_step change  →  executes new step
  submit_job()           →  new run record       →  claims and executes
  approve_step()         →  step approved        →  continues execution
  reject_step()          →  step rejected        →  triggers refine loop
  resume_step()          →  step resumed         →  continues execution
  retry_step()           →  step retry           →  re-executes step

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
        """OPERATOR CONSOLE: List workflow runs from backend (read-only).

        Calls the 'list-runs' CLI command to fetch runs from backend.
        No state modification — pure read operation.
        """
        args = []
        if worker_id:
            args.extend(["--worker-id", worker_id])
        if status_group and status_group != "all":
            args.extend(["--status-group", status_group])
        if workflow_name:
            args.extend(["--workflow-name", workflow_name])
        return self._invoke_from_anywhere(func=list_runs_commands.main, argv=args)

    def list_active_runs_for_worker(self, *, worker_id: str = "") -> list[ActiveRunSummary]:
        """OPERATOR CONSOLE: List active runs for a worker (read-only).

        Calls the 'list-runs' CLI command to fetch runs from backend.
        No state modification — pure read operation.
        """
        json_str = self.list_runs(worker_id=worker_id, status_group="non_terminal")
        return _extract_runs_from_json(json_str)

    def show_run(self, *, run_id: str) -> str:
        """OPERATOR CONSOLE: Show a single run's details (read-only).

        Calls the 'show-run' CLI command to fetch run details from backend.
        No state modification — pure read operation.
        """
        return self._invoke_from_anywhere(
            func=show_run_commands.main, argv=[run_id],
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
        """OPERATOR CONSOLE: Request a backend run to stop.

        Calls the 'stop' CLI command which sets a stop flag in the backend DB.
        The daemon will detect this flag and terminate the job via --cancel-run.

        This is a "request to stop" — not an immediate termination.
        No local job folder needed — pure backend operation.
        """
        args = [run_id]
        if reason:
            args.extend(["--reason", reason])
        return self._invoke_from_anywhere(func=stop_commands.main, argv=args)

    def approve(
        self, *, run_id: str, reject: bool = False, feedback: str = "",
        resume: bool = False, retry: bool = False,
    ) -> str:
        """OPERATOR CONSOLE: Approve/reject/resume/retry at backend level.

        Calls the 'approve' CLI command which updates backend state directly.
        No local job folder needed — pure backend operation.

        The daemon will pick up the updated state and continue execution.
        """
        args = [run_id]
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
        """OPERATOR CONSOLE: Reset a run's current step at backend level.

        Calls the 'reset-step' CLI command which updates backend state directly.
        No local job folder needed — pure backend operation.

        The daemon will pick up the updated step and execute it.
        """
        return self._invoke_from_anywhere(
            func=reset_step_commands.main, argv=[run_id, step_name],
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
        """OPERATOR CONSOLE: Submit a workflow run to the backend queue.

        Calls the 'submit' CLI command which:
        1. Creates a new run record in backend DB
        2. Returns run_id and run_code for tracking

        The daemon will pick up the submitted job and execute it.
        No local job folder created until daemon starts execution.
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
        """UTILITY: Run ``ukbe-run-agent init`` to seed workflow bundles.

        Initializes the global runner home (~/.ukbe-runner) with workflow
        bundles, bootstrap docs, and configuration. No daemon mapping —
        this is a setup/admin operation.
        """
        args = [
            "init", "--workflow", workflow_name,
            "--bundle-domain", bundle_domain,
            "--bundle-profile", bundle_profile,
        ]
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=args)

    def bootstrap_publish(self, *, repo_path: str) -> str:
        """UTILITY: Run ``ukbe-run-agent bootstrap-publish`` to publish bootstrap bundles.

        Publishes bootstrap documentation and workflow bundles to the
        packaged location for distribution. No daemon mapping — this is
        a build/publish operation.
        """
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=["bootstrap-publish"])

    def sync_workflow(
        self, *, repo_path: str, workflow: WorkflowEntry | None = None,
    ) -> str:
        """UTILITY: Sync workflow definitions to the backend.

        Uploads workflow TOML definitions to the backend database so
        the daemon can execute them. No daemon mapping — this is an
        admin/setup operation.
        """
        args: list[str] = []
        if workflow is not None:
            args.append(workflow.workflow_name)
        return self._invoke(repo_path=repo_path, func=sync_workflows.main, argv=args)

    # ------------------------------------------------------------------
    # Step-Level Interventions (triggered from console, require local job folder)
    # These load local job.json, modify it, save it, then sync to backend.
    # ------------------------------------------------------------------

    def approve_step(
        self, *, repo_path: str, template_group: str,
        job_id: str, step_name: str,
    ) -> str:
        """OPERATOR CONSOLE: Approve a specific step in a running job.

        Triggered from console UI. Loads local job.json, marks step as
        human-approved, saves, and syncs to backend. Daemon continues
        execution on next poll.
        """
        args = [
            "run", "--template-group", template_group,
            "--job-id", job_id, "--approve-step", step_name,
        ]
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=args)

    def reject_step(
        self, *, repo_path: str, template_group: str,
        job_id: str, step_name: str,
    ) -> str:
        """OPERATOR CONSOLE: Reject a specific step in a running job.

        Triggered from console UI. Loads local job.json, marks step as
        rejected (triggers refine loop if configured), saves, and syncs
        to backend.
        """
        args = [
            "run", "--template-group", template_group,
            "--job-id", job_id, "--reject-step", step_name,
        ]
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=args)

    def resume_step(
        self, *, repo_path: str, template_group: str,
        job_id: str, step_name: str,
    ) -> str:
        """OPERATOR CONSOLE: Resume a step waiting for intervention or max-retried.

        Triggered from console UI. Loads local job.json, force-approves
        the step (user investigated and fixed issue), advances to next
        step, saves, and syncs to backend.
        """
        args = [
            "run", "--template-group", template_group,
            "--job-id", job_id, "--resume-step", step_name,
        ]
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=args)

    def retry_step(
        self, *, repo_path: str, template_group: str,
        job_id: str, step_name: str,
    ) -> str:
        """OPERATOR CONSOLE: Retry a step waiting for intervention or max-retried.

        Triggered from console UI. Loads local job.json, resets
        reject/failure count, re-executes the same step, saves, and
        syncs to backend.
        """
        args = [
            "run", "--template-group", template_group,
            "--job-id", job_id, "--retry-step", step_name,
        ]
        return self._invoke(repo_path=repo_path, func=run_agent.main, argv=args)

    def cancel_run(
        self, *, repo_path: str, template_group: str,
        job_id: str,
    ) -> str:
        """DAEMON: Actually terminate a running job now.

        Called by daemon (not console) when it detects a stop request.
        Loads local job.json, sets status to STOPPED, saves, and syncs
        to backend. This is the actual termination — the console's
        stop_run() only sets the flag that triggers this.
        """
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
