---
title: "Module Documentation: agent_runner_v2.tools.agent_tools"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/tools/agent_tools.py"
module_area: "tools"
documentation_mode: "summary"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-tools-agent-tools.md"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260704-001 / 2026-07-04T06:01:39+08:00"
created: "2026-07-04T06:01:39+08:00"
owner: "00_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.tools.agent_tools

## 1. Module Overview

### 1.1 Purpose

agent_tools.py — Task coder tool functions for agent-runner steps.

### 1.2 Responsibility

This module belongs to the `tools` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `datetime` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `os` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `sys` | stdlib module | imported dependency |
| `urllib.request` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| | | |

### 2.2 Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `create_todos` | `(step_id, todos)` | Register all todo items for this step. All start as pending. |
| `mark_complete` | `(step_id, todo_index, notes)` | Mark the todo at 1-based index as completed, resolving the original item description. |

### 2.3 Constants / Configuration

| Name | Value / Type | Purpose |
|------|-------------|---------|
| `PROGRESS_FILE` | constant | module configuration |
| `BACKEND_URL` | constant | module configuration |
| `STEP_RUN_ID` | constant | module configuration |

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
