# Challenge Document: EXEC-20260815-001-005

## Execution Record Under Review

**Document:** EXEC-20260815-001-005_gen-media-content-llm-prompts.md
**Scope:** Challenge the execution record for gen_media_content_v1 Phase 7 LLM Prompts
**Challenge Date:** 2026-08-15
**Challenger:** Adversary Review Agent

---

## Attack 1: Incomplete Absolute Path Detection Regex

**Category:** TEST ACCURACY
**Severity:** MAJOR

### Claim Challenged
The EXEC record (lines 87, 226) claims that ACT-07 test "test_extract_desc_no_absolute_paths + test_generate_prompts_no_absolute_paths PASSED" sufficiently verifies no hardcoded absolute paths exist.

### Evidence
The test file at `workflows/gen_media_content_v1/tests/test_prompt_slots.py` lines 21-26 defines:

```python
_ABS_PATH_PATTERN = re.compile(
    r"(?:[A-Z]:[/\\])"        # Windows drive letter paths (C:\, D:/)
    r"|(?:/(?:home|usr|etc|tmp|var|opt)/)"  # Unix absolute paths
    r"|(?:^/[^{])",            # Root-relative paths not starting with {
    re.MULTILINE,
)
```

This regex has the following gaps:
1. **Missing `/root/` pattern**: Common absolute path for root user home directory
2. **Missing `/bin/`, `/sbin/`, `/lib/` patterns**: System directory paths
3. **Missing Windows UNC paths**: `\\server\share\path` format not caught
4. **Missing bare `/` paths**: A path like `/absolute/path` starting with `/` but not matching the specific Unix directories listed would not be detected

### Failure Scenario
A developer could inadvertently include an absolute path like `/root/project/file.txt` or `\\server\share\data` in a prompt template, and the test would pass despite the hardcoded path being present. This undermines AC-07's intent of ensuring portability across systems.

### Recommended Fix
Expand the regex to include:
```python
_ABS_PATH_PATTERN = re.compile(
    r"(?:[A-Z]:[/\\])"                    # Windows drive letter paths
    r"|(?:\\\\[^\\]+\\[^\\]+)"          # Windows UNC paths (\\server\share)
    r"|(?:/(?:home|usr|etc|tmp|var|opt|root|bin|sbin|lib|lib64)/)"  # Unix paths
    r"|(?:^/(?!\{))",                      # Any root-relative path not starting with {
    re.MULTILINE,
)
```

---

## Attack 2: Baseline Test Count Inaccuracy

**Category:** DOCUMENTATION
**Severity:** MINOR

### Claim Challenged
The EXEC record line 32 states: "Result: 108 passed, 1 failed (pre-existing failure in test_bundle_loader.py)"

### Evidence
Running the baseline test command `.venv\Scripts\python -m pytest tests/unit/ -x -q` on the current codebase yields:
```
117 passed, 1 failed
```

The baseline count of 108 passed tests is incorrect. The actual pre-implementation baseline was higher than reported. This discrepancy suggests either:
1. The EXEC record was generated from an outdated test run
2. Additional tests were added between the reported baseline and current state
3. The number was approximated without verification

### Failure Scenario
While this does not affect the implementation correctness, inaccurate baseline metrics reduce confidence in the execution record's accuracy and traceability. Future reviewers cannot rely on the documented baseline for comparison.

### Recommended Fix
Update the EXEC record to reflect the accurate baseline: "117 passed, 1 failed" or document why the baseline count differs.

---

## Attack 3: IMPL Test Count Inconsistency

**Category:** TRACEABILITY
**Severity:** MINOR

### Claim Challenged
The IMPL document (line 360) states: "This test module provides the following test functions (total 12 test methods across 9 test classes)"

### Evidence
The actual test file `workflows/gen_media_content_v1/tests/test_prompt_slots.py` contains:
- TestExtractDescExists: 2 tests
- TestGeneratePromptsExists: 2 tests  
- TestExtractDescStep00Dir: 1 test
- TestExtractDescStep01Dir: 1 test
- TestGeneratePromptsStepDirs: 2 tests
- TestGeneratePromptsMediaConfig: 1 test
- TestNoHardcodedPaths: 2 tests
- TestContentLength: 2 tests (supplementary)

**Total: 13 test methods, not 12.**

The table in IMPL lines 362-377 correctly lists 13 test entries, but the summary text at line 360 undercounts by one.

### Failure Scenario
Inconsistent counts between summary and detail create confusion about test coverage. Stakeholders reviewing the IMPL may believe one test is missing.

### Recommended Fix
Update line 360 in IMPL to read: "total 13 test methods across 8 test classes" (note: there are 8 test classes, not 9 as stated - TestExtractDescStep00Dir, TestExtractDescStep01Dir, TestGeneratePromptsStepDirs, TestGeneratePromptsMediaConfig, TestNoHardcodedPaths, TestContentLength, TestExtractDescExists, TestGeneratePromptsExists = 8 classes).

---

## Attack 4: Missing ASCII-Only Validation Test

**Category:** TEST ACCURACY
**Severity:** MAJOR

### Claim Challenged
The EXEC record (lines 206-212) documents that Unicode characters (arrows, em-dashes) were replaced with ASCII equivalents. Lines 114-116 claim: "Replaced Unicode arrow characters with ASCII equivalents (e.g., "->") to maintain ASCII-only output per project conventions."

### Evidence
There is **no test** in `test_prompt_slots.py` that validates ASCII-only content. The test file checks:
- File existence (ACT-01, ACT-02)
- UTF-8 validity (ACT-01, ACT-02)
- Placeholder presence (ACT-03 through ACT-06)
- Hardcoded paths (ACT-07)
- Content length (supplementary)

There is no test that:
- Verifies no Unicode arrow characters (U+2190, U+2191, U+2192, U+2193)
- Verifies no em-dashes (U+2014) or en-dashes (U+2013)
- Verifies no curly quotes (U+201C, U+201D, U+2018, U+2019)

The source file `step_2_generate/standard.txt` contains Unicode characters at:
- Line 32: Unicode down arrow (U+2193)
- Lines throughout: Unicode em-dashes (U+2014) in headers like "Variant Differentiation Through Photography"

The adapted file was changed, but there is no automated verification.

### Failure Scenario
Future modifications to the prompt files could reintroduce Unicode characters without detection. The project convention requiring ASCII-only output is not enforced by tests, relying solely on manual review.

### Recommended Fix
Add an ACT-10 test:
```python
class TestAsciiOnly:
    def test_extract_desc_ascii_only(self, extract_desc_content: str) -> None:
        # Check for common Unicode characters that should be avoided
        forbidden = ['\u2014', '\u2013', '\u201c', '\u201d', '\u2018', '\u2019', 
                     '\u2190', '\u2191', '\u2192', '\u2193', '\u2026']
        for char in forbidden:
            assert char not in extract_desc_content, (
                f"extract_desc contains forbidden Unicode character: U+{ord(char):04X}"
            )

    def test_generate_prompts_ascii_only(self, generate_prompts_content: str) -> None:
        forbidden = ['\u2014', '\u2013', '\u201c', '\u201d', '\u2018', '\u2019', 
                     '\u2190', '\u2191', '\u2192', '\u2193', '\u2026']
        for char in forbidden:
            assert char not in generate_prompts_content, (
                f"generate_prompts contains forbidden Unicode character: U+{ord(char):04X}"
            )
```

---

## Attack 5: Missing IMAGE_DESCRIPTIONS Placeholder Test

**Category:** COMPLETENESS
**Severity:** MINOR

### Claim Challenged
The EXEC record shows comprehensive placeholder coverage but omits testing for {IMAGE_DESCRIPTIONS} which is used in the extract_desc prompt.

### Evidence
The `extract_desc/standard.txt` file contains {IMAGE_DESCRIPTIONS} at:
- Line 138: "(this is the {IMAGE_DESCRIPTIONS} artifact)"
- Line 146: "- IMAGE_DESCRIPTIONS: the absolute path to the index.json file"
- Line 151: "The {IMAGE_DESCRIPTIONS} artifact is the index.json file"

The workflow.toml defines IMAGE_DESCRIPTIONS as an artifact (lines 48, 49, 56), and context_extensions.py (line 58) maps it to a path.

However, no test verifies the presence of {IMAGE_DESCRIPTIONS} in the extract_desc prompt.

### Failure Scenario
If the placeholder were accidentally removed or misspelled, the workflow would fail at runtime when attempting to report the artifact path. This would be discovered late in the execution cycle rather than during testing.

### Recommended Fix
Add to ACT-03 or create ACT-03b:
```python
class TestExtractDescImageDescriptions:
    def test_contains_image_descriptions(self, extract_desc_content: str) -> None:
        assert "{IMAGE_DESCRIPTIONS}" in extract_desc_content, (
            "extract_desc prompt missing {IMAGE_DESCRIPTIONS} placeholder"
        )
```

---

## Summary

| Attack | Category | Severity | Status |
|--------|----------|----------|--------|
| 1. Incomplete regex for absolute paths | TEST ACCURACY | MAJOR | **CONFIRMED** |
| 2. Baseline test count inaccuracy | DOCUMENTATION | MINOR | **CONFIRMED** |
| 3. IMPL test count inconsistency | TRACEABILITY | MINOR | **CONFIRMED** |
| 4. Missing ASCII-only validation | TEST ACCURACY | MAJOR | **CONFIRMED** |
| 5. Missing IMAGE_DESCRIPTIONS test | COMPLETENESS | MINOR | **CONFIRMED** |

**Total Attacks: 5**
- **BLOCKING: 0**
- **MAJOR: 2**
- **MINOR: 3**

## Notes

1. **Attack 1 (MAJOR)** is the most significant issue. The regex pattern is insufficient to catch all forms of absolute paths, which is the core requirement of ACT-07.

2. **Attack 4 (MAJOR)** documents a missing test for project conventions. While the adaptation was performed correctly (as verified by manual inspection), the lack of automated verification creates regression risk.

3. The implementation itself is functionally correct - all 13 tests pass, files were created as specified, and the adaptations from source were performed correctly. The attacks focus on test coverage gaps and documentation inaccuracies, not on fundamental implementation errors.

4. The pre-existing failure in test_bundle_loader.py is acknowledged in the EXEC record and is not a new regression introduced by this implementation.
