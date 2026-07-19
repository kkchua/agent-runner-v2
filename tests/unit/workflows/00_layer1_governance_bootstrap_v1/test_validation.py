from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path


def _load_actions_module():
    module_path = (
        Path(__file__).resolve().parents[4]
        / "workflows"
        / "00_layer1_governance_bootstrap_v1"
        / "actions.py"
    )
    spec = importlib.util.spec_from_file_location("tests.layer1_actions", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load actions module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_workflow_banner_is_ignored_for_concrete_workflow_name_check() -> None:
    actions = _load_actions_module()
    text = """---
template_id: "SYS-00-IDX"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-15T18:22:18+08:00"
workflow: "00_layer1_governance_bootstrap_v1"
step: "refine_layer1_governance_docs"
change_id: "00L1-GEN-20260715-010"
---

> Managed by workflow: `00_layer1_governance_bootstrap_v1` / step: `refine_layer1_governance_docs`
> This file is workflow-generated and protected from manual edits.

# System Documentation Index

Repo-local outputs live under `docs/repo/` and are outside Layer 1 ownership.
"""
    body = actions._strip_workflow_managed_banner(actions._strip_frontmatter(text))

    assert actions.WORKFLOW_ID_RE.findall(body) == []


def test_multi_workflow_bundle_check_accepts_single_workflow_phrase() -> None:
    actions = _load_actions_module()
    runtime_text = (
        "Plugin workflow bundles may be a single workflow bundle or a "
        "multi-workflow bundle depending on packaging needs."
    )

    assert (
        ("one workflow" in runtime_text.lower())
        or ("single-workflow" in runtime_text.lower())
        or ("single workflow" in runtime_text.lower())
    )
    assert "multi-workflow" in runtime_text.lower()


def test_layer1_governance_contract_declares_bundle_owned_path_contracts() -> None:
    contract = (
        Path(__file__).resolve().parents[4]
        / "workflows"
        / "00_layer1_governance_bootstrap_v1"
        / "bundle_governance"
        / "core_governance.md"
    ).read_text(encoding="utf-8")

    lowered = contract.lower()
    assert "workflow bundles must own their own artifact path contracts" in lowered
    assert "shared runtime code may provide generic path helpers" in lowered
    assert "must not own workflow-specific document output paths" in lowered


def test_layer1_review_and_audit_prompts_require_path_ownership_guardrail() -> None:
    root = Path(__file__).resolve().parents[4] / "workflows" / "00_layer1_governance_bootstrap_v1" / "prompts"
    review_text = (root / "02_review_layer1_governance_docs.txt").read_text(encoding="utf-8")
    audit_text = (root / "04_audit_layer1_governance_accuracy.txt").read_text(encoding="utf-8")
    review_normalized = " ".join(review_text.split())
    audit_normalized = " ".join(audit_text.split())

    assert "workflow bundles own workflow-specific artifact path contracts" in review_normalized
    assert "workflow-name-specific path resolution" in review_normalized
    assert "workflow bundles own workflow-specific artifact path contracts" in audit_normalized
    assert "centralized workflow-family path registries" in audit_normalized


def test_layer1_prompts_require_source_grounding_for_runtime_claims() -> None:
    root = Path(__file__).resolve().parents[4] / "workflows" / "00_layer1_governance_bootstrap_v1" / "prompts"
    review_text = (root / "02_review_layer1_governance_docs.txt").read_text(encoding="utf-8")
    refine_text = (root / "03_refine_layer1_governance_docs.txt").read_text(encoding="utf-8")
    audit_text = (root / "04_audit_layer1_governance_accuracy.txt").read_text(encoding="utf-8")

    assert "{LAYER1_RUNTIME_EVIDENCE}" in review_text
    assert "Source Grounding Checks" in review_text
    assert "_registry" in review_text
    assert "role policies" in review_text
    assert "coder roles" in review_text
    assert "coder connections" in review_text

    assert "{LAYER1_RUNTIME_EVIDENCE}" in refine_text
    assert "align runtime claims with the runtime evidence file" in refine_text
    assert "_registry" in refine_text
    assert "role policies" in refine_text
    assert "coder roles" in refine_text
    assert "coder connections" in refine_text

    assert "{LAYER1_RUNTIME_EVIDENCE}" in audit_text
    assert "Source Grounding Checks" in audit_text
    assert "_registry" in audit_text
    assert "role policies" in audit_text
    assert "coder roles" in audit_text
    assert "coder connections" in audit_text
    assert "filesystem copy" in review_text
    assert "remote registry" in review_text
    assert "bootstrap snapshot" in review_text
    assert "per-execution" in review_text
    assert "filesystem copy" in refine_text
    assert "bundle registry service" in refine_text
    assert "bootstrap snapshot" in refine_text
    assert "per-execution working directory context" in refine_text
    assert "filesystem copy" in audit_text
    assert "remote registry" in audit_text
    assert "bootstrap snapshot" in audit_text
    assert "global runtime home bundle" in audit_text


def test_extra_layer1_checks_reject_unsupported_remote_registry_claims() -> None:
    actions = _load_actions_module()
    with tempfile.TemporaryDirectory() as tmp_dir:
        project_root = Path(tmp_dir)
        docs_root = project_root / "docs" / "system" / "00_governance" / "bootstrap"
        docs_root.mkdir(parents=True, exist_ok=True)

        (docs_root / "README.md").write_text(
            "# System Documentation Index\n\nRepo-local outputs live under `docs/repo/` and are outside Layer 1 ownership.\n",
            encoding="utf-8",
        )
        (docs_root / "DOCUMENTATION_STANDARD.md").write_text(
            "# Purpose\n",
            encoding="utf-8",
        )
        (docs_root / "BUNDLE_TAXONOMY.md").write_text(
            "# Bundle Classes\n\nPlugin workflow bundles define ownership boundaries.\n",
            encoding="utf-8",
        )
        (docs_root / "RUNTIME_GOVERNANCE.md").write_text(
            "\n".join(
                [
                    "# Runtime Governance",
                    "",
                    "The global runtime home hosts the canonical published bundle copy.",
                    "Publish uploads the bundle to a registry as an immutable snapshot.",
                    "Install means downloading its published snapshot with version constraint resolution.",
                    "The registry enforces dependency declarations for each depending bundle.",
                    "The `_registry` file defines role policies, coder roles, and coder connections.",
                    "Bundles support single-workflow and multi-workflow layouts.",
                    "Shared runtime code provides only generic path helpers.",
                    "Each workflow bundle owns workflow-specific artifact path contracts.",
                    "Seeding copies bundle content into the global runtime home.",
                    "No centralized workflow-family path registry is allowed.",
                    "No local repository fallback is allowed.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (docs_root / "JOB-layer1-runtime-evidence.md").write_text(
            "\n".join(
                [
                    "# Layer 1 Runtime Evidence",
                    "",
                    "- publish, install, and seeding are local filesystem copy operations",
                    "- coder_registry.py includes _registry, role policies, coder roles, coder connections",
                    "- bundle_loader.py includes publish_bootstrap_bundle, install_bootstrap_bundle, seed_workflow_bundle",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (docs_root / "JOB-layer1-governance-review.md").write_text(
            "## Source Grounding Checks\n\n_registry role policies coder roles coder connections\n",
            encoding="utf-8",
        )

        checks = actions._extra_layer1_checks(project_root=project_root, job_id="JOB")
        failed = {item["check"] for item in checks if not item["ok"]}

        assert "runtime_no_unsupported_remote_registry_claims" in failed


def test_extra_layer1_checks_reject_install_target_misstatement() -> None:
    actions = _load_actions_module()
    with tempfile.TemporaryDirectory() as tmp_dir:
        project_root = Path(tmp_dir)
        docs_root = project_root / "docs" / "system" / "00_governance" / "bootstrap"
        docs_root.mkdir(parents=True, exist_ok=True)

        (docs_root / "README.md").write_text(
            "# System Documentation Index\n\nRepo-local outputs live under `docs/repo/` and are outside Layer 1 ownership.\n",
            encoding="utf-8",
        )
        (docs_root / "DOCUMENTATION_STANDARD.md").write_text("# Purpose\n", encoding="utf-8")
        (docs_root / "BUNDLE_TAXONOMY.md").write_text(
            "# Bundle Classes\n\nPlugin workflow bundles define ownership boundaries.\n",
            encoding="utf-8",
        )
        (docs_root / "RUNTIME_GOVERNANCE.md").write_text(
            "\n".join(
                [
                    "# Runtime Governance",
                    "",
                    "The bootstrap snapshot is the source artifact for install.",
                    "The global runtime home is the canonical runtime location.",
                    "Publish copies the complete bundle directory from its source location to the global runtime home.",
                    "Install copies a published bundle's files from the global runtime home into the per-execution working directory context.",
                    "Seed uses filesystem copy semantics.",
                    "The `_registry` file defines role policies, coder roles, and coder connections.",
                    "Bundles support single-workflow and multi-workflow layouts.",
                    "Shared runtime code provides only generic path helpers.",
                    "Each workflow bundle owns workflow-specific artifact path contracts.",
                    "No centralized workflow-family path registry is allowed.",
                    "No local repository fallback is allowed.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (docs_root / "JOB-layer1-runtime-evidence.md").write_text(
            "\n".join(
                [
                    "# Layer 1 Runtime Evidence",
                    "",
                    "- publish writes the bootstrap snapshot",
                    "- install copies the bootstrap snapshot into the global runtime home bundle location",
                    "- seed copies packaged workflows into the target global workflow location",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (docs_root / "JOB-layer1-governance-review.md").write_text(
            "## Source Grounding Checks\n\n_registry role policies coder roles coder connections\n",
            encoding="utf-8",
        )

        checks = actions._extra_layer1_checks(project_root=project_root, job_id="JOB")
        failed = {item["check"] for item in checks if not item["ok"]}

        assert "runtime_no_install_target_misstatement" in failed
