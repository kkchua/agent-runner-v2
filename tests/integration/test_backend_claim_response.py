"""Integration test to verify the Backend API returns the correct claim payload."""
import os
import sys
import json
import requests
import pytest

# Try to load backend .env if present
BACKEND_ENV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "agent-runner-backend-v2", ".env")
if os.path.exists(BACKEND_ENV_PATH):
    try:
        import dotenv
        dotenv.load_dotenv(BACKEND_ENV_PATH)
    except ImportError:
        pass

BASE_URL = os.environ.get("AGENT_RUNNER_BACKEND_URL", "http://192.168.0.200:8200")
AUTH_TOKEN = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
WORKER_ID = "test-worker-unit"

@pytest.mark.skipif(not AUTH_TOKEN, reason="SUPABASE_SERVICE_ROLE_KEY not set")
def test_claim_response_contains_implementation_name():
    """Verify that the Backend Claim API returns 'implementation_name' in the run object."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "apikey": AUTH_TOKEN
    }

    # 1. Submit a run with implementation_name
    run_payload = {
        "workflow_name": "agnes_media_gen_v1",
        "worker_id": WORKER_ID,
        "project_root": "D:\\TestRoot",
        "implementation_name": "agnes_media_v1",
        "prompt_selections": {"step_1": "variant_a"}
    }
    
    # We expect this to fail if backend is down, which is fine for local dev
    # But we want to check the structure if it works.
    print(f"\n>>> Submitting to {BASE_URL}/api/runs ...")
    try:
        res = requests.post(f"{BASE_URL}/api/runs", json=run_payload, headers=headers, timeout=5)
        print(f"   Status: {res.status_code}")
        if res.status_code not in (200, 201):
            print(f"   Error: {res.text}")
            pytest.skip(f"Backend not reachable or auth failed: {res.status_code}")
    except requests.ConnectionError:
        pytest.skip(f"Backend not reachable at {BASE_URL}")

    run_data = res.json()
    print(f"   [OK] Run Submitted: {run_data.get('run_code')}")

    # 2. Register Worker
    requests.post(f"{BASE_URL}/api/workers/register", 
                  json={"worker_id": WORKER_ID, "capabilities": {"max_parallel": 5}}, 
                  headers=headers)

    # 3. Claim Work
    print(f"\n>>> Claiming from {BASE_URL}/api/workers/{WORKER_ID}/claim ...")
    res = requests.post(f"{BASE_URL}/api/workers/{WORKER_ID}/claim", headers=headers, timeout=5)
    print(f"   Status: {res.status_code}")
    claim_json = res.json()
    print(f"   Response Keys: {list(claim_json.keys())}")

    run_info = claim_json.get("run")
    assert run_info is not None, "Claim response missing 'run' object"
    
    run_keys = list(run_info.keys())
    print(f"   Run Keys: {run_keys}")
    
    # THE CRITICAL CHECK
    assert "implementation_name" in run_keys, \
        f"[FAIL] Backend did not return 'implementation_name' in claim response! Keys: {run_keys}"
        
    assert run_info["implementation_name"] == "agnes_media_v1", \
        f"[FAIL] Wrong value. Expected 'agnes_media_v1', got '{run_info['implementation_name']}'"
        
    print("[OK] SUCCESS: Backend claim payload is correct.")
