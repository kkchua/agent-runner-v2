"""Runtime hooks implementation with lazy module loading.

This module provides a type-safe replacement for the deferred import pattern
used in shared_runtime_deps.py and manual_runtime_deps.py. It implements
the protocols defined in hooks_protocols.py using lazy module loading to
avoid circular imports.

Usage:
    from .runtime_hooks import RuntimeHooks
    hooks = RuntimeHooks()
    missing = hooks.missing_artifacts(keys, state)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .hooks_protocols import (
    ArtifactHooks,
    BundleHooks,
    CoderHooks,
    DaemonHooks,
    ExecutionHooks,
    JobHooks,
    StepExecutionHooks,
    WorkflowHooks,
)


class RuntimeHooks:
    """Central hook implementation with lazy module loading.

    This class implements all hook protocols using lazy module loading
    to avoid circular imports at initialization time. Modules are only
    imported when their methods are first called.

    This replaces the pattern:
        from . import workflow_runtime as _workflow_runtime
        def _missing_artifacts(...):
            return _workflow_runtime.missing_artifacts(...)

    With:
        hooks = RuntimeHooks()
        hooks.missing_artifacts(...)
    """

    # Module caches for lazy loading
    _workflow_runtime: Any = None
    _step_execution_runtime: Any = None
    _daemon_runtime: Any = None
    _backend_execution: Any = None
    _execution_core: Any = None
    _job_state: Any = None
    _bundle_loader: Any = None

    def _get_workflow_runtime(self) -> Any:
        if self._workflow_runtime is None:
            from . import workflow_runtime
            self._workflow_runtime = workflow_runtime
        return self._workflow_runtime

    def _get_step_execution_runtime(self) -> Any:
        if self._step_execution_runtime is None:
            from . import step_execution_runtime
            self._step_execution_runtime = step_execution_runtime
        return self._step_execution_runtime

    def _get_daemon_runtime(self) -> Any:
        if self._daemon_runtime is None:
            from . import daemon_runtime
            self._daemon_runtime = daemon_runtime
        return self._daemon_runtime

    def _get_backend_execution(self) -> Any:
        if self._backend_execution is None:
            from . import backend_execution
            self._backend_execution = backend_execution
        return self._backend_execution

    def _get_execution_core(self) -> Any:
        if self._execution_core is None:
            from . import execution_core
            self._execution_core = execution_core
        return self._execution_core

    def _get_job_state(self) -> Any:
        if self._job_state is None:
            from . import job_state
            self._job_state = job_state
        return self._job_state

    def _get_bundle_loader(self) -> Any:
        if self._bundle_loader is None:
            from . import bundle_loader
            self._bundle_loader = bundle_loader
        return self._bundle_loader

    # =================================================================
    # ArtifactHooks Implementation
    # =================================================================

    def missing_artifacts(self, keys: list[str], state: dict[str, Any]) -> list[str]:
        """Return list of artifact keys that are missing from state."""
        return self._get_workflow_runtime().missing_artifacts(keys, state)

    # =================================================================
    # WorkflowHooks Implementation
    # =================================================================

    def build_group_cfg_from_execution_spec(
        self,
        spec: dict[str, Any],
        template_group: str,
        step_name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Build group and step config from execution spec."""
        return self._get_backend_execution().build_group_cfg_from_execution_spec(
            spec, template_group, step_name
        )

    # =================================================================
    # CoderHooks Implementation
    # =================================================================

    def resolve_step_coder(
        self,
        *,
        group_cfg: dict[str, Any],
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        cli_coder: str | None,
    ) -> tuple[str, dict[str, Any]] | tuple[str, str | None, str | None, dict[str, Any]]:
        """Resolve the coder for a step."""
        return self._get_step_execution_runtime().resolve_step_coder(
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            cli_coder=cli_coder,
        )

    # =================================================================
    # StepExecutionHooks Implementation
    # =================================================================

    def prepare_step_execution(
        self,
        *,
        template_group: str,
        group_cfg: dict[str, Any],
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        project_root: Path,
        workflow_key_override: str = "",
        cli_coder: str | None = None,
        hooks: Any = None,
    ) -> Any:
        """Prepare a step for execution."""
        # Pass self as hooks if not provided
        effective_hooks = hooks if hooks is not None else self
        return self._get_step_execution_runtime().prepare_step_execution(
            template_group=template_group,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            project_root=project_root,
            workflow_key_override=workflow_key_override,
            cli_coder=cli_coder,
            hooks=effective_hooks,
        )

    def execute_prepared_step(
        self,
        *,
        prepared: Any,
        template_group: str,
        group_cfg: dict[str, Any],
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        effective_root: Path,
        hooks: Any = None,
    ) -> Any:
        """Execute a prepared step."""
        effective_hooks = hooks if hooks is not None else self
        return self._get_step_execution_runtime().execute_prepared_step(
            prepared=prepared,
            template_group=template_group,
            group_cfg=group_cfg,
            state=state,
            step=step,
            step_cfg=step_cfg,
            effective_root=effective_root,
            hooks=effective_hooks,
        )

    # =================================================================
    # DaemonHooks Implementation
    # =================================================================

    def resolve_worker_engine_root(self, engine_root: str | None) -> tuple[str | None, str | None]:
        """Resolve worker engine root path and name."""
        return self._get_daemon_runtime().resolve_worker_engine_root(engine_root)

    def build_worker_crash_result(
        self,
        *,
        run: dict[str, Any],
        step_run: dict[str, Any],
        error: Exception,
    ) -> dict[str, Any]:
        """Build error result for worker crash."""
        return self._get_daemon_runtime().build_worker_crash_result(
            run=run,
            step_run=step_run,
            error=error,
            hooks=self,
        )

    def build_worker_request_payload(
        self,
        *,
        run: dict[str, Any],
        step_run: dict[str, Any],
        step_execution_spec: dict[str, Any] | None = None,
        backend_url: str = "",
        step_spec_source: str = "backend",
    ) -> dict[str, Any]:
        """Build payload for worker request."""
        return self._get_daemon_runtime().build_worker_request_payload(
            run=run,
            step_run=step_run,
            step_execution_spec=step_execution_spec,
            backend_url=backend_url,
            step_spec_source=step_spec_source,
            hooks=self,
        )

    # =================================================================
    # ExecutionHooks Implementation
    # =================================================================

    def invoke_prepared_step(self, prepared: Any) -> Any:
        """Invoke a prepared step."""
        return self._get_execution_core().invoke_prepared_step(prepared)

    # =================================================================
    # JobHooks Implementation
    # =================================================================

    def load_job(self, job_id: str, project_root: Path) -> dict[str, Any]:
        """Load job state."""
        return self._get_job_state().load_job(job_id, project_root)

    def save_job(self, job_id: str, state: dict[str, Any], project_root: Path) -> None:
        """Save job state."""
        return self._get_job_state().save_job(job_id, state, project_root)

    # =================================================================
    # BundleHooks Implementation
    # =================================================================

    def load_project_config(self, workspace_root: Path) -> dict[str, Any]:
        """Load project configuration."""
        return self._get_bundle_loader().load_project_config(workspace_root)

    def load_workflow_module(
        self, workspace_root: Path, bundle_name: str, *, config: dict[str, Any] | None = None
    ) -> Any:
        """Load workflow module."""
        return self._get_bundle_loader().load_workflow_module(
            workspace_root, bundle_name, config=config
        )

    def resolve_workflow_root(
        self, workspace_root: Path, bundle_name: str, *, config: dict[str, Any] | None = None
    ) -> Path:
        """Resolve workflow root path."""
        return self._get_bundle_loader().resolve_workflow_root(
            workspace_root, bundle_name, config=config
        )

    # =================================================================
    # Additional Shared Runtime Functions
    # =================================================================

    def ensure_delivery_folders(self, target_root: Path) -> None:
        """Ensure delivery folders exist."""
        return self._get_workflow_runtime().ensure_delivery_folders(target_root)

    def load_group(
        self,
        group_name: str,
        workspace_root: Path | None = None,
        workflow_root: Path | None = None,
    ) -> dict[str, Any]:
        """Load workflow group configuration."""
        return self._get_workflow_runtime().load_group(
            group_name,
            workspace_root=workspace_root,
            workflow_root=workflow_root,
        )

    def validate_static_reference_files(
        self,
        workspace_root: Path,
        group_cfg: dict[str, Any] | None = None,
        template_group: str = "",
    ) -> None:
        """Validate static reference files."""
        return self._get_workflow_runtime().validate_static_reference_files(
            workspace_root,
            group_cfg=group_cfg,
            template_group=template_group,
        )


class ManualHooks:
    """Hooks implementation for manual mode operations.

    This class provides the hook implementations previously found in
    manual_runtime_deps.py. It uses lazy loading to avoid circular imports.
    """

    _workflow_runtime: Any = None
    _cli_runtime: Any = None
    _failure_runtime: Any = None
    _job_state: Any = None
    _state_defaults: Any = None
    _task_runtime: Any = None

    def _get_workflow_runtime(self) -> Any:
        if self._workflow_runtime is None:
            from . import workflow_runtime
            self._workflow_runtime = workflow_runtime
        return self._workflow_runtime

    def _get_cli_runtime(self) -> Any:
        if self._cli_runtime is None:
            from . import cli_runtime
            self._cli_runtime = cli_runtime
        return self._cli_runtime

    def _get_failure_runtime(self) -> Any:
        if self._failure_runtime is None:
            from . import failure_runtime
            self._failure_runtime = failure_runtime
        return self._failure_runtime

    def _get_job_state(self) -> Any:
        if self._job_state is None:
            from . import job_state
            self._job_state = job_state
        return self._job_state

    def _get_state_defaults(self) -> Any:
        if self._state_defaults is None:
            from . import state_defaults
            self._state_defaults = state_defaults
        return self._state_defaults

    def _get_task_runtime(self) -> Any:
        if self._task_runtime is None:
            from . import task_runtime
            self._task_runtime = task_runtime
        return self._task_runtime

    def missing_artifacts(self, keys: list[str], state: dict) -> list[str]:
        """Return list of missing artifact keys."""
        return self._get_workflow_runtime().missing_artifacts(keys, state)

    def parse_key_value_pairs(self, values: list[str]) -> dict[str, str]:
        """Parse key=value pairs into dict."""
        return self._get_workflow_runtime().parse_key_value_pairs(values)

    def step_progress_label(self, group_cfg: dict, step: str | None) -> str:
        """Get step progress label."""
        return self._get_cli_runtime().step_progress_label(group_cfg, step)

    def format_job_status_summary(self, state: dict, group_cfg: dict) -> str:
        """Format job status summary."""
        return self._get_cli_runtime().format_job_status_summary(
            state, group_cfg, get_job_status=self._get_job_state().get_job_status
        )

    def clear_last_failure(self, state: dict) -> None:
        """Clear last failure from state."""
        return self._get_failure_runtime().clear_last_failure(state)

    def default_loop_context(self) -> dict:
        """Return default loop context."""
        return self._get_state_defaults().default_loop_context()

    def default_replan_context(self) -> dict:
        """Return default replan context."""
        return self._get_state_defaults().default_replan_context()
