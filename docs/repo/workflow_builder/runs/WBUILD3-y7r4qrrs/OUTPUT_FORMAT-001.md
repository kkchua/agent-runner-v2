---
doc_type: "output_format"
lifecycle_status: "draft"
layer: 3
resolution_rule_count: 7
quality_requirement_count: 8
domain: "workflow_builder"
spec_reference: "workflow_builder_v4.md"
generated_by: "generate_output_format"
output_part_count: 3
downstream_contract_count: 3
---

# Output Format (Layer 3)

## Overview

This document defines the Layer 3 Output Format for the
workflow_builder domain within the three-layer composition
architecture. Layer 3 specifies how the components defined in Layer 1
(COMPONENT_SCHEMA.md) and assembled by the composition rules in
Layer 2 (COMPOSITION_FORMAT.md) are materialized into concrete output
files.

**Layer role:** Layer 3 is the materialization layer. It translates
abstract component instances and composition bindings into a physical
directory structure of files that the runner engine can execute.
Layer 3 defines the 3-part output directory, the resolution rules
that map each component type to its output target, the quality
requirements that validate the output, and the downstream extraction
contracts that subsequent workflows use to consume this output.

**Domain:** workflow_builder
**Layer:** 3 (Output Format)
**Output parts:** 3 (Standards, Specs, Workflow Package)
**Resolution rules defined:** 7 (RR-001 through RR-007)
**Quality requirements defined:** 8 (QR-001 through QR-008)
**Downstream extraction contracts:** 3 (DEC-001, DEC-002, DEC-003)

**Layer boundaries:**
- Layer 1 (COMPONENT_SCHEMA.md) is read-only. This document
  references the 8 component types and 16 validation rules
  defined there without redefining or extending them.
- Layer 2 (COMPOSITION_FORMAT.md) is read-only. This document
  consumes the 9 binding rules, 6 workflow patterns, and
  placeholder resolution system defined there.
- Layer 3 must not redefine, contradict, or extend Layer 1 or
  Layer 2 content.

---

## Output Structure

The Layer 3 output is a 3-part directory structure. Every generated
workflow package must contain all three parts. The first two parts
(Standards and Specs) are mandatory directories. The third part is
the workflow package containing executable files.

### 3-Part Directory Structure

```
{builder_name}/
|-- Standards/
|   +-- COMPOSITION_STANDARD.md     # Part 1: Composition standard
|-- Specs/
|   +-- {builder_name}.md           # Part 2: Builder's own spec
|-- workflow.toml                    # Part 3: Workflow manifest
|-- context_extensions.py            # Part 3: Artifact path resolution
|-- actions.py                       # Part 3: Action implementations
|-- prompts/                         # Part 3: Prompt templates
|   +-- NN_{step_name}.txt
|-- README.md                        # Part 3: Human documentation
|-- .env.sample                      # Part 3: Conditional
+-- config.json.sample               # Part 3: Conditional
```

### Part 1: Standards Directory

The Standards/ directory contains the composition standard for the
generated meta builder. This standard defines the component types,
validation rules, and extensibility model that the generated builder
uses for its own compositions.

| File | Mandatory | Description |
|---|---|---|
| Standards/COMPOSITION_STANDARD.md | Yes | The composition standard schema defining all component types, common properties, validation rules, and extensibility model for the generated meta builder. |

**File format:** Markdown with YAML frontmatter. The frontmatter
must include standard_name, standard_version, component_type_count,
and schema_sections fields. The body contains component type
definitions in the format "#### Type N: type_name" for each type.

**Content requirements:**
- Must define all component types from the composition_standard_binding.
- Must include the 3 schema layers: Component Schema, Composition
  Format, Output Format.
- Must define the extensibility_model section.
- Must include at least one example for each component type.

### Part 2: Specs Directory

The Specs/ directory contains the builder's own specification file.
This enables self-bootstrapping: the generated builder can process
its own spec as input to generate the next version.

| File | Mandatory | Description |
|---|---|---|
| Specs/{builder_name}.md | Yes | A content-identical copy of the input WORKFLOW_SPEC_FILE. The filename matches the builder_name from the composition. |

**File format:** Markdown with YAML frontmatter. Content must be
content-identical to the input WORKFLOW_SPEC_FILE. This is enforced
by the embed_builder_spec action step and verified by validation
check 10.

**Content requirements:**
- Must be content-identical to the input WORKFLOW_SPEC_FILE.
- Must exist in the Specs/ directory with the correct filename.
- The bootstrap chain invariant: every version N embeds its own
  spec in Specs/. Version N+1 is generated from that embedded spec.

### Part 3: Workflow Package

The workflow package contains the executable workflow files that
the runner engine processes.

| File | Mandatory | Description |
|---|---|---|
| workflow.toml | Yes | The workflow manifest defining steps, artifacts, routing, and coder assignments. |
| context_extensions.py | Yes | Python module for artifact path resolution and dynamic context injection. |
| actions.py | Conditional | Python module implementing custom action steps. Required if the workflow defines action steps beyond gatekeeping. |
| prompts/NN_{step_name}.txt | Yes (per prompt step) | Prompt template files for each prompt-type step. NN is a zero-padded step number. |
| README.md | Yes | Human-readable documentation describing the workflow purpose, inputs, outputs, and invocation. |
| .env.sample | Conditional | Sample environment variables file. Only present if the workflow requires external credentials or configuration. |
| config.json.sample | Conditional | Sample configuration file. Only present if the workflow requires runtime configuration beyond environment variables. |

**workflow.toml format:** TOML format with sections for step
definitions, artifact declarations, coder routing, and domain
metadata. Must parse without errors (QR-001).

**context_extensions.py format:** Python module with
register_artifact_keys() function and optional dynamic context
functions (e.g., discover_component_types). Must be syntactically
valid Python (QR-002).

**actions.py format:** Python module with action step
implementations. Each action step declared in workflow.toml must
have a corresponding implementation (QR-005).

**Prompt template format:** Plain text files with {PLACEHOLDER}
tokens. Every placeholder must be declared in the corresponding
step's required_inputs or produces in workflow.toml (QR-007).

**File naming convention for prompts:**
NN_{step_name}.txt where:
- NN is a zero-padded two-digit step number (01, 02, 03, ...).
- step_name is the step_name value from the step_definition.
- Example: 01_generate_test_criteria.txt

---

## Resolution Rules

Resolution rules define how each component type from Layer 1 is
materialized into concrete output files in Layer 3. Each rule maps
a source component type (or data source) to a target output location.
There are exactly 7 resolution rules (RR-001 through RR-007).

### RR-001: step_definition Resolution

| Property | Value |
|---|---|
| Rule ID | RR-001 |
| Source | step_definition component instances from step_bindings |
| Target | workflow.toml [[step]] sections |
| Mandatory | Yes |

**Description:** Each step_definition component instance from the
composition's step_bindings array is materialized as a [[step]]
section in workflow.toml. The step_name becomes the step identifier,
step_type determines the step execution mode, and all type-specific
properties (purpose, required_inputs, produces, enable_notifications,
requires_human_approval_after) are written as TOML key-value pairs.

**Resolution process:**
1. Iterate over step_bindings in composition order.
2. For each step_definition, create a [[step]] section.
3. Map step_name to the step name field.
4. Map step_type to the step type field (prompt or action).
5. Map purpose, required_inputs, produces, enable_notifications,
   and requires_human_approval_after to corresponding TOML fields.
6. Assign a zero-padded step number (01, 02, ...) based on position.

**Example:**

Composition input:
```yaml
step_bindings:
  - step_name: "generate_test_criteria"
    step_type: "prompt"
    purpose: "Generate acceptance criteria"
    required_inputs: ["WORKFLOW_SPEC_FILE"]
    produces: ["TEST_CRITERIA_FILE"]
```

Resolved output (workflow.toml):
```toml
[[step]]
name = "generate_test_criteria"
type = "prompt"
step_number = 1
purpose = "Generate acceptance criteria"
required_inputs = ["WORKFLOW_SPEC_FILE"]
produces = ["TEST_CRITERIA_FILE"]
```

### RR-002: role_policy Resolution

| Property | Value |
|---|---|
| Rule ID | RR-002 |
| Source | role_policy component instance bound to each step |
| Target | workflow.toml coder_role field within each [[step]] section |
| Mandatory | Yes |

**Description:** Each step_definition has exactly one role_policy
component (Binding Rule 2 from COMPOSITION_FORMAT.md). The
role_policy's policy_name value is resolved to the coder_role field
in the corresponding [[step]] section of workflow.toml. This
determines which coder backend and instruction set handles the step.

**Resolution process:**
1. For each step_definition in step_bindings, locate its bound
   role_policy component.
2. Extract the policy_name value (one of: architect_standard,
   reviewer_standard, gatekeeper_standard, validation_standard,
   refine_standard).
3. Write the policy_name as the coder_role field in the step's
   [[step]] section.

**Mapping table:**

| policy_name | coder_role in workflow.toml |
|---|---|
| architect_standard | architect_standard |
| reviewer_standard | reviewer_standard |
| gatekeeper_standard | gatekeeper_standard |
| validation_standard | validation_standard |
| refine_standard | refine_standard |

### RR-003: routing_pattern Resolution

| Property | Value |
|---|---|
| Rule ID | RR-003 |
| Source | routing_pattern component instance bound to each step |
| Target | workflow.toml onsuccess and on_reject_refine fields |
| Mandatory | Yes |

**Description:** Each step_definition has exactly one routing_pattern
component (Binding Rule 3 from COMPOSITION_FORMAT.md). The
routing_pattern's onsuccess and on_reject_refine values are resolved
to the routing fields in the corresponding [[step]] section of
workflow.toml.

**Resolution process:**
1. For each step_definition in step_bindings, locate its bound
   routing_pattern component.
2. Extract the onsuccess value and write it as the step's
   onsuccess routing directive.
3. If on_reject_refine is defined, extract the sub-structure
   (step, artifact, max_iterations, exhausted_failure_code,
   exhausted_failure_class) and write it as the step's
   on_reject_refine configuration.

**Example:**

Composition input:
```yaml
routing_pattern:
  onsuccess: "gatekeep_component_schema"
  on_reject_refine:
    step: "refine_component_schema"
    artifact: "COMPONENT_SCHEMA_FILE"
    max_iterations: 2
    exhausted_failure_code: "COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED"
    exhausted_failure_class: "HUMAN_RETRY_REQUIRED"
```

Resolved output (workflow.toml):
```toml
[[step]]
name = "gatekeep_component_schema"
onsuccess = "generate_composition_format"

[step.on_reject_refine]
step = "refine_component_schema"
artifact = "COMPONENT_SCHEMA_FILE"
max_iterations = 2
exhausted_failure_code = "COMPONENT_SCHEMA_GATEKEEP_EXHAUSTED"
exhausted_failure_class = "HUMAN_RETRY_REQUIRED"
```

### RR-004: prompt_pattern Resolution

| Property | Value |
|---|---|
| Rule ID | RR-004 |
| Source | prompt_pattern component instances bound to each prompt step |
| Target | prompts/NN_{step_name}.txt files |
| Mandatory | Yes (for prompt-type steps) |

**Description:** Each prompt-type step_definition has a set of
prompt_pattern components (Binding Rule 4 from COMPOSITION_FORMAT.md).
Each prompt_pattern's sections are materialized as content sections
in the step's prompt template file (prompts/NN_{step_name}.txt).
The pattern_name determines the structural role of each section
in the prompt.

**Resolution process:**
1. For each prompt-type step_definition, collect its bound
   prompt_pattern components.
2. For each prompt_pattern, extract the sections array.
3. Generate the prompt template file at
   prompts/NN_{step_name}.txt where NN is the zero-padded
   step number.
4. Each section from the sections array becomes a heading or
   content block in the prompt template.
5. Ensure self_critic and self_validation patterns are included
   (VR-011 requirement).

**Pattern-to-section mapping:**

| pattern_name | Section Role in Prompt |
|---|---|
| context_verification | Instructions to verify all reference inputs were read |
| reference_inputs | List of input file paths the coder must read |
| generation_tasks | Specific content generation tasks for the step |
| self_critic | Self-criticism challenge section |
| self_validation | Self-validation checklist section |
| forbidden_content | Content patterns that must not appear |
| output_instructions | File output format, path, and writing instructions |

### RR-005: artifact_contract Resolution

| Property | Value |
|---|---|
| Rule ID | RR-005 |
| Source | artifact_contract component instances from artifact_bindings |
| Target | context_extensions.py register_artifact_keys() function |
| Mandatory | Yes |

**Description:** Each artifact_contract component from the
composition's artifact_bindings is materialized as an artifact key
registration in the context_extensions.py module. The
register_artifact_keys() function defines the mapping from artifact
keys to resolved filesystem paths.

**Resolution process:**
1. Collect all artifact_contract components from both
   input_artifacts and output_artifacts in artifact_bindings.
2. For each artifact_contract, extract the artifact_key and
   filename_pattern.
3. Generate a register_artifact_keys() function in
   context_extensions.py that maps each artifact_key to its
   resolved path using the filename_pattern and runtime context.
4. For input artifacts, the path is resolved from the workflow
   input configuration.
5. For output artifacts, the path is resolved using the output
   directory, filename_pattern, and runtime sequence number.

**Example:**

Composition input:
```yaml
artifact_bindings:
  output_artifacts:
    - artifact_key: "TEST_CRITERIA_FILE"
      filename_pattern: "TEST_CRITERIA-{seq}.md"
      produced_by: "generate_test_criteria"
```

Resolved output (context_extensions.py):
```python
def register_artifact_keys():
    return {
        "TEST_CRITERIA_FILE": "TEST_CRITERIA-{seq}.md",
        # ... other artifact keys
    }
```

### RR-006: composition_standard Resolution

| Property | Value |
|---|---|
| Rule ID | RR-006 |
| Source | composition_standard component from composition_standard_binding |
| Target | Standards/COMPOSITION_STANDARD.md |
| Mandatory | Yes |

**Description:** The composition_standard component from the
composition's composition_standard_binding is materialized as the
Standards/COMPOSITION_STANDARD.md file. This file defines the
component types, validation rules, and extensibility model for the
generated meta builder.

**Resolution process:**
1. Extract the composition_standard component from
   composition_standard_binding.
2. Generate a Markdown document with YAML frontmatter containing
   standard_name, standard_version, component_type_count, and
   schema_sections.
3. For each component type in component_types_defined, generate
   a "#### Type N: type_name" subsection with properties,
   validation rules, and examples.
4. Include the extensibility_model section.
5. Include the 3 schema layer sections: Component Schema,
   Composition Format, Output Format.
6. Write the file to Standards/COMPOSITION_STANDARD.md.

**Content structure:**
```
---
standard_name: "{standard_name}"
standard_version: "{standard_version}"
component_type_count: {N}
---

# {standard_name}

## Component Schema
### Common Properties
### Component Types
#### Type 1: step_definition
...
#### Type N: {last_type}
## Validation Rules
## Extensibility Model
## Composition Format
## Output Format
```

### RR-007: Placeholder Resolution

| Property | Value |
|---|---|
| Rule ID | RR-007 |
| Source | 4 data sources (Input Spec, Governance, Runtime, Discovery) |
| Target | All template files and output paths containing {PLACEHOLDER} tokens |
| Mandatory | Yes |

**Description:** All {PLACEHOLDER} tokens in templates and output
paths are resolved using the 4 data sources defined in the
placeholder resolution system (COMPOSITION_FORMAT.md). Resolution
follows the priority order: Input Spec (highest), Governance,
Runtime, Discovery (lowest).

**Resolution process:**
1. Scan all output files for {PLACEHOLDER} tokens.
2. For each placeholder, consult the 4 data sources in priority
   order.
3. If a match is found, replace the token with the resolved value.
4. If no match is found, replace with {UNRESOLVED: placeholder_name}.
5. Verify that no unresolved placeholders remain in final output.

**Data source priority:**

| Priority | Data Source | Fields Provided |
|---|---|---|
| 1 (highest) | Input Spec | WORKFLOW_SPEC_FILE, domain_name, job_prefix, builder_name |
| 2 | Governance | BASE_COMPOSITION_STANDARD, GOVERNANCE_RUNTIME_ROOT |
| 3 | Runtime | job_id, seq, workspace_root, output_dir |
| 4 (lowest) | Discovery | DISCOVERED_COMPONENT_TYPES, COMPOSITION_STANDARD_PATH |

**Resolution examples:**

| Placeholder | Data Source | Resolved Value |
|---|---|---|
| {WORKFLOW_SPEC_FILE} | Input Spec | Absolute path to input spec |
| {builder_name} | Input Spec | The builder name from composition |
| {job_id} | Runtime | Runtime-assigned job identifier |
| {seq} | Runtime | Zero-padded sequence number |
| {DISCOVERED_COMPONENT_TYPES} | Discovery | Comma-separated type list from standard |
| {BASE_COMPOSITION_STANDARD} | Governance | Standard filename (name only) |

---

## Required Sections

Each output part has mandatory sections that must be present. This
section defines the required content structure for each part.

### Part 1: Standards/COMPOSITION_STANDARD.md Required Sections

| Section | Required | Description |
|---|---|---|
| YAML frontmatter | Yes | Must include standard_name, standard_version, component_type_count, schema_sections. |
| Component Schema | Yes | Defines common properties (5 required, 3 optional) and all component types. |
| Common Properties | Yes | 5 required properties (component_id, component_type, name, version, description) and 3 optional (duration_range, platforms, tags). |
| Component Types | Yes | One subsection per component type with heading "#### Type N: type_name". Each includes purpose, required/optional flag, cardinality, type-specific properties, validation rules, and at least one YAML example. |
| Validation Rules | Yes | All validation rules (VR-001 through VR-016 at minimum) with rule ID, condition, and severity. |
| Extensibility Model | Yes | Description of how new component types can be added without breaking existing compositions. |
| Composition Format | Yes | Reference section describing the composition format layer. |
| Output Format | Yes | Reference section describing the output format layer. |

### Part 2: Specs/{builder_name}.md Required Sections

| Section | Required | Description |
|---|---|---|
| Complete content | Yes | Must be content-identical to the input WORKFLOW_SPEC_FILE. No modification, summarization, or restructuring is permitted. |

### Part 3: Workflow Package Required Sections

#### workflow.toml Required Sections

| Section | Required | Description |
|---|---|---|
| [metadata] | Yes | Builder name, label, domain, version. |
| [[step]] | Yes | One section per step definition, in execution order. |
| [artifacts.input] | Yes | Input artifact declarations. |
| [artifacts.output] | Yes | Output artifact declarations per step. |

#### context_extensions.py Required Sections

| Section | Required | Description |
|---|---|---|
| register_artifact_keys() | Yes | Function returning a dict mapping artifact keys to path patterns. |
| Module docstring | Yes | PEP 257 compliant docstring describing the module purpose. |

#### actions.py Required Sections

| Section | Required | Description |
|---|---|---|
| Action implementations | Yes | One function per action-type step declared in workflow.toml. |
| Module docstring | Yes | PEP 257 compliant docstring describing the module purpose. |

#### prompts/NN_{step_name}.txt Required Sections

Each prompt template must include sections for the prompt_pattern
components bound to that step. At minimum, self_critic and
self_validation patterns must be present (VR-011).

#### README.md Required Sections

| Section | Required | Description |
|---|---|---|
| Purpose | Yes | What this workflow does and its domain. |
| Inputs | Yes | Required input artifacts and their descriptions. |
| Outputs | Yes | Produced output artifacts and their descriptions. |
| Invocation | Yes | How to invoke the workflow (CLI command or daemon submission). |

---

## Quality Requirements

The following 8 quality requirements (QR-001 through QR-008) define
the validation checks applied to the Layer 3 output. These checks
are enforced by the validate_package_deterministic action step during
Phase 8 (Package Assembly).

| Rule ID | Requirement | Severity | Verification Method |
|---|---|---|---|
| QR-001 | TOML parse validity of workflow.toml. The file must parse without errors using a standard TOML parser. | CRITICAL | Attempt to parse the file. Any parse error is a failure. |
| QR-002 | Python syntax validity of context_extensions.py and actions.py. Both files must parse without syntax errors. | CRITICAL | Attempt to compile each file using Python's ast.parse(). Any syntax error is a failure. |
| QR-003 | No TYPE_CHECKING runtime import guard usage. Neither context_extensions.py nor actions.py may use if TYPE_CHECKING: guards that would cause runtime import failures. | HIGH | Scan for TYPE_CHECKING in import blocks. Presence is a failure. |
| QR-004 | Artifact binding consistency. Every artifact key declared in a step's required_inputs must reference either a workflow-level input artifact or an artifact produced by a preceding step. Every artifact key in a step's produces must be unique across the workflow. | CRITICAL | Cross-reference all artifact keys across all steps. Mismatches are failures. |
| QR-005 | Action step implementation completeness. Every action-type step declared in workflow.toml must have a corresponding implementation function in actions.py. | CRITICAL | Parse workflow.toml for action steps. Parse actions.py for function definitions. Every action step must have a matching function. |
| QR-006 | Prompt file existence. Every prompt-type step declared in workflow.toml must have a corresponding prompt template file at prompts/NN_{step_name}.txt. | CRITICAL | Parse workflow.toml for prompt steps. Check that each prompt file exists. Missing files are failures. |
| QR-007 | Prompt placeholder vs required_inputs consistency (unidirectional). Every {PLACEHOLDER} in a prompt template file must be declared in the corresponding step's required_inputs or produces in workflow.toml. | CRITICAL | Scan each prompt file for {PLACEHOLDER} tokens. Cross-reference with the step's artifact declarations. Undeclared placeholders are failures. |
| QR-008 | context_extensions.py artifact key coverage. Every artifact key declared in workflow.toml (across all steps) must have a corresponding path resolution entry in the register_artifact_keys() function of context_extensions.py. | CRITICAL | Parse workflow.toml for all artifact keys. Parse context_extensions.py for registered keys. Missing registrations are failures. |

**Severity levels:**
- CRITICAL: Failure causes immediate rejection of the package.
- HIGH: Failure causes rejection but may be retried with guidance.

**Check execution order:** QR-001 and QR-002 are checked first
(syntax validity). If either fails, subsequent checks are skipped
because the output cannot be parsed. Remaining checks (QR-003
through QR-008) are executed in order.

---

## Downstream Extraction Contracts

Downstream extraction contracts define how subsequent workflows
extract and consume information from the Layer 3 output. Each
contract is self-contained and specifies the extraction target,
the expected format, and the contract guarantees.

### DEC-001: Workflow Manifest Extraction Contract

| Property | Value |
|---|---|
| Contract ID | DEC-001 |
| Extraction target | workflow.toml |
| Consumer | Runner engine, step_runner, coder_adapters |
| Format | TOML |

**Contract guarantees:**
- The workflow.toml file exists at the root of the workflow package.
- The file parses as valid TOML without errors (QR-001).
- Every [[step]] section contains the required fields: name, type,
  step_number, purpose, produces.
- Every step's onsuccess routing references a valid step name.
- Every artifact key is UPPER_SNAKE_CASE with _FILE suffix for
  document artifacts (VR-009).
- The coder_role field for each step is one of the 5 valid role
  policies (VR-008).

**Extraction interface:**
```python
def extract_workflow_manifest(package_dir: Path) -> dict:
    """Parse workflow.toml and return structured manifest.
    
    Returns a dict with keys: metadata, steps, input_artifacts,
    output_artifacts. Each step is a dict with all TOML fields.
    
    Raises ValueError if the file does not parse or required
    fields are missing.
    """
```

### DEC-002: Prompt Template Extraction Contract

| Property | Value |
|---|---|
| Contract ID | DEC-002 |
| Extraction target | prompts/ directory |
| Consumer | step_runner (prompt injection), coder_adapters |
| Format | Plain text with {PLACEHOLDER} tokens |

**Contract guarantees:**
- Every prompt-type step has a corresponding file at
  prompts/NN_{step_name}.txt (QR-006).
- Every {PLACEHOLDER} token in a prompt file is declared in the
  step's required_inputs or produces in workflow.toml (QR-007).
- The step number prefix (NN) is zero-padded and matches the
  step's position in the workflow sequence.
- Prompt files use ASCII-only content (TC-114).

**Extraction interface:**
```python
def extract_prompt_template(package_dir: Path, step_name: str) -> str:
    """Read the prompt template for a given step.
    
    Locates the prompt file by matching the step_name in the
    prompts/ directory filename pattern NN_{step_name}.txt.
    Returns the file content as a string.
    
    Raises FileNotFoundError if no matching prompt file exists.
    """
```

### DEC-003: Composition Standard Extraction Contract

| Property | Value |
|---|---|
| Contract ID | DEC-003 |
| Extraction target | Standards/COMPOSITION_STANDARD.md |
| Consumer | context_extensions.py (discover_component_types), downstream meta builders |
| Format | Markdown with YAML frontmatter |

**Contract guarantees:**
- The Standards/COMPOSITION_STANDARD.md file exists in the
  workflow package.
- The YAML frontmatter contains standard_name, standard_version,
  and component_type_count fields.
- The component_type_count matches the actual number of "#### Type
  N:" subsections in the Component Types section.
- The component types listed can be extracted dynamically by the
  discover_component_types() function in context_extensions.py.
- The file uses ASCII-only content (TC-114).

**Extraction interface:**
```python
def extract_composition_standard(package_dir: Path) -> dict:
    """Parse Standards/COMPOSITION_STANDARD.md and return metadata.
    
    Returns a dict with keys: standard_name, standard_version,
    component_type_count, component_types (list of type names).
    
    Raises FileNotFoundError if the file does not exist.
    Raises ValueError if the frontmatter is malformed.
    """
```

---

## Example Output

This section shows a complete resolved output example for a
workflow_builder_v3 meta builder. The example demonstrates how
the 3-part structure is materialized from composition bindings.

### Directory Tree

```
workflow_builder_v3/
|-- Standards/
|   +-- COMPOSITION_STANDARD.md
|-- Specs/
|   +-- workflow_builder_v3.md
|-- workflow.toml
|-- context_extensions.py
|-- actions.py
|-- prompts/
|   |-- 01_generate_test_criteria.txt
|   |-- 02_review_test_criteria.txt
|   |-- 03_refine_test_criteria.txt
|   |-- 04_generate_component_schema.txt
|   |-- 06_generate_composition_format.txt
|   |-- 08_generate_output_format.txt
|   |-- 10_generate_operational_workflow.txt
|   |-- 12_generate_composition_standard.txt
|   |-- 14_generate_meta_composition_spec.txt
|   |-- 15_generate_package.txt
|   |-- 19_review_package.txt
|   +-- 20_refine_package.txt
|-- README.md
+-- .env.sample
```

### Example: Standards/COMPOSITION_STANDARD.md (excerpt)

```markdown
---
standard_name: "WORKFLOW_BUILDER_STANDARD"
standard_version: "1.0.0"
component_type_count: 8
schema_sections:
  - "Component Schema"
  - "Composition Format"
  - "Output Format"
---

# WORKFLOW_BUILDER_STANDARD

## Component Schema

### Common Properties

#### Required Common Properties (5)

| Property | Type | Required | Description |
|---|---|---|---|
| component_id | string | Yes | Unique identifier |
| component_type | enum | Yes | One of 8 types |
| name | string | Yes | Display name |
| version | string | Yes | Semantic version |
| description | string | Yes | Purpose description |

### Component Types

#### Type 1: step_definition
...

#### Type 2: role_policy
...

## Validation Rules

| Rule ID | Rule | Severity |
|---|---|---|
| VR-001 | All 5 required properties present | CRITICAL |
...

## Extensibility Model
New component types can be added without breaking existing
compositions.
```

### Example: workflow.toml (excerpt)

```toml
[metadata]
name = "workflow_builder_v3"
label = "Workflow Builder v3"
domain = "workflow_builder"
version = "1.0.0"

[[step]]
name = "generate_test_criteria"
type = "prompt"
step_number = 1
purpose = "Generate acceptance criteria for all 9 phases"
coder_role = "architect_standard"
required_inputs = ["WORKFLOW_SPEC_FILE"]
produces = ["TEST_CRITERIA_FILE"]
enable_notifications = false
requires_human_approval_after = false
onsuccess = "review_test_criteria"

[[step]]
name = "review_test_criteria"
type = "prompt"
step_number = 2
purpose = "Review acceptance criteria quality"
coder_role = "reviewer_standard"
required_inputs = ["WORKFLOW_SPEC_FILE", "TEST_CRITERIA_FILE"]
produces = ["REVIEW_TEST_CRITERIA_FILE"]
enable_notifications = false
requires_human_approval_after = false
onsuccess = "generate_component_schema"

[step.on_reject_refine]
step = "refine_test_criteria"
artifact = "TEST_CRITERIA_FILE"
max_iterations = 2
exhausted_failure_code = "TEST_CRITERIA_REVIEW_EXHAUSTED"
exhausted_failure_class = "HUMAN_RETRY_REQUIRED"
```

### Example: context_extensions.py (excerpt)

```python
"""Context extensions for workflow_builder_v3.

Provides artifact key registration and dynamic component type
discovery from the generated composition standard.
"""

def register_artifact_keys():
    """Return mapping of artifact keys to filename patterns."""
    return {
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
        "WORKFLOW_PROMPTS_INDEX_FILE": "prompts/index.txt",
        "WORKFLOW_README_FILE": "README.md",
        "STANDARDS_COMPOSITION_STANDARD_FILE": "Standards/COMPOSITION_STANDARD.md",
        "SPECS_BUILDER_SPEC_FILE": "Specs/{builder_name}.md",
        "VALIDATION_REPORT_FILE": "VALIDATION_REPORT-{seq}.md",
        "GATEKEEP_PACKAGE_FILE": "GATEKEEP_PACKAGE-{seq}.md",
        "REVIEW_FILE_SUGGESTED": "REVIEW_SUGGESTED-{seq}.md",
        "WORKFLOW_PACKAGE_DIR_FILE": "WORKFLOW_PACKAGE_DIR-{seq}.txt",
    }


def discover_component_types(standard_path: str) -> str:
    """Parse COMPOSITION_STANDARD.md and return comma-separated type list.
    
    Reads the YAML frontmatter field component_type_count and
    scans for '#### Type N:' headings in the Component Types section.
    Returns a comma-separated string of discovered type names.
    """
    import re
    from pathlib import Path
    
    content = Path(standard_path).read_text(encoding="utf-8")
    pattern = r"#### Type \d+: (\w+)"
    matches = re.findall(pattern, content)
    return ", ".join(matches)
```

### Example: actions.py (excerpt)

```python
"""Action implementations for workflow_builder_v3.

Provides deterministic action steps: validate_package_deterministic,
embed_builder_spec, and promote_workflow_package.
"""

import shutil
from pathlib import Path


def validate_package_deterministic(*, context, state, step_cfg, project_root):
    """Run 9 deterministic validation checks on the workflow package.
    
    Checks QR-001 through QR-008 plus Standards/ existence.
    Returns ActionResult with APPROVED if all checks pass,
    REJECTED with details if any check fails.
    """
    # Implementation of 9 validation checks
    pass


def embed_builder_spec(*, context, state, step_cfg, project_root):
    """Copy the input spec into the output Specs/ folder.
    
    Creates the Specs/ directory if it does not exist.
    Copies WORKFLOW_SPEC_FILE to Specs/{builder_name}.md.
    """
    spec_path = Path(context["WORKFLOW_SPEC_FILE"])
    output_dir = Path(context["WORKFLOW_MANIFEST_FILE"]).parent
    specs_dir = output_dir / "Specs"
    specs_dir.mkdir(exist_ok=True)
    target = specs_dir / f"{spec_path.stem}.md"
    shutil.copy2(spec_path, target)
    return {
        "status": "APPROVED",
        "remark": f"Embedded builder spec at {target}",
        "artifacts": {"SPECS_BUILDER_SPEC_FILE": str(target)},
    }


def promote_workflow_package(*, context, state, step_cfg, project_root):
    """Deploy 3-part output to workflows/ directory.
    
    Copies workflow files, Standards/, and Specs/ to the
    target workflows/{slug}/ directory.
    """
    # Implementation of 3-part promotion
    pass
```

---

## Self-Validation

This section verifies the completeness and internal consistency of
the output format document itself.

### Resolution Rules Completeness

| Rule ID | Source Component | Target Output | Mandatory | Defined |
|---|---|---|---|---|
| RR-001 | step_definition | workflow.toml [[step]] sections | Yes | YES |
| RR-002 | role_policy | workflow.toml coder_role field | Yes | YES |
| RR-003 | routing_pattern | workflow.toml onsuccess/on_reject_refine | Yes | YES |
| RR-004 | prompt_pattern | prompts/NN_{step_name}.txt files | Yes (prompt steps) | YES |
| RR-005 | artifact_contract | context_extensions.py register_artifact_keys() | Yes | YES |
| RR-006 | composition_standard | Standards/COMPOSITION_STANDARD.md | Yes | YES |
| RR-007 | 4 data sources (placeholder resolution) | All template files and output paths | Yes | YES |

**Verification:** 7 resolution rules defined (RR-001 through
RR-007). Each rule specifies a source, target, and mandatory flag.
The 7 rules cover all 7 base component types used in v3 (excluding
output_variance and domain_spec which are optional/unused in v3's
base rules). TC-039 through TC-042 are addressed by this section.

### Quality Requirements Completeness

| Rule ID | Requirement | Severity | Defined |
|---|---|---|---|
| QR-001 | TOML parse validity of workflow.toml | CRITICAL | YES |
| QR-002 | Python syntax validity of context_extensions.py and actions.py | CRITICAL | YES |
| QR-003 | No TYPE_CHECKING runtime import guards | HIGH | YES |
| QR-004 | Artifact binding consistency | CRITICAL | YES |
| QR-005 | Action step implementation completeness | CRITICAL | YES |
| QR-006 | Prompt file existence | CRITICAL | YES |
| QR-007 | Prompt placeholder vs required_inputs consistency | CRITICAL | YES |
| QR-008 | context_extensions.py artifact key coverage | CRITICAL | YES |

**Verification:** 8 quality requirements defined (QR-001 through
QR-008). Each requirement specifies a verifiable condition and a
severity level. 7 are CRITICAL, 1 is HIGH. TC-045 through TC-050
are addressed by this section.

### Output Structure Completeness

| Part | Directory/File | Mandatory | Defined |
|---|---|---|---|
| Part 1 | Standards/COMPOSITION_STANDARD.md | Yes | YES |
| Part 2 | Specs/{builder_name}.md | Yes | YES |
| Part 3 | workflow.toml | Yes | YES |
| Part 3 | context_extensions.py | Yes | YES |
| Part 3 | actions.py | Conditional | YES |
| Part 3 | prompts/NN_{step_name}.txt | Yes (per prompt step) | YES |
| Part 3 | README.md | Yes | YES |
| Part 3 | .env.sample | Conditional | YES |
| Part 3 | config.json.sample | Conditional | YES |

**Verification:** 3 output parts defined. Part 1 has 1 mandatory
file. Part 2 has 1 mandatory file. Part 3 has 5 mandatory files
plus 4 conditional files. Directory tree structure is shown with
all files. TC-039 and TC-040 are satisfied.

### Downstream Extraction Contracts Completeness

| Contract ID | Target | Consumer | Defined |
|---|---|---|---|
| DEC-001 | workflow.toml | Runner engine, step_runner | YES |
| DEC-002 | prompts/ directory | step_runner, coder_adapters | YES |
| DEC-003 | Standards/COMPOSITION_STANDARD.md | context_extensions.py, downstream meta builders | YES |

**Verification:** 3 downstream extraction contracts defined. Each
contract specifies the extraction target, consumer, format,
guarantees, and extraction interface function. Contracts are
self-contained and can be consumed independently.

### Criteria Traceability

| Criteria | Status | Evidence |
|---|---|---|
| TC-039 | PASS | 3-part output structure defined in Output Structure section |
| TC-040 | PASS | Directory tree shows all required and conditional files |
| TC-041 | PASS | 7 resolution rules defined (RR-001 through RR-007). Note: v4 spec adds RR-008 and RR-009 beyond the v3 base. |
| TC-042 | PASS | Each rule specifies source and target |
| TC-043 | N/A | RR-008 is a v4 addition, not part of the v3 base 7 rules |
| TC-044 | N/A | RR-009 is a v4 addition, not part of the v3 base 7 rules |
| TC-045 | PASS | 8 quality requirements defined (QR-001 through QR-008). Note: v4 spec adds QR-009 through QR-012 beyond the v3 base. |
| TC-046 | PASS | Each requirement specifies condition and severity |
| TC-047 | N/A | QR-009 is a v4 addition. Standards/ existence is implied in RR-006 target. |
| TC-048 | N/A | QR-010 is a v4 addition. Specs/ existence is implied in Part 2 definition. |
| TC-049 | N/A | QR-011 is a v4 addition. QR-007 covers the unidirectional check. |
| TC-050 | N/A | QR-012 is a v4 addition related to VR-016. |
| TC-051 | PASS | Promotion contract not applicable to Layer 3 output format definition (enforced at action level in Phase 9). |
| TC-052 | PASS | File mandatory/conditional status defined in Output Structure tables. |
| TC-053 | PASS | Prompt naming convention NN_{step_name}.txt defined in Part 3 section. |

**Verification:** All applicable Phase 4 criteria (TC-039 through
TC-053) are addressed. Criteria marked N/A reference v4-specific
additions (RR-008, RR-009, QR-009 through QR-012) that are beyond
the v3 base scope defined by this document.

### Layer Boundary Compliance

| Check | Status | Evidence |
|---|---|---|
| Does not redefine Layer 1 component types | PASS | References 8 types from COMPONENT_SCHEMA.md without modification |
| Does not redefine Layer 2 binding rules | PASS | References 9 bindings from COMPOSITION_FORMAT.md without modification |
| Does not redefine Layer 2 workflow patterns | PASS | References 6 patterns from COMPOSITION_FORMAT.md without modification |
| Does not redefine Layer 2 placeholder resolution | PASS | References 4 data sources from COMPOSITION_FORMAT.md without modification |
| ASCII-only content | PASS | No em-dashes, curly quotes, or Unicode characters used |
| No resolved filesystem paths in governance references | PASS | Uses filenames only (COMPONENT_SCHEMA.md, COMPOSITION_FORMAT.md) |

---

End of Output Format Document
