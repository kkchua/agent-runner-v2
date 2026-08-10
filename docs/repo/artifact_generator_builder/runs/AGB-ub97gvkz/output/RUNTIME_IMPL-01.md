---
doc_type: "runtime_impl"
identity_locked: true
generator_name: "codebase_intelligence"
codename: "codebase_intelligence"
impl_version: "1.0.0"
composition_spec_ref: "COMPOSITION_SPEC-01.md"
requirement_analysis_ref: "REQUIREMENT_ANALYSIS-01.md"
base_standard_ref: "BASE_COMPOSITION_STANDARD_v1.0.md"
pattern: "input_transformation"
stage_count: 7
meta_component_count: 14
extension_point_count: 6
---

# Runtime Implementation Design Notes: codebase_intelligence

## Implementation Architecture

### High-Level Structure

The runtime follows Pattern 2 (Input Transformation) from BASE_COMPOSITION_STANDARD_v1.0.md. It consists of three module groups that mirror the three layers defined in the composition spec:

| Module Group | Layer | Responsibility |
|---|---|---|
| input_parsers | Layer 1 | Parse codebase files into meta components |
| analysis_engines | Layer 2 | Transform meta components into findings |
| output_renderers | Layer 3 | Serialize output documents to files |

### Component Modules

The implementation is organized into 6 module categories:

1. **core/** -- Pipeline orchestrator, configuration loader, invariant checker
2. **parsers/** -- InputParser protocol implementations (FileParser, ASTParser, AudienceParser)
3. **analyzers/** -- AnalysisEngine protocol implementations (5 health dimensions + 5 security phases)
4. **renderers/** -- OutputRenderer protocol implementations (MarkdownRenderer, JSONRenderer)
5. **models/** -- Data structures for all 14 meta components
6. **extensions/** -- Registry and plugin loading for extension points

### Data Flow

```
Raw Filesystem
    |
    v
[TS-001: Codebase Scan] --> FileInventory (Component 2)
    |
    v
[TS-002: Import Graph Construction] --> ImportGraph (Component 4) + SourceSymbol[] (Component 5)
    |
    +--->[TS-003: Audience Analysis] --> OutputDocument[] (Component 12) per audience
    |
    +--->[TS-004: Health Dimension Analysis] --> Finding[] (Component 11) health
    |
    +--->[TS-005: Security Phase Analysis] --> Finding[] (Component 11) security
    |
    v
[TS-006: Findings Report Assembly] --> OutputDocument[] (health report + security report)
    |
    v
[TS-007: Output Validation] --> RunManifest (Component 14)
    |
    v
[Output Rendering] --> Concrete files (Markdown/JSON/HTML)
```

### Execution Model

- Stages TS-001 and TS-002 are sequential (TS-002 depends on TS-001 output).
- Stages TS-003, TS-004, and TS-005 can execute in parallel after TS-002 completes.
- Stage TS-006 depends on completion of both TS-004 and TS-005.
- Stage TS-007 depends on completion of TS-003 and TS-006.
- The pipeline orchestrator manages this dependency DAG.

---

## Input Loading

### Loader Pipeline

The input loading phase corresponds to transformation stages TS-001 and TS-002.

**Step 1: File Discovery (TS-001)**

```
Input: repository_root (str path)
Output: FileInventory
Algorithm:
  1. Walk directory tree from repository_root
  2. For each file:
     a. Determine file_type by extension mapping:
        .md -> documentation
        .py -> source_code
        .toml, .json, .yaml, .yml, .cfg, .ini -> configuration
        * -> other
     b. Record file_path (relative), encoding (UTF-8), size_bytes
     c. Attempt type-specific parse validation:
        - .md: verify non-empty content with at least one heading
        - .py: attempt AST parse, record SyntaxError in parse_errors
        - config: verify valid TOML/JSON/YAML syntax
     d. Create FileEntry component
  3. Aggregate all FileEntry components into FileInventory
  4. Compute counts: doc_count, source_count, config_count, other_count
  5. Detect has_python_package: any directory containing __init__.py
  6. Detect has_doc_directory: any directory containing .md files
  7. Check invariants INV-001, INV-002, INV-003
```

**Step 2: AST Parsing (TS-002)**

```
Input: FileInventory (source_code entries only)
Output: ImportGraph + list[SourceSymbol]
Algorithm:
  1. For each FileEntry where file_type == source_code:
     a. Compute module name from file_path relative to package root
     b. Parse file content using Python ast.parse()
     c. Walk AST tree for Import and ImportFrom nodes:
        - Import: target = each imported module name
        - ImportFrom: target = module field + name field
        - Resolve relative imports using package structure:
          if level > 0: resolve to absolute using __init__.py chain
     d. Create ImportEdge for each import found
     e. Walk AST tree for top-level definitions:
        - FunctionDef/AsyncFunctionDef -> SourceSymbol(symbol_type=function)
        - ClassDef -> SourceSymbol(symbol_type=class)
        - Module-level assignments -> SourceSymbol(symbol_type=constant)
     f. Set is_exported = not symbol_name.startswith("_")
  2. Build ImportGraph from all ImportEdge components:
     nodes = set(source_module for edge in edges) | set(target_module for edge in edges)
     node_count = len(nodes)
     edge_count = len(edges)
  3. Check invariants INV-004, INV-005, INV-006
```

**Validation Summary:**
- IM-VAL-001 through IM-VAL-008 are checked during loading
- Failures are recorded as parse_errors on FileEntry
- Critical failures (no Python package, no doc directory) halt the pipeline with a clear error

---

## Transformation Engine

### Stage Implementation

Each stage is implemented as a self-contained analyzer class that satisfies the AnalysisEngine protocol. Stages are registered in a stage registry and dispatched by the pipeline orchestrator.

#### TS-003: Audience Analysis

```
Input: FileInventory, list[SourceSymbol], list[AudienceDefinition]
Output: list[OutputDocument] (one per audience)
Algorithm:
  For each AudienceDefinition:
    1. Filter FileInventory entries by audience's focus_areas:
       - Match file_path patterns against focus_areas keywords
       - Include documentation files whose path or heading matches a focus area
    2. Build OutputSection components following audience.section_structure order
    3. For each section:
       - Generate content from filtered codebase docs
       - Apply audience.tone to all text (technical, executive, operational)
       - Exclude topics listed in audience.exclude
    4. Create OutputDocument with:
       - output_type = "audience_report"
       - sections = ordered OutputSection list
       - is_self_contained = true
       - metadata = {audience_id, generation_date, source_version}
  Check invariants INV-007, INV-008, INV-009
```

#### TS-004: Health Dimension Analysis

```
Input: ImportGraph, list[SourceSymbol], FileInventory, list[AnalysisDimension]
Output: list[Finding] (health findings)
Algorithm:
  For each enabled AnalysisDimension:
    Switch on dimension_id:
      DIM-CIRCULAR:
        - Run Tarjan's SCC algorithm on ImportGraph
        - For each SCC with size > 1: create Finding with severity high/critical
        - Evidence: cycle path (file paths, import statements)
      DIM-COUPLING:
        - Compute fan-in (number of importers) and fan-out (number of imports) per module
        - For modules exceeding threshold (default: fan-in > 10 or fan-out > 15): create Finding
        - Evidence: module name, fan-in count, fan-out count, import list
      DIM-DEADCODE:
        - For each SourceSymbol where is_exported == false:
          - Check if symbol is referenced in any ImportEdge or used in any other file
          - If unreferenced: create Finding with severity low/medium
        - Evidence: symbol name, file path, line number
      DIM-COMPLEXITY:
        - For each SourceSymbol where symbol_type == function:
          - Compute cyclomatic complexity (count decision points in AST)
          - If complexity > threshold (default: 10): create Finding
        - Evidence: function name, file path, complexity score, decision points
      DIM-IMPORT:
        - Scan all ImportEdge for anti-patterns:
          - Wildcard imports (from X import *)
          - Relative imports crossing package boundaries
          - Import of private modules (names starting with _)
        - For each violation: create Finding
        - Evidence: import statement, file path, line number
    Each Finding includes:
      - finding_id = "{dimension_id}-{NNN}"
      - severity = SeverityRating per finding
      - evidence = list[Evidence]
      - impact = description of risk
      - remediation = recommended fix
      - is_self_contained = true
  Check invariants INV-010 through INV-013
```

#### TS-005: Security Phase Analysis

```
Input: FileInventory, list[SourceSymbol], list[SecurityPhase]
Output: list[Finding] (security findings)
Algorithm:
  For each enabled SecurityPhase:
    Switch on phase_id:
      PHASE-SECRETS:
        - Pattern scan all source files for:
          - API keys (regex: patterns matching known key formats)
          - Passwords (regex: password/secret/token assignments with literal values)
          - Private keys (regex: PEM header patterns)
          - Database connection strings with embedded credentials
        - For each match: create Finding with severity critical/high
        - REDACT actual secret values from evidence.code_snippet
      PHASE-DEPS:
        - Parse dependency files (pyproject.toml, requirements.txt, setup.py)
        - Extract package name + version pairs
        - Compare against known vulnerability patterns (configurable database)
        - For each vulnerable dependency: create Finding
        - Evidence: package name, version, vulnerability reference
      PHASE-CODEPAT:
        - Scan source files for insecure patterns:
          - eval() / exec() calls with dynamic input
          - os.system() / subprocess.call() with shell=True
          - Unsanitized user input in SQL queries
          - Hardcoded IP addresses or URLs in production code
        - For each match: create Finding
        - Evidence: pattern match, file path, line number
      PHASE-AUTH:
        - Scan for authentication implementation issues:
          - Missing authentication decorators on endpoints
          - Hardcoded credentials in auth modules
          - Missing CSRF protection patterns
          - Weak hash algorithms (MD5, SHA1 for passwords)
        - For each issue: create Finding
        - Evidence: code context, file path, line number
      PHASE-INFRA:
        - Scan configuration files for:
          - Debug mode enabled in production configs
          - Default credentials in config files
          - Missing security headers in web configs
          - Overly permissive CORS settings
        - For each issue: create Finding
        - Evidence: config file path, setting name, current value
    Each Finding includes:
      - finding_id = "{phase_id}-{NNN}"
      - severity = SeverityRating
      - evidence = list[Evidence] (with secret redaction applied)
      - impact, remediation, is_self_contained = true
  Check invariants INV-014 through INV-018
```

#### TS-006: Findings Report Assembly

```
Input: list[Finding] from TS-004 and TS-005
Output: list[OutputDocument] (health report + security report)
Algorithm:
  1. Health Report:
     - Group health findings by source_id (dimension_id)
     - Create OutputDocument with output_type = "health_report"
     - For each enabled dimension with findings:
       - Create OutputSection with section_name = dimension_name
       - Sort findings by severity (critical first, numeric_weight descending)
       - Add findings to section
     - Set is_self_contained = true
  2. Security Report:
     - Group security findings by source_id (phase_id)
     - Create OutputDocument with output_type = "security_report"
     - For each enabled phase with findings:
       - Create OutputSection with section_name = phase_name
       - Sort findings by severity (critical first)
       - Verify all code_snippets have secrets redacted
       - Add findings to section
     - Set is_self_contained = true
  Check invariants INV-019 through INV-021
```

#### TS-007: Output Validation

```
Input: All OutputDocument components
Output: RunManifest
Algorithm:
  1. Collect all OutputDocument components from TS-003 and TS-006
  2. Extract distinct output_type values
  3. Verify output_type_count >= 3 (INV-022)
  4. For each document:
     - Verify is_self_contained == true (INV-023)
     - Verify all findings cite at least one Evidence
     - Verify severity scale consistency
     - Verify no unresolved file references (INV-024)
  5. Build RunManifest:
     - run_id = unique identifier
     - codename = "codebase_intelligence"
     - output_count = len(documents)
     - output_types = sorted list of distinct types
     - documents = all OutputDocument components
     - generation_date = today's date
     - output_type_count = len(output_types)
  6. Return RunManifest
```

### Error Handling Strategy

| Error Type | Handling |
|---|---|
| File read failure | Record in FileEntry.parse_errors, continue scan |
| AST parse failure | Record in FileEntry.parse_errors, skip that file |
| Missing audience directory | Log warning, skip audience analysis (TS-003 produces no output) |
| Invalid audience definition | Skip that audience, continue with valid ones |
| Empty findings for a dimension/phase | Produce section with "No findings" note |
| Invariant violation | Halt pipeline, report which invariant failed |
| Secret redaction failure | Halt with critical error (safety constraint) |

---

## Output Generation

### Rendering Pipeline

After TS-007 produces the RunManifest, the rendering pipeline serializes each OutputDocument to disk.

**Markdown Rendering (Default):**

```
For each OutputDocument:
  1. Build YAML frontmatter:
     - document_id, output_type, title, generation_date, metadata
  2. Render each OutputSection:
     - Section heading: ## section_name
     - Content: free-form text
     - Findings: render each as structured block:
       ### finding_id: title
       - Severity: level
       - Description: description
       - Evidence:
         - file_path:line_number
         - code_snippet (in code block)
       - Impact: impact text
       - Remediation: remediation text
     - Subsections: recurse
  3. Write to file: {output_dir}/{output_type}_{document_id}.md
```

**RunManifest Rendering:**

```
  1. Build YAML frontmatter with run-level metadata
  2. Render summary table of all documents
  3. Write to file: {output_dir}/RUN_MANIFEST.md
```

### Output File Naming Convention

| Output Type | File Pattern |
|---|---|
| audience_report | audience_{audience_id}.md |
| health_report | health_report.md |
| security_report | security_report.md |
| Run manifest | RUN_MANIFEST.md |

---

## Configuration

### Runtime Parameters

Configuration is loaded from a JSON file (config.json) with these defaults:

```json
{
  "repository_root": ".",
  "output_dir": "./output",
  "audiences_dir": "./audiences",
  "dimensions": {
    "DIM-CIRCULAR": {"enabled": true, "config": {}},
    "DIM-COUPLING": {"enabled": true, "config": {"fan_in_threshold": 10, "fan_out_threshold": 15}},
    "DIM-DEADCODE": {"enabled": true, "config": {}},
    "DIM-COMPLEXITY": {"enabled": true, "config": {"cyclomatic_threshold": 10}},
    "DIM-IMPORT": {"enabled": true, "config": {}}
  },
  "phases": {
    "PHASE-SECRETS": {"enabled": true, "config": {}},
    "PHASE-DEPS": {"enabled": true, "config": {"vulnerability_db_path": null}},
    "PHASE-CODEPAT": {"enabled": true, "config": {}},
    "PHASE-AUTH": {"enabled": true, "config": {}},
    "PHASE-INFRA": {"enabled": true, "config": {}}
  },
  "rendering": {
    "format": "markdown",
    "redact_secrets": true
  }
}
```

### Override Precedence

1. Command-line arguments (highest)
2. Environment variables
3. Config file values
4. Built-in defaults (lowest)

---

## Extension Interface

### Protocol Interfaces

Three protocol interfaces define the extension contracts (per composition spec):

**InputParser Protocol:**

| Method | Signature | Purpose |
|---|---|---|
| parse_file | (file_path: str) -> FileEntry | Parse a single file into a meta component |
| parse_imports | (file_path: str) -> list[ImportEdge] | Extract imports via AST |
| parse_symbols | (file_path: str) -> list[SourceSymbol] | Extract symbols via AST |
| parse_audience | (file_path: str) -> AudienceDefinition | Parse audience definition file |

**AnalysisEngine Protocol:**

| Method | Signature | Purpose |
|---|---|---|
| run_dimension | (dimension, graph, symbols) -> list[Finding] | Run a health dimension analysis |
| run_phase | (phase, inventory, symbols) -> list[Finding] | Run a security phase analysis |

**OutputRenderer Protocol:**

| Method | Signature | Purpose |
|---|---|---|
| render_document | (document: OutputDocument) -> str | Render document to string |
| render_manifest | (manifest: RunManifest) -> str | Render manifest to string |
| supported_formats | () -> list[str] | List supported output formats |

### Extension Registration

Extensions are registered via a registry pattern (following CODER_IMPLEMENTATION_SOP):

```
DIMENSION_REGISTRY[dimension_id] = DimensionAnalyzerClass
PHASE_REGISTRY[phase_id] = PhaseAnalyzerClass
RENDERER_REGISTRY[format_name] = RendererClass
```

### Extension Point Implementations

| Extension | How to Add | Registry Key |
|---|---|---|
| EXT-001 Custom audiences | Drop .md file in audiences/ dir | Auto-discovered by InputParser.parse_audience |
| EXT-002 Custom dimensions | Implement AnalysisEngine.run_dimension, register in DIMENSION_REGISTRY | dimension_id string |
| EXT-003 Custom phases | Implement AnalysisEngine.run_phase, register in PHASE_REGISTRY | phase_id string |
| EXT-004 Configurable thresholds | Extend dimension/phase config object | Read from config at runtime |
| EXT-005 Output formats | Implement OutputRenderer, register in RENDERER_REGISTRY | format name string |
| EXT-006 Incremental analysis | Extend FileParser with change detection | Override parse_file with cache layer |

---

## Data Structures

### In-Memory Representation

All meta components are represented as dataclass instances (following CODER_IMPLEMENTATION_SOP pattern):

- FileEntry, FileInventory, ImportEdge, ImportGraph, SourceSymbol, AudienceDefinition
- AnalysisDimension, SecurityPhase, SeverityRating, Evidence, Finding
- OutputDocument, OutputSection, RunManifest

### Severity Rating Enum

```
SeverityRating:
  CRITICAL = (level="critical", numeric_weight=5)
  HIGH = (level="high", numeric_weight=4)
  MEDIUM = (level="medium", numeric_weight=3)
  LOW = (level="low", numeric_weight=2)
  INFO = (level="info", numeric_weight=1)
```

---

## Design Notes

### Key Design Decisions

1. **Registry dispatch over if/elif chains** -- Following CODER_IMPLEMENTATION_SOP, dimension and phase analysis use registry lookup, not conditional chains.

2. **Dataclass configs over parameter lists** -- Dimension and phase configurations use dataclass objects with defaults, not long parameter lists.

3. **Exception-based errors over None returns** -- Pipeline stages raise specific exceptions (ParseError, InvariantViolation, SecretRedactionError) instead of returning None.

4. **Parallel-capable stage execution** -- TS-003, TS-004, TS-005 are designed to be independent and can execute concurrently if the runtime supports it.

5. **Output-type-agnostic rendering** -- The OutputRenderer protocol accepts any OutputDocument regardless of output_type. Different renderers can be swapped without changing the pipeline.

### Traceability to Composition Spec

| Design Element | Spec Reference |
|---|---|
| 7-stage pipeline | TS-001 through TS-007 |
| 14 meta components | Components 1-14 |
| 24 invariants | INV-001 through INV-024 |
| 3 Protocol interfaces | InputParser, AnalysisEngine, OutputRenderer |
| 6 extension points | EXT-001 through EXT-006 |
| Output-type-agnostic | Section 13 of BASE_COMPOSITION_STANDARD |
| Registry dispatch | CODER_IMPLEMENTATION_SOP pattern compliance |

### Explicit Assumptions

1. Python 3.12+ is the minimum runtime (for ast.parse features).
2. The codebase fits in memory (no streaming/chunking for very large repos).
3. File encoding is always UTF-8 (per C-FMT-003).
4. The vulnerability database for PHASE-DEPS is optional; if not provided, the phase reports "database not configured" as an info-level finding.
5. Audience definition files use YAML frontmatter in Markdown format.

---

**End of Runtime Implementation Design Notes**
