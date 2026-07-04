---
title: "Module Documentation: agent_runner_v2.doc_paths"
template_id: "CB-02"
status: "active"
module_path: "agent_runner_v2/doc_paths.py"
module_area: "support"
documentation_mode: "summary"
owner_doc_path: "docs/codebase/02_modules/agent-runner-v2-doc-paths.md"
last_verified_by_change: "40_documentation_sync_v1 / 40DOCSYNC-GEN-20260704-001 / 2026-07-04T13:29:07+08:00"
created: "2026-07-04T13:29:07+08:00"
owner: "40_documentation_sync_v1"
---

# Module Documentation: agent_runner_v2.doc_paths

## 1. Module Overview

### 1.1 Purpose

Auto-generated baseline documentation from repository scan.

### 1.2 Responsibility

This module belongs to the `support` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |
| `pathlib` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| | | |

### 2.2 Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `repo_doc_rel` | `()` | public function |
| `docs_root_rel` | `()` | public function |
| `system_doc_rel` | `()` | public function |
| `system_template_rel` | `()` | public function |
| `system_delivery_template_rel` | `()` | public function |
| `system_codebase_template_rel` | `()` | public function |
| `codebase_doc_rel` | `()` | public function |
| `delivery_doc_rel` | `()` | public function |
| `architecture_site_rel` | `()` | public function |
| `master_bootstrap_docs` | `()` | public function |
| `delivery_scaffold_docs` | `()` | public function |
| `codebase_docs` | `()` | public function |
| `architecture_site_pages` | `()` | public function |
| `prompt_literal_aliases` | `()` | Map literal repo-relative paths to prompt placeholders. |

### 2.3 Constants / Configuration

| Name | Value / Type | Purpose |
|------|-------------|---------|
| `SYSTEM_DOC_ROOT` | constant | module configuration |
| `DOCS_ROOT` | constant | module configuration |
| `SYSTEM_TEMPLATE_ROOT` | constant | module configuration |
| `SYSTEM_DELIVERY_TEMPLATE_ROOT` | constant | module configuration |
| `SYSTEM_CODEBASE_TEMPLATE_ROOT` | constant | module configuration |
| `CODEBASE_DOC_ROOT` | constant | module configuration |
| `DELIVERY_DOC_ROOT` | constant | module configuration |
| `ARCHITECTURE_SITE_ROOT` | constant | module configuration |

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
| `tests/test_documentation_governance.py` | `agent_runner_v2.doc_paths` |
| `tests/test_documentation_guardrails_cleanup.py` | `agent_runner_v2.doc_paths` |

### 6.2 Known Gaps

Auto-generated baseline. Review and refine as the codebase evolves.

## 7. Change Log

| Date | Change | Verified By |
|------|--------|-------------|
| 2026-07-04 | Initial baseline generated from repository scan | 40_documentation_sync_v1 |
