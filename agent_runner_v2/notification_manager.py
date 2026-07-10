"""
notification_manager.py - Centralized notification management for all execution modes.

Provides unified interface for sending workflow and step notifications with consistent
context enrichment and logging.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .notifications import send_notification as _send_notification


def should_send_notifications() -> bool:
    """Check if notifications are enabled globally."""
    try:
        config_path = Path.home() / ".ukbe-runner" / "config.json"
        if not config_path.exists():
            return False
        config = json.loads(config_path.read_text(encoding="utf-8"))
        return bool(config.get("notification", {}).get("enabled", False))
    except Exception:
        return False


def _enrich_context(context: dict[str, Any]) -> dict[str, Any]:
    """Ensure context has all required fields for notifications.
    
    Adds missing fields with sensible defaults:
    - workflow_name: Falls back to template_group if not present
    - job_id: Defaults to "unknown" if missing
    - current_step: Ensures step name is available for step notifications
    """
    enriched = dict(context)
    
    # Ensure workflow_name is set (fallback to template_group)
    if not enriched.get("workflow_name"):
        enriched["workflow_name"] = enriched.get("template_group", "unknown")
    
    # Ensure job_id is set
    if not enriched.get("job_id"):
        enriched["job_id"] = "unknown"
    
    return enriched


def send_workflow_notification(status: str, context: dict[str, Any]) -> bool:
    """Send workflow-level notification (COMPLETED, FAILED, WAITING_FOR_HUMAN_INTERVENTION).
    
    Args:
        status: One of COMPLETED, FAILED, WAITING_FOR_HUMAN_INTERVENTION
        context: Job state dict or relevant context
        
    Returns:
        True if notification sent successfully, False otherwise
    """
    if not should_send_notifications():
        print(f"[notification_manager] Notifications disabled, skipping {status}", flush=True)
        return False
    
    enriched = _enrich_context(context)
    print(f"[notification_manager] Sending WORKFLOW notification: {status} for job {enriched.get('job_id')}", flush=True)
    
    result = _send_notification(status, enriched)
    print(f"[notification_manager] Workflow notification result: {result}", flush=True)
    return result


def send_step_notification(status: str, context: dict[str, Any], step: str, step_cfg: dict[str, Any]) -> bool:
    """Send step-level notification (STEP_COMPLETED, STEP_FAILED).
    
    Checks both global config AND step-level enable_notifications flag.
    
    Args:
        status: One of STEP_COMPLETED, STEP_FAILED
        context: Job state dict
        step: Step name
        step_cfg: Step configuration dict (to check enable_notifications)
        
    Returns:
        True if notification sent successfully, False otherwise
    """
    # Check step-level flag first
    if not step_cfg.get("enable_notifications", False):
        return False
    
    # Check global config
    if not should_send_notifications():
        return False
    
    enriched = _enrich_context(context)
    enriched["current_step"] = step
    enriched["step_name"] = step
    
    print(f"[notification_manager] Sending STEP notification: {status} for step {step}", flush=True)
    
    result = _send_notification(status, enriched)
    print(f"[notification_manager] Step notification result: {result}", flush=True)
    return result
