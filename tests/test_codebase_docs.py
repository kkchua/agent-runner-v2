from __future__ import annotations

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


def test_render_inventory_uses_workflow_name_in_frontmatter(tmp_path):
    (tmp_path / "agent_runner_v2").mkdir()
    (tmp_path / "agent_runner_v2" / "__init__.py").write_text("", encoding="utf-8")

    snapshot = codebase_docs.build_snapshot(
        tmp_path,
        mode="bootstrap",
        job_id="00DOC-GEN-TEST",
        step="00_scan_repo_codebase",
        workflow_name="00_master_docs_bootstrap_v1",
    )

    rendered = codebase_docs.render_inventory(snapshot, title="Repo")
    assert 'workflow: "00_master_docs_bootstrap_v1"' in rendered.splitlines()[:8]
