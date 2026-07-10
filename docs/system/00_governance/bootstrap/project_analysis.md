---
template_id: "SYS-00-PA"
title: "Project Analysis - agent-runner-v2"
status: "active"
generated: "2026-07-10T14:01:15+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "02_generate_project_analysis"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `02_generate_project_analysis`
> This file is workflow-generated and protected from manual edits.

# Repo Overview

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine extracted from UKBE (Unified Knowledge Base Environment). It provides structured multi-step workflow execution across Claude, Codex, Qwen, and aliased models, with built-in review loops, retry mechanisms, approval gates, and deterministic runner actions.

The package exposes a CLI entry point `ukbe-run-agent` that supports three primary execution modes:

1. **Manual workflow execution** (`ukbe-run-agent run`) - Local workflow execution with prompt rendering and coder invocation
2. **Backend-connected worker** (`ukbe-run-agent worker`, `poll`, `execute-step`) - Worker mode for backend-driven execution
3. **Daemon supervisor** (`ukbe-run-agent daemon`) - Workstation supervisor that claims work and spawns child processes

The runtime follows a v2 execution model where `meta.json` sidecar files are the sole structured communication channel between coders and the runner, eliminating markdown write-backs and silent recovery paths.

# Codebase Structure

## Package Layout

```
agent_runner_v2/                    # Main Python package
├── __init__.py                     # Package stub
├── run_agent.py                    # CLI entry point (2,374 lines)
├── step_runner.py                  # Core step execution (2,674 lines)
├── workflow_router.py              # Post-step routing (787 lines)
├── job_state.py                    # Job.json lifecycle (1,806 lines)
├── coder_adapters.py               # Coder invocation (1,079 lines)
├── constants.py                    # Centralized path constants (1,342 lines)
├── bundle_loader.py                # Bootstrap/runtime bundle loading
├── runtime_context.py              # Runtime path context
├── actions/                        # 28 deterministic runner actions
│   ├── __init__.py
│   ├── archive_previous_version.py
│   ├── assemble_video.py
│   ├── copy_artifact.py
│   ├── documentation_validation_core.py
│   ├── execute_i2v.py
│   ├── execute_t2i.py
│   ├── execute_voiceover.py
│   ├── finalize_bootstrap.py
│   ├── generate_site.py
│   ├── generate_site_pdf.py
│   ├── prepare_delivery_scaffold.py
│   ├── promote_artifact.py
│   ├── promote_init.py
│   ├── publish_architecture_site.py
│   ├── scan_repo_codebase.py
│   ├── submit_comfyui.py
│   ├── sync_codebase_docs.py
│   ├── sync_system_docs.py
│   ├── validate_*.py               # 12 validation actions
│   └── ...
├── bootstrap/                      # Bootstrap source (seeds runtime)
│   ├── bundles/core/current/       # Core documentation bundles
│   ├── themes/default/             # HTML theme templates
│   └── workflows/default/          # Default workflow definitions
│       ├── template_groups.py      # 2,453-line workflow registry
│       ├── prompts/                # 200+ prompt templates
│       └── *.json                  # Schema and mapping files
├── workflow_packages/              # Plugin-based workflow system
│   ├── __init__.py
│   ├── base.py
│   ├── loader.py
│   └── registry.py
└── tools/                          # Development utilities
    └── agent_tools.py
```

## Documentation Structure

```
docs/
└── codebase/                       # Codebase documentation (workflow-generated)
    ├── 01_inventory/
    │   └── codebase_inventory.md   # 422-line module inventory
    ├── 02_modules/                 # 72 module documentation files
    ├── 03_components/              # 6 component documentation files
    └── 04_changes/                 # Change impact documents
```

## Test Structure

```
tests/
├── conftest.py                     # Shared fixtures
├── unit/                           # 45+ pure unit tests (isolated logic)
└── integration/                    # Integration tests (real files, subprocesses)
```

## Scripts and Entrypoints

- `run-*.bat` - 35 batch files for workflow execution (Windows)
- `scripts/ukbe-run-delivery.bat` - Shared delivery runner
- `scripts/ukbe-daemon.bat` - Daemon launcher
- `scripts/ukbe-runner.sh` - Unix wrapper

# Workflow and Runtime Model

## Execution Model

Each workflow step follows a strict execution contract:

1. **Load** - Load workflow bundle from runtime path (`%USERPROFILE%\.ukbe-runner\workflows\`)
2. **Render** - Render prompt from template with artifact context substitution
3. **Invoke** - Call coder (Claude/Codex/Qwen) or execute deterministic action
4. **Validate** - Read `meta.json` sidecar written by the step
5. **Route** - Route to next step based on sidecar status (APPROVED/REJECTED)

## Coder/Action Split

- **Coder steps** - Invoke LLM backends via `coder_adapters.py`, return results via `meta.json`
- **Action steps** - Execute deterministic Python functions in `actions/` package

## Sidecar Contract (v2)

The `meta.json` sidecar is the **only** structured result channel:

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED|REJECTED",
    "remark": "Summary of work accomplished",
    "artifacts": {"KEY": "path/to/artifact.md"},
    "recorded_at": "2026-07-10T14:01:15+08:00"
  }
}
```

Key v2 rules:
- No markdown write-backs by the runner
- No silent recovery paths
- Hard failures route explicitly through `route_after_failure()`
- No pre-invocation sidecar writes

## Runtime Source of Truth

Two distinct sources exist:

1. **Packaged bootstrap source** (`agent_runner_v2/bootstrap/`) - Seeds runtime bundles
2. **Runtime workflow bundle** (`%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`) - Active execution source

Runtime prompt/templates are loaded from the global runner home, not from the repo tree directly. The repo bootstrap files only seed those runtime bundles.

## Workflow Families

21 workflow families defined in `template_groups.py`:

| Workflow | Steps | Purpose |
|----------|-------|---------|
| `00_master_docs_bootstrap_v1/v2` | 13 | Master system documentation generation |
| `10_execution_scaffold_v1` | 13 | Delivery scaffold generation |
| `20_initiative_intake_v1` | 5 | Initiative capture and refinement |
| `21_bug_fix_intake_v1` | 7 | Bug triage and patching |
| `30_delivery_planning_v1` | 10 | Plan and task graph generation |
| `31_task_execution_v1` | 12 | Implementation and validation |
| `40_documentation_sync_v1` | 5 | Documentation reconciliation |
| `41_*_doc_v1` | 4 each | Audience-specific documentation |
| `50_architecture_site_v1` | 2 | HTML architecture site publishing |
| `51-55_*_docs_v1` | 1-4 | Audience site generation |
| `image_csv_gen_v1/v2` | 3-5 | Image generation pipeline |
| `videoxpress_gen_v1` | 9 | Video generation pipeline |
| `tiktok_video_pipeline_v1` | 10 | TikTok content pipeline |

# Operational Risks

| Risk | Severity | Evidence |
|------|----------|----------|
| **Monolithic template_groups.py** | High | 2,453-line file with 21 workflows; plugin migration in progress but not complete |
| **Runtime bundle drift** | Medium | Bootstrap source may diverge from runtime; no automatic sync mechanism documented |
| **Windows-centric batch files** | Medium | 35 .bat files vs minimal Unix shell support; WSL support exists but secondary |
| **Meta.json schema versioning** | Low | CURRENT_SCHEMA_VERSION = 6; backward compatibility enforced but migration complexity accumulates |
| **Test isolation gaps** | Medium | Integration tests use tmp_path (filesystem); unit tests should be pure logic but some file dependencies remain |
| **Plugin system migration** | Medium | Workflow package system partially implemented; dual-path discovery (global → local) adds complexity |
| **Documentation coverage** | Low | `docs/` currently only has `codebase/`; `delivery/` and `system/` expected but not populated |

# Architectural Observations

## Strengths

1. **Centralized Constants** - `constants.py` provides single source of truth for all artifact paths and keys; eliminates hardcoded strings
2. **Strict Sidecar Contract** - v2 model eliminates ambiguity with meta.json as sole communication channel
3. **Deterministic Actions** - 28 well-defined runner actions separate from LLM-based coder steps
4. **Multi-Backend Support** - Claude, Codex, Qwen adapters with unified invocation interface
5. **Plugin Architecture** - Workflow packages with `workflow.toml` manifests enable declarative workflow definition

## Constraints

1. **Bootstrap/Runtime Duality** - Must maintain two copies of workflow definitions; changes require explicit sync
2. **Path Handling Complexity** - Windows path handling requires careful `PurePosixPath` usage for cross-platform consistency
3. **Notification Coupling** - Pushover notifications integrated but requires `.env` configuration
4. **Backend Dependency** - Worker mode requires backend connectivity; local mode has limited functionality

## Implementation Patterns

- **Dataclass-based results** - `StepResult`, `CoderInvocationError`, `UsageData` provide typed interfaces
- **PathProxy pattern** - Lazy path resolution for runtime context
- **Template substitution** - Prompt placeholders use `{ARTIFACT_KEY}` pattern replaced at runtime
- **Validation layering** - Guardrails in `documentation_guardrails.py` protect generated documents

# Architecture Posture

| Attribute | Value |
|-----------|-------|
| **current_profile** | `provisional` |
| **target_profile** | `structured` |
| **migration_mode** | `in_progress` |
| **repo_state** | `explicit` |

## Evidence Sources

- `template_groups.py` contains monolithic workflow registry (provisional)
- `workflow_packages/` directory exists with plugin base classes (migration in progress)
- `constants.py` provides centralized artifact keys and paths (structured pattern)
- `step_runner.py` implements strict v2 sidecar contract (structured pattern)
- Comprehensive test suite with unit/integration split (structured pattern)
- 21 workflow families with defined step sequences (explicit)

## Posture Analysis

The repository exhibits characteristics of both provisional and structured profiles:

- **Provisional elements**: Monolithic `template_groups.py` (2,453 lines) with hardcoded workflow definitions; plugin system migration incomplete
- **Structured elements**: Centralized constants, strict sidecar contracts, comprehensive test coverage, deterministic action separation

The migration from monolithic to plugin-based workflows is actively underway, with the `workflow_packages/` module providing the target architecture while `template_groups.py` remains the runtime source of truth.

# Unresolved Documentation Gaps

1. **Runtime Bundle Sync** - No documented procedure for synchronizing bootstrap changes to runtime bundles
2. **Plugin Development Guide** - Missing documentation for creating new workflow packages
3. **Backend API Contract** - Worker mode backend API documentation incomplete
4. **Notification Configuration** - Pushover and notification setup not fully documented
5. **Daemon Operation** - Limited documentation for daemon supervisor deployment and monitoring
6. **Workflow Debugging** - No documented troubleshooting guide for step failures
7. **Cross-Platform Deployment** - Windows-centric documentation; Unix/WSL coverage incomplete
8. **Schema Migration** - Version 6 schema migration history not documented
9. **Artifact Lifecycle** - Document promotion and archival policies not documented
10. **Integration Patterns** - Backend integration patterns for external workflow triggers not documented
