---
template_id: "SYS-03-CR"
version: "1.0.0"
doc_type: "review_artifact"
lifecycle_status: "draft"
---

# Challenge: Implementation Plan

## Summary
- Total attacks: 7
- BLOCKING: 2
- MAJOR: 3
- MINOR: 2

---

## Attack 1: External Dependency Makes AC-05 Unachievable

**Target:** ACT-05 test and AC-05 acceptance criterion

**Scenario:** The impl.yaml files reference `prompts/extract_desc/standard.txt` and `prompts/generate_prompts/standard.txt` as prompt slot files. These files are Phase 7 deliverables from TASK-20260815-001-07 and do not currently exist on disk (confirmed via glob: no .txt files in prompts/ directory).

**Failure:** The TASK AC-05 states "All prompt_slots reference files that exist on disk" as a hard requirement. The IMPL creates impl.yaml files that reference non-existent files, knowingly violating this requirement. The IMPL acknowledges this in OQ-01 but dismisses it as "expected behavior for an incremental SDLC pipeline." However, a test that is guaranteed to fail is not a valid test - it is a documented failure. The implementation plan cannot satisfy AC-05 until Phase 7 is complete, making this task inherently blocked.

**Severity:** BLOCKING

**Evidence:**
- TASK AC-05: "All prompt_slots reference files that exist on disk"
- IMPL ACT-05 Current State: "MISSING -- The prompt .txt files (Phase 7 deliverable from TASK-20260815-001-07) do NOT currently exist on disk"
- Filesystem check: `workflows/gen_media_content_v1/prompts/**/*.txt` returns no files

---

## Attack 2: Test Count Mismatch Violates AC-09

**Target:** ACT-09 test and AC-09 acceptance criterion

**Scenario:** The TASK AC-09 explicitly requires "All 10 tests pass with pytest." The IMPL creates a test file with 24 test methods (6 + 6 + 3 + 3 + 3 + 3 = 24) and claims this "exceeds the minimum 10 tests required."

**Failure:** The acceptance criterion specifies exactly 10 tests, not "at least 10" or "10 or more." The IMPL deliberately exceeds this requirement, creating a compliance violation. If the task stakeholder expects exactly 10 tests (perhaps for reporting consistency or documentation alignment), the IMPL produces non-compliant output. The IMPL cannot satisfy AC-09 as stated because it will produce 24 passing tests, not 10.

**Severity:** MAJOR

**Evidence:**
- TASK AC-09: "All 10 tests pass with pytest"
- IMPL ACT-09: "Total: 6 + 6 + 3 + 3 + 3 + 3 = 24 test methods" and "This exceeds the minimum 10 tests required by AC-09"

---

## Attack 3: No Test for AC-10 (No Existing Files Modified)

**Target:** ACT-10 acceptance criterion test

**Scenario:** AC-10 requires "No existing files were modified." The IMPL includes ACT-10 with verification method "git status check" but this is not implemented as an actual test in the test_impls.py file.

**Failure:** The test file contains no test method that runs `git status` or otherwise verifies no existing files were modified. Step 9 of the Step-by-Step Plan mentions "Run git status to confirm no tracked files were modified" but this is a manual step, not an automated test. AC-09 claims "All 10 tests pass with pytest" but there is no pytest test for AC-10. The IMPL creates only 9 test classes (TestImplFilesExist, TestImplYamlValid, TestPresetJsonValid, TestImplNameMatchesDirectory, TestPromptSlotsReferenceExistingFiles, TestPresetActionNames) covering ACT-01 through ACT-08, but ACT-10 has no automated test.

**Severity:** MAJOR

**Evidence:**
- TASK AC-10: "No existing files were modified"
- IMPL test file: No TestNoExistingFilesModified class or equivalent
- IMPL Step 9: Manual "git status" step, not a pytest test

---

## Attack 4: Unverified Dependency on pyyaml

**Target:** Test execution and ACT-02/ACT-04/ACT-05

**Scenario:** The test file requires `import yaml` which depends on the pyyaml package. The IMPL acknowledges this in OQ-03 but provides no verification that pyyaml is actually installed in the project environment.

**Failure:** If pyyaml is not installed, the test file will fail with ImportError before any tests can run. The IMPL suggests checking with `.venv\Scripts\python -c "import yaml; print(yaml.__version__)"` but this check is not incorporated into the implementation plan as a prerequisite step. The plan has a Dependencies table listing pyyaml as required with status "Must be verified" but no actual verification step is included in the Step-by-Step Plan. If pyyaml is missing, all YAML-related tests (6 + 3 + 3 = 12 tests) will fail with ImportError.

**Severity:** MAJOR

**Evidence:**
- IMPL OQ-03: "The test suite uses yaml.safe_load() which requires the pyyaml package"
- IMPL Dependencies table: "pyyaml | Required | Must be verified"
- IMPL test_impls.py line 440: "import yaml"

---

## Attack 5: Unvalidated Action Override References

**Target:** impl.yaml overrides section and runtime behavior

**Scenario:** All three impl.yaml files contain overrides mapping workflow steps to action implementations: `generate_images -> generate_images_default` and `generate_videos -> generate_videos_default`.

**Failure:** The plan creates these override mappings but never validates that `generate_images_default` and `generate_videos_default` are valid action implementations that exist in the codebase. The test file checks that preset action names correspond to provider directories (ACT-05/ACT-06/ACT-07/ACT-08) but does not check impl.yaml override action names. If these action implementations don't exist or are misnamed, the impl.yaml files will parse correctly but the workflow will fail at runtime. The IMPL provides no test for override action validity.

**Severity:** MINOR

**Evidence:**
- impl.yaml content (all three): `overrides: generate_images: action: "generate_images_default"`
- Test file: No validation of override action names

---

## Attack 6: Dead Code in Test File

**Target:** Test file imports and path manipulation

**Scenario:** The test file contains extensive sys.path manipulation to add the project root to the Python path and imports PROJECT_ROOT, WORKFLOW_ROOT, IMPLS_ROOT.

**Failure:** The test file imports `import sys` and manipulates `sys.path`, but all actual test logic uses only standard library modules (json, pathlib.Path) and third-party modules (pytest, yaml) that don't require the project root to be in sys.path. The sys.path manipulation and PROJECT_ROOT constant are never used for any actual import from the project. This is dead code that adds complexity without functionality. The test file could run without any of the sys.path manipulation or PROJECT_ROOT definition.

**Severity:** MINOR

**Evidence:**
- test_impls.py lines 442-449: sys.path manipulation code
- test_impls.py: No imports from agent_runner_v2 or any project module

---

## Attack 7: render_image=__none__ Provider Directory Assumption

**Target:** video_only preset.json and api_actions structure

**Scenario:** The video_only preset uses `render_image: "__none__"` to skip image generation. The IMPL notes that there is no `api_actions/render_image/__none__/` directory.

**Failure:** The IMPL assumes `__none__` is a "configuration sentinel handled at the workflow routing level" but provides no evidence that the workflow runtime actually handles this case. For render_video, there IS a `__none__` provider directory at `api_actions/render_video/__none__/`, but for render_image there is none. The IMPL creates a configuration that references a non-existent provider without verifying the runtime supports this sentinel value. If the runtime expects all action values to have corresponding provider directories, the video_only preset will cause a runtime failure.

**Severity:** BLOCKING

**Evidence:**
- video_only preset.json: `"render_image": "__none__"`
- IMPL OQ-02: "there is no api_actions/render_image/__none__/ provider directory"
- IMPL OQ-02: "Assumption: The __none__ value for render_image is a configuration sentinel"
- Filesystem check: `api_actions/render_video/__none__/` exists but `api_actions/render_image/__none__/` does not

---

## Conclusion

This implementation plan cannot be executed successfully without addressing the BLOCKING issues:

1. **AC-05 cannot pass** because the prompt files don't exist. The plan knowingly creates files with broken references.
2. **AC-09 cannot be satisfied as specified** because the plan produces 24 tests instead of the required 10.
3. **The video_only preset may cause runtime failures** due to the unverified `__none__` sentinel assumption.

The plan requires revision before implementation can proceed.
