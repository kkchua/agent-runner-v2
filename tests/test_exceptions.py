"""Tests for agent_runner_v2.exceptions."""
from __future__ import annotations

import pytest

from agent_runner_v2.exceptions import (
    PreflightBlockedError,
    MetaJsonMissingError,
    MetaJsonInvalidError,
    ArtifactMissingError,
)


# ---------------------------------------------------------------------------
# PreflightBlockedError
# ---------------------------------------------------------------------------

class TestPreflightBlockedError:
    def test_is_exception(self):
        assert issubclass(PreflightBlockedError, Exception)

    def test_with_message(self):
        msg = "Preflight check failed: artifact not approved"
        exc = PreflightBlockedError(msg)
        assert str(exc) == msg

    def test_can_be_raised_and_caught(self):
        with pytest.raises(PreflightBlockedError):
            raise PreflightBlockedError("blocked")

    def test_can_catch_as_exception(self):
        """Can be caught as generic Exception."""
        with pytest.raises(Exception):
            raise PreflightBlockedError("blocked")


# ---------------------------------------------------------------------------
# MetaJsonMissingError
# ---------------------------------------------------------------------------

class TestMetaJsonMissingError:
    def test_is_exception(self):
        assert issubclass(MetaJsonMissingError, Exception)

    def test_with_message(self):
        msg = "meta.json not found after coder invocation"
        exc = MetaJsonMissingError(msg)
        assert str(exc) == msg

    def test_can_be_raised(self):
        with pytest.raises(MetaJsonMissingError):
            raise MetaJsonMissingError("missing")


# ---------------------------------------------------------------------------
# MetaJsonInvalidError
# ---------------------------------------------------------------------------

class TestMetaJsonInvalidError:
    def test_is_exception(self):
        assert issubclass(MetaJsonInvalidError, Exception)

    def test_with_message(self):
        msg = "meta.json has invalid schema: missing required field 'status'"
        exc = MetaJsonInvalidError(msg)
        assert str(exc) == msg

    def test_can_be_raised(self):
        with pytest.raises(MetaJsonInvalidError):
            raise MetaJsonInvalidError("invalid schema")


# ---------------------------------------------------------------------------
# ArtifactMissingError
# ---------------------------------------------------------------------------

class TestArtifactMissingError:
    def test_is_exception(self):
        assert issubclass(ArtifactMissingError, Exception)

    def test_with_message_and_missing(self):
        missing = ["/path/a.txt", "/path/b.txt"]
        exc = ArtifactMissingError("3 artifacts missing", missing)
        assert str(exc) == "3 artifacts missing"
        assert exc.missing == missing

    def test_missing_is_list(self):
        exc = ArtifactMissingError("oops", ["a", "b", "c"])
        assert isinstance(exc.missing, list)
        assert len(exc.missing) == 3

    def test_missing_can_be_empty(self):
        exc = ArtifactMissingError("no paths", [])
        assert exc.missing == []

    def test_can_be_raised(self):
        with pytest.raises(ArtifactMissingError) as exc_info:
            raise ArtifactMissingError("missing artifacts", ["/x", "/y"])
        assert exc_info.value.missing == ["/x", "/y"]

    def test_catch_as_exception(self):
        """Can be caught as generic Exception."""
        with pytest.raises(Exception):
            raise ArtifactMissingError("oops", [])
