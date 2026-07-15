---
template_id: "SYS-00-RG"
version: "1.0.0"
doc_type: "system"
managed_by: "workflow-generated"
generated_at: "2026-07-15T22:38:14+08:00"
workflow: "00_layer1_governance_bootstrap_v1"
step: "generate_layer1_governance_docs"
change_id: "00L1-20260715-74497d6b"
---

> Managed by workflow: `00_layer1_governance_bootstrap_v1` / step: `generate_layer1_governance_docs`
> This file is workflow-generated and protected from manual edits.

# Runtime Governance

## Purpose

This document defines the steady-state runtime operating model for the
agent-runner framework. It governs how plugin workflow bundles are published,
installed, discovered, and executed. It establishes the control-plane
expectations for the registry, role resolution, artifact ownership, execution
mode parity, and validation gates.

This document does not define repository-specific output paths or
repository-specific artifact ownership. It operates at the runtime
control-plane level only.

## Runtime Scope Model

The runtime operates in two execution modes:

- **Bootstrap mode.** Used during initial governance setup and Layer 1
  document generation. Bootstrap mode runs the governance bootstrap workflow
  to produce or refresh permanent governance documents.

- **Steady-state mode.** Used for ongoing plugin workflow execution.
  Steady-state mode discovers, loads, and executes plugin workflow bundles
  through the standard runner pipeline.

Both modes share the same execution pipeline, step runner, and artifact
resolution mechanism. No separate code path exists for either mode — the
runner spawns a fresh subprocess per workflow invocation, loading the latest
code and configuration from disk.

## Bundle Publish And Install Model

Plugin workflow bundles follow a publish-then-install lifecycle:

### Publish

A plugin workflow bundle is published when its self-contained directory
(manifest, prompts, context extensions, and optional governance) is seeded to
the global runtime home. The global runtime home serves as the authoritative
discovery location for published bundles.

### Install

Installation is implicit: when the runner needs a workflow, it first checks
the global runtime home. If the bundle is found there, it is loaded directly.
If not found, the runner falls back to the local repository's workflow
directory.

### Dual-Path Discovery

1. **Global path (first).** The runner checks the global runtime home for
   the requested workflow bundle. If present, the global copy is used.
2. **Local path (fallback).** If the bundle is not in the global runtime
   home, the runner checks the local repository's workflow directory.

This dual-path model allows shared bundles to be published once and used
across multiple repositories, while still supporting repository-local
bundles that have not been globally published.

## Registry Control Plane

The registry maintains the shared configuration that governs runtime
behavior:

### Role Registry

The role registry maps logical role names to coder, connection, and model
configurations. Roles are typed as architect, reviewer, or developer. Each
role specifies which coder backend to use, which connection provider to use,
and which model to invoke.

### Role Policy Registry

The role policy registry defines role policies that constrain which roles a
step may use. Each policy specifies a default role and a set of allowed
roles. Steps reference a role policy by name; the runner resolves the policy
to determine the actual coder role to invoke.

### Connection Registry

The connection registry defines connection providers and their
authentication models. Each connection specifies a provider, supported coder
backends, model format, and authentication type. The runner uses the
connection registry to configure API endpoints and authentication for each
coder invocation.

## Plugin Bundle Control Model

Plugin workflow bundles are the primary unit of extensibility. A plugin
workflow bundle may be either a `single-workflow` bundle or a
`multi-workflow` bundle:

- **single-workflow** bundles contain one workflow definition with its own
  steps, prompts, and artifact keys. This is the simplest and most common
  form.

- **multi-workflow** bundles contain multiple workflow definitions within a
  single package. Each workflow within the bundle has its own steps,
  prompts, and artifact keys, but they share the bundle's governance and
  context extension infrastructure.

Both bundle forms follow the same discovery, resolution, and execution
pipeline. The runtime does not distinguish between them at the control-plane
level — the bundle manifest declares which workflows it contains, and the
runner loads them accordingly.

## Role And Connection Resolution

Role and connection resolution follows a deterministic chain:

1. The step configuration in the workflow manifest specifies a role policy
   by name.
2. The role policy registry resolves the policy to a default role and a set
   of allowed roles.
3. The role registry resolves the role name to a coder, connection, and
   model identifier.
4. The connection registry resolves the connection name to a provider,
   base URL, and authentication model.
5. The runner uses the resolved coder, connection, and model to invoke the
   LLM for that step.

If the `must_differ` flag is set on a step, the runner ensures that the coder
used for that step differs from the coder used in the previous step, if any.

## Artifact Ownership Enforcement

Artifact ownership is enforced at the workflow level:

1. **Declared ownership.** Each workflow step declares the artifact keys it
   produces and the artifact keys it requires as inputs. The runner uses
   these declarations to enforce ownership boundaries.

2. **No cross-bundle writes.** A step may only write artifacts whose keys
   are declared in its own bundle's manifest. Writing to artifact keys owned
   by another bundle is prohibited.

3. **Layer 1 protection.** The four Layer 1 governance documents are owned
   exclusively by the governance bootstrap workflow. Plugin workflow bundles
   must not declare artifact keys that resolve to Layer 1 document paths.

4. **Transient artifacts.** Review, validation, and audit artifacts are
   supporting evidence only. They are not permanent governance documents and
   must not be declared as permanent produces by plugin workflow bundles.

## Execution Mode Parity

All execution modes — bootstrap, manual batch, and daemon — must follow the
same execution pipeline:

- **Same runner invocation.** The daemon spawns the standard runner command
  via subprocess, identical to manual batch invocation. No special daemon-only
  execution path exists.

- **Same code loading.** Each invocation loads the latest code and
  configuration from disk, ensuring that code changes take effect immediately
  without requiring a daemon restart.

- **Same artifact resolution.** Artifact paths, context extensions, and
  prompt placeholder substitution follow the same resolution mechanism
  regardless of execution mode.

- **Same notification and completion handling.** Workflow completion,
  failure, and notification logic is shared across all execution modes. No
  mode-specific parallel logic exists.

## Validation Gates

The runtime enforces validation gates at the following points:

1. **Pre-execution validation.** Before a step runs, the runner validates
   that required input artifacts exist and are accessible.

2. **Post-execution validation.** After a step completes, the runner
   validates that declared produce artifacts were actually written to disk.

3. **Scope purity validation.** For governance workflows, the validator
   checks that generated documents do not contain concrete workflow
   identifiers, repository-derived artifact names, or forbidden tokens in
   body text.

4. **Frontmatter validation.** For workflow-generated documents, the
   validator checks that all required frontmatter fields are present with
   correct values.

5. **Section validation.** For governance documents, the validator checks
   that all required sections exist and are populated.

Validation failures trigger the refinement loop if the step supports
reject-refine routing. If refinement iterations are exhausted, the workflow
reports a human-retry-required failure.

## Change Control

Changes to the runtime governance model must follow the governance workflow
cycle:

1. **Generate.** The governance bootstrap workflow generates or refreshes
   Layer 1 documents.

2. **Review.** A reviewer step evaluates the generated documents for
   correctness, scope purity, and governance compliance.

3. **Refine.** If review rejects, the refinement step updates the documents
   in-place and returns to review.

4. **Validate.** The validation step runs deterministic checks on file
   existence, frontmatter, sections, and scope purity.

5. **Audit.** The audit step performs a final accuracy check against the
   governance contract.

6. **Completion.** Upon passing all gates, the workflow records completion
   and the documents are accepted as the new authoritative set.

No step in this cycle may be skipped. Manual edits to Layer 1 governance
documents are prohibited. All changes must flow through the full governance
workflow cycle with a new change ID for each run.
