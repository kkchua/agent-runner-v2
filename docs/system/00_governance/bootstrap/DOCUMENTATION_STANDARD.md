---
template_id: "SYS-00-DS"
title: "Documentation Standard"
status: "active"
generated: "2026-07-10T14:07:00+08:00"
workflow: "00_master_docs_bootstrap_v2"
step: "03_generate_system_overview_docs"
change_id: "00DOC-GEN-20260710-004"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v2` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Documentation Standard

## Purpose

This document defines the documentation requirements for the `agent-runner-v2` repository. It establishes:

1. **Baseline rules** that apply to every repository in the ecosystem
2. **Repo-selected profiles** that reflect this repository's current posture
3. **Migration modes** that indicate how standards are being adopted

## Audience Model

| Audience | Documentation Needs | Primary Sources |
|----------|---------------------|-----------------|
| **Stakeholders** | Why this exists, what it enables | System docs, business capabilities |
| **Developers** | How it works, how to extend | Functional spec, developer guide |
| **Operators** | How to run, troubleshoot | Runbook, system overview |
| **Contributors** | How to participate | Documentation standard, developer guide |

## Document Set

### System Documentation

System documentation lives in `docs/system/` and explains the platform holistically:

| Document | Purpose | Maintained By |
|----------|---------|---------------|
| SYSTEM_OVERVIEW | Platform purpose and value flow | Bootstrap workflow |
| BUSINESS_CAPABILITIES | Operational capabilities | Bootstrap workflow |
| FUNCTIONAL_SPEC | Functional scope and behaviors | Bootstrap workflow |
| NON_FUNCTIONAL_REQUIREMENTS | Quality and runtime expectations | Bootstrap workflow |
| SYSTEM_CONTEXT | External boundaries and interfaces | Bootstrap workflow |
| COMPONENT_ARCHITECTURE | Component breakdown | Bootstrap workflow |
| DECISION_LOG | Architectural decisions | Bootstrap workflow |
| DEVELOPER_GUIDE | Development setup | Bootstrap workflow |
| RUNBOOK | Operational procedures | Bootstrap workflow |

### Codebase Documentation

Codebase documentation lives in `docs/codebase/` and tracks the repository state:

| Document | Purpose | Maintained By |
|----------|---------|---------------|
| CODEBASE_INVENTORY | Module and component inventory | Reconcile workflow |
| Module docs (02_modules/) | Per-module documentation | Reconcile workflow |
| Component docs (03_components/) | Cross-cutting concerns | Reconcile workflow |
| Change impact docs (04_changes/) | Change tracking | Reconcile workflow |

### Delivery Documentation

Delivery documentation lives in `docs/delivery/` and tracks initiatives and tasks:

| Document | Purpose | Maintained By |
|----------|---------|---------------|
| Initiatives | Planned and in-flight work | Initiative workflows |
| Plans | Delivery plans for initiatives | Planning workflows |
| Tasks | Implementation tasks | Execution workflows |
| Reviews | Review outcomes | Execution workflows |

## Architecture Baseline

### Universal Documentation Requirements

Every repository in this ecosystem must maintain:

1. **System documentation** in `docs/system/` covering:
   - Platform overview and purpose
   - Functional scope and capabilities
   - Operational characteristics

2. **Codebase documentation** in `docs/codebase/` covering:
   - Current repository structure
   - Module inventory
   - Recent changes

3. **Delivery documentation** in `docs/delivery/` covering:
   - Active initiatives
   - Delivery plans
   - Task execution records

### Documentation Format Standards

All markdown documents must include:

```yaml
---
template_id: "TEMPLATE-XXX"
title: "Document Title"
status: "active"
generated: "2026-07-10T14:07:00+08:00"
workflow: "workflow_name"
step: "step_name"
change_id: "CHANGE-ID"
managed_by: workflow-generated
---
```

All documents must carry the workflow-generated protection banner after frontmatter.

### Directory Structure Standard

```
docs/
├── system/              # Platform documentation
│   ├── 00_governance/   # Master docs, standards
│   ├── 01_context/      # System context
│   ├── 10_architecture/ # Component architecture
│   └── 20_operations/   # Runbooks, guides
├── codebase/            # Repository documentation
│   ├── 01_inventory/    # Codebase inventory
│   ├── 02_modules/      # Module documentation
│   ├── 03_components/   # Component documentation
│   └── 04_changes/      # Change impact documents
└── delivery/            # Delivery documentation
    ├── 01_initiatives/  # Initiative drafts
    ├── 02_drafts/       # Draft documents
    ├── 03_plans/        # Delivery plans
    ├── 04_tasks/        # Task definitions
    ├── 05_implementations/ # Implementation records
    └── 06_reviews/      # Review outcomes
```

## Repo-Selected Profile

This repository follows the **`provisional` → `structured` profile**:

| Aspect | Current State | Target State |
|--------|---------------|--------------|
| **Documentation coverage** | Partial | Comprehensive |
| **Update automation** | Workflow-driven | Fully automated |
| **Validation** | Manual | Automated |
| **Cross-reference integrity** | Best effort | Guaranteed |

### Current Profile Characteristics

- **Monolithic workflow registry** (`template_groups.py`, 2,453 lines) indicates provisional structure
- **Plugin migration in progress** toward structured workflow packages
- **Centralized constants** (`constants.py`, 1,342 lines) indicate structured path management
- **Comprehensive test coverage** (45+ unit tests) indicates structured quality approach

### Target Profile

- Self-contained workflow packages with `workflow.toml` manifests
- Automated documentation reconciliation on code changes
- Validated cross-references between documents
- Deterministic artifact paths via centralized constants

## Migration Mode

**Status**: `in_progress`

### Migration Activities

| Activity | Status | Target Completion |
|----------|--------|-------------------|
| Plugin-based workflows | In progress | TBD |
| Centralized constants | Complete | Done |
| Documentation automation | In progress | TBD |
| Test isolation | Complete | Done |

### Provisional Elements

The following elements reflect provisional posture:

- Monolithic `template_groups.py` with 21 hardcoded workflows
- Workflow package system migration incomplete
- Manual documentation synchronization required

### Structured Elements

The following elements reflect structured posture:

- Centralized artifact path constants in `constants.py`
- Strict sidecar contract (v2) for workflow communication
- Comprehensive unit/integration test split
- Deterministic runner action separation

## Conditional Standards

### For Workflow-Generated Documents

Workflow-generated documents must:

1. Include the `managed_by: workflow-generated` frontmatter field
2. Display the workflow protection banner after frontmatter
3. Reference the generating workflow and step
4. Not be manually edited

### For Hand-Written Documents

Hand-written documents should:

1. Include appropriate frontmatter without `managed_by` field
2. Follow markdown style conventions
3. Reference related documents explicitly
4. Be peer-reviewed before commit

### For Code Documentation

Code modules should:

1. Include module-level docstrings explaining purpose
2. Document public functions with type hints
3. Reference related modules
4. Follow the codebase documentation conventions in `CODER_IMPLEMENTATION_SOP.md`

## Update Triggers

### Automatic Updates

The following trigger automatic documentation updates:

| Trigger | Workflow | Documents Updated |
|---------|----------|-------------------|
| Repository scan | `40_documentation_sync_v1` | Codebase inventory, module docs |
| Bootstrap workflow | `00_master_docs_bootstrap_v2` | System documentation |
| Delivery scaffold | `10_execution_scaffold_v1` | Delivery templates, SOPs |
| Task execution | `31_task_execution_v1` | Task records, review outcomes |

### Manual Updates

The following require manual intervention:

- Architectural decision records (ADR)
- Runbook procedures
- Developer guide updates for new patterns

## Validation

### Document Validation Requirements

Documents must pass:

1. **Structure validation** — Required sections present
2. **Frontmatter validation** — Required fields populated
3. **Reference validation** — Linked documents exist
4. **Style validation** — Follows markdown conventions

### Validation Workflow

Validation is performed by:

- `validate_codebase_docs.py` — Codebase documentation validation
- `validate_system_docs.py` — System documentation validation
- `validate_delivery_docs.py` — Delivery documentation validation

### Validation Results

Results are recorded in:

- `docs/codebase/04_changes/*-validation.md` — Codebase validation
- Validation sidecar files (`*.meta.json`) alongside validated documents

---

## Related Documents

- [README.md](README.md) — System documentation index
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) — Platform overview
- [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md) — Repository analysis and posture

---

*Generated by workflow: `00_master_docs_bootstrap_v2` — Step: `03_generate_system_overview_docs`*
