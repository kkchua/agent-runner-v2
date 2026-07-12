from __future__ import annotations

from agent_runner_v2 import backend_execution
from agent_runner_v2 import run_agent as run_agent_module


def test_backend_execution_build_group_cfg_from_execution_spec() -> None:
    spec = {
        "job_prefix": "TEST",
        "job_init_step": "review_docs",
        "job_init_inputs": ["SYSTEM_DOCS_INDEX"],
        "default_max_rejects": 2,
        "reference_files": {"CORE_GUIDE": "docs/core.md"},
        "prompt_file": "prompts/review.txt",
        "action_name": "",
        "edit_mode": "in_place",
        "result_meta_key": "REVIEW_FILE",
        "result_meta_key_from_context": "REVIEW_FILE_SUGGESTED",
        "template_ref": {"artifact_key": "REVIEW_FILE"},
        "required_inputs": [{"artifact_key": "SYSTEM_DOCS_INDEX"}],
        "optional_inputs": [{"artifact_key": "SYSTEM_DOC_STANDARD"}],
        "immutable_inputs": [{"artifact_key": "BUNDLE_TAXONOMY"}],
        "produces": [{"artifact_key": "REVIEW_FILE"}],
        "updates": [{"artifact_key": "SYSTEM_DOCS_INDEX"}],
        "target_artifact": "SYSTEM_DOCS_INDEX",
        "coder_policy": {
            "default_coder": "reviewer_primary",
            "allowed_coders": ["reviewer_primary", "reviewer_secondary"],
            "must_differ_from_previous_step": True,
        },
        "raw_config": {"enable_notifications": True},
    }

    group_cfg, step_cfg = backend_execution.build_group_cfg_from_execution_spec(
        spec,
        "00_core_governance_bootstrap_v1",
        "review_core_governance_docs",
    )

    assert group_cfg["job_prefix"] == "TEST"
    assert group_cfg["job_init_step"] == "review_docs"
    assert group_cfg["job_init_inputs"] == ["SYSTEM_DOCS_INDEX"]
    assert group_cfg["default_max_rejects"] == 2
    assert group_cfg["reference_files"] == {"CORE_GUIDE": "docs/core.md"}
    assert group_cfg["steps"] == ["review_core_governance_docs"]

    assert step_cfg["prompt_file"] == "prompts/review.txt"
    assert step_cfg["edit_mode"] == "in_place"
    assert step_cfg["result_meta_key"] == "REVIEW_FILE"
    assert step_cfg["result_meta_key_from_context"] == "REVIEW_FILE_SUGGESTED"
    assert step_cfg["required_inputs"] == ["SYSTEM_DOCS_INDEX"]
    assert step_cfg["optional_inputs"] == ["SYSTEM_DOC_STANDARD"]
    assert step_cfg["immutable_inputs"] == ["BUNDLE_TAXONOMY"]
    assert step_cfg["produces"] == ["REVIEW_FILE"]
    assert step_cfg["updates"] == ["SYSTEM_DOCS_INDEX"]
    assert step_cfg["target_artifact"] == "SYSTEM_DOCS_INDEX"
    assert step_cfg["coder"]["default"] == "reviewer_primary"
    assert step_cfg["coder"]["allowed"] == ["reviewer_primary", "reviewer_secondary"]
    assert step_cfg["coder"]["must_differ_from_previous_step"] is True
    assert step_cfg["enable_notifications"] is True


def test_run_agent_build_group_cfg_wrapper_delegates_to_backend_execution() -> None:
    spec = {"raw_config": {}}

    group_cfg, step_cfg = run_agent_module._build_group_cfg_from_execution_spec(
        spec,
        "workflow_x",
        "step_y",
    )

    expected_group_cfg, expected_step_cfg = backend_execution.build_group_cfg_from_execution_spec(
        spec,
        "workflow_x",
        "step_y",
    )

    assert group_cfg == expected_group_cfg
    assert step_cfg == expected_step_cfg
