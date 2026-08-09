# AMB v2 Redesign — Artifact Generator Builder

> **Status:** DESIGN COMPLETE
> **Created:** 2026-08-10
> **Updated:** 2026-08-10
> **Purpose:** Complete redesign of AR Meta Builder v2 as an Artifact Generator Builder

---

## 1. Executive Summary

**AMB = Artifact Generator Builder**

AMB builds artifact generators — workflows that transform input content into output artifacts following a consistent, mandatory pattern:

```
Input → Composition Spec → Runtime Implementation → Output
```

This pattern applies to ALL generators, including AMB itself (self-bootstrap).

---

## 2. Problems with Current Design

### 2.1 Identity Leakage
- Prompts reference "AR Meta Builder v2" and "AMB_STANDARD" directly
- LLM falls back to AMB's own 48-step structure instead of creating target-specific structure
- Forbidden content sections are not sufficient to prevent leakage

### 2.2 Broken Artifact Key References
- Prompts used `{WORKFLOW_SPEC_FILE}` but artifact key was renamed to `BOOTSTRAP_SPEC_FILE`
- Placeholders were not resolved → LLM had no input spec content
- `SPECS_BUILDER_SPEC_FILE` was removed but still referenced in prompts
- `BASE_COMPOSITION_STANDARD` pointed to non-existent path

### 2.3 Misaligned Deliverables
- Bootstrap spec defines 3 deliverables: master spec, default impl, workflow package
- Current prompts only produce workflow package
- No step produces `MASTER_SPEC_FILE` or `DEFAULT_IMPL_FILE`
- No codename concept in prompts

### 2.4 Wrong Phase Count
- Prompt 01 says "8 design phases" but workflow has 9 phases (0-9)

### 2.5 Composition Standard Location
- Base `COMPOSITION_SYSTEM_STANDARD.md` was inside `docs/repo/workflow_builder/` (a workflow folder)
- Should be a governance-level standard, not workflow-specific

### 2.6 Confusing Terminology
- "Spec" used for multiple purposes (bootstrap spec, master spec, composition spec)
- "Meta-builder building meta-builders" concept was confusing
- Unclear what the output actually is

---

## 3. New Vision: Artifact Generator Builder

### 3.1 Core Concept

**AMB builds artifact generators. Artifact generators produce artifacts.**

Both AMB and artifact generators produce artifacts — just different types. This is the bootstrap concept.

### 3.2 Mandatory Pattern

ALL artifact generators MUST follow this pattern:

```
┌─────────────────────────────────────────────────────────────┐
│ Input Content                                               │
│ (files, data, codebase, images, etc.)                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Composition Spec                                            │
│ Transformation rules, meta schema, structure definition     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Runtime Implementation                                      │
│ Concrete executor that follows the composition spec         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Output Artifact                                             │
│ (report, guide, slides, PDF, another generator, etc.)       │
└─────────────────────────────────────────────────────────────┘
```

**Why mandatory?**
- Consistency: users always know how to use any generator
- Extensibility: can add more runtime implementations later
- Clarity: clear separation of "what" (spec) vs "how" (impl)

### 3.3 User Experience (Universal Interface)

```bash
# Using any artifact generator
1. Provide input (files, data, etc.)
2. Select runtime implementation (if multiple exist)
3. Run generator
4. Get output
```

This interface is consistent across ALL artifact generators.

---

## 4. AMB Workflow Structure

### 4.1 Hybrid Approach: Flexible Phases + Rigorous Validation

**From workflow_builder_v1:** Flexible, non-prescriptive phases
**From ar_meta_builder_v2:** Rigorous validation at each step

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Analyze Requirement                                │
│ ─────────────────────────────────────────────────────────── │
│ Generate → Self-Critic → Review → Validate → Gatekeep       │
│ Output: REQUIREMENT_ANALYSIS_FILE                           │
│ (Understand input content and output requirements)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Design Composition Spec                          │
│ ─────────────────────────────────────────────────────────── │
│ Generate → Self-Critic → Review → Validate → Gatekeep       │
│ Output: COMPOSITION_SPEC_FILE                               │
│ (Define transformation rules, meta schema, structure)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Design Runtime Implementation                    │
│ ─────────────────────────────────────────────────────────── │
│ Generate → Self-Critic → Review → Validate → Gatekeep       │
│ Output: RUNTIME_IMPL_FILE                                   │
│ (Default executor that follows the composition spec)        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Define Artifacts                                   │
│ ─────────────────────────────────────────────────────────── │
│ Generate → Self-Critic → Review → Validate → Gatekeep       │
│ Output: ARTIFACT_CONTRACT_FILE                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Design Steps                                       │
│ ─────────────────────────────────────────────────────────── │
│ Generate → Self-Critic → Review → Validate → Gatekeep       │
│ Output: STEP_SEQUENCE_FILE                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 6: Generate Package                                   │
│ ─────────────────────────────────────────────────────────── │
│ Generate → Self-Critic → Review → Validate → Gatekeep       │
│ Output: workflow.toml, context_extensions.py, actions.py,   │
│         prompts/, README.md                                 │
│ (Must implement: input → composition spec → runtime → output)│
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 7: Promote Package                                    │
│ ─────────────────────────────────────────────────────────── │
│ Backup → Copy to target locations                           │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Validation at Each Phase

Every phase includes:
- **Generate:** LLM creates the artifact
- **Self-Critic:** LLM reviews its own work
- **Review:** Second LLM challenges the output
- **Validate:** Deterministic checks (file existence, syntax, etc.)
- **Gatekeep:** Final approval before proceeding

This ensures quality without constraining creativity.

---

## 5. Self-Bootstrap Concept

### 5.1 AMB Can Bootstrap Itself

AMB's own process follows the same pattern:

```
AMB's Input: Requirement doc (for any generator)
     ↓
AMB's Composition Spec: How to build artifact generators (meta-level)
     ↓
AMB's Runtime Implementation: AMB's workflow steps
     ↓
AMB's Output: Artifact generator (workflow package)
```

### 5.2 The Recursive Pattern

| Level | Input | Composition Spec | Runtime Impl | Output |
|-------|-------|------------------|--------------|--------|
| **AMB** | Requirement doc | How to build generators | AMB workflow steps | Artifact generator |
| **Generated Generator** | Domain content | How to transform content | Generator workflow steps | Domain artifact |

### 5.3 AMB's Composition Spec (Meta-Level)

```
"To build a generator:
 1. Analyze the requirement
 2. Design a composition spec for the target domain
 3. Design a runtime implementation
 4. Assemble the workflow package"
```

### 5.4 Generated Generator's Composition Spec (Object-Level)

```
"To produce the target artifact:
 1. Load the input content
 2. Transform using these rules
 3. Produce the output"
```

---

## 6. Design Decisions

### 6.1 Composition System Standard → Governance
- **Decision:** Move `COMPOSITION_SYSTEM_STANDARD.md` to `docs/system/00_governance/foundation/current/`
- **Rationale:** It's a foundational standard for all composition systems, not specific to any workflow
- **Runtime path:** `{GOVERNANCE_RUNTIME_ROOT}/COMPOSITION_SYSTEM_STANDARD.md`
- **Context extension:** `BASE_COMPOSITION_STANDARD` resolves via `get_governance_runtime_root()`

### 6.2 Terminology Clarification
- **Requirement Doc:** Input to AMB (specifies what generator to build)
- **Composition Spec:** Transformation rules (what AMB produces for the target generator)
- **Runtime Implementation:** Concrete executor (what AMB produces for the target generator)
- **Artifact Generator:** The output workflow (what AMB produces)

### 6.3 Mandatory Pattern
- ALL generators follow: input → composition spec → runtime impl → output
- Even if only 1 output type, still use the pattern
- Ensures consistency and extensibility

### 6.4 Codename Versioning (Retained)
- Development versions use `{workflow_name}_{codename}` (e.g., `ar_meta_builder_einstein`)
- Future CLI promotes to `{workflow_name}_v{version}`
- Codename is shared across all deliverables

---

## 7. Implementation Plan

### 7.1 Move Composition Standard
- [ ] Move `COMPOSITION_SYSTEM_STANDARD.md` to `docs/system/00_governance/foundation/current/`
- [ ] Update `context_extensions.py` to use `get_governance_runtime_root()`
- [ ] Run bootstrap-publish to sync to global runner home

### 7.2 Rewrite Workflow Structure
- [ ] Update `workflow.toml` with new 7-phase structure
- [ ] Remove rigid 9-phase composition system pattern
- [ ] Add phases for composition spec and runtime impl design

### 7.3 Rewrite Prompts
- [ ] Remove all "AR Meta Builder v2" and "AMB_STANDARD" references
- [ ] Update prompts for new phase structure
- [ ] Focus on "artifact generator" concept
- [ ] Ensure prompts reference `BOOTSTRAP_SPEC_FILE` (not `WORKFLOW_SPEC_FILE`)
- [ ] Add self-critic sections to all prompts

### 7.4 Update Context Extensions
- [ ] Fix `BASE_COMPOSITION_STANDARD` path
- [ ] Update artifact keys for new structure
- [ ] Ensure all keys are properly registered

### 7.5 Update Actions
- [ ] Fix `WORKFLOW_SPEC_FILE` → `BOOTSTRAP_SPEC_FILE` references
- [ ] Update validation logic for new structure

### 7.6 Sync Bootstrap
- [ ] Run `run-bootstrap-publish.bat`
- [ ] Run `run-init.bat`
- [ ] Test the new AMB workflow

---

## 8. Files to Change

| File | Change |
|------|--------|
| `docs/system/00_governance/foundation/current/COMPOSITION_SYSTEM_STANDARD.md` | Move here from `docs/repo/workflow_builder/standards/` |
| `workflows/ar_meta_builder_v2/workflow.toml` | Rewrite with 7-phase structure |
| `workflows/ar_meta_builder_v2/context_extensions.py` | Fix paths, update artifact keys |
| `workflows/ar_meta_builder_v2/prompts/*.txt` | Rewrite all prompts for new structure |
| `workflows/ar_meta_builder_v2/actions.py` | Fix artifact key references |
| `workflows/ar_meta_builder_v2/Specs/bootstrap.spec.md` | Update for new terminology |

---

## 9. Success Criteria

The new AMB is successful if:
1. ✅ It can build artifact generators that follow the mandatory pattern
2. ✅ Generated generators have clear composition specs and runtime implementations
3. ✅ Users can use any generator with the universal interface (load input + select impl → output)
4. ✅ AMB can bootstrap itself using the same pattern
5. ✅ No identity leakage (AMB's structure doesn't leak into generated generators)
6. ✅ All phases have rigorous validation (self-critic, review, validate, gatekeep)
7. ✅ Composition standard is properly located in governance and referenced at runtime

---

## 10. Key Insights

1. **AMB is a creative designer, not a template filler** — it brainstorms the best architecture for each requirement
2. **The composition spec + runtime impl pattern is mandatory** — ensures consistency across all generators
3. **Flexible phases + rigorous validation** — best of both worlds (workflow_builder_v1 + ar_meta_builder_v2)
4. **Self-bootstrap is elegant** — same pattern at every level (meta and object)
5. **Universal user interface** — users always know how to use any generator

---

## 11. Notes from Discussion

### 2026-08-10
- User wants to rethink the whole AMB structure
- Rename from "meta-builder" to "Artifact Generator Builder"
- Composition standard should be under governance folder
- Runtime should refer to global path like other governance docs
- Current prompts cause LLM to copy AMB's 48-step structure
- Need full rewrite of prompts for artifact generator concept
- Mandatory pattern: input → composition spec → runtime impl → output
- All generators must follow this pattern for consistency
- AMB can bootstrap itself using the same pattern
- Hybrid approach: flexible phases (workflow_builder_v1) + rigorous validation (ar_meta_builder_v2)
