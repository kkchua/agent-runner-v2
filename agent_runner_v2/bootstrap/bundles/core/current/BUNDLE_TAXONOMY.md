---
template_id: "SYS-00-BT"
title: "Bundle Taxonomy"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
managed_by: workflow-generated
generated: "2026-07-10T09:43:38+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Bundle Taxonomy

## Purpose

This document defines the taxonomy of bundles used in the `agent-runner-v2` ecosystem. Bundles are self-contained units of configuration, templates, and assets that workflows consume at runtime.

## Bundle Types

### Core Bundles

Core bundles ship with the package and seed the runtime environment.

| Bundle | Location | Purpose |
|--------|----------|---------|
| `core` | `agent_runner_v2/bootstrap/bundles/core/` | System documentation and governance |
| `workflows` | `agent_runner_v2/bootstrap/workflows/default/` | Workflow definitions and prompts |
| `themes` | `agent_runner_v2/bootstrap/themes/` | HTML/CSS themes for generated sites |

### Runtime Bundles

Runtime bundles live in the user's home directory and are the actual source of truth during execution.

| Bundle | Location | Purpose |
|--------|----------|---------|
| `core` | `%USERPROFILE%\.ukbe-runner\bundles\core\` | Active system documentation |
| `workflows` | `%USERPROFILE%\.ukbe-runner\workflows\<workflow>\` | Active workflow definitions |
| `jobs` | `%USERPROFILE%\.ukbe-runner\jobs\` | Job state and artifacts |

## Bundle Structure

### Core Bundle Layout

```
bundles/core/
├── current/                     # Current version
│   ├── README.md               # Bundle index
│   ├── PROJECT_ANALYSIS.md     # Project analysis
│   ├── SYSTEM_OVERVIEW.md      # System overview
│   ├── DOCUMENTATION_STANDARD.md
│   ├── BUNDLE_TAXONOMY.md      # This file
│   ├── BUNDLE_MIGRATION_PLAN.md
│   ├── BUSINESS_CAPABILITIES.md
│   ├── FUNCTIONAL_SPEC.md
│   ├── NON_FUNCTIONAL_REQUIREMENTS.md
│   ├── SYSTEM_CONTEXT.md
│   ├── COMPONENT_ARCHITECTURE.md
│   ├── DECISION_LOG.md
│   ├── SYSTEM_FILE_STRUCTURE.md
│   ├── DEVELOPER_GUIDE.md
│   ├── RUNBOOK.md
│   └── EXISTING_REPO_WORKFLOW_SOP.md
├── previous/                    # Previous versions (archived)
└── manifest.json               # Bundle manifest
```

### Workflow Bundle Layout

```
workflows/<workflow>/
├── template_groups.py          # Workflow step definitions
├── job_schema.json             # Job state schema
├── llm_response_schema.json    # Meta.json schema
├── model_mapping.json          # Model aliases
└── prompts/
    ├── 00_master_docs_bootstrap_v1/
    │   ├── 02_generate_project_analysis.txt
    │   ├── 03_generate_system_overview_docs.txt
    │   └── ...
    ├── 10_execution_scaffold_v1/
    ├── 20_initiative_intake_v1/
    └── ...
```

### Theme Bundle Layout

```
themes/
└── default/
    ├── layout.html             # Base HTML layout
    ├── styles.css              # CSS styles
    └── assets/                 # Static assets
```

## Bundle Identifiers

### Naming Conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Bundle ID | `<type>_<name>` | `core_default`, `workflow_delivery` |
| Version | `v<major>` | `v1`, `v2` |
| Timestamp | `YYYYMMDD-HHMMSS` | `20260710-094338` |
| Change ID | `00DOC-GEN-<timestamp>-<seq>` | `00DOC-GEN-20260710-004` |

### Bundle Manifest

Each bundle includes a `manifest.json`:

```json
{
  "bundle_id": "core",
  "version": "2026.07.10",
  "created_at": "2026-07-10T09:43:38+08:00",
  "change_id": "00DOC-GEN-20260710-004",
  "workflow": "00_master_docs_bootstrap_v1",
  "documents": [
    {"path": "README.md", "template_id": "SYS-00-IDX"},
    {"path": "SYSTEM_OVERVIEW.md", "template_id": "SYS-00-SO"}
  ],
  "dependencies": [],
  "supersedes": "00DOC-GEN-20260709-003"
}
```

## Bundle Lifecycle

### Creation

1. Workflow generates documents
2. Documents are written to `bootstrap/bundles/<type>/current/`
3. Manifest is generated
4. Bundle is validated

### Seeding

1. `ukbe-run-agent init` copies bundles to `%USERPROFILE%\.ukbe-runner\`
2. Runtime loads from user home, not package
3. Changes require re-seeding or explicit sync

### Archival

1. Previous versions moved to `previous/<timestamp>/`
2. Manifest updated with `superseded_by`
3. Retention policy applied (default: 10 versions)

### Sync

Bootstrap-to-runtime sync is required when:
- Workflow definitions change
- Prompt templates are updated
- Constants are modified
- New workflows are added

## Bundle Relationships

### Dependency Graph

```
core (governance)
    ↑
    └── referenced by all other bundles

workflows (execution)
    ↑
    └── depends on core for standards
    └── consumed by runner at runtime

themes (presentation)
    ↑
    └── depends on core for structure
    └── consumed by site generation
```

### Version Compatibility

| Bundle | Compatible Versions | Notes |
|--------|---------------------|-------|
| core v1 | workflows v1 | Initial release |
| core v2 | workflows v1-v2 | Added new templates |

## Bundle Validation

### Validation Rules

1. **Manifest validation**:
   - Required fields present
   - Version format valid
   - Documents array non-empty

2. **Document validation**:
   - All declared documents exist
   - Frontmatter valid
   - Template IDs match

3. **Cross-reference validation**:
   - Internal links resolve
   - Dependencies exist
   - No circular dependencies

### Validation Tools

| Tool | Purpose |
|------|---------|
| `finalize_bootstrap.py` | Validate and finalize bundles |
| `prepare_delivery_scaffold.py` | Prepare scaffold bundles |

## Best Practices

### For Bundle Authors

1. Always include a manifest
2. Use semantic versioning
3. Document breaking changes
4. Maintain changelog

### For Bundle Consumers

1. Check version compatibility
2. Validate before use
3. Archive old versions
4. Monitor for updates

---

## Related Documents

- [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) — Migration paths
- [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md) — Doc standards

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `03_generate_system_overview_docs` on 2026-07-10T09:43:38+08:00*
