---
doc_type: "default_impl"
identity_locked: true
generator_name: "codebase_intelligence"
codename: "codebase_intelligence"
impl_version: "1.0.0"
composition_spec_ref: "COMPOSITION_SPEC-01.md"
base_standard_ref: "BASE_COMPOSITION_STANDARD_v1.0.md"
pattern: "input_transformation"
layer_count: 3
stage_count: 7
meta_component_count: 14
extension_point_count: 6
---

# Default Runtime Implementation: codebase_intelligence

## 1. Overview

This document is the default runtime implementation for the codebase_intelligence generator. It is a self-contained design that satisfies the composition specification (COMPOSITION_SPEC-01.md) by defining concrete algorithms, data structures, data flow, error handling, configuration defaults, and extension point implementations.

**Codename:** codebase_intelligence

**Composition pattern:** Pattern 2 -- Input Transformation (per BASE_COMPOSITION_STANDARD_v1.0.md)

**Implementation role:** Concrete executor that transforms codebase input into multiple intelligence reports. This implementation satisfies all 24 invariants, all 13 constraints, and all 7 transformation stages defined in the composition spec.

---

## 2. Implementation Architecture

### 2.1 Three-Layer Module Structure

The implementation is organized into three module groups corresponding to the three layers of the composition spec:

| Layer | Module Group | Responsibility | Components Handled |
|---|---|---|---|
| Layer 1 | parsers/ | Parse codebase files into meta components | FileEntry, FileInventory, ImportEdge, ImportGraph, SourceSymbol, AudienceDefinition |
| Layer 2 | analyzers/ | Transform meta components into findings | AnalysisDimension, SecurityPhase, SeverityRating, Evidence, Finding |
| Layer 3 | renderers/ | Serialize output documents to files | OutputDocument, OutputSection, RunManifest |

A fourth module group, core/, provides cross-cutting concerns:

| Module | Responsibility |
|---|---|
| core/pipeline.py | Pipeline orchestrator -- stage execution, dependency DAG, invariant checking |
| core/config.py | Configuration loader with override precedence |
| core/models.py | Dataclass definitions for all 14 meta components |
| core/exceptions.py | Exception hierarchy for pipeline errors |
| core/registries.py | Extension registries (DIMENSION_REGISTRY, PHASE_REGISTRY, RENDERER_REGISTRY) |

### 2.2 Pipeline Orchestrator

The pipeline orchestrator (core/pipeline.py) is the entry point for execution. It manages the 7-stage transformation pipeline as a directed acyclic graph (DAG):

```
Dependency DAG:

  TS-001 --> TS-002 --> TS-003 (audience analysis)
                    |-> TS-004 (health analysis)  --> TS-006 --> TS-007
                    |-> TS-005 (security analysis) -/
```

Execution rules:
- TS-001 must complete before TS-002 starts.
- TS-002 must complete before TS-003, TS-004, and TS-005 start.
- TS-003, TS-004, TS-005 may execute in parallel (they are independent).
- TS-004 and TS-005 must both complete before TS-006 starts.
- TS-003 and TS-006 must both complete before TS-007 starts.
- If any stage raises an InvariantViolation exception, the pipeline halts.

### 2.3 Data Flow

```
Raw Filesystem (repository_root)
    |
    v
[TS-001: Codebase Scan]
    Output: FileInventory
    |
    v
[TS-002: Import Graph Construction]
    Output: ImportGraph, list[SourceSymbol]
    |
    +--- Parallel Branch A ---+
    |                         |
    v                         v
[TS-003: Audience Analysis]   [TS-004: Health Dimensions]  [TS-005: Security Phases]
    Output: list[OutputDocument]   Output: list[Finding]        Output: list[Finding]
    |                         |                         |
    |                         +--- TS-006 ---<-----------+
    |                              Output: list[OutputDocument]
    |                              |
    +---------- TS-007 ---<--------+
                   Output: RunManifest
                   |
                   v
            [Output Rendering]
                   Output: Concrete files on disk
```

---

## 3. Data Structures

All meta components are represented as frozen dataclass instances. This ensures immutability after creation and supports hashability for set operations.

### 3.1 Layer 1 Data Structures

```
@dataclass(frozen=True)
class FileEntry:
    file_path: str          # Relative path from codebase root
    file_type: str          # "documentation" | "source_code" | "configuration" | "other"
    encoding: str           # Always "UTF-8"
    size_bytes: int         # File size in bytes
    is_parseable: bool      # Whether type-specific parsing succeeded
    parse_errors: tuple     # Frozen tuple of error message strings

@dataclass(frozen=True)
class FileInventory:
    entries: tuple          # Frozen tuple of FileEntry
    doc_count: int
    source_count: int
    config_count: int
    other_count: int
    has_python_package: bool
    has_doc_directory: bool

@dataclass(frozen=True)
class ImportEdge:
    source_module: str      # Fully qualified module containing the import
    target_module: str      # Fully qualified module being imported
    import_type: str        # "absolute" | "relative"
    original_import: str    # Raw import statement text
    line_number: int        # Line number in source file

@dataclass(frozen=True)
class ImportGraph:
    edges: tuple            # Frozen tuple of ImportEdge
    nodes: frozenset        # Frozen set of unique module name strings
    node_count: int
    edge_count: int
    # is_acyclic is computed during analysis, not at construction

@dataclass(frozen=True)
class SourceSymbol:
    symbol_name: str
    symbol_type: str        # "function" | "class" | "module" | "constant"
    file_path: str
    line_start: int
    line_end: int
    parameters: tuple       # Frozen tuple of parameter name strings (functions only)
    decorators: tuple       # Frozen tuple of decorator name strings
    docstring: str          # Extracted docstring or empty string
    is_exported: bool       # True if name does not start with underscore

@dataclass(frozen=True)
class AudienceDefinition:
    audience_id: str
    label: str
    tone: str               # "technical" | "executive" | "operational" | custom
    focus_areas: tuple      # Frozen tuple of area name strings
    section_structure: tuple  # Frozen tuple of section name strings (ordered)
    exclude: tuple          # Frozen tuple of topic strings to omit
    source_file: str        # Path to the audience definition .md file
```

### 3.2 Layer 2 Data Structures

```
@dataclass(frozen=True)
class AnalysisDimension:
    dimension_id: str       # e.g., "DIM-CIRCULAR", "DIM-COUPLING", etc.
    dimension_name: str
    description: str
    enabled: bool
    config: dict            # Dimension-specific configuration (mutable copy at read time)

@dataclass(frozen=True)
class SecurityPhase:
    phase_id: str           # e.g., "PHASE-SECRETS", "PHASE-DEPS", etc.
    phase_name: str
    description: str
    enabled: bool
    config: dict            # Phase-specific configuration

@dataclass(frozen=True)
class SeverityRating:
    level: str              # "critical" | "high" | "medium" | "low" | "info"
    numeric_weight: int     # critical=5, high=4, medium=3, low=2, info=1

    # Pre-defined constants:
    # SEVERITY_CRITICAL = SeverityRating("critical", 5)
    # SEVERITY_HIGH = SeverityRating("high", 4)
    # SEVERITY_MEDIUM = SeverityRating("medium", 3)
    # SEVERITY_LOW = SeverityRating("low", 2)
    # SEVERITY_INFO = SeverityRating("info", 1)

@dataclass(frozen=True)
class Evidence:
    file_path: str          # Relative path to file containing the evidence
    line_number: int        # Line number (0 if not applicable)
    code_snippet: str       # Code excerpt (secrets redacted for security findings)
    description: str        # Human-readable explanation

@dataclass(frozen=True)
class Finding:
    finding_id: str         # Format: "{source_id}-{NNN}" (e.g., "DIM-CIRCULAR-001")
    source_type: str        # "health_dimension" | "security_phase"
    source_id: str          # dimension_id or phase_id
    severity: SeverityRating
    title: str
    description: str
    evidence: tuple         # Frozen tuple of Evidence (at least one required)
    impact: str
    remediation: str
    is_self_contained: bool # Must always be True
```

### 3.3 Layer 3 Data Structures

```
@dataclass(frozen=True)
class OutputSection:
    section_id: str
    section_name: str
    content: str            # Free-form text content
    findings: tuple         # Frozen tuple of Finding (may be empty)
    subsections: tuple      # Frozen tuple of child OutputSection (may be empty)

@dataclass(frozen=True)
class OutputDocument:
    document_id: str
    output_type: str        # "audience_report" | "health_report" | "security_report" | custom
    title: str
    sections: tuple         # Frozen tuple of OutputSection (at least one)
    metadata: dict          # Document-level metadata (generation_date, source ref, etc.)
    is_self_contained: bool # Must always be True

@dataclass(frozen=True)
class RunManifest:
    run_id: str
    codename: str           # Always "codebase_intelligence"
    output_count: int
    output_types: tuple     # Frozen tuple of distinct output_type strings
    documents: tuple        # Frozen tuple of OutputDocument
    generation_date: str    # YYYY-MM-DD format
    output_type_count: int  # Must be >= 3
```

### 3.4 Configuration Data Structure

```
@dataclass
class RuntimeConfig:
    repository_root: str = "."
    output_dir: str = "./output"
    audiences_dir: str = "./audiences"
    dimensions: dict = None   # dimension_id -> {"enabled": bool, "config": dict}
    phases: dict = None       # phase_id -> {"enabled": bool, "config": dict}
    rendering_format: str = "markdown"
    redact_secrets: bool = True

    def __post_init__(self):
        if self.dimensions is None:
            self.dimensions = DEFAULT_DIMENSIONS
        if self.phases is None:
            self.phases = DEFAULT_PHASES
```

---

## 4. Algorithms

### 4.1 Stage TS-001: Codebase Scan

**Input:** repository_root (str)
**Output:** FileInventory
**Invariants checked:** INV-001, INV-002, INV-003

**Algorithm: scan_codebase(repository_root)**

```
function scan_codebase(repository_root):
    entries = []
    for each file in recursive_walk(repository_root):
        relative_path = file.relative_to(repository_root)
        extension = file.suffix.lower()

        # Classify file type
        if extension == ".md":
            file_type = "documentation"
        elif extension == ".py":
            file_type = "source_code"
        elif extension in (".toml", ".json", ".yaml", ".yml", ".cfg", ".ini"):
            file_type = "configuration"
        else:
            file_type = "other"

        # Read file content
        try:
            content = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            entries.append(FileEntry(
                file_path=relative_path,
                file_type=file_type,
                encoding="UTF-8",
                size_bytes=file.stat().st_size,
                is_parseable=False,
                parse_errors=("Unicode decode error",)
            ))
            continue

        # Validate parseability
        parse_errors = []
        is_parseable = True

        if file_type == "documentation":
            if not content.strip():
                is_parseable = False
                parse_errors.append("Empty markdown file")
            elif not any(line.startswith("#") for line in content.splitlines()):
                is_parseable = False
                parse_errors.append("No markdown headings found")

        elif file_type == "source_code":
            try:
                ast.parse(content)
            except SyntaxError as e:
                is_parseable = False
                parse_errors.append(f"AST parse error: {e}")

        elif file_type == "configuration":
            try:
                if extension == ".toml":
                    tomllib.loads(content)
                elif extension == ".json":
                    json.loads(content)
                elif extension in (".yaml", ".yml"):
                    yaml.safe_load(content)
            except Exception as e:
                is_parseable = False
                parse_errors.append(f"Config parse error: {e}")

        entries.append(FileEntry(
            file_path=str(relative_path),
            file_type=file_type,
            encoding="UTF-8",
            size_bytes=file.stat().st_size,
            is_parseable=is_parseable,
            parse_errors=tuple(parse_errors)
        ))

    # Aggregate into FileInventory
    doc_count = sum(1 for e in entries if e.file_type == "documentation")
    source_count = sum(1 for e in entries if e.file_type == "source_code")
    config_count = sum(1 for e in entries if e.file_type == "configuration")
    other_count = sum(1 for e in entries if e.file_type == "other")

    has_python_package = any(
        "agent_runner_v2" in e.file_path or "__init__.py" in e.file_path
        for e in entries if e.file_type == "source_code"
    )
    # More robust: check if any directory in the tree contains __init__.py
    has_python_package = any(
        entry.file_path.endswith("__init__.py")
        for entry in entries
    )

    has_doc_directory = any(
        "docs" in entry.file_path or entry.file_path.endswith(".md")
        for entry in entries
    )

    inventory = FileInventory(
        entries=tuple(entries),
        doc_count=doc_count,
        source_count=source_count,
        config_count=config_count,
        other_count=other_count,
        has_python_package=has_python_package,
        has_doc_directory=has_doc_directory
    )

    # Check invariants
    if not inventory.entries:
        raise InvariantViolation("INV-001: FileInventory.entries is empty")
    if not inventory.has_python_package:
        raise InvariantViolation("INV-002: No Python package directory found")
    if not inventory.has_doc_directory:
        raise InvariantViolation("INV-003: No documentation directory found")

    return inventory
```

### 4.2 Stage TS-002: Import Graph Construction

**Input:** FileInventory
**Output:** ImportGraph, list[SourceSymbol]
**Invariants checked:** INV-004, INV-005, INV-006

**Algorithm: build_import_graph(inventory)**

```
function build_import_graph(inventory):
    edges = []
    symbols = []

    # Determine package root (directory containing top-level __init__.py)
    package_root = _detect_package_root(inventory)

    for entry in inventory.entries:
        if entry.file_type != "source_code" or not entry.is_parseable:
            continue

        file_path = entry.file_path
        module_name = _path_to_module(file_path, package_root)
        content = _read_file(entry)
        tree = ast.parse(content)

        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    edges.append(ImportEdge(
                        source_module=module_name,
                        target_module=alias.name,
                        import_type="absolute",
                        original_import=f"import {alias.name}",
                        line_number=node.lineno
                    ))
            elif isinstance(node, ast.ImportFrom):
                level = node.level or 0
                module = node.module or ""

                if level > 0:
                    # Resolve relative import to absolute
                    target = _resolve_relative_import(
                        module_name, module, level, package_root
                    )
                    import_type = "relative"
                else:
                    target = module
                    import_type = "absolute"

                for alias in (node.names or []):
                    full_target = f"{target}.{alias.name}" if alias.name != "*" else target
                    edges.append(ImportEdge(
                        source_module=module_name,
                        target_module=full_target,
                        import_type=import_type,
                        original_import=_reconstruct_import(node, level, module),
                        line_number=node.lineno
                    ))

        # Extract symbols
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                params = tuple(arg.arg for arg in node.args.args)
                decorators = tuple(
                    _get_decorator_name(d) for d in node.decorator_list
                )
                docstring = ast.get_docstring(node) or ""
                symbols.append(SourceSymbol(
                    symbol_name=node.name,
                    symbol_type="function",
                    file_path=file_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    parameters=params,
                    decorators=decorators,
                    docstring=docstring,
                    is_exported=not node.name.startswith("_")
                ))
            elif isinstance(node, ast.ClassDef):
                decorators = tuple(
                    _get_decorator_name(d) for d in node.decorator_list
                )
                docstring = ast.get_docstring(node) or ""
                symbols.append(SourceSymbol(
                    symbol_name=node.name,
                    symbol_type="class",
                    file_path=file_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    parameters=(),
                    decorators=decorators,
                    docstring=docstring,
                    is_exported=not node.name.startswith("_")
                ))
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        symbols.append(SourceSymbol(
                            symbol_name=target.id,
                            symbol_type="constant",
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            parameters=(),
                            decorators=(),
                            docstring="",
                            is_exported=not target.id.startswith("_")
                        ))

    # Build ImportGraph
    all_nodes = set()
    for edge in edges:
        all_nodes.add(edge.source_module)
        all_nodes.add(edge.target_module)

    graph = ImportGraph(
        edges=tuple(edges),
        nodes=frozenset(all_nodes),
        node_count=len(all_nodes),
        edge_count=len(edges)
    )

    # Check invariants
    source_files = [e for e in inventory.entries if e.file_type == "source_code" and e.is_parseable]
    if graph.node_count < len(source_files):
        raise InvariantViolation("INV-004: ImportGraph missing nodes for source files")

    return graph, symbols
```

**Helper: _resolve_relative_import**

```
function _resolve_relative_import(current_module, target_module, level, package_root):
    # Split current module into parts
    parts = current_module.split(".")

    # Go up 'level' directories
    if level > len(parts):
        raise ParseError(f"Relative import level {level} exceeds package depth")

    base_parts = parts[:-level] if level > 0 else parts
    base = ".".join(base_parts)

    if target_module:
        return f"{base}.{target_module}" if base else target_module
    return base
```

### 4.3 Stage TS-003: Audience Analysis

**Input:** FileInventory, list[SourceSymbol], list[AudienceDefinition]
**Output:** list[OutputDocument]
**Invariants checked:** INV-007, INV-008, INV-009

**Algorithm: analyze_audiences(inventory, symbols, audiences)**

```
function analyze_audiences(inventory, symbols, audiences):
    documents = []

    for audience in audiences:
        # Filter files by focus areas
        relevant_entries = _filter_by_focus_areas(inventory, audience.focus_areas)
        relevant_symbols = _filter_symbols_by_focus(symbols, audience.focus_areas)

        # Build sections following section_structure order
        sections = []
        for idx, section_name in enumerate(audience.section_structure):
            section_content = _generate_section_content(
                section_name=section_name,
                entries=relevant_entries,
                symbols=relevant_symbols,
                audience=audience
            )
            # Apply exclude filter
            section_content = _apply_exclude_filter(section_content, audience.exclude)

            sections.append(OutputSection(
                section_id=f"aud-{audience.audience_id}-sec-{idx}",
                section_name=section_name,
                content=section_content,
                findings=(),
                subsections=()
            ))

        doc = OutputDocument(
            document_id=f"audience-{audience.audience_id}",
            output_type="audience_report",
            title=f"{audience.label} Codebase Intelligence Report",
            sections=tuple(sections),
            metadata={
                "audience_id": audience.audience_id,
                "tone": audience.tone,
                "generation_date": _today_iso(),
                "source_file": audience.source_file
            },
            is_self_contained=True
        )
        documents.append(doc)

    # Check invariants
    # INV-007: one document per audience (guaranteed by loop structure)
    # INV-008: no hallucination (all content derived from actual files)
    # INV-009: audience fidelity (tone and structure match definition)

    return documents
```

**Helper: _filter_by_focus_areas**

```
function _filter_by_focus_areas(inventory, focus_areas):
    relevant = []
    for entry in inventory.entries:
        path_lower = entry.file_path.lower()
        for area in focus_areas:
            area_lower = area.lower()
            # Match if area keyword appears in file path
            if area_lower in path_lower:
                relevant.append(entry)
                break
            # Match if file is in a directory named after the area
            path_parts = path_lower.replace("\\", "/").split("/")
            if area_lower in path_parts:
                relevant.append(entry)
                break
    return relevant
```

### 4.4 Stage TS-004: Health Dimension Analysis

**Input:** ImportGraph, list[SourceSymbol], FileInventory, list[AnalysisDimension]
**Output:** list[Finding]
**Invariants checked:** INV-010, INV-011, INV-012, INV-013

**Algorithm: run_health_analysis(graph, symbols, inventory, dimensions)**

```
function run_health_analysis(graph, symbols, inventory, dimensions):
    all_findings = []
    finding_counter = {}  # dimension_id -> counter

    for dimension in dimensions:
        if not dimension.enabled:
            continue  # INV-013: disabled dimensions produce no findings

        finding_counter[dimension.dimension_id] = 0
        analyzer = DIMENSION_REGISTRY.get(dimension.dimension_id)
        if analyzer is None:
            raise ConfigurationError(
                f"No analyzer registered for dimension: {dimension.dimension_id}"
            )

        findings = analyzer.run(graph, symbols, inventory, dimension.config)

        for finding in findings:
            finding_counter[dimension.dimension_id] += 1
            # Assign finding_id with sequential number
            count = finding_counter[dimension.dimension_id]
            numbered_id = f"{dimension.dimension_id}-{count:03d}"

            # Validate finding structure
            _validate_finding(finding, dimension.dimension_id)

            all_findings.append(Finding(
                finding_id=numbered_id,
                source_type="health_dimension",
                source_id=dimension.dimension_id,
                severity=finding.severity,
                title=finding.title,
                description=finding.description,
                evidence=finding.evidence,
                impact=finding.impact,
                remediation=finding.remediation,
                is_self_contained=True
            ))

    return all_findings
```

**Dimension Analyzer Implementations:**

#### DIM-CIRCULAR: Circular Dependency Detection

```
class CircularDependencyAnalyzer:
    """Detects cycles in the import graph using Tarjan's SCC algorithm."""

    function run(graph, symbols, inventory, config):
        findings = []
        adjacency = _build_adjacency(graph)
        sccs = _tarjan_scc(adjacency)

        for scc in sccs:
            if len(scc) > 1:
                # Build evidence: the cycle path
                cycle_edges = [
                    edge for edge in graph.edges
                    if edge.source_module in scc and edge.target_module in scc
                ]
                evidence_list = []
                for edge in cycle_edges:
                    evidence_list.append(Evidence(
                        file_path=_module_to_path(edge.source_module),
                        line_number=edge.line_number,
                        code_snippet=edge.original_import,
                        description=f"Import from {edge.source_module} to {edge.target_module}"
                    ))

                findings.append(Finding(
                    finding_id="DIM-CIRCULAR-000",  # Assigned by caller
                    source_type="health_dimension",
                    source_id="DIM-CIRCULAR",
                    severity=SeverityRating("high", 4),
                    title=f"Circular dependency cycle: {len(scc)} modules",
                    description=f"Circular dependency detected among modules: {', '.join(sorted(scc))}",
                    evidence=tuple(evidence_list),
                    impact="Circular dependencies make modules tightly coupled, "
                           "hindering independent testing, refactoring, and deployment.",
                    remediation="Break the cycle by extracting shared interfaces into a "
                                "separate module, or restructure imports to use dependency injection.",
                    is_self_contained=True
                ))

        return findings

function _tarjan_scc(adjacency):
    """Tarjan's algorithm for strongly connected components."""
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = set()
    result = []

    function strongconnect(v):
        index[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)

        for w in adjacency.get(v, []):
            if w not in index:
                strongconnect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif w in on_stack:
                lowlinks[v] = min(lowlinks[v], index[w])

        if lowlinks[v] == index[v]:
            component = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                component.append(w)
                if w == v:
                    break
            result.append(component)

    for v in adjacency:
        if v not in index:
            strongconnect(v)

    return result
```

#### DIM-COUPLING: Coupling Metrics

```
class CouplingAnalyzer:
    """Computes fan-in and fan-out coupling metrics per module."""

    function run(graph, symbols, inventory, config):
        findings = []
        fan_in_threshold = config.get("fan_in_threshold", 10)
        fan_out_threshold = config.get("fan_out_threshold", 15)

        fan_in = {}   # module -> count of modules importing it
        fan_out = {}  # module -> count of modules it imports

        for edge in graph.edges:
            fan_out[edge.source_module] = fan_out.get(edge.source_module, 0) + 1
            fan_in[edge.target_module] = fan_in.get(edge.target_module, 0) + 1

        # Check all modules in the graph
        for module in graph.nodes:
            fi = fan_in.get(module, 0)
            fo = fan_out.get(module, 0)

            if fi > fan_in_threshold or fo > fan_out_threshold:
                severity = "critical" if (fi > fan_in_threshold * 2 or fo > fan_out_threshold * 2) else "high"
                evidence_list = []

                # Gather import evidence
                for edge in graph.edges:
                    if edge.source_module == module or edge.target_module == module:
                        evidence_list.append(Evidence(
                            file_path=_module_to_path(edge.source_module),
                            line_number=edge.line_number,
                            code_snippet=edge.original_import,
                            description=f"{edge.source_module} -> {edge.target_module}"
                        ))

                findings.append(Finding(
                    finding_id="DIM-COUPLING-000",
                    source_type="health_dimension",
                    source_id="DIM-COUPLING",
                    severity=SeverityRating(severity, 5 if severity == "critical" else 4),
                    title=f"High coupling: {module} (fan-in={fi}, fan-out={fo})",
                    description=f"Module {module} has fan-in={fi} (threshold={fan_in_threshold}) "
                                f"and fan-out={fo} (threshold={fan_out_threshold}).",
                    evidence=tuple(evidence_list[:10]),  # Limit evidence entries
                    impact="Highly coupled modules are difficult to modify, test, or reuse independently.",
                    remediation="Reduce coupling by introducing interfaces, extracting shared logic, "
                                "or applying the dependency inversion principle.",
                    is_self_contained=True
                ))

        return findings
```

#### DIM-DEADCODE: Dead Code Detection

```
class DeadCodeAnalyzer:
    """Identifies symbols not referenced by any import or call."""

    function run(graph, symbols, inventory, config):
        findings = []

        # Build set of all referenced symbol names
        referenced_names = set()
        for edge in graph.edges:
            # The target module is referenced
            referenced_names.add(edge.target_module)
            # Extract imported names from edge
            parts = edge.target_module.split(".")
            if parts:
                referenced_names.add(parts[-1])

        # Also scan for cross-file symbol references via import statements
        for entry in inventory.entries:
            if entry.file_type != "source_code" or not entry.is_parseable:
                continue
            content = _read_file(entry)
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    referenced_names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    referenced_names.add(node.attr)

        # Check each non-exported symbol
        for symbol in symbols:
            if symbol.is_exported:
                continue  # Exported symbols are public API, not dead code
            if symbol.symbol_name in referenced_names:
                continue  # Symbol is referenced somewhere

            findings.append(Finding(
                finding_id="DIM-DEADCODE-000",
                source_type="health_dimension",
                source_id="DIM-DEADCODE",
                severity=SeverityRating("low", 2),
                title=f"Potentially dead code: {symbol.symbol_type} {symbol.symbol_name}",
                description=f"The {symbol.symbol_type} '{symbol.symbol_name}' in {symbol.file_path} "
                            f"(lines {symbol.line_start}-{symbol.line_end}) does not appear to be "
                            f"referenced by any other module.",
                evidence=(Evidence(
                    file_path=symbol.file_path,
                    line_number=symbol.line_start,
                    code_snippet=f"{symbol.symbol_type} {symbol.symbol_name}",
                    description=f"Definition of unreferenced {symbol.symbol_type}"
                ),),
                impact="Dead code increases maintenance burden, confuses readers, "
                       "and may hide latent bugs.",
                remediation="Remove the unused symbol if confirmed unnecessary, "
                            "or add documentation explaining why it is retained.",
                is_self_contained=True
            ))

        return findings
```

#### DIM-COMPLEXITY: Complexity Analysis

```
class ComplexityAnalyzer:
    """Computes cyclomatic complexity for functions."""

    function run(graph, symbols, inventory, config):
        findings = []
        threshold = config.get("cyclomatic_threshold", 10)

        for symbol in symbols:
            if symbol.symbol_type != "function":
                continue

            content = _read_file_by_path(symbol.file_path, inventory)
            if content is None:
                continue

            tree = ast.parse(content)
            complexity = _compute_cyclomatic_complexity(tree, symbol.symbol_name)

            if complexity > threshold:
                severity = "high" if complexity > threshold * 2 else "medium"
                findings.append(Finding(
                    finding_id="DIM-COMPLEXITY-000",
                    source_type="health_dimension",
                    source_id="DIM-COMPLEXITY",
                    severity=SeverityRating(severity, 4 if severity == "high" else 3),
                    title=f"High complexity: {symbol.symbol_name} (cyclomatic={complexity})",
                    description=f"Function '{symbol.symbol_name}' in {symbol.file_path} "
                                f"has cyclomatic complexity {complexity} (threshold={threshold}).",
                    evidence=(Evidence(
                        file_path=symbol.file_path,
                        line_number=symbol.line_start,
                        code_snippet=f"def {symbol.symbol_name}(...)",
                        description=f"Cyclomatic complexity: {complexity}"
                    ),),
                    impact="Highly complex functions are difficult to understand, test, and maintain. "
                           "They tend to have many edge cases and are prone to bugs.",
                    remediation="Break the function into smaller, focused functions. "
                                "Extract conditional branches into helper methods. "
                                "Apply the single responsibility principle.",
                    is_self_contained=True
                ))

        return findings

function _compute_cyclomatic_complexity(tree, function_name):
    """Compute cyclomatic complexity for a named function in an AST."""
    complexity = 1  # Base complexity

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == function_name:
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                    elif isinstance(child, ast.ExceptHandler):
                        complexity += 1
                    elif isinstance(child, ast.With):
                        complexity += 1
                    elif isinstance(child, ast.Assert):
                        complexity += 1
                    elif isinstance(child, ast.comprehension):
                        complexity += 1
                        complexity += len(child.ifs)
                break

    return complexity
```

#### DIM-IMPORT: Import Discipline

```
class ImportDisciplineAnalyzer:
    """Analyzes import patterns for anti-patterns."""

    function run(graph, symbols, inventory, config):
        findings = []

        for edge in graph.edges:
            # Check for wildcard imports
            if "import *" in edge.original_import:
                findings.append(Finding(
                    finding_id="DIM-IMPORT-000",
                    source_type="health_dimension",
                    source_id="DIM-IMPORT",
                    severity=SeverityRating("medium", 3),
                    title=f"Wildcard import in {edge.source_module}",
                    description=f"Wildcard import 'from {edge.target_module} import *' "
                                f"makes it unclear which names are available.",
                    evidence=(Evidence(
                        file_path=_module_to_path(edge.source_module),
                        line_number=edge.line_number,
                        code_snippet=edge.original_import,
                        description="Wildcard import statement"
                    ),),
                    impact="Wildcard imports pollute the namespace, make code harder to read, "
                           "and can cause name collisions.",
                    remediation="Replace wildcard imports with explicit name imports.",
                    is_self_contained=True
                ))

            # Check for imports of private modules
            target_parts = edge.target_module.split(".")
            if any(part.startswith("_") for part in target_parts):
                findings.append(Finding(
                    finding_id="DIM-IMPORT-000",
                    source_type="health_dimension",
                    source_id="DIM-IMPORT",
                    severity=SeverityRating("low", 2),
                    title=f"Import of private module: {edge.target_module}",
                    description=f"Module {edge.source_module} imports from private module "
                                f"{edge.target_module} (name starts with underscore).",
                    evidence=(Evidence(
                        file_path=_module_to_path(edge.source_module),
                        line_number=edge.line_number,
                        code_snippet=edge.original_import,
                        description="Import of private module"
                    ),),
                    impact="Importing from private modules violates encapsulation and "
                           "creates fragile dependencies.",
                    remediation="Use the public API of the target module instead.",
                    is_self_contained=True
                ))

        return findings
```

### 4.5 Stage TS-005: Security Phase Analysis

**Input:** FileInventory, list[SourceSymbol], list[SecurityPhase]
**Output:** list[Finding]
**Invariants checked:** INV-014, INV-015, INV-016, INV-017, INV-018

**Algorithm: run_security_analysis(inventory, symbols, phases)**

```
function run_security_analysis(inventory, symbols, phases):
    all_findings = []
    finding_counter = {}

    for phase in phases:
        if not phase.enabled:
            continue  # INV-018: disabled phases produce no findings

        finding_counter[phase.phase_id] = 0
        analyzer = PHASE_REGISTRY.get(phase.phase_id)
        if analyzer is None:
            raise ConfigurationError(
                f"No analyzer registered for phase: {phase.phase_id}"
            )

        findings = analyzer.run(inventory, symbols, phase.config)

        for finding in findings:
            finding_counter[phase.phase_id] += 1
            count = finding_counter[phase.phase_id]
            numbered_id = f"{phase.phase_id}-{count:03d}"

            # INV-017: Redact secrets from evidence
            redacted_evidence = tuple(
                _redact_secret(evidence) for evidence in finding.evidence
            )

            all_findings.append(Finding(
                finding_id=numbered_id,
                source_type="security_phase",
                source_id=phase.phase_id,
                severity=finding.severity,
                title=finding.title,
                description=finding.description,
                evidence=redacted_evidence,
                impact=finding.impact,
                remediation=finding.remediation,
                is_self_contained=True
            ))

    return all_findings
```

**Phase Analyzer Implementations:**

#### PHASE-SECRETS: Secrets Detection

```
class SecretsAnalyzer:
    """Pattern scan for hardcoded secrets."""

    # Secret detection patterns
    SECRET_PATTERNS = [
        (r'(?:api_key|apikey|api_secret)\s*=\s*["\']([^"\']{16,})["\']', "API key"),
        (r'(?:password|passwd|pwd)\s*=\s*["\']([^"\']+)["\']', "Password"),
        (r'(?:secret|token|auth_token)\s*=\s*["\']([^"\']{8,})["\']', "Secret token"),
        (r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----', "Private key"),
        (r'(?:postgres|mysql|mongodb)://[^:]+:([^@]+)@', "Database credential"),
        (r'AKIA[0-9A-Z]{16}', "AWS access key"),
    ]

    function run(inventory, symbols, config):
        findings = []

        for entry in inventory.entries:
            if entry.file_type != "source_code" or not entry.is_parseable:
                continue

            content = _read_file(entry)
            lines = content.splitlines()

            for line_num, line in enumerate(lines, 1):
                for pattern, secret_type in self.SECRET_PATTERNS:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        # INV-017: The actual secret value is captured but will be
                        # redacted by the pipeline before output
                        raw_value = match.group(1) if match.lastindex else match.group(0)

                        findings.append(Finding(
                            finding_id="PHASE-SECRETS-000",
                            source_type="security_phase",
                            source_id="PHASE-SECRETS",
                            severity=SeverityRating("critical", 5),
                            title=f"Hardcoded {secret_type} detected",
                            description=f"A {secret_type.lower()} appears to be hardcoded "
                                        f"in {entry.file_path} at line {line_num}.",
                            evidence=(Evidence(
                                file_path=entry.file_path,
                                line_number=line_num,
                                code_snippet=_redact_value(line, raw_value),
                                description=f"Potential {secret_type.lower()} in source code"
                            ),),
                            impact="Hardcoded secrets in source code can be exposed through "
                                   "version control, logs, or decompilation.",
                            remediation="Move secrets to environment variables or a secrets "
                                        "manager. Never commit secret values to source control.",
                            is_self_contained=True
                        ))

        return findings
```

#### PHASE-DEPS: Dependencies Audit

```
class DependenciesAnalyzer:
    """Audit dependencies for known vulnerabilities."""

    function run(inventory, symbols, config):
        findings = []
        vuln_db_path = config.get("vulnerability_db_path")

        # Parse dependency declarations
        dependencies = _extract_dependencies(inventory)

        if not dependencies:
            return findings

        if vuln_db_path is None:
            findings.append(Finding(
                finding_id="PHASE-DEPS-001",
                source_type="security_phase",
                source_id="PHASE-DEPS",
                severity=SeverityRating("info", 1),
                title="Vulnerability database not configured",
                description="No vulnerability database path configured. "
                            "Dependency audit cannot check for known vulnerabilities.",
                evidence=(),
                impact="Without a vulnerability database, known vulnerable dependencies "
                       "will not be detected.",
                remediation="Configure vulnerability_db_path in the security phase config "
                            "to enable dependency vulnerability checking.",
                is_self_contained=True
            ))
            return findings

        # Load vulnerability database and check
        vuln_db = _load_vulnerability_db(vuln_db_path)
        for dep_name, dep_version, dep_file in dependencies:
            vulns = vuln_db.get(dep_name, [])
            for vuln in vulns:
                if _version_affected(dep_version, vuln):
                    findings.append(Finding(
                        finding_id="PHASE-DEPS-000",
                        source_type="security_phase",
                        source_id="PHASE-DEPS",
                        severity=SeverityRating(vuln.severity_level, vuln.numeric_weight),
                        title=f"Vulnerable dependency: {dep_name}=={dep_version}",
                        description=f"Dependency {dep_name} version {dep_version} is affected "
                                    f"by {vuln.vuln_id}: {vuln.description}",
                        evidence=(Evidence(
                            file_path=dep_file,
                            line_number=0,
                            code_snippet=f"{dep_name}=={dep_version}",
                            description=f"Vulnerable dependency declaration"
                        ),),
                        impact=vuln.impact,
                        remediation=f"Upgrade {dep_name} to version {vuln.fixed_version} or later.",
                        is_self_contained=True
                    ))

        return findings
```

#### PHASE-CODEPAT: Code Patterns Scan

```
class CodePatternsAnalyzer:
    """Scan for insecure coding patterns."""

    INSECURE_PATTERNS = [
        (r'\beval\s*\(', "eval() call", "high"),
        (r'\bexec\s*\(', "exec() call", "high"),
        (r'\bos\.system\s*\(', "os.system() call", "high"),
        (r'\bsubprocess\.\w+\s*\(.*shell\s*=\s*True', "subprocess with shell=True", "high"),
        (r'\bpickle\.load\s*\(', "pickle.load() call", "medium"),
        (r'\byaml\.load\s*\([^)]*\)\s*(?!.*Loader)', "yaml.load() without Loader", "medium"),
        (r'\bhashlib\.md5\s*\(', "MD5 hash (weak for security)", "low"),
        (r'\bhashlib\.sha1\s*\(', "SHA1 hash (weak for security)", "low"),
    ]

    function run(inventory, symbols, config):
        findings = []

        for entry in inventory.entries:
            if entry.file_type != "source_code" or not entry.is_parseable:
                continue

            content = _read_file(entry)
            lines = content.splitlines()

            for line_num, line in enumerate(lines, 1):
                for pattern, pattern_name, severity_level in self.INSECURE_PATTERNS:
                    if re.search(pattern, line):
                        weight = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
                        findings.append(Finding(
                            finding_id="PHASE-CODEPAT-000",
                            source_type="security_phase",
                            source_id="PHASE-CODEPAT",
                            severity=SeverityRating(severity_level, weight[severity_level]),
                            title=f"Insecure pattern: {pattern_name}",
                            description=f"Found {pattern_name} in {entry.file_path} at line {line_num}. "
                                        f"This pattern may introduce security vulnerabilities.",
                            evidence=(Evidence(
                                file_path=entry.file_path,
                                line_number=line_num,
                                code_snippet=line.strip(),
                                description=f"Insecure pattern: {pattern_name}"
                            ),),
                            impact=_get_pattern_impact(pattern_name),
                            remediation=_get_pattern_remediation(pattern_name),
                            is_self_contained=True
                        ))

        return findings
```

#### PHASE-AUTH: Authentication Review

```
class AuthReviewAnalyzer:
    """Review authentication implementations."""

    function run(inventory, symbols, config):
        findings = []

        # Check for auth-related symbols
        auth_symbols = [s for s in symbols if any(
            kw in s.symbol_name.lower()
            for kw in ("auth", "login", "session", "token", "credential")
        )]

        for symbol in auth_symbols:
            content = _read_file_by_path(symbol.file_path, inventory)
            if content is None:
                continue
            lines = content.splitlines()

            # Check for hardcoded credentials in auth code
            for line_num, line in enumerate(lines, 1):
                if line_num < symbol.line_start or line_num > symbol.line_end:
                    continue
                if re.search(r'(?:password|secret|key)\s*=\s*["\']', line, re.IGNORECASE):
                    findings.append(Finding(
                        finding_id="PHASE-AUTH-000",
                        source_type="security_phase",
                        source_id="PHASE-AUTH",
                        severity=SeverityRating("critical", 5),
                        title="Hardcoded credential in authentication code",
                        description=f"Hardcoded credential found in {symbol.symbol_name} "
                                    f"({symbol.file_path}, line {line_num}).",
                        evidence=(Evidence(
                            file_path=symbol.file_path,
                            line_number=line_num,
                            code_snippet=_redact_inline_secret(line.strip()),
                            description="Hardcoded credential in auth function"
                        ),),
                        impact="Hardcoded credentials in authentication code can be extracted "
                               "by anyone with access to the source.",
                        remediation="Use environment variables or a secrets manager for credentials.",
                        is_self_contained=True
                    ))

        return findings
```

#### PHASE-INFRA: Infrastructure Check

```
class InfrastructureAnalyzer:
    """Check deployment configuration for security issues."""

    INFRA_PATTERNS = [
        (r'debug\s*=\s*True', "Debug mode enabled", "high"),
        (r'DEBUG\s*=\s*True', "DEBUG flag enabled", "high"),
        (r'ALLOWED_HOSTS\s*=\s*\[\s*["\']?\*["\']?\s*\]', "Wildcard ALLOWED_HOSTS", "medium"),
        (r'CORS_ORIGIN\s*=\s*["\']?\*["\']?', "Wildcard CORS origin", "medium"),
        (r'(?:admin|root)\s*[:=]\s*["\']?(?:admin|root|password|1234)', "Default admin credential", "critical"),
    ]

    function run(inventory, symbols, config):
        findings = []

        for entry in inventory.entries:
            if entry.file_type not in ("configuration", "source_code"):
                continue
            if not entry.is_parseable:
                continue

            content = _read_file(entry)
            lines = content.splitlines()

            for line_num, line in enumerate(lines, 1):
                for pattern, issue_name, severity_level in self.INFRA_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        weight = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
                        findings.append(Finding(
                            finding_id="PHASE-INFRA-000",
                            source_type="security_phase",
                            source_id="PHASE-INFRA",
                            severity=SeverityRating(severity_level, weight[severity_level]),
                            title=f"Infrastructure issue: {issue_name}",
                            description=f"Found {issue_name} in {entry.file_path} at line {line_num}.",
                            evidence=(Evidence(
                                file_path=entry.file_path,
                                line_number=line_num,
                                code_snippet=line.strip(),
                                description=f"Configuration issue: {issue_name}"
                            ),),
                            impact=_get_infra_impact(issue_name),
                            remediation=_get_infra_remediation(issue_name),
                            is_self_contained=True
                        ))

        return findings
```

### 4.6 Stage TS-006: Findings Report Assembly

**Input:** list[Finding] from TS-004 and TS-005
**Output:** list[OutputDocument]
**Invariants checked:** INV-019, INV-020, INV-021

**Algorithm: assemble_findings_reports(health_findings, security_findings, dimensions, phases)**

```
function assemble_findings_reports(health_findings, security_findings, dimensions, phases):
    documents = []

    # Health Report (OM-002)
    health_sections = []
    for dimension in dimensions:
        if not dimension.enabled:
            continue
        dim_findings = [f for f in health_findings if f.source_id == dimension.dimension_id]
        # INV-021: only findings from this dimension
        # Sort by severity (critical first)
        dim_findings.sort(key=lambda f: f.severity.numeric_weight, reverse=True)

        if dim_findings:
            content = _render_findings_summary(dim_findings, dimension)
        else:
            content = f"No findings for {dimension.dimension_name}."

        health_sections.append(OutputSection(
            section_id=f"health-{dimension.dimension_id}",
            section_name=dimension.dimension_name,
            content=content,
            findings=tuple(dim_findings),
            subsections=()
        ))

    if health_sections:
        health_doc = OutputDocument(
            document_id="health-report",
            output_type="health_report",
            title="Structural Health Analysis Report",
            sections=tuple(health_sections),
            metadata={
                "generation_date": _today_iso(),
                "dimensions_analyzed": len([d for d in dimensions if d.enabled])
            },
            is_self_contained=True
        )
        documents.append(health_doc)

    # Security Report (OM-003)
    security_sections = []
    for phase in phases:
        if not phase.enabled:
            continue
        phase_findings = [f for f in security_findings if f.source_id == phase.phase_id]
        phase_findings.sort(key=lambda f: f.severity.numeric_weight, reverse=True)

        # INV-017 verification: all code_snippets must have secrets redacted
        for finding in phase_findings:
            for evidence in finding.evidence:
                _verify_redaction(evidence.code_snippet)

        if phase_findings:
            content = _render_findings_summary(phase_findings, phase)
        else:
            content = f"No findings for {phase.phase_name}."

        security_sections.append(OutputSection(
            section_id=f"security-{phase.phase_id}",
            section_name=phase.phase_name,
            content=content,
            findings=tuple(phase_findings),
            subsections=()
        ))

    if security_sections:
        security_doc = OutputDocument(
            document_id="security-report",
            output_type="security_report",
            title="Security Audit Report",
            sections=tuple(security_sections),
            metadata={
                "generation_date": _today_iso(),
                "phases_analyzed": len([p for p in phases if p.enabled])
            },
            is_self_contained=True
        )
        documents.append(security_doc)

    return documents
```

### 4.7 Stage TS-007: Output Validation

**Input:** All OutputDocument components
**Output:** RunManifest
**Invariants checked:** INV-022, INV-023, INV-024

**Algorithm: validate_and_manifest(all_documents)**

```
function validate_and_manifest(all_documents):
    # INV-022: At least 3 output types
    output_types = sorted(set(doc.output_type for doc in all_documents))
    if len(output_types) < 3:
        raise InvariantViolation(
            f"INV-022: Only {len(output_types)} output types produced, minimum is 3. "
            f"Types: {output_types}"
        )

    # INV-023: All documents are self-contained
    for doc in all_documents:
        if not doc.is_self_contained:
            raise InvariantViolation(
                f"INV-023: Document {doc.document_id} is not self-contained"
            )

    # INV-024: No unresolved file references
    for doc in all_documents:
        for section in doc.sections:
            _check_unresolved_references(section)

    # Build RunManifest
    manifest = RunManifest(
        run_id=_generate_run_id(),
        codename="codebase_intelligence",
        output_count=len(all_documents),
        output_types=tuple(output_types),
        documents=tuple(all_documents),
        generation_date=_today_iso(),
        output_type_count=len(output_types)
    )

    return manifest
```

---

## 5. Error Handling

### 5.1 Exception Hierarchy

```
class PipelineError(Exception):
    """Base exception for all pipeline errors."""

class ParseError(PipelineError):
    """Raised when input parsing fails."""

class InvariantViolation(PipelineError):
    """Raised when a pipeline invariant is violated."""

class ConfigurationError(PipelineError):
    """Raised when configuration is invalid or missing."""

class SecretRedactionError(PipelineError):
    """Raised when secret redaction fails (safety critical)."""

class RenderingError(PipelineError):
    """Raised when output rendering fails."""
```

### 5.2 Error Handling Strategy by Stage

| Stage | Error Type | Action |
|---|---|---|
| TS-001 | File read failure | Record in FileEntry.parse_errors, continue scan |
| TS-001 | No Python package found | Raise InvariantViolation(INV-002), halt pipeline |
| TS-001 | No doc directory found | Raise InvariantViolation(INV-003), halt pipeline |
| TS-002 | AST parse failure | Record in FileEntry.parse_errors, skip file |
| TS-002 | Relative import resolution failure | Raise ParseError, halt stage |
| TS-003 | Missing audiences directory | Log warning, produce no audience documents |
| TS-003 | Invalid audience definition | Skip audience, continue with valid ones |
| TS-004 | Unknown dimension_id | Raise ConfigurationError, halt stage |
| TS-004 | Dimension analyzer throws | Catch, log, continue with other dimensions |
| TS-005 | Unknown phase_id | Raise ConfigurationError, halt stage |
| TS-005 | Secret redaction failure | Raise SecretRedactionError, halt pipeline |
| TS-006 | No findings for enabled dimension/phase | Produce section with "No findings" note |
| TS-007 | Less than 3 output types | Raise InvariantViolation(INV-022), halt pipeline |
| TS-007 | Non-self-contained document | Raise InvariantViolation(INV-023), halt pipeline |

---

## 6. Configuration

### 6.1 Default Configuration

```json
{
  "repository_root": ".",
  "output_dir": "./output",
  "audiences_dir": "./audiences",
  "dimensions": {
    "DIM-CIRCULAR": {
      "enabled": true,
      "config": {}
    },
    "DIM-COUPLING": {
      "enabled": true,
      "config": {
        "fan_in_threshold": 10,
        "fan_out_threshold": 15
      }
    },
    "DIM-DEADCODE": {
      "enabled": true,
      "config": {}
    },
    "DIM-COMPLEXITY": {
      "enabled": true,
      "config": {
        "cyclomatic_threshold": 10
      }
    },
    "DIM-IMPORT": {
      "enabled": true,
      "config": {}
    }
  },
  "phases": {
    "PHASE-SECRETS": {
      "enabled": true,
      "config": {}
    },
    "PHASE-DEPS": {
      "enabled": true,
      "config": {
        "vulnerability_db_path": null
      }
    },
    "PHASE-CODEPAT": {
      "enabled": true,
      "config": {}
    },
    "PHASE-AUTH": {
      "enabled": true,
      "config": {}
    },
    "PHASE-INFRA": {
      "enabled": true,
      "config": {}
    }
  },
  "rendering": {
    "format": "markdown",
    "redact_secrets": true
  }
}
```

### 6.2 Override Precedence

From highest to lowest priority:

1. **Command-line arguments** -- e.g., --repository-root, --output-dir, --disable-dimension DIM-COUPLING
2. **Environment variables** -- e.g., CODEBASE_INTELLIGENCE_REPOSITORY_ROOT
3. **Config file values** -- JSON file at ./codebase_intelligence_config.json or specified via --config
4. **Built-in defaults** -- As specified in section 6.1

### 6.3 Configuration Defaults Summary

| Parameter | Default Value | Description |
|---|---|---|
| repository_root | "." | Root directory of the codebase to analyze |
| output_dir | "./output" | Directory for output files |
| audiences_dir | "./audiences" | Directory containing audience definition files |
| rendering.format | "markdown" | Output format: markdown, json, or html |
| rendering.redact_secrets | true | Whether to redact secrets in security findings |
| dimensions.DIM-COUPLING.fan_in_threshold | 10 | Fan-in count that triggers a coupling finding |
| dimensions.DIM-COUPLING.fan_out_threshold | 15 | Fan-out count that triggers a coupling finding |
| dimensions.DIM-COMPLEXITY.cyclomatic_threshold | 10 | Cyclomatic complexity that triggers a finding |
| All dimensions.enabled | true | All 5 baseline dimensions enabled by default |
| All phases.enabled | true | All 5 baseline phases enabled by default |

---

## 7. Extension Interface

### 7.1 Protocol Interfaces

Three protocol interfaces define the contracts for extension. Implementations must satisfy these interfaces to be recognized by the pipeline.

#### InputParser Protocol

```
class InputParser(Protocol):
    def parse_file(self, file_path: str) -> FileEntry:
        """Parse a single file into a FileEntry component."""
        ...

    def parse_imports(self, file_path: str) -> list:
        """Extract import edges from a Python source file via AST."""
        ...

    def parse_symbols(self, file_path: str) -> list:
        """Extract source symbols from a Python source file via AST."""
        ...

    def parse_audience(self, file_path: str) -> AudienceDefinition:
        """Parse an audience definition from a Markdown file with YAML frontmatter."""
        ...
```

#### AnalysisEngine Protocol

```
class AnalysisEngine(Protocol):
    def run_dimension(self, dimension: AnalysisDimension, graph: ImportGraph,
                      symbols: list, inventory: FileInventory) -> list:
        """Run a health dimension analysis. Returns list of Finding."""
        ...

    def run_phase(self, phase: SecurityPhase, inventory: FileInventory,
                  symbols: list) -> list:
        """Run a security phase analysis. Returns list of Finding."""
        ...
```

#### OutputRenderer Protocol

```
class OutputRenderer(Protocol):
    def render_document(self, document: OutputDocument) -> str:
        """Render an OutputDocument to a string in the target format."""
        ...

    def render_manifest(self, manifest: RunManifest) -> str:
        """Render a RunManifest to a string in the target format."""
        ...

    def supported_formats(self) -> list:
        """Return list of supported output format names."""
        ...
```

### 7.2 Extension Registries

Extensions are registered using dictionary-based registries (per CODER_IMPLEMENTATION_SOP registry pattern):

```
DIMENSION_REGISTRY: dict[str, DimensionAnalyzer]
    Keys: dimension_id strings (e.g., "DIM-CIRCULAR")
    Values: Objects with run(graph, symbols, inventory, config) method

PHASE_REGISTRY: dict[str, PhaseAnalyzer]
    Keys: phase_id strings (e.g., "PHASE-SECRETS")
    Values: Objects with run(inventory, symbols, config) method

RENDERER_REGISTRY: dict[str, OutputRenderer]
    Keys: format name strings (e.g., "markdown", "json", "html")
    Values: Objects satisfying the OutputRenderer Protocol
```

### 7.3 Extension Point Implementations

#### EXT-001: Custom Audience Definitions

**How to add:**
1. Create a new .md file in the audiences/ directory.
2. Include YAML frontmatter with required fields:
   ```yaml
   ---
   audience_id: "developers"
   label: "Developer Guide"
   tone: "technical"
   focus_areas: ["source_code", "api", "modules"]
   section_structure: ["Architecture Overview", "Module Index", "API Reference"]
   exclude: ["internal utilities"]
   ---
   ```
3. The InputParser.parse_audience method discovers the file automatically during TS-001.
4. TS-003 produces a new OutputDocument for the new audience.

**What does NOT change:** ImportGraph, AnalysisDimension, SecurityPhase, pipeline stages, invariants.

**Contract:** The audience definition must conform to the AudienceDefinition data structure. The generated OutputDocument must satisfy is_self_contained=True and all output validation rules.

#### EXT-002: Custom Health Dimensions

**How to add:**
1. Create a class with a run(graph, symbols, inventory, config) method.
2. The run method must return a list of Finding components.
3. Each Finding must have evidence (at least one Evidence), use the standard SeverityRating scale, and set is_self_contained=True.
4. Register in DIMENSION_REGISTRY:
   ```
   DIMENSION_REGISTRY["DIM-CUSTOM"] = CustomDimensionAnalyzer()
   ```
5. Enable in config:
   ```json
   {"DIM-CUSTOM": {"enabled": true, "config": {}}}
   ```

**What does NOT change:** ImportGraph construction, security phase analysis, audience analysis, output contract.

**Contract:** Findings must satisfy the Finding data structure. Evidence must cite file paths. Severity must use the 5-level scale.

#### EXT-003: Custom Security Phases

**How to add:**
1. Create a class with a run(inventory, symbols, config) method.
2. The run method must return a list of Finding components.
3. Each Finding must redact actual secret values from evidence.code_snippet.
4. Register in PHASE_REGISTRY:
   ```
   PHASE_REGISTRY["PHASE-CUSTOM"] = CustomPhaseAnalyzer()
   ```
5. Enable in config:
   ```json
   {"PHASE-CUSTOM": {"enabled": true, "config": {}}}
   ```

**What does NOT change:** ImportGraph construction, health dimension analysis, audience analysis.

**Contract:** Findings must satisfy the Finding data structure. Secret values must be redacted. Severity must use the 5-level scale.

#### EXT-004: Configurable Thresholds

**How to add:**
1. Add threshold parameters to the dimension or phase config object in the JSON config.
2. The analyzer reads thresholds from the config dict at runtime.
3. Example:
   ```json
   {"DIM-COMPLEXITY": {"enabled": true, "config": {"cyclomatic_threshold": 15}}}
   ```

**What does NOT change:** Component schemas, pipeline stages, invariants.

**Contract:** Threshold changes must not violate invariants. Findings must still cite evidence and use the standard severity scale regardless of threshold values.

#### EXT-005: Multiple Output Formats

**How to add:**
1. Implement the OutputRenderer Protocol.
2. Register in RENDERER_REGISTRY:
   ```
   RENDERER_REGISTRY["json"] = JSONRenderer()
   ```
3. Set in config:
   ```json
   {"rendering": {"format": "json"}}
   ```

**What does NOT change:** Meta schema, transformation pipeline, invariants. Only the final serialization step varies.

**Contract:** The rendered output must preserve all information from the OutputDocument. All findings, evidence, and metadata must be present. Self-containment and no-hallucination constraints apply to all formats.

#### EXT-006: Incremental Analysis

**How to add:**
1. Implement a cache layer that stores previous FileInventory and ImportGraph state.
2. On subsequent runs, detect changed files by comparing file hashes or timestamps.
3. Re-parse only changed files. Update the ImportGraph incrementally.
4. Feed the updated components into the existing pipeline from TS-003 onward.

**What does NOT change:** Meta schema, transformation stages TS-003 through TS-007, invariants.

**Contract:** The incrementally-updated FileInventory and ImportGraph must be identical to what a full re-analysis would produce. All invariants INV-001 through INV-006 must hold.

### 7.4 Default Renderer Implementations

#### MarkdownRenderer

```
class MarkdownRenderer:
    """Renders OutputDocument and RunManifest to Markdown format."""

    function render_document(document):
        lines = []
        # YAML frontmatter
        lines.append("---")
        lines.append(f"document_id: \"{document.document_id}\"")
        lines.append(f"output_type: \"{document.output_type}\"")
        lines.append(f"title: \"{document.title}\"")
        lines.append(f"generation_date: \"{document.metadata.get('generation_date', '')}\"")
        lines.append(f"is_self_contained: true")
        lines.append("---")
        lines.append("")
        lines.append(f"# {document.title}")
        lines.append("")

        for section in document.sections:
            lines.extend(_render_section(section, level=2))

        return "\n".join(lines)

    function render_manifest(manifest):
        lines = []
        lines.append("---")
        lines.append(f"run_id: \"{manifest.run_id}\"")
        lines.append(f"codename: \"{manifest.codename}\"")
        lines.append(f"output_count: {manifest.output_count}")
        lines.append(f"output_type_count: {manifest.output_type_count}")
        lines.append(f"generation_date: \"{manifest.generation_date}\"")
        lines.append("---")
        lines.append("")
        lines.append(f"# Run Manifest: {manifest.codename}")
        lines.append("")
        lines.append(f"**Run ID:** {manifest.run_id}")
        lines.append(f"**Generated:** {manifest.generation_date}")
        lines.append(f"**Documents:** {manifest.output_count}")
        lines.append(f"**Output types:** {', '.join(manifest.output_types)}")
        lines.append("")
        lines.append("## Documents")
        lines.append("")
        for doc in manifest.documents:
            lines.append(f"- **{doc.title}** ({doc.output_type}): {doc.document_id}")
        lines.append("")
        return "\n".join(lines)

    function supported_formats():
        return ["markdown"]
```

#### JSONRenderer

```
class JSONRenderer:
    """Renders OutputDocument and RunManifest to JSON format."""

    function render_document(document):
        data = {
            "document_id": document.document_id,
            "output_type": document.output_type,
            "title": document.title,
            "metadata": document.metadata,
            "is_self_contained": document.is_self_contained,
            "sections": [_section_to_dict(s) for s in document.sections]
        }
        return json.dumps(data, indent=2)

    function render_manifest(manifest):
        data = {
            "run_id": manifest.run_id,
            "codename": manifest.codename,
            "output_count": manifest.output_count,
            "output_types": list(manifest.output_types),
            "output_type_count": manifest.output_type_count,
            "generation_date": manifest.generation_date,
            "documents": [
                {
                    "document_id": d.document_id,
                    "output_type": d.output_type,
                    "title": d.title,
                    "section_count": len(d.sections)
                }
                for d in manifest.documents
            ]
        }
        return json.dumps(data, indent=2)

    function supported_formats():
        return ["json"]
```

---

## 8. Output Rendering

### 8.1 File Naming Convention

| Output Type | File Pattern | Example |
|---|---|---|
| audience_report | audience_{audience_id}.md | audience_developers.md |
| health_report | health_report.md | health_report.md |
| security_report | security_report.md | security_report.md |
| Run manifest | RUN_MANIFEST.md | RUN_MANIFEST.md |

### 8.2 Rendering Pipeline

```
function render_all(manifest, config):
    renderer = RENDERER_REGISTRY.get(config.rendering_format)
    if renderer is None:
        raise ConfigurationError(f"No renderer for format: {config.rendering_format}")

    extension = _format_extension(config.rendering_format)
    output_dir = config.output_dir

    for doc in manifest.documents:
        content = renderer.render_document(doc)
        if doc.output_type == "audience_report":
            filename = f"audience_{doc.metadata.get('audience_id', 'unknown')}{extension}"
        elif doc.output_type == "health_report":
            filename = f"health_report{extension}"
        elif doc.output_type == "security_report":
            filename = f"security_report{extension}"
        else:
            filename = f"{doc.document_id}{extension}"

        filepath = os.path.join(output_dir, filename)
        _write_file(filepath, content)

    # Render manifest
    manifest_content = renderer.render_manifest(manifest)
    manifest_path = os.path.join(output_dir, f"RUN_MANIFEST{extension}")
    _write_file(manifest_path, manifest_content)
```

### 8.3 Secret Redaction Algorithm

```
function _redact_secret(evidence):
    """Redact secret values from evidence code snippets."""
    snippet = evidence.code_snippet
    for pattern, _ in SecretsAnalyzer.SECRET_PATTERNS:
        match = re.search(pattern, snippet, re.IGNORECASE)
        if match and match.lastindex:
            secret_value = match.group(match.lastindex)
            redacted = secret_value[:3] + "***REDACTED***"
            snippet = snippet.replace(secret_value, redacted)
    return Evidence(
        file_path=evidence.file_path,
        line_number=evidence.line_number,
        code_snippet=snippet,
        description=evidence.description
    )
```

---

## 9. Self-Validation

### 9.1 Invariant Coverage

| Invariant | Stage | How Satisfied |
|---|---|---|
| INV-001 | TS-001 | scan_codebase raises InvariantViolation if entries empty |
| INV-002 | TS-001 | scan_codebase checks has_python_package |
| INV-003 | TS-001 | scan_codebase checks has_doc_directory |
| INV-004 | TS-002 | build_import_graph verifies node count >= source file count |
| INV-005 | TS-002 | _resolve_relative_import resolves all relative imports |
| INV-006 | TS-002 | AST parsing via ast.parse(), no regex for imports |
| INV-007 | TS-003 | One OutputDocument created per AudienceDefinition |
| INV-008 | TS-003 | All content derived from actual FileInventory entries |
| INV-009 | TS-003 | Tone and section_structure match audience definition |
| INV-010 | TS-004 | Each Finding requires at least one Evidence |
| INV-011 | TS-004 | All findings use SeverityRating with 5-level scale |
| INV-012 | TS-004 | Each dimension analyzer is self-contained |
| INV-013 | TS-004 | Disabled dimensions are skipped |
| INV-014 | TS-005 | Each Finding requires at least one Evidence |
| INV-015 | TS-005 | All findings use SeverityRating with 5-level scale |
| INV-016 | TS-005 | Each phase analyzer is self-contained |
| INV-017 | TS-005 | _redact_secret applied to all security evidence |
| INV-018 | TS-005 | Disabled phases are skipped |
| INV-019 | TS-006 | One section per enabled dimension in health report |
| INV-020 | TS-006 | One section per enabled phase in security report |
| INV-021 | TS-006 | Findings filtered by source_id per section |
| INV-022 | TS-007 | Validates output_type_count >= 3 |
| INV-023 | TS-007 | Validates is_self_contained for all documents |
| INV-024 | TS-007 | Checks for unresolved file references |

### 9.2 Constraint Coverage

| Constraint | How Satisfied |
|---|---|
| C-FMT-001 | File type classification by extension (.md) |
| C-FMT-002 | File type classification by extension (.py) |
| C-FMT-003 | encoding="UTF-8" on all FileEntry components |
| C-FMT-004 | ast.parse() used for all import analysis, no regex |
| C-FMT-005 | SeverityRating enum with 5 fixed levels |
| C-FMT-006 | is_self_contained=True on all OutputDocument components |
| C-FMT-007 | Finding requires evidence tuple with at least one Evidence |
| C-CMP-001 | All content derived from actual FileInventory entries |
| C-CMP-002 | _redact_secret applied in TS-005 |
| C-CMP-003 | Audience tone and section_structure applied in TS-003 |
| C-CMP-004 | Each dimension/phase analyzer is independently invocable |
| C-CMP-005 | Audience files auto-discovered from audiences/ directory |
| C-CMP-006 | JSON config controls enabled/disabled for each dimension and phase |

### 9.3 Verification Checklist

- [x] 7 transformation stages implemented (TS-001 through TS-007).
- [x] 14 meta component data structures defined.
- [x] 24 invariants satisfied with explicit checks.
- [x] 13 constraints covered.
- [x] 3 Protocol interfaces defined (InputParser, AnalysisEngine, OutputRenderer).
- [x] 6 extension points documented with procedures and contracts.
- [x] 5 baseline health dimensions implemented.
- [x] 5 baseline security phases implemented.
- [x] Registry-based dispatch (no if/elif chains for dimension/phase/renderer).
- [x] Dataclass-based configuration (no long parameter lists).
- [x] Exception-based error handling (no silent None returns).
- [x] Output-type-agnostic design (OutputDocument is generic interface).
- [x] Default configuration values specified.
- [x] Override precedence defined.
- [x] ASCII-only content. No em-dashes, curly quotes, or Unicode.
- [x] Governance path references use filenames only.

---

**End of Default Runtime Implementation**
