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
effective_version: "SDLC50IMP-99xhlzti"
managed_by: "workflow-generated"
---

# Implementation Plan: gen_media_content_v1 Phase 1 Scaffolding

## Implementation Overview

This plan covers the creation of the initial scaffolding for the gen_media_content_v1
workflow package. The scope is strictly structural: directory skeleton, workflow.toml
manifest, context_extensions.py, sample configuration files, sample environment
variables, README documentation, and unit tests. No implementation code (actions.py,
prompt templates, API provider modules) is produced in this phase.

The deliverable is a valid, parseable workflow package that the agent-runner-v2
workflow system can load, following the same patterns established by the reference
workflow agnes_media_gen_v1.

## Task Traceability

| Item | Source | Traceability |
|---|---|---|
| TASK-20260814-001-01 | TASK file (approved) | Primary input artifact |
| AC-01 through AC-08 | TASK file, Acceptance Criteria | Validation targets |
| Work item WI-20260814-001-01 | TASK file, Document Metadata | Scope origin |

Acceptance criteria mapping:

| Criterion | Plan Section | Verification Method |
|---|---|---|
| AC-01: All directories with __init__.py | Step-by-Step Plan, Step 1 | Directory listing |
| AC-02: Valid workflow.toml with 9 steps, 3 implementations | Step-by-Step Plan, Step 2 | TOML parse validation |
| AC-03: Valid context_extensions.py producing 6 context keys | Step-by-Step Plan, Step 3 | Python parse + unit test |
| AC-04: Valid config.json.sample | Step-by-Step Plan, Step 4 | JSON parse validation |
| AC-05: Valid .env.sample | Step-by-Step Plan, Step 5 | File format check |
| AC-06: README.md with documentation | Step-by-Step Plan, Step 6 | File existence check |
| AC-07: Valid tests/test_context.py | Step-by-Step Plan, Step 7 | Python parse + pytest |
| AC-08: No existing files modified | Step-by-Step Plan (all steps) | git diff verification |

## Implementation Strategy

The strategy follows the established workflow package pattern:

1. **Reference-first approach**: Every file mirrors the structure of the reference
   workflow agnes_media_gen_v1 (workflow.toml, context_extensions.py, config.json.sample,
   .env.sample, README.md). Field names, class hierarchies, and TOML section ordering
   are copied from the reference and adapted to the new workflow name and scope.

2. **Isolation principle**: All new files are created exclusively under
   workflows/gen_media_content_v1/. No existing workflow files, core modules, or
   governance documents are modified. This satisfies AC-08.

3. **Incremental verification**: Each file is created with its own validation gate
   (TOML parse, Python syntax check, JSON parse) before proceeding to the next.
   This prevents cascading errors.

4. **Test-driven structural validation**: Unit tests are created alongside the
   context_extensions.py module, following the pattern in
   tests/unit/workflows/text_summarizer_ayz/test_context_extensions.py.

5. **Layer compliance**: The workflow.toml declares layer="layer3" and
   platform="agent-runner-v2" per the Layer 2 platform contract. Governance and
   platform runtime roots are treated as read-only context injection points,
   consistent with Layer 1 and Layer 2 boundaries.

## Step-by-Step Plan

### Step 1: Create Directory Structure

**Files created:**

- workflows/gen_media_content_v1/prompts/__init__.py
- workflows/gen_media_content_v1/prompts/extract_desc/__init__.py
- workflows/gen_media_content_v1/prompts/generate_prompts/__init__.py
- workflows/gen_media_content_v1/api_actions/__init__.py
- workflows/gen_media_content_v1/api_actions/render_image/__init__.py
- workflows/gen_media_content_v1/api_actions/render_video/__init__.py
- workflows/gen_media_content_v1/impls/__init__.py
- workflows/gen_media_content_v1/impls/agnes_full/__init__.py
- workflows/gen_media_content_v1/impls/happyhorse_product/__init__.py
- workflows/gen_media_content_v1/impls/video_only/__init__.py
- workflows/gen_media_content_v1/tests/__init__.py

**Notes:**

- All __init__.py files are empty, matching the convention in agnes_media_gen_v1.
- No __init__.py at the workflow root itself (workflows/ is not a Python package).
- Directory structure matches the TASK specification exactly.

**Acceptance:** AC-01 satisfied.

### Step 2: Create workflow.toml

**File created:** workflows/gen_media_content_v1/workflow.toml

**Structure:**

1. `[workflow]` header block:
   - name = "gen_media_content_v1"
   - version = "1.0.0"
   - label = "Media Content Generation v1"
   - job_prefix = "MEDIA"
   - visibility = "canonical"
   - init_step = "extract_descriptions"
   - layer = "layer3", platform = "agent-runner-v2"

2. Three `[[workflow.implementation]]` blocks:
   - agnes_full (full pipeline, Agnes APIs for image and video)
   - happyhorse_product (Agnes images + HappyHorse video)
   - video_only (skip LLM/image steps, render videos from existing images)

3. Nine `[[step]]` blocks in sequence:
   1. extract_descriptions (prompt-driven, role_policy="architect_standard",
      on_reject_refine self-loop)
   2. archive_step_00 (action=archive_inputs, source_dir=step_00_inputimage,
      archive_dir=step_00_inputimage_archive,
      index_file=step_01_imagedesc/index.json)
   3. generate_prompts (prompt-driven, role_policy="image_video",
      on_reject_refine self-loop)
   4. archive_step_01 (action=archive_inputs, source_dir=step_01_imagedesc,
      archive_dir=step_01_imagedesc_archive)
   5. generate_images (action=generate_images_default,
      requires_human_approval_after=true)
   6. archive_step_02 (action=archive_inputs, source_dir=step_02_promptvariant,
      archive_dir=step_02_promptvariant_archive,
      index_file=step_03_generatedimage/index.json)
   7. generate_videos (action=generate_videos_default)
   8. archive_step_03 (action=archive_inputs, source_dir=step_03_generatedimage,
      archive_dir=step_03_generatedimage_archive)
   9. stepCompletion (action=step_completion, terminal step)

**Validation:** Parse with `tomllib.load()` (Python 3.11+) to confirm valid TOML.

**Acceptance:** AC-02 satisfied.

### Step 3: Create context_extensions.py

**File created:** workflows/gen_media_content_v1/context_extensions.py

**Class structure:**

- Module docstring describing purpose
- Imports: `from __future__ import annotations`, `pathlib.Path`, `typing.Any`,
  runtime_context helpers, `WorkflowExtensions` base class
- Class `GenMediaContentExtensions(WorkflowExtensions)`:
  - `workflow_name = "gen_media_content_v1"`
  - `register_artifact_keys()`: returns dict mapping IMAGE_DESCRIPTIONS,
    PROMPT_VARIANTS, IMAGE_INDEX, VIDEO_INDEX to absolute paths
  - `build_context_extensions()`: returns dict with:
    - STEP_00_DIR through STEP_04_DIR (5 step directories)
    - STEP_00_ARCHIVE through STEP_04_ARCHIVE (5 archive directories)
    - MEDIA_CONFIG (config.json path)
    - GOVERNANCE_RUNTIME_ROOT (Layer 1 root)
    - PLATFORM_RUNTIME_ROOT (Layer 2 root)
    - All artifact key paths from register_artifact_keys()
  - `install_to_global()`: returns {"status": "NO_OP"}
  - `sync_to_backend()`: returns {"status": "NO_OP"}

**Notes:**

- Follows the exact pattern of agnes_media_gen_v1/context_extensions.py.
- Uses `get_workspace_root()`, `get_governance_runtime_root()`,
  `get_platform_runtime_root()` from `agent_runner_v2.runtime_context`.
- All paths are absolute, resolved from workspace_root.

**Validation:** Python syntax check via `importlib` or `ast.parse()`.

**Acceptance:** AC-03 satisfied.

### Step 4: Create config.json.sample

**File created:** workflows/gen_media_content_v1/config.json.sample

**Structure:**

```json
{
  "prompts": { "extract_desc": "standard", "generate_prompts": "standard" },
  "actions": { "render_image": "agnes_v1", "render_video": "happyhorse_v1_1" },
  "review_images_before_video": true,
  "api": {
    "agnes_v1": { "model": "...", "size": "...", "ratio": "..." },
    "agnes_v2": { "model": "...", "width": 1024, "height": 576, ... },
    "happyhorse_v1_1": { "model": "...", "resolution": "...", ... }
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

**Validation:** `json.loads()` to confirm valid JSON.

**Acceptance:** AC-04 satisfied.

### Step 5: Create .env.sample

**File created:** workflows/gen_media_content_v1/.env.sample

**Content:**

- AGNES_API_KEY_1= (placeholder)
- AGNES_BASE_URL=https://apihub.agnes-ai.com
- HAPPYHORSE_API_KEY_1= (placeholder)
- HAPPYHORSE_BASE_URL=https://dashscope.aliyuncs.com

**Acceptance:** AC-05 satisfied.

### Step 6: Create README.md

**File created:** workflows/gen_media_content_v1/README.md

**Content sections:**

- Overview (unified media generation with pluggable prompts and API providers)
- Directory structure overview (tree diagram)
- Configuration (environment variables + config.json sections)
- Implementations table (agnes_full, happyhorse_product, video_only)
- Prerequisites
- Usage command example

**Acceptance:** AC-06 satisfied.

### Step 7: Create tests/test_context.py

**File created:** workflows/gen_media_content_v1/tests/test_context.py

**Test classes and methods:**

- `TestContextExtensionKeys`:
  - test_step_dir_keys_present: verifies STEP_00_DIR through STEP_04_DIR
  - test_media_config_key_present: verifies MEDIA_CONFIG

- `TestContextExtensionPaths`:
  - test_step_dirs_use_workspace_root: verifies absolute paths rooted at
    workspace_root
  - test_media_config_path: verifies MEDIA_CONFIG points to config.json
  - test_archive_dirs_present: verifies STEP_00_ARCHIVE through STEP_04_ARCHIVE
  - test_governance_and_platform_roots: verifies governance/platform roots

- `TestArtifactKeyRegistration`:
  - test_artifact_keys_registered: verifies all 4 index.json artifact keys

**Pattern:** Follows tests/unit/workflows/text_summarizer_ayz/test_context_extensions.py
using `importlib.util.spec_from_file_location` for dynamic module loading,
`unittest.mock.patch` for runtime_context mocking.

**Validation:** `python -m pytest workflows/gen_media_content_v1/tests/test_context.py -v`

**Acceptance:** AC-07 satisfied.

## Code Changes

### Files to Create (13 total)

| File | Purpose | Lines (est.) |
|---|---|---|
| workflows/gen_media_content_v1/prompts/__init__.py | Empty package marker | 0 |
| workflows/gen_media_content_v1/prompts/extract_desc/__init__.py | Empty package marker | 0 |
| workflows/gen_media_content_v1/prompts/generate_prompts/__init__.py | Empty package marker | 0 |
| workflows/gen_media_content_v1/api_actions/__init__.py | Empty package marker | 0 |
| workflows/gen_media_content_v1/api_actions/render_image/__init__.py | Empty package marker | 0 |
| workflows/gen_media_content_v1/api_actions/render_video/__init__.py | Empty package marker | 0 |
| workflows/gen_media_content_v1/impls/__init__.py | Empty package marker | 0 |
| workflows/gen_media_content_v1/impls/agnes_full/__init__.py | Empty package marker | 0 |
| workflows/gen_media_content_v1/impls/happyhorse_product/__init__.py | Empty package marker | 0 |
| workflows/gen_media_content_v1/impls/video_only/__init__.py | Empty package marker | 0 |
| workflows/gen_media_content_v1/tests/__init__.py | Empty package marker | 0 |
| workflows/gen_media_content_v1/workflow.toml | Workflow manifest | ~187 |
| workflows/gen_media_content_v1/context_extensions.py | Context extensions module | ~143 |
| workflows/gen_media_content_v1/config.json.sample | Sample config | ~38 |
| workflows/gen_media_content_v1/.env.sample | Sample env vars | ~9 |
| workflows/gen_media_content_v1/README.md | Package documentation | ~98 |
| workflows/gen_media_content_v1/tests/test_context.py | Unit tests | ~206 |

### Files to Modify

None. All changes are additive under workflows/gen_media_content_v1/.

### Codebase Files Referenced (Read-Only)

| File | Purpose |
|---|---|
| workflows/agnes_media_gen_v1/workflow.toml | Reference TOML structure |
| workflows/agnes_media_gen_v1/context_extensions.py | Reference class pattern |
| workflows/agnes_media_gen_v1/config.json.sample | Reference config structure |
| workflows/agnes_media_gen_v1/.env.sample | Reference env format |
| workflows/agnes_media_gen_v1/README.md | Reference documentation |
| agent_runner_v2/workflow_packages/extensions_base.py | Base class API |
| agent_runner_v2/runtime_context.py | Runtime path resolution functions |
| agent_runner_v2/runner_actions.py | Available action registry |
| tests/unit/workflows/text_summarizer_ayz/test_context_extensions.py | Test pattern reference |

## Testing Strategy

### Validation Gates

Each file has a specific validation gate:

1. **Python files** (context_extensions.py, test_context.py):
   - Syntax check: `python -c "import ast; ast.parse(open('file').read())"`
   - Import check: `python -c "import workflows.gen_media_content_v1.context_extensions"`

2. **TOML file** (workflow.toml):
   - Parse check: `python -c "import tomllib; tomllib.load(open('file', 'rb'))"`

3. **JSON file** (config.json.sample):
   - Parse check: `python -c "import json; json.load(open('file'))"`

4. **Unit tests** (test_context.py):
   - Execution: `python -m pytest workflows/gen_media_content_v1/tests/test_context.py -v`
   - All tests must pass with 0 failures.

5. **No-modification check**:
   - `git status` to confirm only new files under workflows/gen_media_content_v1/

### Test Coverage

The test file covers:

- Presence of all 5 STEP_*_DIR keys (STEP_00_DIR through STEP_04_DIR)
- Presence of MEDIA_CONFIG key
- Correct path construction from workspace_root for all step directories
- Correct path for config.json
- Presence of all archive directory keys
- Governance and platform runtime root injection
- Artifact key registration (4 index.json paths)

## Test Implementation

The following test code implements the test scope defined in the TASK file.
This is the content for workflows/gen_media_content_v1/tests/test_context.py:

```python
"""Unit tests for gen_media_content_v1 context extensions.

Verifies that context_extensions.py produces the expected keys and
constructs paths correctly from workspace_root.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest


def _load_context_extensions_module():
    """Load the context_extensions module from the workflow package.

    Path calculation: this test file lives at
        workflows/gen_media_content_v1/tests/test_context.py
    which is 3 levels below the repo root (parents[0]=tests,
    parents[1]=gen_media_content_v1, parents[2]=workflows,
    parents[3]=repo root). This differs from the reference pattern in
    tests/unit/workflows/text_summarizer_ayz/test_context_extensions.py
    which uses parents[4] because that file is 4 levels deep
    (tests/unit/workflows/<name>/).
    """
    module_path = (
        Path(__file__).resolve().parents[3]
        / "workflows"
        / "gen_media_content_v1"
        / "context_extensions.py"
    )
    spec = importlib.util.spec_from_file_location(
        "gen_media_content_v1.context_extensions", module_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to load context_extensions module from {module_path}"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestContextExtensionKeys:
    """Verify all expected context keys are produced."""

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_step_dir_keys_present(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """All 5 STEP_*_DIR keys are present in the context."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        ext = context_ext.GenMediaContentExtensions()
        result = ext.build_context_extensions(
            state={}, step="test", step_cfg={}, ctx={}
        )

        expected_dir_keys = [
            "STEP_00_DIR",
            "STEP_01_DIR",
            "STEP_02_DIR",
            "STEP_03_DIR",
            "STEP_04_DIR",
        ]
        for key in expected_dir_keys:
            assert key in result, f"Missing expected key: {key}"

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_media_config_key_present(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """MEDIA_CONFIG key is present in the context."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        ext = context_ext.GenMediaContentExtensions()
        result = ext.build_context_extensions(
            state={}, step="test", step_cfg={}, ctx={}
        )

        assert "MEDIA_CONFIG" in result


class TestContextExtensionPaths:
    """Verify paths are constructed correctly from workspace_root."""

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_step_dirs_use_workspace_root(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """Step directory paths are absolute and rooted at workspace_root."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        ext = context_ext.GenMediaContentExtensions()
        result = ext.build_context_extensions(
            state={}, step="test", step_cfg={}, ctx={}
        )

        expected_mappings = {
            "STEP_00_DIR": "step_00_inputimage",
            "STEP_01_DIR": "step_01_imagedesc",
            "STEP_02_DIR": "step_02_promptvariant",
            "STEP_03_DIR": "step_03_generatedimage",
            "STEP_04_DIR": "step_04_generatedvideo",
        }
        for key, dirname in expected_mappings.items():
            expected_path = str(workspace_root / dirname)
            assert result[key] == expected_path, (
                f"{key}: expected {expected_path}, got {result[key]}"
            )

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_media_config_path(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """MEDIA_CONFIG points to config.json in workspace_root."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        ext = context_ext.GenMediaContentExtensions()
        result = ext.build_context_extensions(
            state={}, step="test", step_cfg={}, ctx={}
        )

        expected_config = str(workspace_root / "config.json")
        assert result["MEDIA_CONFIG"] == expected_config

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_archive_dirs_present(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """Archive directory keys are also present for completeness."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        ext = context_ext.GenMediaContentExtensions()
        result = ext.build_context_extensions(
            state={}, step="test", step_cfg={}, ctx={}
        )

        expected_archive_keys = [
            "STEP_00_ARCHIVE",
            "STEP_01_ARCHIVE",
            "STEP_02_ARCHIVE",
            "STEP_03_ARCHIVE",
            "STEP_04_ARCHIVE",
        ]
        for key in expected_archive_keys:
            assert key in result, f"Missing expected archive key: {key}"

    @patch("agent_runner_v2.runtime_context.get_governance_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_platform_runtime_root")
    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_governance_and_platform_roots(self, mock_get_ws, mock_get_platform, mock_get_gov):
        """Governance and platform runtime roots are injected."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)
        mock_get_gov.return_value = Path("D:/Governance")
        mock_get_platform.return_value = Path("D:/Platform")

        ext = context_ext.GenMediaContentExtensions()
        result = ext.build_context_extensions(
            state={}, step="test", step_cfg={}, ctx={}
        )

        assert result["GOVERNANCE_RUNTIME_ROOT"] == str(Path("D:/Governance"))
        assert result["PLATFORM_RUNTIME_ROOT"] == str(Path("D:/Platform"))


class TestArtifactKeyRegistration:
    """Verify register_artifact_keys produces expected mappings."""

    @patch("agent_runner_v2.runtime_context.get_workspace_root")
    def test_artifact_keys_registered(self, mock_get_ws):
        """All 4 index.json artifact keys are registered."""
        context_ext = _load_context_extensions_module()

        workspace_root = Path("D:/TestWorkspace")
        mock_get_ws.return_value = str(workspace_root)

        ext = context_ext.GenMediaContentExtensions()
        keys = ext.register_artifact_keys()

        expected_keys = {
            "IMAGE_DESCRIPTIONS": f"{workspace_root}/step_01_imagedesc/index.json",
            "PROMPT_VARIANTS": f"{workspace_root}/step_02_promptvariant/index.json",
            "IMAGE_INDEX": f"{workspace_root}/step_03_generatedimage/index.json",
            "VIDEO_INDEX": f"{workspace_root}/step_04_generatedvideo/index.json",
        }
        assert keys == expected_keys
```

## Rollback Plan

Since all changes are purely additive (new files under a new directory), rollback
is straightforward:

1. **Delete the entire directory**: `rmdir /s /q workflows\gen_media_content_v1`
   removes all created files in one operation.

2. **No state modification**: No existing files, database records, or runtime
   state are altered. The workflow package is isolated until it is explicitly
   registered via `ukbe-run-agent sync-workflows`.

3. **Git-based rollback**: If files were committed, `git revert` on the commit
   that added the directory restores the previous state.

4. **No cascading impact**: The workflow package has no dependencies from other
   modules. Removing it does not break any existing functionality.

## Dependencies

### External Dependencies

| Dependency | Purpose | Status |
|---|---|---|
| Python 3.12+ | Runtime for workflow package validation | Available (.venv) |
| tomllib (stdlib) | TOML parsing validation | Available (Python 3.11+) |
| pytest | Unit test execution | Available (dev dependency) |
| agent_runner_v2 package | Base class imports (WorkflowExtensions) | Available (editable install) |

### Prerequisites from Prior Workflows

| Dependency | Source | Status |
|---|---|---|
| WorkflowExtensions base class | agent_runner_v2.workflow_packages.extensions_base | Verified present |
| Runtime context functions | agent_runner_v2.runtime_context | Verified present |
| archive_inputs action | agent_runner_v2.actions.archive_inputs | Verified registered |
| step_completion action | agent_runner_v2.actions.step_completion | Verified registered |
| generate_images_default action | agnes_media_gen_v1/actions.py | Available in bootstrap |
| generate_videos_default action | agnes_media_gen_v1/actions.py | Available in bootstrap |

### Platform Dependencies

| Dependency | Layer | Notes |
|---|---|---|
| Layer 2 platform contract | Layer 2 (read-only) | workflow.toml declares layer="layer3", platform="agent-runner-v2" |
| Layer 1 governance metadata | Layer 1 (read-only) | METADATA_STANDARD.md governs document frontmatter |

## Open Questions

1. **OQ-01: actions.py timing** -- The TASK specifies no implementation code in
   Phase 1. The actions.py module (containing generate_images_default and
   generate_videos_default implementations) is deferred to Phase 2. The current
   bootstrap copy in agnes_media_gen_v1/actions.py provides these actions at
   runtime. Confirmation needed: should gen_media_content_v1 have its own
   actions.py in Phase 2 that imports from or duplicates the bootstrap actions?

2. **OQ-02: Prompt template content** -- The workflow.toml references
   `{{ slot.extract_desc }}` and `{{ slot.generate_prompts }}` but no prompt
   template files exist yet in prompts/extract_desc/ or prompts/generate_prompts/.
   These are deferred to a subsequent phase. The workflow will fail at runtime
   if these slots are not populated before execution.

3. **OQ-03: Implementation preset content** -- The impls/ subdirectories
   (agnes_full, happyhorse_product, video_only) contain only __init__.py files.
   The actual preset configuration that maps dropdown values to provider
   selections is deferred. How should implementations be wired into the runtime
   config resolution?

4. **OQ-04: Backend registration** -- The workflow.toml is created but not yet
   registered with the backend. The `ukbe-run-agent sync-workflows` command must
   be run after the package is complete. This is an operational step, not an
   implementation concern.

## Assumptions

- A-01: The reference workflow agnes_media_gen_v1 is the canonical pattern for
  directory structure, TOML schema, and class hierarchy. All new files follow
  its conventions exactly unless the TASK specifies otherwise.
- A-02: The runtime_context module API (get_workspace_root, get_governance_runtime_root,
  get_platform_runtime_root) is stable and its function signatures have not changed
  since the reference workflow was created.
- A-03: The WorkflowExtensions base class in agent_runner_v2.workflow_packages.extensions_base
  is the correct inheritance target, as confirmed by reading the source code.
- A-04: Action names used in workflow.toml (archive_inputs, step_completion,
  generate_images_default, generate_videos_default) must match entries in the
  runner_actions.py ACTION_REGISTRY. All four were verified present.
- A-05: The target workspace structure (step_00_inputimage through
  step_04_generatedvideo) will be created in the target repository by the
  operator before workflow execution. The workflow package itself does not
  create these directories.

## Critique Resolution

### Finding 1 (M-01): Test Path Resolution Pattern

**Critique summary:** The critique noted that `parents[2]` is used in
`_load_context_extensions_module()` while the reference test in
tests/unit/workflows/text_summarizer_ayz/test_context_extensions.py uses
`parents[4]`. The critique recommended adding a comment to clarify the path
calculation for future maintainers.

**Evaluation:** Partially valid. Code verification revealed that `parents[2]`
was actually incorrect. The test file at
`workflows/gen_media_content_v1/tests/test_context.py` is 3 levels below the
repo root, not 2. The correct index is `parents[3]` (parents[0]=tests,
parents[1]=gen_media_content_v1, parents[2]=workflows, parents[3]=repo root).
Using `parents[2]` would resolve to the `workflows/` directory, producing an
incorrect path of `workflows/workflows/gen_media_content_v1/context_extensions.py`.
The critique reviewer incorrectly concluded that `parents[2]` was correct for
this file location.

**Resolution:** Corrected `parents[2]` to `parents[3]` in the test code block
(Test Implementation section). Added a detailed docstring comment to
`_load_context_extensions_module()` explaining the path calculation and the
difference from the `parents[4]` pattern used in tests/unit/ tests.

**Affected section:** Test Implementation (function `_load_context_extensions_module`,
previously lines 363-370).

### Finding 2 (M-02): TOML Validation Python Version

**Critique summary:** The critique noted that `tomllib.load()` requires Python
3.11+ and recommended documenting the Python version requirement explicitly.

**Evaluation:** Already addressed. The critique itself acknowledged that the
current documentation is acceptable and stated "No change required." The
implementation plan already specifies "Parse with `tomllib.load()` (Python 3.11+)"
at Step 2 validation (line 142). The Dependencies section (External Dependencies
table) also explicitly lists "Python 3.12+" as a dependency with status
"Available (.venv)". The project uses Python 3.12+ per AGENTS.md, which exceeds
the Python 3.11+ minimum for `tomllib`.

**Resolution:** No change made. The documentation is sufficient as-is.

**Affected section:** None.
