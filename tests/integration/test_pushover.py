#!/usr/bin/env python3
"""
Test Pushover notification directly.
Uses the same credential resolution logic as the notification system.
"""
import sys
from pathlib import Path

# Add project root to path (tests/ is a subdirectory)
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_runner_v2.notifications import (
    _resolve_credentials,
    _load_notification_config,
    _pushover_api_call,
)


def test_pushover_direct():
    """Send a test notification directly to Pushover."""
    print("=" * 70)
    print("Pushover Notification Test")
    print("=" * 70)
    
    # Load config
    print("\n1. Loading notification configuration...")
    config = _load_notification_config()
    print(f"   Enabled: {config.get('enabled', False)}")
    print(f"   API URL: {config.get('notify_api_url', 'N/A')}")
    
    if not config.get('enabled', False):
        print("\n❌ Notifications are DISABLED in config.json")
        print("   Fix: Set \"enabled\": true in your config.json")
        return False
    
    # Resolve credentials (uses shared logic - loads .env automatically)
    print("\n2. Resolving credentials (using shared _resolve_credentials)...")
    api_token, user_key = _resolve_credentials()
    
    if not api_token:
        print("   ❌ API Token: NOT SET")
        print("   Fix: Set PUSHOVER_API_TOKEN in .env or api_token in config.json")
    else:
        print(f"   ✓ API Token: {api_token[:8]}...{api_token[-4:]}")
    
    if not user_key:
        print("   ❌ User Key: NOT SET")
        print("   Fix: Set PUSHOVER_USER_KEY in .env or user_key in config.json")
    else:
        print(f"   ✓ User Key: {user_key[:8]}...{user_key[-4:]}")
    
    if not api_token or not user_key:
        print("\n❌ Missing credentials - cannot send notification")
        return False
    
    # Send test notification
    print("\n3. Sending test notification...")
    success = _pushover_api_call(
        api_token=api_token,
        user_key=user_key,
        title="🧪 Test Notification",
        message="This is a test notification from agent-runner-v2.\n\nIf you see this, Pushover integration is working!",
        priority=0,
        api_url=config.get('notify_api_url', 'https://api.pushover.net/1/messages.json'),
    )
    
    if success:
        print("\n✅ SUCCESS! Test notification sent successfully!")
        print("   Check your Pushover app/device for the message.")
        return True
    else:
        print("\n❌ FAILED! Could not send notification.")
        print("   Possible issues:")
        print("   - Invalid API token or user key")
        print("   - Network/firewall blocking the request")
        print("   - Pushover API is down")
        return False


if __name__ == "__main__":
    result = test_pushover_direct()
    sys.exit(0 if result else 1)
