"""__none__ skip provider for video rendering.

Returns a skip marker to bypass video generation entirely,
enabling image-only workflows. No side effects: no HTTP calls,
no file I/O, no exceptions.
"""
from __future__ import annotations


def call_api(
    prompt: str = "",
    image: str | None = None,
    config: dict | None = None,
    api_key: str = "",
    base_url: str = "",
) -> dict:
    """Return a skip marker indicating video generation is disabled.

    This provider performs no operations. It accepts any arguments
    (all optional with defaults) and returns immediately with a
    skip marker dict.

    Parameters
    ----------
    prompt : str
        Ignored. Present for interface compatibility.
    image : str or None
        Ignored. Present for interface compatibility.
    config : dict or None
        Ignored. Present for interface compatibility.
    api_key : str
        Ignored. Present for interface compatibility.
    base_url : str
        Ignored. Present for interface compatibility.

    Returns
    -------
    dict
        {"skipped": True, "reason": "Video generation disabled (__none__ provider)"}
    """
    return {
        "skipped": True,
        "reason": "Video generation disabled (__none__ provider)",
    }
