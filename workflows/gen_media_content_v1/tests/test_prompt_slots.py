"""Tests for gen_media_content_v1 LLM prompt slot placeholders.

Verifies that prompt templates exist, are valid UTF-8, contain required
slot placeholders, and do not contain hardcoded absolute paths.

Reference: TASK-20260815-001-07 Acceptance Criteria AC-01 through AC-09.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

# Resolve paths relative to the workflow package root
WORKFLOW_ROOT = Path(__file__).resolve().parent.parent
EXTRACT_DESC_PROMPT = WORKFLOW_ROOT / "prompts" / "extract_desc" / "standard.txt"
GENERATE_PROMPTS_PROMPT = WORKFLOW_ROOT / "prompts" / "generate_prompts" / "standard.txt"

# Pattern to detect hardcoded absolute paths
_ABS_PATH_PATTERN = re.compile(
    r"(?:[A-Z]:[/\\])"        # Windows drive letter paths (C:\, D:/)
    r"|(?:/(?:home|usr|etc|tmp|var|opt)/)"  # Unix absolute paths
    r"|(?:^/[^{])",            # Root-relative paths not starting with {
    re.MULTILINE,
)


@pytest.fixture
def extract_desc_content() -> str:
    """Read extract_desc prompt as UTF-8."""
    return EXTRACT_DESC_PROMPT.read_text(encoding="utf-8")


@pytest.fixture
def generate_prompts_content() -> str:
    """Read generate_prompts prompt as UTF-8."""
    return GENERATE_PROMPTS_PROMPT.read_text(encoding="utf-8")


# ACT-01: extract_desc prompt file exists and is valid UTF-8
class TestExtractDescExists:
    def test_file_exists(self) -> None:
        assert EXTRACT_DESC_PROMPT.exists(), (
            f"extract_desc prompt not found at {EXTRACT_DESC_PROMPT}"
        )

    def test_valid_utf8(self) -> None:
        # Reading with encoding="utf-8" will raise UnicodeDecodeError if invalid
        content = EXTRACT_DESC_PROMPT.read_text(encoding="utf-8")
        assert isinstance(content, str)
        assert len(content) > 0


# ACT-02: generate_prompts prompt file exists and is valid UTF-8
class TestGeneratePromptsExists:
    def test_file_exists(self) -> None:
        assert GENERATE_PROMPTS_PROMPT.exists(), (
            f"generate_prompts prompt not found at {GENERATE_PROMPTS_PROMPT}"
        )

    def test_valid_utf8(self) -> None:
        content = GENERATE_PROMPTS_PROMPT.read_text(encoding="utf-8")
        assert isinstance(content, str)
        assert len(content) > 0


# ACT-03: extract_desc contains {STEP_00_DIR} placeholder
class TestExtractDescStep00Dir:
    def test_contains_step_00_dir(self, extract_desc_content: str) -> None:
        assert "{STEP_00_DIR}" in extract_desc_content, (
            "extract_desc prompt missing {STEP_00_DIR} placeholder"
        )


# ACT-04: extract_desc contains {STEP_01_DIR} placeholder
class TestExtractDescStep01Dir:
    def test_contains_step_01_dir(self, extract_desc_content: str) -> None:
        assert "{STEP_01_DIR}" in extract_desc_content, (
            "extract_desc prompt missing {STEP_01_DIR} placeholder"
        )


# ACT-05: generate_prompts contains {STEP_01_DIR} and {STEP_02_DIR}
class TestGeneratePromptsStepDirs:
    def test_contains_step_01_dir(self, generate_prompts_content: str) -> None:
        assert "{STEP_01_DIR}" in generate_prompts_content, (
            "generate_prompts prompt missing {STEP_01_DIR} placeholder"
        )

    def test_contains_step_02_dir(self, generate_prompts_content: str) -> None:
        assert "{STEP_02_DIR}" in generate_prompts_content, (
            "generate_prompts prompt missing {STEP_02_DIR} placeholder"
        )


# ACT-06: generate_prompts contains {MEDIA_CONFIG}
class TestGeneratePromptsMediaConfig:
    def test_contains_media_config(self, generate_prompts_content: str) -> None:
        assert "{MEDIA_CONFIG}" in generate_prompts_content, (
            "generate_prompts prompt missing {MEDIA_CONFIG} placeholder"
        )


# ACT-07: No hardcoded absolute paths in either prompt
class TestNoHardcodedPaths:
    def test_extract_desc_no_absolute_paths(self, extract_desc_content: str) -> None:
        matches = _ABS_PATH_PATTERN.findall(extract_desc_content)
        assert not matches, (
            f"extract_desc prompt contains hardcoded absolute paths: {matches}"
        )

    def test_generate_prompts_no_absolute_paths(
        self, generate_prompts_content: str
    ) -> None:
        matches = _ABS_PATH_PATTERN.findall(generate_prompts_content)
        assert not matches, (
            f"generate_prompts prompt contains hardcoded absolute paths: {matches}"
        )


# Supplementary: Content length checks (>100 chars)
class TestContentLength:
    def test_extract_desc_meaningful_content(self, extract_desc_content: str) -> None:
        assert len(extract_desc_content) > 100, (
            "extract_desc prompt has less than 100 characters"
        )

    def test_generate_prompts_meaningful_content(
        self, generate_prompts_content: str
    ) -> None:
        assert len(generate_prompts_content) > 100, (
            "generate_prompts prompt has less than 100 characters"
        )
