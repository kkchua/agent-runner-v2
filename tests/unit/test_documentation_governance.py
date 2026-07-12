"""Documentation-governance workflow tests. Related: IMPL-20260629-01."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from os import fspath

from agent_runner_v2.workflow_router import _resolve_reject_route
from agent_runner_v2.documentation_guardrails import (
    MASTER_BOOTSTRAP_WORKFLOWS,
    execution_scaffold_doc_paths,
    master_bootstrap_doc_paths,
)
from agent_runner_v2 import system_docs
from conftest import load_bootstrap_workflow_module

validate_delivery_docs_module = importlib.import_module("agent_runner_v2.actions.validate_delivery_docs")
documentation_validation_core = importlib.import_module("agent_runner_v2.actions.documentation_validation_core")
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
    validate_sync = template_groups.TEMPLATE_GROUPS["40_documentation_sync_v1"]["step_configs"]["validate_doc_sync"]
    build_site = template_groups.TEMPLATE_GROUPS["50_architecture_site_v1"]["step_configs"]["build_site"]
    validate_site = template_groups.TEMPLATE_GROUPS["50_architecture_site_v1"]["step_configs"]["validate_site"]

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
    assert sync_docs["action"] == "sync_codebase_docs"
    assert sync_docs["required_inputs"] == []
    assert validate_sync["action"] == "validate_codebase_docs"
    assert validate_sync["required_inputs"] == ["CODEBASE_CHANGE_IMPACT", "CODEBASE_INVENTORY"]
    assert build_site["action"] == "publish_architecture_site"
    assert validate_site["action"] == "validate_architecture_site"


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


def test_delivery_validator_no_longer_requires_legacy_engineering_and_operations_folders():
    assert "docs/engineering" not in validate_delivery_docs_module.DELIVERY_FOLDERS
    assert "docs/operations" not in validate_delivery_docs_module.DELIVERY_FOLDERS


def test_documentation_validation_core_is_shared():
    assert documentation_validation_core.DocumentationValidationPlan.__module__.endswith("documentation_validation_core")
    assert callable(documentation_validation_core.validate_documentation_plan)


def test_generated_doc_inventory_covers_master_and_scaffold_outputs():
    master_paths = master_bootstrap_doc_paths(job_id="00DOC-GEN-20260702-003", mode="bootstrap")
    scaffold_paths = execution_scaffold_doc_paths()

    assert "docs/system/00_governance/bootstrap/README.md" in master_paths
    assert "docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md" in master_paths
    assert "docs/system/00_governance/bootstrap/00DOC-GEN-20260702-003-bootstrap-change-log.md" in master_paths
    assert "docs/system/00_governance/bootstrap/WORKFLOW_SOP_v1.md" in scaffold_paths
    assert "docs/system/00_governance/bootstrap/DELIVERY_AGENTS.md" in scaffold_paths
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


def test_template_generation_prompts_require_plan_and_inventory_status_vocabulary():
    prompt_root = Path("agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1")
    generate_text = (prompt_root / "03_generate_templates.txt").read_text(encoding="utf-8")
    refine_text = (prompt_root / "06_refine_templates.txt").read_text(encoding="utf-8")

    assert "explicitly reference the originating plan or task graph" in generate_text
    assert "needs_update" in generate_text
    assert "explicitly references the originating plan or task graph" in refine_text
    assert "needs_update" in refine_text


def test_generated_doc_banner_instruction_is_injected_for_workflow_prompts():
    from agent_runner_v2.run_agent import _augment_generated_doc_prompt

    rendered = _augment_generated_doc_prompt(
        "body",
        template_group="00_master_docs_bootstrap_v1",
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


def test_core_governance_review_step_has_deterministic_review_filename():
    from agent_runner_v2.step_runner import _review_step_code, _suggested_review_file_path

    assert _review_step_code("review_core_governance_docs") == "rcore"
    path = _suggested_review_file_path(
        state={
            "template_group": "00_core_governance_bootstrap_v1",
            "job_id": "00CORE-GEN-TEST",
            "artifacts": {
                "SYSTEM_DOCS_INDEX": "docs/system/00_governance/bootstrap/README.md",
            },
        },
        step="review_core_governance_docs",
        step_cfg={
            "on_reject_refine": {"artifact": "SYSTEM_DOCS_INDEX"},
        },
    )
    assert path == "docs/system/00_governance/bootstrap/00CORE-GEN-TEST-core-governance-review.md"


def test_core_governance_audit_step_has_deterministic_review_filename():
    from agent_runner_v2.step_runner import _review_step_code, _suggested_review_file_path

    assert _review_step_code("audit_core_governance_accuracy") == "acore"
    path = _suggested_review_file_path(
        state={
            "template_group": "00_core_governance_bootstrap_v1",
            "job_id": "00CORE-GEN-TEST",
            "artifacts": {
                "SYSTEM_DOCS_INDEX": "docs/system/00_governance/bootstrap/README.md",
            },
        },
        step="audit_core_governance_accuracy",
        step_cfg={
            "on_reject_refine": {"artifact": "SYSTEM_DOCS_INDEX"},
        },
    )
    assert path == "docs/system/00_governance/bootstrap/00CORE-GEN-TEST-core-governance-audit.md"


def test_codebase_inventory_generation_uses_registry_template_id():
    from agent_runner_v2 import codebase_docs

    snapshot = {
        "generated_at": "2026-07-03T00:00:00+08:00",
        "workflow_name": "00_master_docs_bootstrap_v1",
        "mode": "bootstrap",
        "job_id": "00DOC-GEN-TEST",
        "step": "01_generate_codebase_baseline",
        "items": [],
        "counts": {},
    }
    rendered = codebase_docs.render_inventory(snapshot, title="agent-runner-v2")

    assert 'template_id: "CODEBASE-INV-v1"' in rendered.splitlines()[:8]
    assert "needs_update" in rendered


def test_html_files_are_classified_as_documentation(tmp_path):
    from agent_runner_v2.codebase_docs import _classify_file

    root = tmp_path
    root.mkdir(parents=True, exist_ok=True)
    html_path = root / "docs/site/architecture/index.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text("<html></html>", encoding="utf-8")
    item = _classify_file(root, html_path)

    assert item is not None
    assert item.category == "documentation files"
    assert item.status == "current"


def test_scaffold_prompts_require_baseline_and_profile_handling():
    prompt_root = Path("agent_runner_v2/bootstrap/workflows/default/prompts")

    analysis_text = (prompt_root / "10_execution_scaffold_v1" / "01_project_analysis.txt").read_text(encoding="utf-8")
    sop_text = (prompt_root / "10_execution_scaffold_v1" / "02_generate_sop.txt").read_text(encoding="utf-8")
    planner_text = (prompt_root / "30_delivery_planning_v1" / "02_planner.txt").read_text(encoding="utf-8")
    task_text = (prompt_root / "30_delivery_planning_v1" / "06_task.txt").read_text(encoding="utf-8")
    review_text = (prompt_root / "40_documentation_sync_v1" / "02_review_docs.txt").read_text(encoding="utf-8")
    validate_text = (prompt_root / "40_documentation_sync_v1" / "04_validate_doc_sync.txt").read_text(encoding="utf-8")

    assert "Architecture Posture" in analysis_text
    assert "repo-selected profile" in analysis_text
    assert "Operational Risks" in analysis_text
    assert "Architectural Observations" in analysis_text
    assert "Universal Baseline" in sop_text
    assert "Repo-Selected Profile" in sop_text
    assert "Migration Mode" in sop_text
    assert "conditional standards" in sop_text.lower()
    assert "repo-selected architecture profile" in planner_text
    assert "migration mode" in planner_text.lower()
    assert "architecture posture updates" in task_text
    assert "repo-selected architecture posture" in review_text
    assert "architecture posture docs remain consistent" in validate_text
    assert "next-phase HTML architecture site" in (prompt_root / "00_master_docs_bootstrap_v1" / "04_generate_architecture_docs.txt").read_text(encoding="utf-8")
    sop_text_updated = (prompt_root / "10_execution_scaffold_v1" / "02_generate_sop.txt").read_text(encoding="utf-8")
    assert "repo-wide reconciliation workflow" in sop_text_updated
    assert "50_architecture_site_v1" in sop_text_updated


def test_sop_review_prompt_allows_active_workflow_generated_docs():
    text = Path("agent_runner_v2/bootstrap/workflows/default/prompts/10_execution_scaffold_v1/03_review_sop.txt").read_text(encoding="utf-8")

    assert '"active"' in text
    assert "workflow-generated SOPs" in text


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


