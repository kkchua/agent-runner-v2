"""Documentation-governance workflow tests. Related: IMPL-20260629-01."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

from agent_runner_v2.workflow_router import _resolve_reject_route
from agent_runner_v2.documentation_guardrails import (
    MASTER_BOOTSTRAP_WORKFLOW,
    execution_scaffold_doc_paths,
    master_bootstrap_doc_paths,
)
from agent_runner_v2 import system_docs
from conftest import load_bootstrap_workflow_module

validate_delivery_docs_module = importlib.import_module("agent_runner_v2.actions.validate_delivery_docs")
template_groups = load_bootstrap_workflow_module()


def test_delivery_planning_requires_codebase_governance_inputs():
    master = template_groups.TEMPLATE_GROUPS["00_master_docs_bootstrap_v1"]["step_configs"]["02_generate_project_analysis"]
    master_overview = template_groups.TEMPLATE_GROUPS["00_master_docs_bootstrap_v1"]["step_configs"]["03_generate_system_overview_docs"]
    master_arch = template_groups.TEMPLATE_GROUPS["00_master_docs_bootstrap_v1"]["step_configs"]["04_generate_architecture_docs"]
    scaffold_sop = template_groups.TEMPLATE_GROUPS["10_execution_scaffold_v1"]["step_configs"]["generate_sop"]
    planner = template_groups.TEMPLATE_GROUPS["30_delivery_planning_v1"]["step_configs"]["planner"]
    task_graph = template_groups.TEMPLATE_GROUPS["30_delivery_planning_v1"]["step_configs"]["task_graph"]
    task = template_groups.TEMPLATE_GROUPS["31_task_execution_v1"]["step_configs"]["task"]
    sync_docs = template_groups.TEMPLATE_GROUPS["40_documentation_sync_v1"]["step_configs"]["sync_docs"]

    assert "CODEBASE_SCAN_SNAPSHOT" in master["required_inputs"]
    assert "CODEBASE_CHANGE_IMPACT" in master["required_inputs"]
    assert "CODEBASE_INVENTORY" in master["required_inputs"]
    assert "PROJECT_ANALYSIS" in master["produces"]
    assert "PROJECT_ANALYSIS" in master_overview["required_inputs"]
    assert "SYSTEM_DOCS_INDEX" in master_overview["produces"]
    assert "SYSTEM_DOCS_INDEX" in master_arch["required_inputs"]
    assert "SYSTEM_DOCS_CHANGE_LOG" in master_arch["produces"]
    assert "EXISTING_REPO_WORKFLOW_SOP" in scaffold_sop["produces"]
    assert "CODEBASE_DOC_SOP" in planner["required_inputs"]
    assert "SYSTEM_DOC_STANDARD" in planner["required_inputs"]
    assert "CODEBASE_INVENTORY" in planner["required_inputs"]
    assert "SYSTEM_OVERVIEW" in task_graph["required_inputs"]
    assert "CODEBASE_DOC_STATUS_RULES" in task_graph["required_inputs"]
    assert "System Documentation Impact" in task["template_ref"]["required_sections"]
    assert "RUNBOOK" in sync_docs["required_inputs"]


def test_validator_routes_impl_and_doc_failures_differently():
    validator = template_groups.TEMPLATE_GROUPS_OLD["task_execution_v1"]["step_configs"]["validator"]

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
    required_sections = validate_delivery_docs_module.TEMPLATE_SECTION_REQUIREMENTS["08_delivery_validation_template.md"]
    inventory_sections = validate_delivery_docs_module.CODEBASE_TEMPLATE_SECTION_REQUIREMENTS["02_codebase_inventory_template.md"]
    module_sections = validate_delivery_docs_module.CODEBASE_TEMPLATE_SECTION_REQUIREMENTS["03_codebase_module_template.md"]
    component_sections = validate_delivery_docs_module.CODEBASE_TEMPLATE_SECTION_REQUIREMENTS["04_codebase_component_template.md"]
    change_sections = validate_delivery_docs_module.CODEBASE_TEMPLATE_SECTION_REQUIREMENTS["05_codebase_change_template.md"]
    delivery_registry_sections = validate_delivery_docs_module.TEMPLATE_SECTION_REQUIREMENTS["01_delivery_template_registry.md"]
    system_sections = validate_delivery_docs_module.SYSTEM_DOC_REQUIRED_SECTIONS["docs/system/00_governance/bootstrap/README.md"]
    analysis_sections = validate_delivery_docs_module.SYSTEM_DOC_REQUIRED_SECTIONS["docs/system/00_governance/bootstrap/project_analysis.md"]
    operator_sections = validate_delivery_docs_module.SYSTEM_DOC_REQUIRED_SECTIONS["docs/system/00_governance/bootstrap/EXISTING_REPO_WORKFLOW_SOP.md"]
    runbook_sections = validate_delivery_docs_module.SYSTEM_DOC_REQUIRED_SECTIONS["docs/system/00_governance/bootstrap/RUNBOOK.md"]

    assert "Documentation Synchronization Validation" in required_sections
    assert "File Type Coverage" in inventory_sections
    assert "Module Overview" in module_sections
    assert "Component Overview" in component_sections
    assert "Change Summary" in change_sections
    assert "Registry Overview" in delivery_registry_sections
    assert "Audience Views" in system_sections
    assert "Repo Overview" in analysis_sections
    assert "First-Time Setup" in operator_sections
    assert "Failure Handling" in runbook_sections


def test_delivery_scaffold_paths_match_generated_layout():
    assert validate_delivery_docs_module.REQUIRED_TEMPLATES["DELIVERY_TEMPLATE_REGISTRY"] == "01_delivery_template_registry.md"
    assert validate_delivery_docs_module.REQUIRED_TEMPLATES["DELIVERY_TASK_TEMPLATE"] == "05_delivery_task_template.md"
    assert validate_delivery_docs_module.REQUIRED_CODEBASE_FILES["CODEBASE_TEMPLATE_REGISTRY"].endswith(
        "docs/system/00_governance/bootstrap/templates/codebase/01_codebase_template_registry.md"
    )
    assert validate_delivery_docs_module.REQUIRED_CODEBASE_FILES["CODEBASE_COMPONENT_TEMPLATE"].endswith(
        "docs/system/00_governance/bootstrap/templates/codebase/04_codebase_component_template.md"
    )
    assert validate_delivery_docs_module.DELIVERY_AGENT_ROOT.as_posix() == "docs/delivery/00_standards"
    assert Path("docs/delivery/00_standards/DELIVERY_AGENTS_MD.md").as_posix().endswith("DELIVERY_AGENTS_MD.md")
    assert Path("docs/delivery/00_standards/DELIVERY_AGENT_REVIEWER.md").as_posix().endswith("DELIVERY_AGENT_REVIEWER.md")


def test_generated_doc_inventory_covers_master_and_scaffold_outputs():
    master_paths = master_bootstrap_doc_paths(job_id="00DOC-GEN-20260702-003", mode="bootstrap")
    scaffold_paths = execution_scaffold_doc_paths()

    assert "docs/system/00_governance/bootstrap/README.md" in master_paths
    assert "docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md" in master_paths
    assert "docs/system/00_governance/bootstrap/00DOC-GEN-20260702-003-bootstrap-change-log.md" in master_paths
    assert "docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md" in scaffold_paths
    assert "docs/delivery/00_standards/DELIVERY_AGENTS_MD.md" in scaffold_paths
    assert "docs/delivery/DELIVERY_FOLDER_MAP.json" in scaffold_paths


def test_system_docs_validation_uses_workflow_name_in_frontmatter():
    snapshot = {
        "workflow_name": "00_master_docs_bootstrap_v1",
        "mode": "bootstrap",
        "step": "08_validate_master_system_docs",
    }
    rendered = system_docs.render_system_docs_validation(
        snapshot,
        title="System docs bootstrap validation",
        checks=[("readme", True, "ok")],
    )

    assert 'workflow: "00_master_docs_bootstrap_v1"' in rendered.splitlines()[:8]


def test_scaffold_generation_prompts_require_v2_sidecars():
    prompt_root = "agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1"
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


def test_generated_doc_banner_instruction_is_injected_for_workflow_prompts():
    from agent_runner_v2.run_agent import _augment_generated_doc_prompt

    rendered = _augment_generated_doc_prompt(
        "body",
        template_group=MASTER_BOOTSTRAP_WORKFLOW,
        step="03_generate_system_overview_docs",
        step_cfg={"mode": "bootstrap"},
        state={"job_id": "00DOC-GEN-20260702-003", "current_mode": "bootstrap"},
    )

    assert "Managed by workflow" in rendered
    assert "workflow-generated" in rendered


def test_master_review_step_has_deterministic_review_filename():
    from agent_runner_v2.step_runner import _review_step_code, _suggested_review_file_path

    assert _review_step_code("review_master_system_docs") == "rmaster"
    path = _suggested_review_file_path(
        state={
            "artifacts": {
                "PROJECT_ANALYSIS": "docs/system/00_governance/bootstrap/project_analysis.md",
            }
        },
        step="review_master_system_docs",
        step_cfg={
            "on_reject_refine": {"artifact": "PROJECT_ANALYSIS"},
        },
    )
    assert path.endswith(".md")
    assert "rmaster" in path


def test_master_docs_prompts_require_v2_sidecars_and_expected_artifact_keys():
    files = {
        "02_generate_project_analysis.txt": ["PROJECT_ANALYSIS"],
        "03_generate_system_overview_docs.txt": ["SYSTEM_DOCS_INDEX", "BUNDLE_TAXONOMY", "BUNDLE_MIGRATION_PLAN"],
        "04_generate_architecture_docs.txt": ["SYSTEM_DOCS_CHANGE_LOG"],
    }

    prompt_root = Path("agent_runner_v2/bootstrap/workflows/default/prompts/00_master_docs_bootstrap_v1")
    for name, expected_keys in files.items():
        text = (prompt_root / name).read_text(encoding="utf-8")
        assert "schema_version" in text
        assert '"v2"' in text
        assert "coder_result" in text
        for expected_key in expected_keys:
            assert expected_key in text
    architecture_prompt = (prompt_root / "04_generate_architecture_docs.txt").read_text(encoding="utf-8")
    assert "Do NOT write a plain top-level" in architecture_prompt


def test_qwen_sidecar_validity_short_circuits_stdout_json_parse(monkeypatch, tmp_path):
    from agent_runner_v2 import coder_adapters

    sidecar_path = tmp_path / "meta.json"
    sidecar_path.write_text(
        '{"schema_version":"v2","coder_result":{"status":"APPROVED","remark":"ok","artifacts":{"PROJECT_ANALYSIS":"docs/system/00_governance/bootstrap/project_analysis.md"},"recorded_at":"2026-07-01T00:00:00"}}',
        encoding="utf-8",
    )

    monkeypatch.setattr(coder_adapters, "_run_with_sidecar_poll", lambda *args, **kwargs: (0, "not-json", ""))
    monkeypatch.setattr(coder_adapters, "_is_valid_sidecar_json", lambda path: True)
    monkeypatch.setattr(coder_adapters, "_usage_from_payload", lambda payload, step, coder: None)

    result = coder_adapters._invoke_qwen(
        step="02_generate_project_analysis",
        prompt_text="prompt",
        cwd=tmp_path,
        coder_config={"model": "qwen3.7-plus"},
        sidecar_path=sidecar_path,
        timeout_seconds_override=5,
    )

    assert result["return_code"] == 0
    assert result["parsed_result"] == {}


def test_step_runner_repairs_plain_direct_result_meta_json(tmp_path):
    from agent_runner_v2 import step_runner

    meta_path = tmp_path / "meta.json"
    meta_path.write_text(
        json.dumps(
            {
                "status": "APPROVED",
                "remark": "ok",
                "artifacts": {
                    "SYSTEM_DOCS_CHANGE_LOG": "docs/system/00_governance/test-bootstrap-change-log.md"
                },
            }
        ),
        encoding="utf-8",
    )

    meta = step_runner._repair_or_validate_meta_json(
        meta_path=meta_path,
        parsed_result={},
    )

    assert meta["schema_version"] == "v2"
    assert meta["coder_result"]["status"] == "APPROVED"
    assert meta["coder_result"]["artifacts"]["SYSTEM_DOCS_CHANGE_LOG"] == "docs/system/00_governance/test-bootstrap-change-log.md"
    rewritten = json.loads(meta_path.read_text(encoding="utf-8"))
    assert rewritten["schema_version"] == "v2"


def test_step_runner_repairs_missing_meta_json_from_parsed_result(tmp_path):
    from agent_runner_v2 import step_runner

    meta_path = tmp_path / "meta.json"
    meta = step_runner._repair_or_validate_meta_json(
        meta_path=meta_path,
        parsed_result={
            "status": "APPROVED",
            "remark": "ok",
            "artifacts": {
                "PROJECT_ANALYSIS": "docs/system/00_governance/bootstrap/project_analysis.md"
            },
        },
    )

    assert meta["schema_version"] == "v2"
    assert meta["coder_result"]["status"] == "APPROVED"
    assert meta["coder_result"]["artifacts"]["PROJECT_ANALYSIS"] == "docs/system/00_governance/bootstrap/project_analysis.md"
    assert meta_path.exists()


def test_finalize_bootstrap_uses_state_artifacts_when_context_path_aliases_are_missing(tmp_path):
    from agent_runner_v2.actions.finalize_bootstrap import finalize_bootstrap

    paths = [
        "docs/codebase/04_changes/00DOC-GEN-TEST-bootstrap-snapshot.json",
        "docs/codebase/04_changes/00DOC-GEN-TEST-bootstrap.md",
        "docs/codebase/01_inventory/codebase_inventory.md",
        "docs/system/00_governance/bootstrap/project_analysis.md",
        "docs/system/00_governance/bootstrap/README.md",
        "docs/system/00_governance/bootstrap/00DOC-GEN-TEST-bootstrap-change-log.md",
        "docs/codebase/04_changes/00DOC-GEN-TEST-bootstrap-validation.md",
        "docs/system/00_governance/bootstrap/00DOC-GEN-TEST-bootstrap-validation.md",
    ]
    for rel in paths:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ok\n", encoding="utf-8")

    state = {
        "job_id": "00DOC-GEN-TEST",
        "current_step": "09_finalize_bootstrap",
        "artifacts": {
            "CODEBASE_SCAN_SNAPSHOT": paths[0],
            "CODEBASE_CHANGE_IMPACT": paths[1],
            "CODEBASE_INVENTORY": paths[2],
            "PROJECT_ANALYSIS": paths[3],
            "SYSTEM_DOCS_INDEX": paths[4],
            "SYSTEM_DOCS_CHANGE_LOG": paths[5],
            "VALIDATION_FILE": paths[6],
            "SYSTEM_DOCS_VALIDATION": paths[7],
        },
    }
    context = {
        "BOOTSTRAP_SUMMARY_METAJSON": "docs/system/00_governance/bootstrap/meta.json",
    }
    step_cfg = {"mode": "bootstrap"}

    result = finalize_bootstrap(
        context=context,
        state=state,
        step_cfg=step_cfg,
        project_root=tmp_path,
    )

    assert result.status == "APPROVED"
    assert result.artifacts["BOOTSTRAP_SUMMARY"] == "docs/system/00_governance/bootstrap/00DOC-GEN-TEST-bootstrap-summary.md"


