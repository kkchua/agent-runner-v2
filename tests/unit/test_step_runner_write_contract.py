from __future__ import annotations

from pathlib import Path

import pytest

from agent_runner_v2.exceptions import ArtifactMissingError
from agent_runner_v2.step_runner import (
    _resolve_meta_json_path,
    _resolve_progress_file_path,
    _resolve_allowed_write_paths,
    _snapshot_allowed_write_roots,
    _validate_artifacts_in_produces_list,
    _validate_step_write_contract_config,
    _verify_only_allowed_paths_changed,
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


def test_verify_only_allowed_paths_changed_rejects_unauthorized_files(tmp_path: Path) -> None:
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

    with pytest.raises(ArtifactMissingError, match="outside the declared write contract"):
        _verify_only_allowed_paths_changed(
            before=before,
            allowed_paths=allowed_paths,
            project_root=project_root,
            step="test_step",
        )


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
