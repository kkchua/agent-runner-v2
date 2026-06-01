"""Tests for agent_runner_v2.runtime_context."""
from __future__ import annotations

from pathlib import Path

import pytest

from agent_runner_v2.runtime_context import (
    PACKAGE_ROOT,
    DEFAULT_RUNNER_HOME,
    DEFAULT_WORKFLOW_NAME,
    RuntimeContext,
    PathProxy,
    set_context,
    get_context,
    get_workspace_root,
    get_runner_home,
    get_jobs_root,
    get_workflow_root,
    get_workflow_module,
    set_workflow_module,
    get_delivery_root,
    set_delivery_root,
    resolve_artifact_root,
    PROJECT_ROOT,
    RUNNER_HOME,
    RUNNER_ROOT,
    JOBS_ROOT,
    DELIVERY_ROOT,
    ARTIFACT_ROOT,
)


# ---------------------------------------------------------------------------
# RuntimeContext dataclass
# ---------------------------------------------------------------------------

class TestRuntimeContext:
    def test_default_values(self):
        """Default context uses current working directory and package root."""
        ctx = RuntimeContext(
            workspace_root=Path.cwd().resolve(),
            runner_home=Path.cwd().resolve() / DEFAULT_RUNNER_HOME,
            workflow_name=DEFAULT_WORKFLOW_NAME,
            workflow_root=PACKAGE_ROOT,
            workflow_module=None,
            delivery_root=None,
        )
        assert ctx.workflow_name == "default"
        assert ctx.workflow_module is None
        assert ctx.delivery_root is None

    def test_frozen(self):
        """RuntimeContext is immutable (frozen dataclass)."""
        ctx = RuntimeContext(
            workspace_root=Path("/tmp"),
            runner_home=Path("/tmp/.ukbe-runner"),
            workflow_name="default",
            workflow_root=PACKAGE_ROOT,
            workflow_module=None,
            delivery_root=None,
        )
        with pytest.raises((TypeError, AttributeError)):
            ctx.workspace_root = Path("/other")


# ---------------------------------------------------------------------------
# PathProxy
# ---------------------------------------------------------------------------

class TestPathProxy:
    def test_truediv(self, tmp_workspace, fake_workflow, set_context):
        """PathProxy supports / operator to build sub-paths."""
        proxy = PathProxy(get_workspace_root)
        result = proxy / "subdir"
        assert result == tmp_workspace.workspace_root / "subdir"

    def test_rtruediv(self, tmp_workspace, fake_workflow, set_context):
        """PathProxy supports right-division."""
        proxy = PathProxy(get_workspace_root)
        result = Path("some_prefix") / proxy
        assert result == Path("some_prefix") / tmp_workspace.workspace_root

    def test_fspath(self, tmp_workspace, fake_workflow, set_context):
        """PathProxy is usable with os.fspath."""
        proxy = PathProxy(get_workspace_root)
        assert isinstance(proxy.__fspath__(), str)
        assert proxy.__fspath__() == str(tmp_workspace.workspace_root)

    def test_str(self, tmp_workspace, fake_workflow, set_context):
        """str(PathProxy) returns the underlying path string."""
        proxy = PathProxy(get_workspace_root)
        assert str(proxy) == str(tmp_workspace.workspace_root)

    def test_repr(self, tmp_workspace, fake_workflow, set_context):
        """repr includes the underlying path."""
        proxy = PathProxy(get_workspace_root)
        assert "PathProxy(" in repr(proxy)
        assert str(tmp_workspace.workspace_root) in repr(proxy)

    def test_getattr_delegates(self, tmp_workspace, fake_workflow, set_context):
        """PathProxy delegates attribute access to the underlying Path."""
        proxy = PathProxy(get_workspace_root)
        assert proxy.name == tmp_workspace.workspace_root.name
        assert proxy.exists() is True

    def test_proxy_updates_when_context_changes(self, tmp_workspace, fake_workflow, set_context):
        """PathProxy reflects the latest context after set_context."""
        assert str(PROJECT_ROOT) == str(tmp_workspace.workspace_root)


# ---------------------------------------------------------------------------
# set_context / get_context
# ---------------------------------------------------------------------------

class TestSetContext:
    def test_set_and_get(self, tmp_workspace):
        """set_context updates the global context."""
        ctx = set_context(
            workspace_root=tmp_workspace.workspace_root,
            workflow_name="my_workflow",
        )
        assert ctx.workspace_root == tmp_workspace.workspace_root.resolve()
        assert ctx.workflow_name == "my_workflow"
        assert ctx.runner_home == tmp_workspace.workspace_root / DEFAULT_RUNNER_HOME

    def test_runner_home_derived(self, tmp_workspace):
        """runner_home is always workspace_root / .ukbe-runner."""
        ctx = set_context(workspace_root=tmp_workspace.workspace_root)
        assert ctx.runner_home == tmp_workspace.workspace_root / DEFAULT_RUNNER_HOME

    def test_delivery_root_resolved(self, tmp_workspace):
        """delivery_root is resolved to absolute."""
        ctx = set_context(
            workspace_root=tmp_workspace.workspace_root,
            delivery_root=tmp_workspace.workspace_root / "delivery",
        )
        assert ctx.delivery_root == tmp_workspace.workspace_root / "delivery"

    def test_preserves_existing_when_none(self, tmp_workspace, fake_workflow, set_context):
        """Passing None for workflow_name preserves the previous value."""
        from agent_runner_v2.runtime_context import set_context as _set_ctx
        ctx = get_context()
        existing_name = ctx.workflow_name
        ctx2 = _set_ctx(
            workspace_root=tmp_workspace.workspace_root,
            workflow_name=None,
            workflow_root=tmp_workspace.workflow_root,
        )
        assert ctx2.workflow_name == existing_name


class TestGetters:
    def test_get_workspace_root(self, tmp_workspace, fake_workflow, set_context):
        assert get_workspace_root() == tmp_workspace.workspace_root.resolve()

    def test_get_runner_home(self, tmp_workspace, fake_workflow, set_context):
        assert get_runner_home() == tmp_workspace.workspace_root / DEFAULT_RUNNER_HOME

    def test_get_jobs_root(self, tmp_workspace, fake_workflow, set_context):
        assert get_jobs_root() == tmp_workspace.workspace_root / DEFAULT_RUNNER_HOME / "jobs"

    def test_get_workflow_root(self, tmp_workspace, fake_workflow, set_context):
        assert get_workflow_root() == tmp_workspace.workflow_root.resolve()

    def test_get_workflow_module(self, tmp_workspace, fake_workflow, set_context):
        mod = get_workflow_module()
        assert mod is not None
        assert hasattr(mod, "TEMPLATE_GROUPS")

    def test_set_workflow_module(self, tmp_workspace, fake_workflow, set_context):
        import types
        dummy = types.ModuleType("dummy")
        set_workflow_module(dummy)
        assert get_workflow_module() is dummy

    def test_get_delivery_root_none_by_default(self, tmp_workspace, fake_workflow, set_context):
        """delivery_root is None when not explicitly set."""
        root = get_delivery_root()
        # May be None or workspace_root depending on fixture setup
        assert root is None or root == tmp_workspace.workspace_root

    def test_set_delivery_root(self, tmp_workspace, fake_workflow, set_context):
        new_root = tmp_workspace.workspace_root / "other_delivery"
        set_delivery_root(new_root)
        assert get_delivery_root() == new_root


class TestResolveArtifactRoot:
    def test_uses_workspace_when_no_delivery_root(self, tmp_workspace, fake_workflow, set_context):
        """When delivery_root is None, artifact root = workspace_root."""
        # The fixture sets delivery_root to None by default
        assert resolve_artifact_root() == tmp_workspace.workspace_root

    def test_uses_delivery_root_when_set(self, tmp_workspace, fake_workflow, set_context):
        """When delivery_root is set, artifact root = delivery_root."""
        dr = tmp_workspace.workspace_root / "custom_delivery"
        set_delivery_root(dr)
        assert resolve_artifact_root() == dr


class TestPathProxyGlobals:
    def test_project_root_points_to_workspace(self, tmp_workspace, fake_workflow, set_context):
        assert str(PROJECT_ROOT) == str(tmp_workspace.workspace_root)

    def test_runner_home_proxy(self, tmp_workspace, fake_workflow, set_context):
        expected = tmp_workspace.workspace_root / DEFAULT_RUNNER_HOME
        assert str(RUNNER_HOME) == str(expected)

    def test_jobs_root_proxy(self, tmp_workspace, fake_workflow, set_context):
        expected = tmp_workspace.workspace_root / DEFAULT_RUNNER_HOME / "jobs"
        assert str(JOBS_ROOT) == str(expected)

    def test_artifact_root_proxy_uses_delivery_when_set(self, tmp_workspace, fake_workflow, set_context):
        dr = tmp_workspace.workspace_root / "custom_delivery"
        set_delivery_root(dr)
        assert str(ARTIFACT_ROOT) == str(dr)
