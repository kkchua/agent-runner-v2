"""Image rendering provider registry.

Provider modules are dynamically imported by name (e.g., agnes_v1).
Each provider must export a call_api(prompt, image, config, api_key, base_url) function.
"""
