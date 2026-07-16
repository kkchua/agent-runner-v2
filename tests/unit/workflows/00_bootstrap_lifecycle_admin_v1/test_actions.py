from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_actions_module():
    module_path = (
        Path(__file__).resolve().parents[4]
        / "workflows"
        / "00_bootstrap_lifecycle_admin_v1"
        / "actions.py"
    )
    spec = importlib.util.spec_from_file_location("tests.bootstrap_lifecycle_actions", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load actions module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validate_bootstrap_lifecycle_sources_rejects_missing_source_docs(tmp_path: Path) -> None:
    actions = _load_actions_module()

    result = actions.validate_bootstrap_lifecycle_sources(
        context={},
        state={"job_id": "00BOOT-TEST"},
        step_cfg={},
        project_root=tmp_path,
    )

    assert result.status == "REJECTED"
    assert result.reject_code == "BOOTSTRAP_SOURCE_DOCS_MISSING"


def test_validate_bootstrap_lifecycle_sources_accepts_valid_bundle(tmp_path: Path) -> None:
    actions = _load_actions_module()
    source_root = tmp_path / "docs" / "system" / "00_governance" / "bootstrap"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "README.md").write_text("# Bootstrap\n", encoding="utf-8")

    bundle_root = tmp_path / "workflows" / "demo_bundle"
    (bundle_root / "prompts").mkdir(parents=True, exist_ok=True)
    (bundle_root / "workflow.toml").write_text(
        "\n".join(
            [
                "[workflow]",
                'name = "demo_bundle"',
                'version = "1"',
                'job_prefix = "DEMO"',
                "",
                "[workflow.init]",
                'step = "first"',
                'inputs = []',
                "",
                "[[step]]",
                'name = "first"',
                'action = "step_completion"',
            ]
        ),
        encoding="utf-8",
    )

    state = {"job_id": "00BOOT-TEST"}
    result = actions.validate_bootstrap_lifecycle_sources(
        context={},
        state=state,
        step_cfg={},
        project_root=tmp_path,
    )

    assert result.status == "APPROVED"
    assert state["bootstrap_lifecycle"]["validation"]["validated_workflows"] == ["demo_bundle"]


def test_write_bootstrap_lifecycle_summary_writes_summary_artifact(tmp_path: Path) -> None:
    actions = _load_actions_module()
    summary_path = tmp_path / "docs" / "system" / "00_governance" / "bootstrap" / "00BOOT-TEST-bootstrap-lifecycle-summary.md"
    state = {
        "job_id": "00BOOT-TEST",
        "current_step": "write_bootstrap_lifecycle_summary",
        "bootstrap_lifecycle": {
            "validation": {
                "valid": True,
                "workflow_count": 1,
                "validated_workflows": ["demo_bundle"],
            },
            "publish": {
                "source_root": "D:/repo/docs/system/00_governance/bootstrap",
                "package_bootstrap_root": "D:/repo/agent_runner_v2/bootstrap/bundles/core/current",
                "shared_registry_copied": True,
                "plugin_workflows_copied": ["demo_bundle"],
            },
            "init": {
                "runner_home": "C:/Users/test/.ukbe-runner",
                "workflow_root": "C:/Users/test/.ukbe-runner/workflows/example",
                "bundle_profile": "core+workflow",
                "bundle_domain": "general",
                "plugin_workflows_seeded": ["demo_bundle"],
            },
        },
    }
    context = {
        "BOOTSTRAP_SUMMARY": str(summary_path),
        "BOOTSTRAP_SUMMARY_PATH": str(summary_path),
        "BOOTSTRAP_SUMMARY_METAJSON": str(summary_path.with_suffix(".meta.json")),
    }

    result = actions.write_bootstrap_lifecycle_summary(
        context=context,
        state=state,
        step_cfg={},
        project_root=tmp_path,
    )

    assert result.status == "APPROVED"
    assert summary_path.exists()
    rendered = summary_path.read_text(encoding="utf-8")
    assert "Bootstrap Lifecycle Summary" in rendered
    assert "`demo_bundle`" in rendered
