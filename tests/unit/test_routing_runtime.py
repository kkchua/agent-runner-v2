from __future__ import annotations

from agent_runner_v2.v2.routing_runtime import predict_next_step_after_approved


def test_predict_next_step_after_approved_returns_same_step_for_human_approval() -> None:
    next_step = predict_next_step_after_approved(
        group_cfg={
            "steps": ["review_docs", "validate_docs"],
            "step_configs": {"review_docs": {"requires_human_approval_after": True}},
        },
        state={"template_group": "demo", "completed_steps": []},
        step="review_docs",
        step_cfg={"requires_human_approval_after": True},
    )

    assert next_step == "review_docs"


def test_predict_next_step_after_approved_uses_onsuccess_before_list_order() -> None:
    next_step = predict_next_step_after_approved(
        group_cfg={
            "steps": ["generate", "review", "validate"],
            "step_configs": {
                "generate": {"onsuccess": "validate"},
                "review": {"on_reject_refine": {"step": "refine", "artifact": "DOC"}},
            },
        },
        state={"template_group": "demo", "completed_steps": []},
        step="generate",
        step_cfg={"onsuccess": "validate"},
    )

    assert next_step == "validate"


def test_predict_next_step_after_approved_skips_refine_steps_for_default_progression() -> None:
    next_step = predict_next_step_after_approved(
        group_cfg={
            "steps": ["generate", "review", "refine", "validate"],
            "step_configs": {
                "review": {"on_reject_refine": {"step": "refine", "artifact": "DOC"}},
                "generate": {},
                "refine": {"loop_returns_to": "review"},
                "validate": {},
            },
        },
        state={"template_group": "demo", "completed_steps": ["generate", "review"]},
        step="review",
        step_cfg={},
    )

    assert next_step == "validate"
