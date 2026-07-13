---
template_id: "SYS-00-IDX"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-13T08:00:00+08:00"
workflow: "00_core_governance_bootstrap_v1"
step: "generate_core_governance_docs"
change_id: "INITIAL-BOOTSTRAP"
---

# System Documentation Index

This document defines the canonical documentation contract for the agent-runner ecosystem. It governs how documentation is structured, owned, and maintained across all repositories that use the agent-runner framework.

## Three-Layer Documentation Model

The agent-runner ecosystem uses a three-layer documentation model that separates concerns by ownership scope and authority level.

### Layer 1: Ecosystem Master Docs

Ecosystem master docs define the universal documentation contract for the entire agent-runner ecosystem. These documents are canonical runtime guidance that apply to all repositories using the framework.

**Ownership**: `00_core_governance_bootstrap_v1` workflow bundle  
**Location**: `docs/system/00_governance/bootstrap/`  
**Authority**: Highest — these docs define the rules all other layers must follow  
**Contents**:
- This index (README.md)
- Documentation standard (DOCUMENTATION_STANDARD.md)
- Bundle taxonomy (BUNDLE_TAXONOMY.md)
- Bundle migration plan (BUNDLE_MIGRATION_PLAN.md)

These four documents are the only files this layer owns. They do not contain repo-derived analysis, codebase inventory, or delivery runtime artifacts.

### Layer 2: Workflow Bundle Master Docs

Workflow bundle master docs travel with each installed workflow bundle into the global runner home. Each workflow package contains its own governance manifest and bundle-local documentation that defines how that specific workflow operates.

**Ownership**: Individual workflow bundles (e.g., `workflows/<name>/`)  
**Location**: Global runner home (`%USERPROFILE%\.ukbe-runner\workflows\<name>\`)  
**Authority**: Bundle-scoped — these docs govern only their owning workflow  
**Contents**: Bundle-specific governance contracts, prompt templates, context extensions, and artifact registry rules

Workflow bundles are self-contained packages that include:
- `workflow.toml` — declarative manifest defining steps, routing, and artifact keys
- `prompts/` — prompt template files
- `context_extensions.py` — optional workflow-specific context hooks
- `bundle_governance/` — bundle-local governance manifests

During publish or install, bundle-local governance files are copied into the global runner home alongside the workflow package.

### Layer 3: Repo-Local Generated Docs

Repo-local generated docs are written under `docs/repo/*` and represent repository-specific outputs produced by scaffold, sync, audience, and repo-document workflows. These docs are **not** canonical governance authority.

**Ownership**: Repo-document and scaffold workflows (including the canonical scaffold workflow and other repo-bootstrap workflows)
**Location**: `docs/repo/*` within each repository
**Authority**: Non-authoritative downstream outputs — these docs reflect repo state at generation time
**Contents**: Repository analysis, codebase inventory, system overviews, audience-facing documentation, and delivery run state

Repo-local docs are generated from scanning a specific repository and should not be treated as ecosystem-wide governance. They belong to the repository that produced them and may be regenerated or discarded as needed.

## Audience Views

Different audiences interact with different layers of the documentation model:

### Ecosystem Maintainers

Ecosystem maintainers work primarily with Layer 1 (ecosystem master docs) and the core runner code under `agent_runner_v2/`. They define the universal documentation contract and ensure workflow bundles comply with it.

### Workflow Authors

Workflow authors create new workflow bundles under `workflows/<name>/` and define bundle-local governance in Layer 2. They follow the contract defined in Layer 1 but do not modify ecosystem master docs.

### Repository Contributors

Repository contributors interact with Layer 3 (repo-local generated docs) when working within a specific repository. They consume repo-analysis outputs but do not treat them as canonical governance. Their authority source is the active workflow bundle and current runner code.

### End Users

End users running workflows interact with generated outputs (Layer 3) and workflow-specific documentation (Layer 2). They do not need to understand the three-layer model unless they are authoring new workflows or contributing to the ecosystem.

## Document Map

The following table maps each ecosystem master doc to its purpose and template ID:

| Document | Template ID | Purpose |
|---|---|---|
| README.md (this file) | SYS-00-IDX | Defines the three-layer documentation model and audience views |
| DOCUMENTATION_STANDARD.md | SYS-00-DS | Specifies the structure, validation, and update triggers for ecosystem master docs |
| BUNDLE_TAXONOMY.md | SYS-00-BT | Defines bundle classes, ownership rules, and packaging requirements |
| BUNDLE_MIGRATION_PLAN.md | SYS-00-BMP | Describes migration from legacy mixed-doc models toward the three-layer model |

All four documents are owned by `00_core_governance_bootstrap_v1` and located under `docs/system/00_governance/bootstrap/`.

## Canonical Scaffold Workflow

The canonical scaffold workflow for repository bootstrapping in this ecosystem is `10_execution_scaffold_v2`. This workflow scans a repository and generates repo-local documentation inputs and system-analysis outputs under `docs/repo/*`. It is not a core-governance workflow and does not own ecosystem master docs.

## Governance Boundaries

The following boundaries are hard constraints in this ecosystem:

- **Global governance docs** (Layer 1) are canonical runtime guidance. They define rules, not repo state.
- **Workflow bundle master docs** (Layer 2) own bundle-local governance. They travel with each installed bundle.
- **Repo-generated docs** (Layer 3) live under `docs/repo/*`. They are non-authoritative downstream outputs.
- **Repo-generated docs are not canonical governance authority**. They reflect repository state at generation time and may become stale.

No workflow or document outside `00_core_governance_bootstrap_v1` may modify the four ecosystem master docs. No ecosystem master doc may claim ownership of repo-local outputs under `docs/repo/*`.
