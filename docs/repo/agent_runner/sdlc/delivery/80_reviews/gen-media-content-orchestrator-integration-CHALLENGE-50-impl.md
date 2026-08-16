---
template_id: "SYS-03-CR"
version: "1.0.0"
doc_type: "review_artifact"
lifecycle_status: "draft"
---

# Challenge: Implementation Plan

## Summary
- Total attacks: 6
- BLOCKING: 0
- MAJOR: 5
- MINOR: 1

## Attack 1: Test Count Self-Verification is Not a Real Test
**Target:** ACT-09 test implementation in test_orchestrator.py (lines 897-908 of IMPL)
**Scenario:** The 14th test (test_fourteen_tests_in_file) is a meta-test that counts test methods in the file itself rather than testing actual implementation behavior.
**Failure:** ACT-09 requires "All 14 tests pass with pytest" but one of those tests (the 14th) merely counts how many methods start with "test_" in the source file. It does not verify any functional requirement from the TASK. If the implementation is completely broken but has 14 test methods, this test would pass while the actual functionality fails.
**Severity:** MAJOR

Evidence from IMPL lines 897-908:
```python
class TestTestCount:
    def test_fourteen_tests_in_file(self):
        """ACT-09: Verify this file contains exactly 14 test methods."""
        import inspect
        test_file = Path(__file__)
        source = test_file.read_text(encoding="utf-8")
        test_methods = [
            line.strip() for line in source.splitlines()
            if line.strip().startswith("def test_")
        ]
        assert len(test_methods) == 14, f"Expected 14 test methods, found {len(test_methods)}"
```

## Attack 2: Missing Config Key Validation in generate_images_default
**Target:** STEP-02 Implementation step 5 in IMPL (lines 213-222)
**Scenario:** The plan reads API config from `config["api"][provider_name]` without checking if the provider_name key exists in the "api" section.
**Failure:** If config.json has a valid provider name in actions.render_image but lacks the corresponding entry in the "api" section, the implementation will raise an unhandled KeyError at runtime instead of returning a proper ActionResult with REJECTED status and meaningful error code.
**Severity:** MAJOR

Evidence from IMPL lines 213-222:
```
5. Read API config from config["api"][provider_name]
6. Resolve API key via ApiKeyPool using _resolve_key_prefix
7. Resolve base_url via _resolve_base_url
8. Scan STEP_02_DIR for *_prompts.json variant files
```

No validation exists for the case where `provider_name` is not a key in `config["api"]`. Given config.json.sample only shows entries for "agnes_v1", "agnes_v2", and "happyhorse_v1_1", any other provider would cause a crash.

## Attack 3: Video Orchestrator Reads From Wrong Directory
**Target:** STEP-03 in IMPL (lines 225-238) vs TASK Step 2 item 8a (lines 67-69)
**Scenario:** The TASK specification explicitly states video orchestrator should "Read corresponding variant JSON from {STEP_02_DIR} for video prompt" but the IMPL directs scanning STEP_03_DIR instead.
**Failure:** This is a data flow break. The IMPL says "Scan STEP_03_DIR for updated variant JSONs (containing image_url)" but the TASK requires reading video prompts (t2v_prompt1) from STEP_02_DIR. The updated JSONs in STEP_03_DIR may not contain the original t2v_prompt1 field, causing video generation to fail or use wrong prompts.
**Severity:** MAJOR

Evidence from TASK lines 67-69:
```
8. For each image:
   a. Read corresponding variant JSON from {STEP_02_DIR} for video prompt (t2v_prompt1)
```

Evidence from IMPL lines 225-238:
```
7. Scan STEP_03_DIR for updated variant JSONs (containing image_url from image step)
8. For each variant, read video prompt, call provider.call_api...
```

The IMPL contradicts the TASK by reading from STEP_03_DIR instead of STEP_02_DIR for video prompts.

## Attack 4: No Handling for Empty Directories
**Target:** generate_images_default and generate_videos_default implementations
**Scenario:** When STEP_02_DIR or STEP_03_DIR exists but contains no valid *_prompts.json files, the implementation does not specify how to handle this case.
**Failure:** Looking at the reference implementation (agnes_media_gen_v1/actions.py lines 207-209), it explicitly checks for empty variant lists and returns REJECTED with "NO_INPUTS" code. The IMPL does not include this check in the step-by-step plan, which means the implementation may fail with obscure errors or hang when iterating over an empty collection.
**Severity:** MAJOR

Evidence from reference (agnes_media_gen_v1/actions.py lines 207-209):
```python
if not variant_jsons:
    return ActionResult(status="REJECTED", remark="No variant JSON files found in step_02_promptvariant.", artifacts={}, reject_code="NO_INPUTS")
```

The IMPL plan (STEP-02, lines 213-222) does not include this check, only mentioning "For each variant file, read variations..." which assumes at least one file exists.

## Attack 5: Base URL Resolution Fails for Unknown Providers
**Target:** _resolve_base_url helper function in IMPL (lines 305-313)
**Scenario:** When a provider name is not in _PROVIDER_BASE_URL_MAP, the function derives an env_var name but returns empty string if that env_var is not set.
**Failure:** The fallback logic at lines 311-313 derives an env_var name from the provider name but returns empty string if not found. This means unknown providers will have empty base_url passed to call_api, causing API calls to fail with invalid URLs. There is no validation to reject the action when base_url resolves to empty string.
**Severity:** MINOR

Evidence from IMPL lines 305-314:
```python
def _resolve_base_url(provider_name: str) -> str:
    """Resolve base URL for a provider from environment or default."""
    if provider_name in _PROVIDER_BASE_URL_MAP:
        env_var, default = _PROVIDER_BASE_URL_MAP[provider_name]
        return os.environ.get(env_var, default)
    # Fallback: derive env var name from provider name
    base = provider_name.split("_v")[0].upper()
    env_var = f"{base}_BASE_URL"
    return os.environ.get(env_var, "")  # Returns empty string if not set!
```

No check ensures the returned base_url is non-empty before using it in API calls.

## Attack 6: No Test for ImportError Message Content
**Target:** ACT-08 test implementation in test_orchestrator.py (lines 878-883 of IMPL)
**Scenario:** ACT-08 requires "import_provider raises ImportError for invalid names" but the test only verifies that an ImportError is raised, not that it contains a descriptive message as specified in the TASK.
**Failure:** The TASK AC-08 explicitly states "raises ImportError with descriptive message" but the test at lines 878-883 only checks that ImportError is raised, not the message content. A provider could raise ImportError("x") and pass the test while failing the actual requirement.
**Severity:** MINOR

Evidence from TASK line 90:
```
- import_provider raises ImportError with descriptive message for invalid names
```

Evidence from IMPL test (lines 878-883):
```python
def test_invalid_provider_raises_import_error(self):
    """ACT-08: import_provider raises ImportError for invalid names."""
    with patch("workflows.gen_media_content_v1.actions.importlib.import_module",
                side_effect=ModuleNotFoundError("No module")):
        with pytest.raises(ImportError):
            import_provider("render_image", "nonexistent_provider")
```

The test does not verify the error message is descriptive (e.g., contains "nonexistent_provider" or "not found").
