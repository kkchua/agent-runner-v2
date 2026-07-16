---
template_id: "SYS-03-DL"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:22:07+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# Decision Log: agent-runner-v2

## Decision Table

| ID | Date | Decision | Rationale | Status | Impact |
|----|------|----------|-----------|--------|--------|
| D001 | 2026-01 | Extract runner from UKBE monolith | Enable standalone workflow execution | Implemented | Core architecture |
| D002 | 2026-02 | Adopt plugin-based workflow packages | Replace monolithic `TEMPLATE_GROUPS` dict (2453 lines) | Active migration | Maintainability |
| D003 | 2026-03 | Sidecar meta.json contract | Decouple coder output from runner state | Implemented | Coder integration |
| D004 | 2026-03 | Layer dependency chain | L1→L2→L3+ bootstrap ordering | Implemented | Governance structure |
| D005 | 2026-04 | Dual-path workflow discovery | Global first, local fallback for dev | Implemented | Deployment flexibility |
| D006 | 2026-05 | Daemon spawns manual subprocess | Unified execution path for daemon/manual modes | Implemented | Runtime consistency |
| D007 | 2026-06 | Centralized constants.py | Single source of truth for artifact keys and paths | Implemented | Path management |
| D008 | 2026-06 | Zero source mutation constraint | Bootstrap workflows must not alter code | Implemented | Safety |
| D009 | 2026-07 | Python 3.12 preference | CLI wrapper compatibility, stability | Implemented | Runtime environment |
| D010 | 2026-07 | Absolute paths in context | Windows compatibility for placeholders | Implemented | Cross-platform |

## Architecture Decisions

### AD-001: Plugin-Based Workflow System

**Context**: The monolithic `TEMPLATE_GROUPS` dict in `template_groups.py` grew to 2453 lines with 21 workflows, making maintenance difficult.

**Decision**: Migrate to self-contained plugin workflow packages with:
- `workflow.toml` declarative manifest
- `prompts/` directory for prompt templates
- `context_extensions.py` for workflow-specific context hooks
- `actions.py` for workflow-specific actions

**Status**: Active migration on `feat/plugin-workflow-system` branch

**Consequences**:
- Adding a workflow means creating a directory, not editing a monolithic file
- Adapter pattern preserves execution pipeline compatibility
- Dual-path discovery allows global deployment with local development

### AD-002: Sidecar Meta.json Contract

**Context**: Coder processes produce artifacts, but runner needs structured result reporting.

**Decision**: Each step produces a `meta.json` sidecar file with:
- `coder_result`: status (APPROVED/REJECTED), artifacts, remark
- `runner_data`: invocation metadata, timestamps, checksums
- `usage`: token counts and model information

**Status**: Implemented

**Consequences**:
- Decouples coder output from runner state management
- Enables retry without re-invoking coder
- Supports usage tracking and cost allocation

### AD-003: Layer Dependency Chain

**Context**: Bootstrap workflows must run in order; SDLC workflows depend on governance baseline.

**Decision**: Establish layer ordering:
- Layer 1: `00_layer1_governance_bootstrap_v1` → ecosystem governance
- Layer 2: `00_repo_master_docs_bootstrap_v1` → repo master docs
- Layer 3+: SDLC workflow families → phase-specific artifacts

**Status**: Layer 1 complete, Layer 2 in progress

**Consequences**:
- Each layer depends on previous layer's outputs
- Blocking dependency: Layer 3+ cannot run until Layer 2 complete
- Requires restoration of `00_master_docs_bootstrap_v2` from archive

### AD-004: Daemon-Manual Execution Unification

**Context**: Daemon and manual modes had divergent execution paths, causing maintenance burden.

**Decision**: Daemon spawns manual-mode subprocess for actual execution:
- Daemon polls backend API for job assignments
- Daemon spawns `run_agent.py run` subprocess
- Subprocess writes to same job directory structure

**Status**: Implemented

**Consequences**:
- Single execution path to maintain
- Daemon does not need to duplicate runtime logic
- Subprocess CWD fix ensures `.env` loading works

### AD-005: Centralized Path Constants

**Context**: Artifact paths were scattered across multiple modules, causing maintenance issues.

**Decision**: Consolidate all path constants in `constants.py`:
- Artifact keys (`ARTIFACT_KEY_*`)
- Folder keys (`FOLDER_KEY_*`)
- Path construction functions
- SDLC folder constants for migration

**Status**: Implemented

**Consequences**:
- Single source of truth for paths
- Easier refactoring when folder structure changes
- Prompt placeholders derived from constants

## Follow-up Decisions

| ID | Parent | Decision | Status |
|----|--------|----------|--------|
| F001 | D002 | Migrate legacy SDLC workflows to plugin format | Pending |
| F002 | D003 | Add artifact key normalization for LLM mistakes | Implemented |
| F003 | D005 | Sync workflow packages to backend registry | Implemented |
| F004 | AD-003 | Restore `00_master_docs_bootstrap_v2` from archive | Pending |
| F005 | D007 | Add SDLC folder constants for migration | Implemented |

## Technical Debt Register

| ID | Debt | Impact | Resolution Plan |
|----|------|--------|-----------------|
| TD001 | Legacy `TEMPLATE_GROUPS` still referenced | Blocking full plugin migration | Active migration |
| TD002 | Delivery-era artifact keys (`DRAFT_INIT_FILE`) | Runtime not aligned to SDLC structure | Migration plan documented |
| TD003 | Multiple runtime entrypoints | Maintenance complexity | Unified in v0.3.0 |
| TD004 | Layer 2 bootstrap incomplete | Blocks SDLC workflow-family work | Requires restoration |

## Open Questions

| ID | Question | Owner | Status |
|----|----------|-------|--------|
| Q001 | When to complete plugin migration? | Development team | Active |
| Q002 | How to handle legacy delivery docs during migration? | Development team | Alias strategy proposed |
| Q003 | Should DDD be adopted for SDLC workflows? | Architecture | Conditional, not universal |
