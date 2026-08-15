"""
Test script for the QwenPaw Client.
Run this from the repo root: python -m agent_runner_v2.qwenpaw_client_test
Or directly: python test_qwenpaw_agent_push.py
"""
import sys
import os

# Ensure the repo is in the path so we can import the package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_runner_v2.qwenpaw_client import notify_qwenpaw_agent, notify_telegram

def main():
    msg = (
        "🧪 **Unit Test from Agent Runner**\n\n"
        "This is a test of the dual notification system!"
    )
    
    print("--- 1. Testing notify_qwenpaw_agent (Console) ---")
    success_console = notify_qwenpaw_agent(
        message=f"{msg}\n(This went to QwenPaw Console)",
        session_id="telegram:1531706495", 
        agent_id="default"
    )
    print(f"Console Result: {'SUCCESS' if success_console else 'FAILURE'}")

    print("\n--- 2. Testing notify_telegram (Bot) ---")
    success_telegram = notify_telegram(
        message=f"{msg}\n(This went to Telegram Bot)"
    )
    print(f"Telegram Result: {'SUCCESS' if success_telegram else 'FAILURE'}")

    if success_console and success_telegram:
        print("\nBOTH SUCCESS! The runner can now notify both.")
    else:
        print("\nSome notifications failed.")

if __name__ == "__main__":
    main()
