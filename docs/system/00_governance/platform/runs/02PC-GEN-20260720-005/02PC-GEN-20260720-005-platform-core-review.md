---
template_id: SYS-02-REV
version: "1.0"
doc_type: "review_artifact"
authority: "workflow-generated"
scan_policy: "exclude"
scan_reason: "run-scoped review evidence; excluded from operational scans"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-005"
managed_by: workflow-generated
generated_at: "2026-07-20T16:30:01+08:00"
---

# Platform Core Review -- agent-runner-v2 Layer 2 Constitution

## Decision

**APPROVED**

The staged Layer 2 platform core constitution set is acceptable for
deterministic validation. All six permanent documents are present,
properly scoped to Layer 2, and free of forbidden content. Platform
identity is clear throughout, metadata values conform to the Layer 1
baseline, and the document map is self-including.

## Layer Boundary Findings

### No Layer 1 Governance Redefinition

All six documents inherit Layer 1 governance without redefining it:

- README.md explicitly states "This platform constitution inherits from
  the Layer 1 Governance Foundation without redefining it" and lists
  specific inherited elements (layer definitions, ownership boundaries,
  metadata baseline, governance lifecycle, bundle taxonomy).
- RUNTIME_MODEL.md describes execution architecture (step model,
  daemon/CLI/manual modes, coder integration) -- all Layer 2 platform
  concerns, not ecosystem governance.
- BUNDLE_AUTHORING_CONTRACT.md defines bundle requirements for
  agent-runner-v2 specifically -- a platform contract, not ecosystem
  rules.
- SHARED_SERVICES.md defines runtime services (context extensions,
  artifact resolution, sidecar contract) -- platform operational model.
- METADATA_CONTRACT.md explicitly declares it "does not redefine any
  Layer 1 baseline field or vocabulary" and only extends where the
  platform requires more specific classification.
- VALIDATION_CONTRACT.md defines the platform validation pattern using
  the platform's own validation infrastructure
  (DocumentationValidationPlan, has_section, has_frontmatter_field).

### No Layer 3 Bundle-Specific Drift

No document contains bundle-specific outputs or examples presented as
platform-wide rules:

- No concrete workflow bundle names appear as normative platform rules.
- Source code module references (e.g., runtime_context.py,
  step_runner.py) are factual citations of the platform runtime, not
  bundle-specific content.
- The BUNDLE_AUTHORING_CONTRACT defines generic requirements for ANY
  Layer 3 bundle, not a specific bundle's outputs.

### Platform Identity Present and Clear

Every document declares:
- `platform: "agent-runner-v2"` in frontmatter
- References to agent-runner-v2 as the owning platform throughout body text

README.md opens with a platform identity section stating: "agent-runner-v2
is a standalone, multi-step AI workflow runner."

## Structure Findings

### All Six Required Documents Present

| Document | File | Template ID | Status |
|---|---|---|---|
| Platform Index | README.md | SYS-02-IDX | Present |
| Runtime Model | RUNTIME_MODEL.md | SYS-02-RM | Present |
| Bundle Authoring Contract | BUNDLE_AUTHORING_CONTRACT.md | SYS-02-BAC | Present |
| Shared Services | SHARED_SERVICES.md | SYS-02-SS | Present |
| Metadata Contract | METADATA_CONTRACT.md | SYS-02-MC | Present |
| Validation Contract | VALIDATION_CONTRACT.md | SYS-02-VC | Present |

### Document Map Self-Including

README.md includes itself as "Platform Index" with file `README.md` and
template ID `SYS-02-IDX` in the six-document document map table. No
omission.

### Mandatory Sections Present

Each document was checked against the required sections defined in the
Layer 2 Platform Core Specification:

- **READMEE.md**: platform overview, document map (self-including),
  audience summary, Layer 1 inheritance statement, relationship to other
  layers -- all present.
- **RUNTIME_MODEL.md**: step model, step types, execution paths (CLI,
  daemon, manual), job lifecycle, coder integration, rejection and retry
  model, notification model -- all present.
- **BUNDLE_AUTHORING_CONTRACT.md**: required bundle files, workflow.toml
  format, artifact key conventions, bundle governance requirements,
  metadata compliance -- all present.
- **SHARED_SERVICES.md**: context extensions, artifact resolution, path
  contracts, meta sidecar, notification integration, backend sync
  protocol, action registration -- all present.
- **METADATA_CONTRACT.md**: platform doc_type values, platform authority
  values, additional frontmatter fields, inheritance rules, scan policy
  expectations -- all present.
- **VALIDATION_CONTRACT.md**: DocumentationValidationPlan pattern,
  section-check conventions, frontmatter enforcement, file existence
  checks, bundle validator composition, validate_* action guidance -- all
  present.

### No Operational Bootstrap Mechanics

None of the six documents contain repository setup instructions,
installation procedures, bootstrap commands, or deployment runbooks. The
RUNTIME_MODEL describes execution architecture conceptually, not as
step-by-step operational procedures.

## Metadata Findings

### Frontmatter Compliance per Document

All six documents carry valid YAML frontmatter with these consistent
values:

- `doc_type: "platform_standard"` -- valid Layer 1 value
- `authority: "workflow-generated"` -- valid Layer 1 value
- `scan_policy: "include"` -- valid Layer 1 value, with non-empty
  scan_reason
- `scan_reason` -- non-empty, descriptive, appropriate for each document
- `layer: "layer2"` -- correct for Layer 2 platform standards
- `platform: "agent-runner-v2"` -- consistent platform identity
- `lifecycle_status: "draft"` -- correct for staged (not yet published)
  documents
- `template_id` -- follows `SYS-02-XX` convention
- `version: "1.0"` -- present on all
- `managed_by: workflow-generated` -- present on all
- `effective_version: "02PC-GEN-20260720-005"` -- present on all

### No Lifecycle-State Misuse

All documents use `lifecycle_status: "draft"`. No document incorrectly
uses `published` or `active` while staged. This is correct: the
publication step in the workflow will transition lifecycle status upon
activation.

### No Evidence-as-Standard

The context inventory artifact (02PC-GEN-20260720-005-platform-context-
inventory.md) carries `doc_type: "validation_artifact"` and
`scan_policy: "exclude"`, correctly classifying it as temporary evidence
rather than a permanent platform standard. The six permanent documents
all carry `doc_type: "platform_standard"` with `scan_policy: "include"`.

### Metadata Inheritance Correct

The METADATA_CONTRACT.md correctly identifies:
- Layer 1 baseline fields inherited without redefinition
- Platform extension fields (platform, template_id naming convention,
  managed_by)
- Inheritance direction (L1 -> L2 -> L3)
- Prohibition on Layer 3 redefining L1 or L2 values

## Cited Evidence

No rejection findings to cite. The staged set is clean against all
forbidden-content checks:

1. No Layer 1 governance redefinition or contradiction.
2. No bundle-specific outputs presented as platform-wide rules.
3. All six required permanent documents present.
4. Platform identity (agent-runner-v2) clear in every document.
5. Metadata values conform to Layer 1 baseline vocabularies.
6. No evidence artifacts classified as permanent platform standards.
7. All mandatory sections present per the L2 specification.
8. No operational bootstrap mechanics or repository setup instructions.
9. Document map includes README.md in the six-document permanent set.
10. No lifecycle-state misuse; all staged docs use "draft".

## Next Action

Proceed to deterministic validation (validate_platform_core_docs step).
The staged set is structurally complete, properly scoped, and
metadata-compliant. Validation should confirm:
- All required frontmatter fields with valid values
- All required sections present using has_section checks
- All six files exist on disk
- No forbidden content patterns detected
