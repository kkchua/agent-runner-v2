"""
Check recent runs for sdlc_50_implementation_v1
"""
import requests

BASE_URL = "http://192.168.0.200:8200"
AUTH_TOKEN = "arb_Mt2V0E1ZHT2cynlfkokSfsx3sW_YTxe_iWt982Stslc"

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": AUTH_TOKEN
}

def main():
    print("--- Checking Backend Runs ---")
    res = requests.get(f"{BASE_URL}/api/runs?limit=5", headers=HEADERS)
    
    if res.status_code == 200:
        runs = res.json()
        print(f"Found {len(runs.get('runs', []))} runs")
        for r in runs.get('runs', []):
            if 'sdlc_50' in r.get('workflow_name', ''):
                print(f"\nRun Code: {r.get('run_code')}")
                print(f"  Status: {r.get('run_status')}")
                print(f"  Worker: {r.get('target_worker_id')}")
    else:
        print(f"Error: {res.text}")

if __name__ == "__main__":
    main()
