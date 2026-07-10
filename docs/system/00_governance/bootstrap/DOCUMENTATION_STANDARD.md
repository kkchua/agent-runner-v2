---
template_id: "SYS-00-DS"
title: "Documentation Standard - agent-runner-v2"
status: "active"
managed_by: workflow-generated
generated: "2026-07-10T19:47:28+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260710-0098bf53"
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Documentation Standard: agent-runner-v2

## Purpose

This document defines the baseline documentation rules that apply to every repository in the ecosystem, explains how repo-specific profiles and migration modes are selected, and establishes the conventions for document structure, cross-referencing, and validation.

## Audience Model

Documentation serves multiple audiences with different information needs:

| Audience | Primary Need | Typical Background |
|----------|--------------|-------------------|
| **Stakeholders** | Business value, capabilities, governance | Business, product, executive |
| **Developers** | Architecture, APIs, integration patterns | Engineering, implementation |
| **Operators** | Runtime behavior, deployment, procedures | DevOps, SRE, platform |
| **Testers** | Validation criteria, test procedures | QA, validation engineering |
| **End Users** | Usage guidance, features | Application users |

## Document Set

### System Governance Documents (00_governance/bootstrap/)

These documents establish the governance baseline for the repository:

| Document | Template ID | Purpose |
|----------|-------------|---------|
| README.md | SYS-00-IDX | Documentation index and navigation |
| DOCUMENTATION_STANDARD.md | SYS-00-DS | This document — standards and conventions |
| BUNDLE_TAXONOMY.md | SYS-00-BT | Workflow bundle organization |
| BUNDLE_MIGRATION_PLAN.md | SYS-00-BMP | Migration roadmap and posture |
| SYSTEM_OVERVIEW.md | SYS-00-SO | Platform explanation and value flow |
| BUSINESS_CAPABILITIES.md | SYS-00-BC | Operational capabilities |
| FUNCTIONAL_SPEC.md | SYS-00-FS | Core behaviors and capabilities |
| NON_FUNCTIONAL_REQUIREMENTS.md | SYS-00-NFR | Quality and operational requirements |

### Architecture Documents (00_governance/bootstrap/)

| Document | Template ID | Purpose |
|----------|-------------|---------|
| SYSTEM_CONTEXT.md | SYS-00-SC | System boundaries and interfaces |
| COMPONENT_ARCHITECTURE.md | SYS-00-CA | Component structure |
| DECISION_LOG.md | SYS-00-DL | Architectural decisions |
| SYSTEM_FILE_STRUCTURE.md | SYS-00-SFS | Repository organization |
| DEVELOPER_GUIDE.md | SYS-00-DG | Implementation guidance |
| RUNBOOK.md | SYS-00-RB | Operational procedures |
| EXISTING_REPO_WORKFLOW_SOP.md | SYS-00-SOP | Repo workflow SOP |

### Delivery Documents (delivery/)

| Artifact Type | Template | Purpose |
|---------------|----------|---------|
| INIT_FILE | 02_delivery_initiative_template | Initiative definition |
| PLAN_FILE | 03_delivery_plan_template | Delivery plan |
| TASK_GRAPH_FILE | 04_delivery_task_graph_template | Task decomposition |
| TASK_FILE | 05_delivery_task_template | Individual task |
| IMPL_FILE | 06_delivery_impl_template | Implementation plan |
| REVIEW_FILE | 07_delivery_review_template | Review results |
| VALIDATION_FILE | 08_delivery_validation_template | Validation results |

### Codebase Documents (codebase/)

| Document | Purpose |
|----------|---------|
| CODEBASE_INVENTORY.md | Module and component inventory |
| CODEBASE_DOC_SOP.md | Codebase documentation SOP |
| CHANGE_IMPACT.md | Change impact analysis |

## Architecture Baseline

### Universal Documentation Rules

These rules apply to every repository regardless of profile:

1. **Frontmatter Required**: All markdown documents MUST include YAML frontmatter with:
   - `template_id`: Stable identifier for validation
   - `title`: Human-readable document title
   - `status`: Document lifecycle state

2. **Workflow-Generated Banner**: Generated documents MUST include the standard banner immediately after frontmatter.

3. **Cross-Reference Convention**: Internal links use relative paths from the document's location.

4. **Template ID Stability**: Once assigned, template IDs are immutable across document versions.

5. **Status Lifecycle**: Documents progress through: `draft` → `active` → `archived`

### Path Constants

All documentation paths MUST use centralized constants from `agent_runner_v2/constants.py`:

```python
from agent_runner_v2.constants import (
    ARTIFACT_PATH_PROJECT_ANALYSIS,
    FOLDER_KEY_SYSTEM_BOOTSTRAP,
    artifact_path
)
```

**Prohibited**: Hardcoded path strings anywhere in the codebase.

## Repo-Selected Profile

### Profile Definitions

| Profile | Characteristics | Documentation Depth |
|---------|-----------------|---------------------|
| **minimal** | Prototype, exploratory | Essential docs only |
| **provisional** | Active development, migration in progress | Core set, may have gaps |
| **explicit** | Stable, fully documented | Complete documented system |
| **canonical** | Reference implementation | Complete + exemplary |

### Current Profile: `provisional`

The `agent-runner-v2` repository operates under the `provisional` profile:

- Active plugin system migration in progress
- Documentation being established by bootstrap workflows
- Some gaps exist and are being addressed
- Test coverage exists but comprehensive verification ongoing

### Target Profile: `explicit`

Intended end-state:

- All modules documented
- Architecture decisions recorded
- Operational procedures defined
- Validation automated

## Migration Mode

### Migration Posture

The repository is currently in `in_progress` migration mode:

- Legacy `TEMPLATE_GROUPS` monolith being replaced by plugin workflow system
- Documentation being bootstrapped by automated workflows
- Constants and path logic being centralized
- No stable baseline yet established

### Migration Path

1. **Current**: Bootstrap documentation via `00_master_docs_bootstrap_v2`
2. **Next**: Establish stable SOP and templates via `10_execution_scaffold_v1`
3. **Target**: Explicit profile with full documentation coverage

## Conditional Standards

### When Profile = `provisional`

- Generated docs may have incomplete sections
- Architecture decisions may be in flux
- Documentation drift expected; reconciliation workflows required
- Validation may have exceptions

### When Profile = `explicit`

- All documents must pass validation
- No undocumented public APIs
- Architecture decisions must have ADRs
- Drift detection must pass

## Update Triggers

Documentation MUST be refreshed when:

1. **Code changes** affect documented behavior
2. **Architecture decisions** are made or changed
3. **New modules** are added to the codebase
4. **Workflow changes** affect operational procedures
5. **Migration milestones** are reached

## Validation

### Automated Validation

Documentation validation checks:

- Frontmatter presence and format
- Template ID correctness
- Cross-reference validity
- Required section presence
- Section content completeness

### Validation Commands

```bash
# Validate system documents
ukbe-run-agent run --template-group documentation_sync_v1 --step validate

# Validate delivery documents
ukbe-run-agent run --template-group 10_execution_scaffold_v1 --step validate
```

### Validation Artifacts

Validation produces:
- `VALIDATION_FILE` with pass/fail status
- `SYSTEM_DOCS_VALIDATION` with detailed results

## Document Conventions

### Section Headings

Use these exact section headings where applicable:

- `Purpose` — Why this document exists
- `Scope` — What is and isn't covered
- `Audience` — Who should read this
- `Prerequisites` — What to know first
- `Primary Flows` — Main execution paths
- `Key Risks` — Known issues and mitigations

### Cross-References

```markdown
[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)
[Codebase Inventory](../../codebase/01_inventory/codebase_inventory.md)
```

### Code Blocks

Use fenced code blocks with language identifiers:

```python
# Python example
from agent_runner_v2.constants import ARTIFACT_KEY_PROJECT_ANALYSIS
```

---

*Last updated: 2026-07-10T19:47:28+08:00 via workflow `00_master_docs_bootstrap_v2`*
