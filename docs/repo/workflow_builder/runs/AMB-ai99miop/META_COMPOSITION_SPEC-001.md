---
doc_type: "meta_composition_spec"
lifecycle_status: "draft"
domain: "codebase_to_meta"
self_bootstrap_capable: true
component_type_count: 8
binding_rule_count: 3
resolution_rule_count: 7
quality_requirement_count: 7
phase_count: 5
step_count: 5
artifact_count: 5
audience_count: 3
spec_reference: "codebase_to_meta_v1.md"
standard_name: "AR_META_BUILDER_STANDARD"
standard_version: "1.0.0"
---

# Meta Composition Spec: Codebase to Meta Content v1

## Overview

This document is a self-contained meta composition specification for the
codebase_to_meta domain. It consolidates the 3-layer composition system
(Component Schema, Composition Format, Output Format) and the operational
workflow into a single reference document. A downstream workflow or
generated meta builder can use this single document as input to understand
the complete domain definition without needing to reference the original
bootstrap specification or upstream layered artifacts.

**Domain:** codebase_to_meta
**Standard:** AR_META_BUILDER_STANDARD v1.0.0
**Workflow pattern:** mixed (action steps + prompt-driven steps)
**Self-bootstrap capable:** true

**Traceability:** All content in this document traces to the input
specification (codebase_to_meta_v1.md, Sections 1 through 5) and the
upstream layered artifacts (COMPONENT_SCHEMA.md, COMPOSITION_FORMAT.md,
OUTPUT_FORMAT.md, OPERATIONAL_WORKFLOW.md, COMPOSITION_STANDARD.md).

---

## Domain Overview

**Domain name:** codebase_to_meta

**Label:** Codebase to Meta Content v1

**Job prefix:** META

**Workflow pattern:** mixed (action steps for scanning and publishing,
prompt-driven steps for content generation and review)

**Description:** Transforms codebase documentation into audience-specific
Rich Markdown meta content files via plugin-extensible audience definitions.

### Purpose

The codebase documentation under docs/repo/codebase/current/ contains
approximately 155 files of technical documentation (module docs, component
docs, standards, inventory, change records). This information is
comprehensive but written for a single audience.

Different stakeholders need different views of the same codebase:

- **Developers** need implementation details, APIs, dependencies, setup
  guides, code patterns, extension points, testing guidance.
- **Architects** need design decisions and rationale, pattern analysis,
  component relationships, dependency graphs, technical debt assessment.
- **Executives** need high-level project overview, key metrics (module
  count, test coverage, workflow count), risk summary, progress status.

This composition system scans the codebase docs and produces one Rich
Markdown meta content file per audience. The set of audiences is
plugin-extensible: each audience is defined by a Markdown file with YAML
frontmatter in the workflow's audiences/ directory. Adding a new audience
requires only dropping a new .md file into audiences/. No workflow logic
changes.

**Trigger:** User runs the workflow. No user-provided input artifacts.
All paths are resolved from the repo structure at runtime.

**Outcome:** A set of audience-specific meta content Markdown files
published to docs/repo/meta_content/current/ with full version history.
Each file is self-contained and readable without reference to the source
codebase docs.

### Audience-Based Output Model

The domain produces one output file per discovered audience. The audience
set is dynamically discovered at runtime from the audiences/ directory.
The initial audience set consists of 3 files:

| Audience File | audience_id | Focus |
|---|---|---|
| developer.md | developer | Implementation: APIs, dependencies, setup, patterns, extensions |
| architect.md | architect | Design: decisions, patterns, relationships, dependency graphs, tech debt |
| executive.md | executive | Business: overview, metrics, risk, progress, cost indicators |

Each audience is defined by a Markdown file with YAML frontmatter
containing 6 fields: audience_id, label, tone, focus_areas, exclude
(optional), section_structure. The audience_id becomes the output
subdirectory name and determines the AUD code in the output filename.

### Context Variables

All paths are hardcoded in context_extensions.py. No user-provided
input artifacts.

| Context Variable | Hardcoded Path | Description |
|---|---|---|
| CODEBASE_DOC_ROOT | {repo_root}/docs/repo/codebase/current/ | Source codebase documentation |
| META_CONTENT_ROOT | {repo_root}/docs/repo/meta_content/ | Output staging/publish root |
| AUDIENCE_DIR | {workflow_package}/audiences/ | Audience definition plugins |

### Domain Flow

```
codebase docs --> [codebase_to_meta_v1] --> meta content (per audience)
                                                  |
                                  [meta_content_renderer_v1]
                                                  |
                                    HTML / PDF / DOCX / PPTX
```

---

## Component Schema

This section defines the 8 universal component types that form the
building block library for the codebase_to_meta domain. The domain uses
5 of these 8 types as domain-active components. The remaining 3 types
are part of the universal library and are consumed at later phases.

### Common Properties

Every component instance shares the following common properties:

| Property | Type | Required | Description |
|---|---|---|---|
| component_id | string | Yes | Unique identifier. Format: {TYPE_PREFIX}-{NNN} |
| component_type | string | Yes | Must be one of the 8 defined type names |
| name | string | Yes | Human-readable name for display and documentation |
| version | string | Yes | Semantic version (e.g., "1.0.0") |
| description | string | Yes | Purpose and scope of this component instance |

### Type 1: step_definition

**Purpose:** Defines a single executable step within the workflow. Each
step represents a discrete unit of work: either a deterministic action
(Python code) or a prompt-driven LLM invocation.

**Cardinality:** One or more (1..N). The codebase_to_meta domain defines
exactly 5 steps.

**Required type-specific properties:**

| Property | Type | Description |
|---|---|---|
| step_name | string | Unique step identifier within the workflow |
| step_type | string | Either "prompt" (LLM-driven) or "action" (deterministic Python) |
| purpose | string | Human-readable description of what this step accomplishes |
| produces | array | List of artifact keys produced by this step |

**Domain instances (5):**

| step_name | step_type | Phase | Purpose |
|---|---|---|---|
| scan_audiences | action | Scan | Discover audience definitions from audiences/ directory |
| generate_meta_content | prompt | Generate | Produce one meta content file per discovered audience |
| review_meta_content | prompt | Review | Quality review of all generated meta files |
| refine_meta_content | prompt | Refine | Fix issues found in review (conditional) |
| publish_meta_content | action | Publish | Backup, history, copy to current/ with manifest |

**Validation rules:**
- step_name must be unique within the workflow.
- step_type must be either "prompt" or "action".
- produces must contain at least one artifact key for action steps.
- If step_type is "action", no role_policy reference is needed.
- If step_type is "prompt", a role_policy must reference this step.

### Type 2: role_policy

**Purpose:** Assigns a coder role (policy) to a prompt-type step.
Determines which LLM persona and constraints are applied. Action steps
do not have role assignments.

**Cardinality:** Zero or more (0..N). One role_policy per prompt-type step.

**Required type-specific properties:**

| Property | Type | Description |
|---|---|---|
| step_name | string | The step this role policy applies to |
| policy_name | string | The role/policy identifier (e.g., "architect_standard") |

**Domain instances (3):**

| step_name | policy_name | Rationale |
|---|---|---|
| generate_meta_content | architect_standard | Content generation from structured source |
| review_meta_content | reviewer_standard | Quality review against constraints |
| refine_meta_content | architect_standard | Content regeneration addressing review |

**Validation rules:**
- step_name must reference an existing step_definition.
- policy_name must not be assigned to action-type steps.
- Each prompt-type step must have exactly one role_policy.
- Action-type steps must not have a role_policy entry.

### Type 3: routing_pattern

**Purpose:** Defines the control flow between steps. Specifies onsuccess
and optional on_reject_refine targets. Supports iteration limits and
exhaustion codes.

**Cardinality:** One per step (1..1 per step). Total count matches step
count.

**Required type-specific properties:**

| Property | Type | Description |
|---|---|---|
| step_name | string | The source step for this routing rule |
| onsuccess | string | Target step on successful completion |

**Optional type-specific properties:**

| Property | Type | Description |
|---|---|---|
| on_reject_refine | string | Target step on rejection/refinement request |
| max_iterations | integer | Maximum reject-refine loop iterations |
| exhaustion_code | string | Code emitted when max_iterations is reached |
| exhaustion_classification | string | Classification of exhaustion event |

**Domain instances (5):**

| step_name | onsuccess | on_reject_refine | Max iterations |
|---|---|---|---|
| scan_audiences | generate_meta_content | -- | -- |
| generate_meta_content | review_meta_content | -- | -- |
| review_meta_content | publish_meta_content | refine_meta_content | 2 |
| refine_meta_content | review_meta_content | -- | -- |
| publish_meta_content | step_completion | -- | -- |

**Exhaustion code for review_meta_content:** META_CONTENT_REVIEW_EXHAUSTED,
classification HUMAN_RETRY_REQUIRED.

**Validation rules:**
- step_name must reference an existing step_definition.
- onsuccess must reference an existing step_definition or "step_completion".
- Exactly one step must route to "step_completion".
- Routing must not create unresolvable cycles.
- max_iterations must be specified if on_reject_refine is present.

### Type 4: prompt_pattern

**Purpose:** Defines reusable sections assembled into prompt templates
for prompt-type steps. Each pattern represents a structural block within
a prompt.

**Cardinality:** One or more per prompt-type step (1..N). The domain
defines 6 patterns.

**Required type-specific properties:**

| Property | Type | Description |
|---|---|---|
| pattern_name | string | Identifier for this prompt pattern |
| applied_to | array | List of step_names this pattern applies to |
| content_description | string | Description of what this pattern contributes |

**Domain instances (6):**

| pattern_name | applied_to | Description |
|---|---|---|
| reference_inputs | generate, review, refine | List input artifacts with placeholder paths |
| generation_tasks | generate, refine | Specific content generation instructions per audience |
| self_critic | generate, review, refine | Challenge reasoning, verify audience alignment |
| self_validation | generate, review, refine | Check completeness, attribution, no hallucination |
| forbidden_content | generate, refine | No hallucination, no information beyond source docs |
| output_instructions | generate, review, refine | File path, YAML frontmatter format, ASCII-only |

**Validation rules:**
- pattern_name must be unique within the schema.
- applied_to must reference existing prompt-type step_definitions.
- Every prompt-type step must have at least reference_inputs, self_critic,
  self_validation, and output_instructions patterns applied.
- Generate and refine steps must also include generation_tasks and
  forbidden_content.

### Type 5: artifact_contract

**Purpose:** Defines a named output artifact produced by the workflow.
Specifies the artifact key, filename pattern, producing step, and
whether it is required.

**Cardinality:** One or more (1..N). The domain defines 5 artifacts.

**Required type-specific properties:**

| Property | Type | Description |
|---|---|---|
| artifact_key | string | Unique key identifying this artifact |
| filename_pattern | string | Pattern for the output filename |
| produced_by | string | The step_name that produces this artifact |
| required | boolean | Whether this artifact must be produced for success |

**Domain instances (5):**

| artifact_key | filename_pattern | produced_by | Required |
|---|---|---|---|
| AUDIENCE_INVENTORY_FILE | AUDIENCE_INV-{date}-{seq}_{slug}.md | scan_audiences | Yes |
| META_CONTENT_FILE | {audience_id}/META-{AUD}-{date}-{seq}.md | generate_meta_content | Yes |
| META_INDEX_FILE | meta_index.json | generate_meta_content | Yes |
| REVIEW_FILE_SUGGESTED | META-REV-{date}-{seq}_{slug}.md | review_meta_content | Yes |
| META_MANIFEST_FILE | meta_manifest.json | publish_meta_content | Yes |

**Validation rules:**
- artifact_key must be unique across the entire schema.
- produced_by must reference an existing step_definition.
- filename_pattern must not contain filesystem-incompatible characters.
- Every step_definition produces array must reference valid artifact_keys.
- Required artifacts must be produced by a step that always executes.

### Type 6: composition_standard

**Purpose:** Defines a reusable composition standard that governs how
component types are assembled into workflow packages.

**Cardinality:** Zero or more (0..N).

**Domain status:** Part of the universal component library. Not
instantiated at the Layer 1 component schema level for this domain.
Consumed at Phase 6 (composition standard generation).

**Required properties:** standard_name, standard_version,
component_type_count.

### Type 7: output_variance

**Purpose:** Defines variations in output format that a domain may
produce. Captures resolution rules, quality requirements, and format
constraints.

**Cardinality:** Zero or more (0..N).

**Domain status:** Part of the universal component library. Not
instantiated at Layer 1. Output format details captured at Phase 4.

**Required properties:** variance_name.

### Type 8: domain_spec

**Purpose:** Captures domain-level metadata and context that applies
across all components. Includes domain name, label, job prefix, workflow
pattern, and contextual variables.

**Cardinality:** Zero or one (0..1) per domain.

**Domain status:** Part of the universal component library. Not
instantiated at Layer 1. Domain metadata captured in workflow spec
frontmatter.

**Required properties:** domain_name, domain_label, job_prefix,
workflow_pattern.

### Validation Rules (Global)

| Rule ID | Rule Name | Severity | Description |
|---|---|---|---|
| VR-001 | Audiences directory exists | CRITICAL | audiences/ must exist with at least one .md file |
| VR-002 | Frontmatter validity | CRITICAL | Each audience .md must have valid YAML frontmatter with all required fields |
| VR-003 | Unique audience_id | CRITICAL | No two audience definitions may share the same audience_id |
| VR-004 | Codebase manifest exists | CRITICAL | CODEBASE_DOC_ROOT/codebase_manifest.json must exist |
| VR-005 | No hallucination | CRITICAL | No information invented beyond what codebase docs provide |
| VR-006 | Component ID uniqueness | CRITICAL | Every component_id must be unique within the schema |
| VR-007 | Step name uniqueness | CRITICAL | Every step_name must be unique within the workflow |
| VR-008 | Routing completeness | CRITICAL | Every step has one routing_pattern; exactly one routes to step_completion |
| VR-009 | Self-contained output | HIGH | Each meta content file readable without source docs |
| VR-010 | Source attribution | HIGH | Every factual claim traces to a specific codebase doc file |
| VR-011 | Audience fidelity | HIGH | Tone, focus, and section structure match audience definition |
| VR-012 | YAML frontmatter on output | HIGH | Each meta file has required frontmatter fields |
| VR-013 | Artifact key coverage | HIGH | Every artifact_key in produces has a corresponding artifact_contract |
| VR-014 | Role-step consistency | HIGH | Every prompt step has one role_policy; action steps have none |

---

## Composition Format

This section defines how component instances from the Component Schema
are bound together into compositions that drive workflow execution.

### Binding Rules

The composition defines 3 input data bindings that describe how external
data sources are bound at runtime.

| Binding Name | Source | Cardinality | Required |
|---|---|---|---|
| codebase_docs | Codebase documentation files (~155 .md files under CODEBASE_DOC_ROOT) | Ordered set | Yes |
| codebase_manifest | codebase_manifest.json at CODEBASE_DOC_ROOT | Singleton | Yes |
| audience_defs | Audience plugin .md files from audiences/ | Unordered set | Yes |

**Binding constraints:**
- step_bindings order must be consistent with routing_bindings.
- Each prompt-type step must have exactly one role_policy.
- Action-type steps must NOT have a role_policy entry.
- Every step must have exactly one routing_pattern.
- Every artifact_key must be unique across the composition.
- produced_by must reference an existing step in step_bindings.

### Component Type Bindings

The composition also defines bindings for all 8 component types:

| Binding Rule | Component Type | Cardinality | Required | Pattern |
|---|---|---|---|---|
| step_bindings | step_definition | 1..N | Yes | Ordered list |
| role_bindings | role_policy | 0..N | Conditional | Unordered set |
| routing_bindings | routing_pattern | 1 per step | Yes | Ordered list |
| prompt_bindings | prompt_pattern | 1..N per step | Conditional | Unordered set |
| artifact_bindings | artifact_contract | 1..N | Yes | Unordered set |
| composition_standard_binding | composition_standard | 0..1 | No | Singleton |
| output_variances | output_variance | 0..N | No | Unordered set |
| domain_specs | domain_spec | 0..1 | Yes | Singleton |

### Override Mechanism

Per-audience customization is achieved through audience definition
frontmatter fields. These are NOT component-level overrides in the
traditional sense. They are audience-specific configuration parameters
that drive the LLM's content generation behavior.

| Override Field | Type | Required | Overrides |
|---|---|---|---|
| tone | string | Yes | Default writing style for this audience |
| focus_areas | array | Yes | Which codebase sections to emphasize |
| exclude | array | No | Which content to omit from output |
| section_structure | array | Yes | Output section order for this audience |

**Key distinction:** Traditional component overrides modify component
properties. Audience overrides modify the generation context. The
components themselves remain unchanged; only the input context varies
per audience.

**Non-overridable properties:** The following are set at the composition
level and cannot be overridden per audience: builder_name, builder_label,
job_prefix, workflow_pattern, step_bindings, routing_bindings,
artifact_bindings, domain_specs.

**Merge semantics:** When the generate_meta_content step processes a
single audience:
1. Start with the base content model from codebase documentation and
   codebase_manifest.
2. Apply the audience's focus_areas to select which sections to emphasize.
3. Apply the audience's exclude list to filter out omitted topics.
4. Apply the audience's tone to set the writing style.
5. Apply the audience's section_structure to order the output sections.

Each audience produces an independent output file. There is no
cross-audience merging.

### Placeholder Resolution

Placeholders in prompt templates and composition definitions are resolved
from 4 data sources in priority order. The first source that provides a
value wins.

| Priority | Data Source | Fields Provided | Description |
|---|---|---|---|
| 1 (highest) | Runtime context | CODEBASE_DOC_ROOT, META_CONTENT_ROOT, AUDIENCE_DIR | Hardcoded paths from context_extensions.py |
| 2 | Audience definition | audience_id, label, tone, focus_areas, section_structure | Per-audience frontmatter fields |
| 3 | Codebase manifest | doc_inventory, section_list, total_doc_count | Metadata from codebase_manifest.json |
| 4 (lowest) | Job runtime | job_id, seq, workspace_root | Execution-time values from job runner |

**Unresolved placeholder handling:**
- Artifact key placeholders ({ARTIFACT_KEY}) must be declared in the
  step's required_inputs or produces.
- Context variable placeholder failures are a CRITICAL error.
- Audience field placeholder failures indicate missing required
  frontmatter.
- Job runtime placeholder failures indicate runner configuration errors.

### Composition Principle

There are no user-provided input artifacts. All paths are resolved from
the repo structure at runtime via context variables. The composition
binds codebase docs with audience definitions and produces per-audience
output.

### Input/Output Structure

```
Input:
  CODEBASE_DOC_ROOT/
  |-- codebase_manifest.json
  |-- standards/
  |-- modules/
  +-- inventory/

  audiences/
  |-- developer.md
  |-- architect.md
  +-- executive.md

Output:
  docs/repo/meta_content/current/
  |-- developer/
  |   +-- META-DEV-{date}-{seq}.md
  |-- architect/
  |   +-- META-ARCH-{date}-{seq}.md
  |-- executive/
  |   +-- META-EXEC-{date}-{seq}.md
  +-- meta_manifest.json
```

---

## Output Format

This section defines the concrete output structure, resolution rules,
and quality requirements for generated meta content files.

### YAML Frontmatter Schema

Each meta content file uses Rich Markdown with YAML frontmatter:

| Field | Type | Description |
|---|---|---|
| title | string | Human-readable document title |
| audience | string | Machine-readable audience identifier |
| audience_label | string | Human-readable audience name |
| generated_date | string | Date of generation (YYYY-MM-DD) |
| source_version | string | Version identifier of the source codebase |
| section_count | integer | Number of sections in the document |

### Resolution Rules

The following 7 resolution rules govern the structure of each generated
meta content file:

| Rule | Description | Verifiable Condition |
|---|---|---|
| RR-META-001 | Each audience produces exactly one meta content file | Count of outputs equals count of discovered audiences |
| RR-META-002 | Filename uses audience_id prefix: META-{AUD}-{date}-{seq}.md | AUD derived from audience_id (DEV, ARCH, EXEC) |
| RR-META-003 | Output subdirectory matches audience_id | Parent directory equals audience_id value |
| RR-META-004 | Section order follows section_structure | Output sections appear in section_structure order |
| RR-META-005 | Tone follows tone field | Writing style matches audience tone value |
| RR-META-006 | Excluded topics must not appear | No content related to excluded topics in output |
| RR-META-007 | Source attribution via inline references | Every claim includes inline reference to source file |

### Quality Requirements

The following 7 quality requirements define constraints for each
generated meta content file:

| Rule | Requirement | Severity | Verifiable Condition |
|---|---|---|---|
| QR-META-001 | Completeness | CRITICAL | All codebase sections represented (filtered by focus_areas/exclude) |
| QR-META-002 | Audience fidelity | CRITICAL | Tone, focus, section structure match audience definition |
| QR-META-003 | Self-contained | HIGH | File readable without reference to source docs |
| QR-META-004 | Source attribution | HIGH | Every claim traces to a specific codebase doc file |
| QR-META-005 | No hallucination | CRITICAL | No information beyond what codebase docs provide |
| QR-META-006 | YAML frontmatter | HIGH | All required fields present with correct values |
| QR-META-007 | ASCII-only | HIGH | No em-dashes, no curly quotes, no Unicode characters |

### Meta Content File Format Example

```markdown
---
title: "Agent Runner V2 -- Developer Guide"
audience: developer
audience_label: "Developer"
generated_date: "2026-08-09"
source_version: "SDLC00CB-bgmxg5vi"
section_count: 5
---

# Agent Runner V2 -- Developer Guide

## Overview

The agent-runner-v2 is a Python 3.12+ daemon and CLI execution engine...
(Source: docs/repo/codebase/current/modules/agent_runner_v2.md)

## Module Catalog

### agent_runner_v2.run_agent
Entry point for the ukbe-run-agent CLI...
(Source: docs/repo/codebase/current/modules/run_agent.md)

## API Reference

[Detailed function signatures, parameters, return types]

## Dependency Map

[Module dependency relationships]

## Developer Guide

[Setup, contribution, testing instructions]
```

### Audience Definition Plugin Format

Each audience is defined by a Markdown file in the audiences/ directory
with YAML frontmatter:

| Field | Type | Required | Description |
|---|---|---|---|
| audience_id | string | Yes | Unique identifier, becomes output subdirectory name |
| label | string | Yes | Human-readable display name |
| tone | string | Yes | Writing style guidance for the LLM |
| focus_areas | array | Yes | What to emphasize from codebase docs |
| exclude | array | No | What to omit from output |
| section_structure | array | Yes | Expected output section order |

**Initial audience set (3 files):**

1. **developer.md** -- Implementation-focused: module APIs and signatures,
   dependency relationships, setup and contribution guides, code patterns
   and conventions, extension points.

2. **architect.md** -- Design-focused: design decisions and rationale,
   pattern analysis, component relationships, dependency graphs,
   technical debt assessment, architectural constraints.

3. **executive.md** -- Business-focused: project overview, key metrics
   (module count, test coverage, workflow count), risk summary,
   progress status, cost/effort indicators.

---

## Operational Requirements

This section defines the 5-phase operational workflow, step sequence,
action step definitions, and artifact declarations for the generated
codebase_to_meta workflow.

### Workflow Phases

The generated workflow has 5 phases with 5 steps:

| Phase | Step | Type | Purpose |
|---|---|---|---|
| Scan | scan_audiences | action | Discover audience definitions from audiences/ directory |
| Generate | generate_meta_content | prompt | Produce one meta content file per discovered audience |
| Review | review_meta_content | prompt | Quality review of all generated meta files |
| Refine | refine_meta_content | prompt | Fix issues found in review (conditional, max 2 iterations) |
| Publish | publish_meta_content | action | Backup, history, copy to current/ with manifest |

### Step Sequence and Routing

| step_name | step_type | onsuccess | on_reject_refine | Role |
|---|---|---|---|---|
| scan_audiences | action | generate_meta_content | -- | (action -- no role) |
| generate_meta_content | prompt | review_meta_content | -- | architect_standard |
| review_meta_content | prompt | publish_meta_content | refine_meta_content (max 2) | reviewer_standard |
| refine_meta_content | prompt | review_meta_content | -- | architect_standard |
| publish_meta_content | action | step_completion | -- | (action -- no role) |

**Exhaustion code:** review_meta_content has max 2 iterations. When
exhausted, emits META_CONTENT_REVIEW_EXHAUSTED with classification
HUMAN_RETRY_REQUIRED.

### Action Step: scan_audiences

Recursively scan AUDIENCE_DIR for .md files. Parse YAML frontmatter
from each file. Build an audience inventory with audience_id, label,
tone, focus_areas, exclude, section_structure, and file path.

Write the inventory to AUDIENCE_INVENTORY_FILE.

**Error handling:**
- If AUDIENCE_DIR does not exist or contains no .md files, return
  REJECTED with reject_code NO_AUDIENCES_FOUND.
- If a file has invalid YAML frontmatter, log a warning and skip it.
- If two files define the same audience_id, return REJECTED with
  reject_code DUPLICATE_AUDIENCE_ID.

**Returns:** APPROVED when at least one valid audience is found.

### Action Step: publish_meta_content

Execute the 4-stage publish lifecycle:

1. **Backup** -- If current/ exists and contains files, copy current/
   to backups/BACKUP-{timestamp}/.
2. **History** -- Move old current/ to history/{job_id}/.
3. **Publish** -- For each audience meta content file, copy to
   current/{audience_id}/.
4. **Manifest** -- Write current/meta_manifest.json listing all published
   files with audience_id, filename, generated_date, source_version.

**Returns:** APPROVED when all files are published and manifest written.

### Output Artifacts

| Artifact Key | Description | Produced By | Required |
|---|---|---|---|
| AUDIENCE_INVENTORY_FILE | Discovered audience definitions with metadata | scan_audiences | Yes |
| META_CONTENT_FILE | One Rich Markdown meta content file per audience | generate_meta_content | Yes |
| META_INDEX_FILE | JSON index of all generated meta files | generate_meta_content | Yes |
| REVIEW_FILE_SUGGESTED | Quality review of all generated meta files | review_meta_content | Yes |
| META_MANIFEST_FILE | Published manifest in current/ | publish_meta_content | Yes |

### Prompt Patterns per Step

The following table shows which prompt patterns apply to each prompt-type
step:

| Pattern | generate_meta_content | review_meta_content | refine_meta_content |
|---|---|---|---|
| reference_inputs | Yes | Yes | Yes |
| generation_tasks | Yes | No | Yes |
| self_critic | Yes | Yes | Yes |
| self_validation | Yes | Yes | Yes |
| forbidden_content | Yes | No | Yes |
| output_instructions | Yes | Yes | Yes |

### Domain-Specific Requirements

- The audiences/ directory is part of the workflow package and must be
  deployed to the global runner home at install time.
- The publish lifecycle follows the staging pattern: stage, review,
  refine, backup, history, publish.
- Output paths follow the standard staging pattern: current/, runs/,
  history/, backups/.
- The generate step reads codebase_manifest.json to understand the full
  doc inventory, then selectively reads docs from each section as guided
  by each audience's focus_areas.
- Each meta content file must be self-contained (readable without
  reference to source codebase docs).

### Package File Inventory

The generated workflow package must include:

| File/Directory | Description |
|---|---|
| workflow.toml | Workflow manifest with 5 steps, 5 artifacts, routing |
| context_extensions.py | Artifact key registration with hardcoded paths |
| actions.py | scan_audiences and publish_meta_content implementations |
| prompts/generate_meta_content.txt | Prompt template for generation |
| prompts/review_meta_content.txt | Prompt template for review |
| prompts/refine_meta_content.txt | Prompt template for refinement |
| audiences/developer.md | Developer audience definition |
| audiences/architect.md | Architect audience definition |
| audiences/executive.md | Executive audience definition |
| Specs/codebase_to_meta_v1.md | Runtime spec defining meta content contract |
| README.md | Human documentation |

### Extensibility Model

**Level 1: Adding new audience definitions.** Drop a new .md file into
audiences/. No workflow logic changes required. The scan_audiences action
discovers it automatically.

**Level 2: Adding new component types.** New types can be added to the
universal library provided they include all 5 common properties, do not
alter existing types, and are added as optional.

**Level 3: Domain adaptation.** Different domains may use different
subsets of the 8 universal types. The codebase_to_meta domain uses 5
of 8 types.

**Backward compatibility guarantee:** Any composition valid under
version N remains valid under version N+1, provided no required property
is removed, no optional property becomes required, and no validation
rule severity is increased.

---

## Self-Validation

This section verifies the completeness and internal consistency of this
meta composition spec.

### Section Coverage

| # | Section | Source | Complete |
|---|---|---|---|
| 1 | Domain Overview | Spec Section 1 | Yes |
| 2 | Component Schema | Spec Section 2 + COMPONENT_SCHEMA.md | Yes |
| 3 | Composition Format | Spec Section 3 + COMPOSITION_FORMAT.md | Yes |
| 4 | Output Format | Spec Section 4 + OUTPUT_FORMAT.md | Yes |
| 5 | Operational Requirements | Spec Section 5 + OPERATIONAL_WORKFLOW.md | Yes |

### Component Type Coverage

| # | Type | Domain Status | Instances | Defined |
|---|---|---|---|---|
| 1 | step_definition | Active | 5 | Yes |
| 2 | role_policy | Active | 3 | Yes |
| 3 | routing_pattern | Active | 5 | Yes |
| 4 | prompt_pattern | Active | 6 | Yes |
| 5 | artifact_contract | Active | 5 | Yes |
| 6 | composition_standard | Universal | 0 | Yes |
| 7 | output_variance | Universal | 0 | Yes |
| 8 | domain_spec | Universal | 0 | Yes |

### Phase and Step Coverage

| Phase | Step | Type | Routing | Artifacts | Defined |
|---|---|---|---|---|---|
| Scan | scan_audiences | action | -> generate_meta_content | AUDIENCE_INVENTORY_FILE | Yes |
| Generate | generate_meta_content | prompt | -> review_meta_content | META_CONTENT_FILE, META_INDEX_FILE | Yes |
| Review | review_meta_content | prompt | -> publish / refine (max 2) | REVIEW_FILE_SUGGESTED | Yes |
| Refine | refine_meta_content | prompt | -> review_meta_content | (revises META_CONTENT_FILE) | Yes |
| Publish | publish_meta_content | action | -> step_completion | META_MANIFEST_FILE | Yes |

### Verification Checklist

- [x] All 5 required sections present: Domain Overview, Component Schema,
      Composition Format, Output Format, Operational Requirements.
- [x] Section 1 includes domain name, label, job prefix, description,
      purpose, and audience-based output model.
- [x] Section 2 covers all 5 domain-active component types and 3 universal
      types with validation rules.
- [x] Section 3 covers binding rules, override mechanism, and placeholder
      resolution.
- [x] Section 4 covers YAML frontmatter schema, 7 resolution rules, and
      7 quality requirements.
- [x] Section 5 covers 5 phases, step sequence, action step definitions,
      audience definition plugin format, and artifact declarations.
- [x] Document is self-contained: a downstream consumer can understand the
      meta content format and audience structure from this document alone.
- [x] All content traces to the input specification (codebase_to_meta_v1.md).
      No scope invention.
- [x] ASCII-only content. No em-dashes, curly quotes, or Unicode characters.
- [x] Governance path references use filenames only, not filesystem paths.
- [x] YAML frontmatter includes all required fields including
      self_bootstrap_capable: true.

---

**End of Meta Composition Spec**
