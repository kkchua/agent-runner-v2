# Composition System Specification: Workflow Builder

> **Domain:** Meta-workflow that builds workflows
> **Input to:** workflow_builder_v2 (self-bootstrapping)
> **Standard:** COMPOSITION_SYSTEM_STANDARD.md
> **Purpose:** Define workflow_builder_v2 as a composition system so it can generate its own next version (v3) and so the generated workflows produce extensible output composition specs.

---

## 1. Domain Overview

**Domain name:** `workflow_builder`
**Label:** Workflow Builder
**Job prefix:** `WBUILD`
**Description:** A meta-workflow that takes a composition system specification as input and generates a complete workflow package, including an output composition spec that makes the generated workflow's artifacts extensible.

### 1.1 Purpose

The workflow builder is a meta-workflow — it builds other workflows. It takes a domain's composition system specification (describing components, compositions, and outputs) and generates a complete workflow package that implements that composition system.

**Key innovation:** The builder produces TWO outputs:
1. **Workflow package** — the operational workflow (workflow.toml, prompts, actions, context_extensions.py, README.md)
2. **Output composition spec** — a composition standard that treats the generated workflow's output artifacts as a composable component library, enabling extensibility without code changes

**Trigger:** User provides a composition system specification document describing a domain's three-layer architecture.

**Outcome:** A complete workflow package that implements the composition system, PLUS a composition spec for the workflow's output artifacts so new output types can be added by composition.

### 1.2 Domain Context

The workflow builder sits at the top of the workflow creation hierarchy. It is a meta-meta-workflow: a workflow that builds workflows that build deliverables. The builder itself follows the composition system standard, making it self-describing and self-bootstrapping.

The output composition spec enables a powerful extensibility pattern:
- Example: `codebase_to_meta_v1` produces stakeholder.md, developer.md
- The output composition spec defines these as component types: `stakeholder_meta`, `developer_meta`
- Later, add `architecture_meta`, `user_guide_meta` as new compositions
- The workflow can produce these new output types without code changes

---

## 2. Component Schema (Layer 1)

In this composition system, "components" are the structural building blocks of workflows. Each component type represents a distinct aspect of workflow structure.

### 2.1 Component Types

| Component Type | Purpose | Required? | Cardinality |
|---|---|---|---|
| `step_definition` | A workflow step with type, purpose, inputs, outputs | Yes | Ordered list (N steps per workflow) |
| `role_policy` | Coder role assignment for a step | Yes | Singleton per step |
| `routing_pattern` | How steps connect (success, reject, refine) | Yes | Singleton per step |
| `prompt_pattern` | Prompt structure elements (self-critic, validation, etc.) | No | Unordered set per prompt-driven step |
| `artifact_contract` | Input/output artifact definitions | Yes | Unordered set per workflow |

### 2.2 Common Properties

All components share these properties:

| Property | Type | Required | Description |
|---|---|---|---|
| `component_id` | string | Yes | Unique identifier (format: `{type}-{name}-{seq}`) |
| `component_type` | enum | Yes | One of the 5 types in 2.1 |
| `name` | string | Yes | Human-readable display name |
| `version` | string | Yes | Semantic version (MAJOR.MINOR.PATCH) |
| `description` | string | Yes | What this component does |

### 2.3 Type-Specific Properties

#### Type: step_definition

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `step_name` | string | Yes | Lowercase with underscores | `"generate_component_schema"` |
| `step_type` | enum | Yes | Values: prompt, action | `"prompt"` |
| `purpose` | string | Yes | What this step achieves | `"Generate the component schema for Layer 1"` |
| `required_inputs` | array | No | Artifact keys this step reads | `["WORKFLOW_SPEC_FILE", "TEST_CRITERIA_FILE"]` |
| `produces` | array | Yes | Artifact keys this step writes | `["COMPONENT_SCHEMA_FILE"]` |
| `enable_notifications` | boolean | Yes | Send notifications on completion | `true` |
| `requires_human_approval_after` | boolean | Yes | Wait for human approval | `false` |

#### Type: role_policy

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `policy_name` | enum | Yes | Values: architect_standard, reviewer_standard, gatekeeper_standard, validation_standard, refine_standard | `"architect_standard"` |
| `assignment_rule` | string | Yes | When to use this policy | `"Generation steps (create documents, designs)"` |

#### Type: routing_pattern

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `onsuccess` | string | Yes | Next step on success | `"gatekeep_component_schema"` |
| `on_reject_refine` | object | No | Refinement loop config | See 2.3.2 |
| `max_iterations` | integer | No | Max refine iterations (if on_reject_refine) | `2` |
| `exhausted_failure_code` | string | No | Terminal failure code (if on_reject_refine) | `"COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED"` |
| `exhausted_failure_class` | string | No | Failure class (if on_reject_refine) | `"HUMAN_RETRY_REQUIRED"` |

##### 2.3.2 on_reject_refine structure

| Field | Type | Required | Description |
|---|---|---|---|
| `step` | string | Yes | Step to jump to on rejection |
| `artifact` | string | Yes | Artifact that triggered rejection |
| `max_iterations` | integer | Yes | Max refine loop iterations |
| `exhausted_failure_code` | string | Yes | Terminal failure code |
| `exhausted_failure_class` | string | Yes | Failure class |

#### Type: prompt_pattern

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `pattern_name` | enum | Yes | Values: self_critic, self_validation, context_verification, reference_inputs, generation_tasks, forbidden_content, output_instructions | `"self_critic"` |
| `sections` | array | Yes | Prompt sections this pattern adds | `["Challenge your reasoning before checking completeness"]` |

#### Type: artifact_contract

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `artifact_key` | string | Yes | Unique artifact identifier | `"COMPONENT_SCHEMA_FILE"` |
| `description` | string | Yes | What this artifact contains | `"Component schema for Layer 1"` |
| `filename_pattern` | string | No | Filename pattern with placeholders | `"COMPONENT_SCHEMA-{seq}.md"` |
| `required` | boolean | Yes | Whether this artifact is required | `true` |
| `produced_by` | string | No | Step that produces this artifact | `"generate_component_schema"` |

### 2.4 Component File Format

Components are not stored as individual files. They are defined inline in the workflow composition (Layer 2) and materialized as workflow.toml sections, prompt files, and Python code.

### 2.5 Validation Rules

- **Step name uniqueness:** No duplicate step_name values within a workflow
- **Valid step_type:** Must be one of: prompt, action
- **Valid policy_name:** Must be one of the 5 role policies
- **Artifact key format:** UPPER_SNAKE_CASE, _FILE suffix for documents
- **Routing completeness:** Every step must have onsuccess; review/refine steps must have on_reject_refine
- **Prompt pattern completeness:** Every prompt-driven step must have self_critic and self_validation patterns
- **Artifact flow integrity:** Every step's required_inputs must reference an artifact produced by a prior step or an input artifact

---

## 3. Composition Format (Layer 2)

### 3.1 Composition Structure

A workflow composition is a declarative definition with this structure:

| Field | Type | Required | Description |
|---|---|---|---|
| `workflow_name` | string | Yes | Unique workflow identifier |
| `workflow_label` | string | Yes | Human-readable display name |
| `job_prefix` | string | Yes | 4-6 character prefix for job IDs |
| `workflow_purpose` | string | Yes | What problem this workflow solves |
| `workflow_pattern` | enum | Yes | Pattern type (see 3.1.1) |
| `step_bindings` | array | Yes | Ordered list of step_definitions |
| `artifact_bindings` | object | Yes | Input and output artifact contracts |
| `output_composition_spec` | object | Yes | Composition spec for output artifacts (see 3.6) |

#### 3.1.1 Workflow Patterns

| Pattern | Description | Steps |
|---|---|---|
| `action_only` | All steps are deterministic Python operations | validate → publish → init → sync → stepCompletion |
| `prompt_driven` | LLM generates documents with review/refine loop | generate → review → [refine → review] → promote → stepCompletion |
| `mixed` | Combination of prompt and action steps | generate → review → refine → validate → promote → stepCompletion |
| `gatekeeper_pipeline` | Multi-phase with QC gates after each phase | generate → gatekeep → ... → generate_pkg → gatekeep → validate → review → [refine] → promote → stepCompletion |
| `meta_workflow_builder` | Workflow that builds workflows (this pattern) | generate_test_criteria → review → [refine] → ... → generate_package → validate → gatekeep → review → [refine] → promote → stepCompletion |

### 3.2 Binding Rules

| Binding Name | Component Type | Cardinality | Required? | Description |
|---|---|---|---|---|
| `steps` | step_definition | Ordered list | Yes | Workflow step sequence |
| `roles` | role_policy | Singleton per step | Yes | Each step must have a role |
| `routing` | routing_pattern | Singleton per step | Yes | Each step must have routing |
| `prompts` | prompt_pattern | Unordered set per prompt step | No | Prompt structure elements |
| `artifacts` | artifact_contract | Unordered set | Yes | Input/output artifact definitions |

### 3.3 Override Mechanism

```yaml
step_bindings:
  - step_name: "generate_component_schema"
    step_type: "prompt"
    purpose: "Generate the component schema for Layer 1"
    produces: ["COMPONENT_SCHEMA_FILE"]
    role:
      policy_name: "architect_standard"
    routing:
      onsuccess: "gatekeep_component_schema"
    prompt_patterns:
      - pattern_name: "self_critic"
      - pattern_name: "self_validation"
      - pattern_name: "reference_inputs"
```

**Rules:**
- Every step must bind a role_policy
- Every step must bind a routing_pattern
- Prompt-driven steps should bind prompt_patterns (self_critic, self_validation are mandatory)
- Action-driven steps do not bind prompt_patterns

### 3.4 Placeholder Resolution

| Data Source | Fields Provided | Required? |
|---|---|---|
| Input Spec | WORKFLOW_SPEC_FILE, domain_name, job_prefix | Yes |
| Governance | COMPOSITION_SYSTEM_STANDARD, GOVERNANCE_RUNTIME_ROOT | Yes |
| Runtime | job_id, seq, workspace_root | Yes |

**Resolution rules:**
- Placeholders in prompt templates resolved at runtime
- Artifact paths resolved via context_extensions.py
- Governance paths resolved via runtime_context module

### 3.5 Example Composition

```yaml
workflow_name: "workflow_builder_v3"
workflow_label: "Workflow Builder v3 — Composition System Builder with Output Composition"
job_prefix: "WBUILD3"
workflow_purpose: "Builds composition system workflows and generates output composition specs for extensibility"
workflow_pattern: "meta_workflow_builder"
step_bindings:
  - step_name: "generate_test_criteria"
    step_type: "prompt"
    purpose: "Generate acceptance criteria for the composition system"
    produces: ["TEST_CRITERIA_FILE"]
    role:
      policy_name: "architect_standard"
    routing:
      onsuccess: "review_test_criteria"
  - step_name: "review_test_criteria"
    step_type: "prompt"
    purpose: "Review acceptance criteria"
    produces: ["REVIEW_TEST_CRITERIA_FILE"]
    role:
      policy_name: "reviewer_standard"
    routing:
      onsuccess: "generate_component_schema"
      on_reject_refine:
        step: "refine_test_criteria"
        artifact: "REVIEW_TEST_CRITERIA_FILE"
        max_iterations: 2
        exhausted_failure_code: "TEST_CRITERIA_REVIEW_EXHAUSTED"
        exhausted_failure_class: "HUMAN_RETRY_REQUIRED"
  # ... more steps ...
  - step_name: "generate_output_composition_spec"
    step_type: "prompt"
    purpose: "Generate composition spec for the workflow's output artifacts"
    required_inputs: ["WORKFLOW_SPEC_FILE", "OPERATIONAL_WORKFLOW_FILE"]
    produces: ["OUTPUT_COMPOSITION_SPEC_FILE"]
    role:
      policy_name: "architect_standard"
    routing:
      onsuccess: "generate_package"
artifact_bindings:
  input_artifacts:
    - artifact_key: "WORKFLOW_SPEC_FILE"
      description: "Composition system specification"
      required: true
  output_artifacts:
    - artifact_key: "WORKFLOW_MANIFEST_FILE"
      description: "Generated workflow.toml"
      produced_by: "generate_package"
    - artifact_key: "OUTPUT_COMPOSITION_SPEC_FILE"
      description: "Composition spec for output artifacts"
      produced_by: "generate_output_composition_spec"
output_composition_spec:
  component_types:
    - type_name: "workflow_package_file"
      description: "A file in the generated workflow package"
      properties:
        - file_name: string
        - relative_path: string
        - purpose: string
  compositions:
    - composition_name: "standard_workflow_package"
      bindings:
        workflow_toml: { file_name: "workflow.toml", relative_path: ".", purpose: "Workflow manifest" }
        context_extensions: { file_name: "context_extensions.py", relative_path: ".", purpose: "Artifact key registration" }
        readme: { file_name: "README.md", relative_path: ".", purpose: "Workflow documentation" }
```

### 3.6 Output Composition Spec (NEW)

The output composition spec is a NEW artifact that the workflow builder generates. It treats the workflow's output artifacts as a composable component library.

**Purpose:** Enable extensibility — new output types can be added by composition without modifying the workflow.

**Structure:**
- Defines component types for each output artifact category
- Defines compositions for specific output configurations
- Defines resolution rules for generating outputs

**Example (codebase_to_meta_v1):**
- Component types: `stakeholder_meta`, `developer_meta`, `architecture_meta`, `user_guide_meta`
- Compositions: "stakeholder composition for product X", "developer composition for API docs"
- Outputs: Generated markdown files

---

## 4. Output Format (Layer 3)

### 4.1 Output Structure

The output is a workflow package directory with these files:

| File | Source | Description |
|---|---|---|
| `workflow.toml` | step_bindings + routing + artifacts | Workflow manifest with all step definitions |
| `context_extensions.py` | artifact_bindings | Artifact key registration and context injection |
| `actions.py` | action step_definitions (if any) | Custom action implementations |
| `prompts/*.txt` | prompt step_definitions + prompt_patterns | Prompt templates for each prompt-driven step |
| `README.md` | Generated | Workflow documentation |
| `.env.sample` | Generated (if needed) | Environment variable template |
| `config.json.sample` | Generated (if needed) | Runtime config template |
| `OUTPUT_COMPOSITION_SPEC.md` | output_composition_spec | Composition spec for output artifacts (NEW) |

### 4.2 Resolution Rules

- **All step_definitions expanded** into workflow.toml [[step]] sections with [step.artifacts] and [step.coder]
- **All role_policies resolved** to [step.coder] role_policy values
- **All routing_patterns resolved** to onsuccess and [step.on_reject_refine] configurations
- **All prompt_patterns expanded** into prompt template sections (Objective, Reference Inputs, Generation Tasks, Self-Critic, Self-Validation, Output Instructions, Forbidden Content)
- **OUTPUT_COMPOSITION_SPEC.md generated** by analyzing the input spec's output artifacts and defining them as a composable component library
- **Artifact paths resolved** via context_extensions.py register_artifact_keys()

### 4.3 Quality Requirements

- **No dangling step references:** Every onsuccess and on_reject_refine step must exist
- **No dangling artifact references:** Every required_inputs artifact must be produced by a prior step or be an input artifact
- **Complete prompt patterns:** Every prompt-driven step must have self_critic and self_validation sections
- **Valid role assignments:** Every step must have a role_policy
- **Artifact flow integrity:** Can trace each output artifact back to its producing step
- **Output composition spec completeness:** Every output artifact category must be defined as a component type in the output composition spec
- **Extensibility:** New output types can be added by composing new component types without modifying the workflow

### 4.4 Example Output (Skeleton)

```
workflow_builder_v3/
├── workflow.toml                    # Workflow manifest
├── context_extensions.py            # Artifact key registration
├── actions.py                       # Custom actions (validate_package_deterministic, promote_workflow_package)
├── prompts/
│   ├── 01_generate_test_criteria.txt
│   ├── 02_review_test_criteria.txt
│   ├── 03_refine_test_criteria.txt
│   ├── 04_generate_component_schema.txt
│   ├── 05_gatekeep_component_schema.txt
│   ├── ...
│   ├── 15_generate_output_composition_spec.txt    # NEW
│   └── 16_generate_package.txt
├── README.md                        # Workflow documentation
├── .env.sample                      # Environment variables (if needed)
├── config.json.sample               # Runtime config (if needed)
└── OUTPUT_COMPOSITION_SPEC.md       # NEW — Composition spec for output artifacts
```

---

## 5. Operational Requirements

### 5.1 Workflow Phases

| Phase | Purpose |
|---|---|
| **Foundation (TDD Loop)** | Generate acceptance criteria, review, refine (universal for all workflows) |
| **Component Schema** | Generate component schema for Layer 1, gatekeep |
| **Composition Format** | Generate composition format for Layer 2, gatekeep |
| **Output Format** | Generate output format for Layer 3, gatekeep |
| **Operational Workflow** | Generate operational workflow design, gatekeep |
| **Output Composition Spec** | Generate composition spec for output artifacts (NEW) |
| **Package Assembly** | Generate workflow package, validate, gatekeep, review, refine |
| **Promotion** | Promote workflow package to workflows/ directory |

### 5.2 Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `WORKFLOW_SPEC_FILE` | Composition system specification (input to the builder) | Yes |

### 5.3 Output Artifacts

| Artifact Key | Description | Produced By |
|---|---|---|
| `TEST_CRITERIA_FILE` | Acceptance criteria for the composition system | generate_test_criteria |
| `REVIEW_TEST_CRITERIA_FILE` | Review of acceptance criteria | review_test_criteria |
| `COMPONENT_SCHEMA_FILE` | Component schema for Layer 1 | generate_component_schema |
| `GATEKEEP_COMPONENT_SCHEMA_FILE` | Gatekeep review of component schema | gatekeep_component_schema |
| `COMPOSITION_FORMAT_FILE` | Composition format for Layer 2 | generate_composition_format |
| `GATEKEEP_COMPOSITION_FORMAT_FILE` | Gatekeep review of composition format | gatekeep_composition_format |
| `OUTPUT_FORMAT_FILE` | Output format for Layer 3 | generate_output_format |
| `GATEKEEP_OUTPUT_FORMAT_FILE` | Gatekeep review of output format | gatekeep_output_format |
| `OPERATIONAL_WORKFLOW_FILE` | Operational workflow design | generate_operational_workflow |
| `GATEKEEP_OPERATIONAL_WORKFLOW_FILE` | Gatekeep review of operational workflow | gatekeep_operational_workflow |
| `OUTPUT_COMPOSITION_SPEC_FILE` | Composition spec for output artifacts (NEW) | generate_output_composition_spec |
| `WORKFLOW_MANIFEST_FILE` | Generated workflow.toml | generate_package |
| `WORKFLOW_EXTENSIONS_FILE` | Generated context_extensions.py | generate_package |
| `WORKFLOW_ACTIONS_FILE` | Generated actions.py (if needed) | generate_package |
| `WORKFLOW_PROMPTS_INDEX_FILE` | Generated prompts index | generate_package |
| `WORKFLOW_README_FILE` | Generated README.md | generate_package |
| `VALIDATION_REPORT_FILE` | Deterministic validation report | validate_package_deterministic |
| `GATEKEEP_PACKAGE_FILE` | Gatekeep review of package | gatekeep_package |
| `REVIEW_FILE_SUGGESTED` | Final review of package | review_package |

### 5.4 Action Steps

Two custom action steps:

1. **validate_package_deterministic** — Deterministic validation of the generated workflow package. Checks:
   - workflow.toml syntax and structure
   - Step references (onsuccess, on_reject_refine) exist
   - Artifact references (required_inputs, produces) are valid
   - Role policies are valid
   - Prompt files exist for all prompt-driven steps

2. **promote_workflow_package** — Promote the generated workflow package to the workflows/ directory. Copies:
   - workflow.toml, context_extensions.py, actions.py, prompts/, README.md
   - .env.sample, config.json.sample (if present)
   - OUTPUT_COMPOSITION_SPEC.md (if present)

### 5.5 Domain-Specific Requirements

- **Self-bootstrapping:** The workflow builder should be able to process its own composition spec to generate the next version
- **Output composition spec:** Every generated workflow must include an OUTPUT_COMPOSITION_SPEC.md that treats its output artifacts as a composable component library
- **Extensibility:** The output composition spec must enable adding new output types by composition without modifying the workflow
- **TDD loop universal:** All workflows must start with generate_test_criteria → review → refine (TDD loop)
- **Gatekeeper pattern:** Meta-workflows must have gatekeeper steps after each major phase
- **Action reuse:** Check existing reusable actions before generating custom ones
- **Self-critic/self-validation:** All prompt-driven steps must include self-critic and self-validation sections

---

## 6. References

- **Composition System Standard:** `docs/repo/workflow_builder/current/COMPOSITION_SYSTEM_STANDARD.md`
- **Builder Requirements:** `docs/repo/workflow_builder/current/BUILDER_REQUIREMENTS.md`
- **Current workflow_builder_v2:** `workflows/workflow_builder_v2/`
- **Example specs:** `docs/repo/workflow_builder/specs/video_campaign_manuscript_v2.md`, `docs/repo/workflow_builder/specs/product_master_gen_v2_composition.md`

---

**End of Specification**
