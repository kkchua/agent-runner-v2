---
title: "Module Documentation: agent_runner_v2.workflow_packages.base"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/workflow_packages/base.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-workflow-packages-base.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-roo6dyno / 2026-08-05T23:43:32+08:00"
created: "2026-08-05T23:43:32+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.workflow_packages.base

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

#### GovernanceExtension

**Decorators**: `@dataclass`

**Purpose**: Optional bundle governance extension content.

#### GovernanceArtifact

**Decorators**: `@dataclass`

**Purpose**: Artifact registry entry owned or referenced by bundle governance.

#### BundleGovernance

**Decorators**: `@dataclass`

**Purpose**: Canonical governance contract carried with a workflow bundle.

#### StepConfig

**Decorators**: `@dataclass`

**Purpose**: Canonical, validated step configuration from a workflow.toml manifest.

#### WorkflowBundle

**Decorators**: `@dataclass`

**Purpose**: A fully loaded, validated workflow package ready for execution.

**Methods**:

- `get_step(name: str)` -> `StepConfig` -- Look up a step by name. Raises KeyError if missing.
- `next_step(current: str)` -> `str | None` -- Return the next step in the ordered list, or None.


### 2.2 Functions

No public functions.


### 2.3 Constants / Configuration

No public constants.


## 3. Error Handling

No documented exceptions.


## 4. Testing

### 4.1 Test Coverage

| Test File | Coverage Area |
|-----------|---------------|
| `tests/run_workflow_unit_tests.py` | `agent_runner_v2.workflow_packages.base` |


## 5. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-08-05 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
