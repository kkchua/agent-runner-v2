---
title: "Module Documentation: agent_runner_v2.submitter"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/submitter.py"
module_area: "commands"
documentation_mode: "summary"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-submitter.md"
last_verified_by_change: "40_documentation_sync_v1 / 40DOCSYNC-GEN-20260704-001 / 2026-07-04T13:29:07+08:00"
created: "2026-07-04T13:29:07+08:00"
owner: "40_documentation_sync_v1"
---

# Module Documentation: agent_runner_v2.submitter

## 1. Module Overview

### 1.1 Purpose

submitter.py — ComfyUI API client for agent-runner-v2.

### 1.2 Responsibility

This module belongs to the `commands` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `time` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `urllib.error` | stdlib module | imported dependency |
| `urllib.request` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| `SubmissionResult` | Result of a single entry submission. | |
| `SubmissionSummary` | Summary of a batch submission. | |

### 2.2 Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `load_config` | `(config_path)` | Load ComfyUI config from JSON file, resolving env var placeholders. |
| `login` | `(base_url, email, password)` | Authenticate and return JWT token. |
| `execute_workflow` | `(base_url, token, workflow_key, entry, test_mode)` | Submit a single entry to the ComfyUI workflow. |
| `submit_files` | `(run_dir)` | Submit all JSON files in run_dir to ComfyUI. |
| `main` | `()` | public function |

### 2.3 Constants / Configuration

| Name | Value / Type | Purpose |
|------|-------------|---------|
| `PACKAGE_ROOT` | constant | module configuration |
| `DEFAULT_CONFIG_PATH` | constant | module configuration |

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
| 2026-07-04 | Initial baseline generated from repository scan | 40_documentation_sync_v1 |
