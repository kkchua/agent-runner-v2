---
doc_type: "test_criteria"
lifecycle_status: "draft"
effective_version: "WFBUILD-kxpi9b6d"
workflow_spec: "codebase_to_meta_v1"
created_at: "2026-08-07T02:21:37+08:00"
created_by: "workflow_builder_v1 / generate_test_criteria"
---

# Test Criteria: codebase_to_meta_v1 Workflow

## 1. Spec Objective Summary

The codebase_to_meta_v1 workflow transforms approximately 155 technical codebase
documentation files (located under docs/repo/codebase/current/) into audience-
specific Rich Markdown meta content files. It reads a plugin-extensible set of
audience definitions from the workflow package's audiences/ directory, dynamically
scans the codebase documentation inventory, and generates one tailored meta content
file per audience (developer, architect, executive as the initial set). Each output
file is a self-contained Rich Markdown document with YAML frontmatter, organized
per the audience definition's section_structure. The workflow follows a staging,
review, refine, backup, history, and publish lifecycle pattern (identical to
sdlc_00_codebase_v1), publishing final output to docs/repo/meta_content/current/
with a manifest tracking all published meta files. There are no user-provided
inputs; all paths are resolved internally from the repo structure.

## 2. Criteria for analyze_spec step

### 2.1 Requirements Coverage

2.1.1 The requirements document MUST identify the workflow as a prompt-driven
pipeline with action-driven steps for file operations (backup, archive, publish).

2.1.2 The requirements document MUST identify ALL three initial audience types
explicitly named in the spec: developer, architect, executive.

2.1.3 The requirements document MUST identify the plugin-extensible audience
system: audiences are defined by Markdown files with YAML frontmatter in the
workflow package's audiences/ directory.

2.1.4 The requirements document MUST identify ALL six output artifacts from the
spec: META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX,
REVIEW_FILE_SUGGESTED, META_MANIFEST.

2.1.5 The requirements document MUST identify the staging directory pattern:
docs/repo/meta_content/ with subdirectories current/, runs/{job_id}/,
history/{job_id}/, and backups/.

2.1.6 The requirements document MUST identify the publish lifecycle stages:
Stage, Review, Refine, Backup, History, Publish.

2.1.7 The requirements document MUST capture the constraint that each meta
content file must be self-contained (readable without reference to source docs).

2.1.8 The requirements document MUST capture the constraint that the workflow
dynamically discovers audience definitions at startup by scanning audiences/
for .md files.

2.1.9 The requirements document MUST capture that each audience definition's
YAML frontmatter fields (audience_id, label, tone, focus_areas, exclude,
section_structure) drive the generation.

2.1.10 The requirements document MUST identify codebase_manifest.json as a key
input that the generate step reads to understand the full doc inventory.

2.1.11 The requirements document MUST capture that the workflow has NO
user-provided inputs -- all paths are resolved internally.

2.1.12 The requirements document MUST identify the initial audience set consists
of 3 files: developer.md, architect.md, executive.md in the audiences/ directory.

2.1.13 MUST NOT include scope that contradicts the spec (e.g., adding user
input parameters, changing the audience set, modifying the output directory
structure).

### 2.2 Inference Validation

2.2.1 INFERENCE: If the analyze step infers this workflow is primarily
prompt-driven (LLM generates content) with action support for deterministic
file operations, the inference MUST be justified by referencing: the spec's
statement "The generate step reads codebase_manifest.json... as guided by
each audience's focus_areas" (prompt-driven generation) and the spec's
publish lifecycle with backup/history/publish (action-driven file operations).

2.2.2 INFERENCE: If the analyze step proposes a step sequence, it MUST include
at minimum: (a) audience discovery/scanning, (b) per-audience content
generation, (c) index/manifest creation, (d) review step with human approval,
(e) refine loop, (f) backup action, (g) history action, (h) publish action,
(i) stepCompletion. Any alternative sequencing must be justified.

2.2.3 INFERENCE: If the analyze step infers custom actions for file operations
(backup, history, publish, audience scanning), each inferred action MUST be
justified as a deterministic operation. Justification must explain why it is
suitable for code implementation rather than LLM invocation.

2.2.4 INFERENCE: For each inferred action, the specification MUST include:
(a) purpose (what the action does), (b) inputs (what state/artifacts it reads),
(c) outputs (what artifacts it produces or modifies), (d) logic description
(step-by-step algorithmic behavior).

2.2.5 INFERENCE: If the analyze step infers that audiences/ must be deployed
to global runner home via install_to_global(), this inference MUST be justified
by referencing the spec constraint: "The audiences/ directory is part of the
workflow package and must be deployed to the global runner home via
install_to_global()."

2.2.6 INFERENCE: The analyze step MUST NOT miss the meta_manifest.json
structure as specified in the spec (workflow_id, change_or_run_id,
source_codebase_version, audiences object, published_timestamp, supersedes,
active_set).

### 2.3 Self-Validation

2.3.1 The requirements document MUST include a Self-Validation section that
explicitly checks each of the coverage items in 2.1.1 through 2.1.13.

2.3.2 The Self-Validation section MUST include a traceability table mapping
each spec objective to the requirement that covers it.

2.3.3 If the Self-Validation identifies any gaps, the document MUST report
REJECTED with specific gap descriptions rather than APPROVED with missing
elements.

2.3.4 The Self-Validation section MUST be placed BEFORE the final status
declaration (APPROVED/REJECTED) so the LLM checks before committing.

## 3. Criteria for gatekeep_requirements step

### 3.1 Completeness Verification

3.1.1 The gatekeeper report MUST verify that ALL three audience types
(developer, architect, executive) are covered in the requirements.

3.1.2 The gatekeeper report MUST verify that the plugin-extensible audience
system (dynamic scanning of audiences/ directory) is captured.

3.1.3 The gatekeeper report MUST verify that ALL six output artifacts are
identified (META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX,
REVIEW_FILE_SUGGESTED, META_MANIFEST).

3.1.4 The gatekeeper report MUST verify that the staging/publish directory
pattern is captured (current/, runs/, history/, backups/).

3.1.5 The gatekeeper report MUST verify that the publish lifecycle (Stage,
Review, Refine, Backup, History, Publish) is documented.

### 3.2 Approach Validity

3.2.1 The gatekeeper report MUST evaluate whether the inferred workflow type
(prompt-driven with action support) is appropriate for the spec's objectives
(content generation + file management).

3.2.2 The gatekeeper report MUST evaluate whether the proposed step sequence
is the most appropriate solution. Alternative orderings (e.g., generate all
audiences in one step vs. per-audience steps) must be assessed.

3.2.3 The gatekeeper report MUST verify that the inferred custom actions
(backup, history, publish, audience scanning) are justified and sound.

### 3.3 Downstream Feasibility

3.3.1 The gatekeeper report MUST verify that the requirements contain
sufficient detail for the define_artifacts step to create a complete
artifact contract.

3.3.2 The gatekeeper report MUST verify that the requirements contain
sufficient detail for the design_steps step to create a complete step
architecture.

3.3.3 The gatekeeper report MUST verify that action specifications include
enough detail (inputs, outputs, logic) for the generate_package step to
implement actions.py.

### 3.4 Constraint Satisfaction

3.4.1 The gatekeeper report MUST verify that the self-contained file
constraint is captured.

3.4.2 The gatekeeper report MUST verify that the no-user-input constraint
is captured.

3.4.3 The gatekeeper report MUST verify that the install_to_global()
deployment constraint for audiences/ is captured.

3.4.4 The gatekeeper report MUST verify that the standard staging pattern
constraint is respected.

### 3.5 Evidence and Verdict

3.5.1 The verdict (APPROVED or REJECTED) MUST be justified with specific
evidence referencing requirement IDs and spec sections, not generic
assertions like "looks good."

3.5.2 If REJECTED, the gatekeeper report MUST list specific gaps with
requirement IDs and what is missing.

3.5.3 If REJECTED, the gatekeeper report MUST include actionable fix
instructions for the analyze_spec step to address.

## 4. Criteria for define_artifacts step

### 4.1 Artifact Coverage

4.1.1 The artifact contract MUST define a path pattern for META_DEV_FILE
under docs/repo/meta_content/runs/{job_id}/developer/.

4.1.2 The artifact contract MUST define a path pattern for META_ARCH_FILE
under docs/repo/meta_content/runs/{job_id}/architect/.

4.1.3 The artifact contract MUST define a path pattern for META_EXEC_FILE
under docs/repo/meta_content/runs/{job_id}/executive/.

4.1.4 The artifact contract MUST define a path pattern for META_INDEX
under docs/repo/meta_content/runs/{job_id}/meta_index.json.

4.1.5 The artifact contract MUST define a path pattern for
REVIEW_FILE_SUGGESTED under docs/repo/meta_content/runs/{job_id}/.

4.1.6 The artifact contract MUST define a path pattern for META_MANIFEST
under docs/repo/meta_content/current/meta_manifest.json (publish target).

4.1.7 MUST NOT define path patterns for artifacts not declared in the
requirements (no scope creep).

### 4.2 WORKFLOW_ACTIONS Conditional

4.2.1 If the requirements declare action-driven steps (backup, history,
publish, audience scanning), the artifact contract MUST include the
WORKFLOW_ACTIONS artifact key.

4.2.2 WORKFLOW_ACTIONS path pattern MUST point to the actions.py file
within the workflow package directory.

### 4.3 Placeholder Validity

4.3.1 Path patterns MUST use {job_id} placeholder for per-job isolation,
not hardcoded job IDs.

4.3.2 Path patterns MUST use {seq} or sequence auto-increment for filenames
to prevent overwrites on re-runs.

4.3.3 Path patterns MUST use {slug} where audience-specific naming is needed
(e.g., META-DEV, META-ARCH, META-EXEC prefixes).

4.3.4 MUST NOT use absolute paths in the artifact contract. All paths must
be relative to the project root.

### 4.4 Self-Validation

4.4.1 The artifact contract document MUST include a Self-Validation section
that checks all artifacts from the requirements have corresponding path
patterns.

4.4.2 The Self-Validation MUST explicitly verify the WORKFLOW_ACTIONS
conditional requirement (is it present if action steps exist?).

4.4.3 The Self-Validation MUST verify no placeholder errors (e.g., no
literal "{job_id}" strings left unexpanded, correct placeholder syntax).

## 5. Criteria for gatekeep_artifacts step

### 5.1 Coverage Verification

5.1.1 The gatekeeper report MUST verify ALL artifacts from the requirements
have path patterns defined in the artifact contract.

5.1.2 The gatekeeper report MUST verify all six spec-named artifacts are
present (META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX,
REVIEW_FILE_SUGGESTED, META_MANIFEST).

5.1.3 The gatekeeper report MUST verify the REVIEW_FILE_SUGGESTED path
follows the standard pattern for review documents.

### 5.2 Action Artifacts

5.2.1 The gatekeeper report MUST verify WORKFLOW_ACTIONS is declared in
the artifact contract IF the requirements include action-driven steps.

5.2.2 The gatekeeper report MUST verify WORKFLOW_ACTIONS path pattern
points to a valid location within the workflow package.

### 5.3 Placeholder Completeness

5.3.1 The gatekeeper report MUST verify {job_id} is used in all run-scoped
paths.

5.3.2 The gatekeeper report MUST verify no hardcoded job IDs or dates
appear in path patterns.

5.3.3 The gatekeeper report MUST verify sequence placeholders are used
where re-runs could overwrite output.

### 5.4 Path Validity

5.4.1 The gatekeeper report MUST verify ALL path patterns are relative
(no leading drive letters or absolute paths).

5.4.2 The gatekeeper report MUST verify paths follow the standard
staging convention (docs/repo/meta_content/...).

### 5.5 Chain Integrity

5.5.1 The gatekeeper report MUST verify that input artifacts from the
spec (codebase_manifest.json, audience definition files) are accessible
to the workflow steps.

5.5.2 The gatekeeper report MUST verify that the artifact flow from
inputs through generation to publish is unbroken (no missing links).

5.5.3 The gatekeeper report MUST verify that META_MANIFEST path points
to the publish target (current/) while META_INDEX points to the staging
area (runs/).

## 6. Criteria for design_steps step

### 6.1 Coverage

6.1.1 The step architecture MUST include a step for dynamically scanning
and loading audience definitions from the audiences/ directory.

6.1.2 The step architecture MUST include generation steps for producing
meta content for each discovered audience (at minimum 3: developer,
architect, executive).

6.1.3 The step architecture MUST include a step for creating the meta_index.json
file tracking all generated meta files.

6.1.4 The step architecture MUST include a review step with human approval
gate (requires_human_approval_after = true).

6.1.5 The step architecture MUST include a refine step that loops back
to review after addressing feedback.

6.1.6 The step architecture MUST include a backup step that copies current/
to backups/BACKUP-{timestamp}/.

6.1.7 The step architecture MUST include a history step that moves old
current/ to history/{job_id}/.

6.1.8 The step architecture MUST include a publish step that copies
runs/{job_id}/ to current/ with updated manifest.

6.1.9 The step architecture MUST end with a stepCompletion terminal step.

### 6.2 Artifact Flow

6.2.1 The step architecture MUST allow tracing the complete chain from
inputs (codebase docs, audience definitions, codebase_manifest.json)
through each step to final outputs (meta content files, index, manifest).

6.2.2 Each step's required_inputs MUST be satisfied by prior steps'
produces or by workflow init inputs.

6.2.3 The audience discovery step MUST produce an artifact that downstream
generation steps consume.

6.2.4 MUST NOT have any step that declares required_inputs which no prior
step produces (dangling input references).

### 6.3 Routing Validity

6.3.1 Every step MUST have a valid onsuccess value that references an
existing step name in the architecture.

6.3.2 The terminal step (stepCompletion) MUST NOT have an onsuccess value.

6.3.3 The review step MUST route to promote/publish on success.

6.3.4 The review step MUST have an on_reject_refine block routing to the
refine step.

6.3.5 The refine step MUST have onsuccess routing back to the review step.

6.3.6 All on_reject_refine blocks MUST specify: step (target), artifact
(being refined), max_iterations (positive integer).

### 6.4 Step Type Appropriateness

6.4.1 Content generation steps (producing meta content for each audience)
MUST be classified as prompt-driven (LLM invocation).

6.4.2 File operation steps (backup, history, publish) MUST be classified
as action-driven (Python function).

6.4.3 Audience scanning/discovery SHOULD be classified as action-driven
(deterministic directory scan), not prompt-driven.

6.4.4 The review step MUST be classified as prompt-driven (LLM review
with human approval gate).

6.4.5 The refine step MUST be classified as prompt-driven (LLM revision).

### 6.5 Action Consistency

6.5.1 Action step names MUST match the action specifications from the
requirements document exactly.

6.5.2 Action step artifact declarations (produces, required_inputs) MUST
match the action specifications from the requirements.

### 6.6 Review Loop Design

6.6.1 The review/refine loop MUST use on_reject_refine (not onsuccess
back-edge) for rejection routing.

6.6.2 The on_reject_refine block MUST specify max_iterations (recommended: 2).

6.6.3 The refine step MUST use edit_mode = "in_place" and target_artifact
for the artifact being refined.

6.6.4 MUST NOT have infinite loops -- every loop must have a bounded
max_iterations.

### 6.7 Self-Validation

6.7.1 The step architecture document MUST include a Self-Validation section
that checks routing validity (all onsuccess values reference existing steps).

6.7.2 The Self-Validation MUST check artifact flow (every required_input
is satisfied by a prior produces or init input).

6.7.3 The Self-Validation MUST check that gatekeeper steps follow each
producer step (if the gatekeeper pattern is used).

6.7.4 If any check fails, the document MUST report REJECTED with specific
fixes before attempting to pass.

## 7. Criteria for gatekeep_steps step

### 7.1 Coverage Verification

7.1.1 The gatekeeper report MUST verify ALL requirements have
corresponding steps in the architecture.

7.1.2 The gatekeeper report MUST cross-reference each requirement ID
against step descriptions to confirm coverage.

7.1.3 The gatekeeper report MUST verify no requirement is orphaned
(has no implementing step).

### 7.2 Data Flow Verification

7.2.1 The gatekeeper report MUST verify that each step's required_inputs
are satisfied by prior steps' produces or workflow init inputs.

7.2.2 The gatekeeper report MUST trace the full data chain from
codebase_manifest.json through generation to published manifest.

7.2.3 The gatekeeper report MUST identify any dangling input references
(required_inputs that no step produces).

### 7.3 Routing Validity

7.3.1 The gatekeeper report MUST verify every onsuccess value references
an existing step name.

7.3.2 The gatekeeper report MUST verify the review/refine loop routing
is correct (review -> refine on reject, refine -> review on success).

7.3.3 The gatekeeper report MUST verify stepCompletion is the terminal
step with no onsuccess.

7.3.4 The gatekeeper report MUST verify no orphan steps exist (steps
that are never reached from init_step).

### 7.4 Type Consistency

7.4.1 The gatekeeper report MUST verify prompt-driven steps are assigned
to content generation, review, and refine tasks.

7.4.2 The gatekeeper report MUST verify action-driven steps are assigned
to deterministic file operations (backup, publish, etc.).

7.4.3 The gatekeeper report MUST flag any step where the type does not
match the task nature (e.g., an LLM prompt for a deterministic file copy).

### 7.5 Loop Validity

7.5.1 The gatekeeper report MUST verify all on_reject_refine blocks have
valid step, artifact, and max_iterations fields.

7.5.2 The gatekeeper report MUST verify the refine step's onsuccess
routes back to the review step.

7.5.3 The gatekeeper report MUST verify max_iterations is a positive
integer (not zero, not unbounded).

## 8. Criteria for generate_package step

### 8.1 Principles-Based Generation

8.1.1 The generate step MUST infer the required files from the step
architecture and artifact contract, not from a fixed numbered task list.

8.1.2 The generate step MUST produce a file ONLY if the design calls
for it (no unnecessary files).

8.1.3 The generate step MUST NOT omit a file that the design requires
(no missing files).

### 8.2 File Completeness

8.2.1 workflow.toml MUST exist and contain ALL steps from the step
architecture with correct names, types, routing, and artifact declarations.

8.2.2 context_extensions.py MUST exist and implement WorkflowExtensions
with correct workflow_name and register_artifact_keys.

8.2.3 prompts/ directory MUST contain one .txt file per prompt-driven
step in the architecture.

8.2.4 README.md MUST exist with step reference table and artifact key
listing.

8.2.5 audiences/ directory MUST exist with at least 3 files:
developer.md, architect.md, executive.md.

8.2.6 Each audience definition file MUST be Rich Markdown with YAML
frontmatter containing: audience_id, label, tone, focus_areas, exclude,
section_structure.

8.2.7 install.py MUST exist to deploy audiences/ to global runner home
via install_to_global().

8.2.8 .env.sample MUST exist only if the workflow requires environment
variables (e.g., if API keys are needed). MUST NOT exist if no env
vars are required.

8.2.9 config.json.sample MUST exist only if the workflow requires
runtime configuration. MUST NOT exist if no runtime config is needed.

### 8.3 workflow.toml Specifics

8.3.1 The [workflow] section MUST have name = "codebase_to_meta_v1".

8.3.2 The [workflow] section MUST have job_prefix = "META".

8.3.3 The [workflow] section MUST have init_step pointing to the first
step in the architecture.

8.3.4 Every [[step]] MUST have a name matching the step architecture.

8.3.5 Prompt-driven steps MUST have prompt field pointing to a file
in prompts/ (relative path).

8.3.6 Action-driven steps MUST have action field matching the
@action() decorator name in actions.py.

8.3.7 onsuccess MUST be at the [[step]] top level, NOT under
[step.artifacts].

8.3.8 promotes (if used) MUST be at the [[step]] top level.

8.3.9 Every workflow MUST end with a stepCompletion step using
action = "step_completion".

8.3.10 [step.on_reject_refine] blocks MUST have step, artifact, and
max_iterations fields.

### 8.4 context_extensions.py Specifics

8.4.1 The class MUST set workflow_name = "codebase_to_meta_v1" matching
the directory name.

8.4.2 register_artifact_keys() MUST return path mappings for ALL
artifacts declared in the artifact contract.

8.4.3 build_context_extensions() MUST resolve ALL artifact paths to
absolute paths using get_workspace_root().

8.4.4 MUST NOT return relative paths from build_context_extensions().

8.4.5 MUST import and use get_workspace_root() and/or get_runner_home()
from runtime_context.

8.4.6 MUST register BOTH input and output artifact keys.

### 8.5 actions.py Specifics (if applicable)

8.5.1 If action-driven steps exist in the architecture, actions.py
MUST exist with complete @action() implementations.

8.5.2 Each @action() function MUST have a name matching the action
field in workflow.toml.

8.5.3 Each action MUST contain actual implementation logic, not stubs
or placeholder comments.

8.5.4 Each action MUST return an ActionResult with appropriate status
(APPROVED or REJECTED) and remark.

8.5.5 Backup action MUST copy current/ to backups/BACKUP-{timestamp}/
(not move).

8.5.6 History action MUST move old current/ to history/{job_id}/.

8.5.7 Publish action MUST copy runs/{job_id}/ contents to current/
and update meta_manifest.json.

### 8.6 Prompt File Specifics

8.6.1 Each prompt file MUST use bare {ARTIFACT_KEY} placeholders
(backtick-free).

8.6.2 Each prompt file MUST use ASCII characters only.

8.6.3 Each prompt file MUST include an Objective section.

8.6.4 Each prompt file MUST include Reference Inputs section with
{ARTIFACT_KEY} placeholders.

8.6.5 Each prompt file MUST include Output Instructions specifying
format, encoding, and file naming.

8.6.6 Generation prompts MUST include Self-Validation section.

8.6.7 Review prompts MUST specify APPROVED/REJECTED verdict format.

### 8.7 README.md Specifics

8.7.1 README.md MUST include a step reference table listing all steps,
their types, and routing.

8.7.2 README.md MUST list all artifact keys with descriptions.

8.7.3 README.md MUST describe the audience plugin system (how to add
new audiences).

### 8.8 Self-Validation

8.8.1 The generate step output MUST include a Self-Validation section
that verifies all files implied by the step architecture are present.

8.8.2 The Self-Validation MUST cross-check workflow.toml steps against
actual files produced.

8.8.3 The Self-Validation MUST verify actions.py exists and contains
implementations for all action-driven steps.

8.8.4 The Self-Validation MUST verify prompt files exist for all
prompt-driven steps.

8.8.5 If any file is missing, the Self-Validation MUST report the gap
and generate the missing file before declaring APPROVED.

## 9. Criteria for gatekeep_package step

### 9.1 File Checklist

9.1.1 The gatekeeper report MUST verify workflow.toml exists and is
valid TOML.

9.1.2 The gatekeeper report MUST verify context_extensions.py exists
and is valid Python.

9.1.3 The gatekeeper report MUST verify README.md exists.

9.1.4 The gatekeeper report MUST verify all prompt files referenced
in workflow.toml exist in prompts/.

9.1.5 The gatekeeper report MUST verify actions.py exists if any
action-driven steps are declared in workflow.toml.

9.1.6 The gatekeeper report MUST verify audiences/ directory exists
with developer.md, architect.md, executive.md.

9.1.7 The gatekeeper report MUST verify install.py exists (required
for audiences/ deployment).

### 9.2 Action Completeness

9.2.1 The gatekeeper report MUST verify actions.py contains @action()
decorators matching every action step in workflow.toml.

9.2.2 The gatekeeper report MUST verify each action function contains
actual implementation logic (not stubs, not "pass" placeholders, not
comments-only).

9.2.3 The gatekeeper report MUST verify each action returns
ActionResult with status and remark.

### 9.3 Design Fidelity

9.3.1 The gatekeeper report MUST verify workflow.toml step names
match the step architecture document exactly.

9.3.2 The gatekeeper report MUST verify workflow.toml routing
(onsuccess values) matches the step architecture.

9.3.3 The gatekeeper report MUST verify workflow.toml artifact
declarations (produces, required_inputs) match the artifact contract.

9.3.4 The gatekeeper report MUST verify context_extensions.py
register_artifact_keys() includes all artifact keys from the contract.

### 9.4 Prompt Completeness

9.4.1 The gatekeeper report MUST verify prompts/ directory has exactly
one file per prompt-driven step in the architecture.

9.4.2 The gatekeeper report MUST verify no extra prompt files exist
(prompt files without corresponding steps in workflow.toml).

9.4.3 The gatekeeper report MUST verify each prompt file uses bare
placeholders (no backtick-wrapped {ARTIFACT_KEY}).

### 9.5 Scope Check

9.5.1 The gatekeeper report MUST detect scope shrink -- elements from
the step architecture that are missing in the generated package.

9.5.2 The gatekeeper report MUST detect scope creep -- elements in the
generated package that are not in the step architecture or artifact
contract.

9.5.3 The gatekeeper report MUST flag audience files that do not match
the spec's frontmatter field requirements (audience_id, label, tone,
focus_areas, exclude, section_structure).

## 10. Criteria for validate_bundle step

### 10.1 Structural Checks

10.1.1 The validate_bundle action MUST verify workflow.toml is valid
TOML (parseable without errors).

10.1.2 The validate_bundle action MUST verify all routing references
in workflow.toml resolve to existing step names.

10.1.3 The validate_bundle action MUST verify all artifact keys in
workflow.toml are registered in context_extensions.py.

10.1.4 The validate_bundle action MUST verify the workflow name in
workflow.toml matches the directory name and workflow_name attribute
in context_extensions.py.

10.1.5 The validate_bundle action MUST verify init_step references
an existing step name.

10.1.6 The validate_bundle action MUST verify stepCompletion is the
last step.

### 10.2 Semantic Checks

10.2.1 The validate_bundle action MUST verify actions.py (if present)
contains @action() functions matching all action steps.

10.2.2 The validate_bundle action MUST verify each action function
contains actual logic (not stubs).

10.2.3 The validate_bundle action MUST verify prompt files referenced
in workflow.toml exist and are non-empty.

10.2.4 The validate_bundle action MUST verify audience definition
files have valid YAML frontmatter with all required fields.

### 10.3 File Completeness

10.3.1 The validate_bundle action MUST verify all required files are
present: workflow.toml, context_extensions.py, README.md.

10.3.2 The validate_bundle action MUST verify no unexpected extra
files exist in the package directory.

10.3.3 The validate_bundle action MUST verify audiences/ directory
contains the expected audience definition files.

### 10.4 Validation Report

10.4.1 The validation report MUST list each check performed with
pass/fail status.

10.4.2 The validation report MUST include specific error messages
for any failed checks (file path, line number, what was expected).

10.4.3 The validation report MUST conclude with an overall verdict
(APPROVED if all checks pass, REJECTED if any check fails).

## 11. Criteria for review_package step

### 11.1 Spec Fulfillment

11.1.1 The review MUST verify the generated workflow achieves the
spec's primary objective: transforming codebase docs into audience-
specific meta content files.

11.1.2 The review MUST verify the workflow handles the plugin-
extensible audience system (dynamic discovery, frontmatter-driven
generation).

11.1.3 The review MUST verify the publish lifecycle matches the
spec (Stage, Review, Refine, Backup, History, Publish).

### 11.2 Step-by-Step Verification

11.2.1 The review MUST verify each generation step reads the correct
audience definition and produces content matching the audience's
section_structure.

11.2.2 The review MUST verify the backup step copies current/ to
backups/ (not moves).

11.2.3 The review MUST verify the history step moves old current/
to history/{job_id}/.

11.2.4 The review MUST verify the publish step copies runs/{job_id}/
to current/ and creates/updates meta_manifest.json.

11.2.5 The review MUST verify the meta_manifest.json structure matches
the spec's schema (workflow_id, change_or_run_id, audiences object,
published_timestamp, supersedes, active_set).

### 11.3 Data Flow

11.3.1 The review MUST verify information flows correctly from
codebase docs through generation to published meta content.

11.3.2 The review MUST verify audience definitions are consumed
correctly by generation steps.

11.3.3 The review MUST verify codebase_manifest.json is used to
understand the doc inventory.

### 11.4 No Hallucinations

11.4.1 The review MUST verify no extra configuration files exist
that are not required by the spec.

11.4.2 The review MUST verify no incorrect API calls, wrong model
references, or unnecessary external dependencies are introduced.

11.4.3 The review MUST verify no user-provided input parameters are
added (spec says "no user-provided inputs").

11.4.4 The review MUST verify the audience set matches the spec's
initial set (developer, architect, executive) -- no extra audiences
added, no audiences missing.

### 11.5 Gatekeeper Effectiveness

11.5.1 The review MUST assess whether earlier gatekeepers caught
issues or whether issues reached the final review stage.

11.5.2 If issues are found that gatekeepers should have caught, the
review MUST flag the gatekeeper's ineffectiveness for that specific
issue.

11.5.3 The review MUST NOT flag issues that were already caught and
resolved by earlier gatekeepers.

## 12. Criteria for refine_package step

### 12.1 Completeness

12.1.1 The refine step MUST be able to fix ALL types of issues
flagged in the review report: structural errors, missing files,
logic bugs, prompt quality issues, audience definition problems.

12.1.2 The refine step MUST read the review report and address each
issue systematically.

12.1.3 The refine step MUST NOT introduce new issues while fixing
reported ones.

### 12.2 actions.py Handling

12.2.1 If the review flags actions.py issues (missing actions, stub
implementations, incorrect logic), the refine step MUST be able to
add or update actions.py with corrected implementations.

12.2.2 The refine step MUST NOT break existing working actions while
fixing flagged ones.

### 12.3 Cross-File Consistency

12.3.1 After refinement, workflow.toml step definitions MUST still
match the actual files in the package.

12.3.2 After refinement, context_extensions.py artifact keys MUST
still match all artifacts declared in workflow.toml.

12.3.3 After refinement, prompt file placeholders MUST still be
bare (not accidentally backtick-wrapped during editing).

12.3.4 After refinement, audience definition files MUST still have
valid YAML frontmatter with all required fields.

12.3.5 The refine step MUST verify its changes maintain consistency
across all files before reporting APPROVED.

## 13. Prompt Quality Criteria

The codebase_to_meta_v1 spec involves multiple prompt-driven steps.
Each generated prompt MUST meet the following quality criteria.

### 13.1 Generation Prompts (per-audience meta content generation)

13.1.1 The prompt MUST explicitly instruct the LLM to use file-writing
tools (write tool) to create actual files on disk at the paths
specified by {ARTIFACT_KEY} placeholders.

13.1.2 The prompt MUST clarify that the meta.json result field is for
status/summary ONLY, not for artifact data content.

13.1.3 The prompt MUST specify the output format: Rich Markdown with
YAML frontmatter containing title, audience, audience_label,
generated_date, source_version, section_count.

13.1.4 The prompt MUST instruct the LLM to read the audience definition
file (from audiences/ directory) and follow its section_structure,
tone, focus_areas, and exclude fields.

13.1.5 The prompt MUST instruct the LLM to read codebase_manifest.json
and selectively read relevant docs based on the audience's focus_areas.

13.1.6 The prompt MUST specify that each output file must be
self-contained (no references requiring the source codebase docs).

13.1.7 The prompt MUST include a Self-Validation section instructing
the LLM to verify: all required sections are present, frontmatter is
complete, content matches the audience's focus_areas, excluded topics
are absent.

13.1.8 MUST NOT contain ambiguous phrases like "Write the output to:
{ARTIFACT_KEY}" without clarifying this means "use write tool to create
a file at the path resolved from {ARTIFACT_KEY}."

### 13.2 Review Prompts

13.2.1 The review prompt MUST explicitly instruct the LLM to write the
review report to the specified {ARTIFACT_KEY} path using file-writing
tools.

13.2.2 The review prompt MUST specify the verdict format: APPROVED or
REJECTED on its own line, and that meta.json result must match the
verdict.

13.2.3 The review prompt MUST instruct the LLM to check each generated
meta content file against the audience definition requirements.

13.2.4 The review prompt MUST instruct the LLM to check the meta_index.json
for completeness (all audiences represented).

13.2.5 If REJECTED, the review prompt MUST instruct the LLM to list
specific issues per file with actionable fix instructions.

### 13.3 Refine Prompts

13.3.1 The refine prompt MUST instruct the LLM to read the review
report and address each issue.

13.3.2 The refine prompt MUST specify edit_mode = "in_place" -- modify
existing files, do not recreate from scratch.

13.3.3 The refine prompt MUST instruct the LLM to update meta_index.json
if content changes affect the index.

13.3.4 The refine prompt MUST include a Self-Validation section
instructing the LLM to verify all review issues are addressed before
reporting APPROVED.

### 13.4 Common LLM Mistake Guards

13.4.1 Prompts MUST guard against the LLM putting JSON document content
in the meta.json result field instead of writing it to the artifact file.

13.4.2 Prompts MUST guard against the LLM forgetting to create the
meta_index.json file after generating all audience meta files.

13.4.3 Prompts MUST guard against the LLM hardcoding audience types
instead of dynamically reading from audience definition files.

13.4.4 Prompts MUST guard against the LLM generating content that
references source codebase docs (violates self-contained constraint).

13.4.5 Prompts MUST guard against the LLM including excluded topics
(specified in each audience definition's exclude field).

### 13.5 Output Completeness

13.5.1 Each prompt MUST specify all required outputs with their formats.

13.5.2 Each prompt MUST specify YAML frontmatter fields required in
output documents.

13.5.3 Each prompt MUST specify file naming conventions (e.g.,
META-DEV-{date}-{seq}.md pattern from the spec).

## 14. Audit Criteria

### 14.1 Security Audit

The codebase_to_meta_v1 spec does NOT involve API keys, authentication,
credentials, secrets, or sensitive data. The workflow reads local
codebase documentation files and generates meta content via LLM
invocation. No external API authentication is required. The LLM
interaction is handled by the runner infrastructure, not by the
workflow itself.

No security audit criteria required for this spec.

### 14.2 Logic Audit

This spec involves conditional branching (review/refine loop) and
state management (staging to publish lifecycle). The following
logic audit criteria apply:

14.2.1 The review/refine loop MUST handle the case where all audiences
pass review (no refine needed -- proceed directly to publish).

14.2.2 The review/refine loop MUST handle the case where some audiences
pass but others fail (refine only the failed ones, re-review all).

14.2.3 The refine loop MUST respect max_iterations -- after exhausting
retries, the workflow MUST fail with the configured exhausted_failure_code
(REFINE_EXHAUSTED or equivalent).

14.2.4 The workflow MUST handle the case where audiences/ directory is
empty or contains no valid .md files (error with clear message, not
silent skip).

14.2.5 The workflow MUST handle the case where codebase_manifest.json
is missing or malformed (error with clear message).

14.2.6 The workflow MUST handle the case where some source docs in
codebase docs are missing or unreadable (partial failure with clear
indication of which docs failed).

14.2.7 The publish lifecycle MUST be idempotent -- re-running publish
after a failed attempt must produce the same result as a clean run.

### 14.3 Data Integrity Audit

This spec involves file operations, archiving, index tracking, and
batch processing of multiple audiences. The following data integrity
audit criteria apply:

14.3.1 File operations (write meta content files) MUST produce complete
files -- no partial writes that leave truncated output.

14.3.2 meta_index.json MUST be updated to include ALL successfully
generated meta files. The index MUST be consistent with the actual
files on disk.

14.3.3 meta_manifest.json MUST accurately reflect all published meta
files in current/. The manifest's audiences object MUST have entries
for all audiences that were published.

14.3.4 The backup action MUST copy current/ to backups/ using a
copy-then-verify pattern, not a move. After backup, current/ MUST
still exist and be intact.

14.3.5 The history action MUST move old current/ to history/{job_id}/.
After history, the old current/ MUST no longer exist at its original
location.

14.3.6 The publish action MUST copy runs/{job_id}/ to current/. After
publish, current/ MUST contain all audience subdirectories and their
meta content files.

14.3.7 The publish action MUST update meta_manifest.json in current/
with the correct published_timestamp, source_codebase_version, and
supersedes reference.

14.3.8 Batch processing of multiple audiences MUST be tracked -- the
workflow MUST know which audiences were processed successfully and
which failed.

14.3.9 Partial failure (some audiences succeed, some fail) MUST be
handled -- the workflow MUST NOT proceed to publish if any audience
generation failed.

14.3.10 The audiences/ directory files MUST be treated as read-only
during workflow execution -- the workflow MUST NOT modify audience
definition files.

14.3.11 Source codebase docs under docs/repo/codebase/current/ MUST
be treated as read-only -- the workflow MUST NOT modify source docs.
