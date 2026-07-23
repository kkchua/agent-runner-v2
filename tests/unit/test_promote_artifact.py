"""Unit tests for the global promote_artifact action."""
from __future__ import annotations

from pathlib import Path

import pytest

from agent_runner_v2.actions.promote_artifact import (
    _set_status,
    _update_frontmatter_status,
    promote_artifact,
)


class TestUpdateFrontmatterStatus:
    """Tests for _update_frontmatter_status helper."""

    def test_updates_lifecycle_status_in_frontmatter(self) -> None:
        content = '---\ntemplate_id: "TEST"\nlifecycle_status: "draft"\n---\n\n# Title\n'
        result = _update_frontmatter_status(content, "approved")
        assert result is not None
        assert 'lifecycle_status: "approved"' in result
        assert "draft" not in result

    def test_returns_none_when_no_frontmatter(self) -> None:
        content = "# Title\n\nNo frontmatter here.\n"
        result = _update_frontmatter_status(content, "approved")
        assert result is None

    def test_returns_none_when_no_lifecycle_status_field(self) -> None:
        content = '---\ntemplate_id: "TEST"\nversion: "1.0"\n---\n\n# Title\n'
        result = _update_frontmatter_status(content, "approved")
        assert result is None

    def test_handles_single_quoted_value(self) -> None:
        content = "---\nlifecycle_status: 'draft'\n---\n\n# Title\n"
        result = _update_frontmatter_status(content, "approved")
        assert result is not None
        assert 'lifecycle_status: "approved"' in result

    def test_handles_unquoted_value(self) -> None:
        content = "---\nlifecycle_status: draft\n---\n\n# Title\n"
        result = _update_frontmatter_status(content, "approved")
        assert result is not None
        assert 'lifecycle_status: "approved"' in result


class TestSetStatus:
    """Tests for _set_status dispatch (frontmatter-first, body-text fallback)."""

    def test_prefers_frontmatter_over_body_text(self) -> None:
        content = '---\nlifecycle_status: "draft"\n---\n\n| Status | `draft` |\n'
        result = _set_status(content, "approved")
        assert 'lifecycle_status: "approved"' in result
        assert "| Status | `draft` |" in result

    def test_falls_back_to_table_format(self) -> None:
        content = "# Title\n\n| Status | `draft` |\n"
        result = _set_status(content, "Approved")
        assert "| Status | `Approved` |" in result

    def test_falls_back_to_kv_format(self) -> None:
        content = "# Title\n\n- Status: draft\n"
        result = _set_status(content, "Approved")
        assert "- Status: Approved" in result


class TestPromoteArtifact:
    """Tests for the promote_artifact action function."""

    def test_promotes_frontmatter_artifact(self, tmp_path: Path) -> None:
        artifact = tmp_path / "test.md"
        artifact.write_text(
            '---\ntemplate_id: "SYS-03-IN"\nlifecycle_status: "draft"\n---\n\n# Title\n',
            encoding="utf-8",
        )
        context = {"INIT_FILE": str(artifact)}
        state = {}
        step_cfg = {"promotes": "INIT_FILE", "result_meta_key": "INIT_FILE"}

        result = promote_artifact(
            context=context, state=state, step_cfg=step_cfg, project_root=tmp_path,
        )

        assert result.status == "APPROVED"
        updated = artifact.read_text(encoding="utf-8")
        assert 'lifecycle_status: "Approved"' in updated

    def test_promotes_body_text_artifact(self, tmp_path: Path) -> None:
        artifact = tmp_path / "test.md"
        artifact.write_text("| Status | `draft` |\n", encoding="utf-8")
        context = {"PLAN_FILE": str(artifact)}
        state = {}
        step_cfg = {"promotes": "PLAN_FILE", "result_meta_key": "PLAN_FILE"}

        result = promote_artifact(
            context=context, state=state, step_cfg=step_cfg, project_root=tmp_path,
        )

        assert result.status == "APPROVED"
        updated = artifact.read_text(encoding="utf-8")
        assert "`Approved`" in updated

    def test_strips_bom_during_promote(self, tmp_path: Path) -> None:
        artifact = tmp_path / "test.md"
        artifact.write_text(
            '\ufeff---\ntemplate_id: "TEST"\nlifecycle_status: "draft"\n---\n\n# Title\n',
            encoding="utf-8",
        )
        context = {"TEST_FILE": str(artifact)}
        state = {}
        step_cfg = {"promotes": "TEST_FILE", "result_meta_key": "TEST_FILE"}

        result = promote_artifact(
            context=context, state=state, step_cfg=step_cfg, project_root=tmp_path,
        )

        assert result.status == "APPROVED"
        updated = artifact.read_text(encoding="utf-8")
        assert not updated.startswith("\ufeff")
        assert 'lifecycle_status: "Approved"' in updated

    def test_rejects_when_no_promotes_config(self, tmp_path: Path) -> None:
        context = {}
        state = {}
        step_cfg = {}

        result = promote_artifact(
            context=context, state=state, step_cfg=step_cfg, project_root=tmp_path,
        )

        assert result.status == "REJECTED"
