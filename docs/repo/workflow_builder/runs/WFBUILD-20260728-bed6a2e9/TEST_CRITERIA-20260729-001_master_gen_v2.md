---
doc_type: "test_criteria"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260728-bed6a2e9"
spec_ref: "docs/repo/workflow_builder/specs/product_master_gen_v2.md"
workflow_name: "product_master_gen_v2"
generated_date: "2026-07-29"
---

# Test Criteria: Product Master Generator v2

## 1. Spec Objective Summary

The Product Master Generator v2 workflow ingests a directory of diverse product
source materials (images, PDFs, URLs, text files, spreadsheets, marketing
materials, notes) and produces a canonical Product Master document. The
end-to-end transformation is:

INPUT: A directory path (PRODUCT_SOURCE_DIR) containing product source files of
various types (all optional, use whatever is available), optionally an existing
Product Master for incremental updates (PRODUCT_MASTER_FILE).

OUTPUT: A structured markdown Product Master document with YAML frontmatter
(product name, source count, completeness), table of contents, knowledge
sections organized logically (Product Information, Target Audience, Benefits and
USP, Marketing Assets, plus LLM-proposed additional sections), source
attribution, and optional Changelog for incremental updates.

The workflow must be designed by the builder using the gatekeeper QC pipeline
pattern (Pattern 4), with inference-based requirements generation,
principles-based package generation, and self-validation in each producer step.
The builder has full discretion over the step architecture -- section generation
strategy, quality control placement, review strategy, action steps, artifact
structure, and routing. The spec does not prescribe a fixed number of steps.


## 2. Criteria for analyze_spec Step

### 2.1 Requirements Document Content

1. REQ-001: The requirements document must capture the workflow purpose:
   consolidating product knowledge from diverse source materials into a
   single authoritative Product Master document.
2. REQ-002: The requirements document must identify PRODUCT_SOURCE_DIR as a
   required input of type "directory path" containing source files of various
   types (images, PDFs, URLs, data files, marketing materials, notes).
3. REQ-003: The requirements document must identify PRODUCT_MASTER_FILE as an
   optional input for incremental updates (merge + changelog).
4. REQ-004: The requirements document must identify PRODUCT_MASTER_FILE as the
   primary output artifact: the assembled canonical Product Master document.
5. REQ-005: The requirements document must list all five standard knowledge
   sections: Product Information, Target Audience, Benefits and USP, Marketing
   Assets, and LLM-proposed Additional Sections. Each section must have its
   expected content domains described.
6. REQ-006: The requirements document must capture the constraint that factual
   accuracy is prioritized over completeness.
7. REQ-007: The requirements document must capture the constraint that
   conflicting information must be explicitly identified with both sides and
   source attribution.
8. REQ-008: The requirements document must capture the constraint that missing
   information must be represented as explicit knowledge gaps, not fabricated.
9. REQ-009: The requirements document must capture the constraint that the
   Product Master is downstream-agnostic (no campaign/media assumptions).
10. REQ-010: The requirements document must capture the slug extraction
    requirement from PRODUCT_SOURCE_DIR name for consistent artifact naming.
11. REQ-011: The requirements document must capture incremental update
    behavior: merge new knowledge and add Changelog when PRODUCT_MASTER_FILE
    is provided as input.
12. REQ-012: The requirements document must note that URL files contain one
    URL per line and the LLM fetches/processes URL content.
13. REQ-013: The requirements document must capture the extensibility
    principle: the workflow should analyze input sources and determine if
    additional sections would be valuable based on product type.

### 2.2 Inference Validation

14. REQ-014 (INFERENCE): If the workflow type is inferred (not explicitly
    stated in the spec), the inference must be sound. The spec describes
    file scanning, knowledge synthesis, and assembly -- the type must match
    the nature of the work. Justification must explain why the chosen type
    (e.g., mixed, prompt-driven) is appropriate versus alternatives.
15. REQ-015 (INFERENCE): If the step sequence is proposed, it must be the
    most appropriate solution for the problem domain. The justification must
    explain why this decomposition is better than alternatives (e.g., single
    monolithic step, all-parallel steps, different grouping).
16. REQ-016 (INFERENCE): If custom actions are inferred, they must be truly
    deterministic operations suitable for code implementation (file scanning,
    directory walking, file classification). The justification must explain
    why each action cannot be handled by a prompt step.
17. REQ-017 (INFERENCE): Action specifications must include sufficient detail
    for implementation: purpose, inputs, outputs, logic/algorithm, error
    handling. A vague description like "scan the inputs" is insufficient.
18. REQ-018 (INFERENCE): The requirements must identify all elements that
    can be inferred from the spec. Check: Does the spec mention "images,
    PDFs, URLs, spec sheets, marketing copy, and personal notes"? Are these
    all addressed in the requirements? Are there any elements the LLM should
    have inferred but missed (gaps in the solution)?
19. REQ-019 (INFERENCE): The requirements must identify the supported source
    types from the spec: Product URLs, Product images (PNG, JPG, WEBP), PDFs,
    Data files (CSV, XLSX), Marketing materials (DOCX, MD, TXT), User notes
    (MD, TXT). All must be accounted for in the workflow design.

### 2.3 Input/Output Artifact Identification

20. REQ-020: The requirements must identify all input artifacts with their
    types, required/optional status, and descriptions.
21. REQ-021: The requirements must identify all output artifact keys with
    descriptions of what each artifact contains.
22. REQ-022: The requirements must identify context variables (e.g.,
    PRODUCT_SOURCE_DIR as user input, GOVERNANCE_RUNTIME_ROOT as standard
    runtime injection).

### 2.4 Constraints and Dependencies

23. REQ-023: The requirements must document all constraints from the spec:
    factual accuracy priority, conflict identification, knowledge gap
    representation, downstream agnosticism, slug naming, incremental update
    support.
24. REQ-024: The requirements must document external dependencies (e.g.,
    runner artifact resolution mechanism, WorkflowExtensions interface).

### 2.5 Self-Validation

25. REQ-025 (SELF-VALIDATION): The requirements document must include a
    Self-Validation section that checks coverage before reporting APPROVED.
    The section must verify: (a) all spec objectives are captured, (b) all
    inputs/outputs identified, (c) all constraints documented, (d) inferences
    are justified.
26. REQ-026 (SELF-VALIDATION): If gaps are found during self-validation, the
    document must report REJECTED with specifics about what is missing or
    needs revision, not silently ignore gaps.
27. REQ-027 (SELF-VALIDATION): The Self-Validation section must include
    concrete pass/fail results for each check, not just a statement that
    validation was performed.


## 3. Criteria for gatekeep_requirements Step

### 3.1 Completeness

1. GKR-001: The gatekeeper must verify that ALL spec objectives are covered
   by the requirements. Specifically: knowledge consolidation from diverse
   sources, five standard sections, additional sections proposal, source
   attribution, incremental updates, downstream agnosticism.
2. GKR-002: The gatekeeper must verify that every constraint from the spec
   has a corresponding requirement: factual accuracy priority, conflict
   identification, knowledge gap representation, slug naming, extensibility.
3. GKR-003: The gatekeeper must verify that all input artifacts are
   identified (PRODUCT_SOURCE_DIR, PRODUCT_MASTER_FILE as optional input).
4. GKR-004: The gatekeeper must verify that all output artifacts are
   identified with sufficient description for downstream steps.

### 3.2 Approach Validity

5. GKR-005: The gatekeeper must evaluate whether the inferred workflow type
   is appropriate for the spec's problem domain (knowledge synthesis from
   diverse file types).
6. GKR-006: The gatekeeper must evaluate whether the proposed step sequence
   is the most appropriate decomposition for this type of workflow. If
   sections are generated independently, is the routing correct? If a
   scanning action is proposed, is it truly deterministic?
7. GKR-007: The gatekeeper must check that inferences are justified with
   evidence, not assertions. Each inference should have a "why this and not
   alternatives" explanation.

### 3.3 Downstream Feasibility

8. GKR-008: The gatekeeper must verify that the requirements contain
   sufficient detail for the define_artifacts step to define artifact paths
   and contracts.
9. GKR-009: The gatekeeper must verify that the requirements contain
   sufficient detail for the design_steps step to define step sequence,
   routing, and artifact bindings.
10. GKR-010: The gatekeeper must verify that custom action descriptions
    (if any) contain enough implementation detail for code generation.

### 3.4 Constraint Satisfaction

11. GKR-011: The gatekeeper must verify that all spec constraints are
    respected: no downstream assumptions, factual accuracy priority,
    knowledge gap representation, incremental update support.
12. GKR-012: The gatekeeper must verify that no scope has been invented
    beyond what the spec describes (no extra sections, no extra inputs,
    no extra processing steps not justified by the spec).

### 3.5 Evidence and Verdict

13. GKR-013: The gatekeeper verdict (APPROVED or REJECTED) must be
    justified with specific evidence from the requirements document and
    the spec, not just assertions like "looks good."
14. GKR-014: If REJECTED, the gatekeeper must identify specific gaps or
    issues with enough detail for the analyze_spec step to fix them.
    Generic feedback like "needs more detail" is insufficient.
15. GKR-015: The gatekeeper report must include a structured validation
    results section (table or list) showing each check area and its
    pass/fail status.

### 3.6 Loop Validity

16. GKR-016: If REJECTED, the gatekeeper must route back to the
    analyze_spec step (via on_reject_refine) with specific remediation
    instructions.
17. GKR-017: The gatekeeper must not reject for stylistic preferences
    when the requirements are semantically correct and complete.


## 4. Criteria for define_artifacts Step

### 4.1 Coverage

1. ART-001: Every output artifact identified in the requirements must have
   a corresponding artifact key with a path pattern defined in the contract.
2. ART-002: Every input artifact from the requirements must be documented
   in the contract with its type, source, and required/optional status.
3. ART-003: Shared artifacts (e.g., REVIEW_FILE_SUGGESTED for review/refine
   loops) must be documented with their dual role (producer and consumer).

### 4.2 WORKFLOW_ACTIONS Conditional

4. ART-004: If the requirements declare any action-driven steps (custom
   actions), the artifact contract must include a WORKFLOW_ACTIONS artifact
   key referencing the actions.py path. This is the conditional requirement
   for action code.
5. ART-005: If no action-driven steps are declared in the requirements,
   WORKFLOW_ACTIONS must NOT be included (no unnecessary artifacts).

### 4.3 Placeholder Validity

6. ART-006: Path patterns must use correct placeholders: {job_id} for job
   identifier, {slug} for product name slug, {date} for run date, {seq}
   for auto-incrementing sequence, {iter} for iteration numbers.
7. ART-007: Placeholders must not be misspelled or use non-standard names
   (e.g., {JOB_ID} instead of {job_id}).
8. ART-008: The {slug} placeholder must be documented as derived from
   PRODUCT_SOURCE_DIR directory name.

### 4.4 Path Patterns

9. ART-009: All artifact paths must be relative to the project root
   (e.g., docs/repo/product/runs/{job_id}/...). No absolute paths.
10. ART-010: Path patterns must follow conventions: consistent base
    directory, date/seq/slug components where appropriate, hyphen-separated
    type prefixes in filenames.
11. ART-011: Filename patterns must be consistent across all artifacts
    from the same workflow (same base directory, same slug source, same
    date format).

### 4.5 Self-Validation

12. ART-012 (SELF-VALIDATION): The artifact contract must include a
    Self-Validation section that checks: (a) all requirements artifacts
    have path patterns, (b) WORKFLOW_ACTIONS is included if action steps
    exist, (c) placeholders are valid, (d) paths are relative.
13. ART-013 (SELF-VALIDATION): The Self-Validation results must be
    documented with concrete pass/fail for each check.


## 5. Criteria for gatekeep_artifacts Step

### 5.1 Coverage

1. GKA-001: The gatekeeper must verify that ALL artifacts from the
   requirements have corresponding entries in the contract. Count the
   artifacts in both documents and confirm they match.
2. GKA-002: The gatekeeper must verify that artifact descriptions in the
   contract are consistent with the requirements descriptions.

### 5.2 Action Artifacts

3. GKA-003: If the requirements declare action-driven steps, the
   gatekeeper must verify that WORKFLOW_ACTIONS artifact key exists in
   the contract with a valid path pattern (e.g.,
   workflows/{slug}/actions.py).
4. GKA-004: If no action steps are declared, the gatekeeper must verify
   that WORKFLOW_ACTIONS is NOT present (preventing scope creep).

### 5.3 Placeholder Completeness

5. GKA-005: The gatekeeper must validate that all path patterns use
   valid placeholders ({job_id}, {slug}, {date}, {seq}, {iter}) and
   that each placeholder is documented.
6. GKA-006: The gatekeeper must verify that sequence auto-increment
   ({seq}) is applied where needed (e.g., PRODUCT_MASTER_FILE to prevent
   overwrites).

### 5.4 Path Validity

7. GKA-007: The gatekeeper must verify that all paths are relative
   (no absolute paths like D:/ or C:/).
8. GKA-008: The gatekeeper must verify that all paths follow the
   convention of being under a docs/repo/... or workflows/... base
   directory.

### 5.5 Chain Integrity

9. GKA-009: The gatekeeper must verify that artifact flow from inputs
   to outputs is unbroken: every output artifact has a clear producer,
   every required input has a clear source (prior step output or
   declared input).
10. GKA-010: The gatekeeper must verify no orphan artifacts (artifacts
    defined in the contract but not consumed by any step) unless
    justified as final deliverables.


## 6. Criteria for design_steps Step

### 6.1 Coverage

1. STP-001: The step sequence must implement ALL requirements. Every
   output artifact must have a producing step. Every constraint must
   be enforceable through the step design.
2. STP-002: The step sequence must cover all spec objectives: scanning,
   knowledge generation for each section, assembly, review, refinement,
   completion.
3. STP-003: If gatekeeper steps are included (as per the gatekeeper QC
   pipeline pattern), they must be placed after each major producer step.

### 6.2 Artifact Flow

4. STP-004: The artifact flow must be traceable from inputs to outputs.
   For each step, its required_inputs must be satisfied by either a
   declared input artifact or a prior step's produces.
5. STP-005: The complete chain must be unbroken: INPUT -> scan -> section
   gen -> assembly -> review -> (refine) -> OUTPUT. Every intermediate
   artifact must be produced and consumed exactly once (except shared
   artifacts like REVIEW_FILE_SUGGESTED).
6. STP-006: The assemble step must have ALL section artifacts as
   required_inputs (or it must read them through some other mechanism
   documented in the step details).

### 6.3 Routing Validity

7. STP-007: Every step must have a valid onsuccess routing target that
   references an existing step name.
8. STP-008: Refinement loops must be correctly configured:
   on_reject_refine.step must point to the refine step,
   on_reject_refine.artifact must name the artifact being refined,
   on_reject_refine.max_iterations must be set.
9. STP-009: Refine steps must have loop_returns_to pointing back to the
   review/gatekeeper step for re-evaluation.
10. STP-010: The last step must be stepCompletion with
    action = "step_completion" (terminal step).

### 6.4 Step Type Appropriateness

11. STP-011: Prompt vs action classification must be correct. Deterministic
    file operations (directory scanning, file classification) must be
    action-driven. Knowledge synthesis, analysis, and document generation
    must be prompt-driven.
12. STP-012: Review and gatekeeper steps must be prompt-driven (they
    require LLM judgment to evaluate quality).
13. STP-013: Action steps must not have prompt files. Prompt steps must
    not have action functions.

### 6.5 Action Consistency

14. STP-014: If action steps are declared, the action names must match
    the custom action descriptions in the requirements. The action must
    do what the requirements describe.
15. STP-015: Action step artifact bindings must be consistent with the
    action's declared inputs and outputs in the requirements.

### 6.6 Review Loop Design

16. STP-016: Review/refine loops must have proper on_reject_refine
    configuration with step, artifact, max_iterations, and
    exhausted_failure_code/exhausted_failure_class.
17. STP-017: The loop must have a termination condition (max_iterations)
    to prevent infinite loops.
18. STP-018: If multiple review points exist (e.g., per-section review
    plus final review), each must have its own loop configuration.

### 6.7 Self-Validation

19. STP-019 (SELF-VALIDATION): The step architecture document must include
    a Self-Validation section checking: (a) routing validity (all onsuccess
    targets exist), (b) artifact flow completeness (no broken chains),
    (c) all requirements covered by steps, (d) loop configurations valid.
20. STP-020 (SELF-VALIDATION): The Self-Validation results must show
    concrete pass/fail for each check, with specifics on any issues found.


## 7. Criteria for gatekeep_steps Step

### 7.1 Coverage

1. GKS-001: The gatekeeper must verify that ALL requirements have
   corresponding steps. Count requirements vs steps and confirm coverage.
2. GKS-002: The gatekeeper must verify that all output artifacts from the
   contract have producing steps.
3. GKS-003: The gatekeeper must verify that all input artifacts are
   consumed by at least one step (or are declared as optional and handled
   correctly).

### 7.2 Data Flow

4. GKS-004: The gatekeeper must verify that every step's required_inputs
   are satisfied by prior produces or declared inputs. No step should
   require an artifact that no prior step produces.
5. GKS-005: The gatekeeper must verify the artifact chain from start to
   end: inputs flow through scanning, through generation, through assembly,
   through review, to final output. No broken links.
6. GKS-006: The gatekeeper must verify that optional inputs (e.g.,
   PRODUCT_MASTER_FILE for incremental updates) are handled correctly
   -- they must not block execution if absent.

### 7.3 Routing Validity

7. GKS-007: The gatekeeper must verify that all onsuccess values reference
   valid step names that exist as [[step]] definitions.
8. GKS-008: The gatekeeper must verify that all loop_returns_to values
   reference valid step names.
9. GKS-009: The gatekeeper must verify that all on_reject_refine.step
   values reference valid step names.
10. GKS-010: The gatekeeper must verify that the workflow ends with
    stepCompletion (terminal step).

### 7.4 Type Consistency

11. GKS-011: The gatekeeper must verify that step types match task nature.
    File scanning/classification should be action-driven. Knowledge
    synthesis should be prompt-driven. Review/gatekeeping should be
    prompt-driven.
12. GKS-012: The gatekeeper must verify that role policies are appropriate
    for each step type (architect_standard for generation, reviewer_standard
    for review, validation_standard for gatekeepers).

### 7.5 Loop Validity

13. GKS-013: The gatekeeper must verify that review/refine loops are
    properly configured with max_iterations, exhausted_failure_code, and
    loop_returns_to.
14. GKS-014: The gatekeeper must verify that no step is trapped in an
    unresolvable routing state (every path must eventually reach
    stepCompletion or a failure condition).


## 8. Criteria for generate_package Step

### 8.1 Principles-Based Generation

1. GEN-001: The generation must follow a principles-based approach: infer
   the required files from the step architecture and artifact contract,
   not from a fixed numbered task list.
2. GEN-002: The generation must include a file ONLY if the design calls
   for it. No unnecessary files (e.g., no actions.py if no action steps
   exist, no .env.sample if no environment variables needed).
3. GEN-003: The generation must not omit files that the design requires.
   If action steps exist, actions.py must be generated. If prompt steps
   exist, prompt files must be generated.

### 8.2 File Completeness

4. GEN-004: workflow.toml must exist and be valid TOML. It must contain:
   [workflow] metadata (name, version, label, job_prefix, init_step),
   [[step]] definitions for every step in the step architecture, with
   correct routing (onsuccess), artifact bindings, and coder roles.
5. GEN-005: context_extensions.py must exist. It must define a class
   extending WorkflowExtensions, set workflow_name correctly, implement
   register_artifact_keys() with all artifact keys from the contract,
   and implement build_context_extensions() resolving all paths to
   absolute.
6. GEN-006: If action steps exist in the step architecture, actions.py
   must exist with complete @action implementations. Each action function
   must contain actual logic, not stubs.
7. GEN-007: prompts/ directory must contain one .txt file per
   prompt-driven step. Each prompt file must be referenced by the
   corresponding [[step]] in workflow.toml.
8. GEN-008: README.md must exist with: step reference table, artifact key
   listing, workflow description, usage instructions.

### 8.3 Conditional Files

9. GEN-009: .env.sample must be generated ONLY if the workflow requires
   environment variables (e.g., API keys). If the workflow has no
   external service dependencies, .env.sample must NOT be generated.
10. GEN-010: config.json.sample must be generated ONLY if the workflow
    requires runtime configuration. If not needed, it must NOT be
    generated.
11. GEN-011: bundle_governance.toml is optional. It should be generated
    only if the design calls for backend sync validation. The spec does
    not explicitly require it.
12. GEN-012: install.py should be generated only if the design calls for
    global installation hooks. The spec does not explicitly require it.

### 8.4 workflow.toml Specifics

13. GEN-013: The workflow name in workflow.toml must match the directory
    name exactly (product_master_gen_v2).
14. GEN-014: onsuccess must be at [[step]] top level, NOT under
    [step.artifacts].
15. GEN-015: promotes (if any promote steps exist) must be at [[step]]
    top level, NOT under [step.artifacts].
16. GEN-016: The init_step must reference the first step in the sequence.
17. GEN-017: The last [[step]] must be stepCompletion with
    action = "step_completion".

### 8.5 context_extensions.py Specifics

18. GEN-018: register_artifact_keys() must return mappings for ALL
    artifact keys from the contract, with relative paths.
19. GEN-019: build_context_extensions() must resolve ALL paths to
    absolute using workspace_root.
20. GEN-020: build_context_extensions() must handle project_root=None
    with fallback to get_workspace_root() or Path.cwd().
21. GEN-021: If slug extraction is needed, it must use a proper
    implementation (e.g., from PRODUCT_SOURCE_DIR basename).
22. GEN-022: If sequence auto-increment is needed, it must use
    resolve_next_seq() from agent_runner_v2.constants.

### 8.6 Prompt File Specifics

23. GEN-023: Each prompt must use bare {ARTIFACT_KEY} placeholders
    (not backtick-wrapped).
24. GEN-024: Each prompt must be ASCII-only content.
25. GEN-025: Each prompt must include: Objective, Reference Inputs,
    Artifacts, and Output Instructions sections.
26. GEN-026: Each prompt must explicitly instruct the LLM to write
    content to files using file-writing tools, not put content in the
    meta.json result field.

### 8.7 Self-Validation

27. GEN-027 (SELF-VALIDATION): The generation step must include a
    Self-Validation section checking: (a) file completeness (all files
    from the design are present), (b) design fidelity (files match the
    step architecture and artifact contract), (c) no orphan or missing
    files, (d) cross-file consistency (artifact keys match across
    workflow.toml, context_extensions.py, and prompts).
28. GEN-028 (SELF-VALIDATION): The Self-Validation results must be
    documented with concrete pass/fail for each check.


## 9. Criteria for gatekeep_package Step

### 9.1 File Checklist

1. GKP-001: The gatekeeper must verify ALL expected files exist:
   workflow.toml, context_extensions.py, and any conditional files
   (actions.py, prompts/, README.md, .env.sample, config.json.sample).
2. GKP-002: The gatekeeper must cross-reference the file list against
   the step architecture to ensure no files are missing.

### 9.2 Action Completeness

3. GKP-003: If the step architecture declares action-driven steps, the
   gatekeeper must verify that actions.py exists and contains actual
   @action implementations (not stubs or placeholder comments).
4. GKP-004: The gatekeeper must verify that each @action function name
   matches the action name declared in the corresponding [[step]] in
   workflow.toml.
5. GKP-005: If no action steps are declared, the gatekeeper must verify
   that actions.py does NOT exist (preventing scope creep).

### 9.3 Design Fidelity

6. GKP-006: The gatekeeper must verify that workflow.toml step
   definitions match the step architecture document exactly: step names,
   routing targets, artifact bindings, role policies, loop configurations.
7. GKP-007: The gatekeeper must verify that context_extensions.py
   artifact keys match the artifact contract exactly: same keys, same
   path patterns.
8. GKP-008: The gatekeeper must verify that prompt file content matches
   the step descriptions: each prompt instructs the LLM to produce the
   correct artifact with the correct content scope.

### 9.4 Prompt Completeness

9. GKP-009: The gatekeeper must verify that prompts/ has exactly one
   file per prompt-driven step (no missing prompts, no extra prompts).
10. GKP-010: The gatekeeper must verify that each prompt file path
    referenced in workflow.toml actually exists on disk.

### 9.5 Scope Check

11. GKP-011: The gatekeeper must detect scope shrink: elements from the
    step architecture or artifact contract that are missing in the
    generated package.
12. GKP-012: The gatekeeper must detect scope creep: files or features
    in the generated package that are NOT in the step architecture or
    artifact contract (e.g., unnecessary .env.sample, extra prompts).
13. GKP-013: The gatekeeper verdict must cite specific evidence for any
    scope discrepancies found.


## 10. Criteria for validate_bundle Step

### 10.1 Structural Checks

1. VAL-001: workflow.toml must parse as valid TOML without errors.
2. VAL-002: The [workflow] table must contain: name (matching directory),
   version, label, job_prefix, and init_step.
3. VAL-003: Every [[step]] must have a name field.
4. VAL-004: Every prompt-driven [[step]] must have a prompt field pointing
   to a file that exists under prompts/.
5. VAL-005: Every action-driven [[step]] must have an action field.
6. VAL-006: The init_step value must match the name of the first [[step]].
7. VAL-007: The last [[step]] must be stepCompletion with
   action = "step_completion".
8. VAL-008: All onsuccess values must reference valid step names.
9. VAL-009: All loop_returns_to values must reference valid step names.
10. VAL-010: All on_reject_refine.step values must reference valid step
    names.

### 10.2 Semantic Checks

11. VAL-011: Action functions in actions.py must contain actual logic,
    not stubs or placeholders. Verify by: each action function body must
    contain more than a return statement with hardcoded values.
12. VAL-012: Each prompt file must contain substantive instructions (not
    empty or boilerplate). Each must reference at least one artifact key
    placeholder.
13. VAL-013: context_extensions.py must contain a valid class inheriting
    from WorkflowExtensions with workflow_name set correctly.

### 10.3 Artifact Registration Checks

14. VAL-014: Every artifact key in [step.artifacts].produces must have
    a corresponding entry in context_extensions.py register_artifact_keys().
15. VAL-015: Every artifact key in [step.artifacts].required_inputs must
    either be produced by a prior step or be a declared input artifact.
16. VAL-016: The result_meta_key on each step must match one of the keys
    in that step's produces list.
17. VAL-017: Artifact keys are case-sensitive -- no mismatches between
    workflow.toml and context_extensions.py.

### 10.4 File Completeness

18. VAL-018: The package must contain all required files: workflow.toml,
    context_extensions.py, prompts/ (if prompt steps exist), actions.py
    (if action steps exist).
19. VAL-019: Every prompt file referenced in workflow.toml must exist
    at the specified relative path.
20. VAL-020: No prompt file should exist that is not referenced by any
    step (no orphan prompts).
21. VAL-021: The package must NOT contain unnecessary files (no install.py
    unless justified, no bundle_governance.toml unless justified).


## 11. Criteria for review_package Step

### 11.1 Spec Fulfillment

1. REV-001: The generated workflow must implement the complete end-to-end
   flow: source scanning/inventory -> knowledge generation for each section
   -> assembly into Product Master -> review -> (refine) -> completion.
2. REV-002: The workflow must produce the Product Master document with:
   YAML frontmatter (product name, source count, completeness), table of
   contents, knowledge sections, source attribution.
3. REV-003: All five standard knowledge sections must be covered:
   Product Information, Target Audience, Benefits/USP, Marketing Assets,
   Additional Sections.
4. REV-004: The workflow must support incremental updates (merge +
   changelog) when PRODUCT_MASTER_FILE is provided as input.
5. REV-005: The workflow must be downstream-agnostic (no campaign, media,
   or marketing deployment assumptions in any step or prompt).

### 11.2 Step-by-Step Verification

6. REV-006: Each step must do what the spec describes for that phase.
   Verify by reading the step's prompt or action code and confirming it
   covers the expected content domains.
7. REV-007: The scan/inventory step (if action-driven) must classify
   files correctly per the spec's source types.
8. REV-008: Each section generation step must read the scan report
   and source files, not other sections' output.
9. REV-009: The assembly step must read all section artifacts and produce
   the assembled Product Master with proper frontmatter and structure.
10. REV-010: URL content fetching must be supported (URL files contain
    one URL per line, LLM processes them during generation).

### 11.3 Data Flow

11. REV-011: Information must flow correctly between steps. Verify by
    tracing required_inputs and produces through the step sequence:
    scan report feeds section generation, section artifacts feed assembly,
    assembly feeds review.
12. REV-012: Optional inputs (PRODUCT_MASTER_FILE for incremental mode)
    must flow to the correct step (assembly or equivalent).

### 11.4 No Hallucinations

13. REV-013: The workflow must NOT include steps for campaign generation,
    media creation, or marketing deployment.
14. REV-014: The workflow must NOT hardcode product-specific data or
    assume a specific product type.
15. REV-015: The workflow must NOT require inputs beyond
    PRODUCT_SOURCE_DIR (required) and PRODUCT_MASTER_FILE (optional).
16. REV-016: The workflow must NOT include unnecessary API keys,
    authentication, or external service calls beyond standard LLM
    prompt invocations and URL fetching.
17. REV-017: The workflow must NOT invent standard sections beyond what
    the spec describes (five sections maximum as standard; additional
    sections are LLM-proposed per product).

### 11.5 Gatekeeper Effectiveness

18. REV-018: Review whether the gatekeeper steps caught issues early,
    or whether issues only surfaced at final review. If gatekeepers
    approved artifacts with obvious defects, the gatekeeper prompts may
    need improvement.
19. REV-019: Check if gatekeeper verdicts included specific evidence.
    Generic approvals ("looks good") suggest the gatekeepers did not
    perform thorough validation.


## 12. Criteria for refine_package Step

### 12.1 Completeness

1. RFN-001: The refine step must be able to fix ALL types of issues
   flagged in the review: structural problems (missing files, wrong
   routing), semantic problems (incomplete actions, wrong artifact keys),
   and quality problems (vague prompts, missing sections).
2. RFN-002: The refine step must read the review critique document and
   apply specific fixes for each issue identified.

### 12.2 actions.py Handling

3. RFN-003: If the review flags issues with actions.py (missing action,
   incomplete logic, wrong error handling), the refine step must be able
   to add or update actions.py. The refine prompt must support editing
   Python code files, not just markdown documents.
4. RFN-004: The refine step must preserve existing correct code while
   fixing flagged issues (no regression).

### 12.3 Consistency

5. RFN-005: Refinement must maintain cross-file consistency. If an
   artifact key is renamed in workflow.toml, it must also be renamed
   in context_extensions.py and all prompts that reference it.
6. RFN-006: If routing is changed in workflow.toml, the step architecture
   must remain consistent (no dangling references).
7. RFN-007: The refine step must use edit_mode = "in_place" and
   target_artifact for the artifact being refined, ensuring the same
   file path is updated.


## 13. Prompt Quality Criteria

### 13.1 Output Mechanism Clarity

1. PQ-001: Each prompt must explicitly instruct the LLM to use
   file-writing tools (e.g., write tool) to create actual files on
   disk at the paths specified by artifact placeholders.
2. PQ-002: Each prompt must explicitly state that the meta.json result
   field is for status/summary text ONLY, not for artifact content.
   Acceptable phrasing: "Write content to the file at {ARTIFACT_KEY}.
   The result field in meta.json must contain a brief summary only."
3. PQ-003: Each prompt must NOT use ambiguous phrasing like "Write the
   output to: {ARTIFACT_KEY}" without clarifying this means writing a
   file to the resolved absolute path.
4. PQ-004: Prompts should include explicit instruction: "Write the
   generated content to the file at {ARTIFACT_KEY}" where the
   placeholder resolves to an absolute path.

### 13.2 Ambiguity Check

5. PQ-005: No prompt should contain phrases that could be interpreted
   as "put the content in the result field" rather than "write a file."
   Test: Could an LLM reasonably interpret the instruction as putting
   markdown content into meta.json's result string?
6. PQ-006: Prompts must use "Write the file to {KEY}" or "Create the
   document at {KEY}" -- never just "Output: {KEY}" which is ambiguous.
7. PQ-007: Prompts must specify exactly which source files to consult
   (via the scan report), not leave it to the LLM to guess what
   "relevant sources" means.
8. PQ-008: Assembly/generation prompts must specify the exact sections,
   frontmatter fields, and structure required, not use vague terms
   like "organize appropriately."
9. PQ-009: Review/gatekeeper prompts must specify concrete evaluation
   criteria (completeness, technical soundness, downstream feasibility,
   constraint satisfaction), not just "review the document."
10. PQ-010: Refine prompts must specify how to handle each type of
    review finding, not just "improve the document."

### 13.3 Common LLM Mistake Guards

11. PQ-011: Prompts must guard against the LLM putting document content
    in the meta.json result field instead of writing files. Include
    explicit instruction: "Write content to files, not to the meta.json
    result field."
12. PQ-012: Section generation prompts must guard against fabricating
    product data when sources do not contain it. Include explicit
    instruction: "If information is not found in any source file,
    represent it as a knowledge gap."
13. PQ-013: Assembly prompts must guard against silently dropping
    sections. Include instruction: "Include ALL section artifacts. If
    a section is empty or a stub, include it with a note."
14. PQ-014: Prompts for multi-file steps must guard against skipping
    index file creation when applicable.
15. PQ-015: Section generation prompts must guard against scope creep --
    each section prompt must clearly scope what content belongs in that
    section and what does not.
16. PQ-016: Gatekeeper prompts must guard against rubber-stamping.
    Include instruction: "You must find specific evidence for each
    validation check. If you cannot find evidence, the check fails."

### 13.4 Completeness

17. PQ-017: Each prompt must specify the required output format
    (markdown with YAML frontmatter where applicable, ASCII-only).
18. PQ-018: Each prompt must specify filename patterns using the slug
    placeholder where applicable.
19. PQ-019: Assembly prompts must specify all required frontmatter
    fields (product name, source count, completeness rating at minimum).
20. PQ-020: Refine prompts must specify that the output replaces the
    target artifact in-place (same file path, updated content).
21. PQ-021: Each prompt must include a Reference Inputs section listing
    all input artifacts using bare {ARTIFACT_KEY} placeholders.
22. PQ-022: Each prompt must include an Artifacts section listing all
    output artifacts using bare {ARTIFACT_KEY} placeholders.
23. PQ-023: Additional Sections prompts must specify what to do when no
    additional sections are warranted (produce a stub document stating
    so, not skip the artifact).

### 13.5 Self-Validation in Prompts

24. PQ-024: Each producer prompt (analyze, define, design, generate)
    must include a Self-Validation section that instructs the LLM to
    check its output against specific criteria before reporting APPROVED.
25. PQ-025: The Self-Validation section must include explicit
    instructions: (a) list specific checks, (b) if any check fails,
    revise the output, (c) re-run validation, (d) only report APPROVED
    when all checks pass.
26. PQ-026: The Self-Validation section must instruct the LLM to include
    a "Self-Validation Results" section in the output documenting which
    checks passed/failed and any revisions made.
27. PQ-027: The Self-Validation section must NOT be merely decorative.
    It must include actionable criteria, not just "validate your output."


## 14. Audit Criteria

### 14.1 Security Audit

The spec involves URL fetching (LLM retrieves web content from URL files)
but does not involve API keys, authentication, credentials, or secrets
in the workflow logic itself.

1. SEC-001: When processing URL files, the prompts must instruct the LLM
   to use the webfetch tool (or equivalent) to retrieve URL content.
   The LLM must not execute arbitrary URLs as code.
2. SEC-002: Any file scanning action must not execute or interpret file
   contents -- it only classifies by extension and filename pattern.
   No file content processing at the action level.
3. SEC-003: No credentials, API keys, or tokens should appear in any
   generated artifact or log output. The workflow has no authentication
   requirements beyond standard LLM coder invocation.
4. SEC-004: If the workflow design introduces environment variables
   (e.g., for external service access), they must be loaded from .env
   file, not hardcoded in any generated file.

### 14.2 Logic Audit

The spec involves retry/error handling (review/refine loops), conditional
branching (incremental updates vs fresh generation, additional sections
warranted vs stub), and state management (artifact flow between steps).

5. LOG-001: Review/refine loops must have a maximum iteration count
   (via on_reject_refine.max_iterations) to prevent infinite loops.
6. LOG-002: The on_reject_refine configuration must specify
   exhausted_failure_code and exhausted_failure_class for when
   refinement iterations are exhausted.
7. LOG-003: Refine steps must use edit_mode = "in_place" and
   target_artifact to correctly update the artifact in-place.
8. LOG-004: Refine steps must have loop_returns_to pointing back to
   the review step to create the correct loop routing.
9. LOG-005: The workflow must handle the case where ADDITIONAL_SECTIONS
   is a stub (no additional sections warranted) -- assembly must not
   fail when this section is minimal.
10. LOG-006: The workflow must handle incremental updates correctly:
    when PRODUCT_MASTER_FILE is provided as optional input, assembly
    must produce a Changelog. When not provided, no Changelog section.
11. LOG-007: If a custom scanning action exists, it must handle:
    directory not found (REJECTED with clear error), empty directory
    (REJECTED with "No source files found"), permission errors (REJECTED
    with descriptive message). No unhandled exceptions.

### 14.3 Data Integrity Audit

The spec involves file operations (scanning directories, writing section
artifacts, assembling documents), index tracking (scan report as file
inventory), and batch processing (multiple source files processed into
multiple output artifacts).

12. DAT-001: Section generation steps must write complete files, not
    partial or truncated content. Each section file must contain content
    covering all the topics listed in the spec for that section.
13. DAT-002: The assembled Product Master must include content from ALL
    section artifacts. Verify by: check that each section's key topics
    appear in the final document.
14. DAT-003: Source attribution in the Product Master must reference
    actual files from the source directory. Verify by: cross-reference
    source citations against the scan report file inventory.
15. DAT-004: For incremental updates, the Changelog must accurately
    reflect what changed between old and new Product Master. Verify by:
    compare old input against new output and check Changelog entries
    match the differences.
16. DAT-005: Slug extraction must produce consistent naming across all
    artifacts. Verify by: all output filenames must use the same slug
    value derived from PRODUCT_SOURCE_DIR directory name.
17. DAT-006: Sequence numbers in PRODUCT_MASTER_FILE must auto-increment
    correctly via resolve_next_seq().
18. DAT-007: If a scanning action exists, its report must list every
    file found. File classifications must match the spec's rules.
    Summary counts must be consistent with the file listing.
19. DAT-008: The workflow must handle partial failure gracefully. If
    some source files are unreadable (corrupt PDFs, broken URLs),
    section generation should proceed with available sources, noting
    gaps rather than failing entirely.

### 14.4 Audit Exclusions

The spec does not involve:
- Payment processing or financial data
- Personally identifiable information (PII) handling
- Database write operations
- Concurrent file access or locking requirements

These areas do not require additional audit criteria for this workflow.


## Appendix A: Verification Quick Reference

To verify a criterion, use the following approach:

- REQ-xxx: Read the REQUIREMENTS document. Check each statement against
  the spec. Verify inference justifications.
- GKR-xxx: Read the GATEKEEP_REQUIREMENTS report. Check that verdict
  is evidence-based and specific.
- ART-xxx: Read the ARTIFACTS contract. Verify all requirements artifacts
  have path patterns. Check WORKFLOW_ACTIONS conditional.
- GKA-xxx: Read the GATEKEEP_ARTIFACTS report. Verify coverage checks
  and chain integrity assessment.
- STP-xxx: Read the STEPS architecture document. Trace artifact flow
  and routing. Check Self-Validation results.
- GKS-xxx: Read the GATEKEEP_STEPS report. Verify data flow and routing
  validation.
- GEN-xxx: Read the generated workflow package files. Verify file
  completeness and design fidelity.
- GKP-xxx: Read the GATEKEEP_PACKAGE report. Verify file checklist and
  scope check.
- VAL-xxx: Run structural checks on workflow.toml and cross-reference
  with context_extensions.py and actions.py.
- REV-xxx: Trace data flow through the complete workflow. Verify spec
  fulfillment.
- RFN-xxx: Verify refine step can fix all flagged issues while
  maintaining consistency.
- PQ-xxx: Read each prompt file. Check clarity, completeness, ambiguity
  guards, and Self-Validation sections.
- SEC-xxx: Verify no credentials appear in any generated file. Check
  URL handling safety.
- LOG-xxx: Read workflow.toml for loop/routing configuration. Read
  actions.py for error handling.
- DAT-xxx: Trace artifact paths and naming patterns through
  context_extensions.py. Verify data flow integrity.


## Appendix B: V2 Enhancement Checklist

The following criteria are specific to the v2 enhanced architecture.
Each must be verified in the generated workflow:

1. V2-001: Gatekeeper QC steps exist between each major producer step
   (gatekeep_requirements, gatekeep_artifacts, gatekeep_steps,
   gatekeep_package).
2. V2-002: Each gatekeeper has on_reject_refine routing back to its
   corresponding producer step.
3. V2-003: Each gatekeeper uses validation_standard role policy.
4. V2-004: Each producer step prompt includes a Self-Validation section
   with specific, actionable criteria.
5. V2-005: The generate_package step uses principles-based generation
   (infers files from design, not fixed task list).
6. V2-006: The analyze_spec step performs inference validation --
   justifying workflow type, step sequence, and custom actions with
   evidence, not assertions.
7. V2-007: Gatekeeper verdicts include specific evidence, not just
   pass/fail assertions.
8. V2-008: The workflow builder had discretion over architecture
   decisions (section generation strategy, QC placement, review
   strategy, action steps, artifact structure, routing) and the
   resulting design is sound.
