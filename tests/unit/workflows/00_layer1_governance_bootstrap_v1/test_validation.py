from __future__ import annotations

import importlib.util
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
