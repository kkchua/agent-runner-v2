---
title: "Decision Log"
template_id: "SYS-03-DL"
status: "active"
change_id: "00DOC-20260710-15f76235"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
managed_by: workflow-generated
generated: "2026-07-10T11:57:31+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Decision Log: agent-runner-v2

## Decision Table

| ID | Date | Decision | Context | Rationale | Status |
|----|------|----------|---------|-----------|--------|
| **DEC-001** | 2024-04 | v2 Architecture Rewrite | Extract from UKBE monolith | Need standalone runner with cleaner contracts | Active |
| **DEC-002** | 2024-04 | Sidecar-Only Result Channel | Replace stdout/markdown parsing | Eliminate fragile parsing; explicit structured results | Active |
| **DEC-003** | 2024-04 | Subprocess Per Step | Daemon architecture | Automatic code reload; step isolation | Active |
| **DEC-004** | 2024-06 | Centralized Constants Pattern | Path maintenance burden | Single source of truth for all artifact paths | Active |
| **DEC-005** | 2024-06 | Workflow Router Decoupling | Monolithic state management | Explicit routing functions; coder owns content analysis | Active |
| **DEC-006** | 2024-06 | Declarative Document Protection | Imperative guard maintenance | `produces` lists in template config vs runtime checks | Active |
| **DEC-007** | 2024-07 | ARTIFACT_KEY_* Constants | String literal consistency | Prevent drift between prompts, code, and validation | Active |
| **DEC-008** | 2024-07 | PurePosixPath for Windows | Pathlib relative_to() failures | Cross-platform path consistency | Active |
| **DEC-009** | 2024-07 | Unit/Integration Test Split | pytest tmp_path permissions | Pure logic tests isolated from filesystem tests | Active |
| **DEC-010** | 2024-07 | Prompt Placeholder Substitution | REFERENCE_FILES dict keys | Runtime artifact path resolution | Active |

## Decision Details

### DEC-001: v2 Architecture Rewrite

**Context**: The original UKBE (Universal Knowledge Base Engine) runner was embedded in a larger monolith with tight coupling to backend state and complex recovery logic.

**Decision**: Extract agent-runner-v2 as a standalone package with:
- Clean separation between runner and backend
- Deterministic action layer
- Explicit contracts over implicit conventions

**Consequences**:
- Positive: Faster iteration, clearer boundaries
- Positive: Can run standalone or backend-connected
- Trade-off: Must maintain bootstrap/runtime bundle sync

### DEC-002: Sidecar-Only Result Channel

**Context**: v1 parsed stdout and markdown for results, leading to fragile extraction and silent failures.

**Decision**: `meta.json` sidecar is the **only** structured result channel:
- No markdown write-backs by runner
- No stdout parsing
- No silent recovery paths

**Consequences**:
- Positive: Unambiguous success/failure signaling
- Positive: LLM can report structured artifact lists
- Trade-off: Must ensure LLM writes valid JSON sidecar

### DEC-003: Subprocess Per Step

**Context**: Long-running daemon processes accumulate state and require restart for code changes.

**Decision**: Spawn fresh subprocess via `subprocess.Popen()` for each step:
```python
subprocess.Popen([sys.executable, '-m', 'agent_runner_v2.run_agent', 'execute-step', ...])
```

**Consequences**:
- Positive: Code changes active immediately
- Positive: Step isolation prevents state bleed
- Positive: Failed steps don't crash daemon
- Trade-off: Higher per-step overhead

### DEC-004: Centralized Constants Pattern

**Context**: Hardcoded paths scattered throughout codebase created maintenance burden and Windows/Unix inconsistencies.

**Decision**: Layered constant system in `constants.py`:
- `ARTIFACT_KEY_*` - artifact identification
- `ARTIFACT_PATH_*` - path templates
- `FOLDER_KEY_*` - directory locations
- `REFERENCE_FILES` - prompt placeholder substitution

**Consequences**:
- Positive: Single source of truth
- Positive: Consistent path construction
- Trade-off: Must import constants module throughout

### DEC-005: Workflow Router Decoupling

**Context**: v1 had monolithic `update_job_state_after_result()` with complex branching.

**Decision**: Replace with explicit routing functions in `workflow_router.py`:
- `route_after_step()` - normal completion routing
- `route_after_failure()` - failure handling
- No `extract_blocking_issues()` - coder owns analysis
- No `review_converges()` check - coder decides adequacy

**Consequences**:
- Positive: Clearer control flow
- Positive: Coder has more autonomy
- Trade-off: Less runner-level validation

### DEC-006: Declarative Document Protection

**Context**: Imperative guard functions checking document state became complex and error-prone.

**Decision**: Declarative `produces` lists in step configuration:
- Step declares what it will produce
- Guardrails validate against declarations
- No runtime mutation of source code

**Consequences**:
- Positive: Clear contract per step
- Positive: Validation can check declared vs actual

### DEC-007: ARTIFACT_KEY_* Constants

**Context**: String literals in prompts, code, and validation drifted apart.

**Decision**: All artifact references use `ARTIFACT_KEY_*` constants:
- Prompt placeholders: `{ARTIFACT_KEY_PROJECT_ANALYSIS}`
- REFERENCE_FILES keys: `"ARTIFACT_KEY_PROJECT_ANALYSIS"`
- Validation checks: same keys

**Consequences**:
- Positive: Alignment across all layers
- Positive: Refactoring support via IDE

### DEC-008: PurePosixPath for Windows

**Context**: `Path.relative_to()` fails on Windows with mixed separators.

**Decision**: Use `PurePosixPath` for path construction in constants:
```python
from pathlib import PurePosixPath
ARTIFACT_PATH_SYSTEM_CONTEXT = str(PurePosixPath(FOLDER_KEY_SYSTEM_BOOTSTRAP) / "SYSTEM_CONTEXT.md")
```

**Consequences**:
- Positive: Consistent forward slashes in paths
- Positive: Cross-platform compatibility

### DEC-009: Unit/Integration Test Split

**Context**: pytest `tmp_path` fixture creates directories with permission issues on Windows.

**Decision**: Split tests into:
- `tests/unit/` - pure logic, no filesystem dependencies
- `tests/integration/` - real files, external systems

**Consequences**:
- Positive: Unit tests run fast and reliably
- Positive: Integration tests isolated from pure tests

### DEC-010: Prompt Placeholder Substitution

**Context**: Prompts hardcoded paths that varied by environment.

**Decision**: Runtime substitution via `REFERENCE_FILES` dict:
- Prompt contains `{ARTIFACT_KEY_PROJECT_ANALYSIS}`
- Runner substitutes with actual path at runtime
- LLM sees resolved values

**Consequences**:
- Positive: Environment-agnostic prompts
- Positive: Centralized path management

## Follow-Up Decisions

| ID | Topic | Status | Notes |
|----|-------|--------|-------|
| **FUP-001** | Backend API contract evolution | Pending | Need OpenAPI spec alignment |
| **FUP-002** | Bundle versioning strategy | Pending | Semantic versioning for workflows |
| **FUP-003** | Multi-workspace support | Pending | Current design assumes single workspace |
| **FUP-004** | Distributed execution | Not planned | Out of scope for v2 |
