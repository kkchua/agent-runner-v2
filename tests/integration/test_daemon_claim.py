"""
Integration Test: Daemon's Backend Client Claim Check
This script runs from agent-runner-v2 and uses the exact same V2BackendClient 
class that the Daemon uses to claim work.
"""
import json
import sys
import os
import requests

# Add the agent-runner-v2 root to path so we can import its modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_runner_v2.v2.backend_client import V2BackendClient
from agent_runner_v2.v2.sync import resolve_v2_backend_url, resolve_v2_api_key
from agent_runner_v2.config_loader import load_runner_config

def main():
    print("--- Starting Daemon Client Test ---")

    # 1. Resolve Backend URL and API Key exactly how the Daemon does
    config = load_runner_config()
    
    # Fallbacks as used in daemon_v2.py
    backend_url = os.environ.get("AGENT_RUNNER_V2_BACKEND_URL", "").strip()
    if not backend_url:
        backend_url = str(config.get("v2_backend_url") or "").strip()
    if not backend_url:
        backend_url = str(config.get("backend_url") or "http://127.0.0.1:8100").strip()
        
    api_key = os.environ.get("AGENT_RUNNER_V2_API_KEY", "").strip()
    if not api_key:
        api_key = str(config.get("v2_api_key") or "").strip()

    worker_id = config.get("worker_id", "chua-worker-01")

    print(f"Backend URL: {backend_url}")
    print(f"API Key:     {'(Set)' if api_key else '(Not Set)'}")
    print(f"Worker ID:   {worker_id}")

    if not backend_url:
        print("ERROR: No backend URL configured!")
        return

    # 1.5 Submit a test job (since Daemon only claims)
    print("\n>>> Submitting a test job to ensure queue is not empty...")
    try:
        submit_headers = {"Content-Type": "application/json", "X-API-Key": api_key}
        submit_payload = {
            "workflow_name": "agnes_media_gen_v1",
            "worker_id": worker_id,
            "project_root": "D:\\TestRoot",
            "implementation_name": "agnes_media_v1", 
            "prompt_selections": {"test": "val"}
        }
        res = requests.post(f"{backend_url}/api/runs", json=submit_payload, headers=submit_headers)
        if res.status_code in (200, 201):
            print(f"[OK] Job Submitted: {res.json().get('run_code')}")
        else:
            print(f"[WARN] Submit failed ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"[WARN] Submit failed: {e}")

    # 2. Initialize the exact client the Daemon uses
    client = V2BackendClient(backend_url, api_key=api_key, timeout_seconds=10)

    try:
        print(f"\n>>> Calling client.claim_work(worker_id='{worker_id}') ...")
        response = client.claim_work(worker_id=worker_id)
        
        print(f"Response Type: {type(response)}")
        print(f"Response Content:")
        print(json.dumps(response, indent=2))

        run_data = response.get("run")
        if run_data:
            keys = list(run_data.keys())
            print(f"\n>>> 'run' Keys Found: {keys}")
            
            if "implementation_name" in keys:
                print(f"[OK] SUCCESS: implementation_name = {run_data['implementation_name']}")
                assert run_data['implementation_name'] == "agnes_media_v1"
            else:
                print("[FAIL] MISSING: implementation_name is NOT in the keys!")
        else:
            print("\n[INFO] No run available to claim.")

    except Exception as e:
        print(f"[FAIL] Exception during claim: {e}")

if __name__ == "__main__":
    main()
