# Workflow Specification: Creative Workflow Builder v1

## Overview

**Workflow name:** `creative_workflow_builder_v1`
**Label:** Creative Workflow Builder v1
**Job prefix:** `CWFBLD`
**Description:** Generates a complete agent-runner-v2 workflow package from a creative media agent-md file (JiMeng-style LLM agent instructions). Supports both prompt-only workflows (e.g., world-building, story design) and mixed workflows with Agnes Image/Video API action steps.

## Purpose

Creative media agent-md files (like the 7 JiMeng workflows) contain rich, monolithic LLM agent instructions for image/video generation pipelines. These need to be converted into agent-runner-v2 workflow packages that decompose the monolith into discrete steps with explicit artifact contracts, prompt templates, and optional Agnes API action steps.

**Trigger:** User provides an agent-md file describing a creative media workflow.

**Outcome:** A complete workflow package (`workflow.toml`, `context_extensions.py`, `actions.py` if needed, `prompts/*.txt`, `README.md`) ready to run on agent-runner-v2.

**Key difference from workflow_builder_v1:** This builder understands creative media workflow patterns (visual analysis, storyboard design, prompt engineering, API-based generation, video assembly) and maps JiMeng platform tools to Agnes API equivalents.

## Workflow Type

**Mixed** -- Prompt-driven analysis/design steps with gatekeeper validation, plus action-driven bundle validation and package promotion.

## Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `AGENT_MD_FILE` | The source agent-md file containing the creative workflow instructions | Yes |

## Output Artifacts

| Artifact Key | Filename Pattern | Description |
|---|---|---|
| `CREATIVE_REQUIREMENTS` | `CREATIVE_REQ-{date}-{seq}_{slug}.md` | Parsed workflow structure, phases, tools, constraints |
| `STATE_CONTRACT` | `STATE_CONTRACT-{date}-{seq}_{slug}.md` | Artifact key design and state flow between steps |
| `STEP_ARCHITECTURE` | `STEP_ARCH-{date}-{seq}_{slug}.md` | Step sequence with routing, role policies, API mappings |
| `REVIEW_FILE_SUGGESTED` | `CWFBLD-REV-{date}-{seq}_{slug}.md` | Final review of generated package |
| `WORKFLOW_BUNDLE` | `workflows/<slug>/` | Complete generated workflow package directory |

## Step Sequence

### Step 1: parse_agent_md

```
Step: parse_agent_md
Type: prompt
Role: architect_standard
Purpose: Read the agent-md file and extract its structure -- role definition,
  phase sequence, tool usage, internal variables, global constraints, quality
  checklists, and embedded agent prompts. Classify the workflow archetype
  (image-to-video pipeline, IP creation, storyboard design, e-commerce,
  prompt-only, etc.). Identify which JiMeng tools are used and map them to
  Agnes API equivalents or prompt-only steps.
Produces: CREATIVE_REQUIREMENTS
On success: -> gatekeep_requirements
```

### Step 2: gatekeep_requirements

```
Step: gatekeep_requirements
Type: prompt
Role: validation_standard
Purpose: Validate that the parsed requirements capture all phases, tools,
  constraints, and variables from the original agent-md. Check that the
  archetype classification is correct. Verify no phase was missed or
  misclassified. Self-validate against the original agent-md content.
Produces: REVIEW_FILE_SUGGESTED
On success: -> design_state_contract (requires human approval)
On rejection: -> parse_agent_md (max 2 iterations)
```

### Step 3: design_state_contract

```
Step: design_state_contract
Type: prompt
Role: architect_standard
Purpose: Map the agent-md's internal variables to explicit artifact keys.
  Design the state contract -- which step produces which artifact, which
  step consumes it. Define path patterns with placeholders. Determine
  which state is file-based (Markdown, JSON) vs config-based. For Agnes
  API steps, define the input/output artifact contracts (prompt files
  in, generated media out).
Produces: STATE_CONTRACT
On success: -> gatekeep_state
```

### Step 4: gatekeep_state

```
Step: gatekeep_state
Type: prompt
Role: validation_standard
Purpose: Validate the state contract -- every artifact has exactly one
  producer and at least one consumer. No dangling references. Path
  patterns are consistent. Artifact keys follow naming conventions.
  For API steps: input prompts and output media are properly linked.
Produces: REVIEW_FILE_SUGGESTED
On success: -> design_steps (requires human approval)
On rejection: -> design_state_contract (max 2 iterations)
```

### Step 5: design_steps

```
Step: design_steps
Type: prompt
Role: architect_standard
Purpose: Design the complete step sequence for the target workflow.
  Decompose the agent-md phases into discrete agent-runner steps.
  For each step: determine type (prompt or action), assign role policy,
  define routing (onsuccess, on_reject_refine), place human approval
  gates. Map JiMeng tools to Agnes API @action() functions or
  prompt-only steps. Design review/refine loops for creative quality.
  Determine which steps need self-validation sections.
Produces: STEP_ARCHITECTURE
On success: -> gatekeep_steps
```

### Step 6: gatekeep_steps

```
Step: gatekeep_steps
Type: prompt
Role: validation_standard
Purpose: Validate the step architecture -- step sequence covers all
  agent-md phases, routing is correct, artifact flow matches state
  contract, role policies are appropriate, human gates are placed at
  the right points. For API steps: verify action function signatures
  match the artifact contracts. Check that prompt steps inject all
  needed context from upstream artifacts.
Produces: REVIEW_FILE_SUGGESTED
On success: -> generate_package (requires human approval)
On rejection: -> design_steps (max 2 iterations)
```

### Step 7: generate_package

```
Step: generate_package
Type: prompt
Role: architect_standard
Purpose: Generate all workflow package files from the design documents:
  workflow.toml (step definitions, routing, artifact bindings),
  context_extensions.py (artifact key registration, context injection),
  actions.py (if API steps needed -- Agnes Image/Video API calls with
  retry, config reading, index generation),
  prompts/*.txt (one per prompt-driven step, with artifact placeholders
  and self-validation sections),
  README.md, .env.sample, config.json.sample.
  Follow principles-based generation -- infer required files from the
  design documents, not a fixed list.
Produces: WORKFLOW_BUNDLE
On success: -> validate_bundle
```

### Step 8: validate_bundle

```
Step: validate_bundle
Type: action (validate_creative_bundle)
Purpose: Structural validation of the generated workflow package --
  TOML parses correctly, all referenced prompt files exist, artifact
  keys in workflow.toml match context_extensions.py, action functions
  in actions.py match step declarations, all placeholder references
  in prompts resolve to declared artifacts.
On success: -> review_package
On rejection: -> generate_package (max 2 iterations)
```

### Step 9: review_package

```
Step: review_package
Type: prompt
Role: reviewer_standard
Purpose: Final human review of the complete generated workflow package.
  Present all generated files for inspection. Check that the package
  faithfully represents the original agent-md workflow, that Agnes
  API actions are correctly configured, and that prompt templates
  include all necessary context and constraints.
Produces: REVIEW_FILE_SUGGESTED
On success: -> promote_package (requires human approval)
On rejection: -> refine_package (max 2 iterations)
```

### Step 10: refine_package

```
Step: refine_package
Type: prompt
Role: architect_standard
Purpose: Fix issues identified by the final review. Regenerate only
  the files that need changes.
On success: -> review_package
```

### Step 11: promote_package

```
Step: promote_package
Type: action (promote_creative_workflow)
Purpose: Copy the generated workflow package to workflows/<slug>/
  in the agent-runner-v2 repo.
promotes: WORKFLOW_BUNDLE
On success: -> stepCompletion
```

### Terminal: stepCompletion

```
Step: stepCompletion
Type: action (step_completion)
```

## Context Variables

- `AGENT_MD_ROOT` -- Directory containing the source agent-md file
- `WORKFLOW_TARGET_ROOT` -- Target repo root where workflows/ directory lives (default: agent-runner-v2 project root)
- `GOVERNANCE_RUNTIME_ROOT` -- Layer 1 governance docs (standard)
- `PLATFORM_RUNTIME_ROOT` -- Layer 2 platform docs (standard)

## Special Requirements

- **Principles-based generation** -- The generate_package step infers required files from design documents, not a fixed list. Some workflows need actions.py (API steps), others don't (prompt-only).
- **Dual-mode output** -- Builder supports generating both prompt-only workflows (e.g., world-building, story design) and mixed workflows with Agnes API actions (image/video generation).
- **Agnes API mapping** -- JiMeng tools are mapped to Agnes equivalents: `text2image`/`image2image` -> Agnes Image 2.0 Flash API, `multi_modal2video`/`text2video` -> Agnes Video V2.0 API, `video_editor` -> video concatenation action.
- **State continuity** -- The builder must ensure each prompt step's template injects all upstream artifact content needed for context continuity (replacing JiMeng's in-conversation state accumulation).
- **Self-validation in prompts** -- Each prompt-driven step includes a self-validation section checking output against the agent-md's quality criteria.
- **Auto-incrementing sequence numbers** -- All artifact paths use `{seq}` to prevent overwrites across runs.

## Custom Actions

### Action: validate_creative_bundle

```
Action: validate_creative_bundle
Purpose: Structural validation of the generated workflow package.
  Check TOML syntax, prompt file existence, artifact key consistency
  between workflow.toml and context_extensions.py, action function
  registration, and placeholder resolution in prompt templates.
Returns: APPROVED if valid, REJECTED with specific structural errors.
```

### Action: promote_creative_workflow

```
Action: promote_creative_workflow
Purpose: Copy the generated workflow package directory to
  workflows/<slug>/ in the target repo. Verify the target
  directory doesn't already exist (refuse to overwrite).
Returns: APPROVED with the target path, REJECTED if target exists.
```

## Gatekeeper Requirements

**3 gatekeepers** -- Full pipeline validation:

1. **gatekeep_requirements** (after parse_agent_md) -- Validates parse completeness
2. **gatekeep_state** (after design_state_contract) -- Validates artifact/state design
3. **gatekeep_steps** (after design_steps) -- Validates step architecture

Plus structural validation action (validate_creative_bundle) after package generation.

## Self-Validation

**Enable Self-Validation** -- All producer steps (parse_agent_md, design_state_contract, design_steps, generate_package) include self-check sections validating against the original agent-md content and upstream design documents.

## Notes

- **Reference agent-md files:** 7 JiMeng creative workflows at `D:\MyProjectSpace\01_Workflows\JiMeng\agent-md\` covering image-to-video, world-building, storyboard, IP creation, e-commerce, UGC, and pop-art ad workflows.
- **Existing pattern reference:** `agnes_media_gen_v1` workflow shows the Agnes API integration pattern (retry logic, config reading, index files, archive pattern).
- **Existing builder reference:** `workflow_builder_v1` shows the gatekeeper QC pipeline pattern this builder follows.
- **Key conversion challenge:** JiMeng agents accumulate state in conversation; agent-runner steps are independent. The builder must design artifact contracts that preserve state continuity across steps.
- **Workflow spec template reference:** The builder should use the same spec style as `agnes_media_gen_v1.md` -- concise, WHAT not HOW.
