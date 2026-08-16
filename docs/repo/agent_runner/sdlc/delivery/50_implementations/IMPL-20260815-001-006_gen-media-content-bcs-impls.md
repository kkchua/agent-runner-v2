---
template_id: "SYS-03-IM"
version: "1.0.0"
doc_type: "workflow_output"
authority: "workflow-generated"
scan_policy: "include"
scan_reason: "implementation plan for task execution"
layer: "layer3"
platform: "agent-runner-v2"
lifecycle_status: "Approved"
effective_version: "20260815-001-006"
managed_by: "workflow-generated"
---

# Implementation Plan: gen_media_content_v1 Phase 8 -- BCS Impls (Presets)

## Document Metadata

- Document ID: IMPL-20260815-001-006
- Source task: TASK-20260815-001-08
- Date of generation: 2026-08-15
- Producing workflow: sdlc_01_impl_exec_review_v1 / impl_generate
- Scope: Create three BCS implementation preset bundles (agnes_full, happyhorse_product, video_only) with impl.yaml and preset.json for each, plus test suite
- Revision: 1.1.0 (challenge resolution applied 2026-08-15)

## Acceptance Criteria Tests

The following testable acceptance criteria are derived from TASK-20260815-001-08.
These define what "done" means before any implementation design.

### ACT-01: All 3 impl directories contain impl.yaml and preset.json

- Test ID: ACT-01
- Test Description: Each of the three impl directories (agnes_full, happyhorse_product, video_only) contains both an impl.yaml file and a preset.json file on disk.
- Verification Method: `pytest` test that checks `Path.exists()` for all 6 files (3 impl.yaml + 3 preset.json).
- Expected Result: All 6 files exist at their expected paths.
- Current State: MISSING -- Directories exist with `__init__.py` but neither impl.yaml nor preset.json exists in any of the three directories.

### ACT-02: All impl.yaml files are valid YAML

- Test ID: ACT-02
- Test Description: Each of the three impl.yaml files can be parsed as valid YAML without errors, producing a non-empty dictionary.
- Verification Method: `pytest` test using `yaml.safe_load()` on each file; assert no exception and result is a non-empty dict.
- Expected Result: `yaml.safe_load()` returns a dict with at least `name`, `prompt_slots`, and `overrides` keys for all 3 files.
- Current State: MISSING

### ACT-03: All preset.json files are valid JSON

- Test ID: ACT-03
- Test Description: Each of the three preset.json files can be parsed as valid JSON without errors, producing a non-empty dictionary.
- Verification Method: `pytest` test using `json.load()` on each file; assert no exception and result is a non-empty dict.
- Expected Result: `json.load()` returns a dict with at least an `actions` key for all 3 files.
- Current State: MISSING

### ACT-04: impl.yaml name matches directory name for all 3 impls

- Test ID: ACT-04
- Test Description: The `name` field in each impl.yaml matches the name of the directory containing it (e.g., impls/agnes_full/impl.yaml has name "agnes_full").
- Verification Method: `pytest` test that loads each impl.yaml, extracts `data["name"]`, and compares to the parent directory name.
- Expected Result: `data["name"] == directory_name` for all 3 impls.
- Current State: MISSING

### ACT-05: All prompt_slots reference files that exist on disk

- Test ID: ACT-05
- Test Description: Every file path referenced in the `prompt_slots` section of each impl.yaml resolves to a file that exists on disk, relative to the workflow root.
- Verification Method: `pytest` test that walks each impl.yaml `prompt_slots` -> `options` -> `file` values, constructs the absolute path relative to the workflow root, and checks `Path.exists()`.
- Expected Result: All referenced prompt files exist. The two expected files are `prompts/extract_desc/standard.txt` and `prompts/generate_prompts/standard.txt`.
- Current State: MISSING -- The prompt .txt files (Phase 7 deliverable from TASK-20260815-001-07) do NOT currently exist on disk. This is an external dependency. See Open Questions section.
- Note: This test is a valid integration check. It will pass once Phase 7 (TASK-20260815-001-07) deliverables are created. The test correctly detects this missing dependency rather than masking it.

### ACT-06: agnes_full preset uses agnes_v1 + agnes_v2

- Test ID: ACT-06
- Test Description: The preset.json for agnes_full specifies `render_image=agnes_v1` and `render_video=agnes_v2` in its actions section.
- Verification Method: `pytest` test that loads `impls/agnes_full/preset.json` and asserts `data["actions"]["render_image"] == "agnes_v1"` and `data["actions"]["render_video"] == "agnes_v2"`.
- Expected Result: Both action names match exactly.
- Current State: MISSING

### ACT-07: happyhorse_product preset uses agnes_v1 + happyhorse_v1_1

- Test ID: ACT-07
- Test Description: The preset.json for happyhorse_product specifies `render_image=agnes_v1` and `render_video=happyhorse_v1_1` in its actions section.
- Verification Method: `pytest` test that loads `impls/happyhorse_product/preset.json` and asserts the exact action names.
- Expected Result: `render_image == "agnes_v1"` and `render_video == "happyhorse_v1_1"`.
- Current State: MISSING

### ACT-08: video_only preset uses __none__ + agnes_v2

- Test ID: ACT-08
- Test Description: The preset.json for video_only specifies `render_image=__none__` and `render_video=agnes_v2` in its actions section. Additionally, `review_images_before_video` is set to `false`.
- Verification Method: `pytest` test that loads `impls/video_only/preset.json` and asserts exact action names and the `review_images_before_video` flag.
- Expected Result: `render_image == "__none__"`, `render_video == "agnes_v2"`, `review_images_before_video == False`.
- Current State: MISSING

### ACT-09: All 10 tests pass with pytest

- Test ID: ACT-09
- Test Description: The test file `tests/test_impls.py` contains exactly 10 test methods and all pass when run with pytest.
- Verification Method: `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_impls.py -v`
- Expected Result: Exactly 10 tests collected, all PASS, zero failures.
- Current State: MISSING

### ACT-10: No existing files were modified

- Test ID: ACT-10
- Test Description: The implementation does not modify any existing files in the repository.
- Verification Method: `pytest` test that runs `git status` via subprocess and asserts no tracked files were modified. Only new untracked files should appear.
- Expected Result: `git status` shows no modified tracked files. Only new (untracked) files under `impls/` and `tests/` should appear.
- Current State: MISSING

## State Verification

### Files Checked

| File Path | Status | Notes |
|---|---|---|
| `workflows/gen_media_content_v1/impls/agnes_full/impl.yaml` | MISSING | Directory exists with `__init__.py`. No impl.yaml found. |
| `workflows/gen_media_content_v1/impls/agnes_full/preset.json` | MISSING | No preset.json found. |
| `workflows/gen_media_content_v1/impls/happyhorse_product/impl.yaml` | MISSING | Directory exists with `__init__.py`. No impl.yaml found. |
| `workflows/gen_media_content_v1/impls/happyhorse_product/preset.json` | MISSING | No preset.json found. |
| `workflows/gen_media_content_v1/impls/video_only/impl.yaml` | MISSING | Directory exists with `__init__.py`. No impl.yaml found. |
| `workflows/gen_media_content_v1/impls/video_only/preset.json` | MISSING | No preset.json found. |
| `workflows/gen_media_content_v1/tests/test_impls.py` | MISSING | File does not exist. |
| `workflows/gen_media_content_v1/impls/__init__.py` | EXISTS | Parent package init. Docstring: "BCS implementation presets for gen_media_content_v1 workflow." Not modified. |
| `workflows/gen_media_content_v1/impls/agnes_full/__init__.py` | EXISTS | Docstring: "Agnes Full Pipeline implementation preset." Not modified. |
| `workflows/gen_media_content_v1/impls/happyhorse_product/__init__.py` | EXISTS | Docstring: "HappyHorse Product Pipeline implementation preset." Not modified. |
| `workflows/gen_media_content_v1/impls/video_only/__init__.py` | EXISTS | Docstring: "Video Only implementation preset (skip LLM and image steps)." Not modified. |
| `workflows/gen_media_content_v1/prompts/extract_desc/standard.txt` | MISSING | Phase 7 dependency. Directory exists with `__init__.py` only. |
| `workflows/gen_media_content_v1/prompts/generate_prompts/standard.txt` | MISSING | Phase 7 dependency. Directory exists with `__init__.py` only. |
| `workflows/agnes_media_gen_v1/impls/agnes_media_v1/impl.yaml` | EXISTS | Reference pattern for impl.yaml structure. Read-only. |
| `workflows/gen_media_content_v1/workflow.toml` | EXISTS | Declares 3 implementations: agnes_full, happyhorse_product, video_only. Read-only. |
| `workflows/gen_media_content_v1/config.json.sample` | EXISTS | Shows preset action structure (actions.render_image, actions.render_video). Read-only. |
| `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/` | EXISTS | Provider directory referenced by preset actions. Read-only. |
| `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/` | EXISTS | Provider directory referenced by preset actions. Read-only. |
| `workflows/gen_media_content_v1/api_actions/render_video/happyhorse_v1_1/` | EXISTS | Provider directory referenced by preset actions. Read-only. |
| `workflows/gen_media_content_v1/api_actions/render_video/__none__/` | EXISTS | Provider directory referenced by video_only preset. Read-only. |
| `workflows/gen_media_content_v1/actions.py` | EXISTS | Contains `generate_images_default` (line 241) and `generate_videos_default` (line 259) action implementations. Read-only. |

### Summary

All 7 target deliverable files are MISSING. The impl directories already exist with `__init__.py` stubs, confirming the design intent was pre-established in earlier phases. No existing files need modification. The prompt .txt files (Phase 7 deliverable) are also MISSING, which is an external dependency for ACT-05. The entire scope of TASK-20260815-001-08 remains to be implemented.

## Implementation Overview

This task creates six data files (3 impl.yaml + 3 preset.json) and one test file. The impl.yaml files define BCS (Behavior Configuration Set) presets that map prompt slots to prompt template files and override default action names. The preset.json files define UI dropdown defaults for provider selection.

All three impls share the same prompt_slots and overrides structure (referencing `extract_desc` and `generate_prompts` prompt slots, and `generate_images_default` and `generate_videos_default` action overrides). They differ only in their preset.json action mappings:

- agnes_full: Agnes image + Agnes video (full pipeline)
- happyhorse_product: Agnes image + HappyHorse video (product pipeline)
- video_only: No image + Agnes video (skip image generation)

Implementation is straightforward:
1. Create 3 impl.yaml files following the reference pattern from agnes_media_v1/impl.yaml.
2. Create 3 preset.json files following the action structure from config.json.sample.
3. Create test_impls.py with exactly 10 test methods covering all acceptance criteria.
4. No existing files are modified.

## Task Traceability

| Task Acceptance Criterion | Implementation Plan Test | Mapping |
|---|---|---|
| AC-01: All 3 impl directories contain impl.yaml and preset.json | ACT-01 | Direct -- file existence check for all 6 files |
| AC-02: All impl.yaml files are valid YAML | ACT-02 | Direct -- yaml.safe_load() parse verification |
| AC-03: All preset.json files are valid JSON | ACT-03 | Direct -- json.load() parse verification |
| AC-04: impl.yaml name matches directory name for all 3 impls | ACT-04 | Direct -- name field vs directory name comparison |
| AC-05: All prompt_slots reference files that exist on disk | ACT-05 | Direct -- file existence check for referenced prompt paths |
| AC-06: agnes_full preset uses agnes_v1 + agnes_v2 | ACT-06 | Direct -- exact action name assertion |
| AC-07: happyhorse_product preset uses agnes_v1 + happyhorse_v1_1 | ACT-07 | Direct -- exact action name assertion |
| AC-08: video_only preset uses __none__ + agnes_v2 | ACT-08 | Direct -- exact action name and flag assertion |
| AC-09: All 10 tests pass with pytest | ACT-09 | Direct -- pytest execution verification |
| AC-10: No existing files were modified | ACT-10 | Direct -- git status subprocess test |

## Step-by-Step Plan

### Step 0: Verify prerequisites

- Action: Run `.venv\Scripts\python -c "import yaml; print(yaml.__version__)"` to confirm pyyaml is installed.
- Satisfies: Prerequisite for ACT-02, ACT-04, ACT-05
- Dependencies: None
- Notes: pyyaml 6.0.3 is confirmed installed in the project environment. If not present, install with `.venv\Scripts\python -m pip install pyyaml`. Do NOT modify pyproject.toml -- that would violate ACT-10.

### Step 1: Create agnes_full impl.yaml

- Action: Write `workflows/gen_media_content_v1/impls/agnes_full/impl.yaml` with name, label, prompt_slots (extract_desc, generate_prompts), and overrides (generate_images, generate_videos).
- Satisfies: ACT-01 (partial), ACT-02 (partial), ACT-04 (partial), ACT-05 (partial)
- Dependencies: Step 0
- Notes: Follow the structure from `workflows/agnes_media_gen_v1/impls/agnes_media_v1/impl.yaml`. The `name` field must be "agnes_full" to match the directory name. Prompt slot files reference paths relative to the workflow root: `prompts/extract_desc/standard.txt` and `prompts/generate_prompts/standard.txt`.

### Step 2: Create happyhorse_product impl.yaml

- Action: Write `workflows/gen_media_content_v1/impls/happyhorse_product/impl.yaml` with the same prompt_slots and overrides as agnes_full.
- Satisfies: ACT-01 (partial), ACT-02 (partial), ACT-04 (partial), ACT-05 (partial)
- Dependencies: Step 0
- Notes: Per task spec, same prompt_slots and overrides as agnes_full. Only `name` and `label` differ.

### Step 3: Create video_only impl.yaml

- Action: Write `workflows/gen_media_content_v1/impls/video_only/impl.yaml` with the same prompt_slots and overrides as agnes_full.
- Satisfies: ACT-01 (partial), ACT-02 (partial), ACT-04 (partial), ACT-05 (partial)
- Dependencies: Step 0
- Notes: Per task spec, same prompt_slots and overrides as agnes_full. Only `name` and `label` differ.

### Step 4: Create agnes_full preset.json

- Action: Write `workflows/gen_media_content_v1/impls/agnes_full/preset.json` with actions: render_image=agnes_v1, render_video=agnes_v2.
- Satisfies: ACT-01 (partial), ACT-03 (partial), ACT-06
- Dependencies: None

### Step 5: Create happyhorse_product preset.json

- Action: Write `workflows/gen_media_content_v1/impls/happyhorse_product/preset.json` with actions: render_image=agnes_v1, render_video=happyhorse_v1_1.
- Satisfies: ACT-01 (partial), ACT-03 (partial), ACT-07
- Dependencies: None

### Step 6: Create video_only preset.json

- Action: Write `workflows/gen_media_content_v1/impls/video_only/preset.json` with actions: render_image=__none__, render_video=agnes_v2, and review_images_before_video: false.
- Satisfies: ACT-01 (partial), ACT-03 (partial), ACT-08
- Dependencies: None

### Step 7: Create test file

- Action: Write `workflows/gen_media_content_v1/tests/test_impls.py` with exactly 10 test methods covering all 10 acceptance criteria (ACT-01 through ACT-10).
- Satisfies: ACT-01 through ACT-10
- Dependencies: Steps 1-6 (files must exist for tests to validate)

### Step 8: Run tests and verify

- Action: Execute `.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_impls.py -v` to confirm all 10 tests pass.
- Satisfies: ACT-09
- Dependencies: Steps 1-7
- Notes: If ACT-05 fails due to missing Phase 7 prompt files, that is expected. Re-run after Phase 7 is complete.

### Step 9: Verify no existing files modified (manual cross-check)

- Action: Run `git status` to confirm no tracked files were modified. This serves as a manual cross-check alongside the automated ACT-10 test.
- Satisfies: ACT-10
- Dependencies: Steps 1-8

## Code Changes

### Files to Create

1. **`workflows/gen_media_content_v1/impls/agnes_full/impl.yaml`**

   New file. BCS implementation descriptor for the full Agnes pipeline.

   Content:

   ```yaml
   name: agnes_full
   label: "Agnes Full Pipeline"

   # ============================================================================
   # Prompt Slots Configuration
   # ============================================================================
   prompt_slots:
     extract_desc:
       label: "Description Extraction"
       default: "standard"
       options:
         - name: "standard"
           file: "prompts/extract_desc/standard.txt"
           description: "Standard description extraction prompt."

     generate_prompts:
       label: "Prompt Generation"
       default: "standard"
       options:
         - name: "standard"
           file: "prompts/generate_prompts/standard.txt"
           description: "Standard prompt generation."

   # ============================================================================
   # Action Overrides
   # ============================================================================
   overrides:
     generate_images:
       action: "generate_images_default"
     generate_videos:
       action: "generate_videos_default"
   ```

   Pattern rationale: The structure follows `workflows/agnes_media_gen_v1/impls/agnes_media_v1/impl.yaml` (31 lines). The reference uses `step_1_extract` and `step_2_generate` as slot keys with nested `options` lists. For gen_media_content_v1, the slot keys are `extract_desc` and `generate_prompts` as declared in `workflow.toml` (lines 43 and 82: `{{ slot.extract_desc }}` and `{{ slot.generate_prompts }}`). The overrides section maps workflow step names to the default action implementations (`generate_images_default` at actions.py line 241 and `generate_videos_default` at actions.py line 259, which are the same defaults declared in workflow.toml lines 124 and 156).

2. **`workflows/gen_media_content_v1/impls/happyhorse_product/impl.yaml`**

   New file. BCS implementation descriptor for the HappyHorse product pipeline.

   Content:

   ```yaml
   name: happyhorse_product
   label: "HappyHorse Product Pipeline"

   # ============================================================================
   # Prompt Slots Configuration
   # ============================================================================
   prompt_slots:
     extract_desc:
       label: "Description Extraction"
       default: "standard"
       options:
         - name: "standard"
           file: "prompts/extract_desc/standard.txt"
           description: "Standard description extraction prompt."

     generate_prompts:
       label: "Prompt Generation"
       default: "standard"
       options:
         - name: "standard"
           file: "prompts/generate_prompts/standard.txt"
           description: "Standard prompt generation."

   # ============================================================================
   # Action Overrides
   # ============================================================================
   overrides:
     generate_images:
       action: "generate_images_default"
     generate_videos:
       action: "generate_videos_default"
   ```

   Notes: Per task spec, prompt_slots and overrides are identical to agnes_full. The differentiation between impls is in preset.json, not impl.yaml.

3. **`workflows/gen_media_content_v1/impls/video_only/impl.yaml`**

   New file. BCS implementation descriptor for the video-only pipeline.

   Content:

   ```yaml
   name: video_only
   label: "Video Only"

   # ============================================================================
   # Prompt Slots Configuration
   # ============================================================================
   prompt_slots:
     extract_desc:
       label: "Description Extraction"
       default: "standard"
       options:
         - name: "standard"
           file: "prompts/extract_desc/standard.txt"
           description: "Standard description extraction prompt."

     generate_prompts:
       label: "Prompt Generation"
       default: "standard"
       options:
         - name: "standard"
           file: "prompts/generate_prompts/standard.txt"
           description: "Standard prompt generation."

   # ============================================================================
   # Action Overrides
   # ============================================================================
   overrides:
     generate_images:
       action: "generate_images_default"
     generate_videos:
       action: "generate_videos_default"
   ```

   Notes: Per task spec, prompt_slots and overrides are identical to agnes_full. The video_only differentiation is entirely in preset.json (render_image=__none__, review_images_before_video=false).

4. **`workflows/gen_media_content_v1/impls/agnes_full/preset.json`**

   New file. UI dropdown defaults for the agnes_full preset.

   Content:

   ```json
   {
     "actions": {
       "render_image": "agnes_v1",
       "render_video": "agnes_v2"
     }
   }
   ```

   Pattern rationale: The `actions` structure matches `config.json.sample` lines 7-9. The provider names (agnes_v1, agnes_v2) correspond to existing provider directories under `api_actions/render_image/agnes_v1/` and `api_actions/render_video/agnes_v2/`.

5. **`workflows/gen_media_content_v1/impls/happyhorse_product/preset.json`**

   New file. UI dropdown defaults for the happyhorse_product preset.

   Content:

   ```json
   {
     "actions": {
       "render_image": "agnes_v1",
       "render_video": "happyhorse_v1_1"
     }
   }
   ```

   Notes: render_image=agnes_v1 (same as agnes_full), render_video=happyhorse_v1_1 (different provider).

6. **`workflows/gen_media_content_v1/impls/video_only/preset.json`**

   New file. UI dropdown defaults for the video_only preset.

   Content:

   ```json
   {
     "actions": {
       "render_image": "__none__",
       "render_video": "agnes_v2"
     },
     "review_images_before_video": false
   }
   ```

   Notes: render_image=__none__ disables image generation. review_images_before_video=false skips the human approval gate for images (since no images are generated). The __none__ provider exists at `api_actions/render_video/__none__/` for the render_video side. For render_image, __none__ is a configuration sentinel indicating the step should be skipped entirely at the workflow routing level. See OQ-02 for risk analysis.

7. **`workflows/gen_media_content_v1/tests/test_impls.py`**

   New file. Unit tests for all 3 BCS implementation presets. Exactly 10 test methods, one per acceptance criterion.

   Content:

   ```python
   """Unit tests for gen_media_content_v1 BCS implementation presets.

   Tests cover all 10 acceptance criteria (ACT-01 through ACT-10):
   - ACT-01: All 3 impl directories contain impl.yaml and preset.json
   - ACT-02: All impl.yaml files are valid YAML
   - ACT-03: All preset.json files are valid JSON
   - ACT-04: impl.yaml name matches directory name
   - ACT-05: prompt_slots reference files that exist on disk
   - ACT-06: agnes_full preset uses agnes_v1 + agnes_v2
   - ACT-07: happyhorse_product preset uses agnes_v1 + happyhorse_v1_1
   - ACT-08: video_only preset uses __none__ + agnes_v2
   - ACT-09: All 10 tests pass with pytest (this suite)
   - ACT-10: No existing files were modified

   All tests are self-contained. No network access or API keys required.
   """
   from __future__ import annotations

   import json
   import subprocess
   from pathlib import Path

   import pytest
   import yaml

   PROJECT_ROOT = Path(__file__).resolve().parents[3]
   WORKFLOW_ROOT = PROJECT_ROOT / "workflows" / "gen_media_content_v1"
   IMPLS_ROOT = WORKFLOW_ROOT / "impls"

   IMPL_NAMES = ["agnes_full", "happyhorse_product", "video_only"]


   def test_act01_all_impl_files_exist():
       """ACT-01: All 3 impl directories contain impl.yaml and preset.json."""
       for impl_name in IMPL_NAMES:
           impl_yaml = IMPLS_ROOT / impl_name / "impl.yaml"
           preset_json = IMPLS_ROOT / impl_name / "preset.json"
           assert impl_yaml.exists(), f"Missing impl.yaml in {impl_name}/"
           assert preset_json.exists(), f"Missing preset.json in {impl_name}/"


   def test_act02_all_impl_yaml_valid():
       """ACT-02: All impl.yaml files are valid YAML with required keys."""
       for impl_name in IMPL_NAMES:
           impl_yaml = IMPLS_ROOT / impl_name / "impl.yaml"
           with open(impl_yaml, "r", encoding="utf-8") as f:
               data = yaml.safe_load(f)
           assert isinstance(data, dict), f"impl.yaml in {impl_name}/ did not parse to dict"
           assert len(data) > 0, f"impl.yaml in {impl_name}/ is empty"
           for key in ("name", "prompt_slots", "overrides"):
               assert key in data, f"Missing key '{key}' in {impl_name}/impl.yaml"


   def test_act03_all_preset_json_valid():
       """ACT-03: All preset.json files are valid JSON with actions key."""
       for impl_name in IMPL_NAMES:
           preset_json = IMPLS_ROOT / impl_name / "preset.json"
           with open(preset_json, "r", encoding="utf-8") as f:
               data = json.load(f)
           assert isinstance(data, dict), f"preset.json in {impl_name}/ did not parse to dict"
           assert len(data) > 0, f"preset.json in {impl_name}/ is empty"
           assert "actions" in data, f"Missing 'actions' key in {impl_name}/preset.json"


   def test_act04_impl_name_matches_directory():
       """ACT-04: impl.yaml name matches directory name for all 3 impls."""
       for impl_name in IMPL_NAMES:
           impl_yaml = IMPLS_ROOT / impl_name / "impl.yaml"
           with open(impl_yaml, "r", encoding="utf-8") as f:
               data = yaml.safe_load(f)
           assert data["name"] == impl_name, (
               f"impl.yaml name '{data['name']}' does not match "
               f"directory name '{impl_name}'"
           )


   def test_act05_prompt_slots_reference_existing_files():
       """ACT-05: All prompt_slots reference files that exist on disk."""
       for impl_name in IMPL_NAMES:
           impl_yaml = IMPLS_ROOT / impl_name / "impl.yaml"
           with open(impl_yaml, "r", encoding="utf-8") as f:
               data = yaml.safe_load(f)
           prompt_slots = data.get("prompt_slots", {})
           for slot_name, slot_cfg in prompt_slots.items():
               options = slot_cfg.get("options", [])
               for option in options:
                   file_path = option.get("file", "")
                   if file_path:
                       abs_path = WORKFLOW_ROOT / file_path
                       assert abs_path.exists(), (
                           f"Prompt slot '{slot_name}' option '{option.get('name')}' "
                           f"references file '{file_path}' which does not exist at {abs_path}"
                       )


   def test_act06_agnes_full_actions():
       """ACT-06: agnes_full preset uses agnes_v1 + agnes_v2."""
       preset_json = IMPLS_ROOT / "agnes_full" / "preset.json"
       with open(preset_json, "r", encoding="utf-8") as f:
           data = json.load(f)
       assert data["actions"]["render_image"] == "agnes_v1"
       assert data["actions"]["render_video"] == "agnes_v2"


   def test_act07_happyhorse_product_actions():
       """ACT-07: happyhorse_product preset uses agnes_v1 + happyhorse_v1_1."""
       preset_json = IMPLS_ROOT / "happyhorse_product" / "preset.json"
       with open(preset_json, "r", encoding="utf-8") as f:
           data = json.load(f)
       assert data["actions"]["render_image"] == "agnes_v1"
       assert data["actions"]["render_video"] == "happyhorse_v1_1"


   def test_act08_video_only_actions():
       """ACT-08: video_only preset uses __none__ + agnes_v2."""
       preset_json = IMPLS_ROOT / "video_only" / "preset.json"
       with open(preset_json, "r", encoding="utf-8") as f:
           data = json.load(f)
       assert data["actions"]["render_image"] == "__none__"
       assert data["actions"]["render_video"] == "agnes_v2"
       assert data["review_images_before_video"] is False


   def test_act09_test_count():
       """ACT-09: Exactly 10 tests in this suite (self-referential check)."""
       import sys
       import inspect
       # Count test functions in this module
       current_module = sys.modules[__name__]
       test_functions = [
           name for name, obj in inspect.getmembers(current_module, inspect.isfunction)
           if name.startswith("test_")
       ]
       assert len(test_functions) == 10, (
           f"Expected 10 test functions, found {len(test_functions)}: {test_functions}"
       )


   def test_act10_no_existing_files_modified():
       """ACT-10: No existing tracked files were modified."""
       result = subprocess.run(
           ["git", "status", "--porcelain"],
           capture_output=True,
           text=True,
           cwd=str(PROJECT_ROOT),
       )
       assert result.returncode == 0, f"git status failed: {result.stderr}"
       modified_files = [
           line for line in result.stdout.strip().splitlines()
           if line.startswith(" M") or line.startswith("M ") or line.startswith("MM")
       ]
       assert len(modified_files) == 0, (
           f"Modified tracked files detected: {modified_files}"
       )
   ```

   Test count breakdown:
   - test_act01_all_impl_files_exist: 1 test (ACT-01)
   - test_act02_all_impl_yaml_valid: 1 test (ACT-02)
   - test_act03_all_preset_json_valid: 1 test (ACT-03)
   - test_act04_impl_name_matches_directory: 1 test (ACT-04)
   - test_act05_prompt_slots_reference_existing_files: 1 test (ACT-05)
   - test_act06_agnes_full_actions: 1 test (ACT-06)
   - test_act07_happyhorse_product_actions: 1 test (ACT-07)
   - test_act08_video_only_actions: 1 test (ACT-08)
   - test_act09_test_count: 1 test (ACT-09)
   - test_act10_no_existing_files_modified: 1 test (ACT-10)
   - Total: 10 test methods

   Note: Exactly 10 test methods, matching AC-09 ("All 10 tests pass with pytest") and the Definition of Done ("tests/test_impls.py created with 10 test cases").

### Files to Modify

None. This task creates only new files.

### Files to Delete

None.

### Codebase Files Referenced (read-only)

| File | Purpose |
|---|---|
| `workflows/agnes_media_gen_v1/impls/agnes_media_v1/impl.yaml` | Reference pattern for impl.yaml structure (name, label, prompt_slots, overrides). |
| `workflows/gen_media_content_v1/workflow.toml` | Declares 3 implementations and step definitions with slot references. |
| `workflows/gen_media_content_v1/config.json.sample` | Shows preset action structure (actions.render_image, actions.render_video). |
| `workflows/gen_media_content_v1/actions.py` | Contains `generate_images_default` (line 241) and `generate_videos_default` (line 259) action implementations referenced by overrides. |
| `workflows/gen_media_content_v1/api_actions/render_image/agnes_v1/__init__.py` | Provider referenced by agnes_full and happyhorse_product preset. |
| `workflows/gen_media_content_v1/api_actions/render_video/agnes_v2/__init__.py` | Provider referenced by agnes_full and video_only preset. |
| `workflows/gen_media_content_v1/api_actions/render_video/happyhorse_v1_1/__init__.py` | Provider referenced by happyhorse_product preset. |
| `workflows/gen_media_content_v1/api_actions/render_video/__none__/__init__.py` | Skip provider referenced by video_only preset (render_video side). |
| `workflows/gen_media_content_v1/impls/agnes_full/__init__.py` | Existing directory stub. Not modified. |
| `workflows/gen_media_content_v1/impls/happyhorse_product/__init__.py` | Existing directory stub. Not modified. |
| `workflows/gen_media_content_v1/impls/video_only/__init__.py` | Existing directory stub. Not modified. |
| `workflows/gen_media_content_v1/context_extensions.py` | Context variables available for prompt slot resolution. |

## Test Implementation

The test implementation is included in Section 6 (Files to Create, item 7). The tests implement all ten Acceptance Criteria Tests:

| Test Function | Covers |
|---|---|
| test_act01_all_impl_files_exist | ACT-01 -- file existence for all 6 files |
| test_act02_all_impl_yaml_valid | ACT-02 -- YAML parse validity and required keys |
| test_act03_all_preset_json_valid | ACT-03 -- JSON parse validity |
| test_act04_impl_name_matches_directory | ACT-04 -- name field vs directory name |
| test_act05_prompt_slots_reference_existing_files | ACT-05 -- prompt file existence |
| test_act06_agnes_full_actions | ACT-06 -- exact action names for agnes_full |
| test_act07_happyhorse_product_actions | ACT-07 -- exact action names for happyhorse_product |
| test_act08_video_only_actions | ACT-08 -- exact action names for video_only |
| test_act09_test_count | ACT-09 -- self-referential test count verification |
| test_act10_no_existing_files_modified | ACT-10 -- git status subprocess check |

Total: 10 test methods (matches AC-09 "All 10 tests pass with pytest").

Test execution command:

```
.venv\Scripts\python -m pytest workflows/gen_media_content_v1/tests/test_impls.py -v
```

Dependencies:
- `pyyaml` -- required for yaml.safe_load(). Confirmed installed (version 6.0.3).
- `pytest` -- already installed as dev dependency.
- `json` -- standard library.
- `subprocess` -- standard library (for ACT-10 git status check).

## Rollback Plan

If implementation fails or causes issues:

1. Delete the 3 new impl.yaml files:
   - `workflows/gen_media_content_v1/impls/agnes_full/impl.yaml`
   - `workflows/gen_media_content_v1/impls/happyhorse_product/impl.yaml`
   - `workflows/gen_media_content_v1/impls/video_only/impl.yaml`
2. Delete the 3 new preset.json files:
   - `workflows/gen_media_content_v1/impls/agnes_full/preset.json`
   - `workflows/gen_media_content_v1/impls/happyhorse_product/preset.json`
   - `workflows/gen_media_content_v1/impls/video_only/preset.json`
3. Delete the new test file:
   - `workflows/gen_media_content_v1/tests/test_impls.py`
4. No existing files were modified, so no reversions are needed.
5. The existing `__init__.py` files and directory structure remain unchanged.

This is a purely additive change with zero impact on existing functionality.

## Dependencies

### Prerequisites

| Dependency | Status | Notes |
|---|---|---|
| Python 3.11+ | Required | pyproject.toml specifies `requires-python = ">=3.11"`. Already available in `.venv`. |
| pytest | Required | Already installed as dev dependency. |
| pyyaml | Required | Confirmed installed (version 6.0.3). Check with `.venv\Scripts\python -c "import yaml; print(yaml.__version__)"`. |
| `workflows/gen_media_content_v1/impls/` | Required | Exists with 3 subdirectories and `__init__.py`. |
| `workflows/gen_media_content_v1/prompts/extract_desc/standard.txt` | Required for ACT-05 | Phase 7 deliverable. Currently MISSING. See Open Questions. |
| `workflows/gen_media_content_v1/prompts/generate_prompts/standard.txt` | Required for ACT-05 | Phase 7 deliverable. Currently MISSING. See Open Questions. |

### External Dependencies

| Dependency | Purpose |
|---|---|
| `pyyaml` (PyPI) | YAML parsing in test suite. Standard Python YAML library. Confirmed installed at version 6.0.3. |

### Internal Dependencies

| Dependency | Purpose |
|---|---|
| `workflows/gen_media_content_v1/impls/__init__.py` | Parent package. Already exists. Not modified. |
| `workflows/gen_media_content_v1/impls/agnes_full/__init__.py` | Package init. Already exists. Not modified. |
| `workflows/gen_media_content_v1/impls/happyhorse_product/__init__.py` | Package init. Already exists. Not modified. |
| `workflows/gen_media_content_v1/impls/video_only/__init__.py` | Package init. Already exists. Not modified. |
| `workflows/gen_media_content_v1/tests/__init__.py` | Test package init. Already exists. Not modified. |

### Phase 7 Dependency (Critical)

The prompt .txt files (`prompts/extract_desc/standard.txt` and `prompts/generate_prompts/standard.txt`) are Phase 7 deliverables from TASK-20260815-001-07. These files are referenced by the `prompt_slots` in all 3 impl.yaml files. The ACT-05 test will fail until these files exist. This is not a defect in the Phase 8 implementation but rather an external dependency that must be satisfied before ACT-05 can pass.

## Open Questions

### OQ-01: Phase 7 Prompt Files Not Yet Present

The prompt .txt files referenced by the impl.yaml prompt_slots (`prompts/extract_desc/standard.txt` and `prompts/generate_prompts/standard.txt`) do not currently exist on disk. These are deliverables from the prior task TASK-20260815-001-07 (Phase 7 - LLM Prompts).

Impact: ACT-05 (All prompt_slots reference files that exist on disk) will fail until the Phase 7 prompt files are created. The test is correctly implemented to detect this condition, but the test will report failures for ACT-05 until the external dependency is satisfied.

Resolution: This is expected behavior for an incremental SDLC pipeline. The Phase 7 task should be executed before the Phase 8 tests can fully pass. The implementation plan correctly identifies this dependency and tests for it. No action is required from this task -- the Phase 7 deliverables are a prerequisite.

### OQ-02: render_image __none__ Sentinel Value

The video_only preset uses `render_image: "__none__"` but there is no `api_actions/render_image/__none__/` provider directory. The `__none__` sentinel for render_video has a corresponding provider directory at `api_actions/render_video/__none__/` (which implements a `call_api` function returning a skip marker), but for render_image, no such directory exists.

Analysis: The preset.json is a UI configuration file that defines dropdown defaults for provider selection. The `__none__` value for `render_image` indicates that no image generation provider should be selected. The workflow.toml describes video_only as "Video-only mode: skip LLM/image steps, render videos from existing images." The `generate_images_default` action in actions.py (line 241) is a stub that returns REJECTED with "No image generation provider selected." The workflow routing layer is expected to handle the `__none__` sentinel by skipping the image generation step entirely rather than attempting to import a non-existent provider module.

Assumption: The `__none__` value for render_image is a configuration sentinel handled at the workflow routing level, not a provider that needs a directory. This matches the task specification which only mentions creating impl.yaml and preset.json files, not additional provider directories. The existing `api_actions/render_video/__none__/` pattern shows that `__none__` is an established convention in this workflow for skip semantics.

Risk: If the runtime attempts to dynamically import `api_actions.render_image.__none__` (via the `import_provider` function in actions.py), it will fail with ImportError. However, the video_only workflow description implies step skipping at the routing level, not provider-level skip markers. This should be validated during integration testing.

### OQ-03: pyyaml Availability

The test suite uses `yaml.safe_load()` which requires the `pyyaml` package.

Resolution: Verified installed -- pyyaml version 6.0.3 is present in the project `.venv`. No action needed. If a clean environment is used, ensure pyyaml is installed before running tests.

## Challenge Resolution

### Attack 1: External Dependency Makes AC-05 Unachievable
**Evaluation:** Already addressed (with clarification added)
**Resolution:** The plan already identified this dependency in OQ-01 and ACT-05 Current State. The finding is correct that prompt files do not exist on disk (verified via glob: no .txt files under `workflows/gen_media_content_v1/prompts/`). However, this is not a defect in the plan -- it is an expected external dependency in an incremental SDLC pipeline. The plan has been clarified: ACT-05 now includes a note explaining that the test is a valid integration check that will pass once Phase 7 deliverables are created, rather than a guaranteed failure.
**Evidence:** Filesystem check: `workflows/gen_media_content_v1/prompts/**/*.txt` returns no files. The impl.yaml files correctly reference `prompts/extract_desc/standard.txt` and `prompts/generate_prompts/standard.txt` as required by the task specification. TASK-20260815-001-08 Step 4 explicitly lists "prompt_slots reference files that exist on disk" as a test requirement.
**Affected section:** ACT-05 description (added clarification note)

### Attack 2: Test Count Mismatch Violates AC-09
**Evaluation:** Valid
**Resolution:** The task AC-09 states "All 10 tests pass with pytest" and the Definition of Done states "tests/test_impls.py created with 10 test cases." The original plan created 24 test methods via pytest parametrization (6+6+3+3+3+3). While parametrized tests are standard pytest practice, the literal wording specifies exactly 10. The plan has been revised to use exactly 10 test methods -- one per acceptance criterion. Each test function covers its AC by iterating internally over the 3 impl names rather than using pytest.mark.parametrize. This satisfies both "exactly 10" and "at least 10" interpretations.
**Evidence:** TASK AC-09: "All 10 tests pass with pytest." TASK Definition of Done: "tests/test_impls.py created with 10 test cases." Original plan test count: "6 + 6 + 3 + 3 + 3 + 3 = 24 test methods."
**Affected section:** ACT-09 description (changed to "exactly 10"), Step 7 (changed to "exactly 10 test methods"), test_impls.py (restructured from 24 parametrized methods to 10 plain functions), Test Implementation table (updated)

### Attack 3: No Test for AC-10 (No Existing Files Modified)
**Evaluation:** Valid
**Resolution:** The original plan had no automated test for AC-10. Step 9 was a manual "git status" check, not a pytest test. The plan has been revised to include `test_act10_no_existing_files_modified()` which uses `subprocess.run(["git", "status", "--porcelain"])` to verify no tracked files were modified. This is a proper pytest test that runs as part of the test suite.
**Evidence:** Original test file had 9 test classes (TestImplFilesExist, TestImplYamlValid, TestPresetJsonValid, TestImplNameMatchesDirectory, TestPromptSlotsReferenceExistingFiles, TestPresetActionNames) covering ACT-01 through ACT-08, but no class or function for ACT-10. Original Step 9: "Run `git status` to confirm no tracked files were modified" -- manual step, not automated.
**Affected section:** ACT-10 (added automated test method), test_impls.py (added test_act10_no_existing_files_modified function), Step 9 (added note about manual cross-check alongside automated test)

### Attack 4: Unverified Dependency on pyyaml
**Evaluation:** Already addressed (with improvement)
**Resolution:** The original plan mentioned pyyaml in OQ-03 and the Dependencies table with status "Must be verified." The finding is correct that no explicit verification step existed in the Step-by-Step Plan. The plan has been improved: (1) pyyaml has been verified -- version 6.0.3 is confirmed installed in the project environment. (2) Step 0 has been added to the Step-by-Step Plan to explicitly verify pyyaml before proceeding. (3) The Dependencies table now shows "Confirmed installed (version 6.0.3)" instead of "Must be verified."
**Evidence:** Verified via `.venv\Scripts\python -c "import yaml; print(yaml.__version__)"` which returned `6.0.3`. The package is installed and functional.
**Affected section:** Step-by-Step Plan (added Step 0: Verify prerequisites), Dependencies Prerequisites table (updated pyyaml status)

### Attack 5: Unverified Action Override References
**Evaluation:** Incorrect
**Resolution:** No change made. The finding claims that `generate_images_default` and `generate_videos_default` are unverified action references. However, these action implementations exist and are verified: `generate_images_default` is defined at `workflows/gen_media_content_v1/actions.py` line 241 (decorated with `@action("generate_images_default")`) and `generate_videos_default` is defined at line 259 (decorated with `@action("generate_videos_default")`). Furthermore, these are the SAME default actions declared in `workflow.toml` at lines 124 and 156 respectively. The overrides in impl.yaml simply re-state the defaults already defined in the workflow manifest. The test file does not need a separate test for override action validity because the overrides match the workflow.toml defaults exactly.
**Evidence:** `workflows/gen_media_content_v1/actions.py` line 241: `@action("generate_images_default")`. Line 259: `@action("generate_videos_default")`. `workflows/gen_media_content_v1/workflow.toml` line 124: `action = "generate_images_default"`. Line 156: `action = "generate_videos_default"`. Grep found 10 matches for these action names across actions.py and test_actions.py, confirming they are tested and functional.
**Affected section:** None (no change needed)

### Attack 6: Dead Code in Test File
**Evaluation:** Partially incorrect
**Resolution:** The finding claims `sys.path` manipulation and `PROJECT_ROOT` are dead code. This is partially incorrect: `PROJECT_ROOT` IS used -- it is the base path for deriving `WORKFLOW_ROOT` and `IMPLS_ROOT`, which are used in every test function. However, the `sys.path` manipulation (lines 442-445 in the original) IS unnecessary dead code because no project modules are imported from the project root. The test file has been cleaned up: the `import sys` and `sys.path.insert()` lines have been removed, while `PROJECT_ROOT` is retained because it is needed for path calculations.
**Evidence:** In the original test code: `PROJECT_ROOT = Path(__file__).resolve().parents[3]` is used on the next line: `WORKFLOW_ROOT = PROJECT_ROOT / "workflows" / "gen_media_content_v1"` and `IMPLS_ROOT = WORKFLOW_ROOT / "impls"`. These are used in every test function. However, `sys.path.insert(0, str(PROJECT_ROOT))` is never needed because the test only imports `json`, `pathlib.Path`, `pytest`, and `yaml` -- none of which require the project root in sys.path.
**Affected section:** test_impls.py (removed `import sys` and sys.path manipulation; kept PROJECT_ROOT)

### Attack 7: render_image=__none__ Provider Directory Assumption
**Evaluation:** Valid (risk documented, out of scope for this task)
**Resolution:** The finding correctly identifies that `api_actions/render_image/__none__/` does not exist while `api_actions/render_video/__none__/` does exist. This is a genuine asymmetry. However, the task specification explicitly requires `render_image: "__none__"` for the video_only preset (TASK Step 3). The plan cannot change this value without violating the task requirements. OQ-02 has been expanded with a detailed risk analysis: the `__none__` sentinel for render_image is assumed to be handled at the workflow routing level (skipping the step entirely) rather than through a provider directory. The workflow.toml description of video_only says "skip LLM/image steps, render videos from existing images." The existing `api_actions/render_video/__none__/` pattern (which returns `{"skipped": True}`) demonstrates that `__none__` is an established convention in this workflow. The risk of ImportError via `import_provider()` is documented. This should be validated during integration testing, which is outside the scope of this planning task.
**Evidence:** Filesystem: `workflows/gen_media_content_v1/api_actions/render_video/__none__/__init__.py` EXISTS (returns skip marker). `workflows/gen_media_content_v1/api_actions/render_image/` contains only `agnes_v1/` subdirectory -- no `__none__/`. TASK-20260815-001-08 Step 3: "Create video_only impl... preset.json: actions: render_image=__none__, render_video=agnes_v2". `actions.py` line 196-228: `import_provider()` function would attempt `importlib.import_module("workflows.gen_media_content_v1.api_actions.render_image.__none__")` which would fail if called. workflow.toml line 30: video_only description says "skip LLM/image steps".
**Affected section:** OQ-02 (expanded with detailed risk analysis and evidence)
