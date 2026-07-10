---
template_id: "SYS-03-DL"
title: "Decision Log - agent-runner-v2"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "04_generate_architecture_docs"
managed_by: workflow-generated
generated: "2026-07-10T09:52:38+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Decision Log: agent-runner-v2

## Decision Table

| ID | Date | Decision | Rationale | Status |
|----|------|----------|-----------|--------|
| ADR-001 | 2024-Q2 | Extract runner from UKBE | Need standalone workflow engine | Implemented |
| ADR-002 | 2024-Q3 | Meta.json as only channel | Eliminate ambiguity in LLM communication | Implemented |
| ADR-003 | 2024-Q3 | Remove silent recovery | Explicit failure routing for transparency | Implemented |
| ADR-004 | 2024-Q4 | Centralized constants | Single source of truth for paths | Implemented |
| ADR-005 | 2024-Q4 | Bootstrap/runtime separation | Allow runtime customization without code changes | Implemented |
| ADR-006 | 2025-Q1 | Declarative doc protection | `produces` lists instead of guardrails | Implemented |
| ADR-007 | 2025-Q1 | Review/refine loops | Human-in-the-loop for quality gates | Implemented |
| ADR-008 | 2025-Q2 | v2 sidecar schema | Structured result reporting | Implemented |
| ADR-009 | 2025-Q2 | Daemon mode | Background job processing | Implemented |
| ADR-010 | 2025-Q3 | Backend integration | Persistent job state, event streaming | Implemented |
| ADR-011 | 2026-Q1 | Prompt sidecar injection | Automated sidecar instructions | Implemented |
| ADR-012 | 2026-Q2 | Architecture site generation | HTML documentation for stakeholders | Implemented |
| ADR-013 | 2026-Q3 | Windows pathlib fix | Handle Windows path edge cases | Implemented |
| ADR-014 | 2026-Q3 | Pure unit tests | No filesystem dependencies in unit tests | Implemented |

## Architecture Decisions

### ADR-001: Extract runner from UKBE

**Context**: The workflow orchestration logic was embedded in the larger UKBE system.

**Decision**: Extract into standalone `agent-runner-v2` package.

**Consequences**:
- (+) Reusable across projects
- (+) Clearer responsibilities
- (-) Additional packaging overhead
- (-) Version synchronization needs

### ADR-002: Meta.json as Only Channel

**Context**: v1 had multiple communication channels (stdout parsing, markdown write-backs, sidecars) causing ambiguity.

**Decision**: Meta.json sidecar is the ONLY structured result channel.

**Consequences**:
- (+) Clear contract between runner and coders
- (+) Validatable schema
- (+) No stdout parsing fragility
- (-) Requires file I/O for every step
- (-) LLM must be instructed to write files

### ADR-003: Remove Silent Recovery

**Context**: v1 had automatic recovery functions that masked failures.

**Decision**: No silent recovery; all failures route explicitly through `route_after_failure()`.

**Consequences**:
- (+) Transparent failure handling
- (+) Clear retry/replan decisions
- (-) More explicit error handling code required
- (-) Potential for more interruptions

### ADR-004: Centralized Constants

**Context**: Path strings were scattered throughout the codebase.

**Decision**: All paths defined in `constants.py` with layered constant system.

**Consequences**:
- (+) Single source of truth
- (+) No path inconsistencies
- (+) Easy to refactor paths
- (-) Large constants file (1,333 lines)
- (-) Import dependency on constants

### ADR-005: Bootstrap/Runtime Separation

**Context**: Workflow definitions needed to be customizable per installation.

**Decision**: Packaged bootstrap seeds runtime bundles; runtime loads from `%USERPROFILE%\.ukbe-runner`.

**Consequences**:
- (+) Runtime customization without code changes
- (+) Multiple workflow versions can coexist
- (-) Sync required after bootstrap changes
- (-) Potential for drift between bootstrap and runtime

### ADR-006: Declarative Document Protection

**Context**: Document guardrails were implemented procedurally.

**Decision**: Use declarative `produces` lists in step configs; skip validation for scaffold workflows.

**Consequences**:
- (+) Clear contract in step definition
- (+) Simpler implementation
- (+) Scaffold workflows can write without restrictions
- (-) Requires discipline in defining produces lists

### ADR-007: Review/Refine Loops

**Context**: Quality gates needed human oversight.

**Decision**: Implement review/refine loops with max iteration limits.

**Consequences**:
- (+) Quality gates with human authority
- (+) Coder can refine based on feedback
- (-) Potential for infinite loops without limits
- (-) Added complexity in routing logic

### ADR-008: v2 Sidecar Schema

**Context**: Needed structured result reporting.

**Decision**: JSON schema with `schema_version`, `coder_result` containing `status`, `remark`, `artifacts`.

**Consequences**:
- (+) Machine-parseable results
- (+) Versioned schema for evolution
- (+) Clear artifact reporting
- (-) LLM must be instructed on exact format

### ADR-009: Daemon Mode

**Context**: Long-running background processing needed.

**Decision**: Daemon polls backend, spawns subprocess for each step.

**Consequences**:
- (+) Fresh Python process per step (no memory leaks)
- (+) Code changes picked up automatically
- (+) Isolation between steps
- (-) Process spawn overhead
- (-) No shared state between steps

### ADR-010: Backend Integration

**Context**: Job state needed persistence beyond local files.

**Decision**: WebSocket for events, HTTP for API; local files as cache.

**Consequences**:
- (+) Persistent job state
- (+) Event streaming for monitoring
- (+) Multi-device access
- (-) Network dependency
- (-) Backend availability requirement

### ADR-011: Prompt Sidecar Injection

**Context**: LLMs often forgot to write meta.json.

**Decision**: Automatically inject sidecar instructions into every prompt at runtime.

**Consequences**:
- (+) LLM reminded of contract every time
- (+) Consistent formatting
- (+) Path variables substituted automatically
- (-) Longer prompts
- (-) Some LLM context used for boilerplate

### ADR-012: Architecture Site Generation

**Context**: Stakeholders needed accessible documentation.

**Decision**: Generate HTML sites from markdown documentation.

**Consequences**:
- (+) Browsable documentation
- (+) Audience-specific views
- (+) Searchable content
- (-) Additional build step
- (-) HTML generation complexity

### ADR-013: Windows Pathlib Fix

**Context**: `Path.relative_to()` failed on Windows for valid subpaths.

**Decision**: Use `_safe_relative_to()` helper with fallback to `os.path.relpath()`.

**Consequences**:
- (+) Windows compatibility
- (+) No behavior change on Unix
- (-) Additional function call overhead
- (-) Slightly more complex code

### ADR-014: Pure Unit Tests

**Context**: Unit tests were using `tmp_path` causing permission issues on Windows.

**Decision**: Unit tests must test pure logic without filesystem dependencies.

**Consequences**:
- (+) Fast, reliable unit tests
- (+) No Windows permission issues
- (+) True unit isolation
- (-) Integration tests needed for file I/O
- (-) More test categories to maintain

## Follow-Up Decisions

### Pending

| ID | Topic | Blocked By | Proposed Resolution |
|----|-------|------------|---------------------|
| ADR-P001 | Async step execution | Complexity | Evaluate asyncio vs threads |
| ADR-P002 | Plugin architecture | Stability | Design formal plugin API |
| ADR-P003 | Metrics collection | Backend support | Define metrics schema |

### Superseded

| ID | Original Decision | Superseded By | Reason |
|----|-------------------|---------------|--------|
| ADR-S001 | Procedural guardrails | ADR-006 | Declarative is cleaner |
| ADR-S002 | stdout JSON parsing | ADR-002 | Sidecar is more reliable |
| ADR-S003 | Markdown metadata sync | ADR-002 | Runner doesn't write docs |

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `04_generate_architecture_docs` on 2026-07-10T09:52:38+08:00*
