---
title: "Module Documentation: agent_runner_v2.exceptions"
template_id: "CB-02"
version: "1.0.0"
doc_type: "system"
authority: "workflow-generated"
scan_policy: "include"
lifecycle_status: "approved"
module_path: "agent_runner_v2/exceptions.py"
module_area: "schema"
documentation_mode: "summary"
owner_doc_path: "docs/repo/codebase/current/02_modules/agent-runner-v2-exceptions.md"
last_verified_by_change: "sdlc_00_codebase_v1 / SDLC00CB-20260723-d46af7f2 / 2026-07-23T20:54:20+08:00"
created: "2026-07-23T20:54:20+08:00"
owner: "sdlc_00_codebase_v1"
---

# Module Documentation: agent_runner_v2.exceptions

## 1. Module Overview

### 1.1 Purpose

exceptions.py -- Custom exceptions for agent_runner_v2.

### 1.2 Responsibility

This module belongs to the `schema` area and is documented as `summary`.

### 1.3 Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `__future__` | stdlib module | imported dependency |

## 2. Public API

### 2.1 Classes

#### PreflightBlockedError

**Inherits from**: `Exception`

**Purpose**: Raised when a preflight check blocks step execution (e.g. artifact status not approved).

#### MetaJsonMissingError

**Inherits from**: `Exception`

**Purpose**: Raised when the coder did not write the expected meta.json sidecar after invocation.

#### MetaJsonInvalidError

**Inherits from**: `Exception`

**Purpose**: Raised when meta.json exists but fails schema validation.

#### ArtifactMissingError

**Inherits from**: `Exception`

**Purpose**: Raised when coder_result.artifacts references paths that don't exist on disk.


### 2.2 Functions

No public functions.


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
| 2026-07-23 | Initial baseline generated from repository scan | sdlc_00_codebase_v1 |
