---
template_id: "SYS-00-BMP"
title: "Bundle Migration Plan"
status: "active"
generated: "2026-07-10T14:07:00+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Migration Plan

## Purpose

This document defines the migration strategy for documentation bundles in the `agent-runner-v2` repository. It addresses:

1. **Current state** of documentation bundles
2. **Target state** for documentation organization
3. **Migration path** from current to target
4. **Validation criteria** for successful migration

## Audience

| Role | Use Case |
|------|----------|
| **Maintainers** | Understanding migration priorities and sequencing |
| **Contributors** | Knowing what structures are stable vs. in flux |
| **Operators** | Planning around migration activities |

## Current State Assessment

### Existing Bundle Structure

The repository currently maintains documentation in three primary locations:

#### 1. Bootstrap Bundles

**Location**: `agent_runner_v2/bootstrap/`

**Structure**:
```
bootstrap/
├── bundles/core/current/     # Core documentation bundles
├── themes/default/           # HTML theme templates
└── workflows/default/        # Workflow definitions
    ├── template_groups.py    # 2,453-line monolithic registry
    └── prompts/              # 200+ prompt templates
```

**Status**: Active and functional

**Issues**:
- Monolithic `template_groups.py` is difficult to maintain
- Manual synchronization required with runtime bundles
- No automated drift detection

#### 2. Runtime Bundles

**Location**: `%USERPROFILE%\.ukbe-runner\`

**Structure**:
```
.ukbe-runner/
├── config.json               # Runner configuration
├── jobs/                     # Job execution records
├── workflows/                # Active workflow bundles
└── logs/                     # Execution logs
```

**Status**: Seeded from bootstrap, runtime-managed

**Issues**:
- Can diverge from bootstrap source
- No automatic sync mechanism
- Version tracking manual

#### 3. Repository Documentation

**Location**: `docs/`

**Structure**:
```
docs/
├── system/                   # System documentation
├── codebase/                 # Codebase documentation
└── delivery/                 # Delivery documentation
```

**Status**: Partially populated

**Issues**:
- `docs/system/` minimal before bootstrap
- `docs/delivery/` structure exists, content workflow-generated
- `docs/codebase/` populated by reconcile workflow

### Migration Drivers

| Driver | Impact | Priority |
|--------|--------|----------|
| Monolithic workflow registry | High maintainability burden | High |
| Bootstrap/runtime drift | Risk of execution inconsistency | High |
| Documentation gaps | Incomplete stakeholder visibility | Medium |
| Cross-platform support | Windows-centric limits adoption | Medium |
| Test isolation | Some tests still filesystem-dependent | Low |

## Target State

### Desired Bundle Architecture

#### Plugin-Based Workflow System

**Target Structure**:
```
workflows/
├── <workflow_name>/
│   ├── workflow.toml         # Declarative manifest
│   ├── prompts/              # Prompt templates
│   └── context_extensions.py # Optional context hooks
```

**Benefits**:
- Self-contained workflow packages
- Declarative configuration
- Easier testing and versioning
- Reduced merge conflicts

#### Synchronized Runtime

**Target Behavior**:
- Automatic bootstrap-to-runtime sync
- Version tracking with drift detection
- Clear upgrade path
- Rollback capability

#### Comprehensive Documentation

**Target Coverage**:
- Complete system documentation
- Full codebase inventory
- Active delivery tracking
- Up-to-date templates

### Migration Phases

#### Phase 1: Foundation (Complete)

**Status**: ✅ Complete

**Achievements**:
- Centralized constants in `constants.py`
- Comprehensive test coverage (45+ unit tests)
- Strict sidecar contract (v2)
- Deterministic action separation

**Verification**:
- Unit tests pass
- Constants used throughout codebase
- No hardcoded paths in new code

#### Phase 2: Workflow Package Migration (In Progress)

**Status**: 🔄 In Progress

**Goals**:
- Migrate 21 workflows from `template_groups.py` to plugin packages
- Maintain backward compatibility
- Enable gradual adoption

**Approach**:
1. Create `workflow_packages/` module with base classes
2. Implement `workflow.toml` parser
3. Create adapter from `WorkflowBundle` to legacy format
4. Migrate workflows incrementally

**Timeline**: TBD

**Blockers**:
- Runtime bundle discovery path changes
- Template substitution backward compatibility
- Validation rule migration

#### Phase 3: Documentation Completion (In Progress)

**Status**: 🔄 In Progress

**Goals**:
- Complete system documentation
- Maintain codebase documentation currency
- Populate delivery documentation

**Approach**:
1. Execute `00_master_docs_bootstrap_v2` workflow
2. Enable `40_documentation_sync_v1` reconciliation
3. Standardize delivery documentation

**Timeline**: Current (2026-07-10)

**Current Activity**:
- Generating system documentation
- Establishing documentation standards
- Creating bundle taxonomy

#### Phase 4: Cross-Platform Enhancement (Planned)

**Status**: 📋 Planned

**Goals**:
- Full Unix/Linux support
- WSL optimization
- Container deployment

**Approach**:
1. Shell script equivalents for batch files
2. Path handling abstraction
3. Cross-platform testing

**Timeline**: Future

#### Phase 5: Automation Enhancement (Planned)

**Status**: 📋 Planned

**Goals**:
- Automatic documentation reconciliation
- Drift detection and alerts
- Self-healing documentation

**Approach**:
1. Git hooks for reconcile
2. CI/CD integration
3. Scheduled reconciliation

**Timeline**: Future

## Migration Path

### Workflow Registry Migration

#### Current → Adapter → Target

```
template_groups.py (monolithic)
    ↓
WorkflowBundle adapter (converts to legacy format)
    ↓
workflow_packages/ (plugin system)
    ↓
workflow.toml + prompts/ (declarative)
```

#### Backward Compatibility

During migration:
- Adapter preserves legacy interface
- Existing workflows continue to work
- New workflows use plugin system
- Gradual migration path

### Bootstrap/Runtime Sync

#### Current State

- Bootstrap seeds runtime on `ukbe-run-agent init`
- Changes to bootstrap require manual sync
- No automatic drift detection

#### Target State

- Version-tagged bundles
- Automatic sync on version mismatch
- Drift detection with alerts
- Configurable sync policy

#### Migration Steps

1. Add version metadata to bundles
2. Implement sync command
3. Add drift detection
4. Enable automatic sync (opt-in)

### Documentation Migration

#### System Documentation

**From**: Minimal or scattered documentation

**To**: Comprehensive system documentation in `docs/system/`

**Migration**:
- Execute bootstrap workflow
- Generate all system docs
- Establish update triggers

#### Codebase Documentation

**From**: Ad-hoc or missing

**To**: Complete inventory with automated updates

**Migration**:
- Reconcile workflow generates inventory
- Continuous sync on code changes
- Change tracking automatic

#### Delivery Documentation

**From**: Structure only

**To**: Populated with templates and active records

**Migration**:
- Execute scaffold workflow
- Generate templates
- Workflow execution populates records

## Validation Criteria

### Phase Completion Criteria

| Phase | Completion Criteria |
|-------|-------------------|
| Foundation | All tests pass, constants centralized |
| Workflow Packages | All 21 workflows migrated, tests pass |
| Documentation | All planned docs exist and validate |
| Cross-Platform | Tests pass on Windows, Linux, macOS |
| Automation | Reconciliation runs automatically |

### Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Test coverage | 45+ unit tests | 80%+ coverage |
| Documentation completeness | Partial | 100% |
| Workflow package migration | 0% | 100% |
| Cross-platform support | Windows primary | Multi-platform |
| Bootstrap/runtime drift | Manual detection | Automatic |

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Migration breaks existing workflows | Adapter pattern maintains compatibility |
| Documentation becomes stale | Automated reconciliation workflows |
| Cross-platform issues | Incremental testing, CI/CD |
| Performance regression | Benchmarking, profiling |
| User confusion | Clear documentation, migration guide |

## Rollback Strategy

### Version Control

- All migrations version-controlled
- Tagged releases before major changes
- Branch-based migration testing

### Compatibility Layers

- Adapter pattern preserves interfaces
- Feature flags for new behavior
- Gradual cutover possible

### Recovery Procedures

1. Revert to last known good version
2. Restore from backup bundles
3. Re-run initialization
4. Verify with validation tests

## Timeline Summary

| Phase | Status | Started | Target |
|-------|--------|---------|--------|
| Foundation | Complete | Earlier | Complete |
| Documentation | In Progress | 2026-07-10 | 2026-07-15 |
| Workflow Packages | Planned | TBD | TBD |
| Cross-Platform | Planned | TBD | TBD |
| Automation | Planned | TBD | TBD |

## Related Documents

- [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) — Bundle classification
- [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md) — Repository analysis
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Platform overview

---

*Generated by workflow: `00_master_docs_bootstrap_v2` — Step: `03_generate_system_overview_docs`*
