# Workflow Specification: Prompt Quality Audit v1

> Save to `docs/repo/workflow_builder/specs/prompt_quality_audit_v1.md`.
> The workflow builder reads this document and generates the complete
> workflow package (workflow.toml, context_extensions.py, prompts, actions.py).
>
> **Key principle:** Describe WHAT the workflow does (domain problem, inputs,
> outputs, constraints). The builder infers HOW to structure it (step sequence,
> routing, role policies, gatekeepers, self-validation).

## Overview

**Workflow name:** `prompt_quality_audit_v1`
**Label:** Prompt Quality Audit v1
**Job prefix:** `PQAUD`
**Description:** Semantic audit of all prompt templates in an agent-runner-v2 workflow package. Runs one focused quality dimension per execution — placeholder resolution, instruction clarity, gatekeeper completeness, output contract validation, or cross-workflow consistency. Produces a dimension-specific quality report and improvement recommendations.

## Purpose

The agent-runner-v2 platform is prompt-driven. Every workflow step that produces artifacts relies on LLM prompt templates. If a prompt is ambiguous, missing constraints, has broken placeholders, or doesn't specify output format clearly — the workflow fails silently or produces inconsistent output.

This workflow audits the prompts themselves. Not "does the workflow run?" but "is this prompt well-constructed? Will it reliably produce correct output? Are all placeholders resolvable? Are the gatekeeper constraints complete?"

**Trigger:** Manual — user selects one workflow and one quality dimension to audit per run.

**Scope:** One workflow per run. The user runs the audit against a single workflow's prompts, gets a focused analysis, fixes issues, then moves to the next workflow or dimension.

**Outcome (per run):**
1. **Quality report** — specific issues found in the selected dimension scope, with severity and evidence
2. **Improvement recommendations** — prioritized fixes for the prompt templates

**Dimensions:**

| Dimension | Name | Scope |
|-----------|------|-------|
| 1 | Placeholder Resolution | All `{PLACEHOLDER}` references in prompts — are they registered in context_extensions.py? Do they resolve to real paths/values at runtime? Missing or misspelled placeholders |
| 2 | Instruction Clarity | Are prompt instructions unambiguous? Do they specify what to produce, not how? Are constraints explicit? Are there contradictory instructions? |
| 3 | Gatekeeper Completeness | Do gatekeeper prompts have all required check sections? Are decision vocabularies consistent (APPROVED/REJECTED)? Are gate criteria aligned with what the generate step actually produces? |
| 4 | Output Contract | Do prompts specify expected output format? Are artifact keys referenced correctly? Is the output structure (sections, headings) prescribed? Do prompts match the workflow.toml step configuration? |
| 5 | Internal Consistency | Within the target workflow: are naming conventions consistent across prompts? Do similar steps use similar prompt patterns? Are shared patterns (TDD loop, review, refine) implemented consistently? |

## Workflow Type

**Mixed** — Action-driven static analysis (placeholder extraction, pattern matching, structural validation), plus prompt-driven semantic analysis for clarity assessment and internal pattern comparison.

## Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `AUDIT_SCOPE_FILE` | JSON config specifying target workflow(s) and which dimension to audit | Yes |

**AUDIT_SCOPE_FILE format:**

```json
{
  "dimension": 1,
  "dimension_name": "placeholder_resolution",
  "target_repo_root": "D:\\MyProjectSpace\\01_Workflows\\agent-runner-v2",
  "target_workflow": "sdlc_10_requirement_v1",
  "exclude_patterns": [
    "*.pyc",
    "__pycache__/**"
  ]
}
```

**Dimension values:** 1 (placeholders), 2 (clarity), 3 (gatekeeper), 4 (output_contract), 5 (cross_workflow)

**Target workflow:** Single workflow name — audit one workflow's prompts per run.

## Output Artifacts

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `TEST_CRITERIA_FILE` | `TEST_CRITERIA-{date}-{seq}_{slug}.md` | Acceptance criteria for the audit |
| `SCAN_INDEX_FILE` | `SCAN_INDEX-{date}-{seq}_{slug}.md` | Prompts scanned, workflows covered, exclusions applied |
| `QUALITY_REPORT_FILE` | `PQ_FINDINGS_D{dimension}-{date}-{seq}_{slug}.md` | Dimension-specific quality findings |
| `IMPROVEMENT_RECOMMENDATIONS_FILE` | `PQ_IMPROVEMENT_D{dimension}-{date}-{seq}_{slug}.md` | Prioritized improvement recommendations |
| `REVIEW_FILE_SUGGESTED` | `PQAUD-REV-{date}-{seq}_{slug}.md` | Review of generated documents |
| `VALIDATION_REPORT_FILE` | `PQAUD-VALIDATION-{date}-{seq}_{slug}.md` | Structural validation report |

**Granularity rule:** One artifact key per logical file.

## Context Variables

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| `TARGET_REPO_ROOT` | From AUDIT_SCOPE_FILE | Root of the repo containing workflows |
| `WORKFLOWS_DIR` | `{TARGET_REPO_ROOT}/workflows/` | Directory containing workflow packages |
| `DIMENSION_DEFINITIONS_DIR` | `{workflow_package}/dimensions/` | Directory containing dimension scope definition files |

## Quality Requirements

### Quality Report Must Include

- **Dimension header** — which dimension was run, which workflows were audited
- **Executive summary** — total findings by severity (critical/high/medium/low/info)
- **Per-finding entries:**
  - Severity: critical / high / medium / low / info
  - Workflow name and prompt file (e.g., `sdlc_10_requirement_v1/prompts/01_generate_requirements.txt`)
  - Location within prompt (line number or section reference)
  - Evidence: the problematic text, missing placeholder, or pattern violation
  - Description: what the issue is and why it's a quality problem
  - Impact: how this affects workflow execution or output quality
  - Recommended fix: specific text change or structural update
- **Scope summary** — prompts scanned, workflows covered, total prompt files analyzed
- **Dimension-specific metrics:**
  - Dimension 1: total placeholders found, resolved count, unresolved count, orphan placeholders (in context_extensions but not in any prompt)
  - Dimension 2: prompts reviewed, clarity issues per prompt, ambiguity categories
  - Dimension 3: gatekeeper prompts found, missing check sections, vocabulary inconsistencies
  - Dimension 4: prompts with output format specified, artifact key accuracy, structure prescription coverage
  - Dimension 5: prompts reviewed, pattern consistency score within workflow, naming violations, structural deviations between similar steps

### Improvement Recommendations Must Include

- Prioritized by severity (critical first)
- Each item: finding reference, specific fix, effort estimate (S/M/L)
- Quick wins section: high-impact, low-effort fixes (e.g., fix a misspelled placeholder)
- Pattern improvements: systemic issues that affect multiple prompts
- Template suggestions: recommended text for common fixes

### Scanning Rules

- Scan all `.txt` files under `workflows/{name}/prompts/` for each target workflow
- Parse `workflow.toml` for each target workflow to understand step configuration
- Parse `context_extensions.py` for each target workflow to extract registered artifact keys and context variables
- For dimension 5 (internal consistency): compare all prompts within the target workflow against each other
- Always exclude: `__pycache__/`, `*.pyc`, non-prompt files

## Custom Actions

### Action: scan_workflow_prompts

**Purpose:** Read the AUDIT_SCOPE_FILE config. For the target workflow:
1. List all `.txt` files in `prompts/` directory
2. For each prompt file, extract:
   - All `{PLACEHOLDER}` references (regex: `\{[A-Z_][A-Z0-9_]*\}`)
   - File size, line count
   - Step type classification (generate, review, refine, gatekeeper, test_criteria) based on filename convention
3. Parse `workflow.toml` to extract:
   - Step definitions and their prompt file references
   - Routing rules (onsuccess, on_reject_refine)
   - Coder role assignments
   - Required input/output artifacts
4. Parse `context_extensions.py` to extract:
   - `register_artifact_keys()` return dict — all registered artifact keys and their path patterns
   - `build_context_extensions()` return dict — all injected context variables
   - Any hardcoded paths or workflow-specific context

Build a structured index mapping: workflow → step → prompt file → placeholders → registered keys.

**Returns:** APPROVED with prompt index as structured data. REJECTED only if target workflow doesn't exist.

### Action: validate_placeholder_resolution

**Purpose:** Dimension 1 only. Cross-reference the placeholder scan results:
1. For each `{PLACEHOLDER}` found in prompts, check if it exists in the registered artifact keys OR context variables from context_extensions.py
2. Flag unresolved placeholders (in prompt but not registered)
3. Flag orphan registrations (registered but not used in any prompt)
4. Flag misspelled placeholders (close match to a registered key — e.g., `{TEST_CRITERA_FILE}` vs `{TEST_CRITERIA_FILE}`)
5. Flag path placeholders that should be absolute but use relative patterns
6. Check for placeholder consistency across similar steps (e.g., all review prompts should reference the same review output key)

**Returns:** APPROVED with resolution report (resolved/unresolved/orphan/misspelled counts and details). REJECTED only if no prompts to scan.

### Action: validate_gatekeeper_structure

**Purpose:** Dimension 3 only. For each gatekeeper prompt (identified by filename pattern `*gatekeep*` or `*gatekeep*`):
1. Check for required sections: scope check, artifact verification, decision vocabulary
2. Verify decision vocabulary uses APPROVED/REJECTED consistently
3. Check that gate criteria reference actual artifacts produced by the preceding generate step
4. Verify gate prompts don't duplicate the generate step's instructions (gate should validate, not generate)
5. Check that rejection routing matches workflow.toml (on_reject_refine points to correct step)

**Returns:** APPROVED with gatekeeper validation report. REJECTED only if no gatekeeper prompts found.

## Builder Instructions

**Domain phases:**

1. **TDD loop** — Generate test criteria for the audit, review, refine
2. **Scan** — Action-driven: discover all target prompts, extract placeholders, parse workflow configs, build index
3. **Dimension-specific analysis** — Action-driven static checks:
   - Dimension 1: placeholder resolution cross-reference
   - Dimension 2: file collection only (LLM does all analysis)
   - Dimension 3: gatekeeper structural validation
   - Dimension 4: artifact key and output format extraction
   - Dimension 5: cross-workflow pattern extraction
4. **Semantic analysis** — LLM reads scan results and prompt content, performs dimension-specific quality assessment, produces quality report
5. **Review findings** — Validate completeness and severity ratings
6. **Generate improvement recommendations** — LLM produces prioritized fixes
7. **Validate documents** — Structural validation
8. **Final review** — Human review

**Domain constraints:**

- Each dimension is self-contained — running dimension 1 does not require or produce data from other dimensions
- The prompt index (from scan step) is reused across dimensions
- Findings must cite specific evidence (workflow name, prompt file, line/section, exact text)
- Severity ratings must follow consistent criteria:
  - **Critical:** Broken workflow execution (unresolvable placeholder, missing gatekeeper decision vocabulary, output key mismatch causing step failure)
  - **High:** Likely to cause incorrect output (ambiguous instructions, missing output format specification, gatekeeper checking wrong artifacts)
  - **Medium:** Inconsistency that may confuse LLM (contradictory constraints, non-standard naming, missing context variable)
  - **Low:** Style/convention issue (inconsistent formatting, verbose instructions, non-idiomatic placeholder naming)
  - **Info:** Observation or suggestion (could be clearer, might benefit from restructuring)

**Dimension scope definitions:**

Each dimension has a scope definition file describing what to check:

| Dimension | Scope Definition Content |
|-----------|--------------------------|
| 1 | Placeholder syntax rules, registration requirements, path resolution rules, common misspellings list |
| 2 | Clarity checklist: no HOW instructions, explicit WHAT, single-responsibility per step, no contradictions, constraints before instructions |
| 3 | Required gatekeeper sections, decision vocabulary rules, artifact reference validation, routing consistency |
| 4 | Output format specification rules, artifact key naming conventions (_FILE suffix), section structure requirements |
| 5 | Naming convention catalog, step pattern templates (generate-review-refine), TDD loop structure, shared vocabulary |

## Notes

- **One workflow per run** — Designed for focused, incremental prompt improvement. User audits dimension 1 for a workflow, fixes placeholders, then audits dimension 2, etc.
- **Dimension definitions are pluggable** — Scope definition files in `dimensions/` directory can be updated without changing the workflow. New checks, new rules, new patterns.
- **Platform-critical** — Prompts are the primary interface between the workflow system and the LLM. Prompt quality directly determines output quality. This workflow is meta-quality assurance for the platform itself.
- **Complements workflow builder** — `workflow_builder_v1` generates prompts; this workflow audits them. The builder creates; the auditor verifies.
- **Internal consistency is powerful** — Dimension 5 reveals patterns and inconsistencies within a single workflow. Run it to ensure all prompts in a workflow follow the same conventions before moving to the next workflow.
- **Prompt versioning awareness** — Some workflows have versioned prompts (e.g., `02_generate_prompts_v1.txt` through `02_generate_prompts_v9.txt`). The audit should focus on the latest version unless the scope specifies otherwise. Versioned prompts should be flagged if older versions are still referenced in workflow.toml.
