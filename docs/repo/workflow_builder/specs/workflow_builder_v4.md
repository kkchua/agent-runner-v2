# Composition System Specification: Workflow Builder v4

> **Domain:** Self-bootstrapping meta-meta workflow builder
> **Input to:** workflow_builder_v3 (the meta-meta builder)
> **Standard:** WORKFLOW_BUILDER_STANDARD v1.0.0 (v3's own standard)
> **Bootstraps from:** workflow_builder_v3 → generates v4

---

## 1. Domain Overview

**Domain name:** `workflow_builder`
**Label:** Workflow Builder v4
**Job prefix:** `WBUILD4`
**Description:** Self-bootstrapping meta-meta builder that generates meta builders (agents) with complete 3-part output. Each generated meta builder includes its own composition standard, its own spec in Specs/, and a fully executable workflow package. v4 can process its own spec to generate v5.

### 1.1 Purpose

Workflow Builder v4 is the **production-ready evolution** of v3. It addresses three gaps discovered during the v3 bootstrap run (WBUILD2-4qpaocdy):

1. **Promotion gap** — v2's promote action didn't copy Standards/ and Specs/ directories. v4 enforces 3-part promotion at the action level.
2. **Self-bootstrapping gap** — v3 described self-bootstrapping but didn't implement it. v4 embeds its own spec in Specs/ and validates the bootstrap chain.
3. **Dynamic discovery gap** — v3 hardcoded component types in prompts. v4 reads component types from the generated composition standard dynamically.

**Key Innovation:** v4 is the first version that can **fully bootstrap itself** — feed v4's own spec (from its Specs/ folder) back into v4 to generate v5, with zero manual intervention.

**Three-Part Output (enforced):**
1. `Standards/COMPOSITION_STANDARD.md` — The composition standard for the generated meta builder
2. `Specs/{builder_name}.md` — The builder's own spec (enables self-bootstrapping)
3. Workflow package — workflow.toml, prompts/, actions.py, context_extensions.py, README.md

**Multi-Level Architecture:**
```
Level 0: v4 builder (creates agents, self-bootstrapping)
Level 1: Agent Workflow Spec (composition standard per agent)
Level 2: User Workflows (composition specs per use case)
Level 3: Agent execution outputs (deliverables)
```

**Trigger:** User provides a composition system spec describing a meta builder.

**Outcome:** Three outputs, all promoted correctly:
1. `Standards/COMPOSITION_STANDARD.md` — Composition standard
2. `Specs/{builder_name}.md` — Builder's own spec (copied from WORKFLOW_SPEC_FILE)
3. Workflow package — Executable workflow with all files

### 1.2 Key Differences from v3

| Aspect | v3 | v4 |
|--------|----|----|
| Promotion | Standards/Specs/ copied only if v3's actions.py runs | **Enforced** — promote action always copies 3-part output |
| Self-bootstrapping | Described but not implemented | **Implemented** — embed_builder_spec step copies own spec to Specs/ |
| Component discovery | Hardcoded in prompts (8 types) | **Dynamic** — reads from generated COMPOSITION_STANDARD.md |
| Artifact declarations | Some steps missing WORKFLOW_SPEC_FILE | **Complete** — all prompts match workflow.toml declarations |
| Validation | 9 checks | **11 checks** — adds Specs/ content check and prompt-input full coverage |
| Bootstrap chain | v3 → v4 (manual) | **v4 → v5 (automatic)** — Specs/workflow_builder_v4.md is the input |

### 1.3 Lessons from WBUILD2-4qpaocdy

| Issue | Root Cause | v4 Fix |
|-------|-----------|--------|
| PROMPT_INPUT_MISMATCH | 2 prompts referenced {WORKFLOW_SPEC_FILE} but step didn't declare it | All steps that use {WORKFLOW_SPEC_FILE} declare it in required_inputs |
| STEP_CONTRACT_MISMATCH | refine_package produced STANDARDS_COMPOSITION_STANDARD_FILE but it wasn't in produces list | Both generate_package and refine_package declare it in produces |
| Missing Standards/Specs/ in promoted output | v2's promote action ran (not v3's), v2 didn't know about these dirs | promote action explicitly copies Standards/ and Specs/; validate checks they exist |
| OUTPUT_COMPOSITION_SPEC.md untracked | LLM generated extra file not in artifact registry | Strict artifact key discipline; all outputs must have a registered key |

---

## 2. Component Schema (Layer 1)

### 2.1 Component Types

v4 inherits the same 8 component types as v3. The key difference is **discovery**: v4 reads these types from the generated composition standard dynamically rather than hardcoding them.

| Component Type | Purpose | Required? | Cardinality |
|---|---|---|---|
| `step_definition` | A workflow step with type, purpose, inputs, outputs | Yes | Ordered list |
| `role_policy` | Coder role assignment for a step | Yes | Singleton per step |
| `routing_pattern` | How steps connect (success, reject, refine) | Yes | Singleton per step |
| `prompt_pattern` | Prompt structure elements | No | Unordered set per prompt step |
| `artifact_contract` | Input/output artifact definitions | Yes | Unordered set |
| `composition_standard` | The composition standard schema for the generated meta builder | Yes | Singleton |
| `output_variance` | A specific output configuration | No | Unordered set |
| `domain_spec` | A user-provided spec type the builder processes | No | Unordered set |

### 2.2 Dynamic Discovery Mechanism

**NEW in v4.** Instead of hardcoding the 8 component types in prompts, v4 discovers them from the generated composition standard:

```python
def discover_component_types(standard_path: Path) -> list[str]:
    """Parse COMPOSITION_STANDARD.md to extract component type names.
    
    Reads the YAML frontmatter field `component_type_count` and
    scans for '#### Type N:' headings in the Component Schema section.
    Returns list of type names found.
    """
```

**How it works:**
1. After `generate_composition_standard` step completes, the COMPOSITION_STANDARD_FILE is available
2. Subsequent steps (generate_meta_composition_spec, generate_package) read this file
3. The `discover_component_types()` function in context_extensions.py parses the standard
4. Discovered types are injected into prompt context as `{DISCOVERED_COMPONENT_TYPES}`
5. Prompts use this dynamic list instead of hardcoded type names

**Fallback:** If discovery fails (malformed standard), fall back to the 8 base types from the v3 standard.

### 2.3 Common Properties

Same as v3 — 5 required common properties (component_id, component_type, name, version, description) + 3 optional (duration_range, platforms, tags).

### 2.4 Validation Rules

Same 14 rules as v3 (VR-001 through VR-014), plus:

| Rule ID | Rule |
|---|---|
| VR-015 | Every step that references {WORKFLOW_SPEC_FILE} in its prompt MUST declare WORKFLOW_SPEC_FILE in required_inputs |
| VR-016 | Both generate_package and refine_package MUST declare STANDARDS_COMPOSITION_STANDARD_FILE in produces |

---

## 3. Composition Format (Layer 2)

### 3.1 Composition Structure

Same as v3 with one new binding:

| Field | Type | Required | Description |
|---|---|---|---|
| `builder_name` | string | Yes | Unique builder identifier |
| `builder_label` | string | Yes | Human-readable display name |
| `job_prefix` | string | Yes | 4-6 character prefix |
| `builder_purpose` | string | Yes | What this builder solves |
| `workflow_pattern` | enum | Yes | Pattern type |
| `step_bindings` | array | Yes | Ordered step definitions |
| `artifact_bindings` | object | Yes | Artifact contracts |
| `composition_standard_binding` | object | Yes | The composition standard |
| `output_variances` | array | No | Output configurations |
| `self_bootstrap_binding` | object | **NEW** | Self-bootstrapping configuration (see 3.6) |

### 3.2 Binding Rules

Same 8 bindings as v3, plus:

| Binding Name | Component Type | Cardinality | Required? | Description |
|---|---|---|---|---|
| `self_bootstrap` | domain_spec | Singleton | Yes | **NEW** — References the builder's own spec for self-bootstrapping |

### 3.3 Workflow Patterns

Same 6 patterns as v3. v4 uses `meta_meta_builder` pattern with the additional `embed_builder_spec` step.

### 3.4 Self-Bootstrap Binding (NEW in v4)

The `self_bootstrap_binding` defines how the builder references its own spec for bootstrapping the next version:

| Field | Type | Required | Description |
|---|---|---|---|
| `bootstrap_spec_key` | string | Yes | Artifact key that holds the builder's own spec (always "WORKFLOW_SPEC_FILE") |
| `bootstrap_spec_target` | string | Yes | Where to embed in output (always "Specs/{builder_name}.md") |
| `bootstrap_version` | string | Yes | Current builder version (e.g., "4.0.0") |
| `next_version_pattern` | string | Yes | How to derive next version (e.g., "increment_major") |

**Example:**
```yaml
self_bootstrap_binding:
  bootstrap_spec_key: "WORKFLOW_SPEC_FILE"
  bootstrap_spec_target: "Specs/workflow_builder_v4.md"
  bootstrap_version: "4.0.0"
  next_version_pattern: "increment_major"
```

**Purpose:** This binding tells the builder: "Take the spec you were given as input (WORKFLOW_SPEC_FILE), and embed it in your output's Specs/ folder. This enables the next version to use it as input."

### 3.5 Placeholder Resolution

Same 3 data sources as v3, plus:

| Data Source | Fields Provided | Required? |
|---|---|---|
| Discovery | DISCOVERED_COMPONENT_TYPES, COMPOSITION_STANDARD_PATH | Yes (computed at runtime) |

---

## 4. Output Format (Layer 3)

### 4.1 3-Part Output Structure (Enforced)

```
{builder_name}/
├── Standards/
│   └── COMPOSITION_STANDARD.md     # Part 1: Composition standard
├── Specs/
│   └── {builder_name}.md           # Part 2: Builder's own spec (self-bootstrap)
├── workflow.toml                    # Part 3: Workflow package
├── context_extensions.py
├── actions.py
├── prompts/
│   └── NN_{step_name}.txt
├── README.md
├── .env.sample                      # Conditional
└── config.json.sample               # Conditional
```

### 4.2 Promotion Contract (NEW in v4)

**NEW in v4.** The promote_workflow_package action MUST copy all 3 parts:

| Source | Target | Mandatory? |
|--------|--------|-----------|
| `output/workflow.toml` | `workflows/{slug}/workflow.toml` | Yes |
| `output/context_extensions.py` | `workflows/{slug}/context_extensions.py` | Yes |
| `output/actions.py` | `workflows/{slug}/actions.py` | If exists |
| `output/README.md` | `workflows/{slug}/README.md` | Yes |
| `output/prompts/` | `workflows/{slug}/prompts/` | Yes |
| `output/Standards/` | `workflows/{slug}/Standards/` | **Yes (enforced)** |
| `output/Specs/` | `workflows/{slug}/Specs/` | **Yes (enforced)** |
| `output/.env.sample` | `workflows/{slug}/.env.sample` | If exists |
| `output/config.json.sample` | `workflows/{slug}/config.json.sample` | If exists |

**Enforcement:** If Standards/ or Specs/ is missing from the output, the promote action REJECTS with a clear error message. This prevents the v3 gap where these directories were silently skipped.

### 4.3 Resolution Rules

Same 7 rules as v3 (RR-001 through RR-007), plus:

| Rule ID | Source | Target |
|---|---|---|
| RR-008 | self_bootstrap_binding | Specs/{builder_name}.md (copy of WORKFLOW_SPEC_FILE) |
| RR-009 | DISCOVERED_COMPONENT_TYPES | All prompt templates (dynamic type lists) |

### 4.4 Quality Requirements

Same 8 rules as v3 (QR-001 through QR-008), plus:

| Rule ID | Requirement | Severity |
|---|---|---|
| QR-009 | Standards/ directory exists and contains COMPOSITION_STANDARD.md | CRITICAL |
| QR-010 | Specs/ directory exists and contains at least one .md file | CRITICAL |
| QR-011 | All prompt {PLACEHOLDERS} are declared in their step's required_inputs or produces | CRITICAL |
| QR-012 | Both generate_package and refine_package declare STANDARDS_COMPOSITION_STANDARD_FILE | CRITICAL |

---

## 5. Operational Requirements

### 5.1 Workflow Phases (9 phases)

v4 has 9 phases — same as v3, with Phase 8 enhanced to include the embed_builder_spec step:

| Phase | Purpose | v3→v4 Change |
|---|---|---|
| **1. Foundation (TDD Loop)** | Generate test criteria, review, refine | No change |
| **2. Component Schema (Layer 1)** | Generate + gatekeep component schema | No change |
| **3. Composition Format (Layer 2)** | Generate + gatekeep composition format | No change |
| **4. Output Format (Layer 3)** | Generate + gatekeep output format | No change |
| **5. Operational Workflow** | Generate + gatekeep operational workflow | No change |
| **6. Composition Standard** | Generate + gatekeep composition standard | No change |
| **7. Meta Composition Spec** | Generate meta composition spec | No change |
| **8. Package Assembly** | Generate package, **embed builder spec**, validate, gatekeep, review, refine | **Enhanced** — embed_builder_spec step added between generate and validate |
| **9. Promotion** | Promote 3-part output to workflows/ | **Enhanced** — enforces Standards/ + Specs/ |

### 5.2 New Step: `embed_builder_spec`

**NEW in v4.** This action step copies the input spec (WORKFLOW_SPEC_FILE) into the output's Specs/ folder:

| Property | Value |
|---|---|
| Step name | `embed_builder_spec` |
| Step type | action |
| Input | `WORKFLOW_SPEC_FILE`, `WORKFLOW_MANIFEST_FILE` (to locate output dir) |
| Output | `SPECS_BUILDER_SPEC_FILE` (the embedded spec at `output/Specs/{builder_name}.md`) |
| Position | After `generate_package`, before `validate_package_deterministic` |

**Implementation:**
```python
@action("embed_builder_spec")
def embed_builder_spec(*, context, state, step_cfg, project_root):
    """Copy the input spec into the output Specs/ folder."""
    spec_path = Path(context["WORKFLOW_SPEC_FILE"])
    output_dir = Path(context["WORKFLOW_MANIFEST_FILE"]).parent
    specs_dir = output_dir / "Specs"
    specs_dir.mkdir(exist_ok=True)
    target = specs_dir / f"{spec_path.stem}.md"
    shutil.copy2(spec_path, target)
    return ActionResult(
        status="APPROVED",
        remark=f"Embedded builder spec at {target}",
        artifacts={"SPECS_BUILDER_SPEC_FILE": str(target)},
    )
```

**Purpose:** Ensures every generated meta builder has its own spec in Specs/, enabling the self-bootstrapping loop. When the generated builder is run again, its Specs/ folder already contains the spec that created it.

### 5.3 Enhanced validate_package_deterministic (11 checks)

v4 adds 2 new validation checks to v3's 9:

| Check # | Description | NEW? |
|---|---|---|
| 1 | TOML parse validity of workflow.toml | |
| 2 | Python syntax of context_extensions.py and actions.py | |
| 3 | TYPE_CHECKING runtime import detection | |
| 4 | Artifact binding consistency | |
| 5 | Action step implementation completeness | |
| 6 | Prompt file existence | |
| 7 | Prompt placeholder vs required_inputs consistency | |
| 8 | context_extensions.py artifact key coverage | |
| 9 | Standards/COMPOSITION_STANDARD.md existence | |
| 10 | **Specs/ directory exists and contains at least one .md file** | **NEW** |
| 11 | **All prompt {PLACEHOLDERS} fully declared in step artifacts (bidirectional)** | **NEW** |

**Check 10 detail:** Validates that the embed_builder_spec step ran successfully and Specs/ has content.

**Check 11 detail:** Unlike v3's check 7 which only checked prompt→workflow direction, v4's check 11 also verifies workflow→prompt direction (every artifact in required_inputs/produces that looks like a placeholder IS referenced in the prompt). This catches both missing declarations AND unused declarations.

### 5.4 Enhanced promote_workflow_package

v4's promote action enforces 3-part promotion:

```python
copy_dirs = ["prompts", "Standards", "Specs"]

# Enforcement: reject if Standards/ or Specs/ missing
for required_dir in ["Standards", "Specs"]:
    src = source_dir / required_dir
    if not src.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"Required output directory '{required_dir}/' not found. "
                   f"v4 requires 3-part output: Standards/, Specs/, workflow files.",
            reject_code="MISSING_REQUIRED_OUTPUT_DIR",
        )
```

### 5.5 Dynamic Discovery in Prompts

**NEW in v4.** The generate_package prompt includes:

```
DYNAMIC COMPONENT DISCOVERY:
Read the generated composition standard at:
  {COMPOSITION_STANDARD_FILE}

Extract the component type list from the "Component Types" section.
Use ONLY the types found in the standard. Do NOT hardcode component types.
If the standard defines N types, your workflow.toml must reference exactly those N types.

Discovered types will be available as: {DISCOVERED_COMPONENT_TYPES}
```

The context_extensions.py provides:
```python
def discover_component_types(standard_path: str) -> str:
    """Parse COMPOSITION_STANDARD.md and return comma-separated type list."""
    # Parse frontmatter for component_type_count
    # Scan for "#### Type N: type_name" headings
    # Return "step_definition, role_policy, routing_pattern, ..."
```

### 5.6 Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `WORKFLOW_SPEC_FILE` | Composition system specification | Yes |

### 5.7 Output Artifacts

| Artifact Key | Description | Produced By | v3→v4 Change |
|---|---|---|---|
| `TEST_CRITERIA_FILE` | Acceptance criteria | generate_test_criteria | |
| `REVIEW_TEST_CRITERIA_FILE` | Review of criteria | review_test_criteria | |
| `COMPONENT_SCHEMA_FILE` | Component schema Layer 1 | generate_component_schema | |
| `GATEKEEP_COMPONENT_SCHEMA_FILE` | Gatekeep review | gatekeep_component_schema | |
| `COMPOSITION_FORMAT_FILE` | Composition format Layer 2 | generate_composition_format | |
| `GATEKEEP_COMPOSITION_FORMAT_FILE` | Gatekeep review | gatekeep_composition_format | |
| `OUTPUT_FORMAT_FILE` | Output format Layer 3 | generate_output_format | |
| `GATEKEEP_OUTPUT_FORMAT_FILE` | Gatekeep review | gatekeep_output_format | |
| `OPERATIONAL_WORKFLOW_FILE` | Operational workflow design | generate_operational_workflow | |
| `GATEKEEP_OPERATIONAL_WORKFLOW_FILE` | Gatekeep review | gatekeep_operational_workflow | |
| `COMPOSITION_STANDARD_FILE` | Composition standard | generate_composition_standard | |
| `GATEKEEP_COMPOSITION_STANDARD_FILE` | Gatekeep review | gatekeep_composition_standard | |
| `META_COMPOSITION_SPEC_FILE` | Meta composition spec | generate_meta_composition_spec | |
| `WORKFLOW_MANIFEST_FILE` | workflow.toml | generate_package | |
| `WORKFLOW_EXTENSIONS_FILE` | context_extensions.py | generate_package | |
| `WORKFLOW_ACTIONS_FILE` | actions.py | generate_package | |
| `WORKFLOW_PROMPTS_INDEX_FILE` | prompts index | generate_package | |
| `WORKFLOW_README_FILE` | README.md | generate_package | |
| `STANDARDS_COMPOSITION_STANDARD_FILE` | Standards/COMPOSITION_STANDARD.md | generate_package | Declared in both generate_package AND refine_package produces |
| `SPECS_BUILDER_SPEC_FILE` | **Specs/{builder_name}.md** | **embed_builder_spec** | **NEW** |
| `VALIDATION_REPORT_FILE` | Validation report | validate_package_deterministic | |
| `GATEKEEP_PACKAGE_FILE` | Gatekeep review | gatekeep_package | |
| `REVIEW_FILE_SUGGESTED` | Final review | review_package | |
| `WORKFLOW_PACKAGE_DIR_FILE` | Promote result | promote_workflow_package | |

### 5.8 Action Steps

Three custom action steps (v3 had 2):

| Action | Purpose | v3→v4 Change |
|---|---|---|
| `validate_package_deterministic` | Static analysis (11 checks) | **Added checks 10, 11** |
| `embed_builder_spec` | **Copy spec to Specs/** | **NEW** |
| `promote_workflow_package` | Deploy 3-part output | **Enforces Standards/ + Specs/** |

### 5.9 Domain-Specific Requirements

All v3 requirements inherited, plus:

- **Self-bootstrapping enforced:** Every generated meta builder MUST have its own spec in Specs/. The embed_builder_spec action ensures this.
- **Dynamic discovery mandatory:** generate_package and generate_meta_composition_spec prompts MUST use {DISCOVERED_COMPONENT_TYPES} instead of hardcoded type lists.
- **Promotion completeness:** The promote action MUST copy all 3 parts. Missing Standards/ or Specs/ causes rejection.
- **Bidirectional artifact consistency:** Every {PLACEHOLDER} in a prompt must be declared in the step's artifacts, AND every artifact in the step's artifacts that looks like a placeholder must appear in the prompt.
- **Bootstrap chain integrity:** The spec in Specs/ must be identical to the WORKFLOW_SPEC_FILE that was the input. This enables the next version to use it as input.

---

## 6. Step Sequence

v4 has 22 steps across 10 phases:

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

Phase 8: Package Assembly
  15 generate_package → 16 embed_builder_spec → 17 validate_package_deterministic
  → 18 gatekeep_package → 19 review_package → [20 refine_package]

Phase 9: Promotion
  21 promote_workflow_package → 22 step_completion
```

**Key routing change from v3:** `embed_builder_spec` (step 16) sits between `generate_package` and `validate_package_deterministic`. This ensures the Specs/ directory exists before validation runs (so check 10 can verify it).

---

## 7. Self-Bootstrapping: v4 → v5

v4 can generate v5 by feeding its own spec back into itself:

```
1. v4 is installed at workflows/workflow_builder_v4/
2. v4's Specs/ contains workflow_builder_v4.md (embedded by embed_builder_spec)
3. Submit workflow_builder_v4.md as WORKFLOW_SPEC_FILE to workflow_builder_v4
4. v4 processes the spec → generates workflow_builder_v5/
   - Standards/COMPOSITION_STANDARD.md (v5's standard)
   - Specs/workflow_builder_v4.md (embedded copy of input)
   - workflow.toml, prompts/, actions.py, context_extensions.py, README.md
5. Promote workflow_builder_v5 to workflows/workflow_builder_v5/
6. v5 can now bootstrap v6 using its own Specs/ copy
```

**Bootstrap invariant:** Every version N embeds its own spec in Specs/. Version N+1 is generated from that embedded spec. The chain is unbroken.

---

## 8. References

- **v3 Composition Standard:** `workflows/workflow_builder_v3/Standards/COMPOSITION_STANDARD.md`
- **v3 Spec:** `docs/repo/workflow_builder/specs/workflow_builder_v3.md`
- **v3 Run Output:** `docs/repo/workflow_builder/runs/WBUILD2-4qpaocdy/output/`
- **Base Composition Standard:** `docs/repo/composition_standard/COMPOSITION_SYSTEM_STANDARD.md`
- **Current workflow_builder_v2:** `workflows/workflow_builder_v2/`
- **Meta-Workflow Builder Architecture:** `docs/repo/workflow_builder/standards/META_WORKFLOW_BUILDER_ARCHITECTURE.md`

---

**End of Specification**
