# Execution Challenge: EXEC-20260815-001-001

## Document Metadata

- Challenge ID: CHALLENGE-60-EXEC-001
- Target Execution: EXEC-20260815-001-001
- Source Implementation: IMPL-20260815-001-001
- Challenge Date: 2026-08-15
- Challenger Agent: adversary-qwen3.7-plus

---

## Summary

This document challenges the execution record EXEC-20260815-001-001 which claims successful implementation of gen_media_content_v1 Phase 2 root actions and shared utilities. Five specific attacks are documented below.

---

## Attack 1: Critical Line Number Documentation Errors

### Claim Challenged
The EXEC document provides specific line number ranges for all implemented functions in the "Implementation Traceability" section (lines 67-77) and "Code Changes Made" section (lines 79-109).

### Evidence
Comparing EXEC claims to actual code in `workflows/gen_media_content_v1/actions.py`:

| Function | EXEC Claimed Lines | Actual Lines | Discrepancy |
|----------|-------------------|--------------|-------------|
| `_load_config` | 31-50 | 28-50 | -3 lines (starts earlier) |
| `_api_request_with_retry` | 53-114 | 53-125 | +11 lines (longer) |
| `_write_index` | 117-138 | 128-146 | +11 lines offset |
| `_get_next_sequence_filename` | 141-175 | 149-180 | +8 lines offset |
| `import_provider` | 178-237 | 196-234 | +18 lines offset |
| Action stubs | 240-280 | 241-274 | -6 lines (shorter) |

### Failure Scenario
Line number references in documentation are used by maintainers and reviewers to locate specific functionality. Incorrect line numbers cause:
- Reviewers looking at wrong code sections
- Future diffs and patches targeting incorrect locations
- Traceability breakdown when comparing to IMPL specifications

### Severity
**MAJOR** - Documentation inaccuracy that impedes maintenance and review workflows.

### Fix Required
Update EXEC lines 67-77 and 79-109 with accurate line numbers from the actual implementation.

---

## Attack 2: Undocumented Function Omission

### Claim Challenged
The EXEC "Code Changes Made" section (lines 79-109) documents all functions implemented in actions.py but omits `_get_api_actions_dir()`.

### Evidence
The function `_get_api_actions_dir()` exists at lines 183-193 in `workflows/gen_media_content_v1/actions.py`:

```python
def _get_api_actions_dir():
    """Return the path to the api_actions directory for this workflow.

    Separated as a helper to enable test mocking.

    Returns
    -------
    Path
        Absolute path to the api_actions directory.
    """
    return Path(__file__).resolve().parent / "api_actions"
```

This function was explicitly mentioned in IMPL Section 9 Assumption 2: "A helper function `_get_api_actions_dir()` will be used internally to resolve the base path, enabling test mocking."

### Failure Scenario
The EXEC claims "Functions implemented:" followed by a numbered list (1-8), but there are actually 9 functions (the 8 listed plus `_get_api_actions_dir`). This incomplete documentation:
- Creates confusion about whether the function is part of the API
- Makes future refactoring risky (function could be removed as "unused")
- Breaks traceability from IMPL assumptions to implementation

### Severity
**MAJOR** - Incomplete documentation of implemented functions violates traceability requirements.

### Fix Required
Add `_get_api_actions_dir()` to the function list in EXEC Section "Code Changes Made" with description and line numbers.

---

## Attack 3: Logic Bug in _get_next_sequence_filename at 9999 Boundary

### Claim Challenged
The EXEC claims AC-06 is fully satisfied (line 238: "PASS - 5/5 tests pass") and that `_get_next_sequence_filename` correctly implements the format change at seq > 9999.

### Evidence
Examining the actual implementation at lines 149-180 of `workflows/gen_media_content_v1/actions.py`:

```python
def _get_next_sequence_filename(output_dir: Path, base_name: str, ext: str) -> str:
    ext = ext.lstrip(".")
    base_path = output_dir / f"{base_name}.{ext}"
    if not base_path.exists():
        return f"{base_name}.{ext}"
    seq = 1
    while True:
        candidate = output_dir / f"{base_name}_{seq:03d}.{ext}"
        if not candidate.exists():
            return f"{base_name}_{seq:03d}.{ext}"
        seq += 1
        if seq > 9999:
            return f"{base_name}_{seq:04d}.{ext}"
```

**BUG**: When `seq > 9999`, the function returns immediately with the 4-digit format WITHOUT checking if the file exists. This means:
- If files exist through `_10000`, the function would return `base_10001.ext` without verification
- If `_10001` also exists, the function returns an already-used filename
- The loop exit on line 179-180 bypasses the existence check on lines 175-177

The reference implementation (`workflows/agnes_media_gen_v1/actions.py` lines 84-91) has the same bug, so this is a faithful reproduction of buggy behavior rather than a deviation.

### Failure Scenario
In production use with high-volume media generation (over 10,000 files), the function would return duplicate filenames, causing:
- File overwrites and data loss
- Index corruption
- Workflow failures when expected files are missing or overwritten

### Severity
**BLOCKING** - Implementation contains a logic bug that will cause incorrect behavior at scale.

### Fix Required
Modify lines 179-180 to check file existence before returning:
```python
if seq > 9999:
    candidate = output_dir / f"{base_name}_{seq:04d}.{ext}"
    if not candidate.exists():
        return f"{base_name}_{seq:04d}.{ext}"
```

Add a test case that creates files up to `_10000` and verifies `_10001` is returned.

---

## Attack 4: Incomplete Test Coverage for Deviation 1

### Claim Challenged
The EXEC Deviation 1 documentation (lines 209-214) claims the fix "Changed `range(1, 1000)` to `range(1, 999)`" and justifies it as aligning test setup with expected output.

### Evidence
The actual test at `workflows/gen_media_content_v1/tests/test_actions.py` lines 285-297:

```python
def test_format_change_at_9999_boundary(self, tmp_path):
    # Create files up to _998 to simulate approaching the boundary
    (tmp_path / "image.png").touch()
    for i in range(1, 999):
        (tmp_path / f"image_{i:03d}.png").touch()
    # Next should be _999 (3-digit, since seq <= 9999)
    result = _get_next_sequence_filename(tmp_path, "image", "png")
    assert result == "image_999.png"
```

**ISSUE**: The test name claims to test "format_change_at_9999_boundary" but:
1. It only creates files up to `_998` (not even _999)
2. It tests the 3-digit format, NOT the format change to 4-digit
3. The actual 4-digit format code path (lines 179-180) is NEVER tested

The IMPL Section 4 (Challenge Resolution, Attack 4) explicitly states: "Added `test_format_change_at_9999_boundary` test to verify behavior near the boundary." However, the test does NOT verify the 4-digit format transition.

### Failure Scenario
The 4-digit format code path (which contains the bug in Attack 3) is never executed during tests. This means:
- The buggy code path is not covered
- Production failures at the 9999 boundary would not be caught in CI
- The test name misrepresents what it actually tests

### Severity
**MAJOR** - Test does not cover the functionality it claims to test; leaves production code path untested.

### Fix Required
Add a test that actually triggers the 4-digit format:
```python
def test_format_4_digit_at_10000(self, tmp_path):
    (tmp_path / "image.png").touch()
    for i in range(1, 10000):
        (tmp_path / f"image_{i:03d}.png").touch()
    result = _get_next_sequence_filename(tmp_path, "image", "png")
    assert result == "image_10000.png"  # 4-digit format
```

Update EXEC Deviation 1 to accurately describe what was actually implemented vs what was planned.

---

## Attack 5: IMPL Assumption Violation Not Documented

### Claim Challenged
The EXEC claims all acceptance criteria are satisfied (lines 229-243, "Open Questions: None"), but IMPL Section 9 Assumption 4 states: "The `file_mappings` argument to `_write_index` will contain only JSON-serializable data... Non-serializable objects... are the caller's responsibility to convert."

### Evidence
The `_write_index` function (actions.py lines 128-146):
```python
def _write_index(index_path, step_name, file_mappings):
    index_data = {"step": step_name, "files": file_mappings}
    index_path = Path(index_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
```

The function uses `json.dump()` without any error handling for non-serializable data. If `file_mappings` contains datetime objects, custom classes, or other non-serializable types, `json.dump()` will raise `TypeError`.

The IMPL acknowledged this limitation and added Assumption 4 to document it. However, the EXEC:
1. Does not document this limitation
2. Does not test the error case (what happens with non-serializable data)
3. Claims AC-05 passes without noting the assumption constraint

### Failure Scenario
If a caller passes non-serializable data (e.g., datetime objects in file_mappings), the function will raise TypeError at runtime. This is not:
- Documented in the function's behavior
- Tested to provide clear error messages
- Handled gracefully

### Severity
**MINOR** - Undocumented assumption that could cause runtime failures; missing defensive programming.

### Fix Required
Add to EXEC Section "Code Changes Made" under `_write_index`:
- Note that `file_mappings` must contain only JSON-serializable data
- Document that non-serializable objects will raise TypeError
- Optionally add error handling to provide a clearer error message

---

## Attack Summary

| Attack | Severity | Category | Status |
|--------|----------|----------|--------|
| Attack 1: Line Number Errors | MAJOR | Documentation | REJECTED |
| Attack 2: Undocumented Function | MAJOR | Completeness | REJECTED |
| Attack 3: Logic Bug at 9999 | BLOCKING | Correctness | REJECTED |
| Attack 4: Incomplete Test Coverage | MAJOR | Test Accuracy | REJECTED |
| Attack 5: Undocumented Assumption | MINOR | Documentation | REJECTED |

## Total by Severity

- **BLOCKING**: 1
- **MAJOR**: 3
- **MINOR**: 1

---

## Verification Commands Used

```bash
# Line number verification
# Read actions.py and compared line numbers to EXEC claims

# Test execution
.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_actions.py -v

# Import verification
.venv\Scripts\python -c "from workflows.gen_media_content_v1.actions import _load_config, _api_request_with_retry, _write_index, _get_next_sequence_filename, import_provider"

# Reference pattern comparison
# Read workflows/agnes_media_gen_v1/actions.py for comparison
```

---

## End of Challenge Document
