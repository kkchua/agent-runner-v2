---
doc_type: "review_artifact"
authority: "workflow-generated"
scan_policy: "exclude"
scan_reason: "temporary platform core review artifact for deterministic validation gate"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02AR-20260721-2eaba4b3"
---

# Platform Core Review

## Decision

APPROVED

The staged Layer 2 platform core constitution set is acceptable for deterministic validation. All six required permanent documents are present, correctly classified as platform_standard, and comply with Layer 1 governance inheritance. No rejection findings were identified.

## Layer Boundary Findings

### Layer 1 Governance Boundary

No Layer 1 governance redefinition or contradiction was found.

- README.md line 49: "This platform constitution inherits from Layer 1 governance without redefining it." The five Layer 1 documents are referenced by name and treated as read-only inherited authority.
- README.md line 61: "The Layer 1 governance documents are installed at the global runtime root (GOVERNANCE_RUNTIME_ROOT) and are treated as read-only inherited authority." This correctly delegates to the runtime root placeholder without embedding repo-local L1 paths.
- METADATA_CONTRACT.md lines 22-31: Reproduces the Layer 1 doc_type vocabulary with faithful meanings. Platform-specific values (platform_standard, bundle_definition) extend the vocabulary without redefining Layer 1 base values. The meaning of "platform_standard" in METADATA_CONTRACT.md line 37 ("A Layer 2 operating standard for agent-runner-v2") is a specialization of the Layer 1 meaning ("A Layer 2 operating standard for a specific platform or domain") and does not contradict it.
- METADATA_CONTRACT.md lines 69-74: The authority/managed_by orthogonality statement is consistent with Layer 1 field semantics. Layer 1 defines authority as "who owns the truth"; METADATA_CONTRACT.md adds managed_by as an independent mechanical producer axis. No contradiction.
- RUNTIME_MODEL.md, BUNDLE_AUTHORING_CONTRACT.md, SHARED_SERVICES.md, VALIDATION_CONTRACT.md: None contain Layer 1 governance content. All remain within Layer 2 platform scope.

### Layer 3 Drift Boundary

No Layer 3 bundle-specific content presented as platform-wide rules was found.

- BUNDLE_AUTHORING_CONTRACT.md: Uses generic examples (my_bundle, MY_OUTPUT_FILE, validate_my_output). No actual bundle IDs from the repository (e.g., 02_agent_runner_platform_v1, 01_governance_foundation_v1) are presented as platform standards.
- VALIDATION_CONTRACT.md: Uses generic examples (MYBUNDLE-01, my_output). The bundle validator composition section is a platform-level pattern, not a bundle-specific output.
- No document references specific Layer 3 bundle inventories, prompts, or artifact mappings as platform standards.

### Scope Classification

All six documents are correctly classified as Layer 2 platform constitution content:

- Platform index and identity (README.md)
- Runtime architecture and execution model (RUNTIME_MODEL.md)
- Bundle authoring standards (BUNDLE_AUTHORING_CONTRACT.md)
- Platform conventions and shared services (SHARED_SERVICES.md)
- Platform metadata contracts (METADATA_CONTRACT.md)
- Platform validation contracts (VALIDATION_CONTRACT.md)

## Structure Findings

### Required Document Inventory

All six permanent documents are present in the staged set:

| # | Document | Present | template_id |
|---|---|---|---|
| 1 | README.md | Yes | SYS-02-IDX |
| 2 | RUNTIME_MODEL.md | Yes | SYS-02-RM |
| 3 | BUNDLE_AUTHORING_CONTRACT.md | Yes | SYS-02-BAC |
| 4 | SHARED_SERVICES.md | Yes | SYS-02-SS |
| 5 | METADATA_CONTRACT.md | Yes | SYS-02-MC |
| 6 | VALIDATION_CONTRACT.md | Yes | SYS-02-VC |

### Document Map

README.md lines 20-31 define a document map that explicitly includes all six documents, with README.md listed as entry 1 ("this file"). The map satisfies the requirement that the document map includes the index itself so the published set inventory is six documents, not five companions plus an implicit index.

### Required Sections per Document

Each document contains the required sections defined in the platform validation contract (VALIDATION_CONTRACT.md lines 111-118):

- README.md: Document Map (line 18), Platform Identity (line 35), Layer 1 Inheritance (line 49) -- all present.
- RUNTIME_MODEL.md: Step Model (line 16), Execution Paths (line 69), Job Lifecycle (line 103), Coder Integration (line 128), Rejection And Retry (line 154) -- all present.
- BUNDLE_AUTHORING_CONTRACT.md: Required Bundle Files (line 18), workflow.toml Format (line 32), Artifact Key Conventions (line 113), Bundle Governance Requirements (line 130), Metadata Compliance (line 151) -- all present.
- SHARED_SERVICES.md: Context Extensions (line 18), Artifact Resolution (line 44), Path Contracts (line 68), Meta Sidecar (line 98), Notification Integration (line 139), Backend Sync Protocol (line 157), Action Registration (line 195) -- all present.
- METADATA_CONTRACT.md: Platform doc_type Values (line 18), Platform authority Values (line 48), Additional Frontmatter Fields (line 86), Inheritance Rules (line 102), Scan Policy Expectations (line 117) -- all present.
- VALIDATION_CONTRACT.md: ValidationPlan Pattern (line 18), Section Checks (line 90), Frontmatter Enforcement (line 121), File Existence Checks (line 151), Bundle Validator Composition (line 179) -- all present.

### Section Heading Formatting

All section headings use plain text without inline formatting (no backticks, bold, or italics in headings). Compliant with the section heading rule.

## Metadata Findings

### Frontmatter Compliance

All six permanent documents carry the required frontmatter fields:

| Field | Required | README.md | RUNTIME_MODEL.md | BUNDLE_AUTHORING_CONTRACT.md | SHARED_SERVICES.md | METADATA_CONTRACT.md | VALIDATION_CONTRACT.md |
|---|---|---|---|---|---|---|---|
| template_id | Yes | SYS-02-IDX | SYS-02-RM | SYS-02-BAC | SYS-02-SS | SYS-02-MC | SYS-02-VC |
| version | Yes | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| doc_type | Yes | platform_standard | platform_standard | platform_standard | platform_standard | platform_standard | platform_standard |
| authority | Yes | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated |
| scan_policy | Yes | include | include | include | include | include | include |
| scan_reason | Yes | present | present | present | present | present | present |
| layer | Yes | layer2 | layer2 | layer2 | layer2 | layer2 | layer2 |
| platform | Yes | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 |
| lifecycle_status | Yes | draft | draft | draft | draft | draft | draft |
| effective_version | Yes | 02AR-20260721-2eaba4b3 | 02AR-20260721-2eaba4b3 | 02AR-20260721-2eaba4b3 | 02AR-20260721-2eaba4b3 | 02AR-20260721-2eaba4b3 | 02AR-20260721-2eaba4b3 |

### Layer 1 Baseline Compliance

- All doc_type values (platform_standard) belong to the Layer 1 allowed vocabulary.
- All authority values (workflow-generated) belong to the Layer 1 allowed vocabulary. Correct for staged draft documents.
- All scan_policy values (include) are valid. Layer 2 permanent docs expect scan_policy: "include" per Layer 1 defaults.
- All scan_reason values are non-empty.
- All layer values (layer2) are valid.
- No document claims human-authored authority.

### Platform-Specific Metadata Extensions

- METADATA_CONTRACT.md correctly extends Layer 1 with platform-specific doc_type values (platform_standard, bundle_definition) without redefining Layer 1 base values.
- METADATA_CONTRACT.md correctly extends Layer 1 with platform-specific authority values (platform-owned, bundle-owned) without redefining Layer 1 base values.
- Additional fields (platform, template_id, managed_by) are consistent with the METADATA_STANDARD.md extended field definitions.

### Platform Identity

- All six documents carry platform: "agent-runner-v2".
- README.md line 14: Title is "agent-runner-v2 Platform Core Index".
- README.md lines 35-46: Platform identity section clearly defines agent-runner-v2 as a Layer 2 platform core.
- Each document title includes "agent-runner-v2" prefix.

### Lifecycle State Compliance

- All six staged documents carry lifecycle_status: "draft". This is correct for staged (not yet published) documents.
- No staged document claims lifecycle_status: "published", "active", or any post-publication state.
- RUNTIME_MODEL.md describes the publish lifecycle transition as part of the platform contract, which is appropriate for a platform constitution document. It does not misrepresent the staged documents' own lifecycle state.

### Context Inventory Artifact

- PLATFORM_CONTEXT_INVENTORY carries doc_type: "validation_artifact", authority: "workflow-generated", scan_policy: "exclude", lifecycle_status: "draft". This is consistent with temporary evidence classification.

### Forbidden Content Absence Check

- No operational bootstrap mechanics or repository setup instructions found in any permanent document.
- No evidence artifacts presented as permanent platform standards.
- No lifecycle-state misuse (no published/active values in staged docs).

## Cited Evidence

No rejection findings. All evidence supports approval:

1. README.md line 49: "This platform constitution inherits from Layer 1 governance without redefining it." -- confirms Layer 1 inheritance without redefinition.
2. README.md line 61: "The Layer 1 governance documents are installed at the global runtime root (GOVERNANCE_RUNTIME_ROOT)" -- confirms correct L1 reference pattern.
3. README.md lines 20-31: Document map includes all six documents with README.md as entry 1 -- satisfies the document map requirement.
4. METADATA_CONTRACT.md lines 69-74: "The authority and managed_by fields serve distinct purposes and are orthogonal (independent axes)" -- satisfies the orthogonality requirement.
5. METADATA_CONTRACT.md lines 42-46: Usage rules correctly classify permanent vs temporary doc_types.
6. SHARED_SERVICES.md lines 55-66: Resolution Order describes prefix dispatch, not existence-based fallback. Forbidden phrases ("check the repository working tree first", "fall back to the runtime artifact root") are absent.
7. SHARED_SERVICES.md lines 129-133: Repair fallback correctly describes _repair_or_validate_meta_json() from step_runner.py. Both primary sidecar channel and repair fallback are documented.
8. RUNTIME_MODEL.md lines 34-36: Correctly describes both the primary sidecar channel and the repair fallback. No forbidden "no disk recovery functions" or "no stdout JSON parsing" phrases.
9. VALIDATION_CONTRACT.md lines 111-118: Required sections table matches the actual section headings present in each document.
10. All frontmatter values comply with Layer 1 METADATA_STANDARD.md vocabulary.

## Next Action

The staged set is ready for deterministic validation. The validation step should verify all structural and metadata checks defined in the VALIDATION_CONTRACT.md against these six documents.
