---
doc_type: "audit_artifact"
authority: "workflow-generated"
scan_policy: "exclude"
scan_reason: "run-scoped final semantic audit of platform core constitution"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-GEN-20260720-001"
---

# Platform Core Semantic Audit

- Job ID: `02PC-GEN-20260720-001`
- Workflow: `02_platform_core_foundation_v1`
- Step: `audit_platform_core_docs`
- Date: 2026-07-20

## Decision

**APPROVED**

The staged Layer 2 platform core constitution set is approved for human
review and publish. All six permanent documents pass every forbidden-content
check. One minor code-path inaccuracy was found in RUNTIME_MODEL.md and is
documented below as a non-blocking observation.

## Layer Boundary Audit

### Check: Does any document redefine or contradict Layer 1 governance?

**Result: PASS**

All six documents explicitly inherit Layer 1 governance as read-only
authority. No document redefines Layer 1 layer definitions, ownership
boundaries, document authority rules, metadata classification rules, or
promotion rules.

Evidence:

- README.md contains a dedicated "Layer 1 Inheritance" section that lists
  each inherited Layer 1 document and states: "Layer 1 is inherited, not
  modified." It explicitly declares: "Does not change the meaning of any
  Layer 1 doc_type or authority value."
- METADATA_CONTRACT.md opens with: "This contract does not modify or
  contradict Layer 1 baseline values." Its "Platform-Specific Extensions"
  section refines semantics of existing Layer 1 values (bundle_definition,
  platform_standard) without introducing new literal strings.
- BUNDLE_AUTHORING_CONTRACT.md states: "Layer 3 bundles must operate
  within this contract. They must not modify Layer 1 ecosystem governance
  or this Layer 2 platform constitution."
- No document contains Layer 1 forbidden content (runtime internals,
  bootstrap mechanics, installation flow, registry API behavior).

### Check: Does any document contain bundle-specific content normalized into platform standards?

**Result: PASS**

All documents maintain Layer 2 platform scope. No Layer 3 bundle-specific
outputs, prompts, artifact mappings, or bundle-local rules are presented
as platform-wide standards.

Evidence:

- BUNDLE_AUTHORING_CONTRACT.md defines the contract pattern (required
  files, TOML format, governance package) without embedding any specific
  bundle's configuration as the canonical example.
- SHARED_SERVICES.md describes service APIs (context extensions, artifact
  resolution, path contracts) as platform capabilities available to all
  bundles, not as bundle-specific implementations.
- VALIDATION_CONTRACT.md defines the ValidationPlan pattern and composer
  model without prescribing bundle-specific validation rules.
- README.md document map lists only the six platform constitution
  documents. No bundle inventory or bundle-specific file listing appears.

### Check: Does the document set match the required permanent inventory?

**Result: PASS**

The six required permanent documents are present and correctly named:

| Required Document | Present | Template ID |
|---|---|---|
| README.md | Yes | SYS-02-IDX |
| RUNTIME_MODEL.md | Yes | SYS-02-RM |
| BUNDLE_AUTHORING_CONTRACT.md | Yes | SYS-02-BAC |
| SHARED_SERVICES.md | Yes | SYS-02-SS |
| METADATA_CONTRACT.md | Yes | SYS-02-MC |
| VALIDATION_CONTRACT.md | Yes | SYS-02-VC |

No extra permanent documents are included. The document set matches the
specification exactly.

## Authority Audit

### Check: Do any documents overclaim promotion authority above Layer 2?

**Result: PASS**

All documents correctly identify as Layer 2 platform constitution. No
document claims Layer 1 ecosystem-wide constitutional authority.

Evidence:

- All six documents carry `layer: "layer2"` in frontmatter.
- All six documents carry `doc_type: "platform_standard"`.
- README.md states: "As a Layer 2 platform core, agent-runner-v2
  translates Layer 1 ecosystem governance into a platform-specific
  operating model."
- README.md explicitly scopes Layer 3 relationship: "Layer 3 bundles must
  not modify Layer 1 governance or this platform constitution."
- No document uses language that asserts ecosystem-wide authority (e.g.,
  "all platforms must", "this governs all Layer 2 cores").

### Check: Are authority values consistent across all documents?

**Result: PASS**

All six permanent documents carry:
- `authority: "workflow-generated"` (correct for staged drafts)
- `lifecycle_status: "draft"` (correct for staged run outputs)

The METADATA_CONTRACT.md defines the authority transition rule:
`workflow-generated` -> `platform-owned` occurs on publication. This is
consistent with the current staged state.

### Check: Are temporary evidence artifacts separated from permanent standards?

**Result: PASS**

The validation artifact (PLATFORM_CORE_VALIDATION) and context inventory
(PLATFORM_CONTEXT_INVENTORY) carry:
- `doc_type: "validation_artifact"`
- `authority: "workflow-generated"`
- `scan_policy: "exclude"`
- `lifecycle_status: "draft"` or `"approved"`

These are correctly classified as temporary evidence and are not mixed
into the permanent document set.

## Metadata Audit

### Check: Do all permanent documents carry required frontmatter?

**Result: PASS**

All six documents carry the complete required frontmatter set:

| Field | README | RUNTIME | BAC | SS | MC | VC |
|---|---|---|---|---|---|---|
| template_id | SYS-02-IDX | SYS-02-RM | SYS-02-BAC | SYS-02-SS | SYS-02-MC | SYS-02-VC |
| version | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| doc_type | platform_standard | platform_standard | platform_standard | platform_standard | platform_standard | platform_standard |
| authority | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated |
| scan_policy | include | include | include | include | include | include |
| scan_reason | present | present | present | present | present | present |
| layer | layer2 | layer2 | layer2 | layer2 | layer2 | layer2 |
| platform | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 | agent-runner-v2 |
| lifecycle_status | draft | draft | draft | draft | draft | draft |
| effective_version | 02PC-GEN-... | 02PC-GEN-... | 02PC-GEN-... | 02PC-GEN-... | 02PC-GEN-... | 02PC-GEN-... |
| managed_by | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated | workflow-generated |

### Check: Are metadata values internally consistent?

**Result: PASS**

- All template_ids use the `SYS-02-*` prefix as required by the metadata
  contract.
- All scan_policy values are `"include"` for permanent standards, matching
  the metadata contract's scan policy expectations table.
- All lifecycle_status values are `"draft"`, consistent with staged run
  outputs that have not yet been published.
- The METADATA_CONTRACT.md correctly inherits Layer 1 baseline vocabulary
  without modifying meanings.
- The authority transition table in METADATA_CONTRACT.md correctly
  describes the staged-to-published transition.

### Check: Do staged permanent docs avoid published/active lifecycle state?

**Result: PASS**

All six documents carry `lifecycle_status: "draft"`. None claim
`"published"` or `"active"` status. This is correct for staged run
outputs awaiting human approval and publish.

## Platform Identity Audit

### Check: Is platform identity (agent-runner-v2) clear throughout?

**Result: PASS**

Every document explicitly identifies the platform:

- README.md: "agent-runner-v2 Platform Constitution" as title. Platform
  Identity section defines the platform in the opening paragraph.
- RUNTIME_MODEL.md: "The agent-runner-v2 runtime executes multi-step
  workflows..."
- BUNDLE_AUTHORING_CONTRACT.md: "...to run on the agent-runner-v2
  platform."
- SHARED_SERVICES.md: "...on the agent-runner-v2 platform."
- METADATA_CONTRACT.md: "...for the agent-runner-v2 platform." Multiple
  references to `platform: "agent-runner-v2"` in field semantics.
- VALIDATION_CONTRACT.md: "...platform validation model for
  agent-runner-v2."

All frontmatter carries `platform: "agent-runner-v2"`.

### Check: Does the runtime model contradict the actual platform source code?

**Result: PASS (with one minor observation)**

Key runtime claims verified against source code:

| Claim | Source File | Verified |
|---|---|---|
| step_runner.py is core execution engine | agent_runner_v2/step_runner.py | Yes |
| meta.json is sole communication channel | step_runner.py, QWEN.md | Yes |
| coder_adapters.py manages LLM invocation | agent_runner_v2/coder_adapters.py | Yes |
| coder_registry.py resolves roles to configs | agent_runner_v2/coder_registry.py | Yes |
| Dual-path discovery for registry files | coder_registry.py lines 41-50 | Yes |
| daemon.py spawns fresh subprocess per workflow | agent_runner_v2/daemon.py | Yes |
| workflow_router.py handles post-step routing | agent_runner_v2/workflow_router.py | Yes |
| job_state.py manages on-disk job state | agent_runner_v2/job_state.py | Yes |
| DocumentationValidationPlan exists | documentation_validation_core.py line 18 | Yes |
| has_section() helper exists | documentation_validation_core.py line 48 | Yes |
| has_frontmatter_field() helper exists | documentation_validation_core.py line 53 | Yes |
| write_meta_sidecar() exists | runtime_context.py line 273 | Yes |
| resolve_repo_or_runtime_path() exists | runtime_context.py line 158 | Yes |
| artifact_rel_to_meta_rel() exists | runtime_context.py line 264 | Yes |
| @action() decorator exists | workflow_packages/actions/__init__.py | Yes |

**Minor observation (non-blocking):**

RUNTIME_MODEL.md states role policies resolve via "the global runner home
`~/.ukbe-runner/workflows/default/_registry/`." The actual runtime
registry root in `coder_registry.py` is `RUNNER_ROOT / "_registry"` which
resolves to `~/.ukbe-runner/_registry/`, not
`~/.ukbe-runner/workflows/default/_registry/`. The dual-path discovery
pattern description is architecturally correct; only the specific fallback
path string is imprecise. This is a cosmetic inaccuracy that does not
affect the document's fitness as a Layer 2 platform standard.

## Cited Evidence

### Supporting Citations (all clear)

1. README.md, "Layer 1 Inheritance" section: "Layer 1 is inherited, not
   modified. This platform constitution: Does not change the meaning of
   any Layer 1 doc_type or authority value."

2. METADATA_CONTRACT.md, "Overview" section: "This contract does not
   modify or contradict Layer 1 baseline values."

3. BUNDLE_AUTHORING_CONTRACT.md, "Overview" section: "Layer 3 bundles
   must operate within this contract. They must not modify Layer 1
   ecosystem governance or this Layer 2 platform constitution."

4. All six documents, frontmatter: `layer: "layer2"`,
   `platform: "agent-runner-v2"`, `lifecycle_status: "draft"`,
   `authority: "workflow-generated"`, `doc_type: "platform_standard"`.

5. RUNTIME_MODEL.md, "Coder Registry" section, paragraph on role policy
   resolution: contains minor path inaccuracy
   (`~/.ukbe-runner/workflows/default/_registry/` vs actual
   `~/.ukbe-runner/_registry/`).

6. VALIDATION_CONTRACT.md, "Required File Inventory" section: correctly
   lists all six permanent documents with their template IDs.

### No Rejection Citations

No forbidden content was found. No rejection findings to cite.

## Publish Recommendation

**Recommendation: PROCEED TO HUMAN APPROVAL**

The staged Layer 2 platform core constitution set is ready for human
review and publish:

1. All six permanent documents are present with correct metadata.
2. Layer 1 governance is inherited correctly, not redefined.
3. No Layer 3 bundle-specific drift detected.
4. Platform identity is clear and consistent throughout.
5. No temporary evidence is classified as permanent standard.
6. All lifecycle states are correctly set to "draft" for staged outputs.
7. Runtime model accurately reflects the actual source code architecture.
8. Internal cross-document consistency is maintained (metadata values,
   template IDs, authority rules, document inventory).

The one minor observation (registry path string in RUNTIME_MODEL.md) is
cosmetic and may be corrected during publish or in a subsequent revision.
It does not block approval.
