---
title: "Module Documentation: agent_runner_v2.workflow_package_validator"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/workflow_package_validator.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-package-validator.md"
last_verified_by_change: "sdlc_00_codebase_scaffold_v1 / SDLC00CS-1zcrrbbs / 2026-08-17T21:19:17+08:00"
created: "2026-08-17T21:19:17+08:00"
owner: "sdlc_00_codebase_scaffold_v1"
---

# Module Documentation: agent_runner_v2.workflow_package_validator

## 1. Module Overview

### 1.1 Purpose

Deterministic workflow package validator.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `ast` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

#### ValidationFinding

**Decorators**: `@dataclass`

**Purpose**: A single validation finding.

**Methods**:

- `to_dict()` -> `dict[str, str]` -- method

#### ValidationResult

**Decorators**: `@dataclass`

**Purpose**: Aggregate result of a package validation run.

**Methods**:

- `errors()` -> `list[ValidationFinding]` -- method
- `warnings()` -> `list[ValidationFinding]` -- method
- `passed()` -> `bool` -- method
- `summary()` -> `str` -- method


### 2.2 Functions

#### validate_package()

**Signature**: `validate_package(*, manifest_path: Path, extensions_path: Path | None = None, actions_path: Path | None = None)`

**Purpose**: Run all static checks on a workflow package.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `manifest_path` | `Path` | -- | Path to workflow.toml (required). |
| `extensions_path` | `Path | None` | `None` | Path to context_extensions.py (optional). |
| `actions_path` | `Path | None` | `None` | Path to actions.py (optional). |

**Returns**: `ValidationResult`

---

#### render_report()

**Signature**: `render_report(result: ValidationResult, job_id: str = '')`

**Purpose**: Render validation result as Markdown report.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `result` | `ValidationResult` | -- | -- |
| `job_id` | `str` | `''` | -- |

**Returns**: `str`

---


### 2.3 Constants / Configuration

No public constants.


## 3. Error Handling

No documented exceptions.


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| (none) | No test references found |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-08-17 | Initial baseline generated from repository scan | sdlc_00_codebase_scaffold_v1 |
