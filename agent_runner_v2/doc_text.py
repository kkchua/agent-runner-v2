"""Text processing utilities for documentation generation.

Provides shared functions for sanitizing and formatting text content
in generated documentation files (.md).
"""
from __future__ import annotations

from .tools.agent_tools import sanitize_ascii

__all__ = ["sanitize_ascii"]
