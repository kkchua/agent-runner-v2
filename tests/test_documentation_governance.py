"""Documentation-governance workflow tests. Related: IMPL-20260629-01."""

from __future__ import annotations

import importlib
from pathlib import Path

from agent_runner_v2 import template_groups
from agent_runner_v2.workflow_router import _resolve_reject_route

validate_delivery_docs_module = importlib.import_module("agent_runner_v2.actions.validate_delivery_docs")


def test_delivery_planning_requires_codebase_governance_inputs():
    planner = template_groups.TEMPLATE_GROUPS["delivery_planning_v1"]["step_configs"]["planner"]
    task_graph = template_groups.TEMPLATE_GROUPS["delivery_planning_v1"]["step_configs"]["task_graph"]
    task = template_groups.TEMPLATE_GROUPS["task_execution_v1"]["step_configs"]["task"]

    assert "CODEBASE_DOC_SOP" in planner["required_inputs"]
    assert "CODEBASE_INVENTORY" in planner["required_inputs"]
    assert "CODEBASE_DOC_STATUS_RULES" in task_graph["required_inputs"]
    assert "Documentation Impact" in task["template_ref"]["required_sections"]


def test_validator_routes_impl_and_doc_failures_differently():
    validator = template_groups.TEMPLATE_GROUPS["task_execution_v1"]["step_configs"]["validator"]

    assert validator["on_reject_refine"]["step"] == "refine_impl"
    assert validator["on_reject_refine"]["artifact"] == "IMPL_FILE"
    assert validator["reject_code_routes"]["DOC_SYNC_VALIDATION_FAILED"]["step"] == "refine_docs"
    assert validator["reject_code_routes"]["DOC_SYNC_VALIDATION_FAILED"]["artifact"] == "CODEBASE_CHANGE_IMPACT"


def test_reject_route_prefers_code_specific_override():
    step_cfg = {
        "on_reject_refine": {"step": "refine_impl", "artifact": "IMPL_FILE"},
        "reject_code_routes": {
            "DOC_SYNC_VALIDATION_FAILED": {"step": "refine_docs", "artifact": "CODEBASE_CHANGE_IMPACT"},
        },
    }

    route = _resolve_reject_route(step_cfg=step_cfg, reject_code="DOC_SYNC_VALIDATION_FAILED")
    fallback = _resolve_reject_route(step_cfg=step_cfg, reject_code="IMPL_VALIDATION_FAILED")

    assert route == {"step": "refine_docs", "artifact": "CODEBASE_CHANGE_IMPACT"}
    assert fallback == {"step": "refine_impl", "artifact": "IMPL_FILE"}


def test_validation_rules_cover_pending_review_and_owner_fields():
    required_sections = validate_delivery_docs_module.TEMPLATE_SECTION_REQUIREMENTS["05_validation.template.md"]
    inventory_sections = validate_delivery_docs_module.CODEBASE_TEMPLATE_SECTION_REQUIREMENTS["01_codebase_inventory.template.md"]

    assert "Documentation Sync Results" in required_sections
    assert "Freshness Triggers" in inventory_sections


def test_scaffold_generation_prompts_require_v2_sidecars():
    prompt_root = "agent_runner_v2/bootstrap/workflows/default/prompts/delivery_scaffold_v1"
    files = [
        "01_project_analysis.txt",
        "02_generate_sop.txt",
        "03_generate_templates.txt",
        "04_generate_agents.txt",
    ]

    for name in files:
        path = Path(prompt_root) / name
        text = path.read_text(encoding="utf-8")
        assert "schema_version" in text
        assert '"v2"' in text
        assert "coder_result" in text
