---
template_id: "CODEBASE-MOD-v1"
title: "Codebase Module Template"
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

- **Template ID**: CODEBASE-MOD-v1
- **Artifact Key**: `CODEBASE_MODULE_TEMPLATE`
- **Version**: 1.0
- **Owner**: Codebase Documentation Workflow
- **Purpose**: Documents individual Python modules with module overview, file inventory, architecture, key components, public API, dependencies, testing, change log, documentation governance, and notes

# Module Overview

**Module Name**: `[module_name]`

**File Path**: `agent_runner_v2/[path/to/module].py`

**Documentation Path**: `docs/codebase/02_modules/[module_name].md`

**Module Type**: [core/utility/action/workflow_support/test_support/config/data]

**Summary**: [2-3 sentence description of what this module does and why it exists]

**Key Responsibilities**:
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

**Complexity**: [LOW/MEDIUM/HIGH]

**Lines of Code**: [Approximate line count]

**Test Coverage**: [XX% or N/A]

# File Inventory

## Source Files

[List all files associated with this module]

| File | Purpose | Lines | Last Modified |
|------|---------|-------|---------------|
| `[module_name].py` | Main module implementation | [N] | [Date] |
| `test_[module_name].py` | Unit tests | [N] | [Date] |
| `[related_file].py` | Supporting code | [N] | [Date] |

## Related Documentation

[List documentation files related to this module]

| Document | Path | Purpose | Status |
|----------|------|---------|--------|
| Module Doc | `docs/codebase/02_modules/[module_name].md` | Module documentation | current |
| Change Impact | `docs/codebase/04_changes/CHANGE-IMPACT-[NNN].md` | Change tracking | current |

# Architecture

## Module Position

[Describe where this module fits in the overall architecture]

**Depends On**: [List modules this module depends on]

**Depended By**: [List modules that depend on this module]

**Architectural Layer**: [CLI Layer / Execution Core / Coder Integration / Action Layer / Bootstrap Layer / Support Components]

## Design Patterns

[Identify design patterns used in this module]

| Pattern | Usage | Rationale |
|---------|-------|-----------|
| [Pattern name] | [Where/how used] | [Why this pattern was chosen] |

## Key Abstractions

[Describe key abstractions this module introduces]

- [Abstraction 1: e.g., "StepResult dataclass encapsulates step execution outcomes"]
- [Abstraction 2: e.g., "ArtifactPath constants provide centralized path resolution"]

# Key Components

## Public Classes

[Document public classes exposed by this module]

### Class: `[ClassName]`

**Purpose**: [What this class does]

**Key Attributes**:
- `attribute_name`: [Type] — [Description]

**Key Methods**:
- `method_name(args)`: [Brief description of what method does]

**Usage Example**:
```python
from agent_runner_v2.module_name import ClassName

instance = ClassName(arg1, arg2)
result = instance.method_name()
```

## Public Functions

[Document public functions exposed by this module]

### Function: `function_name(args)`

**Purpose**: [What this function does]

**Parameters**:
- `param1` ([type]): [Description]
- `param2` ([type]): [Description]

**Returns**: [Return type and description]

**Raises**: [Exceptions that may be raised]

**Usage Example**:
```python
from agent_runner_v2.module_name import function_name

result = function_name(arg1, arg2)
```

## Internal Helpers

[Briefly describe key internal helper functions if they are complex or non-obvious]

- `_helper_name()`: [Brief description — only include if complexity warrants documentation]

# Public API

## Exported Symbols

[List all symbols this module exports for use by other modules]

```python
__all__ = [
    "ClassName",
    "function_name",
    "CONSTANT_NAME",
]
```

## Import Patterns

[Show how other modules should import from this module]

```python
# Standard import
from agent_runner_v2.module_name import ClassName

# For utility functions
from agent_runner_v2.module_name import helper_function
```

## API Stability

[Indicate API stability level]

**Stability**: [stable/experimental/deprecated]

**Breaking Change Policy**: [Describe policy for making breaking changes, e.g., "Deprecate for one release before removal"]

# Dependencies

## Internal Dependencies

[List dependencies on other modules within agent_runner_v2]

| Dependency | Import | Purpose | Coupling Level |
|------------|--------|---------|----------------|
| `constants` | `from agent_runner_v2 import constants` | Path constants | LOW |
| `bundle_loader` | `from agent_runner_v2.bundle_loader import ...` | Bundle loading | MEDIUM |

## External Dependencies

[List external library dependencies]

| Library | Version | Purpose | Optional |
|---------|---------|---------|----------|
| [Library name] | [Version] | [What it's used for] | YES/NO |

## Runtime Dependencies

[List runtime requirements not captured by imports]

- [Requirement 1: e.g., "Requires .env file for Pushover credentials"]
- [Requirement 2: e.g., "Requires git CLI available in PATH"]

# Testing

## Test Files

[List test files covering this module]

| Test File | Type | Coverage | Location |
|-----------|------|----------|----------|
| `test_[module].py` | unit/integration | [XX%] | `tests/unit/` or `tests/integration/` |

## Test Strategy

[Describe how this module is tested]

**Unit Tests**: [What aspects are covered by unit tests]

**Integration Tests**: [What aspects require integration testing]

**Manual Testing**: [What aspects require manual verification]

## Test Commands

[Provide commands to run tests for this module]

```bash
# Unit tests
pytest tests/unit/test_[module].py -v

# Integration tests (if applicable)
pytest tests/integration/test_[module].py -v

# With coverage
pytest tests/unit/test_[module].py -v --cov=agent_runner_v2.[module]
```

## Known Test Gaps

[Identify areas not well covered by tests]

- [Gap 1: e.g., "Error handling paths not fully tested"]
- [Gap 2: e.g., "Edge cases in parameter validation need more coverage"]

# Change Log

## Recent Changes

[Document significant changes to this module]

| Date | Change ID | Description | Author | Breaking? |
|------|-----------|-------------|--------|-----------|
| [YYYY-MM-DD] | [Change ID] | [Brief description] | [Name] | YES/NO |
| [YYYY-MM-DD] | [Change ID] | [Brief description] | [Name] | YES/NO |

## Migration Notes

[If breaking changes were made, document migration steps]

### Migration from [Old Version] to [New Version]

1. [Step 1: What users need to do]
2. [Step 2: What users need to do]

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

- [ ] All public classes documented with current signatures
- [ ] All public functions documented with current parameters and return types
- [ ] Code examples in documentation match actual implementation
- [ ] Dependency list reflects current imports
- [ ] Test coverage percentage is accurate
- [ ] Architectural layer assignment is still correct
- [ ] Design patterns identified are still accurate

**Verification Frequency**: 
- Core modules: Every 90 days or on every significant change
- Supporting modules: Every 180 days or on every significant change
- Utility modules: Every 365 days or on every significant change

**Verification Method**: 
- Compare documentation against current code state
- Run module tests to verify examples work
- Review imports to validate dependency list

## Stale Guidance Handling

Rules for when documentation becomes stale:

### When to Update

Update documentation immediately when:
- Public API changes (new classes, functions, or signature changes)
- Implementation logic changes significantly
- Dependencies are added or removed
- Design patterns evolve

### When to Mark needs_update

Mark documentation as `needs_update` when:
- Code has changed but documentation update is deferred
- Known discrepancies exist between code and documentation
- Examples no longer work but documentation structure is still valid

### When to Supersede

Supersede documentation when:
- Module is deprecated and replaced by another module
- Documentation consolidated into a different document
- Functionality moved to a different location entirely

### Review and Validation Expectations

| Aspect | Requirement |
|--------|-------------|
| **Review Frequency** | [Core: 90 days / Supporting: 180 days / Utility: 365 days] |
| **Review Criteria** | Documentation accuracy, completeness, clarity, example validity |
| **Reviewer Role** | [Module owner / Designated reviewer / Technical lead] |
| **Approval Requirements** | [Single reviewer approval / Two-person review for core modules] |

### Synchronization Requirements

Documentation must be synchronized with code changes:

**When Code Changes**:
- Immediately after any public API modification
- Before merging pull requests that modify module behavior
- As part of documentation sync workflows (`40_documentation_sync_v1`)

**How to Synchronize**:
1. Update module documentation to reflect new API
2. Verify all examples still work
3. Update dependency list if imports changed
4. Update change log entry
5. Set status to `pending_review` until reviewer approves
6. After approval, set status to `current` and update verification metadata

**Automated Support**:
- `scan_repo_codebase` action can regenerate module documentation skeleton
- Manual curation required for architecture, design patterns, and usage examples
- Validation workflow checks documentation completeness

# Notes

- [Additional context about module design decisions]
- [Known limitations or constraints]
- [Future improvement opportunities]
- [Link to related discussions or decision logs]
- [Special considerations for Windows compatibility if applicable]
- [Temporary workarounds that need cleanup]
