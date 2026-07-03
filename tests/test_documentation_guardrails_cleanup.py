from __future__ import annotations

from pathlib import Path

from agent_runner_v2.cleanup_generated_docs import cleanup_workflow_generated_docs
from agent_runner_v2.documentation_guardrails import workflow_generated_doc_paths, workflow_stale_generated_doc_paths


def _write_workflow_doc(path: Path, workflow: str, step: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "---",
                f'title: "Demo"',
                f'workflow: "{workflow}"',
                f'step: "{step}"',
                'managed_by: "workflow-generated"',
                "---",
                "",
                f"> Managed by workflow: `{workflow}` / step: `{step}`",
                "> This file is workflow-generated and protected from manual edits.",
                "",
                "# Demo",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_cleanup_identifies_legacy_master_bootstrap_docs(tmp_path: Path) -> None:
    project_root = tmp_path
    canonical = project_root / "docs/system/00_governance/bootstrap/README.md"
    legacy = project_root / "docs/system/README.md"

    _write_workflow_doc(canonical, "00_master_docs_bootstrap_v1", "03_generate_system_overview_docs")
    _write_workflow_doc(legacy, "00_master_docs_bootstrap_v1", "03_generate_system_overview_docs")

    state = {"job_id": "TEST-001", "current_step_cfg": {"mode": "bootstrap"}}
    stale = workflow_stale_generated_doc_paths(
        template_group="00_master_docs_bootstrap_v1",
        state=state,
        project_root=project_root,
    )

    assert "docs/system/README.md" in stale
    assert "docs/system/00_governance/bootstrap/README.md" not in stale

    protected = workflow_generated_doc_paths(
        template_group="00_master_docs_bootstrap_v1",
        state=state,
    )
    assert "docs/system/00_governance/bootstrap/README.md" in protected
    assert "docs/system/README.md" not in protected


def test_cleanup_remove_action_deletes_stale_docs(tmp_path: Path) -> None:
    project_root = tmp_path
    stale_doc = project_root / "docs/system/README.md"

    _write_workflow_doc(stale_doc, "00_master_docs_bootstrap_v1", "03_generate_system_overview_docs")

    result = cleanup_workflow_generated_docs(
        project_root=project_root,
        template_group="00_master_docs_bootstrap_v1",
        job_id="TEST-001",
        mode="bootstrap",
        action="remove",
    )

    assert "docs/system/README.md" in result.stale_paths
    assert "docs/system/README.md" in result.removed_paths
    assert not stale_doc.exists()
