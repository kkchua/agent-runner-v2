#!/usr/bin/env python3
"""
Test notification module functionality.
"""
import os
import sys
from pathlib import Path

# Add project root to path (tests/ is a subdirectory of the root)
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_runner_v2.notifications import (
    _resolve_credentials,
    _load_notification_config,
    _build_message,
    send_notification,
)


def test_resolve_credentials_no_env():
    """Test credential resolution when no env vars are set."""
    # Clear env vars
    old_token = os.environ.pop("PUSHOVER_API_TOKEN", None)
    old_user_key = os.environ.pop("PUSHOVER_USER_KEY", None)
    
    try:
        token, user_key = _resolve_credentials()
        # Should return None if not in config.json either
        print(f"✓ Credentials resolved: token={token is not None}, user_key={user_key is not None}")
    finally:
        # Restore env vars
        if old_token:
            os.environ["PUSHOVER_API_TOKEN"] = old_token
        if old_user_key:
            os.environ["PUSHOVER_USER_KEY"] = old_user_key


def test_load_notification_config():
    """Test loading notification configuration."""
    config = _load_notification_config()
    assert "enabled" in config
    assert "message_config" in config
    assert "priority_by_status" in config
    print(f"✓ Config loaded: enabled={config['enabled']}")


def test_build_message_completed():
    """Test building COMPLETED message."""
    context = {
        "job_id": "TEST-001",
        "workflow_name": "test_workflow",
        "template_group": "test_group",
        "created_at": "2026-07-06T10:00:00",
        "updated_at": "2026-07-06T10:05:30",
    }
    config = {
        "enabled": True,
        "message_config": {
            "include_job_id": True,
            "include_workflow_name": True,
            "include_template_group": True,
            "include_duration": True,
            "include_failed_step": False,
            "include_retry_counts": False,
            "include_artifacts_summary": False,
            "custom_template": None,
        },
        "priority_by_status": {
            "COMPLETED": 0,
            "FAILED": 1,
        }
    }
    
    title, message, priority = _build_message("COMPLETED", context, config)
    assert "✅" in title
    assert "COMPLETED" in title
    assert "TEST-001" in message
    assert "test_workflow" in message
    assert priority == 0
    print(f"✓ COMPLETED message built: title='{title}', priority={priority}")


def test_build_message_failed():
    """Test building FAILED message."""
    context = {
        "job_id": "TEST-002",
        "workflow_name": "test_workflow",
        "template_group": "test_group",
        "current_step": "execute_task",
        "last_failure_reason": "API timeout error",
        "last_failure_code": "TRANSIENT_API_ERROR",
        "reject_counts": {"execute_task": 3},
    }
    config = {
        "enabled": True,
        "message_config": {
            "include_job_id": True,
            "include_workflow_name": True,
            "include_template_group": True,
            "include_duration": False,
            "include_failed_step": True,
            "include_retry_counts": True,
            "include_artifacts_summary": False,
            "custom_template": None,
        },
        "priority_by_status": {
            "COMPLETED": 0,
            "FAILED": 1,
        }
    }
    
    title, message, priority = _build_message("FAILED", context, config)
    assert "❌" in title
    assert "FAILED" in title
    assert "execute_task" in message
    assert "API timeout" in message
    assert priority == 1
    assert "_pushover_extras" in context  # Emergency retry/expire added
    print(f"✓ FAILED message built: title='{title}', priority={priority}")


def test_send_notification_disabled():
    """Test that disabled notifications don't send."""
    result = send_notification("COMPLETED", {"job_id": "TEST"})
    assert result is False
    print("✓ Disabled notification correctly returned False")


def main():
    """Run all tests."""
    print("Testing notification module...\n")
    
    test_resolve_credentials_no_env()
    test_load_notification_config()
    test_build_message_completed()
    test_build_message_failed()
    test_send_notification_disabled()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()
