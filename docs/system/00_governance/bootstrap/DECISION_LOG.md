---
template_id: "SYS-03-DL"
title: "Decision Log"
status: "active"
generated: "2026-07-04T14:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Decision Log

## Decision Table

| ID | Date | Decision | Context | Status |
|----|------|----------|---------|--------|
| ADR-001 | 2024-Q1 | Extract runner from UKBE | Monolithic codebase becoming unmaintainable | Implemented |
| ADR-002 | 2024-Q1 | Python 3.11+ requirement | Match type hint features, dataclass improvements | Implemented |
| ADR-003 | 2024-Q2 | v2 sidecar-only contract | Need deterministic, machine-parseable results | Implemented |
| ADR-004 | 2024-Q2 | Bootstrap/runtime bundle separation | Allow runtime customization without source changes | Implemented |
| ADR-005 | 2024-Q2 | Multi-coder adapter pattern | Support Claude, Codex, Qwen with unified interface | Implemented |
| ADR-006 | 2024-Q3 | Explicit routing (no silent recovery) | Fail fast, clear failure classification | Implemented |
| ADR-007 | 2024-Q3 | Review/refine loops in config | Data-driven iteration control | Implemented |
| ADR-008 | 2024-Q4 | Atomic file operations | Prevent partial writes during concurrent execution | Implemented |
| ADR-009 | 2025-Q1 | Job state migration support | Backward compatibility for state format changes | Implemented |
| ADR-010 | 2025-Q1 | Daemon mode for workstations | Support distributed work claiming | Implemented |

## Decision Details

### ADR-003: v2 Sidecar-Only Contract

**Context**: Need for deterministic, auditable step results that can be validated programmatically.

**Decision**: Step results are communicated exclusively via `meta.json` sidecar files. No markdown write-backs by the runner.

**Consequences**:
- (+) Machine-parseable, schema-validatable results
- (+) Clear separation between runner orchestration and coder generation
- (-) Additional file I/O overhead
- (-) Strict schema compliance required

### ADR-004: Bootstrap/Runtime Bundle Separation

**Context**: Users need to customize workflows without modifying source code.

**Decision**: Packaged bootstrap seeds a global runtime bundle at `~/.ukbe-runner/`. Runtime loads from the global location.

**Consequences**:
- (+) User customization without source changes
- (+) Version pinning possible via `init` command
- (-) Risk of bootstrap/runtime version mismatch
- (-) Additional initialization step required

### ADR-005: Multi-Coder Adapter Pattern

**Context**: Need to support multiple LLM providers with different APIs and capabilities.

**Decision**: Adapter pattern in `coder_adapters.py` with unified interface for Claude, Codex, and Qwen.

**Consequences**:
- (+) Consistent invocation interface across providers
- (+) Easy to add new providers
- (-) Lowest-common-denominator abstraction
- (-) Provider-specific features may be hidden

### ADR-006: Explicit Routing (No Silent Recovery)

**Context**: Silent failures in v1 led to unexpected behavior and difficult debugging.

**Decision**: All routing decisions are explicit. Hard failures route through `route_after_failure()` with classification.

**Consequences**:
- (+) Predictable failure handling
- (+) Clear audit trail
- (-) More verbose error handling code
- (-) Stricter contract requirements

### ADR-010: Daemon Mode for Workstations

**Context**: Need to support distributed execution with workstations as worker nodes.

**Decision**: Daemon mode polls backend, spawns child processes for steps, manages lifecycle.

**Consequences**:
- (+) Scalable distributed execution
- (+) Workstation supervision
- (-) Process management complexity
- (-) Network dependency for backend mode

## Follow-Up Decisions

| ID | Topic | Status | Notes |
|----|-------|--------|-------|
| FUD-001 | Web UI for job monitoring | Proposed | Would require new component |
| FUD-002 | Persistent execution history | Proposed | Currently job-scoped only |
| FUD-003 | Plugin architecture for actions | Proposed | Currently built-in actions only |
| FUD-004 | Workflow dependency graph | Proposed | Currently linear step sequences |
| FUD-005 | Real-time collaboration | Proposed | Multiple workers on same job |

---

*This decision log captures architectural decisions for agent-runner-v2. See SYSTEM_CONTEXT.md for external boundaries and COMPONENT_ARCHITECTURE.md for component relationships.*
