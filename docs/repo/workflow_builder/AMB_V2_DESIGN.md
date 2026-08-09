# AR Meta Builder v2 — Design Document

> **Status:** DESIGN PHASE
> **Created:** 2026-08-09
> **Supersedes:** ar_meta_builder_v1 (current)
> **Base Component Schema:** `docs/repo/workflow_builder/current/COMPOSITION_SYSTEM_STANDARD.md`

---

## 1. Problem Analysis — Why AMB v1 Failed

### 1.1 The Identity Leak

AMB v1 run `AMB-ai99miop` generated `codebase_to_meta_v1` — but the output was an
uncustomized copy of the AMB itself:

| Artifact | What it says | What it should say |
|---|---|---|
| workflow.toml | `name = "ar_meta_builder_v1"` | `name = "codebase_to_meta_v1"` |
| context_extensions.py | `ArMetaBuilderV1Extensions` | `CodebaseToMetaV1Extensions` |
| README.md | "AR Meta Builder v1" | "Codebase to Meta Content v1" |
| Standards/COMPOSITION_STANDARD.md | `AR_META_BUILDER_STANDARD` | `CODEBASE_TO_META_STANDARD` |

The LLM copied the **builder's** identity into every generated artifact instead of
deriving identity from the **input spec**.

### 1.2 The Structure Copy Problem

Worse than identity — the AMB copied its own **entire 9-phase/22-step structure**
into the output. The generated `codebase_to_meta_v1` has the same TDD loop, same
component schema phases, same composition format, same output format, same
operational workflow, same package assembly as the AMB itself.

But the input spec says the workflow should be:
- **Init step:** `scan_audiences`
- **Domain phases:** Scan → Generate → Review → Refine → Publish
- **Type:** Mixed (action for scanning/publishing, prompts for generation/review)

A proper `codebase_to_meta_v1` should have ~5 steps, not 22.

### 1.3 Root Cause

The AMB v1 prompts enforce a **fixed output template** — the 9-phase composition
system structure is hardcoded into the prompt instructions. The LLM never had the
flexibility to design a workflow suited to the target domain. It could only fill in
the template with domain-specific content.

This defeats the purpose of the composition standard and meta composition spec —
they're supposed to be the **target's** LEGO catalog and assembly manual, not a
description of the AMB's own structure.

---

## 2. Pattern Discovery — Studying All Workflows

A comprehensive survey of all 21 workflows in the system revealed these patterns:

### 2.1 Cross-Cutting Patterns (Universal)

| Pattern | Frequency | Description |
|---|---|---|
| `step_completion` terminal | 21/21 | Universal terminal step |
| Review/refine loop | 20/21 | Generate → review → refine on rejection |
| Promote/publish action | 18/21 | Deploy deliverables to target location |
| Exhaustion failure | all loops | `exhausted_failure_code` + `HUMAN_RETRY_REQUIRED` |
| Human approval gate | 14/21 | `requires_human_approval_after` at key points |

### 2.2 Category-Specific Patterns

| Category | Pattern | Steps | Quality Approach |
|---|---|---|---|
| **SDLC delivery** | generate → critique → address → review(human) → refine → promote | 6 | Dual loop: automated critique + human review |
| **Governance/Platform** | collect → generate → review → validate → audit(human) → publish | 9 | Triple refine routing |
| **Media** | linear pipeline with deferred archive | 3-9 | Self-refine + human approval before expensive ops |
| **Meta builder v1** | TDD → analyze_spec → define_artifacts → design_steps → generate_package | 14 | Spec-driven, gatekeep at each phase |
| **Meta builder v2/v3/AMB** | TDD → component_schema → composition_format → output_format → operational_workflow → standard → package | 21-22 | Fixed composition layers, gatekeep each |

### 2.3 Key Insight

**workflow_builder_v1 is the only truly spec-driven meta builder.** It has
`analyze_spec` → `define_artifacts` → `design_steps` — the LLM infers the workflow
structure from the spec. Every subsequent builder (v2, v3, AMB v1) abandoned this
flexibility for a fixed composition layer structure.

The SDLC delivery pattern (generate → critique → address → review → refine → promote)
is the most consistent and proven pattern — used across 9+ workflows with identical
structure.

---

## 3. Core Insight: Recursive Composition

### 3.1 AMB Output and ByProduct Output Are Structurally Identical

There are two artifact types in the system, but they follow the **same structural
pattern**:

| Aspect | AMB Output | ByProduct Output |
|---|---|---|
| **What** | The meta builder itself (workflow package) | What the generated meta builder produces at runtime |
| **Example** | AMB v1 package (workflow.toml, prompts, actions.py) | codebase_to_meta_v1's audience-specific meta content files |
| **Runs in** | Always agent-runner-v2 repo | Any repo, any folder — depends on meta builder design |
| **Structure** | Schema + artifacts + actions + steps + gatekeepers + promote | Schema + artifacts + actions + steps + gatekeepers + promote |

Both follow the same pattern: define domain → define schema → define artifacts →
define actions → define steps → define gatekeepers → approve → promote/publish.

### 3.2 The Recursive Chain

```
Workflow Builder v2
    → reads AMB v1 spec (follows WF Builder v2's composition standard)
    → produces AMB v1 package (AMB Standard v1, derived from WF Builder v2's standard)
    → promotes to workflows/ in agent-runner-v2 repo

AMB v1
    → reads codebase_to_meta_v1 spec (follows AMB v1's composition standard)
    → produces codebase_to_meta_v1 package (CTM Standard v1, derived from AMB Standard v1)
    → promotes per runtime spec definition
```

Each generated standard is a **specialization of its parent's standard**. The
composition standard is recursive — every level follows the same pattern but with
domain-specific content.

### 3.3 The AMB Does One Thing

The AMB doesn't need two different output modes. It always does the same thing:
1. Read runtime spec (which follows the AMB's composition standard)
2. Analyze domain
3. Generate domain standard (derived from AMB's own standard)
4. Generate schema, artifacts, actions, steps, gatekeepers
5. Package, approve, promote

The "AMB output vs ByProduct output" distinction is just about what domain the
output targets — not about different processing or different output structures.

---

## 4. Output Type Distinction

### 4.1 Two Output Delivery Patterns

Not all workflows need the full package → approve → promote → publish pipeline.
The runtime spec declares the output type, and the AMB designs accordingly:

| Output Type | Pipeline | Examples |
|---|---|---|
| **Documented/Versioned** | Full pipeline: review → refine → approve → promote → publish → history | Governance docs, SDLC delivery, workflow packages, codebase docs |
| **Direct** | Just produce (maybe with human approval before expensive ops) | Videos (agnes_gen_video), images + videos (agnes_media_gen) |

### 4.2 When to Use Each

**Documented/Versioned** — when the output needs:
- Version tracking (history of changes)
- Audit trail (who approved what, when)
- Approval gates (human review before publishing)
- Staging lifecycle (stage → review → refine → backup → history → publish)
- Rollback capability (restore previous version)

**Direct** — when the output:
- Is consumed immediately by downstream processes
- Doesn't need versioning or audit trail
- Is expensive to produce (API calls, compute) — needs human approval before execution, not after
- Lives in a single location (no staging/history)

### 4.3 AMB v2 Design Implication

The AMB's Phase 7 (domain steps) designs the output delivery mechanism based on
the spec's declared output type. Some workflows get promote/publish steps, others
just produce directly. This is a spec-driven decision, not a fixed template.

---

## 5. Fine-Tuning Analogy

### 5.1 Base Component Schema as "Pre-Trained Model"

The `COMPOSITION_SYSTEM_STANDARD.md` defines the universal pattern:
- **Universal Component Schema** — Common properties (component_id, component_type,
  name, version, tags, description) + type-specific extensions
- **Composition Format Standard** — Binding rules, override mechanism,
  placeholder resolution
- **Output Format** — Resolved deliverables with all references expanded
- **Validation Rules** — Required fields, unique IDs, type conformance
- **Extensibility Model** — New types without breaking existing compositions

### 5.2 Fine-Tuning Process

```
Base Component Schema (COMPOSITION_SYSTEM_STANDARD.md)
    ├── Universal Component Schema (common properties)
    ├── Composition Format Standard (binding rules)
    └── Output Format (resolved deliverables)
         │
         ▼  fine-tune per domain
    ┌─────────────────────────────────────────┐
    │ Domain Component Schema                  │
    │ ├── Keep relevant base types             │
    │ ├── Add domain-specific types            │
    │ ├── Drop irrelevant types                │
    │ └── Specialize properties per domain     │
    └─────────────────────────────────────────┘
```

The AMB reads the base schema and specializes it for the target domain:
- **Keep** universal common properties (component_id, component_type, etc.)
- **Select** relevant type categories from the base
- **Add** domain-specific component types and properties
- **Drop** types that don't apply to the target domain
- **Specialize** validation rules for the domain

---

## 6. AMB v2 Pipeline

### 6.1 TDD as DNA — Not a Phase

TDD is NOT a separate phase. It is the **operating principle** embedded in every
phase. Every phase follows the same standardized 5-step TDD pattern:

```
┌──────────────────────────────────────────────────────────────┐
│ STANDARDIZED PHASE PATTERN (auto-applied to ALL phases)       │
│                                                               │
│  1. generate_test_criteria                                    │
│     Define what "correct" means for THIS phase's artifact.    │
│     What must be true? What constraints apply?                │
│                                                               │
│  2. review_test_criteria  ← CRITIC                            │
│     Challenge: do these tests actually test the right thing?  │
│     Are they meaningful? Do they cover edge cases?            │
│     [on reject → refine criteria → re-review]                 │
│                                                               │
│  3. generate_artifact                                         │
│     Produce the phase deliverable.                            │
│                                                               │
│  4. validate_artifact  ← DETERMINISTIC (action)               │
│     All docs produced? Structurally valid? Identity correct?  │
│     Parse checks, required sections, key consistency.         │
│                                                               │
│  5. gatekeep_artifact  ← LLM                                  │
│     Run validated test criteria against artifact.             │
│     Pass or fail with specific evidence.                      │
│     [on fail → refine_artifact → back to step 4, max N]      │
│                                                               │
│  → step_completion                                            │
└──────────────────────────────────────────────────────────────┘
```

**Key roles:**
- **Critic** (step 2): Reviews the TEST, not the artifact. Questions whether
  the test criteria actually prove the artifact's correctness.
- **Validate** (step 4): Deterministic checks — docs exist, parse correctly,
  identity matches, structural completeness.
- **Gatekeeper** (step 5): Runs the validated test criteria against the
  artifact. Pass/fail with evidence. Ensures tests are fully implemented and pass.

### 6.2 Nine Design Phases

Each phase produces one design artifact and follows the standardized TDD pattern:

```
Phase 1: Analyze Spec
         → Domain analysis (identity, components, output type, natural phases)

Phase 2: Domain Component Schema
         → Fine-tuned from Base Component Schema (keep/add/drop/specialize)

Phase 3: Composition Format
         → How domain components bind together (binding rules, overrides)

Phase 4: Output Format
         → What the target workflow produces (structure, resolution, quality)

Phase 5: Component Artifacts
         → Artifact keys and filename patterns for the domain

Phase 6: Domain Steps
         → Step sequence following spec's natural phases + output delivery

Phase 7: Runtime Standard
         → Consolidation of Phases 1-6 into the domain's composition standard

Phase 8: Operational Workflow
         → Concrete workflow step sequence using the runtime standard

Phase 9: Package
         → Complete executable workflow package + promote
```

All phases 1-8 follow the standardized TDD pattern (5 steps each).
Phase 9 (Package) uses the standard terminal pattern (validate + review + refine + promote + step_completion).

### 6.3 Phase Details

#### Phase 1: Analyze Spec

**Pre-step: validate_input_spec (action)**
Before any generation, deterministically validate the input spec has the minimum
required fields. If this fails → AWAITING_INTERVENTION (cannot proceed).
- Identity fields present: standard_name, standard_version, standard_filename
- Output type declared: documented_versioned or direct
- Domain overview section present
- At least one component or domain concept described

**Then TDD pattern:**
Read the target spec. Understand the domain, identify natural components, lock
identity fields. Determine output type. Generate **meta-test-criteria** —
cross-phase invariants that ALL subsequent phase gatekeepers must verify:
- Generated workflow uses spec's identity, not builder's identity
- Generated workflow structure matches spec's domain, not AMB's structure
- Output delivery mechanism matches spec's declared output type
- All component types derived from base schema fine-tuning, not hardcoded

**Artifact:** Domain analysis document with identity, component inventory,
natural workflow phases, output delivery pattern, meta-test-criteria.

**Test criteria focus:** Identity correctness, completeness of domain analysis,
output type justification, meta-test-criteria coverage.

#### Phase 2: Domain Component Schema
Read the Base Component Schema (`COMPOSITION_SYSTEM_STANDARD.md`) and fine-tune
for the target domain. Keep relevant universal types, add domain-specific types,
drop irrelevant ones.

**Artifact:** Domain-specific component schema (the target's LEGO block catalog).

**Test criteria focus:** All base common properties retained, fine-tuning
decisions justified, domain types well-defined, validation rules present.

#### Phase 3: Composition Format
Define how domain components bind together. Binding rules, override mechanism,
placeholder resolution — all derived from the domain component schema.

**Artifact:** Composition format document (the target's assembly rules).

**Test criteria focus:** All component types have binding rules, override
mechanism defined, placeholder resolution specified, examples provided.

#### Phase 4: Output Format
Define what the target workflow produces. Output structure, resolution rules,
quality requirements — derived from the domain's composition format.

**Artifact:** Output format document (the target's deliverable specification).

**Test criteria focus:** Output structure matches composition format, resolution
rules complete, quality requirements measurable, consistent with output type.

#### Phase 5: Component Artifacts
Define the specific artifact keys for the target domain. Each artifact key maps
to a filename pattern. This ensures the generated workflow has proper artifact
tracking.

**Validate includes conflict check:** The validate action checks artifact keys
against the existing global registry (`artifact_keys.py`) and known workflow
keys. Flag any collisions with system-level or existing workflow keys.

**Artifact:** Artifact contract (key → filename pattern → description).

**Test criteria focus:** All phases have artifact keys, filename patterns
consistent, no duplicates, naming conventions followed, no conflicts with
existing global keys.

#### Phase 6: Domain Steps
Design the workflow steps that follow the spec's natural domain phases. NOT the
AMB's fixed structure — the target's own phases.

**Output delivery design (based on output type):**
- **Documented/versioned:** Must design the target's own review loops, approval
  gates (`requires_human_approval_after`), promote actions, and archive steps.
  The target workflow gets its own quality lifecycle.
- **Direct:** No review/approval/promote. Just produce. May include human
  approval *before* expensive operations (e.g., API calls).

**Artifact:** Step sequence document (step names, types, routing, role policies,
artifact bindings, delivery mechanism, review/approval design if documented type).

**Test criteria focus:** Steps match spec's natural phases, routing correct,
output delivery matches declared type, no AMB structure leakage. For documented
type: review loops, approval gates, and promote actions explicitly designed.

#### Phase 7: Runtime Standard
Consolidate Phases 1-6 into the domain's composition standard. This is the
target's LEGO catalog — named per identity contract (e.g.,
`CODEBASE_TO_META_STANDARD-v1.md`).

**Artifact:** Composition standard document.

**Test criteria focus:** All phases 1-6 content present and consistent, identity
fields correct, standard named per spec, no builder identity leakage.

#### Phase 8: Operational Workflow
Design the actual workflow step sequence using the runtime standard as input.
This is where the target's natural phases become concrete workflow steps with
prompts, actions, and routing.

**Artifact:** Operational workflow document (the target's assembly manual).

**Test criteria focus:** Steps use standard's components, routing matches domain
steps (Phase 6), prompts reference correct artifacts, identity propagated.

#### Phase 9: Package
Generate the complete executable workflow package:
- `workflow.toml` — with correct identity from spec
- `context_extensions.py` — with domain-specific class name
- `actions.py` — with domain-specific action implementations
- `prompts/` — one per prompt-driven step
- `README.md` — describing the target workflow
- `Standards/{standard_filename}` — the composition standard
- `Specs/` — directory for runtime specs

**Self-bootstrap embedding:** Copy the AMB v2 spec (`WORKFLOW_SPEC_FILE`) to
`output/Specs/{builder_name}.md` — enables AMB v2 to generate AMB v3 (recursive
chain). Same pattern as workflow_builder_v4's `embed_builder_spec`.

**Terminal pattern:** validate_package (action) → review_package (human) →
[refine_package] → promote → step_completion.

### 6.4 Standardized Step Template

Every phase (1-8) instantiates this template with phase-specific content:

| Step | Type | Role | Purpose |
|------|------|------|---------|
| `generate_test_criteria_{phase}` | Prompt | Coder | Define success criteria for this phase |
| `review_test_criteria_{phase}` | Prompt | Critic | Challenge: do tests test the right thing? |
| `[refine_test_criteria_{phase}]` | Prompt | Coder | Fix test criteria (on reject, max N) |
| `generate_{phase}_artifact` | Prompt | Coder | Produce the phase deliverable |
| `validate_{phase}_artifact` | Action | Validator | Deterministic: docs exist, parse, identity |
| `gatekeep_{phase}_artifact` | Prompt | Gatekeeper | Run test criteria + meta-test-criteria, pass/fail |
| `[refine_{phase}_artifact]` | Prompt | Coder | Fix artifact (on fail, max N) |

**Phase 1 special:** Has a pre-step `validate_input_spec` (action) that runs
BEFORE the TDD pattern. Also generates meta-test-criteria as part of its output.

**Meta-test-criteria propagation:** Phase 1's meta-test-criteria are injected
into ALL subsequent phases' gatekeep prompts. Every gatekeeper checks both the
phase-specific test criteria AND the cross-phase meta-test-criteria.

**Refine loops:** Both test criteria and artifact have refine loops with
exhaustion handling (`exhausted_failure_code` + `HUMAN_RETRY_REQUIRED`).

### 6.5 Validate Action Strategy (Resolved)

**Two validate functions:**

```python
@action
def validate_input_spec(job_dir, context):
    """Phase 1 pre-step: validate the input spec has minimum required fields."""
    # Check: identity fields present (standard_name, standard_version, standard_filename)
    # Check: output_type declared (documented_versioned or direct)
    # Check: domain overview section present
    # Check: at least one component or domain concept described
    # On fail → AWAITING_INTERVENTION (cannot proceed without valid spec)

@action
def validate_design_artifact(job_dir, context, phase="component_schema"):
    """Phases 2-8: validate a design artifact."""
    # Common checks (all phases):
    #   - All expected output files exist
    #   - Files parse correctly (markdown, YAML, TOML)
    #   - Identity fields present and match spec
    #   - Required sections present for this phase
    # Phase-specific checks via phase parameter:
    #   - component_schema: all common properties retained, types defined
    #   - composition_format: binding rules for all types, overrides defined
    #   - output_format: resolution rules, quality requirements
    #   - component_artifacts: key uniqueness, filename pattern validity,
    #     NO CONFLICTS with existing global artifact registry (artifact_keys.py)
    #   - domain_steps: routing validity, output type consistency,
    #     review/approval design present if output_type=documented_versioned
    #   - runtime_standard: all phases consolidated, identity correct
    #   - operational_workflow: steps reference standard, prompts exist

@action
def validate_package(job_dir, context):
    """Phase 9: validate the complete workflow package."""
    # All files present (workflow.toml, context_extensions.py, actions.py, prompts/)
    # TOML parse validity, Python syntax
    # Identity consistency across all files
    # Standards/ directory exists with correct filename
    # Specs/ directory exists with embedded builder spec
    # Prompt placeholder vs required_inputs consistency
    # Bidirectional artifact consistency (prompt ↔ workflow.toml)
```

### 6.6 Base Schema Sync Strategy (Resolved)

**Path reference, not embedding.** Prompts use `{BASE_COMPOSITION_STANDARD}`
placeholder resolved at runtime to the file path. The meta-builder reads the
current version at execution time — no embedding, no copying.

**Version guard:** The validate action checks minimum version:

```python
MIN_BASE_SCHEMA_VERSION = "2.0"
```

If the base schema version is below minimum, validation fails with a clear error.
This ensures AMB v2 prompts always work with the schema they expect.

---

## 7. Identity Locking

### 7.1 Runtime Spec Identity Fields

Every runtime spec must declare:

```yaml
## Workflow Identity

standard_name: "CODEBASE_TO_META_STANDARD"
standard_version: "1.0.0"
standard_filename: "CODEBASE_TO_META_STANDARD-v1.md"
```

These values are the single source of truth for all downstream artifacts.

### 7.2 Identity Propagation Chain

```
WORKFLOW_SPEC_FILE (identity fields)
    → analyze_spec (extract identity + output type)
        → component_schema (uses domain name)
            → composition_format (uses domain name)
                → output_format (uses domain name)
                    → runtime_standard (standard_name from spec)
                        → operational_workflow (workflow name from spec)
                            → package (all identity from spec)
```

### 7.3 Forbidden Content (all prompts)

- Do NOT use the builder's name (`ar_meta_builder_v1`) as the workflow name
- Do NOT use the builder's standard name (`AR_META_BUILDER_STANDARD`)
- Do NOT copy the builder's step structure (9 phases, 22 steps)
- Do NOT hardcode component types — derive from spec via base schema fine-tuning
- Do NOT assume documented/versioned output — check spec's output type

---

## 8. Comparison with Previous Builders

| Aspect | v1 | v2/v3 | AMB v1 | AMB v2 |
|---|---|---|---|---|
| Spec analysis | Yes (analyze_spec) | No | No | **Yes (Phase 1)** |
| Component types | Inferred from spec | Hardcoded 8 | Hardcoded 8 | **Fine-tuned from base** |
| Workflow structure | Spec-driven | Fixed 7-phase | Fixed 9-phase | **Spec-driven (9 phases)** |
| TDD approach | None | None | None | **DNA — every phase has test criteria + critic** |
| Phase pattern | Ad hoc | Fixed | Fixed | **Standardized 5-step TDD pattern** |
| Identity | From spec | From builder | From builder | **From spec (locked)** |
| Standard name | N/A | Builder's name | Builder's name | **From spec** |
| Standard filename | N/A | COMPOSITION_STANDARD.md | COMPOSITION_STANDARD.md | **Domain-based + version** |
| Gatekeeper | LLM only | LLM only | LLM only | **Critic (test quality) + Validate (structural) + Gatekeep (pass/fail)** |
| Validate action | None | None | None | **Single parameterized** |
| Runtime standard | N/A | N/A | Phase 6 (after workflow) | **Phase 7 (before workflow)** |
| Component artifacts | Part of define_artifacts | Implicit | Implicit | **Explicit phase** |
| Output type | Assumed documented | Assumed documented | Assumed documented | **Spec-declared (documented or direct)** |
| Recursive awareness | No | No | No | **Yes — output = parent's input** |
| Base schema sync | N/A | N/A | N/A | **Path reference + version guard** |

---

## 9. Status and Next Steps

### Current Status: DESIGN RESOLVED — READY FOR SPEC

### Design Phase (Completed)

- [x] Problem analysis (AMB v1 run review)
- [x] Pattern discovery (all 21 workflows surveyed)
- [x] Recursive composition insight (AMB output = ByProduct output structurally)
- [x] Output type distinction (documented/versioned vs direct)
- [x] Design vision (10-phase pipeline with dual gatekeeper)
- [x] Base Component Schema identified (`COMPOSITION_SYSTEM_STANDARD.md`)
- [x] Fine-tuning analogy confirmed (AI model specialization)
- [x] **Base schema revised to v2** (2026-08-09) — added fine-tuning protocol, output delivery types, recursive composition, identity contract
- [x] **Open questions resolved** (2026-08-09):
  - TDD is DNA, not a phase — standardized 5-step pattern auto-applied to all phases
  - Pipeline: 9 phases (analyze_spec → component_schema → composition_format → output_format → component_artifacts → domain_steps → runtime_standard → operational_workflow → package)
  - Three-tier quality gate per phase: Critic (test quality) + Validate (structural) + Gatekeep (pass/fail)
  - Validate actions: `validate_input_spec` (Phase 1 pre-step) + `validate_design_artifact` (Phases 2-8) + `validate_package` (Phase 9)
  - Base schema sync: path reference with `{BASE_COMPOSITION_STANDARD}` placeholder + version guard
- [x] **Gap analysis completed** (2026-08-09) — 5 gaps found and fixed:
  - G1: Phase 1 pre-step `validate_input_spec` — rejects specs missing identity/output_type
  - G2: Phase 5 validate includes artifact key conflict check against global registry
  - G3: Phase 6 explicitly designs target workflow's review/approval/promote (for documented type)
  - G4: Phase 9 includes self-bootstrap embedding (AMB v2 spec → Specs/ for AMB v3)
  - G5: Phase 1 generates meta-test-criteria — cross-phase invariants injected into all gatekeepers

### Implementation Phase (Next)

- [ ] Write AMB v2 composition system spec (input for workflow_builder)
- [ ] Write detailed prompt templates for each phase (8 prompts)
- [ ] Implement `validate_design_artifact` action
- [ ] Create `workflow.toml` with 8-phase step structure (~24 steps)
- [ ] Create `context_extensions.py` with new artifact keys
- [ ] Add identity fields to `codebase_to_meta_v1.md` spec
- [ ] Run AMB v2 against codebase_to_meta_v1 spec
- [ ] Verify generated workflow has correct identity and structure

---

## 10. References

- AMB v1 job review: `~/.ukbe-runner/jobs/20260809/ar_meta_builder_v1/AMB-ai99miop/`
- Base Component Schema: `docs/repo/workflow_builder/current/COMPOSITION_SYSTEM_STANDARD.md`
- Builder Requirements: `docs/repo/workflow_builder/current/BUILDER_REQUIREMENTS.md`
- Workflow Builder v2 Plan: `docs/repo/workflow_builder/WORKFLOW_BUILDER_V2_PLAN.md`
- V4 Bootstrap Summary: `docs/repo/workflow_builder/V4_BOOTSTRAP_SUMMARY.md`
- All workflow specs: `docs/repo/workflow_builder/specs/`
