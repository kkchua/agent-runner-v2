---
title: "Module Documentation: agent_runner_v2.bundle_loader"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/bundle_loader.py"
module_area: "bootstrap"
documentation_mode: "full"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-bundle-loader.md"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260704-002 / 2026-07-04T10:47:08+08:00"
created: "2026-07-04T10:47:08+08:00"
owner: "00_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.bundle_loader

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `bootstrap` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `importlib.util` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `shutil` | stdlib module | imported dependency |
| `types` | stdlib module | imported dependency |
| `bundle_taxonomy` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| | | |

### 2.2 Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `bundles_root` | `()` | public function |
| `core_bundles_root` | `()` | public function |
| `domain_bundles_root` | `()` | public function |
| `workflow_bundles_root` | `()` | public function |
| `config_path` | `(workspace_root)` | public function |
| `workflows_root` | `(workspace_root)` | public function |
| `workflow_root` | `(workspace_root, workflow_name)` | public function |
| `global_workflows_root` | `()` | public function |
| `global_workflow_root` | `(workflow_name)` | public function |
| `resolve_workflow_root` | `(workspace_root, workflow_name)` | public function |
| `load_project_config` | `(workspace_root)` | public function |
| `save_project_config` | `(workspace_root, config)` | public function |
| `load_workflow_module` | `(workspace_root, workflow_name)` | public function |
| `seed_workflow_bundle` | `(target_root, workflow_name)` | Copy the bootstrap workflow template set into the target global workflow location. |
| `init_workspace` | `(workspace_root, workflow_name)` | public function |

### 2.3 Constants / Configuration

| Name | Value / Type | Purpose |
|------|-------------|---------|
| `GLOBAL_RUNNER_HOME` | constant | module configuration |
| `BOOTSTRAP_ROOT` | constant | module configuration |

## 3. Internal Implementation

### 3.1 Key Data Structures

Auto-generated baseline documentation derived from the current source tree.

### 3.2 Algorithm / Flow

See the source module for implementation details; this document captures the public contract and scan-derived summary.

## 4. I/O Contract

### 4.1 Inputs

Derived from function parameters, imports, and file-level responsibilities.

### 4.2 Outputs

Derived from function return values and side effects observed in the source file.

### 4.3 Side Effects

Tracked at a baseline level by the repository scan.

## 5. Error Handling

| Error Condition | Handling | Recovery |
|----------------|----------|----------|
| | | |

## 6. Testing

### 6.1 Test Coverage

| Test File | Coverage Area |
|-----------|--------------|
| `tests/test_bundle_loader.py` | `agent_runner_v2.bundle_loader` |
| `tests/test_tool_instruction_block.py` | `agent_runner_v2.bundle_loader` |

### 6.2 Known Gaps

Auto-generated baseline. Review and refine as the codebase evolves.

## 7. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-04 | Initial baseline generated from repository scan | 00_master_docs_bootstrap_v1 |
