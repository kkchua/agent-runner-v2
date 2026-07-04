---
template_id: "SYS-00-BMP"
title: "Bundle Migration Plan"
status: "active"
generated: "2026-07-04T12:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-002"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Migration Plan

## Purpose

This document defines the migration strategy for workflow bundles and documentation evolution in agent-runner-v2. It establishes the rules for transitioning between bundle versions, updating runtime bundles, and maintaining consistency between packaged bootstrap and runtime sources.

## Audience Model

| Audience | Concern | Primary Sections |
|----------|---------|------------------|
| **Platform Maintainers** | How do I release bundle updates? | Version Strategy, Release Process |
| **Repository Administrators** | How do I update my runtime bundles? | Runtime Update Procedures |
| **Workflow Authors** | How do I migrate my workflows? | Workflow Migration Patterns |
| **Operators** | How do I manage breaking changes? | Breaking Changes, Rollback Procedures |

## Current State

| Component | Current Version | Status |
|-----------|-----------------|--------|
| Platform | 0.1.0 | Active development |
| Bootstrap Bundle | 1.0.0 | Packaged with platform |
| Runtime Bundle | 1.0.0 (if initialized) | User home directory |
| Job Schema | 2 | v2 execution contract |

## Migration Scenarios

### Scenario 1: Platform Update with Bundle Changes

**Trigger**: New platform release includes bootstrap workflow changes

**Process**:
1. Update platform package (`pip install -e .`)
2. Run `ukbe-run-agent init` to re-seed runtime bundles
3. Existing jobs continue with previous bundle version
4. New jobs use updated bundle

**Considerations**:
- Existing job state is preserved
- Re-initialization is required to see changes
- No automatic migration of in-flight jobs

### Scenario 2: Runtime Bundle Refresh

**Trigger**: Local bootstrap modifications need testing

**Process**:
1. Modify files in `agent_runner_v2/bootstrap/workflows/default/`
2. Run `ukbe-run-agent init` to copy to runtime home
3. Test with new job

**Considerations**:
- Changes are local until committed
- Runtime home is user-specific
- Other users see changes only after pull + init

### Scenario 3: Workflow Family Version Bump

**Trigger**: Breaking changes to workflow definition

**Process**:
1. Create new workflow family with incremented version (e.g., `v1` → `v2`)
2. Maintain both versions during transition period
3. Deprecate old version with timeline
4. Remove old version after deprecation period

**Example**:
```python
# Old version
"delivery_planning_v1": { ... }

# New version
"delivery_planning_v2": { ... }
```

## Version Strategy

### Platform Versioning

Follows semantic versioning:

| Version Component | Meaning | Example Change |
|-------------------|---------|----------------|
| Major | Breaking API changes | New job schema version |
| Minor | New features, backward compatible | New workflow families |
| Patch | Bug fixes | Prompt template fixes |

### Bundle Versioning

Workflow families use integer versions:

| Version | Meaning | Migration Required |
|---------|---------|-------------------|
| Same version | Compatible updates | No |
| New version | Breaking changes | Yes, manual job migration |

### Schema Versioning

Job and response schemas use integer versions:

| Schema | Current | Compatibility |
|--------|---------|---------------|
| `job_schema.json` | 2 | Required for state loading |
| `llm_response_schema.json` | 2 | Required for coder output |

## Runtime Update Procedures

### Standard Update

```bash
# 1. Update platform package
pip install -e .

# 2. Re-initialize runtime bundles
ukbe-run-agent init

# 3. Verify update
ukbe-run-agent show-config
```

### Selective Workflow Update

To update only specific workflows (advanced):

```bash
# 1. Locate runtime workflow directory
# %USERPROFILE%\.ukbe-runner\workflows\

# 2. Replace specific workflow files

# 3. Restart any running daemon
ukbe-run-agent daemon-stop <worker-id>
ukbe-run-agent daemon <worker-id>
```

### Version Verification

```bash
# Check platform version
python -c "import agent_runner_v2; print(agent_runner_v2.__version__)"

# Check runtime bundle version
# (Review template_groups.py in runtime home)
```

## Breaking Changes

### Definition

A breaking change requires action by workflow authors or operators:

| Change Type | Breaking? | Mitigation |
|-------------|-----------|------------|
| New step in workflow | No | Jobs continue; new steps run |
| Removed step | Yes | Existing jobs may fail |
| Renamed artifact key | Yes | Artifact references must update |
| Changed step inputs | Yes | Caller configuration must update |
| New required input | Yes | All job initiations must provide |

### Breaking Change Process

1. **Identify**: Mark as breaking in commit and changelog
2. **Document**: Update this migration plan
3. **Version**: Bump appropriate version component
4. **Communicate**: Notify affected users
5. **Timeline**: Provide migration window
6. **Deprecate**: Remove after migration period

## Rollback Procedures

### Platform Rollback

```bash
# 1. Restore previous package version
git checkout <previous-tag>
pip install -e .

# 2. Re-initialize (restores bundled bundles)
ukbe-run-agent init

# 3. Verify
ukbe-run-agent --version
```

### Runtime Bundle Rollback

```bash
# 1. Stop any running daemon
ukbe-run-agent daemon-stop <worker-id>

# 2. Restore runtime bundles from backup
# Copy from backup location to %USERPROFILE%\.ukbe-runner\workflows\

# 3. Restart daemon if needed
ukbe-run-agent daemon <worker-id>
```

### Job State Recovery

If job state becomes incompatible:

```bash
# 1. Identify affected job
ukbe-run-agent show-job --job-id <job-id>

# 2. Create new job with compatible workflow
ukbe-run-agent run --template-group <workflow>_v<version> --set <artifacts>

# 3. Archive old job
# Move job directory to archive location
```

## Workflow Migration Patterns

### Pattern 1: Artifact Key Rename

```python
# Before
"produces": ["OLD_ARTIFACT_NAME"]

# After
"produces": ["NEW_ARTIFACT_NAME"]

# Migration: Update all references
# - template_groups.py reference_files
# - Job state artifacts
# - Prompt template variable references
```

### Pattern 2: Step Reordering

```python
# Before: step "03_old_step"
# After: step "04_new_step" with same purpose

# Migration: Update job state step tracking
# - completed_steps
# - failed_steps
# - retry_history
```

### Pattern 3: Input Changes

```python
# Before
"required_inputs": ["INPUT_A"]

# After
"required_inputs": ["INPUT_A", "INPUT_B"]

# Migration: Ensure all job initiations provide INPUT_B
```

## Timeline

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Bootstrap Complete | 2026-07-04 | System documentation generated |
| v1.0.0 Release | TBD | First stable release |
| v2 Planning | TBD | Evaluate schema v3, new patterns |

---

*This migration plan is a living document. Update when making breaking changes or adding new migration patterns.*
