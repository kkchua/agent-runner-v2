---
doc_type: "output_format"
lifecycle_status: "draft"
effective_version: "WBUILD2-4qpaocdy"
domain: "workflow_builder"
spec_source: "workflow_builder_v3.md"
composition_standard: "COMPOSITION_SYSTEM_STANDARD.md"
layer: 3
output_part_count: 3
resolution_rule_count: 7
quality_requirement_count: 8
---

# Output Format: Workflow Builder v3

## Overview

This document defines the output format (Layer 3) for the workflow_builder domain. In the three-layer architecture, Layer 3 is the resolved output layer -- the point where component references from the component library (Layer 1, COMPONENT_SCHEMA-001.md) and assembly instructions from the composition definitions (Layer 2, COMPOSITION_FORMAT-001.md) are fully expanded, overrides applied, placeholders resolved, and materialized as concrete files on disk. The workflow_builder domain produces meta-meta builders -- agents that themselves are composition systems capable of generating other workflow builders. Each resolved output is a self-contained, multi-file deliverable consisting of three parts: (1) a composition standard document that defines the component schema, composition format, and output format for the generated meta builder's target domain, (2) a specs directory structure accepting user-provided composition specifications, and (3) an executable workflow package containing the workflow manifest, prompt templates, action implementations, artifact key registrations, and documentation. The output is downstream-agnostic -- it describes WHAT the deliverable is (a complete, self-describing meta builder), not HOW to execute it, enabling downstream workflows to extract their specific concerns from the output without depending on the composition process that produced it.

---

## Output Structure

The resolved output is a directory containing three parts. This structure follows the spec Section 4.1 definition and the COMPOSITION_SYSTEM_STANDARD.md Section 5 output format pattern, adapted for the multi-file nature of meta builder deliverables.

### 3-Part Output Directory

```
{builder_name}/
+-- Standards/
|   +-- COMPOSITION_STANDARD.md
+-- Specs/
|   +-- (user-provided specs go here)
+-- workflow.toml
+-- context_extensions.py
+-- actions.py
+-- prompts/
|   +-- 01_{step_name}.txt
|   +-- 02_{step_name}.txt
|   +-- ...
|   +-- NN_{step_name}.txt
+-- README.md
+-- .env.sample            (if environment variables are needed)
+-- config.json.sample     (if runtime configuration is needed)
```

### Part 1: Standards/COMPOSITION_STANDARD.md

| Attribute | Value |
|---|---|
| Source | composition_standard_binding (Layer 2) |
| Format | Markdown with YAML frontmatter |
| Filename | COMPOSITION_STANDARD.md (always, per spec Section 5.5) |
| Path | {builder_name}/Standards/COMPOSITION_STANDARD.md |
| Required | Yes |

**YAML Frontmatter:**

| Field | Type | Required | Description |
|---|---|---|---|
| doc_type | string | Yes | Always "composition_standard" |
| lifecycle_status | string | Yes | Values: draft, active, deprecated |
| effective_version | string | Yes | Semantic version of the standard (from composition_standard_binding.overrides.standard_version) |
| domain | string | Yes | The target domain name (resolved from {domain_name} placeholder) |
| standard_name | string | Yes | Name of the standard (from composition_standard_binding.overrides.standard_name) |
| component_type_count | integer | Yes | Number of component types defined in the standard |
| schema_layer_count | integer | Yes | Always 3 (Component Schema, Composition Format, Output Format) |

**Required Sections:**

| Section | Purpose |
|---|---|
| Overview | Purpose of the standard, domain context, relationship to the three-layer architecture |
| Component Schema (Layer 1) | All component types with common and type-specific properties, validation rules, examples |
| Composition Format (Layer 2) | Binding rules, override mechanism, placeholder resolution, example composition |
| Output Format (Layer 3) | Output structure, resolution rules, quality requirements, output skeleton |
| Self-Validation | Verification that all 3 layers are defined and complete |

### Part 2: Specs/ Directory

| Attribute | Value |
|---|---|
| Source | domain_specs bindings (Layer 2) |
| Format | Directory structure |
| Required | Yes |
| Initial Content | Empty (accepts user-provided specs at runtime) |

The Specs/ directory is created as part of the output to establish the folder-based domain separation pattern. User-provided specifications are placed here when the generated meta builder is executed. The directory may contain a README.md describing the expected spec format based on the domain_spec components bound in the composition.

### Part 3: Workflow Package

| Attribute | Value |
|---|---|
| Source | step_bindings + routing + artifacts (Layer 2) |
| Format | Mixed (TOML, Python, Markdown, plain text) |
| Required | Yes |

#### workflow.toml

| Field | Type | Required | Description |
|---|---|---|---|
| [workflow] | table | Yes | Workflow metadata: name, label, job_prefix, pattern, description |
| [[step]] | array of tables | Yes | One entry per resolved step_definition (ordered) |
| [[step]].name | string | Yes | Step name (from step_definition.step_name after override) |
| [[step]].type | string | Yes | Step type: "prompt" or "action" (from step_definition.step_type) |
| [[step]].purpose | string | Yes | Step purpose description (from step_definition.purpose after override) |
| [[step]].onsuccess | string | Yes | Next step name on success (from routing_pattern.onsuccess) |
| [step.coder] | table | Yes (for prompt steps) | Coder role assignment (from role_policy) |
| [step.coder].role_policy | string | Yes | Role policy name (from role_policy.policy_name) |
| [step.artifacts] | table | Yes | Artifact bindings for this step |
| [step.artifacts].required_inputs | array | No | Artifact keys this step reads |
| [step.artifacts].produces | array | Yes | Artifact keys this step writes |
| [step.on_reject_refine] | table | Conditional | Refinement loop config (for review/gatekeep steps) |
| [step.on_reject_refine].step | string | Yes | Step to jump to on rejection |
| [step.on_reject_refine].artifact | string | Yes | Artifact that triggered rejection |
| [step.on_reject_refine].max_iterations | integer | Yes | Max refine loop iterations |
| [step.on_reject_refine].exhausted_failure_code | string | Yes | Terminal failure code |
| [step.on_reject_refine].exhausted_failure_class | string | Yes | Failure class |

#### context_extensions.py

| Field | Type | Required | Description |
|---|---|---|---|
| register_artifact_keys() | function | Yes | Registers all artifact keys with their resolved absolute paths |
| ARTIFACT_KEY_REGISTRY | dict | Yes | Maps each artifact_key to its filename pattern |

The context_extensions.py file registers every artifact_contract from the composition. Each artifact_key maps to a filename pattern. At runtime, the path resolution system converts these patterns into absolute paths using job_id, seq, and workspace_root from the Runtime data source.

#### actions.py

| Field | Type | Required | Description |
|---|---|---|---|
| Action functions | functions | Conditional | One function per action step (step_type = "action") |

The actions.py file is generated only when the composition includes at least one action-driven step. Each action function implements the deterministic operation specified by the step_definition.

#### prompts/ Directory

| Attribute | Value |
|---|---|
| Format | Plain text (.txt) files |
| Naming | NN_{step_name}.txt (NN is zero-padded sequence number) |
| Count | One file per prompt-driven step (step_type = "prompt") |

Each prompt file contains the fully expanded prompt template for its corresponding step. The prompt is assembled from the step's prompt_pattern bindings, with all placeholder values resolved.

#### README.md

| Attribute | Value |
|---|---|
| Format | Markdown |
| Required | Yes |

Documents the workflow: purpose, setup instructions, step sequence, artifact contracts, and usage guide.

#### .env.sample (Conditional)

Present when the workflow requires environment variables (e.g., API keys for action steps).

#### config.json.sample (Conditional)

Present when the workflow requires runtime configuration.

### Complete Output Example

```
creative_workflow_builder/
+-- Standards/
|   +-- COMPOSITION_STANDARD.md
+-- Specs/
+-- workflow.toml
+-- context_extensions.py
+-- actions.py
+-- prompts/
|   +-- 01_generate_test_criteria.txt
|   +-- 02_review_test_criteria.txt
|   +-- 03_refine_test_criteria.txt
|   +-- 04_generate_component_schema.txt
|   +-- 05_gatekeep_component_schema.txt
|   +-- ...
|   +-- 18_generate_package.txt
|   +-- 19_validate_package_deterministic.txt
|   +-- 20_gatekeep_package.txt
|   +-- 21_review_package.txt
|   +-- 22_refine_package.txt
|   +-- 23_promote_workflow_package.txt
+-- README.md
+-- .env.sample
```

---

## Resolution Rules

Resolution rules define how Layer 2 compositions are transformed into Layer 3 output files. Each rule describes how a specific component type's references are expanded into concrete output content.

### RR-001: step_definition Resolution

**Source:** step_bindings[] entries in the composition (Layer 2)
**Target:** workflow.toml [[step]] sections + prompts/*.txt files

Every step_definition component referenced in step_bindings is expanded into a [[step]] section in workflow.toml. The expansion process:

1. Look up the component by component_id from the component library (Layer 1)
2. Apply any overrides specified in the step binding (override wins on conflict)
3. Merge the base properties with overrides
4. Write the merged properties to the [[step]] section in workflow.toml
5. If step_type = "prompt", generate a prompts/NN_{step_name}.txt file with the expanded prompt template

**Resolution Example:**

Given a component reference:
```yaml
step_bindings:
  - component_id: "step-generate-component-schema-001"
    overrides:
      purpose: "Generate the component schema for the creative workflow domain"
```

And the base component (from Layer 1):
```yaml
step_name: "generate_component_schema"
step_type: "prompt"
purpose: "Generate the component schema for Layer 1"
required_inputs: ["WORKFLOW_SPEC_FILE", "TEST_CRITERIA_FILE"]
produces: ["COMPONENT_SCHEMA_FILE"]
enable_notifications: true
requires_human_approval_after: false
```

The resolved [[step]] section in workflow.toml:
```toml
[[step]]
name = "generate_component_schema"
type = "prompt"
purpose = "Generate the component schema for the creative workflow domain"
enable_notifications = true
requires_human_approval_after = false

[step.artifacts]
required_inputs = ["WORKFLOW_SPEC_FILE", "TEST_CRITERIA_FILE"]
produces = ["COMPONENT_SCHEMA_FILE"]
```

Note: `purpose` is overridden ("for the creative workflow domain" replaces "for Layer 1"). All other properties retain their base values.

### RR-002: role_policy Resolution

**Source:** role bindings within step_bindings[] entries
**Target:** [step.coder] sections in workflow.toml

Every role_policy component referenced in a step's role binding is expanded into a [step.coder] section. The expansion process:

1. Look up the role_policy by component_id from the component library
2. Apply any overrides specified in the role binding
3. Write the policy_name to [step.coder].role_policy

**Resolution Example:**

```yaml
role:
  component_id: "role-architect-standard-001"
```

Resolves to:
```toml
[step.coder]
role_policy = "architect_standard"
```

### RR-003: routing_pattern Resolution

**Source:** routing bindings within step_bindings[] entries
**Target:** [[step]].onsuccess and [step.on_reject_refine] in workflow.toml

Every routing_pattern component referenced in a step's routing binding is expanded into routing configuration. The expansion process:

1. Look up the routing_pattern by component_id from the component library
2. Apply any overrides (commonly, onsuccess is overridden per-composition)
3. Write onsuccess to [[step]].onsuccess
4. If on_reject_refine is present (after override), write the [step.on_reject_refine] sub-table

**Resolution Example:**

```yaml
routing:
  component_id: "routing-review-test-criteria-001"
  overrides:
    onsuccess: "generate_component_schema"
    on_reject_refine:
      step: "refine_test_criteria"
      artifact: "TEST_CRITERIA_FILE"
      max_iterations: 2
      exhausted_failure_code: "TEST_CRITERIA_REVIEW_EXHAUSTED"
      exhausted_failure_class: "HUMAN_RETRY_REQUIRED"
```

Resolves to:
```toml
[[step]]
name = "review_test_criteria"
# ... other properties ...
onsuccess = "generate_component_schema"

[step.on_reject_refine]
step = "refine_test_criteria"
artifact = "TEST_CRITERIA_FILE"
max_iterations = 2
exhausted_failure_code = "TEST_CRITERIA_REVIEW_EXHAUSTED"
exhausted_failure_class = "HUMAN_RETRY_REQUIRED"
```

### RR-004: prompt_pattern Resolution

**Source:** prompt_patterns[] bindings within step_bindings[] entries (for prompt-driven steps only)
**Target:** prompts/NN_{step_name}.txt files

Every prompt_pattern component referenced in a step's prompt_patterns binding contributes sections to the step's prompt template file. The expansion process:

1. For each prompt_pattern in the binding, look up the component by component_id
2. Extract the sections array from the prompt_pattern
3. Assemble the prompt template by combining sections in the standard order:
   - Objective (from step purpose)
   - Reference Inputs (from reference_inputs pattern)
   - Generation Tasks (from generation_tasks pattern)
   - Self-Critic (from self_critic pattern)
   - Self-Validation (from self_validation pattern)
   - Context Verification (from context_verification pattern, if present)
   - Forbidden Content (from forbidden_content pattern)
   - Output Instructions (from output_instructions pattern)
4. Resolve all {ARTIFACT_KEY} placeholders in the prompt template to absolute file paths

**Note:** Action-driven steps (step_type = "action") do not have prompt patterns and do not generate prompt files.

### RR-005: artifact_contract Resolution

**Source:** artifact_bindings.input_artifacts[] and artifact_bindings.output_artifacts[]
**Target:** context_extensions.py register_artifact_keys()

Every artifact_contract component referenced in artifact_bindings is registered in context_extensions.py. The expansion process:

1. Look up the artifact_contract by component_id from the component library
2. Apply any overrides (commonly produced_by and description are overridden)
3. Register the artifact_key with its filename_pattern in ARTIFACT_KEY_REGISTRY
4. Generate the register_artifact_keys() function that maps each key to its resolved path pattern

**Resolution Example:**

```yaml
artifact_bindings:
  output_artifacts:
    - component_id: "artifact-component-schema-file-001"
      overrides:
        produced_by: "generate_component_schema"
        description: "Component schema for the creative workflow domain"
```

Resolves to context_extensions.py content:
```python
ARTIFACT_KEY_REGISTRY = {
    "COMPONENT_SCHEMA_FILE": "COMPONENT_SCHEMA-{seq}.md",
    # ... other artifact keys ...
}

def register_artifact_keys(known_paths):
    for key, pattern in ARTIFACT_KEY_REGISTRY.items():
        known_paths[key] = pattern
```

### RR-006: composition_standard Resolution

**Source:** composition_standard_binding (singleton)
**Target:** Standards/COMPOSITION_STANDARD.md

The composition_standard component referenced in composition_standard_binding is expanded into the full Standards/COMPOSITION_STANDARD.md document. The expansion process:

1. Look up the composition_standard by component_id from the component library
2. Apply overrides (standard_name, standard_version, component_types_defined, schema_sections, extensibility_model are all overridden per-composition)
3. Generate the full COMPOSITION_STANDARD.md document with the overridden values
4. The document defines the 3-layer schema (Component Schema, Composition Format, Output Format) for the generated meta builder's target domain

**Resolution Example:**

```yaml
composition_standard_binding:
  component_id: "standard-base-composition-001"
  overrides:
    standard_name: "CREATIVE_WORKFLOW_STANDARD"
    standard_version: "1.0.0"
    component_types_defined:
      - "agent_md_analysis"
      - "prompt_template"
      - "api_action"
```

Resolves to Standards/COMPOSITION_STANDARD.md frontmatter:
```yaml
---
doc_type: "composition_standard"
lifecycle_status: "active"
effective_version: "1.0.0"
domain: "creative_workflow"
standard_name: "CREATIVE_WORKFLOW_STANDARD"
component_type_count: 3
schema_layer_count: 3
---
```

### RR-007: Placeholder Resolution

**Source:** {placeholder} tokens in override values and prompt templates
**Target:** All output files

Placeholders are resolved from three data sources in the following order:

| Priority | Data Source | Fields Provided | Resolution Mechanism |
|---|---|---|---|
| 1 | Governance | BASE_COMPOSITION_STANDARD, GOVERNANCE_RUNTIME_ROOT | runtime_context module |
| 2 | Input Spec | WORKFLOW_SPEC_FILE, domain_name, job_prefix | Loaded from WORKFLOW_SPEC_FILE at start |
| 3 | Runtime | job_id, seq, workspace_root | Computed during execution |
| 4 | Prompt templates | {ARTIFACT_KEY} references | context_extensions.py at coder invocation |

**Unresolved Placeholder Handling:**

If a placeholder cannot be resolved from any available data source, it is flagged in the output as:

```
{UNRESOLVED: field_name}
```

For example, if {custom_api_key} cannot be resolved:
```toml
# In workflow.toml or prompt template:
api_endpoint = "{UNRESOLVED: custom_api_key}"
```

Unresolved placeholders are flagged but do not block the workflow. They are noted in the validation report.

---

## Required Sections

The output defines the following required sections, organized by output part. Each section must be present in every resolved output. These sections are domain-defined based on the workflow_builder domain's 3-part output structure.

### Standards/COMPOSITION_STANDARD.md Required Sections

| Section ID | Section Name | Purpose | Content |
|---|---|---|---|
| STD-001 | Overview | Purpose and domain context of the standard | Standard name, version, domain, component types overview, relationship to 3-layer architecture |
| STD-002 | Component Schema (Layer 1) | Defines all component types for the target domain | Common properties, type-specific properties per component type, validation rules, example components |
| STD-003 | Composition Format (Layer 2) | Defines how components are assembled | Binding rules, override mechanism, placeholder resolution data sources, example composition |
| STD-004 | Output Format (Layer 3) | Defines the resolved output structure | Output file structure, resolution rules, quality requirements, output skeleton |
| STD-005 | Self-Validation | Verifies completeness of the standard | Enumeration of all 3 layers, verification that each layer is defined |

### Workflow Package Required Files

| File ID | Filename | Purpose | Content |
|---|---|---|---|
| WP-001 | workflow.toml | Workflow manifest | All steps with routing, coder roles, artifact bindings |
| WP-002 | context_extensions.py | Artifact key registration | ARTIFACT_KEY_REGISTRY dict and register_artifact_keys() function |
| WP-003 | prompts/*.txt | Prompt templates | One file per prompt-driven step with fully expanded prompt content |
| WP-004 | README.md | Workflow documentation | Purpose, setup, step sequence, artifact contracts, usage guide |
| WP-005 | actions.py | Action implementations | One function per action-driven step (conditional -- required only if action steps exist) |

### Specs/ Directory Requirements

| Directory ID | Directory Name | Purpose | Content |
|---|---|---|---|
| SP-001 | Specs/ | User-provided specification storage | Empty at generation time; receives user specs at runtime |

### Section Dependency Rules

| Rule | Description |
|---|---|
| STD-002 depends on | composition_standard_binding.overrides.component_types_defined |
| STD-003 depends on | STD-002 (binding rules reference component types from Layer 1) |
| STD-004 depends on | STD-002, STD-003 (output rules reference both components and compositions) |
| WP-001 depends on | step_bindings, role bindings, routing bindings from Layer 2 |
| WP-002 depends on | artifact_bindings from Layer 2 |
| WP-003 depends on | step_bindings filtered by step_type = "prompt" + prompt_pattern bindings |
| WP-004 depends on | All other workflow package files (documents them) |
| WP-005 depends on | step_bindings filtered by step_type = "action" |

---

## Quality Requirements

All resolved outputs must pass these quality checks. Each requirement is derived from the spec Section 4.3 quality requirements and the test criteria TC-OF-017 and TC-GOF-001 through TC-GOF-014.

### QR-001: No Dangling Step References

Every onsuccess and on_reject_refine step target must exist as a defined [[step]] in workflow.toml. No step may reference a non-existent step name.

**Verification method:** Extract all step names from [[step]] sections. Extract all onsuccess and on_reject_refine.step values. Verify every referenced name exists in the step name set.

**Severity:** CRITICAL (blocks output acceptance)

### QR-002: No Dangling Artifact References

Every required_inputs artifact key must reference an artifact that is either declared as an input_artifact in the artifact_bindings (no produced_by) or produced by a step that executes before the consuming step.

**Verification method:** Build a set of all declared input artifacts and all produced artifacts with their producing step positions. For each step's required_inputs, verify each key exists in the artifact set and was produced before the consuming step's position.

**Severity:** CRITICAL (blocks output acceptance)

### QR-003: Complete Prompt Patterns

Every prompt-driven step (step_type = "prompt") must have a corresponding prompt file in prompts/. The prompt file must include at minimum: objective, reference inputs section, self-critic section, self-validation section, and output instructions section.

**Verification method:** For each step with type = "prompt", verify a corresponding prompts/NN_{step_name}.txt file exists. Parse the file to verify required sections are present.

**Severity:** MAJOR (blocks output acceptance for prompt steps)

### QR-004: Valid Role Assignments

Every step must have a [step.coder] section with a role_policy value that is one of the 5 defined policies: architect_standard, reviewer_standard, gatekeeper_standard, validation_standard, refine_standard.

**Verification method:** For each [[step]], verify [step.coder].role_policy is present and is a valid policy name.

**Severity:** CRITICAL (blocks output acceptance)

### QR-005: Artifact Flow Integrity

Every step's required_inputs must reference an artifact that is either declared as an input artifact at the workflow level or produced by a step that executes before the consuming step. No step may consume an artifact that has not been produced by a prior step or declared as an input.

**Verification method:** Trace each output artifact back to its producing step. Verify temporal ordering: consuming step position > producing step position in the step sequence.

**Severity:** CRITICAL (blocks output acceptance)

### QR-006: Composition Standard Completeness

The Standards/COMPOSITION_STANDARD.md must define all 3 layers: Component Schema (Layer 1), Composition Format (Layer 2), and Output Format (Layer 3). Each layer must contain the required sections defined in this document.

**Verification method:** Parse COMPOSITION_STANDARD.md and verify sections STD-002, STD-003, and STD-004 are present and non-empty.

**Severity:** CRITICAL (blocks output acceptance)

### QR-007: Output Variance Feasibility

Each output_variance in the composition must have a valid and feasible combination of component_requirements. The declared component types must be sufficient to produce the declared output_files.

**Verification method:** For each output_variance, verify that component_requirements include the minimum types needed for the output_files. For example, if output_files includes "actions.py", then step_definition must be in component_requirements.

**Severity:** MAJOR (warning, does not block acceptance)

### QR-008: Cross-File Consistency

No contradictions may exist between output sections. Step names in workflow.toml must match step names in prompts/ filenames. Artifact keys in workflow.toml must match artifact keys in context_extensions.py. Artifact keys in prompt templates must match registered keys.

**Verification method:**
- Extract step names from workflow.toml [[step]] sections and compare with prompt filenames
- Extract artifact keys from workflow.toml [step.artifacts] and compare with ARTIFACT_KEY_REGISTRY in context_extensions.py
- Extract {ARTIFACT_KEY} references from prompt .txt files and compare with ARTIFACT_KEY_REGISTRY

**Severity:** CRITICAL (blocks output acceptance)

---

## Downstream Extraction Contracts

Downstream workflows consume the resolved output by extracting specific sections and fields. The output is downstream-agnostic -- it describes WHAT the deliverable is, not HOW to produce it. Each downstream workflow defines its own extraction contract specifying which parts of the output it reads.

### Contract DEC-001: Workflow Executor Extraction

**Consumer:** The workflow runner (daemon, CLI, or worker mode) that executes the generated meta builder.

**Extracts:**

| Section | Fields Extracted | Purpose |
|---|---|---|
| workflow.toml | [[step]] sections (name, type, purpose, onsuccess) | Build the step execution pipeline |
| workflow.toml | [step.coder].role_policy | Assign coder roles per step |
| workflow.toml | [step.on_reject_refine] | Configure refinement loops |
| workflow.toml | [step.artifacts].required_inputs, produces | Wire artifact dependencies |
| context_extensions.py | ARTIFACT_KEY_REGISTRY | Register artifact paths |
| prompts/*.txt | Full file content | Feed to LLM coder for prompt-driven steps |
| actions.py | Function definitions | Execute for action-driven steps |

**Contract guarantee:** The workflow.toml contains all information needed to execute the workflow. No external lookups into Standards/COMPOSITION_STANDARD.md are required for execution.

### Contract DEC-002: Package Validator Extraction

**Consumer:** The validate_package_deterministic action step that performs deterministic validation of the generated workflow package.

**Extracts:**

| Section | Fields Extracted | Purpose |
|---|---|---|
| workflow.toml | All [[step]] sections | Verify step syntax and structure |
| workflow.toml | All onsuccess values | Verify step references exist |
| workflow.toml | All [step.artifacts].required_inputs and produces | Verify artifact references are valid |
| workflow.toml | All [step.coder].role_policy values | Verify role policies are valid |
| prompts/*.txt | File existence | Verify prompt files exist for all prompt steps |
| context_extensions.py | ARTIFACT_KEY_REGISTRY | Verify artifact key registrations match workflow.toml |
| actions.py | Function existence | Verify action functions exist for all action steps |
| Standards/COMPOSITION_STANDARD.md | File existence and well-formedness | Verify standard file exists and has correct frontmatter |

**Contract guarantee:** The validator can perform all checks using only the output files. No access to the component library or composition is needed.

### Contract DEC-003: Meta Builder Bootstrap Extraction

**Consumer:** A downstream workflow that uses the generated meta builder to build another composition system (self-bootstrapping scenario).

**Extracts:**

| Section | Fields Extracted | Purpose |
|---|---|---|
| Standards/COMPOSITION_STANDARD.md | Component Schema section | Discover what component types the meta builder supports |
| Standards/COMPOSITION_STANDARD.md | Composition Format section | Understand how to compose components for this builder |
| Standards/COMPOSITION_STANDARD.md | Output Format section | Understand what outputs the builder produces |
| Standards/COMPOSITION_STANDARD.md | component_types_defined | Know which component types are available |
| Standards/COMPOSITION_STANDARD.md | extensibility_model | Understand how to extend the component schema |
| workflow.toml | [[step]] sections | Understand the builder's workflow steps |
| README.md | Full content | Understand setup and usage |

**Contract guarantee:** Standards/COMPOSITION_STANDARD.md is self-describing. A downstream workflow can understand the meta builder's capabilities by reading this single file without needing to read the workflow package or other output parts.

### Platform-Specific Considerations

| Platform | Consideration |
|---|---|
| daemon | The workflow runner in daemon mode reads workflow.toml and spawns subprocesses per step. Artifact paths are resolved via context_extensions.py at each step invocation. The daemon does not read Standards/COMPOSITION_STANDARD.md during execution. |
| cli | The CLI runner reads workflow.toml and executes steps sequentially. Same extraction as daemon but in a single process. |
| worker | The worker mode connects to the backend for state management. Artifact paths are synchronized via the backend. The worker extracts the same workflow.toml structure. |
| manual | Manual mode adds human approval gating. The human reviewer extracts the README.md for workflow understanding and individual prompt files for step-by-step review. |

---

## Example Outputs

This section provides a complete example output demonstrating all resolution rules, required sections, and quality requirements in action.

### Example: creative_workflow_builder Resolved Output

This example shows the resolved output for a meta builder that generates creative media workflows. The example traces from composition bindings (Layer 2) to resolved files (Layer 3).

#### File 1: Standards/COMPOSITION_STANDARD.md

```markdown
---
doc_type: "composition_standard"
lifecycle_status: "active"
effective_version: "1.0.0"
domain: "creative_workflow"
standard_name: "CREATIVE_WORKFLOW_STANDARD"
component_type_count: 3
schema_layer_count: 3
---

# Composition Standard: Creative Workflow Standard

## Overview

This standard defines the composition system for creative media workflows.
Domain: creative_workflow. The standard defines 3 component types
across 3 schema layers.

## Component Schema (Layer 1)

### Common Properties

All components share: component_id, component_type, name, version, description.

### Component Types

#### Type 1: agent_md_analysis
- Purpose: Analyzes agent-md input files
- Properties: analysis_type, input_format, output_structure
- Required: Yes

#### Type 2: prompt_template
- Purpose: Defines prompt structures for LLM steps
- Properties: template_type, sections, variables
- Required: Yes

#### Type 3: api_action
- Purpose: Defines API integration actions
- Properties: endpoint, method, auth_type, payload_schema
- Required: No

## Composition Format (Layer 2)

### Binding Rules
- steps: Ordered list of step_definitions (Required)
- roles: Singleton role_policy per step (Required)
- routing: Singleton routing_pattern per step (Required)
- prompts: Unordered set of prompt_patterns per prompt step (Optional)
- artifacts: Unordered set of artifact_contracts (Required)

### Override Mechanism
Overrides merge with base component properties. Override wins on conflict.
Common properties are not overridable.

### Placeholder Resolution
Data sources: Input Spec, Governance, Runtime.
Unresolved placeholders flagged as {UNRESOLVED: field_name}.

## Output Format (Layer 3)

### Output Structure
- workflow.toml: Step definitions with routing and roles
- prompts/: Prompt template files
- context_extensions.py: Artifact key registrations
- README.md: Workflow documentation

### Resolution Rules
- All component_id references expanded
- All overrides applied (override wins on conflict)
- All placeholders resolved or flagged

### Quality Requirements
- No dangling step references
- No dangling artifact references
- Complete prompt patterns
- Valid role assignments
- Cross-file consistency

## Self-Validation

- Layer 1 (Component Schema): DEFINED (3 types)
- Layer 2 (Composition Format): DEFINED (binding rules, overrides, placeholders)
- Layer 3 (Output Format): DEFINED (structure, resolution, quality)
```

#### File 2: workflow.toml (excerpt showing resolved steps)

```toml
[workflow]
name = "creative_workflow_builder"
label = "Creative Workflow Builder"
job_prefix = "CWFBLD"
pattern = "meta_meta_builder"
description = "Generates creative media workflows from agent-md files"

[[step]]
name = "generate_test_criteria"
type = "prompt"
purpose = "Generate acceptance criteria for the creative workflow builder"
onsuccess = "review_test_criteria"
enable_notifications = true
requires_human_approval_after = false

[step.coder]
role_policy = "architect_standard"

[step.artifacts]
produces = ["TEST_CRITERIA_FILE"]

[[step]]
name = "review_test_criteria"
type = "prompt"
purpose = "Review acceptance criteria for completeness and correctness"
onsuccess = "generate_component_schema"
enable_notifications = true
requires_human_approval_after = false

[step.coder]
role_policy = "reviewer_standard"

[step.artifacts]
required_inputs = ["TEST_CRITERIA_FILE"]
produces = ["REVIEW_TEST_CRITERIA_FILE"]

[step.on_reject_refine]
step = "refine_test_criteria"
artifact = "TEST_CRITERIA_FILE"
max_iterations = 2
exhausted_failure_code = "TEST_CRITERIA_REVIEW_EXHAUSTED"
exhausted_failure_class = "HUMAN_RETRY_REQUIRED"

[[step]]
name = "generate_component_schema"
type = "prompt"
purpose = "Generate the component schema for the creative workflow domain"
onsuccess = "gatekeep_component_schema"
enable_notifications = true
requires_human_approval_after = false

[step.coder]
role_policy = "architect_standard"

[step.artifacts]
required_inputs = ["WORKFLOW_SPEC_FILE", "TEST_CRITERIA_FILE"]
produces = ["COMPONENT_SCHEMA_FILE"]

# ... additional steps following the same pattern ...

[[step]]
name = "stepCompletion"
type = "action"
purpose = "Mark creative workflow builder execution as complete"

[step.coder]
role_policy = "validation_standard"
```

#### File 3: context_extensions.py (resolved)

```python
ARTIFACT_KEY_REGISTRY = {
    "WORKFLOW_SPEC_FILE": "{WORKFLOW_SPEC_FILE}",
    "TEST_CRITERIA_FILE": "TEST_CRITERIA-{seq}.md",
    "REVIEW_TEST_CRITERIA_FILE": "REVIEW_TEST_CRITERIA-{seq}.md",
    "COMPONENT_SCHEMA_FILE": "COMPONENT_SCHEMA-{seq}.md",
    "GATEKEEP_COMPONENT_SCHEMA_FILE": "GATEKEEP_COMPONENT_SCHEMA-{seq}.md",
    "COMPOSITION_FORMAT_FILE": "COMPOSITION_FORMAT-{seq}.md",
    "GATEKEEP_COMPOSITION_FORMAT_FILE": "GATEKEEP_COMPOSITION_FORMAT-{seq}.md",
    "OUTPUT_FORMAT_FILE": "OUTPUT_FORMAT-{seq}.md",
    "GATEKEEP_OUTPUT_FORMAT_FILE": "GATEKEEP_OUTPUT_FORMAT-{seq}.md",
    "OPERATIONAL_WORKFLOW_FILE": "OPERATIONAL_WORKFLOW-{seq}.md",
    "GATEKEEP_OPERATIONAL_WORKFLOW_FILE": "GATEKEEP_OPERATIONAL_WORKFLOW-{seq}.md",
    "COMPOSITION_STANDARD_FILE": "COMPOSITION_STANDARD-{seq}.md",
    "GATEKEEP_COMPOSITION_STANDARD_FILE": "GATEKEEP_COMPOSITION_STANDARD-{seq}.md",
    "META_COMPOSITION_SPEC_FILE": "META_COMPOSITION_SPEC-{seq}.md",
    "WORKFLOW_MANIFEST_FILE": "workflow.toml",
    "WORKFLOW_EXTENSIONS_FILE": "context_extensions.py",
    "WORKFLOW_ACTIONS_FILE": "actions.py",
    "WORKFLOW_PROMPTS_INDEX_FILE": "PROMPTS_INDEX-{seq}.md",
    "WORKFLOW_README_FILE": "README.md",
    "VALIDATION_REPORT_FILE": "VALIDATION_REPORT-{seq}.md",
    "GATEKEEP_PACKAGE_FILE": "GATEKEEP_PACKAGE-{seq}.md",
    "REVIEW_FILE_SUGGESTED": "REVIEW-{seq}.md",
}

def register_artifact_keys(known_paths):
    """Register all artifact keys with their filename patterns."""
    for key, pattern in ARTIFACT_KEY_REGISTRY.items():
        known_paths[key] = pattern
```

#### File 4: prompts/04_generate_component_schema.txt (excerpt)

```text
# Objective

Generate the component schema for the creative workflow domain.
This step produces the COMPONENT_SCHEMA_FILE.

## Reference Inputs

Read the following files before producing any output:
- WORKFLOW_SPEC_FILE: {WORKFLOW_SPEC_FILE}
  (Section 2: Component Schema -- defines the component types)
- TEST_CRITERIA_FILE: {TEST_CRITERIA_FILE}
  (Section 2: Criteria for generate_component_schema)

## Generation Tasks

Produce a component schema document with these sections:
1. Overview -- domain context and component type count
2. Common Properties -- 5 required properties shared by all types
3. Component Types -- for each type: properties, validation rules, example
4. Validation Rules (Global) -- all enforceable rules
5. Extensibility Model -- how to add new types
6. Self-Validation -- verification that all types are defined

## Self-Critic

Challenge your reasoning before checking completeness:
- Are you introducing component types not in the spec?
- Did you cover all 3 component types from the spec?
- Are your validation rules specific and enforceable?

## Self-Validation

Before completing, verify:
- Component type count matches the spec (3 types for creative_workflow)
- Each type has common + type-specific properties documented
- All validation rules are present
- At least one example per type

## Output Instructions

Write the output to: {COMPONENT_SCHEMA_FILE}
Format: Markdown with YAML frontmatter
ASCII-only content. No em-dashes, no curly quotes.
```

### Resolution Trace for This Example

The following table traces how each output element resolves from its Layer 2 source:

| Output Element | Layer 2 Source | Resolution Rule | Overrides Applied |
|---|---|---|---|
| [[step]] generate_test_criteria | step-generate-test-criteria-001 | RR-001 | purpose overridden to "for the creative workflow builder" |
| [step.coder] architect_standard | role-architect-standard-001 | RR-002 | No override |
| onsuccess = "review_test_criteria" | routing-generate-test-criteria-001 | RR-003 | onsuccess overridden to "review_test_criteria" |
| prompts/01_generate_test_criteria.txt | prompt_pattern bindings | RR-004 | {ARTIFACT_KEY} placeholders resolved at runtime |
| ARTIFACT_KEY_REGISTRY entry for TEST_CRITERIA_FILE | artifact-test-criteria-file-001 | RR-005 | produced_by overridden to "generate_test_criteria" |
| Standards/COMPOSITION_STANDARD.md | standard-base-composition-001 | RR-006 | standard_name overridden to "CREATIVE_WORKFLOW_STANDARD", component_types_defined overridden to creative domain types |
| {domain_name} in purpose text | N/A (placeholder) | RR-007 | Resolved from Input Spec to "creative_workflow" |

---

## Self-Validation

This section verifies the completeness and correctness of the output format defined above.

### Output Structure Verification

| Check ID | Check | Result |
|---|---|---|
| SV-001 | 3-part output structure defined (Standards/, Specs/, Workflow package) | PASS -- Section "Output Structure" defines all 3 parts |
| SV-002 | workflow.toml field definitions complete | PASS -- All [[step]] fields documented with type, required status, description |
| SV-003 | context_extensions.py structure defined | PASS -- ARTIFACT_KEY_REGISTRY and register_artifact_keys() documented |
| SV-004 | prompts/ directory naming convention defined | PASS -- NN_{step_name}.txt format documented |
| SV-005 | Standards/COMPOSITION_STANDARD.md filename fixed | PASS -- Consistent filename per spec Section 5.5 |
| SV-006 | Conditional files documented | PASS -- actions.py, .env.sample, config.json.sample conditional requirements noted |

### Resolution Rule Verification

| Check ID | Check | Result |
|---|---|---|
| SV-007 | step_definition resolution defined (RR-001) | PASS -- Expands to [[step]] sections with example |
| SV-008 | role_policy resolution defined (RR-002) | PASS -- Expands to [step.coder] with example |
| SV-009 | routing_pattern resolution defined (RR-003) | PASS -- Expands to onsuccess and [step.on_reject_refine] with example |
| SV-010 | prompt_pattern resolution defined (RR-004) | PASS -- Expands to prompt template files with assembly order |
| SV-011 | artifact_contract resolution defined (RR-005) | PASS -- Expands to context_extensions.py with example |
| SV-012 | composition_standard resolution defined (RR-006) | PASS -- Expands to Standards/COMPOSITION_STANDARD.md with example |
| SV-013 | Placeholder resolution defined (RR-007) | PASS -- 3 data sources, resolution order, unresolved handling documented |

### Quality Requirement Verification

| Check ID | Check | Result |
|---|---|---|
| SV-014 | No dangling step references (QR-001) | PASS -- Defined with verification method |
| SV-015 | No dangling artifact references (QR-002) | PASS -- Defined with verification method |
| SV-016 | Complete prompt patterns (QR-003) | PASS -- Defined with verification method |
| SV-017 | Valid role assignments (QR-004) | PASS -- Defined with verification method |
| SV-018 | Artifact flow integrity (QR-005) | PASS -- Defined with verification method |
| SV-019 | Composition standard completeness (QR-006) | PASS -- Defined with verification method |
| SV-020 | Output variance feasibility (QR-007) | PASS -- Defined with verification method |
| SV-021 | Cross-file consistency (QR-008) | PASS -- Defined with verification method |

### Downstream Contract Verification

| Check ID | Check | Result |
|---|---|---|
| SV-022 | Workflow executor extraction contract defined (DEC-001) | PASS -- Fields and guarantees documented |
| SV-023 | Package validator extraction contract defined (DEC-002) | PASS -- Fields and guarantees documented |
| SV-024 | Meta builder bootstrap extraction contract defined (DEC-003) | PASS -- Fields and guarantees documented |
| SV-025 | Platform-specific considerations documented | PASS -- daemon, cli, worker, manual modes covered |

### Test Criteria Traceability

| Test Criteria | Covered By | Status |
|---|---|---|
| TC-OF-001 (3-part output structure) | Output Structure section | COVERED |
| TC-OF-002 (workflow package files) | Output Structure > Part 3 | COVERED |
| TC-OF-003 (file structure skeleton) | Output Structure > Complete Output Example | COVERED |
| TC-OF-004 (COMPOSITION_STANDARD.md filename) | Output Structure > Part 1 | COVERED |
| TC-OF-005 (step_definitions expanded) | Resolution Rules > RR-001 | COVERED |
| TC-OF-006 (role_policies resolved) | Resolution Rules > RR-002 | COVERED |
| TC-OF-007 (routing_patterns resolved) | Resolution Rules > RR-003 | COVERED |
| TC-OF-008 (prompt_patterns expanded) | Resolution Rules > RR-004 | COVERED |
| TC-OF-009 (composition standard generated) | Resolution Rules > RR-006 | COVERED |
| TC-OF-010 (artifact paths via context_extensions.py) | Resolution Rules > RR-005 | COVERED |
| TC-OF-011 (placeholders resolved) | Resolution Rules > RR-007 | COVERED |
| TC-OF-012 (unresolved placeholders flagged) | Resolution Rules > RR-007 | COVERED |
| TC-OF-013 (self-contained output) | Overview + Quality Requirements | COVERED |
| TC-OF-014 (no external lookups) | Overview + Downstream Contracts | COVERED |
| TC-OF-015 (extraction contracts) | Downstream Extraction Contracts | COVERED |
| TC-OF-016 (downstream-agnostic) | Overview + Downstream Contracts | COVERED |
| TC-OF-017 (quality requirements) | Quality Requirements section | COVERED |
| TC-OF-018 (no contradictions) | Quality Requirements > QR-008 | COVERED |
| TC-OF-019 (self-check) | Self-Validation section | COVERED |
| TC-OF-020 (all resolution rules defined) | Self-Validation > SV-007 to SV-013 | COVERED |
| TC-OF-021 (3-part structure matches spec) | Self-Validation > SV-001 | COVERED |
| TC-GOF-001 (component_ids expanded) | Resolution Rules > RR-001 to RR-006 | COVERED |
| TC-GOF-002 (step_definitions in workflow.toml) | Resolution Rules > RR-001 | COVERED |
| TC-GOF-003 (no dangling step references) | Quality Requirements > QR-001 | COVERED |
| TC-GOF-004 (placeholders resolved or flagged) | Resolution Rules > RR-007 | COVERED |
| TC-GOF-005 (no unresolved without marker) | Resolution Rules > RR-007 | COVERED |
| TC-GOF-006 (3 output parts present) | Quality Requirements > QR-006 + Output Structure | COVERED |
| TC-GOF-007 (workflow package files) | Output Structure > Part 3 | COVERED |
| TC-GOF-008 (actions.py conditional) | Output Structure > Part 3 > actions.py | COVERED |
| TC-GOF-009 (no contradictions) | Quality Requirements > QR-008 | COVERED |
| TC-GOF-010 (artifact key consistency) | Quality Requirements > QR-008 | COVERED |
| TC-GOF-011 (downstream extraction feasible) | Downstream Extraction Contracts | COVERED |
| TC-GOF-012 (self-contained) | Overview + Quality Requirements | COVERED |

### Component Schema Alignment Verification

Each of the 8 component types from COMPONENT_SCHEMA-001.md has a defined representation in the output:

| Component Type | Output Representation | Resolution Rule |
|---|---|---|
| step_definition | workflow.toml [[step]] sections | RR-001 |
| role_policy | workflow.toml [step.coder] sections | RR-002 |
| routing_pattern | workflow.toml onsuccess + [step.on_reject_refine] | RR-003 |
| prompt_pattern | prompts/NN_{step_name}.txt files | RR-004 |
| artifact_contract | context_extensions.py ARTIFACT_KEY_REGISTRY | RR-005 |
| composition_standard | Standards/COMPOSITION_STANDARD.md | RR-006 |
| output_variance | Standards/COMPOSITION_STANDARD.md or README.md | RR-006 (within standard) |
| domain_spec | Specs/ directory structure + README.md | Part 2 output structure |

**Verification:** All 8 component types have defined output representations. No type is omitted.

### Composition Format Alignment Verification

| Composition Format Feature | Output Format Handling | Consistent? |
|---|---|---|
| Override mechanism (merge semantics) | RR-001 through RR-006: overrides applied during resolution, override wins on conflict | YES |
| Placeholder resolution (3 data sources) | RR-007: same 3 data sources, same resolution order, {UNRESOLVED: field_name} marker | YES |
| Reference pattern (by component_id) | RR-001 through RR-006: all components looked up by component_id, then expanded | YES |
| Ordering rules (step_bindings ordered) | Output preserves step order from composition in workflow.toml [[step]] sequence | YES |
| Singleton bindings (role, routing per step) | Each [[step]] has exactly one [step.coder] and one onsuccess routing | YES |

### Three-Layer Trace Verification

Tracing a component from schema to composition to output without information loss:

1. **Layer 1 (COMPONENT_SCHEMA-001.md):** step_definition "step-generate-component-schema-001" defines step_name, step_type, purpose, required_inputs, produces, enable_notifications, requires_human_approval_after
2. **Layer 2 (COMPOSITION_FORMAT-001.md):** Composition references this component by component_id with overrides on purpose. Role, routing, and prompt_patterns are bound inline.
3. **Layer 3 (this document):** RR-001 expands the component into workflow.toml [[step]] section with all 7 properties present (base + overrides merged). RR-002 adds [step.coder]. RR-003 adds onsuccess. RR-004 generates the prompt file.

**No information is lost.** All properties from Layer 1 are preserved. Overrides from Layer 2 are applied. The output in Layer 3 contains the complete resolved component content.

---

**End of Output Format**
