---
title: "Module Documentation: agent_runner_v2.runtime_context"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/runtime_context.py"
module_area: "state"
documentation_mode: "full"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-runtime-context.md"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260704-001 / 2026-07-04T06:01:39+08:00"
created: "2026-07-04T06:01:39+08:00"
owner: "00_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.runtime_context

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `state` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `tempfile` | stdlib module | imported dependency |
| `types` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| `RuntimeContext` | public class | |
| `PathProxy` | Lightweight Path-like proxy that resolves lazily from current context. | |

### 2.2 Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `set_context` | `()` | Set process-local runtime context and return it. |
| `get_context` | `()` | public function |
| `get_workspace_root` | `()` | public function |
| `get_runner_home` | `()` | public function |
| `get_jobs_root` | `()` | public function |
| `get_workflow_root` | `()` | public function |
| `get_workflow_module` | `()` | public function |
| `set_workflow_module` | `(module)` | public function |
| `get_delivery_root` | `()` | public function |
| `set_delivery_root` | `(root)` | public function |
| `resolve_artifact_root` | `()` | Return the root for resolving artifact paths. |
| `resolve_repo_or_runtime_path` | `(path_str)` | Resolve a path using the repo/runtime namespace convention. |
| `artifact_rel_to_meta_rel` | `(artifact_rel)` | Return the meta.json sibling path for a repo/runtime-relative artifact. |
| `write_meta_sidecar` | `(meta_path_like)` | Write a v2 meta.json sidecar using the shared path resolver. |
| `resolve_step_meta_rel` | `()` | Resolve the meta.json relative path for a step-owned artifact. |

### 2.3 Constants / Configuration

| Name | Value / Type | Purpose |
|------|-------------|---------|
| `PACKAGE_ROOT` | constant | module configuration |
| `DEFAULT_RUNNER_HOME` | constant | module configuration |
| `GLOBAL_RUNNER_HOME` | constant | module configuration |
| `DEFAULT_WORKFLOW_NAME` | constant | module configuration |
| `_CTX` | constant | module configuration |
| `PROJECT_ROOT` | constant | module configuration |
| `RUNNER_HOME` | constant | module configuration |
| `RUNNER_ROOT` | constant | module configuration |
| `JOBS_ROOT` | constant | module configuration |
| `DELIVERY_ROOT` | constant | module configuration |
| `ARTIFACT_ROOT` | constant | module configuration |

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
| `tests/test_backend_worker_mode.py` | `agent_runner_v2.runtime_context` |
| `tests/test_runtime_context_paths.py` | `agent_runner_v2.runtime_context` |

### 6.2 Known Gaps

Auto-generated baseline. Review and refine as the codebase evolves.

## 7. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-04 | Initial baseline generated from repository scan | 00_master_docs_bootstrap_v1 |
