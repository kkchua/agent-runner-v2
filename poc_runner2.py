#!/usr/bin/env python3
"""
POC Runner v2: Supports stuck/hang simulation.
Usage: poc_runner2.py [--stuck N] [--fail-at N]
  --stuck N: Step N will hang (sleep forever)
  --fail-at N: Step N will fail
"""

import json
import os
import sys
import time
from datetime import datetime, timezone

STATE_FILE = "/tmp/poc-job-state.json"

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[POC {ts}] {msg}", flush=True)

def save_state(status, step=None, detail=None):
    state = {
        "status": status,
        "step": step,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def run_step(step_name, duration=2, stuck=False, fail=False):
    log(f"Starting step: {step_name} ({duration}s)")
    save_state("running", step_name)
    
    for i in range(duration):
        time.sleep(1)
        log(f"  ... {step_name} progress {i+1}/{duration}")
    
    if stuck:
        log(f"⚠️  {step_name} STUCK - hanging forever (simulate timeout)")
        save_state("stuck", step_name, "Process hung, no progress")
        while True:
            time.sleep(60)
    
    if fail:
        log(f"✗ Step {step_name} FAILED")
        save_state("failed", step_name, "Simulated failure")
        sys.exit(1)
    
    log(f"✓ Step {step_name} COMPLETED")
    save_state("completed", step_name)
    return True

def main():
    stuck_step = None
    fail_at = None
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--stuck" and i+1 < len(args):
            stuck_step = int(args[i+1])
            i += 2
        elif args[i] == "--fail-at" and i+1 < len(args):
            fail_at = int(args[i+1])
            i += 2
        else:
            i += 1
    
    log(f"=== POC Background Job Runner v2 ===")
    log(f"PID: {os.getpid()} | stuck_step={stuck_step} | fail_at={fail_at}")
    
    save_state("starting")
    
    steps = [
        ("step_1_fast", 2),
        ("step_2_slow", 3),
        ("step_3_final", 2),
    ]
    
    for idx, (step_name, duration) in enumerate(steps, 1):
        stuck = (idx == stuck_step)
        fail = (idx == fail_at)
        run_step(step_name, duration, stuck=stuck, fail=fail)
    
    log("=== ALL STEPS COMPLETED ===")
    save_state("all_completed")

if __name__ == "__main__":
    main()
