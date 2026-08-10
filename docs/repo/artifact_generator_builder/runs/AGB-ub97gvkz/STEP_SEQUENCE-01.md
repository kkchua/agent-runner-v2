---
doc_type: "step_sequence"
identity_locked: true
generator_name: "codebase_intelligence"
version: "1.0.0"
source_artifact_contract: "ARTIFACT_CONTRACT-01"
source_runtime_impl: "RUNTIME_IMPL-01"
source_composition_spec: "COMPOSITION_SPEC-01"
job_id: "AGB-ub97gvkz"
generated_at: "2026-08-10"
total_steps: 19
output_type: "pipeline_execution"
review_loop_count: 1
recovery_loop_count: 0
approval_gate_count: 0
phase_count: 6
---

# Step Sequence

## Target Identity Reference

The following identity values are sourced from the upstream design artifacts
(RUNTIME_IMPL-01, COMPOSITION_SPEC-01, ARTIFACT_CONTRACT-01) and are
locked for this generated workflow. All step definitions in this document
inherit these identity constraints.

| Field | Value |
|---|---|
| generator_name | codebase_intelligence |
| version | 1.0.0 |
| output_type | pipeline_execution |
| input_artifacts | SOURCE_CODEBASE_DIR, AUDIENCES_DIR, CONFIG_FILE |
| output_artifacts | AUDIENCE_META_CONTENT, STRUCTURAL_HEALTH_REPORT, SECURITY_AUDIT_REPORT, RUN_MANIFEST |

Identity is locked: no downstream configuration may override or substitute
these values.

---

## Phase Overview

The generated codebase_intelligence workflow decomposes into 6 phases.
Phase 1 handles input preparation and configuration. Phase 2 executes
Layer 1 input parsing stages (TS-001, TS-002). Phase 3 executes Layer 2
analysis stages (TS-003, TS-004, TS-005). Phase 4 performs findings
report assembly (TS-006). Phase 5 validates outputs (TS-007) and performs
quality review. Phase 6 handles rendering, delivery, and completion.

Each phase maps directly to the runtime implementation architecture
described in RUNTIME_IMPL-01 and the transformation pipeline defined in
COMPOSITION_SPEC-01.

| Phase | Name | Step Count | Step Types |
|---|---|---|---|
| 1 | Input Preparation | 2 | 2 action |
| 2 | Input Parsing (Layer 1) | 4 | 4 action |
| 3 | Analysis (Layer 2) | 6 | 6 action |
| 4 | Findings Assembly | 2 | 2 action |
| 5 | Validation and Review | 3 | 2 action, 1 prompt |
| 6 | Delivery | 2 | 2 action |

Total primary steps: 19 (18 action, 1 prompt).
Total steps including auxiliary: 20 (18 action, 2 prompt).

Step type distribution across all phases:

| Step Type | Count | Description |
|---|---|---|
| action | 18 | Deterministic Python steps (parsing, analysis, validation, rendering, promotion) |
| prompt | 2 | LLM-driven quality review and parameter adjustment |

---

## Step Definitions

Every step in the generated workflow is defined below. Each step has a
unique name, a type (action or prompt), routing configuration, and a
role_policy for prompt-driven coder assignment.

### Phase 1: Input Preparation

| # | Step Name | Type | onsuccess | on_reject_refine | Role Policy |
|---|---|---|---|---|---|
| 1 | validate_input | action | prepare_configuration | -- | (action) |
| 2 | prepare_configuration | action | scan_codebase | -- | (action) |

Phase 1 validates the external input artifacts and constructs the
RuntimeConfig dataclass for pipeline execution.

Step 1 (validate_input) checks constraints V-IN-001 (files readable as
UTF-8), V-IN-002 (Python files AST-parseable), V-IN-003 (documentation
files non-empty Markdown), V-IN-004 (at least one Python package and one
documentation directory exist). Optional inputs AUDIENCES_DIR and
CONFIG_FILE are checked for existence but missing values do not halt the
pipeline.

Step 2 (prepare_configuration) creates the RuntimeConfig from the JSON
config file (IN-003), environment variables, command-line arguments, and
built-in defaults. Override precedence: CLI args > environment variables
> config file > defaults. The RuntimeConfig includes dimension settings,
phase settings, rendering format, output directory, and threshold values.

### Phase 2: Input Parsing (Layer 1)

| # | Step Name | Type | onsuccess | on_reject_refine | Role Policy |
|---|---|---|---|---|---|
| 3 | scan_codebase | action | validate_scan | -- | (action) |
| 4 | validate_scan | action | build_import_graph | -- | (action) |
| 5 | build_import_graph | action | validate_import_graph | -- | (action) |
| 6 | validate_import_graph | action | analyze_audiences | -- | (action) |

Phase 2 implements Layer 1 of the transformation pipeline: input parsing
stages TS-001 and TS-002 from RUNTIME_IMPL-01. Each stage is followed by
a dedicated invariant validation step.

Stage mapping:

| Step | Pipeline Stage | Transformation ID | Invariant Enforced |
|---|---|---|---|
| scan_codebase | TS-001: Codebase Scan | IM-001, IM-002 | INV-001, INV-002, INV-003 |
| validate_scan | TS-001 Invariant Check | -- | INV-001, INV-002, INV-003 |
| build_import_graph | TS-002: Import Graph Construction | IM-003, IM-004, IM-005 | INV-004, INV-005, INV-006 |
| validate_import_graph | TS-002 Invariant Check | -- | INV-004, INV-005, INV-006 |

Step 3 (scan_codebase) walks the SOURCE_CODEBASE_DIR recursively, creates
FileEntry components (Component 1) for each file, classifies by file_type
(documentation, source_code, configuration, other), and aggregates into
FileInventory (Component 2 / INT-001). Parse errors are recorded in
PARSE_ERRORS_LOG (INT-006).

Step 4 (validate_scan) checks INV-001 (FileInventory.entries non-empty),
INV-002 (has_python_package is true), INV-003 (has_doc_directory is true).
Critical failures halt the pipeline.

Step 5 (build_import_graph) parses all Python source files via AST
(Component 5), extracts ImportEdge components (Component 3), builds the
ImportGraph (Component 4 / INT-002), extracts SourceSymbol components
(Component 5 / INT-003), and resolves relative imports to absolute paths.
Parse errors are appended to PARSE_ERRORS_LOG (INT-006).

Step 6 (validate_import_graph) checks INV-004 (ImportGraph has nodes for
all source files), INV-005 (all relative imports resolved), INV-006
(import graph constructed from AST, not regex).

Extension protocols used per step:

| Step | Protocol | Reference |
|---|---|---|
| scan_codebase | IP-001 (InputParser.parse_file) | RUNTIME_IMPL-01 InputParser Protocol |
| build_import_graph | IP-001 (InputParser.parse_imports, parse_symbols) | RUNTIME_IMPL-01 InputParser Protocol |

### Phase 3: Analysis (Layer 2)

| # | Step Name | Type | onsuccess | on_reject_refine | Role Policy |
|---|---|---|---|---|---|
| 7 | analyze_audiences | action | validate_audiences | -- | (action) |
| 8 | validate_audiences | action | analyze_health_dimensions | -- | (action) |
| 9 | analyze_health_dimensions | action | validate_health | -- | (action) |
| 10 | validate_health | action | analyze_security_phases | -- | (action) |
| 11 | analyze_security_phases | action | validate_security | -- | (action) |
| 12 | validate_security | action | assemble_findings_reports | -- | (action) |

Phase 3 implements Layer 2 of the transformation pipeline: analysis stages
TS-003, TS-004, and TS-005 from RUNTIME_IMPL-01. In the runtime
implementation these three stages can execute in parallel; in the workflow
they execute sequentially for deterministic step ordering.

Stage mapping:

| Step | Pipeline Stage | Transformation ID | Invariant Enforced |
|---|---|---|---|
| analyze_audiences | TS-003: Audience Analysis | OM-001 | INV-007, INV-008, INV-009 |
| validate_audiences | TS-003 Invariant Check | -- | INV-007, INV-008, INV-009 |
| analyze_health_dimensions | TS-004: Health Dimension Analysis | AnalysisEngine.run_dimension | INV-010, INV-011, INV-012, INV-013 |
| validate_health | TS-004 Invariant Check | -- | INV-010, INV-011, INV-012, INV-013 |
| analyze_security_phases | TS-005: Security Phase Analysis | AnalysisEngine.run_phase | INV-014, INV-015, INV-016, INV-017, INV-018 |
| validate_security | TS-005 Invariant Check | -- | INV-014, INV-015, INV-016, INV-017, INV-018 |

Step 7 (analyze_audiences) iterates over parsed AudienceDefinition
components (Component 6) from AUDIENCES_DIR. For each audience, it filters
FileInventory entries by focus_areas, builds OutputSection components
following section_structure, applies audience tone, and produces one
OutputDocument (Component 12) per audience. If no audience definitions
are found, a default codebase overview report is produced to satisfy
INV-022 (minimum 3 output types).

Step 8 (validate_audiences) checks INV-007 (one OutputDocument per
audience), INV-008 (no hallucinated content), INV-009 (tone and structure
match audience definition).

Step 9 (analyze_health_dimensions) iterates over enabled
AnalysisDimension components (Component 7) from RuntimeConfig. For each
dimension, it uses the DIMENSION_REGISTRY to dispatch to the appropriate
analyzer: DIM-CIRCULAR (Tarjan SCC), DIM-COUPLING (fan-in/fan-out),
DIM-DEADCODE (unreferenced symbols), DIM-COMPLEXITY (cyclomatic
complexity), DIM-IMPORT (anti-pattern scan). Each produces Finding
components (Component 11) collected into HEALTH_FINDINGS (INT-004).

Step 10 (validate_health) checks INV-010 (findings cite evidence),
INV-011 (severity consistency), INV-012 (dimension independence),
INV-013 (disabled dimensions produce no findings).

Step 11 (analyze_security_phases) iterates over enabled SecurityPhase
components (Component 8) from RuntimeConfig. For each phase, it uses the
PHASE_REGISTRY to dispatch to the appropriate analyzer: PHASE-SECRETS
(pattern scan with redaction), PHASE-DEPS (vulnerability audit),
PHASE-CODEPAT (insecure pattern scan), PHASE-AUTH (auth review),
PHASE-INFRA (infrastructure check). Each produces Finding components
collected into SECURITY_FINDINGS (INT-005).

Step 12 (validate_security) checks INV-014 (findings cite evidence),
INV-015 (severity consistency), INV-016 (phase independence), INV-017
(secret redaction -- CRITICAL), INV-018 (disabled phases produce no
findings).

Extension protocols used per step:

| Step | Protocol | Reference |
|---|---|---|
| analyze_audiences | IP-001 (InputParser.parse_audience) | RUNTIME_IMPL-01 InputParser Protocol |
| analyze_health_dimensions | AE-001 (AnalysisEngine.run_dimension) | RUNTIME_IMPL-01 AnalysisEngine Protocol |
| analyze_security_phases | AE-001 (AnalysisEngine.run_phase) | RUNTIME_IMPL-01 AnalysisEngine Protocol |

### Phase 4: Findings Assembly

| # | Step Name | Type | onsuccess | on_reject_refine | Role Policy |
|---|---|---|---|---|---|
| 13 | assemble_findings_reports | action | validate_assembly | -- | (action) |
| 14 | validate_assembly | action | validate_outputs | -- | (action) |

Phase 4 implements TS-006 (Findings Report Assembly) from RUNTIME_IMPL-01.

Step 13 (assemble_findings_reports) takes HEALTH_FINDINGS (INT-004) and
SECURITY_FINDINGS (INT-005) and produces two OutputDocument components:
the health report (OUT-002 / STRUCTURAL_HEALTH_REPORT) via OM-002 mapping
and the security report (OUT-003 / SECURITY_AUDIT_REPORT) via OM-003
mapping. Findings are grouped by dimension_id/phase_id, sorted by
severity (critical first), and organized into OutputSection components
(Component 13).

Step 14 (validate_assembly) checks INV-019 (health report has one section
per enabled dimension), INV-020 (security report has one section per
enabled phase), INV-021 (all findings within a section are from the
corresponding dimension/phase).

### Phase 5: Validation and Review

| # | Step Name | Type | onsuccess | on_reject_refine | Role Policy |
|---|---|---|---|---|---|
| 15 | validate_outputs | action | review_quality | -- | (action) |
| 16 | review_quality | prompt | render_outputs | adjust_parameters | reviewer_standard |
| 17 | render_outputs | action | promote_outputs | -- | (action) |

Phase 5 implements TS-007 (Output Validation) from RUNTIME_IMPL-01,
followed by an LLM quality review and output rendering.

Step 15 (validate_outputs) checks INV-022 (output_type_count >= 3),
INV-023 (all OutputDocument.is_self_contained is true), INV-024 (no
unresolved references to source files). It also verifies all findings
cite evidence, severity scale consistency, and no hallucinated content.
It produces the RUN_MANIFEST (OUT-004 / Component 14).

Step 16 (review_quality) uses the reviewer_standard role policy to assess
the quality of generated findings and reports beyond structural
constraints: evidence sufficiency, remediation clarity, finding
prioritization, and overall report completeness. If quality is rejected,
the workflow enters the adjustment loop (see Review Loops section).

Step 17 (render_outputs) serializes all OutputDocument components and the
RunManifest to concrete Markdown files using the OutputRenderer protocol.
Produces AUDIENCE_META_CONTENT (OUT-001), STRUCTURAL_HEALTH_REPORT
(OUT-002), SECURITY_AUDIT_REPORT (OUT-003), and RUN_MANIFEST (OUT-004)
as concrete files on disk.

Extension protocols used per step:

| Step | Protocol | Reference |
|---|---|---|
| render_outputs | OR-001 (OutputRenderer.render_document, render_manifest) | RUNTIME_IMPL-01 OutputRenderer Protocol |

### Phase 6: Delivery

| # | Step Name | Type | onsuccess | on_reject_refine | Role Policy |
|---|---|---|---|---|---|
| 18 | promote_outputs | action | complete_pipeline | -- | (action) |
| 19 | complete_pipeline | action | (terminal) | -- | (action) |

Phase 6 copies the rendered output files to their final output location
and records the pipeline completion result.

Step 18 (promote_outputs) copies AUDIENCE_META_CONTENT,
STRUCTURAL_HEALTH_REPORT, SECURITY_AUDIT_REPORT, and RUN_MANIFEST to the
designated output directory. Backup of any existing files at the
destination is performed if configured.

Step 19 (complete_pipeline) records the final pipeline outcome
(success/failure), captures run metadata (run_id, generation_date,
output_count, output_types), and signals workflow completion.

### Auxiliary Step (Refinement Only)

| # | Step Name | Type | onsuccess | on_reject_refine | Role Policy |
|---|---|---|---|---|---|
| 20 | adjust_parameters | prompt | analyze_audiences | -- | architect_standard |

Step 20 is an auxiliary prompt step activated only during quality review
refinement. It modifies RuntimeConfig parameters (dimension thresholds,
phase sensitivity levels) based on review feedback from step 16. After
adjustment, the analysis pipeline re-executes from analyze_audiences
(step 7) with updated parameters.

### Role Policy Distribution

| Role Policy | Count | Steps |
|---|---|---|
| reviewer_standard | 1 | review_quality (16) |
| architect_standard | 1 | adjust_parameters (20, auxiliary) |
| (action) | 17 | All other steps (1-15, 17-19) |

Total prompt-driven steps: 2 (review_quality, adjust_parameters).
Total action-driven steps: 18.

---

## Routing Logic

### Onsuccess Routing Chain

The primary execution path follows a linear chain through all 19 steps:

```
validate_input (1)
  -> prepare_configuration (2)
  -> scan_codebase (3)
  -> validate_scan (4)
  -> build_import_graph (5)
  -> validate_import_graph (6)
  -> analyze_audiences (7)
  -> validate_audiences (8)
  -> analyze_health_dimensions (9)
  -> validate_health (10)
  -> analyze_security_phases (11)
  -> validate_security (12)
  -> assemble_findings_reports (13)
  -> validate_assembly (14)
  -> validate_outputs (15)
  -> review_quality (16)
  -> render_outputs (17)
  -> promote_outputs (18)
  -> complete_pipeline (19)
  -> (terminal)
```

### Quality Review Loop

When review_quality (Step 16) determines that the findings and reports do
not meet quality standards, the workflow enters an adjustment loop.

| From Step | on_reject_refine Target | Max Iterations | Exhausted Code | Exhausted Class |
|---|---|---|---|---|
| review_quality (16) | adjust_parameters (20) | 2 | QUALITY_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED |

Note: adjust_parameters (Step 20) is an auxiliary prompt step activated
only during refinement. It is not part of the primary execution chain.

Quality review loop mechanics:

1. review_quality (Step 16) evaluates findings quality using
   reviewer_standard role. Criteria include: evidence sufficiency,
   remediation clarity, finding prioritization, report completeness,
   and severity calibration.
2. If quality PASSES: onsuccess to render_outputs (Step 17).
3. If quality REJECTS: on_reject_refine to adjust_parameters (Step 20).
4. adjust_parameters modifies RuntimeConfig parameters (e.g., coupling
   thresholds, complexity thresholds, phase sensitivity) based on review
   feedback.
5. After adjustment, the analysis pipeline re-executes from
   analyze_audiences (Step 7) through validate_outputs (Step 15) with
   updated parameters.
6. This loop repeats up to 2 times.
7. If all attempts fail, workflow halts with QUALITY_REVIEW_EXHAUSTED.

### Secret Redaction Failure

When validate_security (Step 12) detects that secret values are not
properly redacted from security findings (INV-017 violation), the
pipeline halts immediately. Secret redaction failure is a safety
constraint and is unrecoverable as defined in RUNTIME_IMPL-01 Error
Handling Strategy.

| From Step | Failure Action | Error Code |
|---|---|---|
| validate_security (12) | Halt pipeline | SECRET_REDACTION_FAILURE |

### Invariant Violation Handling

When any invariant validation step (Steps 4, 6, 8, 10, 12, 14, 15)
detects an invariant violation, the pipeline halts immediately with a
specific error code identifying the failed invariant. Per RUNTIME_IMPL-01
Error Handling Strategy, invariant violations are unrecoverable.

| Step | Invariant | Error Code |
|---|---|---|
| validate_scan (4) | INV-001 | INVENTORY_EMPTY |
| validate_scan (4) | INV-002 | NO_PYTHON_PACKAGE |
| validate_scan (4) | INV-003 | NO_DOC_DIRECTORY |
| validate_import_graph (6) | INV-004 | INCOMPLETE_GRAPH_NODES |
| validate_import_graph (6) | INV-005 | UNRESOLVED_RELATIVE_IMPORTS |
| validate_import_graph (6) | INV-006 | NON_AST_IMPORT_PARSING |
| validate_audiences (8) | INV-007 | AUDIENCE_DOC_COUNT_MISMATCH |
| validate_audiences (8) | INV-008 | HALLUCINATED_CONTENT |
| validate_audiences (8) | INV-009 | AUDIENCE_FIDELITY_VIOLATION |
| validate_health (10) | INV-010 | FINDING_MISSING_EVIDENCE |
| validate_health (10) | INV-011 | SEVERITY_INCONSISTENCY |
| validate_audiences (8) | INV-012 | DIMENSION_NOT_SELF_CONTAINED |
| validate_health (10) | INV-013 | DISABLED_DIMENSION_FINDINGS |
| validate_security (12) | INV-014 | SECURITY_FINDING_MISSING_EVIDENCE |
| validate_security (12) | INV-015 | SECURITY_SEVERITY_INCONSISTENCY |
| validate_security (12) | INV-016 | PHASE_NOT_SELF_CONTAINED |
| validate_security (12) | INV-017 | SECRET_REDACTION_FAILURE |
| validate_security (12) | INV-018 | DISABLED_PHASE_FINDINGS |
| validate_assembly (14) | INV-019 | HEALTH_REPORT_STRUCTURE |
| validate_assembly (14) | INV-020 | SECURITY_REPORT_STRUCTURE |
| validate_assembly (14) | INV-021 | FINDING_SOURCE_MISMATCH |
| validate_outputs (15) | INV-022 | INSUFFICIENT_OUTPUT_TYPES |
| validate_outputs (15) | INV-023 | NON_SELF_CONTAINED_OUTPUT |
| validate_outputs (15) | INV-024 | UNRESOLVED_REFERENCES |

### Onsuccess Verification

| From Step | onsuccess Target | Target Exists | PASS |
|---|---|---|---|
| validate_input (1) | prepare_configuration (2) | Yes | PASS |
| prepare_configuration (2) | scan_codebase (3) | Yes | PASS |
| scan_codebase (3) | validate_scan (4) | Yes | PASS |
| validate_scan (4) | build_import_graph (5) | Yes | PASS |
| build_import_graph (5) | validate_import_graph (6) | Yes | PASS |
| validate_import_graph (6) | analyze_audiences (7) | Yes | PASS |
| analyze_audiences (7) | validate_audiences (8) | Yes | PASS |
| validate_audiences (8) | analyze_health_dimensions (9) | Yes | PASS |
| analyze_health_dimensions (9) | validate_health (10) | Yes | PASS |
| validate_health (10) | analyze_security_phases (11) | Yes | PASS |
| analyze_security_phases (11) | validate_security (12) | Yes | PASS |
| validate_security (12) | assemble_findings_reports (13) | Yes | PASS |
| assemble_findings_reports (13) | validate_assembly (14) | Yes | PASS |
| validate_assembly (14) | validate_outputs (15) | Yes | PASS |
| validate_outputs (15) | review_quality (16) | Yes | PASS |
| review_quality (16) | render_outputs (17) | Yes | PASS |
| render_outputs (17) | promote_outputs (18) | Yes | PASS |
| promote_outputs (18) | complete_pipeline (19) | Yes | PASS |
| complete_pipeline (19) | (terminal) | N/A | PASS |
| adjust_parameters (20) | analyze_audiences (7) | Yes | PASS |

All 20 onsuccess links verified. No dangling references. PASS.

### On_Reject_Refine Verification

| From Step | on_reject_refine Target | Target Exists | Max Iterations | PASS |
|---|---|---|---|---|
| review_quality (16) | adjust_parameters (20) | Yes | 2 | PASS |

All 1 on_reject_refine links verified. Loop has max iterations greater
than 0 to prevent infinite loops. PASS.

### Dead-End Check

The only terminal step is complete_pipeline (Step 19), which has no
onsuccess (pipeline ends). All non-terminal steps have at least one exit
path (onsuccess or on_reject_refine). PASS.

### Self-Loop Check

No step routes to itself directly. The quality loop goes
review_quality -> adjust_parameters -> analyze_audiences -> ... ->
review_quality, which is a multi-step cycle, not a self-loop. PASS.

### Cycle Check

No unbounded cycles exist. The quality review loop has an explicit max
iteration limit of 2. PASS.

---

## Review Loops

### Review/Refine Loop Table

| # | Review Step | Refine Step | Max Iterations | Exhausted Code | Exhausted Class |
|---|---|---|---|---|---|
| 1 | review_quality (16) | adjust_parameters (20) | 2 | QUALITY_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED |

### Recovery Loop Table

No recovery loops are defined for this pipeline. Per RUNTIME_IMPL-01
Error Handling Strategy, invariant violations and secret redaction
failures are unrecoverable and halt the pipeline immediately.

### Loop Mechanics

#### Quality Review Loop

This loop ensures the generated findings and reports meet quality
standards beyond structural constraints. It is triggered when the LLM
reviewer determines the output is inadequate.

1. review_quality (Step 16) evaluates the findings and reports against
   quality criteria: evidence sufficiency (each finding has adequate
   evidence), remediation clarity (recommended fixes are actionable),
   finding prioritization (severity ratings are appropriate), report
   completeness (all enabled dimensions/phases are covered), and
   overall coherence.
2. If quality passes: control proceeds to render_outputs (Step 17).
3. If quality rejected:
   a. Control transfers to adjust_parameters (Step 20).
   b. adjust_parameters modifies RuntimeConfig parameters based on
      review feedback (e.g., adjust coupling fan_in_threshold,
      fan_out_threshold, cyclomatic_threshold, or phase sensitivity).
   c. Analysis pipeline re-executes from analyze_audiences (Step 7)
      through validate_outputs (Step 15) with updated parameters.
4. Maximum 2 review cycles before human intervention required.

Trace: RUNTIME_IMPL-01 Error Handling Strategy, COMPOSITION_SPEC-01
Transformation Rules (INV-010 through INV-024).

---

## Human Approval

### Approval Gate Configuration

The generated codebase_intelligence workflow does NOT require explicit
human approval gates. All steps set requires_human_approval_after = false.

| Step | requires_human_approval_after | Rationale |
|---|---|---|
| validate_input (1) | false | Deterministic validation |
| prepare_configuration (2) | false | Configuration is parameter-driven |
| scan_codebase (3) | false | Deterministic file scan |
| validate_scan (4) | false | Deterministic invariant check |
| build_import_graph (5) | false | Deterministic AST parsing |
| validate_import_graph (6) | false | Deterministic invariant check |
| analyze_audiences (7) | false | Deterministic audience filtering |
| validate_audiences (8) | false | Deterministic invariant check |
| analyze_health_dimensions (9) | false | Deterministic dimension analysis |
| validate_health (10) | false | Deterministic invariant check |
| analyze_security_phases (11) | false | Deterministic phase analysis |
| validate_security (12) | false | Deterministic invariant check |
| assemble_findings_reports (13) | false | Deterministic assembly |
| validate_assembly (14) | false | Deterministic invariant check |
| validate_outputs (15) | false | Deterministic output validation |
| review_quality (16) | false | Automated LLM review gate |
| render_outputs (17) | false | Deterministic rendering |
| adjust_parameters (20) | false | Parameter adjustment |
| promote_outputs (18) | false | Deterministic file copy |
| complete_pipeline (19) | false | Completion recording |

### Why No Human Approval Gates

The codebase_intelligence pipeline relies on automated quality gates
rather than human approval:

1. Structural invariants (INV-001 through INV-024) are enforced by
   deterministic validation steps (Steps 4, 6, 8, 10, 12, 14, 15).
2. Quality review (Step 16) uses LLM-based assessment as an automated
   gate with a refinement loop.
3. Secret redaction (INV-017) is enforced by the security analysis stage
   with pipeline halt on failure.
4. Output type count (INV-022) is enforced with a default overview
   fallback when audiences are absent.
5. Invariant violations halt the pipeline immediately, preventing
   invalid output from reaching delivery.

This design provides sufficient quality assurance without requiring
human intervention during normal pipeline execution.

---

## Artifact Flow Chains

This section traces each artifact from its producer step to its consumer
steps. Every artifact key from ARTIFACT_CONTRACT-01 is accounted for.
No temporal violations exist.

### Input Artifact Flows

| Artifact Key | Source | First Consumer | All Consumers |
|---|---|---|---|
| SOURCE_CODEBASE_DIR (IN-001) | External input | validate_input (1) | Steps 1, 3, 5, 9, 11 |
| AUDIENCES_DIR (IN-002) | External input (optional) | validate_input (1) | Steps 1, 7 |
| CONFIG_FILE (IN-003) | External input (optional) | validate_input (1) | Steps 1, 2, 9, 11 |

### Pipeline Configuration Flows

| Artifact Key | Producer Step | Consumer Steps |
|---|---|---|
| RUNTIME_CONFIG | prepare_configuration (2) | Steps 3-15, 20 |

### Layer 1 Component Flows (Input Parsing)

| Artifact Key | Producer Step | Consumer Steps |
|---|---|---|
| FILE_INVENTORY (INT-001) | scan_codebase (3) | Steps 4, 5, 7, 9, 11 |
| PARSE_ERRORS_LOG (INT-006, partial) | scan_codebase (3) | Step 15 |
| IMPORT_GRAPH (INT-002) | build_import_graph (5) | Steps 6, 9 |
| SOURCE_SYMBOLS (INT-003) | build_import_graph (5) | Steps 6, 7, 9, 11 |
| PARSE_ERRORS_LOG (INT-006, complete) | build_import_graph (5) | Step 15 |

### Layer 2 Component Flows (Analysis)

| Artifact Key | Producer Step | Consumer Steps |
|---|---|---|
| AUDIENCE_OUTPUT_DOCS (partial OUT-001) | analyze_audiences (7) | Steps 8, 15, 17 |
| HEALTH_FINDINGS (INT-004) | analyze_health_dimensions (9) | Steps 10, 13 |
| SECURITY_FINDINGS (INT-005) | analyze_security_phases (11) | Steps 12, 13 |
| ANALYSIS_INVARIANT_REPORT (TS-003) | validate_audiences (8) | Step 8 (gate check) |
| ANALYSIS_INVARIANT_REPORT (TS-004) | validate_health (10) | Step 10 (gate check) |
| ANALYSIS_INVARIANT_REPORT (TS-005) | validate_security (12) | Step 12 (gate check) |

### Layer 3 Component Flows (Output Rendering)

| Artifact Key | Producer Step | Consumer Steps |
|---|---|---|
| AUDIENCE_META_CONTENT (OUT-001) | render_outputs (17) | Steps 18-19 |
| STRUCTURAL_HEALTH_REPORT (OUT-002) | render_outputs (17) | Steps 18-19 |
| SECURITY_AUDIT_REPORT (OUT-003) | render_outputs (17) | Steps 18-19 |
| RUN_MANIFEST (OUT-004) | validate_outputs (15) | Steps 16, 17, 18-19 |
| ASSEMBLY_INVARIANT_REPORT | validate_assembly (14) | Step 14 (gate check) |
| OUTPUT_VALIDATION_REPORT | validate_outputs (15) | Step 16 |

### Quality Review Flows

| Artifact Key | Producer Step | Consumer Steps |
|---|---|---|
| QUALITY_REVIEW_REPORT | review_quality (16) | Step 20 (if rejected) |
| ADJUSTED_CONFIG | adjust_parameters (20) | Step 7 (re-execution) |

### Delivery Flows

| Artifact Key | Producer Step | Consumer Steps |
|---|---|---|
| AUDIENCE_META_CONTENT_PROMOTED | promote_outputs (18) | (terminal deliverable) |
| STRUCTURAL_HEALTH_REPORT_PROMOTED | promote_outputs (18) | (terminal deliverable) |
| SECURITY_AUDIT_REPORT_PROMOTED | promote_outputs (18) | (terminal deliverable) |
| RUN_MANIFEST_PROMOTED | promote_outputs (18) | (terminal deliverable) |
| COMPLETION_RESULT | complete_pipeline (19) | (terminal marker) |

### Artifact Flow Verification

| Check | Result |
|---|---|
| All artifact keys from ARTIFACT_CONTRACT-01 are accounted for | PASS |
| No artifact is consumed before it is produced | PASS |
| Every produced artifact is consumed by at least one step or is terminal | PASS |
| No dangling references to undeclared artifact keys | PASS |
| Input artifacts (SOURCE_CODEBASE_DIR, AUDIENCES_DIR, CONFIG_FILE) resolve from external sources | PASS |
| Terminal deliverables (four PROMOTED artifacts) are final outputs | PASS |
| Intermediate artifacts (FILE_INVENTORY, IMPORT_GRAPH, SOURCE_SYMBOLS, HEALTH_FINDINGS, SECURITY_FINDINGS, PARSE_ERRORS_LOG) are internal | PASS |

---

## Failure Handling

### Step-Level Failure Matrix

| Step | Failure Type | Error Code | Recovery | Trace |
|---|---|---|---|---|
| validate_input (1) | Source codebase not found | SOURCE_NOT_FOUND | Halt | V-IN-001 |
| validate_input (1) | Source not readable UTF-8 | INVALID_ENCODING | Halt | V-IN-001 |
| validate_input (1) | No Python files parseable | NO_PARSEABLE_SOURCE | Halt | V-IN-002 |
| scan_codebase (3) | Directory walk failure | DIRECTORY_WALK_ERROR | Halt | INV-001 |
| validate_scan (4) | Empty inventory | INVENTORY_EMPTY | Halt | INV-001 |
| validate_scan (4) | No Python package | NO_PYTHON_PACKAGE | Halt | INV-002 |
| validate_scan (4) | No doc directory | NO_DOC_DIRECTORY | Halt | INV-003 |
| build_import_graph (5) | AST parse failure | AST_PARSE_ERROR | Halt (per-file) | INV-006 |
| validate_import_graph (6) | Incomplete graph | INCOMPLETE_GRAPH_NODES | Halt | INV-004 |
| validate_import_graph (6) | Unresolved imports | UNRESOLVED_RELATIVE_IMPORTS | Halt | INV-005 |
| analyze_audiences (7) | Audience parse failure | AUDIENCE_PARSE_ERROR | Skip audience | IM-VAL-008 |
| validate_audiences (8) | Hallucinated content | HALLUCINATED_CONTENT | Halt | INV-008 |
| analyze_health_dimensions (9) | Dimension analysis error | DIMENSION_ANALYSIS_ERROR | Halt | INV-010 |
| validate_health (10) | Missing evidence | FINDING_MISSING_EVIDENCE | Halt | INV-010 |
| validate_health (10) | Severity inconsistency | SEVERITY_INCONSISTENCY | Halt | INV-011 |
| analyze_security_phases (11) | Phase analysis error | PHASE_ANALYSIS_ERROR | Halt | INV-014 |
| validate_security (12) | Secret redaction failure | SECRET_REDACTION_FAILURE | Halt (unrecoverable) | INV-017 |
| validate_security (12) | Missing evidence | SECURITY_FINDING_MISSING_EVIDENCE | Halt | INV-014 |
| assemble_findings_reports (13) | Assembly error | ASSEMBLY_ERROR | Halt | INV-019, INV-020 |
| validate_assembly (14) | Structure violation | HEALTH_REPORT_STRUCTURE | Halt | INV-019 |
| validate_assembly (14) | Finding mismatch | FINDING_SOURCE_MISMATCH | Halt | INV-021 |
| validate_outputs (15) | Insufficient output types | INSUFFICIENT_OUTPUT_TYPES | Halt | INV-022 |
| validate_outputs (15) | Non-self-contained | NON_SELF_CONTAINED_OUTPUT | Halt | INV-023 |
| validate_outputs (15) | Unresolved references | UNRESOLVED_REFERENCES | Halt | INV-024 |
| review_quality (16) | Quality rejected | QUALITY_REVIEW_EXHAUSTED | Recovery loop (2x) | Quality criteria |
| render_outputs (17) | Write failure | WRITE_ERROR | Halt | OR-001 |
| promote_outputs (18) | Promotion failed | PROMOTION_ERROR | Halt | N/A |

### Exhaustion Handling

| Loop | Exhausted Code | Exhausted Class | Action |
|---|---|---|---|
| Quality review (2x) | QUALITY_REVIEW_EXHAUSTED | HUMAN_RETRY_REQUIRED | Halt pipeline, request human review |

---

## Self-Validation

### Check 1: Step Definition Completeness

| Check | Result |
|---|---|
| All 7 pipeline stages (TS-001 to TS-007) have corresponding steps | PASS |
| Input validation step exists before pipeline execution | PASS |
| Each Layer 1 stage has an invariant validation step | PASS |
| Each Layer 2 stage has an invariant validation step | PASS |
| Assembly stage (TS-006) has an invariant validation step | PASS |
| Output validation step (TS-007) exists after assembly | PASS |
| Quality review step exists before rendering | PASS |
| Rendering step exists after quality review | PASS |
| Completion step is terminal | PASS |
| Auxiliary refinement step (adjust_parameters) is defined | PASS |

### Check 2: Routing Validity

| Check | Result |
|---|---|
| All onsuccess targets reference existing steps | PASS |
| All on_reject_refine targets reference existing steps | PASS |
| No step routes to itself | PASS |
| No unbounded cycles | PASS |
| Terminal step has no exit path | PASS |
| All non-terminal steps have at least one exit | PASS |

### Check 3: Artifact Flow Validity

| Check | Result |
|---|---|
| SOURCE_CODEBASE_DIR consumed after external provision | PASS |
| RUNTIME_CONFIG produced before any pipeline step consumes it | PASS |
| FILE_INVENTORY produced before Layer 2 steps consume it | PASS |
| IMPORT_GRAPH produced before health analysis consumes it | PASS |
| SOURCE_SYMBOLS produced before audience and analysis steps consume it | PASS |
| HEALTH_FINDINGS produced before assembly step consumes it | PASS |
| SECURITY_FINDINGS produced before assembly step consumes it | PASS |
| AUDIENCE_META_CONTENT, STRUCTURAL_HEALTH_REPORT, SECURITY_AUDIT_REPORT produced by render_outputs | PASS |
| RUN_MANIFEST produced by validate_outputs before rendering | PASS |
| No step consumes an artifact before it is produced | PASS |

### Check 4: Constraint Enforcement

| Constraint | Enforced By | PASS |
|---|---|---|
| C-FMT-001 (input docs are Rich Markdown) | scan_codebase (3) file_type classification | PASS |
| C-FMT-002 (input source is Python) | scan_codebase (3) file_type classification | PASS |
| C-FMT-003 (input encoding is UTF-8) | validate_input (1) V-IN-001 | PASS |
| C-FMT-004 (AST-based import analysis) | build_import_graph (5) via INV-006 | PASS |
| C-FMT-005 (severity consistency) | validate_health (10) INV-011, validate_security (12) INV-015 | PASS |
| C-FMT-006 (self-contained reports) | validate_outputs (15) INV-023 | PASS |
| C-FMT-007 (evidence-backed findings) | validate_health (10) INV-010, validate_security (12) INV-014 | PASS |
| C-CMP-001 (no hallucination) | validate_audiences (8) INV-008 | PASS |
| C-CMP-002 (secret redaction) | validate_security (12) INV-017 | PASS |
| C-CMP-003 (audience fidelity) | validate_audiences (8) INV-009 | PASS |
| C-CMP-004 (dimension independence) | validate_health (10) INV-012, validate_security (12) INV-016 | PASS |
| C-CMP-005 (plugin extensibility) | analyze_audiences (7), analyze_health_dimensions (9), analyze_security_phases (11) via registry | PASS |
| C-CMP-006 (configurable scope) | prepare_configuration (2) RuntimeConfig.enabled flags | PASS |

### Check 5: Invariant Coverage

| Invariant | Enforced By | PASS |
|---|---|---|
| INV-001 (FileInventory non-empty) | validate_scan (4) | PASS |
| INV-002 (has_python_package) | validate_scan (4) | PASS |
| INV-003 (has_doc_directory) | validate_scan (4) | PASS |
| INV-004 (graph nodes per source) | validate_import_graph (6) | PASS |
| INV-005 (relative imports resolved) | validate_import_graph (6) | PASS |
| INV-006 (AST-based parsing) | validate_import_graph (6) | PASS |
| INV-007 (one doc per audience) | validate_audiences (8) | PASS |
| INV-008 (no hallucination) | validate_audiences (8) | PASS |
| INV-009 (audience fidelity) | validate_audiences (8) | PASS |
| INV-010 (findings cite evidence) | validate_health (10) | PASS |
| INV-011 (severity consistency) | validate_health (10) | PASS |
| INV-012 (dimension independence) | validate_health (10) | PASS |
| INV-013 (disabled dimensions) | validate_health (10) | PASS |
| INV-014 (security findings evidence) | validate_security (12) | PASS |
| INV-015 (security severity) | validate_security (12) | PASS |
| INV-016 (phase independence) | validate_security (12) | PASS |
| INV-017 (secret redaction) | validate_security (12) | PASS |
| INV-018 (disabled phases) | validate_security (12) | PASS |
| INV-019 (health report structure) | validate_assembly (14) | PASS |
| INV-020 (security report structure) | validate_assembly (14) | PASS |
| INV-021 (finding-source alignment) | validate_assembly (14) | PASS |
| INV-022 (3+ output types) | validate_outputs (15) | PASS |
| INV-023 (self-contained outputs) | validate_outputs (15) | PASS |
| INV-024 (no unresolved refs) | validate_outputs (15) | PASS |

### Check 6: Runtime Implementation Compliance

| RUNTIME_IMPL Section | Step Coverage | PASS |
|---|---|---|
| Section: Implementation Architecture (7-stage pipeline) | Steps 3-17 | PASS |
| Section: Input Loading (TS-001, TS-002) | Steps 3-6 | PASS |
| Section: Transformation Engine (TS-003 to TS-005) | Steps 7-12 | PASS |
| Section: Findings Report Assembly (TS-006) | Steps 13-14 | PASS |
| Section: Output Validation (TS-007) | Steps 15-17 | PASS |
| Section: Output Generation (Rendering) | Step 17 | PASS |
| Section: Configuration (RuntimeConfig) | Step 2 | PASS |
| Section: Extension Interface (3 Protocols) | Steps 3, 5, 7, 9, 11, 17 via registry | PASS |
| Section: Error Handling Strategy | Failure matrix, invariant halt checks | PASS |

### Check 7: Recovery Loop Validity

| Check | Result |
|---|---|
| Quality review: review_quality -> adjust_parameters -> analyze_audiences | PASS |
| Quality recovery re-executes Steps 7-15 | PASS |
| Max 2 iterations prevents infinite loop | PASS |
| Secret redaction failure is unrecoverable | PASS |
| All invariant violations are unrecoverable | PASS |
| No recovery loops needed (per runtime design) | PASS |

### Check 8: ASCII Compliance

| Check | Result |
|---|---|
| No em-dashes used | PASS |
| No curly quotes used | PASS |
| No Unicode characters used | PASS |
| YAML frontmatter uses plain ASCII | PASS |
| All identifiers use ASCII characters | PASS |

### Check 9: YAML Frontmatter Compliance

| Field | Value | Present |
|---|---|---|
| doc_type | "step_sequence" | PASS |
| identity_locked | true | PASS |
| generator_name | "codebase_intelligence" | PASS |
| version | "1.0.0" | PASS |
| source_artifact_contract | "ARTIFACT_CONTRACT-01" | PASS |
| source_runtime_impl | "RUNTIME_IMPL-01" | PASS |
| source_composition_spec | "COMPOSITION_SPEC-01" | PASS |
| job_id | "AGB-ub97gvkz" | PASS |
| generated_at | "2026-08-10" | PASS |
| total_steps | 19 | PASS |
| output_type | "pipeline_execution" | PASS |
| review_loop_count | 1 | PASS |
| recovery_loop_count | 0 | PASS |
| approval_gate_count | 0 | PASS |
| phase_count | 6 | PASS |

All mandatory frontmatter fields present. PASS.

### Check 10: Step Count Summary

| Category | Count |
|---|---|
| Total steps | 19 (primary) + 1 (auxiliary) |
| Prompt-driven steps | 2 (review_quality, adjust_parameters) |
| Action-driven steps | 18 |
| Input preparation steps | 2 |
| Input parsing steps (Layer 1) | 4 |
| Analysis steps (Layer 2) | 6 |
| Assembly steps | 2 |
| Validation and review steps | 3 |
| Delivery steps | 2 |
| Auxiliary refinement steps | 1 |

---

## Assumptions

| ID | Assumption | Rationale |
|---|---|---|
| ASM-SS-001 | Pipeline stages execute sequentially within a single process despite parallel capability | RUNTIME_IMPL-01 Execution Model: sequential for deterministic step ordering |
| ASM-SS-002 | Each pipeline stage and its invariant check are exposed as separate action steps for observability | Workflow best practice for traceability |
| ASM-SS-003 | The adjust_parameters step uses LLM review feedback to modify RuntimeConfig thresholds | COMPOSITION_SPEC-01 Extension Mechanism (EXT-004 configurable thresholds) |
| ASM-SS-004 | Extension implementations are resolved via DIMENSION_REGISTRY, PHASE_REGISTRY, RENDERER_REGISTRY at pipeline startup | RUNTIME_IMPL-01 Extension Interface |
| ASM-SS-005 | When no audience definitions are found, a default codebase overview report is produced as a third output type | ARTIFACT_CONTRACT-01 explicit assumption for INV-022 |
| ASM-SS-006 | Invariant validation is performed in dedicated steps rather than inline | Separation of concerns for traceability |
| ASM-SS-007 | Secret redaction failure halts the entire pipeline with no recovery | RUNTIME_IMPL-01 Error Handling Strategy (safety constraint) |
| ASM-SS-008 | Audience analysis, health dimension analysis, and security phase analysis execute sequentially in the workflow | Workflow step ordering requires deterministic linear execution |

---

End of Step Sequence Document
