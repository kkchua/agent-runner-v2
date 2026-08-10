---
doc_type: "composition_spec"
identity_locked: true
codename: "codebase_intelligence"
generator_name: "Codebase Intelligence Generator"
spec_version: "1.0.0"
base_standard_reference: "BASE_COMPOSITION_STANDARD_v1.0.md"
pattern: "input_transformation"
layer_count: 3
meta_component_count: 14
requirement_analysis_ref: "REQUIREMENT_ANALYSIS-01.md"
---

# Composition Specification: Codebase Intelligence Generator

## Overview

**Codename:** codebase_intelligence

**Spec version:** 1.0.0

**Composition pattern:** Pattern 2 -- Input Transformation (per BASE_COMPOSITION_STANDARD)

**Scope:** This specification defines the transformation contract for the codebase intelligence generator. It establishes the meta schema (intermediate representation), the input mapping (how codebase content decomposes into meta components), the transformation rules (how meta content is analyzed and composed), the output contract (generic interface for rendering), and the extension mechanism (how new analysis types and output formats plug in).

**Output-type-agnostic design:** This spec does NOT hardcode any specific output type. It defines a generic OutputDocument interface that multiple runtime implementations can satisfy. The requirement document specifies that the generator MUST produce at least 3 different types of output artifacts. The actual output types are determined at runtime by the LLM based on codebase content. This spec provides the structural contract that all output types must satisfy.

**Traceability:** All content in this specification traces to the requirement analysis (REQUIREMENT_ANALYSIS-01.md), the requirement document (codebase_intelligence.md), and the base composition standard (BASE_COMPOSITION_STANDARD_v1.0.md). No scope is invented beyond what these inputs declare or what is explicitly labeled as an assumption.

---

## Meta Schema Definition

This section defines the intermediate representation (meta schema) for the codebase intelligence generator. The meta schema consists of 14 component types organized across three layers following the Input Transformation pattern.

### Layer 1 Components: Input Parsing

Layer 1 decomposes the raw codebase input into structured meta components. These components represent the parsed form of the codebase -- file inventory, import graph, source symbols, and audience definitions.

#### Component 1: FileEntry

**Purpose:** Represents a single file discovered in the codebase.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| file_path | string | Yes | Relative path from codebase root. |
| file_type | enum | Yes | One of: documentation, source_code, configuration, other. |
| encoding | string | Yes | File encoding. Must be UTF-8. |
| size_bytes | integer | Yes | File size in bytes. |
| is_parseable | boolean | Yes | Whether the file can be parsed by its type parser. |
| parse_errors | array | No | List of parse error messages if is_parseable is false. |

**Validation rules:**
- file_path must be a non-empty relative path.
- file_type must be one of the four defined enum values.
- Documentation files must be non-empty Markdown content (V-IN-003).
- Python source files must be syntactically valid per Python AST (V-IN-002).

**Traceability:** REQ IN-001, V-IN-001 through V-IN-003.

#### Component 2: FileInventory

**Purpose:** Aggregated collection of all FileEntry components discovered during the scan phase. Provides categorized views of the codebase.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| entries | array | Yes | List of FileEntry components. |
| doc_count | integer | Yes | Count of documentation files. |
| source_count | integer | Yes | Count of Python source files. |
| config_count | integer | Yes | Count of configuration files. |
| other_count | integer | Yes | Count of uncategorized files. |
| has_python_package | boolean | Yes | Whether at least one Python package directory exists. |
| has_doc_directory | boolean | Yes | Whether at least one documentation directory exists. |

**Validation rules:**
- entries must not be empty (V-IN-004).
- has_python_package must be true (V-IN-004).
- has_doc_directory must be true (V-IN-004).
- doc_count + source_count + config_count + other_count must equal len(entries).

**Traceability:** REQ TR-001, V-IN-004.

#### Component 3: ImportEdge

**Purpose:** Represents a single directed dependency edge in the import graph. One module imports another.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| source_module | string | Yes | Fully qualified module name that contains the import. |
| target_module | string | Yes | Fully qualified module name being imported. |
| import_type | enum | Yes | One of: absolute, relative. |
| original_import | string | Yes | The original import statement text from source. |
| line_number | integer | Yes | Line number in source file where import appears. |

**Validation rules:**
- source_module and target_module must be non-empty strings.
- import_type must be one of the two enum values.
- Relative imports must be resolved to absolute module paths before graph construction.

**Traceability:** REQ TR-002, C-FMT-004.

#### Component 4: ImportGraph

**Purpose:** Complete directed dependency graph constructed from all ImportEdge components. The graph is the basis for circular dependency detection and coupling metrics.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| edges | array | Yes | List of ImportEdge components. |
| nodes | array | Yes | Set of unique module names (both source and target). |
| node_count | integer | Yes | Number of unique nodes. |
| edge_count | integer | Yes | Number of edges. |
| is_acyclic | boolean | Computed | Whether the graph contains cycles (computed during analysis). |

**Validation rules:**
- All nodes referenced in edges must appear in the nodes set.
- Relative imports must be resolved before the graph is considered complete.
- The graph must be constructed from Python AST parsing, not regex (C-FMT-004).

**Traceability:** REQ TR-002, C-FMT-004.

#### Component 5: SourceSymbol

**Purpose:** Represents a named symbol extracted from Python source code via AST parsing -- a function, class, or module-level definition.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| symbol_name | string | Yes | Name of the symbol. |
| symbol_type | enum | Yes | One of: function, class, module, constant. |
| file_path | string | Yes | Relative path of the source file containing this symbol. |
| line_start | integer | Yes | Starting line number. |
| line_end | integer | Yes | Ending line number. |
| parameters | array | No | List of parameter names (for functions). |
| decorators | array | No | List of decorator names. |
| docstring | string | No | Extracted docstring if present. |
| is_exported | boolean | Yes | Whether the symbol is part of the module public API. |

**Validation rules:**
- symbol_name must be non-empty.
- symbol_type must be one of the four enum values.
- file_path must reference an existing FileEntry.
- line_start must be less than or equal to line_end.

**Traceability:** REQ TR-001, TR-002.

#### Component 6: AudienceDefinition

**Purpose:** Represents a parsed audience plugin file from the audiences/ directory. Defines how codebase content should be filtered and presented for a specific stakeholder group.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| audience_id | string | Yes | Machine-readable identifier for this audience. |
| label | string | Yes | Human-readable audience name. |
| tone | string | Yes | Writing tone for this audience (e.g., technical, executive, operational). |
| focus_areas | array | Yes | List of codebase areas to emphasize. |
| section_structure | array | Yes | Ordered list of output section names. |
| exclude | array | No | List of topics to omit from output. |
| source_file | string | Yes | Path to the audience definition .md file. |

**Validation rules:**
- audience_id must be unique across all AudienceDefinition components.
- focus_areas must contain at least one entry.
- section_structure must contain at least one entry.
- source_file must reference an existing file.

**Traceability:** REQ EP-001, C-CMP-003, C-CMP-005.

### Layer 2 Components: Transformation

Layer 2 represents the analytical results produced by applying transformations to Layer 1 components. These include analysis dimensions, security phases, findings, and severity assessments.

#### Component 7: AnalysisDimension

**Purpose:** Defines a structural health analysis dimension. Each dimension is an independent unit of analysis that can be enabled or disabled via configuration.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| dimension_id | string | Yes | Unique identifier for this dimension. |
| dimension_name | string | Yes | Human-readable name. |
| description | string | Yes | What this dimension analyzes. |
| enabled | boolean | Yes | Whether this dimension is active in the current run. |
| config | object | No | Dimension-specific configuration (thresholds, parameters). |

**Domain instances (5 baseline dimensions):**

| dimension_id | dimension_name | Description |
|---|---|---|
| DIM-CIRCULAR | Circular Dependencies | Detect cycles in the import graph. |
| DIM-COUPLING | Coupling Metrics | Compute coupling between modules/packages. |
| DIM-DEADCODE | Dead Code | Identify unused functions, classes, modules. |
| DIM-COMPLEXITY | Complexity Analysis | Compute complexity metrics for functions/modules. |
| DIM-IMPORT | Import Discipline | Analyze import patterns for violations. |

**Validation rules:**
- dimension_id must be unique across all AnalysisDimension components.
- Each dimension must be self-contained and able to run independently (C-CMP-004).

**Traceability:** REQ OUT-002, TR-004, EP-002.

#### Component 8: SecurityPhase

**Purpose:** Defines a security analysis phase. Each phase is an independent unit of security analysis that can be enabled or disabled via configuration.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| phase_id | string | Yes | Unique identifier for this phase. |
| phase_name | string | Yes | Human-readable name. |
| description | string | Yes | What this phase analyzes. |
| enabled | boolean | Yes | Whether this phase is active in the current run. |
| config | object | No | Phase-specific configuration (patterns, databases). |

**Domain instances (5 baseline phases):**

| phase_id | phase_name | Description |
|---|---|---|
| PHASE-SECRETS | Secrets Detection | Pattern scan for hardcoded secrets. |
| PHASE-DEPS | Dependencies Audit | Known vulnerable dependencies. |
| PHASE-CODEPAT | Code Patterns Scan | Insecure coding patterns. |
| PHASE-AUTH | Authentication Review | Auth implementation issues. |
| PHASE-INFRA | Infrastructure Check | Deployment/configuration issues. |

**Validation rules:**
- phase_id must be unique across all SecurityPhase components.
- Each phase must be self-contained and able to run independently (C-CMP-004).

**Traceability:** REQ OUT-003, TR-005, EP-003.

#### Component 9: SeverityRating

**Purpose:** Standardized severity classification for all findings. Shared across health dimensions and security phases.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| level | enum | Yes | One of: critical, high, medium, low, info. |
| numeric_weight | integer | Yes | Numeric weight for sorting (critical=5, high=4, medium=3, low=2, info=1). |

**Validation rules:**
- level must be one of the five enum values.
- All findings across all dimensions and phases must use this same severity scale (C-FMT-005).

**Traceability:** REQ Q-OUT-006, Q-OUT-010, C-FMT-005.

#### Component 10: Evidence

**Purpose:** Structured evidence citation for a finding. Every finding must include evidence pointing to specific codebase locations.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| file_path | string | Yes | Relative path to the file containing the evidence. |
| line_number | integer | No | Line number within the file. |
| code_snippet | string | No | Relevant code excerpt. |
| description | string | Yes | Human-readable explanation of what the evidence shows. |

**Validation rules:**
- file_path must reference an existing FileEntry.
- All findings must cite at least one Evidence component (C-FMT-007).
- For security findings, actual secret values must be redacted from code_snippet (C-CMP-002).

**Traceability:** REQ Q-OUT-004, Q-OUT-008, C-FMT-007, C-CMP-002.

#### Component 11: Finding

**Purpose:** A structured analytical finding produced by either a health dimension or a security phase. This is the core output unit of the transformation layer.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| finding_id | string | Yes | Unique identifier. Format: {DIMENSION_OR_PHASE_ID}-{NNN}. |
| source_type | enum | Yes | One of: health_dimension, security_phase. |
| source_id | string | Yes | The dimension_id or phase_id that produced this finding. |
| severity | SeverityRating | Yes | Severity classification. |
| title | string | Yes | Short descriptive title. |
| description | string | Yes | Detailed description of the finding. |
| evidence | array | Yes | List of Evidence components supporting this finding. |
| impact | string | Yes | Assessment of the impact if unaddressed. |
| remediation | string | Yes | Recommended fix or mitigation. |
| is_self_contained | boolean | Yes | Whether this finding can be understood without external context. |

**Validation rules:**
- finding_id must be unique across all Finding components.
- source_id must reference an existing AnalysisDimension or SecurityPhase.
- evidence must contain at least one Evidence component (C-FMT-007).
- is_self_contained must be true (C-FMT-006).
- Severity must use the standard SeverityRating scale (C-FMT-005).

**Traceability:** REQ TR-006, Q-OUT-004, Q-OUT-007, Q-OUT-008, C-FMT-005, C-FMT-006, C-FMT-007.

### Layer 3 Components: Output Rendering

Layer 3 defines the generic output interface. The design is output-type-agnostic per BASE_COMPOSITION_STANDARD Section 13. Runtime implementations specialize these components to produce specific output types.

#### Component 12: OutputDocument

**Purpose:** Generic interface for all output documents. This is the central abstraction that makes the spec output-type-agnostic. Each output document has a type, structured content, and metadata.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| document_id | string | Yes | Unique identifier for this output document. |
| output_type | string | Yes | Classifier for the type of output (e.g., audience_report, health_report, security_report). |
| title | string | Yes | Human-readable document title. |
| sections | array | Yes | Ordered list of OutputSection components. |
| metadata | object | Yes | Document-level metadata (generation date, source version, etc.). |
| is_self_contained | boolean | Yes | Whether the document is readable without reference to source files. |

**Validation rules:**
- document_id must be unique across all OutputDocument components.
- output_type must be a non-empty string.
- sections must contain at least one OutputSection.
- is_self_contained must be true (C-FMT-006, Q-OUT-002).
- metadata must include generation_date and source reference.

**Traceability:** REQ OUT-001, OUT-002, OUT-003, Section 13 of base standard.

#### Component 13: OutputSection

**Purpose:** A named section within an OutputDocument. Sections are ordered and may contain text content and/or rendered findings.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| section_id | string | Yes | Unique identifier within the parent document. |
| section_name | string | Yes | Human-readable section heading. |
| content | string | No | Free-form text content for this section. |
| findings | array | No | List of Finding components rendered in this section. |
| subsections | array | No | Ordered list of child OutputSection components. |

**Validation rules:**
- section_id must be unique within the parent document.
- If section contains findings, each finding must be from a relevant dimension/phase.
- Section ordering must follow the audience's section_structure for audience reports.

**Traceability:** REQ TR-003, TR-006.

#### Component 14: RunManifest

**Purpose:** Top-level manifest for a complete generator run. Aggregates all output documents and provides run-level metadata.

**Properties:**

| Property | Type | Required | Description |
|---|---|---|---|
| run_id | string | Yes | Unique identifier for this generator run. |
| codename | string | Yes | Generator codename (codebase_intelligence). |
| output_count | integer | Yes | Number of OutputDocument components produced. |
| output_types | array | Yes | List of distinct output_type values across all documents. |
| documents | array | Yes | List of OutputDocument components. |
| generation_date | string | Yes | Date of generation (YYYY-MM-DD). |
| output_type_count | integer | Yes | Count of distinct output types. |

**Validation rules:**
- output_type_count must be at least 3 (requirement: at least 3 different types).
- documents must contain at least 3 OutputDocument components.
- All document_ids must be unique.
- output_types must match the set of output_type values across documents.

**Traceability:** REQ overview (at least 3 different types of output artifacts).

---

## Input Mapping

This section defines how the raw codebase input maps to Layer 1 meta components. The input mapping is the parsing stage of the Input Transformation pattern.

### Input Source

The generator accepts a composite input: codebase documentation (Rich Markdown) and source code (Python). The input is not a single file but a collection of files organized in a repository structure.

### Mapping Rules

#### IM-001: File Discovery to FileEntry

**Source:** All files in the target repository.

**Mapping logic:**
1. Recursively scan the repository root for files.
2. For each file, create a FileEntry component.
3. Classify file_type based on extension:
   - .md files -> documentation
   - .py files -> source_code
   - .toml, .json, .yaml, .cfg files -> configuration
   - All others -> other
4. Set encoding to UTF-8.
5. Attempt to parse the file based on its type. Record parse_errors if parsing fails.

**Validation:** Each FileEntry must satisfy the validation rules defined in Component 1.

**Traceability:** REQ TR-001, V-IN-001.

#### IM-002: File Inventory Assembly

**Source:** All FileEntry components from IM-001.

**Mapping logic:**
1. Aggregate all FileEntry components into a FileInventory.
2. Compute counts by file_type.
3. Check for at least one Python package directory (a directory containing __init__.py).
4. Check for at least one documentation directory.
5. Set has_python_package and has_doc_directory flags.

**Validation:** The FileInventory must satisfy V-IN-004 (at least one package and one doc directory).

**Traceability:** REQ TR-001, V-IN-004.

#### IM-003: Python AST Parse to ImportEdge

**Source:** All FileEntry components where file_type is source_code.

**Mapping logic:**
1. For each Python source file, parse using Python AST (not regex).
2. Walk the AST to find all Import and ImportFrom nodes.
3. For each import statement, create an ImportEdge:
   - source_module: the module containing the import.
   - target_module: the module being imported.
   - import_type: absolute or relative.
   - original_import: the raw import text.
   - line_number: the AST node line number.
4. Resolve relative imports to absolute module paths using the package structure from FileInventory.

**Validation:** Each ImportEdge must satisfy the validation rules in Component 3. Parsing must use AST, not regex (C-FMT-004).

**Traceability:** REQ TR-002, C-FMT-004.

#### IM-004: Import Graph Construction

**Source:** All ImportEdge components from IM-003.

**Mapping logic:**
1. Collect all unique module names from source_module and target_module fields.
2. Build the ImportGraph with nodes and edges.
3. Compute node_count and edge_count.
4. is_acyclic is computed later during transformation (not at input mapping stage).

**Validation:** The ImportGraph must satisfy the validation rules in Component 4.

**Traceability:** REQ TR-002.

#### IM-005: Python AST Parse to SourceSymbol

**Source:** All FileEntry components where file_type is source_code.

**Mapping logic:**
1. For each Python source file, parse using Python AST.
2. Extract all top-level function definitions (FunctionDef, AsyncFunctionDef).
3. Extract all top-level class definitions (ClassDef).
4. Extract module-level constants (assignments at module scope).
5. For each, create a SourceSymbol with extracted properties.
6. Determine is_exported based on naming convention (no leading underscore).

**Validation:** Each SourceSymbol must satisfy the validation rules in Component 5.

**Traceability:** REQ TR-001, TR-002.

#### IM-006: Audience Definition Discovery

**Source:** Audience plugin files (.md) in the audiences/ directory.

**Mapping logic:**
1. Scan the audiences/ directory for .md files.
2. For each file, parse YAML frontmatter.
3. Extract audience_id, label, tone, focus_areas, section_structure, and exclude fields.
4. Create an AudienceDefinition component for each valid file.
5. Files with invalid or missing frontmatter are flagged but do not block the workflow.

**Validation:** Each AudienceDefinition must satisfy the validation rules in Component 6.

**Traceability:** REQ EP-001, C-CMP-005.

### Input Mapping Validation Summary

| Rule ID | Validation | Severity | Checked At |
|---|---|---|---|
| IM-VAL-001 | All files are readable (UTF-8) | CRITICAL | IM-001 |
| IM-VAL-002 | Python files are AST-parseable | CRITICAL | IM-001, IM-003, IM-005 |
| IM-VAL-003 | Documentation files are non-empty Markdown | HIGH | IM-001 |
| IM-VAL-004 | At least one Python package directory exists | CRITICAL | IM-002 |
| IM-VAL-005 | At least one documentation directory exists | CRITICAL | IM-002 |
| IM-VAL-006 | Import analysis uses AST, not regex | CRITICAL | IM-003 |
| IM-VAL-007 | Relative imports resolved to absolute paths | HIGH | IM-003 |
| IM-VAL-008 | Audience definitions have valid frontmatter | HIGH | IM-006 |

---

## Output Mapping

This section defines how Layer 3 meta components (OutputDocument, OutputSection, RunManifest) map to concrete output artifacts. The output mapping is the rendering stage of the Input Transformation pattern.

### Generic Output Contract

The output contract is defined by the OutputDocument interface (Component 12) and RunManifest (Component 14). These are output-type-agnostic. Runtime implementations specialize them to produce specific output types.

### Mapping Rules

#### OM-001: Audience Content to OutputDocument

**Source:** AudienceDefinition (Component 6) + FileInventory (Component 2) + SourceSymbol (Component 5).

**Mapping logic:**
1. For each AudienceDefinition, create an OutputDocument with output_type set to the audience-specific report classifier.
2. Filter FileInventory entries by the audience's focus_areas.
3. Create OutputSection components following the audience's section_structure order.
4. Apply the audience's tone to all section content.
5. Apply the audience's exclude list to filter omitted topics.
6. Set is_self_contained to true.

**Output artifact:** One output file per audience definition.

**Traceability:** REQ OUT-001, TR-003, Q-OUT-001, Q-OUT-002, Q-OUT-003.

#### OM-002: Health Findings to OutputDocument

**Source:** Finding (Component 11) components where source_type is health_dimension.

**Mapping logic:**
1. Group Finding components by source_id (dimension_id).
2. Create an OutputDocument with output_type set to the health report classifier.
3. For each enabled AnalysisDimension, create an OutputSection containing that dimension's findings.
4. Each section is self-contained (can be read independently).
5. Sort findings within each section by severity (critical first).
6. Set is_self_contained to true.

**Output artifact:** One output file for the structural health report.

**Traceability:** REQ OUT-002, TR-004, TR-006, Q-OUT-004, Q-OUT-006, Q-OUT-007.

#### OM-003: Security Findings to OutputDocument

**Source:** Finding (Component 11) components where source_type is security_phase.

**Mapping logic:**
1. Group Finding components by source_id (phase_id).
2. Create an OutputDocument with output_type set to the security report classifier.
3. For each enabled SecurityPhase, create an OutputSection containing that phase's findings.
4. Each section is self-contained (can be read independently).
5. Sort findings within each section by severity (critical first).
6. Redact actual secret values from all evidence code_snippets (C-CMP-002).
7. Set is_self_contained to true.

**Output artifact:** One output file for the security audit report.

**Traceability:** REQ OUT-003, TR-005, TR-006, Q-OUT-008, Q-OUT-009, Q-OUT-010, Q-OUT-011.

#### OM-004: Run Assembly to RunManifest

**Source:** All OutputDocument components produced by OM-001, OM-002, OM-003.

**Mapping logic:**
1. Collect all OutputDocument components.
2. Extract distinct output_type values.
3. Verify output_type_count >= 3.
4. Create RunManifest aggregating all documents and metadata.

**Validation:** RunManifest must satisfy the validation rules in Component 14.

**Traceability:** REQ overview (at least 3 different types).

### Output Validation Summary

| Rule ID | Validation | Severity | Checked At |
|---|---|---|---|
| OM-VAL-001 | Each report is self-contained | CRITICAL | OM-001, OM-002, OM-003 |
| OM-VAL-002 | Audience tone matches definition | CRITICAL | OM-001 |
| OM-VAL-003 | Audience section_structure is followed | CRITICAL | OM-001 |
| OM-VAL-004 | All findings cite evidence | CRITICAL | OM-002, OM-003 |
| OM-VAL-005 | Severity scale is consistent | CRITICAL | OM-002, OM-003 |
| OM-VAL-006 | Secret values are redacted | CRITICAL | OM-003 |
| OM-VAL-007 | Each dimension/phase section is independent | HIGH | OM-002, OM-003 |
| OM-VAL-008 | At least 3 output types produced | CRITICAL | OM-004 |
| OM-VAL-009 | No hallucinated content | CRITICAL | All OM rules |

---

## Transformation Rules

This section defines the core transformation logic that converts Layer 1 (input parsing) components into Layer 2 (analysis) components, which then feed Layer 3 (output rendering).

### Processing Pipeline

The transformation follows a 7-stage pipeline. Each stage has defined inputs, outputs, and invariants.

#### Stage TS-001: Codebase Scan

**Input:** Raw filesystem access to the target repository.

**Output:** FileInventory (Component 2) containing all FileEntry components.

**Processing logic:**
1. Recursively walk the repository root.
2. For each file, apply IM-001 to create a FileEntry.
3. Aggregate into FileInventory (IM-002).

**Invariants:**
- INV-001: FileInventory.entries is non-empty after this stage.
- INV-002: has_python_package is true.
- INV-003: has_doc_directory is true.

**Traceability:** REQ TR-001.

#### Stage TS-002: Import Graph Construction

**Input:** FileInventory (from TS-001), specifically all source_code entries.

**Output:** ImportGraph (Component 4), SourceSymbol set (Component 5).

**Processing logic:**
1. For each Python source file, parse AST (IM-003).
2. Extract ImportEdge components.
3. Build ImportGraph (IM-004).
4. Extract SourceSymbol components (IM-005).

**Invariants:**
- INV-004: ImportGraph.nodes contains at least one entry per Python source file.
- INV-005: All relative imports are resolved to absolute paths.
- INV-006: ImportGraph is constructed from AST, not regex.

**Traceability:** REQ TR-002, C-FMT-004.

#### Stage TS-003: Audience Analysis

**Input:** FileInventory (from TS-001), SourceSymbol set (from TS-002), AudienceDefinition set (from IM-006).

**Output:** Set of OutputDocument components (one per audience).

**Processing logic:**
1. For each AudienceDefinition, apply OM-001 mapping.
2. Filter codebase content by focus_areas.
3. Generate sections following section_structure.
4. Apply tone and exclude filters.

**Invariants:**
- INV-007: Each audience produces exactly one OutputDocument.
- INV-008: Output content derives only from actual codebase content (no hallucination).
- INV-009: Tone and structure match audience definition.

**Traceability:** REQ TR-003, Q-OUT-001, Q-OUT-002, Q-OUT-003.

#### Stage TS-004: Health Dimension Analysis

**Input:** ImportGraph (from TS-002), SourceSymbol set (from TS-002), FileInventory (from TS-001), AnalysisDimension set (from config).

**Output:** Set of Finding components where source_type is health_dimension.

**Processing logic:**
For each enabled AnalysisDimension:
1. DIM-CIRCULAR: Detect cycles in ImportGraph using DFS/Tarjan algorithm.
2. DIM-COUPLING: Compute coupling metrics between modules (fan-in, fan-out).
3. DIM-DEADCODE: Identify symbols not referenced by any import or call.
4. DIM-COMPLEXITY: Compute cyclomatic complexity for functions.
5. DIM-IMPORT: Analyze import patterns for anti-patterns (wildcard imports, circular references).

For each issue found, create a Finding component with severity, evidence, impact, remediation.

**Invariants:**
- INV-010: Each finding cites at least one Evidence component.
- INV-011: All findings use the standard SeverityRating scale.
- INV-012: Each dimension's findings are self-contained.
- INV-013: Disabled dimensions produce no findings.

**Traceability:** REQ TR-004, Q-OUT-004, Q-OUT-006, Q-OUT-007, C-FMT-005, C-FMT-006, C-FMT-007.

#### Stage TS-005: Security Phase Analysis

**Input:** FileInventory (from TS-001), SourceSymbol set (from TS-002), SecurityPhase set (from config).

**Output:** Set of Finding components where source_type is security_phase.

**Processing logic:**
For each enabled SecurityPhase:
1. PHASE-SECRETS: Scan files for hardcoded secrets using pattern matching.
2. PHASE-DEPS: Audit dependencies against known vulnerability databases.
3. PHASE-CODEPAT: Scan for insecure coding patterns (eval, exec, unsanitized input).
4. PHASE-AUTH: Review authentication implementations for weaknesses.
5. PHASE-INFRA: Check deployment configuration for security issues.

For each issue found, create a Finding component. Redact actual secret values from evidence (C-CMP-002).

**Invariants:**
- INV-014: Each finding cites at least one Evidence component.
- INV-015: All findings use the standard SeverityRating scale.
- INV-016: Each phase's findings are self-contained.
- INV-017: Actual secret values are redacted from evidence.
- INV-018: Disabled phases produce no findings.

**Traceability:** REQ TR-005, Q-OUT-008, Q-OUT-009, Q-OUT-010, Q-OUT-011, C-CMP-002.

#### Stage TS-006: Findings Report Assembly

**Input:** Finding components from TS-004 and TS-005.

**Output:** OutputDocument components for health report (OM-002) and security report (OM-003).

**Processing logic:**
1. Group health findings by dimension_id -> OutputDocument (OM-002).
2. Group security findings by phase_id -> OutputDocument (OM-003).
3. Sort findings by severity within each section.
4. Ensure each section is self-contained.

**Invariants:**
- INV-019: Health report OutputDocument has one section per enabled dimension.
- INV-020: Security report OutputDocument has one section per enabled phase.
- INV-021: All findings within a section are from the corresponding dimension/phase.

**Traceability:** REQ TR-006, C-FMT-006.

#### Stage TS-007: Output Validation

**Input:** All OutputDocument components from TS-003 and TS-006.

**Output:** Validated RunManifest (Component 14).

**Processing logic:**
1. Assemble RunManifest from all OutputDocuments (OM-004).
2. Verify output_type_count >= 3.
3. Verify all documents are self-contained.
4. Verify all findings cite evidence.
5. Verify severity consistency.
6. Verify no hallucinated content (all claims trace to codebase).

**Invariants:**
- INV-022: RunManifest.output_type_count >= 3.
- INV-023: All OutputDocument.is_self_contained is true.
- INV-024: No unresolved references to source files remain.

**Traceability:** REQ TR-007, C-FMT-006, C-CMP-001.

### Invariant Summary

| Invariant | Stage | Description | Severity |
|---|---|---|---|
| INV-001 | TS-001 | FileInventory.entries is non-empty | CRITICAL |
| INV-002 | TS-001 | has_python_package is true | CRITICAL |
| INV-003 | TS-001 | has_doc_directory is true | CRITICAL |
| INV-004 | TS-002 | ImportGraph has nodes for all source files | HIGH |
| INV-005 | TS-002 | Relative imports resolved | HIGH |
| INV-006 | TS-002 | AST-based import parsing | CRITICAL |
| INV-007 | TS-003 | One OutputDocument per audience | HIGH |
| INV-008 | TS-003 | No hallucinated content | CRITICAL |
| INV-009 | TS-003 | Audience fidelity | CRITICAL |
| INV-010 | TS-004 | Findings cite evidence | CRITICAL |
| INV-011 | TS-004 | Severity consistency | CRITICAL |
| INV-012 | TS-004 | Dimension independence | HIGH |
| INV-013 | TS-004 | Disabled dimensions produce no findings | HIGH |
| INV-014 | TS-005 | Findings cite evidence | CRITICAL |
| INV-015 | TS-005 | Severity consistency | CRITICAL |
| INV-016 | TS-005 | Phase independence | HIGH |
| INV-017 | TS-005 | Secret redaction | CRITICAL |
| INV-018 | TS-005 | Disabled phases produce no findings | HIGH |
| INV-019 | TS-006 | Health report structure | HIGH |
| INV-020 | TS-006 | Security report structure | HIGH |
| INV-021 | TS-006 | Finding-source alignment | HIGH |
| INV-022 | TS-007 | At least 3 output types | CRITICAL |
| INV-023 | TS-007 | Self-contained outputs | CRITICAL |
| INV-024 | TS-007 | No unresolved references | HIGH |

### Processing Order Constraints

The stages have the following ordering constraints:

```
TS-001 -> TS-002 -> TS-004 (health analysis depends on import graph)
TS-001 -> TS-002 -> TS-005 (security analysis depends on file inventory)
TS-001 -> TS-003 (audience analysis depends on file inventory)
TS-004 -> TS-006 (findings assembly depends on health analysis)
TS-005 -> TS-006 (findings assembly depends on security analysis)
TS-003, TS-006 -> TS-007 (validation depends on all output documents)
```

TS-003, TS-004, and TS-005 can run in parallel after TS-002 completes, as they are independent analysis units.

---

## Extension Mechanism

This section defines how the composition specification supports extension. It specifies what is fixed, what is variable, and what contracts new implementations must follow.

### Fixed Components (Cannot Be Changed by Extensions)

The following are fixed by this specification and must not be altered by extensions:

1. **Three-layer architecture:** Layer 1 (Input Parsing), Layer 2 (Transformation), Layer 3 (Output Rendering). All extensions must operate within this structure.
2. **Common component properties:** All components must have the properties defined in their respective component definitions.
3. **SeverityRating scale:** The five-level severity scale (critical, high, medium, low, info) is fixed.
4. **Evidence requirements:** All findings must cite evidence with file paths.
5. **Self-containment requirement:** All outputs must be self-contained.
6. **No-hallucination constraint:** All output content must trace to actual codebase content.
7. **Minimum 3 output types:** The generator must always produce at least 3 different types.
8. **7-stage processing pipeline:** The stage ordering and invariants are fixed.

### Variable Components (Can Be Extended)

The following are designed for extension:

#### Extension Point EXT-001: Custom Audience Definitions

**What can change:** The set of AudienceDefinition components.

**How to extend:**
1. Create a new .md file in the audiences/ directory.
2. Include YAML frontmatter with required fields: audience_id, label, tone, focus_areas, section_structure.
3. The scan stage (IM-006) discovers the new file automatically.
4. The audience analysis stage (TS-003) produces a new OutputDocument for the new audience.

**What does NOT change:** ImportGraph, AnalysisDimension, SecurityPhase, or any other component type. The pipeline stages, invariants, and output contract remain identical.

**Contract:** The new audience definition must conform to the AudienceDefinition schema (Component 6). The generated OutputDocument must satisfy all output validation rules (OM-VAL-001 through OM-VAL-009).

**Traceability:** REQ EP-001, C-CMP-005.

#### Extension Point EXT-002: Custom Health Dimensions

**What can change:** The set of AnalysisDimension components.

**How to extend:**
1. Define a new AnalysisDimension with a unique dimension_id.
2. Implement the dimension's analysis logic (cycle detection, metric computation, etc.).
3. Register the dimension in the analysis configuration (JSON config).
4. The health dimension analysis stage (TS-004) runs the new dimension.
5. Findings from the new dimension are included in the health report.

**What does NOT change:** ImportGraph construction, security phase analysis, audience analysis, or output contract. The pipeline stages and invariants remain identical.

**Contract:** The new dimension must produce Finding components that satisfy the Finding schema (Component 11). Findings must cite evidence, use the standard severity scale, and be self-contained.

**Traceability:** REQ EP-002, C-CMP-004.

#### Extension Point EXT-003: Custom Security Phases

**What can change:** The set of SecurityPhase components.

**How to extend:**
1. Define a new SecurityPhase with a unique phase_id.
2. Implement the phase's analysis logic (pattern matching, database lookup, etc.).
3. Register the phase in the security configuration (JSON config).
4. The security phase analysis stage (TS-005) runs the new phase.
5. Findings from the new phase are included in the security report.

**What does NOT change:** ImportGraph construction, health dimension analysis, audience analysis, or output contract. The pipeline stages and invariants remain identical.

**Contract:** The new phase must produce Finding components that satisfy the Finding schema (Component 11). Findings must cite evidence, use the standard severity scale, be self-contained, and redact secret values.

**Traceability:** REQ EP-003, C-CMP-004.

#### Extension Point EXT-004: Configurable Thresholds

**What can change:** The config property of AnalysisDimension and SecurityPhase components.

**How to extend:**
1. Define threshold parameters in the dimension/phase config object.
2. The analysis logic reads thresholds from config at runtime.
3. Different threshold values produce different findings (e.g., higher complexity limit means fewer findings).

**What does NOT change:** The component schemas, pipeline stages, or invariants.

**Contract:** Threshold changes must not violate invariants. Findings must still cite evidence, use the standard severity scale, and be self-contained regardless of threshold values.

**Traceability:** REQ EP-004.

#### Extension Point EXT-005: Multiple Output Formats

**What can change:** The rendering of OutputDocument components to concrete file formats.

**How to extend:**
1. Implement a new OutputRenderer that serializes OutputDocument to a specific format (Markdown, JSON, HTML).
2. Register the renderer in the runtime configuration.
3. The output validation stage (TS-007) validates the rendered output regardless of format.

**What does NOT change:** The meta schema (Components 1-14), transformation pipeline, or invariants. Only the final serialization step varies.

**Contract:** The rendered output must preserve all information from the OutputDocument. All findings, evidence, and metadata must be present in the rendered output. Self-containment and no-hallucination constraints apply to all formats.

**Traceability:** REQ EP-005.

#### Extension Point EXT-006: Incremental Analysis

**What can change:** The input parsing stage (TS-001, TS-002) to support re-analyzing only changed files.

**How to extend:**
1. Maintain a cache of previous FileInventory and ImportGraph state.
2. On subsequent runs, detect changed files (by timestamp or hash).
3. Re-parse only changed files. Update the ImportGraph incrementally.
4. Feed the updated components into the existing pipeline from TS-003 onward.

**What does NOT change:** The meta schema, transformation stages TS-003 through TS-007, or invariants.

**Contract:** The incrementally-updated FileInventory and ImportGraph must be identical to what a full re-analysis would produce. All invariants from INV-001 through INV-006 must hold.

**Traceability:** REQ EP-006.

### Runtime Implementation Contract

Any runtime implementation that satisfies this composition spec must:

1. **Implement all 7 transformation stages** (TS-001 through TS-007) in the specified order.
2. **Satisfy all 24 invariants** (INV-001 through INV-024).
3. **Produce at least 3 distinct output types** per run.
4. **Support the 5 baseline dimensions** and **5 baseline phases** as enabled by default.
5. **Support the 6 extension points** (EXT-001 through EXT-006).
6. **Produce OutputDocument components** that satisfy the generic output contract.
7. **Produce a RunManifest** that aggregates all outputs.

### Protocol Interfaces for Extension

Runtime implementations should define Protocol interfaces for the following extension points:

**InputParser Protocol:**
```
InputParser:
  parse_file(file_path: str) -> FileEntry
  parse_imports(file_path: str) -> list[ImportEdge]
  parse_symbols(file_path: str) -> list[SourceSymbol]
  parse_audience(file_path: str) -> AudienceDefinition
```

**AnalysisEngine Protocol:**
```
AnalysisEngine:
  run_dimension(dimension: AnalysisDimension, graph: ImportGraph, symbols: list[SourceSymbol]) -> list[Finding]
  run_phase(phase: SecurityPhase, inventory: FileInventory, symbols: list[SourceSymbol]) -> list[Finding]
```

**OutputRenderer Protocol:**
```
OutputRenderer:
  render_document(document: OutputDocument) -> str
  render_manifest(manifest: RunManifest) -> str
  supported_formats() -> list[str]
```

These protocols define the contracts that extension implementations must satisfy. The protocols are output-type-agnostic. Different implementations can produce different output formats while satisfying the same interface.

---

## Self-Validation

This section verifies the completeness and internal consistency of this composition specification.

### Meta Schema Coverage

| # | Component Name | Layer | Properties Defined | Validation Rules | Traceability |
|---|---|---|---|---|---|
| 1 | FileEntry | Layer 1 | Yes (7) | Yes | IN-001, V-IN-001 to V-IN-003 |
| 2 | FileInventory | Layer 1 | Yes (7) | Yes | TR-001, V-IN-004 |
| 3 | ImportEdge | Layer 1 | Yes (5) | Yes | TR-002, C-FMT-004 |
| 4 | ImportGraph | Layer 1 | Yes (5) | Yes | TR-002, C-FMT-004 |
| 5 | SourceSymbol | Layer 1 | Yes (9) | Yes | TR-001, TR-002 |
| 6 | AudienceDefinition | Layer 1 | Yes (7) | Yes | EP-001, C-CMP-003, C-CMP-005 |
| 7 | AnalysisDimension | Layer 2 | Yes (5) | Yes | OUT-002, TR-004, EP-002 |
| 8 | SecurityPhase | Layer 2 | Yes (5) | Yes | OUT-003, TR-005, EP-003 |
| 9 | SeverityRating | Layer 2 | Yes (2) | Yes | Q-OUT-006, Q-OUT-010, C-FMT-005 |
| 10 | Evidence | Layer 2 | Yes (4) | Yes | Q-OUT-004, Q-OUT-008, C-FMT-007 |
| 11 | Finding | Layer 2 | Yes (10) | Yes | TR-006, C-FMT-005 to C-FMT-007 |
| 12 | OutputDocument | Layer 3 | Yes (6) | Yes | OUT-001 to OUT-003, Section 13 |
| 13 | OutputSection | Layer 3 | Yes (5) | Yes | TR-003, TR-006 |
| 14 | RunManifest | Layer 3 | Yes (7) | Yes | Overview (3 types) |

**Count: 14 meta components defined. Matches frontmatter meta_component_count: 14.**

### Section Coverage

| # | Section Name | Required | Present |
|---|---|---|---|
| 1 | Meta Schema Definition | Yes | Yes |
| 2 | Input Mapping | Yes | Yes |
| 3 | Output Mapping | Yes | Yes |
| 4 | Transformation Rules | Yes | Yes |
| 5 | Extension Mechanism | Yes | Yes |
| 6 | Self-Validation | Yes | Yes |

**All 6 required sections are present.**

### Layer Coverage

| Layer | Section | Component Count | Defined |
|---|---|---|---|
| Layer 1 (Input Parsing) | Meta Schema Definition | 6 (FileEntry, FileInventory, ImportEdge, ImportGraph, SourceSymbol, AudienceDefinition) | Yes |
| Layer 2 (Transformation) | Meta Schema Definition | 5 (AnalysisDimension, SecurityPhase, SeverityRating, Evidence, Finding) | Yes |
| Layer 3 (Output Rendering) | Meta Schema Definition | 3 (OutputDocument, OutputSection, RunManifest) | Yes |

**All 3 layers are defined with clear component assignments.**

### Transformation Pipeline Coverage

| Stage | Input Components | Output Components | Invariants | Defined |
|---|---|---|---|---|
| TS-001 | Raw filesystem | FileInventory | INV-001 to INV-003 | Yes |
| TS-002 | FileInventory | ImportGraph, SourceSymbol | INV-004 to INV-006 | Yes |
| TS-003 | FileInventory, SourceSymbol, AudienceDefinition | OutputDocument | INV-007 to INV-009 | Yes |
| TS-004 | ImportGraph, SourceSymbol, AnalysisDimension | Finding (health) | INV-010 to INV-013 | Yes |
| TS-005 | FileInventory, SourceSymbol, SecurityPhase | Finding (security) | INV-014 to INV-018 | Yes |
| TS-006 | Finding (all) | OutputDocument (health, security) | INV-019 to INV-021 | Yes |
| TS-007 | All OutputDocuments | RunManifest | INV-022 to INV-024 | Yes |

**All 7 stages are defined with inputs, outputs, and invariants.**

### Extension Point Coverage

| Extension | Type | Procedure Defined | Contract Defined | Backward Compatible |
|---|---|---|---|---|
| EXT-001 | Custom audiences | Yes | Yes (AudienceDefinition schema) | Yes |
| EXT-002 | Custom health dimensions | Yes | Yes (Finding schema) | Yes |
| EXT-003 | Custom security phases | Yes | Yes (Finding schema) | Yes |
| EXT-004 | Configurable thresholds | Yes | Yes (invariant preservation) | Yes |
| EXT-005 | Multiple output formats | Yes | Yes (OutputRenderer protocol) | Yes |
| EXT-006 | Incremental analysis | Yes | Yes (invariant preservation) | Yes |

**All 6 extension points are defined with procedures, contracts, and backward compatibility.**

### Input-to-Output Traceability

| Requirement ID | Input Component | Transformation Stage | Output Component | Output Mapping |
|---|---|---|---|---|
| IN-001 (Source Codebase) | Raw files | TS-001, TS-002 | FileInventory, ImportGraph | -- |
| OUT-001 (Audience Content) | FileInventory, AudienceDefinition | TS-003 | OutputDocument | OM-001 |
| OUT-002 (Health Analysis) | ImportGraph, AnalysisDimension | TS-004, TS-006 | OutputDocument | OM-002 |
| OUT-003 (Security Audit) | FileInventory, SecurityPhase | TS-005, TS-006 | OutputDocument | OM-003 |
| TR-001 (Codebase Scan) | Raw files | TS-001 | FileInventory | IM-001, IM-002 |
| TR-002 (Import Graph) | Python source | TS-002 | ImportGraph, SourceSymbol | IM-003, IM-004, IM-005 |
| TR-003 (Audience Analysis) | AudienceDefinition | TS-003 | OutputDocument | OM-001 |
| TR-004 (Health Dimensions) | ImportGraph | TS-004 | Finding | OM-002 |
| TR-005 (Security Phases) | FileInventory | TS-005 | Finding | OM-003 |
| TR-006 (Findings Reports) | Finding | TS-006 | OutputDocument | OM-002, OM-003 |
| TR-007 (Output Validation) | OutputDocument | TS-007 | RunManifest | OM-004 |

**All requirements trace from input through transformation to output.**

### Constraint Coverage

| Constraint ID | Description | Enforced By |
|---|---|---|
| C-FMT-001 | Input docs are Rich Markdown | IM-001 (file_type classification) |
| C-FMT-002 | Input source is Python | IM-001 (file_type classification) |
| C-FMT-003 | Input encoding is UTF-8 | IM-001 (FileEntry.encoding) |
| C-FMT-004 | AST-based import analysis | INV-006, IM-003 |
| C-FMT-005 | Severity consistency | INV-011, INV-015, SeverityRating |
| C-FMT-006 | Self-contained reports | INV-023, OM-VAL-001 |
| C-FMT-007 | Evidence-backed findings | INV-010, INV-014, Evidence |
| C-CMP-001 | No hallucination | INV-008, OM-VAL-009 |
| C-CMP-002 | Secret redaction | INV-017, OM-VAL-006 |
| C-CMP-003 | Audience fidelity | INV-009, OM-VAL-002, OM-VAL-003 |
| C-CMP-004 | Dimension independence | INV-012, INV-016 |
| C-CMP-005 | Plugin extensibility | EXT-001, IM-006 |
| C-CMP-006 | Configurable scope | EXT-002, EXT-003, AnalysisDimension.enabled |

**All 13 constraints from the requirement analysis are covered.**

### Verification Checklist

- [x] 14 meta components defined across 3 layers.
- [x] meta_component_count (14) matches actual component definitions.
- [x] All 3 layers (Input Parsing, Transformation, Output Rendering) are defined.
- [x] All 7 transformation stages are defined with inputs, outputs, and invariants.
- [x] 24 invariants cover all constraint requirements.
- [x] All 6 extension points have procedures, contracts, and backward compatibility.
- [x] Output-type-agnostic design: OutputDocument is a generic interface, not a specific type.
- [x] Protocol interfaces defined for InputParser, AnalysisEngine, OutputRenderer.
- [x] Input mapping covers all input requirements (IM-001 through IM-006).
- [x] Output mapping covers all output requirements (OM-001 through OM-004).
- [x] All requirements (IN-001, OUT-001 to OUT-003, TR-001 to TR-007) trace through the pipeline.
- [x] All 13 constraints (C-FMT-001 to C-FMT-007, C-CMP-001 to C-CMP-006) are enforced.
- [x] Follows BASE_COMPOSITION_STANDARD Pattern 2 (Input Transformation).
- [x] Follows BASE_COMPOSITION_STANDARD Section 13 (output-type-agnostic design).
- [x] No scope invention: all content traces to requirement analysis or requirement document.
- [x] ASCII-only content. No em-dashes, curly quotes, or Unicode characters.
- [x] Governance path references use filenames only (BASE_COMPOSITION_STANDARD_v1.0.md), not filesystem paths.
- [x] YAML frontmatter includes required fields: doc_type, identity_locked.

---

**End of Composition Specification**
