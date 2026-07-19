from __future__ import annotations

from agent_runner_v2 import run_agent as run_agent_module


def test_master_bootstrap_frontmatter_contract_injection_for_system_docs() -> None:
    step_cfg = {
        "produces": ["SYSTEM_DOCS_INDEX", "SYSTEM_DOC_STANDARD"],
        "mode": "bootstrap",
    }
    state = {"job_id": "00DOC-TEST-001"}

    injected = run_agent_module._augment_generated_doc_prompt(
        "base prompt",
        template_group="00_repo_master_docs_bootstrap_v1",
        step="03_generate_system_overview_docs",
        step_cfg=step_cfg,
        state=state,
    )

    assert 'version: "1.0.0"' in injected
    assert 'generated_at: "<ISO timestamp>"' in injected
    assert '`docs/repo/governance/README.md` -> `template_id: "SYS-00-IDX"`' in injected
    assert '`docs/repo/governance/REPO_DOCUMENTATION_STANDARD.md` -> `template_id: "SYS-00-DS"`' in injected


def test_master_bootstrap_frontmatter_contract_injection_for_codebase_docs() -> None:
    step_cfg = {
        "produces": ["INTEGRATION_MAP", "FAILURE_MODES", "ARCHITECTURE_FLOW"],
        "mode": "bootstrap",
    }
    state = {"job_id": "00DOC-TEST-001"}

    injected = run_agent_module._augment_generated_doc_prompt(
        "base prompt",
        template_group="00_repo_master_docs_bootstrap_v1",
        step="04b_generate_integration_docs",
        step_cfg=step_cfg,
        state=state,
    )

    assert '`template_id: "CB-04-IM"`' in injected
    assert '`template_id: "CB-04-FM"`' in injected
    assert '`template_id: "CB-04-AF"`' in injected
    assert '`doc_type: "codebase"`' in injected
