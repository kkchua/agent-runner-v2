# Workflow Specification: Creative Workflow Builder v1

> Save to `docs/repo/workflow_builder/specs/creative_workflow_builder_v1.md`.
> The workflow builder reads this document and generates the complete
> workflow package.
>
> **Key principle:** Describe WHAT the workflow does. The builder infers HOW
> to structure it (step sequence, routing, role policies, gatekeepers).
> See [BUILDER_REQUIREMENTS.md](../current/BUILDER_REQUIREMENTS.md) for what
> the builder enforces automatically.
>
> **This is a meta-workflow** — its output is another workflow package.
> The builder auto-detects this and enforces: TDD loop (init_step = generate_test_criteria),
> 4 gatekeepers (GATEKEEP_REQUIREMENTS, GATEKEEP_ARTIFACTS, GATEKEEP_STEPS, GATEKEEP_PACKAGE),
> exhausted_failure on all refine loops, action reuse audit.

## Overview

**Workflow name:** `creative_workflow_builder_v1`
**Label:** Creative Workflow Builder v1
**Job prefix:** `CWFBLD`
**Description:** Generates a complete agent-runner-v2 workflow package from a creative media agent-md file (JiMeng-style LLM agent instructions). Supports both prompt-only workflows (e.g., world-building, story design) and mixed workflows with Agnes Image/Video API action steps.

## Purpose

Creative media agent-md files (like the 7 JiMeng workflows) contain rich, monolithic LLM agent instructions for image/video generation pipelines. These need to be converted into agent-runner-v2 workflow packages that decompose the monolith into discrete steps with explicit artifact contracts, prompt templates, and optional Agnes API action steps.

**Trigger:** User provides an agent-md file describing a creative media workflow.

**Outcome:** A complete workflow package (`workflow.toml`, `context_extensions.py`, `actions.py` if needed, `prompts/*.txt`, `README.md`) ready to run on agent-runner-v2, plus three spec documents (spec template, SOP, standard) published to `docs/repo/workflow_builder/current/`.

**Key difference from workflow_builder_v1:** This builder understands creative media workflow patterns (visual analysis, storyboard design, prompt engineering, API-based generation, video assembly) and maps JiMeng platform tools to Agnes API equivalents.

## Workflow Type

**Mixed** — Prompt-driven analysis/design steps with gatekeeper validation, plus action-driven bundle validation and package promotion.

## Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `AGENT_MD_FILE` | The source agent-md file containing the creative workflow instructions | Yes |

## Output Artifacts

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `TEST_CRITERIA` | `TEST_CRITERIA-{date}-{seq}_{slug}.md` | Acceptance criteria for generated workflow |
| `CREATIVE_REQUIREMENTS` | `CREATIVE_REQ-{date}-{seq}_{slug}.md` | Parsed workflow structure, phases, tools, constraints |
| `STATE_CONTRACT` | `STATE_CONTRACT-{date}-{seq}_{slug}.md` | Artifact key design and state flow between steps |
| `STEP_ARCHITECTURE` | `STEP_ARCH-{date}-{seq}_{slug}.md` | Step sequence with routing, role policies, API mappings |
| `WORKFLOW_MANIFEST` | `workflow.toml` | Generated workflow manifest |
| `WORKFLOW_EXTENSIONS` | `context_extensions.py` | Generated artifact key registration and context injection |
| `WORKFLOW_ACTIONS` | `actions.py` | Generated custom actions (conditional — only if API steps needed) |
| `WORKFLOW_PROMPTS_INDEX` | `prompts/` index | Generated prompt template listing |
| `WORKFLOW_README` | `README.md` | Generated user guide for the workflow package |
| `WORKFLOW_ENV_SAMPLE` | `.env.sample` | Generated env template (conditional) |
| `WORKFLOW_CONFIG_SAMPLE` | `config.json.sample` | Generated config template (conditional) |
| `REVIEW_FILE_SUGGESTED` | `CWFBLD-REV-{date}-{seq}_{slug}.md` | Final review of generated package |
| `VALIDATION_REPORT` | `VALIDATION-{date}-{seq}_{slug}.md` | Structural validation report |
| `BUILDER_SPEC_TEMPLATE` | `CREATIVE_WORKFLOW_SPEC_TEMPLATE_v1.md` | Spec template for the generated builder's inputs |
| `BUILDER_SOP` | `CREATIVE_WORKFLOW_SOP_v1.md` | Operating procedure for the generated builder |
| `BUILDER_STANDARD` | `CREATIVE_WORKFLOW_STANDARD_v1.md` | Quality requirements and constraints for the generated builder |

**Granularity rule:** One artifact key per logical file. The runner tracks individual files, not directories.

## Context Variables

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| `AGENT_MD_ROOT` | Directory containing the source agent-md file | Source location |
| `WORKFLOW_TARGET_ROOT` | `{repo_root}` | Target repo where workflows/ directory lives |

## Quality Requirements

- **Dual-mode output** — Builder supports generating both prompt-only workflows (e.g., world-building, story design) and mixed workflows with Agnes API actions (image/video generation).
- **Agnes API mapping** — JiMeng tools are mapped to Agnes equivalents:
  - `text2image`/`image2image` → Agnes Image 2.0 Flash API
  - `multi_modal2video`/`text2video` → Agnes Video V2.0 API
  - `video_editor` → video concatenation action
- **State continuity** — JiMeng agents accumulate state in conversation; agent-runner steps are independent. The builder must design artifact contracts that preserve state continuity across steps.
- **Fixed task list for generate_package** — Unlike workflow_builder_v1 which uses principles-based generation, this builder uses a fixed task list to reduce LLM hallucination risk. The file set is predictable (workflow.toml, context_extensions.py, optional actions.py, prompts, README.md, conditional .env.sample/config.json.sample).
- **Action reuse** — `validate_workflow_bundle` and `promote_workflow_package` from `workflow_builder_v1` are reused. `promote_builder_docs` is a new action for copying spec documents to the builder docs area.

## Custom Actions

**One new action.** This workflow reuses existing actions from `workflow_builder_v1` and adds a new promote action for spec documents:

| Action | Source | Purpose |
|---|---|---|
| `validate_workflow_bundle` | workflow_builder_v1 | Structural validation of generated package |
| `promote_workflow_package` | workflow_builder_v1 | Copy workflow bundle to workflows/ directory |
| `promote_builder_docs` | **new** | Copy spec template, SOP, and standard to docs/repo/workflow_builder/current/ |
| `step_completion` | core | Terminal step |

## Builder Instructions

**Domain phases** (builder determines step sequence):

1. **TDD loop** — Generate test criteria, review, refine (mandatory for meta-workflows)
2. **Parse** — Extract structure from agent-md (role, phases, tools, variables, constraints)
3. **Gatekeep requirements** — Validate parse completeness
4. **Design state contract** — Map agent-md variables to artifact keys
5. **Gatekeep artifacts** — Validate artifact contracts
6. **Design steps** — Decompose into discrete steps with routing
7. **Gatekeep steps** — Validate step architecture
8. **Generate package** — Produce all workflow files AND three spec documents (spec template, SOP, standard)
9. **Gatekeep package** — Validate generated files
10. **Validate bundle** — Structural validation (reuse `validate_workflow_bundle`)
11. **Review package** — Final human review
12. **Refine package** — Fix issues (conditional)
13. **Promote workflow bundle** — Copy to workflows/ (reuse `promote_workflow_package`)
14. **Promote spec documents** — Copy spec template, SOP, standard to docs/repo/workflow_builder/current/ (use `promote_builder_docs`)

**Domain constraints:**

- Classify the workflow archetype (image-to-video pipeline, IP creation, storyboard design, e-commerce, prompt-only, etc.)
- For Agnes API steps, define input/output artifact contracts (prompt files in, generated media out)
- Each prompt step's template must inject all upstream artifact content needed for context continuity

**Spec document requirements:**

- **Spec template** (`CREATIVE_WORKFLOW_SPEC_TEMPLATE_v1.md`) — Blank input template that the generated builder accepts. Should describe the agent-md format, required sections (role, phases, tools, constraints), and quality expectations. Follows the domain-only principle (WHAT not HOW).
- **SOP** (`CREATIVE_WORKFLOW_SOP_v1.md`) — Operating procedure for running the generated builder. Covers setup (agent-md file preparation), execution (CLI command, expected duration), troubleshooting (common failures), and expected outputs.
- **Standard** (`CREATIVE_WORKFLOW_STANDARD_v1.md`) — Quality requirements for the generated builder. Covers Agnes API mapping rules, state continuity requirements, naming conventions, gatekeeper criteria, and archetype classification rules.

## Notes

- **Reference agent-md files:** 7 JiMeng creative workflows at `D:\MyProjectSpace\01_Workflows\JiMeng\agent-md\` covering image-to-video, world-building, storyboard, IP creation, e-commerce, UGC, and pop-art ad workflows.
- **Existing pattern reference:** `agnes_media_gen_v1` workflow shows the Agnes API integration pattern (retry logic, config reading, index files, archive pattern).
- **Existing builder reference:** `workflow_builder_v1` shows the gatekeeper QC pipeline pattern this builder follows.
