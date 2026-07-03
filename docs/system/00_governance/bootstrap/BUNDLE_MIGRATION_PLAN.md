---
template_id: "SYS-00-BMP"
title: "Bundle Migration Plan - agent-runner-v2"
status: "active"
generated: "2026-07-04T08:00:00+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260704-001"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Migration Plan

## Purpose

This document defines the migration path for bundle format evolution in agent-runner-v2. It records historical changes, current version status, and future migration steps.

**Why:** Bundle formats evolve as the platform grows. A clear migration plan ensures smooth transitions and preserves backward compatibility where possible.

## Current Version

| Attribute | Value |
|-----------|-------|
| **Current Version** | v1 |
| **Status** | Stable |
| **Introduced** | 2026-07-03 |
| **Deprecated** | — |

## Version History

### v1 (Current)

**Introduced:** 2026-07-03  
**Status:** Active and stable

#### Features

- Core bundle with system documentation
- Workflow bundles with template groups and prompts
- Domain bundles for specialized documentation
- Bundle manifest (`bundle-set.json`) for selection tracking
- Artifact key taxonomy for delivery workflows

#### Structure

```
%USERPROFILE%\.ukbe-runner/
├── bundles/
│   └── core/                    # System documentation
├── workflows/
│   └── default/                 # Workflow definitions
│       ├── template_groups.py
│       ├── job_schema.json
│       ├── llm_response_schema.json
│       ├── model_mapping.json
│       ├── usage_schema.json
│       └── prompts/
└── bundle-set.json              # Bundle selection manifest
```

## Migration Scenarios

### Scenario: New Bundle Version

When a v2 bundle format is introduced:

1. **Update package** — New bootstrap includes v2 structures
2. **Runtime detection** — Runner detects bundle version at load
3. **Migration path** — Automatic or manual migration as needed
4. **Backward compatibility** — v1 bundles continue to work

### Scenario: Domain Bundle Addition

When adding a new domain bundle:

1. **Define domain** — Create domain taxonomy
2. **Create templates** — Add domain-specific templates
3. **Update manifest** — Register in bundle taxonomy
4. **Document** — Update BUNDLE_TAXONOMY.md

### Scenario: Workflow Family Addition

When adding a new workflow family:

1. **Define steps** — Add to template_groups.py
2. **Create prompts** — Add prompt templates
3. **Test** — Validate workflow execution
4. **Document** — Update relevant documentation

## Backward Compatibility

### Compatibility Guarantees

| Version | Compatible With | Notes |
|---------|-----------------|-------|
| v1 | v1 | Current version |

### Breaking Changes

No breaking changes are planned for v1.

Future v2 may introduce:
- Revised schema structures
- New artifact key categories
- Enhanced domain bundle support

## Future Considerations

### Potential v2 Features

1. **Hierarchical bundles** — Bundle inheritance and composition
2. **Versioned workflows** — Workflow family versioning
3. **Conditional prompts** — Platform-specific prompt variants
4. **Plugin bundles** — Third-party extension support

### Migration Timeline

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| v1 stable | 2026-07-03 | Initial release |
| v2 design | TBD | Design phase for next version |
| v2 alpha | TBD | Alpha testing |
| v1 deprecation | TBD | Announce v1 deprecation |
| v1 EOL | TBD | End of life for v1 |

## Migration Procedures

### Bundle Initialization

New installations receive the current bundle version:

```bash
ukbe-run-agent init
```

This seeds `%USERPROFILE%\.ukbe-runner\` with the current bundle format.

### Bundle Update

Updates are applied via:

```bash
ukbe-run-agent init --force
```

This refreshes the runtime bundle from the packaged bootstrap.

**Note:** Customizations in the runtime bundle may be overwritten. Back up before forcing.

### Bundle Validation

Validate bundle integrity:

```bash
ukbe-run-agent validate-bundle
```

Checks:
- Schema compliance
- Required files present
- Cross-references resolve

## Rollback

If a bundle update causes issues:

1. **Restore from backup** — Manual restoration of `.ukbe-runner\`
2. **Re-init with previous package** — Install previous package version
3. **Report issue** — File issue with bundle version and error details

---

*Generated: 2026-07-04T08:00:00+08:00*
*Workflow: 00_master_docs_bootstrap_v1 / Step: 03_generate_system_overview_docs*
*Change ID: 00DOC-GEN-20260704-001*
