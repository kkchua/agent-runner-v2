---
doc_type: "artifact_contract"
identity_locked: true
codename: "codebase_intelligence"
generator_name: "Codebase Intelligence Generator"
spec_version: "1.0.0"
composition_spec_ref: "COMPOSITION_SPEC-01.md"
runtime_impl_ref: "RUNTIME_IMPL-01.md"
requirement_analysis_ref: "REQUIREMENT_ANALYSIS-01.md"
input_artifact_count: 3
output_artifact_count: 4
intermediate_artifact_count: 6
---

# Artifact Contract: Codebase Intelligence Generator

## Overview

This document defines the complete artifact contract for the codebase_intelligence generator workflow. It specifies every artifact that flows through the 7-stage transformation pipeline (TS-001 through TS-007), including inputs accepted, outputs produced, intermediate data structures, and their relationships. All artifacts trace back to the requirement analysis (REQUIREMENT_ANALYSIS-01.md), composition specification (COMPOSITION_SPEC-01.md), and runtime implementation design (RUNTIME_IMPL-01.md).

The contract uses placeholder tokens for run-specific values:
- {job_id} -- unique identifier for a generator run
- {seq} -- sequence number for versioned artifacts
- {audience_id} -- machine-readable audience identifier
- {dimension_id} -- health dimension identifier (e.g., DIM-CIRCULAR)
- {phase_id} -- security phase identifier (e.g., PHASE-SECRETS)

---

## Input Artifacts

Input artifacts are the external resources the workflow accepts at the start of execution. They correspond to Layer 1 (Input Parsing) of the composition specification.

### IN-001: Source Codebase Directory

| Field | Value |
|---|---|
| Artifact key | SOURCE_CODEBASE_DIR |
| Description | Target repository root containing all codebase files to analyze. Includes documentation (Rich Markdown), Python source code, and configuration files. |
| Type | Directory (filesystem path) |
| Expected formats | .md (Rich Markdown), .py (Python), .toml/.json/.yaml/.yml/.cfg/.ini (configuration), other (uncategorized) |
| Path pattern | {repository_root}/ (resolved from runtime configuration or command-line argument) |
| Required | Yes |
| Validation | V-IN-001: All files readable as UTF-8. V-IN-002: Python files AST-parseable. V-IN-003: Documentation files non-empty Markdown. V-IN-004: At least one Python package directory and one documentation directory exist. |
| Traceability | REQ IN-001, TR-001 |
| Consumed by stage | TS-001 (Codebase Scan) |

### IN-002: Audience Definitions Directory

| Field | Value |
|---|---|
| Artifact key | AUDIENCES_DIR |
| Description | Directory containing audience definition plugin files. Each .md file defines a stakeholder audience with focus areas, section structure, tone, and exclusion list. |
| Type | Directory (filesystem path) |
| Expected formats | .md files with YAML frontmatter containing audience_id, label, tone, focus_areas, section_structure, exclude |
| Path pattern | {audiences_dir}/ (resolved from runtime configuration, default: {repository_root}/audiences/) |
| Required | No |
| Default behavior | If missing or empty, TS-003 produces no audience report output documents. Pipeline continues. |
| Validation | IM-VAL-008: Audience definitions have valid YAML frontmatter. |
| Traceability | REQ EP-001, C-CMP-005, TR-003 |
| Consumed by stage | TS-003 (Audience Analysis) |

### IN-003: Runtime Configuration File

| Field | Value |
|---|---|
| Artifact key | CONFIG_FILE |
| Description | JSON configuration file controlling which analysis dimensions and security phases are enabled, their thresholds, output directory, and rendering format. |
| Type | File |
| Expected formats | .json (JSON object with keys: repository_root, output_dir, audiences_dir, dimensions, phases, rendering) |
| Path pattern | {config_path} (resolved from command-line argument, environment variable, or default config.json) |
| Required | No |
| Default behavior | If not provided, built-in defaults are used: all 5 dimensions and all 5 phases enabled, Markdown rendering, default thresholds. |
| Validation | Override precedence: CLI args > environment variables > config file > defaults. |
| Traceability | REQ EP-004, C-CMP-006, TR-004, TR-005 |
| Consumed by stages | TS-004 (Health Dimension Analysis), TS-005 (Security Phase Analysis), Output Rendering |

---

## Output Artifacts

Output artifacts are the externally visible deliverables produced by the workflow. They correspond to Layer 3 (Output Rendering) of the composition specification. The generator MUST produce at least 3 distinct output types per run (INV-022).

### OUT-001: Audience Reports

| Field | Value |
|---|---|
| Artifact key | AUDIENCE_META_CONTENT |
| Description | One structured Markdown report per audience definition. Contains codebase content filtered by audience focus areas, organized by audience section structure, written in audience tone. |
| Type | File (Markdown) |
| Output format | Rich Markdown with YAML frontmatter |
| Path pattern | {output_dir}/audience_{audience_id}.md |
| Required | Conditional (one per valid audience definition; omitted if no audiences found) |
| Count | 0 to N, where N = number of valid audience definitions discovered |
| Quality constraints | Q-OUT-001: Tone matches audience definition. Q-OUT-002: Self-contained. Q-OUT-003: No hallucination. OM-VAL-001 through OM-VAL-003. |
| Traceability | REQ OUT-001, TR-003, Q-OUT-001 to Q-OUT-003 |
| Produced by stage | TS-003 (Audience Analysis) |
| YAML frontmatter fields | document_id, output_type ("audience_report"), title, generation_date, audience_id |

### OUT-002: Structural Health Report

| Field | Value |
|---|---|
| Artifact key | STRUCTURAL_HEALTH_REPORT |
| Description | Single structured Markdown report containing all health dimension findings. One section per enabled dimension. Findings sorted by severity (critical first). Each finding includes evidence, impact, and remediation. |
| Type | File (Markdown) |
| Output format | Rich Markdown with YAML frontmatter |
| Path pattern | {output_dir}/health_report.md |
| Required | Yes (always produced, even if no findings exist) |
| Count | Exactly 1 per run |
| Quality constraints | Q-OUT-004: Evidence-backed. Q-OUT-006: Consistent severity scale. Q-OUT-007: Dimension independence. OM-VAL-004, OM-VAL-005, OM-VAL-007. |
| Traceability | REQ OUT-002, TR-004, TR-006, Q-OUT-004 to Q-OUT-007 |
| Produced by stage | TS-006 (Findings Report Assembly) |
| YAML frontmatter fields | document_id, output_type ("health_report"), title, generation_date |

### OUT-003: Security Audit Report

| Field | Value |
|---|---|
| Artifact key | SECURITY_AUDIT_REPORT |
| Description | Single structured Markdown report containing all security phase findings. One section per enabled phase. Findings sorted by severity (critical first). Secret values redacted from evidence code snippets. |
| Type | File (Markdown) |
| Output format | Rich Markdown with YAML frontmatter |
| Path pattern | {output_dir}/security_report.md |
| Required | Yes (always produced, even if no findings exist) |
| Count | Exactly 1 per run |
| Quality constraints | Q-OUT-008: Evidence-backed. Q-OUT-009: Secret redaction. Q-OUT-010: Consistent severity. Q-OUT-011: Phase independence. OM-VAL-004 to OM-VAL-006. |
| Traceability | REQ OUT-003, TR-005, TR-006, Q-OUT-008 to Q-OUT-011 |
| Produced by stage | TS-006 (Findings Report Assembly) |
| YAML frontmatter fields | document_id, output_type ("security_report"), title, generation_date |

### OUT-004: Run Manifest

| Field | Value |
|---|---|
| Artifact key | RUN_MANIFEST |
| Description | Top-level manifest aggregating all output documents produced during the run. Provides run-level metadata and summary. |
| Type | File (Markdown) |
| Output format | Rich Markdown with YAML frontmatter |
| Path pattern | {output_dir}/RUN_MANIFEST.md |
| Required | Yes (always produced) |
| Count | Exactly 1 per run |
| Quality constraints | INV-022: output_type_count >= 3. INV-023: All documents self-contained. INV-024: No unresolved references. OM-VAL-008. |
| Traceability | REQ TR-007, C-CMP-001 |
| Produced by stage | TS-007 (Output Validation) |
| YAML frontmatter fields | run_id, codename ("codebase_intelligence"), output_count, output_types, generation_date, output_type_count |

---

## Intermediate Artifacts

Intermediate artifacts are internal processing data structures produced and consumed within the pipeline. They are not external deliverables but are essential for the transformation chain. Each corresponds to one or more meta components defined in the composition specification.

### INT-001: File Inventory

| Field | Value |
|---|---|
| Artifact key | FILE_INVENTORY |
| Description | Aggregated collection of all FileEntry components discovered during TS-001. Contains categorized file counts and structural flags. |
| Type | In-memory data structure (dataclass) |
| Meta component | Component 2 (FileInventory) from COMPOSITION_SPEC |
| Contains | FileEntry[] (Component 1), doc_count, source_count, config_count, other_count, has_python_package, has_doc_directory |
| Produced by | TS-001 (Codebase Scan) |
| Consumed by | TS-002, TS-003, TS-004, TS-005 |
| Persistence | Optional; may be serialized to {output_dir}/.cache/file_inventory.json for debugging or incremental analysis (EXT-006) |

### INT-002: Import Graph

| Field | Value |
|---|---|
| Artifact key | IMPORT_GRAPH |
| Description | Complete directed dependency graph built from Python AST import analysis. Contains all import edges and module nodes. |
| Type | In-memory data structure (dataclass) |
| Meta component | Component 4 (ImportGraph) from COMPOSITION_SPEC |
| Contains | ImportEdge[] (Component 3), nodes (unique module names), node_count, edge_count |
| Produced by | TS-002 (Import Graph Construction) |
| Consumed by | TS-004 (Health Dimension Analysis -- specifically DIM-CIRCULAR, DIM-COUPLING) |
| Persistence | Optional; may be serialized to {output_dir}/.cache/import_graph.json |

### INT-003: Source Symbols

| Field | Value |
|---|---|
| Artifact key | SOURCE_SYMBOLS |
| Description | Set of all named symbols (functions, classes, constants) extracted from Python source code via AST parsing. |
| Type | In-memory data structure (list of dataclass instances) |
| Meta component | Component 5 (SourceSymbol) from COMPOSITION_SPEC |
| Contains | SourceSymbol[] with symbol_name, symbol_type, file_path, line_start, line_end, parameters, decorators, docstring, is_exported |
| Produced by | TS-002 (Import Graph Construction) |
| Consumed by | TS-003, TS-004, TS-005 |
| Persistence | Optional; may be serialized to {output_dir}/.cache/source_symbols.json |

### INT-004: Health Findings

| Field | Value |
|---|---|
| Artifact key | HEALTH_FINDINGS |
| Description | Set of all structural health findings produced by enabled analysis dimensions. Each finding includes severity, evidence, impact, and remediation. |
| Type | In-memory data structure (list of dataclass instances) |
| Meta component | Component 11 (Finding) with source_type = "health_dimension" from COMPOSITION_SPEC |
| Contains | Finding[] with finding_id format "{dimension_id}-{NNN}", severity (SeverityRating Component 9), evidence (Evidence[] Component 10) |
| Produced by | TS-004 (Health Dimension Analysis) |
| Consumed by | TS-006 (Findings Report Assembly) |
| Persistence | Optional; may be serialized to {output_dir}/.cache/health_findings.json |

### INT-005: Security Findings

| Field | Value |
|---|---|
| Artifact key | SECURITY_FINDINGS |
| Description | Set of all security findings produced by enabled security phases. Each finding includes severity, evidence (with secret redaction), impact, and remediation. |
| Type | In-memory data structure (list of dataclass instances) |
| Meta component | Component 11 (Finding) with source_type = "security_phase" from COMPOSITION_SPEC |
| Contains | Finding[] with finding_id format "{phase_id}-{NNN}", severity (SeverityRating Component 9), evidence (Evidence[] Component 10 with redacted code_snippets) |
| Produced by | TS-005 (Security Phase Analysis) |
| Consumed by | TS-006 (Findings Report Assembly) |
| Persistence | Optional; may be serialized to {output_dir}/.cache/security_findings.json |

### INT-006: Parse Errors Log

| Field | Value |
|---|---|
| Artifact key | PARSE_ERRORS_LOG |
| Description | Aggregated log of all file parsing errors encountered during TS-001 and TS-002. Each entry records the file path, error type, and error message. |
| Type | In-memory data structure (list of records) |
| Meta component | Embedded in Component 1 (FileEntry.parse_errors) from COMPOSITION_SPEC |
| Contains | Parse error records: file_path, error_type (syntax, encoding, structure), error_message |
| Produced by | TS-001, TS-002 |
| Consumed by | TS-007 (Output Validation -- for completeness verification) |
| Persistence | Optional; may be serialized to {output_dir}/.cache/parse_errors.json |

---

## Artifact Relationships

This section defines the dependency graph between artifacts, the processing order constraints, and which artifacts are required versus optional.

### Dependency Graph

The following describes which artifacts depend on which other artifacts. An arrow (A -> B) means B depends on A (A must be produced before B can be produced).

```
IN-001 (SOURCE_CODEBASE_DIR)
    |
    +---> INT-001 (FILE_INVENTORY)  [TS-001]
              |
              +---> INT-002 (IMPORT_GRAPH)  [TS-002]
              |       |
              +---> INT-003 (SOURCE_SYMBOLS)  [TS-002]
              |       |
              |       +---> OUT-001 (AUDIENCE_META_CONTENT)  [TS-003]
              |       |       |
              |       |       +---> OUT-004 (RUN_MANIFEST)  [TS-007]
              |       |
              |       +---> INT-004 (HEALTH_FINDINGS)  [TS-004]
              |       |       |
              |       |       +---> OUT-002 (STRUCTURAL_HEALTH_REPORT)  [TS-006]
              |       |               |
              |       |               +---> OUT-004 (RUN_MANIFEST)  [TS-007]
              |       |
              |       +---> INT-005 (SECURITY_FINDINGS)  [TS-005]
              |               |
              |               +---> OUT-003 (SECURITY_AUDIT_REPORT)  [TS-006]
              |                       |
              |                       +---> OUT-004 (RUN_MANIFEST)  [TS-007]
              |
              +---> INT-005 (SECURITY_FINDINGS)  [TS-005]

IN-002 (AUDIENCES_DIR)
    |
    +---> OUT-001 (AUDIENCE_META_CONTENT)  [TS-003]

IN-003 (CONFIG_FILE)
    |
    +---> INT-004 (HEALTH_FINDINGS)  [TS-004, enables/disables dimensions]
    |
    +---> INT-005 (SECURITY_FINDINGS)  [TS-005, enables/disables phases]
    |
    +---> Output Rendering format selection

INT-006 (PARSE_ERRORS_LOG)  [produced across TS-001, TS-002]
    |
    +---> OUT-004 (RUN_MANIFEST)  [TS-007, completeness check]
```

### Processing Order Constraints

The pipeline enforces the following ordering. Stages on the same level may execute in parallel.

| Order | Stage | Depends on | Produces |
|---|---|---|---|
| 1 | TS-001: Codebase Scan | IN-001 | INT-001 (FILE_INVENTORY) |
| 2 | TS-002: Import Graph Construction | INT-001 | INT-002 (IMPORT_GRAPH), INT-003 (SOURCE_SYMBOLS), INT-006 (PARSE_ERRORS_LOG) |
| 3a | TS-003: Audience Analysis | INT-001, INT-003, IN-002 | OUT-001 (AUDIENCE_META_CONTENT) |
| 3b | TS-004: Health Dimension Analysis | INT-002, INT-003, IN-003 | INT-004 (HEALTH_FINDINGS) |
| 3c | TS-005: Security Phase Analysis | INT-001, INT-003, IN-003 | INT-005 (SECURITY_FINDINGS) |
| 4 | TS-006: Findings Report Assembly | INT-004, INT-005 | OUT-002 (STRUCTURAL_HEALTH_REPORT), OUT-003 (SECURITY_AUDIT_REPORT) |
| 5 | TS-007: Output Validation | OUT-001, OUT-002, OUT-003, INT-006 | OUT-004 (RUN_MANIFEST) |

**Parallelism:** TS-003, TS-004, and TS-005 (order 3a, 3b, 3c) are independent and may execute concurrently after TS-002 completes.

### Required vs Optional Artifacts

| Artifact | Status | Condition |
|---|---|---|
| IN-001 (SOURCE_CODEBASE_DIR) | Required | Must be provided and satisfy V-IN-001 to V-IN-004 |
| IN-002 (AUDIENCES_DIR) | Optional | If missing, no audience reports produced |
| IN-003 (CONFIG_FILE) | Optional | Built-in defaults used if not provided |
| OUT-001 (AUDIENCE_META_CONTENT) | Conditional | Produced only if IN-002 contains valid audience definitions |
| OUT-002 (STRUCTURAL_HEALTH_REPORT) | Required | Always produced (even with zero findings) |
| OUT-003 (SECURITY_AUDIT_REPORT) | Required | Always produced (even with zero findings) |
| OUT-004 (RUN_MANIFEST) | Required | Always produced |
| INT-001 (FILE_INVENTORY) | Required | Must be non-empty (INV-001) |
| INT-002 (IMPORT_GRAPH) | Required | Must have at least one node per source file (INV-004) |
| INT-003 (SOURCE_SYMBOLS) | Required | May be empty if no Python source files exist |
| INT-004 (HEALTH_FINDINGS) | Required (as collection) | May be empty if all dimensions disabled or no issues found |
| INT-005 (SECURITY_FINDINGS) | Required (as collection) | May be empty if all phases disabled or no issues found |
| INT-006 (PARSE_ERRORS_LOG) | Required (as collection) | May be empty if no parse errors encountered |

### Minimum Output Type Constraint

INV-022 requires that the RunManifest reports output_type_count >= 3. Given the baseline configuration:
- OUT-001 provides output_type "audience_report" (conditional on audience definitions)
- OUT-002 provides output_type "health_report" (always)
- OUT-003 provides output_type "security_report" (always)

If no audience definitions exist, only 2 output types are produced (health_report, security_report), which violates INV-022. The pipeline must handle this case by either:
1. Treating INV-022 as a warning when audiences are absent (documented assumption).
2. Producing a third output type (e.g., a codebase summary report) when audiences are absent.

**Explicit assumption:** When no audience definitions are provided, the pipeline produces a default codebase overview report as a third output type to satisfy INV-022. This follows the requirement that "at least 3 different types of output artifacts" must be produced.

---

## Naming Conventions

This section defines consistent naming patterns for all artifact paths and identifiers.

### Directory Structure

```
{output_dir}/
    audience_{audience_id}.md          -- OUT-001 per audience
    health_report.md                   -- OUT-002
    security_report.md                 -- OUT-003
    RUN_MANIFEST.md                    -- OUT-004
    .cache/
        file_inventory.json            -- INT-001 (optional persistence)
        import_graph.json              -- INT-002 (optional persistence)
        source_symbols.json            -- INT-003 (optional persistence)
        healthfindings.json            -- INT-004 (optional persistence)
        securityfindings.json          -- INT-005 (optional persistence)
        parse_errors.json              -- INT-006 (optional persistence)
```

### Path Pattern Rules

1. **Job-specific runs:** When the generator is invoked as part of a batch or job, the output directory is scoped by job_id:
   `{jobs_root}/{job_id}/output/`

2. **Audience report naming:** `audience_{audience_id}.md` where audience_id is the machine-readable identifier from the AudienceDefinition (Component 6). Example: `audience_developer.md`, `audience_architect.md`.

3. **Fixed-name reports:** Health report, security report, and run manifest use fixed filenames (no dynamic segments).

4. **Cache directory:** Intermediate artifact persistence uses a hidden `.cache/` subdirectory under the output directory. These files are for debugging and incremental analysis only; they are not part of the output contract.

5. **Finding ID format:** `{dimension_id}-{NNN}` for health findings, `{phase_id}-{NNN}` for security findings, where NNN is a zero-padded 3-digit sequence number within the dimension/phase. Example: `DIM-CIRCULAR-001`, `PHASE-SECRETS-003`.

6. **Document ID format:** `{output_type}_{generation_date}` for uniqueness within a run. Example: `health_report_2026-08-10`.

7. **Run ID format:** `{codename}_{generation_date}_{run_sequence}`. Example: `codebase_intelligence_2026-08-10_001`.

### Placeholder Tokens

| Token | Description | Example |
|---|---|---|
| {job_id} | Unique run identifier assigned by the workflow runner | AGB-ub97gvkz |
| {seq} | Zero-padded sequence number for versioned documents | 01, 02, 03 |
| {audience_id} | Machine-readable audience identifier from audience definition | developer, architect |
| {dimension_id} | Health dimension identifier | DIM-CIRCULAR, DIM-COUPLING |
| {phase_id} | Security phase identifier | PHASE-SECRETS, PHASE-DEPS |
| {output_dir} | Root output directory for the current run | output/ |
| {repository_root} | Root of the target codebase being analyzed | . (current directory) |
| {audiences_dir} | Directory containing audience definition files | audiences/ |
| {config_path} | Path to the runtime configuration JSON file | config.json |

---

## Self-Validation

This section verifies that all artifacts declared in the requirement analysis, composition specification, and runtime implementation are covered by this contract.

### Input Artifact Coverage

| Requirement Source | Required Input | Contract Coverage | Status |
|---|---|---|---|
| REQ IN-001 | Source codebase (docs + Python) | IN-001 (SOURCE_CODEBASE_DIR) | Covered |
| REQ EP-001 | Audience definition files | IN-002 (AUDIENCES_DIR) | Covered |
| REQ EP-004, C-CMP-006 | JSON config for dimensions/phases | IN-003 (CONFIG_FILE) | Covered |
| COMPOSITION_SPEC IM-001 to IM-006 | Filesystem, audience files, config | IN-001, IN-002, IN-003 | Covered |
| RUNTIME_IMPL Configuration section | config.json with dimensions, phases, rendering | IN-003 | Covered |

### Output Artifact Coverage

| Requirement Source | Required Output | Contract Coverage | Status |
|---|---|---|---|
| REQ OUT-001 | Audience-specific meta content | OUT-001 (AUDIENCE_META_CONTENT) | Covered |
| REQ OUT-002 | Structural health analysis | OUT-002 (STRUCTURAL_HEALTH_REPORT) | Covered |
| REQ OUT-003 | Security audit findings | OUT-003 (SECURITY_AUDIT_REPORT) | Covered |
| REQ TR-007 | Output validation / manifest | OUT-004 (RUN_MANIFEST) | Covered |
| COMPOSITION_SPEC OM-001 | Audience reports | OUT-001 | Covered |
| COMPOSITION_SPEC OM-002 | Health report | OUT-002 | Covered |
| COMPOSITION_SPEC OM-003 | Security report | OUT-003 | Covered |
| COMPOSITIONSPEC OM-004 | Run assembly manifest | OUT-004 | Covered |
| RUNTIME_IMPL Output File Naming | audience_*.md, health_report.md, security_report.md, RUN_MANIFEST.md | OUT-001 to OUT-004 | Covered |
| INV-022 | At least 3 output types | OUT-001, OUT-002, OUT-003 | Covered |

### Intermediate Artifact Coverage

| Meta Component | Contract Coverage | Stage Produced | Stage Consumed | Status |
|---|---|---|---|---|
| Component 1 (FileEntry) | Embedded in INT-001 | TS-001 | TS-002, TS-003 | Covered |
| Component 2 (FileInventory) | INT-001 | TS-001 | TS-002 to TS-005 | Covered |
| Component 3 (ImportEdge) | Embedded in INT-002 | TS-002 | TS-004 | Covered |
| Component 4 (ImportGraph) | INT-002 | TS-002 | TS-004 | Covered |
| Component 5 (SourceSymbol) | INT-003 | TS-002 | TS-003, TS-004, TS-005 | Covered |
| Component 6 (AudienceDefinition) | Parsed from IN-002 | IN-002 (external) | TS-003 | Covered |
| Component 7 (AnalysisDimension) | From IN-003 config | IN-003 (external) | TS-004 | Covered |
| Component 8 (SecurityPhase) | From IN-003 config | IN-003 (external) | TS-005 | Covered |
| Component 9 (SeverityRating) | Embedded in INT-004, INT-005 | TS-004, TS-005 | TS-006 | Covered |
| Component 10 (Evidence) | Embedded in INT-004, INT-005 | TS-004, TS-005 | TS-006 | Covered |
| Component 11 (Finding) | INT-004, INT-005 | TS-004, TS-005 | TS-006 | Covered |
| Component 12 (OutputDocument) | Realized in OUT-001 to OUT-003 | TS-003, TS-006 | TS-007 | Covered |
| Component 13 (OutputSection) | Embedded in OUT-001 to OUT-003 | TS-003, TS-006 | TS-007 | Covered |
| Component 14 (RunManifest) | OUT-004 | TS-007 | External consumer | Covered |

### Stage-to-Artifact Traceability

| Stage | Inputs | Outputs | Invariants Checked | Contract Artifacts |
|---|---|---|---|---|
| TS-001 | IN-001 | INT-001, INT-006 | INV-001 to INV-003 | Covered |
| TS-002 | INT-001 | INT-002, INT-003, INT-006 | INV-004 to INV-006 | Covered |
| TS-003 | INT-001, INT-003, IN-002 | OUT-001 | INV-007 to INV-009 | Covered |
| TS-004 | INT-002, INT-003, IN-003 | INT-004 | INV-010 to INV-013 | Covered |
| TS-005 | INT-001, INT-003, IN-003 | INT-005 | INV-014 to INV-018 | Covered |
| TS-006 | INT-004, INT-005 | OUT-002, OUT-003 | INV-019 to INV-021 | Covered |
| TS-007 | OUT-001, OUT-002, OUT-003, INT-006 | OUT-004 | INV-022 to INV-024 | Covered |

### Completeness Checklist

- [x] All 3 input artifacts from requirement analysis are listed (IN-001 to IN-003).
- [x] All 4 output artifacts from requirement analysis are listed (OUT-001 to OUT-004).
- [x] All 6 intermediate artifacts covering 14 meta components are listed (INT-001 to INT-006).
- [x] Path patterns are consistent across all artifacts (no absolute paths, placeholder tokens used).
- [x] Dependency graph covers all 7 pipeline stages.
- [x] Processing order constraints match COMPOSITION_SPEC transformation rules.
- [x] Required vs optional status is defined for every artifact.
- [x] Naming conventions match RUNTIME_IMPL output file naming table.
- [x] All 24 invariants (INV-001 to INV-024) trace to specific artifacts.
- [x] Minimum 3 output types constraint (INV-022) is addressed.
- [x] No scope invention: all content traces to requirement analysis, composition spec, or runtime implementation.
- [x] ASCII-only: no em-dashes, curly quotes, or Unicode characters.
- [x] YAML frontmatter includes required fields: doc_type ("artifact_contract"), identity_locked (true).

---

**End of Artifact Contract**
