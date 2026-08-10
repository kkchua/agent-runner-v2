---
doc_type: "composition_standard"
identity_locked: true
codename: "codebase_intelligence"
generator_name: "Codebase Intelligence Generator"
version: "1.0.0"
base_standard_ref: "BASE_COMPOSITION_STANDARD_v1.0.md"
pattern: "input_transformation"
layer_count: 3
meta_component_count: 14
stage_count: 7
invariant_count: 24
extension_point_count: 6
---

# Composition Standard: Codebase Intelligence Generator

## Overview

This document is the generator-specific composition standard for
codebase_intelligence. It is derived from BASE_COMPOSITION_STANDARD_v1.0.md
and adapted to the codebase intelligence domain. It defines the meta schema,
transformation rules, invariants, extension interfaces, and output contract
that all runtime implementations must satisfy.

**Codename:** codebase_intelligence

**Composition pattern:** Pattern 2 -- Input Transformation

**Identity locked:** No downstream configuration may override or
substitute the codename, generator name, or version.

---

## 1. Three-Layer Architecture

The codebase_intelligence generator follows the Input Transformation
pattern with three layers:

| Layer | Name | Responsibility | Components |
|---|---|---|---|
| Layer 1 | Input Parsing | Parse codebase files into structured meta components | FileEntry, FileInventory, ImportEdge, ImportGraph, SourceSymbol, AudienceDefinition |
| Layer 2 | Transformation | Analyze meta components to produce findings | AnalysisDimension, SecurityPhase, SeverityRating, Evidence, Finding |
| Layer 3 | Output Rendering | Serialize output documents to files | OutputDocument, OutputSection, RunManifest |

### Data Flow

```
Raw Filesystem (repository_root)
    |
    v
[TS-001: Codebase Scan] --> FileInventory (INT-001)
    |
    v
[TS-002: Import Graph Construction] --> ImportGraph (INT-002), SourceSymbol[] (INT-003)
    |
    +---> [TS-003: Audience Analysis] --> OutputDocument[] per audience
    |
    +---> [TS-004: Health Dimension Analysis] --> Finding[] (INT-004)
    |
    +---> [TS-005: Security Phase Analysis] --> Finding[] (INT-005)
    |
    v
[TS-006: Findings Report Assembly] --> OutputDocument[] (health + security)
    |
    v
[TS-007: Output Validation] --> RunManifest (OUT-004)
    |
    v
[Output Rendering] --> Concrete files (Markdown)
```

### Processing Order Constraints

```
TS-001 -> TS-002 -> TS-003 (audience analysis)
                  |-> TS-004 (health analysis)  --> TS-006 --> TS-007
                  |-> TS-005 (security analysis) -/
```

TS-003, TS-004, and TS-005 may execute in parallel after TS-002
completes, as they are independent analysis units.

---

## 2. Meta Schema

The meta schema consists of 14 component types organized across
three layers.

### Layer 1 Components (Input Parsing)

#### Component 1: FileEntry

Represents a single file discovered in the codebase.

| Property | Type | Required | Description |
|---|---|---|---|
| file_path | string | Yes | Relative path from codebase root |
| file_type | enum | Yes | documentation, source_code, configuration, other |
| encoding | string | Yes | Must be UTF-8 |
| size_bytes | integer | Yes | File size in bytes |
| is_parseable | boolean | Yes | Whether type-specific parsing succeeded |
| parse_errors | array | No | Parse error messages if not parseable |

Validation: file_path must be non-empty relative path. file_type
must be one of four defined values. Documentation files must be
non-empty Markdown. Python files must be AST-parseable.

#### Component 2: FileInventory

Aggregated collection of all FileEntry components.

| Property | Type | Required | Description |
|---|---|---|---|
| entries | array | Yes | List of FileEntry components |
| doc_count | integer | Yes | Count of documentation files |
| source_count | integer | Yes | Count of Python source files |
| config_count | integer | Yes | Count of configuration files |
| other_count | integer | Yes | Count of uncategorized files |
| has_python_package | boolean | Yes | At least one Python package directory exists |
| has_doc_directory | boolean | Yes | At least one documentation directory exists |

Validation: entries must not be empty (INV-001). has_python_package
must be true (INV-002). has_doc_directory must be true (INV-003).

#### Component 3: ImportEdge

A single directed dependency edge in the import graph.

| Property | Type | Required | Description |
|---|---|---|---|
| source_module | string | Yes | Fully qualified module containing the import |
| target_module | string | Yes | Fully qualified module being imported |
| import_type | enum | Yes | absolute or relative |
| original_import | string | Yes | Raw import statement text |
| line_number | integer | Yes | Line number in source file |

#### Component 4: ImportGraph

Complete directed dependency graph from all ImportEdge components.

| Property | Type | Required | Description |
|---|---|---|---|
| edges | array | Yes | List of ImportEdge components |
| nodes | array | Yes | Set of unique module names |
| node_count | integer | Yes | Number of unique nodes |
| edge_count | integer | Yes | Number of edges |

Validation: All nodes in edges must appear in nodes set. Relative
imports must be resolved (INV-005). Graph must be from AST, not
regex (INV-006).

#### Component 5: SourceSymbol

A named symbol extracted from Python source via AST.

| Property | Type | Required | Description |
|---|---|---|---|
| symbol_name | string | Yes | Name of the symbol |
| symbol_type | enum | Yes | function, class, module, constant |
| file_path | string | Yes | Relative path of containing file |
| line_start | integer | Yes | Starting line number |
| line_end | integer | Yes | Ending line number |
| parameters | array | No | Parameter names (functions only) |
| decorators | array | No | Decorator names |
| docstring | string | No | Extracted docstring |
| is_exported | boolean | Yes | Whether part of public API |

#### Component 6: AudienceDefinition

A parsed audience plugin file from audiences/ directory.

| Property | Type | Required | Description |
|---|---|---|---|
| audience_id | string | Yes | Machine-readable identifier |
| label | string | Yes | Human-readable name |
| tone | string | Yes | Writing tone (technical, executive, operational) |
| focus_areas | array | Yes | Codebase areas to emphasize |
| section_structure | array | Yes | Ordered list of output section names |
| exclude | array | No | Topics to omit |
| source_file | string | Yes | Path to the audience definition .md file |

### Layer 2 Components (Transformation)

#### Component 7: AnalysisDimension

Defines a structural health analysis dimension.

| Property | Type | Required | Description |
|---|---|---|---|
| dimension_id | string | Yes | Unique identifier (e.g., DIM-CIRCULAR) |
| dimension_name | string | Yes | Human-readable name |
| description | string | Yes | What this dimension analyzes |
| enabled | boolean | Yes | Whether active in current run |
| config | object | No | Dimension-specific configuration |

Baseline dimensions: DIM-CIRCULAR, DIM-COUPLING, DIM-DEADCODE,
DIM-COMPLEXITY, DIM-IMPORT.

#### Component 8: SecurityPhase

Defines a security analysis phase.

| Property | Type | Required | Description |
|---|---|---|---|
| phase_id | string | Yes | Unique identifier (e.g., PHASE-SECRETS) |
| phase_name | string | Yes | Human-readable name |
| description | string | Yes | What this phase analyzes |
| enabled | boolean | Yes | Whether active in current run |
| config | object | No | Phase-specific configuration |

Baseline phases: PHASE-SECRETS, PHASE-DEPS, PHASE-CODEPAT,
PHASE-AUTH, PHASE-INFRA.

#### Component 9: SeverityRating

Standardized severity classification shared across all findings.

| Property | Type | Required | Description |
|---|---|---|---|
| level | enum | Yes | critical, high, medium, low, info |
| numeric_weight | integer | Yes | critical=5, high=4, medium=3, low=2, info=1 |

#### Component 10: Evidence

Structured evidence citation for a finding.

| Property | Type | Required | Description |
|---|---|---|---|
| file_path | string | Yes | Relative path to evidence file |
| line_number | integer | No | Line number within file |
| code_snippet | string | No | Relevant code excerpt (redacted for security) |
| description | string | Yes | Human-readable explanation |

Validation: All findings must cite at least one Evidence (INV-010,
INV-014). Secret values must be redacted (INV-017).

#### Component 11: Finding

Core analytical finding from a health dimension or security phase.

| Property | Type | Required | Description |
|---|---|---|---|
| finding_id | string | Yes | Format: {source_id}-{NNN} |
| source_type | enum | Yes | health_dimension or security_phase |
| source_id | string | Yes | dimension_id or phase_id |
| severity | SeverityRating | Yes | Severity classification |
| title | string | Yes | Short descriptive title |
| description | string | Yes | Detailed description |
| evidence | array | Yes | List of Evidence components |
| impact | string | Yes | Impact if unaddressed |
| remediation | string | Yes | Recommended fix |
| is_self_contained | boolean | Yes | Must always be true |

### Layer 3 Components (Output Rendering)

#### Component 12: OutputDocument

Generic interface for all output documents (output-type-agnostic).

| Property | Type | Required | Description |
|---|---|---|---|
| document_id | string | Yes | Unique identifier |
| output_type | string | Yes | Classifier (audience_report, health_report, security_report) |
| title | string | Yes | Human-readable title |
| sections | array | Yes | Ordered list of OutputSection |
| metadata | object | Yes | Document-level metadata |
| is_self_contained | boolean | Yes | Must always be true |

#### Component 13: OutputSection

A named section within an OutputDocument.

| Property | Type | Required | Description |
|---|---|---|---|
| section_id | string | Yes | Unique within parent document |
| section_name | string | Yes | Human-readable heading |
| content | string | No | Free-form text content |
| findings | array | No | Finding components rendered in section |
| subsections | array | No | Child OutputSection components |

#### Component 14: RunManifest

Top-level manifest for a complete generator run.

| Property | Type | Required | Description |
|---|---|---|---|
| run_id | string | Yes | Unique run identifier |
| codename | string | Yes | Always "codebase_intelligence" |
| output_count | integer | Yes | Number of OutputDocument components |
| output_types | array | Yes | List of distinct output_type values |
| documents | array | Yes | List of OutputDocument components |
| generation_date | string | Yes | YYYY-MM-DD format |
| output_type_count | integer | Yes | Must be >= 3 |

---

## 3. Transformation Pipeline

Seven stages transform input into output. Each stage has defined
inputs, outputs, and invariants.

### Stage TS-001: Codebase Scan

**Input:** Raw filesystem (repository_root)
**Output:** FileInventory (Component 2)
**Invariants:** INV-001, INV-002, INV-003

Recursively walk the repository root. For each file, create a
FileEntry by classifying file_type based on extension. Aggregate
into FileInventory with counts and structural flags.

### Stage TS-002: Import Graph Construction

**Input:** FileInventory (source_code entries)
**Output:** ImportGraph (Component 4), SourceSymbol[] (Component 5)
**Invariants:** INV-004, INV-005, INV-006

Parse each Python source file using AST. Extract ImportEdge components
from Import and ImportFrom nodes. Resolve relative imports to absolute
paths. Extract SourceSymbol components from top-level definitions.
Build ImportGraph from all edges.

### Stage TS-003: Audience Analysis

**Input:** FileInventory, SourceSymbol[], AudienceDefinition[]
**Output:** OutputDocument[] (one per audience)
**Invariants:** INV-007, INV-008, INV-009

For each AudienceDefinition, filter FileInventory by focus_areas,
build OutputSections following section_structure order, apply tone,
exclude specified topics. Produce one self-contained OutputDocument
per audience.

### Stage TS-004: Health Dimension Analysis

**Input:** ImportGraph, SourceSymbol[], FileInventory, AnalysisDimension[]
**Output:** Finding[] (health findings)
**Invariants:** INV-010, INV-011, INV-012, INV-013

For each enabled dimension, run analysis via DIMENSION_REGISTRY
dispatch. DIM-CIRCULAR uses Tarjan SCC. DIM-COUPLING computes
fan-in/fan-out. DIM-DEADCODE finds unreferenced symbols.
DIM-COMPLEXITY computes cyclomatic complexity. DIM-IMPORT scans
for anti-patterns.

### Stage TS-005: Security Phase Analysis

**Input:** FileInventory, SourceSymbol[], SecurityPhase[]
**Output:** Finding[] (security findings)
**Invariants:** INV-014, INV-015, INV-016, INV-017, INV-018

For each enabled phase, run analysis via PHASE_REGISTRY dispatch.
PHASE-SECRETS pattern scans for hardcoded secrets. PHASE-DEPS audits
dependencies. PHASE-CODEPAT scans for insecure patterns. PHASE-AUTH
reviews auth implementations. PHASE-INFRA checks deployment config.
All secret values must be redacted from evidence (INV-017).

### Stage TS-006: Findings Report Assembly

**Input:** Finding[] from TS-004 and TS-005
**Output:** OutputDocument[] (health report, security report)
**Invariants:** INV-019, INV-020, INV-021

Group health findings by dimension_id into one OutputDocument.
Group security findings by phase_id into another OutputDocument.
Sort findings by severity (critical first). Ensure each section
is self-contained.

### Stage TS-007: Output Validation

**Input:** All OutputDocument components
**Output:** RunManifest (Component 14)
**Invariants:** INV-022, INV-023, INV-024

Collect all OutputDocuments. Verify output_type_count >= 3 (INV-022).
Verify all documents are self-contained (INV-023). Verify no
unresolved references (INV-024). Build RunManifest.

---

## 4. Invariants

24 invariants must hold at all times during pipeline execution.

| ID | Stage | Description | Severity |
|---|---|---|---|
| INV-001 | TS-001 | FileInventory.entries is non-empty | CRITICAL |
| INV-002 | TS-001 | has_python_package is true | CRITICAL |
| INV-003 | TS-001 | has_doc_directory is true | CRITICAL |
| INV-004 | TS-002 | ImportGraph has nodes for all source files | HIGH |
| INV-005 | TS-002 | Relative imports resolved to absolute | HIGH |
| INV-006 | TS-002 | Graph constructed from AST, not regex | CRITICAL |
| INV-007 | TS-003 | One OutputDocument per audience | HIGH |
| INV-008 | TS-003 | No hallucinated content | CRITICAL |
| INV-009 | TS-003 | Audience fidelity (tone/structure match) | CRITICAL |
| INV-010 | TS-004 | Findings cite evidence | CRITICAL |
| INV-011 | TS-004 | Severity consistency | CRITICAL |
| INV-012 | TS-004 | Dimension independence | HIGH |
| INV-013 | TS-004 | Disabled dimensions produce no findings | HIGH |
| INV-014 | TS-005 | Security findings cite evidence | CRITICAL |
| INV-015 | TS-005 | Security severity consistency | CRITICAL |
| INV-016 | TS-005 | Phase independence | HIGH |
| INV-017 | TS-005 | Secret redaction | CRITICAL |
| INV-018 | TS-005 | Disabled phases produce no findings | HIGH |
| INV-019 | TS-006 | Health report has one section per dimension | HIGH |
| INV-020 | TS-006 | Security report has one section per phase | HIGH |
| INV-021 | TS-006 | Findings match section source | HIGH |
| INV-022 | TS-007 | At least 3 output types | CRITICAL |
| INV-023 | TS-007 | Self-contained outputs | CRITICAL |
| INV-024 | TS-007 | No unresolved references | HIGH |

Invariant violations halt the pipeline immediately. INV-017
(secret redaction failure) is unrecoverable.

---

## 5. Constraints

### Format Constraints

| ID | Description |
|---|---|
| C-FMT-001 | Input documentation is Rich Markdown |
| C-FMT-002 | Input source code is Python |
| C-FMT-003 | Input encoding is UTF-8 |
| C-FMT-004 | Import analysis uses AST, not regex |
| C-FMT-005 | All findings use consistent 5-level severity scale |
| C-FMT-006 | Reports are self-contained |
| C-FMT-007 | All findings cite evidence |

### Compatibility Constraints

| ID | Description |
|---|---|
| C-CMP-001 | No hallucination -- only report what exists |
| C-CMP-002 | Secret values must be redacted |
| C-CMP-003 | Audience fidelity -- tone/structure match definition |
| C-CMP-004 | Dimension/phase independence |
| C-CMP-005 | Plugin extensibility for audiences |
| C-CMP-006 | Configurable scope via JSON config |

---

## 6. Extension Interfaces

Three Protocol interfaces define extension contracts.

### InputParser Protocol

| Method | Signature | Purpose |
|---|---|---|
| parse_file | (file_path: str) -> FileEntry | Parse single file |
| parse_imports | (file_path: str) -> list[ImportEdge] | Extract imports via AST |
| parse_symbols | (file_path: str) -> list[SourceSymbol] | Extract symbols via AST |
| parse_audience | (file_path: str) -> AudienceDefinition | Parse audience definition |

### AnalysisEngine Protocol

| Method | Signature | Purpose |
|---|---|---|
| run_dimension | (dimension, graph, symbols, inventory, config) -> list[Finding] | Run health dimension |
| run_phase | (phase, inventory, symbols, config) -> list[Finding] | Run security phase |

### OutputRenderer Protocol

| Method | Signature | Purpose |
|---|---|---|
| render_document | (document: OutputDocument) -> str | Render document to string |
| render_manifest | (manifest: RunManifest) -> str | Render manifest to string |
| supported_formats | () -> list[str] | List supported formats |

### Extension Registries

| Registry | Keys | Values |
|---|---|---|
| DIMENSION_REGISTRY | dimension_id strings | DimensionAnalyzer instances |
| PHASE_REGISTRY | phase_id strings | PhaseAnalyzer instances |
| RENDERER_REGISTRY | format name strings | OutputRenderer instances |

---

## 7. Extension Points

| ID | Extension | How to Extend |
|---|---|---|
| EXT-001 | Custom Audiences | Drop .md file in audiences/ dir |
| EXT-002 | Custom Health Dimensions | Implement AnalysisEngine.run_dimension, register |
| EXT-003 | Custom Security Phases | Implement AnalysisEngine.run_phase, register |
| EXT-004 | Configurable Thresholds | Modify dimension/phase config |
| EXT-005 | Output Formats | Implement OutputRenderer, register |
| EXT-006 | Incremental Analysis | Add cache layer to InputParser |

---

## 8. Output Contract

The generator MUST produce at least 3 distinct output types per
run (INV-022). The baseline output types are:

| Output Type | Artifact Key | Description |
|---|---|---|
| audience_report | AUDIENCE_META_CONTENT | One per audience definition |
| health_report | STRUCTURAL_HEALTH_REPORT | Health dimension findings |
| security_report | SECURITY_AUDIT_REPORT | Security phase findings |
| run_manifest | RUN_MANIFEST | Run-level metadata |

When no audience definitions are provided, a default codebase
overview report is produced as a third output type to satisfy
INV-022.

All output documents must satisfy:
- is_self_contained = true (INV-023)
- No unresolved references (INV-024)
- Evidence-backed findings (INV-010, INV-014)
- Standard severity scale (INV-011, INV-015)
- Secret values redacted (INV-017)

---

## 9. Error Handling

| Error Type | Handling |
|---|---|
| File read failure | Record in parse_errors, continue scan |
| AST parse failure | Record in parse_errors, skip file |
| Missing audience directory | Log warning, skip audience analysis |
| Invalid audience definition | Skip audience, continue with valid ones |
| Empty findings for dimension/phase | Produce section with "No findings" |
| Invariant violation | Halt pipeline, report failed invariant |
| Secret redaction failure | Halt with critical error (unrecoverable) |

---

## 10. Self-Validation

| Check | Status |
|---|---|
| 14 meta components defined across 3 layers | PASS |
| 7 transformation stages defined | PASS |
| 24 invariants defined with stage mapping | PASS |
| 13 constraints covered | PASS |
| 3 Protocol interfaces defined | PASS |
| 6 extension points documented | PASS |
| Output-type-agnostic design | PASS |
| ASCII-only content | PASS |
| YAML frontmatter complete | PASS |
| Governance paths use filenames only | PASS |
| Identity locked to codebase_intelligence | PASS |

---

**End of Composition Standard**
