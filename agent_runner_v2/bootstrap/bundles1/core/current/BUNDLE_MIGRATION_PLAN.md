---
template_id: "SYS-00-BMP"
title: "Bundle Migration Plan - agent-runner-v2"
status: "active"
generated: "2026-07-08T23:10:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260708-78fb419e"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Migration Plan

## Purpose

This document defines the migration strategy for workflow bundles in the `agent-runner-v2` system. It establishes versioning rules, migration procedures, and the path from provisional to stable bundle states.

## Current State

### Current Bundle Version

- **Bootstrap Bundle**: `core/current`
- **Runtime Bundle**: `%USERPROFILE%\.ukbe-runner\workflows\`
- **Migration Mode**: `provisional`

### Current Posture

The repository is in `provisional` migration mode:

- Established patterns exist (centralized constants, workflow families)
- Universal abstraction is still evolving
- Bundle structure is stable but may change as the standard matures

## Migration Modes

### Mode Definitions

| Mode | Description | Characteristics |
|------|-------------|-----------------|
| `greenfield` | New bundle with no history | No migration concerns |
| `provisional` | Active development | Patterns established, standard evolving |
| `migrating` | Explicit version transition | Old and new versions coexist |
| `stable` | Mature, versioned | Clear versioning, backward compatibility |

### Mode Transitions

```
greenfield → provisional → stable
                ↓
            migrating (if needed)
```

## Versioning Strategy

### Semantic Versioning

When the bundle reaches `stable` mode, it will use semantic versioning:

- **Major**: Breaking changes to workflow contracts
- **Minor**: New workflows, features, backward compatible
- **Patch**: Bug fixes, documentation updates

### Change IDs

During `provisional` mode, changes are tracked by:

- **Date**: `YYYYMMDD` format
- **Hash**: Unique identifier for the change
- **Type**: `bootstrap`, `scaffold`, `sync`, etc.

Example: `00DOC-20260708-78fb419e-bootstrap`

## Migration Procedures

### Provisional to Stable Migration

When transitioning from `provisional` to `stable`:

1. **Freeze Current State**
   - Tag current bootstrap bundle
   - Document all known patterns
   - Validate against test suite

2. **Establish Versioning**
   - Assign semantic version (e.g., `1.0.0`)
   - Create version directory structure
   - Update bundle loader logic

3. **Update Runtime References**
   - Ensure runtime bundles reference stable versions
   - Test initialization with new structure
   - Update documentation

4. **Validation**
   - Run full test suite
   - Validate all workflow families
   - Verify cross-references

### Backward Compatibility

During migration, maintain backward compatibility:

- Old job states must remain readable
- Existing runtime bundles continue to function
- New features are opt-in where possible

## Migration Checklist

### Pre-Migration

- [ ] All tests passing
- [ ] Documentation complete
- [ ] No open blocking issues
- [ ] Migration plan reviewed

### During Migration

- [ ] Bootstrap bundle tagged
- [ ] Runtime bundles updated
- [ ] Configuration migrated
- [ ] Validation successful

### Post-Migration

- [ ] Smoke tests pass
- [ ] Example workflows run successfully
- [ ] Documentation updated
- [ ] Migration mode updated to `stable`

## Risk Mitigation

### Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking changes in workflow contracts | Medium | High | Comprehensive test suite, backward compatibility layer |
| Runtime bundle incompatibility | Low | High | Version pinning, rollback capability |
| Configuration migration failure | Low | Medium | Automated migration scripts, manual fallback |
| Documentation drift | Medium | Medium | Automated sync workflows, validation |

### Rollback Plan

If migration fails:

1. Identify failure point
2. Restore previous runtime bundle
3. Revert configuration changes
4. Document failure for next attempt

## Timeline

### Provisional Phase (Current)

- **Duration**: Until universal standard stabilizes
- **Activities**: Pattern refinement, documentation updates, feature development
- **Exit Criteria**: Standard is stable, test coverage is comprehensive

### Migration Phase (Future)

- **Duration**: 1-2 weeks
- **Activities**: Version assignment, testing, documentation
- **Deliverables**: Stable bundle version, migration guide

### Stable Phase (Target)

- **Duration**: Ongoing
- **Activities**: Maintenance, minor updates, patch releases
- **Deliverables**: Versioned bundles, changelog, compatibility matrix

## Operational Considerations

### Runtime Bundle Updates

Users update runtime bundles via:

```bash
ukbe-run-agent init
```

This re-seeds from the packaged bootstrap source.

### Custom Workflow Preservation

User-defined workflows in `%USERPROFILE%\.ukbe-runner\workflows\custom/` are preserved during updates.

### Backup and Recovery

Before migration:

```bash
# Backup current runtime
cp -r %USERPROFILE%\.ukbe-runner %USERPROFILE%\.ukbe-runner.backup

# Restore if needed
cp -r %USERPROFILE%\.ukbe-runner.backup %USERPROFILE%\.ukbe-runner
```

## Validation

### Pre-Migration Validation

Validate before each migration:

- All workflow families execute successfully
- All prompts render correctly
- All artifacts are generated
- All cross-references resolve

### Post-Migration Validation

Validate after migration:

- Runtime bundles load correctly
- Jobs execute without errors
- Configuration is valid
- Documentation is complete

---

*Generated by workflow: 00_master_docs_bootstrap_v1 | Step: 03_generate_system_overview_docs | Change: 00DOC-20260708-78fb419e*
