"""Tests for runner_actions.py — registry, dispatch, unknown action error.

Uses mock.patch for action functions since we only test the registry/dispatch layer.
"""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from agent_runner_v2.runner_actions import (
    ACTION_REGISTRY,
    execute,
    get_registered_actions,
)
from agent_runner_v2.action_result import ActionResult


# ====================================================================
# ACTION_REGISTRY
# ====================================================================

class TestActionRegistry:
    def test_is_dict(self):
        assert isinstance(ACTION_REGISTRY, dict)

    def test_contains_expected_actions(self):
        """Registry should contain the three built-in actions."""
        assert "submit_comfyui" in ACTION_REGISTRY
        assert "validate_delivery_docs" in ACTION_REGISTRY
        assert "archive_images" in ACTION_REGISTRY

    def test_all_values_are_callable(self):
        for name, fn in ACTION_REGISTRY.items():
            assert callable(fn), f"Action '{name}' is not callable"

    def test_no_duplicate_keys(self):
        keys = list(ACTION_REGISTRY.keys())
        assert len(keys) == len(set(keys))


# ====================================================================
# execute()
# ====================================================================

class TestExecute:
    def test_dispatch_to_registered_action(self):
        """execute() should call the registered action function with correct kwargs."""
        mock_fn = MagicMock(return_value=ActionResult(status="APPROVED", remark="ok", artifacts={}))

        with patch.dict(ACTION_REGISTRY, {"test_action": mock_fn}):
            result = execute(
                action_name="test_action",
                context={"KEY": "value"},
                state={"artifacts": {}},
                step_cfg={"produces": ["X"]},
                step="some_step",
                project_root=Path("/tmp"),
            )

        mock_fn.assert_called_once()
        call_kwargs = mock_fn.call_args[1]
        assert call_kwargs["context"] == {"KEY": "value"}
        assert call_kwargs["state"] == {"artifacts": {}}
        assert call_kwargs["step_cfg"] == {"produces": ["X"]}
        assert result.status == "APPROVED"

    def test_unknown_action_raises_key_error(self):
        """execute() should raise KeyError for unregistered actions."""
        with pytest.raises(KeyError, match="Unknown runner action 'nonexistent'"):
            execute(
                action_name="nonexistent",
                context={},
                state={},
                step_cfg={},
                step="step",
                project_root=Path("/tmp"),
            )

    def test_unknown_action_error_message_lists_registered(self):
        """Error message should include sorted list of registered action names."""
        try:
            execute(
                action_name="bogus",
                context={},
                state={},
                step_cfg={},
                step="step",
                project_root=Path("/tmp"),
            )
        except KeyError as exc:
            msg = str(exc)
            assert "Registered actions:" in msg
            # Should list the real registered actions
            for action_name in get_registered_actions():
                assert action_name in msg

    def test_action_exception_propagates(self):
        """If an action raises, the exception should propagate."""
        def failing_action(**kwargs):
            raise ValueError("action failed")

        with patch.dict(ACTION_REGISTRY, {"fail_action": failing_action}):
            with pytest.raises(ValueError, match="action failed"):
                execute(
                    action_name="fail_action",
                    context={},
                    state={},
                    step_cfg={},
                    step="step",
                    project_root=Path("/tmp"),
                )

    def test_action_return_value_passed_through(self):
        """ActionResult from action should be returned directly."""
        expected = ActionResult(
            status="REJECTED",
            remark="validation failed",
            artifacts={"REVIEW_FILE": "review.md"},
            reject_code="VALIDATION_FAIL",
        )
        mock_fn = MagicMock(return_value=expected)

        with patch.dict(ACTION_REGISTRY, {"check": mock_fn}):
            result = execute(
                action_name="check",
                context={},
                state={},
                step_cfg={},
                step="validator",
                project_root=Path("/tmp"),
            )

        assert result is expected
        assert result.status == "REJECTED"
        assert result.reject_code == "VALIDATION_FAIL"


# ====================================================================
# get_registered_actions()
# ====================================================================

class TestGetRegisteredActions:
    def test_returns_list(self):
        result = get_registered_actions()
        assert isinstance(result, list)

    def test_returns_sorted(self):
        result = get_registered_actions()
        assert result == sorted(result)

    def test_contains_all_registry_keys(self):
        result = get_registered_actions()
        assert set(result) == set(ACTION_REGISTRY.keys())

    def test_empty_when_registry_empty(self):
        with patch.dict(ACTION_REGISTRY, {}, clear=True):
            result = get_registered_actions()
            assert result == []
