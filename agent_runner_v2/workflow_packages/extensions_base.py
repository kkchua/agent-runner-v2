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
