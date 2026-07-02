---
title: "Bundle Migration Plan"
template_id: "SYS-00-BMP"
status: "active"
managed_by: workflow-generated
generated: "2026-07-02T00:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260702-005"
---

# Bundle Migration Plan

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

## Overview

This document provides guidance for migrating workflow bundles and job states between versions of agent-runner-v2.

## Version Compatibility

### Current Version

- **Package Version**: 0.1.0
- **Job Schema Version**: v6
- **Sidecar Schema**: v2

### Compatibility Matrix

| Package Version | Job Schema | Sidecar Schema | Migration Required |
|-----------------|------------|----------------|------------------|
| 0.1.0 | v6 | v2 | Baseline |
| < 0.1.0 | v1-v5 | v1 | Yes |

## Migration Scenarios

### Scenario 1: Package Update (New Bootstrap)

**Trigger**: Package updated with new workflow definitions

**Steps**:

1. Backup existing runtime bundle:
   ```bash
   cp -r %USERPROFILE%\.ukbe-runner\workflows %USERPROFILE%\.ukbe-runner\workflows.backup
   ```

2. Reinitialize from new bootstrap:
   ```bash
   ukbe-run-agent init
   ```

3. Verify workflows load correctly:
   ```bash
   ukbe-run-agent list-workflows
   ```

**Risk**: Low — bootstrap seeding is non-destructive to jobs

### Scenario 2: Job State Schema Migration

**Trigger**: Job state schema version mismatch

**Automatic Migration**:

The `job_state.py` module includes `migrate_job_state()` which automatically migrates older job states:

| From Version | To Version | Migration Actions |
|--------------|------------|-------------------|
| v1-v5 | v6 | Add missing fields, update structure |

**Manual Verification**:

```python
from agent_runner_v2.job_state import load_job, save_job

# Load will auto-migrate
state = load_job(job_path)

# Save in new format
save_job(state, job_path)
```

### Scenario 3: Workflow Bundle Drift

**Trigger**: Runtime bundle differs from packaged source

**Detection**:

Compare checksums or timestamps between:
- `agent_runner_v2/bootstrap/workflows/default/`
- `%USERPROFILE%\.ukbe-runner\workflows\`

**Resolution**:

```bash
# Force re-seed from bootstrap
ukbe-run-agent init --force

# Or manually sync specific workflows
ukbe-run-agent sync-workflow {workflow_name}
```

### Scenario 4: Breaking Prompt Changes

**Trigger**: Prompt template changes require job restart

**Impact**: In-progress jobs may fail validation

**Mitigation**:

1. Complete or cancel in-progress jobs before updating
2. Use workflow versioning (`_v1`, `_v2`) for incompatible changes
3. Document breaking changes in release notes

## Migration Checklist

### Before Migration

- [ ] Backup existing runtime bundle
- [ ] List in-progress jobs
- [ ] Review release notes for breaking changes
- [ ] Verify new package version compatibility

### During Migration

- [ ] Run `ukbe-run-agent init`
- [ ] Verify workflow templates load
- [ ] Check for schema migration warnings
- [ ] Validate a test job

### After Migration

- [ ] Verify existing jobs remain accessible
- [ ] Test a complete workflow execution
- [ ] Confirm prompt templates render correctly
- [ ] Clean up backup if successful

## Rollback Procedures

### Rollback Runtime Bundle

```bash
# Remove current bundle
rmdir /s %USERPROFILE%\.ukbe-runner\workflows

# Restore backup
move %USERPROFILE%\.ukbe-runner\workflows.backup %USERPROFILE%\.ukbe-runner\workflows
```

### Rollback Package

```bash
pip install agent-runner-v2=={previous_version}
ukbe-run-agent init
```

## Deprecated Features

| Feature | Deprecated In | Removal Target | Replacement |
|---------|---------------|----------------|-------------|
| v1 sidecar format | 0.1.0 | 0.2.0 | v2 sidecar (meta.json) |
| Markdown write-backs | 0.1.0 | 0.2.0 | Sidecar-only communication |
| Legacy job states | 0.1.0 | 0.2.0 | Schema v6 job states |

## Future Migration Roadmap

### Version 0.2.0 (Planned)

- Remove v1 sidecar backward compatibility
- Remove markdown write-back functions
- Require schema v6 job states

### Version 0.3.0 (Proposed)

- Bundle versioning in metadata
- Delta-based bundle updates
- Migration hooks for custom workflows

## Troubleshooting

### Issue: Job fails with "schema version mismatch"

**Cause**: Job state created by older/newer package version

**Solution**: Auto-migration should handle this. If not:

```python
from agent_runner_v2.job_state import migrate_job_state, load_job, save_job

state = load_job(path)
migrate_job_state(state)  # Force migration
save_job(state, path)
```

### Issue: Prompt template not found

**Cause**: Runtime bundle missing new template

**Solution**: Reinitialize bundle

```bash
ukbe-run-agent init
```

### Issue: Workflow family not recognized

**Cause**: Runtime bundle out of sync

**Solution**: Sync workflows

```bash
ukbe-run-agent sync-workflows-to-backend
```

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `03_generate_system_overview_docs`*
