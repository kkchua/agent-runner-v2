---
title: "Module Documentation: agent_runner_v2.step_runner"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/step_runner.py"
module_area: "core"
documentation_mode: "full"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-step-runner.md"
last_verified_by_change: "00_master_docs_bootstrap_v1 / 00DOC-GEN-20260702-005 / 2026-07-02T18:00:53+08:00"
created: "2026-07-02T18:00:53+08:00"
owner: "00_master_docs_bootstrap_v1"
---

# Module Documentation: agent_runner_v2.step_runner

## 1. Module Overview

### 1.1 Purpose

step_runner.py — Core step execution contract for agent_runner_v2.

### 1.2 Responsibility

This module belongs to the `core` area and is documented as `full`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `dataclasses` | stdlib module | imported dependency |
| `datetime` | stdlib module | imported dependency |
| `hashlib` | stdlib module | imported dependency |
| `json` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |
| `re` | stdlib module | imported dependency |
| `shutil` | stdlib module | imported dependency |
| `tempfile` | stdlib module | imported dependency |
| `typing` | stdlib module | imported dependency |
| `artifact_paths` | external module | repository dependency |
| `coder_adapters` | external module | repository dependency |
| `documentation_guardrails` | external module | repository dependency |
| `exceptions` | external module | repository dependency |
| `runtime_context` | external module | repository dependency |

## 2. Public API

### 2.1 Classes

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| `StepResult` | public class | |

### 2.2 Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `run_step` | `()` | Invoke coder, read meta.json contract, validate artifacts, enrich sidecar. |
| `run_action` | `()` | Execute a runner action (non-coder step). |
| `enrich_sidecar` | `()` | Atomically append runner_data section to existing meta.json. |
| `build_context` | `(state)` | Build the full context dict for prompt rendering. |
| `render_prompt` | `(template_text, context)` | public function |
| `prompt_checksum` | `(prompt_text)` | public function |
| `resolve_prompt_path` | `()` | Resolve prompt file path with three-level fallback. |

### 2.3 Constants / Configuration

| Name | Value / Type | Purpose |
|------|-------------|---------|
| `RESULT_SCHEMA_PATH` | constant | module configuration |
| `_TOOL_INSTRUCTION_TEMPLATE` | constant | module configuration |

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
| `tests/test_backend_worker_mode.py` | `agent_runner_v2.step_runner` |
| `tests/test_documentation_governance.py` | `agent_runner_v2.step_runner` |
| `tests/test_tool_instruction_block.py` | `agent_runner_v2.step_runner` |

### 6.2 Known Gaps

Auto-generated baseline. Review and refine as the codebase evolves.

## 7. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-02 | Initial baseline generated from repository scan | 00_master_docs_bootstrap_v1 |
