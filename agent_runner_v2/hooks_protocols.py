"""Protocol definitions for hook interfaces to enable type-safe dependency injection.

This module defines Protocol types that replace the opaque `hooks: Any` pattern
used throughout the codebase. These protocols enable:

1. Type checking of hook usage
2. Clearer dependency documentation
3. Easier testing through mock implementations
4. Safer refactoring

Usage:
    from .hooks_protocols import StepExecutionHooks, ArtifactHooks

    def prepare_step(..., hooks: StepExecutionHooks) -> None:
        missing = hooks.missing_artifacts(keys, state)  # Type-safe!
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ArtifactHooks(Protocol):
    """Protocol for artifact-related operations."""

    def missing_artifacts(self, keys: list[str], state: dict[str, Any]) -> list[str]:
        """Return list of artifact keys that are missing from state."""
        ...


@runtime_checkable
class WorkflowHooks(Protocol):
    """Protocol for workflow configuration operations."""

    def build_group_cfg_from_execution_spec(
        self,
        spec: dict[str, Any],
        template_group: str,
        step_name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Build group and step config from execution spec."""
        ...


@runtime_checkable
class CoderHooks(Protocol):
    """Protocol for coder resolution operations."""

    def resolve_step_coder(
        self,
        *,
        group_cfg: dict[str, Any],
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        cli_coder: str | None,
    ) -> tuple[str, dict[str, Any]] | tuple[str, str | None, str | None, dict[str, Any]]:
        """Resolve the coder for a step.

        Returns:
            Either (coder_used, coder_config) or
            (coder_used, coder_alias, coder_role, coder_config)
        """
        ...


@runtime_checkable
class StepExecutionHooks(Protocol):
    """Combined protocol for step execution operations.

    This is the primary interface used by step_execution_runtime functions.
    """

    # Artifact operations
    def _missing_artifacts(self, keys: list[str], state: dict[str, Any]) -> list[str]:
        """Return list of artifact keys that are missing from state."""
        ...

    def missing_artifacts(self, keys: list[str], state: dict[str, Any]) -> list[str]:
        """Return list of artifact keys that are missing from state."""
        ...

    # Job state operations
    def check_preflight_artifact_status(
        self, *, step_cfg: dict[str, Any], state: dict[str, Any]
    ) -> None:
        """Check preflight artifact status."""
        ...

    def ensure_planning_task_queue_integrity(
        self, state: dict[str, Any], step: str
    ) -> None:
        """Ensure planning task queue integrity."""
        ...

    def ensure_execution_task_binding_integrity(
        self, state: dict[str, Any], step: str
    ) -> None:
        """Ensure execution task binding integrity."""
        ...

    def make_step_dir(
        self, group_cfg: dict[str, Any], state: dict[str, Any], step: str
    ) -> Path:
        """Create and return step directory."""
        ...

    # Step runner operations
    def build_context(
        self,
        state: dict[str, Any],
        *,
        step: str,
        step_cfg: dict[str, Any],
        project_root: Path,
    ) -> dict[str, str]:
        """Build context dictionary for prompt rendering."""
        ...

    def resolve_prompt_path(
        self, *, step_cfg: dict[str, Any], coder: str, model_id: str | None
    ) -> Path:
        """Resolve prompt file path."""
        ...

    def render_prompt(
        self, template: str, context: dict[str, str], *, step_cfg: dict[str, Any]
    ) -> str:
        """Render prompt template with context."""
        ...

    def prompt_checksum(self, text: str) -> str:
        """Calculate checksum for prompt text."""
        ...

    def _save_text(self, path: Path, text: str) -> None:
        """Save text to file."""
        ...

    def run_action(
        self,
        *,
        action_name: str,
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        step_dir: Path,
        project_root: Path,
        context: dict[str, str],
    ) -> Any:
        """Run an action."""
        ...

    def run_step(
        self,
        *,
        group_name: str,
        group_cfg: dict[str, Any],
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        coder: str,
        coder_config: dict[str, Any] | None,
        prompt_text: str,
        checksum: str,
        step_dir: Path,
        project_root: Path,
        context: dict[str, str],
    ) -> Any:
        """Run a step with coder."""
        ...

    # Coder operations
    def _resolve_step_coder(
        self,
        *,
        group_cfg: dict[str, Any],
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        cli_coder: str | None,
    ) -> tuple[str, dict[str, Any]] | tuple[str, str | None, str | None, dict[str, Any]]:
        """Resolve the coder for a step."""
        ...

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
        ...

    # Workflow config operations
    def build_group_cfg_from_execution_spec(
        self,
        spec: dict[str, Any],
        template_group: str,
        step_name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Build group and step config from execution spec."""
        ...

    def prepare_step_execution(
        self,
        *,
        template_group: str,
        group_cfg: dict[str, Any],
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        project_root: Path,
        workflow_key_override: str,
        cli_coder: str | None,
        hooks: Any,  # Self-reference for nested calls
    ) -> Any:
        """Prepare a step for execution."""
        ...


@runtime_checkable
class ExecutionHooks(Protocol):
    """Protocol for execution-related operations."""

    def invoke_prepared_step(self, prepared: Any) -> Any:
        """Invoke a prepared step."""
        ...


@runtime_checkable
class JobHooks(Protocol):
    """Protocol for job state operations."""

    def load_job(self, job_id: str, project_root: Path) -> dict[str, Any]:
        """Load job state."""
        ...

    def save_job(self, job_id: str, state: dict[str, Any], project_root: Path) -> None:
        """Save job state."""
        ...


@runtime_checkable
class StepGuardrails(Protocol):
    """Protocol for step guardrail validation hooks.

    Workflows may optionally implement guardrails.py with pre_check and post_check
    functions to validate inputs before execution and outputs after execution.

    Both methods return a tuple of (is_valid, reject_reason, reject_code).
    When is_valid is False, the step is rejected immediately with the provided
    reason and code.
    """

    def pre_check(
        self,
        *,
        step: str,
        step_cfg: dict[str, Any],
        state: dict[str, Any],
        prepared: Any,
    ) -> tuple[bool, str | None, str | None]:
        """Validate inputs before step execution.

        Args:
            step: Current step name.
            step_cfg: Step configuration dict from workflow.toml.
            state: Current job state dict.
            prepared: PreparedStepExecution dataclass with execution context.

        Returns:
            Tuple of (is_valid, reject_reason_or_none, reject_code_or_none).
            If is_valid is False, reject_reason and reject_code must be provided.
        """
        ...

    def post_check(
        self,
        *,
        step: str,
        step_cfg: dict[str, Any],
        state: dict[str, Any],
        step_result: Any,
    ) -> tuple[bool, str | None, str | None]:
        """Validate outputs after step execution.

        Args:
            step: Current step name.
            step_cfg: Step configuration dict from workflow.toml.
            state: Current job state dict.
            step_result: StepResult dataclass with execution results.

        Returns:
            Tuple of (is_valid, reject_reason_or_none, reject_code_or_none).
            If is_valid is False, reject_reason and reject_code must be provided.
        """
        ...


@runtime_checkable
class BundleHooks(Protocol):
    """Protocol for bundle loading operations."""

    def load_project_config(self, workspace_root: Path) -> dict[str, Any]:
        """Load project configuration."""
        ...

    def load_workflow_module(
        self, workspace_root: Path, bundle_name: str, *, config: dict[str, Any] | None = None
    ) -> Any:
        """Load workflow module."""
        ...

    def resolve_workflow_root(
        self, workspace_root: Path, bundle_name: str, *, config: dict[str, Any] | None = None
    ) -> Path:
        """Resolve workflow root path."""
        ...
