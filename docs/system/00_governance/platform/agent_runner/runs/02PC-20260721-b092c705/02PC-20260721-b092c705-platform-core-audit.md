---
doc_type: "audit_artifact"
authority: "workflow-generated"
scan_policy: "exclude"
scan_reason: "final semantic audit of staged Layer 2 platform core set"
layer: "layer2"
platform: "agent-runner-v2"
lifecycle_status: "draft"
effective_version: "02PC-20260721-b092c705"
generated_at: "2026-07-21T17:52:21+08:00"
---

# Platform Core Semantic Audit

- Job ID: `02PC-20260721-b092c705`
- Audit scope: All six staged permanent Layer 2 platform constitution
  documents plus reference inputs and platform source code.
- Audit type: Final semantic verification before human approval and
  publish.

## Decision

APPROVED

The staged Layer 2 platform core constitution set for agent-runner-v2
is ready for human approval and publish. Every claim in every document
matches the platform source code. Zero factual errors found. Zero
forbidden-content violations found. Zero layer-boundary violations
found.

## Layer Boundary Audit

All six permanent documents remain within Layer 2 scope.

- README.md inherits Layer 1 governance explicitly (line 62: "This
  platform constitution inherits from Layer 1 governance without
  redefining it") and does not redefine any Layer 1 rules.
- RUNTIME_MODEL.md describes the agent-runner-v2 execution architecture
  at the platform-contract level. It does not contain Layer 1 governance
  rules or Layer 3 bundle-specific outputs.
- BUNDLE_AUTHORING_CONTRACT.md defines the contract for all Layer 3
  bundles generically. Examples use placeholder names (my_bundle_name,
  my_bundle) and do not present any specific bundle's configuration as
  a platform rule.
- SHARED_SERVICES.md documents platform runtime services using actual
  source code signatures. No bundle-specific logic is normalized into
  platform standards.
- METADATA_CONTRACT.md extends Layer 1 metadata rules for the platform
  without redefining any Layer 1 baseline values.
- VALIDATION_CONTRACT.md documents the platform validation model using
  the actual DocumentationValidationPlan pattern from the source code.

No Layer 3 bundle-specific drift detected. No concrete bundle
inventories are included. No Layer 1 constitutional content is
redefined or contradicted.

## Authority Audit

### Lifecycle State

All six staged permanent documents carry `lifecycle_status: "draft"`,
which is correct for documents that have not yet been published. No
staged document claims `lifecycle_status: "published"` or
`lifecycle_status: "active"`. This is correct per the Layer 1
governance lifecycle standard.

### Authority Values

All six staged documents carry `authority: "workflow-generated"`, which
is correct for documents produced by the `02_platform_core_foundation_v1`
workflow before publication. After publish, these may be updated to
`platform-owned` per the METADATA_CONTRACT.md rules.

### Authority and Managed-By Orthogonality

METADATA_CONTRACT.md "Usage Rules" section (lines 101-117) explicitly
states that `authority` and `managed_by` are orthogonal axes:

- `authority` answers: "Who owns the canonical truth of this document?"
  (content ownership)
- `managed_by` answers: "What mechanism produced and maintains this
  file?" (mechanical production)

The contract explicitly provides the consistency example: "A document
carrying authority: 'platform-owned' and managed_by: workflow-generated
is consistent: the platform core owns the content, but a workflow
mechanically produces and maintains the file on disk."

No contradiction exists between these two fields. The orthogonality
statement is explicit and unambiguous.

### Layer 1 Vocabulary Compliance

All `doc_type`, `authority`, and `scan_policy` values used in the
staged set match the Layer 1 allowed vocabulary as defined in
METADATA_STANDARD.md (Layer 1 governance runtime root). No generated
document claims `human-authored` authority. No Layer 3 document claims
`platform-owned` authority or `platform_standard` doc_type.

## Metadata Audit

### Required Fields

All six permanent documents carry all required fields:

| Field | Present | Value |
|---|---|---|
| template_id | Yes | SYS-02-IDX, SYS-02-RM, SYS-02-BAC, SYS-02-SS, SYS-02-MC, SYS-02-VC |
| version | Yes | "1.0" on all documents |
| doc_type | Yes | "platform_standard" on all documents |
| authority | Yes | "workflow-generated" on all documents |
| scan_policy | Yes | "include" on all documents |
| scan_reason | Yes | Non-empty on all documents |
| layer | Yes | "layer2" on all documents |
| platform | Yes | "agent-runner-v2" on all documents |
| lifecycle_status | Yes | "draft" on all documents |
| effective_version | Yes | "02PC-20260721-b092c705" on all documents |
| managed_by | Yes | "workflow-generated" on all documents |

### Platform Extension Compliance

All platform extension fields (platform, template_id, managed_by,
lifecycle_status, effective_version) are present and carry valid
values per the METADATA_CONTRACT.md specification.

### Evidence Separation

Temporary evidence artifacts (context inventory, validation report,
review artifact) carry appropriate `doc_type` values
("validation_artifact", "review_artifact") with `scan_policy: "exclude"`
and are clearly separated from the permanent document set. No evidence
artifact is presented as a permanent platform standard.

## Platform Identity Audit

Platform identity "agent-runner-v2" is clearly and consistently stated
throughout the document set:

- README.md "Platform Identity" section establishes the platform as
  "a general-purpose workflow execution engine" and explains its role
  as "one of several possible Layer 2 cores that operationalize Layer 1
  ecosystem governance for a specific runtime family."
- Every permanent document carries `platform: "agent-runner-v2"` in
  frontmatter.
- Every permanent document carries `layer: "layer2"` in frontmatter.
- No document claims ecosystem-wide (Layer 1) authority.
- No document collapses into Layer 3 bundle-specific content.
- Cross-document references are consistent (e.g., SHARED_SERVICES.md
  references the Bundle Authoring Contract; METADATA_CONTRACT.md is
  referenced by BUNDLE_AUTHORING_CONTRACT.md).

## Signature Accuracy Audit

Every documented function signature in SHARED_SERVICES.md was
cross-verified against the actual platform source code.

### build_context_extensions()

Documented (SHARED_SERVICES.md lines 35-42):

    def build_context_extensions(
        *,
        state: dict,
        step: str,
        step_cfg: dict,
        ctx: dict[str, str],
        project_root: Path | None = None,
    ) -> dict[str, str]:

Source (workflows/02_platform_core_foundation_v1/context_extensions.py
line 35):

    def build_context_extensions(
        *,
        state: dict,
        step: str,
        step_cfg: dict,
        ctx: dict[str, str],
        project_root: Path | None = None,
    ) -> dict[str, str]:

MATCH.

### build_output_paths()

Documented (SHARED_SERVICES.md line 138):

    def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:

Source (workflows/02_platform_core_foundation_v1/output_paths.py line 4):

    def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:

MATCH. The output_paths.py module is the canonical contract invoked by
the platform via workflow_path_contracts.py.

### resolve_repo_or_runtime_path()

Documented (SHARED_SERVICES.md lines 91-96):

    def resolve_repo_or_runtime_path(
        path_str: str,
        *,
        project_root: Path | None = None,
        runtime_root: Path | None = None,
    ) -> Path:

Source (agent_runner_v2/runtime_context.py line 158):

    def resolve_repo_or_runtime_path(
        path_str: str,
        *,
        project_root: Path | None = None,
        runtime_root: Path | None = None,
    ) -> Path:

MATCH.

### write_meta_sidecar()

Documented (SHARED_SERVICES.md lines 240-249):

    def write_meta_sidecar(
        meta_path_like: str | Path,
        *,
        status: str,
        remark: str,
        artifacts: dict,
        project_root: Path | None = None,
        runtime_root: Path | None = None,
        extra: dict[str, Any] | None = None,
    ) -> Path:

Source (agent_runner_v2/runtime_context.py line 273):

    def write_meta_sidecar(
        meta_path_like: str | Path,
        *,
        status: str,
        remark: str,
        artifacts: dict,
        project_root: Path | None = None,
        runtime_root: Path | None = None,
        extra: dict[str, Any] | None = None,
    ) -> Path:

MATCH.

## Resolution Order Accuracy Audit

SHARED_SERVICES.md "Resolution Order" section (lines 99-115) describes
the behavior of resolve_repo_or_runtime_path() as prefix-dispatch:

1. Absolute paths returned unchanged.
2. Repo-owned prefixes (docs/, archive/, scripts/, temp/) resolved
   under project root.
3. Runner-home paths (.ukbe-runner/) resolved under runner home.
4. Default resolved under jobs root.

Source code (agent_runner_v2/runtime_context.py lines 158-187) confirms
this exact behavior. The function dispatches by path prefix using
str.startswith() checks. It does NOT check the filesystem for existence
before resolving. No forbidden phrases ("check the repository working
tree first", "fall back to the runtime artifact root") are present.

MATCH.

## Meta Sidecar Accuracy Audit

Both RUNTIME_MODEL.md (lines 183-192) and SHARED_SERVICES.md (lines
210-232) accurately describe:

1. The meta.json sidecar as the primary communication channel between
   the coder and the runner.
2. The repair fallback via `_repair_or_validate_meta_json()` in
   `step_runner.py` (source line 637).
3. Handling of both MetaJsonMissingError and MetaJsonInvalidError.
4. Repair via parsed stdout when the sidecar is missing or invalid.

No forbidden phrases ("no disk recovery functions", "no stdout JSON
parsing", "sole communication channel" paired with denial of fallbacks)
are present in either document.

MATCH.

## BackendClient Method Accuracy Audit

All 14 BackendClient public methods documented in SHARED_SERVICES.md
(lines 320-339) were verified against agent_runner_v2/backend_client.py:

| Method | Source Line | Status |
|---|---|---|
| submit_run() | 40 | EXISTS |
| approve_run() | 85 | EXISTS |
| get_run() | 93 | EXISTS |
| list_runs() | 96 | EXISTS |
| stop_run() | 115 | EXISTS |
| reset_run_step() | 121 | EXISTS |
| register_worker() | 124 | EXISTS |
| heartbeat() | 132 | EXISTS |
| claim_step() | 170 | EXISTS |
| complete_step_run() | 173 | EXISTS |
| sync_job_state() | 176 | EXISTS |
| create_artifact() | 179 | EXISTS |
| create_event() | 182 | EXISTS |
| cleanup_execution() | 185 | EXISTS |

The BackendClient dataclass definition (base_url: str, timeout_seconds:
int = 30) matches source lines 9-12.

MATCH. Zero mismatches.

## Forbidden Content Audit

The following forbidden content checks were performed against all six
permanent documents:

| Check | Result |
|---|---|
| Layer 1 governance redefinition or contradiction | PASS - none found |
| Bundle-specific content normalized into platform standards | PASS - none found |
| Missing platform identity (agent-runner-v2) | PASS - present throughout |
| Temporary evidence normalized into permanent standards | PASS - evidence separated |
| Overclaimed promotion authority above Layer 2 | PASS - none found |
| Internal conflicts on authority, lifecycle, or metadata rules | PASS - none found |
| Published/active lifecycle state in staged docs | PASS - all carry draft |
| Runtime model contradicting source code | PASS - model matches code |
| Wrong function signatures | PASS - all signatures match |
| Wrong resolution-order description | PASS - prefix-dispatch correct |
| "no disk recovery functions" phrase | PASS - not present |
| "no stdout JSON parsing" phrase | PASS - not present |
| "sole communication channel" denying fallbacks | PASS - not present |
| Missing BackendClient subsection | PASS - present with all methods |
| Wrong BackendClient method names | PASS - all 14 methods exist |
| Shortened/schematic example paths | PASS - canonical paths used |
| Non-ASCII characters | PASS - ASCII only confirmed |

All checks pass. Zero forbidden-content violations.

## Cited Evidence

Positive citations for the record:

- README.md line 62: "This platform constitution inherits from Layer 1
  governance without redefining it."
- README.md lines 48-58: Document map lists all six permanent documents
  including README.md itself (self-including index).
- README.md lines 99-106: Explicit exclusions stating the set does not
  include Layer 1 governance, bundle inventories, job-history evidence,
  or setup guides.
- METADATA_CONTRACT.md lines 101-117: Explicit orthogonality statement
  for authority and managed_by fields with concrete consistency example.
- SHARED_SERVICES.md lines 99-115: Accurate prefix-dispatch resolution
  order matching runtime_context.py lines 158-187.
- SHARED_SERVICES.md lines 210-232: Accurate description of meta sidecar
  repair fallback matching step_runner.py lines 637-677.
- RUNTIME_MODEL.md lines 183-192: Accurate description of meta sidecar
  as primary channel with repair fallback covering MetaJsonMissingError
  and MetaJsonInvalidError.
- VALIDATION_CONTRACT.md lines 97-104: Complete template_id to required
  section mapping table matching actual document headings.
- VALIDATION_CONTRACT.md lines 187-199: Canonical path usage examples
  using full paths (docs/system/00_governance/platform/current/...).
- BUNDLE_AUTHORING_CONTRACT.md lines 261-289: Metadata compliance rules
  correctly referencing Layer 1 baseline and platform extensions.

## Publish Recommendation

The staged Layer 2 platform core constitution set is ready for human
approval and publish. The audit found zero defects across all audit
dimensions:

1. Layer boundary correctness: All documents stay within Layer 2 scope.
2. Authority and metadata compliance: All fields and values are correct.
3. Source code accuracy: All function signatures, method names, and
   behavioral descriptions match the actual platform source code.
4. Platform identity: "agent-runner-v2" is clearly stated throughout.
5. Forbidden content: None present.
6. Lifecycle state: All staged documents correctly carry "draft" status.

Recommended next step: Present the approved permanent set plus this
audit evidence to the platform owner for explicit human approval,
then proceed to publish into
docs/system/00_governance/platform/current/.
