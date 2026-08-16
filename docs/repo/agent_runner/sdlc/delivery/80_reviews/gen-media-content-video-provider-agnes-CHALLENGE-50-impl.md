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

## Attack 1: Missing Test for "cancelled" Status
**Target:** ACT-03, ACT-04 and TASK AC-05
**Scenario:** The TASK specification (AC-05) explicitly states that poll returns "failed/error/cancelled" status must raise RuntimeError. The IMPL only provides tests for "failed" (ACT-03) and "error" (ACT-04), completely omitting "cancelled".
**Failure:** When the API returns status="cancelled", the implementation may or may not raise RuntimeError - there is no test verifying this behavior. If the implementation fails to handle "cancelled", the acceptance criterion AC-05 is not met.
**Evidence:**
- TASK AC-05: "call_api() raises RuntimeError when poll returns failed/error/cancelled status"
- IMPL ACT-03: tests "failed" status only
- IMPL ACT-04: tests "error" status only
- No ACT-XX tests "cancelled" status
**Severity:** BLOCKING

## Attack 2: Missing Test for HTTP Errors During Polling
**Target:** Poll error handling (Open Questions section)
**Scenario:** The IMPL Open Questions section states "HTTP errors during polling are handled gracefully (the poll loop continues on request exceptions, only timing out after max attempts)". However, there is NO corresponding acceptance criteria test for this behavior.
**Failure:** ACT-16 tests timeout when poll always returns "processing", but does NOT test when polls raise HTTPError, ConnectionError, or Timeout. If the implementation incorrectly propagates these exceptions instead of continuing the poll loop, the behavior would not match the specification.
**Evidence:**
- Open Questions section line 845: "HTTP errors during polling are handled gracefully"
- ACT-05, ACT-06, ACT-07: Only test HTTP errors during SUBMIT phase, not POLL phase
- Reference code (actions.py lines 372-375): Has try/except around poll requests.get, but IMPL doesn't verify this in tests
**Severity:** MAJOR

## Attack 3: Fragile Payload Extraction Pattern in Tests
**Target:** ACT-08, ACT-09, ACT-10 test implementations
**Scenario:** The tests extract payload using `call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")`. This pattern is fragile and can cause AttributeError.
**Failure:** When `requests.post` is called with keyword arguments like `requests.post(url, json=payload)`, the `call_args` structure is: `call(url, json={...})`. In this case `call_args[1]` is the keyword args dict `{'json': {...}}`, but `call_kwargs[1]` (attempting to index the Call object) does not work as intended. If the implementation uses different calling conventions, the test will crash with AttributeError: 'call' object has no attribute 'get'.
**Evidence:**
- ACT-08 lines 479-480: `payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")`
- ACT-09 lines 522-524: Same pattern
- ACT-10 lines 554-556: Same pattern
- The pattern assumes `call_args[1]` is a dict when accessed via `call_kwargs[1]`, but `call_kwargs` is the Call object itself
**Severity:** MAJOR

## Attack 4: Missing Test for JSON Decode Error During Polling
**Target:** Poll response parsing
**Scenario:** The IMPL tests JSON decode errors during submit (implied by exception handling), but the poll phase also calls `status_resp.json()` (line 365 in reference code). If the poll returns invalid JSON, the code would crash with ValueError.
**Failure:** No test verifies that a non-JSON poll response raises RuntimeError. The reference code (actions.py) has a try/except around `status_resp.json()` but the IMPL doesn't specify or test this behavior for the poll phase.
**Evidence:**
- Reference code actions.py line 365: `status_data = status_resp.json()` is called without JSON validation
- ACT-05 tests HTTP errors, but not JSON decode errors
- No test for `json.JSONDecodeError` during polling
**Severity:** MAJOR

## Attack 5: Missing Trailing Slash Handling in base_url
**Target:** STEP-02, Section 6.1
**Scenario:** The IMPL doesn't specify that base_url should have trailing slashes stripped, unlike the reference image provider which uses `base_url.rstrip('/')`.
**Failure:** If base_url is provided as "https://apihub.agnes-ai.com/", the endpoint construction would produce "https://apihub.agnes-ai.com//v1/videos" (double slash), which the API may reject. The Phase 3 image provider handles this correctly.
**Evidence:**
- IMPL Section 6.1 line 177: `POST to {base_url}/v1/videos` - no rstrip mentioned
- agnes_v1/__init__.py line 54: Uses `base_url.rstrip('/')` to handle trailing slashes
- IMPL doesn't mention this edge case
**Severity:** MINOR

## Attack 6: No Test for Missing video_url in Completed Response
**Target:** Poll response handling
**Scenario:** The IMPL tests successful extraction of video_url but doesn't test the case where poll returns status="completed" but video_url is missing or empty.
**Failure:** If the API returns `{"status": "completed"}` without a URL field, the implementation may return `{"video_url": ""}` or crash. TASK AC-03 requires "video_url" on successful completion, implying it must have a valid value.
**Evidence:**
- ACT-01 tests successful case with URL present
- ACT-18 tests fallback from "url" to "video_url" key
- No test for when BOTH keys are missing in completed response
- Reference code actions.py line 377-378: Raises ValueError if no download URL after completion
**Severity:** MINOR

## Attack 7: Whitespace-Only base_url Not Tested
**Target:** ACT-14 input validation
**Scenario:** ACT-14 tests empty base_url ("") but not whitespace-only base_url ("   "). The reference implementation checks `not base_url.strip()` to catch both cases.
**Failure:** If base_url="   " (spaces), the implementation might pass validation and produce malformed URLs like "   /v1/videos". The test only covers the empty string case.
**Evidence:**
- ACT-14 line 670-671: Tests `base_url=""` only
- agnes_v1/__init__.py line 44: Uses `not base_url or not base_url.strip()` to catch both empty and whitespace-only
- IMPL doesn't specify which validation approach to use
**Severity:** MINOR
