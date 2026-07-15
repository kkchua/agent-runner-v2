---
template_id: "SYS-00-BT"
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

# Bundle Taxonomy

## Bundle Classes

The governance framework recognizes two primary bundle classes:

### Core Governance Bundles

Core governance bundles produce permanent ecosystem-level governance
documents. They are owned by the governance bootstrap workflow and are
canonical in visibility — meaning they represent the authoritative source of
truth for their document set.

Characteristics:

- Owned by the governance bootstrap workflow.
- Produce permanent, protected governance documents.
- Must not contain repository-specific content, concrete workflow
  identifiers, or repository-derived artifact names.
- Subject to the full generate, review, refine, validate, and audit cycle.
- Changes require a governance bootstrap run with a new change ID.

### Plugin Workflow Bundles

Plugin workflow bundles are self-contained, reusable workflow packages that
define steps, prompts, artifact keys, and coder policies. They are the primary
unit of extensibility for the agent-runner framework.

Characteristics:

- May be single-workflow or multi-workflow bundles.
- Each bundle contains a declarative manifest, prompt templates, optional
  context extensions, and optional bundle governance.
- Discovered through a dual-path model: global runtime home first, local
  repository fallback second.
- Plugin workflow bundles may produce artifacts governed by Layer 1 policy
  but do not own Layer 1 governance documents.
- Plugin workflow bundles must not modify, rename, or delete Layer 1
  governance documents.

## Ownership Rules

Ownership boundaries between bundle classes are strict and enforced:

1. **Core governance bundles own Layer 1 documents.** Only the governance
   bootstrap workflow may create, update, or delete the four Layer 1
   governance documents. Plugin workflow bundles must not write to Layer 1
   paths.

2. **Plugin workflow bundles own their own artifacts.** Each plugin workflow
   bundle owns the artifacts it declares in its manifest. Artifact keys must
   not collide with Layer 1 artifact keys.

3. **No cross-bundle writes.** A bundle may not write artifacts owned by
   another bundle. Artifact ownership is determined by the bundle that
   declares the artifact key in its manifest.

4. **Governance contract precedence.** When a plugin workflow bundle's local
   prompt text conflicts with Layer 1 governance policy, the Layer 1
   governance contract takes precedence.

5. **Review and validation artifacts are transient.** Artifacts produced by
   review, validation, or audit steps are supporting evidence only. They are
   not permanent governance documents and must not become part of the Layer 1
   document set.

## Packaging Rules

Plugin workflow bundles must conform to the following packaging rules:

### Manifest

Every plugin workflow bundle must include a declarative manifest file that
declares:

- Workflow name, version, label, and job prefix.
- Step definitions with routing rules (success, reject-refine).
- Artifact keys for produces and required inputs.
- Coder role policies per step.
- Optional human approval gates.
- Optional notification flags.

### Prompt Templates

Each step that requires LLM interaction must have a corresponding prompt
template file. Prompt templates may use placeholder tokens that are resolved
at runtime by the context builder.

### Context Extensions

Bundles may include optional context extension modules that inject
workflow-specific paths and variables into the prompt rendering context.
Context extensions must not introduce repository-specific logic into Layer 1
governance documents.

### Bundle Governance

Bundles may include optional bundle governance files that define
canonical source documents, generated adapter targets, and governance
inclusion rules. Bundle governance is advisory to the workflow itself and
does not override Layer 1 policy.

### Directory Structure

A plugin workflow bundle is a self-contained directory containing:

- The declarative manifest file.
- A prompts subdirectory for prompt templates.
- Optional context extension module.
- Optional bundle governance files and subdirectory.

The bundle directory name serves as the unique identifier for the workflow
within the framework's discovery and registry systems.
