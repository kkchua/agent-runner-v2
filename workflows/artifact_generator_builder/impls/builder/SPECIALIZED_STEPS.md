# Builder Specialized Steps

Builder-type workflows require these specialized transformation steps that are unique to generating workflow packages. These steps are **in addition to** the standard AGB pipeline (parse input → analyze → plan → generate → validate).

## Specialized Steps

### 1. Generate Workflow TOML

**Step name:** `generate_workflow_toml`
**Type:** prompt
**Purpose:** Produce the workflow.toml file with step definitions, routing, identity, and implementation declarations.

**Input:** Analysis JSON, domain plan
**Output:** `WORKFLOW_TOML`

**Generation rules:**
- Extract identity from analysis (name, job_prefix, version, label, description)
- Generate `[[step]]` entries from domain_steps with onsuccess chaining
- Map action steps to `action = "<function_name>"`
- Map prompt steps to `prompt = "prompts/<file>.txt"`
- Generate `[[workflow.implementation]]` entries from implementations
- Set init_step to the first domain step
- Always include terminal `step_completion` step

---

### 2. Generate Actions Python

**Step name:** `generate_actions_py`
**Type:** prompt
**Purpose:** Produce actions.py with @action-decorated Python functions for all action-type steps.

**Input:** Domain plan (action step plans), analysis JSON
**Output:** `ACTIONS_PY`

**Generation rules:**
- Import from `agent_runner_v2.action_result` and `agent_runner_v2.workflow_packages.actions`
- Each action function uses keyword-only args: `(context, state, step_cfg, project_root)`
- Each function reads inputs from `context` dict, writes outputs to `state["artifacts"]`
- Return `ActionResult` with status APPROVED/REJECTED, remark, artifacts dict
- Include reject_code for all REJECTED paths
- Follow the action plan from DOMAIN_PLAN for core logic, validation rules, error handling

---

### 3. Generate Context Extensions Python

**Step name:** `generate_context_extensions_py`
**Type:** prompt
**Purpose:** Produce context_extensions.py with artifact key registration and runtime context builder.

**Input:** Analysis JSON (artifact keys), workflow identity
**Output:** `CONTEXT_EXTENSIONS_PY`

**Generation rules:**
- Import from `agent_runner_v2.runtime_context` and `agent_runner_v2.workflow_packages.extensions_base`
- Create class extending `WorkflowExtensions` with `workflow_name` set
- Declare `INPUT_ARTIFACTS` dict (artifact key → default subpath)
- Declare `OUTPUT_ARTIFACTS` dict (artifact key → filename pattern)
- Implement `register_artifact_keys()`, `build_context_extensions()`, `install_to_global()`, `sync_to_backend()`
- Use `resolve_input_artifacts()` and `resolve_output_artifacts()` helpers

---

### 4. Generate Prompts

**Step name:** `generate_prompts`
**Type:** prompt
**Purpose:** Produce prompt template files for all prompt-type steps.

**Input:** Domain plan (prompt step plans), analysis JSON
**Output:** `PROMPTS_DIR` (multiple .txt files)

**Generation rules:**
- Filename format: `{step_number}_{step_name}.txt`
- Include artifact placeholder sections (e.g., `{INPUT_ARTIFACT}`)
- Include output instructions with target artifact path
- Include validation checklist
- Include role policy justification
- Follow the prompt plan from DOMAIN_PLAN

---

### 5. Generate Implementations

**Step name:** `generate_implementations`
**Type:** prompt
**Purpose:** Produce impls/ directory with override files for each declared implementation.

**Input:** Analysis JSON (implementations), domain plan
**Output:** `IMPLS_DIR`

**Generation rules:**
- Create subdirectory per implementation: `impls/<impl_name>/`
- Generate `impl.yaml` with override declarations
- Generate override prompts in `impls/<impl_name>/prompts/`
- Generate override actions.py if action overrides are declared
- Only override steps that differ from the default implementation

---

### 6. Generate README

**Step name:** `generate_readme`
**Type:** prompt
**Purpose:** Produce README.md documenting the generated workflow.

**Input:** Analysis JSON, workflow.toml (generated)
**Output:** `README_MD`

**Generation rules:**
- Include pipeline steps table (step name, type, detail)
- Include implementations table
- Include usage command: `ukbe-run-agent run --template-group <name>`
- Include file structure tree

---

## Step Ordering

The specialized steps execute after the standard AGB analysis/planning phase:

```
Standard AGB Pipeline:
  parse_input → analyze_requirement → build_analysis_json → build_domain_plan

Builder Specialized Steps:
  generate_workflow_toml
  → generate_actions_py
  → generate_context_extensions_py
  → generate_prompts
  → generate_implementations
  → generate_readme
  → validate_package
  → step_completion
```

## Notes

- The specialized steps are all prompt-driven (LLM generates code)
- Each step's prompt plan is defined in the DOMAIN_PLAN
- The validate_package step runs the quality gates (PACKAGE_REVIEW, VALIDATION_FINDINGS, GATEKEEP_PACKAGE)
- Generator-type workflows do NOT use these specialized steps — they use standard transformation steps instead
