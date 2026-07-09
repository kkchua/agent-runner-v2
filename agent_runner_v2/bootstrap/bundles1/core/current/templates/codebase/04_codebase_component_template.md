---
template_id: "CODEBASE-COMP-v1"
title: "Codebase Component Template"
status: "active"
generated: "2026-07-09T10:35:00+08:00"
workflow: "10_execution_scaffold_v1"
step: "07_generate_templates"
change_id: "10SCAFFOLD-20260708-8a4445fc"
managed_by: workflow-generated
---

> Managed by workflow: `10_execution_scaffold_v1` / step: `generate_templates`
> This file is workflow-generated and protected from manual edits.

# Metadata

- **Template ID**: CODEBASE-COMP-v1
- **Artifact Key**: `CODEBASE_COMPONENT_TEMPLATE`
- **Version**: 1.0
- **Owner**: Codebase Documentation Workflow
- **Purpose**: Documents higher-level components (packages, suites) with component overview, file coverage, interface, implementation details, dependencies, testing, change log, documentation governance, and notes

# Component Overview

**Component Name**: `[component_name]`

**Component Type**: [package/suite/subsystem/layer]

**Root Path**: `agent_runner_v2/[path/to/component]/`

**Documentation Path**: `docs/codebase/03_components/[component_name].md`

**Summary**: [2-3 sentence description of what this component does and why it exists as a cohesive unit]

**Key Responsibilities**:
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

**Complexity**: [LOW/MEDIUM/HIGH]

**Module Count**: [Number of modules in this component]

**Total Lines of Code**: [Approximate line count across all modules]

## Constituent Modules

[List all modules that comprise this component]

| Module | Path | Purpose | Lines |
|--------|------|---------|-------|
| [module_name] | `agent_runner_v2/[path]/[module].py` | [Brief purpose] | [N] |
| [module_name] | `agent_runner_v2/[path]/[module].py` | [Brief purpose] | [N] |

# File Coverage

## Source Files

[Enumerate all source files in this component]

| File | Type | Purpose | Lines | Last Modified |
|------|------|---------|-------|---------------|
| `[file].py` | module | [Purpose] | [N] | [Date] |
| `[file].py` | module | [Purpose] | [N] | [Date] |
| `__init__.py` | package init | Package initialization | [N] | [Date] |

## Test Files

[List test files covering this component]

| Test File | Type | Coverage | Location |
|-----------|------|----------|----------|
| `test_[component].py` | unit/integration | [XX%] | `tests/unit/` or `tests/integration/` |
| `test_[module].py` | unit/integration | [XX%] | `tests/unit/` or `tests/integration/` |

## Related Documentation

[List documentation files related to this component]

| Document | Path | Purpose | Status |
|----------|------|---------|--------|
| Component Doc | `docs/codebase/03_components/[component_name].md` | Component documentation | current |
| Module Docs | `docs/codebase/02_modules/[module].md` | Individual module docs | current |
| Change Impact | `docs/codebase/04_changes/CHANGE-IMPACT-[NNN].md` | Change tracking | current |

# Interface

## Public API Surface

[Describe the public API this component exposes to other components]

### Exported Classes

[List classes other components can import from this component]

```python
from agent_runner_v2.[component] import ClassName
```

| Class | Module | Purpose |
|-------|--------|---------|
| `ClassName` | `[module].py` | [Brief purpose] |

### Exported Functions

[List functions other components can call]

```python
from agent_runner_v2.[component].[module] import function_name
```

| Function | Module | Purpose |
|----------|--------|---------|
| `function_name()` | `[module].py` | [Brief purpose] |

### Exported Constants

[List constants other components may reference]

| Constant | Module | Value/Purpose |
|----------|--------|---------------|
| `CONSTANT_NAME` | `[module].py` | [Value or description] |

## Integration Points

[Describe how this component integrates with other components]

### Consumes From

[List components this component depends on]

| Component | What It Consumes | Purpose |
|-----------|------------------|---------|
| `[component_name]` | [Classes/functions/constants] | [Why needed] |

### Provides To

[List components that depend on this component]

| Component | What They Consume | Purpose |
|-----------|-------------------|---------|
| `[component_name]` | [What they get from us] | [Why they need it] |

## Configuration Interface

[Describe configuration this component reads or requires]

| Configuration Key | Source | Purpose | Default |
|-------------------|--------|---------|---------|
| `[config_key]` | `.env` / `config.json` / constants.py | [What it controls] | [Default value] |

# Implementation Details

## Architecture

[Describe internal architecture of this component]

**Architectural Pattern**: [e.g., Layered architecture, Plugin architecture, Pipeline pattern]

**Key Design Decisions**:
- [Decision 1: e.g., "Separation of concerns between prompt rendering and execution"]
- [Decision 2: e.g., "Centralized path constants to avoid hardcoded strings"]

**Data Flow**:
[Describe how data flows through this component]

```
[Input] → [Processing Stage 1] → [Processing Stage 2] → [Output]
```

## Key Algorithms

[Document any significant algorithms or logic within this component]

### Algorithm: [Algorithm Name]

**Purpose**: [What problem this algorithm solves]

**Approach**: [High-level description of approach]

**Complexity**: [Time/space complexity if relevant]

**Implementation**:
```python
# Simplified example
def key_algorithm(input_data):
    """Implements [algorithm name]"""
    # Step 1: [Description]
    intermediate = process_step_1(input_data)
    
    # Step 2: [Description]
    result = process_step_2(intermediate)
    
    return result
```

## State Management

[Describe how this component manages state]

**State Type**: [Stateless / In-memory state / Persistent state / Mixed]

**State Storage**: [Where state is stored: variables, files, database, etc.]

**State Lifecycle**: [When state is created, updated, and destroyed]

**Concurrency Considerations**: [Any thread-safety or concurrency concerns]

## Error Handling

[Describe error handling strategy for this component]

**Error Types**: [What kinds of errors this component handles]

**Error Propagation**: [How errors are propagated to callers]

**Recovery Strategies**: [What recovery mechanisms exist]

**Logging**: [What this component logs and at what levels]

# Dependencies

## Internal Dependencies

[List dependencies on other components within agent_runner_v2]

| Component | Modules Used | Purpose | Coupling Level |
|-----------|--------------|---------|----------------|
| `[component_name]` | `[module1]`, `[module2]` | [Why needed] | LOW/MEDIUM/HIGH |

## External Dependencies

[List external library dependencies specific to this component]

| Library | Version | Purpose | Optional |
|---------|---------|---------|----------|
| [Library name] | [Version] | [What it's used for] | YES/NO |

## Runtime Dependencies

[List runtime requirements not captured by imports]

- [Requirement 1: e.g., "Requires .env file for credentials"]
- [Requirement 2: e.g., "Requires git CLI available in PATH"]
- [Requirement 3: e.g., "Requires write access to job directory"]

# Testing

## Test Strategy

[Describe how this component is tested]

**Unit Tests**: [What aspects are covered by unit tests]

**Integration Tests**: [What aspects require integration testing]

**End-to-End Tests**: [What aspects require full workflow testing]

**Manual Testing**: [What aspects require manual verification]

## Test Coverage

[Summarize test coverage for this component]

| Metric | Value |
|--------|-------|
| Overall Coverage | [XX%] |
| Modules Covered | [N out of M modules] |
| Critical Paths Covered | [YES/NO/PARTIAL] |
| Edge Cases Covered | [List or describe] |

## Test Commands

[Provide commands to run tests for this component]

```bash
# Unit tests
pytest tests/unit/test_[component].py -v

# Integration tests (if applicable)
pytest tests/integration/test_[component].py -v

# With coverage
pytest tests/ -k [component] -v --cov=agent_runner_v2.[component]
```

## Known Test Gaps

[Identify areas not well covered by tests]

- [Gap 1: e.g., "Error handling paths not fully tested"]
- [Gap 2: e.g., "Concurrent execution scenarios not covered"]
- [Gap 3: e.g., "Edge cases in parameter validation need more coverage"]

# Change Log

## Recent Changes

[Document significant changes to this component]

| Date | Change ID | Description | Author | Breaking? | Modules Affected |
|------|-----------|-------------|--------|-----------|------------------|
| [YYYY-MM-DD] | [Change ID] | [Brief description] | [Name] | YES/NO | [module1, module2] |
| [YYYY-MM-DD] | [Change ID] | [Brief description] | [Name] | YES/NO | [module1] |

## Migration Notes

[If breaking changes were made, document migration steps]

### Migration from [Old Version] to [New Version]

1. [Step 1: What users need to do]
2. [Step 2: What users need to do]
3. [Step 3: Update imports from old modules to new modules]

# Documentation Governance

## Documentation Status Tracking

| Field | Value |
|-------|-------|
| **Owner** | [Role or name responsible for this documentation] |
| **Last Verified** | [YYYY-MM-DD — when documentation was last verified against code] |
| **Next Review Due** | [YYYY-MM-DD — when documentation should be reviewed next] |
| **Status** | [current/needs_update/pending_review/superseded] |
| **Last Verified By Change** | [Commit hash or change ID that last verified this documentation] |

## Freshness Checks

Use this checklist to keep documentation in sync with code:

- [ ] All constituent modules listed and up-to-date
- [ ] Public API surface reflects current exports
- [ ] Integration points accurately describe dependencies
- [ ] Architecture description matches current implementation
- [ ] Key algorithms documented if complex
- [ ] State management approach accurately described
- [ ] Error handling strategy documented
- [ ] Dependency list reflects current state
- [ ] Test coverage metrics are accurate

**Verification Frequency**: 
- Core components: Every 90 days or on every significant change
- Supporting components: Every 180 days or on every significant change
- Utility components: Every 365 days or on every significant change

**Verification Method**: 
- Compare documentation against current code state
- Verify all constituent modules still exist and are correctly listed
- Review imports across component boundaries to validate integration points
- Run component tests to verify documented behavior

## Stale Guidance Handling

Rules for when documentation becomes stale:

### When to Update

Update documentation immediately when:
- New modules added to component
- Public API changes (new exports or removed exports)
- Integration points change (new dependencies or removed dependencies)
- Architecture evolves significantly
- Implementation details change in ways that affect understanding

### When to Mark needs_update

Mark documentation as `needs_update` when:
- Code has changed but documentation update is deferred
- Known discrepancies exist between code and documentation
- Module list incomplete but component structure still valid

### When to Supersede

Supersede documentation when:
- Component deprecated and replaced by another component
- Component split into multiple components
- Component merged into another component
- Functionality moved to a different location entirely

### Review and Validation Expectations

| Aspect | Requirement |
|--------|-------------|
| **Review Frequency** | [Core: 90 days / Supporting: 180 days / Utility: 365 days] |
| **Review Criteria** | Documentation accuracy, completeness, API surface accuracy, integration point accuracy |
| **Reviewer Role** | [Component owner / Architect / Technical lead] |
| **Approval Requirements** | [Single reviewer approval / Two-person review for core components] |

### Synchronization Requirements

Documentation must be synchronized with code changes:

**When Code Changes**:
- Immediately after adding or removing modules from component
- Before merging pull requests that modify component public API
- Before merging pull requests that change integration points
- As part of documentation sync workflows (`40_documentation_sync_v1`)

**How to Synchronize**:
1. Update constituent module list
2. Update public API surface to reflect current exports
3. Update integration points if dependencies changed
4. Update architecture description if design evolved
5. Update dependency list
6. Set status to `pending_review` until reviewer approves
7. After approval, set status to `current` and update verification metadata

**Automated Support**:
- `scan_repo_codebase` action can identify constituent modules
- Manual curation required for architecture, integration points, and API surface
- Validation workflow checks documentation completeness

# Notes

- [Additional context about component design decisions]
- [Known limitations or constraints]
- [Future improvement opportunities]
- [Link to related discussions or decision logs]
- [Special considerations for Windows compatibility if applicable]
- [Temporary workarounds that need cleanup]
- [Cross-component coordination requirements]
