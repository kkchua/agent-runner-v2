---
template_id: "SYS-00-RG"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-15T23:45:00+08:00"
workflow: "00_layer1_governance_bootstrap_v1"
step: "refine_layer1_governance_docs"
change_id: "00L1-20260715-c2f96104"
---

> Managed by workflow: `00_layer1_governance_bootstrap_v1` / step: `refine_layer1_governance_docs`
> This file is workflow-generated and protected from manual edits.

# Runtime Governance

## Purpose

This document defines the steady-state runtime operating model for plugin workflow bundles. It establishes the registry control plane, plugin bundle control model, role and connection resolution, artifact ownership enforcement, execution mode parity, validation gates, and change control rules that govern how plugin workflows operate at runtime.

## Runtime Scope Model

The runtime scope encompasses all plugin workflow bundles registered in the ecosystem registry. Each bundle operates within its declared scope and produces artifacts according to its manifest. The runtime control plane manages bundle registration, versioning, discovery, and execution — it does not own repository-specific artifacts or repo-local outputs under `docs/repo/`. Those are managed by Layer 2 (repository master-doc structure) or Layer 3 (plugin workflow families).

## Bundle Publish And Install Model

Plugin workflow bundles follow a publish/install lifecycle:

**Publish**
Bundle authors publish their bundle to the ecosystem registry by registering its manifest, which declares the bundle's workflow definitions, artifact production rules, and validation gates.

**Install**  
Repositories install plugin bundles from the registry. Installation copies the bundle's workflow definitions, prompts, and actions into the repository's local workflow directory. Installed bundles conform to the Layer 1 governance contract.

**Sync**  
Changes to bootstrap workflow files must be synced to the global runner home before they take effect in prompts. The sync mechanism ensures runtime bundles reflect the current state of the source repository.

## Registry Control Plane

The registry control plane manages the lifecycle of plugin workflow bundles:

**Registration**  
Bundles register themselves with the ecosystem registry, providing their manifest and metadata.

**Discovery**  
Repositories discover available bundles through the registry, filtering by domain, profile, or workflow name.

**Versioning**  
The registry tracks bundle versions and supports versioned installs. Breaking changes require a new major version and a migration plan.

**Deprecation**  
Deprecated bundles remain available but emit warnings during install. Removal requires a grace period and migration guidance.

## Plugin Bundle Control Model

Plugin workflow bundles may be either single-workflow bundles or multi-workflow bundles:

**Single-Workflow Bundles**  
A single-workflow bundle contains exactly one workflow definition. This pattern is appropriate for focused, atomic operations such as documentation generation, code scanning, or artifact validation.

**Multi-Workflow Bundles**  
A multi-workflow bundle contains multiple related workflows that share context, artifacts, or execution logic. This pattern is appropriate for complex pipelines requiring sequential or conditional workflow steps.

The runtime control plane must support both patterns without requiring separate handling logic. Bundle manifests declare whether a bundle is single-workflow or multi-workflow, and the runtime adapts accordingly.

## Role And Connection Resolution

Plugin bundles resolve roles and connections at runtime:

**Role Resolution**  
Each workflow step declares a role policy (e.g., architect_standard, reviewer_standard). The runtime resolves the role to a concrete coder adapter based on the execution context.

**Connection Resolution**  
Bundles may declare external connections (MCP servers, API endpoints, credential sources). The runtime resolves these connections from the execution environment, supporting both `.env` files and shared credential resolution functions.

## Artifact Ownership Enforcement

Artifact ownership follows the Layer 1 bundle taxonomy:

**Declared Artifacts**
Each workflow step declares which artifacts it produces. The runtime enforces that only declared artifacts are written to disk according to the bundle manifest.

**Protected Artifacts**
Layer 1 governance documents are protected from modification by plugin workflows. Attempting to write to a protected path causes a validation failure.

**Repo-Local Output Boundary**
Outputs under `docs/repo/` are outside Layer 1 ownership. Plugin workflows may produce repo-local outputs if their bundle manifest declares them, but these outputs are owned by Layer 2 or Layer 3, not by the Layer 1 runtime control plane.

## Execution Mode Parity

Plugin workflows must behave identically across execution modes:

**Daemon Mode**  
Long-running daemon process executes workflow steps sequentially, maintaining state between steps.

**Manual Mode**  
Interactive execution where each step runs independently with explicit user approval between steps.

**Backend Mode**  
Remote execution via backend API, supporting distributed or cloud-based workflow processing.

All three modes must produce identical artifacts, enforce identical validation gates, and respect identical artifact ownership rules. Execution mode parity is validated at bundle registration time.

## Validation Gates

Validation gates enforce correctness before a workflow step can complete:

**Section Presence**  
Generated documents must contain all required sections as defined in the bundle manifest.

**Scope Purity**  
Layer 1 documents must not contain concrete workflow identifiers or repo-derived artifact names.

**Artifact Correctness**  
Produced artifacts must match their declared schema and pass structural validation.

**Forbidden Literals**  
Documents must not contain unresolved placeholder token patterns or references to legacy delivery scaffold identifiers.

Failed validation gates trigger refinement loops up to a configured maximum iteration count. Exhausted refinement loops result in a human-retry-required failure.

## Change Control

Changes to Layer 1 governance documents follow strict change control:

**Backward Compatibility**  
Changes must preserve backward compatibility where possible. Breaking changes require a new major version.

**Migration Plan**  
Breaking changes require a bundle migration plan documenting the upgrade path for existing bundles.

**Review Requirement**  
All Layer 1 changes require ecosystem-wide review before merge.

**Audit Trail**  
Every change produces an audit record including the change ID, author, rationale, and affected documents.
