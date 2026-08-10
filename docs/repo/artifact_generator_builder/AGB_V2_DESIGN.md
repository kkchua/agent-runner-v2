---
title: "Artifact Generator Builder v2 — Design Document"
version: "2.0"
date: "2026-08-10"
status: "IMPLEMENTED"
supersedes: "ar_meta_builder_v1"
---

# Artifact Generator Builder v2 — Design Document

> **Status:** IMPLEMENTED (2026-08-10)
> **Created:** 2026-08-09
> **Updated:** 2026-08-10
> **Supersedes:** ar_meta_builder_v1 (current)
> **Base Composition Standard:** `docs/system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v1.0.md`

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

### 1.3 Missing Deliverables

The AMB v1 workflow never instructed the LLM to produce:
- A master specification document
- A generator-specific composition standard
- A default runtime implementation

The composition standard only listed 3 outputs informally. The requirement docs had no codename field. The promote action only copied workflow package files.

### 1.4 Root Cause

The AMB v1 prompts enforce a **fixed output template** — the 9-phase composition
system structure is hardcoded into the prompt instructions. The LLM never had the
flexibility to design a workflow suited to the target domain. It could only fill in
the template with domain-specific content.

This defeats the purpose of the composition standard and meta composition spec —
they're supposed to be the **target's** LEGO catalog and assembly manual, not a
description of the AMB's own structure.

---

## 2. Pattern Discovery — Studying All Workflows

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

## 3. Core Design Principles

### 3.1 Three Required Deliverables

Every AGB-generated generator MUST produce three deliverables:

| # | Deliverable | Artifact Key | Purpose |
|---|---|---|---|
| 1 | Composition Standard | `COMPOSITION_STANDARD_FILE` | Generator-specific composition rules (derived from base standard) |
| 2 | Default Runtime Impl | `DEFAULT_IMPL_FILE` | Self-contained default implementation of all transformation stages |
| 3 | Workflow Package | (multiple keys) | Executable workflow package (workflow.toml, context_extensions.py, actions.py, prompts/, README.md) |

### 3.2 Codename Versioning

The codename is **assigned in the requirement doc's YAML frontmatter**, not generated by the LLM:

```yaml
---
codename: "text_summarizer"
title: "Simple Text Summarizer"
---
```

The codename is used for:
- File naming: `{codename}_MASTER_SPEC.md`, `{codename}_COMPOSITION_STANDARD.md`
- Promote target: `workflows/{codename}/`
- Identity throughout all generated artifacts

### 3.3 Composition Standard Section 10 — Single Source of Truth

All enforcement rules for AGB-generated generators are defined in **BASE_COMPOSITION_STANDARD_v1.0.md Section 10**:

- **10.1 Required Deliverables** — The three deliverables table
- **10.2 Required Generator File Structure** — `workflows/{codename}/` layout
- **10.3 AGB Run Behavior** — All artifacts go to `runs/{job_id}/` during AGB run
- **10.4 Factory Workflow Phases** — Phase descriptions
- **10.5 Example** — Complete example structure
- **10.6 Self-Bootstrap** — How generators can be self-bootstrapped

Prompts reference Section 10 with **MANDATORY** enforcement language. Rules are NOT repeated across prompts.

### 3.4 Requirement Docs Describe Content, Not Artifact Keys

Requirement docs describe **WHAT** the input and output content is like. The LLM decides **HOW** to implement it, including:
- Artifact key names
- Implementation approach
- Transformation algorithms

Example (correct):
```markdown
## Input Artifacts
- Source text document (plain text or markdown)

## Output Artifacts
- Condensed summary (10-20% of original length)
- Key points list (bullet-point extraction)
```

Example (incorrect — prescribing implementation):
```markdown
## Input Artifacts
- INPUT_TEXT_FILE: path to input text

## Output Artifacts
- SUMMARY_FILE: path to summary output
- Extension Points: HTML → PDF conversion
```

### 3.5 Run-Time vs Publish-Time Paths

**During AGB run:** ALL artifacts go to `docs/repo/artifact_generator_builder/runs/{job_id}/`

**After promote:** Deliverables are packaged into `workflows/{codename}/`:
```
workflows/{codename}/
├── workflow.toml
├── context_extensions.py
├── actions.py
├── README.md
├── standards/
│   └── COMPOSITION_STANDARD.md
└── impls/
    └── default.impl.md
```

---

## 4. AGB v2 Pipeline

### 4.1 Seven Phases

The AGB v2 pipeline uses 7 phases (simplified from the original 9-phase design):

```
Phase 1: Analyze Requirement
         → Domain analysis (identity, components, output type, natural phases)

Phase 2: Design Composition Spec
         → Composition spec for the target generator

Phase 3: Design Runtime Implementation
         → Runtime implementation design + default implementation deliverable

Phase 4: Define Artifacts
         → Artifact keys and filename patterns for the target generator

Phase 5: Design Steps
         → Step sequence following spec's natural phases + output delivery

Phase 6: Generate Package + Deliverables
         → Complete workflow package + Composition Standard

Phase 7: Promote Package
         → Package all 3 deliverables into workflows/{codename}/
```

### 4.2 Phase Details

#### Phase 1: Analyze Requirement

**Pre-step: validate_input_spec (action)**
Before any generation, deterministically validate the requirement doc has the minimum
required fields. If this fails → AWAITING_INTERVENTION (cannot proceed).
- Codename field present in YAML frontmatter
- Title and overview present
- At least one input and one output artifact described

**Then TDD pattern:**
Read the requirement doc. Understand the domain, identify natural components, lock
identity fields. Generate **meta-test-criteria** —
cross-phase invariants that ALL subsequent phase gatekeepers must verify:
- Generated workflow uses codename from requirement doc, not builder's identity
- Generated workflow structure matches requirement doc's domain, not AGB's structure
- All three deliverables are produced
- Composition Standard Section 10 is followed

**Artifact:** Domain analysis document with identity, component inventory,
natural workflow phases, meta-test-criteria.

#### Phase 2: Design Composition Spec

Design the composition spec for the target generator. This defines how the generator's
components bind together — binding rules, override mechanism, placeholder resolution.

**Artifact:** Composition spec document.

#### Phase 3: Design Runtime Implementation

Design the runtime implementation and produce the **DEFAULT_IMPL_FILE** deliverable.
This is a self-contained implementation of all transformation stages.

**Produces TWO files:**
- `RUNTIME_IMPL_FILE` — Intermediate runtime implementation design (in `runs/{job_id}/output/`)
- `DEFAULT_IMPL_FILE` — Deliverable default implementation (in `runs/{job_id}/output/runtime_impls/default.impl.md`)

**MANDATORY:** Must follow Composition Standard Section 10. REJECT if DEFAULT_IMPL_FILE is missing or codename is wrong.

#### Phase 4: Define Artifacts

Define the specific artifact keys for the target domain. Each artifact key maps
to a filename pattern. This ensures the generated workflow has proper artifact
tracking.

**Validate includes conflict check:** The validate action checks artifact keys
against the existing global registry (`artifact_keys.py`) and known workflow
keys. Flag any collisions with system-level or existing workflow keys.

**Artifact:** Artifact contract (key → filename pattern → description).

#### Phase 5: Design Steps

Design the workflow steps that follow the spec's natural domain phases. NOT the
AGB's fixed structure — the target's own phases.

**Output delivery design (based on output type):**
- **Documented/versioned:** Must design the target's own review loops, approval
  gates (`requires_human_approval_after`), promote actions, and archive steps.
- **Direct:** No review/approval/promote. Just produce. May include human
  approval *before* expensive operations (e.g., API calls).

**Artifact:** Step sequence document (step names, types, routing, role policies,
artifact bindings, delivery mechanism).

#### Phase 6: Generate Package + Deliverables

Generate the complete executable workflow package AND the remaining deliverable:

**Part A: Workflow Package (5 files)**
- `WORKFLOW_MANIFEST_FILE` — workflow.toml with correct codename
- `WORKFLOW_EXTENSIONS_FILE` — context_extensions.py with domain-specific class
- `WORKFLOW_ACTIONS_FILE` — actions.py with domain-specific actions
- `WORKFLOW_PROMPTS_DIR` — prompts/ directory (one per prompt-driven step)
- `WORKFLOW_README_FILE` — README.md describing the target workflow

**Part B: Deliverable (1 file)**
- `COMPOSITION_STANDARD_FILE` — Generator-specific composition standard ({codename}_COMPOSITION_STANDARD.md)

**MANDATORY:** Must follow Composition Standard Section 10. REJECT if any of the 3 deliverables is missing.

#### Phase 7: Promote Package

Package all 3 deliverables into `workflows/{codename}/`:

**Promote action (`promote_workflow_package`):**
- Workflow package → `workflows/{codename}/` (root files)
- Composition standard → `workflows/{codename}/standards/`
- Default impl → `workflows/{codename}/impls/`

Creates subdirectories as needed. Reads codename from workflow.toml manifest name field.

### 4.3 Standardized Step Template

Every phase (1-6) instantiates this template with phase-specific content:

| Step | Type | Role | Purpose |
|------|------|------|---------|
| `generate_{phase}` | Prompt | Coder | Produce the phase deliverable |
| `review_{phase}` | Prompt | Critic | Review for completeness and correctness |
| `[refine_{phase}]` | Prompt | Coder | Fix issues (on reject, max N) |
| `gatekeep_{phase}` | Prompt | Gatekeeper | Final gatekeep — pass/fail with evidence |

**Phase 1 special:** Has a pre-step `validate_input_spec` (action) that runs
BEFORE the TDD pattern. Also generates meta-test-criteria as part of its output.

**Phase 3 special:** Produces TWO files (RUNTIME_IMPL_FILE + DEFAULT_IMPL_FILE).

**Phase 6 special:** Produces TWO files (workflow package + COMPOSITION_STANDARD_FILE).

**Phase 7 special:** Action-driven (promote_workflow_package), not prompt-driven.

**Meta-test-criteria propagation:** Phase 1's meta-test-criteria are injected
into ALL subsequent phases' gatekeep prompts. Every gatekeeper checks both the
phase-specific criteria AND the cross-phase meta-test-criteria.

**Refine loops:** Both review and gatekeep have refine loops with
exhaustion handling (`exhausted_failure_code` + `HUMAN_RETRY_REQUIRED`).

---

## 5. Identity Locking

### 5.1 Codename as Identity

Every requirement doc MUST declare a codename in YAML frontmatter:

```yaml
---
codename: "text_summarizer"
title: "Simple Text Summarizer"
---
```

The codename is the single source of truth for all downstream artifacts.

### 5.2 Identity Propagation Chain

```
REQUIREMENT_DOC (codename field)
    → analyze_requirement (extract codename + domain)
        → design_composition_spec (uses codename)
            → design_runtime_impl (uses codename)
                → define_artifacts (uses codename)
                    → design_steps (uses codename)
                        → generate_package (all files use codename)
                            → promote_package (workflows/{codename}/)
```

### 5.3 Forbidden Content (all prompts)

- Do NOT use the builder's name (`artifact_generator_builder`) as the workflow name
- Do NOT copy the builder's step structure (7 phases)
- Do NOT hardcode component types — derive from requirement doc
- Do NOT let the LLM generate the codename — read it from the requirement doc
- Do NOT repeat enforcement rules in prompts — reference BASE_COMPOSITION_STANDARD_v1.0.md Section 10

---

## 6. Enforcement Strategy

### 6.1 MANDATORY Language

All prompts use **MANDATORY** enforcement language when referencing BASE_COMPOSITION_STANDARD_v1.0.md Section 10:

```markdown
# MANDATORY: BASE_COMPOSITION_STANDARD_v1.0.md Section 10

You MUST verify compliance with BASE_COMPOSITION_STANDARD_v1.0.md Section 10 ({BASE_COMPOSITION_STANDARD}). REJECT if:
- Any of the three required deliverables is missing (Section 10.1)
- File names or directory structure do not match (Section 10.2)
- Codename "{CODENAME}" is not used consistently
- Builder identity is referenced anywhere
```

### 6.2 Single Source of Truth

All enforcement rules are defined in **BASE_COMPOSITION_STANDARD_v1.0.md Section 10**, NOT repeated across prompts. Prompts reference the standard, they don't duplicate it.

### 6.3 Review and Gatekeep REJECT Conditions

Review and gatekeep steps explicitly state REJECT conditions:
- Missing deliverables
- Wrong file names or structure
- Codename not used consistently
- Builder identity leakage

---

## 7. Comparison with Previous Builders

| Aspect | v1 | v2/v3 | AMB v1 | AGB v2 |
|---|---|---|---|---|
| Spec analysis | Yes (analyze_spec) | No | No | **Yes (Phase 1)** |
| Component types | Inferred from spec | Hardcoded 8 | Hardcoded 8 | **Derived from requirement doc** |
| Workflow structure | Spec-driven | Fixed 7-phase | Fixed 9-phase | **Spec-driven (7 phases)** |
| Identity | From spec | From builder | From builder | **From requirement doc codename** |
| Deliverables | Workflow package | Workflow package | Workflow package | **3 deliverables (Composition Standard, Default Impl, Workflow Package)** |
| Promote target | workflows/{name}/ | workflows/{name}/ | workflows/{name}/ | **workflows/{codename}/ with subdirectories** |
| Enforcement | LLM only | LLM only | LLM only | **BASE_COMPOSITION_STANDARD_v1.0.md Section 10 + MANDATORY language** |
| Requirement doc | Defines artifact keys | Defines artifact keys | Defines artifact keys | **Describes content only (LLM decides keys)** |
| Runtime impl | Single file | Single file | Single file | **Directory (RUNTIME_IMPL_DIR) with default.impl.md** |

---

## 8. Implementation Status

### Current Status: IMPLEMENTED (2026-08-10)

### Completed

- [x] Problem analysis (AMB v1 run review)
- [x] Pattern discovery (all 21 workflows surveyed)
- [x] Three deliverables design (Composition Standard, Default Impl, Workflow Package)
- [x] Codename versioning (from requirement doc frontmatter)
- [x] BASE_COMPOSITION_STANDARD_v1.0.md Section 10 (single source of truth)
- [x] Promote action (packages into workflows/{codename}/ with subdirectories)
- [x] Requirement doc rewrite (describes content, not artifact keys)
- [x] MANDATORY enforcement language in all prompts
- [x] RUNTIME_IMPL_DIR (directory for multiple implementations)
- [x] All artifacts go to runs/{job_id}/ during AGB run
- [x] context_extensions.py with codename resolution
- [x] workflow.toml with 7-phase step structure
- [x] actions.py with promote_workflow_package action

### Pending

- [ ] RUNTIME_IMPL_FILE → RUNTIME_IMPL_DIR rename in context_extensions.py (file locked)
- [ ] Bootstrap publish (user will do manually)
- [ ] Run init to propagate to global runner home
- [ ] Re-submit AGB job to verify all 4 deliverables are produced correctly

---

## 9. References

- Base Composition Standard: `docs/system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v1.0.md`
- AGB workflow: `workflows/artifact_generator_builder/`
- AGB requirement docs: `workflows/artifact_generator_builder/Specs/`
