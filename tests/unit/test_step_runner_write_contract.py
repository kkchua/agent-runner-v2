from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from agent_runner_v2.exceptions import ArtifactMissingError
from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.step_runner import (
    _backfill_declared_produced_artifacts,
    _set_master_docs_aliases,
    _resolve_meta_json_path,
    _resolve_progress_file_path,
    _resolve_allowed_write_paths,
    _snapshot_allowed_write_roots,
    _validate_declared_produced_artifacts_exist,
    _validate_artifacts_in_produces_list,
    _validate_step_write_contract_config,
    _verify_only_allowed_paths_changed,
    run_action,
)


def test_validate_artifacts_in_produces_list_allows_explicit_aliases_only() -> None:
    _validate_artifacts_in_produces_list(
        artifacts={
            "IMPL_FILE_PATH": "docs/delivery/05_implementations/impl.md",
            "VALIDATION_FILE_METAJSON": "docs/delivery/06_validations/impl.meta.json",
        },
        produces=["IMPL_FILE", "VALIDATION_FILE"],
        step="test_step",
    )

    with pytest.raises(ArtifactMissingError):
        _validate_artifacts_in_produces_list(
            artifacts={"IMPL_FILE_V2": "docs/delivery/05_implementations/impl.md"},
            produces=["IMPL_FILE"],
            step="test_step",
        )


def test_validate_artifacts_in_produces_list_allows_master_docs_legacy_aliases() -> None:
    _validate_artifacts_in_produces_list(
        artifacts={
            "README": "docs/system/00_governance/bootstrap/README.md",
            "CHANGE_LOG": "docs/system/00_governance/bootstrap/00DOC-test-bootstrap-change-log.md",
        },
        produces=["SYSTEM_DOCS_INDEX", "SYSTEM_DOCS_CHANGE_LOG"],
        step="06_refine_master_system_docs",
    )


def test_set_master_docs_aliases_supports_core_governance_workflow(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    ctx: dict[str, str] = {}
    state = {
        "template_group": "00_core_governance_bootstrap_v1",
        "job_id": "00CORE-GEN-TEST",
        "backend_step_dir_rel": r"00_core_governance_bootstrap_v1\00CORE-GEN-TEST\01_generate_core_governance_docs",
    }
    monkeypatch.setattr(
        "agent_runner_v2.step_runner.get_workflow_module",
        lambda: SimpleNamespace(TEMPLATE_GROUPS={}),
    )

    _set_master_docs_aliases(
        ctx=ctx,
        state=state,
        step="generate_core_governance_docs",
        artifacts={"SYSTEM_DOCS_INDEX": ""},
        produces=[
            "SYSTEM_DOCS_INDEX",
            "SYSTEM_DOC_STANDARD",
            "BUNDLE_TAXONOMY",
            "RUNTIME_GOVERNANCE",
        ],
        project_root=tmp_path,
    )

    assert ctx["SYSTEM_DOCS_INDEX"].replace("\\", "/") == str((tmp_path / "docs/system/00_governance/bootstrap/README.md").resolve()).replace("\\", "/")
    assert ctx["SYSTEM_DOC_STANDARD"].replace("\\", "/") == str((tmp_path / "docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md").resolve()).replace("\\", "/")
    assert ctx["BUNDLE_TAXONOMY"].replace("\\", "/") == str((tmp_path / "docs/system/00_governance/bootstrap/BUNDLE_TAXONOMY.md").resolve()).replace("\\", "/")
    assert ctx["RUNTIME_GOVERNANCE"].replace("\\", "/") == str((tmp_path / "docs/system/00_governance/bootstrap/RUNTIME_GOVERNANCE.md").resolve()).replace("\\", "/")


def test_validate_declared_produced_artifacts_exist_uses_contract_paths(tmp_path: Path) -> None:
    readme = tmp_path / "docs/system/00_governance/bootstrap/README.md"
    readme.parent.mkdir(parents=True, exist_ok=True)
    readme.write_text("ok\n", encoding="utf-8")

    _validate_declared_produced_artifacts_exist(
        artifacts={},
        produces=["SYSTEM_DOCS_INDEX"],
        context={"SYSTEM_DOCS_INDEX": "docs/system/00_governance/bootstrap/README.md"},
        state={"artifacts": {}},
        project_root=tmp_path,
        step="generate_core_governance_docs",
    )


def test_validate_declared_produced_artifacts_exist_rejects_missing_declared_output(tmp_path: Path) -> None:
    with pytest.raises(ArtifactMissingError, match="declared produced artifacts are missing on disk"):
        _validate_declared_produced_artifacts_exist(
            artifacts={"SYSTEM_DOCS_INDEX": "docs/system/00_governance/bootstrap/README.md"},
            produces=["SYSTEM_DOCS_INDEX", "SYSTEM_DOC_STANDARD"],
            context={
                "SYSTEM_DOCS_INDEX": "docs/system/00_governance/bootstrap/README.md",
                "SYSTEM_DOC_STANDARD": "docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md",
            },
            state={"artifacts": {}},
            project_root=tmp_path,
            step="generate_core_governance_docs",
        )


def test_backfill_declared_produced_artifacts_binds_existing_contract_files(tmp_path: Path) -> None:
    sop = tmp_path / "docs/repo/governance/EXISTING_REPO_WORKFLOW_SOP.md"
    sop.parent.mkdir(parents=True, exist_ok=True)
    sop.write_text("ok\n", encoding="utf-8")

    artifacts = _backfill_declared_produced_artifacts(
        artifacts={"SYSTEM_DOCS_CHANGE_LOG": "docs/repo/governance/00RMD-bootstrap-change-log.md"},
        produces=["SYSTEM_DOCS_CHANGE_LOG", "EXISTING_REPO_WORKFLOW_SOP"],
        context={"EXISTING_REPO_WORKFLOW_SOP": "docs/repo/governance/EXISTING_REPO_WORKFLOW_SOP.md"},
        state={"artifacts": {}},
        project_root=tmp_path,
    )

    assert "EXISTING_REPO_WORKFLOW_SOP" in artifacts
    assert artifacts["EXISTING_REPO_WORKFLOW_SOP"].replace("\\", "/").endswith(
        "/docs/repo/governance/EXISTING_REPO_WORKFLOW_SOP.md"
    )


def test_validate_step_write_contract_config_requires_declared_writes() -> None:
    with pytest.raises(RuntimeError, match="write-capable"):
        _validate_step_write_contract_config(
            step_cfg={"result_meta_key": "IMPL_FILE", "produces": []},
            step="executor",
        )


def test_resolve_allowed_write_paths_uses_updates_and_meta(tmp_path: Path) -> None:
    project_root = tmp_path
    allowed = _resolve_allowed_write_paths(
        step_cfg={"produces": [], "updates": ["IMPL_FILE"]},
        context={"IMPL_FILE": "docs/delivery/05_implementations/IMPL-1.md"},
        state={"artifacts": {"IMPL_FILE": "docs/delivery/05_implementations/IMPL-1.md"}},
        project_root=project_root,
        meta_path=project_root / "docs/delivery/05_implementations/IMPL-1.meta.json",
    )

    assert project_root / "docs/delivery/05_implementations/IMPL-1.md" in allowed
    assert project_root / "docs/delivery/05_implementations/IMPL-1.meta.json" in allowed


def test_verify_only_allowed_paths_changed_reports_only_allowed_paths(tmp_path: Path) -> None:
    project_root = tmp_path
    allowed_path = project_root / "docs/allowed.md"
    meta_path = project_root / "docs/allowed.meta.json"
    rogue_path = project_root / "docs/rogue.md"

    for path in (allowed_path, meta_path, rogue_path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("before\n", encoding="utf-8")

    allowed_paths = {allowed_path.resolve(), meta_path.resolve()}
    before = _snapshot_allowed_write_roots(allowed_paths=allowed_paths, project_root=project_root)

    allowed_path.write_text("after\n", encoding="utf-8")
    rogue_path.write_text("changed\n", encoding="utf-8")

    changed = _verify_only_allowed_paths_changed(
        before=before,
        allowed_paths=allowed_paths,
        project_root=project_root,
        step="test_step",
    )

    assert [path.replace("\\", "/") for path in changed] == [str(allowed_path.resolve()).replace("\\", "/")]


def test_resolve_progress_file_path_prefers_global_job_step_dir() -> None:
    resolved = _resolve_progress_file_path(
        state={"backend_step_dir_rel": r".ukbe-runner\jobs\31_task_execution_v1\JOB-123\10_executor"},
        step="executor",
    )
    assert ".ukbe-runner" in resolved
    assert resolved.endswith(r"10_executor\progress.jsonl")


def test_resolve_progress_file_path_never_falls_back_to_repo_root() -> None:
    resolved = _resolve_progress_file_path(
        state={"template_group": "31_task_execution_v1", "job_id": "JOB-123"},
        step="executor",
    )
    assert resolved.endswith(r"31_task_execution_v1\JOB-123\00_executor\progress.jsonl")
    assert resolved != "progress.jsonl"


def test_resolve_meta_json_path_uses_meta_key_directly_when_already_meta(tmp_path: Path) -> None:
    """_METAJSON context keys are pre-resolved paths — no second .meta suffix."""
    project_root = tmp_path
    step_cfg = {"result_meta_key_from_context": "REVIEW_FILE_SUGGESTED_METAJSON"}
    context = {"REVIEW_FILE_SUGGESTED_METAJSON": "docs/system/00_governance/bootstrap/00DOC-test-bootstrap-validation.meta.json"}

    result = _resolve_meta_json_path(
        step_cfg=step_cfg,
        context=context,
        project_root=project_root,
    )

    expected = project_root / "docs/system/00_governance/bootstrap/00DOC-test-bootstrap-validation.meta.json"
    assert result == expected, f"Expected {expected}, got {result}"


def test_resolve_meta_json_path_applies_artifact_rel_to_meta_rel_for_artifact_key(tmp_path: Path) -> None:
    """Non-_METAJSON keys point to artifact paths — meta.json is derived."""
    project_root = tmp_path
    step_cfg = {"result_meta_key_from_context": "REVIEW_FILE_SUGGESTED"}
    context = {"REVIEW_FILE_SUGGESTED": "docs/delivery/01_initiatives/INIT-1.md"}

    result = _resolve_meta_json_path(
        step_cfg=step_cfg,
        context=context,
        project_root=project_root,
    )

    expected = project_root / "docs/delivery/01_initiatives/INIT-1.meta.json"
    assert result == expected, f"Expected {expected}, got {result}"


def test_resolve_meta_json_path_falls_back_to_step_dir(tmp_path: Path) -> None:
    """When neither meta key is present, fall back to step_dir / meta.json."""
    project_root = tmp_path
    step_dir = tmp_path / "steps" / "10_executor"
    step_dir.mkdir(parents=True, exist_ok=True)

    result = _resolve_meta_json_path(
        step_cfg={},
        context={},
        project_root=project_root,
        step_dir=step_dir,
    )

    assert result == step_dir / "meta.json"


def test_run_action_preserves_reject_code_in_step_result(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project_root = tmp_path
    artifact_rel = "docs/system/00_governance/bootstrap/validation.md"
    artifact_path = project_root / artifact_rel
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text("validation failed\n", encoding="utf-8")

    monkeypatch.setattr(
        "agent_runner_v2.runner_actions.execute",
        lambda **kwargs: ActionResult(
            status="REJECTED",
            remark="validation failed",
            artifacts={"SYSTEM_DOCS_VALIDATION": artifact_rel},
            reject_code="CORE_GOVERNANCE_VALIDATION_FAILED",
        ),
    )

    result = run_action(
        action_name="validate_core_governance_docs",
        state={},
        step="validate_core_governance_docs",
        step_cfg={
            "produces": ["SYSTEM_DOCS_VALIDATION"],
            "result_meta_key_from_context": "SYSTEM_DOCS_VALIDATION_METAJSON",
        },
        step_dir=project_root / ".ukbe-runner" / "jobs" / "wf" / "JOB-1" / "04_validate_core_governance_docs",
        project_root=project_root,
        context={"SYSTEM_DOCS_VALIDATION_METAJSON": "docs/system/00_governance/bootstrap/validation.meta.json"},
    )

    assert result.status == "REJECTED"
    assert result.reject_code == "CORE_GOVERNANCE_VALIDATION_FAILED"
