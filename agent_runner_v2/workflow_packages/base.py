from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StepConfig:
    """Canonical, validated step configuration from a workflow.toml manifest."""

    name: str
    prompt_file: str | None = None
    action: str | None = None
    mode: str | None = None

    # Artifact contract
    produces: list[str] = field(default_factory=list)
    required_inputs: list[str] = field(default_factory=list)
    optional_inputs: list[str] = field(default_factory=list)
    result_meta_key: str | None = None
    result_meta_key_from_context: str | None = None
    target_artifact: str | None = None
    edit_mode: str | None = None
    immutable_inputs: list[str] = field(default_factory=list)
    produced_document_status: dict[str, Any] | None = None

    # Coder configuration
    coder_default: str | None = None
    coder_allowed: list[str] = field(default_factory=list)
    coder_must_differ: bool = False

    # Routing
    on_approve: str | None = None
    on_reject_refine: dict[str, Any] | None = None
    on_exhaust_replan: dict[str, Any] | None = None
    reject_code_routes: dict[str, Any] | None = None

    # Review gating
    requires_human_approval_after: bool = False
    loop_returns_to: str | None = None
    replan_returns_to: str | None = None

    # Behaviour flags
    enable_notifications: bool = False

    # Template conformance (for generated documents)
    template_ref: dict[str, Any] | None = None

    # Post-action hook (e.g. "generate_site_pdf" after LLM step)
    post_action: str | None = None

    # Pass-through for any unrecognised fields (preserves forward compat)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkflowBundle:
    """A fully loaded, validated workflow package ready for execution."""

    name: str
    version: str
    label: str
    job_prefix: str

    manifest_path: Path
    bundle_root: Path

    steps: dict[str, StepConfig]
    step_order: list[str]

    init_step: str
    init_inputs: list[str]
    default_max_rejects: int = 3

    # Optional custom context extension module path (loaded via importlib at runtime)
    context_extensions_path: Path | None = None

    # Metadata
    description: str = ""
    visibility: str = ""

    def get_step(self, name: str) -> StepConfig:
        """Look up a step by name. Raises KeyError if missing."""
        return self.steps[name]

    def next_step(self, current: str) -> str | None:
        """Return the next step in the ordered list, or None."""
        try:
            idx = self.step_order.index(current)
            if idx + 1 < len(self.step_order):
                return self.step_order[idx + 1]
            return None
        except ValueError:
            return None
