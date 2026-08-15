---
template_id: "SYS-03-CR"
version: "1.0.0"
doc_type: "review_artifact"
lifecycle_status: "draft"
---

# Challenge: Implementation Plan

## Summary

- Total attacks: 7
- BLOCKING: 1
- MAJOR: 3
- MINOR: 3

---

## Attack 1: Test Timeout Parameter Not Actually Verified

**Target:** ACT-04 test `test_timeout_handling` in test_actions.py (lines 464-476 of IMPL)

**Scenario:** The test mocks `requests.get` to raise `Timeout` and verifies that `_api_request_with_retry` eventually raises `RuntimeError`. However, it never verifies that the `timeout` parameter is actually passed to the underlying `requests.get()` call.

**Failure:** The test would pass even if the implementation completely ignored the `timeout` parameter and used a hardcoded value. The test only verifies retry behavior, not that the timeout configuration is respected. This is a trivial test that does not verify the actual acceptance criterion.

**Evidence:**
- Test code at lines 464-476 mocks `requests.get` with `side_effect` but never asserts on call arguments
- The implementation at line 259 of IMPL lists `timeout=500` as a parameter
- The reference implementation at `workflows/agnes_media_gen_v1/actions.py` lines 42-44 shows timeout is passed to requests

**Severity:** MAJOR

---

## Attack 2: HTTP 400 Retry Logic Contradicts TASK Specification

**Target:** STEP-03: Implement _api_request_with_retry (lines 190-194 of IMPL)

**Scenario:** The TASK specification (lines 45-51) states: "Retry on HTTP 503, 429, and timeout errors." The IMPL states (lines 153, 258) that the function "retries only on HTTP 503 and 429 (not 400 as in the reference)."

**Failure:** The IMPL acknowledges it is deviating from the reference implementation pattern, but this deviation is NOT because the TASK excluded 400 - the TASK never mentioned 400 at all. However, the reference implementation at `workflows/agnes_media_gen_v1/actions.py` line 46 shows retry on 400: `if resp.status_code in (503, 429, 400):`. The IMPL correctly identified this deviation but the test at lines 396-417 of IMPL's test code does not test 400 behavior at all - it only tests 503 and 429.

**Evidence:**
- TASK lines 45-51: "Retry on HTTP 503, 429, and timeout errors" - 400 is not mentioned
- Reference `workflows/agnes_media_gen_v1/actions.py` line 46: retries on 400
- IMPL line 153 notes: "retries only on HTTP 503 and 429 (not 400 as in the reference)"
- ACT-04 verification method (lines 57-58) only mentions 503, 429, and timeout - no mention of 400

The IMPL has a silent breaking change from the reference pattern. If any caller expects 400 retry behavior (based on using the reference pattern), their code will break.

**Severity:** MAJOR

---

## Attack 3: Trivial Test for JSON Structure

**Target:** ACT-05 test `test_correct_json_structure` (lines 504-515 of IMPL)

**Scenario:** The test writes an index file, reads it back, and asserts on structure. However, it uses a hardcoded `tmp_path` provided by pytest which is guaranteed to be writable and empty.

**Failure:** The test does not verify that the function handles:
1. Existing files being overwritten
2. Invalid paths (parent directory is a file, not a directory)
3. Permission errors when writing

The acceptance criterion AC-05 requires "valid JSON" but the test only checks structure, not JSON validity (e.g., what if the function writes malformed JSON when `file_mappings` contains non-serializable objects?).

**Evidence:**
- Test at lines 504-515 uses `json.load(f)` which would raise if JSON is invalid, but doesn't test edge cases
- No test for `file_mappings` containing non-JSON-serializable types (e.g., datetime objects, custom classes)
- No test for file permissions or read-only filesystems

**Severity:** MINOR

---

## Attack 4: Sequence Filename Format Inconsistency at Scale

**Target:** STEP-05: Implement _get_next_sequence_filename (lines 202-206 of IMPL)

**Scenario:** The reference implementation at `workflows/agnes_media_gen_v1/actions.py` lines 78-91 shows:
```python
if seq > 9999:
    return f"{base_name}_{seq:04d}.{ext}"
```

**Failure:** The IMPL test only covers up to `base_002.ext` (lines 547-553), but the reference changes formatting at 10000 files from `_{seq:03d}` to `_{seq:04d}`. This means:
- `base_999.ext` (3 digits with leading zeros)
- `base_10000.ext` (5 digits, no leading zeros implied)

The IMPL does not document or test this format change boundary. If a caller expects consistent filename patterns for sorting or parsing, this will break at 10000 files.

**Evidence:**
- Reference `workflows/agnes_media_gen_v1/actions.py` lines 90-91: format change at seq > 9999
- IMPL test at lines 547-553 only tests up to `_002`
- IMPL line 260 describes function but does not mention the 9999 boundary

**Severity:** MINOR

---

## Attack 5: Missing ImportError Context in import_provider

**Target:** STEP-06: Implement import_provider (lines 208-212 of IMPL)

**Scenario:** The function must "Raise ImportError if the module does not exist or has no call_api" (TASK line 66). The test at lines 585-604 checks for ImportError but doesn't verify the error message provides useful context.

**Failure:** If import_provider raises a generic `ImportError` without indicating WHICH provider failed, debugging will be difficult. The test at line 590 checks `with pytest.raises(ImportError)` but does not check `match="provider_name"` or similar context.

**Evidence:**
- TASK line 66: "Raise ImportError if the module does not exist or has no call_api"
- Test at lines 585-590: `with pytest.raises(ImportError)` - no match parameter
- Test at lines 592-604: `with pytest.raises(ImportError, match="call_api")` - only checks for call_api in message, not provider name

If a workflow uses multiple providers and one fails, the error won't indicate which one.

**Severity:** MINOR

---

## Attack 6: Test File Path Fragility via parents[3]

**Target:** test_actions.py lines 321-323 (IMPL lines 321-323)

**Scenario:** The test file calculates `PROJECT_ROOT` using `Path(__file__).resolve().parents[3]` to find the config.json.sample file.

**Failure:** This assumes a fixed directory depth from test file to project root:
- `workflows/gen_media_content_v1/tests/test_actions.py` (depth 3 should reach project root)
- If the file is moved or the directory structure changes, this breaks

More critically, the test at lines 362-369 only runs if `sample_path.exists()` (conditional test). If the path calculation is wrong, the test silently skips instead of failing.

**Evidence:**
- Line 321: `PROJECT_ROOT = Path(__file__).resolve().parents[3]`
- Lines 364-365: `if sample_path.exists():` - conditional execution hides path errors

**Severity:** MAJOR

---

## Attack 7: Mock Provider Test Doesn't Match Real Provider Structure

**Target:** ACT-07 test `test_successful_import` (lines 568-584 of IMPL)

**Scenario:** The test creates a mock provider module by writing Python code to an `__init__.py` file and then imports it.

**Failure:** The test writes the mock module as:
```python
def call_api(prompt, image, config, api_key, base_url):
    return {'status': 'ok'}
```

But the actual provider modules in `workflows/gen_media_content_v1/api_actions/render_image/__init__.py` indicate providers are subMODULES (directories with `__init__.py`), not just functions in `__init__.py`. The test structure doesn't match the real structure where providers have their own directories.

**Evidence:**
- Test lines 571-577: creates `provider_dir / "__init__.py"` with function definition
- Real structure: `api_actions/render_image/` contains provider subdirectories (implied by comments in `__init__.py`)
- The reference `workflows/agnes_media_gen_v1/impls/` shows provider implementations as full modules

If `import_provider` expects to import from `api_actions.render_image.{provider_name}` as a submodule, but the test mocks it as just an `__init__.py` with a function, the test may pass while real usage fails.

**Severity:** BLOCKING

---

## Compliance Summary

| Check | Status |
|-------|--------|
| All 5 attack areas checked | PASS |
| Every attack includes specific evidence | PASS |
| Severity ratings justified | PASS |
| At least 5 attacks documented | PASS (7 attacks) |
| No metadata/formatting attacks | PASS |
