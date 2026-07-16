---
template_id: "SYS-00-BMP"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T22:13:00+08:00"
workflow: "00_repo_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00RMD-20260716-5ee28fa5"
---

# Bundle Migration Plan

This document defines the migration strategy from legacy monolithic workflow
definitions to plugin-based workflow bundles for the `agent-runner-v2` repository.

## Migration Overview

### Current State

The repository currently uses a hybrid architecture:

| Component | Status | Location |
|-----------|--------|----------|
| Legacy `TEMPLATE_GROUPS` dict | Active | `agent_runner_v2/workflow_specs.py` |
| Plugin workflow packages | Active | `agent_runner_v2/bootstrap/workflows/default/` |
| Plugin system adapter | Active | `agent_runner_v2/workflow_packages/` |

The legacy `TEMPLATE_GROUPS` dict (2453 lines) contains hardcoded workflow
definitions that are being migrated to self-contained plugin packages.

### Target State

All workflow definitions will use the plugin-based architecture:

- Declarative TOML manifests (`workflow.toml`)
- Prompt templates in `prompts/` directories
- Context extensions in `context_extensions.py`
- Workflow-specific actions in `actions.py`
- No hardcoded workflow definitions in Python

### Migration Mode

**Status**: Active migration on `feat/plugin-workflow-system` branch

- Version 0.3.0 released with refactored daemon shared runtime
- Bootstrap workflows migrated to plugin packages
- Legacy SDLC workflows pending migration

## Layer Dependency Chain

Migration follows a strict layer dependency:

```
Layer 1: 00_layer1_governance_bootstrap_v1
    ↓ Generates docs/system/00_governance/
Layer 2: 00_master_docs_bootstrap_v2 (needs restoration)
    ↓ Generates docs/repo/sdlc/00_governance/
Layer 3+: SDLC workflow families (10, 20, 30, etc.)
    ↓ Produces phase-specific artifacts
```

**Current blockers:**

- Layer 2 bootstrap workflow exists only in archive
- Must be restored before SDLC workflow-family work can proceed

## Migration Phases

### Phase 1: Plugin System Foundation (Complete)

- Created `workflow_packages/` module with base, loader, registry
- Implemented configuration source adapter pattern
- Established dual-path discovery (global first, local fallback)
- Migrated bootstrap workflow bundles

### Phase 2: Daemon Runtime Unification (Complete)

- Unified daemon and manual execution paths
- Refactored shared runtime dependencies
- Fixed daemon subprocess CWD for `.env` loading
- Version 0.3.0 released

### Phase 3: Layer 2 Bootstrap Restoration (In Progress)

- Restore `00_master_docs_bootstrap_v2` from archive
- Rename to `00_master_docs_bootstrap_v1` (first live version)
- Extend to generate `docs/repo/sdlc/00_governance/`
- Unblock SDLC workflow-family work

### Phase 4: Legacy SDLC Migration (Planned)

Migrate 4 legacy workflows to 8 new SDLC workflow bundles:

| Legacy Workflow | Target SDLC Bundle(s) |
|-----------------|-----------------------|
| `delivery_scaffold_v1` | Multiple phase-specific bundles |
| `initiative_intake_v1` | Requirements phase bundle |
| `delivery_planning_v1` | Planning phase bundle |
| `task_execution_v1` | Execution phase bundle |

### Phase 5: Legacy Cleanup (Planned)

- Remove `TEMPLATE_GROUPS` dict from `workflow_specs.py`
- Remove hardcoded workflow definitions
- Update all imports to use plugin system
- Validate all workflow tests pass

## Migration Checklist

For each workflow migration:

1. **Create workflow directory** under `workflows/<workflow_name>/`
2. **Create workflow.toml** with complete manifest
3. **Extract prompts** from legacy definitions to `prompts/` directory
4. **Create context_extensions.py** if workflow needs custom context hooks
5. **Create actions.py** if workflow needs custom actions
6. **Validate bundle** using `workflow_bundle_validator.py`
7. **Test execution** in both manual and daemon modes
8. **Update tests** to reference new bundle paths
9. **Remove legacy entry** from `TEMPLATE_GROUPS` dict
10. **Update documentation** with new workflow paths

## Artifact Key Migration

Legacy delivery-era artifact keys need migration to SDLC semantics:

| Legacy Key | SDLC Key | Status |
|------------|----------|--------|
| `DRAFT_INIT_FILE` | `INITIATIVE_DRAFT` | Pending |
| `DRAFT_PLAN_FILE` | `PLAN_DRAFT` | Pending |
| `DELIVERY_SCAFFOLD` | `SDLC_SCAFFOLD` | Pending |

The `constants.py` file now includes SDLC folder keys for the new structure.

## Developer Guides

Two developer guides are available:

- `GUIDE_MIGRATE_WORKFLOW_PACKAGE.md` — 10-step migration process
- `GUIDE_CREATE_WORKFLOW_PACKAGE.md` — Creating new plugin packages

These guides codify the migration patterns for consistent, repeatable migrations.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Layer 2 bootstrap incomplete | Blocks all SDLC work | Prioritize restoration from archive |
| Plugin/legacy divergence | Execution failures | Adapter pattern preserves compatibility |
| Missing test coverage | Regression risk | Comprehensive unit tests for plugin system |
| Artifact key migration | Runtime path errors | Gradual migration with fallback aliases |

## Success Criteria

Migration is complete when:

1. All workflows use TOML manifests
2. Legacy `TEMPLATE_GROUPS` dict is removed
3. All tests pass with plugin system only
4. Documentation reflects new structure
5. SDLC governance baseline is generated
