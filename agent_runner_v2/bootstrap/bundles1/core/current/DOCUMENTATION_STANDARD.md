---
template_id: "SYS-00-DS"
title: "Documentation Standard - agent-runner-v2"
status: "active"
generated: "2026-07-08T23:10:23+08:00"
workflow: "00_master_docs_bootstrap_v1"
step: "03_generate_system_overview_docs"
change_id: "00DOC-20260708-78fb419e"
managed_by: workflow-generated
---

> Managed by workflow: `00_master_docs_bootstrap_v1` / step: `03_generate_system_overview_docs`
> This file is workflow-generated and protected from manual edits.

# Documentation Standard

## Purpose

This document defines the documentation standards for the `agent-runner-v2` repository. It establishes the baseline rules that apply to every repository, explains how repo-specific profiles are selected, and describes the migration modes available for documentation governance.

## Audience Model

### Primary Audiences

| Audience | Role | Information Needs |
|----------|------|-------------------|
| Stakeholders | Business decision-makers, product managers | Business value, capabilities, high-level architecture |
| Developers | Software engineers, integration developers | Functional specs, API contracts, implementation details |
| Operators | DevOps engineers, system administrators | Runtime requirements, operational procedures, troubleshooting |
| Functional Consumers | Workflow authors, end users | Usage patterns, workflow capabilities, functional behaviors |

### Audience-Specific Documentation

Documentation is organized into audience-specific views:

- **Stakeholder View**: Focus on business value, capabilities, and high-level system overview
- **Developer View**: Focus on implementation details, functional specifications, and technical standards
- **Operator View**: Focus on operational requirements, procedures, and system health
- **Functional Consumer View**: Focus on usage patterns, workflow families, and functional capabilities

## Document Set

### Universal Baseline Documents

Every repository must maintain these core documents:

| Document | Template ID | Required | Purpose |
|----------|-------------|----------|---------|
| README.md | SYS-00-IDX | Yes | Documentation index and entry point |
| PROJECT_ANALYSIS.md | SYS-00-PA | Yes | Repository analysis and architecture posture |
| DOCUMENTATION_STANDARD.md | SYS-00-DS | Yes | This document — documentation conventions |

### Repository-Specific Documents

Based on repository type and complexity, additional documents may be required:

| Document Category | Documents | When Required |
|-------------------|-----------|---------------|
| Overview | SYSTEM_OVERVIEW, BUSINESS_CAPABILITIES, FUNCTIONAL_SPEC, NON_FUNCTIONAL_REQUIREMENTS | All repositories |
| Architecture | SYSTEM_CONTEXT, COMPONENT_ARCHITECTURE, DECISION_LOG, SYSTEM_FILE_STRUCTURE | Medium+ complexity |
| Operations | DEVELOPER_GUIDE, RUNBOOK, EXISTING_REPO_WORKFLOW_SOP | Medium+ complexity |

### Generated vs. Manual Documents

| Type | Rule |
|------|------|
| Workflow-Generated | Created by `00_master_docs_bootstrap_v1` and subsequent workflows; protected from manual edits |
| Manual | Created and maintained by human authors; subject to standard review processes |
| Hybrid | Generated with manual sections clearly marked and preserved |

## Architecture Baseline

### Universal Documentation Rules

These rules apply to every repository regardless of profile:

1. **Frontmatter Required**: All system documents must include YAML frontmatter with `template_id`, `title`, `status`, `generated`, `workflow`, `step`, and `change_id`
2. **Workflow-Generated Protection**: Documents with `managed_by: workflow-generated` are protected from manual edits
3. **Artifact Key Placeholders**: Prompt templates must use `{ARTIFACT_KEY}` placeholders instead of hardcoded paths
4. **Centralized Constants**: All documentation paths must use `constants.py` as the single source of truth
5. **Section Headings**: Use exact section headings as specified in generation prompts
6. **Cross-References**: Use relative paths for internal links; validate on generation
7. **Change Tracking**: Every document change must be tracked with a change ID

### File Organization Baseline

```
docs/
├── system/
│   └── 00_governance/bootstrap/     # System documentation (master docs)
├── codebase/
│   ├── 01_inventory/                 # Codebase inventory
│   ├── 02_modules/                   # Module documentation
│   ├── 03_components/                # Component documentation
│   └── 04_changes/                   # Change impact documents
├── delivery/
│   ├── 01_initiatives/               # Initiative documents
│   ├── 02_plans/                     # Delivery plans
│   ├── 03_tasks/                     # Task documents
│   └── ...
└── site/                             # Generated architecture sites
```

## Repo-Selected Profile

### Profile Selection

Repositories select a documentation profile based on their characteristics:

| Profile | Characteristics | Documentation Depth |
|---------|-----------------|---------------------|
| `minimal` | Simple scripts, single-purpose tools | Index + README only |
| `standard` | Typical application/service | Full system docs + basic architecture |
| `comprehensive` | Complex platform, multiple services | Full system docs + detailed architecture + operations |

### Current Repository Profile

**Repository**: `agent-runner-v2`
**Selected Profile**: `comprehensive`
**Rationale**: Multi-component platform with workflow orchestration, backend integration, and complex documentation requirements

### Profile-Specific Requirements

For `comprehensive` profile:

- All 18 master documents must be generated
- Module-level documentation for all Python modules
- Component documentation for workflow families
- Change impact tracking for all significant changes
- Architecture site generation capability

## Migration Mode

### Migration Modes

| Mode | Description | When to Use |
|------|-------------|-------------|
| `greenfield` | New repository with no existing documentation | New projects |
| `provisional` | Existing patterns with evolving universal abstraction | Active development |
| `migrating` | Explicit migration from old standard to new | Legacy projects |
| `stable` | Fully aligned with universal baseline | Mature projects |

### Current Migration Posture

**Current Mode**: `provisional`
**Explanation**: The repository has established patterns (centralized constants, defined workflow families) but the universal abstraction is still evolving. The repo serves as a testbed for the comprehensive documentation standard.

### Migration Path

1. **Current**: Provisional mode with comprehensive profile
2. **Target**: Stable mode with comprehensive profile
3. **Blockers**: None identified
4. **Timeline**: As universal standard stabilizes

## Conditional Standards

### Conditional Based on Repository Type

| Condition | Standard Application |
|-----------|----------------------|
| Python package | Full module documentation required |
| CLI tool | Command reference documentation required |
| Web service | API documentation required |
| Workflow engine | Workflow family documentation required |

### Conditional Based on Complexity

| Complexity | Documentation Depth |
|------------|---------------------|
| < 1000 LOC | Minimal profile |
| 1000-5000 LOC | Standard profile |
| > 5000 LOC | Comprehensive profile |

## Update Triggers

### Automatic Updates

Documentation is automatically regenerated when:

- Workflow `00_master_docs_bootstrap_v1` is executed
- Codebase sync workflow detects significant changes
- New workflow families are added
- Architecture decisions are recorded

### Manual Updates

Manual updates may be triggered by:

- Architecture decision records (DECISION_LOG.md)
- Significant feature additions
- Breaking changes to APIs or workflows
- Operational incident post-mortems

### Update Process

1. Identify trigger (automatic or manual)
2. Execute appropriate workflow step
3. Review generated changes
4. Validate against current repository state
5. Commit with descriptive message

## Validation

### Validation Rules

| Rule | Method | Frequency |
|------|--------|-----------|
| Frontmatter complete | Schema validation | Every generation |
| Cross-references valid | Link checking | Every generation |
| Section headings match | Template validation | Every generation |
| Protected docs unchanged | Git diff | Continuous |
| Paths use constants | Code review | PR review |

### Validation Failures

Validation failures are handled according to severity:

| Severity | Handling |
|----------|----------|
| Blocking | Workflow step fails, no artifacts written |
| Warning | Logged, artifacts written with warnings |
| Info | Logged only, no action required |

### Validation Tools

- `documentation_validation_core.py`: Core validation logic
- `validate_system_docs.py`: System documentation validation
- `validate_codebase_docs.py`: Codebase documentation validation
- `validate_delivery_docs.py`: Delivery documentation validation

---

*Generated by workflow: 00_master_docs_bootstrap_v1 | Step: 03_generate_system_overview_docs | Change: 00DOC-20260708-78fb419e*
