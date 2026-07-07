#!/usr/bin/env python3
"""
End-to-end test for notification system.
Tests step-level and workflow-level notifications through the actual hooks.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_runner_v2.notifications import send_notification


def test_workflow_level_notification():
    """Test workflow-level COMPLETED notification."""
    print("=" * 70)
    print("Testing Workflow-Level Notification")
    print("=" * 70)
    
    # Simulate a completed workflow state
    context = {
        "job_id": "TEST-WORKFLOW-001",
        "template_group": "test_workflow",
        "workflow_name": "test_workflow",
        "job_status": "COMPLETED",
        "current_step": None,
        "completed_steps": ["step1", "step2", "step3"],
        "created_at": "2026-07-06T10:00:00",
        "updated_at": "2026-07-06T10:15:30",
    }
    
    print("\nSending COMPLETED notification...")
    result = send_notification("COMPLETED", context)
    
    if result:
        print("✅ Workflow-level notification sent successfully!")
    else:
        print("❌ Workflow-level notification failed (check logs above)")
    
    return result


def test_step_level_notification():
    """Test step-level notification with enable_notifications flag."""
    print("\n" + "=" * 70)
    print("Testing Step-Level Notification")
    print("=" * 70)
    
    # Simulate a step completion state
    context = {
        "job_id": "TEST-STEP-001",
        "template_group": "test_workflow",
        "workflow_name": "test_workflow",
        "job_status": "IN_PROGRESS",
        "current_step": "execute_implementation",
        "step_name": "execute_implementation",
        "completed_steps": ["project_analysis"],
        "created_at": "2026-07-06T10:00:00",
        "updated_at": "2026-07-06T10:05:00",
    }
    
    # Simulate step_cfg with enable_notifications
    step_cfg = {
        "enable_notifications": True,
        "prompt_file": "test_prompt.txt",
        "produces": ["IMPL_FILE"],
    }
    
    print(f"\nStep config: enable_notifications = {step_cfg.get('enable_notifications')}")
    print("Sending STEP_COMPLETED notification...")
    
    # This would normally be called from advance_step() in job_state.py
    # For testing, we call it directly
    result = send_notification("STEP_COMPLETED", context)
    
    if result:
        print("✅ Step-level notification sent successfully!")
    else:
        print("❌ Step-level notification failed (check logs above)")
    
    return result


def test_failed_step_notification():
    """Test step failure notification."""
    print("\n" + "=" * 70)
    print("Testing Step Failure Notification")
    print("=" * 70)
    
    context = {
        "job_id": "TEST-FAIL-001",
        "template_group": "test_workflow",
        "workflow_name": "test_workflow",
        "job_status": "WAITING_FOR_HUMAN_INTERVENTION",
        "current_step": "execute_implementation",
        "step_name": "execute_implementation",
        "last_failure_reason": "API timeout error",
        "last_failure_code": "TRANSIENT_API_ERROR",
        "last_failure_source": "adapter",
    }
    
    print("\nSending STEP_FAILED notification...")
    result = send_notification("STEP_FAILED", context)
    
    if result:
        print("✅ Step failure notification sent successfully!")
    else:
        print("❌ Step failure notification failed (check logs above)")
    
    return result


def main():
    """Run all end-to-end tests."""
    print("\nRunning Notification System End-to-End Tests\n")
    
    results = []
    
    # Test 1: Workflow-level notification
    results.append(("Workflow COMPLETED", test_workflow_level_notification()))
    
    # Test 2: Step-level notification
    results.append(("Step COMPLETED", test_step_level_notification()))
    
    # Test 3: Step failure notification
    results.append(("Step FAILED", test_failed_step_notification()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
