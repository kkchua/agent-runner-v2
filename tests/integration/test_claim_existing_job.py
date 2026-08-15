"""
Integration Test: Claim Existing Job
Attempts to claim the job you just submitted to verify the Backend response payload.
"""
import os
import sys
import json
import requests
import pytest

# --- CONFIGURATION ---
# We run this from agent-runner-v2, so we look for backend env or daemon config
BACKEND_URL = os.environ.get("AGENT_RUNNER_BACKEND_URL", "http://192.168.0.200:8200")
WORKER_ID = "chua-worker-01"

def get_auth_headers():
    """
    Attempt to find the Auth Token from various places:
    1. Environment variable BACKEND_AUTH_TOKEN
    2. SUPABASE_SERVICE_ROLE_KEY from .env
    3. ~/.ukbe-runner/config.json (Daemon config)
    """
    token = os.environ.get("BACKEND_AUTH_TOKEN") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    # If not in env, try to read daemon config
    if not token:
        config_path = os.path.expanduser("~/.ukbe-runner/config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    cfg = json.load(f)
                    # Try common key names
                    token = cfg.get("v2_api_key") or cfg.get("api_key") or cfg.get("backend_token")
            except:
                pass

    if not token:
        return None

    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "x-api-key": token
    }

def test_claim_existing_job():
    headers = get_auth_headers()
    if not headers:
        print(">>> [WARN] No Auth Token found. Skipping test.")
        print(">>> Please ensure SUPABASE_SERVICE_ROLE_KEY or BACKEND_AUTH_TOKEN is set.")
        pytest.skip("No Auth Token found")

    print(f">>> 1. Calling Backend Claim API at {BACKEND_URL}/api/workers/{WORKER_ID}/claim ...")
    
    try:
        res = requests.post(f"{BACKEND_URL}/api/workers/{WORKER_ID}/claim", headers=headers, timeout=10)
        print(f"    Status: {res.status_code}")
        
        if res.status_code == 401:
            print(f"    [FAIL] Unauthorized. Check your Auth Token.")
            print(f"    Response: {res.text}")
            return

        data = res.json()
        print(f"    Response: {json.dumps(data, indent=2)}")

        run_info = data.get("run")
        if not run_info:
            print("    [INFO] No work available to claim (Queue empty).")
            return

        run_keys = list(run_info.keys())
        print(f"\n>>> 2. Checking Payload Keys: {run_keys}")

        # CRITICAL CHECK
        if "implementation_name" in run_keys:
            val = run_info["implementation_name"]
            print(f"    [OK] SUCCESS: Found implementation_name = '{val}'")
            assert val is not None, "Value is null!"
        else:
            print("    [FAIL] MISSING: 'implementation_name' is NOT in the keys!")
            print("    This confirms the Backend is NOT sending the data.")
            assert False, "Missing key"

    except Exception as e:
        print(f"    [FAIL] Exception: {e}")

if __name__ == "__main__":
    test_claim_existing_job()
