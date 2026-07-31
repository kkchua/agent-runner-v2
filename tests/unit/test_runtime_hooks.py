"""Unit tests for runtime_hooks module.

Tests get_workflow_guardrails() discovery, caching, and error handling.
Tests RuntimeHooks and ManualHooks lazy loading delegation.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent_runner_v2.runtime_hooks import (
    ManualHooks,
    RuntimeHooks,
    get_workflow_guardrails,
    _GUARDRAIL_CACHE,
)


# ---------------------------------------------------------------------------
# get_workflow_guardrails
# ---------------------------------------------------------------------------

class TestGetWorkflowGuardrails:
    """Test guardrail discovery function."""

    def setup_method(self):
        """Clear guardrail cache before each test."""
        _GUARDRAIL_CACHE.clear()

    def test_returns_none_for_unknown_workflow(self):
        """Unknown workflow name returns None."""
        with patch("agent_runner_v2.workflow_packages.registry.get_global_registry") as mock_reg:
            mock_registry = MagicMock()
            mock_registry.get.return_value = None
            mock_reg.return_value = mock_registry

            result = get_workflow_guardrails("nonexistent_workflow")

        assert result is None

    def test_returns_none_when_no_guardrails_file(self, tmp_path):
        """Workflow without guardrails.py returns None."""
        mock_bundle = MagicMock()
        mock_bundle.bundle_root = tmp_path  # No guardrails.py here

        with patch("agent_runner_v2.workflow_packages.registry.get_global_registry") as mock_reg:
            mock_registry = MagicMock()
            mock_registry.get.return_value = mock_bundle
            mock_reg.return_value = mock_registry

            result = get_workflow_guardrails("my_workflow")

        assert result is None

    def test_returns_none_when_guardrails_has_no_functions(self, tmp_path):
        """guardrails.py without pre_check/post_check returns None."""
        guardrails_file = tmp_path / "guardrails.py"
        guardrails_file.write_text("# empty guardrails\nx = 1\n", encoding="utf-8")

        mock_bundle = MagicMock()
        mock_bundle.bundle_root = tmp_path

        with patch("agent_runner_v2.workflow_packages.registry.get_global_registry") as mock_reg:
            mock_registry = MagicMock()
            mock_registry.get.return_value = mock_bundle
            mock_reg.return_value = mock_registry

            result = get_workflow_guardrails("my_workflow")

        assert result is None

    def test_returns_module_when_pre_check_exists(self, tmp_path):
        """guardrails.py with pre_check() returns the module."""
        guardrails_file = tmp_path / "guardrails.py"
        guardrails_file.write_text(
            "def pre_check(step_name, context):\n    return True\n",
            encoding="utf-8",
        )

        mock_bundle = MagicMock()
        mock_bundle.bundle_root = tmp_path

        with patch("agent_runner_v2.workflow_packages.registry.get_global_registry") as mock_reg:
            mock_registry = MagicMock()
            mock_registry.get.return_value = mock_bundle
            mock_reg.return_value = mock_registry

            result = get_workflow_guardrails("wf_with_pre")

        assert result is not None
        assert callable(getattr(result, "pre_check", None))

    def test_returns_module_when_post_check_exists(self, tmp_path):
        """guardrails.py with post_check() returns the module."""
        guardrails_file = tmp_path / "guardrails.py"
        guardrails_file.write_text(
            "def post_check(step_name, context, output):\n    return True\n",
            encoding="utf-8",
        )

        mock_bundle = MagicMock()
        mock_bundle.bundle_root = tmp_path

        with patch("agent_runner_v2.workflow_packages.registry.get_global_registry") as mock_reg:
            mock_registry = MagicMock()
            mock_registry.get.return_value = mock_bundle
            mock_reg.return_value = mock_registry

            result = get_workflow_guardrails("wf_with_post")

        assert result is not None
        assert callable(getattr(result, "post_check", None))

    def test_caches_none_result(self):
        """None result is cached — second call skips registry lookup."""
        with patch("agent_runner_v2.workflow_packages.registry.get_global_registry") as mock_reg:
            mock_registry = MagicMock()
            mock_registry.get.return_value = None
            mock_reg.return_value = mock_registry

            get_workflow_guardrails("cached_none")
            get_workflow_guardrails("cached_none")

        # Registry should only be called once (second call hits cache)
        assert mock_registry.get.call_count == 1

    def test_caches_module_result(self, tmp_path):
        """Module result is cached — second call skips filesystem."""
        guardrails_file = tmp_path / "guardrails.py"
        guardrails_file.write_text(
            "def pre_check(step_name, context):\n    return True\n",
            encoding="utf-8",
        )

        mock_bundle = MagicMock()
        mock_bundle.bundle_root = tmp_path

        with patch("agent_runner_v2.workflow_packages.registry.get_global_registry") as mock_reg:
            mock_registry = MagicMock()
            mock_registry.get.return_value = mock_bundle
            mock_reg.return_value = mock_registry

            r1 = get_workflow_guardrails("cached_mod")
            r2 = get_workflow_guardrails("cached_mod")

        assert r1 is r2
        assert mock_registry.get.call_count == 1

    def test_handles_import_error_gracefully(self, tmp_path):
        """guardrails.py with syntax error returns None, doesn't crash."""
        guardrails_file = tmp_path / "guardrails.py"
        guardrails_file.write_text("def pre_check(\n  # syntax error\n", encoding="utf-8")

        mock_bundle = MagicMock()
        mock_bundle.bundle_root = tmp_path

        with patch("agent_runner_v2.workflow_packages.registry.get_global_registry") as mock_reg:
            mock_registry = MagicMock()
            mock_registry.get.return_value = mock_bundle
            mock_reg.return_value = mock_registry

            result = get_workflow_guardrails("broken_guardrails")

        assert result is None

    def test_uses_bundle_root_not_path(self, tmp_path):
        """Verify we use bundle_root attribute, not path."""
        guardrails_file = tmp_path / "guardrails.py"
        guardrails_file.write_text(
            "def pre_check(step_name, context):\n    return True\n",
            encoding="utf-8",
        )

        mock_bundle = MagicMock()
        mock_bundle.bundle_root = tmp_path
        # Explicitly remove 'path' to prove we don't use it
        del mock_bundle.path

        with patch("agent_runner_v2.workflow_packages.registry.get_global_registry") as mock_reg:
            mock_registry = MagicMock()
            mock_registry.get.return_value = mock_bundle
            mock_reg.return_value = mock_registry

            result = get_workflow_guardrails("uses_bundle_root")

        assert result is not None


# ---------------------------------------------------------------------------
# RuntimeHooks lazy loading
# ---------------------------------------------------------------------------

class TestRuntimeHooksLazyLoading:
    """Test that RuntimeHooks loads modules lazily."""

    def test_init_does_not_import_modules(self):
        """Creating RuntimeHooks doesn't import any runtime modules."""
        hooks = RuntimeHooks()
        assert hooks._workflow_runtime is None
        assert hooks._step_execution_runtime is None
        assert hooks._daemon_runtime is None
        assert hooks._backend_execution is None
        assert hooks._execution_core is None
        assert hooks._job_state is None
        assert hooks._bundle_loader is None

    def test_missing_artifacts_delegates_to_workflow_runtime(self):
        """missing_artifacts() loads workflow_runtime and delegates."""
        hooks = RuntimeHooks()
        mock_module = MagicMock()
        mock_module.missing_artifacts.return_value = ["KEY_A"]
        hooks._workflow_runtime = mock_module

        result = hooks.missing_artifacts(["KEY_A", "KEY_B"], {"KEY_B": "value"})

        mock_module.missing_artifacts.assert_called_once_with(
            ["KEY_A", "KEY_B"], {"KEY_B": "value"}
        )
        assert result == ["KEY_A"]

    def test_load_job_delegates_to_job_state(self):
        """load_job() loads job_state module and delegates."""
        hooks = RuntimeHooks()
        mock_module = MagicMock()
        mock_module.load_job.return_value = {"status": "running"}
        hooks._job_state = mock_module

        result = hooks.load_job("job-1", Path("/repo"))

        mock_module.load_job.assert_called_once_with("job-1", Path("/repo"))
        assert result == {"status": "running"}

    def test_save_job_delegates_to_job_state(self):
        """save_job() loads job_state module and delegates."""
        hooks = RuntimeHooks()
        mock_module = MagicMock()
        hooks._job_state = mock_module

        hooks.save_job("job-1", {"status": "done"}, Path("/repo"))

        mock_module.save_job.assert_called_once_with("job-1", {"status": "done"}, Path("/repo"))

    def test_invoke_prepared_step_delegates_to_execution_core(self):
        """invoke_prepared_step() loads execution_core and delegates."""
        hooks = RuntimeHooks()
        mock_module = MagicMock()
        mock_module.invoke_prepared_step.return_value = "result"
        hooks._execution_core = mock_module

        prepared = MagicMock()
        result = hooks.invoke_prepared_step(prepared)

        mock_module.invoke_prepared_step.assert_called_once_with(prepared)
        assert result == "result"


# ---------------------------------------------------------------------------
# ManualHooks
# ---------------------------------------------------------------------------

class TestManualHooks:
    """Test ManualHooks lazy loading."""

    def test_init_does_not_import_modules(self):
        """Creating ManualHooks doesn't import any modules."""
        hooks = ManualHooks()
        assert hooks._workflow_runtime is None
        assert hooks._cli_runtime is None
        assert hooks._failure_runtime is None
        assert hooks._job_state is None
        assert hooks._state_defaults is None
        assert hooks._task_runtime is None

    def test_missing_artifacts_delegates(self):
        """missing_artifacts() delegates to workflow_runtime."""
        hooks = ManualHooks()
        mock_module = MagicMock()
        mock_module.missing_artifacts.return_value = []
        hooks._workflow_runtime = mock_module

        result = hooks.missing_artifacts(["KEY"], {})

        mock_module.missing_artifacts.assert_called_once()
        assert result == []

    def test_parse_key_value_pairs_delegates(self):
        """parse_key_value_pairs() delegates to workflow_runtime."""
        hooks = ManualHooks()
        mock_module = MagicMock()
        mock_module.parse_key_value_pairs.return_value = {"k": "v"}
        hooks._workflow_runtime = mock_module

        result = hooks.parse_key_value_pairs(["k=v"])

        assert result == {"k": "v"}

    def test_clear_last_failure_delegates(self):
        """clear_last_failure() delegates to failure_runtime."""
        hooks = ManualHooks()
        mock_module = MagicMock()
        hooks._failure_runtime = mock_module

        state = {"last_failure": "error"}
        hooks.clear_last_failure(state)

        mock_module.clear_last_failure.assert_called_once_with(state)

    def test_default_loop_context_delegates(self):
        """default_loop_context() delegates to state_defaults."""
        hooks = ManualHooks()
        mock_module = MagicMock()
        mock_module.default_loop_context.return_value = {"mode": "loop"}
        hooks._state_defaults = mock_module

        result = hooks.default_loop_context()

        assert result == {"mode": "loop"}
