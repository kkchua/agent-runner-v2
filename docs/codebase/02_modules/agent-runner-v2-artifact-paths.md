---
title: "Module Documentation: agent_runner_v2.artifact_paths"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/artifact_paths.py"
module_area: "schema"
documentation_mode: "summary"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-artifact-paths.md"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260704-002 / 2026-07-04T10:47:08+08:00"
created: "2026-07-04T10:47:08+08:00"
owner: "00_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.artifact_paths

## 1. Module Overview

### 1.1 Purpose

artifact_paths.py — Single source of truth for all step artifact paths.

### 1.2 Responsibility

This module belongs to the `schema` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `hashlib` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `logging` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| | | |

### 2.2 Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `compute_paths` | `()` | Return (artifact_path, meta_json_path) — single source of truth. |
| `meta_json_path_for_artifact` | `(artifact_path)` | Return the meta.json path for any artifact path. |
| `load_meta_json` | `(artifact_path)` | Load coder-written meta.json. Returns None if missing. |
| `read_coder_result` | `(artifact_path)` | Read coder_result from meta.json. Returns None if missing or invalid. |

### 2.3 Constants / Configuration

| Name | Value / Type | Purpose |
|------|-------------|---------|
| | | |

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
| | |

### 6.2 Known Gaps

Auto-generated baseline. Review and refine as the codebase evolves.

## 7. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-04 | Initial baseline generated from repository scan | 00_master_docs_bootstrap_v1 |
