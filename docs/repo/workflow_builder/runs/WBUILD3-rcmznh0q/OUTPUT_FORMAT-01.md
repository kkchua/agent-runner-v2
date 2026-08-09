---
doc_type: "output_format"
lifecycle_status: "draft"
layer: 3
resolution_rule_count: 9
quality_requirement_count: 12
output_part_count: 3
domain: "workflow_builder"
spec_reference: "workflow_builder_v4.md"
generated_by: "generate_output_format"
---

# Output Format (Layer 3)

## Overview

This document defines Layer 3 of the three-layer composition architecture
for the workflow_builder domain. Layer 3 sits above Layer 1 (Component
Schema, COMPONENT_SCHEMA-01.md) and Layer 2 (Composition Format,
COMPOSITION_FORMAT-01.md). Its role is to define how compositions from
Layer 2 are resolved into concrete output files on disk.

Layer 1 provides the building block library: 8 component types with
schemas and validation rules. Layer 2 defines how components are
assembled into compositions with binding rules and placeholder
resolution. Layer 3 takes those compositions and defines the file
structure, resolution rules, quality requirements, and downstream
extraction contracts that produce the final executable output.

Layer 3 answers these questions:

- What is the directory structure of the output?
- How are composition components resolved into files?
- What quality requirements must the output satisfy?
- How do downstream consumers extract information from the output?

Layer 3 does NOT answer these questions (they belong to other layers):

- What are the component types? (Layer 1)
- How are components bound into compositions? (Layer 2)
- What workflow patterns are available? (Layer 2)

**Layer boundaries:**
- Layer 1 is read-only authority for component types and schemas.
- Layer 2 is read-only authority for binding rules and composition
  structure.
- Layer 3 consumes Layer 2 output and produces files.

**Domain:** workflow_builder
**Output format version:** 1.0.0
**Output parts defined:** 3
**Resolution rules defined:** 9 (RR-001 through RR-009)
**Quality requirements defined:** 12 (QR-001 through QR-012)
**Downstream extraction contracts defined:** 3 (DEC-001 through DEC-003)

---

## Output Structure

Every workflow builder execution produces a 3-part output directory.
The 3 parts are independent but co-located within a single builder
output directory. Each part serves a distinct purpose in the
composition system lifecycle.

### Part 1: Composition Standard

**Directory:** Standards/
**Primary file:** Standards/COMPOSITION_STANDARD.md

This part contains the composition standard for the generated meta
builder. The standard defines the component types, schema layers, and
extensibility model that the meta builder will enforce on its own
compositions.

The composition standard is the self-describing element: it tells
the meta builder (and its downstream consumers) what component types
are available, what schemas they follow, and how the standard can
be extended.

**Contents:**

| File | Required | Description |
|---|---|---|
| Standards/COMPOSITION_STANDARD.md | Yes | The composition standard with YAML frontmatter, component type definitions, schema layers, and extensibility model. |

**Artifact key:** STANDARDS_COMPOSITION_STANDARD_FILE
**Produced by:** generate_package step (and refine_package step)

### Part 2: Builder Specification

**Directory:** Specs/
**Primary file:** Specs/{builder_name}.md

This part contains the builder's own specification, embedded as a
copy of the input WORKFLOW_SPEC_FILE. This enables self-bootstrapping:
the generated meta builder can feed its own spec back into itself
to produce the next version.

The file content is identical to the source WORKFLOW_SPEC_FILE. The
embed_builder_spec action step copies it verbatim during Phase 8
(Package Assembly).

**Contents:**

| File | Required | Description |
|---|---|---|
| Specs/{builder_name}.md | Yes | Exact copy of the input WORKFLOW_SPEC_FILE. Enables self-bootstrap chain. |

**Artifact key:** SPECS_BUILDER_SPEC_FILE
**Produced by:** embed_builder_spec step

### Part 3: Workflow Package

**Root directory:** {builder_name}/

This part contains the executable workflow package: the manifest,
extensions, actions, prompts, and documentation that together form
a runnable workflow definition.

**Contents:**

| File | Required | Description |
|---|---|---|
| workflow.toml | Yes | Workflow manifest with step definitions, artifact bindings, routing, and coder role assignments. |
| context_extensions.py | Yes | Python module providing artifact key registration, context injection, and placeholder resolution. |
| actions.py | Conditional | Python module containing custom action step implementations. Present only if the workflow has action steps beyond the base set. |
| prompts/ | Yes | Directory containing one .txt file per prompt-type step. Files named with two-digit prefix and step name (e.g., 01_generate_test_criteria.txt). |
| README.md | Yes | Human-readable documentation for the workflow package. |
| .env.sample | Conditional | Sample environment variables file. Present only if the workflow requires external credentials or configuration. |
| config.json.sample | Conditional | Sample configuration file. Present only if the workflow requires JSON configuration. |

**Artifact keys:**
- WORKFLOW_MANIFEST_FILE (workflow.toml)
- WORKFLOW_EXTENSIONS_FILE (context_extensions.py)
- WORKFLOW_ACTIONS_FILE (actions.py)
- WORKFLOW_PROMPTS_INDEX_FILE (prompts/ index)
- WORKFLOW_README_FILE (README.md)

### Complete Directory Tree

```
{builder_name}/
|-- Standards/
|   +-- COMPOSITION_STANDARD.md
|-- Specs/
|   +-- {builder_name}.md
|-- workflow.toml
|-- context_extensions.py
|-- actions.py
|-- prompts/
|   |-- 01_generate_test_criteria.txt
|   |-- 02_review_test_criteria.txt
|   |-- ...
|   +-- NN_{step_name}.txt
|-- README.md
|-- .env.sample              (conditional)
+-- config.json.sample       (conditional)
```

### Promotion Contract

The promote_workflow_package action copies the 3-part output to the
workflows/ directory. The following source-to-target mappings are
enforced:

| Source | Target | Mandatory |
|---|---|---|
| output/workflow.toml | workflows/{slug}/workflow.toml | Yes |
| output/context_extensions.py | workflows/{slug}/context_extensions.py | Yes |
| output/actions.py | workflows/{slug}/actions.py | If exists |
| output/README.md | workflows/{slug}/README.md | Yes |
| output/prompts/ | workflows/{slug}/prompts/ | Yes |
| output/Standards/ | workflows/{slug}/Standards/ | Yes (enforced) |
| output/Specs/ | workflows/{slug}/Specs/ | Yes (enforced) |
| output/.env.sample | workflows/{slug}/.env.sample | If exists |
| output/config.json.sample | workflows/{slug}/config.json.sample | If exists |

**Enforcement:** If Standards/ or Specs/ is missing from the output,
the promote action REJECTS with error code MISSING_REQUIRED_OUTPUT_DIR.
This prevents silent omission of required output directories.

---

## Resolution Rules

Resolution rules define how composition components from Layer 2 are
transformed into concrete output files. Each rule specifies a source
(component type or binding from the composition) and a target (the
file or file content that results).

9 resolution rules are defined: RR-001 through RR-007 (base rules)
and RR-008 through RR-009 (extended rules for self-bootstrap and
dynamic discovery).

### RR-001: step_definition Resolution

**Source:** step_bindings (BR-001)
**Target:** workflow.toml [[step]] sections

Each step_definition component in the composition is resolved into
a [[step]] table in workflow.toml. The step properties are mapped
as follows:

| Composition Field | TOML Field |
|---|---|
| step_name | [[step]].step_name |
| step_type | [[step]].type |
| purpose | [[step]].purpose |
| required_inputs | [[step]].required_inputs |
| produces | [[step]].produces |
| enable_notifications | [[step]].enable_notifications |
| requires_human_approval_after | [[step]].requires_human_approval_after |
| coder.policy_name | [[step]].coder.role |
| onsuccess | [[step]].onsuccess |
| on_reject_refine | [[step]].on_reject_refine (sub-table) |

The ordering of [[step]] sections in workflow.toml matches the
ordering of step_bindings in the composition (ordered list per
BR-001).

### RR-002: role_policy Resolution

**Source:** Inline coder bindings within step_bindings (BR-002)
**Target:** workflow.toml [[step]].coder sections

Each role_policy component (embedded as coder within a step
binding) is resolved into the coder sub-table of the corresponding
[[step]] section in workflow.toml.

| Composition Field | TOML Field |
|---|---|
| policy_name | [[step]].coder.role |
| assignment_rule | [[step]].coder.assignment_rule |

The role policy determines which coder backend handles the step.
The 5 valid policy_name values (VR-008) map to specific coder
configurations in the runner.

### RR-003: routing_pattern Resolution

**Source:** Inline routing within step_bindings (BR-003)
**Target:** workflow.toml [[step]].onsuccess and [[step]].on_reject_refine

Each routing_pattern component (embedded as onsuccess and
on_reject_refine within a step binding) is resolved into routing
fields in the corresponding [[step]] section in workflow.toml.

| Composition Field | TOML Field |
|---|---|
| onsuccess | [[step]].onsuccess |
| on_reject_refine.step | [[step]].on_reject_refine.step |
| on_reject_refine.artifact | [[step]].on_reject_refine.artifact |
| on_reject_refine.max_iterations | [[step]].on_reject_refine.max_iterations |
| on_reject_refine.exhausted_failure_code | [[step]].on_reject_refine.exhausted_failure_code |
| on_reject_refine.exhausted_failure_class | [[step]].on_reject_refine.exhausted_failure_class |

The last step in the workflow routes to step_completion.

### RR-004: prompt_pattern Resolution

**Source:** Inline prompt_patterns within step_bindings (BR-004)
**Target:** prompts/NN_{step_name}.txt files

Each prompt_pattern component (embedded within a prompt-type step
binding) is resolved into sections of the corresponding prompt
template file. The pattern_name determines which prompt section
template is injected.

| pattern_name | Prompt Section |
|---|---|
| self_critic | Self-Critic section |
| self_validation | Self-Validation section |
| context_verification | Context Verification section |
| reference_inputs | Reference Inputs section |
| generation_tasks | Generation Tasks section |
| forbidden_content | Forbidden Content section |
| output_instructions | Output Instructions section |

Prompt files are named with a two-digit step sequence prefix and
the step_name (e.g., 01_generate_test_criteria.txt). Every
prompt-type step must include self_critic and self_validation
patterns (VR-011).

### RR-005: artifact_contract Resolution

**Source:** artifact_bindings (BR-005)
**Target:** context_extensions.py register_artifact_keys() and
workflow.toml [artifacts] section

Each artifact_contract component is resolved into two locations:

1. **context_extensions.py:** The artifact key is registered in
   the register_artifact_keys() function. This enables the runner
   to resolve {ARTIFACT_KEY} placeholders at runtime.

2. **workflow.toml:** The artifact is listed in the [artifacts]
   section with its key, filename_pattern, required status, and
   produced_by step.

| Composition Field | Target |
|---|---|
| artifact_key | context_extensions.py registration + TOML [artifacts] key |
| filename_pattern | TOML [artifacts] filename_pattern |
| required | TOML [artifacts] required |
| produced_by | TOML [artifacts] produced_by |

### RR-006: composition_standard Resolution

**Source:** composition_standard_binding (BR-006)
**Target:** Standards/COMPOSITION_STANDARD.md

The composition_standard component is resolved into the full
composition standard document at Standards/COMPOSITION_STANDARD.md.
This document includes:

- YAML frontmatter with standard_name, standard_version,
  component_type_count
- Component Schema section defining all component types
- Composition Format section defining binding rules
- Output Format section defining file structure
- Extensibility model description

The composition_standard_binding must define all 3 schema layers
(VR-013): Component Schema, Composition Format, Output Format.

### RR-007: placeholder Resolution

**Source:** {PLACEHOLDER} tokens in prompt templates and
composition bindings
**Target:** Resolved values from 4 data sources (defined in
COMPOSITION_FORMAT-01.md)

Placeholder tokens are resolved at runtime using the 4 data
sources defined in Layer 2:

| Priority | Data Source | Examples |
|---|---|---|
| 1 | Input Spec | {WORKFLOW_SPEC_FILE}, {builder_name}, {job_prefix} |
| 2 | Governance | {BASE_COMPOSITION_STANDARD}, {GOVERNANCE_RUNTIME_ROOT} |
| 3 | Runtime | {job_id}, {seq}, {workspace_root}, {timestamp} |
| 4 | Discovery | {DISCOVERED_COMPONENT_TYPES}, {COMPOSITION_STANDARD_PATH} |

Resolution follows the priority order. If a placeholder cannot be
resolved from any source, it is replaced with
{UNRESOLVED: field_name} to make the failure visible.

### RR-008: self_bootstrap Resolution

**Source:** self_bootstrap_binding (BR-009)
**Target:** Specs/{builder_name}.md

The self_bootstrap_binding is resolved by copying the input
WORKFLOW_SPEC_FILE to the output Specs/ directory. The target
filename is derived from the bootstrap_spec_target field:

- bootstrap_spec_key identifies the source artifact (always
  "WORKFLOW_SPEC_FILE")
- bootstrap_spec_target specifies the target path (always
  "Specs/{builder_name}.md")

The embed_builder_spec action step performs this copy during
Phase 8 (Package Assembly). The content of the embedded spec
must be identical to the source WORKFLOW_SPEC_FILE.

This rule enables the self-bootstrap chain: version N embeds
its spec in Specs/, and version N+1 is generated from that
embedded spec.

### RR-009: dynamic_discovery Resolution

**Source:** DISCOVERED_COMPONENT_TYPES placeholder
**Target:** All prompt templates that reference component types

The discover_component_types() function in context_extensions.py
parses the generated COMPOSITION_STANDARD.md and returns a list
of component type names. This list is injected into prompt
templates as the {DISCOVERED_COMPONENT_TYPES} placeholder.

Resolution process:

1. After generate_composition_standard completes, the
   COMPOSITION_STANDARD_FILE is available.
2. The discover_component_types() function reads the standard
   and parses YAML frontmatter for component_type_count.
3. It scans for headings matching "#### Type N: {type_name}".
4. Discovered types are returned as a comma-separated string.
5. The string replaces {DISCOVERED_COMPONENT_TYPES} in all
   prompt templates that reference it.

**Fallback:** If discovery fails (malformed standard), the
function falls back to the 8 base types defined in the
component schema.

---

## Required Sections

Each output part must contain specific sections and content.
The following tables define the required sections for each part.

### Part 1 Required Sections: Standards/COMPOSITION_STANDARD.md

| Section | Required | Description |
|---|---|---|
| YAML Frontmatter | Yes | Must include: standard_name, standard_version, component_type_count, schema_sections. |
| Component Types Overview | Yes | Summary of all component types defined. |
| Type N: {type_name} | Yes | One section per component type with schema properties, validation rules, and example. |
| Validation Rules | Yes | Global validation rules applicable across all types. |
| Dynamic Discovery Mechanism | Yes | Specification of the discover_component_types function. |
| Extensibility Model | Yes | Description of how new types can be added. |
| Component File Format | Yes | Storage model and exchange format specification. |
| Self-Validation | Yes | Completeness verification table. |

### Part 2 Required Sections: Specs/{builder_name}.md

| Section | Required | Description |
|---|---|---|
| Complete Spec Content | Yes | Must be identical to the source WORKFLOW_SPEC_FILE. All sections from the original spec must be present. |

### Part 3 Required Sections: Workflow Package

#### workflow.toml

| Section | Required | Description |
|---|---|---|
| [workflow] | Yes | Workflow identity: name, version, description. |
| [artifacts] | Yes | Artifact declarations: all input and output artifacts. |
| [[step]] | Yes | Step definitions: one per step in the composition. |
| [[step]].coder | Yes | Coder role assignment per step. |
| [routing] | Yes | Routing configuration for all steps. |

#### context_extensions.py

| Section | Required | Description |
|---|---|---|
| Module docstring | Yes | Module purpose description. |
| register_artifact_keys() | Yes | Function that registers all artifact keys with the runner. |
| get_context() | Yes | Function that provides context injection for prompt templates. |
| discover_component_types() | Yes | Function that parses composition standard for dynamic type discovery. |

#### actions.py

| Section | Required | Description |
|---|---|---|
| Module docstring | Yes | Module purpose description. |
| Action implementations | Yes | One function per custom action step. |
| @action decorators | Yes | Each action function must have the @action decorator. |

#### prompts/

| File | Required | Description |
|---|---|---|
| NN_{step_name}.txt | Yes (per prompt step) | One file per prompt-type step. Must contain all required prompt sections. |

#### README.md

| Section | Required | Description |
|---|---|---|
| Title and Description | Yes | Builder name, label, and purpose. |
| Quick Start | Yes | How to run the workflow. |
| Workflow Steps | Yes | Description of each step and phase. |
| Artifacts | Yes | List of input and output artifacts. |
| Configuration | Yes | Required environment variables and configuration. |

---

## Quality Requirements

12 quality requirements define the acceptance criteria for the
output. Each requirement has a unique identifier and a severity
level. Requirements QR-001 through QR-008 are base requirements.
Requirements QR-009 through QR-012 are extended requirements for
self-bootstrap and dynamic discovery enforcement.

### QR-001: TOML Parse Validity

**Severity:** CRITICAL

The workflow.toml file must be valid TOML. The file must parse
without errors using a standard TOML parser. Invalid TOML causes
immediate rejection.

**Verification method:** TOML parser parse check.

### QR-002: Python Syntax Validity

**Severity:** CRITICAL

The context_extensions.py and actions.py files must be valid
Python. The files must compile without syntax errors using
Python 3.12+ syntax rules.

**Verification method:** Python compile() or ast.parse() check.

### QR-003: TYPE_CHECKING Runtime Import Detection

**Severity:** CRITICAL

Neither context_extensions.py nor actions.py may import modules
under TYPE_CHECKING guards that are used at runtime. All runtime
imports must be unconditional. This prevents import errors when
the runner loads the modules.

**Verification method:** Static analysis for TYPE_CHECKING import
usage patterns.

### QR-004: Artifact Binding Consistency

**Severity:** CRITICAL

Every artifact key referenced in a step's required_inputs must be
produced by a preceding step or declared as a workflow input
artifact. No dangling references are permitted. This enforces
VR-012 at the output level.

**Verification method:** Cross-reference check between step
required_inputs and artifact declarations.

### QR-005: Action Step Implementation Completeness

**Severity:** CRITICAL

Every step with step_type: action must have a corresponding
implementation in actions.py. The @action decorator must reference
the correct step_name. Missing implementations cause rejection.

**Verification method:** Cross-reference check between action steps
in workflow.toml and @action decorators in actions.py.

### QR-006: Prompt File Existence

**Severity:** CRITICAL

Every step with step_type: prompt must have a corresponding .txt
file in the prompts/ directory. The filename must match the pattern
NN_{step_name}.txt. Missing prompt files cause rejection.

**Verification method:** Directory listing check against prompt-type
steps in workflow.toml.

### QR-007: Prompt Placeholder vs required_inputs Consistency

**Severity:** CRITICAL

Every {PLACEHOLDER} found in a prompt template must be declared in
the corresponding step's required_inputs array or in the workflow's
global artifact declarations. Undeclared placeholders indicate
missing input declarations.

**Verification method:** Regex scan of prompt files for {PLACEHOLDER}
patterns, cross-referenced with step required_inputs.

### QR-008: context_extensions.py Artifact Key Coverage

**Severity:** CRITICAL

The register_artifact_keys() function in context_extensions.py must
register all artifact keys declared in the workflow.toml [artifacts]
section. Missing registrations cause placeholder resolution failures
at runtime.

**Verification method:** Cross-reference check between TOML artifact
declarations and register_artifact_keys() function body.

### QR-009: Standards Directory Existence

**Severity:** CRITICAL

The Standards/ directory must exist in the output and must contain
the file COMPOSITION_STANDARD.md. This enforces Part 1 of the
3-part output structure.

**Verification method:** Directory and file existence check.

### QR-010: Specs Directory Existence

**Severity:** CRITICAL

The Specs/ directory must exist in the output and must contain at
least one .md file. This enforces Part 2 of the 3-part output
structure and validates that the embed_builder_spec step completed
successfully.

**Verification method:** Directory existence check and file listing
for .md files.

### QR-011: Bidirectional Prompt Placeholder Consistency

**Severity:** CRITICAL

All {PLACEHOLDER} tokens in prompt templates must be declared in
their step's required_inputs or produces arrays. Additionally, every
artifact in required_inputs/produces that uses UPPER_SNAKE_CASE
naming convention must appear as a {PLACEHOLDER} in the prompt or
be a known runtime-resolved value. This bidirectional check catches
both missing declarations and unused declarations.

**Verification method:** Bidirectional cross-reference between prompt
{PLACEHOLDER} patterns and step artifact declarations.

### QR-012: STANDARDS_COMPOSITION_STANDARD_FILE Declaration

**Severity:** CRITICAL

Both the generate_package step and the refine_package step must
declare STANDARDS_COMPOSITION_STANDARD_FILE in their produces lists.
This ensures the composition standard is always generated during
package assembly, regardless of whether the package was generated
fresh or refined after review rejection.

**Verification method:** Check workflow.toml [[step]] sections for
generate_package and refine_package to verify STANDARDS_COMPOSITION_STANDARD_FILE
appears in both produces arrays.

---

## Downstream Extraction Contracts

Downstream extraction contracts define how consumers of the output
can reliably extract specific information. Each contract specifies
what data is available, where to find it, and what format to expect.

### DEC-001: Workflow Manifest Extraction

**Consumer:** Workflow runner (step_runner.py, coder_adapters.py)
**Source:** workflow.toml
**Extraction method:** TOML parser

The workflow runner extracts the following from workflow.toml:

| Data | TOML Path | Usage |
|---|---|---|
| Workflow name | [workflow].name | Job identification |
| Step definitions | [[step]] sections | Step execution dispatch |
| Step types | [[step]].type | Dispatch to prompt or action handler |
| Coder roles | [[step]].coder.role | Coder backend selection |
| Routing rules | [[step]].onsuccess, [[step]].on_reject_refine | Step sequence control |
| Artifact declarations | [artifacts] section | Artifact key registration |
| Required inputs per step | [[step]].required_inputs | Input resolution before step execution |
| Produced outputs per step | [[step]].produces | Output tracking after step completion |

**Contract:** The workflow.toml file is self-contained. All
information needed for step dispatch, routing, and artifact tracking
is present in this single file. No external file reads are required
for basic workflow execution.

### DEC-002: Prompt Template Extraction

**Consumer:** Coder adapters (coder_adapters.py)
**Source:** prompts/*.txt
**Extraction method:** Plain text read with placeholder substitution

The coder adapter extracts prompt templates from the prompts/
directory. Each .txt file contains the full prompt for one step.
Placeholders ({PLACEHOLDER_NAME}) are substituted with resolved
values before sending to the LLM.

| Data | Source | Usage |
|---|---|---|
| Full prompt text | prompts/NN_{step_name}.txt | LLM instruction payload |
| Placeholder tokens | Regex scan for {UPPER_SNAKE_CASE} | Context injection points |
| Self-critic section | Prompt content | Reasoning quality check |
| Self-validation section | Prompt content | Completeness verification |

**Contract:** Prompt files are plain text with UTF-8 encoding
(ASCII subset). Placeholder tokens use the {UPPER_SNAKE_CASE}
pattern. All placeholders must be resolvable from the 4 data
sources defined in Layer 2.

### DEC-003: Composition Standard Extraction

**Consumer:** context_extensions.py discover_component_types()
**Source:** Standards/COMPOSITION_STANDARD.md
**Extraction method:** YAML frontmatter parse + heading scan

The context_extensions module extracts component type information
from the composition standard for dynamic discovery:

| Data | Source Location | Usage |
|---|---|---|
| component_type_count | YAML frontmatter | Validation: expected number of types |
| Type names | Headings "#### Type N: {name}" | Dynamic type list for prompts |
| standard_name | YAML frontmatter | Standard identification |
| standard_version | YAML frontmatter | Version compatibility check |
| schema_sections | YAML frontmatter or body | Layer completeness validation |

**Contract:** The composition standard uses YAML frontmatter with
known field names. Component types are defined in the body using
"#### Type N: {type_name}" heading pattern. The discover function
must handle malformed input gracefully (fallback to 8 base types).

---

## Example Output

This section provides a complete example of resolved output for a
Workflow Builder v3 meta-meta builder.

### Directory Structure

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

### workflow.toml (excerpt)

```toml
[workflow]
name = "workflow_builder_v3"
version = "3.0.0"
description = "Self-bootstrapping meta-meta builder"

[artifacts]
WORKFLOW_SPEC_FILE = { required = true }
TEST_CRITERIA_FILE = { filename_pattern = "TEST_CRITERIA-{seq}.md", produced_by = "generate_test_criteria" }
COMPONENT_SCHEMA_FILE = { filename_pattern = "COMPONENT_SCHEMA-{seq}.md", produced_by = "generate_component_schema" }
# ... additional artifact declarations ...

[[step]]
step_name = "generate_test_criteria"
type = "prompt"
purpose = "Generate acceptance criteria for the workflow"
required_inputs = ["WORKFLOW_SPEC_FILE"]
produces = ["TEST_CRITERIA_FILE"]
enable_notifications = false
requires_human_approval_after = false

[step.coder]
role = "architect_standard"

[step.onsuccess]
next = "review_test_criteria"

# ... additional steps ...
```

### context_extensions.py (excerpt)

```python
"""Context extensions for workflow_builder_v3."""

from pathlib import Path


def register_artifact_keys() -> dict:
    """Register all artifact keys with their filename patterns."""
    return {
        "TEST_CRITERIA_FILE": "TEST_CRITERIA-{seq}.md",
        "COMPONENT_SCHEMA_FILE": "COMPONENT_SCHEMA-{seq}.md",
        "COMPOSITION_FORMAT_FILE": "COMPOSITION_FORMAT-{seq}.md",
        "OUTPUT_FORMAT_FILE": "OUTPUT_FORMAT-{seq}.md",
        # ... additional registrations ...
    }


def discover_component_types(standard_path: str) -> str:
    """Parse COMPOSITION_STANDARD.md and return comma-separated type list."""
    path = Path(standard_path)
    content = path.read_text(encoding="utf-8")
    types = []
    for line in content.splitlines():
        if line.startswith("#### Type ") and ":" in line:
            type_name = line.split(":", 1)[1].strip()
            types.append(type_name)
    if not types:
        # Fallback to 8 base types
        types = [
            "step_definition", "role_policy", "routing_pattern",
            "prompt_pattern", "artifact_contract",
            "composition_standard", "output_variance", "domain_spec",
        ]
    return ", ".join(types)
```

### actions.py (excerpt)

```python
"""Custom action steps for workflow_builder_v3."""

import shutil
from pathlib import Path


def embed_builder_spec(*, context, state, step_cfg, project_root):
    """Copy the input spec to the output Specs/ directory."""
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


def validate_package_deterministic(*, context, state, step_cfg, project_root):
    """Run 11 deterministic validation checks on the package."""
    checks = []
    # Check 1: TOML parse validity
    # Check 2: Python syntax check
    # ... checks 3 through 11 ...
    return {
        "status": "APPROVED",
        "remark": f"All 11 checks passed",
        "artifacts": {"VALIDATION_REPORT_FILE": str(report_path)},
    }


def promote_workflow_package(*, context, state, step_cfg, project_root):
    """Promote the 3-part output to the workflows/ directory."""
    # Enforce 3-part promotion including Standards/ and Specs/
    # ...
    return {
        "status": "APPROVED",
        "remark": "Promoted 3-part output to workflows/",
        "artifacts": {"WORKFLOW_PACKAGE_DIR_FILE": str(target_dir)},
    }
```

### prompts/01_generate_test_criteria.txt (excerpt)

```
# Generate Test Criteria

## Objective
Generate acceptance criteria for the workflow based on the
composition system specification.

## Reference Inputs
Read the following files before producing output:
- WORKFLOW_SPEC_FILE: {WORKFLOW_SPEC_FILE}

## Generation Tasks
1. Read the workflow specification
2. Identify all phases and steps
3. Define acceptance criteria for each phase
4. Ensure all criteria are verifiable and traceable

## Self-Critic
- Did you read the spec for each property or invent them?
- Are your criteria specific and enforceable?

## Self-Validation
- Verify all phases have corresponding criteria
- Check that criteria count matches frontmatter
- Confirm traceability to spec sections

## Output Instructions
Write the test criteria to: {TEST_CRITERIA_FILE}
Format: Markdown with YAML frontmatter
```

---

## Self-Validation

This section verifies that the output format document satisfies
all defined requirements.

### Resolution Rules Completeness

| Rule ID | Source | Target | Defined |
|---|---|---|---|
| RR-001 | step_bindings | workflow.toml [[step]] sections | YES |
| RR-002 | coder bindings | workflow.toml [[step]].coder | YES |
| RR-003 | routing bindings | workflow.toml routing fields | YES |
| RR-004 | prompt_patterns | prompts/NN_{step_name}.txt | YES |
| RR-005 | artifact_bindings | context_extensions.py + TOML | YES |
| RR-006 | composition_standard_binding | Standards/COMPOSITION_STANDARD.md | YES |
| RR-007 | {PLACEHOLDER} tokens | Resolved values from 4 sources | YES |
| RR-008 | self_bootstrap_binding | Specs/{builder_name}.md | YES |
| RR-009 | DISCOVERED_COMPONENT_TYPES | Prompt templates | YES |

**Verification:** 9 resolution rules defined (RR-001 through
RR-009). TC-025 satisfied.

### Quality Requirements Completeness

| Rule ID | Requirement | Severity | Defined |
|---|---|---|---|
| QR-001 | TOML parse validity | CRITICAL | YES |
| QR-002 | Python syntax validity | CRITICAL | YES |
| QR-003 | TYPE_CHECKING detection | CRITICAL | YES |
| QR-004 | Artifact binding consistency | CRITICAL | YES |
| QR-005 | Action implementation completeness | CRITICAL | YES |
| QR-006 | Prompt file existence | CRITICAL | YES |
| QR-007 | Prompt placeholder consistency | CRITICAL | YES |
| QR-008 | Artifact key coverage | CRITICAL | YES |
| QR-009 | Standards/ directory existence | CRITICAL | YES |
| QR-010 | Specs/ directory existence | CRITICAL | YES |
| QR-011 | Bidirectional placeholder consistency | CRITICAL | YES |
| QR-012 | STANDARDS_COMPOSITION_STANDARD_FILE declaration | CRITICAL | YES |

**Verification:** 12 quality requirements defined (QR-001 through
QR-012). TC-028 satisfied.

### Output Structure Completeness

| Part | Directory | Primary File | Defined |
|---|---|---|---|
| Part 1 | Standards/ | COMPOSITION_STANDARD.md | YES |
| Part 2 | Specs/ | {builder_name}.md | YES |
| Part 3 | {builder_name}/ | workflow.toml + package files | YES |

**Verification:** 3 output parts defined. TC-024 satisfied.

### Promotion Contract Completeness

| Source | Target | Mandatory | Defined |
|---|---|---|---|
| workflow.toml | workflows/{slug}/workflow.toml | Yes | YES |
| context_extensions.py | workflows/{slug}/context_extensions.py | Yes | YES |
| actions.py | workflows/{slug}/actions.py | If exists | YES |
| README.md | workflows/{slug}/README.md | Yes | YES |
| prompts/ | workflows/{slug}/prompts/ | Yes | YES |
| Standards/ | workflows/{slug}/Standards/ | Yes (enforced) | YES |
| Specs/ | workflows/{slug}/Specs/ | Yes (enforced) | YES |
| .env.sample | workflows/{slug}/.env.sample | If exists | YES |
| config.json.sample | workflows/{slug}/config.json.sample | If exists | YES |

**Verification:** 9 file/directory mappings defined. TC-033
satisfied.

### Downstream Extraction Contracts Completeness

| Contract | Consumer | Source | Defined |
|---|---|---|---|
| DEC-001 | Workflow runner | workflow.toml | YES |
| DEC-002 | Coder adapters | prompts/*.txt | YES |
| DEC-003 | context_extensions.py | Standards/COMPOSITION_STANDARD.md | YES |

**Verification:** 3 downstream extraction contracts defined.

### Criteria Traceability

| Criteria | Status | Evidence |
|---|---|---|
| TC-024 | PASS | 3-part output structure in Output Structure section |
| TC-025 | PASS | 9 resolution rules defined (RR-001 through RR-009) |
| TC-026 | PASS | RR-008 maps self_bootstrap_binding to Specs/{builder_name}.md |
| TC-027 | PASS | RR-009 maps DISCOVERED_COMPONENT_TYPES to prompt templates |
| TC-028 | PASS | 12 quality requirements defined (QR-001 through QR-012) |
| TC-029 | PASS | QR-009 enforces Standards/ with COMPOSITION_STANDARD.md at CRITICAL |
| TC-030 | PASS | QR-010 enforces Specs/ with at least one .md file at CRITICAL |
| TC-031 | PASS | QR-011 enforces placeholder declaration consistency at CRITICAL |
| TC-032 | PASS | QR-012 enforces STANDARDS_COMPOSITION_STANDARD_FILE in both steps at CRITICAL |
| TC-033 | PASS | Promotion contract with 9 file/directory mappings |

**Verification:** All Phase 4 criteria (TC-024 through TC-033)
are satisfied by this document.

---

End of Output Format Document
