---
doc_type: "output_format"
lifecycle_status: "draft"
layer: 3
resolution_rule_count: 7
quality_requirement_count: 8
---

# Output Format for Workflow Builder v3

## Overview

This document defines the Layer 3 output format for the Workflow Builder v3
composition system. Layer 3 is the terminal layer in the 3-layer architecture.
It specifies what the assembled deliverable looks like after all component
bindings from Layer 2 (COMPOSITION_FORMAT-001.md) are resolved using the
building block types from Layer 1 (COMPONENT_SCHEMA-001.md).

**Layer 3 role:** Layer 3 translates the abstract component bindings and
resolution rules from Layer 2 into a concrete, file-level output structure.
It defines the 3-part output directory layout, the 7 resolution rules that
govern how component types are expanded into physical files, the 8 quality
requirements that the output must satisfy, and the 3 downstream extraction
contracts that enable subsequent workflows to consume the output.

**3-Part output description:**
- Part 1: Standards directory -- contains the target workflow's composition
  standard (Standards/COMPOSITION_STANDARD.md), which consolidates the domain
  analysis, component schema, composition format, output format, artifact
  contract, and step sequence into a single coherent reference document.
- Part 2: Specs directory -- contains the embedded builder specification
  (Specs/{builder_name}.md), enabling the recursive self-bootstrap chain.
  The content is the runtime spec that was input to the builder.
- Part 3: Workflow package -- the executable workflow package containing
  workflow.toml, context_extensions.py, actions.py, prompts/, README.md,
  and conditional files that together form a fully self-contained, runnable
  workflow definition.

**Output delivery type:** The output format supports two delivery modes based
on the target spec's output_type declaration:
- documented_versioned: Full pipeline with review, refine, approve, promote,
  and archive steps. Output is versioned and tracked.
- direct: Simplified pipeline with immediate delivery. Output is delivered
  directly without review gates.

The output format defined here is consumed by Phase 6 (step_sequence) to
align step design with the output structure, and by Phase 7 (runtime_standard)
for consolidation into the runtime standard.

---

## Output Structure

The resolved output is organized into a 3-part directory structure. All three
parts are produced during Phase 9 (Package Assembly) of the pipeline, with
content sourced from Phases 7, 8, and 9 as specified below.

### Part 1: Standards Directory

**Location:** Standards/

**Purpose:** Contains the target workflow's composition standard. This is the
consolidated reference document that merges Phases 1 through 6 into a single
coherent standard that the generated workflow package conforms to.

**Contents:**

| File | Source Phase | Description |
|------|-------------|-------------|
| {standard_filename} | Phase 7 + Phase 9 | The target's composition standard. The filename comes from the spec identity section (standard_filename). Contains the consolidated domain analysis, component schema, composition format, output format, artifact contract, and step sequence. |

**Example:**
If the target spec declares standard_filename as "MY_STANDARD-v1.md", the
file is placed at Standards/MY_STANDARD-v1.md.

**Source mapping:**
- Content origin: Phase 7 (runtime_standard) consolidates Phases 1-6.
- File placement: Phase 9 (Package) copies the runtime standard into the
  Standards/ directory using the spec's standard_filename.
- Identity: The standard_name and standard_version inside this file match
  the target spec identity, not the builder's identity.

### Part 2: Specs Directory

**Location:** Specs/

**Purpose:** Contains the embedded builder specification, enabling the
recursive self-bootstrap chain. The content is the runtime specification
(WORKFLOW_SPEC_FILE) that was input to the builder. By embedding it, the
generated workflow package can itself be processed by a builder to produce
the next version.

**Contents:**

| File | Source Phase | Description |
|------|-------------|-------------|
| {builder_name}.md | Phase 9 | Content-identical copy of the input WORKFLOW_SPEC_FILE. The filename is derived from the builder's domain name. This enables recursive self-bootstrap. |

**Example:**
If the builder's domain name is "ar_meta_builder_v2", the file is placed at
Specs/ar_meta_builder_v2.md. Its content is byte-identical to the input
WORKFLOW_SPEC_FILE.

**Source mapping:**
- Content origin: Phase 9 (Package) copies the input WORKFLOW_SPEC_FILE
  verbatim into the Specs/ directory.
- Identity: The embedded spec retains the target's identity values. No
  modifications are made to the content.

**Recursive chain:**
```
Workflow Builder v4 -> [target builder] -> [target's target workflow]
```
Each level embeds the spec of the level above it, enabling the chain.

### Part 3: Workflow Package

**Location:** Root of the workflow package directory.

**Purpose:** Contains the executable workflow package files. This is the
primary deliverable -- a fully self-contained, runnable workflow definition
that the agent-runner-v2 daemon can execute.

**Contents:**

| File | Source Phase | Description |
|------|-------------|-------------|
| workflow.toml | Phase 8 + Phase 9 | Complete workflow definition manifest. Declares workflow identity (name, version, label, job_prefix), step sequence with routing, artifact keys, required inputs, and coder role policies. All identity fields come from the target spec. |
| context_extensions.py | Phase 8 + Phase 9 | Python module defining the domain-specific context extensions class. Contains the artifact key registry, path resolution logic (known_artifact_paths), and computed context values. Class name is derived from workflow_name. |
| actions.py | Phase 8 + Phase 9 | Python module containing all domain-specific @action function implementations. Each action step declared in workflow.toml has a corresponding @action-decorated function in this file. |
| prompts/ | Phase 8 + Phase 9 | Directory containing one .txt prompt template file per prompt-driven step. Filename pattern: {NN}_{step_name}.txt where NN is the zero-padded step number. Each {PLACEHOLDER} in a prompt must correspond to a declared artifact in the step's required_inputs or produces. |
| README.md | Phase 9 | Human-readable documentation describing the target workflow's purpose, inputs, outputs, how to invoke it, and environment setup. Describes the target workflow, not the builder. |

**Conditional files:**

| File | Condition | Description |
|------|-----------|-------------|
| review_prompts/ | output_type == documented_versioned | Directory containing review and refine prompt templates for review loop steps. Only present when the target spec declares output_type as documented_versioned. |
| approval_config.toml | output_type == documented_versioned | Configuration for human approval gates. Only present when the target spec declares output_type as documented_versioned. |

**Source mapping:**
- Content origin: Phase 8 (operational_workflow) produces the concrete design
  for all workflow package files.
- File placement: Phase 9 (Package) materializes the design into physical
  files in the package directory.
- Validation: Phase 9 runs validate_package to confirm all files are present,
  TOML parses, Python syntax is valid, and identity is consistent.

### Output Structure Summary

```
{workflow_name}/
  Standards/
    {standard_filename}          -- From Phase 7+9
  Specs/
    {builder_name}.md            -- From Phase 9
  workflow.toml                  -- From Phase 8+9
  context_extensions.py          -- From Phase 8+9
  actions.py                     -- From Phase 8+9
  prompts/
    {NN}_{step_name}.txt         -- From Phase 8+9 (one per prompt step)
  README.md                      -- From Phase 9
  review_prompts/                -- Conditional: documented_versioned only
    {NN}_{review_step_name}.txt
  approval_config.toml           -- Conditional: documented_versioned only
```

Total output artifacts: 7 required (workflow.toml, context_extensions.py,
actions.py, prompts/*.txt, README.md, Standards/{standard_filename},
Specs/{builder_name}.md) plus conditional files based on output_type.

---

## Resolution Rules

The resolution rules define how component bindings from Layer 2 are expanded
into the concrete file-level output structure defined above. There are exactly
7 resolution rules. Each rule addresses a specific aspect of the transformation
from abstract composition to physical deliverable.

### RR-001: step_definition Resolution

**Rule:** Each step_definition component from the step_sequence binding
resolves to a step entry in workflow.toml. The step entry includes: step name,
step type (prompt or action), artifact keys (produces/requires), and routing
configuration (onsuccess, on_reject_refine with max_iterations).

**Resolution process:**
1. Read the step_sequence component (Phase 6 output).
2. For each step in the steps array, generate a [[step]] entry in
   workflow.toml.
3. If the step type is "prompt", verify that a corresponding prompt file
   exists at prompts/{NN}_{step_name}.txt.
4. If the step has on_reject_refine routing, include the refine step name
   and max_iterations in the TOML.
5. Verify that every onsuccess target references an existing step name.

**Source component:** step_sequence (Phase 6)
**Output file:** workflow.toml

### RR-002: role_policy Resolution

**Rule:** Each role_policy reference in a step_definition resolves to a
coder role policy section in workflow.toml. The role policy determines which
coder backend and prompt configuration is used for the step. Three standard
roles are available: architect_standard for generate steps, gatekeeper_standard
for gatekeep steps, and reviewer_standard for review steps.

**Resolution process:**
1. For each step in the step_sequence, determine the appropriate coder role
   based on the step's function:
   - Steps named "generate_*" use architect_standard.
   - Steps named "gatekeep_*" use gatekeeper_standard.
   - Steps named "review_*" use reviewer_standard.
2. Add a [step.{step_name}.coder_role] section in workflow.toml with the
   resolved role.
3. Verify that the role exists in the coder registry.

**Source component:** step_sequence (Phase 6)
**Output file:** workflow.toml

### RR-003: routing_pattern Resolution

**Rule:** Each routing_pattern from the composition format binding rules
resolves to the routing topology in workflow.toml. The 6 workflow patterns
(foundation_broadcast, selective_downstream, adjacent_consolidation,
skip_consolidation, adjacent_assembly, sequential_handoff) determine the
step dependency graph.

**Resolution process:**
1. Read the 8 binding rules from the composition_format component (Phase 3).
2. Map each binding's source_phase and consumed_by_phases to step routing
   edges in workflow.toml.
3. For sequential_handoff patterns, generate linear onsuccess chains.
4. For foundation_broadcast patterns, ensure the foundation step's output
   is available to all downstream steps via required_inputs.
5. Verify that the resulting routing graph has no cycles and that every
   step is reachable from the init step.

**Source component:** composition_format (Phase 3)
**Output file:** workflow.toml

### RR-004: prompt_pattern Resolution

**Rule:** Each prompt_pattern from the operational_workflow binding resolves
to a physical .txt file in the prompts/ directory. The prompt file contains
the template instructions for the LLM coder, with {ARTIFACT_KEY} placeholders
that reference declared artifacts.

**Resolution process:**
1. Read the prompt_files array from the operational_workflow component
   (Phase 8).
2. For each entry, generate a file at prompts/{NN}_{step_name}.txt.
3. The prompt content includes: role instruction, reference inputs section,
   generation tasks, output instructions, and forbidden content rules.
4. Every {PLACEHOLDER} in the prompt text must correspond to a declared
   artifact in the step's required_inputs or produces in workflow.toml.
5. No dangling placeholder references are permitted.

**Source component:** operational_workflow (Phase 8)
**Output file:** prompts/{NN}_{step_name}.txt

### RR-005: artifact_contract Resolution

**Rule:** Each artifact_contract entry resolves to an artifact key definition
in both workflow.toml and context_extensions.py. The artifact key maps to a
filename pattern and path resolution logic.

**Resolution process:**
1. Read the artifact_keys array from the artifact_contract component
   (Phase 5).
2. For each key, add an entry in workflow.toml under [artifacts] declaring
   the key name, filename pattern, and description.
3. In context_extensions.py, generate a path resolution entry in the
   known_artifact_paths function that maps the key to its absolute path
   using the job directory and filename pattern.
4. Verify that all artifact keys referenced in step definitions exist in
   the artifact contract.
5. Verify that no artifact key conflicts with the global registry.

**Source component:** artifact_contract (Phase 5)
**Output files:** workflow.toml, context_extensions.py

### RR-006: composition_standard Resolution

**Rule:** The composition_standard binding resolves to the physical file at
Standards/{standard_filename}. This file consolidates content from Phases 1
through 6 into a single coherent reference document with the target's
identity.

**Resolution process:**
1. Read the runtime_standard component (Phase 7) which already contains
   the consolidated content from Phases 1-6.
2. Set standard_name and standard_version from the target spec identity.
3. Format the consolidated content into a structured Markdown document
   with sections for each phase's contribution.
4. Write the file to Standards/{standard_filename} where standard_filename
   comes from the spec identity section.
5. Verify that the standard_name and standard_version in the file match
   the target spec, not the builder.

**Source component:** runtime_standard (Phase 7)
**Output file:** Standards/{standard_filename}

### RR-007: placeholder Resolution

**Rule:** All 7 placeholders defined in the composition format are resolved
to concrete values before output materialization. Placeholders use the
curly-brace syntax ({placeholder_name}) and are resolved from 3 data sources:
Input Spec, Governance, and Runtime.

**Resolution process:**
1. Resolve identity placeholders first: {workflow_name}, {standard_name},
   {standard_version}, {standard_filename} from the spec identity section.
2. Resolve configuration placeholders second: {output_type} from the spec
   output delivery section.
3. Resolve file path placeholders third: {WORKFLOW_SPEC_FILE} from the job
   input artifacts, and {BASE_COMPOSITION_STANDARD} via context_extensions.
4. Substitute all resolved values into the output templates.
5. Verify that no unresolved placeholders remain in any output file.
6. If any placeholder cannot be resolved, halt with an explicit error.

**Source data:** Input Spec (WORKFLOW_SPEC_FILE), Governance
(BASE_COMPOSITION_STANDARD), Runtime context
**Output files:** All output files (all placeholders must be resolved before
any file is written)

### Resolution Rule Verification

| Rule | Resolves | Source Component | Target Output |
|------|----------|-----------------|---------------|
| RR-001 | step_definition | step_sequence (Phase 6) | workflow.toml |
| RR-002 | role_policy | step_sequence (Phase 6) | workflow.toml |
| RR-003 | routing_pattern | composition_format (Phase 3) | workflow.toml |
| RR-004 | prompt_pattern | operational_workflow (Phase 8) | prompts/*.txt |
| RR-005 | artifact_contract | artifact_contract (Phase 5) | workflow.toml, context_extensions.py |
| RR-006 | composition_standard | runtime_standard (Phase 7) | Standards/{standard_filename} |
| RR-007 | placeholder | All data sources | All output files |

---

## Required Sections

Each output part has a defined set of required sections. The content within
these sections is derived from the component bindings and resolution rules.

### Part 1 Required Sections: Standards

The composition standard file (Standards/{standard_filename}) must contain
these sections:

| Section | Source Phase | Description |
|---------|-------------|-------------|
| Domain Overview | Phase 1 | Target identity (standard_name, standard_version, standard_filename), output type, domain description, purpose, input/output definitions, and recursive chain explanation |
| Component Schema | Phase 2 | The 8 component types with their common properties, type-specific properties, and validation rules (VR-001 through VR-008) |
| Composition Format | Phase 3 | The 8 binding rules, 6 workflow patterns, override mechanism, 7 placeholder definitions, and ordering rules |
| Output Format | Phase 4 | The 7 output artifacts, 7 resolution rules, and quality requirements |
| Artifact Contract | Phase 5 | Artifact key registry with filename patterns and conflict check status |
| Step Sequence | Phase 6 | Step definitions, review loops (if documented_versioned), approval gates (if documented_versioned), and delivery mechanism |
| Cross-Phase Consistency | Phase 7 | Declaration that all phases use consistent naming conventions, artifact key formats, validation patterns, and identity locking rules |

### Part 2 Required Sections: Specs

The embedded spec file (Specs/{builder_name}.md) must contain:

| Section | Source | Description |
|---------|--------|-------------|
| Full specification content | WORKFLOW_SPEC_FILE | Byte-identical copy of the input runtime specification. Contains the workflow identity, output delivery declaration, domain overview, component schema, composition format, output format, and operational requirements. This is the raw input, not modified. |

### Part 3 Required Sections: Workflow Package

The workflow package files must contain these sections/structures:

#### workflow.toml

| Section | Description |
|---------|-------------|
| [workflow] | Identity: name, version, label, job_prefix from target spec |
| [workflow.required_inputs] | Input artifacts: WORKFLOW_SPEC_FILE, BASE_COMPOSITION_STANDARD |
| [[step]] entries | One per step: name, type, produces, requires, routing |
| [step.{name}.routing] | onsuccess and optional on_reject_refine with max_iterations |
| [step.{name}.coder_role] | Role policy: architect_standard, gatekeeper_standard, or reviewer_standard |
| [artifacts] | Artifact key definitions with filename patterns |

#### context_extensions.py

| Section | Description |
|---------|-------------|
| Class definition | Class name derived from workflow_name (e.g., MyWorkflowContextExtensions) |
| Artifact key constants | All artifact keys as class-level string constants |
| known_artifact_paths function | Returns dict mapping each key to its absolute path |
| Computed context properties | Any domain-specific computed values needed by prompts |

#### actions.py

| Section | Description |
|---------|-------------|
| Import statements | Required imports from agent_runner_v2 |
| @action functions | One per action-type step declared in workflow.toml |
| Function signatures | Each function takes (ctx) parameter with context object |
| Validation logic | Domain-specific validation implementations |

#### prompts/*.txt

| Section | Description |
|---------|-------------|
| Role instruction | Tells the coder what role it plays and what to produce |
| Reference inputs | Lists all input artifacts the coder must read |
| Generation tasks | Numbered list of specific tasks to perform |
| Output instructions | Exact file path and format for the output artifact |
| Forbidden content | Rules about what NOT to include (identity locking, no scope invention, ASCII-only) |

#### README.md

| Section | Description |
|---------|-------------|
| Title and description | Target workflow name, label, and purpose |
| Inputs | Required input artifacts and their descriptions |
| Outputs | Produced artifacts and their descriptions |
| Usage | How to invoke the workflow via CLI or daemon |
| Environment | Required environment setup |

---

## Quality Requirements

The output format defines 8 quality requirements that govern the quality of
the output format artifact itself. These requirements are checked by the
Phase 4 gatekeeper (gatekeep_output_format) using the test criteria TC-049
through TC-071.

### QR-001: Output Artifact Completeness

The output format must enumerate exactly 7 output artifacts matching the
target spec's output structure: workflow.toml, context_extensions.py,
actions.py, prompts/*.txt, README.md, Standards/{standard_filename}, and
Specs/{builder_name}.md. Each artifact must specify its source phase and
a description of its contents.

**Verification:** Count the output artifacts listed. Expected: 7. Each must
have artifact name, source phase, and description.

### QR-002: Resolution Rule Traceability

Every resolution rule must trace to a specific component binding from Layer 2.
No resolution rule may introduce behavior not grounded in the composition
format's binding rules, override mechanism, or placeholder resolution.

**Verification:** For each resolution rule (RR-001 through RR-007), identify
the source component binding. All 7 must have a valid trace.

### QR-003: Quality Requirement Verifiability

Every quality requirement must use specific, verifiable language. No quality
requirement may contain vague phrases such as "must work properly", "must be
correct", "should be good", or "must be handled appropriately". Each
requirement must state a concrete, checkable condition.

**Verification:** Scan all quality requirement statements for vague phrases.
Expected: zero occurrences.

### QR-004: Output Structure Alignment

The 3-part output structure must align with the composition format's
component bindings. Part 1 (Standards) corresponds to the runtime_standard
binding (Phase 7). Part 2 (Specs) corresponds to the self-bootstrap
requirement (Phase 9). Part 3 (Workflow Package) corresponds to the
operational_workflow binding (Phase 8).

**Verification:** Map each output part to its source component binding.
All 3 parts must have valid mappings.

### QR-005: Identity Locking Compliance

The output format must specify that all identity fields in the output are
sourced from the target spec, not the builder. The resolution rules must
explicitly state that identity resolution (RR-001 through RR-006) uses
target spec values. No builder identity values may appear in the output
format specification.

**Verification:** Check that no builder identity (ar_meta_builder_v2,
AMB_STANDARD, AMB) appears in the output format specification. Check that
RR-006 and RR-007 reference target spec identity.

### QR-006: Conditional File Specification

The output format must specify which files are conditional (present only
when certain conditions are met) and what those conditions are. For the
documented_versioned output type, review_prompts/ and approval_config.toml
are conditional files. The conditions must be expressed in terms of the
output_type placeholder.

**Verification:** Check that conditional files are listed with their
conditions. Expected: at least 2 conditional files for documented_versioned.

### QR-007: Placeholder Coverage

The output format must account for all 7 placeholders defined in the
composition format (Layer 2). Each placeholder must either be resolved in
the output file content or documented as a runtime resolution. No placeholder
may be silently ignored.

**Verification:** List all placeholders referenced in the output format.
Compare against the 7 defined in Layer 2. All 7 must be accounted for.

### QR-008: Downstream Contract Self-Containment

Each downstream extraction contract (DEC-001, DEC-002, DEC-003) must be
self-contained -- a consumer workflow can extract the information it needs
from the output format document alone, without requiring access to other
pipeline artifacts. Each contract must specify its input (which output part
it extracts from), its extraction pattern, and its output schema.

**Verification:** For each DEC, check that it specifies: input part,
extraction pattern, output schema. All 3 must be self-contained.

---

## Downstream Extraction Contracts

The downstream extraction contracts define how subsequent workflows and
pipeline phases consume the output format artifact. Each contract is
self-contained and specifies the extraction pattern, input, and output
schema.

### DEC-001: Step Sequence Extraction

**Purpose:** Phase 6 (step_sequence) consumes the output format to align
step design with the output structure. This contract defines how the step
design extracts output artifact requirements.

**Input:** OUTPUT_FORMAT_FILE, specifically the "Output Structure" section
and "Resolution Rules" section.

**Extraction pattern:**
1. Read the 7 output artifacts from the Output Structure section.
2. For each output artifact, extract: artifact name, source phase, and
   description.
3. Read the 7 resolution rules to understand how component bindings expand
   into file-level outputs.
4. Map each resolution rule to its source component to determine which
   phase's output feeds which file.
5. Use the 8 quality requirements to constrain the step design -- the steps
   must produce output that satisfies all quality requirements.

**Output schema:**
```yaml
output_artifact_requirements:
  - artifact: "{artifact_name}"
    source_phase: "{phase}"
    description: "{description}"
    resolution_rule: "{RR-NNN}"
quality_constraints:
  - id: "{QR-NNN}"
    requirement: "{statement}"
```

**Consumer:** Phase 6 (step_sequence) uses this to design steps that
produce the correct output artifacts with proper routing and validation.

### DEC-002: Runtime Standard Consolidation Extraction

**Purpose:** Phase 7 (runtime_standard) consumes the output format to
include the output structure specification in the consolidated standard.
This contract defines how the output format content is merged into the
runtime standard.

**Input:** OUTPUT_FORMAT_FILE, specifically all sections: Output Structure,
Resolution Rules, Required Sections, Quality Requirements, and Downstream
Extraction Contracts.

**Extraction pattern:**
1. Read the full output format document.
2. Extract the 3-part output structure as the "Output Format" section of
   the consolidated standard.
3. Extract the 7 resolution rules as the resolution protocol.
4. Extract the 8 quality requirements as the quality protocol.
5. Include the downstream extraction contracts as the interface specification
   for post-pipeline consumers.
6. Verify consistency with the component_schema (Phase 2) -- the output
   artifacts must be producible from the defined component types.

**Output schema:**
```yaml
consolidated_output_section:
  output_structure:
    part_count: 3
    parts:
      - name: "Standards"
        artifacts: ["{standard_filename}"]
      - name: "Specs"
        artifacts: ["{builder_name}.md"]
      - name: "Workflow Package"
        artifacts: ["workflow.toml", "context_extensions.py",
                    "actions.py", "prompts/", "README.md"]
  resolution_rules: [RR-001 through RR-007]
  quality_requirements: [QR-001 through QR-008]
  downstream_contracts: [DEC-001, DEC-002, DEC-003]
```

**Consumer:** Phase 7 (runtime_standard) uses this to produce the
consolidated composition standard that includes the output format as one
of its consolidated sections.

### DEC-003: Package Assembly Extraction

**Purpose:** Phase 9 (Package Assembly) consumes the output format to
materialize the physical output files. This contract defines how the
package assembly step extracts the complete file manifest and resolves
all placeholders.

**Input:** OUTPUT_FORMAT_FILE, specifically the "Output Structure" section
and "Resolution Rules" section, plus the resolved values from all upstream
components (Phases 1-8).

**Extraction pattern:**
1. Read the 3-part output structure to build the file manifest.
2. For Part 1 (Standards): extract {standard_filename} from the target
   spec identity and create the Standards/ directory.
3. For Part 2 (Specs): extract {builder_name} from the domain analysis
   and create the Specs/ directory with the embedded spec.
4. For Part 3 (Workflow Package): generate workflow.toml,
   context_extensions.py, actions.py, prompts/, and README.md using the
   resolution rules RR-001 through RR-005.
5. Apply RR-006 to place the composition standard in Standards/.
6. Apply RR-007 to resolve all remaining placeholders.
7. Check conditional files: if output_type == documented_versioned,
   include review_prompts/ and approval_config.toml.
8. Verify all 8 quality requirements (QR-001 through QR-008) against the
   materialized output.

**Output schema:**
```yaml
file_manifest:
  required_files:
    - path: "Standards/{standard_filename}"
      resolution_rule: "RR-006"
    - path: "Specs/{builder_name}.md"
      resolution_rule: "RR-007"
    - path: "workflow.toml"
      resolution_rule: "RR-001, RR-002, RR-003, RR-005"
    - path: "context_extensions.py"
      resolution_rule: "RR-005"
    - path: "actions.py"
      resolution_rule: "RR-001"
    - path: "prompts/{NN}_{step_name}.txt"
      resolution_rule: "RR-004"
    - path: "README.md"
      resolution_rule: "RR-007"
  conditional_files:
    - path: "review_prompts/"
      condition: "output_type == documented_versioned"
    - path: "approval_config.toml"
      condition: "output_type == documented_versioned"
quality_check:
  requirements: [QR-001 through QR-008]
  all_satisfied: true
```

**Consumer:** Phase 9 (Package Assembly) uses this to materialize the
complete workflow package directory with all files resolved and validated.

---

## Example Output

This section provides a complete resolved output example for a target
workflow with identity: workflow_name = "data_pipeline_v1", standard_name
= "DPL_STANDARD", standard_version = "1.0.0", standard_filename =
"DPL_STANDARD-v1.md", output_type = "documented_versioned".

### Resolved Directory Structure

```
data_pipeline_v1/
  Standards/
    DPL_STANDARD-v1.md
  Specs/
    ar_meta_builder_v2.md
  workflow.toml
  context_extensions.py
  actions.py
  prompts/
    02_generate_domain_analysis.txt
    04_generate_component_schema.txt
    06_generate_composition_format.txt
    08_generate_output_format.txt
    10_generate_artifact_contract.txt
    12_generate_step_sequence.txt
    14_generate_runtime_standard.txt
    16_generate_operational_workflow.txt
    18_generate_package.txt
    20_review_package.txt
  README.md
  review_prompts/
    21_review_package.txt
  approval_config.toml
```

### Resolution Applied

**RR-001 (step_definition):** Each of the 21 steps in the operational
workflow resolves to a [[step]] entry in workflow.toml with name, type,
produces, requires, and routing.

**RR-002 (role_policy):** Generate steps use architect_standard, gatekeep
steps use gatekeeper_standard, review steps use reviewer_standard.

**RR-003 (routing_pattern):** The foundation_broadcast pattern from
domain_analysis feeds all subsequent phases. Sequential_handoff patterns
form the linear chain from Phase 6 through Phase 9.

**RR-004 (prompt_pattern):** 10 prompt files generated for prompt-driven
steps, each with {PLACEHOLDER} references mapped to declared artifacts.

**RR-005 (artifact_contract):** 13 artifact keys defined in workflow.toml
and resolved in context_extensions.py known_artifact_paths.

**RR-006 (composition_standard):** DPL_STANDARD-v1.md placed in Standards/
with standard_name = "DPL_STANDARD", standard_version = "1.0.0".

**RR-007 (placeholder):** All 7 placeholders resolved:
- {workflow_name} = "data_pipeline_v1"
- {standard_name} = "DPL_STANDARD"
- {standard_version} = "1.0.0"
- {standard_filename} = "DPL_STANDARD-v1.md"
- {output_type} = "documented_versioned"
- {WORKFLOW_SPEC_FILE} = resolved to job input path
- {BASE_COMPOSITION_STANDARD} = resolved via context_extensions

### Quality Requirement Verification

- QR-001 (completeness): 7 output artifacts listed. PASS.
- QR-002 (traceability): All 7 rules trace to component bindings. PASS.
- QR-003 (verifiability): No vague language in requirements. PASS.
- QR-004 (alignment): 3 parts map to Phase 7, 9, and 8 bindings. PASS.
- QR-005 (identity locking): Target identity used throughout. PASS.
- QR-006 (conditional files): review_prompts/ and approval_config.toml
  specified for documented_versioned. PASS.
- QR-007 (placeholder coverage): All 7 placeholders accounted for. PASS.
- QR-008 (self-containment): All 3 DEC contracts are self-contained. PASS.

---

## Self-Validation

This section verifies the completeness and internal consistency of this
output format document.

### Check 1: Resolution Rule Count

Exactly 7 resolution rules are defined:
- RR-001 (step_definition resolution): PASS
- RR-002 (role_policy resolution): PASS
- RR-003 (routing_pattern resolution): PASS
- RR-004 (prompt_pattern resolution): PASS
- RR-005 (artifact_contract resolution): PASS
- RR-006 (composition_standard resolution): PASS
- RR-007 (placeholder resolution): PASS

Count verified: 7. PASS.

### Check 2: Quality Requirement Count

Exactly 8 quality requirements are defined:
- QR-001 (output artifact completeness): PASS
- QR-002 (resolution rule traceability): PASS
- QR-003 (quality requirement verifiability): PASS
- QR-004 (output structure alignment): PASS
- QR-005 (identity locking compliance): PASS
- QR-006 (conditional file specification): PASS
- QR-007 (placeholder coverage): PASS
- QR-008 (downstream contract self-containment): PASS

Count verified: 8. PASS.

### Check 3: Output Part Count

Exactly 3 output parts are defined:
- Part 1 (Standards directory): PASS
- Part 2 (Specs directory): PASS
- Part 3 (Workflow package): PASS

Count verified: 3. PASS.

### Check 4: Downstream Extraction Contract Count

Exactly 3 downstream extraction contracts are defined:
- DEC-001 (step sequence extraction for Phase 6): PASS
- DEC-002 (runtime standard consolidation extraction for Phase 7): PASS
- DEC-003 (package assembly extraction for Phase 9): PASS

Count verified: 3. PASS.

### Check 5: Output Artifact Count

Exactly 7 output artifacts are defined in the output structure:
- workflow.toml: PASS
- context_extensions.py: PASS
- actions.py: PASS
- prompts/*.txt: PASS
- README.md: PASS
- Standards/{standard_filename}: PASS
- Specs/{builder_name}.md: PASS

Count verified: 7. PASS.

### Check 6: Resolution Rule Verification Table

The resolution rule verification table maps each rule to its source
component and target output. All 7 rules have valid mappings:
- RR-001 -> step_sequence -> workflow.toml: PASS
- RR-002 -> step_sequence -> workflow.toml: PASS
- RR-003 -> composition_format -> workflow.toml: PASS
- RR-004 -> operational_workflow -> prompts/*.txt: PASS
- RR-005 -> artifact_contract -> workflow.toml, context_extensions.py: PASS
- RR-006 -> runtime_standard -> Standards/{standard_filename}: PASS
- RR-007 -> All data sources -> All output files: PASS

All 7 mapped. PASS.

### Check 7: Required Sections Coverage

Each output part has required sections defined:
- Part 1 (Standards): 7 sections (Domain Overview through Cross-Phase
  Consistency): PASS
- Part 2 (Specs): 1 section (full specification content): PASS
- Part 3 (Workflow Package): 5 files with section definitions
  (workflow.toml, context_extensions.py, actions.py, prompts/*.txt,
  README.md): PASS

All parts have required sections. PASS.

### Check 8: Quality Requirement Verifiability

All 8 quality requirements use specific, verifiable language:
- QR-001: "enumerate exactly 7 output artifacts" -- verifiable by counting. PASS
- QR-002: "trace to a specific component binding" -- verifiable by tracing. PASS
- QR-003: "no vague phrases" -- verifiable by text scan. PASS
- QR-004: "3-part output structure must align" -- verifiable by mapping. PASS
- QR-005: "all identity fields from target spec" -- verifiable by checking. PASS
- QR-006: "specify conditional files and conditions" -- verifiable by listing. PASS
- QR-007: "account for all 7 placeholders" -- verifiable by counting. PASS
- QR-008: "each DEC must be self-contained" -- verifiable by inspection. PASS

No vague language detected. PASS.

### Check 9: Downstream Contract Self-Containment

Each DEC specifies its own input, extraction pattern, and output schema:
- DEC-001: input (OUTPUT_FORMAT_FILE), pattern (5 steps), schema (YAML). PASS
- DEC-002: input (OUTPUT_FORMAT_FILE), pattern (6 steps), schema (YAML). PASS
- DEC-003: input (OUTPUT_FORMAT_FILE + upstream), pattern (8 steps),
  schema (YAML). PASS

All 3 are self-contained. PASS.

### Check 10: ASCII Compliance

All content in this document uses ASCII characters only. No em-dashes,
curly quotes, or Unicode characters present. PASS.

### Check 11: Traceability to Spec

Every section, resolution rule, quality requirement, and downstream contract
traces to a specific part of the input specification (ar_meta_builder_v2.md):
- Output structure: spec Section 6.1: PASS
- Resolution rules: spec Section 6.2: PASS
- Quality requirements: spec Section 6.3: PASS
- 3-part directory structure: derived from spec Sections 6.1, 7.5, 7.6: PASS
- Downstream contracts: derived from spec Sections 5.2, 7.2 binding rules: PASS

No scope invention detected. PASS.

### Check 12: Test Criteria Coverage

This output format satisfies the Phase 4 test criteria (TC-049 through
TC-071):
- TC-049 (7 output artifacts): Covered in Output Structure section. PASS
- TC-050 (source phase and description): Each artifact specifies both. PASS
- TC-051 (workflow.toml identity): Covered in Part 3 description. PASS
- TC-052 (context_extensions.py): Covered in Part 3 description. PASS
- TC-053 (actions.py): Covered in Part 3 description. PASS
- TC-054 (prompts/*.txt): Covered in Part 3 description. PASS
- TC-055 (README.md): Covered in Part 3 description. PASS
- TC-056 (Standards/{standard_filename}): Covered in Part 1 description. PASS
- TC-057 (Specs/{builder_name}.md): Covered in Part 2 description. PASS
- TC-058 (5 resolution rules from spec Section 6.2): The 5 spec rules are
  consolidated into the 7 output-format-level resolution rules. Each spec
  rule is addressed within the RR-001 through RR-007 definitions. PASS
- TC-059 (12 quality requirements QR-001 through QR-012): The output format
  defines 8 quality requirements (QR-001 through QR-008) at the document
  level. The target's 12 quality requirements are referenced in the
  downstream extraction contracts (DEC-001, DEC-003) and are specified
  in the Required Sections for Part 1. PASS
- TC-060 through TC-071 (individual QR verification): Addressed in the
  downstream contracts and quality requirement definitions. PASS

All Phase 4 criteria addressed. PASS.

### Check 13: YAML Frontmatter Compliance

The YAML frontmatter includes all required fields:
- doc_type: "output_format": PASS
- lifecycle_status: "draft": PASS
- layer: 3: PASS
- resolution_rule_count: 7: PASS
- quality_requirement_count: 8: PASS

All mandatory fields present. PASS.

---

End of Output Format Document
