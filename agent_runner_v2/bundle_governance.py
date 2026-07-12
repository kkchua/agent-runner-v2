from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .workflow_packages.base import (
    BundleGovernance,
    GovernanceArtifact,
    GovernanceExtension,
)


def load_bundle_governance(bundle_root: Path) -> BundleGovernance | None:
    manifest_path = bundle_root / "bundle_governance.toml"
    if not manifest_path.is_file():
        return None

    data = _load_toml(manifest_path)
    gov = data.get("governance")
    if not isinstance(gov, dict):
        raise ValueError(
            f"Expected [governance] section in {manifest_path}"
        )

    canonical_source = _require_str(gov, "canonical_source", manifest_path)
    generated_dir = gov.get("generated_dir", "bundle_governance/generated")
    include_in_prompts = bool(gov.get("include_in_prompts", False))
    adapter_targets = _coerce_str_list(gov.get("adapter_targets", ["AGENTS.md"]))
    prompt_targets = _coerce_str_list(gov.get("prompt_targets", ["all"]))

    canonical_source_path = (bundle_root / canonical_source).resolve()
    if not canonical_source_path.is_file():
        raise ValueError(
            f"Bundle governance canonical source does not exist: {canonical_source_path}"
        )

    generated_dir_path = (bundle_root / str(generated_dir)).resolve()
    extensions = _parse_extensions(
        data.get("extension", []),
        bundle_root=bundle_root,
        manifest_path=manifest_path,
    )
    artifact_registry = _parse_artifacts(
        data.get("artifact", []),
        manifest_path=manifest_path,
    )

    return BundleGovernance(
        manifest_path=manifest_path.resolve(),
        canonical_source_path=canonical_source_path,
        generated_dir=generated_dir_path,
        adapter_targets=adapter_targets,
        include_in_prompts=include_in_prompts,
        prompt_targets=prompt_targets,
        extensions=extensions,
        artifact_registry=artifact_registry,
    )


def render_bundle_governance_target(
    governance: BundleGovernance,
    *,
    bundle_name: str,
    bundle_label: str,
    target: str,
) -> str:
    canonical_text = governance.canonical_source_path.read_text(encoding="utf-8").strip()
    lines = [
        f"# {target}",
        "",
        "<!-- Generated from bundle_governance.toml. Edit the canonical source instead. -->",
        "",
        f"- Bundle: `{bundle_name}`",
        f"- Label: {bundle_label}",
        f"- Canonical source: `{_safe_rel(governance.canonical_source_path, governance.manifest_path.parent)}`",
    ]
    if governance.manifest_path.is_file():
        lines.append(
            f"- Governance manifest: `{_safe_rel(governance.manifest_path, governance.manifest_path.parent)}`"
        )
    lines.extend([
        "",
        "## Canonical Guidance",
        "",
        canonical_text,
    ])

    extension_blocks = _render_extension_blocks(governance, target=target)
    if extension_blocks:
        lines.extend(["", "## Enabled Extensions", ""])
        lines.extend(extension_blocks)

    artifact_table = _render_artifact_registry(governance)
    if artifact_table:
        lines.extend(["", "## Artifact Registry", ""])
        lines.extend(artifact_table)

    lines.append("")
    return "\n".join(lines)


def render_prompt_governance_block(
    governance: BundleGovernance,
    *,
    bundle_name: str,
    bundle_label: str,
    step_name: str,
) -> str:
    lines = [
        "",
        "",
        "## Bundle Governance",
        "",
        f"This step belongs to workflow bundle `{bundle_name}` ({bundle_label}).",
        "Follow the canonical bundle governance contract below. If any local prompt text conflicts with this contract, the governance contract wins.",
        f"Current step: `{step_name}`",
        "",
        governance.canonical_source_path.read_text(encoding="utf-8").strip(),
    ]

    extension_blocks = _render_extension_blocks(governance, target="prompt")
    if extension_blocks:
        lines.extend(["", "### Active Governance Extensions", ""])
        lines.extend(extension_blocks)

    artifact_table = _render_artifact_registry(governance)
    if artifact_table:
        lines.extend(["", "### Workflow Artifact Registry", ""])
        lines.extend(artifact_table)

    return "\n".join(lines)


def generate_bundle_governance_adapters(
    governance: BundleGovernance,
    *,
    bundle_name: str,
    bundle_label: str,
) -> dict[str, Path]:
    governance.generated_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for target in governance.adapter_targets:
        target_path = governance.generated_dir / target
        content = render_bundle_governance_target(
            governance,
            bundle_name=bundle_name,
            bundle_label=bundle_label,
            target=target,
        )
        target_path.write_text(content, encoding="utf-8")
        written[target] = target_path
    return written


def bundle_governance_summary(governance: BundleGovernance) -> dict[str, Any]:
    return {
        "manifest_path": str(governance.manifest_path),
        "canonical_source_path": str(governance.canonical_source_path),
        "generated_dir": str(governance.generated_dir),
        "adapter_targets": list(governance.adapter_targets),
        "include_in_prompts": governance.include_in_prompts,
        "prompt_targets": list(governance.prompt_targets),
        "extensions": [asdict(item) for item in governance.extensions],
        "artifact_registry": [asdict(item) for item in governance.artifact_registry],
    }


def _render_extension_blocks(governance: BundleGovernance, *, target: str) -> list[str]:
    lines: list[str] = []
    for extension in governance.extensions:
        if not extension.enabled:
            continue
        targets = extension.targets or ["all"]
        if "all" not in targets and target not in targets:
            continue
        text = extension.source_path.read_text(encoding="utf-8").strip()
        lines.extend([f"### {extension.name}", "", text, ""])
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def _render_artifact_registry(governance: BundleGovernance) -> list[str]:
    if not governance.artifact_registry:
        return []
    lines = [
        "| Artifact Key | Required | Path | Description |",
        "|---|---|---|---|",
    ]
    for artifact in governance.artifact_registry:
        required = "yes" if artifact.required else "no"
        description = artifact.description.replace("\n", " ").strip()
        lines.append(
            f"| `{artifact.key}` | {required} | `{artifact.path}` | {description} |"
        )
    return lines


def _parse_extensions(
    raw_extensions: Any,
    *,
    bundle_root: Path,
    manifest_path: Path,
) -> list[GovernanceExtension]:
    if raw_extensions is None:
        return []
    if not isinstance(raw_extensions, list):
        raise ValueError(
            f"Expected [[extension]] entries in {manifest_path}"
        )
    extensions: list[GovernanceExtension] = []
    for idx, item in enumerate(raw_extensions):
        if not isinstance(item, dict):
            raise ValueError(
                f"Extension entry {idx} in {manifest_path} must be a table"
            )
        name = _require_str(item, "name", manifest_path)
        source = _require_str(item, "source", manifest_path)
        source_path = (bundle_root / source).resolve()
        if not source_path.is_file():
            raise ValueError(
                f"Bundle governance extension source does not exist: {source_path}"
            )
        extensions.append(
            GovernanceExtension(
                name=name,
                source_path=source_path,
                targets=_coerce_str_list(item.get("targets", ["all"])),
                enabled=bool(item.get("enabled", True)),
                required=bool(item.get("required", False)),
                description=str(item.get("description", "")),
            )
        )
    return extensions


def _parse_artifacts(raw_artifacts: Any, *, manifest_path: Path) -> list[GovernanceArtifact]:
    if raw_artifacts is None:
        return []
    if not isinstance(raw_artifacts, list):
        raise ValueError(
            f"Expected [[artifact]] entries in {manifest_path}"
        )
    artifacts: list[GovernanceArtifact] = []
    for idx, item in enumerate(raw_artifacts):
        if not isinstance(item, dict):
            raise ValueError(
                f"Artifact entry {idx} in {manifest_path} must be a table"
            )
        artifacts.append(
            GovernanceArtifact(
                key=_require_str(item, "key", manifest_path),
                path=_require_str(item, "path", manifest_path),
                description=str(item.get("description", "")),
                required=bool(item.get("required", True)),
            )
        )
    return artifacts


def _coerce_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _require_str(data: dict[str, Any], key: str, manifest_path: Path) -> str:
    value = data.get(key)
    if value is None or str(value).strip() == "":
        raise ValueError(
            f"Missing required string field '{key}' in {manifest_path}"
        )
    return str(value)


def _load_toml(path: Path) -> dict[str, Any]:
    import sys

    if sys.version_info >= (3, 11):
        import tomllib
    else:
        try:
            import tomli as tomllib  # type: ignore[no-redef]
        except ImportError as exc:
            raise ImportError(
                "No TOML library available. Install tomli for Python < 3.11."
            ) from exc
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _safe_rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)
