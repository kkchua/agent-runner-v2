"""Round-robin API key pool for external API calls.

This module provides a reusable utility for rotating through multiple API keys
stored in environment variables. Useful for distributing load across multiple
API accounts or avoiding per-key rate limits.

Key naming convention:
    PREFIX_1, PREFIX_2, PREFIX_3, ... (numbered suffix, starts at 1)

Fallback:
    If no numbered keys found, falls back to bare PREFIX (single key).

Example:
    # .env file
    AGNES_API_KEY_1=sk-abc123...
    AGNES_API_KEY_2=sk-def456...
    AGNES_API_KEY_3=sk-ghi789...

    # In action
    from agent_runner_v2.api_key_pool import ApiKeyPool

    pool = ApiKeyPool("AGNES_API_KEY", project_root=project_root)
    api_key = pool.next_key()  # Returns key_1, then key_2, ..., key_N, then key_1
"""
from __future__ import annotations

import logging
import os
import re
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


def mask_api_key(key: str, show_last: int = 6) -> str:
    """Mask an API key for safe logging, showing only the last N characters.

    Args:
        key: The API key to mask.
        show_last: Number of trailing characters to reveal (default 6).

    Returns:
        Masked string like "****...abcd12" or "****" if key is too short.

    Example:
        >>> mask_api_key("sk-abc123def456ghi789")
        '****...i789'
        >>> mask_api_key("short")
        '****'
    """
    if not key or len(key) <= show_last:
        return "****"
    return f"****...{key[-show_last:]}"


def load_env_from_project(project_root: Path | str | None = None) -> None:
    """Load environment variables from .env file in project root.

    Searches for .env in the project_root directory. If not found, falls back
    to default dotenv behavior (searches current directory and parents).

    Args:
        project_root: Root path of the target repository. If None, uses
            current working directory.
    """
    from dotenv import load_dotenv

    root = Path(project_root) if project_root else Path.cwd()
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.debug("Loaded .env from %s", env_path)
    else:
        load_dotenv()
        logger.debug("Loaded .env from default location")


class ApiKeyPool:
    """Round-robin pool of API keys loaded from environment variables.

    Discovers all environment variables matching the pattern {PREFIX}_{N}
    where N is a positive integer (1, 2, 3, ...). Provides round-robin
    rotation through the discovered keys.

    If no numbered keys are found, falls back to the bare {PREFIX} environment
    variable (single key pool).

    Thread-safe: multiple threads can call next_key() concurrently.

    Attributes:
        prefix: The key prefix (e.g., "AGNES_API_KEY").
        keys: List of discovered keys in order.
    """

    def __init__(
        self,
        prefix: str,
        project_root: Path | str | None = None,
        *,
        load_env: bool = True,
    ) -> None:
        """Initialize the API key pool.

        Args:
            prefix: The environment variable prefix (e.g., "AGNES_API_KEY").
                Will discover {PREFIX}_1, {PREFIX}_2, etc.
            project_root: Root path containing .env file. If None, uses cwd.
            load_env: If True, load .env file before discovering keys.
                Set to False if .env is already loaded.
        """
        self.prefix = prefix

        if load_env:
            load_env_from_project(project_root)

        self.keys = self._discover_keys()
        self._counter = 0
        self._lock = threading.Lock()

        if not self.keys:
            logger.warning(
                "No API keys found for prefix '%s' (checked %s_N and %s)",
                prefix,
                prefix,
                prefix,
            )
        else:
            logger.info(
                "ApiKeyPool('%s'): discovered %d key(s)",
                prefix,
                len(self.keys),
            )

    def _discover_keys(self) -> list[str]:
        """Discover API keys from environment variables.

        Searches for {PREFIX}_1, {PREFIX}_2, ... (numbered keys).
        Falls back to bare {PREFIX} if no numbered keys found.

        Returns:
            List of non-empty key values in order.
        """
        numbered_keys = []
        pattern = re.compile(rf"^{re.escape(self.prefix)}_(\d+)$")

        # Scan environment for matching keys
        for env_var, value in os.environ.items():
            match = pattern.match(env_var)
            if match and value:
                index = int(match.group(1))
                numbered_keys.append((index, value))

        # Sort by index number
        numbered_keys.sort(key=lambda x: x[0])

        if numbered_keys:
            return [key for _, key in numbered_keys]

        # Fallback: check for bare prefix
        bare_key = os.environ.get(self.prefix, "")
        if bare_key:
            return [bare_key]

        return []

    def next_key(self) -> str:
        """Get the next API key in round-robin order.

        Returns:
            The next API key string. Returns empty string if no keys available.

        Example:
            pool = ApiKeyPool("AGNES_API_KEY")
            key1 = pool.next_key()  # First key
            key2 = pool.next_key()  # Second key
            key3 = pool.next_key()  # Third key (or first if only 3 keys)
        """
        if not self.keys:
            return ""

        with self._lock:
            key = self.keys[self._counter % len(self.keys)]
            self._counter += 1
            return key

    def current_index(self) -> int:
        """Get the index (0-based) of the last returned key.

        Returns:
            The index of the most recently returned key, or -1 if no keys.
        """
        if not self.keys:
            return -1
        return (self._counter - 1) % len(self.keys)

    def __len__(self) -> int:
        """Return the number of keys in the pool."""
        return len(self.keys)

    def __repr__(self) -> str:
        """Return a string representation of the pool."""
        return (
            f"ApiKeyPool(prefix={self.prefix!r}, "
            f"keys={len(self.keys)}, "
            f"next_index={self._counter % len(self.keys) if self.keys else 0})"
        )
