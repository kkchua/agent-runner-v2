#!/usr/bin/env python3
"""
POC: Background job runner with monitoring.
Demonstrates: run, monitor (completed/stuck/hung), rectify.
"""

import json
import os
import subprocess
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

def run_step(step_name, duration=3, should_fail=False):
    """Simulate a job step."""
    log(f"Starting step: {step_name} (will take ~{duration}s)")
    save_state("running", step_name)
    
    for i in range(duration):
        time.sleep(1)
        log(f"  ... {step_name} progress {i+1}/{duration}")
    
    if should_fail:
        log(f"Step {step_name} FAILED")
        save_state("failed", step_name, "Simulated failure")
        return False
    
    log(f"Step {step_name} COMPLETED")
    save_state("completed", step_name)
    return True

def check_stuck(proc, last_output_time, timeout=15):
    """Check if process is stuck (no output for N seconds)."""
    elapsed = time.time() - last_output_time
    if elapsed > timeout:
        return True, f"No output for {elapsed:.0f}s (timeout: {timeout}s)"
    return False, None

def main():
    log("=== POC Background Job Runner ===")
    log(f"PID: {os.getpid()}")
    
    save_state("starting")
    
    # Simulate running steps
    steps = [
        ("step_1_fast", 2, False),
        ("step_2_slow", 3, False),
        ("step_3_final", 2, False),
    ]
    
    all_ok = True
    for step_name, duration, should_fail in steps:
        if not run_step(step_name, duration, should_fail):
            all_ok = False
            break
    
    if all_ok:
        log("=== ALL STEPS COMPLETED ===")
        save_state("all_completed")
    else:
        log("=== JOB FAILED ===")
        save_state("job_failed")

if __name__ == "__main__":
    main()
