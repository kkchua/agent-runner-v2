---
template_id: "SYS-03-DL"
title: "Decision Log - agent-runner-v2"
status: "active"
generated: "2026-07-04T10:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Decision Log: agent-runner-v2

## Decision Table

| ID | Date | Decision | Context | Rationale | Status |
|----|------|----------|---------|-----------|--------|
| ARCH-001 | 2024-Q2 | Extract from UKBE | Create standalone runner | Enable independent deployment and versioning | Implemented |
| ARCH-002 | 2024-Q2 | v2 Runtime Model | Replace v1 recovery-heavy model | Eliminate silent failures, explicit routing only | Implemented |
| ARCH-003 | 2024-Q2 | meta.json Sidecar | Sole structured result channel | Remove ambiguity, enable strict validation | Implemented |
| ARCH-004 | 2024-Q2 | Bootstrap/Runtime Split | Package seeds global runner home | Enable runtime customization without code changes | Implemented |
| ARCH-005 | 2024-Q3 | Multi-Coder Support | Claude, Codex, Qwen adapters | Support diverse LLM providers | Implemented |
| ARCH-006 | 2024-Q3 | Three Execution Modes | Local, Worker, Daemon | Cover development to production deployment | Implemented |
| ARCH-007 | 2024-Q3 | Windows-First Paths | Primary Windows deployment | Match primary use case, cross-platform secondary | Implemented |
| ARCH-008 | 2024-Q4 | Documentation Guardrails | Protect workflow-generated docs | Prevent documentation drift | Implemented |
| ARCH-009 | 2025-Q1 | Template-Based Workflows | Externalize prompt templates | Enable workflow customization | Implemented |
| ARCH-010 | 2025-Q1 | Schema Versioning | Job state schema evolution | Enable backward compatibility | Implemented |
| ARCH-011 | 2025-Q2 | Action Pattern | Deterministic non-coder steps | Consistent I/O contracts across step types | Implemented |
| ARCH-012 | 2025-Q2 | Review/Refine Loops | Explicit loop context in job state | Support iterative refinement workflows | Implemented |
| ARCH-013 | 2025-Q3 | Task Execution Binding | Planning/execution split | Enable separate planning and execution jobs | Implemented |
| ARCH-014 | 2025-Q3 | Backend Integration | HTTP API for distributed execution | Support worker pools and centralized control | Implemented |
| ARCH-015 | 2025-Q4 | Daemon Supervisor | Child process management | Reliable long-running workstation supervision | Implemented |
| ARCH-016 | 2026-Q1 | Bundle Taxonomy | Structured bundle organization | Support domain-specific workflow extensions | Implemented |
| ARCH-017 | 2026-Q2 | Documentation Bootstrap | Automated system doc generation | Ensure docs stay synchronized with code | In Progress |

## Key Decisions Explained

### ARCH-003: meta.json as Sole Communication Channel

**Context:** Early versions attempted to parse coder output from stdout or support multiple result formats.

**Decision:** All step results must be written to a `meta.json` sidecar file.

**Consequences:**
- (+) Unambiguous result validation
- (+) Structured artifact claims
- (+) Clear separation between output and result
- (-) Requires coder discipline to write sidecar
- (-) Additional file I/O per step

### ARCH-004: Bootstrap/Runtime Split

**Context:** Need to package workflow definitions while allowing customization.

**Decision:** Package contains bootstrap source; `init` command seeds global runner home; runtime loads from global home.

**Consequences:**
- (+) Users customize workflows without forking code
- (+) Clean separation between core and extensions
- (+) Versioned bootstrap updates
- (-) Requires `init` step before first use
- (-) Two sources of truth (package vs global home)

### ARCH-006: Three Execution Modes

**Context:** Different use cases require different deployment patterns.

**Decision:** Support Local (development), Worker (backend-driven), and Daemon (supervised) modes.

**Consequences:**
- (+) Single codebase covers all deployment scenarios
- (+) Consistent workflow execution across modes
- (+) Gradual operational complexity (local → worker → daemon)
- (-) Increased CLI complexity
- (-) Mode-specific code paths to maintain

### ARCH-008: Documentation Guardrails

**Context:** Workflow-generated documentation can be accidentally modified.

**Decision:** Track generated documents, inject managed-by banners, prevent manual edits.

**Consequences:**
- (+) Clear ownership of generated docs
- (+) Prevents documentation drift
- (+) Audit trail of doc generation
- (-) Additional complexity in doc operations
- (-) Requires workflow adherence to guardrails

## Follow-Up Decisions

| ID | Topic | Status | Notes |
|----|-------|--------|-------|
| FUP-001 | Cross-Platform Path Handling | Pending | Evaluate full Linux/macOS support |
| FUP-002 | Async Coder Invocation | Pending | Consider async/await for concurrent steps |
| FUP-003 | Workflow Hot-Reload | Pending | Reload bundles without restart |
| FUP-004 | Distributed State | Pending | Shared job state across workers |
| FUP-005 | Plugin Architecture | Pending | Third-party action registration |
| FUP-006 | Metrics and Observability | Pending | Structured logging, metrics export |

---

*Generated: 2026-07-04T10:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 04_generate_architecture_docs*
*Change ID: 00DOC-GEN-20260704-001*
