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
- MAJOR: 4
- MINOR: 2

## Attack 1: Function Signature Mismatch - BLOCKING

**Target:** STEP-01, call_api function signature

**Scenario:** The IMPL defines `call_api(prompt: str, config: dict, api_key: str, base_url: str)` but the registry docstring at `workflows/gen_media_content_v1/api_actions/render_image/__init__.py` (line 4) specifies the provider must export `call_api(prompt, image, config, api_key, base_url)` with 5 parameters including an `image` parameter.

**Failure:** The IMPL signature `(prompt, config, api_key, base_url)` has 4 parameters while the registry contract requires 5 parameters `(prompt, image, config, api_key, base_url)`. When `import_provider()` in `workflows/gen_media_content_v1/actions.py` (lines 196-234) attempts to validate and call the function, it will fail with a TypeError due to missing the `image` argument. This makes the provider incompatible with the existing import infrastructure.

**Evidence:**
- Registry docstring at `workflows/gen_media_content_v1/api_actions/render_image/__init__.py` line 4: "Each provider must export a call_api(prompt, image, config, api_key, base_url) function."
- IMPL STEP-01: `def call_api(prompt: str, config: dict, api_key: str, base_url: str) -> dict:`
- Reference implementation at `workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py` uses image-based workflow where the image parameter is used in video generation

**Severity:** BLOCKING

---

## Attack 2: Missing Required Config Key Validation - MAJOR

**Target:** STEP-01, payload construction

**Scenario:** The IMPL constructs payload using `config["model"]` and `config["size"]` without validating these keys exist. If the config dict is missing required keys, the function will raise KeyError instead of RuntimeError.

**Failure:** Per TASK AC-04 and AC-05, the function must raise RuntimeError on errors. However, if config is `{}` or missing "model" or "size" keys, Python will raise KeyError at line `config["model"]`, which is not a RuntimeError and violates the error handling contract.

**Evidence:**
- IMPL STEP-01: `payload = {"model": config["model"], "prompt": prompt, "size": config["size"], ...}`
- No validation checks for required config keys before access
- No test case for missing config keys in test plan

**Severity:** MAJOR

---

## Attack 3: Incomplete HTTP Exception Handling - MAJOR

**Target:** STEP-01, HTTP error handling

**Scenario:** The IMPL only catches HTTP errors via `resp.raise_for_status()` which raises requests.exceptions.HTTPError. However, network-level errors (ConnectionError, Timeout, ConnectTimeout) are not caught and will propagate as-is instead of being converted to RuntimeError.

**Failure:** Per TASK AC-05, the function must raise RuntimeError on HTTP errors. However, `requests.post()` can raise:
- requests.exceptions.ConnectionError
- requests.exceptions.Timeout
- requests.exceptions.ConnectTimeout
- requests.exceptions.ReadTimeout

These are not HTTPError subclasses and will not be caught by `raise_for_status()`. They will bubble up uncaught, violating the RuntimeError contract.

**Evidence:**
- IMPL STEP-01: Only calls `resp.raise_for_status()` for error detection
- No try/except around `requests.post()` call
- Reference implementation at `workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py` uses `_api_request_with_retry` which handles these cases
- Test ACT-05 only tests HTTPError, not other request exceptions

**Severity:** MAJOR

---

## Attack 4: Malformed base_url Handling - MAJOR

**Target:** STEP-01, endpoint URL construction

**Scenario:** The IMPL uses `f"{base_url.rstrip('/')}/v1/images/generations"` to construct the endpoint URL. If base_url is an empty string, this produces `/v1/images/generations` which is not a valid URL.

**Failure:** The IMPL does not validate that base_url is a non-empty string with a valid scheme (http/https). An empty string, whitespace-only string, or malformed URL will produce an invalid endpoint that will fail at request time with a confusing error rather than a clear RuntimeError.

**Evidence:**
- IMPL STEP-01 line 176: `f"{base_url.rstrip('/')}/v1/images/generations"`
- No validation of base_url format or non-emptiness
- No test case for empty or malformed base_url

**Severity:** MAJOR

---

## Attack 5: JSON Decode Error Not Handled - MAJOR

**Target:** STEP-01, response parsing

**Scenario:** The IMPL calls `resp.json()` without handling JSONDecodeError. If the API returns a non-JSON response (e.g., HTML error page, empty response), the function will raise JSONDecodeError instead of RuntimeError.

**Failure:** Per TASK AC-04 and AC-05, errors must raise RuntimeError. However, if the server returns an HTML error page or malformed JSON, `resp.json()` will raise `requests.exceptions.JSONDecodeError` which is not caught and converted to RuntimeError.

**Evidence:**
- IMPL STEP-01: `data = resp.json().get("data", [])` with no try/except
- No test case for non-JSON response
- Reference implementation at `workflows/agnes_media_gen_v1/impls/agnes_media_v1/actions.py` does not handle this either, indicating a pattern gap

**Severity:** MAJOR

---

## Attack 6: Missing Test for Revised Prompt - MINOR

**Target:** Section 7, test implementation

**Scenario:** The IMPL tests verify that "image_url" exists in the return dict (ACT-03 test) but do not verify that "revised_prompt" also exists, despite it being part of the return contract defined in STEP-01.

**Failure:** The ACT-03 test only asserts `"image_url" in result` but not `"revised_prompt" in result`. A broken implementation could return only `{"image_url": "..."}` and pass the test while violating the documented return contract `{"image_url": "<url>", "revised_prompt": "<prompt>"}`.

**Evidence:**
- IMPL Test Implementation ACT-03 (line 347-349): `assert "image_url" in result` but no `assert "revised_prompt" in result`
- STEP-01 specification: Return dict with `image_url` and `revised_prompt` keys

**Severity:** MINOR

---

## Attack 7: Missing Timeout Parameter Test - MINOR

**Target:** STEP-01, timeout parameter

**Scenario:** The IMPL specifies `timeout=500` in the requests.post() call but there is no test verifying this timeout is actually passed to requests.post(). A broken implementation could use a different timeout or omit it entirely.

**Failure:** The TASK requires the function to use `requests` library for HTTP calls with a 500-second timeout (per reference implementation). The IMPL includes timeout=500 but no test verifies this parameter is passed to requests.post().

**Evidence:**
- IMPL STEP-01: `requests.post(endpoint, headers=headers, json=payload, timeout=500)`
- No test inspects the timeout parameter passed to requests.post()
- Test ACT-06 inspects json payload, ACT-07 inspects URL, but no test inspects timeout

**Severity:** MINOR

---

## Verification Summary

All 5 attack areas have been checked:
1. Attack Necessity: Files do not exist, plan is needed (PASS)
2. Attack Test Coverage: Found gaps in test coverage for revised_prompt and timeout
3. Attack Implementation Logic: Found signature mismatch, missing validation, incomplete error handling
4. Attack Data Flow: Return contract may not be fully verified by tests
5. Attack Edge Cases: Found JSON decode error and malformed URL edge cases

Total: 7 attacks documented (1 BLOCKING, 4 MAJOR, 2 MINOR)
