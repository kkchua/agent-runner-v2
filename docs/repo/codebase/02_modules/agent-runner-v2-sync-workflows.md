---
title: "Module Documentation: agent_runner_v2.sync_workflows"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/sync_workflows.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/02_modules/agent-runner-v2-sync-workflows.md"
last_verified_by_change: "00_repo_master_docs_bootstrap_v1 / 00RMD-20260716-5ee28fa5 / 2026-07-16T22:09:16+08:00"
created: "2026-07-16T22:09:16+08:00"
owner: "00_repo_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.sync_workflows

## 1. Module Overview

### 1.1 Purpose

Sync workflow definitions to the backend registry.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `argparse` | stdlib module | imported dependency |
| `hashlib` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `urllib` | stdlib module | imported dependency |
| `config_loader` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |
| `workflow_bundle_validator` | external module | repository dependency |
| `workflow_packages.loader` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

No public classes.


### 2.2 Functions

#### main()

**Signature**: `main()`

**Returns**: `int`

---


### 2.3 Constants / Configuration

| Name | Purpose |
|------|--------|
| `_WORKFLOWS_DIR` | module configuration |


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
| 2026-07-16 | Initial baseline generated from repository scan | 00_repo_master_docs_bootstrap_v1 |
