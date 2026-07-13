from __future__ import annotations

from pathlib import Path

from agent_runner_v2.backend_execution import build_group_cfg_from_execution_spec


def test_build_group_cfg_from_execution_spec_restores_workflow_bundle_for_package_actions():
    prompt_file = str(
        Path("D:/MyProjectSpace/01_Workflows/agent-runner-v2/agent_runner_v2/bootstrap/workflows/default/00_core_governance_bootstrap_v1/prompts/01_generate_core_governance_docs.txt").resolve()
    )
    spec = {
        "prompt_file": prompt_file,
        "action_name": "validate_core_governance_docs",
        "raw_config": {
            "action": "validate_core_governance_docs",
        },
    }

    group_cfg, step_cfg = build_group_cfg_from_execution_spec(
        spec,
        "00_core_governance_bootstrap_v1",
        "validate_core_governance_docs",
    )

    bundle = step_cfg.get("_workflow_bundle")
    assert bundle is not None
    assert "validate_core_governance_docs" in (bundle.custom_actions or {})
    assert group_cfg.get("_workflow_bundle") is bundle


def test_build_group_cfg_from_execution_spec_without_prompt_file_skips_bundle_restore():
    group_cfg, step_cfg = build_group_cfg_from_execution_spec(
        {"raw_config": {}},
        "wf",
        "step",
    )
    assert "_workflow_bundle" not in step_cfg
    assert "_workflow_bundle" not in group_cfg


def test_build_group_cfg_from_execution_spec_restores_bundle_for_relative_prompt_file():
    spec = {
        "prompt_file": "00_core_governance_bootstrap_v1/prompts/01_generate_core_governance_docs.txt",
        "action_name": "validate_core_governance_docs",
        "raw_config": {
            "action": "validate_core_governance_docs",
        },
    }

    group_cfg, step_cfg = build_group_cfg_from_execution_spec(
        spec,
        "00_core_governance_bootstrap_v1",
        "validate_core_governance_docs",
    )

    bundle = step_cfg.get("_workflow_bundle")
    assert bundle is not None
    assert "validate_core_governance_docs" in (bundle.custom_actions or {})
    assert group_cfg.get("_workflow_bundle") is bundle
