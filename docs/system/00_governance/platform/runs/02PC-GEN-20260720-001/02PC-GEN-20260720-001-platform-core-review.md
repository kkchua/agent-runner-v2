---
doc_type: "review_artifact"
authority: "workflow-generated"
scan_policy: "exclude"
scan_reason: "run-scoped review artifact; exclude from operational scans"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-001"
---

# Platform Core Review

## Decision

**APPROVED**

The staged Layer 2 platform core constitution set passes all review
checks. No forbidden content was found. The document set is correctly
scoped to Layer 2, inherits Layer 1 governance without redefining it,
contains no Layer 3 bundle-specific drift, and satisfies all structural
and metadata requirements. The set is ready for deterministic validation.

## Layer Boundary Findings

### Layer 1 Governance

No Layer 1 redefinition or contradiction detected.

- README.md explicitly declares Layer 1 inheritance with a table mapping
  each inherited Layer 1 document to its template ID and how Layer 2
  applies it. It states: "Layer 1 is inherited, not modified."
- METADATA_CONTRACT.md states: "This contract does not modify or
  contradict Layer 1 baseline values." It extends Layer 1 vocabulary
  with platform-specific semantics without changing baseline meanings.
- BUNDLE_AUTHORING_CONTRACT.md references Layer 1 metadata baseline and
  Layer 2 extensions as inherited authority.
- VALIDATION_CONTRACT.md enforces Layer 1 baseline checks as a platform
  service without altering their definitions.
- RUNTIME_MODEL.md describes platform execution architecture without
  making ecosystem-wide governance claims.
- SHARED_SERVICES.md describes platform runtime services without
  redefining cross-ecosystem ownership or authority rules.

### Layer 3 Bundle-Specific Drift

No Layer 3 bundle-specific drift detected.

- BUNDLE_AUTHORING_CONTRACT.md defines the contract for all Layer 3
  bundles generically. It does not contain outputs or examples from any
  specific bundle masquerading as platform-wide rules.
- SHARED_SERVICES.md describes service APIs available to all bundles.
  Code examples use generic placeholder names (e.g., my_custom_action,
  my_workflow_v1), not specific bundle identifiers.
- VALIDATION_CONTRACT.md describes the validation composition pattern
  generically. The composition example uses placeholder names.
- No document contains job-specific evidence, run-specific outputs, or
  single-bundle artifacts presented as platform standards.

### Layer 2 Scope Compliance

All six documents contain content appropriate for Layer 2:

- Platform runtime architecture (RUNTIME_MODEL.md)
- Platform bundle authoring contract (BUNDLE_AUTHORING_CONTRACT.md)
- Platform shared services (SHARED_SERVICES.md)
- Platform metadata extensions (METADATA_CONTRACT.md)
- Platform validation model (VALIDATION_CONTRACT.md)
- Platform index and identity (README.md)

## Structure Findings

### Document Inventory

All six required permanent documents are present:

| Document | File | Template ID | Present |
|---|---|---|---|
| Platform Index | README.md | SYS-02-IDX | Yes |
| Runtime Model | RUNTIME_MODEL.md | SYS-02-RM | Yes |
| Bundle Authoring Contract | BUNDLE_AUTHORING_CONTRACT.md | SYS-02-BAC | Yes |
| Shared Services | SHARED_SERVICES.md | SYS-02-SS | Yes |
| Metadata Contract | METADATA_CONTRACT.md | SYS-02-MC | Yes |
| Validation Contract | VALIDATION_CONTRACT.md | SYS-02-VC | Yes |

### Document Map

The README.md Document Map table includes all six documents including
itself (README.md). The map is complete and correct.

### Required Sections Per Document

**README.md (SYS-02-IDX):**
- Platform Identity: Present
- Document Map: Present (self-including, six documents)
- Layer 1 Inheritance: Present
- Relationship to Other Layers: Present
- Audience: Present
- Document Status: Present

**RUNTIME_MODEL.md (SYS-02-RM):**
- Step Model: Present (prompt-driven and action-driven)
- Step Types: Present (all 9 step types listed)
- Execution Paths: Present (CLI, Daemon, Manual)
- Job Lifecycle: Present (state, phases)
- Coder Integration: Present (adapters, registry, role policies)
- Rejection And Retry: Present (refinement loop, replan, reject codes)
- Notification Model: Present (manager, configuration, events)

**BUNDLE_AUTHORING_CONTRACT.md (SYS-02-BAC):**
- Required Bundle Files: Present (structure and summary table)
- workflow.toml Format: Present (all sections documented)
- Artifact Key Conventions: Present (canonical keys, placeholders, naming)
- Bundle Governance Requirements: Present (TOML and package)
- Metadata Compliance: Present (frontmatter, inheritance, classification)

**SHARED_SERVICES.md (SYS-02-SS):**
- Context Extensions: Present (build_context_extensions)
- Artifact Resolution: Present (resolve_repo_or_runtime_path, known_artifact_paths)
- Path Contracts: Present (build_output_paths, workflow-owned contracts)
- Meta Sidecar: Present (contract, write_meta_sidecar, context keys)
- Notification Integration: Present (manager, configuration, events)
- Backend Sync Protocol: Present (daemon communication, client, payload)
- Action Registration: Present (@action decorator, platform actions, result contract)

**METADATA_CONTRACT.md (SYS-02-MC):**
- Platform doc_type Values: Present (baseline inherited + extensions)
- Platform authority Values: Present (baseline inherited + refinements)
- Additional Frontmatter Fields: Present (platform, template_id, managed_by)
- Inheritance Rules: Present (Layer 1 to Layer 2, Layer 2 extensions, Layer 2 to Layer 3)
- Scan Policy Expectations: Present (document classes, scanner behavior, platform rules)

**VALIDATION_CONTRACT.md (SYS-02-VC):**
- ValidationPlan Pattern: Present (DocumentationValidationPlan, plan structure, execution)
- Section Checks: Present (has_section, required sections table, rules)
- Frontmatter Enforcement: Present (has_frontmatter_field, required fields by class, violations)
- File Existence Checks: Present (required inventory, rules, sidecar validation)
- Bundle Validator Composition: Present (platform validators, bundle-local, composition pattern)
- Guidance for validate_* Actions: Present (when to write, design principles, output contract, rejection codes)

### Forbidden Content Absence

- No operational bootstrap mechanics or repository setup instructions.
- No evidence artifacts presented as permanent platform standards.
- No Layer 1 governance redefinition.
- No Layer 3 bundle-specific drift.

## Metadata Findings

### Frontmatter Compliance

All six permanent documents carry correct frontmatter:

| Field | Expected | README | RM | BAC | SS | MC | VC |
|---|---|---|---|---|---|---|---|
| template_id | SYS-02-* | PASS | PASS | PASS | PASS | PASS | PASS |
| doc_type | platform_standard | PASS | PASS | PASS | PASS | PASS | PASS |
| authority | workflow-generated | PASS | PASS | PASS | PASS | PASS | PASS |
| scan_policy | include | PASS | PASS | PASS | PASS | PASS | PASS |
| scan_reason | non-empty | PASS | PASS | PASS | PASS | PASS | PASS |
| layer | layer2 | PASS | PASS | PASS | PASS | PASS | PASS |
| platform | agent-runner-v2 | PASS | PASS | PASS | PASS | PASS | PASS |
| lifecycle_status | draft | PASS | PASS | PASS | PASS | PASS | PASS |
| effective_version | job ID | PASS | PASS | PASS | PASS | PASS | PASS |
| managed_by | workflow-generated | PASS | PASS | PASS | PASS | PASS | PASS |

### Lifecycle State

All documents correctly carry `lifecycle_status: "draft"`. No staged
document uses `published` or `active` lifecycle values. The README.md
explicitly states: "This is a staged run output. All documents carry
lifecycle_status: 'draft'."

### Platform Identity

All documents clearly identify `agent-runner-v2` as the platform in both
frontmatter (`platform: "agent-runner-v2"`) and body content. The
README.md Platform Identity section provides a clear description of what
agent-runner-v2 is and its role as a Layer 2 core.

### Metadata Inheritance

The METADATA_CONTRACT.md correctly inherits Layer 1 baseline values
without redefining them. Platform-specific extensions refine the
semantics of existing Layer 1 values (e.g., `platform_standard`,
`bundle_definition`, `platform-owned`, `bundle-owned`) for the
agent-runner-v2 context without introducing conflicting meanings.

## Cited Evidence

No offending content was found. The following positive evidence supports
the approval decision:

1. README.md, "Layer 1 Inheritance" section: "Layer 1 is inherited, not
   modified. This platform constitution: Does not change the meaning of
   any Layer 1 doc_type or authority value."

2. METADATA_CONTRACT.md, "Overview" section: "This contract does not
   modify or contradict Layer 1 baseline values. Layer 1 defines the
   common field names and baseline vocabulary. This document extends
   them for the agent-runner-v2 platform."

3. README.md, "Document Map" section: Table includes all six documents
   with README.md itself listed as the first entry.

4. All six documents carry `lifecycle_status: "draft"` in frontmatter,
   correctly reflecting staged status.

5. All six documents carry `platform: "agent-runner-v2"` in frontmatter,
   establishing clear platform identity.

6. BUNDLE_AUTHORING_CONTRACT.md uses generic placeholder names
   (e.g., my_workflow_v1, my_custom_action) in examples, not specific
   bundle identifiers.

7. VALIDATION_CONTRACT.md correctly separates platform-level validation
   from bundle-local checks in the "Validation Scope" table.

## Next Action

Proceed to deterministic validation (validate_platform_core_docs step).
The staged set is structurally complete, metadata-compliant, and
layer-boundary-clean.
