from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GovernanceExtension:
    """Optional bundle governance extension content."""

    name: str
    source_path: Path
    targets: list[str] = field(default_factory=list)
    enabled: bool = True
    required: bool = False
    description: str = ""


@dataclass(frozen=True)
class GovernanceArtifact:
    """Artifact registry entry owned or referenced by bundle governance."""

    key: str
    path: str
    description: str = ""
    required: bool = True


@dataclass(frozen=True)
class BundleGovernance:
    """Canonical governance contract carried with a workflow bundle."""

    manifest_path: Path
    canonical_source_path: Path
    generated_dir: Path
    adapter_targets: list[str] = field(default_factory=list)
    include_in_prompts: bool = False
    prompt_targets: list[str] = field(default_factory=list)
    extensions: list[GovernanceExtension] = field(default_factory=list)
    artifact_registry: list[GovernanceArtifact] = field(default_factory=list)


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
    coder_role_policy: str | None = None
    coder_default_role: str | None = None
    coder_allowed_roles: list[str] = field(default_factory=list)
    coder_must_differ: bool = False

    # Routing
    on_approve: str | None = None
    on_reject_refine: dict[str, Any] | None = None
    reject_code_routes: dict[str, Any] | None = None

    # Review gating
    requires_human_approval_after: bool = False

    # Behaviour flags
    enable_notifications: bool = False

    # Template conformance (for generated documents)
    template_ref: dict[str, Any] | None = None

    # Post-action hook (e.g. "generate_site_pdf" after LLM step)
    post_action: str | None = None

    # Prompt Slot ID (for dynamic prompt resolution via impl.yaml)
    prompt_slot_id: str | None = None

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

    # Optional bundle-level governance contract and generated adapters
    governance: BundleGovernance | None = None

    # Package-local actions registered via @action() decorator
    custom_actions: dict[str, Any] = field(default_factory=dict)

    # Metadata
    description: str = ""
    visibility: str = ""

    # Alternative implementation declarations from [[workflow.implementation]]
    implementations: list[dict[str, str]] = field(default_factory=list)

    # Prompt slot definitions from the active implementation (impl.yaml)
    # Maps slot_id -> {label, default, options: [{name, file, description}]}
    impl_prompt_slots: dict[str, Any] = field(default_factory=dict)

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
