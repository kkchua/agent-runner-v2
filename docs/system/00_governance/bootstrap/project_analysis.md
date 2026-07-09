---
template_id: "SYS-00-PA"
managed_by: workflow-generated
generated: "2026-07-09T21:14:38+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "02_generate_project_analysis"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `02_generate_project_analysis`
> This file is workflow-generated and protected from manual edits.

# Project Analysis: agent-runner-v2

## Repo Overview

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine extracted from UKBE. It runs structured multi-step workflows across Claude, Codex, Qwen, and aliased models, with review loops, retries, approval gates, and deterministic runner actions.

The package provides a CLI entry point `ukbe-run-agent` that supports three primary usage modes:
- **Local workflow execution** (`run`): Manual execution with prompt rendering and step routing
- **Backend-connected execution** (`worker`, `poll`, `execute-step`): Worker mode for backend-driven step execution
- **Daemon supervision** (`daemon`): Workstation supervisor that claims work and spawns child processes

The runtime loads workflow definitions from `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`, not directly from the repo tree. The packaged bootstrap source in `agent_runner_v2/bootstrap/workflows/default/` exists only to seed those global workflow bundles.

## Codebase Structure

### Package Layout (`agent_runner_v2/`)

| Module | Responsibility |
|--------|---------------|
| `run_agent.py` | CLI entry point and top-level orchestration (~2,300 lines) |
| `step_runner.py` | Prompt rendering, sidecar validation, artifact checks (~2,400 lines) |
| `workflow_router.py` | Post-step routing for approve/reject/failure cases (~800 lines) |
| `job_state.py` | `job.json` lifecycle management (~1,800 lines) |
| `coder_adapters.py` | Claude/Codex/Qwen invocation and polling (~1,000 lines) |
| `constants.py` | Centralized artifact path constants and path generation (~1,000 lines) |
| `runtime_context.py` | Active workflow/runtime path context |
| `bundle_loader.py` | Bootstrap seeding and workflow bundle loading |
| `documentation_guardrails.py` | Generated doc manifest and protection |

### Actions Package (`agent_runner_v2/actions/`)

29 deterministic runner actions including:
- Documentation: `validate_delivery_docs.py`, `validate_codebase_docs.py`, `sync_system_docs.py`
- Architecture site: `generate_site.py`, `publish_architecture_site.py`, `validate_*_site.py`
- Bootstrap: `prepare_delivery_scaffold.py`, `finalize_bootstrap.py`, `scan_repo_codebase.py`
- Media: `execute_t2i.py`, `execute_i2v.py`, `execute_voiceover.py`, `assemble_video.py`

### Bootstrap Assets (`agent_runner_v2/bootstrap/`)

- `workflows/default/`: Workflow definitions, template groups, prompts
- `bundles/core/current/`: Core bundle with master system docs, templates, SOPs
- `themes/default/`: HTML themes for architecture site generation

### Tests (`tests/`)

Split structure:
- `tests/unit/`: Pure logic tests (isolated, no filesystem dependencies)
- `tests/integration/`: Integration tests with real files, external systems, subprocesses

### Documentation (`docs/`)

- `docs/codebase/`: Codebase documentation (inventory, modules, components, changes)
- `docs/operations/`: Operational guides (daemon quickstart, workflow SOP)

## Workflow and Runtime Model

### Core Execution Model

Each workflow step follows a strict v2 contract:

1. Load the active workflow bundle from `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`
2. Render a prompt from the bundle prompt template with context substitution
3. Invoke a coder (Claude Code, Codex CLI, Qwen Code) or execute a deterministic action
4. Read the `meta.json` sidecar written by the step — this is the **only** structured result channel
5. Validate artifacts against expected paths
6. Route to the next step based on sidecar status (APPROVED/REJECTED) and retry limits

### Key v2 Differences from v1

- **No markdown write-backs**: Runner does not write to markdown files (no `sync_review_metadata`, `stamp_created_metadata`)
- **meta.json only**: Sidecar is the sole communication channel (no fallbacks, no stdout JSON parsing)
- **No pre-invocation sidecar writes**: Sidecar is written only by the coder, not the runner
- **No recovery functions**: Disk recovery functions removed; explicit failure routing only
- **Hard failures route explicitly**: `MetaJsonMissingError`, `MetaJsonInvalidError` go to `route_after_failure()` immediately
- **Coder owns content analysis**: `blocking_issues` is always `[]`; content analysis is the coder's job

### Coder/Action Split

- **Coders**: External LLM tools (Claude Code, Codex CLI, Qwen Code) invoked via `coder_adapters.py`
- **Actions**: Deterministic Python functions in `actions/` package executed directly by the runner
- **Invocation**: Both paths go through `run_step()`; coders via `invoke_coder()`, actions via `run_action()`

### Sidecar Contract

The `meta.json` sidecar must contain:
```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED" | "REJECTED",
    "remark": "Brief summary",
    "artifacts": {"ARTIFACT_KEY": "relative/path/to/file.md"},
    "recorded_at": "2026-07-09T21:14:38+08:00"
  }
}
```

Status decision rules:
- Return `APPROVED` only if ALL required artifacts exist on disk AND meta.json is written
- Return `REJECTED` if any artifact is missing or cannot be created
- Runner validates artifacts against expected paths before routing

### Bootstrap/Runtime Distinction

| Aspect | Bootstrap Source | Runtime Bundle |
|--------|-----------------|----------------|
| Location | `agent_runner_v2/bootstrap/workflows/default/` | `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\` |
| Purpose | Package-local seed/template | Active execution source |
| Updates | Via code changes + sync | Used by running workflows |
| Loading | `bundle_loader.py` | `runtime_context.py` |

**Critical**: Changes to bootstrap workflow files (`template_groups.py`, constants) must be synced to the global runner home before they take effect in prompts.

## Operational Risks

### 1. Bootstrap/Runtime Bundle Sync Gap

**Risk**: Changes to `template_groups.py` or prompt templates in the repo are not automatically reflected in runtime execution. The runtime loads from `%USERPROFILE%\.ukbe-runner\workflows\default\`, not the repo.

**Mitigation**: Run sync scripts (`sync-workflows-to-backend.bat`, `sync-10_execution_scaffold_v1-workflow-spec.bat`) after modifying bootstrap files.

### 2. Windows Path Handling Edge Cases

**Risk**: Windows `pathlib.Path.relative_to()` can fail even for valid subpaths, requiring `os.path.relpath()` fallback in `_safe_relative_to()`.

**Evidence**: `run_agent.py` contains `_safe_relative_to()` helper for Windows compatibility.

### 3. External Coder Tool Dependency

**Risk**: Runtime depends on external CLI tools (Claude Code, Codex CLI, Qwen Code) being installed and accessible. No bundled fallback.

**Impact**: Worker mode failures if target workstation lacks required coder.

### 4. Job State Schema Version Drift

**Risk**: Job state schema version 6 (v2) may not be backward compatible with v1 jobs. Migration path exists but must be executed.

**Evidence**: `CURRENT_SCHEMA_VERSION = 6` in `job_state.py`; `migrate_job_state()` function present.

### 5. Daemon Child Process Management

**Risk**: Daemon spawns fresh subprocesses for each step execution; child process failures must be tracked and reported via heartbeat.

**Impact**: Orphaned processes or missed heartbeats can leave jobs in `IN_PROGRESS` state indefinitely.

### 6. Placeholder Resolution Ordering

**Risk**: Workflow prompt placeholders (e.g., `{PROJECT_ANALYSIS}`) are resolved from `ARTIFACT_KEYS` + `known_artifact_paths()`, not `REFERENCE_FILES`. Misconfiguration can leave placeholders unresolved.

**Evidence**: Memory confirms this was a past issue causing unresolved `{DELIVERY_AGENT_PLANNER}` tokens.

## Architectural Observations

### 1. Centralized Constants Architecture

All documentation paths use a layered constant system in `constants.py`:
- `ARTIFACT_KEY_*` constants define canonical artifact keys
- `FOLDER_KEY_*` constants define folder locations
- `known_artifact_paths()` provides path mapping regardless of artifact existence
- Zero hardcoded path strings in validation logic

This prevents the previous fragmentation where paths were scattered across modules.

### 2. Strict Separation of Concerns

- `step_runner.py`: Only prompt rendering and sidecar validation
- `workflow_router.py`: Only post-step routing decisions
- `job_state.py`: Only job.json lifecycle
- `coder_adapters.py`: Only external coder invocation
- `actions/`: Only deterministic actions

No module exceeds ~2,500 lines; responsibilities are narrowly scoped.

### 3. Generated Document Protection

Workflow-generated documents carry:
- YAML frontmatter with `template_id`, `managed_by: workflow-generated`
- Protection banner after frontmatter
- Inventory tracking in `documentation_guardrails.py`

This prevents manual edits to generated docs and enables cleanup/refreshes.

### 4. Test Structure Separation

Tests are explicitly split:
- `tests/unit/`: Pure logic, isolated, no filesystem dependencies
- `tests/integration/`: Real files, external systems, subprocesses

This aligns with pytest markers and enables targeted test execution.

### 5. Batch File Workflow Launchers

34 `.bat` files provide Windows-native workflow launching:
- `run-00_master_docs_bootstrap_v1.bat` through `run-55_user_docs_v1.bat`
- `submit-*.bat` for backend submission
- `run-tests.bat`, `run-integration-tests.bat`, `run-all-tests.bat`

This suggests Windows is the primary development/deployment platform.

## Architecture Posture

| Attribute | Value |
|-----------|-------|
| **current_profile** | `explicit` |
| **target_profile** | `universal-bootstrap` |
| **migration_mode** | `maintenance` |
| **repo_state** | `explicit` |

### Evidence Sources

1. **Comprehensive workflow definitions**: `template_groups.py` defines 12+ workflow families (initiative_intake_v1, delivery_planning_v1, task_execution_v1, documentation_sync_v1, architecture_site_v1, etc.)

2. **Strict v2 contract enforcement**: Code explicitly rejects v1 patterns (no markdown write-backs, no recovery functions, meta.json only)

3. **Centralized constants**: `constants.py` with 100+ artifact keys and pre-computed path mappings

4. **Bootstrap bundle structure**: `agent_runner_v2/bootstrap/bundles/core/current/` contains master system docs, templates, SOPs

5. **Generated doc protection**: `documentation_guardrails.py` with manifest tracking and protection banners

6. **Test infrastructure**: 109+ unit tests with strict separation from integration tests

### Posture Assessment

The repository is **explicit** — it declares its architecture standard clearly through:
- Documented v2 execution model in QWEN.md
- Centralized constants with zero hardcoded paths
- Generated doc protection with workflow attribution
- Strict separation between bootstrap source and runtime bundles

The `target_profile` of `universal-bootstrap` reflects the intent to provide a reusable workflow orchestration system across multiple repos, not just a one-off tool.

## Unresolved Documentation Gaps

1. **Workflow Bundle Sync Procedure**: No single document describes the complete workflow for syncing bootstrap changes to runtime bundles (existence of batch files implies this is tribal knowledge).

2. **Daemon Operational Guide**: While `docs/operations/DAEMON_MODE_QUICKSTART.md` exists, comprehensive daemon troubleshooting (child process debugging, heartbeat diagnostics) is not fully documented.

3. **Backend API Contract**: The backend alignment design notes exist but the full API contract for `worker`, `poll`, `execute-step` modes is not documented in the system docs.

4. **Coder Timeout Configuration**: Cascading timeout priority (step override → env var → config.json → default) is in code but not prominently documented.

5. **Failure Mode Taxonomy**: `CONTROL_CLASSES` (`AUTO_RETRYABLE`, `HUMAN_RETRY_REQUIRED`, `FATAL`) and `FAILURE_SOURCES` exist in code but lack comprehensive documentation for operators.

6. **Architecture Site Generation**: The HTML site generation process (themes, layout.html, PDF generation) is implemented but not documented in system docs.

7. **Bundle Migration Procedures**: `BUNDLE_MIGRATION_PLAN.md` exists but migration procedures for existing workspaces are not fully operationalized.
