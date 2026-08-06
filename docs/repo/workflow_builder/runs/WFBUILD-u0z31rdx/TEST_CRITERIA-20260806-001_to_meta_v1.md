---
doc_type: "test_criteria"
lifecycle_status: "draft"
effective_version: "WFBUILD-u0z31rdx"
spec_source: "codebase_to_meta_v1.md"
created_date: "2026-08-06"
---

# Test Criteria: Codebase to Meta Content v1

## 1. Spec Objective Summary

The codebase_to_meta_v1 workflow transforms approximately 155 technical
documentation files from docs/repo/codebase/current/ into audience-specific
Rich Markdown meta content files. The workflow uses a plugin-extensible
audience definition system where each audience (initially developer,
architect, executive) is defined by a Markdown file with YAML frontmatter
in the workflow's audiences/ directory. The end-to-end transformation is:
codebase documentation (single developer audience) -> audience-specific
meta content files (one per audience, tailored by tone, focus_areas,
exclude, and section_structure) -> published to docs/repo/meta_content/current/
with full version history via a staging lifecycle (stage, review, refine,
backup, history, publish).

The workflow has no user-provided inputs; all paths are resolved from the
repo structure. It follows the same staging/publish pattern as
sdlc_00_codebase_v1.

## 2. Criteria for analyze_spec step

### 2.1 Completeness Criteria

1. The requirements document MUST identify the workflow purpose: transforming
   codebase documentation into audience-specific Rich Markdown meta content.

2. The requirements document MUST identify all three initial audiences
   (developer, architect, executive) and their distinct characteristics
   (tone, focus_areas, exclude, section_structure).

3. The requirements document MUST identify the input source:
   docs/repo/codebase/current/ containing approximately 155 files across
   5 sections (00_standards, 01_inventory, 02_modules, 03_components,
   04_changes) plus codebase_manifest.json.

4. The requirements document MUST identify the input source:
   audiences/ directory in the workflow package containing audience
   definition .md files.

5. The requirements document MUST identify all output artifacts:
   META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX,
   REVIEW_FILE_SUGGESTED, META_MANIFEST.

6. The requirements document MUST identify the staging directory structure:
   docs/repo/meta_content/current/, runs/{job_id}/, history/{job_id}/,
   and backups/.

7. The requirements document MUST identify the publish lifecycle stages:
   Stage, Review, Refine, Backup, History, Publish.

8. The requirements document MUST document the constraint that each meta
   content file must be self-contained (readable without reference to
   source codebase docs).

9. The requirements document MUST document the constraint that audience
   definitions are dynamically discovered at startup by scanning the
   audiences/ directory for .md files.

10. The requirements document MUST document the constraint that the
    audiences/ directory must be deployed to the global runner home via
    install_to_global().

### 2.2 Inference Validation Criteria

11. INFERENCE VALIDATION - Workflow Type: If the workflow type is inferred
    as "mixed" (prompt-driven for content generation + action-driven for
    file operations), the document MUST justify why this type is appropriate.
    Specifically:
    a) Content generation (audience-tailored meta content) requires LLM
       judgment and synthesis -- prompt-driven is correct.
    b) File operations (audience discovery, backup, history move, publish
       copy, manifest generation) are deterministic -- action-driven is
       correct.
    c) If an alternative type is proposed (e.g., purely prompt-driven),
       the justification for why action steps are unnecessary must be
       compelling and specific.

12. INFERENCE VALIDATION - Step Sequence: The proposed step sequence MUST
    logically implement the publish lifecycle described in the spec.
    a) Steps for content generation (per audience) must precede review.
    b) Steps for review/refine must precede publish.
    c) Steps for backup, history, and publish must be in correct order.
    d) The sequence must account for dynamic audience discovery before
       generation.
    e) If a step is missing (e.g., no audience discovery step, no backup
       step), this is a gap.

13. INFERENCE VALIDATION - Custom Actions: Each proposed action MUST be
    a deterministic operation. For this spec, expected actions include:
    a) discover_audiences: scan audiences/ directory, parse YAML frontmatter
       from each .md file, produce list of audience definitions. This is
       deterministic file scanning and parsing.
    b) scan_codebase_docs: read codebase_manifest.json, build index of
       available documentation. This is deterministic file reading.
    c) create_backup: copy current/ to backups/BACKUP-{timestamp}/. This
       is deterministic file copying.
    d) move_to_history: move old current/ to history/{job_id}/. This is
       deterministic file moving.
    e) publish_to_current: copy runs/{job_id}/ to current/ with updated
       manifest. This is deterministic file copying.
    f) generate_manifest: produce meta_manifest.json with audience metadata,
       timestamps, supersedes info. This is deterministic JSON generation.

14. INFERENCE VALIDATION - Action Specifications: Each action specification
    MUST include:
    a) Action name (lowercase_with_underscores).
    b) Purpose: what the action achieves.
    c) Inputs: files/context it reads.
    d) Outputs: files/artifacts it produces.
    e) Logic: high-level description of the operation.
    If any action specification is missing these elements, it is incomplete.

15. INFERENCE VALIDATION - Missing Inferences: The document MUST NOT miss
    elements that are clearly implied by the spec:
    a) The audiences/ directory with 3 .md files is a required workflow
       package component.
    b) install.py or install_to_global() is needed for deploying audiences/
       to the global runner home.
    c) The meta content file format (Rich Markdown with YAML frontmatter)
       is specified and must be reflected in generation step design.
    d) The publish manifest format (JSON with workflow_id, audiences,
       timestamps, supersedes) is specified and must be reflected.
    e) The review/refine loop for human approval of generated content.

### 2.3 Self-Validation Criteria

16. SELF-VALIDATION: The requirements document MUST include a Self-Validation
    section that explicitly checks:
    a) Completeness: all spec objectives covered?
    b) Inference Soundness: workflow type, step sequence, and action
       specifications are appropriate and justified?
    c) Action Specifications: each action has purpose, inputs, outputs,
       logic fully specified?
    d) Feasibility: can downstream artifact definition step consume this?
    e) Constraint Compliance: all spec constraints respected?

17. SELF-VALIDATION: If gaps are found during self-validation, the document
    MUST report REJECTED with specific gaps listed, NOT APPROVED.

18. MUST NOT report APPROVED if any required spec element is missing from
    the requirements without explicit acknowledgment.

## 3. Criteria for gatekeep_requirements step

### 3.1 Completeness Gate

1. COMPLETENESS: The gatekeeper report MUST verify that the requirements
   document captures ALL spec objectives:
   a) Audience-specific content generation for all 3 initial audiences.
   b) Plugin-extensible audience definition system.
   c) Dynamic audience discovery from audiences/ directory.
   d) Codebase documentation scanning and selective reading.
   e) Staging/review/refine/publish lifecycle.
   f) Backup and history management.
   g) Meta manifest generation.
   h) install_to_global() for audiences/ deployment.

2. COMPLETENESS: The gatekeeper MUST verify that all input artifacts are
   declared: codebase docs root, codebase_manifest.json, audience
   definitions in audiences/.

3. COMPLETENESS: The gatekeeper MUST verify that all output artifacts are
   declared: META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX,
   REVIEW_FILE_SUGGESTED, META_MANIFEST.

### 3.2 Approach Validity Gate

4. APPROACH VALIDITY: The gatekeeper MUST evaluate whether the inferred
   workflow type (mixed: prompt + action) is appropriate. If the
   requirements propose a different type, the gatekeeper must assess
   whether it can still achieve all spec objectives.

5. APPROACH VALIDITY: The gatekeeper MUST evaluate whether the proposed
   step sequence correctly implements the publish lifecycle. Specifically:
   a) Does the sequence include audience discovery before generation?
   b) Does it include review/refine before publish?
   c) Does it include backup before publish?
   d) Does it include history move before or during publish?

6. APPROACH VALIDITY: The gatekeeper MUST verify that action step
   specifications describe truly deterministic operations. Content
   generation should NOT be classified as action-driven; file operations
   should NOT be classified as prompt-driven.

### 3.3 Downstream Feasibility Gate

7. DOWNSTREAM FEASIBILITY: The gatekeeper MUST verify that the artifact
   definition step can consume these requirements. Specifically:
   a) Are all artifacts named in UPPER_SNAKE_CASE?
   b) Are artifact purposes clear enough to derive path patterns?
   c) Are input/output relationships clear?

8. DOWNSTREAM FEASIBILITY: The gatekeeper MUST verify that the step
   design step can consume these requirements. Specifically:
   a) Are step purposes clear enough to derive prompt content?
   b) Are action specifications detailed enough to derive code?
   c) Are dependencies between steps clear?

### 3.4 Constraint Satisfaction Gate

9. CONSTRAINT SATISFACTION: The gatekeeper MUST verify all spec constraints
   are respected:
   a) Self-contained meta content files.
   b) Dynamic audience discovery at startup.
   c) Audience frontmatter drives generation (tone, focus_areas, exclude,
      section_structure).
   d) Staging pattern follows docs/repo/meta_content/ structure.
   e) Artifact keys use _FILE suffix for documents.
   f) Standard prompt-driven pattern with review/refine loop.

### 3.5 Evidence and Verdict Gate

10. EVIDENCE: The gatekeeper verdict (APPROVED or REJECTED) MUST be
    justified with specific evidence from the requirements document and
    the original spec. Assertions without evidence are insufficient.

11. EVIDENCE: The gatekeeper report MUST include a Validation Results
    table with Question, Status (PASS/FAIL), and Evidence columns for
    each validation question.

12. LOOP VALIDITY: If the verdict is REJECTED, the report MUST identify
    specific gaps with enough detail for the analyze_spec step to fix them.
    Vague findings like "needs improvement" are insufficient.

13. MUST NOT approve requirements that have known gaps or missing elements.

## 4. Criteria for define_artifacts step

### 4.1 Coverage Criteria

1. Every artifact identified in the requirements MUST have a path pattern
   defined in the artifact contract. This includes at minimum:
   a) META_DEV_FILE - developer meta content file
   b) META_ARCH_FILE - architect meta content file
   c) META_EXEC_FILE - executive meta content file
   d) META_INDEX - JSON index of generated meta files
   e) REVIEW_FILE_SUGGESTED - review document
   f) META_MANIFEST - published manifest in current/

2. If the requirements declare action-driven steps, the artifact contract
   MUST include the WORKFLOW_ACTIONS artifact key for actions.py.

3. Intermediate artifacts needed for the staging lifecycle must be declared:
   a) Staging area under runs/{job_id}/ with per-audience subdirectories.
   b) Backup artifacts under backups/.
   c) History artifacts under history/{job_id}/.

### 4.2 Placeholder Validity Criteria

4. Path patterns MUST use {job_id} for job-specific directories.

5. Path patterns MUST use {seq} for auto-incrementing sequence numbers
   in filenames (e.g., META-DEV-{date}-{seq}.md).

6. If slug-based naming is used, {slug} must be correctly placed.

7. If iteration-based naming is used (e.g., per-audience), {iter} must
   be correctly placed.

8. MUST NOT use hardcoded dates or job IDs in path patterns.

### 4.3 Path Convention Criteria

9. All path patterns MUST be relative to the project root.

10. Output paths MUST follow the staging pattern:
    a) Staging: docs/repo/meta_content/runs/{job_id}/
    b) Published: docs/repo/meta_content/current/
    c) History: docs/repo/meta_content/history/{job_id}/
    d) Backups: docs/repo/meta_content/backups/

11. Per-audience output MUST use subdirectories named by audience_id:
    a) developer/ under staging and current
    b) architect/ under staging and current
    c) executive/ under staging and current

12. The meta_manifest.json MUST be at docs/repo/meta_content/current/
    level (not inside an audience subdirectory).

### 4.4 Self-Validation Criteria

13. SELF-VALIDATION: The artifact contract MUST include a Self-Validation
    section that checks:
    a) All artifacts from requirements have path patterns defined.
    b) WORKFLOW_ACTIONS is included if action steps are declared.
    c) All path patterns are relative.
    d) Placeholder usage is correct ({job_id}, {seq}, {slug}, {iter}).

14. MUST NOT omit WORKFLOW_ACTIONS if requirements declare action-driven
    steps.

## 5. Criteria for gatekeep_artifacts step

### 5.1 Coverage Gate

1. COVERAGE: The gatekeeper MUST verify that ALL artifacts from the
   requirements document have corresponding path patterns in the artifact
   contract. Missing artifacts must be flagged.

2. COVERAGE: The gatekeeper MUST verify that the six spec-declared
   artifacts (META_DEV_FILE, META_ARCH_FILE, META_EXEC_FILE, META_INDEX,
   REVIEW_FILE_SUGGESTED, META_MANIFEST) are all present.

### 5.2 Action Artifacts Gate

3. ACTION ARTIFACTS: If the requirements declare action-driven steps,
   the gatekeeper MUST verify that WORKFLOW_ACTIONS is included in the
   artifact contract. This is critical because without it, actions.py
   will not be generated.

4. ACTION ARTIFACTS: The gatekeeper MUST verify that action-related
   intermediate artifacts (if any) have path patterns defined.

### 5.3 Placeholder Completeness Gate

5. PLACEHOLDER COMPLETENESS: The gatekeeper MUST validate that path
   patterns use correct placeholders:
   a) {job_id} for job-specific directories.
   b) {seq} for sequence numbers in filenames.
   c) No hardcoded dates or job IDs.

6. PLACEHOLDER COMPLETENESS: The gatekeeper MUST verify that placeholders
   are used consistently across related artifacts (e.g., all staging paths
   use the same {job_id} root).

### 5.4 Path Validity Gate

7. PATH VALIDITY: The gatekeeper MUST verify ALL path patterns are
   relative to the project root. Absolute paths are forbidden.

8. PATH VALIDITY: The gatekeeper MUST verify paths follow the staging
   pattern convention (current/, runs/, history/, backups/).

9. PATH VALIDITY: The gatekeeper MUST verify per-audience paths use
   audience_id subdirectories (developer/, architect/, executive/).

### 5.5 Chain Integrity Gate

10. CHAIN INTEGRITY: The gatekeeper MUST verify artifact flow from inputs
    to outputs is unbroken:
    a) Input artifacts (codebase docs, audience definitions) can be
       resolved at runtime.
    b) Generated artifacts (meta content files) have clear paths.
    c) Published artifacts (current/ files, manifest) have clear paths.
    d) Intermediate artifacts (staging, backup, history) have clear paths.

11. MUST NOT approve an artifact contract with broken chains (e.g., an
    output artifact with no way to reach it from the inputs).

## 6. Criteria for design_steps step

### 6.1 Coverage Criteria

1. The step architecture MUST implement ALL requirements from the
   requirements document. Every spec objective must map to at least one
   step.

2. The step sequence MUST include steps for each phase of the publish
   lifecycle:
   a) Audience discovery / codebase scanning.
   b) Content generation (per audience).
   c) Index generation.
   d) Review / refine loop.
   e) Backup creation.
   f) History archiving.
   g) Publishing to current/.
   h) Manifest generation.

### 6.2 Artifact Flow Criteria

3. The artifact flow MUST be traceable from inputs to outputs. For each
   step, the reviewer must be able to verify:
   a) required_inputs are produced by prior steps or are external inputs.
   b) produces are consumed by subsequent steps or are final outputs.
   c) No orphaned artifacts (produced but never consumed).
   d) No unsatisfied dependencies (required but never produced).

4. The data flow for the content generation path must be:
   codebase docs + audience definition -> LLM generation -> meta content
   file -> index entry -> review -> refine (if needed) -> publish.

### 6.3 Routing Validity Criteria

5. Every step MUST have a valid onsuccess value pointing to an existing
   step name.

6. The workflow MUST end with stepCompletion (action: step_completion).

7. Review steps MUST have on_reject_refine configuration pointing back
   to the appropriate generation/refine step.

8. Refine steps MUST have onsuccess pointing back to the review step
   (loop_returns_to pattern).

9. MUST NOT have circular routing that does not involve a review/refine
   loop (e.g., step A -> step B -> step A without human approval).

### 6.4 Step Type Appropriateness Criteria

10. Content generation steps (producing audience-tailored meta content)
    MUST be classified as prompt-driven (type: prompt).

11. File operation steps (audience discovery, backup, history, publish,
    manifest generation) MUST be classified as action-driven (type: action).

12. Review/critique steps MUST be classified as prompt-driven.

13. Step classification MUST be consistent with the requirements document.
    If the requirements specify an action, the step architecture must use
    action type.

### 6.5 Action Consistency Criteria

14. Action names in the step architecture MUST match action names in the
    requirements document's Custom Actions table.

15. Each action step MUST reference an action that is fully specified
    in the requirements (purpose, inputs, outputs, logic).

### 6.6 Review Loop Design Criteria

16. The review/refine loop MUST be properly configured:
    a) Review step has on_reject_refine pointing to refine step.
    b) Refine step has onsuccess pointing back to review step.
    c) max_iterations is set (recommended: 2).
    d) exhausted_failure_code and exhausted_failure_class are defined.

17. The review step SHOULD have requires_human_approval_after = true
    for human-in-the-loop quality control.

### 6.7 Self-Validation Criteria

18. SELF-VALIDATION: The step architecture MUST include a Self-Validation
    section that checks:
    a) Routing validity: all onsuccess targets exist, no broken links.
    b) Artifact flow: all required_inputs satisfied by prior produces.
    c) Action consistency: action names match requirements.
    d) Review loop: on_reject_refine correctly configured.
    e) Completeness: all requirements have corresponding steps.

19. MUST NOT report APPROVED if routing is broken or artifact flow has
    gaps.

## 7. Criteria for gatekeep_steps step

### 7.1 Coverage Gate

1. COVERAGE: The gatekeeper MUST verify ALL requirements from the
   requirements document have corresponding steps in the architecture.
   Each spec objective must be traceable to at least one step.

2. COVERAGE: The gatekeeper MUST specifically verify:
   a) Audience discovery step exists.
   b) Content generation exists for all 3 audiences (or is parameterized).
   c) Index generation step exists.
   d) Review/refine loop exists.
   e) Backup, history, publish steps exist.
   f) Manifest generation step exists.
   g) stepCompletion terminal step exists.

### 7.2 Data Flow Gate

3. DATA FLOW: The gatekeeper MUST verify that each step's required_inputs
   are satisfied by prior steps' produces or by external inputs. Trace
   the full dependency chain:
   a) First step's required_inputs must be external (no prior produces).
   b) Each subsequent step's required_inputs must be produced by a prior
      step or be declared external.
   c) Final step produces must include all spec-declared output artifacts.

4. DATA FLOW: The gatekeeper MUST verify no circular dependencies exist
   outside of explicit review/refine loops.

### 7.3 Routing Validity Gate

5. ROUTING VALIDITY: The gatekeeper MUST verify:
   a) Every step has onsuccess pointing to an existing step.
   b) The last content step routes to stepCompletion.
   c) Review steps have on_reject_refine to refine/generate steps.
   d) Refine steps route back to review on success.

### 7.4 Type Consistency Gate

6. TYPE CONSISTENCY: The gatekeeper MUST verify step types match task
   nature:
   a) LLM synthesis/generation tasks -> prompt type.
   b) Deterministic file operations -> action type.
   c) The classification is consistent with the requirements document.

### 7.5 Loop Validity Gate

7. LOOP VALIDITY: The gatekeeper MUST verify review/refine loops are
   properly configured:
   a) on_reject_refine points to the correct producer step.
   b) The artifact being refined matches the produced artifact.
   c) max_iterations is set and reasonable (not 0, not unlimited).
   d) exhausted_failure_code is defined.

8. MUST NOT approve a step architecture with broken loops or missing
   terminal step.

## 8. Criteria for generate_package step

### 8.1 Principles-Based Generation Criteria

1. PRINCIPLES-BASED: Generation MUST follow the principles-based approach.
   The coder MUST infer required files from STEP_ARCHITECTURE and
   ARTIFACT_CONTRACT, NOT follow a fixed numbered list.

2. PRINCIPLES-BASED: For each prompt-driven step in the architecture,
   a prompt file MUST be generated. For each action-driven step, an
   action implementation MUST be added to actions.py.

### 8.2 File Completeness Criteria

3. FILE COMPLETENESS: The following core files MUST always be present:
   a) workflow.toml
   b) context_extensions.py
   c) README.md

4. FILE COMPLETENESS: If the architecture declares prompt-driven steps,
   prompts/ directory MUST contain one .txt file per prompt-driven step.

5. FILE COMPLETENESS: If the architecture declares action-driven steps,
   actions.py MUST exist with @action implementations for ALL declared
   actions.

6. FILE COMPLETENESS: The audiences/ directory MUST contain the 3 initial
   audience definition files:
   a) audiences/developer.md
   b) audiences/architect.md
   c) audiences/executive.md

7. FILE COMPLETENESS: Each audience .md file MUST have YAML frontmatter
   with audience_id, label, tone, focus_areas, exclude, section_structure.

8. FILE COMPLETENESS: Conditional files:
   a) .env.sample: MUST exist if the workflow uses environment variables
      (e.g., for API keys -- unlikely for this spec, but check).
   b) config.json.sample: MUST exist if the workflow needs runtime config
      (unlikely for this spec, but check).

### 8.3 actions.py Criteria

9. actions.py: If present, each @action decorator MUST use the exact
   action name from the step architecture.

10. actions.py: Each action function MUST:
    a) Accept keyword-only arguments: context, state, step_cfg, project_root.
    b) Return ActionResult with status ("APPROVED" or "REJECTED").
    c) Include proper error handling for expected failure modes.
    d) Have type hints and docstrings.

11. actions.py: The discover_audiences action MUST:
    a) Scan the audiences/ directory for .md files.
    b) Parse YAML frontmatter from each file.
    c) Produce a structured list of audience definitions.
    d) Handle the case where audiences/ directory is empty or missing.

12. actions.py: The create_backup action MUST:
    a) Copy docs/repo/meta_content/current/ to
       docs/repo/meta_content/backups/BACKUP-{timestamp}/.
    b) Handle the case where current/ does not exist (first run).
    c) Use copy operation (not move) to preserve source.

13. actions.py: The publish_to_current action MUST:
    a) Copy runs/{job_id}/ content to docs/repo/meta_content/current/.
    b) Generate/update meta_manifest.json in current/.
    c) Handle overwriting of existing files.

14. actions.py: The generate_manifest action MUST produce a JSON file
    with: workflow_id, change_or_run_id, source_codebase_version,
    audiences dict, published_timestamp, supersedes, active_set.

### 8.4 workflow.toml Criteria

15. workflow.toml: MUST declare name = "codebase_to_meta_v1" (matching
    directory name).

16. workflow.toml: MUST declare job_prefix = "META" (from spec).

17. workflow.toml: Step sequence MUST match STEP_ARCHITECTURE exactly:
    same step names, same order, same types (prompt vs action).

18. workflow.toml: Artifact bindings MUST match ARTIFACT_CONTRACT exactly:
    same artifact keys in produces, required_inputs.

19. workflow.toml: onsuccess values MUST be at [[step]] top level, NOT
    under [step.artifacts].

20. workflow.toml: MUST end with stepCompletion step
    (action = "step_completion").

21. workflow.toml: Review steps MUST have requires_human_approval_after
    where appropriate.

22. workflow.toml: Refine steps MUST have target_artifact and
    edit_mode = "in_place" if editing existing artifacts.

### 8.5 context_extensions.py Criteria

23. context_extensions.py: MUST define a class extending WorkflowExtensions.

24. context_extensions.py: workflow_name MUST be "codebase_to_meta_v1".

25. context_extensions.py: register_artifact_keys() MUST return a dict
    with ALL artifact keys from the ARTIFACT_CONTRACT.

26. context_extensions.py: register_artifact_keys() MUST use RELATIVE
    paths (relative to project root).

27. context_extensions.py: build_context_extensions() MUST resolve ALL
    paths to ABSOLUTE paths.

28. context_extensions.py: MUST handle {job_id}, {seq}, {slug} placeholder
    resolution correctly.

29. context_extensions.py: MUST NOT have undefined variable references.

### 8.6 prompts/ Criteria

30. prompts/: MUST contain one .txt file per prompt-driven step.

31. prompts/: Each prompt file MUST use bare {ARTIFACT_KEY} placeholders
    (NOT backtick-wrapped).

32. prompts/: Each prompt file MUST be ASCII-only.

33. prompts/: Each prompt file MUST include Objective, Reference Inputs,
    and Output Instructions sections.

34. prompts/: Filename convention: prompts/NN_step_name.txt where NN is
    step order.

### 8.7 README.md Criteria

35. README.md: MUST include a step reference listing all workflow steps.

36. README.md: MUST list all artifact keys and their descriptions.

37. README.md: MUST document the audience plugin system and how to add
    new audiences.

38. README.md: MUST document the publish lifecycle (stage, review, refine,
    backup, history, publish).

### 8.8 Self-Validation Criteria

39. SELF-VALIDATION: The generation step MUST include Self-Validation
    checking:
    a) File completeness: all files implied by design are present.
    b) Design fidelity: files match STEP_ARCHITECTURE and ARTIFACT_CONTRACT.
    c) Action implementation: all declared actions are implemented.
    d) Artifact reporting: all generated file paths reported in meta.json.

40. MUST NOT report APPROVED if actions.py is missing when action steps
    are declared in the architecture.

41. MUST NOT report APPROVED if any artifact key from the contract is
    missing from context_extensions.py.

## 9. Criteria for gatekeep_package step

### 9.1 File Checklist Gate

1. FILE CHECKLIST: The gatekeeper MUST verify ALL expected files exist.
   The expected file list for this spec:
   a) workflow.toml (always required).
   b) context_extensions.py (always required).
   c) README.md (always required).
   d) actions.py (required -- action steps are declared).
   e) prompts/NN_*.txt (one per prompt-driven step).
   f) audiences/developer.md (required).
   g) audiences/architect.md (required).
   h) audiences/executive.md (required).
   i) .env.sample (conditional -- only if env vars needed).
   j) config.json.sample (conditional -- only if config needed).

2. FILE CHECKLIST: The gatekeeper MUST produce a File Checklist table
   showing Expected vs Actual (Present/Missing) for each file.

### 9.2 Action Completeness Gate

3. ACTION COMPLETENESS: If action steps are declared, the gatekeeper
   MUST verify actions.py exists.

4. ACTION COMPLETENESS: The gatekeeper MUST verify actions.py contains
   actual implementations (not stubs). Each @action function must have
   real logic, not just return ActionResult with placeholder data.

5. ACTION COMPLETENESS: The gatekeeper MUST verify every action declared
   in the step architecture has a corresponding @action function in
   actions.py.

### 9.3 Design Fidelity Gate

6. DESIGN FIDELITY: The gatekeeper MUST verify workflow.toml implements
   the exact step sequence from STEP_ARCHITECTURE. Step names, types,
   routing, and artifact bindings must match.

7. DESIGN FIDELITY: The gatekeeper MUST verify context_extensions.py
   registers all artifact keys from ARTIFACT_CONTRACT with correct
   path patterns.

8. DESIGN FIDELITY: The gatekeeper MUST verify prompts/ has one file
   per prompt-driven step and filenames match convention.

### 9.4 Prompt Completeness Gate

9. PROMPT COMPLETENESS: The gatekeeper MUST verify prompts/ contains
   exactly one file per prompt-driven step. Missing prompts or extra
   prompts must be flagged.

10. PROMPT COMPLETENESS: The gatekeeper MUST verify prompt files use
    bare {ARTIFACT_KEY} placeholders (not backtick-wrapped).

### 9.5 Scope Check Gate

11. SCOPE CHECK: The gatekeeper MUST detect scope shrink -- elements
    from the design that were silently dropped or simplified. Compare
    the generated files against STEP_ARCHITECTURE and ARTIFACT_CONTRACT.

12. SCOPE CHECK: The gatekeeper MUST detect scope creep -- elements
    added that are not in the design (extra steps, extra artifacts,
    extra files without justification).

13. MUST NOT approve a package with scope shrink or scope creep.

## 10. Criteria for validate_bundle step

### 10.1 Structural Checks

1. TOML validity: workflow.toml MUST parse without errors.

2. Routing: All onsuccess values MUST reference existing step names.

3. Artifact registration: All artifact keys used in step fields MUST
   be registered in context_extensions.py register_artifact_keys().

4. Step termination: The last step MUST be stepCompletion with
   action = "step_completion".

5. Step naming: All step names MUST be lowercase_with_underscores and
   unique within the workflow.

### 10.2 Semantic Checks

6. Action code: Each @action function in actions.py MUST contain actual
   logic, not just stub implementations that return APPROVED with no
   side effects.

7. Action signatures: Each @action function MUST accept keyword-only
   arguments: context, state, step_cfg, project_root.

8. Action returns: Each @action function MUST return ActionResult with
   status, remark, and artifacts fields.

9. Context extensions: build_context_extensions() MUST return absolute
   paths. Verify no relative paths leak through.

10. Audience definitions: Each audiences/*.md file MUST have valid YAML
    frontmatter with all required fields (audience_id, label, tone,
    focus_areas, exclude, section_structure).

### 10.3 File Completeness Checks

11. All required files MUST be present: workflow.toml,
    context_extensions.py, README.md, actions.py (if action steps),
    prompts/ (if prompt steps), audiences/ (3 .md files).

12. MUST NOT have extra files that are not accounted for by the design
    (no orphaned files).

## 11. Criteria for review_package step

### 11.1 Spec Fulfillment

1. The review MUST verify the workflow actually achieves the spec
   objective: transforming codebase docs into audience-specific meta
   content for developer, architect, and executive audiences.

2. The review MUST verify the audience plugin system works: adding a
   new .md file to audiences/ should produce a new meta content file
   without workflow logic changes.

3. The review MUST verify the publish lifecycle matches the spec:
   stage -> review -> refine -> backup -> history -> publish.

### 11.2 Step-by-Step Verification

4. The review MUST verify each step does what the spec describes:
   a) Audience discovery: correctly scans audiences/ and parses
      frontmatter.
   b) Content generation: produces audience-tailored Rich Markdown
      with correct YAML frontmatter.
   c) Index generation: produces JSON index with audience metadata.
   d) Review/refine: properly loops until approved.
   e) Backup: copies current/ to backups/ with timestamp.
   f) History: moves old current/ to history/{job_id}/.
   g) Publish: copies staging to current/ with manifest.

### 11.3 Data Flow Verification

5. The review MUST verify information flows correctly between steps:
   a) Codebase docs -> generation -> meta content files.
   b) Audience definitions -> generation -> audience-tailored content.
   c) Generated files -> index -> manifest.
   d) Review feedback -> refine -> improved files.

### 11.4 No Hallucinations

6. The review MUST verify no extra configurations are added that are
   not in the spec (e.g., wrong API models, unnecessary environment
   variables, unused config options).

7. The review MUST verify no wrong models or role policies are used
   (e.g., using implement_standard for content generation instead of
   architect_standard).

8. The review MUST verify no unnecessary user inputs are required
   (the spec says "No user-provided inputs").

### 11.5 Gatekeeper Effectiveness

9. The review SHOULD assess whether gatekeeper steps caught issues
   early. If the package reaches final review with obvious errors
   (missing files, broken routing), the gatekeepers failed.

10. The review MUST identify any issues that slipped through
    gatekeepers and assess root cause.

## 12. Criteria for refine_package step

### 12.1 Completeness Criteria

1. COMPLETENESS: The refine step MUST be able to fix ALL types of
   issues flagged in the review:
   a) Missing files: can add new files to the package.
   b) Broken routing: can fix workflow.toml step routing.
   c) Incomplete actions: can add or update actions.py implementations.
   d) Missing prompts: can add new prompt files.
   e) Incorrect artifacts: can fix artifact bindings.
   f) Placeholder issues: can fix backtick-wrapped or missing placeholders.

2. COMPLETENESS: The refine step MUST maintain consistency across all
   files when making changes. If workflow.toml changes, context_extensions.py
   and prompts must remain consistent.

### 12.2 actions.py Handling

3. actions.py HANDLING: If the review flags missing or incomplete actions,
   the refine step MUST be able to:
   a) Create actions.py if it does not exist.
   b) Add new @action functions for missing actions.
   c) Fix existing @action functions that have incomplete logic.
   d) Update action function signatures to match expected pattern.

4. actions.py HANDLING: After refinement, actions.py MUST still be
   consistent with workflow.toml (action names match, artifact bindings
   match).

### 12.3 Consistency Criteria

5. CONSISTENCY: Refinement MUST maintain cross-file consistency:
   a) If a step is added/removed in workflow.toml, corresponding prompt
      file must be added/removed.
   b) If an artifact key changes in workflow.toml, context_extensions.py
      must be updated.
   c) If an action name changes, both workflow.toml and actions.py must
      match.

6. CONSISTENCY: The refine step MUST use target_artifact and
   edit_mode = "in_place" for editing existing files rather than
   overwriting them entirely.

7. MUST NOT introduce new issues while fixing flagged issues.

## 13. Prompt Quality Criteria (for prompt-driven steps)

For each prompt-driven step in the generated workflow, the following
criteria verify prompt quality:

### 13.1 Output Mechanism Criteria

1. Each prompt MUST explicitly instruct the LLM to use file-writing tools
   to create actual files on disk. The prompt MUST clarify that the
   meta.json result field is for status/summary ONLY, not artifact data.

2. Each prompt MUST use unambiguous language for file output:
   "Write the output to {ARTIFACT_KEY}" is acceptable ONLY if the prompt
   also clarifies this means "write to the file path resolved from
   {ARTIFACT_KEY}". If ambiguous, it must be reworded.

3. Each prompt MUST NOT instruct the LLM to put file content (JSON,
   Markdown) into the meta.json result field.

### 13.2 Ambiguity Check Criteria

4. Each prompt MUST be reviewed for phrases that could be misinterpreted:
   a) "Generate the content" -- where? To a file? To the result field?
   b) "Return the output" -- return to where? File or meta.json?
   c) "Include X in the output" -- which output file?

5. Each prompt MUST use imperative, unambiguous instructions:
   a) "Write the document to {ARTIFACT_KEY}" -- clear file output.
   b) "Set status to APPROVED in meta.json" -- clear meta.json usage.

### 13.3 Common LLM Mistakes Guard Criteria

6. Each prompt MUST guard against known failure modes:
   a) Putting JSON data in result field instead of writing files.
   b) Forgetting to create required output files.
   c) Skipping index or manifest file creation.
   d) Using hardcoded paths instead of {ARTIFACT_KEY} placeholders.
   e) Wrapping placeholders in backticks.

7. Prompts for content generation steps MUST specifically guard against:
   a) Generating content for only one audience instead of all audiences.
   b) Not following the audience definition's section_structure.
   c) Not including required YAML frontmatter in output files.

8. Prompts for file operation steps (if prompt-driven) MUST guard against:
   a) Using move instead of copy for backup operations.
   b) Not creating index files after batch operations.
   c) Overwriting existing files without backup.

### 13.4 Completeness Criteria

9. Each prompt MUST specify ALL required outputs:
   a) File format (Rich Markdown, JSON, TOML, etc.).
   b) Required sections or fields.
   c) File naming conventions (if not handled by artifact keys).
   d) Encoding (ASCII-only).

10. Each prompt MUST specify the expected YAML frontmatter (if applicable):
    a) Required fields (doc_type, lifecycle_status, effective_version).
    b) Optional fields.

### 13.5 Self-Validation Criteria

11. Each prompt-driven producer step MUST include a Self-Validation section
    that checks output completeness before reporting APPROVED.

12. The Self-Validation section MUST instruct the LLM to:
    a) Verify all required files were written.
    b) Verify file content matches required format.
    c) Verify no required elements are missing.
    d) If checks fail, revise output and re-validate.
    e) Only report APPROVED when all checks pass.

13. MUST NOT have a Self-Validation section that merely mentions validation
    exists without instructing the LLM to actually perform it and revise
    if needed.

## 14. Audit Criteria (Conditional)

### 14.1 Security Audit

The codebase_to_meta_v1 spec does NOT involve API keys, authentication,
credentials, secrets, or sensitive data. The workflow reads local
documentation files and writes local output files. No external API calls
are required.

Therefore: Security audit criteria are NOT required for this spec.

However, if the generated workflow were to add external integrations
(e.g., calling an LLM API for content generation), the following would
apply:
- API keys loaded from .env file, not hardcoded.
- Credentials passed securely (e.g., Bearer token in headers).
- No credential values in generated files or logs.
- Authentication failures handled gracefully.

### 14.2 Logic Audit

The codebase_to_meta_v1 spec DOES involve conditional branching and
state management:

1. LOGIC AUDIT - Audience Discovery: The discover_audiences action must
   handle:
   a) Empty audiences/ directory (no .md files found).
   b) Malformed YAML frontmatter in an audience file.
   c) Missing required fields in frontmatter.
   d) Duplicate audience_id values.

2. LOGIC AUDIT - Review/Refine Loop: The review/refine loop must handle:
   a) Maximum iterations exhausted (max_iterations reached).
   b) Proper loop termination when review approves.
   c) Proper loop continuation when review rejects.
   d) exhausted_failure_code triggered correctly.

3. LOGIC AUDIT - Publish Lifecycle: The publish actions must handle:
   a) First-run scenario: current/ does not exist yet. No backup needed.
   b) Normal scenario: current/ exists, create backup, move to history,
      copy staging to current.
   c) Partial failure: some audiences succeed, others fail during
      generation.
   d) Concurrent runs: two jobs running simultaneously should not
      corrupt each other's output.

4. LOGIC AUDIT - State Management: The workflow must properly manage
   state across step boundaries:
   a) Artifacts produced by early steps must be available to later steps.
   b) The job_id must be consistent across all staging paths.
   c) The source_codebase_version must be captured and propagated to
      the manifest.

### 14.3 Data Integrity Audit

The codebase_to_meta_v1 spec DOES involve file operations, archiving,
index tracking, and batch processing:

1. DATA INTEGRITY - File Operations:
   a) Backup operations MUST use copy (not move) to preserve source.
   b) History operations MUST use move (source is being replaced).
   c) Publish operations MUST copy staging to current (not move, to
      preserve staging for audit trail).
   d) File writes MUST be atomic (write complete file, not partial).
      Use temporary file + rename pattern if needed.

2. DATA INTEGRITY - Index Tracking:
   a) meta_index.json MUST list all generated meta files with audience
      metadata.
   b) meta_manifest.json MUST accurately reflect what is published in
      current/.
   c) After publish, meta_manifest.json MUST be updated with:
      published_timestamp, supersedes (previous job_id or null),
      active_set = true.

3. DATA INTEGRITY - Batch Processing:
   a) The workflow processes multiple audiences as a batch. If one
      audience generation fails, the others should not be affected.
   b) The workflow reads ~155 codebase docs. Partial read failures
      (one file unreadable) should not abort the entire generation.
   c) The index file must track which audience files were successfully
      generated.

4. DATA INTEGRITY - Archiving:
   a) History archiving must preserve the complete previous current/
      content (all audience files, manifest).
   b) Backup must preserve the complete current/ content with a
      timestamped directory name.
   c) After archiving, the old current/ directory must be empty or
      removed before new content is copied in.

## 15. Audience Plugin System Criteria

These criteria are specific to the plugin-extensible audience system
described in the spec:

1. The audiences/ directory MUST be part of the workflow package.

2. Each audience .md file MUST be parseable as Rich Markdown with YAML
   frontmatter.

3. The frontmatter MUST include: audience_id, label, tone, focus_areas,
   exclude, section_structure.

4. The body of each audience .md file provides additional prompt guidance
   for the LLM. This MUST be incorporated into the generation prompt.

5. Adding a new audience MUST NOT require changes to workflow.toml,
   context_extensions.py, or actions.py. Only dropping a new .md file
   into audiences/ should be sufficient.

6. The discover_audiences action MUST dynamically detect all .md files
   in audiences/ at runtime, not hardcode the 3 initial audiences.

7. The output directory structure MUST create per-audience subdirectories
   dynamically based on discovered audience_id values.

## 16. Publish Lifecycle Criteria

These criteria verify the staging/publish pattern matches the spec:

1. STAGE: Generated meta content files MUST be written to
   docs/repo/meta_content/runs/{job_id}/ with per-audience subdirectories.

2. REVIEW: A review document MUST be generated covering all audience
   meta content files. Human approval is required before publishing.

3. REFINE: If review rejects, refine step must update the meta content
   files in the staging area. Loop continues until approved.

4. BACKUP: Before publishing, current/ MUST be copied to
   docs/repo/meta_content/backups/BACKUP-{timestamp}/. On first run
   (no current/), backup step must handle gracefully.

5. HISTORY: Old current/ MUST be moved to
   docs/repo/meta_content/history/{job_id}/. This preserves previous
   versions.

6. PUBLISH: Staging content MUST be copied to
   docs/repo/meta_content/current/ with per-audience subdirectories.
   meta_manifest.json MUST be updated in current/.

7. MANIFEST: meta_manifest.json MUST contain:
   a) workflow_id: "codebase_to_meta_v1"
   b) change_or_run_id: the job_id
   c) source_codebase_version: identifier for source docs version
   d) audiences: dict mapping audience_id to {label, file, generated_date}
   e) published_timestamp: ISO 8601 timestamp
   f) supersedes: previous job_id or null
   g) active_set: true
