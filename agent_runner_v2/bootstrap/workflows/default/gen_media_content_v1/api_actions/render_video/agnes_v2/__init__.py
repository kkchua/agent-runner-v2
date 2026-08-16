"""Agnes v2 video rendering provider.

Pure call_api() function that submits video generation jobs and polls until
completion using the Agnes Video V2.0 API (image-to-video).

Signature follows TASK-20260815-001-04 Step 1a:
    call_api(prompt, image, config, api_key, base_url) -> dict

The provider implements an asynchronous two-phase flow:
  1. Submit phase: POST to {base_url}/v1/videos to start video generation.
  2. Poll phase: GET to {base_url}/agnesapi?video_id={id} every 10 seconds,
     up to 120 attempts, until status is "completed", "failed", "error",
     or "cancelled".

Returns {"video_url": "<download_url>"} on success.
Raises RuntimeError on any failure condition.
"""
from __future__ import annotations

import time

import requests


def call_api(
    prompt: str,
    image: str,
    config: dict,
    api_key: str,
    base_url: str,
) -> dict:
    """Submit a video generation job and poll until completion.

    Parameters
    ----------
    prompt : str
        Text description of the video to generate.
    image : str
        URL of the input image for image-to-video generation.
    config : dict
        Provider configuration with keys: model, width, height.
        Optional keys: num_frames, frame_rate, negative_prompt.
    api_key : str
        Bearer token for API authentication.
    base_url : str
        Base URL of the Agnes API (e.g., "https://apihub.agnes-ai.com").

    Returns
    -------
    dict
        {"video_url": "<download_url>"}

    Raises
    ------
    RuntimeError
        If input validation fails, HTTP request fails, response is not
        valid JSON, video_id is missing, poll returns a terminal failure
        status, polling times out, or the completed response contains
        no video URL.
    """
    # --- Input validation ---
    if not base_url or not base_url.strip():
        raise RuntimeError("base_url must be a non-empty string")

    missing_keys = [k for k in ("model", "width", "height") if k not in config]
    if missing_keys:
        raise RuntimeError(
            f"config is missing required keys: {missing_keys}"
        )

    # --- Build submit request ---
    endpoint = f"{base_url.rstrip('/')}/v1/videos"
    payload = {
        "model": config["model"],
        "prompt": prompt,
        "image": image,
        "width": config["width"],
        "height": config["height"],
        "num_frames": config.get("num_frames", 0),
        "frame_rate": config.get("frame_rate", 0),
    }
    if "negative_prompt" in config:
        payload["negative_prompt"] = config["negative_prompt"]

    submit_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # --- Submit phase ---
    try:
        submit_resp = requests.post(
            endpoint, headers=submit_headers, json=payload, timeout=500
        )
        submit_resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        # Include response body for debugging
        error_body = ""
        if hasattr(exc.response, 'text'):
            error_body = exc.response.text[:500]
        raise RuntimeError(f"Agnes Video API request failed: {exc}. Response: {error_body}") from exc

    # --- Parse submit response ---
    try:
        submit_data = submit_resp.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Agnes Video API returned non-JSON response: {exc}"
        ) from exc

    video_id = submit_data.get("video_id", "") or submit_data.get("id", "")
    if not video_id:
        raise RuntimeError(
            "Agnes Video API submit response missing video_id"
        )

    # --- Poll phase ---
    status_url = f"{base_url.rstrip('/')}/agnesapi?video_id={video_id}"
    poll_headers = {
        "Authorization": f"Bearer {api_key}",
    }
    max_poll_attempts = 120
    poll_interval = 10
    video_download_url = ""
    poll_attempt = 0

    for poll_attempt in range(max_poll_attempts):
        time.sleep(poll_interval)
        try:
            status_resp = requests.get(
                status_url, headers=poll_headers, timeout=500
            )
            status_resp.raise_for_status()
        except requests.exceptions.RequestException:
            if poll_attempt >= max_poll_attempts - 1:
                raise RuntimeError(
                    f"Polling timed out after {max_poll_attempts} attempts"
                )
            continue

        try:
            status_data = status_resp.json()
        except ValueError as exc:
            if poll_attempt >= max_poll_attempts - 1:
                raise RuntimeError(
                    f"Agnes Video API poll returned non-JSON response: {exc}"
                ) from exc
            continue

        vid_status = status_data.get("status", "")
        if vid_status == "completed":
            video_download_url = (
                status_data.get("url", "")
                or status_data.get("video_url", "")
            )
            break
        elif vid_status in ("failed", "error", "cancelled"):
            raise RuntimeError(
                f"Video generation failed with status: {vid_status}"
            )

    if not video_download_url:
        if poll_attempt >= max_poll_attempts - 1 and not video_download_url:
            raise RuntimeError(
                f"Polling timed out after {max_poll_attempts} attempts"
            )
        raise RuntimeError(
            "Agnes Video API completed response missing video URL"
        )

    return {"video_url": video_download_url}
