# Platform Core Semantic Audit

## Decision

APPROVED

The staged Layer 2 platform core constitution set passes all semantic audit checks with zero findings. Every documented function signature, method name, resolution behavior, and lifecycle rule matches the actual platform source code. The set is ready for human approval and publish.

## Layer Boundary Audit

### Layer 1 Governance Inheritance

All six permanent documents inherit Layer 1 governance without redefining it.

- README.md line 49: "This platform constitution inherits from Layer 1 governance without redefining it." The five Layer 1 documents (LAYER_MODEL.md, METADATA_STANDARD.md, DOCUMENT_AUTHORITY.md, BUNDLE_TAXONOMY.md, GOVERNANCE_LIFECYCLE.md) are referenced by exact filename and treated as read-only inherited authority. All five names match the actual files in `C:\Users\kengk\.ukbe-runner\bundles\core\current\foundation\`.
- README.md line 61: Layer 1 governance documents are referenced via the `GOVERNANCE_RUNTIME_ROOT` placeholder. No repo-local L1 path strings (e.g., `docs/system/00_governance/foundation/current/`) appear in any permanent document.
- METADATA_CONTRACT.md lines 22-31: Layer 1 doc_type vocabulary is reproduced with faithful meanings. The platform-specific extension `platform_standard` is a specialization of the Layer 1 meaning, not a redefinition.
- METADATA_CONTRACT.md lines 52-65: Layer 1 authority vocabulary is inherited. Platform-specific extensions (`platform-owned`, `bundle-owned`) are added without redefining Layer 1 values.
- METADATA_CONTRACT.md lines 102-115: Inheritance rules correctly state that no lower layer may redefine values defined by a higher layer.
- RUNTIME_MODEL.md, BUNDLE_AUTHORING_CONTRACT.md, SHARED_SERVICES.md, VALIDATION_CONTRACT.md: None contain Layer 1 governance content. All remain within Layer 2 platform scope.

### Layer 3 Drift Boundary

No Layer 3 bundle-specific content was normalized into platform standards.

- BUNDLE_AUTHORING_CONTRACT.md uses generic examples (`my_bundle`, `MY_OUTPUT_FILE`, `validate_my_output`). No actual Layer 3 bundle IDs are presented as platform standards.
- VALIDATION_CONTRACT.md uses generic examples (`MYBUNDLE-01`, `my_output`). The bundle validator composition pattern is a platform-level contract, not a bundle-specific output.
- No document references specific Layer 3 bundle inventories, prompts, or artifact mappings as platform rules.

### Layer 2 Scope Verification

All six documents contain only content that belongs in Layer 2:

- Platform identity and index (README.md)
- Runtime execution architecture (RUNTIME_MODEL.md)
- Bundle authoring contract (BUNDLE_AUTHORING_CONTRACT.md)
- Shared runtime services (SHARED_SERVICES.md)
- Platform metadata contract (METADATA_CONTRACT.md)
- Platform validation contract (VALIDATION_CONTRACT.md)

## Authority Audit

### Platform Identity

All six permanent documents carry `platform: "agent-runner-v2"` in frontmatter. Every document title includes the "agent-runner-v2" prefix. The platform identity is unambiguous throughout.

### Authority Values

All six documents carry `authority: "workflow-generated"`, which is correct for staged draft documents. The METADATA_CONTRACT.md defines the authority lifecycle: staged docs use `workflow-generated`, published docs transition to `platform-owned`. No staged document claims `platform-owned` or `published` lifecycle state.

### Lifecycle State

All six permanent documents carry `lifecycle_status: "draft"`. This is correct for staged (not yet published) documents. No staged document claims `lifecycle_status: "published"`, `"active"`, or any post-publication state.

### Authority vs managed_by Orthogonality

METADATA_CONTRACT.md lines 69-74 explicitly state that `authority` and `managed_by` are orthogonal (independent axes). `authority` declares content ownership; `managed_by` declares the mechanical producer. A document carrying `authority: "platform-owned"` + `managed_by: "workflow-generated"` is explicitly stated as consistent. This satisfies the orthogonality requirement.

### Promotion Authority

No document claims promotion authority above Layer 2. The documents describe the platform operating model without claiming cross-ecosystem governance authority.

## Metadata Audit

### Frontmatter Compliance

All six documents carry all required frontmatter fields with valid values:

| Field | README.md | RUNTIME_MODEL.md | BUNDLE_AUTHORING_CONTRACT.md | SHARED_SERVICES.md | METADATA_CONTRACT.md | VALIDATION_CONTRACT.md |
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
| effective_version | 02AR-20260721-2eaba4b3 | 02AR-20260721-2eaba4b3 | 02AR-20260721-2eaba4b3 | 02AR-20260721-2eaba4b3 | 02AR-20260721-2eaba4b3 | 02AR-20260721-2eaba4b3 |

### Signature Accuracy Audit

Every documented function signature was cross-checked against the actual platform source code.

1. `build_context_extensions()` in SHARED_SERVICES.md line 25:
   - Documented: `def build_context_extensions(*, state: dict, step: str, step_cfg: dict, ctx: dict[str, str], project_root: Path | None = None) -> dict[str, str]:`
   - Source (workflows/02_agent_runner_platform_v1/context_extensions.py line 49-56): Exact match. VERIFIED.

2. `build_output_paths()` in SHARED_SERVICES.md line 77:
   - Documented: `def build_output_paths(*, job_id: str = "{job_id}", mode: str = "{mode}") -> dict[str, str]:`
   - Source minimum contract: The runner calls `build_output_paths(job_id=job_id, mode=mode)` in workflow_path_contracts.py line 19. Bundle implementations may accept additional optional parameters (e.g., `loop_iteration: int = 0` in the actual bundle). The documented signature is the minimum contract that the runner enforces. VERIFIED.

3. `resolve_repo_or_runtime_path()` in SHARED_SERVICES.md lines 50-52:
   - Documented: `def resolve_repo_or_runtime_path(path_str: str, *, project_root: Path | None = None, runtime_root: Path | None = None) -> Path:`
   - Source (runtime_context.py line 158-163): Exact match. VERIFIED.

4. `write_meta_sidecar()` in SHARED_SERVICES.md lines 124-125:
   - Documented: `def write_meta_sidecar(meta_path_like: str | Path, *, status: str, remark: str, artifacts: dict, project_root: Path | None = None, runtime_root: Path | None = None, extra: dict[str, Any] | None = None) -> Path:`
   - Source (runtime_context.py lines 273-282): Exact match. VERIFIED.

5. `DocumentationValidationPlan` in VALIDATION_CONTRACT.md lines 24-32:
   - Source (documentation_validation_core.py lines 17-23): Exact match. VERIFIED.

6. `validate_documentation_plan()` in VALIDATION_CONTRACT.md line 49:
   - Documented: `def validate_documentation_plan(*, project_root: Path, plan: DocumentationValidationPlan) -> list[ValidationCheck]:`
   - Source (documentation_validation_core.py line 58): Exact match. VERIFIED.

7. `has_section()` in VALIDATION_CONTRACT.md line 95:
   - Documented: `def has_section(content: str, section: str) -> bool:`
   - Source (documentation_validation_core.py line 48): Exact match. VERIFIED.

8. `has_frontmatter_field()` in VALIDATION_CONTRACT.md line 125:
   - Documented: `def has_frontmatter_field(content: str, field: str) -> bool:`
   - Source (documentation_validation_core.py line 53): Exact match. VERIFIED.

9. `check_file_exists()` in VALIDATION_CONTRACT.md line 160:
   - Documented: `def check_file_exists(project_root: Path, rel_path: str) -> tuple[bool, str]:`
   - Source (documentation_validation_core.py line 26): Exact match. VERIFIED.

10. `check_folder_exists()` in VALIDATION_CONTRACT.md line 170:
    - Documented: `def check_folder_exists(project_root: Path, rel_path: str) -> tuple[bool, str]:`
    - Source (documentation_validation_core.py line 33): Exact match. VERIFIED.

11. `ActionResult` dataclass in SHARED_SERVICES.md lines 228-234:
    - Source (action_result.py lines 10-15): Exact match. VERIFIED.

12. `@action()` decorator in SHARED_SERVICES.md line 198:
    - Documented: `def action(name: str | None = None) -> Callable[[ActionFn], ActionFn]:`
    - Source (workflow_packages/actions/__init__.py line 31): Exact match. VERIFIED.

### Resolution Order Accuracy

SHARED_SERVICES.md lines 56-66 describe prefix dispatch, not existence-based fallback:

1. Absolute paths returned unchanged.
2. `docs/`, `archive/`, `scripts/`, `temp/` prefixes resolve under project root.
3. `.ukbe-runner/` prefix resolves under runner home.
4. Everything else resolves under jobs root.

Source (runtime_context.py lines 171-187) confirms this exact dispatch logic. No forbidden phrases ("check the repository working tree first", "fall back to the runtime artifact root") appear. VERIFIED.

### Meta Sidecar Accuracy

Both RUNTIME_MODEL.md lines 34-36 and SHARED_SERVICES.md lines 96-133 accurately describe:
- The primary sidecar channel (meta.json v2 schema)
- The repair fallback via `_repair_or_validate_meta_json()` in step_runner.py (line 637)

No forbidden phrases ("no disk recovery functions", "no stdout JSON parsing", "sole communication channel" paired with denial of fallbacks) appear. VERIFIED.

### BackendClient Method Accuracy

SHARED_SERVICES.md lines 163-178 list 14 public methods. All 14 exist as `def` in backend_client.py:

| Method | Source Line |
|---|---|
| submit_run() | line 40 |
| approve_run() | line 85 |
| get_run() | line 93 |
| list_runs() | line 96 |
| stop_run() | line 115 |
| reset_run_step() | line 121 |
| register_worker() | line 124 |
| heartbeat() | line 132 |
| claim_step() | line 170 |
| complete_step_run() | line 173 |
| sync_job_state() | line 176 |
| create_artifact() | line 179 |
| create_event() | line 182 |
| cleanup_execution() | line 185 |

Zero mismatches. VERIFIED.

### Path Canonical Accuracy

No shortened or schematic example paths (e.g., `docs/platform/README.md`) appear in any permanent document. All path references use full canonical forms where present. VERIFIED.

### ASCII Compliance

No non-ASCII characters found in any of the six permanent documents or two evidence artifacts. VERIFIED.

## Platform Identity Audit

- All six documents carry `platform: "agent-runner-v2"`.
- All document titles use the "agent-runner-v2" prefix.
- README.md lines 35-46 define the platform identity clearly.
- Each document is scoped to the agent-runner-v2 platform without claiming cross-platform applicability.
- The `platform_standard` doc_type is used consistently for all permanent documents.
- Temporary evidence artifacts are correctly separated from permanent standards.

## Cited Evidence

All findings support approval. No rejection findings exist.

1. README.md line 49: "This platform constitution inherits from Layer 1 governance without redefining it." -- confirms Layer 1 inheritance without redefinition.
2. README.md line 61: "The Layer 1 governance documents are installed at the global runtime root (GOVERNANCE_RUNTIME_ROOT)" -- confirms correct L1 reference pattern without repo-local paths.
3. README.md lines 20-31: Document map includes all six documents with README.md as entry 1. The published set inventory is six documents, not five plus an implicit index.
4. METADATA_CONTRACT.md lines 69-74: "The authority and managed_by fields serve distinct purposes and are orthogonal (independent axes)" -- satisfies the orthogonality requirement.
5. SHARED_SERVICES.md lines 56-66: Resolution Order describes prefix dispatch, not existence-based fallback. Verified against runtime_context.py lines 171-187.
6. SHARED_SERVICES.md lines 129-133: Repair fallback correctly describes `_repair_or_validate_meta_json()` from step_runner.py line 637.
7. RUNTIME_MODEL.md lines 34-36: Correctly describes both the primary sidecar channel and the repair fallback. No forbidden phrases present.
8. SHARED_SERVICES.md lines 163-178: All 14 BackendClient methods verified against backend_client.py. Zero mismatches.
9. VALIDATION_CONTRACT.md lines 111-118: Required sections table matches actual section headings in all six documents.
10. All frontmatter values comply with Layer 1 METADATA_STANDARD.md vocabulary. No redefinitions.
11. All staged documents carry `lifecycle_status: "draft"`. No document prematurely claims published/active state.
12. RUNTIME_MODEL.md lines 24-36: `run_step()` description matches source code at step_runner.py lines 119-317.
13. RUNTIME_MODEL.md lines 49-55: `run_action()` description matches source code at step_runner.py lines 324-403.
14. SHARED_SERVICES.md lines 24-26: `build_context_extensions()` signature verified against context_extensions.py line 49-56.
15. SHARED_SERVICES.md lines 77-78: `build_output_paths()` signature verified against the runner contract in workflow_path_contracts.py line 19.
16. SHARED_SERVICES.md lines 50-52: `resolve_repo_or_runtime_path()` signature verified against runtime_context.py lines 158-163.
17. SHARED_SERVICES.md lines 124-125: `write_meta_sidecar()` signature verified against runtime_context.py lines 273-282.
18. VALIDATION_CONTRACT.md lines 24-49: All validation primitive signatures verified against documentation_validation_core.py.

## Publish Recommendation

The staged Layer 2 platform core constitution set is ready for human approval and publish.

The set is:
- Semantically correct against the actual platform source code
- Layer 2 scoped with no Layer 1 redefinition or Layer 3 drift
- Metadata-compliant with all required frontmatter fields
- Platform-identified as agent-runner-v2 throughout
- Free of forbidden content
- Consistent internally on authority, lifecycle, and metadata rules
- In correct lifecycle state (draft) for staged documents

The recommended next step is the human approval gate (Step 7 of the workflow), followed by the publish action (Step 8) which will copy the approved set to `docs/system/00_governance/platform/agent_runner/current/`, transition frontmatter from `draft` to `published`, and write the publish manifest.
