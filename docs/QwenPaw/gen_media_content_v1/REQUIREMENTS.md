# Requirements: gen_media_content_v1 — Unified Media Generation Workflow

## 1. Background

Two existing workflows (`agnes_media_gen_v1` and `agnes_gen_video_v1`) share overlapping logic but are locked to specific API providers. The goal is to create a new unified workflow package that decouples steps from implementations, enabling any combination of LLM prompts and API providers.

## 2. Source Workflows

| Workflow | Location |
|---|---|
| `agnes_media_gen_v1` | `workflows/agnes_media_gen_v1/` |
| `agnes_gen_video_v1` | `workflows/agnes_gen_video_v1/` |

## 3. Design Principles

### 3.1 workflow.toml is the Orchestrator
- `workflow.toml` defines the pipeline: steps, order, gates, routing.
- It uses `{{ slot.* }}` syntax for prompt/action resolution.
- It does NOT contain provider-specific logic.

### 3.2 Each Step is a Swappable Unit
- **LLM steps** (prompt-driven): resolved via `{{ slot.* }}` in `workflow.toml` → picks from `prompts/<step>/*.txt`.
- **Action steps** (code-driven): resolved by root orchestrator reading `config.json` → dispatches to provider in `api_actions/`.
- Each `@action` or prompt file is a **single unit of work** — independently testable with its own unit test.

### 3.3 Action Resolution Flow
- `workflow.toml` declares `action = "generate_images_default"` and `action = "generate_videos_default"` (always the same — these are the **orchestrator actions**).
- Root `actions.py` implements `generate_images_default` and `generate_videos_default`.
- The orchestrator reads `config.json` → finds `actions.render_image` and `actions.render_video`.
- It dynamically imports the corresponding provider module from `api_actions/` and dispatches to it.
- This keeps `workflow.toml` static while allowing per-job provider selection via config.

### 3.4 API Providers are Pure
- A provider function takes: `prompt` + `image` (optional) + `config params` (model, resolution, ratio, etc.).
- It does NOT scan directories, parse JSON files, or orchestrate loops.
- It calls the external API, handles polling (for async APIs), and returns the result.
- Directory scanning, JSON parsing, batching, and index.json writing belong in the **orchestrator action** (root `actions.py`).

### 3.5 Impls are Presets (Flavor Bookmarks)
- `impls/<name>/` contains `preset.json` that auto-fills ALL dropdown values.
- `impls/<name>/impl.yaml` maps step names to orchestrator action names (BCS contract).
- User selects an impl → all dropdowns populate → user can still override any value.

### 3.6 Different Flows = Different Workflow Packages
- If a flow needs different steps or routing, create a separate workflow package.
- This workflow (`gen_media_content_v1`) covers: extract_desc → generate_prompts → render_image → render_video.
- Additional flows (e.g., thumbnails, quality checks) are separate packages.

### 3.7 TDD Mandatory
- Every `@action` function has a corresponding unit test.
- Every prompt template has a test verifying it renders with slot variables.
- Provider functions (pure API calls) must have tests with mocked HTTP.
- Tests are co-located: `tests/test_<module>.py`.

## 4. Directory Structure

```
gen_media_content_v1/
├── workflow.toml              # Orchestrator: defines steps, slots, routing (action names are static)
├── actions.py                 # Root actions: orchestrator + shared utilities + default stubs
├── context_extensions.py      # Context variable providers (step dirs, config path, etc.)
├── config.json.sample         # Sample config with all fields documented
├── .env.sample                # Sample environment variables
├── README.md                  # Usage documentation
│
├── prompts/                   # ← LLM prompt pool (dropdown source)
│   ├── extract_desc/
│   │   └── standard.txt       # Default: full 9-group attribute extraction
│   └── generate_prompts/
│       └── standard.txt       # Default: photorealistic prompt generation
│
├── api_actions/               # ← API provider pool (code pool, dynamically imported)
│   ├── __init__.py            # Provider registry: maps provider name → module
│   ├── render_image/
│   │   ├── __init__.py
│   │   └── agnes_v1/
│   │       ├── __init__.py    # Exports: call_api(prompt, image, config) → result
│   │       └── test_agnes_v1.py  # Unit tests (mocked HTTP)
│   └── render_video/
│       ├── __init__.py
│       ├── agnes_v2/
│       │   ├── __init__.py    # Exports: call_api(prompt, image, config) → result
│       │   └── test_agnes_v2.py
│       ├── happyhorse_v1_1/
│       │   ├── __init__.py    # Exports: call_api(prompt, image, config) → result
│       │   └── test_happyhorse_v1_1.py
│       └── __none__/
│           └── __init__.py    # Exports: call_api() → "skipped" marker
│
├── impls/                     # ← Presets / flavor bookmarks (BCS layer)
│   ├── agnes_full/
│   │   ├── impl.yaml          # BCS: maps steps to orchestrator action names
│   │   └── preset.json        # UI: auto-fill all dropdown defaults
│   ├── happyhorse_product/
│   │   ├── impl.yaml
│   │   └── preset.json
│   └── video_only/
│       ├── impl.yaml
│       └── preset.json
│
└── tests/                     # ← Integration + orchestrator tests
    ├── test_actions.py        # Tests for root actions.py (orchestrator, utilities)
    └── test_context.py        # Tests for context_extensions.py
```

## 5. workflow.toml Specification

```toml
[workflow]
name = "gen_media_content_v1"
version = "1.0.0"
label = "Media Content Generation v1"
job_prefix = "MEDIA"
description = "Unified media generation pipeline with pluggable prompts and API providers."
visibility = "canonical"
default_max_rejects = 3
init_step = "extract_descriptions"

layer = "layer3"
platform = "agent-runner-v2"

# Implementations (BCS) — each impl maps to a preset
[[workflow.implementation]]
name = "agnes_full"
description = "Full pipeline using Agnes APIs for both image and video"
label = "Agnes Full Pipeline"

[[workflow.implementation]]
name = "happyhorse_product"
description = "Product-focused pipeline: Agnes images + HappyHorse video"
label = "HappyHorse Product Pipeline"

[[workflow.implementation]]
name = "video_only"
description = "Video-only mode: skip LLM/image steps, render videos from existing images"
label = "Video Only"

[workflow.governance]
include_in_prompts = true
prompt_targets = ["all"]

# ─── Step 1: Extract Descriptions (LLM) ───
[[step]]
name = "extract_descriptions"
prompt = "{{ slot.extract_desc }}"
enable_notifications = true
requires_human_approval_after = false
onsuccess = "archive_step_00"

[step.artifacts]
produces = ["IMAGE_DESCRIPTIONS"]
result_meta_key = "IMAGE_DESCRIPTIONS"

[step.coder]
role_policy = "architect_standard"

[step.on_reject_refine]
step = "extract_descriptions"
artifact = "IMAGE_DESCRIPTIONS"
max_iterations = 1
exhausted_failure_code = "DESCRIPTION_EXTRACT_EXHAUSTED"
exhausted_failure_class = "HUMAN_RETRY_REQUIRED"

# ─── Step 1b: Archive step_00 ───
[[step]]
name = "archive_step_00"
action = "archive_inputs"
source_dir = "step_00_inputimage"
archive_dir = "step_00_inputimage_archive"
index_file = "step_01_imagedesc/index.json"
onsuccess = "generate_prompts"

[step.artifacts]
result_meta_key = "ARCHIVE_STEP_00"

# ─── Step 2: Generate Prompts (LLM) ───
[[step]]
name = "generate_prompts"
prompt = "{{ slot.generate_prompts }}"
enable_notifications = true
requires_human_approval_after = false
onsuccess = "archive_step_01"

[step.artifacts]
produces = ["PROMPT_VARIANTS"]
result_meta_key = "PROMPT_VARIANTS"

[step.coder]
role_policy = "image_video"

[step.on_reject_refine]
step = "generate_prompts"
artifact = "PROMPT_VARIANTS"
max_iterations = 1
exhausted_failure_code = "PROMPT_GENERATION_EXHAUSTED"
exhausted_failure_class = "HUMAN_RETRY_REQUIRED"

# ─── Step 2b: Archive step_01 ───
[[step]]
name = "archive_step_01"
action = "archive_inputs"
source_dir = "step_01_imagedesc"
archive_dir = "step_01_imagedesc_archive"
onsuccess = "generate_images"

[step.artifacts]
result_meta_key = "ARCHIVE_STEP_01"

# ─── Step 3: Render Images (Action) ───
[[step]]
name = "generate_images"
action = "generate_images_default"
enable_notifications = true
requires_human_approval_after = true
onsuccess = "archive_step_02"

[step.artifacts]
produces = ["IMAGE_INDEX"]
result_meta_key = "IMAGE_INDEX"

# ─── Step 3b: Archive step_02 ───
[[step]]
name = "archive_step_02"
action = "archive_inputs"
source_dir = "step_02_promptvariant"
archive_dir = "step_02_promptvariant_archive"
index_file = "step_03_generatedimage/index.json"
onsuccess = "generate_videos"

[step.artifacts]
result_meta_key = "ARCHIVE_STEP_02"

# ─── Step 4: Render Videos (Action) ───
[[step]]
name = "generate_videos"
action = "generate_videos_default"
enable_notifications = true
requires_human_approval_after = false
onsuccess = "archive_step_03"

[step.artifacts]
produces = ["VIDEO_INDEX"]
result_meta_key = "VIDEO_INDEX"

# ─── Step 4b: Archive step_03 ───
[[step]]
name = "archive_step_03"
action = "archive_inputs"
source_dir = "step_03_generatedimage"
archive_dir = "step_03_generatedimage_archive"
onsuccess = "stepCompletion"

[step.artifacts]
result_meta_key = "ARCHIVE_STEP_03"

# ─── Step 5: Completion ───
[[step]]
name = "stepCompletion"
action = "step_completion"
```

## 6. config.json.sample

```json
{
  "prompts": {
    "extract_desc": "standard",
    "generate_prompts": "standard"
  },
  "actions": {
    "render_image": "agnes_v1",
    "render_video": "happyhorse_v1_1"
  },
  "review_images_before_video": true,
  "api": {
    "agnes_v1": {
      "model": "agnes-image-2.1-flash",
      "size": "1024x1024",
      "ratio": "1:1"
    },
    "agnes_v2": {
      "model": "agnes-video-v2.0",
      "width": 1024,
      "height": 576,
      "num_frames": 72,
      "frame_rate": 24,
      "video_prompt_field": "t2v_prompt1",
      "video_prompt_prefix": "",
      "video_prompt_postfix": ""
    },
    "happyhorse_v1_1": {
      "model": "happyhorse-1.1-i2v",
      "resolution": "480P",
      "ratio": "9:16",
      "duration": 15
    }
  },
  "num_variants": 4,
  "max_concurrent": 2,
  "process_delay": 15,
  "coder_timeout": 900,
  "api_timeout": 500,
  "api_max_retries": 5,
  "retry_base_wait": 5
}
```

## 7. API Provider Contracts

Each provider exposes a `call_api()` function (not decorated with `@action`). The orchestrator in root `actions.py` calls it.

### 7.1 render_image (Agnes V1)
- **Function**: `call_api(prompt: str, config: dict) -> dict`
- **Returns**: `{"image_url": "...", "image_filename": "..."}`
- **Endpoint**: `POST {base_url}/v1/images/generations`
- **Config fields used**: `model`, `size`, `ratio`

### 7.2 render_video (Agnes V2)
- **Function**: `call_api(prompt: str, image_path_or_url, config: dict) -> dict`
- **Returns**: `{"video_url": "...", "video_filename": "..."}`
- **Submit**: `POST {base_url}/v1/videos`
- **Poll**: `GET {base_url}/agnesapi?video_id=xxx`
- **Status**: `"completed"` / `"failed"`
- **Config fields used**: `model`, `width`, `height`, `num_frames`, `frame_rate`, `negative_prompt`

### 7.3 render_video (HappyHorse V1.1)
- **Function**: `call_api(prompt: str, image_path_or_url, config: dict) -> dict`
- **Returns**: `{"video_url": "...", "video_filename": "..."}`
- **Submit**: `POST {base_url}/api/v1/services/aigc/video-generation/video-synthesis` (with `X-DashScope-Async: enable` header)
- **Poll**: `GET {base_url}/api/v1/tasks/{task_id}`
- **Status**: `"SUCCEEDED"` / `"FAILED"`
- **Config fields used**: `model`, `resolution`, `ratio`, `duration`

### 7.4 render_video (__none__ / Skip)
- **Function**: `call_api() -> dict`
- **Returns**: `{"skipped": True}`
- **Purpose**: Allows user to skip video generation via dropdown selection.

### 7.5 Common Provider Interface
All providers must conform to this interface:
```python
def call_api(
    prompt: str,
    image: str | Path | None = None,  # URL string, local path, or None
    config: dict = {},
    api_key: str = "",
    base_url: str = "",
) -> dict:
    """Call the provider's API. Returns result dict or raises RuntimeError."""
    ...
```

## 8. BCS Preset Format

### 8.1 impl.yaml
```yaml
name: <preset_name>
description: "<human description>"
overrides:
  generate_images:
    action: "generate_images_default"
  generate_videos:
    action: "generate_videos_default"
```

### 8.2 preset.json
```json
{
  "name": "<preset_name>",
  "label": "<UI display label>",
  "defaults": {
    "prompts": {
      "extract_desc": "<prompt_name>",
      "generate_prompts": "<prompt_name>"
    },
    "actions": {
      "render_image": "<provider_name>",
      "render_video": "<provider_name>"
    },
    "review_images_before_video": true,
    "api_config_overrides": {
      "<provider_key>": { ... }
    }
  }
}
```

## 9. Test Requirements

- **Every `@action` function** must have a corresponding unit test.
- **Every prompt template** must have a test verifying slot variable substitution works.
- **config.json loading** must be tested (valid, missing fields, invalid values).
- **`__none__` action** must be tested (returns APPROVED, no side effects).
- Tests must run with `pytest` from the workflow directory.
- Tests must NOT require real API keys (use mocks).

## 10. Constraints

- Do NOT modify existing workflows (`agnes_media_gen_v1`, `agnes_gen_video_v1`). This is a new package.
- API provider functions must be pure — no directory scanning, no JSON parsing, no orchestration.
- Orchestrator logic (directory scanning, JSON parsing, batching, index writing) stays in root `actions.py`.
- All shared utilities (`_api_request_with_retry`, `_write_index`, etc.) stay in root `actions.py`.
- BCS compliance: `impl.yaml` follows the existing BCS contract format.
- Every provider must export `call_api()` as its public interface.
- Provider `__init__.py` must be importable without side effects (no env loading, no network calls at import time).
