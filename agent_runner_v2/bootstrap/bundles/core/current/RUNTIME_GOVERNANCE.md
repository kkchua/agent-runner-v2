---
template_id: "SYS-00-RG"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-16T10:05:56+08:00"
workflow: "00_layer1_governance_bootstrap_v1"
step: "generate_layer1_governance_docs"
change_id: "00L1-20260716-e4c16ad4"
---

> Managed by workflow: `00_layer1_governance_bootstrap_v1` / step: `generate_layer1_governance_docs`
> This file is workflow-generated and protected from manual edits.

# Runtime Governance

## Purpose

This document defines the steady-state runtime operating model for the plugin
workflow ecosystem. It establishes the rules for bundle publishing, installation,
registry control, validation gates, and execution mode parity.

## Runtime Scope Model

The runtime scope model defines how bundles are organized and accessed:

### Global Runtime Home

The global runtime home is the canonical location for published workflow
bundles. It serves as the single source of truth for workflow definitions
at runtime.

**Location**: The global runtime home is located at a well-known path in the
user environment and contains all published workflow bundles.

**Contents**:

- Published workflow bundles (core governance, plugin workflow, domain)
- Registry files (roles, connections, policies)
- Bundle manifests and version information

### Bundle Isolation

Each workflow bundle is isolated from other bundles:

- Bundles do not share mutable state
- Bundles communicate through well-defined interfaces
- Bundle updates do not affect other bundles

## Bundle Publish And Install Model

### Publishing

Bundle publishing follows these rules:

1. **Source**: Bundles are authored in repository workflow directories
2. **Validation**: Bundles must pass validation before publishing
3. **Publish Target**: Validated bundles are published to the global runtime home
4. **Version Recording**: Published bundles record version information in manifests

### Installation

Bundle installation follows these rules:

1. **Init Command**: The init command seeds the global runtime home with core bundles
2. **Sync Command**: The sync command updates bundles from repository sources
3. **Verification**: Installation verifies bundle integrity and version compatibility
4. **Registration**: Installed bundles are registered with the runtime registry

### Bundle Types at Runtime

Plugin workflow bundles may be either:

- **Single-workflow bundles**: Contain exactly one workflow definition with its
  prompts, actions, and context extensions
- **Multi-workflow bundles**: Contain multiple related workflow definitions that
  share common resources

Both bundle types follow the same publish and install model.

## Registry Control Plane

### Registry Purpose

The registry control plane provides:

- Workflow bundle discovery
- Role and connection resolution
- Policy enforcement
- Execution coordination

### Registry Components

| Component | Purpose |
|-----------|---------|
| Workflow Registry | Discover and load workflow bundles |
| Role Registry | Resolve roles for workflow execution |
| Connection Registry | Resolve connections for workflow execution |
| Policy Registry | Enforce execution policies |

### Registry Access

The registry is accessed through well-defined interfaces:

- Bundle discovery queries
- Role resolution queries
- Connection resolution queries
- Policy evaluation queries

## Plugin Bundle Control Model

### Bundle Lifecycle

Plugin workflow bundles follow a defined lifecycle:

1. **Authoring**: Bundle is created in repository workflow directory
2. **Validation**: Bundle is validated against schema and governance rules
3. **Publishing**: Validated bundle is published to global runtime home
4. **Registration**: Published bundle is registered with runtime registry
5. **Execution**: Bundle workflows are executed on demand
6. **Updates**: Bundle can be updated through sync or republish

### Bundle Versioning

Bundle versioning follows these rules:

- Semantic versioning for bundle versions
- Version compatibility checks during installation
- Breaking changes require major version increments

### Bundle Dependencies

Bundle dependencies follow these rules:

- Dependencies must be explicitly declared in manifest
- Circular dependencies are not allowed
- Core governance bundles cannot depend on plugin or domain bundles

## Role And Connection Resolution

### Role Resolution

Role resolution determines which role executes a workflow step:

- Roles are defined in registry files
- Role policies control role assignment
- Workflow manifests can specify required roles

### Connection Resolution

Connection resolution determines how workflows connect to external systems:

- Connections are defined in registry files
- Connection types are declared in workflow manifests
- Credential resolution follows defined precedence rules

### Resolution Precedence

Resolution follows a defined precedence:

1. Workflow manifest declarations
2. Registry file definitions
3. Environment-based defaults
4. User-provided overrides

## Artifact Ownership Enforcement

### Ownership Rules

Artifacts generated by workflows are owned by:

- The workflow that generated the artifact
- The bundle that contains the workflow
- The execution that created the artifact instance

### Ownership Metadata

Artifact ownership is recorded in:

- Artifact metadata files (sidecar files)
- Execution records
- Bundle manifests

### Ownership Queries

Ownership can be queried through:

- Artifact metadata inspection
- Execution record lookup
- Bundle manifest examination

## Execution Mode Parity

### Supported Execution Modes

The runtime supports multiple execution modes:

| Mode | Description |
|------|-------------|
| Manual | Direct execution via CLI |
| Daemon | Background execution via daemon process |
| Worker | Distributed execution via worker processes |

### Parity Requirements

All execution modes must follow:

- Same workflow loading logic
- Same validation gates
- Same artifact ownership rules
- Same notification behavior

### Mode-Specific Behavior

Mode-specific behavior is limited to:

- Execution triggering (manual vs. daemon vs. worker)
- Progress reporting (blocking vs. background)
- Resource management (foreground vs. background)

The core workflow execution logic must be identical across all modes.

## Validation Gates

### Pre-Publish Validation

Before publishing, bundles must pass:

- Schema validation (manifest structure)
- Governance validation (scope purity, ownership)
- Dependency validation (compatibility, circular dependencies)

### Pre-Execution Validation

Before execution, workflows must pass:

- Bundle validation (manifest, prompts, actions)
- Role validation (role exists, policy permits)
- Connection validation (connection exists, credentials available)

### Post-Execution Validation

After execution, results must pass:

- Artifact validation (required artifacts exist, ownership recorded)
- Status validation (terminal state is valid)
- Metadata validation (sidecar files are complete)

## Change Control

### Change Categories

Changes are categorized by impact:

| Category | Impact | Approval Required |
|----------|--------|-------------------|
| Patch | Bug fixes, minor improvements | Bundle owner |
| Minor | New features, backward compatible | Bundle owner |
| Major | Breaking changes | System architect |

### Change Process

Changes follow this process:

1. **Propose**: Change is proposed in change request
2. **Validate**: Change is validated against governance rules
3. **Approve**: Change is approved by appropriate authority
4. **Publish**: Changed bundle is published to runtime
5. **Verify**: Published change is verified in runtime

### Rollback

Rollback is supported for:

- Bundle version rollback (restore previous version)
- Configuration rollback (restore previous configuration)
- Registry rollback (restore previous registry state)

Rollback requires appropriate authority approval.