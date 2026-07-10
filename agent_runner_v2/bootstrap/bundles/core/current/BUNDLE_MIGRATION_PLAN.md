---
title: "Bundle Migration Plan"
template_id: "SYS-00-BMP"
status: "active"
generated: "2026-07-10T11:45:32+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-15f76235"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Migration Plan

## Current State

### Bootstrap Bundle Version

| Attribute | Value |
|-----------|-------|
| **Bundle Name** | `default` |
| **Location** | `agent_runner_v2/bootstrap/workflows/default/` |
| **Workflow Families** | 8+ active workflows |
| **Prompt Templates** | 100+ templates |
| **Schema Version** | 1.0.0 |

### Workflow Families

| ID | Name | Status | Version |
|----|------|--------|---------|
| `00` | master_docs_bootstrap_v1 | active | v1 |
| `10` | execution_scaffold_v1 | active | v1 |
| `20` | initiative_intake_v1 | active | v1 |
| `21` | bug_fix_intake_v1 | active | v1 |
| `30` | delivery_planning_v1 | active | v1 |
| `31` | task_execution_v1 | active | v1 |
| `40` | documentation_sync_v1 | active | v1 |
| `41` | audience_doc_v1 | active | v1 |

## Migration Strategy

### Strategy: Incremental Evolution

The repository follows an incremental migration strategy where:

1. **Bootstrap templates** in the repo are the source of truth
2. **Runtime bundles** are seeded from bootstrap during `init`
3. **Changes** to bootstrap require re-initialization to take effect
4. **Backward compatibility** is maintained across minor versions

### Migration Scenarios

| Scenario | Action | Impact |
|----------|--------|--------|
| New workflow added | Add to bootstrap, run `init` | New workflows available |
| Prompt modified | Update bootstrap, run `init` | New jobs use updated prompts |
| Schema changed | Update bootstrap, run `init`, migrate jobs | Existing jobs may need migration |
| Workflow deprecated | Mark deprecated, maintain for 2 versions | Existing jobs continue working |

## Runtime Bundle Drift

### Drift Mechanism

The runtime bundle in `%USERPROFILE%\.ukbe-runner\workflows\` may diverge from the bootstrap bundle:

| Cause | Effect | Mitigation |
|-------|--------|------------|
| Bootstrap changed without `init` | Runtime uses old templates | Run `ukbe-run-agent init` |
| Manual runtime edits | Bootstrap/runtime mismatch | Avoid manual runtime edits |
| Version rollback | Runtime newer than bootstrap | Re-run `init` after rollback |

### Sync Procedure

To synchronize bootstrap to runtime:

```bash
# Full re-initialization
ukbe-run-agent init

# Or use sync batch file
sync-workflows-to-runtime.bat
```

## Version Migration Paths

### v1 to v2 (Future)

When workflow v2 is introduced:

1. Create new workflow directory: `prompts/workflow_name_v2/`
2. Copy v1 templates as baseline
3. Modify templates for v2 contract
4. Add v2 definition to `template_groups.py`
5. Update documentation
6. Run `init` to seed v2 runtime bundle

### Schema Evolution

| Change Type | Backward Compatible | Action Required |
|-------------|---------------------|-----------------|
| Add optional field | Yes | None |
| Add required field | No | Job migration |
| Remove field | No | Job migration |
| Rename field | No | Job migration |

### Job Migration

When schema changes require job migration:

```python
# In job_state.py
migrate_job_state(state, from_version, to_version)
```

Migration functions ensure backward compatibility.

## Workflow Deprecation

### Deprecation Lifecycle

| Phase | Duration | Action |
|-------|----------|--------|
| Active | Indefinite | Fully supported |
| Deprecated | 2 major versions | Still works, warnings issued |
| Removed | After deprecation | No longer available |

### Deprecation Process

1. Mark workflow as deprecated in `template_groups.py`:
   ```python
   "workflow_v1": {
       "deprecated": True,
       "replaced_by": "workflow_v2"
   }
   ```

2. Update documentation to reflect deprecation

3. Maintain for 2 major versions

4. Remove in third major version

## Bundle Taxonomy Evolution

### Current Taxonomy Version

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-10 | Initial taxonomy |

### Future Taxonomy Changes

| Proposed Change | Rationale | Target Version |
|-----------------|-----------|----------------|
| Workflow prefix standardization | Clearer categorization | 1.1.0 |
| Step naming convention | Consistent ordering | 1.1.0 |
| Artifact key simplification | Reduced verbosity | 2.0.0 |

## Migration Checklist

### Before Migration

- [ ] Review all workflow dependencies
- [ ] Backup existing runtime bundles
- [ ] Identify jobs requiring migration
- [ ] Test new templates in isolation
- [ ] Update documentation

### During Migration

- [ ] Run `ukbe-run-agent init`
- [ ] Verify runtime bundle updated
- [ ] Test workflow execution
- [ ] Validate job migration (if applicable)
- [ ] Monitor for errors

### After Migration

- [ ] Archive old runtime bundles
- [ ] Update operational runbooks
- [ ] Communicate changes to users
- [ ] Monitor job success rates
- [ ] Document lessons learned

## Rollback Procedure

If migration fails:

1. Stop runner execution
2. Restore runtime bundle from backup:
   ```bash
   xcopy /E /I backup\workflows %USERPROFILE%\.ukbe-runner\workflows\
   ```
3. Verify restored bundle works
4. Investigate failure cause
5. Retry migration with fixes

## Related Documents

- [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) — Bundle structure definitions
- [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md) — Documentation governance
- `agent_runner_v2/bootstrap/workflows/default/template_groups.py` — Workflow definitions

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-07-10 | Initial migration plan | `00_master_docs_bootstrap_v1` |
