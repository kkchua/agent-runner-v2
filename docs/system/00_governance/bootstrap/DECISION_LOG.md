---
template_id: "SYS-03-DL"
title: "Decision Log - agent-runner-v2"
status: "active"
generated: "2026-07-10T14:20:05+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Decision Log

## Decision Table

| ID | Date | Decision | Context | Status |
|----|------|----------|---------|--------|
| DEC-001 | 2024-Q2 | Extract from UKBE | Create standalone runner from UKBE monolith | ✅ Implemented |
| DEC-002 | 2024-Q3 | v2 Sidecar Contract | meta.json as sole communication channel | ✅ Implemented |
| DEC-003 | 2024-Q4 | Bootstrap/Runtime Duality | Packaged source seeds global runtime | ✅ Implemented |
| DEC-004 | 2025-Q1 | Centralized Constants | Single source of truth for paths | ✅ Implemented |
| DEC-005 | 2025-Q2 | Plugin Architecture | Self-contained workflow packages | 🔄 In Progress |
| DEC-006 | 2025-Q3 | Auto-Injection | Remove manual sidecar boilerplate | ✅ Implemented |
| DEC-007 | 2025-Q4 | Test Split | Unit/integration directory separation | ✅ Implemented |
| DEC-008 | 2026-Q1 | Pathlib Windows Fix | Fix relative_to() on Windows | ✅ Implemented |
| DEC-009 | 2026-Q2 | Workflow Package Discovery | Dual-path (global→local) loading | ✅ Implemented |

## Detailed Decisions

### DEC-001: Extract from UKBE

**Context**: The runner was embedded in the larger UKBE (Unified Knowledge Base Environment) system, creating deployment coupling.

**Decision**: Extract into standalone `agent-runner-v2` package with its own lifecycle.

**Consequences**:
- Independent versioning and deployment
- Clearer responsibility boundaries
- Separate repository for focused development

### DEC-002: v2 Sidecar Contract

**Context**: v1 used markdown write-backs and stdout parsing, creating ambiguity in result communication.

**Decision**: meta.json is the **only** structured result channel. No markdown write-backs, no silent recovery, explicit routing.

**Consequences**:
- Unambiguous step results
- Schema-versioned contracts
- Hard failures routed explicitly through `route_after_failure()`
- Required significant refactoring of all workflow steps

### DEC-003: Bootstrap/Runtime Duality

**Context**: Workflows need to be packaged but also user-modifiable.

**Decision**: Package bootstrap source in repo (`agent_runner_v2/bootstrap/`), seed to global runner home (`%USERPROFILE%\.ukbe-runner\`) via `init` command.

**Consequences**:
- Users can modify runtime workflows without editing package
- Updates require explicit re-initialization
- Two sources of truth require careful management

### DEC-004: Centralized Constants

**Context**: Hardcoded paths scattered across codebase created maintenance issues.

**Decision**: Consolidate all path constants into `constants.py` with ARTIFACT_KEY_* and ARTIFACT_PATH_* constants.

**Consequences**:
- Zero hardcoded strings in path construction
- Section requirements use constants as keys
- Single source of truth for validation

### DEC-005: Plugin Architecture

**Context**: `template_groups.py` grew to 2,453 lines with 21 workflows—unmaintainable.

**Decision**: Migrate to self-contained workflow packages with `workflow.toml` manifests.

**Status**: In progress. Adapter pattern maintains compatibility with existing execution pipeline.

### DEC-006: Auto-Injection

**Context**: Manual sidecar boilerplate in prompts was error-prone and inconsistent.

**Decision**: Automatically inject sidecar instructions at runtime via template substitution.

**Consequences**:
- Consistent sidecar format across all prompts
- Reduced prompt maintenance burden
- Centralized injection logic in `step_runner.py`

### DEC-007: Test Split

**Context**: Mixed test types in single directory made it hard to run quick checks.

**Decision**: Separate `tests/unit/` (pure logic, isolated) from `tests/integration/` (real files, subprocesses).

**Consequences**:
- Fast unit test feedback
- Clear separation of concerns
- Integration tests can use filesystem and network

### DEC-008: Pathlib Windows Fix

**Context**: `Path.relative_to()` fails on Windows when paths have different drive letters.

**Decision**: Add explicit handling for Windows path edge cases.

**Consequences**:
- Cross-platform path operations work correctly
- Windows development fully supported

### DEC-009: Dual-Path Discovery

**Context**: Workflow packages need both global (runner home) and local (project) sources.

**Decision**: Global first, local fallback. No automatic fallback from global to local at runtime.

**Consequences**:
- Explicit path resolution
- Predictable loading order
- Local overrides possible but not automatic

## Follow-Up Decisions

| ID | Description | Priority | Owner |
|----|-------------|----------|-------|
| DEC-FU-001 | Complete plugin migration for all 21 workflows | High | Architecture |
| DEC-FU-002 | Document runtime bundle sync procedure | Medium | Documentation |
| DEC-FU-003 | Backend API contract documentation | Medium | Backend |
| DEC-FU-004 | Unix-first deployment option | Low | Platform |

## Related Documents

| Document | Purpose |
|----------|---------|
| [COMPONENT_ARCHITECTURE.md](COMPONENT_ARCHITECTURE.md) | Component breakdown |
| [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) | Migration strategy |
