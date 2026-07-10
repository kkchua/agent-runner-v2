---
template_id: "SYS-00-PA"
title: "Project Analysis - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:43:59+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "02_generate_project_analysis"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `02_generate_project_analysis`
> This file is workflow-generated and protected from manual edits.

# Project Analysis: agent-runner-v2

## Repo Overview

`agent-runner-v2` is a standalone Python LLM workflow orchestration engine extracted from UKBE. It runs structured multi-step workflows across Claude, Codex, Qwen, and aliased models, with review loops, retries, approval gates, and deterministic runner actions.

The system provides a CLI entry point (`ukbe-run-agent`) that supports three primary usage modes:

1. **Local workflow execution** - Manual workflow runs via `ukbe-run-agent run`
2. **Backend-connected worker operation** - Single-step execution via `worker`, `poll`, and `execute-step` commands
3. **Workstation supervision** - Daemon mode via `ukbe-run-agent daemon`

The backend is the source of truth for runs, step runs, artifacts, events, and approvals. The runner handles prompt rendering, coder/action execution, output validation, and step result submission.

Key differentiators:
- Strict v2 sidecar contract (`meta.json` as the only structured result channel)
- No markdown write-backs by the runner
- No silent recovery paths - hard failures route explicitly through runner failure handling
- Plugin-based workflow bundle system with dual-path discovery (global first, local fallback)

## Codebase Structure

### Package Layout

```
agent_runner_v2/
├── __init__.py                    # Package stub
├── run_agent.py                   # CLI entry point (core)
├── step_runner.py                 # Step execution contract (core)
├── workflow_router.py             # Post-step routing (core)
├── job_state.py                   # Job.json lifecycle (state)
├── runtime_context.py             # Runtime path context (state)
├── coder_adapters.py              # LLM invocation (coder)
├── bundle_loader.py               # Bootstrap seeding and loading (bootstrap)
├── constants.py                   # Centralized artifact paths (support)
├── template_groups.py             # Package-local workflow definitions
├── workflow_packages/             # Plugin-based workflow system
│   ├── base.py
│   ├── loader.py
│   └── registry.py
├── actions/                       # Deterministic runner actions (30+ actions)
│   ├── scan_repo_codebase.py
│   ├── sync_codebase_docs.py
│   ├── validate_delivery_docs.py
│   └── ... (27 more action modules)
├── bootstrap/                     # Bootstrap source
│   ├── workflows/default/         # Default workflow bundle
│   ├── bundles/core/current/      # Master system docs bundle
│   └── themes/default/            # HTML site themes
├── config/                        # Configuration
│   └── section_requirements.py
└── tools/                         # Tool utilities
    └── agent_tools.py
```

### Workflow Bundles

The system uses a two-tier workflow discovery:

1. **Global runtime bundles**: `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`
2. **Project-local workflows**: `workflows/<workflow>/workflow.toml` (plugin packages)

Bootstrap source in `agent_runner_v2/bootstrap/workflows/default/` seeds the global runtime bundles.

### Scripts and Entry Points

- `ukbe-run-agent` - Main CLI entry point
- 40+ batch files for workflow execution (`run-*.bat`, `submit-*.bat`)
- Shell scripts for Unix environments (`scripts/*.sh`)

### Documentation Structure

```
docs/
├── system/                        # System documentation (generated)
│   └── 00_governance/bootstrap/
├── codebase/                      # Codebase documentation
│   ├── 01_inventory/              # Inventory documents
│   ├── 02_modules/                # Module documentation (73 modules)
│   ├── 03_components/             # Component documentation
│   └── 04_changes/              # Change impact documents
delivery/                          # Delivery artifacts
```

### Tests

```
tests/
├── unit/                          # Isolated logic tests (45 passing)
├── integration/                   # Integration tests
└── conftest.py                    # Shared fixtures
```

## Workflow and Runtime Model

### Core Execution Loop

Each workflow step follows this sequence:

1. **Load workflow bundle** - From global runner home or local plugin
2. **Render prompt** - Using template with context substitution
3. **Invoke coder or action**:
   - **Coder steps**: Call Claude/Codex/Qwen via adapters
   - **Action steps**: Execute deterministic Python actions
4. **Read meta.json sidecar** - The only structured result channel
5. **Validate artifacts** - Check existence of declared outputs
6. **Route to next step** - Based on result status and workflow config

### Sidecar Contract (v2)

The `meta.json` sidecar is the canonical result channel:

```json
{
  "schema_version": "v2",
  "coder_result": {
    "status": "APPROVED|REJECTED",
    "remark": "Human-readable summary",
    "artifacts": {"ARTIFACT_KEY": "relative/path/to/file.md"},
    "recorded_at": "2026-07-10T19:43:59+08:00"
  }
}
```

Key rules:
- `meta.json` is mandatory - missing sidecar is a hard failure
- No markdown write-backs by the runner
- Artifact paths are relative to project root
- Runner enriches sidecar with timing, checksums, and changed paths

### Coder/Action Split

| Aspect | Coder Steps | Action Steps |
|--------|-------------|--------------|
| Execution | Subprocess to LLM | In-process Python call |
| Output | Written by LLM | Written by action code |
| Validation | Artifact existence | Same |
| Retry | Configurable | Same |
| Timeout | Configurable | Same |

### Workflow Bundle/Runtime Distinction

**Packaged bootstrap source** (in repo):
- `agent_runner_v2/bootstrap/workflows/default/`
- Used only for seeding global bundles
- Not loaded directly at runtime

**Runtime workflow bundles** (global):
- `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`
- Loaded by `bundle_loader.py`
- Source of truth for execution

**Plugin workflow packages** (project-local):
- `workflows/<workflow>/workflow.toml`
- Self-contained with manifest, prompts, and optional hooks
- Converted to same dict format as legacy TEMPLATE_GROUPS

### Routing Model

Post-step routing supports:
- **approve** - Step accepted, advance to next
- **reject** - Step rejected, route to refine/replan
- **failure** - Hard failure, route through failure handling
- **waiting** - Awaiting external input

Review/refine loops enforce `max_rejects` limits before escalating to replan.

## Operational Risks

### 1. Bootstrap/Runtime Sync Risk

**Risk**: Changes to bootstrap workflow files may not propagate to global runtime bundles, causing execution to use stale templates.

**Evidence**: The codebase has `template_groups.py` (legacy monolithic) alongside the new plugin system. Runtime loads from global runner home, not from repo directly.

**Mitigation**: `sync_workflows.py` provides two-tier discovery (TEMPLATE_GROUPS + plugin workflow.toml), but manual sync is required.

### 2. Meta.json Contract Violation

**Risk**: LLM backends may not write valid meta.json sidecars, causing hard failures.

**Evidence**: `step_runner.py` raises `MetaJsonMissingError` and `MetaJsonInvalidError` as hard failures with no silent recovery.

**Mitigation**: Prompt templates include explicit sidecar instructions; validation schema enforced.

### 3. Path Resolution Complexity

**Risk**: Multiple path resolution layers (constants.py, doc_paths.py, runtime_context.py) may drift or conflict.

**Evidence**: Recent refactoring moved all path constants to `constants.py`, but memory notes indicate this was a significant cleanup effort.

**Mitigation**: Centralized constants.py with layered constant system and zero hardcoded strings.

### 4. Test Coverage Gaps

**Risk**: Module documentation shows "(none) No test references found" for most core modules.

**Evidence**: Only 45 unit tests exist; core modules like `run_agent.py`, `step_runner.py`, `workflow_router.py` have no documented test coverage.

**Mitigation**: Tests exist but coverage tracking is not integrated into module docs.

### 5. Plugin System Migration

**Risk**: Migration from monolithic TEMPLATE_GROUPS to plugin workflow system is in progress on `feat/plugin-workflow-system` branch.

**Evidence**: Git status shows modified `template_groups.py` and new `workflow_packages/` modules.

**Mitigation**: Adapter pattern ensures backward compatibility; runtime execution pipeline unchanged.

### 6. Windows-Specific Path Issues

**Risk**: Path manipulation on Windows may hit `pathlib` edge cases (e.g., `relative_to()` failures).

**Evidence**: Memory notes indicate recent fix for Windows pathlib bug.

**Mitigation**: Fix applied; requires ongoing vigilance for cross-platform compatibility.

## Architectural Observations

### 1. Strict Contract Enforcement

The v2 architecture enforces strict contracts at boundaries:
- Meta.json is the only valid result channel
- Artifact paths must exist or trigger hard failures
- Prompt rendering uses centralized placeholder substitution

This design eliminates ambiguous failure modes but requires disciplined LLM backend compliance.

### 2. Adapter Pattern for Workflow Loading

The plugin system is a **configuration source adapter**, not a runtime replacement:

```
WorkflowBundle (workflow.toml + prompts/)
    ↓
Adapter (workflow_packages/loader.py)
    ↓
Dict format (same as TEMPLATE_GROUPS)
    ↓
Existing execution pipeline
```

This minimizes risk while enabling maintainable workflow development.

### 3. Dual-Path Discovery

Runtime workflow discovery uses global-first, local-fallback:

1. Check `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\`
2. Fallback to repo `workflows/<workflow>/`

This supports both packaged workflows and project-specific overrides.

### 4. Centralized Constants

All documentation artifact paths and section requirements moved to `constants.py`:
- Pre-computed path constants
- Zero hardcoded strings in path construction
- Direct lookup during validation without intermediate mapping

This addresses previous maintenance nightmares from scattered string literals.

### 5. Process-Per-Step Execution

The daemon spawns fresh subprocesses for each step:
- Code changes are picked up automatically
- No daemon restart required for updates
- Isolation between steps prevents state corruption

### 6. Documentation-First Governance

The system enforces documentation as a first-class artifact:
- Workflows generate and validate docs
- Codebase inventory auto-synchronizes
- Architecture sites publish audience-specific views

This creates a self-documenting system with drift detection.

## Architecture Posture

| Attribute | Value |
|-----------|-------|
| **current_profile** | `provisional` |
| **target_profile** | `explicit` |
| **migration_mode** | `in_progress` |
| **repo_state** | `provisional` |

### Evidence Sources

1. **Plugin system migration**: Active branch `feat/plugin-workflow-system` with modified template_groups.py and new workflow_packages/ modules
2. **Constants refactoring**: Recent memory notes confirm migration to centralized constants.py completed
3. **Bootstrap/runtime distinction**: QWEN.md and README.md explicitly document two-tier source of truth
4. **v2 sidecar contract**: CODER_IMPLEMENTATION_SOP.md and QWEN.md specify strict meta.json enforcement
5. **Test infrastructure**: 45 unit tests passing; integration tests separated; coverage gaps noted

### Posture Assessment

The repository is in a **provisional** architecture state because:

1. **Active migration**: Plugin workflow system is replacing legacy TEMPLATE_GROUPS
2. **Runtime complexity**: Bootstrap vs runtime distinction requires careful synchronization
3. **Documentation in flux**: Bootstrap documents are being generated by the current workflow
4. **Test coverage**: While tests exist, comprehensive coverage verification is ongoing

The intended **target_profile** is `explicit` - a fully documented, tested, and typed system with clear architectural boundaries and automated validation.

## Unresolved Documentation Gaps

### 1. Workflow Package Migration Guide

**Gap**: No comprehensive guide for migrating existing workflows from TEMPLATE_GROUPS to plugin packages.

**Impact**: Developers may continue adding to monolithic template_groups.py

**Action for later steps**: Generate migration guide as part of BUNDLE_MIGRATION_PLAN.md

### 2. Runtime Bundle Synchronization SOP

**Gap**: No documented procedure for ensuring bootstrap changes propagate to global runtime bundles.

**Impact**: Runtime may execute stale workflow definitions

**Action for later steps**: Document sync workflow in EXISTING_REPO_WORKFLOW_SOP.md

### 3. Test Coverage by Module

**Gap**: Module documentation shows "No test references found" but tests may exist.

**Impact**: Cannot assess actual test coverage gaps

**Action for later steps**: Reconcile codebase inventory with test discovery

### 4. Cross-Platform Path Handling

**Gap**: Windows-specific pathlib issues were fixed but not comprehensively documented.

**Impact**: Future contributors may reintroduce Windows incompatibilities

**Action for later steps**: Document Windows path constraints in DEVELOPER_GUIDE.md

### 5. Notification System Configuration

**Gap**: Pushover notifications mentioned in PUSHOVER_NOTIFICATIONS.md but integration points unclear.

**Impact**: Operational visibility may be inconsistent

**Action for later steps**: Document notification lifecycle in RUNBOOK.md

### 6. Backend API Contract

**Gap**: Backend-connected worker modes depend on API contract not documented in this repo.

**Impact**: Integration maintenance requires external knowledge

**Action for later steps**: Reference backend API documentation or document integration points

### 7. Daemon State Recovery

**Gap**: Daemon failure recovery and child process orphaning not documented.

**Impact**: Operational incidents may require tribal knowledge

**Action for later steps**: Document recovery procedures in RUNBOOK.md

---

*This analysis serves as the baseline for downstream master document generation. It reflects the repository state as of the bootstrap scan timestamp and should be refreshed when significant structural changes occur.*
