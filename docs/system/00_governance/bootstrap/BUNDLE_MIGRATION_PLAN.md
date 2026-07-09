---
template_id: "SYS-00-BMP"
managed_by: workflow-generated
generated: "2026-07-09T21:18:02+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260709-002"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Migration Plan

## Purpose

This document defines the migration procedures for workflow bundles in agent-runner-v2. It describes how bundles are versioned, how migrations are executed, and how to handle version transitions.

The migration plan serves as the reference for system maintainers when updating workflow definitions, changing bundle structures, or migrating existing workspaces to new bundle versions.

## Audience Model

| Audience | Concerns | How This Document Helps |
|----------|----------|----------------------|
| **System Maintainers** | Migration procedures, version transitions | Understanding migration mechanics |
| **Operators** | Workspace migration, downtime handling | Migration procedures and timing |
| **Developers** | Backward compatibility, breaking changes | Version compatibility rules |

## Migration Principles

### Core Principles

1. **Backward Compatibility**: New bundle versions support existing job states
2. **Explicit Migration**: Migrations are explicit, not automatic
3. **No Data Loss**: Job history and artifacts are preserved
4. **Rollback Support**: Migrations can be reversed if issues occur
5. **Version Pinning**: Workspaces can pin to specific bundle versions

### Migration Scope

| Scope | Description |
|-------|-------------|
| **Bootstrap to Runtime** | Sync package source to user directory |
| **Version Upgrade** | Migrate to new bundle version |
| **Workspace Migration** | Migrate existing jobs to new structure |
| **Schema Migration** | Update job state schema version |

## Bundle Versions

### Version Identification

Bundle versions are identified by:

| Identifier | Source | Example |
|------------|--------|---------|
| **Git commit** | Bootstrap source | `d57a719` |
| **Change ID** | Generated documents | `00DOC-GEN-20260709-002` |
| **Schema version** | Job state | `6` (v2) |

### Version States

| State | Meaning |
|-------|---------|
| **current** | Active, supported version |
| **deprecated** | Supported but superseded |
| **archived** | Read-only, unsupported |

## Migration Procedures

### Bootstrap to Runtime Sync

**Purpose**: Update runtime bundle with latest bootstrap changes

**Procedure:**

1. Modify bootstrap source files
2. Run sync script: `sync-workflows-to-backend.bat`
3. Verify runtime bundle updated
4. Test workflow execution

**Validation:**

- Compare file checksums between source and runtime
- Verify prompt templates render correctly
- Confirm template_groups.py loads without errors

### Schema Migration

**Purpose**: Migrate job state to new schema version

**Procedure:**

1. Update `CURRENT_SCHEMA_VERSION` in `job_state.py`
2. Implement migration function in `migrate_job_state()`
3. Test migration with sample jobs
4. Deploy with migration enabled

**Migration Function Pattern:**

```python
def migrate_v5_to_v6(state: dict) -> dict:
    """Migrate schema version 5 to 6."""
    state["schema_version"] = 6
    # Add new fields
    state["new_field"] = default_value
    # Transform existing fields
    state["transformed"] = transform(state["old_field"])
    del state["old_field"]
    return state
```

### Workspace Migration

**Purpose**: Migrate existing workspace to new bundle version

**Procedure:**

1. Backup existing workspace
2. Archive old bundle to `bundles/core/archived/`
3. Publish new bundle to `bundles/core/current/`
4. Update workspace bundle reference
5. Reconcile existing documents
6. Validate workspace integrity

**Rollback:**

1. Restore from backup
2. Revert bundle reference
3. Reconcile documents to previous state

## Compatibility Rules

### Forward Compatibility

| Scenario | Rule |
|----------|------|
| New workflow family | Ignored by older runner versions |
| New step in workflow | Older runners fail gracefully |
| New artifact type | Ignored by older validation |
| New schema field | Ignored by older parsers |

### Backward Compatibility

| Scenario | Rule |
|----------|------|
| Removed workflow family | Must be deprecated first |
| Removed step | Must provide migration path |
| Removed artifact | Validation warning, not error |
| Removed schema field | Must be optional first |

### Breaking Changes

Breaking changes require major version bump:

| Change Type | Migration Required |
|-------------|-------------------|
| Schema version decrease | No (forward only) |
| Required field removal | Yes |
| Artifact path change | Yes |
| Workflow family rename | Yes |
| Prompt template structure change | No (runtime effect only) |

## Migration Checklist

### Pre-Migration

- [ ] Identify affected workspaces
- [ ] Backup current bundle
- [ ] Document breaking changes
- [ ] Prepare rollback procedure
- [ ] Schedule maintenance window

### Migration

- [ ] Execute backup
- [ ] Deploy new bundle
- [ ] Run migration scripts
- [ ] Verify job state integrity
- [ ] Test workflow execution
- [ ] Validate document generation

### Post-Migration

- [ ] Monitor error logs
- [ ] Verify active jobs complete
- [ ] Confirm new jobs start successfully
- [ ] Update documentation
- [ ] Archive old bundle

### Rollback

- [ ] Restore from backup
- [ ] Revert bundle reference
- [ ] Reconcile documents
- [ ] Verify workspace integrity
- [ ] Document rollback reason

## Migration Commands

### Command Reference

| Command | Purpose |
|---------|---------|
| `ukbe-run-agent init` | Re-initialize workspace with current bundle |
| `sync-workflows-to-backend.bat` | Sync bootstrap to runtime |
| `python -m agent_runner_v2.actions.finalize_bootstrap` | Finalize bootstrap migration |
| `python -m agent_runner_v2.actions.archive_previous_version` | Archive previous bundle version |

### Script Locations

| Script | Location |
|--------|----------|
| `sync-workflows-to-backend.bat` | Repository root |
| `sync-10_execution_scaffold_v1-workflow-spec.bat` | Repository root |
| `run-00_master_docs_bootstrap_v1.bat` | Repository root |

## Troubleshooting

### Common Migration Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Schema version mismatch | Old job with new runner | Run migration |
| Missing workflow family | Sync not executed | Re-sync bootstrap |
| Template load failure | Corrupted runtime bundle | Re-initialize workspace |
| Document validation failure | Outdated section requirements | Refresh documents |
| Path resolution error | Constants mismatch | Verify constants.py sync |

### Migration Logs

Migration activities are logged to:

```
%USERPROFILE%\.ukbe-runner\logs\migration.log
```

Log format:

```
[TIMESTAMP] [LEVEL] [WORKSPACE] [ACTION] [RESULT] [DETAILS]
```

### Emergency Procedures

**Complete Migration Failure:**

1. Stop all workflow execution
2. Restore from pre-migration backup
3. Revert to previous bundle version
4. Notify affected users
5. Investigate failure cause

**Partial Migration Failure:**

1. Identify failed workspaces
2. Re-run migration for affected workspaces
3. Verify successful completion
4. Document intermittent issue

---

*Generated by workflow: 00_master_docs_bootstrap_v1 / step: 03_generate_system_overview_docs*
