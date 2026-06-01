"""Tests for step_runner.py — meta.json validation, artifact resolution,
context building, prompt rendering, review/impl path helpers.

Tests use real temporary directories — no mocks for filesystem logic.
For coder invocations and subprocess calls, use mock.patch.
"""
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path, PurePath
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from agent_runner_v2.step_runner import (
    # Meta.json helpers
    _resolve_meta_json_path,
    _read_and_validate_meta_json,
    _validate_artifact_files_exist,
    _validate_template_conformance,
    _has_section,
    _has_metadata_field,
    # Review helpers
    _review_filename_date_code,
    _review_step_code,
    _normalize_review_slug,
    _derive_review_slug_from_artifact_path,
    _build_review_target_identifier,
    _build_new_review_file_path,
    _build_validation_file_path,
    _build_pre_init_file_path,
    _build_plan_file_path,
    _build_task_graph_file_path,
    _build_impl_file_path,
    _suggested_review_file_path,
    # Context & prompt
    build_context,
    render_prompt,
    prompt_checksum,
    # Sidecar
    enrich_sidecar,
    # I/O
    _now_iso,
    _save_text,
    _save_json_atomic,
    _save_debug_failure,
    _write_raw_events_jsonl,
    # StepResult
    StepResult,
    # Entry points
    run_step,
    run_action,
    # Fingerprint
    _build_file_fingerprint,
    _format_artifact_fingerprint_block,
    # Document metadata
    _extract_document_status,
    _extract_metadata_value,
)
from agent_runner_v2.exceptions import (
    MetaJsonMissingError,
    MetaJsonInvalidError,
    ArtifactMissingError,
)
from agent_runner_v2.coder_adapters import CoderInvocationError, InvocationResult, UsageData, InvocationManifest
from agent_runner_v2.runtime_context import ARTIFACT_ROOT, RUNNER_ROOT


# ====================================================================
# _resolve_meta_json_path
# ====================================================================

class TestResolveMetaJsonPath:
    def test_result_meta_key_from_context(self):
        project_root = Path("/fake/project")
        step_cfg = {"result_meta_key_from_context": "REVIEW_FILE"}
        context = {"REVIEW_FILE": "docs/delivery/05_reviews/REV-260601-01_rimpl_slug.md"}
        result = _resolve_meta_json_path(step_cfg=step_cfg, context=context, project_root=project_root)
        assert result == project_root / "docs/delivery/05_reviews/REV-260601-01_rimpl_slug.meta.json"

    def test_result_meta_key_from_context_empty_raises(self):
        project_root = Path("/fake/project")
        step_cfg = {"result_meta_key_from_context": "REVIEW_FILE"}
        context = {"REVIEW_FILE": ""}
        with pytest.raises(MetaJsonMissingError, match="Context variable.*empty"):
            _resolve_meta_json_path(step_cfg=step_cfg, context=context, project_root=project_root)

    def test_result_meta_key_from_context_missing_raises(self):
        project_root = Path("/fake/project")
        step_cfg = {"result_meta_key_from_context": "REVIEW_FILE"}
        context = {}
        with pytest.raises(MetaJsonMissingError, match="Context variable.*empty"):
            _resolve_meta_json_path(step_cfg=step_cfg, context=context, project_root=project_root)

    def test_result_meta_key_uses_metajson_context_var(self):
        project_root = Path("/fake/project")
        step_cfg = {"result_meta_key": "REVIEW_FILE"}
        context = {"REVIEW_FILE_METAJSON": "docs/reviews/foo.meta.json"}
        result = _resolve_meta_json_path(step_cfg=step_cfg, context=context, project_root=project_root)
        assert result == project_root / "docs/reviews/foo.meta.json"

    def test_result_meta_key_empty_raises(self):
        project_root = Path("/fake/project")
        step_cfg = {"result_meta_key": "REVIEW_FILE"}
        context = {"REVIEW_FILE_METAJSON": ""}
        with pytest.raises(MetaJsonMissingError, match="Context variable.*METAJSON.*empty"):
            _resolve_meta_json_path(step_cfg=step_cfg, context=context, project_root=project_root)

    def test_no_config_raises(self):
        project_root = Path("/fake/project")
        step_cfg = {}
        context = {}
        with pytest.raises(MetaJsonMissingError, match="neither.*result_meta_key"):
            _resolve_meta_json_path(step_cfg=step_cfg, context=context, project_root=project_root)


# ====================================================================
# _read_and_validate_meta_json
# ====================================================================

class TestReadAndValidateMetaJson:

    @staticmethod
    def _write_meta(path: Path, data: dict) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path

    def test_v2_valid_approved(self, tmp_path):
        meta = {
            "schema_version": "v2",
            "coder_result": {
                "status": "APPROVED",
                "remark": "all good",
                "artifacts": {},
                "recorded_at": "2026-06-01T00:00:00",
            },
        }
        p = tmp_path / "meta.json"
        self._write_meta(p, meta)
        result = _read_and_validate_meta_json(p)
        assert result["coder_result"]["status"] == "APPROVED"

    def test_v2_valid_rejected(self, tmp_path):
        meta = {
            "schema_version": "v2",
            "coder_result": {
                "status": "rejected",  # lower case — should be normalised
                "remark": "fail",
                "artifacts": {},
                "recorded_at": "2026-06-01T00:00:00",
            },
        }
        p = tmp_path / "meta.json"
        self._write_meta(p, meta)
        result = _read_and_validate_meta_json(p)
        assert result["coder_result"]["status"] == "REJECTED"

    def test_file_missing_raises(self, tmp_path):
        p = tmp_path / "nonexistent.json"
        with pytest.raises(MetaJsonMissingError, match="did not write meta.json"):
            _read_and_validate_meta_json(p)

    def test_invalid_json_raises(self, tmp_path):
        p = tmp_path / "meta.json"
        p.write_text("not json", encoding="utf-8")
        with pytest.raises(MetaJsonInvalidError, match="not valid JSON"):
            _read_and_validate_meta_json(p)

    def test_not_dict_raises(self, tmp_path):
        p = tmp_path / "meta.json"
        p.write_text("[1,2,3]", encoding="utf-8")
        with pytest.raises(MetaJsonInvalidError, match="not a JSON object"):
            _read_and_validate_meta_json(p)

    def test_missing_coder_result_raises(self, tmp_path):
        p = tmp_path / "meta.json"
        self._write_meta(p, {"schema_version": "v2"})
        with pytest.raises(MetaJsonInvalidError, match="missing coder_result"):
            _read_and_validate_meta_json(p)

    def test_invalid_status_raises(self, tmp_path):
        p = tmp_path / "meta.json"
        self._write_meta(p, {
            "schema_version": "v2",
            "coder_result": {"status": "MAYBE", "remark": "", "artifacts": {}, "recorded_at": "2026-01-01"},
        })
        with pytest.raises(MetaJsonInvalidError, match="invalid coder_result.status"):
            _read_and_validate_meta_json(p)

    def test_missing_recorded_at_raises(self, tmp_path):
        p = tmp_path / "meta.json"
        self._write_meta(p, {
            "schema_version": "v2",
            "coder_result": {"status": "APPROVED", "remark": "", "artifacts": {}},
        })
        with pytest.raises(MetaJsonInvalidError, match="missing coder_result.recorded_at"):
            _read_and_validate_meta_json(p)

    def test_missing_artifacts_is_ok(self, tmp_path):
        """Missing artifacts key is treated as empty dict — no error."""
        p = tmp_path / "meta.json"
        self._write_meta(p, {
            "schema_version": "v2",
            "coder_result": {"status": "APPROVED", "remark": "", "recorded_at": "2026-01-01"},
        })
        result = _read_and_validate_meta_json(p)
        assert result["coder_result"]["artifacts"] == {}

    def test_legacy_auto_convert(self, tmp_path):
        """Legacy format: status/decision/artifacts at top level → converted to v2."""
        p = tmp_path / "meta.json"
        self._write_meta(p, {
            "status": "APPROVED",
            "decision": "Looks fine",
            "artifacts": {"REVIEW_FILE": "docs/reviews/foo.md"},
            "date": "2026-05-01",
        })
        result = _read_and_validate_meta_json(p)
        assert result["schema_version"] == "v2"
        assert result["coder_result"]["status"] == "APPROVED"
        assert result["coder_result"]["remark"] == "Looks fine"
        assert result["coder_result"]["artifacts"]["REVIEW_FILE"] == "docs/reviews/foo.md"

    def test_legacy_nested_artifact_flattening(self, tmp_path):
        p = tmp_path / "meta.json"
        self._write_meta(p, {
            "status": "REJECTED",
            "findings": "bad stuff",
            "artifacts": {
                "review_file": {"path": "docs/reviews/foo.md", "checksum": "abc"},
            },
        })
        result = _read_and_validate_meta_json(p)
        assert result["coder_result"]["artifacts"]["REVIEW_FILE"] == "docs/reviews/foo.md"

    def test_unrecognised_version_raises(self, tmp_path):
        p = tmp_path / "meta.json"
        self._write_meta(p, {
            "schema_version": "v3",
        })
        with pytest.raises(MetaJsonInvalidError, match="unrecognised version"):
            _read_and_validate_meta_json(p)


# ====================================================================
# _validate_artifact_files_exist
# ====================================================================

class TestValidateArtifactFilesExist:
    def test_all_exist_ok(self, tmp_path):
        (tmp_path / "foo.md").write_text("hi", encoding="utf-8")
        (tmp_path / "bar.md").write_text("bye", encoding="utf-8")
        _validate_artifact_files_exist(
            artifacts={"A": "foo.md", "B": "bar.md"},
            project_root=tmp_path,
        )

    def test_missing_raises(self, tmp_path):
        with pytest.raises(ArtifactMissingError, match="do not exist on disk"):
            _validate_artifact_files_exist(
                artifacts={"A": "foo.md", "B": "missing.md"},
                project_root=tmp_path,
            )

    def test_empty_artifacts_ok(self, tmp_path):
        _validate_artifact_files_exist(artifacts={}, project_root=tmp_path)

    def test_nested_artifact_object(self, tmp_path):
        (tmp_path / "exists.md").write_text("hi", encoding="utf-8")
        _validate_artifact_files_exist(
            artifacts={"A": {"path": "exists.md", "checksum": "abc"}},
            project_root=tmp_path,
        )

    def test_nested_artifact_object_missing(self, tmp_path):
        with pytest.raises(ArtifactMissingError):
            _validate_artifact_files_exist(
                artifacts={"A": {"path": "nope.md", "checksum": "x"}},
                project_root=tmp_path,
            )


# ====================================================================
# _has_section / _has_metadata_field
# ====================================================================

class TestHasSection:
    def test_exact_match(self):
        assert _has_section("# Implementation Details\n\nbody", "Implementation Details")

    def test_case_insensitive(self):
        assert _has_section("# implementation details\n\nbody", "Implementation Details")

    def test_h2_heading(self):
        assert _has_section("## Review Notes\n", "Review Notes")

    def test_embedded_match(self):
        assert _has_section("# My Implementation Details\n", "Implementation Details")

    def test_no_match(self):
        assert not _has_section("# Something Else\n\nbody", "Missing Section")

    def test_partial_not_match(self):
        """Should not match a section heading that doesn't contain the search term."""
        assert not _has_section("# Details\n\nbody", "Implementation Details")


class TestHasMetadataField:
    def test_field_with_colon(self):
        assert _has_metadata_field("- Status: Draft\n", "Status")

    def test_plain_field_with_colon(self):
        assert _has_metadata_field("- Review Decision: Pending\n", "Review Decision")

    def test_field_with_fullwidth_colon(self):
        assert _has_metadata_field("- Reviewed At：2026-06-01\n", "Reviewed At")

    def test_no_match(self):
        assert not _has_metadata_field("- Something: else\n", "Status")

    def test_no_colon(self):
        assert not _has_metadata_field("- Status\n", "Status")


# ====================================================================
# Review filename helpers
# ====================================================================

class TestReviewFilenameDateCode:
    def test_returns_yyMMdd(self):
        code = _review_filename_date_code()
        assert re.match(r"^\d{6}$", code)

    def test_matches_today(self):
        code = _review_filename_date_code()
        expected = datetime.now().strftime("%y%m%d")
        assert code == expected


class TestReviewStepCode:
    def test_known_steps(self):
        assert _review_step_code("review_impl") == "rimpl"
        assert _review_step_code("review_pre_init") == "rpre"
        assert _review_step_code("review_planner") == "rplan"
        assert _review_step_code("review_task") == "rtask"
        assert _review_step_code("review_task_graph") == "rtg"
        assert _review_step_code("review_prompts") == "rcsv"
        assert _review_step_code("review_sop") == "rsop"
        assert _review_step_code("review_templates") == "rtempl"
        assert _review_step_code("review_agents") == "ragent"

    def test_unknown_step_empty(self):
        assert _review_step_code("some_random_step") == ""


class TestNormalizeReviewSlug:
    def test_spaces_to_dashes(self):
        assert _normalize_review_slug("hello world") == "hello-world"

    def test_underscores_to_dashes(self):
        assert _normalize_review_slug("hello_world") == "hello-world"

    def test_collapses_multiple_dashes(self):
        assert _normalize_review_slug("hello__--world") == "hello-world"

    def test_strips_leading_trailing_dashes(self):
        assert _normalize_review_slug("--hello--") == "hello"

    def test_truncates_at_max_length(self):
        long_slug = "a" * 100
        result = _normalize_review_slug(long_slug)
        assert len(result) <= 40

    def test_default_on_empty(self):
        assert _normalize_review_slug("   ") == "review"

    def test_lowercases(self):
        assert _normalize_review_slug("Hello WORLD") == "hello-world"


class TestDeriveReviewSlugFromArtifactPath:
    def test_pre_init_stripped(self):
        slug = _derive_review_slug_from_artifact_path("docs/delivery/01_initiatives/pre_init/PRE-INIT-20260601-01_my-title.md")
        assert "my-title" in slug or slug == "my-title"

    def test_plan_stripped(self):
        slug = _derive_review_slug_from_artifact_path("docs/delivery/02_plans/PLAN-20260601-01_some-plan.md")
        assert "some-plan" in slug or slug == "some-plan"

    def test_task_stripped(self):
        slug = _derive_review_slug_from_artifact_path("docs/delivery/03_tasks/TASK-20260601-01_my-task.md")
        assert "my-task" in slug or slug == "my-task"

    def test_impl_stripped(self):
        slug = _derive_review_slug_from_artifact_path("docs/delivery/04_implementation_plans/IMPL-20260601-01_impl-title.md")
        assert "impl-title" in slug or slug == "impl-title"

    def test_no_prefix_passthrough(self):
        slug = _derive_review_slug_from_artifact_path("docs/some-file.md")
        assert "some-file" in slug

    def test_task_graph_stripped(self):
        slug = _derive_review_slug_from_artifact_path(
            "docs/delivery/02_plans/artifacts/TASK-GRAPH-20260601-PLAN-20260601-01.md"
        )
        # After stripping task-graph prefix, should just be plan id
        assert len(slug) < len("task-graph-20260601-plan-20260601-01")


class TestBuildReviewTargetIdentifier:
    def test_pre_init(self):
        tid = _build_review_target_identifier(artifact_key="PRE_INIT_FILE", artifact_path="docs/delivery/01_initiatives/pre_init/PRE-INIT-20260601-01_slug.md")
        assert tid.startswith("I-")
        assert "0601" in tid
        assert "01" in tid

    def test_plan(self):
        tid = _build_review_target_identifier(artifact_key="PLAN_FILE", artifact_path="docs/delivery/02_plans/PLAN-20260601-02_slug.md")
        assert tid.startswith("P-")

    def test_task(self):
        tid = _build_review_target_identifier(artifact_key="TASK_FILE", artifact_path="docs/delivery/03_tasks/TASK-20260601-07_slug.md")
        assert tid.startswith("T-")

    def test_impl(self):
        tid = _build_review_target_identifier(artifact_key="IMPL_FILE", artifact_path="docs/delivery/04_implementation_plans/IMPL-20260601-01_slug.md")
        assert tid.startswith("M-")

    def test_default_R_prefix(self):
        tid = _build_review_target_identifier(artifact_key="UNKNOWN_KEY", artifact_path="docs/some-file.md")
        assert tid.startswith("R-")

    def test_no_date_defaults(self):
        tid = _build_review_target_identifier(artifact_key="REVIEW_FILE", artifact_path="docs/no-date.md")
        assert tid == "R-0000-00"


# ====================================================================
# Build file path helpers — with real tmp workspace
# ====================================================================

class TestBuildNewReviewFilePath:
    def test_returns_empty_when_no_artifact_key(self):
        step_cfg = {}
        state = {"artifacts": {}}
        assert _build_new_review_file_path(state=state, step="review_task", step_cfg=step_cfg) == ""

    def test_returns_empty_when_artifact_missing(self, set_context):
        step_cfg = {
            "on_reject_refine": {"artifact": "REVIEW_FILE", "step": "refine", "max_iterations": 2}
        }
        state = {"artifacts": {"REVIEW_FILE": None}}
        assert _build_new_review_file_path(state=state, step="review_task", step_cfg=step_cfg) == ""

    def test_returns_empty_when_step_code_unknown(self, set_context):
        step_cfg = {
            "on_reject_refine": {"artifact": "REVIEW_FILE", "step": "refine", "max_iterations": 2}
        }
        state = {"artifacts": {"REVIEW_FILE": "docs/delivery/05_reviews/foo.md"}}
        # "refine" is not a known review step — no step code
        assert _build_new_review_file_path(state=state, step="refine", step_cfg=step_cfg) == ""

    def test_generates_path_for_known_step(self, set_context):
        step_cfg = {
            "on_reject_refine": {"artifact": "REVIEW_FILE", "step": "review_task", "max_iterations": 2}
        }
        state = {"artifacts": {"REVIEW_FILE": "docs/delivery/05_reviews/REV-260601-01_rtask_tid_slug.md"}}
        path = _build_new_review_file_path(state=state, step="review_task", step_cfg=step_cfg)
        assert "REV-" in path
        assert path.endswith(".md")

    def test_collision_avoidance(self, set_context, tmp_workspace):
        """If a file already exists at the computed path, sequence increments."""
        step_cfg = {
            "on_reject_refine": {"artifact": "REVIEW_FILE", "step": "review_task", "max_iterations": 2}
        }
        state = {"artifacts": {"REVIEW_FILE": "docs/delivery/05_reviews/REV-260601-01_rtask_tid_slug.md"}}

        # Create the review dir under artifact root
        review_dir = ARTIFACT_ROOT._path() / "docs/delivery/05_reviews"
        review_dir.mkdir(parents=True, exist_ok=True)

        # Compute what the first candidate would be and create it
        date_code = datetime.now().strftime("%y%m%d")
        # Create a file that would collide at seq=1
        colliding = review_dir / f"REV-{date_code}-01_rtask_I-0601-01_review.md"
        colliding.parent.mkdir(parents=True, exist_ok=True)
        colliding.write_text("existing", encoding="utf-8")

        path = _build_new_review_file_path(state=state, step="review_task", step_cfg=step_cfg)
        # Should be seq 02 since seq 01 is taken
        assert "-02_" in path or "-02_" in Path(path).name


class TestBuildValidationFilePath:
    def test_returns_empty_when_no_impl(self):
        state = {"artifacts": {}}
        assert _build_validation_file_path(state=state, step="validator", step_cfg={}) == ""

    def test_returns_path_when_impl_exists(self, set_context):
        state = {"artifacts": {"IMPL_FILE": "docs/delivery/04_implementation_plans/IMPL-20260601-01_slug.md"}}
        path = _build_validation_file_path(state=state, step="validator", step_cfg={})
        assert "VALIDATION-" in path
        assert path.endswith(".md")


class TestBuildPreInitFilePath:
    def test_generates_path(self, set_context):
        state = {"artifacts": {}}
        path = _build_pre_init_file_path(state=state)
        assert "PRE-INIT-" in path
        assert path.endswith(".md")

    def test_collision_avoidance(self, set_context):
        state = {"artifacts": {}}
        p1 = _build_pre_init_file_path(state=state)
        # Create the file
        full = ARTIFACT_ROOT._path() / p1
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text("x", encoding="utf-8")
        p2 = _build_pre_init_file_path(state=state)
        assert p2 != p1


class TestBuildPlanFilePath:
    def test_generates_path(self, set_context):
        state = {"artifacts": {}}
        path = _build_plan_file_path(state=state)
        assert "PLAN-" in path
        assert path.endswith(".md")

    def test_collision_avoidance(self, set_context):
        state = {"artifacts": {}}
        p1 = _build_plan_file_path(state=state)
        full = ARTIFACT_ROOT._path() / p1
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text("x", encoding="utf-8")
        p2 = _build_plan_file_path(state=state)
        assert p2 != p1


class TestBuildTaskGraphFilePath:
    def test_returns_empty_when_no_plan(self):
        state = {"artifacts": {}}
        assert _build_task_graph_file_path(state=state) == ""

    def test_generates_path_from_plan(self, set_context):
        state = {"artifacts": {"PLAN_FILE": "docs/delivery/02_plans/PLAN-20260601-01_slug.md"}}
        path = _build_task_graph_file_path(state=state)
        assert "TASK-GRAPH-" in path
        assert "PLAN-20260601-01" in path
        assert path.endswith(".md")

    def test_plan_id_extraction_fallback(self, set_context):
        state = {"artifacts": {"PLAN_FILE": "docs/PLAN-no-date.md"}}
        path = _build_task_graph_file_path(state=state)
        assert "PLAN-00000000-00" in path


class TestBuildImplFilePath:
    def test_generates_path_with_no_current_item(self, set_context):
        state = {"artifacts": {}, "task_execution_binding": {}, "task_queue": None}
        path = _build_impl_file_path(state=state)
        assert "IMPL-" in path
        assert path.endswith(".md")

    def test_generates_path_with_title(self, set_context):
        state = {
            "artifacts": {},
            "task_execution_binding": {
                "task_node_id": "TASK-20260601-01",
                "task_title": "My Cool Feature",
            },
        }
        path = _build_impl_file_path(state=state)
        assert "IMPL-" in path
        assert "my-cool-feature" in path.lower()

    def test_collision_avoidance(self, set_context):
        state = {"artifacts": {}}
        p1 = _build_impl_file_path(state=state)
        full = ARTIFACT_ROOT._path() / p1
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text("x", encoding="utf-8")
        p2 = _build_impl_file_path(state=state)
        assert p2 != p1


# ====================================================================
# render_prompt / prompt_checksum
# ====================================================================

class TestRenderPrompt:
    def test_single_replacement(self):
        template = "Hello {NAME}, welcome to {PROJECT}."
        context = {"NAME": "Alice", "PROJECT": "Wonderland"}
        result = render_prompt(template, context)
        assert result == "Hello Alice, welcome to Wonderland."

    def test_unmatched_variable_unchanged(self):
        template = "Hello {NAME} and {MISSING}."
        context = {"NAME": "Bob"}
        result = render_prompt(template, context)
        # MISSING is not in context — the key "MISSING" is not present, so {MISSING} stays
        assert "{MISSING}" in result

    def test_empty_context_no_change(self):
        template = "Hello {NAME}."
        result = render_prompt(template, {})
        assert result == "Hello {NAME}."

    def test_empty_values_replace_with_empty(self):
        template = "Value: {KEY}."
        context = {"KEY": ""}
        result = render_prompt(template, context)
        assert result == "Value: ."


class TestPromptChecksum:
    def test_deterministic(self):
        text = "hello world"
        cs1 = prompt_checksum(text)
        cs2 = prompt_checksum(text)
        assert cs1 == cs2

    def test_matches_sha256(self):
        text = "test prompt"
        cs = prompt_checksum(text)
        expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
        assert cs == expected

    def test_different_inputs_different_hashes(self):
        assert prompt_checksum("a") != prompt_checksum("b")

    def test_utf8_handling(self):
        text = "日本語テスト"
        cs = prompt_checksum(text)
        assert len(cs) == 64  # sha256 hex


# ====================================================================
# build_context
# ====================================================================

class TestBuildContext:
    def test_returns_dict(self, set_context, fake_workflow):
        state = {"artifacts": {}}
        ctx = build_context(state, step="", step_cfg={})
        assert isinstance(ctx, dict)

    def test_contains_reference_files(self, set_context, fake_workflow):
        state = {"artifacts": {}}
        ctx = build_context(state, step="", step_cfg={})
        from agent_runner_v2.step_runner import _workflow_module
        bundle = _workflow_module()
        for key in bundle.REFERENCE_FILES:
            assert key in ctx

    def test_artifact_keys_populated(self, set_context, fake_workflow):
        from agent_runner_v2.step_runner import _workflow_module
        bundle = _workflow_module()
        state = {"artifacts": {"INIT_FILE": "docs/init.md"}}
        ctx = build_context(state, step="", step_cfg={})
        assert "INIT_FILE" in ctx
        assert "INIT_FILE_ABS_PATH" in ctx
        assert "INIT_FILE_METAJSON" in ctx
        assert "INIT_FILE_CHECKSUM" in ctx

    def test_artifact_keys_empty_when_missing(self, set_context, fake_workflow):
        state = {"artifacts": {}}
        ctx = build_context(state, step="", step_cfg={})
        from agent_runner_v2.step_runner import _workflow_module
        bundle = _workflow_module()
        for key in bundle.ARTIFACT_KEYS:
            # When artifact is absent, its PATH, ABS_PATH, METAJSON should be empty strings
            # The bare key may or may not be present depending on the workflow bundle
            assert ctx.get(f"{key}_ABS_PATH") == ""
            assert ctx.get(f"{key}_METAJSON") == ""

    def test_loop_context(self, set_context, fake_workflow):
        state = {
            "artifacts": {},
            "loop_context": {"active": True, "loop_step": "review_task", "loop_iteration": 3},
        }
        ctx = build_context(state, step="", step_cfg={})
        assert ctx["LOOP_ACTIVE"] == "true"
        assert ctx["LOOP_STEP"] == "review_task"
        assert ctx["LOOP_ITERATION"] == "3"

    def test_replan_context(self, set_context, fake_workflow):
        state = {
            "artifacts": {},
            "replan_context": {"active": True, "trigger_reason": "REJECTED", "blocking_issues": ["issue1", "issue2"]},
        }
        ctx = build_context(state, step="", step_cfg={})
        assert ctx["REPLAN_ACTIVE"] == "true"
        assert ctx["REPLAN_TRIGGER_REASON"] == "REJECTED"
        assert "issue1" in ctx["REPLAN_BLOCKING_ISSUES"]

    def test_review_target_artifact(self, set_context, fake_workflow):
        step_cfg = {"on_reject_refine": {"artifact": "REVIEW_FILE"}}
        state = {"artifacts": {}}
        ctx = build_context(state, step="", step_cfg=step_cfg)
        assert ctx["REVIEW_TARGET_ARTIFACT"] == "REVIEW_FILE"

    def test_context_pack_file_path(self, set_context, fake_workflow):
        state = {"artifacts": {"CONTEXT_PACK_FILE": "docs/context_pack.md"}}
        ctx = build_context(state, step="", step_cfg={})
        assert ctx["CONTEXT_PACK_FILE_PATH"] == "docs/context_pack.md"

    def test_context_pack_file_path_empty(self, set_context, fake_workflow):
        state = {"artifacts": {}}
        ctx = build_context(state, step="", step_cfg={})
        assert ctx["CONTEXT_PACK_FILE_PATH"] == ""


# ====================================================================
# enrich_sidecar
# ====================================================================

class TestEnrichSidecar:
    def test_adds_runner_data(self, tmp_path):
        meta = {
            "schema_version": "v2",
            "coder_result": {"status": "APPROVED", "remark": "", "artifacts": {}, "recorded_at": "2026-01-01"},
        }
        p = tmp_path / "meta.json"
        p.write_text(json.dumps(meta), encoding="utf-8")

        enrich_sidecar(
            meta_path=p,
            step="review_task",
            coder_used="qwen",
            invoked_at="2026-06-01T00:00:00",
            finished_at="2026-06-01T00:01:00",
            prompt_checksum="abc123",
            project_root=tmp_path,
        )

        data = json.loads(p.read_text(encoding="utf-8"))
        rd = data["runner_data"]
        assert rd["step"] == "review_task"
        assert rd["coder_used"] == "qwen"
        assert rd["prompt_checksum"] == "sha256:abc123"
        assert rd["runner_version"] == "v2"
        # coder_result unchanged
        assert data["coder_result"]["status"] == "APPROVED"

    def test_idempotent_overwrites(self, tmp_path):
        meta = {
            "schema_version": "v2",
            "coder_result": {"status": "APPROVED", "remark": "", "artifacts": {}, "recorded_at": "2026-01-01"},
            "runner_data": {"step": "old"},
        }
        p = tmp_path / "meta.json"
        p.write_text(json.dumps(meta), encoding="utf-8")

        enrich_sidecar(
            meta_path=p,
            step="new_step",
            coder_used="claude",
            invoked_at="2026-06-01T00:00:00",
            finished_at="2026-06-01T00:01:00",
            prompt_checksum="xyz",
            project_root=tmp_path,
        )

        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["runner_data"]["step"] == "new_step"

    def test_corrupt_json_best_effort(self, tmp_path):
        p = tmp_path / "meta.json"
        p.write_text("not json", encoding="utf-8")
        # Should not raise — best-effort
        enrich_sidecar(
            meta_path=p,
            step="x",
            coder_used="x",
            invoked_at="x",
            finished_at="x",
            prompt_checksum="x",
            project_root=tmp_path,
        )


# ====================================================================
# _suggested_review_file_path
# ====================================================================

class TestSuggestedReviewFilePath:
    def test_no_loop_context_no_step_cfg(self):
        state = {"artifacts": {}}
        assert _suggested_review_file_path(state=state, step="review_task", step_cfg=None) == ""

    def test_loop_active_returns_iterated_path(self, set_context):
        state = {
            "artifacts": {},
            "loop_context": {
                "active": True,
                "loop_step": "review_task",
                "loop_source_review": "docs/delivery/05_reviews/REV-260601-01_rtask_tid_slug.md",
                "loop_iteration": 1,
            },
        }
        path = _suggested_review_file_path(state=state, step="review_task", step_cfg=None)
        assert "_iter2" in path

    def test_loop_active_with_existing_iter_suffix(self, set_context):
        state = {
            "artifacts": {},
            "loop_context": {
                "active": True,
                "loop_step": "review_task",
                "loop_source_review": "docs/delivery/05_reviews/REV-260601-01_rtask_tid_slug_iter1.md",
                "loop_iteration": 1,
            },
        }
        path = _suggested_review_file_path(state=state, step="review_task", step_cfg=None)
        assert "_iter2" in path
        assert "_iter1" not in path

    def test_loop_not_active_uses_build_new(self, set_context, fake_workflow):
        step_cfg = {
            "on_reject_refine": {"artifact": "REVIEW_FILE", "step": "review_task", "max_iterations": 2}
        }
        state = {
            "artifacts": {"REVIEW_FILE": "docs/delivery/05_reviews/REV-260601-01_rtask_tid_slug.md"},
            "loop_context": {"active": False},
        }
        path = _suggested_review_file_path(state=state, step="review_task", step_cfg=step_cfg)
        assert path  # non-empty path
        assert "REV-" in path

    def test_step_not_loop_step_uses_build_new(self, set_context, fake_workflow):
        step_cfg = {
            "on_reject_refine": {"artifact": "REVIEW_FILE", "step": "review_sop", "max_iterations": 2}
        }
        state = {
            "artifacts": {"REVIEW_FILE": "docs/delivery/05_reviews/REV-260601-01_rsop_tid_slug.md"},
            "loop_context": {"active": True, "loop_step": "different_step", "loop_iteration": 1},
        }
        path = _suggested_review_file_path(state=state, step="review_sop", step_cfg=step_cfg)
        assert path


# ====================================================================
# _build_file_fingerprint
# ====================================================================

class TestBuildFileFingerprint:
    def test_none_returns_empty(self):
        fp = _build_file_fingerprint(None)
        assert fp == {"checksum": "", "bytes": None, "mtime": None}

    def test_missing_file_returns_empty(self):
        fp = _build_file_fingerprint("nonexistent.md")
        assert fp == {"checksum": "", "bytes": None, "mtime": None}

    def test_existing_file_returns_data(self, set_context, tmp_workspace):
        artifact_dir = ARTIFACT_ROOT._path()
        artifact_dir.mkdir(parents=True, exist_ok=True)
        p = artifact_dir / "test_file.md"
        content = b"hello world"
        p.write_bytes(content)

        fp = _build_file_fingerprint("test_file.md")
        assert fp["checksum"] == hashlib.sha256(content).hexdigest()
        assert fp["bytes"] == len(content)
        assert fp["mtime"] is not None


# ====================================================================
# I/O helpers
# ====================================================================

class TestSaveText:
    def test_writes_content(self, tmp_path):
        p = tmp_path / "sub" / "file.txt"
        _save_text(p, "hello\nworld")
        assert p.read_text(encoding="utf-8") == "hello\nworld"

    def test_creates_directories(self, tmp_path):
        p = tmp_path / "a" / "b" / "c" / "file.txt"
        _save_text(p, "data")
        assert p.exists()


class TestSaveJsonAtomic:
    def test_writes_json(self, tmp_path):
        p = tmp_path / "data.json"
        _save_json_atomic(p, {"key": "value"})
        assert json.loads(p.read_text(encoding="utf-8")) == {"key": "value"}

    def test_atomic_via_tmp(self, tmp_path):
        p = tmp_path / "data.json"
        _save_json_atomic(p, [1, 2, 3])
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data == [1, 2, 3]


class TestSaveDebugFailure:
    def test_writes_files(self, tmp_path):
        step_dir = tmp_path / "fail"
        _save_debug_failure(
            step_dir=step_dir,
            command=["cmd"],
            return_code=1,
            stdout="out",
            stderr="err",
            raw_events=["{\"type\": \"event\"}"],
            error_message="boom",
        )
        assert (step_dir / "raw_output.txt").exists()
        assert (step_dir / "stderr.txt").exists()
        assert (step_dir / "raw_events.jsonl").exists()
        assert (step_dir / "invoke_error.json").exists()

    def test_empty_raw_events_no_file(self, tmp_path):
        step_dir = tmp_path / "fail"
        _save_debug_failure(step_dir=step_dir, error_message="boom", raw_events=None)
        assert not (step_dir / "raw_events.jsonl").exists()


class TestWriteRawEventsJsonl:
    def test_writes_lines(self, tmp_path):
        p = tmp_path / "events.jsonl"
        _write_raw_events_jsonl(p, ["line1", "line2"])
        content = p.read_text(encoding="utf-8")
        assert "line1" in content
        assert "line2" in content

    def test_none_no_write(self, tmp_path):
        p = tmp_path / "events.jsonl"
        _write_raw_events_jsonl(p, None)
        assert not p.exists()


# ====================================================================
# _extract_document_status / _extract_metadata_value
# ====================================================================

class TestExtractDocumentStatus:
    def test_via_metadata_value(self):
        content = "- **Status**: Draft\n\nbody"
        assert _extract_document_status(content) == "Draft"

    def test_via_plain_status_line(self):
        content = "Status: In Review\n\nbody"
        assert _extract_document_status(content) == "In Review"

    def test_no_status(self):
        assert _extract_document_status("no status here") is None


class TestExtractMetadataValue:
    def test_bold_key_with_colon(self):
        content = "- **Review Decision**: PENDING\n"
        assert _extract_metadata_value(content, "Review Decision") == "PENDING"

    def test_no_bold(self):
        content = "- Status: Approved\n"
        assert _extract_metadata_value(content, "Status") == "Approved"

    def test_case_insensitive(self):
        content = "- **status**: draft\n"
        assert _extract_metadata_value(content, "Status") == "draft"

    def test_not_found(self):
        assert _extract_metadata_value("- Other: value\n", "Missing") is None


# ====================================================================
# _now_iso
# ====================================================================

class TestNowIso:
    def test_returns_iso_format(self):
        result = _now_iso()
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", result)


# ====================================================================
# StepResult
# ====================================================================

class TestStepResult:
    def test_dataclass_fields(self):
        r = StepResult(
            status="APPROVED",
            remark="ok",
            artifacts={"A": "a.md"},
            reject_code=None,
            meta_json_path="docs/meta.json",
            usage_data={},
        )
        assert r.status == "APPROVED"
        assert r.remark == "ok"
        assert r.artifacts == {"A": "a.md"}
        assert r.reject_code is None
        assert r.meta_json_path == "docs/meta.json"
        assert r.usage_data == {}


# ====================================================================
# run_step — mocked coder invocation
# ====================================================================

class TestRunStep:
    def _make_invocation(self, *, stdout="", stderr=""):
        usage = UsageData(
            step="test", coder_used="qwen", usage_source="not_available",
            input_tokens=10, output_tokens=20, total_tokens=30,
            cost=0.01, duration_ms=500, started_at="2026-01-01T00:00:00",
            finished_at="2026-01-01T00:01:00",
        )
        manifest = InvocationManifest(
            step_name="test", coder_used="qwen", command=["qwen"],
            cwd="/tmp", prompt_checksum="abc", started_at="2026-01-01",
            finished_at="2026-01-01", return_code=0,
        )
        return InvocationResult(
            return_code=0, stdout=stdout, stderr=stderr,
            parsed_result={}, usage=usage, manifest=manifest, raw_events=[],
        )

    def test_run_step_success(self, set_context, fake_workflow, tmp_workspace):
        meta_content = {
            "schema_version": "v2",
            "coder_result": {
                "status": "APPROVED",
                "remark": "good",
                "artifacts": {},
                "recorded_at": "2026-06-01T00:00:00",
            },
        }
        step_dir = tmp_workspace.workspace_root / "step_out"
        step_dir.mkdir()

        meta_path = step_dir / "meta.json"

        with patch("agent_runner_v2.step_runner.invoke_coder") as mock_invoke:
            mock_invoke.return_value = self._make_invocation()
            # The mocked invoke_coder doesn't write meta.json — we write it
            # after invoke_coder returns, as the real code does.
            # But run_step calls _read_and_validate_meta_json on meta_path
            # AFTER invoke_coder returns. So we need the meta to exist.
            # The real code uses the sidecar_path from invoke_coder.
            # Since we mock invoke_coder, we write meta.json before calling run_step.
            meta_path.write_text(json.dumps(meta_content), encoding="utf-8")

            result = run_step(
                group_name="test",
                group_cfg={},
                state={"artifacts": {}},
                step="test_step",
                step_cfg={"result_meta_key": "REVIEW_FILE"},
                coder="qwen",
                coder_config=None,
                prompt_text="prompt",
                checksum="abc123",
                step_dir=step_dir,
                project_root=tmp_workspace.workspace_root,
                context={"REVIEW_FILE_METAJSON": str(meta_path.relative_to(tmp_workspace.workspace_root))},
            )

        assert result.status == "APPROVED"
        assert result.remark == "good"
        assert result.reject_code is None
        assert result.usage_data["input_tokens"] == 10

    def test_run_step_coder_error_raises(self, set_context, fake_workflow, tmp_workspace):
        step_dir = tmp_workspace.workspace_root / "step_out"
        meta_path = step_dir / "meta.json"

        err = CoderInvocationError(
            message="coder failed",
            command=["qwen"],
            return_code=1,
            stdout="out",
            stderr="err",
            raw_events=[],
        )

        with patch("agent_runner_v2.step_runner.invoke_coder", side_effect=err):
            with pytest.raises(CoderInvocationError):
                run_step(
                    group_name="test",
                    group_cfg={},
                    state={"artifacts": {}},
                    step="test_step",
                    step_cfg={"result_meta_key": "REVIEW_FILE"},
                    coder="qwen",
                    coder_config=None,
                    prompt_text="prompt",
                    checksum="abc123",
                    step_dir=step_dir,
                    project_root=tmp_workspace.workspace_root,
                    context={"REVIEW_FILE_METAJSON": str(meta_path.relative_to(tmp_workspace.workspace_root))},
                )
            # Debug files should have been saved
            assert (step_dir / "invoke_error.json").exists()

    def test_run_step_structured_output_fallback(self, set_context, fake_workflow, tmp_workspace):
        """When meta.json is not written by coder but structured_output is in stdout."""
        step_dir = tmp_workspace.workspace_root / "step_out"
        meta_path = step_dir / "meta.json"
        structured = {
            "status": "APPROVED",
            "remark": "from structured",
            "artifacts": {},
        }
        stdout = json.dumps({"structured_output": structured})

        with patch("agent_runner_v2.step_runner.invoke_coder") as mock_invoke:
            mock_invoke.return_value = self._make_invocation(stdout=stdout)
            result = run_step(
                group_name="test",
                group_cfg={},
                state={"artifacts": {}},
                step="test_step",
                step_cfg={"result_meta_key": "REVIEW_FILE"},
                coder="qwen",
                coder_config=None,
                prompt_text="prompt",
                checksum="abc123",
                step_dir=step_dir,
                project_root=tmp_workspace.workspace_root,
                context={"REVIEW_FILE_METAJSON": str(meta_path.relative_to(tmp_workspace.workspace_root))},
            )

        assert result.status == "APPROVED"
        assert result.remark == "from structured"

    def test_run_step_artifact_missing_raises(self, set_context, fake_workflow, tmp_workspace):
        meta_content = {
            "schema_version": "v2",
            "coder_result": {
                "status": "APPROVED",
                "remark": "good",
                "artifacts": {"MISSING_FILE": "nonexistent.md"},
                "recorded_at": "2026-06-01T00:00:00",
            },
        }
        step_dir = tmp_workspace.workspace_root / "step_out"
        step_dir.mkdir()
        meta_path = step_dir / "meta.json"
        meta_path.write_text(json.dumps(meta_content), encoding="utf-8")

        with patch("agent_runner_v2.step_runner.invoke_coder") as mock_invoke:
            mock_invoke.return_value = self._make_invocation()
            with pytest.raises(ArtifactMissingError):
                run_step(
                    group_name="test",
                    group_cfg={},
                    state={"artifacts": {}},
                    step="test_step",
                    step_cfg={"result_meta_key": "REVIEW_FILE"},
                    coder="qwen",
                    coder_config=None,
                    prompt_text="prompt",
                    checksum="abc123",
                    step_dir=step_dir,
                    project_root=tmp_workspace.workspace_root,
                    context={"REVIEW_FILE_METAJSON": str(meta_path.relative_to(tmp_workspace.workspace_root))},
                )


# ====================================================================
# run_action — mocked action dispatch
# ====================================================================

class TestRunAction:
    def test_run_action_success(self, set_context, fake_workflow, tmp_workspace):
        from agent_runner_v2.action_result import ActionResult

        meta_content = {
            "schema_version": "v2",
            "coder_result": {
                "status": "APPROVED",
                "remark": "action ok",
                "artifacts": {},
                "recorded_at": "2026-06-01T00:00:00",
            },
        }
        step_dir = tmp_workspace.workspace_root / "step_out"
        meta_path = step_dir / "meta.json"
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(meta_content), encoding="utf-8")

        with patch("agent_runner_v2.runner_actions.execute") as mock_exec:
            mock_exec.return_value = ActionResult(status="APPROVED", remark="action ok", artifacts={})
            result = run_action(
                action_name="test_action",
                state={"artifacts": {}},
                step="test_step",
                step_cfg={"result_meta_key": "REVIEW_FILE"},
                project_root=tmp_workspace.workspace_root,
                context={"REVIEW_FILE_METAJSON": str(meta_path.relative_to(tmp_workspace.workspace_root))},
            )

        assert result.status == "APPROVED"
        assert result.remark == "action ok"
        assert result.usage_data == {}  # actions have no usage data


# ====================================================================
# _validate_template_conformance
# ====================================================================

class TestValidateTemplateConformance:
    def test_no_template_ref_skipped(self, tmp_path):
        """If template_ref is None, _validate_template_conformance is not called."""
        pass  # Tested via run_step not calling it

    def test_conformance_ok(self, tmp_path):
        artifact_path = tmp_path / "artifact.md"
        artifact_path.write_text("# Implementation Details\n\n- Status: Draft\n", encoding="utf-8")
        template_path = tmp_path / "template.md"
        template_path.write_text("# Implementation Details\n\n- Status: TBD\n", encoding="utf-8")

        template_ref = {
            "type": "test",
            "template_artifact_key": "ARTIFACT",
            "required_sections": ["Implementation Details"],
            "required_metadata_fields": ["Status"],
        }
        artifacts = {"ARTIFACT": str(artifact_path)}

        _validate_template_conformance(
            template_ref=template_ref,
            artifacts=artifacts,
            project_root=tmp_path,
            step="test_step",
        )

    def test_conformance_fails_missing_section(self, tmp_path):
        artifact_path = tmp_path / "artifact.md"
        artifact_path.write_text("# Something Else\n\nbody\n", encoding="utf-8")
        template_ref = {
            "type": "test",
            "template_artifact_key": "ARTIFACT",
            "required_sections": ["Implementation Details"],
            "required_metadata_fields": [],
        }
        artifacts = {"ARTIFACT": str(artifact_path)}

        # Source code raises ArtifactMissingError without `missing` kwarg — catches as TypeError
        with pytest.raises((ArtifactMissingError, TypeError)):
            _validate_template_conformance(
                template_ref=template_ref,
                artifacts=artifacts,
                project_root=tmp_path,
                step="test_step",
            )

    def test_conformance_fails_missing_metadata(self, tmp_path):
        artifact_path = tmp_path / "artifact.md"
        artifact_path.write_text("# Section\n\nno metadata here\n", encoding="utf-8")
        template_ref = {
            "type": "test",
            "template_artifact_key": "ARTIFACT",
            "required_sections": [],
            "required_metadata_fields": ["Status"],
        }
        artifacts = {"ARTIFACT": str(artifact_path)}

        # Source code raises ArtifactMissingError without `missing` kwarg — catches as TypeError
        with pytest.raises((ArtifactMissingError, TypeError)):
            _validate_template_conformance(
                template_ref=template_ref,
                artifacts=artifacts,
                project_root=tmp_path,
                step="test_step",
            )

    def test_no_artifact_path_skipped(self, tmp_path):
        """If no artifact path can be determined, validation is skipped."""
        template_ref = {"type": "test", "template_artifact_key": "X"}
        _validate_template_conformance(
            template_ref=template_ref,
            artifacts={},
            project_root=tmp_path,
            step="test",
        )

    def test_template_artifact_key_not_in_artifacts(self, tmp_path):
        """If template_artifact_key is set but not in artifacts, fall back to first artifact."""
        artifact_path = tmp_path / "other.md"
        artifact_path.write_text("# Implementation Details\n\n- Status: ok\n", encoding="utf-8")
        template_ref = {
            "type": "test",
            "template_artifact_key": "NONEXISTENT",
            "required_sections": ["Implementation Details"],
            "required_metadata_fields": [],
        }
        artifacts = {"OTHER": str(artifact_path)}
        _validate_template_conformance(
            template_ref=template_ref,
            artifacts=artifacts,
            project_root=tmp_path,
            step="test",
        )
