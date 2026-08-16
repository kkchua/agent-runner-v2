"""Base class for workflow plugin lifecycle hooks.

Every workflow package must have a ``context_extensions.py`` module that
defines a :class:`WorkflowExtensions` subclass.  The runner's scanner
(:mod:`workflow_packages.hooks`) discovers these subclasses and invokes
their hook methods at the appropriate lifecycle points.

Unoverridden methods are safe no-ops, so a workflow only implements the
hooks it needs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..runtime_context import (
  get_runner_home, 
  get_workflow_root
)


class WorkflowExtensions:
    """Base class for workflow plugin lifecycle hooks.

    Subclass this in your workflow's ``context_extensions.py`` and
    override the methods your workflow needs.  The scanner discovers
    the subclass automatically — no registration required.

    Attributes:
        workflow_name: The workflow package name (must match the
            directory name, e.g. ``"sdlc_10_requirement_v1"``).
    """

    workflow_name: str = ""

    # ------------------------------------------------------------------
    # Artifact path registration
    # ------------------------------------------------------------------

    def register_artifact_keys(
        self,
        *,
        job_id: str = "{job_id}",
        mode: str = "{mode}",
    ) -> dict[str, str]:
        """Return artifact key to relative-path mappings.

        Called during workflow startup to populate the global
        ``ARTIFACT_PATHS`` registry.  Paths may contain ``{job_id}``
        and ``{slug}`` placeholders that are resolved at runtime.

        Returns:
            Dict mapping artifact key strings to repo-relative path
            templates.
        """
        return {}

    # ------------------------------------------------------------------
    # Prompt context injection
    # ------------------------------------------------------------------

    def build_context_extensions(
        self,
        *,
        state: dict[str, Any],
        step: str,
        step_cfg: dict[str, Any],
        ctx: dict[str, str],
        project_root: Path | None = None,
    ) -> dict[str, str]:
        """Return additional context variables for prompt rendering.

        Called before each step's prompt template is rendered.  Use
        this to inject absolute artifact paths, governance roots, and
        any other context the prompt templates need.

        Returns:
            Dict of context-variable name to value strings.  These are
            merged into the prompt rendering context.
        """
        return {}

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def init(
        self,
        *,
        workspace_root: Path,
        runner_home: Path,
    ) -> None:
        """One-time initialization when ``ukbe-run-agent init`` runs.

        Use this to install workflow artifacts to the global runner
        home, seed configuration, or perform any setup that must
        happen once per environment.
        """
        pass

    # ------------------------------------------------------------------
    # Installation and sync
    # ------------------------------------------------------------------

    def install_to_global(
        self,
        *,
        workspace_root: Path,
        runner_home: Path,
    ) -> dict[str, Any]:
        """Install workflow files to the global runner home.

        Called by ``ukbe-run-agent init`` and ``ukbe-run-agent install``
        to copy workflow-specific artifacts (templates, contracts,
        governance docs) to the global runner home directory.

        Returns:
            Dict with at least a ``"status"`` key:
            ``"INSTALLED"`` if files were copied,
            ``"SKIPPED"`` if prerequisites are missing,
            ``"NO_OP"`` if this workflow has nothing to install.
        """
        return {"status": "NO_OP"}

    def sync_to_backend(
        self,
        *,
        workspace_root: Path,
    ) -> dict[str, Any]:
        """Sync workflow definition to the backend registry.

        Called by ``ukbe-run-agent sync-workflows`` and
        ``ukbe-run-agent install`` to register the workflow's step
        definitions, artifact types, and routing rules with the
        backend database.

        Returns:
            Dict with at least a ``"status"`` key:
            ``"SYNCED"`` if the definition was posted,
            ``"SKIPPED"`` if no backend is configured,
            ``"NO_OP"`` if this workflow does not sync.
        """
        return {"status": "NO_OP"}


def resolve_input_specs(
    result: dict[str, str],
    state: dict[str, Any],
    workflow_name: str,
    spec_keys: list[str],
) -> None:
    """Deprecated: use resolve_input_artifacts() instead.

    Kept for backward compatibility with existing workflows that still
    call this function.  New workflows MUST use the two-dict pattern
    with resolve_input_artifacts() and resolve_output_artifacts().
    """
    specs_dir = get_runner_home() / "workflows" / "default" / workflow_name / "Specs"

    artifacts = state.get("artifacts") or {}

    for key in spec_keys:
        value = artifacts.get(key)

        if not value or not value.strip():
            resolved = str(specs_dir / "default_spec.md")
            result[key] = resolved
            artifacts[key] = resolved
            continue

        filename = Path(value).name
        resolved = str(specs_dir / filename)
        result[key] = resolved
        artifacts[key] = resolved


def resolve_input_artifacts(
    result: dict[str, str],
    state: dict[str, Any],
    workspace_root: Path,
    input_artifacts: dict[str, str],
) -> None:
    """Resolve input artifact keys to ``{workspace_root}/input/`` paths.

    Universal input resolver for the two-dict pattern.  Every workflow
    MUST call this from ``build_context_extensions()`` to resolve its
    input artifact keys.

    Resolution rules:
    - If the artifact value in state is a non-empty string, extract the
      filename and resolve to ``input/{filename}``.
    - If the value is empty/blank and the dict entry is non-empty, use
      the dict entry as the default filename.
    - If both are empty, set the result to an empty string (optional
      artifact — the step may handle absence gracefully).

    Args:
        result: The context extensions dict being built. Modified in place.
        state: Job state dict containing ``artifacts``.
        workspace_root: The workspace root path (job execution root).
        input_artifacts: Class-level INPUT_ARTIFACTS dict mapping
            artifact keys to default filenames (or "" for no default).
    """
    input_dir = Path(workspace_root) / "input"
    artifacts = state.get("artifacts") or {}

    for key, default_name in input_artifacts.items():
        value = artifacts.get(key, "")

        if value and value.strip():
            filename = Path(value).name
        elif default_name:
            filename = default_name
        else:
            result[key] = ""
            continue

        resolved = str(input_dir / filename)
        result[key] = resolved
        artifacts[key] = resolved


def resolve_output_artifacts(
    result: dict[str, str],
    state: dict[str, Any],
    workspace_root: Path,
    output_artifacts: dict[str, str],
) -> None:
    """Resolve output artifact keys to ``{workspace_root}/output/{job_id}/`` paths.

    Universal output resolver for the two-dict pattern.  Every workflow
    MUST call this from ``build_context_extensions()`` to resolve its
    output artifact keys.

    Each pattern may contain ``{seq}`` which is replaced with the
    current sequence number from state (``state["seq"]``, defaulting
    to ``"001"``).

    Args:
        result: The context extensions dict being built. Modified in place.
        state: Job state dict containing ``job_id`` and ``seq``.
        workspace_root: The workspace root path (job execution root).
        output_artifacts: Class-level OUTPUT_ARTIFACTS dict mapping
            artifact keys to filename patterns.
    """
    job_id = str(state.get("job_id") or "unknown")
    seq = str(state.get("seq") or "001").zfill(3)
    output_dir = Path(workspace_root) / "output" / job_id

    for key, pattern in output_artifacts.items():
        resolved_name = pattern.replace("{seq}", seq)
        result[key] = str(output_dir / resolved_name)
