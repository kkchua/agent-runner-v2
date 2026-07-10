---
template_id: "SYS-00-DS"
title: "Documentation Standard"
status: "active"
change_id: "00DOC-GEN-20260710-004"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
managed_by: workflow-generated
generated: "2026-07-10T09:43:38+08:00"
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Documentation Standard

## Purpose

This document defines the documentation standards for the `agent-runner-v2` repository. It establishes the baseline rules that apply to every repository in the ecosystem, explains how repo-specific profiles are selected, and describes the migration modes for transitioning between standards.

## Audience Model

| Audience | What They Need | How This Doc Helps |
|----------|----------------|-------------------|
| Documentation Authors | Know what to write and where | Clear structure and template requirements |
| Code Reviewers | Validate doc completeness | Checklist and validation criteria |
| New Contributors | Understand the doc system | Overview of organization and conventions |
| Tool Builders | Parse and process docs | Metadata schema and file conventions |

## Document Set

### Ecosystem Document Hierarchy

```
system/                    # Ecosystem-level documentation
├── 00_governance/         # Governance docs (this bootstrap set)
│   └── bootstrap/          # Master system docs
├── 01_architecture/        # Architecture standards
├── 02_engineering/         # Engineering standards
└── 03_operations/          # Operations standards

codebase/                  # Repository-level documentation
├── 00_standards/           # Codebase-specific standards
├── 01_inventory/           # Auto-generated inventory
├── 02_modules/             # Module documentation
├── 03_components/          # Component documentation
└── 04_changes/             # Change impact documents

delivery/                  # Workflow artifacts
├── 01_initiatives/         # Initiative documents
├── 02_plans/               # Delivery plans
├── 03_task_graphs/         # Task graph definitions
├── 04_tasks/               # Task specifications
├── 05_implementations/     # Implementation plans
├── 06_reviews/             # Review documents
└── 08_agents/              # Agent contracts
```

### Document Types

| Type | Location | Purpose | Template ID Prefix |
|------|----------|---------|-------------------|
| Governance | system/00_governance/ | Ecosystem standards and posture | SYS-00-* |
| Architecture | system/01_architecture/ | System architecture docs | SYS-01-* |
| Engineering | system/02_engineering/ | Engineering standards | SYS-02-* |
| Operations | system/03_operations/ | Operational procedures | SYS-03-* |
| Codebase Standards | codebase/00_standards/ | Repo-specific conventions | CBS-* |
| Module Docs | codebase/02_modules/ | Module documentation | MOD-* |
| Component Docs | codebase/03_components/ | Component documentation | COMP-* |
| Change Impact | codebase/04_changes/ | Change impact analysis | CB-04 |
| Delivery | delivery/ | Workflow artifacts | Various |

## Architecture Baseline

### Universal Documentation Rules

These rules apply to **every** repository in the ecosystem:

1. **All markdown documents MUST include YAML frontmatter** with:
   - `template_id`: Unique template identifier
   - `status`: Document status (active, draft, archived)
   - `title`: Human-readable title

2. **Workflow-generated documents are protected**:
   - Marked with `managed_by: workflow-generated` in frontmatter
   - Include the workflow-generated banner after frontmatter
   - Should not be edited manually (changes will be overwritten)

3. **Section requirements are mandatory**:
   - Documents must include all sections defined in their template
   - Section order must match the template specification
   - Section headings must match exactly (case-sensitive)

4. **Artifact paths use centralized constants**:
   - No hardcoded paths in code or documentation
   - All paths reference `constants.py` definitions
   - Path construction uses `ARTIFACT_PATH_*` constants

5. **Meta.json sidecar is the result channel**:
   - All workflow steps report results via `meta.json`
   - Sidecar must follow the v2 schema
   - No markdown write-backs by the runner

## Repo-Selected Profile

### Profile Selection

Repositories select a documentation profile based on their maturity and purpose:

| Profile | Description | When to Use |
|---------|-------------|-------------|
| `provisional` | No clear standard yet; early-stage repo | New projects, experiments |
| `explicit` | Delivery scaffold governance model | Production workflows |
| `minimal` | Essential docs only | Simple tools, libraries |
| `comprehensive` | Full documentation suite | Complex systems, platforms |

### Current Repository Profile

| Field | Value |
|-------|-------|
| `current_profile` | `provisional` |
| `target_profile` | `explicit` (delivery scaffold governance model) |
| `migration_mode` | `bootstrap-in-progress` |
| `repo_state` | `provisional` |

### Profile Assessment Criteria

A repository is `provisional` when:
- No architecture standard document exists
- Documentation is being bootstrapped
- Structure is still evolving

A repository reaches `explicit` when:
- All master system docs are generated
- Delivery scaffold SOPs are in place
- Template registry is populated
- Agent contracts are defined

## Migration Mode

### Bootstrap-In-Progress

The current migration mode is `bootstrap-in-progress`. This means:

1. **Documents are being generated** via the `00_master_docs_bootstrap_v1` workflow
2. **Structure is provisional** and may change during bootstrap
3. **Validation is relaxed** for missing cross-references
4. **Review gates are active** for generated documents

### Migration Path

```
provisional → bootstrap-in-progress → explicit → comprehensive
     ↑                    ↓              ↓
  initial state      validate       enhance
```

### Completion Criteria

To exit `bootstrap-in-progress` and enter `explicit`:
- [x] PROJECT_ANALYSIS.md generated
- [x] System overview docs generated (this step)
- [ ] Architecture docs generated (step 04)
- [ ] Integration docs generated (step 04b)
- [ ] Failure docs generated (step 04c)
- [ ] Architecture flow docs generated (step 04d)
- [ ] Master system docs reviewed (step 05)
- [ ] Master system docs refined (step 06, if needed)

## Conditional Standards

### When to Apply Strict Validation

Strict validation applies when:
- Document status is `active`
- Template ID matches known templates
- Document is not in bootstrap mode

### When to Allow Exceptions

Exceptions are permitted when:
- Document status is `draft`
- Repository is in `bootstrap-in-progress` mode
- Exception is documented in change impact

### Version Compatibility

| Schema Version | Compatible With | Notes |
|----------------|-----------------|-------|
| v2 | Current | Meta.json sidecar schema |
| v1 | Legacy | Fallback for old workflows |

## Update Triggers

### Automatic Updates

Documents are automatically regenerated when:
- Workflow is triggered with `regenerate: true`
- Source code changes affect documentation
- Template requirements change

### Manual Updates

Manual updates require:
1. Change impact document
2. Workflow approval
3. Review gate passage

### Change Classification

| Change Type | Trigger | Action |
|-------------|---------|--------|
| Minor | Typo, formatting | Auto-approve |
| Medium | Section updates | Review required |
| Major | Structure change | Approval gate |

## Validation

### Document Validation Rules

1. **Frontmatter validation**:
   - Required fields present
   - Template ID matches known templates
   - Status is valid value

2. **Structure validation**:
   - All required sections present
   - Section order matches template
   - Headings match exactly

3. **Content validation**:
   - No placeholder text
   - Cross-references resolve
   - Links are valid

4. **Sidecar validation**:
   - Meta.json follows schema
   - Artifacts declared in `produces` exist
   - Status is APPROVED or REJECTED

### Validation Tools

| Tool | Purpose | Location |
|------|---------|----------|
| validate_system_docs.py | System doc validation | actions/ |
| validate_delivery_docs.py | Delivery doc validation | actions/ |
| validate_codebase_docs.py | Codebase doc validation | actions/ |

### Validation Frequency

- **Pre-commit**: Fast validation (frontmatter, structure)
- **CI/CD**: Full validation (content, cross-references)
- **Release**: Complete validation (all rules)

---

## Related Documents

- [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md) — Repository posture assessment
- [BUNDLE_TAXONOMY.md](BUNDLE_TAXONOMY.md) — Bundle organization
- [BUNDLE_MIGRATION_PLAN.md](BUNDLE_MIGRATION_PLAN.md) — Migration guidance

---

*Generated by workflow `00_master_docs_bootstrap_v1` step `03_generate_system_overview_docs` on 2026-07-10T09:43:38+08:00*
