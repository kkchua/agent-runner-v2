---
template_id: "SYS-00-BMP"
title: "Bundle Migration Plan - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:47:28+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Migration Plan: agent-runner-v2

## Purpose

This document outlines the migration path from the monolithic workflow bundle system to the plugin-based workflow system. It defines current state, target state, migration phases, and rollback procedures.

## Scope

This plan covers:
- Migration from `TEMPLATE_GROUPS` monolith to plugin packages
- Bootstrap-to-runtime synchronization
- Backward compatibility maintenance
- Risk mitigation and rollback

## Current State

### Monolithic System

**Location**: `agent_runner_v2/bootstrap/workflows/default/template_groups.py`

**Characteristics**:
- Single 2453+ line Python file
- 21+ workflow definitions
- Hardcoded step configurations
- Mixed concerns (workflows, prompts, routing logic)

**Pain Points**:
- Unmaintainable at scale
- No independent versioning
- Difficult to test in isolation
- Adding workflow = editing massive file
- Code review complexity

### Active Migration Branch

**Branch**: `feat/plugin-workflow-system`

**Status**: In progress

**Git Status**:
- Modified `template_groups.py`
- New `workflow_packages/` module
- Modified core execution modules

## Target State

### Plugin-Based System

**Location**: `<repo>/workflows/<workflow_name>/`

**Characteristics**:
- Self-contained workflow packages
- Declarative `workflow.toml` manifests
- Versioned independently
- Testable in isolation
- Clear separation of concerns

**Structure**:
```
workflows/<workflow_name>/
├── workflow.toml          # Manifest, steps, routing, policies
├── prompts/               # Prompt template files
│   └── <step>.txt
└── context_extensions.py  # Optional context hooks
```

## Migration Phases

### Phase 1: Infrastructure (COMPLETE)

**Goal**: Establish plugin infrastructure without breaking existing system.

**Deliverables**:
- [x] `workflow_packages/base.py` — WorkflowBundle dataclass
- [x] `workflow_packages/loader.py` — TOML parsing and validation
- [x] `workflow_packages/registry.py` — Bundle discovery
- [x] `workflow_packages/actions/` — Plugin action handlers

**Risk Level**: Low (additive only)

### Phase 2: Adapter Implementation (IN PROGRESS)

**Goal**: Bridge plugin format to existing execution pipeline.

**Deliverables**:
- [x] Dual-path discovery (TEMPLATE_GROUPS + plugin)
- [x] Adapter converts WorkflowBundle → TEMPLATE_GROUPS dict format
- [x] Context extension hooks for workflow-specific logic
- [ ] Remove hardcoded `_set_*_aliases()` from step_runner.py

**Risk Level**: Medium (changes discovery path)

**Rollback**: Revert to TEMPLATE_GROUPS-only discovery

### Phase 3: Workflow Migration (PENDING)

**Goal**: Migrate existing workflows to plugin format.

**Approach**: Incremental migration per workflow family:

1. Create `workflows/<name>/workflow.toml`
2. Copy prompts to `workflows/<name>/prompts/`
3. Extract context hooks to `context_extensions.py`
4. Test plugin version alongside TEMPLATE_GROUPS
5. Remove from TEMPLATE_GROUPS once stable

**Priority Order**:
1. Documentation workflows (`40_documentation_sync_v1`)
2. Delivery workflows (`30_delivery_planning_v1`, `31_task_execution_v1`)
3. Scaffold workflows (`10_execution_scaffold_v1`)
4. Intake workflows (`20_initiative_intake_v1`, `21_bug_fix_intake_v1`)
5. Bootstrap workflows (`00_master_docs_bootstrap_v1`)

**Risk Level**: Medium (per-workflow validation required)

**Rollback**: Keep TEMPLATE_GROUPS entry until plugin verified

### Phase 4: Legacy Deprecation (FUTURE)

**Goal**: Remove monolithic TEMPLATE_GROUPS support.

**Prerequisites**:
- All workflows migrated to plugins
- Plugin system stable for N releases
- Documentation updated
- Migration guide published

**Risk Level**: Low (cleanup only)

## Backward Compatibility

### Adapter Pattern

The plugin system is a **configuration source adapter**, not a runtime replacement:

```
WorkflowBundle (workflow.toml + prompts/)
    ↓
Adapter (workflow_packages/loader.py)
    ↓
Dict format (same as TEMPLATE_GROUPS produces)
    ↓
Existing execution pipeline
```

This ensures:
- Zero changes to `step_runner.py`, `workflow_router.py`, `coder_adapters.py`
- Existing workflows continue to work
- Gradual migration possible

### Dual-Path Discovery

```python
# Pseudo-code
def load_workflow(workflow_name):
    # Global runtime first
    if exists(global_runtime_path / workflow_name):
        return load_from_global(workflow_name)
    
    # Project-local plugin fallback
    if exists(repo_path / "workflows" / workflow_name / "workflow.toml"):
        return load_plugin(workflow_name)
    
    # TEMPLATE_GROUPS fallback
    return TEMPLATE_GROUPS[workflow_name]
```

## Migration Risks

### Risk 1: Runtime/Plugin Drift

**Risk**: Plugin and TEMPLATE_GROUPS versions diverge.

**Mitigation**:
- Validation workflow compares outputs
- CI checks for drift
- Single source of truth for prompts

### Risk 2: Context Hook Complexity

**Risk**: `_set_*_aliases()` functions scattered in step_runner.py.

**Mitigation**:
- Move to `context_extensions.py` in each plugin
- Document hook interface
- Test hooks in isolation

### Risk 3: Path Resolution Changes

**Risk**: Plugin paths different from TEMPLATE_GROUPS paths.

**Mitigation**:
- Centralized path constants
- Validation at load time
- Clear error messages

### Risk 4: Sync Issues

**Risk**: Bootstrap changes don't propagate to runtime.

**Mitigation**:
- `sync_workflows.py` two-tier discovery
- Automated sync in CI
- Clear documentation

## Rollback Procedures

### Rollback Adapter Changes

```bash
# Revert to TEMPLATE_GROUPS-only discovery
git checkout HEAD -- agent_runner_v2/bundle_loader.py
```

### Rollback Plugin Migration

For individual workflow:
1. Keep TEMPLATE_GROUPS entry (don't delete)
2. Remove plugin directory
3. Restore TEMPLATE_GROUPS version

### Emergency Rollback

If critical issue detected:
1. Revert to last known good commit
2. Disable plugin discovery in config
3. Fall back to TEMPLATE_GROUPS exclusively

## Validation Checkpoints

### Per-Phase Validation

| Phase | Validation | Success Criteria |
|-------|------------|------------------|
| 1 | Unit tests pass | All 45 unit tests pass |
| 2 | Dual discovery | Both paths resolve same workflow |
| 3 | Workflow parity | Plugin output matches TEMPLATE_GROUPS |
| 4 | Cleanup | No TEMPLATE_GROUPS references remain |

### Continuous Validation

- CI runs full test suite
- Integration tests verify end-to-end
- Documentation sync validates bundles

## Documentation Updates

### Required Updates

- [ ] `GUIDE_CREATE_WORKFLOW_PACKAGE.md` — Create new workflow
- [ ] `GUIDE_MIGRATE_WORKFLOW_PACKAGE.md` — Migrate existing workflow
- [ ] `QWEN.md` — Runtime source of truth explanation
- [ ] `CODER_IMPLEMENTATION_SOP.md` — Plugin conventions

### Developer Communication

- Migration status in README
- Branch documentation
- Team announcement

## Timeline

| Phase | Target | Status |
|-------|--------|--------|
| 1. Infrastructure | 2026-07-01 | COMPLETE |
| 2. Adapter | 2026-07-15 | IN PROGRESS |
| 3. Workflow Migration | 2026-08-01 | PENDING |
| 4. Legacy Deprecation | 2026-09-01 | FUTURE |

## Success Criteria

Migration complete when:

- [ ] All workflows migrated to plugins
- [ ] TEMPLATE_GROUPS file removed
- [ ] Plugin system documentation complete
- [ ] All tests pass (unit + integration)
- [ ] No regression in workflow execution
- [ ] Developer guide published

---

*Last updated: 2026-07-10T19:47:28+08:00 via workflow `00_master_docs_bootstrap_v2`*
