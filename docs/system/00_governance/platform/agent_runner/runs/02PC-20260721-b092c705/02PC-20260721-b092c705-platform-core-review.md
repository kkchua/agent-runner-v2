---
doc_type: "review_artifact"
authority: "workflow-generated"
scan_policy: "exclude"
scan_reason: "run-scoped platform core review artifact; temporary evidence only"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-20260721-b092c705"
---

# Platform Core Review

## Decision

APPROVED

The staged Layer 2 platform core constitution set for agent-runner-v2
is acceptable for deterministic validation. All six required permanent
documents are present, carry correct metadata, respect Layer 2 scope
boundaries, inherit Layer 1 governance without redefinition, and contain
no Layer 3 bundle-specific drift or forbidden content.

## Layer Boundary Findings

### Layer 1 Governance Inheritance

No Layer 1 redefinition or contradiction detected.

- README.md "Layer 1 Inheritance" section explicitly states: "This
  platform constitution inherits from Layer 1 governance without
  redefining it." It correctly describes Layer 1 as "the ecosystem
  constitution" covering "three-layer architecture, document authority,
  bundle taxonomy, governance lifecycle, and metadata standard."
- METADATA_CONTRACT.md "Inheritance Rules" section correctly states:
  "Layer 1 defines the common field names and baseline vocabulary. All
  documents across all layers inherit these fields." The platform
  extensions (platform, template_id, managed_by, lifecycle_status,
  effective_version) are clearly additive and do not redefine Layer 1
  baseline values.
- All doc_type and authority values used in the staged set match the
  Layer 1 vocabulary defined in METADATA_STANDARD.md and
  DOCUMENT_AUTHORITY.md.

### Layer 3 Bundle-Specific Drift

No bundle-specific outputs or examples presented as platform-wide rules.

- BUNDLE_AUTHORING_CONTRACT.md defines the contract for all Layer 3
  bundles, using generic examples (e.g., "my_bundle_name", "my_bundle")
  that illustrate the pattern without presenting any specific bundle's
  configuration as a platform rule.
- VALIDATION_CONTRACT.md defines the platform validation model using
  the DocumentationValidationPlan pattern from the platform source
  code. Its examples (e.g., "MY_OUTPUT", "MY_REPORT") are clearly
  illustrative placeholders for Layer 3 authors.
- No concrete Layer 3 bundle inventory is included.

### Platform Identity

Platform identity "agent-runner-v2" is clearly stated in all six
permanent documents. Every document carries `platform: "agent-runner-v2"`
in frontmatter. The README.md "Platform Identity" section establishes
the platform as "a general-purpose workflow execution engine" and
explains its role as one of several possible Layer 2 cores.

### Evidence Separation

No evidence artifacts are presented as permanent platform standards.
The context inventory correctly carries `doc_type: "validation_artifact"`
with `scan_policy: "exclude"` and explicitly states it is "comparison
context only" and "not part of the permanent Layer 2 platform set."

### Bootstrap and Operational Content

No repository setup instructions or bootstrap mechanics are present.
README.md explicitly states: "It does not serve as a runtime operations
manual." The documents describe platform contracts at the appropriate
Layer 2 abstraction level.

## Structure Findings

### Document Inventory

All six required permanent documents are present:

| Document | Template ID | Present |
|---|---|---|
| README.md | SYS-02-IDX | Yes |
| RUNTIME_MODEL.md | SYS-02-RM | Yes |
| BUNDLE_AUTHORING_CONTRACT.md | SYS-02-BAC | Yes |
| SHARED_SERVICES.md | SYS-02-SS | Yes |
| METADATA_CONTRACT.md | SYS-02-MC | Yes |
| VALIDATION_CONTRACT.md | SYS-02-VC | Yes |

### Document Map Completeness

README.md "Document Map" section lists all six permanent documents
including itself. It explicitly states "This platform constitution set
contains six permanent documents, including this index" and provides a
table with all six entries.

### Required Sections per Document

All mandatory sections are present:

- README.md: Document Map, Platform Identity, Layer 1 Inheritance
- RUNTIME_MODEL.md: Step Model, Execution Paths, Job Lifecycle,
  Coder Integration, Rejection And Retry
- BUNDLE_AUTHORING_CONTRACT.md: Required Bundle Files, workflow.toml
  Format, Artifact Key Conventions, Bundle Governance Requirements,
  Metadata Compliance
- SHARED_SERVICES.md: Context Extensions, Artifact Resolution, Path
  Contracts, Meta Sidecar, Notification Integration, Backend Sync
  Protocol, Action Registration
- METADATA_CONTRACT.md: Platform doc_type Values, Platform authority
  Values, Additional Frontmatter Fields, Inheritance Rules, Scan
  Policy Expectations
- VALIDATION_CONTRACT.md: ValidationPlan Pattern, Section Checks,
  Frontmatter Enforcement, File Existence Checks, Bundle Validator
  Composition

### Function Signature Cross-Verification

Function signatures in SHARED_SERVICES.md were verified against the
platform source code:

- `build_context_extensions(*, state, step, step_cfg, ctx,
  project_root)` -- matches
  `agent_runner_v2/bootstrap/workflows/default/02_platform_core_foundation_v1/context_extensions.py`
  line 35.
- `resolve_repo_or_runtime_path(path_str, *, project_root,
  runtime_root)` -- matches `runtime_context.py` line 158.
- `write_meta_sidecar(meta_path_like, *, status, remark, artifacts,
  project_root, runtime_root, extra)` -- matches `runtime_context.py`
  line 273.
- `build_output_paths(*, job_id, mode)` -- matches
  `output_paths.py` line 4.

### Resolution Order Accuracy

The "Resolution Order" section in SHARED_SERVICES.md accurately
describes the prefix-dispatch behavior of `resolve_repo_or_runtime_path()`.
The source code (runtime_context.py lines 158-187) confirms: absolute
paths returned unchanged, repo-owned prefixes (docs/, archive/,
scripts/, temp/) resolve under project root, .ukbe-runner/ prefix
resolves under runner home, all other paths resolve under jobs root.
No forbidden phrases ("check the repository working tree first",
"fall back to the runtime artifact root") are present.

### Meta Sidecar Repair Accuracy

Both RUNTIME_MODEL.md and SHARED_SERVICES.md correctly describe the
meta.json sidecar as the primary communication channel AND the repair
fallback via `_repair_or_validate_meta_json()` in step_runner.py. The
source code (step_runner.py lines 637-677) confirms the function handles
MetaJsonMissingError and MetaJsonInvalidError with repair from parsed
stdout. No forbidden phrases ("no disk recovery functions",
"no stdout JSON parsing") are present.

### Authority and Managed-by Orthogonality

METADATA_CONTRACT.md "Usage Rules" section explicitly states: "The
fields authority and managed_by are orthogonal axes." It defines
authority as "Who owns the canonical truth" and managed_by as "What
mechanism produced and maintains this file." It provides the consistency
example: a document with authority "platform-owned" and managed_by
"workflow-generated" is consistent.

### Cross-Document Consistency

All six documents agree on:

- Platform identifier: "agent-runner-v2"
- Layer: "layer2"
- Doc type: "platform_standard"
- Authority: "workflow-generated" (correct for staged draft)
- Metadata vocabulary inherited from Layer 1
- Six-document permanent set

## Metadata Findings

### Frontmatter Completeness

All six permanent documents carry: template_id, version, doc_type,
authority, scan_policy, scan_reason, layer, platform, lifecycle_status,
effective_version, managed_by.

### Layer 1 Baseline Compliance

- doc_type values ("platform_standard", "validation_artifact") match
  the Layer 1 allowed vocabulary.
- authority values ("workflow-generated") match the Layer 1 allowed
  vocabulary.
- scan_policy values ("include" for permanent, "exclude" for evidence)
  match the Layer 1 allowed vocabulary.
- layer values ("layer2") match the Layer 1 allowed layer values.
- No generated document claims "human-authored" authority.

### Platform Extension Compliance

- platform: "agent-runner-v2" on all documents.
- lifecycle_status: "draft" on all staged documents, which is correct
  for documents not yet published.
- No "published" or "active" lifecycle values appear in staged docs.

### Lifecycle State Appropriateness

All staged documents correctly carry lifecycle_status: "draft". The
metadata contract lists the lifecycle states as: draft, review,
approved, published, superseded, deprecated, retired. These match the
Layer 1 governance lifecycle standard. No lifecycle-state misuse is
present.

### ASCII Compliance

All six documents confirmed ASCII-only via binary read test.

## Cited Evidence

No rejection findings. All review criteria pass. The following positive
observations are cited for the record:

- README.md line 62-63: "This platform constitution inherits from
  Layer 1 governance without redefining it."
- README.md lines 48-58: Document map lists all six permanent documents
  including README.md itself.
- README.md lines 99-106: Explicit exclusions stating the document set
  does not include Layer 1 governance, bundle inventories, job-history
  evidence, or setup guides.
- METADATA_CONTRACT.md lines 101-117: Explicit orthogonality statement
  for authority and managed_by fields.
- SHARED_SERVICES.md lines 99-115: Accurate prefix-dispatch resolution
  order matching runtime_context.py source code.
- SHARED_SERVICES.md lines 210-232: Accurate description of meta sidecar
  repair fallback matching step_runner.py source code.
- RUNTIME_MODEL.md lines 184-192: Accurate description of meta sidecar
  repair covering MetaJsonMissingError and MetaJsonInvalidError.
- VALIDATION_CONTRACT.md lines 97-104: Complete template_id to required
  section mapping table matching the actual document headings.

## Next Action

Proceed to deterministic validation (Step 5: Validate Platform Core
Docs). The staged set is structurally complete, metadata-compliant,
and layer-boundary correct. Validation should confirm all programmatic
checks pass.
