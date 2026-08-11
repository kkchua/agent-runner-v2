# Artifact Generator Builder — Design Document

> **Status:** v3 REDESIGN (2026-08-14)
> **Created:** 2026-08-09
> **Updated:** 2026-08-14
> **Base Composition Standard:** `docs/system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v1.0.md` (v2.0)

---

## 1. Core Insight

**AGB is just another artifact pipeline.** Same pattern as agnes_media_gen_v1 or any SDLC workflow:

```
requirement.md  →  [AGB: actions + LLM]  →  workflow_package/
workflow_package/  →  [AGB: actions + LLM]  →  another_workflow_package/
```

Input artifact A → AGB Generator (actions + LLM) → output artifact B.

**The infrastructure is already predefined.** step_runner, routing, artifact system, WorkflowExtensions, @action, workflow.toml schema — all fixed. The LLM should NOT "design" any of this.

## 2. What the LLM Generates (Only 2 Things)

1. **actions.py** — domain-specific action logic
2. **Prompt .txt files** — domain-specific LLM instructions

## 3. What is Assembled Mechanically (No LLM)

- **workflow.toml** — step sequence, routing, artifact bindings
- **context_extensions.py** — artifact key registration, path resolution
- **impl.yaml** — implementation override files
- **README.md** — generated during promote step

The `assemble_package` action reads the Analysis JSON and produces all structural files deterministically.

## 4. Pipeline (10 Steps)

```
1.  analyze_requirement  (prompt)  — Read requirement doc, produce Analysis JSON
2.  plan_domain_logic    (prompt)  — Design what actions + prompts are needed
3.  challenge_plan       (prompt)  — Attack the plan: missing edges, weak validations
    ↕ refine loop (max 2)
4.  implement_domain     (prompt)  — Write actions.py + prompt .txt files
5.  critic_impl          (prompt)  — Review code logic + prompt quality
    ↕ refine loop (max 2)
6.  assemble_package     (ACTION)  — Build workflow.toml + context_extensions.py + impl.yaml
7.  review_package       (prompt)  — Holistic review of assembled package
8.  validate_structure   (ACTION)  — Deterministic structural validation
9.  gatekeep_package     (prompt)  — Final pass/fail gate
10. promote_package      (ACTION)  — Deploy + generate README.md
```

### SDLC Quality Flow

| Phase | Steps | Pattern |
|-------|-------|---------|
| Analysis | 1 | Understand domain |
| Plan ↔ Challenge | 2 ↔ 3 | Design domain logic, then attack it |
| Implement ↔ Critic | 4 ↔ 5 | Write code + prompts, then review them |
| Execution | 6 | Assemble package |
| Review → Validate → Gatekeep | 7–9 | Quality gates |
| Promote → Publish | 10 | Deploy |

### Scope of Quality Gates

All review, validation, and gatekeep steps focus **only on domain logic**:

| Gate | Reviews | Does NOT Review |
|------|---------|-----------------|
| challenge_plan | Missing edge cases, weak validations, wrong artifact bindings | Workflow structure (predefined) |
| critic_impl | Code logic, error handling, prompt clarity, constraint enforcement | workflow.toml syntax (assembled mechanically) |
| review_package | Holistic quality of actions + prompts | Infrastructure assembly |
| validate_structure | File existence, syntax, artifact consistency | Domain logic correctness |
| gatekeep_package | Functional viability — can the workflow actually run? | Structural compliance (already validated) |

## 5. Analysis JSON Schema

The Analysis JSON is the contract between step 1 (analyze_requirement) and step 6 (assemble_package). It contains all information needed to mechanically construct structural files.

```json
{
  "identity": {
    "name": "text_summarizer_ayz",
    "job_prefix": "TXTSUM",
    "version": "1.0.0",
    "label": "Text Summarizer",
    "description": "Transforms long text into condensed output",
    "codename": "text_summarizer_ayz"
  },
  "domain_steps": [
    {
      "name": "parse_input",
      "type": "action",
      "action_name": "parse_input_document",
      "required_inputs": ["SOURCE_DOCUMENT_FILE"],
      "produces": ["PARSED_DOCUMENT"]
    },
    {
      "name": "analyze_structure",
      "type": "prompt",
      "prompt_file": "02_analyze_structure.txt",
      "role_policy": "architect_standard",
      "required_inputs": ["PARSED_DOCUMENT"],
      "produces": ["ANALYSIS_RESULT"]
    }
  ],
  "artifact_keys": {
    "inputs": [{"key": "SOURCE_DOCUMENT_FILE", "pattern": "input/{filename}"}],
    "intermediate": [{"key": "PARSED_DOCUMENT", "pattern": "intermediate/PARSED_DOCUMENT.json"}],
    "outputs": [{"key": "SUMMARY_FILE", "pattern": "output/SUMMARY_FILE.md"}]
  },
  "implementations": [
    {
      "name": "key_points",
      "description": "Produces ordered list of key points",
      "overrides": {
        "render_output": {"action": "render_list_output"}
      }
    }
  ]
}
```

## 6. Deliverables

AGB produces a single deliverable: the **workflow package**.

```
workflows/{codename}/
    workflow.toml              # assembled by action
    context_extensions.py      # assembled by action
    actions.py                 # LLM-generated
    prompts/                   # LLM-generated
        *.txt
    impls/                     # multi-impl support
        {impl_name}/
            impl.yaml          # assembled by action
            actions.py         # LLM-generated (override actions)
            prompts/           # LLM-generated (override prompts)
    README.md                  # generated during promote
```

No intermediate design documents (composition spec, runtime impl, artifact contract) are generated.

## 7. What Changed from v2

| Aspect | v2 (old) | v3 (new) |
|--------|----------|----------|
| Steps | 18 | 10 |
| LLM generates | Everything (workflow.toml, context_extensions.py, actions.py, prompts, composition standard) | Only actions.py + prompts |
| Infrastructure | LLM-designed | Predefined, assembled mechanically |
| Quality pattern | Adversarial challenge/respond/gatekeep (2 cycles) | SDLC plan↔challenge, implement↔critic |
| Intermediate docs | 5 (requirement analysis, composition spec, runtime impl, artifact contract, impl plan) | 1 (Analysis JSON) |
| Deliverables | 2 (composition standard + workflow package) | 1 (workflow package) |
| Token cost | ~280K | ~60K (estimated) |
| Duration | ~72 min | ~30 min (estimated) |

## 8. Future Extensibility

### Add Implementation to Existing Generator

```
Input: requirement doc (new impl) + existing workflow package
Output: same package + new impls/{new_name}/ directory + updated workflow.toml
```

Only the delta is generated — new impl's actions + prompts + impl.yaml. Base workflow untouched.

### Self-Bootstrap

AGB can build itself. The self-bootstrap requirement specifies:
- **Input:** Requirement documents
- **Output:** Workflow packages (per BASE_COMPOSITION_STANDARD v2.0)

## 9. References

- Base Composition Standard: `docs/system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v1.0.md`
- AGB workflow: `workflows/artifact_generator_builder/`
- AGB requirement docs: `workflows/artifact_generator_builder/Specs/`
