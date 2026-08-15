"""Agnes v1 image rendering provider.

Pure call_api() function that generates images from text prompts
using the Agnes Image API (v1/images/generations endpoint).

Signature follows TASK-20260815-001-03 Step 1a:
    call_api(prompt, config, api_key, base_url) -> dict

Note: The registry docstring at render_image/__init__.py mentions an
``image`` parameter. That signature applies to video providers (image-to-video).
For text-to-image generation, no input image is required.
"""
from __future__ import annotations

import requests


def call_api(prompt: str, config: dict, api_key: str, base_url: str) -> dict:
    """Generate an image from a text prompt using the Agnes Image API.

    Parameters
    ----------
    prompt : str
        Text description of the image to generate.
    config : dict
        Provider configuration with keys: model, size, ratio.
    api_key : str
        Bearer token for API authentication.
    base_url : str
        Base URL of the Agnes API (e.g., "https://apihub.agnes-ai.com").

    Returns
    -------
    dict
        {"image_url": "<url>", "revised_prompt": "<prompt>"}

    Raises
    ------
    RuntimeError
        If input validation fails, HTTP request fails, response is not
        valid JSON, or response contains no image URL.
    """
    # --- Input validation ---
    if not base_url or not base_url.strip():
        raise RuntimeError("base_url must be a non-empty string")

    missing_keys = [k for k in ("model", "size") if k not in config]
    if missing_keys:
        raise RuntimeError(
            f"config is missing required keys: {missing_keys}"
        )

    # --- Build request ---
    endpoint = f"{base_url.rstrip('/')}/v1/images/generations"
    payload = {
        "model": config["model"],
        "prompt": prompt,
        "size": config["size"],
        "ratio": config.get("ratio", ""),
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # --- Execute request with unified error handling ---
    try:
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=500)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Agnes Image API request failed: {exc}") from exc

    # --- Parse response ---
    try:
        resp_data = resp.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Agnes Image API returned non-JSON response: {exc}"
        ) from exc

    data = resp_data.get("data", [])
    image_url = data[0].get("url", "") if data else ""

    if not image_url:
        raise RuntimeError(
            "Agnes Image API response contains no image URL"
        )

    return {"image_url": image_url, "revised_prompt": prompt}
