---
template_id: "SYS-03-DL"
managed_by: workflow-generated
generated: "2026-07-09T21:26:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Decision Log

## Decision Table

| ID | Date | Decision | Context | Rationale | Status |
|----|------|----------|---------|-----------|--------|
| DEC-001 | 2024-Q2 | Extract agent-runner from UKBE | UKBE monolith becoming unmanageable | Enable standalone usage, clearer contracts | Accepted |
| DEC-002 | 2024-Q3 | v2 rewrite with strict sidecar contract | v1 had multiple communication channels | Simplify reasoning, eliminate fallback paths | Accepted |
| DEC-003 | 2024-Q4 | Bootstrap/Runtime separation | Need package-local seeds + global runtime | Enable package distribution while allowing runtime customization | Accepted |
| DEC-004 | 2024-Q4 | Centralized constants in `constants.py` | Path strings scattered across modules | Single source of truth, prevent drift | Accepted |
| DEC-005 | 2025-Q1 | Unit/Integration test split | Tests mixing concerns, slow execution | Faster unit tests, clear separation | Accepted |
| DEC-006 | 2025-Q1 | Windows primary platform | Development team on Windows | Batch file workflow launchers, Windows path handling | Accepted |
| DEC-007 | 2025-Q2 | Daemon mode with child processes | Need workstation supervision | Fresh subprocess per step picks up code changes automatically | Accepted |
| DEC-008 | 2025-Q2 | Artifact key placeholders in prompts | Hardcoded paths in prompts | Runtime path resolution, bootstrap/runtime flexibility | Accepted |
| DEC-009 | 2025-Q3 | Generated document protection | Manual edits to generated docs | Prevent drift, enable regeneration | Accepted |
| DEC-010 | 2025-Q4 | 12+ workflow family definitions | Growing delivery patterns | Encode best practices, reduce setup time | Accepted |
| DEC-011 | 2026-Q1 | Template ID system | Document identification drift | Stable identifiers for validation | Accepted |
| DEC-012 | 2026-Q1 | Meta.json auto-injection | Coder forgetting sidecar format | Guaranteed sidecar instruction presence | Accepted |
| DEC-013 | 2026-Q2 | Documentation sync workflow | Documentation drift from code | Automated reconciliation | Accepted |
| DEC-014 | 2026-Q2 | Architecture site generation | HTML views for stakeholders | Multi-audience communication | Accepted |
| DEC-015 | 2026-Q3 | Schema version 6 (v2) | Job state compatibility | Clear versioning, migration path | Accepted |

## Key Decisions Explained

### DEC-002: Strict Sidecar Contract

**Context**: v1 had multiple ways for coders to communicate results (stdout JSON, markdown metadata, sidecar). This created ambiguity and fallback complexity.

**Decision**: v2 uses `meta.json` sidecar as the **only** structured communication channel.

**Consequences**:
- (+) Clear contract between runner and coder
- (+) Deterministic result parsing
- (+) No fallback ambiguity
- (-) Coders must understand and implement sidecar contract
- (-) No recovery from missing sidecar

### DEC-003: Bootstrap/Runtime Separation

**Context**: Package needs to ship workflow definitions, but runtime needs user-customizable workflows.

**Decision**: Ship bootstrap source in package; copy to global runner home on `init`.

**Consequences**:
- (+) Package can be distributed with default workflows
- (+) Users can customize runtime workflows without modifying package
- (+) Clean upgrade path (re-init preserves or refreshes)
- (-) Changes to bootstrap require explicit sync to take effect
- (-) Two sources of truth during development

### DEC-004: Centralized Constants

**Context**: Path strings scattered across modules, causing inconsistencies.

**Decision**: All artifact keys, folder keys, and path construction in `constants.py`.

**Consequences**:
- (+) Single source of truth for all paths
- (+) Prevents case mismatches
- (+) Enables artifact key placeholder substitution
- (-) Large constants file (~1,000 lines)
- (-) Must import constants module for any path operation

### DEC-007: Daemon with Child Processes

**Context**: Need long-running workstation supervisor that can execute steps without blocking.

**Decision**: Daemon polls backend, spawns child `execute-step` subprocess per unit of work.

**Consequences**:
- (+) Code changes picked up automatically (fresh import per step)
- (+) Process isolation between steps
- (+) Child can be killed without affecting daemon
- (-) Process management complexity
- (-) Inter-process communication via files

### DEC-009: Generated Document Protection

**Context**: Manual edits to workflow-generated documentation caused drift.

**Decision**: Generated docs carry `managed_by: workflow-generated` frontmatter and protection banner.

**Consequences**:
- (+) Clear ownership
- (+) Enables automated cleanup/refresh
- (+) Prevents accidental manual edits
- (-) Cannot manually fix typos in generated docs
- (-) Regeneration overwrites all content

## Follow-Up Decisions

| ID | Description | Status | Owner |
|----|-------------|--------|-------|
| FUP-001 | Backend API documentation | Pending | Backend team |
| FUP-002 | Coder timeout configuration guide | Pending | Documentation |
| FUP-003 | Failure mode taxonomy documentation | Pending | Documentation |
| FUP-004 | Bundle migration procedure operationalization | Pending | Operations |
| FUP-005 | Architecture site theme customization | Pending | UX |

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 04_generate_architecture_docs*
