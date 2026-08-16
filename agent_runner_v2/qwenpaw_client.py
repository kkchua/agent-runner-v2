#!/usr/bin/env python3
"""
qwenpaw_client.py — Client for interacting with the QwenPaw Agent REST API 
and Telegram Bot API.

Provides functions to push updates to:
1. QwenPaw Console (for the agent to monitor).
2. Telegram (for the user to see).
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Any


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

def _resolve_credentials() -> tuple[str, str, str, str, str]:
    """Resolve QwenPaw and Telegram credentials.

    Returns (qwenpaw_url, agent_id, session_id, tg_bot_token, tg_chat_id).
    """
    # Load .env file first to ensure we get the tokens
    try:
        from dotenv import load_dotenv
        import os
        # Try to find .env in current dir or parent dir
        from pathlib import Path
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=True) # Force override to use repo settings
    except ImportError:
        pass
    
    # QwenPaw Credentials
    base_url = os.environ.get("QWENPAW_BASE_URL", "http://localhost:8088").strip()
    agent_id = os.environ.get("QWENPAW_AGENT_ID", "default").strip()
    session_id = os.environ.get("QWENPAW_SESSION_ID", "telegram:1531706495").strip()
    
    # Telegram Credentials (from env)
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    # Priority 1: Group Chat ID
    tg_chat = os.environ.get("TELEGRAM_GROUPCHAT_ID", "").strip()
    # Priority 2: Private Chat ID
    if not tg_chat:
        tg_chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    
    return base_url, agent_id, session_id, tg_token, tg_chat


# ---------------------------------------------------------------------------
# 1. QwenPaw Console Notification
# ---------------------------------------------------------------------------

def notify_qwenpaw_agent(
    message: str,
    session_id: str | None = None,
    agent_id: str | None = None,
    base_url: str | None = None,
    user_id: str = "agent-runner-v2",
    timeout: int = 10
) -> bool:
    """Sends a message to the QwenPaw Console."""
    try:
        def_url, def_agent, def_session, _, _ = _resolve_credentials()
        final_url = base_url or def_url
        final_agent = agent_id or def_agent
        final_session = session_id or def_session

        if not final_url or not final_agent or not final_session:
            print("[qwenpaw_client] Missing QwenPaw credentials.", flush=True)
            return False

        payload = {
            "input": [{"role": "user", "content": [{"type": "text", "text": message}]}],
            "session_id": final_session,
            "user_id": user_id,
            "channel": "console"
        }

        chat_url = f"{final_url}/api/console/chat"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(chat_url, data=data, method="POST", headers={"Content-Type": "application/json", "X-Agent-Id": final_agent})

        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                print(f"[qwenpaw_client] Sent to Console: {final_session}", flush=True)
                return True
    except Exception as exc:
        print(f"[qwenpaw_client] QwenPaw notification failed: {exc}", flush=True)
    return False


# ---------------------------------------------------------------------------
# 2. Telegram Bot Notification
# ---------------------------------------------------------------------------

def notify_telegram(
    message: str,
    bot_token: str | None = None,
    chat_id: str | None = None,
    timeout: int = 10
) -> bool:
    """Sends a message directly to Telegram via the Official Bot API."""
    try:
        _, _, _, def_token, def_chat = _resolve_credentials()
        final_token = bot_token or def_token
        final_chat = chat_id or def_chat

        if not final_token or not final_chat:
            print("[qwenpaw_client] Missing Telegram credentials (TELEGRAM_BOT_TOKEN/CHAT_ID).", flush=True)
            return False

        # Official Telegram Bot API URL
        url = f"https://api.telegram.org/bot{final_token}/sendMessage"
        
        # Using HTML parse_mode which is more robust than Markdown for auto-generated text
        payload = {
            "chat_id": final_chat,
            "text": message,
            "parse_mode": "HTML"
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})

        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("ok"):
                print(f"[qwenpaw_client] Sent to Telegram via {final_token[:10]}... to chat {final_chat}", flush=True)
                return True
            else:
                print(f"[qwenpaw_client] Telegram API Error: {result.get('description')}", flush=True)
                return False
    except Exception as exc:
        print(f"[qwenpaw_client] Telegram notification failed: {exc}", flush=True)
    return False
