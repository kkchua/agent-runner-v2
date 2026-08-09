# Workflow Builder v4 Bootstrap Summary

**Created:** 2026-08-10  
**Spec Location:** `docs/repo/workflow_builder/specs/workflow_builder_v4.md`  
**Input To:** workflow_builder_v2 (for generation) or workflow_builder_v4 (for self-bootstrapping)

---

## What is v4?

Workflow Builder v4 is the **production-ready evolution** of v3 that addresses three critical gaps discovered during the v3 bootstrap run (WBUILD2-4qpaocdy):

1. **Promotion Gap** — v2's promote action didn't copy Standards/ and Specs/ directories
2. **Self-Bootstrapping Gap** — v3 described but didn't implement self-bootstrapping
3. **Dynamic Discovery Gap** — v3 hardcoded component types in prompts

---

## Three Key Improvements

### 1. Fix Promotion + 3-Part Output Declaration

**Problem:** v2's promote action only copied `prompts/` directory, missing `Standards/` and `Specs/`.

**Solution:**
- `promote_workflow_package` action explicitly copies all 3 parts: `Standards/`, `Specs/`, and workflow files
- All steps that reference `{WORKFLOW_SPEC_FILE}` declare it in `required_inputs` (fixes PROMPT_INPUT_MISMATCH)
- `STANDARDS_COMPOSITION_STANDARD_FILE` declared in both `generate_package` and `refine_package` produces (fixes STEP_CONTRACT_MISMATCH)
- New validation check 10: verify `Specs/` directory exists and contains at least one .md file
- New validation check 11: bidirectional artifact consistency (prompt↔workflow.toml)

**Files Modified:**
- `actions.py` — Enhanced `promote_workflow_package` with enforcement
- `workflow.toml` — All steps declare complete artifact lists
- `validate_package_deterministic` — Added checks 10 and 11

### 2. Full Self-Bootstrapping Loop

**Problem:** v3 described self-bootstrapping but didn't implement it. The builder's own spec wasn't embedded in the output.

**Solution:**
- New step: `embed_builder_spec` — copies `WORKFLOW_SPEC_FILE` to `output/Specs/{builder_name}.md`
- New artifact: `SPECS_BUILDER_SPEC_FILE` — the embedded spec
- New composition binding: `self_bootstrap_binding` — defines bootstrap configuration
- Validation check 10 ensures `Specs/` has content before promotion

**Bootstrap Chain:**
```
v4's Specs/workflow_builder_v4.md → feed into v4 → generates v5
v5's Specs/workflow_builder_v5.md → feed into v5 → generates v6
... (unbroken chain)
```

**Files Modified:**
- `actions.py` — New `embed_builder_spec` action
- `workflow.toml` — Step 16: embed_builder_spec (between generate_package and validate)
- `context_extensions.py` — New artifact key `SPECS_BUILDER_SPEC_FILE`

### 3. Dynamic Component Discovery from Standard

**Problem:** v3 hardcoded 8 component types in prompts. Adding a new type required editing prompts.

**Solution:**
- New function: `discover_component_types(standard_path)` — parses `COMPOSITION_STANDARD.md` to extract type list
- generate_package prompt uses `{DISCOVERED_COMPONENT_TYPES}` placeholder instead of hardcoded list
- context_extensions.py injects discovered types into prompt context at runtime
- Fallback: if discovery fails, use v3's 8 base types

**How It Works:**
1. After `generate_composition_standard` completes, `COMPOSITION_STANDARD_FILE` is available
2. `discover_component_types()` parses the standard's frontmatter and headings
3. Discovered types injected as `{DISCOVERED_COMPONENT_TYPES}`
4. Prompts use dynamic list: "Use ONLY the types found in the standard. Do NOT hardcode."

**Files Modified:**
- `context_extensions.py` — New `discover_component_types()` function
- `prompts/15_generate_package.txt` — Uses `{DISCOVERED_COMPONENT_TYPES}`
- `prompts/14_generate_meta_composition_spec.txt` — Uses `{DISCOVERED_COMPONENT_TYPES}`

---

## v4 Spec Structure (490 lines)

| Section | Content |
|---------|---------|
| 1. Domain Overview | Purpose, 3 improvements, lessons from WBUILD2-4qpaocdy |
| 2. Component Schema | 8 component types + dynamic discovery mechanism |
| 3. Composition Format | Bindings + self_bootstrap_binding (NEW) |
| 4. Output Format | 3-part output + promotion contract (ENFORCED) |
| 5. Operational Requirements | 9 phases, 22 steps, 3 actions, 11 validation checks |
| 6. Step Sequence | Visual routing diagram |
| 7. Self-Bootstrapping | v4 → v5 bootstrap chain |
| 8. References | Links to v3 standard, v3 spec, v3 run output |

---

## v4 Workflow: 22 Steps, 9 Phases

```
Phase 1: Foundation (TDD Loop)
  01 generate_test_criteria → 02 review_test_criteria → [03 refine_test_criteria]

Phase 2: Component Schema (Layer 1)
  04 generate_component_schema → 05 gatekeep_component_schema

Phase 3: Composition Format (Layer 2)
  06 generate_composition_format → 07 gatekeep_composition_format

Phase 4: Output Format (Layer 3)
  08 generate_output_format → 09 gatekeep_output_format

Phase 5: Operational Workflow
  10 generate_operational_workflow → 11 gatekeep_operational_workflow

Phase 6: Composition Standard (v3 Innovation)
  12 generate_composition_standard → 13 gatekeep_composition_standard

Phase 7: Meta Composition Spec (v3 Innovation)
  14 generate_meta_composition_spec

Phase 8: Package Assembly (ENHANCED)
  15 generate_package → 16 embed_builder_spec (NEW) → 17 validate_package_deterministic
  → 18 gatekeep_package → 19 review_package → [20 refine_package]

Phase 9: Promotion (ENHANCED)
  21 promote_workflow_package → 22 step_completion
```

---

## Validation: 11 Checks (v3 had 9)

| # | Check | NEW? |
|---|-------|------|
| 1 | TOML parse validity | |
| 2 | Python syntax | |
| 3 | TYPE_CHECKING runtime import detection | |
| 4 | Artifact binding consistency | |
| 5 | Action step implementation completeness | |
| 6 | Prompt file existence | |
| 7 | Prompt placeholder vs required_inputs consistency | |
| 8 | context_extensions.py artifact key coverage | |
| 9 | Standards/COMPOSITION_STANDARD.md existence | |
| 10 | **Specs/ directory exists and contains .md file** | **NEW** |
| 11 | **Bidirectional artifact consistency (prompt↔workflow)** | **NEW** |

---

## How to Generate v4

### Use workflow_builder_v3 (The Meta-Meta Builder)

```bash
# Submit v4 spec to v3 (the meta-meta builder)
ukbe-run-agent submit \
  --template-group workflow_builder_v3 \
  --artifact WORKFLOW_SPEC_FILE=docs/repo/workflow_builder/specs/workflow_builder_v4.md
```

**Expected Output:**
- `workflows/workflow_builder_v4/` — Complete workflow package
- `workflows/workflow_builder_v4/Standards/COMPOSITION_STANDARD.md` — v4's composition standard
- `workflows/workflow_builder_v4/Specs/workflow_builder_v4.md` — Embedded spec (self-bootstrap)

**Why v3?** v3 is the meta-meta builder designed to generate meta builders with 3-part output (Standards/, Specs/, workflow). Using v2 would miss the Standards/ and Specs/ directories because v2's promote action doesn't know about them.

### Self-Bootstrap: v4 → v5 (After v4 is Generated)

```bash
# v4 generates v5 using its own embedded spec
ukbe-run-agent submit \
  --template-group workflow_builder_v4 \
  --artifact WORKFLOW_SPEC_FILE=workflows/workflow_builder_v4/Specs/workflow_builder_v4.md
```

---

## Conformance to v3 Standard

The v4 spec conforms to v3's `WORKFLOW_BUILDER_STANDARD v1.0.0`:

✅ **Layer 1 (Component Schema):** 8 component types, common properties, validation rules (VR-001 to VR-016)  
✅ **Layer 2 (Composition Format):** Composition structure, binding rules, self_bootstrap_binding  
✅ **Layer 3 (Output Format):** 3-part output, promotion contract, resolution rules (RR-001 to RR-009)  
✅ **Quality Requirements:** QR-001 to QR-012 (v3 had QR-001 to QR-008)

---

## Lessons from WBUILD2-4qpaocdy (Addressed)

| Issue | Root Cause | v4 Fix |
|-------|-----------|--------|
| PROMPT_INPUT_MISMATCH | 2 prompts referenced `{WORKFLOW_SPEC_FILE}` but step didn't declare it | VR-015 + QR-011 + Check 11 |
| STEP_CONTRACT_MISMATCH | refine_package produced `STANDARDS_COMPOSITION_STANDARD_FILE` but it wasn't in produces | VR-016 + explicit declaration in both generate_package and refine_package |
| Missing Standards/Specs/ in promoted output | v2's promote action didn't know about these dirs | Section 4.2 promotion contract + Section 5.4 enforcement |
| OUTPUT_COMPOSITION_SPEC.md untracked | LLM generated extra file not in artifact registry | Strict artifact key discipline (Section 5.7) |

---

## Next Steps

1. **Review the spec** — Read `docs/repo/workflow_builder/specs/workflow_builder_v4.md`
2. **Generate v4** — Submit the spec to workflow_builder_v2
3. **Verify 3-part output** — Check that Standards/, Specs/, and workflow files are all present
4. **Test self-bootstrap** — Feed v4's embedded spec back into v4 to generate v5
5. **Iterate** — Each version improves on the previous (v5 → v6 → ...)

---

## References

- **v4 Spec:** `docs/repo/workflow_builder/specs/workflow_builder_v4.md`
- **v3 Spec:** `docs/repo/workflow_builder/specs/workflow_builder_v3.md`
- **v3 Standard:** `workflows/workflow_builder_v3/Standards/COMPOSITION_STANDARD.md`
- **v3 Run Output:** `docs/repo/workflow_builder/runs/WBUILD2-4qpaocdy/output/`
- **Base Composition Standard:** `docs/repo/composition_standard/COMPOSITION_SYSTEM_STANDARD.md`

---

**Status:** ✅ READY FOR GENERATION
