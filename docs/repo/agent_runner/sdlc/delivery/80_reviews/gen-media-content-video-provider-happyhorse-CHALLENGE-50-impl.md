---
template_id: "SYS-03-CR"
version: "1.0.0"
doc_type: "review_artifact"
lifecycle_status: "draft"
---

# Challenge: Implementation Plan

## Summary
- Total attacks: 8
- BLOCKING: 1
- MAJOR: 4
- MINOR: 3

## Attack 1: Missing HTTP Error Handling During Polling Phase

**Target:** Section 6a (provider module implementation), poll phase error handling

**Scenario:** The implementation plan describes catching `RequestException` during poll GET requests and continuing to the next attempt unless it is the final attempt. However, the actual code path when `raise_for_status()` is called on a failed HTTP response (e.g., 500, 503) will raise `HTTPError` (a subclass of RequestException), which is caught. The plan states that on the final attempt it should raise RuntimeError, but there's no logic to distinguish between HTTP errors and network errors.

**Failure:** When the poll endpoint returns HTTP 500 or 503, the error is swallowed for attempts 0-118, and on attempt 119 a generic RuntimeError is raised without the actual HTTP status code or error response body. This makes debugging production failures impossible because the actual API error message is lost.

**Evidence:** Reference implementation in `workflows/agnes_gen_video_v1/impls/happyhorse_v1_1/actions.py` lines 195-198 show the same pattern where RequestException is caught and silently continued, losing error details.

**Severity:** MAJOR

## Attack 2: No Test for HTTP Errors During Poll Phase

**Target:** ACT-13 and ACT-14 (HTTP and Connection error tests), poll phase coverage

**Scenario:** ACT-13 and ACT-14 test HTTP errors and ConnectionError during the submit phase, but there are no corresponding tests for HTTP errors during the poll phase. The plan describes catching RequestException during polling (line 237 in Section 6a), but no test verifies this behavior.

**Failure:** If the implementation fails to properly handle HTTP errors during polling (e.g., by not catching them or by raising the wrong exception type), the tests would still pass. The gap means the polling error handling logic is unverified.

**Evidence:** Test list in Section 6b shows tests for submit-phase errors (ACT-13, ACT-14) but no tests for poll-phase HTTP errors, ConnectionError, or Timeout during polling.

**Severity:** MAJOR

## Attack 3: Missing JSON Decode Error Handling

**Target:** Section 6a, submit response parsing and poll response parsing

**Scenario:** The plan calls for calling `response.json()` on both submit and poll responses without any try/except block for `json.JSONDecodeError`. In the reference implementation (`agnes_v1/__init__.py` lines 74-79), JSON decode errors are explicitly caught and converted to RuntimeError with a descriptive message.

**Failure:** If the API returns malformed JSON (e.g., due to a partial response or proxy error), the implementation will raise `json.JSONDecodeError` instead of `RuntimeError`, breaking the error handling contract expected by callers. This is a regression from the agnes_v1 pattern that the plan claims to follow.

**Evidence:** Compare `agnes_v1/__init__.py` lines 74-79 with Section 6a which has no corresponding JSON error handling in the "Parse submit response" or poll response sections.

**Severity:** MAJOR

## Attack 4: No Test for JSON Decode Errors

**Target:** Test module (Section 6b, test list)

**Scenario:** The test_image_provider_agnes_v1.py includes `test_json_decode_error_raises_runtime_error` which verifies that JSON decode errors are converted to RuntimeError. The IMPL test list (16 tests) has no corresponding test for JSON decode errors.

**Failure:** Without this test, the implementation could omit JSON error handling entirely and still pass all 16 tests. This creates a blind spot where malformed API responses cause unhandled exceptions instead of graceful failures.

**Evidence:** `test_image_provider_agnes_v1.py` lines 144-165 shows the JSON decode error test pattern that is missing from the IMPL test plan (Section 6b, lines 252-268).

**Severity:** MINOR

## Attack 5: Poll Loop Off-By-One Logic Error

**Target:** Section 6a, poll loop implementation

**Scenario:** The plan describes "for attempt in range(120)" and "if final attempt, raise RuntimeError". However, range(120) produces attempts 0-119. The check "if final attempt" would need to be "attempt == 119", but the logic described uses "continue polling (if final attempt, raise RuntimeError)" which is ambiguous.

**Failure:** The actual implementation in `workflows/agnes_gen_video_v1/impls/happyhorse_v1_1/actions.py` lines 176-198 shows `for poll_attempt in range(max_poll_attempts):` followed by `if poll_attempt >= max_poll_attempts - 1:` on line 196. If the IMPL follows this pattern, on attempt 119 (the last iteration), when a RequestException occurs, it raises RuntimeError. But if the task stays PENDING for all 120 attempts, the loop exits without raising an error, and the code continues to the "no video_url after loop" check.

**Evidence:** The reference implementation shows this pattern where the loop exit does not inherently raise an error - only the explicit check after the loop raises. But the IMPL plan (line 240) says "If no video_url after loop, raise RuntimeError" which adds an extra condition check that may not be reached if the logic flow is wrong.

**Severity:** MINOR

## Attack 6: No Validation of Image Parameter Format

**Target:** Section 6a, input validation section

**Scenario:** The plan validates base_url and config keys but does not validate the `image` parameter. The TASK specification says image should be "sent as URL string, not base64", but the implementation doesn't validate this.

**Failure:** If a caller passes base64-encoded image data (perhaps mistakenly copied from the reference implementation in actions.py line 125), the implementation will silently pass it to the API, causing an API error that only manifests after the async job fails. This wastes API quota and delays error detection.

**Evidence:** Section 6a "Input validation section" only checks base_url and config keys. There's no validation that image is a valid URL string or that it doesn't start with "data:image" (base64).

**Severity:** MINOR

## Attack 7: Incomplete Header Validation in Tests

**Target:** ACT-20 and ACT-21, header validation tests

**Scenario:** ACT-20 claims to test "Correct submit headers (Authorization Bearer + Content-Type + X-DashScope-Async)" and ACT-21 claims to test "Correct poll headers (Authorization Bearer only)". However, looking at test_correct_headers in Section 7 (lines 629-658), it only verifies that Authorization header equals "Bearer {api_key}" but does not verify:
1. That submit headers DON'T contain unexpected keys
2. That the Authorization format is strictly "Bearer " + api_key (could be missing space or wrong casing)
3. That poll headers truly ONLY contain Authorization (could leak other headers)

**Failure:** The test would pass even if the implementation accidentally included the Content-Type header in poll requests or formatted the Authorization header incorrectly (e.g., "bearer " lowercase or missing the space).

**Evidence:** Test implementation in Section 7 lines 648-658 only checks positive presence of expected headers, not absence of forbidden headers or strict format compliance.

**Severity:** MAJOR

## Attack 8: Non-Existent Reference File Claimed

**Target:** Section 5 "Codebase Files Referenced (read-only)"

**Scenario:** The IMPL claims that `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py` EXISTS and is a "Phase 4 provider -- follow same error handling pattern". However, this file does not exist on disk.

**Failure:** The plan makes claims about following patterns from agnes_v2, but since the file doesn't exist, implementers cannot verify the pattern. This creates ambiguity about expected behavior and may lead to incorrect assumptions. The "Scope Assessment" (lines 90-93) claims "All work described in TASK-20260815-001-05 is NEW" which contradicts the claim that agnes_v2 exists as a reference.

**Evidence:** glob of `workflows/gen_media_content_v1/api_actions/render_video/**` returns only `__init__.py`, confirming no agnes_v2 directory exists.

**Severity:** BLOCKING
