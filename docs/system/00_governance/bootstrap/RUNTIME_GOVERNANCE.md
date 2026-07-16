---
template_id: "SYS-00-RG"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-17T06:15:00+08:00"
workflow: "00_layer1_governance_bootstrap_v1"
step: "generate_layer1_governance_docs"
change_id: "00L1-20260716-4841a345"
---

> Managed by workflow: `00_layer1_governance_bootstrap_v1` / step: `generate_layer1_governance_docs`
> This file is workflow-generated and protected from manual edits.

# Runtime Governance

## Purpose

This document defines the steady-state runtime model for the plugin workflow system. It establishes the control-plane expectations, bundle publish/install procedures, registry management, validation gates, and execution mode parity rules.

This governance applies to the runtime infrastructure and does not define repository-specific output paths, repository-local workflow inventories, or fallback loading behavior.

## Runtime Scope Model

The runtime governs three distinct scopes:

| Scope | Description |
|-------|-------------|
| Global runtime home | Canonical location for published bundles and runtime configuration |
| Bundle registry | Control-plane index of available bundles and their metadata |
| Execution context | Per-job runtime environment with resolved bundles and configurations |

The runtime does not govern repository-local outputs, repository-specific documentation, or workflow-specific artifact generation. Those responsibilities belong to plugin workflow bundles.

## Bundle Publish And Install Model

### Canonical Runtime Source

The global published bundle copy under the global runtime home is the canonical runtime source. All bundle references resolve against this canonical copy.

| Component | Location |
|-----------|----------|
| Global runtime home | User-level runner home directory |
| Published bundles | Bundles subdirectory under global runtime home |
| Core bundle set | Core bundle collection packaged with runtime distribution |
| Plugin bundles | Plugin workflow bundles published to global registry |

### Publish Operation

Bundle publishing copies a validated bundle from development location to the global published bundle copy:

1. Validate bundle manifest completeness
2. Verify bundle structure compliance
3. Copy bundle to global published bundle location
4. Update bundle registry with new version metadata
5. Mark previous version as superseded (if applicable)

Published bundles become immediately available to all execution contexts.

### Install Operation

Bundle installation prepares a bundle for execution:

1. Resolve bundle from global published bundle copy
2. Load bundle manifest and validate schema
3. Register bundle artifacts and step definitions
4. Prepare execution context with bundle configuration

Installation does not copy bundles to repository locations. All references resolve from the global published copy.

## Registry Control Plane

### Bundle Registry

The bundle registry is the control-plane index for all available bundles:

| Registry Function | Description |
|-------------------|-------------|
| Bundle discovery | List available bundles and versions |
| Metadata storage | Store bundle manifests, dependencies, and version history |
| Dependency resolution | Resolve bundle dependencies and version constraints |
| Supersession tracking | Track which versions supersede others |

The registry does not store bundle content. It stores metadata and references to the global published bundle copy.

### Version Management

The registry tracks bundle versions:

| State | Description |
|-------|-------------|
| Active | Current recommended version for execution |
| Superseded | Replaced by newer version, available for legacy execution |
| Deprecated | Scheduled for removal, execution discouraged |
| Retired | Removed from registry, no longer available |

Version transitions require explicit administrator action through registry control commands.

## Plugin Bundle Control Model

### Bundle Types

Plugin workflow bundles may be either:

| Type | Description |
|------|-------------|
| Single-workflow bundles | Contain one workflow with its complete step set, prompts, and artifact contracts |
| Multi-workflow bundles | Contain multiple related workflows sharing templates, context extensions, and common logic |

Both bundle types follow the same publish/install model and registry management. The distinction affects only internal bundle organization and artifact ownership.

### Workflow Bundle Ownership

Plugin workflow bundles own their workflow-specific artifact path contracts:

| Bundle Responsibility | Description |
|----------------------|-------------|
| Output paths | Define canonical locations for generated documents |
| Review paths | Define paths for review and validation artifacts |
| Artifact inventory | Declare all artifacts the workflow may produce |
| Protection declarations | Identify which documents are workflow-generated and protected |

Shared runtime code provides generic path helpers and enforcement infrastructure but must not own workflow-specific document output paths.

### Steady-State Ownership Model

The steady-state ownership model follows these rules:

1. **Workflow bundles own workflow-specific paths**: Each bundle declares its artifact paths in its manifest
2. **No workflow-name-specific resolution branches**: Shared runtime code must not contain workflow-name-specific path resolution logic
3. **No centralized workflow-family registries**: Path contracts live in bundle manifests, not in shared registries
4. **Generic helpers only**: Shared runtime provides generic path construction, not workflow-specific path lookup

Centralized workflow-family path registries and workflow-name-specific resolution branches are transitional artifacts and must not be described as the steady-state ownership model.

## Role And Connection Resolution

### Coder Role Resolution

The runtime resolves coder roles from bundle manifests:

| Resolution Step | Description |
|-----------------|-------------|
| Role declaration | Bundle declares coder roles required for workflow steps |
| Role mapping | Runtime maps role identifiers to concrete coder backends |
| Credential resolution | Runtime resolves authentication credentials for each role |
| Connection establishment | Runtime establishes connections to coder services |

Role resolution occurs at execution start, not at bundle publish time.

### Connection Management

The runtime manages connections to external services:

| Connection Type | Lifecycle |
|-----------------|-----------|
| Coder service connections | Established per-execution, closed after completion |
| Registry connections | Persistent for control-plane operations |
| Notification connections | Established per-notification, closed after delivery |

Connections are scoped to execution contexts and do not persist across executions.

## Artifact Ownership Enforcement

### Ownership Declaration

Artifacts declare ownership through frontmatter and protection banners:

| Declaration | Location |
|--------------|----------|
| managed_by | YAML frontmatter field indicating workflow-generated status |
| workflow | YAML frontmatter field identifying owning workflow |
| Protection banner | Markdown block immediately after frontmatter |

The runtime enforces ownership by rejecting modifications to workflow-generated documents from unauthorized sources.

### Write Path Validation

The runtime validates write operations against declared artifact paths:

| Validation | Description |
|------------|-------------|
| Path ownership | Verify write target belongs to executing bundle |
| Protection check | Reject writes to workflow-generated documents |
| Scope verification | Enforce bundle scope boundaries |

Validation failures block step completion and require remediation.

## Execution Mode Parity

### Mode Definitions

The runtime supports multiple execution modes with identical behavior:

| Mode | Description |
|------|-------------|
| Manual | Interactive execution through command-line interface |
| Daemon | Automated execution through background service |
| Backend | Remote execution through API-driven backend service |

All modes produce identical outputs for identical inputs. Mode differences affect only execution triggering and status reporting.

### Parity Requirements

Execution modes must maintain strict parity:

1. **Identical step execution**: All modes execute the same workflow steps in the same order
2. **Identical artifact production**: All modes produce the same artifacts with the same content
3. **Identical notification behavior**: All modes send the same notifications at the same points
4. **Identical error handling**: All modes handle errors consistently and produce equivalent failure artifacts

Parity deviations indicate bugs requiring immediate remediation.

## Validation Gates

### Bundle Validation

Bundles undergo validation before publish:

| Gate | Description |
|------|-------------|
| Manifest schema | Verify manifest follows declared schema |
| Prompt completeness | Verify all step prompts exist and are readable |
| Artifact declaration | Verify all declared artifacts have defined paths |
| Dependency resolution | Verify all dependencies resolve to available bundles |

Bundle validation failures block publish. Remediation requires correcting bundle structure or manifest.

### Execution Validation

Workflow execution undergoes validation at each step:

| Gate | Description |
|------|-------------|
| Input artifact presence | Verify all required input artifacts exist |
| Step authorization | Verify executing bundle owns target artifacts |
| Output path validity | Verify output paths fall within bundle ownership |
| Document protection | Verify writes do not target protected documents |

Execution validation failures block step completion. Remediation requires correcting step configuration or artifact ownership.

### Governance Validation

Layer 1 governance undergoes validation during bootstrap:

| Gate | Description |
|------|-------------|
| Frontmatter completeness | Verify all required frontmatter fields present |
| Section presence | Verify all required sections present |
| ASCII compliance | Verify body text contains only ASCII characters |
| Scope purity | Verify no repository-specific content present |
| Ownership correctness | Verify documents match declared ownership |

Governance validation failures block bootstrap completion. Remediation requires correcting governance document content.

## Change Control

### Bundle Version Changes

Bundle version changes follow semantic versioning:

| Change Type | Version Impact |
|-------------|----------------|
| Breaking changes | Major version increment |
| New features | Minor version increment |
| Bug fixes | Patch version increment |

Breaking changes require coordination with dependent bundles and repositories.

### Governance Changes

Layer 1 governance changes require governance bootstrap workflow execution:

1. Modify governance source files in workflow bundle
2. Execute governance bootstrap workflow
3. Validate generated governance documents
4. Approve and commit updated documents

Manual edits to Layer 1 documents are prohibited. All changes flow through the governance bootstrap workflow.

### Registry Changes

Registry changes require administrative action:

| Change | Authorization |
|--------|---------------|
| Bundle activation | Administrator approval |
| Bundle deprecation | Administrator approval |
| Bundle retirement | Administrator approval after deprecation period |
| Version supersession | Automatic on new version publish |

Registry changes are logged and auditable. Unauthorized registry modifications are rejected.