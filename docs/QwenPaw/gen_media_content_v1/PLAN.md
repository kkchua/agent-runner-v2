# Implementation Plan: gen_media_content_v1

## Phases

### Phase 1: Scaffolding + workflow.toml + context
- **Scope:** Directory structure, workflow.toml, context_extensions.py, config samples
- **Deliverables:**
  - All directories and __init__.py files
  - workflow.toml (with {{ slot.* }} syntax, BCS impl declarations)
  - context_extensions.py (provides STEP_00_DIR through STEP_04_DIR, MEDIA_CONFIG)
  - config.json.sample, .env.sample, README.md (stubs)
- **Tests:** workflow.toml parses correctly, context_extensions.py produces correct keys
- **Acceptance:** workflow.toml validates, no Python errors in context_extensions.py

### Phase 2: Root actions.py — Shared Utilities + Orchestrator Stubs
- **Scope:** Root actions.py with utilities and placeholder orchestrator actions
- **Deliverables:**
  - Shared utilities: _load_config, _api_request_with_retry, _write_index, _get_next_sequence_filename, import_provider
  - @action("generate_images_default") — placeholder (REJECTED with "no provider selected")
  - @action("generate_videos_default") — placeholder (REJECTED with "no provider selected")
- **Tests:** Utilities work correctly (retry logic, index writing, config loading, provider import)
- **Acceptance:** All utility tests pass. Orchestrator stubs return correct REJECTED result when no provider configured.

### Phase 3: API Provider — render_image (agnes_v1)
- **Scope:** api_actions/render_image/agnes_v1/ with pure call_api()
- **Deliverables:**
  - api_actions/render_image/__init__.py (registry)
  - api_actions/render_image/agnes_v1/__init__.py (exports call_api)
  - Unit tests with mocked HTTP
- **Acceptance:** Provider returns correct result dict from mocked response. No side effects.

### Phase 4: API Provider — render_video (agnes_v2)
- **Scope:** api_actions/render_video/agnes_v2/ with pure call_api()
- **Deliverables:**
  - api_actions/render_video/__init__.py (registry)
  - api_actions/render_video/agnes_v2/__init__.py (exports call_api with submit + poll)
  - Unit tests with mocked HTTP (submit response + poll response)
- **Acceptance:** Provider correctly submits, polls, and returns video URL from mocked responses.

### Phase 5: API Provider — render_video (happyhorse_v1_1)
- **Scope:** api_actions/render_video/happyhorse_v1_1/ with pure call_api() (DashScope style)
- **Deliverables:**
  - api_actions/render_video/happyhorse_v1_1/__init__.py (exports call_api with DashScope endpoints)
  - Unit tests with mocked HTTP
- **Acceptance:** Provider uses DashScope endpoints, correct headers, correct payload format, correct status polling.

### Phase 6: API Provider — render_video (__none__ / skip)
- **Scope:** api_actions/render_video/__none__/
- **Deliverables:**
  - api_actions/render_video/__none__/__init__.py (exports call_api returning skip marker)
  - Unit tests
- **Acceptance:** Returns {"skipped": True}. No side effects, no HTTP calls.

### Phase 7: LLM Prompts
- **Scope:** prompts/ directory with default prompt templates
- **Deliverables:**
  - prompts/extract_desc/standard.txt (adapted from existing agnes_media_gen_v1 step 1 prompt)
  - prompts/generate_prompts/standard.txt (adapted from existing agnes_media_gen_v1 step 2 prompt)
  - Tests verifying slot variable substitution
- **Acceptance:** Prompts render correctly when slot variables are replaced.

### Phase 8: BCS Impls (Presets)
- **Scope:** impls/ directory with preset bundles
- **Deliverables:**
  - impls/agnes_full/ (impl.yaml + preset.json)
  - impls/happyhorse_product/ (impl.yaml + preset.json)
  - impls/video_only/ (impl.yaml + preset.json)
- **Acceptance:** YAML and JSON are valid. impl.yaml maps to orchestrator action names. preset.json has correct defaults.

### Phase 9: Wire Orchestrator + Integration
- **Scope:** Connect everything — orchestrator dispatches to providers, handles batching
- **Deliverables:**
  - Updated generate_images_default in root actions.py — reads config, imports provider, scans dirs, batches, writes index.json
  - Updated generate_videos_default in root actions.py — same pattern
  - Integration tests (full mock pipeline run)
- **Acceptance:** Full mock run from variant JSONs → images → videos passes. Index files are correct.

## Workflow

For each phase:
1. Give opencode a focused prompt with only what it needs for that phase
2. Run from repo root: D:\MyProjectSpace\01_Workflows\agent-runner-v2\
3. Review code, run tests, verify against requirements
4. If passes → proceed to next phase
5. If fails → investigate, ask opencode to fix

## Status
- [ ] Phase 1
- [ ] Phase 2
- [ ] Phase 3
- [ ] Phase 4
- [ ] Phase 5
- [ ] Phase 6
- [ ] Phase 7
- [ ] Phase 8
- [ ] Phase 9
