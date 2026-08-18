"""Agnes Video V2.0 provider for render_video step.

Calls the Agnes Video API (image-to-video) with submit→poll→download pattern.
"""
from __future__ import annotations

import logging
import time

import requests

logger = logging.getLogger(__name__)


def call_api(
    prompt: str,
    image: str,
    config: dict,
    api_key: str,
    base_url: str,
) -> dict:
    """Generate a video using Agnes Video V2.0 API (image-to-video).

    Parameters
    ----------
    prompt : str
        Video generation prompt.
    image : str
        Image URL or base64 data URI for image-to-video.
    config : dict
        Provider config from api.agnes_v2 section (model, width, height, num_frames, frame_rate).
    api_key : str
        Agnes API key.
    base_url : str
        Agnes API base URL.

    Returns
    -------
    dict
        {"video_url": str} on success.

    Raises
    ------
    RuntimeError
        If API call fails, polling times out, or no video URL in response.
    """
    model = config.get("model", "agnes-video-v2.0")
    width = config.get("width", 1024)
    height = config.get("height", 576)
    num_frames = config.get("num_frames", 72)
    frame_rate = config.get("frame_rate", 24)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Step 1: Submit video generation task
    submit_endpoint = f"{base_url.rstrip('/')}/v1/videos"
    payload = {
        "model": model,
        "prompt": prompt,
        "image": image,
        "width": width,
        "height": height,
        "num_frames": num_frames,
        "frame_rate": frame_rate,
    }

    logger.info("Submitting video task to %s with model=%s, %dx%d, %d frames",
                submit_endpoint, model, width, height, num_frames)

    submit_resp = requests.post(submit_endpoint, headers=headers, json=payload, timeout=500)
    submit_resp.raise_for_status()
    submit_data = submit_resp.json()

    video_id = submit_data.get("video_id", "") or submit_data.get("id", "")
    if not video_id:
        raise RuntimeError(f"No video_id in submit response: {submit_data}")

    logger.info("Video task submitted, video_id: %s", video_id)

    # Step 2: Poll for completion
    status_endpoint = f"{base_url.rstrip('/')}/agnesapi"
    status_url = f"{status_endpoint}?video_id={video_id}"
    max_poll_attempts = 120
    poll_interval = 10

    video_download_url = ""
    for poll_attempt in range(max_poll_attempts):
        time.sleep(poll_interval)

        try:
            status_resp = requests.get(status_url, headers=headers, timeout=500)
            status_resp.raise_for_status()
            status_data = status_resp.json()
        except requests.exceptions.RequestException as exc:
            logger.warning("Poll attempt %d/%d failed: %s", poll_attempt + 1, max_poll_attempts, exc)
            continue

        vid_status = status_data.get("status", "")
        logger.debug("Poll %d/%d: status=%s", poll_attempt + 1, max_poll_attempts, vid_status)

        if vid_status == "completed":
            video_download_url = status_data.get("url", "") or status_data.get("video_url", "")
            break
        elif vid_status in ("failed", "error", "cancelled"):
            raise RuntimeError(f"Video generation failed with status: {vid_status}")

    if not video_download_url:
        raise RuntimeError(f"No download URL after {max_poll_attempts} poll attempts")

    logger.info("Video completed: %s", video_download_url[:80] + "..." if len(video_download_url) > 80 else video_download_url)
    return {"video_url": video_download_url}
