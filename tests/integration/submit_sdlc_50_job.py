"""
Submit Job: sdlc_50_implementation_v1
"""
import requests
import json

BASE_URL = "http://192.168.0.200:8200"
AUTH_TOKEN = "arb_Mt2V0E1ZHT2cynlfkokSfsx3sW_YTxe_iWt982Stslc"

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": AUTH_TOKEN
}

# The input file we want to process
# We pass ONLY the filename because context_extensions.py now resolves it to the correct folder.
TASK_FILENAME = "TASK-20260814-001-01_gen-media-content-scaffolding.md"

def main():
    print("--- Submitting Job to sdlc_50_implementation_v1 ---")
    
    payload = {
        "workflow_name": "sdlc_50_implementation_v1",
        "worker_id": "chua-worker-01",
        "project_root": "D:\\MyProjectSpace\\01_Workflows\\agent-runner-v2",
        "input_payload": {
            "TASK_FILE": TASK_FILENAME
        }
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        res = requests.post(f"{BASE_URL}/api/runs", json=payload, headers=HEADERS)
        print(f"Status: {res.status_code}")
        
        if res.status_code in (200, 201):
            data = res.json()
            print(f"[OK] Job Submitted! Run Code: {data.get('run_code')}")
            print(f"   ID: {data.get('run_id')}")
        else:
            print(f"❌ Error: {res.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
