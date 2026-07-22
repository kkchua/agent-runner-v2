"""Unit tests for codebase_init_commands module."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from agent_runner_v2.codebase_init_commands import (
    _generate_codebase_inventory,
    _generate_codebase_doc_sop,
    _generate_codebase_status_rules,
    _write_text,
    main,
)


class TestCodebaseInitCommands:
    """Tests for codebase-init CLI command."""

    def test_generate_codebase_inventory_returns_string(self, tmp_path: Path) -> None:
        """Test that inventory generation returns a string."""
        # Create a simple project structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("# main")
        (tmp_path / "README.md").write_text("# README")
        
        result = _generate_codebase_inventory(tmp_path)
        
        assert isinstance(result, str)
        assert "Codebase Inventory" in result
        assert "Repository Overview" in result
        assert "File Statistics" in result

    def test_generate_codebase_inventory_includes_frontmatter(self, tmp_path: Path) -> None:
        """Test that inventory includes YAML frontmatter."""
        (tmp_path / "test.py").write_text("# test")
        
        result = _generate_codebase_inventory(tmp_path)
        
        assert result.startswith("---")
        assert "template_id:" in result
        assert "version:" in result
        assert "doc_type:" in result
        assert "lifecycle_status:" in result

    def test_generate_codebase_doc_sop_returns_string(self, tmp_path: Path) -> None:
        """Test that SOP generation returns a string."""
        result = _generate_codebase_doc_sop(tmp_path)
        
        assert isinstance(result, str)
        assert "Codebase Documentation Standard" in result
        assert "Documentation Structure" in result
        assert "Documentation Rules" in result

    def test_generate_codebase_status_rules_returns_string(self, tmp_path: Path) -> None:
        """Test that status rules generation returns a string."""
        result = _generate_codebase_status_rules(tmp_path)
        
        assert isinstance(result, str)
        assert "Codebase Documentation Status Rules" in result
        assert "Status Values" in result
        assert "Status Transitions" in result

    def test_write_text_creates_file(self, tmp_path: Path) -> None:
        """Test that _write_text creates a file with content."""
        test_file = tmp_path / "subdir" / "test.txt"
        content = "Test content"
        
        _write_text(test_file, content)
        
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == content

    def test_write_text_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test that _write_text creates parent directories."""
        test_file = tmp_path / "a" / "b" / "c" / "test.txt"
        
        _write_text(test_file, "content")
        
        assert test_file.exists()
        assert test_file.parent.is_dir()

    def test_main_creates_directory_structure(self, tmp_path: Path) -> None:
        """Test that main creates the expected directory structure."""
        result = main(["--project-root", str(tmp_path)])
        
        assert result == 0
        
        # Check directories were created
        assert (tmp_path / "docs" / "repo" / "codebase" / "00_standards").is_dir()
        assert (tmp_path / "docs" / "repo" / "codebase" / "01_inventory").is_dir()
        assert (tmp_path / "docs" / "repo" / "codebase" / "02_modules").is_dir()
        assert (tmp_path / "docs" / "repo" / "codebase" / "03_components").is_dir()
        assert (tmp_path / "docs" / "repo" / "codebase" / "04_changes").is_dir()

    def test_main_generates_files(self, tmp_path: Path) -> None:
        """Test that main generates the expected files."""
        result = main(["--project-root", str(tmp_path)])
        
        assert result == 0
        
        # Check files were created
        assert (tmp_path / "docs" / "repo" / "codebase" / "01_inventory" / "codebase_inventory.md").is_file()
        assert (tmp_path / "docs" / "repo" / "codebase" / "00_standards" / "CODEBASE_DOC_SOP.md").is_file()
        assert (tmp_path / "docs" / "repo" / "codebase" / "00_standards" / "CODEBASE_DOC_STATUS_RULES.md").is_file()

    def test_main_fails_if_codebase_exists_without_force(self, tmp_path: Path) -> None:
        """Test that main fails if codebase docs exist without --force."""
        # Create initial codebase
        main(["--project-root", str(tmp_path)])
        
        # Try to run again without --force
        result = main(["--project-root", str(tmp_path)])
        
        assert result == 1

    def test_main_succeeds_with_force(self, tmp_path: Path) -> None:
        """Test that main succeeds with --force even if codebase exists."""
        # Create initial codebase
        main(["--project-root", str(tmp_path)])
        
        # Run again with --force
        result = main(["--project-root", str(tmp_path), "--force"])
        
        assert result == 0

    def test_main_fails_for_nonexistent_project_root(self, tmp_path: Path) -> None:
        """Test that main fails for non-existent project root."""
        nonexistent = tmp_path / "does_not_exist"
        
        result = main(["--project-root", str(nonexistent)])
        
        assert result == 1

    def test_main_uses_cwd_by_default(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that main uses current directory by default."""
        monkeypatch.chdir(tmp_path)
        
        result = main([])
        
        assert result == 0
        assert (tmp_path / "docs" / "repo" / "codebase").is_dir()

    def test_generated_inventory_has_correct_metadata(self, tmp_path: Path) -> None:
        """Test that generated inventory has correct metadata."""
        main(["--project-root", str(tmp_path)])
        
        inventory_path = tmp_path / "docs" / "repo" / "codebase" / "01_inventory" / "codebase_inventory.md"
        content = inventory_path.read_text(encoding="utf-8")
        
        assert 'template_id: "SYS-00-CI"' in content
        assert 'doc_type: "system"' in content
        assert 'lifecycle_status: "approved"' in content
        assert 'managed_by: "cli-command"' in content

    def test_generated_sop_has_correct_metadata(self, tmp_path: Path) -> None:
        """Test that generated SOP has correct metadata."""
        main(["--project-root", str(tmp_path)])
        
        sop_path = tmp_path / "docs" / "repo" / "codebase" / "00_standards" / "CODEBASE_DOC_SOP.md"
        content = sop_path.read_text(encoding="utf-8")
        
        assert 'template_id: "SYS-00-CDS"' in content
        assert 'doc_type: "system"' in content
        assert 'lifecycle_status: "approved"' in content

    def test_generated_status_rules_has_correct_metadata(self, tmp_path: Path) -> None:
        """Test that generated status rules has correct metadata."""
        main(["--project-root", str(tmp_path)])
        
        rules_path = tmp_path / "docs" / "repo" / "codebase" / "00_standards" / "CODEBASE_DOC_STATUS_RULES.md"
        content = rules_path.read_text(encoding="utf-8")
        
        assert 'template_id: "SYS-00-CSR"' in content
        assert 'doc_type: "system"' in content
        assert 'lifecycle_status: "approved"' in content
