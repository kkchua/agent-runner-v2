---
template_id: "SYS-03-DL"
title: "Decision Log - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:56:49+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "04_generate_architecture_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `04_generate_architecture_docs`
> This file is workflow-generated and protected from manual edits.

# Decision Log: agent-runner-v2

## Decision Table

| ID | Date | Decision | Rationale | Status |
|----|------|----------|-----------|--------|
| ADR-001 | 2024-Q1 | Extract agent-runner from UKBE | Need standalone workflow engine | Accepted |
| ADR-002 | 2024-Q2 | v2 sidecar contract (meta.json only) | Eliminate ambiguous failure modes | Accepted |
| ADR-003 | 2024-Q2 | Subprocess-per-step execution | Fresh code loading, isolation | Accepted |
| ADR-004 | 2024-Q3 | Plugin workflow system | Replace 2453-line template_groups.py | In Progress |
| ADR-005 | 2024-Q4 | Centralized constants.py | Zero hardcoded paths | Accepted |
| ADR-006 | 2025-Q1 | Dual-path bundle discovery | Global first, local fallback | Accepted |
| ADR-007 | 2025-Q1 | Adapter pattern for plugins | Minimize execution pipeline risk | Accepted |
| ADR-008 | 2025-Q2 | Process-local runtime context | Thread-safe, testable | Accepted |
| ADR-009 | 2025-Q2 | Documentation-first governance | Self-documenting system | Accepted |
| ADR-010 | 2025-Q3 | Strict artifact validation | No silent recovery paths | Accepted |
| ADR-011 | 2025-Q4 | Centralized section requirements | Validation without mapping layers | Accepted |
| ADR-012 | 2026-Q1 | Windows pathlib compatibility | Fix relative_to() edge cases | Accepted |
| ADR-013 | 2026-Q2 | Prompt placeholder normalization | REFERENCE_FILES keys as placeholders | Accepted |

## Decision Details

### ADR-002: v2 Sidecar Contract

**Context**: Need clear communication channel between LLM and runner.

**Decision**: `meta.json` is the ONLY structured result channel.

**Consequences**:
- LLM must write valid JSON sidecar
- No stdout parsing fallback
- Hard failures for missing/invalid sidecars
- Clear contract enforcement

### ADR-004: Plugin Workflow System

**Context**: Monolithic template_groups.py at 2453+ lines is unmaintainable.

**Decision**: Migrate to self-contained workflow packages with adapter pattern.

**Architecture**:
```
workflows/<name>/
├── workflow.toml       # Manifest
├── prompts/            # Templates
└── context_extensions.py  # Hooks
```

**Consequences**:
- Adding workflow = create directory, not edit monolith
- Adapter converts to existing dict format
- Zero changes to execution pipeline
- Dual-path discovery maintained

### ADR-005: Centralized Constants

**Context**: Scattered string literals created maintenance nightmare.

**Decision**: All paths and section requirements in `constants.py`.

**Benefits**:
- Single source of truth
- Direct lookup without mapping layers
- Zero hardcoded strings
- Case consistency

### ADR-007: Adapter Pattern for Plugins

**Context**: Risk of breaking proven execution pipeline.

**Decision**: Plugin system is configuration source adapter, not runtime replacement.

**Flow**:
```
WorkflowBundle → Adapter → Dict format → Existing pipeline
```

**Benefits**:
- Proven execution pipeline unchanged
- Minimal risk
- Easy rollback
- Backward compatible

### ADR-013: Prompt Placeholder Normalization

**Context**: Artifact key mismatches causing validation failures.

**Decision**: Use REFERENCE_FILES dict keys as placeholders.

**Pattern**:
- Placeholder: `{ARTIFACT_KEY_CODEBASE_DOC_SOP}`
- Maps to value: `CODEBASE_DOC_SOP_v1`
- LLM reports key in meta.json
- Validation passes

## Follow-Up Decisions

| Item | Description | Owner | Due |
|------|-------------|-------|-----|
| DEC-FU-001 | Complete plugin system migration | TBD | 2026-Q3 |
| DEC-FU-002 | Deprecate TEMPLATE_GROUPS legacy path | TBD | 2026-Q4 |
| DEC-FU-003 | Add workflow package template generator | TBD | 2026-Q3 |
| DEC-FU-004 | Document cross-platform path handling | TBD | 2026-Q3 |
| DEC-FU-005 | Add integration test coverage for plugin loading | TBD | 2026-Q3 |

---

*Last updated: 2026-07-10T19:56:49+08:00 via workflow `00_master_docs_bootstrap_v2`*
