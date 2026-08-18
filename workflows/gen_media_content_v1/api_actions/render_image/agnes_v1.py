"""Agnes Image 2.1 Flash provider for render_image step.

Calls the Agnes Image API to generate images from text prompts.
"""
from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)


def call_api(
    prompt: str,
    config: dict,
    api_key: str,
    base_url: str,
) -> dict:
    """Generate an image using Agnes Image 2.1 Flash API.

    Parameters
    ----------
    prompt : str
        Text-to-image prompt.
    config : dict
        Provider config from api.agnes_v1 section (model, size, ratio).
    api_key : str
        Agnes API key.
    base_url : str
        Agnes API base URL.

    Returns
    -------
    dict
        {"image_url": str} on success.

    Raises
    ------
    RuntimeError
        If API call fails or no image URL in response.
    """
    model = config.get("model", "agnes-image-2.1-flash")
    size = config.get("size", "1K")
    ratio = config.get("ratio", "")

    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
    }
    if ratio:
        payload["ratio"] = ratio

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    endpoint = f"{base_url.rstrip('/')}/v1/images/generations"
    logger.info("Calling Agnes Image API: %s with model=%s, size=%s", endpoint, model, size)

    resp = requests.post(endpoint, headers=headers, json=payload, timeout=500)
    resp.raise_for_status()

    resp_data = resp.json()
    data_array = resp_data.get("data", [])

    if not data_array:
        raise RuntimeError("No image data in API response")

    image_url = data_array[0].get("url", "")
    if not image_url:
        raise RuntimeError("No image URL in API response")

    logger.info("Image generated: %s", image_url[:80] + "..." if len(image_url) > 80 else image_url)
    return {"image_url": image_url}
