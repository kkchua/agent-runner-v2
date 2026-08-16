# Builder Specialized Steps

Builder-type workflows produce executable agent-runner-v2 workflow packages as output.
The output is split between **LLM-generated domain logic** and **mechanically assembled
infrastructure** — the LLM never writes structural files.

## Architecture

The builder follows a template-based pattern:

```
AGB Pipeline (fixed — runs the builder itself):
  analyze_requirement → plan_domain_logic → challenge_plan
  → implement_domain → critic_impl
  → assemble_package → review_package → validate_structure
  → gatekeep_package → promote_package → step_completion

What the LLM generates (during implement_domain):
  ├── actions.py          — @action functions for the target workflow's action steps
  ├── prompts/*.txt       — prompt templates for the target workflow's prompt steps
  ├── impls/*/prompts/    — implementation-specific prompt overrides
  └── requirements.txt    — Python dependencies

What AGB assembles mechanically (during assemble_package):
  ├── workflow.toml       — from Analysis JSON (identity, domain_steps, implementations)
  ├── context_extensions.py — from Analysis JSON (artifact_keys)
  └── impls/*/impl.yaml  — from Analysis JSON (implementation overrides)

What AGB deploys (during promote_package):
  └── workflows/{codename}/ — complete workflow package directory
```

The LLM defines the target workflow's **domain steps** in the Analysis JSON.
These domain steps describe what the target workflow DOES (parse input, analyze
structure, design output, generate logic). The LLM then generates the code and
prompts for those domain steps. Infrastructure is assembled from the Analysis JSON.

## What the LLM Generates

### actions.py (domain action functions)

**Artifact:** `WORKFLOW_ACTIONS_FILE`
**Generated during:** implement_domain step

**Rules:**
- Import from `agent_runner_v2.action_result` and `agent_runner_v2.workflow_packages.actions`
- Each action function uses keyword-only args: `(*, context, state, step_cfg, project_root)`
- Each function reads inputs from `context` dict, writes outputs to `context` paths
- Return `ActionResult` with status APPROVED/REJECTED, remark, artifacts dict
- Include reject_code for all REJECTED paths
- Follow the action plan from DOMAIN_PLAN for core logic, validation rules, error handling
- One `@action("name")` function per action-type domain step in the Analysis JSON

### prompts/*.txt (prompt templates)

**Artifact:** `WORKFLOW_PROMPTS_DIR`
**Generated during:** implement_domain step

**Rules:**
- Filename format: `{step_number}_{step_name}.txt`
- Include artifact placeholder sections (e.g., `{INPUT_ARTIFACT}`)
- Include output instructions with target artifact path
- Include validation checklist
- Include role policy justification
- One prompt file per prompt-type domain step in the Analysis JSON

### Impl-specific overrides

**Artifact:** `IMPL_OVERRIDE_FILES` (impls/*/prompts/, impls/*/actions.py)
**Generated during:** implement_domain step

**Rules:**
- Each implementation gets its own prompts/ directory with override prompt files
- Override prompts follow the same structure as default prompts
- Override prompts implement the variant strategy (e.g., more comprehensive, more concise)

---

## What AGB Assembles Mechanically

### _assemble_package action

**Type:** action (no LLM)
**Input:** `ANALYSIS_JSON_FILE`, `WORKFLOW_ACTIONS_FILE`, `WORKFLOW_PROMPTS_DIR`
**Output:** `WORKFLOW_MANIFEST_FILE`, `WORKFLOW_EXTENSIONS_FILE`, `IMPL_OVERRIDE_FILES`

**What it produces:**
- `workflow.toml` — Step definitions with onsuccess chaining, identity, implementation declarations, artifact bindings, terminal step_completion
- `context_extensions.py` — WorkflowExtensions subclass with INPUT_ARTIFACTS and OUTPUT_ARTIFACTS dicts, correct imports from `agent_runner_v2.workflow_packages.workflow_extensions`
- `impls/*/impl.yaml` — Override declarations for each alternative implementation

**Assembly rules:**
- Extract identity from Analysis JSON (name, job_prefix, version, label, description)
- Generate `[[step]]` entries from domain_steps with onsuccess chaining
- Map action steps to `action = "<function_name>"`
- Map prompt steps to `prompt = "prompts/<file>.txt"`
- Generate `[[workflow.implementation]]` entries from implementations
- Set init_step to the first domain step
- Always include terminal `step_completion` step
- Generate context_extensions.py with correct imports and two-dict pattern
- Generate impl.yaml for each implementation with override mappings

**Reference implementation:** AGB's own `_assemble_package` action in `workflows/artifact_generator_builder/actions.py`

### _promote_workflow_package action

**Type:** action (no LLM)
**Input:** `WORKFLOW_MANIFEST_FILE`, `WORKFLOW_ACTIONS_FILE`, `WORKFLOW_EXTENSIONS_FILE`, `WORKFLOW_PROMPTS_DIR`
**Output:** `WORKFLOW_PACKAGE_DIR`

**What it does:**
- Read codename from the generated workflow.toml
- Back up any existing `workflows/{codename}/` directory
- Copy workflow.toml, context_extensions.py, actions.py, README.md, prompts/, impls/ to target
- Generate README.md if not present (from workflow.toml metadata)

**Reference implementation:** AGB's own `_promote_workflow_package` action in `workflows/artifact_generator_builder/actions.py`

---

## Domain Step Design Guidelines

The domain_steps in the Analysis JSON define the TARGET workflow's pipeline.
They describe what the target workflow DOES, not how it's built or deployed.

**DO include in domain_steps:**
- Input parsing/extraction (action steps)
- Content analysis (prompt steps)
- Design/planning (prompt steps)
- Domain logic generation (prompt steps)
- Domain-specific data transforms (action steps)

**DO NOT include in domain_steps:**
- Generating workflow.toml (assembled mechanically)
- Generating context_extensions.py (assembled mechanically)
- Generating impl.yaml (assembled mechanically)
- Generating README.md (generated by promote)
- Assembling the package (done by _assemble_package)
- Deploying/promoting (done by _promote_workflow_package)

---

## Notes

- The LLM generates only 3 things: actions.py, prompts/*.txt, and requirements.txt
- Infrastructure files (workflow.toml, context_extensions.py, impl.yaml) are assembled mechanically by the `_assemble_package` action from the Analysis JSON
- The `_promote_workflow_package` action deploys the assembled package to the target workflow directory
- The quality gates (review_package, validate_structure, gatekeep_package) verify the assembled package before deployment
- Generator-type workflows do NOT use these specialized steps — they use standard transformation steps instead
