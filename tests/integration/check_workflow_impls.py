"""
Test: Check what the Backend knows about workflow implementations
"""
import json
import requests

BASE_URL = "http://192.168.0.200:8200"
AUTH_TOKEN = "arb_Mt2V0E1ZHT2cynlfkokSfsx3sW_YTxe_iWt982Stslc"

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": AUTH_TOKEN
}

def main():
    print("--- Checking Workflow Implementations ---")
    res = requests.get(f"{BASE_URL}/api/workflows", headers=HEADERS)
    print(f"Status: {res.status_code}")
    
    if res.status_code != 200:
        print(f"Error: {res.text}")
        return

    workflows = res.json()
    for wf in workflows:
        if "media" in wf["workflow_name"]:
            print(f"\nWorkflow: {wf['workflow_name']}")
            print(f"  Implementations: {json.dumps(wf.get('implementations', []), indent=2)}")

if __name__ == "__main__":
    main()
