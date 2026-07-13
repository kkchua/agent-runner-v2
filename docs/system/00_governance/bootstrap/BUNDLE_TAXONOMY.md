---
template_id: "SYS-00-BT"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-13T23:04:55+08:00"
workflow: "00_core_governance_bootstrap_v1"
step: "generate_core_governance_docs"
change_id: "00CORE-20260713-7d31e8d4"
---

# Bundle Taxonomy

This document defines the canonical bundle classification system for the agent-runner ecosystem. It specifies bundle classes, ownership rules, and packaging requirements that maintain clear authority boundaries across all workflow packages.

## Bundle Classes

The ecosystem recognizes exactly one concrete bundle class with canonical governance authority:

### Core Governance Bundles

**Purpose**: Define universal documentation contracts and three-layer model rules applicable across all repositories and workflow bundles.

**Scope**:
- Govern ecosystem master docs under `docs/system/00_governance/bootstrap/`
- Establish documentation standards, validation criteria, and update triggers
- Define bundle taxonomy and migration strategies
- Enforce ownership boundaries between ecosystem, bundle, and repo-local layers

**Canonical Example**: `00_core_governance_bootstrap_v1`

**Ownership Rules**:
- Owned exclusively by the `00_core_governance_bootstrap_v1` workflow bundle
- No other workflow may modify core governance bundle contents
- Changes require deterministic review, validation, and audit approval
- Must not claim ownership of repo-derived analysis or delivery outputs

**Artifact Set**: Limited to four canonical files plus transient review/validation outputs:
- README.md (SYS-00-IDX)
- DOCUMENTATION_STANDARD.md (SYS-00-DS)
- BUNDLE_TAXONOMY.md (SYS-00-BT)
- BUNDLE_MIGRATION_PLAN.md (SYS-00-BMP)

Other bundle classes exist in the ecosystem but are subordinate to core governance bundles. They operate within Layer 2 (workflow bundle master docs) or Layer 3 (repo-local generated docs) and must conform to the rules defined by core governance bundles. When conflicts arise between bundle-local docs and core governance docs, the core governance docs win.

## Ownership Rules

Bundle ownership follows strict hierarchical rules that prevent authority confusion and documentation drift:

### Hierarchical Authority

1. **Core governance bundles** hold supreme authority over ecosystem-wide documentation contracts. Their rules apply universally and cannot be overridden by subordinate bundles.

2. **Workflow bundle master docs** (Layer 2) own their specific workflow's domain but must not contradict core governance rules. Each bundle carries its master docs into the global runner home during publish and install operations.

3. **Repo-local generated docs** (Layer 3) are downstream outputs produced by repository-scanning workflows. They have no governance authority and must conform to both Layer 1 and Layer 2 rules.

### Non-Overlap Principle

No two bundles may claim ownership of the same artifact path or documentation domain. Explicit separation prevents:

- Conflicting instructions across multiple governance sources
- Stale assumptions propagating from deprecated bundles
- Validation gaps where no bundle claims responsibility

When a new bundle is created, its `bundle_governance.toml` manifest must declare its artifact registry and explicitly exclude paths owned by existing bundles. The core governance bundle validates this declaration during bundle installation.

### Conflict Resolution

When prompt instructions, stale repo docs, or bundle-local guidance conflict with core governance docs:

1. Core governance docs win unconditionally
2. Conflicting content in subordinate layers must be marked as deprecated
3. Bundle refinement loops update only the affected core governance files
4. Validation gates reject updates that violate ownership boundaries

## Packaging Rules

Bundle packaging enforces consistent structure, discoverability, and runtime deployment across all workflow packages.

### Package Structure

Each workflow bundle resides under `workflows/<name>/` and contains:

```
workflows/<name>/
├── workflow.toml          # Declarative manifest (steps, routing, artifact keys)
├── prompts/               # Prompt template files for each step
├── actions.py             # Optional Python action implementations
├── bundle_governance/     # Bundle-local master docs and extensions
│   ├── <governance>.md    # Canonical bundle-specific governance docs
│   ├── extensions/        # Governance extension rules
│   └── generated/         # Auto-generated adapter files (AGENTS.md, CLAUDE.md, QWEN.md)
└── context_extensions.py  # Optional workflow-specific context hooks
```

### Dual-Path Discovery

Plugin workflow packages use dual-path discovery for runtime deployment:

1. **Global runner home** (`%USERPROFILE%\.ukbe-runner\workflows\<workflow_name>\`): Primary location where installed bundles reside. Bundle-local master docs travel here during publish/install operations.

2. **Local repository fallback** (`workflows/<name>/` within individual repos): Secondary location used during development or when global installation is unavailable.

The adapter pattern converts `WorkflowBundle` objects into the same dict format that legacy monolithic configurations produced, ensuring zero changes to the existing execution pipeline (`step_runner.py`, `workflow_router.py`, `coder_adapters.py`, `job_state.py`).

### Manifest Requirements

Every `workflow.toml` must include:

- `[workflow]` section with name, version, label, description, and visibility
- `[[step]]` entries defining each execution step with prompt/action references
- `[step.artifacts]` sections declaring produces, required_inputs, and result_meta_key
- `[step.coder]` sections specifying allowed roles and default_role

Bundle governance manifests under `bundle_governance/` must declare their artifact registry and ownership boundaries explicitly. The `core_governance.md` file within each bundle's governance directory serves as the canonical source of truth for that bundle's scope.

### Versioning and Migration

Bundle versions follow semantic versioning (MAJOR.MINOR.PATCH). Major version increments indicate breaking changes to the documentation contract or ownership boundaries. Minor increments add new capabilities without modifying existing rules. Patch increments fix errors or clarify ambiguous language.

Migration from legacy bundle models to the current three-layer architecture proceeds through defined phases documented in BUNDLE_MIGRATION_PLAN.md. During migration, legacy bundles remain operational but are marked as deprecated. New bundles must conform to the three-layer model from inception.
