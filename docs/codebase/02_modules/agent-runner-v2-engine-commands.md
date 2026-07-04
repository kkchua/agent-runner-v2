---
title: "Module Documentation: agent_runner_v2.engine_commands"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/engine_commands.py"
module_area: "commands"
documentation_mode: "summary"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-engine-commands.md"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260704-002 / 2026-07-04T10:47:08+08:00"
created: "2026-07-04T10:47:08+08:00"
owner: "00_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.engine_commands

## 1. Module Overview

### 1.1 Purpose

Engine version management for agent_runner_v2.

### 1.2 Responsibility

This module belongs to the `commands` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `argparse` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `shutil` | stdlib module | imported dependency |
| `subprocess` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `tarfile` | stdlib module | imported dependency |
| `tempfile` | stdlib module | imported dependency |
| `urllib.request` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| | | |

### 2.2 Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `cmd_snapshot` | `(project_root)` | Snapshot the live package source into repo-local SNAPSHOT version. |
| `cmd_install` | `(tag, github_repo, global_install, from_path, project_root)` | Install engine from a local path or a GitHub tag. |
| `cmd_use` | `(project_root, version, local)` | Set the active engine version in config.json. |
| `cmd_list` | `(project_root)` | List all installed engine versions (global + repo-local). |
| `main` | `(argv)` | public function |

### 2.3 Constants / Configuration

| Name | Value / Type | Purpose |
|------|-------------|---------|
| `DEFAULT_GITHUB_REPO` | constant | module configuration |

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
