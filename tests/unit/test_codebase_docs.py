from __future__ import annotations

import shutil
import subprocess

from agent_runner_v2 import codebase_docs


def test_build_snapshot_excludes_tmp_and_pytest_artifacts(tmp_path, monkeypatch):
    (tmp_path / "agent_runner_v2").mkdir()
    (tmp_path / "agent_runner_v2" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Repo\n", encoding="utf-8")
    (tmp_path / ".tmp" / "pytest-basetemp-123").mkdir(parents=True)
    (tmp_path / ".tmp" / "pytest-basetemp-123" / "generated.md").write_text("temp", encoding="utf-8")
    (tmp_path / ".pytest_cache").mkdir()
    (tmp_path / ".pytest_cache" / "state.json").write_text("{}", encoding="utf-8")

    class _Bundle:
        TEMPLATE_GROUPS = {
            "00_master_docs_bootstrap_v1": {
                "visibility": "canonical",
                "job_prefix": "00DOC",
                "job_init_step": "00_scan_repo_codebase",
                "job_init_inputs": [],
                "steps": [],
                "step_configs": {},
            }
        }

    monkeypatch.setattr(codebase_docs, "get_workflow_module", lambda: _Bundle)

    snapshot = codebase_docs.build_snapshot(
        tmp_path,
        mode="bootstrap",
        job_id="00DOC-GEN-TEST",
        step="00_scan_repo_codebase",
    )

    rel_paths = {item.rel_path for item in snapshot["items"]}
    assert "README.md" in rel_paths
    assert all(not path.startswith(".tmp/") for path in rel_paths)
    assert all(".pytest_cache" not in path for path in rel_paths)


def test_build_snapshot_respects_gitignore(tmp_path, monkeypatch):
    if shutil.which("git") is None:
        return

    (tmp_path / "agent_runner_v2").mkdir()
    (tmp_path / "agent_runner_v2" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Repo\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("ignored.txt\nignored_dir/\n", encoding="utf-8")
    (tmp_path / "ignored.txt").write_text("hidden\n", encoding="utf-8")
    (tmp_path / "ignored_dir").mkdir()
    (tmp_path / "ignored_dir" / "secret.py").write_text("print('x')\n", encoding="utf-8")
    (tmp_path / "visible.py").write_text("print('ok')\n", encoding="utf-8")

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

    class _Bundle:
        TEMPLATE_GROUPS = {
            "00_master_docs_bootstrap_v1": {
                "visibility": "canonical",
                "job_prefix": "00DOC",
                "job_init_step": "00_scan_repo_codebase",
                "job_init_inputs": [],
                "steps": [],
                "step_configs": {},
            }
        }

    monkeypatch.setattr(codebase_docs, "get_workflow_module", lambda: _Bundle)

    snapshot = codebase_docs.build_snapshot(
        tmp_path,
        mode="bootstrap",
        job_id="00DOC-GEN-TEST",
        step="00_scan_repo_codebase",
    )

    rel_paths = {item.rel_path for item in snapshot["items"]}
    assert "visible.py" in rel_paths
    assert "ignored.txt" not in rel_paths
    assert all(not path.startswith("ignored_dir/") for path in rel_paths)


def test_render_inventory_uses_workflow_name_in_frontmatter(tmp_path, monkeypatch):
    (tmp_path / "agent_runner_v2").mkdir()
    (tmp_path / "agent_runner_v2" / "__init__.py").write_text("", encoding="utf-8")

    class _Bundle:
        TEMPLATE_GROUPS = {
            "00_master_docs_bootstrap_v1": {
                "visibility": "canonical",
                "job_prefix": "00DOC",
                "job_init_step": "00_scan_repo_codebase",
                "job_init_inputs": [],
                "steps": [],
                "step_configs": {},
            }
        }

    monkeypatch.setattr(codebase_docs, "get_workflow_module", lambda: _Bundle)

    snapshot = codebase_docs.build_snapshot(
        tmp_path,
        mode="bootstrap",
        job_id="00DOC-GEN-TEST",
        step="00_scan_repo_codebase",
        workflow_name="00_master_docs_bootstrap_v1",
    )

    rendered = codebase_docs.render_inventory(snapshot, title="Repo")
    assert 'workflow: "00_master_docs_bootstrap_v1"' in rendered.splitlines()[:12]


def test_extract_raises_parses_docstring():
    """Test that _extract_raises correctly parses Raises sections from docstrings."""
    docstring = """Invoke coder and validate artifacts.

    Raises:
        CoderInvocationError — coder process failed
        MetaJsonMissingError: coder did not write meta.json
        ArtifactMissingError — meta.json references paths that don't exist
    """
    raises = codebase_docs._extract_raises(docstring)
    assert len(raises) == 3
    assert raises[0]["exception"] == "CoderInvocationError"
    assert "coder process failed" in raises[0]["description"]
    assert raises[1]["exception"] == "MetaJsonMissingError"
    assert raises[2]["exception"] == "ArtifactMissingError"


def test_extract_raises_handles_empty_docstring():
    """Test that _extract_raises handles empty or missing Raises sections."""
    assert codebase_docs._extract_raises("") == []
    assert codebase_docs._extract_raises("No raises here.") == []
    assert codebase_docs._extract_raises(None) == []


def test_extract_parameters_with_type_hints():
    """Test that _extract_parameters extracts type hints correctly."""
    import ast

    source = '''
def example(name: str, count: int = 5, *args: str, key: bool = True, **kwargs: Any) -> None:
    pass
'''
    tree = ast.parse(source)
    func = tree.body[0]
    params = codebase_docs._extract_parameters(func)

    assert len(params) == 5
    assert params[0]["name"] == "name"
    assert params[0]["type"] == "str"
    assert params[1]["name"] == "count"
    assert params[1]["type"] == "int"
    assert params[1]["default"] == "5"
    assert params[2]["name"] == "*args"
    assert params[2]["kind"] == "varargs"
    assert params[3]["name"] == "key"
    assert params[3]["kind"] == "keyword-only"
    assert params[4]["name"] == "**kwargs"
    assert params[4]["kind"] == "kwargs"


def test_build_signature_includes_types():
    """Test that _build_signature includes type hints in signature."""
    import ast

    source = '''
def example(name: str, count: int = 5) -> bool:
    pass
'''
    tree = ast.parse(source)
    func = tree.body[0]
    sig = codebase_docs._build_signature(func)

    assert "name: str" in sig
    assert "count: int = 5" in sig


def test_extract_return_type():
    """Test that _extract_return_type extracts return type annotation."""
    import ast

    source = '''
def example() -> dict[str, Any]:
    pass
'''
    tree = ast.parse(source)
    func = tree.body[0]
    ret = codebase_docs._extract_return_type(func)

    assert ret == "dict[str, Any]"


def test_enhanced_module_doc_contains_signature():
    """Test that render_module_doc includes enhanced function signatures."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        module_dir = tmp_path / "agent_runner_v2"
        module_dir.mkdir()

        # Create a test module with typed functions
        (module_dir / "__init__.py").write_text("", encoding="utf-8")
        (module_dir / "test_module.py").write_text('''
"""Test module for documentation."""

def example_func(name: str, count: int = 5) -> bool:
    """Example function with type hints.

    Raises:
        ValueError — if name is empty
    """
    return True
''', encoding="utf-8")

        # Scan the module
        result = codebase_docs._scan_python_module(tmp_path, module_dir / "test_module.py")

        # Check enhanced data
        func = result["public_functions"][0]
        assert func["name"] == "example_func"
        assert "name: str" in func["signature"]
        assert "count: int = 5" in func["signature"]
        assert func["return_type"] == "bool"
        assert len(func["raises"]) == 1
        assert func["raises"][0]["exception"] == "ValueError"

        # Render and check output
        snapshot = {
            "generated_at": "2026-07-04T12:00:00",
            "workflow_name": "test",
            "job_id": "TEST-001",
            "mode": "test",
        }
        output = codebase_docs.render_module_doc(snapshot, result)

        assert "example_func()" in output
        assert "name: str" in output
        assert "**Returns**: `bool`" in output
        assert "**Raises**:" in output
        assert "ValueError" in output


def test_build_snapshot_respects_codebase_scan_ignore(tmp_path, monkeypatch):
    """Test that .codebase-scan-ignore file excludes matching paths."""
    (tmp_path / "agent_runner_v2").mkdir()
    (tmp_path / "agent_runner_v2" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Repo\n", encoding="utf-8")
    (tmp_path / "secrets").mkdir()
    (tmp_path / "secrets" / "keys.json").write_text("{}", encoding="utf-8")
    (tmp_path / "generated").mkdir()
    (tmp_path / "generated" / "output.txt").write_text("data", encoding="utf-8")
    (tmp_path / "notes.tmp").write_text("temp", encoding="utf-8")

    # Create .codebase-scan-ignore file
    (tmp_path / ".codebase-scan-ignore").write_text(
        "# Exclude sensitive and generated files\n"
        "secrets/\n"
        "generated/\n"
        "*.tmp\n",
        encoding="utf-8",
    )

    class _Bundle:
        TEMPLATE_GROUPS = {
            "00_master_docs_bootstrap_v1": {
                "visibility": "canonical",
                "job_prefix": "00DOC",
                "job_init_step": "00_scan_repo_codebase",
                "job_init_inputs": [],
                "steps": [],
                "step_configs": {},
            }
        }

    monkeypatch.setattr(codebase_docs, "get_workflow_module", lambda: _Bundle)

    snapshot = codebase_docs.build_snapshot(
        tmp_path,
        mode="bootstrap",
        job_id="00DOC-GEN-TEST",
        step="00_scan_repo_codebase",
    )

    rel_paths = {item.rel_path for item in snapshot["items"]}
    # Should include README.md
    assert "README.md" in rel_paths
    # Should exclude secrets/, generated/, and *.tmp
    assert all(not path.startswith("secrets/") for path in rel_paths)
    assert all(not path.startswith("generated/") for path in rel_paths)
    assert all(not path.endswith(".tmp") for path in rel_paths)


def test_load_scan_exclusions_returns_empty_when_no_file(tmp_path):
    """Test that _load_scan_exclusions returns empty list when file doesn't exist."""
    patterns = codebase_docs._load_scan_exclusions(tmp_path)
    assert patterns == []


def test_load_scan_exclusions_parses_file(tmp_path):
    """Test that _load_scan_exclusions correctly parses the ignore file."""
    (tmp_path / ".codebase-scan-ignore").write_text(
        "# Comment line\n"
        "\n"
        "secrets/\n"
        "*.log\n"
        "  # Indented comment\n"
        "build/\n",
        encoding="utf-8",
    )
    patterns = codebase_docs._load_scan_exclusions(tmp_path)
    assert patterns == ["secrets/", "*.log", "build/"]


def test_matches_exclusion_patterns():
    """Test the _matches_exclusion function with various patterns."""
    # Simple filename match
    assert codebase_docs._matches_exclusion("test.log", ["*.log"])
    assert not codebase_docs._matches_exclusion("test.txt", ["*.log"])

    # Directory pattern
    assert codebase_docs._matches_exclusion("secrets/keys.json", ["secrets/"])
    assert codebase_docs._matches_exclusion("deep/secrets/keys.json", ["secrets/"])

    # Path pattern with slash
    assert codebase_docs._matches_exclusion("docs/generated/output.md", ["docs/generated/"])
    assert not codebase_docs._matches_exclusion("other/generated/output.md", ["docs/generated/"])

    # Double-star pattern (matches at any depth)
    assert codebase_docs._matches_exclusion("a/b/c/file.log", ["**/*.log"])
    assert codebase_docs._matches_exclusion("a/file.log", ["**/*.log"])

    # Empty patterns
    assert not codebase_docs._matches_exclusion("any/path", [])
