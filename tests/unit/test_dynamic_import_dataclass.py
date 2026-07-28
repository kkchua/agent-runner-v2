"""Regression test: dynamic importlib loading of modules containing @dataclass.

Verifies that ``_load_package_actions`` can load an ``actions.py`` that defines
``@dataclass`` classes without crashing.  The root cause was that the module
was not registered in ``sys.modules`` before ``exec_module``, so the
``@dataclass`` decorator's internal ``sys.modules.get(cls.__module__)`` call
returned ``None`` and raised ``AttributeError: 'NoneType' object has no
attribute '__dict__'``.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from agent_runner_v2.workflow_packages.loader import (
    _ACTION_CACHE,
    _load_package_actions,
)


@pytest.fixture(autouse=True)
def _clear_action_cache():
    """Ensure each test starts with a clean action cache."""
    _ACTION_CACHE.clear()
    yield
    _ACTION_CACHE.clear()


class TestDynamicImportDataclass:
    """@dataclass inside dynamically loaded actions.py must not crash."""

    def test_load_actions_with_dataclass(self, tmp_path: Path):
        bundle = tmp_path / "test_workflow_v1"
        bundle.mkdir()
        actions_file = bundle / "actions.py"
        actions_file.write_text(
            textwrap.dedent("""\
                from dataclasses import dataclass
                from pathlib import Path

                @dataclass
                class _WorkItem:
                    name: str
                    path: Path
                    count: int
            """),
            encoding="utf-8",
        )

        result = _load_package_actions(bundle)
        assert isinstance(result, dict)

    def test_load_actions_with_dataclass_kw_only(self, tmp_path: Path):
        """@dataclass with kw_only=True also requires sys.modules entry."""
        bundle = tmp_path / "test_kw_only_v1"
        bundle.mkdir()
        actions_file = bundle / "actions.py"
        actions_file.write_text(
            textwrap.dedent("""\
                from dataclasses import dataclass, field

                @dataclass(kw_only=True)
                class _Config:
                    name: str = field(default="default")
                    value: int = field(default=0)
            """),
            encoding="utf-8",
        )

        result = _load_package_actions(bundle)
        assert isinstance(result, dict)

    def test_load_actions_no_actions_file(self, tmp_path: Path):
        bundle = tmp_path / "no_actions_v1"
        bundle.mkdir()

        result = _load_package_actions(bundle)
        assert result == {}
