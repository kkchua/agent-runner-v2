"""HappyHorse v1.1 video rendering provider.

Pure call_api() function that generates videos from text prompts and input images
using the HappyHorse v1.1 API (DashScope-style async task submission and polling).

Signature follows TASK-20260815-001-05 Step 1a:
    call_api(prompt, image, config, api_key, base_url) -> dict

The DashScope API uses an async submission model:
1. POST to video-generation endpoint with X-DashScope-Async header
2. Extract task_id from response
3. Poll task status endpoint every 15 seconds (max 120 attempts)
4. On SUCCEEDED: return video URL; on FAILED or timeout: raise RuntimeError
"""
from __future__ import annotations

import time

import requests


def call_api(prompt: str, image: str, config: dict, api_key: str, base_url: str) -> dict:
    """Generate a video from a text prompt and input image using HappyHorse v1.1 (DashScope API).

    Parameters
    ----------
    prompt : str
        Text description of the video to generate.
    image : str
        URL of the input image (first frame). Sent as URL string, NOT base64.
    config : dict
        Provider configuration with keys: model, resolution, and optional ratio, duration.
    api_key : str
        Bearer token for API authentication.
    base_url : str
        Base URL of the DashScope API (e.g., "https://dashscope.aliyuncs.com").

    Returns
    -------
    dict
        {"video_url": "<download_url>"}

    Raises
    ------
    RuntimeError
        If input validation fails, HTTP request fails, response is not valid JSON,
        task_id is missing, task fails, polling times out, or no video URL is found.
    """
    # --- Input validation ---
    if not base_url or not base_url.strip():
        raise RuntimeError("base_url must be a non-empty string")

    missing_keys = [k for k in ("model", "resolution") if k not in config]
    if missing_keys:
        raise RuntimeError(
            f"config is missing required keys: {missing_keys}"
        )

    # --- Build submit request ---
    submit_endpoint = f"{base_url.rstrip('/')}/api/v1/services/aigc/video-generation/video-synthesis"
    submit_payload = {
        "model": config["model"],
        "input": {
            "prompt": prompt,
            "media": [{"type": "first_frame", "url": image}],
        },
        "parameters": {
            "resolution": config["resolution"],
            "ratio": config.get("ratio", "9:16"),
            "duration": config.get("duration", 15),
        },
    }
    submit_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }

    # --- Execute submit with error handling ---
    try:
        submit_resp = requests.post(
            submit_endpoint, headers=submit_headers, json=submit_payload, timeout=500
        )
        submit_resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"HappyHorse submit request failed: {exc}") from exc

    # --- Parse submit response ---
    try:
        submit_data = submit_resp.json()
    except ValueError as exc:
        raise RuntimeError(
            f"HappyHorse submit returned non-JSON response: {exc}"
        ) from exc

    # --- Extract task_id ---
    output = submit_data.get("output", {})
    task_id = output.get("task_id", "")
    if not task_id:
        raise RuntimeError(
            f"HappyHorse submit response missing task_id. Response: {submit_data}"
        )

    # --- Poll loop ---
    poll_endpoint = f"{base_url.rstrip('/')}/api/v1/tasks/{task_id}"
    poll_headers = {"Authorization": f"Bearer {api_key}"}
    max_attempts = 120
    poll_interval = 15
    video_download_url = ""

    for attempt in range(max_attempts):
        time.sleep(poll_interval)
        try:
            poll_resp = requests.get(
                poll_endpoint, headers=poll_headers, timeout=500
            )
            poll_resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            if attempt >= max_attempts - 1:
                raise RuntimeError(
                    f"Polling timed out after {max_attempts} attempts. Last error: {exc}"
                ) from exc
            continue

        # --- Parse poll response ---
        try:
            poll_data = poll_resp.json()
        except ValueError as exc:
            raise RuntimeError(
                f"HappyHorse poll returned non-JSON response: {exc}"
            ) from exc

        poll_output = poll_data.get("output", {})
        task_status = poll_output.get("task_status", "")

        if task_status == "SUCCEEDED":
            video_download_url = poll_output.get("video_url", "")
            if not video_download_url:
                results = poll_output.get("results", [])
                if results:
                    video_download_url = results[0].get("url", "")
            if video_download_url:
                break
            raise RuntimeError(
                "HappyHorse task SUCCEEDED but no video_url found in response"
            )
        elif task_status == "FAILED":
            raise RuntimeError(
                f"HappyHorse task FAILED: {poll_data}"
            )
        # Other statuses (PENDING, etc.): continue polling

    if not video_download_url:
        raise RuntimeError(
            f"Poll timeout: task did not complete within {max_attempts} attempts"
        )

    return {"video_url": video_download_url}
