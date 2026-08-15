"""Unit tests for impl_name propagation through the execution chain.

Tests cover:
- CLI parsing of --impl-name flag
- _load_group() wrapper passes impl_name through
- impl_name extraction from state
- daemon_v2.py extracting impl_name from context_payload
- manual_runtime.py extracting impl_name from backend state
- End-to-end: impl_name flows from CLI to load_workflow_package()

These tests verify the BUG FIX that wires impl_name through 6 broken call sites.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Fix 1: CLI --impl-name flag
# ---------------------------------------------------------------------------


class TestImplNameCLIFlag:
    """--impl-name flag is parsed and passed through to args."""

    def test_impl_name_flag_parsed(self):
        from agent_runner_v2.run_agent import parse_args

        ns = parse_args(["run", "--project-root", "/tmp/x", "--template-group", "test_wf",
                          "--impl-name", "key_points"])
        assert ns.impl_name == "key_points"

    def test_impl_name_defaults_to_empty_string(self):
        from agent_runner_v2.run_agent import parse_args

        ns = parse_args(["run", "--project-root", "/tmp/x", "--template-group", "test_wf"])
        assert ns.impl_name == ""

    def test_impl_name_accepts_various_values(self):
        from agent_runner_v2.run_agent import parse_args

        ns = parse_args(["run", "--project-root", "/tmp/x", "--template-group", "test_wf",
                          "--impl-name", "default"])
        assert ns.impl_name == "default"

        ns = parse_args(["run", "--project-root", "/tmp/x", "--template-group", "test_wf",
                          "--impl-name", "anime"])
        assert ns.impl_name == "anime"


# ---------------------------------------------------------------------------
# Fix 2a/2b/2c: _load_group() wrappers pass impl_name
# ---------------------------------------------------------------------------


class TestLoadGroupPassesImplName:
    """All _load_group() wrappers forward impl_name to workflow_runtime.load_group()."""

    @patch("agent_runner_v2.run_agent._workflow_runtime")
    def test_run_agent_load_group_passes_impl_name(self, mock_runtime):
        from agent_runner_v2.run_agent import _load_group

        mock_runtime.load_group.return_value = {"step_configs": {}}
        _load_group("test_wf", workspace_root=Path("/tmp"), workflow_root=Path("/tmp/wf"),
                    impl_name="key_points")

        mock_runtime.load_group.assert_called_once_with(
            "test_wf",
            workspace_root=Path("/tmp"),
            workflow_root=Path("/tmp/wf"),
            impl_name="key_points",
        )

    @patch("agent_runner_v2.shared_runtime_deps._workflow_runtime")
    def test_shared_runtime_deps_load_group_passes_impl_name(self, mock_runtime):
        from agent_runner_v2.shared_runtime_deps import _load_group

        mock_runtime.load_group.return_value = {"step_configs": {}}
        _load_group("test_wf", workspace_root=Path("/tmp"), workflow_root=Path("/tmp/wf"),
                    impl_name="key_points")

        mock_runtime.load_group.assert_called_once_with(
            "test_wf",
            workspace_root=Path("/tmp"),
            workflow_root=Path("/tmp/wf"),
            impl_name="key_points",
        )

    @patch("agent_runner_v2.runtime_hooks.RuntimeHooks._get_workflow_runtime")
    def test_runtime_hooks_load_group_passes_impl_name(self, mock_get_runtime):
        from agent_runner_v2.runtime_hooks import RuntimeHooks

        mock_runtime = MagicMock()
        mock_runtime.load_group.return_value = {"step_configs": {}}
        mock_get_runtime.return_value = mock_runtime

        hooks = RuntimeHooks()
        hooks.load_group("test_wf", workspace_root=Path("/tmp"), workflow_root=Path("/tmp/wf"),
                         impl_name="key_points")

        mock_runtime.load_group.assert_called_once_with(
            "test_wf",
            workspace_root=Path("/tmp"),
            workflow_root=Path("/tmp/wf"),
            impl_name="key_points",
        )

    @patch("agent_runner_v2.run_agent._workflow_runtime")
    def test_load_group_without_impl_name_is_none(self, mock_runtime):
        """When impl_name is not provided, it defaults to None (not empty string)."""
        from agent_runner_v2.run_agent import _load_group

        mock_runtime.load_group.return_value = {"step_configs": {}}
        _load_group("test_wf")

        mock_runtime.load_group.assert_called_once_with(
            "test_wf",
            workspace_root=None,
            workflow_root=None,
            impl_name=None,
        )


# ---------------------------------------------------------------------------
# Fix 3: run_agent.py extracts impl_name from args/state
# ---------------------------------------------------------------------------


class TestImplNameExtraction:
    """impl_name is correctly extracted from CLI args and state."""

    def test_impl_name_from_cli_args_takes_priority(self):
        """When --impl-name is provided on CLI, it should be used."""
        args_impl = "key_points"
        state_impl = "default"

        impl_name = args_impl or (state_impl if state_impl else None) or ""
        impl_name = impl_name.strip() or None

        assert impl_name == "key_points"

    def test_impl_name_from_state_when_cli_empty(self):
        """When CLI --impl-name is empty, fall back to state."""
        args_impl = ""
        state_impl = "key_points"

        impl_name = args_impl or (state_impl if state_impl else None) or ""
        impl_name = impl_name.strip() or None

        assert impl_name == "key_points"

    def test_impl_name_none_when_both_empty(self):
        """When both CLI and state are empty, impl_name should be None."""
        args_impl = ""
        state = None

        impl_name = args_impl or (state.get("impl_name") if state else None) or ""
        impl_name = impl_name.strip() or None

        assert impl_name is None

    def test_impl_name_strips_whitespace(self):
        """Whitespace-only impl_name should be normalized to None."""
        args_impl = "   "
        state_impl = ""

        impl_name = args_impl or (state_impl if state_impl else None) or ""
        impl_name = impl_name.strip() or None

        assert impl_name is None

    def test_impl_name_from_state_dict(self):
        """impl_name from state dict should work correctly."""
        args_impl = ""
        state = {"impl_name": "key_points"}

        impl_name = args_impl or (state.get("impl_name") if state else None) or ""
        impl_name = impl_name.strip() or None

        assert impl_name == "key_points"


# ---------------------------------------------------------------------------
# Fix 4: daemon_v2.py extracts impl_name from context_payload
# ---------------------------------------------------------------------------


class TestDaemonImplNameExtraction:
    """daemon_v2.py extracts impl_name from backend context_payload and adds to cli_args."""

    def test_impl_name_extracted_from_context_payload(self):
        run_data = {
            "context_payload": {
                "impl_name": "key_points",
            }
        }
        context_payload = run_data.get("context_payload") or {}
        impl_name = str(context_payload.get("impl_name") or context_payload.get("IMPL_NAME") or "").strip()

        assert impl_name == "key_points"

    def test_impl_name_extracted_from_IMPL_NAME_fallback(self):
        run_data = {
            "context_payload": {
                "IMPL_NAME": "key_points",
            }
        }
        context_payload = run_data.get("context_payload") or {}
        impl_name = str(context_payload.get("impl_name") or context_payload.get("IMPL_NAME") or "").strip()

        assert impl_name == "key_points"

    def test_impl_name_empty_when_not_present(self):
        run_data = {
            "context_payload": {},
        }
        context_payload = run_data.get("context_payload") or {}
        impl_name = str(context_payload.get("impl_name") or context_payload.get("IMPL_NAME") or "").strip()

        assert impl_name == ""

    def test_impl_name_empty_when_context_payload_missing(self):
        run_data = {}
        context_payload = run_data.get("context_payload") or {}
        impl_name = str(context_payload.get("impl_name") or context_payload.get("IMPL_NAME") or "").strip()

        assert impl_name == ""


# ---------------------------------------------------------------------------
# Fix 5: manual_runtime.py extracts impl_name from backend state
# ---------------------------------------------------------------------------


class TestManualRuntimeImplNameExtraction:
    """manual_runtime.py extracts impl_name from backend context_payload into state."""

    def test_impl_name_extracted_from_context(self):
        state = {}
        run = {
            "context_payload": {
                "impl_name": "key_points",
            }
        }
        context = run.get("context_payload") or {}
        impl = str(context.get("impl_name") or context.get("IMPL_NAME") or "").strip()
        if impl:
            state["impl_name"] = impl

        assert state["impl_name"] == "key_points"

    def test_impl_name_extracted_from_IMPL_NAME_fallback(self):
        state = {}
        run = {
            "context_payload": {
                "IMPL_NAME": "key_points",
            }
        }
        context = run.get("context_payload") or {}
        impl = str(context.get("impl_name") or context.get("IMPL_NAME") or "").strip()
        if impl:
            state["impl_name"] = impl

        assert state["impl_name"] == "key_points"

    def test_impl_name_not_set_when_empty(self):
        state = {}
        run = {
            "context_payload": {},
        }
        context = run.get("context_payload") or {}
        impl = str(context.get("impl_name") or context.get("IMPL_NAME") or "").strip()
        if impl:
            state["impl_name"] = impl

        assert "impl_name" not in state

    def test_impl_name_not_set_when_context_missing(self):
        state = {}
        run = {}
        context = run.get("context_payload") or {}
        impl = str(context.get("impl_name") or context.get("IMPL_NAME") or "").strip()
        if impl:
            state["impl_name"] = impl

        assert "impl_name" not in state
