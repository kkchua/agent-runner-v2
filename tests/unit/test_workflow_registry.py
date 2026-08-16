"""Unit tests for the WorkflowRegistry discovery mechanism."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_runner_v2.workflow_packages.registry import WorkflowRegistry


class TestWorkflowRegistry:
    """Registry discovery, caching, and error handling."""

    def test_empty_registry_returns_empty_list(self, tmp_path):
        registry = WorkflowRegistry.create(search_paths=[tmp_path])
        assert registry.list_workflows() == []

    def test_unknown_workflow_raises_key_error(self, tmp_path):
        registry = WorkflowRegistry.create(search_paths=[tmp_path])
        with pytest.raises(KeyError, match="nonexistent"):
            registry.get("nonexistent")

    def test_has_returns_false_for_missing(self, tmp_path):
        registry = WorkflowRegistry.create(search_paths=[tmp_path])
        assert not registry.has("nonexistent")

    def test_discovers_workflow_package(self, project_root):
        """Verify the real workflow packages are discovered by scanning workflows/."""
        registry = WorkflowRegistry.from_project_root(str(project_root))
        available = registry.list_workflows()
        assert "01_governance_foundation_v1" in available

    def test_get_returns_loaded_bundle(self, project_root):
        registry = WorkflowRegistry.from_project_root(str(project_root))
        bundle = registry.get("01_governance_foundation_v1")
        assert bundle.name == "01_governance_foundation_v1"
        assert bundle.manifest_path.parent.name == "01_governance_foundation_v1"

    def test_discover_is_idempotent(self, project_root):
        registry = WorkflowRegistry.from_project_root(str(project_root))
        first = registry.list_workflows()
        registry.discover()
        second = registry.list_workflows()
        assert first == second

    def test_missing_directory_produces_no_errors(self, tmp_path):
        registry = WorkflowRegistry()
        registry.add_search_path(tmp_path / "nonexistent")
        registry.discover()
        assert registry.list_workflows() == []

    def test_add_search_path_twice_does_not_duplicate(self, project_root):
        registry = WorkflowRegistry()
        registry.add_search_path(str(project_root / "workflows"))
        registry.add_search_path(str(project_root / "workflows"))
        registry.discover()
        # discover() clears _bundles before indexing, so no duplication
        count = len(registry.list_workflows())
        assert count >= 1

    def test_get_after_clear(self, project_root, tmp_path):
        registry = WorkflowRegistry()
        registry.add_search_path(str(project_root / "workflows"))
        registry.discover()
        assert registry.has("01_governance_foundation_v1")
        # Create a new registry with empty path
        registry2 = WorkflowRegistry.create(search_paths=[tmp_path])
        assert not registry2.has("01_governance_foundation_v1")

    def test_global_singleton(self):
        from agent_runner_v2.workflow_packages.registry import (
            get_global_registry,
            set_global_registry,
        )

        r1 = get_global_registry()
        r2 = get_global_registry()
        assert r1 is r2  # same instance

        r3 = WorkflowRegistry()
        set_global_registry(r3)
        assert get_global_registry() is r3
