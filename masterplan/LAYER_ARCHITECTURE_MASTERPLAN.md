---
doc_type: "masterplan"
authority: "human-authored"
scan_policy: "exclude"
scan_reason: "reference blueprint; exclude from operational document scans"
---

# Layer Architecture Masterplan

## Status

This document is the current architectural blueprint for the ecosystem
documentation and workflow layering model.

It is intentionally separate from the existing workflow-generated
bootstrap documents. Those generated documents reflect an older model and
must not be treated as the source of truth for future Layer 1 redesign
work.

## Purpose

This master plan defines the target operating model for a three-layer
ecosystem:

- Layer 1: core governance and ownership rules
- Layer 2: platform or domain core
- Layer 3: concrete workflow bundles and delivery outputs

The purpose of this document is to fix the architectural boundaries first
so the next workflow design is derived from a correct model rather than
trying to repair a drifting one.

## Design Principles

### Governance Before Implementation

Layer 1 defines what must be governed, who owns what, and what may or may
not appear in lower layers. It does not define runtime mechanics,
bootstrap copy behavior, installer flow, registry internals, or execution
algorithms.

### Stable Boundaries

Each layer must have a clear contract:

- what it owns
- what it may reference
- what it must not define
- what artifacts it is allowed to generate

### Replaceable Layer 2s

The ecosystem must support multiple Layer 2 cores without changing Layer
1. Examples include:

- AI-driven SDLC core
- ComfyUI core
- n8n core
- agent-runner-v2 core

Each Layer 2 translates Layer 1 governance into a platform-specific
operating model.

### Bundle-Centric Delivery

Layer 3 is where practical workflows live. Layer 3 bundles are the units
that actually generate documents, reports, scaffolds, assets, or other
delivery outputs.

### Drift Prevention

No layer may silently absorb responsibilities from another layer. When
drift appears, the fix is to restore the boundary, not to refine wording
inside the wrong layer.

## The Three-Layer Model

## Layer 1

### Role

Layer 1 is the ecosystem constitution.

It defines the non-negotiable governance model that applies across all
Layer 2 cores and all Layer 3 bundles that choose to adopt this
architecture.

### Objective

Layer 1 exists to answer these questions:

- What is the purpose of the ecosystem?
- What kinds of layers are allowed?
- What does each layer own?
- What is forbidden in each layer?
- How are governance documents structured?
- How are ownership, review, approval, and change authority defined?

### What Layer 1 Owns

Layer 1 owns only cross-ecosystem governance concerns:

- layer definitions
- ownership boundaries
- document authority model
- document metadata classification rules
- bundle taxonomy at a conceptual level
- change control principles
- review and approval obligations
- naming and classification principles
- inheritance rules between layers
- rules for what lower layers must declare for themselves

### What Layer 1 Must Not Own

Layer 1 must not define:

- runtime implementation details
- repository bootstrap mechanics
- installation flow
- publish flow
- registry API behavior
- execution engine internals
- path resolution algorithms
- platform-specific node or tool behavior
- concrete repository inventory
- concrete workflow bundle inventory
- concrete generated outputs for a specific domain

If a statement requires knowledge of how a specific platform executes,
installs, validates, stores, or publishes something, it does not belong in
Layer 1.

### Layer 1 Deliverables

Layer 1 should produce a compact and stable governance set, for example:

- an index document for the architecture
- a layer definition document
- a bundle and ownership taxonomy
- a governance lifecycle standard
- a documentation authority standard
- a metadata standard

The exact filenames may change, but the content focus must remain purely
governance-oriented.

### Layer 1 Metadata Governance

Layer 1 should define a minimal metadata convention that all governed
documents may use for classification and scan control.

The purpose of this metadata is not presentation. The purpose is:

- to distinguish human-authored reference material from generated outputs
- to distinguish governance documents from operational artifacts
- to allow scanners, validators, and workflows to include or exclude
  documents deterministically

At minimum, the governance model should support these metadata fields:

- `doc_type`
- `authority`
- `scan_policy`
- `scan_reason`

Recommended meanings:

| Field | Purpose |
|---|---|
| `doc_type` | High-level classification such as `masterplan`, `system`, `workflow_output`, or `review_artifact`. |
| `authority` | Ownership source such as `human-authored` or `workflow-generated`. |
| `scan_policy` | Scanner intent such as `include`, `exclude`, or `conditional`. |
| `scan_reason` | Human-readable reason for the scan policy. |

### Layer 1 Scan Policy Rule

Layer 1 should define the rule that document scanners must honor explicit
scan metadata when present.

The initial policy should be:

- documents marked with `scan_policy: "exclude"` are excluded from normal
  operational scans
- excluded documents may still be read deliberately by a workflow or a
  human when they are the intended source
- absence of scan metadata does not automatically make a document
  authoritative

This gives the ecosystem a deterministic control point similar in intent
to search-engine exclusion, but implemented as repo-local governance
metadata rather than a web crawler protocol.

### Layer 1 Metadata Standard

Layer 1 should define a strict but small metadata standard that can be
applied across Layer 1, Layer 2, and Layer 3 documents.

The goal is to make document ownership and scan behavior machine-readable
without forcing every layer to share the same content model.

### Required Metadata Fields

Every governed document that participates in workflow scanning,
classification, review, or publication should support these fields:

| Field | Required | Description |
|---|---|---|
| `doc_type` | Yes | Functional class of the document. |
| `authority` | Yes | Who owns the truth of the document. |
| `scan_policy` | Yes | Default scanner treatment. |
| `scan_reason` | Yes | Why the scan policy was chosen. |

Additional fields may be added by Layer 2 or Layer 3, but these Layer 1
fields form the common minimum contract.

### Allowed `doc_type` Values

Layer 1 should define the initial `doc_type` vocabulary as:

| Value | Meaning |
|---|---|
| `masterplan` | Human-authored reference blueprint used to guide design decisions. |
| `system` | System-level governance or platform document intended to be part of a governed doc set. |
| `workflow_output` | Concrete output generated by a workflow execution. |
| `review_artifact` | Review result, critique, or recommendation artifact. |
| `validation_artifact` | Deterministic validation result or compliance artifact. |
| `audit_artifact` | Audit or verification artifact created after review or validation. |
| `bundle_definition` | A bundle-local definition or control document owned by a workflow bundle. |
| `platform_standard` | A Layer 2 operating standard for a specific platform or domain. |

Layer 2 may extend this vocabulary for platform needs, but it must not
change the meaning of Layer 1 values.

### Allowed `authority` Values

Layer 1 should define the initial `authority` vocabulary as:

| Value | Meaning |
|---|---|
| `human-authored` | Canonical content is maintained directly by humans. |
| `workflow-generated` | Canonical content is produced and maintained by a workflow. |
| `bundle-owned` | Canonical content is owned by a specific Layer 3 bundle. |
| `platform-owned` | Canonical content is owned by a specific Layer 2 platform core. |
| `derived` | Content is generated from another authoritative source and is not itself the root authority. |

Layer 2 and Layer 3 may introduce narrower authority values, but they
must preserve this distinction between canonical and derived content.

### Allowed `scan_policy` Values

Layer 1 should define the initial `scan_policy` vocabulary as:

| Value | Meaning |
|---|---|
| `include` | Include in normal operational scans. |
| `exclude` | Exclude from normal operational scans unless explicitly targeted. |
| `conditional` | Include only when a scanner is running under rules that explicitly request this class. |

This avoids ambiguous interpretations such as using blank metadata to mean
either include or exclude.

### Field Semantics

The fields should be interpreted as follows:

- `doc_type` answers what this document is
- `authority` answers who owns the truth of this document
- `scan_policy` answers whether scanners should consider it by default
- `scan_reason` explains the intended use so exclusions remain auditable

### Inheritance Rules

The metadata convention should inherit downward across layers as follows:

- Layer 1 defines the common field names and baseline vocabulary
- Layer 2 may extend value sets for platform-specific needs
- Layer 3 may apply platform-specific values defined by its parent Layer 2
- no lower layer may redefine the meaning of Layer 1 baseline values

This preserves interoperability while still allowing platform-specific
detail where needed.

### Layer-Specific Expectations

Expected defaults by layer:

| Layer | Typical `doc_type` | Typical `authority` | Typical `scan_policy` |
|---|---|---|---|
| Layer 1 | `system` or `masterplan` | `human-authored` or `workflow-generated` | `include` or `exclude` |
| Layer 2 | `platform_standard` or `system` | `platform-owned` or `workflow-generated` | `include` |
| Layer 3 | `bundle_definition`, `workflow_output`, `review_artifact`, `validation_artifact`, or `audit_artifact` | `bundle-owned`, `workflow-generated`, or `derived` | `include` or `conditional` |

These are expectations, not hardcoded restrictions, but deviations should
be intentional and reviewable.

### Scanner Compliance Rules

Any scanner, validator, or workflow component that performs document
discovery should obey these rules:

1. If a recognized `scan_policy` is present, honor it.
2. If `scan_policy` is `exclude`, skip the document unless the caller
   explicitly requested it.
3. If `scan_policy` is `conditional`, require an explicit inclusion rule.
4. If metadata is malformed, treat the document as non-compliant and
   report it.
5. If metadata is absent, the scanner may apply fallback behavior, but the
   document must not be assumed authoritative solely because it was found.

### Validation Rules

Future Layer 1 validation should enforce at least:

- required metadata fields are present where the standard applies
- values belong to the allowed vocabulary or an allowed extension set
- `scan_reason` is non-empty when `scan_policy` is `exclude` or
  `conditional`
- generated documents do not claim `human-authored` authority
- derived documents do not present themselves as the root authority

### Review Rules

Future review steps should treat metadata misuse as a governance defect.

Examples:

- a master plan without `scan_policy: "exclude"`
- a generated artifact claiming `human-authored`
- a review artifact marked as a system authority document
- a platform-specific standard pretending to be Layer 1 governance

### Implementation Rule

Layer 1 should define the metadata contract, but it should not define the
scanner implementation. The actual parser, discovery logic, and fallback
behavior belong in Layer 2 platform design and code.

### Document Authority Matrix

Layer 1 should define a clear authority matrix so every document class has
an expected ownership model.

This prevents two common failures:

- generated artifacts pretending to be constitutional documents
- reference blueprints being mistaken for operational system outputs

| Layer | Document Class | Typical `doc_type` | Allowed `authority` | Notes |
|---|---|---|---|---|
| Layer 1 | Master plan / blueprint | `masterplan` | `human-authored` | Reference-only architecture source. Normally excluded from operational scans. |
| Layer 1 | Governance standard | `system` | `human-authored`, `workflow-generated` | Must represent ecosystem-wide governance only. |
| Layer 1 | Review / audit evidence | `review_artifact`, `audit_artifact`, `validation_artifact` | `workflow-generated`, `derived` | Evidence is not constitutional authority. |
| Layer 2 | Platform constitution | `platform_standard`, `system` | `platform-owned`, `human-authored`, `workflow-generated` | Owns platform-specific operating standards. |
| Layer 2 | Platform-generated evidence | `review_artifact`, `validation_artifact`, `audit_artifact` | `workflow-generated`, `derived` | Supports Layer 2 compliance and evolution. |
| Layer 3 | Bundle definition | `bundle_definition` | `bundle-owned`, `human-authored`, `workflow-generated` | Concrete bundle contract within a Layer 2 context. |
| Layer 3 | Workflow output | `workflow_output` | `workflow-generated`, `bundle-owned`, `derived` | May be canonical for the bundle output, but not for higher-layer governance. |
| Layer 3 | Review / validation / audit outputs | `review_artifact`, `validation_artifact`, `audit_artifact` | `workflow-generated`, `derived` | Operational evidence only. |

### Authority Interpretation Rules

The matrix should be interpreted with these rules:

- `human-authored` means humans maintain the authoritative source text
- `workflow-generated` means the workflow is the authoritative producer
  for that document
- `platform-owned` means the owning Layer 2 core governs the content
- `bundle-owned` means the owning Layer 3 bundle governs the content
- `derived` means the artifact was produced from another source and should
  not be treated as the origin of truth

### Authority Constraints By Layer

Layer 1 constraints:

- a Layer 1 `masterplan` should normally be `human-authored`
- a Layer 1 governance standard may be `workflow-generated` only if the
  generating workflow itself is governed by an accepted Layer 1 model
- Layer 1 evidence artifacts must never be mistaken for permanent
  constitutional documents

Layer 2 constraints:

- Layer 2 platform standards must clearly identify the owning platform
- Layer 2 must not label platform-specific operating rules as generic
  ecosystem authority

Layer 3 constraints:

- Layer 3 outputs may be authoritative for the bundle that owns them
- Layer 3 outputs must not claim Layer 1 or Layer 2 constitutional
  authority unless explicitly promoted through a higher-layer process

### Promotion Rule

Documents do not become higher-layer authority merely because they are
useful, widely reused, or frequently referenced.

Promotion to a higher layer requires:

1. explicit review against the target layer scope
2. reclassification under the target layer metadata rules
3. acceptance by the owning authority of that higher layer

For example:

- a Layer 3 bundle guide does not become a Layer 2 platform standard by
  convention alone
- a Layer 2 platform standard does not become Layer 1 governance because
  multiple platforms copied it

### Conflict Rule

If document authority conflicts with document content, content scope wins
for classification and the document should be flagged.

Examples:

- a document marked `masterplan` that contains operational runbook detail
  is misclassified
- a document marked `workflow_output` that tries to define ecosystem
  governance is misclassified
- a document marked `system` but limited to one platform probably belongs
  in Layer 2, not Layer 1

## Content Boundary Matrix

Layer 1 should define an explicit allowed-versus-forbidden content matrix
for all three layers. This is necessary because boundary drift usually
happens through content, not just metadata.

The matrix below should be used as the basis for future review prompts,
audit prompts, and deterministic validators.

| Content Type | Layer 1 | Layer 2 | Layer 3 |
|---|---|---|---|
| Ecosystem purpose and constitutional scope | Allowed | Reference only | Reference only |
| Definition of Layer 1, Layer 2, and Layer 3 | Allowed | Reference only | Reference only |
| Cross-ecosystem ownership rules | Allowed | Must not redefine | Must not redefine |
| Generic document authority rules | Allowed | May extend | Must inherit |
| Generic metadata classification rules | Allowed | May extend | Must inherit |
| Generic bundle taxonomy | Allowed | May specialize | Applies only |
| Platform/runtime architecture | Forbidden | Allowed | Reference only |
| Platform installation/publish/deploy model | Forbidden | Allowed | Reference only unless bundle-specific usage constraints apply |
| Platform metadata contracts | Forbidden | Allowed | Reference and comply |
| Shared runtime services | Forbidden | Allowed | Reference and consume |
| Concrete workflow definition | Forbidden | Forbidden | Allowed |
| Prompts and context extensions | Forbidden | Template/reference only | Allowed |
| Concrete artifact path contracts | Forbidden | Pattern only | Allowed |
| Concrete output file inventory | Forbidden | Pattern or template only | Allowed |
| Bundle-local review criteria | Forbidden | Standardize pattern only | Allowed |
| Bundle-local validators | Forbidden | Shared framework only | Allowed |
| Job history and execution evidence | Forbidden | Forbidden except platform-level evidence | Allowed |
| Review/audit/validation evidence | Evidence only, not constitutional | Evidence only | Allowed |
| Platform-specific examples | Forbidden | Allowed | Allowed |
| Bundle-specific examples | Forbidden | Template or reference only | Allowed |
| Repository-specific inventory | Forbidden | Allowed when repository is the Layer 2 subject | Allowed when owned by the bundle |

### Layer 1 Allowed Content

Layer 1 should contain only content that remains valid across multiple
Layer 2 cores.

Allowed Layer 1 content includes:

- governance principles
- ownership boundaries
- authority and promotion rules
- metadata rules
- conceptual bundle taxonomy
- review and validation obligations at principle level
- document lifecycle and change control at principle level

If a statement becomes false when switching from one platform to another,
it probably does not belong in Layer 1.

### Layer 1 Forbidden Content

Layer 1 must reject:

- runtime internals
- execution flows
- bootstrap copy mechanisms
- install, publish, deploy, or registry procedures
- path resolution logic
- platform-specific validation rules
- concrete workflow IDs and bundle inventories
- repository-local examples unless the example is purely schematic and
  clearly non-authoritative

### Layer 2 Allowed Content

Layer 2 should contain the platform or domain operating model required for
Layer 3 bundles to function coherently.

Allowed Layer 2 content includes:

- runtime architecture
- platform conventions
- platform metadata standards
- shared service contracts
- installation and deployment standards for that platform
- platform-specific validation contracts
- platform-specific authoring standards for Layer 3 bundles

### Layer 2 Forbidden Content

Layer 2 must reject:

- attempts to redefine Layer 1 governance
- one-off job artifacts being presented as platform standards
- bundle-specific outputs being misrepresented as platform-wide rules
- content that only makes sense for one bundle unless the document is a
  starter template or reference example

### Layer 3 Allowed Content

Layer 3 should contain concrete operational and delivery assets.

Allowed Layer 3 content includes:

- workflow definitions
- prompts
- context extensions
- validators
- bundle-local governance files
- artifact mappings
- generated outputs
- review, audit, and validation evidence

### Layer 3 Forbidden Content

Layer 3 must reject:

- ecosystem-wide constitutional claims
- platform-wide standards that belong in Layer 2
- hidden dependency on undocumented Layer 2 behavior
- generated content that pretends to change higher-layer governance by
  itself

### Boundary Decision Heuristics

When content classification is unclear, apply these tests:

1. Cross-platform test:
   If the statement should remain true for every adopted platform, it may
   belong in Layer 1.
2. Platform test:
   If the statement is true for one platform core but not necessarily
   others, it belongs in Layer 2.
3. Bundle test:
   If the statement is true only for one concrete workflow bundle or one
   generated output family, it belongs in Layer 3.
4. Operationality test:
   If the statement explains how something executes, installs, resolves,
   validates, or publishes, it is not Layer 1.
5. Promotion test:
   If the content originated as a lower-layer artifact, it stays in that
   layer until it is explicitly promoted.

### Review Enforcement Guidance

Future review steps should ask:

- Does this document contain content that would stop being true if the
  platform changed?
- Does this document define an implementation instead of a governance
  boundary?
- Does this document claim authority above the layer its content supports?
- Does this document mix constitutional rules with operational examples?

If the answer is yes, the review should reject or reclassify the content.

### Validator Enforcement Guidance

Future validators should support at least these checks:

- Layer 1 docs must not contain forbidden operational keywords or sections
  that imply runtime procedure ownership
- Layer 2 docs must identify the platform/domain they govern
- Layer 3 docs must identify the owning bundle or workflow context
- evidence artifacts must not be mistaken for permanent standards
- metadata classification must be consistent with actual content scope

### Layer 1 Audience

Primary audiences:

- ecosystem owners
- architecture owners
- platform-core authors
- workflow framework designers

Secondary audiences:

- workflow bundle authors
- reviewers and auditors

### Layer 1 Success Criteria

Layer 1 is successful when:

- it is reusable across very different Layer 2 cores
- it stays stable even when implementation changes underneath
- it is precise enough to reject out-of-scope content
- it is small enough to remain governable

### Layer 1 Failure Modes

Layer 1 is wrong when it starts describing:

- how code works
- how a runtime should discover files
- how a registry should be queried
- how a repository should be bootstrapped
- how a specific workflow should validate outputs

Those are signs that Layer 2 or Layer 3 content has leaked upward.

## Layer 2

### Role

Layer 2 is the platform or domain constitution.

It translates Layer 1 governance into an operating model for one specific
platform, runtime family, or solution domain.

### Objective

Layer 2 exists to answer these questions:

- How does this specific platform/domain apply Layer 1?
- What core capabilities does this platform provide?
- What standard bundle types exist in this platform?
- What shared runtime or framework services are available?
- What conventions must Layer 3 bundles follow in this platform?

### Valid Layer 2 Examples

Examples of valid Layer 2 cores:

- AI-driven SDLC core
- ComfyUI core
- n8n core
- agent-runner-v2 core

Each of these may have very different runtime behavior, packaging shape,
validation logic, and operating constraints. That difference belongs here,
not in Layer 1.

### What Layer 2 Owns

Layer 2 owns the platform-specific or domain-specific core model:

- runtime architecture for that platform
- bundle operating conventions for that platform
- repository or platform structure conventions
- shared services used by Layer 3 bundles
- platform-specific validation model
- platform-specific installation or deployment model
- platform-specific metadata contracts
- standard interfaces that Layer 3 bundles must comply with
- canonical directory conventions for that platform

### What Layer 2 Must Not Own

Layer 2 must not redefine:

- the meaning of Layer 1
- cross-ecosystem governance authority
- cross-ecosystem ownership rules
- generic architectural layer definitions

Layer 2 also must not collapse into Layer 3 by becoming a concrete bundle
inventory or a job-output dump.

### Layer 2 Deliverables

A Layer 2 core should typically define:

- platform overview
- operating model
- shared runtime or service contracts
- bundle authoring contract
- metadata and validation contract
- platform-specific review and release standards

Layer 2 may also define templates, starter bundles, and reference
implementations for its Layer 3 ecosystem.

### Layer 2 Audience

Primary audiences:

- platform maintainers
- runtime maintainers
- framework contributors
- bundle authors targeting that platform

### Layer 2 Success Criteria

Layer 2 is successful when:

- it cleanly applies Layer 1 without contradicting it
- it is concrete enough for Layer 3 authors to build against
- platform details live here instead of leaking into Layer 1
- multiple Layer 3 bundles can share the same Layer 2 core

### Layer 2 Failure Modes

Layer 2 is wrong when:

- it redefines ecosystem-wide governance
- it hardcodes one workflow bundle as the entire platform
- it mixes platform standards with job-history artifacts
- it becomes so generic that Layer 3 authors still need to guess the
  platform contract

## Layer 3

### Role

Layer 3 is the implementation and delivery layer.

This is where concrete workflow bundles, domain automations, generators,
analysis jobs, bootstrap packs, or solution-specific outputs live.

### Objective

Layer 3 exists to answer these questions:

- What does this workflow bundle do?
- What inputs does it require?
- What outputs does it produce?
- What review and validation steps does it run?
- What artifact paths, schemas, prompts, and context rules does it own?

### What Layer 3 Owns

Layer 3 owns concrete execution assets:

- workflow definitions
- prompts
- context extensions
- bundle-local governance files
- concrete artifact contracts
- generated documents and reports
- domain-specific validators
- job-level review and audit outputs

### What Layer 3 Must Not Own

Layer 3 must not redefine:

- ecosystem-wide governance
- the architectural meaning of the three layers
- the platform constitution defined by its parent Layer 2

Layer 3 can extend and specialize. It cannot rewrite higher-layer
authority.

### Layer 3 Deliverables

Examples of Layer 3 outputs:

- generated documentation
- analysis findings
- implementation plans
- scaffolds
- code changes
- release notes
- workflow review and audit artifacts

These outputs are expected to vary heavily by bundle and by domain.

### Layer 3 Audience

Primary audiences:

- end users of a workflow bundle
- operators running a bundle
- maintainers of a specific bundle
- reviewers of generated outputs

### Layer 3 Success Criteria

Layer 3 is successful when:

- a bundle can be understood and run within its Layer 2 contract
- ownership of generated outputs is explicit
- review and validation are specific to the bundle objective
- generated outputs do not claim governance authority they do not own

### Layer 3 Failure Modes

Layer 3 is wrong when:

- it invents platform-wide rules
- it mutates higher-layer governance through generated outputs
- it produces artifacts whose ownership is ambiguous
- it relies on undocumented Layer 2 behavior

## Relationship Between Layers

### Inheritance Model

The layers relate as follows:

- Layer 1 governs Layer 2 and Layer 3 conceptually
- Layer 2 operationalizes Layer 1 for one platform or domain
- Layer 3 implements work within one Layer 2 context

Layer 3 should be understandable only after its parent Layer 2 is known.
Layer 2 should be governable only because Layer 1 defines the authority
model.

### Dependency Direction

Allowed direction:

- Layer 3 depends on Layer 2
- Layer 2 depends on Layer 1

Forbidden direction:

- Layer 1 depending on Layer 2 specifics
- Layer 1 depending on Layer 3 specifics
- Layer 2 depending on one Layer 3 bundle for its own definition

### Change Direction

Expected change frequency:

- Layer 1 changes rarely
- Layer 2 changes occasionally
- Layer 3 changes frequently

This is intentional. Governance should be more stable than platform
conventions, and platform conventions should be more stable than concrete
bundle outputs.

## Governance and Ownership Matrix

| Concern | Layer 1 | Layer 2 | Layer 3 |
|---|---|---|---|
| Ecosystem governance model | Owns | References | References |
| Platform/runtime operating model | Must not own | Owns | References |
| Concrete workflow bundle behavior | Must not own | Constrains | Owns |
| Generated job outputs | Must not own | May classify | Owns |
| Review obligations | Owns at principle level | Owns platform standard | Owns bundle execution |
| Validation obligations | Owns at principle level | Owns platform contract | Owns concrete checks |
| Artifact path contracts | Must not own | May standardize pattern | Owns concrete mapping |
| Runtime implementation | Must not own | Owns | References or extends |
| Bundle taxonomy | Owns generic model | Specializes for platform | Applies |

## Workflow Design Implications

This master plan implies the next workflow design should follow these
rules:

### New Layer 1 Workflow Scope

The new Layer 1 workflow must generate only governance content. It must
be incapable, by prompt and validation design, of drifting into runtime or
platform implementation details.

### Layer 1 Review Role

The review step for Layer 1 must reject any content that:

- defines runtime operations
- names installer or publish mechanics
- describes registry behavior
- documents platform-specific implementation
- behaves like a Layer 2 operating manual

The current problem is not only generation quality. It is also that the
review role has not been explicitly designed to enforce the layer
boundary. That must change in the new workflow.

### Layer 2 Workflow Scope

Future Layer 2 workflows should generate platform constitutions, not
bundle outputs. A Layer 2 workflow for `agent-runner-v2` may define the
runtime model, metadata contracts, and bundle authoring rules for that
platform.

### Layer 3 Workflow Scope

Future Layer 3 workflows should generate or maintain concrete bundles and
their outputs within a declared Layer 2 context.

## Promotion Model

Promotion is the controlled process of moving proven lower-layer knowledge
into a higher-layer standard.

Promotion does not mean "this artifact is good." It means the reusable
part of the artifact has been reviewed, re-scoped, and accepted as
higher-layer authority.

### Why Promotion Exists

The promotion model exists to prevent two governance failures:

- useful lower-layer artifacts being treated as higher-layer truth without
  review
- higher layers being polluted by bundle-specific or platform-specific
  detail

Promotion allows the ecosystem to learn from real execution without
destroying layer boundaries.

### Core Promotion Principle

Promote the reusable rule, contract, pattern, or interface.

Do not promote:

- raw job history
- one-off generated outputs
- bundle-specific examples
- platform-specific mechanics into Layer 1
- implementation detail when only the governing principle is reusable

### Promotion Path

The normal maturation path is:

1. Layer 3 proves something works in practice.
2. Layer 2 extracts and standardizes the platform-reusable portion.
3. Layer 1 abstracts only the cross-platform governance principle when
   appropriate.

This means:

- Layer 3 is the proving ground
- Layer 2 is the standardization layer
- Layer 1 is the constitutional layer

### Layer 3 to Layer 2 Promotion

This is the most common promotion path.

A Layer 3 artifact or bundle pattern may be promoted into Layer 2 when:

- it has been reused successfully across multiple bundles in the same
  platform/domain
- it expresses a platform-level capability, contract, or authoring
  standard
- the reusable part can be separated from bundle-specific execution detail

Typical candidates:

- bundle authoring patterns
- validation contracts
- review loops
- shared artifact conventions
- standard interfaces
- reusable bundle packaging rules for one platform

Typical non-candidates:

- one workflow's concrete prompt set
- one bundle's output inventory
- one bundle's job-history evidence
- a one-off workaround

### Layer 2 to Layer 1 Promotion

This should be rare.

A Layer 2 standard may be promoted into Layer 1 only when:

- the principle is valid across multiple distinct Layer 2 cores
- the platform-specific implementation detail can be removed
- what remains is truly governance, ownership, classification, or
  authority logic

Typical candidates:

- cross-platform metadata rules
- cross-platform authority rules
- generic bundle taxonomy concepts
- governance lifecycle requirements

Typical non-candidates:

- runtime service contracts
- installation procedures
- deployment workflows
- platform-specific validator logic
- repository operating structure tied to one platform

### Promotion Extraction Rule

Promotion should usually create a new higher-layer document or section
rather than copying the lower-layer artifact verbatim.

The extraction rule is:

- keep examples, evidence, and implementation detail in the source layer
- move only the reusable abstraction upward
- reword the promoted content to match the target layer's scope

This avoids carrying Layer 3 and Layer 2 noise into higher-layer
governance.

### Promotion Approval Gates

Every promotion should pass these gates:

1. Scope gate:
   Does the content actually belong in the target layer?
2. Reuse gate:
   Has the content shown repeat value beyond its source artifact?
3. Abstraction gate:
   Can the reusable principle be separated from local detail?
4. Ownership gate:
   Is the receiving layer willing to own and maintain it?
5. Metadata gate:
   Will the promoted artifact be reclassified correctly under the target
   layer's metadata rules?

If any gate fails, the content should remain in its current layer.

### Promotion Outcomes

Valid promotion outcomes include:

- a Layer 3 pattern becomes a Layer 2 platform standard
- a Layer 3 bundle interface becomes a Layer 2 authoring contract
- a Layer 2 metadata rule becomes a Layer 1 governance standard
- a Layer 2 review principle becomes a Layer 1 governance obligation

Invalid promotion outcomes include:

- a Layer 3 generated report being treated as a Layer 2 constitution
- a Layer 2 runtime mechanism being copied into Layer 1 governance
- a widely reused workaround being promoted without scope cleanup

### Promotion Metadata Changes

Promotion requires explicit reclassification.

At minimum, promotion should review and update:

- `doc_type`
- `authority`
- `scan_policy`
- `scan_reason`
- owning layer
- owning authority

A document does not become higher-layer authority simply because it was
moved to another folder.

### Promotion Review Questions

Future promotion reviews should ask:

- What exact reusable concept is being promoted?
- What source-layer detail must be stripped away?
- Why does the target layer need to own this?
- Would the promoted content still be valid if another bundle or platform
  used it?
- Is this a constitutional rule, a platform contract, or a bundle
  behavior?

### Demotion and Reversal

Promotion is not irreversible.

If promoted content is later found to be too specific for its assigned
layer, it should be:

1. reclassified to the correct lower layer, or
2. split into a higher-layer principle plus lower-layer implementation

This is important because premature promotion is one of the main ways
governance becomes bloated.

### Practical Interpretation

In practical terms:

- Layer 3 may contain POCs, modules, experiments, or powerful bundle-local
  patterns
- Layer 2 turns proven platform-reusable ideas into a proper core/system
- Layer 1 captures only the cross-platform governance principles that
  remain after operational detail is removed

## Recommended Next Design Sequence

The redesign sequence should be:

1. Finalize this master plan.
2. Define the target Layer 1 document set based on this model.
3. Define acceptance and rejection criteria for Layer 1 content.
4. Create a brand-new Layer 1 workflow from those criteria.
5. Define one or more Layer 2 cores against the finalized Layer 1.
6. Build Layer 3 bundles under a chosen Layer 2.

## Lifecycle Model

Each layer needs an explicit lifecycle model so governance does not stop at
document structure. The lifecycle defines how content is created, reviewed,
approved, changed, deprecated, and retired.

The lifecycle model should become the basis for future workflow design.

### Common Lifecycle States

All layers may use the same high-level state model, even though the review
and approval gates differ by layer:

1. Draft
2. In review
3. Approved
4. Active
5. Revised
6. Deprecated
7. Retired

Suggested meanings:

| State | Meaning |
|---|---|
| `Draft` | New or changed content under preparation. Not authoritative yet. |
| `In review` | Content is being checked against the owning layer rules. |
| `Approved` | The owning authority accepted the content for use. |
| `Active` | The content is the current effective version. |
| `Revised` | A new accepted version supersedes an older one. |
| `Deprecated` | The content may still exist but should not be used for new work. |
| `Retired` | The content is no longer valid for operational use. |

### Layer 1 Lifecycle

Layer 1 changes should be rare and deliberate.

#### Layer 1 Creation

A Layer 1 artifact may be created when:

- a new ecosystem governance concept is required
- a governance gap is found that affects multiple Layer 2 cores
- a repeated higher-layer conflict requires constitutional clarification

#### Layer 1 Review

Layer 1 review must check:

- cross-platform validity
- governance-only scope
- ownership clarity
- metadata correctness
- non-duplication with Layer 2 or Layer 3 standards

#### Layer 1 Approval

Layer 1 approval should require acceptance by the ecosystem governance
owner or equivalent constitutional authority.

Layer 1 content must not become active merely because a workflow generated
it. Workflow generation is a production mechanism, not final authority by
itself.

#### Layer 1 Revision

A Layer 1 revision should happen only when:

- a governance rule is incorrect
- a governance rule is incomplete
- multiple Layer 2 cores reveal the same missing principle
- metadata or authority rules need constitutional correction

#### Layer 1 Deprecation and Retirement

Layer 1 content may be deprecated when:

- it is superseded by a clearer governance standard
- it is architecturally incorrect
- the ecosystem no longer uses the concept it governs

Retirement should preserve traceability, including:

- what replaced it
- when it stopped being active
- why it was retired

### Layer 2 Lifecycle

Layer 2 changes are expected but should remain stable enough for multiple
Layer 3 bundles to depend on them.

#### Layer 2 Creation

A Layer 2 core may be created when:

- a new platform or domain adopts the ecosystem
- a platform needs its own operating constitution
- multiple Layer 3 bundles require a shared platform contract

#### Layer 2 Review

Layer 2 review must check:

- alignment with Layer 1
- platform specificity without overreach into Layer 1
- usefulness for multiple Layer 3 bundles
- clarity of shared platform contracts
- correct distinction between platform standards and bundle outputs

#### Layer 2 Approval

Layer 2 approval should require acceptance by the owning platform/core
maintainer authority.

#### Layer 2 Revision

Layer 2 may be revised when:

- the platform runtime changes
- bundle authoring contracts change
- platform metadata contracts change
- repeated Layer 3 patterns justify standardization

#### Layer 2 Deprecation and Retirement

Layer 2 content may be deprecated when:

- the platform contract is being replaced
- the platform/domain is no longer supported
- the standard has been split into more precise platform standards

Retirement must preserve migration guidance for dependent Layer 3 bundles
where applicable.

### Layer 3 Lifecycle

Layer 3 is expected to change the most frequently.

#### Layer 3 Creation

A Layer 3 artifact or bundle may be created when:

- a new workflow objective exists
- a new POC or module is needed
- a platform capability needs a concrete executable bundle
- an output-producing workflow is introduced

#### Layer 3 Review

Layer 3 review must check:

- alignment with its parent Layer 2 contract
- clear bundle ownership
- explicit artifact contracts
- fit for purpose against the workflow objective
- correct classification of outputs and evidence

#### Layer 3 Approval

Layer 3 approval should require acceptance by the owning bundle maintainer
or delegated operational authority.

#### Layer 3 Revision

Layer 3 may be revised when:

- prompts change
- output contracts change
- validators change
- execution steps change
- bundle-local governance changes

#### Layer 3 Deprecation and Retirement

Layer 3 content may be deprecated when:

- a bundle is superseded
- a bundle is experimental and no longer recommended
- a workflow objective is obsolete
- the bundle is absorbed into a new Layer 2 standard or a replacement
  bundle

Retirement should preserve historical traceability for prior outputs where
needed.

### Lifecycle Responsibilities Matrix

| Lifecycle Concern | Layer 1 | Layer 2 | Layer 3 |
|---|---|---|---|
| Creation trigger | Cross-ecosystem governance need | Platform/domain need | Bundle/workflow need |
| Primary reviewer | Governance authority | Platform authority | Bundle authority |
| Approval authority | Ecosystem owner | Platform/core owner | Bundle maintainer/operator |
| Change frequency | Rare | Occasional | Frequent |
| Deprecation basis | Constitutional replacement/correction | Platform replacement/change | Bundle replacement/obsolescence |
| Retirement traceability | Required | Required | Recommended, often required for outputs |

### Publication Rule

Publication should be treated separately from approval.

The correct sequence is:

1. create or revise
2. review
3. approve
4. publish or activate

This matters because a generated artifact can exist before it is accepted
as active authority.

### Effective Version Rule

At any given time, each governed standard should have a clear effective
version.

Older versions may remain stored for traceability, but scanners and
workflows should know which version is active.

This rule is especially important for:

- Layer 1 governance standards
- Layer 2 platform constitutions
- Layer 3 bundle definitions that own active output contracts

### Change Classification Rule

Changes should be classified by impact before approval:

- editorial change
- clarification
- behavioral change
- governance change
- breaking change

Suggested interpretation:

| Change Class | Meaning |
|---|---|
| `editorial change` | Wording only. No intended meaning change. |
| `clarification` | Meaning made clearer without changing expected behavior. |
| `behavioral change` | Expected operational behavior changes. Usually Layer 2 or Layer 3. |
| `governance change` | Ownership, authority, or governing rules change. Often Layer 1 or Layer 2. |
| `breaking change` | Existing dependent bundles or standards may need migration. |

### Promotion and Lifecycle Interaction

Promotion is not a shortcut around lifecycle controls.

When content is promoted:

- the source artifact keeps its own lifecycle history
- the promoted artifact enters the target layer as a new draft or revision
- the target layer must review and approve it under its own rules

This ensures promotion does not bypass governance.

### Deprecation Signaling

Deprecated or retired content should be explicitly marked in metadata or
header status fields where the platform supports it.

Future Layer 2 implementations may define concrete fields such as:

- `status`
- `effective_version`
- `supersedes`
- `superseded_by`
- `deprecated_at`
- `retired_at`

Those implementation details belong to Layer 2, but the need for explicit
lifecycle signaling is a Layer 1 governance concern.

## Workflow Operating Model

The three-layer architecture should drive workflow design directly.

This means a workflow is not only judged by whether it produces valid
files. It is also judged by whether it stays inside the authority,
content, and lifecycle boundaries of its intended layer.

### Workflow Governance Principle

Every workflow should declare:

- which layer it belongs to
- what authority it is allowed to create or modify
- what permanent artifacts it may produce
- what temporary evidence artifacts it may produce
- what it must reject as out of scope

If a workflow cannot state these clearly, it is not yet governable.

### Workflow Classes By Layer

The workflow model should distinguish three broad classes:

| Workflow Class | Primary Layer | Purpose |
|---|---|---|
| Governance workflow | Layer 1 | Produce or maintain ecosystem governance standards. |
| Platform-core workflow | Layer 2 | Produce or maintain platform/domain constitutions and shared contracts. |
| Bundle workflow | Layer 3 | Produce or maintain concrete bundles and operational outputs. |

This classification is about governing purpose, not implementation
complexity.

### Permanent Versus Temporary Artifacts

Every workflow should distinguish between:

- permanent artifacts
- temporary evidence artifacts

Permanent artifacts are authoritative outputs intended to remain active
after workflow completion.

Temporary evidence artifacts exist to support trust in the workflow run,
such as:

- review artifacts
- validation artifacts
- audit artifacts
- trace or reasoning summaries when retained by policy

Temporary evidence must not be mistaken for the permanent standard itself.

### Layer 1 Workflow Operating Rules

A Layer 1 workflow should be intentionally narrow.

Its purpose is to produce governance standards only.

#### Layer 1 Workflow Allowed Outputs

A Layer 1 workflow may produce:

- permanent Layer 1 governance documents
- temporary review artifacts
- temporary validation artifacts
- temporary audit artifacts

It must not produce:

- runtime operating manuals
- repository-local execution guides
- platform-specific implementation standards
- bundle-local prompts or artifact contracts masquerading as governance

#### Layer 1 Workflow Review Role

The review role in a Layer 1 workflow must act as a scope gate, not just a
quality gate.

It must reject outputs that:

- define runtime operations
- specify installation, publish, deploy, or registry procedures
- document platform-specific implementation
- name concrete workflow bundle inventories unless the purpose is purely
  illustrative and explicitly non-authoritative
- behave like a Layer 2 or Layer 3 document

The review step should not ask only "is this well written?" It must ask
"does this belong in Layer 1 at all?"

#### Layer 1 Workflow Validation Role

The validation role in a Layer 1 workflow should enforce:

- required metadata
- layer-appropriate content boundaries
- allowed authority values
- required sections for the target governance set
- absence of forbidden operational detail
- separation of permanent governance artifacts from temporary evidence

#### Layer 1 Workflow Audit Role

The audit role in a Layer 1 workflow should verify:

- the accepted document still reflects Layer 1 scope after refinement
- no lower-layer implementation detail was normalized into governance
- metadata and authority remain consistent with actual content
- all promoted concepts were abstracted correctly rather than copied
  upward verbatim

#### Layer 1 Workflow Refinement Rule

Refinement must not become an uncontrolled loop that keeps polishing the
wrong scope.

If the problem is layer mismatch rather than wording quality, refinement
should:

1. reject the artifact,
2. identify the correct owning layer, and
3. require reclassification or redesign.

This rule matters because iterative refinement can otherwise make a wrong
document look more convincing without making it more correct.

### Layer 2 Workflow Operating Rules

Layer 2 workflows should operationalize one platform or domain without
pretending to define cross-ecosystem governance.

#### Layer 2 Workflow Allowed Outputs

A Layer 2 workflow may produce:

- platform constitutions
- shared runtime or service contracts
- platform metadata standards
- platform authoring standards
- temporary review, validation, and audit artifacts

It should not produce:

- Layer 1 constitutional rules
- bundle-specific outputs presented as platform standards

#### Layer 2 Workflow Review Role

The review role in a Layer 2 workflow must reject outputs that:

- redefine Layer 1
- are too bundle-specific to serve as platform standards
- mix platform constitutions with job-run evidence
- lack clear platform ownership

#### Layer 2 Workflow Validation Role

The validation role in a Layer 2 workflow should enforce:

- alignment with Layer 1 metadata and authority rules
- platform identification
- consistency of shared contracts
- separation of platform standards from bundle outputs

### Layer 3 Workflow Operating Rules

Layer 3 workflows are where execution-specific variation is expected.

#### Layer 3 Workflow Allowed Outputs

A Layer 3 workflow may produce:

- bundle definitions
- prompts
- validators
- generated docs and reports
- implementation plans
- code changes
- review, validation, and audit artifacts

#### Layer 3 Workflow Review Role

The review role in a Layer 3 workflow must reject outputs that:

- claim higher-layer constitutional authority
- rely on undefined Layer 2 behavior
- leave artifact ownership ambiguous
- produce outputs outside the bundle's declared objective

#### Layer 3 Workflow Validation Role

The validation role in a Layer 3 workflow should enforce:

- alignment with parent Layer 2 contract
- artifact completeness
- metadata correctness
- output-path or artifact-contract consistency
- distinction between permanent outputs and temporary evidence

### Workflow Artifact Classification Rule

Every produced artifact should be classifiable by answering:

1. Is it permanent or temporary?
2. What layer owns it?
3. What authority value does it carry?
4. Should scanners include or exclude it by default?
5. Is it a governing standard, a platform standard, a bundle definition,
   or evidence?

If the workflow cannot answer these questions, artifact tracking will
degrade over time.

### Workflow Tracking Rule

Workflow tracking should record enough metadata to understand:

- which workflow produced the artifact
- which layer the workflow belongs to
- whether the artifact is permanent or temporary
- the declared authority of the artifact
- the artifact's lifecycle status when relevant

This is important because job history alone is not enough to infer
governance status correctly.

### Workflow Rejection Rule

A workflow should fail or reject when:

- the intended layer is unclear
- produced artifacts cross layer boundaries without explicit promotion
- metadata classification conflicts with content scope
- a temporary evidence artifact is about to be treated as permanent
  authority

Silently accepting misclassified artifacts creates governance debt.

### Workflow Design Checklist

Future workflow design should explicitly answer:

1. Which layer does this workflow belong to?
2. What permanent artifacts can it create?
3. What temporary artifacts can it create?
4. What content is forbidden for this workflow?
5. What must review reject?
6. What must validation enforce?
7. What metadata must every output carry?
8. What promotion path exists if the output becomes broadly reusable?

### Workflow Redesign Implication For Layer 1

The next Layer 1 redesign should begin from this workflow operating model,
not from the legacy Layer 1 package structure.

That means:

- start from Layer 1 scope and rejection rules
- define the target permanent governance set
- define temporary evidence artifacts separately
- design review to enforce boundary correctness first
- design validation to enforce metadata and scope deterministically
- only then choose prompts, steps, and file layout

## Proposed Initial Layer 1 Document Set

A reasonable starting set for the new Layer 1 workflow is:

- `README.md`
- `LAYER_MODEL.md`
- `GOVERNANCE_LIFECYCLE.md`
- `BUNDLE_TAXONOMY.md`
- `DOCUMENT_AUTHORITY.md`
- `METADATA_STANDARD.md`

This is only a proposal, but it is closer to the intended Layer 1 scope
than the current runtime-heavy document set.

## Non-Goals

This master plan does not yet define:

- the exact file structure of a new Layer 1 workflow bundle
- the exact prompt wording
- the exact validator implementation
- the exact Layer 2 file trees
- the exact migration plan from the old generated docs

Those should be designed only after this architecture is accepted.

## Decision Rule

When in doubt, classify content by the narrowest layer that can own it
correctly:

- if it governs every platform, it is Layer 1
- if it governs one platform or domain, it is Layer 2
- if it governs one concrete workflow bundle or its outputs, it is Layer 3

If a statement feels operational, executable, platform-specific, or
bundle-specific, it should be pushed downward out of Layer 1.
