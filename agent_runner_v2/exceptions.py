#!/usr/bin/env python3
"""
exceptions.py — Custom exceptions for agent_runner_v2.

These replace the implicit error paths in v1 that relied on fallback recovery functions.
In v2, each failure has an explicit type so the runner can route it correctly.
"""
from __future__ import annotations


class PreflightBlockedError(Exception):
    """Raised when a preflight check blocks step execution (e.g. artifact status not approved)."""


class MetaJsonMissingError(Exception):
    """Raised when the coder did not write the expected meta.json sidecar after invocation.

    In v2 this is a hard failure — no recovery, no disk fallback.
    """


class MetaJsonInvalidError(Exception):
    """Raised when meta.json exists but fails schema validation.

    Includes a human-readable reason explaining exactly what is wrong.
    """


class ArtifactMissingError(Exception):
    """Raised when coder_result.artifacts references paths that don't exist on disk.

    Contains a list of missing paths for diagnostic output.
    """

    def __init__(self, message: str, missing: list[str]) -> None:
        super().__init__(message)
        self.missing = missing
