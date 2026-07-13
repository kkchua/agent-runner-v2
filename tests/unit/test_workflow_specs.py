from __future__ import annotations

from agent_runner_v2.workflow_specs import build_step_execution_spec


def test_build_step_execution_spec_keeps_transport_only_raw_config():
    group_cfg = {
        "job_prefix": "TEST",
        "job_init_step": "review",
        "job_init_inputs": [],
        "default_max_rejects": 2,
        "reference_files": {},
        "steps": ["review"],
        "step_configs": {
            "review": {
                "prompt_file": "prompts/review.txt",
                "required_inputs": ["DOC_A"],
                "on_reject_refine": {"step": "refine", "artifact": "DOC_A"},
                "onsuccess": "validate",
                "enable_notifications": True,
                "produced_document_status": {"artifact": "DOC_A", "required_status": "approved"},
                "post_action": "publish_doc",
            }
        },
    }

    spec = build_step_execution_spec(
        template_group="demo_workflow",
        step_name="review",
        group_cfg=group_cfg,
    )

    raw_config = spec["raw_config"]
    assert raw_config["prompt_file"] == "prompts/review.txt"
    assert raw_config["required_inputs"] == ["DOC_A"]
    assert raw_config["on_reject_refine"] == {"step": "refine", "artifact": "DOC_A"}
    assert raw_config["enable_notifications"] is True
    assert raw_config["produced_document_status"] == {"artifact": "DOC_A", "required_status": "approved"}
    assert raw_config["post_action"] == "publish_doc"
    assert "onsuccess" not in raw_config
