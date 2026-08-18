# AGB Artifact Usage Reference

> **Purpose:** Track which artifact keys are used by which steps, actions, prompts, and documentation
> **Workflow:** artifact_generator_builder v3.0.0
> **Design principle:** Domain artifacts (LLM's world) vs Infrastructure artifacts (platform's world) are separated by construction.

---

## Domain Artifacts (LLM's World)

These artifacts flow through the domain pipeline. The LLM sees and works with these only.

### Input Artifacts

| Key | Pattern | Producer | Consumer(s) | Description |
|-----|---------|----------|-------------|-------------|
| `REQUIREMENT_DOC` | `input/` | User | analyze_requirement | The requirement document (markdown with YAML frontmatter) |

### Domain Pipeline Artifacts

| Key | Pattern | Producer | Consumer(s) | Description |
|-----|---------|----------|-------------|-------------|
| `ANALYSIS_JSON_FILE` | `ANALYSIS_JSON-{seq}.json` | analyze_requirement | plan_domain_logic, implement_domain | Domain analysis: identity + domain_steps + artifact_keys |
| `DOMAIN_PLAN_FILE` | `DOMAIN_PLAN-{seq}.md` | plan_domain_logic | challenge_plan, implement_domain | Detailed plan for domain actions + prompts |
| `PLAN_CHALLENGE_FILE` | `PLAN_CHALLENGE-{seq}.md` | challenge_plan | (refine loop → plan_domain_logic) | Critique of the domain plan |
| `WORKFLOW_ACTIONS_FILE` | `actions.py` | implement_domain | assemble_package, review_package, validate_structure, gatekeep_package, promote_package | Domain action functions |
| `WORKFLOW_PROMPTS_DIR` | `prompts/` | implement_domain | assemble_package, review_package, promote_package | Domain prompt templates |
| `WORKFLOW_REQUIREMENTS_FILE` | `requirements.txt` | implement_domain | (final domain output) | External dependencies list |
| `IMPL_CRITIQUE_FILE` | `IMPL_CRITIQUE-{seq}.md` | critic_impl | (refine loop → implement_domain) | Review of domain implementation |

---

## Infrastructure Artifacts (Platform's World)

These artifacts are produced by the platform's infrastructure layer. The domain LLM never sees or references these.

| Key | Pattern | Producer | Consumer(s) | Description |
|-----|---------|----------|-------------|-------------|
| `WORKFLOW_EXTENSIONS_FILE` | `context_extensions.py` | copy_infrastructure (step 2) | implement_domain (read-only, for artifact key reference) | Context extensions for artifact key resolution |
| `WORKFLOW_MANIFEST_FILE` | `workflow.toml` | assemble_package (step 7) | review_package, validate_structure, gatekeep_package, promote_package | Generated workflow manifest |
| `IMPL_OVERRIDE_FILES` | `impls/` | assemble_package (step 7) | (final output) | Implementation override files (if any) |
| `PACKAGE_REVIEW_FILE` | `PACKAGE_REVIEW-{seq}.md` | review_package (step 8) | gatekeep_package | Holistic package review |
| `VALIDATION_FINDINGS_FILE` | `VALIDATION_FINDINGS-{seq}.md` | validate_structure (step 9) | gatekeep_package | Deterministic validation results |
| `GATEKEEP_PACKAGE_FILE` | `GATEKEEP_PACKAGE-{seq}.md` | gatekeep_package (step 10) | (final output) | Final gatekeeper decision |
| `WORKFLOW_PACKAGE_DIR` | (promoted path) | promote_package (step 11) | (final output) | Final promoted workflow directory |

---

## System Context Variables (Not Artifacts)

These are injected into context but are not tracked as artifacts:

| Key | Source | Description |
|-----|--------|-------------|
| `CODENAME` | Extracted from REQUIREMENT_DOC frontmatter | Workflow codename |
| `GOVERNANCE_RUNTIME_ROOT` | Runtime | Path to governance docs (~/.ukbe-runner/bundles/core/current/) |
| `PLATFORM_RUNTIME_ROOT` | Runtime | Path to platform docs |
| `BASE_COMPOSITION_STANDARD` | Runtime | Path to BCS_v2.0.md |

---

## Data Flow Summary

### Domain Pipeline (LLM's World)
```
REQUIREMENT_DOC
    ↓
analyze_requirement → ANALYSIS_JSON_FILE
    ↓
plan_domain_logic → DOMAIN_PLAN_FILE
    ↓
challenge_plan → PLAN_CHALLENGE_FILE (refine loop → plan_domain_logic)
    ↓
implement_domain → WORKFLOW_ACTIONS_FILE, WORKFLOW_PROMPTS_DIR, WORKFLOW_REQUIREMENTS_FILE
    ↓
critic_impl → IMPL_CRITIQUE_FILE (refine loop → implement_domain)
```

### Infrastructure Pipeline (Platform's World)
```
WORKFLOW_ACTIONS_FILE + WORKFLOW_PROMPTS_DIR + ANALYSIS_JSON_FILE
    ↓
assemble_package → WORKFLOW_MANIFEST_FILE, WORKFLOW_EXTENSIONS_FILE, IMPL_OVERRIDE_FILES
    ↓
review_package → PACKAGE_REVIEW_FILE (refine loop → implement_domain)
    ↓
validate_structure → VALIDATION_FINDINGS_FILE
    ↓
gatekeep_package → GATEKEEP_PACKAGE_FILE (refine loop → implement_domain)
    ↓
promote_package → WORKFLOW_PACKAGE_DIR
```

---

## Refine Loops

| Challenge/Critique | Returns To | Max Iterations |
|--------------------|------------|----------------|
| `PLAN_CHALLENGE_FILE` | `plan_domain_logic` | 2 |
| `IMPL_CRITIQUE_FILE` | `implement_domain` | 2 |
| `PACKAGE_REVIEW_FILE` | `implement_domain` | 2 |
| `GATEKEEP_PACKAGE_FILE` | `implement_domain` | 2 |

---

## Implementation Notes

- **Domain/Infrastructure separation:** Domain prompts never reference infrastructure files or artifact keys. Infrastructure is universal/standard — same for every AGB run.
- **Single standard implementation:** AGB generates workflows with a single "standard" implementation. The `[[workflow.implementation]] name = "standard"` is added automatically by the assembler.
- **Two-tier prompt resolution:** Prompts resolve from `impls/{name}/prompts/` first, then fallback to `prompts/`.
- **Analysis JSON is domain-only:** No infrastructure fields (no implementations array, no extend_mode).

---

## See Also

- [02_ANALYSIS_JSON_SCHEMA.md](./02_ANALYSIS_JSON_SCHEMA.md) — Analysis JSON structure (domain-only)
- [BCS_v2.0.md](./BCS_v2.0.md) — Base Composition Standard
- [07_SDLC_PIPELINE.md](./07_SDLC_PIPELINE.md) — Step-by-step pipeline walkthrough
