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
    context_extensions.py      # assembled by action (two-dict pattern)
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

### Path Convention

All workflows follow the universal `input/` and `output/{job_id}/` convention:

```
{workspace_root}/
    input/                          ← all input artifacts
    output/{job_id}/                ← all output artifacts (per-job, isolated)
```

The generated `context_extensions.py` uses two class-level dicts
(`INPUT_ARTIFACTS`, `OUTPUT_ARTIFACTS`) with universal resolvers
(`resolve_input_artifacts`, `resolve_output_artifacts`).

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

## 8. Extend Mode: Adding Implementations to Existing Workflows

AGB v3 supports **extend mode** — adding new implementations to an existing generated workflow without regenerating the entire package.

### How It Works

**Input:** 
- `REQUIREMENT_DOC` — describes the NEW implementation to add
- `EXISTING_WORKFLOW_DIR` — path to the existing workflow package (e.g., `workflows/text_summarizer/`)

**Output:** 
- Same workflow package with new `impls/{new_name}/` directory added
- Updated `workflow.toml` with new `[[workflow.implementation]]` declaration
- Existing `actions.py`, `prompts/`, `context_extensions.py` remain unchanged

### Extend Mode Pipeline

The same 10-step pipeline runs, but each step behaves differently in extend mode:

| Step | New Workflow Mode | Extend Mode |
|------|------------------|-------------|
| 1. analyze_requirement | Design full domain structure | Read existing workflow.toml, analyze ONLY new impl |
| 2. plan_domain_logic | Plan all actions + prompts | Plan ONLY new impl overrides |
| 3. challenge_plan | Challenge full domain plan | Challenge ONLY new impl design |
| 4. implement_domain | Write actions.py + prompts/ | Write ONLY `impls/{new_name}/` files |
| 5. critic_impl | Review full implementation | Review ONLY new impl files |
| 6. assemble_package | Generate all files from scratch | Copy existing files, add new impl declarations |
| 7. review_package | Review full package | Review merged package |
| 8. validate_structure | Validate new package | Validate merged package |
| 9. gatekeep_package | Gatekeep new package | Gatekeep merged package |
| 10. promote_package | Promote to workflows/ | Merge into existing workflows/ |

### Analysis JSON Schema (Extend Mode)

In extend mode, the Analysis JSON includes:

```json
{
  "identity": { ... },           // Copied from existing workflow.toml
  "domain_steps": [ ... ],       // Copied from existing workflow.toml
  "artifact_keys": { ... },      // Copied from existing workflow.toml
  "implementations": [           // ONLY the new implementation(s)
    {
      "name": "new_impl_name",
      "description": "...",
      "overrides": { ... }
    }
  ],
  "extend_mode": true            // Flag to indicate extend mode
}
```

### Implementation Details

**assemble_package (extend mode):**
1. Reads existing `workflow.toml` from `EXISTING_WORKFLOW_DIR`
2. Appends new `[[workflow.implementation]]` sections
3. Copies existing `context_extensions.py`, `actions.py`, `prompts/`
4. Copies existing `impls/` directory (if present)
5. Generates `impl.yaml` for NEW implementations only

**promote_workflow_package (extend mode):**
1. If target `workflows/{codename}/` doesn't exist, copies from existing
2. Updates `workflow.toml` with merged version (existing + new impls)
3. Merges new `impls/{new_name}/` into existing `impls/`
4. Does NOT overwrite existing `actions.py`, `prompts/`, `context_extensions.py`

### Usage Example

```bash
# Submit an extend mode job via operator console:
# - Workflow: artifact_generator_builder
# - Input artifacts:
#   - REQUIREMENT_DOC: new_impl_requirement.md
#   - EXISTING_WORKFLOW_DIR: workflows/text_summarizer/
```

The new requirement doc should describe ONLY the new implementation strategy, not the full workflow.

### Self-Bootstrap

AGB can build itself. The self-bootstrap requirement specifies:
- **Input:** Requirement documents
- **Output:** Workflow packages (per BASE_COMPOSITION_STANDARD v2.0)

## 9. References

- Base Composition Standard: `docs/system/00_governance/foundation/current/BASE_COMPOSITION_STANDARD_v1.0.md`
- AGB workflow: `workflows/artifact_generator_builder/`
- AGB requirement docs: `workflows/artifact_generator_builder/Specs/`
