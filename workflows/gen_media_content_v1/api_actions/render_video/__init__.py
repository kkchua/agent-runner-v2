"""Video rendering provider registry.

Provider modules are dynamically imported by name (e.g., agnes_v2, happyhorse_v1_1).
Each provider must export a call_api(prompt, image, config, api_key, base_url) function.
The special __none__ provider returns a skip marker to bypass video generation.
"""
