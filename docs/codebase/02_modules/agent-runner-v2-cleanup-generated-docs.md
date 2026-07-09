---
title: "Module Documentation: agent_runner_v2.cleanup_generated_docs"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/cleanup_generated_docs.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-cleanup-generated-docs.md"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260709-002 / 2026-07-09T21:13:38+08:00"
created: "2026-07-09T21:13:38+08:00"
owner: "00_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.cleanup_generated_docs

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `argparse` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `shutil` | stdlib module | imported dependency |
| `documentation_guardrails` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

#### CleanupResult

**Decorators**: `@dataclass`

**Purpose**: Public class


### 2.2 Functions

#### cleanup_workflow_generated_docs()

**Signature**: `cleanup_workflow_generated_docs(*, project_root: Path, template_group: str, job_id: str, mode: str, action: str = 'report', quarantine_root: str = DEFAULT_LEGACY_QUARANTINE_DIR)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `project_root` | `Path` | — | — |
| `template_group` | `str` | — | — |
| `job_id` | `str` | — | — |
| `mode` | `str` | — | — |
| `action` | `str` | `'report'` | — |
| `quarantine_root` | `str` | `DEFAULT_LEGACY_QUARANTINE_DIR` | — |

**Returns**: `CleanupResult`

---

#### main()

**Signature**: `main(argv: list[str] | None = None)`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `argv` | `list[str] | None` | `None` | — |

**Returns**: `int`

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
| 2026-07-09 | Initial baseline generated from repository scan | 00_master_docs_bootstrap_v1 |
