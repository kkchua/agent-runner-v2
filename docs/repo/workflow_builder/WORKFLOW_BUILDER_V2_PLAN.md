# Workflow Builder v2 Implementation Plan

> **Status:** DRAFT
> **Created:** 2026-08-07
> **Approach:** Rewrite from scratch using Composition System Standard + Meta-Workflow Builder Architecture

---

## 1. Overview

**Goal:** Create `workflow_builder_v2` — a meta-workflow builder that follows the Composition System Standard and Meta-Workflow Builder Architecture.

**Key Decisions:**
1. **Coexist** with v1 (not replace)
2. **Rewrite from scratch** using the new standards (not migrate v1 code)
3. **Full composition support** — v2 is purely composition-based, ignore v1's traditional workflow concept
4. **Location:** `workflows/workflow_builder_v2/`

**What v2 Builds:**
- Component schemas (following Composition System Standard)
- Composition formats (YAML-based assembly instructions)
- Output assemblers (resolve compositions into deliverables)
- Complete composition-based workflow packages

**What v2 Does NOT Build:**
- Traditional workflow packages (workflow.toml, prompts, actions.py)
- That's v1's job

---

## 2. Architecture

### 2.1 Meta-Workflow Skeleton

v2 follows the universal meta-workflow execution flow:

```
Phase 1: Foundation (TDD Loop)
├── generate_test_criteria         — Define acceptance criteria for composition workflows
├── review_test_criteria           — Review criteria quality
└── refine_test_criteria           — Fix issues (conditional)

Phase 2: Requirements
├── generate_requirements          — Define component schema + composition format + output format
├── gatekeep_requirements          — Validate requirements completeness
└── [review/refine if needed]

Phase 3: Artifacts
├── generate_artifacts             — Define artifact contract (component library, compositions, outputs)
├── gatekeep_artifacts             — Validate artifact contract
└── [review/refine if needed]

Phase 4: Steps
├── generate_steps                 — Define step architecture (scan, plan, generate, review)
├── gatekeep_steps                 — Validate step design
└── [review/refine if needed]

Phase 5: Package
├── generate_package               — Generate complete composition workflow package
├── gatekeep_package               — Validate package completeness
├── review_package                 — Comprehensive quality review
└── refine_package                 — Fix issues (conditional, loops)

Phase 6: Promotion
├── promote                        — Deploy to workflows/ directory
└── stepCompletion                 — Terminal step
```

### 2.2 Step Implementations

Each step implements the step interface from the Meta-Workflow Builder Architecture standard.

**Generation Steps:**
- `generate_test_criteria` — Generates test criteria for composition workflows
- `generate_requirements` — Generates component schema, composition format, output format
- `generate_artifacts` — Generates artifact contract (COMPONENT_LIBRARY_DIR, COMPOSITIONS_DIR, OUTPUT_FILE, etc.)
- `generate_steps` — Generates step architecture for the target composition workflow
- `generate_package` — Generates complete workflow package (workflow.toml, context_extensions.py, actions.py, prompts/)

**Gatekeeper Steps:**
- `gatekeep_requirements` — Validates component schema completeness, composition format, output format
- `gatekeep_artifacts` — Validates artifact contract (all keys registered, paths correct)
- `gatekeep_steps` — Validates step architecture (scan, plan, generate, review steps present)
- `gatekeep_package` — Validates package completeness (all files present, aligned)

**Review/Refine Steps:**
- `review_package` — Comprehensive review (component schema quality, composition format, output structure, downstream contracts)
- `refine_package` — Fix issues found in review

**Promotion Step:**
- `promote` — Copy workflow package to `workflows/{workflow_name}/`

### 2.3 Input/Output

**Input:**
- `WORKFLOW_SPEC` — Specification for the composition workflow to build (following Composition System Standard)

**Output:**
- Complete workflow package for a composition-based workflow:
  - `workflow.toml` — Workflow manifest
  - `context_extensions.py` — Artifact key registration, context injection
  - `actions.py` — Component scanning, composition resolution, output assembly
  - `prompts/*.txt` — Prompt templates for generation/review steps
  - `README.md` — User guide
  - `.env.sample` — Environment variables (if needed)
  - `config.json.sample` — Runtime config (if needed)

---

## 3. Implementation Phases

### Phase 1: Scaffold (Current)

**Goal:** Create the workflow directory structure and basic files.

**Tasks:**
1. Create `workflows/workflow_builder_v2/` directory
2. Create `workflow.toml` with the meta-workflow skeleton
3. Create `context_extensions.py` with artifact key registration
4. Create placeholder `actions.py`
5. Create `prompts/` directory with placeholder files
6. Create `README.md`

**Deliverables:**
- Basic workflow structure that can be loaded by the runner
- All artifact keys registered
- Step sequence defined

### Phase 2: Prompts

**Goal:** Write comprehensive prompts for each step.

**Tasks:**
1. Write `01_generate_test_criteria.txt` — Instructions for generating test criteria
2. Write `02_review_test_criteria.txt` — Review checklist for test criteria
3. Write `03_refine_test_criteria.txt` — Refinement rules
4. Write `04_generate_requirements.txt` — Instructions for generating component schema, composition format, output format
5. Write `05_gatekeep_requirements.txt` — Validation questions for requirements
6. Write `06_generate_artifacts.txt` — Instructions for generating artifact contract
7. Write `07_gatekeep_artifacts.txt` — Validation questions for artifacts
8. Write `08_generate_steps.txt` — Instructions for generating step architecture
9. Write `09_gatekeep_steps.txt` — Validation questions for steps
10. Write `10_generate_package.txt` — Instructions for generating complete package
11. Write `11_gatekeep_package.txt` — Validation questions for package
12. Write `12_review_package.txt` — Comprehensive review checklist
13. Write `13_refine_package.txt` — Refinement rules

**Deliverables:**
- All prompt templates written
- Self-critic sections included
- Domain-specific instructions for composition workflows

### Phase 3: Actions

**Goal:** Implement custom actions for composition workflow generation.

**Tasks:**
1. Implement `scan_components` action — Scan component library, validate schema
2. Implement `resolve_compositions` action — Resolve composition references, apply overrides
3. Implement `assemble_output` action — Generate resolved output
4. Implement `validate_component_schema` action — Validate component schema conformance
5. Implement `validate_composition_format` action — Validate composition format
6. Implement `promote_composition_workflow` action — Deploy workflow package

**Deliverables:**
- All actions implemented
- Error handling included
- ActionResult returns correct

### Phase 4: Testing

**Goal:** Test v2 with real composition workflow specs.

**Tasks:**
1. Test with `video_campaign_manuscript_v1` spec
2. Verify generated workflow package is complete
3. Run the generated workflow with sample components/compositions
4. Verify output quality

**Deliverables:**
- v2 successfully builds video_campaign_manuscript_v1
- Generated workflow runs correctly
- Output manuscripts are high quality

### Phase 5: Documentation

**Goal:** Document v2 usage and architecture.

**Tasks:**
1. Complete README.md with usage instructions
2. Document the step implementation interface
3. Provide examples of domain-specific step implementations
4. Document the factory pattern

**Deliverables:**
- Comprehensive README
- Developer guide for creating new domain builders
- Example implementations

---

## 4. Key Differences from v1

| Aspect | v1 | v2 |
|--------|----|----|
| **Purpose** | Build traditional workflows | Build composition-based workflows |
| **Output** | workflow.toml + prompts + actions.py | Component schema + composition resolver + output assembler |
| **Step Implementations** | Traditional workflow logic | Composition system logic |
| **Prompts** | Focus on workflow structure | Focus on component schema, composition format, output format |
| **Gatekeepers** | Validate workflow structure | Validate component schema conformance, composition format |
| **Review** | Check workflow quality | Check component quality, composition resolution, output completeness |
| **Domain** | Traditional workflows | Composition System Standard |

---

## 5. Success Criteria

v2 is successful when:

1. **Functional:** Can build a complete composition-based workflow from a spec
2. **Quality:** Generated workflows produce high-quality outputs
3. **Stable:** No crashes, handles edge cases gracefully
4. **Documented:** Clear usage instructions and developer guide
5. **Tested:** Validated with at least one real composition workflow spec

---

## 6. Risks and Mitigations

**Risk 1: Complexity**
- v2 is more complex than v1 (component schema validation, composition resolution, output assembly)
- **Mitigation:** Start with simple composition workflows, iterate to complex ones

**Risk 2: Prompt Quality**
- Prompts need to be very clear about component schema, composition format, output format
- **Mitigation:** Include extensive examples in prompts, self-critic sections

**Risk 3: Action Implementation**
- Composition resolution logic is non-trivial (reference expansion, override merging, placeholder filling)
- **Mitigation:** Start with simple resolution, add complexity incrementally

**Risk 4: Testing**
- Need sample components and compositions to test
- **Mitigation:** Create sample component library and compositions for video_campaign_manuscript_v1

---

## 7. Timeline

**Phase 1 (Scaffold):** 1 day
**Phase 2 (Prompts):** 2-3 days
**Phase 3 (Actions):** 2-3 days
**Phase 4 (Testing):** 1-2 days
**Phase 5 (Documentation):** 1 day

**Total:** 7-10 days

---

## 8. Next Steps

1. **Get approval** on this plan
2. **Start Phase 1** — Create workflow directory structure
3. **Iterate** through phases 2-5
4. **Validate** with video_campaign_manuscript_v1 spec

---

**End of Plan**
