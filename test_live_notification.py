"""
Manual test to trigger a real Telegram notification from the runner.
Run this from the repo root: python test_live_notification.py
"""
import sys
import os

# Ensure we can import the package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_runner_v2.notifications import send_notification

# Simulate a job completion context
context = {
    "job_id": "LIVE-TEST-001",
    "workflow_name": "test_workflow_manual",
    "last_failure_step": None,
    "last_failure_reason": None,
    "last_failure_code": None,
}

print("--- Triggering Live Notification ---")
print("If successful, check your Telegram bot!")

# Send a "COMPLETED" notification
success = send_notification(status="COMPLETED", context=context)

if success:
    print("Notification sent successfully.")
else:
    print("Notification failed. Check logs.")
