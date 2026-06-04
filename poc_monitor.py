#!/usr/bin/env python3
"""
POC: Monitor script - checks background job state.
Reports: running, completed, failed, stuck/hung.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

STATE_FILE = "/tmp/poc-job-state.json"

def check():
    if not os.path.exists(STATE_FILE):
        return "no_state", "No state file found (job not started yet)"
    
    with open(STATE_FILE) as f:
        state = json.load(f)
    
    status = state.get("status", "unknown")
    step = state.get("step", "")
    detail = state.get("detail", "")
    ts = state.get("timestamp", "")
    
    return status, f"step={step}, detail={detail}, ts={ts}"

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "check"
    
    if action == "check":
        status, detail = check()
        print(f"Status: {status}")
        print(f"Detail: {detail}")
    elif action == "watch":
        print("Watching state file (Ctrl+C to stop)...")
        last = None
        while True:
            status, detail = check()
            current = f"{status}: {detail}"
            if current != last:
                print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {current}")
                last = current
                if status in ("all_completed", "job_failed", "no_state"):
                    break
            time.sleep(1)

if __name__ == "__main__":
    main()
