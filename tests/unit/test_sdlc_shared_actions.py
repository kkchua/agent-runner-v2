"""Unit tests for SDLC shared actions."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent_runner_v2.actions.sdlc_shared_actions import (
    _update_frontmatter_status,
    promote_artifact,
    promote_to_requirement,
    promote_all,
    aggregate_executions,
    create_backup,
    generate_sync_log,
    commit_changes,
)


class TestUpdateFrontmatterStatus:
    """Tests for _update_frontmatter_status helper."""

    def test_updates_existing_status(self) -> None:
        """Test updating existing lifecycle_status field."""
        content = """---
template_id: "TEST"
lifecycle_status: "draft"
---

# Test Document
"""
        result = _update_frontmatter_status(content, "approved")
        
        assert 'lifecycle_status: "approved"' in result
        assert 'lifecycle_status: "draft"' not in result

    def test_adds_status_if_missing(self) -> None:
        """Test adding lifecycle_status field if not present."""
        content = """---
template_id: "TEST"
---

# Test Document
"""
        result = _update_frontmatter_status(content, "approved")
        
        assert 'lifecycle_status: "approved"' in result

    def test_preserves_content_after_frontmatter(self) -> None:
        """Test that content after frontmatter is preserved."""
        content = """---
template_id: "TEST"
lifecycle_status: "draft"
---

# Test Document

Some content here.
"""
        result = _update_frontmatter_status(content, "approved")
        
        assert "# Test Document" in result
        assert "Some content here." in result

    def test_returns_unchanged_if_no_frontmatter(self) -> None:
        """Test that content without frontmatter is returned unchanged."""
        content = "# Test Document\n\nNo frontmatter here."
        
        result = _update_frontmatter_status(content, "approved")
        
        assert result == content


class TestPromoteArtifact:
    """Tests for promote_artifact action."""

    def test_promotes_artifact_to_approved(self, tmp_path: Path) -> None:
        """Test that promote_artifact changes status to approved."""
        # Create test artifact
        artifact_path = tmp_path / "test.md"
        artifact_path.write_text("""---
template_id: "TEST"
lifecycle_status: "draft"
---

# Test
""")
        
        context = {"TEST_FILE": str(artifact_path)}
        state = {"artifacts": {"TEST_FILE": str(artifact_path)}}
        step_cfg = {"promotes": "TEST_FILE"}
        
        result = promote_artifact(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "APPROVED"
        assert "TEST_FILE" in result.artifacts
        
        # Verify file was updated
        updated_content = artifact_path.read_text()
        assert 'lifecycle_status: "approved"' in updated_content

    def test_rejects_if_promotes_missing(self, tmp_path: Path) -> None:
        """Test that action rejects if 'promotes' config is missing."""
        context = {}
        state = {"artifacts": {}}
        step_cfg = {}
        
        result = promote_artifact(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "REJECTED"
        assert result.reject_code == "MISSING_PROMOTES_CONFIG"

    def test_rejects_if_artifact_not_found(self, tmp_path: Path) -> None:
        """Test that action rejects if artifact file doesn't exist."""
        context = {}
        state = {"artifacts": {"TEST_FILE": "nonexistent.md"}}
        step_cfg = {"promotes": "TEST_FILE"}
        
        result = promote_artifact(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "REJECTED"
        assert result.reject_code == "ARTIFACT_FILE_NOT_FOUND"


class TestPromoteToRequirement:
    """Tests for promote_to_requirement action."""

    def test_creates_req_from_pre_req(self, tmp_path: Path) -> None:
        """Test that action creates REQ file from PRE-REQ file."""
        # Create test PRE-REQ
        pre_req_dir = tmp_path / "docs" / "repo" / "sdlc" / "delivery" / "pre_requirements"
        pre_req_dir.mkdir(parents=True)
        pre_req_path = pre_req_dir / "PRE-REQ-20260721-001_test-slug.md"
        pre_req_path.write_text("""---
template_id: "TEST"
lifecycle_status: "draft"
---

# Pre-Requirement
""")
        
        context = {"PRE_REQ_FILE": str(pre_req_path)}
        state = {"artifacts": {"PRE_REQ_FILE": str(pre_req_path)}}
        step_cfg = {
            "source": "PRE_REQ_FILE",
            "dest": "REQ_FILE",
            "dest_dir": "docs/repo/sdlc/delivery/requirements",
        }
        
        result = promote_to_requirement(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "APPROVED"
        assert "PRE_REQ_FILE" in result.artifacts
        assert "REQ_FILE" in result.artifacts
        
        # Verify REQ file was created
        req_path = tmp_path / result.artifacts["REQ_FILE"]
        assert req_path.exists()
        
        # Verify REQ has approved status
        req_content = req_path.read_text()
        assert 'lifecycle_status: "approved"' in req_content
        
        # Verify PRE-REQ still exists
        assert pre_req_path.exists()

    def test_extracts_slug_from_filename(self, tmp_path: Path) -> None:
        """Test that action extracts slug from PRE-REQ filename."""
        pre_req_dir = tmp_path / "docs" / "repo" / "sdlc" / "delivery" / "pre_requirements"
        pre_req_dir.mkdir(parents=True)
        pre_req_path = pre_req_dir / "PRE-REQ-20260721-001_add-auth-feature.md"
        pre_req_path.write_text("---\ntemplate_id: TEST\nlifecycle_status: draft\n---\n")
        
        context = {"PRE_REQ_FILE": str(pre_req_path)}
        state = {"artifacts": {"PRE_REQ_FILE": str(pre_req_path)}}
        step_cfg = {"source": "PRE_REQ_FILE", "dest": "REQ_FILE"}
        
        result = promote_to_requirement(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "APPROVED"
        req_path = tmp_path / result.artifacts["REQ_FILE"]
        assert "add-auth-feature" in req_path.name


class TestPromoteAll:
    """Tests for promote_all action."""

    def test_promotes_multiple_artifacts(self, tmp_path: Path) -> None:
        """Test that action promotes multiple artifacts."""
        # Create test artifacts
        rev_path = tmp_path / "REV.md"
        mem_path = tmp_path / "MEM.md"
        close_path = tmp_path / "CLOSE.md"
        
        for path in [rev_path, mem_path, close_path]:
            path.write_text("---\nlifecycle_status: draft\n---\n")
        
        context = {}
        state = {
            "artifacts": {
                "REV_FILE": str(rev_path),
                "MEM_FILE": str(mem_path),
                "CLOSE_FILE": str(close_path),
            }
        }
        step_cfg = {"promotes": ["REV_FILE", "MEM_FILE", "CLOSE_FILE"]}
        
        result = promote_all(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "APPROVED"
        assert len(result.artifacts) == 3
        
        # Verify all files were updated
        for path in [rev_path, mem_path, close_path]:
            content = path.read_text()
            assert 'lifecycle_status: "approved"' in content

    def test_rejects_if_promotes_list_missing(self, tmp_path: Path) -> None:
        """Test that action rejects if 'promotes' list is missing."""
        context = {}
        state = {"artifacts": {}}
        step_cfg = {}
        
        result = promote_all(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "REJECTED"
        assert result.reject_code == "MISSING_PROMOTES_CONFIG"


class TestAggregateExecutions:
    """Tests for aggregate_executions action."""

    def test_aggregates_exec_documents(self, tmp_path: Path) -> None:
        """Test that action aggregates EXEC documents."""
        # Create test EXEC documents
        exec_dir = tmp_path / "docs" / "repo" / "sdlc" / "delivery" / "executions" / "TEST-001"
        exec_dir.mkdir(parents=True)
        
        exec1_path = exec_dir / "EXEC-001.md"
        exec2_path = exec_dir / "EXEC-002.md"
        exec1_path.write_text("# EXEC 1")
        exec2_path.write_text("# EXEC 2")
        
        context = {}
        state = {
            "job_id": "TEST-001",
            "artifacts": {
                "EXEC_001": str(exec1_path),
                "EXEC_002": str(exec2_path),
            }
        }
        step_cfg = {}
        
        result = aggregate_executions(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "APPROVED"
        assert "EXECUTION_AGGREGATION" in result.artifacts
        
        # Verify aggregation file was created
        agg_path = tmp_path / result.artifacts["EXECUTION_AGGREGATION"]
        assert agg_path.exists()
        
        content = agg_path.read_text()
        assert "EXEC_001" in content
        assert "EXEC_002" in content

    def test_rejects_if_no_exec_docs(self, tmp_path: Path) -> None:
        """Test that action rejects if no EXEC documents found."""
        context = {}
        state = {"job_id": "TEST-001", "artifacts": {}}
        step_cfg = {}
        
        result = aggregate_executions(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "REJECTED"
        assert result.reject_code == "NO_EXEC_DOCS_FOUND"


class TestCreateBackup:
    """Tests for create_backup action."""

    def test_creates_backup_of_codebase(self, tmp_path: Path) -> None:
        """Test that action creates backup of current/ codebase docs."""
        # Create test codebase structure with current/ directory
        codebase_dir = tmp_path / "docs" / "repo" / "codebase"
        current_dir = codebase_dir / "current"
        current_dir.mkdir(parents=True)
        (current_dir / "test.md").write_text("# Test")

        context = {}
        state = {}
        step_cfg = {}

        result = create_backup(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )

        assert result.status == "APPROVED"
        assert "CODEBASE_BACKUP" in result.artifacts

        # Verify backup was created from current/
        backup_path = tmp_path / result.artifacts["CODEBASE_BACKUP"]
        assert backup_path.exists()
        assert (backup_path / "test.md").exists()

    def test_creates_empty_backup_when_no_current(self, tmp_path: Path) -> None:
        """Test that action creates empty backup marker when current/ doesn't exist."""
        codebase_dir = tmp_path / "docs" / "repo" / "codebase"
        codebase_dir.mkdir(parents=True)

        result = create_backup(
            context={},
            state={},
            step_cfg={},
            project_root=tmp_path,
        )

        assert result.status == "APPROVED"
        backup_path = tmp_path / result.artifacts["CODEBASE_BACKUP"]
        assert backup_path.exists()
        assert (backup_path / "README.md").exists()

    def test_rejects_if_codebase_not_found(self, tmp_path: Path) -> None:
        """Test that action rejects if codebase root doesn't exist."""
        context = {}
        state = {}
        step_cfg = {}
        
        result = create_backup(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "REJECTED"
        assert result.reject_code == "CODEBASE_ROOT_NOT_FOUND"


class TestGenerateSyncLog:
    """Tests for generate_sync_log action."""

    def test_generates_sync_log(self, tmp_path: Path) -> None:
        """Test that action generates sync log."""
        context = {}
        state = {"job_id": "TEST-001", "current_step": "generate_sync_log"}
        step_cfg = {}
        
        result = generate_sync_log(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "APPROVED"
        assert "SYNC_LOG" in result.artifacts
        
        # Verify sync log was created
        log_path = tmp_path / result.artifacts["SYNC_LOG"]
        assert log_path.exists()
        
        content = log_path.read_text()
        assert "Codebase Sync Log" in content
        assert "TEST-001" in content


class TestCommitChanges:
    """Tests for commit_changes action."""

    def test_skips_if_not_git_repo(self, tmp_path: Path) -> None:
        """Test that action skips if not a git repository."""
        context = {}
        state = {}
        step_cfg = {}
        
        result = commit_changes(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "APPROVED"
        assert "Not a git repository" in result.remark

    @patch("agent_runner_v2.actions.sdlc_shared_actions.subprocess.run")
    def test_commits_changes_in_git_repo(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test that action commits changes in git repository."""
        # Create .git directory
        (tmp_path / ".git").mkdir()
        
        # Create codebase directory
        codebase_dir = tmp_path / "docs" / "repo" / "codebase"
        codebase_dir.mkdir(parents=True)
        
        # Mock subprocess responses
        mock_run.return_value = MagicMock(stdout="M docs/repo/codebase/test.md", stderr="")
        
        context = {}
        state = {}
        step_cfg = {}
        
        result = commit_changes(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "APPROVED"
        assert mock_run.called

    @patch("agent_runner_v2.actions.sdlc_shared_actions.subprocess.run")
    def test_skips_if_no_changes(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test that action skips if no changes to commit."""
        # Create .git directory
        (tmp_path / ".git").mkdir()
        
        # Mock subprocess responses (no changes)
        mock_run.return_value = MagicMock(stdout="", stderr="")
        
        context = {}
        state = {}
        step_cfg = {}
        
        result = commit_changes(
            context=context,
            state=state,
            step_cfg=step_cfg,
            project_root=tmp_path,
        )
        
        assert result.status == "APPROVED"
        assert "No changes to commit" in result.remark
